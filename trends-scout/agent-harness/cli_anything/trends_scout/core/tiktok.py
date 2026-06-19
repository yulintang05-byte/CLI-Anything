"""TikTok trend scraping — trending videos, hashtags, sounds/music.

Uses TikTok's public endpoints (no API key required for basic trending data).
For Research API access, set tiktok_client_key and tiktok_client_secret.
"""
import re
import json
import time
from collections import Counter
from typing import Optional

from cli_anything.trends_scout.utils import config as cfg_mod
from cli_anything.trends_scout.utils.http import get_json, get_html, make_session

_TT_BASE = "https://www.tiktok.com"
_TT_API = "https://www.tiktok.com/api"
_TT_RESEARCH_API = "https://open.tiktokapis.com/v2"


# ── Research API (optional, requires credentials) ───────────────────────────

def _get_research_token() -> Optional[str]:
    """Obtain a Research API token via client credentials flow."""
    client_key = cfg_mod.get("tiktok_client_key")
    client_secret = cfg_mod.get("tiktok_client_secret")
    if not client_key or not client_secret:
        return None
    import requests
    resp = requests.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        data={
            "client_key": client_key,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        },
        timeout=15,
    )
    if resp.ok:
        return resp.json().get("access_token")
    return None


def _research_api_trending(token: str, limit: int = 20) -> list[dict]:
    """Use Research API to query trending videos."""
    import requests
    payload = {
        "query": {
            "and": [{"operation": "EQ", "field_name": "region_code", "field_values": ["US"]}]
        },
        "max_count": limit,
        "cursor": 0,
        "start_date": _days_ago(7),
        "end_date": _today(),
        "sort_type": "0",
        "sort_field": "view_count",
    }
    resp = requests.post(
        f"{_TT_RESEARCH_API}/research/video/query/",
        json=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        timeout=20,
    )
    if not resp.ok:
        return []
    items = resp.json().get("data", {}).get("videos", [])
    return [_normalize_research(v) for v in items]


def _today() -> str:
    from datetime import date
    return date.today().strftime("%Y%m%d")


def _days_ago(n: int) -> str:
    from datetime import date, timedelta
    return (date.today() - timedelta(days=n)).strftime("%Y%m%d")


def _normalize_research(v: dict) -> dict:
    hashtags = [f"#{t}" for t in v.get("hashtag_names", [])]
    return {
        "id": str(v.get("id", "")),
        "desc": v.get("video_description", ""),
        "author": v.get("username", ""),
        "views": v.get("view_count", 0),
        "likes": v.get("like_count", 0),
        "shares": v.get("share_count", 0),
        "comments": v.get("comment_count", 0),
        "music_title": v.get("music_id", ""),
        "hashtags": hashtags,
        "url": f"https://www.tiktok.com/@{v.get('username', '')}",
    }


# ── Public endpoint scraping ─────────────────────────────────────────────────

def _public_trending(region: str = "US", limit: int = 30) -> list[dict]:
    """Scrape TikTok Discover/Trending page for viral content."""
    videos = []

    # Try the explore API endpoint (public, no auth)
    try:
        sess = make_session(mobile=True)
        sess.headers.update({
            "Referer": "https://www.tiktok.com/",
            "Origin": "https://www.tiktok.com",
        })
        resp = sess.get(
            f"{_TT_API}/explore/item_list/",
            params={
                "aid": "1988",
                "count": min(limit, 30),
                "insertedItemID": "",
                "region": region,
                "priority_region": region,
                "language": "en",
                "isNonPersonalized": "0",
                "from_page": "fyp",
                "itemList": "",
                "keyword": "",
            },
            timeout=15,
        )
        if resp.ok:
            data = resp.json()
            for item in data.get("itemList", [])[:limit]:
                videos.append(_normalize_public(item))
    except Exception:
        pass

    # Fallback: scrape Discover page HTML
    if not videos:
        videos = _scrape_discover_page(region)

    return videos[:limit]


def _normalize_public(item: dict) -> dict:
    desc = item.get("desc", "")
    author = item.get("author", {})
    music = item.get("music", {})
    stats = item.get("stats", {})
    hashtags = _extract_hashtags(desc)
    # Also extract from challengeInfoList
    challenges = item.get("challenges", []) or item.get("textExtra", [])
    for c in challenges:
        tag = c.get("hashtagName", "") or c.get("challengeName", "")
        if tag:
            hashtags.append(f"#{tag}")
    return {
        "id": item.get("id", ""),
        "desc": desc,
        "author": author.get("uniqueId", "") or author.get("nickname", ""),
        "views": stats.get("playCount", 0),
        "likes": stats.get("diggCount", 0),
        "shares": stats.get("shareCount", 0),
        "comments": stats.get("commentCount", 0),
        "music_title": music.get("title", ""),
        "music_author": music.get("authorName", ""),
        "music_id": music.get("id", ""),
        "hashtags": list(set(hashtags)),
        "url": f"https://www.tiktok.com/@{author.get('uniqueId', '')}/video/{item.get('id', '')}",
    }


