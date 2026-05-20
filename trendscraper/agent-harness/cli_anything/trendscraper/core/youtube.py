"""YouTube trend scraper — trending videos, hashtags, and music via YouTube Data API v3.

Requires a Google API key with YouTube Data API v3 enabled.
Get one at: https://console.cloud.google.com/apis/credentials

Set via:
    trendscraper config set --youtube-api-key YOUR_KEY
    or: export YOUTUBE_API_KEY=YOUR_KEY
"""
from __future__ import annotations

import os
import re
import json
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from collections import Counter

import httpx

_CACHE_DIR = Path.home() / ".config" / "cli-anything-trendscraper" / "cache"
_CACHE_TTL_SECONDS = 3600  # 1 hour

YOUTUBE_CATEGORIES = {
    "1": "Film & Animation",
    "2": "Autos & Vehicles",
    "10": "Music",
    "15": "Pets & Animals",
    "17": "Sports",
    "20": "Gaming",
    "22": "People & Blogs",
    "23": "Comedy",
    "24": "Entertainment",
    "25": "News & Politics",
    "26": "Howto & Style",
    "27": "Education",
    "28": "Science & Technology",
    "29": "Nonprofits & Activism",
}

# Top regions for trend analysis
REGIONS = {
    "US": "United States",
    "GB": "United Kingdom",
    "AU": "Australia",
    "CA": "Canada",
    "IN": "India",
    "BR": "Brazil",
    "DE": "Germany",
    "FR": "France",
    "JP": "Japan",
    "KR": "South Korea",
}


def _get_api_key() -> str | None:
    key = os.environ.get("YOUTUBE_API_KEY")
    if key:
        return key
    cfg_file = Path.home() / ".config" / "cli-anything-trendscraper" / "config.json"
    if cfg_file.exists():
        cfg = json.loads(cfg_file.read_text())
        return cfg.get("youtube_api_key")
    return None


def _cache_path(key: str) -> Path:
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    h = hashlib.md5(key.encode()).hexdigest()
    return _CACHE_DIR / f"yt_{h}.json"


def _load_cache(key: str) -> dict | None:
    p = _cache_path(key)
    if not p.exists():
        return None
    data = json.loads(p.read_text())
    if time.time() - data.get("_cached_at", 0) > _CACHE_TTL_SECONDS:
        return None
    return data


def _save_cache(key: str, data: dict) -> None:
    data["_cached_at"] = time.time()
    _cache_path(key).write_text(json.dumps(data, indent=2))


def _extract_hashtags(text: str) -> list[str]:
    """Pull #hashtags from a video description or title."""
    return [tag.lower() for tag in re.findall(r"#(\w+)", text or "")]


def _extract_music_mentions(title: str, description: str, tags: list[str]) -> list[str]:
    """Heuristically detect music/song references from video metadata."""
    music_patterns = [
        r"(?:official\s+(?:audio|music|video|mv))",
        r"(?:ft\.?|feat\.?)\s+([\w\s]+?)(?:\s*[\|\-\(\[]|$)",
        r"(?:prod\.?|produced\s+by)\s+([\w\s]+?)(?:\s*[\|\-\(\[]|$)",
    ]
    combined = f"{title} {description or ''}"
    mentions = []
    for pat in music_patterns:
        m = re.search(pat, combined, re.IGNORECASE)
        if m and m.lastindex:
            mentions.append(m.group(1).strip())
    for tag in (tags or []):
        if any(w in tag.lower() for w in ["music", "song", "remix", "beat", "official"]):
            mentions.append(tag)
    return list(dict.fromkeys(mentions))  # deduplicate preserving order


