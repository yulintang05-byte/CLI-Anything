"""Viral music tracking — trending sounds on TikTok and YouTube Shorts."""

import os
import urllib.request
import urllib.parse
import urllib.error
import json
from dataclasses import dataclass


TIKTOK_RAPID_HOST = "tiktok-api6.p.rapidapi.com"
TIKTOK_RAPID_BASE = "https://tiktok-api6.p.rapidapi.com"

# Curated trending sound categories with known viral tracks (May 2025)
# Updated manually — supplement with live API data when keys are available
TRENDING_SOUNDS_CATALOG: dict[str, list[dict]] = {
    "motivational": [
        {"title": "Eye of the Tiger", "artist": "Survivor", "mood": "hype", "best_for": ["fitness", "sports", "motivation"]},
        {"title": "Lose Yourself", "artist": "Eminem", "mood": "intense", "best_for": ["hustle", "grind", "entrepreneurship"]},
        {"title": "Can't Stop the Feeling", "artist": "Justin Timberlake", "mood": "upbeat", "best_for": ["lifestyle", "positivity"]},
    ],
    "chill_aesthetic": [
        {"title": "Aesthetic (Lo-fi)", "artist": "Various", "mood": "chill", "best_for": ["aesthetic", "study", "vlog"]},
        {"title": "Blinding Lights", "artist": "The Weeknd", "mood": "nostalgic", "best_for": ["fashion", "night", "travel"]},
        {"title": "Golden Hour", "artist": "JVKE", "mood": "warm", "best_for": ["lifestyle", "travel", "romance"]},
    ],
    "viral_dance": [
        {"title": "Espresso", "artist": "Sabrina Carpenter", "mood": "fun", "best_for": ["dance", "fun", "fashion"]},
        {"title": "Texas Hold 'Em", "artist": "Beyoncé", "mood": "country_pop", "best_for": ["dance", "country", "trending"]},
        {"title": "Flowers", "artist": "Miley Cyrus", "mood": "empowerment", "best_for": ["selfcare", "beauty", "lifestyle"]},
    ],
    "hype": [
        {"title": "Industry Baby", "artist": "Lil Nas X", "mood": "hype", "best_for": ["gym", "fashion", "goals"]},
        {"title": "HUMBLE.", "artist": "Kendrick Lamar", "mood": "trap", "best_for": ["flex", "confidence", "grind"]},
        {"title": "Tití Me Preguntó", "artist": "Bad Bunny", "mood": "reggaeton", "best_for": ["party", "dance", "lifestyle"]},
    ],
    "trendy_2025": [
        {"title": "APT.", "artist": "ROSE & Bruno Mars", "mood": "upbeat", "best_for": ["trending", "kpop", "dance"]},
        {"title": "Luther", "artist": "Kendrick Lamar & SZA", "mood": "R&B", "best_for": ["love", "aesthetic", "chill"]},
        {"title": "Die With A Smile", "artist": "Lady Gaga & Bruno Mars", "mood": "emotional", "best_for": ["emotional", "love", "ballad"]},
    ],
    "royalty_free": [
        {"title": "Epidemic Sound (subscription)", "url": "https://www.epidemicsound.com", "mood": "varied", "best_for": ["any", "commercial_safe"]},
        {"title": "YouTube Audio Library", "url": "https://studio.youtube.com/channel/UC/music", "mood": "varied", "best_for": ["youtube", "commercial_safe"]},
        {"title": "Pixabay Music", "url": "https://pixabay.com/music/", "mood": "varied", "best_for": ["any", "free", "commercial_safe"]},
    ],
}


@dataclass
class TrendingSound:
    title: str
    artist: str
    platform: str
    play_count: int = 0
    video_count: int = 0
    mood: str = ""
    best_for: list[str] | None = None
    source: str = ""
    url: str = ""

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "artist": self.artist,
            "platform": self.platform,
            "play_count": self.play_count,
            "video_count": self.video_count,
            "mood": self.mood,
            "best_for": self.best_for or [],
            "source": self.source,
            "url": self.url,
        }


def _http_get(url: str, headers: dict | None = None) -> dict | str | None:
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return raw
    except Exception as e:
        return {"error": str(e)}


def fetch_tiktok_trending_sounds(max_results: int = 20) -> list[dict]:
    """Fetch trending TikTok sounds via RapidAPI or return catalog fallback."""
    rapid_key = os.environ.get("TIKTOK_RAPIDAPI_KEY", "")
    if not rapid_key:
        return get_catalog_sounds()

    headers = {
        "x-rapidapi-key": rapid_key,
        "x-rapidapi-host": TIKTOK_RAPID_HOST,
    }
    data = _http_get(
        f"{TIKTOK_RAPID_BASE}/music/trending?count={min(max_results, 30)}",
        headers,
    )
    if not isinstance(data, dict) or "musicList" not in data:
        # Try alternate endpoint
        data = _http_get(f"{TIKTOK_RAPID_BASE}/trending/sounds", headers)

    if isinstance(data, dict) and "musicList" in data:
        results = []
        for item in data["musicList"][:max_results]:
            music = item.get("music", item)
            results.append({
                "platform": "tiktok",
                "title": music.get("title", ""),
                "artist": music.get("authorName", ""),
                "play_count": music.get("playCount", 0),
                "video_count": music.get("videoCount", music.get("useCount", 0)),
                "duration": music.get("duration", 0),
                "url": f"https://www.tiktok.com/music/-{music.get('id', '')}",
                "source": "rapidapi",
            })
        return results

    return get_catalog_sounds()


def get_catalog_sounds(
    category: str | None = None,
    niche: str | None = None,
) -> list[dict]:
    """Return curated sound recommendations from local catalog."""
    results = []
    catalog = TRENDING_SOUNDS_CATALOG

    if category:
        if category not in catalog:
            return []
        catalog = {category: catalog[category]}

    for cat, sounds in catalog.items():
        for sound in sounds:
            if niche and sound.get("best_for") and niche.lower() not in [b.lower() for b in sound["best_for"]]:
                continue
            results.append({
                "category": cat,
                "platform": "tiktok/shorts",
                "source": "catalog",
                **sound,
            })
    return results


def recommend_sounds_for_niche(niche: str) -> list[dict]:
    """Return sounds that fit a content niche."""
    results = []
    for cat, sounds in TRENDING_SOUNDS_CATALOG.items():
        for sound in sounds:
            best_for = sound.get("best_for", [])
            if any(niche.lower() in b.lower() or b.lower() in niche.lower() for b in best_for):
                results.append({"category": cat, **sound})
    if not results:
        # Fallback: return trendy_2025 category
        results = [{"category": "trendy_2025", **s} for s in TRENDING_SOUNDS_CATALOG.get("trendy_2025", [])]
    return results


def list_sound_categories() -> list[str]:
    return list(TRENDING_SOUNDS_CATALOG.keys())
