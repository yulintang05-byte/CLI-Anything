"""Trending music and sounds tracker for social platforms."""

from typing import Any

# Curated trending music database — May 2026
_TRENDING_MUSIC: dict[str, list[dict]] = {
    "tiktok": [
        {
            "id": "tk_mus_001",
            "title": "Into The Groove (Viral Remix)",
            "artist": "Madonna (remix)",
            "genre": "Pop / Dance",
            "bpm": 128,
            "trend_type": "dance_challenge",
            "use_case": "dance videos, GRWM, transformation reels",
            "status": "peaking",
            "trend_name": "Follow That Tune",
            "tip": "Sync outfit reveal or transformation to the drop at 0:32",
        },
        {
            "id": "tk_mus_002",
            "title": "Bridgerton Waltz (Pop Edit)",
            "artist": "Netflix x Various Artists",
            "genre": "Orchestral Pop",
            "bpm": 96,
            "trend_type": "aesthetic",
            "use_case": "formal-to-casual transitions, aesthetic vlogs, OOTD",
            "status": "growing",
            "trend_name": "Bridgerton Dance",
            "tip": "Cut from elegant opening to casual reveal — contrast is the hook",
        },
        {
            "id": "tk_mus_003",
            "title": "DRIFT PHONK (Various)",
            "artist": "Multiple Phonk Artists",
            "genre": "Phonk",
            "bpm": 140,
            "trend_type": "dance_challenge",
            "use_case": "high-energy edits, gym videos, car content, dance challenges",
            "status": "evergreen",
            "trend_name": "Phonk Dance Challenge",
            "tip": "Use the drop as your key transition moment — gymrats love this",
        },
        {
            "id": "tk_mus_004",
            "title": "Brazilian Phonk 2026",
            "artist": "Various Brazilian Artists",
            "genre": "Brazilian Phonk",
            "bpm": 150,
            "trend_type": "viral_audio",
            "use_case": "montage videos, street content, fitness edits",
            "status": "growing",
            "trend_name": "Phonk Dance Challenge variant",
            "tip": "Brazilian phonk hits especially well for street-style and sports content",
        },
        {
            "id": "tk_mus_005",
            "title": "Lo-fi Morning Ambient",
            "artist": "Various Lo-fi Producers",
            "genre": "Lo-fi / Ambient",
            "bpm": 75,
            "trend_type": "vibe",
            "use_case": "morning routine vlogs, study videos, aesthetic lifestyle",
            "status": "evergreen",
            "trend_name": "Slow-Living Morning Routine",
            "tip": "Don't overcut to the beat — let clips breathe for 3-5 seconds each",
        },
        {
            "id": "tk_mus_006",
            "title": "Soft Cinematic Background",
            "artist": "Various Film Score Producers",
            "genre": "Cinematic / Ambient",
            "bpm": 60,
            "trend_type": "storytelling",
            "use_case": "storytime videos, emotional reveals, business journey content",
            "status": "peaking",
            "trend_name": "Emotional ROI Storytime",
            "tip": "Builds emotional tension without distracting from spoken narration",
        },
        {
            "id": "tk_mus_007",
            "title": "ASMR Kitchen Sounds",
            "artist": "N/A (Sound FX)",
            "genre": "ASMR",
            "bpm": None,
            "trend_type": "food_content",
            "use_case": "cooking videos, recipe reveals, food ASMR",
            "status": "evergreen",
            "trend_name": "Viral Recipe trend",
            "tip": "Layered ASMR sounds (crunch + pour + sizzle) outperform music for food content",
        },
        {
            "id": "tk_mus_008",
            "title": "Money Counting Sound Effect",
            "artist": "N/A (Sound FX)",
            "genre": "Sound Effect",
            "bpm": None,
            "trend_type": "business_reveal",
            "use_case": "income reveal, earnings screenshot, side hustle content",
            "status": "peaking",
            "trend_name": "AI Side Hustle Reveal",
            "tip": "Pair with dramatic zoom-in on screen showing earnings — 3-second hook rule",
        },
    ],
    "youtube": [
        {
            "id": "yt_mus_001",
            "title": "Chaos/Meme Background Music",
            "artist": "Various Royalty-Free",
            "genre": "Electronic / Meme",
            "bpm": 120,
            "trend_type": "entertainment",
            "use_case": "compilation videos, chaos culture Shorts",
            "status": "peaking",
            "trend_name": "Chaos Culture Compilations",
            "tip": "Sync audio cuts to visual cuts exactly — YouTube's algorithm rewards retention",
        },
        {
            "id": "yt_mus_002",
            "title": "Lo-fi Study/Chill Beats",
            "artist": "Chillhop / Lo-fi Hip Hop",
            "genre": "Lo-fi Hip Hop",
            "bpm": 80,
            "trend_type": "background",
            "use_case": "slow vlogs, cozy content, study-with-me videos",
            "status": "evergreen",
            "trend_name": "Cozy Slow-Living Vlogs",
            "tip": "YouTube audiences stay 40% longer on cozy content with lo-fi background",
        },
        {
            "id": "yt_mus_003",
            "title": "Dramatic String Score",
            "artist": "Various Film Score / Epic Music",
            "genre": "Cinematic",
            "bpm": 90,
            "trend_type": "drama",
            "use_case": "micro-drama shorts, storytime series, tension building",
            "status": "growing",
            "trend_name": "Micro-Drama Storytelling",
            "tip": "Cliffhanger moment should hit exactly at the 45-second mark for Shorts",
        },
        {
            "id": "yt_mus_004",
            "title": "Sports Hype / EDM Drop",
            "artist": "Various EDM Artists",
            "genre": "EDM / Sports Hype",
            "bpm": 135,
            "trend_type": "sports",
            "use_case": "sports highlight reels, gaming montages, reaction videos",
            "status": "evergreen",
            "trend_name": "Sports Recap Shorts",
            "tip": "Drop must coincide with the peak highlight moment — pre-roll 3 seconds of build-up",
        },
        {
            "id": "yt_mus_005",
            "title": "Nostalgic Synthwave / Y2K",
            "artist": "Various Synthwave Producers",
            "genre": "Synthwave / Y2K",
            "bpm": 100,
            "trend_type": "nostalgia",
            "use_case": "2000s/2010s nostalgia edits, throwback vlogs, pop culture essays",
            "status": "peaking",
            "trend_name": "Nostalgic Edit Series",
            "tip": "Layer era-appropriate music with VHS filter and jump cuts for maximum nostalgia effect",
        },
    ],
}


