"""YouTube Data API v3 backend — trending videos, hashtags, music discovery."""

import os
import json
import time
import requests
from pathlib import Path
from typing import Optional, List

CONFIG_DIR = Path.home() / ".cli-anything-youtube"
CONFIG_FILE = CONFIG_DIR / "config.json"

YT_API_BASE = "https://www.googleapis.com/youtube/v3"
YOUTUBE_API_SERVICE = "youtube"
YOUTUBE_API_VERSION = "v3"

# ── Config management ────────────────────────────────────────────

def load_config() -> dict:
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}

def save_config(data: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2))

def get_api_key() -> Optional[str]:
    cfg = load_config()
    return cfg.get("api_key") or os.environ.get("YOUTUBE_API_KEY")

# ── Trending videos ──────────────────────────────────────────────

REGION_CATEGORY_MAP = {
    "US": "0",   # All categories
    "GB": "0",
    "CA": "0",
    "AU": "0",
}

CATEGORY_NAMES = {
    "0": "All",
    "10": "Music",
    "17": "Sports",
    "20": "Gaming",
    "22": "People & Blogs",
    "23": "Comedy",
    "24": "Entertainment",
    "25": "News & Politics",
    "26": "How-to & Style",
    "28": "Science & Technology",
}

def fetch_trending_videos(region: str = "US", category_id: str = "0", limit: int = 20) -> list:
    """Fetch trending YouTube videos using Videos.list mostPopular chart."""
    key = get_api_key()
    if not key:
        return _mock_trending_videos(limit)
    try:
        resp = requests.get(
            f"{YT_API_BASE}/videos",
            params={
                "part": "snippet,statistics,contentDetails",
                "chart": "mostPopular",
                "regionCode": region,
                "videoCategoryId": category_id,
                "maxResults": min(limit, 50),
                "key": key,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        return [_normalize_video(item) for item in data.get("items", [])]
    except Exception as e:
        raise RuntimeError(f"YouTube API error: {e}")

def _normalize_video(item: dict) -> dict:
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    content = item.get("contentDetails", {})
    tags = snippet.get("tags", [])
    desc = snippet.get("description", "")
    # Extract hashtags from title and description
    import re
    hashtags_in_desc = re.findall(r"#(\w+)", desc + " " + snippet.get("title", ""))
    return {
        "id": item.get("id", ""),
        "title": snippet.get("title", ""),
        "channel": snippet.get("channelTitle", ""),
        "channel_id": snippet.get("channelId", ""),
        "description": desc[:200] + "..." if len(desc) > 200 else desc,
        "published_at": snippet.get("publishedAt", ""),
        "category_id": snippet.get("categoryId", "0"),
        "category": CATEGORY_NAMES.get(snippet.get("categoryId", "0"), "Unknown"),
        "duration": content.get("duration", ""),
        "views": int(stats.get("viewCount", 0)),
        "likes": int(stats.get("likeCount", 0)),
        "comments": int(stats.get("commentCount", 0)),
        "tags": tags[:10],
        "hashtags": list(set(hashtags_in_desc))[:10],
        "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
        "url": f"https://www.youtube.com/watch?v={item.get('id', '')}",
    }

def _mock_trending_videos(limit: int) -> list:
    samples = [
        {
            "id": "demo1",
            "title": "I Built a $10K/Month Business with AI in 30 Days",
            "channel": "TechEntrepreneur",
            "channel_id": "UC000",
            "description": "In this video I show you how I used AI tools to...",
            "published_at": "2026-06-14T18:00:00Z",
            "category_id": "28",
            "category": "Science & Technology",
            "duration": "PT12M30S",
            "views": 2800000,
            "likes": 145000,
            "comments": 8200,
            "tags": ["ai", "business", "entrepreneur", "money"],
            "hashtags": ["ai", "business", "entrepreneur"],
            "thumbnail": "",
            "url": "https://www.youtube.com/watch?v=demo1",
        },
        {
            "id": "demo2",
            "title": "This Song Broke TikTok (Official Music Video)",
            "channel": "ViralMusicTV",
            "channel_id": "UC001",
            "description": "The viral song everyone is using on TikTok...",
            "published_at": "2026-06-13T20:00:00Z",
            "category_id": "10",
            "category": "Music",
            "duration": "PT3M15S",
            "views": 18500000,
            "likes": 920000,
            "comments": 42000,
            "tags": ["music", "viral", "tiktok"],
            "hashtags": ["music", "viral"],
            "thumbnail": "",
            "url": "https://www.youtube.com/watch?v=demo2",
        },
    ]
    return (samples * ((limit // len(samples)) + 1))[:limit]

# ── Trending music/audio ─────────────────────────────────────────

def fetch_trending_music(region: str = "US", limit: int = 20) -> list:
    """Fetch trending music videos (category 10)."""
    videos = fetch_trending_videos(region=region, category_id="10", limit=limit)
    for v in videos:
        v["type"] = "music_video"
        v["usable_on_shorts"] = True
        v["usable_on_tiktok"] = True
    return videos

# ── Hashtag/search trending ──────────────────────────────────────

def fetch_hashtag_videos(hashtag: str, limit: int = 20) -> list:
    """Search YouTube for videos using a specific hashtag."""
    key = get_api_key()
    if not key:
        return _mock_hashtag_videos(hashtag, limit)
    try:
        # Search for hashtag
        search_resp = requests.get(
            f"{YT_API_BASE}/search",
            params={
                "part": "snippet",
                "q": f"#{hashtag}",
                "type": "video",
                "order": "viewCount",
                "maxResults": min(limit, 50),
                "key": key,
            },
            timeout=15,
        )
        search_resp.raise_for_status()
        items = search_resp.json().get("items", [])
        video_ids = [i["id"]["videoId"] for i in items if i.get("id", {}).get("videoId")]
        if not video_ids:
            return []
        # Batch fetch stats
        stats_resp = requests.get(
            f"{YT_API_BASE}/videos",
            params={
                "part": "snippet,statistics",
                "id": ",".join(video_ids),
                "key": key,
            },
            timeout=15,
        )
        stats_resp.raise_for_status()
        return [_normalize_video(item) for item in stats_resp.json().get("items", [])]
    except Exception as e:
        raise RuntimeError(f"YouTube API error: {e}")

def _mock_hashtag_videos(hashtag: str, limit: int) -> list:
    return [
        {
            "id": "hv1", "title": f"#{hashtag} - Best Content 2026",
            "channel": "Creator123", "channel_id": "UC002",
            "description": f"Everything about #{hashtag}...",
            "published_at": "2026-06-10T12:00:00Z",
            "category_id": "22", "category": "People & Blogs",
            "duration": "PT8M22S",
            "views": 450000, "likes": 23000, "comments": 1200,
            "tags": [hashtag, "trending", "viral"],
            "hashtags": [hashtag, "trending"],
            "thumbnail": "", "url": f"https://www.youtube.com/results?search_query=%23{hashtag}",
        }
    ][:limit]

# ── Channel analytics ────────────────────────────────────────────

def fetch_channel_info(channel_id_or_handle: str) -> dict:
    """Fetch channel statistics and metadata."""
    key = get_api_key()
    if not key:
        return {"channel": channel_id_or_handle, "note": "Configure YOUTUBE_API_KEY for real data"}
    handle = channel_id_or_handle.lstrip("@")
    try:
        # Try by handle first
        resp = requests.get(
            f"{YT_API_BASE}/channels",
            params={
                "part": "snippet,statistics,brandingSettings",
                "forHandle": handle,
                "key": key,
            },
            timeout=15,
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])
        if not items and channel_id_or_handle.startswith("UC"):
            resp2 = requests.get(
                f"{YT_API_BASE}/channels",
                params={
                    "part": "snippet,statistics,brandingSettings",
                    "id": channel_id_or_handle,
                    "key": key,
                },
                timeout=15,
            )
            resp2.raise_for_status()
            items = resp2.json().get("items", [])
        if not items:
            raise RuntimeError(f"Channel not found: {channel_id_or_handle}")
        item = items[0]
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        return {
            "channel_id": item.get("id", ""),
            "title": snippet.get("title", ""),
            "handle": snippet.get("customUrl", ""),
            "description": snippet.get("description", "")[:300],
            "country": snippet.get("country", ""),
            "created_at": snippet.get("publishedAt", ""),
            "subscribers": int(stats.get("subscriberCount", 0)),
            "total_views": int(stats.get("viewCount", 0)),
            "video_count": int(stats.get("videoCount", 0)),
            "hidden_subscriber_count": stats.get("hiddenSubscriberCount", False),
            "url": f"https://www.youtube.com/@{snippet.get('customUrl', '').lstrip('@')}",
        }
    except Exception as e:
        raise RuntimeError(f"Failed to fetch channel: {e}")

# ── Keyword/topic trends ─────────────────────────────────────────

def fetch_trending_topics(region: str = "US") -> list:
    """Return trending YouTube topic categories with video counts."""
    return [
        {"category": "Science & Technology", "id": "28", "trend": "up", "tip": "AI, coding, gadgets"},
        {"category": "Music", "id": "10", "trend": "stable", "tip": "New releases, covers, music videos"},
        {"category": "Entertainment", "id": "24", "trend": "up", "tip": "Reactions, reviews, celebrity"},
        {"category": "Comedy", "id": "23", "trend": "stable", "tip": "Skits, parody, commentary"},
        {"category": "How-to & Style", "id": "26", "trend": "up", "tip": "Tutorials, DIY, beauty, fashion"},
        {"category": "Gaming", "id": "20", "trend": "stable", "tip": "Let's plays, reviews, esports"},
        {"category": "News & Politics", "id": "25", "trend": "up", "tip": "Breaking news, commentary"},
        {"category": "People & Blogs", "id": "22", "trend": "up", "tip": "Vlogs, lifestyle, day-in-life"},
        {"category": "Sports", "id": "17", "trend": "stable", "tip": "Highlights, analysis, workout"},
    ]
