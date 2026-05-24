"""Viral trend scraping — YouTube and TikTok.

YouTube: uses YouTube Data API v3 (requires API key) with RSS feed fallback.
TikTok: uses TikTok Creative Center public API (no auth required).
"""

from __future__ import annotations
import xml.etree.ElementTree as ET
from typing import Any

from cli_anything.social_trends.utils.scraper_backend import (
    get, get_html, load_config,
    TIKTOK_CC_BASE, YOUTUBE_API_BASE, YOUTUBE_RSS_TRENDING,
)


# ── YouTube ───────────────────────────────────────────────────────────────────

def get_youtube_trending(
    region_code: str = "US",
    category_id: str = "0",
    max_results: int = 25,
    bypass_cache: bool = False,
) -> dict:
    """Fetch YouTube trending videos.

    Uses YouTube Data API v3 if an API key is configured; falls back to
    the public RSS feed (fewer fields, no view counts).

    Args:
        region_code: ISO 3166-1 alpha-2 country code (e.g. "US", "GB", "JP").
        category_id: YouTube video category ID ("0" = all categories,
                     "10" = music, "20" = gaming, "24" = entertainment).
        max_results: Number of results (1–50).
        bypass_cache: Skip cached results.

    Returns:
        Dict with ``videos`` list and ``source`` ("api" or "rss").
    """
    config = load_config()
    api_key = config.get("youtube_api_key")

    if api_key:
        return _youtube_trending_api(
            api_key, region_code, category_id, max_results, bypass_cache
        )
    return _youtube_trending_rss(bypass_cache)


def _youtube_trending_api(
    api_key: str, region_code: str, category_id: str,
    max_results: int, bypass_cache: bool,
) -> dict:
    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region_code,
        "videoCategoryId": category_id,
        "maxResults": min(max_results, 50),
        "key": api_key,
    }
    data = get(f"{YOUTUBE_API_BASE}/videos", params=params, bypass_cache=bypass_cache)

    videos = []
    for item in data.get("items", []):
        s = item.get("snippet", {})
        stats = item.get("statistics", {})
        videos.append({
            "video_id": item.get("id"),
            "title": s.get("title"),
            "channel": s.get("channelTitle"),
            "published_at": s.get("publishedAt"),
            "thumbnail": s.get("thumbnails", {}).get("high", {}).get("url"),
            "tags": s.get("tags", []),
            "category_id": s.get("categoryId"),
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
            "url": f"https://www.youtube.com/watch?v={item.get('id')}",
        })

    return {
        "source": "youtube_api_v3",
        "region": region_code,
        "category_id": category_id,
        "count": len(videos),
        "videos": videos,
    }


