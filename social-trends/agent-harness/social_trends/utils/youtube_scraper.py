"""
YouTube trend scraper — works in two modes:
  1. API mode   : YouTube Data API v3 (set YOUTUBE_API_KEY env var)
  2. Scrape mode: Public RSS + noembed endpoints (no key needed)
"""
import os
import json
import time
import hashlib
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Optional
import requests

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
NOEMBED_URL = "https://noembed.com/embed?url=https://www.youtube.com/watch?v={}"
YT_RSS_TRENDING = "https://www.youtube.com/feeds/videos.xml?chart=trending&regionCode={}"

# Public trending endpoint (no auth) — region code ISO 3166-1 alpha-2
YT_TRENDING_PAGE = "https://www.youtube.com/feed/trending"

CATEGORY_IDS = {
    "all": "0",
    "music": "10",
    "gaming": "20",
    "news": "25",
    "entertainment": "24",
    "sports": "17",
    "howto": "26",
    "science": "28",
}


def _api_key() -> Optional[str]:
    return os.environ.get("YOUTUBE_API_KEY")


def _get(url: str, params: dict = None, timeout: int = 15) -> dict:
    resp = requests.get(url, params=params, timeout=timeout,
                        headers={"User-Agent": "SocialTrendsCLI/1.0"})
    resp.raise_for_status()
    return resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text


# ---------------------------------------------------------------------------
# API-mode helpers
# ---------------------------------------------------------------------------

def fetch_trending_videos_api(region: str = "US", category: str = "all",
                               max_results: int = 25) -> list[dict]:
    """Fetch trending videos via YouTube Data API v3."""
    key = _api_key()
    if not key:
        raise EnvironmentError(
            "YOUTUBE_API_KEY not set. Run in scrape mode or set the env var."
        )
    params = {
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular",
        "regionCode": region,
        "videoCategoryId": CATEGORY_IDS.get(category, "0"),
        "maxResults": min(max_results, 50),
        "key": key,
    }
    data = _get(f"{YOUTUBE_API_BASE}/videos", params)
    out = []
    for item in data.get("items", []):
        s = item.get("snippet", {})
        st = item.get("statistics", {})
        out.append({
            "id": item["id"],
            "title": s.get("title", ""),
            "channel": s.get("channelTitle", ""),
            "published": s.get("publishedAt", ""),
            "views": int(st.get("viewCount", 0)),
            "likes": int(st.get("likeCount", 0)),
            "comments": int(st.get("commentCount", 0)),
            "tags": s.get("tags", []),
            "description": s.get("description", "")[:300],
            "thumbnail": s.get("thumbnails", {}).get("high", {}).get("url", ""),
            "url": f"https://youtu.be/{item['id']}",
            "source": "api",
        })
    return out


def fetch_trending_hashtags_api(region: str = "US", max_results: int = 50) -> list[dict]:
    """Extract trending hashtags from trending video tags."""
    videos = fetch_trending_videos_api(region=region, max_results=max_results)
    tag_freq: dict[str, int] = {}
    tag_views: dict[str, int] = {}
    for v in videos:
        for tag in v.get("tags", []):
            t = tag.lower().strip()
            if t:
                tag_freq[t] = tag_freq.get(t, 0) + 1
                tag_views[t] = tag_views.get(t, 0) + v["views"]
    ranked = sorted(tag_freq.items(), key=lambda x: (x[1], tag_views[x[0]]), reverse=True)
    return [{"hashtag": f"#{t}", "frequency": f, "total_views": tag_views[t]}
            for t, f in ranked[:50]]


def search_trending_topic_api(query: str, max_results: int = 20) -> list[dict]:
    """Search YouTube for a topic and return sorted by view count."""
    key = _api_key()
    if not key:
        raise EnvironmentError("YOUTUBE_API_KEY not set.")
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "viewCount",
        "publishedAfter": (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "maxResults": min(max_results, 50),
        "key": key,
    }
    data = _get(f"{YOUTUBE_API_BASE}/search", params)
    ids = [i["id"]["videoId"] for i in data.get("items", []) if "videoId" in i.get("id", {})]
    if not ids:
        return []
    stats = _get(f"{YOUTUBE_API_BASE}/videos", {
        "part": "statistics,snippet",
        "id": ",".join(ids),
        "key": key,
    })
    out = []
    for item in stats.get("items", []):
        s = item["snippet"]
        st = item.get("statistics", {})
        out.append({
            "id": item["id"],
            "title": s["title"],
            "channel": s["channelTitle"],
            "views": int(st.get("viewCount", 0)),
            "likes": int(st.get("likeCount", 0)),
            "url": f"https://youtu.be/{item['id']}",
            "source": "api",
        })
    return sorted(out, key=lambda x: x["views"], reverse=True)


# ---------------------------------------------------------------------------
# Scrape-mode helpers (no API key needed)
# ---------------------------------------------------------------------------

def _extract_initial_data(html: str) -> dict:
    """Pull ytInitialData from a YouTube HTML page."""
    match = re.search(r'var ytInitialData\s*=\s*(\{.*?\});\s*</script>', html, re.DOTALL)
    if not match:
        match = re.search(r'window\["ytInitialData"\]\s*=\s*(\{.*?\});', html, re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return {}


def _parse_view_count(text: str) -> int:
    """Parse '1.2M views' → 1200000."""
    text = text.replace(",", "").lower().strip()
    m = re.search(r"([\d.]+)\s*([kmb]?)", text)
    if not m:
        return 0
    n, unit = float(m.group(1)), m.group(2)
    multipliers = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}
    return int(n * multipliers.get(unit, 1))


