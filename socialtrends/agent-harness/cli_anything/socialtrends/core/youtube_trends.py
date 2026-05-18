"""YouTube trending content fetcher using the YouTube Data API v3.

Requires a YouTube Data API v3 key configured via:
    socialtrends auth setup --youtube-key <KEY>

Free tier: 10,000 units/day — trending fetch costs ~1 unit per video.
"""

import re
import requests
from collections import Counter

from cli_anything.socialtrends.utils import cache, config

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

VIDEO_CATEGORIES = {
    "0": "All",
    "1": "Film & Animation",
    "2": "Autos & Vehicles",
    "10": "Music",
    "15": "Pets & Animals",
    "17": "Sports",
    "19": "Travel & Events",
    "20": "Gaming",
    "22": "People & Blogs",
    "23": "Comedy",
    "24": "Entertainment",
    "25": "News & Politics",
    "26": "How-to & Style",
    "27": "Education",
    "28": "Science & Technology",
    "29": "Nonprofits & Activism",
}


def _api_key() -> str:
    key = config.get("youtube_api_key")
    if not key:
        raise RuntimeError(
            "YouTube API key not configured.\n"
            "Run: socialtrends auth setup --youtube-key YOUR_KEY\n"
            "Get a free key at: https://console.cloud.google.com/ → YouTube Data API v3"
        )
    return key


def fetch_trending(
    region: str = "US",
    category_id: str = "0",
    max_results: int = 50,
    use_cache: bool = True,
) -> list[dict]:
    """Fetch trending videos from YouTube Data API v3.

    Args:
        region: ISO 3166-1 alpha-2 country code (US, GB, IN, etc.)
        category_id: YouTube video category ID (0 = all categories)
        max_results: Number of videos to retrieve (max 50 per page)
        use_cache: Use cached results if available (6h TTL)

    Returns:
        List of video dicts with id, title, channel, tags, stats, hashtags
    """
    cache_key = f"yt_trending_{region}_{category_id}_{max_results}"
    if use_cache:
        cached = cache.get_cached(cache_key)
        if cached:
            return cached

    api_key = _api_key()
    url = f"{YOUTUBE_API_BASE}/videos"
    params = {
        "part": "snippet,statistics,topicDetails",
        "chart": "mostPopular",
        "regionCode": region,
        "videoCategoryId": category_id,
        "maxResults": min(max_results, 50),
        "key": api_key,
    }

    resp = requests.get(url, params=params, timeout=15)
    if resp.status_code == 400:
        raise RuntimeError(f"YouTube API error: {resp.json().get('error', {}).get('message', 'Bad request')}")
    if resp.status_code == 403:
        raise RuntimeError("YouTube API quota exceeded or invalid key.")
    resp.raise_for_status()

    raw = resp.json()
    videos = []
    for item in raw.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        desc = snippet.get("description", "")
        tags = snippet.get("tags", [])
        hashtags = _extract_hashtags(desc) + [f"#{t.replace(' ', '')}" for t in tags if t]

        videos.append({
            "id": item["id"],
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "category_id": snippet.get("categoryId", ""),
            "published_at": snippet.get("publishedAt", ""),
            "description": desc[:500],
            "tags": tags[:20],
            "hashtags": list(dict.fromkeys(hashtags))[:30],
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
            "url": f"https://youtu.be/{item['id']}",
        })

    if use_cache:
        cache.set_cached(cache_key, videos, ttl_hours=6)

    return videos


def extract_trending_hashtags(
    videos: list[dict],
    min_count: int = 2,
    top_n: int = 50,
) -> list[dict]:
    """Aggregate hashtags across trending videos ranked by frequency.

    Args:
        videos: List returned by fetch_trending()
        min_count: Minimum appearances to include
        top_n: Maximum hashtags to return

    Returns:
        List of {hashtag, count, percent} dicts sorted by count desc
    """
    counter: Counter = Counter()
    for v in videos:
        for tag in v.get("hashtags", []):
            counter[tag.lower()] += 1

    total = len(videos) or 1
    results = [
        {
            "hashtag": tag,
            "count": cnt,
            "percent": round(cnt / total * 100, 1),
        }
        for tag, cnt in counter.most_common(top_n)
        if cnt >= min_count
    ]
    return results


def get_trending_topics(region: str = "US") -> dict:
    """High-level wrapper: trending topics across all major categories.

    Returns:
        Dict with top_videos, top_hashtags, top_channels, categories_breakdown
    """
    videos = fetch_trending(region=region, max_results=50)
    hashtags = extract_trending_hashtags(videos)

    channels: Counter = Counter()
    cats: Counter = Counter()
    for v in videos:
        channels[v["channel"]] += v["views"]
        cats[VIDEO_CATEGORIES.get(v["category_id"], "Unknown")] += 1

    return {
        "region": region,
        "video_count": len(videos),
        "top_videos": videos[:10],
        "top_hashtags": hashtags[:20],
        "top_channels": [{"channel": c, "total_views": v} for c, v in channels.most_common(10)],
        "categories_breakdown": dict(cats.most_common()),
    }


def list_categories() -> list[dict]:
    """Return all YouTube video categories."""
    return [{"id": k, "name": v} for k, v in VIDEO_CATEGORIES.items()]


def _extract_hashtags(text: str) -> list[str]:
    return re.findall(r"#\w+", text)
