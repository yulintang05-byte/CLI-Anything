"""TikTok trending scraper — uses public Creative Center API endpoints."""

import json
import time
import re
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional


_CC_BASE = "https://ads.tiktok.com/creative_radar_api/v1"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://ads.tiktok.com/business/creativecenter/",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

_DISCOVER_URL = "https://www.tiktok.com/api/explore/item_list/"
_CC_HASHTAG_URL = f"{_CC_BASE}/hashtag/list"
_CC_SOUND_URL = f"{_CC_BASE}/sound/list"
_CC_CREATOR_URL = f"{_CC_BASE}/creator/list"
_CC_VIDEO_URL = f"{_CC_BASE}/trending/insight/video"


def _get(url: str, params: Optional[dict] = None, timeout: int = 12) -> Optional[dict]:
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw)
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError):
        return None


def get_trending_hashtags(
    region: str = "US", period: int = 7, limit: int = 30
) -> list[dict]:
    """
    Fetch trending hashtags from TikTok Creative Center.
    period: 7=last 7 days, 30=last 30 days, 120=last 120 days
    """
    params = {
        "period": period,
        "country_code": region,
        "page": 1,
        "limit": limit,
        "sort_by": "popular",
    }
    data = _get(_CC_HASHTAG_URL, params)
    if data and data.get("code") == 0:
        items = data.get("data", {}).get("list", [])
        return [
            {
                "hashtag": f"#{item.get('hashtag_name', '')}",
                "rank": item.get("rank", idx + 1),
                "post_count": item.get("publish_cnt", 0),
                "video_views": item.get("video_views", 0),
                "trend": item.get("trend", ""),
                "country": region,
            }
            for idx, item in enumerate(items)
        ]

    # Fallback: scrape the Creative Center page
    return _scrape_cc_hashtags_html(region, limit)


def _scrape_cc_hashtags_html(region: str = "US", limit: int = 30) -> list[dict]:
    """Fallback HTML scrape of TikTok Creative Center trending hashtags."""
    url = (
        "https://ads.tiktok.com/business/creativecenter/trends/hashtag/pc/en"
        f"?period=7&region={region}"
    )
    req = urllib.request.Request(url, headers=_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception:
        return []

    # Extract hashtag names from the page
    tags = re.findall(r'"hashtag_name"\s*:\s*"([^"]+)"', html)
    seen: set[str] = set()
    results = []
    for i, tag in enumerate(tags[:limit]):
        if tag not in seen:
            seen.add(tag)
            results.append(
                {
                    "hashtag": f"#{tag}",
                    "rank": i + 1,
                    "post_count": None,
                    "video_views": None,
                    "trend": "",
                    "country": region,
                }
            )
    return results


def get_trending_sounds(
    region: str = "US", period: int = 7, limit: int = 20
) -> list[dict]:
    """Fetch trending sounds/music from TikTok Creative Center."""
    params = {
        "period": period,
        "country_code": region,
        "page": 1,
        "limit": limit,
        "sort_by": "popular",
    }
    data = _get(_CC_SOUND_URL, params)
    if data and data.get("code") == 0:
        items = data.get("data", {}).get("list", [])
        return [
            {
                "rank": item.get("rank", idx + 1),
                "title": item.get("clip_title", ""),
                "artist": item.get("author", ""),
                "duration": item.get("duration", 0),
                "post_count": item.get("publish_cnt", 0),
                "video_views": item.get("video_views", 0),
                "link": item.get("play_url", ""),
                "trend": item.get("trend", ""),
                "country": region,
            }
            for idx, item in enumerate(items)
        ]
    return []


def get_trending_creators(
    region: str = "US", period: int = 7, limit: int = 20
) -> list[dict]:
    """Fetch trending TikTok creators from Creative Center."""
    params = {
        "period": period,
        "country_code": region,
        "page": 1,
        "limit": limit,
        "sort_by": "follower_cnt",
    }
    data = _get(_CC_CREATOR_URL, params)
    if data and data.get("code") == 0:
        items = data.get("data", {}).get("list", [])
        return [
            {
                "rank": item.get("rank", idx + 1),
                "username": item.get("nick_name", ""),
                "followers": item.get("follower_cnt", 0),
                "likes": item.get("like_cnt", 0),
                "niche": item.get("category", ""),
                "country": region,
            }
            for idx, item in enumerate(items)
        ]
    return []


def get_trending_videos(region: str = "US", period: int = 7, limit: int = 20) -> list[dict]:
    """Fetch trending TikTok videos from Creative Center."""
    params = {
        "period": period,
        "country_code": region,
        "page": 1,
        "limit": limit,
    }
    data = _get(_CC_VIDEO_URL, params)
    if data and data.get("code") == 0:
        items = data.get("data", {}).get("list", [])
        return [
            {
                "rank": idx + 1,
                "title": item.get("video_title", item.get("desc", "")),
                "author": item.get("author_name", ""),
                "play_count": item.get("play_count", 0),
                "like_count": item.get("like_count", 0),
                "comment_count": item.get("comment_count", 0),
                "share_count": item.get("share_count", 0),
                "hashtags": item.get("hashtag_list", []),
                "sound": item.get("music_title", ""),
                "duration": item.get("duration", 0),
                "country": region,
            }
            for idx, item in enumerate(items)
        ]
    return []


def derive_niche_hashtags(hashtags: list[dict], niche: str) -> list[dict]:
    """Filter & score hashtags relevant to a specific niche."""
    niche_lower = niche.lower()
    niche_words = set(re.findall(r"\w+", niche_lower))

    scored = []
    for tag in hashtags:
        name = tag["hashtag"].lstrip("#").lower()
        # Score by overlap with niche keywords
        tag_words = set(re.findall(r"\w+", name))
        overlap = len(niche_words & tag_words)
        scored.append({**tag, "niche_score": overlap})

    # Sort: niche_score desc, then post_count desc
    scored.sort(
        key=lambda x: (x["niche_score"], x.get("post_count") or 0),
        reverse=True,
    )
    return scored
