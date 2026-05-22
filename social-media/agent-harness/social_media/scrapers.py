"""
Trend scrapers for YouTube and TikTok using public APIs and data endpoints.

YouTube: Uses YouTube Data API v3 (free, 10k units/day quota).
TikTok:  Uses TikTok Research API (for eligible developers) with a
         public trending endpoint fallback via RapidAPI.
"""
import os
import json
import time
import re
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone
from typing import Optional


YT_API_BASE = "https://www.googleapis.com/youtube/v3"
RAPIDAPI_HOST = "tiktok-api23.p.rapidapi.com"


def _get(url: str, headers: dict = None) -> dict:
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


# ── YouTube ──────────────────────────────────────────────────────────────────

def youtube_trending(api_key: str, region: str = "US", max_results: int = 50) -> list[dict]:
    """Return top trending YouTube videos with tags and music info."""
    params = urllib.parse.urlencode({
        "part": "snippet,statistics,topicDetails",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": max_results,
        "key": api_key,
    })
    data = _get(f"{YT_API_BASE}/videos?{params}")
    results = []
    for item in data.get("items", []):
        sn = item["snippet"]
        st = item.get("statistics", {})
        results.append({
            "id": item["id"],
            "title": sn["title"],
            "channel": sn["channelTitle"],
            "published": sn["publishedAt"],
            "views": int(st.get("viewCount", 0)),
            "likes": int(st.get("likeCount", 0)),
            "comments": int(st.get("commentCount", 0)),
            "tags": sn.get("tags", []),
            "category_id": sn.get("categoryId"),
            "thumbnail": sn["thumbnails"]["high"]["url"],
            "description_snippet": sn["description"][:280],
        })
    return results


def youtube_trending_hashtags(videos: list[dict], top_n: int = 30) -> list[dict]:
    """Aggregate and rank hashtags from trending video tags."""
    counts: dict[str, int] = {}
    for v in videos:
        for tag in v.get("tags", []):
            tag = tag.lower().strip()
            if tag:
                counts[tag] = counts.get(tag, 0) + 1
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return [{"hashtag": f"#{t}", "frequency": c} for t, c in ranked]


def youtube_search_trending_music(api_key: str, region: str = "US", max_results: int = 20) -> list[dict]:
    """Search YouTube for trending music / audio tracks."""
    params = urllib.parse.urlencode({
        "part": "snippet",
        "q": "trending music 2025",
        "type": "video",
        "videoCategoryId": "10",  # Music category
        "order": "viewCount",
        "regionCode": region,
        "maxResults": max_results,
        "key": api_key,
    })
    data = _get(f"{YT_API_BASE}/search?{params}")
    return [
        {
            "id": i["id"].get("videoId"),
            "title": i["snippet"]["title"],
            "channel": i["snippet"]["channelTitle"],
            "published": i["snippet"]["publishedAt"],
            "thumbnail": i["snippet"]["thumbnails"]["high"]["url"],
        }
        for i in data.get("items", [])
        if i["id"].get("videoId")
    ]


# ── TikTok ───────────────────────────────────────────────────────────────────

def tiktok_trending_via_rapidapi(rapidapi_key: str, region: str = "US") -> list[dict]:
    """
    Fetch TikTok trending videos using the TikTok API on RapidAPI.
    Sign up at rapidapi.com and subscribe to 'tiktok-api23' (free tier).
    """
    url = f"https://{RAPIDAPI_HOST}/api/trending/feed?region={region}"
    headers = {
        "x-rapidapi-key": rapidapi_key,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }
    data = _get(url, headers)
    items = data.get("itemList", []) or data.get("data", {}).get("itemList", [])
    results = []
    for item in items:
        desc = item.get("desc", "")
        hashtags = re.findall(r"#(\w+)", desc)
        music = item.get("music", {})
        stats = item.get("stats", {})
        results.append({
            "id": item.get("id"),
            "desc": desc,
            "hashtags": hashtags,
            "music_title": music.get("title"),
            "music_author": music.get("authorName"),
            "music_id": music.get("id"),
            "plays": stats.get("playCount", 0),
            "likes": stats.get("diggCount", 0),
            "shares": stats.get("shareCount", 0),
            "comments": stats.get("commentCount", 0),
            "author": item.get("author", {}).get("uniqueId"),
        })
    return results


def tiktok_trending_hashtags(videos: list[dict], top_n: int = 30) -> list[dict]:
    """Rank hashtags from TikTok trending feed."""
    counts: dict[str, int] = {}
    for v in videos:
        for tag in v.get("hashtags", []):
            tag = tag.lower().strip()
            if tag:
                counts[tag] = counts.get(tag, 0) + 1
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return [{"hashtag": f"#{t}", "frequency": c} for t, c in ranked]


def tiktok_trending_music(videos: list[dict], top_n: int = 20) -> list[dict]:
    """Extract trending music/audio from TikTok feed."""
    counts: dict[str, dict] = {}
    for v in videos:
        mid = v.get("music_id")
        if mid:
            if mid not in counts:
                counts[mid] = {
                    "music_id": mid,
                    "title": v.get("music_title"),
                    "author": v.get("music_author"),
                    "use_count": 0,
                }
            counts[mid]["use_count"] += 1
    ranked = sorted(counts.values(), key=lambda x: x["use_count"], reverse=True)
    return ranked[:top_n]


# ── Combined trend report ─────────────────────────────────────────────────────

def build_trend_report(
    yt_api_key: Optional[str],
    rapidapi_key: Optional[str],
    region: str = "US",
) -> dict:
    """Pull trends from all available sources and return a unified report."""
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "region": region,
        "youtube": {},
        "tiktok": {},
        "cross_platform_hashtags": [],
        "trending_music": [],
    }

    yt_videos = []
    if yt_api_key:
        try:
            yt_videos = youtube_trending(yt_api_key, region)
            report["youtube"]["trending_videos"] = yt_videos[:10]
            report["youtube"]["top_hashtags"] = youtube_trending_hashtags(yt_videos, 25)
            report["youtube"]["trending_music"] = youtube_search_trending_music(yt_api_key, region, 10)
        except Exception as e:
            report["youtube"]["error"] = str(e)

    tt_videos = []
    if rapidapi_key:
        try:
            tt_videos = tiktok_trending_via_rapidapi(rapidapi_key, region)
            report["tiktok"]["trending_videos"] = tt_videos[:10]
            report["tiktok"]["top_hashtags"] = tiktok_trending_hashtags(tt_videos, 25)
            report["tiktok"]["trending_music"] = tiktok_trending_music(tt_videos, 10)
        except Exception as e:
            report["tiktok"]["error"] = str(e)

    # Cross-platform hashtags (appear on both)
    yt_tags = {h["hashtag"] for h in report.get("youtube", {}).get("top_hashtags", [])}
    tt_tags = {h["hashtag"] for h in report.get("tiktok", {}).get("top_hashtags", [])}
    report["cross_platform_hashtags"] = sorted(yt_tags & tt_tags)

    # Unified music list
    music = []
    for m in report.get("tiktok", {}).get("trending_music", []):
        music.append({"source": "tiktok", **m})
    for m in report.get("youtube", {}).get("trending_music", []):
        music.append({"source": "youtube", **m})
    report["trending_music"] = music

    return report
