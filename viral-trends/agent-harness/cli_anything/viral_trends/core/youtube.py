"""YouTube trending scraper — uses yt-dlp for public data, YouTube Data API v3 when key is set."""

import json
import subprocess
import os
from typing import Optional


YT_TRENDING_URLS = {
    "US": "https://www.youtube.com/feed/trending",
    "music": "https://www.youtube.com/feed/trending?bp=4gINGgt5dG1hX2NoYXJ0cw%3D%3D",
    "gaming": "https://www.youtube.com/feed/trending?bp=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D",
    "movies": "https://www.youtube.com/feed/trending?bp=4gIKGgh0cmFpbGVycw%3D%3D",
}


def _run_ytdlp(args: list[str]) -> dict | list | None:
    cmd = ["yt-dlp", "--dump-json", "--no-warnings", "--quiet"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        lines = [l for l in result.stdout.strip().splitlines() if l.strip()]
        if not lines:
            return None
        if len(lines) == 1:
            return json.loads(lines[0])
        return [json.loads(l) for l in lines]
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        return None


def _search_trending(query: str, count: int = 20) -> list[dict]:
    raw = _run_ytdlp([f"ytsearch{count}:{query}"])
    if raw is None:
        return []
    if isinstance(raw, dict):
        raw = [raw]
    return [_normalize_video(v) for v in raw]


def _normalize_video(v: dict) -> dict:
    tags = v.get("tags") or []
    description = v.get("description") or ""
    hashtags = [t for t in tags if t.startswith("#")]
    hashtags += [w for w in description.split() if w.startswith("#")]

    return {
        "id": v.get("id", ""),
        "title": v.get("title", ""),
        "channel": v.get("uploader", ""),
        "views": v.get("view_count", 0),
        "likes": v.get("like_count", 0),
        "comments": v.get("comment_count", 0),
        "duration": v.get("duration", 0),
        "upload_date": v.get("upload_date", ""),
        "hashtags": list(dict.fromkeys(hashtags)),
        "tags": tags[:20],
        "thumbnail": v.get("thumbnail", ""),
        "url": v.get("webpage_url", ""),
        "music": _extract_music_info(v),
        "platform": "youtube",
    }


def _extract_music_info(v: dict) -> dict | None:
    chapters = v.get("chapters") or []
    # yt-dlp exposes music info under various fields
    music_info = {}
    if v.get("track"):
        music_info["track"] = v.get("track")
    if v.get("artist"):
        music_info["artist"] = v.get("artist")
    if v.get("album"):
        music_info["album"] = v.get("album")
    return music_info if music_info else None


def fetch_trending(category: str = "general", region: str = "US", count: int = 20) -> list[dict]:
    """Fetch YouTube trending videos. Falls back to search if yt-dlp feed fails."""
    queries = {
        "general": "trending viral 2025",
        "music": "trending music 2025",
        "gaming": "trending gaming 2025",
        "movies": "trending movies 2025",
        "shorts": "#shorts trending",
    }
    query = queries.get(category, queries["general"])

    # Try API first if key available
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if api_key:
        return _fetch_via_api(api_key, category, region, count)

    return _search_trending(query, count)


def _fetch_via_api(api_key: str, category: str, region: str, count: int) -> list[dict]:
    """Use YouTube Data API v3 to get trending videos."""
    try:
        import urllib.request
        import urllib.parse

        category_ids = {"music": "10", "gaming": "20", "movies": "30", "general": "0"}
        cat_id = category_ids.get(category, "0")

        params = {
            "part": "snippet,statistics",
            "chart": "mostPopular",
            "regionCode": region,
            "maxResults": str(count),
            "key": api_key,
        }
        if cat_id != "0":
            params["videoCategoryId"] = cat_id

        url = "https://www.googleapis.com/youtube/v3/videos?" + urllib.parse.urlencode(params)
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        results = []
        for item in data.get("items", []):
            snip = item.get("snippet", {})
            stats = item.get("statistics", {})
            tags = snip.get("tags", [])
            hashtags = [t for t in tags if t.startswith("#")]
            results.append({
                "id": item.get("id", ""),
                "title": snip.get("title", ""),
                "channel": snip.get("channelTitle", ""),
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "duration": 0,
                "upload_date": snip.get("publishedAt", "")[:10].replace("-", ""),
                "hashtags": hashtags,
                "tags": tags[:20],
                "thumbnail": snip.get("thumbnails", {}).get("high", {}).get("url", ""),
                "url": f"https://www.youtube.com/watch?v={item.get('id', '')}",
                "music": None,
                "platform": "youtube",
            })
        return results
    except Exception:
        return []


def fetch_music_trends(region: str = "US", count: int = 20) -> list[dict]:
    """Fetch trending music videos from YouTube Music charts."""
    return fetch_trending("music", region, count)
