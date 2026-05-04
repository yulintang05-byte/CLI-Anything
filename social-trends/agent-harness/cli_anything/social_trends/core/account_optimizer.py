from datetime import datetime
from typing import Any, Dict, List

OPTIMAL_TIMES: Dict[str, Dict[str, List[str]]] = {
    "tiktok": {
        "Mon": ["06:00", "10:00", "22:00"],
        "Tue": ["02:00", "04:00", "09:00"],
        "Wed": ["07:00", "08:00", "11:00"],
        "Thu": ["09:00", "12:00", "19:00"],
        "Fri": ["05:00", "13:00", "15:00"],
        "Sat": ["11:00", "19:00", "20:00"],
        "Sun": ["07:00", "08:00", "16:00"],
    },
    "instagram": {
        "Mon": ["06:00", "10:00", "22:00"],
        "Tue": ["02:00", "04:00", "09:00"],
        "Wed": ["07:00", "08:00", "11:00"],
        "Thu": ["09:00", "12:00", "19:00"],
        "Fri": ["05:00", "13:00", "15:00"],
        "Sat": ["11:00", "19:00", "20:00"],
        "Sun": ["07:00", "08:00", "16:00"],
    },
    "youtube": {
        "Mon": ["14:00", "16:00"],
        "Tue": ["14:00", "16:00"],
        "Wed": ["14:00", "16:00"],
        "Thu": ["14:00", "16:00"],
        "Fri": ["14:00", "16:00"],
        "Sat": ["09:00", "10:00"],
        "Sun": ["09:00", "10:00"],
    },
}

HASHTAG_RULES: Dict[str, Dict[str, Any]] = {
    "tiktok": {
        "optimal_count": "3-5",
        "structure": "1 mega + 1-2 niche + 1-2 platform (#fyp)",
        "best_practice": "Put hashtags in caption, keep it clean",
        "avoid": "Avoid 30+ hashtag dumps – TikTok algorithm ignores them",
    },
    "instagram": {
        "optimal_count": "15-20",
        "structure": "Mix large (1-5M), medium (100K-1M), small (<100K) tags",
        "best_practice": "Add in caption or first comment immediately after posting",
        "avoid": "Banned hashtags, repetitive sets across every post",
    },
    "youtube": {
        "optimal_count": "3-5",
        "structure": "1-2 broad topic + 2-3 specific niche terms",
        "best_practice": "Use in title, description, and the tags field",
        "avoid": "Misleading tags – YouTube penalises tag stuffing",
    },
}

NICHE_HASHTAG_SETS: Dict[str, Dict[str, List[str]]] = {
    "fitness": {
        "mega": ["#fitness", "#workout", "#gym"],
        "niche": ["#homeworkout", "#weightloss", "#gains", "#bodybuilding"],
        "platform": ["#fyp", "#foryou", "#trending"],
        "engagement": ["#fitfam", "#fitnessmotivation", "#gymlife"],
    },
    "food": {
        "mega": ["#food", "#foodie", "#cooking"],
        "niche": ["#recipe", "#homecooking", "#mealprep"],
        "platform": ["#fyp", "#foryou", "#foodtok"],
        "engagement": ["#foodlover", "#delicious", "#yummy"],
    },
    "fashion": {
        "mega": ["#fashion", "#style", "#ootd"],
        "niche": ["#streetwear", "#outfitinspo", "#fashiontips"],
        "platform": ["#fyp", "#foryou", "#fashiontiktok"],
        "engagement": ["#fashionista", "#styleinspo", "#lookbook"],
    },
    "beauty": {
        "mega": ["#beauty", "#makeup", "#skincare"],
        "niche": ["#makeuptutorial", "#skincareroutine", "#glam"],
        "platform": ["#fyp", "#foryou", "#beautytok"],
        "engagement": ["#beautylovers", "#makeuplover", "#glowup"],
    },
    "travel": {
        "mega": ["#travel", "#wanderlust", "#explore"],
        "niche": ["#traveltips", "#travelguide", "#adventure"],
        "platform": ["#fyp", "#foryou", "#traveltok"],
        "engagement": ["#travelgram", "#traveller", "#bucketlist"],
    },
    "business": {
        "mega": ["#business", "#entrepreneur", "#money"],
        "niche": ["#sidehustle", "#passiveincome", "#investing"],
        "platform": ["#fyp", "#foryou", "#businesstips"],
        "engagement": ["#success", "#motivation", "#mindset"],
    },
    "lifestyle": {
        "mega": ["#lifestyle", "#life", "#daily"],
        "niche": ["#dayinmylife", "#routine", "#vlog"],
        "platform": ["#fyp", "#foryou", "#lifestyletok"],
        "engagement": ["#luxurylifestyle", "#grwm", "#aesthetic"],
    },
    "gaming": {
        "mega": ["#gaming", "#gamer", "#games"],
        "niche": ["#gameplay", "#fps", "#rpg"],
        "platform": ["#fyp", "#foryou", "#gamingtok"],
        "engagement": ["#gamingcommunity", "#streamer", "#twitch"],
    },
    "tech": {
        "mega": ["#tech", "#technology", "#ai"],
        "niche": ["#coding", "#software", "#innovation"],
        "platform": ["#fyp", "#foryou", "#techtok"],
        "engagement": ["#programmer", "#developer", "#startup"],
    },
    "motivation": {
        "mega": ["#motivation", "#success", "#mindset"],
        "niche": ["#selfimprovement", "#personaldevelopment", "#goals"],
        "platform": ["#fyp", "#foryou", "#motivationtok"],
        "engagement": ["#inspirational", "#hustle", "#grind"],
    },
}

