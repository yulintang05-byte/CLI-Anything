"""Output formatting utilities for tables, JSON, and rich terminal output."""

import json
import csv
import io
from typing import Any


def print_json(data: Any):
    print(json.dumps(data, indent=2, default=str))


def print_table(rows: list[list], headers: list[str] | None = None):
    try:
        from tabulate import tabulate
        print(tabulate(rows, headers=headers or "firstrow", tablefmt="rounded_outline"))
    except ImportError:
        if headers:
            print("\t".join(headers))
        for row in rows:
            print("\t".join(str(c) for c in row))


def to_csv_string(rows: list[list]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerows(rows)
    return buf.getvalue()


def format_viral_score(score: float) -> str:
    if score >= 80:
        return f"🔥 {score}"
    if score >= 60:
        return f"📈 {score}"
    if score >= 40:
        return f"📊 {score}"
    return f"📉 {score}"


def format_number(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def format_hashtag_table(hashtags: list[dict]) -> list[list]:
    rows = [["Rank", "Hashtag", "Frequency", "Cross-Platform", "Recommendation"]]
    for i, h in enumerate(hashtags, 1):
        rows.append([
            i,
            h.get("hashtag", ""),
            h.get("frequency", h.get("combined_score", "—")),
            "✅" if h.get("cross_platform") else "—",
            h.get("recommendation", ""),
        ])
    return rows


def format_video_table(videos: list[dict]) -> list[list]:
    rows = [["Rank", "Title", "Channel", "Views", "Engagement", "Viral Score", "Velocity"]]
    for i, v in enumerate(videos, 1):
        rows.append([
            i,
            v.get("title", "")[:45] + ("…" if len(v.get("title", "")) > 45 else ""),
            v.get("channel", "")[:20],
            format_number(v.get("views", 0)),
            f"{v.get('engagement_pct', 0):.1f}%",
            format_viral_score(v.get("viral_score", 0)),
            v.get("velocity", "—"),
        ])
    return rows
