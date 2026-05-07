"""Hashtag analysis, scoring, and recommendation engine."""

import re
from collections import Counter
from typing import Optional


# Niche-to-seed-hashtag mapping for theme page research
NICHE_HASHTAGS: dict[str, list[str]] = {
    "motivation": ["#motivation", "#mindset", "#success", "#grindset", "#hustle", "#levelup", "#discipline", "#growthmindset", "#dailymotivation", "#inspire"],
    "fitness": ["#fitness", "#gymtok", "#workout", "#fitspo", "#gains", "#bodybuilding", "#weightloss", "#healthylifestyle", "#gymmotivation", "#fitcheck"],
    "luxury": ["#luxury", "#luxurylifestyle", "#millionairemindset", "#rich", "#wealthy", "#highend", "#luxe", "#baller", "#richlife", "#entrepreneur"],
    "aesthetic": ["#aesthetic", "#aestheticvibes", "#dark_aesthetic", "#aestheticroom", "#cottagecore", "#darkacademia", "#softgirl", "#cleanesthetic", "#moodboard", "#vibes"],
    "food": ["#foodtok", "#foodie", "#recipe", "#cooking", "#mukbang", "#foodasmr", "#tiktokfood", "#yummy", "#foodreview", "#whatieat"],
    "fashion": ["#fashion", "#ootd", "#style", "#fashiontok", "#outfitcheck", "#thrift", "#streetwear", "#grwm", "#fashionista", "#aesthetic"],
    "finance": ["#finance", "#investing", "#stockmarket", "#passiveincome", "#makemoneyonline", "#crypto", "#financialliteracy", "#moneytips", "#budgeting", "#wealthbuilding"],
    "travel": ["#travel", "#traveltok", "#wanderlust", "#explore", "#adventure", "#travellife", "#digitalnomad", "#backpacking", "#travelblogger", "#bucketlist"],
    "pets": ["#pettok", "#dogsoftiktok", "#catsoftiktok", "#pet", "#cute", "#animalsoftiktok", "#puppy", "#kitten", "#funnypets", "#fluffyanimals"],
    "gaming": ["#gaming", "#gamer", "#gamingsetup", "#twitch", "#streamer", "#fps", "#rpg", "#pcgaming", "#consolegaming", "#esports"],
    "beauty": ["#beauty", "#makeup", "#skincare", "#glam", "#beautytok", "#makeuptutorial", "#grwm", "#skincareroutine", "#blush", "#foundation"],
    "themepage": ["#themepage", "#reposter", "#curator", "#nichememe", "#nichepage", "#pagegrowth", "#pageflipping", "#themepages", "#contentcurator", "#passiveincome"],
}

# Engagement benchmarks per platform
ENGAGEMENT_BENCHMARKS = {
    "tiktok": {"poor": 0.02, "average": 0.05, "good": 0.10, "viral": 0.20},
    "youtube": {"poor": 0.01, "average": 0.03, "good": 0.06, "viral": 0.10},
    "instagram": {"poor": 0.01, "average": 0.03, "good": 0.06, "viral": 0.10},
}

# Hashtag size tiers (follower/post counts)
HASHTAG_TIERS = {
    "micro": (0, 100_000, "Micro — high reach-to-competition ratio, ideal for niche targeting"),
    "mid": (100_000, 1_000_000, "Mid — balanced visibility and competition"),
    "macro": (1_000_000, 10_000_000, "Macro — broad reach, high competition"),
    "mega": (10_000_000, float("inf"), "Mega — maximum reach, very competitive"),
}


def analyze_hashtags(
    hashtags: list[str],
    platform: str = "tiktok",
    niche: Optional[str] = None,
) -> dict:
    """
    Analyze a list of hashtags and return ranked recommendations.

    Scores each hashtag by frequency, suggests complementary tags,
    and classifies by size tier.
    """
    cleaned = [h.lower().lstrip("#") for h in hashtags if h]
    freq = Counter(cleaned)

    ranked = []
    for tag, count in freq.most_common():
        tier = _classify_tier(tag)
        ranked.append({
            "hashtag": f"#{tag}",
            "frequency": count,
            "tier": tier["name"],
            "tier_description": tier["description"],
            "recommended": tier["name"] in ("micro", "mid"),
        })

    # Suggest related hashtags from niche map
    suggestions = []
    if niche and niche.lower() in NICHE_HASHTAGS:
        existing = {f"#{h.lstrip('#').lower()}" for h in hashtags}
        for ht in NICHE_HASHTAGS[niche.lower()]:
            if ht.lower() not in existing:
                suggestions.append(ht)

    # Build optimal set: mix of tiers for maximum reach
    optimal_set = _build_optimal_set(ranked, niche)

    return {
        "platform": platform,
        "niche": niche,
        "total_analyzed": len(hashtags),
        "unique_hashtags": len(freq),
        "ranked_hashtags": ranked,
        "suggested_additions": suggestions[:15],
        "optimal_set": optimal_set,
        "strategy_tips": _hashtag_strategy_tips(platform),
    }


