"""TikTok trend scraper — trending hashtags, sounds, and creators.

Scraping Strategy (in priority order):
  1. TikTok Research API  — official, requires approved developer account
  2. ms_token web scrape  — unofficial, uses httpx with browser headers
  3. Cached / demo data   — fallback when both above are unavailable

TikTok Research API: https://developers.tiktok.com/products/research-api/
Set your access token via:
    trendscraper config set --tiktok-token YOUR_TOKEN
    or: export TIKTOK_ACCESS_TOKEN=YOUR_TOKEN
"""
from __future__ import annotations

import os
import re
import json
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any
from collections import Counter

import httpx

_CACHE_DIR = Path.home() / ".config" / "cli-anything-trendscraper" / "cache"
_CACHE_TTL_SECONDS = 1800  # 30 min — TikTok trends move fast

_RESEARCH_API_BASE = "https://open.tiktokapis.com/v2"

# Known high-engagement niches for theme page research
TRENDING_NICHES = [
    "motivational", "luxury", "cars", "fitness", "travel",
    "food", "fashion", "beauty", "gaming", "pets",
    "finance", "crypto", "sports", "comedy", "dance",
    "aesthetics", "lofi", "nature", "diy", "tech",
]


def _get_token() -> str | None:
    token = os.environ.get("TIKTOK_ACCESS_TOKEN")
    if token:
        return token
    cfg_file = Path.home() / ".config" / "cli-anything-trendscraper" / "config.json"
    if cfg_file.exists():
        cfg = json.loads(cfg_file.read_text())
        return cfg.get("tiktok_access_token")
    return None


def _cache_path(key: str) -> Path:
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    h = hashlib.md5(key.encode()).hexdigest()
    return _CACHE_DIR / f"tt_{h}.json"


def _load_cache(key: str) -> dict | None:
    p = _cache_path(key)
    if not p.exists():
        return None
    data = json.loads(p.read_text())
    if time.time() - data.get("_cached_at", 0) > _CACHE_TTL_SECONDS:
        return None
    return data


def _save_cache(key: str, data: dict) -> None:
    data["_cached_at"] = time.time()
    _cache_path(key).write_text(json.dumps(data, indent=2))


def fetch_trending_hashtags(
    region: str = "US",
    limit: int = 30,
    token: str | None = None,
) -> dict[str, Any]:
    """Fetch trending TikTok hashtags.

    Tries Research API first, then scrape fallback.
    """
    cache_key = f"tt_hashtags_{region}_{limit}"
    cached = _load_cache(cache_key)
    if cached:
        return cached

    tok = token or _get_token()
    if tok:
        result = _fetch_hashtags_research_api(tok, region, limit)
    else:
        result = _fetch_hashtags_scrape(region, limit)

    _save_cache(cache_key, result)
    return result


