"""Social media account optimization engine.

Provides data-driven recommendations for:
- Bio optimization
- Posting schedule (best times by niche + platform)
- Hashtag strategy
- Content pillars
- Engagement rate benchmarks
- Profile audit
"""

from __future__ import annotations

import re
import time
from typing import Optional

from .trends import NICHE_KEYWORDS, get_hashtag_suggestions

# ── Benchmark data ────────────────────────────────────────────────────

# Best posting times (UTC hour ranges) by platform + niche
# Based on aggregated creator community research (Sprout Social, Later, etc.)
BEST_TIMES: dict[str, dict[str, list[tuple[int, int]]]] = {
    "tiktok": {
        "general":    [(6, 9), (12, 15), (19, 23)],
        "fitness":    [(5, 8), (11, 13), (18, 21)],
        "beauty":     [(7, 10), (12, 14), (19, 22)],
        "fashion":    [(8, 11), (13, 15), (19, 22)],
        "food":       [(11, 13), (17, 20), (21, 23)],
        "finance":    [(7, 10), (12, 14), (20, 22)],
        "gaming":     [(14, 17), (19, 23), (0, 2)],
        "comedy":     [(12, 15), (19, 22), (0, 2)],
        "motivation": [(6, 8), (12, 13), (20, 22)],
        "education":  [(9, 11), (14, 17), (20, 22)],
    },
    "youtube": {
        "general":    [(14, 16), (18, 21)],
        "gaming":     [(14, 17), (20, 23)],
        "fitness":    [(6, 9), (17, 20)],
        "education":  [(10, 13), (17, 20)],
        "beauty":     [(11, 14), (18, 21)],
        "food":       [(11, 14), (17, 20)],
        "music":      [(15, 18), (20, 23)],
        "general":    [(14, 16), (18, 21)],
    },
}

# Engagement rate benchmarks by platform + follower tier
ENGAGEMENT_BENCHMARKS: dict[str, dict[str, float]] = {
    "tiktok": {
        "nano (<10k)":     18.0,
        "micro (10k-100k)": 12.0,
        "mid (100k-1M)":    8.0,
        "macro (1M+)":      5.0,
    },
    "youtube": {
        "small (<10k)":    8.0,
        "mid (10k-100k)":  5.0,
        "large (100k-1M)": 3.0,
        "mega (1M+)":      1.5,
    },
    "instagram": {
        "nano (<10k)":     5.0,
        "micro (10k-100k)": 3.0,
        "mid (100k-1M)":    1.5,
        "macro (1M+)":      0.8,
    },
}

# Content frequency recommendations per niche + platform
POSTING_FREQUENCY: dict[str, dict[str, str]] = {
    "tiktok": {
        "fitness":    "1-3x / day",
        "beauty":     "1-2x / day",
        "fashion":    "1-2x / day",
        "food":       "1-3x / day",
        "comedy":     "2-4x / day",
        "gaming":     "1-2x / day",
        "finance":    "1x / day",
        "motivation": "1-2x / day",
        "education":  "1x / day",
        "general":    "1-3x / day",
    },
    "youtube": {
        "fitness":    "3-5x / week",
        "beauty":     "2-3x / week",
        "gaming":     "3-5x / week",
        "education":  "2-4x / week",
        "finance":    "2-3x / week",
        "food":       "2-3x / week",
        "travel":     "1-2x / week",
        "general":    "2-4x / week",
    },
}

# Content pillars by niche (the 3-4 content categories to rotate through)
CONTENT_PILLARS: dict[str, list[str]] = {
    "fitness":    ["Workout tutorials", "Transformation/results", "Nutrition tips", "Motivation/mindset"],
    "beauty":     ["Product reviews", "GRWM tutorials", "Skincare routines", "Trend recreations"],
    "fashion":    ["Outfit of the day", "Styling tips", "Haul videos", "Seasonal trends"],
    "food":       ["Recipes/cooking", "Restaurant reviews", "Healthy vs indulgent", "Cultural food exploration"],
    "finance":    ["Money tips", "Investment breakdowns", "Income reports", "Myth busting"],
    "gaming":     ["Gameplay highlights", "Reviews", "Tips & tricks", "Live reactions"],
    "comedy":     ["Skits/sketches", "Reaction videos", "Trend parodies", "POV scenarios"],
    "motivation": ["Daily affirmations", "Success stories", "Mindset shifts", "Productivity hacks"],
    "education":  ["How-to tutorials", "Explainer videos", "Myth vs fact", "Case studies"],
    "pets":       ["Cute moments", "Training tips", "Pet care advice", "Day in the life"],
    "travel":     ["Destination guides", "Travel hacks", "Budget tips", "Vlog content"],
    "tech":       ["Product reviews", "Tutorial/how-to", "Industry news", "Comparisons"],
    "dance":      ["Tutorial breakdown", "Original choreography", "Trend dances", "Collabs/duets"],
    "music":      ["Original music", "Covers", "Behind the scenes", "Fan interaction"],
    "art":        ["Process videos (timelapse)", "Tutorials", "Finished pieces", "Behind the scenes"],
}


