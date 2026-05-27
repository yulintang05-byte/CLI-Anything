"""TikTok trend scraper.

Pulls trending data from three sources in priority order:
  1. TikTok Creative Center public API (trending hashtags & sounds, no auth required)
  2. TikTok Discover page web scrape
  3. Curated static fallback so the CLI always returns something useful

No authentication or API key is required.
"""

from __future__ import annotations

import json
import re
from typing import Any

from cli_anything.social_trends.utils.scraper_backend import get_json, get_html

# ── TikTok Creative Center ────────────────────────────────────────────────────

_CC_BASE = "https://ads.tiktok.com/business/creativecenter"
_CC_HASHTAGS_URL = f"{_CC_BASE}/api/pc/trending/hashtag/list"
_CC_SOUNDS_URL = f"{_CC_BASE}/api/pc/trending/sound/list"
_CC_VIDEOS_URL = f"{_CC_BASE}/api/pc/trending/video/list"

_CC_HEADERS = {
    "Referer": "https://ads.tiktok.com/business/creativecenter/trending-hashtags/pc/en",
    "Origin": "https://ads.tiktok.com",
    "Accept": "application/json, text/plain, */*",
}


def _cc_params(region: str = "US", period: int = 7) -> dict:
    """Base query params for Creative Center API calls."""
    return {
        "period": period,        # 7 or 30 days
        "region": region.upper(),
        "country_code": region.upper(),
        "page": 1,
        "limit": 30,
        "sort_by": "popular",
    }


def fetch_trending_hashtags_cc(region: str = "US",
                               period: int = 7) -> list[dict]:
    """Trending hashtags from TikTok Creative Center."""
    try:
        params = _cc_params(region, period)
        data = get_json(_CC_HASHTAGS_URL, params=params,
                        extra_headers=_CC_HEADERS, cache_ttl=3600)
        items = (data.get("data", {}).get("list", [])
                 or data.get("data", [])
                 or [])
        return [_parse_cc_hashtag(item) for item in items]
    except Exception:
        return []


def fetch_trending_sounds_cc(region: str = "US",
                             period: int = 7) -> list[dict]:
    """Trending sounds/music from TikTok Creative Center."""
    try:
        params = _cc_params(region, period)
        data = get_json(_CC_SOUNDS_URL, params=params,
                        extra_headers=_CC_HEADERS, cache_ttl=3600)
        items = (data.get("data", {}).get("list", [])
                 or data.get("data", [])
                 or [])
        return [_parse_cc_sound(item) for item in items]
    except Exception:
        return []


def fetch_trending_videos_cc(region: str = "US",
                             period: int = 7) -> list[dict]:
    """Trending videos from TikTok Creative Center."""
    try:
        params = _cc_params(region, period)
        data = get_json(_CC_VIDEOS_URL, params=params,
                        extra_headers=_CC_HEADERS, cache_ttl=3600)
        items = (data.get("data", {}).get("list", [])
                 or data.get("data", [])
                 or [])
        return [_parse_cc_video(item) for item in items]
    except Exception:
        return []


def _parse_cc_hashtag(item: dict) -> dict:
    return {
        "hashtag": "#" + item.get("hashtag_name", item.get("name", "")).lstrip("#"),
        "views": item.get("video_views", item.get("view_cnt", 0)),
        "posts": item.get("publish_cnt", item.get("video_cnt", 0)),
        "trend": item.get("trend", ""),
        "rank": item.get("rank", 0),
        "source": "tiktok_creative_center",
    }


def _parse_cc_sound(item: dict) -> dict:
    return {
        "sound_id": str(item.get("music_id", item.get("id", ""))),
        "title": item.get("music_title", item.get("title", "")),
        "author": item.get("author_name", item.get("artist", "")),
        "usage_count": item.get("video_cnt", item.get("use_cnt", 0)),
        "duration": item.get("duration", 0),
        "cover": item.get("cover", ""),
        "trend": item.get("trend", ""),
        "source": "tiktok_creative_center",
    }


def _parse_cc_video(item: dict) -> dict:
    return {
        "video_id": str(item.get("video_id", item.get("id", ""))),
        "title": item.get("video_title", item.get("desc", "")),
        "author": item.get("author_name", ""),
        "like_count": item.get("digg_count", item.get("like_cnt", 0)),
        "comment_count": item.get("comment_cnt", 0),
        "share_count": item.get("share_cnt", 0),
        "play_count": item.get("play_cnt", 0),
        "hashtags": [
            "#" + h.lstrip("#")
            for h in item.get("hashtag_list", [])
        ],
        "source": "tiktok_creative_center",
    }


# ── Web scrape fallback ───────────────────────────────────────────────────────

