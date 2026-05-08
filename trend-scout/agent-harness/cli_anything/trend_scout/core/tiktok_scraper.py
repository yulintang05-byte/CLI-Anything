"""TikTok viral trend scraper — hashtags, sounds, challenges, and creator analysis."""

import os
import re
import time
import json
import logging
from datetime import datetime
from typing import Any
from collections import Counter

logger = logging.getLogger(__name__)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# TikTokApi optional import
try:
    from TikTokApi import TikTokApi as _TikTokApi
    TIKTOK_API_AVAILABLE = True
except ImportError:
    TIKTOK_API_AVAILABLE = False

# Pyktok optional import (lightweight scraper)
try:
    import pyktok as pyk
    PYKTOK_AVAILABLE = True
except ImportError:
    PYKTOK_AVAILABLE = False


# Known TikTok trend categories
TIKTOK_CHALLENGE_TAGS = [
    "fyp", "foryou", "foryoupage", "trending", "viral", "tiktoktrend",
    "challenge", "duet", "xyzbca", "blowup", "trend",
]

CONTENT_NICHES = {
    "fitness": ["workout", "gym", "fitness", "gains", "cardio", "bodybuilding", "yoga", "running"],
    "fashion": ["ootd", "fashion", "style", "outfit", "streetwear", "thrift", "aesthetic"],
    "food": ["food", "recipe", "cooking", "foodie", "mukbang", "baking", "restaurant"],
    "beauty": ["makeup", "skincare", "beauty", "glow", "foundation", "tutorial", "glam"],
    "gaming": ["gaming", "game", "twitch", "fortnite", "roblox", "minecraft", "gamer"],
    "finance": ["money", "finance", "investing", "crypto", "stocks", "sidehustle", "rich"],
    "motivation": ["motivation", "mindset", "hustle", "grind", "success", "entrepreneur"],
    "music": ["music", "song", "artist", "newmusic", "rnb", "hiphop", "pop", "lyrics"],
    "comedy": ["funny", "comedy", "humor", "meme", "lol", "prank", "jokes"],
    "travel": ["travel", "wanderlust", "vacation", "explore", "adventure", "destination"],
}


