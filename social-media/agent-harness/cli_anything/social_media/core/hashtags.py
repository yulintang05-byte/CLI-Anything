"""Hashtag generation, scoring, and optimization."""

from datetime import datetime


_NICHE_HASHTAG_SETS: dict[str, dict] = {
    "finance": {
        "high_volume": ["#money", "#personalfinance", "#investing", "#finance", "#wealth"],
        "mid_volume": ["#passiveincome", "#sidehustle", "#financialfreedom", "#stockmarket", "#budgeting"],
        "low_competition": ["#moneytips2025", "#financetok", "#debtfree", "#cashflow", "#frugalliving"],
        "niche_specific": ["#dividendinvesting", "#realestateinvesting", "#cryptotips", "#indexfunds", "#firejourney"],
    },
    "fitness": {
        "high_volume": ["#gym", "#fitness", "#workout", "#health", "#motivation"],
        "mid_volume": ["#weightloss", "#bodybuilding", "#fitnessmotivation", "#gymlife", "#cardio"],
        "low_competition": ["#gymmotivation2025", "#homeworkout", "#fitcheck", "#gainz", "#preworkout"],
        "niche_specific": ["#calisthenics", "#powerlifting", "#crossfit", "#hiit", "#mealprep"],
    },
    "lifestyle": {
        "high_volume": ["#lifestyle", "#aesthetic", "#dayinmylife", "#vlog", "#morningroutine"],
        "mid_volume": ["#productivityhacks", "#selfimprovement", "#minimalism", "#slowliving", "#intentionalliving"],
        "low_competition": ["#morningroutine2025", "#aestheticvlog", "#cozyaesthetic", "#softlife", "#quietluxury"],
        "niche_specific": ["#femaleentrepreneur", "#digitalnomad", "#remotework", "#solotravel", "#capsulewardrobe"],
    },
    "fashion": {
        "high_volume": ["#fashion", "#ootd", "#style", "#outfit", "#fashionista"],
        "mid_volume": ["#streetstyle", "#styletips", "#fashioninspo", "#outfitideas", "#clothing"],
        "low_competition": ["#outfitoftheday2025", "#fashiontok", "#styleover30", "#plussize", "#thriftflip"],
        "niche_specific": ["#darkacademia", "#cottagecore", "#y2kaesthetic", "#oldmoney", "#quietluxury"],
    },
    "food": {
        "high_volume": ["#food", "#recipe", "#cooking", "#foodie", "#yummy"],
        "mid_volume": ["#easyrecipes", "#mealprep", "#healthyfood", "#foodtok", "#homecooking"],
        "low_competition": ["#recipetok", "#easydinner", "#quickrecipes", "#budgetmeals", "#mealprepping"],
        "niche_specific": ["#glutenfree", "#vegrecipes", "#keto", "#mediterraneandiet", "#proteinmeals"],
    },
    "beauty": {
        "high_volume": ["#beauty", "#skincare", "#makeup", "#glowup", "#beautytips"],
        "mid_volume": ["#skincarerutine", "#makeuptutorial", "#beautyreview", "#dermatologist", "#skintok"],
        "low_competition": ["#skincareunder30", "#cleangirl", "#nofilterskin", "#glasskin", "#slugging"],
        "niche_specific": ["#hyperpigmentation", "#acnetreatment", "#antiaging", "#retinol", "#spf"],
    },
    "motivation": {
        "high_volume": ["#motivation", "#mindset", "#success", "#entrepreneur", "#hustle"],
        "mid_volume": ["#selfimprovement", "#personaldevelopment", "#growthmindset", "#mentalhealth", "#positivity"],
        "low_competition": ["#dailymotivation2025", "#entrepreneurmindset", "#successhabits", "#morningmotivation", "#goalsetting"],
        "niche_specific": ["#abundancemindset", "#manifestation", "#lawofattraction", "#gratitude", "#journaling"],
    },
    "travel": {
        "high_volume": ["#travel", "#wanderlust", "#travelgram", "#explore", "#adventure"],
        "mid_volume": ["#traveltips", "#budgettravel", "#solotravel", "#digitalnomad", "#backpacking"],
        "low_competition": ["#hiddengems", "#travelcreator", "#slowtravel", "#sustainabletravel", "#luxurytravel"],
        "niche_specific": ["#visafreecountries", "#cheapflights", "#airbnbhacks", "#hostellife", "#workandtravel"],
    },
    "general": {
        "high_volume": ["#fyp", "#foryoupage", "#viral", "#trending", "#foryou"],
        "mid_volume": ["#explore", "#reels", "#shorts", "#contentcreator", "#creator"],
        "low_competition": ["#viralvideo", "#trendingvideo", "#newcreator", "#smallcreator", "#grwm"],
        "niche_specific": [],
    },
}

_PLATFORM_LIMITS = {
    "tiktok": {"max_tags": 5, "optimal": 3, "in_caption": True},
    "instagram": {"max_tags": 30, "optimal": 11, "in_caption": False},
    "youtube_shorts": {"max_tags": 10, "optimal": 5, "in_caption": True},
    "youtube": {"max_tags": 15, "optimal": 8, "in_caption": False},
}


