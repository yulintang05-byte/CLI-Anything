"""Hashtag optimization engine.

Generates optimal hashtag sets for any niche, platform, and content type.
Scores hashtag mixes by competition, reach, and relevance.
"""

from dataclasses import dataclass
from typing import Optional


NICHE_HASHTAG_SETS = {
    "fitness": {
        "mega": ["#fitness", "#gym", "#workout", "#fitspo", "#fitnessmotivation"],
        "mid": ["#gymtok", "#gymlife", "#workoutmotivation", "#fitnessjourney", "#liftingweights"],
        "niche": ["#homeWorkout", "#legday", "#pullday", "#physique", "#natty"],
        "trending_june_2026": ["#SummerBody2026", "#GymTok", "#fitness"],
    },
    "finance": {
        "mega": ["#money", "#finance", "#investing", "#wealth", "#personalfinance"],
        "mid": ["#financetok", "#moneytips", "#stockmarket", "#budgeting", "#financialfreedom"],
        "niche": ["#dividendinvesting", "#indexfunds", "#debtfree", "#FIRE", "#passiveincome"],
        "trending_june_2026": ["#sidehustle", "#passiveincome2026", "#wealthmindset"],
    },
    "business": {
        "mega": ["#business", "#entrepreneur", "#startup", "#marketing", "#success"],
        "mid": ["#businesstips", "#entrepreneurship", "#smallbusiness", "#ceo", "#hustle"],
        "niche": ["#solopreneur", "#contentcreator", "#dropshipping", "#ecommerce", "#agencylife"],
        "trending_june_2026": ["#smallbusiness", "#entrepreneurmindset", "#ai"],
    },
    "lifestyle": {
        "mega": ["#lifestyle", "#motivation", "#inspiration", "#mindset", "#selfimprovement"],
        "mid": ["#morningroutine", "#selfcare", "#productivity", "#growthmindset", "#dailyroutine"],
        "niche": ["#minimalist", "#slowliving", "#intentionalliving", "#wellnessjourney", "#morningperson"],
        "trending_june_2026": ["#SummerVibes2026", "#aesthetic", "#dayinmylife"],
    },
    "food": {
        "mega": ["#food", "#foodie", "#cooking", "#recipe", "#foodtok"],
        "mid": ["#homecooking", "#easyrecipes", "#mealprep", "#foodphotography", "#cheflife"],
        "niche": ["#30minutemeals", "#budgetmeals", "#highprotein", "#cleaneating", "#airfryer"],
        "trending_june_2026": ["#foodtok", "#recipe2026", "#easyrecipes"],
    },
    "tech": {
        "mega": ["#tech", "#technology", "#ai", "#innovation", "#coding"],
        "mid": ["#techtok", "#programming", "#softwareengineering", "#aitools", "#productivity"],
        "niche": ["#chatgpt", "#machinelearning", "#developerlife", "#buildinpublic", "#saas"],
        "trending_june_2026": ["#ai", "#aitools2026", "#futuretech"],
    },
    "entertainment": {
        "mega": ["#entertainment", "#trending", "#viral", "#funny", "#comedy"],
        "mid": ["#sketch", "#memes", "#storytime", "#relatable", "#humor"],
        "niche": ["#animereaction", "#moviereview", "#musicreaction", "#popculture", "#reactionvideo"],
        "trending_june_2026": ["#HouseOfTheDragon", "#OliviaRodrigo", "#LoveIsland2026"],
    },
    "sports": {
        "mega": ["#sports", "#football", "#soccer", "#basketball", "#fyp"],
        "mid": ["#highlights", "#sportsbet", "#sportstok", "#athlete", "#sportsmotivation"],
        "niche": ["#WorldCup2026", "#FIFA", "#MLS", "#Premier League", "#Champions League"],
        "trending_june_2026": ["#WorldCup2026", "#FIFA2026", "#PRESSURE"],
    },
    "beauty": {
        "mega": ["#beauty", "#makeup", "#skincare", "#fashion", "#style"],
        "mid": ["#makeuptutorial", "#glowup", "#skincareroutine", "#ootd", "#beautytips"],
        "niche": ["#drugstorebeauty", "#antiaging", "#cleanbeauty", "#glassskin", "#melanin"],
        "trending_june_2026": ["#SummerMakeup", "#glowup2026", "#skincare"],
    },
    "general": {
        "mega": ["#viral", "#fyp", "#foryou", "#trending", "#foryoupage"],
        "mid": ["#explore", "#reels", "#content", "#creator", "#socialmedia"],
        "niche": ["#contentcreator", "#digitalmarketing", "#growthhacks", "#algorithm", "#newcreator"],
        "trending_june_2026": ["#WorldCup2026", "#fyp", "#viral"],
    },
}

