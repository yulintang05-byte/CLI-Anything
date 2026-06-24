#!/usr/bin/env python3
"""YouTube Data API v3 — trending videos, viral hashtags, and music discovery.

Requires: YOUTUBE_API_KEY environment variable or configured via:
  cli-anything-social config set-key --platform youtube --key <YOUR_KEY>

Get a free API key at: https://console.developers.google.com/
Quota: 10,000 units/day (free tier). videos.list costs 1 unit per call.
"""

import re
import isodate
from typing import Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from cli_anything.social_trends.utils.config import get_youtube_api_key
from cli_anything.social_trends.utils.formatters import fmt_number, fmt_duration


CATEGORY_IDS = {
    "music": "10",
    "gaming": "20",
    "news": "25",
    "entertainment": "24",
    "sports": "17",
    "education": "27",
    "film": "1",
    "comedy": "23",
    "howto": "26",
    "science": "28",
    "travel": "19",
    "people": "22",
    "fashion": "None",
    "all": None,
}

VALID_REGIONS = [
    "US", "GB", "CA", "AU", "IN", "DE", "FR", "JP", "KR", "BR",
    "MX", "NG", "ZA", "AE", "ID", "PH", "TH", "VN", "EG", "AR",
]


def _build_client():
    api_key = get_youtube_api_key()
    if not api_key:
        raise RuntimeError(
            "YouTube API key not found.\n"
            "Set it with: cli-anything-social config set-key --platform youtube --key <YOUR_KEY>\n"
            "Or: export YOUTUBE_API_KEY=<YOUR_KEY>\n"
            "Get a free key at: https://console.developers.google.com/"
        )
    return build("youtube", "v3", developerKey=api_key, cache_discovery=False)


def _parse_duration(iso_duration: str) -> int:
    """Parse ISO 8601 duration to seconds."""
    try:
        return int(isodate.parse_duration(iso_duration).total_seconds())
    except Exception:
        return 0


def _extract_hashtags(text: str) -> list[str]:
    """Extract #hashtags from title/description."""
    return re.findall(r"#(\w+)", text)


def fetch_trending_videos(
    region: str = "US",
    category: str = "all",
    max_results: int = 25,
    shorts_only: bool = False,
) -> list[dict]:
    """Fetch trending YouTube videos for a given region and category.

    Returns list of video dicts with: id, title, channel, views, likes,
    comments, duration, hashtags, thumbnail, published_at, url.
    """
    client = _build_client()
    cat_id = CATEGORY_IDS.get(category.lower())

    params = {
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular",
        "regionCode": region.upper(),
        "maxResults": min(max_results, 50),
    }
    if cat_id:
        params["videoCategoryId"] = cat_id

    try:
        response = client.videos().list(**params).execute()
    except HttpError as e:
        raise RuntimeError(f"YouTube API error: {e.reason}") from e

    videos = []
    for item in response.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        content = item.get("contentDetails", {})

        duration_secs = _parse_duration(content.get("duration", "PT0S"))
        title = snippet.get("title", "")
        description = snippet.get("description", "")
        tags = snippet.get("tags", [])

        hashtags = list(set(_extract_hashtags(title) + _extract_hashtags(description)))
        hashtags.extend([t for t in tags if not t.startswith("#")])
        hashtags = list(dict.fromkeys(hashtags))[:15]

        if shorts_only and duration_secs > 60:
            continue

        videos.append({
            "id": item["id"],
            "title": title,
            "channel": snippet.get("channelTitle", ""),
            "channel_id": snippet.get("channelId", ""),
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "duration_secs": duration_secs,
            "duration": fmt_duration(duration_secs),
            "hashtags": hashtags,
            "tags": tags[:10],
            "category_id": snippet.get("categoryId", ""),
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "published_at": snippet.get("publishedAt", ""),
            "url": f"https://www.youtube.com/watch?v={item['id']}",
            "is_short": duration_secs <= 60,
        })

    return videos


def fetch_trending_music(region: str = "US", max_results: int = 20) -> list[dict]:
    """Fetch trending music videos on YouTube."""
    return fetch_trending_videos(region=region, category="music", max_results=max_results)


