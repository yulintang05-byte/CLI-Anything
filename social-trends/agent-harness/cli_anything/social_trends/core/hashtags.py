"""Hashtag strategy engine — platform-specific sets by niche and goal."""

from typing import Any

# Platform hashtag limits and best-practice counts
_PLATFORM_CONFIG = {
    "tiktok": {"optimal_count": 5, "max_count": 10, "note": "3-5 highly targeted; avoid over-tagging"},
    "youtube": {"optimal_count": 4, "max_count": 15, "note": "3-5 in description; first 3 appear above title"},
    "instagram": {"optimal_count": 11, "max_count": 30, "note": "Mix of broad + niche; avoid banned tags"},
}

# Evergreen hashtags by niche (seed data — updated May 2026)
_NICHE_HASHTAGS: dict[str, dict[str, list[str]]] = {
    "fitness": {
        "broad": ["#fitness", "#workout", "#gym", "#health", "#motivation"],
        "niche": ["#fitnessmotivation", "#gymlife", "#bodybuilding", "#personaltrainer", "#weightloss"],
        "shorts": ["#fitnessshorts", "#quickworkout", "#workoutathome", "#fitcheck", "#gymshorts"],
        "trending": ["#75hard", "#bodytransformation", "#calisthenics", "#pilates2026", "#peakphysique"],
    },
    "finance": {
        "broad": ["#finance", "#money", "#investing", "#wealth", "#business"],
        "niche": ["#personalfinance", "#stockmarket", "#passiveincome", "#sidehustle", "#financialfreedom"],
        "shorts": ["#moneytips", "#financeshorts", "#investingtips", "#budgeting", "#richhabits"],
        "trending": ["#ai_income", "#cryptotrading2026", "#realestateinvesting", "#debtfree", "#financialliteracy"],
    },
    "gaming": {
        "broad": ["#gaming", "#gamer", "#videogames", "#gameplay", "#game"],
        "niche": ["#gamingcommunity", "#gamersofyoutube", "#pcgaming", "#consolegaming", "#mobilegaming"],
        "shorts": ["#gamingshorts", "#shortsgaming", "#gamingclips", "#gamingfails", "#gamingmemes"],
        "trending": ["#airgaming", "#gamingnews2026", "#esports", "#streamer", "#newgame2026"],
    },
    "food": {
        "broad": ["#food", "#foodie", "#cooking", "#recipe", "#eat"],
        "niche": ["#homecooking", "#mealprep", "#foodphotography", "#foodtiktok", "#foodshorts"],
        "shorts": ["#quickrecipe", "#cookingshorts", "#easymeals", "#foodhacks", "#tasty"],
        "trending": ["#minieggcake", "#viralrecipe2026", "#asmrcooking", "#streetfood", "#cottagecorefood"],
    },
    "lifestyle": {
        "broad": ["#lifestyle", "#vlog", "#daily", "#life", "#dayinmylife"],
        "niche": ["#slowliving", "#minimalism", "#morningroutine", "#selfcare", "#wellbeing"],
        "shorts": ["#lifestylevlog", "#cozyliving", "#routinevlog", "#productiveday", "#aesthetic"],
        "trending": ["#quietluxury", "#slowliving2026", "#corecore", "#lifestylecheck", "#livebeautifully"],
    },
    "tech": {
        "broad": ["#tech", "#technology", "#ai", "#software", "#gadgets"],
        "niche": ["#aitools", "#techreview", "#programming", "#startup", "#innovation"],
        "shorts": ["#techshorts", "#aiexplained", "#techhacks", "#codingtips", "#softwaredev"],
        "trending": ["#ai2026", "#llm", "#claude", "#chatgpt", "#claudecode", "#automateeverything"],
    },
    "music": {
        "broad": ["#music", "#song", "#musician", "#newmusic", "#hiphop"],
        "niche": ["#independentartist", "#musicproducer", "#singersongwriter", "#undergroundmusic", "#fypmusic"],
        "shorts": ["#musicshorts", "#tiktokmusic", "#viralsong", "#newartist", "#musicvideo"],
        "trending": ["#phonkmusic", "#phonk2026", "#viralhits", "#trendingsong", "#popmusic2026"],
    },
    "beauty": {
        "broad": ["#beauty", "#makeup", "#skincare", "#fashion", "#style"],
        "niche": ["#makeuptutorial", "#skincareRoutine", "#beautyshorts", "#grwm", "#ootd"],
        "shorts": ["#beautyshorts", "#makeupshorts", "#fashiontips", "#skincaretips", "#grwmshorts"],
        "trending": ["#quietluxury", "#cleanbeauty", "#skincare2026", "#microtrend", "#aestheticfashion"],
    },
    "business": {
        "broad": ["#business", "#entrepreneur", "#success", "#startup", "#marketing"],
        "niche": ["#smallbusiness", "#entrepreneurship", "#digitalmarketing", "#ecommerce", "#branding"],
        "shorts": ["#businesstips", "#entrepreneurshorts", "#motivationshorts", "#mindset", "#growthhacks"],
        "trending": ["#ai_business", "#solopreneur", "#themepage", "#contentcreator2026", "#creatoreconomy"],
    },
    "education": {
        "broad": ["#education", "#learn", "#knowledge", "#facts", "#didyouknow"],
        "niche": ["#learnontiktok", "#educationalcontent", "#studytips", "#science", "#history"],
        "shorts": ["#eduShorts", "#learnwithme", "#funfacts", "#explainedinseconds", "#mindblown"],
        "trending": ["#ailearning", "#personalgrowth", "#learneveryday", "#curiosity2026", "#lifehacks"],
    },
}

