"""Cross-platform trend analysis and aggregation.

Combines YouTube and TikTok data to surface:
  - Top trending hashtags across both platforms
  - Music/sounds crossing from TikTok to YouTube
  - Shared topics and content opportunities
  - Posting-time recommendations
"""

from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any


def aggregate_hashtags(
    yt_videos: list[dict],
    tt_hashtags: list[dict],
    tt_videos: list[dict],
) -> list[dict[str, Any]]:
    """Merge hashtag data from YouTube and TikTok into a unified ranked list."""
    counts: dict[str, dict[str, Any]] = {}

    for v in yt_videos:
        for tag in v.get("hashtags", []):
            t = tag.lower().lstrip("#")
            key = f"#{t}"
            if key not in counts:
                counts[key] = {"hashtag": key, "youtube_count": 0, "tiktok_count": 0, "tiktok_views": 0}
            counts[key]["youtube_count"] += 1

    for item in tt_hashtags:
        tag = item.get("hashtag", "").lower()
        if tag not in counts:
            counts[tag] = {"hashtag": tag, "youtube_count": 0, "tiktok_count": 0, "tiktok_views": 0}
        counts[tag]["tiktok_count"] = item.get("posts", 0)
        counts[tag]["tiktok_views"] = item.get("views", 0)

    for v in tt_videos:
        for tag in v.get("hashtags", []):
            t = tag.lower()
            if t not in counts:
                counts[t] = {"hashtag": t, "youtube_count": 0, "tiktok_count": 0, "tiktok_views": 0}
            counts[t]["tiktok_count"] += 1

    results = list(counts.values())
    for r in results:
        yt_score = r["youtube_count"] * 10
        tt_score = min(r["tiktok_count"] / 1000, 100) if r["tiktok_count"] > 1000 else r["tiktok_count"] * 0.1
        tt_view_score = min(r["tiktok_views"] / 1_000_000, 50) if r["tiktok_views"] > 0 else 0
        r["cross_platform"] = r["youtube_count"] > 0 and (r["tiktok_count"] > 0 or r["tiktok_views"] > 0)
        r["score"] = yt_score + tt_score + tt_view_score

    return sorted(results, key=lambda x: -x["score"])


def find_crossover_music(
    yt_videos: list[dict],
    tt_music: list[dict],
) -> list[dict[str, Any]]:
    """Find music trending on TikTok that also appears in YouTube content."""
    yt_titles = " ".join(v.get("title", "").lower() for v in yt_videos)

    crossover = []
    for track in tt_music:
        title = track.get("title", "").lower()
        artist = track.get("artist", "").lower()
        found_in_yt = title in yt_titles or artist in yt_titles
        crossover.append({
            **track,
            "crossover": found_in_yt,
            "opportunity": "Use this sound — it's viral on TikTok" + (" AND trending on YouTube" if found_in_yt else ""),
        })

    return sorted(crossover, key=lambda x: (-int(x["crossover"]), -x.get("uses", 0)))


def top_content_opportunities(
    yt_videos: list[dict],
    tt_hashtags: list[dict],
    tt_videos: list[dict],
) -> list[dict[str, Any]]:
    """Identify high-opportunity content topics with posting angle recommendations."""
    topic_counter: Counter = Counter()

    for v in yt_videos:
        words = re.findall(r"\b[A-Za-z]{5,}\b", v.get("title", ""))
        topic_counter.update(w.lower() for w in words)

    for v in tt_videos:
        words = re.findall(r"\b[A-Za-z]{5,}\b", v.get("caption", ""))
        topic_counter.update(w.lower() for w in words)

    stop = {
        "about", "after", "again", "being", "could", "every", "first", "going",
        "great", "great", "have", "their", "there", "these", "thing", "think",
        "those", "video", "watch", "where", "which", "would", "youre", "yours",
    }

    opportunities = []
    for topic, count in topic_counter.most_common(15):
        if topic in stop or len(topic) < 5:
            continue
        opportunities.append({
            "topic": topic,
            "mention_count": count,
            "angle_youtube": f"Long-form breakdown: 'Everything about #{topic} explained'",
            "angle_tiktok": f"Quick hook: 'POV you finally understand #{topic}' or trending sound + #{topic}",
            "angle_instagram": f"Carousel: '5 things you need to know about #{topic}'",
        })
    return opportunities[:10]


def best_posting_times() -> dict[str, list[dict[str, str]]]:
    """Return evidence-based best posting times (UTC) per platform."""
    return {
        "tiktok": [
            {"day": "Tuesday", "time": "09:00 UTC", "note": "Morning commute spike"},
            {"day": "Thursday", "time": "19:00 UTC", "note": "Pre-weekend discovery peak"},
            {"day": "Friday", "time": "05:00 UTC", "note": "US East Coast morning"},
            {"day": "Saturday", "time": "11:00 UTC", "note": "Weekend scroll session"},
            {"day": "Sunday", "time": "07:00 UTC", "note": "Highest overall engagement"},
        ],
        "youtube": [
            {"day": "Wednesday", "time": "14:00 UTC", "note": "US afternoon — feeds index by 4pm"},
            {"day": "Thursday", "time": "15:00 UTC", "note": "Top US engagement window"},
            {"day": "Friday", "time": "12:00 UTC", "note": "Pre-weekend traffic surge"},
            {"day": "Saturday", "time": "09:00 UTC", "note": "Weekend morning binge"},
        ],
        "instagram": [
            {"day": "Monday", "time": "11:00 UTC", "note": "Post-weekend engagement rebound"},
            {"day": "Wednesday", "time": "11:00 UTC", "note": "Mid-week high"},
            {"day": "Friday", "time": "10:00 UTC", "note": "Shares peak on Fridays"},
        ],
    }


def generate_summary(
    yt_videos: list[dict],
    tt_data: dict,
    region: str,
) -> dict[str, Any]:
    """Generate a full cross-platform trend summary."""
    tt_hashtags = tt_data.get("hashtags", [])
    tt_music = tt_data.get("music", [])
    tt_videos = tt_data.get("videos", [])

    agg_hashtags = aggregate_hashtags(yt_videos, tt_hashtags, tt_videos)
    crossover_music = find_crossover_music(yt_videos, tt_music)
    opportunities = top_content_opportunities(yt_videos, tt_hashtags, tt_videos)
    times = best_posting_times()

    return {
        "region": region,
        "youtube_videos_analyzed": len(yt_videos),
        "tiktok_hashtags_analyzed": len(tt_hashtags),
        "tiktok_videos_analyzed": len(tt_videos),
        "top_hashtags": agg_hashtags[:20],
        "cross_platform_hashtags": [h for h in agg_hashtags if h.get("cross_platform")][:10],
        "trending_music": crossover_music[:10],
        "content_opportunities": opportunities,
        "best_posting_times": times,
        "top_youtube_videos": sorted(yt_videos, key=lambda v: -v.get("views", 0))[:5],
        "top_tiktok_sounds": tt_music[:5],
    }