def trending_music(platform: str) -> list[dict]:
    """Return trending music for a platform."""
    if platform not in _TRENDING_MUSIC:
        raise ValueError(f"Unknown platform '{platform}'. Choose from: {', '.join(_TRENDING_MUSIC.keys())}")
    return _TRENDING_MUSIC[platform]


def search_music(query: str, platform: str = "all") -> list[dict]:
    """Search trending music by title, artist, genre, or use case."""
    q = query.lower()
    platforms = list(_TRENDING_MUSIC.keys()) if platform == "all" else [platform]
    results = []
    for p in platforms:
        for track in _TRENDING_MUSIC.get(p, []):
            searchable = " ".join([
                track.get("title", ""),
                track.get("artist", ""),
                track.get("genre", ""),
                track.get("use_case", ""),
                track.get("trend_name", ""),
            ]).lower()
            if q in searchable:
                results.append({**track, "platform": p})
    return results


def get_music_by_trend(trend_name: str) -> list[dict]:
    """Return music associated with a specific trend name."""
    results = []
    for platform, tracks in _TRENDING_MUSIC.items():
        for track in tracks:
            if trend_name.lower() in track.get("trend_name", "").lower():
                results.append({**track, "platform": platform})
    return results


def music_by_use_case(use_case: str, platform: str = "all") -> list[dict]:
    """Find music that fits a specific content use case."""
    q = use_case.lower()
    platforms = list(_TRENDING_MUSIC.keys()) if platform == "all" else [platform]
    results = []
    for p in platforms:
        for track in _TRENDING_MUSIC.get(p, []):
            if q in track.get("use_case", "").lower():
                results.append({**track, "platform": p})
    return results


def list_genres(platform: str = "all") -> list[str]:
    """List available genres in the music database."""
    platforms = list(_TRENDING_MUSIC.keys()) if platform == "all" else [platform]
    genres: set[str] = set()
    for p in platforms:
        for track in _TRENDING_MUSIC.get(p, []):
            genres.add(track.get("genre", "Unknown"))
    return sorted(genres)
