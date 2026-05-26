#!/usr/bin/env python3
"""Trend analysis engine — scores, ranks, and cross-references viral trends."""

import re
import math
from collections import Counter
from typing import Any


# Weights for virality scoring
_WEIGHT_VIEWS = 0.40
_WEIGHT_ENGAGEMENT = 0.35   # likes + comments + shares relative to views
_WEIGHT_RECENCY = 0.15
_WEIGHT_CROSS_PLATFORM = 0.10


def _safe_int(val: Any) -> int:
    if isinstance(val, int):
        return val
    if isinstance(val, float):
        return int(val)
    try:
        return int(str(val).replace(",", "").replace("K", "000").replace("M", "000000").replace("B", "000000000"))
    except Exception:
        return 0


def _engagement_rate(item: dict) -> float:
    plays = _safe_int(item.get("plays", item.get("views", 0)))
    if plays == 0:
        return 0.0
    eng = (
        _safe_int(item.get("likes", item.get("like_count", 0)))
        + _safe_int(item.get("comments", item.get("comment_count", 0)))
        + _safe_int(item.get("shares", item.get("share_count", 0)))
    )
    return eng / plays


def virality_score(item: dict) -> float:
    """Compute a 0-100 virality score for a video or hashtag."""
    views = _safe_int(item.get("plays", item.get("views", item.get("view_count", item.get("post_count", 0)))))
    if views == 0:
        return 0.0
    eng_rate = _engagement_rate(item)
    # Log-normalize views (YouTube videos can have 100M+, TikTok 10M+)
    view_score = min(math.log10(max(views, 1)) / 8.0, 1.0)  # 100M views → ~1.0
    eng_score = min(eng_rate / 0.20, 1.0)                   # 20% engagement → max
    cross = 1.0 if item.get("crossover") else 0.0
    score = (
        _WEIGHT_VIEWS * view_score
        + _WEIGHT_ENGAGEMENT * eng_score
        + _WEIGHT_RECENCY * 0.5      # placeholder until we parse dates
        + _WEIGHT_CROSS_PLATFORM * cross
    ) * 100
    return round(score, 1)


def rank_trends(items: list[dict]) -> list[dict]:
    """Add virality_score to each item and return sorted by score desc."""
    scored = []
    for item in items:
        item = dict(item)
        item["virality_score"] = virality_score(item)
        scored.append(item)
    return sorted(scored, key=lambda x: x["virality_score"], reverse=True)


def extract_all_hashtags(yt_videos: list[dict], tt_videos: list[dict]) -> list[dict]:
    """Merge hashtags from both platforms and rank by frequency + virality."""
    counter: Counter = Counter()
    sources: dict[str, dict] = {}

    for v in yt_videos:
        score = virality_score(v)
        for ht in v.get("hashtags", []):
            ht = ht.lower().lstrip("#")
            counter[ht] += 1
            if ht not in sources:
                sources[ht] = {"youtube": 0, "tiktok": 0, "total_score": 0.0}
            sources[ht]["youtube"] += 1
            sources[ht]["total_score"] += score

    for v in tt_videos:
        score = virality_score(v)
        for ht in v.get("hashtags", []):
            ht = ht.lower().lstrip("#")
            counter[ht] += 1
            if ht not in sources:
                sources[ht] = {"youtube": 0, "tiktok": 0, "total_score": 0.0}
            sources[ht]["tiktok"] += 1
            sources[ht]["total_score"] += score

    results = []
    for ht, count in counter.most_common():
        src = sources.get(ht, {})
        crossover = src.get("youtube", 0) > 0 and src.get("tiktok", 0) > 0
        results.append({
            "hashtag": f"#{ht}",
            "total_mentions": count,
            "youtube_mentions": src.get("youtube", 0),
            "tiktok_mentions": src.get("tiktok", 0),
            "crossover": crossover,
            "combined_virality": round(src.get("total_score", 0.0), 1),
        })
    return results


def find_crossover_trends(
    yt_items: list[dict], tt_items: list[dict]
) -> list[dict]:
    """Find hashtags/trends that appear on BOTH YouTube and TikTok."""
    def normalize(s: str) -> str:
        return re.sub(r"[^a-z0-9]", "", s.lower())

    yt_tags = {normalize(ht) for v in yt_items for ht in v.get("hashtags", [])}
    tt_tags = {normalize(ht) for v in tt_items for ht in v.get("hashtags", [])}

    shared = yt_tags & tt_tags
    results = []
    for tag in sorted(shared):
        yt_views = sum(
            _safe_int(v.get("views", 0))
            for v in yt_items
            if tag in [normalize(h) for h in v.get("hashtags", [])]
        )
        tt_plays = sum(
            _safe_int(v.get("plays", 0))
            for v in tt_items
            if tag in [normalize(h) for h in v.get("hashtags", [])]
        )
        results.append({
            "hashtag": f"#{tag}",
            "platforms": ["youtube", "tiktok"],
            "youtube_total_views": yt_views,
            "tiktok_total_plays": tt_plays,
            "crossover": True,
        })
    return sorted(results, key=lambda x: x["youtube_total_views"] + x["tiktok_total_plays"], reverse=True)


def generate_content_calendar(trends: list[dict], days: int = 7) -> list[dict]:
    """Create a posting schedule using the top trends for the next N days."""
    top = rank_trends(trends)[:days * 2]
    calendar = []
    # Optimal posting times per platform (based on industry research)
    times = {
        "tiktok": ["7:00 AM", "12:00 PM", "7:00 PM", "10:00 PM"],
        "youtube": ["2:00 PM", "4:00 PM", "8:00 PM"],
        "instagram": ["6:00 AM", "12:00 PM", "5:00 PM", "9:00 PM"],
    }
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for i in range(days):
        day_trends = top[i * 2: i * 2 + 2] if i * 2 + 1 < len(top) else top[-2:]
        calendar.append({
            "day": day_names[i % 7],
            "day_number": i + 1,
            "recommended_hashtags": [t["hashtag"] for t in day_trends if "hashtag" in t][:5],
            "posting_windows": {
                "tiktok": times["tiktok"],
                "youtube": times["youtube"],
                "instagram": times["instagram"],
            },
            "content_angle": _suggest_angle(day_trends),
        })
    return calendar


def _suggest_angle(trends: list[dict]) -> str:
    """Suggest a content angle based on current trends."""
    titles = " ".join(t.get("title", t.get("hashtag", "")) for t in trends).lower()
    if any(w in titles for w in ["challenge", "trend", "viral"]):
        return "Participate in or react to the trending challenge"
    if any(w in titles for w in ["music", "song", "sound", "audio"]):
        return "Create content using the trending sound/music"
    if any(w in titles for w in ["tutorial", "how", "tips", "learn"]):
        return "Educational/tutorial content aligned with trending topics"
    if any(w in titles for w in ["funny", "lol", "meme", "comedy"]):
        return "Comedy/reaction content riding the viral wave"
    return "Create original content incorporating these trending hashtags"
