"""Hashtag analysis, scoring, and niche-specific recommendation engine.

Contains a curated knowledge base of viral hashtags organized by niche,
competition tier, and platform. All data is current as of May 2026.
"""

from __future__ import annotations
import re
from typing import Literal

# ── Niche hashtag database ────────────────────────────────────────────────────
# Structure: niche -> tier -> list of hashtags
# Tiers: mega (100M+ posts), large (10M+), medium (1M+), niche (<1M)
# Using a mix of tiers gives the algorithm signal while avoiding pure competition.

NICHE_HASHTAGS: dict[str, dict[str, list[str]]] = {
    "fitness": {
        "mega":   ["#fitness", "#gym", "#workout", "#health", "#motivation", "#fit", "#bodybuilding", "#exercise"],
        "large":  ["#fitnessmotivation", "#personaltrainer", "#gymlife", "#gains", "#fitfam", "#strengthtraining"],
        "medium": ["#homeworkout", "#fitnesstips", "#gymtok", "#weightloss", "#musclebuilding", "#fitcheck"],
        "niche":  ["#girlswholift", "#calisthenics", "#powerlifting", "#crossfit", "#75hard", "#pilatesreformer"],
    },
    "food": {
        "mega":   ["#food", "#foodie", "#recipe", "#cooking", "#delicious", "#yummy", "#eat", "#foodporn"],
        "large":  ["#foodtok", "#healthyfood", "#homecooking", "#foodlover", "#instafood", "#tasty"],
        "medium": ["#easyrecipes", "#mealprep", "#whatieatinaday", "#mukbang", "#cookingvideo", "#dinnerideas"],
        "niche":  ["#highproteinmeals", "#veganrecipes", "#keto", "#glutenfree", "#batchcooking", "#budgetmeals"],
    },
    "fashion": {
        "mega":   ["#fashion", "#style", "#ootd", "#outfit", "#clothing", "#streetstyle", "#fashionista"],
        "large":  ["#outfitcheck", "#fitcheck", "#fashiontok", "#lookbook", "#styleblogger", "#mensfashion"],
        "medium": ["#thriftflip", "#thrifted", "#wiwt", "#streetwear", "#vintagestyle", "#capsulewardrobe"],
        "niche":  ["#slowfashion", "#sustainablefashion", "#fashionhacks", "#outfitinspo", "#preppy", "#darkacademia"],
    },
    "beauty": {
        "mega":   ["#makeup", "#beauty", "#skincare", "#makeuptutorial", "#glam", "#cosmetics", "#lipstick"],
        "large":  ["#makeuplook", "#skincareroutine", "#beautytok", "#glowup", "#makeupbeginner", "#selfcare"],
        "medium": ["#nailcheck", "#hairtok", "#hairtransformation", "#grwm", "#getreadywithme", "#dewyskin"],
        "niche":  ["#cleanskincare", "#slugging", "#glazeddonutskin", "#k-beauty", "#skintok", "#nailart"],
    },
    "lifestyle": {
        "mega":   ["#lifestyle", "#life", "#love", "#happy", "#inspo", "#aesthetic", "#vibe", "#positivevibes"],
        "large":  ["#dailyvlog", "#dayinmylife", "#slowliving", "#romanticizeyourlife", "#softlife"],
        "medium": ["#morningroutine", "#nightroutine", "#productivityhacks", "#organization", "#cleantok"],
        "niche":  ["#cottagecore", "#goblincore", "#darkacademia", "#minimalism", "#intentionalliving"],
    },
    "money": {
        "mega":   ["#money", "#finance", "#investing", "#crypto", "#business", "#entrepreneur", "#wealth"],
        "large":  ["#personalfinance", "#sidehustle", "#passiveincome", "#moneytips", "#stockmarket", "#financetok"],
        "medium": ["#financialtips", "#budgeting", "#savingmoney", "#financialfreedom", "#realestate"],
        "niche":  ["#dividendinvesting", "#indexfunds", "#frugal", "#debtfree", "#FIRE", "#dropshipping"],
    },
    "travel": {
        "mega":   ["#travel", "#wanderlust", "#travelphotography", "#adventure", "#explore", "#vacation"],
        "large":  ["#traveltok", "#travellife", "#travelgram", "#backpacking", "#solotravel", "#roadtrip"],
        "medium": ["#travelwithme", "#hiddengems", "#budgettravel", "#luxurytravel", "#digitalnomad"],
        "niche":  ["#slowtravel", "#vanlife", "#workandtravel", "#europeantravel", "#asiatravel"],
    },
    "gaming": {
        "mega":   ["#gaming", "#gamer", "#games", "#videogames", "#ps5", "#xbox", "#pc", "#twitch"],
        "large":  ["#gamingsetup", "#gamertok", "#fps", "#esports", "#streamer", "#gamingcommunity"],
        "medium": ["#minecraft", "#fortnite", "#valorant", "#leagueoflegends", "#rpg", "#indiegames"],
        "niche":  ["#retrogaming", "#gamingroom", "#pcbuilding", "#vrgaming", "#mobilegaming"],
    },
    "motivation": {
        "mega":   ["#motivation", "#success", "#mindset", "#inspiration", "#goals", "#hustle", "#grind"],
        "large":  ["#selfdevelopment", "#growthmindset", "#discipline", "#hardwork", "#mindfulness"],
        "medium": ["#levelup", "#personalgrowth", "#selfimprovement", "#manifestation", "#affirmations"],
        "niche":  ["#stoicism", "#mentalstrength", "#morningmotivation", "#successmindset", "#dopaminedetox"],
    },
    "education": {
        "mega":   ["#learnontiktok", "#education", "#learning", "#school", "#knowledge", "#tips"],
        "large":  ["#edutok", "#didyouknow", "#lifehacks", "#protips", "#funfacts", "#sciencetok"],
        "medium": ["#studytok", "#studywithme", "#languagelearning", "#mathisfun", "#historytok"],
        "niche":  ["#psychologytips", "#philosophytok", "#cognitivebiases", "#criticalthinking"],
    },
    "pets": {
        "mega":   ["#pets", "#dog", "#cat", "#puppy", "#kitten", "#animals", "#cute", "#animalsoftiktok"],
        "large":  ["#dogtok", "#cattok", "#dogsofinstagram", "#catsofinstagram", "#petlover", "#funnypets"],
        "medium": ["#dogtraining", "#petcare", "#petlife", "#smalldog", "#bigdog", "#rescuedog"],
        "niche":  ["#exoticpets", "#reptiles", "#bunnytok", "#birdsoftiktok", "#hamster"],
    },
    "music": {
        "mega":   ["#music", "#song", "#singing", "#musician", "#newmusic", "#pop", "#hiphop", "#rnb"],
        "large":  ["#musictok", "#original", "#cover", "#producer", "#rapper", "#guitarist", "#piano"],
        "medium": ["#indiepop", "#lofi", "#beats", "#soundcloud", "#unsigned", "#musicproduction"],
        "niche":  ["#jazzpiano", "#classicalmusic", "#folkmusic", "#soulmusic", "#undergroundhiphop"],
    },
    "luxury": {
        "mega":   ["#luxury", "#rich", "#lifestyle", "#expensive", "#millionaire"],
        "large":  ["#luxuryliving", "#luxurylifestyle", "#highend", "#eliteliving", "#luxurycars"],
        "medium": ["#luxurywatch", "#designerlife", "#privatejet", "#luxuryhotel", "#penthouseliving"],
        "niche":  ["#watchcollector", "#rolexwatch", "#hypercar", "#luxuryyacht", "#artcollector"],
    },
    "real_estate": {
        "mega":   ["#realestate", "#house", "#home", "#property", "#investing"],
        "large":  ["#realestateagent", "#househunting", "#homebuying", "#realestateinvesting", "#mortgage"],
        "medium": ["#housetour", "#homeremodel", "#interiordesign", "#architecture", "#hometips"],
        "niche":  ["#wholesalingrealestate", "#houseflipping", "#rentalincome", "#proptech", "#reits"],
    },
}

