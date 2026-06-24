"""YouTube trend intelligence — wraps YouTube Data API v3.

Covers trending videos, viral music (category 10), trending hashtags,
and per-channel optimization data. All responses are normalized to
platform-agnostic dicts for easy cross-platform comparison.
"""

from typing import Optional
from cli_anything.social_trends.utils.trends_backend import yt_get, cached


# YouTube video category IDs
CATEGORY_IDS = {
    "music": "10",
    "gaming": "20",
    "entertainment": "24",
    "howto": "26",
    "comedy": "23",
    "news": "25",
    "sports": "17",
    "travel": "19",
    "beauty": "26",
    "education": "27",
    "science": "28",
}

SUPPORTED_REGIONS = [
    "US", "GB", "CA", "AU", "IN", "BR", "JP", "KR",
    "FR", "DE", "MX", "ID", "TH", "PH", "VN",
]


def _normalize_video(item: dict) -> dict:
    """Normalize a raw YouTube API video item."""
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    content = item.get("contentDetails", {})
    return {
        "id": item.get("id", ""),
        "platform": "youtube",
        "title": snippet.get("title", ""),
        "channel": snippet.get("channelTitle", ""),
        "channel_id": snippet.get("channelId", ""),
        "published_at": snippet.get("publishedAt", ""),
        "description": snippet.get("description", "")[:300],
        "tags": snippet.get("tags", []),
        "category_id": snippet.get("categoryId", ""),
        "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
        "views": int(stats.get("viewCount", 0)),
        "likes": int(stats.get("likeCount", 0)),
        "comments": int(stats.get("commentCount", 0)),
        "duration": content.get("duration", ""),
        "url": f"https://youtube.com/watch?v={item.get('id', '')}",
    }


def get_trending_videos(
    region: str = "US",
    category: str = "all",
    max_results: int = 25,
) -> dict:
    """Fetch trending videos from YouTube.

    Args:
        region: ISO 3166-1 alpha-2 country code (e.g. 'US', 'GB').
        category: One of CATEGORY_IDS keys, or 'all' for across all categories.
        max_results: Number of results to return (max 50).

    Returns:
        dict with 'videos' list and metadata.
    """
    cache_key = f"yt_trending_{region}_{category}_{max_results}"

    def fetch():
        params = {
            "part": "snippet,statistics,contentDetails",
            "chart": "mostPopular",
            "regionCode": region,
            "maxResults": min(max_results, 50),
        }
        if category != "all" and category in CATEGORY_IDS:
            params["videoCategoryId"] = CATEGORY_IDS[category]

        data = yt_get("videos", params)
        videos = [_normalize_video(item) for item in data.get("items", [])]
        return {
            "platform": "youtube",
            "region": region,
            "category": category,
            "total": len(videos),
            "videos": videos,
        }

    return cached(cache_key, fetch)


def get_trending_music(region: str = "US", max_results: int = 25) -> dict:
    """Fetch trending music videos (YouTube category 10).

    Returns normalized video items focusing on music metadata.
    """
    return get_trending_videos(region=region, category="music", max_results=max_results)


def extract_trending_hashtags(region: str = "US", max_results: int = 50) -> dict:
    """Extract trending hashtags from trending video titles, descriptions, and tags.

    YouTube doesn't expose hashtags as a first-class concept, so we mine
    the top-50 trending videos and extract #hashtag patterns.
    """
    cache_key = f"yt_hashtags_{region}"

    def fetch():
        import re
        result = get_trending_videos(region=region, max_results=50)
        hashtag_counts: dict[str, int] = {}

        for video in result.get("videos", []):
            # Extract from title, description, and tags
            text = " ".join([
                video.get("title", ""),
                video.get("description", ""),
                " ".join(video.get("tags", [])),
            ])
            found = re.findall(r"#(\w+)", text, re.IGNORECASE)
            for tag in found:
                tag_lower = tag.lower()
                hashtag_counts[tag_lower] = hashtag_counts.get(tag_lower, 0) + 1

        sorted_tags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)
        hashtags = [
            {"tag": f"#{tag}", "count": count, "platform": "youtube"}
            for tag, count in sorted_tags[:max_results]
        ]
        return {
            "platform": "youtube",
            "region": region,
            "total": len(hashtags),
            "hashtags": hashtags,
        }

    return cached(cache_key, fetch)


def search_videos(
    query: str,
    region: str = "US",
    order: str = "relevance",
    max_results: int = 20,
    published_after: Optional[str] = None,
) -> dict:
    """Search YouTube videos for trend research.

    Args:
        query: Search query (e.g. '#viral', 'trending dance challenge').
        region: ISO region code.
        order: 'relevance' | 'viewCount' | 'date' | 'rating'.
        max_results: Number of results.
        published_after: ISO 8601 date string to filter recency.
    """
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "regionCode": region,
        "order": order,
        "maxResults": min(max_results, 50),
    }
    if published_after:
        params["publishedAfter"] = published_after

    data = yt_get("search", params)
    items = data.get("items", [])

    # Enrich with statistics via a follow-up videos request
    video_ids = [item["id"]["videoId"] for item in items if item.get("id", {}).get("videoId")]
    enriched = []
    if video_ids:
        vid_data = yt_get("videos", {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(video_ids),
        })
        enriched = [_normalize_video(v) for v in vid_data.get("items", [])]
    else:
        for item in items:
            enriched.append({
                "id": item["id"].get("videoId", ""),
                "platform": "youtube",
                "title": item["snippet"].get("title", ""),
                "channel": item["snippet"].get("channelTitle", ""),
                "published_at": item["snippet"].get("publishedAt", ""),
                "url": f"https://youtube.com/watch?v={item['id'].get('videoId', '')}",
            })

    return {
        "platform": "youtube",
        "query": query,
        "region": region,
        "order": order,
        "total": len(enriched),
        "videos": enriched,
    }


def get_channel_stats(channel_id: str) -> dict:
    """Get channel statistics for account optimization.

    Args:
        channel_id: YouTube channel ID (starts with UC...).
    """
    data = yt_get("channels", {
        "part": "snippet,statistics,brandingSettings,contentDetails",
        "id": channel_id,
    })
    items = data.get("items", [])
    if not items:
        raise RuntimeError(f"Channel not found: {channel_id}")

    ch = items[0]
    snippet = ch.get("snippet", {})
    stats = ch.get("statistics", {})
    branding = ch.get("brandingSettings", {}).get("channel", {})

    return {
        "platform": "youtube",
        "channel_id": channel_id,
        "name": snippet.get("title", ""),
        "description": snippet.get("description", "")[:500],
        "country": snippet.get("country", ""),
        "created_at": snippet.get("publishedAt", ""),
        "subscribers": int(stats.get("subscriberCount", 0)),
        "views_total": int(stats.get("viewCount", 0)),
        "video_count": int(stats.get("videoCount", 0)),
        "keywords": branding.get("keywords", ""),
        "url": f"https://youtube.com/channel/{channel_id}",
    }


def get_video_categories(region: str = "US") -> dict:
    """List all YouTube video categories for a region."""
    data = yt_get("videoCategories", {
        "part": "snippet",
        "regionCode": region,
        "hl": "en_US",
    })
    cats = [
        {"id": item["id"], "name": item["snippet"]["title"], "assignable": item["snippet"]["assignable"]}
        for item in data.get("items", [])
    ]
    return {"region": region, "categories": cats}
