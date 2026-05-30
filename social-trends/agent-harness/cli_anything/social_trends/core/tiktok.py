"""TikTok trend scraper — uses public TikTok endpoints for trending content."""

import json
import re
import time
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

import requests

_CACHE_DIR = Path.home() / ".cli-anything-social-trends" / "cache"
_CACHE_TTL = 1800  # 30 min (TikTok trends move fast)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
}


def _cache_path(key: str) -> Path:
    h = hashlib.md5(key.encode()).hexdigest()
    return _CACHE_DIR / f"tt_{h}.json"


def _read_cache(key: str) -> dict | None:
    p = _cache_path(key)
    if not p.exists():
        return None
    try:
        with open(p) as f:
            data = json.load(f)
        if time.time() - data.get("_ts", 0) > _CACHE_TTL:
            return None
        return data
    except (json.JSONDecodeError, IOError):
        return None


def _write_cache(key: str, data: dict):
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    data["_ts"] = time.time()
    try:
        with open(_cache_path(key), "w") as f:
            json.dump(data, f)
    except IOError:
        pass


def fetch_trending_tiktok(
    region: str = "US",
    max_results: int = 30,
    use_cache: bool = True,
) -> dict:
    """
    Fetch TikTok trending videos, hashtags, and sounds.

    Args:
        region: region code (US, GB, etc.)
        max_results: max videos to return
        use_cache: use local cache

    Returns:
        dict with keys: videos, hashtags, music, fetched_at, source, region
    """
    cache_key = f"tt_trending_{region}_{max_results}"
    if use_cache:
        cached = _read_cache(cache_key)
        if cached:
            cached["from_cache"] = True
            return cached

    result = _fetch_trending_page(region, max_results)
    result["fetched_at"] = datetime.now(timezone.utc).isoformat()
    result["region"] = region

    if use_cache:
        _write_cache(cache_key, result)

    return result


def _fetch_trending_page(region: str, max_results: int) -> dict:
    """Scrape TikTok trending via their internal API."""
    # TikTok's public trending/discover API
    url = "https://www.tiktok.com/api/explore/item_list/"
    params = {
        "aid": "1988",
        "app_language": "en",
        "app_name": "tiktok_web",
        "channel": "tiktok_web",
        "count": min(max_results, 30),
        "device_platform": "web_pc",
        "focus_state": "true",
        "from_page": "fyp",
        "history_len": "2",
        "is_fullscreen": "false",
        "is_page_visible": "true",
        "itemID": "1",
        "language": "en",
        "os": "windows",
        "priority_region": region,
        "pullType": "1",
        "region": region,
        "screen_height": "900",
        "screen_width": "1440",
        "webcast_language": "en",
    }

    try:
        resp = requests.get(url, params=params, headers=_HEADERS, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return _parse_tiktok_item_list(data, max_results)
    except Exception:
        pass

    # Fallback: scrape trending discover page
    return _fetch_discover_fallback(region, max_results)


def _parse_tiktok_item_list(data: dict, max_results: int) -> dict:
    items = data.get("itemList", [])
    videos = []
    hashtag_counts: dict[str, int] = {}
    music_tracks: dict[str, dict] = {}

    for item in items[:max_results]:
        desc = item.get("desc", "")
        stats = item.get("stats", {})
        author = item.get("author", {})
        music = item.get("music", {})
        video = item.get("video", {})

        play_count = stats.get("playCount", 0)
        like_count = stats.get("diggCount", 0)
        share_count = stats.get("shareCount", 0)
        comment_count = stats.get("commentCount", 0)

        hashtags = re.findall(r"#(\w+)", desc)
        for h in hashtags:
            h = h.lower()
            hashtag_counts[h] = hashtag_counts.get(h, 0) + max(play_count, 1)

        # Also check challenges/hashtag objects
        for challenge in item.get("challenges", []):
            h = challenge.get("title", "").lower()
            if h:
                views = challenge.get("stats", {}).get("viewCount", 0)
                hashtag_counts[h] = hashtag_counts.get(h, 0) + max(views, play_count)

        # Collect music
        music_id = music.get("id", "")
        if music_id and music_id not in music_tracks:
            music_tracks[music_id] = {
                "id": music_id,
                "title": music.get("title", ""),
                "artist": music.get("authorName", ""),
                "duration": music.get("duration", 0),
                "is_original": music.get("original", False),
                "use_count": 0,
                "platform": "tiktok",
            }
        if music_id in music_tracks:
            music_tracks[music_id]["use_count"] += 1

        video_id = item.get("id", "")
        videos.append({
            "id": video_id,
            "description": desc[:200],
            "author": author.get("uniqueId", ""),
            "author_name": author.get("nickname", ""),
            "play_count": play_count,
            "like_count": like_count,
            "share_count": share_count,
            "comment_count": comment_count,
            "hashtags": hashtags,
            "music_title": music.get("title", ""),
            "music_artist": music.get("authorName", ""),
            "duration": video.get("duration", 0),
            "url": f"https://www.tiktok.com/@{author.get('uniqueId', '')}/video/{video_id}",
            "cover": video.get("cover", ""),
        })

    sorted_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)
    sorted_music = sorted(music_tracks.values(), key=lambda x: x["use_count"], reverse=True)

    return {
        "videos": videos,
        "hashtags": [{"tag": f"#{h}", "score": s} for h, s in sorted_hashtags[:30]],
        "music": sorted_music[:20],
        "source": "tiktok_api",
        "total_fetched": len(videos),
    }


