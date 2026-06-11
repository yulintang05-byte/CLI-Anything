"""
Cross-platform hashtag analyzer.
Aggregates hashtags from YouTube + TikTok, scores them, and produces
ranked recommendations optimized for reach vs competition ratio.
"""
from __future__ import annotations
import re
import math
from dataclasses import dataclass, field, asdict
from typing import Literal

Platform = Literal["youtube", "tiktok", "both"]


@dataclass
class HashtagScore:
    hashtag:       str
    platform:      str
    frequency:     int   = 0
    total_reach:   int   = 0   # views/plays
    total_likes:   int   = 0
    competition:   str   = "unknown"   # low / medium / high
    trend_score:   float = 0.0
    recommended:   bool  = False
    category:      str   = "general"

    def to_dict(self) -> dict:
        return asdict(self)


# Niche categories for theme-page targeting
NICHE_HASHTAGS: dict[str, list[str]] = {
    "fitness": ["fitness", "workout", "gym", "gains", "fitcheck", "bodybuilding",
                "calisthenics", "crossfit", "running", "weightloss", "fitspo",
                "health", "nutrition", "protein", "cardio"],
    "fashion": ["fashion", "ootd", "style", "outfitcheck", "trending", "aesthetic",
                "streetwear", "luxury", "thrift", "vintage", "fashiontok",
                "shopping", "haul", "drip", "fits"],
    "food":    ["foodtok", "recipe", "cooking", "foodie", "mukbang", "eats",
                "homecooking", "chef", "yummy", "foodporn", "baking",
                "meal", "dinner", "snacks", "tasty"],
    "finance": ["finance", "investing", "stocks", "crypto", "money", "wealth",
                "financialtips", "sidehustle", "passive", "budget",
                "richlife", "millionaire", "trading", "forex"],
    "travel":  ["travel", "explore", "wanderlust", "adventure", "vacation",
                "traveltok", "roadtrip", "beach", "mountains", "backpacking",
                "travel2024", "travelvlog", "destination"],
    "gaming":  ["gaming", "gamer", "twitch", "streamclip", "gameplay",
                "fps", "rpg", "esports", "minecraft", "fortnite",
                "valorant", "cod", "lol", "gamedev"],
    "beauty":  ["beauty", "makeup", "skincare", "glam", "grwm", "tutorial",
                "glow", "skincareroutine", "makeupartist", "aesthetics",
                "lips", "eyeshadow", "foundation"],
    "motivation": ["motivation", "mindset", "success", "hustle", "grind",
                   "positivity", "selfimprovement", "goals", "inspire",
                   "levelup", "growth", "discipline"],
}

# Hashtag volume tiers (estimated monthly searches)
_VOLUME_TIERS = {
    "mega":   (10_000_000, float("inf"), "high",   0.2),   # >10M: high competition, low score boost
    "large":  (1_000_000,  10_000_000,  "high",   0.4),
    "medium": (100_000,    1_000_000,   "medium", 0.7),
    "small":  (10_000,     100_000,     "low",    1.0),    # sweet spot
    "micro":  (0,          10_000,      "low",    0.8),
}

# Known mega hashtags (competition = high, avoid as sole tag)
MEGA_TAGS = {
    "fyp", "foryou", "foryoupage", "viral", "trending", "tiktok",
    "youtube", "reels", "shorts", "explore", "fy", "fypシ",
}


def _competition_tier(reach: int, frequency: int) -> tuple[str, float]:
    """Estimate competition level and score multiplier."""
    if not reach:
        reach = frequency * 10_000  # rough estimate

    for tier, (lo, hi, comp, mult) in _VOLUME_TIERS.items():
        if lo <= reach < hi:
            return comp, mult
    return "medium", 0.7


def _trend_score(ht: str, frequency: int, reach: int, likes: int) -> float:
    """
    Score = log(reach + 1) * frequency_weight * competition_multiplier * niche_bonus
    Range roughly 0-100.
    """
    tag = ht.lstrip("#").lower()

    # Penalise generic mega-tags heavily
    if tag in MEGA_TAGS:
        return max(1.0, math.log(reach + 1) * 0.1)

    comp, mult = _competition_tier(reach, frequency)

    engagement_ratio = (likes / max(1, reach)) * 100  # %
    engagement_weight = 1.0 + min(2.0, engagement_ratio / 5.0)

    score = (math.log(reach + 1) * 0.4 +
             math.log(frequency + 1) * 10 +
             math.log(likes + 1) * 0.3) * mult * engagement_weight

    return round(min(score, 100.0), 2)


