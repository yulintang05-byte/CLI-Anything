"""TikTok viral trend scraper.

Supports two backends:
  1. TikTok Research API (official, requires approved access)
  2. Web scraping fallback via requests + BeautifulSoup

Set TIKTOK_API_KEY + TIKTOK_API_SECRET for the official Research API.
Without credentials the scraper uses publicly available data endpoints.
"""

import os
import re
import json
import time
import random
from typing import Optional
import requests
from bs4 import BeautifulSoup


TIKTOK_RESEARCH_API = "https://open.tiktokapis.com/v2"
TIKTOK_WEB_BASE = "https://www.tiktok.com"

_TOKEN_CACHE: dict = {}


# ── Auth ─────────────────────────────────────────────────────────────────────

def _get_research_token() -> Optional[str]:
    """Fetch OAuth2 bearer token for TikTok Research API."""
    client_key = os.environ.get("TIKTOK_API_KEY")
    client_secret = os.environ.get("TIKTOK_API_SECRET")
    if not (client_key and client_secret):
        return None

    now = time.time()
    if _TOKEN_CACHE.get("expires_at", 0) > now + 60:
        return _TOKEN_CACHE.get("token")

    resp = requests.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        data={
            "client_key": client_key,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        },
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    token = data.get("access_token")
    _TOKEN_CACHE["token"] = token
    _TOKEN_CACHE["expires_at"] = now + data.get("expires_in", 7200)
    return token


def _has_research_api() -> bool:
    return bool(os.environ.get("TIKTOK_API_KEY") and os.environ.get("TIKTOK_API_SECRET"))


# ── Research API backend ──────────────────────────────────────────────────────

def _research_query(endpoint: str, payload: dict) -> dict:
    token = _get_research_token()
    if not token:
        raise RuntimeError("TikTok Research API credentials not configured")
    resp = requests.post(
        f"{TIKTOK_RESEARCH_API}/{endpoint}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()


def _research_get_trending_hashtags(max_results: int = 30) -> list[dict]:
    """Use Research API to get trending hashtags by video count."""
    # Research API: query videos created in the last 7 days, aggregate by hashtag
    payload = {
        "query": {
            "and": [
                {"operation": "GT", "field_name": "view_count", "field_values": ["100000"]}
            ]
        },
        "start_date": _days_ago_str(7),
        "end_date": _today_str(),
        "max_count": min(max_results, 100),
        "fields": "hashtag_names,view_count,like_count,share_count,music_id",
    }
    data = _research_query("research/video/query/", payload)
    hashtag_stats: dict[str, dict] = {}
    for video in data.get("data", {}).get("videos", []):
        for tag in video.get("hashtag_names", []):
            tag_lower = tag.lower()
            if tag_lower not in hashtag_stats:
                hashtag_stats[tag_lower] = {"video_count": 0, "total_views": 0, "total_likes": 0}
            hashtag_stats[tag_lower]["video_count"] += 1
            hashtag_stats[tag_lower]["total_views"] += video.get("view_count", 0)
            hashtag_stats[tag_lower]["total_likes"] += video.get("like_count", 0)

    ranked = sorted(hashtag_stats.items(), key=lambda x: x[1]["total_views"], reverse=True)
    return [
        {
            "hashtag": f"#{tag}",
            "video_count": stats["video_count"],
            "total_views": stats["total_views"],
            "avg_views": stats["total_views"] // max(stats["video_count"], 1),
            "total_likes": stats["total_likes"],
        }
        for tag, stats in ranked[:max_results]
    ]


def _research_get_trending_sounds(max_results: int = 20) -> list[dict]:
    payload = {
        "query": {
            "and": [
                {"operation": "GT", "field_name": "view_count", "field_values": ["500000"]}
            ]
        },
        "start_date": _days_ago_str(7),
        "end_date": _today_str(),
        "max_count": 100,
        "fields": "music_id,view_count,like_count",
    }
    data = _research_query("research/video/query/", payload)
    music_stats: dict[str, dict] = {}
    for video in data.get("data", {}).get("videos", []):
        mid = str(video.get("music_id", ""))
        if not mid:
            continue
        if mid not in music_stats:
            music_stats[mid] = {"video_count": 0, "total_views": 0}
        music_stats[mid]["video_count"] += 1
        music_stats[mid]["total_views"] += video.get("view_count", 0)

    ranked = sorted(music_stats.items(), key=lambda x: x[1]["total_views"], reverse=True)
    return [
        {
            "music_id": mid,
            "video_count": stats["video_count"],
            "total_views": stats["total_views"],
            "tiktok_url": f"https://www.tiktok.com/music/-{mid}",
        }
        for mid, stats in ranked[:max_results]
    ]


# ── Web scrape backend ────────────────────────────────────────────────────────

_SCRAPE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
}


def _scrape_tiktok_trending() -> list[dict]:
    """Scrape TikTok trending page for hashtags and metadata."""
    try:
        resp = requests.get(
            f"{TIKTOK_WEB_BASE}/trending",
            headers=_SCRAPE_HEADERS,
            timeout=20,
        )
        resp.raise_for_status()
        return _parse_tiktok_next_data(resp.text)
    except Exception:
        return _scrape_tiktok_hashtag_page("trending")


