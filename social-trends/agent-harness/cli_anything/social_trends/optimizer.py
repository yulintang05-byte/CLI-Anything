"""Account optimizer — converts trend data into actionable posting strategies."""

import re
from datetime import datetime, timezone
from typing import Optional


# Optimal posting windows per platform (UTC hour ranges, day-of-week 0=Mon..6=Sun)
_POSTING_WINDOWS = {
    "tiktok": {
        "best_hours_utc": [12, 15, 19, 20, 21],  # 12pm, 3pm, 7-9pm ET
        "best_days": [1, 2, 3, 4],               # Tue-Fri
        "worst_days": [5, 6],
        "posting_frequency": "1-3x per day",
        "video_length": "15-30s for trending, 60-90s for storytelling",
    },
    "youtube": {
        "best_hours_utc": [14, 15, 16, 17, 18],  # 2-6pm ET
        "best_days": [4, 5, 6],                   # Fri-Sun
        "worst_days": [0, 1],
        "posting_frequency": "3-5x per week (Shorts), 1-2x per week (long-form)",
        "video_length": "Shorts: 15-60s | Long-form: 8-15 min (ad-revenue sweet spot)",
    },
    "instagram": {
        "best_hours_utc": [14, 17, 18, 20],
        "best_days": [1, 3, 4],
        "worst_days": [6],
        "posting_frequency": "1-2x per day (Reels), 3-5x per week (feed)",
        "video_length": "Reels: 15-30s max engagement; Stories: 15s per slide",
    },
    "twitter": {
        "best_hours_utc": [13, 14, 15, 18, 19],
        "best_days": [1, 2, 3, 4],
        "worst_days": [6],
        "posting_frequency": "3-5x per day",
        "video_length": "N/A for video focus; threads perform best 5-7 tweets",
    },
}

# Platform hashtag strategy
_HASHTAG_STRATEGY = {
    "tiktok": {
        "total": "3-6 hashtags",
        "mix": "1 mega (>1B views) + 2 large (100M-1B) + 2 niche (<10M)",
        "avoid": "Avoid 20+ hashtags — kills reach in TikTok algo",
        "tip": "Always include #fyp and 1 super-niche hashtag for the algo",
    },
    "youtube": {
        "total": "3-5 in title/description",
        "mix": "1 trending broad + 2 niche keywords + channel brand tag",
        "avoid": "Don't use unrelated tags — YouTube penalizes this",
        "tip": "Put most important hashtag first in description",
    },
    "instagram": {
        "total": "5-10 hashtags (Reels), 3-5 (feed posts)",
        "mix": "2 large + 3 medium + 3 small niche",
        "avoid": "Banned/overused tags drop reach into shadow territory",
        "tip": "First comment hashtag strategy works just as well as caption",
    },
}


def build_hashtag_set(
    trending_tags: list[dict],
    niche: str,
    platform: str = "tiktok",
    max_tags: int = 8,
) -> dict:
    """
    Build an optimized hashtag set for a given niche + platform.
    trending_tags: output from tiktok.get_trending_hashtags() or youtube.extract_hashtags_from_titles()
    """
    strategy = _HASHTAG_STRATEGY.get(platform, _HASHTAG_STRATEGY["tiktok"])

    # Bucket tags by estimated size (using post_count where available)
    mega, large, medium, niche_tags = [], [], [], []
    for tag in trending_tags:
        pc = tag.get("post_count") or 0
        name = tag["hashtag"]
        niche_lower = niche.lower()
        tag_name_lower = name.lstrip("#").lower()
        is_niche_related = any(
            w in tag_name_lower for w in re.findall(r"\w+", niche_lower)
        )

        if pc == 0:
            # No post_count data — distribute by position in list
            medium.append(name)
        elif pc >= 1_000_000_000:
            mega.append(name)
        elif pc >= 100_000_000:
            large.append(name)
        elif is_niche_related:
            niche_tags.append(name)
        else:
            medium.append(name)

    # Always include platform essentials
    essentials = {
        "tiktok": ["#fyp", "#foryou", "#foryoupage"],
        "youtube": [],
        "instagram": ["#reels", "#explore"],
    }.get(platform, [])

    # Build final set
    selected: list[str] = []

    # 1. Essentials
    for tag in essentials:
        if tag not in selected:
            selected.append(tag)

    # 2. 1 mega
    for tag in mega[:1]:
        if tag not in selected:
            selected.append(tag)

    # 3. 2 large
    for tag in large[:2]:
        if tag not in selected:
            selected.append(tag)

    # 4. niche-related
    for tag in niche_tags[:3]:
        if tag not in selected:
            selected.append(tag)

    # 5. Fill with medium
    for tag in medium:
        if len(selected) >= max_tags:
            break
        if tag not in selected:
            selected.append(tag)

    return {
        "hashtags": selected[:max_tags],
        "count": len(selected[:max_tags]),
        "platform": platform,
        "niche": niche,
        "strategy": strategy,
    }


