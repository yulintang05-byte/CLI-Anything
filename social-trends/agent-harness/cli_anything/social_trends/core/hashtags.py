"""Social Trends - Hashtag research, scoring, and set generation."""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from cli_anything.social_trends.core.session import Session

# Hashtag tier thresholds (approximate post count ranges)
HASHTAG_TIERS = {
    "mega":   {"min": 1_000_000_000, "max": None,          "label": "mega (1B+)", "competition": "extreme"},
    "macro":  {"min": 100_000_000,   "max": 1_000_000_000, "label": "macro (100M-1B)", "competition": "very high"},
    "large":  {"min": 10_000_000,    "max": 100_000_000,   "label": "large (10M-100M)", "competition": "high"},
    "mid":    {"min": 1_000_000,     "max": 10_000_000,    "label": "mid (1M-10M)", "competition": "medium"},
    "micro":  {"min": 100_000,       "max": 1_000_000,     "label": "micro (100K-1M)", "competition": "low"},
    "niche":  {"min": 0,             "max": 100_000,       "label": "niche (<100K)", "competition": "very low"},
}

# Platform-specific hashtag limits and recommendations
PLATFORM_HASHTAG_RULES = {
    "tiktok": {
        "max_hashtags": 5,
        "optimal_hashtags": 3,
        "caption_limit": 2200,
        "strategy": "Use 1 broad + 1 trending + 1-2 niche tags",
    },
    "instagram": {
        "max_hashtags": 30,
        "optimal_hashtags": 20,
        "caption_limit": 2200,
        "strategy": "Mix of mega, macro, mid, and niche tags",
    },
    "youtube": {
        "max_hashtags": 15,
        "optimal_hashtags": 8,
        "caption_limit": 5000,
        "strategy": "Use descriptive + trending + searchable tags",
    },
    "twitter": {
        "max_hashtags": 3,
        "optimal_hashtags": 2,
        "caption_limit": 280,
        "strategy": "1-2 trending or branded tags maximum",
    },
}

# Niche hashtag databases (curated sets for common niches)
NICHE_HASHTAG_DB: Dict[str, Dict[str, List[str]]] = {
    "fitness": {
        "mega":  ["#fitness", "#gym", "#workout", "#motivation", "#fit"],
        "macro": ["#fitnessmotivation", "#gymlife", "#bodybuilding", "#training", "#exercise"],
        "mid":   ["#fitfam", "#workoutmotivation", "#fitnesstips", "#strengthtraining", "#cardio"],
        "niche": ["#homeworkout", "#calisthenics", "#functionalfitness", "#hiitworkout", "#crossfit"],
    },
    "food": {
        "mega":  ["#food", "#foodie", "#foodporn", "#instafood", "#yummy"],
        "macro": ["#foodlover", "#homecooking", "#recipe", "#cooking", "#delicious"],
        "mid":   ["#foodphotography", "#mealprep", "#healthyfood", "#foodblogger", "#easyrecipes"],
        "niche": ["#mealprepping", "#weeknightdinner", "#glutenfree", "#plantbased", "#airfryer"],
    },
    "fashion": {
        "mega":  ["#fashion", "#style", "#ootd", "#outfitoftheday", "#clothing"],
        "macro": ["#fashionblogger", "#streetstyle", "#fashionstyle", "#outfitinspiration", "#styleguide"],
        "mid":   ["#fashionista", "#lookoftheday", "#styletips", "#whatiwore", "#capsulewardrobe"],
        "niche": ["#thriftedoutfit", "#sustainablefashion", "#vintagestyle", "#slowfashion", "#minimalstyle"],
    },
    "beauty": {
        "mega":  ["#beauty", "#makeup", "#skincare", "#beautytips", "#glam"],
        "macro": ["#makeuptutorial", "#makeuplover", "#skincareroutine", "#beautyhacks", "#glowup"],
        "mid":   ["#beautyblogger", "#makeupoftheday", "#skincareproducts", "#dewyglam", "#cleanbeauty"],
        "niche": ["#sluggingmethod", "#glasskin", "#undereyepatches", "#micellarwater", "#koreanbeauty"],
    },
    "travel": {
        "mega":  ["#travel", "#wanderlust", "#adventure", "#explore", "#travelphotography"],
        "macro": ["#travelgram", "#traveling", "#traveler", "#vacation", "#holiday"],
        "mid":   ["#travelblogger", "#travellife", "#travelphoto", "#traveltips", "#travelcouple"],
        "niche": ["#solotravel", "#budgettravel", "#digitalnomadfam", "#vanlife", "#offbeatenpath"],
    },
    "finance": {
        "mega":  ["#money", "#finance", "#investing", "#wealth", "#personalfinance"],
        "macro": ["#financialfreedom", "#passiveincome", "#investment", "#moneymanagement", "#debtfree"],
        "mid":   ["#financetips", "#stockmarket", "#budgeting", "#savingmoney", "#buildingwealth"],
        "niche": ["#indexfunds", "#dividendinvesting", "#realestateinvesting", "#frugalliving", "#coastfire"],
    },
    "gaming": {
        "mega":  ["#gaming", "#gamer", "#games", "#videogames", "#esports"],
        "macro": ["#gamingcommunity", "#pcgaming", "#streamer", "#twitch", "#ps5"],
        "mid":   ["#gamingsetup", "#gamerlife", "#gamingmemes", "#consolegaming", "#mobilegaming"],
        "niche": ["#indiegames", "#retrogaming", "#rpggames", "#speedrun", "#completionist"],
    },
    "motivation": {
        "mega":  ["#motivation", "#inspiration", "#success", "#mindset", "#goals"],
        "macro": ["#motivationalquotes", "#inspirationalquotes", "#successmindset", "#hustle", "#grind"],
        "mid":   ["#dailymotivation", "#positivevibes", "#selfdevelopment", "#growthmindset", "#entrepreneurmindset"],
        "niche": ["#morningaffirmations", "#neuroplasticity", "#stoicism", "#atomichabits", "#deepwork"],
    },
    "luxury": {
        "mega":  ["#luxury", "#lifestyle", "#rich", "#wealth", "#millionaire"],
        "macro": ["#luxurylife", "#luxurylifestyle", "#luxurycars", "#luxuryhomes", "#highlife"],
        "mid":   ["#luxurytravel", "#luxuryfashion", "#supercars", "#privatejet", "#yachtlife"],
        "niche": ["#hypercars", "#watchcollector", "#couture", "#ultraluxury", "#blackcard"],
    },
}


