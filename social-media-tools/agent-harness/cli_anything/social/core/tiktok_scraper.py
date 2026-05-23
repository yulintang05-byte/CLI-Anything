"""TikTok trend scraper — uses public web endpoints and tiktok-scraper."""
import json
import re
import time
from typing import Dict, List, Optional, Any

import requests


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/16.0 Mobile/15E148 Safari/604.1"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
}

_TT_DISCOVER_URL = "https://www.tiktok.com/api/explore/item_list/"
_TT_TRENDING_URL = "https://www.tiktok.com/api/recommend/item_list/"
_TT_HASHTAG_URL = "https://www.tiktok.com/api/challenge/item_list/"
_TT_MUSIC_URL = "https://www.tiktok.com/api/music/item_list/"

# Public TikTok endpoints for trend data (no auth needed)
_TT_PUBLIC_TRENDING = (
    "https://www.tiktok.com/trending"
)


def _tt_session() -> requests.Session:
    sess = requests.Session()
    sess.headers.update(_HEADERS)
    # Seed basic TikTok cookies so requests look like a browser
    sess.cookies.set("tt_webid_v2", "1234567890123456789", domain=".tiktok.com")
    sess.cookies.set("tiktok_webapp_theme", "light", domain=".tiktok.com")
    return sess


def _parse_views(n: Any) -> int:
    if isinstance(n, int):
        return n
    if isinstance(n, float):
        return int(n)
    if isinstance(n, str):
        n = n.lower().replace(",", "")
        if "b" in n:
            return int(float(n.replace("b", "")) * 1_000_000_000)
        if "m" in n:
            return int(float(n.replace("m", "")) * 1_000_000)
        if "k" in n:
            return int(float(n.replace("k", "")) * 1_000)
        try:
            return int(n)
        except ValueError:
            return 0
    return 0


def scrape_trending_videos(
    region: str = "US",
    limit: int = 30,
    use_fallback: bool = True,
) -> List[Dict]:
    """
    Scrape TikTok trending videos.

    Returns list of video dicts with title, author, views, music, hashtags.
    Falls back to scrape + regex parse if API endpoints are blocked.
    """
    results = _try_tiktok_api(region, limit)
    if results:
        return results
    if use_fallback:
        return _scrape_tiktok_web(limit)
    return []


def _try_tiktok_api(region: str, limit: int) -> List[Dict]:
    """Attempt TikTok internal API endpoints."""
    sess = _tt_session()
    params = {
        "count": min(limit, 30),
        "id": 1,
        "sourceType": 12,
        "itemList": [],
        "region": region,
        "priority_region": region,
        "language": "en",
    }
    try:
        resp = sess.get(_TT_TRENDING_URL, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("itemList", [])
            if items:
                return _parse_tt_items(items)
    except (requests.RequestException, json.JSONDecodeError):
        pass
    return []


def _parse_tt_items(items: List[Dict]) -> List[Dict]:
    results = []
    for i, item in enumerate(items, 1):
        desc = item.get("desc", "")
        author = item.get("author", {})
        music = item.get("music", {})
        stats = item.get("stats", {})
        video = item.get("video", {})

        hashtags = re.findall(r"#(\w+)", desc)
        challenges = [c.get("title", "") for c in item.get("challenges", [])]
        all_ht = list(dict.fromkeys(
            [f"#{h}" for h in hashtags] + [f"#{c}" for c in challenges if c]
        ))

        results.append({
            "rank": i,
            "video_id": item.get("id", ""),
            "description": desc[:200],
            "author_handle": author.get("uniqueId", ""),
            "author_nickname": author.get("nickname", ""),
            "author_followers": author.get("stats", {}).get("followerCount", 0),
            "views": stats.get("playCount", 0),
            "likes": stats.get("diggCount", 0),
            "shares": stats.get("shareCount", 0),
            "comments": stats.get("commentCount", 0),
            "music_title": music.get("title", ""),
            "music_author": music.get("authorName", ""),
            "music_id": music.get("id", ""),
            "music_is_original": music.get("original", False),
            "hashtags": all_ht[:15],
            "duration_secs": video.get("duration", 0),
            "url": f"https://www.tiktok.com/@{author.get('uniqueId','')}/"
                   f"video/{item.get('id','')}",
            "platform": "tiktok",
            "source": "tiktok_api",
        })
    return results


def _scrape_tiktok_web(limit: int) -> List[Dict]:
    """Fallback: scrape TikTok web page for trend signals."""
    sess = _tt_session()
    results = []
    try:
        resp = sess.get("https://www.tiktok.com/trending", timeout=20)
        html = resp.text
    except requests.RequestException as e:
        return [{"error": f"TikTok web request failed: {e}"}]

    # Extract NEXT_DATA or sigi state
    sigi_match = re.search(r'id="SIGI_STATE"[^>]*>(\{.+?\})</script>', html, re.DOTALL)
    next_match = re.search(r'id="__NEXT_DATA__"[^>]*>(\{.+?\})</script>', html, re.DOTALL)
    raw_json = None
    for m in [sigi_match, next_match]:
        if m:
            try:
                raw_json = json.loads(m.group(1))
                break
            except json.JSONDecodeError:
                continue

    if raw_json:
        # Try to walk the JSON structure for item lists
        results = _walk_json_for_videos(raw_json, limit)

    if not results:
        # Last resort: extract video IDs from page HTML
        video_ids = list(dict.fromkeys(re.findall(r'"id":"(\d{15,20})"', html)))
        authors = re.findall(r'"uniqueId":"([^"]+)"', html)
        descs = re.findall(r'"desc":"([^"]{5,}?)"', html)
        for i, vid_id in enumerate(video_ids[:limit], 1):
            results.append({
                "rank": i,
                "video_id": vid_id,
                "description": descs[i - 1] if i - 1 < len(descs) else "",
                "author_handle": authors[i - 1] if i - 1 < len(authors) else "",
                "author_nickname": "",
                "views": 0,
                "likes": 0,
                "hashtags": [],
                "music_title": "",
                "url": f"https://www.tiktok.com/video/{vid_id}",
                "platform": "tiktok",
                "source": "html_scrape",
            })
    return results


def _walk_json_for_videos(data: Any, limit: int, depth: int = 0) -> List[Dict]:
    """Recursively search JSON for TikTok video item lists."""
    if depth > 6:
        return []
    if isinstance(data, list) and data and isinstance(data[0], dict):
        if "id" in data[0] and "desc" in data[0]:
            return _parse_tt_items(data[:limit])
    if isinstance(data, dict):
        for key in ("items", "itemList", "videoList", "list"):
            if key in data and isinstance(data[key], list):
                r = _walk_json_for_videos(data[key], limit, depth + 1)
                if r:
                    return r
        for v in data.values():
            r = _walk_json_for_videos(v, limit, depth + 1)
            if r:
                return r
    return []


def scrape_trending_hashtags(region: str = "US", limit: int = 50) -> List[Dict]:
    """Extract trending hashtags from TikTok discover + trending pages."""
    all_videos = scrape_trending_videos(region=region, limit=50)

    hashtag_counts: Dict[str, int] = {}
    hashtag_views: Dict[str, int] = {}
    hashtag_contexts: Dict[str, List[str]] = {}

    for video in all_videos:
        if "error" in video:
            continue
        for ht in video.get("hashtags", []):
            ht_l = ht.lower()
            hashtag_counts[ht_l] = hashtag_counts.get(ht_l, 0) + 1
            hashtag_views[ht_l] = hashtag_views.get(ht_l, 0) + video.get("views", 0)
            if ht_l not in hashtag_contexts:
                hashtag_contexts[ht_l] = []
            if len(hashtag_contexts[ht_l]) < 3:
                hashtag_contexts[ht_l].append(video.get("description", "")[:60])

    # Also try TikTok discover API
    discover = _scrape_tt_discover_hashtags(limit)
    for d in discover:
        ht_l = d.get("hashtag", "").lower()
        if ht_l not in hashtag_counts:
            hashtag_counts[ht_l] = 0
        hashtag_counts[ht_l] += d.get("video_count", 0) // 10000

    sorted_tags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)
    results = []
    for rank, (ht, count) in enumerate(sorted_tags[:limit], 1):
        results.append({
            "rank": rank,
            "hashtag": ht,
            "appearances": count,
            "total_views": hashtag_views.get(ht, 0),
            "seen_in": hashtag_contexts.get(ht, []),
            "platform": "tiktok",
        })
    return results


