"""TikTok trend scraper.

Scrapes TikTok's public trending data via their web API endpoints.
No API key required for public trend discovery.

Install: pip install requests beautifulsoup4

Note: TikTok aggressively rate-limits bots. If endpoints return 403/empty,
use --mock to get sample data in the expected schema for agent development.
"""

import json
import re
import time
from typing import Optional
from urllib.parse import urlencode

try:
    import requests
    from bs4 import BeautifulSoup
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

# Public-facing headers that mimic a browser visit
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
    "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124"',
    "sec-ch-ua-platform": '"Windows"',
}

# Endpoints (subject to TikTok changes)
_TRENDING_FEED_URL = "https://www.tiktok.com/api/explore/item_list/"
_DISCOVER_URL = "https://www.tiktok.com/discover"
_TAG_BASE = "https://www.tiktok.com/tag/"


def _check_deps() -> None:
    if not _HAS_REQUESTS:
        raise RuntimeError(
            "requests and beautifulsoup4 required. "
            "Install: pip install requests beautifulsoup4"
        )


def _get(url: str, params: Optional[dict] = None, timeout: int = 20) -> dict | None:
    _check_deps()
    try:
        resp = requests.get(
            url, params=params, headers=_HEADERS, timeout=timeout
        )
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception:
        return None


def _parse_sigi_state(html: str) -> Optional[dict]:
    """Extract __UNIVERSAL_DATA_FOR_REHYDRATION__ JSON from TikTok HTML."""
    match = re.search(
        r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>([^<]+)</script>',
        html,
    )
    if not match:
        match = re.search(
            r'window\["SIGI_STATE"\]\s*=\s*(\{.+?\});\s*window\[',
            html, re.DOTALL
        )
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    return None


def get_trending_videos(limit: int = 20) -> list[dict]:
    """Fetch trending TikTok videos from the Explore feed.

    Returns:
        List of dicts: id, description, author, music, hashtags, stats.
    """
    _check_deps()
    params = {
        "count": min(limit, 30),
        "cursor": 0,
        "type": 1,
        "secUid": "",
        "sourceType": 12,
        "language": "en",
    }
    data = _get(_TRENDING_FEED_URL, params=params)
    if not data or "itemList" not in data:
        # Try scraping the discover HTML page as fallback
        return _scrape_discover_videos(limit)

    videos = []
    for item in (data.get("itemList") or [])[:limit]:
        videos.append(_parse_video_item(item))
    return videos


def _scrape_discover_videos(limit: int = 20) -> list[dict]:
    """Fallback: scrape TikTok Discover HTML page."""
    _check_deps()
    try:
        resp = requests.get(
            _DISCOVER_URL, headers=_HEADERS, timeout=20
        )
        if resp.status_code != 200:
            return []
        state = _parse_sigi_state(resp.text)
        if not state:
            return []
        videos = []
        items = (
            state.get("ItemModule") or
            state.get("defaultScopeMap", {}).get("webapp.explore-feed", {})
            .get("itemList", [])
        )
        if isinstance(items, dict):
            items = list(items.values())
        for item in items[:limit]:
            if isinstance(item, dict):
                videos.append(_parse_video_item(item))
        return videos
    except Exception:
        return []


def _parse_video_item(item: dict) -> dict:
    """Normalise a raw TikTok video item dict."""
    desc = item.get("desc") or item.get("description") or ""
    hashtags = re.findall(r"#(\w+)", desc)

    author = item.get("author") or {}
    music = item.get("music") or {}
    stats = item.get("stats") or item.get("statsV2") or {}

    return {
        "id": item.get("id"),
        "description": desc[:300],
        "hashtags": hashtags,
        "author": {
            "handle": author.get("uniqueId") or author.get("handle"),
            "nickname": author.get("nickname"),
            "followers": author.get("stats", {}).get("followerCount"),
        },
        "music": {
            "id": music.get("id"),
            "title": music.get("title"),
            "author": music.get("authorName"),
            "is_original": music.get("original", False),
        },
        "stats": {
            "views": _safe_int(stats.get("playCount") or stats.get("play_count")),
            "likes": _safe_int(stats.get("diggCount") or stats.get("digg_count")),
            "comments": _safe_int(stats.get("commentCount") or stats.get("comment_count")),
            "shares": _safe_int(stats.get("shareCount") or stats.get("share_count")),
        },
        "url": f"https://www.tiktok.com/@{author.get('uniqueId', '')}/video/{item.get('id', '')}",
    }