# Goal-based hashtag modifiers
_GOAL_MODIFIERS: dict[str, list[str]] = {
    "viral": ["#fyp", "#viral", "#foryoupage", "#trending", "#foryou"],
    "growth": ["#newcreator", "#followme", "#subscribe", "#creatoronsocialmedia", "#smallcreator"],
    "engagement": ["#comment", "#like", "#share", "#duet", "#collab"],
    "sales": ["#shop", "#linkinbio", "#ad", "#sponsored", "#affiliate"],
    "community": ["#community", "#support", "#together", "#tribe", "#family"],
}


def suggest_hashtags(niche: str, platform: str, goal: str = "viral") -> dict[str, Any]:
    """Return an optimized hashtag set for a niche/platform/goal combination."""
    if platform not in _PLATFORM_CONFIG:
        raise ValueError(f"Unknown platform '{platform}'. Choose from: {', '.join(_PLATFORM_CONFIG.keys())}")

    niche_lower = niche.lower()
    if niche_lower not in _NICHE_HASHTAGS:
        available = ", ".join(_NICHE_HASHTAGS.keys())
        raise ValueError(f"Unknown niche '{niche}'. Available niches: {available}")

    config = _PLATFORM_CONFIG[platform]
    niche_tags = _NICHE_HASHTAGS[niche_lower]
    goal_tags = _GOAL_MODIFIERS.get(goal, _GOAL_MODIFIERS["viral"])

    # Build optimized set
    optimal = config["optimal_count"]
    set_primary = niche_tags["trending"][:2] + niche_tags["niche"][:2] + goal_tags[:1]
    set_secondary = niche_tags["shorts"][:3] + niche_tags["broad"][:2] + goal_tags[1:3]
    set_extended = niche_tags["broad"] + niche_tags["niche"] + niche_tags["trending"] + goal_tags

    # Deduplicate while preserving order
    seen: set[str] = set()
    full_set: list[str] = []
    for tag in set_primary + set_secondary + set_extended:
        if tag not in seen:
            seen.add(tag)
            full_set.append(tag)

    return {
        "platform": platform,
        "niche": niche,
        "goal": goal,
        "optimal_count": optimal,
        "primary_set": set_primary[:optimal],
        "extended_set": full_set[:config["max_count"]],
        "platform_note": config["note"],
        "copy_paste": " ".join(set_primary[:optimal]),
    }


def hashtag_set_all_platforms(niche: str, goal: str = "viral") -> dict[str, Any]:
    """Return optimized hashtag sets for all platforms at once."""
    return {
        p: suggest_hashtags(niche, p, goal)
        for p in _PLATFORM_CONFIG
    }


