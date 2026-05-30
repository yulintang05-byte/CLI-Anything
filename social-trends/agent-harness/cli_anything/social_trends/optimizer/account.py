#!/usr/bin/env python3
"""Account optimizer — analyzes account profiles and recommends optimizations.

Covers bio, posting schedule, hashtag strategy, content mix,
engagement tactics, and growth levers for TikTok and YouTube channels.
"""

from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------------------
# Account profile input schema
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = {
    "platform": str,
    "username": str,
}

OPTIONAL_FIELDS = {
    "follower_count": int,
    "following_count": int,
    "post_count": int,
    "avg_views": int,
    "avg_likes": int,
    "avg_comments": int,
    "avg_shares": int,
    "bio": str,
    "niche": str,
    "posting_frequency_per_week": float,
    "account_age_days": int,
    "has_link_in_bio": bool,
    "verified": bool,
    "profile_pic_set": bool,
    "recent_hashtags": list,
    "top_performing_content_types": list,
}


def analyze_account(profile: dict) -> dict:
    """Run full account optimization analysis.

    Args:
        profile: Dict with account data (see REQUIRED_FIELDS + OPTIONAL_FIELDS)

    Returns:
        dict with scores, recommendations, and an action plan
    """
    platform = profile.get("platform", "").lower()
    username = profile.get("username", "unknown")

    scores = _score_account(profile, platform)
    recommendations = _build_recommendations(profile, platform, scores)
    action_plan = _build_action_plan(recommendations)
    posting_schedule = _optimal_posting_schedule(platform, profile.get("niche", ""))
    hashtag_strategy = _hashtag_strategy(platform, profile)

    overall_score = sum(scores.values()) // max(len(scores), 1)

    return {
        "account": {
            "username": username,
            "platform": platform,
            "analyzed_at": datetime.utcnow().isoformat() + "Z",
        },
        "overall_score": overall_score,
        "grade": _score_to_grade(overall_score),
        "category_scores": scores,
        "recommendations": recommendations,
        "action_plan": action_plan,
        "optimal_posting_schedule": posting_schedule,
        "hashtag_strategy": hashtag_strategy,
    }


def bulk_optimize(accounts: list[dict]) -> list[dict]:
    """Run analysis across multiple accounts.

    Args:
        accounts: List of account profile dicts

    Returns:
        List of analysis results sorted by overall score ascending
        (lowest-scoring = needs the most work first)
    """
    results = [analyze_account(acc) for acc in accounts]
    return sorted(results, key=lambda x: x["overall_score"])


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _score_account(profile: dict, platform: str) -> dict[str, int]:
    """Score each dimension 0-100."""
    scores = {}

    # --- Profile completeness ---
    completeness = 60
    if profile.get("bio") and len(profile["bio"]) > 20:
        completeness += 20
    if profile.get("has_link_in_bio"):
        completeness += 10
    if profile.get("profile_pic_set"):
        completeness += 10
    scores["profile_completeness"] = min(completeness, 100)

    # --- Engagement rate ---
    avg_views = profile.get("avg_views", 0)
    avg_likes = profile.get("avg_likes", 0)
    avg_comments = profile.get("avg_comments", 0)
    avg_shares = profile.get("avg_shares", 0)

    if avg_views > 0:
        er = (avg_likes + avg_comments + avg_shares) / avg_views * 100
        if platform == "tiktok":
            # TikTok average ER is ~5-8%
            if er >= 10:
                scores["engagement_rate"] = 95
            elif er >= 6:
                scores["engagement_rate"] = 75
            elif er >= 3:
                scores["engagement_rate"] = 50
            else:
                scores["engagement_rate"] = 25
        else:
            # YouTube average ER is ~2-4%
            if er >= 5:
                scores["engagement_rate"] = 95
            elif er >= 3:
                scores["engagement_rate"] = 75
            elif er >= 1:
                scores["engagement_rate"] = 50
            else:
                scores["engagement_rate"] = 25
    else:
        scores["engagement_rate"] = 0

    # --- Posting consistency ---
    freq = profile.get("posting_frequency_per_week", 0)
    if platform == "tiktok":
        if freq >= 7:
            scores["posting_consistency"] = 100
        elif freq >= 4:
            scores["posting_consistency"] = 75
        elif freq >= 2:
            scores["posting_consistency"] = 50
        elif freq >= 1:
            scores["posting_consistency"] = 25
        else:
            scores["posting_consistency"] = 0
    else:  # YouTube
        if freq >= 5:
            scores["posting_consistency"] = 100
        elif freq >= 3:
            scores["posting_consistency"] = 80
        elif freq >= 1:
            scores["posting_consistency"] = 55
        elif freq >= 0.5:
            scores["posting_consistency"] = 30
        else:
            scores["posting_consistency"] = 0

    # --- Follower to following ratio ---
    followers = profile.get("follower_count", 0)
    following = profile.get("following_count", 1)
    ratio = followers / max(following, 1)
    if ratio >= 10:
        scores["authority_ratio"] = 100
    elif ratio >= 5:
        scores["authority_ratio"] = 80
    elif ratio >= 2:
        scores["authority_ratio"] = 60
    elif ratio >= 1:
        scores["authority_ratio"] = 40
    else:
        scores["authority_ratio"] = 20

    # --- Hashtag strategy ---
    hashtags = profile.get("recent_hashtags", [])
    if 3 <= len(hashtags) <= 6:
        scores["hashtag_strategy"] = 90
    elif 1 <= len(hashtags) <= 10:
        scores["hashtag_strategy"] = 65
    elif len(hashtags) > 10:
        scores["hashtag_strategy"] = 40  # hashtag stuffing penalty
    else:
        scores["hashtag_strategy"] = 10

    # --- Niche clarity ---
    if profile.get("niche") and len(profile["niche"]) > 2:
        scores["niche_clarity"] = 80
    else:
        scores["niche_clarity"] = 30

    return scores


