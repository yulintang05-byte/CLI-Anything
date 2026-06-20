"""Account optimization engine — analyze trend data and generate platform-specific recommendations."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


PLATFORM_SPECS = {
    "tiktok": {
        "optimal_post_times": ["7am", "11am", "7pm", "9pm"],
        "post_frequency": "3-5 videos/week",
        "video_length": "15-60 seconds for maximum reach",
        "caption_length": "under 150 characters",
        "hashtag_count": "3-5 targeted hashtags",
        "hook_window_seconds": 3,
        "completion_rate_target": 0.75,
        "algorithm_signals": ["watch time", "replays", "shares", "comments", "follows from video"],
        "content_pillars": 4,
        "growth_path": "Smaller accounts still have viral pathway via FYP algorithm",
    },
    "instagram": {
        "optimal_post_times": ["9am", "11am", "1pm", "7pm"],
        "post_frequency": "3-5 Reels/week + 1-2 static posts/week",
        "video_length": "7-15 seconds for Reels (max 90s)",
        "caption_length": "125-150 characters for preview; full caption up to 2200",
        "hashtag_count": "5-10 niche-relevant hashtags (avoid banned tags)",
        "hook_window_seconds": 2,
        "completion_rate_target": 0.80,
        "algorithm_signals": ["saves", "shares (DMs)", "watch time", "likes", "comments"],
        "content_pillars": 3,
        "growth_path": "Originality Score rewards native content; cross-posted TikToks penalized",
    },
    "youtube_shorts": {
        "optimal_post_times": ["12pm", "3pm", "6pm", "9pm"],
        "post_frequency": "3-7 Shorts/week",
        "video_length": "15-59 seconds (sub-60 performs best)",
        "caption_length": "title under 70 chars; description with keywords",
        "hashtag_count": "3-5 in description (#Shorts mandatory)",
        "hook_window_seconds": 3,
        "completion_rate_target": 0.70,
        "algorithm_signals": ["likes", "subscriptions from Short", "shares", "swipe-aways (negative)"],
        "content_pillars": 4,
        "growth_path": "Shorts feed exposes non-subscribers; high swipe-away kills distribution",
    },
}


def optimize_account(
    platform: str,
    niche: str,
    current_followers: int = 0,
    avg_views: int = 0,
    post_frequency_per_week: int = 0,
    trending_hashtags: list[str] | None = None,
    trending_sounds: list[dict] | None = None,
    account_goals: list[str] | None = None,
) -> dict:
    """Generate optimization recommendations for a social media account.

    Args:
        platform: 'tiktok', 'instagram', or 'youtube_shorts'.
        niche: Account niche/topic (e.g., 'fitness', 'finance', 'comedy').
        current_followers: Current follower count.
        avg_views: Average views per post.
        post_frequency_per_week: How often they currently post.
        trending_hashtags: List of trending hashtag names from trend scraper.
        trending_sounds: List of trending sound dicts from TikTok scraper.
        account_goals: List of goals (e.g., ['grow_followers', 'monetize', 'drive_traffic']).

    Returns:
        Optimization report with scored recommendations.
    """
    platform = platform.lower().replace(" ", "_").replace("-", "_")
    if platform not in PLATFORM_SPECS:
        available = list(PLATFORM_SPECS.keys())
        raise ValueError(f"Unknown platform '{platform}'. Available: {available}")

    specs = PLATFORM_SPECS[platform]
    goals = account_goals or ["grow_followers"]

    engagement_rate = _calc_engagement_rate(current_followers, avg_views)
    account_stage = _classify_account_stage(current_followers)

    recommendations = []

    # Posting frequency recommendation
    rec_freq = specs["post_frequency"]
    if post_frequency_per_week < 3:
        recommendations.append({
            "priority": "critical",
            "category": "posting_frequency",
            "issue": f"Posting only {post_frequency_per_week}x/week (recommended: {rec_freq})",
            "action": f"Increase to {rec_freq} — consistency is the #1 growth lever on {platform}",
            "impact": "high",
        })
    else:
        recommendations.append({
            "priority": "good",
            "category": "posting_frequency",
            "issue": f"Current: {post_frequency_per_week}x/week",
            "action": f"Maintain {rec_freq}; batch-create content to stay consistent",
            "impact": "medium",
        })

    # Timing recommendation
    recommendations.append({
        "priority": "medium",
        "category": "optimal_timing",
        "issue": "Post timing affects initial reach",
        "action": f"Post during peak hours: {', '.join(specs['optimal_post_times'])} (audience timezone)",
        "impact": "medium",
    })

    # Hook recommendation
    recommendations.append({
        "priority": "critical",
        "category": "content_hook",
        "issue": f"First {specs['hook_window_seconds']}s determine if viewer stays",
        "action": (
            f"Open every video with a scroll-stopping hook in under {specs['hook_window_seconds']}s. "
            "Use pattern-interrupt, bold statement, or visual surprise. "
            "Never start with 'Hey guys' or slow intros."
        ),
        "impact": "high",
    })

    # Algorithm signals recommendation
    signals = specs["algorithm_signals"]
    recommendations.append({
        "priority": "high",
        "category": "algorithm_signals",
        "issue": "Not all engagements are equal",
        "action": (
            f"Optimize for: {', '.join(signals[:3])}. "
            f"These carry the most weight on {platform}. "
            "End videos with a specific CTA that drives the top signal."
        ),
        "impact": "high",
    })

    # Hashtag recommendation with trend data
    hashtag_action = f"Use {specs['hashtag_count']} per post: 1 broad, 1-2 niche-specific, 1-2 trending"
    if trending_hashtags:
        top5 = trending_hashtags[:5]
        hashtag_action += f". Current trending tags to test: {', '.join('#' + h for h in top5)}"
    recommendations.append({
        "priority": "medium",
        "category": "hashtag_strategy",
        "issue": "Hashtags aid discovery but are secondary to watch time",
        "action": hashtag_action,
        "impact": "medium",
    })

    # Trending sounds (TikTok/Instagram specific)
    if platform in ("tiktok", "instagram") and trending_sounds:
        top_sound = trending_sounds[0]
        recommendations.append({
            "priority": "high",
            "category": "trending_audio",
            "issue": "Audio is the primary discovery mechanism on TikTok/Reels",
            "action": (
                f"Use trending sound '{top_sound.get('title', '')}' by {top_sound.get('artist', '')} "
                f"(used in {top_sound.get('usage_count', 0):,} videos). "
                "Incorporate trending audio within 48h of it hitting trending — early movers get more reach."
            ),
            "impact": "high",
        })

    # Content pillars recommendation
    recommendations.append({
        "priority": "medium",
        "category": "content_strategy",
        "issue": f"Random content prevents audience retention",
        "action": (
            f"Build {specs['content_pillars']} content pillars for the '{niche}' niche. "
            "Example for any niche: Educational (30%), Entertainment (30%), "
            "Trending/Reactive (20%), Personal/BTS (20%). "
            "Consistency in pillars builds subscriber expectations."
        ),
        "impact": "high",
    })

    # Originality recommendation (Instagram-specific)
    if platform == "instagram":
        recommendations.append({
            "priority": "high",
            "category": "originality",
            "issue": "Instagram Originality Score penalizes recycled content",
            "action": (
                "Never repost TikToks with watermarks — re-record natively. "
                "Instagram 2026 heavily suppresses cross-posted content. "
                f"Growth path: {specs['growth_path']}"
            ),
            "impact": "high",
        })

    # Stage-specific recommendations
    stage_rec = _stage_recommendation(account_stage, platform, niche)
    recommendations.append(stage_rec)

    # Engagement rate analysis
    eng_rec = _engagement_recommendation(engagement_rate, platform)
    recommendations.append(eng_rec)

    # Score and sort
    priority_order = {"critical": 0, "high": 1, "medium": 2, "good": 3, "low": 4}
    recommendations.sort(key=lambda r: priority_order.get(r["priority"], 5))

    return {
        "platform": platform,
        "niche": niche,
        "account_stage": account_stage,
        "current_followers": current_followers,
        "avg_views": avg_views,
        "engagement_rate_pct": round(engagement_rate * 100, 2),
        "engagement_health": _rate_engagement(engagement_rate),
        "post_frequency_per_week": post_frequency_per_week,
        "goals": goals,
        "platform_specs": specs,
        "recommendations": recommendations,
        "critical_count": sum(1 for r in recommendations if r["priority"] == "critical"),
        "high_count": sum(1 for r in recommendations if r["priority"] == "high"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def optimize_all_accounts(
    accounts: list[dict],
    trending_hashtags: list[str] | None = None,
    trending_sounds: list[dict] | None = None,
) -> list[dict]:
    """Optimize multiple accounts in one call.

    Each account dict should have: platform, niche, and optionally
    current_followers, avg_views, post_frequency_per_week, account_goals.
    """
    results = []
    for acc in accounts:
        platform = acc.get("platform", "tiktok")
        niche = acc.get("niche", "general")
        try:
            result = optimize_account(
                platform=platform,
                niche=niche,
                current_followers=acc.get("current_followers", 0),
                avg_views=acc.get("avg_views", 0),
                post_frequency_per_week=acc.get("post_frequency_per_week", 0),
                trending_hashtags=trending_hashtags,
                trending_sounds=trending_sounds,
                account_goals=acc.get("account_goals"),
            )
            result["account_name"] = acc.get("name", f"{platform}_{niche}")
            results.append(result)
        except Exception as e:
            results.append({
                "account_name": acc.get("name", "unknown"),
                "platform": platform,
                "error": str(e),
            })
    return results


# ── Helpers ───────────────────────────────────────────────────────────

def _calc_engagement_rate(followers: int, avg_views: int) -> float:
    if followers <= 0:
        return 0.0
    return avg_views / followers


def _classify_account_stage(followers: int) -> str:
    if followers == 0:
        return "brand_new"
    if followers < 1_000:
        return "nano"
    if followers < 10_000:
        return "micro"
    if followers < 100_000:
        return "mid_tier"
    if followers < 1_000_000:
        return "macro"
    return "mega"


def _rate_engagement(rate: float) -> str:
    if rate >= 0.15:
        return "excellent"
    if rate >= 0.06:
        return "good"
    if rate >= 0.03:
        return "average"
    if rate >= 0.01:
        return "below_average"
    return "poor"


def _stage_recommendation(stage: str, platform: str, niche: str) -> dict:
    actions = {
        "brand_new": (
            "Start with 30-day challenge: post daily in your niche. "
            "Speed of feedback beats perfection — ship fast, improve from data. "
            "Study top 3 accounts in your niche; reverse-engineer their formats."
        ),
        "nano": (
            "Focus on one content format that's working and repeat it. "
            "Engage every single comment in your first hour after posting — "
            "early engagement signals velocity to the algorithm."
        ),
        "micro": (
            "Now is the time to test trending audio and hashtag strategies. "
            "Collab with 2-3 accounts of similar size in adjacent niches. "
            "Start building an email list — social audiences are rented."
        ),
        "mid_tier": (
            "Introduce brand deals or affiliate products — your CPM is high enough. "
            "Create a consistent series format (e.g., weekly 'X mistakes people make'). "
            "Repurpose your best-performing content across platforms."
        ),
        "macro": (
            "Double down on what's working. Diversify revenue (merchandise, community, course). "
            "Hire a content editor/manager — bottleneck shifts from creation to distribution."
        ),
        "mega": (
            "Focus on IP development, franchises, and vertical businesses. "
            "Platform diversification is critical — don't be one-platform dependent."
        ),
    }
    return {
        "priority": "high",
        "category": "growth_stage",
        "issue": f"Account stage: {stage}",
        "action": actions.get(stage, "Focus on consistency and audience research."),
        "impact": "high",
    }


def _engagement_recommendation(rate: float, platform: str) -> dict:
    health = _rate_engagement(rate)
    if health in ("excellent", "good"):
        action = (
            f"Engagement rate ({rate * 100:.1f}%) is strong. "
            "Leverage this for brand deals — highlight it in your media kit. "
            "Focus on converting engaged followers to email subscribers or community members."
        )
        priority = "good"
    elif health == "average":
        action = (
            f"Engagement rate ({rate * 100:.1f}%) is average. "
            "Increase direct CTAs: ask a question at the end of each video. "
            "Reply to every comment in the first 60 minutes to boost comment velocity."
        )
        priority = "medium"
    else:
        action = (
            f"Engagement rate ({rate * 100:.1f}%) needs improvement. "
            "Audit your last 10 posts — what topic/format drove the most comments? "
            "Create more content specifically designed to provoke responses: "
            "polls, controversial takes, 'comment your answer' prompts."
        )
        priority = "high"

    return {
        "priority": priority,
        "category": "engagement_rate",
        "issue": f"Engagement health: {health}",
        "action": action,
        "impact": "high",
    }
