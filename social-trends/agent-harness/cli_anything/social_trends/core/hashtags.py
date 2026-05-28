"""Hashtag intelligence — analysis, scoring, and recommendations.

Cross-platform hashtag strategy engine. Works with data from YouTube and
TikTok scrapers, and also has a built-in niche knowledge base.
"""

import re
from typing import Any


def compute_virality_score(video_count: int, view_count: int,
                            engagement_rate: float = 0.0) -> float:
    """Compute a 0-100 virality score for a hashtag.

    Formula balances volume (reach) and engagement (quality).

    Args:
        video_count: Number of videos using the hashtag.
        view_count: Total views across all videos.
        engagement_rate: Average engagement rate (0-100).

    Returns:
        Float 0-100 representing virality potential.
    """
    if video_count == 0 and view_count == 0:
        return 0.0

    # Reach component (log scale): 0-50 points
    import math
    reach = min(50.0, math.log10(max(view_count, 1)) * 5)

    # Volume component: 0-30 points
    volume = min(30.0, math.log10(max(video_count, 1)) * 3.5)

    # Engagement component: 0-20 points
    engagement = min(20.0, engagement_rate * 2)

    return round(reach + volume + engagement, 2)


def competition_level(video_count: int) -> str:
    """Classify competition level based on video count.

    Args:
        video_count: Number of videos with this hashtag.

    Returns:
        'low', 'medium', 'high', or 'oversaturated'.
    """
    if video_count <= 50_000:
        return "low"
    elif video_count < 500_000:
        return "medium"
    elif video_count < 5_000_000:
        return "high"
    else:
        return "oversaturated"


def recommend_hashtag_mix(niche: str, platform: str = "tiktok") -> dict:
    """Generate a recommended hashtag mix for a given niche.

    Returns a balanced strategy: broad + medium + niche hashtags.
    Platform-specific best practices are applied.

    Args:
        niche: Content niche (e.g., 'fitness', 'cooking', 'gaming').
        platform: 'tiktok' or 'youtube' (affects count and strategy).

    Returns:
        Dict with {broad, medium, niche, posting_tip, example_caption}.
    """
    niche_lower = niche.lower().strip()
    db = _NICHE_HASHTAG_DB.get(niche_lower, _get_default_niche_hashtags(niche_lower))

    if platform == "tiktok":
        # TikTok: 3-5 hashtags max, mix of broad+niche
        return {
            "platform": "tiktok",
            "niche": niche,
            "strategy": "3-5 hashtags: 1 mega (100M+), 1 large (10M+), 2-3 niche",
            "broad": db["broad"][:2],
            "medium": db["medium"][:2],
            "niche_specific": db["niche"][:3],
            "recommended_caption": _build_tiktok_caption(niche, db),
            "tip": "TikTok's algorithm weighs niche hashtags heavily. Avoid >7 tags.",
        }
    else:
        # YouTube: keywords in title + tags field, hashtags in description
        return {
            "platform": "youtube",
            "niche": niche,
            "strategy": "3 hashtags in description, 15+ keywords in tags field",
            "broad": db["broad"][:3],
            "medium": db["medium"][:3],
            "niche_specific": db["niche"][:5],
            "tags_field": db.get("youtube_tags", db["niche"] + db["medium"]),
            "tip": "YouTube hashtags show above the title. Use 3 max in description.",
        }


def _build_tiktok_caption(niche: str, db: dict) -> str:
    """Build an example TikTok caption with hashtags."""
    tags = (
        db["broad"][:1]
        + db["medium"][:1]
        + db["niche"][:2]
        + ["#fyp", "#foryou"]
    )
    return " ".join(tags[:5])


def _get_default_niche_hashtags(niche: str) -> dict:
    """Generate default hashtag structure for unknown niches."""
    return {
        "broad": ["#fyp", "#viral", "#trending"],
        "medium": [f"#{niche}content", f"#{niche}creator"],
        "niche": [f"#{niche}", f"#{niche}tips", f"#{niche}life"],
        "youtube_tags": [niche, f"{niche} tips", f"{niche} tutorial", f"{niche} for beginners"],
    }