def research_hashtags(
    session: Session,
    topic: str,
    platform: str = "tiktok",
    limit: int = 30,
) -> Dict[str, Any]:
    """Research and return hashtags for a given topic."""
    project = session.get_project()
    niche = topic.lower()

    # Check niche DB first
    db_tags = _get_db_tags(niche, limit)

    # Extract from cached trends
    trend_tags = _extract_from_trends(project, niche)

    # Merge and score
    all_tags = _merge_and_score(db_tags, trend_tags, platform)

    rules = PLATFORM_HASHTAG_RULES.get(platform, PLATFORM_HASHTAG_RULES["tiktok"])

    return {
        "topic": topic,
        "platform": platform,
        "total_found": len(all_tags),
        "platform_rules": rules,
        "hashtags": all_tags[:limit],
        "recommended_mix": _recommended_mix(all_tags, platform),
    }


def score_hashtag(tag: str) -> Dict[str, Any]:
    """Return tier classification and usage guidance for a hashtag."""
    tag = tag.lower().lstrip("#")

    # Check all niche DBs
    for niche, tiers in NICHE_HASHTAG_DB.items():
        for tier_name, tags in tiers.items():
            if f"#{tag}" in tags or tag in [t.lstrip("#") for t in tags]:
                tier_info = HASHTAG_TIERS.get(tier_name, {})
                return {
                    "tag": f"#{tag}",
                    "niche": niche,
                    "tier": tier_name,
                    "tier_label": tier_info.get("label", tier_name),
                    "competition": tier_info.get("competition", "unknown"),
                    "recommendation": _tier_recommendation(tier_name),
                }

    return {
        "tag": f"#{tag}",
        "niche": "general",
        "tier": "unknown",
        "tier_label": "unclassified",
        "competition": "unknown",
        "recommendation": "No data. Try researching via the trends commands first.",
    }


