"""TikTok trending scraper — hashtags, sounds, and videos via public endpoints."""
from __future__ import annotations

import json
import re
import time
from typing import Any

import requests

# TikTok public API base (used by TikTok web app)
_BASE = "https://www.tiktok.com"
_API_BASE = "https://api16-normal-c-useast1a.tiktokv.com"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.tiktok.com/",
}

REGION_CODES = {
    "us": "US", "uk": "GB", "ca": "CA", "au": "AU",
    "in": "IN", "br": "BR", "de": "DE", "fr": "FR",
    "jp": "JP", "kr": "KR", "mx": "MX", "ng": "NG",
}


def _extract_next_data(html: str) -> dict:
    """Extract __NEXT_DATA__ JSON embedded in TikTok HTML pages."""
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    return {}


def _extract_sigi_state(html: str) -> dict:
    """Extract SIGI_STATE (server-side rendered data) from TikTok HTML."""
    m = re.search(r'<script id="SIGI_STATE"[^>]*>(.*?)</script>', html, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    return {}


def scrape_tiktok_trending(
    region: str = "US",
    limit: int = 25,
    timeout: int = 30,
) -> dict:
    """
    Fetch TikTok trending videos, hashtags, and sounds.

    Uses TikTok's public discover/trending page — no API key required.
    Returns dict with: region, videos, hashtags, sounds, scraped_at.
    """
    region = REGION_CODES.get(region.lower(), region.upper())

    videos, hashtags, sounds = [], [], []

    # Attempt 1: TikTok trending page (discover)
    try:
        resp = requests.get(
            f"{_BASE}/foryou",
            headers=_HEADERS,
            timeout=timeout,
            allow_redirects=True,
        )
        html = resp.text
        next_data = _extract_next_data(html)
        sigi = _extract_sigi_state(html)
        _parse_sigi_state(sigi, videos, hashtags, sounds, limit)
    except Exception:
        pass

    # Attempt 2: TikTok trending hashtags via discover page
    if not hashtags:
        try:
            resp = requests.get(
                f"{_BASE}/trending",
                headers=_HEADERS,
                timeout=timeout,
                allow_redirects=True,
            )
            html = resp.text
            hashtags = _parse_hashtags_from_html(html)
        except Exception:
            pass

    # Attempt 3: Fallback to known high-signal TikTok challenge endpoints
    if not hashtags:
        hashtags = _fetch_trending_hashtags_fallback(region, timeout)

    if not sounds:
        sounds = _fetch_trending_sounds_fallback(region, timeout)

    return {
        "region": region,
        "videos": videos[:limit],
        "hashtags": hashtags[:50],
        "sounds": sounds[:30],
        "total_videos": len(videos[:limit]),
        "total_hashtags": len(hashtags[:50]),
        "total_sounds": len(sounds[:30]),
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": "tiktok_public",
    }


def _parse_sigi_state(
    sigi: dict,
    videos: list,
    hashtags: list,
    sounds: list,
    limit: int,
) -> None:
    """Parse TikTok's SIGI_STATE embedded JSON for video/hashtag/sound data."""
    item_module = sigi.get("ItemModule", {})
    challenge_module = sigi.get("ChallengeModule", {})
    music_module = sigi.get("MusicModule", {})

    for item_id, item in list(item_module.items())[:limit]:
        video = item.get("video", {})
        author = item.get("author", "")
        music = item.get("music", {})
        stats = item.get("stats", {})
        desc = item.get("desc", "")
        challenges = item.get("challenges", [])

        vid_hashtags = [f"#{c.get('title','')}" for c in challenges if c.get("title")]

        videos.append({
            "id": item_id,
            "url": f"https://www.tiktok.com/@{author}/video/{item_id}",
            "author": f"@{author}",
            "description": desc,
            "hashtags": vid_hashtags,
            "music": {
                "id": music.get("id", ""),
                "title": music.get("title", ""),
                "author": music.get("authorName", ""),
                "is_original": music.get("original", False),
            },
            "stats": {
                "plays": stats.get("playCount", 0),
                "likes": stats.get("diggCount", 0),
                "comments": stats.get("commentCount", 0),
                "shares": stats.get("shareCount", 0),
            },
            "duration": video.get("duration", 0),
        })

    for chal_id, chal in challenge_module.items():
        hashtags.append({
            "tag": f"#{chal.get('title','')}",
            "view_count": chal.get("stats", {}).get("videoCount", 0),
            "video_count": chal.get("stats", {}).get("videoCount", 0),
            "id": chal_id,
        })

    for music_id, music in music_module.items():
        sounds.append({
            "id": music_id,
            "title": music.get("title", ""),
            "author": music.get("authorName", ""),
            "use_count": music.get("stats", {}).get("videoCount", 0),
            "is_original": music.get("original", False),
        })


def _parse_hashtags_from_html(html: str) -> list[dict]:
    """Fallback: extract hashtag mentions from raw HTML."""
    tags = re.findall(r'/tag/([a-zA-Z0-9_]+)', html)
    counts: dict[str, int] = {}
    for t in tags:
        tl = t.lower()
        counts[tl] = counts.get(tl, 0) + 1
    return sorted(
        [{"tag": f"#{k}", "mentions_on_page": v} for k, v in counts.items() if len(k) > 1],
        key=lambda x: x["mentions_on_page"],
        reverse=True,
    )


def _fetch_trending_hashtags_fallback(region: str, timeout: int) -> list[dict]:
    """
    Fetch trending hashtags from TikTok's creative center (public, no auth).
    https://ads.tiktok.com/business/creativecenter/hashtag/trending
    """
    try:
        url = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list"
        params = {
            "period": "7",
            "country_code": region,
            "sort_by": "popular",
            "page": "1",
            "limit": "50",
        }
        headers = {**_HEADERS, "Accept": "application/json"}
        resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("data", {}).get("list", [])
            return [
                {
                    "tag": f"#{item.get('hashtag_name','')}",
                    "rank": item.get("rank", 0),
                    "view_count": item.get("video_views", 0),
                    "video_count": item.get("publish_cnt", 0),
                    "trend": item.get("trend", ""),
                }
                for item in items
            ]
    except Exception:
        pass

    # Hard-coded top evergreen TikTok hashtags as last resort fallback
    return [
        {"tag": "#fyp", "note": "For You Page — top reach driver"},
        {"tag": "#foryou", "note": "For You Page variant"},
        {"tag": "#viral", "note": "Viral content signal"},
        {"tag": "#trending", "note": "General trending signal"},
        {"tag": "#tiktok", "note": "Platform tag"},
        {"tag": "#foryoupage", "note": "FYP variant"},
        {"tag": "#xyzbca", "note": "Algorithm reach tag"},
        {"tag": "#duet", "note": "Duet engagement driver"},
    ]


def _fetch_trending_sounds_fallback(region: str, timeout: int) -> list[dict]:
    """Fetch trending sounds from TikTok Creative Center."""
    try:
        url = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/music/list"
        params = {
            "period": "7",
            "country_code": region,
            "sort_by": "popular",
            "page": "1",
            "limit": "30",
        }
        headers = {**_HEADERS, "Accept": "application/json"}
        resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("data", {}).get("list", [])
            return [
                {
                    "id": item.get("music_id", ""),
                    "title": item.get("music_name", ""),
                    "author": item.get("author", ""),
                    "rank": item.get("rank", 0),
                    "use_count": item.get("video_cnt", 0),
                    "trend": item.get("trend", ""),
                    "tiktok_url": f"https://www.tiktok.com/music/{item.get('music_id','')}",
                }
                for item in items
            ]
    except Exception:
        pass
    return []


def scrape_tiktok_hashtag(hashtag: str, limit: int = 20, timeout: int = 30) -> dict:
    """Fetch videos for a specific TikTok hashtag challenge."""
    tag = hashtag.lstrip("#")
    try:
        resp = requests.get(
            f"{_BASE}/tag/{tag}",
            headers=_HEADERS,
            timeout=timeout,
        )
        html = resp.text
        sigi = _extract_sigi_state(html)
        next_data = _extract_next_data(html)

        videos: list[dict] = []
        hashtag_info: dict = {}

        item_module = sigi.get("ItemModule", {})
        for item_id, item in list(item_module.items())[:limit]:
            author = item.get("author", "")
            stats = item.get("stats", {})
            videos.append({
                "id": item_id,
                "url": f"https://www.tiktok.com/@{author}/video/{item_id}",
                "author": f"@{author}",
                "description": item.get("desc", ""),
                "stats": {
                    "plays": stats.get("playCount", 0),
                    "likes": stats.get("diggCount", 0),
                },
            })

        challenge_module = sigi.get("ChallengeModule", {})
        for _, chal in challenge_module.items():
            if chal.get("title", "").lower() == tag.lower():
                hashtag_info = {
                    "tag": f"#{tag}",
                    "view_count": chal.get("stats", {}).get("videoCount", 0),
                    "description": chal.get("desc", ""),
                }
                break

        return {
            "hashtag": f"#{tag}",
            "info": hashtag_info,
            "videos": videos,
            "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
    except Exception as e:
        return {
            "hashtag": f"#{tag}",
            "error": str(e),
            "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
