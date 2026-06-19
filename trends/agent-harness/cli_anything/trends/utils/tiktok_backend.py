"""TikTok backend — supports Research API (official) and cookie-based scraping fallback.

Authentication modes (in priority order):
  1. TikTok Research API key  (TIKTOK_RESEARCH_API_KEY env var or config)
  2. Browser session cookies  (tiktok_cookies in config)
  3. Public hashtag scraping  (no auth, limited data)
"""

from __future__ import annotations

import json
import re
import sys
import time
from typing import Optional

try:
    import requests
except ImportError:
    print("requests not found. Install with: pip3 install requests", file=sys.stderr)
    sys.exit(1)

TIKTOK_RESEARCH_API = "https://open.tiktokapis.com/v2"
TIKTOK_WEB_API = "https://www.tiktok.com/api"
TIKTOK_BASE = "https://www.tiktok.com"

_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

_MOBILE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/17.0 Mobile/15E148 Safari/604.1"
)


# ── Research API (official) ────────────────────────────────────────────────


def research_api_query_videos(
    access_token: str,
    keywords: list[str] = None,
    region_codes: list[str] = None,
    max_count: int = 20,
    start_date: str = None,
    end_date: str = None,
) -> list[dict]:
    """Query TikTok Research API for videos by keywords/region.

    Requires an approved TikTok Research API access token.
    Apply at: https://developers.tiktok.com/products/research-api/
    """
    from datetime import datetime, timedelta

    if not start_date:
        start_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y%m%d")
    if not end_date:
        end_date = datetime.utcnow().strftime("%Y%m%d")

    body = {
        "query": {
            "and": [],
        },
        "start_date": start_date,
        "end_date": end_date,
        "max_count": min(max_count, 100),
        "fields": "id,video_description,create_time,region_code,share_count,view_count,like_count,comment_count,music_id,hashtag_names",
    }

    if keywords:
        body["query"]["and"].append({
            "operation": "IN",
            "field_name": "keyword",
            "field_values": keywords,
        })
    if region_codes:
        body["query"]["and"].append({
            "operation": "IN",
            "field_name": "region_code",
            "field_values": region_codes,
        })

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    resp = requests.post(
        f"{TIKTOK_RESEARCH_API}/research/video/query/",
        json=body,
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    videos = []
    for item in data.get("data", {}).get("videos", []):
        videos.append({
            "id": str(item.get("id", "")),
            "description": item.get("video_description", ""),
            "views": item.get("view_count", 0),
            "likes": item.get("like_count", 0),
            "comments": item.get("comment_count", 0),
            "shares": item.get("share_count", 0),
            "hashtags": [f"#{h.lower()}" for h in item.get("hashtag_names", [])],
            "music_id": str(item.get("music_id", "")),
            "region": item.get("region_code", ""),
            "created_at": item.get("create_time", ""),
            "url": f"https://www.tiktok.com/video/{item.get('id', '')}",
            "platform": "tiktok",
            "source": "research_api",
        })

    return videos


def research_api_get_trending_hashtags(
    access_token: str,
    region: str = "US",
    max_count: int = 20,
) -> list[dict]:
    """Get trending hashtags via Research API."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    params = {
        "region_code": region,
        "max_count": min(max_count, 20),
        "fields": "hashtag_name,view_count,video_count,trend",
    }
    resp = requests.get(
        f"{TIKTOK_RESEARCH_API}/research/trend/keyword/",
        params=params,
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    hashtags = []
    for item in data.get("data", {}).get("hashtag_list", []):
        hashtags.append({
            "hashtag": f"#{item.get('hashtag_name', '').lower()}",
            "views": item.get("view_count", 0),
            "video_count": item.get("video_count", 0),
            "trend": item.get("trend", ""),
            "platform": "tiktok",
            "source": "research_api",
        })

    return sorted(hashtags, key=lambda x: x["views"], reverse=True)


# ── Cookie-based scraping (unofficial) ────────────────────────────────────


def cookie_get_trending_feed(cookies: dict, count: int = 20, region: str = "US") -> list[dict]:
    """Fetch TikTok trending feed using browser session cookies.

    To get cookies: open TikTok in browser → DevTools → Application →
    Cookies → copy sessionid, ttwid, tt_webid, and msToken values to config.
    """
    session = requests.Session()
    for k, v in cookies.items():
        session.cookies.set(k, v, domain=".tiktok.com")

    headers = {
        "User-Agent": _BROWSER_UA,
        "Referer": f"{TIKTOK_BASE}/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": TIKTOK_BASE,
    }

    params = {
        "count": count,
        "id": "1",
        "type": "5",
        "secUid": "",
        "maxCursor": "0",
        "minCursor": "0",
        "sourceType": "12",
        "appId": "1233",
        "region": region,
        "priority_region": region,
        "language": "en",
    }

    resp = session.get(
        f"{TIKTOK_WEB_API}/trending/feed/",
        headers=headers,
        params=params,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    videos = []
    for item in data.get("itemList", []):
        desc = item.get("desc", "")
        author = item.get("author", {})
        stats = item.get("stats", {})
        music = item.get("music", {})
        challenges = item.get("challenges", [])

        hashtags = [f"#{c.get('title', '').lower()}" for c in challenges if c.get("title")]
        hashtags += _extract_hashtags_from_desc(desc)
        hashtags = list(dict.fromkeys(hashtags))[:15]

        videos.append({
            "id": item.get("id", ""),
            "description": desc,
            "author": author.get("uniqueId", ""),
            "author_name": author.get("nickname", ""),
            "views": stats.get("playCount", 0),
            "likes": stats.get("diggCount", 0),
            "comments": stats.get("commentCount", 0),
            "shares": stats.get("shareCount", 0),
            "hashtags": hashtags,
            "music_title": music.get("title", ""),
            "music_author": music.get("authorName", ""),
            "music_id": str(music.get("id", "")),
            "url": f"https://www.tiktok.com/@{author.get('uniqueId', '')}/video/{item.get('id', '')}",
            "platform": "tiktok",
            "source": "cookie_scrape",
        })

    return videos


def cookie_get_trending_sounds(cookies: dict, count: int = 20) -> list[dict]:
    """Get trending sounds/music from TikTok discover page."""
    session = requests.Session()
    for k, v in cookies.items():
        session.cookies.set(k, v, domain=".tiktok.com")

    headers = {
        "User-Agent": _BROWSER_UA,
        "Referer": f"{TIKTOK_BASE}/",
        "Accept": "application/json, text/plain, */*",
    }

    params = {
        "discoverType": "3",  # sounds/music
        "needItemList": "false",
        "keyWord": "",
        "offset": "0",
        "count": count,
        "useRecommend": "false",
        "language": "en",
    }

    resp = session.get(
        f"{TIKTOK_WEB_API}/discover/item_list/",
        headers=headers,
        params=params,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    sounds = []
    for item in data.get("musicList", []):
        sounds.append({
            "id": str(item.get("id", "")),
            "title": item.get("title", ""),
            "artist": item.get("authorName", ""),
            "video_count": item.get("videoCount", 0),
            "cover_url": item.get("coverMedium", {}).get("urlList", [""])[0],
            "platform": "tiktok",
            "source": "cookie_scrape",
        })

    return sorted(sounds, key=lambda x: x["video_count"], reverse=True)


# ── Public scraping fallback (no auth) ───────────────────────────────────


def public_get_hashtag_info(hashtag: str) -> dict:
    """Fetch public hashtag stats from TikTok (no auth required)."""
    tag = hashtag.lstrip("#")
    headers = {
        "User-Agent": _MOBILE_UA,
        "Accept": "application/json, text/plain, */*",
    }
    params = {
        "challengeName": tag,
        "msToken": "",
    }
    resp = requests.get(
        f"{TIKTOK_WEB_API}/challenge/detail/",
        headers=headers,
        params=params,
        timeout=20,
    )
    if resp.status_code != 200:
        return {"hashtag": f"#{tag}", "error": f"HTTP {resp.status_code}"}

    try:
        data = resp.json()
        challenge = data.get("challengeInfo", {}).get("challenge", {})
        stats = data.get("challengeInfo", {}).get("stats", {})
        return {
            "hashtag": f"#{tag}",
            "title": challenge.get("title", tag),
            "video_count": stats.get("videoCount", 0),
            "view_count": stats.get("viewCount", 0),
            "platform": "tiktok",
            "source": "public",
        }
    except (json.JSONDecodeError, KeyError):
        return {"hashtag": f"#{tag}", "error": "parse error"}


def public_scrape_trending_page(region: str = "US") -> dict:
    """Scrape trending hashtags from TikTok's public trending page (JS JSON embedded).

    Returns partial data — full rendering requires JavaScript.
    """
    headers = {
        "User-Agent": _BROWSER_UA,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    resp = requests.get(f"{TIKTOK_BASE}/trending", headers=headers, timeout=20)
    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}", "hashtags": [], "videos": []}

    html = resp.text

    # Extract __UNIVERSAL_DATA_FOR_REHYDRATION__ JSON blob
    match = re.search(
        r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
        html,
        re.DOTALL,
    )
    if not match:
        return {"error": "no embedded data found", "hashtags": [], "videos": []}

    try:
        raw = json.loads(match.group(1))
        # Walk the nested structure to find trend lists
        trending_items = _walk_for_trending(raw)
        return {"hashtags": trending_items, "error": None}
    except (json.JSONDecodeError, KeyError, TypeError):
        return {"error": "failed to parse embedded JSON", "hashtags": [], "videos": []}


def _walk_for_trending(data, depth: int = 0) -> list[dict]:
    """Recursively search JSON tree for challenge/hashtag list items."""
    if depth > 8:
        return []
    results = []
    if isinstance(data, dict):
        # Look for challenge/hashtag data patterns
        if "challengeName" in data or "challenge" in data:
            name = data.get("challengeName") or data.get("challenge", {}).get("title", "")
            if name:
                results.append({
                    "hashtag": f"#{name.lower()}",
                    "video_count": data.get("videoCount", data.get("stats", {}).get("videoCount", 0)),
                    "source": "page_scrape",
                    "platform": "tiktok",
                })
        for v in data.values():
            results.extend(_walk_for_trending(v, depth + 1))
    elif isinstance(data, list):
        for item in data[:50]:
            results.extend(_walk_for_trending(item, depth + 1))
    return results


def _extract_hashtags_from_desc(desc: str) -> list[str]:
    found = re.findall(r"#([A-Za-z0-9_]+)", desc)
    return [f"#{h.lower()}" for h in found]


# ── Unified entry point ───────────────────────────────────────────────────


def get_trending(
    access_token: Optional[str] = None,
    cookies: Optional[dict] = None,
    region: str = "US",
    count: int = 20,
) -> dict:
    """Auto-select best available auth method and return trending data."""
    if access_token:
        try:
            videos = research_api_query_videos(
                access_token, region_codes=[region], max_count=count
            )
            hashtags = research_api_get_trending_hashtags(access_token, region=region)
            return {"videos": videos, "hashtags": hashtags, "source": "research_api"}
        except Exception as e:
            pass  # fall through

    if cookies:
        try:
            videos = cookie_get_trending_feed(cookies, count=count, region=region)
            sounds = cookie_get_trending_sounds(cookies, count=count)
            hashtags = _aggregate_hashtags_from_videos(videos)
            return {
                "videos": videos,
                "hashtags": hashtags,
                "sounds": sounds,
                "source": "cookie_scrape",
            }
        except Exception:
            pass

    # Public fallback
    result = public_scrape_trending_page(region=region)
    return {
        "videos": [],
        "hashtags": result.get("hashtags", []),
        "sounds": [],
        "source": "public_scrape",
        "note": "Limited data — add TikTok API key or cookies for full trending data.",
    }


def _aggregate_hashtags_from_videos(videos: list[dict]) -> list[dict]:
    """Aggregate hashtags from scraped videos."""
    from collections import defaultdict
    tag_data: dict[str, dict] = defaultdict(
        lambda: {"count": 0, "total_views": 0, "total_likes": 0}
    )
    for v in videos:
        for tag in v.get("hashtags", []):
            tag_data[tag]["count"] += 1
            tag_data[tag]["total_views"] += v.get("views", 0)
            tag_data[tag]["total_likes"] += v.get("likes", 0)

    results = []
    for tag, d in tag_data.items():
        score = d["count"] * 10 + d["total_views"] / 1_000_000
        results.append({
            "hashtag": tag,
            "video_count": d["count"],
            "total_views": d["total_views"],
            "total_likes": d["total_likes"],
            "score": round(score, 2),
            "platform": "tiktok",
        })
    return sorted(results, key=lambda x: x["score"], reverse=True)
