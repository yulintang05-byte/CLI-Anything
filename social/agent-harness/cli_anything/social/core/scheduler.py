"""Content scheduler — posting calendars, frequency analysis, content mix.

Generates data-driven content schedules tailored to each platform's
algorithm and the account's niche. All outputs are JSON-serialisable
for integration with scheduling tools (Buffer, Later, Publer, etc.).
"""

import datetime
import calendar
from typing import Optional

from cli_anything.social.core.accounts import (
    PLATFORM_BENCHMARKS,
    _POSTING_TIMES,
    _BEST_DAYS,
    NICHE_KEYWORDS,
)

# ── Content type distributions by niche ──────────────────────────────────────

CONTENT_MIX: dict[str, dict[str, dict[str, int]]] = {
    "fitness": {
        "tiktok": {
            "workout_clip": 30,
            "transformation": 20,
            "nutrition_tip": 20,
            "motivation": 15,
            "Q&A_or_collab": 15,
        },
        "instagram": {
            "reel_workout": 35,
            "carousel_tips": 25,
            "story_poll": 20,
            "transformation_post": 20,
        },
        "youtube": {
            "full_workout": 40,
            "shorts_tip": 30,
            "nutrition_video": 20,
            "transformation_story": 10,
        },
    },
    "finance": {
        "tiktok": {
            "money_tip": 35,
            "market_update": 20,
            "side_hustle_idea": 25,
            "personal_story": 10,
            "myth_debunk": 10,
        },
        "instagram": {
            "infographic_carousel": 40,
            "reel_tip": 30,
            "story_quiz": 15,
            "quote_post": 15,
        },
        "youtube": {
            "deep_dive_explainer": 35,
            "shorts_fact": 30,
            "portfolio_update": 20,
            "interview": 15,
        },
    },
    "motivation": {
        "tiktok": {
            "speech_edit": 40,
            "quote_visual": 25,
            "success_story": 20,
            "daily_challenge": 15,
        },
        "instagram": {
            "quote_post": 40,
            "reel_speech": 30,
            "story_affirmation": 20,
            "carousel_tips": 10,
        },
        "youtube": {
            "motivational_compilation": 40,
            "biography_story": 30,
            "shorts_quote": 30,
        },
    },
    "beauty": {
        "tiktok": {
            "tutorial": 35,
            "product_review": 25,
            "GRWM": 20,
            "transformation": 15,
            "dupe_video": 5,
        },
        "instagram": {
            "reel_tutorial": 35,
            "product_flatlay": 25,
            "story_swipe_up": 20,
            "GRWM_reel": 20,
        },
        "youtube": {
            "full_tutorial": 40,
            "haul_video": 25,
            "skincare_routine": 20,
            "shorts_hack": 15,
        },
    },
    "food": {
        "tiktok": {
            "recipe_video": 50,
            "food_hack": 20,
            "taste_test": 15,
            "asmr_cooking": 15,
        },
        "instagram": {
            "reel_recipe": 45,
            "photo_food": 25,
            "story_poll": 15,
            "carousel_recipe": 15,
        },
        "youtube": {
            "full_recipe": 40,
            "shorts_hack": 30,
            "mukbang": 15,
            "restaurant_review": 15,
        },
    },
    "travel": {
        "tiktok": {
            "destination_highlight": 35,
            "travel_hack": 25,
            "day_in_destination": 20,
            "budget_tip": 20,
        },
        "instagram": {
            "location_reel": 40,
            "travel_carousel": 30,
            "story_QnA": 15,
            "itinerary_post": 15,
        },
        "youtube": {
            "full_vlog": 40,
            "destination_guide": 30,
            "shorts_tip": 20,
            "travel_mistake": 10,
        },
    },
}

_DEFAULT_MIX = {
    "original_content": 40,
    "curated_content": 30,
    "engagement_content": 20,
    "promotional_content": 10,
}

# ── Content hook templates ────────────────────────────────────────────────────

