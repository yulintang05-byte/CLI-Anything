"""TikTok Creative Center scraper — trending hashtags, sounds, and videos.

Uses TikTok's public Creative Center API (no auth required for trend data).
Respects rate limits with configurable delays between requests.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    import sys
    print("requests library not found. Install with: pip install requests", file=sys.stderr)
    raise

CREATIVE_CENTER_BASE = "https://ads.tiktok.com/creative_radar_api/v1"

COUNTRY_CODES = {
    "us": "US", "uk": "GB", "ca": "CA", "au": "AU",
    "de": "DE", "fr": "FR", "jp": "JP", "br": "BR",
    "in": "IN", "mx": "MX", "id": "ID", "ph": "PH",
}

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://ads.tiktok.com/",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}


def _get(url: str, params: dict | None = None, timeout: int = 15) -> dict:
    resp = requests.get(url, params=params, headers=_HEADERS, timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(
            f"TikTok Creative Center request failed (HTTP {resp.status_code}): {url}"
        )
    data = resp.json()
    code = data.get("code", data.get("status_code", 0))
    if code != 0:
        msg = data.get("message", data.get("msg", "unknown error"))
        raise RuntimeError(f"TikTok API error {code}: {msg}")
    return data


def trending_hashtags(
    country: str = "US",
    period: int = 7,
    limit: int = 30,
) -> list[dict]:
    """Fetch trending hashtags from TikTok Creative Center.

    Args:
        country: Country code (US, GB, CA, AU, DE, FR, JP, BR...).
        period: Time window in days (1, 7, 30).
        limit: Max results to return.

    Returns:
        List of hashtag dicts with name, rank, video_count, view_count, trend.
    """
    country = country.upper()
    url = f"{CREATIVE_CENTER_BASE}/popular_trend/hashtag/list"
    params = {
        "period": period,
        "country_code": country,
        "page": 1,
        "limit": min(limit, 50),
    }
    data = _get(url, params)
    items = data.get("data", {}).get("list", [])
    results = []
    for item in items:
        results.append({
            "rank": item.get("rank", 0),
            "name": item.get("hashtag_name", ""),
            "id": item.get("hashtag_id", ""),
            "video_count": item.get("publish_cnt", 0),
            "view_count": item.get("video_views", 0),
            "trend": item.get("trend", ""),
            "country": country,
            "period_days": period,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        })
    return results[:limit]


def trending_sounds(
    country: str = "US",
    period: int = 7,
    limit: int = 30,
) -> list[dict]:
    """Fetch trending sounds/music from TikTok Creative Center.

    Returns:
        List of sound dicts with title, artist, usage_count, rank, play_url.
    """
    country = country.upper()
    url = f"{CREATIVE_CENTER_BASE}/popular_trend/music/list"
    params = {
        "period": period,
        "country_code": country,
        "page": 1,
        "limit": min(limit, 50),
    }
    data = _get(url, params)
    items = data.get("data", {}).get("list", [])
    results = []
    for item in items:
        results.append({
            "rank": item.get("rank", 0),
            "title": item.get("music_name", ""),
            "artist": item.get("author", ""),
            "id": item.get("music_id", ""),
            "usage_count": item.get("video_cnt", 0),
            "play_url": item.get("play_url", ""),
            "cover_url": item.get("cover_url", ""),
            "duration_sec": item.get("duration", 0),
            "trend": item.get("trend", ""),
            "country": country,
            "period_days": period,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        })
    return results[:limit]


def trending_videos(
    country: str = "US",
    period: int = 7,
    limit: int = 20,
) -> list[dict]:
    """Fetch trending videos from TikTok Creative Center.

    Returns:
        List of video dicts with id, desc, author, stats, hashtags, music.
    """
    country = country.upper()
    url = f"{CREATIVE_CENTER_BASE}/popular_trend/video/list"
    params = {
        "period": period,
        "country_code": country,
        "page": 1,
        "limit": min(limit, 30),
    }
    data = _get(url, params)
    items = data.get("data", {}).get("list", [])
    results = []
    for item in items:
        results.append({
            "rank": item.get("rank", 0),
            "video_id": item.get("item_id", ""),
            "description": item.get("desc", ""),
            "author": item.get("author_name", ""),
            "author_followers": item.get("follower_cnt", 0),
            "like_count": item.get("like_cnt", 0),
            "comment_count": item.get("comment_cnt", 0),
            "share_count": item.get("share_cnt", 0),
            "view_count": item.get("play_cnt", 0),
            "hashtags": [h.get("name", "") for h in item.get("hashtag_list", [])],
            "music_title": item.get("music_info", {}).get("music_name", ""),
            "music_artist": item.get("music_info", {}).get("author", ""),
            "cover_url": item.get("cover_url", ""),
            "country": country,
            "period_days": period,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        })
    return results[:limit]


def trending_creators(
    country: str = "US",
    period: int = 7,
    limit: int = 20,
) -> list[dict]:
    """Fetch trending creators from TikTok Creative Center."""
    country = country.upper()
    url = f"{CREATIVE_CENTER_BASE}/popular_trend/creator/list"
    params = {
        "period": period,
        "country_code": country,
        "page": 1,
        "limit": min(limit, 30),
    }
    data = _get(url, params)
    items = data.get("data", {}).get("list", [])
    results = []
    for item in items:
        results.append({
            "rank": item.get("rank", 0),
            "username": item.get("nick_name", ""),
            "user_id": item.get("author_id", ""),
            "followers": item.get("follower_cnt", 0),
            "follower_growth": item.get("follower_growth_rate", 0),
            "avg_views": item.get("avg_play_cnt", 0),
            "like_count": item.get("like_cnt", 0),
            "avatar_url": item.get("avatar_url", ""),
            "country": country,
            "period_days": period,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        })
    return results[:limit]


def full_trend_report(
    country: str = "US",
    period: int = 7,
    hashtag_limit: int = 20,
    sound_limit: int = 20,
    video_limit: int = 10,
    creator_limit: int = 10,
    delay: float = 0.5,
) -> dict:
    """Fetch all trend categories and return a consolidated report.

    Args:
        delay: Seconds to wait between API calls (be a polite scraper).
    """
    report: dict[str, Any] = {
        "platform": "tiktok",
        "country": country.upper(),
        "period_days": period,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "hashtags": [],
        "sounds": [],
        "videos": [],
        "creators": [],
        "errors": [],
    }

    for category, fn, limit in [
        ("hashtags", lambda: trending_hashtags(country, period, hashtag_limit), hashtag_limit),
        ("sounds", lambda: trending_sounds(country, period, sound_limit), sound_limit),
        ("videos", lambda: trending_videos(country, period, video_limit), video_limit),
        ("creators", lambda: trending_creators(country, period, creator_limit), creator_limit),
    ]:
        try:
            report[category] = fn()
        except Exception as e:
            report["errors"].append({"category": category, "error": str(e)})
        if delay > 0:
            time.sleep(delay)

    return report
