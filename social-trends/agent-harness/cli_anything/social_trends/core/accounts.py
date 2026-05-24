"""Account optimization — posting schedules, profile audits, growth strategies.

Platform-specific best practices derived from public creator research.
No account credentials required — returns actionable strategy data.
"""

from __future__ import annotations
from typing import Literal

Platform = Literal["tiktok", "youtube", "instagram", "twitter", "all"]


# Best posting times by platform and timezone bucket (UTC offset → local hours)
POSTING_WINDOWS: dict[str, dict[str, list[dict]]] = {
    "tiktok": {
        "weekday": [
            {"time": "06:00-09:00", "reason": "Morning commute scroll"},
            {"time": "12:00-15:00", "reason": "Lunch break peak"},
            {"time": "19:00-23:00", "reason": "Evening prime time (highest engagement)"},
        ],
        "weekend": [
            {"time": "09:00-11:00", "reason": "Late morning casual scroll"},
            {"time": "14:00-17:00", "reason": "Afternoon peak"},
            {"time": "19:00-22:00", "reason": "Weekend evening — slightly lower than weekday"},
        ],
        "best_days": ["Tuesday", "Thursday", "Friday"],
        "avoid_days": ["Monday morning", "Sunday late night"],
    },
    "youtube": {
        "weekday": [
            {"time": "14:00-16:00", "reason": "After school / afternoon lull"},
            {"time": "20:00-23:00", "reason": "Evening prime watch time"},
        ],
        "weekend": [
            {"time": "09:00-11:00", "reason": "Saturday/Sunday morning binge"},
            {"time": "15:00-18:00", "reason": "Peak weekend afternoon"},
        ],
        "best_days": ["Thursday", "Friday", "Saturday"],
        "avoid_days": ["Monday", "Tuesday morning"],
    },
    "instagram": {
        "weekday": [
            {"time": "07:00-09:00", "reason": "Morning feed check"},
            {"time": "11:00-13:00", "reason": "Pre-lunch scroll"},
            {"time": "17:00-19:00", "reason": "Post-work wind-down"},
        ],
        "weekend": [
            {"time": "10:00-13:00", "reason": "Brunch scroll"},
            {"time": "17:00-20:00", "reason": "Evening engagement peak"},
        ],
        "best_days": ["Wednesday", "Friday", "Sunday"],
        "avoid_days": ["Monday 08:00-10:00"],
    },
}

POSTING_FREQUENCY: dict[str, dict] = {
    "tiktok": {
        "minimum": "1x/day",
        "optimal": "3-5x/day",
        "maximum": "7x/day",
        "note": "TikTok rewards quantity. More posts = more chances to go viral.",
    },
    "youtube": {
        "shorts": {"minimum": "1x/day", "optimal": "2-3x/day"},
        "long_form": {"minimum": "1x/week", "optimal": "2-3x/week"},
        "note": "Consistency matters more than frequency for YouTube.",
    },
    "instagram": {
        "reels": {"minimum": "3x/week", "optimal": "1x/day"},
        "feed": {"minimum": "3x/week", "optimal": "5x/week"},
        "stories": {"minimum": "3x/day", "optimal": "7-10x/day"},
        "note": "Stories keep you top-of-mind; Reels drive new followers.",
    },
}

PROFILE_CHECKLIST: dict[str, list[dict]] = {
    "tiktok": [
        {"item": "Username", "tip": "Short, memorable, niche-relevant. Use same name across platforms."},
        {"item": "Profile photo", "tip": "High-res face photo (1:1) OR niche-specific brand logo. No blurry pics."},
        {"item": "Bio", "tip": "80 chars max. State your niche + value prop. Add 1 CTA (link/DM/follow)."},
        {"item": "Link in bio", "tip": "Use Linktree or Stan Store to consolidate all links."},
        {"item": "Pinned videos", "tip": "Pin your 3 best-performing or most representative videos."},
        {"item": "Content pillars", "tip": "Stick to 3-5 content themes. Algorithm rewards consistency."},
        {"item": "Posting consistency", "tip": "Post same time every day for 30 days to train algorithm."},
        {"item": "Reply to comments", "tip": "Reply within 1h of posting — boosts comment velocity signal."},
        {"item": "Duet/Stitch enables", "tip": "Enable both — they generate free distribution."},
        {"item": "TikTok LIVE", "tip": "Go live 2-3x/week once you have 1K followers. Massive reach boost."},
    ],
    "youtube": [
        {"item": "Channel name", "tip": "Searchable + brand-able. Include niche keyword if possible."},
        {"item": "Channel art", "tip": "2560x1440px banner. Include niche, upload schedule, social handles."},
        {"item": "Channel description", "tip": "First 100 chars show in search. Include keywords naturally."},
        {"item": "Channel trailer", "tip": "60-90s hook trailer for non-subscribers. Explain who you are + value."},
        {"item": "Playlists", "tip": "Organise videos into playlists to increase session watch time."},
        {"item": "End screens", "tip": "Add Subscribe + Video elements to every video (last 20 seconds)."},
        {"item": "Cards", "tip": "Add cards at 20-40% and 80% timestamps."},
        {"item": "Chapters", "tip": "Add timestamps/chapters to all videos 8+ minutes long."},
        {"item": "Thumbnails", "tip": "Consistent style (same font, colour palette, face expression)."},
        {"item": "Community tab", "tip": "Post 3-5x/week once unlocked (500 subs). Keeps audience warm."},
    ],
    "instagram": [
        {"item": "Username", "tip": "Match TikTok/YouTube handle exactly for cross-platform SEO."},
        {"item": "Profile photo", "tip": "Same as TikTok for brand recognition."},
        {"item": "Bio", "tip": "150 chars. Niche keyword in name field (shows in search). 1 emoji per line max."},
        {"item": "Highlights", "tip": "Create 5-8 highlights with custom covers. Include: About, FAQs, Content, Shop."},
        {"item": "Link in bio", "tip": "One link (Linktree/Stan Store) — same as TikTok for consistency."},
        {"item": "Content grid", "tip": "Plan a cohesive grid aesthetic (alternating, puzzle, checkerboard)."},
        {"item": "Reels hook", "tip": "First 1-3 seconds must hook. Show end result or ask a question."},
        {"item": "Hashtags", "tip": "3-5 hashtags in caption (not comments). Mix of sizes."},
    ],
}

