"""Social media account optimization engine.

Analyzes account metrics and generates specific, actionable optimization
reports. Works with manually provided stats or platform API data.
"""

import json
import math
from pathlib import Path
from typing import Any

from cli_anything.social_trends.utils.social_backend import get_config_dir


# ── Engagement Rate Benchmarks ───────────────────────────────────────────

_ENGAGEMENT_BENCHMARKS = {
    "tiktok": {
        "excellent": 6.0,
        "good": 3.0,
        "average": 1.0,
        "poor": 0.0,
    },
    "instagram": {
        "excellent": 3.5,
        "good": 1.5,
        "average": 0.5,
        "poor": 0.0,
    },
    "youtube": {
        "excellent": 4.0,
        "good": 2.0,
        "average": 0.8,
        "poor": 0.0,
    },
}

# ── Optimal Posting Times ────────────────────────────────────────────────

_POSTING_SCHEDULES = {
    "tiktok": {
        "best_days": ["Tuesday", "Thursday", "Friday"],
        "best_times_utc": ["06:00", "10:00", "19:00", "22:00"],
        "frequency": "1-4 posts per day",
        "note": "Post 2-3x daily when building a following. Consistency > volume.",
    },
    "instagram_reels": {
        "best_days": ["Monday", "Wednesday", "Friday"],
        "best_times_utc": ["08:00", "11:00", "17:00", "20:00"],
        "frequency": "4-7 Reels per week",
        "note": "Instagram Reels get 22% more interaction than standard videos.",
    },
    "youtube_shorts": {
        "best_days": ["Friday", "Saturday", "Sunday"],
        "best_times_utc": ["15:00", "17:00", "20:00"],
        "frequency": "1-2 Shorts per day",
        "note": "YouTube Shorts feed traffic peaks on weekends.",
    },
    "youtube": {
        "best_days": ["Thursday", "Friday", "Saturday"],
        "best_times_utc": ["14:00", "17:00", "20:00"],
        "frequency": "1-3 videos per week",
        "note": "Long-form YouTube: quality > frequency. 1 great video beats 5 average ones.",
    },
}


def calculate_engagement_rate(likes: int, comments: int, shares: int,
                               views: int, platform: str = "tiktok") -> dict:
    """Calculate engagement rate and benchmark against platform averages.

    Args:
        likes: Number of likes/hearts.
        comments: Number of comments.
        shares: Number of shares/reposts.
        views: Number of views/impressions.
        platform: 'tiktok', 'instagram', 'youtube'.

    Returns:
        Dict with {rate, grade, benchmark, suggestions}.
    """
    if views == 0:
        return {"engagement_rate": 0.0, "grade": "N/A", "benchmark": "no data", "suggestions": []}

    if platform == "tiktok":
        rate = (likes + comments + shares) / views * 100
    elif platform == "instagram":
        rate = (likes + comments + shares) / views * 100
    else:  # youtube
        rate = (likes + comments) / views * 100

    rate = round(rate, 4)
    benchmarks = _ENGAGEMENT_BENCHMARKS.get(platform, _ENGAGEMENT_BENCHMARKS["tiktok"])

    if rate >= benchmarks["excellent"]:
        grade = "A+ (Excellent)"
        suggestions = ["Maintain current strategy — your content is resonating strongly."]
    elif rate >= benchmarks["good"]:
        grade = "B (Good)"
        suggestions = [
            "Add a call-to-action (CTA) in every video: 'Follow for more', 'Comment your thoughts'",
            "Reply to every comment in the first hour — this boosts algorithmic rank.",
        ]
    elif rate >= benchmarks["average"]:
        grade = "C (Average)"
        suggestions = [
            "Hook: first 1-3 seconds are critical. Lead with the most engaging moment.",
            "Add text overlays to retain viewers who watch on mute.",
            "End with a question to prompt comments.",
            "Post consistently — the algorithm rewards regular creators.",
        ]
    else:
        grade = "D (Below Average)"
        suggestions = [
            "Audit your content: watch your last 10 videos. Identify what's not landing.",
            "Study 3 top creators in your niche and reverse-engineer their hooks.",
            "Reduce video length — shorter content often gets higher completion rates.",
            "Experiment with trending sounds to reach new audiences.",
            "Post at peak times: " + ", ".join(_POSTING_SCHEDULES.get(platform, _POSTING_SCHEDULES["tiktok"])["best_times_utc"]) + " UTC",
        ]

    return {
        "engagement_rate": rate,
        "grade": grade,
        "platform_benchmark_good": benchmarks["good"],
        "platform_benchmark_excellent": benchmarks["excellent"],
        "suggestions": suggestions,
    }


