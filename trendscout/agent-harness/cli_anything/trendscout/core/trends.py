"""TrendScout – cross-platform trend aggregation and analysis."""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from cli_anything.trendscout.core import youtube as yt_mod
from cli_anything.trendscout.core import tiktok as tt_mod


def cross_platform_trends(
    category: str = "all",
    region: str = "us",
    limit: int = 20,
) -> Dict[str, Any]:
    """Aggregate trending hashtags and music across YouTube + TikTok."""
    yt_data = yt_mod.aggregate_trending_hashtags(category=category, region=region, limit=limit)
    tt_data = tt_mod.fetch_trending_hashtags(limit=limit)
    tt_sounds = tt_mod.fetch_trending_sounds(limit=10)

    # Merge hashtag scores with platform weighting
    scores: Dict[str, Dict[str, Any]] = {}

    for item in yt_data.get("top_hashtags", []):
        tag = item["hashtag"].lower()
        scores[tag] = {"tag": item["hashtag"], "youtube_freq": item["frequency"], "tiktok_freq": 0, "tiktok_views": 0}

    for item in tt_data.get("hashtags", []):
        tag = item["hashtag"].lower()
        if tag in scores:
            scores[tag]["tiktok_freq"] += 1
            scores[tag]["tiktok_views"] = item.get("view_count", 0)
        else:
            scores[tag] = {"tag": item["hashtag"], "youtube_freq": 0, "tiktok_freq": 1, "tiktok_views": item.get("view_count", 0)}

    # Score: cross-platform tags get a boost
    def _score(entry: Dict[str, Any]) -> float:
        yt = entry["youtube_freq"]
        tt = entry["tiktok_freq"]
        views = entry["tiktok_views"]
        cross_boost = 3.0 if (yt > 0 and tt > 0) else 1.0
        return (yt * 2 + tt * 1.5 + views / 1_000_000_000) * cross_boost

    sorted_tags = sorted(scores.values(), key=_score, reverse=True)

    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "category": category,
        "region": region,
        "cross_platform_hashtags": sorted_tags[:30],
        "trending_sounds": tt_sounds.get("sounds", [])[:10],
        "youtube_top_hashtags": yt_data.get("top_hashtags", [])[:10],
        "tiktok_top_hashtags": tt_data.get("hashtags", [])[:10],
        "sources_demo_mode": {
            "youtube": yt_data.get("demo_mode", False),
            "tiktok": tt_data.get("demo_mode", False),
        },
    }


def niche_hashtag_report(
    niche: str,
    region: str = "us",
    limit: int = 30,
) -> Dict[str, Any]:
    """Generate a hashtag report for a specific content niche.

    Maps common niche names to relevant categories and seeds hashtag lists.
    """
    niche_lower = niche.lower()
    niche_map = {
        "gaming": {"yt_cat": "gaming", "seed_tags": ["#gaming", "#gamer", "#fps", "#rpg", "#gaming", "#twitch", "#esports", "#game"]},
        "music": {"yt_cat": "music", "seed_tags": ["#music", "#newmusic", "#indie", "#hiphop", "#pop", "#rnb", "#producer"]},
        "beauty": {"yt_cat": "beauty", "seed_tags": ["#beauty", "#makeup", "#skincare", "#grwm", "#beautytok", "#glam", "#tutorial"]},
        "fitness": {"yt_cat": "all", "seed_tags": ["#fitness", "#gym", "#workout", "#gains", "#fitnessmotivation", "#bodybuilding", "#calisthenics"]},
        "food": {"yt_cat": "all", "seed_tags": ["#food", "#foodtok", "#recipe", "#cooking", "#foodie", "#easyrecipe", "#mukbang"]},
        "fashion": {"yt_cat": "beauty", "seed_tags": ["#fashion", "#ootd", "#style", "#outfit", "#streetwear", "#fashiontok", "#haul"]},
        "travel": {"yt_cat": "all", "seed_tags": ["#travel", "#wanderlust", "#traveltok", "#adventure", "#explore", "#vacation", "#backpacking"]},
        "finance": {"yt_cat": "all", "seed_tags": ["#finance", "#money", "#investing", "#stockmarket", "#crypto", "#personalfinance", "#financetips"]},
        "comedy": {"yt_cat": "entertainment", "seed_tags": ["#comedy", "#funny", "#humor", "#memes", "#lol", "#skit", "#comedytok"]},
        "education": {"yt_cat": "science", "seed_tags": ["#education", "#learnontiktok", "#didyouknow", "#science", "#history", "#edutok"]},
        "pets": {"yt_cat": "all", "seed_tags": ["#pets", "#cats", "#dogs", "#dogsoftiktok", "#catsoftiktok", "#cutepets", "#animals"]},
        "tech": {"yt_cat": "tech", "seed_tags": ["#tech", "#technology", "#apple", "#android", "#ai", "#coding", "#programming"]},
        "motivation": {"yt_cat": "all", "seed_tags": ["#motivation", "#mindset", "#selfimprovement", "#grindset", "#hustle", "#success", "#inspiration"]},
        "art": {"yt_cat": "entertainment", "seed_tags": ["#art", "#artist", "#drawing", "#painting", "#digitalart", "#artwork", "#procreate"]},
        "sports": {"yt_cat": "sports", "seed_tags": ["#sports", "#basketball", "#soccer", "#football", "#nba", "#nfl", "#athlete"]},
    }

    config = niche_map.get(niche_lower, {
        "yt_cat": "all",
        "seed_tags": [f"#{niche_lower}", f"#{niche_lower}tok", f"#{niche_lower}tiktok"],
    })

    yt_hashtags = yt_mod.aggregate_trending_hashtags(
        category=config["yt_cat"], region=region, limit=limit
    )
    tt_hashtags = tt_mod.fetch_trending_hashtags(limit=limit)

    # Combine: seed tags + trending tags
    platform_tags = [
        t["hashtag"].lower()
        for t in yt_hashtags.get("top_hashtags", []) + tt_hashtags.get("hashtags", [])
    ]
    all_tags = config["seed_tags"] + [t for t in platform_tags if t not in config["seed_tags"]]

    # Deduplicate preserving order
    seen = set()
    unique_tags = []
    for t in all_tags:
        tl = t.lower()
        if tl not in seen:
            seen.add(tl)
            unique_tags.append(t)

    return {
        "niche": niche,
        "region": region,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "recommended_hashtags": unique_tags[:limit],
        "seed_hashtags": config["seed_tags"],
        "trending_on_youtube": [t["hashtag"] for t in yt_hashtags.get("top_hashtags", [])[:10]],
        "trending_on_tiktok": [t["hashtag"] for t in tt_hashtags.get("hashtags", [])[:10]],
        "strategy_tip": _niche_strategy_tip(niche_lower),
    }


