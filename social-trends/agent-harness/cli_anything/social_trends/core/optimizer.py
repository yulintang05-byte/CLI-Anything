"""Account optimization engine — posting schedule, bio, content strategy, and SEO."""

from __future__ import annotations
from datetime import datetime, timezone


PLATFORM_BEST_TIMES = {
    "tiktok": {
        "monday":    ["06:00", "10:00", "22:00"],
        "tuesday":   ["09:00", "12:00", "19:00"],
        "wednesday": ["07:00", "08:00", "23:00"],
        "thursday":  ["09:00", "12:00", "19:00"],
        "friday":    ["05:00", "13:00", "15:00"],
        "saturday":  ["11:00", "19:00", "20:00"],
        "sunday":    ["07:00", "08:00", "16:00"],
        "timezone":  "EST",
        "source":    "Influencer Marketing Hub 2024 analysis",
    },
    "youtube": {
        "monday":    ["14:00", "17:00"],
        "tuesday":   ["14:00", "17:00"],
        "wednesday": ["14:00", "17:00"],
        "thursday":  ["14:00", "17:00"],
        "friday":    ["14:00", "17:00"],
        "saturday":  ["09:00", "11:00"],
        "sunday":    ["09:00", "11:00"],
        "timezone":  "EST",
        "source":    "Hootsuite 2024 analysis",
    },
    "instagram": {
        "monday":    ["08:00", "17:00"],
        "tuesday":   ["08:00", "14:00"],
        "wednesday": ["11:00"],
        "thursday":  ["08:00", "14:00"],
        "friday":    ["08:00", "12:00"],
        "saturday":  ["09:00"],
        "sunday":    ["08:00"],
        "timezone":  "EST",
        "source":    "Sprout Social 2024 analysis",
    },
    "twitter": {
        "monday":    ["09:00", "12:00"],
        "tuesday":   ["09:00", "12:00"],
        "wednesday": ["09:00", "12:00"],
        "thursday":  ["09:00", "12:00"],
        "friday":    ["09:00", "12:00"],
        "saturday":  ["09:00"],
        "sunday":    ["09:00"],
        "timezone":  "EST",
        "source":    "Buffer 2024 analysis",
    },
}

POSTING_FREQUENCY = {
    "tiktok":    {"min": 1, "max": 4, "unit": "per day",   "note": "Consistency beats virality — post daily"},
    "youtube":   {"min": 1, "max": 3, "unit": "per week",  "note": "Quality > quantity; 2/week is sweet spot"},
    "instagram": {"min": 3, "max": 7, "unit": "per week",  "note": "Reels 3-5/week + Stories daily"},
    "twitter":   {"min": 3, "max": 10, "unit": "per day",  "note": "News/commentary gets best engagement"},
}

PROFILE_OPTIMIZATION = {
    "tiktok": {
        "bio_length": "80 chars max",
        "bio_tips": [
            "State your value proposition in first 1-2 words",
            "Include 1-2 emojis to catch the eye",
            "Add a CTA (link in bio, follow for X)",
            "Use a niche keyword for discoverability",
        ],
        "username_tips": [
            "Short, memorable, easy to spell",
            "Avoid numbers/underscores if possible",
            "Match your niche or name",
        ],
        "profile_pic": "High-contrast face photo or bold logo — no busy backgrounds",
        "link_tip": "Use Linktree or Stan.store to consolidate links",
    },
    "youtube": {
        "bio_length": "1000 chars (first 200 shown above fold)",
        "bio_tips": [
            "Include keywords in first 200 chars for search",
            "Explain what your channel offers + upload schedule",
            "Add social media links",
            "Include a keyword-rich channel description",
        ],
        "username_tips": ["Use your brand/niche name", "Consistent with other platforms"],
        "profile_pic": "Professional headshot or brand logo 800x800px minimum",
        "banner": "2560x1440px — show upload schedule + brand personality",
        "link_tip": "Feature up to 5 links in channel header",
    },
    "instagram": {
        "bio_length": "150 chars",
        "bio_tips": [
            "Line 1: Who you are / what you do",
            "Line 2: What value you provide",
            "Line 3: CTA with link reference",
            "Use keywords naturally for search",
        ],
        "username_tips": ["Searchable + brandable", "Consider adding niche keyword"],
        "profile_pic": "High-quality face or logo — circular crop, stand out",
        "link_tip": "Use link-in-bio tool; update it with every major post",
    },
}

CONTENT_HOOKS = [
    "I went from [BEFORE] to [AFTER] in [TIME] — here's how",
    "Stop doing [WRONG THING]. Do this instead:",
    "Nobody talks about this, but [INSIGHT]...",
    "Watch till the end — this changed everything for me",
    "POV: You just discovered [TOPIC]",
    "Things I wish I knew before [THING]",
    "The [THING] nobody tells you about [NICHE]",
    "[NUMBER] signs you're [RELATABLE SITUATION]",
    "Day [NUMBER] of [CHALLENGE] — [RESULT]",
    "This [TOOL/HACK] saved me [TIME/MONEY]",
]


