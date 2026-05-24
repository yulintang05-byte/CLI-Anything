"""Trending music / sounds for TikTok and YouTube.

TikTok: Creative Center sounds API (no auth required).
YouTube: trending music category via YouTube Data API v3.
"""

from __future__ import annotations

from cli_anything.social_trends.utils.scraper_backend import (
    get, load_config,
    TIKTOK_CC_BASE, YOUTUBE_API_BASE,
)


def get_tiktok_trending_sounds(
    region: str = "US",
    period: int = 7,
    sort_by: str = "popular",
    limit: int = 20,
    page: int = 1,
    bypass_cache: bool = False,
) -> dict:
    """Fetch trending sounds/music from TikTok Creative Center.

    Args:
        region: Country code (e.g. "US", "GB", "IN").
        period: 7, 30, or 120 days.
        sort_by: "popular" or "new".
        limit: Results per page (max 50).
        page: Page number.
        bypass_cache: Skip cache.

    Returns:
        Dict with ``sounds`` list including title, artist, usage counts.
    """
    valid_periods = {7, 30, 120}
    period = period if period in valid_periods else 7
    sort_by = sort_by if sort_by in ("popular", "new") else "popular"

    params = {
        "limit": min(limit, 50),
        "period": period,
        "region": region.upper(),
        "page": page,
        "sort_by": sort_by,
    }
    try:
        data = get(
            f"{TIKTOK_CC_BASE}/trending/music/list",
            params=params,
            bypass_cache=bypass_cache,
        )
    except Exception as e:
        return {"error": str(e), "sounds": []}

    sounds = []
    for item in data.get("data", {}).get("list", []):
        sounds.append({
            "music_id": item.get("music_id") or item.get("id"),
            "title": item.get("music_name") or item.get("title"),
            "artist": item.get("author") or item.get("artist_name"),
            "duration_sec": item.get("duration"),
            "video_count": item.get("video_count") or item.get("use_count"),
            "rank": item.get("rank"),
            "trend_score": item.get("trend_score"),
            "cover_url": item.get("cover_large") or item.get("cover_url"),
            "play_url": item.get("play_url"),
            "is_original": item.get("is_original", False),
            "region": item.get("country") or region.upper(),
        })

    return {
        "source": "tiktok_creative_center",
        "region": region.upper(),
        "period_days": period,
        "sort_by": sort_by,
        "count": len(sounds),
        "sounds": sounds,
    }


def search_tiktok_sounds(
    query: str,
    region: str = "US",
    limit: int = 20,
    bypass_cache: bool = False,
) -> dict:
    """Search TikTok sounds by keyword via Creative Center.

    Args:
        query: Search keyword (song title, artist name).
        region: Country code.
        limit: Max results.
        bypass_cache: Skip cache.

    Returns:
        Dict with matching ``sounds``.
    """
    params = {
        "keyword": query,
        "region": region.upper(),
        "limit": min(limit, 50),
    }
    try:
        data = get(
            f"{TIKTOK_CC_BASE}/trending/music/search",
            params=params,
            bypass_cache=bypass_cache,
        )
    except Exception as e:
        # Fallback: filter from trending list
        trending = get_tiktok_trending_sounds(region=region, limit=50, bypass_cache=bypass_cache)
        q = query.lower()
        filtered = [
            s for s in trending.get("sounds", [])
            if q in (s.get("title") or "").lower()
            or q in (s.get("artist") or "").lower()
        ]
        return {
            "query": query,
            "source": "filtered_trending",
            "note": f"Search API unavailable ({e}); filtered from trending list",
            "count": len(filtered),
            "sounds": filtered,
        }

    sounds = []
    for item in data.get("data", {}).get("list", []):
        sounds.append({
            "music_id": item.get("music_id") or item.get("id"),
            "title": item.get("music_name") or item.get("title"),
            "artist": item.get("author") or item.get("artist_name"),
            "video_count": item.get("video_count") or item.get("use_count"),
            "duration_sec": item.get("duration"),
            "cover_url": item.get("cover_large") or item.get("cover_url"),
            "play_url": item.get("play_url"),
        })

    return {
        "query": query,
        "source": "tiktok_creative_center_search",
        "region": region.upper(),
        "count": len(sounds),
        "sounds": sounds,
    }


def get_youtube_trending_music(
    region_code: str = "US",
    max_results: int = 25,
    bypass_cache: bool = False,
) -> dict:
    """Fetch trending music videos from YouTube (category 10).

    Requires a YouTube Data API v3 key (set via `config set youtube_api_key`).

    Args:
        region_code: ISO country code.
        max_results: Number of results.
        bypass_cache: Skip cache.

    Returns:
        Dict with ``videos`` list of trending music.
    """
    config = load_config()
    api_key = config.get("youtube_api_key")
    if not api_key:
        return {
            "error": "youtube_api_key not configured",
            "tip": "Run: cli-anything-social-trends config set youtube_api_key YOUR_KEY",
            "videos": [],
        }

    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region_code,
        "videoCategoryId": "10",  # Music
        "maxResults": min(max_results, 50),
        "key": api_key,
    }
    try:
        data = get(
            f"{YOUTUBE_API_BASE}/videos",
            params=params,
            bypass_cache=bypass_cache,
        )
    except Exception as e:
        return {"error": str(e), "videos": []}

    videos = []
    for item in data.get("items", []):
        s = item.get("snippet", {})
        stats = item.get("statistics", {})
        videos.append({
            "video_id": item.get("id"),
            "title": s.get("title"),
            "channel": s.get("channelTitle"),
            "published_at": s.get("publishedAt"),
            "tags": s.get("tags", []),
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "url": f"https://www.youtube.com/watch?v={item.get('id')}",
        })

    return {
        "source": "youtube_api_v3",
        "category": "music",
        "region": region_code,
        "count": len(videos),
        "videos": videos,
    }


def get_cross_platform_music_trends(region: str = "US") -> dict:
    """Get trending music across both TikTok and YouTube in one call.

    Args:
        region: Country code.

    Returns:
        Unified dict with ``tiktok_sounds`` and ``youtube_music`` sections.
    """
    tiktok = get_tiktok_trending_sounds(region=region)
    youtube = get_youtube_trending_music(region_code=region)

    # Find overlapping artist/song names
    yt_titles = {(v.get("title") or "").lower() for v in youtube.get("videos", [])}
    crossover = [
        s for s in tiktok.get("sounds", [])
        if any(
            (s.get("title") or "").lower() in yt
            or (s.get("artist") or "").lower() in yt
            for yt in yt_titles
        )
    ]

    return {
        "region": region,
        "tiktok_sounds": tiktok,
        "youtube_music": youtube,
        "cross_platform_hits": {
            "count": len(crossover),
            "sounds": crossover,
            "insight": (
                "These sounds appear on both platforms — using them maximises "
                "discoverability across TikTok and YouTube Shorts simultaneously."
            ),
        },
    }
