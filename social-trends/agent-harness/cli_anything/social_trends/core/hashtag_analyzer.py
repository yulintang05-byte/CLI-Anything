"""Hashtag analysis and suggestion engine.

Combines data from YouTube tags and TikTok hashtags to produce
ranked, niche-optimised hashtag sets ready to paste into captions.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Sequence


@dataclass
class HashtagScore:
    tag: str
    platform: str              # "youtube" | "tiktok" | "both"
    reach_score: float         # 0-100 estimated reach potential
    competition_score: float   # 0-100 (higher = more competitive)
    trend_velocity: float      # % growth over past 7 days (approx.)
    post_count: int
    view_count: int
    recommended: bool = False

    def to_dict(self) -> dict:
        return {
            "tag": self.tag,
            "platform": self.platform,
            "reach_score": self.reach_score,
            "competition_score": self.competition_score,
            "trend_velocity": self.trend_velocity,
            "post_count": self.post_count,
            "view_count": self.view_count,
            "recommended": self.recommended,
        }

    @property
    def opportunity_score(self) -> float:
        """Reach / competition ratio — higher is better."""
        denom = max(self.competition_score, 1)
        return round(self.reach_score / denom * 100, 1)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _normalize(value: float, lo: float, hi: float) -> float:
    """Min-max normalize value to 0-100."""
    if hi == lo:
        return 50.0
    return round(min(max((value - lo) / (hi - lo) * 100, 0), 100), 2)


def _log_scale(count: int) -> float:
    """Apply log10 so huge counts don't dwarf everything."""
    return math.log10(max(count, 1))


def _clean_tag(tag: str) -> str:
    tag = tag.strip().lstrip("#").lower()
    tag = re.sub(r"[^\w]", "", tag)
    return tag


# ── Public API ────────────────────────────────────────────────────────────────

def score_tiktok_hashtags(
    hashtags: list,  # list[TikTokHashtag]
) -> list[HashtagScore]:
    """Convert raw TikTokHashtag objects into scored HashtagScore objects."""
    if not hashtags:
        return []

    post_counts = [h.post_count for h in hashtags]
    view_counts = [h.view_count for h in hashtags]
    log_posts = [_log_scale(p) for p in post_counts]
    log_views = [_log_scale(v) for v in view_counts]

    min_lp, max_lp = min(log_posts), max(log_posts)
    min_lv, max_lv = min(log_views), max(log_views)

    scores: list[HashtagScore] = []
    for h in hashtags:
        lp = _log_scale(h.post_count)
        lv = _log_scale(h.view_count)

        # Reach correlates with views, competition with post count
        reach = _normalize(lv, min_lv, max_lv)
        competition = _normalize(lp, min_lp, max_lp)

        # trend_score from API (rank improvement) — normalise to %
        velocity = min(float(h.trend_score), 999.0)

        scores.append(
            HashtagScore(
                tag=f"#{_clean_tag(h.name)}",
                platform="tiktok",
                reach_score=reach,
                competition_score=competition,
                trend_velocity=velocity,
                post_count=h.post_count,
                view_count=h.view_count,
            )
        )

    # Mark top-opportunity hashtags as recommended
    sorted_by_opportunity = sorted(scores, key=lambda s: s.opportunity_score, reverse=True)
    for s in sorted_by_opportunity[:10]:
        s.recommended = True

    return scores


def score_youtube_tags(
    tag_counts: list[tuple[str, int]],
) -> list[HashtagScore]:
    """Score YouTube tags extracted from trending videos.

    tag_counts: output of youtube_trends.extract_top_tags()
    """
    if not tag_counts:
        return []

    counts = [c for _, c in tag_counts]
    log_counts = [_log_scale(c) for c in counts]
    min_lc, max_lc = min(log_counts), max(log_counts)

    scores: list[HashtagScore] = []
    for tag, count in tag_counts:
        lc = _log_scale(count)
        reach = _normalize(lc, min_lc, max_lc)
        # Competition estimated: high count = high competition on YouTube
        competition = reach * 0.9
        scores.append(
            HashtagScore(
                tag=f"#{_clean_tag(tag)}",
                platform="youtube",
                reach_score=reach,
                competition_score=competition,
                trend_velocity=0.0,
                post_count=count,
                view_count=0,
            )
        )

    sorted_by_reach = sorted(scores, key=lambda s: s.reach_score, reverse=True)
    for s in sorted_by_reach[:10]:
        s.recommended = True

    return scores


def merge_platform_scores(
    tiktok_scores: list[HashtagScore],
    youtube_scores: list[HashtagScore],
) -> list[HashtagScore]:
    """Merge TikTok and YouTube scores, boosting tags that appear on both."""
    index: dict[str, HashtagScore] = {}

    for s in tiktok_scores:
        index[s.tag] = s

    for s in youtube_scores:
        if s.tag in index:
            existing = index[s.tag]
            # Average reach, take max competition, mark as cross-platform
            merged = HashtagScore(
                tag=s.tag,
                platform="both",
                reach_score=round((existing.reach_score + s.reach_score) / 2 * 1.2, 2),
                competition_score=max(existing.competition_score, s.competition_score),
                trend_velocity=existing.trend_velocity,
                post_count=existing.post_count + s.post_count,
                view_count=existing.view_count,
                recommended=True,  # cross-platform = strong signal
            )
            index[s.tag] = merged
        else:
            index[s.tag] = s

    return sorted(index.values(), key=lambda s: s.opportunity_score, reverse=True)


