#!/usr/bin/env python3
"""YouTube trend scraper — fetches trending videos, hashtags, and music.

Supports two modes:
  API mode   — requires a YouTube Data API v3 key (YOUTUBE_API_KEY env var)
  Scrape mode — parses ytInitialData JSON embedded in YouTube trending pages
"""

import os
import re
import json
import time
import random
import requests
from typing import Optional

_YT_TRENDING_URL = "https://www.youtube.com/feed/trending"
_YT_MUSIC_TRENDING_URL = "https://www.youtube.com/feed/trending?bp=4gINGgt5dG1hX2NoYXJ0cw%3D%3D"
_YT_API_BASE = "https://www.googleapis.com/youtube/v3"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "DNT": "1",
}


def _api_key() -> Optional[str]:
    return os.environ.get("YOUTUBE_API_KEY")


def _get_page_data(url: str) -> Optional[dict]:
    """Fetch a YouTube page and extract the embedded ytInitialData JSON."""
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        match = re.search(r"var ytInitialData\s*=\s*({.*?});\s*</script>", resp.text, re.DOTALL)
        if not match:
            match = re.search(r"ytInitialData\s*=\s*({.*?});", resp.text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    except Exception:
        pass
    return None


def _extract_video_items(data: dict) -> list[dict]:
    """Walk ytInitialData to extract video metadata from trending feed."""
    videos = []
    try:
        tabs = (
            data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]
        )
        for tab in tabs:
            try:
                items = tab["tabRenderer"]["content"]["sectionListRenderer"]["contents"]
                for section in items:
                    try:
                        shelf_items = section["itemSectionRenderer"]["contents"]
                        for shelf in shelf_items:
                            try:
                                for vr in shelf["shelfRenderer"]["content"]["expandedShelfContentsRenderer"]["items"]:
                                    vd = vr.get("videoRenderer", {})
                                    if not vd:
                                        continue
                                    title = ""
                                    try:
                                        title = vd["title"]["runs"][0]["text"]
                                    except Exception:
                                        pass
                                    views = ""
                                    try:
                                        views = vd["viewCountText"]["simpleText"]
                                    except Exception:
                                        pass
                                    channel = ""
                                    try:
                                        channel = vd["ownerText"]["runs"][0]["text"]
                                    except Exception:
                                        pass
                                    video_id = vd.get("videoId", "")
                                    desc = ""
                                    try:
                                        desc_runs = vd["descriptionSnippet"]["runs"]
                                        desc = "".join(r["text"] for r in desc_runs)
                                    except Exception:
                                        pass
                                    hashtags = re.findall(r"#(\w+)", title + " " + desc)
                                    videos.append({
                                        "platform": "youtube",
                                        "video_id": video_id,
                                        "url": f"https://www.youtube.com/watch?v={video_id}",
                                        "title": title,
                                        "channel": channel,
                                        "views": views,
                                        "hashtags": hashtags,
                                        "description_snippet": desc,
                                    })
                            except Exception:
                                pass
                    except Exception:
                        pass
            except Exception:
                pass
    except Exception:
        pass
    return videos


def fetch_trending_videos(limit: int = 20, region: str = "US") -> list[dict]:
    """Return trending YouTube videos. Uses API if key available, else scrapes."""
    api_key = _api_key()
    if api_key:
        return _api_fetch_trending(api_key, limit, region)
    return _scrape_trending(limit)


def _api_fetch_trending(api_key: str, limit: int, region: str) -> list[dict]:
    """Fetch trending videos via YouTube Data API v3."""
    results = []
    url = f"{_YT_API_BASE}/videos"
    params = {
        "part": "snippet,statistics,topicDetails",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": min(limit, 50),
        "key": api_key,
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("items", []):
            sn = item.get("snippet", {})
            st = item.get("statistics", {})
            title = sn.get("title", "")
            desc = sn.get("description", "")
            tags = sn.get("tags", [])
            hashtags = [t for t in tags if t.startswith("#")]
            hashtags += re.findall(r"#(\w+)", title + " " + desc)
            results.append({
                "platform": "youtube",
                "video_id": item["id"],
                "url": f"https://www.youtube.com/watch?v={item['id']}",
                "title": title,
                "channel": sn.get("channelTitle", ""),
                "views": st.get("viewCount", "0"),
                "likes": st.get("likeCount", "0"),
                "comments": st.get("commentCount", "0"),
                "hashtags": list(set(hashtags)),
                "tags": tags,
                "published_at": sn.get("publishedAt", ""),
                "category_id": sn.get("categoryId", ""),
            })
    except Exception as e:
        raise RuntimeError(f"YouTube API error: {e}") from e
    return results[:limit]


def _scrape_trending(limit: int) -> list[dict]:
    """Scrape YouTube trending page for video metadata."""
    data = _get_page_data(_YT_TRENDING_URL)
    if not data:
        raise RuntimeError(
            "Could not fetch YouTube trending page. "
            "Set YOUTUBE_API_KEY environment variable to use the API instead."
        )
    videos = _extract_video_items(data)
    return videos[:limit]


def fetch_trending_hashtags(limit: int = 30) -> list[dict]:
    """Extract trending hashtags from YouTube trending videos."""
    videos = fetch_trending_videos(limit=50)
    hashtag_counts: dict[str, int] = {}
    hashtag_videos: dict[str, list[str]] = {}
    for v in videos:
        for ht in v.get("hashtags", []):
            ht_lower = ht.lower()
            hashtag_counts[ht_lower] = hashtag_counts.get(ht_lower, 0) + 1
            hashtag_videos.setdefault(ht_lower, [])
            if v["title"] not in hashtag_videos[ht_lower]:
                hashtag_videos[ht_lower].append(v["title"])
    ranked = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)
    return [
        {
            "platform": "youtube",
            "hashtag": f"#{ht}",
            "video_count": count,
            "sample_videos": hashtag_videos[ht][:3],
        }
        for ht, count in ranked[:limit]
    ]


def fetch_trending_music(limit: int = 20) -> list[dict]:
    """Fetch trending music on YouTube (Music chart)."""
    data = _get_page_data(_YT_MUSIC_TRENDING_URL)
    music = []
    if data:
        videos = _extract_video_items(data)
        for v in videos[:limit]:
            music.append({
                "platform": "youtube",
                "title": v["title"],
                "artist": v["channel"],
                "url": v["url"],
                "views": v.get("views", ""),
            })
    if not music:
        api_key = _api_key()
        if api_key:
            music = _api_fetch_music_trending(api_key, limit)
    return music[:limit]


def _api_fetch_music_trending(api_key: str, limit: int) -> list[dict]:
    """Fetch trending music via YouTube API (videoCategoryId=10 = Music)."""
    url = f"{_YT_API_BASE}/videos"
    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "videoCategoryId": "10",
        "regionCode": "US",
        "maxResults": min(limit, 50),
        "key": api_key,
    }
    results = []
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        for item in resp.json().get("items", []):
            sn = item["snippet"]
            st = item.get("statistics", {})
            results.append({
                "platform": "youtube",
                "video_id": item["id"],
                "title": sn.get("title", ""),
                "artist": sn.get("channelTitle", ""),
                "url": f"https://www.youtube.com/watch?v={item['id']}",
                "views": st.get("viewCount", "0"),
                "likes": st.get("likeCount", "0"),
            })
    except Exception:
        pass
    return results
