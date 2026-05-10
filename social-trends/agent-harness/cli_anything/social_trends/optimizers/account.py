"""Account optimizer — generate platform-specific growth strategies from trend data."""
from __future__ import annotations

import time
from typing import Any


PLATFORMS = ["tiktok", "youtube", "instagram", "all"]

# Optimal posting specs per platform
PLATFORM_SPECS = {
    "tiktok": {
        "video_length": "15–60s (sweet spot: 21–34s for FYP push; 3–5min for retention bonuses)",
        "aspect_ratio": "9:16 (1080×1920)",
        "caption_limit": "2200 chars",
        "hashtag_limit": "5–7 (avoid stuffing — 3 niche + 2 broad + 1–2 trending)",
        "best_times": ["6:00–9:00 AM", "12:00–3:00 PM", "7:00–11:00 PM"],
        "hook_window": "First 1–3 seconds",
        "algorithm_signals": ["completion rate", "re-watches", "shares", "saves", "comments"],
        "cta_placement": "End of video + pinned comment",
        "bio_limit": "80 chars",
    },
    "youtube": {
        "video_length": "Shorts: 15–60s | Long-form: 8–15 min (ad-break sweet spot)",
        "aspect_ratio": "16:9 (long-form) | 9:16 (Shorts)",
        "caption_limit": "5000 chars (first 200 shown above fold)",
        "hashtag_limit": "3–5 (YouTube penalizes over-tagging)",
        "best_times": ["2:00–4:00 PM Fri–Sun", "12:00–3:00 PM weekdays"],
        "hook_window": "First 30 seconds (determines churn rate)",
        "algorithm_signals": ["CTR", "AVD (avg view duration)", "likes", "subs after watch"],
        "cta_placement": "30s mark + end screen + pinned comment",
        "bio_limit": "1000 chars",
    },
    "instagram": {
        "video_length": "Reels: 15–90s (60s optimal) | Stories: 15s per card",
        "aspect_ratio": "9:16 (Reels/Stories) | 1:1 (feed)",
        "caption_limit": "2200 chars (first 125 shown)",
        "hashtag_limit": "3–10 (5 is optimal — mix niche + broad)",
        "best_times": ["8:00–9:00 AM", "11:00 AM–1:00 PM", "7:00–9:00 PM"],
        "hook_window": "First 3 seconds",
        "algorithm_signals": ["saves", "shares", "DMs", "comments", "story replies"],
        "cta_placement": "Caption + Stories swipe-up link",
        "bio_limit": "150 chars + link in bio",
    },
}

# Growth phases and their strategies
GROWTH_PHASES = {
    "0–1k": {
        "label": "Launch Phase",
        "goal": "Establish content identity and initial audience",
        "strategy": [
            "Post 2–3x/day on TikTok, 1x/day on Shorts — volume beats quality at this stage",
            "Duet and stitch trending videos to piggyback their reach",
            "Reply to every comment with a video reply — boosts distribution",
            "Follow 20–30 creators in your niche daily (unfollow after 72h if no follow-back)",
            "Use 1–2 mega hashtags (#fyp) + 2–3 niche hashtags only",
            "Study your 'For You' page for 30 min/day — TikTok reveals your ideal audience",
        ],
        "avoid": [
            "Buying followers — kills engagement rate permanently",
            "Posting without a hook in the first 2 seconds",
            "Inconsistent niche — algorithm can't categorize your content",
        ],
    },
    "1k–10k": {
        "label": "Momentum Phase",
        "goal": "Convert algorithmic reach into loyal followers",
        "strategy": [
            "Post 1–2x/day — quality begins to matter more than pure volume",
            "Pin your 3 best videos at the top of your profile",
            "Introduce a content series (recurring format builds return viewers)",
            "Analyze which videos hit >20% follower-to-view ratio — double down on that format",
            "Engage in comment sections of trending creators in your niche",
            "Start cross-posting: TikTok → YouTube Shorts → Instagram Reels (watermark removal required)",
            "Add a link in bio (TikTok Business unlocks this at 1k)",
        ],
        "avoid": [
            "Deleting underperforming videos — it resets distribution signals",
            "Switching niches after momentum begins",
        ],
    },
    "10k–100k": {
        "label": "Scale Phase",
        "goal": "Build monetizable audience and brand deals pipeline",
        "strategy": [
            "Batch content: record 5–7 videos per session, post on schedule",
            "A/B test thumbnails and hooks — 80% of views are driven by the first 2s",
            "Introduce collaboration strategy: duets, collabs, and shoutout-for-shoutout (SFS)",
            "Start email/Discord list capture — platform-independent audience ownership",
            "Apply for YouTube Partner Program (1k subs + 4k watch hours or 10M Shorts views)",
            "TikTok Creator Fund ($0.02–0.04/1k views) — supplement with brand deals ($250–2k/post)",
            "Research sponsored content rates in your niche — CPM x audience size = your floor rate",
        ],
        "avoid": [
            "Over-posting (burnout kills consistency — the #1 predictor of growth)",
            "Ignoring analytics — post at your audience's peak active hours",
        ],
    },
    "100k+": {
        "label": "Authority Phase",
        "goal": "Diversify revenue and build multi-platform brand",
        "strategy": [
            "Launch digital product (course, preset pack, e-book) — 1% conversion at 100k = $10k+ launch",
            "Negotiate 3–6 month brand partnership retainers instead of one-off posts",
            "Hire a video editor and thumbnail designer — free your creative bandwidth",
            "Build YouTube long-form to capture evergreen search traffic (vs. short-form algorithmic feed)",
            "Start a newsletter or Substack — direct audience relationship independent of algorithms",
            "License your content to media brands (Jukin Media, ViralHog, etc.)",
        ],
        "avoid": [
            "Staying on a single platform — algorithm changes can zero out income overnight",
        ],
    },
}


