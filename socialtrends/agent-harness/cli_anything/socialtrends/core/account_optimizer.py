"""Account optimization engine for TikTok, Instagram, and YouTube.

Generates platform-specific optimization recommendations for:
- Bio and profile setup
- Posting schedules (timezone-adjusted)
- Caption formulas
- Content strategy frameworks
- Engagement rate benchmarks
"""

from __future__ import annotations
import re
from typing import Literal

Platform = Literal["tiktok", "instagram", "youtube", "twitter"]

# ── Platform specifications ───────────────────────────────────────────────────

PLATFORM_SPECS: dict[str, dict] = {
    "tiktok": {
        "bio_limit": 80,
        "username_limit": 24,
        "name_limit": 30,
        "hashtag_sweet_spot": "3–5 in caption, 20–30 in first comment",
        "caption_length": "50–150 chars (short punchy captions win)",
        "video_length": {
            "optimal": "7–30 seconds for virality",
            "education": "60–180 seconds for watch-through",
            "stories": "Use 15-second Stories for announcements",
        },
        "best_post_times_et": {
            "weekday": ["6:00 AM", "10:00 AM", "7:00 PM", "9:00 PM"],
            "weekend": ["9:00 AM", "12:00 PM", "3:00 PM", "8:00 PM"],
        },
        "posting_frequency": "1–4 videos/day for rapid growth",
        "profile_picture": "Clear face/logo, high contrast, no text",
        "link_in_bio": "Use Linktree or Beacons — TikTok allows 1 link",
        "algorithm_signals": [
            "Watch-through rate (complete views) — most important",
            "Shares — strongest signal after watch time",
            "Comments — add engagement",
            "Likes — least important signal",
            "Re-watches — huge positive signal",
        ],
        "growth_hacks": [
            "Post on viral sounds within first 24h of a sound trending",
            "Reply to comments with a video — gets extra distribution",
            "Use trending templates from CapCut",
            "First 1–3 seconds MUST hook — or viewers scroll",
            "Pin 3 best-performing videos to profile",
            "Duet or stitch trending creators in your niche",
        ],
    },
    "instagram": {
        "bio_limit": 150,
        "username_limit": 30,
        "name_limit": 30,
        "hashtag_sweet_spot": "3–5 in caption OR 20–30 in comment",
        "caption_length": "125–2200 chars (first line is the hook — make it count)",
        "video_length": {
            "reels": "7–30 seconds for max reach, up to 90s for depth",
            "carousel": "Up to 10 slides — use final slide as CTA",
            "stories": "15 seconds, use interactive elements",
        },
        "best_post_times_et": {
            "weekday": ["7:00 AM", "11:00 AM", "2:00 PM", "5:00 PM"],
            "weekend": ["10:00 AM", "1:00 PM", "4:00 PM"],
        },
        "posting_frequency": "1 Reel/day + 2–5 Stories/day for growth",
        "profile_picture": "Brand logo or professional headshot — 320x320px",
        "link_in_bio": "Linktree/Beacons with 5+ links (products, lead magnet, etc.)",
        "algorithm_signals": [
            "Saves — #1 signal for Reels algorithm",
            "Shares to Stories/DMs — 2nd strongest",
            "Comments (especially back-and-forth threads)",
            "Profile visits from a post",
            "Watch-through rate on Reels",
        ],
        "growth_hacks": [
            "Ask 'Save this for later' at the end of every educational post",
            "Use carousel posts — 3x more reach than single images",
            "Post Reels with trending audio within 72h of audio trending",
            "Reply to EVERY comment in the first hour — triggers algorithm",
            "Collab posts with creators in adjacent niches",
            "Story Polls/Questions boost engagement signals",
        ],
    },
    "youtube": {
        "bio_limit": 1000,
        "username_limit": 20,
        "name_limit": 100,
        "hashtag_sweet_spot": "3–5 in description, up to 15 total",
        "caption_length": "Description: 250–5000 chars with keyword-rich first 125 chars",
        "video_length": {
            "shorts": "15–60 seconds for Shorts feed",
            "tutorials": "8–20 minutes for tutorial content",
            "vlogs": "10–25 minutes for vlog content",
            "long_form": "20–60 minutes for deep-dive content",
        },
        "best_post_times_et": {
            "weekday": ["12:00 PM", "3:00 PM", "7:00 PM"],
            "weekend": ["9:00 AM", "12:00 PM", "3:00 PM"],
        },
        "posting_frequency": "1 long-form/week + 3–5 Shorts/week",
        "profile_picture": "Logo or face — consistent with other platforms",
        "link_in_bio": "Channel description + pinned comment + end screen",
        "algorithm_signals": [
            "Click-through rate (CTR) from thumbnail+title — most important",
            "Average view duration / percentage viewed",
            "Session starts (first video a user watches)",
            "Satisfaction signals (likes, comments, 'not interested' ratio)",
        ],
        "growth_hacks": [
            "Thumbnail face with emotion outperforms text-only by 40%",
            "Title: include exact search keyword + intrigue/controversy",
            "Upload Shorts versions of long-form content",
            "Post within trending topic's first 48h window",
            "End cards to next video keep viewers in session",
            "Chapters (timestamps) improve watch duration",
        ],
    },
}


