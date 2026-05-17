#!/usr/bin/env python3
"""Account optimization engine — score, analyze, and generate action plans."""

import time
from typing import Optional


# Niche-specific optimization profiles
_NICHE_PROFILES = {
    "fitness": {
        "best_post_times": ["6:00 AM", "12:00 PM", "5:30 PM", "8:00 PM"],
        "post_frequency": "1-2x/day",
        "content_split": {"educational": 40, "motivational": 30, "entertainment": 20, "promotional": 10},
        "caption_length": "short (1-3 lines) + CTA",
        "hashtag_count": {"tiktok": 5, "instagram": 15, "youtube": 5},
        "top_hashtags": ["#fitness", "#gym", "#workout", "#fitnessmotivation", "#bodybuilding", "#healthylifestyle"],
        "hook_templates": [
            "If you're not doing X, you're leaving gains on the table",
            "The workout that changed my physique in [N] weeks:",
            "Stop making this gym mistake — here's what to do instead",
            "Day [N] of [challenge] — real results incoming",
        ],
        "optimal_video_length": {"tiktok": "15-30s", "youtube_shorts": "under 60s", "youtube_long": "8-15min"},
        "monetization": ["fitness app affiliate", "supplement brands", "gym gear", "online coaching"],
    },
    "cooking": {
        "best_post_times": ["11:00 AM", "5:00 PM", "7:00 PM"],
        "post_frequency": "1x/day",
        "content_split": {"tutorial": 50, "recipe_reveal": 30, "food_story": 10, "promotional": 10},
        "caption_length": "medium (ingredients list) + CTA",
        "hashtag_count": {"tiktok": 5, "instagram": 12, "youtube": 8},
        "top_hashtags": ["#recipe", "#foodtok", "#cooking", "#easyrecipes", "#foodlover", "#homecooking"],
        "hook_templates": [
            "This [dish] takes [N] minutes and tastes like a restaurant:",
            "I tried the viral [food] recipe — here's what happened",
            "The [ingredient] trick chefs don't want you to know",
            "POV: You finally learn to make [dish]",
        ],
        "optimal_video_length": {"tiktok": "30-60s", "youtube_shorts": "under 60s", "youtube_long": "10-20min"},
        "monetization": ["kitchen affiliate", "food delivery apps", "meal kit sponsors", "cookbook"],
    },
    "travel": {
        "best_post_times": ["8:00 AM", "7:00 PM", "9:00 PM"],
        "post_frequency": "5-7x/week",
        "content_split": {"destination_showcase": 40, "tips_hacks": 30, "vlog": 20, "promotional": 10},
        "caption_length": "medium (story + tip) + CTA",
        "hashtag_count": {"tiktok": 8, "instagram": 20, "youtube": 6},
        "top_hashtags": ["#travel", "#travelgram", "#wanderlust", "#traveltok", "#vacation", "#adventure"],
        "hook_templates": [
            "[Country] on [budget] — full breakdown:",
            "Hidden gems in [place] that tourists miss:",
            "I lived in [city] for [N] days — honest review",
            "How I travel [frequency] for under $[amount]/month",
        ],
        "optimal_video_length": {"tiktok": "30-60s", "youtube_shorts": "under 60s", "youtube_long": "15-25min"},
        "monetization": ["hotel affiliate", "booking platforms", "travel cards", "travel insurance"],
    },
    "finance": {
        "best_post_times": ["7:00 AM", "12:00 PM", "6:00 PM"],
        "post_frequency": "1x/day",
        "content_split": {"educational": 50, "case_study": 25, "opinion": 15, "promotional": 10},
        "caption_length": "short + strong CTA to link in bio",
        "hashtag_count": {"tiktok": 5, "instagram": 10, "youtube": 5},
        "top_hashtags": ["#investing", "#money", "#financetok", "#personalfinance", "#wealth", "#stocks"],
        "hook_templates": [
            "How I made $[amount] doing [strategy] — step by step:",
            "The [N] money mistakes keeping you broke:",
            "If I had to start from $0 today, I would do this:",
            "This [strategy] makes your money work while you sleep",
        ],
        "optimal_video_length": {"tiktok": "30-45s", "youtube_shorts": "under 60s", "youtube_long": "12-20min"},
        "monetization": ["investment platforms affiliate", "fintech apps", "digital courses", "consulting"],
    },
    "fashion": {
        "best_post_times": ["12:00 PM", "3:00 PM", "8:00 PM"],
        "post_frequency": "1-2x/day",
        "content_split": {"ootd": 40, "styling_tips": 30, "haul": 20, "promotional": 10},
        "caption_length": "short + outfit details + CTA",
        "hashtag_count": {"tiktok": 8, "instagram": 20, "youtube": 5},
        "top_hashtags": ["#fashion", "#ootd", "#style", "#outfitinspo", "#fashiontok", "#streetstyle"],
        "hook_templates": [
            "How to style [item] [N] different ways:",
            "I only bought [N] pieces this month — here's every outfit",
            "POV: Finding your personal style on a budget",
            "[Season] outfit formula that always works:",
        ],
        "optimal_video_length": {"tiktok": "15-45s", "youtube_shorts": "under 60s", "youtube_long": "10-15min"},
        "monetization": ["LTK affiliate", "Amazon fashion", "brand deals", "Depop/reselling"],
    },
    "beauty": {
        "best_post_times": ["9:00 AM", "1:00 PM", "7:00 PM"],
        "post_frequency": "1x/day",
        "content_split": {"tutorial": 40, "review": 30, "routine": 20, "promotional": 10},
        "caption_length": "medium (products used) + CTA",
        "hashtag_count": {"tiktok": 8, "instagram": 15, "youtube": 6},
        "top_hashtags": ["#beauty", "#skincare", "#makeup", "#beautytok", "#grwm", "#makeuptutorial"],
        "hook_templates": [
            "POV: You finally find your [skin concern] solution",
            "[Expensive product] dupe that actually works:",
            "My [N]-step routine that cleared my skin in [time]",
            "Testing viral [product] — worth the hype?",
        ],
        "optimal_video_length": {"tiktok": "30-60s", "youtube_shorts": "under 60s", "youtube_long": "12-18min"},
        "monetization": ["Sephora affiliate", "brand deals", "Amazon beauty", "own product line"],
    },
    "gaming": {
        "best_post_times": ["4:00 PM", "7:00 PM", "10:00 PM"],
        "post_frequency": "1-2x/day",
        "content_split": {"highlights": 40, "tutorial": 30, "commentary": 20, "promotional": 10},
        "caption_length": "short + game name + CTA",
        "hashtag_count": {"tiktok": 6, "instagram": 12, "youtube": 8},
        "top_hashtags": ["#gaming", "#gamer", "#fps", "#gamingclips", "#streamer", "#esports"],
        "hook_templates": [
            "How I went from [rank] to [rank] in [N] days:",
            "The trick most [game] players don't know:",
            "Average player vs 1000-hour player moment:",
            "I used [unusual strategy] for [N] games — results:",
        ],
        "optimal_video_length": {"tiktok": "15-30s", "youtube_shorts": "under 60s", "youtube_long": "10-20min"},
        "monetization": ["gaming gear affiliate", "game keys", "coaching", "channel memberships"],
    },
    "general": {
        "best_post_times": ["8:00 AM", "12:00 PM", "7:00 PM"],
        "post_frequency": "1x/day",
        "content_split": {"educational": 35, "entertainment": 35, "personal": 20, "promotional": 10},
        "caption_length": "short + CTA",
        "hashtag_count": {"tiktok": 5, "instagram": 12, "youtube": 5},
        "top_hashtags": ["#fyp", "#foryou", "#viral", "#trending", "#explore"],
        "hook_templates": [
            "If you [pain point], watch this:",
            "[N] things I wish I knew before [topic]:",
            "The [topic] strategy that actually works in [year]:",
            "Why [common belief] is wrong — and what to do instead:",
        ],
        "optimal_video_length": {"tiktok": "15-45s", "youtube_shorts": "under 60s", "youtube_long": "8-15min"},
        "monetization": ["affiliate marketing", "sponsorships", "digital products"],
    },
}


