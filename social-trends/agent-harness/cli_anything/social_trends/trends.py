"""Cross-platform trend analysis and scoring engine."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any


# ── Cross-platform trend aggregation ──────────────────────────────────

def merge_hashtags(
    youtube_tags: list[dict[str, Any]],
    tiktok_tags: list[dict[str, Any]],
    top_n: int = 30,
) -> list[dict[str, Any]]:
    """Merge and re-score hashtags from YouTube + TikTok.

    Cross-platform presence is a strong virality signal — tags that appear
    on both platforms get a 1.5x boost.

    Returns list of dicts: tag, score, frequency, avg_views, platforms, recommendation.
    """
    combined: dict[str, dict[str, Any]] = {}

    for tag_list, platform in [(youtube_tags, "youtube"), (tiktok_tags, "tiktok")]:
        for t in tag_list:
            tag = t["tag"].lower().strip()
            if tag not in combined:
                combined[tag] = {
                    "tag": tag,
                    "score": 0.0,
                    "frequency": 0,
                    "avg_views": 0,
                    "platforms": [],
                }
            combined[tag]["score"] += t.get("score", 0)
            combined[tag]["frequency"] += t.get("frequency", 0)
            combined[tag]["avg_views"] = max(
                combined[tag]["avg_views"], t.get("avg_views", 0)
            )
            if platform not in combined[tag]["platforms"]:
                combined[tag]["platforms"].append(platform)

    # Cross-platform boost
    results = []
    for tag, data in combined.items():
        score = data["score"]
        if len(data["platforms"]) > 1:
            score *= 1.5  # cross-platform virality bonus
        rec = _hashtag_recommendation(tag, data["avg_views"], data["frequency"], data["platforms"])
        results.append({**data, "score": round(score, 2), "recommendation": rec})

    return sorted(results, key=lambda x: x["score"], reverse=True)[:top_n]


def merge_trends(
    youtube_trends: list[dict[str, Any]],
    tiktok_trends: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Combine trends from both platforms into a unified ranked list."""
    combined = []
    for t in youtube_trends:
        combined.append({**t, "platform": "youtube"})
    for t in tiktok_trends:
        combined.append({**t, "platform": "tiktok"})
    return sorted(combined, key=lambda x: x.get("score", 0), reverse=True)


def analyze_niche_opportunity(
    niche: str,
    all_hashtags: list[dict[str, Any]],
    all_trends: list[dict[str, Any]],
) -> dict[str, Any]:
    """Score how well a niche is currently trending.

    Returns a report with: opportunity_score, competition_level,
    trending_hashtags, content_angles, recommended_posting_times.
    """
    niche_lower = niche.lower()

    # Find relevant tags
    relevant_tags = [
        t for t in all_hashtags
        if niche_lower in t["tag"] or t["tag"] in niche_lower
    ]

    # Competition proxy: avg frequency across all tags
    avg_freq = (
        sum(t["frequency"] for t in all_hashtags) / len(all_hashtags)
        if all_hashtags else 1
    )
    niche_freq = (
        sum(t["frequency"] for t in relevant_tags) / len(relevant_tags)
        if relevant_tags else 0
    )

    # Opportunity score: high views + moderate competition = best
    opp_score = 0.0
    for t in relevant_tags:
        views_norm = math.log10(max(t.get("avg_views", 1), 1)) / 7  # 0-1
        comp_norm = min(niche_freq / max(avg_freq, 1), 1)
        opp_score += views_norm * (1 - comp_norm * 0.5)

    opp_score = round(min(opp_score * 10, 100), 1)

    if opp_score >= 70:
        competition = "low — great opportunity"
    elif opp_score >= 40:
        competition = "medium — competitive but viable"
    else:
        competition = "high — saturated niche"

    content_angles = _suggest_content_angles(niche)
    posting_times = _optimal_posting_times(niche)

    return {
        "niche": niche,
        "opportunity_score": opp_score,
        "competition_level": competition,
        "trending_hashtag_count": len(relevant_tags),
        "top_hashtags": [t["tag"] for t in relevant_tags[:5]],
        "content_angles": content_angles,
        "recommended_posting_times": posting_times,
    }