# Platform-specific boost tags (always include a few)
PLATFORM_BOOST: dict[str, list[str]] = {
    "tiktok":    ["#fyp", "#foryou", "#foryoupage", "#viral", "#trending", "#CapCut"],
    "instagram": ["#reels", "#explore", "#instadaily", "#instagram", "#instagood", "#photooftheday"],
    "youtube":   ["#shorts", "#youtubeshorts", "#youtube", "#subscribe"],
}


def suggest_hashtags(
    niche: str,
    platform: Literal["tiktok", "instagram", "youtube", "all"] = "tiktok",
    count: int = 30,
    include_boost: bool = True,
) -> dict:
    """Generate an optimized hashtag set for a niche.

    Mixes mega/large/medium/niche tags for maximum reach + discovery.
    Optimal ratio: 20% mega, 30% large, 30% medium, 20% niche.

    Args:
        niche: Content niche (e.g. "fitness", "food", "money")
        platform: Target platform for boost tags
        count: Total hashtags to return
        include_boost: Include platform boost tags

    Returns:
        Dict with hashtags, tiers_used, strategy_note
    """
    niche_data = _find_niche(niche)
    if not niche_data:
        return {
            "error": f"Niche '{niche}' not found.",
            "available_niches": list_niches(),
        }

    # Calculate tier quotas
    mega_n  = max(1, int(count * 0.15))
    large_n = max(2, int(count * 0.25))
    med_n   = max(2, int(count * 0.30))
    niche_n = max(2, int(count * 0.20))
    boost_n = max(3, int(count * 0.10)) if include_boost else 0

    selected: list[str] = []
    tiers_used: dict[str, list[str]] = {}

    for tier_name, quota in [("mega", mega_n), ("large", large_n), ("medium", med_n), ("niche", niche_n)]:
        tier_tags = niche_data.get(tier_name, [])[:quota]
        selected.extend(tier_tags)
        tiers_used[tier_name] = tier_tags

    if include_boost and platform != "all":
        boost = PLATFORM_BOOST.get(platform, [])[:boost_n]
        selected = boost + selected
        tiers_used["platform_boost"] = boost

    # Deduplicate, preserving order
    seen: set[str] = set()
    deduped = []
    for tag in selected:
        tl = tag.lower()
        if tl not in seen:
            seen.add(tl)
            deduped.append(tag)

    final = deduped[:count]

    return {
        "niche": niche,
        "platform": platform,
        "hashtags": final,
        "count": len(final),
        "tiers": tiers_used,
        "strategy_note": (
            f"Mix of {len(tiers_used.get('mega', []))} mega + "
            f"{len(tiers_used.get('large', []))} large + "
            f"{len(tiers_used.get('medium', []))} medium + "
            f"{len(tiers_used.get('niche', []))} niche tags "
            f"+ {len(tiers_used.get('platform_boost', []))} platform boost tags."
        ),
        "caption_ready": " ".join(final),
    }


