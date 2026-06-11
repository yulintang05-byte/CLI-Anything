"""
Account optimization engine.
Analyses account stats and produces actionable growth recommendations.
Works with any platform that provides the standard stats dict.
"""
from __future__ import annotations
import math
from datetime import datetime
from typing import Literal

Platform = Literal["youtube", "tiktok", "instagram", "all"]


# Optimal posting windows by platform (UTC hour ranges, day 0=Mon)
OPTIMAL_TIMES: dict[str, list[dict]] = {
    "tiktok": [
        {"day": "Tuesday",   "hours": "7-9 AM",  "tz": "EST",  "score": 9.5},
        {"day": "Thursday",  "hours": "9-11 AM", "tz": "EST",  "score": 9.2},
        {"day": "Friday",    "hours": "5-7 PM",  "tz": "EST",  "score": 9.0},
        {"day": "Saturday",  "hours": "11AM-1PM","tz": "EST",  "score": 8.8},
        {"day": "Wednesday", "hours": "7-9 AM",  "tz": "EST",  "score": 8.5},
    ],
    "youtube": [
        {"day": "Friday",    "hours": "3-5 PM",  "tz": "EST",  "score": 9.4},
        {"day": "Saturday",  "hours": "9-11 AM", "tz": "EST",  "score": 9.2},
        {"day": "Thursday",  "hours": "2-4 PM",  "tz": "EST",  "score": 8.9},
        {"day": "Sunday",    "hours": "11AM-1PM","tz": "EST",  "score": 8.7},
        {"day": "Wednesday", "hours": "3-5 PM",  "tz": "EST",  "score": 8.5},
    ],
    "instagram": [
        {"day": "Monday",    "hours": "6-8 AM",  "tz": "EST",  "score": 9.3},
        {"day": "Tuesday",   "hours": "11AM-1PM","tz": "EST",  "score": 9.1},
        {"day": "Wednesday", "hours": "11AM-1PM","tz": "EST",  "score": 9.0},
        {"day": "Friday",    "hours": "10AM-12PM","tz": "EST", "score": 8.8},
        {"day": "Sunday",    "hours": "9-11 AM", "tz": "EST",  "score": 8.6},
    ],
}

# Growth phase benchmarks
GROWTH_PHASES = {
    "seed":    (0,      1_000,   "0–1K followers — focus on consistency and niche authority"),
    "sprout":  (1_000,  10_000,  "1K–10K — optimize hooks, increase posting frequency"),
    "rising":  (10_000, 100_000, "10K–100K — collaborate, use trending audio, cross-promote"),
    "viral":   (100_000,1_000_000,"100K–1M — monetize, brand deals, merchandise"),
    "mega":    (1_000_000,float("inf"), "1M+ — maintain authenticity, diversify revenue"),
}

FREQUENCY_BENCHMARKS: dict[str, dict] = {
    "tiktok":    {"min": 1, "optimal": 3,  "max": 5,  "unit": "day"},
    "youtube":   {"min": 1, "optimal": 3,  "max": 5,  "unit": "week"},
    "instagram": {"min": 1, "optimal": 1,  "max": 3,  "unit": "day"},
    "shorts":    {"min": 1, "optimal": 2,  "max": 4,  "unit": "day"},
}


def _phase(followers: int) -> tuple[str, str]:
    for name, (lo, hi, desc) in GROWTH_PHASES.items():
        if lo <= followers < hi:
            return name, desc
    return "mega", GROWTH_PHASES["mega"][2]


def calculate_engagement_rate(followers: int, avg_likes: int,
                               avg_comments: int = 0, avg_shares: int = 0) -> float:
    """Standard engagement rate formula: (likes+comments+shares) / followers * 100."""
    if followers <= 0:
        return 0.0
    total = avg_likes + avg_comments + avg_shares
    return round((total / followers) * 100, 2)


