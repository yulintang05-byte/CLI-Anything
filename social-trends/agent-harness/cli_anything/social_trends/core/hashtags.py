"""Hashtag optimization — generate tiered hashtag sets, analyze strategy."""

from cli_anything.social_trends.utils.social_backend import (
    get_niche_hashtags,
    list_niches,
    NICHE_HASHTAGS,
)


# Per-platform hashtag count recommendations
PLATFORM_HASHTAG_LIMITS = {
    "tiktok":    {"min": 3, "max": 5,  "recommended": 4,  "note": "Use 3–5 focused tags; algorithm favors relevance over volume"},
    "instagram": {"min": 5, "max": 30, "recommended": 20, "note": "Use 20–25 for Reels; mix mega/large/niche tiers"},
    "youtube":   {"min": 3, "max": 15, "recommended": 5,  "note": "Use 3–5 tags in title/description; they appear above title"},
    "twitter":   {"min": 1, "max": 3,  "recommended": 2,  "note": "1–2 is optimal; too many reduces engagement"},
    "linkedin":  {"min": 3, "max": 5,  "recommended": 5,  "note": "3–5 relevant professional hashtags"},
}


def optimize_hashtags(
    niche: str,
    platform: str = "tiktok",
    strategy: str = "balanced",
    count: int = 0,
) -> dict:
    """Generate an optimized hashtag set for a niche and platform."""
    platform = platform.lower()
    limits = PLATFORM_HASHTAG_LIMITS.get(platform, PLATFORM_HASHTAG_LIMITS["tiktok"])
    target = count or limits["recommended"]
    tags_by_tier = get_niche_hashtags(niche)

    if strategy == "reach":
        ordered_tiers = ["mega", "large", "medium", "niche"]
    elif strategy == "engagement":
        ordered_tiers = ["niche", "medium", "large", "mega"]
    else:  # balanced
        ordered_tiers = ["large", "medium", "niche", "mega"]

    selected: list[str] = []
    per_tier = max(1, target // len(ordered_tiers))
    for tier in ordered_tiers:
        pool = tags_by_tier.get(tier, [])
        selected.extend(pool[:per_tier])

    # Fill up to target if needed
    if len(selected) < target:
        all_tags = [t for tier in ordered_tiers for t in tags_by_tier.get(tier, [])]
        for t in all_tags:
            if t not in selected:
                selected.append(t)
            if len(selected) >= target:
                break

    selected = selected[:target]

    return {
        "niche": niche,
        "platform": platform,
        "strategy": strategy,
        "count": len(selected),
        "hashtags": selected,
        "copy_ready": " ".join(selected),
        "limits": limits,
        "tiers_used": {
            tier: [t for t in selected if t in tags_by_tier.get(tier, [])]
            for tier in ["mega", "large", "medium", "niche"]
        },
    }


def generate_hashtag_sets(niche: str, platform: str = "tiktok") -> dict:
    """Generate multiple hashtag sets (A/B test variants)."""
    sets = {}
    for strategy in ("reach", "engagement", "balanced"):
        result = optimize_hashtags(niche, platform, strategy)
        sets[strategy] = {
            "hashtags": result["hashtags"],
            "copy_ready": result["copy_ready"],
            "use_case": {
                "reach": "New account or post — maximize impressions",
                "engagement": "Established account — maximize comments/saves",
                "balanced": "Default — good mix of reach and engagement",
            }[strategy],
        }
    limits = PLATFORM_HASHTAG_LIMITS.get(platform.lower(), PLATFORM_HASHTAG_LIMITS["tiktok"])
    return {
        "niche": niche,
        "platform": platform,
        "sets": sets,
        "platform_tip": limits["note"],
        "rotation_tip": "Rotate between sets every 3–5 posts to avoid shadowban.",
    }


def analyze_hashtag(tag: str) -> dict:
    """Return analysis for a single hashtag."""
    tag = tag.lstrip("#").lower()
    for niche, tiers in NICHE_HASHTAGS.items():
        for tier, tags in tiers.items():
            clean_tags = [t.lstrip("#").lower() for t in tags]
            if tag in clean_tags:
                tier_info = {
                    "mega":   {"size": "500M+ posts", "competition": "Very High", "reach": "Maximum", "tip": "Use as 1 of 3–5 tags only"},
                    "large":  {"size": "10M–500M posts", "competition": "High", "reach": "High", "tip": "Good anchor tag"},
                    "medium": {"size": "1M–10M posts", "competition": "Medium", "reach": "Good", "tip": "Sweet spot for growth"},
                    "niche":  {"size": "<1M posts", "competition": "Low", "reach": "Targeted", "tip": "High engagement rate"},
                }
                return {
                    "tag": f"#{tag}",
                    "niche": niche,
                    "tier": tier,
                    **tier_info.get(tier, {}),
                    "found_in_database": True,
                }
    return {
        "tag": f"#{tag}",
        "niche": "unknown",
        "tier": "unknown",
        "found_in_database": False,
        "tip": "Research this tag's post count on each platform before using.",
    }


def list_all_niches() -> list[dict]:
    """List all supported niches with their tag counts."""
    result = []
    for niche, tiers in NICHE_HASHTAGS.items():
        total = sum(len(v) for v in tiers.values())
        result.append({
            "niche": niche,
            "total_tags": total,
            "tiers": list(tiers.keys()),
        })
    return sorted(result, key=lambda x: x["niche"])


def get_platform_strategy(platform: str) -> dict:
    """Full hashtag strategy guide for a platform."""
    p = platform.lower()
    limits = PLATFORM_HASHTAG_LIMITS.get(p, PLATFORM_HASHTAG_LIMITS["tiktok"])
    guides = {
        "tiktok": {
            "strategy": "Less is more. TikTok's algorithm distributes content based on viewer signals, not hashtags. Use 3–5 ultra-relevant tags.",
            "dos": ["Use 1 mega + 2–3 niche tags", "Include #fyp only if content is broadly entertaining", "Use niche tags to reach targeted communities", "Match hashtags to exact video content"],
            "donts": ["Don't use 20+ hashtags", "Don't copy-paste same set every post", "Don't use irrelevant mega tags", "Don't buy or follow hashtag 'cheat sheets' blindly"],
            "growth_hack": "Pin your top 3 hashtags in comments instead of caption to keep captions clean and boost engagement.",
        },
        "instagram": {
            "strategy": "Use 20–25 hashtags for Reels, 5–10 for feed posts. Mix 20% mega, 40% large, 30% medium, 10% niche.",
            "dos": ["Put hashtags in caption (not comments) for Reels", "Research competitors' hashtags", "Track which sets perform best", "Use location hashtags for local businesses"],
            "donts": ["Don't use banned hashtags (check beforehand)", "Don't use the same set every post — rotate 3 sets", "Don't stuff captions with irrelevant tags"],
            "growth_hack": "Create a niche-specific hashtag (e.g., #YourBrand + niche) and use it consistently to build community.",
        },
        "youtube": {
            "strategy": "Use 3–5 tags in the description. The first hashtag appears above the video title. Keywords matter more than hashtags for YouTube SEO.",
            "dos": ["Use tags directly related to your video topic", "Research what competitor videos rank for", "Include your channel name as a hashtag", "Use the video's main keyword as first hashtag"],
            "donts": ["Don't use misleading tags", "Don't use excessive hashtags (YouTube may ignore your description)", "Don't keyword-stuff"],
            "growth_hack": "Pair hashtags with strong title and description SEO — YouTube is primarily a search engine, not a feed.",
        },
    }
    guide = guides.get(p, guides.get("tiktok", {}))
    return {
        "platform": p,
        "limits": limits,
        **guide,
    }