class TikTokScraper:
    """Scrapes TikTok for viral trends, sounds, hashtags, and challenges."""

    def __init__(self, ms_token: str | None = None, session_id: str | None = None):
        self.ms_token = ms_token or os.environ.get("TIKTOK_MS_TOKEN")
        self.session_id = session_id or os.environ.get("TIKTOK_SESSION_ID")
        self._cache: dict[str, Any] = {}
        self._cache_ttl = 1800  # 30 min — TikTok trends move fast
        self._api = None

    def _get_api(self):
        if self._api is None and TIKTOK_API_AVAILABLE:
            self._api = _TikTokApi()
        return self._api

    def _cached(self, key: str, fn, *args, **kwargs):
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["ts"] < self._cache_ttl:
                return entry["data"]
        result = fn(*args, **kwargs)
        self._cache[key] = {"ts": time.time(), "data": result}
        return result

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_trending_hashtags(self, region: str = "US", limit: int = 30) -> list[dict]:
        """Return trending TikTok hashtags with engagement metrics."""
        key = f"tt_hashtags_{region}_{limit}"
        return self._cached(key, self._fetch_trending_hashtags, region, limit)

    def get_trending_sounds(self, region: str = "US", limit: int = 20) -> list[dict]:
        """Return trending TikTok sounds/music used in viral content."""
        key = f"tt_sounds_{region}_{limit}"
        return self._cached(key, self._fetch_trending_sounds, region, limit)

    def get_trending_challenges(self, limit: int = 15) -> list[dict]:
        """Return active TikTok challenges."""
        key = f"tt_challenges_{limit}"
        return self._cached(key, self._fetch_challenges, limit)

    def get_niche_trends(self, niche: str, limit: int = 20) -> dict:
        """Return trending content, hashtags, and sounds for a specific niche."""
        niche_lower = niche.lower()
        niche_tags = CONTENT_NICHES.get(niche_lower, [niche_lower])
        return self._cached(
            f"tt_niche_{niche_lower}_{limit}",
            self._fetch_niche_trends,
            niche_tags,
            niche,
            limit,
        )

    def get_viral_content_patterns(self, region: str = "US") -> dict:
        """Analyze viral TikTok content for posting time, duration, and caption patterns."""
        hashtags = self.get_trending_hashtags(region=region, limit=50)
        sounds = self.get_trending_sounds(region=region, limit=20)
        challenges = self.get_trending_challenges(limit=10)
        return {
            "best_hashtags": hashtags[:15],
            "trending_sounds": sounds[:10],
            "active_challenges": challenges[:5],
            "optimal_video_duration": self._get_optimal_duration(),
            "best_posting_times": self._get_best_posting_times(region),
            "caption_tips": self._get_caption_tips(),
            "hook_formulas": self._get_hook_formulas(),
            "region": region,
            "scraped_at": datetime.utcnow().isoformat(),
        }

    def analyze_creator(self, username: str) -> dict:
        """Analyze a TikTok creator's content strategy."""
        key = f"tt_creator_{username}"
        return self._cached(key, self._fetch_creator_analysis, username)

    def get_sound_for_niche(self, niche: str) -> list[dict]:
        """Suggest trending sounds that work well for a specific niche."""
        all_sounds = self.get_trending_sounds(limit=50)
        niche_keywords = CONTENT_NICHES.get(niche.lower(), [niche.lower()])
        scored = []
        for sound in all_sounds:
            score = sound.get("video_count", 0)
            title_lower = sound.get("title", "").lower()
            for kw in niche_keywords:
                if kw in title_lower:
                    score *= 2
            scored.append({**sound, "niche_score": score})
        scored.sort(key=lambda x: x["niche_score"], reverse=True)
        return scored[:15]

    def get_hashtag_strategy(self, niche: str, follower_count: int = 0) -> dict:
        """Generate a hashtag strategy mix for a niche and account size."""
        niche_trends = self.get_niche_trends(niche=niche, limit=30)
        trending = self.get_trending_hashtags(limit=20)

        niche_tags = [h["hashtag"] for h in niche_trends.get("hashtags", [])[:8]]
        broad_tags = [h["hashtag"] for h in trending[:5]]

        if follower_count < 1000:
            size_tags = ["smallcreator", "growthhack", "newaccount", "smalltiktok"]
        elif follower_count < 10000:
            size_tags = ["midcreator", "contentcreator", "tiktokcreator"]
        else:
            size_tags = ["creator", "contentcreator"]

        strategy = {
            "recommended_hashtags": niche_tags + broad_tags + size_tags + ["fyp", "foryou", "viral"],
            "mix_breakdown": {
                "niche_specific": niche_tags,
                "broad_trending": broad_tags,
                "account_size": size_tags,
                "always_include": ["fyp", "foryou", "viral", "trending"],
            },
            "total_count": len(niche_tags) + len(broad_tags) + len(size_tags) + 4,
            "note": "TikTok recommends 3-5 hashtags; algorithm reads captions so quality > quantity",
            "caption_template": self._build_caption_template(niche, niche_tags[:3]),
        }
        return strategy

    # ------------------------------------------------------------------
    # Internal fetch methods
    # ------------------------------------------------------------------

    def _fetch_trending_hashtags(self, region: str, limit: int) -> list[dict]:
        api = self._get_api()
        if api:
            try:
                import asyncio
                return asyncio.run(self._async_fetch_hashtags(api, limit))
            except Exception as e:
                logger.warning(f"TikTokApi hashtag fetch failed: {e}")

        # Fallback: curated trending hashtags with static data + region context
        return self._static_trending_hashtags(region, limit)

    async def _async_fetch_hashtags(self, api, limit: int) -> list[dict]:
        results = []
        async with api as a:
            async for video in a.trending.videos(count=100):
                for challenge in (video.as_dict.get("challenges") or []):
                    results.append(challenge.get("title", ""))
        counter = Counter(results)
        return [
            {
                "hashtag": f"#{tag}",
                "video_count_estimate": count * 1000,
                "frequency_in_trending": count,
                "trending_score": round(count / max(len(results), 1) * 100, 1),
            }
            for tag, count in counter.most_common(limit)
        ]

    def _fetch_trending_sounds(self, region: str, limit: int) -> list[dict]:
        api = self._get_api()
        if api:
            try:
                import asyncio
                return asyncio.run(self._async_fetch_sounds(api, limit))
            except Exception as e:
                logger.warning(f"TikTokApi sound fetch failed: {e}")
        return self._static_trending_sounds(limit)

    async def _async_fetch_sounds(self, api, limit: int) -> list[dict]:
        sound_counts: dict[str, dict] = {}
        async with api as a:
            async for video in a.trending.videos(count=100):
                music = video.as_dict.get("music", {})
                sid = music.get("id", "")
                if sid:
                    if sid not in sound_counts:
                        sound_counts[sid] = {
                            "id": sid,
                            "title": music.get("title", ""),
                            "artist": music.get("authorName", ""),
                            "duration": music.get("duration", 0),
                            "video_count": 0,
                            "url": f"https://www.tiktok.com/music/{sid}",
                        }
                    sound_counts[sid]["video_count"] += 1
        sounds = sorted(sound_counts.values(), key=lambda x: x["video_count"], reverse=True)
        return sounds[:limit]

    def _fetch_challenges(self, limit: int) -> list[dict]:
        api = self._get_api()
        if api:
            try:
                import asyncio
                return asyncio.run(self._async_fetch_challenges(api, limit))
            except Exception:
                pass
        return self._static_challenges(limit)

    async def _async_fetch_challenges(self, api, limit: int) -> list[dict]:
        challenges: dict[str, int] = {}
        async with api as a:
            async for video in a.trending.videos(count=200):
                for c in (video.as_dict.get("challenges") or []):
                    title = c.get("title", "")
                    if title and "challenge" in title.lower():
                        challenges[title] = challenges.get(title, 0) + 1
        return [
            {"challenge": name, "trend_strength": count, "hashtag": f"#{name}"}
            for name, count in sorted(challenges.items(), key=lambda x: x[1], reverse=True)[:limit]
        ]

    def _fetch_niche_trends(self, niche_tags: list[str], niche: str, limit: int) -> dict:
        api = self._get_api()
        hashtags = []
        videos = []

        if api:
            try:
                import asyncio
                result = asyncio.run(self._async_fetch_niche(api, niche_tags, niche, limit))
                return result
            except Exception as e:
                logger.warning(f"TikTokApi niche fetch failed: {e}")

        return {
            "niche": niche,
            "hashtags": [{"hashtag": f"#{t}", "category": niche} for t in niche_tags[:limit]],
            "sounds": self._static_trending_sounds(10),
            "tip": f"Add TIKTOK_MS_TOKEN env var for live {niche} trend data",
            "scraped_at": datetime.utcnow().isoformat(),
        }

    async def _async_fetch_niche(self, api, niche_tags: list[str], niche: str, limit: int) -> dict:
        tag_videos: list[dict] = []
        async with api as a:
            primary_tag = niche_tags[0] if niche_tags else niche
            hashtag = a.hashtag(name=primary_tag)
            async for video in hashtag.videos(count=limit):
                d = video.as_dict
                tag_videos.append({
                    "id": d.get("id", ""),
                    "description": d.get("desc", "")[:300],
                    "views": d.get("stats", {}).get("playCount", 0),
                    "likes": d.get("stats", {}).get("diggCount", 0),
                    "shares": d.get("stats", {}).get("shareCount", 0),
                    "sound_title": d.get("music", {}).get("title", ""),
                    "sound_artist": d.get("music", {}).get("authorName", ""),
                    "hashtags": [c.get("title", "") for c in (d.get("challenges") or [])],
                    "url": f"https://www.tiktok.com/@{d.get('author', {}).get('uniqueId', '')}/video/{d.get('id', '')}",
                })

        all_tags: Counter = Counter()
        all_sounds: Counter = Counter()
        for v in tag_videos:
            all_tags.update(v.get("hashtags", []))
            s = v.get("sound_title", "")
            if s:
                all_sounds[s] += 1

        return {
            "niche": niche,
            "top_videos": sorted(tag_videos, key=lambda x: x.get("views", 0), reverse=True)[:10],
            "hashtags": [{"hashtag": f"#{t}", "frequency": c} for t, c in all_tags.most_common(20)],
            "trending_sounds": [{"title": s, "video_count": c} for s, c in all_sounds.most_common(10)],
            "scraped_at": datetime.utcnow().isoformat(),
        }

    def _fetch_creator_analysis(self, username: str) -> dict:
        api = self._get_api()
        if api:
            try:
                import asyncio
                return asyncio.run(self._async_creator_analysis(api, username))
            except Exception as e:
                logger.warning(f"Creator analysis failed: {e}")
        return {
            "username": username,
            "error": "Set TIKTOK_MS_TOKEN for live creator analysis",
            "tip": "Get ms_token from TikTok cookies after logging in (inspect Application > Cookies)",
        }

    async def _async_creator_analysis(self, api, username: str) -> dict:
        async with api as a:
            user = a.user(username=username)
            info = await user.info()
            user_data = info.as_dict if hasattr(info, "as_dict") else {}
            videos = []
            async for video in user.videos(count=30):
                d = video.as_dict
                videos.append({
                    "views": d.get("stats", {}).get("playCount", 0),
                    "likes": d.get("stats", {}).get("diggCount", 0),
                    "shares": d.get("stats", {}).get("shareCount", 0),
                    "duration": d.get("video", {}).get("duration", 0),
                    "hashtags": [c.get("title", "") for c in (d.get("challenges") or [])],
                    "sound": d.get("music", {}).get("title", ""),
                })

        views = [v["views"] for v in videos]
        durations = [v["duration"] for v in videos if v["duration"] > 0]
        all_tags: Counter = Counter()
        for v in videos:
            all_tags.update(v["hashtags"])

        return {
            "username": username,
            "follower_count": user_data.get("stats", {}).get("followerCount", 0),
            "total_likes": user_data.get("stats", {}).get("heartCount", 0),
            "avg_views": int(sum(views) / len(views)) if views else 0,
            "avg_duration_seconds": int(sum(durations) / len(durations)) if durations else 0,
            "top_hashtags": [t for t, _ in all_tags.most_common(10)],
            "engagement_rate": self._calc_engagement(videos),
            "posting_pattern": self._estimate_posting_frequency(videos),
            "analyzed_at": datetime.utcnow().isoformat(),
        }

    # ------------------------------------------------------------------
    # Static fallback data (when no API key available)
    # ------------------------------------------------------------------

    def _static_trending_hashtags(self, region: str, limit: int) -> list[dict]:
        """Curated always-relevant TikTok hashtags — updated to 2025 trends."""
        base = [
            {"hashtag": "#fyp", "video_count_estimate": 50_000_000_000, "trending_score": 100},
            {"hashtag": "#foryou", "video_count_estimate": 40_000_000_000, "trending_score": 98},
            {"hashtag": "#foryoupage", "video_count_estimate": 30_000_000_000, "trending_score": 97},
            {"hashtag": "#viral", "video_count_estimate": 20_000_000_000, "trending_score": 95},
            {"hashtag": "#trending", "video_count_estimate": 10_000_000_000, "trending_score": 92},
            {"hashtag": "#tiktok", "video_count_estimate": 8_000_000_000, "trending_score": 90},
            {"hashtag": "#xyzbca", "video_count_estimate": 5_000_000_000, "trending_score": 85},
            {"hashtag": "#blowup", "video_count_estimate": 2_000_000_000, "trending_score": 80},
            {"hashtag": "#makemefamous", "video_count_estimate": 1_500_000_000, "trending_score": 75},
            {"hashtag": "#realtalk", "video_count_estimate": 1_200_000_000, "trending_score": 72},
            {"hashtag": "#contentcreator", "video_count_estimate": 1_000_000_000, "trending_score": 70},
            {"hashtag": "#ai", "video_count_estimate": 900_000_000, "trending_score": 68},
            {"hashtag": "#motivation", "video_count_estimate": 800_000_000, "trending_score": 65},
            {"hashtag": "#smallbusiness", "video_count_estimate": 700_000_000, "trending_score": 63},
            {"hashtag": "#entrepreneur", "video_count_estimate": 650_000_000, "trending_score": 60},
            {"hashtag": "#sidehustle", "video_count_estimate": 600_000_000, "trending_score": 58},
            {"hashtag": "#storytime", "video_count_estimate": 550_000_000, "trending_score": 55},
            {"hashtag": "#pov", "video_count_estimate": 500_000_000, "trending_score": 53},
            {"hashtag": "#grwm", "video_count_estimate": 480_000_000, "trending_score": 50},
            {"hashtag": "#dayinmylife", "video_count_estimate": 450_000_000, "trending_score": 48},
            {"hashtag": "#aesthetic", "video_count_estimate": 420_000_000, "trending_score": 45},
            {"hashtag": "#vlog", "video_count_estimate": 400_000_000, "trending_score": 43},
            {"hashtag": "#tips", "video_count_estimate": 380_000_000, "trending_score": 40},
            {"hashtag": "#tutorial", "video_count_estimate": 360_000_000, "trending_score": 38},
            {"hashtag": "#howto", "video_count_estimate": 340_000_000, "trending_score": 35},
            {"hashtag": "#relatable", "video_count_estimate": 320_000_000, "trending_score": 33},
            {"hashtag": "#mindset", "video_count_estimate": 300_000_000, "trending_score": 30},
            {"hashtag": "#facts", "video_count_estimate": 280_000_000, "trending_score": 28},
            {"hashtag": "#lifehacks", "video_count_estimate": 260_000_000, "trending_score": 25},
            {"hashtag": "#tipsandtricks", "video_count_estimate": 240_000_000, "trending_score": 23},
        ]
        return base[:limit]

    def _static_trending_sounds(self, limit: int) -> list[dict]:
        return [
            {"title": "original sound - trending", "artist": "various", "video_count": 5_000_000, "tip": "Use TikTok app > Discover > Sounds for live trending sounds"},
            {"title": "Flowers - Miley Cyrus", "artist": "Miley Cyrus", "video_count": 2_000_000},
            {"title": "Rich Flex - Drake & 21 Savage", "artist": "Drake", "video_count": 1_800_000},
            {"title": "As It Was - Harry Styles", "artist": "Harry Styles", "video_count": 1_500_000},
            {"title": "Espresso - Sabrina Carpenter", "artist": "Sabrina Carpenter", "video_count": 1_200_000},
            {"title": "Calm Down - Rema", "artist": "Rema", "video_count": 1_000_000},
            {"title": "Anti-Hero - Taylor Swift", "artist": "Taylor Swift", "video_count": 900_000},
            {"title": "Unholy - Sam Smith", "artist": "Sam Smith", "video_count": 850_000},
            {"title": "Creepin - Metro Boomin", "artist": "Metro Boomin", "video_count": 800_000},
            {"title": "Golden Hour - JVKE", "artist": "JVKE", "video_count": 750_000},
        ][:limit]

    def _static_challenges(self, limit: int) -> list[dict]:
        return [
            {"challenge": "whatimlistening", "trend_strength": 9, "hashtag": "#whatimlistening"},
            {"challenge": "dayinmylife", "trend_strength": 8, "hashtag": "#dayinmylife"},
            {"challenge": "grwm", "trend_strength": 8, "hashtag": "#grwm"},
            {"challenge": "transformationchallenge", "trend_strength": 7, "hashtag": "#transformationchallenge"},
            {"challenge": "tellmewithout", "trend_strength": 7, "hashtag": "#tellmewithout"},
        ][:limit]

    # ------------------------------------------------------------------
    # Strategy helpers
    # ------------------------------------------------------------------

    def _get_optimal_duration(self) -> dict:
        return {
            "sweet_spot_seconds": "7-15",
            "still_good_seconds": "15-30",
            "longer_format_seconds": "60-180",
            "note": "Algorithm favors full watch-through — shorter is safer unless content demands length",
            "hook_window_seconds": "0-3",
        }

    def _get_best_posting_times(self, region: str) -> dict:
        times = {
            "US": ["6-9 AM EST", "12-2 PM EST", "7-10 PM EST"],
            "GB": ["7-9 AM GMT", "12-1 PM GMT", "7-9 PM GMT"],
            "AU": ["7-9 AM AEST", "12-2 PM AEST", "6-9 PM AEST"],
        }
        return {
            "best_windows": times.get(region, times["US"]),
            "best_days": ["Tuesday", "Thursday", "Friday", "Saturday"],
            "frequency_recommendation": "1-4 posts/day for growth",
            "note": "Post when YOUR audience is active — check TikTok Analytics after 1k followers",
        }

    def _get_caption_tips(self) -> list[str]:
        return [
            "Start with a hook question: 'Did you know...' or 'This changed my life'",
            "Use 3-5 hashtags max (quality > quantity)",
            "Add a call-to-action: 'Save this for later', 'Follow for more', 'Comment your answer'",
            "Keep captions under 150 characters — TikTok truncates at ~100",
            "Emojis increase engagement — use 2-3 relevant ones",
            "Mention the hook from your video in the caption",
        ]

    def _get_hook_formulas(self) -> list[str]:
        return [
            "POV: [relatable situation]",
            "Things [niche audience] will understand",
            "I tried [thing] so you don't have to",
            "Tell me you're a [type] without telling me",
            "The [thing] that [result] in [timeframe]",
            "Nobody talks about this but [surprising fact]",
            "Wait for it... [unexpected twist at end]",
            "This [product/hack/tip] changed my [life/routine/business]",
            "Story time: [engaging first line]",
            "[Number] things I wish I knew before [activity]",
        ]

    def _build_caption_template(self, niche: str, top_tags: list[str]) -> str:
        tag_str = " ".join(f"#{t}" for t in top_tags)
        return f"[Hook related to {niche}] — save this! ✨ {tag_str} #fyp #viral"

    def _calc_engagement(self, videos: list[dict]) -> str:
        if not videos:
            return "0%"
        total_views = sum(v.get("views", 0) for v in videos)
        total_likes = sum(v.get("likes", 0) for v in videos)
        if total_views == 0:
            return "0%"
        rate = (total_likes / total_views) * 100
        return f"{rate:.2f}%"

    def _estimate_posting_frequency(self, videos: list[dict]) -> str:
        return f"Analyzed {len(videos)} recent videos"
