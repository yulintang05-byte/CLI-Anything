"""YouTube trend discovery via YouTube Data API v3.

Requires a YouTube Data API v3 key set via:
    cli-anything-social-trends config set-key youtube <KEY>

Free tier: 10,000 units/day.  One trending list call ≈ 1 unit.
"""

import re
import json
from typing import Optional
from collections import Counter
from datetime import datetime

import requests

_YT_BASE = "https://www.googleapis.com/youtube/v3"

# YouTube video category IDs
CATEGORIES = {
    "all": "0",
    "music": "10",
    "gaming": "20",
    "entertainment": "24",
    "news": "25",
    "sports": "17",
    "science": "28",
    "howto": "26",
    "comedy": "34",
    "film": "30",
    "autos": "2",
    "travel": "19",
    "pets": "15",
    "fashion": "26",
    "food": "26",
}


class YouTubeTrends:
    """Fetch trending videos, hashtags, and music from YouTube Data API v3."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _get(self, endpoint: str, params: dict) -> dict:
        params["key"] = self.api_key
        resp = requests.get(f"{_YT_BASE}/{endpoint}", params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_trending_videos(
        self,
        region: str = "US",
        category: str = "all",
        max_results: int = 50,
    ) -> list[dict]:
        """Return top trending videos with title, channel, stats, and hashtags."""
        cat_id = CATEGORIES.get(category.lower(), "0")
        data = self._get("videos", {
            "part": "snippet,statistics,topicDetails",
            "chart": "mostPopular",
            "regionCode": region,
            "videoCategoryId": cat_id,
            "maxResults": min(max_results, 50),
        })
        results = []
        for item in data.get("items", []):
            snip = item.get("snippet", {})
            stats = item.get("statistics", {})
            tags = snip.get("tags", [])
            hashtags = [t for t in tags if not t.startswith("#")]
            hashtags += _extract_hashtags(snip.get("description", ""))
            hashtags += _extract_hashtags(snip.get("title", ""))
            results.append({
                "id": item["id"],
                "title": snip.get("title", ""),
                "channel": snip.get("channelTitle", ""),
                "published_at": snip.get("publishedAt", ""),
                "category_id": snip.get("categoryId", ""),
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "hashtags": list(set(hashtags)),
                "thumbnail": snip.get("thumbnails", {}).get("high", {}).get("url", ""),
                "url": f"https://youtube.com/watch?v={item['id']}",
            })
        return results

    def get_trending_hashtags(
        self,
        region: str = "US",
        max_results: int = 50,
        top_n: int = 30,
    ) -> list[dict]:
        """Aggregate and rank hashtags from trending videos."""
        videos = self.get_trending_videos(region=region, max_results=max_results)
        counter: Counter = Counter()
        view_weight: dict = {}
        for v in videos:
            views = v["views"]
            for tag in v["hashtags"]:
                tag_lower = tag.lower().strip()
                if tag_lower:
                    counter[tag_lower] += 1
                    view_weight[tag_lower] = view_weight.get(tag_lower, 0) + views
        ranked = sorted(
            counter.keys(),
            key=lambda t: (counter[t] * 0.4 + view_weight.get(t, 0) / 1_000_000 * 0.6),
            reverse=True,
        )[:top_n]
        return [
            {
                "hashtag": f"#{t}",
                "appearances": counter[t],
                "total_views_on_trending": view_weight.get(t, 0),
                "score": round(counter[t] * 0.4 + view_weight.get(t, 0) / 1_000_000 * 0.6, 2),
            }
            for t in ranked
        ]

    def get_trending_music(self, region: str = "US", max_results: int = 30) -> list[dict]:
        """Return trending music videos from the Music category (cat 10)."""
        videos = self.get_trending_videos(region=region, category="music", max_results=max_results)
        music = []
        for v in videos:
            artist, title = _parse_music_title(v["title"])
            music.append({
                "title": title,
                "artist": artist,
                "channel": v["channel"],
                "views": v["views"],
                "likes": v["likes"],
                "url": v["url"],
                "hashtags": v["hashtags"],
            })
        return music

    def search_trending_topic(self, query: str, region: str = "US", max_results: int = 20) -> list[dict]:
        """Search for videos on a trending topic/keyword."""
        data = self._get("search", {
            "part": "snippet",
            "q": query,
            "type": "video",
            "order": "viewCount",
            "regionCode": region,
            "maxResults": min(max_results, 50),
            "publishedAfter": _days_ago_iso(7),
        })
        results = []
        for item in data.get("items", []):
            snip = item.get("snippet", {})
            results.append({
                "id": item["id"].get("videoId", ""),
                "title": snip.get("title", ""),
                "channel": snip.get("channelTitle", ""),
                "published_at": snip.get("publishedAt", ""),
                "description_preview": snip.get("description", "")[:200],
                "hashtags": _extract_hashtags(snip.get("description", "")),
                "url": f"https://youtube.com/watch?v={item['id'].get('videoId', '')}",
            })
        return results


# ── Helpers ────────────────────────────────────────────────────────────────────

def _extract_hashtags(text: str) -> list[str]:
    return [m.lstrip("#").lower() for m in re.findall(r"#\w+", text)]


def _parse_music_title(title: str) -> tuple[str, str]:
    """Split 'Artist - Song Title (...)' into (artist, song)."""
    for sep in (" - ", " – ", " — ", " | "):
        if sep in title:
            parts = title.split(sep, 1)
            return parts[0].strip(), parts[1].strip()
    return "", title.strip()


def _days_ago_iso(days: int) -> str:
    from datetime import timedelta
    dt = datetime.utcnow() - timedelta(days=days)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