def score_hashtag(tag: str) -> dict:
    """Score a hashtag's characteristics and virality potential.

    Args:
        tag: Hashtag with or without # prefix

    Returns:
        Dict with score (0-100), tier_guess, recommendations
    """
    tag = tag.lstrip("#").lower()
    length = len(tag)
    has_numbers = bool(re.search(r"\d", tag))
    word_count = len(re.findall(r"[A-Z][a-z]+|[a-z]+", tag))

    # Check which tier it appears in across all niches
    tier_hits: list[str] = []
    niches_found: list[str] = []
    for niche_name, tiers in NICHE_HASHTAGS.items():
        for tier, tags in tiers.items():
            if f"#{tag}" in tags or tag in [t.lstrip("#") for t in tags]:
                tier_hits.append(tier)
                niches_found.append(niche_name)

    score = 50  # baseline
    recommendations: list[str] = []

    if "mega" in tier_hits:
        score = 95
        recommendations.append("Mega-viral tag — high competition, use sparingly (1-2 max).")
    elif "large" in tier_hits:
        score = 80
        recommendations.append("Large tag — good reach, include 3-4.")
    elif "medium" in tier_hits:
        score = 65
        recommendations.append("Medium tag — solid discovery vehicle, great backbone.")
    elif "niche" in tier_hits:
        score = 55
        recommendations.append("Niche tag — lower competition, high intent audience.")

    if length < 5:
        score -= 10
        recommendations.append("Very short — may be too generic.")
    elif 8 <= length <= 18:
        score += 5
    elif length > 30:
        score -= 5
        recommendations.append("Very long hashtag — harder to remember.")

    if has_numbers and tag not in ["75hard", "1000xclub"]:
        score -= 5
        recommendations.append("Numbers in hashtags can reduce algorithmic reach.")

    return {
        "hashtag": f"#{tag}",
        "score": max(0, min(100, score)),
        "tier": tier_hits[0] if tier_hits else "unknown",
        "niches": niches_found,
        "length": length,
        "recommendations": recommendations,
    }


def analyze_hashtag_set(tags: list[str]) -> dict:
    """Analyze a set of hashtags for balance and effectiveness.

    Args:
        tags: List of hashtags

    Returns:
        Dict with analysis, tier_breakdown, missing_tiers, score
    """
    scored = [score_hashtag(t) for t in tags]
    tier_counts: dict[str, int] = {}
    for s in scored:
        tier = s["tier"]
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    total = len(tags)
    avg_score = sum(s["score"] for s in scored) / total if total else 0

    missing = []
    if not tier_counts.get("mega"):
        missing.append("mega (add 1-2 for broad reach)")
    if not tier_counts.get("niche"):
        missing.append("niche (add 3-5 for targeted discovery)")

    return {
        "total": total,
        "avg_score": round(avg_score, 1),
        "tier_breakdown": tier_counts,
        "missing_tiers": missing,
        "recommendation": (
            "Well-balanced set." if not missing
            else f"Add {', '.join(missing)}."
        ),
        "scored_tags": scored,
    }


def list_niches() -> list[str]:
    """Return all available niche categories."""
    return sorted(NICHE_HASHTAGS.keys())


def get_niche_hashtags(niche: str) -> dict:
    """Get all hashtags for a niche organized by tier."""
    data = _find_niche(niche)
    if not data:
        return {"error": f"Niche '{niche}' not found.", "available": list_niches()}
    return {"niche": niche, "tiers": data}


def _find_niche(niche: str) -> dict | None:
    niche = niche.lower().replace(" ", "_").replace("-", "_")
    if niche in NICHE_HASHTAGS:
        return NICHE_HASHTAGS[niche]
    # Fuzzy match
    for k in NICHE_HASHTAGS:
        if niche in k or k in niche:
            return NICHE_HASHTAGS[k]
    return None
