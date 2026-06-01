#!/usr/bin/env python3
"""YouTube trending scraper — uses YouTube Data API v3."""

import os
import re
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from collections import Counter
from typing import Optional

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


def _get_api_key() -> str:
    key = os.environ.get("YOUTUBE_API_KEY", "")
    if not key:
        raise EnvironmentError(
            "YOUTUBE_API_KEY not set. Get one at https://console.cloud.google.com/ "
            "(enable YouTube Data API v3, then create an API key)."
        )
    return key


def _api_get(endpoint: str, params: dict) -> dict:
    params["key"] = _get_api_key()
    url = f"{YOUTUBE_API_BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read().decode())


def get_trending_videos(
    region_code: str = "US",
    category_id: str = "0",
    max_results: int = 25,
) -> list[dict]:
    """Fetch trending YouTube videos for a region."""
    data = _api_get(
        "videos",
        {
            "part": "snippet,statistics,contentDetails",
            "chart": "mostPopular",
            "regionCode": region_code,
            "videoCategoryId": category_id,
            "maxResults": min(max_results, 50),
        },
    )
    results = []
    for item in data.get("items", []):
        snip = item["snippet"]
        stats = item.get("statistics", {})
        results.append(
            {
                "video_id": item["id"],
                "title": snip.get("title", ""),
                "channel": snip.get("channelTitle", ""),
                "published_at": snip.get("publishedAt", ""),
                "description": snip.get("description", "")[:300],
                "tags": snip.get("tags", []),
                "thumbnail": snip.get("thumbnails", {})
                .get("high", {})
                .get("url", ""),
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
                "url": f"https://www.youtube.com/watch?v={item['id']}",
            }
        )
    return results


def extract_trending_hashtags(videos: list[dict], top_n: int = 30) -> list[dict]:
    """Extract + rank hashtags from a set of trending videos."""
    counter: Counter = Counter()
    for v in videos:
        # Tags from metadata
        for tag in v.get("tags", []):
            clean = tag.lower().strip()
            if clean:
                counter[clean] += v.get("view_count", 1)
        # Hashtags embedded in title/description
        text = f"{v.get('title','')} {v.get('description','')}"
        for ht in re.findall(r"#(\w+)", text):
            counter[ht.lower()] += v.get("view_count", 1)
    return [
        {"hashtag": f"#{tag}", "score": score, "rank": i + 1}
        for i, (tag, score) in enumerate(counter.most_common(top_n))
    ]


def get_trending_music_videos(region_code: str = "US", max_results: int = 15) -> list[dict]:
    """Fetch trending music videos (category 10 = Music)."""
    return get_trending_videos(region_code=region_code, category_id="10", max_results=max_results)


def search_trending_sounds(query: str, max_results: int = 10) -> list[dict]:
    """Search YouTube for trending sounds/music by query."""
    data = _api_get(
        "search",
        {
            "part": "snippet",
            "q": query,
            "type": "video",
            "videoCategoryId": "10",
            "order": "viewCount",
            "maxResults": min(max_results, 25),
            "publishedAfter": datetime.now(timezone.utc)
            .replace(day=1)
            .isoformat()
            .replace("+00:00", "Z"),
        },
    )
    results = []
    for item in data.get("items", []):
        snip = item["snippet"]
        vid_id = item["id"].get("videoId", "")
        results.append(
            {
                "video_id": vid_id,
                "title": snip.get("title", ""),
                "channel": snip.get("channelTitle", ""),
                "published_at": snip.get("publishedAt", ""),
                "url": f"https://www.youtube.com/watch?v={vid_id}",
            }
        )
    return results


def get_video_categories(region_code: str = "US") -> list[dict]:
    """List available YouTube video categories."""
    data = _api_get(
        "videoCategories",
        {"part": "snippet", "regionCode": region_code},
    )
    return [
        {"id": item["id"], "name": item["snippet"]["title"]}
        for item in data.get("items", [])
        if item["snippet"].get("assignable", False)
    ]
