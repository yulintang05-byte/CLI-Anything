"""Viral music tracker — identifies trending audio across TikTok and YouTube Shorts."""

from collections import Counter
from datetime import datetime, timezone
from typing import Optional


# Curated viral tracks database (updated periodically)
VIRAL_TRACKS_DB: list[dict] = [
    {"title": "Espresso", "artist": "Sabrina Carpenter", "platforms": ["tiktok", "youtube", "instagram"], "genre": "pop", "bpm": 104, "mood": "upbeat", "viral_use": "transition, dance, aesthetic", "tiktok_uses": 15_000_000},
    {"title": "APT.", "artist": "ROSÉ & Bruno Mars", "platforms": ["tiktok", "youtube"], "genre": "pop", "bpm": 120, "mood": "playful", "viral_use": "couple content, dance, challenge", "tiktok_uses": 12_000_000},
    {"title": "Die With A Smile", "artist": "Lady Gaga & Bruno Mars", "platforms": ["tiktok", "youtube", "instagram"], "genre": "pop ballad", "bpm": 76, "mood": "emotional", "viral_use": "storytelling, emotional, couples", "tiktok_uses": 9_500_000},
    {"title": "BIRDS OF A FEATHER", "artist": "Billie Eilish", "platforms": ["tiktok", "youtube"], "genre": "indie pop", "bpm": 105, "mood": "dreamy", "viral_use": "aesthetic, slow-mo, nature content", "tiktok_uses": 8_200_000},
    {"title": "Good Luck, Babe!", "artist": "Chappell Roan", "platforms": ["tiktok", "youtube"], "genre": "synth pop", "bpm": 132, "mood": "dramatic", "viral_use": "reaction, drama, storytelling", "tiktok_uses": 7_800_000},
    {"title": "Too Sweet", "artist": "Hozier", "platforms": ["tiktok", "youtube", "instagram"], "genre": "indie folk", "bpm": 82, "mood": "romantic", "viral_use": "food content, aesthetic, slow-mo", "tiktok_uses": 6_900_000},
    {"title": "Please Please Please", "artist": "Sabrina Carpenter", "platforms": ["tiktok", "youtube"], "genre": "pop", "bpm": 95, "mood": "fun", "viral_use": "comedy, couples, relatable", "tiktok_uses": 6_400_000},
    {"title": "Levii's Jeans", "artist": "Beyoncé ft. Post Malone", "platforms": ["tiktok", "youtube"], "genre": "country pop", "bpm": 118, "mood": "confident", "viral_use": "fashion, GRWM, confidence", "tiktok_uses": 5_800_000},
    {"title": "Luther", "artist": "Kendrick Lamar & SZA", "platforms": ["tiktok", "youtube"], "genre": "hip-hop", "bpm": 88, "mood": "smooth", "viral_use": "aesthetic, couple, vibes", "tiktok_uses": 11_200_000},
    {"title": "Not Like Us", "artist": "Kendrick Lamar", "platforms": ["tiktok", "youtube"], "genre": "hip-hop", "bpm": 97, "mood": "aggressive", "viral_use": "hype, reaction, POV", "tiktok_uses": 14_500_000},
    {"title": "Timeless", "artist": "The Weeknd & Playboi Carti", "platforms": ["tiktok", "youtube"], "genre": "r&b", "bpm": 115, "mood": "dark", "viral_use": "aesthetic, dark content, moody", "tiktok_uses": 5_200_000},
    {"title": "Lovin On Me", "artist": "Jack Harlow", "platforms": ["tiktok", "youtube", "instagram"], "genre": "hip-hop", "bpm": 103, "mood": "chill", "viral_use": "dance, summer, comedy", "tiktok_uses": 4_900_000},
    {"title": "Beautiful Things", "artist": "Benson Boone", "platforms": ["tiktok", "youtube", "instagram"], "genre": "pop rock", "bpm": 126, "mood": "emotional uplifting", "viral_use": "emotional, wedding, milestone", "tiktok_uses": 8_700_000},
    {"title": "Supernatural", "artist": "NewJeans", "platforms": ["tiktok", "youtube"], "genre": "k-pop", "bpm": 120, "mood": "cute", "viral_use": "dance, kpop, girl content", "tiktok_uses": 4_200_000},
    {"title": "Harleys In Hawaii (Slowed)", "artist": "Katy Perry (slowed remix)", "platforms": ["tiktok"], "genre": "pop slowed", "bpm": 75, "mood": "dreamy aesthetic", "viral_use": "travel, aesthetic, slow-mo", "tiktok_uses": 3_800_000},
]