def _scrape_discover_page(region: str = "US") -> list[dict]:
    """Fallback: parse TikTok trending/discover HTML for hashtag data."""
    videos = []
    try:
        html = get_html(f"{_TT_BASE}/trending", mobile=True)
        # Extract SIGI_STATE json from page
        match = re.search(r'<script\s+id="SIGI_STATE"[^>]*>(\{.*?\})</script>', html, re.DOTALL)
        if match:
            data = json.loads(match.group(1))
            item_module = data.get("ItemModule", {})
            for vid_id, item in item_module.items():
                videos.append(_normalize_public(item))
    except Exception:
        pass
    return videos


def _extract_hashtags(text: str) -> list[str]:
    return list(set(re.findall(r'#\w+', text)))


# ── Hashtag trending ─────────────────────────────────────────────────────────

def _get_hashtag_data(tag: str) -> dict:
    """Get stats for a specific TikTok hashtag."""
    tag = tag.lstrip("#")
    try:
        sess = make_session(mobile=False)
        resp = sess.get(
            f"{_TT_API}/challenge/item_list/",
            params={"aid": "1988", "challengeID": "", "challengeName": tag,
                    "count": "1", "cursor": "0"},
            timeout=10,
        )
        if resp.ok:
            data = resp.json()
            challenge = data.get("challengeInfo", {}).get("challenge", {})
            stats = data.get("challengeInfo", {}).get("stats", {})
            return {
                "hashtag": f"#{tag}",
                "views": stats.get("viewCount", 0),
                "videos": stats.get("videoCount", 0),
                "title": challenge.get("title", tag),
            }
    except Exception:
        pass
    return {"hashtag": f"#{tag}", "views": 0, "videos": 0}


# ── Public API ──────────────────────────────────────────────────────────────

def get_trending(region: str = "US", limit: int = 25) -> dict:
    """Get trending TikTok videos. Uses Research API if credentials set."""
    videos = []
    source = "scrape"

    token = _get_research_token()
    if token:
        videos = _research_api_trending(token, limit=limit)
        source = "research_api"

    if not videos:
        videos = _public_trending(region=region, limit=limit)
        source = "public"

    all_hashtags = []
    for v in videos:
        all_hashtags.extend(v.get("hashtags", []))

    top_hashtags = [tag for tag, _ in Counter(all_hashtags).most_common(20)]
    return {
        "platform": "tiktok",
        "region": region,
        "total": len(videos),
        "top_hashtags": top_hashtags,
        "videos": videos,
        "source": source,
    }


def get_hashtags(region: str = "US", limit: int = 30) -> dict:
    """Extract trending TikTok hashtags from viral content."""
    data = get_trending(region=region, limit=50)
    all_tags = []
    for v in data["videos"]:
        all_tags.extend(v.get("hashtags", []))

    counts = Counter(all_tags)
    hashtags = [
        {"hashtag": tag, "frequency": count}
        for tag, count in counts.most_common(limit)
        if tag and len(tag) > 1
    ]
    return {
        "platform": "tiktok",
        "region": region,
        "hashtags": hashtags,
    }


def get_trending_sounds(region: str = "US", limit: int = 20) -> dict:
    """Find trending sounds/music from viral TikTok videos."""
    data = get_trending(region=region, limit=50)
    music_counter: Counter = Counter()
    music_details: dict = {}

    for v in data["videos"]:
        music_title = v.get("music_title", "") or ""
        music_author = v.get("music_author", "") or ""
        music_id = v.get("music_id", "") or ""
        if music_title:
            key = f"{music_title} — {music_author}" if music_author else music_title
            music_counter[key] += 1
            if key not in music_details:
                music_details[key] = {
                    "title": music_title,
                    "author": music_author,
                    "id": music_id,
                }

    sounds = [
        {
            "rank": i + 1,
            "title": music_details[key]["title"],
            "artist": music_details[key]["author"],
            "sound_id": music_details[key]["id"],
            "video_count": count,
            "url": f"https://www.tiktok.com/music/{music_details[key]['id']}"
            if music_details[key]["id"] else "",
        }
        for i, (key, count) in enumerate(music_counter.most_common(limit))
    ]

    return {
        "platform": "tiktok",
        "region": region,
        "trending_sounds": sounds,
        "total": len(sounds),
    }


def lookup_hashtag(tag: str) -> dict:
    """Look up stats for a specific TikTok hashtag."""
    return _get_hashtag_data(tag)
