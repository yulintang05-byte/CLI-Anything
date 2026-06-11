"""
TikTok trend scraper — three-tier approach:
  1. pyktok     : scrape individual videos/user pages (no auth)
  2. Public API : unofficial trending/discover endpoints
  3. Fallback   : manual niche hashtag lookup via public web
"""
import os
import re
import json
import time
import random
import hashlib
from datetime import datetime
from typing import Optional
import requests

# Unofficial TikTok trending endpoints
TT_TRENDING_BASE = "https://www.tiktok.com/api/explore/item_list/"
TT_HASHTAG_BASE  = "https://www.tiktok.com/api/challenge/item_list/"
TT_DISCOVER_URL  = "https://www.tiktok.com/node/share/discover"

# User-Agent pool to avoid rate-limiting
_UAS = [
    "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 Chrome/112.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/605.1.15 Version/16.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/113.0.0.0 Safari/537.36",
]

_COMMON_HEADERS = {
    "Referer": "https://www.tiktok.com/",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}


def _ua() -> str:
    return random.choice(_UAS)


def _sleep():
    time.sleep(random.uniform(0.8, 2.2))


def _get_json(url: str, params: dict = None, timeout: int = 20) -> dict:
    headers = {**_COMMON_HEADERS, "User-Agent": _ua()}
    try:
        resp = requests.get(url, params=params, headers=headers,
                            timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        return resp.json()
    except (requests.RequestException, ValueError) as e:
        return {"error": str(e)}


def _parse_count(val) -> int:
    """Convert '1.2M' or int/str to int."""
    if isinstance(val, int):
        return val
    if isinstance(val, float):
        return int(val)
    val = str(val).strip().lower().replace(",", "")
    m = re.match(r"([\d.]+)([kmb]?)", val)
    if not m:
        return 0
    n, unit = float(m.group(1)), m.group(2)
    return int(n * {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}.get(unit, 1))


# ---------------------------------------------------------------------------
# Trending video fetcher (unofficial TikTok explore API)
# ---------------------------------------------------------------------------

def fetch_trending_videos(region: str = "US", max_results: int = 30) -> list[dict]:
    """
    Fetch trending TikTok videos using the unofficial explore API.
    Falls back to scraping the discover page if API fails.
    """
    params = {
        "categoryType": "0",
        "count": min(max_results, 30),
        "itemList": "[]",
        "language": "en",
        "region": region,
        "from_page": "fyp",
    }
    data = _get_json(TT_TRENDING_BASE, params)
    videos = _parse_video_list(data.get("itemList", []))
    if videos:
        return videos[:max_results]

    # Fallback: scrape discover page
    return _scrape_discover(region, max_results)


def _parse_video_item(item: dict) -> dict:
    """Normalize a TikTok video item from the API response."""
    author = item.get("author", {})
    stats  = item.get("stats", {})
    music  = item.get("music", {})
    video  = item.get("video", {})
    desc   = item.get("desc", "")

    hashtags = re.findall(r"#(\w+)", desc)

    return {
        "id":          item.get("id", ""),
        "description": desc,
        "author":      author.get("uniqueId", author.get("nickname", "")),
        "author_id":   author.get("id", ""),
        "plays":       _parse_count(stats.get("playCount", 0)),
        "likes":       _parse_count(stats.get("diggCount", 0)),
        "shares":      _parse_count(stats.get("shareCount", 0)),
        "comments":    _parse_count(stats.get("commentCount", 0)),
        "hashtags":    hashtags,
        "music_title": music.get("title", ""),
        "music_author": music.get("authorName", ""),
        "music_id":    music.get("id", ""),
        "duration":    video.get("duration", 0),
        "created":     datetime.utcfromtimestamp(
                           item.get("createTime", 0)).strftime("%Y-%m-%d"),
        "url":         f"https://www.tiktok.com/@{author.get('uniqueId', 'unknown')}/video/{item.get('id', '')}",
        "source":      "api",
    }


def _parse_video_list(items: list) -> list[dict]:
    return [_parse_video_item(i) for i in items if isinstance(i, dict)]


def _scrape_discover(region: str = "US", max_results: int = 30) -> list[dict]:
    """Scrape TikTok discover/trending page as HTML fallback."""
    url = "https://www.tiktok.com/trending"
    headers = {**_COMMON_HEADERS, "User-Agent": _ua()}
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        html = resp.text
    except requests.RequestException as e:
        return [{"error": str(e), "source": "scrape_fail"}]

    # Extract __NEXT_DATA__ from TikTok's Next.js page
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>',
                      html, re.DOTALL)
    if match:
        try:
            nd = json.loads(match.group(1))
            items = (nd.get("props", {}).get("pageProps", {})
                      .get("items", []))
            if items:
                return _parse_video_list(items)[:max_results]
        except (json.JSONDecodeError, KeyError):
            pass

    # Last resort: pull video IDs from href patterns
    ids = re.findall(r'/video/(\d{15,20})', html)
    users = re.findall(r'/@([\w.]+)/video/', html)
    out = []
    for i, (vid_id, user) in enumerate(zip(ids, users)):
        if i >= max_results:
            break
        out.append({
            "id":    vid_id,
            "author": user,
            "url":   f"https://www.tiktok.com/@{user}/video/{vid_id}",
            "source": "html_scrape",
        })
    return out


