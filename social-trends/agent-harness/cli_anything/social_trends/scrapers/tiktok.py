#!/usr/bin/env python3
"""TikTok trend scraper — extracts trending hashtags, sounds, and videos.

Uses yt-dlp for video data and httpx + BeautifulSoup for trending page scraping.
No official API key required for public trending data.
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from typing import Optional


def _ytdlp_available() -> bool:
    try:
        subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--version"],
            capture_output=True, timeout=10
        )
        return True
    except Exception:
        return False


def _httpx_available() -> bool:
    try:
        import httpx  # noqa: F401
        return True
    except ImportError:
        return False


def _bs4_available() -> bool:
    try:
        import bs4  # noqa: F401
        return True
    except ImportError:
        return False


def _normalize_count(raw) -> int:
    if raw is None:
        return 0
    if isinstance(raw, int):
        return raw
    s = str(raw).upper().replace(",", "").replace(" ", "")
    try:
        if s.endswith("K"):
            return int(float(s[:-1]) * 1_000)
        if s.endswith("M"):
            return int(float(s[:-1]) * 1_000_000)
        if s.endswith("B"):
            return int(float(s[:-1]) * 1_000_000_000)
        return int(float(s))
    except ValueError:
        return 0


def _extract_hashtags(text: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"#\w+", text or "")))


# ---------------------------------------------------------------------------
# TikTok trending data via yt-dlp
# ---------------------------------------------------------------------------

def _run_ytdlp_tiktok(args: list[str]) -> dict:
    cmd = [sys.executable, "-m", "yt_dlp", "--no-warnings", "--quiet"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        if result.returncode != 0:
            raise RuntimeError(f"yt-dlp error: {result.stderr.strip()}")
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        raise RuntimeError("yt-dlp timed out after 90s")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Could not parse yt-dlp output: {e}")


def scrape_trending(
    region: str = "US",
    limit: int = 20,
) -> dict:
    """Scrape TikTok trending/discover feed.

    Uses yt-dlp to pull trending TikTok videos with full metadata including
    music, hashtags, author info, and engagement numbers.

    Args:
        region: Country code for localized trends (US, GB, IN, …)
        limit: Max number of videos

    Returns:
        dict with videos, hashtags, sounds/music, and metadata
    """
    if not _ytdlp_available():
        raise RuntimeError("yt-dlp is not installed. Run: pip install yt-dlp")

    url = "https://www.tiktok.com/trending"
    raw = _run_ytdlp_tiktok([
        "--dump-single-json",
        "--flat-playlist",
        f"--playlist-end={limit}",
        "--extractor-args", f"tiktok:webpage_download=true",
        url,
    ])

    entries = raw.get("entries", [])[:limit]
    return _process_tiktok_entries(entries, source="trending", region=region)


def scrape_hashtag(
    hashtag: str,
    limit: int = 20,
) -> dict:
    """Scrape videos for a specific TikTok hashtag/challenge.

    Args:
        hashtag: Tag with or without '#' prefix
        limit: Max number of videos

    Returns:
        dict with videos and engagement stats
    """
    if not _ytdlp_available():
        raise RuntimeError("yt-dlp is not installed. Run: pip install yt-dlp")

    tag = hashtag.lstrip("#")
    url = f"https://www.tiktok.com/tag/{tag}"

    raw = _run_ytdlp_tiktok([
        "--dump-single-json",
        "--flat-playlist",
        f"--playlist-end={limit}",
        url,
    ])

    entries = raw.get("entries", [])[:limit]
    result = _process_tiktok_entries(entries, source=f"hashtag:{hashtag}")
    result["hashtag"] = f"#{tag}"
    result["hashtag_url"] = url
    return result


def scrape_sound(
    sound_url: str,
    limit: int = 20,
) -> dict:
    """Scrape videos using a specific TikTok sound.

    Args:
        sound_url: Full TikTok sound URL
        limit: Max videos to fetch

    Returns:
        dict with video list and sound metadata
    """
    if not _ytdlp_available():
        raise RuntimeError("yt-dlp is not installed. Run: pip install yt-dlp")

    raw = _run_ytdlp_tiktok([
        "--dump-single-json",
        "--flat-playlist",
        f"--playlist-end={limit}",
        sound_url,
    ])

    entries = raw.get("entries", [])[:limit]
    result = _process_tiktok_entries(entries, source="sound")
    result["sound_url"] = sound_url
    return result


def get_trending_hashtags(region: str = "US", limit: int = 30) -> dict:
    """Get trending hashtags by scraping TikTok Discover/Explore page.

    Falls back to known-popular evergreen categories when live scraping
    is rate-limited or unavailable.

    Args:
        region: Country code
        limit: Max hashtags to return

    Returns:
        dict with ranked hashtags
    """
    try:
        if not _httpx_available() or not _bs4_available():
            raise RuntimeError("httpx and beautifulsoup4 required for hashtag scraping")
        return _scrape_trending_hashtags_web(region, limit)
    except Exception as e:
        # Graceful fallback: return seeded popular hashtags with note
        return _fallback_trending_hashtags(region, limit, str(e))


def get_trending_sounds(region: str = "US", limit: int = 20) -> dict:
    """Get trending sounds/music on TikTok.

    Args:
        region: Country code
        limit: Max sounds to return

    Returns:
        dict with ranked sounds including title, artist, video count
    """
    try:
        if not _httpx_available():
            raise RuntimeError("httpx required for sound scraping")
        return _scrape_trending_sounds_api(region, limit)
    except Exception as e:
        return _fallback_trending_sounds(region, limit, str(e))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _process_tiktok_entries(
    entries: list[dict],
    source: str = "unknown",
    region: str = "US",
) -> dict:
    videos = []
    hashtag_counts: dict[str, int] = {}
    hashtag_views: dict[str, int] = {}
    sound_counts: dict[str, dict] = {}

    for entry in entries:
        video_id = entry.get("id", "")
        title = entry.get("title") or entry.get("description", "")
        author = entry.get("uploader") or entry.get("creator", "")
        author_id = entry.get("uploader_id", "")
        views = _normalize_count(entry.get("view_count"))
        likes = _normalize_count(entry.get("like_count"))
        comments = _normalize_count(entry.get("comment_count"))
        shares = _normalize_count(entry.get("repost_count"))
        duration = entry.get("duration", 0)
        timestamp = entry.get("timestamp")
        upload_date = entry.get("upload_date", "")

        hashtags = _extract_hashtags(title)
        for ht in hashtags:
            hashtag_counts[ht] = hashtag_counts.get(ht, 0) + 1
            hashtag_views[ht] = hashtag_views.get(ht, 0) + views

        # Extract sound/music metadata
        sound = _extract_tiktok_sound(entry)
        if sound:
            key = sound.get("sound_id") or sound.get("title", "")
            if key:
                if key not in sound_counts:
                    sound_counts[key] = {**sound, "video_count": 0, "total_views": 0}
                sound_counts[key]["video_count"] += 1
                sound_counts[key]["total_views"] += views

        # Engagement rate calculation
        engagement_rate = 0.0
        if views > 0:
            engagement_rate = round((likes + comments + shares) / views * 100, 2)

        videos.append({
            "rank": len(videos) + 1,
            "video_id": video_id,
            "url": entry.get("webpage_url") or f"https://www.tiktok.com/@{author_id}/video/{video_id}",
            "title": title,
            "author": author,
            "author_id": author_id,
            "views": views,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "engagement_rate_pct": engagement_rate,
            "duration_seconds": duration,
            "upload_date": upload_date,
            "hashtags": hashtags,
            "sound": sound,
        })

    sorted_hashtags = sorted(
        [
            {
                "hashtag": k,
                "video_count": hashtag_counts[k],
                "total_views": hashtag_views[k],
                "score": hashtag_counts[k] * hashtag_views[k],
            }
            for k in hashtag_counts
        ],
        key=lambda x: x["score"],
        reverse=True,
    )

    sorted_sounds = sorted(
        sound_counts.values(),
        key=lambda x: x["total_views"],
        reverse=True,
    )

    return {
        "metadata": {
            "source": f"tiktok_{source}",
            "region": region,
            "scraped_at": datetime.utcnow().isoformat() + "Z",
            "video_count": len(videos),
        },
        "videos": videos,
        "hashtags": sorted_hashtags[:50],
        "trending_sounds": sorted_sounds[:20],
    }


def _extract_tiktok_sound(entry: dict) -> Optional[dict]:
    """Extract sound/music info from a TikTok yt-dlp entry."""
    sound_id = entry.get("sound_id") or entry.get("music_id") or ""
    title = entry.get("track") or entry.get("music") or entry.get("sound_title", "")
    artist = entry.get("artist") or entry.get("music_author", "")
    is_original = entry.get("original_sound", False)
    duration = entry.get("music_duration")

    if not title and not sound_id:
        return None

    return {
        "sound_id": str(sound_id),
        "title": title,
        "artist": artist,
        "is_original": is_original,
        "duration_seconds": duration,
        "url": f"https://www.tiktok.com/music/{title.replace(' ', '-')}-{sound_id}" if sound_id else None,
    }


def _scrape_trending_hashtags_web(region: str, limit: int) -> dict:
    """Scrape TikTok trending hashtags using httpx."""
    import httpx
    from bs4 import BeautifulSoup

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml",
    }

    with httpx.Client(headers=headers, timeout=30, follow_redirects=True) as client:
        resp = client.get(
            "https://www.tiktok.com/explore",
            params={"lang": "en"},
        )
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    hashtags = []
    # TikTok renders hashtag challenges in data-e2e attributes or JSON script tags
    for script in soup.find_all("script", type="application/json"):
        try:
            data = json.loads(script.string or "")
            _extract_hashtags_from_json(data, hashtags)
        except Exception:
            continue

    # Also try anchor tags that look like hashtag links
    for a in soup.find_all("a", href=re.compile(r"/tag/")):
        tag = a.get("href", "").split("/tag/")[-1].split("?")[0]
        if tag and not any(h["hashtag"] == f"#{tag}" for h in hashtags):
            hashtags.append({
                "hashtag": f"#{tag}",
                "video_count": None,
                "total_views": None,
                "source": "web_scrape",
            })

    return {
        "region": region,
        "hashtags": hashtags[:limit],
        "scraped_at": datetime.utcnow().isoformat() + "Z",
        "method": "web_scrape",
    }


def _extract_hashtags_from_json(data, results: list, depth: int = 0):
    """Recursively mine nested JSON for hashtag challenge data."""
    if depth > 8:
        return
    if isinstance(data, dict):
        # TikTok uses challengeName / hashtagName in their JSON blobs
        tag = data.get("challengeName") or data.get("hashtagName") or data.get("title")
        views = data.get("stats", {}).get("videoCount") or data.get("viewCount")
        if tag and isinstance(tag, str) and 2 < len(tag) < 50:
            results.append({
                "hashtag": f"#{tag}" if not tag.startswith("#") else tag,
                "video_count": _normalize_count(views),
                "total_views": _normalize_count(
                    data.get("stats", {}).get("viewCount") or data.get("videoViewCount")
                ),
                "source": "json_embedded",
            })
        for v in data.values():
            _extract_hashtags_from_json(v, results, depth + 1)
    elif isinstance(data, list):
        for item in data[:50]:
            _extract_hashtags_from_json(item, results, depth + 1)


def _scrape_trending_sounds_api(region: str, limit: int) -> dict:
    """Fetch trending sounds via TikTok's internal API endpoints."""
    import httpx

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Referer": "https://www.tiktok.com/",
    }

    # TikTok's internal music chart endpoint
    params = {
        "aid": "1988",
        "app_name": "tiktok_web",
        "device_platform": "web_pc",
        "region": region,
        "music_chart_type": "1",  # 1=trending, 2=new, 3=rising
        "offset": "0",
        "limit": str(limit),
    }

    with httpx.Client(headers=headers, timeout=30) as client:
        resp = client.get(
            "https://www.tiktok.com/api/music/trending/",
            params=params,
        )
        resp.raise_for_status()
        data = resp.json()

    sounds = []
    for item in data.get("music_list", [])[:limit]:
        music = item.get("music", {}) or item
        sounds.append({
            "rank": len(sounds) + 1,
            "sound_id": str(music.get("id", "")),
            "title": music.get("title", ""),
            "artist": music.get("author_name", "") or music.get("owner_nickname", ""),
            "duration_seconds": music.get("duration"),
            "video_count": _normalize_count(music.get("user_count")),
            "cover_url": music.get("cover_large") or music.get("cover_medium", ""),
            "url": f"https://www.tiktok.com/music/-{music.get('id', '')}",
        })

    return {
        "region": region,
        "sounds": sounds,
        "scraped_at": datetime.utcnow().isoformat() + "Z",
        "method": "api",
    }