def _parse_tiktok_next_data(html: str) -> list[dict]:
    """Extract __NEXT_DATA__ JSON from TikTok page."""
    soup = BeautifulSoup(html, "lxml")
    script = soup.find("script", {"id": "__NEXT_DATA__"})
    if not script:
        return []
    try:
        data = json.loads(script.string)
        items = (
            data.get("props", {})
            .get("pageProps", {})
            .get("items", [])
        )
        results = []
        for item in items[:50]:
            desc = item.get("desc", "")
            stats = item.get("stats", {})
            music = item.get("music", {})
            results.append(
                {
                    "video_id": item.get("id", ""),
                    "description": desc[:200],
                    "hashtags": _extract_hashtags(desc),
                    "views": stats.get("playCount", 0),
                    "likes": stats.get("diggCount", 0),
                    "shares": stats.get("shareCount", 0),
                    "comments": stats.get("commentCount", 0),
                    "music_title": music.get("title", ""),
                    "music_author": music.get("authorName", ""),
                    "music_id": str(music.get("id", "")),
                    "author": item.get("author", {}).get("uniqueId", ""),
                    "url": f"https://www.tiktok.com/@{item.get('author', {}).get('uniqueId', '')}/"
                    f"video/{item.get('id', '')}",
                }
            )
        return results
    except (json.JSONDecodeError, KeyError):
        return []


def _scrape_tiktok_hashtag_page(hashtag: str) -> list[dict]:
    """Scrape a TikTok hashtag page and extract video metadata."""
    clean = hashtag.lstrip("#")
    try:
        resp = requests.get(
            f"{TIKTOK_WEB_BASE}/tag/{clean}",
            headers=_SCRAPE_HEADERS,
            timeout=20,
        )
        resp.raise_for_status()
        results = _parse_tiktok_next_data(resp.text)
        for r in results:
            r["source_hashtag"] = f"#{clean}"
        return results
    except Exception:
        return []


def _aggregate_hashtags_from_videos(videos: list[dict], max_results: int = 30) -> list[dict]:
    hashtag_stats: dict[str, dict] = {}
    for v in videos:
        for tag in v.get("hashtags", []):
            tag_lower = tag.lower()
            if tag_lower not in hashtag_stats:
                hashtag_stats[tag_lower] = {"video_count": 0, "total_views": 0, "total_likes": 0}
            hashtag_stats[tag_lower]["video_count"] += 1
            hashtag_stats[tag_lower]["total_views"] += v.get("views", 0)
            hashtag_stats[tag_lower]["total_likes"] += v.get("likes", 0)

    ranked = sorted(hashtag_stats.items(), key=lambda x: x[1]["total_views"], reverse=True)
    return [
        {
            "hashtag": f"#{tag}",
            "video_count": stats["video_count"],
            "total_views": stats["total_views"],
            "avg_views": stats["total_views"] // max(stats["video_count"], 1),
        }
        for tag, stats in ranked[:max_results]
    ]


def _aggregate_sounds_from_videos(videos: list[dict], max_results: int = 20) -> list[dict]:
    sound_stats: dict[str, dict] = {}
    for v in videos:
        mid = v.get("music_id", "")
        if not mid:
            continue
        if mid not in sound_stats:
            sound_stats[mid] = {
                "title": v.get("music_title", ""),
                "author": v.get("music_author", ""),
                "video_count": 0,
                "total_views": 0,
            }
        sound_stats[mid]["video_count"] += 1
        sound_stats[mid]["total_views"] += v.get("views", 0)

    ranked = sorted(sound_stats.items(), key=lambda x: x[1]["total_views"], reverse=True)
    return [
        {
            "music_id": mid,
            "title": stats["title"],
            "author": stats["author"],
            "video_count": stats["video_count"],
            "total_views": stats["total_views"],
            "tiktok_url": f"https://www.tiktok.com/music/-{mid}",
        }
        for mid, stats in ranked[:max_results]
    ]


# ── Public API ────────────────────────────────────────────────────────────────

def get_trending_hashtags(max_results: int = 30) -> list[dict]:
    """Return ranked trending TikTok hashtags with view and like counts."""
    if _has_research_api():
        return _research_get_trending_hashtags(max_results)
    videos = _scrape_tiktok_trending()
    return _aggregate_hashtags_from_videos(videos, max_results)


def get_trending_sounds(max_results: int = 20) -> list[dict]:
    """Return trending TikTok sounds/music with usage counts."""
    if _has_research_api():
        return _research_get_trending_sounds(max_results)
    videos = _scrape_tiktok_trending()
    return _aggregate_sounds_from_videos(videos, max_results)


def get_trending_videos(hashtag: Optional[str] = None, max_results: int = 20) -> list[dict]:
    """Return trending TikTok videos, optionally filtered by hashtag."""
    if hashtag:
        videos = _scrape_tiktok_hashtag_page(hashtag)
    else:
        videos = _scrape_tiktok_trending()
    return sorted(videos, key=lambda x: x.get("views", 0), reverse=True)[:max_results]


def search_by_keyword(keyword: str, max_results: int = 20) -> list[dict]:
    """Search TikTok content by keyword (uses hashtag page as proxy)."""
    videos = _scrape_tiktok_hashtag_page(keyword)
    if not videos:
        videos = get_trending_videos(hashtag=keyword, max_results=max_results)
    return videos[:max_results]


def get_niche_trends(niche: str) -> dict:
    """Return combined hashtag + sound trends for a specific niche."""
    videos = _scrape_tiktok_hashtag_page(niche)
    return {
        "niche": niche,
        "top_hashtags": _aggregate_hashtags_from_videos(videos, 15),
        "top_sounds": _aggregate_sounds_from_videos(videos, 10),
        "top_videos": sorted(videos, key=lambda x: x.get("views", 0), reverse=True)[:5],
        "total_videos_analyzed": len(videos),
    }


# ── helpers ───────────────────────────────────────────────────────────────────

def _extract_hashtags(text: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"#(\w+)", text)))


def _days_ago_str(days: int) -> str:
    from datetime import datetime, timedelta, timezone
    dt = datetime.now(timezone.utc) - timedelta(days=days)
    return dt.strftime("%Y%m%d")


def _today_str() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y%m%d")
