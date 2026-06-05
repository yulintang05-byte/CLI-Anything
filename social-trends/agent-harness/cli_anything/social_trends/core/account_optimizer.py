"""Account optimization engine for YouTube and TikTok accounts.

Scores accounts on profile completeness, posting cadence, hashtag strategy,
and content quality. Returns actionable improvement plans.
"""

from typing import Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
import math


# Optimal posting windows (UTC hours) by platform — based on aggregated engagement studies
_POSTING_WINDOWS = {
    "tiktok": {
        "best_hours": [6, 7, 9, 12, 14, 19, 20, 21],
        "best_days": ["Tuesday", "Thursday", "Friday", "Saturday"],
        "frequency": "1-3 posts/day",
        "tip": "TikTok's algorithm rewards daily posting. Post when your audience is online — check TikTok Analytics > Followers > Active Times.",
    },
    "youtube": {
        "best_hours": [14, 15, 16, 17, 20, 21],
        "best_days": ["Thursday", "Friday", "Saturday", "Sunday"],
        "frequency": "2-4 videos/week for growth; 1/week minimum",
        "tip": "YouTube Shorts: 1-2/day. Long-form: 2-3/week. Consistency beats volume.",
    },
    "instagram": {
        "best_hours": [8, 9, 11, 12, 17, 18, 21],
        "best_days": ["Monday", "Wednesday", "Friday"],
        "frequency": "4-7 posts/week + daily Stories",
        "tip": "Reels get 3-4x more reach than static posts. Prioritize Reels with trending audio.",
    },
}

# Engagement rate benchmarks (by follower tier)
_ENGAGEMENT_BENCHMARKS = {
    "tiktok": {
        "<1k": (5.0, 15.0),
        "1k-10k": (3.0, 9.0),
        "10k-100k": (2.0, 6.0),
        "100k-1m": (1.5, 4.0),
        ">1m": (1.0, 3.0),
    },
    "youtube": {
        "<1k": (4.0, 10.0),
        "1k-10k": (2.0, 6.0),
        "10k-100k": (1.0, 4.0),
        "100k-1m": (0.5, 2.0),
        ">1m": (0.2, 1.0),
    },
}


@dataclass
class AccountProfile:
    platform: str
    handle: str
    followers: int = 0
    following: int = 0
    total_posts: int = 0
    avg_views: int = 0
    avg_likes: int = 0
    avg_comments: int = 0
    has_profile_photo: bool = True
    has_bio: bool = False
    bio_text: str = ""
    has_link: bool = False
    posting_days_per_week: float = 0.0
    uses_hashtags: bool = False
    avg_hashtag_count: int = 0
    uses_trending_audio: bool = False
    has_cta_in_bio: bool = False
    niche: str = ""
    recent_video_views: list = field(default_factory=list)


