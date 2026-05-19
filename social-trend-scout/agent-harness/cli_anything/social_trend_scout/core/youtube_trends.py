"""YouTube trending data via YouTube Data API v3."""

import re
from datetime import datetime
from typing import Any

YOUTUBE_CATEGORIES = {
    "0": "All",
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

# Tag count thresholds that consistently correlate with virality
VIRAL_ENGAGEMENT_THRESHOLD = 0.05  # 5% engagement rate = views / (likes + comments)


class YouTubeTrends:
    """Fetch and analyse trending content from YouTube Data API v3."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._service = None

    def _get_service(self):
        if self._service is None:
            from googleapiclient.discovery import build
            self._service = build("youtube", "v3", developerKey=self.api_key)
        return self._service

    # ------------------------------------------------------------------
    # Trending videos
    # ------------------------------------------------------------------

    def get_trending_videos(
        self,
        region: str = "US",
        category_id: str = "0",
        limit: int = 50,
    ) -> list[dict]:
        """Return up to `limit` trending videos for a region and category."""
        svc = self._get_service()
        results = []
        next_page = None

        while len(results) < limit:
            req_params = {
                "part": "snippet,statistics,contentDetails",
                "chart": "mostPopular",
                "regionCode": region,
                "maxResults": min(50, limit - len(results)),
            }
            if category_id != "0":
                req_params["videoCategoryId"] = category_id
            if next_page:
                req_params["pageToken"] = next_page

            response = svc.videos().list(**req_params).execute()
            for item in response.get("items", []):
                results.append(self._parse_video(item))
            next_page = response.get("nextPageToken")
            if not next_page:
                break

        return results[:limit]

    def _parse_video(self, item: dict) -> dict:
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))
        engagement = round((likes + comments) / max(views, 1) * 100, 2)

        hashtags = self._extract_hashtags(
            snippet.get("title", "") + " " + snippet.get("description", "")
        )

        return {
            "id": item["id"],
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "category_id": snippet.get("categoryId", ""),
            "published_at": snippet.get("publishedAt", ""),
            "views": views,
            "likes": likes,
            "comments": comments,
            "engagement_pct": engagement,
            "hashtags": hashtags[:10],
            "tags": snippet.get("tags", [])[:15],
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "duration": item.get("contentDetails", {}).get("duration", ""),
        }

    # ------------------------------------------------------------------
    # Hashtag extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_hashtags(text: str) -> list[str]:
        return list(dict.fromkeys(re.findall(r"#\w+", text.lower())))

    # ------------------------------------------------------------------
    # Trending hashtags (derived from trending video corpus)
    # ------------------------------------------------------------------

    def get_trending_hashtags(
        self,
        region: str = "US",
        category_id: str = "0",
        limit: int = 50,
        top_n: int = 30,
    ) -> list[dict]:
        """Aggregate hashtags from trending videos and rank by frequency."""
        videos = self.get_trending_videos(region=region, category_id=category_id, limit=limit)
        freq: dict[str, int] = {}
        for v in videos:
            for tag in v["hashtags"] + [f"#{t.lower().replace(' ', '')}" for t in v["tags"]]:
                freq[tag] = freq.get(tag, 0) + 1

        ranked = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [{"hashtag": h, "frequency": f} for h, f in ranked[:top_n]]

    # ------------------------------------------------------------------
    # Trending music / audio
    # ------------------------------------------------------------------

    def get_trending_music(self, region: str = "US", limit: int = 30) -> list[dict]:
        """Return trending videos in the Music category (id=10)."""
        videos = self.get_trending_videos(region=region, category_id="10", limit=limit)
        music = []
        for v in videos:
            music.append({
                "title": v["title"],
                "channel": v["channel"],
                "views": v["views"],
                "likes": v["likes"],
                "engagement_pct": v["engagement_pct"],
                "hashtags": v["hashtags"],
                "video_id": v["id"],
            })
        return music

    # ------------------------------------------------------------------
    # Viral score ranking
    # ------------------------------------------------------------------

    def rank_by_viral_score(self, videos: list[dict]) -> list[dict]:
        """Add a viral_score (0–100) and sort descending."""
        if not videos:
            return []
        max_views = max(v["views"] for v in videos) or 1
        max_eng = max(v["engagement_pct"] for v in videos) or 1

        for v in videos:
            view_score = v["views"] / max_views * 60
            eng_score = v["engagement_pct"] / max_eng * 40
            v["viral_score"] = round(view_score + eng_score, 1)

        return sorted(videos, key=lambda v: v["viral_score"], reverse=True)

    # ------------------------------------------------------------------
    # Summary report
    # ------------------------------------------------------------------

    def trend_report(self, region: str = "US", category_id: str = "0") -> dict:
        videos = self.get_trending_videos(region=region, category_id=category_id, limit=50)
        ranked = self.rank_by_viral_score(videos)
        hashtags = self.get_trending_hashtags(region=region, category_id=category_id)
        music = self.get_trending_music(region=region, limit=20)

        return {
            "generated_at": datetime.utcnow().isoformat(),
            "region": region,
            "category": YOUTUBE_CATEGORIES.get(category_id, "Unknown"),
            "top_videos": ranked[:10],
            "top_hashtags": hashtags[:20],
            "trending_music": music[:10],
            "total_videos_analyzed": len(videos),
        }
