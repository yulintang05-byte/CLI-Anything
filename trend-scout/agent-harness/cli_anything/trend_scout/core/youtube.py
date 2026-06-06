"""YouTube trend scraping via yt-dlp and YouTube's internal browse API.

Uses two complementary approaches:
  1. yt-dlp on youtube.com/feed/trending — reliable, no auth needed
  2. YouTube's internal /youtubei/v1/browse endpoint — richer hashtag data
"""

import json
import re
import subprocess
import sys
import time
from typing import Any
import urllib.request
import urllib.error


# ── yt-dlp approach ───────────────────────────────────────────────────────────

TRENDING_URLS = {
    "default":    "https://www.youtube.com/feed/trending",
    "music":      "https://www.youtube.com/feed/trending?bp=4gINGgt5dG1hX2NoYXJ0cw%3D%3D",
    "gaming":     "https://www.youtube.com/feed/trending?bp=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D",
    "movies":     "https://www.youtube.com/feed/trending?bp=4gIKGghmaWxtc19hbmQ%3D",
}

CATEGORIES = list(TRENDING_URLS.keys())


def _run_ytdlp(url: str, extra_args: list[str] | None = None) -> list[dict]:
    """Run yt-dlp --flat-playlist --dump-json and return parsed entries."""
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--flat-playlist",
        "--dump-json",
        "--no-warnings",
        "--quiet",
        "--extractor-args", "youtube:skip=dash,hls",
    ]
    if extra_args:
        cmd.extend(extra_args)
    cmd.append(url)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        entries = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return entries
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def _extract_hashtags_from_text(text: str) -> list[str]:
    """Pull #hashtags from video title/description."""
    return re.findall(r"#(\w+)", text or "")


def _parse_entry(entry: dict) -> dict:
    title = entry.get("title") or entry.get("fulltitle", "")
    desc = entry.get("description", "") or ""
    tags = entry.get("tags") or []
    hashtags = list(set(_extract_hashtags_from_text(title) + _extract_hashtags_from_text(desc) + tags))

    return {
        "id": entry.get("id", ""),
        "title": title,
        "channel": entry.get("channel") or entry.get("uploader", ""),
        "view_count": entry.get("view_count") or 0,
        "like_count": entry.get("like_count") or 0,
        "duration": entry.get("duration") or 0,
        "upload_date": entry.get("upload_date", ""),
        "url": f"https://www.youtube.com/watch?v={entry.get('id', '')}",
        "hashtags": hashtags,
        "thumbnail": entry.get("thumbnail", ""),
        "category": entry.get("categories", [None])[0] if entry.get("categories") else "",
    }


# ── internal YouTube browse API ───────────────────────────────────────────────

_BROWSE_API = "https://www.youtube.com/youtubei/v1/browse"
_YT_CLIENT = {
    "clientName": "WEB",
    "clientVersion": "2.20240101",
    "hl": "en",
    "gl": "US",
}


def _yt_api_request(browse_id: str, params: str = "") -> dict:
    payload = json.dumps({
        "context": {"client": _YT_CLIENT},
        "browseId": browse_id,
        **({"params": params} if params else {}),
    }).encode()

    req = urllib.request.Request(
        _BROWSE_API,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "X-YouTube-Client-Name": "1",
            "X-YouTube-Client-Version": "2.20240101",
            "Origin": "https://www.youtube.com",
            "Referer": "https://www.youtube.com/feed/trending",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError, Exception):
        return {}


def _deep_find(obj: Any, key: str) -> list:
    """Recursively collect all values for a given key in nested dicts/lists."""
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                results.append(v)
            else:
                results.extend(_deep_find(v, key))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(_deep_find(item, key))
    return results