GROWTH_STRATEGIES: dict[str, list[str]] = {
    "tiktok": [
        "Hook in first 0.5 seconds — show the RESULT or make a bold claim",
        "Loop your video — last frame connects back to first (increases rewatch rate)",
        "Reply to comments WITH VIDEO — generates new distribution",
        "Use trending sounds within 24-48h of them going viral",
        "Collab with creators in your niche (even small accounts)",
        "Post 3+ videos/day for 30 days during initial growth phase",
        "Use the 'Stitch' feature to react to trending content in your niche",
        "Create series content (Part 1/5) to encourage profile visits",
        "Engage with top comments on trending videos in your niche",
        "TikTok rewards 'completion rate' — keep videos under 30s initially",
    ],
    "youtube": [
        "Thumbnail A/B test — only change 1 element at a time",
        "Title: front-load keywords in first 40 characters",
        "First 30 seconds must deliver on the thumbnail/title promise",
        "Ask a compelling question in your description to boost comments",
        "Upload Shorts version of every Long-Form video",
        "Reply to every comment in the first 48h",
        "Research 'mid-tail' keywords with TubeBuddy or VidIQ",
        "Create 'reaction' or 'response' videos to viral content in niche",
        "Cross-promote in YouTube Community tab when posting",
        "Re-upload evergreen content with updated thumbnail every 6 months",
    ],
    "instagram": [
        "Post Reels within 24h of a trend going viral on TikTok",
        "Use Collab feature to co-post Reels with similar-size accounts",
        "Stories poll/question sticker daily to boost algorithm signal",
        "Share Reels to Stories immediately after posting",
        "DM new followers a personalised welcome message",
        "Engage 30 min BEFORE posting (comment on 10 posts in niche)",
        "Broadcast Channel: build direct audience before every post",
        "Carousel posts get 3x more reach than single images",
        "Include keyword in caption first line (Instagram text search)",
        "Go Live with another creator — cross-promotes to both audiences",
    ],
}


def optimize_profile(platform: Platform, niche: str = "") -> dict:
    """Return a full profile optimisation checklist for a platform.

    Args:
        platform: Target social platform.
        niche: Optional content niche for tailored tips.

    Returns:
        Dict with checklist items and growth strategies.
    """
    if platform == "all":
        return {
            "platforms": {
                p: optimize_profile(p, niche)  # type: ignore[arg-type]
                for p in ("tiktok", "youtube", "instagram")
            }
        }

    checklist = PROFILE_CHECKLIST.get(platform, [])
    strategies = GROWTH_STRATEGIES.get(platform, [])
    freq = POSTING_FREQUENCY.get(platform, {})

    return {
        "platform": platform,
        "niche": niche or "general",
        "profile_checklist": checklist,
        "growth_strategies": strategies,
        "posting_frequency": freq,
        "priority_actions": checklist[:3],
    }


def get_posting_schedule(platform: Platform, timezone: str = "US/Eastern") -> dict:
    """Return optimal posting schedule for a platform.

    Args:
        platform: Target platform.
        timezone: Timezone string (e.g. "US/Eastern", "Europe/London").

    Returns:
        Dict with day-by-day posting times and rationale.
    """
    if platform == "all":
        return {
            "platforms": {
                p: get_posting_schedule(p, timezone)  # type: ignore[arg-type]
                for p in ("tiktok", "youtube", "instagram")
            }
        }

    windows = POSTING_WINDOWS.get(platform, {})
    freq = POSTING_FREQUENCY.get(platform, {})

    return {
        "platform": platform,
        "timezone": timezone,
        "weekday_windows": windows.get("weekday", []),
        "weekend_windows": windows.get("weekend", []),
        "best_days": windows.get("best_days", []),
        "avoid_times": windows.get("avoid_days", []),
        "posting_frequency": freq,
        "weekly_template": _build_weekly_template(platform),
        "note": (
            "These times are in your LOCAL timezone. Adjust by checking "
            "your analytics for audience peak hours once you have 50+ posts."
        ),
    }