def _fetch_discover_fallback(region: str, max_results: int) -> dict:
    """Fallback: scrape TikTok discover/trending hashtags page."""
    url = "https://www.tiktok.com/api/discover/challenge/"
    params = {
        "aid": "1988",
        "count": "30",
        "cursor": "0",
        "language": "en",
        "region": region,
    }

    hashtags = []
    try:
        resp = requests.get(url, params=params, headers=_HEADERS, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get("challengeInfoList", [])[:30]:
                info = item.get("challengeInfo", {})
                stats = item.get("stats", {})
                title = info.get("challenge", {}).get("title", "")
                if title:
                    hashtags.append({
                        "tag": f"#{title}",
                        "score": stats.get("viewCount", 0),
                    })
    except Exception:
        pass

    if not hashtags:
        # Static fallback with evergreen TikTok hashtags
        hashtags = _evergreen_tiktok_hashtags()

    return {
        "videos": [],
        "hashtags": hashtags[:30],
        "music": _evergreen_tiktok_music(),
        "source": "tiktok_discover_fallback",
        "total_fetched": 0,
        "note": "Live scraping unavailable; showing evergreen/cached trending data",
    }


def _evergreen_tiktok_hashtags() -> list[dict]:
    """Known high-performing evergreen TikTok hashtags by niche."""
    return [
        {"tag": "#fyp", "score": 50_000_000_000},
        {"tag": "#foryou", "score": 45_000_000_000},
        {"tag": "#foryoupage", "score": 40_000_000_000},
        {"tag": "#viral", "score": 20_000_000_000},
        {"tag": "#trending", "score": 15_000_000_000},
        {"tag": "#tiktok", "score": 12_000_000_000},
        {"tag": "#xyzbca", "score": 10_000_000_000},
        {"tag": "#blowthisup", "score": 8_000_000_000},
        {"tag": "#duet", "score": 7_000_000_000},
        {"tag": "#stitch", "score": 6_500_000_000},
        {"tag": "#comedy", "score": 6_000_000_000},
        {"tag": "#funny", "score": 5_800_000_000},
        {"tag": "#dance", "score": 5_500_000_000},
        {"tag": "#food", "score": 5_000_000_000},
        {"tag": "#fitness", "score": 4_500_000_000},
        {"tag": "#motivation", "score": 4_000_000_000},
        {"tag": "#lifestyle", "score": 3_800_000_000},
        {"tag": "#fashion", "score": 3_500_000_000},
        {"tag": "#beauty", "score": 3_200_000_000},
        {"tag": "#travel", "score": 3_000_000_000},
    ]


def _evergreen_tiktok_music() -> list[dict]:
    """Commonly used TikTok sounds/music for content."""
    return [
        {"title": "original sound", "artist": "creator", "use_count": 0, "is_original": True, "platform": "tiktok"},
        {"title": "Monkeys Spinning Monkeys", "artist": "Kevin MacLeod", "use_count": 0, "platform": "tiktok"},
        {"title": "Oh No", "artist": "Kreepa", "use_count": 0, "platform": "tiktok"},
        {"title": "Savage Love", "artist": "Jawsh 685 & Jason Derulo", "use_count": 0, "platform": "tiktok"},
        {"title": "Stay", "artist": "The Kid LAROI & Justin Bieber", "use_count": 0, "platform": "tiktok"},
    ]


def fetch_tiktok_hashtags(region: str = "US", top_n: int = 30) -> list[dict]:
    """Return top trending TikTok hashtags."""
    result = fetch_trending_tiktok(region=region)
    return result.get("hashtags", [])[:top_n]


def fetch_tiktok_music(region: str = "US", max_results: int = 20) -> list[dict]:
    """Return trending TikTok sounds/music."""
    result = fetch_trending_tiktok(region=region)
    return result.get("music", [])[:max_results]