def fetch_trending_hashtags_web() -> list[dict]:
    """Scrape TikTok Discover page for trending hashtags."""
    try:
        soup = get_html("https://www.tiktok.com/discover",
                        extra_headers={"Referer": "https://www.tiktok.com/"},
                        cache_ttl=3600)
        results = []
        for tag in soup.find_all(href=re.compile(r"/tag/")):
            name = tag.get_text(strip=True).strip("#")
            if name:
                results.append({
                    "hashtag": f"#{name}",
                    "source": "tiktok_web",
                })
        return list({r["hashtag"]: r for r in results}.values())[:30]
    except Exception:
        return []


# ── Curated fallback (always succeeds) ───────────────────────────────────────
# Updated periodically; serves as a useful baseline when live scraping fails.

_STATIC_HASHTAGS = [
    {"hashtag": "#fyp",             "category": "discovery",   "avg_views": "900B+"},
    {"hashtag": "#foryoupage",      "category": "discovery",   "avg_views": "600B+"},
    {"hashtag": "#viral",           "category": "discovery",   "avg_views": "300B+"},
    {"hashtag": "#trending",        "category": "discovery",   "avg_views": "200B+"},
    {"hashtag": "#foryou",          "category": "discovery",   "avg_views": "150B+"},
    {"hashtag": "#tiktok",          "category": "platform",    "avg_views": "100B+"},
    {"hashtag": "#duet",            "category": "engagement",  "avg_views": "50B+"},
    {"hashtag": "#stitch",          "category": "engagement",  "avg_views": "45B+"},
    {"hashtag": "#howto",           "category": "education",   "avg_views": "40B+"},
    {"hashtag": "#tutorial",        "category": "education",   "avg_views": "38B+"},
    {"hashtag": "#aesthetic",       "category": "lifestyle",   "avg_views": "35B+"},
    {"hashtag": "#motivation",      "category": "lifestyle",   "avg_views": "33B+"},
    {"hashtag": "#fitness",         "category": "health",      "avg_views": "30B+"},
    {"hashtag": "#workout",         "category": "health",      "avg_views": "28B+"},
    {"hashtag": "#recipe",          "category": "food",        "avg_views": "26B+"},
    {"hashtag": "#foodtiktok",      "category": "food",        "avg_views": "24B+"},
    {"hashtag": "#travel",          "category": "travel",      "avg_views": "22B+"},
    {"hashtag": "#fashion",         "category": "fashion",     "avg_views": "20B+"},
    {"hashtag": "#ootd",            "category": "fashion",     "avg_views": "18B+"},
    {"hashtag": "#booktok",         "category": "niche",       "avg_views": "16B+"},
    {"hashtag": "#financetiktok",   "category": "niche",       "avg_views": "14B+"},
    {"hashtag": "#studytok",        "category": "niche",       "avg_views": "12B+"},
    {"hashtag": "#smallbusiness",   "category": "business",    "avg_views": "10B+"},
    {"hashtag": "#entrepreneur",    "category": "business",    "avg_views": "9B+"},
    {"hashtag": "#sidehustle",      "category": "business",    "avg_views": "8B+"},
]

_STATIC_SOUNDS = [
    {"title": "As It Was", "author": "Harry Styles", "category": "pop"},
    {"title": "Calm Down", "author": "Rema & Selena Gomez", "category": "pop"},
    {"title": "Flowers", "author": "Miley Cyrus", "category": "pop"},
    {"title": "Miley Cyrus - Flowers (sped up)", "author": "Sped Up Nation", "category": "sped-up"},
    {"title": "Die For You", "author": "The Weeknd", "category": "r&b"},
    {"title": "Creepin'", "author": "Metro Boomin", "category": "hip-hop"},
    {"title": "Escapism.", "author": "RAYE", "category": "pop"},
    {"title": "Golden Hour", "author": "JVKE", "category": "pop"},
    {"title": "Made You Look", "author": "Meghan Trainor", "category": "pop"},
    {"title": "Superhero (Heroes & Villains)", "author": "Metro Boomin", "category": "hip-hop"},
]


# ── Unified entry points ──────────────────────────────────────────────────────

def get_trending_hashtags(region: str = "US", period: int = 7) -> list[dict]:
    """Return trending TikTok hashtags, with fallback chain."""
    results = fetch_trending_hashtags_cc(region, period)
    if not results:
        results = fetch_trending_hashtags_web()
    if not results:
        results = [dict(h, source="static_fallback") for h in _STATIC_HASHTAGS]
    return results


def get_trending_sounds(region: str = "US", period: int = 7) -> list[dict]:
    """Return trending TikTok sounds, with fallback chain."""
    results = fetch_trending_sounds_cc(region, period)
    if not results:
        results = [dict(s, source="static_fallback") for s in _STATIC_SOUNDS]
    return results


def get_trending_videos(region: str = "US", period: int = 7) -> list[dict]:
    """Return trending TikTok videos."""
    return fetch_trending_videos_cc(region, period)
