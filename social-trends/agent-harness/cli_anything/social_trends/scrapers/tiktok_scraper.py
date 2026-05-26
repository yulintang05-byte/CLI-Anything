#!/usr/bin/env python3
"""TikTok trend scraper — fetches viral hashtags, trending sounds, and hot videos.

Modes:
  Research API — set TIKTOK_CLIENT_KEY + TIKTOK_CLIENT_SECRET (approved apps only)
  Scrape mode  — hits TikTok's public discover/trending endpoints with session cookies

TikTok aggressively protects its API; scrape mode may require a valid session cookie
(set TIKTOK_SESSION_ID env var from your browser's sessionid cookie).
"""

import os
import re
import json
import time
import hashlib
import requests
from typing import Optional
from urllib.parse import urlencode

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Mobile/15E148 TikTok/31.5.4"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
    "Origin": "https://www.tiktok.com",
}

_DISCOVER_BASE = "https://www.tiktok.com/api/discover"
_TRENDING_HASHTAG_URL = f"{_DISCOVER_BASE}/hashtag/"
_TRENDING_MUSIC_URL = f"{_DISCOVER_BASE}/music/"
_TRENDING_VIDEO_URL = "https://www.tiktok.com/api/recommend/item_list/"


def _session_id() -> Optional[str]:
    return os.environ.get("TIKTOK_SESSION_ID")


def _client_key() -> Optional[str]:
    return os.environ.get("TIKTOK_CLIENT_KEY")


def _client_secret() -> Optional[str]:
    return os.environ.get("TIKTOK_CLIENT_SECRET")


def _build_session() -> requests.Session:
    sess = requests.Session()
    sess.headers.update(_HEADERS)
    sid = _session_id()
    if sid:
        sess.cookies.set("sessionid", sid, domain=".tiktok.com")
    return sess


