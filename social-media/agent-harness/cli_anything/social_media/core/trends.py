"""YouTube & TikTok viral trend scraper."""

import json
import re
import time
from datetime import datetime
from typing import Optional
import urllib.request
import urllib.parse


def _http_get(url: str, headers: dict = None) -> str:
    req = urllib.request.Request(url, headers=headers or {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


# ─── YouTube ──────────────────────────────────────────────────────────────────

def youtube_trending(category: str = "all", region: str = "US", max_results: int = 20) -> dict:
    """Fetch YouTube trending videos via yt-dlp (no API key needed)."""
    try:
        import subprocess, sys
        category_map = {
            "all": "0", "music": "10", "gaming": "20",
            "film": "1", "entertainment": "24", "howto": "26",
        }
        cat_id = category_map.get(category.lower(), "0")
        url = f"https://www.youtube.com/feed/trending?bp=Q{cat_id}IBAA%3D"

        result = subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--dump-json", "--flat-playlist",
             f"--playlist-end={max_results}", "--no-warnings", url],
            capture_output=True, text=True, timeout=60
        )
        videos = []
        for line in result.stdout.strip().splitlines():
            if not line.strip():
                continue
            try:
                v = json.loads(line)
                videos.append({
                    "title": v.get("title", ""),
                    "id": v.get("id", ""),
                    "url": f"https://youtube.com/watch?v={v.get('id','')}",
                    "channel": v.get("uploader") or v.get("channel", ""),
                    "views": v.get("view_count"),
                    "duration": v.get("duration"),
                    "upload_date": v.get("upload_date", ""),
                    "description": (v.get("description") or "")[:200],
                })
            except json.JSONDecodeError:
                pass
        return {
            "platform": "youtube",
            "category": category,
            "region": region,
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "count": len(videos),
            "videos": videos,
        }
    except Exception as exc:
        return {"platform": "youtube", "error": str(exc), "videos": []}


def youtube_trending_hashtags(region: str = "US") -> dict:
    """Extract hashtags from YouTube trending video titles/descriptions."""
    data = youtube_trending(region=region, max_results=30)
    tag_freq: dict[str, int] = {}
    for v in data.get("videos", []):
        text = f"{v['title']} {v['description']}"
        tags = re.findall(r"#(\w+)", text)
        for t in tags:
            tag_freq[t.lower()] = tag_freq.get(t.lower(), 0) + 1

    sorted_tags = sorted(tag_freq.items(), key=lambda x: x[1], reverse=True)
    return {
        "platform": "youtube",
        "region": region,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "hashtags": [{"tag": f"#{t}", "frequency": c} for t, c in sorted_tags[:50]],
    }


def youtube_trending_music(region: str = "US", max_results: int = 20) -> dict:
    """Fetch YouTube Music trending charts."""
    data = youtube_trending(category="music", region=region, max_results=max_results)
    return {
        "platform": "youtube_music",
        "region": region,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "tracks": data.get("videos", []),
    }


# ─── TikTok ───────────────────────────────────────────────────────────────────

def tiktok_trending_hashtags(region: str = "US") -> dict:
    """Fetch TikTok trending hashtags from public discovery page."""
    try:
        # TikTok public trending hashtag endpoint
        url = "https://www.tiktok.com/api/explore/item_list/?aid=1988&count=30&type=5"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.tiktok.com/",
            "Accept": "application/json, text/plain, */*",
        }
        html = _http_get("https://www.tiktok.com/trending", headers)
        # Extract __NEXT_DATA__ JSON
        match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
        hashtags = []
        if match:
            try:
                nd = json.loads(match.group(1))
                props = nd.get("props", {}).get("pageProps", {})
                # Navigate possible trending data paths
                items = (
                    props.get("trendingData", {}).get("challengeList", [])
                    or props.get("itemList", [])
                )
                for item in items[:30]:
                    ch = item.get("challengeInfo", {}).get("challenge", item)
                    name = ch.get("title") or ch.get("challengeName", "")
                    views = ch.get("stats", {}).get("videoCount") or ch.get("videoCount")
                    if name:
                        hashtags.append({"tag": f"#{name}", "video_count": views})
            except (json.JSONDecodeError, AttributeError):
                pass

        # Fallback: scrape visible hashtag patterns
        if not hashtags:
            tags = re.findall(r'challengeName["\s:]+([^"&,\s]{2,40})', html)
            hashtags = [{"tag": f"#{t}", "video_count": None} for t in set(tags[:30])]

        return {
            "platform": "tiktok",
            "region": region,
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "hashtags": hashtags,
            "note": "Public data only. For full access, configure TikTok Research API credentials.",
        }
    except Exception as exc:
        return {
            "platform": "tiktok",
            "error": str(exc),
            "hashtags": [],
            "note": "Set up TikTok Research API at developers.tiktok.com for reliable access.",
        }


