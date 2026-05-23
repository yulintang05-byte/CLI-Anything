"""Trend analyzer — cross-platform trend aggregation and ranking.

Combines TikTok and YouTube data to identify the highest-value trends
for content creation and account growth.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field, asdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cli_anything.social_trends.core.tiktok_scraper import TikTokTrendReport
    from cli_anything.social_trends.core.youtube_scraper import YouTubeTrendReport


@dataclass
class CrossPlatformTrend:
    """A trend detected on one or both platforms."""
    keyword: str
    platforms: list[str] = field(default_factory=list)
    tiktok_score: float = 0.0      # 0–100 based on views/videos
    youtube_score: float = 0.0     # 0–100 based on views/frequency
    cross_platform_score: float = 0.0
    tiktok_views: int = 0
    youtube_views: int = 0
    category: str = ""             # hashtag / sound / topic / music
    recommendation: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TrendAnalysis:
    """Full cross-platform trend analysis result."""
    analyzed_at: str = ""
    top_trends: list[CrossPlatformTrend] = field(default_factory=list)
    best_hashtags: list[str] = field(default_factory=list)
    best_sounds: list[str] = field(default_factory=list)
    posting_strategy: list[str] = field(default_factory=list)
    content_ideas: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "analyzed_at": self.analyzed_at,
            "top_trends": [t.to_dict() for t in self.top_trends],
            "best_hashtags": self.best_hashtags,
            "best_sounds": self.best_sounds,
            "posting_strategy": self.posting_strategy,
            "content_ideas": self.content_ideas,
        }


# ── Scoring helpers ────────────────────────────────────────────────────

def _normalize(values: list[float], cap: float = 100.0) -> list[float]:
    """Min-max normalize a list to [0, cap]."""
    if not values:
        return values
    mn, mx = min(values), max(values)
    if mx == mn:
        return [cap / 2.0] * len(values)
    return [(v - mn) / (mx - mn) * cap for v in values]


# ── Analyzer ──────────────────────────────────────────────────────────

class TrendAnalyzer:
    """Aggregate TikTok + YouTube trend data into actionable insights."""

    def analyze(
        self,
        tiktok_report: "TikTokTrendReport | None" = None,
        youtube_report: "YouTubeTrendReport | None" = None,
    ) -> TrendAnalysis:
        from datetime import datetime, timezone

        trends: dict[str, CrossPlatformTrend] = {}

        # ── Ingest TikTok hashtags ──────────────────────────────────────
        if tiktok_report:
            ht_views = [h.view_count for h in tiktok_report.trending_hashtags]
            scores = _normalize([float(v) for v in ht_views])
            for ht, score in zip(tiktok_report.trending_hashtags, scores):
                key = ht.name.lower()
                if key not in trends:
                    trends[key] = CrossPlatformTrend(keyword=key, category="hashtag")
                trends[key].tiktok_score = score
                trends[key].tiktok_views = ht.view_count
                if "TikTok" not in trends[key].platforms:
                    trends[key].platforms.append("TikTok")

        # ── Ingest TikTok sounds ────────────────────────────────────────
        if tiktok_report:
            sound_counts = [s.video_count or s.play_count for s in tiktok_report.trending_sounds]
            scores = _normalize([float(c) for c in sound_counts])
            for sound, score in zip(tiktok_report.trending_sounds, scores):
                key = f"{sound.title} — {sound.artist}".lower()
                if key not in trends:
                    trends[key] = CrossPlatformTrend(keyword=key, category="sound")
                trends[key].tiktok_score = max(trends[key].tiktok_score, score)
                if "TikTok" not in trends[key].platforms:
                    trends[key].platforms.append("TikTok")

        # ── Ingest YouTube hashtags ─────────────────────────────────────
        if youtube_report:
            yt_ht_list = youtube_report.top_hashtags
            for i, ht in enumerate(yt_ht_list):
                key = ht.lower().lstrip("#")
                score = max(0.0, 100.0 - i * (100.0 / max(len(yt_ht_list), 1)))
                if key not in trends:
                    trends[key] = CrossPlatformTrend(keyword=key, category="hashtag")
                trends[key].youtube_score = score
                if "YouTube" not in trends[key].platforms:
                    trends[key].platforms.append("YouTube")

        # ── Ingest YouTube music ────────────────────────────────────────
        if youtube_report:
            yt_views = [m.view_count for m in youtube_report.trending_music]
            scores = _normalize([float(v) for v in yt_views])
            for music, score in zip(youtube_report.trending_music, scores):
                key = f"{music.title} — {music.artist}".lower()
                if key not in trends:
                    trends[key] = CrossPlatformTrend(keyword=key, category="music")
                trends[key].youtube_score = max(trends[key].youtube_score, score)
                trends[key].youtube_views = music.view_count
                if "YouTube" not in trends[key].platforms:
                    trends[key].platforms.append("YouTube")

        # ── Compute cross-platform score ────────────────────────────────
        for t in trends.values():
            cross_bonus = 20.0 if len(t.platforms) > 1 else 0.0
            t.cross_platform_score = (t.tiktok_score * 0.6 + t.youtube_score * 0.4) + cross_bonus
            t.cross_platform_score = min(t.cross_platform_score, 100.0)

        ranked = sorted(trends.values(), key=lambda t: t.cross_platform_score, reverse=True)

        # ── Generate recommendations ────────────────────────────────────
        for t in ranked:
            if len(t.platforms) > 1:
                t.recommendation = "🔥 CROSS-PLATFORM VIRAL — use immediately"
            elif t.tiktok_score >= 80:
                t.recommendation = "⚡ TikTok explosive — post with this trend NOW"
            elif t.youtube_score >= 80:
                t.recommendation = "📺 YouTube trending — adapt for Shorts/Reels"
            elif t.cross_platform_score >= 60:
                t.recommendation = "📈 Rising trend — get in early"
            else:
                t.recommendation = "👀 Watch this trend — monitor for 48h"

        # ── Best hashtags ───────────────────────────────────────────────
        best_hashtags = [
            f"#{t.keyword}"
            for t in ranked
            if t.category == "hashtag"
        ][:25]

        # ── Best sounds ─────────────────────────────────────────────────
        best_sounds = [
            t.keyword
            for t in ranked
            if t.category in ("sound", "music")
        ][:15]

        # ── Posting strategy ────────────────────────────────────────────
        strategy = _build_posting_strategy(ranked, tiktok_report, youtube_report)

        # ── Content ideas ────────────────────────────────────────────────
        content_ideas = _generate_content_ideas(ranked)

        return TrendAnalysis(
            analyzed_at=datetime.now(timezone.utc).isoformat(),
            top_trends=ranked[:50],
            best_hashtags=best_hashtags,
            best_sounds=best_sounds,
            posting_strategy=strategy,
            content_ideas=content_ideas,
        )


def _build_posting_strategy(
    trends: list[CrossPlatformTrend],
    tiktok_report,
    youtube_report,
) -> list[str]:
    """Build a data-driven posting strategy from trend analysis."""
    strategy = []

    cross_platform = [t for t in trends if len(t.platforms) > 1]
    tiktok_only = [t for t in trends if t.platforms == ["TikTok"] and t.tiktok_score >= 70]
    yt_only = [t for t in trends if t.platforms == ["YouTube"] and t.youtube_score >= 70]

    if cross_platform:
        strategy.append(
            f"PRIORITY 1 — {len(cross_platform)} cross-platform trends detected. "
            "Post within 24 hours using: "
            + ", ".join(f"#{t.keyword}" for t in cross_platform[:5])
        )

    if tiktok_only:
        strategy.append(
            f"PRIORITY 2 — TikTok-specific: Use sounds from trending list. "
            "Hashtag stack: " + " ".join(f"#{t.keyword}" for t in tiktok_only[:5])
        )

    if yt_only:
        strategy.append(
            f"PRIORITY 3 — YouTube/Shorts: Repurpose as vertical 60s clips. "
            "Topics: " + ", ".join(t.keyword for t in yt_only[:5])
        )

    strategy += [
        "POST TIMING: TikTok — 6-10am, 7-9pm ET (highest FYP push windows)",
        "POST TIMING: YouTube Shorts — 12-3pm ET (peak discovery)",
        "HASHTAG FORMULA: 3 mega (#fyp, #viral) + 5 niche + 2 branded = 10 total",
        "SOUND STRATEGY: Use trending audio within 48h of it peaking for 2-3x reach",
        "VIDEO LENGTH: TikTok 7-15s for max completion rate; 21-34s for storytelling",
        "CAPTION: Hook in first 3 words. End with CTA question to boost comments",
        "POSTING FREQUENCY: 1-3x/day TikTok; 1x/day YouTube Shorts for algorithm favor",
        "ENGAGEMENT: Reply to ALL comments within 1h of posting — boosts distribution",
    ]
    return strategy


def _generate_content_ideas(trends: list[CrossPlatformTrend]) -> list[str]:
    """Generate content ideas based on trending topics."""
    ideas = []
    hashtag_trends = [t for t in trends if t.category == "hashtag"][:5]
    sound_trends = [t for t in trends if t.category in ("sound", "music")][:3]

    for t in hashtag_trends:
        ideas.append(f"#{t.keyword} video: React to or demonstrate '{t.keyword}' in your niche")

    for t in sound_trends:
        ideas.append(
            f"Use trending sound '{t.keyword}' — lip sync, transition, or POV format"
        )

    ideas += [
        "Day-in-the-life using 3+ trending sounds back-to-back",
        "Duet or stitch with a viral creator in your niche",
        "'POV: You found out about [trending topic]' format",
        "Storytime over trending audio — 3-part series",
        "Product/service demo using current trending template",
        "'Rating viral [niche] trends' reaction video",
        "Comment bait: 'Which [option A] or [option B]?' over trending music",
        "Behind-the-scenes with trending sound overlay",
    ]
    return ideas
