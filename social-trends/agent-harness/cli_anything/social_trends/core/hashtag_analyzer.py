"""Hashtag analysis and strategy builder.

Combines signals from YouTube and TikTok to surface the best hashtags
to use for your niche, scored by trend velocity, reach, and competition.
"""

import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional


COMPETITION_TIERS = {
    "mega": (10_000_000, float("inf")),
    "high": (1_000_000, 10_000_000),
    "medium": (100_000, 1_000_000),
    "low": (10_000, 100_000),
    "niche": (0, 10_000),
}


@dataclass
class HashtagScore:
    tag: str
    platform: str
    mention_count: int
    est_reach: int
    competition: str
    trend_score: float
    recommended_use: str
    notes: str


class HashtagAnalyzer:
    def __init__(self):
        self._yt_tags: Counter = Counter()
        self._tt_tags: Counter = Counter()
        self._niche_seeds: dict[str, list[str]] = {}
        self._strategy_cache: dict[str, list[HashtagScore]] = {}

    # ── Feed data in ──────────────────────────────────────────────────

    def feed_youtube(self, hashtag_counts: list[tuple[str, int]]) -> None:
        """Ingest extracted YouTube hashtag counts."""
        for tag, cnt in hashtag_counts:
            tag = _clean_tag(tag)
            if tag:
                self._yt_tags[tag] += cnt

    def feed_tiktok(self, hashtag_counts: list[tuple[str, int]]) -> None:
        """Ingest extracted TikTok hashtag counts."""
        for tag, cnt in hashtag_counts:
            tag = _clean_tag(tag)
            if tag:
                self._tt_tags[tag] += cnt

    def set_niche_seeds(self, niche: str, seeds: list[str]) -> None:
        """Register seed hashtags for a niche to weight scoring."""
        self._niche_seeds[niche] = [_clean_tag(s) for s in seeds]

    # ── Analysis ──────────────────────────────────────────────────────

    def get_top_cross_platform(self, limit: int = 30) -> list[HashtagScore]:
        """Return hashtags trending on BOTH platforms — highest priority."""
        all_tags = set(self._yt_tags) | set(self._tt_tags)
        scores = []
        for tag in all_tags:
            yt_cnt = self._yt_tags.get(tag, 0)
            tt_cnt = self._tt_tags.get(tag, 0)
            if yt_cnt > 0 and tt_cnt > 0:
                # Cross-platform bonus: multiply combined score
                combined = (yt_cnt * 0.6) + (tt_cnt * 1.4)
                scores.append((tag, combined, yt_cnt, tt_cnt, "both"))
        scores.sort(key=lambda x: x[1], reverse=True)
        return [
            self._build_score(tag, cnt, yt, tt, platform="both")
            for tag, cnt, yt, tt, platform in scores[:limit]
        ]

    def get_top_by_platform(
        self, platform: str, limit: int = 30
    ) -> list[HashtagScore]:
        """Top hashtags for a single platform."""
        source = self._yt_tags if platform == "youtube" else self._tt_tags
        return [
            self._build_score(tag, cnt, cnt if platform == "youtube" else 0,
                              cnt if platform == "tiktok" else 0, platform)
            for tag, cnt in source.most_common(limit)
        ]

    def build_post_strategy(
        self, niche: str, platform: str = "both", max_tags: int = 30
    ) -> dict:
        """Build a complete hashtag posting strategy for a niche and platform.

        Returns a dict with 3 buckets:
          - pillar_tags: 3-5 broad reach tags (post every time)
          - niche_tags: 10-15 mid-competition tags (core strategy)
          - micro_tags: 5-10 low-competition tags (community building)
        """
        seeds = self._niche_seeds.get(niche, [niche])
        if platform == "both":
            candidates = self.get_top_cross_platform(100)
        else:
            candidates = self.get_top_by_platform(platform, 100)

        # Boost seed tags
        seed_boosted = []
        for hs in candidates:
            boost = 2.0 if hs.tag in seeds else 1.0
            seed_boosted.append((hs, hs.trend_score * boost))
        seed_boosted.sort(key=lambda x: x[1], reverse=True)

        pillar, niche_bucket, micro = [], [], []
        for hs, _ in seed_boosted:
            if hs.competition in ("mega", "high") and len(pillar) < 5:
                pillar.append(hs)
            elif hs.competition in ("medium",) and len(niche_bucket) < 15:
                niche_bucket.append(hs)
            elif hs.competition in ("low", "niche") and len(micro) < 10:
                micro.append(hs)
            if len(pillar) >= 5 and len(niche_bucket) >= 15 and len(micro) >= 10:
                break

        total = pillar + niche_bucket + micro
        tag_string = " ".join(f"#{hs.tag}" for hs in total[:max_tags])
        return {
            "niche": niche,
            "platform": platform,
            "pillar_tags": [_score_dict(s) for s in pillar],
            "niche_tags": [_score_dict(s) for s in niche_bucket],
            "micro_tags": [_score_dict(s) for s in micro],
            "ready_to_paste": tag_string,
            "total_tags": len(total),
            "generated_at": _now_iso(),
        }

    def compare_tags(self, tags: list[str]) -> list[HashtagScore]:
        """Compare a user-supplied list of tags against scraped data."""
        results = []
        for raw in tags:
            tag = _clean_tag(raw)
            yt = self._yt_tags.get(tag, 0)
            tt = self._tt_tags.get(tag, 0)
            results.append(self._build_score(tag, yt + tt, yt, tt, "both" if yt and tt else ("youtube" if yt else "tiktok")))
        return sorted(results, key=lambda x: x.trend_score, reverse=True)

    # ── Internal helpers ──────────────────────────────────────────────

    def _build_score(
        self, tag: str, combined: float, yt: int, tt: int, platform: str
    ) -> HashtagScore:
        est_reach = _estimate_reach(yt, tt)
        competition = _tier(est_reach)
        trend_score = _trend_score(yt, tt, combined)
        rec, notes = _recommend(competition, trend_score, platform)
        return HashtagScore(
            tag=tag,
            platform=platform,
            mention_count=yt + tt,
            est_reach=est_reach,
            competition=competition,
            trend_score=round(trend_score, 2),
            recommended_use=rec,
            notes=notes,
        )

    def to_json(self, strategy: dict) -> str:
        return json.dumps(strategy, indent=2, default=str)


