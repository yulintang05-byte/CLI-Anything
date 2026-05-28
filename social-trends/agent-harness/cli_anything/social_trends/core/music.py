"""Trending music and sound discovery.

Aggregates trending audio signals from TikTok and YouTube, with genre
classification and usage trend analysis. No API keys required for basic use.
"""

from typing import Any

from cli_anything.social_trends.utils.social_backend import cache_get, cache_set
from cli_anything.social_trends.core import tiktok as tt


def get_trending_sounds(platform: str = "tiktok", region: str = "US",
                        max_results: int = 20) -> list[dict]:
    """Fetch trending sounds/music for the given platform.

    Args:
        platform: 'tiktok', 'youtube', or 'all'.
        region: Region code (e.g., 'US').
        max_results: Max sounds to return.

    Returns:
        List of {title, artist, platform, video_count, genre, mood}.
    """
    if platform == "tiktok":
        sounds = tt.get_trending_sounds_web(region, max_results)
        return [_enrich_sound(s, "tiktok") for s in sounds]

    elif platform == "youtube":
        return _youtube_trending_music(region, max_results)

    else:  # all
        tt_sounds = tt.get_trending_sounds_web(region, max_results // 2)
        yt_sounds = _youtube_trending_music(region, max_results // 2)
        combined = [_enrich_sound(s, "tiktok") for s in tt_sounds] + yt_sounds
        combined.sort(key=lambda x: x.get("video_count", 0), reverse=True)
        return combined[:max_results]


def _enrich_sound(sound: dict, platform: str) -> dict:
    """Add genre and mood classification to a sound dict."""
    title = sound.get("title", "").lower()
    artist = sound.get("artist", "").lower()

    genre = _classify_genre(title, artist)
    mood = _classify_mood(title)

    return {
        **sound,
        "platform": platform,
        "genre": genre,
        "mood": mood,
        "use_case": _suggest_use_case(genre, mood),
    }


def _classify_genre(title: str, artist: str) -> str:
    """Classify a song into a genre bucket based on title/artist signals."""
    text = f"{title} {artist}"
    genre_keywords = {
        "hip-hop": ["rap", "hip hop", "trap", "drill", "freestyle", "bars", "kendrick", "drake", "travis"],
        "pop": ["pop", "sabrina", "taylor", "ariana", "billie", "dua", "olivia", "chappell"],
        "r&b": ["r&b", "soul", "sza", "bryson", "frank ocean", "the weeknd", "usher"],
        "edm": ["edm", "house", "techno", "electronic", "remix", "dj", "drop", "bass"],
        "indie": ["indie", "alternative", "hozier", "mitski", "phoebe", "sufjan"],
        "latin": ["latin", "reggaeton", "bad bunny", "karol g", "j balvin", "maluma"],
        "country": ["country", "morgan wallen", "luke combs", "zach bryan"],
        "k-pop": ["kpop", "k-pop", "bts", "blackpink", "rosé", "newjeans", "aespa"],
    }
    for genre, keywords in genre_keywords.items():
        if any(kw in text for kw in keywords):
            return genre
    return "other"


def _classify_mood(title: str) -> str:
    """Classify the mood/energy of a track."""
    title_lower = title.lower()
    moods = {
        "hype": ["banger", "hard", "energy", "fire", "heat", "loud"],
        "emotional": ["sad", "cry", "heart", "love", "miss", "pain", "sorry"],
        "chill": ["chill", "slow", "soft", "gentle", "smooth", "mellow"],
        "party": ["party", "dance", "move", "groove", "club", "night"],
        "motivational": ["rise", "strong", "power", "fight", "win", "hustle"],
    }
    for mood, keywords in moods.items():
        if any(kw in title_lower for kw in keywords):
            return mood
    return "neutral"


def _suggest_use_case(genre: str, mood: str) -> str:
    """Suggest content types that work well with this sound."""
    use_cases = {
        ("hip-hop", "hype"): "transformation videos, gym content, attitude clips",
        ("hip-hop", "motivational"): "hustle content, entrepreneur reels, success stories",
        ("pop", "emotional"): "story time, vulnerable content, relatable moments",
        ("pop", "party"): "GRWM, fashion, lifestyle, fun content",
        ("r&b", "chill"): "aesthetic content, vlog, day-in-my-life, cooking",
        ("edm", "hype"): "travel montage, sports, workout, highlight reels",
        ("indie", "chill"): "art, photography, cozy content, journaling",
        ("latin", "party"): "dance, beach, food, culture content",
        ("k-pop", "hype"): "dance covers, fashion, makeup, beauty tutorials",
    }
    return use_cases.get((genre, mood), "versatile — works with most content types")


def _youtube_trending_music(region: str, max_results: int) -> list[dict]:
    """Get trending music from YouTube's music category."""
    cache_key = f"yt_music_{region}"
    cached = cache_get(cache_key)
    if cached:
        return cached[:max_results]

    from cli_anything.social_trends.utils.social_backend import load_config
    from cli_anything.social_trends.core import youtube as yt

    config = load_config()
    try:
        if config.get("youtube_api_key"):
            videos = yt.get_trending_api(region, category="10", max_results=max_results)
        else:
            videos = yt.get_trending_ytdlp(region, max_results)
            videos = [v for v in videos if any(
                kw in v.get("title", "").lower()
                for kw in ("official", "music", "audio", "lyrics", "mv")
            )]

        result = []
        for v in videos[:max_results]:
            result.append({
                "sound_id": v.get("id", ""),
                "title": v.get("title", ""),
                "artist": v.get("channel", ""),
                "video_count": 1,
                "avg_views": v.get("views", 0),
                "youtube_url": v.get("url", ""),
                "platform": "youtube",
                "genre": _classify_genre(v.get("title", ""), v.get("channel", "")),
                "mood": _classify_mood(v.get("title", "")),
                "use_case": "",
                "source": v.get("source", ""),
            })

        if result:
            cache_set(cache_key, result)
        return result
    except Exception:
        return []


def get_sound_strategy(niche: str) -> dict:
    """Get recommended sound/music strategy for a content niche.

    Args:
        niche: Content niche (e.g., 'fitness', 'cooking', 'motivation').

    Returns:
        Dict with {niche, recommended_genres, moods, posting_tip, audio_tips}.
    """
    strategies = {
        "fitness": {
            "recommended_genres": ["hip-hop", "edm", "pop"],
            "moods": ["hype", "motivational"],
            "audio_tips": [
                "Use trending gym/workout tracks — they correlate with FYP boosts",
                "Original sounds with motivational voiceovers get high saves",
                "Fast-paced EDM drops match high-intensity workout cuts",
            ],
        },
        "cooking": {
            "recommended_genres": ["r&b", "pop", "indie"],
            "moods": ["chill", "neutral"],
            "audio_tips": [
                "ASMR cooking sounds (no music) often outperform music-backed videos",
                "Upbeat pop works for recipe reveals and transformations",
                "Lo-fi beats signal 'cozy content' — great for baking and slow recipes",
            ],
        },
        "fashion": {
            "recommended_genres": ["pop", "hip-hop", "r&b"],
            "moods": ["party", "hype"],
            "audio_tips": [
                "Use viral trending sounds first to ride the wave",
                "Attitude-driven hip-hop works for fashion model walks",
                "Transitions synced to beat drops get high replays",
            ],
        },
        "motivation": {
            "recommended_genres": ["hip-hop", "pop"],
            "moods": ["motivational", "hype"],
            "audio_tips": [
                "Voiceovers over instrumental beats outperform music-only",
                "Use film dialogue clips + chill beats for inspirational quotes",
                "Build your own original audio — branded sounds get reshared",
            ],
        },
        "gaming": {
            "recommended_genres": ["edm", "hip-hop"],
            "moods": ["hype", "party"],
            "audio_tips": [
                "No-copyright game soundtracks avoid Content ID strikes",
                "Lo-fi hip-hop for chill gaming montages",
                "Sync gameplay highlights to drops in EDM tracks",
            ],
        },
    }

    default = {
        "recommended_genres": ["pop", "hip-hop"],
        "moods": ["neutral", "hype"],
        "audio_tips": [
            "Use currently trending sounds in the first 24-48h of them going viral",
            "Niche-relevant audio outperforms generic trending sounds in the long run",
            "Original sounds and voiceovers build stronger audience connection",
        ],
    }

    strategy = strategies.get(niche.lower(), default)
    strategy["niche"] = niche
    strategy["posting_tip"] = (
        "Sound selection affects distribution. TikTok's algorithm groups "
        "content by sound — using a trending sound puts you in a viral pool."
    )
    return strategy
