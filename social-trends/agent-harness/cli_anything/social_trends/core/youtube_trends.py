import os
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..utils.social_backend import cache_key, get_cached, get_config, get_session, set_cached

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

VIDEO_CATEGORIES: Dict[str, str] = {
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
}


def _get_api_key() -> str:
    config = get_config()
    key = config.get("youtube_api_key") or os.environ.get("YOUTUBE_API_KEY", "")
    if not key:
        raise ValueError(
            "YouTube API key not configured. "
            "Run: social-trends config set youtube-api-key <key>"
        )
    return key


def _map_item(item: dict) -> dict:
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    return {
        "id": item["id"],
        "title": snippet.get("title", ""),
        "channel": snippet.get("channelTitle", ""),
        "published_at": snippet.get("publishedAt", ""),
        "category_id": snippet.get("categoryId", ""),
        "category_name": VIDEO_CATEGORIES.get(snippet.get("categoryId", ""), "Unknown"),
        "description": snippet.get("description", "")[:500],
        "tags": snippet.get("tags", []),
        "view_count": int(stats.get("viewCount", 0)),
        "like_count": int(stats.get("likeCount", 0)),
        "comment_count": int(stats.get("commentCount", 0)),
        "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
        "url": f"https://www.youtube.com/watch?v={item['id']}",
    }


def get_trending_videos(
    region: str = "US",
    category_id: Optional[str] = None,
    max_results: int = 50,
    use_cache: bool = True,
) -> List[Dict[str, Any]]:
    ck = cache_key("yt_trending", region, category_id, max_results)
    if use_cache:
        cached = get_cached(ck)
        if cached:
            return cached

    api_key = _get_api_key()
    session = get_session()
    params: Dict[str, Any] = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": min(max_results, 50),
        "key": api_key,
    }
    if category_id:
        params["videoCategoryId"] = category_id

    videos: List[dict] = []
    while len(videos) < max_results:
        resp = session.get(f"{YOUTUBE_API_BASE}/videos", params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("items", []):
            videos.append(_map_item(item))
        page_token = data.get("nextPageToken")
        if not page_token or len(videos) >= max_results:
            break
        params["pageToken"] = page_token

    result = videos[:max_results]
    if use_cache:
        set_cached(ck, result, ttl_seconds=3600)
    return result


def get_trending_hashtags(region: str = "US", top_n: int = 50) -> List[Dict[str, Any]]:
    videos = get_trending_videos(region=region, max_results=50)

    counts: Dict[str, int] = {}
    video_map: Dict[str, List[str]] = {}

    for video in videos:
        for tag in video.get("tags", []):
            t = tag.lower().strip()
            if t:
                counts[t] = counts.get(t, 0) + video.get("view_count", 0)
                video_map.setdefault(t, []).append(video["title"])

        for ht in re.findall(r"#(\w+)", f"{video['title']} {video['description']}"):
            h = ht.lower()
            counts[h] = counts.get(h, 0) + video.get("view_count", 0)

    sorted_tags = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [
        {
            "hashtag": f"#{tag}",
            "total_views": views,
            "video_count": len(video_map.get(tag, [])),
            "sample_videos": video_map.get(tag, [])[:3],
        }
        for tag, views in sorted_tags[:top_n]
    ]


def get_trending_music(region: str = "US") -> List[Dict[str, Any]]:
    return get_trending_videos(region=region, category_id="10", max_results=20)


def get_trending_by_category(region: str = "US") -> Dict[str, List[Dict[str, Any]]]:
    key_categories = ["10", "20", "22", "23", "24", "26", "28"]
    result: Dict[str, list] = {}
    for cat_id in key_categories:
        cat_name = VIDEO_CATEGORIES.get(cat_id, cat_id)
        try:
            result[cat_name] = get_trending_videos(
                region=region, category_id=cat_id, max_results=10
            )
        except Exception:
            result[cat_name] = []
    return result


def search_trending_topics(
    query: str,
    region: str = "US",
    max_results: int = 20,
) -> List[Dict[str, Any]]:
    api_key = _get_api_key()
    session = get_session()
    since = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "viewCount",
        "regionCode": region,
        "publishedAfter": since,
        "maxResults": min(max_results, 50),
        "key": api_key,
    }
    resp = session.get(f"{YOUTUBE_API_BASE}/search", params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    results = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        vid_id = item["id"].get("videoId", "")
        results.append({
            "id": vid_id,
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "published_at": snippet.get("publishedAt", ""),
            "description": snippet.get("description", "")[:300],
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "url": f"https://www.youtube.com/watch?v={vid_id}",
        })
    return results
