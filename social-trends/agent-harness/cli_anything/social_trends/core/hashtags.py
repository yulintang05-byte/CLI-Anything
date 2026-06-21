"""Hashtag Aggregation — Cross-platform hashtag scoring and optimization."""

import re
from typing import Optional


_OPTIMAL_COUNT = {"tiktok": 5, "youtube": 8, "instagram": 15, "default": 10}

_BANNED_OR_SHADOWBAN_RISK = {
    "followback", "f4f", "like4like", "l4l", "follow4follow",
    "likeforlike", "spamforspam",
}


def score_hashtag_set(hashtags: list[str], platform: str = "tiktok") -> dict:
    """Score a set of hashtags for effectiveness on a given platform."""
    cleaned = [_normalize(h) for h in hashtags if _normalize(h)]
    issues = []
    score = 100

    optimal = _OPTIMAL_COUNT.get(platform, _OPTIMAL_COUNT["default"])
    if len(cleaned) > optimal * 1.5:
        score -= 15
        issues.append(f"Too many hashtags ({len(cleaned)}); optimal for {platform} is ~{optimal}")
    elif len(cleaned) < 3:
        score -= 20
        issues.append("Too few hashtags; use at least 3")

    risky = [h for h in cleaned if h in _BANNED_OR_SHADOWBAN_RISK]
    if risky:
        score -= 30
        issues.append(f"Shadowban-risk hashtags detected: {', '.join('#' + r for r in risky)}")

    duplicates = [h for h in cleaned if cleaned.count(h) > 1]
    if duplicates:
        score -= 10
        issues.append(f"Duplicate hashtags: {', '.join(set('#' + d for d in duplicates))}")

    has_broad = any(h in {"fyp", "foryou", "foryoupage", "viral", "trending"} for h in cleaned)
    has_niche = any(len(h) > 8 and h not in {"foryoupage", "foryou"} for h in cleaned)
    if not has_broad:
        score -= 10
        issues.append("No broad reach hashtags (#fyp, #foryou, #viral)")
    if not has_niche:
        score -= 10
        issues.append("No niche-specific hashtags — add content-specific tags")

    return {
        "score": max(0, score),
        "grade": _grade(score),
        "count": len(cleaned),
        "optimal_count": optimal,
        "issues": issues,
        "cleaned_hashtags": ["#" + h for h in cleaned],
    }


def build_optimal_set(
    niche_tags: list[str],
    viral_tags: list[str],
    platform: str = "tiktok",
    count: Optional[int] = None,
) -> list[str]:
    """Build an optimal hashtag set mixing broad viral + niche-specific tags."""
    optimal = count or _OPTIMAL_COUNT.get(platform, 10)
    broad = [t for t in viral_tags if _normalize(t) in {"fyp", "foryou", "foryoupage", "viral", "trending"}]
    niche = [t for t in niche_tags if _normalize(t) not in {_normalize(b) for b in broad}]
    mid_tier = [t for t in viral_tags if t not in broad]

    result = []
    # Always include 2-3 broad tags
    result.extend(broad[:3])
    # Fill with niche tags
    remaining = optimal - len(result)
    result.extend(niche[:max(remaining // 2, 2)])
    # Fill rest with mid-tier viral
    remaining = optimal - len(result)
    result.extend(mid_tier[:remaining])
    # Trim to optimal
    return result[:optimal]


def suggest_caption_hashtags(caption: str, available_tags: list[str], platform: str = "tiktok") -> list[str]:
    """Pick hashtags relevant to caption text."""
    words = set(re.findall(r"\b\w+\b", caption.lower()))
    scored: list[tuple[int, str]] = []
    for tag in available_tags:
        tag_words = set(re.findall(r"\b\w+\b", tag.lower().lstrip("#")))
        overlap = len(words & tag_words)
        scored.append((overlap, tag))
    scored.sort(key=lambda x: -x[0])
    optimal = _OPTIMAL_COUNT.get(platform, 10)
    return [t for _, t in scored[:optimal]]


def _normalize(h: str) -> str:
    return h.lstrip("#").strip().lower()


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 45:
        return "D"
    return "F"
