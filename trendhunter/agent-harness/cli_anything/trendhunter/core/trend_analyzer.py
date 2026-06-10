"""Cross-platform trend analyzer — scores, ranks, and surfaces viral opportunities."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from cli_anything.trendhunter.core.youtube_scraper import YouTubeTrends
from cli_anything.trendhunter.core.tiktok_scraper import TikTokTrends, TikTokHashtag


# Category keyword maps for niche detection
_NICHE_KEYWORDS: dict[str, list[str]] = {
    "fitness":     ["gym", "workout", "fitness", "health", "exercise", "gains", "lifting", "cardio", "diet"],
    "beauty":      ["makeup", "skincare", "beauty", "glam", "glow", "tutorial", "nails", "hair"],
    "fashion":     ["outfit", "ootd", "style", "fashion", "clothes", "drip", "streetwear", "thrift"],
    "food":        ["recipe", "food", "cooking", "baking", "eat", "foodie", "chef", "meal"],
    "finance":     ["money", "investing", "stocks", "crypto", "finance", "wealth", "budget", "passive"],
    "gaming":      ["gaming", "gamer", "game", "fps", "twitch", "stream", "esports", "minecraft"],
    "travel":      ["travel", "vlog", "adventure", "explore", "trip", "vacation", "abroad", "backpack"],
    "motivation":  ["motivation", "mindset", "grind", "hustle", "success", "inspire", "growth"],
    "comedy":      ["funny", "comedy", "humor", "prank", "meme", "lol", "roast", "sketch"],
    "education":   ["learn", "tips", "howto", "tutorial", "didyouknow", "facts", "science", "history"],
    "pets":        ["dog", "cat", "pet", "puppy", "kitten", "animals", "wildlife"],
    "tech":        ["tech", "ai", "coding", "developer", "software", "gadget", "review", "startup"],
    "music":       ["music", "song", "artist", "rap", "rnb", "pop", "singer", "producer", "beat"],
    "lifestyle":   ["lifestyle", "dayinmylife", "morning", "routine", "aesthetic", "vibe", "minimalism"],
    "business":    ["business", "entrepreneur", "marketing", "brand", "ecommerce", "shopify", "dropship"],
}


@dataclass
class ScoredTrend:
    tag: str
    score: float
    platforms: list[str] = field(default_factory=list)
    niches: list[str] = field(default_factory=list)
    yt_count: int = 0
    tt_count: int = 0
    view_estimate: int = 0
    recommendation: str = ""

    def to_dict(self) -> dict:
        return {
            "tag":            self.tag,
            "score":          round(self.score, 2),
            "platforms":      self.platforms,
            "niches":         self.niches,
            "yt_count":       self.yt_count,
            "tt_count":       self.tt_count,
            "view_estimate":  self.view_estimate,
            "recommendation": self.recommendation,
        }


@dataclass
class TrendReport:
    top_trends: list[ScoredTrend] = field(default_factory=list)
    cross_platform: list[ScoredTrend] = field(default_factory=list)
    yt_only: list[ScoredTrend] = field(default_factory=list)
    tt_only: list[ScoredTrend] = field(default_factory=list)
    trending_music: list[dict] = field(default_factory=list)
    niche_opportunities: dict[str, list[str]] = field(default_factory=dict)
    viral_hooks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "top_trends":          [t.to_dict() for t in self.top_trends],
            "cross_platform":      [t.to_dict() for t in self.cross_platform],
            "yt_only":             [t.to_dict() for t in self.yt_only],
            "tt_only":             [t.to_dict() for t in self.tt_only],
            "trending_music":      self.trending_music,
            "niche_opportunities": self.niche_opportunities,
            "viral_hooks":         self.viral_hooks,
        }


def _detect_niches(tag: str) -> list[str]:
    """Detect which content niches a hashtag belongs to."""
    tag_lower = tag.lower()
    return [
        niche for niche, keywords in _NICHE_KEYWORDS.items()
        if any(kw in tag_lower for kw in keywords)
    ]


def _score_hashtag(tag: str, yt_count: int = 0, tt_count: int = 0,
                   tt_view_count: int = 0) -> float:
    """Score a trend 0-100 based on multi-platform presence and engagement."""
    score = 0.0

    # Cross-platform bonus (big signal)
    if yt_count > 0 and tt_count > 0:
        score += 40.0
    elif yt_count > 0:
        score += 20.0
    elif tt_count > 0:
        score += 20.0

    # TikTok view count (logarithmic scale)
    if tt_view_count > 0:
        import math
        score += min(30.0, math.log10(max(tt_view_count, 1)) * 3)

    # YouTube frequency bonus
    if yt_count >= 3:
        score += 15.0
    elif yt_count >= 1:
        score += 8.0

    # TikTok frequency bonus
    if tt_count >= 5:
        score += 15.0
    elif tt_count >= 2:
        score += 8.0

    # Length heuristic: mid-length tags are more niche and less saturated
    tag_len = len(tag)
    if 5 <= tag_len <= 15:
        score += 5.0

    return min(score, 100.0)


def analyze_trends(yt: YouTubeTrends, tt: TikTokTrends,
                   top_n: int = 30) -> TrendReport:
    """Merge YouTube and TikTok data into a scored, ranked trend report."""
    report = TrendReport()

    # Build tag frequency maps
    yt_tag_counts: dict[str, int] = {}
    for tag in yt.trending_hashtags:
        yt_tag_counts[tag.lower()] = yt_tag_counts.get(tag.lower(), 0) + 1

    tt_tag_map: dict[str, TikTokHashtag] = {
        h.name.lower(): h for h in tt.hashtags
    }
    tt_tag_counts: dict[str, int] = {
        tag: 1 for tag in tt_tag_map
    }

    # Union of all tags
    all_tags = set(yt_tag_counts.keys()) | set(tt_tag_counts.keys())

    scored: list[ScoredTrend] = []
    for tag in all_tags:
        if len(tag) < 2:
            continue
        yt_c  = yt_tag_counts.get(tag, 0)
        tt_c  = tt_tag_counts.get(tag, 0)
        tt_ht = tt_tag_map.get(tag)
        tt_views = tt_ht.view_count if tt_ht else 0

        score = _score_hashtag(tag, yt_c, tt_c, tt_views)
        platforms = (["youtube"] if yt_c > 0 else []) + (["tiktok"] if tt_c > 0 else [])
        niches = _detect_niches(tag)

        rec = ""
        if yt_c > 0 and tt_c > 0:
            rec = f"Cross-platform hit — use on both YouTube and TikTok now"
        elif tt_views > 1_000_000_000:
            rec = f"Mega-volume TikTok tag ({tt_views/1e9:.1f}B views) — high competition"
        elif tt_views > 100_000_000:
            rec = f"High-volume TikTok tag — good reach, moderate competition"
        elif yt_c > 0:
            rec = f"YouTube trending — add to video title/description"

        scored.append(ScoredTrend(
            tag=tag, score=score, platforms=platforms, niches=niches,
            yt_count=yt_c, tt_count=tt_c, view_estimate=tt_views,
            recommendation=rec,
        ))

    scored.sort(key=lambda x: x.score, reverse=True)
    report.top_trends     = scored[:top_n]
    report.cross_platform = [s for s in scored if len(s.platforms) == 2][:15]
    report.yt_only        = [s for s in scored if s.platforms == ["youtube"]][:10]
    report.tt_only        = [s for s in scored if s.platforms == ["tiktok"]][:15]

    # Merge music trends
    music: list[dict] = list(yt.trending_music)
    for sound in tt.sounds:
        music.append({"title": sound.name, "artist": sound.artist, "source": "tiktok"})
    report.trending_music = music[:20]

    # Niche opportunities: group top tags by niche
    for trend in report.top_trends:
        for niche in trend.niches:
            report.niche_opportunities.setdefault(niche, []).append(f"#{trend.tag}")

    # Viral hooks
    report.viral_hooks = _generate_viral_hooks(report.top_trends[:10])

    return report


def _generate_viral_hooks(trends: list[ScoredTrend]) -> list[str]:
    """Generate viral hook templates based on top trends."""
    hooks = []
    for t in trends[:5]:
        niche = t.niches[0] if t.niches else "content"
        hooks.extend([
            f"POV: You just discovered #{t.tag} and it changed everything",
            f"Things nobody tells you about #{t.tag} 👀",
            f"Watch until the end — #{t.tag} tutorial that actually works",
            f"The #{t.tag} secret accounts don't want you to know",
        ])
    return hooks[:20]


def get_recommended_hashtags(niche: str, all_trends: TrendReport,
                              mix: bool = True, count: int = 15) -> list[str]:
    """Return a recommended hashtag set for a niche.

    mix=True applies the 30/30/30/10 strategy:
      30% mega (>1B views) — reach
      30% mid  (100M-1B)   — balance
      30% niche (<100M)    — targeted
      10% branded/unique   — discoverability
    """
    niche_lower = niche.lower()

    niche_tags  = [t.tag for t in all_trends.top_trends
                   if niche_lower in t.niches]
    mega_tags   = [t.tag for t in all_trends.tt_only
                   if t.view_estimate > 1_000_000_000][:5]
    mid_tags    = [t.tag for t in all_trends.tt_only
                   if 100_000_000 < t.view_estimate <= 1_000_000_000][:5]

    if not mix:
        combined = (niche_tags + mid_tags + mega_tags)
        return list(dict.fromkeys(f"#{t}" for t in combined))[:count]

    # 30/30/30/10
    n_mega   = max(1, int(count * 0.3))
    n_mid    = max(1, int(count * 0.3))
    n_niche  = max(1, int(count * 0.3))
    n_extra  = count - n_mega - n_mid - n_niche

    result = (
        [f"#{t}" for t in mega_tags[:n_mega]] +
        [f"#{t}" for t in mid_tags[:n_mid]] +
        [f"#{t}" for t in niche_tags[:n_niche]] +
        [f"#{niche}", f"#{niche}community", "#creator"][:n_extra]
    )
    return list(dict.fromkeys(result))[:count]
