"""Account optimization engine — posting schedules, hashtag strategy, content calendar."""

import json
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict


# ---------------------------------------------------------------------------
# Platform-specific best-practice data (research-backed defaults)
# ---------------------------------------------------------------------------

PLATFORM_BEST_TIMES = {
    "tiktok": {
        "monday":    [6, 10, 22],
        "tuesday":   [2, 4, 9],
        "wednesday": [7, 8, 11],
        "thursday":  [9, 12, 19],
        "friday":    [5, 13, 15],
        "saturday":  [11, 19, 20],
        "sunday":    [7, 8, 16],
        "notes": "TikTok peaks during commute hours (7-9am), lunch (12-1pm), and evenings (7-10pm) in the audience's local timezone.",
    },
    "youtube": {
        "monday":    [14, 15, 16],
        "tuesday":   [14, 15, 16],
        "wednesday": [14, 15, 16],
        "thursday":  [14, 15, 16],
        "friday":    [14, 15, 16],
        "saturday":  [9, 10, 11],
        "sunday":    [9, 10, 11],
        "notes": "YouTube performs best when published 2-3pm on weekdays (indexes in time for evening traffic). Weekends favor morning publishing.",
    },
    "instagram": {
        "monday":    [6, 11, 19],
        "tuesday":   [7, 10, 15],
        "wednesday": [6, 8, 22],
        "thursday":  [7, 10, 21],
        "friday":    [8, 11, 13],
        "saturday":  [8, 10, 13],
        "sunday":    [8, 9, 21],
        "notes": "Instagram Reels follow TikTok timing. Stories perform well during morning routines and post-dinner browsing.",
    },
    "twitter": {
        "monday":    [8, 10, 12],
        "tuesday":   [8, 10, 12],
        "wednesday": [8, 10, 12],
        "thursday":  [8, 10, 12],
        "friday":    [8, 10, 12],
        "saturday":  [9, 10, 11],
        "sunday":    [9, 10, 11],
        "notes": "Twitter peaks during work hours. B2B content Tue-Thu 8-10am. Entertainment content Thu-Fri evenings.",
    },
    "facebook": {
        "monday":    [9, 13, 15],
        "tuesday":   [9, 13, 15],
        "wednesday": [9, 13, 15],
        "thursday":  [9, 13, 15],
        "friday":    [9, 13, 14],
        "saturday":  [12, 13, 14],
        "sunday":    [12, 13, 14],
        "notes": "Facebook favors mid-morning/early afternoon. Weekend peaks 12-1pm.",
    },
}

HASHTAG_TIERS = {
    "mega":   {"min_posts": 500_000_000, "label": "Mega (>500M)", "strategy": "Brand awareness; low discoverability"},
    "large":  {"min_posts": 5_000_000,   "label": "Large (5M-500M)", "strategy": "Wide reach; competitive"},
    "medium": {"min_posts": 500_000,     "label": "Medium (500K-5M)", "strategy": "Best balance of reach and ranking"},
    "small":  {"min_posts": 50_000,      "label": "Small (50K-500K)", "strategy": "High ranking potential; niche audience"},
    "micro":  {"min_posts": 0,           "label": "Micro (<50K)", "strategy": "Dominate the niche; community-focused"},
}

CONTENT_TYPES = {
    "educational":  {"hook": "Did you know...", "cta": "Save this for later!", "ideal_length_s": 45, "frequency": "3x/week"},
    "entertainment":{"hook": "You won't believe...", "cta": "Follow for more!", "ideal_length_s": 20, "frequency": "daily"},
    "tutorial":     {"hook": "How to [result] in [time]", "cta": "Try this and comment how it went", "ideal_length_s": 60, "frequency": "2x/week"},
    "trending":     {"hook": "[trending sound/challenge]", "cta": "Tag someone who needs to see this", "ideal_length_s": 15, "frequency": "as trends appear"},
    "behind_scenes":{"hook": "POV: [scenario]", "cta": "Follow for the full story", "ideal_length_s": 30, "frequency": "2x/week"},
    "testimonial":  {"hook": "[transformation] before/after", "cta": "DM me [keyword] for more info", "ideal_length_s": 30, "frequency": "1x/week"},
    "ugc":          {"hook": "Our community said...", "cta": "Share yours in comments!", "ideal_length_s": 25, "frequency": "1x/week"},
}

