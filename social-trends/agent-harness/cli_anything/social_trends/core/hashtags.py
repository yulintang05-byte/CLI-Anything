"""Hashtag research, generation, and optimization.

Builds optimized hashtag sets for TikTok and YouTube Shorts using:
- TikTok Creative Center trending hashtags
- Niche-based hashtag strategies
- Mix-size strategy (mega + mid + micro + niche)
"""

from __future__ import annotations
import re
from typing import Literal

from cli_anything.social_trends.utils.scraper_backend import get, TIKTOK_CC_BASE


Platform = Literal["tiktok", "youtube", "instagram", "all"]

# Curated niche → seed hashtags mapping (expanded at runtime with live data)
NICHE_SEEDS: dict[str, list[str]] = {
    "fitness": ["fitness", "workout", "gym", "health", "bodybuilding", "weightloss", "fitspo"],
    "food": ["food", "foodie", "recipe", "cooking", "chef", "foodtok", "yummy", "delicious"],
    "fashion": ["fashion", "ootd", "style", "outfit", "streetwear", "aesthetic", "clothing"],
    "beauty": ["beauty", "makeup", "skincare", "glam", "beautytips", "cosmetics", "nails"],
    "travel": ["travel", "wanderlust", "explore", "adventure", "vacation", "traveltok"],
    "gaming": ["gaming", "gamer", "gameplay", "twitch", "esports", "videogames", "xbox"],
    "finance": ["finance", "money", "investing", "stocks", "crypto", "sidehustle", "passive"],
    "motivation": ["motivation", "mindset", "success", "hustle", "grind", "entrepreneur"],
    "pets": ["pets", "dog", "cat", "dogsoftiktok", "catsoftiktok", "animals", "puppy"],
    "comedy": ["comedy", "funny", "humor", "lol", "meme", "viral", "relatable"],
    "education": ["education", "learnontiktok", "didyouknow", "facts", "science", "history"],
    "music": ["music", "newmusic", "singer", "rapper", "producer", "musicvideo", "hiphop"],
    "dance": ["dance", "dancing", "choreography", "dancechallenge", "dancer"],
    "business": ["business", "entrepreneur", "startup", "marketing", "ecommerce", "dropshipping"],
    "relationship": ["relationship", "dating", "love", "couplegoals", "advice", "dating101"],
}

# TikTok optimal hashtag counts per post type
TIKTOK_HASHTAG_STRATEGY = {
    "mega": {"range": "1B+", "count": 1, "purpose": "Discoverability, massive audience"},
    "large": {"range": "100M–1B", "count": 2, "purpose": "Broad reach"},
    "medium": {"range": "10M–100M", "count": 3, "purpose": "Targeted reach"},
    "small": {"range": "1M–10M", "count": 2, "purpose": "Niche community"},
    "micro": {"range": "<1M", "count": 2, "purpose": "Hyper-niche, high engagement rate"},
}

MEGA_HASHTAGS = [
    "fyp", "foryou", "foryoupage", "viral", "trending",
    "fy", "fypシ", "explorepage", "viralvideo",
]


def research_hashtags(
    topic: str,
    platform: Platform = "tiktok",
    region: str = "US",
    limit: int = 30,
    bypass_cache: bool = False,
) -> dict:
    """Research hashtags for a topic by combining live trends + seeds.

    Args:
        topic: Niche or keyword (e.g. "fitness", "cooking").
        platform: Target platform.
        region: Country code.
        limit: Max hashtags to return.
        bypass_cache: Skip cache.

    Returns:
        Dict with ranked ``hashtags`` list.
    """
    topic_lower = topic.lower().strip()

    # Get live trending data
    live_hashtags = _fetch_live_hashtags(topic_lower, region, limit * 2, bypass_cache)

    # Merge with curated seeds
    seeds = []
    for niche, tags in NICHE_SEEDS.items():
        if topic_lower in niche or any(topic_lower in t for t in tags):
            seeds.extend(tags)
    seeds = list(dict.fromkeys(seeds))  # deduplicate preserving order

    # Combine live + seeds
    combined = live_hashtags
    live_names = {h["name"].lower() for h in live_hashtags}
    for seed in seeds:
        if seed.lower() not in live_names:
            combined.append({"hashtag": f"#{seed}", "name": seed, "source": "curated"})

    combined = combined[:limit]

    return {
        "topic": topic,
        "platform": platform,
        "region": region,
        "count": len(combined),
        "hashtags": combined,
        "tip": (
            "Use 3-5 hashtags for TikTok (quality > quantity). "
            "Mix mega/trending with niche-specific tags."
        ),
    }