HOOK_TEMPLATES: dict[str, list[str]] = {
    "curiosity": [
        "You won't believe what {topic} does to {outcome}...",
        "Nobody talks about this {niche} secret...",
        "I tested {topic} for 30 days — here's what happened",
        "The dark side of {topic} nobody tells you",
        "This {niche} hack changed everything for me",
    ],
    "value": [
        "{N} {niche} tips that actually work",
        "How to {outcome} in {timeframe}",
        "Stop doing this in {niche} — do this instead",
        "The {niche} formula that got me {result}",
        "Everything you need to know about {topic} in 60 seconds",
    ],
    "social_proof": [
        "How I grew from {start} to {end} in {timeframe}",
        "{N} things I wish I knew before starting {niche}",
        "I made ${amount} from {niche} — here's exactly how",
        "Why I quit {topic} after {timeframe} (and what I do instead)",
    ],
    "controversy": [
        "{Popular belief} is a lie. Here's the truth about {topic}",
        "Unpopular opinion: {contrarian take on niche}",
        "I tried every {niche} method — only {N} actually work",
        "The {niche} advice that's secretly making you worse",
    ],
}

# ── Posting frequency data ────────────────────────────────────────────────────

_FREQ_ADVICE: dict[str, dict] = {
    "tiktok": {
        "starter":    {"posts_per_day": 3, "note": "Post 3x/day for first 30 days — volume is king"},
        "growing":    {"posts_per_day": 2, "note": "2x/day; prioritise quality over volume now"},
        "established":{"posts_per_day": 1, "note": "1-2x/day; focus on evergreen + trending mix"},
    },
    "instagram": {
        "starter":    {"posts_per_day": 1, "stories_per_day": 3,
                       "note": "1 Reel + 3 Stories/day; Stories are free reach"},
        "growing":    {"posts_per_day": 1, "stories_per_day": 5,
                       "note": "1 Reel + 5 Stories; start Carousels (high saves)"},
        "established":{"posts_per_day": 1, "stories_per_day": 7,
                       "note": "Reel + Carousel rotation + daily Stories"},
    },
    "youtube": {
        "starter":    {"posts_per_week": 3, "note": "3 Shorts/week + 1 long-form to build catalog"},
        "growing":    {"posts_per_week": 4, "note": "2 long-form + 2 Shorts/week"},
        "established":{"posts_per_week": 2, "note": "2 polished long-form/week; quality over quantity"},
    },
}


# ── Core functions ────────────────────────────────────────────────────────────

