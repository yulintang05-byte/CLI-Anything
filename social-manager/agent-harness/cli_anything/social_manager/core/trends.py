"""Trend aggregation — pulls viral data from YouTube and TikTok and formats reports."""
import json
from datetime import datetime
from typing import Optional

from cli_anything.social_manager.utils import youtube_client, tiktok_client
from cli_anything.social_manager.utils.config import get as cfg_get


def get_tiktok_trends(region: str = "US", period: int = 7, limit: int = 20) -> dict:
    hashtags = tiktok_client.fetch_trending_hashtags(region=region, period=period, limit=limit)
    sounds = tiktok_client.fetch_trending_sounds(region=region, period=period, limit=limit)
    return {
        "platform": "TikTok",
        "region": region,
        "period_days": period,
        "fetched_at": datetime.utcnow().isoformat(),
        "trending_hashtags": hashtags,
        "trending_sounds": sounds,
    }


def get_youtube_trends(
    region: str = "US",
    category: str = "",
    max_results: int = 25,
    api_key: Optional[str] = None,
) -> dict:
    key = api_key or cfg_get("youtube_api_key")
    if not key:
        return _youtube_fallback(region)

    try:
        videos = youtube_client.fetch_trending_videos(key, region=region, category_id=category, max_results=max_results)
        top_hashtags = youtube_client.extract_top_hashtags(videos)
        music = youtube_client.fetch_trending_music(key, region=region, max_results=15)
        return {
            "platform": "YouTube",
            "region": region,
            "fetched_at": datetime.utcnow().isoformat(),
            "trending_videos": videos,
            "top_hashtags": top_hashtags,
            "trending_music": music,
        }
    except Exception as e:
        return {"platform": "YouTube", "error": str(e), "region": region}


def _youtube_fallback(region: str) -> dict:
    """Curated June 2026 YouTube trend data when no API key is configured."""
    return {
        "platform": "YouTube",
        "region": region,
        "fetched_at": datetime.utcnow().isoformat(),
        "note": "Static fallback — add YouTube API key via: cli-anything-social config set youtube_api_key YOUR_KEY",
        "trending_topics": [
            "World Cup 2026 highlights",
            "Olivia Rodrigo new album reaction",
            "AI tools for creators 2026",
            "Summer travel vlogs",
            "Finance tips for Gen Z",
            "Startup growth stories",
            "Lofi study playlists",
            "Try-on hauls",
            "Gaming (Roblox, competitive FPS)",
            "Commentary / drama channels",
        ],
        "top_hashtags": [
            ("#Shorts", 50), ("#Music", 38), ("#Gaming", 30), ("#Viral", 27),
            ("#Trending", 24), ("#Subscribe", 20), ("#Travel", 18), ("#WorldCup2026", 16),
            ("#AI", 14), ("#Finance", 12), ("#Tech", 11), ("#Funny", 10),
            ("#Motivation", 9), ("#LoFi", 8), ("#Vlog", 7),
        ],
        "trending_music": [
            {"title": "Like a Prayer (Remix)", "artist": "Josh Fawaz", "trend": "Summer Anthem"},
            {"title": "Rock Music", "artist": "Charli XCX", "trend": "Glitch Edit Format"},
            {"title": "The Puerto Rico Song", "artist": "Saxboy Billy", "trend": "Summer Earworm"},
            {"title": "Olivia Rodrigo – New Album Tracks", "artist": "Olivia Rodrigo", "trend": "Lyric Overlays"},
        ],
    }


def generate_trend_report(region: str = "US") -> dict:
    """Full viral intelligence report combining YouTube + TikTok."""
    tiktok = get_tiktok_trends(region=region)
    youtube = get_youtube_trends(region=region)

    # Cross-platform rising topics
    cross_platform = [
        "World Cup 2026",
        "Summer travel content",
        "AI tools / automation",
        "Personal finance",
        "Love Island",
        "Y2K aesthetics",
        "Entrepreneur/startup",
        "Olivia Rodrigo new album",
    ]

    return {
        "report_date": datetime.utcnow().strftime("%Y-%m-%d"),
        "region": region,
        "cross_platform_trends": cross_platform,
        "tiktok": tiktok,
        "youtube": youtube,
    }
