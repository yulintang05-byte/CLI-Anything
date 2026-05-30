#!/usr/bin/env python3
"""YouTube trend scraper — extracts trending videos, hashtags, and music.

Uses yt-dlp (no API key required) and YouTube RSS feeds for public trend data.
"""

import json
import subprocess
import sys
from datetime import datetime
from typing import Optional


def _run_ytdlp(args: list[str]) -> dict:
    """Run yt-dlp and return parsed JSON output."""
    cmd = [sys.executable, "-m", "yt_dlp", "--no-warnings", "--quiet"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            raise RuntimeError(f"yt-dlp error: {result.stderr.strip()}")
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        raise RuntimeError("yt-dlp timed out after 60s")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Could not parse yt-dlp output: {e}")


def _ytdlp_available() -> bool:
    try:
        subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--version"],
            capture_output=True, timeout=10
        )
        return True
    except Exception:
        return False


def _extract_hashtags(text: str) -> list[str]:
    """Pull #hashtags from title/description text."""
    import re
    return list(dict.fromkeys(re.findall(r"#\w+", text or "")))


def _normalize_count(raw) -> int:
    """Normalize view/like counts that may be strings like '1.2M'."""
    if raw is None:
        return 0
    if isinstance(raw, int):
        return raw
    s = str(raw).upper().replace(",", "")
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


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def scrape_trending(
    region: str = "US",
    category: str = "all",
    limit: int = 20,
    include_music: bool = True,
) -> dict:
    """Scrape YouTube trending page.

    Args:
        region: ISO country code (US, GB, IN, …)
        category: all | music | gaming | news | movies
        limit: max number of videos to return
        include_music: extract music/audio info per video

    Returns:
        dict with keys: videos, hashtags, music_tracks, metadata
    """
    category_ids = {
        "all": "0",
        "music": "10",
        "gaming": "20",
        "news": "25",
        "movies": "44",
    }
    cat_id = category_ids.get(category.lower(), "0")

    # YouTube trending URL pattern
    url = f"https://www.youtube.com/feed/trending?bp=4gIN{cat_id}&gl={region}"

    if not _ytdlp_available():
        raise RuntimeError(
            "yt-dlp is not installed. Run: pip install yt-dlp"
        )

    raw = _run_ytdlp([
        "--dump-single-json",
        "--flat-playlist",
        f"--playlist-end={limit}",
        "--extractor-args", "youtube:skip=dash,hls",
        url,
    ])

    entries = raw.get("entries", [])[:limit]
    videos = []
    all_hashtags: dict[str, int] = {}
    music_tracks: dict[str, dict] = {}

    for entry in entries:
        video_id = entry.get("id", "")
        title = entry.get("title", "")
        channel = entry.get("channel") or entry.get("uploader", "")
        views = _normalize_count(entry.get("view_count"))
        likes = _normalize_count(entry.get("like_count"))
        duration = entry.get("duration", 0)
        description = entry.get("description", "")
        thumbnails = entry.get("thumbnails", [])
        thumbnail = thumbnails[-1]["url"] if thumbnails else ""
        upload_date = entry.get("upload_date", "")
        categories = entry.get("categories", [])
        tags = entry.get("tags", []) or []

        hashtags = _extract_hashtags(title) + _extract_hashtags(description)
        hashtags += [f"#{t}" for t in tags if t and not t.startswith("#")]
        hashtags = list(dict.fromkeys(hashtags))

        for ht in hashtags:
            all_hashtags[ht] = all_hashtags.get(ht, 0) + views

        music_info = None
        if include_music:
            music_info = _extract_music_info(entry)
            if music_info:
                key = music_info["track"] or music_info["artist"]
                if key:
                    if key not in music_tracks:
                        music_tracks[key] = {**music_info, "video_count": 0, "total_views": 0}
                    music_tracks[key]["video_count"] += 1
                    music_tracks[key]["total_views"] += views

        videos.append({
            "rank": len(videos) + 1,
            "video_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "title": title,
            "channel": channel,
            "views": views,
            "likes": likes,
            "duration_seconds": duration,
            "upload_date": upload_date,
            "categories": categories,
            "hashtags": hashtags,
            "thumbnail": thumbnail,
            "music": music_info,
        })

    sorted_hashtags = sorted(
        [{"hashtag": k, "weighted_views": v} for k, v in all_hashtags.items()],
        key=lambda x: x["weighted_views"],
        reverse=True,
    )

    sorted_music = sorted(
        music_tracks.values(),
        key=lambda x: x["total_views"],
        reverse=True,
    )

    return {
        "metadata": {
            "source": "youtube_trending",
            "region": region,
            "category": category,
            "scraped_at": datetime.utcnow().isoformat() + "Z",
            "video_count": len(videos),
        },
        "videos": videos,
        "hashtags": sorted_hashtags[:50],
        "music_tracks": sorted_music[:20],
    }


