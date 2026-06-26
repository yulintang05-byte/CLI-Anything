"""Account optimization — posting schedules, profile audit, growth tactics."""

from typing import Any, Dict, List, Optional


# Optimal posting windows by platform (hour ranges in local time, 24h format)
_BEST_TIMES: Dict[str, List[Dict[str, Any]]] = {
    "tiktok": [
        {"day": "Monday",    "hours": [6, 10, 19, 22], "note": "Morning commute + evening scroll"},
        {"day": "Tuesday",   "hours": [9, 12, 19],     "note": "Lunch break + evening"},
        {"day": "Wednesday", "hours": [7, 11, 19, 21], "note": "Mid-week high engagement"},
        {"day": "Thursday",  "hours": [9, 12, 19],     "note": "Pre-weekend buzz"},
        {"day": "Friday",    "hours": [5, 13, 15, 23], "note": "Weekend excitement builds"},
        {"day": "Saturday",  "hours": [11, 19, 20],    "note": "Afternoon + evening peak"},
        {"day": "Sunday",    "hours": [7, 8, 16],      "note": "Sunday morning + afternoon wind-down"},
    ],
    "instagram": [
        {"day": "Monday",    "hours": [6, 11, 19], "note": "Morning + lunch"},
        {"day": "Tuesday",   "hours": [8, 14, 20], "note": "Strong engagement day"},
        {"day": "Wednesday", "hours": [9, 11, 20], "note": "Midweek peak"},
        {"day": "Thursday",  "hours": [11, 14, 19], "note": "Lunch + evening"},
        {"day": "Friday",    "hours": [10, 14, 17], "note": "Wind-down before weekend"},
        {"day": "Saturday",  "hours": [10, 21],    "note": "Late morning + night"},
        {"day": "Sunday",    "hours": [10, 16],    "note": "Relaxed browsing"},
    ],
    "youtube": [
        {"day": "Monday",    "hours": [14, 22], "note": "Evening viewing"},
        {"day": "Tuesday",   "hours": [14, 22], "note": "Consistent evening audience"},
        {"day": "Wednesday", "hours": [14, 22], "note": "Mid-week high retention"},
        {"day": "Thursday",  "hours": [12, 21], "note": "Lunch + evening"},
        {"day": "Friday",    "hours": [12, 21], "note": "Pre-weekend"},
        {"day": "Saturday",  "hours": [9, 11],  "note": "Morning viewing — highest watch time"},
        {"day": "Sunday",    "hours": [9, 11],  "note": "Sunday is #1 YouTube day"},
    ],
    "twitter": [
        {"day": "Monday",    "hours": [8, 12, 18], "note": "Morning news cycle"},
        {"day": "Tuesday",   "hours": [9, 13],     "note": "Highest Twitter engagement"},
        {"day": "Wednesday", "hours": [9, 12],     "note": "Midweek spike"},
        {"day": "Thursday",  "hours": [10, 13],    "note": "Trending conversations"},
        {"day": "Friday",    "hours": [10, 12],    "note": "Pre-weekend"},
        {"day": "Saturday",  "hours": [9],         "note": "Lower volume, less competition"},
        {"day": "Sunday",    "hours": [10],        "note": "Low volume"},
    ],
}

_PLATFORM_SPECS: Dict[str, Dict[str, Any]] = {
    "tiktok": {
        "ideal_video_length": "15–30s for viral, 60–90s for educational",
        "aspect_ratio": "9:16 (1080x1920)",
        "caption_limit": 2200,
        "bio_limit": 80,
        "link_in_bio": "1 link (TikTok bio)",
        "posting_frequency": "1–3 times/day for fast growth",
        "content_types": ["short clips", "POV", "tutorials", "trends", "storytimes", "duets"],
        "algorithm_signals": ["watch time %", "shares", "comments", "follows from video"],
        "hook_window_seconds": 3,
    },
    "instagram": {
        "ideal_video_length": "Reels: 7–15s. Feed: 3–60s",
        "aspect_ratio": "9:16 Reels, 1:1 Feed, 4:5 Portrait",
        "caption_limit": 2200,
        "bio_limit": 150,
        "link_in_bio": "1 link + Linktree or Stan Store",
        "posting_frequency": "3–5 Reels/week + 1 story/day",
        "content_types": ["Reels", "carousels", "stories", "UGC reposts", "behind-the-scenes"],
        "algorithm_signals": ["saves", "shares to stories", "sends", "watch time"],
        "hook_window_seconds": 2,
    },
    "youtube": {
        "ideal_video_length": "Shorts: 15–60s. Long-form: 8–15 min for ads",
        "aspect_ratio": "16:9 standard, 9:16 for Shorts",
        "caption_limit": 5000,
        "bio_limit": 1000,
        "link_in_bio": "Multiple (channel about tab + descriptions)",
        "posting_frequency": "2–3 videos/week (Shorts daily is ok)",
        "content_types": ["tutorials", "reviews", "vlogs", "shorts", "compilations", "challenges"],
        "algorithm_signals": ["CTR on thumbnail", "average view duration", "subscribers from video"],
        "hook_window_seconds": 30,
    },
}