def _get_research_token() -> Optional[str]:
    """Obtain OAuth2 access token from TikTok Research API."""
    key = _client_key()
    secret = _client_secret()
    if not (key and secret):
        return None
    try:
        resp = requests.post(
            "https://open.tiktokapis.com/v2/oauth/token/",
            data={
                "client_key": key,
                "client_secret": secret,
                "grant_type": "client_credentials",
            },
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("access_token")
    except Exception:
        return None


def fetch_trending_hashtags(limit: int = 30) -> list[dict]:
    """Return trending TikTok hashtags with post counts."""
    sess = _build_session()
    params = {
        "count": min(limit, 30),
        "cursor": 0,
        "scene": 1,
    }
    hashtags = []
    try:
        resp = sess.get(_TRENDING_HASHTAG_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("challengeInfoList", []):
            ch = item.get("challengeInfo", {}) or item
            stats = ch.get("stats", {})
            challenge = ch.get("challenge", ch)
            hashtags.append({
                "platform": "tiktok",
                "hashtag": f"#{challenge.get('title', '')}",
                "post_count": stats.get("videoCount", 0),
                "view_count": stats.get("viewCount", 0),
                "id": challenge.get("id", ""),
            })
    except Exception:
        hashtags = _scrape_trending_hashtags_fallback(limit)

    return hashtags[:limit]


def _scrape_trending_hashtags_fallback(limit: int) -> list[dict]:
    """Parse trending hashtags from TikTok's explore/discover web page."""
    sess = _build_session()
    sess.headers["User-Agent"] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
    hashtags = []
    try:
        resp = sess.get("https://www.tiktok.com/explore", timeout=15)
        resp.raise_for_status()
        # TikTok embeds __UNIVERSAL_DATA_FOR_REHYDRATION__ JSON
        match = re.search(
            r'window\["__UNIVERSAL_DATA_FOR_REHYDRATION__"\]\s*=\s*({.*?})\s*;',
            resp.text, re.DOTALL
        )
        if not match:
            match = re.search(r'"__UNIVERSAL_DATA_FOR_REHYDRATION__":\s*({.*?})\s*[,}]', resp.text, re.DOTALL)
        if match:
            data = json.loads(match.group(1))
            # Walk the data tree looking for hashtag challenges
            raw = json.dumps(data)
            tags = re.findall(r'"title"\s*:\s*"([^"#][^"]*)".*?"videoCount"\s*:\s*(\d+)', raw)
            for title, count in tags[:limit]:
                if len(title) < 50 and not any(c in title for c in [" ", "/"]):
                    hashtags.append({
                        "platform": "tiktok",
                        "hashtag": f"#{title}",
                        "post_count": int(count),
                        "view_count": 0,
                    })
    except Exception:
        pass
    return hashtags[:limit]


def fetch_trending_sounds(limit: int = 20) -> list[dict]:
    """Return trending TikTok sounds/music."""
    sess = _build_session()
    params = {
        "count": min(limit, 30),
        "cursor": 0,
        "scene": 4,
    }
    sounds = []
    try:
        resp = sess.get(_TRENDING_MUSIC_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("musicList", []):
            music = item.get("music", item)
            stats = item.get("stats", {})
            sounds.append({
                "platform": "tiktok",
                "title": music.get("title", ""),
                "author": music.get("authorName", ""),
                "duration": music.get("duration", 0),
                "play_url": music.get("playUrl", ""),
                "cover_url": music.get("coverThumb", ""),
                "video_count": stats.get("videoCount", 0),
                "id": music.get("id", ""),
            })
    except Exception:
        sounds = _scrape_sounds_fallback(limit)
    return sounds[:limit]


def _scrape_sounds_fallback(limit: int) -> list[dict]:
    """Fallback: extract sounds from trending video metadata."""
    videos = fetch_trending_videos(limit=limit * 2)
    seen = set()
    sounds = []
    for v in videos:
        sound_key = v.get("sound_title", "")
        if sound_key and sound_key not in seen:
            seen.add(sound_key)
            sounds.append({
                "platform": "tiktok",
                "title": v.get("sound_title", ""),
                "author": v.get("sound_author", ""),
                "duration": v.get("sound_duration", 0),
                "video_count": 0,
            })
    return sounds[:limit]


def fetch_trending_videos(limit: int = 20) -> list[dict]:
    """Return currently trending TikTok videos."""
    sess = _build_session()
    params = {
        "count": min(limit, 30),
        "id": "1",
        "type": "5",
        "secUid": "",
        "maxCursor": "0",
        "minCursor": "0",
        "shareUid": "",
        "lang": "en",
        "scene": "25",
    }
    videos = []
    try:
        resp = sess.get(_TRENDING_VIDEO_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("itemList", []):
            desc = item.get("desc", "")
            hashtags = re.findall(r"#(\w+)", desc)
            author = item.get("author", {})
            stats = item.get("stats", {})
            music = item.get("music", {})
            videos.append({
                "platform": "tiktok",
                "id": item.get("id", ""),
                "url": f"https://www.tiktok.com/@{author.get('uniqueId', '')}/" + f"video/{item.get('id', '')}",
                "description": desc,
                "hashtags": hashtags,
                "author": author.get("uniqueId", ""),
                "author_followers": author.get("stats", {}).get("followerCount", 0),
                "likes": stats.get("diggCount", 0),
                "comments": stats.get("commentCount", 0),
                "shares": stats.get("shareCount", 0),
                "plays": stats.get("playCount", 0),
                "sound_title": music.get("title", ""),
                "sound_author": music.get("authorName", ""),
                "sound_duration": music.get("duration", 0),
            })
    except Exception:
        pass
    return videos[:limit]


def fetch_all_trends(limit: int = 30) -> dict:
    """Aggregate all TikTok trend types in one call."""
    return {
        "hashtags": fetch_trending_hashtags(limit),
        "sounds": fetch_trending_sounds(limit),
        "videos": fetch_trending_videos(limit),
    }