NICHE_HASHTAG_SETS: dict[str, list[str]] = {
    "fitness": [
        "#fitness", "#workout", "#gym", "#fitnessmotivation", "#fit",
        "#health", "#bodybuilding", "#training", "#personaltrainer", "#weightloss",
        "#muscle", "#cardio", "#fitlife", "#healthy", "#exercise",
    ],
    "food": [
        "#food", "#foodie", "#cooking", "#recipe", "#homecooking",
        "#foodphotography", "#instafood", "#foodlover", "#delicious", "#yummy",
        "#healthyfood", "#foodblogger", "#mealprep", "#dinner", "#lunch",
    ],
    "fashion": [
        "#fashion", "#style", "#ootd", "#outfit", "#fashionblogger",
        "#streetstyle", "#trend", "#clothing", "#styleinspiration", "#fashionstyle",
        "#outfitoftheday", "#fashionista", "#chic", "#aesthetic", "#grwm",
    ],
    "finance": [
        "#finance", "#money", "#investing", "#personalfinance", "#financetips",
        "#wealthbuilding", "#stockmarket", "#passiveincome", "#financialfreedom", "#entrepreneur",
        "#sidehustle", "#makemoney", "#crypto", "#budgeting", "#richlife",
    ],
    "beauty": [
        "#beauty", "#makeup", "#skincare", "#cosmetics", "#beautytips",
        "#makeuptutorial", "#glam", "#skincareroutine", "#grwm", "#makeuplover",
        "#foundation", "#eyeshadow", "#lipstick", "#beautyinfluencer", "#selfcare",
    ],
    "travel": [
        "#travel", "#wanderlust", "#travelgram", "#travelblogger", "#travelphotography",
        "#explore", "#adventure", "#vacation", "#trip", "#world",
        "#travelvlog", "#backpacking", "#nature", "#tourism", "#bucketlist",
    ],
    "gaming": [
        "#gaming", "#gamer", "#games", "#videogames", "#twitch",
        "#gamingcommunity", "#ps5", "#xbox", "#pcgaming", "#streamer",
        "#esports", "#gamingsetup", "#letsplay", "#retrogaming", "#mobile",
    ],
    "business": [
        "#business", "#entrepreneur", "#startup", "#marketing", "#success",
        "#motivation", "#businesstips", "#digitalmarketing", "#branding", "#leadership",
        "#hustle", "#CEO", "#smallbusiness", "#growthmindset", "#networking",
    ],
    "pets": [
        "#pets", "#dogs", "#cats", "#dogoftheday", "#catoftheday",
        "#dogsofinstagram", "#catsofinstagram", "#petlover", "#puppylove", "#cute",
        "#animallover", "#petsofinstagram", "#doglife", "#kitten", "#puppy",
    ],
    "lifestyle": [
        "#lifestyle", "#life", "#motivation", "#inspiration", "#happiness",
        "#mindset", "#positivity", "#wellness", "#selfcare", "#mindfulness",
        "#livingmybestlife", "#daily", "#morningroutine", "#productivity", "#goals",
    ],
}


# ---------------------------------------------------------------------------
# Core optimization functions
# ---------------------------------------------------------------------------

def generate_posting_schedule(
    platform: str,
    timezone: str = "EST",
    posts_per_week: int = 7,
    start_date: Optional[str] = None,
) -> list[dict]:
    """
    Generate an optimized posting schedule for a platform.
    Returns a list of recommended post slots for the next 7 days.
    """
    platform_lower = platform.lower()
    if platform_lower not in PLATFORM_BEST_TIMES:
        platform_lower = "tiktok"

    times_data = PLATFORM_BEST_TIMES[platform_lower]
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    base_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.utcnow()
    # Align to next Monday
    days_ahead = (7 - base_date.weekday()) % 7
    week_start = base_date + timedelta(days=days_ahead)

    slots = []
    for i, day in enumerate(days):
        best_hours = times_data.get(day, [12, 18])
        date = week_start + timedelta(days=i)
        for hour in best_hours[:2]:
            slots.append({
                "date": date.strftime("%Y-%m-%d"),
                "day": day.capitalize(),
                "hour_utc": hour,
                "time_display": f"{hour:02d}:00 UTC ({_utc_to_tz(hour, timezone)})",
                "platform": platform,
                "slot_quality": "prime" if hour in best_hours[:1] else "good",
            })

    # Trim to requested posts_per_week
    prime_slots = [s for s in slots if s["slot_quality"] == "prime"]
    good_slots  = [s for s in slots if s["slot_quality"] == "good"]
    schedule = (prime_slots + good_slots)[:posts_per_week]
    schedule.sort(key=lambda x: (x["date"], x["hour_utc"]))
    return schedule


