"""Account optimization engine.

Generates data-driven recommendations for profile, content strategy,
hashtag sets, and posting schedules based on live trend data.
"""

import time
from typing import Optional

from . import trend_aggregator as agg


# Niche-specific keyword maps for hashtag relevance scoring
_NICHE_EXPANSIONS = {
    "fitness": ["gym", "workout", "health", "muscle", "cardio", "weight", "training", "bodybuilding"],
    "fashion": ["style", "outfit", "ootd", "clothing", "trend", "aesthetic", "wear", "looks"],
    "food": ["recipe", "cooking", "eat", "foodie", "chef", "meal", "delicious", "kitchen"],
    "travel": ["adventure", "explore", "vacation", "trip", "destination", "wanderlust", "hotel"],
    "finance": ["money", "invest", "wealth", "crypto", "stocks", "budget", "income", "savings"],
    "beauty": ["makeup", "skincare", "glow", "cosmetics", "glam", "tutorial", "nails", "hair"],
    "gaming": ["game", "play", "stream", "gamer", "esports", "console", "pc", "fps"],
    "tech": ["technology", "ai", "software", "coding", "developer", "startup", "innovation"],
    "music": ["song", "artist", "beat", "audio", "rap", "pop", "hiphop", "producer"],
    "motivation": ["mindset", "success", "hustle", "grind", "inspire", "entrepreneur", "goals"],
    "luxury": ["expensive", "rich", "wealth", "lifestyle", "premium", "exclusive", "millionaire"],
    "comedy": ["funny", "humor", "laugh", "meme", "joke", "viral", "entertainment", "prank"],
    "cars": ["automotive", "supercar", "racing", "drift", "horsepower", "auto", "speed"],
}

# Platform-specific best posting windows (hour ranges, 24h UTC offset by timezone)
_POSTING_WINDOWS = {
    "tiktok": [
        {"day": "Mon-Fri", "window": "06:00-10:00", "reason": "Morning commute scroll"},
        {"day": "Mon-Fri", "window": "12:00-14:00", "reason": "Lunch break peak"},
        {"day": "Mon-Fri", "window": "19:00-23:00", "reason": "Evening prime time"},
        {"day": "Sat-Sun", "window": "09:00-11:00", "reason": "Weekend morning"},
        {"day": "Sat-Sun", "window": "14:00-17:00", "reason": "Weekend afternoon peak"},
    ],
    "instagram": [
        {"day": "Mon-Fri", "window": "08:00-09:00", "reason": "Pre-work check"},
        {"day": "Mon-Fri", "window": "11:00-13:00", "reason": "Midday engagement"},
        {"day": "Mon-Fri", "window": "17:00-19:00", "reason": "After work"},
        {"day": "Sat-Sun", "window": "10:00-12:00", "reason": "Weekend leisure"},
    ],
    "youtube": [
        {"day": "Mon-Wed", "window": "14:00-16:00", "reason": "Afternoon discovery"},
        {"day": "Thu-Fri", "window": "12:00-15:00", "reason": "Pre-weekend uploads"},
        {"day": "Sat-Sun", "window": "09:00-11:00", "reason": "Weekend binge sessions"},
    ],
    "twitter": [
        {"day": "Mon-Fri", "window": "08:00-10:00", "reason": "Morning news cycle"},
        {"day": "Mon-Fri", "window": "12:00-13:00", "reason": "Lunch scroll"},
        {"day": "Mon-Fri", "window": "17:00-18:00", "reason": "End of workday"},
    ],
}