def trending_hashtags(platform: str) -> list[dict]:
    """Return current trending hashtags for a platform."""
    base = {
        "tiktok": [
            {"tag": "#fyp", "reach": "ultra-high", "category": "discovery"},
            {"tag": "#viral", "reach": "ultra-high", "category": "discovery"},
            {"tag": "#foryoupage", "reach": "high", "category": "discovery"},
            {"tag": "#trending", "reach": "high", "category": "discovery"},
            {"tag": "#phonkmusic", "reach": "high", "category": "music"},
            {"tag": "#slowliving", "reach": "medium-high", "category": "lifestyle"},
            {"tag": "#storytime", "reach": "high", "category": "entertainment"},
            {"tag": "#sidehustle", "reach": "high", "category": "business"},
            {"tag": "#ai_income", "reach": "medium", "category": "business"},
            {"tag": "#corecore", "reach": "medium", "category": "aesthetic"},
            {"tag": "#90s", "reach": "medium-high", "category": "nostalgia"},
            {"tag": "#bridgerton", "reach": "medium", "category": "entertainment"},
            {"tag": "#quietluxury", "reach": "medium", "category": "fashion"},
            {"tag": "#morningroutine", "reach": "medium-high", "category": "lifestyle"},
            {"tag": "#viralrecipe", "reach": "medium", "category": "food"},
        ],
        "youtube": [
            {"tag": "#shorts", "reach": "ultra-high", "category": "format"},
            {"tag": "#viral", "reach": "ultra-high", "category": "discovery"},
            {"tag": "#trending", "reach": "high", "category": "discovery"},
            {"tag": "#youtube", "reach": "high", "category": "platform"},
            {"tag": "#funny", "reach": "high", "category": "entertainment"},
            {"tag": "#gaming", "reach": "high", "category": "gaming"},
            {"tag": "#music", "reach": "high", "category": "music"},
            {"tag": "#tech", "reach": "medium-high", "category": "tech"},
            {"tag": "#vlog", "reach": "medium-high", "category": "lifestyle"},
            {"tag": "#nostalgia", "reach": "medium", "category": "entertainment"},
            {"tag": "#explained", "reach": "medium", "category": "education"},
            {"tag": "#slowliving", "reach": "medium", "category": "lifestyle"},
            {"tag": "#sports", "reach": "medium-high", "category": "sports"},
            {"tag": "#drama", "reach": "medium", "category": "entertainment"},
            {"tag": "#ai", "reach": "medium-high", "category": "tech"},
        ],
        "instagram": [
            {"tag": "#instagood", "reach": "ultra-high", "category": "general"},
            {"tag": "#reels", "reach": "ultra-high", "category": "format"},
            {"tag": "#viral", "reach": "high", "category": "discovery"},
            {"tag": "#trending", "reach": "high", "category": "discovery"},
            {"tag": "#ootd", "reach": "high", "category": "fashion"},
            {"tag": "#aesthetic", "reach": "high", "category": "visual"},
            {"tag": "#grwm", "reach": "medium-high", "category": "beauty"},
            {"tag": "#smallbusiness", "reach": "medium-high", "category": "business"},
            {"tag": "#slowliving", "reach": "medium", "category": "lifestyle"},
            {"tag": "#quietluxury", "reach": "medium", "category": "fashion"},
            {"tag": "#linkinbio", "reach": "medium", "category": "cta"},
            {"tag": "#explore", "reach": "high", "category": "discovery"},
            {"tag": "#contentcreator", "reach": "medium-high", "category": "creator"},
            {"tag": "#morningroutine", "reach": "medium", "category": "lifestyle"},
            {"tag": "#motivationalquotes", "reach": "medium-high", "category": "inspiration"},
        ],
    }
    if platform not in base:
        raise ValueError(f"Unknown platform. Choose from: {', '.join(base.keys())}")
    return base[platform]


def list_niches() -> list[str]:
    return sorted(_NICHE_HASHTAGS.keys())


def list_platforms() -> list[str]:
    return list(_PLATFORM_CONFIG.keys())
