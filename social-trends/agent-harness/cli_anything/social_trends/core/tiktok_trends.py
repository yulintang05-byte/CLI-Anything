import re
from typing import Any, Dict, List

from ..utils.social_backend import cache_key, get_cached, get_config, get_session, set_cached

TIKTOK_API_BASE = "https://www.tiktok.com/api"

# Evergreen high-traffic hashtags used as fallback when live scraping is unavailable
_EVERGREEN_HASHTAGS = [
    {"hashtag": "#fyp", "category": "Viral", "avg_views": "1T+", "description": "For You Page – highest algorithmic reach"},
    {"hashtag": "#foryou", "category": "Viral", "avg_views": "500B+", "description": "FYP trigger"},
    {"hashtag": "#foryoupage", "category": "Viral", "avg_views": "400B+", "description": "FYP trigger variant"},
    {"hashtag": "#trending", "category": "Discovery", "avg_views": "200B+", "description": "Trending discovery"},
    {"hashtag": "#viral", "category": "Discovery", "avg_views": "100B+", "description": "Viral content signal"},
    {"hashtag": "#tiktok", "category": "Platform", "avg_views": "50B+", "description": "Platform reach"},
    {"hashtag": "#funny", "category": "Entertainment", "avg_views": "300B+", "description": "Comedy content"},
    {"hashtag": "#dance", "category": "Dance", "avg_views": "200B+", "description": "Dance challenges"},
    {"hashtag": "#music", "category": "Music", "avg_views": "100B+", "description": "Music content"},
    {"hashtag": "#duet", "category": "Engagement", "avg_views": "80B+", "description": "Duet collab content"},
    {"hashtag": "#stitch", "category": "Engagement", "avg_views": "60B+", "description": "Stitch response content"},
    {"hashtag": "#comedy", "category": "Entertainment", "avg_views": "150B+", "description": "Comedy skits"},
    {"hashtag": "#beauty", "category": "Beauty", "avg_views": "100B+", "description": "Beauty & makeup"},
    {"hashtag": "#fashion", "category": "Fashion", "avg_views": "80B+", "description": "Fashion content"},
    {"hashtag": "#fitness", "category": "Health", "avg_views": "60B+", "description": "Fitness & workout"},
    {"hashtag": "#food", "category": "Food", "avg_views": "90B+", "description": "Food & recipes"},
    {"hashtag": "#travel", "category": "Travel", "avg_views": "70B+", "description": "Travel vlogs"},
    {"hashtag": "#motivation", "category": "Lifestyle", "avg_views": "50B+", "description": "Motivational content"},
    {"hashtag": "#business", "category": "Business", "avg_views": "40B+", "description": "Business tips"},
    {"hashtag": "#entrepreneur", "category": "Business", "avg_views": "30B+", "description": "Entrepreneurship"},
    {"hashtag": "#gaming", "category": "Gaming", "avg_views": "80B+", "description": "Gaming content"},
    {"hashtag": "#skincare", "category": "Beauty", "avg_views": "50B+", "description": "Skincare routines"},
    {"hashtag": "#grwm", "category": "Lifestyle", "avg_views": "60B+", "description": "Get ready with me"},
    {"hashtag": "#dayinmylife", "category": "Lifestyle", "avg_views": "40B+", "description": "DITL vlogs"},
    {"hashtag": "#storytime", "category": "Entertainment", "avg_views": "45B+", "description": "Story-telling content"},
    {"hashtag": "#learnontiktok", "category": "Education", "avg_views": "55B+", "description": "Educational content"},
    {"hashtag": "#booktok", "category": "Books", "avg_views": "35B+", "description": "Book community"},
    {"hashtag": "#foodtok", "category": "Food", "avg_views": "40B+", "description": "Food community"},
    {"hashtag": "#pettok", "category": "Pets", "avg_views": "30B+", "description": "Pet content"},
    {"hashtag": "#techtok", "category": "Tech", "avg_views": "25B+", "description": "Technology content"},
]


