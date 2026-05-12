"""Account optimization engine.

Generates actionable optimization reports for TikTok, Instagram,
and YouTube theme pages based on current trend data.
"""

from __future__ import annotations

import time
from typing import Any

from .trends import (
    generate_hashtag_sets,
    _suggest_content_angles,
    _optimal_posting_times,
)


# ── Optimization report generator ─────────────────────────────────────

def generate_optimization_report(
    accounts: list[dict[str, Any]],
    hashtags: list[dict[str, Any]],
    sounds: list[dict[str, Any]],
    trends: list[dict[str, Any]],
    niche: str = "",
    region: str = "US",
) -> dict[str, Any]:
    """Build a full optimization report for all accounts.

    Returns a report dict with per-account recommendations and
    a global strategy section.
    """
    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "region": region,
        "niche": niche or "general",
        "global_strategy": _build_global_strategy(hashtags, sounds, trends, niche),
        "accounts": [],
        "content_calendar": build_content_calendar(trends, hashtags, niche, days=7),
        "growth_tactics": _growth_tactics(niche),
    }

    for account in accounts:
        platform = account.get("platform", "tiktok").lower()
        handle = account.get("handle", "")
        acct_niche = account.get("niche", niche)
        report["accounts"].append(
            _optimize_account(platform, handle, acct_niche, hashtags, sounds, trends)
        )

    return report


def _build_global_strategy(
    hashtags: list[dict[str, Any]],
    sounds: list[dict[str, Any]],
    trends: list[dict[str, Any]],
    niche: str,
) -> dict[str, Any]:
    tag_sets = generate_hashtag_sets(hashtags, niche=niche)
    top_sounds = sounds[:5]
    top_trends = trends[:5]

    return {
        "hashtag_sets": tag_sets,
        "top_trending_sounds": [
            {"id": s.get("music_id", ""), "title": s.get("title", ""), "score": s.get("score", 0)}
            for s in top_sounds
        ],
        "top_trends": [
            {"title": t.get("title", ""), "platform": t.get("platform", ""), "score": t.get("score", 0)}
            for t in top_trends
        ],
        "posting_frequency": _posting_frequency_rec(niche),
        "content_pillars": _content_pillars(niche),
        "engagement_hooks": _engagement_hooks(),
    }


def _optimize_account(
    platform: str,
    handle: str,
    niche: str,
    hashtags: list[dict[str, Any]],
    sounds: list[dict[str, Any]],
    trends: list[dict[str, Any]],
) -> dict[str, Any]:
    """Generate per-account recommendations."""
    tag_sets = generate_hashtag_sets(hashtags, niche=niche)
    posting_times = _optimal_posting_times(niche)
    content_angles = _suggest_content_angles(niche)

    bio = _optimized_bio(platform, handle, niche)
    cta = _call_to_action(platform, niche)

    platform_tips = _platform_specific_tips(platform, niche, sounds)

    return {
        "handle": handle,
        "platform": platform,
        "niche": niche,
        "bio_template": bio,
        "call_to_action": cta,
        "optimal_posting_times": posting_times,
        "recommended_hashtags": tag_sets["balanced"],
        "content_angles": content_angles[:5],
        "platform_tips": platform_tips,
        "monetization_paths": _monetization_paths(platform, niche),
    }


def _optimized_bio(platform: str, handle: str, niche: str) -> str:
    niche_cap = niche.title() if niche else "Content"
    templates = {
        "tiktok": f"🔥 Daily {niche_cap} content\n📱 New videos every day\n👇 Follow for more",
        "instagram": f"✨ {niche_cap} | Inspiration Daily\n📲 DM for collabs\n👇 Link in bio",
        "youtube": f"🎬 {niche_cap} Videos Weekly\nSubscribe for the best {niche_cap.lower()} content\n📧 Business: contact@email.com",
    }
    return templates.get(platform, f"Daily {niche_cap} content — Follow for more!")


def _call_to_action(platform: str, niche: str) -> list[str]:
    ctas = {
        "tiktok": [
            "Follow for more daily content 🔥",
            "Comment your thoughts below 👇",
            "Share this with someone who needs to see it",
            "Duet this if you agree!",
            "Follow before this blows up 📱",
        ],
        "instagram": [
            "Save this for later 📌",
            "Tag a friend who needs this!",
            "Double tap if this helped you ❤️",
            "Comment below with your experience",
            "Share to your story!",
        ],
        "youtube": [
            "Subscribe and hit the bell 🔔",
            "Comment your biggest takeaway",
            "Share this video — it helps the channel!",
            "Like if this was helpful 👍",
            "Watch the next video in the playlist →",
        ],
    }
    return ctas.get(platform, ["Follow for more!", "Share with a friend"])


