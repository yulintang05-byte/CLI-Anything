"""YouTube trending scraper — uses YouTube Data API v3 (free quota: 10k units/day)."""

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any


YT_API_BASE = "https://www.googleapis.com/youtube/v3"
MUSIC_CHART_BASE = "https://charts.youtube.com/charts/TrendingVideos"


def _api_key() -> str:
    key = os.environ.get("YOUTUBE_API_KEY", "")
    if not key:
        raise RuntimeError(
            "YOUTUBE_API_KEY env var not set. "
            "Get a free key at https://console.cloud.google.com/apis/library/youtube.googleapis.com"
        )
    return key


def _get(url: str) -> dict:
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"YouTube API error {e.code}: {body}") from e


def _extract_hashtags(text: str) -> list[str]:
    return re.findall(r"#\w+", text)


def get_trending_videos(region_code: str = "US", category_id: str = "0", max_results: int = 25) -> list[dict]:
    """Fetch top trending videos for a region."""
    params = urllib.parse.urlencode(
        {
            "part": "snippet,statistics,contentDetails",
            "chart": "mostPopular",
            "regionCode": region_code,
            "videoCategoryId": category_id,
            "maxResults": min(max_results, 50),
            "key": _api_key(),
        }
    )
    data = _get(f"{YT_API_BASE}/videos?{params}")
    results = []
    for item in data.get("items", []):
        snip = item.get("snippet", {})
        stats = item.get("statistics", {})
        desc = snip.get("description", "")
        title = snip.get("title", "")
        hashtags = list(
            dict.fromkeys(
                _extract_hashtags(title) + _extract_hashtags(desc)
            )
        )
        results.append(
            {
                "video_id": item.get("id", ""),
                "title": title,
                "channel": snip.get("channelTitle", ""),
                "published_at": snip.get("publishedAt", ""),
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
                "tags": snip.get("tags", [])[:15],
                "hashtags": hashtags,
                "category_id": snip.get("categoryId", ""),
                "url": f"https://youtube.com/watch?v={item.get('id', '')}",
            }
        )
    return sorted(results, key=lambda x: x["view_count"], reverse=True)


def get_trending_music(region_code: str = "US", max_results: int = 25) -> list[dict]:
    """Fetch trending music videos (category 10 = Music)."""
    return get_trending_videos(region_code=region_code, category_id="10", max_results=max_results)


def search_trending_hashtags(query: str, max_results: int = 20) -> list[dict]:
    """Search YouTube for videos with a hashtag/keyword and return engagement metrics."""
    params = urllib.parse.urlencode(
        {
            "part": "snippet",
            "q": query,
            "type": "video",
            "order": "viewCount",
            "maxResults": min(max_results, 50),
            "publishedAfter": _days_ago_iso(7),
            "key": _api_key(),
        }
    )
    search_data = _get(f"{YT_API_BASE}/search?{params}")
    video_ids = [i["id"]["videoId"] for i in search_data.get("items", []) if i.get("id", {}).get("videoId")]
    if not video_ids:
        return []
    id_str = ",".join(video_ids)
    stats_params = urllib.parse.urlencode(
        {"part": "statistics,snippet", "id": id_str, "key": _api_key()}
    )
    stats_data = _get(f"{YT_API_BASE}/videos?{stats_params}")
    results = []
    for item in stats_data.get("items", []):
        snip = item.get("snippet", {})
        stats = item.get("statistics", {})
        results.append(
            {
                "video_id": item.get("id", ""),
                "title": snip.get("title", ""),
                "channel": snip.get("channelTitle", ""),
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "url": f"https://youtube.com/watch?v={item.get('id', '')}",
            }
        )
    return sorted(results, key=lambda x: x["view_count"], reverse=True)


def extract_top_hashtags(videos: list[dict], top_n: int = 30) -> list[dict]:
    """Aggregate hashtag frequency across a list of trend videos."""
    freq: dict[str, int] = {}
    for v in videos:
        for tag in v.get("hashtags", []) + [f"#{t}" for t in v.get("tags", [])]:
            t = tag.lower().strip()
            if t and len(t) > 1:
                freq[t] = freq.get(t, 0) + 1
    return sorted(
        [{"hashtag": k, "count": v} for k, v in freq.items()],
        key=lambda x: x["count"],
        reverse=True,
    )[:top_n]


def get_categories(region_code: str = "US") -> list[dict]:
    params = urllib.parse.urlencode(
        {"part": "snippet", "regionCode": region_code, "key": _api_key()}
    )
    data = _get(f"{YT_API_BASE}/videoCategories?{params}")
    return [
        {"id": i["id"], "title": i["snippet"]["title"]}
        for i in data.get("items", [])
        if i.get("snippet", {}).get("assignable")
    ]


def _days_ago_iso(days: int) -> str:
    from datetime import timedelta
    dt = datetime.now(timezone.utc) - timedelta(days=days)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