def fetch_trending_videos_scrape(region: str = "US", category: str = "all",
                                  max_results: int = 25) -> list[dict]:
    """Scrape YouTube trending page without API key."""
    cat_paths = {
        "all": "?hl=en&gl={r}",
        "music": "?bp=4gINGgt5dG1hX2NoYXJ0cw%3D%3D&hl=en&gl={r}",
        "gaming": "?bp=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D&hl=en&gl={r}",
        "movies": "?bp=4gIKGgh0cmFpbGVycw%3D%3D&hl=en&gl={r}",
    }
    path_template = cat_paths.get(category, cat_paths["all"])
    url = "https://www.youtube.com/feed/trending" + path_template.format(r=region)

    try:
        resp = requests.get(url, timeout=20,
                            headers={"Accept-Language": "en-US,en;q=0.9",
                                     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})
        resp.raise_for_status()
    except requests.RequestException as e:
        return [{"error": str(e), "source": "scrape"}]

    data = _extract_initial_data(resp.text)
    videos = []
    try:
        tabs = data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]
        for tab in tabs:
            items = (tab.get("tabRenderer", {})
                        .get("content", {})
                        .get("sectionListRenderer", {})
                        .get("contents", []))
            for section in items:
                for item_section in section.get("itemSectionRenderer", {}).get("contents", []):
                    for renderer_key in ("videoRenderer", "compactVideoRenderer"):
                        if renderer_key in item_section:
                            r = item_section[renderer_key]
                            vid_id = r.get("videoId", "")
                            title = "".join(t.get("text", "") for t in
                                            r.get("title", {}).get("runs", []))
                            channel = "".join(t.get("text", "") for t in
                                              r.get("ownerText", {}).get("runs", []))
                            view_text = r.get("viewCountText", {}).get("simpleText", "0")
                            videos.append({
                                "id": vid_id,
                                "title": title,
                                "channel": channel,
                                "views": _parse_view_count(view_text),
                                "url": f"https://youtu.be/{vid_id}",
                                "source": "scrape",
                            })
    except (KeyError, TypeError):
        pass

    # Fallback: regex extraction when JSON parse partially fails
    if not videos:
        for m in re.finditer(r'"videoId":"([^"]+)".*?"title":\{"runs":\[\{"text":"([^"]+)"', resp.text):
            if len(videos) >= max_results:
                break
            vid_id, title = m.group(1), m.group(2)
            videos.append({"id": vid_id, "title": title, "url": f"https://youtu.be/{vid_id}", "source": "scrape"})

    return videos[:max_results]


def fetch_trending_videos(region: str = "US", category: str = "all",
                          max_results: int = 25) -> list[dict]:
    """Auto-detect API vs scrape mode."""
    if _api_key():
        return fetch_trending_videos_api(region, category, max_results)
    return fetch_trending_videos_scrape(region, category, max_results)


def fetch_music_trends(region: str = "US", max_results: int = 20) -> list[dict]:
    """Return trending music videos."""
    videos = fetch_trending_videos(region=region, category="music", max_results=max_results)
    # Enrich with music-specific fields from title pattern analysis
    for v in videos:
        title = v.get("title", "")
        # Detect artist - song format
        if " - " in title:
            parts = title.split(" - ", 1)
            v["artist"] = parts[0].strip()
            v["track"] = parts[1].strip()
        elif " | " in title:
            parts = title.split(" | ", 1)
            v["artist"] = parts[0].strip()
            v["track"] = parts[1].strip()
        else:
            v["artist"] = v.get("channel", "")
            v["track"] = title
    return videos


def extract_hashtags_from_videos(videos: list[dict]) -> list[dict]:
    """Extract and rank hashtags from video metadata."""
    freq: dict[str, int] = {}
    for v in videos:
        desc = v.get("description", "") + " " + v.get("title", "")
        tags_in_desc = re.findall(r"#(\w+)", desc)
        for t in tags_in_desc:
            key = t.lower()
            freq[key] = freq.get(key, 0) + 1
        for tag in v.get("tags", []):
            key = tag.lower().replace(" ", "")
            freq[key] = freq.get(key, 0) + 1
    ranked = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [{"hashtag": f"#{t}", "frequency": f} for t, f in ranked[:50]]


def get_channel_stats_api(channel_id: str) -> dict:
    """Fetch channel statistics via API."""
    key = _api_key()
    if not key:
        return {"error": "YOUTUBE_API_KEY required for channel stats"}
    data = _get(f"{YOUTUBE_API_BASE}/channels", {
        "part": "snippet,statistics,brandingSettings",
        "id": channel_id,
        "key": key,
    })
    if not data.get("items"):
        return {"error": f"Channel {channel_id} not found"}
    item = data["items"][0]
    s = item["snippet"]
    st = item["statistics"]
    return {
        "id": channel_id,
        "title": s["title"],
        "description": s.get("description", "")[:500],
        "created": s.get("publishedAt", ""),
        "country": s.get("country", ""),
        "subscribers": int(st.get("subscriberCount", 0)),
        "total_views": int(st.get("viewCount", 0)),
        "video_count": int(st.get("videoCount", 0)),
        "avg_views_per_video": (int(st.get("viewCount", 0)) //
                                max(1, int(st.get("videoCount", 1)))),
    }
