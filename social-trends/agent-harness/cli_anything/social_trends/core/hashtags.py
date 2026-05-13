"""Hashtag intelligence — cross-platform analysis, optimization, and set generation."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional


# Niche → hashtag bank (high-volume + mid-volume + niche-specific mix for optimal reach)
NICHE_HASHTAG_BANKS: dict[str, dict[str, list[str]]] = {
    "fitness": {
        "high": ["#fitness", "#gym", "#workout", "#health", "#motivation", "#fit", "#exercise"],
        "mid": ["#gains", "#weightloss", "#bodybuilding", "#fitspo", "#cardio", "#strength", "#training"],
        "niche": ["#homeworkout", "#gymlife", "#fitnessmotivation", "#transformationtuesday", "#musclebuilding"],
        "viral": ["#fyp", "#foryou", "#viral", "#trending"],
    },
    "beauty": {
        "high": ["#beauty", "#makeup", "#skincare", "#beautiful", "#style", "#fashion", "#love"],
        "mid": ["#glam", "#tutorial", "#makeuptutorial", "#glow", "#skincareroutine", "#selfcare"],
        "niche": ["#naturalmakeup", "#skintok", "#glowup", "#beautyadvice", "#makeuptips"],
        "viral": ["#fyp", "#foryou", "#viral", "#beautytok"],
    },
    "food": {
        "high": ["#food", "#foodie", "#recipe", "#cooking", "#delicious", "#yummy", "#eat"],
        "mid": ["#homecooking", "#easyrecipe", "#dinner", "#lunch", "#breakfast", "#snack", "#foodlover"],
        "niche": ["#foodtok", "#cookingtips", "#mealprep", "#healthyfood", "#quickrecipe"],
        "viral": ["#fyp", "#foryou", "#viral", "#foodtiktok"],
    },
    "finance": {
        "high": ["#money", "#investing", "#finance", "#wealth", "#success", "#entrepreneur", "#business"],
        "mid": ["#personalfinance", "#stockmarket", "#crypto", "#savings", "#budgeting", "#passive income"],
        "niche": ["#moneytok", "#financetips", "#financialfreedom", "#investing101", "#stocktips"],
        "viral": ["#fyp", "#foryou", "#viral", "#fintech"],
    },
    "fashion": {
        "high": ["#fashion", "#style", "#ootd", "#outfit", "#clothing", "#trendy", "#streetwear"],
        "mid": ["#fashiontok", "#fashioninspo", "#styleinspo", "#outfitideas", "#haul", "#thrift"],
        "niche": ["#outfitcheck", "#fashionadvice", "#stylingtips", "#grwm", "#closettour"],
        "viral": ["#fyp", "#foryou", "#viral", "#fashiontrends"],
    },
    "gaming": {
        "high": ["#gaming", "#gamer", "#videogames", "#games", "#twitch", "#gameplay", "#esports"],
        "mid": ["#xbox", "#playstation", "#pc", "#nintendo", "#fps", "#rpg", "#mmorpg"],
        "niche": ["#gamingtok", "#gamertok", "#gamingsetup", "#streamclips", "#gamingcommunity"],
        "viral": ["#fyp", "#foryou", "#viral", "#gamingtiktok"],
    },
    "travel": {
        "high": ["#travel", "#wanderlust", "#explore", "#adventure", "#vacation", "#holiday", "#traveler"],
        "mid": ["#travelgram", "#backpacking", "#roadtrip", "#traveltips", "#worldtravel", "#bucketlist"],
        "niche": ["#traveltok", "#travelhacks", "#budgettravel", "#solotravel", "#digitalnomad"],
        "viral": ["#fyp", "#foryou", "#viral", "#traveltiktok"],
    },
    "motivation": {
        "high": ["#motivation", "#success", "#mindset", "#inspiration", "#goals", "#hustle", "#grind"],
        "mid": ["#entrepreneur", "#selfdevelopment", "#positivity", "#growth", "#discipline", "#focus"],
        "niche": ["#motivationtok", "#successmindset", "#morningroutine", "#selfimprovement", "#dailymotivation"],
        "viral": ["#fyp", "#foryou", "#viral", "#motivationdaily"],
    },
    "comedy": {
        "high": ["#funny", "#comedy", "#humor", "#lol", "#memes", "#laugh", "#viral"],
        "mid": ["#skit", "#joke", "#comedyvideo", "#relatable", "#funnymemes", "#comedytok"],
        "niche": ["#standupcomedy", "#prank", "#parody", "#funnydaily", "#comedycentral"],
        "viral": ["#fyp", "#foryou", "#viral", "#funnyvideo"],
    },
    "pets": {
        "high": ["#pets", "#animals", "#dog", "#cat", "#cute", "#dogsoftiktok", "#catsoftiktok"],
        "mid": ["#puppy", "#kitten", "#petlover", "#animalsoftiktok", "#petcare", "#funnypets"],
        "niche": ["#pettok", "#dogtraining", "#catbehavior", "#petadvice", "#rescuedog"],
        "viral": ["#fyp", "#foryou", "#viral", "#petstagram"],
    },
}

PLATFORM_LIMITS = {
    "tiktok": 30,
    "instagram": 30,
    "youtube": 15,
    "twitter": 3,
    "linkedin": 5,
}

OPTIMAL_COUNTS = {
    "tiktok": 5,      # TikTok: 3-7 is sweet spot, too many dilute reach
    "instagram": 10,   # Instagram: 5-15 for Reels, 20-30 for posts
    "youtube": 5,      # YouTube: 3-7 in description
    "twitter": 2,
    "linkedin": 3,
}


@dataclass
class HashtagSet:
    platform: str
    niche: str
    hashtags: list[str]
    strategy_note: str
    estimated_reach: str
    mix: dict[str, list[str]]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class HashtagAnalysis:
    tag: str
    platform: str
    estimated_volume: str
    competition: str
    recommended: bool
    reason: str

    def to_dict(self) -> dict:
        return asdict(self)


def generate_hashtag_set(
    niche: str,
    platform: str = "tiktok",
    include_viral: bool = True,
    custom_tags: Optional[list[str]] = None,
) -> HashtagSet:
    """
    Generate an optimized hashtag set for a given niche and platform.
    Balances high-volume, mid-volume, and niche-specific tags for maximum reach.
    """
    niche_lower = niche.lower()
    bank = NICHE_HASHTAG_BANKS.get(niche_lower, _build_generic_bank(niche))
    limit = PLATFORM_LIMITS.get(platform, 10)
    optimal = OPTIMAL_COUNTS.get(platform, 5)

    # Mix strategy: ~20% high, ~40% mid, ~30% niche, ~10% viral
    n_high = max(1, int(optimal * 0.20))
    n_viral = max(1, int(optimal * 0.15)) if include_viral else 0
    n_mid = max(1, int(optimal * 0.40))
    n_niche = max(0, optimal - n_high - n_mid - n_viral)

    selected: list[str] = []
    mix: dict[str, list[str]] = {}

    high_pick = bank.get("high", [])[:n_high]
    mid_pick = bank.get("mid", [])[:n_mid]
    niche_pick = bank.get("niche", [])[:n_niche] if n_niche > 0 else []
    viral_pick = bank.get("viral", [])[:n_viral] if include_viral else []

    mix["high_volume"] = high_pick
    mix["mid_volume"] = mid_pick
    mix["niche_specific"] = niche_pick
    mix["viral"] = viral_pick

    selected = (high_pick + mid_pick + niche_pick + viral_pick)[:limit]

    if custom_tags:
        for tag in custom_tags:
            t = tag if tag.startswith("#") else f"#{tag}"
            if t not in selected and len(selected) < limit:
                selected.append(t)

    reach_map = {"high": "1M+", "mid": "100K–1M", "niche": "10K–100K"}
    strategy_note = (
        f"Optimized {platform} set for '{niche}': "
        f"{n_high} high-volume (broad reach), "
        f"{n_mid} mid-volume (targeted), "
        f"{n_niche} niche-specific (community), "
        f"{n_viral} viral boosters. "
        f"Total: {len(selected)}/{limit} allowed."
    )

    return HashtagSet(
        platform=platform,
        niche=niche,
        hashtags=selected,
        strategy_note=strategy_note,
        estimated_reach="50K–500K impressions per post (varies by account size)",
        mix=mix,
    )


def _build_generic_bank(niche: str) -> dict[str, list[str]]:
    """Build a generic hashtag bank for unknown niches."""
    base = niche.lower().replace(" ", "")
    return {
        "high": [f"#{base}", f"#{base}life", f"#{base}community", "#trending", "#viral"],
        "mid": [f"#{base}tips", f"#{base}advice", f"#{base}goals", f"#{base}daily", f"#{base}lover"],
        "niche": [f"#{base}tiktok", f"#{base}tok", f"#{base}content", f"#{base}creator"],
        "viral": ["#fyp", "#foryou", "#viral", "#trending"],
    }


def analyze_hashtags(tags: list[str], platform: str = "tiktok") -> list[HashtagAnalysis]:
    """Analyze a list of hashtags and provide optimization recommendations."""
    VOLUME_MAP = {
        "#fyp": ("500B+", "Very High"),
        "#foryou": ("350B+", "Very High"),
        "#viral": ("180B+", "Very High"),
        "#trending": ("80B+", "High"),
        "#fitness": ("90B+", "High"),
        "#gym": ("85B+", "High"),
        "#makeup": ("110B+", "High"),
        "#skincare": ("55B+", "High"),
        "#food": ("95B+", "High"),
        "#recipe": ("28B+", "High"),
        "#gaming": ("110B+", "High"),
        "#music": ("75B+", "High"),
        "#fashion": ("60B+", "High"),
        "#travel": ("42B+", "High"),
        "#motivation": ("35B+", "High"),
        "#money": ("30B+", "High"),
    }

    results: list[HashtagAnalysis] = []
    for tag in tags:
        tag_lower = tag.lower() if tag.startswith("#") else f"#{tag.lower()}"
        volume, competition = VOLUME_MAP.get(tag_lower, ("Unknown", "Unknown"))
        recommended = competition not in ("Very High",) or len(tags) <= 5
        reason = (
            "High competition — use sparingly as 1 of 5+ tags"
            if competition == "Very High"
            else "Good balance of reach and discoverability"
        )
        results.append(
            HashtagAnalysis(
                tag=tag_lower,
                platform=platform,
                estimated_volume=volume,
                competition=competition,
                recommended=recommended,
                reason=reason,
            )
        )
    return results


def cross_platform_strategy(niche: str) -> dict:
    """Generate a complete cross-platform hashtag strategy for a niche."""
    return {
        "niche": niche,
        "platforms": {
            platform: generate_hashtag_set(niche, platform).to_dict()
            for platform in ["tiktok", "instagram", "youtube", "twitter", "linkedin"]
        },
        "pro_tips": [
            "Rotate hashtag sets every 2-3 weeks to avoid shadow-banning",
            "Never copy-paste the exact same hashtag set across every post",
            "Mix 1-2 mega tags (100M+ posts), 3-5 mid tags (10M-100M), and 2-3 niche tags (<1M)",
            "Place hashtags in comments on Instagram Reels for cleaner captions",
            "On TikTok, put hashtags at the END of your caption",
            "Track which hashtag sets drive the most views using platform analytics",
            "Use platform search to discover emerging hashtags before they peak",
        ],
    }