def create_content_calendar(
    platform: str,
    niche: str,
    weeks: int = 4,
    posts_per_day: int = 0,
    start_date: str = "",
) -> dict:
    """Generate a content calendar with specific post ideas.

    Args:
        platform: 'tiktok', 'youtube', or 'instagram'.
        niche: Content niche.
        weeks: Number of weeks to plan (1-12).
        posts_per_day: Override default posting frequency.
        start_date: ISO date string (YYYY-MM-DD). Defaults to today.

    Returns:
        Dict with weekly schedule, post ideas, and hashtag sets.
    """
    weeks = max(1, min(weeks, 12))

    if start_date:
        try:
            start = datetime.date.fromisoformat(start_date)
        except ValueError:
            start = datetime.date.today()
    else:
        start = datetime.date.today()

    # Determine frequency
    bench = PLATFORM_BENCHMARKS.get(platform, {})
    default_min, default_max = bench.get("daily_post_target", (1, 2))
    freq = posts_per_day if posts_per_day > 0 else default_min

    # Get content mix for this niche+platform
    mix = (
        CONTENT_MIX.get(niche.lower(), {}).get(platform, {})
        or _DEFAULT_MIX
    )
    content_types = list(mix.keys())
    weights = list(mix.values())

    # Best posting times
    times_data = _POSTING_TIMES.get(platform, {})
    best_times = times_data.get("US", times_data.get("global", ["12:00 PM"]))
    best_days_set = set(_BEST_DAYS.get(platform, []))

    # Hashtag sets for rotation
    hashtag_sets = _generate_hashtag_sets(niche, platform, count=3)

    # Generate weeks
    weekly_plan = []
    total_posts = 0
    current_date = start

    for week_num in range(1, weeks + 1):
        week_posts = []
        week_start = current_date

        for day_offset in range(7):
            day = current_date + datetime.timedelta(days=day_offset)
            day_name = calendar.day_name[day.weekday()]
            is_best_day = day_name in best_days_set

            day_posts = []
            posts_today = freq + (1 if is_best_day else 0)

            for post_num in range(posts_today):
                # Rotate content types
                ct_index = total_posts % len(content_types)
                content_type = content_types[ct_index]

                # Rotate hashtag sets
                hashtag_set = hashtag_sets[total_posts % len(hashtag_sets)]

                # Pick a hook template
                hooks = HOOK_TEMPLATES.get("value", [])
                hook = hooks[total_posts % len(hooks)]

                # Pick posting time
                post_time = best_times[post_num % len(best_times)]

                day_posts.append({
                    "post_number": total_posts + 1,
                    "content_type": content_type.replace("_", " ").title(),
                    "hook_template": hook,
                    "post_time": post_time,
                    "hashtag_set": f"Set {(total_posts % len(hashtag_sets)) + 1}",
                    "hashtags": hashtag_set,
                    "notes": _content_type_notes(content_type, niche, platform),
                })
                total_posts += 1

            if day_posts:
                week_posts.append({
                    "date": day.isoformat(),
                    "day": day_name,
                    "is_peak_day": is_best_day,
                    "posts": day_posts,
                })

        current_date = current_date + datetime.timedelta(days=7)

        weekly_plan.append({
            "week": week_num,
            "week_start": week_start.isoformat(),
            "week_end": (week_start + datetime.timedelta(days=6)).isoformat(),
            "post_count": sum(len(d["posts"]) for d in week_posts),
            "theme": _week_theme(week_num, niche),
            "days": week_posts,
        })

    return {
        "platform": platform,
        "niche": niche,
        "start_date": start.isoformat(),
        "end_date": (start + datetime.timedelta(weeks=weeks)).isoformat(),
        "total_weeks": weeks,
        "total_posts": total_posts,
        "posts_per_day": freq,
        "hashtag_sets": {
            f"Set {i+1}": tags for i, tags in enumerate(hashtag_sets)
        },
        "content_mix": mix,
        "weeks": weekly_plan,
        "generated_at": _now_iso(),
    }


def get_posting_frequency(
    platform: str,
    account_stage: str = "starter",
) -> dict:
    """Return posting frequency advice for an account stage.

    Args:
        platform: 'tiktok', 'youtube', or 'instagram'.
        account_stage: 'starter' (<1K), 'growing' (1K-50K), 'established' (50K+).

    Returns:
        Dict with frequency recommendation and rationale.
    """
    platform_freqs = _FREQ_ADVICE.get(platform, _FREQ_ADVICE.get("tiktok", {}))
    stage_data = platform_freqs.get(account_stage, platform_freqs.get("starter", {}))

    frequency_rules = {
        "tiktok": (
            "TikTok rewards volume in the early growth phase. The algorithm "
            "tests each video independently, so more posts = more chances to "
            "go viral. Reduce frequency only once you find your winning format."
        ),
        "youtube": (
            "YouTube rewards consistency over volume. A weekly schedule that "
            "never misses beats daily uploads that eventually stop. "
            "Shorts can fill the gaps between long-form videos."
        ),
        "instagram": (
            "Instagram's algorithm heavily weights saves and shares over likes. "
            "Stories keep you top-of-mind daily while Reels drive discovery. "
            "Aim for 1 Reel + daily Stories minimum."
        ),
    }

    return {
        "platform": platform,
        "account_stage": account_stage,
        "recommendation": stage_data,
        "rationale": frequency_rules.get(platform, ""),
        "burnout_prevention": [
            "Batch-create content 1-2 weeks ahead to avoid posting gaps.",
            "Build a content bank of 30+ pieces before you start posting.",
            "Repurpose: 1 long-form video → 5 Shorts/Reels → 10 quote posts.",
            "Hire an editor once you can afford it — most creators burn out on editing.",
        ],
    }


