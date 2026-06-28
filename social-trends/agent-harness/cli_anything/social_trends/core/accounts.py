"""Social Trends - Account management and optimization scoring."""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from cli_anything.social_trends.core.session import Session

SUPPORTED_PLATFORMS = ["tiktok", "youtube", "instagram", "twitter", "facebook"]

# Optimization rules per platform
PLATFORM_OPTIMIZATION: Dict[str, Dict[str, Any]] = {
    "tiktok": {
        "posting_frequency": "1-4 times/day",
        "optimal_times": ["7:00-9:00 AM", "12:00-3:00 PM", "7:00-9:00 PM"],
        "content_length": "15-60 seconds for max reach; 3-5 min for depth",
        "bio_tip": "Use keywords in bio. Add link-in-bio tool. Include 1-2 niche hashtags.",
        "engagement_tip": "Reply to ALL comments in first 30 minutes. Use duet/stitch features.",
        "hook_tip": "First 1-3 seconds must hook. Text overlay boosts retention.",
        "trend_tip": "Jump on sounds within 24-48h of trending. Add trending hashtags immediately.",
        "max_engagement_rate": 5.96,
        "good_engagement_rate": 3.0,
        "average_engagement_rate": 1.5,
    },
    "youtube": {
        "posting_frequency": "2-3 times/week for Shorts; 1/week for long-form",
        "optimal_times": ["2:00-4:00 PM", "6:00-9:00 PM", "Fri-Sun"],
        "content_length": "Shorts: 15-60s; Long-form: 7-15 min for max ad revenue",
        "bio_tip": "Keyword-rich channel description. Link all social accounts. Add subscribe CTA.",
        "engagement_tip": "Pin a comment with a question. Reply within 2 hours of posting.",
        "hook_tip": "First 30 seconds determine watch time. Use chapters for long videos.",
        "trend_tip": "Title and thumbnail are #1 for CTR. Use trending keywords in title.",
        "max_engagement_rate": 3.5,
        "good_engagement_rate": 2.0,
        "average_engagement_rate": 0.8,
    },
    "instagram": {
        "posting_frequency": "3-7 posts/week; 2-10 Stories/day",
        "optimal_times": ["6:00-9:00 AM", "12:00-2:00 PM", "5:00-7:00 PM"],
        "content_length": "Reels: 7-15s or 30-60s; Carousels: 5-10 slides",
        "bio_tip": "5-7 keyword-rich words in name field. Clear value prop. Link-in-bio.",
        "engagement_tip": "Post Reels for reach. Use carousels for saves. Mix with feed posts.",
        "hook_tip": "Cover image determines Reel play rate. Bold text in first frame.",
        "trend_tip": "Use Remix feature. Track Reels trends in Explore. Pin top content.",
        "max_engagement_rate": 6.0,
        "good_engagement_rate": 3.0,
        "average_engagement_rate": 1.2,
    },
    "twitter": {
        "posting_frequency": "3-10 tweets/day including replies",
        "optimal_times": ["8:00-10:00 AM", "12:00-1:00 PM", "5:00-6:00 PM"],
        "content_length": "Tweets: 71-100 chars for max engagement",
        "bio_tip": "Front-load keywords. Use searchable terms. Add niche tags in name.",
        "engagement_tip": "Thread for depth. Reply to trending conversations. Quote retweet with value.",
        "hook_tip": "First 8 words decide if expanded. Lead with the most valuable insight.",
        "trend_tip": "Monitor trending tab daily. Tweet about trends within 30 minutes.",
        "max_engagement_rate": 2.0,
        "good_engagement_rate": 1.0,
        "average_engagement_rate": 0.3,
    },
    "facebook": {
        "posting_frequency": "1-2 posts/day",
        "optimal_times": ["1:00-4:00 PM", "Weekdays"],
        "content_length": "Video: 3-5 min; Post: 40-80 chars for feed",
        "bio_tip": "Complete all About fields. Add keywords. Use custom URL.",
        "engagement_tip": "Native video outperforms all. Ask questions to boost comments.",
        "hook_tip": "Thumbnail and first 3 seconds are critical for autoplay.",
        "trend_tip": "Facebook Watch trending. Share Reels natively (cross-post).",
        "max_engagement_rate": 3.0,
        "good_engagement_rate": 1.5,
        "average_engagement_rate": 0.5,
    },
}