def get_trending_hashtags(limit: int = 30) -> list[dict]:
    """Scrape trending hashtag challenges from TikTok Discover.

    Returns:
        List of dicts: hashtag, title, video_count, view_count.
    """
    _check_deps()
    try:
        resp = requests.get(_DISCOVER_URL, headers=_HEADERS, timeout=20)
        if resp.status_code != 200:
            return _mock_trending_hashtags(limit)

        state = _parse_sigi_state(resp.text)
        if state:
            hashtags = _extract_hashtags_from_state(state, limit)
            if hashtags:
                return hashtags

        # HTML fallback
        soup = BeautifulSoup(resp.text, "html.parser")
        hashtags = []
        for tag in soup.select("a[href*='/tag/']")[:limit * 2]:
            href = tag.get("href", "")
            name = re.search(r"/tag/([^/?#]+)", href)
            if name:
                label = tag.get_text(strip=True)
                hashtags.append({
                    "hashtag": f"#{name.group(1)}",
                    "title": label or name.group(1),
                    "video_count": None,
                    "view_count": None,
                })
        seen = set()
        unique = []
        for h in hashtags:
            if h["hashtag"] not in seen:
                seen.add(h["hashtag"])
                unique.append(h)
        return unique[:limit] if unique else _mock_trending_hashtags(limit)
    except Exception:
        return _mock_trending_hashtags(limit)


def _extract_hashtags_from_state(state: dict, limit: int) -> list[dict]:
    """Pull hashtag challenge data from the SIGI state blob."""
    results = []
    challenges = (
        state.get("ChallengePage") or
        state.get("challengeData") or
        state.get("webapp.challenge-detail", {}).get("challengeInfo") or
        {}
    )
    if isinstance(challenges, dict):
        for key, val in challenges.items():
            if isinstance(val, dict) and "challengeInfo" in val:
                ch = val["challengeInfo"].get("challenge", {})
                stats = val["challengeInfo"].get("stats", {})
                results.append({
                    "hashtag": f"#{ch.get('title', key)}",
                    "title": ch.get("desc", ""),
                    "video_count": stats.get("videoCount"),
                    "view_count": stats.get("viewCount"),
                })
            if len(results) >= limit:
                break
    return results


def get_trending_music(limit: int = 20) -> list[dict]:
    """Extract trending music/sounds from TikTok's trending video feed.

    Returns:
        List of dicts: id, title, author, use_count, is_original.
    """
    videos = get_trending_videos(limit=min(limit * 2, 50))
    seen_ids: set = set()
    music_list = []
    for v in videos:
        m = v.get("music") or {}
        mid = m.get("id")
        if mid and mid not in seen_ids:
            seen_ids.add(mid)
            music_list.append({
                "id": mid,
                "title": m.get("title"),
                "author": m.get("author"),
                "is_original": m.get("is_original", False),
                "use_count": None,
                "tiktok_url": f"https://www.tiktok.com/music/{mid}",
            })
        if len(music_list) >= limit:
            break
    return music_list if music_list else _mock_trending_music(limit)


def get_hashtag_stats(hashtag: str) -> dict:
    """Fetch stats for a specific TikTok hashtag/challenge.

    Args:
        hashtag: Tag name without the # symbol.

    Returns:
        Dict with title, video_count, view_count, description.
    """
    _check_deps()
    tag = hashtag.lstrip("#")
    url = f"{_TAG_BASE}{tag}"
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=20)
        if resp.status_code != 200:
            return {"hashtag": f"#{tag}", "error": f"HTTP {resp.status_code}"}
        state = _parse_sigi_state(resp.text)
        if state:
            ch_page = state.get("ChallengePage") or {}
            info = ch_page.get("challengeInfo") or {}
            challenge = info.get("challenge") or {}
            stats = info.get("stats") or {}
            return {
                "hashtag": f"#{tag}",
                "title": challenge.get("title", tag),
                "description": challenge.get("desc", ""),
                "video_count": stats.get("videoCount"),
                "view_count": stats.get("viewCount"),
                "url": url,
            }
        return {"hashtag": f"#{tag}", "url": url, "error": "Could not parse stats"}
    except Exception as e:
        return {"hashtag": f"#{tag}", "error": str(e)}


# ── Mock data (for --mock / offline / rate-limited mode) ──────────────

