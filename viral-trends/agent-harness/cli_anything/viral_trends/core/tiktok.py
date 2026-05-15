"""TikTok trending scraper — uses yt-dlp for public hashtag/discover feeds."""

import json
import subprocess
import re
from typing import Optional


TIKTOK_DISCOVER_HASHTAGS = [
    "fyp", "foryou", "foryoupage", "viral", "trending",
    "trending2025", "viral2025", "explore", "xyzbca",
]


def _run_ytdlp_tiktok(url: str, count: int = 20) -> list[dict]:
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--no-warnings",
        "--quiet",
        "--playlist-items", f"1:{count}",
        url,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        lines = [l for l in result.stdout.strip().splitlines() if l.strip()]
        parsed = []
        for line in lines:
            try:
                parsed.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return parsed
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def _normalize_tiktok(v: dict) -> dict:
    description = v.get("description") or v.get("title") or ""
    hashtags = re.findall(r"#\w+", description)

    music_info = {}
    if v.get("track"):
        music_info["track"] = v.get("track")
    if v.get("artist"):
        music_info["artist"] = v.get("artist")
    # TikTok-specific music fields
    if v.get("music"):
        m = v["music"]
        if isinstance(m, dict):
            music_info.update({
                "track": m.get("title", music_info.get("track", "")),
                "artist": m.get("authorName", music_info.get("artist", "")),
                "id": m.get("id", ""),
                "duration": m.get("duration", 0),
            })

    return {
        "id": v.get("id", ""),
        "title": description[:100],
        "channel": v.get("uploader", "") or v.get("creator", ""),
        "views": v.get("view_count", 0),
        "likes": v.get("like_count", 0),
        "comments": v.get("comment_count", 0),
        "shares": v.get("repost_count", 0),
        "duration": v.get("duration", 0),
        "upload_date": v.get("upload_date", ""),
        "hashtags": list(dict.fromkeys(hashtags)),
        "thumbnail": v.get("thumbnail", ""),
        "url": v.get("webpage_url", ""),
        "music": music_info if music_info else None,
        "platform": "tiktok",
    }


def fetch_hashtag_feed(hashtag: str, count: int = 20) -> list[dict]:
    """Fetch TikTok videos from a hashtag feed."""
    tag = hashtag.lstrip("#")
    url = f"https://www.tiktok.com/tag/{tag}"
    raw = _run_ytdlp_tiktok(url, count)
    return [_normalize_tiktok(v) for v in raw]


def fetch_trending(region: str = "US", count: int = 20) -> list[dict]:
    """Fetch TikTok trending videos by sampling top viral hashtags."""
    results = []
    seen_ids: set[str] = set()

    # Sample from top viral hashtags
    for tag in TIKTOK_DISCOVER_HASHTAGS[:3]:
        videos = fetch_hashtag_feed(tag, count=min(count, 10))
        for v in videos:
            if v["id"] not in seen_ids:
                seen_ids.add(v["id"])
                results.append(v)
        if len(results) >= count:
            break

    return results[:count]


def fetch_music_trends(count: int = 20) -> list[dict]:
    """Extract trending music/sounds from viral TikTok videos."""
    videos = fetch_trending(count=count * 2)
    music_map: dict[str, dict] = {}

    for v in videos:
        m = v.get("music")
        if not m:
            continue
        key = m.get("track", "") + "|" + m.get("artist", "")
        if not key.strip("|"):
            continue
        if key in music_map:
            music_map[key]["use_count"] += 1
            music_map[key]["total_views"] = (music_map[key].get("total_views", 0)
                                              + (v.get("views") or 0))
        else:
            music_map[key] = {
                "track": m.get("track", "Unknown"),
                "artist": m.get("artist", "Unknown"),
                "music_id": m.get("id", ""),
                "use_count": 1,
                "total_views": v.get("views") or 0,
                "platform": "tiktok",
            }

    ranked = sorted(music_map.values(), key=lambda x: x["use_count"], reverse=True)
    return ranked[:count]


def fetch_discover_hashtags(count: int = 30) -> list[dict]:
    """Return TikTok discover/trending hashtags by analyzing viral feed."""
    videos = fetch_trending(count=50)
    tag_counts: dict[str, int] = {}
    tag_views: dict[str, int] = {}

    for v in videos:
        for tag in v.get("hashtags", []):
            t = tag.lower()
            tag_counts[t] = tag_counts.get(t, 0) + 1
            tag_views[t] = tag_views.get(t, 0) + (v.get("views") or 0)

    ranked = sorted(tag_counts.keys(), key=lambda t: tag_counts[t], reverse=True)
    return [
        {
            "hashtag": t,
            "video_count": tag_counts[t],
            "total_views": tag_views[t],
            "platform": "tiktok",
        }
        for t in ranked[:count]
    ]
