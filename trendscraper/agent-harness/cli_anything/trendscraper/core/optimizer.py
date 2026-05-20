"""Social media account optimizer — captions, posting times, content strategy.

Analyzes trending data and produces actionable optimization for:
- TikTok, Instagram Reels, YouTube Shorts, Twitter/X
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

_CONFIG_DIR = Path.home() / ".config" / "cli-anything-trendscraper"

# Optimal posting windows (UTC hours) per platform from aggregated studies
OPTIMAL_POST_TIMES: dict[str, list[dict]] = {
    "tiktok": [
        {"day": "Tuesday", "hours": [9, 15, 21], "note": "Highest engagement"},
        {"day": "Thursday", "hours": [12, 15, 21], "note": "Peak hours"},
        {"day": "Friday", "hours": [5, 13, 21], "note": "Friday viral window"},
        {"day": "Saturday", "hours": [11, 19, 20], "note": "Weekend peak"},
    ],
    "instagram": [
        {"day": "Monday", "hours": [6, 12, 18], "note": "Week opener"},
        {"day": "Wednesday", "hours": [11, 13, 20], "note": "Mid-week peak"},
        {"day": "Friday", "hours": [10, 16, 19], "note": "TGIF spike"},
        {"day": "Sunday", "hours": [19, 20, 21], "note": "Sunday evening"},
    ],
    "youtube": [
        {"day": "Thursday", "hours": [12, 15, 17], "note": "Pre-weekend views"},
        {"day": "Friday", "hours": [12, 15, 17], "note": "Friday views peak"},
        {"day": "Saturday", "hours": [9, 11, 16], "note": "Weekend binge"},
        {"day": "Sunday", "hours": [9, 11, 16], "note": "Sunday catch-up"},
    ],
    "twitter": [
        {"day": "Tuesday", "hours": [8, 9, 12], "note": "News cycle peak"},
        {"day": "Wednesday", "hours": [8, 9, 12], "note": "Mid-week engagement"},
        {"day": "Thursday", "hours": [8, 9, 12], "note": "Thursday news spike"},
    ],
}

HASHTAG_COUNTS_BY_PLATFORM: dict[str, dict] = {
    "tiktok": {"min": 3, "max": 5, "note": "3-5 targeted hashtags outperform keyword spam"},
    "instagram": {"min": 5, "max": 15, "note": "Mix niche (3-5), medium (5-7), broad (3-5)"},
    "youtube": {"min": 3, "max": 8, "note": "Use in description, first 3 most important"},
    "twitter": {"min": 1, "max": 2, "note": "1-2 max — more hurts reach on Twitter/X"},
    "youtube_shorts": {"min": 3, "max": 6, "note": "Same as YouTube but more niche-specific"},
}

ENGAGEMENT_HOOKS = [
    "This will change the way you think about {topic}…",
    "Nobody talks about this {topic} hack 👇",
    "POV: You just discovered {topic}",
    "The {topic} secret nobody wants you to know",
    "I tested {topic} for 30 days — here's what happened",
    "Things they don't teach you about {topic}",
    "Day {n} of {challenge} — {milestone}",
    "Stop doing {mistake} — do THIS instead for {topic}",
    "Rate my {subject} 1-10 👇 (be honest)",
    "Replying to @{user}: Here's the truth about {topic}",
]

CAPTION_TEMPLATES: dict[str, list[str]] = {
    "motivation": [
        "Your future self will thank you for starting today. 💪\n\n{hashtags}",
        "The only person you should compete with is who you were yesterday.\n\n{hashtags}",
        "Discipline > Motivation. Here's why 🧵\n\n{hashtags}",
    ],
    "luxury": [
        "This is what success looks like 👀✨\n\n{hashtags}",
        "The lifestyle is earned, not given 🔑\n\n{hashtags}",
        "Level up or get left behind 💎\n\n{hashtags}",
    ],
    "fitness": [
        "No excuses. Results speak louder 💪\n\n{hashtags}",
        "The gym doesn't care about your feelings 🏋️\n\n{hashtags}",
        "Consistency > Perfection. Show up every day.\n\n{hashtags}",
    ],
    "finance": [
        "Your bank account reflects your habits. Change your habits, change your life 💰\n\n{hashtags}",
        "Rich people buy assets. Poor people buy liabilities. Which are you doing? 📈\n\n{hashtags}",
        "The best investment you can make is in yourself. Here's how 💡\n\n{hashtags}",
    ],
    "travel": [
        "This place exists and most people will never see it 🌍\n\n{hashtags}",
        "Life's too short to stay in one place ✈️\n\n{hashtags}",
        "Pack light, travel far, leave no trace 🌿\n\n{hashtags}",
    ],
    "generic": [
        "If this resonates, save it for later 📌\n\n{hashtags}",
        "Comment your thoughts below 👇\n\n{hashtags}",
        "Share this with someone who needs to see it 🔄\n\n{hashtags}",
    ],
}


def optimize_caption(
    text: str = "",
    platform: str = "tiktok",
    niche: str = "generic",
    trending_hashtags: list[str] | None = None,
    max_hashtags: int | None = None,
) -> dict[str, Any]:
    """Generate an optimized caption with trending hashtags for a given platform."""
    platform = platform.lower()
    ht_config = HASHTAG_COUNTS_BY_PLATFORM.get(platform, HASHTAG_COUNTS_BY_PLATFORM["tiktok"])
    limit = max_hashtags or ht_config["max"]

    tags = _select_best_hashtags(trending_hashtags or [], niche, platform, limit)
    hashtag_str = " ".join(f"#{t.lstrip('#')}" for t in tags)

    templates = CAPTION_TEMPLATES.get(niche, CAPTION_TEMPLATES["generic"])
    base_caption = (text.strip() + "\n\n" + hashtag_str) if text else templates[0].format(hashtags=hashtag_str)

    hook = _suggest_hook(niche)
    cta = _suggest_cta(platform)

    return {
        "platform": platform,
        "niche": niche,
        "caption": base_caption,
        "hashtags_used": tags,
        "hashtag_count": len(tags),
        "hashtag_strategy": ht_config["note"],
        "suggested_hook": hook,
        "call_to_action": cta,
        "character_count": len(base_caption),
        "posting_tip": OPTIMAL_POST_TIMES.get(platform, [{}])[0],
    }


def generate_content_calendar(
    niche: str = "motivation",
    platform: str = "tiktok",
    days: int = 7,
    trending_hashtags: list[str] | None = None,
) -> dict[str, Any]:
    """Generate a 7-day content calendar with post ideas and optimal timing."""
    tags = trending_hashtags or []
    calendar = []
    content_types = _content_type_rotation(niche)

    for day_num in range(days):
        from datetime import timedelta
        post_date = datetime.utcnow() + timedelta(days=day_num)
        day_name = post_date.strftime("%A")

        # Find best posting time for this day
        times = _best_time_for_day(platform, day_name)
        content_type = content_types[day_num % len(content_types)]
        idea = _generate_post_idea(niche, content_type, day_num)
        day_tags = _select_best_hashtags(tags, niche, platform, 5, seed=day_num)

        calendar.append({
            "day": day_num + 1,
            "date": post_date.strftime("%Y-%m-%d"),
            "day_name": day_name,
            "platform": platform,
            "content_type": content_type,
            "post_idea": idea,
            "suggested_times_utc": times,
            "hashtags": [f"#{t.lstrip('#')}" for t in day_tags],
            "hook": _suggest_hook(niche),
            "priority": "HIGH" if day_name in ["Tuesday", "Thursday", "Friday"] else "MEDIUM",
        })

    return {
        "niche": niche,
        "platform": platform,
        "calendar_start": datetime.utcnow().strftime("%Y-%m-%d"),
        "days": days,
        "posts": calendar,
        "weekly_tip": f"Post consistently at your peak times. For {platform}, aim for {days} posts over {days} days minimum.",
    }


def analyze_account(
    platform: str,
    followers: int = 0,
    avg_views: int = 0,
    avg_likes: int = 0,
    niche: str = "generic",
    posting_frequency: str = "daily",
) -> dict[str, Any]:
    """Analyze account health and provide optimization recommendations."""
    engagement_rate = (avg_likes / avg_views * 100) if avg_views > 0 else 0
    view_to_follower = (avg_views / followers * 100) if followers > 0 else 0

    grade = _grade_account(engagement_rate, view_to_follower, platform)
    recs = _generate_recommendations(platform, engagement_rate, view_to_follower, followers, niche, posting_frequency)

    return {
        "platform": platform,
        "niche": niche,
        "followers": followers,
        "avg_views": avg_views,
        "avg_likes": avg_likes,
        "engagement_rate": round(engagement_rate, 2),
        "view_to_follower_ratio": round(view_to_follower, 2),
        "account_grade": grade,
        "benchmarks": _benchmarks(platform),
        "recommendations": recs,
        "monetization_threshold": _monetization_threshold(platform, followers),
        "estimated_value": _estimate_page_value(platform, followers, engagement_rate, niche),
    }


def _select_best_hashtags(
    trending: list[str],
    niche: str,
    platform: str,
    limit: int,
    seed: int = 0,
) -> list[str]:
    niche_tags = _niche_hashtags(niche)
    broad_tags = _broad_tags(platform)
    pool = [t.lstrip("#").lower() for t in trending] + niche_tags + broad_tags
    seen: set[str] = set()
    unique = []
    for t in pool:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return unique[:limit]


def _niche_hashtags(niche: str) -> list[str]:
    mapping = {
        "motivation": ["motivation", "mindset", "success", "grind", "hustlehard", "goals", "discipline", "levelup", "selfimprovement", "winning"],
        "luxury": ["luxury", "rich", "wealth", "lifestyle", "millionaire", "boss", "success", "billionaire", "moneymindset", "entrepreneur"],
        "fitness": ["fitness", "gym", "workout", "gains", "fitnessmotivation", "bodybuilding", "health", "weightloss", "getfit", "training"],
        "finance": ["finance", "investing", "money", "wealth", "stocks", "crypto", "financialfreedom", "passiveincome", "realestate", "sidehustle"],
        "travel": ["travel", "wanderlust", "explore", "adventure", "backpacking", "travelphotography", "worldtravel", "nomad", "bucketlist", "travelgram"],
        "food": ["food", "foodie", "recipe", "cooking", "delicious", "foodporn", "homecooking", "easyrecipe", "mealprep", "foodlover"],
        "fashion": ["fashion", "style", "ootd", "streetwear", "outfitoftheday", "fashionblogger", "aesthetic", "lookbook", "styletips", "trend"],
        "cars": ["cars", "supercar", "exotic", "carporn", "automotivephotography", "vehicle", "carsofinstagram", "hypercar", "motorsport", "drift"],
        "gaming": ["gaming", "gamer", "videogames", "twitch", "esports", "xbox", "playstation", "pcgaming", "fps", "gameplay"],
        "beauty": ["beauty", "makeup", "skincare", "glam", "beautytips", "makeuptutorial", "skincareroutine", "beautyhacks", "foundation", "eyeshadow"],
    }
    return mapping.get(niche, ["viral", "trending", "fyp", "foryou", "explore"])


def _broad_tags(platform: str) -> list[str]:
    if platform == "tiktok":
        return ["fyp", "foryoupage", "foryou", "viral", "trending", "xyzbca"]
    elif platform == "instagram":
        return ["reels", "explore", "viral", "trending", "instadaily"]
    elif platform in ("youtube", "youtube_shorts"):
        return ["shorts", "viral", "trending", "youtube"]
    return ["viral", "trending", "explore"]


def _suggest_hook(niche: str) -> str:
    hooks = {
        "motivation": "Nobody talks about THIS side of success...",
        "luxury": "POV: You just unlocked the lifestyle 👀",
        "fitness": "I used to skip the gym every day until I did THIS",
        "finance": "The money secret rich people don't want you to know 💰",
        "travel": "This place exists and nobody is talking about it 🌍",
        "food": "This recipe broke the internet for a reason 🍽️",
        "fashion": "The outfit formula that always works 🔥",
        "cars": "When the car does something nobody expects... 🏎️",
        "gaming": "Nobody told me this trick existed until I found it",
        "beauty": "Skincare hack dermatologists don't want you knowing 💄",
        "generic": "Wait for it... 🤯",
    }
    return hooks.get(niche, hooks["generic"])


def _suggest_cta(platform: str) -> str:
    ctas = {
        "tiktok": "Comment '🔥' if this helped | Follow for daily tips",
        "instagram": "Save this for later 📌 | Tag someone who needs this",
        "youtube": "Subscribe and hit 🔔 | Comment your thoughts below",
        "twitter": "RT if you agree | Follow for more",
    }
    return ctas.get(platform, "Follow for more content like this")


def _best_time_for_day(platform: str, day_name: str) -> list[int]:
    schedule = OPTIMAL_POST_TIMES.get(platform, OPTIMAL_POST_TIMES["tiktok"])
    for entry in schedule:
        if entry["day"] == day_name:
            return entry["hours"]
    return [12, 18]


def _content_type_rotation(niche: str) -> list[str]:
    rotations = {
        "motivation": ["Quote graphic", "Personal story", "Listicle (5 tips)", "Challenge/question", "Transformation story", "Duet/reply trend", "Day-in-the-life"],
        "finance": ["Myth vs Fact", "How-to tutorial", "Case study", "Quick stat", "Tool review", "Portfolio update", "Q&A"],
        "fitness": ["Workout demo", "Before/after", "Meal prep", "Myth bust", "Training tip", "Rest day content", "Challenge"],
        "generic": ["Educational", "Entertainment", "Behind the scenes", "Q&A", "Trend hijack", "Testimonial/story", "CTA post"],
    }
    return rotations.get(niche, rotations["generic"])


def _generate_post_idea(niche: str, content_type: str, index: int) -> str:
    ideas = {
        "Quote graphic": f"Find a trending {niche} quote with high saves on Pinterest/Twitter and recreate as a video",
        "Personal story": f"Share a real struggle you overcame related to {niche} — authenticity drives shares",
        "Listicle (5 tips)": f"5 {niche} tips most people learn too late (text-on-screen or voiceover format)",
        "Challenge/question": f"Ask your audience a polarizing question about {niche} to drive comments",
        "Transformation story": f"Show before/after or journey arc in {niche} — hook viewers in first 2 seconds",
        "Duet/reply trend": "Find a viral video in your niche and duet or stitch with your take",
        "Day-in-the-life": f"A day-in-the-life focused on {niche} lifestyle and habits",
        "Educational": f"Teach one specific {niche} concept in under 60 seconds",
        "Entertainment": f"Use trending sound/meme format and apply it to {niche}",
        "Behind the scenes": f"Show the process behind your {niche} content creation",
        "Q&A": "Answer top-voted comment from your last post",
        "Trend hijack": f"Take a trending audio/format and apply it to {niche}",
    }
    return ideas.get(content_type, f"Create {content_type} content about {niche}")


def _grade_account(engagement_rate: float, view_ratio: float, platform: str) -> str:
    benchmarks = _benchmarks(platform)
    if engagement_rate >= benchmarks["great_engagement"]:
        return "A — Excellent"
    elif engagement_rate >= benchmarks["good_engagement"]:
        return "B — Good"
    elif engagement_rate >= benchmarks["avg_engagement"]:
        return "C — Average"
    else:
        return "D — Needs Work"


def _benchmarks(platform: str) -> dict:
    return {
        "tiktok": {"avg_engagement": 5.0, "good_engagement": 8.0, "great_engagement": 15.0, "viral_views": 100_000},
        "instagram": {"avg_engagement": 1.5, "good_engagement": 3.5, "great_engagement": 6.0, "viral_views": 50_000},
        "youtube": {"avg_engagement": 2.0, "good_engagement": 4.0, "great_engagement": 8.0, "viral_views": 100_000},
        "twitter": {"avg_engagement": 0.5, "good_engagement": 1.5, "great_engagement": 3.0, "viral_views": 10_000},
    }.get(platform, {"avg_engagement": 3.0, "good_engagement": 6.0, "great_engagement": 10.0, "viral_views": 50_000})


def _generate_recommendations(
    platform: str,
    engagement_rate: float,
    view_ratio: float,
    followers: int,
    niche: str,
    posting_frequency: str,
) -> list[str]:
    recs = []
    if engagement_rate < _benchmarks(platform)["avg_engagement"]:
        recs.append("Engagement below average — add a strong CTA in every post (question, poll, or 'comment X')")
        recs.append("Hook viewers in the first 1-2 seconds — 70%+ of people scroll past within 2 seconds")

    if posting_frequency not in ("daily", "twice_daily"):
        recs.append(f"Increase posting frequency to daily minimum on {platform} — consistency beats perfection")

    if platform == "tiktok":
        recs.append("Use 3-5 niche hashtags max — avoid generic #fyp spam; specificity wins on TikTok's algorithm")
        recs.append("Respond to ALL comments in first 30 minutes — this signals to the algorithm to push your video")
        recs.append("Re-use your highest-performing hooks — iterate on what works, not what's new")

    elif platform == "instagram":
        recs.append("Post Reels daily for 2x organic reach vs static posts in current algorithm")
        recs.append("Use Instagram's native features (polls, questions, countdowns) to boost reach")
        recs.append("Collab posts reach 2x audiences — DM micro-influencers in your niche for collabs")

    elif platform == "youtube":
        recs.append("CTR (click-through rate) is king — A/B test thumbnails every upload")
        recs.append("Retention drops at 30% = algorithm kill; add pattern interrupts every 60 seconds")
        recs.append("End screen + pinned comment CTA dramatically increases subscribe rate")

    if followers < 1000:
        recs.append("Focus on reach, not followers — viral content > follow requests from micro accounts")
    elif followers < 10_000:
        recs.append("You're in the growth phase — consistency and collaboration are your fastest levers")
    else:
        recs.append("Monetization-ready tier — activate brand deals, affiliate links, and digital products")

    recs.append(f"Post trending {niche} content within 24 hours of a trend emerging for maximum reach window")
    return recs


def _monetization_threshold(platform: str, followers: int) -> dict:
    thresholds = {
        "tiktok": {"brand_deals": 5_000, "creator_fund": 10_000, "live_gifts": 1_000, "tiktok_shop": 5_000},
        "instagram": {"brand_deals": 5_000, "reels_bonus": 10_000, "shopping": 200, "subscriptions": 10_000},
        "youtube": {"monetize": 1_000, "brand_deals": 10_000, "memberships": 30_000, "super_thanks": 1_000},
        "twitter": {"super_follows": 10_000, "brand_deals": 5_000, "ads_revenue": 5_000_000},
    }
    platform_thresholds = thresholds.get(platform, {})
    status = {}
    for tier, required in platform_thresholds.items():
        status[tier] = {
            "required_followers": required,
            "unlocked": followers >= required,
            "gap": max(0, required - followers),
        }
    return status


def _estimate_page_value(platform: str, followers: int, engagement_rate: float, niche: str) -> dict:
    """Estimate current page/account market value for potential sale."""
    # Industry standard: $X per 1000 followers × engagement multiplier × niche premium
    base_cpm = {"tiktok": 15, "instagram": 20, "youtube": 35, "twitter": 5}.get(platform, 10)
    engagement_mult = max(0.5, min(3.0, engagement_rate / 3.0))
    niche_premiums = {"finance": 2.5, "fitness": 1.8, "luxury": 2.0, "beauty": 1.7, "technology": 2.2, "motivation": 1.4, "generic": 1.0}
    niche_mult = niche_premiums.get(niche, 1.0)
    estimated_value = int((followers / 1000) * base_cpm * engagement_mult * niche_mult)
    return {
        "estimated_usd": estimated_value,
        "per_post_rate": int(estimated_value * 0.01),
        "note": "Estimate based on follower count, engagement, and niche. Actual value varies with content quality and audience demographics.",
    }
