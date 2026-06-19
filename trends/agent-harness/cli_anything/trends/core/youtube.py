"""YouTube trending — high-level interface wrapping youtube_backend."""

from __future__ import annotations

from typing import Optional

from cli_anything.trends.utils import youtube_backend as _yt


def fetch_trending(
    api_key: str,
    region: str = "US",
    category: str = "all",
    max_results: int = 50,
) -> dict:
    """Fetch trending YouTube videos and extract aggregated signals."""
    videos = _yt.get_trending_videos(
        api_key, region=region, category=category, max_results=max_results
    )
    hashtags = _yt.aggregate_hashtags(videos)
    top_videos = sorted(videos, key=lambda v: v.get("views", 0), reverse=True)

    return {
        "platform": "youtube",
        "region": region,
        "category": category,
        "video_count": len(videos),
        "videos": top_videos,
        "hashtags": hashtags[:30],
        "top_channels": _top_channels(videos, n=10),
    }


def fetch_trending_music(
    api_key: str,
    region: str = "US",
    max_results: int = 50,
) -> dict:
    """Fetch trending music from YouTube (category 10)."""
    videos = _yt.get_trending_music(api_key, region=region, max_results=max_results)
    music_trends = _yt.aggregate_music_trends(videos)
    hashtags = _yt.aggregate_hashtags(videos)

    return {
        "platform": "youtube",
        "region": region,
        "category": "music",
        "video_count": len(videos),
        "videos": videos,
        "music_trends": music_trends[:20],
        "hashtags": hashtags[:20],
    }


def _top_channels(videos: list[dict], n: int = 10) -> list[dict]:
    from collections import defaultdict
    ch_views: dict[str, int] = defaultdict(int)
    ch_count: dict[str, int] = defaultdict(int)
    for v in videos:
        ch = v.get("channel", "")
        if ch:
            ch_views[ch] += v.get("views", 0)
            ch_count[ch] += 1
    results = [
        {"channel": ch, "total_views": views, "video_count": ch_count[ch]}
        for ch, views in sorted(ch_views.items(), key=lambda x: x[1], reverse=True)[:n]
    ]
    return results
