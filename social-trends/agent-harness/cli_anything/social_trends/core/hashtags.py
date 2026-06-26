"""Hashtag analysis — scoring, suggestions, and cross-platform ranking."""

import re
from typing import Any, Dict, List, Optional


# Rough engagement-tier classification by follower reach
_TIER_THRESHOLDS = {
    "nano":  (0,       100_000),      # < 100K posts — low competition, high engagement
    "micro": (100_000, 500_000),      # 100K–500K
    "mid":   (500_000, 2_000_000),    # 500K–2M
    "macro": (2_000_000, 10_000_000), # 2M–10M
    "mega":  (10_000_000, None),      # 10M+ — dominated by big accounts
}

# Platform best-practice hashtag counts
PLATFORM_HASHTAG_LIMITS = {
    "tiktok":    {"optimal": 5,  "max": 10,  "note": "3-5 works best; over 10 hurts reach"},
    "instagram": {"optimal": 8,  "max": 30,  "note": "7-15 highly relevant tags outperform 30 generic ones"},
    "youtube":   {"optimal": 5,  "max": 15,  "note": "Put top 3 in title; rest in description"},
    "twitter":   {"optimal": 2,  "max": 4,   "note": "1-2 highly specific tags drive CTR"},
    "linkedin":  {"optimal": 3,  "max": 5,   "note": "3 professional niche tags recommended"},
}


def classify_hashtag_by_volume(post_count: int) -> str:
    """Return the competition tier for a hashtag based on post count."""
    for tier, (low, high) in _TIER_THRESHOLDS.items():
        if high is None:
            if post_count >= low:
                return tier
        elif low <= post_count < high:
            return tier
    return "unknown"


def score_hashtag_set(hashtags: List[str], post_counts: Dict[str, int]) -> Dict[str, Any]:
    """
    Score a set of hashtags for a post.

    Returns a diversity score (mix of tiers), coverage score, and
    per-tag details.
    """
    scored = []
    tier_counts: Dict[str, int] = {}
    for tag in hashtags:
        clean = tag.lstrip("#").lower()
        count = post_counts.get(clean, 0)
        tier = classify_hashtag_by_volume(count)
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
        scored.append({
            "hashtag": f"#{clean}",
            "post_count": count,
            "tier": tier,
        })

    if not hashtags:
        return {
            "hashtags": [],
            "tier_distribution": {},
            "diversity_score": 0,
            "quality_score": 0,
            "recommendation": "No hashtags provided.",
        }

    # Diversity = how many tiers are represented (ideal: nano + micro + mid)
    ideal_tiers = {"nano", "micro", "mid"}
    present_tiers = set(tier_counts.keys())
    diversity_score = len(ideal_tiers & present_tiers) / len(ideal_tiers)

    # Penalize if too many mega tags (low discovery)
    mega_ratio = tier_counts.get("mega", 0) / max(len(hashtags), 1)
    quality_score = round((diversity_score * 0.7 + (1 - mega_ratio) * 0.3) * 100)

    return {
        "hashtags": scored,
        "tier_distribution": tier_counts,
        "diversity_score": round(diversity_score * 100),
        "quality_score": quality_score,
        "recommendation": _recommend_from_tiers(tier_counts, len(hashtags)),
    }


def _recommend_from_tiers(tier_counts: Dict[str, int], total: int) -> str:
    mega = tier_counts.get("mega", 0)
    nano = tier_counts.get("nano", 0)
    mid = tier_counts.get("mid", 0)
    if mega > total * 0.5:
        return "Too many high-competition mega tags. Replace half with nano/micro niche tags for better reach."
    if nano > total * 0.7:
        return "Very niche mix — good for engaged audiences, but add 2-3 mid-tier tags to broaden discovery."
    if mid >= 2 and nano >= 2:
        return "Solid mix of niche and mid-tier tags. Consider adding 1 trending tag for viral potential."
    return "Balanced hashtag set. Monitor post performance to refine further."


def generate_hashtag_strategy(
    niche: str,
    platform: str = "tiktok",
    trending_tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Generate a complete hashtag strategy for a niche and platform.

    Returns tiered hashtag buckets with counts and rationale.
    """
    platform = platform.lower()
    limits = PLATFORM_HASHTAG_LIMITS.get(platform, PLATFORM_HASHTAG_LIMITS["tiktok"])
    optimal = limits["optimal"]

    niche_slug = niche.lower().replace(" ", "")
    trending = [t.lstrip("#").lower() for t in (trending_tags or [])]

    # Build buckets
    nano_tags = [f"#{niche_slug}niche", f"#{niche_slug}community", f"#{niche_slug}tips"]
    micro_tags = [f"#{niche_slug}101", f"#{niche_slug}hack", f"#{niche_slug}daily"]
    mid_tags = [f"#{niche_slug}", f"#{niche_slug}life", f"#{niche_slug}lover"]
    trend_tags = [f"#{t}" for t in trending[:3]]

    # Mix according to optimal count
    if optimal <= 3:
        strategy_tags = trend_tags[:1] + mid_tags[:1] + nano_tags[:1]
    elif optimal <= 6:
        strategy_tags = trend_tags[:2] + mid_tags[:2] + micro_tags[:1] + nano_tags[:1]
    else:
        strategy_tags = trend_tags[:2] + mid_tags[:2] + micro_tags[:2] + nano_tags[:2]

    return {
        "niche": niche,
        "platform": platform,
        "optimal_count": optimal,
        "max_count": limits["max"],
        "platform_note": limits["note"],
        "strategy_tags": strategy_tags[:optimal],
        "all_suggestions": {
            "trending_viral": trend_tags,
            "mid_tier_discovery": mid_tags,
            "micro_niche": micro_tags,
            "nano_community": nano_tags,
        },
        "posting_tip": (
            f"For {platform}: start each post with your 2 strongest mid-tier tags, "
            f"then add niche-specific tags, end with 1-2 trending tags."
        ),
    }


def extract_hashtags_from_text(text: str) -> List[str]:
    """Extract all hashtags from a block of text."""
    return re.findall(r"#(\w+)", text)


def deduplicate_and_rank(
    hashtag_lists: List[List[str]],
) -> List[Dict[str, Any]]:
    """Merge multiple hashtag lists, deduplicate, and rank by frequency."""
    counts: Dict[str, int] = {}
    for lst in hashtag_lists:
        for tag in lst:
            clean = tag.lstrip("#").lower()
            counts[clean] = counts.get(clean, 0) + 1
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [{"hashtag": f"#{t}", "frequency": c} for t, c in ranked]


def suggest_caption_hashtags(
    caption: str,
    platform: str = "tiktok",
    extra_niche_tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Given a caption draft, extract existing hashtags and suggest improvements.
    """
    existing = extract_hashtags_from_text(caption)
    limits = PLATFORM_HASHTAG_LIMITS.get(platform.lower(), PLATFORM_HASHTAG_LIMITS["tiktok"])
    current_count = len(existing)
    optimal = limits["optimal"]

    suggestions = []
    if current_count < optimal:
        needed = optimal - current_count
        if extra_niche_tags:
            suggestions = [t.lstrip("#") for t in extra_niche_tags[:needed]]
        suggestions_fmt = [f"#{s}" for s in suggestions]
    else:
        suggestions_fmt = []

    return {
        "platform": platform,
        "existing_hashtags": [f"#{t}" for t in existing],
        "current_count": current_count,
        "optimal_count": optimal,
        "suggested_additions": suggestions_fmt,
        "platform_note": limits["note"],
        "status": "good" if current_count >= optimal else "add_more",
    }