# ---------------------------------------------------------------------------
# Fallback data (used when live scraping fails)
# ---------------------------------------------------------------------------

_FALLBACK_HASHTAGS = {
    "US": [
        "#fyp", "#foryou", "#foryoupage", "#viral", "#trending",
        "#xyzbca", "#explore", "#tiktok", "#followme", "#duet",
        "#greenscreen", "#POV", "#challenge", "#comedy", "#funny",
        "#dance", "#music", "#art", "#food", "#fashion",
        "#beauty", "#fitness", "#gym", "#motivation", "#life",
        "#love", "#cute", "#aesthetic", "#vlog", "#storytime",
    ],
    "GB": [
        "#fyp", "#viral", "#uk", "#british", "#london",
        "#foryou", "#trending", "#tiktokuk", "#funny", "#comedy",
        "#fitness", "#fashion", "#food", "#music", "#art",
        "#beauty", "#lifestyle", "#vlog", "#challenge", "#explore",
    ],
}


def _fallback_trending_hashtags(region: str, limit: int, error: str) -> dict:
    tags = _FALLBACK_HASHTAGS.get(region, _FALLBACK_HASHTAGS["US"])[:limit]
    return {
        "region": region,
        "hashtags": [
            {"hashtag": t, "video_count": None, "total_views": None, "source": "seed_data"}
            for t in tags
        ],
        "scraped_at": datetime.utcnow().isoformat() + "Z",
        "method": "fallback_seed",
        "note": f"Live scraping unavailable ({error}). Showing curated seed hashtags.",
    }


_FALLBACK_SOUNDS = [
    {"title": "original sound", "artist": "various creators", "is_original": True},
    {"title": "Flowers", "artist": "Miley Cyrus", "is_original": False},
    {"title": "As It Was", "artist": "Harry Styles", "is_original": False},
    {"title": "Calm Down", "artist": "Rema", "is_original": False},
    {"title": "Rich Flex", "artist": "Drake & 21 Savage", "is_original": False},
    {"title": "Unholy", "artist": "Sam Smith", "is_original": False},
    {"title": "About Damn Time", "artist": "Lizzo", "is_original": False},
    {"title": "Bad Habit", "artist": "Steve Lacy", "is_original": False},
]


def _fallback_trending_sounds(region: str, limit: int, error: str) -> dict:
    sounds = [
        {**s, "rank": i + 1, "video_count": None, "source": "seed_data"}
        for i, s in enumerate(_FALLBACK_SOUNDS[:limit])
    ]
    return {
        "region": region,
        "sounds": sounds,
        "scraped_at": datetime.utcnow().isoformat() + "Z",
        "method": "fallback_seed",
        "note": f"Live scraping unavailable ({error}). Showing curated seed sounds.",
    }