def get_best_posting_times(platform: str, timezone: str = "UTC") -> Dict[str, Any]:
    """Return optimal posting windows for a given platform."""
    platform = platform.lower()
    if platform not in _BEST_TIMES:
        available = list(_BEST_TIMES.keys())
        raise ValueError(f"Unknown platform '{platform}'. Available: {available}")

    schedule = _BEST_TIMES[platform]
    # Flatten to a simple top-5 slots recommendation
    all_slots = []
    for day_info in schedule:
        for hour in day_info["hours"]:
            all_slots.append({
                "day": day_info["day"],
                "hour": hour,
                "time_display": f"{hour:02d}:00 {timezone}",
                "note": day_info["note"],
            })

    # Priority slots (highest engagement across studies)
    priority = [s for s in all_slots if s["hour"] in (7, 9, 11, 19, 21)]

    return {
        "platform": platform,
        "timezone_note": f"Times shown in {timezone}. Adjust to YOUR audience's timezone.",
        "full_schedule": schedule,
        "top_5_slots": priority[:5],
        "weekly_frequency_recommendation": _PLATFORM_SPECS.get(platform, {}).get("posting_frequency", ""),
    }


def audit_account(
    platform: str,
    handle: str,
    bio: Optional[str] = None,
    follower_count: int = 0,
    following_count: int = 0,
    post_count: int = 0,
    has_link: bool = False,
    has_profile_picture: bool = True,
    posting_frequency_per_week: float = 0,
    avg_views: int = 0,
    avg_likes: int = 0,
) -> Dict[str, Any]:
    """
    Audit an account's profile completeness and health.

    Returns a scored checklist with actionable recommendations.
    """
    platform = platform.lower()
    spec = _PLATFORM_SPECS.get(platform, {})
    issues: List[str] = []
    wins: List[str] = []
    score = 100

    # Profile completeness
    if not has_profile_picture:
        issues.append("Missing profile picture — accounts without PFP get 40% less profile visits")
        score -= 15
    else:
        wins.append("Profile picture set")

    if bio:
        bio_len = len(bio)
        bio_limit = spec.get("bio_limit", 150)
        if bio_len < 20:
            issues.append(f"Bio too short ({bio_len} chars). Add keywords + CTA. Limit: {bio_limit}")
            score -= 10
        elif bio_len > bio_limit:
            issues.append(f"Bio too long ({bio_len} chars, limit {bio_limit}). Shorten it.")
            score -= 5
        else:
            wins.append(f"Bio length good ({bio_len}/{bio_limit} chars)")
    else:
        issues.append("No bio provided for audit — add a keyword-rich bio with a CTA")
        score -= 10

    if not has_link and platform in ("instagram", "tiktok", "youtube"):
        issues.append("No link in bio — add a Linktree or Stan Store to capture leads")
        score -= 10
    elif has_link:
        wins.append("Link in bio present")

    # Follow ratio
    if following_count > 0 and follower_count > 0:
        ratio = follower_count / following_count
        if ratio < 0.5 and follower_count < 1000:
            issues.append(
                f"Follow ratio {ratio:.1f}:1 looks like a follow-for-follow account. "
                "Unfollow non-followers to improve credibility."
            )
            score -= 5
        elif ratio >= 1:
            wins.append(f"Healthy follow ratio: {ratio:.1f}:1")

    # Posting consistency
    if posting_frequency_per_week == 0:
        issues.append("Unknown posting frequency. Aim for at least 3 posts/week for algorithmic growth.")
        score -= 5
    elif posting_frequency_per_week < 1:
        issues.append(
            f"Posting only {posting_frequency_per_week:.1f}x/week — algorithms deprioritize inactive accounts. "
            f"Target: {spec.get('posting_frequency', '3–5 posts/week')}"
        )
        score -= 15
    elif posting_frequency_per_week >= 3:
        wins.append(f"Good posting frequency: {posting_frequency_per_week:.1f}x/week")

    # Engagement rate
    if follower_count > 0 and avg_likes > 0:
        engagement_rate = avg_likes / follower_count * 100
        if engagement_rate < 1.0:
            issues.append(
                f"Low engagement rate: {engagement_rate:.2f}%. "
                "Under 1% suggests your content isn't resonating. "
                "Try trending formats, CTAs in captions, and engaging with comments."
            )
            score -= 10
        elif engagement_rate >= 3.0:
            wins.append(f"Excellent engagement rate: {engagement_rate:.2f}%")
        else:
            wins.append(f"Average engagement rate: {engagement_rate:.2f}% (target 3%+)")

    score = max(0, score)
    grade = "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 55 else "D"

    return {
        "platform": platform,
        "handle": handle,
        "score": score,
        "grade": grade,
        "wins": wins,
        "issues": issues,
        "next_actions": issues[:3],
        "platform_specs": spec,
    }


