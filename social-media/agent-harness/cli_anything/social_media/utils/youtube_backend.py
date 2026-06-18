"""YouTube backend — wraps YouTube Data API v3 and youtubesearchpython fallback."""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

# ── Config ────────────────────────────────────────────────────────────────────

_CONFIG_PATH = Path.home() / ".cli-anything-social" / "youtube_config.json"
_CACHE_PATH = Path.home() / ".cli-anything-social" / "youtube_cache.json"

_YT_CATEGORY_MAP = {
    "music": "10",
    "gaming": "20",
    "entertainment": "24",
    "news": "25",
    "howto": "26",
    "sports": "17",
    "comedy": "23",
    "film": "1",
    "autos": "2",
    "science": "28",
    "travel": "19",
    "fashion": "26",
    "food": "26",
    "fitness": "17",
    "education": "27",
    "tech": "28",
    "beauty": "26",
    "pets": "15",
    "vlogs": "22",
    "dance": "10",
}


class YouTubeBackend:
    """Wraps YouTube Data API v3. Falls back to youtubesearchpython if no key."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("YOUTUBE_API_KEY") or self._load_key()
        self._base = "https://www.googleapis.com/youtube/v3"
        _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

    # ── Auth ──────────────────────────────────────────────────────────────────

    def _load_key(self) -> str | None:
        if _CONFIG_PATH.exists():
            try:
                return json.loads(_CONFIG_PATH.read_text()).get("api_key")
            except Exception:
                return None
        return None

    def save_key(self, api_key: str):
        _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        _CONFIG_PATH.write_text(json.dumps({"api_key": api_key}, indent=2))
        self.api_key = api_key

    def is_configured(self) -> bool:
        return bool(self.api_key)

    # ── Trending Videos ───────────────────────────────────────────────────────

    def get_trending_videos(
        self,
        region: str = "US",
        category: str = "all",
        max_results: int = 25,
    ) -> list[dict]:
        """Fetch trending videos. Uses official API if key configured, else fallback."""
        if self.api_key:
            return self._trending_api(region, category, max_results)
        return self._trending_fallback(category, max_results)

    def _trending_api(self, region: str, category: str, max_results: int) -> list[dict]:
        cat_id = _YT_CATEGORY_MAP.get(category.lower(), "") if category != "all" else ""
        params: dict[str, Any] = {
            "part": "snippet,statistics,contentDetails",
            "chart": "mostPopular",
            "regionCode": region.upper(),
            "maxResults": min(max_results, 50),
            "key": self.api_key,
        }
        if cat_id:
            params["videoCategoryId"] = cat_id

        resp = requests.get(f"{self._base}/videos", params=params, timeout=10)
        resp.raise_for_status()
        items = resp.json().get("items", [])
        return [self._normalize_video(v) for v in items]

    def _trending_fallback(self, category: str, max_results: int) -> list[dict]:
        """Use youtubesearchpython (no API key required)."""
        try:
            from youtubesearchpython import VideosSearch
            query = f"trending {category}" if category != "all" else "trending 2024"
            vs = VideosSearch(query, limit=max_results)
            results = vs.result().get("result", [])
            return [self._normalize_search_result(r) for r in results]
        except ImportError:
            return self._trending_web_fallback(max_results)

    def _trending_web_fallback(self, max_results: int) -> list[dict]:
        """Minimal web fallback — returns empty with a note."""
        return [{
            "id": "no_api_key",
            "title": "Configure YouTube API key for trend data",
            "channel": "cli-anything-social",
            "views": 0,
            "likes": 0,
            "published": datetime.now(timezone.utc).isoformat(),
            "tags": [],
            "description": "Run: cli-anything-social auth youtube --api-key YOUR_KEY",
            "url": "https://console.cloud.google.com/apis/library/youtube.googleapis.com",
            "thumbnail": "",
            "duration": "",
        }]

    def _normalize_video(self, v: dict) -> dict:
        snip = v.get("snippet", {})
        stats = v.get("statistics", {})
        return {
            "id": v.get("id", ""),
            "title": snip.get("title", ""),
            "channel": snip.get("channelTitle", ""),
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "published": snip.get("publishedAt", ""),
            "tags": snip.get("tags", []),
            "description": snip.get("description", "")[:200],
            "url": f"https://www.youtube.com/watch?v={v.get('id', '')}",
            "thumbnail": snip.get("thumbnails", {}).get("high", {}).get("url", ""),
            "duration": v.get("contentDetails", {}).get("duration", ""),
        }

    def _normalize_search_result(self, r: dict) -> dict:
        views_raw = r.get("viewCount", {})
        views = 0
        if isinstance(views_raw, dict):
            views_str = views_raw.get("text", "0").replace(",", "").split()[0]
            try:
                views = int(views_str)
            except (ValueError, IndexError):
                views = 0
        return {
            "id": r.get("id", ""),
            "title": r.get("title", ""),
            "channel": r.get("channel", {}).get("name", ""),
            "views": views,
            "likes": 0,
            "comments": 0,
            "published": r.get("publishedTime", ""),
            "tags": [],
            "description": r.get("descriptionSnippet", [{}])[0].get("text", "") if r.get("descriptionSnippet") else "",
            "url": r.get("link", ""),
            "thumbnail": r.get("thumbnails", [{}])[0].get("url", "") if r.get("thumbnails") else "",
            "duration": r.get("duration", ""),
        }

    # ── Search ────────────────────────────────────────────────────────────────

    def search_videos(
        self,
        query: str,
        order: str = "viewCount",
        max_results: int = 20,
        region: str = "US",
    ) -> list[dict]:
        if not self.api_key:
            try:
                from youtubesearchpython import VideosSearch
                vs = VideosSearch(query, limit=max_results)
                return [self._normalize_search_result(r) for r in vs.result().get("result", [])]
            except ImportError:
                return []

        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "order": order,
            "maxResults": min(max_results, 50),
            "regionCode": region,
            "key": self.api_key,
        }
        resp = requests.get(f"{self._base}/search", params=params, timeout=10)
        resp.raise_for_status()
        items = resp.json().get("items", [])

        video_ids = [i["id"]["videoId"] for i in items if i.get("id", {}).get("videoId")]
        if not video_ids:
            return []

        stats_params = {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(video_ids),
            "key": self.api_key,
        }
        stats_resp = requests.get(f"{self._base}/videos", params=stats_params, timeout=10)
        stats_resp.raise_for_status()
        return [self._normalize_video(v) for v in stats_resp.json().get("items", [])]

    # ── Trending Hashtags (derived from video tags) ───────────────────────────

    def get_trending_hashtags(
        self,
        region: str = "US",
        category: str = "all",
        top_n: int = 30,
    ) -> list[dict]:
        """Derive trending hashtags from tags on the most-viewed videos."""
        videos = self.get_trending_videos(region=region, category=category, max_results=50)
        tag_counts: dict[str, int] = {}
        tag_views: dict[str, int] = {}
        for v in videos:
            for tag in v.get("tags", []):
                t = tag.lower().strip().lstrip("#")
                if not t or len(t) < 2:
                    continue
                tag_counts[t] = tag_counts.get(t, 0) + 1
                tag_views[t] = tag_views.get(t, 0) + v.get("views", 0)

        ranked = sorted(tag_counts.items(), key=lambda x: (x[1], tag_views.get(x[0], 0)), reverse=True)
        return [
            {
                "hashtag": f"#{tag}",
                "video_count": count,
                "total_views": tag_views.get(tag, 0),
                "score": round(count * 0.4 + (tag_views.get(tag, 0) / 1_000_000) * 0.6, 2),
            }
            for tag, count in ranked[:top_n]
        ]

    # ── Trending Music ────────────────────────────────────────────────────────

    def get_trending_music(self, region: str = "US", max_results: int = 25) -> list[dict]:
        """Get trending music videos specifically."""
        return self.get_trending_videos(region=region, category="music", max_results=max_results)

    # ── Cache ─────────────────────────────────────────────────────────────────

    def cache_results(self, key: str, data: list) -> None:
        cache = {}
        if _CACHE_PATH.exists():
            try:
                cache = json.loads(_CACHE_PATH.read_text())
            except Exception:
                cache = {}
        cache[key] = {"data": data, "timestamp": time.time()}
        _CACHE_PATH.write_text(json.dumps(cache, indent=2))

    def load_cache(self, key: str, max_age_seconds: int = 3600) -> list | None:
        if not _CACHE_PATH.exists():
            return None
        try:
            cache = json.loads(_CACHE_PATH.read_text())
            entry = cache.get(key)
            if entry and (time.time() - entry["timestamp"]) < max_age_seconds:
                return entry["data"]
        except Exception:
            pass
        return None
