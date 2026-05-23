"""YouTube trend scraper — viral videos, music, and hashtag analysis.

Uses the official YouTube Data API v3. Requires a Google API key.
Set YOUTUBE_API_KEY in your environment or .env file.

Get a free key at: https://console.cloud.google.com/
Enable "YouTube Data API v3" in the API Library.
Free quota: 10,000 units/day (sufficient for all trend operations here).
"""

import os
import re
import sys
from collections import Counter
from dataclasses import dataclass, field, asdict
import requests


# ── Data Models ────────────────────────────────────────────────────────

@dataclass
class YouTubeTrendingVideo:
    id: str
    title: str
    channel: str
    channel_id: str = ""
    description: str = ""
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    published_at: str = ""
    duration: str = ""
    category_id: str = ""
    category_name: str = ""
    hashtags: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    thumbnail_url: str = ""
    url: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class YouTubeTrendingMusic:
    title: str
    artist: str
    video_id: str = ""
    view_count: int = 0
    like_count: int = 0
    url: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class YouTubeTrendReport:
    scraped_at: str = ""
    region: str = "US"
    trending_videos: list[YouTubeTrendingVideo] = field(default_factory=list)
    trending_music: list[YouTubeTrendingMusic] = field(default_factory=list)
    top_hashtags: list[str] = field(default_factory=list)
    top_tags: list[str] = field(default_factory=list)
    trending_categories: list[str] = field(default_factory=list)
    recommended_hashtags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "scraped_at": self.scraped_at,
            "region": self.region,
            "trending_videos": [v.to_dict() for v in self.trending_videos],
            "trending_music": [m.to_dict() for m in self.trending_music],
            "top_hashtags": self.top_hashtags,
            "top_tags": self.top_tags,
            "trending_categories": self.trending_categories,
            "recommended_hashtags": self.recommended_hashtags,
        }


# ── Category mapping ───────────────────────────────────────────────────

