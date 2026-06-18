"""Hashtag strategy engine — scoring, mix optimization, and set generation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

# ── Tier definitions ──────────────────────────────────────────────────────────

# Based on post/view counts. Lower competition = higher engagement rate.
_TIERS: list[tuple[str, int, int, float, str]] = [
    # (tier_name, min_posts, max_posts, avg_engagement_rate, description)
    ("mega",   50_000_000,  999_999_999, 0.003, ">50M posts — max reach, very low ER"),
    ("large",  10_000_000,   49_999_999, 0.007, "10–50M posts — broad reach"),
    ("medium",  1_000_000,    9_999_999, 0.020, "1–10M posts — balanced"),
    ("small",     100_000,      999_999, 0.060, "100K–1M posts — niche, high ER"),
    ("micro",       1_000,       99_999, 0.150, "1K–100K posts — very niche, best ER"),
]

# Optimal hashtag mix per post size limit
_OPTIMAL_MIX: dict[str, dict[str, int]] = {
    "instagram": {"mega": 2, "large": 4, "medium": 6, "small": 8, "micro": 5},   # 25 total
    "tiktok":    {"mega": 1, "large": 2, "medium": 4, "small": 5, "micro": 3},   # 15 total
    "youtube":   {"mega": 2, "large": 3, "medium": 5, "small": 5, "micro": 0},   # 15 total
    "twitter":   {"mega": 0, "large": 1, "medium": 1, "small": 0, "micro": 0},   # 2 total
}

# Niche-specific high-performing hashtag sets (research-backed)
_NICHE_HASHTAGS: dict[str, dict[str, list[str]]] = {
    "fitness": {
        "mega":   ["fitness", "workout", "gym", "health", "fitnessmotivation"],
        "large":  ["weightloss", "bodybuilding", "exercise", "fitfam", "personaltrainer"],
        "medium": ["strengthtraining", "cardio", "homeworkout", "fitnessinspiration", "gains"],
        "small":  ["workoutmotivation", "fitnesscommunity", "gymlife", "calisthenics", "hiit"],
        "micro":  ["functionalfitness", "resistancetraining", "macros", "progresspic", "swolemate"],
    },
    "fashion": {
        "mega":   ["fashion", "style", "ootd", "outfit", "clothing"],
        "large":  ["fashionblogger", "streetstyle", "fashionista", "aesthetic", "vintage"],
        "medium": ["fashioninspo", "outfitinspo", "fashionstyle", "slowfashion", "thrift"],
        "small":  ["fashioncommunity", "outfitcheck", "fashionphotography", "capsulewardrobe"],
        "micro":  ["sustainablefashion", "minimalstyle", "luxuryfashion", "fashionforward"],
    },
    "food": {
        "mega":   ["food", "foodie", "recipe", "cooking", "eat"],
        "large":  ["instafood", "foodphotography", "homecooking", "foodblogger", "healthyfood"],
        "medium": ["mealprep", "foodlover", "delicious", "yummy", "foodstagram"],
        "small":  ["cookingvideos", "easyrecipes", "dinnerideas", "foodtiktok", "cheflife"],
        "micro":  ["plantbased", "veganrecipes", "glutenfree", "whole30", "keto"],
    },
    "finance": {
        "mega":   ["money", "finance", "investing", "wealth", "personalfinance"],
        "large":  ["financialliteracy", "stockmarket", "crypto", "sidehustle", "passiveincome"],
        "medium": ["moneymindset", "financetips", "budgeting", "debtfree", "financialgoals"],
        "small":  ["financialindependence", "investingtips", "stockstowatch", "buildingwealth"],
        "micro":  ["dividendinvesting", "indexfunds", "retirementplanning", "frugalliving"],
    },
    "beauty": {
        "mega":   ["beauty", "makeup", "skincare", "makeupartist", "cosmetics"],
        "large":  ["beautyinfluencer", "glam", "eyeliner", "foundation", "lipstick"],
        "medium": ["beautytips", "skincareRoutine", "makeuptutorial", "beautyreview"],
        "small":  ["cleanbeauty", "koreanbeauty", "naturalmakeup", "drugstorebeauty"],
        "micro":  ["hyperpigmentation", "actives", "retinol", "spf", "snailmucin"],
    },
    "travel": {
        "mega":   ["travel", "explore", "wanderlust", "traveler", "adventure"],
        "large":  ["travelphotography", "traveling", "vacation", "travellife", "travelblogger"],
        "medium": ["travelgram", "instatravel", "roadtrip", "backpacking", "budgettravel"],
        "small":  ["solotravel", "digitalnomad", "travelcouple", "luxurytravel", "hikemore"],
        "micro":  ["offthebeatenpath", "hiddengemtravel", "slowtravel", "vanlife"],
    },
    "motivation": {
        "mega":   ["motivation", "success", "mindset", "hustle", "entrepreneur"],
        "large":  ["inspiration", "positivity", "goalsetter", "grind", "businessowner"],
        "medium": ["motivationalquotes", "selfimprovement", "personaldevelopment", "growth"],
        "small":  ["disciplineoverexcitement", "smallbusiness", "consistency", "dailymotivation"],
        "micro":  ["stoicism", "atomichabits", "deepwork", "purposefullife"],
    },
    "gaming": {
        "mega":   ["gaming", "gamer", "videogames", "game", "twitch"],
        "large":  ["gameplay", "ps5", "xbox", "pcgaming", "streamer"],
        "medium": ["gamingcommunity", "gaminglife", "esports", "retrogaming", "fps"],
        "small":  ["indiegames", "rpg", "gamingsetup", "battlestation"],
        "micro":  ["soulslike", "roguelite", "coopgames", "competitive"],
    },
    "general": {
        "mega":   ["fyp", "viral", "trending", "foryou", "explore"],
        "large":  ["reels", "content", "creator", "socialmedia", "contentcreator"],
        "medium": ["smallcreator", "growmyaccount", "newcreator", "gainrealfollowers"],
        "small":  ["tiktoktips", "instagramtips", "youtubetips", "creatoreconomy"],
        "micro":  ["ugc", "contentcreation", "algorithimhacks", "growyourpresence"],
    },
}


@dataclass
class Hashtag:
    tag: str
    tier: str
    estimated_posts: int | None
    engagement_rate: float
    niche: str
    platform_score: dict[str, float]  # platform -> score 0-100


def get_tier(estimated_posts: int) -> str:
    for name, lo, hi, _, _ in _TIERS:
        if lo <= estimated_posts <= hi:
            return name
    return "micro" if estimated_posts < 1_000 else "mega"


def score_hashtag(tag: str, platform: str, niche: str = "general") -> float:
    """Score a hashtag 0–100 for use on a given platform in a given niche.

    Factors: tier fit for platform, niche relevance, estimated engagement.
    """
    tag_clean = tag.lower().lstrip("#").strip()
    niche_data = _NICHE_HASHTAGS.get(niche, _NICHE_HASHTAGS["general"])
    mix = _OPTIMAL_MIX.get(platform, _OPTIMAL_MIX["instagram"])

    # Check if it's a known high-value tag in the niche
    tier_score = 0.0
    for tier_name, tags in niche_data.items():
        if tag_clean in tags:
            # Score by how much this tier is desired
            count = mix.get(tier_name, 0)
            total = sum(mix.values()) or 1
            tier_score = (count / total) * 100
            break
    else:
        # Unknown tag — infer from name length (shorter = usually bigger)
        tier_score = max(10, 60 - len(tag_clean) * 2)

    # Platform-universal power tags that always score high
    _TIKTOK_POWER_TAGS = {"fyp", "foryou", "foryoupage", "viral", "trending", "xyzbca"}
    _IG_POWER_TAGS = {"explore", "reels", "reelsinstagram", "instadaily", "instagood"}
    if platform == "tiktok" and tag_clean in _TIKTOK_POWER_TAGS:
        tier_score = max(tier_score, 75.0)
    elif platform == "instagram" and tag_clean in _IG_POWER_TAGS:
        tier_score = max(tier_score, 60.0)

    return round(min(100, tier_score), 1)


def generate_hashtag_set(
    niche: str,
    platform: str,
    custom_tags: list[str] | None = None,
    include_general: bool = True,
) -> dict[str, list[str]]:
    """Generate an optimized hashtag set for a post.

    Returns a dict with tier-grouped hashtags and a flat list for copy-paste.
    """
    niche_key = niche.lower().replace(" ", "").replace("-", "")
    niche_data = _NICHE_HASHTAGS.get(niche_key, _NICHE_HASHTAGS["general"])
    mix = _OPTIMAL_MIX.get(platform, _OPTIMAL_MIX["instagram"])

    selected: dict[str, list[str]] = {}
    for tier_name, count in mix.items():
        pool = niche_data.get(tier_name, _NICHE_HASHTAGS["general"].get(tier_name, []))
        if include_general and tier_name in _NICHE_HASHTAGS["general"]:
            pool = list(dict.fromkeys(pool + _NICHE_HASHTAGS["general"][tier_name]))
        selected[tier_name] = [f"#{t}" for t in pool[:count]]

    # Inject custom tags into appropriate tiers
    if custom_tags:
        for tag in custom_tags:
            selected.setdefault("custom", []).append(
                f"#{tag.lstrip('#')}"
            )

    all_tags = [t for tags in selected.values() for t in tags]
    all_tags = list(dict.fromkeys(all_tags))  # deduplicate preserving order

    return {
        "by_tier": selected,
        "flat": all_tags,
        "copy_paste": " ".join(all_tags),
        "count": len(all_tags),
        "platform": platform,
        "niche": niche,
    }


def analyze_hashtag_set(tags: list[str], niche: str = "general") -> dict:
    """Analyze an existing hashtag set and give improvement advice."""
    niche_data = _NICHE_HASHTAGS.get(niche, _NICHE_HASHTAGS["general"])

    tier_counts: dict[str, int] = {t[0]: 0 for t in _TIERS}
    unknown: list[str] = []

    for tag in tags:
        tc = tag.lower().lstrip("#").strip()
        found = False
        for tier_name, tier_tags in niche_data.items():
            if tc in tier_tags:
                tier_counts[tier_name] = tier_counts.get(tier_name, 0) + 1
                found = True
                break
        if not found:
            unknown.append(tag)

    # Score vs optimal IG mix
    optimal = _OPTIMAL_MIX["instagram"]
    total_optimal = sum(optimal.values())
    total_current = len(tags)

    advice: list[str] = []
    for tier_name, ideal_count in optimal.items():
        current = tier_counts.get(tier_name, 0)
        ideal_pct = ideal_count / total_optimal
        if current < ideal_count:
            advice.append(f"Add {ideal_count - current} more {tier_name} hashtags")
        elif current > ideal_count * 2:
            advice.append(f"Too many {tier_name} hashtags — consider removing {current - ideal_count}")

    if total_current > 30:
        advice.append("Reduce to ≤30 hashtags on Instagram for best reach")
    if total_current < 10:
        advice.append("Add more hashtags — you're leaving reach on the table")

    return {
        "tag_count": total_current,
        "tier_distribution": tier_counts,
        "unknown_tags": unknown,
        "advice": advice,
        "diversity_score": round(len([v for v in tier_counts.values() if v > 0]) / 5 * 100, 1),
    }


def extract_hashtags(text: str) -> list[str]:
    """Parse hashtags from a caption or description."""
    return re.findall(r"#\w+", text)


def available_niches() -> list[str]:
    return sorted(_NICHE_HASHTAGS.keys())
