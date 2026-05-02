"""Account optimization engine — scoring, checklists, and posting schedules."""

from typing import Any

# Optimal posting windows (UTC-adjusted; shown as local time recommendations)
_POSTING_SCHEDULES: dict[str, dict[str, Any]] = {
    "tiktok": {
        "best_days": ["Tuesday", "Thursday", "Friday"],
        "best_times": ["6am-9am", "12pm-2pm", "7pm-9pm"],
        "frequency": "1-3 posts/day",
        "note": "TikTok favors recency — post during peak active hours for your target timezone",
        "windows": [
            {"day": "Tuesday", "time": "7am", "score": 9},
            {"day": "Thursday", "time": "9am", "score": 10},
            {"day": "Friday", "time": "5pm", "score": 10},
            {"day": "Saturday", "time": "11am", "score": 8},
            {"day": "Sunday", "time": "7pm", "score": 8},
        ],
    },
    "youtube": {
        "best_days": ["Thursday", "Friday", "Saturday"],
        "best_times": ["2pm-4pm", "8pm-11pm"],
        "frequency": "Shorts: daily. Long-form: 2-3x/week",
        "note": "YouTube rewards consistency — same day/time weekly builds subscriber expectation",
        "windows": [
            {"day": "Thursday", "time": "3pm", "score": 9},
            {"day": "Friday", "time": "4pm", "score": 10},
            {"day": "Saturday", "time": "2pm", "score": 9},
            {"day": "Sunday", "time": "8pm", "score": 8},
        ],
    },
    "instagram": {
        "best_days": ["Monday", "Wednesday", "Friday"],
        "best_times": ["8am-10am", "11am-1pm", "7pm-9pm"],
        "frequency": "Reels: 4-7x/week. Feed posts: 3-5x/week. Stories: daily",
        "note": "Instagram Reels get 2× more reach than feed posts — prioritize Reels",
        "windows": [
            {"day": "Monday", "time": "8am", "score": 9},
            {"day": "Wednesday", "time": "11am", "score": 10},
            {"day": "Friday", "time": "1pm", "score": 9},
            {"day": "Sunday", "time": "7pm", "score": 8},
        ],
    },
}