class AccountOptimizer:
    """Score and optimize social media accounts."""

    def score_account(self, profile: AccountProfile) -> dict:
        """Run a full optimization audit and return score + action plan."""
        checks = []
        total = 0
        max_score = 0

        def check(name: str, passed: bool, points: int, fix: str, priority: str = "medium"):
            nonlocal total, max_score
            max_score += points
            earned = points if passed else 0
            total += earned
            checks.append({
                "check": name,
                "passed": passed,
                "points_earned": earned,
                "points_possible": points,
                "priority": priority,
                "fix": fix if not passed else "✓ Done",
            })

        # Profile completeness
        check("Profile photo set", profile.has_profile_photo, 5, "Add a clear, high-quality profile photo. Faces convert 40% better than logos.", "high")
        check("Bio filled in", profile.has_bio and len(profile.bio_text) > 20, 10, "Write a bio: WHO you are + WHAT you post + WHY follow + CTA (link/follow).", "high")
        check("CTA in bio", profile.has_cta_in_bio, 8, "Add a call to action: 'Follow for daily [niche] tips' or 'Link below for free [X]'.", "high")
        check("Link in bio", profile.has_link, 7, "Add a link (Linktree, landing page, or product) to capture traffic.", "medium")
        check("Niche defined", bool(profile.niche), 8, "Pick ONE niche and stick to it. Niche accounts grow 3x faster than general ones.", "high")

        # Posting cadence
        freq_ok = profile.posting_days_per_week >= (3 if profile.platform == "tiktok" else 2)
        check(
            "Posting frequency",
            freq_ok,
            12,
            f"Post more consistently. Aim for {_POSTING_WINDOWS.get(profile.platform, {}).get('frequency', '3x/week')}.",
            "high",
        )

        # Hashtag strategy
        hashtag_count_ok = 3 <= profile.avg_hashtag_count <= 8
        check("Hashtag count (3-8)", hashtag_count_ok, 8, "Use 3-8 targeted hashtags per post. More dilutes your content; fewer misses discovery.", "medium")
        check("Uses hashtags", profile.uses_hashtags, 5, "Add relevant hashtags to every post for discoverability.", "high")

        # Audio (TikTok/Reels)
        if profile.platform in ("tiktok", "instagram"):
            check("Uses trending audio", profile.uses_trending_audio, 10, "Use trending sounds from the TikTok/Instagram trending audio list. Trending audio gets 2-3x more push from the algorithm.", "high")

        # Engagement rate
        er = self._calc_engagement_rate(profile)
        er_tier = self._follower_tier(profile.followers)
        benchmark = _ENGAGEMENT_BENCHMARKS.get(profile.platform, {}).get(er_tier, (1.0, 5.0))
        er_ok = er >= benchmark[0]
        check(
            f"Engagement rate ≥ {benchmark[0]:.1f}% (your tier benchmark)",
            er_ok,
            15,
            f"Your ER is {er:.2f}%. Improve by: asking questions in captions, replying to all comments (first hour), posting at optimal times ({_POSTING_WINDOWS.get(profile.platform, {}).get('best_hours', [])}:00 UTC).",
            "high",
        )

        # Content consistency
        if profile.recent_video_views:
            consistency_ok = self._views_consistency(profile.recent_video_views) < 0.8
            check("View count consistency", consistency_ok, 7, "High variance in views = inconsistent content type. Find your best-performing format and double down.", "medium")

        pct = round(total / max_score * 100, 1) if max_score else 0
        grade = "A" if pct >= 85 else "B" if pct >= 70 else "C" if pct >= 55 else "D" if pct >= 40 else "F"

        return {
            "handle": profile.handle,
            "platform": profile.platform,
            "score": total,
            "max_score": max_score,
            "percent": pct,
            "grade": grade,
            "engagement_rate": f"{er:.2f}%",
            "follower_tier": er_tier,
            "checks": checks,
            "top_priorities": [c for c in checks if not c["passed"] and c["priority"] == "high"][:5],
            "posting_schedule": _POSTING_WINDOWS.get(profile.platform, {}),
        }

    def growth_plan(self, profile: AccountProfile, goal_followers: int, weeks: int = 12) -> dict:
        """Generate a concrete week-by-week growth plan."""
        current = profile.followers
        needed = goal_followers - current
        if needed <= 0:
            return {"message": "Already at or above goal!"}

        weekly_growth_needed = needed / weeks
        daily_posts = max(1, round(profile.posting_days_per_week)) if profile.posting_days_per_week else 1

        plan = []
        for week in range(1, weeks + 1):
            phase = "Foundation" if week <= 4 else "Growth" if week <= 8 else "Scale"
            actions = _week_actions(week, profile.platform, phase)
            plan.append({
                "week": week,
                "phase": phase,
                "target_followers": round(current + weekly_growth_needed * week),
                "posts_per_day": daily_posts + (1 if week > 4 else 0),
                "focus_actions": actions,
            })

        return {
            "current_followers": current,
            "goal_followers": goal_followers,
            "weeks": weeks,
            "weekly_growth_needed": round(weekly_growth_needed),
            "platform": profile.platform,
            "plan": plan,
        }

    def compare_accounts(self, profiles: list[AccountProfile]) -> list[dict]:
        """Score and rank multiple accounts."""
        scored = [self.score_account(p) for p in profiles]
        return sorted(scored, key=lambda x: x["score"], reverse=True)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _calc_engagement_rate(self, p: AccountProfile) -> float:
        if p.followers == 0 or p.avg_views == 0:
            return 0.0
        interactions = p.avg_likes + p.avg_comments
        return interactions / max(p.avg_views, p.followers) * 100

    def _follower_tier(self, followers: int) -> str:
        if followers < 1000:
            return "<1k"
        elif followers < 10_000:
            return "1k-10k"
        elif followers < 100_000:
            return "10k-100k"
        elif followers < 1_000_000:
            return "100k-1m"
        else:
            return ">1m"

    def _views_consistency(self, views: list[int]) -> float:
        if len(views) < 2:
            return 0.0
        mean = sum(views) / len(views)
        if mean == 0:
            return 0.0
        variance = sum((v - mean) ** 2 for v in views) / len(views)
        return math.sqrt(variance) / mean  # coefficient of variation


def _week_actions(week: int, platform: str, phase: str) -> list[str]:
    base = {
        "Foundation": [
            "Optimize profile (photo, bio, CTA, link)",
            "Research 5 top accounts in your niche — study their hooks & formats",
            "Post daily using trending hashtags",
            "Reply to EVERY comment within 1 hour of posting",
        ],
        "Growth": [
            "Duet/stitch top creators in your niche (TikTok) or reply to viral videos (YouTube)",
            "Test 3 different content formats this week",
            "Collaborate with 1 creator at similar follower count",
            "Analyze your best-performing post — replicate the format",
        ],
        "Scale": [
            "Cross-post to Instagram Reels / YouTube Shorts",
            "Add link in bio to capture leads",
            "Go live once this week for algorithmic boost",
            "Create a 'series' — episodic content keeps people returning",
        ],
    }
    actions = base.get(phase, [])
    if platform == "tiktok" and week % 4 == 0:
        actions.append("Check TikTok Trending page every morning for new sounds to use")
    if platform == "youtube" and week % 3 == 0:
        actions.append("Research 10 high-volume, low-competition keywords via YouTube autocomplete")
    return actions