# ---------------------------------------------------------------------------
# Hashtag trend fetcher
# ---------------------------------------------------------------------------

def fetch_hashtag_videos(hashtag: str, max_results: int = 20) -> list[dict]:
    """Fetch recent TikTok videos for a specific hashtag."""
    tag = hashtag.lstrip("#")
    params = {
        "challengeName": tag,
        "count": min(max_results, 30),
        "cursor": 0,
    }
    data = _get_json(TT_HASHTAG_BASE, params)
    if "error" in data:
        return [{"error": data["error"], "hashtag": f"#{tag}"}]
    items = data.get("itemList", [])
    videos = _parse_video_list(items)
    for v in videos:
        v["queried_hashtag"] = f"#{tag}"
    return videos[:max_results]


def fetch_trending_hashtags(region: str = "US", count: int = 30) -> list[dict]:
    """
    Pull trending hashtags by analyzing trending videos.
    Also enriches with challenge-level stats when available.
    """
    videos = fetch_trending_videos(region=region, max_results=50)
    freq: dict[str, dict] = {}
    for v in videos:
        for ht in v.get("hashtags", []):
            key = ht.lower()
            if key not in freq:
                freq[key] = {"hashtag": f"#{ht}", "videos": 0, "total_plays": 0, "total_likes": 0}
            freq[key]["videos"] += 1
            freq[key]["total_plays"] += v.get("plays", 0)
            freq[key]["total_likes"] += v.get("likes", 0)

    ranked = sorted(freq.values(),
                    key=lambda x: (x["videos"], x["total_plays"]),
                    reverse=True)
    return ranked[:count]


# ---------------------------------------------------------------------------
# Music/audio trend fetcher
# ---------------------------------------------------------------------------

def fetch_trending_music(region: str = "US", max_results: int = 25) -> list[dict]:
    """Extract trending music/audio from trending TikTok videos."""
    videos = fetch_trending_videos(region=region, max_results=50)
    music_freq: dict[str, dict] = {}
    for v in videos:
        mid = v.get("music_id", "")
        title = v.get("music_title", "")
        author = v.get("music_author", "")
        if not mid and not title:
            continue
        key = mid or hashlib.md5(title.encode()).hexdigest()
        if key not in music_freq:
            music_freq[key] = {
                "music_id":    mid,
                "title":       title,
                "artist":      author,
                "video_count": 0,
                "total_plays": 0,
                "total_likes": 0,
            }
        music_freq[key]["video_count"] += 1
        music_freq[key]["total_plays"] += v.get("plays", 0)
        music_freq[key]["total_likes"] += v.get("likes", 0)

    ranked = sorted(music_freq.values(),
                    key=lambda x: (x["video_count"], x["total_plays"]),
                    reverse=True)
    return ranked[:max_results]


# ---------------------------------------------------------------------------
# User profile scraper (public data only)
# ---------------------------------------------------------------------------

def fetch_user_stats(username: str) -> dict:
    """Fetch public TikTok user stats."""
    username = username.lstrip("@")
    url = f"https://www.tiktok.com/@{username}"
    headers = {**_COMMON_HEADERS, "User-Agent": _ua()}
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        html = resp.text
    except requests.RequestException as e:
        return {"error": str(e)}

    # Try __NEXT_DATA__
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>',
                      html, re.DOTALL)
    if match:
        try:
            nd = json.loads(match.group(1))
            user_info = (nd.get("props", {}).get("pageProps", {})
                           .get("userInfo", {}))
            stats = user_info.get("stats", {})
            user  = user_info.get("user", {})
            return {
                "username":   username,
                "nickname":   user.get("nickname", username),
                "bio":        user.get("signature", ""),
                "verified":   user.get("verified", False),
                "followers":  _parse_count(stats.get("followerCount", 0)),
                "following":  _parse_count(stats.get("followingCount", 0)),
                "likes":      _parse_count(stats.get("heartCount", 0)),
                "video_count": _parse_count(stats.get("videoCount", 0)),
                "url":        f"https://www.tiktok.com/@{username}",
            }
        except (json.JSONDecodeError, KeyError):
            pass

    # Regex fallback
    def _re_stat(pattern: str) -> int:
        m = re.search(pattern, html)
        return _parse_count(m.group(1)) if m else 0

    return {
        "username":  username,
        "followers": _re_stat(r'"followerCount":(\d+)'),
        "following": _re_stat(r'"followingCount":(\d+)'),
        "likes":     _re_stat(r'"heartCount":(\d+)'),
        "videos":    _re_stat(r'"videoCount":(\d+)'),
        "url":       f"https://www.tiktok.com/@{username}",
    }
