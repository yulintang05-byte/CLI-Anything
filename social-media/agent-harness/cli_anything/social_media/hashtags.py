"""Hashtag research, scoring, and set builder for TikTok & Instagram."""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass, field, asdict
from typing import Optional

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class HashtagInfo:
    tag: str
    platform: str
    post_count: Optional[int] = None
    view_count: Optional[int] = None
    difficulty: Optional[str] = None   # low / medium / high / viral
    trend_direction: Optional[str] = None  # rising / stable / declining
    related: list[str] = field(default_factory=list)
    top_niches: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class HashtagSet:
    niche: str
    platform: str
    strategy: str          # "broad" | "niche" | "micro" | "balanced"
    tags: list[str] = field(default_factory=list)
    estimated_reach: str = ""
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# TikTok hashtag research via Creative Center
# ---------------------------------------------------------------------------

TIKTOK_HASHTAG_API = (
    "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list"
)
TIKTOK_KEYWORD_API = (
    "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/detail"
)


def _cc_headers() -> dict:
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://ads.tiktok.com",
        "Referer": "https://ads.tiktok.com/",
    }


def _cc_get(url: str) -> dict:
    req = urllib.request.Request(url, headers=_cc_headers())
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"TikTok Creative Center error {e.code}: {e.read().decode()}") from e


def fetch_tiktok_trending_hashtags(
    region: str = "US",
    period: int = 7,
    limit: int = 30,
) -> list[HashtagInfo]:
    """Fetch top trending hashtags from TikTok Creative Center (public endpoint)."""
    url = (
        f"{TIKTOK_HASHTAG_API}"
        f"?period={period}&region_code={region.upper()}"
        f"&page=1&limit={min(limit, 50)}&country_code=US&language=en"
    )
    try:
        data = _cc_get(url)
    except Exception as e:
        raise RuntimeError(f"Could not fetch TikTok trending hashtags: {e}") from e

    items = (
        data.get("data", {}).get("list", [])
        or data.get("data", {}).get("hashtag_list", [])
        or []
    )
    result: list[HashtagInfo] = []
    for item in items[:limit]:
        name = item.get("hashtag_name") or item.get("name", "")
        views = item.get("video_views") or item.get("view_cnt", 0)
        posts = item.get("publish_cnt") or item.get("item_count", 0)
        result.append(HashtagInfo(
            tag=f"#{name}",
            platform="tiktok",
            post_count=posts,
            view_count=views,
            difficulty=_score_difficulty(posts),
            trend_direction="rising",
        ))
    return result


# ---------------------------------------------------------------------------
# Niche hashtag sets — curated + auto-generated strategies
# ---------------------------------------------------------------------------

# Curated seed sets by niche — agents can extend via fetch functions
NICHE_SEEDS: dict[str, list[str]] = {
    "fitness": [
        "#fitness", "#gym", "#workout", "#fitcheck", "#gymtok",
        "#weightloss", "#gains", "#bodybuilding", "#cardio", "#healthylifestyle",
        "#personaltrainer", "#fitnessmotivation", "#calisthenics", "#homeworkout",
        "#fitfam",
    ],
    "fashion": [
        "#fashion", "#ootd", "#style", "#fashiontok", "#outfitcheck",
        "#aesthetic", "#streetwear", "#thrift", "#grwm", "#fashionista",
        "#lookbook", "#vintagefashion", "#styletips", "#outfitinspo", "#wiwt",
    ],
    "food": [
        "#food", "#foodtok", "#recipe", "#cooking", "#foodie",
        "#homecooking", "#mealprep", "#easyrecipes", "#foodreview", "#asmrfood",
        "#mukbang", "#whatieatinaday", "#healthyfood", "#veganfood", "#dessert",
    ],
    "beauty": [
        "#beauty", "#makeup", "#skincare", "#grwm", "#makeuptutorial",
        "#skintok", "#glam", "#naturalmakeup", "#glow", "#makeuptok",
        "#skincareroutine", "#beautytips", "#glowup", "#selfcare", "#beautyhacks",
    ],
    "finance": [
        "#finance", "#money", "#investing", "#stockmarket", "#financetok",
        "#sidehustle", "#passiveincome", "#entrepreneur", "#wealth", "#crypto",
        "#personalfinance", "#budgeting", "#financialfreedom", "#moneytips", "#hustle",
    ],
    "gaming": [
        "#gaming", "#gamer", "#gamertok", "#videogames", "#fortniteclips",
        "#minecraft", "#fps", "#mobileegaming", "#pcgaming", "#streamer",
        "#twitch", "#youtube", "#gamingcommunity", "#esports", "#nba2k",
    ],
    "travel": [
        "#travel", "#traveltok", "#wanderlust", "#explore", "#adventure",
        "#vacation", "#travellife", "#traveldiaries", "#backpacking", "#roadtrip",
        "#travelgram", "#travelblogger", "#luxurytravel", "#budgettravel", "#solotravel",
    ],
    "motivation": [
        "#motivation", "#mindset", "#success", "#hustle", "#grind",
        "#selfimprovement", "#personaldevelopment", "#discipline", "#goals", "#inspire",
        "#entrepreneur", "#positivity", "#accountability", "#growth", "#mentalhealth",
    ],
    "pets": [
        "#pets", "#dogsoftiktok", "#catsoftiktok", "#petlover", "#cute",
        "#funnypets", "#animals", "#dog", "#cat", "#puppy",
        "#kitten", "#doglover", "#catlover", "#dogmom", "#petcare",
    ],
    "comedy": [
        "#comedy", "#funny", "#humor", "#memes", "#relatable",
        "#skit", "#comédytok", "#foryoupage", "#viral", "#trending",
        "#funnymemes", "#jokes", "#lol", "#fyp", "#comedytok",
    ],
}

