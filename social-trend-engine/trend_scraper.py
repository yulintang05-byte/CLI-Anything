"""
YouTube + TikTok viral trend scraper.
Uses yt-dlp for metadata extraction (no API key required).
Extracts: titles, views, hashtags, music, descriptions.
"""

import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime
from typing import Optional

try:
    import yt_dlp
except ImportError:
    print("Installing yt-dlp...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp", "-q"])
    import yt_dlp


YOUTUBE_TRENDING_URLS = {
    "general":     "https://www.youtube.com/feed/trending",
    "music":       "https://www.youtube.com/feed/trending?bp=4gINGgt5dG1hX2NoYXJ0cw%3D%3D",
    "gaming":      "https://www.youtube.com/feed/trending?bp=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D",
    "films":       "https://www.youtube.com/feed/trending?bp=4gIKGgh0cmFpbGVycw%3D%3D",
}

TIKTOK_TRENDING_URLS = {
    "trending":    "https://www.tiktok.com/trending",
    "discover":    "https://www.tiktok.com/explore",
}

# yt-dlp options shared across scrapers
_BASE_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "extract_flat": "in_playlist",
    "skip_download": True,
    "ignoreerrors": True,
    "socket_timeout": 15,
}


def _extract_hashtags(text: str) -> list[str]:
    """Pull #hashtags from any free-form text."""
    return [tag.lower() for tag in re.findall(r"#(\w+)", text or "")]


def _extract_music_from_info(info: dict) -> Optional[str]:
    """Best-effort music/track detection from yt-dlp info dict."""
    for field in ("track", "artist", "album", "music", "song"):
        val = info.get(field)
        if val:
            return f"{info.get('artist', '')} - {val}".strip(" -")
    # TikTok stores it in 'music_info'
    music_info = info.get("music_info") or info.get("music") or {}
    if isinstance(music_info, dict):
        title = music_info.get("title") or music_info.get("name") or ""
        author = music_info.get("author") or music_info.get("artist") or ""
        if title:
            return f"{author} - {title}".strip(" -")
    return None


def scrape_youtube_trending(category: str = "general", max_results: int = 30) -> list[dict]:
    """
    Fetch YouTube trending videos for a given category.
    Returns list of dicts with: title, url, views, likes, hashtags, description, channel, published.
    """
    url = YOUTUBE_TRENDING_URLS.get(category, YOUTUBE_TRENDING_URLS["general"])
    opts = {
        **_BASE_OPTS,
        "playlistend": max_results,
    }

    results = []
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            entries = info.get("entries", []) if info else []

            for entry in entries:
                if not entry:
                    continue
                # Fetch full metadata for each video
                try:
                    full_opts = {**_BASE_OPTS, "extract_flat": False}
                    with yt_dlp.YoutubeDL(full_opts) as ydl2:
                        full = ydl2.extract_info(
                            f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                            download=False,
                        )
                except Exception:
                    full = entry

                if not full:
                    continue

                desc = full.get("description") or ""
                tags = full.get("tags") or []
                hashtags = _extract_hashtags(desc) + [t.lower() for t in tags if t]

                results.append({
                    "platform":     "youtube",
                    "category":     category,
                    "title":        full.get("title") or entry.get("title", ""),
                    "url":          full.get("webpage_url") or f"https://youtube.com/watch?v={entry.get('id','')}",
                    "views":        full.get("view_count") or 0,
                    "likes":        full.get("like_count") or 0,
                    "channel":      full.get("uploader") or "",
                    "hashtags":     list(set(hashtags)),
                    "description":  desc[:500],
                    "duration_sec": full.get("duration") or 0,
                    "published":    full.get("upload_date") or "",
                    "music":        _extract_music_from_info(full),
                    "scraped_at":   datetime.utcnow().isoformat(),
                })
    except Exception as e:
        print(f"[YouTube scrape error] {e}")

    return results


def scrape_tiktok_trending(username: str = "", hashtag: str = "", max_results: int = 30) -> list[dict]:
    """
    Scrape TikTok trending/hashtag/user content.
    Provide either a username or hashtag (without #).
    Falls back to general trending if neither given.
    """
    if username:
        url = f"https://www.tiktok.com/@{username}"
    elif hashtag:
        url = f"https://www.tiktok.com/tag/{hashtag.lstrip('#')}"
    else:
        # General trending page
        url = "https://www.tiktok.com/trending"

    opts = {
        **_BASE_OPTS,
        "playlistend": max_results,
    }

    results = []
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            entries = (info.get("entries") or []) if info else []
            # If single video returned directly
            if not entries and info and info.get("id"):
                entries = [info]

            for entry in entries:
                if not entry:
                    continue

                desc = entry.get("description") or entry.get("title") or ""
                hashtags = _extract_hashtags(desc)
                music = _extract_music_from_info(entry)

                results.append({
                    "platform":     "tiktok",
                    "title":        entry.get("title") or desc[:100],
                    "url":          entry.get("webpage_url") or entry.get("url") or "",
                    "views":        entry.get("view_count") or 0,
                    "likes":        entry.get("like_count") or 0,
                    "shares":       entry.get("repost_count") or 0,
                    "comments":     entry.get("comment_count") or 0,
                    "channel":      entry.get("uploader") or entry.get("creator") or "",
                    "hashtags":     hashtags,
                    "description":  desc[:500],
                    "duration_sec": entry.get("duration") or 0,
                    "music":        music,
                    "published":    entry.get("upload_date") or "",
                    "scraped_at":   datetime.utcnow().isoformat(),
                })
    except Exception as e:
        print(f"[TikTok scrape error - {url}] {e}")

    return results


def get_trending_hashtags(data: list[dict], top_n: int = 30) -> list[tuple[str, int]]:
    """Aggregate and rank hashtags from scraped results."""
    counter: Counter = Counter()
    for item in data:
        for tag in item.get("hashtags", []):
            if tag and len(tag) > 1:
                counter[tag] += 1
    return counter.most_common(top_n)


def get_trending_music(data: list[dict], top_n: int = 20) -> list[tuple[str, int]]:
    """Aggregate and rank trending music/tracks from scraped results."""
    counter: Counter = Counter()
    for item in data:
        music = item.get("music")
        if music:
            counter[music] += 1
    return counter.most_common(top_n)


def save_results(data: list[dict], filepath: str) -> None:
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} results to {filepath}")


if __name__ == "__main__":
    print("Testing YouTube trending scrape (general, 5 videos)...")
    yt = scrape_youtube_trending("general", max_results=5)
    print(json.dumps(yt[:2], indent=2))
    print(f"\nTop hashtags: {get_trending_hashtags(yt, 10)}")