def add_account(
    session: Session,
    name: str,
    platform: str,
    handle: str,
    niche: str = "",
) -> Dict[str, Any]:
    """Add a social media account to the project."""
    project = session.get_project()
    platform = platform.lower()

    if platform not in SUPPORTED_PLATFORMS:
        raise ValueError(f"Unsupported platform '{platform}'. Supported: {SUPPORTED_PLATFORMS}")

    # Check for duplicate handle+platform
    for acc in project.get("accounts", []):
        if acc["platform"] == platform and acc["handle"] == handle:
            raise ValueError(f"Account @{handle} on {platform} already exists.")

    account: Dict[str, Any] = {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "platform": platform,
        "handle": handle,
        "niche": niche,
        "added_at": datetime.now().isoformat(),
        "stats": {
            "followers": 0,
            "following": 0,
            "posts": 0,
            "avg_views": 0,
            "avg_likes": 0,
            "avg_comments": 0,
            "engagement_rate": 0.0,
        },
        "optimization_score": None,
        "last_optimized": None,
    }

    session.snapshot(f"add account {handle} on {platform}")
    project.setdefault("accounts", []).append(account)

    return account


def update_account_stats(
    session: Session,
    handle: str,
    platform: str,
    **stats: Any,
) -> Dict[str, Any]:
    """Update account statistics (followers, views, engagement, etc.)."""
    project = session.get_project()
    account = _find_account(project, handle, platform)

    session.snapshot(f"update stats {handle}")
    account["stats"].update({k: v for k, v in stats.items() if k in account["stats"]})

    # Recalculate engagement rate
    followers = account["stats"]["followers"]
    avg_likes = account["stats"]["avg_likes"]
    avg_comments = account["stats"]["avg_comments"]
    if followers > 0:
        account["stats"]["engagement_rate"] = round(
            ((avg_likes + avg_comments) / followers) * 100, 2
        )

    return account