def get_content_hooks(
    niche: str,
    hook_type: str = "all",
    count: int = 10,
) -> dict:
    """Generate content hook templates for a specific niche.

    Args:
        niche: Content niche.
        hook_type: 'curiosity', 'value', 'social_proof', 'controversy', or 'all'.
        count: Number of hooks to return.

    Returns:
        Dict with hooks personalised to the niche.
    """
    niche_kw = NICHE_KEYWORDS.get(niche.lower(), [niche])
    topic = niche_kw[0] if niche_kw else niche

    if hook_type == "all":
        all_hooks = []
        for htype, templates in HOOK_TEMPLATES.items():
            for tmpl in templates:
                personalised = _personalise_hook(tmpl, niche, topic)
                all_hooks.append({"type": htype, "hook": personalised})
    else:
        templates = HOOK_TEMPLATES.get(hook_type, HOOK_TEMPLATES["value"])
        all_hooks = [
            {"type": hook_type, "hook": _personalise_hook(t, niche, topic)}
            for t in templates
        ]

    return {
        "niche": niche,
        "hook_type": hook_type,
        "hooks": all_hooks[:count],
        "usage_tips": [
            "The hook is the first 0.5-1.5 seconds of your video — cut to it immediately.",
            "Test 2 different hooks per week and double-down on the winner.",
            "Questions and numbers in hooks increase watch time by 20-30%.",
            "Curiosity hooks work best for broad audiences; value hooks for niche audiences.",
        ],
    }


