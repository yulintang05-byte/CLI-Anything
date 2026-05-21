"""TikTok viral trend scraper — hashtags, sounds, and trending videos."""

import json
import re
import time
import requests
from typing import Optional
from urllib.parse import quote

HEADERS_BASE = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.0 Mobile/15E148 Safari/604.1"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
}

# TikTok public discovery endpoint (no auth needed for basic trend data)
TRENDING_URL = "https://www.tiktok.com/node/share/discover"
HASHTAG_URL = "https://www.tiktok.com/api/discover/itemlist/"
SEARCH_URL = "https://www.tiktok.com/api/search/general/full/"

# TrendTok-style data from public TikTok endpoints
TIKTOK_TRENDING_API = "https://www.tiktok.com/api/discover/itemlist/"


def fetch_trending_hashtags(
    session_id: Optional[str] = None,
    region: str = "US",
    top_n: int = 30,
) -> list[dict]:
    """Fetch trending TikTok hashtags via discover API."""
    cookies = {}
    if session_id:
        cookies["sessionid"] = session_id

    url = "https://www.tiktok.com/api/discover/challenge/"
    params = {
        "discoverType": 0,
        "needItemList": False,
        "keyWord": "",
        "offset": 0,
        "count": top_n,
        "useRecommend": False,
        "language": "en",
        "appId": 1180,
        "region": region,
    }

    try:
        resp = requests.get(url, params=params, headers=HEADERS_BASE, cookies=cookies, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        challenges = data.get("challengeInfoList", [])
        return [_parse_hashtag(c) for c in challenges[:top_n]]
    except (requests.RequestException, json.JSONDecodeError) as e:
        # Fallback: scrape trending page
        return _scrape_trending_hashtags_fallback(session_id, region, top_n)


def _scrape_trending_hashtags_fallback(
    session_id: Optional[str], region: str, top_n: int
) -> list[dict]:
    """Scrape TikTok trending page for hashtags."""
    cookies = {"tt_webid_v2": "1", "tiktok_webapp_theme": "light"}
    if session_id:
        cookies["sessionid"] = session_id

    try:
        resp = requests.get(
            "https://www.tiktok.com/trending",
            headers=HEADERS_BASE,
            cookies=cookies,
            timeout=20,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"TikTok trending fetch failed: {e}") from e

    hashtags = set()
    # Extract hashtags from page HTML
    patterns = [
        r'"hashtagName"\s*:\s*"([^"]+)"',
        r'"title"\s*:\s*"(#[^"]+)"',
        r'href="/tag/([^"?]+)"',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, resp.text)
        for m in matches:
            tag = m.strip().lstrip("#")
            if tag and len(tag) > 1:
                hashtags.add(tag)
        if len(hashtags) >= top_n:
            break

    return [{"hashtag": f"#{h}", "view_count": None, "source": "scrape"} for h in list(hashtags)[:top_n]]


def _parse_hashtag(challenge_info: dict) -> dict:
    challenge = challenge_info.get("challengeInfo", challenge_info)
    ch = challenge.get("challenge", challenge)
    stats = challenge.get("stats", {})
    return {
        "hashtag": f"#{ch.get('title', '')}",
        "view_count": stats.get("viewCount", 0),
        "video_count": stats.get("videoCount", 0),
        "description": ch.get("desc", ""),
        "source": "tiktok_api",
    }


def fetch_trending_sounds(
    session_id: Optional[str] = None,
    region: str = "US",
    top_n: int = 25,
) -> list[dict]:
    """Fetch trending TikTok sounds/music."""
    cookies = {}
    if session_id:
        cookies["sessionid"] = session_id

    url = "https://www.tiktok.com/api/discover/music/"
    params = {
        "discoverType": 0,
        "needItemList": False,
        "keyWord": "",
        "offset": 0,
        "count": top_n,
        "useRecommend": False,
        "language": "en",
        "appId": 1180,
        "region": region,
    }

    try:
        resp = requests.get(url, params=params, headers=HEADERS_BASE, cookies=cookies, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        music_list = data.get("musicList", [])
        return [_parse_sound(m) for m in music_list[:top_n]]
    except (requests.RequestException, json.JSONDecodeError) as e:
        raise RuntimeError(f"TikTok sounds fetch failed: {e}") from e


def _parse_sound(music_info: dict) -> dict:
    m = music_info.get("music", music_info)
    stats = music_info.get("stats", {})
    return {
        "id": m.get("id", ""),
        "title": m.get("title", ""),
        "author": m.get("authorName", ""),
        "duration": m.get("duration", 0),
        "play_url": m.get("playUrl", ""),
        "cover": m.get("coverThumb", ""),
        "use_count": stats.get("useCount", 0),
        "tiktok_url": f"https://www.tiktok.com/music/{quote(m.get('title',''))}-{m.get('id','')}",
        "source": "tiktok_api",
    }


def fetch_trending_videos(
    session_id: Optional[str] = None,
    region: str = "US",
    max_results: int = 20,
) -> list[dict]:
    """Fetch trending TikTok videos."""
    cookies = {}
    if session_id:
        cookies["sessionid"] = session_id

    url = "https://www.tiktok.com/api/recommend/itemlist/"
    params = {
        "count": max_results,
        "type": 5,
        "secUid": "",
        "maxCursor": 0,
        "minCursor": 0,
        "sourceType": 12,
        "appId": 1180,
        "region": region,
        "language": "en",
    }

    try:
        resp = requests.get(url, params=params, headers=HEADERS_BASE, cookies=cookies, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("itemList", [])
        return [_parse_video(v) for v in items[:max_results]]
    except (requests.RequestException, json.JSONDecodeError) as e:
        raise RuntimeError(f"TikTok videos fetch failed: {e}") from e


def _parse_video(item: dict) -> dict:
    author = item.get("author", {})
    stats = item.get("stats", {})
    music = item.get("music", {})
    desc = item.get("desc", "")

    # Extract hashtags from description
    hashtags = re.findall(r"#(\w+)", desc)

    return {
        "id": item.get("id", ""),
        "description": desc,
        "author": author.get("uniqueId", ""),
        "author_name": author.get("nickname", ""),
        "play_count": stats.get("playCount", 0),
        "like_count": stats.get("diggCount", 0),
        "share_count": stats.get("shareCount", 0),
        "comment_count": stats.get("commentCount", 0),
        "hashtags": hashtags,
        "music_title": music.get("title", ""),
        "music_author": music.get("authorName", ""),
        "music_id": music.get("id", ""),
        "url": f"https://www.tiktok.com/@{author.get('uniqueId', '')}/video/{item.get('id', '')}",
        "source": "tiktok_api",
    }


def search_hashtag_videos(
    hashtag: str,
    session_id: Optional[str] = None,
    max_results: int = 20,
) -> list[dict]:
    """Fetch top videos for a specific hashtag."""
    cookies = {}
    if session_id:
        cookies["sessionid"] = session_id

    clean_tag = hashtag.lstrip("#")
    url = "https://www.tiktok.com/api/challenge/itemlist/"
    params = {
        "challengeID": "",
        "count": max_results,
        "cursor": 0,
        "shareUid": "",
        "recStart": 0,
        "language": "en",
    }

    # First, resolve challenge ID
    challenge_url = "https://www.tiktok.com/api/challenge/detail/"
    ch_params = {"challengeName": clean_tag, "language": "en"}
    try:
        ch_resp = requests.get(
            challenge_url, params=ch_params, headers=HEADERS_BASE, cookies=cookies, timeout=10
        )
        ch_resp.raise_for_status()
        ch_data = ch_resp.json()
        challenge_id = (
            ch_data.get("challengeInfo", {})
            .get("challenge", {})
            .get("id", "")
        )
        if challenge_id:
            params["challengeID"] = challenge_id
            resp = requests.get(url, params=params, headers=HEADERS_BASE, cookies=cookies, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return [_parse_video(v) for v in data.get("itemList", [])[:max_results]]
    except (requests.RequestException, json.JSONDecodeError, KeyError):
        pass
    return []


def extract_niche_hashtags(videos: list[dict], top_n: int = 30) -> list[dict]:
    """Aggregate hashtag frequency from a list of videos."""
    from collections import Counter
    counts: Counter = Counter()
    for v in videos:
        for tag in v.get("hashtags", []):
            counts[f"#{tag.lower()}"] += 1
    return [{"hashtag": h, "frequency": c} for h, c in counts.most_common(top_n)]