def engagement_health(rate: float, platform: str) -> dict:
    """Classify engagement rate quality per platform."""
    benchmarks = {
        "tiktok":    {"excellent": 5.0, "good": 3.0, "average": 1.0, "poor": 0.5},
        "youtube":   {"excellent": 4.0, "good": 2.0, "average": 0.5, "poor": 0.1},
        "instagram": {"excellent": 6.0, "good": 3.0, "average": 1.0, "poor": 0.5},
    }
    thresholds = benchmarks.get(platform, benchmarks["tiktok"])

    if rate >= thresholds["excellent"]:
        level, color = "Excellent", "green"
    elif rate >= thresholds["good"]:
        level, color = "Good", "yellow"
    elif rate >= thresholds["average"]:
        level, color = "Average", "orange"
    else:
        level, color = "Poor — action needed", "red"

    return {
        "rate":       rate,
        "level":      level,
        "platform":   platform,
        "benchmarks": thresholds,
        "advice":     _engagement_advice(rate, thresholds),
    }


def _engagement_advice(rate: float, thresholds: dict) -> str:
    if rate >= thresholds["excellent"]:
        return "Excellent engagement! Double down on your current content style."
    if rate >= thresholds["good"]:
        return "Good engagement. Experiment with CTAs and polls to push higher."
    if rate >= thresholds["average"]:
        return "Average. Test shorter hooks (first 3 sec), ask direct questions in captions."
    return "Low engagement. Audit your posting times, hook quality, and hashtag relevance."


def project_growth(followers: int, avg_weekly_gain: int,
                   weeks: int = 12) -> list[dict]:
    """Project follower growth over N weeks."""
    projections = []
    current = followers
    for w in range(1, weeks + 1):
        # Apply slight compounding (virality factor) if already growing fast
        multiplier = 1.0 + (0.05 if avg_weekly_gain > followers * 0.1 else 0.0)
        gain = int(avg_weekly_gain * (multiplier ** w))
        current += gain
        projections.append({
            "week":      w,
            "followers": current,
            "gain":      gain,
        })
    return projections


def full_account_audit(stats: dict, platform: str) -> dict:
    """
    Complete account health audit.

    Expected stats keys:
        followers, following, avg_likes, avg_comments, avg_shares,
        post_frequency (posts per week), account_age_days,
        avg_views (optional), niche (optional)
    """
    followers    = int(stats.get("followers", 0))
    following    = int(stats.get("following", 0))
    avg_likes    = int(stats.get("avg_likes", 0))
    avg_comments = int(stats.get("avg_comments", 0))
    avg_shares   = int(stats.get("avg_shares", 0))
    avg_views    = int(stats.get("avg_views", 0))
    freq         = float(stats.get("post_frequency", 0))
    age_days     = int(stats.get("account_age_days", 30))
    niche        = stats.get("niche", "general")

    phase_name, phase_desc = _phase(followers)
    er = calculate_engagement_rate(followers, avg_likes, avg_comments, avg_shares)
    er_health = engagement_health(er, platform)

    # Follower-to-following ratio
    ff_ratio = round(followers / max(1, following), 2)
    ff_advice = (
        "Healthy ratio." if ff_ratio >= 1.0
        else "Following more than followers — unfollow inactive accounts to improve credibility."
    )

    # Reach rate (views / followers)
    reach_rate = round((avg_views / max(1, followers)) * 100, 2) if avg_views else None

    # Frequency score
    bench = FREQUENCY_BENCHMARKS.get(platform, FREQUENCY_BENCHMARKS["tiktok"])
    posts_per_week = freq if bench["unit"] == "week" else freq * 7
    freq_score = "optimal" if bench["min"] <= posts_per_week <= bench["max"] else (
        "too low — increase cadence" if posts_per_week < bench["min"] else "too high — risk burnout"
    )

    # Overall score (0-100)
    score_components = {
        "engagement": min(er / max(0.1, er_health["benchmarks"]["excellent"]) * 25, 25),
        "frequency":  20 if freq_score == "optimal" else (10 if "increase" in freq_score else 5),
        "ff_ratio":   15 if ff_ratio >= 1 else max(0, 15 - (1 - ff_ratio) * 15),
        "reach":      min((reach_rate or 0) / 20 * 20, 20) if reach_rate else 10,
        "age_bonus":  min(age_days / 365 * 20, 20),
    }
    overall_score = round(sum(score_components.values()), 1)

    # Priority action items
    actions = []
    if er < er_health["benchmarks"]["average"]:
        actions.append("PRIORITY: Improve hook — first 3 seconds must stop the scroll")
    if posts_per_week < bench["min"]:
        actions.append(f"Post {bench['optimal']}x/{bench['unit']} minimum (currently {freq}x/week)")
    if ff_ratio < 0.5:
        actions.append("Mass-unfollow inactive accounts to improve credibility")
    if followers < 1000:
        actions.append("Comment on 20 trending posts/day to accelerate discovery")
    if not stats.get("niche"):
        actions.append("Define a clear niche — general accounts grow 3x slower")
    if followers > 1000 and not stats.get("has_link_in_bio"):
        actions.append("Add a link-in-bio tool (Linktree/Stan Store) to monetize traffic")

    return {
        "platform":         platform,
        "phase":            phase_name,
        "phase_description": phase_desc,
        "overall_score":    overall_score,
        "score_breakdown":  score_components,
        "engagement_rate":  er,
        "engagement_health": er_health,
        "ff_ratio":         ff_ratio,
        "ff_advice":        ff_advice,
        "reach_rate_pct":   reach_rate,
        "posting_frequency": freq_score,
        "optimal_times":    OPTIMAL_TIMES.get(platform, OPTIMAL_TIMES["tiktok"])[:3],
        "priority_actions": actions,
        "niche":            niche,
    }


