"""Account optimizer — scores trends, generates hashtag sets,
posting schedules, caption templates, and optimization reports."""

import re
from datetime import datetime, timedelta
from typing import Optional


# ── Virality scoring ──────────────────────────────────────────────

def score_trend(trend: dict, platform: str = "tiktok") -> float:
    """Return a virality score 0–100 for a trend dict."""
    score = 0.0
    views = trend.get("view_count", 0) or trend.get("play_count", 0)
    clips = trend.get("publish_count", 0) or trend.get("clip_count", 0)
    likes = trend.get("like_count", 0)
    comments = trend.get("comment_count", 0)
    shares = trend.get("share_count", 0)

    # engagement score (weighted sum, log-scaled)
    import math
    engagement = (
        math.log10(max(views, 1)) * 2 +
        math.log10(max(clips, 1)) * 1.5 +
        math.log10(max(likes, 1)) * 1.2 +
        math.log10(max(comments, 1)) * 1.0 +
        math.log10(max(shares, 1)) * 1.8
    )
    # normalise to 0-100 (empirical cap at ~35 log units)
    score = min(engagement / 35.0 * 100, 100)

    # bonus for "rising" trend label
    trend_label = (trend.get("trend") or "").lower()
    if trend_label in ("rising", "breakout", "surging"):
        score = min(score * 1.25, 100)

    return round(score, 1)


def rank_trends(trends: list, platform: str = "tiktok") -> list:
    """Add a virality_score to each trend and sort descending."""
    for t in trends:
        t["virality_score"] = score_trend(t, platform)
    return sorted(trends, key=lambda x: x["virality_score"], reverse=True)


# ── Hashtag strategy ──────────────────────────────────────────────

# Best-practice hashtag counts per platform
HASHTAG_LIMITS = {
    "tiktok": {"min": 3, "max": 6, "sweet_spot": 4},
    "instagram": {"min": 5, "max": 30, "sweet_spot": 15},
    "youtube": {"min": 3, "max": 15, "sweet_spot": 7},
}

NICHE_SEED_HASHTAGS = {
    "fitness": ["#fitness", "#workout", "#gym", "#fitnessmotivation", "#health", "#bodybuilding", "#weightloss"],
    "food": ["#foodie", "#recipe", "#cooking", "#foodphotography", "#delicious", "#homecooking", "#foodlover"],
    "travel": ["#travel", "#wanderlust", "#travelgram", "#adventure", "#explore", "#vacation", "#travelblogger"],
    "fashion": ["#fashion", "#style", "#ootd", "#outfitoftheday", "#fashionista", "#streetstyle", "#clothing"],
    "beauty": ["#beauty", "#makeup", "#skincare", "#beautytips", "#glam", "#makeuptutorial", "#selfcare"],
    "finance": ["#money", "#investing", "#personalfinance", "#stockmarket", "#financetips", "#wealth", "#sidehustle"],
    "motivation": ["#motivation", "#mindset", "#success", "#inspiration", "#grind", "#hustle", "#selfimprovement"],
    "gaming": ["#gaming", "#gamer", "#videogames", "#twitch", "#esports", "#gameplay", "#gamingcommunity"],
    "tech": ["#tech", "#technology", "#ai", "#coding", "#programming", "#startup", "#innovation"],
    "comedy": ["#funny", "#comedy", "#humor", "#memes", "#laugh", "#viral", "#lol"],
    "pets": ["#pets", "#dogs", "#cats", "#dogsoftiktok", "#catsoftiktok", "#petlover", "#animals"],
    "dance": ["#dance", "#dancing", "#choreography", "#dancevideos", "#dancer", "#viral", "#tiktokdance"],
}


def build_hashtag_set(
    niche: str,
    trending_hashtags: list,
    platform: str = "tiktok",
    include_niche_seeds: bool = True,
) -> dict:
    """Build an optimal hashtag mix: niche seeds + trending + broad."""
    limits = HASHTAG_LIMITS.get(platform, {"min": 3, "max": 10, "sweet_spot": 5})
    target = limits["sweet_spot"]

    niche_seeds = NICHE_SEED_HASHTAGS.get(niche.lower(), [])
    trending_top = [t["hashtag"] for t in trending_hashtags[:20]]

    # pick top trending that overlap with niche (if any), else just top trending
    niche_words = set(re.split(r"[^a-z]+", niche.lower())) | {niche.lower()}
    niche_trending = [
        h for h in trending_top
        if any(w in h.lower() for w in niche_words)
    ]
    general_trending = [h for h in trending_top if h not in niche_trending]

    seen = set()

    def _add(tag: str) -> bool:
        if tag not in seen:
            seen.add(tag)
            result_tags.append(tag)
            return True
        return False

    result_tags = []
    # 1. must-have niche seeds (up to 2)
    if include_niche_seeds and niche_seeds:
        for s in niche_seeds[:2]:
            _add(s)
    # 2. niche-specific trending (up to 2)
    for h in niche_trending[:2]:
        _add(h)
    # 3. general trending (fill to target)
    for h in general_trending:
        if len(result_tags) >= target:
            break
        _add(h)
    # 4. top niche seeds to fill
    for s in niche_seeds:
        if len(result_tags) >= target:
            break
        _add(s)

    result_tags = result_tags[:limits["max"]]

    return {
        "hashtags": result_tags,
        "count": len(result_tags),
        "platform": platform,
        "recommendation": (
            f"Use {len(result_tags)} hashtags — mix of niche-specific and trending. "
            f"Place them at the end of caption or first comment (Instagram)."
        ),
    }