def get_posting_schedule(
    platforms: list[str] | None = None,
    timezone_offset: int = -5,
) -> dict:
    """
    Return optimal posting schedule for specified platforms.

    Args:
        platforms: list of platforms (tiktok, youtube, instagram, twitter)
        timezone_offset: UTC offset for your timezone

    Returns:
        dict with per-platform schedules and weekly plan
    """
    if not platforms:
        platforms = ["tiktok", "youtube", "instagram"]

    schedule = {}
    for platform in platforms:
        p = platform.lower()
        if p in PLATFORM_BEST_TIMES:
            times = PLATFORM_BEST_TIMES[p].copy()
            freq = POSTING_FREQUENCY.get(p, {})
            schedule[p] = {
                "best_times": {day: t for day, t in times.items() if day not in ("timezone", "source")},
                "timezone": times.get("timezone", "EST"),
                "source": times.get("source", ""),
                "frequency": freq,
            }

    weekly_plan = _build_weekly_plan(platforms)

    return {
        "platforms": schedule,
        "weekly_plan": weekly_plan,
        "general_tips": [
            "Post at peak times consistently for 2-4 weeks before adjusting",
            "Check your platform analytics to see WHEN your specific audience is online",
            "Schedule posts in batches — batch-create content for a week",
            "First 30-60 min after posting: engage with comments to boost algorithm",
        ],
    }


def _build_weekly_plan(platforms: list[str]) -> list[dict]:
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    plan = []
    for day in days:
        day_lower = day.lower()
        actions = []
        for p in platforms:
            times = PLATFORM_BEST_TIMES.get(p.lower(), {})
            day_times = times.get(day_lower, [])
            if day_times:
                actions.append({"platform": p, "times": day_times})
        plan.append({"day": day, "actions": actions})
    return plan


def optimize_account(
    platform: str,
    niche: str = "",
    current_followers: int = 0,
    goals: list[str] | None = None,
) -> dict:
    """
    Generate an account optimization plan.

    Args:
        platform: social platform name
        niche: content niche
        current_followers: current follower count
        goals: list of goals (growth, monetization, brand_deals, traffic)

    Returns:
        dict with optimization recommendations
    """
    if not goals:
        goals = ["growth"]

    profile_tips = PROFILE_OPTIMIZATION.get(platform.lower(), {})
    growth_stage = _determine_growth_stage(current_followers)
    recommendations = _build_recommendations(platform, niche, growth_stage, goals)

    return {
        "platform": platform,
        "niche": niche,
        "follower_count": current_followers,
        "growth_stage": growth_stage,
        "profile_optimization": profile_tips,
        "content_recommendations": recommendations["content"],
        "growth_tactics": recommendations["growth"],
        "monetization_path": recommendations.get("monetization", []),
        "kpis_to_track": _kpis_for_platform(platform),
        "content_hooks": CONTENT_HOOKS[:5],
    }


def _determine_growth_stage(followers: int) -> dict:
    if followers < 1_000:
        return {"stage": "nano", "label": "Nano (0–1K)", "priority": "Consistency + niche authority"}
    elif followers < 10_000:
        return {"stage": "micro", "label": "Micro (1K–10K)", "priority": "Engagement rate + collabs"}
    elif followers < 100_000:
        return {"stage": "mid", "label": "Mid-tier (10K–100K)", "priority": "Brand deals + diversification"}
    elif followers < 1_000_000:
        return {"stage": "macro", "label": "Macro (100K–1M)", "priority": "Monetization + team building"}
    else:
        return {"stage": "mega", "label": "Mega (1M+)", "priority": "Brand + passive income"}


def _build_recommendations(platform: str, niche: str, stage: dict, goals: list[str]) -> dict:
    content = [
        f"Post {POSTING_FREQUENCY.get(platform.lower(), {}).get('min', 1)}-{POSTING_FREQUENCY.get(platform.lower(), {}).get('max', 3)} times {POSTING_FREQUENCY.get(platform.lower(), {}).get('unit', 'per week')}",
        "Use trending audio/music relevant to your niche",
        "Hook viewers in the first 1-3 seconds",
        "Add captions/text overlays for silent viewing",
        "End with a clear CTA (follow, comment, share)",
        "Respond to all comments within first hour of posting",
        "Create content series/repeatable formats for consistency",
        "Study top 10 viral posts in your niche — reverse-engineer them",
    ]

    growth = [
        "Duet/stitch trending content in your niche (TikTok/Instagram)",
        "Collaborate with 3-5 creators in adjacent niches monthly",
        "Cross-promote across all your platforms",
        "Comment value-adding replies on top creators' posts daily",
        "Go Live 2x/week to boost algorithm reach",
        "Use trending sounds within 24-48 hours of them going viral",
        "Pin your best-performing content to your profile",
        "Run a challenge or contest to incentivize shares",
    ]

    if stage["stage"] in ("nano", "micro"):
        growth.insert(0, "Engage genuinely in 5-10 niche communities daily")
        growth.insert(1, "Post consistently for 90 days before pivoting strategy")

    monetization = []
    if "monetization" in goals:
        monetization = [
            "10K followers: Brand ambassador deals ($50-500/post)",
            "50K followers: Sponsored posts ($500-5K/post range)",
            "100K followers: Apply for TikTok Creator Fund / YouTube Partner Program",
            "Offer a digital product or Patreon from day 1",
            "Affiliate marketing — promote products you actually use",
            "LTK, Amazon Associates, ClickBank for product links",
        ]

    return {"content": content, "growth": growth, "monetization": monetization}


