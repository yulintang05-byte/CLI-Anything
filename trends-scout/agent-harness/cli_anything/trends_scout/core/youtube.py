"""YouTube trend scraping — trending videos, hashtags, and viral music.

Uses YouTube Data API v3 when an API key is configured, falls back to
scraping the public YouTube trending page (no key required).
"""
import re
import json
from collections import Counter
from typing import Optional

from cli_anything.trends_scout.utils import config as cfg_mod
from cli_anything.trends_scout.utils.http import get_json, get_html

_YT_API_BASE = "https://www.googleapis.com/youtube/v3"
_YT_TRENDING_URL = "https://www.youtube.com/feed/trending"


# ── API-based fetching ──────────────────────────────────────────────────────

def _api_trending(region: str = "US", category_id: str = "0",
                  max_results: int = 50) -> list[dict]:
    """Fetch trending videos via YouTube Data API v3."""
    api_key = cfg_mod.get("youtube_api_key")
    if not api_key:
        raise RuntimeError(
            "No YouTube API key set. Run: trends-scout config set-key youtube_api_key <KEY>\n"
            "Get a free key at: https://console.developers.google.com/"
        )
    data = get_json(f"{_YT_API_BASE}/videos", params={
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region,
        "videoCategoryId": category_id,
        "maxResults": max_results,
        "key": api_key,
    })
    videos = []
    for item in data.get("items", []):
        snip = item.get("snippet", {})
        stats = item.get("statistics", {})
        tags = snip.get("tags", [])
        hashtags = [t for t in tags if t.startswith("#")] + _extract_hashtags(snip.get("description", ""))
        videos.append({
            "id": item["id"],
            "title": snip.get("title", ""),
            "channel": snip.get("channelTitle", ""),
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "published": snip.get("publishedAt", ""),
            "tags": tags[:10],
            "hashtags": list(set(hashtags))[:15],
            "description_snippet": snip.get("description", "")[:200],
            "thumbnail": snip.get("thumbnails", {}).get("high", {}).get("url", ""),
        })
    return videos


# ── Scrape-based fetching (no API key) ─────────────────────────────────────

def _scrape_trending(region: str = "US") -> list[dict]:
    """Scrape YouTube trending page for video data."""
    try:
        html = get_html(_YT_TRENDING_URL)
    except Exception as e:
        raise RuntimeError(f"Could not fetch YouTube trending page: {e}")

    # Extract initial data JSON embedded in page
    match = re.search(r'var ytInitialData\s*=\s*(\{.*?\});', html, re.DOTALL)
    if not match:
        # Try alternate pattern
        match = re.search(r'ytInitialData\s*=\s*(\{.*?\});\s*</script>', html, re.DOTALL)
    if not match:
        return _scrape_trending_fallback(html)

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return _scrape_trending_fallback(html)

    videos = []
    try:
        tabs = (data.get("contents", {})
                    .get("twoColumnBrowseResultsRenderer", {})
                    .get("tabs", []))
        for tab in tabs:
            contents = (tab.get("tabRenderer", {})
                           .get("content", {})
                           .get("sectionListRenderer", {})
                           .get("contents", []))
            for section in contents:
                items = (section.get("itemSectionRenderer", {})
                                .get("contents", []))
                for item in items:
                    renderer = item.get("videoRenderer", {})
                    if not renderer:
                        continue
                    title = _deep_text(renderer.get("title", {}))
                    channel = _deep_text(renderer.get("longBylineText", {}))
                    views_text = _deep_text(renderer.get("viewCountText", {}))
                    video_id = renderer.get("videoId", "")
                    desc = _deep_text(renderer.get("detailedMetadataSnippets", [{}]))
                    hashtags = _extract_hashtags(title + " " + desc)
                    videos.append({
                        "id": video_id,
                        "title": title,
                        "channel": channel,
                        "views_text": views_text,
                        "views": _parse_views(views_text),
                        "hashtags": hashtags,
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                    })
    except Exception:
        pass

    return videos or _scrape_trending_fallback(html)


def _scrape_trending_fallback(html: str) -> list[dict]:
    """Minimal fallback: extract video IDs and titles from raw HTML."""
    videos = []
    ids = re.findall(r'"videoId":"([^"]{11})"', html)
    titles = re.findall(r'"title":\{"runs":\[\{"text":"([^"]+)"', html)
    seen = set()
    for vid_id, title in zip(ids, titles):
        if vid_id in seen:
            continue
        seen.add(vid_id)
        hashtags = _extract_hashtags(title)
        videos.append({
            "id": vid_id,
            "title": title,
            "channel": "",
            "views": 0,
            "hashtags": hashtags,
            "url": f"https://www.youtube.com/watch?v={vid_id}",
        })
    return videos[:50]