ALWAYS_INCLUDE = ["#fyp", "#foryou", "#foryoupage", "#viral", "#trending"]


def build_hashtag_set(
    niche: str,
    platform: str = "tiktok",
    strategy: str = "balanced",
    max_tags: int = 30,
) -> HashtagSet:
    """
    Build an optimized hashtag set for a given niche.

    Strategies:
      broad    — high-volume general tags for max reach (harder to rank)
      niche    — mid-size niche-specific tags (targeted audience)
      micro    — small, hyper-specific tags (easiest to rank)
      balanced — mix of all three (recommended for growth)
    """
    niche_key = niche.lower().replace(" ", "")
    seed_tags = list(NICHE_SEEDS.get(niche_key, []))

    if not seed_tags:
        # Fallback: generate generic tags from the niche word
        seed_tags = [
            f"#{niche_key}",
            f"#{niche_key}tok",
            f"#{niche_key}life",
            f"#{niche_key}tips",
            f"#{niche_key}daily",
            f"#{niche_key}community",
            f"#{niche_key}content",
            f"#{niche_key}lover",
        ]

    if strategy == "broad":
        selected = ALWAYS_INCLUDE[:5] + seed_tags[:max_tags - 5]
        notes = "High-reach tags — competitive but maximizes discovery surface."
        reach = "1M–100M+ per tag"
    elif strategy == "niche":
        selected = seed_tags[5:] + [f"#{niche_key}creator", f"#{niche_key}vibes"]
        selected = selected[:max_tags]
        notes = "Mid-tier niche tags — easier to rank, more targeted audience."
        reach = "10K–1M per tag"
    elif strategy == "micro":
        selected = [
            f"#{niche_key}tips",
            f"#{niche_key}hacks",
            f"#{niche_key}beginner",
            f"#{niche_key}advice",
            f"small{niche_key}creator",
            f"new{niche_key}content",
        ]
        selected = ["#" + t.lstrip("#") for t in selected][:max_tags]
        notes = "Micro tags — small community but very easy to rank #1."
        reach = "1K–50K per tag"
    else:  # balanced
        broad = ALWAYS_INCLUDE[:3]
        mid = seed_tags[:8]
        micro = [f"#{niche_key}creator", f"#{niche_key}community", f"small{niche_key}"]
        selected = (broad + mid + micro)[:max_tags]
        notes = (
            "Balanced mix: 3 broad viral tags + 8 niche-specific + 3 micro. "
            "Best strategy for new and growing accounts."
        )
        reach = "Mixed: 10K–100M+"

    return HashtagSet(
        niche=niche,
        platform=platform,
        strategy=strategy,
        tags=list(dict.fromkeys(selected)),  # deduplicate, preserve order
        estimated_reach=reach,
        notes=notes,
    )


