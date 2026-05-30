#!/usr/bin/env python3
"""Content calendar generator for theme pages.

Produces weekly and monthly posting schedules with content type suggestions,
trending hook templates, and posting time recommendations.
"""

from datetime import datetime, timedelta
from typing import Optional


# Content type templates per niche
CONTENT_TEMPLATES = {
    "luxury_lifestyle": [
        {"type": "showcase", "hook": "You've never seen a [X] like this...", "format": "short_video"},
        {"type": "comparison", "hook": "Budget vs Luxury: [X]", "format": "side_by_side"},
        {"type": "facts", "hook": "[X] facts about [luxury item] most people don't know", "format": "text_overlay"},
        {"type": "aspiration", "hook": "When you finally [achieve goal]...", "format": "aesthetic_video"},
        {"type": "transformation", "hook": "From $0 to [X] — the real story", "format": "talking_head"},
        {"type": "tour", "hook": "Inside a $[X]M [mansion/yacht/car]", "format": "walkthrough_video"},
    ],
    "fitness_motivation": [
        {"type": "transformation", "hook": "[X] months, [Y] lbs — here's what I did", "format": "before_after"},
        {"type": "workout", "hook": "Try this [X] min workout — no equipment needed", "format": "tutorial"},
        {"type": "tip", "hook": "The [X] fitness mistake 99% of people make", "format": "talking_head"},
        {"type": "motivation", "hook": "On days you don't want to go to the gym...", "format": "montage"},
        {"type": "myth_bust", "hook": "[Common fitness belief] is actually wrong. Here's why:", "format": "educational"},
        {"type": "challenge", "hook": "Try this 30-second challenge — can you do it?", "format": "interactive"},
    ],
    "finance_investing": [
        {"type": "tip", "hook": "[X] money rules they don't teach in school", "format": "list_video"},
        {"type": "news", "hook": "This is happening to [X] and most people don't know", "format": "news_reaction"},
        {"type": "strategy", "hook": "How I made $[X] doing [Y] in [Z] months", "format": "case_study"},
        {"type": "warning", "hook": "STOP doing [X] with your money", "format": "talking_head"},
        {"type": "explainer", "hook": "What is [financial concept]? Explained in 60 seconds", "format": "educational"},
        {"type": "resource", "hook": "[X] free tools every investor should be using", "format": "roundup"},
    ],
    "food_recipes": [
        {"type": "recipe", "hook": "3-ingredient [dish] that actually tastes amazing", "format": "cooking_tutorial"},
        {"type": "hack", "hook": "I can't believe I didn't know this [cooking trick] sooner", "format": "hack_reveal"},
        {"type": "taste_test", "hook": "Testing viral [dish] — is it worth it?", "format": "reaction"},
        {"type": "comparison", "hook": "[Homemade] vs [Restaurant] — $[X] difference", "format": "side_by_side"},
        {"type": "weekly_prep", "hook": "My $[X] weekly meal prep for [diet type]", "format": "prep_walkthrough"},
        {"type": "review", "hook": "I tried [viral restaurant/recipe] so you don't have to", "format": "vlog"},
    ],
    "general": [
        {"type": "educational", "hook": "[X] things you didn't know about [topic]", "format": "list_video"},
        {"type": "story", "hook": "I tried [X] for 30 days — here's what happened", "format": "vlog"},
        {"type": "reaction", "hook": "Reacting to [viral trend/video]", "format": "duet_stitch"},
        {"type": "tips", "hook": "[X] [niche] tips that changed my life", "format": "talking_head"},
        {"type": "showcase", "hook": "Wait for it... [satisfying reveal]", "format": "short_clip"},
        {"type": "debate", "hook": "[Controversial opinion in niche] — fight me", "format": "opinion_video"},
    ],
}

# Posting time slots by platform
BEST_TIMES = {
    "tiktok": ["06:00", "09:00", "12:00", "15:00", "19:00", "21:00"],
    "youtube": ["08:00", "12:00", "16:00", "19:00"],
    "instagram": ["07:00", "11:00", "14:00", "19:00", "21:00"],
}

# Days of week performance multipliers (0=Monday, 6=Sunday)
DAY_WEIGHTS = {
    "tiktok": [0.85, 0.90, 1.0, 1.0, 1.1, 0.95, 0.90],
    "youtube": [0.80, 0.85, 0.90, 1.1, 1.15, 1.0, 0.90],
    "instagram": [0.85, 0.90, 0.95, 1.0, 1.1, 1.0, 0.85],
}