def _score_to_grade(score: int) -> str:
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    if score >= 50:
        return "D"
    return "F"


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------

def _build_recommendations(
    profile: dict, platform: str, scores: dict
) -> list[dict]:
    recs = []
    priority_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

    # Profile completeness
    if scores.get("profile_completeness", 0) < 80:
        if not profile.get("bio") or len(profile.get("bio", "")) < 20:
            recs.append({
                "priority": "CRITICAL",
                "category": "profile",
                "title": "Write a compelling bio",
                "detail": (
                    "Your bio is missing or too short. Include: (1) what you do, "
                    "(2) who you help, (3) a social proof element, (4) a CTA. "
                    f"Example for {platform}: 'Daily {profile.get('niche', 'content')} tips | "
                    "Helping [audience] achieve [outcome] | Link below for free resources'"
                ),
                "impact": "High — bio is the first thing potential followers read",
            })
        if not profile.get("has_link_in_bio"):
            recs.append({
                "priority": "HIGH",
                "category": "profile",
                "title": "Add a link in bio",
                "detail": (
                    "Use a link aggregator (Linktree, Stan Store, Beacons.ai) to point followers "
                    "to your best content, newsletter, product, or other socials. "
                    "This turns followers into leads and email subscribers."
                ),
                "impact": "Medium-High — critical for monetization",
            })
        if not profile.get("profile_pic_set"):
            recs.append({
                "priority": "HIGH",
                "category": "profile",
                "title": "Set a professional profile photo",
                "detail": (
                    "Use a high-quality headshot or branded logo. "
                    "Accounts without profile photos lose ~30% of potential follows at first glance."
                ),
                "impact": "Medium — trust signal",
            })

    # Engagement rate
    er_score = scores.get("engagement_rate", 0)
    if er_score < 50:
        recs.append({
            "priority": "CRITICAL",
            "category": "engagement",
            "title": "Boost engagement rate — currently below average",
            "detail": (
                "Low ER hurts algorithmic distribution. Tactics: "
                "(1) End every video with an explicit CTA ('Comment X if you agree'). "
                "(2) Reply to every comment in the first hour of posting. "
                "(3) Post at peak times for your audience. "
                "(4) Use controversial/question-based hooks in captions. "
                "(5) Pin a comment yourself to spark conversation."
            ),
            "impact": "Critical — ER is the #1 signal for algorithmic push",
        })
    elif er_score < 75:
        recs.append({
            "priority": "MEDIUM",
            "category": "engagement",
            "title": "Improve engagement rate from good to great",
            "detail": (
                "Your engagement is decent but can be higher. "
                "Try: (1) Ask direct questions in captions. "
                "(2) Create 'save-worthy' content (tutorials, lists, resources). "
                "(3) Use 'duet/stitch this' CTAs on TikTok. "
                "(4) Collaborate with similar accounts for comment exchanges."
            ),
            "impact": "Medium — pushes you into creator reward tiers",
        })

    # Posting frequency
    freq = profile.get("posting_frequency_per_week", 0)
    cons_score = scores.get("posting_consistency", 0)
    if cons_score < 50:
        if platform == "tiktok":
            recs.append({
                "priority": "CRITICAL",
                "category": "consistency",
                "title": "Post more consistently — TikTok requires daily posting for growth",
                "detail": (
                    f"You're posting ~{freq:.1f}x/week. TikTok's algorithm rewards daily posters. "
                    "Target: 1-3 posts/day. Batch-create content once a week (2-3 hour session). "
                    "Use CapCut templates and trending audio to speed up production. "
                    "Quality matters less than consistency at <10K followers."
                ),
                "impact": "Critical — consistency is TikTok's #1 growth factor below 100K",
            })
        else:
            recs.append({
                "priority": "HIGH",
                "category": "consistency",
                "title": "Increase upload frequency for YouTube Shorts",
                "detail": (
                    f"You're uploading ~{freq:.1f}x/week. For Shorts growth, target 3-5/day. "
                    "For long-form, 2-3/week is optimal. "
                    "Create a content bank: record 10 videos on Sunday, edit and schedule throughout the week."
                ),
                "impact": "High — frequency directly correlates with Shorts distribution",
            })

    # Hashtag strategy
    ht_score = scores.get("hashtag_strategy", 0)
    hashtags = profile.get("recent_hashtags", [])
    if ht_score < 60:
        if len(hashtags) > 10:
            recs.append({
                "priority": "HIGH",
                "category": "hashtags",
                "title": "Stop hashtag stuffing — it hurts reach",
                "detail": (
                    f"You're using {len(hashtags)} hashtags. Both platforms penalize "
                    "hashtag stuffing in 2024. Use 3-5 targeted hashtags: "
                    "(1) 1-2 large niche hashtags (1M+ posts), "
                    "(2) 1-2 medium hashtags (100K-1M posts), "
                    "(3) 1 micro hashtag (<100K posts, very specific). "
                    "This is the 'hashtag stack' strategy used by 7-figure creators."
                ),
                "impact": "High — wrong hashtag use suppresses distribution",
            })
        else:
            recs.append({
                "priority": "MEDIUM",
                "category": "hashtags",
                "title": "Develop a systematic hashtag strategy",
                "detail": (
                    "Use the 3-tier hashtag stack: (1) 1 mega-hashtag for discoverability, "
                    "(2) 1-2 niche hashtags for targeted reach, "
                    "(3) 1 trending hashtag for algorithmic boost. "
                    "Research competitors in your niche and note which hashtags their top posts use."
                ),
                "impact": "Medium — hashtags are 15-20% of discoverability",
            })

    # Niche clarity
    if scores.get("niche_clarity", 0) < 60:
        recs.append({
            "priority": "HIGH",
            "category": "strategy",
            "title": "Niche down to accelerate growth",
            "detail": (
                "Broad accounts grow slowly. The fastest-growing accounts own a specific niche. "
                "Instead of 'fitness', do 'home workouts for busy moms'. "
                "Instead of 'cooking', do '5-ingredient college meals'. "
                "Specific niches have less competition and more loyal followers."
            ),
            "impact": "High — niche specificity is the #1 predictor of fast growth",
        })

    # Sort by priority
    priority_map = {p: i for i, p in enumerate(priority_order)}
    recs.sort(key=lambda r: priority_map.get(r["priority"], 99))
    return recs