PLATFORM_RULES = {
    "tiktok": {
        "optimal_count": 5,
        "max": 10,
        "formula": "1 mega + 2 mid + 1 niche + 1 trending",
        "placement": "Caption (not separate comment)",
        "note": "TikTok algorithm reads hashtags as content signals — be accurate to niche",
    },
    "youtube": {
        "optimal_count": 4,
        "max": 8,
        "formula": "1 mega + 1 niche + 1 trending + #Shorts",
        "placement": "Description first 5 lines OR title (one only)",
        "note": "Always include #Shorts for YouTube Shorts distribution",
    },
    "instagram": {
        "optimal_count": 5,
        "max": 10,
        "formula": "2 niche + 1 mid + 1 trending + 1 location (optional)",
        "placement": "Caption (end of caption, after line breaks)",
        "note": "Instagram 2026: fewer, more relevant hashtags outperform hashtag dumps",
    },
}


def generate_hashtag_set(
    niche: str,
    platform: str = "tiktok",
    include_trending: bool = True,
    count: Optional[int] = None,
) -> dict:
    """Generate an optimized hashtag set for a given niche and platform."""
    niche_key = _match_niche(niche)
    tags = NICHE_HASHTAG_SETS.get(niche_key, NICHE_HASHTAG_SETS["general"])
    rules = PLATFORM_RULES.get(platform.lower(), PLATFORM_RULES["tiktok"])

    optimal = rules["optimal_count"]
    if count:
        optimal = min(count, rules["max"])

    selected = []
    # Always grab at least one mega tag
    if tags["mega"]:
        selected.append(tags["mega"][0])
    # Fill from mid tier
    for t in tags["mid"][:2]:
        if len(selected) < optimal - 2:
            selected.append(t)
    # Add trending
    if include_trending and tags["trending_june_2026"]:
        selected.append(tags["trending_june_2026"][0])
    # Add niche micro-tag last
    if tags["niche"]:
        selected.append(tags["niche"][0])
    # Pad to optimal if needed
    while len(selected) < optimal:
        for pool in [tags["mid"], tags["niche"], tags["mega"]]:
            for t in pool:
                if t not in selected and len(selected) < optimal:
                    selected.append(t)

    selected = selected[:optimal]

    # YouTube always needs #Shorts
    if platform.lower() == "youtube" and "#Shorts" not in selected and "#shorts" not in selected:
        if len(selected) >= optimal:
            selected[-1] = "#Shorts"
        else:
            selected.append("#Shorts")

    return {
        "platform": platform,
        "niche": niche,
        "hashtags": selected,
        "formatted": " ".join(selected),
        "count": len(selected),
        "strategy": rules["formula"],
        "placement_tip": rules["placement"],
        "platform_note": rules["note"],
        "full_pool": {
            "mega": tags["mega"],
            "mid": tags["mid"],
            "niche": tags["niche"],
            "trending_june_2026": tags["trending_june_2026"],
        },
    }


def _match_niche(niche: str) -> str:
    """Fuzzy-match user input to a niche key."""
    niche_lower = niche.lower()
    mapping = {
        "fitness": ["fit", "gym", "workout", "health", "exercise", "training"],
        "finance": ["finance", "money", "invest", "wealth", "budget", "stock", "crypto"],
        "business": ["business", "entrepreneur", "startup", "ceo", "marketing", "ecom"],
        "lifestyle": ["lifestyle", "motivation", "mindset", "routine", "self", "personal"],
        "food": ["food", "cook", "recipe", "eat", "chef", "meal", "restaurant"],
        "tech": ["tech", "ai", "code", "software", "program", "dev", "computer", "saas"],
        "entertainment": ["entertainment", "funny", "comedy", "meme", "anime", "movie", "music"],
        "sports": ["sport", "football", "soccer", "basketball", "baseball", "fifa", "world cup"],
        "beauty": ["beauty", "makeup", "skincare", "fashion", "style", "hair", "nails"],
    }
    for key, keywords in mapping.items():
        if any(kw in niche_lower for kw in keywords):
            return key
    return "general"
