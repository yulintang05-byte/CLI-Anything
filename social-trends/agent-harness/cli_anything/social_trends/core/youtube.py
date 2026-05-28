"""YouTube trending scraper.

Two modes:
1. YouTube Data API v3 (requires API key) — most reliable, structured data
2. yt-dlp fallback (no API key needed) — scrapes trending feed directly

Both return the same normalized VideoResult format so callers are agnostic.
"""

import json
import subprocess
import sys
from typing import Any

from cli_anything.social_trends.utils.social_backend import (
    load_config, youtube_api_get, cache_get, cache_set,
)


def _normalize_api_video(item: dict) -> dict:
    """Convert a YouTube API video resource to our standard format."""
    snip = item.get("snippet", {})
    stats = item.get("statistics", {})
    return {
        "id": item.get("id", ""),
        "title": snip.get("title", ""),
        "channel": snip.get("channelTitle", ""),
        "published": snip.get("publishedAt", ""),
        "description": snip.get("description", "")[:200],
        "thumbnail": (snip.get("thumbnails", {}).get("high", {}) or {}).get("url", ""),
        "tags": snip.get("tags", []),
        "category_id": snip.get("categoryId", ""),
        "views": int(stats.get("viewCount", 0)),
        "likes": int(stats.get("likeCount", 0)),
        "comments": int(stats.get("commentCount", 0)),
        "engagement_rate": _engagement_rate(stats),
        "url": f"https://www.youtube.com/watch?v={item.get('id', '')}",
        "source": "youtube_api",
    }


def _engagement_rate(stats: dict) -> float:
    """Compute engagement rate = (likes + comments) / views."""
    views = int(stats.get("viewCount", 0))
    if views == 0:
        return 0.0
    likes = int(stats.get("likeCount", 0))
    comments = int(stats.get("commentCount", 0))
    return round((likes + comments) / views * 100, 4)


def _normalize_ytdlp_video(entry: dict) -> dict:
    """Convert a yt-dlp extracted video dict to our standard format."""
    views = entry.get("view_count") or 0
    likes = entry.get("like_count") or 0
    comments = entry.get("comment_count") or 0
    er = round((likes + comments) / views * 100, 4) if views > 0 else 0.0
    return {
        "id": entry.get("id", ""),
        "title": entry.get("title", ""),
        "channel": entry.get("uploader", entry.get("channel", "")),
        "published": entry.get("upload_date", ""),
        "description": (entry.get("description") or "")[:200],
        "thumbnail": entry.get("thumbnail", ""),
        "tags": entry.get("tags") or [],
        "category_id": "",
        "views": views,
        "likes": likes,
        "comments": comments,
        "engagement_rate": er,
        "url": entry.get("webpage_url", f"https://www.youtube.com/watch?v={entry.get('id', '')}"),
        "source": "ytdlp",
    }


def get_trending_api(region: str = "US", category: str = "0",
                     max_results: int = 20) -> list[dict]:
    """Fetch trending videos via YouTube Data API v3.

    Args:
        region: ISO 3166-1 country code (e.g., 'US', 'GB').
        category: YouTube category ID (0=all, 10=music, 15=pets, 17=sports,
                  20=gaming, 22=people, 23=comedy, 24=entertainment,
                  25=news, 26=how-to, 28=science).
        max_results: Number of videos to return (max 50).

    Returns:
        List of normalized video dicts.
    """
    cache_key = f"yt_trending_{region}_{category}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": min(max_results, 50),
    }
    if category != "0":
        params["videoCategoryId"] = category

    data = youtube_api_get("videos", params)
    videos = [_normalize_api_video(item) for item in data.get("items", [])]
    cache_set(cache_key, videos)
    return videos