def tiktok_trending_music(region: str = "US") -> dict:
    """Fetch TikTok trending sounds/music."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
            "Referer": "https://www.tiktok.com/",
        }
        html = _http_get("https://www.tiktok.com/music/trending", headers)
        match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
        tracks = []
        if match:
            try:
                nd = json.loads(match.group(1))
                items = nd.get("props", {}).get("pageProps", {}).get("itemList", [])
                seen = set()
                for item in items:
                    m = item.get("music", {})
                    tid = m.get("id", "")
                    if tid and tid not in seen:
                        seen.add(tid)
                        tracks.append({
                            "title": m.get("title", ""),
                            "author": m.get("authorName", ""),
                            "id": tid,
                            "duration": m.get("duration"),
                            "cover": m.get("coverLarge", ""),
                        })
            except (json.JSONDecodeError, AttributeError):
                pass

        # Fallback: extract music names from page
        if not tracks:
            names = re.findall(r'"title"\s*:\s*"([^"]{3,80})"', html)
            tracks = [{"title": n, "author": "", "id": ""} for n in list(dict.fromkeys(names))[:20]]

        return {
            "platform": "tiktok",
            "region": region,
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "tracks": tracks,
            "note": "Public data only. Use TikTok Research API for complete access.",
        }
    except Exception as exc:
        return {
            "platform": "tiktok",
            "error": str(exc),
            "tracks": [],
        }


def tiktok_trending_videos(region: str = "US", max_results: int = 20) -> dict:
    """Fetch TikTok trending/FYP videos metadata (public)."""
    try:
        import subprocess, sys
        result = subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--dump-json", "--flat-playlist",
             f"--playlist-end={max_results}", "--no-warnings",
             "https://www.tiktok.com/trending"],
            capture_output=True, text=True, timeout=60
        )
        videos = []
        for line in result.stdout.strip().splitlines():
            if not line.strip():
                continue
            try:
                v = json.loads(line)
                videos.append({
                    "title": v.get("title", ""),
                    "id": v.get("id", ""),
                    "url": v.get("webpage_url", ""),
                    "author": v.get("uploader", ""),
                    "likes": v.get("like_count"),
                    "views": v.get("view_count"),
                    "duration": v.get("duration"),
                    "hashtags": re.findall(r"#(\w+)", v.get("description", "")),
                })
            except json.JSONDecodeError:
                pass
        return {
            "platform": "tiktok",
            "region": region,
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "count": len(videos),
            "videos": videos,
        }
    except Exception as exc:
        return {"platform": "tiktok", "error": str(exc), "videos": []}


# ─── Cross-platform ────────────────────────────────────────────────────────────

def cross_platform_trends(region: str = "US") -> dict:
    """Aggregate trends across YouTube + TikTok."""
    yt = youtube_trending(region=region, max_results=10)
    tt_tags = tiktok_trending_hashtags(region=region)
    yt_tags = youtube_trending_hashtags(region=region)
    tt_music = tiktok_trending_music(region=region)

    # Find hashtags appearing on both platforms
    yt_tag_set = {h["tag"].lower() for h in yt_tags.get("hashtags", [])}
    tt_tag_set = {h["tag"].lower() for h in tt_tags.get("hashtags", [])}
    cross_tags = list(yt_tag_set & tt_tag_set)

    return {
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "region": region,
        "youtube_top_videos": yt.get("videos", [])[:5],
        "youtube_top_hashtags": yt_tags.get("hashtags", [])[:10],
        "tiktok_top_hashtags": tt_tags.get("hashtags", [])[:10],
        "tiktok_trending_music": tt_music.get("tracks", [])[:5],
        "cross_platform_hashtags": cross_tags[:10],
        "insight": (
            f"Found {len(cross_tags)} hashtags trending on BOTH YouTube and TikTok. "
            "Use these for maximum cross-platform reach."
        ),
    }
