"""TikTok trend scraper — uses TikTok's open discovery endpoints.

No API key required. Accesses publicly available trending data.
"""

import json
import re
import time
from typing import Optional

try:
    import requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

from . import cache as _cache

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.0 Mobile/15E148 Safari/604.1"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
    "Origin": "https://www.tiktok.com",
}

_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
}


def _fetch_discover_page() -> str:
    """Fetch TikTok's discover/explore page HTML."""
    if not _REQUESTS_OK:
        raise RuntimeError("requests required: pip install requests")
    try:
        resp = requests.get(
            "https://www.tiktok.com/explore",
            headers=_BROWSER_HEADERS,
            timeout=15,
        )
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        raise RuntimeError(f"Failed to fetch TikTok discover page: {e}") from e


def _extract_sigi_state(html: str) -> Optional[dict]:
    """Extract __NEXT_DATA__ or SIGI_STATE JSON from TikTok page."""
    # Try __NEXT_DATA__ first
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    # Try SIGI_STATE
    m = re.search(r'<script id="SIGI_STATE" type="application/json">(.+?)</script>', html, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    return None


def _parse_hashtag_challenge(challenge: dict) -> dict:
    return {
        "platform": "tiktok",
        "tag": "#" + challenge.get("title", challenge.get("challengeName", "")),
        "view_count": challenge.get("stats", {}).get("viewCount", 0),
        "video_count": challenge.get("stats", {}).get("videoCount", 0),
        "description": (challenge.get("desc", "") or "")[:200],
        "is_trending": True,
    }


def _walk_for_challenges(obj, results: list, limit: int) -> None:
    """Recursively find challengeInfo / hashtagChallenge nodes."""
    if len(results) >= limit:
        return
    if isinstance(obj, dict):
        if "challengeInfo" in obj or "challengeName" in obj:
            parsed = _parse_hashtag_challenge(obj)
            if parsed["tag"] != "#":
                results.append(parsed)
                return
        if "title" in obj and "stats" in obj and "videoCount" in obj.get("stats", {}):
            parsed = _parse_hashtag_challenge(obj)
            if parsed["tag"] != "#":
                results.append(parsed)
                return
        for v in obj.values():
            _walk_for_challenges(v, results, limit)
            if len(results) >= limit:
                return
    elif isinstance(obj, list):
        for item in obj:
            _walk_for_challenges(item, results, limit)
            if len(results) >= limit:
                return


def get_trending_hashtags(limit: int = 30, use_cache: bool = True) -> dict:
    """Fetch trending TikTok hashtags from the explore/discover page.

    Falls back to fetching from the TikTok API challenge endpoint.
    """
    cache_key = "tiktok_trending_hashtags"
    if use_cache:
        cached = _cache.get(cache_key, ttl=1800)  # 30 min TTL for fast-moving TikTok
        if cached:
            cached["from_cache"] = True
            return cached

    challenges = []

    # Strategy 1: parse embedded JSON from discover page
    try:
        html = _fetch_discover_page()
        state = _extract_sigi_state(html)
        if state:
            _walk_for_challenges(state, challenges, limit)
    except Exception:
        pass

    # Strategy 2: TikTok's challenge list API (no auth required for public data)
    if not challenges:
        try:
            api_resp = requests.get(
                "https://www.tiktok.com/api/challenge/item_list/",
                params={"challengeID": "", "count": limit, "cursor": 0},
                headers=_HEADERS,
                timeout=10,
            )
            if api_resp.status_code == 200:
                data = api_resp.json()
                for item in data.get("challengeList", [])[:limit]:
                    challenges.append(_parse_hashtag_challenge(item))
        except Exception:
            pass

    # Strategy 3: scrape trending hashtags from TikTok's public pages via regex
    if not challenges:
        try:
            html = _fetch_discover_page()
            raw_tags = re.findall(r'"title"\s*:\s*"([^"]{2,50})"', html)
            seen = set()
            for tag in raw_tags:
                clean = tag.strip().lstrip("#")
                if clean and clean not in seen and re.match(r"^[\w一-鿿]+$", clean):
                    seen.add(clean)
                    challenges.append({
                        "platform": "tiktok",
                        "tag": "#" + clean,
                        "view_count": 0,
                        "video_count": 0,
                        "description": "",
                        "is_trending": True,
                    })
                    if len(challenges) >= limit:
                        break
        except Exception:
            pass

    result = {
        "platform": "tiktok",
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "count": len(challenges),
        "hashtags": challenges[:limit],
        "from_cache": False,
    }
    _cache.set(cache_key, result)
    return result


def get_trending_sounds(limit: int = 20, use_cache: bool = True) -> dict:
    """Fetch trending TikTok sounds/music."""
    cache_key = "tiktok_trending_sounds"
    if use_cache:
        cached = _cache.get(cache_key, ttl=3600)
        if cached:
            cached["from_cache"] = True
            return cached

    sounds = []

    try:
        # TikTok music/sound trending endpoint (publicly accessible)
        resp = requests.get(
            "https://www.tiktok.com/api/recommend/item_list/",
            params={"count": 20, "id": 1, "type": 5, "secUid": "", "maxCursor": 0,
                    "minCursor": 0, "sourceType": 12, "appId": 1233},
            headers=_HEADERS,
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get("itemList", [])[:limit]:
                music = item.get("music", {})
                if music:
                    sounds.append({
                        "platform": "tiktok",
                        "sound_id": music.get("id", ""),
                        "title": music.get("title", ""),
                        "artist": music.get("authorName", ""),
                        "duration": music.get("duration", 0),
                        "is_original": music.get("original", False),
                        "cover_url": music.get("coverLarge", "") or music.get("coverMedium", ""),
                        "use_count": item.get("stats", {}).get("playCount", 0),
                    })
    except Exception:
        pass

    # Fallback: parse from the main page
    if not sounds:
        try:
            html = _fetch_discover_page()
            state = _extract_sigi_state(html)
            if state:
                _walk_for_sounds(state, sounds, limit)
        except Exception:
            pass

    result = {
        "platform": "tiktok",
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "count": len(sounds),
        "sounds": sounds[:limit],
        "from_cache": False,
    }
    _cache.set(cache_key, result)
    return result


def _walk_for_sounds(obj, results: list, limit: int) -> None:
    if len(results) >= limit:
        return
    if isinstance(obj, dict):
        if "music" in obj and isinstance(obj["music"], dict) and "title" in obj["music"]:
            m = obj["music"]
            results.append({
                "platform": "tiktok",
                "sound_id": str(m.get("id", "")),
                "title": m.get("title", ""),
                "artist": m.get("authorName", ""),
                "duration": m.get("duration", 0),
                "is_original": m.get("original", False),
                "cover_url": m.get("coverLarge", "") or m.get("coverMedium", ""),
                "use_count": 0,
            })
            return
        for v in obj.values():
            _walk_for_sounds(v, results, limit)
            if len(results) >= limit:
                return
    elif isinstance(obj, list):
        for item in obj:
            _walk_for_sounds(item, results, limit)
            if len(results) >= limit:
                return


def get_trending_videos(limit: int = 20, use_cache: bool = True) -> dict:
    """Fetch trending TikTok videos from the For You page recommendation."""
    cache_key = "tiktok_trending_videos"
    if use_cache:
        cached = _cache.get(cache_key, ttl=1800)
        if cached:
            cached["from_cache"] = True
            return cached

    videos = []
    try:
        resp = requests.get(
            "https://www.tiktok.com/api/recommend/item_list/",
            params={"count": limit, "id": 1, "type": 5, "secUid": "",
                    "maxCursor": 0, "minCursor": 0, "sourceType": 12, "appId": 1233},
            headers=_HEADERS,
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get("itemList", [])[:limit]:
                desc = item.get("desc", "")
                hashtags = [t.lower() for t in re.findall(r"#(\w+)", desc)]
                stats = item.get("stats", {})
                author = item.get("author", {})
                music = item.get("music", {})
                videos.append({
                    "platform": "tiktok",
                    "id": item.get("id", ""),
                    "description": desc[:300],
                    "author": author.get("nickname", author.get("uniqueId", "")),
                    "author_followers": author.get("followerCount", 0),
                    "play_count": stats.get("playCount", 0),
                    "like_count": stats.get("diggCount", 0),
                    "comment_count": stats.get("commentCount", 0),
                    "share_count": stats.get("shareCount", 0),
                    "hashtags": hashtags,
                    "sound_title": music.get("title", ""),
                    "sound_artist": music.get("authorName", ""),
                    "duration": item.get("video", {}).get("duration", 0),
                })
    except Exception as e:
        raise RuntimeError(f"Failed to fetch TikTok trending videos: {e}") from e

    result = {
        "platform": "tiktok",
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "count": len(videos),
        "videos": videos[:limit],
        "from_cache": False,
    }
    _cache.set(cache_key, result)
    return result
