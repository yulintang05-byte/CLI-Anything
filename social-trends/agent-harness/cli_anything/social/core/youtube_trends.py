"""YouTube viral trend scraper — uses yt-dlp (no API key) + YouTube Data API v3 (optional)."""
import json
import re
import subprocess
import sys
from typing import List, Dict, Optional, Any

from cli_anything.social.utils.scraper import RateLimitedSession, BROWSER_HEADERS

YOUTUBE_TRENDING_CATEGORIES = {
    "now":      "https://www.youtube.com/feed/trending",
    "music":    "https://www.youtube.com/feed/trending?bp=4gIuKioKaHR0cHM6Ly93d3cueW91dHViZS5jb20vZmVlZC9tdXNpYz9icz10cnVl",
    "gaming":   "https://www.youtube.com/feed/trending?bp=4gIuKioKaHR0cHM6Ly93d3cueW91dHViZS5jb20vZmVlZC9nYW1pbmcvYnM9dHJ1ZQ==",
    "films":    "https://www.youtube.com/feed/trending?bp=4gIuKioKaHR0cHM6Ly93d3cueW91dHViZS5jb20vZmVlZC9maWxtcz9icz10cnVl",
}

# Country codes for trending localization
COUNTRY_CODES = {
    "us": "US", "uk": "GB", "ca": "CA", "au": "AU",
    "in": "IN", "br": "BR", "mx": "MX", "de": "DE", "fr": "FR",
}


def _ytdlp_available() -> bool:
    try:
        subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--version"],
            capture_output=True, check=True
        )
        return True
    except Exception:
        return False


def _run_ytdlp(url: str, extra_args: List[str] = None) -> Optional[str]:
    """Run yt-dlp and return stdout."""
    cmd = [sys.executable, "-m", "yt_dlp", "--no-warnings", "--quiet"] + (extra_args or []) + [url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.stdout.strip() if result.returncode == 0 else None
    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None


def scrape_trending_ytdlp(category: str = "now", max_results: int = 20) -> List[Dict]:
    """Scrape YouTube trending via yt-dlp (no API key required)."""
    url = YOUTUBE_TRENDING_CATEGORIES.get(category, YOUTUBE_TRENDING_CATEGORIES["now"])
    output = _run_ytdlp(
        url,
        extra_args=["--flat-playlist", "--dump-json", f"--playlist-end={max_results}"]
    )
    if not output:
        return []

    videos = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            videos.append({
                "id":         data.get("id", ""),
                "title":      data.get("title", ""),
                "uploader":   data.get("uploader", data.get("channel", "")),
                "view_count": data.get("view_count", 0),
                "duration":   data.get("duration", 0),
                "url":        f"https://youtube.com/watch?v={data.get('id','')}",
                "hashtags":   _extract_hashtags(data.get("title", "") + " " + data.get("description", "")),
                "category":   category,
            })
        except json.JSONDecodeError:
            continue

    return videos[:max_results]


def scrape_trending_api(api_key: str, region: str = "US", max_results: int = 20) -> List[Dict]:
    """Scrape YouTube trending via Data API v3 (requires API key)."""
    session = RateLimitedSession(min_delay=0.5, max_delay=1.5)
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part":       "snippet,statistics,contentDetails",
        "chart":      "mostPopular",
        "regionCode": region.upper(),
        "maxResults": min(max_results, 50),
        "key":        api_key,
    }
    data = session.get_json(url, params=params)
    if not data or "items" not in data:
        return []

    videos = []
    for item in data["items"]:
        snippet = item.get("snippet", {})
        stats   = item.get("statistics", {})
        videos.append({
            "id":            item.get("id", ""),
            "title":         snippet.get("title", ""),
            "uploader":      snippet.get("channelTitle", ""),
            "view_count":    int(stats.get("viewCount", 0)),
            "like_count":    int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
            "published_at":  snippet.get("publishedAt", ""),
            "url":           f"https://youtube.com/watch?v={item.get('id','')}",
            "hashtags":      snippet.get("tags", [])[:10],
            "description":   snippet.get("description", "")[:200],
            "category":      snippet.get("categoryId", ""),
        })

    return videos


def extract_trending_hashtags(videos: List[Dict], top_n: int = 20) -> List[Dict]:
    """Aggregate hashtag frequency across trending videos."""
    freq: Dict[str, int] = {}
    for v in videos:
        for tag in v.get("hashtags", []):
            tag = tag.lower().strip("#").strip()
            if tag and len(tag) > 1:
                freq[tag] = freq.get(tag, 0) + 1

    sorted_tags = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [{"hashtag": f"#{t}", "frequency": f} for t, f in sorted_tags[:top_n]]


def extract_trending_music(videos: List[Dict]) -> List[Dict]:
    """Extract music-related signals from trending data."""
    music_signals = []
    music_keywords = [
        "official", "mv", "music video", "audio", "lyrics", "remix",
        "feat", "ft.", "prod.", "beat", "album", "ep", "single",
    ]
    for v in videos:
        title_lower = v.get("title", "").lower()
        if any(kw in title_lower for kw in music_keywords):
            music_signals.append({
                "title":     v.get("title", ""),
                "artist":    v.get("uploader", ""),
                "views":     v.get("view_count", 0),
                "url":       v.get("url", ""),
                "hashtags":  v.get("hashtags", []),
            })
    return music_signals


def get_youtube_trends(
    category: str = "now",
    region: str = "US",
    max_results: int = 20,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Main entry point: return trending videos, hashtags, and music."""
    if api_key:
        videos = scrape_trending_api(api_key, region=region, max_results=max_results)
        method = "api"
    elif _ytdlp_available():
        videos = scrape_trending_ytdlp(category=category, max_results=max_results)
        method = "yt-dlp"
    else:
        return {
            "error": "Install yt-dlp (`pip install yt-dlp`) or provide a YouTube Data API v3 key.",
            "videos": [],
            "hashtags": [],
            "music": [],
        }

    return {
        "method":   method,
        "category": category,
        "region":   region,
        "videos":   videos,
        "hashtags": extract_trending_hashtags(videos),
        "music":    extract_trending_music(videos),
        "count":    len(videos),
    }


# ── helpers ──────────────────────────────────────────────────────────────────

def _extract_hashtags(text: str) -> List[str]:
    return list({m.group(0) for m in re.finditer(r"#\w+", text)})
