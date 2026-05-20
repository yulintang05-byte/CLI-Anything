"""Unified trend aggregator — cross-platform analysis, scoring, and reporting."""
from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any
from collections import Counter, defaultdict

from cli_anything.trendscraper.core import youtube as yt
from cli_anything.trendscraper.core import tiktok as tt


def fetch_all_trends(region: str = "US", max_results: int = 50) -> dict[str, Any]:
    """Fetch trends from both YouTube and TikTok, then merge and score them."""
    yt_data = yt.fetch_trending_videos(region=region, max_results=max_results)
    tt_data = tt.fetch_trending_hashtags(region=region, limit=max_results)

    merged_hashtags = _merge_hashtags(yt_data, tt_data)
    cross_platform = _find_cross_platform_trends(yt_data, tt_data)
    music = _merge_music(yt_data, tt_data)

    return {
        "fetched_at": datetime.utcnow().isoformat(),
        "region": region,
        "sources": {
            "youtube": yt_data.get("source"),
            "tiktok": tt_data.get("source"),
        },
        "trending_hashtags": merged_hashtags,
        "cross_platform_trends": cross_platform,
        "trending_music": music,
        "youtube_summary": {
            "video_count": yt_data.get("video_count", 0),
            "top_hashtags": yt_data.get("trending_hashtags", [])[:10],
        },
        "tiktok_summary": {
            "video_count": tt_data.get("video_count", 0),
            "top_hashtags": tt_data.get("trending_hashtags", [])[:10],
            "top_sounds": tt_data.get("trending_sounds", [])[:10],
        },
    }


def _merge_hashtags(yt_data: dict, tt_data: dict) -> list[dict]:
    """Merge and score hashtags from both platforms."""
    scores: dict[str, dict] = defaultdict(lambda: {"tag": "", "yt_count": 0, "tt_count": 0, "total": 0, "score": 0.0, "platforms": []})

    for h in yt_data.get("trending_hashtags", []):
        tag = h["tag"].lower().strip("#")
        scores[tag]["tag"] = tag
        scores[tag]["yt_count"] = h["count"]
        scores[tag]["platforms"].append("youtube")

    for h in tt_data.get("trending_hashtags", []):
        tag = h["tag"].lower().strip("#")
        scores[tag]["tag"] = tag
        scores[tag]["tt_count"] = h["count"]
        if "tiktok" not in scores[tag]["platforms"]:
            scores[tag]["platforms"].append("tiktok")

    for tag, s in scores.items():
        s["total"] = s["yt_count"] + s["tt_count"]
        # Cross-platform bonus: 2x multiplier
        cross_bonus = 2.0 if len(s["platforms"]) > 1 else 1.0
        s["score"] = round((s["total"] + 1) * cross_bonus * math.log(s["total"] + 2), 2)

    ranked = sorted(scores.values(), key=lambda x: x["score"], reverse=True)
    return ranked[:50]


def _find_cross_platform_trends(yt_data: dict, tt_data: dict) -> list[dict]:
    """Identify hashtags trending on BOTH platforms simultaneously."""
    yt_tags = {h["tag"].lower().strip("#") for h in yt_data.get("trending_hashtags", [])}
    tt_tags = {h["tag"].lower().strip("#") for h in tt_data.get("trending_hashtags", [])}
    shared = yt_tags & tt_tags

    yt_lookup = {h["tag"].lower().strip("#"): h["count"] for h in yt_data.get("trending_hashtags", [])}
    tt_lookup = {h["tag"].lower().strip("#"): h["count"] for h in tt_data.get("trending_hashtags", [])}

    result = []
    for tag in shared:
        result.append({
            "tag": tag,
            "youtube_count": yt_lookup.get(tag, 0),
            "tiktok_count": tt_lookup.get(tag, 0),
            "virality": "HIGH",
        })

    return sorted(result, key=lambda x: x["youtube_count"] + x["tiktok_count"], reverse=True)


