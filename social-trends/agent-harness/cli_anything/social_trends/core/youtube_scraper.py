"""YouTube trend scraping via YouTube Data API v3.

Requires a Google Cloud project with YouTube Data API v3 enabled.
Get an API key at: https://console.cloud.google.com/
"""

import re
import json
import time
from collections import Counter
from datetime import datetime, timezone
from typing import Optional

import requests

_YT_API_BASE = "https://www.googleapis.com/youtube/v3"
_NICHE_QUERIES = {
    "fitness": ["workout", "gym motivation", "fitness challenge"],
    "food": ["cooking tutorial", "recipe", "food challenge"],
    "travel": ["travel vlog", "travel tips", "hidden gems"],
    "tech": ["tech review", "unboxing", "gadgets"],
    "beauty": ["makeup tutorial", "skincare routine", "GRWM"],
    "gaming": ["gameplay", "gaming highlights", "speedrun"],
    "motivation": ["motivational speech", "success mindset", "self improvement"],
    "finance": ["investing tips", "how to make money", "passive income"],
    "fashion": ["outfit ideas", "style tips", "fashion haul"],
    "comedy": ["funny moments", "pranks", "memes"],
}


class YouTubeScraper:
    def __init__(self, api_key: str, region_code: str = "US", max_results: int = 50):
        self.api_key = api_key
        self.region_code = region_code
        self.max_results = max_results
        self._session = requests.Session()
        self._session.params = {"key": api_key}

    def _get(self, endpoint: str, params: dict) -> dict:
        url = f"{_YT_API_BASE}/{endpoint}"
        resp = self._session.get(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_trending_videos(self, category_id: str = "0") -> list[dict]:
        """Fetch most-popular videos for a given category (0 = all)."""
        data = self._get("videos", {
            "part": "snippet,statistics,topicDetails",
            "chart": "mostPopular",
            "regionCode": self.region_code,
            "maxResults": self.max_results,
            "videoCategoryId": category_id,
        })
        videos = []
        for item in data.get("items", []):
            snip = item["snippet"]
            stats = item.get("statistics", {})
            videos.append({
                "id": item["id"],
                "title": snip["title"],
                "channel": snip["channelTitle"],
                "published_at": snip["publishedAt"],
                "description": snip.get("description", "")[:500],
                "tags": snip.get("tags", []),
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
                "thumbnail": snip["thumbnails"]["high"]["url"],
                "category_id": snip.get("categoryId", ""),
                "url": f"https://www.youtube.com/watch?v={item['id']}",
            })
        return videos

    def get_trending_by_niche(self, niche: str, max_results: int = 20) -> list[dict]:
        """Search trending videos for a specific niche keyword set."""
        queries = _NICHE_QUERIES.get(niche.lower(), [niche])
        results = []
        for q in queries[:2]:
            data = self._get("search", {
                "part": "snippet",
                "q": q,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": _days_ago_iso(7),
                "regionCode": self.region_code,
                "maxResults": max_results // len(queries[:2]),
            })
            for item in data.get("items", []):
                snip = item["snippet"]
                results.append({
                    "id": item["id"]["videoId"],
                    "title": snip["title"],
                    "channel": snip["channelTitle"],
                    "published_at": snip["publishedAt"],
                    "description": snip.get("description", "")[:300],
                    "thumbnail": snip["thumbnails"]["high"]["url"],
                    "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                    "niche": niche,
                })
            time.sleep(0.3)
        return results

    def extract_hashtags(self, videos: list[dict]) -> list[tuple[str, int]]:
        """Extract and rank hashtags from video titles, descriptions, and tags."""
        counter: Counter = Counter()
        pattern = re.compile(r"#(\w+)")
        for v in videos:
            text = f"{v.get('title','')} {v.get('description','')} {' '.join(v.get('tags',[]))}"
            tags = pattern.findall(text.lower())
            counter.update(tags)
            # Count explicit tags list as well
            for t in v.get("tags", []):
                counter[t.lower().replace(" ", "")] += 1
        return counter.most_common(50)

    def get_trending_music(self, videos: list[dict]) -> list[dict]:
        """Detect music-related trending videos and extract track info."""
        music_keywords = re.compile(
            r"(official\s+(audio|video|mv)|lyric\s+video|music\s+video|"
            r"ft\.|feat\.|prod\.|remix|\(official\))",
            re.IGNORECASE,
        )
        music_videos = [v for v in videos if music_keywords.search(v["title"])]
        tracks = []
        for v in music_videos[:20]:
            # Parse "Artist - Song Title (Official Video)" pattern
            match = re.match(r"^(.+?)\s*[-–]\s*(.+?)(?:\s*[\(\[]|$)", v["title"])
            tracks.append({
                "title": match.group(2).strip() if match else v["title"],
                "artist": match.group(1).strip() if match else v["channel"],
                "view_count": v.get("view_count", 0),
                "url": v["url"],
                "channel": v["channel"],
            })
        return sorted(tracks, key=lambda x: x["view_count"], reverse=True)

    def get_channel_stats(self, channel_id: str) -> dict:
        """Fetch stats for a specific channel (for your own account analysis)."""
        data = self._get("channels", {
            "part": "snippet,statistics,brandingSettings",
            "id": channel_id,
        })
        items = data.get("items", [])
        if not items:
            return {}
        item = items[0]
        snip = item["snippet"]
        stats = item.get("statistics", {})
        return {
            "id": channel_id,
            "name": snip["title"],
            "description": snip.get("description", ""),
            "subscriber_count": int(stats.get("subscriberCount", 0)),
            "view_count": int(stats.get("viewCount", 0)),
            "video_count": int(stats.get("videoCount", 0)),
            "country": snip.get("country", "US"),
            "custom_url": snip.get("customUrl", ""),
            "published_at": snip.get("publishedAt", ""),
        }

    def get_channel_videos(self, channel_id: str, max_results: int = 20) -> list[dict]:
        """Get recent videos from a channel for performance analysis."""
        # First get uploads playlist ID
        ch = self._get("channels", {
            "part": "contentDetails",
            "id": channel_id,
        })
        items = ch.get("items", [])
        if not items:
            return []
        playlist_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
        data = self._get("playlistItems", {
            "part": "snippet,contentDetails",
            "playlistId": playlist_id,
            "maxResults": max_results,
        })
        video_ids = [
            item["contentDetails"]["videoId"]
            for item in data.get("items", [])
        ]
        if not video_ids:
            return []
        stats_data = self._get("videos", {
            "part": "snippet,statistics",
            "id": ",".join(video_ids),
        })
        videos = []
        for item in stats_data.get("items", []):
            snip = item["snippet"]
            stats = item.get("statistics", {})
            views = int(stats.get("viewCount", 0))
            likes = int(stats.get("likeCount", 0))
            comments = int(stats.get("commentCount", 0))
            engagement = round((likes + comments) / max(views, 1) * 100, 2)
            videos.append({
                "id": item["id"],
                "title": snip["title"],
                "published_at": snip["publishedAt"],
                "view_count": views,
                "like_count": likes,
                "comment_count": comments,
                "engagement_rate": engagement,
                "tags": snip.get("tags", []),
                "url": f"https://www.youtube.com/watch?v={item['id']}",
            })
        return videos

    def get_video_categories(self) -> dict[str, str]:
        """Return mapping of category ID → name for this region."""
        data = self._get("videoCategories", {
            "part": "snippet",
            "regionCode": self.region_code,
        })
        return {
            item["id"]: item["snippet"]["title"]
            for item in data.get("items", [])
        }


def _days_ago_iso(days: int) -> str:
    from datetime import timedelta
    dt = datetime.now(timezone.utc) - timedelta(days=days)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