def generate_growth_roadmap(
    platform: str,
    current_followers: int,
    target_followers: int,
    niche: str,
    days: int = 90,
) -> Dict[str, Any]:
    """
    Generate a 90-day growth roadmap for an account.
    """
    platform = platform.lower()
    needed = target_followers - current_followers
    if needed <= 0:
        return {"status": "already_at_target", "message": "Target already reached!"}

    daily_needed = needed / days
    spec = _PLATFORM_SPECS.get(platform, {})

    phases = [
        {
            "phase": 1,
            "days": "1–30",
            "focus": "Foundation",
            "goals": [
                "Optimize profile (PFP, bio, link in bio)",
                "Define your content pillar (the 1 thing you're known for)",
                "Post 1x/day to find your best-performing format",
                "Engage with 20 accounts in your niche daily (like, comment meaningfully)",
                f"Use 5–7 trending hashtags per post in #{niche} niche",
            ],
            "expected_growth": f"+{int(daily_needed * 0.5 * 30)} followers",
        },
        {
            "phase": 2,
            "days": "31–60",
            "focus": "Acceleration",
            "goals": [
                "Double down on your top 3 content formats from Phase 1",
                "Start collaborating with 2–3 accounts in your niche (duets, collabs)",
                "Add trending sounds/music to every post",
                "Batch-create content (film 5 videos in one session)",
                "Reply to ALL comments in first hour after posting",
            ],
            "expected_growth": f"+{int(daily_needed * 1.0 * 30)} followers",
        },
        {
            "phase": 3,
            "days": "61–90",
            "focus": "Monetization-Ready Scale",
            "goals": [
                "Launch a lead magnet or freebie to build email list",
                "Post 2x/day (repurpose long content as Shorts/Reels)",
                "Start a series (multi-part content drives follows for the next episode)",
                "Cross-post across platforms to compound reach",
                "Test paid promotion on your 2–3 highest-performing posts",
            ],
            "expected_growth": f"+{int(daily_needed * 1.5 * 30)} followers",
        },
    ]

    return {
        "platform": platform,
        "niche": niche,
        "current_followers": current_followers,
        "target_followers": target_followers,
        "gap": needed,
        "timeline_days": days,
        "daily_growth_needed": round(daily_needed),
        "roadmap": phases,
        "content_types": spec.get("content_types", []),
        "key_metric_to_watch": spec.get("algorithm_signals", [])[0] if spec.get("algorithm_signals") else "engagement rate",
        "hook_window": f"You have {spec.get('hook_window_seconds', 3)} seconds to hook viewers. Open STRONG.",
    }


def cross_platform_strategy(
    platforms: List[str],
    niche: str,
    primary_platform: str = "tiktok",
) -> Dict[str, Any]:
    """
    Generate a cross-platform content repurposing strategy.
    """
    primary = primary_platform.lower()
    secondary = [p.lower() for p in platforms if p.lower() != primary]

    repurpose_map = {
        ("tiktok", "instagram"): "Download TikTok (no watermark via SnapTik), post as Reel",
        ("tiktok", "youtube"): "Compile 5–10 TikToks weekly into a YouTube Shorts playlist or a 'best of' long-form",
        ("tiktok", "twitter"): "Screenshot stats from viral TikToks and post the insight as a Twitter thread",
        ("instagram", "tiktok"): "Export Reels, post to TikTok with trending sound overlaid",
        ("youtube", "tiktok"): "Cut best moments into 15–30s clips for TikTok using the Clipper tool",
        ("youtube", "instagram"): "Export Shorts as Reels; pull quote cards from long-form for carousels",
    }

    repurpose_plan = []
    for sec in secondary:
        key = (primary, sec)
        rev_key = (sec, primary)
        tip = repurpose_map.get(key) or repurpose_map.get(rev_key) or f"Download content from {primary} and repost on {sec}"
        repurpose_plan.append({
            "from": primary,
            "to": sec,
            "method": tip,
            "extra_work_minutes": 5,
        })

    return {
        "primary_platform": primary,
        "secondary_platforms": secondary,
        "niche": niche,
        "strategy": "Create once on your primary platform, distribute everywhere.",
        "repurpose_plan": repurpose_plan,
        "tools": ["Clipper (this toolkit)", "SnapTik (remove TikTok watermark)", "Canva (add captions/branding)"],
        "posting_order": f"Post on {primary} first. Wait 24–48h for algorithm to push it, then cross-post.",
        "weekly_schedule": {
            "Monday": f"Film batch (3-5 videos for {primary})",
            "Tuesday": f"Post Day 1 on {primary}, repurpose to {secondary[0] if secondary else 'Instagram'}",
            "Wednesday": f"Post Day 2 on {primary}, analyze Day 1 performance",
            "Thursday": f"Post Day 3 + cross-post best performer",
            "Friday": f"Engage with community, plan next week's trend hooks",
            "Saturday": "Optional extra post for weekend audience",
            "Sunday": "Content planning + trend research session",
        },
    }
