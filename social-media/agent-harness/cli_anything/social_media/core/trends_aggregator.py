"""Cross-platform trend aggregation — merges YouTube + TikTok signals
into unified viral intelligence reports.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

from cli_anything.social_media.core.youtube_scraper import (
    YouTubeTrendsResult, scrape_youtube_trending
)
from cli_anything.social_media.core.tiktok_scraper import (
    TikTokTrendsResult, scrape_tiktok_trending
)


@dataclass
class UnifiedTrend:
    """A trend present on both (or one) platform(s) with combined signal."""
    keyword: str
    platforms: list[str]               # ['youtube', 'tiktok']
    combined_score: float
    youtube_avg_views: int
    tiktok_avg_plays: int
    hashtag_count_yt: int
    hashtag_count_tt: int
    recommended_caption: str           # ready-to-use caption snippet
    recommended_hashtags: list[str]    # merged top hashtags

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CrossPlatformReport:
    generated_at: str
    niche: str
    region: str
    youtube: Optional[dict]
    tiktok: Optional[dict]
    unified_trends: list[UnifiedTrend]
    master_hashtags: list[str]         # top hashtags valid on both platforms
    master_sounds: list[str]           # music / sounds to use
    proactive_actions: list[str]       # prioritized action items

    def to_dict(self) -> dict:
        return {
            "generated_at": self.generated_at,
            "niche": self.niche,
            "region": self.region,
            "youtube": self.youtube,
            "tiktok": self.tiktok,
            "unified_trends": [t.to_dict() for t in self.unified_trends],
            "master_hashtags": self.master_hashtags,
            "master_sounds": self.master_sounds,
            "proactive_actions": self.proactive_actions,
        }


# ── Aggregation logic ─────────────────────────────────────────────────

def _merge_hashtags(
    yt_tags: list[dict],
    tt_tags: list[dict],
    top_n: int = 30,
) -> list[str]:
    """Merge YouTube + TikTok hashtag lists into a prioritized master list."""
    scores: dict[str, float] = {}

    for h in yt_tags:
        tag = h["tag"].lower()
        scores[tag] = scores.get(tag, 0) + h.get("trend_score", 0) * 1.0

    for h in tt_tags:
        tag = h["tag"].lower()
        # TikTok discovery weight slightly higher — bigger viral amplifier
        scores[tag] = scores.get(tag, 0) + h.get("trend_score", 0) * 1.2

    # Sort by combined score
    sorted_tags = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [f"#{tag}" for tag, _ in sorted_tags[:top_n]]


def _merge_sounds(
    yt_music: list,
    tt_music: list,
    top_n: int = 10,
) -> list[str]:
    """Merge YouTube + TikTok music/sounds into a master list."""
    sounds: dict[str, float] = {}

    for m in yt_music:
        title = m.title if hasattr(m, "title") else m.get("title", "")
        artist = m.artist if hasattr(m, "artist") else m.get("artist", "")
        score = m.trend_score if hasattr(m, "trend_score") else m.get("trend_score", 0)
        key = f"{title} - {artist}".strip(" -")
        if key:
            sounds[key] = sounds.get(key, 0) + score * 0.8

    for m in tt_music:
        title = m.title if hasattr(m, "title") else m.get("title", "")
        artist = m.artist if hasattr(m, "artist") else m.get("artist", "")
        score = m.trend_score if hasattr(m, "trend_score") else m.get("trend_score", 0)
        key = f"{title} - {artist}".strip(" -")
        if key:
            sounds[key] = sounds.get(key, 0) + score * 1.0

    sorted_sounds = sorted(sounds.items(), key=lambda x: x[1], reverse=True)
    return [s for s, _ in sorted_sounds[:top_n]]


def _build_unified_trends(
    yt_result: Optional[YouTubeTrendsResult],
    tt_result: Optional[TikTokTrendsResult],
) -> list[UnifiedTrend]:
    """Find cross-platform keywords and build UnifiedTrend objects."""
    yt_tag_map: dict[str, dict] = {}
    tt_tag_map: dict[str, dict] = {}

    if yt_result:
        for h in yt_result.top_hashtags:
            yt_tag_map[h["tag"]] = h

    if tt_result:
        for h in tt_result.top_hashtags:
            tt_tag_map[h["tag"]] = h

    all_tags = set(yt_tag_map.keys()) | set(tt_tag_map.keys())
    unified: list[UnifiedTrend] = []

    for tag in all_tags:
        platforms = []
        yt_views = 0
        tt_plays = 0
        yt_count = 0
        tt_count = 0
        score = 0.0

        if tag in yt_tag_map:
            platforms.append("youtube")
            yt_views = yt_tag_map[tag].get("avg_views", 0)
            yt_count = yt_tag_map[tag].get("count", 0)
            score += yt_tag_map[tag].get("trend_score", 0) * 1.0

        if tag in tt_tag_map:
            platforms.append("tiktok")
            tt_plays = tt_tag_map[tag].get("avg_plays", 0)
            tt_count = tt_tag_map[tag].get("count", 0)
            score += tt_tag_map[tag].get("trend_score", 0) * 1.2

        # Cross-platform bonus — tag is hot on both
        if len(platforms) == 2:
            score *= 1.5

        # Build a recommended caption snippet
        caption = f"#{tag} — trending across {' & '.join(p.capitalize() for p in platforms)}"

        # Top related hashtags
        related = []
        if tag in yt_tag_map and yt_result:
            related += [h["tag"] for h in yt_result.top_hashtags[:5] if h["tag"] != tag]
        if tag in tt_tag_map and tt_result:
            related += [h["tag"] for h in tt_result.top_hashtags[:5] if h["tag"] != tag]
        related_unique = list(dict.fromkeys(related))[:8]

        unified.append(UnifiedTrend(
            keyword=tag,
            platforms=platforms,
            combined_score=round(score, 4),
            youtube_avg_views=yt_views,
            tiktok_avg_plays=tt_plays,
            hashtag_count_yt=yt_count,
            hashtag_count_tt=tt_count,
            recommended_caption=caption,
            recommended_hashtags=[f"#{t}" for t in related_unique],
        ))

    unified.sort(key=lambda x: x.combined_score, reverse=True)
    return unified[:40]


def _build_proactive_actions(
    yt_result: Optional[YouTubeTrendsResult],
    tt_result: Optional[TikTokTrendsResult],
    unified: list[UnifiedTrend],
    master_hashtags: list[str],
    master_sounds: list[str],
) -> list[str]:
    """Generate a prioritized action plan from all available data."""
    actions = []

    # Immediate wins
    if unified:
        top = unified[0]
        actions.append(
            f"[PRIORITY 1] Create a post around '#{top.keyword}' — "
            f"highest combined score across {', '.join(top.platforms)}"
        )

    if master_sounds:
        actions.append(
            f"[PRIORITY 2] Use this sound immediately: '{master_sounds[0]}' — "
            "trending on both platforms right now"
        )

    if master_hashtags:
        tag_str = " ".join(master_hashtags[:7])
        actions.append(
            f"[PRIORITY 3] Copy-paste this hashtag block into your next post: {tag_str}"
        )

    # YouTube-specific
    if yt_result and yt_result.viral_patterns:
        actions.append(f"[YOUTUBE] {yt_result.viral_patterns[0]}")
    if yt_result and yt_result.top_hashtags:
        yt_top = yt_result.top_hashtags[0]
        actions.append(
            f"[YOUTUBE] Top tag: #{yt_top['tag']} "
            f"({yt_top['count']} viral videos, avg {yt_top['avg_views']:,} views)"
        )

    # TikTok-specific
    if tt_result and tt_result.content_strategy:
        for s in tt_result.content_strategy[:3]:
            actions.append(f"[TIKTOK] {s}")

    # Cross-platform amplification
    cross_tags = [t for t in unified if len(t.platforms) == 2]
    if cross_tags:
        actions.append(
            f"[CROSS-PLATFORM] {len(cross_tags)} hashtags trending on BOTH YouTube & TikTok — "
            "post same content to both platforms simultaneously for maximum reach"
        )

    # Theme page growth
    actions.append(
        "[GROWTH] Repost 3 viral videos per day from your niche using ScreenShot/Repost tools — "
        "credit original creators to build goodwill and get reshares"
    )
    actions.append(
        "[GROWTH] Engage with top 5 viral posts in your niche within 1h of their posting — "
        "early comments boost your account visibility in the same feed"
    )

    return actions


# ── Public API ────────────────────────────────────────────────────────

def generate_cross_platform_report(
    niche: str = "general",
    region: str = "US",
    max_results: int = 25,
    include_youtube: bool = True,
    include_tiktok: bool = True,
    yt_category: str = "trending",
) -> CrossPlatformReport:
    """Generate a full cross-platform viral intelligence report.

    Args:
        niche: Content niche for TikTok ('fitness', 'finance', 'food',
               'beauty', 'travel', 'fashion', 'comedy', 'education', 'general').
        region: Target region code (e.g., 'US', 'GB').
        max_results: Videos to analyze per platform.
        include_youtube: Whether to scrape YouTube.
        include_tiktok: Whether to scrape TikTok.
        yt_category: YouTube trending category ('trending', 'music',
                     'gaming', 'movies').

    Returns:
        CrossPlatformReport with all trend data and action items.
    """
    yt_result: Optional[YouTubeTrendsResult] = None
    tt_result: Optional[TikTokTrendsResult] = None

    if include_youtube:
        yt_result = scrape_youtube_trending(
            category=yt_category, region=region, max_results=max_results
        )

    if include_tiktok:
        tt_result = scrape_tiktok_trending(
            niche=niche, region=region, max_results=max_results
        )

    yt_tags = yt_result.top_hashtags if yt_result else []
    tt_tags = tt_result.top_hashtags if tt_result else []
    yt_music = yt_result.trending_music if yt_result else []
    tt_music = tt_result.trending_music if tt_result else []

    master_hashtags = _merge_hashtags(yt_tags, tt_tags)
    master_sounds = _merge_sounds(yt_music, tt_music)
    unified_trends = _build_unified_trends(yt_result, tt_result)
    proactive_actions = _build_proactive_actions(
        yt_result, tt_result, unified_trends, master_hashtags, master_sounds
    )

    return CrossPlatformReport(
        generated_at=datetime.utcnow().isoformat() + "Z",
        niche=niche,
        region=region,
        youtube=yt_result.to_dict() if yt_result else None,
        tiktok=tt_result.to_dict() if tt_result else None,
        unified_trends=unified_trends,
        master_hashtags=master_hashtags,
        master_sounds=master_sounds,
        proactive_actions=proactive_actions,
    )
