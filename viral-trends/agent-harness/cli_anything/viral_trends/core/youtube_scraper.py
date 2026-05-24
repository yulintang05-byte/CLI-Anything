"""YouTube trending scraper — fetches viral videos, hashtags, and music without API keys."""

import re
import json
import time
import random
import urllib.request
import urllib.parse
from typing import Optional
from datetime import datetime, timezone


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# YouTube trending category IDs
CATEGORY_MAP = {
    "now":    "0",   # Trending Now
    "music":  "10",  # Music
    "gaming": "20",  # Gaming
    "films":  "26",  # Films & Shows
    "shorts": "0",   # Shorts (filtered from main trending)
}

REGION_CODES = {
    "us": "US", "uk": "GB", "ca": "CA", "au": "AU",
    "in": "IN", "br": "BR", "de": "DE", "fr": "FR",
    "jp": "JP", "kr": "KR", "mx": "MX", "ng": "NG",
}


def _fetch_url(url: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=_HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as exc:
            if attempt == retries - 1:
                raise RuntimeError(f"Failed to fetch {url}: {exc}") from exc
            time.sleep(1.5 * (attempt + 1))
    return ""


def _extract_initial_data(html: str) -> Optional[dict]:
    """Pull ytInitialData JSON blob from YouTube page HTML."""
    patterns = [
        r"var ytInitialData\s*=\s*(\{.*?\});\s*</script>",
        r"window\[\"ytInitialData\"\]\s*=\s*(\{.*?\});",
        r"ytInitialData\s*=\s*(\{.*?\});\s*var ",
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                continue
    return None


def _walk(obj, key):
    """Recursively find all values for a given key in a nested dict/list."""
    results = []
    if isinstance(obj, dict):
        if key in obj:
            results.append(obj[key])
        for v in obj.values():
            results.extend(_walk(v, key))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(_walk(item, key))
    return results


def _parse_videos(data: dict, limit: int = 30) -> list[dict]:
    """Extract video metadata from ytInitialData."""
    videos = []
    video_renderers = _walk(data, "videoRenderer")
    for vr in video_renderers:
        if len(videos) >= limit:
            break
        try:
            video_id = vr.get("videoId", "")
            title_runs = _walk(vr.get("title", {}), "text")
            title = "".join(title_runs)
            channel_runs = _walk(vr.get("longBylineText", {}), "text")
            channel = "".join(channel_runs).strip()
            view_text = ""
            for vm in _walk(vr, "viewCountText"):
                if isinstance(vm, dict):
                    view_text = "".join(_walk(vm, "text"))
                    break
                elif isinstance(vm, str):
                    view_text = vm
                    break
            published = ""
            for pt in _walk(vr, "publishedTimeText"):
                if isinstance(pt, dict):
                    published = "".join(_walk(pt, "text"))
                    break
                elif isinstance(pt, str):
                    published = pt
                    break
            duration = ""
            for dt in _walk(vr, "lengthText"):
                if isinstance(dt, dict):
                    duration = "".join(_walk(dt, "text"))
                    break
                elif isinstance(dt, str):
                    duration = dt
                    break
            # Extract hashtags from title
            hashtags = re.findall(r"#\w+", title)
            if video_id:
                videos.append({
                    "video_id": video_id,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "title": title,
                    "channel": channel,
                    "views": view_text,
                    "published": published,
                    "duration": duration,
                    "hashtags": hashtags,
                })
        except Exception:
            continue
    return videos


def fetch_trending(
    category: str = "now",
    region: str = "us",
    limit: int = 30,
) -> dict:
    """Fetch YouTube trending videos for a category and region."""
    region_code = REGION_CODES.get(region.lower(), region.upper())
    cat_id = CATEGORY_MAP.get(category.lower(), "0")
    url = (
        f"https://www.youtube.com/feed/trending"
        f"?bp=Q{cat_id}%3D%3D&gl={region_code}&hl=en"
    )
    html = _fetch_url(url)
    data = _extract_initial_data(html)
    if not data:
        return {"error": "Could not parse YouTube page", "videos": [], "hashtags": [], "music_tracks": []}

    videos = _parse_videos(data, limit=limit)

    # Aggregate hashtags across all videos
    all_tags: dict[str, int] = {}
    for v in videos:
        for tag in v["hashtags"]:
            all_tags[tag.lower()] = all_tags.get(tag.lower(), 0) + 1
    ranked_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)

    # For music category, extract track info (title often contains "- Artist")
    music_tracks = []
    if category == "music":
        for v in videos:
            t = v["title"]
            if " - " in t:
                parts = t.split(" - ", 1)
                music_tracks.append({"artist": parts[0].strip(), "track": parts[1].strip(), "video_url": v["url"]})
            else:
                music_tracks.append({"artist": v["channel"], "track": t, "video_url": v["url"]})

    return {
        "platform": "youtube",
        "category": category,
        "region": region_code,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "videos": videos,
        "hashtags": [{"tag": t, "count": c} for t, c in ranked_tags],
        "music_tracks": music_tracks,
        "total": len(videos),
    }


def fetch_music_trends(region: str = "us", limit: int = 20) -> dict:
    """Fetch YouTube Music trending tracks."""
    return fetch_trending(category="music", region=region, limit=limit)


def search_hashtag(hashtag: str, limit: int = 20) -> dict:
    """Fetch top videos for a specific hashtag."""
    tag = hashtag.lstrip("#")
    url = f"https://www.youtube.com/hashtag/{urllib.parse.quote(tag)}"
    html = _fetch_url(url)
    data = _extract_initial_data(html)
    if not data:
        return {"error": "Could not parse hashtag page", "videos": []}
    videos = _parse_videos(data, limit=limit)
    return {
        "platform": "youtube",
        "hashtag": f"#{tag}",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "videos": videos,
        "total": len(videos),
    }