_CATEGORY_MAP = {
    "1": "Film & Animation",
    "2": "Autos & Vehicles",
    "10": "Music",
    "15": "Pets & Animals",
    "17": "Sports",
    "19": "Travel & Events",
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


# ── YouTube Scraper ────────────────────────────────────────────────────

class YouTubeScraper:
    """Fetch YouTube trending data using the Data API v3.

    Args:
        api_key: YouTube Data API v3 key. Falls back to YOUTUBE_API_KEY env var.
        region: ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB', 'IN').
    """

    def __init__(self, api_key: str | None = None, region: str = "US"):
        self.api_key = api_key or os.environ.get("YOUTUBE_API_KEY", "")
        self.region = region.upper()
        self._base_url = "https://www.googleapis.com/youtube/v3"

    def _api_get(self, endpoint: str, params: dict) -> dict:
        """Direct requests fallback when google-api-python-client isn't installed."""
        params["key"] = self.api_key
        url = f"{self._base_url}/{endpoint}"
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()

    # ── Trending Videos ────────────────────────────────────────────────

    def get_trending_videos(
        self,
        count: int = 50,
        category_id: str = "",
    ) -> list[YouTubeTrendingVideo]:
        """Get YouTube trending/most-popular videos.

        Args:
            count: Number of videos to return (max 200, uses pagination).
            category_id: Optional category filter (e.g., "10" for Music).
        """
        if not self.api_key:
            print("  [YouTube] No API key — returning mock data", file=sys.stderr)
            return self._mock_trending_videos()

        videos = []
        page_token = None
        batch = min(count, 50)

        while len(videos) < count:
            params = {
                "part": "snippet,statistics,contentDetails",
                "chart": "mostPopular",
                "regionCode": self.region,
                "maxResults": batch,
                "hl": "en",
            }
            if category_id:
                params["videoCategoryId"] = category_id
            if page_token:
                params["pageToken"] = page_token

            try:
                data = self._api_get("videos", params)
            except requests.exceptions.HTTPError as e:
                print(f"  [YouTube] API error: {e}", file=sys.stderr)
                break

            for item in data.get("items", []):
                v = self._parse_video_item(item)
                if v:
                    videos.append(v)

            page_token = data.get("nextPageToken")
            if not page_token:
                break

        return videos[:count]

    def _parse_video_item(self, item: dict) -> YouTubeTrendingVideo | None:
        try:
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            content = item.get("contentDetails", {})
            video_id = item["id"]

            # Extract hashtags from title and description
            title = snippet.get("title", "")
            description = snippet.get("description", "")
            text = title + " " + description
            hashtags = list(dict.fromkeys(re.findall(r"#(\w+)", text)))

            tags = snippet.get("tags", []) or []
            category_id = snippet.get("categoryId", "")

            thumb_url = ""
            thumbs = snippet.get("thumbnails", {})
            for quality in ("maxres", "high", "medium", "default"):
                if quality in thumbs:
                    thumb_url = thumbs[quality].get("url", "")
                    break

            return YouTubeTrendingVideo(
                id=video_id,
                title=title,
                channel=snippet.get("channelTitle", ""),
                channel_id=snippet.get("channelId", ""),
                description=description[:500],
                view_count=int(stats.get("viewCount", 0)),
                like_count=int(stats.get("likeCount", 0)),
                comment_count=int(stats.get("commentCount", 0)),
                published_at=snippet.get("publishedAt", ""),
                duration=content.get("duration", ""),
                category_id=category_id,
                category_name=_CATEGORY_MAP.get(category_id, ""),
                hashtags=hashtags,
                tags=tags[:20],
                thumbnail_url=thumb_url,
                url=f"https://www.youtube.com/watch?v={video_id}",
            )
        except (KeyError, TypeError, ValueError):
            return None

    def _mock_trending_videos(self) -> list[YouTubeTrendingVideo]:
        """Mock data when API key is not configured."""
        return [
            YouTubeTrendingVideo(
                id="mock_001",
                title="[Set YOUTUBE_API_KEY to fetch real trending videos]",
                channel="API Key Required",
                view_count=0,
                url="https://console.cloud.google.com/",
            )
        ]

    # ── Trending Music ─────────────────────────────────────────────────

    def get_trending_music(self, count: int = 30) -> list[YouTubeTrendingMusic]:
        """Get trending music videos from YouTube (category 10)."""
        if not self.api_key:
            return self._mock_trending_music()

        videos = self.get_trending_videos(count=count, category_id="10")
        music = []
        for v in videos:
            # Parse "Artist - Song Title" pattern common in music videos
            parts = re.split(r"\s*[-–—]\s*", v.title, maxsplit=1)
            if len(parts) == 2:
                artist, title = parts[0].strip(), parts[1].strip()
            else:
                artist, title = v.channel, v.title

            music.append(YouTubeTrendingMusic(
                title=title,
                artist=artist,
                video_id=v.id,
                view_count=v.view_count,
                like_count=v.like_count,
                url=v.url,
            ))
        return music[:count]

    def _mock_trending_music(self) -> list[YouTubeTrendingMusic]:
        return [
            YouTubeTrendingMusic("Set YOUTUBE_API_KEY to fetch trending music", "API Key Required"),
        ]

    # ── Tag & Hashtag Analysis ─────────────────────────────────────────

    def get_top_hashtags(self, videos: list[YouTubeTrendingVideo], top_n: int = 50) -> list[str]:
        """Extract and rank hashtags across a set of trending videos."""
        counter: Counter = Counter()
        for v in videos:
            for ht in v.hashtags:
                counter[ht.lower()] += 1
        return [ht for ht, _ in counter.most_common(top_n)]

    def get_top_tags(self, videos: list[YouTubeTrendingVideo], top_n: int = 50) -> list[str]:
        """Extract and rank tags across a set of trending videos."""
        counter: Counter = Counter()
        for v in videos:
            for tag in v.tags:
                counter[tag.lower()] += 1
        return [tag for tag, _ in counter.most_common(top_n)]

    def get_trending_categories(self, videos: list[YouTubeTrendingVideo]) -> list[str]:
        """Rank categories by trending video count."""
        counter: Counter = Counter()
        for v in videos:
            if v.category_name:
                counter[v.category_name] += 1
        return [cat for cat, _ in counter.most_common()]

    # ── Full Trend Report ──────────────────────────────────────────────

    def build_trend_report(self, video_count: int = 50) -> YouTubeTrendReport:
        """Build a comprehensive YouTube trend report."""
        from datetime import datetime, timezone

        if sys.stderr.isatty():
            print("  [YouTube] Fetching trending videos...", file=sys.stderr)
        videos = self.get_trending_videos(count=video_count)

        if sys.stderr.isatty():
            print("  [YouTube] Fetching trending music...", file=sys.stderr)
        music = self.get_trending_music(count=30)

        top_ht = self.get_top_hashtags(videos)
        top_tags = self.get_top_tags(videos)
        categories = self.get_trending_categories(videos)

        # Recommended hashtags: mix of content hashtags and trending tags
        recommended = [f"#{ht}" for ht in top_ht[:20]]
        for tag in top_tags[:15]:
            tag_fmt = f"#{tag.replace(' ', '')}"
            if tag_fmt not in recommended:
                recommended.append(tag_fmt)

        return YouTubeTrendReport(
            scraped_at=datetime.now(timezone.utc).isoformat(),
            region=self.region,
            trending_videos=videos,
            trending_music=music,
            top_hashtags=top_ht[:30],
            top_tags=top_tags[:30],
            trending_categories=categories,
            recommended_hashtags=recommended[:30],
        )