def get_platform_spec(platform: str) -> dict:
    """Return full spec sheet for a platform.

    Args:
        platform: tiktok, instagram, or youtube

    Returns:
        Platform specifications dict
    """
    spec = PLATFORM_SPECS.get(platform.lower())
    if not spec:
        return {"error": f"Unknown platform '{platform}'.", "available": list(PLATFORM_SPECS.keys())}
    return {"platform": platform, **spec}


def generate_bio(
    platform: str,
    niche: str,
    name: str,
    cta: str = "",
    keywords: list[str] | None = None,
) -> dict:
    """Generate an optimized bio template for a platform.

    Args:
        platform: tiktok, instagram, or youtube
        niche: Content niche (fitness, food, etc.)
        name: Creator/brand name
        cta: Call-to-action text (e.g. "Download my free guide")
        keywords: Niche keywords to embed

    Returns:
        Dict with bio_template, char_count, tips
    """
    spec = PLATFORM_SPECS.get(platform.lower(), {})
    limit = spec.get("bio_limit", 150)
    kws = keywords or [niche]

    templates = {
        "tiktok": (
            f"{name} | {niche.title()} Content\n"
            f"✨ {kws[0].title()} tips & tricks\n"
            f"{'📩 ' + cta if cta else '👇 Links below'}"
        ),
        "instagram": (
            f"✨ {name}\n"
            f"📍 {niche.title()} Creator\n"
            f"🎯 {kws[0].title()} | {kws[1].title() if len(kws) > 1 else 'Lifestyle'}\n"
            f"{'💌 ' + cta if cta else '🔗 Free resources below ↓'}"
        ),
        "youtube": (
            f"Welcome to {name} — your home for {niche} content.\n\n"
            f"We post {kws[0]} tips, tutorials, and {kws[-1]} insights every week.\n"
            f"{'→ ' + cta if cta else '→ Subscribe for weekly ' + niche + ' content!'}\n\n"
            f"Business: contact@{name.lower().replace(' ', '')}.com"
        ),
    }

    bio = templates.get(platform.lower(), templates["instagram"])
    char_count = len(bio)

    tips = [
        f"Limit is {limit} chars — you're using {char_count}.",
        "Include 1 clear value proposition (what viewers get).",
        "Add 1 CTA — link, DM, or subscribe.",
    ]
    if char_count > limit:
        tips.insert(0, f"⚠ Bio exceeds {platform} limit by {char_count - limit} chars — trim it.")

    return {
        "platform": platform,
        "bio_template": bio,
        "char_count": char_count,
        "limit": limit,
        "tips": tips,
    }