def get_posting_schedule(
    platform: str,
    timezone_offset: int = -5,
    posts_per_week: int = 7,
) -> dict:
    """
    Generate a weekly posting schedule for a platform.
    timezone_offset: hours from UTC (e.g. -5 for EST, +1 for CET)
    """
    config = _POSTING_WINDOWS.get(platform, _POSTING_WINDOWS["tiktok"])
    best_days = config["best_days"]
    best_hours_utc = config["best_hours_utc"]

    # Convert UTC hours to local
    best_hours_local = [
        (h + timezone_offset) % 24 for h in best_hours_utc
    ]

    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    schedule = []

    slots_needed = posts_per_week
    for day_idx in (best_days + [d for d in range(7) if d not in config["best_days"]]):
        if slots_needed <= 0:
            break
        # How many posts on this day
        posts_today = 1 if day_idx not in config["worst_days"] else 0
        if posts_today == 0:
            continue
        # Pick best hour
        hour = best_hours_local[len(schedule) % len(best_hours_local)]
        am_pm = "AM" if hour < 12 else "PM"
        hour_12 = hour % 12 or 12
        schedule.append(
            {
                "day": day_names[day_idx],
                "time_local": f"{hour_12}:00 {am_pm}",
                "time_utc": f"{best_hours_utc[len(schedule) % len(best_hours_utc)]:02d}:00 UTC",
                "priority": "high" if day_idx in best_days else "medium",
            }
        )
        slots_needed -= 1

    return {
        "platform": platform,
        "schedule": schedule[:posts_per_week],
        "frequency": config["posting_frequency"],
        "video_length": config["video_length"],
        "timezone_offset": timezone_offset,
    }


def generate_content_angles(
    trending_titles: list[str],
    niche: str,
    platform: str = "tiktok",
) -> list[dict]:
    """
    Derive content angle ideas from trending titles adapted to a niche.
    """
    # Common viral content frameworks
    frameworks = [
        ("POV:", "Point of view hooks — put viewer in a scenario"),
        ("Wait for it...", "Delayed reveal format — keeps watch time high"),
        ("Day in the life of...", "Lifestyle/behind-scenes — high relatability"),
        ("Things you didn't know about...", "Informational hook — education niche"),
        ("This changed everything...", "Transformation story — strong emotional hook"),
        ("I tried [trend] for 30 days...", "Challenge format — built-in narrative arc"),
        ("How I went from X to Y...", "Before/after — aspirational content"),
        ("Stop doing this if you want...", "Negative hook — curiosity gap"),
        ("The truth about...", "Expose format — controversy + trust building"),
        ("React to...", "Reaction content — leverages existing trending media"),
    ]

    angles = []

    # Generate niche-adapted angles from trending titles
    for title in trending_titles[:5]:
        # Find the core topic
        core = re.sub(r"[^a-zA-Z0-9 ]", "", title).strip()[:50]
        angles.append(
            {
                "angle": f"React/comment on: '{core}' — adapted to {niche}",
                "framework": "React to...",
                "virality_reason": "Riding existing trend momentum",
                "platform_fit": platform,
            }
        )

    # Add framework-based angles
    for template, description in frameworks[:6]:
        angles.append(
            {
                "angle": f"{template} {niche}",
                "framework": template,
                "virality_reason": description,
                "platform_fit": platform,
            }
        )

    return angles