# Account optimization checklists by platform
_OPTIMIZATION_CHECKLISTS: dict[str, list[dict]] = {
    "tiktok": [
        {"item": "Switch to Business/Creator account", "priority": "critical", "impact": "unlocks analytics + monetization"},
        {"item": "Complete profile: photo + bio + link", "priority": "critical", "impact": "+15% follow rate from profile visits"},
        {"item": "Bio includes clear niche hook (1 line max)", "priority": "high", "impact": "describes your value prop instantly"},
        {"item": "Link in bio points to landing page or link aggregator", "priority": "high", "impact": "drives off-platform conversions"},
        {"item": "Pinned video showcases best/viral content", "priority": "high", "impact": "+20% subscriber conversion from profile"},
        {"item": "Profile photo is clear face or branded image", "priority": "high", "impact": "builds trust and recognition"},
        {"item": "Post 1-3x daily at peak hours (7am, 9am, 7pm)", "priority": "high", "impact": "TikTok rewards daily activity"},
        {"item": "Use 3-5 hashtags (2 trending + 2 niche + 1 broad)", "priority": "high", "impact": "balanced hashtag strategy"},
        {"item": "First 3 seconds have strong visual hook", "priority": "critical", "impact": "prevents swipe-away; boosts watch time"},
        {"item": "Caption includes CTA (comment, duet, follow)", "priority": "medium", "impact": "+8% engagement rate average"},
        {"item": "Reply to every comment in first 2 hours", "priority": "high", "impact": "boosts algorithm rank for that video"},
        {"item": "Use trending sounds (discover > sounds)", "priority": "high", "impact": "sound-linked discovery = bonus reach"},
        {"item": "Add closed captions to all videos", "priority": "medium", "impact": "+40% watch time for non-sound viewers"},
        {"item": "Consistent posting schedule (same days/times)", "priority": "high", "impact": "builds audience habit and expectation"},
        {"item": "Cross-post to YouTube Shorts + Instagram Reels", "priority": "medium", "impact": "3× content reach with same effort"},
    ],
    "youtube": [
        {"item": "Channel art (banner) matches niche + brand colors", "priority": "high", "impact": "first impression on channel page"},
        {"item": "Channel description includes keywords for SEO", "priority": "critical", "impact": "YouTube search and recommendation ranking"},
        {"item": "Custom channel URL (@yourname)", "priority": "high", "impact": "brand recognition and shareability"},
        {"item": "Channel trailer for non-subscribers (90sec max)", "priority": "high", "impact": "+20% subscription rate from channel visits"},
        {"item": "All videos have custom thumbnails (not auto-frame)", "priority": "critical", "impact": "CTR improvement of 200-400%"},
        {"item": "Thumbnail uses bright contrast + readable text (3 words max)", "priority": "critical", "impact": "primary driver of click-through rate"},
        {"item": "Video title front-loads keyword (first 60 chars)", "priority": "critical", "impact": "SEO + CTR driver"},
        {"item": "Description has timestamps, links, and keyword-rich first 3 lines", "priority": "high", "impact": "SEO ranking + viewer UX"},
        {"item": "Add 3-5 relevant hashtags in description", "priority": "high", "impact": "hashtags appear above title on Shorts"},
        {"item": "End screen with subscribe button + next video", "priority": "high", "impact": "+15% session time"},
        {"item": "Cards link to related content at peak watch-time moments", "priority": "medium", "impact": "reduces bounce rate"},
        {"item": "Chapters/timestamps for long-form videos", "priority": "high", "impact": "YouTube shows chapter previews in search"},
        {"item": "Upload Shorts daily (repurpose existing content)", "priority": "high", "impact": "Shorts drives channel discovery in 2026"},
        {"item": "Engage in community tab (polls, updates)", "priority": "medium", "impact": "keeps subscribers active between uploads"},
        {"item": "Respond to comments in first 24 hours", "priority": "high", "impact": "boosts video in recommendation algorithm"},
    ],
    "instagram": [
        {"item": "Switch to Professional (Creator or Business) account", "priority": "critical", "impact": "unlocks insights, scheduling, monetization"},
        {"item": "Profile photo is high-res, clear, on-brand", "priority": "high", "impact": "brand recognition at small sizes"},
        {"item": "Bio: niche + value + CTA + link (150 chars max)", "priority": "critical", "impact": "converts profile visitors to followers"},
        {"item": "Link in bio: use Linktree, Stan.store, or own landing page", "priority": "high", "impact": "single hub for all monetization links"},
        {"item": "Highlights cover key content categories (branded covers)", "priority": "high", "impact": "+25% follow rate from profile visits"},
        {"item": "Post Reels 4-7x/week (Reels get 2× reach vs feed)", "priority": "critical", "impact": "primary growth driver on Instagram 2026"},
        {"item": "First frame of Reel is eye-catching still or text hook", "priority": "critical", "impact": "determines autoplay engagement"},
        {"item": "Add captions to all Reels (85% watched muted)", "priority": "high", "impact": "2× completion rate improvement"},
        {"item": "Use 8-12 hashtags (mix of broad + niche + location)", "priority": "high", "impact": "discovery via explore page"},
        {"item": "Post Stories every day (polls, questions, countdowns)", "priority": "high", "impact": "maintains engagement between Reels"},
        {"item": "Tag relevant accounts and locations", "priority": "medium", "impact": "appears on tagged location feeds"},
        {"item": "Collaborate feature (collab posts) with accounts in niche", "priority": "medium", "impact": "shared audience exposure"},
        {"item": "Post carousels for educational content (saves = ranking signal)", "priority": "high", "impact": "saves are the strongest engagement signal"},
        {"item": "Respond to DMs and comments within 4 hours", "priority": "high", "impact": "Instagram prioritizes active creators"},
        {"item": "Use Instagram Subscription for exclusive content monetization", "priority": "medium", "impact": "direct recurring revenue from followers"},
    ],
}

# Scoring weights for account health check
_SCORE_WEIGHTS = {
    "critical": 20,
    "high": 10,
    "medium": 5,
}


def optimize_account(platform: str) -> dict[str, Any]:
    """Return the full optimization checklist for a platform."""
    if platform not in _OPTIMIZATION_CHECKLISTS:
        raise ValueError(f"Unknown platform '{platform}'. Choose from: {', '.join(_OPTIMIZATION_CHECKLISTS.keys())}")
    checklist = _OPTIMIZATION_CHECKLISTS[platform]
    total_score = sum(_SCORE_WEIGHTS[item["priority"]] for item in checklist)
    return {
        "platform": platform,
        "total_possible_score": total_score,
        "item_count": len(checklist),
        "critical_items": [i for i in checklist if i["priority"] == "critical"],
        "high_items": [i for i in checklist if i["priority"] == "high"],
        "medium_items": [i for i in checklist if i["priority"] == "medium"],
        "checklist": checklist,
    }


