"""Trend fetching and aggregation across YouTube and TikTok."""

from datetime import datetime, timezone
from typing import Any

from cli_anything.social_trends.utils import youtube_backend as yt
from cli_anything.social_trends.utils import tiktok_backend as tt


def fetch_platform_trends(platform: str, niche: str = "general", region: str = "US",
                          max_results: int = 25) -> dict:
    """Fetch trending content from a platform and return normalised results."""
    platform = platform.lower()
    fetched_at = datetime.now(timezone.utc).isoformat()

    if platform == "youtube":
        videos = yt.fetch_trending_videos(region=region, max_results=max_results)
        hashtags = yt.fetch_trending_hashtags_from_videos(region=region)
        shorts = yt.fetch_youtube_shorts_trends(topic=niche, region=region)
        return {
            "platform": "youtube",
            "niche": niche,
            "region": region,
            "fetched_at": fetched_at,
            "trending_videos": videos[:max_results],
            "trending_hashtags": hashtags[:30],
            "shorts_trends": shorts[:10],
            "summary": _youtube_summary(videos),
        }

    if platform == "tiktok":
        hashtags = tt.fetch_trending_hashtags(niche=niche, region=region)
        sounds = tt.fetch_trending_sounds(niche=niche)
        return {
            "platform": "tiktok",
            "niche": niche,
            "region": region,
            "fetched_at": fetched_at,
            "trending_hashtags": hashtags,
            "trending_sounds": sounds,
            "summary": _tiktok_summary(niche),
        }

    if platform == "all":
        yt_data = fetch_platform_trends("youtube", niche=niche, region=region, max_results=max_results)
        tt_data = fetch_platform_trends("tiktok", niche=niche, region=region)
        cross = _cross_platform_insights(yt_data, tt_data, niche)
        return {
            "platform": "all",
            "niche": niche,
            "region": region,
            "fetched_at": fetched_at,
            "youtube": yt_data,
            "tiktok": tt_data,
            "cross_platform_insights": cross,
        }

    return {"error": f"Unknown platform '{platform}'. Use: youtube, tiktok, all"}


def search_trends(query: str, platform: str = "youtube", max_results: int = 20) -> dict:
    """Search for content trends matching a query."""
    platform = platform.lower()
    if platform == "youtube":
        results = yt.search_trending_by_topic(query, max_results=max_results)
        return {
            "platform": "youtube",
            "query": query,
            "results": results,
            "count": len(results),
        }
    if platform == "tiktok":
        # yt-dlp hashtag search on TikTok
        tag = query.lstrip("#").replace(" ", "")
        results = tt._ytdlp_fetch(
            f"https://www.tiktok.com/tag/{tag}",
            ["--playlist-end", str(max_results)],
        )
        if results:
            return {
                "platform": "tiktok",
                "query": f"#{tag}",
                "results": [{
                    "id": e.get("id", ""),
                    "title": e.get("title", ""),
                    "url": e.get("url") or e.get("webpage_url", ""),
                    "view_count": e.get("view_count", 0),
                } for e in results],
                "count": len(results),
            }
        return {
            "platform": "tiktok",
            "query": f"#{tag}",
            "note": "Install yt-dlp or set TikTok API credentials for live search",
            "results": [],
        }
    return {"error": f"Unknown platform '{platform}'"}


def compare_platforms(niche: str, region: str = "US") -> dict:
    """Side-by-side comparison of trends across YouTube and TikTok for a niche."""
    yt_tags = yt.fetch_trending_hashtags_from_videos(region=region)
    tt_tags = tt.fetch_trending_hashtags(niche=niche, region=region)

    yt_tag_names = {t.get("hashtag", "") for t in yt_tags if isinstance(t, dict) and "hashtag" in t}
    tt_tag_names: set[str] = set()
    tt_tags_list = tt_tags.get("hashtags", [])
    for t in tt_tags_list:
        if isinstance(t, dict):
            name = t.get("name", "")
        else:
            name = str(t)
        if name:
            tt_tag_names.add(name)

    shared = yt_tag_names & tt_tag_names
    yt_only = yt_tag_names - tt_tag_names
    tt_only = tt_tag_names - yt_tag_names

    return {
        "niche": niche,
        "region": region,
        "shared_hashtags": sorted(shared)[:15],
        "youtube_only": sorted(yt_only)[:15],
        "tiktok_only": sorted(tt_only)[:15],
        "recommendation": (
            "Use shared hashtags on both platforms. "
            "YouTube-only tags work well for long-form SEO. "
            "TikTok-only tags are ideal for short-form discovery."
        ),
    }


def _youtube_summary(videos: list[dict]) -> dict:
    if not videos or "source" in videos[0]:
        return {"note": "Set YOUTUBE_API_KEY for detailed analytics"}
    views = [v.get("views", 0) for v in videos if isinstance(v.get("views"), int)]
    categories: dict[str, int] = {}
    for v in videos:
        cat = v.get("category", "Unknown")
        categories[cat] = categories.get(cat, 0) + 1
    top_cat = max(categories, key=lambda k: categories[k]) if categories else "N/A"
    return {
        "total_videos_analysed": len(videos),
        "avg_views": int(sum(views) / len(views)) if views else 0,
        "max_views": max(views) if views else 0,
        "top_category": top_cat,
        "category_breakdown": categories,
    }


def _tiktok_summary(niche: str) -> dict:
    return {
        "niche": niche,
        "optimal_video_length": "15–30 seconds for max completion rate",
        "posting_frequency": "1–3 times/day for algorithm boost",
        "best_posting_windows": _best_posting_times(niche),
        "hook_rule": "First 1–3 seconds must stop the scroll",
    }


def _cross_platform_insights(yt_data: dict, tt_data: dict, niche: str) -> list[str]:
    return [
        f"Repurpose YouTube Shorts as TikTok videos — same format, double the reach",
        f"YouTube SEO titles → TikTok text overlay captions for the '{niche}' niche",
        "Post TikTok first (faster virality), then upload to YouTube Shorts/Reels",
        "Trending TikTok sounds often predict YouTube trending music 2–4 weeks later",
        "Cross-post highest-performing content within 24h of peak engagement",
        "Use identical hashtag core across platforms but add 3–5 platform-specific tags",
    ]


def _best_posting_times(niche: str) -> list[str]:
    # Engagement research-backed windows (UTC offsets adjusted for US/global audiences)
    base_times = {
        "fitness": ["6–8 AM", "12–1 PM", "6–8 PM"],
        "food": ["11 AM–1 PM", "5–7 PM", "8–10 PM"],
        "fashion": ["9–11 AM", "1–3 PM", "7–9 PM"],
        "beauty": ["7–9 AM", "12–2 PM", "7–9 PM"],
        "finance": ["7–9 AM", "12–1 PM", "6–8 PM"],
        "gaming": ["3–5 PM", "7–9 PM", "10 PM–12 AM"],
        "education": ["8–10 AM", "12–2 PM", "5–7 PM"],
        "comedy": ["12–2 PM", "5–7 PM", "9–11 PM"],
        "motivation": ["6–8 AM", "12–1 PM", "5–7 PM"],
        "general": ["9–11 AM", "12–3 PM", "7–9 PM"],
    }
    return base_times.get(niche.lower(), base_times["general"])
