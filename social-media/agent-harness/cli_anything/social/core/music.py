"""
Trending music and sound intelligence.

Sources:
  1. TikTok Creative Center — trending sounds (live scrape)
  2. YouTube trending music category (live scrape)
  3. Curated evergreen viral sound strategies (static knowledge)
"""
from typing import Dict, List, Optional

from cli_anything.social.core.scraper import (
    tiktok_trending_music,
    youtube_trending_music,
)


def get_trending_music(
    platform: str = "all",
    region: str = "US",
    limit: int = 20,
) -> Dict:
    """Fetch trending music across platforms."""
    results: Dict = {"platform": platform, "region": region}

    errors: List[str] = []

    if platform in ("tiktok", "all"):
        try:
            results["tiktok"] = tiktok_trending_music(region=region, limit=limit)
        except Exception as exc:
            errors.append(f"TikTok music fetch failed: {exc}")
            results["tiktok"] = []

    if platform in ("youtube", "all"):
        try:
            results["youtube"] = youtube_trending_music(region=region, limit=limit)
        except Exception as exc:
            errors.append(f"YouTube music fetch failed: {exc}")
            results["youtube"] = []

    if errors:
        results["warnings"] = errors

    results["strategy"] = music_strategy()
    return results


def music_strategy() -> Dict:
    """Return a static expert-curated music strategy for viral content."""
    return {
        "when_to_use_trending_sounds": [
            "Hook viewers in the first 1-3 seconds with the drop or most recognizable part.",
            "Use a trending sound within 24-72 hours of it appearing on the FYP for maximum boost.",
            "Match the energy of the music to your content — mismatch kills retention.",
            "TikTok's algorithm actively pushes content using trending sounds to more FYP pages.",
        ],
        "sound_selection_framework": {
            "viral_momentum":     "Sounds with 50K-500K uses are in the 'sweet spot' — big enough to be trending, small enough that your video isn't buried.",
            "rising_sounds":      "Sort TikTok Creative Center by 'Rising' to find sounds gaining momentum before peak saturation.",
            "evergreen_sounds":   "Lofi beats, nature sounds, and cinematic scores always perform well for educational and aesthetic content.",
            "original_audio":     "Creating original audio is the highest-ceiling play — if it goes viral, every duet/stitch drives traffic back to you.",
        },
        "music_copyright_guide": {
            "tiktok":    "Use TikTok's built-in sound library — pre-licensed. Third-party music may get muted or restricted.",
            "instagram": "Use Reels audio from Instagram's library. Original audio can be used by others if you allow it.",
            "youtube":   "Use YouTube Audio Library (free) or purchase licenses. Copyright claims can demonetize your video.",
            "tips": [
                "DistroKid, TuneCore, and CD Baby can get your original music onto TikTok/IG with revenue sharing.",
                "Royalty-free doesn't always mean free to use commercially — always read the license.",
                "If you hear a song in a viral video, search the exact title in TikTok Sounds before using it.",
            ],
        },
        "posting_with_music": {
            "tiktok_tips": [
                "Add the trending sound at video creation, not post-upload — it affects discovery.",
                "The 'Save sound' feature shows you sounds used by accounts you follow that are trending.",
                "Use 'Add to Favorites' to build a library of sounds to use in future content.",
            ],
            "content_types_by_sound": [
                {"sound_type": "Trending pop/hiphop", "best_content": "Transitions, GRWM, lifestyle vlogs"},
                {"sound_type": "Slow emotional",      "best_content": "Transformation, before/after, storytelling"},
                {"sound_type": "Upbeat/energetic",    "best_content": "Workouts, cooking timelapse, travel montage"},
                {"sound_type": "Voiceover meme audio","best_content": "POV skits, relatable humor, commentary"},
                {"sound_type": "Lo-fi/ambient",       "best_content": "Study with me, ASMR, aesthetic content"},
            ],
        },
    }