def account_schedule(platform: str) -> dict[str, Any]:
    """Return optimal posting schedule for a platform."""
    if platform not in _POSTING_SCHEDULES:
        raise ValueError(f"Unknown platform '{platform}'. Choose from: {', '.join(_POSTING_SCHEDULES.keys())}")
    return _POSTING_SCHEDULES[platform]


def analyze_account(platform: str, niche: str, completed_items: list[str] = None) -> dict[str, Any]:
    """Score an account based on which optimization items are completed."""
    checklist = _OPTIMIZATION_CHECKLISTS.get(platform)
    if not checklist:
        raise ValueError(f"Unknown platform '{platform}'.")

    completed = set(completed_items or [])
    total_possible = sum(_SCORE_WEIGHTS[i["priority"]] for i in checklist)
    earned = sum(
        _SCORE_WEIGHTS[i["priority"]]
        for i in checklist
        if i["item"] in completed
    )
    score_pct = round((earned / total_possible) * 100) if total_possible else 0

    missing_critical = [i for i in checklist if i["priority"] == "critical" and i["item"] not in completed]
    next_actions = missing_critical[:3] or [i for i in checklist if i["item"] not in completed][:3]

    grade = "A" if score_pct >= 85 else "B" if score_pct >= 70 else "C" if score_pct >= 50 else "D"

    return {
        "platform": platform,
        "niche": niche,
        "score": earned,
        "max_score": total_possible,
        "score_pct": score_pct,
        "grade": grade,
        "items_completed": len(completed),
        "items_total": len(checklist),
        "next_actions": next_actions,
        "status": "optimized" if score_pct >= 85 else "needs_work" if score_pct >= 50 else "critical_gaps",
    }


def growth_roadmap(platform: str, current_followers: int) -> dict[str, Any]:
    """Return a growth roadmap based on current follower count."""
    stages = {
        "tiktok": [
            {"range": (0, 1000), "phase": "seed", "focus": "post 2x/day, niche down hard, study analytics"},
            {"range": (1000, 10000), "phase": "growth", "focus": "test formats weekly, double down on best-performer type"},
            {"range": (10000, 50000), "phase": "monetize", "focus": "Creator Fund + affiliate links + TikTok Shop"},
            {"range": (50000, 500000), "phase": "scale", "focus": "brand deals, digital products, theme page management"},
            {"range": (500000, 999999999), "phase": "authority", "focus": "multi-platform empire, agency/consulting, IP licensing"},
        ],
        "youtube": [
            {"range": (0, 1000), "phase": "seed", "focus": "1000 subs to unlock monetization — Shorts + 2x/week long-form"},
            {"range": (1000, 10000), "phase": "growth", "focus": "A/B test thumbnails, use analytics to double-down on top topics"},
            {"range": (10000, 100000), "phase": "monetize", "focus": "YPP ads + sponsors + channel memberships"},
            {"range": (100000, 1000000), "phase": "scale", "focus": "brand partnerships, own products, Shorts feed domination"},
            {"range": (1000000, 999999999), "phase": "authority", "focus": "multi-channel network, licensing, speaking, book deals"},
        ],
        "instagram": [
            {"range": (0, 1000), "phase": "seed", "focus": "daily Reels + Stories, engage with bigger accounts in niche"},
            {"range": (1000, 10000), "phase": "growth", "focus": "affiliate links in bio, collab with similar-sized accounts"},
            {"range": (10000, 50000), "phase": "monetize", "focus": "brand deals + IG Subscription + digital products"},
            {"range": (50000, 500000), "phase": "scale", "focus": "multi-page management, UGC brand partnerships"},
            {"range": (500000, 999999999), "phase": "authority", "focus": "own brand launch, licensing, international partnerships"},
        ],
    }

    platform_stages = stages.get(platform, [])
    current_stage = next(
        (s for s in platform_stages if s["range"][0] <= current_followers < s["range"][1]),
        platform_stages[-1] if platform_stages else {},
    )

    next_milestone = next(
        (s["range"][0] for s in platform_stages if s["range"][0] > current_followers),
        None,
    )

    return {
        "platform": platform,
        "current_followers": current_followers,
        "current_phase": current_stage.get("phase"),
        "current_focus": current_stage.get("focus"),
        "next_milestone": next_milestone,
        "followers_to_next": (next_milestone - current_followers) if next_milestone else 0,
        "all_stages": platform_stages,
    }


def list_platforms() -> list[str]:
    return list(_OPTIMIZATION_CHECKLISTS.keys())
