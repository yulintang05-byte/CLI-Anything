"""Account optimizer — analyzes your channels and generates actionable improvements.

Works with YouTube and TikTok accounts. Generates:
  - Bio optimization suggestions
  - Optimal posting schedule based on your niche
  - Content gap analysis (what trends you're missing)
  - Engagement rate benchmarking
  - Cross-posting recommendations
"""

import json
import re
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Optional


# Industry-average engagement benchmarks by platform
_YT_BENCHMARKS = {
    "micro": {"subs": (0, 10_000), "avg_er": 6.0},
    "small": {"subs": (10_000, 100_000), "avg_er": 3.5},
    "mid": {"subs": (100_000, 1_000_000), "avg_er": 2.0},
    "large": {"subs": (1_000_000, float("inf")), "avg_er": 1.2},
}
_TT_BENCHMARKS = {
    "micro": {"followers": (0, 10_000), "avg_er": 9.0},
    "small": {"followers": (10_000, 100_000), "avg_er": 6.0},
    "mid": {"followers": (100_000, 1_000_000), "avg_er": 4.5},
    "large": {"followers": (1_000_000, float("inf")), "avg_er": 3.0},
}

# Best posting times per niche (UTC hours) — based on aggregated studies
_POSTING_SCHEDULE = {
    "fitness":    {"days": ["Mon", "Wed", "Fri", "Sun"], "hours_utc": [6, 12, 17]},
    "food":       {"days": ["Tue", "Thu", "Sat", "Sun"], "hours_utc": [11, 17, 20]},
    "travel":     {"days": ["Mon", "Fri", "Sat", "Sun"], "hours_utc": [7, 13, 19]},
    "tech":       {"days": ["Mon", "Tue", "Wed", "Thu"], "hours_utc": [9, 15, 21]},
    "beauty":     {"days": ["Tue", "Thu", "Sat", "Sun"], "hours_utc": [10, 16, 20]},
    "gaming":     {"days": ["Fri", "Sat", "Sun"],         "hours_utc": [15, 19, 22]},
    "motivation": {"days": ["Mon", "Wed", "Fri"],          "hours_utc": [6, 7, 17]},
    "finance":    {"days": ["Mon", "Tue", "Wed", "Thu"],  "hours_utc": [8, 12, 18]},
    "fashion":    {"days": ["Tue", "Thu", "Sat"],          "hours_utc": [10, 15, 19]},
    "comedy":     {"days": ["Thu", "Fri", "Sat", "Sun"],  "hours_utc": [16, 20, 22]},
    "default":    {"days": ["Mon", "Wed", "Fri", "Sat"],  "hours_utc": [9, 15, 20]},
}

_BIO_MAX_CHARS = {"youtube": 1000, "tiktok": 80}
_BIO_MUST_HAVES = [
    "niche keyword",
    "value proposition",
    "posting frequency",
    "call-to-action",
]


