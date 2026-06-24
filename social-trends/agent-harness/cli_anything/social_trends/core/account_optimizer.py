#!/usr/bin/env python3
"""Account optimizer — profile scoring, posting schedules, and growth playbooks.

Analyzes account configuration and generates actionable optimization recommendations
across Instagram, TikTok, and YouTube based on 2025-2026 best practices.
"""

from typing import Optional
from cli_anything.social_trends.utils.config import load_accounts


PLATFORM_SPECS = {
    "instagram": {
        "bio_max_chars": 150,
        "hashtags_optimal": 5,
        "hashtags_max": 10,
        "stories_per_day": 5,
        "posts_per_week": 5,
        "reels_per_week": 4,
        "best_times": ["8 AM", "12 PM", "6 PM", "9 PM"],
        "best_days": ["Tuesday", "Wednesday", "Thursday", "Friday"],
        "content_split": {"Reels": "60%", "Carousels": "25%", "Static": "15%"},
        "key_metric": "Saves + Shares (weighted 3x over likes in 2026 algorithm)",
    },
    "tiktok": {
        "bio_max_chars": 80,
        "hashtags_optimal": 5,
        "hashtags_max": 7,
        "posts_per_day_min": 1,
        "posts_per_day_max": 3,
        "best_times": ["9 AM", "12 PM", "5 PM", "8 PM"],
        "best_days": ["Tuesday", "Thursday", "Friday", "Saturday"],
        "content_split": {"Original": "80%", "Duet/Stitch": "15%", "Live": "5%"},
        "key_metric": "Average watch time % (aim for 80%+)",
    },
    "youtube": {
        "bio_max_chars": 1000,
        "hashtags_optimal": 3,
        "hashtags_max": 15,
        "videos_per_week": 2,
        "shorts_per_week": 5,
        "best_times": ["2 PM", "4 PM", "9 PM"],
        "best_days": ["Thursday", "Friday", "Saturday"],
        "content_split": {"Long-form": "30%", "Shorts": "60%", "Community": "10%"},
        "key_metric": "Click-through rate (CTR) on thumbnails (aim for 4-8%)",
    },
}

NICHE_CONTENT_PILLARS = {
    "motivation": [
        "Personal story / struggle", "Mindset tips", "Success evidence (before/after)",
        "Challenge or accountability", "Quote + music",
    ],
    "fitness": [
        "Workout tutorials", "Transformation content", "Nutrition tips",
        "Debunking myths", "Day-in-the-life", "Equipment reviews",
    ],
    "finance": [
        "Income reports / transparency", "Step-by-step tutorials", "Tool reviews",
        "Myth busting", "Case studies", "Emergency/cautionary tales",
    ],
    "fashion": [
        "Outfit of the day (OOTD)", "Styling tips", "Hauls and reviews",
        "Trend reactions", "Budget vs luxury comparisons", "GRWM",
    ],
    "beauty": [
        "Tutorials", "Product reviews", "Get Ready With Me (GRWM)",
        "Transformations", "Dupes and comparisons", "Skincare routines",
    ],
    "gaming": [
        "Gameplay clips", "Tips and tricks", "Reviews", "Tier lists",
        "Reactions to new releases", "Challenge runs",
    ],
    "food": [
        "Recipes", "Restaurant reviews", "Meal prep", "Mukbang",
        "Cooking hacks", "Ingredient deep dives",
    ],
    "business": [
        "Behind the scenes", "Revenue breakdowns", "Lessons learned",
        "Tool walkthroughs", "Client stories", "Mistakes to avoid",
    ],
}