def _scrape_tt_discover_hashtags(limit: int) -> List[Dict]:
    """Scrape TikTok Discover page for trending hashtags."""
    sess = _tt_session()
    results = []
    try:
        resp = sess.get("https://www.tiktok.com/discover", timeout=15)
        html = resp.text
        # Find challenge/hashtag patterns in page
        tags_raw = re.findall(r'"challengeName":"([^"]+)"', html)
        view_counts = re.findall(r'"viewCount":(\d+)', html)
        video_counts = re.findall(r'"videoCount":(\d+)', html)
        for i, tag in enumerate(tags_raw[:limit]):
            results.append({
                "hashtag": f"#{tag}",
                "view_count": int(view_counts[i]) if i < len(view_counts) else 0,
                "video_count": int(video_counts[i]) if i < len(video_counts) else 0,
                "platform": "tiktok",
            })
    except requests.RequestException:
        pass
    return results


def scrape_trending_music(region: str = "US", limit: int = 25) -> List[Dict]:
    """Extract trending music/audio from TikTok."""
    videos = scrape_trending_videos(region=region, limit=50)

    music_counts: Dict[str, int] = {}
    music_data: Dict[str, Dict] = {}

    for video in videos:
        if "error" in video or not video.get("music_title"):
            continue
        music_key = f"{video['music_title']}||{video['music_author']}"
        music_counts[music_key] = music_counts.get(music_key, 0) + 1
        if music_key not in music_data:
            music_data[music_key] = {
                "music_title": video["music_title"],
                "music_author": video["music_author"],
                "music_id": video.get("music_id", ""),
                "is_original": video.get("music_is_original", False),
                "total_views": 0,
            }
        music_data[music_key]["total_views"] += video.get("views", 0)

    sorted_music = sorted(music_counts.items(), key=lambda x: x[1], reverse=True)
    results = []
    for rank, (key, count) in enumerate(sorted_music[:limit], 1):
        data = music_data[key]
        results.append({
            "rank": rank,
            "song_title": data["music_title"],
            "artist": data["music_author"],
            "music_id": data["music_id"],
            "videos_using": count,
            "total_views": data["total_views"],
            "is_original_sound": data["is_original"],
            "tiktok_url": (
                f"https://www.tiktok.com/music/{data['music_id']}"
                if data["music_id"] else ""
            ),
            "platform": "tiktok",
        })
    return results


def search_hashtag_videos(hashtag: str, limit: int = 20) -> List[Dict]:
    """Search TikTok for videos using a specific hashtag."""
    clean = hashtag.lstrip("#")
    sess = _tt_session()
    params = {
        "challengeName": clean,
        "count": min(limit, 30),
        "cursor": 0,
        "sourceType": 67,
    }
    try:
        resp = sess.get(_TT_HASHTAG_URL, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("itemList", [])
            return _parse_tt_items(items)
    except (requests.RequestException, json.JSONDecodeError):
        pass
    return []