def score_hashtags(raw: list[dict], platform: str = "both") -> list[HashtagScore]:
    """
    Convert raw hashtag dicts (from scrapers) into ranked HashtagScore objects.

    Expected raw dict keys (any subset):
        hashtag, frequency, total_views / total_plays, total_likes
    """
    scored = []
    for item in raw:
        ht  = item.get("hashtag", "").lstrip("#").lower()
        if not ht:
            continue
        freq   = int(item.get("frequency", item.get("videos", 1)))
        reach  = int(item.get("total_views", item.get("total_plays", 0)))
        likes  = int(item.get("total_likes", 0))
        comp, _ = _competition_tier(reach, freq)
        ts = _trend_score(ht, freq, reach, likes)

        # Detect niche category
        category = "general"
        for niche, tags in NICHE_HASHTAGS.items():
            if ht in tags:
                category = niche
                break

        scored.append(HashtagScore(
            hashtag=f"#{ht}",
            platform=platform,
            frequency=freq,
            total_reach=reach,
            total_likes=likes,
            competition=comp,
            trend_score=ts,
            recommended=(ts >= 15.0 and ht not in MEGA_TAGS),
            category=category,
        ))

    return sorted(scored, key=lambda x: x.trend_score, reverse=True)


def build_hashtag_set(scored: list[HashtagScore], target_count: int = 30,
                      niche: str = None) -> list[str]:
    """
    Build an optimal hashtag set for a post.

    Strategy:
      - 5-7 broad/trending tags  (score >= 50, high reach)
      - 10-15 niche-specific tags (score >= 15)
      - 5-8 low-competition tags  (micro/small)
    Fill to target_count.
    """
    broad   = [h for h in scored if h.trend_score >= 50 and h.hashtag.lstrip("#") not in MEGA_TAGS]
    niched  = [h for h in scored if 15 <= h.trend_score < 50 and
               (niche is None or h.category == niche or h.category == "general")]
    micro   = [h for h in scored if h.competition == "low" and h.trend_score < 15]

    result = []
    for pool, limit in [(broad, 7), (niched, 15), (micro, 8)]:
        result += [h.hashtag for h in pool[:limit]]
        if len(result) >= target_count:
            break

    return list(dict.fromkeys(result))[:target_count]  # dedup, preserve order


def cross_platform_merge(yt_hashtags: list[dict],
                          tt_hashtags: list[dict]) -> list[HashtagScore]:
    """
    Merge YouTube and TikTok hashtag lists.
    Tags appearing on both platforms get a 1.5× score boost.
    """
    yt_scored = {h.hashtag: h for h in score_hashtags(yt_hashtags, "youtube")}
    tt_scored = {h.hashtag: h for h in score_hashtags(tt_hashtags, "tiktok")}

    all_tags = set(yt_scored) | set(tt_scored)
    merged = []
    for tag in all_tags:
        yt = yt_scored.get(tag)
        tt = tt_scored.get(tag)
        if yt and tt:
            combined = HashtagScore(
                hashtag=tag,
                platform="both",
                frequency=yt.frequency + tt.frequency,
                total_reach=yt.total_reach + tt.total_reach,
                total_likes=yt.total_likes + tt.total_likes,
                competition=yt.competition if yt.trend_score >= tt.trend_score else tt.competition,
                trend_score=round((yt.trend_score + tt.trend_score) * 1.5 / 2, 2),
                category=yt.category if yt.category != "general" else tt.category,
            )
            combined.recommended = combined.trend_score >= 15 and tag.lstrip("#") not in MEGA_TAGS
            merged.append(combined)
        elif yt:
            merged.append(yt)
        else:
            merged.append(tt)

    return sorted(merged, key=lambda x: x.trend_score, reverse=True)


def recommend_for_niche(niche: str, platform: Platform = "both") -> list[str]:
    """Return pre-curated hashtag recommendations for a given niche."""
    base = NICHE_HASHTAGS.get(niche.lower(), [])
    # Add platform-specific variants
    if platform in ("tiktok", "both"):
        base = base + [f"{t}tok" for t in base[:5] if f"{t}tok" not in base]
    if platform in ("youtube", "both"):
        base = base + [f"{t}youtube" for t in base[:3] if f"{t}youtube" not in base]
    return [f"#{t}" for t in list(dict.fromkeys(base))[:30]]


def analyze_description(text: str) -> dict:
    """Extract and score existing hashtags from a caption/description."""
    found = re.findall(r"#(\w+)", text)
    raw = [{"hashtag": t, "frequency": 1} for t in found]
    scored = score_hashtags(raw)
    return {
        "found":       [h.hashtag for h in scored],
        "count":       len(scored),
        "avg_score":   round(sum(h.trend_score for h in scored) / max(1, len(scored)), 2),
        "weak_tags":   [h.hashtag for h in scored if h.trend_score < 10],
        "strong_tags": [h.hashtag for h in scored if h.trend_score >= 30],
        "mega_tags":   [h.hashtag for h in scored if h.hashtag.lstrip("#") in MEGA_TAGS],
        "suggestions": "Add more niche-specific low-competition tags for better reach." if len(scored) < 10 else "",
    }