BIO_TEMPLATES = {
    "instagram": {
        "creator": "🎯 {niche} creator\n{value_prop}\n📍 {location}\n👇 {cta}",
        "brand": "{brand_name} | {one_liner}\n✅ {social_proof}\n📩 {contact}\n🔗 {link_text}",
        "theme_page": "{niche} 🔥 | Daily {content_type}\n{follower_count}+ following\n👇 {cta}",
    },
    "tiktok": {
        "creator": "{niche} tips 🎯 | {value_prop} | {cta}",
        "brand": "{brand_name} | {niche} | {cta}",
        "theme_page": "Daily {niche} content 🔥 | {cta}",
    },
    "youtube": {
        "creator": (
            "Welcome to {channel_name}!\n\n"
            "I post {content_type} about {niche} every {schedule}.\n\n"
            "{value_prop}\n\n"
            "📧 Business: {email}\n"
            "📱 Instagram: {instagram_handle}"
        ),
    },
}


def score_bio(bio: str, platform: str) -> dict:
    """Score a bio string for optimization quality (0-100)."""
    spec = PLATFORM_SPECS.get(platform.lower(), {})
    max_chars = spec.get("bio_max_chars", 150)
    score = 0
    feedback = []
    improvements = []

    # Length check
    bio_len = len(bio)
    if 0 < bio_len <= max_chars:
        score += 20
        feedback.append(f"✓ Length OK ({bio_len}/{max_chars} chars)")
    elif bio_len == 0:
        feedback.append("✗ Bio is empty")
        improvements.append("Add a bio with your niche, value proposition, and CTA")
    else:
        score += 5
        feedback.append(f"✗ Bio too long ({bio_len}/{max_chars} chars)")
        improvements.append(f"Trim bio to under {max_chars} characters")

    # Keyword check
    keywords_to_check = ["coach", "creator", "tips", "help", "learn", "grow", "build", "make", "earn"]
    has_keyword = any(kw in bio.lower() for kw in keywords_to_check)
    if has_keyword:
        score += 20
        feedback.append("✓ Contains niche/value keyword")
    else:
        improvements.append("Add a niche keyword (e.g., 'fitness coach', 'finance tips', 'travel creator')")

    # CTA check
    cta_indicators = ["link", "click", "dm", "shop", "join", "watch", "follow", "check", "↓", "👇", "⬇"]
    has_cta = any(c in bio.lower() for c in cta_indicators)
    if has_cta:
        score += 20
        feedback.append("✓ Has call-to-action")
    else:
        improvements.append("Add a clear CTA (e.g., '👇 Free guide below', 'DM for collab', 'Link in bio')")

    # Emoji check (improves scannability)
    emoji_count = sum(1 for c in bio if ord(c) > 127)
    if 1 <= emoji_count <= 8:
        score += 15
        feedback.append("✓ Good emoji usage")
    elif emoji_count == 0:
        improvements.append("Add 2-4 emojis to improve scannability and visual appeal")
    else:
        score += 5
        improvements.append("Reduce emoji count — too many look spammy")

    # Social proof
    proof_indicators = ["k followers", "m followers", "years", "clients", "helped", "students", "#1", "top"]
    has_proof = any(p in bio.lower() for p in proof_indicators)
    if has_proof:
        score += 25
        feedback.append("✓ Contains social proof")
    else:
        improvements.append("Add social proof (e.g., '10K+ helped', '5 years exp', 'Top 1% creator')")

    return {
        "score": score,
        "grade": _score_to_grade(score),
        "feedback": feedback,
        "improvements": improvements,
        "bio_length": bio_len,
        "max_chars": max_chars,
    }


def _score_to_grade(score: int) -> str:
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def get_posting_schedule(platform: str, niche: str, goal: str = "growth") -> dict:
    """Generate a customized weekly posting schedule."""
    spec = PLATFORM_SPECS.get(platform.lower())
    if not spec:
        available = ", ".join(PLATFORM_SPECS.keys())
        raise ValueError(f"Unknown platform '{platform}'. Available: {available}")

    pillars = NICHE_CONTENT_PILLARS.get(niche.lower(), [
        "Educational content", "Personal story", "Engagement bait",
        "Trending topic reaction", "Promotional content (max 20%)",
    ])

    if platform.lower() == "tiktok":
        schedule = _build_tiktok_schedule(spec, pillars, goal)
    elif platform.lower() == "instagram":
        schedule = _build_instagram_schedule(spec, pillars, goal)
    else:
        schedule = _build_youtube_schedule(spec, pillars, goal)

    return {
        "platform": platform,
        "niche": niche,
        "goal": goal,
        "weekly_schedule": schedule,
        "content_pillars": pillars,
        "content_split": spec.get("content_split", {}),
        "key_metric": spec.get("key_metric", ""),
        "best_times": spec.get("best_times", []),
        "best_days": spec.get("best_days", []),
    }


