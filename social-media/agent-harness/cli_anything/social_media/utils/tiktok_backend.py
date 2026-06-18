"""TikTok backend — scrapes trending content, hashtags, and sounds.

Uses TikTokApi (Playwright-based) when available, falls back to
requests-based scraping with browser headers.

NOTE: TikTok scraping operates in a gray area of TikTok's ToS.
This is provided for personal research/strategy purposes only.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import requests

_CACHE_PATH = Path.home() / ".cli-anything-social" / "tiktok_cache.json"

# Realistic browser headers to avoid bot detection
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.tiktok.com/",
    "Origin": "https://www.tiktok.com",
}

# Known trending hashtag categories for seeding when API unavailable
_CATEGORY_SEEDS = {
    "all": ["fyp", "foryou", "viral", "trending", "foryoupage"],
    "music": ["music", "song", "newsong", "musicvideo", "singersongwriter"],
    "dance": ["dance", "dancechallenge", "choreography", "dancetrend"],
    "comedy": ["funny", "comedy", "humor", "lol", "meme"],
    "food": ["food", "recipe", "cooking", "foodtok", "whatieatinaday"],
    "fitness": ["fitness", "workout", "gym", "fitnessmotivation", "health"],
    "fashion": ["fashion", "ootd", "style", "outfit", "fashiontok"],
    "beauty": ["beauty", "makeup", "skincare", "beautytips", "glam"],
    "finance": ["finance", "money", "investing", "personalfinance", "crypto"],
    "travel": ["travel", "wanderlust", "travellife", "roadtrip", "explore"],
    "gaming": ["gaming", "gamer", "videogames", "gameplay", "twitch"],
    "motivation": ["motivation", "mindset", "success", "entrepreneur", "hustle"],
    "education": ["learnontiktok", "didyouknow", "facts", "education", "howto"],
    "pets": ["pets", "dogsoftiktok", "cats", "cutepets", "animallovers"],
    "diy": ["diy", "craft", "tutorial", "lifehacks", "howto"],
}


class TikTokBackend:
    """Wraps TikTok data access. Uses TikTokApi when available, else fallback."""

    def __init__(self):
        self._playwright_available = self._check_playwright()
        _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

    def _check_playwright(self) -> bool:
        try:
            import playwright  # noqa
            return True
        except ImportError:
            return False

    # ── Trending Hashtags ─────────────────────────────────────────────────────

    def get_trending_hashtags(
        self,
        category: str = "all",
        region: str = "US",
        top_n: int = 30,
    ) -> list[dict]:
        """Get trending TikTok hashtags. Tries API then falls back to research data."""
        cached = self.load_cache(f"hashtags_{category}_{region}")
        if cached:
            return cached[:top_n]

        if self._playwright_available:
            try:
                result = self._fetch_trending_api(category, top_n)
                if result:
                    self.cache_results(f"hashtags_{category}_{region}", result)
                    return result[:top_n]
            except Exception:
                pass

        result = self._trending_hashtags_web(category, region, top_n)
        self.cache_results(f"hashtags_{category}_{region}", result)
        return result

    def _fetch_trending_api(self, category: str, top_n: int) -> list[dict]:
        """Use TikTokApi (requires Playwright) to fetch trending hashtags."""
        import asyncio

        async def _fetch():
            from TikTokApi import TikTokApi
            results = []
            async with TikTokApi() as api:
                await api.create_sessions(
                    ms_tokens=[], num_sessions=1, sleep_after=3,
                    headless=True,
                )
                seeds = _CATEGORY_SEEDS.get(category, _CATEGORY_SEEDS["all"])
                for seed in seeds[:3]:
                    tag = api.hashtag(name=seed)
                    info = await tag.info()
                    results.append({
                        "hashtag": f"#{seed}",
                        "view_count": info.as_dict.get("stats", {}).get("viewCount", 0),
                        "video_count": info.as_dict.get("stats", {}).get("videoCount", 0),
                        "is_trending": True,
                        "source": "tiktok_api",
                    })
            return results

        return asyncio.run(_fetch())

    def _trending_hashtags_web(
        self, category: str, region: str, top_n: int
    ) -> list[dict]:
        """Requests-based approach using TikTok's internal suggestion endpoints."""
        results = []

        try:
            url = "https://www.tiktok.com/api/suggest/get/"
            params = {
                "keyword": _CATEGORY_SEEDS.get(category, ["trending"])[0],
                "count": 20,
                "from": 0,
                "lang": "en",
                "country": region.lower(),
            }
            resp = requests.get(url, headers=_HEADERS, params=params, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("sug_list", [])[:top_n]:
                    tag = item.get("sug_term", "").lstrip("#")
                    if tag:
                        results.append({
                            "hashtag": f"#{tag}",
                            "view_count": 0,
                            "video_count": 0,
                            "is_trending": True,
                            "source": "tiktok_suggest",
                        })
        except Exception:
            pass

        # Supplement with known high-performing hashtags for the category
        known = _CATEGORY_SEEDS.get(category, _CATEGORY_SEEDS["all"])
        existing_tags = {r["hashtag"] for r in results}
        for tag in known:
            htag = f"#{tag}"
            if htag not in existing_tags:
                results.append({
                    "hashtag": htag,
                    "view_count": None,
                    "video_count": None,
                    "is_trending": True,
                    "source": "research",
                })
        return results[:top_n]

    # ── Trending Sounds / Music ───────────────────────────────────────────────

    def get_trending_sounds(self, region: str = "US", top_n: int = 20) -> list[dict]:
        """Get trending TikTok sounds/music."""
        cached = self.load_cache(f"sounds_{region}")
        if cached:
            return cached[:top_n]

        result = self._fetch_trending_sounds_web(region, top_n)
        self.cache_results(f"sounds_{region}", result)
        return result

    def _fetch_trending_sounds_web(self, region: str, top_n: int) -> list[dict]:
        """Scrape trending sounds from TikTok's discover page."""
        sounds = []
        try:
            url = "https://www.tiktok.com/api/discover/music/"
            params = {
                "scene": 0,
                "count": top_n,
                "from": 0,
                "lang": "en",
                "country": region.lower(),
            }
            resp = requests.get(url, headers=_HEADERS, params=params, timeout=8)
            if resp.status_code == 200:
                for item in resp.json().get("musicInfoList", [])[:top_n]:
                    music = item.get("music", {})
                    sounds.append({
                        "id": music.get("id", ""),
                        "title": music.get("title", ""),
                        "author": music.get("authorName", ""),
                        "duration": music.get("duration", 0),
                        "video_count": item.get("useCount", 0),
                        "cover": music.get("coverThumb", ""),
                        "is_original": music.get("original", False),
                        "source": "tiktok_api",
                    })
        except Exception:
            pass

        if not sounds:
            # Return placeholder data when no network access
            sounds = [
                {
                    "id": "", "title": "Trending sound data requires TikTok access",
                    "author": "Configure network access",
                    "duration": 0, "video_count": 0, "cover": "",
                    "is_original": False, "source": "placeholder",
                }
            ]
        return sounds

    # ── Trending Videos ───────────────────────────────────────────────────────

    def get_trending_videos(
        self, region: str = "US", category: str = "all", top_n: int = 20
    ) -> list[dict]:
        """Get trending TikTok videos."""
        cached = self.load_cache(f"videos_{category}_{region}")
        if cached:
            return cached[:top_n]

        result = self._fetch_trending_videos_web(region, category, top_n)
        self.cache_results(f"videos_{category}_{region}", result)
        return result

    def _fetch_trending_videos_web(
        self, region: str, category: str, top_n: int
    ) -> list[dict]:
        videos = []
        try:
            seed = _CATEGORY_SEEDS.get(category, ["trending"])[0]
            url = "https://www.tiktok.com/api/search/item/full/"
            params = {
                "keyword": seed,
                "count": top_n,
                "offset": 0,
                "lang": "en",
                "country": region.lower(),
            }
            resp = requests.get(url, headers=_HEADERS, params=params, timeout=8)
            if resp.status_code == 200:
                for item in resp.json().get("item_list", [])[:top_n]:
                    author = item.get("author", {})
                    stats = item.get("stats", {})
                    videos.append({
                        "id": item.get("id", ""),
                        "description": item.get("desc", ""),
                        "author": author.get("nickname", ""),
                        "author_id": author.get("uniqueId", ""),
                        "plays": stats.get("playCount", 0),
                        "likes": stats.get("diggCount", 0),
                        "shares": stats.get("shareCount", 0),
                        "comments": stats.get("commentCount", 0),
                        "hashtags": [t["hashtagName"] for t in item.get("textExtra", []) if "hashtagName" in t],
                        "music": item.get("music", {}).get("title", ""),
                        "music_author": item.get("music", {}).get("authorName", ""),
                        "duration": item.get("video", {}).get("duration", 0),
                        "url": f"https://www.tiktok.com/@{author.get('uniqueId', '')}/ video/{item.get('id', '')}",
                        "source": "tiktok_web",
                    })
        except Exception:
            pass
        return videos

    # ── Cache ─────────────────────────────────────────────────────────────────

    def cache_results(self, key: str, data: list) -> None:
        cache = {}
        if _CACHE_PATH.exists():
            try:
                cache = json.loads(_CACHE_PATH.read_text())
            except Exception:
                cache = {}
        cache[key] = {"data": data, "timestamp": time.time()}
        _CACHE_PATH.write_text(json.dumps(cache, indent=2))

    def load_cache(self, key: str, max_age_seconds: int = 1800) -> list | None:
        if not _CACHE_PATH.exists():
            return None
        try:
            cache = json.loads(_CACHE_PATH.read_text())
            entry = cache.get(key)
            if entry and (time.time() - entry["timestamp"]) < max_age_seconds:
                return entry["data"]
        except Exception:
            pass
        return None
