"""YouTube trend scraper using yt-dlp + YouTube Data API v3 fallback."""
import subprocess
import json
import re
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

import requests


# YouTube trending RSS/scrape endpoints (no API key needed)
YT_TRENDING_URL = "https://www.youtube.com/feed/trending"
YT_MUSIC_TRENDING_URL = "https://www.youtube.com/feed/trending?bp=4gINGgt5dG1hX2NoYXJ0cw%3D%3D"
YT_GAMING_TRENDING_URL = "https://www.youtube.com/feed/trending?bp=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _yt_dlp_extract(url: str, extra_args: List[str] = None) -> Optional[Dict]:
    """Run yt-dlp to extract metadata from a URL."""
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--no-download",
        "--quiet",
        "--no-warnings",
        "--flat-playlist",
    ]
    if extra_args:
        cmd.extend(extra_args)
    cmd.append(url)
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60
        )
        lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
        parsed = []
        for line in lines:
            try:
                parsed.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return parsed
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def _extract_initial_data(html: str) -> Optional[Dict]:
    """Parse YouTube's ytInitialData from page HTML."""
    match = re.search(r"var ytInitialData\s*=\s*(\{.+?\});\s*</script>", html, re.DOTALL)
    if not match:
        match = re.search(r"ytInitialData\s*=\s*(\{.+?\});", html, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def _parse_view_count(text: str) -> int:
    """Convert '1.2M views' → 1200000."""
    if not text:
        return 0
    text = text.lower().replace(",", "").replace(" views", "").strip()
    try:
        if "b" in text:
            return int(float(text.replace("b", "")) * 1_000_000_000)
        if "m" in text:
            return int(float(text.replace("m", "")) * 1_000_000)
        if "k" in text:
            return int(float(text.replace("k", "")) * 1_000)
        return int(text)
    except ValueError:
        return 0


def scrape_trending_videos(
    category: str = "now",
    country: str = "US",
    limit: int = 30,
    api_key: Optional[str] = None,
) -> List[Dict]:
    """
    Scrape YouTube trending videos.

    Args:
        category: 'now'|'music'|'gaming'|'movies'
        country: ISO country code
        limit: max results
        api_key: YouTube Data API v3 key (uses web scrape if None)
    """
    if api_key:
        return _api_trending(api_key, category, country, limit)
    return _scrape_trending_web(category, country, limit)


def _api_trending(api_key: str, category: str, country: str, limit: int) -> List[Dict]:
    """Use YouTube Data API v3 for trending videos."""
    CAT_MAP = {"music": "10", "gaming": "20", "movies": "1", "now": ""}
    cat_id = CAT_MAP.get(category, "")
    params = {
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular",
        "regionCode": country,
        "maxResults": min(limit, 50),
        "key": api_key,
    }
    if cat_id:
        params["videoCategoryId"] = cat_id
    try:
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params=params, timeout=15, headers=_HEADERS,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return [{"error": str(e)}]

    results = []
    for item in data.get("items", []):
        snip = item.get("snippet", {})
        stats = item.get("statistics", {})
        tags = snip.get("tags", [])
        hashtags = [f"#{t.replace(' ', '')}" for t in tags if t]
        results.append({
            "rank": len(results) + 1,
            "title": snip.get("title", ""),
            "channel": snip.get("channelTitle", ""),
            "video_id": item.get("id", ""),
            "url": f"https://youtube.com/watch?v={item.get('id', '')}",
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "hashtags": hashtags[:10],
            "published_at": snip.get("publishedAt", ""),
            "description_snippet": snip.get("description", "")[:200],
            "thumbnail": snip.get("thumbnails", {}).get("high", {}).get("url", ""),
            "category": category,
            "source": "youtube_api",
        })
    return results


def _scrape_trending_web(category: str, country: str, limit: int) -> List[Dict]:
    """Scrape YouTube trending page without API key."""
    CAT_URLS = {
        "now": f"https://www.youtube.com/feed/trending",
        "music": f"https://www.youtube.com/feed/trending?bp=4gINGgt5dG1hX2NoYXJ0cw%3D%3D",
        "gaming": f"https://www.youtube.com/feed/trending?bp=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D",
        "movies": f"https://www.youtube.com/feed/trending?bp=4gIKGghtb3ZpZXM%3D",
    }
    url = CAT_URLS.get(category, CAT_URLS["now"])

    # Try yt-dlp playlist extraction
    items = _yt_dlp_extract(url, ["--playlist-items", f"1-{limit}"])
    if items:
        results = []
        for i, item in enumerate(items[:limit], 1):
            vid_id = item.get("id", "")
            tags = item.get("tags") or []
            hashtags = [f"#{t.replace(' ', '')}" for t in tags if isinstance(t, str)]
            desc = item.get("description") or ""
            ht_in_desc = re.findall(r"#\w+", desc)
            all_ht = list(dict.fromkeys(hashtags + ht_in_desc))[:15]
            results.append({
                "rank": i,
                "title": item.get("title", ""),
                "channel": item.get("channel") or item.get("uploader", ""),
                "video_id": vid_id,
                "url": item.get("webpage_url") or f"https://youtube.com/watch?v={vid_id}",
                "views": item.get("view_count") or 0,
                "likes": item.get("like_count") or 0,
                "duration_secs": item.get("duration") or 0,
                "hashtags": all_ht,
                "published_at": str(item.get("upload_date", "")),
                "description_snippet": desc[:200],
                "thumbnail": item.get("thumbnail", ""),
                "category": category,
                "source": "yt-dlp",
            })
        return results

    # Fallback: requests + regex parse
    return _scrape_with_requests(url, limit, category)


def _scrape_with_requests(url: str, limit: int, category: str) -> List[Dict]:
    """Fallback HTML scraper for YouTube trending."""
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=20)
        resp.raise_for_status()
        html = resp.text
    except requests.RequestException as e:
        return [{"error": f"HTTP request failed: {e}"}]

    # Extract video IDs from HTML
    video_ids = list(dict.fromkeys(re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)))
    titles_raw = re.findall(r'"text":"([^"]{5,100})"', html)
    channels = re.findall(r'"ownerText":\{"runs":\[\{"text":"([^"]+)"', html)
    view_strs = re.findall(r'"viewCountText":\{"simpleText":"([^"]+)"', html)

    results = []
    for i, vid_id in enumerate(video_ids[:limit], 1):
        title = titles_raw[i - 1] if i - 1 < len(titles_raw) else ""
        channel = channels[i - 1] if i - 1 < len(channels) else ""
        views = _parse_view_count(view_strs[i - 1]) if i - 1 < len(view_strs) else 0
        results.append({
            "rank": i,
            "title": title,
            "channel": channel,
            "video_id": vid_id,
            "url": f"https://youtube.com/watch?v={vid_id}",
            "views": views,
            "likes": 0,
            "hashtags": [],
            "published_at": "",
            "description_snippet": "",
            "thumbnail": f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg",
            "category": category,
            "source": "html_scrape",
        })
    return results