# ── Pure functions ──────────────────────────────────────────────────────

def _clean_tag(tag: str) -> str:
    return re.sub(r"[^\w]", "", tag.lower().strip("#"))


def _estimate_reach(yt: int, tt: int) -> int:
    # Rough heuristic: each YT mention ~50k views, TT mention ~200k views
    return (yt * 50_000) + (tt * 200_000)


def _tier(reach: int) -> str:
    for name, (lo, hi) in COMPETITION_TIERS.items():
        if lo <= reach < hi:
            return name
    return "niche"


def _trend_score(yt: int, tt: int, combined: float) -> float:
    # Weighted: TikTok velocity matters more for trend detection
    return (yt * 0.5 + tt * 1.5) * (1 + (1 if yt > 0 and tt > 0 else 0))


def _recommend(competition: str, score: float, platform: str) -> tuple[str, str]:
    recs = {
        "mega": ("use sparingly", "High competition — pair with niche tags for discoverability"),
        "high": ("use 2-3 per post", "Strong reach, moderate competition"),
        "medium": ("core strategy", "Best ROI — enough reach with manageable competition"),
        "low": ("use freely", "Community builder — great for early growth"),
        "niche": ("targeted use", "Very small audience — use only if highly relevant"),
    }
    return recs.get(competition, ("use freely", ""))


def _score_dict(s: HashtagScore) -> dict:
    return asdict(s)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
