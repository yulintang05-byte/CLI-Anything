"""YouTube viral trend scraper using yt-dlp and YouTube Data API v3."""

import json
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from typing import Optional


YOUTUBE_TRENDING_URL = "https://www.youtube.com/feed/trending"
YT_API_BASE = "https://www.googleapis.com/youtube/v3"

# Trending category IDs (YouTube regionalized)
CATEGORIES = {
    "all": "0",
    "music": "10",
    "gaming": "20",
    "films": "30",
    "entertainment": "2",
    "beauty": "26",
    "howto": "26",
    "news": "25",
    "sports": "17",
    "tech": "28",
    "travel": "19",
    "food": "26",
}


def _yt_dlp_available() -> bool:
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _ytdlp_trending(region: str = "US", limit: int = 20) -> list[dict]:
    """Fetch trending via yt-dlp flat playlist extraction."""
    url = f"https://www.youtube.com/feed/trending?gl={region}"
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--dump-json",
        "--playlist-end", str(limit),
        "--no-warnings",
        "--quiet",
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    videos = []
    for line in result.stdout.strip().splitlines():
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            videos.append({
                "id": data.get("id", ""),
                "title": data.get("title", ""),
                "url": f"https://www.youtube.com/watch?v={data.get('id', '')}",
                "uploader": data.get("uploader", data.get("channel", "")),
                "view_count": data.get("view_count", 0),
                "like_count": data.get("like_count", 0),
                "duration": data.get("duration", 0),
                "hashtags": _extract_hashtags(data.get("description", "") or data.get("title", "")),
                "thumbnail": data.get("thumbnail", ""),
                "upload_date": data.get("upload_date", ""),
                "platform": "youtube",
                "source": "yt-dlp",
            })
        except (json.JSONDecodeError, KeyError):
            continue
    return videos


def _api_trending(api_key: str, region: str = "US", category: str = "0", limit: int = 20) -> list[dict]:
    """Fetch trending via YouTube Data API v3."""
    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region,
        "videoCategoryId": category,
        "maxResults": min(limit, 50),
        "key": api_key,
    }
    url = f"{YT_API_BASE}/videos?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        data = json.loads(resp.read().decode())
    videos = []
    for item in data.get("items", []):
        snip = item.get("snippet", {})
        stats = item.get("statistics", {})
        desc = snip.get("description", "")
        title = snip.get("title", "")
        tags = snip.get("tags", [])
        hashtags = list(set(_extract_hashtags(desc) + _extract_hashtags(title) + [f"#{t.replace(' ','')}" for t in tags[:5]]))
        videos.append({
            "id": item["id"],
            "title": title,
            "url": f"https://www.youtube.com/watch?v={item['id']}",
            "uploader": snip.get("channelTitle", ""),
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
            "published_at": snip.get("publishedAt", ""),
            "thumbnail": snip.get("thumbnails", {}).get("high", {}).get("url", ""),
            "hashtags": hashtags,
            "tags": tags[:10],
            "category_id": snip.get("categoryId", ""),
            "platform": "youtube",
            "source": "youtube-api",
        })
    return videos


def _extract_hashtags(text: str) -> list[str]:
    """Pull #hashtags from any text string."""
    if not text:
        return []
    import re
    return list(set(re.findall(r"#\w+", text)))


def get_trending(
    region: str = "US",
    category: str = "all",
    limit: int = 20,
    api_key: Optional[str] = None,
) -> dict:
    """
    Fetch YouTube trending videos.

    Tries YouTube Data API first (if api_key provided), falls back to yt-dlp.
    Returns structured dict with videos, hashtags, and metadata.
    """
    cat_id = CATEGORIES.get(category.lower(), "0")
    videos = []
    method = "none"

    if api_key:
        try:
            videos = _api_trending(api_key, region, cat_id, limit)
            method = "youtube-api"
        except Exception as e:
            videos = []
            method = f"api-failed:{e}"

    if not videos and _yt_dlp_available():
        try:
            videos = _ytdlp_trending(region, limit)
            method = "yt-dlp"
        except Exception as e:
            method = f"yt-dlp-failed:{e}"

    if not videos:
        # Fallback: return curated demo data so the CLI stays useful offline
        videos = _demo_trending(limit)
        method = "demo"

    all_hashtags = {}
    for v in videos:
        for ht in v.get("hashtags", []):
            all_hashtags[ht] = all_hashtags.get(ht, 0) + 1

    top_hashtags = sorted(all_hashtags.items(), key=lambda x: x[1], reverse=True)

    return {
        "platform": "youtube",
        "region": region,
        "category": category,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "method": method,
        "total": len(videos),
        "videos": videos,
        "top_hashtags": [{"hashtag": h, "count": c} for h, c in top_hashtags[:30]],
    }


