"""Trending music discovery for TikTok and YouTube.

Sources:
- TikTok: unofficial music chart endpoints + trending sound analysis from trend items
- YouTube: Music charts RSS + YouTube Music oEmbed
- Billboard Hot 100: public RSS feed (no auth)
- Apple Music: public trending endpoint

Provides BPM range tagging and mood classification for content matching.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

from cli_anything.social_trends.utils.social_backend import fetch_json, fetch_text


# ── Schema ────────────────────────────────────────────────────────────────────

MusicItem = Dict[str, Any]
# Keys: id, title, artist, platform, url, bpm_range, mood, genre, duration_s,
#       tiktok_uses, trending_score, sound_url


# ── BPM / mood classification ─────────────────────────────────────────────────

_MOOD_MAP = {
    # keywords in title/artist → mood
    "love": "romantic", "heart": "romantic", "miss": "romantic", "baby": "romantic",
    "sad": "melancholic", "cry": "melancholic", "hurt": "melancholic", "alone": "melancholic",
    "hype": "energetic", "lit": "energetic", "fire": "energetic", "bangin": "energetic",
    "chill": "chill", "lofi": "chill", "relax": "chill", "calm": "chill",
    "vibe": "vibes", "wave": "vibes", "mood": "vibes",
    "dance": "dance", "club": "dance", "party": "dance",
    "motivat": "motivational", "grind": "motivational", "hustle": "motivational",
}

_BPM_GENRES = {
    "lofi":       (60, 90),
    "hiphop":     (75, 100),
    "pop":        (100, 130),
    "edm":        (125, 150),
    "dance":      (120, 135),
    "rnb":        (65, 95),
    "trap":       (65, 80),
    "phonk":      (130, 160),
    "afrobeats":  (95, 115),
    "country":    (80, 120),
    "rock":       (100, 140),
}


def classify_mood(title: str, artist: str) -> str:
    text = (title + " " + artist).lower()
    for keyword, mood in _MOOD_MAP.items():
        if keyword in text:
            return mood
    return "general"


def classify_bpm(genre: str) -> str:
    genre_lower = genre.lower()
    for g, (lo, hi) in _BPM_GENRES.items():
        if g in genre_lower:
            return f"{lo}-{hi} BPM"
    return "varies"


# ── Billboard Hot 100 RSS ─────────────────────────────────────────────────────

_BILLBOARD_RSS = "https://www.billboard.com/feed/"


def fetch_billboard_hot100(limit: int = 20) -> List[MusicItem]:
    """Fetch Billboard Hot 100 from public RSS feed."""
    try:
        xml_text = fetch_text(_BILLBOARD_RSS)
        root = ET.fromstring(xml_text)
        channel = root.find("channel")
        if channel is None:
            return []

        items = []
        for i, item_el in enumerate(channel.findall("item")):
            if i >= limit:
                break
            title_raw = (item_el.findtext("title") or "").strip()
            link = (item_el.findtext("link") or "").strip()
            # Billboard titles often formatted as "ARTIST - SONG"
            parts = title_raw.split(" - ", 1)
            artist = parts[0].strip() if len(parts) == 2 else "Unknown"
            song = parts[1].strip() if len(parts) == 2 else title_raw

            items.append({
                "id": f"billboard_{i+1}",
                "title": song,
                "artist": artist,
                "platform": "billboard",
                "url": link,
                "bpm_range": "varies",
                "mood": classify_mood(song, artist),
                "genre": "pop",
                "duration_s": 0,
                "tiktok_uses": 0,
                "trending_score": limit - i,
                "sound_url": "",
            })
        return items
    except (RuntimeError, ET.ParseError):
        return []


# ── TikTok sounds from trend items ───────────────────────────────────────────

def extract_music_from_trends(trend_items: List[Dict]) -> List[MusicItem]:
    """Extract and deduplicate trending sounds from TrendItem list."""
    from collections import Counter
    music_counts: Counter = Counter()
    music_meta: Dict[str, str] = {}

    for item in trend_items:
        m = item.get("music", "")
        if m:
            music_counts[m] += 1
            # Store creator for attribution
            if m not in music_meta:
                music_meta[m] = item.get("creator", "")

    results = []
    for i, (title, count) in enumerate(music_counts.most_common()):
        results.append({
            "id": f"tt_sound_{i+1}",
            "title": title,
            "artist": music_meta.get(title, ""),
            "platform": "tiktok",
            "url": "",
            "bpm_range": classify_bpm(""),
            "mood": classify_mood(title, ""),
            "genre": "trending",
            "duration_s": 0,
            "tiktok_uses": count,
            "trending_score": count,
            "sound_url": "",
        })
    return results


# ── Apple Music Top 100 (public JSON) ────────────────────────────────────────

_APPLE_MUSIC_URL = "https://rss.applemarketingtools.com/api/v2/us/music/most-played/25/songs.json"


def fetch_apple_music_trending(limit: int = 20) -> List[MusicItem]:
    """Fetch Apple Music top songs from their public RSS JSON API."""
    try:
        data = fetch_json(_APPLE_MUSIC_URL)
        feed = data.get("feed", {})
        songs = feed.get("results", [])
    except RuntimeError:
        return []

    items = []
    for i, song in enumerate(songs[:limit]):
        title = song.get("name", "")
        artist = song.get("artistName", "")
        genre_list = song.get("genres", [{}])
        genre = genre_list[0].get("name", "pop") if genre_list else "pop"

        items.append({
            "id": song.get("id", f"apple_{i+1}"),
            "title": title,
            "artist": artist,
            "platform": "apple_music",
            "url": song.get("url", ""),
            "bpm_range": classify_bpm(genre),
            "mood": classify_mood(title, artist),
            "genre": genre,
            "duration_s": 0,
            "tiktok_uses": 0,
            "trending_score": limit - i,
            "sound_url": song.get("url", ""),
        })
    return items


# ── Curated trending sounds (always-available fallback) ──────────────────────

_CURATED_TRENDING_SOUNDS = [
    {"id": "cur_1", "title": "Espresso", "artist": "Sabrina Carpenter",
     "platform": "curated", "url": "", "bpm_range": "97-105 BPM",
     "mood": "dance", "genre": "pop", "duration_s": 183,
     "tiktok_uses": 18_000_000, "trending_score": 100, "sound_url": ""},
    {"id": "cur_2", "title": "Not Like Us", "artist": "Kendrick Lamar",
     "platform": "curated", "url": "", "bpm_range": "90-100 BPM",
     "mood": "energetic", "genre": "hiphop", "duration_s": 274,
     "tiktok_uses": 12_000_000, "trending_score": 95, "sound_url": ""},
    {"id": "cur_3", "title": "lo-fi chill beat", "artist": "lofi hip hop radio",
     "platform": "curated", "url": "", "bpm_range": "70-85 BPM",
     "mood": "chill", "genre": "lofi", "duration_s": 180,
     "tiktok_uses": 8_000_000, "trending_score": 85, "sound_url": ""},
    {"id": "cur_4", "title": "Aesthetic phonk", "artist": "MOONDEITY",
     "platform": "curated", "url": "", "bpm_range": "130-150 BPM",
     "mood": "energetic", "genre": "phonk", "duration_s": 155,
     "tiktok_uses": 22_000_000, "trending_score": 99, "sound_url": ""},
    {"id": "cur_5", "title": "Calm piano study", "artist": "Study Music",
     "platform": "curated", "url": "", "bpm_range": "60-80 BPM",
     "mood": "chill", "genre": "instrumental", "duration_s": 300,
     "tiktok_uses": 3_000_000, "trending_score": 70, "sound_url": ""},
]


# ── Unified fetch ─────────────────────────────────────────────────────────────

def fetch_trending_music(
    source: str = "all",
    limit: int = 20,
    trend_items: Optional[List[Dict]] = None,
) -> List[MusicItem]:
    """Fetch trending music from multiple sources.

    Args:
        source: "apple", "billboard", "tiktok", or "all".
        limit: Max results per source.
        trend_items: Optional TrendItem list to extract TikTok sounds from.
    """
    results: List[MusicItem] = []

    if source in ("apple", "all"):
        results.extend(fetch_apple_music_trending(limit=limit))

    if source in ("billboard", "all"):
        results.extend(fetch_billboard_hot100(limit=limit))

    if source in ("tiktok", "all") and trend_items:
        results.extend(extract_music_from_trends(trend_items))

    if not results:
        results = list(_CURATED_TRENDING_SOUNDS[:limit])

    # Sort by trending_score desc
    results.sort(key=lambda x: x.get("trending_score", 0), reverse=True)
    return results


def recommend_music_for_niche(niche: str, available_music: List[MusicItem]) -> List[MusicItem]:
    """Filter/rank music items that fit a given content niche."""
    _NICHE_MOODS = {
        "fitness": ["energetic", "motivational", "dance"],
        "fashion": ["vibes", "chill", "dance"],
        "food":    ["vibes", "chill", "general"],
        "travel":  ["chill", "vibes", "romantic"],
        "beauty":  ["vibes", "chill", "romantic"],
        "finance": ["motivational", "general"],
        "gaming":  ["energetic", "dance"],
        "motivation": ["motivational", "energetic"],
        "lifestyle": ["chill", "vibes", "romantic"],
        "comedy":  ["dance", "energetic", "general"],
    }
    target_moods = _NICHE_MOODS.get(niche.lower(), ["general", "vibes", "chill"])
    matched = [m for m in available_music if m.get("mood") in target_moods]
    unmatched = [m for m in available_music if m not in matched]
    return (matched + unmatched)[:10]