def _deep_text(obj) -> str:
    """Recursively extract text from YouTube's nested text objects."""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        if "simpleText" in obj:
            return obj["simpleText"]
        if "runs" in obj:
            return "".join(r.get("text", "") for r in obj["runs"])
        for v in obj.values():
            t = _deep_text(v)
            if t:
                return t
    if isinstance(obj, list):
        parts = [_deep_text(i) for i in obj]
        return " ".join(p for p in parts if p)
    return ""


def _parse_views(text: str) -> int:
    text = text.lower().replace(",", "").replace(" views", "").strip()
    try:
        if "b" in text:
            return int(float(text.replace("b", "")) * 1_000_000_000)
        if "m" in text:
            return int(float(text.replace("m", "")) * 1_000_000)
        if "k" in text:
            return int(float(text.replace("k", "")) * 1_000)
        return int(text)
    except (ValueError, TypeError):
        return 0


def _extract_hashtags(text: str) -> list[str]:
    return list(set(re.findall(r'#\w+', text)))


# ── Public API ──────────────────────────────────────────────────────────────

def get_trending(region: str = "US", category: str = "0",
                 limit: int = 25) -> dict:
    """Get trending YouTube videos. Uses API if key set, else scrapes."""
    api_key = cfg_mod.get("youtube_api_key")
    if api_key:
        videos = _api_trending(region=region, category_id=category,
                               max_results=min(limit, 50))
    else:
        videos = _scrape_trending(region=region)

    videos = videos[:limit]
    all_hashtags = []
    for v in videos:
        all_hashtags.extend(v.get("hashtags", []))

    top_hashtags = [tag for tag, _ in Counter(all_hashtags).most_common(20)]
    return {
        "platform": "youtube",
        "region": region,
        "total": len(videos),
        "top_hashtags": top_hashtags,
        "videos": videos,
        "source": "api" if api_key else "scrape",
    }


def get_hashtags(region: str = "US", limit: int = 30) -> dict:
    """Extract the most common trending hashtags from YouTube."""
    data = get_trending(region=region, limit=50)
    all_tags = []
    for v in data["videos"]:
        all_tags.extend(v.get("hashtags", []))
        # Also parse tags array if present
        all_tags.extend(f"#{t.lstrip('#')}" for t in v.get("tags", []))

    counts = Counter(all_tags)
    hashtags = [
        {"hashtag": tag, "frequency": count}
        for tag, count in counts.most_common(limit)
    ]
    return {
        "platform": "youtube",
        "region": region,
        "hashtags": hashtags,
    }


def get_trending_music(region: str = "US", limit: int = 20) -> dict:
    """Find trending music from YouTube Music charts and viral videos."""
    api_key = cfg_mod.get("youtube_api_key")
    music_videos = []

    if api_key:
        # Category 10 = Music on YouTube
        try:
            vids = _api_trending(region=region, category_id="10",
                                 max_results=min(limit, 50))
            music_videos = vids
        except Exception:
            pass

    if not music_videos:
        # Scrape music section from trending
        try:
            html = get_html("https://www.youtube.com/feed/trending?bp=4gIuKhgKEkZFbXVzaWNfY2hh")
            music_videos = _scrape_trending_fallback(html)
        except Exception:
            pass

    # Try YouTube Music charts page as additional source
    tracks = []
    for v in music_videos[:limit]:
        title = v.get("title", "")
        # Parse "Artist - Song Title" pattern common in music videos
        parts = re.split(r'\s*[-–|]\s*', title, maxsplit=1)
        artist = parts[0].strip() if len(parts) > 1 else ""
        song = parts[1].strip() if len(parts) > 1 else title
        tracks.append({
            "artist": artist,
            "song": song,
            "title": title,
            "video_id": v.get("id", ""),
            "views": v.get("views", 0),
            "url": v.get("url", f"https://www.youtube.com/watch?v={v.get('id', '')}"),
        })

    return {
        "platform": "youtube",
        "region": region,
        "trending_music": tracks,
        "total": len(tracks),
    }
