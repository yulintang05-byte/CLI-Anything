"""TikTok trend scraper — uses TikTok Creative Center public API
(no auth required) for trending hashtags, songs, and creator data.
Also scrapes the Discover page for real-time hashtag trends."""

import json
import re
import time
from typing import Optional
import requests

# TikTok Creative Center public API — no auth required
CC_BASE = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend"
CC_HASHTAG_LIST = f"{CC_BASE}/hashtag/list"
CC_MUSIC_LIST   = f"{CC_BASE}/music/list"
CC_CREATOR_LIST = f"{CC_BASE}/creator/list"
CC_VIDEO_LIST   = f"{CC_BASE}/video/list"

# Public TikTok site for scraping
TIKTOK_DISCOVER_URL = "https://www.tiktok.com/discover"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://ads.tiktok.com/",
    "Origin": "https://ads.tiktok.com",
}

DEFAULT_PARAMS = {
    "period": 7,        # past 7 days
    "page": 1,
    "limit": 30,
    "order_by": "popular",
    "industry_id": "",
    "country_code": "US",
    "region_id": "",
}


def _cc_get(url: str, extra_params: dict = None, ms_token: Optional[str] = None) -> dict:
    params = dict(DEFAULT_PARAMS)
    if extra_params:
        params.update(extra_params)
    headers = dict(HEADERS)
    cookies = {}
    if ms_token:
        cookies["msToken"] = ms_token
    resp = requests.get(url, params=params, headers=headers, cookies=cookies, timeout=20)
    resp.raise_for_status()
    return resp.json()


# ── Hashtags ─────────────────────────────────────────────────────

def fetch_trending_hashtags(
    country: str = "US",
    period: int = 7,
    limit: int = 30,
    ms_token: Optional[str] = None,
) -> list:
    """Return trending TikTok hashtags from Creative Center."""
    try:
        data = _cc_get(CC_HASHTAG_LIST, {"country_code": country, "period": period, "limit": limit}, ms_token)
        items = data.get("data", {}).get("list", []) or data.get("data", []) or []
        results = []
        for item in items:
            results.append({
                "hashtag": f"#{item.get('hashtag_name', '')}",
                "id": item.get("hashtag_id", ""),
                "view_count": item.get("video_views", 0),
                "publish_count": item.get("publish_cnt", 0),
                "trend": item.get("trend", ""),
                "url": f"https://www.tiktok.com/tag/{item.get('hashtag_name', '')}",
            })
        return results
    except Exception as e:
        # Fall back to discover-page scrape
        return _scrape_discover_hashtags()


def _scrape_discover_hashtags() -> list:
    """Scrape TikTok Discover page for trending hashtags (fallback)."""
    try:
        resp = requests.get(TIKTOK_DISCOVER_URL, headers={
            **HEADERS, "Referer": "https://www.tiktok.com/"
        }, timeout=20)
        resp.raise_for_status()
        # Extract JSON embedded in Next.js __NEXT_DATA__ or window.__INITIAL_STATE__
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', resp.text, re.DOTALL)
        if match:
            page_data = json.loads(match.group(1))
            # Walk tree looking for hashtag lists
            tags = _walk_for_hashtags(page_data)
            if tags:
                return tags
        # Pattern 2: extract hashtag-looking strings from page
        tags_raw = re.findall(r'"challengeName"\s*:\s*"([^"]+)"', resp.text)
        views_raw = re.findall(r'"stats"\s*:\s*\{[^}]*"videoCount"\s*:\s*(\d+)', resp.text)
        results = []
        for i, tag in enumerate(tags_raw[:30]):
            view_count = int(views_raw[i]) if i < len(views_raw) else 0
            results.append({
                "hashtag": f"#{tag}",
                "id": "",
                "view_count": view_count,
                "publish_count": 0,
                "trend": "",
                "url": f"https://www.tiktok.com/tag/{tag}",
            })
        return results
    except Exception:
        return []


def _walk_for_hashtags(obj, depth=0) -> list:
    if depth > 10:
        return []
    results = []
    if isinstance(obj, dict):
        if "challengeName" in obj or "hashtagName" in obj:
            name = obj.get("challengeName") or obj.get("hashtagName", "")
            if name:
                results.append({
                    "hashtag": f"#{name}",
                    "id": obj.get("id", ""),
                    "view_count": obj.get("stats", {}).get("videoCount", 0) if isinstance(obj.get("stats"), dict) else 0,
                    "publish_count": 0,
                    "trend": "",
                    "url": f"https://www.tiktok.com/tag/{name}",
                })
        for v in obj.values():
            results.extend(_walk_for_hashtags(v, depth + 1))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(_walk_for_hashtags(item, depth + 1))
    return results[:30]