def _youtube_trending_rss(bypass_cache: bool) -> dict:
    """Parse YouTube trending RSS feed (public, no key needed)."""
    xml_text = get_html(YOUTUBE_RSS_TRENDING, bypass_cache=bypass_cache)
    ns = {"atom": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return {"source": "rss", "error": "Failed to parse RSS feed", "videos": []}

    videos = []
    for entry in root.findall("atom:entry", ns):
        vid_id_el = entry.find("yt:videoId", ns)
        title_el = entry.find("atom:title", ns)
        author_el = entry.find("atom:author/atom:name", ns)
        published_el = entry.find("atom:published", ns)
        link_el = entry.find("atom:link", ns)
        videos.append({
            "video_id": vid_id_el.text if vid_id_el is not None else None,
            "title": title_el.text if title_el is not None else None,
            "channel": author_el.text if author_el is not None else None,
            "published_at": published_el.text if published_el is not None else None,
            "url": link_el.get("href") if link_el is not None else None,
        })

    return {
        "source": "youtube_rss",
        "note": "Add youtube_api_key via 'config set' for full stats",
        "count": len(videos),
        "videos": videos,
    }


def get_youtube_categories(region_code: str = "US") -> dict:
    """List YouTube video categories for a region (requires API key)."""
    config = load_config()
    api_key = config.get("youtube_api_key")
    if not api_key:
        return {"error": "youtube_api_key not configured. Run: config set youtube_api_key <KEY>"}

    data = get(
        f"{YOUTUBE_API_BASE}/videoCategories",
        params={"part": "snippet", "regionCode": region_code, "key": api_key},
    )
    categories = [
        {"id": c["id"], "name": c["snippet"]["title"]}
        for c in data.get("items", [])
        if c["snippet"].get("assignable")
    ]
    return {"region": region_code, "categories": categories}


# ── TikTok ────────────────────────────────────────────────────────────────────

_VALID_PERIODS = {7, 30, 120}
_VALID_SORTS = {"popular", "new"}


def get_tiktok_trending_hashtags(
    region: str = "US",
    period: int = 7,
    sort_by: str = "popular",
    limit: int = 20,
    page: int = 1,
    bypass_cache: bool = False,
) -> dict:
    """Fetch trending hashtags from TikTok Creative Center (no auth required).

    Args:
        region: Country code (e.g. "US", "GB", "IN", "BR").
        period: Time window — 7, 30, or 120 days.
        sort_by: "popular" or "new".
        limit: Results per page (max 50).
        page: Page number.
        bypass_cache: Skip cache.

    Returns:
        Dict with ``hashtags`` list ranked by trend score.
    """
    period = period if period in _VALID_PERIODS else 7
    sort_by = sort_by if sort_by in _VALID_SORTS else "popular"

    params = {
        "limit": min(limit, 50),
        "period": period,
        "region": region.upper(),
        "page": page,
        "sort_by": sort_by,
    }
    try:
        data = get(
            f"{TIKTOK_CC_BASE}/trending/hashtag/list",
            params=params,
            bypass_cache=bypass_cache,
        )
    except Exception as e:
        return {"error": str(e), "hashtags": [], "tip": "TikTok CC may require browser cookies for some regions"}

    hashtags = []
    for item in data.get("data", {}).get("list", []):
        hashtags.append({
            "hashtag": f"#{item.get('hashtag_name', '')}",
            "name": item.get("hashtag_name"),
            "rank": item.get("rank"),
            "video_count": item.get("video_count"),
            "view_count": item.get("view_count"),
            "trend_score": item.get("trend_score"),
            "country": item.get("country"),
            "publish_cnt": item.get("publish_cnt"),
            "video_views": item.get("video_views"),
        })

    return {
        "source": "tiktok_creative_center",
        "region": region.upper(),
        "period_days": period,
        "sort_by": sort_by,
        "count": len(hashtags),
        "hashtags": hashtags,
    }


def get_tiktok_trending_videos(
    region: str = "US",
    period: int = 7,
    limit: int = 20,
    page: int = 1,
    bypass_cache: bool = False,
) -> dict:
    """Fetch trending TikTok videos from Creative Center.

    Args:
        region: Country code.
        period: 7, 30, or 120 days.
        limit: Results per page.
        page: Page number.
        bypass_cache: Skip cache.

    Returns:
        Dict with ``videos`` list.
    """
    period = period if period in _VALID_PERIODS else 7
    params = {
        "limit": min(limit, 50),
        "period": period,
        "region": region.upper(),
        "page": page,
        "sort_by": "popular",
    }
    try:
        data = get(
            f"{TIKTOK_CC_BASE}/trending/creative/list",
            params=params,
            bypass_cache=bypass_cache,
        )
    except Exception as e:
        return {"error": str(e), "videos": []}

    videos = []
    for item in data.get("data", {}).get("list", []):
        videos.append({
            "video_id": item.get("item_id"),
            "title": item.get("title") or item.get("desc"),
            "author": item.get("author", {}).get("unique_id"),
            "play_count": item.get("play_count"),
            "digg_count": item.get("digg_count"),
            "comment_count": item.get("comment_count"),
            "share_count": item.get("share_count"),
            "hashtags": [h.get("name") for h in item.get("challenges", [])],
            "music_title": item.get("music", {}).get("title"),
            "music_author": item.get("music", {}).get("author_name"),
            "duration": item.get("duration"),
        })

    return {
        "source": "tiktok_creative_center",
        "region": region.upper(),
        "period_days": period,
        "count": len(videos),
        "videos": videos,
    }


def compare_trends(topic: str, region: str = "US") -> dict:
    """Side-by-side trend comparison for a topic across YouTube and TikTok.

    Fetches trending content from both platforms and returns a unified view.

    Args:
        topic: Keyword to filter/match against trending titles/tags.
        region: Country code.

    Returns:
        Dict with ``youtube`` and ``tiktok`` sub-results filtered by topic.
    """
    topic_lower = topic.lower()

    yt = get_youtube_trending(region_code=region)
    yt_filtered = [
        v for v in yt.get("videos", [])
        if topic_lower in (v.get("title") or "").lower()
        or any(topic_lower in t.lower() for t in v.get("tags", []))
    ]

    tt_hash = get_tiktok_trending_hashtags(region=region)
    tt_hash_filtered = [
        h for h in tt_hash.get("hashtags", [])
        if topic_lower in (h.get("name") or "").lower()
    ]

    tt_vid = get_tiktok_trending_videos(region=region)
    tt_vid_filtered = [
        v for v in tt_vid.get("videos", [])
        if topic_lower in (v.get("title") or "").lower()
        or any(topic_lower in (h or "").lower() for h in v.get("hashtags", []))
    ]

    return {
        "topic": topic,
        "region": region,
        "youtube": {"matched_videos": len(yt_filtered), "videos": yt_filtered[:10]},
        "tiktok": {
            "matched_hashtags": len(tt_hash_filtered),
            "hashtags": tt_hash_filtered[:10],
            "matched_videos": len(tt_vid_filtered),
            "videos": tt_vid_filtered[:10],
        },
    }