CONTENT_PILLAR_TEMPLATES: Dict[str, List[str]] = {
    "fitness": [
        "Workout tutorials & demonstrations",
        "Nutrition & meal prep",
        "Transformation & progress stories",
        "Fitness motivation & mindset",
        "Product & supplement reviews",
    ],
    "food": [
        "Quick & easy recipes",
        "Restaurant & product reviews",
        "Food hacks & pro tips",
        "Cultural cuisine exploration",
        "Kitchen gadget reviews",
    ],
    "business": [
        "Business tips & growth strategies",
        "Income & revenue transparency",
        "Day-in-the-life (entrepreneur)",
        "Tools & resources",
        "Mindset & productivity",
    ],
    "lifestyle": [
        "Morning/evening routines",
        "Product reviews & hauls",
        "Day-in-the-life vlogs",
        "Travel & experiences",
        "Life advice & lessons",
    ],
    "tech": [
        "Tool & app reviews",
        "How-to tutorials",
        "AI & automation tips",
        "Industry news & takes",
        "Behind-the-build content",
    ],
}

POSTING_FREQUENCY: Dict[str, str] = {
    "tiktok": "1-3 videos/day",
    "instagram": "1 Reel/day + 3-5 Stories",
    "youtube": "2-3 videos/week",
    "youtube_shorts": "1-2 Shorts/day",
}


def _resolve_niche(niche: str) -> Dict[str, List[str]]:
    n = niche.lower()
    if n in NICHE_HASHTAG_SETS:
        return NICHE_HASHTAG_SETS[n]
    for key, tags in NICHE_HASHTAG_SETS.items():
        if n in key or key in n:
            return tags
    return {}


def get_hashtag_strategy(platform: str, niche: str) -> Dict[str, Any]:
    platform = platform.lower()
    rules = HASHTAG_RULES.get(platform, HASHTAG_RULES["tiktok"]).copy()
    niche_tags = _resolve_niche(niche)

    if platform == "tiktok":
        recommended = (
            niche_tags.get("mega", [])[:1]
            + niche_tags.get("niche", [])[:2]
            + ["#fyp", "#foryou"]
        )
    elif platform == "instagram":
        recommended = list(
            dict.fromkeys(
                niche_tags.get("mega", [])
                + niche_tags.get("niche", [])
                + niche_tags.get("engagement", [])
                + niche_tags.get("platform", [])
            )
        )[:20]
    else:
        recommended = niche_tags.get("mega", [])[:2] + niche_tags.get("niche", [])[:3]

    return {
        "platform": platform,
        "niche": niche,
        "recommended_hashtags": recommended[:20],
        **rules,
        "all_niche_tags": niche_tags,
    }


