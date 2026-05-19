"""TikTok trending data via TikTokApi (unofficial) + Research API fallback."""

import asyncio
import json
import re
from datetime import datetime
from typing import Any

# TikTok niche hashtag seeds — used to discover related trending content
NICHE_SEEDS: dict[str, list[str]] = {
    "fitness": ["#gym", "#workout", "#fitness", "#gains", "#bodybuilding"],
    "motivation": ["#motivation", "#mindset", "#success", "#grindset", "#hustle"],
    "beauty": ["#makeup", "#skincare", "#beauty", "#glam", "#makeuptutorial"],
    "food": ["#foodtok", "#recipe", "#cooking", "#foodie", "#mukbang"],
    "gaming": ["#gaming", "#gamer", "#twitch", "#fps", "#valorant"],
    "fashion": ["#fashion", "#ootd", "#style", "#streetwear", "#fits"],
    "finance": ["#moneytok", "#investing", "#stocks", "#crypto", "#personalfinance"],
    "comedy": ["#funny", "#comedy", "#meme", "#viral", "#foryou"],
    "cars": ["#carsoftiktok", "#car", "#supercar", "#drift", "#automotive"],
    "anime": ["#anime", "#animeedit", "#weeb", "#otaku", "#animefyp"],
}


class TikTokTrends:
    """Fetch trending data from TikTok.

    Two modes:
    - unofficial (default): Uses TikTokApi (Playwright-based). Requires
      `playwright install chromium` and may need cookies.
    - research_api: Uses TikTok Research API (approved accounts only).
      Set research_api_token to enable.
    """

    def __init__(self, ms_token: str | None = None, research_api_token: str | None = None):
        self.ms_token = ms_token
        self.research_api_token = research_api_token

    # ------------------------------------------------------------------
    # Trending hashtags
    # ------------------------------------------------------------------

    def get_trending_hashtags(self, limit: int = 30) -> list[dict]:
        """Return trending hashtags from TikTok discover page."""
        try:
            return asyncio.run(self._fetch_trending_hashtags(limit))
        except Exception as e:
            return self._fallback_trending_hashtags(str(e))

    async def _fetch_trending_hashtags(self, limit: int) -> list[dict]:
        from TikTokApi import TikTokApi
        results = []
        async with TikTokApi() as api:
            if self.ms_token:
                await api.create_sessions(ms_tokens=[self.ms_token], num_sessions=1, sleep_after=3)
            else:
                await api.create_sessions(num_sessions=1, sleep_after=3, headless=True)

            async for trend in api.trending.videos(count=limit):
                info = trend.as_dict
                desc = info.get("desc", "")
                tags = re.findall(r"#\w+", desc.lower())
                for tag in tags:
                    existing = next((r for r in results if r["hashtag"] == tag), None)
                    if existing:
                        existing["frequency"] += 1
                        existing["total_views"] += info.get("stats", {}).get("playCount", 0)
                    else:
                        results.append({
                            "hashtag": tag,
                            "frequency": 1,
                            "total_views": info.get("stats", {}).get("playCount", 0),
                        })

        results.sort(key=lambda x: x["frequency"], reverse=True)
        return results[:limit]

    def _fallback_trending_hashtags(self, error: str) -> list[dict]:
        """Return a curated list of currently known viral TikTok hashtags when API fails."""
        return [
            {"hashtag": "#fyp", "frequency": 0, "note": f"fallback (API error: {error[:60]})"},
            {"hashtag": "#foryou", "frequency": 0, "note": "fallback"},
            {"hashtag": "#foryoupage", "frequency": 0, "note": "fallback"},
            {"hashtag": "#viral", "frequency": 0, "note": "fallback"},
            {"hashtag": "#trending", "frequency": 0, "note": "fallback"},
            {"hashtag": "#tiktok", "frequency": 0, "note": "fallback"},
            {"hashtag": "#xyzbca", "frequency": 0, "note": "fallback"},
            {"hashtag": "#blowthisup", "frequency": 0, "note": "fallback"},
        ]

    # ------------------------------------------------------------------
    # Trending sounds / music
    # ------------------------------------------------------------------

    def get_trending_sounds(self, limit: int = 30) -> list[dict]:
        """Return trending sounds extracted from trending videos."""
        try:
            return asyncio.run(self._fetch_trending_sounds(limit))
        except Exception as e:
            return [{"error": str(e), "note": "Install playwright: playwright install chromium"}]

    async def _fetch_trending_sounds(self, limit: int) -> list[dict]:
        from TikTokApi import TikTokApi
        sound_freq: dict[str, dict] = {}

        async with TikTokApi() as api:
            if self.ms_token:
                await api.create_sessions(ms_tokens=[self.ms_token], num_sessions=1, sleep_after=3)
            else:
                await api.create_sessions(num_sessions=1, sleep_after=3, headless=True)

            async for video in api.trending.videos(count=min(limit * 3, 200)):
                info = video.as_dict
                music = info.get("music", {})
                sound_id = str(music.get("id", ""))
                if not sound_id:
                    continue
                if sound_id in sound_freq:
                    sound_freq[sound_id]["frequency"] += 1
                    sound_freq[sound_id]["total_plays"] += info.get("stats", {}).get("playCount", 0)
                else:
                    sound_freq[sound_id] = {
                        "sound_id": sound_id,
                        "title": music.get("title", "Unknown"),
                        "author": music.get("authorName", "Unknown"),
                        "duration": music.get("duration", 0),
                        "original": music.get("original", False),
                        "frequency": 1,
                        "total_plays": info.get("stats", {}).get("playCount", 0),
                    }

        ranked = sorted(sound_freq.values(), key=lambda x: x["frequency"], reverse=True)
        return ranked[:limit]

    # ------------------------------------------------------------------
    # Niche trending content
    # ------------------------------------------------------------------

    def get_niche_trends(self, niche: str, limit: int = 20) -> list[dict]:
        """Return trending videos for a specific niche."""
        try:
            return asyncio.run(self._fetch_niche_trends(niche, limit))
        except Exception as e:
            seeds = NICHE_SEEDS.get(niche.lower(), [f"#{niche}"])
            return [{"error": str(e), "suggested_hashtags": seeds}]

    async def _fetch_niche_trends(self, niche: str, limit: int) -> list[dict]:
        from TikTokApi import TikTokApi
        seeds = NICHE_SEEDS.get(niche.lower(), [f"#{niche}"])
        results = []

        async with TikTokApi() as api:
            if self.ms_token:
                await api.create_sessions(ms_tokens=[self.ms_token], num_sessions=1, sleep_after=3)
            else:
                await api.create_sessions(num_sessions=1, sleep_after=3, headless=True)

            for hashtag_str in seeds[:3]:
                tag_name = hashtag_str.lstrip("#")
                try:
                    tag = api.hashtag(name=tag_name)
                    async for video in tag.videos(count=limit // len(seeds[:3]) + 1):
                        info = video.as_dict
                        results.append({
                            "id": info.get("id"),
                            "desc": info.get("desc", "")[:200],
                            "author": info.get("author", {}).get("uniqueId", ""),
                            "plays": info.get("stats", {}).get("playCount", 0),
                            "likes": info.get("stats", {}).get("diggCount", 0),
                            "comments": info.get("stats", {}).get("commentCount", 0),
                            "shares": info.get("stats", {}).get("shareCount", 0),
                            "music": info.get("music", {}).get("title", ""),
                            "hashtag_used": hashtag_str,
                        })
                except Exception:
                    continue

        results.sort(key=lambda x: x["plays"], reverse=True)
        return results[:limit]

    # ------------------------------------------------------------------
    # Hashtags for a niche
    # ------------------------------------------------------------------

    def get_niche_hashtags(self, niche: str) -> list[str]:
        """Return seed + expanded hashtag list for a niche."""
        base = NICHE_SEEDS.get(niche.lower(), [f"#{niche}"])
        universal = ["#fyp", "#foryou", "#viral", "#trending", "#foryoupage"]
        return base + universal

    # ------------------------------------------------------------------
    # Research API (approved accounts)
    # ------------------------------------------------------------------

    def get_research_api_trends(self, query: str, days: int = 7) -> dict:
        """Use TikTok Research API for trend data (requires approved token)."""
        if not self.research_api_token:
            return {"error": "research_api_token not set. Apply at developers.tiktok.com"}

        import requests
        headers = {
            "Authorization": f"Bearer {self.research_api_token}",
            "Content-Type": "application/json",
        }
        # TikTok Research API — video query endpoint
        payload = {
            "query": {
                "and": [{"operation": "IN", "field_name": "keyword", "field_values": [query]}]
            },
            "start_date": self._days_ago(days),
            "end_date": self._today(),
            "max_count": 100,
            "fields": "id,video_description,like_count,comment_count,share_count,view_count,hashtag_names,music_id,voice_to_text",
        }
        url = "https://open.tiktokapis.com/v2/research/video/query/"
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def _days_ago(n: int) -> str:
        from datetime import timedelta
        return (datetime.utcnow() - timedelta(days=n)).strftime("%Y%m%d")

    @staticmethod
    def _today() -> str:
        return datetime.utcnow().strftime("%Y%m%d")

    # ------------------------------------------------------------------
    # Full trend report
    # ------------------------------------------------------------------

    def trend_report(self, niche: str | None = None) -> dict:
        report: dict[str, Any] = {
            "generated_at": datetime.utcnow().isoformat(),
            "platform": "tiktok",
        }
        report["trending_hashtags"] = self.get_trending_hashtags(limit=30)
        report["trending_sounds"] = self.get_trending_sounds(limit=20)
        if niche:
            report["niche"] = niche
            report["niche_hashtags"] = self.get_niche_hashtags(niche)
            report["niche_videos"] = self.get_niche_trends(niche, limit=20)
        return report