def _utc_to_tz(hour_utc: int, tz: str) -> str:
    offsets = {"EST": -5, "CST": -6, "MST": -7, "PST": -8,
               "GMT": 0, "CET": 1, "IST": 5, "JST": 9, "AEST": 10}
    offset = offsets.get(tz.upper(), 0)
    local = (hour_utc + offset) % 24
    suffix = "AM" if local < 12 else "PM"
    display = local if local <= 12 else local - 12
    display = 12 if display == 0 else display
    return f"{display}:00 {suffix} {tz.upper()}"


def build_hashtag_strategy(
    niche: str,
    platform: str = "tiktok",
    trending_hashtags: Optional[list[dict]] = None,
    count: int = 25,
) -> dict:
    """
    Build a tiered hashtag strategy for a niche, optionally blending in live trending data.
    Returns sets of hashtags by tier with usage instructions.
    """
    niche_lower = niche.lower()
    base_tags = NICHE_HASHTAG_SETS.get(niche_lower, [])

    # Supplement with trending hashtags if provided
    trending_tags = []
    if trending_hashtags:
        for t in trending_hashtags[:15]:
            tag = t.get("hashtag", "")
            if tag and tag not in base_tags:
                trending_tags.append(tag)

    all_tags = list(dict.fromkeys(base_tags + trending_tags))

    # Tier assignment heuristic (without live API, approximate by tag popularity assumption)
    # Real implementation would call hashtag info API
    mega_tags  = [t for t in all_tags if len(t) <= 7][:3]   # short = usually huge
    large_tags = all_tags[3:8]
    medium_tags = all_tags[8:16]
    small_tags  = all_tags[16:22]
    micro_tags  = trending_tags[:5]   # new trending = potentially micro

    limits = {"tiktok": 5, "instagram": 30, "youtube": 15, "twitter": 3, "facebook": 5}
    tag_limit = limits.get(platform.lower(), 10)

    combo = (mega_tags[:1] + large_tags[:2] + medium_tags[:3] + small_tags[:3] + micro_tags[:2])[:tag_limit]

    return {
        "niche": niche,
        "platform": platform,
        "total_available_tags": len(all_tags),
        "recommended_combo": combo,
        "recommended_combo_str": " ".join(combo),
        "tiers": {
            "mega":   {"tags": mega_tags,   "strategy": HASHTAG_TIERS["mega"]["strategy"]},
            "large":  {"tags": large_tags,  "strategy": HASHTAG_TIERS["large"]["strategy"]},
            "medium": {"tags": medium_tags, "strategy": HASHTAG_TIERS["medium"]["strategy"]},
            "small":  {"tags": small_tags,  "strategy": HASHTAG_TIERS["small"]["strategy"]},
            "micro":  {"tags": micro_tags,  "strategy": HASHTAG_TIERS["micro"]["strategy"]},
        },
        "platform_limit": tag_limit,
        "pro_tips": [
            f"Use {tag_limit} hashtags max on {platform} — quality over quantity.",
            "Rotate hashtag sets every 5-7 posts to avoid shadow-banning signals.",
            "Place hashtags in the caption (TikTok/Instagram) or pinned comment (YouTube).",
            "Always include 1-2 niche-specific tags + 1-2 trending tags per post.",
            "Track which hashtag combinations drive the most profile visits.",
        ],
    }


