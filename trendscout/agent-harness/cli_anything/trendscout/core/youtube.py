"""TrendScout – YouTube trending scraper.

Fetches trending videos, hashtags, and music from YouTube using yt-dlp
(no API key required) and the public YouTube RSS trending feed.
"""

import json
import subprocess
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone


# YouTube category IDs for trending
_CATEGORY_IDS = {
    "all": "0",
    "music": "10",
    "gaming": "20",
    "film": "1",
    "entertainment": "24",
    "news": "25",
    "beauty": "26",
    "sports": "17",
    "science": "28",
    "tech": "28",
}

_REGION_CODES = {
    "us": "US", "uk": "GB", "ca": "CA", "au": "AU",
    "in": "IN", "br": "BR", "de": "DE", "fr": "FR",
    "jp": "JP", "kr": "KR", "mx": "MX", "id": "ID",
}

# Trending RSS feed (public, no key needed)
_RSS_BASE = "https://www.youtube.com/feeds/videos.xml?hl=en_US"


def _run_ytdlp(args: List[str], timeout: int = 30) -> Dict[str, Any]:
    """Run yt-dlp and return parsed JSON output."""
    try:
        result = subprocess.run(
            ["yt-dlp"] + args,
            capture_output=True, text=True, timeout=timeout,
        )
        if result.returncode != 0:
            raise RuntimeError(f"yt-dlp error: {result.stderr.strip()[:400]}")
        return json.loads(result.stdout)
    except FileNotFoundError:
        raise RuntimeError(
            "yt-dlp not found. Install with: pip install yt-dlp"
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("yt-dlp timed out. Try again or reduce --limit.")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse yt-dlp output: {e}")


def _fetch_url(url: str, timeout: int = 15) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch_trending(
    category: str = "all",
    region: str = "us",
    limit: int = 20,
) -> Dict[str, Any]:
    """Fetch YouTube trending videos via yt-dlp.

    Returns video list with titles, channels, view counts, hashtags.
    """
    cat = category.lower()
    reg = _REGION_CODES.get(region.lower(), region.upper())
    cat_id = _CATEGORY_IDS.get(cat, "0")

    url = f"https://www.youtube.com/feed/trending?bp=Q{cat_id}IARBQ%3D%3D&gl={reg}"

    try:
        data = _run_ytdlp([
            "--flat-playlist",
            "--playlist-end", str(limit),
            "--dump-single-json",
            "--quiet",
            url,
        ])

        videos = []
        for entry in data.get("entries", [])[:limit]:
            vid: Dict[str, Any] = {
                "id": entry.get("id", ""),
                "title": entry.get("title", ""),
                "channel": entry.get("channel", entry.get("uploader", "")),
                "duration": entry.get("duration"),
                "view_count": entry.get("view_count"),
                "like_count": entry.get("like_count"),
                "thumbnail": entry.get("thumbnail", ""),
                "url": f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                "upload_date": entry.get("upload_date", ""),
                "hashtags": _extract_hashtags(entry.get("description", "") or entry.get("title", "")),
            }
            videos.append(vid)

        return {
            "source": "youtube",
            "category": cat,
            "region": reg,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "count": len(videos),
            "videos": videos,
        }

    except RuntimeError as exc:
        # Graceful fallback with demo data when yt-dlp unavailable
        return _demo_trending(cat, reg, limit, str(exc))


def fetch_trending_music(region: str = "us", limit: int = 20) -> Dict[str, Any]:
    """Fetch YouTube Music trending via yt-dlp (charts playlist)."""
    reg = _REGION_CODES.get(region.lower(), region.upper())

    # YouTube Music charts playlist URL
    url = f"https://music.youtube.com/playlist?list=PLFgquLnL59alCl_2TQvOiD5Vgm1hCaGSI"

    try:
        data = _run_ytdlp([
            "--flat-playlist",
            "--playlist-end", str(limit),
            "--dump-single-json",
            "--quiet",
            url,
        ])

        tracks = []
        for entry in data.get("entries", [])[:limit]:
            track: Dict[str, Any] = {
                "id": entry.get("id", ""),
                "title": entry.get("title", ""),
                "artist": entry.get("channel", entry.get("uploader", "")),
                "duration": entry.get("duration"),
                "url": f"https://music.youtube.com/watch?v={entry.get('id', '')}",
                "thumbnail": entry.get("thumbnail", ""),
            }
            tracks.append(track)

        return {
            "source": "youtube_music",
            "region": reg,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "count": len(tracks),
            "tracks": tracks,
        }

    except RuntimeError as exc:
        return _demo_music(reg, limit, str(exc))


def extract_hashtags_from_video(video_url: str) -> Dict[str, Any]:
    """Extract hashtags from a specific YouTube video's description."""
    try:
        data = _run_ytdlp([
            "--dump-single-json",
            "--quiet",
            video_url,
        ])

        desc = data.get("description", "")
        tags = data.get("tags", [])
        title_hashtags = _extract_hashtags(data.get("title", ""))
        desc_hashtags = _extract_hashtags(desc)

        all_hashtags = list(dict.fromkeys(title_hashtags + desc_hashtags + [f"#{t}" for t in tags]))

        return {
            "video_id": data.get("id", ""),
            "title": data.get("title", ""),
            "channel": data.get("channel", ""),
            "view_count": data.get("view_count"),
            "hashtags": all_hashtags,
            "tags": tags,
        }

    except RuntimeError as exc:
        raise RuntimeError(f"Could not fetch video hashtags: {exc}")


def aggregate_trending_hashtags(
    category: str = "all",
    region: str = "us",
    limit: int = 50,
) -> Dict[str, Any]:
    """Aggregate hashtag frequency across trending videos."""
    trending = fetch_trending(category=category, region=region, limit=limit)

    freq: Dict[str, int] = {}
    for video in trending.get("videos", []):
        for tag in video.get("hashtags", []):
            tag_lower = tag.lower()
            freq[tag_lower] = freq.get(tag_lower, 0) + 1

    sorted_tags = sorted(freq.items(), key=lambda x: x[1], reverse=True)

    return {
        "source": "youtube",
        "category": category,
        "region": region,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "total_videos_analyzed": len(trending.get("videos", [])),
        "top_hashtags": [
            {"hashtag": tag, "frequency": count}
            for tag, count in sorted_tags[:30]
        ],
    }


def _extract_hashtags(text: str) -> List[str]:
    """Pull #hashtags out of a string."""
    import re
    return re.findall(r"#\w+", text)


# ── Demo / offline fallback ───────────────────────────────────────────────────

def _demo_trending(cat: str, reg: str, limit: int, error: str) -> Dict[str, Any]:
    """Return curated demo data when yt-dlp is unavailable."""
    DEMO_VIDEOS = [
        {"id": "dQw4w9WgXcQ", "title": "Never Gonna Give You Up", "channel": "Rick Astley", "view_count": 1400000000, "hashtags": ["#rickroll", "#classic", "#viral"]},
        {"id": "kJQP7kiw5Fk", "title": "Despacito", "channel": "Luis Fonsi", "view_count": 8200000000, "hashtags": ["#despacito", "#latin", "#music"]},
        {"id": "JGwWNGJdvx8", "title": "Shape of You", "channel": "Ed Sheeran", "view_count": 5900000000, "hashtags": ["#edsheeran", "#pop", "#music"]},
        {"id": "9bZkp7q19f0", "title": "GANGNAM STYLE", "channel": "PSY", "view_count": 4900000000, "hashtags": ["#gangnamstyle", "#kpop", "#viral"]},
        {"id": "RgKAFK5djSk", "title": "Wiz Khalifa – See You Again", "channel": "Wiz Khalifa", "view_count": 5800000000, "hashtags": ["#seeyouagain", "#tribute", "#music"]},
        {"id": "hT_nvWreIhg", "title": "Count on Me", "channel": "Bruno Mars", "view_count": 1200000000, "hashtags": ["#brunomars", "#pop", "#friendship"]},
        {"id": "OPf0YbXqDm0", "title": "Mark Ronson – Uptown Funk", "channel": "Mark Ronson ft. Bruno Mars", "view_count": 4500000000, "hashtags": ["#uptownfunk", "#dance", "#viral"]},
        {"id": "bo_efYLyMFc", "title": "Baby Shark Dance", "channel": "Pinkfong", "view_count": 13500000000, "hashtags": ["#babyshark", "#kids", "#viral"]},
        {"id": "lp-EO5I60KA", "title": "YouTube Rewind 2019", "channel": "YouTube", "view_count": 220000000, "hashtags": ["#youtuberewind", "#trending"]},
        {"id": "0yW7b8evMpI", "title": "Minecraft Survival Let's Play", "channel": "DreamWasTaken", "view_count": 45000000, "hashtags": ["#minecraft", "#gaming", "#survival"]},
    ]
    videos = [
        {**v, "url": f"https://www.youtube.com/watch?v={v['id']}", "thumbnail": f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg", "duration": 240, "like_count": None, "upload_date": "20240101"}
        for v in DEMO_VIDEOS[:limit]
    ]
    return {
        "source": "youtube",
        "category": cat,
        "region": reg,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "count": len(videos),
        "videos": videos,
        "demo_mode": True,
        "note": f"Demo data — yt-dlp unavailable: {error[:120]}",
    }


def _demo_music(reg: str, limit: int, error: str) -> Dict[str, Any]:
    DEMO_TRACKS = [
        {"id": "JGwWNGJdvx8", "title": "Shape of You", "artist": "Ed Sheeran", "duration": 234},
        {"id": "kJQP7kiw5Fk", "title": "Despacito", "artist": "Luis Fonsi ft. Daddy Yankee", "duration": 229},
        {"id": "OPf0YbXqDm0", "title": "Uptown Funk", "artist": "Mark Ronson ft. Bruno Mars", "duration": 270},
        {"id": "RgKAFK5djSk", "title": "See You Again", "artist": "Wiz Khalifa ft. Charlie Puth", "duration": 229},
        {"id": "dQw4w9WgXcQ", "title": "Never Gonna Give You Up", "artist": "Rick Astley", "duration": 213},
        {"id": "hT_nvWreIhg", "title": "Count on Me", "artist": "Bruno Mars", "duration": 176},
        {"id": "9bZkp7q19f0", "title": "GANGNAM STYLE", "artist": "PSY", "duration": 252},
        {"id": "GRxofEmo3HA", "title": "Perfect", "artist": "Ed Sheeran", "duration": 263},
        {"id": "1G4isv_Fylg", "title": "Stay With Me", "artist": "Sam Smith", "duration": 172},
        {"id": "rutjZhBSG8A", "title": "Sunflower", "artist": "Post Malone", "duration": 158},
    ]
    tracks = [
        {**t, "url": f"https://music.youtube.com/watch?v={t['id']}", "thumbnail": f"https://i.ytimg.com/vi/{t['id']}/hqdefault.jpg"}
        for t in DEMO_TRACKS[:limit]
    ]
    return {
        "source": "youtube_music",
        "region": reg,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "count": len(tracks),
        "tracks": tracks,
        "demo_mode": True,
        "note": f"Demo data — yt-dlp unavailable: {error[:120]}",
    }