def _kpis_for_platform(platform: str) -> list[dict]:
    kpis = {
        "tiktok": [
            {"metric": "Video completion rate", "target": ">50%", "why": "Primary algorithm signal"},
            {"metric": "Like-to-view ratio", "target": ">5%", "why": "Measures content resonance"},
            {"metric": "Share rate", "target": ">2%", "why": "Boosts viral distribution"},
            {"metric": "Comment rate", "target": ">1%", "why": "Engagement depth"},
            {"metric": "Follower growth rate", "target": ">5%/month", "why": "Channel health"},
        ],
        "youtube": [
            {"metric": "Click-through rate (CTR)", "target": "4-10%", "why": "Thumbnail+title effectiveness"},
            {"metric": "Average view duration", "target": ">50%", "why": "Primary ranking signal"},
            {"metric": "Impressions to views", "target": ">5%", "why": "Search discoverability"},
            {"metric": "Subscriber conversion rate", "target": ">2%", "why": "Audience building"},
            {"metric": "Revenue per mille (RPM)", "target": "$2-15", "why": "Monetization health"},
        ],
        "instagram": [
            {"metric": "Reach rate", "target": ">10% of followers", "why": "Content distribution"},
            {"metric": "Saves per post", "target": ">1% of reach", "why": "High-value engagement signal"},
            {"metric": "Story completion rate", "target": ">70%", "why": "Story content quality"},
            {"metric": "Reel plays", "target": "Growing week-over-week", "why": "Reach expansion"},
        ],
    }
    return kpis.get(platform.lower(), [])


def generate_bio(
    platform: str,
    name: str,
    niche: str,
    value_prop: str,
    cta: str = "follow",
) -> dict:
    """
    Generate an optimized profile bio.

    Args:
        platform: tiktok, youtube, instagram
        name: your name or brand name
        niche: content niche
        value_prop: what unique value you provide
        cta: call to action (follow, subscribe, link in bio)

    Returns:
        dict with bio options and character counts
    """
    limits = {"tiktok": 80, "youtube": 200, "instagram": 150}
    limit = limits.get(platform.lower(), 150)

    emojis = _niche_emoji(niche)

    options = [
        f"{emojis[0]} {niche.title()} tips that actually work\n{value_prop}\n{_cta_text(cta)}",
        f"{name} | {niche.title()} {emojis[0]}\n{value_prop}\n{_cta_text(cta)}",
        f"Helping you {value_prop.lower()}\n{emojis[0]} {niche.title()} content daily\n{_cta_text(cta)}",
    ]

    return {
        "platform": platform,
        "character_limit": limit,
        "bio_options": [
            {"text": opt, "length": len(opt), "fits": len(opt) <= limit}
            for opt in options
        ],
        "tips": PROFILE_OPTIMIZATION.get(platform.lower(), {}).get("bio_tips", []),
    }


def _niche_emoji(niche: str) -> list[str]:
    mapping = {
        "fitness": ["💪", "🏋️", "🔥"],
        "food": ["🍳", "🥗", "👨‍🍳"],
        "finance": ["💰", "📈", "🏦"],
        "fashion": ["👗", "✨", "💅"],
        "beauty": ["💄", "✨", "🌸"],
        "travel": ["✈️", "🌍", "🗺️"],
        "gaming": ["🎮", "🕹️", "⚡"],
        "tech": ["💻", "🤖", "⚡"],
        "motivation": ["🔥", "💪", "🚀"],
        "comedy": ["😂", "🎭", "✨"],
        "lifestyle": ["✨", "🌟", "💫"],
        "music": ["🎵", "🎤", "🎹"],
        "business": ["💼", "📊", "🚀"],
    }
    return mapping.get(niche.lower(), ["✨", "🔥", "💡"])


def _cta_text(cta: str) -> str:
    ctas = {
        "follow": "👇 Follow for daily tips",
        "subscribe": "🔔 Subscribe for new content",
        "link": "🔗 Free guide → link in bio",
        "dm": "📩 DM me 'START' to begin",
        "shop": "🛍️ Shop the look → link in bio",
    }
    return ctas.get(cta.lower(), f"👇 {cta}")