def analyze_account(stats: dict) -> dict:
    """Perform a full account analysis from provided stats.

    Args:
        stats: Dict containing account metrics. Expected keys:
            - followers (int)
            - following (int)
            - total_posts (int)
            - avg_views (int)
            - avg_likes (int)
            - avg_comments (int)
            - avg_shares (int, optional)
            - platform (str)
            - niche (str, optional)
            - account_age_days (int, optional)

    Returns:
        Comprehensive analysis dict.
    """
    platform = stats.get("platform", "tiktok")
    followers = int(stats.get("followers", 0))
    following = int(stats.get("following", 0))
    posts = int(stats.get("total_posts", 0))
    avg_views = int(stats.get("avg_views", 0))
    avg_likes = int(stats.get("avg_likes", 0))
    avg_comments = int(stats.get("avg_comments", 0))
    avg_shares = int(stats.get("avg_shares", 0))
    account_age_days = int(stats.get("account_age_days", 365))
    niche = stats.get("niche", "general")

    # Engagement
    engagement = calculate_engagement_rate(
        avg_likes, avg_comments, avg_shares, avg_views, platform
    )

    # Follower-to-following ratio
    ff_ratio = round(followers / max(following, 1), 2)
    ff_health = "healthy" if ff_ratio >= 1.0 else "follow-for-follow pattern detected"

    # Content frequency
    posts_per_month = round(posts / max(account_age_days / 30, 1), 1)
    ideal_freq = _POSTING_SCHEDULES.get(platform, _POSTING_SCHEDULES["tiktok"])["frequency"]

    # Views-to-followers ratio (virality coefficient)
    vc = round(avg_views / max(followers, 1), 2) if followers > 0 else 0.0
    vc_label = (
        "viral reach" if vc > 5 else
        "above average" if vc > 1 else
        "average" if vc > 0.3 else
        "below average — content not reaching beyond followers"
    )

    # Growth rate estimate
    growth_rate = _estimate_growth_rate(followers, account_age_days, platform)

    # Bio score
    bio_score = stats.get("bio_score", None)

    # Monetization readiness
    monetization = _check_monetization_eligibility(followers, avg_views, platform)

    return {
        "platform": platform,
        "niche": niche,
        "followers": followers,
        "following": following,
        "follow_ratio": ff_ratio,
        "follow_ratio_health": ff_health,
        "total_posts": posts,
        "posts_per_month": posts_per_month,
        "recommended_frequency": ideal_freq,
        "avg_views": avg_views,
        "engagement": engagement,
        "virality_coefficient": vc,
        "virality_label": vc_label,
        "estimated_growth_rate": growth_rate,
        "monetization_status": monetization,
        "score": _compute_account_score(engagement, vc, ff_ratio, posts_per_month),
        "top_recommendations": _generate_recommendations(
            engagement, vc, ff_ratio, posts_per_month, platform, niche, monetization
        ),
    }


def _estimate_growth_rate(followers: int, age_days: int, platform: str) -> str:
    """Rough growth rate label."""
    if age_days == 0:
        return "unknown"
    avg_daily = followers / age_days
    if avg_daily > 1000:
        return "viral (>1K/day)"
    elif avg_daily > 100:
        return "fast (100-1K/day)"
    elif avg_daily > 10:
        return "steady (10-100/day)"
    else:
        return "slow (<10/day)"