def get_niche_hashtags(niche: str, platform: str = "tiktok") -> dict:
    """Return the seed hashtag set for a specific niche."""
    niche_lower = niche.lower()
    if niche_lower not in NICHE_HASHTAGS:
        # Fuzzy match
        matches = [k for k in NICHE_HASHTAGS if niche_lower in k or k in niche_lower]
        if matches:
            niche_lower = matches[0]
        else:
            return {
                "niche": niche,
                "available_niches": list(NICHE_HASHTAGS.keys()),
                "hashtags": [],
                "error": f"Niche '{niche}' not found. Choose from available_niches.",
            }

    hashtags = NICHE_HASHTAGS[niche_lower]
    return {
        "niche": niche_lower,
        "platform": platform,
        "hashtags": hashtags,
        "count": len(hashtags),
        "usage_strategy": _hashtag_strategy_tips(platform),
        "optimal_set": _build_optimal_set(
            [{"hashtag": h, "frequency": 1, "tier": _classify_tier(h.lstrip("#"))["name"], "recommended": True} for h in hashtags],
            niche_lower,
        ),
    }


def recommend_for_content(
    description: str,
    platform: str = "tiktok",
    target_count: int = 20,
) -> dict:
    """Auto-recommend hashtags based on content description."""
    desc_lower = description.lower()
    matched_niches = []
    for niche, keywords in NICHE_HASHTAGS.items():
        if any(kw.lstrip("#").lower() in desc_lower for kw in keywords):
            matched_niches.append(niche)

    all_suggested: list[str] = []
    for niche in matched_niches[:3]:
        all_suggested.extend(NICHE_HASHTAGS[niche])

    # Always add universal high-performing tags
    universal = ["#fyp", "#foryou", "#foryoupage", "#viral", "#trending"]
    final_set = list(dict.fromkeys(all_suggested + universal))[:target_count]

    return {
        "content_description": description,
        "platform": platform,
        "detected_niches": matched_niches,
        "recommended_hashtags": final_set,
        "count": len(final_set),
        "copy_paste": " ".join(final_set),
    }


def _classify_tier(tag: str) -> dict:
    """Classify a hashtag by its rough size tier based on naming patterns."""
    tag = tag.lstrip("#").lower()
    # Heuristic: very generic short tags are mega, specific long tags are micro
    if len(tag) <= 4 or tag in ("fyp", "foryou", "viral", "trend", "love", "cute", "fun", "life"):
        return {"name": "mega", "description": HASHTAG_TIERS["mega"][2]}
    if len(tag) >= 15 or any(c.isdigit() for c in tag):
        return {"name": "micro", "description": HASHTAG_TIERS["micro"][2]}
    if any(word in tag for word in ["tiktok", "youtube", "instagram", "reel", "shorts"]):
        return {"name": "macro", "description": HASHTAG_TIERS["macro"][2]}
    return {"name": "mid", "description": HASHTAG_TIERS["mid"][2]}


def _build_optimal_set(ranked: list[dict], niche: Optional[str]) -> list[str]:
    """Build a balanced hashtag set mixing micro, mid, and macro tiers."""
    by_tier: dict[str, list[str]] = {"micro": [], "mid": [], "macro": [], "mega": []}
    for r in ranked:
        t = r.get("tier", "mid")
        by_tier[t].append(r["hashtag"])

    # Add niche seeds
    if niche and niche in NICHE_HASHTAGS:
        for ht in NICHE_HASHTAGS[niche]:
            tier = _classify_tier(ht)["name"]
            if ht not in by_tier[tier]:
                by_tier[tier].append(ht)

    # Target mix: 30% micro, 40% mid, 20% macro, 10% mega (TikTok/IG optimal)
    optimal = (
        by_tier["micro"][:6]
        + by_tier["mid"][:8]
        + by_tier["macro"][:4]
        + by_tier["mega"][:2]
    )
    return list(dict.fromkeys(optimal))[:20]


def _hashtag_strategy_tips(platform: str) -> list[str]:
    tips = {
        "tiktok": [
            "Use 3-5 niche hashtags + 2-3 mid-tier + #fyp for maximum discoverability.",
            "Avoid using ONLY #fyp — TikTok's algorithm prefers specific signals.",
            "Rotate your hashtag sets every 5-7 posts to avoid shadowbanning.",
            "Put your most important hashtag in the video caption, not just comments.",
            "Research competitor hashtags weekly — trends shift every 2-3 weeks.",
            "Use #duet, #stitch, #greenscreen to tap into existing viral content.",
        ],
        "youtube": [
            "Use 3-5 hashtags max in the description — YouTube penalizes stuffing.",
            "Put your primary hashtag in the video title for search boost.",
            "Use location-based hashtags (#NYCfood, #LAfitness) for local discovery.",
            "Year-based hashtags (#fitness2025) perform well in January.",
            "Hashtags in Shorts descriptions behave differently — use trending ones.",
        ],
        "instagram": [
            "Use 5-10 highly relevant hashtags in the first comment for cleaner captions.",
            "Mix 3 tiers: 2-3 mega (1M+), 3-4 macro (100k-1M), 3-4 micro (<100k).",
            "Create a branded hashtag and encourage followers to use it.",
            "Stories hashtags are indexed separately — always add 1-2.",
            "Reels hashtags follow TikTok patterns — niche + broad works best.",
        ],
    }
    return tips.get(platform.lower(), tips["tiktok"])