def _platform_specific_tips(
    platform: str, niche: str, sounds: list[dict[str, Any]]
) -> list[str]:
    top_sound = sounds[0].get("title", "trending sound") if sounds else "a trending sound"

    tips = {
        "tiktok": [
            f"Use '{top_sound}' — currently the #1 trending sound for maximum reach",
            "Post 1-3x per day during peak hours (7am, 12pm, 7pm)",
            "Hook viewers in the first 0.5 seconds — start mid-action",
            "Use 3-5 hashtags max — quality over quantity on TikTok",
            "Reply to comments with video replies to boost engagement",
            "Stitch or Duet trending content in your niche",
            "Add captions — 80% of TikTok is watched without sound initially",
            "Shoot vertically (9:16), 1080x1920px, 15-60 seconds for best reach",
        ],
        "instagram": [
            "Post Reels daily — Instagram pushes Reels 3x more than static posts",
            f"Use '{top_sound}' on Reels — trending audio boosts distribution",
            "Use 3-5 hashtags on Reels, 10-15 on feed posts",
            "Carousel posts get 3x more saves than single images",
            "Stories: post 5-10 per day with interactive stickers (polls, questions)",
            "Collaborate with similar accounts for mutual shoutouts",
            "Pin your 3 best performing posts to your profile",
            "Go live once a week — Instagram rewards live creators",
        ],
        "youtube": [
            "Upload 2-3x per week consistently for the first 3 months",
            "Thumbnail + title determines 80% of click-through rate — test both",
            "First 30 seconds must deliver on the title's promise",
            "Add chapters to your videos for better watch-time metrics",
            "End screen + cards pointing to your best playlists",
            "Reply to every comment in the first 24 hours",
            "Research keywords with YouTube autosuggest before every upload",
            "Create a Shorts version of every long-form video",
        ],
    }
    return tips.get(platform, [
        "Post consistently",
        "Engage with your audience",
        "Use trending sounds and hashtags",
    ])


def _posting_frequency_rec(niche: str) -> dict[str, str]:
    return {
        "tiktok": "1-3 posts/day",
        "instagram_reels": "1 Reel/day",
        "instagram_feed": "4-5 posts/week",
        "instagram_stories": "5-10 stories/day",
        "youtube": "2-3 videos/week",
        "youtube_shorts": "1 Short/day",
    }


def _content_pillars(niche: str) -> list[str]:
    """Return 5 evergreen content pillars for a niche."""
    generic = [
        "Educational/How-to",
        "Entertainment/Trending",
        "Inspirational/Motivational",
        "Behind the Scenes",
        "User Generated / Community",
    ]
    niche_map = {
        "fitness": ["Workout tutorials", "Transformation stories", "Nutrition tips", "Equipment reviews", "Motivation"],
        "food": ["Recipes", "Restaurant reviews", "Food hacks", "Meal prep", "Taste tests"],
        "fashion": ["OOTDs", "Hauls", "Styling tips", "Trend reports", "Budget vs luxury"],
        "finance": ["How-to guides", "Success stories", "Product reviews", "Market insights", "Beginner tips"],
        "gaming": ["Gameplay clips", "Tutorials", "Reviews", "Community challenges", "Reactions"],
    }
    niche_lower = niche.lower()
    for key, pillars in niche_map.items():
        if key in niche_lower:
            return pillars
    return generic


def _engagement_hooks() -> list[str]:
    return [
        "Wait for it... (creates suspense, boosts watch time)",
        "This changed everything for me... (personal story hook)",
        "Nobody talks about this but... (exclusivity hook)",
        "POV: you just discovered... (relatable scenario)",
        "Stop doing this if you want [result] (negative hook)",
        "The secret [industry] doesn't want you to know (curiosity hook)",
        "I tried this for 30 days and... (challenge hook)",
        "Watch until the end — the last part is wild (retention hook)",
    ]


def _growth_tactics(niche: str) -> list[dict[str, str]]:
    return [
        {
            "tactic": "Trend Hijacking",
            "description": "Monitor trending sounds/hashtags daily and post content using them within 24h of trending",
            "effort": "Low",
            "impact": "High",
        },
        {
            "tactic": "Cross-Platform Repurposing",
            "description": "Post every TikTok to YouTube Shorts and Instagram Reels — 3x reach, 1x effort",
            "effort": "Low",
            "impact": "High",
        },
        {
            "tactic": "Comment Farming",
            "description": "Ask a question in every post caption. Reply to every comment in the first hour",
            "effort": "Medium",
            "impact": "High",
        },
        {
            "tactic": "Niche Collaboration",
            "description": "DM 5 accounts in your niche weekly for shoutout exchanges (similar follower count)",
            "effort": "Medium",
            "impact": "High",
        },
        {
            "tactic": "Viral Remix",
            "description": "Find the top 10 viral videos in your niche and create your own spin on the same concept",
            "effort": "Medium",
            "impact": "Very High",
        },
        {
            "tactic": "Pinned Comment Strategy",
            "description": "Pin a comment asking viewers to follow for part 2 — drives follower conversion",
            "effort": "Low",
            "impact": "Medium",
        },
        {
            "tactic": "Posting Window Optimization",
            "description": "Post at peak audience hours (7am, 12pm, 7pm local time for your target region)",
            "effort": "Low",
            "impact": "Medium",
        },
        {
            "tactic": "Authority Building",
            "description": "Post 1 ultra-high-value educational video per week that earns saves and shares",
            "effort": "High",
            "impact": "Very High",
        },
    ]