def audit_account(platform: Platform, niche: str = "", follower_count: int = 0) -> dict:
    """Run a strategic account audit and return prioritised action items.

    Args:
        platform: Social platform.
        niche: Content niche.
        follower_count: Current follower count (used to tailor advice).

    Returns:
        Dict with audit findings and prioritised next steps.
    """
    checklist = PROFILE_CHECKLIST.get(platform, [])

    if follower_count < 1000:
        growth_phase = "foundation"
        priority = [
            "Post 1-5x daily for 30 straight days without missing",
            "Hook in first 0.5-1 second of every video",
            "Use 3-5 trending hashtags per post",
            "Reply to every single comment within 1 hour",
            "Study your top 3 competitors — reverse-engineer their hooks",
        ]
    elif follower_count < 10_000:
        growth_phase = "growth"
        priority = [
            "Identify your 3 highest-performing content formats and double down",
            "Start collaborating with creators at 2-5x your following",
            "Test paid promotion on your best organic post ($5-20/day)",
            "Launch a recurring series to build loyal return audience",
            "Begin collecting emails via lead magnet offer",
        ]
    elif follower_count < 100_000:
        growth_phase = "scaling"
        priority = [
            "Hire a video editor — remove production bottleneck",
            "Create a content team or hire a social media manager",
            "Launch brand partnerships / UGC creator deals",
            "Build a second monetisation pillar (course, merch, service)",
            "Cross-post to every platform simultaneously",
        ]
    else:
        growth_phase = "monetisation"
        priority = [
            "Diversify revenue: brand deals + digital products + affiliate",
            "Launch a community (Discord, Patreon, Circle)",
            "Build an email list for algorithm-proof audience ownership",
            "License your content to media companies",
            "Launch a sub-brand targeting a micro-niche within your audience",
        ]

    return {
        "platform": platform,
        "niche": niche,
        "follower_count": follower_count,
        "growth_phase": growth_phase,
        "profile_checklist": checklist,
        "priority_actions": priority,
        "monetisation_threshold": _monetisation_threshold(platform),
    }


def _monetisation_threshold(platform: str) -> dict:
    thresholds = {
        "tiktok": {
            "creator_fund": "10K followers + 100K views in 30 days",
            "tiktok_shop": "1K followers",
            "live_gifts": "1K followers",
            "brand_deals": "5K-10K followers (micro-influencer)",
        },
        "youtube": {
            "adsense": "1,000 subscribers + 4,000 watch hours OR 10M Shorts views",
            "super_thanks": "Same as AdSense",
            "channel_memberships": "500 subscribers",
            "brand_deals": "1K subscribers (micro)",
        },
        "instagram": {
            "creator_badge": "Available in select countries, no follower minimum",
            "subscriptions": "10K followers",
            "brand_deals": "1K-5K followers (nano-influencer)",
            "affiliate": "Any size — use LTK or Amazon Associates",
        },
    }
    return thresholds.get(platform, {})


def _build_weekly_template(platform: str) -> list[dict]:
    templates = {
        "tiktok": [
            {"day": "Monday", "posts": 2, "type": "Educational + Trend"},
            {"day": "Tuesday", "posts": 3, "type": "How-to + Trend + Behind-scenes"},
            {"day": "Wednesday", "posts": 2, "type": "POV/Story + Tutorial"},
            {"day": "Thursday", "posts": 3, "type": "Trend + Q&A reply + Value"},
            {"day": "Friday", "posts": 3, "type": "Viral hook + Funny + Motivational"},
            {"day": "Saturday", "posts": 2, "type": "Lifestyle + Collab/Duet"},
            {"day": "Sunday", "posts": 1, "type": "Week recap / Teaser for Monday"},
        ],
        "youtube": [
            {"day": "Monday", "posts": 0, "type": "Editing day"},
            {"day": "Tuesday", "posts": 1, "type": "Shorts only"},
            {"day": "Wednesday", "posts": 0, "type": "Filming day"},
            {"day": "Thursday", "posts": 1, "type": "Long-form upload + Community post"},
            {"day": "Friday", "posts": 1, "type": "Shorts — repurpose long-form clip"},
            {"day": "Saturday", "posts": 1, "type": "Bonus Shorts or Premiere"},
            {"day": "Sunday", "posts": 0, "type": "Planning + analytics review"},
        ],
        "instagram": [
            {"day": "Monday", "posts": 1, "type": "Motivational Reel"},
            {"day": "Tuesday", "posts": 1, "type": "Educational Carousel"},
            {"day": "Wednesday", "posts": 1, "type": "Behind-the-scenes Reel"},
            {"day": "Thursday", "posts": 1, "type": "Product/Service showcase"},
            {"day": "Friday", "posts": 1, "type": "Trend Reel + Community engage"},
            {"day": "Saturday", "posts": 1, "type": "Lifestyle/Personal story"},
            {"day": "Sunday", "posts": 0, "type": "Stories only + plan next week"},
        ],
    }
    return templates.get(platform, [])