def _fetch_hashtags_research_api(token: str, region: str, limit: int) -> dict[str, Any]:
    """Use TikTok Research API to query trending hashtags."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    body = {
        "query": {
            "and": [{"operation": "EQ", "field_name": "region_code", "field_values": [region]}],
        },
        "start_date": _days_ago(7),
        "end_date": _today(),
        "max_count": limit,
        "cursor": 0,
    }
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                f"{_RESEARCH_API_BASE}/research/video/query/",
                headers=headers,
                json=body,
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        return _empty_tt_result(f"research_api_error: {exc}")

    hashtags: list[str] = []
    sounds: list[str] = []
    videos = []

    for item in data.get("data", {}).get("videos", []):
        video_hashtags = [h.get("name", "") for h in item.get("hashtag_names", [])]
        hashtags.extend(video_hashtags)
        music = item.get("music_id") or item.get("bgm_author_name", "")
        if music:
            sounds.append(str(music))
        videos.append({
            "id": item.get("id"),
            "author": item.get("author_name"),
            "likes": item.get("like_count", 0),
            "shares": item.get("share_count", 0),
            "comments": item.get("comment_count", 0),
            "views": item.get("view_count", 0),
            "hashtags": video_hashtags,
            "music": item.get("music_id"),
            "region": item.get("region_code"),
        })

    return _build_tt_result(hashtags, sounds, videos, region, "research_api")


def _fetch_hashtags_scrape(region: str, limit: int) -> dict[str, Any]:
    """Scrape TikTok discover/trending page for hashtags and sounds."""
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.tiktok.com/",
    }
    hashtags: list[str] = []
    sounds: list[str] = []
    videos: list[dict] = []

    # Attempt 1: TikTok trending page
    try:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            resp = client.get("https://www.tiktok.com/trending", headers=headers)
            html = resp.text

        # Extract SIGI_STATE or __NEXT_DATA__ JSON
        for pattern in [
            r'<script id="SIGI_STATE"[^>]*>(\{.+?\})</script>',
            r'<script id="__NEXT_DATA__"[^>]*>(\{.+?\})</script>',
        ]:
            m = re.search(pattern, html, re.DOTALL)
            if m:
                raw = json.loads(m.group(1))
                hashtags, sounds, videos = _parse_tt_page_data(raw, limit)
                break
    except Exception:
        pass

    # Attempt 2: discover page
    if not hashtags:
        try:
            with httpx.Client(timeout=30, follow_redirects=True) as client:
                resp = client.get("https://www.tiktok.com/discover", headers=headers)
                html = resp.text
            hashtags_raw = re.findall(r'"challengeName"\s*:\s*"([^"]+)"', html)
            sound_raw = re.findall(r'"musicName"\s*:\s*"([^"]+)"', html)
            hashtags.extend([h.lower() for h in hashtags_raw[:limit]])
            sounds.extend(sound_raw[:20])
        except Exception:
            pass

    return _build_tt_result(hashtags, sounds, videos, region, "scrape")


def _parse_tt_page_data(data: dict, limit: int) -> tuple[list[str], list[str], list[dict]]:
    hashtags: list[str] = []
    sounds: list[str] = []
    videos: list[dict] = []

    # Walk common paths in SIGI_STATE
    for key in ["ItemModule", "videoData"]:
        items = data.get(key, {})
        if isinstance(items, dict):
            items = list(items.values())
        if isinstance(items, list):
            for item in items[:limit]:
                if not isinstance(item, dict):
                    continue
                challenges = item.get("challenges", item.get("textExtra", []))
                for ch in challenges:
                    tag = ch.get("hashtagName", ch.get("challengeName", ""))
                    if tag:
                        hashtags.append(tag.lower())
                music = item.get("music", {})
                if music:
                    sounds.append(music.get("title", music.get("authorName", "")))
                stats = item.get("stats", item.get("statistics", {}))
                videos.append({
                    "id": item.get("id"),
                    "author": (item.get("author", {}) or {}).get("uniqueId", ""),
                    "likes": stats.get("diggCount", 0),
                    "shares": stats.get("shareCount", 0),
                    "comments": stats.get("commentCount", 0),
                    "views": stats.get("playCount", 0),
                    "hashtags": hashtags[-5:],
                    "music": music.get("title", "") if music else "",
                })
    return hashtags, sounds, videos


def _build_tt_result(
    hashtags: list[str],
    sounds: list[str],
    videos: list[dict],
    region: str,
    source: str,
) -> dict[str, Any]:
    hashtag_counts = Counter(hashtags).most_common(30)
    sound_counts = Counter(s for s in sounds if s).most_common(20)
    return {
        "platform": "tiktok",
        "region": region,
        "fetched_at": datetime.utcnow().isoformat(),
        "video_count": len(videos),
        "videos": videos[:50],
        "trending_hashtags": [{"tag": h, "count": c} for h, c in hashtag_counts],
        "trending_sounds": [{"title": s, "count": c} for s, c in sound_counts],
        "source": source,
    }


def _empty_tt_result(reason: str) -> dict[str, Any]:
    return {
        "platform": "tiktok",
        "region": "unknown",
        "fetched_at": datetime.utcnow().isoformat(),
        "video_count": 0,
        "videos": [],
        "trending_hashtags": [],
        "trending_sounds": [],
        "source": reason,
        "error": reason,
    }


def fetch_trending_sounds(region: str = "US", limit: int = 20, token: str | None = None) -> dict[str, Any]:
    """Fetch trending TikTok sounds/music."""
    result = fetch_trending_hashtags(region=region, limit=limit, token=token)
    return {
        "platform": "tiktok",
        "region": region,
        "fetched_at": result.get("fetched_at"),
        "trending_sounds": result.get("trending_sounds", []),
        "source": result.get("source"),
    }


def fetch_hashtag_stats(hashtag: str, token: str | None = None) -> dict[str, Any]:
    """Query stats for a specific TikTok hashtag via Research API."""
    tok = token or _get_token()
    if not tok:
        return {"error": "tiktok_access_token required", "hashtag": hashtag}

    headers = {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}
    body = {
        "query": {
            "and": [
                {
                    "operation": "IN",
                    "field_name": "hashtag_name",
                    "field_values": [hashtag],
                }
            ]
        },
        "start_date": _days_ago(30),
        "end_date": _today(),
        "max_count": 100,
    }
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                f"{_RESEARCH_API_BASE}/research/video/query/",
                headers=headers,
                json=body,
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        return {"error": str(exc), "hashtag": hashtag}

    videos = data.get("data", {}).get("videos", [])
    total_views = sum(v.get("view_count", 0) for v in videos)
    total_likes = sum(v.get("like_count", 0) for v in videos)

    return {
        "hashtag": hashtag,
        "fetched_at": datetime.utcnow().isoformat(),
        "sample_video_count": len(videos),
        "total_views_sample": total_views,
        "total_likes_sample": total_likes,
        "avg_views": total_views // len(videos) if videos else 0,
        "avg_likes": total_likes // len(videos) if videos else 0,
        "source": "research_api",
    }


def _days_ago(n: int) -> str:
    from datetime import timedelta
    d = datetime.utcnow() - timedelta(days=n)
    return d.strftime("%Y%m%d")


def _today() -> str:
    return datetime.utcnow().strftime("%Y%m%d")
