"""Hashtag analysis and optimization engine.

Combines YouTube and TikTok data to produce optimized hashtag sets with
competition tiers, engagement scores, and per-niche recommendations.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

CACHE_DIR = Path.home() / ".config" / "viral-trends" / "cache"

# Competition brackets based on TikTok views
COMPETITION_TIERS = {
    "mega":   (10_000_000_000, float("inf")),   # 10B+ views
    "high":   (1_000_000_000,  10_000_000_000), # 1B–10B
    "medium": (100_000_000,    1_000_000_000),  # 100M–1B
    "low":    (10_000_000,     100_000_000),    # 10M–100M
    "niche":  (0,              10_000_000),     # <10M
}

# Ideal hashtag mix for a single post (30-tag limit)
OPTIMAL_MIX = {
    "mega":   5,
    "high":   8,
    "medium": 10,
    "low":    5,
    "niche":  2,
}


def _tier(views: int) -> str:
    for name, (lo, hi) in COMPETITION_TIERS.items():
        if lo <= views < hi:
            return name
    return "niche"


def score_hashtag(entry: dict) -> float:
    """Score a hashtag 0–100 based on views, frequency, and tier balance."""
    views = entry.get("views", 0) or entry.get("total_views", 0)
    freq  = entry.get("frequency", 1)
    tier  = _tier(views)

    # Reward medium competition most — best reach/competition balance
    tier_weights = {"mega": 0.4, "high": 0.7, "medium": 1.0, "low": 0.8, "niche": 0.6}
    base = min(views / 1_000_000_000, 1.0) * 50   # up to 50 pts from views
    freq_bonus = min(freq * 5, 20)                  # up to 20 pts from frequency
    tier_bonus = tier_weights.get(tier, 0.5) * 30  # up to 30 pts from tier
    return round(base + freq_bonus + tier_bonus, 2)


def analyze_hashtags(
    yt_hashtags: list[dict],
    tt_hashtags: list[dict],
) -> list[dict]:
    """Merge and rank hashtags from both platforms.

    Each output entry has keys:
        hashtag, yt_frequency, tt_views, combined_score, tier, platforms
    """
    merged: dict[str, dict] = {}

    for entry in yt_hashtags:
        tag = entry.get("hashtag", "").lower().strip("#")
        if not tag:
            continue
        merged.setdefault(tag, {
            "hashtag": tag,
            "yt_frequency": 0,
            "yt_total_views": 0,
            "tt_views": 0,
            "frequency": 0,
            "platforms": [],
        })
        merged[tag]["yt_frequency"] += entry.get("frequency", 1)
        merged[tag]["yt_total_views"] += entry.get("total_views", 0)
        merged[tag]["frequency"] += entry.get("frequency", 1)
        if "youtube" not in merged[tag]["platforms"]:
            merged[tag]["platforms"].append("youtube")

    for entry in tt_hashtags:
        tag = entry.get("hashtag", "").lower().strip("#")
        if not tag:
            continue
        merged.setdefault(tag, {
            "hashtag": tag,
            "yt_frequency": 0,
            "yt_total_views": 0,
            "tt_views": 0,
            "frequency": 0,
            "platforms": [],
        })
        merged[tag]["tt_views"] += entry.get("views", 0)
        merged[tag]["frequency"] += 1
        if "tiktok" not in merged[tag]["platforms"]:
            merged[tag]["platforms"].append("tiktok")

    result = []
    for tag, data in merged.items():
        views = max(data["tt_views"], data["yt_total_views"])
        score = score_hashtag({**data, "views": views})
        result.append({
            **data,
            "combined_score": score,
            "tier": _tier(views),
            "views": views,
        })

    return sorted(result, key=lambda x: x["combined_score"], reverse=True)


def build_optimal_set(
    ranked: list[dict],
    niche: str = "",
    max_tags: int = 30,
) -> dict[str, list[str]]:
    """Build a posting-ready hashtag set balanced across competition tiers.

    Returns dict with keys: optimal_set (flat list), by_tier (dict), caption_block
    """
    by_tier: dict[str, list[str]] = {t: [] for t in COMPETITION_TIERS}

    for entry in ranked:
        tag = entry["hashtag"]
        tier = entry.get("tier", "niche")
        if niche and niche.lower() not in tag.lower():
            if len(by_tier[tier]) >= OPTIMAL_MIX.get(tier, 3) * 2:
                continue
        by_tier[tier].append(tag)

    # Fill optimal set with the mix
    optimal: list[str] = []
    for tier, target_count in OPTIMAL_MIX.items():
        pool = by_tier[tier]
        optimal.extend(pool[:target_count])

    optimal = optimal[:max_tags]

    caption_block = " ".join(f"#{t}" for t in optimal)

    return {
        "optimal_set":   optimal,
        "by_tier":       {k: v[:10] for k, v in by_tier.items()},
        "caption_block": caption_block,
        "tag_count":     len(optimal),
    }


def extract_niche_hashtags(text: str) -> list[str]:
    """Extract hashtags from any text body."""
    return list(dict.fromkeys(re.findall(r"#(\w+)", text.lower())))


def filter_by_niche(hashtags: list[dict], niche: str) -> list[dict]:
    """Filter hashtag list to entries relevant to a niche keyword."""
    niche_lower = niche.lower()
    return [
        h for h in hashtags
        if niche_lower in h.get("hashtag", "").lower()
        or niche_lower in h.get("category", "").lower()
    ]
