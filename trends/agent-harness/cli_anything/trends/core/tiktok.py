"""TikTok trending — high-level interface wrapping tiktok_backend."""

from __future__ import annotations

from typing import Optional

from cli_anything.trends.utils import tiktok_backend as _tt


def fetch_trending(
    access_token: Optional[str] = None,
    cookies: Optional[dict] = None,
    region: str = "US",
    count: int = 20,
) -> dict:
    """Fetch trending TikTok videos and signals using best available auth."""
    raw = _tt.get_trending(
        access_token=access_token,
        cookies=cookies,
        region=region,
        count=count,
    )

    videos = raw.get("videos", [])
    hashtags = raw.get("hashtags", [])
    sounds = raw.get("sounds", [])
    source = raw.get("source", "unknown")
    note = raw.get("note")

    top_videos = sorted(videos, key=lambda v: v.get("views", 0), reverse=True)

    result = {
        "platform": "tiktok",
        "region": region,
        "source": source,
        "video_count": len(videos),
        "videos": top_videos,
        "hashtags": hashtags[:30],
        "sounds": sounds[:20],
    }
    if note:
        result["note"] = note
    return result


def fetch_hashtag_info(hashtag: str) -> dict:
    """Get public stats for a specific TikTok hashtag."""
    return _tt.public_get_hashtag_info(hashtag)


def fetch_trending_hashtags(
    access_token: Optional[str] = None,
    region: str = "US",
    max_count: int = 20,
) -> list[dict]:
    """Get trending hashtags from Research API (requires approved key)."""
    if not access_token:
        raise ValueError(
            "TikTok Research API key required for hashtag trends.\n"
            "Apply at: https://developers.tiktok.com/products/research-api/\n"
            "Then: cli-anything-trends config set tiktok_api_key <token>"
        )
    return _tt.research_api_get_trending_hashtags(
        access_token, region=region, max_count=max_count
    )