@dataclass
class AccountAudit:
    platform: str
    username: str
    niche: str
    follower_count: int
    tier: str
    current_er: float
    benchmark_er: float
    er_vs_benchmark: str
    bio_score: int
    bio_suggestions: list[str]
    posting_schedule: dict
    content_gaps: list[str]
    trending_topics_to_cover: list[str]
    cross_platform_tips: list[str]
    quick_wins: list[str]
    score: int
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AccountOptimizer:
    def __init__(self):
        self._accounts: dict[str, dict] = {}
        self._trending_hashtags: list[str] = []
        self._trending_topics: list[str] = []
        self._niche: str = "default"

    # ── Setup ──────────────────────────────────────────────────────────

    def set_niche(self, niche: str) -> None:
        self._niche = niche.lower()

    def feed_trending_hashtags(self, tags: list[str]) -> None:
        self._trending_hashtags = [t.lstrip("#").lower() for t in tags]

    def feed_trending_topics(self, topics: list[str]) -> None:
        self._trending_topics = topics

    def register_account(self, platform: str, username: str, stats: dict) -> None:
        key = f"{platform}:{username}"
        self._accounts[key] = {"platform": platform, "username": username, **stats}

    # ── Core audit ────────────────────────────────────────────────────

    def audit_youtube_account(
        self, channel_stats: dict, recent_videos: list[dict], niche: Optional[str] = None
    ) -> AccountAudit:
        niche = niche or self._niche
        subs = channel_stats.get("subscriber_count", 0)
        tier = _yt_tier(subs)
        benchmark = _YT_BENCHMARKS[tier]["avg_er"]

        # Compute actual ER from recent videos
        ers = [v.get("engagement_rate", 0) for v in recent_videos if v.get("engagement_rate", 0) > 0]
        actual_er = round(sum(ers) / len(ers), 2) if ers else 0.0
        er_label = _er_label(actual_er, benchmark)

        bio = channel_stats.get("description", "")
        bio_score, bio_suggestions = _audit_bio(bio, "youtube", niche)

        schedule = _POSTING_SCHEDULE.get(niche, _POSTING_SCHEDULE["default"])
        gaps = self._find_content_gaps(recent_videos, niche)
        quick_wins = self._quick_wins_youtube(channel_stats, recent_videos, actual_er, benchmark, niche)
        cross_tips = _cross_platform_tips("youtube", niche)

        score = _overall_score(bio_score, actual_er, benchmark, len(quick_wins))

        return AccountAudit(
            platform="youtube",
            username=channel_stats.get("name", channel_stats.get("custom_url", "unknown")),
            niche=niche,
            follower_count=subs,
            tier=tier,
            current_er=actual_er,
            benchmark_er=benchmark,
            er_vs_benchmark=er_label,
            bio_score=bio_score,
            bio_suggestions=bio_suggestions,
            posting_schedule=schedule,
            content_gaps=gaps,
            trending_topics_to_cover=self._trending_topics[:10],
            cross_platform_tips=cross_tips,
            quick_wins=quick_wins,
            score=score,
        )

    def audit_tiktok_account(
        self, account_stats: dict, recent_videos: list[dict] = None, niche: Optional[str] = None
    ) -> AccountAudit:
        niche = niche or self._niche
        recent_videos = recent_videos or []
        followers = account_stats.get("follower_count", 0)
        tier = _tt_tier(followers)
        benchmark = _TT_BENCHMARKS[tier]["avg_er"]

        ers = [v.get("engagement_rate", 0) for v in recent_videos if v.get("engagement_rate", 0) > 0]
        actual_er = round(sum(ers) / len(ers), 2) if ers else 0.0
        er_label = _er_label(actual_er, benchmark)

        bio = account_stats.get("bio", "")
        bio_score, bio_suggestions = _audit_bio(bio, "tiktok", niche)

        schedule = _POSTING_SCHEDULE.get(niche, _POSTING_SCHEDULE["default"])
        gaps = self._find_content_gaps(recent_videos, niche)
        quick_wins = self._quick_wins_tiktok(account_stats, actual_er, benchmark, niche)
        cross_tips = _cross_platform_tips("tiktok", niche)

        score = _overall_score(bio_score, actual_er, benchmark, len(quick_wins))

        return AccountAudit(
            platform="tiktok",
            username=account_stats.get("username", "unknown"),
            niche=niche,
            follower_count=followers,
            tier=tier,
            current_er=actual_er,
            benchmark_er=benchmark,
            er_vs_benchmark=er_label,
            bio_score=bio_score,
            bio_suggestions=bio_suggestions,
            posting_schedule=schedule,
            content_gaps=gaps,
            trending_topics_to_cover=self._trending_topics[:10],
            cross_platform_tips=cross_tips,
            quick_wins=quick_wins,
            score=score,
        )

    def generate_optimization_report(self, audits: list[AccountAudit]) -> dict:
        """Combine multiple account audits into a unified action plan."""
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "niche": self._niche,
            "accounts": [asdict(a) for a in audits],
            "unified_action_plan": self._unified_action_plan(audits),
            "trending_hashtags_to_use": self._trending_hashtags[:30],
            "trending_topics_to_cover": self._trending_topics[:10],
        }

    def to_json(self, report: dict) -> str:
        return json.dumps(report, indent=2, default=str)

    # ── Internal helpers ──────────────────────────────────────────────

    def _find_content_gaps(self, videos: list[dict], niche: str) -> list[str]:
        existing_topics = " ".join(
            v.get("title", "") + " " + " ".join(v.get("tags", []))
            for v in videos
        ).lower()
        gaps = []
        for trend in self._trending_topics:
            kw = trend.lower()
            if kw not in existing_topics:
                gaps.append(f"Missing: '{trend}' — currently trending in your niche")
        for tag in self._trending_hashtags[:20]:
            if f"#{tag}" not in existing_topics and tag not in existing_topics:
                gaps.append(f"Unused trending hashtag: #{tag}")
        return gaps[:15]

    def _quick_wins_youtube(
        self, stats: dict, videos: list[dict], er: float, benchmark: float, niche: str
    ) -> list[str]:
        wins = []
        if er < benchmark * 0.7:
            wins.append("Add end screens and cards to all videos to boost engagement")
        if not stats.get("custom_url"):
            wins.append("Claim your custom YouTube handle (improves discoverability)")
        desc = stats.get("description", "")
        if len(desc) < 200:
            wins.append("Expand channel description with keywords and links")
        if videos:
            no_tags = [v for v in videos if not v.get("tags")]
            if len(no_tags) > len(videos) // 3:
                wins.append(f"{len(no_tags)} recent videos have no tags — add trending tags immediately")
        wins.append("Pin your best-performing video as channel trailer")
        wins.append(f"Post {niche} content on {', '.join(_POSTING_SCHEDULE.get(niche, _POSTING_SCHEDULE['default'])['days'])} for maximum reach")
        wins.append("Add chapter markers to videos longer than 5 minutes")
        return wins

    def _quick_wins_tiktok(
        self, stats: dict, er: float, benchmark: float, niche: str
    ) -> list[str]:
        wins = []
        if er < benchmark * 0.7:
            wins.append("Reply to every comment in first hour of posting (boosts algorithm ranking)")
        bio = stats.get("bio", "")
        if len(bio) < 40:
            wins.append("TikTok bio is too short — add niche keywords and a CTA link")
        if not stats.get("verified"):
            wins.append("Apply for Creator Program to unlock analytics and monetization")
        wins.append("Use trending sounds from the past 48 hours on next 3 posts")
        wins.append(f"Duet or stitch a viral {niche} video to piggyback trending traffic")
        wins.append("Post 1-3 times daily during your peak hours for 14 days straight")
        wins.append("Add text overlay and closed captions to all videos (boosts watch time)")
        return wins

    def _unified_action_plan(self, audits: list[AccountAudit]) -> list[str]:
        plan = [
            "WEEK 1 — Foundation",
            "  1. Apply all bio optimizations across all accounts",
            "  2. Implement trending hashtag strategy from this report",
            "  3. Set up content calendar based on optimal posting schedule",
            "",
            "WEEK 2 — Content Blitz",
            "  4. Create content covering all identified content gaps",
            "  5. Use top 3 trending sounds on TikTok posts",
            "  6. Publish YouTube Shorts versions of TikTok content",
            "",
            "WEEK 3 — Cross-Promotion",
            "  7. Cross-post all content across platforms with platform-native formatting",
            "  8. Engage in trending hashtag communities daily (30 min/day)",
            "  9. Collaborate or duet with accounts in same niche",
            "",
            "WEEK 4 — Analyze & Iterate",
            " 10. Review analytics — double down on top-performing content formats",
            " 11. Update hashtag strategy with fresh scrape from this tool",
            " 12. A/B test thumbnails and hooks on 2 videos",
        ]
        # Add platform-specific quick wins
        for audit in audits:
            plan.append(f"\n[{audit.platform.upper()} @{audit.username}] Priority actions:")
            for i, win in enumerate(audit.quick_wins[:3], 1):
                plan.append(f"  {i}. {win}")
        return plan


