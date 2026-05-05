"""YouTube viral trends scraper — no API key required.

Uses yt-dlp (flat playlist mode) to pull trending videos, then extracts
hashtags and music from video metadata. Falls back to requests+html parsing
if yt-dlp is unavailable.
"""

from __future__ import annotations

import json
import subprocess
import re
from collections import Counter
from typing import Any


# YouTube trending feed URLs per category
_YT_TRENDING_URLS = {
    "all":     "https://www.youtube.com/feed/trending",
    "music":   "https://www.youtube.com/feed/trending?bp=4gIuKhgKEgMLAhADGAAgASoECAIQAXoECAIQAQ%3D%3D",
    "gaming":  "https://www.youtube.com/feed/trending?bp=4gIcKhgKEgMLAhADGAAgASoECAEQAXoECAEQAQ%3D%3D",
    "movies":  "https://www.youtube.com/feed/trending?bp=4gIuKhgKEgMLAhADGAAgASoECAMQAXoECAMQAQ%3D%3D",
}


def _run_ytdlp(url: str, max_items: int = 25) -> list[dict]:
    """Run yt-dlp flat-playlist dump and return parsed entries."""
    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--flat-playlist",
                "--dump-json",
                "--playlist-end", str(max_items),
                "--no-warnings",
                "--quiet",
                url,
            ],
            capture_output=True,
            text=True,
            timeout=45,
        )
        entries = []
        for line in result.stdout.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        return entries
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return []


def _parse_hashtags(text: str) -> list[str]:
    """Extract #hashtags from a string."""
    return re.findall(r"#(\w+)", text or "")


def _fetch_trending_html(url: str) -> str:
    """Fallback: fetch raw HTML from YouTube trending page."""
    try:
        import urllib.request
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return ""


def _extract_titles_from_html(html: str) -> list[str]:
    """Pull video titles from YouTube trending HTML (ytInitialData)."""
    match = re.search(r"var ytInitialData\s*=\s*(\{.*?\});</script>", html, re.DOTALL)
    if not match:
        return []
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return []
    titles: list[str] = []
    raw = json.dumps(data)
    for m in re.finditer(r'"title"\s*:\s*\{"runs"\s*:\s*\[.*?"text"\s*:\s*"([^"]+)"', raw):
        titles.append(m.group(1))
    return list(dict.fromkeys(titles))[:30]


def fetch_youtube_trends(category: str = "all", max_items: int = 25) -> dict[str, Any]:
    """
    Fetch YouTube trending videos for a given category.

    Returns a dict with:
      - videos: list of trending video info
      - top_hashtags: most common hashtags across videos
      - top_keywords: most common title keywords
      - trending_music: music-related trending titles
    """
    url = _YT_TRENDING_URLS.get(category, _YT_TRENDING_URLS["all"])
    entries = _run_ytdlp(url, max_items)

    videos: list[dict] = []
    all_hashtags: list[str] = []
    all_titles: list[str] = []

    if entries:
        for e in entries:
            title = e.get("title", "")
            desc = e.get("description", "") or ""
            tags = e.get("tags") or []
            views = e.get("view_count", 0)
            uploader = e.get("uploader", "")
            vid_id = e.get("id", "")
            duration = e.get("duration_string", e.get("duration", ""))
            hashtags = _parse_hashtags(f"{title} {desc}") + [t for t in tags if t.startswith("#")]
            all_hashtags.extend(hashtags)
            all_titles.append(title)
            videos.append({
                "title": title,
                "url": f"https://www.youtube.com/watch?v={vid_id}" if vid_id else "",
                "uploader": uploader,
                "views": views,
                "duration": duration,
                "hashtags": hashtags[:10],
            })
    else:
        # Fallback: HTML scrape
        html = _fetch_trending_html(url)
        titles = _extract_titles_from_html(html)
        for t in titles:
            all_titles.append(t)
            videos.append({"title": t, "url": "", "uploader": "", "views": 0, "duration": "", "hashtags": []})

    # Top keywords from titles (filter stopwords)
    stopwords = {"the", "a", "an", "in", "on", "at", "to", "for", "of", "and",
                 "or", "is", "it", "this", "that", "with", "be", "you", "i",
                 "my", "me", "your", "we", "are", "was", "were", "its"}
    words: list[str] = []
    for title in all_titles:
        for w in re.findall(r"[a-zA-Z]{3,}", title.lower()):
            if w not in stopwords:
                words.append(w)

    top_keywords = [w for w, _ in Counter(words).most_common(20)]
    top_hashtags = [f"#{h}" for h, _ in Counter(all_hashtags).most_common(15)]

    # Music-related
    music_keywords = {"song", "music", "official", "mv", "audio", "lyrics",
                      "remix", "beat", "rap", "pop", "rnb", "hip", "hop"}
    trending_music = [v["title"] for v in videos if any(k in v["title"].lower() for k in music_keywords)]

    return {
        "platform": "youtube",
        "category": category,
        "total_fetched": len(videos),
        "videos": videos[:max_items],
        "top_hashtags": top_hashtags,
        "top_keywords": top_keywords,
        "trending_music": trending_music[:10],
    }
