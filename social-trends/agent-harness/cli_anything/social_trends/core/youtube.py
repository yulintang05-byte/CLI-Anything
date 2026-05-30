"""YouTube trend scraper — uses innertube API (no key required) and Data API v3 (with key)."""

import json
import re
import time
import hashlib
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

import requests

# YouTube innertube client config (mirrors what youtube-dl/yt-dlp uses)
_INNERTUBE_KEY = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
_INNERTUBE_CONTEXT = {
    "client": {
        "clientName": "WEB",
        "clientVersion": "2.20240101.00.00",
        "hl": "en",
        "gl": "US",
    }
}

_CACHE_DIR = Path.home() / ".cli-anything-social-trends" / "cache"
_CACHE_TTL = 3600  # 1 hour


def _cache_path(key: str) -> Path:
    h = hashlib.md5(key.encode()).hexdigest()
    return _CACHE_DIR / f"{h}.json"


def _read_cache(key: str) -> dict | None:
    p = _cache_path(key)
    if not p.exists():
        return None
    try:
        with open(p) as f:
            data = json.load(f)
        if time.time() - data.get("_ts", 0) > _CACHE_TTL:
            return None
        return data
    except (json.JSONDecodeError, IOError):
        return None


def _write_cache(key: str, data: dict):
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    data["_ts"] = time.time()
    try:
        with open(_cache_path(key), "w") as f:
            json.dump(data, f)
    except IOError:
        pass


def _innertube_post(endpoint: str, body: dict, timeout: int = 15) -> dict:
    url = f"https://www.youtube.com/youtubei/v1/{endpoint}?key={_INNERTUBE_KEY}&prettyPrint=false"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "X-YouTube-Client-Name": "1",
        "X-YouTube-Client-Version": "2.20240101.00.00",
        "Origin": "https://www.youtube.com",
        "Referer": "https://www.youtube.com/",
    }
    body["context"] = _INNERTUBE_CONTEXT
    resp = requests.post(url, json=body, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def _extract_text(run_list: list) -> str:
    if not run_list:
        return ""
    return "".join(r.get("text", "") for r in run_list)


def _extract_hashtags_from_text(text: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"#(\w+)", text)))


def _parse_view_count(text: str) -> int:
    text = text.replace(",", "").strip().lower()
    # Match number (optionally decimal) followed by optional suffix
    m = re.match(r"([\d.]+)\s*([kmb]?)", text)
    if not m:
        return 0
    try:
        num = float(m.group(1))
        suffix = m.group(2)
        if suffix == "k":
            return int(num * 1_000)
        if suffix == "m":
            return int(num * 1_000_000)
        if suffix == "b":
            return int(num * 1_000_000_000)
        return int(num)
    except (ValueError, IndexError):
        return 0


def fetch_trending_youtube(
    category: str = "all",
    region: str = "US",
    max_results: int = 25,
    api_key: str | None = None,
    use_cache: bool = True,
) -> dict:
    """
    Fetch YouTube trending videos.

    Args:
        category: one of 'all', 'music', 'gaming', 'news', 'movies'
        region: ISO country code (US, GB, etc.)
        max_results: max videos to return (1-50)
        api_key: YouTube Data API v3 key (optional, falls back to innertube)
        use_cache: whether to use local cache

    Returns:
        dict with keys: videos, hashtags, music, fetched_at, source, region, category
    """
    cache_key = f"yt_trending_{category}_{region}_{max_results}"
    if use_cache:
        cached = _read_cache(cache_key)
        if cached:
            cached["from_cache"] = True
            return cached

    if api_key:
        result = _fetch_via_data_api(api_key, category, region, max_results)
    else:
        result = _fetch_via_innertube(category, region, max_results)

    result["fetched_at"] = datetime.now(timezone.utc).isoformat()
    result["region"] = region
    result["category"] = category

    if use_cache:
        _write_cache(cache_key, result)

    return result


def _category_id(category: str) -> str:
    mapping = {
        "all": "0",
        "music": "10",
        "gaming": "20",
        "news": "25",
        "movies": "1",
        "sports": "17",
    }
    return mapping.get(category.lower(), "0")


def _fetch_via_data_api(api_key: str, category: str, region: str, max_results: int) -> dict:
    """YouTube Data API v3 trending endpoint."""
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": min(max_results, 50),
        "videoCategoryId": _category_id(category),
        "key": api_key,
    }
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    videos = []
    all_hashtags: dict[str, int] = {}
    music_tracks: dict[str, dict] = {}

    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        desc = snippet.get("description", "")
        title = snippet.get("title", "")

        view_count = int(stats.get("viewCount", 0))
        like_count = int(stats.get("likeCount", 0))
        comment_count = int(stats.get("commentCount", 0))

        tags = snippet.get("tags", [])
        hashtags = _extract_hashtags_from_text(title + " " + desc)
        for h in hashtags + [t for t in tags if not t.startswith("#")]:
            h = h.lower().strip()
            if h:
                all_hashtags[h] = all_hashtags.get(h, 0) + view_count

        video_entry = {
            "id": item.get("id", ""),
            "title": title,
            "channel": snippet.get("channelTitle", ""),
            "view_count": view_count,
            "like_count": like_count,
            "comment_count": comment_count,
            "published_at": snippet.get("publishedAt", ""),
            "hashtags": hashtags,
            "thumbnail": (snippet.get("thumbnails", {}).get("high", {}) or {}).get("url", ""),
            "url": f"https://www.youtube.com/watch?v={item.get('id', '')}",
            "duration": item.get("contentDetails", {}).get("duration", ""),
        }
        videos.append(video_entry)

    sorted_hashtags = sorted(all_hashtags.items(), key=lambda x: x[1], reverse=True)
    return {
        "videos": videos[:max_results],
        "hashtags": [{"tag": f"#{h}", "score": s} for h, s in sorted_hashtags[:30]],
        "music": list(music_tracks.values())[:20],
        "source": "youtube_data_api_v3",
        "total_fetched": len(videos),
    }