def generate_content_calendar(
    niche: str,
    platform: str = "tiktok",
    weeks: int = 4,
    posts_per_week: int = 7,
    trending_topics: Optional[list[str]] = None,
) -> list[dict]:
    """
    Generate a content calendar mixing content types optimally.
    Returns a list of post ideas with hooks, CTAs, and hashtags.
    """
    content_type_rotation = [
        "entertainment", "educational", "entertainment",
        "trending", "tutorial", "behind_scenes", "testimonial",
    ]

    calendar = []
    base_date = datetime.utcnow()
    days_ahead = (7 - base_date.weekday()) % 7
    week_start = base_date + timedelta(days=days_ahead if days_ahead > 0 else 7)

    niche_tags = NICHE_HASHTAG_SETS.get(niche.lower(), ["#content", "#creator"])

    day_counter = 0
    for week in range(weeks):
        week_start_actual = week_start + timedelta(weeks=week)
        posts_this_week = [i % len(content_type_rotation) for i in range(posts_per_week)]

        for post_idx in range(posts_per_week):
            content_key = content_type_rotation[posts_this_week[post_idx]]
            ct = CONTENT_TYPES[content_key]
            post_date = week_start_actual + timedelta(days=post_idx)

            # Pick relevant trending topic if available
            trending_topic = ""
            if trending_topics:
                trending_topic = trending_topics[day_counter % len(trending_topics)]

            hook = ct["hook"]
            if trending_topic and content_key == "trending":
                hook = f"This {trending_topic} trend is taking over"

            calendar.append({
                "week": week + 1,
                "post_number": day_counter + 1,
                "date": post_date.strftime("%Y-%m-%d"),
                "day": post_date.strftime("%A"),
                "platform": platform,
                "content_type": content_key,
                "hook": hook,
                "cta": ct["cta"],
                "ideal_length": f"{ct['ideal_length_s']}s",
                "frequency_note": ct["frequency"],
                "suggested_hashtags": (niche_tags[:3] + [f"#{content_key}"])[:5],
                "trending_tie_in": trending_topic,
                "status": "planned",
            })
            day_counter += 1

    return calendar


def audit_account(account_data: dict) -> dict:
    """
    Audit a social media account and return optimization recommendations.
    account_data should contain: platform, username, follower_count,
    avg_views, avg_likes, avg_comments, posting_frequency, niche, bio.
    """
    platform = account_data.get("platform", "unknown")
    followers = account_data.get("follower_count", 0)
    avg_views = account_data.get("avg_views", 0)
    avg_likes = account_data.get("avg_likes", 0)
    avg_comments = account_data.get("avg_comments", 0)
    posting_freq = account_data.get("posting_frequency_per_week", 0)
    niche = account_data.get("niche", "general")
    bio = account_data.get("bio", "")

    # Engagement rate
    if avg_views > 0:
        engagement_rate = (avg_likes + avg_comments) / avg_views * 100
    elif followers > 0:
        engagement_rate = (avg_likes + avg_comments) / followers * 100
    else:
        engagement_rate = 0

    # Benchmarks
    eng_benchmarks = {
        "tiktok": {"poor": 1, "average": 5, "good": 10, "viral": 20},
        "instagram": {"poor": 1, "average": 3, "good": 6, "viral": 10},
        "youtube": {"poor": 0.5, "average": 2, "good": 5, "viral": 10},
        "twitter": {"poor": 0.5, "average": 1, "good": 3, "viral": 6},
    }
    bench = eng_benchmarks.get(platform.lower(), {"poor": 1, "average": 3, "good": 7, "viral": 15})

    if engagement_rate >= bench["viral"]:
        eng_grade = "viral"
    elif engagement_rate >= bench["good"]:
        eng_grade = "good"
    elif engagement_rate >= bench["average"]:
        eng_grade = "average"
    else:
        eng_grade = "poor"

    # Recommendations
    recs = []

    if posting_freq < 3:
        recs.append({
            "priority": "high",
            "category": "consistency",
            "issue": f"Only posting {posting_freq}x/week",
            "fix": "Increase to 5-7x/week. Consistency is the #1 growth driver on all platforms.",
        })
    if posting_freq > 14:
        recs.append({
            "priority": "medium",
            "category": "consistency",
            "issue": "Posting too frequently (2+/day) may saturate your audience",
            "fix": "Test 1/day cadence for 30 days and measure engagement change.",
        })
    if len(bio) < 50:
        recs.append({
            "priority": "high",
            "category": "profile",
            "issue": "Bio is too short or missing",
            "fix": "Add: (1) who you help, (2) what you do, (3) CTA (follow/link). Under 150 chars.",
        })
    if engagement_rate < bench["average"]:
        recs.append({
            "priority": "high",
            "category": "engagement",
            "issue": f"Engagement rate {engagement_rate:.1f}% is below average ({bench['average']}%) for {platform}",
            "fix": "End every video with a question. Reply to ALL comments in the first hour. Use strong hooks in first 3 seconds.",
        })
    if followers > 0 and avg_views < followers * 0.05:
        recs.append({
            "priority": "high",
            "category": "reach",
            "issue": "Views significantly lower than follower count — algorithm isn't pushing your content",
            "fix": "Improve watch-through rate: cut intros, front-load value, use pattern interrupts every 3-5 seconds.",
        })

    recs.append({
        "priority": "medium",
        "category": "seo",
        "issue": "General",
        "fix": f"Use your main keyword ({niche}) in the first 3 words of every caption/title.",
    })
    recs.append({
        "priority": "medium",
        "category": "thumbnails",
        "issue": "General",
        "fix": "Test 3 thumbnail variations with split test tools. High-contrast, face + emotion + text overlay wins.",
    })
    recs.append({
        "priority": "low",
        "category": "cross_posting",
        "issue": "General",
        "fix": "Repurpose each video to 3 platforms: TikTok → Reels → YouTube Shorts. 3x distribution, 1x effort.",
    })

    return {
        "account": account_data.get("username", "unknown"),
        "platform": platform,
        "niche": niche,
        "follower_count": followers,
        "engagement_rate_pct": round(engagement_rate, 2),
        "engagement_grade": eng_grade,
        "engagement_benchmark": bench,
        "posting_frequency_per_week": posting_freq,
        "recommendations": sorted(recs, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["priority"]]),
        "score": _calculate_account_score(engagement_rate, bench, posting_freq, len(bio), followers),
        "audited_at": datetime.utcnow().isoformat(),
    }


