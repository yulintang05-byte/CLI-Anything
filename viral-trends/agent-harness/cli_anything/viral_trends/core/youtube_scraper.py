"""YouTube trending scraper.

Uses yt-dlp (subprocess) as the primary backend to pull YouTube Trending and
YouTube Shorts trending pages without requiring an API key.  Falls back to a
lightweight requests-based approach when yt-dlp is not installed.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

CACHE_DIR = Path.home() / ".config" / "viral-trends" / "cache"
CACHE_TTL = 3600  # 1 hour

TRENDING_URLS = {
    "all":    "https://www.youtube.com/feed/trending",
    "music":  "https://www.youtube.com/feed/trending?bp=4gINGgt5dG1hX2NoYXJ0cw%3D%3D",
    "gaming": "https://www.youtube.com/feed/trending?bp=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D",
    "films":  "https://www.youtube.com/feed/trending?bp=4gIKGgh0cmFpbGVycw%3D%3D",
    "shorts": "https://www.youtube.com/shorts/",
}


# ── Cache helpers ─────────────────────────────────────────────────────────────

def _cache_path(key: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"yt_{key}.json"


def _load_cache(key: str) -> list[dict] | None:
    p = _cache_path(key)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text())
        if time.time() - data.get("ts", 0) < CACHE_TTL:
            return data["items"]
    except (json.JSONDecodeError, KeyError):
        pass
    return None


def _save_cache(key: str, items: list[dict]) -> None:
    _cache_path(key).write_text(json.dumps({"ts": time.time(), "items": items}))


# ── yt-dlp backend ────────────────────────────────────────────────────────────

def _ytdlp_available() -> bool:
    return subprocess.run(
        ["yt-dlp", "--version"],
        capture_output=True,
    ).returncode == 0


def _scrape_with_ytdlp(category: str = "all", limit: int = 30) -> list[dict]:
    url = TRENDING_URLS.get(category, TRENDING_URLS["all"])
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--flat-playlist",
        "--playlist-end", str(limit),
        "--no-warnings",
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {result.stderr[:200]}")

    videos = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError:
            continue

        hashtags = _extract_hashtags(raw.get("description", "") or raw.get("title", ""))
        videos.append({
            "id":          raw.get("id", ""),
            "title":       raw.get("title", ""),
            "channel":     raw.get("channel", raw.get("uploader", "")),
            "views":       raw.get("view_count", 0),
            "likes":       raw.get("like_count", 0),
            "duration":    raw.get("duration", 0),
            "url":         f"https://youtu.be/{raw.get('id', '')}",
            "thumbnail":   raw.get("thumbnail", ""),
            "hashtags":    hashtags,
            "description": (raw.get("description", "") or "")[:300],
            "platform":    "youtube",
            "category":    category,
        })
    return videos


# ── requests fallback ─────────────────────────────────────────────────────────

_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def _scrape_with_requests(category: str = "all", limit: int = 30) -> list[dict]:
    if not HAS_REQUESTS:
        raise RuntimeError("requests not installed; run: pip install requests")

    url = TRENDING_URLS.get(category, TRENDING_URLS["all"])
    resp = requests.get(url, headers=_BROWSER_HEADERS, timeout=30)
    resp.raise_for_status()
    html = resp.text

    # YouTube embeds video data in ytInitialData JSON
    match = re.search(r"var ytInitialData\s*=\s*(\{.+?\});</script>", html, re.DOTALL)
    if not match:
        return []

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return []

    videos = []
    for item in _walk_json(data, "videoRenderer"):
        vid_id = item.get("videoId", "")
        title_runs = item.get("title", {}).get("runs", [{}])
        title = "".join(r.get("text", "") for r in title_runs)
        channel_runs = item.get("ownerText", {}).get("runs", [{}])
        channel = "".join(r.get("text", "") for r in channel_runs)
        views_text = item.get("viewCountText", {}).get("simpleText", "0")
        desc_runs = item.get("descriptionSnippet", {}).get("runs", [{}])
        description = "".join(r.get("text", "") for r in desc_runs)

        hashtags = _extract_hashtags(description + " " + title)
        videos.append({
            "id":          vid_id,
            "title":       title,
            "channel":     channel,
            "views":       _parse_view_count(views_text),
            "likes":       0,
            "duration":    0,
            "url":         f"https://youtu.be/{vid_id}",
            "thumbnail":   f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg" if vid_id else "",
            "hashtags":    hashtags,
            "description": description[:300],
            "platform":    "youtube",
            "category":    category,
        })
        if len(videos) >= limit:
            break
    return videos


def _walk_json(obj: Any, target_key: str) -> list[dict]:
    """Recursively find all objects where a key named target_key exists."""
    results = []
    if isinstance(obj, dict):
        if target_key in obj:
            results.append(obj[target_key])
        for v in obj.values():
            results.extend(_walk_json(v, target_key))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(_walk_json(item, target_key))
    return results


# ── Shared helpers ────────────────────────────────────────────────────────────

def _extract_hashtags(text: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"#(\w+)", text)))


def _parse_view_count(text: str) -> int:
    text = text.replace(",", "").replace(" views", "").strip()
    multipliers = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}
    for suffix, mult in multipliers.items():
        if text.upper().endswith(suffix):
            try:
                return int(float(text[:-1]) * mult)
            except ValueError:
                return 0
    try:
        return int(text)
    except ValueError:
        return 0


# ── Public API ────────────────────────────────────────────────────────────────

def get_trending(
    category: str = "all",
    limit: int = 30,
    use_cache: bool = True,
    force_refresh: bool = False,
) -> list[dict]:
    """Return trending YouTube videos for the given category.

    Args:
        category: one of all | music | gaming | films | shorts
        limit:    max videos to return (1-50)
        use_cache: return cached results if fresh
        force_refresh: bypass cache

    Returns list of video dicts with keys:
        id, title, channel, views, likes, duration, url, thumbnail,
        hashtags, description, platform, category
    """
    cache_key = f"{category}_{limit}"
    if use_cache and not force_refresh:
        cached = _load_cache(cache_key)
        if cached is not None:
            return cached[:limit]

    if _ytdlp_available():
        videos = _scrape_with_ytdlp(category, limit)
    else:
        videos = _scrape_with_requests(category, limit)

    _save_cache(cache_key, videos)
    return videos


def get_all_hashtags(category: str = "all", limit: int = 30) -> list[dict]:
    """Return ranked hashtags extracted from YouTube trending videos.

    Each entry: {hashtag, frequency, total_views, videos}
    """
    videos = get_trending(category, limit)
    counts: dict[str, dict] = {}
    for v in videos:
        for tag in v["hashtags"]:
            tag_lower = tag.lower()
            if tag_lower not in counts:
                counts[tag_lower] = {"hashtag": tag_lower, "frequency": 0, "total_views": 0, "videos": []}
            counts[tag_lower]["frequency"] += 1
            counts[tag_lower]["total_views"] += v.get("views", 0)
            counts[tag_lower]["videos"].append(v["id"])

    ranked = sorted(counts.values(), key=lambda x: x["frequency"], reverse=True)
    return ranked


def get_trending_music_from_videos(limit: int = 30) -> list[dict]:
    """Extract music-related keywords and channel names from music trending."""
    videos = get_trending("music", limit)
    return [
        {
            "title":   v["title"],
            "channel": v["channel"],
            "views":   v["views"],
            "url":     v["url"],
            "hashtags": v["hashtags"],
        }
        for v in videos
    ]