def fetch_trending_videos(
    region: str = "US",
    category_id: str = "",
    max_results: int = 50,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Fetch trending YouTube videos for a region/category.

    Returns a dict with keys: videos, hashtags, music, fetched_at, region.
    Works without API key using a lightweight scrape fallback (limited data).
    """
    key = api_key or _get_api_key()
    cache_key = f"trending_{region}_{category_id}_{max_results}"
    cached = _load_cache(cache_key)
    if cached:
        return cached

    if key:
        result = _fetch_via_api(key, region, category_id, max_results)
    else:
        result = _fetch_via_scrape(region, max_results)

    _save_cache(cache_key, result)
    return result


def _fetch_via_api(
    api_key: str,
    region: str,
    category_id: str,
    max_results: int,
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": min(max_results, 50),
        "key": api_key,
    }
    if category_id:
        params["videoCategoryId"] = category_id

    with httpx.Client(timeout=30) as client:
        resp = client.get("https://www.googleapis.com/youtube/v3/videos", params=params)
        resp.raise_for_status()
        data = resp.json()

    videos = []
    all_hashtags: list[str] = []
    all_music: list[str] = []

    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        tags = snippet.get("tags", [])
        description = snippet.get("description", "")
        title = snippet.get("title", "")

        hashtags = _extract_hashtags(f"{title} {description}")
        for tag in tags:
            if tag.startswith("#"):
                hashtags.append(tag[1:].lower())
        music = _extract_music_mentions(title, description, tags)

        video = {
            "id": item.get("id"),
            "title": title,
            "channel": snippet.get("channelTitle"),
            "published_at": snippet.get("publishedAt"),
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "category_id": snippet.get("categoryId"),
            "tags": tags[:20],
            "hashtags": hashtags,
            "music": music,
            "thumbnail": (snippet.get("thumbnails", {}).get("high", {}) or {}).get("url"),
            "url": f"https://youtube.com/watch?v={item.get('id')}",
        }
        videos.append(video)
        all_hashtags.extend(hashtags)
        all_music.extend(music)

    hashtag_counts = Counter(all_hashtags).most_common(30)
    music_counts = Counter(all_music).most_common(20)

    return {
        "platform": "youtube",
        "region": region,
        "fetched_at": datetime.utcnow().isoformat(),
        "video_count": len(videos),
        "videos": videos,
        "trending_hashtags": [{"tag": h, "count": c} for h, c in hashtag_counts],
        "trending_music": [{"title": m, "count": c} for m, c in music_counts],
        "source": "youtube_data_api_v3",
    }


def _fetch_via_scrape(region: str, max_results: int) -> dict[str, Any]:
    """Lightweight scrape of YouTube trending page (no API key required)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    gl_map = {"US": "US", "GB": "GB", "AU": "AU", "CA": "CA", "IN": "IN"}
    gl = gl_map.get(region, "US")

    try:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            resp = client.get(
                "https://www.youtube.com/feed/trending",
                headers=headers,
                params={"gl": gl},
            )
            html = resp.text

        # Extract ytInitialData JSON blob
        match = re.search(r"var ytInitialData\s*=\s*(\{.+?\});</script>", html, re.DOTALL)
        if not match:
            return _empty_result("youtube", region, "scrape_no_data")

        raw = json.loads(match.group(1))
        videos = _parse_yt_initial_data(raw, max_results)
    except Exception as exc:
        return _empty_result("youtube", region, f"scrape_error: {exc}")

    all_hashtags: list[str] = []
    all_music: list[str] = []
    for v in videos:
        all_hashtags.extend(v.get("hashtags", []))
        all_music.extend(v.get("music", []))

    return {
        "platform": "youtube",
        "region": region,
        "fetched_at": datetime.utcnow().isoformat(),
        "video_count": len(videos),
        "videos": videos,
        "trending_hashtags": [{"tag": h, "count": c} for h, c in Counter(all_hashtags).most_common(30)],
        "trending_music": [{"title": m, "count": c} for m, c in Counter(all_music).most_common(20)],
        "source": "youtube_scrape",
    }


def _parse_yt_initial_data(data: dict, limit: int) -> list[dict]:
    """Walk ytInitialData to extract video renderer items."""
    videos = []
    try:
        tabs = (
            data.get("contents", {})
            .get("twoColumnBrowseResultsRenderer", {})
            .get("tabs", [])
        )
        for tab in tabs:
            tab_content = tab.get("tabRenderer", {}).get("content", {})
            section_list = tab_content.get("sectionListRenderer", {}).get("contents", [])
            for section in section_list:
                items = (
                    section.get("itemSectionRenderer", {}).get("contents", [])
                    or section.get("shelfRenderer", {}).get("content", {})
                    .get("expandedShelfContentsRenderer", {}).get("items", [])
                )
                for item in items:
                    vr = item.get("videoRenderer") or item.get("compactVideoRenderer")
                    if not vr:
                        continue
                    vid_id = vr.get("videoId", "")
                    title = _get_text(vr.get("title"))
                    channel = _get_text(vr.get("ownerText") or vr.get("longBylineText"))
                    views_raw = _get_text(vr.get("viewCountText") or vr.get("shortViewCountText"))
                    hashtags = _extract_hashtags(title)
                    music = _extract_music_mentions(title, "", [])
                    videos.append({
                        "id": vid_id,
                        "title": title,
                        "channel": channel,
                        "views_raw": views_raw,
                        "views": _parse_view_count(views_raw),
                        "hashtags": hashtags,
                        "music": music,
                        "url": f"https://youtube.com/watch?v={vid_id}" if vid_id else "",
                    })
                    if len(videos) >= limit:
                        return videos
    except Exception:
        pass
    return videos


def _get_text(node: Any) -> str:
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        runs = node.get("runs")
        if runs and isinstance(runs, list):
            return "".join(r.get("text", "") for r in runs)
        return node.get("simpleText", "")
    return ""


def _parse_view_count(raw: str) -> int:
    if not raw:
        return 0
    raw = raw.replace(",", "").replace(" views", "").strip()
    multipliers = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}
    for suffix, mult in multipliers.items():
        if raw.upper().endswith(suffix):
            try:
                return int(float(raw[:-1]) * mult)
            except ValueError:
                return 0
    try:
        return int(raw)
    except ValueError:
        return 0