def get_posting_schedule(
    platform: str,
    timezone: str = "ET",
    posts_per_week: int = 7,
) -> dict:
    """Generate a weekly posting schedule optimized for platform algorithm.

    Args:
        platform: tiktok, instagram, or youtube
        timezone: Timezone label (ET, PT, GMT, etc.) — for display only
        posts_per_week: Target posts per week

    Returns:
        Dict with schedule, frequency_note, timezone_note
    """
    spec = PLATFORM_SPECS.get(platform.lower(), {})
    times = spec.get("best_post_times_et", {"weekday": ["7:00 PM"], "weekend": ["12:00 PM"]})
    freq = spec.get("posting_frequency", "1/day")

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekdays = days[:5]
    weekend = days[5:]

    schedule = []
    for i, day in enumerate(days):
        is_weekend = day in weekend
        day_times = times.get("weekend" if is_weekend else "weekday", [])
        n_posts = max(1, posts_per_week // 7)
        post_times = day_times[:n_posts]
        schedule.append({"day": day, "post_at": post_times, "post_count": len(post_times)})

    offset_note = {
        "ET": "ET = UTC-5 (EST) / UTC-4 (EDT)",
        "PT": "Subtract 3h from ET times above",
        "GMT": "Add 5h to ET times above",
        "CET": "Add 6h to ET times above",
        "IST": "Add 10.5h to ET times above",
        "AEST": "Add 15h to ET times above",
    }.get(timezone, f"Adjust from ET accordingly for {timezone}")

    return {
        "platform": platform,
        "schedule": schedule,
        "frequency_note": freq,
        "times_in_et": True,
        "timezone_note": offset_note,
        "pro_tip": (
            "Post consistently at the same time daily — "
            "the algorithm rewards predictable posting patterns."
        ),
    }


def generate_caption(
    topic: str,
    niche: str,
    platform: str = "tiktok",
    include_hashtags: bool = False,
    hashtags: list[str] | None = None,
) -> dict:
    """Generate an engagement-optimized caption using proven formulas.

    Args:
        topic: What the content is about
        niche: Content niche
        platform: Target platform
        include_hashtags: Whether to append hashtags to caption
        hashtags: Hashtags to append (if include_hashtags=True)

    Returns:
        Dict with captions, formula_used, tips
    """
    topic_clean = topic.strip().rstrip(".")

    caption_formulas = {
        "hook_value_cta": (
            f"POV: You finally understand {topic_clean} 👀\n\n"
            f"Here's what nobody tells you about {niche}:\n\n"
            f"Save this for later 🔖"
        ),
        "question_hook": (
            f"Why does NOBODY talk about {topic_clean}? 🤯\n\n"
            f"This changed my entire {niche} game.\n"
            f"Drop a ❤ if this helped!"
        ),
        "story_hook": (
            f"I spent 3 months studying {topic_clean} so you don't have to.\n\n"
            f"Here's what I learned about {niche}:\n"
            f"Comment '{niche.upper()}' and I'll send you more."
        ),
        "listicle": (
            f"5 things about {topic_clean} that will change how you do {niche}:\n\n"
            f"1️⃣ [Most surprising insight]\n"
            f"2️⃣ [Actionable tip]\n"
            f"3️⃣ [Common mistake]\n"
            f"4️⃣ [Pro tip]\n"
            f"5️⃣ [Best practice]\n\n"
            f"Which one surprised you most? 👇"
        ),
        "contrarian": (
            f"Hot take: {topic_clean} is NOT what you think it is 🔥\n\n"
            f"Agree or disagree? Let me know below 👇"
        ),
    }

    # Pick best formula for platform
    formula_pick = {
        "tiktok": "hook_value_cta",
        "instagram": "listicle",
        "youtube": "story_hook",
    }.get(platform.lower(), "hook_value_cta")

    main_caption = caption_formulas[formula_pick]
    spec = PLATFORM_SPECS.get(platform.lower(), {})
    cap_len = spec.get("caption_length", "50–300 chars")

    if include_hashtags and hashtags:
        main_caption += "\n\n" + " ".join(hashtags[:30])

    return {
        "platform": platform,
        "topic": topic,
        "formula_used": formula_pick,
        "caption": main_caption,
        "char_count": len(main_caption),
        "caption_length_guide": cap_len,
        "all_formulas": caption_formulas,
        "tips": [
            "Hook must be in the first line — it's what people see before 'more'.",
            "End with a question or CTA to drive comments.",
            "Test different formulas and track which drives most watch-through.",
        ],
    }


def calculate_engagement_rate(
    followers: int,
    likes: int,
    comments: int,
    shares: int = 0,
    saves: int = 0,
) -> dict:
    """Calculate engagement rate and benchmark against industry standards.

    Args:
        followers: Total follower count
        likes: Likes on post/video
        comments: Comments on post/video
        shares: Shares (optional)
        saves: Saves/bookmarks (optional)

    Returns:
        Dict with er_percent, rating, benchmark, improvement_tips
    """
    total_engagement = likes + comments + shares * 2 + saves * 3
    er = (total_engagement / followers * 100) if followers else 0

    benchmarks = [
        (20,  "Viral 🔥",    "Top 1% — exceptional, keep doing what you're doing."),
        (10,  "Excellent ✅", "Top 5% — strong community engagement."),
        (5,   "Good 👍",      "Industry average for established accounts."),
        (2,   "Average 😐",   "Typical for large accounts (100k+). Focus on saves/shares."),
        (1,   "Below avg ⚠", "Needs improvement — focus on hooks and CTAs."),
        (0,   "Low 🚨",       "Very low — review content quality and posting frequency."),
    ]

    rating, advice = "Low 🚨", ""
    for threshold, label, tip in benchmarks:
        if er >= threshold:
            rating, advice = label, tip
            break

    return {
        "followers": followers,
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "saves": saves,
        "engagement_rate_percent": round(er, 2),
        "rating": rating,
        "benchmark_advice": advice,
        "improvement_tips": [
            "Add a question at end of every caption — minimum 3x comments.",
            "Reply to every comment within 1 hour of posting.",
            "Ask viewers to 'save this for later' — saves are the #1 signal.",
            "Use polls/interactive stickers in Stories/Community posts.",
            "Post at peak times for your specific audience (check analytics).",
        ],
    }


def full_account_audit(
    platform: str,
    niche: str,
    followers: int,
    avg_likes: int,
    avg_comments: int,
    posts_per_week: int,
    has_link_in_bio: bool = True,
    bio_has_cta: bool = False,
) -> dict:
    """Run a complete account audit with actionable recommendations.

    Args:
        platform: tiktok, instagram, or youtube
        niche: Content niche
        followers: Follower count
        avg_likes: Average likes per post
        avg_comments: Average comments per post
        posts_per_week: Current posting frequency
        has_link_in_bio: Whether a link is in bio
        bio_has_cta: Whether bio has a clear CTA

    Returns:
        Dict with overall_score, issues, recommendations, priority_actions
    """
    er_data = calculate_engagement_rate(followers, avg_likes, avg_comments)
    er = er_data["engagement_rate_percent"]

    issues: list[str] = []
    wins: list[str] = []
    priority: list[str] = []

    spec = PLATFORM_SPECS.get(platform.lower(), {})
    rec_freq = spec.get("posting_frequency", "1/day")

    # Engagement check
    if er < 2:
        issues.append(f"Low engagement rate ({er}%) — content not resonating.")
        priority.append("A/B test 2 different hook styles this week.")
    elif er >= 5:
        wins.append(f"Strong engagement rate ({er}%) — above average.")

    # Posting frequency
    if posts_per_week < 3:
        issues.append(f"Low posting frequency ({posts_per_week}/week) — algorithm rewards consistency.")
        priority.append(f"Increase to 5+ posts/week. Recommended: {rec_freq}.")
    else:
        wins.append(f"Good posting frequency ({posts_per_week}/week).")

    # Bio
    if not has_link_in_bio:
        issues.append("No link in bio — missing conversion opportunity.")
        priority.append("Add Linktree/Beacons link immediately.")
    if not bio_has_cta:
        issues.append("Bio lacks a clear CTA — visitors don't know what action to take.")
        priority.append("Add 1 specific CTA to bio (e.g. 'Download free guide ↓').")

    score = max(0, 100 - len(issues) * 15 + len(wins) * 5)

    return {
        "platform": platform,
        "niche": niche,
        "followers": followers,
        "engagement_rate": er,
        "engagement_rating": er_data["rating"],
        "overall_score": min(100, score),
        "wins": wins,
        "issues": issues,
        "priority_actions": priority,
        "recommendations": spec.get("growth_hacks", []),
        "algorithm_signals": spec.get("algorithm_signals", []),
    }
