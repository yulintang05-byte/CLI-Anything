"""YouTube Data API v3 backend — trending videos, music, and hashtag extraction."""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from typing import Optional

try:
    import requests
except ImportError:
    print("requests not found. Install with: pip3 install requests", file=sys.stderr)
    sys.exit(1)

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

CATEGORY_IDS = {
    "all": None,
    "music": "10",
    "gaming": "20",
    "entertainment": "24",
    "news": "25",
    "howto": "26",
    "sports": "17",
    "film": "1",
    "comedy": "23",
    "science": "28",
}

REGION_CODES = {
    "us": "US", "uk": "GB", "ca": "CA", "au": "AU",
    "de": "DE", "fr": "FR", "jp": "JP", "kr": "KR",
    "br": "BR", "in": "IN", "mx": "MX", "it": "IT",
}


def get_trending_videos(
    api_key: str,
    region: str = "US",
    category: str = "all",
    max_results: int = 50,
) -> list[dict]:
    """Fetch trending videos from YouTube Data API v3 mostPopular chart."""
    region = REGION_CODES.get(region.lower(), region.upper())
    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": min(max_results, 50),
        "key": api_key,
    }
    cat_id = CATEGORY_IDS.get(category.lower())
    if cat_id:
        params["videoCategoryId"] = cat_id

    resp = requests.get(f"{YOUTUBE_API_BASE}/videos", params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    videos = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        tags = [t for t in (snippet.get("tags") or []) if t]
        desc = snippet.get("description") or ""

        desc_hashtags = extract_hashtags_from_text(desc)
        tag_hashtags = [f"#{t.lower()}" for t in tags if t.startswith("#")]
        all_hashtags = list(dict.fromkeys(desc_hashtags + tag_hashtags))[:15]

        videos.append({
            "id": item.get("id"),
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "category_id": snippet.get("categoryId", ""),
            "published_at": snippet.get("publishedAt", ""),
            "views": int(stats.get("viewCount") or 0),
            "likes": int(stats.get("likeCount") or 0),
            "comments": int(stats.get("commentCount") or 0),
            "hashtags": all_hashtags,
            "tags": tags[:20],
            "description_preview": desc[:200],
            "thumbnail": (snippet.get("thumbnails") or {}).get("high", {}).get("url", ""),
            "url": f"https://youtube.com/watch?v={item.get('id')}",
            "platform": "youtube",
        })

    return videos


def get_trending_music(
    api_key: str,
    region: str = "US",
    max_results: int = 50,
) -> list[dict]:
    """Get trending music videos (YouTube category 10)."""
    return get_trending_videos(api_key, region=region, category="music", max_results=max_results)


def get_video_categories(api_key: str, region: str = "US") -> list[dict]:
    """Fetch available video category list for a region."""
    region = REGION_CODES.get(region.lower(), region.upper())
    params = {
        "part": "snippet",
        "regionCode": region,
        "hl": "en",
        "key": api_key,
    }
    resp = requests.get(f"{YOUTUBE_API_BASE}/videoCategories", params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return [
        {"id": item["id"], "title": item["snippet"]["title"]}
        for item in data.get("items", [])
        if item.get("snippet", {}).get("assignable", False)
    ]


def extract_hashtags_from_text(text: str) -> list[str]:
    """Extract hashtags from description or title text."""
    found = re.findall(r"#([A-Za-z0-9_]+)", text)
    return [f"#{h.lower()}" for h in found]


def aggregate_hashtags(videos: list[dict]) -> list[dict]:
    """Aggregate hashtags from video list, rank by frequency × engagement."""
    tag_data: dict[str, dict] = defaultdict(
        lambda: {"count": 0, "total_views": 0, "total_likes": 0, "videos": []}
    )

    for v in videos:
        for tag in v.get("hashtags", []):
            tag_data[tag]["count"] += 1
            tag_data[tag]["total_views"] += v.get("views", 0)
            tag_data[tag]["total_likes"] += v.get("likes", 0)
            title = v.get("title", "")
            if title and title not in tag_data[tag]["videos"]:
                tag_data[tag]["videos"].append(title)

    results = []
    for tag, d in tag_data.items():
        score = d["count"] * 10 + d["total_views"] / 1_000_000
        results.append({
            "hashtag": tag,
            "video_count": d["count"],
            "total_views": d["total_views"],
            "total_likes": d["total_likes"],
            "sample_videos": d["videos"][:3],
            "score": round(score, 2),
            "platform": "youtube",
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)


def aggregate_music_trends(videos: list[dict]) -> list[dict]:
    """Extract music/artist trends from music category videos."""
    from collections import Counter

    # Parse artist from title patterns like "Artist - Song", "Song by Artist"
    artist_views: dict[str, int] = defaultdict(int)
    artist_counts: dict[str, int] = defaultdict(int)

    for v in videos:
        title = v.get("title", "")
        channel = v.get("channel", "")
        views = v.get("views", 0)

        artist_views[channel] += views
        artist_counts[channel] += 1

    results = []
    for artist, views in sorted(artist_views.items(), key=lambda x: x[1], reverse=True)[:20]:
        results.append({
            "artist": artist,
            "video_count": artist_counts[artist],
            "total_views": views,
            "platform": "youtube",
        })
    return results
