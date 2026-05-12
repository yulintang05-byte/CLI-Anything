"""Trend fetching for YouTube and TikTok.

Supports:
- YouTube Data API v3 (requires YOUTUBE_API_KEY env var) — authoritative
- YouTube HTML scrape fallback (no key needed)
- TikTok trending via RapidAPI (requires TIKTOK_RAPIDAPI_KEY)
- TikTok HTML scrape fallback
"""

import os
import json
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone
from typing import Optional


# ── YouTube ───────────────────────────────────────────────────────────────────

YT_API_BASE = "https://www.googleapis.com/youtube/v3"

# TikTok trending via unofficial/rapid mirror
TIKTOK_RAPID_HOST = "tiktok-api6.p.rapidapi.com"
TIKTOK_RAPID_BASE = "https://tiktok-api6.p.rapidapi.com"


def _http_get(url: str, headers: dict | None = None) -> dict | str | None:
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return raw
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


# ── YouTube trending ──────────────────────────────────────────────────────────

def fetch_youtube_trending(
    region: str = "US",
    category_id: str = "0",
    max_results: int = 25,
) -> list[dict]:
    """Return top trending YouTube videos.

    Uses YouTube Data API v3 when YOUTUBE_API_KEY is set, otherwise falls back
    to scraping the YouTube trending page (limited metadata).
    """
    api_key = os.environ.get("YOUTUBE_API_KEY", "")
    if api_key:
        return _yt_api_trending(api_key, region, category_id, max_results)
    return _yt_scrape_trending(region, max_results)


def _yt_api_trending(
    api_key: str,
    region: str,
    category_id: str,
    max_results: int,
) -> list[dict]:
    params = urllib.parse.urlencode({
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region,
        "videoCategoryId": category_id,
        "maxResults": min(max_results, 50),
        "key": api_key,
    })
    data = _http_get(f"{YT_API_BASE}/videos?{params}")
    if isinstance(data, dict) and "items" in data:
        results = []
        for item in data["items"]:
            snip = item.get("snippet", {})
            stats = item.get("statistics", {})
            results.append({
                "platform": "youtube",
                "id": item.get("id", ""),
                "title": snip.get("title", ""),
                "channel": snip.get("channelTitle", ""),
                "published_at": snip.get("publishedAt", ""),
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
                "tags": snip.get("tags", []),
                "thumbnail": snip.get("thumbnails", {}).get("high", {}).get("url", ""),
                "url": f"https://www.youtube.com/watch?v={item.get('id', '')}",
                "source": "youtube_api",
            })
        return results
    return [{"error": "YouTube API error", "detail": str(data)}]


