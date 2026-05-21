"""YouTube viral trend scraper — uses YouTube Data API v3 + public trending page."""

import json
import re
import time
import requests
from typing import Optional

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
TRENDING_URL = "https://www.youtube.com/feed/trending"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

CATEGORY_IDS = {
    "general": "0",
    "music": "10",
    "gaming": "20",
    "movies": "1",
    "tech": "28",
    "sports": "17",
    "beauty": "26",
    "entertainment": "24",
}


def fetch_trending_via_api(
    api_key: str,
    category: str = "general",
    region: str = "US",
    max_results: int = 25,
) -> list[dict]:
    """Return trending videos using the YouTube Data API v3."""
    cat_id = CATEGORY_IDS.get(category.lower(), "0")
    url = f"{YOUTUBE_API_BASE}/videos"
    params = {
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": max_results,
        "videoCategoryId": cat_id,
        "key": api_key,
    }
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    items = resp.json().get("items", [])
    return [_parse_api_video(v) for v in items]


def _parse_api_video(item: dict) -> dict:
    snip = item.get("snippet", {})
    stats = item.get("statistics", {})
    tags = snip.get("tags", [])
    return {
        "id": item.get("id", ""),
        "title": snip.get("title", ""),
        "channel": snip.get("channelTitle", ""),
        "published_at": snip.get("publishedAt", ""),
        "views": int(stats.get("viewCount", 0)),
        "likes": int(stats.get("likeCount", 0)),
        "comments": int(stats.get("commentCount", 0)),
        "tags": tags[:20],
        "description_snippet": snip.get("description", "")[:200],
        "thumbnail": snip.get("thumbnails", {}).get("high", {}).get("url", ""),
        "url": f"https://youtube.com/watch?v={item.get('id','')}",
        "source": "youtube_api",
    }


def fetch_trending_scrape(category: str = "general", region: str = "US") -> list[dict]:
    """Scrape YouTube trending page (no API key required)."""
    cat_map = {
        "general": "",
        "music": "?bp=4gINGgt5dG1hOmdleXNyaQ%3D%3D",
        "gaming": "?bp=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D",
    }
    suffix = cat_map.get(category.lower(), "")
    url = f"{TRENDING_URL}{suffix}"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"YouTube scrape failed: {e}") from e

    # Extract ytInitialData JSON blob
    match = re.search(r"var ytInitialData\s*=\s*(\{.*?\});\s*</script>", resp.text, re.DOTALL)
    if not match:
        # Try alternate pattern
        match = re.search(r"ytInitialData\s*=\s*(\{.+?\});\s*(?:var |</script>)", resp.text, re.DOTALL)
    if not match:
        raise RuntimeError("Could not extract YouTube trending data. YouTube may have changed their page structure.")

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse YouTube data: {e}") from e

    return _extract_videos_from_yt_data(data)


def _extract_videos_from_yt_data(data: dict) -> list[dict]:
    videos = []
    try:
        tabs = (
            data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]
        )
        for tab in tabs:
            if "tabRenderer" not in tab:
                continue
            content = tab["tabRenderer"].get("content", {})
            sections = content.get("sectionListRenderer", {}).get("contents", [])
            for section in sections:
                items = section.get("itemSectionRenderer", {}).get("contents", [])
                for item in items:
                    shelf = item.get("shelfRenderer", {})
                    shelf_items = (
                        shelf.get("content", {})
                        .get("expandedShelfContentsRenderer", {})
                        .get("items", [])
                    )
                    for si in shelf_items:
                        vr = si.get("videoRenderer", {})
                        if vr:
                            videos.append(_parse_scraped_video(vr))
    except (KeyError, TypeError):
        pass
    return videos


def _parse_scraped_video(vr: dict) -> dict:
    title = ""
    title_runs = vr.get("title", {}).get("runs", [])
    if title_runs:
        title = title_runs[0].get("text", "")

    channel_runs = (
        vr.get("ownerText", {}).get("runs", [])
        or vr.get("longBylineText", {}).get("runs", [])
    )
    channel = channel_runs[0].get("text", "") if channel_runs else ""

    views_text = vr.get("viewCountText", {}).get("simpleText", "") or ""
    vid_id = vr.get("videoId", "")

    thumbnail = ""
    thumbs = vr.get("thumbnail", {}).get("thumbnails", [])
    if thumbs:
        thumbnail = thumbs[-1].get("url", "")

    return {
        "id": vid_id,
        "title": title,
        "channel": channel,
        "views_text": views_text,
        "views": _parse_view_count(views_text),
        "thumbnail": thumbnail,
        "url": f"https://youtube.com/watch?v={vid_id}" if vid_id else "",
        "tags": [],
        "source": "youtube_scrape",
    }


def _parse_view_count(text: str) -> int:
    text = text.lower().replace(",", "").replace(" views", "").strip()
    if not text:
        return 0
    multipliers = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}
    for suffix, mult in multipliers.items():
        if text.endswith(suffix):
            try:
                return int(float(text[:-1]) * mult)
            except ValueError:
                return 0
    try:
        return int(text)
    except ValueError:
        return 0


def extract_trending_hashtags(videos: list[dict], top_n: int = 30) -> list[dict]:
    """Derive trending hashtags from video tags and titles."""
    from collections import Counter
    tag_counts: Counter = Counter()
    for v in videos:
        for tag in v.get("tags", []):
            clean = tag.strip().lower()
            if clean:
                tag_counts[f"#{clean.replace(' ', '')}"] += 1
        # Also mine title words
        for word in v.get("title", "").split():
            if word.startswith("#"):
                tag_counts[word.lower()] += 1

    return [{"hashtag": h, "count": c} for h, c in tag_counts.most_common(top_n)]


def fetch_trending_music_from_videos(videos: list[dict]) -> list[dict]:
    """Extract music/audio cues from YouTube Music category trending videos."""
    music_items = []
    for v in videos:
        title = v.get("title", "")
        channel = v.get("channel", "")
        # Heuristic: music videos usually have artist - song format
        if " - " in title or "official" in title.lower() or "music video" in title.lower():
            music_items.append({
                "title": title,
                "artist": channel,
                "views": v.get("views", 0),
                "url": v.get("url", ""),
                "platform": "youtube",
            })
    return music_items