def _check_monetization_eligibility(followers: int, avg_views: int,
                                     platform: str) -> dict:
    """Check monetization program eligibility."""
    result = {"platform": platform, "eligible": [], "requirements": {}}

    if platform == "tiktok":
        # TikTok Creator Rewards Program
        if followers >= 10_000 and avg_views >= 100_000:
            result["eligible"].append("TikTok Creator Rewards Program")
        result["requirements"]["Creator Rewards Program"] = "10K followers + 100K views/30 days + 18+"
        result["requirements"]["LIVE Gifts"] = "1K followers"
        result["requirements"]["Series"] = "10K followers"
        # TikTok Shop
        if followers >= 1_000:
            result["eligible"].append("TikTok Shop Affiliate")
        result["requirements"]["TikTok Shop Affiliate"] = "1K followers + 18+"

    elif platform == "youtube":
        # YouTube Partner Program
        if followers >= 1_000 and avg_views >= 4_000:  # proxy for 4K watch hours
            result["eligible"].append("YouTube Partner Program (YPP)")
        result["requirements"]["YouTube Partner Program"] = "1K subscribers + 4K watch hours/year OR 10M Shorts views/90 days"
        result["requirements"]["YouTube Shopping"] = "10K subscribers"
        result["requirements"]["Channel Memberships"] = "500 subscribers"

    elif platform == "instagram":
        if followers >= 10_000:
            result["eligible"].append("Instagram Subscriptions")
            result["eligible"].append("Instagram Gifts")
        result["requirements"]["Subscriptions"] = "10K followers + professional account"
        result["requirements"]["Brand Collabs Manager"] = "10K followers"
        result["requirements"]["Instagram Shopping"] = "eligible business account"

    return result


def _compute_account_score(engagement: dict, vc: float,
                            ff_ratio: float, posts_per_month: float) -> int:
    """Compute an overall 0-100 account health score."""
    score = 0
    er = engagement.get("engagement_rate", 0)
    if er >= 6:
        score += 40
    elif er >= 3:
        score += 30
    elif er >= 1:
        score += 20
    else:
        score += 5

    # Virality coefficient: 0-25 pts
    vc_pts = min(25, vc * 5)
    score += vc_pts

    # Follow ratio: 0-15 pts
    ff_pts = min(15, ff_ratio * 5)
    score += ff_pts

    # Posting frequency: 0-20 pts
    score += min(20, posts_per_month * 2)

    return min(100, int(score))


def _generate_recommendations(engagement: dict, vc: float, ff_ratio: float,
                               posts_per_month: float, platform: str,
                               niche: str, monetization: dict) -> list[str]:
    """Generate the top 5 most impactful recommendations."""
    recs = []

    # Engagement recs
    recs.extend(engagement.get("suggestions", [])[:2])

    # Virality
    if vc < 1:
        recs.append(
            "Boost discoverability: use 3-5 trending hashtags + 2 niche hashtags in every post."
        )
    if vc > 3:
        recs.append(
            "You have viral reach — convert it: pin your best video, add link in bio, push CTAs."
        )

    # Follow ratio
    if ff_ratio < 0.5:
        recs.append(
            "Unfollow non-followers: a high following count relative to followers signals low authority."
        )

    # Posting frequency
    schedule = _POSTING_SCHEDULES.get(platform, _POSTING_SCHEDULES["tiktok"])
    if posts_per_month < 4:
        recs.append(
            f"Post more consistently. Recommended: {schedule['frequency']}. "
            f"Best times: {', '.join(schedule['best_times_utc'])} UTC."
        )

    # Monetization
    if not monetization.get("eligible"):
        next_milestone = list(monetization.get("requirements", {}).items())
        if next_milestone:
            prog, req = next_milestone[0]
            recs.append(f"Focus on monetization milestone: {prog} requires {req}.")

    return recs[:6]


def generate_bio(niche: str, platform: str = "tiktok",
                 keywords: list[str] | None = None,
                 cta: str = "") -> dict:
    """Generate an optimized bio for a given niche and platform.

    Args:
        niche: Account niche (e.g., 'fitness', 'cooking').
        platform: 'tiktok', 'instagram', 'youtube'.
        keywords: Optional custom keywords to include.
        cta: Call-to-action text (e.g., 'Link in bio for free guide').

    Returns:
        Dict with {bio, character_count, tips, examples}.
    """
    kws = keywords or []
    cta_text = cta or _DEFAULT_CTAS.get(niche, "New videos every week")

    templates = _BIO_TEMPLATES.get(niche, _BIO_TEMPLATES["general"])
    # Pre-substitute {niche} before .format() so templates without it don't fail
    raw = templates[0].replace("{niche}", niche)
    bio = raw.format(cta=cta_text, keywords=", ".join(kws[:2]) if kws else niche)

    limits = {"tiktok": 80, "instagram": 150, "youtube": 1000}
    char_limit = limits.get(platform, 150)

    if len(bio) > char_limit:
        bio = bio[:char_limit - 3] + "..."

    return {
        "bio": bio,
        "character_count": len(bio),
        "character_limit": char_limit,
        "tips": [
            f"Keep it under {char_limit} characters for {platform}.",
            "Use line breaks on Instagram to improve readability.",
            "Include a clear niche identifier in the first line.",
            "Add a CTA (call-to-action) pointing to your link in bio.",
            "Use 1-3 relevant emojis max — they increase click-through by 15%.",
        ],
        "examples": templates[:3],
    }