def audit_account(platform: str, handle: str, niche: str,
                  followers: int = 0, avg_views: int = 0,
                  avg_likes: int = 0, bio: str = "",
                  posts_per_week: float = 0) -> dict:
    """Run a full account audit and return scored recommendations.

    Args:
        platform: 'tiktok' or 'youtube'.
        handle: Account handle/username.
        niche: Content niche.
        followers: Current follower/subscriber count.
        avg_views: Average views per video.
        avg_likes: Average likes per video.
        bio: Current bio/description text.
        posts_per_week: Current posting frequency.

    Returns:
        Audit dict with score (0-100), issues, and action items.
    """
    issues: list[str] = []
    wins: list[str] = []
    action_items: list[str] = []
    score = 60  # baseline

    platform = platform.lower()
    niche = niche.lower()

    # Engagement rate check
    er = 0.0
    if followers > 0 and avg_likes > 0:
        er = (avg_likes / max(avg_views, 1)) * 100
        benchmarks = ENGAGEMENT_BENCHMARKS.get(platform, {})
        tier_label = _get_follower_tier(platform, followers)
        benchmark = benchmarks.get(tier_label, 5.0)
        if er >= benchmark:
            score += 15
            wins.append(f"Engagement rate {er:.1f}% is at or above benchmark ({benchmark}%)")
        elif er >= benchmark * 0.6:
            score += 5
            action_items.append(
                f"Engagement rate {er:.1f}% is below benchmark {benchmark}%. "
                "Reply to every comment for 30 days to boost."
            )
        else:
            score -= 10
            issues.append(f"Engagement rate {er:.1f}% is significantly below benchmark {benchmark}%.")
            action_items.append(
                "Call-to-action in every video (ask a question, request a comment)."
            )

    # Posting frequency check
    if posts_per_week > 0:
        rec_freq = POSTING_FREQUENCY.get(platform, {}).get(niche, "1-3x / day" if platform == "tiktok" else "2-4x / week")
        try:
            lo, hi = _parse_freq(rec_freq, platform)
            weekly_lo = lo * 7 if "day" in rec_freq else lo
            weekly_hi = hi * 7 if "day" in rec_freq else hi
            if posts_per_week >= weekly_lo:
                score += 10
                wins.append(f"Posting {posts_per_week:.1f}x/week meets recommendation ({rec_freq})")
            else:
                score -= 5
                action_items.append(f"Increase to {rec_freq} to maximise algorithm reach.")
        except Exception:
            pass

    # Bio audit
    if bio:
        bio_score, bio_issues, bio_wins = _audit_bio(bio, niche, platform)
        score += bio_score
        issues += bio_issues
        wins += bio_wins
        if bio_score < 0:
            action_items.append("Rewrite bio to include: niche keyword, value proposition, CTA.")
    else:
        issues.append("No bio provided — bio is critical for profile conversion.")
        action_items.append("Add a bio with your niche + value proposition + call to action.")

    # Hashtag suggestion
    suggested_tags = get_hashtag_suggestions(niche, platform, count=15)

    score = max(0, min(100, score))
    return {
        "handle": handle,
        "platform": platform,
        "niche": niche,
        "score": score,
        "grade": _score_to_grade(score),
        "followers": followers,
        "engagement_rate": round(er, 2),
        "wins": wins,
        "issues": issues,
        "action_items": action_items,
        "suggested_hashtags": suggested_tags,
        "best_posting_times": get_best_posting_times(platform, niche),
        "recommended_frequency": POSTING_FREQUENCY.get(platform, {}).get(niche, "1-2x / day"),
        "content_pillars": CONTENT_PILLARS.get(niche, ["Educational", "Entertainment", "Inspirational", "Promotional"]),
    }


def get_best_posting_times(platform: str, niche: str = "general") -> list[dict]:
    """Return best posting time windows for a platform + niche.

    Returns:
        List of dicts with day_of_week, utc_start_hour, utc_end_hour, reason.
    """
    platform = platform.lower()
    niche_key = niche.lower() if niche.lower() in BEST_TIMES.get(platform, {}) else "general"
    windows = BEST_TIMES.get(platform, {}).get(niche_key, [(12, 15), (19, 22)])

    results = []
    day_labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    priority_days = {
        "tiktok": ["Tuesday", "Thursday", "Friday", "Saturday"],
        "youtube": ["Thursday", "Friday", "Saturday", "Sunday"],
    }
    priority = priority_days.get(platform, ["Tuesday", "Thursday", "Saturday"])

    for day in day_labels:
        is_priority = day in priority
        for start, end in windows:
            results.append({
                "day": day,
                "utc_start": start,
                "utc_end": end,
                "label": f"{start:02d}:00–{end:02d}:00 UTC",
                "priority": is_priority,
            })

    # Sort: priority days first, then by hour
    results.sort(key=lambda x: (0 if x["priority"] else 1, x["utc_start"]))
    return results


