"""TikTok trending scraper — uses yt-dlp + public API endpoints."""
import json
import re
import subprocess
from typing import Any


_TIKTOK_TRENDING_URL = "https://www.tiktok.com/trending"

# yt-dlp can download TikTok trending hashtag pages
_TIKTOK_HASHTAG_BASE = "https://www.tiktok.com/tag/{}"

# Public TikTok discover feed (no auth required)
_TIKTOK_DISCOVER_URL = "https://www.tiktok.com/api/explore/item_list/"


def _run_ytdlp(args: list[str], timeout: int = 60) -> dict[str, Any]:
    cmd = ["yt-dlp", "--no-warnings", "--quiet"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def _extract_hashtags(text: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"#(\w+)", text or "")))


def fetch_hashtag_videos(hashtag: str, limit: int = 10) -> list[dict]:
    """
    Fetch top videos for a TikTok hashtag using yt-dlp.
    Returns list of dicts: id, title, author, likes, plays, hashtags, music, url
    """
    url = _TIKTOK_HASHTAG_BASE.format(hashtag.lstrip("#"))
    args = [
        "--flat-playlist",
        "--playlist-end", str(limit),
        "--dump-single-json",
        url,
    ]
    try:
        data = _run_ytdlp(args, timeout=90)
    except (RuntimeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"TikTok hashtag scrape failed: {exc}") from exc

    entries = data.get("entries") or []
    results = []
    for entry in entries:
        if not entry:
            continue
        desc = entry.get("description") or entry.get("title") or ""
        tags = _extract_hashtags(desc)
        results.append({
            "id": entry.get("id", ""),
            "title": desc[:200],
            "author": entry.get("uploader") or entry.get("channel", ""),
            "likes": entry.get("like_count", 0),
            "plays": entry.get("view_count", 0),
            "hashtags": tags,
            "music": entry.get("track") or entry.get("music_track", ""),
            "music_author": entry.get("artist") or entry.get("music_author", ""),
            "url": entry.get("url") or entry.get("webpage_url", ""),
        })
    return results


def fetch_video_details(video_url: str) -> dict:
    """Fetch full metadata for a single TikTok video URL."""
    try:
        data = _run_ytdlp(["--dump-single-json", "--skip-download", video_url])
    except (RuntimeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"TikTok detail fetch failed: {exc}") from exc

    desc = data.get("description") or data.get("title") or ""
    tags = _extract_hashtags(desc)
    return {
        "id": data.get("id", ""),
        "title": desc[:200],
        "author": data.get("uploader") or data.get("channel", ""),
        "likes": data.get("like_count", 0),
        "comments": data.get("comment_count", 0),
        "plays": data.get("view_count", 0),
        "shares": data.get("repost_count", 0),
        "hashtags": tags,
        "music": data.get("track", ""),
        "music_author": data.get("artist", ""),
        "duration": data.get("duration", 0),
        "upload_date": data.get("upload_date", ""),
        "url": video_url,
    }


def fetch_trending_sounds_from_videos(videos: list[dict]) -> list[dict]:
    """
    Aggregate music/sound usage across a set of TikTok video dicts.
    Returns ranked list of: music, music_author, frequency
    """
    counts: dict[str, dict] = {}
    for v in videos:
        track = (v.get("music") or "").strip()
        if not track or track.lower() in ("", "original sound"):
            continue
        key = track.lower()
        if key not in counts:
            counts[key] = {"music": track, "music_author": v.get("music_author", ""), "frequency": 0}
        counts[key]["frequency"] += 1

    return sorted(counts.values(), key=lambda x: x["frequency"], reverse=True)


def aggregate_hashtags(videos: list[dict]) -> list[dict]:
    """Rank hashtags by frequency across a list of TikTok video dicts."""
    freq: dict[str, int] = {}
    for v in videos:
        for tag in v.get("hashtags", []):
            key = tag.lower()
            freq[key] = freq.get(key, 0) + 1
    ranked = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [{"hashtag": f"#{t}", "frequency": c} for t, c in ranked]