def build_caption_set(
    scores: list[HashtagScore],
    platform: str = "tiktok",
    count: int = 30,
    mix: str = "balanced",
) -> list[str]:
    """Build an optimal hashtag set for a caption.

    Args:
        scores: Ranked HashtagScore list.
        platform: Target platform ("tiktok" or "youtube").
        count: Total hashtags to include (TikTok cap: 30, YouTube: 15).
        mix: Strategy — "balanced" | "viral" | "niche"
    """
    count = min(count, 30 if platform == "tiktok" else 15)

    if mix == "viral":
        # Prioritise raw reach
        pool = sorted(scores, key=lambda s: s.reach_score, reverse=True)
    elif mix == "niche":
        # Prioritise low competition (opportunity score)
        pool = sorted(scores, key=lambda s: s.opportunity_score, reverse=True)
    else:
        # Balanced: mix high-reach + high-opportunity
        pool = sorted(scores, key=lambda s: s.reach_score * 0.5 + s.opportunity_score * 0.5, reverse=True)

    seen: set[str] = set()
    result: list[str] = []
    for s in pool:
        if s.tag not in seen:
            seen.add(s.tag)
            result.append(s.tag)
        if len(result) >= count:
            break
    return result


def suggest_for_niche(niche: str, count: int = 20) -> list[str]:
    """Return curated starter hashtag suggestions for a given niche.

    These are evergreen, high-reach tags — override with live scraped data
    when available.
    """
    NICHE_TAGS: dict[str, list[str]] = {
        "fitness": [
            "#fitness", "#gym", "#workout", "#fityourself", "#fitnessmotivation",
            "#bodybuilding", "#gains", "#cardio", "#weightloss", "#healthylifestyle",
            "#gymlife", "#fitfam", "#personaltrainer", "#musclebuilding", "#homeworkout",
            "#calisthenics", "#crossfit", "#strengthtraining", "#gymmotivation", "#shredded",
        ],
        "travel": [
            "#travel", "#wanderlust", "#travelgram", "#adventure", "#explore",
            "#travelblogger", "#travellife", "#vacation", "#backpacking", "#travelphotography",
            "#travelvlog", "#worldtravel", "#solotravel", "#traveltheworld", "#luxurytravel",
            "#digitalnomad", "#bucketlist", "#travelcouple", "#travelcommunity", "#instatravel",
        ],
        "food": [
            "#food", "#foodie", "#cooking", "#recipe", "#homecooking",
            "#foodporn", "#delicious", "#yummy", "#easyrecipes", "#mealprep",
            "#foodlover", "#instafood", "#healthyfood", "#vegancooking", "#baking",
            "#dinnerideas", "#snacks", "#foodblogger", "#tasty", "#foodphotography",
        ],
        "beauty": [
            "#beauty", "#makeup", "#skincare", "#glowup", "#tutorial",
            "#makeuptutorial", "#skincareroutine", "#beautytips", "#selfcare", "#grwm",
            "#cosmetics", "#beautyblogger", "#motd", "#makeuplover", "#skintok",
            "#cleanbeauty", "#glam", "#eyeshadow", "#lipstick", "#nails",
        ],
        "fashion": [
            "#fashion", "#style", "#ootd", "#streetwear", "#outfitinspo",
            "#fashiontok", "#styleinspo", "#streetstyle", "#outfitoftheday", "#fashionista",
            "#aesthetics", "#cottagecore", "#y2k", "#thrifted", "#vintage",
            "#fashionblogger", "#lookbook", "#wiwt", "#closet", "#styletips",
        ],
        "gaming": [
            "#gaming", "#gamer", "#gameplay", "#streamer", "#gamingcommunity",
            "#ps5", "#xbox", "#pcgaming", "#mobilegaming", "#esports",
            "#gamertok", "#twitch", "#youtube", "#fortnite", "#minecraft",
            "#cod", "#videogames", "#gamingnews", "#gamereview", "#rpg",
        ],
        "finance": [
            "#finance", "#investing", "#money", "#crypto", "#stocks",
            "#financialtips", "#passiveincome", "#sidehustle", "#budgeting", "#savemoney",
            "#wealthbuilding", "#millionairemindset", "#financialfreedom", "#moneytok", "#investment",
            "#daytrading", "#realestate", "#entrepreneur", "#moneymindset", "#frugal",
        ],
        "lifestyle": [
            "#lifestyle", "#dailyvlog", "#dayinmylife", "#morningroutine", "#productivity",
            "#selfimprovement", "#mindset", "#motivation", "#grwm", "#vlog",
            "#aesthetic", "#minimalism", "#routines", "#habits", "#nightroutine",
            "#contentcreator", "#influencer", "#relatable", "#trendingtopic", "#viral",
        ],
    }

    niche = niche.lower().strip()
    tags = NICHE_TAGS.get(niche, [])

    if not tags:
        # Generic viral booster set if niche unknown
        tags = [
            "#fyp", "#viral", "#trending", "#foryoupage", "#fypシ",
            "#explore", "#reels", "#tiktok", "#youtube", "#content",
            "#creator", "#follow", "#like", "#share", "#subscribe",
            "#new", "#trending2024", "#viral2024", "#foryu", "#recommended",
        ]

    return tags[:count]
