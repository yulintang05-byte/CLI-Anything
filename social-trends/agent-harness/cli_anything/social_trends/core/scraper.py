"""High-level scraper — orchestrates YouTube and TikTok scraping."""

from __future__ import annotations

from typing import Callable

from cli_anything.social_trends.utils.social_trends_backend import (
    scrape_youtube_trending,
    scrape_youtube_trending_via_api,
    scrape_tiktok_trending,
    scrape_tiktok_hashtag,
    get_trending_hashtags,
    get_tiktok_trending_sounds,
    get_youtube_api_key,
    get_tiktok_session,
)


def scrape_platform(
    platform: str,
    limit: int = 30,
    country: str = "US",
    use_cache: bool = True,
    on_progress: Callable | None = None,
    youtube_api_key: str | None = None,
    tiktok_session_id: str | None = None,
) -> list[dict]:
    """Scrape trending videos from one or both platforms.

    platform: 'youtube' | 'tiktok' | 'all'
    Returns flat list of normalized video dicts.
    """
    results = []

    if platform in ("youtube", "all"):
        yt_key = get_youtube_api_key(youtube_api_key)
        if yt_key:
            vids = scrape_youtube_trending_via_api(yt_key, country_code=country, limit=limit)
        else:
            vids = scrape_youtube_trending(country_code=country, limit=limit,
                                           use_cache=use_cache, on_progress=on_progress)
        results.extend(vids)

    if platform in ("tiktok", "all"):
        session = get_tiktok_session(tiktok_session_id)
        vids = scrape_tiktok_trending(limit=limit, session_id=session,
                                      use_cache=use_cache, on_progress=on_progress)
        results.extend(vids)

    return results


def get_all_hashtags(videos: list[dict], top_n: int = 30) -> list[dict]:
    return get_trending_hashtags(videos, top_n=top_n)


def get_all_sounds(videos: list[dict]) -> list[dict]:
    tiktok_vids = [v for v in videos if v.get("platform") == "tiktok"]
    return get_tiktok_trending_sounds(tiktok_vids)


def scrape_hashtag_videos(
    hashtag: str,
    platform: str = "tiktok",
    limit: int = 30,
    tiktok_session_id: str | None = None,
) -> list[dict]:
    """Scrape videos for a specific hashtag."""
    session = get_tiktok_session(tiktok_session_id)
    if platform == "tiktok":
        return scrape_tiktok_hashtag(hashtag, limit=limit, session_id=session)
    raise ValueError(f"Hashtag scraping not yet supported for platform: {platform}")