def _empty_result(platform: str, region: str, reason: str) -> dict:
    return {
        "platform": platform,
        "region": region,
        "fetched_at": datetime.utcnow().isoformat(),
        "video_count": 0,
        "videos": [],
        "trending_hashtags": [],
        "trending_music": [],
        "source": reason,
        "error": reason,
    }


def fetch_trending_music(region: str = "US", api_key: str | None = None) -> dict[str, Any]:
    """Fetch trending music from the YouTube Music category (category_id=10)."""
    return fetch_trending_videos(region=region, category_id="10", max_results=50, api_key=api_key)


def search_hashtag_videos(
    hashtag: str,
    max_results: int = 20,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Search YouTube for videos using a specific hashtag."""
    key = api_key or _get_api_key()
    if not key:
        return _empty_result("youtube", "global", "api_key_required_for_search")

    with httpx.Client(timeout=30) as client:
        resp = client.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet",
                "q": f"#{hashtag}",
                "type": "video",
                "order": "viewCount",
                "maxResults": min(max_results, 50),
                "key": key,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    videos = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        vid_id = item.get("id", {}).get("videoId", "")
        title = snippet.get("title", "")
        videos.append({
            "id": vid_id,
            "title": title,
            "channel": snippet.get("channelTitle"),
            "published_at": snippet.get("publishedAt"),
            "thumbnail": (snippet.get("thumbnails", {}).get("high", {}) or {}).get("url"),
            "url": f"https://youtube.com/watch?v={vid_id}",
            "hashtags": _extract_hashtags(f"{title} {snippet.get('description', '')}"),
        })

    return {
        "platform": "youtube",
        "query_hashtag": hashtag,
        "fetched_at": datetime.utcnow().isoformat(),
        "video_count": len(videos),
        "videos": videos,
        "source": "youtube_search_api",
    }