def suggest_bio(niche: str, platform: str, handle: str,
                value_prop: str = "", cta: str = "") -> dict:
    """Generate an optimised bio template.

    Args:
        niche: Content niche.
        platform: 'tiktok' or 'youtube'.
        handle: Account handle.
        value_prop: What value does the account deliver?
        cta: Desired call to action (e.g., "Link in bio for free guide").

    Returns:
        Dict with bio_template and tips.
    """
    niche = niche.lower()
    keyword = NICHE_KEYWORDS.get(niche, [niche])[0].title()

    if not value_prop:
        value_prop = f"Daily {keyword} content"
    if not cta:
        cta = "👇 New video every day"

    char_limits = {"tiktok": 80, "youtube": 1000, "instagram": 150}
    limit = char_limits.get(platform.lower(), 150)

    if platform.lower() == "youtube":
        template = (
            f"Welcome to {handle}! 🎯 {value_prop.rstrip('.')}.\n\n"
            f"I post {niche} content to help you achieve your goals.\n\n"
            f"📌 New videos every week — Subscribe for {keyword} tips!\n"
            f"📩 Business inquiries: [your email]"
        )
    else:
        template = (
            f"{keyword} creator 🎯 | {value_prop[:40]}\n"
            f"{cta}"
        )[:limit]

    tips = [
        f"Keep under {limit} characters for {platform}.",
        "Use 1-2 relevant emojis (not more — looks spammy).",
        "Include your niche keyword for discoverability.",
        "Add a clear call to action (CTA).",
        "If you have a link, reference it: 'Link below ↓'.",
    ]
    return {"bio_template": template, "char_limit": limit, "tips": tips}


def get_engagement_rate(views: int, likes: int, comments: int = 0) -> dict:
    """Calculate engagement rate and benchmark it.

    Returns:
        Dict with er_by_views, er_by_likes, benchmark_rating.
    """
    if views <= 0:
        return {"error": "views must be > 0"}
    er_views = ((likes + comments) / views) * 100
    er_likes = (likes / views) * 100
    rating = "poor"
    if er_likes >= 10:
        rating = "excellent"
    elif er_likes >= 5:
        rating = "good"
    elif er_likes >= 2:
        rating = "average"
    return {
        "engagement_rate_by_views": round(er_views, 2),
        "likes_rate": round(er_likes, 2),
        "rating": rating,
        "target_likes_rate": ">5% TikTok, >3% YouTube",
    }


# ── Helpers ───────────────────────────────────────────────────────────

def _audit_bio(bio: str, niche: str, platform: str) -> tuple[int, list, list]:
    score = 0
    issues = []
    wins = []
    keywords = NICHE_KEYWORDS.get(niche, [niche])
    lower_bio = bio.lower()

    has_keyword = any(k in lower_bio for k in keywords)
    if has_keyword:
        score += 5
        wins.append("Bio contains niche keyword — good for discoverability.")
    else:
        score -= 5
        issues.append(f"Bio missing niche keyword. Add one of: {', '.join(keywords[:3])}")

    has_cta = any(w in lower_bio for w in ["follow", "subscribe", "link", "click", "check", "shop", "dm"])
    if has_cta:
        score += 5
        wins.append("Bio contains a call to action.")
    else:
        score -= 3
        issues.append("No CTA in bio — add 'Follow for daily tips' or similar.")

    char_limits = {"tiktok": 80, "youtube": 1000}
    limit = char_limits.get(platform, 150)
    if len(bio) > limit:
        score -= 2
        issues.append(f"Bio too long ({len(bio)} chars, limit {limit}). Trim it.")

    return score, issues, wins


def _get_follower_tier(platform: str, followers: int) -> str:
    if platform == "tiktok":
        if followers < 10_000:   return "nano (<10k)"
        if followers < 100_000:  return "micro (10k-100k)"
        if followers < 1_000_000: return "mid (100k-1M)"
        return "macro (1M+)"
    else:
        if followers < 10_000:   return "small (<10k)"
        if followers < 100_000:  return "mid (10k-100k)"
        if followers < 1_000_000: return "large (100k-1M)"
        return "mega (1M+)"


def _score_to_grade(score: int) -> str:
    if score >= 85: return "A"
    if score >= 70: return "B"
    if score >= 55: return "C"
    if score >= 40: return "D"
    return "F"


def _parse_freq(freq_str: str, platform: str) -> tuple[float, float]:
    match = re.search(r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)", freq_str)
    if match:
        return float(match.group(1)), float(match.group(2))
    match = re.search(r"(\d+(?:\.\d+)?)", freq_str)
    if match:
        v = float(match.group(1))
        return v, v
    return 1.0, 3.0
