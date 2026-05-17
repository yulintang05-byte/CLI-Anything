"""TikTok trend scraping via TikTokApi (playwright-based) with HTTP fallback.

TikTokApi uses a real browser session to bypass bot detection.
Run `playwright install chromium` once before using TikTok features.

Fallback: lightweight HTTP scraper for public /trending data when
the playwright backend is unavailable.
"""

import asyncio
import json
import re
import time
from collections import Counter
from typing import Optional

import requests

_TIKTOK_BASE = "https://www.tiktok.com"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
}
_NICHE_HASHTAGS = {
    "fitness": ["workout", "gymtok", "fitnessmotivation", "gym", "bodybuilding"],
    "food": ["foodtok", "cooking", "recipe", "foodie", "mukbang"],
    "travel": ["traveltok", "travel", "wanderlust", "adventure", "explore"],
    "tech": ["techtok", "tech", "gadgets", "coding", "ai"],
    "beauty": ["beautytok", "makeup", "skincare", "grwm", "glam"],
    "gaming": ["gamingtok", "gaming", "gamer", "twitch", "esports"],
    "motivation": ["motivation", "mindset", "selflove", "success", "grind"],
    "finance": ["fintok", "investing", "moneytips", "personalfinance", "stocks"],
    "fashion": ["fashiontok", "ootd", "style", "outfitinspo", "fashion"],
    "comedy": ["funny", "comedy", "lol", "humor", "meme"],
}


class TikTokScraper:
    """Fetch trending data from TikTok using TikTokApi or HTTP fallback."""

    def __init__(self, use_playwright: bool = True, ms_token: Optional[str] = None):
        self.use_playwright = use_playwright
        self.ms_token = ms_token
        self._session = requests.Session()
        self._session.headers.update(_HEADERS)

    # ── Public methods ─────────────────────────────────────────────────

    def get_trending_videos(self, count: int = 30) -> list[dict]:
        """Return trending TikTok videos. Uses playwright if available."""
        if self.use_playwright:
            try:
                return asyncio.run(self._async_trending(count))
            except Exception:
                pass
        return self._http_trending(count)

    def get_hashtag_videos(self, hashtag: str, count: int = 20) -> list[dict]:
        """Fetch top videos for a given hashtag."""
        if self.use_playwright:
            try:
                return asyncio.run(self._async_hashtag(hashtag, count))
            except Exception:
                pass
        return self._http_hashtag(hashtag, count)

    def get_niche_hashtags(self, niche: str) -> list[str]:
        """Return known seed hashtags for a niche."""
        return _NICHE_HASHTAGS.get(niche.lower(), [niche])

    def get_trending_sounds(self, videos: list[dict]) -> list[dict]:
        """Extract and rank trending sounds/music from a video list."""
        counter: Counter = Counter()
        sound_map: dict[str, dict] = {}
        for v in videos:
            sound = v.get("sound") or {}
            sid = sound.get("id") or sound.get("title", "")
            if sid:
                counter[sid] += 1
                if sid not in sound_map:
                    sound_map[sid] = sound
        results = []
        for sid, cnt in counter.most_common(20):
            info = sound_map.get(sid, {})
            results.append({
                "id": sid,
                "title": info.get("title", sid),
                "artist": info.get("author_name", "Unknown"),
                "video_count": cnt,
                "duration": info.get("duration", 0),
                "is_original": info.get("is_original", False),
            })
        return results

    def extract_hashtags(self, videos: list[dict]) -> list[tuple[str, int]]:
        """Extract hashtags from video descriptions and challenge lists."""
        counter: Counter = Counter()
        pattern = re.compile(r"#(\w+)")
        for v in videos:
            desc = v.get("description", "") or v.get("desc", "")
            tags = pattern.findall(desc.lower())
            counter.update(tags)
            for ch in v.get("challenges", []):
                title = ch.get("title", "").lower().replace(" ", "")
                if title:
                    counter[title] += 1
        return counter.most_common(50)

    def get_account_stats(self, username: str) -> dict:
        """Fetch public stats for a TikTok account (your own or competitors)."""
        url = f"{_TIKTOK_BASE}/@{username}"
        try:
            resp = self._session.get(url, timeout=15)
            resp.raise_for_status()
            data = _extract_sigi_state(resp.text)
            user_info = (
                data.get("UserPage", {})
                    .get("uniqueId", {})
                    .get(username, {})
                    .get("userInfo", {})
            )
            user = user_info.get("user", {})
            stats = user_info.get("stats", {})
            return {
                "username": username,
                "nickname": user.get("nickname", ""),
                "bio": user.get("signature", ""),
                "follower_count": stats.get("followerCount", 0),
                "following_count": stats.get("followingCount", 0),
                "video_count": stats.get("videoCount", 0),
                "heart_count": stats.get("heartCount", 0),
                "verified": user.get("verified", False),
                "url": url,
            }
        except Exception as exc:
            return {"username": username, "error": str(exc)}

    # ── Playwright async backend ───────────────────────────────────────

    async def _async_trending(self, count: int) -> list[dict]:
        try:
            from TikTokApi import TikTokApi
        except ImportError as e:
            raise ImportError("Install TikTokApi: pip install TikTokApi") from e

        kwargs = {"ms_tokens": [self.ms_token]} if self.ms_token else {}
        async with TikTokApi() as api:
            await api.create_sessions(
                num_sessions=1,
                sleep_after=3,
                **kwargs,
            )
            videos = []
            async for video in api.trending.videos(count=count):
                videos.append(_normalize_tiktok_video(video.as_dict))
            return videos

    async def _async_hashtag(self, hashtag: str, count: int) -> list[dict]:
        try:
            from TikTokApi import TikTokApi
        except ImportError as e:
            raise ImportError("Install TikTokApi: pip install TikTokApi") from e

        kwargs = {"ms_tokens": [self.ms_token]} if self.ms_token else {}
        async with TikTokApi() as api:
            await api.create_sessions(num_sessions=1, sleep_after=3, **kwargs)
            tag = api.hashtag(name=hashtag)
            videos = []
            async for video in tag.videos(count=count):
                videos.append(_normalize_tiktok_video(video.as_dict))
            return videos

    # ── HTTP fallback ──────────────────────────────────────────────────

    def _http_trending(self, count: int) -> list[dict]:
        """Best-effort HTTP scrape of TikTok trending page."""
        url = f"{_TIKTOK_BASE}/trending"
        try:
            resp = self._session.get(url, timeout=15)
            resp.raise_for_status()
            data = _extract_sigi_state(resp.text)
            items = list(data.get("ItemModule", {}).values())
            return [_normalize_tiktok_video(v) for v in items[:count]]
        except Exception:
            return []

    def _http_hashtag(self, hashtag: str, count: int) -> list[dict]:
        """Best-effort HTTP scrape of a TikTok hashtag page."""
        url = f"{_TIKTOK_BASE}/tag/{hashtag}"
        try:
            resp = self._session.get(url, timeout=15)
            resp.raise_for_status()
            data = _extract_sigi_state(resp.text)
            items = list(data.get("ItemModule", {}).values())
            return [_normalize_tiktok_video(v) for v in items[:count]]
        except Exception:
            return []