def _extract_video_renderers(data: dict) -> list[dict]:
    """Pull videoRenderer objects from browse API response."""
    renderers = _deep_find(data, "videoRenderer")
    videos = []
    for r in renderers:
        vid_id = r.get("videoId", "")
        title_runs = _deep_find(r.get("title", {}), "text")
        title = "".join(title_runs)
        channel_runs = _deep_find(r.get("longBylineText", {}), "text")
        channel = "".join(channel_runs)

        view_text_list = _deep_find(r.get("viewCountText", {}), "text")
        view_text = "".join(view_text_list).replace(",", "").replace(" views", "")
        view_count = 0
        try:
            view_count = int(re.sub(r"[^\d]", "", view_text))
        except ValueError:
            pass

        overlay = _deep_find(r, "simpleText")
        duration_str = ""
        for t in overlay:
            if re.match(r"^\d+:\d+", str(t)):
                duration_str = t
                break

        hashtags = _deep_find(r, "hashtag")
        if not hashtags:
            hashtags = _extract_hashtags_from_text(title)

        videos.append({
            "id": vid_id,
            "title": title,
            "channel": channel,
            "view_count": view_count,
            "duration": duration_str,
            "url": f"https://www.youtube.com/watch?v={vid_id}",
            "hashtags": list(set(hashtags)),
        })
    return videos


# ── Public API ────────────────────────────────────────────────────────────────

def fetch_trending(category: str = "default", limit: int = 20) -> dict:
    """Fetch YouTube trending videos for a given category.

    Returns: {"category": ..., "videos": [...], "top_hashtags": [...], "top_sounds": [...]}
    """
    if category not in TRENDING_URLS:
        raise ValueError(f"Unknown category '{category}'. Choose from: {', '.join(CATEGORIES)}")

    url = TRENDING_URLS[category]

    # Try yt-dlp first (most reliable)
    raw = _run_ytdlp(url)
    videos = [_parse_entry(e) for e in raw[:limit]]

    # Fallback: internal browse API (get extra data)
    if not videos:
        browse_id = "FEtrending"
        params_map = {
            "music": "4gINGgt5dG1hX2NoYXJ0cw%3D%3D",
            "gaming": "4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D",
            "movies": "4gIKGghmaWxtc19hbmQ%3D",
        }
        data = _yt_api_request(browse_id, params_map.get(category, ""))
        videos = _extract_video_renderers(data)[:limit]

    # Aggregate top hashtags across all videos
    all_tags: dict[str, int] = {}
    for v in videos:
        for tag in v.get("hashtags", []):
            all_tags[tag.lower()] = all_tags.get(tag.lower(), 0) + 1

    top_hashtags = sorted(all_tags, key=lambda t: all_tags[t], reverse=True)[:30]

    return {
        "category": category,
        "source": "youtube",
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "video_count": len(videos),
        "videos": videos,
        "top_hashtags": top_hashtags,
        "top_sounds": _extract_top_sounds(videos),
    }


def _extract_top_sounds(videos: list[dict]) -> list[str]:
    """Infer popular sounds/tracks from video titles and descriptions."""
    music_keywords = []
    patterns = [
        r'\(Official [A-Za-z ]*\)',
        r'ft\. ([^|]+)',
        r'feat\. ([^|]+)',
        r'prod\. by ([^|]+)',
    ]
    for v in videos:
        title = v.get("title", "")
        for pattern in patterns:
            m = re.search(pattern, title, re.IGNORECASE)
            if m:
                music_keywords.append(m.group(0).strip())
    return list(dict.fromkeys(music_keywords))[:10]


def fetch_hashtag_videos(hashtag: str, limit: int = 10) -> dict:
    """Fetch recent videos for a specific YouTube hashtag."""
    url = f"https://www.youtube.com/hashtag/{hashtag.lstrip('#')}"
    raw = _run_ytdlp(url)
    videos = [_parse_entry(e) for e in raw[:limit]]
    return {
        "hashtag": hashtag.lstrip("#"),
        "source": "youtube",
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "video_count": len(videos),
        "videos": videos,
    }


def trending_categories() -> list[str]:
    return CATEGORIES
