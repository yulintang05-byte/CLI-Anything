"""Viral music tracker — trending sounds on TikTok and YouTube."""

import re
import json
import urllib.request
import urllib.parse
from typing import Optional


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _http_get(url: str, headers: Optional[dict] = None, timeout: int = 15) -> str:
    req_headers = dict(_HEADERS)
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


# ── TikTok sounds from trending videos ───────────────────────────


def extract_music_from_tiktok_videos(videos: list[dict]) -> list[dict]:
    """Aggregate and rank music/sounds from a TikTok video list."""
    music_counts: dict[str, dict] = {}
    for v in videos:
        music = v.get("music", {})
        if not music:
            continue
        music_id = str(music.get("id", ""))
        if not music_id:
            continue
        if music_id not in music_counts:
            music_counts[music_id] = {
                "id": music_id,
                "title": music.get("title", "Unknown"),
                "artist": music.get("authorName", "Unknown"),
                "duration": music.get("duration", 0),
                "cover": music.get("coverThumb", ""),
                "url": f"https://www.tiktok.com/music/{music_id}",
                "video_count": 0,
            }
        music_counts[music_id]["video_count"] += 1

    ranked = sorted(music_counts.values(), key=lambda x: x["video_count"], reverse=True)
    return ranked


# ── YouTube Music chart scrape ────────────────────────────────────


def fetch_youtube_music_trending(region: str = "US", max_results: int = 20) -> list[dict]:
    """Fetch trending music from YouTube Music charts."""
    url = f"https://charts.youtube.com/charts/TopSongs/{region}/weekly"
    try:
        html = _http_get(url, headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch YouTube Music charts: {exc}") from exc

    # Try to parse structured data from the page
    tracks = _parse_yt_music_chart(html, max_results)
    return tracks


def _parse_yt_music_chart(html: str, max_results: int) -> list[dict]:
    """Parse track listings from YouTube Music charts page."""
    # Look for JSON-LD or embedded data
    match = re.search(r"<script[^>]+type=['\"]application/json['\"][^>]*>(.+?)</script>", html, re.DOTALL)
    if not match:
        return []
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return []

    tracks = []
    _walk_for_tracks(data, tracks, max_results)
    return tracks[:max_results]


def _walk_for_tracks(node, tracks: list, max_results: int):
    if len(tracks) >= max_results:
        return
    if isinstance(node, dict):
        if "videoDetails" in node or ("videoId" in node and "title" in node):
            vid_id = node.get("videoId", "")
            title = node.get("title", "") or (node.get("videoDetails", {}) or {}).get("title", "")
            artist = node.get("author", "") or (node.get("videoDetails", {}) or {}).get("author", "")
            if vid_id and title:
                tracks.append({
                    "video_id": vid_id,
                    "title": title,
                    "artist": artist,
                    "url": f"https://www.youtube.com/watch?v={vid_id}",
                    "chart": "YouTube Weekly Top Songs",
                })
                return
        for v in node.values():
            _walk_for_tracks(v, tracks, max_results)
    elif isinstance(node, list):
        for item in node:
            _walk_for_tracks(item, tracks, max_results)


# ── Cross-platform sound strategy ────────────────────────────────


MUSIC_STRATEGY_GUIDE = {
    "tiktok": {
        "best_practice": (
            "Use sounds that are trending in the last 7 days for maximum algorithm boost. "
            "TikTok actively promotes videos using trending sounds — check the 'Trending' "
            "tab in the sounds library before posting."
        ),
        "timing": "Post within 24–48 hours of a sound going viral for best visibility.",
        "niche_tip": "Search your niche + 'sound' to find community-specific viral audio.",
        "original_audio": (
            "Original audio can also go viral — use a memorable hook in the first 0–3 seconds. "
            "Name your sound with a keyword so others can find and use it."
        ),
    },
    "youtube_shorts": {
        "best_practice": (
            "YouTube Shorts heavily promotes videos using songs from YouTube Music catalog. "
            "Use 'Create' mode in Shorts to pick from trending tracks."
        ),
        "timing": "Remix trending sounds within the same week they appear in Shorts feed.",
        "niche_tip": "Use instrumental versions of trending songs to avoid copyright strikes.",
        "original_audio": "YouTube pays creators for original Shorts audio via the Partner Program.",
    },
    "instagram_reels": {
        "best_practice": (
            "Instagram surfaces Reels with Reels-featured music. Use the Instagram music "
            "library and check 'Trending' badge next to tracks."
        ),
        "timing": "Match music to your visual rhythm — hook viewers in first 3 seconds.",
        "niche_tip": "Trending songs on TikTok typically reach Instagram 1–2 weeks later.",
        "original_audio": "Use original audio with a strong hook; Instagram can suggest it to others.",
    },
}


def get_music_strategy(platform: str) -> dict:
    return MUSIC_STRATEGY_GUIDE.get(platform.lower(), {
        "error": f"Unknown platform '{platform}'. Choose: tiktok, youtube_shorts, instagram_reels"
    })


def suggest_sounds_for_niche(niche: str) -> list[dict]:
    """Return curated sound style suggestions for a niche (no live data required)."""
    suggestions = {
        "fitness": [
            {"style": "High-energy EDM / pump-up beats", "example_genre": "EDM, Hip-Hop"},
            {"style": "Motivational speech overlay", "example_genre": "Spoken word + beats"},
            {"style": "Trending pop with fast tempo (130+ BPM)", "example_genre": "Pop"},
        ],
        "beauty": [
            {"style": "Soft pop / indie vibes", "example_genre": "Indie Pop"},
            {"style": "Trending viral audio (e.g. 'Get Ready With Me' sounds)", "example_genre": "Pop"},
            {"style": "Lo-fi beats for calm tutorials", "example_genre": "Lo-fi"},
        ],
        "food": [
            {"style": "Upbeat cooking sounds + light music", "example_genre": "Acoustic"},
            {"style": "Satisfying ASMR-adjacent audio", "example_genre": "Ambient"},
            {"style": "Trending viral sounds from food creators", "example_genre": "Various"},
        ],
        "finance": [
            {"style": "Corporate / lo-fi beats", "example_genre": "Lo-fi, Ambient"},
            {"style": "Motivational speech + background music", "example_genre": "Spoken word"},
            {"style": "Trending informational sounds", "example_genre": "Trending audio"},
        ],
        "motivation": [
            {"style": "Epic orchestral / cinematic", "example_genre": "Orchestral"},
            {"style": "Hip-hop beats with motivational samples", "example_genre": "Hip-Hop"},
            {"style": "Speech clips from known figures + music overlay", "example_genre": "Various"},
        ],
        "travel": [
            {"style": "Cinematic ambient soundscapes", "example_genre": "Ambient / Cinematic"},
            {"style": "Local/regional music matching destination", "example_genre": "World Music"},
            {"style": "Upbeat indie / folk for adventure feel", "example_genre": "Indie Folk"},
        ],
    }
    result = suggestions.get(niche.lower())
    if not result:
        return [{"style": "Trending audio in your niche", "example_genre": "Various — check TikTok Discover"}]
    return result