def generate_hashtag_set(
    session: Session,
    niche: str,
    platform: str = "tiktok",
    mix: str = "balanced",
    set_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a ready-to-use hashtag set for a niche and platform."""
    project = session.get_project()
    rules = PLATFORM_HASHTAG_RULES.get(platform, PLATFORM_HASHTAG_RULES["tiktok"])
    optimal = rules["optimal_hashtags"]

    db_tags = NICHE_HASHTAG_DB.get(niche.lower(), {})
    if not db_tags:
        # Fallback: use motivation if niche unknown
        db_tags = NICHE_HASHTAG_DB.get("motivation", {})

    if mix == "aggressive":
        selection = _select_aggressive(db_tags, optimal)
    elif mix == "safe":
        selection = _select_safe(db_tags, optimal)
    else:
        selection = _select_balanced(db_tags, optimal)

    # Add trending tags from cached data
    trend_tags = _extract_from_trends(project, niche)[:2]
    for t in trend_tags:
        if t["tag"] not in selection and len(selection) < rules["max_hashtags"]:
            selection.append(t["tag"])

    set_data: Dict[str, Any] = {
        "id": str(uuid.uuid4())[:8],
        "name": set_name or f"{niche}_{platform}_{mix}",
        "niche": niche,
        "platform": platform,
        "mix_strategy": mix,
        "hashtags": selection,
        "count": len(selection),
        "platform_limit": rules["max_hashtags"],
        "strategy_tip": rules["strategy"],
        "caption_ready": " ".join(selection),
    }

    session.snapshot(f"generate hashtag set {set_data['name']}")
    project.setdefault("hashtag_sets", []).append(set_data)

    return set_data


def list_hashtag_sets(session: Session) -> List[Dict[str, Any]]:
    """List all saved hashtag sets."""
    project = session.get_project()
    return project.get("hashtag_sets", [])


def _get_db_tags(niche: str, limit: int) -> List[Dict[str, Any]]:
    db = NICHE_HASHTAG_DB.get(niche)
    if not db:
        # Fuzzy match: find closest niche
        for key in NICHE_HASHTAG_DB:
            if key in niche or niche in key:
                db = NICHE_HASHTAG_DB[key]
                break
    if not db:
        return []

    result = []
    tier_priority = ["mid", "niche", "macro", "large", "mega"]
    for tier in tier_priority:
        for tag in db.get(tier, []):
            result.append({
                "tag": tag,
                "tier": tier,
                "tier_label": HASHTAG_TIERS[tier]["label"],
                "competition": HASHTAG_TIERS[tier]["competition"],
                "source": "database",
            })
    return result[:limit]


def _extract_from_trends(project: Dict[str, Any], niche: str) -> List[Dict[str, Any]]:
    """Extract relevant hashtags from cached trend data."""
    freq: Dict[str, int] = {}
    for trend in project.get("trends", []):
        title = trend.get("title", "").lower()
        if niche not in title and niche not in " ".join(trend.get("hashtags", [])).lower():
            continue
        for tag in trend.get("hashtags", []):
            tag = tag.lower()
            freq[tag] = freq.get(tag, 0) + 1

    return [
        {"tag": tag, "tier": "trending", "tier_label": "trending", "competition": "varies", "source": "trends", "frequency": count}
        for tag, count in sorted(freq.items(), key=lambda x: x[1], reverse=True)
    ]


def _merge_and_score(
    db_tags: List[Dict[str, Any]],
    trend_tags: List[Dict[str, Any]],
    platform: str,
) -> List[Dict[str, Any]]:
    seen = set()
    merged = []
    for tag in trend_tags + db_tags:
        t = tag["tag"]
        if t not in seen:
            seen.add(t)
            merged.append(tag)
    return merged


def _recommended_mix(tags: List[Dict[str, Any]], platform: str) -> Dict[str, Any]:
    rules = PLATFORM_HASHTAG_RULES.get(platform, PLATFORM_HASHTAG_RULES["tiktok"])
    optimal = rules["optimal_hashtags"]

    by_tier: Dict[str, List[str]] = {}
    for tag in tags:
        tier = tag.get("tier", "niche")
        by_tier.setdefault(tier, []).append(tag["tag"])

    recommended: List[str] = []
    # For balanced mix: 1 mega/macro + some mid + mostly niche/micro
    for tier in ["mega", "macro", "large", "mid", "micro", "niche", "trending"]:
        pool = by_tier.get(tier, [])
        if pool and len(recommended) < optimal:
            take = max(1, min(len(pool), optimal // max(1, len(HASHTAG_TIERS))))
            recommended.extend(pool[:take])

    return {
        "tags": recommended[:optimal],
        "count": min(len(recommended), optimal),
        "target": optimal,
        "strategy": rules["strategy"],
    }


def _select_balanced(db_tags: Dict[str, List[str]], n: int) -> List[str]:
    result = []
    tiers = ["mid", "niche", "micro", "macro", "large", "mega"]
    per_tier = max(1, n // len(tiers))
    for tier in tiers:
        result.extend(db_tags.get(tier, [])[:per_tier])
    return list(dict.fromkeys(result))[:n]


def _select_aggressive(db_tags: Dict[str, List[str]], n: int) -> List[str]:
    """Aggressive: more mega/macro for reach."""
    result = []
    for tier in ["mega", "macro", "large", "mid", "niche"]:
        result.extend(db_tags.get(tier, []))
    return list(dict.fromkeys(result))[:n]


def _select_safe(db_tags: Dict[str, List[str]], n: int) -> List[str]:
    """Safe: more niche/micro for discoverability."""
    result = []
    for tier in ["niche", "micro", "mid", "macro", "large"]:
        result.extend(db_tags.get(tier, []))
    return list(dict.fromkeys(result))[:n]


def _tier_recommendation(tier: str) -> str:
    recs = {
        "mega":  "Very high competition. Use sparingly (1 per set). Good for brand awareness only.",
        "macro": "High competition. Mix with niche tags. Use 1-2 per set.",
        "large": "Medium-high competition. Good for reach in established niches.",
        "mid":   "Balanced reach vs competition. Core of most hashtag sets.",
        "micro": "Low competition. High discoverability for new accounts.",
        "niche": "Very low competition. Best for niche communities and new accounts.",
    }
    return recs.get(tier, "No specific recommendation.")