# Genre mood mapping for content type recommendations
MOOD_TO_CONTENT: dict[str, list[str]] = {
    "upbeat": ["transition videos", "GRWM", "day-in-my-life", "workout", "unboxing"],
    "emotional": ["storytelling", "couple content", "milestone", "heartfelt message"],
    "dreamy": ["aesthetic shots", "slow-mo", "nature", "travel", "room tour"],
    "playful": ["comedy skits", "challenge", "couple content", "dance"],
    "dramatic": ["POV content", "reaction", "plot twist reveals", "storytime"],
    "romantic": ["couple content", "aesthetic", "date night", "anniversary"],
    "confident": ["fashion OOTD", "glow-up", "boss energy", "luxury content"],
    "aggressive": ["hype content", "motivation", "gym clips", "transformation"],
    "chill": ["lifestyle vlog", "study with me", "lo-fi", "daily routine"],
    "smooth": ["aesthetic", "night-out", "vibes", "luxury"],
    "dark": ["moody aesthetic", "dark academia", "night content", "mysterious"],
    "cute": ["pet content", "K-pop inspired", "wholesome", "soft girl"],
    "fun": ["comedy", "trend participation", "POV", "collab"],
    "dark aesthetic": ["urban photography", "moody edits", "film grain aesthetic"],
    "dreamy aesthetic": ["golden hour", "cottagecore", "film photography", "travel"],
    "emotional uplifting": ["milestone posts", "before-after", "comeback story", "gratitude"],
}


def get_trending_music(
    platform: str = "all",
    genre: Optional[str] = None,
    mood: Optional[str] = None,
    limit: int = 10,
    from_scraped_data: Optional[list[dict]] = None,
) -> dict:
    """
    Return trending music tracks filtered by platform, genre, or mood.

    If from_scraped_data is provided, extracts and ranks music from live scrape results.
    Otherwise uses the curated database.
    """
    if from_scraped_data:
        return _analyze_scraped_music(from_scraped_data, platform, limit)

    tracks = VIRAL_TRACKS_DB.copy()

    if platform != "all":
        tracks = [t for t in tracks if platform.lower() in t.get("platforms", [])]

    if genre:
        tracks = [t for t in tracks if genre.lower() in t.get("genre", "").lower()]

    if mood:
        tracks = [t for t in tracks if mood.lower() in t.get("mood", "").lower()]

    tracks.sort(key=lambda x: x.get("tiktok_uses", 0), reverse=True)
    tracks = tracks[:limit]

    for track in tracks:
        track["content_ideas"] = MOOD_TO_CONTENT.get(track.get("mood", ""), ["general content"])

    return {
        "platform": platform,
        "genre_filter": genre,
        "mood_filter": mood,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "total": len(tracks),
        "tracks": tracks,
        "usage_tips": _music_usage_tips(platform),
    }


def _analyze_scraped_music(videos: list[dict], platform: str, limit: int) -> dict:
    """Extract and rank music from scraped video data."""
    music_counter: Counter = Counter()
    music_details: dict[str, dict] = {}

    for v in videos:
        title = v.get("music_title", "").strip()
        author = v.get("music_author", "").strip()
        if title:
            key = f"{title} — {author}" if author else title
            music_counter[key] += 1
            if key not in music_details:
                music_details[key] = {
                    "title": title,
                    "artist": author,
                    "track_key": key,
                    "video_count": 0,
                    "total_plays": 0,
                }
            music_details[key]["video_count"] += 1
            music_details[key]["total_plays"] += v.get("play_count", 0)

    ranked = sorted(
        music_details.values(),
        key=lambda x: x["total_plays"],
        reverse=True,
    )[:limit]

    for track in ranked:
        best_match = _match_db_track(track["title"])
        if best_match:
            track["bpm"] = best_match.get("bpm")
            track["mood"] = best_match.get("mood")
            track["content_ideas"] = MOOD_TO_CONTENT.get(best_match.get("mood", ""), [])

    return {
        "platform": platform,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": "live-scrape",
        "total": len(ranked),
        "tracks": ranked,
        "usage_tips": _music_usage_tips(platform),
    }


