"""Account Optimization — Profile scoring and actionable recommendations."""

import re
from typing import Optional


_PLATFORM_LIMITS = {
    "tiktok": {
        "bio_max": 80,
        "username_max": 24,
        "name_max": 30,
        "post_frequency_daily": {"min": 1, "optimal": 3},
        "best_times_utc": ["12:00", "15:00", "18:00", "21:00"],
    },
    "youtube": {
        "bio_max": 1000,
        "username_max": 30,
        "name_max": 100,
        "post_frequency_weekly": {"min": 1, "optimal": 3},
        "best_times_utc": ["14:00", "16:00", "20:00"],
    },
    "instagram": {
        "bio_max": 150,
        "username_max": 30,
        "name_max": 30,
        "post_frequency_daily": {"min": 1, "optimal": 2},
        "best_times_utc": ["08:00", "12:00", "17:00", "21:00"],
    },
}


def score_profile(
    platform: str,
    username: str,
    display_name: str,
    bio: str,
    has_profile_photo: bool = True,
    has_link: bool = False,
    follower_count: int = 0,
    following_count: int = 0,
    post_count: int = 0,
    niche: Optional[str] = None,
) -> dict:
    """Score a social media profile and return graded recommendations."""
    limits = _PLATFORM_LIMITS.get(platform, _PLATFORM_LIMITS["tiktok"])
    score = 100
    recs: list[dict] = []

    # Username
    if len(username) > limits["username_max"]:
        score -= 5
        recs.append({"priority": "low", "area": "username", "action": f"Shorten username to ≤{limits['username_max']} chars"})
    if re.search(r"\d{4,}", username):
        score -= 5
        recs.append({"priority": "medium", "area": "username", "action": "Remove random numbers from username — harder to find and looks unprofessional"})

    # Display name
    if not display_name or len(display_name.strip()) < 3:
        score -= 10
        recs.append({"priority": "high", "area": "display_name", "action": "Add a keyword-rich display name (e.g., 'Fitness Tips by Jake')"})
    elif niche and niche.lower() not in display_name.lower():
        score -= 5
        recs.append({"priority": "medium", "area": "display_name", "action": f"Consider including your niche '{niche}' in display name for SEO"})

    # Bio
    bio_len = len(bio.strip())
    if bio_len == 0:
        score -= 20
        recs.append({"priority": "critical", "area": "bio", "action": "Write a bio — this is the #1 conversion driver. Include: niche, value prop, CTA"})
    elif bio_len < 30:
        score -= 10
        recs.append({"priority": "high", "area": "bio", "action": f"Bio too short ({bio_len} chars). Add niche, value proposition, and a call-to-action"})
    elif bio_len > limits["bio_max"]:
        score -= 5
        recs.append({"priority": "medium", "area": "bio", "action": f"Bio exceeds {limits['bio_max']} char limit — it will be cut off"})

    has_cta = any(kw in bio.lower() for kw in ["click", "link", "shop", "follow", "dm", "check", "join", "get", "free"])
    if bio and not has_cta:
        score -= 10
        recs.append({"priority": "high", "area": "bio", "action": "Add a clear CTA to bio (e.g., 'Link below for free guide ↓')"})

    # Profile photo
    if not has_profile_photo:
        score -= 15
        recs.append({"priority": "critical", "area": "photo", "action": "Upload a high-quality profile photo — profiles without photos get ~60% fewer follows"})

    # Link in bio
    if not has_link and platform in ("tiktok", "instagram"):
        score -= 10
        recs.append({"priority": "high", "area": "link", "action": "Add a link in bio — use Linktree, Beacons, or Stan Store to maximize conversions"})

    # Following ratio
    if following_count > 0 and follower_count > 0:
        ratio = follower_count / following_count
        if ratio < 0.5 and following_count > 500:
            score -= 10
            recs.append({"priority": "medium", "area": "ratio", "action": f"Follow:Follower ratio is low ({ratio:.1f}x). Unfollow inactive accounts to improve credibility"})

    # Post count
    if post_count < 10:
        score -= 10
        recs.append({"priority": "high", "area": "content", "action": "Post more content — accounts with <10 posts rarely go viral. Aim for 20+ posts before pushing growth"})

    recs.sort(key=lambda r: {"critical": 0, "high": 1, "medium": 2, "low": 3}[r["priority"]])

    return {
        "platform": platform,
        "username": username,
        "score": max(0, score),
        "grade": _grade(score),
        "recommendations": recs,
        "quick_wins": [r for r in recs if r["priority"] in ("critical", "high")][:5],
    }


def posting_schedule(platform: str, timezone_offset: int = 0) -> dict:
    """Return optimal posting times for a platform adjusted for a UTC offset."""
    limits = _PLATFORM_LIMITS.get(platform, _PLATFORM_LIMITS["tiktok"])
    best_utc = limits.get("best_times_utc", ["12:00", "18:00"])
    adjusted = []
    for t in best_utc:
        h, m = map(int, t.split(":"))
        local_h = (h + timezone_offset) % 24
        adjusted.append(f"{local_h:02d}:{m:02d}")

    freq = limits.get("post_frequency_daily") or limits.get("post_frequency_weekly")
    unit = "day" if "post_frequency_daily" in limits else "week"

    return {
        "platform": platform,
        "best_times_local": adjusted,
        "best_times_utc": best_utc,
        "timezone_offset_hours": timezone_offset,
        "frequency": {
            "unit": unit,
            "minimum": freq["min"],
            "optimal": freq["optimal"],
        },
        "tips": _posting_tips(platform),
    }


def _posting_tips(platform: str) -> list[str]:
    tips = {
        "tiktok": [
            "Post 1-4x/day consistently — algorithm rewards consistency over perfection",
            "Use trending audio within 24-48h of it going viral",
            "Hook viewers in the first 1-2 seconds to maximize watch time",
            "Reply to comments with video replies to boost engagement signals",
            "Stitch/Duet viral content in your niche for reach spikes",
        ],
        "youtube": [
            "Post Shorts daily, long-form 1-3x/week",
            "Write SEO-optimized titles (keyword first, 60 chars max)",
            "Upload custom thumbnails — they drive 90% of click-through rate",
            "Add chapters to long videos to reduce abandonment",
            "Respond to every comment in the first hour after posting",
        ],
        "instagram": [
            "Reels outperform static posts 3x — prioritize video content",
            "Post Stories daily to stay top of feed",
            "Use the 'collab' feature to co-post with similar accounts",
            "Carousel posts get 2-3x more reach than single images",
            "Hashtag strategy: mix 3-5 large, 5-7 medium, 3-5 niche tags",
        ],
    }
    return tips.get(platform, tips["tiktok"])


def _grade(score: int) -> str:
    if score >= 90: return "A"
    if score >= 75: return "B"
    if score >= 60: return "C"
    if score >= 45: return "D"
    return "F"