def optimize_account(niche: str, platform: str, follower_count: int = 0,
                     avg_views: int = 0, avg_likes: int = 0) -> dict:
    """
    Generate a comprehensive account optimization plan.

    Args:
        niche: Content niche (fitness, cooking, travel, finance, etc.)
        platform: tiktok, youtube, instagram, or all
        follower_count: Current follower count (for tier-specific advice)
        avg_views: Average views per video
        avg_likes: Average likes per video
    """
    profile = _NICHE_PROFILES.get(niche.lower(), _NICHE_PROFILES["general"])
    tier = _get_account_tier(follower_count)
    engagement_rate = _calc_engagement_rate(follower_count, avg_likes)
    score = _score_account(follower_count, avg_views, avg_likes, niche)
    action_plan = _build_action_plan(profile, platform, tier, engagement_rate, niche)

    result = {
        "platform": platform,
        "niche": niche,
        "account_tier": tier,
        "engagement_rate": f"{engagement_rate:.2f}%",
        "optimization_score": score,
        "posting_schedule": {
            "best_times": profile["best_post_times"],
            "frequency": profile["post_frequency"],
            "notes": f"Post consistently for 21+ days to train the algorithm",
        },
        "content_strategy": {
            "content_mix": profile["content_split"],
            "recommended_length": profile["optimal_video_length"].get(
                platform, profile["optimal_video_length"].get("tiktok", "30-60s")
            ),
            "hook_templates": profile["hook_templates"],
            "caption_length": profile["caption_length"],
        },
        "hashtag_strategy": {
            "recommended_count": profile["hashtag_count"].get(platform, 10),
            "top_hashtags": profile["top_hashtags"],
            "strategy": _hashtag_strategy(platform, niche, tier),
        },
        "monetization_paths": profile["monetization"],
        "action_plan": action_plan,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    if follower_count > 0:
        result["current_stats"] = {
            "followers": follower_count,
            "avg_views": avg_views,
            "avg_likes": avg_likes,
            "engagement_rate": f"{engagement_rate:.2f}%",
        }

    return result


def _get_account_tier(followers: int) -> str:
    if followers == 0:
        return "new"
    if followers < 1000:
        return "nano"
    if followers < 10000:
        return "micro"
    if followers < 100000:
        return "mid"
    if followers < 1000000:
        return "macro"
    return "mega"


def _calc_engagement_rate(followers: int, avg_likes: int) -> float:
    if followers == 0:
        return 0.0
    return (avg_likes / followers) * 100


def _score_account(followers: int, avg_views: int, avg_likes: int, niche: str) -> dict:
    scores = {}

    # Follower score (0-100)
    if followers == 0:
        scores["followers"] = 0
    elif followers < 1000:
        scores["followers"] = int((followers / 1000) * 30)
    elif followers < 10000:
        scores["followers"] = 30 + int(((followers - 1000) / 9000) * 30)
    elif followers < 100000:
        scores["followers"] = 60 + int(((followers - 10000) / 90000) * 30)
    else:
        scores["followers"] = min(100, 90 + int((followers / 1000000) * 10))

    # Engagement score (0-100)
    if followers > 0 and avg_likes > 0:
        er = (avg_likes / followers) * 100
        if er < 1:
            scores["engagement"] = int(er * 20)
        elif er < 3:
            scores["engagement"] = 20 + int(((er - 1) / 2) * 40)
        elif er < 6:
            scores["engagement"] = 60 + int(((er - 3) / 3) * 30)
        else:
            scores["engagement"] = min(100, 90 + int(er))
    else:
        scores["engagement"] = 0

    # Virality score (view:follower ratio)
    if followers > 0 and avg_views > 0:
        ratio = avg_views / followers
        if ratio >= 3:
            scores["virality"] = min(100, int(ratio * 10))
        elif ratio >= 1:
            scores["virality"] = 50 + int((ratio - 1) * 25)
        else:
            scores["virality"] = int(ratio * 50)
    else:
        scores["virality"] = 0

    total = int((scores["followers"] * 0.3 + scores["engagement"] * 0.4 + scores["virality"] * 0.3))
    return {
        "total": total,
        "breakdown": scores,
        "grade": _score_to_grade(total),
        "verdict": _score_verdict(total),
    }


def _score_to_grade(score: int) -> str:
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B+"
    if score >= 60:
        return "B"
    if score >= 50:
        return "C+"
    if score >= 40:
        return "C"
    return "D"


def _score_verdict(score: int) -> str:
    if score >= 80:
        return "High-performing account — focus on monetization and scaling"
    if score >= 60:
        return "Growing well — double down on content consistency and hooks"
    if score >= 40:
        return "Building phase — prioritize niche clarity and posting schedule"
    if score >= 20:
        return "Early stage — focus on finding your viral content style"
    return "New account — post daily, test content types, find your hook formula"


def _hashtag_strategy(platform: str, niche: str, tier: str) -> list[str]:
    base = [
        "Use 3 tiers: 1-2 mega tags (#fyp), 2-3 mid tags (#[niche]), 2-3 niche tags (#[specific topic])",
        "Rotate hashtag sets every 3-5 posts to avoid shadowban signals",
        "Include 1 location-based tag if targeting a local audience",
        "Never use banned or flagged hashtags — audit your list monthly",
    ]
    if platform == "tiktok":
        base.append("On TikTok, 3-5 focused hashtags outperform 20+ generic ones")
        base.append("Use TikTok Creative Center to check hashtag growth curves before posting")
    elif platform == "instagram":
        base.append("Instagram allows 30 hashtags — use 10-15 highly relevant ones")
        base.append("Mix hashtag sizes: some under 500k posts for better ranking chance")
    elif platform == "youtube":
        base.append("YouTube hashtags go in description — use 3-5 max, add to title if relevant")
    if tier in ("new", "nano"):
        base.append("Target smaller hashtags (under 500k posts) where you can rank on page 1")
    elif tier in ("mid", "macro", "mega"):
        base.append("You can now target larger hashtags — your authority helps you rank")
    return base


def _build_action_plan(profile: dict, platform: str, tier: str,
                        engagement_rate: float, niche: str) -> list[dict]:
    """Generate a prioritized 30-day action plan."""
    week1 = {
        "week": 1,
        "focus": "Foundation & Consistency",
        "tasks": [
            "Audit your profile: clear niche statement in bio, CTA in bio (link or follow)",
            "Create a content bank of 21 ideas using the hook templates",
            f"Post {profile['post_frequency']} at these times: {', '.join(profile['best_post_times'][:2])}",
            "Test 3 different hook styles — track which gets highest 3-second retention",
            "Set up a content pillars doc: educational / entertaining / promotional split",
        ],
    }
    week2 = {
        "week": 2,
        "focus": "Hook & Retention Optimization",
        "tasks": [
            "Analyze which of your week-1 posts got highest completion rate — double down on that style",
            "A/B test thumbnail/cover image styles (if applicable)",
            "Engage with top 10 creators in your niche: genuine comments build community awareness",
            "Create one 'list-based' video and one 'transformation/before-after' video",
            "Add a verbal CTA at the 50% mark of every video ('Follow for more [value]')",
        ],
    }
    week3 = {
        "week": 3,
        "focus": "Trending Content Integration",
        "tasks": [
            "Identify 2-3 trending sounds this week and create niche-specific content using them",
            "Jump on 1 trending hashtag challenge that fits your niche",
            "Create a 'comment bait' video — ask a question that your audience wants to answer",
            "Cross-post your best performing content to a second platform",
            "Pin your best-performing video to top of profile",
        ],
    }
    week4 = {
        "week": 4,
        "focus": "Monetization Prep & Scale",
        "tasks": [
            f"Begin outreach to micro-brand partnerships in {niche} (DM 5 brands/week)",
            "Create a media kit: follower count, engagement rate, niche audience demographics",
            "Set up affiliate links for: " + ", ".join(profile["monetization"][:2]),
            "Launch a 'value bomb' piece of content designed to generate saves/shares",
            "Review analytics: double down on top 3 performing video formats next month",
        ],
    }

    ongoing = {
        "week": "ongoing",
        "focus": "Sustainable Growth",
        "tasks": [
            "Check trending sounds every Monday — adapt 1-2 per week",
            "Reply to every comment in first hour after posting (algorithm signal)",
            "Batch-create content 1 week ahead to maintain consistency",
            "Monthly: audit hashtag sets, check competitors' top posts, update hook library",
            "Quarterly: revisit content mix percentages based on analytics",
        ],
    }

    return [week1, week2, week3, week4, ongoing]


def generate_report(accounts: list[dict]) -> dict:
    """Generate a multi-account optimization report."""
    reports = []
    for acct in accounts:
        niche = acct.get("niche", "general")
        platform = acct.get("platform", "tiktok")
        report = optimize_account(
            niche=niche,
            platform=platform,
            follower_count=acct.get("followers", 0),
            avg_views=acct.get("avg_views", 0),
            avg_likes=acct.get("avg_likes", 0),
        )
        report["account_name"] = acct.get("name", f"{platform}/{niche}")
        reports.append(report)

    return {
        "total_accounts": len(reports),
        "reports": reports,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
