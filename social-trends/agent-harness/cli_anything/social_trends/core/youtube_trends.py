"""YouTube trend scraper.

Two modes:
  1. YouTube Data API v3  — high-quality, requires free API key.
  2. Web scrape fallback  — no key required, returns limited fields.

Configure your API key once:
    cli-anything-social-trends config set --youtube-api-key AIza...
"""

from __future__ import annotations

import re
from typing import Any

from cli_anything.social_trends.utils.scraper_backend import (
    get_html, get_json, load_config,
)

# ── YouTube Data API v3 ───────────────────────────────────────────────────────

_YT_API_BASE = "https://www.googleapis.com/youtube/v3"
_YT_TRENDING_URL = "https://www.youtube.com/feed/trending"
_YT_CATEGORY_IDS = {
    "all": "0",
    "music": "10",
    "gaming": "20",
    "film": "1",
    "news": "25",
    "sports": "17",
    "science": "28",
    "howto": "26",
    "travel": "19",
    "pets": "15",
    "entertainment": "24",
}


def _api_key() -> str | None:
    return load_config().get("youtube_api_key")


# ── API-based scraping ────────────────────────────────────────────────────────

def fetch_trending_videos_api(region: str = "US", category: str = "all",
                              max_results: int = 25) -> list[dict]:
    """Fetch trending videos via YouTube Data API v3."""
    key = _api_key()
    if not key:
        raise RuntimeError(
            "YouTube API key not configured. "
            "Run: cli-anything-social-trends config set --youtube-api-key <KEY>"
        )

    cat_id = _YT_CATEGORY_IDS.get(category.lower(), "0")
    params = {
        "part": "snippet,statistics,topicDetails",
        "chart": "mostPopular",
        "regionCode": region.upper(),
        "maxResults": max_results,
        "key": key,
    }
    if cat_id != "0":
        params["videoCategoryId"] = cat_id

    data = get_json(f"{_YT_API_BASE}/videos", params=params, cache_ttl=900)
    return [_parse_api_video(item) for item in data.get("items", [])]


def fetch_trending_hashtags_api(region: str = "US",
                                max_results: int = 25) -> list[dict]:
    """Extract trending hashtags from top videos."""
    videos = fetch_trending_videos_api(region=region, max_results=max_results)
    return _extract_hashtags(videos)


def fetch_trending_music_api(region: str = "US") -> list[dict]:
    """Fetch trending music videos via API."""
    return fetch_trending_videos_api(region=region, category="music", max_results=20)


def _parse_api_video(item: dict) -> dict:
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    return {
        "id": item.get("id", ""),
        "title": snippet.get("title", ""),
        "channel": snippet.get("channelTitle", ""),
        "published_at": snippet.get("publishedAt", ""),
        "description": snippet.get("description", "")[:500],
        "tags": snippet.get("tags", []),
        "category_id": snippet.get("categoryId", ""),
        "view_count": int(stats.get("viewCount", 0)),
        "like_count": int(stats.get("likeCount", 0)),
        "comment_count": int(stats.get("commentCount", 0)),
        "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
        "hashtags": _extract_tags_from_text(
            snippet.get("title", "") + " " + snippet.get("description", "")
        ),
        "source": "youtube_api",
    }


# ── Web-scrape fallback ───────────────────────────────────────────────────────

def fetch_trending_videos_web(region: str = "US",
                              max_results: int = 25) -> list[dict]:
    """Scrape YouTube trending page (no API key required).

    Returns limited metadata — use the API mode for full statistics.
    """
    url = f"{_YT_TRENDING_URL}?gl={region.upper()}"
    soup = get_html(url, cache_ttl=900)
    videos = []

    # YouTube inlines its initial data as a JSON blob inside a <script> tag
    for script in soup.find_all("script"):
        text = script.string or ""
        if "ytInitialData" in text:
            match = re.search(r"var ytInitialData\s*=\s*(\{.*?\});", text, re.DOTALL)
            if match:
                try:
                    import json
                    raw = json.loads(match.group(1))
                    videos = _parse_yt_initial_data(raw, max_results)
                except Exception:
                    pass
            break

    return videos or _scrape_yt_fallback(soup, max_results)