def generate_account_optimization(
    platform: str = "all",
    niche: str = "",
    follower_count: int = 0,
    trend_data: dict | None = None,
) -> dict:
    """
    Generate a personalized account optimization plan.

    Args:
        platform: Target platform(s) — tiktok, youtube, instagram, or all
        niche: Content niche (e.g., finance, fitness, beauty, gaming)
        follower_count: Current follower count (determines growth phase advice)
        trend_data: Output from generate_full_report() for trend-specific tips
    """
    platforms = list(PLATFORM_SPECS.keys()) if platform == "all" else [platform.lower()]
    platforms = [p for p in platforms if p in PLATFORM_SPECS]

    growth_phase = _determine_growth_phase(follower_count)
    phase_data = GROWTH_PHASES[growth_phase]

    platform_configs = {p: PLATFORM_SPECS[p] for p in platforms}

    trend_tips = []
    if trend_data:
        trend_tips = _extract_trend_tips(trend_data, niche)

    bio_templates = _generate_bio_templates(niche, platforms)
    content_calendar = _generate_content_calendar(platforms, niche, trend_data)
    hashtag_strategy = _build_hashtag_strategy(niche, trend_data, platforms)

    return {
        "platform": platform,
        "niche": niche or "general",
        "follower_count": follower_count,
        "growth_phase": {
            "range": growth_phase,
            "label": phase_data["label"],
            "goal": phase_data["goal"],
        },
        "platform_specs": platform_configs,
        "growth_strategy": {
            "actions": phase_data["strategy"],
            "avoid": phase_data["avoid"],
        },
        "trend_specific_tips": trend_tips,
        "hashtag_strategy": hashtag_strategy,
        "bio_templates": bio_templates,
        "content_calendar": content_calendar,
        "monetization_roadmap": _build_monetization_roadmap(follower_count, niche),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def _determine_growth_phase(follower_count: int) -> str:
    if follower_count < 1000:
        return "0–1k"
    if follower_count < 10000:
        return "1k–10k"
    if follower_count < 100000:
        return "10k–100k"
    return "100k+"


def _extract_trend_tips(trend_data: dict, niche: str) -> list[str]:
    tips = []
    summary = trend_data.get("summary", {})

    top_tags = summary.get("top_5_hashtags", [])
    if top_tags:
        tips.append(f"Add these NOW-trending tags to your next post: {' '.join(top_tags[:3])}")

    top_sounds = summary.get("top_3_sounds", [])
    if top_sounds:
        tips.append(f"Use trending audio: '{top_sounds[0]}' — early adopters get 5–10x more distribution")

    action_items = trend_data.get("action_items", [])
    tips.extend(action_items[:3])

    cross = trend_data.get("hashtags", {}).get("cross_platform", [])
    if cross:
        tags = " ".join(h["tag"] for h in cross[:4])
        tips.append(f"These tags are hot on BOTH platforms — use them on every post: {tags}")

    return tips


def _generate_bio_templates(niche: str, platforms: list[str]) -> dict:
    niche_label = niche or "content"
    templates: dict[str, list[str]] = {}

    for platform in platforms:
        limit = PLATFORM_SPECS[platform]["bio_limit"]
        templates[platform] = [
            f"🎯 Daily {niche_label} tips | Follow for {niche_label} secrets | New videos {_post_freq(platform)}",
            f"Teaching you {niche_label} | {_follower_social_proof()} | 👇 Free resource below",
            f"Your {niche_label} guide 📚 | Simplified strategies | Join {_post_freq(platform)}",
        ]
    return templates


def _post_freq(platform: str) -> str:
    return {"tiktok": "daily", "youtube": "weekly", "instagram": "daily"}.get(platform, "regularly")


def _follower_social_proof() -> str:
    return "Join 10k+ learners"


def _generate_content_calendar(
    platforms: list[str],
    niche: str,
    trend_data: dict | None,
) -> list[dict]:
    """Generate a 7-day content calendar with platform-specific post ideas."""
    content_angles = []
    if trend_data:
        content_angles = trend_data.get("topics", {}).get("content_angles", [])

    niche_label = niche or "your niche"
    base_formats = [
        f"Hook + controversy: 'The truth about {niche_label} nobody tells you'",
        f"Quick tutorial: '3 {niche_label} tips in 30 seconds'",
        f"Story + lesson: 'I tried this {niche_label} hack for 7 days — here's what happened'",
        f"Trending audio: Repurpose top trending sound with {niche_label} content",
        f"Social proof: 'How I grew my {niche_label} account from 0 to [milestone]'",
        f"Reaction/Commentary: React to a viral {niche_label} video (stitch/duet)",
        f"Value bomb: 'Free {niche_label} resource — save this video'",
    ]

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    calendar = []
    for i, day in enumerate(days):
        idea = base_formats[i % len(base_formats)]
        if content_angles and i < len(content_angles):
            idea = content_angles[i]
        calendar.append({
            "day": day,
            "idea": idea,
            "platforms": platforms,
            "best_time": PLATFORM_SPECS.get(platforms[0] if platforms else "tiktok", {}).get("best_times", ["6:00 PM"])[i % 3],
            "format": "short-form" if i % 3 != 2 else "long-form (YouTube) / carousel (IG)",
        })
    return calendar


def _build_hashtag_strategy(
    niche: str,
    trend_data: dict | None,
    platforms: list[str],
) -> dict:
    strategy: dict[str, Any] = {}

    trending_tags = []
    if trend_data:
        trending_tags = [h["tag"] for h in trend_data.get("hashtags", {}).get("top_hashtags", [])[:10]]

    niche_tags = _niche_hashtags(niche)

    for platform in platforms:
        limit_str = PLATFORM_SPECS[platform]["hashtag_limit"]
        strategy[platform] = {
            "formula": limit_str,
            "trending_now": trending_tags[:5],
            "niche_specific": niche_tags[:5],
            "evergreen": ["#fyp", "#viral", "#trending"] if platform == "tiktok" else ["#youtube", "#youtubeshorts"],
            "example_combo": (trending_tags[:2] + niche_tags[:3])[:6],
        }
    return strategy


def _niche_hashtags(niche: str) -> list[str]:
    tag_map = {
        "finance": ["#personalfinance", "#investing", "#moneytips", "#financialfreedom", "#stockmarket"],
        "fitness": ["#fitness", "#workout", "#gym", "#health", "#fitnessmotivation"],
        "beauty": ["#beauty", "#makeup", "#skincare", "#beautytips", "#glam"],
        "gaming": ["#gaming", "#gamer", "#videogames", "#twitch", "#gaminglife"],
        "food": ["#food", "#foodtok", "#recipe", "#cooking", "#foodie"],
        "tech": ["#tech", "#technology", "#ai", "#coding", "#developer"],
        "fashion": ["#fashion", "#style", "#ootd", "#outfitoftheday", "#fashiontok"],
        "business": ["#entrepreneur", "#business", "#hustle", "#startups", "#sidehustle"],
        "travel": ["#travel", "#wanderlust", "#traveltok", "#adventure", "#explore"],
        "education": ["#learnontiktok", "#education", "#didyouknow", "#facts", "#lifehacks"],
    }
    niche_lower = niche.lower() if niche else ""
    for key, tags in tag_map.items():
        if key in niche_lower or niche_lower in key:
            return tags
    return ["#content", "#creator", "#viral", "#trending", "#fyp"]


def _build_monetization_roadmap(follower_count: int, niche: str) -> list[dict]:
    phase = _determine_growth_phase(follower_count)
    roadmap = [
        {
            "milestone": "1,000 followers",
            "unlocks": ["TikTok link in bio", "Instagram swipe-up stories (business)", "YouTube community posts"],
            "estimated_revenue": "$0 (build phase)",
            "status": "completed" if follower_count >= 1000 else "pending",
        },
        {
            "milestone": "10,000 followers",
            "unlocks": ["Brand deal inquiries ($50–500/post)", "TikTok Creator Marketplace access", "Affiliate marketing conversions become meaningful"],
            "estimated_revenue": "$100–2k/month",
            "status": "completed" if follower_count >= 10000 else "pending",
        },
        {
            "milestone": "50,000 followers",
            "unlocks": ["YouTube Partner Program (if 1k subs + 4k watch hrs)", "Consistent brand deals ($500–2k/post)", "Digital product launch viability"],
            "estimated_revenue": "$500–5k/month",
            "status": "completed" if follower_count >= 50000 else "pending",
        },
        {
            "milestone": "100,000 followers",
            "unlocks": ["5-figure brand deals", "Course/coaching launch ($10k+ potential)", "Speaking/consulting inquiries"],
            "estimated_revenue": "$2k–20k/month",
            "status": "completed" if follower_count >= 100000 else "pending",
        },
        {
            "milestone": "1,000,000 followers",
            "unlocks": ["6-figure brand partnerships", "TV/media opportunities", "Licensing deals", "Agency representation"],
            "estimated_revenue": "$20k–200k/month",
            "status": "completed" if follower_count >= 1000000 else "pending",
        },
    ]
    return roadmap