def _merge_music(yt_data: dict, tt_data: dict) -> list[dict]:
    """Merge music trends from YouTube and TikTok."""
    music: dict[str, dict] = defaultdict(lambda: {"title": "", "yt_count": 0, "tt_count": 0, "platforms": []})

    for m in yt_data.get("trending_music", []):
        t = _normalize_title(m["title"])
        music[t]["title"] = m["title"]
        music[t]["yt_count"] = m["count"]
        music[t]["platforms"].append("youtube")

    for s in tt_data.get("trending_sounds", []):
        t = _normalize_title(s["title"])
        music[t]["title"] = s["title"]
        music[t]["tt_count"] = s["count"]
        if "tiktok" not in music[t]["platforms"]:
            music[t]["platforms"].append("tiktok")

    ranked = sorted(music.values(), key=lambda x: x["yt_count"] + x["tt_count"], reverse=True)
    return ranked[:30]


def _normalize_title(title: str) -> str:
    import re
    return re.sub(r"[^\w\s]", "", (title or "").lower().strip())


def generate_trend_report(
    region: str = "US",
    output_file: str | None = None,
    max_results: int = 50,
) -> dict[str, Any]:
    """Generate a full trend report and optionally save it as JSON."""
    all_trends = fetch_all_trends(region=region, max_results=max_results)

    report = {
        "report_title": f"Viral Trend Report — {region} — {datetime.utcnow().strftime('%Y-%m-%d')}",
        "generated_at": datetime.utcnow().isoformat(),
        "region": region,
        "executive_summary": _executive_summary(all_trends),
        "trends": all_trends,
        "recommended_hashtags": _top_hashtags_for_posting(all_trends),
        "recommended_music": all_trends.get("trending_music", [])[:10],
        "action_items": _generate_action_items(all_trends),
    }

    if output_file:
        Path(output_file).write_text(json.dumps(report, indent=2))

    return report


def _executive_summary(trends: dict) -> dict:
    hashtags = trends.get("trending_hashtags", [])
    cross = trends.get("cross_platform_trends", [])
    music = trends.get("trending_music", [])
    return {
        "total_trending_hashtags": len(hashtags),
        "cross_platform_trending": len(cross),
        "top_3_hashtags": [h["tag"] for h in hashtags[:3]],
        "top_3_cross_platform": [h["tag"] for h in cross[:3]],
        "top_music": music[0]["title"] if music else "N/A",
    }


def _top_hashtags_for_posting(trends: dict) -> list[str]:
    """Return 15 best hashtags to use in a post right now."""
    cross = [f"#{h['tag']}" for h in trends.get("cross_platform_trends", [])[:5]]
    top = [f"#{h['tag']}" for h in trends.get("trending_hashtags", [])[:10]]
    combined = list(dict.fromkeys(cross + top))
    return combined[:15]


def _generate_action_items(trends: dict) -> list[str]:
    items = []
    cross = trends.get("cross_platform_trends", [])
    if cross:
        tags = ", ".join(f"#{h['tag']}" for h in cross[:3])
        items.append(f"Post content using cross-platform trending tags: {tags}")

    music = trends.get("trending_music", [])
    if music:
        items.append(f"Use trending sound '{music[0]['title']}' in your next TikTok/Reel")

    top_yt = (trends.get("youtube_summary", {}).get("top_hashtags") or [{}])[:1]
    if top_yt and top_yt[0].get("tag"):
        items.append(f"Create YouTube content around #{top_yt[0]['tag']} — currently viral")

    top_tt = (trends.get("tiktok_summary", {}).get("top_hashtags") or [{}])[:1]
    if top_tt and top_tt[0].get("tag"):
        items.append(f"Use #{top_tt[0]['tag']} TikTok hashtag — high engagement right now")

    items.append("Post within 2 hours of identifying a cross-platform trend for max reach")
    items.append("Batch-create 3-5 pieces of content around each top trend before it peaks")
    return items


def save_trends_csv(trends: dict, output_file: str) -> None:
    """Export trending hashtags to CSV for spreadsheet analysis."""
    import csv
    hashtags = trends.get("trending_hashtags", [])
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["tag", "yt_count", "tt_count", "total", "score", "platforms"])
        writer.writeheader()
        for h in hashtags:
            row = {
                "tag": h.get("tag", ""),
                "yt_count": h.get("yt_count", 0),
                "tt_count": h.get("tt_count", 0),
                "total": h.get("total", 0),
                "score": h.get("score", 0),
                "platforms": ",".join(h.get("platforms", [])),
            }
            writer.writerow(row)
