"""YouTube trending scraper — official Data API v3 with yt-dlp fallback."""

import json
import re
import subprocess
import shutil
from typing import Any, Dict, List, Optional

import requests


YT_API_BASE = "https://www.googleapis.com/youtube/v3"

CATEGORY_MAP = {
    "all": "0",
    "film": "1",
    "autos": "2",
    "music": "10",
    "pets": "15",
    "sports": "17",
    "gaming": "20",
    "people": "22",
    "comedy": "23",
    "entertainment": "24",
    "news": "25",
    "howto": "26",
    "education": "27",
    "science": "28",
    "shows": "43",
}

TRENDING_URLS = {
    "all": "https://www.youtube.com/feed/trending",
    "music": "https://www.youtube.com/feed/trending?bp=4gINGgt5dEphYWJnZTNJc0IAJBQ%3D%3D",
    "gaming": "https://www.youtube.com/feed/trending?bp=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D",
    "film": "https://www.youtube.com/feed/trending?bp=4gIKGgh0cmFpbGVycw%3D%3D",
}


def fetch_trending_api(
    api_key: str,
    category: str = "all",
    region: str = "US",
    limit: int = 25,
) -> List[Dict[str, Any]]:
    """Fetch trending videos via YouTube Data API v3."""
    category_id = CATEGORY_MAP.get(category.lower(), "0")
    params = {
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": min(limit, 50),
        "key": api_key,
    }
    if category_id != "0":
        params["videoCategoryId"] = category_id

    resp = requests.get(f"{YT_API_BASE}/videos", params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    results = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        results.append({
            "id": item.get("id", ""),
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "published_at": snippet.get("publishedAt", ""),
            "description": snippet.get("description", "")[:300],
            "tags": snippet.get("tags", []),
            "category_id": snippet.get("categoryId", ""),
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "url": f"https://www.youtube.com/watch?v={item.get('id', '')}",
            "source": "youtube_api",
        })
    return results


def fetch_trending_ytdlp(category: str = "all", limit: int = 25) -> List[Dict[str, Any]]:
    """Fetch trending via yt-dlp (no API key required)."""
    if not shutil.which("yt-dlp"):
        raise RuntimeError(
            "yt-dlp not found. Install it: pip install yt-dlp  OR  brew install yt-dlp"
        )

    url = TRENDING_URLS.get(category.lower(), TRENDING_URLS["all"])
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--flat-playlist",
        "--playlist-end", str(limit),
        "--quiet",
        "--no-warnings",
        url,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        raise RuntimeError("yt-dlp timed out after 60s")

    if result.returncode != 0 and not result.stdout.strip():
        raise RuntimeError(f"yt-dlp failed: {result.stderr[:200]}")

    videos = []
    for line in result.stdout.strip().splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        videos.append({
            "id": item.get("id", ""),
            "title": item.get("title", ""),
            "channel": item.get("channel", item.get("uploader", "")),
            "published_at": item.get("upload_date", ""),
            "description": (item.get("description") or "")[:300],
            "tags": item.get("tags") or [],
            "category_id": "",
            "view_count": item.get("view_count") or 0,
            "like_count": item.get("like_count") or 0,
            "comment_count": item.get("comment_count") or 0,
            "thumbnail": item.get("thumbnail", ""),
            "url": item.get("url") or f"https://www.youtube.com/watch?v={item.get('id', '')}",
            "source": "ytdlp",
        })
    return videos[:limit]


def extract_hashtags_from_videos(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract and rank hashtags from video titles, descriptions, and tags."""
    counts: Dict[str, int] = {}
    for v in videos:
        # From tags
        for tag in v.get("tags", []):
            clean = tag.lower().strip().replace(" ", "")
            if clean:
                counts[clean] = counts.get(clean, 0) + 1
        # From title + description
        text = f"{v.get('title', '')} {v.get('description', '')}"
        for match in re.findall(r"#(\w+)", text):
            clean = match.lower()
            counts[clean] = counts.get(clean, 0) + 1

    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [{"hashtag": f"#{tag}", "count": cnt} for tag, cnt in ranked[:50]]


def fetch_trending(
    api_key: Optional[str] = None,
    category: str = "all",
    region: str = "US",
    limit: int = 25,
) -> Dict[str, Any]:
    """Fetch YouTube trending — API first, yt-dlp fallback."""
    method = "unknown"
    videos = []
    error = None

    if api_key:
        try:
            videos = fetch_trending_api(api_key, category, region, limit)
            method = "youtube_data_api_v3"
        except Exception as e:
            error = str(e)

    if not videos:
        try:
            videos = fetch_trending_ytdlp(category, limit)
            method = "yt-dlp"
            error = None
        except Exception as e2:
            if error:
                raise RuntimeError(
                    f"Both methods failed.\nAPI error: {error}\nyt-dlp error: {e2}"
                )
            raise

    hashtags = extract_hashtags_from_videos(videos)

    return {
        "platform": "youtube",
        "category": category,
        "region": region,
        "fetch_method": method,
        "video_count": len(videos),
        "videos": videos,
        "top_hashtags": hashtags[:20],
    }
