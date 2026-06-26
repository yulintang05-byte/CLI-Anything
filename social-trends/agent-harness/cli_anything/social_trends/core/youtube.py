"""YouTube trend scraping — Data API v3 (with key) or free proxy fallback."""

import re
from typing import Any, Dict, List, Optional

from cli_anything.social_trends.utils.http import get_json, _YOUTUBE_HEADERS

_API_BASE = "https://www.googleapis.com/youtube/v3"
# Free no-key proxy that mirrors YouTube Data API v3 (yt.lemnoslife.com)
_PROXY_BASE = "https://yt.lemnoslife.com/noKey"

# Video category IDs
CATEGORIES = {
    "all": "0",
    "music": "10",
    "gaming": "20",
    "entertainment": "24",
    "news": "25",
    "howto": "26",
    "sports": "17",
    "tech": "28",
    "travel": "19",
    "comedy": "23",
    "education": "27",
    "film": "1",
    "fashion": "26",
    "food": "26",
}


def fetch_trending(
    api_key: Optional[str] = None,
    region: str = "US",
    category: str = "all",
    max_results: int = 20,
) -> Dict[str, Any]:
    """
    Fetch trending videos from YouTube.

    Uses the official YouTube Data API v3 when an api_key is provided,
    otherwise falls back to a public no-key proxy.
    """
    category_id = CATEGORIES.get(category.lower(), "0")
    if api_key:
        return _fetch_via_api(api_key, region, category_id, max_results)
    return _fetch_via_proxy(region, category_id, max_results)


def _fetch_via_api(
    api_key: str, region: str, category_id: str, max_results: int
) -> Dict[str, Any]:
    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region,
        "videoCategoryId": category_id,
        "maxResults": min(max_results, 50),
        "key": api_key,
    }
    data = get_json(f"{_API_BASE}/videos", params=params, headers=_YOUTUBE_HEADERS)
    return _parse_api_response(data, region, "youtube_api")


def _fetch_via_proxy(
    region: str, category_id: str, max_results: int
) -> Dict[str, Any]:
    """Use yt.lemnoslife.com free proxy — no API key required."""
    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region,
        "videoCategoryId": category_id,
        "maxResults": min(max_results, 50),
    }
    try:
        data = get_json(f"{_PROXY_BASE}/videos", params=params, headers=_YOUTUBE_HEADERS)
        return _parse_api_response(data, region, "youtube_proxy")
    except Exception as e:
        raise RuntimeError(
            f"YouTube fetch failed. Try setting a YouTube Data API v3 key with "
            f"`social-trends config set youtube_api_key YOUR_KEY`. Error: {e}"
        )


def _parse_api_response(data: Dict, region: str, source: str) -> Dict[str, Any]:
    videos = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        video_id = item.get("id", "")
        tags = snippet.get("tags", []) or []
        videos.append({
            "id": video_id,
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "views": _safe_int(stats.get("viewCount")),
            "likes": _safe_int(stats.get("likeCount")),
            "comments": _safe_int(stats.get("commentCount")),
            "tags": tags[:20],
            "hashtags": _extract_hashtags(snippet.get("title", "") + " " + snippet.get("description", "")),
            "description_snippet": (snippet.get("description") or "")[:200],
            "published_at": snippet.get("publishedAt", ""),
            "thumbnail": (snippet.get("thumbnails") or {}).get("high", {}).get("url", ""),
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "category_id": snippet.get("categoryId", ""),
        })

    all_hashtags = _rank_hashtags_from_videos(videos)
    return {
        "source": source,
        "region": region,
        "total": len(videos),
        "videos": videos,
        "trending_hashtags": all_hashtags[:30],
        "trending_tags": _rank_tags_from_videos(videos)[:30],
    }


def fetch_channel_info(channel_id: str, api_key: str) -> Dict[str, Any]:
    """Fetch basic channel stats via the official API."""
    params = {
        "part": "snippet,statistics",
        "id": channel_id,
        "key": api_key,
    }
    data = get_json(f"{_API_BASE}/channels", params=params, headers=_YOUTUBE_HEADERS)
    items = data.get("items", [])
    if not items:
        raise ValueError(f"Channel '{channel_id}' not found.")
    item = items[0]
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    return {
        "id": channel_id,
        "title": snippet.get("title", ""),
        "description": (snippet.get("description") or "")[:300],
        "subscribers": _safe_int(stats.get("subscriberCount")),
        "views_total": _safe_int(stats.get("viewCount")),
        "video_count": _safe_int(stats.get("videoCount")),
        "country": snippet.get("country", ""),
        "published_at": snippet.get("publishedAt", ""),
        "thumbnail": (snippet.get("thumbnails") or {}).get("high", {}).get("url", ""),
        "url": f"https://www.youtube.com/channel/{channel_id}",
    }


def search_videos(
    query: str,
    api_key: str,
    region: str = "US",
    max_results: int = 10,
    order: str = "viewCount",
) -> Dict[str, Any]:
    """Search videos by keyword — requires API key."""
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "regionCode": region,
        "maxResults": min(max_results, 50),
        "order": order,
        "key": api_key,
    }
    data = get_json(f"{_API_BASE}/search", params=params, headers=_YOUTUBE_HEADERS)
    results = []
    for item in data.get("items", []):
        vid_id = item.get("id", {}).get("videoId", "")
        snippet = item.get("snippet", {})
        results.append({
            "id": vid_id,
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "description_snippet": (snippet.get("description") or "")[:150],
            "published_at": snippet.get("publishedAt", ""),
            "url": f"https://www.youtube.com/watch?v={vid_id}",
        })
    return {"query": query, "region": region, "total": len(results), "results": results}


def extract_trending_music_from_videos(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract likely trending music titles from video metadata.
    Looks for music category videos and audio feature patterns.
    """
    music_signals = []
    music_keywords = re.compile(
        r"(official\s*(music\s*)?(video|audio|lyric|mv)|"
        r"feat\.?|ft\.?|prod\.?|remix|cover|lyrics?|audio)",
        re.IGNORECASE,
    )
    for v in videos:
        title = v.get("title", "")
        cat = v.get("category_id", "")
        if cat == "10" or music_keywords.search(title):
            cleaned = re.sub(r"\(.*?\)|\[.*?\]", "", title).strip()
            music_signals.append({
                "title": cleaned,
                "original_title": title,
                "views": v.get("views", 0),
                "url": v.get("url", ""),
                "channel": v.get("channel", ""),
            })
    music_signals.sort(key=lambda x: x["views"], reverse=True)
    return music_signals


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_hashtags(text: str) -> List[str]:
    return list(dict.fromkeys(re.findall(r"#(\w+)", text)))


def _rank_hashtags_from_videos(videos: List[Dict]) -> List[Dict[str, Any]]:
    counts: Dict[str, int] = {}
    for v in videos:
        for tag in v.get("hashtags", []):
            tag_lower = tag.lower()
            counts[tag_lower] = counts.get(tag_lower, 0) + 1
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [{"hashtag": f"#{t}", "frequency": c} for t, c in ranked]


def _rank_tags_from_videos(videos: List[Dict]) -> List[Dict[str, Any]]:
    counts: Dict[str, int] = {}
    for v in videos:
        for tag in v.get("tags", []):
            tag_lower = tag.lower().strip()
            if tag_lower:
                counts[tag_lower] = counts.get(tag_lower, 0) + 1
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [{"tag": t, "frequency": c} for t, c in ranked]


def _safe_int(val: Any) -> int:
    try:
        return int(val or 0)
    except (TypeError, ValueError):
        return 0
