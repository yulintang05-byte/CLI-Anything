"""Account optimizer — posting schedule, profile audit, and content calendar."""

from typing import Optional
import datetime


# ── Posting time recommendations ─────────────────────────────────


_OPTIMAL_TIMES: dict[str, dict[str, list]] = {
    "tiktok": {
        "monday":    ["6:00 AM", "10:00 AM", "10:00 PM"],
        "tuesday":   ["2:00 AM", "4:00 AM", "9:00 AM"],
        "wednesday": ["7:00 AM", "8:00 AM", "11:00 PM"],
        "thursday":  ["9:00 AM", "12:00 PM", "7:00 PM"],
        "friday":    ["5:00 AM", "1:00 PM", "3:00 PM"],
        "saturday":  ["11:00 AM", "7:00 PM", "8:00 PM"],
        "sunday":    ["7:00 AM", "8:00 AM", "4:00 PM"],
    },
    "instagram": {
        "monday":    ["6:00 AM", "12:00 PM", "6:00 PM"],
        "tuesday":   ["8:00 AM", "2:00 PM", "6:00 PM"],
        "wednesday": ["9:00 AM", "11:00 AM", "5:00 PM"],
        "thursday":  ["7:00 AM", "12:00 PM", "5:00 PM"],
        "friday":    ["7:00 AM", "10:00 AM", "5:00 PM"],
        "saturday":  ["9:00 AM", "12:00 PM", "2:00 PM"],
        "sunday":    ["10:00 AM", "1:00 PM", "5:00 PM"],
    },
    "youtube": {
        "monday":    ["2:00 PM", "3:00 PM", "4:00 PM"],
        "tuesday":   ["2:00 PM", "3:00 PM", "4:00 PM"],
        "wednesday": ["2:00 PM", "4:00 PM", "5:00 PM"],
        "thursday":  ["2:00 PM", "4:00 PM", "5:00 PM"],
        "friday":    ["12:00 PM", "3:00 PM", "4:00 PM"],
        "saturday":  ["9:00 AM", "11:00 AM", "1:00 PM"],
        "sunday":    ["9:00 AM", "11:00 AM", "1:00 PM"],
    },
}

_POSTING_FREQUENCY: dict[str, dict[str, str]] = {
    "tiktok": {
        "minimum":  "1 post/day",
        "optimal":  "3–5 posts/day",
        "maximum":  "8 posts/day",
        "note": "TikTok rewards consistency more than any platform. Volume matters.",
    },
    "instagram": {
        "minimum":  "3 posts/week (feed) + 5 Stories/day",
        "optimal":  "1 feed post/day + 10 Stories/day + 1 Reel/day",
        "maximum":  "3 feed posts/day",
        "note": "Reels get 2–3x more reach than static posts — prioritize video.",
    },
    "youtube": {
        "minimum":  "1 video/week",
        "optimal":  "2 videos/week (long-form) + 3 Shorts/week",
        "maximum":  "1 video/day",
        "note": "Consistency > volume on YouTube. Quality long-form drives subs.",
    },
    "youtube_shorts": {
        "minimum":  "3 Shorts/week",
        "optimal":  "1–3 Shorts/day",
        "maximum":  "5 Shorts/day",
        "note": "Shorts are separate from main channel algorithm — post independently.",
    },
}


def get_optimal_times(platform: str, timezone: str = "EST") -> dict:
    schedule = _OPTIMAL_TIMES.get(platform.lower())
    if not schedule:
        return {"error": f"Unknown platform '{platform}'"}
    return {
        "platform": platform,
        "timezone": timezone,
        "schedule": schedule,
        "note": f"Times shown in {timezone}. Convert to your local timezone.",
    }


def get_posting_frequency(platform: str) -> dict:
    freq = _POSTING_FREQUENCY.get(platform.lower())
    if not freq:
        return {"error": f"Unknown platform '{platform}'"}
    return {"platform": platform, **freq}


# ── Profile optimization checklist ───────────────────────────────


_PROFILE_CHECKLIST: dict[str, list[dict]] = {
    "tiktok": [
        {"item": "Username", "action": "Keep it short (<15 chars), memorable, and niche-related"},
        {"item": "Profile photo", "action": "Clear face photo or niche-relevant logo (high contrast)"},
        {"item": "Bio", "action": "80 chars max: who you are + value prop + CTA (e.g. 'Follow for daily finance tips')"},
        {"item": "Link in bio", "action": "Use Linktree or Beacons to aggregate all links (Instagram, YouTube, etc.)"},
        {"item": "Category", "action": "Set your creator category in Settings > Account > Switch to Creator Account"},
        {"item": "Email", "action": "Add business email for brand deals via Settings > Creator Tools"},
        {"item": "Pinned videos", "action": "Pin your 3 best-performing or most representative videos"},
        {"item": "Creator tools", "action": "Enable Creator Analytics, Creator Marketplace, and TikTok LIVE"},
        {"item": "Series", "action": "Group related content in Series for algorithm clustering"},
        {"item": "Stitch/Duet permissions", "action": "Enable to allow organic UGC and discovery"},
    ],
    "instagram": [
        {"item": "Username", "action": "Match your TikTok handle for cross-platform discoverability"},
        {"item": "Profile photo", "action": "Same as TikTok for brand consistency"},
        {"item": "Display name", "action": "Include niche keyword (e.g. 'John | Finance Tips')"},
        {"item": "Bio", "action": "150 chars: niche + social proof + CTA. Use emojis sparingly for visual breaks."},
        {"item": "Link in bio", "action": "Primary link + Linktree/Beacons for multiple destinations"},
        {"item": "Business account", "action": "Switch to Professional Account for analytics and contact buttons"},
        {"item": "Story Highlights", "action": "Create 5–7 branded Highlights (Best Of, Tips, FAQs, Collabs, etc.)"},
        {"item": "Grid aesthetic", "action": "First 9 posts should establish visual identity — use consistent filter/color"},
        {"item": "Contact info", "action": "Add email and phone for brand partnerships"},
        {"item": "Category label", "action": "Set to your niche category under Edit Profile > Category"},
    ],
    "youtube": [
        {"item": "Channel name", "action": "Match cross-platform handle. Can include niche keyword."},
        {"item": "Profile photo", "action": "800x800px minimum. Recognizable at small sizes."},
        {"item": "Banner", "action": "2560x1440px. Show posting schedule and what channel is about."},
        {"item": "Channel description", "action": "1000 chars: what you cover, posting frequency, subscribe CTA. Include keywords."},
        {"item": "Channel URL", "action": "Claim custom URL once eligible (500+ subs + 30+ days old)"},
        {"item": "Featured sections", "action": "Set up: Trailer for new visitors, Popular Uploads, Playlists"},
        {"item": "Channel trailer", "action": "60–90 second video explaining channel value. Hook in first 5 seconds."},
        {"item": "Playlists", "action": "Group videos by topic for watch time sessions and SEO"},
        {"item": "End screens", "action": "Add end screens to every video linking to next video or subscribe"},
        {"item": "Watermark", "action": "Add subscribe watermark to all videos via Customization > Branding"},
    ],
}


