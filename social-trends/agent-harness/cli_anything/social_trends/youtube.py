"""YouTube Data API v3 client for trend research.

Requires:
    pip install google-api-python-client

Set YOUTUBE_API_KEY environment variable (get free key at console.cloud.google.com).
Daily quota: 10,000 units free. Trending videos = 1 unit per call.
"""

from __future__ import annotations

import os
import re
import time
from typing import Any


# ── Category map (YouTube video category IDs) ─────────────────────────

CATEGORY_MAP: dict[str, str] = {
    "all": "0",
    "film": "1",
    "music": "10",
    "pets": "15",
    "sports": "17",
    "gaming": "20",
    "comedy": "23",
    "entertainment": "24",
    "news": "25",
    "howto": "26",
    "science": "28",
    "fashion": "fashion",  # resolved via search
    "fitness": "fitness",
}

# Region codes (ISO 3166-1 alpha-2)
REGIONS = ["US", "GB", "CA", "AU", "IN", "BR", "DE", "FR", "JP", "KR", "MX", "NG"]


def _get_api_key() -> str:
    key = os.environ.get("YOUTUBE_API_KEY", "")
    if not key:
        raise EnvironmentError(
            "YOUTUBE_API_KEY not set. Get a free key at: "
            "https://console.cloud.google.com/apis/library/youtube.googleapis.com"
        )
    return key


def _build_service():
    """Build the YouTube API service client."""
    try:
        from googleapiclient.discovery import build
    except ImportError:
        raise ImportError(
            "google-api-python-client not installed. Run: pip install google-api-python-client"
        )
    return build("youtube", "v3", developerKey=_get_api_key())


def _extract_hashtags(text: str) -> list[str]:
    """Extract #hashtags from a string."""
    return [t.lower() for t in re.findall(r"#(\w+)", text or "")]


def _score_video(item: dict[str, Any]) -> float:
    """Score a video by engagement signals."""
    stats = item.get("statistics", {})
    views = int(stats.get("viewCount", 0))
    likes = int(stats.get("likeCount", 0))
    comments = int(stats.get("commentCount", 0))
    # Engagement rate proxy: (likes + comments*2) / views * 1000
    if views == 0:
        return 0.0
    engagement = (likes + comments * 2) / views * 1000
    # Scale by log views so mega-viral gets higher absolute score
    import math
    return round(engagement * math.log10(max(views, 1)), 2)


def fetch_trending_videos(
    region: str = "US",
    category: str = "all",
    max_results: int = 50,
) -> list[dict[str, Any]]:
    """Fetch trending videos from YouTube for a region/category.

    Args:
        region: ISO 3166-1 alpha-2 region code (e.g. "US", "GB").
        category: Category name from CATEGORY_MAP or raw category ID.
        max_results: Number of videos to fetch (max 50 per API call).

    Returns:
        List of trend dicts with keys: id, title, channel, views, likes,
        comments, hashtags, thumbnail, url, score, published_at.
    """
    service = _build_service()
    cat_id = CATEGORY_MAP.get(category.lower(), category)

    kwargs: dict[str, Any] = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region.upper(),
        "maxResults": min(max_results, 50),
    }
    if cat_id.isdigit() and cat_id != "0":
        kwargs["videoCategoryId"] = cat_id

    response = service.videos().list(**kwargs).execute()
    items = response.get("items", [])

    results = []
    for item in items:
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        vid_id = item.get("id", "")
        title = snippet.get("title", "")
        description = snippet.get("description", "")
        hashtags = list(set(
            _extract_hashtags(title) + _extract_hashtags(description)
        ))[:10]

        results.append({
            "id": vid_id,
            "title": title,
            "channel": snippet.get("channelTitle", ""),
            "published_at": snippet.get("publishedAt", ""),
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "hashtags": hashtags,
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "url": f"https://www.youtube.com/watch?v={vid_id}",
            "score": _score_video(item),
            "category": category,
            "region": region,
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)


def fetch_trending_music(region: str = "US", max_results: int = 25) -> list[dict[str, Any]]:
    """Fetch trending music videos from YouTube Music category.

    Returns tracks with title, artist, views, hashtags, and YouTube URL.
    """
    return fetch_trending_videos(region=region, category="music", max_results=max_results)


def search_trending_topic(
    query: str,
    region: str = "US",
    max_results: int = 20,
    order: str = "viewCount",
) -> list[dict[str, Any]]:
    """Search YouTube for videos in a niche/topic, ordered by view count.

    Args:
        query: Search query (niche, topic, or keyword).
        region: Region code.
        max_results: Number of results (max 50).
        order: "viewCount", "relevance", "date", or "rating".

    Returns:
        List of video dicts matching the search.
    """
    service = _build_service()

    search_response = service.search().list(
        part="snippet",
        q=query,
        type="video",
        regionCode=region.upper(),
        maxResults=min(max_results, 50),
        order=order,
        publishedAfter=_iso_days_ago(7),  # last 7 days for freshness
    ).execute()

    video_ids = [
        item["id"]["videoId"]
        for item in search_response.get("items", [])
        if item["id"].get("videoId")
    ]

    if not video_ids:
        return []

    # Fetch statistics for the found videos
    stats_response = _build_service().videos().list(
        part="snippet,statistics",
        id=",".join(video_ids),
    ).execute()

    results = []
    for item in stats_response.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        vid_id = item.get("id", "")
        title = snippet.get("title", "")
        description = snippet.get("description", "")
        hashtags = list(set(
            _extract_hashtags(title) + _extract_hashtags(description)
        ))[:10]

        results.append({
            "id": vid_id,
            "title": title,
            "channel": snippet.get("channelTitle", ""),
            "published_at": snippet.get("publishedAt", ""),
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "hashtags": hashtags,
            "url": f"https://www.youtube.com/watch?v={vid_id}",
            "score": _score_video(item),
            "query": query,
            "region": region,
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)


def extract_all_hashtags(videos: list[dict[str, Any]], top_n: int = 30) -> list[dict[str, Any]]:
    """Aggregate and rank hashtags across a list of video trend dicts.

    Returns dicts with: tag, frequency, avg_views, score.
    """
    from collections import defaultdict

    tag_data: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"count": 0, "total_views": 0, "total_likes": 0}
    )

    for v in videos:
        views = v.get("views", 0)
        likes = v.get("likes", 0)
        for tag in v.get("hashtags", []):
            tag_data[tag]["count"] += 1
            tag_data[tag]["total_views"] += views
            tag_data[tag]["total_likes"] += likes

    results = []
    for tag, data in tag_data.items():
        count = data["count"]
        avg_views = data["total_views"] // count if count else 0
        avg_likes = data["total_likes"] // count if count else 0
        import math
        score = round(count * math.log10(max(avg_views, 10)), 2)
        results.append({
            "tag": tag,
            "frequency": count,
            "avg_views": avg_views,
            "avg_likes": avg_likes,
            "score": score,
            "platform": "youtube",
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)[:top_n]


def _iso_days_ago(days: int) -> str:
    """Return ISO 8601 timestamp for N days ago."""
    import datetime
    dt = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