def get_optimal_posting_times(platform: str, timezone: str = "EST") -> Dict[str, Any]:
    platform = platform.lower()
    times = OPTIMAL_TIMES.get(platform, OPTIMAL_TIMES["tiktok"])
    day = datetime.now().strftime("%a")
    return {
        "platform": platform,
        "timezone_note": f"Times shown are general best-practice; adjust to your audience's timezone (provided: {timezone})",
        "today": {"day": day, "best_times": times.get(day, [])},
        "full_week": times,
        "tips": [
            "Post consistently at the same times daily",
            "Run a 30-day test at these times then adjust using native analytics",
            "TikTok: aim for 1-3 posts/day to maximise algorithmic exposure",
            "YouTube: 2-3 videos/week sustains subscriber growth without burnout",
            "Instagram: Reels perform best within 1 hr of your audience waking up",
        ],
    }


def audit_account_profile(platform: str, username: str) -> Dict[str, Any]:
    return {
        "platform": platform,
        "username": username,
        "checklist": {
            "profile_basics": [
                {"item": "Profile picture is high-quality and on-brand", "priority": "HIGH"},
                {"item": "Username is short, memorable, and searchable", "priority": "HIGH"},
                {"item": "Bio includes niche-relevant keywords", "priority": "HIGH"},
                {"item": "Bio has a clear call-to-action (CTA)", "priority": "HIGH"},
                {"item": "Link-in-bio is active and leads to a conversion page", "priority": "HIGH"},
            ],
            "content_strategy": [
                {"item": "Hook viewers within the first 1-3 seconds", "priority": "HIGH"},
                {"item": f"Posting at least {POSTING_FREQUENCY.get(platform.lower(), '1x/day')}", "priority": "HIGH"},
                {"item": "Trending sounds/music used on TikTok posts", "priority": "MEDIUM"},
                {"item": "Captions/subtitles added to all videos", "priority": "MEDIUM"},
                {"item": "3-5 defined content pillars (themes)", "priority": "HIGH"},
            ],
            "growth_tactics": [
                {"item": "Reply to every comment within the first hour of posting", "priority": "HIGH"},
                {"item": "Engage with similar accounts in your niche daily", "priority": "HIGH"},
                {"item": "Collaborate with creators at similar follower counts", "priority": "MEDIUM"},
                {"item": "Cross-post Reels/Shorts across platforms", "priority": "MEDIUM"},
                {"item": "Use 3-5 targeted hashtags per post", "priority": "MEDIUM"},
            ],
            "monetization_readiness": [
                {"item": "Creator/Business account enabled", "priority": "HIGH"},
                {"item": "Analytics tracking reviewed weekly", "priority": "HIGH"},
                {"item": "Affiliate links set up in bio/Linktree", "priority": "MEDIUM"},
                {"item": "Platform monetisation threshold reached", "priority": "HIGH"},
                {"item": "Media kit created for brand outreach", "priority": "MEDIUM"},
            ],
        },
        "scoring_guide": {
            "0-25%": "Needs major overhaul",
            "26-50%": "Room for significant improvement",
            "51-75%": "Good – focus on growth tactics",
            "76-100%": "Well-optimised – focus on monetisation",
        },
    }


def generate_content_pillars(niche: str, platform: str) -> Dict[str, Any]:
    pillars = CONTENT_PILLAR_TEMPLATES.get(
        niche.lower(),
        [
            f"{niche.capitalize()} tutorials & how-tos",
            f"{niche.capitalize()} tips & tricks",
            f"Behind the scenes ({niche})",
            f"{niche.capitalize()} product / tool reviews",
            "Community & engagement content",
        ],
    )
    return {
        "niche": niche,
        "platform": platform,
        "content_pillars": pillars,
        "content_mix": {
            "educational": "40%",
            "entertaining": "30%",
            "promotional": "20%",
            "community": "10%",
        },
        "recommended_frequency": POSTING_FREQUENCY.get(platform.lower(), "Daily posting recommended"),
        "ideas_per_pillar_per_month": 8,
        "total_monthly_content": len(pillars) * 8,
    }