def generate_hashtag_sets(
    hashtags: list[dict[str, Any]],
    niche: str = "",
    post_type: str = "standard",
) -> dict[str, list[str]]:
    """Generate ready-to-use hashtag sets for different post strategies.

    Returns a dict with three sets:
      - viral: max viral potential (trending, high score)
      - niche: targeted niche engagement
      - balanced: mix of viral + niche (recommended)
    """
    sorted_tags = sorted(hashtags, key=lambda h: h.get("score", 0), reverse=True)

    # Split into tiers
    top = [t["tag"] for t in sorted_tags[:10]]
    mid = [t["tag"] for t in sorted_tags[10:25]]
    low = [t["tag"] for t in sorted_tags[25:40]]

    # Always-include tags
    base = ["fyp", "viral", "trending"]
    if niche:
        base.append(niche.lower().replace(" ", ""))

    def _make_set(tags: list[str], size: int = 15) -> list[str]:
        combined = list(dict.fromkeys(base + tags))  # dedup, preserve order
        return combined[:size]

    return {
        "viral": _make_set(top[:12]),
        "niche": _make_set(mid[:12] + [niche.lower().replace(" ", "")] if niche else mid[:12]),
        "balanced": _make_set(top[:6] + mid[:6] + low[:3]),
    }


def score_content_idea(
    title: str,
    hashtags: list[str],
    trending_hashtags: list[dict[str, Any]],
    trending_sounds: list[dict[str, Any]],
) -> dict[str, Any]:
    """Score a content idea against current trends.

    Returns: relevance_score (0-100), matched_hashtags, sound_recommendation, verdict.
    """
    title_lower = title.lower()
    matched = []
    trend_score = 0.0

    for ht in trending_hashtags:
        tag = ht["tag"]
        if tag in hashtags or tag in title_lower:
            matched.append(tag)
            trend_score += ht.get("score", 0)

    # Normalize to 0-100
    max_possible = sum(h.get("score", 0) for h in trending_hashtags[:5]) or 1
    relevance = round(min(trend_score / max_possible * 100, 100), 1)

    top_sound = trending_sounds[0] if trending_sounds else None
    sound_rec = top_sound.get("title", "Any trending sound") if top_sound else "Browse current trending sounds"

    if relevance >= 70:
        verdict = "Highly aligned with trends — post ASAP"
    elif relevance >= 40:
        verdict = "Moderately trendy — add more trending hashtags"
    else:
        verdict = "Low trend alignment — pivot topic or wait for a better trend cycle"

    return {
        "relevance_score": relevance,
        "matched_hashtags": matched,
        "sound_recommendation": sound_rec,
        "verdict": verdict,
    }


# ── Internal helpers ───────────────────────────────────────────────────

_CONTENT_ANGLES: dict[str, list[str]] = {
    "fitness": ["30-day transformation", "5-min home workout", "gym mistakes", "what I eat in a day", "trainer reacts"],
    "food": ["recipe under 5 mins", "restaurant vs homemade", "broke college meals", "aesthetic food prep", "food hacks"],
    "luxury": ["day in my life", "what rich people buy", "luxury haul", "comparing prices", "CEO morning routine"],
    "motivation": ["mindset shift", "quotes that hit different", "raw truth", "glow-up story", "millionaire habits"],
    "fashion": ["outfit of the day", "style on a budget", "trend vs classic", "closet clean-out", "seasonal haul"],
    "gaming": ["speedrun attempts", "game breaking glitches", "ranking every character", "reacting to noobs", "hidden features"],
    "beauty": ["drugstore dupes", "no makeup makeup", "skin transformation", "honest reviews", "grwm vlog"],
    "finance": ["how I made $X", "passive income ideas", "money mistakes to avoid", "investing 101", "frugal hacks"],
}

_POSTING_TIMES: dict[str, list[str]] = {
    "fitness": ["6:00 AM", "12:00 PM", "6:00 PM"],
    "food": ["11:00 AM", "5:00 PM", "8:00 PM"],
    "luxury": ["9:00 AM", "2:00 PM", "8:00 PM"],
    "default": ["7:00 AM", "12:00 PM", "7:00 PM"],
}


def _suggest_content_angles(niche: str) -> list[str]:
    niche_lower = niche.lower()
    for key, angles in _CONTENT_ANGLES.items():
        if key in niche_lower:
            return angles
    return [
        "Day in the life",
        "Top 5 secrets",
        "Before vs after",
        "Beginner mistakes",
        "Honest review",
    ]


def _optimal_posting_times(niche: str) -> list[str]:
    niche_lower = niche.lower()
    for key, times in _POSTING_TIMES.items():
        if key in niche_lower:
            return times
    return _POSTING_TIMES["default"]


def _hashtag_recommendation(
    tag: str, avg_views: int, frequency: int, platforms: list[str]
) -> str:
    if avg_views > 1_000_000 and len(platforms) > 1:
        return "Top priority — viral cross-platform"
    if avg_views > 500_000:
        return "High value — use in every post"
    if frequency > 10:
        return "Consistent performer — reliable reach"
    return "Emerging — monitor for growth"
