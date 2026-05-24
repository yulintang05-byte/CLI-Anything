"""TikTok trending scraper — fetches viral videos, hashtags, sounds, and creators."""

import re
import json
import time
import urllib.request
import urllib.parse
from typing import Optional
from datetime import datetime, timezone


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.0 Mobile/15E148 Safari/604.1"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
}

_MOBILE_HEADERS = {
    "User-Agent": (
        "TikTok 26.2.0 rv:262018 (iPhone; iOS 14.4.2; en_US) "
        "Cronet"
    ),
    "Accept": "*/*",
}

REGION_MAP = {
    "us": "US", "uk": "GB", "ca": "CA", "au": "AU",
    "in": "IN", "br": "BR", "de": "DE", "fr": "FR",
    "jp": "JP", "kr": "KR", "mx": "MX", "ng": "NG",
}


def _fetch(url: str, headers: dict, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as exc:
            if attempt == retries - 1:
                raise RuntimeError(f"Fetch failed [{url}]: {exc}") from exc
            time.sleep(1.5 * (attempt + 1))
    return ""


def _extract_sigi_state(html: str) -> Optional[dict]:
    """Extract SIGI_STATE / __NEXT_DATA__ JSON from TikTok HTML."""
    patterns = [
        r'<script id="SIGI_STATE"[^>]*>(\{.*?\})</script>',
        r'window\["SIGI_STATE"\]\s*=\s*(\{.*?\})',
        r'<script id="__NEXT_DATA__"[^>]*>(\{.*?\})</script>',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                continue
    return None


def _parse_item_list(items: list) -> list[dict]:
    """Parse TikTok item (video) objects into clean dicts."""
    results = []
    for item in items:
        if not isinstance(item, dict):
            continue
        try:
            vid_id = item.get("id", "")
            desc = item.get("desc", "")
            author = item.get("author", {})
            stats = item.get("stats", {})
            music = item.get("music", {})

            hashtags = re.findall(r"#\w+", desc)
            # Also check challengeInfoList
            for ch in item.get("challenges", []):
                tag = ch.get("title", "")
                if tag:
                    hashtags.append(f"#{tag}")
            hashtags = list(dict.fromkeys(hashtags))  # deduplicate, preserve order

            results.append({
                "video_id": vid_id,
                "url": f"https://www.tiktok.com/@{author.get('uniqueId','')}/video/{vid_id}",
                "description": desc,
                "author": {
                    "username": author.get("uniqueId", ""),
                    "nickname": author.get("nickname", ""),
                    "followers": author.get("stats", {}).get("followerCount", 0),
                },
                "stats": {
                    "plays": stats.get("playCount", 0),
                    "likes": stats.get("diggCount", 0),
                    "comments": stats.get("commentCount", 0),
                    "shares": stats.get("shareCount", 0),
                },
                "music": {
                    "id": music.get("id", ""),
                    "title": music.get("title", ""),
                    "author": music.get("authorName", ""),
                    "original": music.get("original", False),
                },
                "hashtags": hashtags,
                "duration": item.get("video", {}).get("duration", 0),
            })
        except Exception:
            continue
    return results


def fetch_trending(region: str = "us", limit: int = 30) -> dict:
    """Fetch TikTok trending videos via the discover/trend endpoint."""
    region_code = REGION_MAP.get(region.lower(), region.upper())
    # TikTok's public trending API endpoint
    url = (
        "https://www.tiktok.com/api/recommend/item_list/"
        f"?count={min(limit, 50)}&id=1&type=5&secUid=&maxCursor=0"
        f"&minCursor=0&sourceType=12&appId=1233&region={region_code}"
        f"&language=en&device_id=7000000000000000000"
    )
    try:
        raw = _fetch(url, _HEADERS)
        data = json.loads(raw)
        items = data.get("itemList", [])
    except Exception:
        # Fallback: scrape TikTok trending web page
        items = []
        try:
            html = _fetch("https://www.tiktok.com/trending", _HEADERS)
            state = _extract_sigi_state(html)
            if state:
                item_module = state.get("ItemModule", {})
                items = list(item_module.values()) if isinstance(item_module, dict) else []
        except Exception:
            pass

    videos = _parse_item_list(items[:limit])

    # Aggregate hashtags
    tag_counts: dict[str, int] = {}
    for v in videos:
        for tag in v["hashtags"]:
            tag_counts[tag.lower()] = tag_counts.get(tag.lower(), 0) + 1
    ranked_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

    # Aggregate music
    music_counts: dict[str, dict] = {}
    for v in videos:
        m = v["music"]
        mid = m.get("id", "")
        if mid and mid not in music_counts:
            music_counts[mid] = {**m, "video_count": 0}
        if mid:
            music_counts[mid]["video_count"] += 1
    trending_music = sorted(music_counts.values(), key=lambda x: x["video_count"], reverse=True)

    return {
        "platform": "tiktok",
        "region": region_code,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "videos": videos,
        "hashtags": [{"tag": t, "count": c} for t, c in ranked_tags],
        "trending_music": trending_music,
        "total": len(videos),
    }


def fetch_hashtag_trends(hashtag: str, limit: int = 20) -> dict:
    """Fetch top TikTok videos for a specific hashtag/challenge."""
    tag = hashtag.lstrip("#")
    url = (
        "https://www.tiktok.com/api/challenge/item_list/"
        f"?challengeName={urllib.parse.quote(tag)}&count={limit}"
        f"&cursor=0&device_id=7000000000000000000"
    )
    try:
        raw = _fetch(url, _HEADERS)
        data = json.loads(raw)
        items = data.get("itemList", [])
    except Exception:
        # Try the web hashtag page
        items = []
        try:
            html = _fetch(f"https://www.tiktok.com/tag/{urllib.parse.quote(tag)}", _HEADERS)
            state = _extract_sigi_state(html)
            if state:
                item_module = state.get("ItemModule", {})
                items = list(item_module.values()) if isinstance(item_module, dict) else []
        except Exception:
            pass

    videos = _parse_item_list(items[:limit])
    return {
        "platform": "tiktok",
        "hashtag": f"#{tag}",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "videos": videos,
        "total": len(videos),
    }


def fetch_trending_sounds(region: str = "us", limit: int = 20) -> dict:
    """Aggregate trending sounds/music from TikTok trending feed."""
    data = fetch_trending(region=region, limit=50)
    music = data.get("trending_music", [])[:limit]
    return {
        "platform": "tiktok",
        "region": REGION_MAP.get(region.lower(), region.upper()),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "trending_sounds": music,
        "total": len(music),
    }


def fetch_creator_trends(region: str = "us", limit: int = 20) -> dict:
    """Extract trending creators from TikTok trending feed."""
    data = fetch_trending(region=region, limit=50)
    creator_map: dict[str, dict] = {}
    for v in data.get("videos", []):
        a = v.get("author", {})
        uname = a.get("username", "")
        if uname and uname not in creator_map:
            creator_map[uname] = {**a, "viral_videos": 0, "total_plays": 0}
        if uname:
            creator_map[uname]["viral_videos"] += 1
            creator_map[uname]["total_plays"] += v.get("stats", {}).get("plays", 0)

    creators = sorted(creator_map.values(), key=lambda x: x["total_plays"], reverse=True)[:limit]
    return {
        "platform": "tiktok",
        "region": REGION_MAP.get(region.lower(), region.upper()),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "trending_creators": creators,
        "total": len(creators),
    }
