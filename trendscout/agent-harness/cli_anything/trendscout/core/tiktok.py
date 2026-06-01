"""TrendScout – TikTok trending scraper.

Fetches trending hashtags, sounds, and video metadata from TikTok's
public explore/trending endpoints using plain HTTP requests.
No API key or login required for public trending data.
"""

import json
import re
import urllib.request
import urllib.parse
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.0 Mobile/15E148 Safari/604.1"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.tiktok.com/",
}

# TikTok public trending hashtag API (no auth, paginated)
_HASHTAG_TRENDING_URL = (
    "https://www.tiktok.com/api/explore/item_list/"
    "?aid=1988&app_language=en&count=30&from_page=fyp"
)

_DISCOVER_URL = "https://www.tiktok.com/node/share/discover"


def _get(url: str, timeout: int = 15) -> str:
    req = urllib.request.Request(url, headers=_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as exc:
        raise RuntimeError(f"HTTP request failed: {exc}")


def fetch_trending_hashtags(limit: int = 30) -> Dict[str, Any]:
    """Fetch trending hashtags on TikTok via public discover endpoint."""
    try:
        # TikTok trending discover page
        raw = _get("https://www.tiktok.com/explore", timeout=20)
        hashtags = _parse_hashtags_from_html(raw)

        if not hashtags:
            # Try alternate endpoint
            raw2 = _get(
                "https://www.tiktok.com/api/discover/hashtag/"
                "?aid=1988&count=30&from_page=fyp",
                timeout=15,
            )
            data = json.loads(raw2)
            hashtags = _parse_hashtags_from_json(data)

        return {
            "source": "tiktok",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "count": len(hashtags[:limit]),
            "hashtags": hashtags[:limit],
        }

    except Exception as exc:
        return _demo_hashtags(limit, str(exc))


def fetch_trending_sounds(limit: int = 20) -> Dict[str, Any]:
    """Fetch currently trending TikTok sounds/music."""
    try:
        raw = _get(
            "https://www.tiktok.com/api/music/trending/"
            "?aid=1988&count=20&from_page=fyp",
            timeout=15,
        )
        data = json.loads(raw)
        sounds = _parse_sounds_from_json(data)

        return {
            "source": "tiktok",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "count": len(sounds[:limit]),
            "sounds": sounds[:limit],
        }

    except Exception as exc:
        return _demo_sounds(limit, str(exc))


def fetch_fyp_trends(limit: int = 20) -> Dict[str, Any]:
    """Fetch trending FYP (For You Page) content metadata."""
    try:
        raw = _get(_HASHTAG_TRENDING_URL, timeout=20)
        data = json.loads(raw)
        items = data.get("itemList", [])

        videos = []
        for item in items[:limit]:
            desc = item.get("desc", "")
            author = item.get("author", {})
            stats = item.get("stats", {})
            music = item.get("music", {})
            challenges = item.get("challenges", [])

            hashtags = re.findall(r"#\w+", desc)

            videos.append({
                "id": item.get("id", ""),
                "description": desc[:200],
                "author": author.get("uniqueId", ""),
                "author_nickname": author.get("nickname", ""),
                "likes": stats.get("diggCount", 0),
                "comments": stats.get("commentCount", 0),
                "shares": stats.get("shareCount", 0),
                "plays": stats.get("playCount", 0),
                "music_title": music.get("title", ""),
                "music_author": music.get("authorName", ""),
                "music_id": music.get("id", ""),
                "hashtags": hashtags,
                "challenges": [c.get("title", "") for c in challenges],
                "url": f"https://www.tiktok.com/@{author.get('uniqueId', '')}/video/{item.get('id', '')}",
            })

        # Aggregate hashtag frequency
        freq: Dict[str, int] = {}
        for v in videos:
            for tag in v["hashtags"]:
                freq[tag.lower()] = freq.get(tag.lower(), 0) + 1

        top_tags = sorted(freq.items(), key=lambda x: x[1], reverse=True)

        return {
            "source": "tiktok_fyp",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "count": len(videos),
            "videos": videos,
            "top_hashtags_in_batch": [
                {"hashtag": t, "frequency": c} for t, c in top_tags[:15]
            ],
        }

    except Exception as exc:
        return _demo_fyp(limit, str(exc))


def search_hashtag(hashtag: str, limit: int = 20) -> Dict[str, Any]:
    """Search TikTok for a specific hashtag and return trending videos."""
    tag = hashtag.lstrip("#")
    try:
        url = (
            f"https://www.tiktok.com/api/search/item/full/"
            f"?keyword=%23{urllib.parse.quote(tag)}&count={limit}&from_page=search"
        )
        raw = _get(url, timeout=20)
        data = json.loads(raw)
        items = data.get("item_list", data.get("data", []))

        results = []
        for item in items[:limit]:
            desc = item.get("desc", "")
            author = item.get("author", {})
            stats = item.get("stats", {})

            results.append({
                "id": item.get("id", ""),
                "description": desc[:200],
                "author": author.get("uniqueId", ""),
                "likes": stats.get("diggCount", 0),
                "plays": stats.get("playCount", 0),
                "hashtags": re.findall(r"#\w+", desc),
                "url": f"https://www.tiktok.com/@{author.get('uniqueId', '')}/video/{item.get('id', '')}",
            })

        return {
            "source": "tiktok",
            "query_hashtag": f"#{tag}",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "count": len(results),
            "results": results,
        }

    except Exception as exc:
        raise RuntimeError(f"Hashtag search failed for #{tag}: {exc}")


# ── HTML / JSON parsers ───────────────────────────────────────────────────────

def _parse_hashtags_from_html(html: str) -> List[Dict[str, Any]]:
    """Try to extract hashtag data embedded in TikTok HTML."""
    # TikTok embeds JSON in <script id="__UNIVERSAL_DATA_FOR_REHYDRATION__">
    match = re.search(r'id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(\{.*?\})</script>', html, re.DOTALL)
    if not match:
        return []
    try:
        data = json.loads(match.group(1))
        # Walk the nested structure to find challenge/hashtag lists
        return _walk_for_challenges(data)
    except (json.JSONDecodeError, KeyError):
        return []


def _walk_for_challenges(obj: Any, depth: int = 0) -> List[Dict[str, Any]]:
    if depth > 8:
        return []
    if isinstance(obj, dict):
        # Look for challenge or hashtag keys
        if "challengeName" in obj or "hashtagName" in obj:
            name = obj.get("challengeName") or obj.get("hashtagName", "")
            return [{"hashtag": f"#{name}", "view_count": obj.get("viewCount", obj.get("views", 0))}]
        results = []
        for v in obj.values():
            results.extend(_walk_for_challenges(v, depth + 1))
        return results
    if isinstance(obj, list):
        results = []
        for item in obj[:50]:
            results.extend(_walk_for_challenges(item, depth + 1))
        return results
    return []


def _parse_hashtags_from_json(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    hashtags = []
    for item in data.get("challengeList", data.get("hashtagList", [])):
        name = item.get("challengeInfo", {}).get("challenge", {}).get("title", "") or item.get("hashtag", {}).get("title", "")
        view_count = item.get("challengeInfo", {}).get("stats", {}).get("viewCount", 0)
        if name:
            hashtags.append({"hashtag": f"#{name}", "view_count": view_count})
    return hashtags


def _parse_sounds_from_json(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    sounds = []
    for item in data.get("musicList", data.get("items", [])):
        music = item.get("music", item)
        sounds.append({
            "id": music.get("id", ""),
            "title": music.get("title", ""),
            "artist": music.get("authorName", ""),
            "duration": music.get("duration", 0),
            "play_count": music.get("playCount", 0),
            "url": music.get("playUrl", ""),
        })
    return sounds


# ── Demo / offline fallback ───────────────────────────────────────────────────

def _demo_hashtags(limit: int, error: str) -> Dict[str, Any]:
    DEMO = [
        {"hashtag": "#fyp", "view_count": 35_000_000_000},
        {"hashtag": "#foryou", "view_count": 28_000_000_000},
        {"hashtag": "#viral", "view_count": 22_000_000_000},
        {"hashtag": "#foryoupage", "view_count": 18_500_000_000},
        {"hashtag": "#trending", "view_count": 15_000_000_000},
        {"hashtag": "#tiktok", "view_count": 12_000_000_000},
        {"hashtag": "#dance", "view_count": 9_000_000_000},
        {"hashtag": "#funny", "view_count": 8_500_000_000},
        {"hashtag": "#music", "view_count": 8_000_000_000},
        {"hashtag": "#comedy", "view_count": 7_500_000_000},
        {"hashtag": "#pov", "view_count": 7_000_000_000},
        {"hashtag": "#duet", "view_count": 6_500_000_000},
        {"hashtag": "#aesthetic", "view_count": 6_000_000_000},
        {"hashtag": "#tutorial", "view_count": 5_500_000_000},
        {"hashtag": "#challenge", "view_count": 5_000_000_000},
        {"hashtag": "#motivation", "view_count": 4_800_000_000},
        {"hashtag": "#food", "view_count": 4_500_000_000},
        {"hashtag": "#fashion", "view_count": 4_200_000_000},
        {"hashtag": "#fitness", "view_count": 4_000_000_000},
        {"hashtag": "#gaming", "view_count": 3_800_000_000},
        {"hashtag": "#skincare", "view_count": 3_600_000_000},
        {"hashtag": "#studywithme", "view_count": 3_400_000_000},
        {"hashtag": "#storytime", "view_count": 3_200_000_000},
        {"hashtag": "#satisfying", "view_count": 3_000_000_000},
        {"hashtag": "#cats", "view_count": 2_800_000_000},
        {"hashtag": "#dogs", "view_count": 2_600_000_000},
        {"hashtag": "#cooking", "view_count": 2_500_000_000},
        {"hashtag": "#workout", "view_count": 2_400_000_000},
        {"hashtag": "#nightroutine", "view_count": 2_200_000_000},
        {"hashtag": "#booktok", "view_count": 2_000_000_000},
    ]
    return {
        "source": "tiktok",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "count": len(DEMO[:limit]),
        "hashtags": DEMO[:limit],
        "demo_mode": True,
        "note": f"Demo data (TikTok blocked or unavailable): {error[:120]}",
    }


def _demo_sounds(limit: int, error: str) -> Dict[str, Any]:
    DEMO = [
        {"id": "1", "title": "Flowers", "artist": "Miley Cyrus", "duration": 200, "play_count": 15_000_000},
        {"id": "2", "title": "Cruel Summer", "artist": "Taylor Swift", "duration": 178, "play_count": 14_200_000},
        {"id": "3", "title": "As It Was", "artist": "Harry Styles", "duration": 167, "play_count": 13_800_000},
        {"id": "4", "title": "About Damn Time", "artist": "Lizzo", "duration": 193, "play_count": 12_500_000},
        {"id": "5", "title": "Running Up That Hill", "artist": "Kate Bush", "duration": 300, "play_count": 11_000_000},
        {"id": "6", "title": "Heat Waves", "artist": "Glass Animals", "duration": 238, "play_count": 10_500_000},
        {"id": "7", "title": "Easy On Me", "artist": "Adele", "duration": 224, "play_count": 9_800_000},
        {"id": "8", "title": "Super Freaky Girl", "artist": "Nicki Minaj", "duration": 195, "play_count": 9_200_000},
        {"id": "9", "title": "Anti-Hero", "artist": "Taylor Swift", "duration": 200, "play_count": 8_900_000},
        {"id": "10", "title": "Bad Habit", "artist": "Steve Lacy", "duration": 231, "play_count": 8_500_000},
    ]
    return {
        "source": "tiktok",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "count": len(DEMO[:limit]),
        "sounds": DEMO[:limit],
        "demo_mode": True,
        "note": f"Demo data (TikTok blocked or unavailable): {error[:120]}",
    }


def _demo_fyp(limit: int, error: str) -> Dict[str, Any]:
    DEMO_VIDEOS = [
        {"id": "v001", "description": "POV: you finally did it #viral #fyp #motivation", "author": "creator_vibes", "likes": 2_400_000, "plays": 18_000_000, "music_title": "Flowers", "music_author": "Miley Cyrus", "hashtags": ["#viral", "#fyp", "#motivation"]},
        {"id": "v002", "description": "Day in my life as a content creator #vlog #aesthetic #contentcreator", "author": "aesthetic_daily", "likes": 1_800_000, "plays": 12_500_000, "music_title": "Cruel Summer", "music_author": "Taylor Swift", "hashtags": ["#vlog", "#aesthetic", "#contentcreator"]},
        {"id": "v003", "description": "This trend is taking over! #dance #trending #foryou", "author": "dance_queen99", "likes": 3_200_000, "plays": 24_000_000, "music_title": "About Damn Time", "music_author": "Lizzo", "hashtags": ["#dance", "#trending", "#foryou"]},
        {"id": "v004", "description": "5 tips to grow on TikTok fast! #tiktokgrowth #tips #socialmedia", "author": "growth_hacks", "likes": 950_000, "plays": 8_200_000, "music_title": "As It Was", "music_author": "Harry Styles", "hashtags": ["#tiktokgrowth", "#tips", "#socialmedia"]},
        {"id": "v005", "description": "Cooking this recipe changed my life #foodtok #recipe #cooking", "author": "chef_viral", "likes": 1_200_000, "plays": 9_500_000, "music_title": "Heat Waves", "music_author": "Glass Animals", "hashtags": ["#foodtok", "#recipe", "#cooking"]},
    ]
    freq: Dict[str, int] = {}
    for v in DEMO_VIDEOS:
        for t in v["hashtags"]:
            freq[t] = freq.get(t, 0) + 1
    top_tags = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return {
        "source": "tiktok_fyp",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "count": len(DEMO_VIDEOS[:limit]),
        "videos": DEMO_VIDEOS[:limit],
        "top_hashtags_in_batch": [{"hashtag": t, "frequency": c} for t, c in top_tags[:10]],
        "demo_mode": True,
        "note": f"Demo data (TikTok blocked or unavailable): {error[:120]}",
    }
