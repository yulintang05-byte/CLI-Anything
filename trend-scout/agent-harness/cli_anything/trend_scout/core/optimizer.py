"""Account optimization engine.

Analyzes scraped trend data and generates actionable posting strategy
recommendations: best times, hashtag mixes, content pillars, sound pairings.
"""

import time
from typing import Any


# ── Posting time data (based on 2024-2026 platform research) ─────────────────

_BEST_TIMES: dict[str, dict[str, list[str]]] = {
    "tiktok": {
        "monday":    ["06:00-09:00", "12:00-15:00", "19:00-23:00"],
        "tuesday":   ["09:00-12:00", "15:00-18:00", "19:00-23:00"],
        "wednesday": ["06:00-09:00", "12:00-15:00", "21:00-23:00"],
        "thursday":  ["09:00-12:00", "15:00-18:00", "20:00-23:00"],
        "friday":    ["05:00-09:00", "12:00-15:00", "19:00-23:00"],
        "saturday":  ["09:00-11:00", "14:00-17:00", "20:00-23:00"],
        "sunday":    ["07:00-11:00", "14:00-17:00", "19:00-23:00"],
    },
    "youtube": {
        "monday":    ["14:00-16:00", "20:00-21:00"],
        "tuesday":   ["14:00-16:00", "20:00-21:00"],
        "wednesday": ["14:00-16:00", "20:00-21:00"],
        "thursday":  ["14:00-16:00", "20:00-21:00"],
        "friday":    ["14:00-16:00", "20:00-21:00"],
        "saturday":  ["09:00-11:00", "17:00-20:00"],
        "sunday":    ["09:00-11:00", "17:00-20:00"],
    },
    "instagram": {
        "monday":    ["06:00-09:00", "12:00-14:00", "17:00-20:00"],
        "tuesday":   ["08:00-10:00", "12:00-14:00", "17:00-20:00"],
        "wednesday": ["08:00-10:00", "12:00-14:00", "17:00-20:00"],
        "thursday":  ["08:00-10:00", "12:00-14:00", "17:00-20:00"],
        "friday":    ["08:00-10:00", "12:00-14:00", "17:00-20:00"],
        "saturday":  ["09:00-11:00", "14:00-17:00"],
        "sunday":    ["10:00-12:00", "14:00-17:00"],
    },
}

_DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

# Hashtag strategy by account size
_HASHTAG_STRATEGY = {
    "nano":   {"count": "5-10",  "mix": "80% niche, 20% mid-range", "note": "Avoid #fyp traps — niche tags get you real followers"},
    "micro":  {"count": "10-20", "mix": "60% niche, 30% mid-range, 10% broad", "note": "Layer 2-3 trending tags on viral content only"},
    "mid":    {"count": "15-25", "mix": "50% niche, 35% mid-range, 15% broad", "note": "Test trending tags on every 3rd post"},
    "macro":  {"count": "20-30", "mix": "30% niche, 40% mid-range, 30% broad", "note": "Broad tags work at scale — prioritize engagement rate"},
    "mega":   {"count": "5-15",  "mix": "20% niche, 30% mid-range, 50% broad", "note": "Algorithm pushes your content regardless — focus on quality"},
}

# Content pillars for theme pages
_CONTENT_PILLARS = {
    "motivation": ["quote cards", "success stories", "morning routines", "mindset shifts", "books summaries"],
    "fashion":    ["outfit inspo", "haul videos", "fit checks", "style guides", "trend roundups"],
    "food":       ["recipes", "restaurant reviews", "food hacks", "aesthetic plating", "taste tests"],
    "fitness":    ["workout demos", "progress videos", "nutrition tips", "challenges", "transformation stories"],
    "travel":     ["destination reels", "travel hacks", "budget tips", "hidden gems", "packing guides"],
    "comedy":     ["skits", "reaction videos", "relatable moments", "duets/stitches", "POV videos"],
    "finance":    ["money tips", "investing basics", "side hustles", "budgeting", "financial freedom stories"],
    "beauty":     ["tutorials", "product reviews", "get-ready-with-me", "transformation", "dupes"],
    "gaming":     ["gameplay clips", "tips and tricks", "game reviews", "tournaments", "reaction"],
    "education":  ["did you know", "explainers", "myth busting", "tutorials", "book/course reviews"],
}


def _follower_tier(count: int) -> str:
    if count < 1_000:
        return "nano"
    if count < 10_000:
        return "micro"
    if count < 100_000:
        return "mid"
    if count < 1_000_000:
        return "macro"
    return "mega"


def _today_name() -> str:
    return _DAYS[time.localtime().tm_wday]


