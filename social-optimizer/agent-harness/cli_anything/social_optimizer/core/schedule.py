"""Posting schedule optimizer — best times by platform and timezone."""

from typing import Any, Dict, List, Optional


# Best posting windows (day: [hours in local timezone]) based on engagement studies
# Indexed 0=Mon ... 6=Sun, hours in 24h
BEST_TIMES: Dict[str, Dict[str, List[int]]] = {
    "tiktok": {
        "monday":    [6, 10, 22],
        "tuesday":   [2, 4, 9],
        "wednesday": [7, 8, 11],
        "thursday":  [9, 12, 19],
        "friday":    [5, 13, 15],
        "saturday":  [11, 19, 20],
        "sunday":    [7, 8, 16],
    },
    "youtube": {
        "monday":    [14, 17],
        "tuesday":   [14, 17],
        "wednesday": [14, 17],
        "thursday":  [14, 17],
        "friday":    [14, 17],
        "saturday":  [9, 11],
        "sunday":    [9, 11],
    },
    "instagram": {
        "monday":    [11, 14],
        "tuesday":   [8, 14, 17],
        "wednesday": [9, 11, 17],
        "thursday":  [8, 11, 17],
        "friday":    [5, 11, 14],
        "saturday":  [11, 20],
        "sunday":    [7, 8, 17],
    },
    "twitter": {
        "monday":    [8, 12],
        "tuesday":   [9, 12],
        "wednesday": [8, 12, 17],
        "thursday":  [8, 12],
        "friday":    [8, 12],
        "saturday":  [11, 14],
        "sunday":    [12, 17],
    },
    "facebook": {
        "monday":    [9, 13],
        "tuesday":   [9, 13],
        "wednesday": [9, 13, 17],
        "thursday":  [9, 13],
        "friday":    [9, 13],
        "saturday":  [12, 14],
        "sunday":    [12, 16],
    },
}

DAYS_ORDER = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def get_best_times(platform: str) -> Dict[str, List[str]]:
    """Return best posting windows for a platform."""
    platform = platform.lower()
    times = BEST_TIMES.get(platform)
    if not times:
        raise ValueError(f"No schedule data for platform '{platform}'.")

    result = {}
    for day, hours in times.items():
        result[day] = [f"{h:02d}:00" for h in hours]
    return result


def generate_schedule(
    platform: str,
    posts_per_day: int = 1,
    timezone: str = "US/Eastern",
) -> List[Dict[str, Any]]:
    """Generate a weekly posting schedule for a platform."""
    platform = platform.lower()
    times = BEST_TIMES.get(platform)
    if not times:
        raise ValueError(f"No schedule data for platform '{platform}'.")

    schedule = []
    for day in DAYS_ORDER:
        day_hours = times[day][:posts_per_day]
        for hour in day_hours:
            schedule.append({
                "day": day.capitalize(),
                "time": f"{hour:02d}:00",
                "timezone": timezone,
                "platform": platform,
                "post_type": _recommended_post_type(platform, day, hour),
            })

    return schedule


def _recommended_post_type(platform: str, day: str, hour: int) -> str:
    if platform == "tiktok":
        if hour < 7:
            return "Short viral clip (trending sound)"
        if hour < 12:
            return "Educational/value content"
        return "Entertainment/trending content"
    if platform == "youtube":
        if day in ("saturday", "sunday"):
            return "Long-form video (15-30 min)"
        return "Mid-length video (8-15 min) or YouTube Short"
    if platform == "instagram":
        if hour >= 17:
            return "Carousel post or Reel"
        return "Feed post or Story"
    return "Standard post"


def schedule_frequency_advice(platform: str) -> Dict[str, Any]:
    """Recommended posting frequency and strategy for a platform."""
    advice = {
        "tiktok": {
            "min_posts_per_day": 1,
            "optimal_posts_per_day": 3,
            "max_posts_per_day": 5,
            "weekly_target": "14-21 posts",
            "note": "Quantity matters on TikTok. Post at least once daily. 3× daily is the sweet spot for growth accounts.",
            "content_mix": ["50% trending hooks", "30% value/educational", "20% personal brand"],
        },
        "youtube": {
            "min_posts_per_day": 0,
            "optimal_posts_per_day": 1,
            "max_posts_per_day": 2,
            "weekly_target": "2-3 long-form + 3-5 Shorts",
            "note": "YouTube rewards consistency over quantity. 2-3 videos/week + daily Shorts is ideal.",
            "content_mix": ["60% evergreen SEO", "25% trending topics", "15% community/personal"],
        },
        "instagram": {
            "min_posts_per_day": 0,
            "optimal_posts_per_day": 1,
            "max_posts_per_day": 3,
            "weekly_target": "4-7 Reels + 2-3 carousels + daily Stories",
            "note": "Reels are #1 growth driver. Post Stories daily to stay top of feed.",
            "content_mix": ["50% Reels", "30% Carousels", "20% Static posts"],
        },
        "twitter": {
            "min_posts_per_day": 3,
            "optimal_posts_per_day": 8,
            "max_posts_per_day": 20,
            "weekly_target": "50-80 tweets + 2-3 threads",
            "note": "Twitter/X rewards high volume. Threads are the #1 follow driver.",
            "content_mix": ["40% value tweets", "30% threads", "20% replies", "10% reposts"],
        },
        "facebook": {
            "min_posts_per_day": 0,
            "optimal_posts_per_day": 1,
            "max_posts_per_day": 2,
            "weekly_target": "5-7 posts",
            "note": "Facebook organic reach is low — focus on Groups and boosted Reels.",
            "content_mix": ["40% video/Reels", "30% link posts", "30% images"],
        },
    }
    result = advice.get(platform.lower())
    if not result:
        raise ValueError(f"No frequency data for platform '{platform}'.")
    result["platform"] = platform.lower()
    return result