def _yt_scrape_trending(region: str, max_results: int) -> list[dict]:
    """Minimal scrape — returns placeholders when JS-rendered content blocks us."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "gl": region,
        "hl": "en",
    }
    url = f"https://www.youtube.com/feed/trending?gl={region}&hl=en"
    raw = _http_get(url, headers)
    if isinstance(raw, dict) and "error" in raw:
        return [{"platform": "youtube", "source": "scrape", **raw}]

    # Extract video IDs from ytInitialData JSON blob embedded in HTML
    import re
    ids_found = re.findall(r'"videoId"\s*:\s*"([A-Za-z0-9_-]{11})"', raw or "")
    seen: set[str] = set()
    results = []
    for vid in ids_found:
        if vid in seen:
            continue
        seen.add(vid)
        results.append({
            "platform": "youtube",
            "id": vid,
            "url": f"https://www.youtube.com/watch?v={vid}",
            "source": "scrape_html",
            "note": "Add YOUTUBE_API_KEY for full metadata",
        })
        if len(results) >= max_results:
            break
    return results or [{"platform": "youtube", "source": "scrape_html",
                        "note": "No IDs extracted — page may require JS. Set YOUTUBE_API_KEY."}]


# ── TikTok trending ───────────────────────────────────────────────────────────

def fetch_tiktok_trending(max_results: int = 25) -> list[dict]:
    """Return trending TikTok videos.

    Uses TIKTOK_RAPIDAPI_KEY if set (tiktok-api6.p.rapidapi.com),
    otherwise falls back to parsing the TikTok trending JSON endpoint.
    """
    rapid_key = os.environ.get("TIKTOK_RAPIDAPI_KEY", "")
    if rapid_key:
        return _tiktok_rapid_trending(rapid_key, max_results)
    return _tiktok_scrape_trending(max_results)


def _tiktok_rapid_trending(key: str, max_results: int) -> list[dict]:
    headers = {
        "x-rapidapi-key": key,
        "x-rapidapi-host": TIKTOK_RAPID_HOST,
    }
    data = _http_get(f"{TIKTOK_RAPID_BASE}/feed/trending?region=US&count={min(max_results, 30)}", headers)
    if not isinstance(data, dict) or "itemList" not in data:
        return [{"platform": "tiktok", "source": "rapidapi", "error": str(data)}]

    results = []
    for item in data.get("itemList", [])[:max_results]:
        author = item.get("author", {})
        stats = item.get("stats", {})
        music = item.get("music", {})
        results.append({
            "platform": "tiktok",
            "id": item.get("id", ""),
            "description": item.get("desc", ""),
            "author": author.get("uniqueId", ""),
            "play_count": stats.get("playCount", 0),
            "like_count": stats.get("diggCount", 0),
            "comment_count": stats.get("commentCount", 0),
            "share_count": stats.get("shareCount", 0),
            "music_title": music.get("title", ""),
            "music_author": music.get("authorName", ""),
            "hashtags": [c.get("hashtagName", "") for c in item.get("challenges", [])],
            "url": f"https://www.tiktok.com/@{author.get('uniqueId','')}/video/{item.get('id','')}",
            "source": "rapidapi",
        })
    return results


def _tiktok_scrape_trending(max_results: int) -> list[dict]:
    """Scrape TikTok discover page for trending hashtags/sounds (HTML only)."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
        ),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }
    raw = _http_get("https://www.tiktok.com/trending", headers)
    if isinstance(raw, dict) and "error" in raw:
        return [{"platform": "tiktok", "source": "scrape", **raw}]

    import re
    # Extract hashtag names from page
    tags = re.findall(r'"hashtagName"\s*:\s*"([^"]+)"', raw or "")
    seen: set[str] = set()
    results = []
    for tag in tags:
        if tag in seen:
            continue
        seen.add(tag)
        results.append({
            "platform": "tiktok",
            "type": "hashtag",
            "name": tag,
            "url": f"https://www.tiktok.com/tag/{tag}",
            "source": "scrape_html",
            "note": "Set TIKTOK_RAPIDAPI_KEY for video-level trending data",
        })
        if len(results) >= max_results:
            break
    return results or [{
        "platform": "tiktok",
        "source": "scrape_html",
        "note": "TikTok blocked the scrape. Set TIKTOK_RAPIDAPI_KEY for reliable data.",
    }]


# ── YouTube search (for hashtag/sound research) ───────────────────────────────

def search_youtube(query: str, max_results: int = 10) -> list[dict]:
    api_key = os.environ.get("YOUTUBE_API_KEY", "")
    if not api_key:
        return [{"error": "YOUTUBE_API_KEY not set — cannot search YouTube API"}]
    params = urllib.parse.urlencode({
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "viewCount",
        "maxResults": min(max_results, 50),
        "key": api_key,
    })
    data = _http_get(f"{YT_API_BASE}/search?{params}")
    if not isinstance(data, dict) or "items" not in data:
        return [{"error": str(data)}]
    results = []
    for item in data["items"]:
        snip = item.get("snippet", {})
        vid_id = item.get("id", {}).get("videoId", "")
        results.append({
            "platform": "youtube",
            "id": vid_id,
            "title": snip.get("title", ""),
            "channel": snip.get("channelTitle", ""),
            "published_at": snip.get("publishedAt", ""),
            "description": snip.get("description", "")[:200],
            "url": f"https://www.youtube.com/watch?v={vid_id}",
            "source": "youtube_search",
        })
    return results


# ── TikTok hashtag search ─────────────────────────────────────────────────────

def search_tiktok_hashtag(hashtag: str) -> dict:
    rapid_key = os.environ.get("TIKTOK_RAPIDAPI_KEY", "")
    if not rapid_key:
        return {"error": "TIKTOK_RAPIDAPI_KEY not set"}
    headers = {
        "x-rapidapi-key": rapid_key,
        "x-rapidapi-host": TIKTOK_RAPID_HOST,
    }
    encoded = urllib.parse.quote(hashtag.lstrip("#"))
    data = _http_get(f"{TIKTOK_RAPID_BASE}/hashtag/info?name={encoded}", headers)
    if not isinstance(data, dict):
        return {"error": str(data)}
    challenge = data.get("challengeInfo", {}).get("challenge", {})
    stats = data.get("challengeInfo", {}).get("stats", {})
    return {
        "platform": "tiktok",
        "hashtag": hashtag,
        "view_count": stats.get("viewCount", 0),
        "video_count": stats.get("videoCount", 0),
        "title": challenge.get("title", ""),
        "description": challenge.get("desc", ""),
    }