def _match_db_track(title: str) -> Optional[dict]:
    """Fuzzy match a track title against the curated database."""
    title_lower = title.lower()
    for track in VIRAL_TRACKS_DB:
        if track["title"].lower() in title_lower or title_lower in track["title"].lower():
            return track
    return None


def recommend_music_for_niche(niche: str) -> dict:
    """Recommend the best trending music for a specific content niche."""
    niche_to_moods: dict[str, list[str]] = {
        "motivation": ["upbeat", "confident", "aggressive"],
        "fitness": ["upbeat", "aggressive", "confident"],
        "luxury": ["smooth", "confident", "dark"],
        "aesthetic": ["dreamy", "chill", "dark aesthetic"],
        "food": ["upbeat", "fun", "playful"],
        "fashion": ["upbeat", "confident", "playful"],
        "finance": ["confident", "upbeat", "chill"],
        "travel": ["dreamy", "upbeat", "emotional uplifting"],
        "pets": ["cute", "playful", "fun"],
        "gaming": ["aggressive", "upbeat", "dramatic"],
        "beauty": ["upbeat", "playful", "fun"],
        "themepage": ["dreamy", "emotional", "upbeat"],
        "couples": ["romantic", "emotional", "playful"],
        "comedy": ["fun", "playful", "upbeat"],
    }

    target_moods = niche_to_moods.get(niche.lower(), ["upbeat", "chill"])
    recommended = []
    for mood in target_moods:
        matches = [t for t in VIRAL_TRACKS_DB if mood in t.get("mood", "")]
        for m in matches:
            if m not in recommended:
                m = dict(m)
                m["recommended_for_mood"] = mood
                m["content_ideas"] = MOOD_TO_CONTENT.get(mood, [])
                recommended.append(m)

    recommended.sort(key=lambda x: x.get("tiktok_uses", 0), reverse=True)

    return {
        "niche": niche,
        "target_moods": target_moods,
        "recommended_tracks": recommended[:8],
        "pro_tip": (
            f"For '{niche}' content: lead with the drop/hook of the song in the first 0-2 seconds. "
            "TikTok's algorithm rewards videos that keep viewers past the 3-second mark — "
            "syncing your most dramatic visual to the song's beat drop maximizes this."
        ),
    }


def _music_usage_tips(platform: str) -> list[str]:
    tips = {
        "tiktok": [
            "Use the trending sound version, not a cover — TikTok boosts videos on the original sound's trend page.",
            "Add the song in the first 0.5 seconds — videos with audio from frame 1 get higher initial push.",
            "Sync key visual moments to the beat for 20-40% higher completion rates.",
            "Trending sounds change fast — check TikTok Creative Center weekly for the current top 100.",
            "Using a sound with 500k-2M uses (not 10M+) puts you in less competitive discovery.",
            "Original audio you create can become viral — watermark it with your handle.",
        ],
        "youtube": [
            "YouTube Shorts follows TikTok trends by ~1-2 weeks — use sounds that just peaked on TikTok.",
            "Use royalty-free music from YouTube Audio Library to avoid monetization conflicts.",
            "Songs in the public domain (pre-1928) can be used freely for long-form content.",
            "Background music at 10-20% volume with voiceover performs best for educational content.",
            "YouTube Music's Charts page shows what's trending in your country — cross-reference weekly.",
        ],
        "instagram": [
            "Instagram Reels uses the same trending audio system as TikTok — look for the arrow icon.",
            "Music from Instagram's official library avoids copyright restrictions on non-US audiences.",
            "Stories with music stickers get 15% higher reply rates than silent stories.",
            "Reels with trending audio get distributed to explore — check the audio's page for view counts.",
        ],
        "all": [
            "Cross-platform: a sound trending on TikTok this week will peak on Instagram Reels next week.",
            "Keep a swipe file of trending sounds — save them to drafts immediately before they expire.",
            "Instrumental or lyric-free tracks work best for voiceover educational content on all platforms.",
        ],
    }
    return tips.get(platform.lower(), tips["tiktok"])