# Platform bio/profile optimization templates
_PROFILE_TEMPLATES = {
    "tiktok": {
        "bio_formula": "[Hook statement] | [Value prop] | [CTA with link]",
        "bio_example": "Daily {niche} tips that actually work | Follow for {value} | Link below",
        "bio_max_chars": 80,
        "profile_tips": [
            "Use a clear, recognizable profile photo (face or logo)",
            "Add 1-2 emojis that represent your niche",
            "Include a direct CTA (Follow, Link in bio, etc.)",
            "Mention your posting frequency (Daily, 3x/week)",
            "Connect Instagram and YouTube for cross-promotion",
        ],
        "content_format": "9:16 vertical, 1080x1920px, 15-60s optimal",
        "caption_formula": "Hook question or statement + 3-5 hashtags + CTA",
    },
    "instagram": {
        "bio_formula": "[Who you are] | [What you do] | [Why follow] | [CTA + link]",
        "bio_example": "{niche} creator | {value} | DM for collabs | Link below",
        "bio_max_chars": 150,
        "profile_tips": [
            "Switch to a Creator or Business account for analytics",
            "Use a keyword in your name field (not just display name) for SEO",
            "Highlight covers should match your theme aesthetic",
            "Add location if locally targeted",
            "Pin your best 3 posts (Reels perform best)",
        ],
        "content_format": "Reels: 9:16 1080x1920px | Feed: 1:1 or 4:5 | Stories: 9:16",
        "caption_formula": "Hook (first 2 lines) + Story + CTA + 20-30 hashtags",
    },
    "youtube": {
        "bio_formula": "[Upload schedule] | [Channel value prop] | [Links]",
        "bio_example": "New videos every {day} | {niche} tips, tricks & tutorials",
        "bio_max_chars": 1000,
        "profile_tips": [
            "Fill channel keywords (Settings > Channel > Basic info)",
            "Create a compelling channel trailer (60-90 seconds)",
            "Set up end screens and cards on every video",
            "Use a consistent thumbnail style/template",
            "Pin a channel membership or best video as featured",
        ],
        "content_format": "16:9 1920x1080p (minimum), thumbnail 1280x720px",
        "caption_formula": "Keyword-rich title + Detailed description with timestamps + Tags",
    },
}


def optimize_profile(platform: str, niche: str) -> dict:
    """Generate profile optimization checklist for a platform and niche.

    Returns actionable steps the account owner can implement immediately.
    """
    platform = platform.lower()
    template = _PROFILE_TEMPLATES.get(platform, _PROFILE_TEMPLATES["tiktok"])
    niche_keywords = _NICHE_EXPANSIONS.get(niche.lower(), [niche.lower()])

    return {
        "platform": platform,
        "niche": niche,
        "bio_formula": template["bio_formula"],
        "bio_example": template["bio_example"].replace("{niche}", niche)
            .replace("{value}", f"{niche} value")
            .replace("{day}", "Tuesday & Friday"),
        "bio_max_chars": template["bio_max_chars"],
        "content_format": template["content_format"],
        "caption_formula": template["caption_formula"],
        "profile_tips": template["profile_tips"],
        "niche_keywords": niche_keywords[:10],
        "seo_tip": f"Include '{niche}' in your display name or username for search visibility",
        "action_items": [
            f"1. Update bio to match formula: {template['bio_formula']}",
            "2. Post 3 pieces of content TODAY to establish baseline",
            "3. Engage with 10 accounts in your niche (like + comment)",
            f"4. Research top 5 {niche} creators and note their content patterns",
            "5. Set up analytics tracking (Creator account required)",
        ],
    }