def extract_trending_hashtags(videos: list[dict], top_n: int = 20) -> list[dict]:
    """Aggregate and rank hashtags from a list of trending videos.

    Returns list of {hashtag, count, total_views} sorted by total_views.
    """
    counts: dict[str, dict] = {}
    for v in videos:
        for tag in v.get("hashtags", []):
            tag_lower = tag.lower()
            if tag_lower not in counts:
                counts[tag_lower] = {"hashtag": f"#{tag_lower}", "count": 0, "total_views": 0}
            counts[tag_lower]["count"] += 1
            counts[tag_lower]["total_views"] += v.get("views", 0)

    ranked = sorted(counts.values(), key=lambda x: x["total_views"], reverse=True)
    return ranked[:top_n]


def fetch_channel_stats(channel_id: str) -> dict:
    """Fetch statistics for a YouTube channel."""
    client = _build_client()
    try:
        resp = client.channels().list(
            part="snippet,statistics,brandingSettings",
            id=channel_id,
        ).execute()
    except HttpError as e:
        raise RuntimeError(f"YouTube API error: {e.reason}") from e

    items = resp.get("items", [])
    if not items:
        raise RuntimeError(f"Channel not found: {channel_id}")

    item = items[0]
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    branding = item.get("brandingSettings", {}).get("channel", {})

    return {
        "id": item["id"],
        "title": snippet.get("title", ""),
        "description": snippet.get("description", ""),
        "country": snippet.get("country", ""),
        "subscribers": int(stats.get("subscriberCount", 0)),
        "total_views": int(stats.get("viewCount", 0)),
        "video_count": int(stats.get("videoCount", 0)),
        "keywords": branding.get("keywords", ""),
        "created_at": snippet.get("publishedAt", ""),
        "url": f"https://www.youtube.com/channel/{item['id']}",
    }


def search_trending_by_keyword(keyword: str, region: str = "US", max_results: int = 15) -> list[dict]:
    """Search YouTube for trending videos matching a keyword or hashtag."""
    client = _build_client()
    try:
        search_resp = client.search().list(
            part="id,snippet",
            q=keyword,
            type="video",
            order="viewCount",
            regionCode=region.upper(),
            maxResults=min(max_results, 50),
            relevanceLanguage="en",
        ).execute()
    except HttpError as e:
        raise RuntimeError(f"YouTube API error: {e.reason}") from e

    video_ids = [item["id"]["videoId"] for item in search_resp.get("items", [])]
    if not video_ids:
        return []

    try:
        vid_resp = client.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(video_ids),
        ).execute()
    except HttpError as e:
        raise RuntimeError(f"YouTube API error: {e.reason}") from e

    results = []
    for item in vid_resp.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        content = item.get("contentDetails", {})
        duration_secs = _parse_duration(content.get("duration", "PT0S"))
        title = snippet.get("title", "")
        hashtags = _extract_hashtags(title) + _extract_hashtags(snippet.get("description", ""))

        results.append({
            "id": item["id"],
            "title": title,
            "channel": snippet.get("channelTitle", ""),
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "duration": fmt_duration(duration_secs),
            "hashtags": list(dict.fromkeys(hashtags))[:10],
            "published_at": snippet.get("publishedAt", ""),
            "url": f"https://www.youtube.com/watch?v={item['id']}",
            "is_short": duration_secs <= 60,
        })

    return sorted(results, key=lambda x: x["views"], reverse=True)


def get_trending_summary(region: str = "US") -> dict:
    """Get a complete trending summary: top videos, top hashtags, top music, top Shorts."""
    all_videos = fetch_trending_videos(region=region, max_results=50)
    music_videos = fetch_trending_videos(region=region, category="music", max_results=20)
    shorts = [v for v in all_videos if v["is_short"]]
    hashtags = extract_trending_hashtags(all_videos, top_n=25)

    return {
        "region": region,
        "top_videos": all_videos[:10],
        "top_shorts": shorts[:10],
        "trending_music": music_videos[:10],
        "trending_hashtags": hashtags[:20],
        "total_fetched": len(all_videos),
    }
