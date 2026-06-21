"""YouTube Trends — Fetch trending videos, hashtags, and music via YouTube Data API v3."""

import os
import json
import time
import requests
from datetime import datetime, timezone
from typing import Optional


_BASE = "https://www.googleapis.com/youtube/v3"
_DEFAULT_REGION = "US"
_DEFAULT_MAX = 50


class YouTubeTrendsError(Exception):
    pass


class YouTubeTrendsClient:
    def __init__(self, api_key: str, region_code: str = _DEFAULT_REGION):
        if not api_key:
            raise YouTubeTrendsError("YouTube Data API key is required. Set YOUTUBE_API_KEY env var.")
        self.api_key = api_key
        self.region_code = region_code
        self._session = requests.Session()
        self._session.params = {"key": self.api_key}

    def _get(self, endpoint: str, params: dict) -> dict:
        url = f"{_BASE}/{endpoint}"
        resp = self._session.get(url, params=params, timeout=15)
        if resp.status_code == 403:
            raise YouTubeTrendsError("YouTube API quota exceeded or key invalid.")
        if resp.status_code == 400:
            body = resp.json()
            msg = body.get("error", {}).get("message", "Bad request")
            raise YouTubeTrendsError(f"YouTube API error: {msg}")
        resp.raise_for_status()
        return resp.json()

    def trending_videos(self, category_id: str = "0", max_results: int = 25) -> list[dict]:
        """Fetch trending videos. category_id 0=all, 10=music, 17=sports, 24=entertainment."""
        data = self._get("videos", {
            "part": "snippet,statistics,topicDetails",
            "chart": "mostPopular",
            "regionCode": self.region_code,
            "videoCategoryId": category_id,
            "maxResults": min(max_results, 50),
        })
        results = []
        for item in data.get("items", []):
            s = item["snippet"]
            stats = item.get("statistics", {})
            results.append({
                "id": item["id"],
                "title": s["title"],
                "channel": s["channelTitle"],
                "published_at": s["publishedAt"],
                "description": s.get("description", "")[:200],
                "tags": s.get("tags", [])[:20],
                "category_id": s.get("categoryId", ""),
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
                "thumbnail": s.get("thumbnails", {}).get("high", {}).get("url", ""),
                "url": f"https://youtube.com/watch?v={item['id']}",
            })
        return results

    def trending_hashtags(self, max_videos: int = 50) -> list[dict]:
        """Extract trending hashtags from top trending videos."""
        videos = self.trending_videos(max_results=max_videos)
        tag_counts: dict[str, int] = {}
        tag_views: dict[str, int] = {}
        for v in videos:
            for tag in v["tags"]:
                tag_lower = tag.lower().strip()
                if not tag_lower:
                    continue
                tag_counts[tag_lower] = tag_counts.get(tag_lower, 0) + 1
                tag_views[tag_lower] = tag_views.get(tag_lower, 0) + v["view_count"]

        ranked = sorted(
            [{"hashtag": f"#{t}", "appearances": c, "total_views": tag_views[t]}
             for t, c in tag_counts.items()],
            key=lambda x: (x["appearances"], x["total_views"]),
            reverse=True,
        )
        return ranked[:50]

    def trending_music(self, max_results: int = 25) -> list[dict]:
        """Fetch trending music videos (category 10)."""
        return self.trending_videos(category_id="10", max_results=max_results)

    def search_trending_topic(self, query: str, max_results: int = 20) -> list[dict]:
        """Search YouTube for content around a trending topic."""
        data = self._get("search", {
            "part": "snippet",
            "q": query,
            "type": "video",
            "order": "viewCount",
            "publishedAfter": _days_ago_iso(7),
            "regionCode": self.region_code,
            "maxResults": min(max_results, 50),
        })
        return [
            {
                "id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["channelTitle"],
                "published_at": item["snippet"]["publishedAt"],
                "description": item["snippet"].get("description", "")[:200],
                "thumbnail": item["snippet"].get("thumbnails", {}).get("high", {}).get("url", ""),
                "url": f"https://youtube.com/watch?v={item['id']['videoId']}",
            }
            for item in data.get("items", [])
        ]

    def video_categories(self) -> list[dict]:
        """List YouTube video categories for the configured region."""
        data = self._get("videoCategories", {
            "part": "snippet",
            "regionCode": self.region_code,
            "hl": "en_US",
        })
        return [
            {"id": item["id"], "title": item["snippet"]["title"], "assignable": item["snippet"].get("assignable", False)}
            for item in data.get("items", [])
            if item["snippet"].get("assignable", False)
        ]


def _days_ago_iso(days: int) -> str:
    from datetime import timedelta
    dt = datetime.now(timezone.utc) - timedelta(days=days)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
