"""Content planner — generate a posting calendar from live trends.

Combines trending hashtags, sounds, and themes into a ready-to-execute
weekly/monthly content plan optimised for each platform.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

from cli_anything.social_trends.core import tiktok_trends, youtube_trends, trend_analyzer


# ── Plan generators ───────────────────────────────────────────────────────────

def generate_weekly_plan(platform: str = "tiktok", niche: str = "general",
                         region: str = "US",
                         posts_per_day: int = 2) -> dict:
    """Generate a 7-day content plan with trending hashtags and sounds."""
    platform = platform.lower()
    today = datetime.now()

    # Fetch live trends
    try:
        if platform == "tiktok":
            hashtags = tiktok_trends.get_trending_hashtags(region)
            sounds = tiktok_trends.get_trending_sounds(region)
        else:
            yt_tags = youtube_trends.get_trending_hashtags(region)
            hashtags = yt_tags
            sounds = []
    except Exception:
        hashtags = []
        sounds = []

    top_tags = [h["hashtag"] for h in hashtags[:10]]
    top_sounds = [f"{s['title']} — {s['author']}" for s in sounds[:5]]

    days = []
    content_themes = _content_themes_for_niche(niche)
    for i in range(7):
        day = today + timedelta(days=i)
        day_name = day.strftime("%A")
        day_str = day.strftime("%Y-%m-%d")

        day_posts = []
        for j in range(posts_per_day):
            theme_idx = (i * posts_per_day + j) % len(content_themes)
            theme = content_themes[theme_idx]
            day_posts.append({
                "post_number": j + 1,
                "time": _optimal_time(platform, day.weekday(), j),
                "content_type": theme["type"],
                "concept": theme["concept"],
                "hook": theme["hook"],
                "suggested_hashtags": _select_hashtags(top_tags, niche, platform, 5),
                "suggested_sound": top_sounds[j % len(top_sounds)] if top_sounds else None,
                "cta": theme["cta"],
            })

        days.append({
            "date": day_str,
            "day": day_name,
            "posts": day_posts,
        })

    return {
        "platform": platform,
        "niche": niche,
        "region": region,
        "week_of": today.strftime("%Y-%m-%d"),
        "posts_per_day": posts_per_day,
        "days": days,
        "trending_hashtags": top_tags[:10],
        "trending_sounds": top_sounds[:5],
        "generated_at": today.isoformat(),
    }


def generate_hashtag_set(niche: str = "general", platform: str = "tiktok",
                         region: str = "US", count: int = 7) -> dict:
    """Generate an optimised hashtag set for a post."""
    try:
        if platform == "tiktok":
            live_tags = [h["hashtag"] for h in tiktok_trends.get_trending_hashtags(region)[:15]]
        else:
            live_tags = [h["hashtag"] for h in youtube_trends.get_trending_hashtags(region)[:15]]
    except Exception:
        live_tags = []

    selected = _select_hashtags(live_tags, niche, platform, count)
    scored = trend_analyzer.score_hashtag_set(selected)
    return {
        "platform": platform,
        "niche": niche,
        "hashtag_set": selected,
        "analysis": scored,
        "copy_paste": " ".join(selected),
    }


def generate_content_ideas(niche: str = "general", count: int = 10,
                           region: str = "US") -> list[dict]:
    """Generate content ideas based on live trends in a niche."""
    try:
        yt_videos = youtube_trends.get_trending_videos(region, max_results=15)
        tt_videos = tiktok_trends.get_trending_videos(region)
    except Exception:
        yt_videos = []
        tt_videos = []

    merged = trend_analyzer.merge_trends(yt_videos, tt_videos)
    top_themes = [t["theme"] for t in merged.get("top_themes", [])[:5]]

    templates = _idea_templates(niche, top_themes)
    return templates[:count]


# ── Internal helpers ──────────────────────────────────────────────────────────

def _optimal_time(platform: str, weekday: int, post_idx: int) -> str:
    """Return a recommended posting time for the given platform and day."""
    # Research-backed best times (general baseline)
    tt_times = [
        ["7:00 AM", "12:00 PM", "7:00 PM"],  # Mon
        ["8:00 AM", "1:00 PM", "8:00 PM"],   # Tue
        ["7:00 AM", "12:00 PM", "9:00 PM"],  # Wed
        ["9:00 AM", "2:00 PM", "7:00 PM"],   # Thu
        ["8:00 AM", "1:00 PM", "8:00 PM"],   # Fri
        ["9:00 AM", "2:00 PM", "10:00 PM"],  # Sat
        ["11:00 AM", "4:00 PM", "8:00 PM"],  # Sun
    ]
    yt_times = [
        ["2:00 PM", "8:00 PM"],  # Mon
        ["2:00 PM", "9:00 PM"],  # Tue
        ["3:00 PM", "9:00 PM"],  # Wed
        ["2:00 PM", "8:00 PM"],  # Thu
        ["2:00 PM", "6:00 PM"],  # Fri
        ["9:00 AM", "3:00 PM"],  # Sat
        ["9:00 AM", "3:00 PM"],  # Sun
    ]
    if platform == "youtube":
        times = yt_times[weekday % 7]
    else:
        times = tt_times[weekday % 7]
    return times[post_idx % len(times)]


def _select_hashtags(live_tags: list[str], niche: str, platform: str,
                     count: int) -> list[str]:
    """Build a balanced hashtag set from live trending tags + niche tags."""
    niche_tags = _niche_hashtags(niche, platform)
    discovery = ["#fyp", "#foryoupage", "#viral"] if platform == "tiktok" else ["#trending"]
    combined = (
        discovery[:1]
        + niche_tags[:2]
        + [t for t in live_tags[:5] if t not in niche_tags][:2]
        + niche_tags[2:4]
    )
    seen = set()
    unique = []
    for t in combined:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return unique[:count]


def _niche_hashtags(niche: str, platform: str) -> list[str]:
    """Return curated hashtag suggestions for a niche."""
    niche_map = {
        "motivation": ["#motivation", "#mindset", "#success", "#grindculture", "#inspiration"],
        "fitness": ["#fitness", "#workout", "#gym", "#fitlife", "#health", "#gains"],
        "finance": ["#finance", "#investing", "#moneytips", "#personalfinance", "#sidehustle"],
        "food": ["#foodtiktok", "#recipe", "#cooking", "#foodie", "#easyrecipe"],
        "travel": ["#travel", "#wanderlust", "#traveltiktok", "#explore", "#adventure"],
        "fashion": ["#fashion", "#ootd", "#style", "#outfitinspo", "#wiwt"],
        "beauty": ["#beauty", "#makeup", "#skincare", "#glowup", "#beautytips"],
        "gaming": ["#gaming", "#gamer", "#gameplay", "#twitch", "#pcgaming"],
        "music": ["#music", "#newmusic", "#artist", "#hiphop", "#pop"],
        "luxury": ["#luxury", "#lifestyle", "#rich", "#expensive", "#flexing"],
        "pets": ["#pets", "#dogsoftiktok", "#catsoftiktok", "#cute", "#animalsoftiktok"],
        "relationships": ["#relationships", "#dating", "#redflag", "#lovequotes", "#singlelife"],
        "study": ["#studytok", "#studywithme", "#student", "#productivity", "#college"],
        "business": ["#smallbusiness", "#entrepreneur", "#business", "#startuplife", "#ceo"],
        "general": ["#trending", "#fyp", "#viral", "#foryoupage", "#explore"],
    }
    key = niche.lower().replace("-", "").replace(" ", "")
    for k, tags in niche_map.items():
        if k in key or key in k:
            return tags
    return niche_map["general"]


_CONTENT_THEME_DB: dict[str, list[dict]] = {
    "motivation": [
        {"type": "quote-video", "concept": "Morning discipline quote with motivational music",
         "hook": "Most people fail because of this one thing...", "cta": "Save this as your daily reminder"},
        {"type": "tip-carousel", "concept": "5 habits of highly successful people",
         "hook": "Steal these 5 habits that changed my life", "cta": "Follow for daily mindset content"},
        {"type": "story-time", "concept": "A failure that led to breakthrough",
         "hook": "I lost everything at 22. Here's what happened next.", "cta": "Drop a 🔥 if this hit"},
        {"type": "b-roll-voiceover", "concept": "Early morning routine montage",
         "hook": "5 AM doesn't care about your excuses", "cta": "Comment your wake-up time"},
        {"type": "challenge", "concept": "30-day discipline challenge",
         "hook": "Do this every day for 30 days — watch what happens", "cta": "I'm in? Comment YES"},
    ],
    "fitness": [
        {"type": "workout-demo", "concept": "5-minute morning workout (no equipment)",
         "hook": "5 minutes a day is all you need to start", "cta": "Save this for tomorrow morning"},
        {"type": "transformation", "concept": "Before/after + what changed",
         "hook": "I did this for 90 days. The results shocked me.", "cta": "DM me 'plan' for my routine"},
        {"type": "nutrition-tip", "concept": "High-protein meals under $5",
         "hook": "Eat this instead of a protein bar — way better", "cta": "Follow for daily fitness tips"},
        {"type": "myth-busting", "concept": "Common gym mistake most people make",
         "hook": "Stop doing this at the gym immediately", "cta": "Tag someone who needs to see this"},
        {"type": "challenge", "concept": "7-day step challenge",
         "hook": "10,000 steps a day for 7 days — join me", "cta": "Comment if you're doing this with me"},
    ],
    "finance": [
        {"type": "tip-carousel", "concept": "3 investments everyone should have by 25",
         "hook": "Your 40-year-old self will thank you for starting this now", "cta": "Save this before you scroll"},
        {"type": "explainer", "concept": "How compound interest works (visually)",
         "hook": "$100/month becomes THIS much in 30 years", "cta": "Follow for daily money tips"},
        {"type": "income-breakdown", "concept": "How I make money from [side hustle]",
         "hook": "I made $3K last month from my phone — here's how", "cta": "Comment 'HOW' for details"},
        {"type": "myth-busting", "concept": "Biggest money myths you need to unlearn",
         "hook": "Your parents lied to you about money", "cta": "Save this and share with a friend"},
        {"type": "challenge", "concept": "No-spend challenge weekend recap",
         "hook": "I spent $0 this weekend — here's what I learned", "cta": "Try it and report back"},
    ],
    "general": [
        {"type": "value-tip", "concept": "Top 3 tools/apps in [niche]",
         "hook": "These 3 free tools changed everything for me", "cta": "Save this — you'll need it"},
        {"type": "story-time", "concept": "Biggest mistake I made (and what I learned)",
         "hook": "I wish someone told me this earlier", "cta": "Follow so you don't make the same mistake"},
        {"type": "tutorial", "concept": "How to [solve niche problem] in 60 seconds",
         "hook": "If you struggle with [problem], watch this", "cta": "Comment if this helped"},
        {"type": "trend-reaction", "concept": "My take on the latest trend in the niche",
         "hook": "Everyone is talking about this — here's the truth", "cta": "Drop your opinion below"},
        {"type": "day-in-life", "concept": "Day in the life as a [niche] creator",
         "hook": "What my day actually looks like (no filter)", "cta": "Follow for more real content"},
    ],
}


def _content_themes_for_niche(niche: str) -> list[dict]:
    """Return content themes for a niche, falling back to general."""
    key = niche.lower()
    for k in _CONTENT_THEME_DB:
        if k in key or key in k:
            return _CONTENT_THEME_DB[k]
    return _CONTENT_THEME_DB["general"]


def _idea_templates(niche: str, trending_themes: list[str]) -> list[dict]:
    """Generate actionable content ideas combining niche + trending themes."""
    themes = _content_themes_for_niche(niche)
    ideas = []
    for i, theme in enumerate(themes):
        trend_overlay = trending_themes[i % len(trending_themes)] if trending_themes else ""
        ideas.append({
            "id": i + 1,
            "format": theme["type"],
            "concept": theme["concept"],
            "hook": theme["hook"],
            "trending_angle": f"Tie into '{trend_overlay}' trend" if trend_overlay else "",
            "cta": theme["cta"],
            "effort": _effort_estimate(theme["type"]),
            "viral_potential": _viral_estimate(theme["type"]),
        })
    # Fill remaining with trend-driven ideas
    for j, trend in enumerate(trending_themes):
        ideas.append({
            "id": len(themes) + j + 1,
            "format": "trend-stitch",
            "concept": f"React to or build on '{trend}' trend in your niche",
            "hook": f"Everyone's talking about {trend} — here's my [niche] take",
            "trending_angle": f"Trend: {trend}",
            "cta": "Comment your thoughts",
            "effort": "low",
            "viral_potential": "high",
        })
    return ideas


def _effort_estimate(content_type: str) -> str:
    high = {"workout-demo", "tutorial", "income-breakdown", "day-in-life"}
    low = {"quote-video", "b-roll-voiceover", "trend-stitch", "challenge"}
    if content_type in high:
        return "high"
    if content_type in low:
        return "low"
    return "medium"


def _viral_estimate(content_type: str) -> str:
    high = {"story-time", "myth-busting", "transformation", "challenge", "trend-stitch"}
    medium = {"tip-carousel", "tutorial", "explainer"}
    if content_type in high:
        return "high"
    if content_type in medium:
        return "medium"
    return "standard"
