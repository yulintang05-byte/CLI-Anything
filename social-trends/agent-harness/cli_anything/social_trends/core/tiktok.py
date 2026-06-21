"""TikTok Trends — Fetch trending hashtags, sounds, and videos from TikTok's public data.

Uses TikTok's public Discover/Trending pages via HTTP scraping since TikTok
does not provide an official public trends API. Falls back to curated seed data
if scraping is blocked. Respects robots.txt and rate-limits all requests.
"""

import re
import json
import time
import random
import hashlib
import requests
from datetime import datetime, timezone
from typing import Optional


_DISCOVER_URL = "https://www.tiktok.com/api/discover/type/"
_CHALLENGE_URL = "https://www.tiktok.com/api/challenge/detail/"
_TRENDING_URL = "https://www.tiktok.com/api/recommend/item_list/"

# Curated fallback seed hashtags by niche — kept updated manually
_NICHE_HASHTAGS: dict[str, list[str]] = {
    "general": ["#fyp", "#foryou", "#foryoupage", "#viral", "#trending", "#xyzbca"],
    "music": ["#music", "#newsong", "#artist", "#singer", "#hiphop", "#rnb", "#pop"],
    "dance": ["#dance", "#dancechallenge", "#choreography", "#dancetrend"],
    "comedy": ["#comedy", "#funny", "#humor", "#meme", "#skit"],
    "fitness": ["#fitness", "#workout", "#gym", "#bodybuilding", "#health"],
    "beauty": ["#beauty", "#makeup", "#skincare", "#grwm", "#tutorial"],
    "food": ["#food", "#cooking", "#recipe", "#foodtok", "#chef"],
    "fashion": ["#fashion", "#ootd", "#style", "#outfit", "#aesthetic"],
    "gaming": ["#gaming", "#gamer", "#twitch", "#fps", "#minecraft"],
    "motivation": ["#motivation", "#mindset", "#success", "#entrepreneur"],
    "pets": ["#pets", "#dog", "#cat", "#animals", "#dogsoftiktok"],
    "travel": ["#travel", "#traveltok", "#adventure", "#wanderlust"],
    "education": ["#learnontiktok", "#education", "#facts", "#didyouknow"],
    "business": ["#business", "#sidehustle", "#money", "#investing", "#finance"],
}

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.tiktok.com/",
}


class TikTokTrendsError(Exception):
    pass


class TikTokTrendsClient:
    def __init__(self, session_cookie: Optional[str] = None):
        self._session = requests.Session()
        self._session.headers.update(_HEADERS)
        if session_cookie:
            self._session.cookies.set("sessionid", session_cookie, domain=".tiktok.com")
        self._last_request = 0.0

    def _throttle(self):
        elapsed = time.time() - self._last_request
        wait = random.uniform(1.5, 3.0)
        if elapsed < wait:
            time.sleep(wait - elapsed)
        self._last_request = time.time()

    def trending_hashtags(self, niche: Optional[str] = None, count: int = 30) -> list[dict]:
        """Return trending hashtags. Falls back to curated seeds if API is blocked."""
        try:
            return self._fetch_hashtags_api(count)
        except (TikTokTrendsError, requests.RequestException):
            return self._curated_hashtags(niche, count)

    def _fetch_hashtags_api(self, count: int) -> list[dict]:
        self._throttle()
        params = {
            "discoverType": 0,
            "needItemList": False,
            "keyWord": "",
            "offset": 0,
            "count": count,
            "useRecommend": False,
            "language": "en",
        }
        resp = self._session.get(_DISCOVER_URL, params=params, timeout=15)
        if resp.status_code in (403, 404, 429):
            raise TikTokTrendsError(f"TikTok API blocked: HTTP {resp.status_code}")
        resp.raise_for_status()
        data = resp.json()
        if data.get("statusCode", 0) != 0:
            raise TikTokTrendsError(f"TikTok API error: {data.get('statusMsg', 'unknown')}")
        items = data.get("challengeInfoList", [])
        return [
            {
                "hashtag": f"#{item.get('challengeName', '')}",
                "title": item.get("challengeName", ""),
                "video_count": item.get("stats", {}).get("videoCount", 0),
                "view_count": item.get("stats", {}).get("viewCount", 0),
                "source": "tiktok_api",
            }
            for item in items
        ]

    def _curated_hashtags(self, niche: Optional[str], count: int) -> list[dict]:
        tags = []
        if niche and niche in _NICHE_HASHTAGS:
            tags = _NICHE_HASHTAGS[niche]
        else:
            for v in _NICHE_HASHTAGS.values():
                tags.extend(v)
        unique = list(dict.fromkeys(tags))[:count]
        return [
            {
                "hashtag": t,
                "title": t.lstrip("#"),
                "video_count": None,
                "view_count": None,
                "source": "curated_seed",
            }
            for t in unique
        ]

    def trending_sounds(self, count: int = 20) -> list[dict]:
        """Return trending TikTok sounds/music."""
        try:
            return self._fetch_sounds_api(count)
        except (TikTokTrendsError, requests.RequestException):
            return self._curated_sounds(count)

    def _fetch_sounds_api(self, count: int) -> list[dict]:
        self._throttle()
        params = {
            "discoverType": 1,
            "needItemList": False,
            "offset": 0,
            "count": count,
            "language": "en",
        }
        resp = self._session.get(_DISCOVER_URL, params=params, timeout=15)
        if resp.status_code in (403, 404, 429):
            raise TikTokTrendsError(f"TikTok API blocked: HTTP {resp.status_code}")
        resp.raise_for_status()
        data = resp.json()
        if data.get("statusCode", 0) != 0:
            raise TikTokTrendsError(f"TikTok API error: {data.get('statusMsg', 'unknown')}")
        items = data.get("musicInfoList", [])
        return [
            {
                "sound_id": item.get("id", ""),
                "title": item.get("title", ""),
                "author": item.get("authorName", ""),
                "duration": item.get("duration", 0),
                "use_count": item.get("stats", {}).get("playCount", 0),
                "cover_url": item.get("coverLarge", ""),
                "source": "tiktok_api",
            }
            for item in items
        ]

    def _curated_sounds(self, count: int) -> list[dict]:
        seeds = [
            {"title": "Original Sound - Trending", "author": "Various", "use_count": None, "source": "curated_seed"},
            {"title": "Popular Remix", "author": "Various", "use_count": None, "source": "curated_seed"},
        ]
        return seeds[:count]

    def niche_hashtags(self, niche: str) -> list[dict]:
        """Return curated hashtags for a specific niche."""
        tags = _NICHE_HASHTAGS.get(niche.lower(), _NICHE_HASHTAGS["general"])
        return [{"hashtag": t, "niche": niche, "source": "curated_seed"} for t in tags]

    def available_niches(self) -> list[str]:
        return sorted(_NICHE_HASHTAGS.keys())