def generate_hashtag_set(
    niche: str,
    platform: Platform = "tiktok",
    region: str = "US",
    post_count: int = 1,
    bypass_cache: bool = False,
) -> dict:
    """Generate an optimised hashtag set using the mix-size strategy.

    Follows the proven 1 mega + 2-3 mid + 2-3 niche formula.

    Args:
        niche: Content niche (e.g. "fitness", "food", "fashion").
        platform: Target platform.
        region: Country code.
        post_count: Number of unique post sets to generate.
        bypass_cache: Skip cache.

    Returns:
        Dict with ``sets`` (one per post), each containing categorised hashtags.
    """
    niche_lower = niche.lower().strip()
    seeds = NICHE_SEEDS.get(niche_lower, [niche_lower])
    live = _fetch_live_hashtags(niche_lower, region, 50, bypass_cache)
    live_names = [h["name"] for h in live]

    sets = []
    for i in range(post_count):
        offset = i * 3
        # Rotate through seeds so each post gets slightly different tags
        rotated_seeds = seeds[offset % len(seeds):] + seeds[:offset % len(seeds)]
        niche_tags = rotated_seeds[:3]
        trending_tags = live_names[offset:offset + 3] if live_names else []
        mega = [MEGA_HASHTAGS[i % len(MEGA_HASHTAGS)]]

        all_tags = list(dict.fromkeys(mega + trending_tags + niche_tags))
        sets.append({
            "post_number": i + 1,
            "mega_tags": [f"#{t}" for t in mega],
            "trending_tags": [f"#{t}" for t in trending_tags],
            "niche_tags": [f"#{t}" for t in niche_tags],
            "full_set": [f"#{t}" for t in all_tags],
            "copy_paste": " ".join(f"#{t}" for t in all_tags),
        })

    return {
        "niche": niche,
        "platform": platform,
        "region": region,
        "strategy": TIKTOK_HASHTAG_STRATEGY,
        "sets": sets,
    }


def analyze_hashtag(hashtag: str, region: str = "US", bypass_cache: bool = False) -> dict:
    """Get metrics for a specific hashtag from TikTok Creative Center.

    Args:
        hashtag: Hashtag name (with or without leading #).
        region: Country code.
        bypass_cache: Skip cache.

    Returns:
        Dict with hashtag metrics and usage recommendation.
    """
    clean = re.sub(r"^#+", "", hashtag).strip()

    # Fetch trending list and find this hashtag
    try:
        data = get(
            f"{TIKTOK_CC_BASE}/trending/hashtag/list",
            params={"limit": 50, "period": 7, "region": region.upper(), "page": 1, "sort_by": "popular"},
            bypass_cache=bypass_cache,
        )
        items = data.get("data", {}).get("list", [])
        match = next(
            (i for i in items if (i.get("hashtag_name") or "").lower() == clean.lower()),
            None,
        )
    except Exception as e:
        return {"hashtag": clean, "error": str(e)}

    if not match:
        return {
            "hashtag": f"#{clean}",
            "found_in_trending": False,
            "note": (
                f"#{clean} is not in the current top-50 trending hashtags for {region}. "
                "It may still be valuable as a niche tag."
            ),
            "recommendation": "Use as a micro/niche tag alongside 2-3 trending tags.",
        }

    video_count = match.get("video_count", 0)
    competition_level = (
        "ultra-high (avoid — too saturated)" if video_count > 1_000_000_000
        else "high" if video_count > 100_000_000
        else "medium" if video_count > 10_000_000
        else "low (great for niche reach)" if video_count > 1_000_000
        else "very low (hyper-niche)"
    )

    return {
        "hashtag": f"#{clean}",
        "found_in_trending": True,
        "rank": match.get("rank"),
        "video_count": video_count,
        "view_count": match.get("view_count"),
        "trend_score": match.get("trend_score"),
        "competition_level": competition_level,
        "recommendation": _hashtag_recommendation(video_count),
    }


def _hashtag_recommendation(video_count: int) -> str:
    if video_count > 1_000_000_000:
        return "Extremely saturated. Use sparingly as a discovery tag; pair with 3-4 niche tags."
    if video_count > 100_000_000:
        return "High competition. Good for broad reach; always pair with niche-specific tags."
    if video_count > 10_000_000:
        return "Solid mid-range tag. Use 2-3 of these per post for balanced reach + engagement."
    if video_count > 1_000_000:
        return "Great niche tag. Lower competition = higher chance of trending within niche."
    return "Micro-niche tag. Excellent engagement rate; combine with 1-2 larger tags."


def _fetch_live_hashtags(topic: str, region: str, limit: int, bypass_cache: bool) -> list[dict]:
    """Fetch and filter trending hashtags relevant to a topic."""
    try:
        data = get(
            f"{TIKTOK_CC_BASE}/trending/hashtag/list",
            params={"limit": min(limit, 50), "period": 7, "region": region.upper(),
                    "page": 1, "sort_by": "popular"},
            bypass_cache=bypass_cache,
        )
        items = data.get("data", {}).get("list", [])
    except Exception:
        return []

    results = []
    for item in items:
        name = item.get("hashtag_name", "")
        results.append({
            "hashtag": f"#{name}",
            "name": name,
            "video_count": item.get("video_count"),
            "view_count": item.get("view_count"),
            "trend_score": item.get("trend_score"),
            "rank": item.get("rank"),
            "source": "live_trending",
        })

    # Filter by topic relevance if we have enough
    topic_filtered = [r for r in results if topic in r["name"].lower()]
    return topic_filtered if topic_filtered else results
