"""TikTok trending scraper.

Two backends, chosen automatically:
  1. TikTok Research API (official) — set TIKTOK_CLIENT_KEY + TIKTOK_CLIENT_SECRET
  2. Unofficial lightweight scraper via mobile API endpoints — no credentials needed
     (rate-limited; suitable for personal/research use)
"""

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


# ── Official Research API ────────────────────────────────────────────────────

RESEARCH_API = "https://open.tiktokapis.com/v2"


def _has_official_creds() -> bool:
    return bool(os.environ.get("TIKTOK_CLIENT_KEY")) and bool(
        os.environ.get("TIKTOK_CLIENT_SECRET")
    )


def _get_access_token() -> str:
    url = "https://open.tiktokapis.com/v2/oauth/token/"
    data = urllib.parse.urlencode(
        {
            "client_key": os.environ["TIKTOK_CLIENT_KEY"],
            "client_secret": os.environ["TIKTOK_CLIENT_SECRET"],
            "grant_type": "client_credentials",
        }
    ).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        body = json.loads(r.read().decode())
    token = body.get("access_token")
    if not token:
        raise RuntimeError(f"TikTok token error: {body}")
    return token


def _research_query(token: str, payload: dict) -> dict:
    url = f"{RESEARCH_API}/research/video/query/"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def search_official(keyword: str, max_count: int = 20) -> list[dict]:
    """Search via TikTok Research API (requires approved app credentials)."""
    token = _get_access_token()
    payload = {
        "query": {
            "and": [{"operation": "IN", "field_name": "keyword", "field_values": [keyword]}]
        },
        "max_count": min(max_count, 100),
        "cursor": 0,
        "fields": "id,username,video_description,like_count,comment_count,share_count,view_count,hashtag_names,music_id,create_time",
    }
    data = _research_query(token, payload)
    videos = data.get("data", {}).get("videos", [])
    return _normalize_official(videos)


def get_trending_hashtags_official(max_count: int = 30) -> list[dict]:
    """Trending hashtag challenge list via Research API."""
    token = _get_access_token()
    url = f"{RESEARCH_API}/research/hashtag/query/?fields=id,name,video_count,view_count"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read().decode())
    hashtags = data.get("data", {}).get("hashtags", [])
    return sorted(
        [
            {
                "hashtag": f"#{h.get('name', '')}",
                "video_count": h.get("video_count", 0),
                "view_count": h.get("view_count", 0),
            }
            for h in hashtags
        ],
        key=lambda x: x["view_count"],
        reverse=True,
    )[:max_count]


def _normalize_official(videos: list) -> list[dict]:
    result = []
    for v in videos:
        result.append(
            {
                "video_id": str(v.get("id", "")),
                "username": v.get("username", ""),
                "description": v.get("video_description", ""),
                "hashtags": [f"#{h}" for h in v.get("hashtag_names", [])],
                "like_count": v.get("like_count", 0),
                "comment_count": v.get("comment_count", 0),
                "share_count": v.get("share_count", 0),
                "view_count": v.get("view_count", 0),
                "music_id": v.get("music_id", ""),
                "created_at": v.get("create_time", ""),
                "url": f"https://tiktok.com/@{v.get('username', '')}/video/{v.get('id', '')}",
                "source": "official_api",
            }
        )
    return sorted(result, key=lambda x: x["view_count"], reverse=True)


# ── Unofficial Lightweight Scraper ───────────────────────────────────────────

_MOBILE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
)

_DISCOVER_URL = "https://www.tiktok.com/api/discover/challenge/?count=30&from_page=trending&WebIdLastTime=0"
_TRENDING_URL = "https://www.tiktok.com/api/recommend/item_list/?count=30&from_page=fyp"


def _http_get_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": _MOBILE_UA,
            "Referer": "https://www.tiktok.com/",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))
    except Exception as exc:
        return {"error": str(exc), "items": [], "challengeList": []}


def get_trending_hashtags_unofficial(count: int = 30) -> list[dict]:
    """Scrape trending hashtag challenges from TikTok discover page."""
    data = _http_get_json(_DISCOVER_URL)
    challenges = data.get("challengeList", [])
    results = []
    for c in challenges[:count]:
        info = c.get("challengeInfo", {}).get("challenge", {})
        stats = c.get("challengeInfo", {}).get("statsV2", {})
        results.append(
            {
                "hashtag": f"#{info.get('title', '')}",
                "video_count": int(stats.get("videoCount", 0)),
                "view_count": int(stats.get("viewCount", 0)),
                "source": "unofficial_scraper",
            }
        )
    return sorted(results, key=lambda x: x["view_count"], reverse=True)


def get_trending_sounds_unofficial(count: int = 20) -> list[dict]:
    """Extract trending music/sounds from TikTok FYP feed."""
    data = _http_get_json(_TRENDING_URL)
    items = data.get("itemList", [])
    sounds: dict[str, dict] = {}
    for item in items:
        music = item.get("music", {})
        mid = str(music.get("id", ""))
        if not mid:
            continue
        if mid not in sounds:
            sounds[mid] = {
                "music_id": mid,
                "title": music.get("title", ""),
                "author": music.get("authorName", ""),
                "original": music.get("original", False),
                "duration": music.get("duration", 0),
                "video_count": 0,
                "cover_url": music.get("coverThumb", ""),
            }
        sounds[mid]["video_count"] += 1
    return sorted(sounds.values(), key=lambda x: x["video_count"], reverse=True)[:count]


def get_trending_videos_unofficial(count: int = 20) -> list[dict]:
    """Fetch trending FYP videos from TikTok."""
    data = _http_get_json(_TRENDING_URL)
    items = data.get("itemList", [])
    results = []
    for item in items[:count]:
        desc = item.get("desc", "")
        author = item.get("author", {})
        stats = item.get("stats", {})
        music = item.get("music", {})
        hashtags = re.findall(r"#\w+", desc)
        results.append(
            {
                "video_id": item.get("id", ""),
                "username": author.get("uniqueId", ""),
                "description": desc,
                "hashtags": hashtags,
                "like_count": stats.get("diggCount", 0),
                "comment_count": stats.get("commentCount", 0),
                "share_count": stats.get("shareCount", 0),
                "view_count": stats.get("playCount", 0),
                "music_title": music.get("title", ""),
                "music_author": music.get("authorName", ""),
                "url": f"https://tiktok.com/@{author.get('uniqueId', '')}/video/{item.get('id', '')}",
                "source": "unofficial_scraper",
            }
        )
    return sorted(results, key=lambda x: x["view_count"], reverse=True)


# ── Unified entrypoints ──────────────────────────────────────────────────────

def get_trending_hashtags(count: int = 30) -> list[dict]:
    if _has_official_creds():
        try:
            return get_trending_hashtags_official(count)
        except Exception:
            pass
    return get_trending_hashtags_unofficial(count)


def get_trending_videos(count: int = 20) -> list[dict]:
    if _has_official_creds():
        try:
            return search_official("trending", count)
        except Exception:
            pass
    return get_trending_videos_unofficial(count)


def get_trending_sounds(count: int = 20) -> list[dict]:
    return get_trending_sounds_unofficial(count)


def extract_top_hashtags(videos: list[dict], top_n: int = 30) -> list[dict]:
    freq: dict[str, int] = {}
    for v in videos:
        for tag in v.get("hashtags", []):
            t = tag.lower().strip()
            freq[t] = freq.get(t, 0) + 1
    return sorted(
        [{"hashtag": k, "count": v} for k, v in freq.items()],
        key=lambda x: x["count"],
        reverse=True,
    )[:top_n]