# ── Helpers ────────────────────────────────────────────────────────────

def _extract_sigi_state(html: str) -> dict:
    """Pull the __UNIVERSAL_DATA_FOR_REHYDRATION__ JSON blob from TikTok HTML."""
    match = re.search(
        r'<script\s+id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
        html,
        re.DOTALL,
    )
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    # Legacy SIGI_STATE fallback
    match = re.search(r'window\["SIGI_STATE"\]\s*=\s*(\{.*?\});', html, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    return {}


def _normalize_tiktok_video(raw: dict) -> dict:
    """Normalize raw TikTok API / scrape data to a consistent schema."""
    stats = raw.get("stats", {}) or raw.get("statistics", {})
    author = raw.get("author", {}) if isinstance(raw.get("author"), dict) else {}
    music = raw.get("music", {}) or {}
    challenges = raw.get("challenges", []) or []
    return {
        "id": raw.get("id", ""),
        "description": raw.get("desc", "") or raw.get("description", ""),
        "author": author.get("uniqueId", "") or raw.get("authorMeta", {}).get("name", ""),
        "author_nickname": author.get("nickname", ""),
        "play_count": int(stats.get("playCount", 0) or stats.get("play_count", 0)),
        "like_count": int(stats.get("diggCount", 0) or stats.get("like_count", 0)),
        "comment_count": int(stats.get("commentCount", 0) or stats.get("comment_count", 0)),
        "share_count": int(stats.get("shareCount", 0) or stats.get("share_count", 0)),
        "sound": {
            "id": music.get("id", ""),
            "title": music.get("title", ""),
            "author_name": music.get("authorName", "") or music.get("author", ""),
            "duration": music.get("duration", 0),
            "is_original": music.get("original", False),
        },
        "challenges": [
            {"title": c.get("title", "") if isinstance(c, dict) else str(c)}
            for c in challenges
        ],
        "created_time": raw.get("createTime", 0),
        "url": f"https://www.tiktok.com/@{author.get('uniqueId', 'user')}/video/{raw.get('id', '')}",
        "engagement_rate": _calc_engagement(stats),
    }


def _calc_engagement(stats: dict) -> float:
    plays = int(stats.get("playCount", 1) or 1)
    likes = int(stats.get("diggCount", 0))
    comments = int(stats.get("commentCount", 0))
    shares = int(stats.get("shareCount", 0))
    return round((likes + comments + shares) / max(plays, 1) * 100, 3)