# ── Posting schedule ─────────────────────────────────────────────

PEAK_TIMES = {
    "tiktok": {
        "monday":    ["6:00-10:00", "19:00-23:00"],
        "tuesday":   ["6:00-10:00", "19:00-23:00"],
        "wednesday": ["6:00-10:00", "19:00-23:00"],
        "thursday":  ["6:00-10:00", "19:00-23:00"],
        "friday":    ["6:00-10:00", "18:00-22:00"],
        "saturday":  ["9:00-13:00", "18:00-22:00"],
        "sunday":    ["9:00-13:00", "18:00-22:00"],
    },
    "instagram": {
        "monday":    ["11:00-13:00", "19:00-21:00"],
        "tuesday":   ["9:00-11:00", "19:00-21:00"],
        "wednesday": ["11:00-13:00", "17:00-19:00"],
        "thursday":  ["11:00-13:00", "19:00-21:00"],
        "friday":    ["11:00-13:00", "17:00-19:00"],
        "saturday":  ["10:00-12:00"],
        "sunday":    ["10:00-12:00"],
    },
    "youtube": {
        "monday":    ["15:00-17:00"],
        "tuesday":   ["15:00-17:00"],
        "wednesday": ["15:00-17:00"],
        "thursday":  ["15:00-17:00"],
        "friday":    ["15:00-18:00"],
        "saturday":  ["10:00-14:00"],
        "sunday":    ["10:00-14:00"],
    },
}

OPTIMAL_FREQUENCY = {
    "tiktok":    {"posts_per_day": 2, "max_per_day": 4},
    "instagram": {"posts_per_day": 1, "max_per_day": 2},
    "youtube":   {"posts_per_day": 0.3, "max_per_day": 1},  # ~2-3/week
}


def generate_posting_schedule(
    platform: str,
    posts_per_week: int = None,
    start_date: Optional[datetime] = None,
    timezone: str = "EST",
) -> list:
    """Generate a 7-day posting schedule with optimal times."""
    if start_date is None:
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    freq = OPTIMAL_FREQUENCY.get(platform, {"posts_per_day": 1, "max_per_day": 2})
    if posts_per_week is None:
        posts_per_week = max(1, int(freq["posts_per_day"] * 7))

    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    peaks = PEAK_TIMES.get(platform, {})

    schedule = []
    posts_placed = 0
    for i, day in enumerate(days):
        if posts_placed >= posts_per_week:
            break
        date = start_date + timedelta(days=i)
        windows = peaks.get(day, ["12:00-13:00"])
        # place at most max_per_day posts on this day
        day_posts = min(int(freq["max_per_day"]), posts_per_week - posts_placed)
        for j in range(day_posts):
            window = windows[j % len(windows)]
            schedule.append({
                "date": date.strftime("%Y-%m-%d"),
                "day": day.capitalize(),
                "time_window": f"{window} {timezone}",
                "platform": platform,
                "post_number": posts_placed + 1,
            })
            posts_placed += 1

    return schedule


# ── Account optimization report ───────────────────────────────────

PROFILE_CHECKLIST = {
    "tiktok": [
        "Profile photo: clear face or brand logo, good lighting",
        "Bio: 1 keyword-rich line + CTA (e.g. 'Follow for daily fitness tips ↓')",
        "Link in bio: use Linktree or Beacons.ai to house all links",
        "Featured videos: pin your 3 best-performing videos",
        "TikTok LIVE: go live 1×/week — boosts algorithm reach",
        "Sounds: always use trending audio (even at low volume)",
        "Duets/Stitch: enable both — they extend reach",
        "Creator Marketplace: apply once you hit 10k followers",
    ],
    "instagram": [
        "Profile photo: professional, consistent with other platforms",
        "Username: short, memorable, same across all platforms",
        "Bio: keywords, emojis, CTA, and location if relevant",
        "Link in bio: dynamic (Linktree) or single landing page",
        "Highlights: organize into 4-6 labelled story highlights with covers",
        "Reels: post 3-5 Reels/week — they get 2× organic reach vs feed posts",
        "Collab posts: use Instagram Collab feature to cross-promote",
        "Alt text: add keyword-rich alt text to every image post for SEO",
    ],
    "youtube": [
        "Channel art: 2560×1440px with channel name and upload schedule",
        "Channel icon: professional photo or logo",
        "About section: keyword-rich description including upload schedule",
        "Channel trailer: 60–90s hook for non-subscribers",
        "Playlists: organize all videos into playlists for watch time",
        "End screens: always add 2 end screen elements",
        "Cards: add cards at 20% and 70% of video length",
        "Chapters: add timestamps in description for all videos ≥5min",
        "Thumbnail: bright, high-contrast, face close-up when possible",
        "Title formula: keyword + curiosity gap (e.g. 'I tried X for 30 days (shocking result)')",
    ],
}


