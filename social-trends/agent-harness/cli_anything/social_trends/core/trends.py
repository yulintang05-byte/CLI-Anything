"""Trend analysis — aggregate scraped data into actionable trend reports."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any


def analyze_trends(videos: list[dict]) -> dict:
    """Produce a comprehensive trend report from scraped videos.

    Returns:
        {
          top_hashtags, trending_sounds, content_patterns,
          best_posting_categories, viral_score_threshold,
          platform_breakdown, engagement_stats
        }
    """
    if not videos:
        return {"error": "No videos to analyze", "top_hashtags": [], "trending_sounds": []}

    yt_vids = [v for v in videos if v.get("platform") == "youtube"]
    tt_vids = [v for v in videos if v.get("platform") == "tiktok"]

    top_hashtags = _rank_hashtags(videos)
    trending_sounds = _rank_sounds(tt_vids)
    content_patterns = _extract_content_patterns(videos)
    engagement_stats = _compute_engagement_stats(videos)
    viral_threshold = _compute_viral_threshold(videos)

    return {
        "platform_breakdown": {
            "youtube": len(yt_vids),
            "tiktok": len(tt_vids),
            "total": len(videos),
        },
        "top_hashtags": top_hashtags[:30],
        "trending_sounds": trending_sounds[:20],
        "content_patterns": content_patterns,
        "engagement_stats": engagement_stats,
        "viral_score_threshold": viral_threshold,
        "best_categories": _top_categories(videos),
        "recommendations": _generate_recommendations(videos, top_hashtags, trending_sounds),
    }


def _rank_hashtags(videos: list[dict]) -> list[dict]:
    counts: dict[str, dict] = {}
    for v in videos:
        views = v.get("views", 0)
        for tag in v.get("hashtags", []):
            tag = tag.lower().strip()
            if len(tag) < 2 or tag == "#":
                continue
            if tag not in counts:
                counts[tag] = {
                    "hashtag": tag,
                    "appearances": 0,
                    "total_views": 0,
                    "platforms": set(),
                }
            counts[tag]["appearances"] += 1
            counts[tag]["total_views"] += views
            counts[tag]["platforms"].add(v.get("platform", "unknown"))

    ranked = sorted(counts.values(), key=lambda x: x["total_views"], reverse=True)
    for r in ranked:
        r["platforms"] = list(r["platforms"])
    return ranked


def _rank_sounds(tiktok_videos: list[dict]) -> list[dict]:
    sound_map: dict[str, dict] = {}
    for v in tiktok_videos:
        music = v.get("music_used")
        if not music or not music.get("title"):
            continue
        key = f"{music['title']}||{music.get('artist','')}"
        if key not in sound_map:
            sound_map[key] = {
                "title": music["title"],
                "artist": music.get("artist", "Unknown"),
                "id": music.get("id", ""),
                "video_count": 0,
                "total_views": 0,
                "count": 0,
            }
        sound_map[key]["video_count"] += 1
        sound_map[key]["count"] += 1
        sound_map[key]["total_views"] += v.get("views", 0)

    return sorted(sound_map.values(), key=lambda x: x["video_count"], reverse=True)


def _extract_content_patterns(videos: list[dict]) -> dict:
    """Identify common title patterns, keywords, and content formats."""
    titles = [v.get("title", "") for v in videos]
    all_words: list[str] = []
    for t in titles:
        words = re.findall(r"\b\w{4,}\b", t.lower())
        all_words.extend(words)

    stop = {"this", "that", "with", "from", "have", "what", "your", "they",
            "when", "will", "were", "been", "their", "more", "about", "just",
            "into", "than", "then", "some", "like", "over", "also", "only"}
    filtered = [w for w in all_words if w not in stop]
    top_words = Counter(filtered).most_common(20)

    # Detect title patterns (lists, questions, how-tos)
    list_count = sum(1 for t in titles if re.search(r"\d+\s+(best|ways|tips|things|reasons)", t, re.I))
    question_count = sum(1 for t in titles if t.strip().endswith("?"))
    howto_count = sum(1 for t in titles if re.search(r"\bhow\s+to\b", t, re.I))
    reaction_count = sum(1 for t in titles if re.search(r"\b(reaction|reacting|responds)\b", t, re.I))

    total = len(titles) or 1
    return {
        "top_keywords": [{"word": w, "count": c} for w, c in top_words],
        "title_formats": {
            "list_videos_pct": round(list_count / total * 100, 1),
            "question_videos_pct": round(question_count / total * 100, 1),
            "howto_videos_pct": round(howto_count / total * 100, 1),
            "reaction_videos_pct": round(reaction_count / total * 100, 1),
        },
        "avg_title_length": round(sum(len(t) for t in titles) / total, 1),
    }


def _compute_engagement_stats(videos: list[dict]) -> dict:
    if not videos:
        return {}
    views = [v.get("views", 0) for v in videos]
    likes = [v.get("likes", 0) for v in videos]
    n = len(videos)
    avg_views = sum(views) / n
    avg_likes = sum(likes) / n
    engagement_rates = []
    for v in videos:
        vv = v.get("views", 0)
        if vv > 0:
            engagement_rates.append((v.get("likes", 0) + v.get("comments", 0)) / vv * 100)
    avg_er = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0

    return {
        "avg_views": round(avg_views),
        "avg_likes": round(avg_likes),
        "max_views": max(views),
        "min_views": min(views),
        "avg_engagement_rate_pct": round(avg_er, 2),
        "total_videos_analyzed": n,
    }


def _compute_viral_threshold(videos: list[dict]) -> int:
    views = sorted([v.get("views", 0) for v in videos], reverse=True)
    if not views:
        return 100000
    top_20_pct_idx = max(1, len(views) // 5)
    return views[top_20_pct_idx]


def _top_categories(videos: list[dict]) -> list[dict]:
    cat_views: dict[str, int] = {}
    for v in videos:
        for cat in v.get("categories", []):
            cat_views[cat] = cat_views.get(cat, 0) + v.get("views", 0)
    ranked = sorted(cat_views.items(), key=lambda x: x[1], reverse=True)
    return [{"category": k, "total_views": v} for k, v in ranked[:10]]


def _generate_recommendations(
    videos: list[dict],
    hashtags: list[dict],
    sounds: list[dict],
) -> list[str]:
    recs = []
    if hashtags:
        top3 = [h["hashtag"] for h in hashtags[:3]]
        recs.append(f"Use these top hashtags in your next posts: {', '.join(top3)}")
    if sounds:
        top_sound = sounds[0]
        recs.append(
            f"Trending sound: '{top_sound['title']}' by {top_sound['artist']} "
            f"(used in {top_sound['video_count']} trending videos)"
        )
    yt_vids = [v for v in videos if v.get("platform") == "youtube"]
    tt_vids = [v for v in videos if v.get("platform") == "tiktok"]
    if tt_vids:
        avg_tt = sum(v.get("views", 0) for v in tt_vids) / len(tt_vids)
        recs.append(f"TikTok average trending views: {avg_tt:,.0f} — aim to exceed this benchmark")
    if yt_vids:
        avg_yt = sum(v.get("views", 0) for v in yt_vids) / len(yt_vids)
        recs.append(f"YouTube average trending views: {avg_yt:,.0f} — target this for viral potential")
    recs.append("Post within 48h of a trend appearing — early movers get 3-5x more reach")
    recs.append("Hook viewers in the first 2 seconds — trending videos average <3s hooks")
    return recs
