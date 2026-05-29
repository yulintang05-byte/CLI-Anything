"""Content calendar and posting schedule optimizer."""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from cli_anything.social_trends.core.store import Store
from cli_anything.social_trends.core.accounts import _PLATFORM_BEST_TIMES, _POSTING_FREQUENCY
from cli_anything.social_trends.core.theme_pages import NICHE_DATA, _match_niche

_CONTENT_TYPES: Dict[str, List[str]] = {
    "fitness":      ["Workout tutorial", "Transformation reveal", "Nutrition tip", "Motivation clip", "Q&A"],
    "finance":      ["Money tip", "Investment breakdown", "Budget walkthrough", "Income update", "News reaction"],
    "luxury":       ["Lifestyle tour", "Product unboxing", "Travel reel", "POV content", "Behind the scenes"],
    "travel":       ["Destination guide", "Budget breakdown", "Hidden gem", "Travel hack", "Day vlog"],
    "food":         ["Quick recipe", "ASMR cook", "Restaurant review", "Meal prep", "Viral recreation"],
    "gaming":       ["Highlight clip", "Tutorial", "Setup tour", "Review", "World record attempt"],
    "crypto":       ["Market analysis", "Coin spotlight", "News reaction", "Beginner guide", "Portfolio update"],
    "fashion":      ["Outfit of the day", "Haul", "Style tip", "Thrift flip", "Lookbook"],
    "motivational": ["Motivation speech", "Daily quote", "Book summary", "Success story", "Morning routine"],
    "sports":       ["Highlight reel", "Top 10", "Player news", "Match reaction", "Training tip"],
}

_FORMATS: Dict[str, List[str]] = {
    "tiktok":    ["60s video", "30s video", "15s clip", "TikTok Live", "Stitch/Duet"],
    "youtube":   ["Long-form (10-20min)", "YouTube Short", "Live stream", "Community post"],
    "instagram": ["Reel (30-60s)", "Story", "Carousel post", "Feed photo", "Live"],
}

_DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def optimize_schedule(store: Store, account_id: str, platform: Optional[str] = None) -> Dict[str, Any]:
    account = store.get_account(account_id)
    plat = (platform or account.get("platform", "tiktok")).lower()
    niche = account.get("niche", "motivational")

    best_times = _PLATFORM_BEST_TIMES.get(plat, _PLATFORM_BEST_TIMES["tiktok"])
    frequency = _POSTING_FREQUENCY.get(plat, _POSTING_FREQUENCY["tiktok"])

    schedule = {
        "account_id": account_id,
        "platform": plat,
        "niche": niche,
        "posting_frequency": frequency,
        "weekly_schedule": {day: times for day, times in best_times.items()},
        "best_days": ["Tuesday", "Thursday", "Friday"] if plat == "tiktok" else ["Wednesday", "Thursday"],
        "timezone_note": "All times in EST. Adjust for your audience's primary timezone.",
        "algorithm_tips": [
            "Post at peak times but prioritize consistency over perfection",
            "Never go more than 48 hours without posting",
            "Engage with comments within first 60 minutes (boosts reach by 30-50%)",
            f"Optimal cadence: {frequency['optimal']}",
            "Use the platform's latest features (duets, stitches, remix) for extra push",
        ],
        "content_batch_tip": "Film 5-7 videos in one session, then schedule throughout the week.",
    }

    store.update_account(account_id, {"posting_schedule": schedule["weekly_schedule"]})
    store.save()
    return schedule


def generate_calendar(
    store: Store,
    account_id: str,
    days: int = 7,
) -> List[Dict[str, Any]]:
    account = store.get_account(account_id)
    niche = account.get("niche", "motivational")
    platform = account.get("platform", "tiktok")

    niche_key = _match_niche(niche)
    content_types = _CONTENT_TYPES.get(niche_key, _CONTENT_TYPES["motivational"])
    formats = _FORMATS.get(platform, _FORMATS["tiktok"])
    best_times = _PLATFORM_BEST_TIMES.get(platform, _PLATFORM_BEST_TIMES["tiktok"])
    niche_data = NICHE_DATA.get(niche_key, {})

    # Pull hashtags from store if available
    hashtag_sets = ["#fyp #viral #foryou", "#trending #explore", "#niche #community"]
    if store.hashtags:
        all_tags = [h["tag"] for h in store.hashtags[:20]]
        if all_tags:
            chunk = len(all_tags) // 3 or 1
            hashtag_sets = [
                " ".join(all_tags[:chunk]),
                " ".join(all_tags[chunk:chunk*2]),
                " ".join(all_tags[chunk*2:]),
            ]

    calendar: List[Dict[str, Any]] = []
    base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    for i in range(days):
        day_date = base_date + timedelta(days=i)
        day_name = _DAYS_OF_WEEK[day_date.weekday()]
        times = best_times.get(day_name.lower(), ["12:00 PM"])

        content_type = content_types[i % len(content_types)]
        fmt = formats[i % len(formats)]
        hashtag_set = hashtag_sets[i % len(hashtag_sets)]

        posts_today = []
        for j, post_time in enumerate(times[:2]):  # max 2 per day in calendar
            hook_ideas = niche_data.get("best_content_formats", [content_type])
            hook = hook_ideas[j % len(hook_ideas)] if hook_ideas else content_type

            posts_today.append({
                "post_number": j + 1,
                "time": post_time,
                "content_type": content_type,
                "format": fmt,
                "hook_idea": hook,
                "hashtags": hashtag_set,
                "cta": "Follow for more" if j == 0 else "Comment your thoughts",
                "trending_audio_tip": "Check trending audio in app and use within 48h of peak",
            })

        calendar.append({
            "date": day_date.strftime("%Y-%m-%d"),
            "day": day_name,
            "platform": platform,
            "posts": posts_today,
        })

    return calendar


def export_schedule(store: Store, account_id: str, path: str) -> Dict[str, Any]:
    calendar = generate_calendar(store, account_id, days=30)
    schedule = optimize_schedule(store, account_id)
    data = {
        "account_id": account_id,
        "schedule": schedule,
        "calendar": calendar,
        "exported_at": datetime.now().isoformat(),
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    return {"success": True, "path": path, "days": len(calendar)}