def generate_weekly_calendar(
    niche: str = "general",
    platforms: Optional[list[str]] = None,
    posts_per_day: int = 2,
    start_date: Optional[str] = None,
) -> dict:
    """Generate a 7-day content calendar.

    Args:
        niche: Content niche (matches keys in CONTENT_TEMPLATES)
        platforms: List of platforms (tiktok, youtube, instagram)
        posts_per_day: Posts per platform per day
        start_date: YYYY-MM-DD start date (defaults to tomorrow)

    Returns:
        dict with day-by-day schedule and content assignments
    """
    if platforms is None:
        platforms = ["tiktok", "youtube"]

    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
    else:
        start = datetime.utcnow() + timedelta(days=1)
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)

    templates = CONTENT_TEMPLATES.get(niche, CONTENT_TEMPLATES["general"])
    template_cycle = templates * ((7 * posts_per_day * len(platforms)) // len(templates) + 1)

    calendar = []
    template_idx = 0

    for day_offset in range(7):
        date = start + timedelta(days=day_offset)
        day_name = date.strftime("%A")
        date_str = date.strftime("%Y-%m-%d")
        weekday = date.weekday()

        day_posts = []
        for platform in platforms:
            times = BEST_TIMES.get(platform, ["12:00", "18:00"])
            weight = DAY_WEIGHTS.get(platform, [1.0] * 7)[weekday]
            post_times = times[:posts_per_day]

            for time_slot in post_times:
                template = template_cycle[template_idx % len(template_cycle)]
                template_idx += 1
                day_posts.append({
                    "platform": platform,
                    "date": date_str,
                    "day": day_name,
                    "time_utc": time_slot,
                    "performance_multiplier": round(weight, 2),
                    "content_type": template["type"],
                    "hook_template": template["hook"],
                    "format": template["format"],
                    "hashtag_reminder": f"Use 3-5 hashtags for {platform}",
                    "status": "scheduled",
                })

        calendar.append({
            "date": date_str,
            "day": day_name,
            "posts": sorted(day_posts, key=lambda p: p["time_utc"]),
            "total_posts": len(day_posts),
        })

    return {
        "niche": niche,
        "platforms": platforms,
        "start_date": start.strftime("%Y-%m-%d"),
        "end_date": (start + timedelta(days=6)).strftime("%Y-%m-%d"),
        "total_posts": 7 * posts_per_day * len(platforms),
        "calendar": calendar,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


def generate_monthly_calendar(
    niche: str = "general",
    platforms: Optional[list[str]] = None,
    posts_per_day: int = 2,
    start_date: Optional[str] = None,
) -> dict:
    """Generate a 30-day content calendar."""
    if platforms is None:
        platforms = ["tiktok", "youtube"]

    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
    else:
        start = datetime.utcnow() + timedelta(days=1)
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)

    templates = CONTENT_TEMPLATES.get(niche, CONTENT_TEMPLATES["general"])
    weekly_themes = _get_monthly_themes(niche)

    weeks = []
    for week_num in range(4):
        week_start = start + timedelta(days=week_num * 7)
        week_start_str = week_start.strftime("%Y-%m-%d")
        week = generate_weekly_calendar(
            niche=niche,
            platforms=platforms,
            posts_per_day=posts_per_day,
            start_date=week_start_str,
        )
        week["week_number"] = week_num + 1
        week["weekly_theme"] = weekly_themes[week_num] if week_num < len(weekly_themes) else "evergreen content"
        weeks.append(week)

    total_posts = 30 * posts_per_day * len(platforms)
    return {
        "niche": niche,
        "platforms": platforms,
        "start_date": start.strftime("%Y-%m-%d"),
        "end_date": (start + timedelta(days=29)).strftime("%Y-%m-%d"),
        "total_posts": total_posts,
        "weekly_themes": weekly_themes,
        "weeks": weeks,
        "monthly_goals": _monthly_goals(niche),
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


def _get_monthly_themes(niche: str) -> list[str]:
    themes = {
        "luxury_lifestyle": [
            "Week 1: Dream destinations & real estate",
            "Week 2: Ultimate car collection showcase",
            "Week 3: Luxury watches & fashion",
            "Week 4: Private jets & yachts — the lifestyle",
        ],
        "fitness_motivation": [
            "Week 1: Beginner mistakes & corrections",
            "Week 2: Advanced workout techniques",
            "Week 3: Nutrition & recovery science",
            "Week 4: Mental strength & discipline",
        ],
        "finance_investing": [
            "Week 1: Budgeting & debt elimination",
            "Week 2: Investing basics — stocks & ETFs",
            "Week 3: Passive income streams",
            "Week 4: Advanced strategies & case studies",
        ],
        "food_recipes": [
            "Week 1: 5-ingredient quick meals",
            "Week 2: Meal prep mastery",
            "Week 3: Restaurant recreations",
            "Week 4: Desserts & special occasions",
        ],
    }
    return themes.get(niche, [
        "Week 1: Educational foundation content",
        "Week 2: Inspiring showcase content",
        "Week 3: Practical tips & tutorials",
        "Week 4: Community engagement & Q&A",
    ])


def _monthly_goals(niche: str) -> list[str]:
    return [
        "Grow followers by 500-2,000",
        "Achieve at least 2 viral posts (10x average views)",
        "Test 3 different hook formats — identify best performer",
        "Build email list by 100+ subscribers",
        "Generate first $100-500 in affiliate revenue",
    ]
