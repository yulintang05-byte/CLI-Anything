"""Music and sound trend tracker.

Aggregates trending sounds from TikTok and music from YouTube to surface
cross-platform audio trends.  Provides usage guidance so creators know
which tracks to use on which platform.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from cli_anything.viral_trends.core import tiktok_scraper, youtube_scraper

CACHE_DIR = Path.home() / ".config" / "viral-trends" / "cache"
CACHE_TTL = 3600

# Platform music limits (fair-use / rights notes)
PLATFORM_NOTES = {
    "tiktok":   "Use licensed tracks from the TikTok Sound Library for commercial accounts to avoid strikes.",
    "youtube":  "Use YouTube Audio Library tracks or licensed music; unlicensed audio triggers Content ID claims.",
    "instagram":"Instagram Reels has its own licensed music library — search within the app.",
    "shorts":   "YouTube Shorts inherits standard Content ID rules; use royalty-free or licensed tracks.",
}

USAGE_TIPS = [
    "Use trending sounds within 24–72 hours of their peak for maximum algorithmic boost.",
    "Pair a trending sound with an original hook in the first 3 seconds to retain viewers.",
    "Original sounds you create can trend too — add your niche as the sound name.",
    "Duets and Stitches using viral sounds inherit some of that sound's distribution.",
    "On TikTok, sounds in the 'For You' feed are heavily algorithmically promoted.",
    "Cross-post the same audio clip to YouTube Shorts and Instagram Reels — triple reach.",
]


def _cache_path(key: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"music_{key}.json"


def _load_cache(key: str) -> list[dict] | None:
    p = _cache_path(key)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text())
        if time.time() - data.get("ts", 0) < CACHE_TTL:
            return data["items"]
    except (json.JSONDecodeError, KeyError):
        pass
    return None


def _save_cache(key: str, items: list[dict]) -> None:
    _cache_path(key).write_text(json.dumps({"ts": time.time(), "items": items}))


def get_cross_platform_music(limit: int = 20) -> dict:
    """Return music/sound trends aggregated from YouTube and TikTok.

    Returns dict with keys:
        tiktok_sounds     — list of trending TikTok sounds
        youtube_music     — list of trending YouTube music videos
        cross_platform    — sounds/tracks trending on BOTH platforms
        usage_tips        — list of actionable tips
        platform_notes    — rights/licensing guidance per platform
    """
    cached = _load_cache(f"cross_{limit}")
    if cached:
        return cached[0] if cached else {}

    tt_sounds  = tiktok_scraper.get_trending_sounds(limit=limit)
    yt_music   = youtube_scraper.get_trending_music_from_videos(limit=limit)

    # Build cross-platform matches: track titles that appear in both
    tt_titles  = {s["sound"].lower() for s in tt_sounds}
    yt_titles  = {v["title"].lower() for v in yt_music}
    cross_keys = tt_titles & yt_titles

    cross_platform = []
    for s in tt_sounds:
        if s["sound"].lower() in cross_keys:
            cross_platform.append({**s, "platforms": ["tiktok", "youtube"]})

    result = {
        "tiktok_sounds":   tt_sounds,
        "youtube_music":   yt_music,
        "cross_platform":  cross_platform,
        "usage_tips":      USAGE_TIPS,
        "platform_notes":  PLATFORM_NOTES,
    }
    _save_cache(f"cross_{limit}", [result])
    return result


def rank_sounds_by_engagement(sounds: list[dict]) -> list[dict]:
    """Sort sounds by plays/views descending."""
    return sorted(sounds, key=lambda s: s.get("plays", 0) or s.get("views", 0), reverse=True)


def get_usage_guide() -> dict:
    """Return a static guide on how to use trending music effectively."""
    return {
        "tips":           USAGE_TIPS,
        "platform_notes": PLATFORM_NOTES,
        "licensing": {
            "tiktok":   "Built-in Commercial Music Library (CML) for business accounts.",
            "youtube":  "YouTube Audio Library + licensed music via Content ID.",
            "instagram":"Built-in music library inside the Reels editor.",
            "all":      "Epidemic Sound, Artlist, Musicbed — paid royalty-free services.",
        },
        "workflow": [
            "1. Find a trending sound on TikTok Discover > Sounds",
            "2. Check if it's trending on YouTube Shorts too (cross-platform)",
            "3. Create your video content FIRST, then sync to the beat",
            "4. Post within 48h of the sound peaking for best algorithmic pickup",
            "5. Add 2–3 hashtags that match the sound's mood/genre",
        ],
    }
