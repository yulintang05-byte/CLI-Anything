"""YouTube Data API v3 backend for trend fetching."""

import json
import subprocess
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

CATEGORY_NAMES: Dict[str, str] = {
    "0":  "All",
    "1":  "Film & Animation",
    "2":  "Autos & Vehicles",
    "10": "Music",
    "17": "Sports",
    "20": "Gaming",
    "22": "People & Blogs",
    "23": "Comedy",
    "24": "Entertainment",
    "25": "News & Politics",
    "26": "Howto & Style",
    "28": "Science & Technology",
}


class YouTubeBackend:
    """Wraps YouTube Data API v3 calls."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    def fetch_trending(
        self,
        region_code: str = "US",
        category_id: str = "0",
        max_results: int = 20,
    ) -> List[Dict[str, Any]]:
        """Fetch trending videos. Falls back to yt-dlp if no API key."""
        if self.api_key:
            return self._fetch_via_api(region_code, category_id, max_results)
        return self._fetch_via_ytdlp(region_code, max_results)

    def _fetch_via_api(
        self,
        region_code: str,
        category_id: str,
        max_results: int,
    ) -> List[Dict[str, Any]]:
        """Fetch trending via official YouTube Data API v3."""
        params = {
            "part": "snippet,statistics",
            "chart": "mostPopular",
            "regionCode": region_code,
            "maxResults": min(max_results, 50),
            "key": self.api_key,
        }
        if category_id and category_id != "0":
            params["videoCategoryId"] = category_id

        url = f"{YOUTUBE_API_BASE}/videos?" + urllib.parse.urlencode(params)

        try:
            with urllib.request.urlopen(url, timeout=15) as resp:
                data = json.loads(resp.read().decode())
        except Exception as e:
            raise RuntimeError(f"YouTube API request failed: {e}")

        results = []
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            tags = snippet.get("tags", [])
            hashtags = [f"#{t.replace(' ', '')}" for t in tags[:10] if t]

            results.append({
                "video_id": item["id"],
                "platform": "youtube",
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "description": snippet.get("description", "")[:200],
                "published_at": snippet.get("publishedAt", ""),
                "category": CATEGORY_NAMES.get(category_id, "All"),
                "region": region_code,
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
                "hashtags": hashtags,
                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                "url": f"https://www.youtube.com/watch?v={item['id']}",
                "source": "youtube_api",
            })

        return results

    def _fetch_via_ytdlp(
        self,
        region_code: str,
        max_results: int,
    ) -> List[Dict[str, Any]]:
        """Fetch trending via yt-dlp (no API key required)."""
        url = f"https://www.youtube.com/feed/trending?gl={region_code}"

        try:
            cmd = [
                "yt-dlp",
                "--dump-json",
                "--flat-playlist",
                "--playlist-end", str(min(max_results, 30)),
                "--no-warnings",
                "--quiet",
                url,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        except FileNotFoundError:
            raise RuntimeError(
                "yt-dlp not found. Install with: pip install yt-dlp\n"
                "Or set a YouTube API key in project config: project set-config youtube_api_key YOUR_KEY"
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("yt-dlp timed out fetching YouTube trending.")

        if result.returncode != 0 and not result.stdout.strip():
            raise RuntimeError(f"yt-dlp failed: {result.stderr[:500]}")

        results = []
        for line in result.stdout.strip().splitlines():
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue

            tags = item.get("tags") or []
            hashtags = [f"#{t.replace(' ', '')}" for t in tags[:10] if t]

            # Extract hashtags from title (e.g. #viral #trending)
            title = item.get("title", "")
            for word in title.split():
                if word.startswith("#") and word not in hashtags:
                    hashtags.append(word.lower())

            results.append({
                "video_id": item.get("id", ""),
                "platform": "youtube",
                "title": title,
                "channel": item.get("channel") or item.get("uploader", ""),
                "description": (item.get("description") or "")[:200],
                "published_at": item.get("upload_date", ""),
                "category": item.get("categories", ["Unknown"])[0] if item.get("categories") else "Unknown",
                "region": region_code,
                "view_count": item.get("view_count") or 0,
                "like_count": item.get("like_count") or 0,
                "comment_count": item.get("comment_count") or 0,
                "hashtags": hashtags,
                "thumbnail": item.get("thumbnail", ""),
                "url": item.get("webpage_url") or f"https://www.youtube.com/watch?v={item.get('id', '')}",
                "duration_sec": item.get("duration") or 0,
                "source": "yt-dlp",
            })

        return results
