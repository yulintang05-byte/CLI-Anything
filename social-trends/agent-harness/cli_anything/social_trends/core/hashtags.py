"""Hashtag strategy engine — mix, score, and optimize hashtag sets."""

from typing import Optional


# Tier definitions for hashtag strategy
_TIER_THRESHOLDS = {
    "mega":   500_000_000,   # 500M+ views  — extremely broad, low reach probability
    "large":  100_000_000,   # 100M–500M    — high competition
    "medium":  10_000_000,   # 10M–100M     — balanced sweet spot
    "small":   1_000_000,    # 1M–10M       — niche, higher chance of featuring
    "micro":           0,    # <1M           — very niche, tight community
}

_IDEAL_MIX = {
    "mega":   2,
    "large":  3,
    "medium": 8,
    "small":  5,
    "micro":  5,
}  # Total 23 — leave room for niche/branded

_MAX_TIKTOK_HASHTAGS = 30
_MAX_INSTAGRAM_HASHTAGS = 30
_MAX_YOUTUBE_HASHTAGS = 15


def classify_hashtag(view_count: int) -> str:
    """Classify a hashtag by view/use count into a competition tier."""
    for tier, threshold in _TIER_THRESHOLDS.items():
        if view_count >= threshold:
            return tier
    return "micro"


def score_hashtag_set(hashtags: list[dict]) -> dict:
    """Score a hashtag set for expected reach vs. discoverability balance."""
    tier_counts: dict[str, int] = {t: 0 for t in _TIER_THRESHOLDS}
    for h in hashtags:
        tier = h.get("tier") or classify_hashtag(h.get("view_count", 0))
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    total = len(hashtags)
    ideal_total = sum(_IDEAL_MIX.values())

    # Score based on deviation from ideal mix
    score = 100
    for tier, ideal_count in _IDEAL_MIX.items():
        actual_ratio = tier_counts.get(tier, 0) / max(total, 1)
        ideal_ratio = ideal_count / ideal_total
        deviation = abs(actual_ratio - ideal_ratio)
        score -= deviation * 30  # penalize 30 points per full deviation unit

    score = max(0, min(100, round(score)))

    return {
        "score": score,
        "total": total,
        "tier_breakdown": tier_counts,
        "recommendation": _score_recommendation(score),
    }


def _score_recommendation(score: int) -> str:
    if score >= 85:
        return "Excellent mix — strong balance of reach and discoverability"
    if score >= 70:
        return "Good mix — minor adjustments could improve discoverability"
    if score >= 50:
        return "Fair — add more medium/small tier hashtags for better reach"
    return "Needs improvement — too many mega tags dilute your discoverability"


def build_optimal_set(
    niche_tags: list[str],
    trending_tags: list[dict],
    platform: str = "tiktok",
    branded_tags: Optional[list[str]] = None,
    max_count: Optional[int] = None,
) -> list[str]:
    """Build an optimised hashtag set for a post.

    Strategy:
    - 2 mega tags (fyp, viral) for broad exposure
    - 3 large trending tags from current trends
    - 8 medium niche tags
    - 5 small niche tags
    - 5 micro/branded tags
    - 1–2 branded tags if provided
    """
    if max_count is None:
        max_count = {
            "tiktok": _MAX_TIKTOK_HASHTAGS,
            "instagram": _MAX_INSTAGRAM_HASHTAGS,
            "youtube": _MAX_YOUTUBE_HASHTAGS,
        }.get(platform.lower(), 20)

    result: list[str] = []
    seen: set[str] = set()

    def _add(tag: str):
        t = tag if tag.startswith("#") else f"#{tag}"
        t_lower = t.lower()
        if t_lower not in seen and len(result) < max_count:
            result.append(t)
            seen.add(t_lower)

    # Mega — universal reach
    for t in ["#fyp", "#foryou", "#viral"]:
        _add(t)

    # Large — top trending (by view/use count)
    trending_sorted = sorted(
        trending_tags, key=lambda x: x.get("view_count", x.get("count", 0)), reverse=True
    )
    for item in trending_sorted[:4]:
        _add(item.get("hashtag", ""))

    # Medium + small — niche tags
    for t in niche_tags[:18]:
        _add(t)

    # Branded
    for t in (branded_tags or [])[:3]:
        _add(t)

    # Fill remaining with more niche tags
    for t in niche_tags[18:]:
        _add(t)

    return result[:max_count]


def format_hashtags(tags: list[str], style: str = "inline") -> str:
    """Format a hashtag list for copy-paste.

    styles: inline, newline, spaced
    """
    if style == "newline":
        return "\n".join(tags)
    if style == "spaced":
        return " ".join(tags)
    # inline — block separated from caption
    return "\n\n" + " ".join(tags)


def hashtag_report(tags: list[str], view_counts: Optional[dict] = None) -> list[dict]:
    """Generate a detailed report for each hashtag."""
    report = []
    for tag in tags:
        vc = (view_counts or {}).get(tag.lstrip("#").lower(), 0)
        report.append({
            "hashtag": tag,
            "view_count": vc,
            "tier": classify_hashtag(vc),
            "formatted": tag if tag.startswith("#") else f"#{tag}",
        })
    return report
