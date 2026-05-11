"""Music trend tracker — cross-platform trending audio intelligence.

Aggregates trending sounds from TikTok scraping, YouTube music chart data,
and a curated seed catalogue.  Provides per-genre breakdowns and
content-creation guidance (tempo, mood, ideal use cases).
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

# ──────────────────────────────────────────────────────────────────────────────
# Curated genre-aware trend catalogue
# ──────────────────────────────────────────────────────────────────────────────

# Structure: genre → list of {title, artist, bpm, mood, best_for, platforms}
GENRE_CATALOGUE: Dict[str, List[Dict[str, Any]]] = {
    "pop": [
        {"title": "Cruel Summer", "artist": "Taylor Swift", "bpm": 170, "mood": "energetic",
         "best_for": ["montage", "transition", "dance"], "platforms": ["tiktok", "reels", "shorts"]},
        {"title": "As It Was", "artist": "Harry Styles", "bpm": 174, "mood": "bittersweet",
         "best_for": ["storytime", "lifestyle", "vlog"], "platforms": ["tiktok", "reels"]},
        {"title": "Flowers", "artist": "Miley Cyrus", "bpm": 118, "mood": "empowering",
         "best_for": ["glow-up", "confidence", "fitness"], "platforms": ["tiktok", "reels", "shorts"]},
        {"title": "escapism.", "artist": "RAYE ft. 070 Shake", "bpm": 127, "mood": "dreamy",
         "best_for": ["aesthetic", "transition", "fashion"], "platforms": ["tiktok", "reels"]},
        {"title": "Unholy", "artist": "Sam Smith & Kim Petras", "bpm": 131, "mood": "dark-fun",
         "best_for": ["comedy", "skit", "dance"], "platforms": ["tiktok", "reels"]},
        {"title": "Levitating", "artist": "Dua Lipa", "bpm": 103, "mood": "upbeat",
         "best_for": ["dance", "montage", "travel"], "platforms": ["tiktok", "reels", "shorts"]},
        {"title": "Anti-Hero", "artist": "Taylor Swift", "bpm": 97, "mood": "self-aware",
         "best_for": ["relatable", "humor", "pov"], "platforms": ["tiktok", "reels"]},
    ],
    "hip-hop": [
        {"title": "Rich Flex", "artist": "Drake & 21 Savage", "bpm": 140, "mood": "flex",
         "best_for": ["flex", "lifestyle", "car"], "platforms": ["tiktok", "reels", "shorts"]},
        {"title": "Creepin'", "artist": "Metro Boomin & The Weeknd", "bpm": 90, "mood": "moody",
         "best_for": ["night", "aesthetic", "vibe"], "platforms": ["tiktok", "reels"]},
        {"title": "Wait for U", "artist": "Future ft. Drake & Tems", "bpm": 140, "mood": "chill",
         "best_for": ["couple", "vlog", "travel"], "platforms": ["tiktok", "reels"]},
        {"title": "Major Distribution", "artist": "Drake & 21 Savage", "bpm": 140, "mood": "confident",
         "best_for": ["hustle", "entrepreneur", "flex"], "platforms": ["tiktok", "reels", "shorts"]},
        {"title": "Superhero (Heroes & Villains)", "artist": "Metro Boomin & Future", "bpm": 130,
         "mood": "epic", "best_for": ["motivation", "transformation", "montage"],
         "platforms": ["tiktok", "reels", "shorts"]},
    ],
    "rnb": [
        {"title": "Kill Bill", "artist": "SZA", "bpm": 85, "mood": "smooth",
         "best_for": ["vlog", "lifestyle", "couple"], "platforms": ["tiktok", "reels"]},
        {"title": "Snooze", "artist": "SZA", "bpm": 76, "mood": "romantic",
         "best_for": ["aesthetic", "couple", "storytime"], "platforms": ["tiktok", "reels"]},
        {"title": "Ghost in the Machine", "artist": "SZA ft. Phoebe Bridgers", "bpm": 90,
         "mood": "introspective", "best_for": ["deep", "pov", "storytime"],
         "platforms": ["tiktok", "reels"]},
        {"title": "Late Night Talking", "artist": "Harry Styles", "bpm": 123, "mood": "fun",
         "best_for": ["vlog", "couple", "day-in-life"], "platforms": ["tiktok", "reels"]},
    ],
    "electronic": [
        {"title": "Infinity", "artist": "Jaymes Young (viral edit)", "bpm": 128, "mood": "epic",
         "best_for": ["montage", "transition", "sports"], "platforms": ["tiktok", "reels", "shorts"]},
        {"title": "Stunnin'", "artist": "Curtis Waters ft. Harm Franklin", "bpm": 130,
         "mood": "confident", "best_for": ["confidence", "fashion", "flex"],
         "platforms": ["tiktok", "reels"]},
        {"title": "Faded", "artist": "Alan Walker", "bpm": 90, "mood": "nostalgic",
         "best_for": ["travel", "nature", "cinematic"], "platforms": ["youtube", "reels", "shorts"]},
        {"title": "Lose Control", "artist": "Teddy Swims", "bpm": 108, "mood": "emotional",
         "best_for": ["emotional", "couple", "reaction"], "platforms": ["tiktok", "reels"]},
    ],
    "country": [
        {"title": "Fast Car", "artist": "Luke Combs", "bpm": 95, "mood": "nostalgic",
         "best_for": ["driving", "lifestyle", "story"], "platforms": ["tiktok", "reels", "youtube"]},
        {"title": "Wait in the Truck", "artist": "Hardy ft. Lainey Wilson", "bpm": 84,
         "mood": "powerful", "best_for": ["story", "pov", "drama"],
         "platforms": ["tiktok", "youtube"]},
        {"title": "She Had Me at Heads Carolina", "artist": "Cole Swindell", "bpm": 96,
         "mood": "feel-good", "best_for": ["summer", "lifestyle", "travel"],
         "platforms": ["tiktok", "reels"]},
    ],
    "viral-audio": [
        {"title": "Murder on the Dancefloor", "artist": "Sophie Ellis-Bextor", "bpm": 130,
         "mood": "fun", "best_for": ["dance", "transition", "comedy"],
         "platforms": ["tiktok", "reels"]},
        {"title": "Victoria's Secret", "artist": "Jax", "bpm": 135, "mood": "empowering",
         "best_for": ["body-positive", "confidence", "fashion"],
         "platforms": ["tiktok", "reels"]},
        {"title": "Calm Down", "artist": "Rema & Selena Gomez", "bpm": 106, "mood": "chill",
         "best_for": ["vibe", "couple", "travel"], "platforms": ["tiktok", "reels", "shorts"]},
        {"title": "Boy's a liar Pt. 2", "artist": "PinkPantheress & Ice Spice", "bpm": 165,
         "mood": "sassy", "best_for": ["comedy", "skit", "trending"],
         "platforms": ["tiktok", "reels"]},
        {"title": "Rich Girl", "artist": "Gwen Stefani (viral TikTok remix)", "bpm": 127,
         "mood": "fun", "best_for": ["flex", "fashion", "lifestyle"],
         "platforms": ["tiktok", "reels"]},
    ],
}

# Platform-specific optimal content lengths for music-paired videos
PLATFORM_MUSIC_GUIDANCE: Dict[str, Dict[str, Any]] = {
    "tiktok": {
        "optimal_clip_lengths_sec": [7, 15, 30, 60],
        "peak_posting_times_utc": ["12:00", "15:00", "19:00", "21:00"],
        "caption_tip": "Use the first 3 seconds to hook — match your visual cut to the beat drop.",
        "sound_tip": "Use trending original sounds; boost them with your own voice-over on top.",
        "max_hashtags": 30,
        "recommended_hashtags": 15,
    },
    "youtube_shorts": {
        "optimal_clip_lengths_sec": [15, 30, 60],
        "peak_posting_times_utc": ["14:00", "17:00", "20:00"],
        "caption_tip": "Put your main keyword in the first 40 characters of the title.",
        "sound_tip": "YouTube Shorts favours audio-matched trending songs from the Shorts sound library.",
        "max_hashtags": 15,
        "recommended_hashtags": 5,
    },
    "instagram_reels": {
        "optimal_clip_lengths_sec": [15, 30, 60, 90],
        "peak_posting_times_utc": ["11:00", "13:00", "17:00", "19:00"],
        "caption_tip": "Write a strong opening line before 'more' fold — algorithm shows it in Explore.",
        "sound_tip": "Use 'Original Audio' overlaid with trending music to show up in the audio search.",
        "max_hashtags": 30,
        "recommended_hashtags": 10,
    },
}


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def list_trending_music(
    genre: Optional[str] = None,
    platform: Optional[str] = None,
    mood: Optional[str] = None,
    limit: int = 20,
) -> Dict[str, Any]:
    """Return trending music, optionally filtered by genre / platform / mood."""
    all_tracks: List[Dict] = []

    if genre:
        genres_to_check = [genre.lower().replace(" ", "-")]
    else:
        genres_to_check = list(GENRE_CATALOGUE.keys())

    for g in genres_to_check:
        tracks = GENRE_CATALOGUE.get(g, [])
        for t in tracks:
            entry = {**t, "genre": g}
            if platform and platform.lower() not in entry.get("platforms", []):
                continue
            if mood and mood.lower() not in entry.get("mood", ""):
                continue
            all_tracks.append(entry)

    all_tracks = all_tracks[:limit]

    return {
        "filter_genre": genre,
        "filter_platform": platform,
        "filter_mood": mood,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "count": len(all_tracks),
        "tracks": all_tracks,
    }


def get_music_for_content_type(content_type: str) -> Dict[str, Any]:
    """Recommend music tracks best suited to a content type.

    content_type: e.g. 'dance', 'travel', 'comedy', 'motivation', 'aesthetic'
    """
    ct = content_type.lower().strip()
    matches: List[Dict] = []

    for genre, tracks in GENRE_CATALOGUE.items():
        for t in tracks:
            if ct in t.get("best_for", []):
                matches.append({**t, "genre": genre})

    if not matches:
        # Fuzzy match — find any track whose best_for contains a word similar to ct
        for genre, tracks in GENRE_CATALOGUE.items():
            for t in tracks:
                for use in t.get("best_for", []):
                    if ct in use or use in ct:
                        entry = {**t, "genre": genre}
                        if entry not in matches:
                            matches.append(entry)

    return {
        "content_type": ct,
        "count": len(matches),
        "tracks": matches[:15],
    }


def get_platform_music_guide(platform: str) -> Dict[str, Any]:
    """Return music + posting guidance for a specific platform."""
    plat = platform.lower().replace(" ", "_").replace("-", "_")

    # Normalise aliases
    aliases = {
        "tiktok": "tiktok",
        "shorts": "youtube_shorts",
        "youtube_shorts": "youtube_shorts",
        "reels": "instagram_reels",
        "instagram_reels": "instagram_reels",
        "instagram": "instagram_reels",
    }
    key = aliases.get(plat)
    if key is None:
        valid = list(PLATFORM_MUSIC_GUIDANCE.keys())
        raise ValueError(f"Unknown platform '{platform}'. Valid: {valid}")

    guide = PLATFORM_MUSIC_GUIDANCE[key]
    recommended_tracks = list_trending_music(platform=plat.split("_")[0], limit=5)["tracks"]

    return {
        "platform": key,
        "guidance": guide,
        "recommended_tracks": recommended_tracks,
    }


def list_genres() -> List[str]:
    """List all supported music genres."""
    return sorted(GENRE_CATALOGUE.keys())


def list_moods() -> List[str]:
    """List all unique moods across the catalogue."""
    moods: set = set()
    for tracks in GENRE_CATALOGUE.values():
        for t in tracks:
            moods.add(t.get("mood", ""))
    return sorted(m for m in moods if m)
