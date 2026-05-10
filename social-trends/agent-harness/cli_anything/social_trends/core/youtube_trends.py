"""YouTube trends scraper using YouTube Data API v3."""

import os
import json
import time
import re
from datetime import datetime, timedelta
from typing import Optional
from collections import Counter

YOUTUBE_API_AVAILABLE = False
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    YOUTUBE_API_AVAILABLE = True
except BaseException:
    pass

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


REGION_CODES = {
    "US": "United States",
    "GB": "United Kingdom",
    "CA": "Canada",
    "AU": "Australia",
    "IN": "India",
    "BR": "Brazil",
    "MX": "Mexico",
    "DE": "Germany",
    "FR": "France",
    "JP": "Japan",
    "KR": "South Korea",
    "PH": "Philippines",
    "NG": "Nigeria",
    "ZA": "South Africa",
}

CATEGORY_IDS = {
    "0":  "Film & Animation",
    "1":  "Autos & Vehicles",
    "2":  "Music",
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


def _get_youtube_client(api_key: str):
    if not YOUTUBE_API_AVAILABLE:
        raise RuntimeError("google-api-python-client not installed. Run: pip install google-api-python-client")
    return build("youtube", "v3", developerKey=api_key)


def _parse_duration(iso_duration: str) -> int:
    """Convert ISO 8601 duration to seconds."""
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso_duration)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds


def fetch_trending_videos(
    api_key: str,
    region: str = "US",
    category_id: Optional[str] = None,
    max_results: int = 50,
) -> list[dict]:
    """Fetch trending videos from YouTube for a given region."""
    yt = _get_youtube_client(api_key)
    params = {
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular",
        "regionCode": region.upper(),
        "maxResults": min(max_results, 50),
    }
    if category_id:
        params["videoCategoryId"] = category_id

    response = yt.videos().list(**params).execute()
    videos = []
    for item in response.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        content = item.get("contentDetails", {})
        desc = snippet.get("description", "")
        hashtags = re.findall(r"#(\w+)", desc + " " + snippet.get("title", ""))
        videos.append({
            "id": item["id"],
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "published_at": snippet.get("publishedAt", ""),
            "category_id": snippet.get("categoryId", ""),
            "category": CATEGORY_IDS.get(snippet.get("categoryId", ""), "Unknown"),
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
            "duration_seconds": _parse_duration(content.get("duration", "PT0S")),
            "hashtags": hashtags,
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "url": f"https://www.youtube.com/watch?v={item['id']}",
            "tags": snippet.get("tags", []),
            "description_snippet": desc[:200],
        })
    return videos


def extract_trending_hashtags(videos: list[dict], top_n: int = 30) -> list[dict]:
    """Extract and rank trending hashtags from a list of videos."""
    counter: Counter = Counter()
    hashtag_views: dict[str, int] = {}
    for v in videos:
        views = v.get("view_count", 0)
        for tag in v.get("hashtags", []):
            tag_lower = tag.lower()
            counter[tag_lower] += 1
            hashtag_views[tag_lower] = hashtag_views.get(tag_lower, 0) + views
        for tag in v.get("tags", []):
            if tag.startswith("#"):
                tag_lower = tag.lstrip("#").lower()
                counter[tag_lower] += 1

    results = []
    for tag, count in counter.most_common(top_n):
        results.append({
            "hashtag": f"#{tag}",
            "video_count": count,
            "total_views": hashtag_views.get(tag, 0),
            "avg_views": hashtag_views.get(tag, 0) // max(count, 1),
        })
    return results


def fetch_trending_music(api_key: str, region: str = "US", max_results: int = 25) -> list[dict]:
    """Fetch trending music videos from YouTube Music category."""
    videos = fetch_trending_videos(api_key, region=region, category_id="10", max_results=max_results)
    music = []
    for v in videos:
        title = v["title"]
        artist = v["channel"]
        # Try to parse "Artist - Song" format
        if " - " in title:
            parts = title.split(" - ", 1)
            artist = parts[0].strip()
            song = parts[1].strip()
        elif "–" in title:
            parts = title.split("–", 1)
            artist = parts[0].strip()
            song = parts[1].strip()
        else:
            song = title
        music.append({
            "rank": len(music) + 1,
            "artist": artist,
            "song": song,
            "channel": v["channel"],
            "view_count": v["view_count"],
            "like_count": v["like_count"],
            "duration_seconds": v["duration_seconds"],
            "url": v["url"],
            "hashtags": v["hashtags"],
            "thumbnail": v["thumbnail"],
        })
    return music


