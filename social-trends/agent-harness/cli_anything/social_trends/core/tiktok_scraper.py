"""TikTok viral trend scraper using TikTokApi (Playwright) with HTTP fallback."""

import json
import re
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from typing import Optional


TIKTOK_DISCOVER_URL = "https://www.tiktok.com/discover"
TIKTOK_API_TRENDING = "https://www.tiktok.com/api/explore/item_list/"


def _tiktokapi_available() -> bool:
    try:
        import TikTokApi  # noqa: F401
        return True
    except ImportError:
        return False


def _fetch_via_tiktokapi(region: str = "US", limit: int = 20) -> list[dict]:
    """Fetch trending using the TikTokApi package (requires Playwright + ms_token)."""
    import asyncio
    from TikTokApi import TikTokApi

    results = []

    async def _run():
        async with TikTokApi() as api:
            await api.create_sessions(num_sessions=1, sleep_after=3, headless=True)
            async for video in api.trending.videos(count=limit):
                data = video.as_dict
                author = data.get("author", {})
                stats = data.get("stats", {})
                music = data.get("music", {})
                desc = data.get("desc", "")
                challenges = data.get("challenges", [])
                ht_from_challenges = [f"#{c.get('title','')}" for c in challenges if c.get("title")]
                ht_from_desc = _extract_hashtags(desc)
                results.append({
                    "id": data.get("id", ""),
                    "description": desc,
                    "url": f"https://www.tiktok.com/@{author.get('uniqueId','')}/video/{data.get('id','')}",
                    "author": author.get("uniqueId", ""),
                    "author_name": author.get("nickname", ""),
                    "play_count": stats.get("playCount", 0),
                    "digg_count": stats.get("diggCount", 0),
                    "comment_count": stats.get("commentCount", 0),
                    "share_count": stats.get("shareCount", 0),
                    "hashtags": list(set(ht_from_desc + ht_from_challenges)),
                    "music_id": music.get("id", ""),
                    "music_title": music.get("title", ""),
                    "music_author": music.get("authorName", ""),
                    "music_url": music.get("playUrl", ""),
                    "duration": data.get("video", {}).get("duration", 0),
                    "create_time": data.get("createTime", 0),
                    "platform": "tiktok",
                    "source": "tiktokapi",
                })

    asyncio.run(_run())
    return results


def _fetch_via_rapidapi(api_key: str, limit: int = 20, region: str = "US") -> list[dict]:
    """Fetch trending via RapidAPI TikTok endpoints."""
    url = "https://tiktok-scraper7.p.rapidapi.com/feed/list"
    params = urllib.parse.urlencode({"region": region.lower(), "count": min(limit, 30)})
    req = urllib.request.Request(
        f"{url}?{params}",
        headers={
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "tiktok-scraper7.p.rapidapi.com",
        }
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())

    results = []
    for item in data.get("data", {}).get("videos", [])[:limit]:
        author = item.get("author", {})
        music = item.get("music", {})
        desc = item.get("desc", "")
        results.append({
            "id": item.get("video_id", ""),
            "description": desc,
            "url": item.get("video_url", ""),
            "author": author.get("unique_id", ""),
            "author_name": author.get("nickname", ""),
            "play_count": item.get("play_count", 0),
            "digg_count": item.get("digg_count", 0),
            "comment_count": item.get("comment_count", 0),
            "share_count": item.get("share_count", 0),
            "hashtags": _extract_hashtags(desc),
            "music_title": music.get("title", ""),
            "music_author": music.get("author", ""),
            "platform": "tiktok",
            "source": "rapidapi",
        })
    return results


