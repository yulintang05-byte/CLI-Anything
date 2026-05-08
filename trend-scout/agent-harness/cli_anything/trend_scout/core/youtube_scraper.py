"""YouTube viral trend scraper using YouTube Data API v3 and yt-dlp fallback."""

import os
import re
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Any
from collections import Counter

logger = logging.getLogger(__name__)

# Optional imports - graceful fallback if not installed
try:
    from googleapiclient.discovery import build as yt_build
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False

try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


# YouTube category IDs for trending
YT_CATEGORIES = {
    "all": "0",
    "music": "10",
    "gaming": "20",
    "entertainment": "24",
    "news": "25",
    "sports": "17",
    "science": "28",
    "howto": "26",
    "fashion": "26",
    "food": "26",
}

REGION_CODES = ["US", "GB", "CA", "AU", "IN", "BR", "MX", "FR", "DE", "JP"]


class YouTubeScraper:
    """Scrapes YouTube for trending videos, hashtags, music, and viral content."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("YOUTUBE_API_KEY")
        self._service = None
        self._cache: dict[str, Any] = {}
        self._cache_ttl = 3600  # 1 hour

    def _get_service(self):
        if not self._service and YOUTUBE_API_AVAILABLE and self.api_key:
            self._service = yt_build("youtube", "v3", developerKey=self.api_key)
        return self._service

    def _cached(self, key: str, fn, *args, **kwargs):
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["ts"] < self._cache_ttl:
                return entry["data"]
        result = fn(*args, **kwargs)
        self._cache[key] = {"ts": time.time(), "data": result}
        return result

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_trending_videos(self, region: str = "US", category: str = "all", max_results: int = 50) -> list[dict]:
        """Return trending YouTube videos for a region/category."""
        key = f"trending_{region}_{category}_{max_results}"
        return self._cached(key, self._fetch_trending, region, category, max_results)

    def get_trending_hashtags(self, region: str = "US", limit: int = 30) -> list[dict]:
        """Extract and rank trending hashtags from top trending videos."""
        videos = self.get_trending_videos(region=region, max_results=50)
        return self._extract_hashtags(videos, limit)

    def get_trending_music(self, region: str = "US", limit: int = 20) -> list[dict]:
        """Return trending music/songs from YouTube Music charts."""
        key = f"music_{region}_{limit}"
        return self._cached(key, self._fetch_trending_music, region, limit)

    def get_trending_sounds_for_content(self, niche: str, region: str = "US") -> list[dict]:
        """Find trending audio/music relevant to a specific niche."""
        all_music = self.get_trending_music(region=region, limit=50)
        videos = self.get_trending_videos(region=region, max_results=50)
        niche_lower = niche.lower()
        relevant = [
            v for v in videos
            if niche_lower in v.get("title", "").lower()
            or niche_lower in v.get("description", "").lower()
            or any(niche_lower in t.lower() for t in v.get("tags", []))
        ]
        return {"trending_music": all_music[:20], "niche_relevant_videos": relevant[:10]}

    def get_viral_topics(self, region: str = "US") -> list[dict]:
        """Extract viral topic clusters from trending data."""
        videos = self.get_trending_videos(region=region, max_results=50)
        return self._cluster_topics(videos)

    def analyze_competitor(self, channel_url: str) -> dict:
        """Analyze a competitor YouTube channel for posting patterns and trends."""
        if YTDLP_AVAILABLE:
            return self._analyze_channel_ytdlp(channel_url)
        return {"error": "yt-dlp not installed. Run: pip install yt-dlp", "channel_url": channel_url}

    def get_multi_region_trends(self, regions: list[str] | None = None) -> dict:
        """Aggregate trending data across multiple regions."""
        if regions is None:
            regions = ["US", "GB", "CA", "AU"]
        results = {}
        for region in regions:
            try:
                results[region] = {
                    "videos": self.get_trending_videos(region=region, max_results=20),
                    "hashtags": self.get_trending_hashtags(region=region, limit=15),
                }
            except Exception as e:
                results[region] = {"error": str(e)}
        global_hashtags = self._aggregate_global_hashtags(results)
        return {"by_region": results, "global_trending_hashtags": global_hashtags}

    # ------------------------------------------------------------------
    # Internal fetch methods
    # ------------------------------------------------------------------

    def _fetch_trending(self, region: str, category: str, max_results: int) -> list[dict]:
        service = self._get_service()
        if service:
            return self._fetch_trending_api(service, region, category, max_results)
        if YTDLP_AVAILABLE:
            return self._fetch_trending_ytdlp(region, max_results)
        return self._fetch_trending_scrape(region, max_results)

    def _fetch_trending_api(self, service, region: str, category: str, max_results: int) -> list[dict]:
        params = {
            "part": "snippet,statistics,contentDetails",
            "chart": "mostPopular",
            "regionCode": region,
            "maxResults": min(max_results, 50),
        }
        cat_id = YT_CATEGORIES.get(category, "0")
        if cat_id != "0":
            params["videoCategoryId"] = cat_id

        response = service.videos().list(**params).execute()
        videos = []
        for item in response.get("items", []):
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            description = snippet.get("description", "")
            tags = snippet.get("tags", [])
            hashtags = self._extract_hashtags_from_text(description + " " + " ".join(tags))
            videos.append({
                "id": item["id"],
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "category_id": snippet.get("categoryId", ""),
                "published_at": snippet.get("publishedAt", ""),
                "description": description[:500],
                "tags": tags[:20],
                "hashtags": hashtags,
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                "url": f"https://youtube.com/watch?v={item['id']}",
                "region": region,
                "scraped_at": datetime.utcnow().isoformat(),
            })
        return videos

    def _fetch_trending_ytdlp(self, region: str, max_results: int) -> list[dict]:
        """Fallback: use yt-dlp to fetch trending without API key."""
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "playlistend": max_results,
        }
        url = f"https://www.youtube.com/feed/trending?gl={region}"
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                entries = info.get("entries", []) if info else []
                videos = []
                for e in entries[:max_results]:
                    hashtags = self._extract_hashtags_from_text(
                        e.get("description", "") + " " + " ".join(e.get("tags", []) or [])
                    )
                    videos.append({
                        "id": e.get("id", ""),
                        "title": e.get("title", ""),
                        "channel": e.get("uploader", ""),
                        "views": e.get("view_count", 0) or 0,
                        "likes": e.get("like_count", 0) or 0,
                        "tags": (e.get("tags") or [])[:20],
                        "hashtags": hashtags,
                        "description": (e.get("description") or "")[:500],
                        "url": e.get("webpage_url", f"https://youtube.com/watch?v={e.get('id', '')}"),
                        "thumbnail": e.get("thumbnail", ""),
                        "region": region,
                        "scraped_at": datetime.utcnow().isoformat(),
                    })
                return videos
        except Exception as e:
            logger.warning(f"yt-dlp scrape failed: {e}")
            return []

    def _fetch_trending_scrape(self, region: str, max_results: int) -> list[dict]:
        """Last resort: return instructions to set up API key."""
        return [{
            "error": "No scraping method available",
            "fix": "Set YOUTUBE_API_KEY env var (free YouTube Data API v3 key from console.cloud.google.com) or install yt-dlp: pip install yt-dlp",
            "region": region,
        }]

    def _fetch_trending_music(self, region: str, limit: int) -> list[dict]:
        service = self._get_service()
        if service:
            params = {
                "part": "snippet,statistics",
                "chart": "mostPopular",
                "regionCode": region,
                "videoCategoryId": YT_CATEGORIES["music"],
                "maxResults": min(limit, 50),
            }
            response = service.videos().list(**params).execute()
            tracks = []
            for item in response.get("items", []):
                snippet = item.get("snippet", {})
                stats = item.get("statistics", {})
                tracks.append({
                    "id": item["id"],
                    "title": snippet.get("title", ""),
                    "artist": snippet.get("channelTitle", ""),
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)),
                    "url": f"https://youtube.com/watch?v={item['id']}",
                    "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                    "region": region,
                    "use_for_content": True,
                    "scraped_at": datetime.utcnow().isoformat(),
                })
            return tracks

        # yt-dlp fallback for music charts
        if YTDLP_AVAILABLE:
            ydl_opts = {"quiet": True, "no_warnings": True, "extract_flat": True, "playlistend": limit}
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info("https://charts.youtube.com/charts/TopSongs/global", download=False)
                    if info:
                        return [
                            {
                                "id": e.get("id", ""),
                                "title": e.get("title", ""),
                                "artist": e.get("uploader", ""),
                                "views": e.get("view_count", 0) or 0,
                                "url": e.get("webpage_url", ""),
                                "use_for_content": True,
                            }
                            for e in (info.get("entries") or [])[:limit]
                        ]
            except Exception:
                pass
        return []

    def _analyze_channel_ytdlp(self, channel_url: str) -> dict:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "playlistend": 30,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(channel_url, download=False)
                entries = info.get("entries", []) if info else []
                titles = [e.get("title", "") for e in entries]
                all_tags = []
                for e in entries:
                    all_tags.extend(e.get("tags") or [])
                views = [e.get("view_count", 0) or 0 for e in entries]
                return {
                    "channel": info.get("uploader", channel_url) if info else channel_url,
                    "total_videos_analyzed": len(entries),
                    "avg_views": int(sum(views) / len(views)) if views else 0,
                    "top_video": max(entries, key=lambda e: e.get("view_count", 0) or 0, default={}).get("title", ""),
                    "common_tags": [t for t, _ in Counter(all_tags).most_common(20)],
                    "common_words_in_titles": self._top_words(titles, 20),
                    "posting_frequency": self._estimate_posting_freq(entries),
                    "scraped_at": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            return {"error": str(e), "channel_url": channel_url}

    # ------------------------------------------------------------------
    # Extraction helpers
    # ------------------------------------------------------------------

    def _extract_hashtags_from_text(self, text: str) -> list[str]:
        if not text:
            return []
        return list(dict.fromkeys(re.findall(r"#(\w+)", text)))

    def _extract_hashtags(self, videos: list[dict], limit: int) -> list[dict]:
        counter: Counter = Counter()
        for v in videos:
            for tag in v.get("hashtags", []):
                counter[tag.lower()] += 1
            for tag in v.get("tags", []):
                counter[tag.lower().replace(" ", "")] += 1
        return [
            {"hashtag": f"#{tag}", "frequency": count, "trending_score": round(count / max(len(videos), 1) * 100, 1)}
            for tag, count in counter.most_common(limit)
        ]

    def _cluster_topics(self, videos: list[dict]) -> list[dict]:
        word_counts: Counter = Counter()
        for v in videos:
            words = re.findall(r"\b[a-zA-Z]{4,}\b", v.get("title", "").lower())
            word_counts.update(words)
        stop_words = {"this", "that", "with", "your", "have", "from", "they", "what", "when", "will", "more", "been"}
        topics = [
            {"topic": word, "frequency": count, "trending": True}
            for word, count in word_counts.most_common(30)
            if word not in stop_words
        ]
        return topics[:20]

    def _aggregate_global_hashtags(self, regional_data: dict) -> list[dict]:
        counter: Counter = Counter()
        for region_data in regional_data.values():
            for h in region_data.get("hashtags", []):
                tag = h.get("hashtag", "")
                if tag:
                    counter[tag] += h.get("frequency", 1)
        return [
            {"hashtag": tag, "global_frequency": count}
            for tag, count in counter.most_common(20)
        ]

    def _top_words(self, titles: list[str], limit: int) -> list[str]:
        counter: Counter = Counter()
        stop = {"the", "a", "an", "in", "on", "of", "to", "for", "and", "or", "is", "it", "my", "your"}
        for title in titles:
            words = re.findall(r"\b[a-zA-Z]{3,}\b", title.lower())
            counter.update(w for w in words if w not in stop)
        return [w for w, _ in counter.most_common(limit)]

    def _estimate_posting_freq(self, entries: list[dict]) -> str:
        if len(entries) < 2:
            return "unknown"
        dates = []
        for e in entries:
            ts = e.get("upload_date", "")
            if ts and len(ts) == 8:
                try:
                    dates.append(datetime.strptime(ts, "%Y%m%d"))
                except ValueError:
                    pass
        if len(dates) < 2:
            return "unknown"
        dates.sort(reverse=True)
        deltas = [(dates[i] - dates[i + 1]).days for i in range(min(len(dates) - 1, 9))]
        avg = sum(deltas) / len(deltas)
        if avg < 2:
            return "daily"
        elif avg < 5:
            return "every 2-4 days"
        elif avg < 10:
            return "weekly"
        else:
            return "bi-weekly or less"