def _build_tiktok_schedule(spec: dict, pillars: list, goal: str) -> list[dict]:
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    times = spec["best_times"]
    result = []
    for i, day in enumerate(days):
        posts = []
        # 2 posts on peak days (Tue, Thu, Fri, Sat), 1 on others
        n_posts = 2 if day in spec["best_days"] else 1
        for j in range(n_posts):
            pillar = pillars[(i * 2 + j) % len(pillars)]
            posts.append({
                "time": times[j % len(times)],
                "content_type": "Short (15-60s)",
                "pillar": pillar,
                "format_idea": _get_format_for_pillar(pillar),
            })
        result.append({"day": day, "posts": posts})
    return result


def _build_instagram_schedule(spec: dict, pillars: list, goal: str) -> list[dict]:
    peak_days = spec["best_days"]
    times = spec["best_times"]
    result = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for i, day in enumerate(days):
        posts = []
        if day in peak_days:
            pillar = pillars[i % len(pillars)]
            posts.append({
                "time": times[i % len(times)],
                "content_type": "Reel (15-90s)" if i % 3 != 2 else "Carousel (5-10 slides)",
                "pillar": pillar,
                "format_idea": _get_format_for_pillar(pillar),
            })
        posts.append({
            "time": "Any time",
            "content_type": "Story (5-7 slides)",
            "pillar": "Engagement / Behind the scenes",
            "format_idea": "Poll, Q&A, countdown, or BTS clip",
        })
        result.append({"day": day, "posts": posts})
    return result


def _build_youtube_schedule(spec: dict, pillars: list, goal: str) -> list[dict]:
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    times = spec["best_times"]
    result = []
    for i, day in enumerate(days):
        posts = []
        if day in spec["best_days"]:
            pillar = pillars[i % len(pillars)]
            if day == "Thursday":
                posts.append({
                    "time": times[0],
                    "content_type": "Long-form video (8-15 min)",
                    "pillar": pillar,
                    "format_idea": _get_format_for_pillar(pillar),
                })
            else:
                posts.append({
                    "time": times[0],
                    "content_type": "YouTube Short (30-60s)",
                    "pillar": pillar,
                    "format_idea": "Clipped highlight from long-form or standalone tip",
                })
        elif day in ["Monday", "Wednesday"]:
            posts.append({
                "time": times[-1],
                "content_type": "YouTube Short (30-60s)",
                "pillar": "Quick tip / Trending topic",
                "format_idea": "Talking head or b-roll montage with text overlay",
            })
        result.append({"day": day, "posts": posts})
    return result


def _get_format_for_pillar(pillar: str) -> str:
    mapping = {
        "personal story": "Talking head with b-roll cutaways",
        "tutorial": "Screen recording or step-by-step demo",
        "transformation": "Side-by-side before/after with music",
        "tips": "Text overlay list with fast cuts",
        "reaction": "Split screen or side-by-side",
        "educational": "Explainer with graphics or whiteboard",
        "behind the scenes": "Raw footage / vlog style",
        "engagement": "Question prompt or poll overlay",
    }
    pillar_lower = pillar.lower()
    for key, fmt in mapping.items():
        if key in pillar_lower:
            return fmt
    return "Hook (3s) → Value → CTA"