def research_hashtag(tag: str, platform: str = "tiktok") -> HashtagInfo:
    """
    Research a single hashtag — returns metadata including estimated difficulty.
    Uses TikTok Creative Center for TikTok; returns estimates for Instagram.
    """
    clean = tag.lstrip("#")
    if platform == "tiktok":
        return _research_tiktok_tag(clean)
    elif platform == "instagram":
        return _research_instagram_tag_estimate(clean)
    else:
        raise ValueError(f"Unsupported platform: {platform}. Use 'tiktok' or 'instagram'.")


def _research_tiktok_tag(name: str) -> HashtagInfo:
    url = (
        f"{TIKTOK_KEYWORD_API}"
        f"?period=7&hashtag_name={urllib.parse.quote(name)}&country_code=US&language=en"
    )
    try:
        data = _cc_get(url)
        detail = data.get("data", {}).get("detail", {}) or {}
        posts = detail.get("publish_cnt") or detail.get("item_count", 0)
        views = detail.get("video_views") or detail.get("view_cnt", 0)
        related_raw = detail.get("related_hashtag_list", []) or []
        related = [f"#{r.get('hashtag_name', '')}" for r in related_raw[:10]]
        trend = detail.get("trend") or "stable"
        return HashtagInfo(
            tag=f"#{name}",
            platform="tiktok",
            post_count=posts,
            view_count=views,
            difficulty=_score_difficulty(posts),
            trend_direction=trend,
            related=related,
        )
    except Exception as e:
        # Return basic info if API call fails
        return HashtagInfo(
            tag=f"#{name}",
            platform="tiktok",
            difficulty="unknown",
            trend_direction="unknown",
        )


def _research_instagram_tag_estimate(name: str) -> HashtagInfo:
    # Instagram doesn't expose a public hashtag API without auth.
    # Return a heuristic estimate based on tag length and popularity signals.
    difficulty = "medium"
    if len(name) <= 5:
        difficulty = "high"
    elif len(name) >= 15:
        difficulty = "low"

    return HashtagInfo(
        tag=f"#{name}",
        platform="instagram",
        difficulty=difficulty,
        trend_direction="unknown",
        top_niches=["general"],
    )


def analyze_competitor_hashtags(text: str) -> list[str]:
    """Extract all hashtags from a caption or bio text."""
    return re.findall(r"#\w+", text)


# ---------------------------------------------------------------------------
# Hashtag performance scoring
# ---------------------------------------------------------------------------

def _score_difficulty(post_count: Optional[int]) -> str:
    if post_count is None:
        return "unknown"
    if post_count >= 10_000_000:
        return "viral"      # Super competitive — avoid as primary
    if post_count >= 1_000_000:
        return "high"       # Hard to rank
    if post_count >= 100_000:
        return "medium"     # Sweet spot for growing accounts
    if post_count >= 10_000:
        return "low"        # Easy to rank
    return "micro"          # Very small — rank easily but low reach


def score_hashtag_set(tags: list[str]) -> dict:
    """
    Score a list of hashtags for diversity and strategy balance.
    Returns a breakdown without making any API calls.
    """
    viral = [t for t in tags if t.lower() in {h.lower() for h in ALWAYS_INCLUDE}]
    niche_tags = [t for t in tags if t not in viral]

    return {
        "total": len(tags),
        "viral_broad": len(viral),
        "niche_specific": len(niche_tags),
        "balance_score": _balance_score(len(viral), len(niche_tags), len(tags)),
        "recommendation": _balance_recommendation(len(viral), len(tags)),
        "tags": tags,
    }


def _balance_score(viral: int, niche: int, total: int) -> str:
    if total == 0:
        return "N/A"
    viral_pct = viral / total
    if 0.10 <= viral_pct <= 0.20:
        return "optimal"
    if viral_pct < 0.10:
        return "needs more broad tags"
    return "too many viral tags — harder to rank"


def _balance_recommendation(viral: int, total: int) -> str:
    if total == 0:
        return "Add hashtags first."
    pct = viral / total
    if pct < 0.10:
        return "Add 2-3 broad viral tags like #fyp or #viral."
    if pct > 0.25:
        return "Replace some viral tags with niche-specific ones for better ranking."
    return "Good balance! Your set looks strong."