# ── Pure helpers ──────────────────────────────────────────────────────────

def _yt_tier(subs: int) -> str:
    for tier, info in _YT_BENCHMARKS.items():
        lo, hi = info["subs"]
        if lo <= subs < hi:
            return tier
    return "micro"


def _tt_tier(followers: int) -> str:
    for tier, info in _TT_BENCHMARKS.items():
        lo, hi = info["followers"]
        if lo <= followers < hi:
            return tier
    return "micro"


def _er_label(actual: float, benchmark: float) -> str:
    if actual >= benchmark * 1.5:
        return f"EXCELLENT (+{round((actual/benchmark-1)*100)}% vs benchmark)"
    if actual >= benchmark:
        return f"ABOVE AVERAGE (+{round((actual/benchmark-1)*100)}% vs benchmark)"
    if actual >= benchmark * 0.7:
        return f"BELOW AVERAGE (-{round((1-actual/benchmark)*100)}% vs benchmark)"
    return f"LOW (-{round((1-actual/benchmark)*100)}% vs benchmark — needs immediate attention)"


def _audit_bio(bio: str, platform: str, niche: str) -> tuple[int, list[str]]:
    score = 0
    suggestions = []
    max_chars = _BIO_MAX_CHARS.get(platform, 500)
    bio_lower = bio.lower()

    if len(bio) > max_chars * 0.5:
        score += 20
    else:
        suggestions.append(f"Bio is short — use up to {max_chars} characters to explain your value")

    if niche.lower() in bio_lower or any(w in bio_lower for w in niche.split()):
        score += 20
    else:
        suggestions.append(f"Add your niche keyword '{niche}' to bio for SEO discoverability")

    call_to_actions = ["link in bio", "subscribe", "follow", "check out", "dm me", "join", "click"]
    if any(cta in bio_lower for cta in call_to_actions):
        score += 20
    else:
        suggestions.append("Add a clear call-to-action (e.g. 'New videos every Mon/Wed/Fri')")

    if re.search(r"(https?://|linktr\.ee|bit\.ly|beacons\.ai)", bio, re.I):
        score += 20
    else:
        suggestions.append("Add a link (Linktree or direct URL) to drive traffic to other channels/products")

    if platform == "tiktok" and len(bio) > 60:
        score += 20
    elif platform == "youtube" and any(
        w in bio_lower for w in ["every", "weekly", "daily", "mon", "wed", "fri"]
    ):
        score += 20
    else:
        suggestions.append("Mention your posting schedule to set viewer expectations")

    return score, suggestions


def _cross_platform_tips(platform: str, niche: str) -> list[str]:
    tips = {
        "youtube": [
            "Post TikTok-style Shorts (under 60s) to appear in YouTube Shorts feed",
            "Mention your TikTok handle in every video outro",
            "Use YouTube Community tab to tease upcoming content (drives retention)",
            "Mirror your TikTok thumbnails as YouTube Shorts covers for brand consistency",
        ],
        "tiktok": [
            "Post YouTube link in bio and mention it in every 5th video",
            "Repurpose long YouTube content as 15-60s TikTok hooks",
            "Go Live on TikTok weekly — algorithm heavily boosts Live creators",
            "Create TikTok series (Part 1, Part 2) to drive profile visits and follows",
        ],
    }
    return tips.get(platform, [])


def _overall_score(bio_score: int, er: float, benchmark: float, gaps_count: int) -> int:
    score = bio_score  # 0-100
    er_ratio = min(er / max(benchmark, 0.1), 2.0)
    score += int(er_ratio * 30)  # 0-60 bonus
    score -= min(gaps_count * 2, 20)  # penalty for gaps
    return max(0, min(100, score))