def _fetch_hashtag_videos(hashtag: str, limit: int = 10, api_key: Optional[str] = None) -> list[dict]:
    """Fetch top videos for a specific TikTok hashtag via RapidAPI."""
    if not api_key:
        return []
    tag = hashtag.lstrip("#")
    url = "https://tiktok-scraper7.p.rapidapi.com/challenge/posts"
    params = urllib.parse.urlencode({"name": tag, "count": min(limit, 30)})
    req = urllib.request.Request(
        f"{url}?{params}",
        headers={
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "tiktok-scraper7.p.rapidapi.com",
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        return [
            {
                "id": v.get("video_id", ""),
                "description": v.get("desc", ""),
                "url": v.get("video_url", ""),
                "author": v.get("author", {}).get("unique_id", ""),
                "play_count": v.get("play_count", 0),
                "digg_count": v.get("digg_count", 0),
                "hashtags": _extract_hashtags(v.get("desc", "")),
                "music_title": v.get("music", {}).get("title", ""),
                "platform": "tiktok",
                "source": "rapidapi-hashtag",
            }
            for v in data.get("data", {}).get("videos", [])[:limit]
        ]
    except Exception:
        return []


def _extract_hashtags(text: str) -> list[str]:
    if not text:
        return []
    return list(set(re.findall(r"#\w+", text)))


def _demo_trending(limit: int) -> list[dict]:
    samples = [
        {"id": "tt1", "description": "POV: you discovered the #booktok trend and now can't stop reading 📚 #fyp #viral #reading", "author": "bookworm_daily", "author_name": "Book Worm", "play_count": 42000000, "digg_count": 3200000, "comment_count": 45000, "share_count": 890000, "hashtags": ["#booktok", "#fyp", "#viral", "#reading"], "music_title": "Aesthetic Chill Beats", "music_author": "LoFiStudio", "platform": "tiktok", "source": "demo"},
        {"id": "tt2", "description": "The gym glow-up nobody warned you about 💪 #gymtok #fitness #transformation #fyp", "author": "gains_with_grace", "author_name": "Grace Fitness", "play_count": 28000000, "digg_count": 2100000, "comment_count": 38000, "share_count": 560000, "hashtags": ["#gymtok", "#fitness", "#transformation", "#fyp"], "music_title": "Leveling Up", "music_author": "BeatDropper", "platform": "tiktok", "source": "demo"},
        {"id": "tt3", "description": "I tried the viral #sleepygirlmocktail and here's what happened 😴🍹 #wellness #tiktokfood #viral", "author": "wellness.willow", "author_name": "Willow Wellness", "play_count": 61000000, "digg_count": 5400000, "comment_count": 92000, "share_count": 1200000, "hashtags": ["#sleepygirlmocktail", "#wellness", "#tiktokfood", "#viral"], "music_title": "Good Night Vibes", "music_author": "ChillWave", "platform": "tiktok", "source": "demo"},
        {"id": "tt4", "description": "Theme page income report: $4,200 this month with 0 original content #themepage #passiveincome #socialmedia", "author": "digital.hustle.hq", "author_name": "Digital Hustle HQ", "play_count": 18000000, "digg_count": 1800000, "comment_count": 67000, "share_count": 430000, "hashtags": ["#themepage", "#passiveincome", "#socialmedia", "#makemoneyonline"], "music_title": "Money Moves", "music_author": "HustleBeats", "platform": "tiktok", "source": "demo"},
        {"id": "tt5", "description": "Rating every #aestheticroom trend so you don't have to 🏠✨ #interiordesign #fyp #roomcheck", "author": "aesthetic.spaces", "author_name": "Aesthetic Spaces", "play_count": 35000000, "digg_count": 2700000, "comment_count": 54000, "share_count": 780000, "hashtags": ["#aestheticroom", "#interiordesign", "#fyp", "#roomcheck"], "music_title": "Cozy Afternoon", "music_author": "AmbientVibes", "platform": "tiktok", "source": "demo"},
        {"id": "tt6", "description": "The algorithm hack that got me 100k followers in 14 days 🔥 #tiktokgrowth #algorithm #contentcreator", "author": "viral.formula", "author_name": "The Viral Formula", "play_count": 22000000, "digg_count": 1950000, "comment_count": 81000, "share_count": 620000, "hashtags": ["#tiktokgrowth", "#algorithm", "#contentcreator", "#growthhack"], "music_title": "Rise Up", "music_author": "MotivationBeats", "platform": "tiktok", "source": "demo"},
    ]
    return samples[:limit]


def get_trending(
    region: str = "US",
    limit: int = 20,
    rapidapi_key: Optional[str] = None,
    use_tiktokapi: bool = False,
) -> dict:
    """
    Fetch TikTok trending videos.

    Priority: TikTokApi (Playwright) > RapidAPI > demo fallback.
    Returns structured dict with videos, top hashtags, and trending music.
    """
    videos = []
    method = "none"

    if use_tiktokapi and _tiktokapi_available():
        try:
            videos = _fetch_via_tiktokapi(region, limit)
            method = "tiktokapi-playwright"
        except Exception as e:
            method = f"tiktokapi-failed:{e}"

    if not videos and rapidapi_key:
        try:
            videos = _fetch_via_rapidapi(rapidapi_key, limit, region)
            method = "rapidapi"
        except Exception as e:
            method = f"rapidapi-failed:{e}"

    if not videos:
        videos = _demo_trending(limit)
        method = "demo"

    all_hashtags: dict[str, int] = {}
    all_music: dict[str, int] = {}
    for v in videos:
        for ht in v.get("hashtags", []):
            all_hashtags[ht] = all_hashtags.get(ht, 0) + 1
        music_key = f"{v.get('music_title', '')} — {v.get('music_author', '')}"
        if music_key.strip("— "):
            all_music[music_key] = all_music.get(music_key, 0) + 1

    top_hashtags = sorted(all_hashtags.items(), key=lambda x: x[1], reverse=True)
    top_music = sorted(all_music.items(), key=lambda x: x[1], reverse=True)

    return {
        "platform": "tiktok",
        "region": region,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "method": method,
        "total": len(videos),
        "videos": videos,
        "top_hashtags": [{"hashtag": h, "count": c} for h, c in top_hashtags[:30]],
        "trending_music": [{"track": t, "usage_count": c} for t, c in top_music[:20]],
    }


def get_hashtag_info(
    hashtag: str,
    limit: int = 10,
    rapidapi_key: Optional[str] = None,
) -> dict:
    """Fetch top videos for a specific TikTok hashtag."""
    videos = _fetch_hashtag_videos(hashtag, limit, rapidapi_key)
    total_plays = sum(v.get("play_count", 0) for v in videos)
    return {
        "hashtag": hashtag,
        "videos_fetched": len(videos),
        "total_plays": total_plays,
        "videos": videos,
        "platform": "tiktok",
    }
