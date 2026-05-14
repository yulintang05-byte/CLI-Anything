"""Trend analysis: aggregate, score, and rank content across platforms."""

from __future__ import annotations
from typing import Any
from collections import Counter


def score_video(video: dict) -> float:
    """Engagement score normalized for comparison across platforms."""
    plays = video.get("plays", video.get("views", 0)) or 0
    likes = video.get("likes", 0) or 0
    comments = video.get("comments", 0) or 0
    shares = video.get("shares", 0) or 0
    # Weighted engagement rate proxy
    engagement = likes * 1.0 + comments * 2.0 + shares * 3.0
    if plays > 0:
        return round((engagement / max(plays, 1)) * 100, 4)
    return 0.0


def merge_trends(yt_videos: list[dict], tt_videos: list[dict]) -> list[dict]:
    """Merge YouTube and TikTok trending into a unified ranked list."""
    combined = []
    for v in yt_videos:
        v = {**v, "engagement_score": score_video(v)}
        combined.append(v)
    for v in tt_videos:
        v = {**v, "engagement_score": score_video(v)}
        combined.append(v)
    combined.sort(key=lambda x: x["engagement_score"], reverse=True)
    for i, item in enumerate(combined):
        item["combined_rank"] = i + 1
    return combined


def top_hashtags_across_platforms(
    yt_tags: list[dict], tt_tags: list[dict], limit: int = 20
) -> list[dict]:
    """Merge and rank hashtags from both platforms."""
    merged: dict[str, dict] = {}
    for tag_info in yt_tags:
        tag = tag_info["tag"].lower().lstrip("#")
        if tag not in merged:
            merged[tag] = {"tag": f"#{tag}", "youtube_count": 0, "tiktok_count": 0, "total": 0}
        merged[tag]["youtube_count"] += tag_info.get("count", 1)
        merged[tag]["total"] += tag_info.get("count", 1)
    for tag_info in tt_tags:
        tag = tag_info["tag"].lower().lstrip("#")
        if tag not in merged:
            merged[tag] = {"tag": f"#{tag}", "youtube_count": 0, "tiktok_count": 0, "total": 0}
        val = tag_info.get("video_count", tag_info.get("count", 1))
        merged[tag]["tiktok_count"] += val
        merged[tag]["total"] += val
    ranked = sorted(merged.values(), key=lambda x: x["total"], reverse=True)
    for i, item in enumerate(ranked[:limit]):
        item["cross_platform_rank"] = i + 1
    return ranked[:limit]


def trend_velocity(videos: list[dict]) -> list[dict]:
    """Estimate velocity: high-engagement items relative to their rank position."""
    results = []
    for v in videos:
        rank = v.get("rank", v.get("combined_rank", 99))
        score = score_video(v)
        velocity = round(score / max(rank, 1), 6)
        results.append({**v, "velocity": velocity})
    return sorted(results, key=lambda x: x["velocity"], reverse=True)


def niche_affinity(videos: list[dict], keywords: list[str]) -> list[dict]:
    """Filter and score videos by niche keyword relevance."""
    kw_lower = [k.lower() for k in keywords]
    scored = []
    for v in videos:
        text = (
            v.get("title", "") + " " +
            v.get("description", "") + " " +
            " ".join(v.get("hashtags", []))
        ).lower()
        hits = sum(1 for kw in kw_lower if kw in text)
        if hits > 0:
            scored.append({**v, "niche_score": hits})
    return sorted(scored, key=lambda x: x["niche_score"], reverse=True)


def content_gap_analysis(yt_tags: list[dict], tt_tags: list[dict]) -> dict[str, list[dict]]:
    """Find tags trending on one platform but not the other — content opportunity gaps."""
    yt_set = {t["tag"].lower().lstrip("#") for t in yt_tags}
    tt_set = {t["tag"].lower().lstrip("#") for t in tt_tags}

    yt_only = [t for t in yt_tags if t["tag"].lower().lstrip("#") not in tt_set]
    tt_only = [t for t in tt_tags if t["tag"].lower().lstrip("#") not in yt_set]
    both = [
        t for t in yt_tags if t["tag"].lower().lstrip("#") in tt_set
    ]
    return {
        "youtube_only": yt_only[:10],
        "tiktok_only": tt_only[:10],
        "cross_platform_opportunities": both[:10],
    }