def scrape_trending_hashtags(api_key: Optional[str] = None, limit: int = 50) -> List[Dict]:
    """Extract trending hashtags from YouTube trending videos."""
    all_trends = scrape_trending_videos(category="now", limit=50, api_key=api_key)
    all_trends += scrape_trending_videos(category="music", limit=30, api_key=api_key)

    hashtag_counts: Dict[str, int] = {}
    hashtag_contexts: Dict[str, List[str]] = {}

    for video in all_trends:
        if "error" in video:
            continue
        for ht in video.get("hashtags", []):
            ht_clean = ht.lower()
            hashtag_counts[ht_clean] = hashtag_counts.get(ht_clean, 0) + 1
            if ht_clean not in hashtag_contexts:
                hashtag_contexts[ht_clean] = []
            if len(hashtag_contexts[ht_clean]) < 3:
                hashtag_contexts[ht_clean].append(video.get("title", ""))

    sorted_tags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)
    results = []
    for rank, (ht, count) in enumerate(sorted_tags[:limit], 1):
        results.append({
            "rank": rank,
            "hashtag": ht,
            "appearances": count,
            "seen_in": hashtag_contexts.get(ht, []),
            "platform": "youtube",
        })
    return results


def scrape_trending_music(api_key: Optional[str] = None, limit: int = 25) -> List[Dict]:
    """Extract trending music/audio from YouTube Music charts."""
    music_trends = scrape_trending_videos(category="music", limit=limit, api_key=api_key)

    results = []
    for video in music_trends:
        if "error" in video:
            continue
        title = video.get("title", "")
        artist_match = re.match(r"^(.+?)\s*[-–|]\s*(.+?)$", title)
        artist = artist_match.group(1).strip() if artist_match else video.get("channel", "")
        song = artist_match.group(2).strip() if artist_match else title

        results.append({
            "rank": video.get("rank", 0),
            "song_title": song,
            "artist": artist,
            "channel": video.get("channel", ""),
            "views": video.get("views", 0),
            "url": video.get("url", ""),
            "hashtags": video.get("hashtags", []),
            "platform": "youtube",
            "use_for_content": True,
        })
    return results


def get_niche_hashtags(niche: str, api_key: Optional[str] = None, limit: int = 20) -> List[Dict]:
    """Search for top hashtags in a specific niche using yt-dlp search."""
    search_url = f"ytsearch{min(limit, 30)}:{niche} trending 2024"
    items = _yt_dlp_extract(search_url)
    if not items:
        return []

    hashtag_counts: Dict[str, int] = {}
    for item in items:
        tags = item.get("tags") or []
        desc = item.get("description") or ""
        found = [f"#{t.replace(' ', '')}" for t in tags]
        found += re.findall(r"#\w+", desc)
        for ht in found:
            ht_l = ht.lower()
            hashtag_counts[ht_l] = hashtag_counts.get(ht_l, 0) + 1

    return [
        {"rank": i, "hashtag": ht, "appearances": c, "niche": niche, "platform": "youtube"}
        for i, (ht, c) in enumerate(
            sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:limit], 1
        )
    ]