def get_content_repurposing_plan(
    source_platform: str,
    target_platforms: list[str],
    niche: str,
) -> dict:
    """Generate a repurposing strategy to maximise content across platforms.

    Args:
        source_platform: Where you create original content.
        target_platforms: Platforms to repurpose to.
        niche: Content niche.

    Returns:
        Dict with per-platform repurposing instructions and format requirements.
    """
    repurpose_maps: dict[str, dict[str, dict]] = {
        "tiktok": {
            "instagram": {
                "format": "Remove TikTok watermark → upload as Reel",
                "edits": ["Crop to 9:16 if needed", "Add IG-specific hashtags", "Adjust caption"],
                "tool": "SnapTik.app to download without watermark",
                "delay": "Post 24-48h after TikTok to avoid duplicate content penalty",
            },
            "youtube": {
                "format": "Upload as YouTube Short (vertical, <60s)",
                "edits": ["Add YouTube end card", "Change hashtags to YouTube tags"],
                "tool": "yt-dlp or direct export",
                "delay": "Post same day or next day",
            },
            "twitter": {
                "format": "Download video → upload natively on Twitter/X",
                "edits": ["Trim to <2:20", "Add text thread with key points"],
                "tool": "Twitter media upload",
                "delay": "Post same day",
            },
        },
        "youtube": {
            "tiktok": {
                "format": "Edit to vertical 9:16, <60s highlights",
                "edits": ["Add hook in first frame", "Add trending TikTok audio overlay"],
                "tool": "CapCut for vertical reformat",
                "delay": "Post same day (Shorts feed is separate algorithm)",
            },
            "instagram": {
                "format": "Vertical recut → Reel (30-90s) or IGTV for longer",
                "edits": ["Add IG captions overlay", "IG-specific hashtags in caption"],
                "tool": "CapCut, InShot, or Premiere",
                "delay": "Post 1-2 days after YouTube",
            },
        },
        "instagram": {
            "tiktok": {
                "format": "Download Reel → remove IG watermark → post on TikTok",
                "edits": ["Add trending TikTok audio", "Adjust caption to TikTok style"],
                "tool": "Regrann or screen record",
                "delay": "24h after Instagram",
            },
            "youtube": {
                "format": "Upload as YouTube Short if <60s",
                "edits": ["Add YouTube-specific tags", "Adjust description for SEO"],
                "tool": "Direct upload",
                "delay": "Same day",
            },
        },
    }

    source_map = repurpose_maps.get(source_platform, {})
    plans = []
    for target in target_platforms:
        if target != source_platform:
            plan = source_map.get(target, {
                "format": f"Adapt {source_platform} content for {target}",
                "edits": ["Adjust format to platform specs", "Rewrite caption"],
                "tool": "Video editor of choice",
                "delay": "24-48h after original post",
            })
            plans.append({
                "source": source_platform,
                "target": target,
                **plan,
            })

    return {
        "source_platform": source_platform,
        "niche": niche,
        "repurposing_plans": plans,
        "roi_note": (
            "One piece of content → 3-5 platforms = 3-5x reach with ~20% extra effort. "
            "Batch repurposing (do all platforms at once) saves 60% of the time vs sequential."
        ),
        "generated_at": _now_iso(),
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _generate_hashtag_sets(
    niche: str,
    platform: str,
    count: int = 3,
) -> list[list[str]]:
    """Generate rotating hashtag sets for a niche and platform."""
    from cli_anything.social.core.accounts import NICHE_KEYWORDS, PLATFORM_BENCHMARKS

    niche_kw = NICHE_KEYWORDS.get(niche.lower(), [niche])
    bench = PLATFORM_BENCHMARKS.get(platform, {})
    max_tags = bench.get("max_hashtags_per_post", 5)

    niche_tags = [f"#{kw.replace(' ', '')}" for kw in niche_kw]
    broad_tiktok = ["#fyp", "#foryou", "#viral", "#trending", "#foryoupage"]
    broad_yt = ["#shorts", "#youtube", "#viral"]
    broad_ig = ["#explore", "#reels", "#viral", "#trending", "#instagood"]

    broad = (
        broad_tiktok if platform == "tiktok"
        else broad_yt if platform == "youtube"
        else broad_ig
    )

    sets = []
    for i in range(count):
        tag_set = niche_tags[i::count][:max_tags - 2] + broad[:2]
        sets.append(tag_set)

    return sets


def _content_type_notes(
    content_type: str,
    niche: str,
    platform: str,
) -> str:
    notes_map = {
        "workout_clip": f"30-45s clip showcasing a {niche} exercise with form cues. Use energetic music.",
        "tutorial": f"Step-by-step {niche} tutorial. Hook: 'I'll show you exactly how to...'",
        "motivation": f"20s motivational edit with speech + {niche} visuals. High energy music.",
        "product_review": f"Honest {niche} product review. Show before/after or unboxing.",
        "money_tip": f"Single {niche} tip in 15-30s. Start with shocking stat.",
        "recipe_video": f"30-45s recipe from start to finish. ASMR audio + satisfying cuts.",
        "destination_highlight": f"30-60s destination montage. Use cinematic B-roll + dreamy music.",
        "quote_visual": f"Quote graphic with voice-over or text overlay. 15-20s max.",
    }
    return notes_map.get(content_type, f"Create engaging {niche} {content_type.replace('_', ' ')} content.")


def _week_theme(week_num: int, niche: str) -> str:
    themes = [
        f"Foundation — introduce your {niche} perspective",
        f"Education — teach core {niche} concepts",
        f"Social proof — share results and stories",
        f"Engagement — polls, Q&A, challenges",
        f"Monetisation — soft launch affiliate/product",
        f"Viral push — high-energy trending content",
    ]
    return themes[(week_num - 1) % len(themes)]


def _personalise_hook(template: str, niche: str, topic: str) -> str:
    replacements = {
        "{niche}": niche,
        "{topic}": topic,
        "{outcome}": f"your {niche} results",
        "{timeframe}": "30 days",
        "{N}": "5",
        "{result}": "10K followers",
        "{start}": "0",
        "{end}": "10K",
        "{amount}": "1,000",
    }
    result = template
    for placeholder, value in replacements.items():
        result = result.replace(placeholder, value)
    return result


def _now_iso() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
