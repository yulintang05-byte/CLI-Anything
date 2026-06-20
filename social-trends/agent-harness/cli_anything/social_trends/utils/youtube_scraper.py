"""YouTube trending scraper — videos, music, and category trends.

Supports two modes:
  1. YouTube Data API v3 (requires YOUTUBE_API_KEY) — structured, reliable.
  2. HTML scrape of youtube.com/feed/trending (no key needed) — fallback.
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone
from typing import Any

try:
    import requests
except ImportError:
    import sys
    print("requests library not found. Install with: pip install requests", file=sys.stderr)
    raise

YT_API_BASE = "https://www.googleapis.com/youtube/v3"

CATEGORY_IDS = {
    "music": "10",
    "gaming": "20",
    "entertainment": "24",
    "news": "25",
    "howto": "26",
    "sports": "17",
    "film": "1",
    "comedy": "23",
    "education": "27",
    "science": "28",
    "travel": "19",
    "fashion": "22",
    "food": "22",
}

REGION_CODES = {
    "us": "US", "uk": "GB", "ca": "CA", "au": "AU",
    "de": "DE", "fr": "FR", "jp": "JP", "br": "BR",
    "in": "IN", "mx": "MX", "id": "ID", "ph": "PH",
    "kr": "KR", "ng": "NG", "za": "ZA",
}

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


# ── API v3 (requires key) ─────────────────────────────────────────────

def _api_get(endpoint: str, params: dict, api_key: str) -> dict:
    params["key"] = api_key
    resp = requests.get(f"{YT_API_BASE}/{endpoint}", params=params, timeout=15)
    if resp.status_code == 403:
        raise RuntimeError(
            "YouTube API quota exceeded or key invalid. "
            "Set YOUTUBE_API_KEY or use --api-key."
        )
    if resp.status_code != 200:
        raise RuntimeError(
            f"YouTube API error (HTTP {resp.status_code}): {resp.text[:200]}"
        )
    return resp.json()


def trending_videos_api(
    api_key: str,
    region: str = "US",
    category: str | None = None,
    limit: int = 25,
) -> list[dict]:
    """Fetch trending videos via YouTube Data API v3.

    Args:
        api_key: YouTube Data API v3 key.
        region: Region code (US, GB, CA, AU...).
        category: Optional category filter (music, gaming, entertainment...).
        limit: Max results (max 50 per page).

    Returns:
        List of video dicts with title, channel, views, likes, tags, etc.
    """
    region = region.upper()
    params: dict[str, Any] = {
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": min(limit, 50),
    }
    if category and category.lower() in CATEGORY_IDS:
        params["videoCategoryId"] = CATEGORY_IDS[category.lower()]

    data = _api_get("videos", params, api_key)
    items = data.get("items", [])
    results = []
    for i, item in enumerate(items):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        content = item.get("contentDetails", {})
        results.append({
            "rank": i + 1,
            "video_id": item.get("id", ""),
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "channel_id": snippet.get("channelId", ""),
            "description": snippet.get("description", "")[:200],
            "tags": snippet.get("tags", [])[:15],
            "category_id": snippet.get("categoryId", ""),
            "published_at": snippet.get("publishedAt", ""),
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
            "duration": content.get("duration", ""),
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "url": f"https://www.youtube.com/watch?v={item.get('id', '')}",
            "region": region,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        })
    return results[:limit]


def trending_music_api(
    api_key: str,
    region: str = "US",
    limit: int = 20,
) -> list[dict]:
    """Fetch trending music videos via YouTube Data API v3."""
    return trending_videos_api(api_key, region=region, category="music", limit=limit)


def search_trending_hashtag_api(
    api_key: str,
    hashtag: str,
    region: str = "US",
    limit: int = 10,
) -> list[dict]:
    """Search for videos using a specific hashtag via YouTube Data API v3."""
    params: dict[str, Any] = {
        "part": "snippet",
        "q": f"#{hashtag}",
        "type": "video",
        "order": "viewCount",
        "regionCode": region.upper(),
        "maxResults": min(limit, 50),
        "publishedAfter": "2026-01-01T00:00:00Z",
    }
    data = _api_get("search", params, api_key)
    items = data.get("items", [])
    results = []
    for i, item in enumerate(items):
        snippet = item.get("snippet", {})
        vid_id = item.get("id", {}).get("videoId", "")
        results.append({
            "rank": i + 1,
            "video_id": vid_id,
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "published_at": snippet.get("publishedAt", ""),
            "description": snippet.get("description", "")[:150],
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "url": f"https://www.youtube.com/watch?v={vid_id}",
            "hashtag": hashtag,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        })
    return results[:limit]


# ── HTML scrape (no key) ──────────────────────────────────────────────

def trending_videos_scrape(
    region: str = "US",
    limit: int = 25,
) -> list[dict]:
    """Scrape YouTube trending page without an API key.

    Extracts video data embedded in the page's initial data JSON blob.
    Note: YouTube's page structure changes periodically; this may break.

    Returns:
        List of video dicts (fewer fields than API version).
    """
    region = region.upper()
    url = "https://www.youtube.com/feed/trending"
    params = {"gl": region, "hl": "en"}

    try:
        resp = requests.get(url, params=params, headers=_HEADERS, timeout=20)
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch YouTube trending page: {e}")

    if resp.status_code != 200:
        raise RuntimeError(f"YouTube trending page returned HTTP {resp.status_code}")

    # Extract ytInitialData JSON blob embedded in page
    match = re.search(r"var ytInitialData\s*=\s*(\{.+?\});\s*</script>", resp.text, re.DOTALL)
    if not match:
        raise RuntimeError(
            "Could not extract ytInitialData from YouTube page. "
            "YouTube may have changed their page structure."
        )

    try:
        yt_data = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse ytInitialData JSON: {e}")

    videos = _extract_videos_from_yt_data(yt_data)
    results = []
    for i, v in enumerate(videos[:limit]):
        v["rank"] = i + 1
        v["region"] = region
        v["fetched_at"] = datetime.now(timezone.utc).isoformat()
        results.append(v)
    return results


def _extract_videos_from_yt_data(data: dict) -> list[dict]:
    """Traverse ytInitialData tree to find video renderers."""
    videos = []
    try:
        tabs = (
            data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]
        )
        for tab in tabs:
            tab_content = tab.get("tabRenderer", {}).get("content", {})
            sections = tab_content.get("sectionListRenderer", {}).get("contents", [])
            for section in sections:
                items = (
                    section.get("itemSectionRenderer", {})
                    .get("contents", [{}])[0]
                    .get("shelfRenderer", {})
                    .get("content", {})
                    .get("expandedShelfContentsRenderer", {})
                    .get("items", [])
                )
                for item in items:
                    vr = item.get("videoRenderer", {})
                    if not vr:
                        continue
                    vid_id = vr.get("videoId", "")
                    title_runs = vr.get("title", {}).get("runs", [])
                    title = title_runs[0].get("text", "") if title_runs else ""
                    channel_runs = (
                        vr.get("longBylineText", {}).get("runs", [])
                        or vr.get("shortBylineText", {}).get("runs", [])
                    )
                    channel = channel_runs[0].get("text", "") if channel_runs else ""
                    view_text = (
                        vr.get("viewCountText", {}).get("simpleText", "")
                        or vr.get("viewCountText", {}).get("runs", [{}])[0].get("text", "")
                    )
                    thumb = (
                        vr.get("thumbnail", {}).get("thumbnails", [{}])[-1].get("url", "")
                    )
                    videos.append({
                        "video_id": vid_id,
                        "title": title,
                        "channel": channel,
                        "view_count_text": view_text,
                        "thumbnail": thumb,
                        "url": f"https://www.youtube.com/watch?v={vid_id}",
                    })
    except (KeyError, IndexError, TypeError):
        pass
    return videos


# ── Unified interface ─────────────────────────────────────────────────

def trending_videos(
    region: str = "US",
    category: str | None = None,
    limit: int = 25,
    api_key: str | None = None,
) -> list[dict]:
    """Fetch trending videos — uses API if key available, else HTML scrape."""
    key = api_key or os.environ.get("YOUTUBE_API_KEY")
    if key:
        return trending_videos_api(key, region=region, category=category, limit=limit)
    return trending_videos_scrape(region=region, limit=limit)


def full_trend_report(
    region: str = "US",
    limit: int = 20,
    api_key: str | None = None,
    delay: float = 0.5,
) -> dict:
    """Consolidated YouTube trend report across key categories."""
    key = api_key or os.environ.get("YOUTUBE_API_KEY")
    report: dict[str, Any] = {
        "platform": "youtube",
        "region": region.upper(),
        "api_mode": "api_v3" if key else "html_scrape",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "trending_all": [],
        "trending_music": [],
        "errors": [],
    }

    try:
        report["trending_all"] = trending_videos(region=region, limit=limit, api_key=key)
    except Exception as e:
        report["errors"].append({"category": "trending_all", "error": str(e)})

    if key:
        time.sleep(delay)
        try:
            report["trending_music"] = trending_music_api(key, region=region, limit=limit)
        except Exception as e:
            report["errors"].append({"category": "trending_music", "error": str(e)})

    return report