def generate_hashtag_set(
    niche: str,
    platform: str = "tiktok",
    count: int = 30,
    region: str = "US",
    use_cache: bool = True,
) -> dict:
    """Generate an optimized hashtag set mixing trending + niche-specific tags.

    Follows the mix strategy:
    - 30% mega tags (1M+ posts) for discovery
    - 40% mid tags (100K-1M posts) for targeted reach
    - 30% niche tags (<100K posts) for community
    """
    # Get live trending hashtags
    try:
        opportunities = agg.find_opportunities(niche=niche, region=region, use_cache=use_cache)
        trending_tags = [t["tag"] for t in opportunities.get("relevant_hashtags", [])[:20]]
        cross_platform_tags = [t["tag"] for t in opportunities.get("top_cross_platform_tags", [])[:10]]
    except Exception:
        trending_tags = []
        cross_platform_tags = []

    # Niche-specific curated tags
    niche_lower = niche.lower()
    niche_words = _NICHE_EXPANSIONS.get(niche_lower, [niche_lower])
    curated_niche = [f"#{w}" for w in niche_words[:8]]
    curated_broad = [f"#{niche_lower}", f"#{niche_lower}tips", f"#{niche_lower}motivation",
                     f"#{niche_lower}life", f"#{niche_lower}community"]

    # Platform mega tags
    if platform == "tiktok":
        mega_tags = ["#fyp", "#foryoupage", "#viral", "#trending", "#foryou"]
    elif platform == "instagram":
        mega_tags = ["#reels", "#explore", "#instadaily", "#viral", "#trending"]
    elif platform == "youtube":
        mega_tags = ["#shorts", "#youtube", "#trending", "#viral"]
    else:
        mega_tags = ["#viral", "#trending", "#explore"]

    # Assemble the set
    final_set = list(dict.fromkeys(
        mega_tags[:3] + trending_tags[:8] + cross_platform_tags[:5]
        + curated_niche[:6] + curated_broad[:4] + mega_tags[3:]
    ))[:count]

    # Tag mix breakdown
    mix = {
        "mega_tags_for_discovery": mega_tags[:3],
        "trending_tags_from_scrape": trending_tags[:8],
        "cross_platform_tags": cross_platform_tags[:5],
        "niche_specific_tags": curated_niche[:6],
        "niche_broad_tags": curated_broad[:4],
    }

    return {
        "platform": platform,
        "niche": niche,
        "region": region,
        "hashtag_count": len(final_set),
        "hashtags": final_set,
        "hashtags_string": " ".join(final_set),
        "mix_breakdown": mix,
        "usage_tip": (
            f"For {platform}: Use all {len(final_set)} tags. "
            "Rotate the mid-tier tags every 3-5 posts to avoid shadow bans. "
            "Always keep the niche tags consistent."
        ),
        "rotation_strategy": {
            "keep_always": mega_tags[:2] + curated_niche[:3],
            "rotate_every_5_posts": trending_tags[:5],
        },
    }


