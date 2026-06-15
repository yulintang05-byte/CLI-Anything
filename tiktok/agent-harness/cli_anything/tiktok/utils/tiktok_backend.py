"""TikTok data backend — fetches trends, hashtags, and music via multiple APIs."""

import os
import json
import time
import requests
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".cli-anything-tiktok"
CONFIG_FILE = CONFIG_DIR / "config.json"

RAPIDAPI_HOST = "tiktok-api6.p.rapidapi.com"
APIFY_BASE = "https://api.apify.com/v2"

# ── Config management ────────────────────────────────────────────

def load_config() -> dict:
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}

def save_config(data: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2))

def get_rapidapi_key() -> Optional[str]:
    cfg = load_config()
    return cfg.get("rapidapi_key") or os.environ.get("RAPIDAPI_KEY")

def get_apify_token() -> Optional[str]:
    cfg = load_config()
    return cfg.get("apify_token") or os.environ.get("APIFY_TOKEN")

# ── Trending videos ──────────────────────────────────────────────

def fetch_trending_videos(region: str = "US", limit: int = 20) -> list:
    """Fetch trending TikTok videos via RapidAPI TikTok endpoint."""
    key = get_rapidapi_key()
    if not key:
        return _mock_trending_videos(limit)
    headers = {
        "x-rapidapi-key": key,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }
    try:
        resp = requests.get(
            f"https://{RAPIDAPI_HOST}/trending/feed",
            headers=headers,
            params={"region": region, "count": limit},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        items = data.get("itemList", data.get("data", []))
        return [_normalize_video(v) for v in items[:limit]]
    except Exception as e:
        raise RuntimeError(f"Failed to fetch trending videos: {e}")

def _normalize_video(raw: dict) -> dict:
    stats = raw.get("stats", raw.get("statistics", {}))
    author = raw.get("author", raw.get("authorMeta", {}))
    music = raw.get("music", raw.get("musicMeta", {}))
    desc = raw.get("desc", raw.get("text", ""))
    return {
        "id": raw.get("id", ""),
        "description": desc,
        "author": author.get("uniqueId", author.get("nickName", "")),
        "author_followers": author.get("followerCount", 0),
        "views": stats.get("playCount", stats.get("videoPlayCount", 0)),
        "likes": stats.get("diggCount", stats.get("heartCount", 0)),
        "comments": stats.get("commentCount", 0),
        "shares": stats.get("shareCount", 0),
        "music_title": music.get("title", ""),
        "music_author": music.get("authorName", ""),
        "music_id": music.get("id", ""),
        "hashtags": [h.get("name", h) if isinstance(h, dict) else h
                     for h in raw.get("textExtra", [])
                     if isinstance(h, dict) and h.get("hashtagName") or isinstance(h, str)],
        "duration": raw.get("video", {}).get("duration", 0),
        "create_time": raw.get("createTime", 0),
    }

def _mock_trending_videos(limit: int) -> list:
    """Return sample structure when no API key configured."""
    samples = [
        {"id": "demo1", "description": "POV: you discovered this viral trend #fyp #viral",
         "author": "demo_creator", "author_followers": 500000,
         "views": 12500000, "likes": 890000, "comments": 14200, "shares": 45000,
         "music_title": "Trending Sound", "music_author": "Artist Name", "music_id": "music1",
         "hashtags": ["fyp", "viral", "trending"], "duration": 15, "create_time": int(time.time())},
    ]
    return (samples * ((limit // len(samples)) + 1))[:limit]

# ── Trending hashtags ────────────────────────────────────────────

def fetch_trending_hashtags(keyword: str = "", region: str = "US", limit: int = 30) -> list:
    """Fetch trending hashtags via Apify TikTok Trending Hashtags Scraper."""
    token = get_apify_token()
    if not token:
        return _mock_trending_hashtags(limit)
    try:
        run_resp = requests.post(
            f"{APIFY_BASE}/acts/scrapeengine~tiktok-trending-hashtags-scraper/runs",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"keyword": keyword or "trending", "region": region, "maxItems": limit},
            timeout=20,
        )
        run_resp.raise_for_status()
        run_id = run_resp.json()["data"]["id"]
        # poll for completion
        for _ in range(30):
            time.sleep(3)
            status_resp = requests.get(
                f"{APIFY_BASE}/actor-runs/{run_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            if status_resp.json()["data"]["status"] in ("SUCCEEDED", "FAILED"):
                break
        dataset_id = status_resp.json()["data"]["defaultDatasetId"]
        items_resp = requests.get(
            f"{APIFY_BASE}/datasets/{dataset_id}/items",
            headers={"Authorization": f"Bearer {token}"},
            params={"limit": limit},
            timeout=15,
        )
        return items_resp.json()
    except Exception as e:
        raise RuntimeError(f"Failed to fetch hashtags: {e}")

def _mock_trending_hashtags(limit: int) -> list:
    tags = [
        {"hashtag": "fyp", "views": 45000000000, "videos": 950000000, "trend": "stable"},
        {"hashtag": "viral", "views": 31000000000, "videos": 620000000, "trend": "up"},
        {"hashtag": "foryou", "views": 28000000000, "videos": 510000000, "trend": "stable"},
        {"hashtag": "trending", "views": 9800000000, "videos": 180000000, "trend": "up"},
        {"hashtag": "tiktok", "views": 8200000000, "videos": 150000000, "trend": "stable"},
        {"hashtag": "comedy", "views": 4100000000, "videos": 85000000, "trend": "up"},
        {"hashtag": "dance", "views": 3900000000, "videos": 72000000, "trend": "up"},
        {"hashtag": "motivation", "views": 2700000000, "videos": 52000000, "trend": "up"},
        {"hashtag": "aesthetic", "views": 2300000000, "videos": 41000000, "trend": "up"},
        {"hashtag": "lifestyle", "views": 1900000000, "videos": 38000000, "trend": "stable"},
        {"hashtag": "businesstips", "views": 890000000, "videos": 12000000, "trend": "up"},
        {"hashtag": "makemoney", "views": 760000000, "videos": 9800000, "trend": "up"},
        {"hashtag": "ai", "views": 650000000, "videos": 8200000, "trend": "up"},
        {"hashtag": "entrepreneur", "views": 580000000, "videos": 7100000, "trend": "up"},
        {"hashtag": "themepage", "views": 320000000, "videos": 4200000, "trend": "up"},
    ]
    return tags[:limit]

# ── Trending music/sounds ────────────────────────────────────────

def fetch_trending_music(region: str = "US", limit: int = 20) -> list:
    """Fetch trending TikTok sounds/music."""
    key = get_rapidapi_key()
    if not key:
        return _mock_trending_music(limit)
    headers = {
        "x-rapidapi-key": key,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }
    try:
        resp = requests.get(
            f"https://{RAPIDAPI_HOST}/music/trending",
            headers=headers,
            params={"region": region, "count": limit},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        items = data.get("musicList", data.get("data", []))
        return [_normalize_music(m) for m in items[:limit]]
    except Exception as e:
        raise RuntimeError(f"Failed to fetch trending music: {e}")

def _normalize_music(raw: dict) -> dict:
    stats = raw.get("stats", {})
    return {
        "id": raw.get("id", ""),
        "title": raw.get("title", ""),
        "author": raw.get("authorName", raw.get("author", "")),
        "duration": raw.get("duration", 0),
        "video_count": stats.get("videoCount", raw.get("videoCount", 0)),
        "cover_url": raw.get("coverMedium", raw.get("coverLarge", "")),
        "play_url": raw.get("playUrl", ""),
        "is_original": raw.get("original", False),
        "album": raw.get("album", ""),
        "trend": "up" if stats.get("videoCount", 0) > 100000 else "new",
    }

def _mock_trending_music(limit: int) -> list:
    sounds = [
        {"id": "s1", "title": "Aesthetic Lo-Fi Beat", "author": "Lo-Fi Studio",
         "duration": 60, "video_count": 4800000, "cover_url": "", "play_url": "",
         "is_original": False, "album": "", "trend": "up"},
        {"id": "s2", "title": "Viral EDM Drop", "author": "EDM Artist",
         "duration": 30, "video_count": 3200000, "cover_url": "", "play_url": "",
         "is_original": False, "album": "", "trend": "up"},
        {"id": "s3", "title": "Motivational Speech Mix", "author": "Motivation Creator",
         "duration": 45, "video_count": 2100000, "cover_url": "", "play_url": "",
         "is_original": True, "album": "", "trend": "up"},
    ]
    return (sounds * ((limit // len(sounds)) + 1))[:limit]

# ── Account info ─────────────────────────────────────────────────

def fetch_account_info(username: str) -> dict:
    """Fetch TikTok account/profile data."""
    key = get_rapidapi_key()
    if not key:
        return {"username": username, "note": "Configure RAPIDAPI_KEY for real data"}
    headers = {
        "x-rapidapi-key": key,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }
    try:
        resp = requests.get(
            f"https://{RAPIDAPI_HOST}/user/info",
            headers=headers,
            params={"uniqueId": username},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        user = data.get("userInfo", data.get("data", {}).get("user", {}))
        stats = data.get("statsV2", data.get("data", {}).get("stats", {}))
        return {
            "username": user.get("uniqueId", username),
            "display_name": user.get("nickname", ""),
            "bio": user.get("signature", ""),
            "followers": int(stats.get("followerCount", 0)),
            "following": int(stats.get("followingCount", 0)),
            "likes": int(stats.get("heartCount", 0)),
            "videos": int(stats.get("videoCount", 0)),
            "verified": user.get("verified", False),
            "private": user.get("privateAccount", False),
        }
    except Exception as e:
        raise RuntimeError(f"Failed to fetch account info: {e}")

# ── Hashtag analytics ────────────────────────────────────────────

def fetch_hashtag_analytics(hashtag: str) -> dict:
    """Fetch detailed analytics for a specific hashtag."""
    key = get_rapidapi_key()
    if not key:
        return {
            "hashtag": hashtag,
            "views": 0,
            "videos": 0,
            "note": "Configure RAPIDAPI_KEY for real analytics",
        }
    headers = {
        "x-rapidapi-key": key,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }
    try:
        resp = requests.get(
            f"https://{RAPIDAPI_HOST}/hashtag/info",
            headers=headers,
            params={"name": hashtag},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        challenge = data.get("challengeInfo", data.get("data", {}))
        stats = challenge.get("stats", challenge.get("challengeAnnex", {}))
        return {
            "hashtag": hashtag,
            "title": challenge.get("challenge", {}).get("title", hashtag),
            "views": stats.get("viewCount", 0),
            "videos": stats.get("videoCount", 0),
            "description": challenge.get("challenge", {}).get("desc", ""),
        }
    except Exception as e:
        raise RuntimeError(f"Failed to fetch hashtag analytics: {e}")