def audit_profile(platform: str) -> list[dict]:
    """Return full profile optimization checklist for a platform."""
    checklist = _PROFILE_CHECKLIST.get(platform.lower())
    if not checklist:
        return [{"error": f"Unknown platform '{platform}'"}]
    return checklist


# ── Content calendar generator ────────────────────────────────────


def generate_content_calendar(
    niche: str,
    platforms: list[str],
    days: int = 7,
    start_date: Optional[str] = None,
) -> list[dict]:
    """Generate a 7-day content calendar with post ideas per platform."""
    if start_date:
        try:
            start = datetime.date.fromisoformat(start_date)
        except ValueError:
            start = datetime.date.today()
    else:
        start = datetime.date.today()

    content_types = _get_content_types(niche)
    calendar = []

    for day_offset in range(days):
        date = start + datetime.timedelta(days=day_offset)
        weekday = date.strftime("%A").lower()
        day_plan = {
            "date": str(date),
            "weekday": weekday.capitalize(),
            "posts": [],
        }

        for platform in platforms:
            times = _OPTIMAL_TIMES.get(platform.lower(), {}).get(weekday, ["12:00 PM"])
            post_time = times[0] if times else "12:00 PM"
            content_idea = content_types[(day_offset * len(platforms) + platforms.index(platform)) % len(content_types)]

            day_plan["posts"].append({
                "platform": platform,
                "time": post_time,
                "content_type": content_idea["type"],
                "idea": content_idea["idea"],
                "hashtag_strategy": content_idea.get("hashtags", "Use niche + trending tags"),
            })

        calendar.append(day_plan)

    return calendar


def _get_content_types(niche: str) -> list[dict]:
    """Return a rotation of content types/ideas for a niche."""
    base = [
        {"type": "Educational", "idea": f"3 things most {niche} beginners get wrong", "hashtags": f"#{niche}tips #{niche}101"},
        {"type": "Trending audio", "idea": f"Use viral sound with {niche} context", "hashtags": f"#fyp #{niche}"},
        {"type": "Behind the scenes", "idea": f"Day in the life as a {niche} creator", "hashtags": f"#{niche}lifestyle #dayinthelife"},
        {"type": "Tutorial", "idea": f"Step-by-step {niche} how-to (under 60s)", "hashtags": f"#{niche}tutorial #howto"},
        {"type": "Relatable", "idea": f"{niche} problems only real fans understand", "hashtags": f"#{niche}community #relatable"},
        {"type": "Opinion/Hot take", "idea": f"Controversial {niche} opinion (engagement bait)", "hashtags": f"#{niche} #hottake"},
        {"type": "Transformation", "idea": f"Before vs. After in {niche}", "hashtags": f"#{niche}transformation #glow"},
    ]
    return base


# ── Growth rate calculator ────────────────────────────────────────


def calculate_growth_rate(
    start_followers: int,
    end_followers: int,
    days: int,
) -> dict:
    """Calculate follower growth metrics."""
    if days <= 0:
        return {"error": "days must be positive"}
    gained = end_followers - start_followers
    rate_per_day = gained / days
    rate_percent = (gained / max(start_followers, 1)) * 100
    days_to_10k = None
    if end_followers < 10_000 and rate_per_day > 0:
        days_to_10k = round((10_000 - end_followers) / rate_per_day)
    days_to_100k = None
    if end_followers < 100_000 and rate_per_day > 0:
        days_to_100k = round((100_000 - end_followers) / rate_per_day)

    return {
        "start_followers": start_followers,
        "end_followers": end_followers,
        "gained": gained,
        "days_measured": days,
        "per_day_avg": round(rate_per_day, 1),
        "growth_percent": round(rate_percent, 2),
        "days_to_10k": days_to_10k,
        "days_to_100k": days_to_100k,
        "assessment": _assess_growth(rate_percent, days),
    }


def _assess_growth(rate_percent: float, days: int) -> str:
    daily_rate = rate_percent / max(days, 1)
    if daily_rate >= 1.0:
        return "Viral — exceptional growth, sustain with consistency"
    if daily_rate >= 0.3:
        return "Strong — above average, double down on what's working"
    if daily_rate >= 0.1:
        return "Healthy — on track, optimize posting times and hashtags"
    if daily_rate > 0:
        return "Slow — experiment with content format, sounds, and posting frequency"
    return "Stagnant — pivot content strategy; test new niches or formats"
