"""Cross-platform trend aggregation and analysis.

Combines YouTube + TikTok trend data, finds cross-platform momentum,
and produces niche-specific hashtag + content recommendations.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Optional

from . import youtube_scraper as yt
from . import tiktok_scraper as tt


# ── Niche keyword taxonomy ────────────────────────────────────────────

NICHE_KEYWORDS: dict[str, list[str]] = {
    "fitness":    ["gym", "workout", "fitness", "gains", "exercise", "training", "health", "weight", "muscle", "cardio"],
    "beauty":     ["makeup", "skincare", "beauty", "tutorial", "glam", "cosmetics", "glow", "hair", "nails", "routine"],
    "fashion":    ["fashion", "outfit", "ootd", "style", "clothes", "streetwear", "trend", "haul", "lookbook"],
    "food":       ["food", "recipe", "cooking", "baking", "eat", "restaurant", "chef", "foodie", "meal", "vegan"],
    "finance":    ["money", "invest", "finance", "wealth", "stocks", "crypto", "budget", "income", "rich", "business"],
    "travel":     ["travel", "vacation", "trip", "explore", "adventure", "wanderlust", "hotel", "flight", "tourism"],
    "gaming":     ["gaming", "game", "twitch", "minecraft", "fortnite", "esports", "fps", "rpg", "streamer", "lets play"],
    "comedy":     ["funny", "comedy", "meme", "humor", "lol", "prank", "skit", "joke", "laugh", "parody"],
    "motivation": ["motivation", "mindset", "success", "hustle", "grind", "inspire", "goals", "positivity", "growth"],
    "pets":       ["dog", "cat", "pet", "puppy", "kitten", "animals", "cute", "paws", "fluffy", "wildlife"],
    "tech":       ["tech", "ai", "programming", "coding", "software", "gadget", "review", "unboxing", "developer"],
    "dance":      ["dance", "choreography", "hiphop", "ballet", "moves", "freestyle", "tiktokdance", "crew"],
    "music":      ["music", "song", "artist", "rap", "pop", "rnb", "singer", "producer", "beat", "album"],
    "art":        ["art", "drawing", "painting", "digital", "illustration", "design", "creative", "sketch", "artist"],
    "education":  ["learn", "education", "study", "school", "tips", "facts", "howto", "diy", "tutorial", "guide"],
}


def _normalize_tag(tag: str) -> str:
    return tag.lstrip("#").lower().strip()


def _tag_matches_niche(tag: str, niche: str) -> bool:
    keywords = NICHE_KEYWORDS.get(niche.lower(), [])
    t = _normalize_tag(tag)
    return any(kw in t for kw in keywords)


# ── Aggregation ───────────────────────────────────────────────────────

def aggregate_trends(
    niche: Optional[str] = None,
    limit: int = 30,
    country: str = "US",
) -> dict:
    """Fetch and merge trending data from YouTube and TikTok.

    Args:
        niche: Optional niche filter (see NICHE_KEYWORDS keys).
        limit: Number of results per platform.
        country: Country code for YouTube regional trends.

    Returns:
        Dict with youtube_videos, tiktok_videos, cross_platform_hashtags,
        trending_music, niche_hashtags.
    """
    result: dict = {
        "youtube_videos": [],
        "tiktok_videos": [],
        "youtube_hashtags": [],
        "tiktok_hashtags": [],
        "cross_platform_hashtags": [],
        "trending_music": [],
        "niche_hashtags": [],
        "errors": [],
    }

    # YouTube
    try:
        yt_videos = yt.get_trending_videos(limit=limit, country=country)
        result["youtube_videos"] = yt_videos
        yt_tags = yt.get_trending_hashtags(limit=limit, country=country)
        result["youtube_hashtags"] = yt_tags
    except Exception as e:
        result["errors"].append(f"YouTube: {e}")

    # TikTok
    try:
        tt_videos = tt.get_trending_videos(limit=limit)
        result["tiktok_videos"] = tt_videos
        tt_tags = tt.get_trending_hashtags(limit=limit)
        result["tiktok_hashtags"] = tt_tags
    except Exception as e:
        result["errors"].append(f"TikTok: {e}")

    # Cross-platform hashtag overlap
    yt_tag_set = {_normalize_tag(t.get("hashtag", "")) for t in result["youtube_hashtags"]}
    tt_tag_set = {_normalize_tag(t.get("hashtag", "")) for t in result["tiktok_hashtags"]}
    cross = yt_tag_set & tt_tag_set
    result["cross_platform_hashtags"] = sorted([f"#{t}" for t in cross if t])

    # Trending music (TikTok-first, supplement with YouTube music)
    try:
        tt_music = tt.get_trending_music(limit=10)
        result["trending_music"] = tt_music
    except Exception as e:
        result["errors"].append(f"TikTok music: {e}")

    if not result["trending_music"]:
        try:
            yt_music = yt.get_trending_music(limit=10, country=country)
            result["trending_music"] = [
                {"title": v["song_title"], "artist": v["artist"], "platform": "youtube"}
                for v in yt_music
            ]
        except Exception:
            pass

    # Niche filtering
    if niche:
        all_hashtags = (
            [_normalize_tag(t.get("hashtag", "")) for t in result["youtube_hashtags"]] +
            [_normalize_tag(t.get("hashtag", "")) for t in result["tiktok_hashtags"]]
        )
        niche_tags = [t for t in all_hashtags if _tag_matches_niche(t, niche)]
        niche_tags += NICHE_KEYWORDS.get(niche.lower(), [])
        seen = set()
        unique_niche: list[str] = []
        for t in niche_tags:
            if t not in seen:
                seen.add(t)
                unique_niche.append(f"#{t}")
        result["niche_hashtags"] = unique_niche[:30]

    return result


def get_cross_platform_music(limit: int = 20) -> list[dict]:
    """Identify music trending on both YouTube and TikTok simultaneously.

    Returns music sorted by estimated cross-platform momentum.
    """
    try:
        yt_music = yt.get_trending_music(limit=30)
    except Exception:
        yt_music = []
    try:
        tt_music = tt.get_trending_music(limit=30)
    except Exception:
        tt_music = []

    yt_titles = {v.get("song_title", "").lower(): v for v in yt_music}
    tt_titles = {m.get("title", "").lower(): m for m in tt_music}

    cross = []
    for title, yt_v in yt_titles.items():
        for tt_title, tt_m in tt_titles.items():
            if title and tt_title and (title[:20] in tt_title or tt_title[:20] in title):
                cross.append({
                    "title": yt_v.get("song_title"),
                    "artist": yt_v.get("artist"),
                    "youtube_views": yt_v.get("views"),
                    "tiktok_uses": tt_m.get("use_count"),
                    "youtube_url": yt_v.get("url"),
                    "tiktok_url": tt_m.get("tiktok_url"),
                    "momentum": "high",
                })
                break

    # Add platform-unique trending
    for m in tt_music[:limit]:
        if not any(m.get("title", "").lower()[:20] in c["title"].lower() for c in cross):
            cross.append({
                "title": m.get("title"),
                "artist": m.get("author"),
                "tiktok_uses": m.get("use_count"),
                "momentum": "tiktok",
            })

    return cross[:limit]


def get_hashtag_suggestions(niche: str, platform: str = "both", count: int = 30) -> list[str]:
    """Generate optimised hashtag set for a niche.

    Mixes high-reach, mid-tier, and niche-specific tags for best discoverability.

    Args:
        niche: Content niche (fitness, beauty, food, etc.).
        platform: 'youtube', 'tiktok', or 'both'.
        count: Total hashtags to return.

    Returns:
        List of hashtag strings (with # prefix), ordered by strategy:
        broad → mid → niche.
    """
    niche = niche.lower().strip()
    keywords = NICHE_KEYWORDS.get(niche, [niche])

    # Tier 1 — broad reach (always trending, high competition)
    broad = ["#fyp", "#viral", "#trending", "#foryou", "#explore"]

    # Tier 2 — mid-tier (platform-relevant)
    mid_yt = ["#youtubeshorts", "#shorts", "#youtube", "#subscribe", "#newvideo"]
    mid_tt = ["#tiktok", "#tiktokviral", "#tiktokcreator", "#fypage", "#4u"]

    # Tier 3 — niche-specific
    niche_tags = [f"#{kw.replace(' ', '')}" for kw in keywords]

    # Tier 4 — engagement bait (use sparingly)
    engagement = ["#follow", "#like", "#comment", "#share", "#duet"]

    if platform == "youtube":
        combined = broad + mid_yt + niche_tags + engagement
    elif platform == "tiktok":
        combined = broad + mid_tt + niche_tags + engagement
    else:
        combined = broad + mid_yt[:3] + mid_tt[:3] + niche_tags + engagement

    # Deduplicate preserving order
    seen: set = set()
    unique: list[str] = []
    for tag in combined:
        t = tag.lower()
        if t not in seen:
            seen.add(t)
            unique.append(tag)
    return unique[:count]


def analyze_trend_velocity(videos: list[dict]) -> dict:
    """Estimate which trends are accelerating vs. decelerating.

    Analyses upload recency vs. view count to score trend momentum.

    Args:
        videos: List of video dicts (from get_trending_videos).

    Returns:
        Dict with hot_trends, rising_trends, fading_trends lists.
    """
    hot, rising, fading = [], [], []
    for v in videos:
        views = v.get("views") or 0
        date_str = v.get("upload_date") or ""
        try:
            from datetime import datetime, timezone
            if date_str and len(date_str) == 8:
                upload = datetime.strptime(date_str, "%Y%m%d").replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                days_old = (now - upload).days
                daily_views = views / max(days_old, 1)
                entry = {**v, "days_old": days_old, "daily_views": int(daily_views)}
                if days_old <= 3 and views > 100_000:
                    hot.append(entry)
                elif days_old <= 7:
                    rising.append(entry)
                else:
                    fading.append(entry)
            else:
                rising.append(v)
        except Exception:
            rising.append(v)
    return {
        "hot_trends": sorted(hot, key=lambda x: x.get("daily_views", 0), reverse=True),
        "rising_trends": sorted(rising, key=lambda x: x.get("views", 0) or 0, reverse=True),
        "fading_trends": fading,
    }
