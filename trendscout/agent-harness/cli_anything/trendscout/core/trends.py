"""Trend aggregation and cross-platform analysis."""

from datetime import datetime
from typing import Any, Dict, List, Optional


def aggregate(
    youtube_data: Optional[Dict[str, Any]] = None,
    tiktok_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Merge YouTube and TikTok trend data into a unified report."""
    sources = []
    all_hashtags: Dict[str, int] = {}
    all_videos: List[Dict] = []
    summary: Dict[str, Any] = {}

    if youtube_data:
        sources.append("youtube")
        for entry in youtube_data.get("top_hashtags", []):
            tag = entry["hashtag"]
            all_hashtags[tag] = all_hashtags.get(tag, 0) + entry.get("count", 1) * 2  # weight YT
        for v in youtube_data.get("videos", []):
            v["_platform"] = "youtube"
            all_videos.append(v)
        summary["youtube"] = {
            "video_count": youtube_data.get("video_count", 0),
            "top_video": (youtube_data.get("videos") or [{}])[0].get("title", ""),
            "fetch_method": youtube_data.get("fetch_method", ""),
        }

    if tiktok_data:
        sources.append("tiktok")
        for entry in tiktok_data.get("top_hashtags", []):
            tag = entry["hashtag"]
            all_hashtags[tag] = all_hashtags.get(tag, 0) + entry.get("count", 1)
        for v in tiktok_data.get("videos", []):
            v["_platform"] = "tiktok"
            all_videos.append(v)
        summary["tiktok"] = {
            "video_count": tiktok_data.get("video_count", 0),
            "top_video": (tiktok_data.get("videos") or [{}])[0].get("description", "")[:60],
            "fetch_method": tiktok_data.get("fetch_method", ""),
        }

    ranked_tags = sorted(all_hashtags.items(), key=lambda x: x[1], reverse=True)

    crossplatform = [
        {"hashtag": tag, "score": score, "platforms": _tag_platforms(tag, youtube_data, tiktok_data)}
        for tag, score in ranked_tags
        if _tag_on_multiple(tag, youtube_data, tiktok_data)
    ]

    return {
        "generated_at": datetime.now().isoformat(),
        "platforms": sources,
        "total_videos_analyzed": len(all_videos),
        "top_hashtags": [{"hashtag": t, "score": s} for t, s in ranked_tags[:30]],
        "crossplatform_trends": crossplatform[:15],
        "platform_summary": summary,
    }


def _tag_set(data: Optional[Dict[str, Any]]) -> set:
    if not data:
        return set()
    return {e["hashtag"] for e in data.get("top_hashtags", [])}


def _tag_on_multiple(
    tag: str,
    youtube_data: Optional[Dict],
    tiktok_data: Optional[Dict],
) -> bool:
    yt = _tag_set(youtube_data)
    tt = _tag_set(tiktok_data)
    return tag in yt and tag in tt


def _tag_platforms(
    tag: str,
    youtube_data: Optional[Dict],
    tiktok_data: Optional[Dict],
) -> List[str]:
    platforms = []
    if tag in _tag_set(youtube_data):
        platforms.append("youtube")
    if tag in _tag_set(tiktok_data):
        platforms.append("tiktok")
    return platforms


def score_video_potential(video: Dict[str, Any]) -> int:
    """Heuristic virality score 0-100 for a single video."""
    views = video.get("view_count", 0) or 0
    likes = video.get("like_count", 0) or 0
    comments = video.get("comment_count", 0) or 0

    engagement = (likes + comments * 3) / max(views, 1) * 100
    score = min(int(engagement * 10 + (views / 1_000_000) * 5), 100)
    return score


def recommend_hashtags(
    niche: str,
    platform: str = "both",
    youtube_data: Optional[Dict] = None,
    tiktok_data: Optional[Dict] = None,
) -> List[Dict[str, Any]]:
    """Suggest optimal hashtag mix for a given niche."""
    from cli_anything.trendscout.core.tiktok import NICHE_HASHTAGS

    niche_tags = NICHE_HASHTAGS.get(niche.lower(), [])
    trending: Dict[str, int] = {}

    if youtube_data and platform in ("youtube", "both"):
        for entry in youtube_data.get("top_hashtags", []):
            trending[entry["hashtag"]] = trending.get(entry["hashtag"], 0) + 2

    if tiktok_data and platform in ("tiktok", "both"):
        for entry in tiktok_data.get("top_hashtags", []):
            trending[entry["hashtag"]] = trending.get(entry["hashtag"], 0) + 1

    recommendations = []

    # Add niche-specific tags
    for tag in niche_tags[:5]:
        recommendations.append({
            "hashtag": f"#{tag}",
            "type": "niche",
            "trending_score": trending.get(f"#{tag}", 0),
            "reason": f"Core {niche} niche tag",
        })

    # Add trending overlap tags
    for tag, score in sorted(trending.items(), key=lambda x: x[1], reverse=True)[:10]:
        clean = tag.lstrip("#").lower()
        if clean not in niche_tags:
            recommendations.append({
                "hashtag": tag,
                "type": "trending",
                "trending_score": score,
                "reason": "Currently trending on tracked platforms",
            })

    # Always recommend core viral tags
    for vtag in ["#fyp", "#viral", "#trending"]:
        if not any(r["hashtag"] == vtag for r in recommendations):
            recommendations.append({
                "hashtag": vtag,
                "type": "evergreen",
                "trending_score": 100,
                "reason": "High-reach evergreen tag",
            })

    return recommendations[:20]