def _fetch_via_innertube(category: str, region: str, max_results: int) -> dict:
    """YouTube innertube browse API (no API key required)."""
    cat_map = {
        "all": "FEtrending",
        "music": "FEtrending_music",
        "gaming": "FEtrending_gaming",
        "movies": "FEtrending_movies",
        "news": "FEtrending_news",
    }
    browse_id = cat_map.get(category.lower(), "FEtrending")

    body = {
        "browseId": browse_id,
        "params": "4gINGgt5dE1vYmls",
    }

    try:
        data = _innertube_post("browse", body)
    except Exception as e:
        raise RuntimeError(f"YouTube innertube API failed: {e}") from e

    videos = []
    all_hashtags: dict[str, int] = {}

    # Walk the response tree to find video renderers
    def _walk(node):
        if isinstance(node, dict):
            if "videoRenderer" in node:
                _parse_video_renderer(node["videoRenderer"])
            elif "richItemRenderer" in node:
                content = node["richItemRenderer"].get("content", {})
                if "videoRenderer" in content:
                    _parse_video_renderer(content["videoRenderer"])
            for v in node.values():
                _walk(v)
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    def _parse_video_renderer(vr: dict):
        title = _extract_text(vr.get("title", {}).get("runs", []))
        if not title:
            return

        view_text = _extract_text(
            vr.get("viewCountText", {}).get("runs", [])
            or [vr.get("viewCountText", {})]
        ) or vr.get("viewCountText", {}).get("simpleText", "0")

        view_count = _parse_view_count(view_text)
        channel = _extract_text(
            vr.get("longBylineText", {}).get("runs", [])
            or vr.get("shortBylineText", {}).get("runs", [])
        )
        video_id = vr.get("videoId", "")
        hashtags = _extract_hashtags_from_text(title)
        for h in hashtags:
            h = h.lower()
            all_hashtags[h] = all_hashtags.get(h, 0) + max(view_count, 1)

        thumbnails = vr.get("thumbnail", {}).get("thumbnails", [])
        thumb_url = thumbnails[-1]["url"] if thumbnails else ""

        videos.append({
            "id": video_id,
            "title": title,
            "channel": channel,
            "view_count": view_count,
            "like_count": 0,
            "comment_count": 0,
            "published_at": vr.get("publishedTimeText", {}).get("simpleText", ""),
            "hashtags": hashtags,
            "thumbnail": thumb_url,
            "url": f"https://www.youtube.com/watch?v={video_id}" if video_id else "",
            "duration": vr.get("lengthText", {}).get("simpleText", ""),
        })

    _walk(data)

    sorted_hashtags = sorted(all_hashtags.items(), key=lambda x: x[1], reverse=True)
    result_videos = videos[:max_results]

    return {
        "videos": result_videos,
        "hashtags": [{"tag": f"#{h}", "score": s} for h, s in sorted_hashtags[:30]],
        "music": _extract_music_from_videos(result_videos),
        "source": "youtube_innertube",
        "total_fetched": len(videos),
    }


def _extract_music_from_videos(videos: list[dict]) -> list[dict]:
    """Heuristically identify music content from trending videos."""
    music = []
    music_keywords = ["official video", "official audio", "lyrics", "music video", "mv", "audio"]
    seen = set()

    for v in videos:
        title_lower = v["title"].lower()
        if any(kw in title_lower for kw in music_keywords):
            track_key = v["channel"].lower()
            if track_key not in seen:
                seen.add(track_key)
                music.append({
                    "title": v["title"],
                    "artist": v["channel"],
                    "view_count": v["view_count"],
                    "url": v["url"],
                    "platform": "youtube",
                })
    return music[:20]


def fetch_youtube_hashtags(
    category: str = "all",
    region: str = "US",
    top_n: int = 30,
    api_key: str | None = None,
) -> list[dict]:
    """Return top trending hashtags from YouTube."""
    result = fetch_trending_youtube(category=category, region=region, api_key=api_key)
    return result.get("hashtags", [])[:top_n]


def fetch_youtube_music(
    region: str = "US",
    max_results: int = 20,
    api_key: str | None = None,
) -> list[dict]:
    """Return trending music tracks from YouTube."""
    result = fetch_trending_youtube(category="music", region=region, api_key=api_key)
    music = result.get("music", [])
    if not music:
        music = _extract_music_from_videos(result.get("videos", []))
    return music[:max_results]