def generate_account_report(account: dict, trending_hashtags: list = None, trending_music: list = None) -> dict:
    """Generate a full optimization report for one account."""
    platform = account.get("platform", "tiktok")
    handle = account.get("handle", "")
    niche = account.get("niche", "general")
    goals = account.get("goals", [])

    hashtag_set = build_hashtag_set(
        niche=niche,
        trending_hashtags=trending_hashtags or [],
        platform=platform,
    ) if trending_hashtags is not None else None

    schedule = generate_posting_schedule(platform, posts_per_week=7 if platform == "tiktok" else 3)

    top_music = []
    if trending_music:
        top_music = [
            {"title": m.get("title", ""), "artist": m.get("artist", ""), "clip_count": m.get("clip_count", 0)}
            for m in trending_music[:5]
        ]

    return {
        "account": {
            "platform": platform,
            "handle": f"@{handle}",
            "niche": niche,
            "goals": goals,
        },
        "profile_checklist": PROFILE_CHECKLIST.get(platform, []),
        "hashtag_strategy": hashtag_set,
        "posting_schedule": schedule[:7],
        "trending_music_to_use": top_music,
        "growth_tips": _growth_tips(platform, niche),
        "content_pillars": _content_pillars(niche),
    }


def _growth_tips(platform: str, niche: str) -> list:
    base = {
        "tiktok": [
            "Post within the first 30 minutes of peak hours — TikTok's algo favors fresh content",
            "Reply to EVERY comment in the first hour after posting",
            "Use trending sounds even if off-topic — put them at 5% volume",
            "Hook viewers in first 1–2 seconds: text overlay + movement",
            "Post 2–3× per day consistently for 30 days to train the algorithm",
            "Engage with 10 accounts in your niche for 10 min before posting",
            "Duet or stitch trending videos in your niche weekly",
        ],
        "instagram": [
            "Post Reels every day for 30 days — Instagram rewards consistency heavily",
            "Use all 5 Reel remix options to increase reach",
            "Reply to DMs and comments within 1 hour of posting",
            "Cross-post Reels to TikTok and YouTube Shorts for 3× reach",
            "Use Close Friends Stories for exclusive content to boost loyalty",
            "Collaborate with accounts in the 5k–50k follower range in your niche",
            "Add keywords in caption (not just hashtags) for Instagram SEO",
        ],
        "youtube": [
            "Nail the first 30 seconds — if retention drops, re-do the intro",
            "Upload on consistent days/times — subscribers appreciate reliability",
            "Add a chapter list in every description for better search indexing",
            "Create 'search-demand' videos first (answer questions people are Googling)",
            "Use A/B testing for thumbnails via YouTube Studio",
            "End every video with a strong verbal CTA to subscribe",
            "Create Shorts versions of long videos to funnel viewers",
        ],
    }
    return base.get(platform, [])


def _content_pillars(niche: str) -> list:
    """Return 4 content pillars for the given niche."""
    pillars = {
        "fitness": ["Workout tutorials", "Nutrition tips", "Transformation stories", "Motivation & mindset"],
        "food": ["Recipes & how-to", "Restaurant reviews", "Food hacks & tips", "Behind the scenes cooking"],
        "travel": ["Destination guides", "Travel hacks & tips", "Day-in-my-life vlogs", "Budget travel breakdowns"],
        "fashion": ["Outfit ideas & OOTD", "Trend breakdowns", "Thrift & budget finds", "Style challenges"],
        "beauty": ["Tutorials & how-to", "Product reviews", "Skincare routines", "Transformation content"],
        "finance": ["Money tips & hacks", "Investment breakdowns", "Income reports & side hustles", "Debt payoff stories"],
        "motivation": ["Daily affirmations", "Success stories", "Mindset shifts", "Productivity systems"],
        "gaming": ["Gameplay highlights", "Game reviews", "Tips & tricks", "Reactions & commentary"],
        "tech": ["Product reviews", "How-to tutorials", "Industry news takes", "Comparison videos"],
        "comedy": ["Skits & parody", "Relatable situations", "Trend participation", "Reactions"],
        "pets": ["Cute moments", "Training tips", "Pet product reviews", "Day in the life"],
        "dance": ["Choreography tutorials", "Trend participation", "Reaction to dances", "Behind the scenes"],
    }
    default = ["Educational tips", "Behind the scenes", "Community engagement", "Trending topic reaction"]
    return pillars.get(niche.lower(), default)
