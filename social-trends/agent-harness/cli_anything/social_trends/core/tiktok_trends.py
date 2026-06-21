"""TikTok Trends — fetch viral videos, hashtags, and sounds.

Two backends are supported:
  1. TikTok Research API (official, requires approved academic/business account)
     https://developers.tiktok.com/products/research-api/
     social-trends config set tiktok_client_key KEY
     social-trends config set tiktok_client_secret SECRET

  2. RapidAPI / TikTok Scraper proxy (unofficial, requires RapidAPI key)
     social-trends config set rapidapi_key KEY
     Endpoint: "tiktok-scraper7.p.rapidapi.com" (popular community endpoint)

The module auto-selects based on which keys are configured.
"""

import os
import json
import time
from typing import Any, Optional
import requests

from . import config as cfg

_RESEARCH_AUTH_URL = "https://open.tiktokapis.com/v2/oauth/token/"
_RESEARCH_QUERY_URL = "https://open.tiktokapis.com/v2/research/video/query/"
_RAPIDAPI_BASE = "https://tiktok-scraper7.p.rapidapi.com"

_TOKEN_CACHE_KEY = "tiktok_access_token"
_TOKEN_EXPIRY_KEY = "tiktok_token_expiry"


# ── Authentication (Research API) ────────────────────────────────────