def _calculate_account_score(eng_rate: float, bench: dict, freq: int, bio_len: int, followers: int) -> dict:
    scores = {}
    # Engagement score 0-30
    if eng_rate >= bench["viral"]:
        scores["engagement"] = 30
    elif eng_rate >= bench["good"]:
        scores["engagement"] = 22
    elif eng_rate >= bench["average"]:
        scores["engagement"] = 15
    else:
        scores["engagement"] = max(0, int(eng_rate / bench["average"] * 15))

    # Consistency score 0-25
    if 5 <= freq <= 10:
        scores["consistency"] = 25
    elif 3 <= freq <= 14:
        scores["consistency"] = 15
    elif freq > 0:
        scores["consistency"] = 5
    else:
        scores["consistency"] = 0

    # Profile score 0-20
    if bio_len >= 100:
        scores["profile"] = 20
    elif bio_len >= 50:
        scores["profile"] = 12
    else:
        scores["profile"] = 4

    # Growth score 0-25
    if followers >= 100_000:
        scores["growth"] = 25
    elif followers >= 10_000:
        scores["growth"] = 18
    elif followers >= 1_000:
        scores["growth"] = 10
    else:
        scores["growth"] = 5

    total = sum(scores.values())
    if total >= 85:
        grade = "A"
    elif total >= 70:
        grade = "B"
    elif total >= 55:
        grade = "C"
    elif total >= 40:
        grade = "D"
    else:
        grade = "F"

    return {"breakdown": scores, "total": total, "max": 100, "grade": grade}


def optimize_bio(niche: str, platform: str, value_prop: str = "", cta: str = "") -> dict:
    """Generate optimized bio templates for a niche and platform."""
    templates = {
        "tiktok": [
            f"I help {niche} people [result] without [pain point] ✨ | New videos daily | Follow for more {niche} tips 👇",
            f"[Your name] | {niche.capitalize()} content creator | Sharing what actually works 🔥 | {cta or 'Follow for daily tips'}",
            f"📍 [Location] | {niche.capitalize()} tips that go viral | {value_prop or 'Teaching what I know'} | {cta or '↓ Latest video ↓'}",
        ],
        "youtube": [
            f"[Channel Name] — {niche.capitalize()} tutorials, tips, and strategies | New videos every [day] | {value_prop or 'Helping you master ' + niche}",
            f"Hi! I'm [Name] and I create {niche} content to help you [result]. Subscribe for weekly uploads → {cta or 'link below'}",
        ],
        "instagram": [
            f"✨ {niche.capitalize()} creator | {value_prop or 'Sharing daily ' + niche + ' tips'}\n📌 New posts daily\n👇 {cta or 'Check my latest reel'}",
            f"[Name] | {niche.capitalize()} 🌟\n• [Credential 1]\n• [Credential 2]\n• {value_prop or niche + ' enthusiast'}\n⬇️ {cta or 'Follow + turn on notifications'}",
        ],
    }
    platform_lower = platform.lower()
    return {
        "platform": platform,
        "niche": niche,
        "templates": templates.get(platform_lower, templates.get("tiktok", [])),
        "tips": [
            "Include a clear value prop (what you do + who you help) in the first line.",
            "Add a CTA — tell people exactly what to do next.",
            "Use keywords your niche searches for (improves discoverability).",
            "Emojis as visual bullets break up text and improve readability.",
            f"Keep bio under {150 if platform_lower == 'tiktok' else 160} characters for full display without truncation.",
        ],
    }
