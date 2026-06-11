"""TikTok trend analysis — fetch, parse, and summarize trending content."""

from __future__ import annotations

from cli_anything.tiktok.utils.tiktok_backend import (
    get_trending_videos,
    get_hashtag_videos,
    extract_trends_from_videos,
)


def fetch_trending(region: str = "US", limit: int = 20,
                   session_id: str | None = None) -> dict:
    """Fetch trending videos and extract trend signals."""
    videos = get_trending_videos(region=region, limit=limit, session_id=session_id)
    trends = extract_trends_from_videos(videos)
    return {
        "region": region,
        "video_count": len(videos),
        "videos": videos,
        "trending_hashtags": trends["trending_hashtags"],
        "trending_sounds": trends["trending_sounds"],
    }


def fetch_by_hashtag(tag: str, limit: int = 20,
                     session_id: str | None = None) -> dict:
    """Fetch top videos for a hashtag and extract trends."""
    tag = tag.lstrip("#").strip()
    videos = get_hashtag_videos(tag, limit=limit, session_id=session_id)
    trends = extract_trends_from_videos(videos)
    return {
        "hashtag": f"#{tag}",
        "video_count": len(videos),
        "videos": videos,
        "related_hashtags": trends["trending_hashtags"],
        "trending_sounds": trends["trending_sounds"],
    }


def build_trend_report(region: str = "US", limit: int = 30) -> dict:
    """Build a comprehensive daily trend report."""
    result = fetch_trending(region=region, limit=limit)
    top_tags = result["trending_hashtags"][:15]
    top_sounds = result["trending_sounds"][:10]

    high_perf = sorted(
        result["videos"],
        key=lambda v: (v.get("view_count") or 0),
        reverse=True,
    )[:5]

    return {
        "date": _today(),
        "region": region,
        "total_videos_analyzed": result["video_count"],
        "top_hashtags": top_tags,
        "top_sounds": top_sounds,
        "top_videos": high_perf,
        "insights": _generate_insights(result),
    }


def _generate_insights(data: dict) -> list[str]:
    insights = []
    tags = [t["hashtag"] for t in data.get("trending_hashtags", [])[:5]]
    if tags:
        insights.append(f"Top trending hashtags right now: " + ", ".join(f"#{t}" for t in tags))
    sounds = [s["title"] for s in data.get("trending_sounds", [])[:3]]
    if sounds:
        insights.append(f"Viral sounds to use: " + ", ".join(sounds))
    vids = data.get("videos", [])
    avg_views = sum(v.get("view_count") or 0 for v in vids) / max(len(vids), 1)
    if avg_views > 0:
        insights.append(f"Average views on trending page: {avg_views:,.0f}")
    return insights


def _today() -> str:
    from datetime import date
    return date.today().isoformat()