def _auth_headers() -> Dict[str, str]:
    config = get_config()
    headers: Dict[str, str] = {
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
    if config.get("tiktok_cookie"):
        headers["Cookie"] = config["tiktok_cookie"]
    return headers


def _extract_hashtags(items: list) -> List[Dict[str, Any]]:
    seen: Dict[str, Dict[str, Any]] = {}
    for item in items:
        stats = item.get("stats", {})
        play_count = stats.get("playCount", 0)
        for ch in item.get("challenges", []):
            name = ch.get("title", "").lower()
            if name:
                if name not in seen:
                    seen[name] = {
                        "hashtag": f"#{name}",
                        "view_count": ch.get("stats", {}).get("viewCount", 0),
                        "video_count": ch.get("stats", {}).get("videoCount", 0),
                        "description": ch.get("desc", ""),
                    }
                else:
                    seen[name]["view_count"] += play_count
        for ht in re.findall(r"#(\w+)", item.get("desc", "")):
            h = ht.lower()
            if h not in seen:
                seen[h] = {"hashtag": f"#{h}", "view_count": play_count, "video_count": 1, "description": ""}
            else:
                seen[h]["view_count"] += play_count
                seen[h]["video_count"] += 1
    return sorted(seen.values(), key=lambda x: x["view_count"], reverse=True)


def get_trending_hashtags_tiktok(country: str = "US", top_n: int = 30) -> List[Dict[str, Any]]:
    ck = cache_key("tt_hashtags", country, top_n)
    cached = get_cached(ck)
    if cached:
        return cached

    session = get_session()
    session.headers.update(_auth_headers())
    try:
        resp = session.get(
            f"{TIKTOK_API_BASE}/explore/item_list/",
            params={
                "count": 16,
                "type": "1",
                "secUid": "",
                "maxCursor": "0",
                "minCursor": "0",
                "sourceType": "12",
                "appId": "1233",
                "region": country,
                "priority_region": country,
                "language": "en",
            },
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            tags = _extract_hashtags(data.get("itemList", []))
            if tags:
                result = tags[:top_n]
                set_cached(ck, result, ttl_seconds=1800)
                return result
    except Exception:
        pass

    # Fallback to curated evergreen list
    result = _EVERGREEN_HASHTAGS[:top_n]
    set_cached(ck, result, ttl_seconds=1800)
    return result


def get_trending_sounds(country: str = "US", top_n: int = 20) -> List[Dict[str, Any]]:
    ck = cache_key("tt_sounds", country, top_n)
    cached = get_cached(ck)
    if cached:
        return cached

    session = get_session()
    session.headers.update(_auth_headers())
    try:
        resp = session.get(
            f"{TIKTOK_API_BASE}/music/trending/",
            params={"count": top_n, "region": country, "language": "en"},
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            sounds = [
                {
                    "id": m.get("id", ""),
                    "title": m.get("title", ""),
                    "artist": m.get("authorName", ""),
                    "play_count": m.get("stats", {}).get("playCount", 0),
                    "duration": m.get("duration", 0),
                    "cover": m.get("coverThumb", ""),
                }
                for m in data.get("musicList", [])
            ]
            if sounds:
                set_cached(ck, sounds, ttl_seconds=3600)
                return sounds[:top_n]
    except Exception:
        pass

    fallback = [
        {
            "note": "Live trending sounds require a TikTok session cookie.",
            "action": "Run: social-trends config set tiktok-cookie <cookie-string>",
            "tip": "Open TikTok in Chrome → DevTools → Application → Cookies → copy the 'Cookie' header value",
        }
    ]
    set_cached(ck, fallback, ttl_seconds=1800)
    return fallback


def get_trending_videos_tiktok(country: str = "US", top_n: int = 20) -> List[Dict[str, Any]]:
    ck = cache_key("tt_videos", country, top_n)
    cached = get_cached(ck)
    if cached:
        return cached

    session = get_session()
    session.headers.update(_auth_headers())
    try:
        resp = session.get(
            f"{TIKTOK_API_BASE}/recommend/item_list/",
            params={
                "count": top_n,
                "type": "5",
                "secUid": "",
                "maxCursor": "0",
                "minCursor": "0",
                "sourceType": "12",
                "appId": "1233",
                "region": country,
                "priority_region": country,
                "language": "en",
                "isNonPersonalized": "1",
            },
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            videos = []
            for item in data.get("itemList", []):
                author = item.get("author", {})
                stats = item.get("stats", {})
                music = item.get("music", {})
                uid = author.get("uniqueId", "")
                videos.append({
                    "id": item.get("id", ""),
                    "description": item.get("desc", ""),
                    "author": uid,
                    "author_name": author.get("nickname", ""),
                    "play_count": stats.get("playCount", 0),
                    "like_count": stats.get("diggCount", 0),
                    "comment_count": stats.get("commentCount", 0),
                    "share_count": stats.get("shareCount", 0),
                    "music_title": music.get("title", ""),
                    "music_artist": music.get("authorName", ""),
                    "url": f"https://www.tiktok.com/@{uid}/video/{item.get('id', '')}",
                    "hashtags": re.findall(r"#(\w+)", item.get("desc", "")),
                })
            if videos:
                result = videos[:top_n]
                set_cached(ck, result, ttl_seconds=1800)
                return result
    except Exception:
        pass

    return []