def _build_action_plan(recommendations: list[dict]) -> list[dict]:
    """Convert recommendations into a numbered 30-day action plan."""
    plan = []
    day_map = {
        "CRITICAL": "Days 1-3",
        "HIGH": "Days 4-10",
        "MEDIUM": "Days 11-21",
        "LOW": "Days 22-30",
    }

    for i, rec in enumerate(recommendations, 1):
        plan.append({
            "step": i,
            "timeline": day_map.get(rec["priority"], "This month"),
            "action": rec["title"],
            "category": rec["category"],
            "priority": rec["priority"],
        })

    return plan


# ---------------------------------------------------------------------------
# Posting schedule
# ---------------------------------------------------------------------------

_POSTING_SCHEDULES = {
    "tiktok": {
        "default": {
            "best_days": ["Tuesday", "Wednesday", "Thursday", "Friday"],
            "best_times_utc": ["13:00", "16:00", "19:00", "21:00"],
            "frequency": "1-3 posts/day",
            "notes": "TikTok distributes globally so UTC times work well. Avoid posting 2am-7am UTC.",
        },
        "fitness": {
            "best_days": ["Monday", "Wednesday", "Friday", "Sunday"],
            "best_times_utc": ["06:00", "12:00", "17:00", "20:00"],
            "frequency": "1-2 posts/day",
            "notes": "Fitness audience checks TikTok before/after workouts. Monday motivation posts perform 40% better.",
        },
        "food": {
            "best_days": ["Wednesday", "Thursday", "Friday", "Saturday"],
            "best_times_utc": ["11:00", "17:00", "20:00"],
            "frequency": "1-2 posts/day",
            "notes": "Post recipes before lunch/dinner hours. Weekend posts get 25% more saves.",
        },
        "fashion": {
            "best_days": ["Monday", "Tuesday", "Thursday", "Saturday"],
            "best_times_utc": ["09:00", "13:00", "20:00"],
            "frequency": "1-3 posts/day",
            "notes": "Monday 'outfit of the week' hooks perform well. Saturday shopping-day content converts best.",
        },
    },
    "youtube": {
        "default": {
            "best_days": ["Thursday", "Friday", "Saturday", "Sunday"],
            "best_times_utc": ["14:00", "16:00", "18:00"],
            "frequency": "Shorts: 3-5/day | Long-form: 2-3/week",
            "notes": "Shorts follow TikTok rules. Long-form: Thu-Sat uploads get 30% more initial views.",
        },
        "gaming": {
            "best_days": ["Friday", "Saturday", "Sunday"],
            "best_times_utc": ["17:00", "20:00", "22:00"],
            "frequency": "2-4 shorts/day, 1-2 long-form/week",
            "notes": "Gaming audience peaks on weekends evenings. Reaction/tier-list content gets highest CTR.",
        },
        "education": {
            "best_days": ["Tuesday", "Wednesday", "Thursday"],
            "best_times_utc": ["12:00", "15:00", "18:00"],
            "frequency": "1-2 long-form/week, 2-3 shorts/day",
            "notes": "Students watch on weekday afternoons. Tutorial hooks in first 15s are critical for retention.",
        },
    },
}