_DEFAULT_CTAS = {
    "fitness": "Free workout plan — link in bio",
    "cooking": "Free recipes — link in bio",
    "finance": "Free investment guide — link in bio",
    "fashion": "Shop my looks — link in bio",
    "beauty": "My fave products — link in bio",
    "motivation": "Join the community — link in bio",
    "tech": "Best AI tools — link in bio",
    "travel": "Travel guides — link in bio",
    "gaming": "Watch me live — link in bio",
    "business": "Free course — link in bio",
}

_BIO_TEMPLATES = {
    "fitness": [
        "💪 {niche} Coach | Helping you build your best body\n📲 {cta}",
        "🏋️ Daily {niche} tips & workouts\nTransform your body in 90 days\n👇 {cta}",
        "Certified PT | {niche} & Nutrition\n🔥 Real results, no fluff\n{cta}",
    ],
    "cooking": [
        "🍳 Easy {niche} for busy people\nNew recipes every week\n👇 {cta}",
        "Home chef | Making {niche} simple\n🥘 Healthy, fast & delicious\n{cta}",
        "Food lover 🍴 | {niche} tips & hacks\n{cta}",
    ],
    "fashion": [
        "👗 {niche} & Style Inspo\nOutfit ideas for every occasion\n🛍️ {cta}",
        "Your daily dose of {niche}\nDressing on a budget 💸\n{cta}",
        "Style | {niche} | Confidence\nNew {niche} content daily\n{cta}",
    ],
    "finance": [
        "💰 Teaching {niche} for beginners\nNo fluff, just results\n📊 {cta}",
        "Helping you build wealth through {niche}\n🏦 Daily money tips\n{cta}",
        "{niche} & investing simplified\n💵 {cta}",
    ],
    "motivation": [
        "🔥 Daily {niche} & mindset content\nYour potential is limitless\n{cta}",
        "Helping you unlock your best self\n💡 {niche} every day\n{cta}",
        "Mindset | Growth | {niche}\n🚀 {cta}",
    ],
    "general": [
        "🎯 {niche} content creator\nNew videos weekly\n{cta}",
        "{keywords} | Daily content\n{cta}",
        "Sharing my passion for {niche}\n👇 {cta}",
    ],
}

_BIO_TEMPLATES["fitness"] = [t.replace("{niche}", "fitness") for t in _BIO_TEMPLATES["fitness"]]
_BIO_TEMPLATES["cooking"] = [t.replace("{niche}", "cooking") for t in _BIO_TEMPLATES["cooking"]]


def save_account_profile(name: str, stats: dict) -> str:
    """Persist an account profile to disk for tracking over time."""
    config_dir = get_config_dir()
    profiles_dir = config_dir / "profiles"
    profiles_dir.mkdir(exist_ok=True)
    path = profiles_dir / f"{name}.json"
    import time
    stats["_saved_at"] = time.time()
    with open(path, "w") as f:
        json.dump(stats, f, indent=2)
    return str(path)


def load_account_profile(name: str) -> dict:
    """Load a saved account profile."""
    config_dir = get_config_dir()
    path = config_dir / "profiles" / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"No profile found for '{name}'. Use 'accounts save' to create one.")
    with open(path, "r") as f:
        return json.load(f)


def list_account_profiles() -> list[str]:
    """List all saved account profiles."""
    config_dir = get_config_dir()
    profiles_dir = config_dir / "profiles"
    if not profiles_dir.exists():
        return []
    return [p.stem for p in profiles_dir.glob("*.json")]