def generate_report(
    platform: str,
    niche: str,
    follower_count: int,
    trending_hashtags: list[str],
    trending_sounds: list[dict] | None = None,
) -> dict:
    """Generate a full account optimization report.

    Args:
        platform: "tiktok" | "youtube" | "instagram"
        niche: content niche (e.g. "fitness", "travel")
        follower_count: current follower count
        trending_hashtags: list of trending hashtag names (without #)
        trending_sounds: list of sound dicts with title/artist keys
    """
    platform = platform.lower()
    tier = _follower_tier(follower_count)
    hashtag_strat = _HASHTAG_STRATEGY.get(tier, _HASHTAG_STRATEGY["micro"])

    # Best posting times
    times = _BEST_TIMES.get(platform, _BEST_TIMES["tiktok"])
    today = _today_name()
    todays_times = times.get(today, [])
    tomorrow = _DAYS[(_DAYS.index(today) + 1) % 7]
    tomorrows_times = times.get(tomorrow, [])

    # Hashtag recommendations: top trending + niche mix
    top_trending = trending_hashtags[:5]
    niche_pillar = _CONTENT_PILLARS.get(niche.lower(), _CONTENT_PILLARS.get("motivation", []))

    # Sound recommendations
    sound_recs = []
    if trending_sounds:
        for s in trending_sounds[:5]:
            sound_recs.append(f"{s.get('title', '')} — {s.get('artist', '')}")

    # Caption formula
    caption_formulas = [
        "Hook (1 line) → Value (3 lines) → CTA + 3-5 hashtags",
        "POV: [relatable situation] → reveal → engagement question",
        "Did you know [fact]? → context → save this for later",
        "[Bold claim] → proof → call to action",
    ]

    # Growth tactics
    growth_tactics = _growth_tactics(platform, tier, niche)

    return {
        "platform": platform,
        "niche": niche,
        "follower_count": follower_count,
        "tier": tier,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "posting_times": {
            "today": {"day": today, "windows": todays_times},
            "tomorrow": {"day": tomorrow, "windows": tomorrows_times},
            "full_week": times,
        },
        "hashtag_strategy": {
            "recommended_count": hashtag_strat["count"],
            "mix": hashtag_strat["mix"],
            "note": hashtag_strat["note"],
            "top_trending_to_use": [f"#{t}" for t in top_trending],
            "niche_hashtags_to_rotate": [f"#{t}" for t in _niche_hashtags(niche)],
        },
        "content_pillars": {
            "niche": niche,
            "formats": niche_pillar[:5],
            "post_frequency": _post_frequency(platform, tier),
        },
        "sound_recommendations": sound_recs,
        "caption_formulas": caption_formulas,
        "growth_tactics": growth_tactics,
        "monetization_milestones": _monetization_milestones(platform),
    }


def _niche_hashtags(niche: str) -> list[str]:
    """Return niche-specific hashtag suggestions."""
    niche_tags: dict[str, list[str]] = {
        "motivation":  ["motivationmonday", "mindset", "selfimprovement", "growthmindset", "successquotes"],
        "fashion":     ["ootd", "fashioninspo", "styleinspo", "outfitideas", "fashionblogger"],
        "food":        ["foodie", "foodtok", "easyrecipes", "foodblogger", "whatsforeating"],
        "fitness":     ["fitnessmotivation", "gymtok", "workouttips", "fitnessgirl", "bodybuilding"],
        "travel":      ["traveltok", "travelinspo", "wanderlust", "travelwithme", "bucketlist"],
        "comedy":      ["comedytok", "funny", "laughing", "funnymemes", "humor"],
        "finance":     ["financetok", "moneytips", "personalfinance", "investing101", "sidehustle"],
        "beauty":      ["beautytok", "makeuptutorial", "skincareroutine", "grwm", "beautytips"],
        "gaming":      ["gamingtok", "gamingcommunity", "gamer", "gamingclips", "fyp"],
        "education":   ["learnontiktok", "edutok", "didyouknow", "factsoftiktok", "studytok"],
    }
    return niche_tags.get(niche.lower(), ["trending", "viral", "foryou", "content", "creator"])


def _post_frequency(platform: str, tier: str) -> str:
    freq: dict[str, dict[str, str]] = {
        "tiktok": {
            "nano": "1-2x/day (consistency > quantity at start)",
            "micro": "2-3x/day (test formats, double down on winners)",
            "mid": "3-5x/day (volume drives algorithm exposure)",
            "macro": "2-3x/day (quality compounds at scale)",
            "mega": "1-2x/day (audience expects quality, not quantity)",
        },
        "youtube": {
            "nano": "1x/week (production quality matters most)",
            "micro": "2x/week + 3-5 Shorts/week",
            "mid": "3x/week + daily Shorts",
            "macro": "2-3x/week + daily Shorts",
            "mega": "1-2x/week (subscribers will wait for quality)",
        },
        "instagram": {
            "nano": "1 Reel/day + 3-5 Stories/day",
            "micro": "1-2 Reels/day + 5-7 Stories/day",
            "mid": "2-3 Reels/day + 7-10 Stories/day",
            "macro": "1-2 Reels/day + daily Stories",
            "mega": "1 Reel/day + Stories + Lives",
        },
    }
    return freq.get(platform, freq["tiktok"]).get(tier, "2x/day")