# ── Music ─────────────────────────────────────────────────────────

def fetch_trending_music(
    country: str = "US",
    period: int = 7,
    limit: int = 30,
    ms_token: Optional[str] = None,
) -> list:
    """Return trending TikTok songs from Creative Center."""
    try:
        data = _cc_get(CC_MUSIC_LIST, {"country_code": country, "period": period, "limit": limit}, ms_token)
        items = data.get("data", {}).get("list", []) or data.get("data", []) or []
        results = []
        for item in items:
            results.append({
                "title": item.get("music_name", ""),
                "artist": item.get("author", ""),
                "music_id": item.get("music_id", ""),
                "clip_count": item.get("clip_count", 0),
                "view_count": item.get("video_views", 0),
                "trend": item.get("trend", ""),
                "duration": item.get("duration", 0),
                "cover_url": item.get("cover_url", ""),
                "tiktok_url": f"https://www.tiktok.com/music/x-{item.get('music_id', '')}",
            })
        return results
    except Exception:
        return []


# ── Creators ─────────────────────────────────────────────────────

def fetch_trending_creators(
    country: str = "US",
    period: int = 7,
    limit: int = 20,
    ms_token: Optional[str] = None,
) -> list:
    """Return trending TikTok creators from Creative Center."""
    try:
        data = _cc_get(CC_CREATOR_LIST, {"country_code": country, "period": period, "limit": limit}, ms_token)
        items = data.get("data", {}).get("list", []) or data.get("data", []) or []
        results = []
        for item in items:
            results.append({
                "username": item.get("nick_name", ""),
                "handle": f"@{item.get('tt_user_name', '')}",
                "follower_count": item.get("follower_cnt", 0),
                "like_count": item.get("like_cnt", 0),
                "video_count": item.get("video_cnt", 0),
                "avg_views": item.get("avg_views", 0),
                "niche": item.get("industry", {}).get("name", "") if isinstance(item.get("industry"), dict) else "",
                "country": item.get("country_code", ""),
                "profile_url": f"https://www.tiktok.com/@{item.get('tt_user_name', '')}",
                "avatar": item.get("avatar_url", ""),
            })
        return results
    except Exception:
        return []


# ── Trending Videos ───────────────────────────────────────────────

def fetch_trending_videos(
    country: str = "US",
    period: int = 7,
    limit: int = 20,
    ms_token: Optional[str] = None,
) -> list:
    """Return trending TikTok videos from Creative Center."""
    try:
        data = _cc_get(CC_VIDEO_LIST, {"country_code": country, "period": period, "limit": limit}, ms_token)
        items = data.get("data", {}).get("list", []) or data.get("data", []) or []
        results = []
        for item in items:
            results.append({
                "video_id": item.get("video_id", ""),
                "desc": item.get("desc", "")[:200],
                "author": item.get("author", {}).get("unique_id", "") if isinstance(item.get("author"), dict) else "",
                "play_count": item.get("statistics", {}).get("play_count", 0) if isinstance(item.get("statistics"), dict) else 0,
                "like_count": item.get("statistics", {}).get("digg_count", 0) if isinstance(item.get("statistics"), dict) else 0,
                "comment_count": item.get("statistics", {}).get("comment_count", 0) if isinstance(item.get("statistics"), dict) else 0,
                "share_count": item.get("statistics", {}).get("share_count", 0) if isinstance(item.get("statistics"), dict) else 0,
                "music_title": item.get("music", {}).get("title", "") if isinstance(item.get("music"), dict) else "",
                "hashtags": [t.get("name", "") for t in item.get("challenges", []) if isinstance(t, dict)][:8],
                "url": f"https://www.tiktok.com/@{item.get('author', {}).get('unique_id', '') if isinstance(item.get('author'), dict) else ''}/video/{item.get('video_id', '')}",
            })
        return results
    except Exception:
        return []


# ── Niche hashtag search ──────────────────────────────────────────

def search_hashtag_stats(hashtag: str, ms_token: Optional[str] = None) -> dict:
    """Get stats for a specific hashtag via Creative Center."""
    tag = hashtag.lstrip("#")
    try:
        url = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/info"
        params = {"hashtag_name": tag}
        headers = dict(HEADERS)
        cookies = {"msToken": ms_token} if ms_token else {}
        resp = requests.get(url, params=params, headers=headers, cookies=cookies, timeout=15)
        resp.raise_for_status()
        data = resp.json().get("data", {})
        return {
            "hashtag": f"#{tag}",
            "view_count": data.get("video_views", 0),
            "publish_count": data.get("publish_cnt", 0),
            "trend": data.get("trend", ""),
        }
    except Exception:
        return {"hashtag": f"#{tag}", "view_count": 0, "publish_count": 0, "trend": ""}
