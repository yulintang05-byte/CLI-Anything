"""YouTube viral trend scraper using YouTube Data API v3."""

import re
import os
from typing import Optional
import requests


YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

# YouTube category IDs
CATEGORY_MUSIC = "10"
CATEGORY_ENTERTAINMENT = "24"
CATEGORY_GAMING = "20"
CATEGORY_HOWTO = "26"
CATEGORY_NEWS = "25"
CATEGORY_SPORTS = "17"
CATEGORY_SCIENCE = "28"


def _get_api_key() -> str:
    key = os.environ.get("YOUTUBE_API_KEY", "")
    if not key:
        raise RuntimeError(
            "YOUTUBE_API_KEY environment variable not set. "
            "Get a free key at https://console.cloud.google.com/apis/library/youtube.googleapis.com"
        )
    return key


def _yt_get(endpoint: str, params: dict) -> dict:
    params["key"] = _get_api_key()
    resp = requests.get(f"{YOUTUBE_API_BASE}/{endpoint}", params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def get_trending_videos(
    region_code: str = "US",
    max_results: int = 25,
    category_id: Optional[str] = None,
) -> list[dict]:
    """Return trending YouTube videos with extracted hashtags and music cues."""
    params = {
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular",
        "regionCode": region_code,
        "maxResults": min(max_results, 50),
    }
    if category_id:
        params["videoCategoryId"] = category_id

    data = _yt_get("videos", params)
    results = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        results.append(
            {
                "video_id": item["id"],
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "published_at": snippet.get("publishedAt", ""),
                "hashtags": _extract_hashtags(
                    snippet.get("title", "") + " " + snippet.get("description", "")
                ),
                "description_preview": snippet.get("description", "")[:200],
                "url": f"https://youtu.be/{item['id']}",
                "thumbnail": snippet.get("thumbnails", {})
                .get("high", {})
                .get("url", ""),
            }
        )
    return results


def get_trending_music(region_code: str = "US", max_results: int = 25) -> list[dict]:
    """Return trending YouTube Music videos."""
    videos = get_trending_videos(
        region_code=region_code,
        max_results=max_results,
        category_id=CATEGORY_MUSIC,
    )
    # Enrich with music-specific fields
    for v in videos:
        artist, track = _parse_music_title(v["title"])
        v["artist"] = artist
        v["track"] = track
    return videos


def search_trending_by_niche(
    niche: str,
    max_results: int = 20,
    order: str = "viewCount",
) -> list[dict]:
    """Search YouTube for trending content in a specific niche."""
    params = {
        "part": "snippet",
        "q": niche,
        "type": "video",
        "order": order,
        "maxResults": min(max_results, 50),
        "publishedAfter": _days_ago_iso(7),
    }
    data = _yt_get("search", params)
    video_ids = [i["id"]["videoId"] for i in data.get("items", []) if i.get("id", {}).get("videoId")]
    if not video_ids:
        return []

    detail_params = {
        "part": "snippet,statistics",
        "id": ",".join(video_ids),
    }
    detail_data = _yt_get("videos", detail_params)
    results = []
    for item in detail_data.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        results.append(
            {
                "video_id": item["id"],
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "published_at": snippet.get("publishedAt", ""),
                "hashtags": _extract_hashtags(
                    snippet.get("title", "") + " " + snippet.get("description", "")
                ),
                "url": f"https://youtu.be/{item['id']}",
            }
        )
    return sorted(results, key=lambda x: x["views"], reverse=True)


def get_trending_hashtags(region_code: str = "US", max_results: int = 50) -> list[dict]:
    """Extract and rank trending hashtags from YouTube trending feed."""
    videos = get_trending_videos(region_code=region_code, max_results=max_results)
    hashtag_counts: dict[str, int] = {}
    hashtag_views: dict[str, int] = {}
    for v in videos:
        for tag in v["hashtags"]:
            tag_lower = tag.lower()
            hashtag_counts[tag_lower] = hashtag_counts.get(tag_lower, 0) + 1
            hashtag_views[tag_lower] = hashtag_views.get(tag_lower, 0) + v["views"]

    ranked = sorted(hashtag_counts.items(), key=lambda x: (x[1], hashtag_views.get(x[0], 0)), reverse=True)
    return [
        {
            "hashtag": f"#{tag}",
            "video_count": count,
            "total_views": hashtag_views.get(tag, 0),
            "avg_views": hashtag_views.get(tag, 0) // max(count, 1),
        }
        for tag, count in ranked
    ]


def analyze_hashtag(hashtag: str, max_results: int = 20) -> dict:
    """Return performance data for a specific hashtag."""
    clean = hashtag.lstrip("#")
    videos = search_trending_by_niche(f"#{clean}", max_results=max_results)
    if not videos:
        return {"hashtag": hashtag, "video_count": 0, "avg_views": 0, "total_views": 0, "top_videos": []}

    total_views = sum(v["views"] for v in videos)
    return {
        "hashtag": f"#{clean}",
        "video_count": len(videos),
        "total_views": total_views,
        "avg_views": total_views // len(videos),
        "top_videos": videos[:5],
    }


# ── helpers ──────────────────────────────────────────────────────────────────

def _extract_hashtags(text: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"#(\w+)", text)))


def _parse_music_title(title: str) -> tuple[str, str]:
    for sep in (" - ", " – ", " | ", " by "):
        if sep in title:
            parts = title.split(sep, 1)
            return parts[0].strip(), parts[1].strip()
    return "", title.strip()


def _days_ago_iso(days: int) -> str:
    from datetime import datetime, timedelta, timezone
    dt = datetime.now(timezone.utc) - timedelta(days=days)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