def get_search_trends(query: str, limit: int = 10, api_key: Optional[str] = None) -> dict:
    """Search YouTube for trending content on a specific topic."""
    if api_key:
        try:
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "order": "viewCount",
                "maxResults": min(limit, 50),
                "key": api_key,
            }
            url = f"{YT_API_BASE}/search?{urllib.parse.urlencode(params)}"
            with urllib.request.urlopen(url, timeout=15) as resp:
                data = json.loads(resp.read().decode())
            results = []
            for item in data.get("items", []):
                snip = item.get("snippet", {})
                vid_id = item.get("id", {}).get("videoId", "")
                results.append({
                    "id": vid_id,
                    "title": snip.get("title", ""),
                    "url": f"https://www.youtube.com/watch?v={vid_id}",
                    "uploader": snip.get("channelTitle", ""),
                    "published_at": snip.get("publishedAt", ""),
                    "hashtags": _extract_hashtags(snip.get("description", "")),
                    "platform": "youtube",
                })
            return {"query": query, "results": results, "source": "youtube-api"}
        except Exception:
            pass

    if _yt_dlp_available():
        try:
            cmd = [
                "yt-dlp",
                "--flat-playlist",
                "--dump-json",
                "--playlist-end", str(limit),
                "--no-warnings",
                "--quiet",
                f"ytsearch{limit}:{query}",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            results = []
            for line in result.stdout.strip().splitlines():
                if not line.strip():
                    continue
                try:
                    d = json.loads(line)
                    results.append({
                        "id": d.get("id", ""),
                        "title": d.get("title", ""),
                        "url": f"https://www.youtube.com/watch?v={d.get('id','')}",
                        "uploader": d.get("uploader", ""),
                        "hashtags": _extract_hashtags(d.get("description", "") or d.get("title", "")),
                        "platform": "youtube",
                    })
                except (json.JSONDecodeError, KeyError):
                    continue
            return {"query": query, "results": results, "source": "yt-dlp"}
        except Exception:
            pass

    return {"query": query, "results": [], "source": "unavailable"}


def _demo_trending(limit: int) -> list[dict]:
    """Return realistic demo data when no scraping tool is available."""
    samples = [
        {"id": "demo1", "title": "AI Takes Over Creative Jobs #AItrends #futureofwork", "uploader": "TechInsider", "view_count": 8500000, "like_count": 245000, "hashtags": ["#AItrends", "#futureofwork", "#AI"], "platform": "youtube", "source": "demo"},
        {"id": "demo2", "title": "Morning routine that changed my life #productivity #morningroutine", "uploader": "LifeHacks", "view_count": 4200000, "like_count": 189000, "hashtags": ["#productivity", "#morningroutine", "#motivation"], "platform": "youtube", "source": "demo"},
        {"id": "demo3", "title": "How I made $10k in 30 days with theme pages #themepages #passiveincome", "uploader": "DigitalHustle", "view_count": 3800000, "like_count": 167000, "hashtags": ["#themepages", "#passiveincome", "#makemoneyonline"], "platform": "youtube", "source": "demo"},
        {"id": "demo4", "title": "Viral TikTok songs of 2025 (full list) #tiktokmusic #viral", "uploader": "MusicCharts", "view_count": 6100000, "like_count": 312000, "hashtags": ["#tiktokmusic", "#viral", "#music2025"], "platform": "youtube", "source": "demo"},
        {"id": "demo5", "title": "Content creator growth hack nobody talks about #contentcreator #growthhack", "uploader": "CreatorAcademy", "view_count": 2900000, "like_count": 98000, "hashtags": ["#contentcreator", "#growthhack", "#socialmedia"], "platform": "youtube", "source": "demo"},
    ]
    return samples[:limit]
