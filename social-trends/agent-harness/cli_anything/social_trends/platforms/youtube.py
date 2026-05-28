"""YouTube trending scraper — no API key required.

Fetches trending videos, viral hashtags, and popular music from YouTube's
public trending/explore pages using requests + regex against the initial data.
"""

import re
import json
import time
import random
import hashlib
from datetime import datetime, timezone
from typing import Any
import requests

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

_HEADERS = {
    "User-Agent": _UA,
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# YouTube category IDs for trending
_CATEGORIES = {
    "all": "0",
    "music": "10",
    "gaming": "20",
    "movies": "1",
    "news": "25",
}


def _yt_initial_data(url: str) -> dict:
    """Pull ytInitialData JSON embedded in any YouTube page."""
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        m = re.search(r"var ytInitialData\s*=\s*(\{.*?\});\s*</script>", resp.text, re.DOTALL)
        if not m:
            m = re.search(r"ytInitialData\s*=\s*(\{.*?\});", resp.text, re.DOTALL)
        if m:
            return json.loads(m.group(1))
    except Exception:
        pass
    return {}


def _walk(obj: Any, target_key: str, results: list, max_depth: int = 20) -> None:
    """Recursively walk nested dicts/lists to collect all values at target_key."""
    if max_depth <= 0:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == target_key:
                results.append(v)
            else:
                _walk(v, target_key, results, max_depth - 1)
    elif isinstance(obj, list):
        for item in obj:
            _walk(item, target_key, results, max_depth - 1)


def get_trending_videos(category: str = "all", limit: int = 20) -> list[dict]:
    """Return trending YouTube videos for the given category."""
    cat_id = _CATEGORIES.get(category.lower(), "0")
    url = f"https://www.youtube.com/feed/trending?bp=4gINGgt7category_id}}"
    # Use the correct trending URL format
    if cat_id == "0":
        url = "https://www.youtube.com/feed/trending"
    else:
        # YouTube uses a base64 param for category filtering
        url = f"https://www.youtube.com/feed/trending?bp=4gIN{_cat_bp(cat_id)}"

    data = _yt_initial_data(url)
    videos = []

    video_renderers: list = []
    _walk(data, "videoRenderer", video_renderers)

    seen = set()
    for renderer in video_renderers:
        if not isinstance(renderer, dict):
            continue
        vid_id = renderer.get("videoId", "")
        if not vid_id or vid_id in seen:
            continue
        seen.add(vid_id)

        title_runs = renderer.get("title", {}).get("runs", [])
        title = "".join(r.get("text", "") for r in title_runs)

        channel_runs = (
            renderer.get("ownerText", {}).get("runs", [])
            or renderer.get("shortBylineText", {}).get("runs", [])
        )
        channel = "".join(r.get("text", "") for r in channel_runs)

        views_text = (
            renderer.get("viewCountText", {}).get("simpleText", "")
            or renderer.get("viewCountText", {}).get("runs", [{}])[0].get("text", "")
        )

        published = (
            renderer.get("publishedTimeText", {}).get("simpleText", "")
        )

        thumbnail_url = ""
        thumbs = renderer.get("thumbnail", {}).get("thumbnails", [])
        if thumbs:
            thumbnail_url = thumbs[-1].get("url", "")

        badge_labels: list[str] = []
        badges = renderer.get("badges", []) or renderer.get("ownerBadges", [])
        _walk(badges, "label", badge_labels)

        videos.append({
            "platform": "youtube",
            "video_id": vid_id,
            "title": title,
            "channel": channel,
            "views": views_text,
            "published": published,
            "thumbnail": thumbnail_url,
            "url": f"https://www.youtube.com/watch?v={vid_id}",
            "badges": badge_labels,
            "category": category,
        })
        if len(videos) >= limit:
            break

    return videos


def get_trending_hashtags(limit: int = 30) -> list[dict]:
    """Extract trending hashtags by scanning YouTube trending page descriptions."""
    data = _yt_initial_data("https://www.youtube.com/feed/trending")

    # Collect all text runs and look for hashtag-style links
    hashtag_renderers: list = []
    _walk(data, "hashtagHeaderRenderer", hashtag_renderers)

    tags: list[dict] = []
    seen: set[str] = set()

    for r in hashtag_renderers:
        if not isinstance(r, dict):
            continue
        runs = r.get("hashtag", {}).get("runs", [])
        for run in runs:
            txt = run.get("text", "")
            if txt.startswith("#") and txt not in seen:
                seen.add(txt)
                tags.append({
                    "platform": "youtube",
                    "hashtag": txt,
                    "type": "trending",
                })

    # Also pull hashtags from video titles/descriptions
    title_texts: list[str] = []
    _walk(data, "text", title_texts)
    for txt in title_texts:
        if isinstance(txt, str):
            for m in re.finditer(r"#\w+", txt):
                tag = m.group(0)
                if tag not in seen:
                    seen.add(tag)
                    tags.append({"platform": "youtube", "hashtag": tag, "type": "extracted"})

    return tags[:limit]


def get_trending_music(limit: int = 20) -> list[dict]:
    """Return trending music videos from YouTube Music charts page."""
    # Pull from YouTube Music category trending
    url = "https://www.youtube.com/feed/trending?bp=4gIuKhgKFmFwcEFQbVBKWUYzRHR4RFZTZTU4amQQARgD"
    data = _yt_initial_data(url)

    videos: list[dict] = []
    seen: set[str] = set()
    video_renderers: list = []
    _walk(data, "videoRenderer", video_renderers)

    for renderer in video_renderers:
        if not isinstance(renderer, dict):
            continue
        vid_id = renderer.get("videoId", "")
        if not vid_id or vid_id in seen:
            continue
        seen.add(vid_id)

        title_runs = renderer.get("title", {}).get("runs", [])
        title = "".join(r.get("text", "") for r in title_runs)
        channel_runs = (
            renderer.get("ownerText", {}).get("runs", [])
            or renderer.get("shortBylineText", {}).get("runs", [])
        )
        channel = "".join(r.get("text", "") for r in channel_runs)
        views_text = renderer.get("viewCountText", {}).get("simpleText", "")

        videos.append({
            "platform": "youtube",
            "type": "music",
            "video_id": vid_id,
            "title": title,
            "artist": channel,
            "views": views_text,
            "url": f"https://www.youtube.com/watch?v={vid_id}",
        })
        if len(videos) >= limit:
            break

    return videos


def get_viral_keywords(limit: int = 25) -> list[dict]:
    """Extract high-frequency keywords from trending YouTube video titles."""
    videos = get_trending_videos(limit=50)
    freq: dict[str, int] = {}
    stopwords = {
        "the", "a", "an", "in", "on", "at", "to", "for", "of", "and",
        "or", "but", "is", "was", "are", "were", "be", "been", "has",
        "have", "had", "do", "did", "will", "would", "could", "should",
        "i", "you", "he", "she", "we", "they", "it", "this", "that",
        "with", "from", "by", "as", "up", "out", "if", "about",
    }
    for v in videos:
        words = re.findall(r"[a-zA-Z]{3,}", v.get("title", "").lower())
        for w in words:
            if w not in stopwords:
                freq[w] = freq.get(w, 0) + 1

    sorted_kw = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [
        {"keyword": kw, "frequency": cnt, "platform": "youtube"}
        for kw, cnt in sorted_kw[:limit]
    ]


def _cat_bp(cat_id: str) -> str:
    """Approximate base64 param for YouTube trending category filter."""
    cat_map = {
        "10": "GgttdXNpY190cmVuZA%3D%3D",
        "20": "GgtqZ2FtaW5nX3RyZW5k",
        "1":  "GgtIbW92aWVzX3RyZW5k",
        "25": "Ggt4bmV3c190cmVuZA%3D%3D",
    }
    return cat_map.get(cat_id, "")
