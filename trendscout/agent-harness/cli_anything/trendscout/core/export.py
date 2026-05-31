"""Export trend data to JSON, CSV, and Markdown reports."""

import csv
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


def export_json(data: Any, path: str) -> str:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    return path


def export_csv(videos: List[Dict[str, Any]], path: str) -> str:
    if not videos:
        raise ValueError("No videos to export.")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    fields = ["id", "title", "description", "channel", "username", "view_count",
              "like_count", "comment_count", "share_count", "hashtags", "url",
              "source", "_platform"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for v in videos:
            row = dict(v)
            row["hashtags"] = ",".join(v.get("hashtags") or v.get("tags") or [])
            writer.writerow(row)
    return path


def export_hashtags_csv(hashtags: List[Dict[str, Any]], path: str) -> str:
    if not hashtags:
        raise ValueError("No hashtags to export.")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    fields = list(hashtags[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(hashtags)
    return path


def generate_report(aggregated: Dict[str, Any]) -> str:
    """Render a Markdown trend report from aggregated data."""
    ts = aggregated.get("generated_at", datetime.now().isoformat())
    platforms = ", ".join(aggregated.get("platforms", ["unknown"]))
    total = aggregated.get("total_videos_analyzed", 0)

    lines = [
        f"# TrendScout Report",
        f"",
        f"**Generated:** {ts}",
        f"**Platforms:** {platforms}",
        f"**Videos Analyzed:** {total}",
        f"",
        f"---",
        f"",
        f"## Top Hashtags",
        f"",
    ]

    for i, entry in enumerate(aggregated.get("top_hashtags", [])[:20], 1):
        tag = entry.get("hashtag", "")
        score = entry.get("score", "")
        lines.append(f"{i:2}. `{tag}` — score: {score}")

    lines += ["", "---", "", "## Cross-Platform Trends", ""]
    cross = aggregated.get("crossplatform_trends", [])
    if cross:
        for entry in cross[:10]:
            tag = entry.get("hashtag", "")
            plats = ", ".join(entry.get("platforms", []))
            lines.append(f"- `{tag}` — on {plats}")
    else:
        lines.append("_No cross-platform overlaps detected._")

    lines += ["", "---", "", "## Platform Summary", ""]
    for platform, summary in aggregated.get("platform_summary", {}).items():
        lines.append(f"### {platform.capitalize()}")
        lines.append(f"- Videos: {summary.get('video_count', 0)}")
        lines.append(f"- Top video: {summary.get('top_video', '')[:80]}")
        lines.append(f"- Fetch method: {summary.get('fetch_method', '')}")
        lines.append("")

    return "\n".join(lines)
