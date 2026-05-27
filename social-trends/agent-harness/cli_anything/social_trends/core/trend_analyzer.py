"""Cross-platform trend analyzer.

Merges YouTube and TikTok data into unified trend scores,
identifies cross-platform viral themes, and surfaces actionable insights.
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any


# ── Cross-platform merge ──────────────────────────────────────────────────────

def merge_hashtags(yt_tags: list[dict], tt_tags: list[dict]) -> list[dict]:
    """Merge YouTube and TikTok hashtags by name, computing a unified score."""
    combined: dict[str, dict] = {}

    for i, tag in enumerate(yt_tags):
        name = _normalize_tag(tag.get("hashtag", ""))
        if not name:
            continue
        entry = combined.setdefault(name, {"hashtag": name, "yt_rank": None,
                                           "tt_rank": None, "views": 0,
                                           "frequency": 0, "platforms": []})
        entry["yt_rank"] = i + 1
        entry["frequency"] = tag.get("frequency", 1)
        if "youtube" not in entry["platforms"]:
            entry["platforms"].append("youtube")

    for i, tag in enumerate(tt_tags):
        name = _normalize_tag(tag.get("hashtag", ""))
        if not name:
            continue
        entry = combined.setdefault(name, {"hashtag": name, "yt_rank": None,
                                           "tt_rank": None, "views": 0,
                                           "frequency": 0, "platforms": []})
        entry["tt_rank"] = i + 1
        entry["views"] = tag.get("views", 0)
        if "tiktok" not in entry["platforms"]:
            entry["platforms"].append("tiktok")

    results = list(combined.values())
    for r in results:
        r["score"] = _trend_score(r)
        r["cross_platform"] = len(r["platforms"]) > 1

    return sorted(results, key=lambda x: -x["score"])


def merge_trends(yt_videos: list[dict], tt_videos: list[dict]) -> dict:
    """Build a unified trend report from both platforms."""
    yt_themes = _extract_themes(yt_videos)
    tt_themes = _extract_themes(tt_videos)

    # Union all themes, score by combined frequency
    all_themes: dict[str, int] = defaultdict(int)
    for theme, freq in yt_themes.items():
        all_themes[theme] += freq * 2      # slight YouTube weight
    for theme, freq in tt_themes.items():
        all_themes[theme] += freq * 3      # TikTok moves faster

    top_themes = sorted(all_themes.items(), key=lambda x: -x[1])[:10]

    return {
        "top_themes": [{"theme": t, "score": s} for t, s in top_themes],
        "youtube_video_count": len(yt_videos),
        "tiktok_video_count": len(tt_videos),
        "cross_platform_opportunity": _cross_platform_themes(yt_themes, tt_themes),
    }


# ── Scoring ───────────────────────────────────────────────────────────────────

def _trend_score(entry: dict) -> float:
    """Composite trend score. Higher = more viral potential."""
    score = 0.0
    if entry.get("yt_rank"):
        score += max(0, 50 - entry["yt_rank"])     # up to 49 pts
    if entry.get("tt_rank"):
        score += max(0, 50 - entry["tt_rank"])
    if entry.get("cross_platform"):
        score += 30                                  # big bonus
    if entry.get("views", 0) > 1_000_000_000:
        score += 20
    elif entry.get("views", 0) > 100_000_000:
        score += 10
    score += min(entry.get("frequency", 0), 15)
    return round(score, 1)


def score_hashtag_set(hashtags: list[str]) -> dict:
    """Score a user-provided list of hashtags for estimated reach."""
    ranked = []
    for tag in hashtags:
        name = _normalize_tag(tag)
        tier = _hashtag_tier(name)
        ranked.append({
            "hashtag": name,
            "tier": tier["tier"],
            "estimated_reach": tier["reach"],
            "recommendation": tier["recommendation"],
        })
    return {
        "hashtags": ranked,
        "mix_score": _mix_score(ranked),
        "suggestion": _mix_advice(ranked),
    }


def _hashtag_tier(tag: str) -> dict:
    """Classify a hashtag by rough size tier."""
    # Discovery tags (100B+ views)
    discovery = {"fyp", "foryoupage", "foryou", "viral", "trending", "tiktok"}
    # Large niche (10B+)
    large = {"fitness", "motivation", "fashion", "food", "travel", "beauty",
             "music", "dance", "comedy", "howto", "tutorial", "lifestyle",
             "aesthetic", "workout", "recipe", "ootd", "makeup", "gaming"}
    # Medium niche (1B-10B)
    medium = {"booktok", "studytok", "smallbusiness", "entrepreneur",
              "financetiktok", "skincare", "yoga", "meditation", "cooking",
              "vegan", "minimalism", "digitalart", "photography"}

    clean = tag.lstrip("#").lower()
    if clean in discovery:
        return {
            "tier": "discovery",
            "reach": "100B+ views",
            "recommendation": "Good for discoverability but very competitive.",
        }
    if clean in large:
        return {
            "tier": "large-niche",
            "reach": "10B-100B views",
            "recommendation": "Strong reach — use 2-3 of these per post.",
        }
    if clean in medium:
        return {
            "tier": "medium-niche",
            "reach": "1B-10B views",
            "recommendation": "Good engagement density — ideal core tag.",
        }
    return {
        "tier": "micro-niche",
        "reach": "<1B views",
        "recommendation": "High engagement rate — combine with larger tags.",
    }


def _mix_score(ranked: list[dict]) -> str:
    tiers = [r["tier"] for r in ranked]
    if not tiers:
        return "N/A"
    has_discovery = any(t == "discovery" for t in tiers)
    has_large = any(t == "large-niche" for t in tiers)
    has_micro = any(t == "micro-niche" for t in tiers)
    if has_discovery and has_large and has_micro:
        return "Excellent — balanced mix across tiers"
    if has_large and has_micro:
        return "Good — add 1-2 discovery tags"
    if has_discovery and not has_micro:
        return "Fair — too broad, add micro-niche tags"
    return "Needs work — see suggestions below"


def _mix_advice(ranked: list[dict]) -> str:
    tiers = {r["tier"] for r in ranked}
    tips = []
    if "discovery" not in tiers:
        tips.append("Add 1-2 discovery tags (#fyp, #viral)")
    if "large-niche" not in tiers:
        tips.append("Add 1-2 large niche tags relevant to your content")
    if "micro-niche" not in tiers:
        tips.append("Add 3-5 micro-niche tags for your specific audience")
    if len(ranked) < 5:
        tips.append("Use 5-10 hashtags per post for best coverage")
    if len(ranked) > 15:
        tips.append("Keep hashtags under 15 — too many dilutes engagement")
    return "; ".join(tips) if tips else "Hashtag mix looks good!"


# ── Theme extraction ──────────────────────────────────────────────────────────

_THEME_KEYWORDS = {
    "fitness": {"fitness", "workout", "gym", "health", "exercise", "training"},
    "food": {"food", "recipe", "cooking", "baking", "eat", "chef", "meal"},
    "travel": {"travel", "vacation", "trip", "explore", "adventure", "world"},
    "fashion": {"fashion", "style", "ootd", "outfit", "clothes", "wear"},
    "beauty": {"beauty", "makeup", "skincare", "cosmetics", "glow", "foundation"},
    "tech": {"tech", "technology", "coding", "programming", "ai", "software"},
    "gaming": {"game", "gaming", "gamer", "gameplay", "console", "esports"},
    "music": {"music", "song", "artist", "singer", "rap", "pop", "album"},
    "education": {"learn", "tutorial", "howto", "tips", "study", "school"},
    "motivation": {"motivation", "mindset", "success", "grind", "hustle"},
    "business": {"business", "entrepreneur", "startup", "money", "invest"},
    "comedy": {"funny", "comedy", "humor", "laugh", "meme", "joke"},
    "lifestyle": {"lifestyle", "aesthetic", "vibe", "daily", "routine"},
    "pets": {"dog", "cat", "pet", "puppy", "kitten", "animal"},
}


def _extract_themes(videos: list[dict]) -> dict[str, int]:
    freq: dict[str, int] = defaultdict(int)
    for v in videos:
        text = (
            v.get("title", "") + " " +
            v.get("description", "") + " " +
            " ".join(v.get("tags", [])) + " " +
            " ".join(v.get("hashtags", []))
        ).lower()
        for theme, keywords in _THEME_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                freq[theme] += 1
    return dict(freq)


def _cross_platform_themes(yt: dict, tt: dict) -> list[str]:
    """Themes present on both platforms — highest opportunity."""
    yt_set = set(yt.keys())
    tt_set = set(tt.keys())
    return sorted(yt_set & tt_set)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _normalize_tag(tag: str) -> str:
    clean = tag.strip().lower()
    if not clean.startswith("#"):
        clean = "#" + clean
    return clean
