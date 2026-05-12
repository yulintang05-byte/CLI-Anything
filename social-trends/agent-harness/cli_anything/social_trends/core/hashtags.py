"""Hashtag research, analysis, and recommendation engine."""

import re
from dataclasses import dataclass, field
from typing import Optional


# Curated seed hashtag sets by niche — updated May 2025
NICHE_HASHTAGS: dict[str, list[str]] = {
    "fitness": [
        "fitness", "workout", "gym", "fitnessmotivation", "bodybuilding",
        "weightloss", "cardio", "personaltrainer", "fitspo", "healthylifestyle",
        "calisthenics", "crossfit", "gains", "homeworkout", "gymlife",
    ],
    "food": [
        "food", "foodie", "recipe", "cooking", "foodphotography",
        "instafood", "homecooking", "foodlover", "delicious", "chef",
        "easyrecipes", "mealprep", "healthyfood", "baking", "dinner",
    ],
    "travel": [
        "travel", "wanderlust", "travelphotography", "adventure", "explore",
        "vacation", "travelblogger", "travelgram", "worldtravel", "bucketlist",
        "backpacking", "digitalnomad", "solotravel", "tourism", "traveltips",
    ],
    "fashion": [
        "fashion", "style", "ootd", "outfit", "fashionblogger",
        "streetstyle", "aesthetics", "fashionista", "model", "vintage",
        "stylist", "trendy", "luxury", "outfitoftheday", "clothing",
    ],
    "beauty": [
        "beauty", "makeup", "skincare", "glam", "makeupartist",
        "beautytips", "foundation", "lipstick", "eyeshadow", "glowup",
        "skincareRoutine", "selfcare", "naturalmakeup", "beautyreview", "grwm",
    ],
    "motivational": [
        "motivation", "inspiration", "mindset", "success", "hustle",
        "grindset", "goals", "positivevibes", "selfimprovement", "discipline",
        "entrepreneurship", "growthmindset", "abundance", "affirmations", "dailymotivation",
    ],
    "gaming": [
        "gaming", "gamer", "videogames", "twitch", "esports",
        "gameplay", "streamer", "ps5", "xbox", "pcgaming",
        "nintendo", "fps", "rpg", "fortnite", "gaming highlights",
    ],
    "finance": [
        "finance", "investing", "crypto", "stockmarket", "personalfinance",
        "money", "wealth", "passive income", "financialfreedom", "sidehustle",
        "budgeting", "stocks", "realestate", "entrepreneur", "makemoneyonline",
    ],
    "lifestyle": [
        "lifestyle", "vlog", "dayinmylife", "dailyvlog", "aesthetic",
        "minimalism", "productivity", "morningroutine", "nightroutine", "selflove",
        "wellness", "mentalhealth", "journaling", "contentcreator", "influencer",
    ],
    "animals": [
        "pets", "dogs", "cats", "animals", "cute",
        "dogsofinstagram", "catsofinstagram", "puppy", "kitten", "wildlife",
        "animallovers", "petcare", "rescuedogs", "adoptdontshop", "funnypets",
    ],
}

# Platform-specific viral booster tags (2025)
VIRAL_BOOSTERS: dict[str, list[str]] = {
    "tiktok": [
        "fyp", "foryoupage", "foryou", "viral", "trending",
        "trend", "tiktok", "tiktokviral", "fypシ", "viralvideo",
    ],
    "youtube": [
        "shorts", "youtubeshorts", "trending", "viral", "new",
        "reels", "viralvideo", "trending2025", "youtube",
    ],
    "instagram": [
        "reels", "instareels", "viral", "trending", "explore",
        "instadaily", "instagood", "instagram", "instagramreels",
    ],
    "cross_platform": [
        "viral", "trending", "fyp", "explore", "contentcreator",
        "socialmedia", "growyouraccount", "newvideo",
    ],
}


