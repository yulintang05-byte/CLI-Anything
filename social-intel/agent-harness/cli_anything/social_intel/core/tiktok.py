"""TikTok trend intelligence — trending hashtags, sounds, and videos.

Data sources (in order of preference):
  1. TikTok Research API  — official, requires approved developer access
     https://developers.tiktok.com/products/research-api/
  2. TikTok Discover (public)  — unofficial scrape of discover/trending page
  3. Cached data  — falls back to last saved cache if all else fails

The Research API is the most reliable. Apply at:
  https://developers.tiktok.com/application/research-api
"""

import re
import time
import json
from typing import Optional
from collections import Counter

import requests

from cli_anything.social_intel.utils.backend import (
    get_api_key, load_config, save_cache, load_cache,
)

_RESEARCH_BASE = "https://open.tiktokapis.com/v2"

_HEADERS_WEB = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
}


# ── Auth ─────────────────────────────────────────────────────────

def _research_headers() -> dict:
    token = get_api_key("tiktok")
    if not token:
        raise RuntimeError(
            "TikTok Research API token not set.\n"
            "Run: social-intel auth setup --tiktok-api-key YOUR_TOKEN\n"
            "Apply for access: https://developers.tiktok.com/application/research-api"
        )
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


# ── Research API ─────────────────────────────────────────────────

