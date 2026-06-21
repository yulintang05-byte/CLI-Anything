"""YouTube Trends — fetch viral videos, hashtags, and music via YouTube Data API v3.

Requires a YouTube Data API v3 key:
    social-trends config set youtube_api_key YOUR_KEY
    or set YOUTUBE_API_KEY env var.

Free quota: 10,000 units/day. Each trends fetch ≈ 1 unit.
Get a key: https://console.developers.google.com/ → Enable "YouTube Data API v3"
"""

import os
from typing import Any, Optional
import requests

from . import config as cfg

_API_BASE = "https://www.googleapis.com/youtube/v3"

# YouTube video category IDs (most relevant for social media growth)
CATEGORY_IDS = {
    "all": None,
    "music": "10",
    "gaming": "20",
    "entertainment": "24",
    "howto": "26",
    "news": "25",
    "sports": "17",
    "comedy": "23",
    "film": "1",
    "auto": "2",
    "pets": "15",
    "travel": "19",
    "fashion": "26",
    "food": "26",
}


def _api_key() -> str:
    return cfg.require("youtube_api_key", env_var="YOUTUBE_API_KEY")


def _get(endpoint: str, params: dict) -> dict:
    params["key"] = _api_key()
    resp = requests.get(f"{_API_BASE}/{endpoint}", params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_trending_videos(
    region: str = "US",
    category: str = "all",
    limit: int = 20,
) -> list[dict]:
    """Return top trending videos with engagement metrics."""
    params: dict[str, Any] = {
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular",
        "regionCode": region.upper(),
        "maxResults": min(limit, 50),
    }
    cat_id = CATEGORY_IDS.get(category.lower())
    if cat_id:
        params["videoCategoryId"] = cat_id

    data = _get("videos", params)
    results = []
    for item in data.get("items", []):
        snip = item.get("snippet", {})
        stats = item.get("statistics", {})
        tags = snip.get("tags", [])
        # Extract hashtags from tags and description
        desc = snip.get("description", "")
        hashtags = [t for t in tags if not t.startswith("#")]
        hashtags += _extract_hashtags(desc)
        results.append({
            "id": item.get("id"),
            "title": snip.get("title"),
            "channel": snip.get("channelTitle"),
            "published": snip.get("publishedAt", "")[:10],
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "hashtags": hashtags[:10],
            "thumbnail": snip.get("thumbnails", {}).get("high", {}).get("url", ""),
            "url": f"https://www.youtube.com/watch?v={item.get('id')}",
            "category": category,
            "region": region.upper(),
        })
    return results


def get_trending_hashtags(region: str = "US", limit: int = 20) -> list[dict]:
    """Aggregate trending hashtags from the top 50 trending videos."""
    videos = get_trending_videos(region=region, limit=50)
    hashtag_counts: dict[str, int] = {}
    hashtag_views: dict[str, int] = {}
    for v in videos:
        for tag in v.get("hashtags", []):
            tag_lower = tag.lower().lstrip("#")
            if len(tag_lower) < 2:
                continue
            hashtag_counts[tag_lower] = hashtag_counts.get(tag_lower, 0) + 1
            hashtag_views[tag_lower] = hashtag_views.get(tag_lower, 0) + v.get("views", 0)
    results = [
        {
            "hashtag": f"#{tag}",
            "occurrences": count,
            "total_views": hashtag_views[tag],
            "platform": "YouTube",
            "region": region.upper(),
        }
        for tag, count in sorted(hashtag_counts.items(), key=lambda x: -x[1])
    ]
    return results[:limit]


def search_trending_hashtag(hashtag: str, region: str = "US", limit: int = 20) -> list[dict]:
    """Search videos for a specific hashtag and return engagement data."""
    params: dict[str, Any] = {
        "part": "snippet",
        "q": hashtag if hashtag.startswith("#") else f"#{hashtag}",
        "type": "video",
        "order": "viewCount",
        "regionCode": region.upper(),
        "maxResults": min(limit, 50),
    }
    data = _get("search", params)
    video_ids = [item["id"]["videoId"] for item in data.get("items", [])]
    if not video_ids:
        return []
    # Fetch stats
    stats_data = _get("videos", {
        "part": "snippet,statistics",
        "id": ",".join(video_ids),
    })
    results = []
    for item in stats_data.get("items", []):
        snip = item.get("snippet", {})
        stats = item.get("statistics", {})
        results.append({
            "id": item.get("id"),
            "title": snip.get("title"),
            "channel": snip.get("channelTitle"),
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "hashtag": hashtag,
            "url": f"https://www.youtube.com/watch?v={item.get('id')}",
        })
    return sorted(results, key=lambda x: -x["views"])


def get_trending_music(region: str = "US", limit: int = 20) -> list[dict]:
    """Fetch trending music videos with artist and track data."""
    videos = get_trending_videos(region=region, category="music", limit=limit)
    results = []
    for v in videos:
        title = v["title"]
        channel = v["channel"]
        # Parse "Artist - Song Title" patterns common in music videos
        if " - " in title:
            parts = title.split(" - ", 1)
            artist = parts[0].strip()
            track = parts[1].strip()
        else:
            artist = channel
            track = title
        results.append({
            "track": track,
            "artist": artist,
            "channel": channel,
            "views": v["views"],
            "likes": v["likes"],
            "hashtags": v["hashtags"],
            "url": v["url"],
            "platform": "YouTube",
            "region": region.upper(),
        })
    return results


def get_channel_stats(channel_id: str) -> dict:
    """Fetch stats for a YouTube channel (for account optimization)."""
    data = _get("channels", {
        "part": "snippet,statistics,brandingSettings",
        "id": channel_id,
    })
    items = data.get("items", [])
    if not items:
        return {}
    item = items[0]
    snip = item.get("snippet", {})
    stats = item.get("statistics", {})
    branding = item.get("brandingSettings", {}).get("channel", {})
    return {
        "id": channel_id,
        "name": snip.get("title"),
        "description": snip.get("description", "")[:200],
        "subscribers": int(stats.get("subscriberCount", 0)),
        "total_views": int(stats.get("viewCount", 0)),
        "video_count": int(stats.get("videoCount", 0)),
        "keywords": branding.get("keywords", ""),
        "country": snip.get("country", ""),
        "created": snip.get("publishedAt", "")[:10],
    }


def _extract_hashtags(text: str) -> list[str]:
    import re
    return re.findall(r"#(\w+)", text)