def _get_research_token() -> str:
    """Fetch or return cached OAuth2 client-credentials token."""
    now = time.time()
    cached = cfg.get(_TOKEN_CACHE_KEY)
    expiry = cfg.get(_TOKEN_EXPIRY_KEY, 0)
    if cached and now < expiry - 60:
        return cached

    client_key = cfg.require("tiktok_client_key", env_var="TIKTOK_CLIENT_KEY")
    client_secret = cfg.require("tiktok_client_secret", env_var="TIKTOK_CLIENT_SECRET")

    resp = requests.post(
        _RESEARCH_AUTH_URL,
        data={
            "client_key": client_key,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    token = data["access_token"]
    cfg.set_key(_TOKEN_CACHE_KEY, token)
    cfg.set_key(_TOKEN_EXPIRY_KEY, now + data.get("expires_in", 7200))
    return token


def _backend() -> str:
    """Return 'research' or 'rapidapi' based on configured keys."""
    if cfg.get("tiktok_client_key") or os.environ.get("TIKTOK_CLIENT_KEY"):
        return "research"
    if cfg.get("rapidapi_key") or os.environ.get("RAPIDAPI_KEY"):
        return "rapidapi"
    raise ValueError(
        "No TikTok API credentials configured.\n"
        "Option 1 (Official Research API — requires approval):\n"
        "  social-trends config set tiktok_client_key KEY\n"
        "  social-trends config set tiktok_client_secret SECRET\n"
        "Option 2 (RapidAPI proxy — instant access):\n"
        "  social-trends config set rapidapi_key YOUR_RAPIDAPI_KEY\n"
        "  Get a key at https://rapidapi.com (search 'TikTok Scraper')"
    )


# ── Research API backend ──────────────────────────────────────────────

def _research_query_videos(query: dict, limit: int = 20) -> list[dict]:
    token = _get_research_token()
    payload = {
        "query": query,
        "start_date": _days_ago(7),
        "end_date": _today(),
        "max_count": min(limit, 100),
        "fields": "id,create_time,username,region_code,video_description,music_id,like_count,comment_count,share_count,view_count,hashtag_names,voice_to_text",
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    resp = requests.post(_RESEARCH_QUERY_URL, json=payload, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json().get("data", {}).get("videos", [])


def _research_trending(region: str = "US", limit: int = 20) -> list[dict]:
    """High-engagement videos in last 7 days via Research API."""
    query = {
        "and": [
            {"operation": "EQ", "field_name": "region_code", "field_values": [region.upper()]}
        ]
    }
    videos = _research_query_videos(query, limit=limit)
    return [_normalize_research_video(v) for v in videos]


def _normalize_research_video(v: dict) -> dict:
    return {
        "id": v.get("id"),
        "description": v.get("video_description", "")[:120],
        "username": v.get("username"),
        "views": v.get("view_count", 0),
        "likes": v.get("like_count", 0),
        "comments": v.get("comment_count", 0),
        "shares": v.get("share_count", 0),
        "hashtags": [f"#{h}" for h in v.get("hashtag_names", [])],
        "music_id": v.get("music_id"),
        "region": v.get("region_code"),
        "url": f"https://www.tiktok.com/@{v.get('username')}/video/{v.get('id')}",
        "platform": "TikTok",
    }


# ── RapidAPI backend ──────────────────────────────────────────────────

def _rapidapi_headers() -> dict:
    key = cfg.require("rapidapi_key", env_var="RAPIDAPI_KEY")
    return {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": "tiktok-scraper7.p.rapidapi.com",
    }


def _rapidapi_get(path: str, params: dict) -> dict:
    resp = requests.get(
        f"{_RAPIDAPI_BASE}{path}",
        params=params,
        headers=_rapidapi_headers(),
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def _rapidapi_trending(region: str = "US", limit: int = 20) -> list[dict]:
    data = _rapidapi_get("/trending", {"region": region.upper(), "count": min(limit, 30)})
    items = data.get("data", [])
    return [_normalize_rapidapi_video(v) for v in items[:limit]]


def _rapidapi_hashtag_videos(hashtag: str, limit: int = 20) -> list[dict]:
    tag = hashtag.lstrip("#")
    data = _rapidapi_get("/hashtag/videos", {"name": tag, "count": min(limit, 30)})
    items = data.get("data", {}).get("itemList", [])
    return [_normalize_rapidapi_video(v) for v in items[:limit]]


def _rapidapi_trending_sounds(limit: int = 20) -> list[dict]:
    data = _rapidapi_get("/trending/sound", {"count": min(limit, 30)})
    items = data.get("data", [])
    results = []
    for item in items[:limit]:
        music = item.get("music", {})
        stats = item.get("stats", {})
        results.append({
            "id": music.get("id"),
            "title": music.get("title"),
            "author": music.get("authorName"),
            "duration": music.get("duration"),
            "uses": stats.get("playCount", 0),
            "cover": music.get("coverThumb"),
            "platform": "TikTok",
            "url": f"https://www.tiktok.com/music/{music.get('id')}",
        })
    return results


def _normalize_rapidapi_video(v: dict) -> dict:
    desc = v.get("desc", "")
    author = v.get("author", {})
    stats = v.get("stats", {})
    music = v.get("music", {})
    import re
    hashtags = re.findall(r"#(\w+)", desc)
    vid_id = v.get("id")
    username = author.get("uniqueId", "")
    return {
        "id": vid_id,
        "description": desc[:120],
        "username": username,
        "views": stats.get("playCount", 0),
        "likes": stats.get("diggCount", 0),
        "comments": stats.get("commentCount", 0),
        "shares": stats.get("shareCount", 0),
        "hashtags": [f"#{h}" for h in hashtags],
        "music": music.get("title", ""),
        "music_author": music.get("authorName", ""),
        "url": f"https://www.tiktok.com/@{username}/video/{vid_id}",
        "platform": "TikTok",
    }


# ── Public API ────────────────────────────────────────────────────────

def get_trending_videos(region: str = "US", limit: int = 20) -> list[dict]:
    """Return trending TikTok videos with engagement metrics."""
    backend = _backend()
    if backend == "research":
        return _research_trending(region=region, limit=limit)
    return _rapidapi_trending(region=region, limit=limit)


def get_trending_hashtags(region: str = "US", limit: int = 20) -> list[dict]:
    """Aggregate trending hashtags from top TikTok videos."""
    videos = get_trending_videos(region=region, limit=50)
    counts: dict[str, int] = {}
    views: dict[str, int] = {}
    for v in videos:
        for tag in v.get("hashtags", []):
            tag_clean = tag.lstrip("#").lower()
            if len(tag_clean) < 2:
                continue
            counts[tag_clean] = counts.get(tag_clean, 0) + 1
            views[tag_clean] = views.get(tag_clean, 0) + v.get("views", 0)
    results = [
        {
            "hashtag": f"#{tag}",
            "occurrences": count,
            "total_views": views[tag],
            "platform": "TikTok",
            "region": region.upper(),
        }
        for tag, count in sorted(counts.items(), key=lambda x: -x[1])
    ]
    return results[:limit]


def get_hashtag_videos(hashtag: str, limit: int = 20) -> list[dict]:
    """Videos for a specific hashtag (RapidAPI backend only)."""
    backend = _backend()
    if backend == "rapidapi":
        return _rapidapi_hashtag_videos(hashtag, limit=limit)
    # Research API: query by hashtag
    query = {
        "and": [
            {"operation": "IN", "field_name": "hashtag_name",
             "field_values": [hashtag.lstrip("#")]}
        ]
    }
    videos = _research_query_videos(query, limit=limit)
    return [_normalize_research_video(v) for v in videos]


def get_trending_sounds(limit: int = 20) -> list[dict]:
    """Return trending TikTok sounds/music (RapidAPI only)."""
    backend = _backend()
    if backend == "rapidapi":
        return _rapidapi_trending_sounds(limit=limit)
    # Research API doesn't expose sounds directly
    # Aggregate music_id from trending videos as proxy
    videos = get_trending_videos(limit=50)
    music_counts: dict[str, int] = {}
    for v in videos:
        mid = v.get("music_id") or v.get("music", "")
        if mid:
            music_counts[str(mid)] = music_counts.get(str(mid), 0) + 1
    results = [
        {"id": mid, "uses": count, "platform": "TikTok",
         "note": "music_id from Research API — use RapidAPI for full metadata"}
        for mid, count in sorted(music_counts.items(), key=lambda x: -x[1])
    ]
    return results[:limit]


def _today() -> str:
    from datetime import date
    return date.today().strftime("%Y%m%d")


def _days_ago(n: int) -> str:
    from datetime import date, timedelta
    return (date.today() - timedelta(days=n)).strftime("%Y%m%d")