def _niche_strategy_tip(niche: str) -> str:
    tips = {
        "gaming": "Post stream highlights with trending game names. Use #[GameName]clips format. Partner with speedrunners.",
        "music": "Cover trending sounds on TikTok within 24h of a song blowing up. YouTube: reaction + review format.",
        "beauty": "GRWM (Get Ready With Me) format dominates. Post during morning commute hours (7–9am).",
        "fitness": "Transformation content + 30-day challenge format. Post Mon/Weds/Fri (gym motivation days).",
        "food": "Speeded-up cooking videos under 60s perform best. Recipe reveals + ASMR sounds.",
        "fashion": "Outfit change transitions are evergreen. Thrift hauls and dupes consistently trend.",
        "travel": "'Hidden gems in [city]' format generates high saves. Post from airports (viral context).",
        "finance": "Controversy-angle works: 'Things your bank doesn't want you to know'. Relatable money fails.",
        "comedy": "Stitch/Duet trending viral moments within 48h for built-in discovery boost.",
        "education": "Hook with a counterintuitive fact in the first 2 seconds. 'Did you know...' pattern.",
        "pets": "Cute + unexpected behavior = viral formula. Post between 7–9pm when people decompress.",
        "tech": "First-look and unboxing videos spike on product launch days. Be among the first.",
        "motivation": "Short (<30s) quotes set to trending audio. Personal story arcs build loyal audience.",
        "art": "Time-lapse creation videos do extremely well. Process > finished product for engagement.",
        "sports": "Reaction content to live events within 2h of game end. Highlight compilations.",
    }
    return tips.get(niche, f"Post consistently at peak hours (7-9am, 12-2pm, 7-10pm). Mix trending hashtags with niche-specific ones.")


def best_posting_times(platform: str = "both", timezone_name: str = "EST") -> Dict[str, Any]:
    """Return research-backed best posting times per platform."""
    schedule = {
        "tiktok": {
            "best_days": ["Tuesday", "Thursday", "Friday"],
            "best_times_est": [
                "06:00–10:00 (morning commute)",
                "11:00–13:00 (lunch break)",
                "19:00–23:00 (prime evening)",
            ],
            "worst_times": "Weekdays 14:00–16:00 (afternoon slump)",
            "optimal_frequency": "1–3 posts/day",
            "notes": "TikTok's algorithm rewards consistency. Post at least 4x/week for growth phase.",
        },
        "youtube": {
            "best_days": ["Friday", "Saturday", "Sunday"],
            "best_times_est": [
                "12:00–16:00 (weekend afternoon)",
                "20:00–22:00 (prime time)",
            ],
            "worst_times": "Monday/Tuesday early morning",
            "optimal_frequency": "2–3 videos/week (long-form) or daily (Shorts)",
            "notes": "YouTube Shorts get extra push when posted alongside long-form content.",
        },
        "instagram": {
            "best_days": ["Monday", "Wednesday", "Friday"],
            "best_times_est": [
                "09:00–11:00",
                "13:00–14:00",
                "19:00–21:00",
            ],
            "worst_times": "Late night and early morning",
            "optimal_frequency": "4–7 Reels/week, 1–3 Stories/day",
            "notes": "Reels get 22% more engagement than standard video posts.",
        },
    }

    platform_lower = platform.lower()
    if platform_lower == "both":
        return {
            "timezone": timezone_name,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "platforms": schedule,
        }
    if platform_lower in schedule:
        return {
            "platform": platform_lower,
            "timezone": timezone_name,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            **schedule[platform_lower],
        }
    raise ValueError(f"Unknown platform '{platform}'. Choose: tiktok, youtube, instagram, both")