def generate_hashtag_set(
    niche: str,
    platform: str = "tiktok",
    strategy: str = "balanced",
    custom_tags: list[str] = None,
) -> dict:
    """Generate an optimized hashtag set for a niche and platform.

    Strategies:
    - 'balanced': Mix of high/mid/low competition (recommended)
    - 'aggressive': Max high-volume tags for reach
    - 'niche': Focus on niche-specific tags for conversion
    - 'stealth': Low-competition tags to avoid shadowban risk
    """
    niche_lower = niche.lower()
    niche_data = _NICHE_HASHTAG_SETS.get(niche_lower, _NICHE_HASHTAG_SETS["general"])
    platform_cfg = _PLATFORM_LIMITS.get(platform, _PLATFORM_LIMITS["tiktok"])
    max_tags = platform_cfg["optimal"]

    if strategy == "balanced":
        tags = (
            niche_data["high_volume"][:2]
            + niche_data["mid_volume"][:2]
            + niche_data["low_competition"][:2]
            + _NICHE_HASHTAG_SETS["general"]["high_volume"][:2]
        )
    elif strategy == "aggressive":
        tags = (
            niche_data["high_volume"]
            + _NICHE_HASHTAG_SETS["general"]["high_volume"][:3]
        )
    elif strategy == "niche":
        tags = (
            niche_data["niche_specific"]
            + niche_data["low_competition"][:3]
            + niche_data["mid_volume"][:2]
        )
    elif strategy == "stealth":
        tags = (
            niche_data["low_competition"]
            + niche_data["niche_specific"][:3]
        )
    else:
        tags = niche_data["high_volume"] + niche_data["mid_volume"]

    if custom_tags:
        tags = list(dict.fromkeys(custom_tags + tags))

    tags = list(dict.fromkeys(tags))[:max_tags + 5]

    return {
        "niche": niche,
        "platform": platform,
        "strategy": strategy,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "hashtags": tags[:max_tags],
        "extended_set": tags,
        "caption_format": _format_for_caption(tags[:max_tags], platform),
        "platform_config": platform_cfg,
        "tips": _hashtag_tips(platform, strategy),
    }


def score_hashtags(tags: list[str], platform: str = "tiktok") -> dict:
    """Score an existing set of hashtags for quality and reach potential."""
    platform_cfg = _PLATFORM_LIMITS.get(platform, _PLATFORM_LIMITS["tiktok"])
    max_tags = platform_cfg["max_tags"]

    all_known: dict[str, dict] = {}
    for niche_data in _NICHE_HASHTAG_SETS.values():
        for tier, tier_tags in niche_data.items():
            for tag in tier_tags:
                all_known[tag] = {"tier": tier, "known": True}

    scored = []
    issues = []
    total_score = 0

    for tag in tags:
        tag_lower = tag.lower() if tag.startswith("#") else f"#{tag.lower()}"
        info = all_known.get(tag_lower, {"tier": "unknown", "known": False})
        tier = info["tier"]

        if tier == "high_volume":
            score = 3
        elif tier == "mid_volume":
            score = 4
        elif tier == "low_competition":
            score = 5
        elif tier == "niche_specific":
            score = 4
        else:
            score = 2

        scored.append({"tag": tag_lower, "score": score, "tier": tier, "known": info["known"]})
        total_score += score

    if len(tags) > max_tags:
        issues.append(f"Too many hashtags ({len(tags)}). Platform max: {max_tags}.")
    if len(tags) < 3:
        issues.append("Too few hashtags. Use at least 3 for better reach.")

    high_vol = sum(1 for s in scored if s["tier"] == "high_volume")
    if high_vol == len(tags):
        issues.append("All high-volume tags = high competition. Mix in niche tags.")

    avg_score = total_score / max(len(scored), 1)

    return {
        "platform": platform,
        "tag_count": len(tags),
        "optimal_count": platform_cfg["optimal"],
        "avg_score": round(avg_score, 2),
        "overall_rating": _score_to_rating(avg_score),
        "scored_tags": scored,
        "issues": issues,
        "recommendation": _recommend_from_score(avg_score, issues),
    }


def list_niches() -> list[dict]:
    """List all available niches with their hashtag counts."""
    return [
        {
            "niche": niche,
            "total_tags": sum(len(v) for v in data.values()),
            "tiers": list(data.keys()),
        }
        for niche, data in _NICHE_HASHTAG_SETS.items()
    ]


def save_hashtag_set(project: dict, name: str, tags: list[str], niche: str, platform: str) -> dict:
    """Save a hashtag set to the project."""
    entry = {
        "name": name,
        "niche": niche,
        "platform": platform,
        "tags": tags,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    project.setdefault("hashtag_sets", []).append(entry)
    return entry


def list_hashtag_sets(project: dict) -> list[dict]:
    return project.get("hashtag_sets", [])


def _format_for_caption(tags: list[str], platform: str) -> str:
    if platform == "instagram":
        return "\n.\n.\n.\n" + " ".join(tags)
    return " ".join(tags)


def _hashtag_tips(platform: str, strategy: str) -> list[str]:
    tips = [
        "Rotate hashtag sets every 7-10 posts to avoid shadowban patterns.",
        "Never use the exact same hashtags on every post.",
    ]
    if platform == "tiktok":
        tips.append("TikTok: place hashtags at the END of caption, not mid-text.")
        tips.append("3-5 hashtags is the TikTok sweet spot — more can hurt reach.")
    elif platform == "instagram":
        tips.append("Instagram: first comment hashtag placement gets same reach with cleaner captions.")
        tips.append("Mix 3 high + 4 mid + 4 low competition for best Instagram results.")
    if strategy == "aggressive":
        tips.append("Aggressive strategy works best on established accounts (10k+ followers).")
    return tips


def _score_to_rating(score: float) -> str:
    if score >= 4.5:
        return "Excellent"
    if score >= 3.5:
        return "Good"
    if score >= 2.5:
        return "Average"
    return "Needs Work"


def _recommend_from_score(score: float, issues: list[str]) -> str:
    if issues:
        return f"Fix issues first: {issues[0]}"
    if score >= 4.0:
        return "Great hashtag mix. Monitor performance and rotate sets weekly."
    return "Add more niche-specific and mid-competition tags for better targeting."