def _parse_yt_initial_data(data: dict, max_results: int) -> list[dict]:
    """Walk ytInitialData to extract video renderers."""
    results = []
    try:
        tabs = (data.get("contents", {})
                    .get("twoColumnBrowseResultsRenderer", {})
                    .get("tabs", []))
        for tab in tabs:
            sections = (tab.get("tabRenderer", {})
                           .get("content", {})
                           .get("sectionListRenderer", {})
                           .get("contents", []))
            for section in sections:
                items = (section.get("itemSectionRenderer", {})
                                .get("contents", [{}])[0]
                                .get("shelfRenderer", {})
                                .get("content", {})
                                .get("expandedShelfContentsRenderer", {})
                                .get("items", []))
                for item in items:
                    vr = item.get("videoRenderer", {})
                    if not vr:
                        continue
                    title = _text(vr.get("title", {}))
                    channel = _text(vr.get("ownerText", {}))
                    views = _text(vr.get("viewCountText", {}))
                    vid_id = vr.get("videoId", "")
                    results.append({
                        "id": vid_id,
                        "title": title,
                        "channel": channel,
                        "view_count_text": views,
                        "url": f"https://www.youtube.com/watch?v={vid_id}",
                        "hashtags": _extract_tags_from_text(title),
                        "source": "youtube_web",
                    })
                    if len(results) >= max_results:
                        return results
    except Exception:
        pass
    return results


def _scrape_yt_fallback(soup: Any, max_results: int) -> list[dict]:
    """Last-resort: grab any video links visible in the DOM."""
    results = []
    for a in soup.find_all("a", href=re.compile(r"/watch\?v=")):
        href = a.get("href", "")
        vid_id = re.search(r"v=([a-zA-Z0-9_-]{11})", href)
        if not vid_id:
            continue
        title = a.get("title") or a.get_text(strip=True)
        results.append({
            "id": vid_id.group(1),
            "title": title,
            "url": f"https://www.youtube.com{href}",
            "hashtags": _extract_tags_from_text(title),
            "source": "youtube_web_fallback",
        })
        if len(results) >= max_results:
            break
    return results


# ── Shared helpers ────────────────────────────────────────────────────────────

def _text(obj: dict) -> str:
    """Extract text from a YouTube renderer text object."""
    if "simpleText" in obj:
        return obj["simpleText"]
    runs = obj.get("runs", [])
    return "".join(r.get("text", "") for r in runs)


def _extract_tags_from_text(text: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"#(\w+)", text)))


def _extract_hashtags(videos: list[dict]) -> list[dict]:
    """Aggregate hashtag frequency across videos."""
    counts: dict[str, int] = {}
    for v in videos:
        tags = v.get("hashtags", []) + v.get("tags", [])
        for tag in tags:
            clean = tag.lower().strip()
            if clean:
                counts[clean] = counts.get(clean, 0) + 1

    return [
        {"hashtag": f"#{t}", "frequency": c}
        for t, c in sorted(counts.items(), key=lambda x: -x[1])
    ]


# ── Unified entry points ──────────────────────────────────────────────────────

def get_trending_videos(region: str = "US", category: str = "all",
                        max_results: int = 25) -> list[dict]:
    """Auto-select API or web fallback based on config."""
    if _api_key():
        return fetch_trending_videos_api(region, category, max_results)
    return fetch_trending_videos_web(region, max_results)


def get_trending_hashtags(region: str = "US",
                          max_results: int = 25) -> list[dict]:
    videos = get_trending_videos(region, max_results=max_results)
    return _extract_hashtags(videos)


def get_trending_music(region: str = "US") -> list[dict]:
    if _api_key():
        return fetch_trending_music_api(region)
    return fetch_trending_videos_web(region, max_results=20)
