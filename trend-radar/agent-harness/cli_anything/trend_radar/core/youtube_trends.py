"""YouTube Trends — YouTube Data API v3 integration for trend intelligence.

Requires a free YouTube Data API v3 key:
  https://console.cloud.google.com → Enable YouTube Data API v3
  Set YOUTUBE_API_KEY env var or pass --api-key to each command.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from cli_anything.trend_radar.utils.trend_backend import TrendBackend

YT_API_BASE = "https://www.googleapis.com/youtube/v3"

# YouTube video category name → category ID
CATEGORY_IDS: dict[str, str | None] = {
    "all":           None,
    "film":          "1",
    "autos":         "2",
    "music":         "10",
    "pets":          "15",
    "sports":        "17",
    "travel":        "19",
    "gaming":        "20",
    "entertainment": "24",
    "news":          "25",
    "howto":         "26",
    "education":     "27",
    "science":       "28",
    "tech":          "28",
    "food":          "26",
    "fashion":       "26",
}


class YouTubeTrends:
    """Fetch trending videos, hashtags, and music from YouTube Data API v3."""

    def __init__(self):
        self._backend = TrendBackend()

    # ── Public API ────────────────────────────────────────────────────

    def get_trending(
        self,
        region: str = "US",
        category: str = "all",
        limit: int = 20,
        api_key: str | None = None,
    ) -> list[dict]:
        """Fetch currently trending YouTube videos.

        Returns list of dicts: video_id, title, channel, views, likes,
        comments, published_at, thumbnail_url, tags.
        """
        key = self._require_key(api_key)
        cat_id = CATEGORY_IDS.get(category.lower())
        params: dict[str, Any] = {
            "part": "snippet,statistics",
            "chart": "mostPopular",
            "regionCode": region.upper(),
            "maxResults": min(limit, 50),
            "key": key,
        }
        if cat_id:
            params["videoCategoryId"] = cat_id

        data = self._backend.get(f"{YT_API_BASE}/videos", params=params)
        return [self._parse_video(item) for item in data.get("items", [])]

    def get_trending_hashtags(
        self,
        niche: str,
        region: str = "US",
        limit: int = 25,
        api_key: str | None = None,
    ) -> list[dict]:
        """Find trending hashtags for a niche by aggregating tags from top videos.

        Returns list of dicts: tag, video_count, avg_views, score.
        """
        key = self._require_key(api_key)

        # Search top videos for the niche in the past 30 days
        search_params = {
            "part": "id",
            "q": niche,
            "type": "video",
            "order": "viewCount",
            "regionCode": region.upper(),
            "maxResults": 50,
            "publishedAfter": _days_ago(30),
            "key": key,
        }
        search_data = self._backend.get(f"{YT_API_BASE}/search", params=search_params)
        video_ids = [
            i["id"]["videoId"]
            for i in search_data.get("items", [])
            if i.get("id", {}).get("videoId")
        ]
        if not video_ids:
            return []

        # Fetch full stats + tags for those videos
        stats_data = self._backend.get(f"{YT_API_BASE}/videos", params={
            "part": "snippet,statistics",
            "id": ",".join(video_ids[:50]),
            "key": key,
        })

        # Aggregate tags weighted by view count
        tag_agg: dict[str, dict] = {}
        for item in stats_data.get("items", []):
            views = int(item.get("statistics", {}).get("viewCount", 0))
            for raw_tag in item.get("snippet", {}).get("tags", []):
                tag = raw_tag.lower().strip().replace(" ", "_").replace("#", "")
                if len(tag) > 2:
                    if tag not in tag_agg:
                        tag_agg[tag] = {"video_count": 0, "total_views": 0}
                    tag_agg[tag]["video_count"] += 1
                    tag_agg[tag]["total_views"] += views

        results = []
        for tag, agg in sorted(tag_agg.items(), key=lambda x: -x[1]["total_views"]):
            vc = agg["video_count"]
            tv = agg["total_views"]
            results.append({
                "tag": tag,
                "video_count": vc,
                "avg_views": tv // vc if vc else 0,
                "score": min(100, int((tv / 1_000_000) * 10 + vc * 5)),
            })
        return results[:limit]

    def get_trending_music(
        self,
        region: str = "US",
        limit: int = 20,
        api_key: str | None = None,
    ) -> list[dict]:
        """Get trending music videos from YouTube Music category."""
        return self.get_trending(region=region, category="music", limit=limit, api_key=api_key)

    # ── Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _require_key(api_key: str | None) -> str:
        k = api_key or os.environ.get("YOUTUBE_API_KEY", "")
        if not k:
            raise RuntimeError(
                "YouTube API key required.\n"
                "  1. Set env var: export YOUTUBE_API_KEY=AIza...\n"
                "  2. Or pass:     --api-key AIza...\n"
                "  Get a free key: https://console.cloud.google.com → Enable YouTube Data API v3"
            )
        return k

    @staticmethod
    def _parse_video(item: dict) -> dict:
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        return {
            "video_id":      item.get("id", ""),
            "title":         snippet.get("title", ""),
            "channel":       snippet.get("channelTitle", ""),
            "description":   snippet.get("description", "")[:200],
            "published_at":  snippet.get("publishedAt", ""),
            "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "tags":          snippet.get("tags", [])[:10],
            "views":         int(stats.get("viewCount", 0)),
            "likes":         int(stats.get("likeCount", 0)),
            "comments":      int(stats.get("commentCount", 0)),
            "category_id":   snippet.get("categoryId", ""),
        }


def _days_ago(days: int) -> str:
    """Return ISO 8601 timestamp for N days ago (UTC)."""
    dt = datetime.now(timezone.utc) - timedelta(days=days)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