def analyze_hashtag_set(hashtags: list[str]) -> dict:
    """Analyze a set of hashtags for strategy quality.

    Args:
        hashtags: List of hashtag strings (with or without #).

    Returns:
        Dict with {score, issues, recommendations, breakdown}.
    """
    tags = [h.lstrip("#").lower() for h in hashtags]
    issues = []
    recommendations = []

    # Count checks
    if len(tags) > 30:
        issues.append(f"Too many hashtags ({len(tags)}). Instagram max is 30, TikTok best practice is 3-5.")
    if len(tags) < 3:
        recommendations.append("Use at least 3 hashtags for better reach.")

    # Diversity check
    broad_count = sum(1 for t in tags if t in _MEGA_HASHTAGS)
    if broad_count == len(tags):
        issues.append("All hashtags are mega-broad (#fyp, #viral). Add 2-3 niche-specific tags.")
    if broad_count == 0 and len(tags) >= 5:
        recommendations.append("Consider adding 1-2 broad hashtags (#fyp, #foryou) for initial reach.")

    # Duplicate check
    if len(set(tags)) < len(tags):
        issues.append("Duplicate hashtags found. Each tag should be unique.")

    # Score calculation
    score = 70  # Base
    score += min(20, len(tags) * 2)
    score -= len(issues) * 10
    score += len(recommendations) * 2
    score = max(0, min(100, score))

    return {
        "hashtag_count": len(tags),
        "unique_count": len(set(tags)),
        "broad_tags": [f"#{t}" for t in tags if t in _MEGA_HASHTAGS],
        "niche_tags": [f"#{t}" for t in tags if t not in _MEGA_HASHTAGS],
        "quality_score": score,
        "issues": issues,
        "recommendations": recommendations,
    }


def rank_hashtags(hashtag_list: list[dict]) -> list[dict]:
    """Rank a list of hashtag dicts by opportunity score.

    Opportunity = high views + low competition (niche sweet spot).

    Args:
        hashtag_list: List of {hashtag, video_count, view_count} dicts.

    Returns:
        Sorted list with added opportunity_score and competition fields.
    """
    import math

    for item in hashtag_list:
        vc = item.get("video_count", 0)
        vv = item.get("view_count", 0)
        # Opportunity: high views relative to video count (less competition)
        avg_views_per_video = vv / max(vc, 1)
        opportunity = min(100, math.log10(max(avg_views_per_video, 1)) * 10)
        item["opportunity_score"] = round(opportunity, 1)
        item["competition"] = competition_level(vc)
        item["virality_score"] = compute_virality_score(vc, vv)

    hashtag_list.sort(key=lambda x: x["opportunity_score"], reverse=True)
    return hashtag_list


# ── Niche Hashtag Database ────────────────────────────────────────────────

_MEGA_HASHTAGS = {
    "fyp", "foryou", "foryoupage", "viral", "trending", "tiktok",
    "reels", "explore", "instagram", "youtube", "viral", "trending",
}

