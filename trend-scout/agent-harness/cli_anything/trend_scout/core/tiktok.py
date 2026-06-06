"""TikTok trend scraping via TikTok's web API endpoints.

Uses browser-like headers to access TikTok's public trending data without
requiring login or API keys. Falls back to static curated trend data when
live scraping is blocked by device-integrity checks.
"""

import json
import re
import time
import urllib.request
import urllib.error
import urllib.parse
from typing import Any


# ── TikTok API constants ──────────────────────────────────────────────────────

_BASE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
    "Origin": "https://www.tiktok.com",
}

# TikTok's public discovery API (no auth needed for public content)
_DISCOVERY_API = "https://www.tiktok.com/api/discover/type/"
_HASHTAG_SUGGEST = "https://www.tiktok.com/api/seo/suggest/keyword/"
_TRENDING_API = "https://www.tiktok.com/api/item_list/"

# Country codes for trending lookup
REGIONS = {
    "us": "US",
    "uk": "GB",
    "ca": "CA",
    "au": "AU",
    "global": "",
}


# ── HTTP helper ───────────────────────────────────────────────────────────────

def _get_json(url: str, params: dict | None = None) -> dict | list:
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=_BASE_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError, Exception):
        return {}


# ── Hashtag scraping ──────────────────────────────────────────────────────────

def _fetch_challenge_info(hashtag: str) -> dict:
    """Look up challenge/hashtag stats from TikTok."""
    data = _get_json(
        "https://www.tiktok.com/api/challenge/detail/",
        {"challengeName": hashtag.lstrip("#"), "aid": "1988"},
    )
    if not isinstance(data, dict):
        return {}
    challenge = data.get("challengeInfo", {}).get("challenge", {})
    stats = data.get("challengeInfo", {}).get("stats", {})
    return {
        "name": challenge.get("title", hashtag.lstrip("#")),
        "description": challenge.get("desc", ""),
        "video_count": stats.get("videoCount", 0),
        "view_count": stats.get("viewCount", 0),
    }


def _scrape_trending_hashtags_from_discover() -> list[dict]:
    """Hit TikTok's discover endpoint to get trending hashtag cards."""
    data = _get_json(
        _DISCOVERY_API,
        {"discoverType": 0, "needItemList": False, "keyWord": "", "offset": 0, "count": 30, "useRecommend": False},
    )
    if not isinstance(data, dict):
        return []

    hashtag_list = data.get("hashtagList") or data.get("body") or []
    results = []
    for item in hashtag_list:
        if not isinstance(item, dict):
            continue
        challenge = item.get("challengeInfo", {}).get("challenge", item)
        stats = item.get("challengeInfo", {}).get("stats", item)
        results.append({
            "name": challenge.get("title") or item.get("title", ""),
            "video_count": stats.get("videoCount") or item.get("videoCount", 0),
            "view_count": stats.get("viewCount") or item.get("viewCount", 0),
        })
    return results


# ── Trending sounds ───────────────────────────────────────────────────────────

def _fetch_trending_sounds(region: str = "US", limit: int = 20) -> list[dict]:
    """Fetch trending music/sounds from TikTok."""
    params = {
        "aid": "1988",
        "app_language": "en",
        "region": region,
        "type": 2,  # 2 = music trending
        "count": limit,
        "offset": 0,
    }
    data = _get_json(_DISCOVERY_API, params)
    if not isinstance(data, dict):
        return []

    music_list = data.get("musicList") or data.get("body") or []
    results = []
    for item in music_list:
        if not isinstance(item, dict):
            continue
        music = item.get("music") or item
        results.append({
            "id": music.get("id", ""),
            "title": music.get("title", ""),
            "artist": music.get("authorName", ""),
            "duration": music.get("duration", 0),
            "play_url": music.get("playUrl", ""),
            "cover_url": music.get("coverThumb", ""),
            "video_count": item.get("stats", {}).get("videoCount", 0),
        })
    return results


# ── Trending videos ───────────────────────────────────────────────────────────

def _fetch_trending_videos(region: str = "US", limit: int = 20) -> list[dict]:
    """Fetch trending videos from TikTok's item list."""
    params = {
        "aid": "1988",
        "app_language": "en",
        "region": region,
        "feedType": "0",
        "count": limit,
    }
    data = _get_json(_TRENDING_API, params)
    if not isinstance(data, dict):
        return []

    item_list = data.get("itemList") or []
    results = []
    for item in item_list:
        if not isinstance(item, dict):
            continue
        desc = item.get("desc", "")
        music = item.get("music") or {}
        author = item.get("author") or {}
        stats = item.get("stats") or {}
        hashtags = re.findall(r"#(\w+)", desc)

        results.append({
            "id": item.get("id", ""),
            "description": desc,
            "author": author.get("uniqueId", ""),
            "author_followers": item.get("authorStats", {}).get("followerCount", 0),
            "play_count": stats.get("playCount", 0),
            "like_count": stats.get("diggCount", 0),
            "comment_count": stats.get("commentCount", 0),
            "share_count": stats.get("shareCount", 0),
            "hashtags": hashtags,
            "sound": {
                "title": music.get("title", ""),
                "artist": music.get("authorName", ""),
                "id": music.get("id", ""),
            },
            "url": f"https://www.tiktok.com/@{author.get('uniqueId', '')}/ video/{item.get('id', '')}",
            "create_time": item.get("createTime", 0),
        })
    return results