def _monetization_paths(platform: str, niche: str) -> list[dict[str, str]]:
    paths = {
        "tiktok": [
            {"method": "TikTok Creator Fund / LIVE Gifts", "timeline": "1,000+ followers", "est_revenue": "$0.02-0.04 per 1k views"},
            {"method": "Brand Deals", "timeline": "10k+ followers", "est_revenue": "$50-500 per post"},
            {"method": "Affiliate Marketing", "timeline": "Any size", "est_revenue": "5-20% commission per sale"},
            {"method": "Link in Bio (Linktree)", "timeline": "Any size", "est_revenue": "Drives to external offers"},
        ],
        "instagram": [
            {"method": "Instagram Bonuses / Gifts", "timeline": "Invited program", "est_revenue": "Variable"},
            {"method": "Sponsored Posts", "timeline": "5k+ followers", "est_revenue": "$100-2000 per post"},
            {"method": "Affiliate Links in Bio", "timeline": "Any size", "est_revenue": "5-30% commission"},
            {"method": "Sell Presets / Products", "timeline": "1k+ followers", "est_revenue": "$10-97 per product"},
        ],
        "youtube": [
            {"method": "YouTube AdSense", "timeline": "1k subs + 4k watch hours", "est_revenue": "$1-5 RPM"},
            {"method": "Channel Memberships", "timeline": "500+ subscribers", "est_revenue": "$4.99-49.99/month"},
            {"method": "Sponsored Integrations", "timeline": "5k+ subs", "est_revenue": "$100-5000 per video"},
            {"method": "Merchandise", "timeline": "10k+ subs", "est_revenue": "Variable"},
        ],
    }
    return paths.get(platform, [
        {"method": "Affiliate Marketing", "timeline": "Any size", "est_revenue": "Commission-based"},
        {"method": "Brand Deals", "timeline": "Growing audience", "est_revenue": "Negotiated"},
    ])


# ── Content calendar builder ───────────────────────────────────────────

def build_content_calendar(
    trends: list[dict[str, Any]],
    hashtags: list[dict[str, Any]],
    niche: str = "",
    days: int = 7,
) -> list[dict[str, Any]]:
    """Generate a 7-day content calendar based on current trends.

    Returns list of day plans with: day, theme, content_idea,
    hashtags, best_time, platform_notes.
    """
    import datetime

    content_angles = _suggest_content_angles(niche or "general")
    top_tags = [h["tag"] for h in hashtags[:15]]
    top_trends = trends[:days]

    calendar = []
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    themes = [
        "Educational",
        "Trending Reaction",
        "Behind the Scenes",
        "Inspirational",
        "Challenge/Interactive",
        "Showcase/Review",
        "Community Engagement",
    ]

    for i in range(days):
        day_name = days_of_week[i % 7]
        theme = themes[i % len(themes)]
        angle = content_angles[i % len(content_angles)]

        # Use actual trend as content inspiration if available
        trend_inspiration = top_trends[i] if i < len(top_trends) else {}
        inspired_by = trend_inspiration.get("title", "")

        # Pick hashtags: rotate to avoid repetition
        start = (i * 5) % max(len(top_tags), 1)
        day_tags = (top_tags + top_tags)[start:start + 8]

        calendar.append({
            "day": day_name,
            "theme": theme,
            "content_idea": angle,
            "inspired_by": inspired_by,
            "hashtags": day_tags,
            "best_posting_time": _optimal_posting_times(niche)[i % 3],
            "platforms": ["TikTok", "Instagram Reels", "YouTube Shorts"],
            "notes": _day_specific_notes(day_name, theme),
        })

    return calendar


def _day_specific_notes(day: str, theme: str) -> str:
    notes = {
        "Monday": "High engagement day — post your best content for the week",
        "Tuesday": "Strong posting day — audience is active mid-morning",
        "Wednesday": "Mid-week peak — great for trending/reaction content",
        "Thursday": "Pre-weekend traffic spike starts — push CTAs",
        "Friday": "Entertainment content performs best — keep it fun",
        "Saturday": "Highest casual viewing — longer form does better",
        "Sunday": "Plan and batch next week's content — post 1 evergreen piece",
    }
    return notes.get(day, "Post consistently and engage with comments")
