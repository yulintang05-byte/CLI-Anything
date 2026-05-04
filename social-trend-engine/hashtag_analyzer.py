"""
Hashtag analysis and optimization engine.
Scores hashtags by reach potential, competition tier, and niche relevance.
Builds optimal hashtag sets for YouTube and TikTok posts.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False


# ─── Tier classification by approximate audience size ────────────────────────

TIER_THRESHOLDS = {
    "mega":    1_000_000,   # 1M+ posts → very high competition, low discovery
    "large":     500_000,   # 500K–1M
    "medium":    100_000,   # 100K–500K → sweet spot
    "small":      10_000,   # 10K–100K  → niche authority
    "micro":           0,   # <10K      → emerging/new
}

# Known high-performing hashtag clusters by niche
NICHE_CLUSTERS: dict[str, list[str]] = {
    "lifestyle":  ["lifestyle", "dailylife", "dayinmylife", "routine", "aesthetic",
                   "vlog", "contentcreator", "influencer", "motivational"],
    "fitness":    ["fitness", "gym", "workout", "fitnessmotivation", "gains",
                   "fityoutuber", "bodybuilding", "health", "weightloss", "calisthenics"],
    "food":       ["food", "foodie", "recipe", "cooking", "easyrecipes", "mukbang",
                   "asmr", "foodtiktok", "homecooking", "mealprep"],
    "fashion":    ["fashion", "ootd", "style", "outfitoftheday", "streetwear",
                   "fashiontiktok", "thrift", "haul", "aesthetic"],
    "gaming":     ["gaming", "gamer", "twitch", "fps", "minecraft", "valorant",
                   "callofduty", "gameplay", "esports", "streamer"],
    "beauty":     ["beauty", "makeup", "skincare", "glowup", "tutorial",
                   "makeuptutorial", "drugstorebeauty", "grwm", "selfcare"],
    "finance":    ["finance", "investing", "stockmarket", "crypto", "passiveincome",
                   "sidehustle", "money", "financetok", "wealth", "budgeting"],
    "travel":     ["travel", "traveltok", "wanderlust", "adventure", "explore",
                   "vacation", "traveltheworld", "digitalnomad", "backpacking"],
    "comedy":     ["funny", "comedy", "memes", "humor", "relatable",
                   "trending", "viral", "foryou", "fyp"],
    "education":  ["learnontiktok", "educational", "didyouknow", "facts",
                   "science", "history", "psychology", "lifehacks", "tips"],
    "music":      ["music", "newmusic", "indieartist", "producer", "songwriter",
                   "musicvideo", "hiphop", "rnb", "pop", "edm"],
    "tech":       ["tech", "technology", "coding", "programming", "ai",
                   "software", "startup", "gadgets", "innovation"],
}

# Evergreen viral boosters (always safe to include a few)
VIRAL_BOOSTERS = ["fyp", "foryoupage", "foryou", "viral", "trending", "explore"]


@dataclass
class HashtagScore:
    tag: str
    tier: str
    trend_score: float          # 0–100 from Google Trends (if available)
    engagement_potential: float # composite 0–1
    recommended: bool
    reason: str


@dataclass
class HashtagSet:
    platform: str
    niche: str
    primary: list[str]     # high-reach (tier: large/mega)
    secondary: list[str]   # mid-reach (tier: medium)
    niche_tags: list[str]  # niche authority (tier: small/micro)
    boosters: list[str]    # viral boosters
    full_set: list[str] = field(default_factory=list)

    def __post_init__(self):
        seen = set()
        combined = self.primary + self.secondary + self.niche_tags + self.boosters
        self.full_set = [t for t in combined if not (t in seen or seen.add(t))]

    def as_caption_string(self) -> str:
        return " ".join(f"#{t}" for t in self.full_set)

    def summary(self) -> str:
        lines = [
            f"Platform : {self.platform.upper()}",
            f"Niche    : {self.niche}",
            f"Primary  : {' '.join('#'+t for t in self.primary)}",
            f"Secondary: {' '.join('#'+t for t in self.secondary)}",
            f"Niche    : {' '.join('#'+t for t in self.niche_tags)}",
            f"Boosters : {' '.join('#'+t for t in self.boosters)}",
            f"Total    : {len(self.full_set)} tags",
            "",
            "Caption-ready:",
            self.as_caption_string(),
        ]
        return "\n".join(lines)


def classify_tier(tag: str, approx_post_count: int = 0) -> str:
    for tier, threshold in TIER_THRESHOLDS.items():
        if approx_post_count >= threshold:
            return tier
    return "micro"


def get_google_trends(keywords: list[str], timeframe: str = "now 7-d") -> dict[str, float]:
    """
    Return interest scores (0-100) for keywords via Google Trends.
    Returns empty dict on failure.
    """
    if not PYTRENDS_AVAILABLE or not keywords:
        return {}

    scores: dict[str, float] = {}
    # Pytrends allows max 5 keywords per request
    for i in range(0, len(keywords), 5):
        batch = keywords[i:i+5]
        try:
            pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25), retries=2, backoff_factor=0.5)
            pt.build_payload(batch, timeframe=timeframe, geo="")
            df = pt.interest_over_time()
            if df is not None and not df.empty:
                for kw in batch:
                    if kw in df.columns:
                        scores[kw] = float(df[kw].mean())
        except Exception:
            pass
    return scores


def analyze_scraped_hashtags(
    hashtag_counts: list[tuple[str, int]],
    niche: str = "lifestyle",
) -> list[HashtagScore]:
    """
    Score a list of (hashtag, frequency) tuples from scraped data.
    """
    results = []
    for tag, count in hashtag_counts:
        tier = classify_tier(tag, count * 10_000)  # rough estimate
        engagement = min(count / max(1, max(c for _, c in hashtag_counts)), 1.0)
        recommended = tier in ("medium", "small", "micro") or tag in VIRAL_BOOSTERS
        reason = (
            "Sweet-spot reach" if tier == "medium"
            else "Niche authority" if tier in ("small", "micro")
            else "Viral booster" if tag in VIRAL_BOOSTERS
            else "High competition — pair with niche tags"
        )
        results.append(HashtagScore(
            tag=tag,
            tier=tier,
            trend_score=0.0,  # populated below if pytrends available
            engagement_potential=round(engagement, 3),
            recommended=recommended,
            reason=reason,
        ))

    # Enrich with Google Trends scores
    tags = [s.tag for s in results]
    trend_scores = get_google_trends(tags[:20])
    for score in results:
        score.trend_score = round(trend_scores.get(score.tag, 0.0), 1)

    results.sort(key=lambda s: (s.engagement_potential + s.trend_score / 100), reverse=True)
    return results


def build_optimal_hashtag_set(
    platform: str,
    niche: str,
    scraped_tags: Optional[list[tuple[str, int]]] = None,
    custom_tags: Optional[list[str]] = None,
) -> HashtagSet:
    """
    Build a platform-optimized hashtag set for a post.

    YouTube best practices: 3–5 highly relevant tags in description + title tag
    TikTok best practices: 5–8 tags, mix of mega/medium/niche + fyp boosters
    """
    niche_key = niche.lower()
    base_cluster = NICHE_CLUSTERS.get(niche_key, NICHE_CLUSTERS["lifestyle"])

    # Extract top scraped tags
    scraped_top = [t for t, _ in (scraped_tags or [])[:20]]

    # Merge and deduplicate
    all_candidates = list(dict.fromkeys(scraped_top + base_cluster + (custom_tags or [])))

    if platform == "youtube":
        # YouTube: fewer, highly specific tags — 5 max in title/description
        primary = all_candidates[:2]
        secondary = all_candidates[2:4]
        niche_tags = all_candidates[4:6]
        boosters = []  # YouTube doesn't use fyp-style boosters
    else:
        # TikTok: balanced mix, 6–10 total
        primary = all_candidates[:2]
        secondary = all_candidates[2:5]
        niche_tags = all_candidates[5:8]
        boosters = VIRAL_BOOSTERS[:3]

    return HashtagSet(
        platform=platform,
        niche=niche,
        primary=primary,
        secondary=secondary,
        niche_tags=niche_tags,
        boosters=boosters,
    )


def get_niche_hashtag_strategy(niche: str) -> str:
    """Return a text strategy guide for a specific niche."""
    cluster = NICHE_CLUSTERS.get(niche.lower())
    if not cluster:
        available = ", ".join(NICHE_CLUSTERS.keys())
        return f"Unknown niche. Available niches: {available}"

    lines = [
        f"HASHTAG STRATEGY FOR: #{niche.upper()}",
        "=" * 50,
        "",
        "CORE TAGS (always include 2-3):",
        "  " + "  ".join(f"#{t}" for t in cluster[:4]),
        "",
        "SUPPORTING TAGS (rotate these):",
        "  " + "  ".join(f"#{t}" for t in cluster[4:]),
        "",
        "TIKTOK FORMULA (8-10 tags):",
        "  1x mega tag  (1M+ views) — brand awareness",
        "  3x medium tags (100K-500K) — discovery sweet spot",
        "  2x niche tags (<100K)     — authority & community",
        "  2x viral boosters         — #fyp #foryoupage",
        "",
        "YOUTUBE FORMULA (3-5 tags):",
        "  Focus on 1 primary keyword + 2-3 long-tail variations",
        "  Put most important tag in video title",
        "  Add 3-5 in description first line",
        "",
        "POSTING TIME OPTIMIZATION:",
        "  TikTok: 6-9 AM, 12-3 PM, 7-9 PM (local time of audience)",
        "  YouTube: Tue-Thu, 12-4 PM EST for max algorithm push",
        "",
        "PRO TIP: Never use 30 random hashtags. 5-8 targeted tags",
        "outperform spam every time on both platforms.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    hs = build_optimal_hashtag_set("tiktok", "fitness")
    print(hs.summary())
    print()
    print(get_niche_hashtag_strategy("fitness"))
