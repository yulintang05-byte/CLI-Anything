#!/usr/bin/env python3
"""Output formatters for social-trends CLI."""

import json
from typing import Any


def fmt_number(n: int) -> str:
    """Format large numbers with K/M suffixes."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def fmt_duration(seconds: int) -> str:
    """Format seconds into mm:ss or h:mm:ss."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def print_json(data: Any):
    print(json.dumps(data, indent=2, default=str, ensure_ascii=False))


def print_table(rows: list[dict], columns: list[str], widths: dict[str, int] | None = None):
    """Print a simple ASCII table."""
    if not rows:
        print("  (no results)")
        return
    if widths is None:
        widths = {}
    col_widths = {}
    for col in columns:
        w = widths.get(col, len(col))
        for row in rows:
            val = str(row.get(col, ""))
            w = max(w, len(val))
        col_widths[col] = min(w, 60)

    header = "  ".join(col.ljust(col_widths[col]) for col in columns)
    sep = "  ".join("-" * col_widths[col] for col in columns)
    print(header)
    print(sep)
    for row in rows:
        line = "  ".join(str(row.get(col, "")).ljust(col_widths[col])[:col_widths[col]] for col in columns)
        print(line)


def print_section(title: str, char: str = "="):
    width = max(len(title) + 4, 50)
    print()
    print(char * width)
    print(f"  {title}")
    print(char * width)


def print_bullet(items: list[str], prefix: str = "  •"):
    for item in items:
        print(f"{prefix} {item}")


def print_score_bar(label: str, score: float, max_score: float = 100.0, width: int = 30):
    filled = int((score / max_score) * width)
    bar = "█" * filled + "░" * (width - filled)
    print(f"  {label:<20} [{bar}] {score:.0f}/{max_score:.0f}")