# ── Curated fallback data (used when live scraping is blocked) ─────────────

_FALLBACK_HASHTAGS = [
    {"name": "fyp", "video_count": 50_000_000, "view_count": 5_000_000_000},
    {"name": "foryou", "video_count": 40_000_000, "view_count": 4_000_000_000},
    {"name": "foryoupage", "video_count": 35_000_000, "view_count": 3_500_000_000},
    {"name": "viral", "video_count": 30_000_000, "view_count": 3_000_000_000},
    {"name": "trending", "video_count": 20_000_000, "view_count": 2_000_000_000},
    {"name": "tiktok", "video_count": 15_000_000, "view_count": 1_500_000_000},
    {"name": "video", "video_count": 10_000_000, "view_count": 1_000_000_000},
    {"name": "funny", "video_count": 8_000_000, "view_count": 800_000_000},
    {"name": "dance", "video_count": 7_000_000, "view_count": 700_000_000},
    {"name": "love", "video_count": 6_000_000, "view_count": 600_000_000},
    {"name": "music", "video_count": 5_500_000, "view_count": 550_000_000},
    {"name": "life", "video_count": 5_000_000, "view_count": 500_000_000},
    {"name": "challenge", "video_count": 4_500_000, "view_count": 450_000_000},
    {"name": "fashion", "video_count": 4_000_000, "view_count": 400_000_000},
    {"name": "beauty", "video_count": 3_500_000, "view_count": 350_000_000},
    {"name": "food", "video_count": 3_000_000, "view_count": 300_000_000},
    {"name": "fitness", "video_count": 2_500_000, "view_count": 250_000_000},
    {"name": "travel", "video_count": 2_000_000, "view_count": 200_000_000},
    {"name": "comedy", "video_count": 1_800_000, "view_count": 180_000_000},
    {"name": "motivation", "video_count": 1_500_000, "view_count": 150_000_000},
]

_FALLBACK_SOUNDS = [
    {"title": "Espresso", "artist": "Sabrina Carpenter", "video_count": 2_500_000},
    {"title": "APT.", "artist": "ROSÉ & Bruno Mars", "video_count": 2_100_000},
    {"title": "Birds of a Feather", "artist": "Billie Eilish", "video_count": 1_800_000},
    {"title": "Die With a Smile", "artist": "Lady Gaga & Bruno Mars", "video_count": 1_600_000},
    {"title": "Not Like Us", "artist": "Kendrick Lamar", "video_count": 1_400_000},
    {"title": "Good Luck, Babe!", "artist": "Chappell Roan", "video_count": 1_300_000},
    {"title": "Taste", "artist": "Sabrina Carpenter", "video_count": 1_100_000},
    {"title": "Levii's Jeans", "artist": "Beyoncé", "video_count": 900_000},
    {"title": "Please Please Please", "artist": "Sabrina Carpenter", "video_count": 850_000},
    {"title": "Beautiful Things", "artist": "Benson Boone", "video_count": 800_000},
]


# ── Public API ────────────────────────────────────────────────────────────────

def fetch_trending(region: str = "us", limit: int = 20) -> dict:
    """Fetch TikTok trending videos, hashtags, and sounds."""
    region_code = REGIONS.get(region.lower(), "US")

    videos = _fetch_trending_videos(region_code, limit)
    sounds = _fetch_trending_sounds(region_code, 20)
    hashtags = _scrape_trending_hashtags_from_discover()

    live_data = bool(videos or hashtags or sounds)

    if not hashtags:
        hashtags = _FALLBACK_HASHTAGS
    if not sounds:
        sounds = _FALLBACK_SOUNDS

    # Aggregate hashtags from videos
    video_tags: dict[str, int] = {}
    for v in videos:
        for tag in v.get("hashtags", []):
            video_tags[tag.lower()] = video_tags.get(tag.lower(), 0) + 1

    top_from_videos = sorted(video_tags, key=lambda t: video_tags[t], reverse=True)[:20]

    return {
        "region": region.lower(),
        "source": "tiktok",
        "live_data": live_data,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "video_count": len(videos),
        "videos": videos,
        "top_hashtags": [h["name"] for h in hashtags[:30]],
        "hashtag_details": hashtags[:30],
        "trending_sounds": sounds[:20],
        "top_hashtags_from_videos": top_from_videos,
    }


def fetch_hashtag(hashtag: str) -> dict:
    """Look up stats and info for a specific TikTok hashtag."""
    info = _fetch_challenge_info(hashtag)
    if not info:
        # Return minimal data if API is blocked
        name = hashtag.lstrip("#")
        info = {
            "name": name,
            "description": f"TikTok challenge/hashtag: #{name}",
            "video_count": 0,
            "view_count": 0,
        }
    info["url"] = f"https://www.tiktok.com/tag/{hashtag.lstrip('#')}"
    info["source"] = "tiktok"
    info["fetched_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return info


def fetch_trending_sounds(region: str = "us", limit: int = 20) -> dict:
    """Fetch trending sounds/music on TikTok."""
    region_code = REGIONS.get(region.lower(), "US")
    sounds = _fetch_trending_sounds(region_code, limit)
    live_data = bool(sounds)
    if not sounds:
        sounds = _FALLBACK_SOUNDS

    return {
        "region": region.lower(),
        "source": "tiktok",
        "live_data": live_data,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sound_count": len(sounds),
        "sounds": sounds[:limit],
    }


def available_regions() -> list[str]:
    return list(REGIONS.keys())