_NICHE_HASHTAG_DB: dict[str, dict] = {
    "fitness": {
        "broad": ["#fitness", "#gym", "#workout"],
        "medium": ["#fitnessmotivation", "#fitnessjourney", "#workoutroutine"],
        "niche": ["#homeworkout", "#strengthtraining", "#caloriedeficit", "#bulkingseason", "#fitcheck"],
        "youtube_tags": ["workout routine", "home workout", "gym motivation", "fitness tips", "weight loss"],
    },
    "cooking": {
        "broad": ["#food", "#cooking", "#recipe"],
        "medium": ["#foodtiktok", "#cookingvideo", "#mealprep"],
        "niche": ["#easyrecipes", "#30minutemeals", "#budgetmeals", "#healthyeating", "#foodhacks"],
        "youtube_tags": ["easy recipe", "quick dinner", "meal prep", "cooking tutorial", "budget meals"],
    },
    "fashion": {
        "broad": ["#fashion", "#style", "#ootd"],
        "medium": ["#fashiontiktok", "#outfitcheck", "#styleinspo"],
        "niche": ["#thriftflip", "#outfitoftheday", "#fashionhacks", "#capsulewardrobe", "#streetstyle"],
        "youtube_tags": ["outfit ideas", "fashion haul", "style tips", "thrift flip", "get ready with me"],
    },
    "beauty": {
        "broad": ["#beauty", "#makeup", "#skincare"],
        "medium": ["#beautytips", "#makeuptutorial", "#skincareRoutine"],
        "niche": ["#drugstorebeauty", "#glowup", "#cleanskincare", "#grwm", "#makeuptransformation"],
        "youtube_tags": ["makeup tutorial", "skincare routine", "drugstore makeup", "glow up", "GRWM"],
    },
    "gaming": {
        "broad": ["#gaming", "#gamer", "#games"],
        "medium": ["#gamingtiktok", "#gamingmemes", "#gameplay"],
        "niche": ["#fps", "#pcgaming", "#gamingsetup", "#streamer", "#esports"],
        "youtube_tags": ["gaming highlights", "game review", "gaming tips", "best moments", "gameplay"],
    },
    "travel": {
        "broad": ["#travel", "#wanderlust", "#adventure"],
        "medium": ["#traveltiktok", "#travelinspo", "#travelwithme"],
        "niche": ["#solotravel", "#budgettravel", "#hiddengems", "#travelhacks", "#digitalnomad"],
        "youtube_tags": ["travel vlog", "travel tips", "budget travel", "hidden gems", "solo travel"],
    },
    "finance": {
        "broad": ["#money", "#finance", "#investing"],
        "medium": ["#personalfinance", "#moneytips", "#financialliteracy"],
        "niche": ["#stockmarket", "#passiveincome", "#sidehustle", "#debtfree", "#savingmoney"],
        "youtube_tags": ["investing for beginners", "passive income", "side hustle", "stock market", "budgeting"],
    },
    "motivation": {
        "broad": ["#motivation", "#mindset", "#success"],
        "medium": ["#motivationalquotes", "#selfimprovement", "#growthmindset"],
        "niche": ["#dailymotivation", "#entrepreneurmindset", "#levelup", "#discipline", "#hardwork"],
        "youtube_tags": ["motivational speech", "success mindset", "self improvement", "discipline", "morning routine"],
    },
    "comedy": {
        "broad": ["#funny", "#comedy", "#humor"],
        "medium": ["#funnytiktok", "#comedyvideo", "#relatable"],
        "niche": ["#funnymoments", "#skit", "#comedyskit", "#adulthumor", "#cringe"],
        "youtube_tags": ["funny compilation", "comedy sketch", "relatable humor", "funny moments"],
    },
    "tech": {
        "broad": ["#tech", "#technology", "#ai"],
        "medium": ["#techtok", "#techreview", "#gadgets"],
        "niche": ["#aitools", "#productivity", "#softwareengineering", "#coding", "#startups"],
        "youtube_tags": ["tech review", "AI tools", "productivity tips", "best gadgets", "software tutorial"],
    },
    "music": {
        "broad": ["#music", "#song", "#newmusic"],
        "medium": ["#musictiktok", "#musicvideo", "#originalmusic"],
        "niche": ["#indiemusic", "#producer", "#beatmaker", "#hiphop", "#rnb"],
        "youtube_tags": ["music video", "new song", "original music", "beat", "producer"],
    },
    "pets": {
        "broad": ["#pets", "#dogs", "#cats"],
        "medium": ["#dogsoftiktok", "#catsoftiktok", "#petlover"],
        "niche": ["#dogmom", "#catmom", "#funnyanimals", "#cuteanimals", "#pettraining"],
        "youtube_tags": ["cute dogs", "funny cats", "pet compilation", "dog training", "cat behavior"],
    },
    "business": {
        "broad": ["#business", "#entrepreneur", "#startup"],
        "medium": ["#businesstips", "#entrepreneurlife", "#ceo"],
        "niche": ["#smallbusiness", "#ecommerce", "#dropshipping", "#smma", "#businessmindset"],
        "youtube_tags": ["business tips", "how to start a business", "entrepreneurship", "online business", "ecommerce"],
    },
    "education": {
        "broad": ["#education", "#learning", "#school"],
        "medium": ["#edutok", "#learnontiktok", "#didyouknow"],
        "niche": ["#lifehacks", "#funfacts", "#howto", "#tutorials", "#studywithme"],
        "youtube_tags": ["educational video", "how to", "tutorial", "explained", "learn"],
    },
    "art": {
        "broad": ["#art", "#artist", "#drawing"],
        "medium": ["#arttiktok", "#digitalart", "#artwork"],
        "niche": ["#speedpaint", "#artprocess", "#characterdesign", "#illustration", "#procreate"],
        "youtube_tags": ["art tutorial", "drawing process", "digital art", "speed paint", "illustration"],
    },
}