def optimize_account(session: Session, handle: str, platform: str) -> Dict[str, Any]:
    """Generate a full optimization report for an account."""
    project = session.get_project()
    account = _find_account(project, handle, platform)
    rules = PLATFORM_OPTIMIZATION.get(platform, {})
    stats = account.get("stats", {})

    checks = []
    score = 0
    max_score = 0

    # Engagement check
    max_score += 25
    er = stats.get("engagement_rate", 0)
    good_er = rules.get("good_engagement_rate", 2.0)
    avg_er = rules.get("average_engagement_rate", 1.0)
    if er >= good_er:
        checks.append({"category": "Engagement Rate", "status": "good", "score": 25, "detail": f"{er}% (good)"})
        score += 25
    elif er >= avg_er:
        checks.append({"category": "Engagement Rate", "status": "ok", "score": 15, "detail": f"{er}% (average) — aim for {good_er}%+"})
        score += 15
    else:
        checks.append({"category": "Engagement Rate", "status": "needs work", "score": 5, "detail": f"{er}% (below average) — {rules.get('engagement_tip', '')}"})
        score += 5

    # Follower check
    max_score += 20
    followers = stats.get("followers", 0)
    if followers >= 10_000:
        checks.append({"category": "Audience Size", "status": "good", "score": 20, "detail": f"{followers:,} followers"})
        score += 20
    elif followers >= 1_000:
        checks.append({"category": "Audience Size", "status": "growing", "score": 12, "detail": f"{followers:,} followers — focus on consistency"})
        score += 12
    else:
        checks.append({"category": "Audience Size", "status": "early stage", "score": 5, "detail": f"{followers:,} followers — post daily to grow"})
        score += 5

    # Content volume
    max_score += 15
    posts = stats.get("posts", 0)
    if posts >= 50:
        checks.append({"category": "Content Volume", "status": "good", "score": 15, "detail": f"{posts} posts published"})
        score += 15
    elif posts >= 10:
        checks.append({"category": "Content Volume", "status": "ok", "score": 10, "detail": f"{posts} posts — maintain {rules.get('posting_frequency', 'regular')} posting"})
        score += 10
    else:
        checks.append({"category": "Content Volume", "status": "needs work", "score": 3, "detail": f"Only {posts} posts — increase to {rules.get('posting_frequency', 'daily')}"})
        score += 3

    # Niche clarity
    max_score += 15
    niche = account.get("niche", "")
    if niche:
        checks.append({"category": "Niche Clarity", "status": "good", "score": 15, "detail": f"Niche set: '{niche}'"})
        score += 15
    else:
        checks.append({"category": "Niche Clarity", "status": "missing", "score": 0, "detail": "No niche set — define your niche for better targeting"})

    # Platform-specific tip
    max_score += 25
    checks.append({"category": "Platform Strategy", "status": "tip", "score": 25, "detail": rules.get("trend_tip", "Follow trends in your niche")})
    score += 25

    pct = round((score / max_score) * 100) if max_score > 0 else 0
    grade = "A" if pct >= 85 else "B" if pct >= 70 else "C" if pct >= 55 else "D" if pct >= 40 else "F"

    report: Dict[str, Any] = {
        "handle": handle,
        "platform": platform,
        "optimization_score": pct,
        "grade": grade,
        "checks": checks,
        "top_tips": _top_tips(platform, stats, account.get("niche", "")),
        "posting_schedule": {
            "frequency": rules.get("posting_frequency"),
            "optimal_times": rules.get("optimal_times"),
        },
        "bio_optimization": rules.get("bio_tip"),
        "hook_strategy": rules.get("hook_tip"),
    }

    session.snapshot(f"optimize account {handle}")
    account["optimization_score"] = pct
    account["last_optimized"] = datetime.now().isoformat()

    return report


def list_accounts(session: Session, platform: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all accounts in the project."""
    project = session.get_project()
    accounts = project.get("accounts", [])
    if platform:
        accounts = [a for a in accounts if a["platform"] == platform]
    return accounts


def remove_account(session: Session, handle: str, platform: str) -> Dict[str, Any]:
    """Remove an account from the project."""
    project = session.get_project()
    before = len(project.get("accounts", []))
    project["accounts"] = [
        a for a in project.get("accounts", [])
        if not (a["handle"] == handle and a["platform"] == platform)
    ]
    removed = before - len(project["accounts"])
    if removed == 0:
        raise ValueError(f"Account @{handle} on {platform} not found.")
    session.snapshot(f"remove account {handle}")
    return {"removed": removed, "handle": handle, "platform": platform}


def _find_account(project: Dict[str, Any], handle: str, platform: str) -> Dict[str, Any]:
    for acc in project.get("accounts", []):
        if acc["handle"] == handle and acc["platform"] == platform:
            return acc
    handles = [f"@{a['handle']} ({a['platform']})" for a in project.get("accounts", [])]
    raise ValueError(f"Account @{handle} on {platform} not found. Existing: {handles}")


def _top_tips(platform: str, stats: Dict[str, Any], niche: str) -> List[str]:
    rules = PLATFORM_OPTIMIZATION.get(platform, {})
    tips = [
        f"Post at optimal times: {', '.join(rules.get('optimal_times', []))}",
        rules.get("engagement_tip", "Engage with your audience daily"),
        rules.get("hook_tip", "Strong hooks increase retention"),
        f"Optimal content length: {rules.get('content_length', 'varies')}",
    ]
    if not niche:
        tips.append("Define your niche to attract a targeted audience")
    er = stats.get("engagement_rate", 0)
    good_er = rules.get("good_engagement_rate", 2.0)
    if er < good_er:
        tips.append(f"Boost engagement: target {good_er}%+ engagement rate")
    return tips
