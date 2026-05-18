"""YouTube trend scraper.

Uses yt-dlp (no API key required) to fetch trending videos, music,
and hashtag data from YouTube's public trending pages.

Install: pip install yt-dlp
"""

import json
import re
import shutil
import subprocess
import time
from typing import Optional

# YouTube trending category URLs (base64-encoded browse params)
TRENDING_URLS = {
    "general":  "https://www.youtube.com/feed/trending",
    "music":    "https://www.youtube.com/feed/trending?bp=4gINGgt5dG1hX2NoYXJ0cw%3D%3D",
    "gaming":   "https://www.youtube.com/feed/trending?bp=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D",
    "movies":   "https://www.youtube.com/feed/trending?bp=4gIKGgh0cmFpbGVycw%3D%3D",
}

# Hashtag-pattern regex
_HASHTAG_RE = re.compile(r"#[\w-￿]+")


def _ytdlp_available() -> bool:
    return shutil.which("yt-dlp") is not None


def _run_ytdlp(args: list[str], timeout: int = 90) -> str:
    """Run yt-dlp and return stdout, raising on failure."""
    if not _ytdlp_available():
        raise RuntimeError(
            "yt-dlp not found. Install with: pip install yt-dlp"
        )
    result = subprocess.run(
        ["yt-dlp"] + args,
        capture_output=True, text=True, timeout=timeout
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(f"yt-dlp error: {result.stderr[:300]}")
    return result.stdout


def get_trending_videos(
    category: str = "general",
    limit: int = 20,
    country: str = "US",
) -> list[dict]:
    """Fetch trending YouTube videos.

    Args:
        category: One of 'general', 'music', 'gaming', 'movies'.
        limit: Max number of videos to return.
        country: Two-letter country code for regional trending.

    Returns:
        List of video dicts with id, title, channel, views, tags, etc.
    """
    url = TRENDING_URLS.get(category, TRENDING_URLS["general"])
    args = [
        "--flat-playlist",
        "-j",
        "--playlist-end", str(limit),
        "--no-warnings",
        "--geo-bypass-country", country,
        url,
    ]
    raw = _run_ytdlp(args)
    videos = []
    for line in raw.strip().splitlines():
        if not line.strip():
            continue
        try:
            v = json.loads(line)
        except json.JSONDecodeError:
            continue
        hashtags = _HASHTAG_RE.findall(v.get("description") or "")
        hashtags += [t for t in (v.get("tags") or []) if isinstance(t, str)]
        videos.append({
            "id": v.get("id"),
            "title": v.get("title"),
            "channel": v.get("uploader") or v.get("channel"),
            "views": v.get("view_count"),
            "likes": v.get("like_count"),
            "duration_sec": v.get("duration"),
            "url": f"https://youtube.com/watch?v={v.get('id')}",
            "upload_date": v.get("upload_date"),
            "hashtags": list(dict.fromkeys(hashtags))[:20],
            "description_snippet": (v.get("description") or "")[:200],
            "category": category,
            "thumbnail": (v.get("thumbnails") or [{}])[-1].get("url"),
        })
    return videos


def get_trending_music(limit: int = 20, country: str = "US") -> list[dict]:
    """Fetch trending music videos from YouTube Charts.

    Returns:
        List of music video dicts with artist, title, views, etc.
    """
    videos = get_trending_videos(category="music", limit=limit, country=country)
    music = []
    for v in videos:
        title = v.get("title", "")
        channel = v.get("channel", "")
        # Try to split "Artist - Title" convention
        parts = title.split(" - ", 1)
        artist = parts[0].strip() if len(parts) == 2 else channel
        song = parts[1].strip() if len(parts) == 2 else title
        music.append({
            **v,
            "artist": artist,
            "song_title": song,
            "type": "music_video",
        })
    return music


def get_trending_hashtags(limit: int = 30, country: str = "US") -> list[dict]:
    """Extract trending hashtags from YouTube's general trending page.

    Returns:
        List of dicts: {hashtag, count, example_video_title}
    """
    videos = get_trending_videos(category="general", limit=50, country=country)
    hashtag_counts: dict[str, dict] = {}
    for v in videos:
        for tag in v.get("hashtags", []):
            tag = tag.lstrip("#").lower()
            if not tag:
                continue
            if tag not in hashtag_counts:
                hashtag_counts[tag] = {
                    "hashtag": f"#{tag}",
                    "count": 0,
                    "example_video": v.get("title", ""),
                }
            hashtag_counts[tag]["count"] += 1
    sorted_tags = sorted(
        hashtag_counts.values(),
        key=lambda x: x["count"],
        reverse=True,
    )
    return sorted_tags[:limit]


def search_channel_trends(channel_url: str, limit: int = 20) -> list[dict]:
    """Fetch recent/popular videos from a specific channel.

    Useful for competitor analysis and trend spotting by niche.
    """
    args = [
        "--flat-playlist",
        "-j",
        "--playlist-end", str(limit),
        "--no-warnings",
        channel_url,
    ]
    raw = _run_ytdlp(args)
    videos = []
    for line in raw.strip().splitlines():
        if not line.strip():
            continue
        try:
            v = json.loads(line)
        except json.JSONDecodeError:
            continue
        videos.append({
            "id": v.get("id"),
            "title": v.get("title"),
            "channel": v.get("uploader") or v.get("channel"),
            "views": v.get("view_count"),
            "url": f"https://youtube.com/watch?v={v.get('id')}",
            "upload_date": v.get("upload_date"),
            "hashtags": _HASHTAG_RE.findall(v.get("description") or ""),
        })
    return videos


def get_video_details(video_url: str) -> dict:
    """Fetch full metadata for a single YouTube video.

    Returns detailed info including tags, engagement metrics, description.
    """
    args = ["-j", "--no-warnings", video_url]
    raw = _run_ytdlp(args)
    if not raw.strip():
        raise RuntimeError(f"No data returned for {video_url}")
    try:
        v = json.loads(raw.strip().splitlines()[0])
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse video metadata: {e}")
    hashtags = _HASHTAG_RE.findall(v.get("description") or "")
    return {
        "id": v.get("id"),
        "title": v.get("title"),
        "channel": v.get("uploader"),
        "subscribers": v.get("channel_follower_count"),
        "views": v.get("view_count"),
        "likes": v.get("like_count"),
        "comments": v.get("comment_count"),
        "duration_sec": v.get("duration"),
        "upload_date": v.get("upload_date"),
        "tags": v.get("tags", []),
        "hashtags": hashtags,
        "categories": v.get("categories", []),
        "description": (v.get("description") or "")[:500],
        "url": v.get("webpage_url"),
    }