def get_trending_ytdlp(region: str = "US", max_results: int = 20) -> list[dict]:
    """Fetch trending videos via yt-dlp (no API key required).

    Uses yt-dlp to extract the YouTube trending feed for the given region.

    Args:
        region: ISO 3166-1 country code.
        max_results: Number of videos to return.

    Returns:
        List of normalized video dicts.
    """
    cache_key = f"yt_trending_ytdlp_{region}"
    cached = cache_get(cache_key)
    if cached:
        return cached[:max_results]

    # yt-dlp URL for trending by region
    url = f"https://www.youtube.com/feed/trending?gl={region}&hl=en"

    try:
        cmd = [
            sys.executable, "-m", "yt_dlp",
            "--dump-json",
            "--flat-playlist",
            "--playlist-end", str(min(max_results, 50)),
            "--no-warnings",
            "--quiet",
            url,
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            raise RuntimeError(f"yt-dlp failed: {result.stderr[:200]}")

        videos = []
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                videos.append(_normalize_ytdlp_video(entry))
            except json.JSONDecodeError:
                continue

        cache_set(cache_key, videos)
        return videos[:max_results]

    except FileNotFoundError:
        raise RuntimeError(
            "yt-dlp not found. Install with: pip install yt-dlp"
        )


def get_trending(region: str = "US", category: str = "0",
                 max_results: int = 20) -> list[dict]:
    """Get YouTube trending videos, using API if configured, else yt-dlp.

    Args:
        region: ISO 3166-1 country code.
        category: YouTube category ID (API mode only).
        max_results: Number of videos to return.

    Returns:
        List of normalized video dicts.
    """
    config = load_config()
    if config.get("youtube_api_key"):
        return get_trending_api(region, category, max_results)
    return get_trending_ytdlp(region, max_results)


def extract_hashtags_from_videos(videos: list[dict]) -> list[dict]:
    """Extract and rank hashtags found in video titles, descriptions, and tags.

    Args:
        videos: List of normalized video dicts.

    Returns:
        List of {hashtag, count, avg_views, videos} sorted by count desc.
    """
    import re
    from collections import defaultdict

    tag_data: dict[str, dict] = defaultdict(lambda: {"count": 0, "total_views": 0, "video_ids": []})

    for v in videos:
        text = f"{v.get('title', '')} {v.get('description', '')}"
        found = set(re.findall(r"#(\w+)", text, re.IGNORECASE))
        # Also include YouTube tags field
        for tag in v.get("tags", []):
            found.add(tag.lower().replace(" ", ""))

        views = v.get("views", 0)
        for tag in found:
            tag = tag.lower().strip()
            if len(tag) < 2:
                continue
            tag_data[tag]["count"] += 1
            tag_data[tag]["total_views"] += views
            tag_data[tag]["video_ids"].append(v.get("id", ""))

    result = []
    for tag, data in tag_data.items():
        avg_views = data["total_views"] // data["count"] if data["count"] > 0 else 0
        result.append({
            "hashtag": f"#{tag}",
            "count": data["count"],
            "avg_views": avg_views,
            "video_count": len(data["video_ids"]),
        })

    result.sort(key=lambda x: (x["count"], x["avg_views"]), reverse=True)
    return result


def get_trending_music_from_videos(videos: list[dict]) -> list[dict]:
    """Extract music/audio signals from trending video metadata.

    Looks for music-related keywords and artist mentions in titles/tags.

    Args:
        videos: List of normalized video dicts.

    Returns:
        List of {title, artist, count, avg_views} sorted by count desc.
    """
    import re
    from collections import defaultdict

    music_signals: dict[str, dict] = defaultdict(lambda: {"count": 0, "total_views": 0})

    # Patterns to extract music mentions
    patterns = [
        r'"([^"]+)" by ([A-Z][a-zA-Z\s]+)',
        r'- ([A-Z][a-zA-Z\s]+) \(Official',
        r'([A-Z][a-zA-Z\s]+) - Official (Music|Audio|Video)',
    ]

    for v in videos:
        title = v.get("title", "")
        # Only look at music category videos
        if v.get("category_id") in ("10",) or any(
            kw in title.lower() for kw in ("official", "lyrics", "audio", "music video", "mv")
        ):
            key = title[:80]
            music_signals[key]["count"] += 1
            music_signals[key]["total_views"] += v.get("views", 0)
            music_signals[key]["channel"] = v.get("channel", "")
            music_signals[key]["url"] = v.get("url", "")

    result = []
    for title, data in music_signals.items():
        avg_views = data["total_views"] // max(data["count"], 1)
        result.append({
            "title": title,
            "channel": data.get("channel", ""),
            "url": data.get("url", ""),
            "count": data["count"],
            "avg_views": avg_views,
        })

    result.sort(key=lambda x: x["avg_views"], reverse=True)
    return result[:20]


YOUTUBE_CATEGORIES = {
    "0": "All",
    "10": "Music",
    "15": "Pets & Animals",
    "17": "Sports",
    "20": "Gaming",
    "22": "People & Blogs",
    "23": "Comedy",
    "24": "Entertainment",
    "25": "News & Politics",
    "26": "How-to & Style",
    "28": "Science & Technology",
}