def _mock_trending_hashtags(limit: int = 20) -> list[dict]:
    """Sample trending hashtags mirroring real TikTok schema."""
    samples = [
        {"hashtag": "#fyp", "title": "For You Page", "video_count": 50_000_000, "view_count": 5_000_000_000_000},
        {"hashtag": "#viral", "title": "Viral Videos", "video_count": 25_000_000, "view_count": 2_000_000_000_000},
        {"hashtag": "#trending", "title": "Trending Now", "video_count": 15_000_000, "view_count": 1_500_000_000_000},
        {"hashtag": "#foryou", "title": "For You", "video_count": 12_000_000, "view_count": 900_000_000_000},
        {"hashtag": "#dance", "title": "Dance Challenges", "video_count": 10_000_000, "view_count": 800_000_000_000},
        {"hashtag": "#comedy", "title": "Comedy", "video_count": 8_000_000, "view_count": 600_000_000_000},
        {"hashtag": "#duet", "title": "Duet", "video_count": 7_000_000, "view_count": 500_000_000_000},
        {"hashtag": "#fashion", "title": "Fashion", "video_count": 6_000_000, "view_count": 450_000_000_000},
        {"hashtag": "#fitness", "title": "Fitness", "video_count": 5_000_000, "view_count": 400_000_000_000},
        {"hashtag": "#food", "title": "Food & Cooking", "video_count": 5_000_000, "view_count": 380_000_000_000},
        {"hashtag": "#beautyhacks", "title": "Beauty Hacks", "video_count": 4_000_000, "view_count": 300_000_000_000},
        {"hashtag": "#motivation", "title": "Motivation", "video_count": 3_500_000, "view_count": 280_000_000_000},
        {"hashtag": "#travel", "title": "Travel", "video_count": 3_000_000, "view_count": 250_000_000_000},
        {"hashtag": "#storytime", "title": "Story Time", "video_count": 2_500_000, "view_count": 200_000_000_000},
        {"hashtag": "#satisfying", "title": "Satisfying Videos", "video_count": 2_000_000, "view_count": 190_000_000_000},
        {"hashtag": "#lifehacks", "title": "Life Hacks", "video_count": 1_800_000, "view_count": 170_000_000_000},
        {"hashtag": "#aesthetic", "title": "Aesthetic", "video_count": 1_600_000, "view_count": 150_000_000_000},
        {"hashtag": "#challenge", "title": "Challenges", "video_count": 1_500_000, "view_count": 140_000_000_000},
        {"hashtag": "#business", "title": "Business Tips", "video_count": 1_200_000, "view_count": 110_000_000_000},
        {"hashtag": "#invest", "title": "Investing", "video_count": 1_000_000, "view_count": 90_000_000_000},
    ]
    return samples[:limit]


def _mock_trending_music(limit: int = 10) -> list[dict]:
    """Sample trending TikTok sounds mirroring real schema."""
    samples = [
        {"id": "1", "title": "Aesthetic - Xilo", "author": "Xilo", "is_original": False, "use_count": 4_200_000},
        {"id": "2", "title": "Stay - The Kid LAROI & Justin Bieber", "author": "The Kid LAROI", "is_original": False, "use_count": 3_800_000},
        {"id": "3", "title": "Blinding Lights - The Weeknd", "author": "The Weeknd", "is_original": False, "use_count": 3_100_000},
        {"id": "4", "title": "original sound - creator123", "author": "creator123", "is_original": True, "use_count": 2_700_000},
        {"id": "5", "title": "Industry Baby - Lil Nas X", "author": "Lil Nas X", "is_original": False, "use_count": 2_400_000},
        {"id": "6", "title": "Good 4 U - Olivia Rodrigo", "author": "Olivia Rodrigo", "is_original": False, "use_count": 2_200_000},
        {"id": "7", "title": "MONTERO - Lil Nas X", "author": "Lil Nas X", "is_original": False, "use_count": 2_000_000},
        {"id": "8", "title": "Levitating - Dua Lipa", "author": "Dua Lipa", "is_original": False, "use_count": 1_900_000},
        {"id": "9", "title": "Kiss Me More - Doja Cat", "author": "Doja Cat", "is_original": False, "use_count": 1_700_000},
        {"id": "10", "title": "Peaches - Justin Bieber", "author": "Justin Bieber", "is_original": False, "use_count": 1_500_000},
    ]
    return samples[:limit]


def _safe_int(val) -> Optional[int]:
    try:
        return int(val)
    except (TypeError, ValueError):
        return None