def _optimal_posting_schedule(platform: str, niche: str) -> dict:
    """Return the optimal posting schedule for platform + niche."""
    platform = platform.lower()
    niche = niche.lower() if niche else ""
    platform_schedules = _POSTING_SCHEDULES.get(platform, _POSTING_SCHEDULES["tiktok"])

    # Find matching niche schedule
    schedule = platform_schedules.get("default")
    for niche_key in platform_schedules:
        if niche_key != "default" and niche_key in niche:
            schedule = platform_schedules[niche_key]
            break

    return {
        "platform": platform,
        "niche": niche or "general",
        **schedule,
    }


# ---------------------------------------------------------------------------
# Hashtag strategy builder
# ---------------------------------------------------------------------------

def _hashtag_strategy(platform: str, profile: dict) -> dict:
    """Build a custom hashtag stack recommendation."""
    niche = profile.get("niche", "general")
    followers = profile.get("follower_count", 0)

    if followers < 1000:
        tier = "new"
    elif followers < 10000:
        tier = "growing"
    elif followers < 100000:
        tier = "established"
    else:
        tier = "large"

    tier_advice = {
        "new": {
            "strategy": "Use medium + micro hashtags (avoid mega tags — you'll drown)",
            "mega_count": 0,
            "niche_count": 2,
            "micro_count": 2,
            "trending_count": 1,
            "total": 5,
            "reasoning": "At <1K followers, mega hashtags (100M+ posts) will bury you. Focus on micro (10K-100K) and trending (1M-5M) tags where you can rank.",
        },
        "growing": {
            "strategy": "Mix of niche + trending hashtags, 1 mega for discoverability",
            "mega_count": 1,
            "niche_count": 2,
            "micro_count": 1,
            "trending_count": 1,
            "total": 5,
            "reasoning": "At 1K-10K you can compete in medium pools. Add one trending tag per post to catch algorithmic pushes.",
        },
        "established": {
            "strategy": "Branded hashtag + niche authority tags + 1 trending",
            "mega_count": 1,
            "niche_count": 2,
            "micro_count": 0,
            "trending_count": 1,
            "branded_count": 1,
            "total": 5,
            "reasoning": "At 10K-100K create your own hashtag (e.g., #YourUsername) and promote it. This builds community and tracks UGC.",
        },
        "large": {
            "strategy": "Own hashtag + 2-3 niche + trending moment",
            "mega_count": 1,
            "niche_count": 2,
            "micro_count": 0,
            "trending_count": 1,
            "branded_count": 1,
            "total": 5,
            "reasoning": "Large accounts should be driving trends, not chasing them. Create challenges and branded moments.",
        },
    }

    return {
        "account_tier": tier,
        "follower_count": followers,
        "niche": niche,
        "platform": platform,
        **tier_advice[tier],
        "pro_tip": (
            "Research your top 5 competitors' best-performing posts and note exactly "
            "which hashtags they used. This is your fastest path to finding what works in your niche."
        ),
    }