def batch_audit(accounts: list[dict]) -> list[dict]:
    """Run full_account_audit on multiple accounts."""
    return [full_account_audit(a["stats"], a["platform"]) for a in accounts]


def monetization_readiness(followers: int, er: float, platform: str) -> dict:
    """Assess readiness for different monetization tiers."""
    tiers = {
        "brand_deals": {
            "tiktok":    {"min_followers": 10_000,  "min_er": 2.0},
            "youtube":   {"min_followers": 1_000,   "min_er": 1.0},
            "instagram": {"min_followers": 5_000,   "min_er": 2.5},
        },
        "affiliate_marketing": {
            "tiktok":    {"min_followers": 1_000,   "min_er": 1.5},
            "youtube":   {"min_followers": 500,     "min_er": 0.5},
            "instagram": {"min_followers": 1_000,   "min_er": 1.0},
        },
        "platform_monetization": {
            "tiktok":    {"min_followers": 10_000,  "min_er": 2.0,  "note": "TikTok Creator Fund"},
            "youtube":   {"min_followers": 1_000,   "min_er": None, "note": "YPP: 1K subs + 4K watch hours"},
            "instagram": {"min_followers": 10_000,  "min_er": 2.0,  "note": "Reels bonus program"},
        },
        "digital_products": {
            "tiktok":    {"min_followers": 5_000,   "min_er": 2.0},
            "youtube":   {"min_followers": 2_000,   "min_er": 1.5},
            "instagram": {"min_followers": 3_000,   "min_er": 2.0},
        },
    }

    results = {}
    for tier, platforms in tiers.items():
        req = platforms.get(platform, platforms.get("tiktok", {}))
        min_f = req.get("min_followers", 0)
        min_e = req.get("min_er", 0.0) or 0.0
        ready = followers >= min_f and er >= min_e
        pct   = round(min(followers / max(1, min_f), 1.0) * 50 +
                      min(er / max(0.1, min_e), 1.0) * 50, 1)
        results[tier] = {
            "ready":       ready,
            "progress_pct": pct,
            "requires":    f"{min_f:,} followers & {min_e}% ER",
            "note":        req.get("note", ""),
        }

    return results
