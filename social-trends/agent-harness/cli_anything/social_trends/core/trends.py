"""Social Trends - Fetch and cache viral trend data from YouTube and TikTok."""

import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from cli_anything.social_trends.core.session import Session
from cli_anything.social_trends.utils.youtube_backend import YouTubeBackend
from cli_anything.social_trends.utils.tiktok_backend import TikTokBackend

YOUTUBE_CATEGORY_MAP = {
    "all": "0",
    "music": "10",
    "gaming": "20",
    "entertainment": "24",
    "news": "25",
    "howto": "26",
    "sports": "17",
    "comedy": "23",
    "people": "22",
    "tech": "28",
    "film": "1",
    "autos": "2",
}

TIKTOK_CATEGORY_MAP = {
    "all": "",
    "dance": "dance",
    "comedy": "comedy",
    "food": "food",
    "beauty": "beauty",
    "fitness": "fitness",
    "fashion": "fashion",
    "music": "music",
    "travel": "travel",
    "pets": "pets",
    "sports": "sports",
    "education": "education",
}


def fetch_trends(
    session: Session,
    platform: str = "both",
    category: str = "all",
    region: str = "US",
    limit: int = 20,
) -> Dict[str, Any]:
    """Fetch trending content from YouTube and/or TikTok."""
    project = session.get_project()
    api_key = project.get("config", {}).get("youtube_api_key", "")

    results: Dict[str, Any] = {
        "fetched_at": datetime.now().isoformat(),
        "platform": platform,
        "category": category,
        "region": region,
        "youtube": [],
        "tiktok": [],
    }

    if platform in ("youtube", "both"):
        yt = YouTubeBackend(api_key=api_key)
        cat_id = YOUTUBE_CATEGORY_MAP.get(category.lower(), "0")
        results["youtube"] = yt.fetch_trending(
            region_code=region,
            category_id=cat_id,
            max_results=limit,
        )

    if platform in ("tiktok", "both"):
        tt = TikTokBackend()
        cat_slug = TIKTOK_CATEGORY_MAP.get(category.lower(), "")
        results["tiktok"] = tt.fetch_trending(
            category=cat_slug,
            region=region,
            limit=limit,
        )

    session.snapshot("fetch trends")
    _cache_trends(project, results)

    return {
        "success": True,
        "fetched_at": results["fetched_at"],
        "youtube_count": len(results["youtube"]),
        "tiktok_count": len(results["tiktok"]),
        "youtube_trends": results["youtube"],
        "tiktok_trends": results["tiktok"],
    }


def list_cached_trends(session: Session, platform: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return previously fetched trends from the project cache."""
    project = session.get_project()
    cached = project.get("trends", [])

    if platform:
        cached = [t for t in cached if t.get("platform") == platform]

    return sorted(cached, key=lambda t: t.get("view_count", 0), reverse=True)


def search_trends(
    session: Session,
    query: str,
    platform: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Search cached trends by keyword in title, description, or hashtags."""
    project = session.get_project()
    cached = project.get("trends", [])
    q = query.lower()

    results = []
    for trend in cached:
        if platform and trend.get("platform") != platform:
            continue
        title = trend.get("title", "").lower()
        desc = trend.get("description", "").lower()
        tags = " ".join(trend.get("hashtags", [])).lower()
        if q in title or q in desc or q in tags:
            results.append(trend)

    return sorted(results, key=lambda t: t.get("view_count", 0), reverse=True)


def get_top_trends(
    session: Session,
    platform: Optional[str] = None,
    n: int = 10,
) -> List[Dict[str, Any]]:
    """Return the top N cached trends by view count."""
    all_trends = list_cached_trends(session, platform=platform)
    return all_trends[:n]


def extract_trend_hashtags(session: Session) -> List[Dict[str, Any]]:
    """Pull all unique hashtags from cached trends with frequency counts."""
    project = session.get_project()
    freq: Dict[str, Dict[str, Any]] = {}

    for trend in project.get("trends", []):
        platform = trend.get("platform", "unknown")
        for tag in trend.get("hashtags", []):
            tag = tag.lower().lstrip("#")
            if tag not in freq:
                freq[tag] = {"tag": tag, "count": 0, "platforms": set(), "avg_views": 0, "total_views": 0}
            freq[tag]["count"] += 1
            freq[tag]["platforms"].add(platform)
            freq[tag]["total_views"] += trend.get("view_count", 0)

    result = []
    for tag, data in freq.items():
        count = data["count"]
        result.append({
            "tag": tag,
            "frequency": count,
            "platforms": list(data["platforms"]),
            "avg_views": int(data["total_views"] / count) if count > 0 else 0,
        })

    return sorted(result, key=lambda x: (x["frequency"], x["avg_views"]), reverse=True)


def _cache_trends(project: Dict[str, Any], results: Dict[str, Any]) -> None:
    """Merge fetched trends into project cache, deduplicating by video_id."""
    existing_ids = {t.get("video_id") for t in project.get("trends", [])}
    new_entries = []

    fetched_at = results["fetched_at"]

    for item in results.get("youtube", []):
        if item.get("video_id") not in existing_ids:
            item["fetched_at"] = fetched_at
            new_entries.append(item)
            existing_ids.add(item.get("video_id"))

    for item in results.get("tiktok", []):
        if item.get("video_id") not in existing_ids:
            item["fetched_at"] = fetched_at
            new_entries.append(item)
            existing_ids.add(item.get("video_id"))

    project.setdefault("trends", []).extend(new_entries)

    # Cap cache at 500 items, keeping highest view counts
    if len(project["trends"]) > 500:
        project["trends"] = sorted(
            project["trends"],
            key=lambda t: t.get("view_count", 0),
            reverse=True,
        )[:500]
