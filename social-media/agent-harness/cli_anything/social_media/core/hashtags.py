"""Hashtag research, scoring, and niche-specific sets for maximum reach."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class HashtagSet:
    niche: str
    platform: str
    mega: list[str] = field(default_factory=list)       # >1B posts — discovery only
    large: list[str] = field(default_factory=list)      # 100M-1B  — broad reach
    medium: list[str] = field(default_factory=list)     # 10M-100M — targeted
    niche_tags: list[str] = field(default_factory=list) # <10M     — high engagement
    avoid: list[str] = field(default_factory=list)      # shadow-banned or saturated


# ──────────────────────────────────────────────
#  Niche hashtag database
# ──────────────────────────────────────────────

HASHTAG_DB: dict[str, HashtagSet] = {
    "fitness": HashtagSet(
        niche="fitness",
        platform="tiktok+instagram",
        mega=["#fyp", "#viral", "#foryou"],
        large=["#fitness", "#gym", "#workout", "#health", "#motivation"],
        medium=["#gymlife", "#fitnessmotivation", "#personaltrainer", "#fitcheck", "#gymrat"],
        niche_tags=["#GymTok", "#LiftingLife", "#HomeWorkout", "#CalisthenicsLife", "#FitFam2025"],
        avoid=["#like4like", "#follow4follow", "#spam"],
    ),
    "finance": HashtagSet(
        niche="finance",
        platform="tiktok+instagram",
        mega=["#fyp", "#viral"],
        large=["#money", "#finance", "#investing", "#wealth", "#rich"],
        medium=["#stockmarket", "#personalfinance", "#financetips", "#passiveincome", "#sidehustle"],
        niche_tags=["#FinanceTok", "#MoneyTikTok", "#IndexFunds", "#FIRE", "#BudgetingTips"],
        avoid=["#getrichquick", "#makemoney"],
    ),
    "lifestyle": HashtagSet(
        niche="lifestyle",
        platform="tiktok+instagram",
        mega=["#fyp", "#viral", "#aesthetic"],
        large=["#lifestyle", "#dayinmylife", "#vlog", "#routine", "#selfcare"],
        medium=["#morningroutine", "#nightroutine", "#grwm", "#dayinthelife", "#minimalism"],
        niche_tags=["#SoftLife", "#LuxuryLifestyle", "#SlowLiving", "#CleanGirl", "#ThatGirl"],
        avoid=[],
    ),
    "business": HashtagSet(
        niche="business",
        platform="tiktok+instagram",
        mega=["#fyp", "#viral"],
        large=["#entrepreneur", "#business", "#marketing", "#startup", "#success"],
        medium=["#smallbusiness", "#ecommerce", "#dropshipping", "#contentcreator", "#onlinebusiness"],
        niche_tags=["#DigitalMarketing", "#SMM", "#CreatorEconomy", "#SoloFounder", "#B2B"],
        avoid=["#hustleculture"],
    ),
    "food": HashtagSet(
        niche="food",
        platform="tiktok+instagram",
        mega=["#fyp", "#viral", "#food"],
        large=["#foodie", "#recipe", "#cooking", "#foodtok", "#yummy"],
        medium=["#homecooking", "#mealprep", "#foodphotography", "#easyrecipes", "#healthyfood"],
        niche_tags=["#FoodTok", "#WhatIEat", "#QuickRecipes", "#DinnerIdeas", "#FoodBlogger"],
        avoid=[],
    ),
    "tech": HashtagSet(
        niche="tech",
        platform="tiktok+youtube",
        mega=["#fyp", "#viral", "#ai"],
        large=["#tech", "#technology", "#ai", "#coding", "#programming"],
        medium=["#developer", "#softwaredeveloper", "#aitools", "#chatgpt", "#machinelearning"],
        niche_tags=["#AITikTok", "#TechTok", "#CodeLife", "#BuiltWithAI", "#NoCode"],
        avoid=[],
    ),
    "themepage": HashtagSet(
        niche="themepage",
        platform="tiktok+instagram",
        mega=["#fyp", "#viral", "#foryoupage"],
        large=["#motivation", "#quotes", "#mindset", "#success", "#inspiration"],
        medium=["#motivationalquotes", "#successmindset", "#dailymotivation", "#growthmindset", "#hustle"],
        niche_tags=["#ThemePage", "#FacelessMarketing", "#FacelessContent", "#AutomatedContent", "#DigitalBusiness"],
        avoid=["#spam", "#followforfollow"],
    ),
    "beauty": HashtagSet(
        niche="beauty",
        platform="tiktok+instagram",
        mega=["#fyp", "#viral", "#beauty"],
        large=["#makeup", "#skincare", "#grwm", "#beautytips", "#glam"],
        medium=["#skincarerroutine", "#makeuptutorial", "#glowup", "#beautyhacks", "#skintok"],
        niche_tags=["#SkinTok", "#CleanBeauty", "#DupeAlert", "#GRWM2025", "#GetUnready"],
        avoid=[],
    ),
    "travel": HashtagSet(
        niche="travel",
        platform="tiktok+instagram",
        mega=["#fyp", "#viral", "#travel"],
        large=["#traveltok", "#adventure", "#explore", "#wanderlust", "#travellife"],
        medium=["#solotravel", "#budgettravel", "#travelguide", "#hiddengems", "#travelcouple"],
        niche_tags=["#TravelTok", "#DigitalNomad", "#TravelHacks", "#CheapFlights", "#BestPlaces"],
        avoid=[],
    ),
}


def get_hashtag_set(niche: str, platform: str = "tiktok") -> Optional[HashtagSet]:
    key = niche.lower().replace(" ", "")
    return HASHTAG_DB.get(key)


def list_niches() -> list[str]:
    return sorted(HASHTAG_DB.keys())


def build_caption_hashtags(niche: str, max_tags: int = 30) -> dict:
    """
    Build an optimized hashtag block using the 'mix strategy':
    - 20% mega tags (discovery reach)
    - 30% large tags (broad audience)
    - 30% medium tags (targeted reach)
    - 20% niche tags (high engagement rate)
    """
    hs = get_hashtag_set(niche)
    if hs is None:
        return {"error": f"Niche '{niche}' not found. Available: {list_niches()}"}

    n_mega   = max(1, int(max_tags * 0.20))
    n_large  = max(1, int(max_tags * 0.30))
    n_medium = max(1, int(max_tags * 0.30))
    n_niche  = max(1, int(max_tags * 0.20))

    selected = (
        hs.mega[:n_mega]
        + hs.large[:n_large]
        + hs.medium[:n_medium]
        + hs.niche_tags[:n_niche]
    )

    return {
        "niche": niche,
        "platform": hs.platform,
        "total_tags": len(selected),
        "hashtags": selected,
        "caption_block": " ".join(selected),
        "strategy": {
            "mega": hs.mega[:n_mega],
            "large": hs.large[:n_large],
            "medium": hs.medium[:n_medium],
            "niche": hs.niche_tags[:n_niche],
        },
        "avoid": hs.avoid,
        "tip": (
            "Post hashtags in the caption (TikTok) or first comment (Instagram). "
            "Rotate 20% of tags every 3-5 posts to avoid shadowban patterns."
        ),
    }


def hashtag_audit(tags: list[str]) -> dict:
    """Score a list of hashtags and flag issues."""
    known_banned = {
        "#like4like", "#follow4follow", "#spam", "#l4l", "#f4f",
        "#followme", "#likeforlike", "#comment4comment",
    }
    results = []
    for tag in tags:
        t = tag.lower() if tag.startswith("#") else f"#{tag.lower()}"
        flag = "banned" if t in known_banned else "ok"
        results.append({"tag": t, "status": flag})

    ok_count = sum(1 for r in results if r["status"] == "ok")
    return {
        "total": len(results),
        "ok": ok_count,
        "flagged": len(results) - ok_count,
        "tags": results,
        "recommendation": (
            "Remove all flagged tags immediately. "
            "Banned hashtags trigger shadowban even when mixed with clean tags."
        ),
    }