def _growth_tactics(platform: str, tier: str, niche: str) -> list[str]:
    base = [
        "Hook viewers in the first 1-2 seconds (pattern interrupt)",
        "Add captions/subtitles — 85% of videos are watched on mute",
        "End with a question to drive comments (boost engagement rate)",
        "Reply to every comment in the first hour (signals activity)",
        "Cross-post to all platforms within 2 hours of publishing",
    ]
    platform_specific: dict[str, list[str]] = {
        "tiktok": [
            "Duet/Stitch viral videos in your niche for free exposure",
            "Pin your 3 best performing videos to your profile",
            "Go LIVE 2-3x/week to boost algorithmic reach",
            "Use trending sounds even for non-music content",
            "Post at least one 'controversial take' per week for debate comments",
        ],
        "youtube": [
            "Optimize thumbnails — test A/B with YouTube Studio",
            "Add chapters/timestamps to improve session watch time",
            "Post Shorts to feed long-form algorithm",
            "Use YouTube's community tab after 500 subscribers",
            "Collaborate with similar-sized channels for cross-promotion",
        ],
        "instagram": [
            "Use the 'Add Yours' sticker on Stories to drive UGC",
            "Repost top-performing TikToks as Reels (remove watermark first)",
            "Use Broadcast Channels to build superfan community",
            "Collab posts reach both audiences simultaneously",
            "Save this post: call-to-action drives highest saves rate",
        ],
    }
    return base + platform_specific.get(platform, [])


def _monetization_milestones(platform: str) -> list[dict]:
    milestones: dict[str, list[dict]] = {
        "tiktok": [
            {"milestone": "1K followers", "unlocks": "LIVE access"},
            {"milestone": "10K followers", "unlocks": "TikTok Creator Rewards Program eligibility"},
            {"milestone": "100K views/30 days", "unlocks": "Full Creator Rewards Program ($0.40-$1/1K views)"},
            {"milestone": "10K followers + 100K views", "unlocks": "TikTok Shop affiliate commission"},
            {"milestone": "100K followers", "unlocks": "Brand deals ($500-$2,000/post avg)"},
            {"milestone": "1M followers", "unlocks": "TikTok Pulse ad revenue sharing"},
        ],
        "youtube": [
            {"milestone": "500 subscribers", "unlocks": "Community posts"},
            {"milestone": "1K subs + 4K watch hours", "unlocks": "YouTube Partner Program (ads)"},
            {"milestone": "1K subs + 10M Shorts views", "unlocks": "Shorts monetization"},
            {"milestone": "20K subscribers", "unlocks": "Super Thanks + Channel Memberships"},
            {"milestone": "100K subscribers", "unlocks": "Silver Play Button + brand deals ($1K-$10K/video)"},
        ],
        "instagram": [
            {"milestone": "10K followers", "unlocks": "Swipe-up links in Stories"},
            {"milestone": "10K followers + professional account", "unlocks": "Instagram Gifts on Reels"},
            {"milestone": "30K followers", "unlocks": "Subscriptions feature"},
            {"milestone": "50K followers", "unlocks": "Brand deals ($200-$1,500/post avg)"},
            {"milestone": "100K followers", "unlocks": "Meta Content Monetization"},
        ],
    }
    return milestones.get(platform, milestones["tiktok"])


def compare_trends(yt_trends: dict, tt_trends: dict) -> dict:
    """Cross-platform trend comparison — find overlapping viral themes."""
    yt_tags = set(yt_trends.get("top_hashtags", []))
    tt_tags = set(tt_trends.get("top_hashtags", []))
    overlap = yt_tags & tt_tags

    yt_sounds = set(v.get("title", "") for v in yt_trends.get("top_sounds", []))
    tt_sounds = set(s.get("title", "") for s in tt_trends.get("trending_sounds", []))
    sound_overlap = yt_sounds & tt_sounds

    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cross_platform_hashtags": sorted(overlap),
        "youtube_only_tags": sorted(yt_tags - tt_tags)[:10],
        "tiktok_only_tags": sorted(tt_tags - yt_tags)[:10],
        "cross_platform_sounds": sorted(sound_overlap),
        "recommendation": (
            "Post content using cross-platform hashtags first — "
            "they signal platform-agnostic virality. "
            "Then layer platform-specific tags for native boost."
        ),
        "action_items": [
            f"Use #{t} on both platforms immediately" for t in list(overlap)[:5]
        ] + [
            "Create 1 piece of content per cross-platform trend this week",
            "Track which cross-platform tag drives highest engagement rate",
        ],
    }
