"""YouTube trending scraper — uses innertube (no key) or Data API v3 (with key)."""
from __future__ import annotations

import json
import re
import time
from typing import Any

import requests

# Public client key YouTube embeds in every web page (client-side, no auth)
_INNERTUBE_KEY = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
_INNERTUBE_URL = "https://www.youtube.com/youtubei/v1/browse"
_DATA_API_URL = "https://www.googleapis.com/youtube/v3/videos"

# YouTube category IDs
CATEGORIES = {
    "all": "0",
    "music": "10",
    "gaming": "20",
    "entertainment": "24",
    "news": "25",
    "sports": "17",
    "science": "28",
    "howto": "26",
    "film": "1",
}

REGION_CODES = {
    "us": "US", "uk": "GB", "ca": "CA", "au": "AU",
    "in": "IN", "br": "BR", "de": "DE", "fr": "FR",
    "jp": "JP", "kr": "KR", "mx": "MX", "ng": "NG",
}


def _innertube_context(region: str) -> dict:
    return {
        "client": {
            "clientName": "WEB",
            "clientVersion": "2.20240501.00.00",
            "gl": region.upper(),
            "hl": "en",
        }
    }


def _extract_text(obj: Any) -> str:
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        if "simpleText" in obj:
            return obj["simpleText"]
        if "runs" in obj:
            return "".join(r.get("text", "") for r in obj["runs"])
    return ""


def _parse_innertube_video(renderer: dict) -> dict | None:
    vid_id = renderer.get("videoId", "")
    if not vid_id:
        return None
    title = _extract_text(renderer.get("title", {}))
    channel = _extract_text(renderer.get("longBylineText", renderer.get("shortBylineText", {})))
    views = _extract_text(renderer.get("viewCountText", {}))
    duration = _extract_text(renderer.get("lengthText", {}))
    published = _extract_text(renderer.get("publishedTimeText", {}))
    description = _extract_text(renderer.get("descriptionSnippet", {}))
    badges = [
        _extract_text(b.get("metadataBadgeRenderer", {}).get("label", ""))
        for b in renderer.get("badges", [])
    ]
    return {
        "id": vid_id,
        "url": f"https://www.youtube.com/watch?v={vid_id}",
        "title": title,
        "channel": channel,
        "views": views,
        "duration": duration,
        "published": published,
        "description": description,
        "badges": [b for b in badges if b],
    }


def _walk_renderers(obj: Any, results: list, limit: int) -> None:
    if len(results) >= limit:
        return
    if isinstance(obj, dict):
        if "videoRenderer" in obj:
            v = _parse_innertube_video(obj["videoRenderer"])
            if v:
                results.append(v)
        else:
            for v in obj.values():
                _walk_renderers(v, results, limit)
    elif isinstance(obj, list):
        for item in obj:
            _walk_renderers(item, results, limit)


def scrape_youtube_trending(
    region: str = "US",
    category: str = "all",
    limit: int = 25,
    api_key: str | None = None,
    timeout: int = 30,
) -> dict:
    """
    Fetch YouTube trending videos.

    With api_key: uses official YouTube Data API v3.
    Without api_key: uses YouTube's innertube (no auth required).

    Returns dict with keys: region, category, videos, scraped_at, source.
    """
    region = REGION_CODES.get(region.lower(), region.upper())
    cat_id = CATEGORIES.get(category.lower(), category)

    if api_key:
        return _scrape_with_data_api(region, cat_id, limit, api_key, timeout)
    return _scrape_with_innertube(region, cat_id, limit, timeout)


def _scrape_with_innertube(region: str, category_id: str, limit: int, timeout: int) -> dict:
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-YouTube-Client-Name": "1",
        "X-YouTube-Client-Version": "2.20240501.00.00",
    }
    payload: dict = {
        "browseId": "FEtrending",
        "context": _innertube_context(region),
    }
    if category_id != "0":
        payload["params"] = _category_param(category_id)

    resp = requests.post(
        _INNERTUBE_URL,
        params={"key": _INNERTUBE_KEY},
        json=payload,
        headers=headers,
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()

    videos: list[dict] = []
    _walk_renderers(data, videos, limit)

    return {
        "region": region,
        "category": category_id,
        "videos": videos[:limit],
        "total": len(videos[:limit]),
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": "innertube",
    }


def _category_param(category_id: str) -> str:
    # Base64-encoded proto param for trending category filter
    params_map = {
        "10": "4gINGgtZTVVzaWMlMzQ%3D",   # Music
        "20": "4gINGgtZTUdhbWluZw%3D%3D",  # Gaming
        "24": "4gINGgtZTUVudGVydGFpbm1lbnQ%3D",  # Entertainment
        "25": "4gINGgtZTU5ld3M%3D",         # News
        "17": "4gINGgtZTVNwb3J0cw%3D%3D",  # Sports
    }
    return params_map.get(category_id, "")


def _scrape_with_data_api(
    region: str, category_id: str, limit: int, api_key: str, timeout: int
) -> dict:
    params: dict = {
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": min(limit, 50),
        "key": api_key,
    }
    if category_id != "0":
        params["videoCategoryId"] = category_id

    resp = requests.get(_DATA_API_URL, params=params, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    videos = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        content = item.get("contentDetails", {})
        vid_id = item.get("id", "")
        videos.append({
            "id": vid_id,
            "url": f"https://www.youtube.com/watch?v={vid_id}",
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "description": snippet.get("description", "")[:300],
            "published": snippet.get("publishedAt", ""),
            "tags": snippet.get("tags", []),
            "views": stats.get("viewCount", "0"),
            "likes": stats.get("likeCount", "0"),
            "comments": stats.get("commentCount", "0"),
            "duration": content.get("duration", ""),
            "category_id": snippet.get("categoryId", ""),
        })

    return {
        "region": region,
        "category": category_id,
        "videos": videos,
        "total": len(videos),
        "next_page_token": data.get("nextPageToken"),
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": "youtube_data_api_v3",
    }


def extract_hashtags_from_videos(videos: list[dict]) -> list[dict]:
    """Extract and rank hashtags from video titles, descriptions, and tags."""
    tag_counts: dict[str, int] = {}
    for v in videos:
        text = f"{v.get('title','')} {v.get('description','')} {' '.join(v.get('tags',[]))}"
        for tag in re.findall(r"#(\w+)", text):
            tag_lower = tag.lower()
            tag_counts[tag_lower] = tag_counts.get(tag_lower, 0) + 1
        for tag in v.get("tags", []):
            t = tag.lower().replace(" ", "")
            tag_counts[t] = tag_counts.get(t, 0) + 1

    return sorted(
        [{"tag": f"#{k}", "count": v} for k, v in tag_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )
