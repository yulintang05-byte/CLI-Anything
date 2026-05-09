"""YouTube Data API v3 backend for trend intelligence.

Set YOUTUBE_API_KEY environment variable to enable full access.
Without a key, returns mock/cached data for agent testing.

Get a free API key at: https://console.cloud.google.com/
Enable: YouTube Data API v3 (free tier: 10,000 units/day)
"""

import os
import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from typing import Any

_YT_BASE = "https://www.googleapis.com/youtube/v3"

# Region-aware video category IDs
_CATEGORY_NAMES = {
    "1": "Film & Animation", "2": "Autos & Vehicles", "10": "Music",
    "15": "Pets & Animals", "17": "Sports", "19": "Travel & Events",
    "20": "Gaming", "22": "People & Blogs", "23": "Comedy",
    "24": "Entertainment", "25": "News & Politics", "26": "Howto & Style",
    "27": "Education", "28": "Science & Technology", "29": "Nonprofits",
}

# Curated fallback trends used when no API key is configured
_FALLBACK_TRENDS = {
    "trending_topics": [
        "AI tools tutorial", "Day in my life", "Morning routine", "Budget tips 2025",
        "Side hustle ideas", "Outfit of the day", "Cooking hack", "Travel vlog",
        "Gym motivation", "Productivity setup",
    ],
    "trending_hashtags": [
        "#fyp", "#viral", "#trending", "#foryou", "#explore",
        "#tutorial", "#motivation", "#aesthetic", "#vlog", "#satisfying",
    ],
    "trending_categories": ["How-to & Style", "Entertainment", "People & Blogs", "Music"],
    "note": "Install YOUTUBE_API_KEY env var for live data",
}


def _api_get(endpoint: str, params: dict) -> dict:
    api_key = os.environ.get("YOUTUBE_API_KEY", "")
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY not set")
    params["key"] = api_key
    url = f"{_YT_BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def fetch_trending_videos(region: str = "US", category_id: str = "", max_results: int = 25) -> list[dict]:
    """Fetch most popular videos on YouTube right now."""
    params: dict[str, Any] = {
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": max_results,
    }
    if category_id:
        params["videoCategoryId"] = category_id

    try:
        data = _api_get("videos", params)
        videos = []
        for item in data.get("items", []):
            snip = item["snippet"]
            stats = item.get("statistics", {})
            videos.append({
                "id": item["id"],
                "title": snip["title"],
                "channel": snip["channelTitle"],
                "category": _CATEGORY_NAMES.get(snip.get("categoryId", ""), "Unknown"),
                "tags": snip.get("tags", [])[:10],
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "published_at": snip["publishedAt"],
                "thumbnail": snip["thumbnails"].get("high", {}).get("url", ""),
                "url": f"https://youtube.com/watch?v={item['id']}",
            })
        return videos
    except ValueError:
        return [{"source": "fallback", **_FALLBACK_TRENDS}]
    except urllib.error.HTTPError as e:
        return [{"error": f"YouTube API error {e.code}: {e.reason}"}]


def search_trending_by_topic(topic: str, max_results: int = 20, order: str = "viewCount") -> list[dict]:
    """Search YouTube for trending videos on a topic."""
    params: dict[str, Any] = {
        "part": "snippet",
        "q": topic,
        "type": "video",
        "order": order,
        "maxResults": max_results,
        "publishedAfter": _days_ago_iso(7),
    }
    try:
        data = _api_get("search", params)
        results = []
        for item in data.get("items", []):
            snip = item["snippet"]
            vid_id = item["id"].get("videoId", "")
            results.append({
                "id": vid_id,
                "title": snip["title"],
                "channel": snip["channelTitle"],
                "description": snip["description"][:150],
                "published_at": snip["publishedAt"],
                "url": f"https://youtube.com/watch?v={vid_id}",
            })
        return results
    except ValueError:
        return [{"topic": topic, "note": "Set YOUTUBE_API_KEY for live search", "sample": _FALLBACK_TRENDS["trending_topics"][:5]}]
    except urllib.error.HTTPError as e:
        return [{"error": f"YouTube API error {e.code}: {e.reason}"}]


def fetch_trending_hashtags_from_videos(region: str = "US", max_videos: int = 50) -> list[dict]:
    """Extract and rank hashtags from trending YouTube videos."""
    videos = fetch_trending_videos(region=region, max_results=max_videos)
    if videos and "source" in videos[0]:
        return [{"hashtags": _FALLBACK_TRENDS["trending_hashtags"], "note": "Set YOUTUBE_API_KEY for live data"}]

    tag_counts: dict[str, int] = {}
    for v in videos:
        for tag in v.get("tags", []):
            clean = f"#{tag.lower().replace(' ', '')}"
            tag_counts[clean] = tag_counts.get(clean, 0) + 1

    ranked = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    return [{"hashtag": h, "frequency": c} for h, c in ranked[:50]]


def fetch_youtube_shorts_trends(topic: str = "", region: str = "US") -> list[dict]:
    """Search for trending YouTube Shorts content."""
    query = f"{topic} #shorts" if topic else "#shorts viral"
    params: dict[str, Any] = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "videoDuration": "short",
        "order": "viewCount",
        "maxResults": 20,
        "publishedAfter": _days_ago_iso(7),
        "regionCode": region,
    }
    try:
        data = _api_get("search", params)
        results = []
        for item in data.get("items", []):
            snip = item["snippet"]
            vid_id = item["id"].get("videoId", "")
            results.append({
                "id": vid_id,
                "title": snip["title"],
                "channel": snip["channelTitle"],
                "url": f"https://youtube.com/shorts/{vid_id}",
                "thumbnail": snip["thumbnails"].get("high", {}).get("url", ""),
            })
        return results
    except ValueError:
        return [{"note": "Set YOUTUBE_API_KEY for live Shorts data"}]
    except urllib.error.HTTPError as e:
        return [{"error": f"YouTube API error {e.code}: {e.reason}"}]


def get_video_categories(region: str = "US") -> list[dict]:
    """List available YouTube video categories for a region."""
    try:
        data = _api_get("videoCategories", {"part": "snippet", "regionCode": region})
        return [
            {"id": item["id"], "name": item["snippet"]["title"]}
            for item in data.get("items", [])
            if item["snippet"].get("assignable", False)
        ]
    except ValueError:
        return [{"id": k, "name": v} for k, v in _CATEGORY_NAMES.items()]
    except urllib.error.HTTPError as e:
        return [{"error": f"YouTube API error {e.code}: {e.reason}"}]


def _days_ago_iso(days: int) -> str:
    from datetime import timezone, timedelta
    dt = datetime.now(timezone.utc) - timedelta(days=days)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