def fetch_trending_by_category(api_key: str, region: str = "US") -> dict[str, list[dict]]:
    """Fetch trending videos grouped by category."""
    categories = ["0", "10", "20", "22", "23", "24", "26", "28"]
    result = {}
    for cat_id in categories:
        cat_name = CATEGORY_IDS.get(cat_id, f"Category {cat_id}")
        try:
            videos = fetch_trending_videos(api_key, region=region, category_id=cat_id, max_results=10)
            if videos:
                result[cat_name] = videos
            time.sleep(0.1)
        except Exception:
            pass
    return result


def get_video_engagement_rate(video: dict) -> float:
    """Calculate engagement rate: (likes + comments) / views."""
    views = video.get("view_count", 0)
    if not views:
        return 0.0
    engagement = video.get("like_count", 0) + video.get("comment_count", 0)
    return round((engagement / views) * 100, 3)


def analyze_trending_patterns(videos: list[dict]) -> dict:
    """Analyze patterns across trending videos."""
    if not videos:
        return {}

    durations = [v["duration_seconds"] for v in videos if v["duration_seconds"] > 0]
    views = [v["view_count"] for v in videos if v["view_count"] > 0]
    all_tags: list[str] = []
    for v in videos:
        all_tags.extend(v.get("tags", []))
        all_tags.extend(v.get("hashtags", []))

    tag_counter = Counter(t.lower().lstrip("#") for t in all_tags)
    category_counter = Counter(v["category"] for v in videos)

    avg_duration = sum(durations) / len(durations) if durations else 0
    avg_views = sum(views) / len(views) if views else 0
    engagement_rates = [get_video_engagement_rate(v) for v in videos]
    avg_engagement = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0

    # Identify high-performing duration ranges
    short = [d for d in durations if d < 60]
    medium = [d for d in durations if 60 <= d < 600]
    long_ = [d for d in durations if d >= 600]

    return {
        "total_videos_analyzed": len(videos),
        "avg_duration_seconds": round(avg_duration, 1),
        "avg_duration_formatted": f"{int(avg_duration // 60)}m {int(avg_duration % 60)}s",
        "avg_views": int(avg_views),
        "avg_engagement_rate_pct": round(avg_engagement, 3),
        "top_categories": [{"category": k, "count": v} for k, v in category_counter.most_common(5)],
        "top_tags": [{"tag": k, "count": v} for k, v in tag_counter.most_common(20)],
        "duration_breakdown": {
            "short_under_1min": len(short),
            "medium_1_10min": len(medium),
            "long_over_10min": len(long_),
        },
        "best_duration_range": (
            "under 1 minute" if len(short) > len(medium) and len(short) > len(long_) else
            "1-10 minutes" if len(medium) >= len(long_) else
            "over 10 minutes"
        ),
    }


def search_trending_niche(api_key: str, niche: str, max_results: int = 25) -> list[dict]:
    """Search for trending content in a specific niche."""
    yt = _get_youtube_client(api_key)
    week_ago = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    response = yt.search().list(
        part="snippet",
        q=niche,
        type="video",
        order="viewCount",
        publishedAfter=week_ago,
        maxResults=min(max_results, 50),
        relevanceLanguage="en",
    ).execute()

    video_ids = [item["id"]["videoId"] for item in response.get("items", [])]
    if not video_ids:
        return []

    stats_resp = yt.videos().list(
        part="snippet,statistics,contentDetails",
        id=",".join(video_ids),
    ).execute()

    videos = []
    for item in stats_resp.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        content = item.get("contentDetails", {})
        desc = snippet.get("description", "")
        hashtags = re.findall(r"#(\w+)", desc + " " + snippet.get("title", ""))
        videos.append({
            "id": item["id"],
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "published_at": snippet.get("publishedAt", ""),
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
            "duration_seconds": _parse_duration(content.get("duration", "PT0S")),
            "hashtags": hashtags,
            "tags": snippet.get("tags", []),
            "url": f"https://www.youtube.com/watch?v={item['id']}",
            "engagement_rate": get_video_engagement_rate({
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
            }),
        })
    videos.sort(key=lambda x: x["view_count"], reverse=True)
    return videos
