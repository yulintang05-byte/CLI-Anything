"""Account optimizer - platform-specific 2026 algorithm strategies."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import Counter


# 2026 algorithm weights per platform (based on public research)
PLATFORM_SIGNALS = {
    "tiktok": {
        "completion_rate":  {"weight": 35, "threshold": 0.70, "description": "70%+ completion rate needed for FYP push in 2026"},
        "shares":           {"weight": 25, "threshold": 5, "description": "Shares are the strongest single signal on TikTok"},
        "saves":            {"weight": 20, "threshold": 3, "description": "Saves indicate high-value content — algorithm rewards them heavily"},
        "comments":         {"weight": 10, "threshold": 10, "description": "Comments show community — reply fast to seed early engagement"},
        "likes":            {"weight": 5,  "threshold": 20, "description": "Likes matter least now — don't optimize for them exclusively"},
        "rewatch_rate":     {"weight": 5,  "threshold": 0.15, "description": "Rewatches signal quality — strong hook increases this"},
    },
    "youtube_shorts": {
        "completion_rate":  {"weight": 30, "threshold": 0.60, "description": "60%+ completion boosts Shorts visibility"},
        "swipe_away_rate":  {"weight": 25, "threshold": 0.10, "description": "Low swipe-away rate = algorithm keeps showing it"},
        "likes_ratio":      {"weight": 20, "threshold": 0.05, "description": "5%+ like rate is strong for Shorts"},
        "comments":         {"weight": 15, "threshold": 5, "description": "Comments extend shelf life of content"},
        "saves":            {"weight": 10, "threshold": 2, "description": "Saves signal evergreen value"},
    },
    "youtube_long": {
        "watch_time_hours": {"weight": 35, "threshold": 4, "description": "Total watch hours drive recommendation engine"},
        "ctr":              {"weight": 25, "threshold": 0.06, "description": "6%+ CTR is strong — optimize thumbnails and titles"},
        "avg_view_duration": {"weight": 20, "threshold": 0.45, "description": "45%+ average view duration is benchmark for recommendations"},
        "comments":         {"weight": 10, "threshold": 20, "description": "Comments signal community health"},
        "subscribers":      {"weight": 10, "threshold": 10, "description": "Post-video subscriber rate signals strong content"},
    },
    "instagram_reels": {
        "shares":           {"weight": 30, "threshold": 5, "description": "Shares (send to friend) are #1 Reels signal in 2026"},
        "saves":            {"weight": 25, "threshold": 3, "description": "Saves rank above likes now — drive value/educational content"},
        "completion_rate":  {"weight": 25, "threshold": 0.65, "description": "65%+ completion needed for Explore push"},
        "comments":         {"weight": 15, "threshold": 8, "description": "Replies in comments extend post reach"},
        "likes":            {"weight": 5,  "threshold": 30, "description": "Likes are vanity metric in 2026 Reels algorithm"},
    },
}

OPTIMAL_POST_TIMES = {
    "tiktok": {
        "Mon": ["6:00-8:00am", "7:00-9:00pm"],
        "Tue": ["9:00-11:00am", "7:00-9:00pm"],
        "Wed": ["7:00-9:00am", "7:00-11:00pm"],
        "Thu": ["9:00-11:00am", "7:00-9:00pm"],
        "Fri": ["5:00-7:00am", "5:00-7:00pm"],
        "Sat": ["11:00am-1:00pm", "7:00-9:00pm"],
        "Sun": ["7:00-9:00am", "4:00-6:00pm"],
        "note": "Use YOUR audience timezone. Check TikTok Analytics > Followers > Activity.",
    },
    "youtube": {
        "best_days": ["Friday", "Saturday", "Sunday"],
        "best_times": ["2:00-4:00pm", "6:00-9:00pm"],
        "note": "YouTube viewers skew afternoon/evening vs TikTok's morning peak.",
    },
    "instagram": {
        "best_days": ["Tuesday", "Wednesday", "Thursday"],
        "best_times": ["9:00-11:00am", "6:00-8:00pm"],
        "note": "Instagram Reels peaked earlier in the day than TikTok historically.",
    },
}


def audit_account(
    platform: str,
    username: str,
    followers: int = 0,
    avg_views: int = 0,
    avg_likes: int = 0,
    avg_comments: int = 0,
    avg_shares: int = 0,
    avg_saves: int = 0,
    posts_per_week: int = 3,
    niche: str = "",
    bio_has_cta: bool = False,
    has_link_in_bio: bool = False,
) -> Dict[str, Any]:
    """
    Audit a social media account and provide optimization recommendations.

    Returns a detailed report with score, weaknesses, and action steps.
    """
    platform = platform.lower().replace(" ", "_")
    signals = PLATFORM_SIGNALS.get(platform, PLATFORM_SIGNALS["tiktok"])

    issues = []
    strengths = []
    score = 0
    max_score = 100

    # Engagement rate
    if followers > 0 and avg_views > 0:
        view_rate = avg_views / followers
        if view_rate >= 0.3:
            strengths.append(f"Strong view rate ({view_rate:.0%} of followers) — content is being distributed well.")
            score += 20
        elif view_rate >= 0.1:
            score += 10
            issues.append({
                "issue": "Low view-to-follower ratio",
                "detail": f"{view_rate:.0%} of followers see your content. Aim for 30%+.",
                "fix": "Post at peak times, use 3-5 niche hashtags, improve hook in first 2 seconds.",
                "priority": "high",
            })
        else:
            issues.append({
                "issue": "Very low view rate",
                "detail": f"Only {view_rate:.0%} of followers see posts — algorithm is not distributing your content.",
                "fix": "Reset by posting 3 high-quality videos this week. Focus on completion rate > 70% by leading with value.",
                "priority": "critical",
            })

    # Engagement rate calculation
    if avg_views > 0:
        eng_rate = (avg_likes + avg_comments + avg_shares + avg_saves) / avg_views
        if eng_rate >= 0.08:
            strengths.append(f"High engagement rate ({eng_rate:.1%}) — algorithm will boost this content.")
            score += 20
        elif eng_rate >= 0.03:
            score += 10
            issues.append({
                "issue": "Below-average engagement rate",
                "detail": f"{eng_rate:.1%} engagement on views. Strong accounts hit 8%+.",
                "fix": "End every video with a direct CTA: 'Save this if it helped you' or 'Comment your #1 takeaway'.",
                "priority": "medium",
            })
        else:
            issues.append({
                "issue": "Low engagement rate",
                "detail": f"Only {eng_rate:.1%} engagement. Content may not be driving action.",
                "fix": "Add stronger CTAs, ask questions in captions, reply to ALL comments in first hour.",
                "priority": "high",
            })

    # Posting frequency
    if posts_per_week == 0:
        issues.append({
            "issue": "Not posting",
            "detail": "No recent posts detected. Accounts that don't post lose algorithmic favor fast.",
            "fix": "Post minimum 3x/week. Consistency matters more than perfection.",
            "priority": "critical",
        })
    elif posts_per_week < 3:
        issues.append({
            "issue": "Under-posting",
            "detail": f"{posts_per_week} posts/week. 2026 research shows 3-5 posts/week is optimal.",
            "fix": "Batch-create content once a week (filming 4-5 videos in one session) to maintain consistency.",
            "priority": "medium",
        })
    elif posts_per_week >= 3:
        score += 10
        if posts_per_week > 7:
            issues.append({
                "issue": "Possibly over-posting",
                "detail": f"{posts_per_week} posts/week may dilute quality. Quality beats quantity in 2026.",
                "fix": "Test reducing to 4-5 quality posts/week and monitor per-video performance.",
                "priority": "low",
            })
        else:
            strengths.append(f"Good posting frequency ({posts_per_week}x/week).")

    # Niche clarity
    if not niche:
        issues.append({
            "issue": "Niche not defined",
            "detail": "The algorithm cannot categorize your account if content spans multiple topics.",
            "fix": "Pick ONE niche and stick to it for 30 days. Then optionally expand.",
            "priority": "high",
        })
    else:
        score += 10
        strengths.append(f"Niche defined: {niche}. Algorithm can index and distribute to the right audience.")

    # Bio & CTA
    if not bio_has_cta:
        issues.append({
            "issue": "No call-to-action in bio",
            "detail": "Bio with no CTA loses converting visitors. Every profile visit is a potential follower/customer.",
            "fix": "Add a micro-CTA to bio: 'Daily [niche] tips ↓' or 'Free guide in link below'.",
            "priority": "medium",
        })
    else:
        score += 5
        strengths.append("Bio has CTA — good for converting profile visitors.")

    if not has_link_in_bio:
        issues.append({
            "issue": "No link in bio",
            "detail": "Missing monetization pathway. Link in bio is the #1 revenue channel for creators.",
            "fix": "Add a linktree or direct product/newsletter link. Mention it in videos: 'Link in bio for [value]'.",
            "priority": "medium",
        })
    else:
        score += 5
        strengths.append("Link in bio present — monetization pathway is set up.")

    # Shares signal (most important on TikTok/Reels)
    if platform in ("tiktok", "instagram_reels") and avg_views > 0:
        share_rate = avg_shares / avg_views if avg_views > 0 else 0
        threshold = signals.get("shares", {}).get("threshold", 5)
        if avg_shares < threshold and avg_views > 100:
            issues.append({
                "issue": "Low share rate (critical signal)",
                "detail": f"Shares are the #1 algorithm signal in 2026. Avg shares: {avg_shares}.",
                "fix": "Create content specifically designed to be shared: 'Send this to someone who needs it', surprising facts, relatable content.",
                "priority": "critical",
            })
        elif avg_shares >= threshold:
            score += 15
            strengths.append(f"Good share rate — strong algorithm distribution signal.")

    # Build recommendations
    recs = _build_recommendations(platform, niche, issues)

    issues.sort(key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x["priority"], 4))

    return {
        "audited_at": datetime.now().isoformat(),
        "platform": platform,
        "username": username,
        "health_score": min(score, max_score),
        "grade": _score_to_grade(score),
        "strengths": strengths,
        "issues": issues,
        "recommendations": recs,
        "posting_times": OPTIMAL_POST_TIMES.get(platform.split("_")[0], OPTIMAL_POST_TIMES["tiktok"]),
        "algorithm_signals": signals,
    }


def _score_to_grade(score: int) -> str:
    if score >= 80:
        return "A - Optimized"
    elif score >= 60:
        return "B - Good"
    elif score >= 40:
        return "C - Needs Work"
    elif score >= 20:
        return "D - Underperforming"
    return "F - Critical Issues"


def _build_recommendations(platform: str, niche: str, issues: List[Dict]) -> List[str]:
    recs = []
    priorities = {i["issue"] for i in issues}

    if "Low view-to-follower ratio" in priorities or "Very low view rate" in priorities:
        recs.append(
            "HOOK AUDIT: Review your first 2 seconds. The algorithm decides distribution in the first frame. "
            "Use text overlay, bold visual, or surprising statement instantly."
        )

    if platform == "tiktok":
        recs.append(
            "2026 TikTok: Spoken keywords matter. Say your hashtags out loud in the video — TikTok's audio indexing "
            "boosts your content for those search terms even without hashtags in caption."
        )
        recs.append(
            "Qualified Views threshold: get past the 5-second mark. If viewers drop under 5s, TikTok stops pushing. "
            "Test different hooks A/B style — same content, different opening."
        )

    if platform in ("youtube_shorts", "youtube_long"):
        recs.append(
            "2026 YouTube: Thumbnail + title CTR is the first gate. Use high-contrast thumbnails, "
            "expressive faces, and curiosity gaps in titles. Tools: Canva for thumbnails."
        )
        recs.append(
            "YouTube Shorts in 2026 feeds into long-form subscribers. Create Shorts that tease or extend "
            "your long-form content to build ecosystem."
        )

    if niche:
        recs.append(
            f"NICHE DOMINATION: For {niche}, aim to be THE go-to account. "
            "Niche specificity in 2026 outperforms broad accounts 5:1 for follower conversion rate."
        )

    recs.append(
        "ENGAGEMENT WINDOW: Reply to every comment in the first 60 minutes of posting. "
        "This extends the algorithm's testing phase and signals an active community."
    )

    recs.append(
        "BATCH CREATION: Film 4-5 videos per session, 1x per week. "
        "Reduces decision fatigue and ensures consistent output without burnout."
    )

    return recs


def bulk_optimize_accounts(accounts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Optimize multiple accounts at once — useful for theme page networks.

    Each account dict: {platform, username, followers, avg_views, niche, ...}
    """
    results = []
    overall_issues = []

    for acct in accounts:
        audit = audit_account(**acct)
        results.append({
            "username": acct.get("username"),
            "platform": acct.get("platform"),
            "health_score": audit["health_score"],
            "grade": audit["grade"],
            "critical_issues": [i for i in audit["issues"] if i["priority"] == "critical"],
            "top_recommendation": audit["recommendations"][0] if audit["recommendations"] else "",
        })
        overall_issues.extend([i["issue"] for i in audit["issues"] if i["priority"] == "critical"])

    results.sort(key=lambda x: x["health_score"])
    common_issues = Counter(overall_issues).most_common(5)

    return {
        "optimized_at": datetime.now().isoformat(),
        "accounts_audited": len(accounts),
        "results": results,
        "common_critical_issues": [{"issue": i, "count": c} for i, c in common_issues],
        "portfolio_avg_score": sum(r["health_score"] for r in results) / len(results) if results else 0,
        "priority_action": (
            f"Fix '{common_issues[0][0]}' across {common_issues[0][1]} accounts first — "
            "it's the most common blocker in your portfolio."
        ) if common_issues else "Run individual audits for specific recommendations.",
    }


from collections import Counter