@dataclass
class HashtagSet:
    niche: str
    primary: list[str] = field(default_factory=list)       # core niche tags
    boosters: list[str] = field(default_factory=list)      # viral/reach boosters
    niche_specific: list[str] = field(default_factory=list)  # sub-niche tags
    platform_boosters: list[str] = field(default_factory=list)

    def to_caption(self, max_tags: int = 30) -> str:
        all_tags = (
            ["#" + t for t in self.primary[:10]]
            + ["#" + t for t in self.boosters[:5]]
            + ["#" + t for t in self.niche_specific[:8]]
            + ["#" + t for t in self.platform_boosters[:5]]
        )
        return " ".join(all_tags[:max_tags])

    def to_dict(self) -> dict:
        return {
            "niche": self.niche,
            "primary": self.primary,
            "boosters": self.boosters,
            "niche_specific": self.niche_specific,
            "platform_boosters": self.platform_boosters,
            "caption_ready": self.to_caption(),
            "total_tags": len(self.primary) + len(self.boosters)
                + len(self.niche_specific) + len(self.platform_boosters),
        }


def recommend_hashtags(
    niche: str,
    platform: str = "tiktok",
    count: int = 30,
    include_boosters: bool = True,
) -> HashtagSet:
    """Return a curated HashtagSet for a given niche and platform."""
    niche_lower = niche.lower()
    primary = NICHE_HASHTAGS.get(niche_lower, [niche_lower])[:15]

    boosters = VIRAL_BOOSTERS.get(platform.lower(), []) + VIRAL_BOOSTERS["cross_platform"]
    if not include_boosters:
        boosters = []

    # Build niche-specific sub-tags by checking overlap in other niches
    niche_specific: list[str] = []
    for other_niche, tags in NICHE_HASHTAGS.items():
        if other_niche != niche_lower and niche_lower in other_niche:
            niche_specific.extend(tags[:5])

    platform_boosters = VIRAL_BOOSTERS.get(platform.lower(), [])[:5]

    return HashtagSet(
        niche=niche,
        primary=primary,
        boosters=boosters[:8],
        niche_specific=niche_specific[:8],
        platform_boosters=platform_boosters,
    )


def extract_hashtags(text: str) -> list[str]:
    """Pull #hashtags out of any text/caption."""
    return [m.lstrip("#").lower() for m in re.findall(r"#\w+", text)]


def score_hashtag_mix(tags: list[str]) -> dict:
    """Rate a hashtag list on balance between reach and niche specificity."""
    all_known = {t for tags_list in NICHE_HASHTAGS.values() for t in tags_list}
    all_boosters = {t for tags_list in VIRAL_BOOSTERS.values() for t in tags_list}

    niche_count = sum(1 for t in tags if t.lower() in all_known)
    booster_count = sum(1 for t in tags if t.lower() in all_boosters)
    unknown_count = len(tags) - niche_count - booster_count

    score = min(100, int(
        (niche_count / max(len(tags), 1)) * 40
        + (booster_count / max(len(tags), 1)) * 30
        + (min(len(tags), 25) / 25) * 30
    ))
    return {
        "total": len(tags),
        "niche_tags": niche_count,
        "booster_tags": booster_count,
        "unknown_tags": unknown_count,
        "score": score,
        "advice": _hashtag_advice(len(tags), niche_count, booster_count),
    }


def _hashtag_advice(total: int, niche: int, booster: int) -> str:
    advice = []
    if total < 5:
        advice.append("Too few tags — add more for reach.")
    elif total > 35:
        advice.append("Over 35 tags can look spammy — trim to 20-30.")
    if booster < 3:
        advice.append("Add 3-5 viral boosters (fyp, trending, viral).")
    if niche < 5:
        advice.append("Add niche-specific tags to attract targeted followers.")
    if not advice:
        return "Good mix! Balanced niche + booster tags."
    return " ".join(advice)


def list_niches() -> list[str]:
    return sorted(NICHE_HASHTAGS.keys())
