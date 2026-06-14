"""YouTube Data API v3 client — fetches trending videos, music, and hashtags."""
import requests
from typing import Optional

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

# YouTube video category IDs
CATEGORY_MUSIC = "10"
CATEGORY_ENTERTAINMENT = "24"
CATEGORY_HOWTO = "26"
CATEGORY_ALL = ""


def fetch_trending_videos(
    api_key: str,
    region: str = "US",
    category_id: str = CATEGORY_ALL,
    max_results: int = 25,
) -> list[dict]:
    """Fetch YouTube trending videos for a region."""
    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": max_results,
        "key": api_key,
    }
    if category_id:
        params["videoCategoryId"] = category_id

    resp = requests.get(f"{YOUTUBE_API_BASE}/videos", params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    results = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        tags = snippet.get("tags", [])
        hashtags = [t for t in tags if t.startswith("#")] or [f"#{t.replace(' ', '')}" for t in tags[:5]]
        results.append({
            "id": item["id"],
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "published": snippet.get("publishedAt", "")[:10],
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "tags": tags[:10],
            "hashtags": hashtags[:5],
            "description_snippet": snippet.get("description", "")[:120],
            "category_id": snippet.get("categoryId", ""),
            "url": f"https://youtube.com/watch?v={item['id']}",
        })
    return results


def fetch_trending_music(api_key: str, region: str = "US", max_results: int = 20) -> list[dict]:
    return fetch_trending_videos(api_key, region, CATEGORY_MUSIC, max_results)


def extract_top_hashtags(videos: list[dict], top_n: int = 20) -> list[tuple[str, int]]:
    """Count hashtag frequency across a list of trending videos."""
    counts: dict[str, int] = {}
    for v in videos:
        for tag in v.get("hashtags", []):
            tag = tag.lower().strip("#").strip()
            if tag:
                counts[f"#{tag}"] = counts.get(f"#{tag}", 0) + 1
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_n]


def search_videos(api_key: str, query: str, max_results: int = 10) -> list[dict]:
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "viewCount",
        "maxResults": max_results,
        "key": api_key,
    }
    resp = requests.get(f"{YOUTUBE_API_BASE}/search", params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    results = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        results.append({
            "id": item["id"].get("videoId", ""),
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "published": snippet.get("publishedAt", "")[:10],
            "description_snippet": snippet.get("description", "")[:120],
        })
    return results