def search_videos_research(
    keywords: list[str],
    max_count: int = 20,
    region_code: str = "US",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> dict:
    """Query TikTok Research API for videos matching keywords.

    Args:
        keywords: List of search terms (e.g., ["viral", "fyp"]).
        max_count: Number of results (max 100 per request).
        region_code: ISO country code filter.
        start_date: YYYYMMDD format (defaults to 7 days ago).
        end_date: YYYYMMDD format (defaults to today).

    Returns:
        Dict with videos, top hashtags, top sounds.
    """
    if not start_date:
        start_date = time.strftime("%Y%m%d", time.gmtime(time.time() - 7 * 86400))
    if not end_date:
        end_date = time.strftime("%Y%m%d")

    payload = {
        "query": {
            "and": [{"operation": "IN", "field_name": "keyword", "field_values": keywords}],
        },
        "start_date": start_date,
        "end_date": end_date,
        "max_count": min(max_count, 100),
        "cursor": 0,
        "search_id": "",
        "fields": "id,video_description,hashtag_names,music_id,like_count,comment_count,share_count,view_count,region_code",
    }

    r = requests.post(
        f"{_RESEARCH_BASE}/research/video/query/",
        headers=_research_headers(),
        json=payload,
        timeout=20,
    )
    r.raise_for_status()
    data = r.json()

    videos = data.get("data", {}).get("videos", [])
    return _process_research_videos(videos, source="research_api")


def get_trending_hashtags_research(region_code: str = "US") -> dict:
    """Fetch trending hashtags via Research API (requires access).

    Searches for high-engagement recent videos and extracts the most
    common hashtags as a proxy for trending topics.
    """
    result = search_videos_research(
        keywords=["fyp", "foryou", "trending", "viral"],
        max_count=100,
        region_code=region_code,
    )
    return result


# ── Public Discover Scraper ──────────────────────────────────────

def get_trending_public(
    region: str = "US",
    use_cache_on_fail: bool = True,
) -> dict:
    """Scrape TikTok's public discover/trending page.

    Uses TikTok's unofficial trending API endpoint. Falls back to cached
    data if the request fails (TikTok rate-limits aggressively).

    Args:
        region: Country code.
        use_cache_on_fail: Return last cached result if scrape fails.

    Returns:
        Dict with trending hashtags, sounds, and video metadata.
    """
    try:
        return _scrape_trending(region)
    except Exception as exc:
        if use_cache_on_fail:
            cached = load_cache("tiktok_trending")
            if cached:
                cached["_from_cache"] = True
                cached["_cache_error"] = str(exc)
                return cached
        raise RuntimeError(
            f"TikTok public scrape failed: {exc}\n"
            "TikTok heavily restricts automated access. Options:\n"
            "  1. Use TikTok Research API (social-intel tiktok search)\n"
            "  2. Use pyktok: pip install pyktok  (browser-cookie based)\n"
            "  3. Try social-intel tiktok hashtag <tag> for manual lookup"
        ) from exc


def _scrape_trending(region: str) -> dict:
    """Call TikTok's internal trending endpoint (public, no auth)."""
    url = "https://www.tiktok.com/api/discover/music/"
    params = {
        "aid": "1988",
        "app_language": "en",
        "region": region,
        "count": "30",
        "from_page": "discover",
    }
    r = requests.get(url, params=params, headers=_HEADERS_WEB, timeout=15)
    r.raise_for_status()
    data = r.json()

    music_list = data.get("music_list", [])
    sounds = []
    for m in music_list:
        sounds.append({
            "id": m.get("id", ""),
            "title": m.get("title", ""),
            "author": m.get("authorName", ""),
            "duration": m.get("duration", 0),
            "use_count": m.get("userCount", 0),
            "cover_url": m.get("coverThumb", {}).get("url_list", [""])[0],
            "play_url": m.get("playUrl", {}).get("url_list", [""])[0],
        })

    # Also grab hashtag challenges
    hashtags = _scrape_trending_hashtags(region)

    result = {
        "region": region,
        "trending_sounds": sounds[:20],
        "trending_hashtags": hashtags,
        "source": "tiktok_public",
    }
    save_cache("tiktok_trending", result)
    return result


def _scrape_trending_hashtags(region: str) -> list[dict]:
    url = "https://www.tiktok.com/api/discover/challenge/"
    params = {
        "aid": "1988",
        "app_language": "en",
        "region": region,
        "count": "30",
        "from_page": "discover",
    }
    try:
        r = requests.get(url, params=params, headers=_HEADERS_WEB, timeout=15)
        r.raise_for_status()
        data = r.json()
        challenges = data.get("challenge_list", [])
        return [
            {
                "hashtag": c.get("challenge_info", {}).get("cha_name", ""),
                "view_count": c.get("challenge_info", {}).get("view_count", 0),
                "video_count": c.get("challenge_info", {}).get("video_count", 0),
                "description": c.get("challenge_info", {}).get("desc", ""),
            }
            for c in challenges
        ]
    except Exception:
        return []


# ── Hashtag Analyzer ─────────────────────────────────────────────

def analyze_hashtag(tag: str) -> dict:
    """Analyze a TikTok hashtag — view count, video count, competition.

    Uses the public challenge page endpoint.
    """
    tag = tag.lstrip("#")
    url = f"https://www.tiktok.com/api/challenge/detail/"
    params = {
        "aid": "1988",
        "challengeName": tag,
    }
    try:
        r = requests.get(url, params=params, headers=_HEADERS_WEB, timeout=15)
        r.raise_for_status()
        data = r.json()
        info = data.get("challengeInfo", {}).get("challenge", {})
        stats = data.get("challengeInfo", {}).get("stats", {})
        return {
            "hashtag": tag,
            "view_count": stats.get("viewCount", 0),
            "video_count": stats.get("videoCount", 0),
            "description": info.get("desc", ""),
            "competition_level": _competition_tiktok(stats.get("videoCount", 0)),
            "opportunity_score": _opportunity_score(
                stats.get("viewCount", 0),
                stats.get("videoCount", 0),
            ),
        }
    except Exception as exc:
        return {
            "hashtag": tag,
            "error": str(exc),
            "tip": "TikTok may be rate-limiting. Try again in a few minutes.",
        }


def _competition_tiktok(video_count: int) -> str:
    if video_count > 5_000_000:
        return "very_high"
    if video_count > 1_000_000:
        return "high"
    if video_count > 100_000:
        return "medium"
    return "low"


def _opportunity_score(views: int, videos: int) -> str:
    """Views-per-video ratio indicates whether the hashtag converts traffic."""
    if videos == 0:
        return "unknown"
    vpv = views / videos
    if vpv > 50_000:
        return "excellent"
    if vpv > 10_000:
        return "good"
    if vpv > 1_000:
        return "fair"
    return "poor"


# ── Helpers ──────────────────────────────────────────────────────

def _process_research_videos(videos: list, source: str) -> dict:
    all_hashtags: list[str] = []
    music_ids: list[str] = []
    processed = []

    for v in videos:
        tags = v.get("hashtag_names", [])
        all_hashtags.extend([t.lower() for t in tags])
        if v.get("music_id"):
            music_ids.append(str(v["music_id"]))
        processed.append({
            "id": v.get("id", ""),
            "description": v.get("video_description", "")[:200],
            "hashtags": tags,
            "view_count": v.get("view_count", 0),
            "like_count": v.get("like_count", 0),
            "comment_count": v.get("comment_count", 0),
            "share_count": v.get("share_count", 0),
            "region": v.get("region_code", ""),
        })

    top_hashtags = [
        {"hashtag": f"#{t}", "frequency": c}
        for t, c in Counter(all_hashtags).most_common(20)
    ]
    top_sounds = [
        {"music_id": mid, "frequency": c}
        for mid, c in Counter(music_ids).most_common(10)
    ]

    result = {
        "total": len(processed),
        "videos": processed,
        "top_hashtags": top_hashtags,
        "top_sounds": top_sounds,
        "source": source,
    }
    save_cache("tiktok_research", result)
    return result