def optimize_content_strategy(
    niche: str,
    platform: str = "tiktok",
    posts_per_week: int = 7,
    region: str = "US",
    use_cache: bool = True,
) -> dict:
    """Generate a full content strategy based on trends and niche.

    Returns content pillars, hook formulas, and a weekly content plan.
    """
    niche_lower = niche.lower()

    # Content pillars (5-pillar framework)
    pillar_map = {
        "fitness": ["Education (form/technique)", "Transformation (before/after)",
                    "Motivation/Mindset", "Routine/Day-in-life", "Product/Review"],
        "finance": ["Tips/Hacks", "Case Studies/Success", "Mistakes to Avoid",
                    "News/Commentary", "How-to/Tutorial"],
        "fashion": ["Outfit Inspiration (OOTD)", "Haul/Review", "Styling Tips",
                    "Trend Breakdown", "Behind-the-scenes"],
        "food": ["Recipes (quick)", "Restaurant Reviews", "Cooking Tips",
                 "Food Science/Facts", "Seasonal/Trending"],
        "luxury": ["Lifestyle showcases", "Product deep-dives", "Comparison (worth it?)",
                   "Behind-the-scenes wealth", "Aspirational storytelling"],
        "comedy": ["Relatable skits", "Trend reactions", "POV videos",
                   "Parody/Satire", "Duet/Collab content"],
    }
    pillars = pillar_map.get(niche_lower, [
        f"Educational {niche} content",
        f"{niche} tips & hacks",
        f"Personal story/{niche} journey",
        f"Trending {niche} reactions",
        f"{niche} product/tool reviews",
    ])

    # Hook formulas
    hook_formulas = [
        f"\"Did you know {niche} can...\" (curiosity gap)",
        f"\"POV: You're a {niche} expert\" (perspective hook)",
        f"\"Stop doing THIS with {niche}\" (negative hook)",
        f"\"The {niche} hack nobody talks about\" (secret hook)",
        f"\"I tried {niche} for 30 days...\" (challenge hook)",
        f"\"Rate my {niche} (1-10)\" (engagement bait hook)",
    ]

    # Build weekly content calendar
    calendar = []
    pillar_cycle = pillars * ((posts_per_week // len(pillars)) + 1)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    windows = _POSTING_WINDOWS.get(platform, _POSTING_WINDOWS["tiktok"])

    for i in range(posts_per_week):
        day = days[i % 7]
        pillar = pillar_cycle[i]
        window = windows[i % len(windows)]
        calendar.append({
            "day": day,
            "posting_window": window["window"],
            "content_pillar": pillar,
            "hook_formula": hook_formulas[i % len(hook_formulas)],
            "content_idea": f"{pillar} — {hook_formulas[i % len(hook_formulas)]}",
        })

    # Get trending hashtags for this niche
    try:
        hashtag_result = generate_hashtag_set(niche=niche, platform=platform,
                                              region=region, use_cache=use_cache)
        top_hashtags = hashtag_result["hashtags"][:15]
    except Exception:
        top_hashtags = [f"#{niche}", "#viral", "#trending"]

    return {
        "niche": niche,
        "platform": platform,
        "posts_per_week": posts_per_week,
        "content_pillars": pillars,
        "hook_formulas": hook_formulas,
        "weekly_calendar": calendar,
        "recommended_hashtags": top_hashtags,
        "engagement_tactics": [
            "Reply to EVERY comment in the first hour after posting",
            "Ask a question at the end of every caption",
            "Do a Stitch or Duet with a trending video in your niche",
            "Go Live once per week to boost algorithmic distribution",
            "Cross-post Reels/Shorts across Instagram, TikTok, and YouTube Shorts",
        ],
        "growth_kpis": {
            "week_1_goal": "100 followers, 1,000 views total",
            "month_1_goal": "500 followers, 1 viral post (10K+ views)",
            "month_3_goal": "2,000+ followers, consistent 5K+ views per post",
        },
    }


def best_posting_times(platform: str, timezone: str = "EST") -> dict:
    """Return optimal posting windows for a platform.

    Times shown are local time in the specified timezone.
    """
    platform = platform.lower()
    windows = _POSTING_WINDOWS.get(platform, _POSTING_WINDOWS["tiktok"])

    tz_offset_map = {
        "EST": -5, "EDT": -4, "CST": -6, "CDT": -5,
        "MST": -7, "MDT": -6, "PST": -8, "PDT": -7,
        "GMT": 0, "UTC": 0, "BST": 1, "CET": 1, "IST": 5,
    }
    offset = tz_offset_map.get(timezone.upper(), 0)

    return {
        "platform": platform,
        "timezone": timezone,
        "utc_offset_hours": offset,
        "posting_windows": windows,
        "best_days": {
            "tiktok": ["Tuesday", "Thursday", "Friday"],
            "instagram": ["Monday", "Wednesday", "Friday"],
            "youtube": ["Thursday", "Friday", "Saturday"],
            "twitter": ["Monday", "Wednesday", "Thursday"],
        }.get(platform, ["Tuesday", "Thursday", "Saturday"]),
        "worst_days": {
            "tiktok": ["Sunday evening"],
            "instagram": ["Sunday", "Monday morning"],
            "youtube": ["Monday", "Tuesday"],
        }.get(platform, ["Sunday"]),
        "frequency_recommendation": {
            "minimum": "3x/week to maintain algorithmic favor",
            "optimal": "1x/day for fastest growth",
            "maximum": "3x/day (risk of reduced per-post distribution)",
        },
        "consistency_note": (
            "Consistency beats frequency. Posting at the same time daily "
            "trains the algorithm to expect and distribute your content."
        ),
    }