def optimize_account(platform: str, handle: str, niche: str,
                     bio: Optional[str] = None,
                     follower_count: int = 0,
                     goal: str = "growth") -> dict:
    """Run a full account optimization audit."""
    spec = PLATFORM_SPECS.get(platform.lower())
    if not spec:
        available = ", ".join(PLATFORM_SPECS.keys())
        raise ValueError(f"Unknown platform '{platform}'. Available: {available}")

    bio_analysis = score_bio(bio or "", platform) if bio else None
    schedule = get_posting_schedule(platform, niche, goal)
    growth_stage = _get_growth_stage(follower_count)
    action_plan = _get_action_plan(platform, niche, follower_count, goal)

    return {
        "account": {
            "platform": platform,
            "handle": f"@{handle.lstrip('@')}",
            "niche": niche,
            "goal": goal,
            "followers": follower_count,
            "growth_stage": growth_stage,
        },
        "bio_analysis": bio_analysis,
        "posting_schedule": schedule,
        "30_day_action_plan": action_plan,
        "platform_specs": spec,
    }


def _get_growth_stage(followers: int) -> dict:
    if followers == 0:
        return {"stage": "Pre-launch", "priority": "Build foundation content before first post"}
    if followers < 1_000:
        return {"stage": "Nano (0-1K)", "priority": "Consistency and niche clarity — post daily"}
    if followers < 10_000:
        return {"stage": "Micro (1K-10K)", "priority": "Engagement loops and collaborations"}
    if followers < 100_000:
        return {"stage": "Mid-tier (10K-100K)", "priority": "Monetization + repurposing content"}
    if followers < 1_000_000:
        return {"stage": "Macro (100K-1M)", "priority": "Brand deals + own products"}
    return {"stage": "Mega (1M+)", "priority": "Diversify revenue + build off-platform assets"}


def _get_action_plan(platform: str, niche: str, followers: int, goal: str) -> list[dict]:
    base_plan = [
        {
            "week": 1,
            "focus": "Content Foundation",
            "tasks": [
                f"Film 7-10 pieces of content in one shoot day",
                f"Set up all profiles with optimized bio, profile pic, and highlight covers",
                f"Research top 20 competitors in {niche} niche — note their best performing formats",
                f"Build hashtag bank: 30+ tags across small/medium/large buckets",
                f"Schedule first week's posts using your optimal posting times",
            ],
        },
        {
            "week": 2,
            "focus": "Engagement & Algorithm Seeding",
            "tasks": [
                "Reply to EVERY comment within the first hour of posting",
                "Engage with 20 accounts/day in your niche (genuine comments, not 'great post!')",
                "Duet or stitch 2-3 trending videos in your niche",
                "Post at least 1 poll/question in Stories or Community tab",
                "Analyze Week 1 metrics — double down on what performed best",
            ],
        },
        {
            "week": 3,
            "focus": "Growth Acceleration",
            "tasks": [
                "Reach out to 5 accounts in same niche for collab or shoutout swap",
                "Repurpose best-performing video to all platforms (cross-post)",
                "Create a 'lead magnet' (free checklist, guide, template) to add to bio link",
                "Test a new content format you haven't tried yet",
                "Start building email list — link to landing page in bio",
            ],
        },
        {
            "week": 4,
            "focus": "Monetization Setup",
            "tasks": [
                "Join 2-3 affiliate programs in your niche (Amazon, ShareASale, niche-specific)",
                "Create first promotional post (no more than 1 in 5 posts)",
                "DM brands in your niche for gifted collaboration",
                "Review month analytics — identify your top 3 content types by reach",
                "Plan Month 2 content calendar based on Month 1 learnings",
            ],
        },
    ]
    return base_plan


def get_all_accounts_summary() -> list[dict]:
    """Load all saved accounts and return optimization summaries."""
    accounts = load_accounts()
    if not accounts:
        return []
    summaries = []
    for acc in accounts:
        stage = _get_growth_stage(acc.get("followers", 0))
        summaries.append({
            **acc,
            "growth_stage": stage["stage"],
            "priority": stage["priority"],
        })
    return summaries