def _extract_music_info(entry: dict) -> Optional[dict]:
    """Extract music/audio metadata from a yt-dlp entry."""
    # yt-dlp surfaces music metadata in several places
    info = {}

    # Check 'music' field (YouTube auto-detected)
    for music_entry in entry.get("music", []) or []:
        info["track"] = music_entry.get("song") or music_entry.get("track", "")
        info["artist"] = music_entry.get("artist", "")
        info["album"] = music_entry.get("album", "")
        info["release_year"] = music_entry.get("release_year")
        break

    # Fallback to top-level fields
    if not info.get("track"):
        info["track"] = entry.get("track", "") or ""
    if not info.get("artist"):
        info["artist"] = entry.get("artist", "") or entry.get("creator", "") or ""

    if not info.get("track") and not info.get("artist"):
        return None
    return info


def scrape_hashtag_videos(
    hashtag: str,
    limit: int = 10,
) -> dict:
    """Fetch videos for a specific YouTube hashtag.

    Args:
        hashtag: Hashtag without or with '#' prefix
        limit: Max number of videos

    Returns:
        dict with videos list and engagement metrics
    """
    if not hashtag.startswith("#"):
        hashtag = f"#{hashtag}"

    if not _ytdlp_available():
        raise RuntimeError("yt-dlp is not installed. Run: pip install yt-dlp")

    url = f"https://www.youtube.com/hashtag/{hashtag.lstrip('#')}"
    raw = _run_ytdlp([
        "--dump-single-json",
        "--flat-playlist",
        f"--playlist-end={limit}",
        url,
    ])

    entries = raw.get("entries", [])[:limit]
    videos = []
    total_views = 0

    for entry in entries:
        views = _normalize_count(entry.get("view_count"))
        total_views += views
        videos.append({
            "video_id": entry.get("id", ""),
            "url": f"https://www.youtube.com/watch?v={entry.get('id', '')}",
            "title": entry.get("title", ""),
            "channel": entry.get("channel") or entry.get("uploader", ""),
            "views": views,
            "upload_date": entry.get("upload_date", ""),
        })

    return {
        "hashtag": hashtag,
        "videos": videos,
        "total_views": total_views,
        "avg_views": total_views // max(len(videos), 1),
        "scraped_at": datetime.utcnow().isoformat() + "Z",
    }


def get_top_hashtags_for_niche(
    niche: str,
    limit: int = 20,
) -> dict:
    """Search YouTube for a niche and extract the most-used hashtags.

    Args:
        niche: Topic/niche keyword (e.g. 'fitness', 'cooking', 'gaming')
        limit: Number of videos to analyze

    Returns:
        dict with ranked hashtags and their frequency
    """
    if not _ytdlp_available():
        raise RuntimeError("yt-dlp is not installed. Run: pip install yt-dlp")

    url = f"https://www.youtube.com/results?search_query={niche}&sp=CAMSAhAB"  # sort by view count
    raw = _run_ytdlp([
        "--dump-single-json",
        "--flat-playlist",
        f"--playlist-end={limit}",
        url,
    ])

    entries = raw.get("entries", [])[:limit]
    hashtag_freq: dict[str, int] = {}
    hashtag_views: dict[str, int] = {}

    for entry in entries:
        views = _normalize_count(entry.get("view_count"))
        text = (entry.get("title", "") or "") + " " + (entry.get("description", "") or "")
        tags = entry.get("tags", []) or []
        hashtags = _extract_hashtags(text) + [f"#{t}" for t in tags if t]
        for ht in dict.fromkeys(hashtags):
            hashtag_freq[ht] = hashtag_freq.get(ht, 0) + 1
            hashtag_views[ht] = hashtag_views.get(ht, 0) + views

    ranked = sorted(
        [
            {
                "hashtag": k,
                "frequency": hashtag_freq[k],
                "total_views": hashtag_views[k],
                "score": hashtag_freq[k] * hashtag_views[k],
            }
            for k in hashtag_freq
        ],
        key=lambda x: x["score"],
        reverse=True,
    )

    return {
        "niche": niche,
        "videos_analyzed": len(entries),
        "hashtags": ranked[:limit],
        "scraped_at": datetime.utcnow().isoformat() + "Z",
    }
