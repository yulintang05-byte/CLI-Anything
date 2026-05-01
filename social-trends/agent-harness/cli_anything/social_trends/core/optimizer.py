"""Account optimization engine — bio, posting schedule, hashtags, content plans.

All advice is data-driven and platform-specific. No external API required.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional


POSTING_SCHEDULES = {
    "tiktok": {
        "best_days": ["Tuesday", "Thursday", "Friday", "Saturday"],
        "best_times_utc": ["06:00", "09:00", "12:00", "19:00", "21:00"],
        "frequency": "1–3 posts/day minimum for growth",
        "cadence_tip": "Post consistently — TikTok rewards accounts that post daily",
        "slots": [
            {"day": "Tuesday", "time": "07:00", "tz_note": "7AM local = peak morning scroll"},
            {"day": "Thursday", "time": "09:00", "tz_note": "9AM local = commute/work break"},
            {"day": "Friday", "time": "12:00", "tz_note": "Noon = lunch scroll peak"},
            {"day": "Saturday", "time": "11:00", "tz_note": "Weekend leisure browsing"},
            {"day": "Sunday", "time": "19:00", "tz_note": "Sunday evening = highest avg views"},
        ],
    },
    "youtube": {
        "best_days": ["Wednesday", "Thursday", "Friday", "Saturday"],
        "best_times_utc": ["14:00", "15:00", "16:00", "17:00"],
        "frequency": "1 long-form/week + 3–5 Shorts/week",
        "cadence_tip": "Consistency beats frequency on YouTube — same day every week builds habit",
        "slots": [
            {"day": "Wednesday", "time": "14:00", "tz_note": "2PM EST = highest mid-week views"},
            {"day": "Friday", "time": "15:00", "tz_note": "3PM EST = pre-weekend peak"},
            {"day": "Saturday", "time": "10:00", "tz_note": "Saturday morning = highest weekend reach"},
            {"day": "Sunday", "time": "16:00", "tz_note": "Sunday afternoon = research/learning mindset"},
        ],
    },
    "instagram": {
        "best_days": ["Monday", "Tuesday", "Wednesday", "Friday"],
        "best_times_utc": ["08:00", "11:00", "13:00", "17:00", "19:00"],
        "frequency": "1 Reel/day + 3–5 Stories/day",
        "cadence_tip": "Reels get 3x reach of static posts — prioritize video content",
        "slots": [
            {"day": "Monday", "time": "08:00", "tz_note": "Monday morning = fresh week motivation"},
            {"day": "Tuesday", "time": "11:00", "tz_note": "Tuesday mid-morning = peak engagement"},
            {"day": "Wednesday", "time": "19:00", "tz_note": "Wednesday evening = most active period"},
            {"day": "Friday", "time": "17:00", "tz_note": "Friday after work = leisure scrolling"},
        ],
    },
}

BIO_TEMPLATES = {
    "fitness": {
        "tiktok": [
            "💪 {niche} coach | Helping you {transformation} | {cta} 👇",
            "🔥 Lost {stat} lbs | Now teaching you how | Free workout 👇",
            "{credential} fitness creator | {posts_per_week}x/week workouts | Join {count}+ in {community} 👇",
        ],
        "youtube": [
            "{niche} Fitness — New videos every {day} | {subscriber_count}+ transformations | Subscribe 👇",
            "Real fitness advice, no BS | {credential} | Weekly workouts + meal plans",
        ],
        "instagram": [
            "💪 {niche} | {credential}\n📩 Coaching DMs open\n👇 Free training plan",
            "Helping {audience} get {result} in {timeframe}\n🏆 {credential}\n📲 DM 'READY' to start",
        ],
    },
    "finance": {
        "tiktok": [
            "💰 Making money work for you | {credential} | Free {lead_magnet} 👇",
            "Went from {before} → {after} | Teaching financial freedom | Start here 👇",
            "💸 {niche} finance tips daily | {years}yr experience | Free guide 👇",
        ],
        "youtube": [
            "Financial freedom for {audience} | Weekly money tips | Subscribe for {value_prop}",
            "{credential} | {niche} investing simplified | New video every {day}",
        ],
    },
    "general": {
        "tiktok": [
            "🔥 {niche} content daily | DM for collabs | {cta} 👇",
            "{value_prop} for {audience} | {posts_per_week}x/week | {cta} 👇",
            "📲 {niche} | Helping {audience} {goal} | {cta} 👇",
        ],
        "youtube": [
            "{niche} | New videos {frequency} | Subscribe for {value_prop}",
            "Helping {audience} {goal} | {credential} | Subscribe 👇",
        ],
        "instagram": [
            "📸 {niche} creator\n🌟 {value_prop}\n👇 {cta}",
            "{niche} | {credential}\n📩 Collabs: {email_placeholder}\n👇 Latest content",
        ],
    },
}

CONTENT_PLAN_TEMPLATES = {
    "fitness": [
        {"day": 1, "format": "Transformation reveal", "hook": "I lost X lbs in Y days — here's exactly how", "platform": "both"},
        {"day": 2, "format": "Quick workout", "hook": "5-min workout that burns more than an hour at the gym", "platform": "tiktok"},
        {"day": 3, "format": "Meal prep", "hook": "What I eat in a day to stay lean (under $50)", "platform": "both"},
        {"day": 4, "format": "Myth busting", "hook": "Stop doing [common mistake] — it's killing your progress", "platform": "youtube"},
        {"day": 5, "format": "Day in my life", "hook": "How I stay consistent while working full time", "platform": "tiktok"},
        {"day": 6, "format": "Q&A", "hook": "Answering your biggest fitness questions", "platform": "both"},
        {"day": 7, "format": "Weekly challenge", "hook": "7-day challenge that will change your body", "platform": "both"},
    ],
    "finance": [
        {"day": 1, "format": "Money mistake", "hook": "The #1 mistake that kept me broke (avoid this)", "platform": "both"},
        {"day": 2, "format": "Income reveal", "hook": "How I made $X this month (full breakdown)", "platform": "tiktok"},
        {"day": 3, "format": "Budget tutorial", "hook": "This budget method changed my life — try it today", "platform": "both"},
        {"day": 4, "format": "Investing 101", "hook": "If I had to start investing with $100 — here's what I'd do", "platform": "youtube"},
        {"day": 5, "format": "Side hustle", "hook": "The side hustle nobody is talking about in 2025", "platform": "tiktok"},
        {"day": 6, "format": "Savings hack", "hook": "Saved $10k in 6 months — my exact system", "platform": "both"},
        {"day": 7, "format": "Weekly roundup", "hook": "This week's best money moves (recapping the week)", "platform": "youtube"},
    ],
    "general": [
        {"day": 1, "format": "Value bomb", "hook": "The [secret/hack/method] nobody tells you about [topic]", "platform": "both"},
        {"day": 2, "format": "Story time", "hook": "How I went from [before] to [after] (my full story)", "platform": "tiktok"},
        {"day": 3, "format": "Tutorial", "hook": "Step-by-step: how to [achieve goal] in [timeframe]", "platform": "both"},
        {"day": 4, "format": "Long-form", "hook": "Everything you need to know about [topic] (complete guide)", "platform": "youtube"},
        {"day": 5, "format": "Trend hijack", "hook": "[Trending topic] — here's my take as a [niche creator]", "platform": "tiktok"},
        {"day": 6, "format": "Collab/duet", "hook": "Reacting to the most [viral] [topic] content this week", "platform": "both"},
        {"day": 7, "format": "Community CTA", "hook": "Tell me your biggest [niche] struggle (real talk)", "platform": "both"},
    ],
}

PROFILE_OPTIMIZATION_CHECKLIST = {
    "tiktok": [
        {"item": "Profile photo", "status_key": "profile_photo", "tip": "Use a clear face photo or bold logo — avoid generic stock images"},
        {"item": "Username", "status_key": "username", "tip": "Keep under 20 chars, include niche keyword, no underscores"},
        {"item": "Bio (150 chars)", "status_key": "bio", "tip": "Hook → Value prop → CTA with emoji. Include a keyword for SEO."},
        {"item": "Link in bio", "status_key": "link", "tip": "Use Linktree or Beacons.ai — point to your #1 offer or email list"},
        {"item": "Pinned videos (3)", "status_key": "pinned", "tip": "Pin: best performing, most shareable, and intro/about video"},
        {"item": "Content niche", "status_key": "niche", "tip": "Pick ONE niche for first 90 days — mixed content confuses the algorithm"},
        {"item": "Consistent posting", "status_key": "cadence", "tip": "Post minimum 1x/day for first 30 days to train the algorithm"},
        {"item": "Engagement", "status_key": "engagement", "tip": "Reply to every comment for first 24hrs — boosts distribution 2–3x"},
        {"item": "Hashtag strategy", "status_key": "hashtags", "tip": "3–5 tags max: 1 broad + 2 niche + 1 trending. Never use #fyp alone."},
        {"item": "Sound strategy", "status_key": "sounds", "tip": "Use trending sounds under 72hrs old for maximum algorithm boost"},
    ],
    "youtube": [
        {"item": "Channel art", "status_key": "channel_art", "tip": "2560x1440px banner — show face, niche, and upload schedule"},
        {"item": "Channel icon", "status_key": "icon", "tip": "Square face or logo, 800x800px minimum"},
        {"item": "Channel description", "status_key": "description", "tip": "First 2 lines show in search — lead with your value prop and keywords"},
        {"item": "Channel trailer", "status_key": "trailer", "tip": "60-90s trailer: hook (5s) → problem you solve → why you → CTA"},
        {"item": "Playlists", "status_key": "playlists", "tip": "Group content into 3–5 topic playlists — increases session time 40%"},
        {"item": "Featured channels", "status_key": "featured", "tip": "Feature 3–5 complementary channels for community signals"},
        {"item": "About page keywords", "status_key": "keywords", "tip": "Include 3–5 search keywords naturally in the About section"},
        {"item": "Thumbnail style", "status_key": "thumbnails", "tip": "Consistent color palette + font + face = brand recognition"},
        {"item": "Upload schedule", "status_key": "schedule", "tip": "Same day/time weekly — subscribers build viewing habits"},
        {"item": "End screens", "status_key": "end_screens", "tip": "Every video needs end screen with subscribe + suggested video CTA"},
    ],
}


def get_posting_schedule(platform: str, timezone: str = "EST") -> dict:
    platform = platform.lower()
    schedule = POSTING_SCHEDULES.get(platform, POSTING_SCHEDULES["tiktok"])
    return {
        "platform": platform,
        "timezone_note": f"Times shown in UTC — convert to {timezone} for your audience",
        "frequency": schedule["frequency"],
        "cadence_tip": schedule["cadence_tip"],
        "best_days": schedule["best_days"],
        "best_times_utc": schedule["best_times_utc"],
        "recommended_slots": schedule["slots"],
        "pro_tip": "A/B test your posting times for 2 weeks and double down on what works for YOUR audience.",
    }


def get_bio_templates(platform: str, niche: str) -> dict:
    platform = platform.lower()
    niche_key = "general"
    for k in BIO_TEMPLATES:
        if k in niche.lower():
            niche_key = k
            break

    templates = BIO_TEMPLATES.get(niche_key, BIO_TEMPLATES["general"])
    platform_templates = templates.get(platform, templates.get("tiktok", []))

    return {
        "platform": platform,
        "niche": niche,
        "templates": platform_templates,
        "placeholders": {
            "{niche}": f"Your {niche} specialty",
            "{transformation}": "The result you deliver",
            "{cta}": "Free guide / link in bio / DM me",
            "{credential}": "Your proof/experience",
            "{audience}": "Who you help",
            "{lead_magnet}": "Free resource you offer",
        },
        "bio_rules": [
            "Lead with WHO you help or WHAT result you deliver — not your name",
            "Use 1–2 relevant emojis maximum on TikTok/Instagram",
            "Always end with a clear CTA (call to action)",
            "Include a searchable keyword for discovery",
            "Keep it under the character limit: TikTok 80 chars, Instagram 150, YouTube 1000",
        ],
    }


def get_hashtag_recommendations(niche: str, platform: str, count: int = 15) -> dict:
    from cli_anything.social_trends.utils import tiktok_backend as tt
    from cli_anything.social_trends.utils import youtube_backend as yt

    platform = platform.lower()
    if platform == "tiktok":
        data = tt.fetch_trending_hashtags(niche=niche, limit=count)
        tags = data["items"]
    else:
        data = yt.fetch_trending_hashtags(niche=niche, limit=count)
        tags = data["items"]

    # Categorize by competition
    low = [t for t in tags if t.get("competition") in ("low",)]
    medium = [t for t in tags if t.get("competition") in ("medium",)]
    high = [t for t in tags if t.get("competition") in ("high", "very_high", "extreme")]

    return {
        "platform": platform,
        "niche": niche,
        "total": len(tags),
        "strategy": {
            "low_competition": [t["tag"] for t in low[:3]],
            "medium_competition": [t["tag"] for t in medium[:3]],
            "high_competition": [t["tag"] for t in high[:3]],
            "recommended_mix": f"{', '.join([t['tag'] for t in low[:1]])} + {', '.join([t['tag'] for t in medium[:2]])} + {', '.join([t['tag'] for t in high[:2]])}",
        },
        "all_tags": tags,
        "rules": [
            "TikTok: Use 3–5 tags. More is NOT better.",
            "YouTube: Use 3 hashtags in description — first 3 appear above title",
            "Instagram: 3–5 highly relevant tags outperform 30 generic ones",
            "Rotate your hashtag sets to avoid shadowban patterns",
            "Replace 1 tag per week with a newly trending alternative",
        ],
    }


def get_content_plan(niche: str, platform: str, days: int = 7) -> dict:
    niche_key = "general"
    for k in CONTENT_PLAN_TEMPLATES:
        if k in niche.lower():
            niche_key = k
            break

    template = CONTENT_PLAN_TEMPLATES.get(niche_key, CONTENT_PLAN_TEMPLATES["general"])
    plan = [d for d in template if d["day"] <= days]

    # Filter by platform if specific platform requested
    if platform.lower() not in ("all", "both"):
        plan = [
            d for d in plan
            if d["platform"] in (platform.lower(), "both")
        ]

    return {
        "platform": platform,
        "niche": niche,
        "days": days,
        "content_plan": plan,
        "viral_hooks": [
            "I tried [trending thing] for 30 days — here's what happened",
            "Nobody is talking about this [niche] secret",
            "Stop doing [common mistake] — do THIS instead",
            "How I went from [relatable before] to [aspirational after]",
            "The [niche] hack that got me [result] in [timeframe]",
            "POV: You finally found the [solution] you've been looking for",
            "Watch this if you want to [goal] without [common pain]",
        ],
        "pro_tips": [
            "Film in batches — create 7 days of content in 2 hours",
            "Repurpose every YouTube video into 3–5 TikTok/Shorts clips",
            "First 1–3 seconds are everything — hook with movement or bold text",
            "Use pattern interrupts every 3–5 seconds to retain viewers",
            "Always end with a CTA: comment, follow, or link in bio",
        ],
    }


def get_profile_checklist(platform: str) -> dict:
    platform = platform.lower()
    checklist = PROFILE_OPTIMIZATION_CHECKLIST.get(platform, PROFILE_OPTIMIZATION_CHECKLIST["tiktok"])
    return {
        "platform": platform,
        "checklist": checklist,
        "total_items": len(checklist),
        "priority_order": [item["item"] for item in checklist],
        "impact_summary": f"Completing all {len(checklist)} items typically increases profile click-through rate by 40–60% and follow rate by 25–35%.",
    }