def analyze_account(
    platform: str,
    niche: str,
    current_followers: int = 0,
    avg_views: int = 0,
    posts_per_week: int = 0,
    trending_hashtags: Optional[list[dict]] = None,
) -> dict:
    """
    Analyze an account and return optimization recommendations.
    """
    recommendations = []
    score = 100  # start perfect, subtract for issues

    # Posting frequency analysis
    freq_targets = {"tiktok": 7, "youtube": 3, "instagram": 5}
    target_freq = freq_targets.get(platform, 5)
    if posts_per_week < target_freq * 0.5:
        score -= 20
        recommendations.append(
            {
                "priority": "HIGH",
                "category": "posting_frequency",
                "issue": f"Only {posts_per_week}x/week — below optimal for {platform}",
                "fix": f"Increase to {target_freq}x/week minimum for algorithm favor",
            }
        )
    elif posts_per_week > target_freq * 2:
        score -= 5
        recommendations.append(
            {
                "priority": "MEDIUM",
                "category": "posting_frequency",
                "issue": "Posting too frequently — can dilute engagement rate",
                "fix": f"Cap at {target_freq * 2}x/week; focus on quality over quantity",
            }
        )

    # Engagement rate
    if current_followers > 0 and avg_views > 0:
        view_rate = avg_views / current_followers
        if view_rate < 0.1:
            score -= 25
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "engagement",
                    "issue": f"View rate {view_rate:.1%} is very low (under 10%)",
                    "fix": "Audit your hooks — first 2 seconds must stop the scroll. Test 5 different hook styles.",
                }
            )
        elif view_rate < 0.5:
            score -= 10
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "engagement",
                    "issue": f"View rate {view_rate:.1%} — room to improve",
                    "fix": "Add strong CTA at 80% of video. Use trending audio to boost distribution.",
                }
            )

    # Hashtag optimization
    if trending_hashtags:
        tag_set = build_hashtag_set(trending_hashtags, niche, platform)
        recommendations.append(
            {
                "priority": "HIGH",
                "category": "hashtags",
                "issue": "Optimize hashtag stack with current trends",
                "fix": f"Use these tags: {', '.join(tag_set['hashtags'][:6])}",
                "full_set": tag_set,
            }
        )

    # Growth stage advice
    if current_followers < 1_000:
        recommendations.append(
            {
                "priority": "HIGH",
                "category": "growth_stage",
                "issue": "Early growth phase — need viral breakthrough",
                "fix": (
                    "Focus 100% on trending sounds + trending topics in your niche. "
                    "Post daily. Engage with top 10 creators in your niche (comment first 30 min after they post)."
                ),
            }
        )
    elif current_followers < 10_000:
        recommendations.append(
            {
                "priority": "MEDIUM",
                "category": "growth_stage",
                "issue": "Building phase — consistency is key",
                "fix": (
                    "Identify your 3 top-performing content pillars and double down. "
                    "Start pinning best-performing video. Add link-in-bio."
                ),
            }
        )
    elif current_followers < 100_000:
        recommendations.append(
            {
                "priority": "MEDIUM",
                "category": "growth_stage",
                "issue": "Mid-tier — monetization window opening",
                "fix": (
                    "Start TikTok Series or YouTube memberships. "
                    "Collab with 2-5 creators at similar size. "
                    "Build email list NOW — social platforms can de-platform you."
                ),
            }
        )
    else:
        recommendations.append(
            {
                "priority": "LOW",
                "category": "growth_stage",
                "issue": "Established — focus on monetization & brand deals",
                "fix": "Diversify to owned channels (newsletter, website). Negotiate brand deals at $10-20 CPM minimum.",
            }
        )

    return {
        "platform": platform,
        "niche": niche,
        "health_score": max(0, score),
        "followers": current_followers,
        "avg_views": avg_views,
        "recommendations": sorted(
            recommendations, key=lambda x: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[x["priority"]]
        ),
        "posting_schedule": get_posting_schedule(platform, posts_per_week=target_freq),
    }
