"""Cross-platform trend analyzer: aggregates YouTube + TikTok data into actionable insights."""

import json
import re
from datetime import datetime
from collections import Counter
from typing import Any

from .youtube_scraper import YouTubeScraper
from .tiktok_scraper import TikTokScraper


class TrendAnalyzer:
    """Aggregates YouTube and TikTok trends into unified, actionable reports."""

    def __init__(self, youtube_api_key: str | None = None, tiktok_ms_token: str | None = None):
        self.yt = YouTubeScraper(api_key=youtube_api_key)
        self.tt = TikTokScraper(ms_token=tiktok_ms_token)

    # ------------------------------------------------------------------
    # Core analysis
    # ------------------------------------------------------------------

    def get_unified_trends(self, niche: str = "general", region: str = "US") -> dict:
        """Return a unified trend report merging YouTube + TikTok data."""
        yt_videos = self.yt.get_trending_videos(region=region, max_results=30)
        yt_hashtags = self.yt.get_trending_hashtags(region=region, limit=20)
        yt_music = self.yt.get_trending_music(region=region, limit=10)

        tt_hashtags = self.tt.get_trending_hashtags(region=region, limit=20)
        tt_sounds = self.tt.get_trending_sounds(region=region, limit=10)
        tt_patterns = self.tt.get_viral_content_patterns(region=region)

        cross_platform = self._find_cross_platform_trends(yt_hashtags, tt_hashtags)

        return {
            "niche": niche,
            "region": region,
            "cross_platform_trends": cross_platform,
            "youtube": {
                "trending_videos": yt_videos[:10],
                "top_hashtags": yt_hashtags[:10],
                "trending_music": yt_music[:5],
                "viral_topics": self.yt.get_viral_topics(region=region)[:10],
            },
            "tiktok": {
                "top_hashtags": tt_hashtags[:10],
                "trending_sounds": tt_sounds[:5],
                "active_challenges": tt_patterns.get("active_challenges", [])[:5],
                "hook_formulas": tt_patterns.get("hook_formulas", [])[:5],
                "best_posting_times": tt_patterns.get("best_posting_times", {}),
            },
            "content_opportunities": self._identify_opportunities(yt_videos, tt_hashtags, niche),
            "generated_at": datetime.utcnow().isoformat(),
        }

    def get_niche_deep_dive(self, niche: str, region: str = "US") -> dict:
        """Deep analysis of a specific content niche across both platforms."""
        yt_niche = self.yt.get_trending_sounds_for_content(niche=niche, region=region)
        tt_niche = self.tt.get_niche_trends(niche=niche, limit=25)
        tt_sounds = self.tt.get_sound_for_niche(niche=niche)
        tt_hashtag_strategy = self.tt.get_hashtag_strategy(niche=niche)

        return {
            "niche": niche,
            "region": region,
            "youtube": {
                "trending_sounds": yt_niche.get("trending_music", [])[:10],
                "niche_videos": yt_niche.get("niche_relevant_videos", [])[:8],
            },
            "tiktok": {
                "niche_hashtags": tt_niche.get("hashtags", [])[:15],
                "top_niche_videos": tt_niche.get("top_videos", [])[:5],
                "best_sounds_for_niche": tt_sounds[:8],
                "hashtag_strategy": tt_hashtag_strategy,
            },
            "content_ideas": self._generate_content_ideas(niche),
            "posting_strategy": self._build_posting_strategy(niche),
            "generated_at": datetime.utcnow().isoformat(),
        }

    def get_music_trends(self, region: str = "US") -> dict:
        """Aggregate trending music/sounds from YouTube and TikTok."""
        yt_music = self.yt.get_trending_music(region=region, limit=20)
        tt_sounds = self.tt.get_trending_sounds(region=region, limit=20)

        return {
            "region": region,
            "youtube_trending_music": yt_music[:15],
            "tiktok_trending_sounds": tt_sounds[:15],
            "cross_platform_hits": self._find_music_crossover(yt_music, tt_sounds),
            "tip": "Use sounds trending on TikTok in YouTube Shorts for cross-platform boost",
            "generated_at": datetime.utcnow().isoformat(),
        }

    def get_hashtag_master_list(self, niche: str, region: str = "US", follower_count: int = 0) -> dict:
        """Generate a complete hashtag strategy for both platforms."""
        yt_hashtags = self.yt.get_trending_hashtags(region=region, limit=30)
        tt_strategy = self.tt.get_hashtag_strategy(niche=niche, follower_count=follower_count)
        tt_niche = self.tt.get_niche_trends(niche=niche, limit=20)

        yt_tags = [h["hashtag"] for h in yt_hashtags[:10]]
        tt_tags = tt_strategy.get("recommended_hashtags", [])[:15]

        return {
            "niche": niche,
            "follower_tier": self._get_follower_tier(follower_count),
            "youtube_hashtags": {
                "recommended": yt_tags,
                "note": "YouTube: 3-5 hashtags in title/description for best reach",
            },
            "tiktok_hashtags": {
                "recommended": tt_tags,
                "strategy": tt_strategy.get("mix_breakdown", {}),
                "caption_template": tt_strategy.get("caption_template", ""),
                "note": "TikTok: 3-5 hashtags, algorithm reads full captions",
            },
            "universal_tags": self._get_universal_tags(niche),
            "niche_specific": [h.get("hashtag", "") for h in tt_niche.get("hashtags", [])[:10]],
            "generated_at": datetime.utcnow().isoformat(),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _find_cross_platform_trends(self, yt_tags: list[dict], tt_tags: list[dict]) -> list[dict]:
        yt_set = {h.get("hashtag", "").lstrip("#").lower() for h in yt_tags}
        tt_set = {h.get("hashtag", "").lstrip("#").lower() for h in tt_tags}
        overlap = yt_set & tt_set
        if not overlap:
            return [{"note": "No direct overlap found — cross-post by adapting format per platform"}]
        return [{"hashtag": f"#{t}", "platforms": ["YouTube", "TikTok"], "strength": "HIGH"} for t in overlap]

    def _find_music_crossover(self, yt_music: list[dict], tt_sounds: list[dict]) -> list[dict]:
        yt_titles = {m.get("title", "").lower() for m in yt_music}
        crossover = []
        for s in tt_sounds:
            title = s.get("title", "").lower()
            for yt_title in yt_titles:
                artist = s.get("artist", "").lower()
                if artist and artist in yt_title or title in yt_title:
                    crossover.append({
                        "sound": s.get("title", ""),
                        "artist": s.get("artist", ""),
                        "platforms": ["YouTube", "TikTok"],
                        "tip": "This sound is trending on both — high opportunity",
                    })
                    break
        return crossover[:5]

    def _identify_opportunities(self, yt_videos: list[dict], tt_hashtags: list[dict], niche: str) -> list[dict]:
        opportunities = []
        niche_lower = niche.lower()

        high_view_videos = sorted(yt_videos, key=lambda x: x.get("views", 0), reverse=True)[:5]
        for v in high_view_videos:
            if v.get("views", 0) > 1_000_000:
                opportunities.append({
                    "type": "YouTube Trending",
                    "title": v.get("title", ""),
                    "views": v.get("views", 0),
                    "action": f"Create a {niche} perspective on this topic",
                    "hashtags": v.get("hashtags", [])[:5],
                })

        top_tt_tags = [h.get("hashtag", "") for h in tt_hashtags[:5]]
        if top_tt_tags:
            opportunities.append({
                "type": "TikTok Hashtag Opportunity",
                "tags": top_tt_tags,
                "action": f"Post {niche} content using these trending tags in next 24h",
                "urgency": "HIGH — TikTok trends peak and fade fast",
            })

        return opportunities

    def _generate_content_ideas(self, niche: str) -> list[dict]:
        templates = {
            "fitness": [
                {"title": "5-minute morning routine that changed my body", "format": "Tutorial"},
                {"title": "What I eat in a day (realistic)", "format": "Day-in-life"},
                {"title": "Gym mistakes 90% of people make", "format": "Educational"},
            ],
            "fashion": [
                {"title": "Styling the same piece 5 different ways", "format": "Outfit ideas"},
                {"title": "Thrift haul under $20 (designer look)", "format": "Haul"},
                {"title": "Outfit formula that works every time", "format": "Tips"},
            ],
            "finance": [
                {"title": "How I made my first $1k online (step by step)", "format": "Story"},
                {"title": "Things I stopped buying to save $500/month", "format": "Tips"},
                {"title": "Investing explained in 60 seconds", "format": "Educational"},
            ],
            "food": [
                {"title": "5-ingredient recipe that tastes like takeout", "format": "Recipe"},
                {"title": "What I actually eat in a week (budget edition)", "format": "Day-in-life"},
                {"title": "Restaurant hack nobody tells you about", "format": "Tips"},
            ],
            "beauty": [
                {"title": "$10 drugstore dupe for [luxury product]", "format": "Review"},
                {"title": "Skincare routine that cleared my skin in 30 days", "format": "Before/After"},
                {"title": "Makeup mistakes that are aging you", "format": "Educational"},
            ],
        }
        niche_ideas = templates.get(niche.lower(), [])
        generic = [
            {"title": f"Things {niche} beginners need to hear", "format": "Educational"},
            {"title": f"Day in the life of a {niche} creator", "format": "Vlog"},
            {"title": f"Hot take: [controversial {niche} opinion]", "format": "Opinion"},
            {"title": f"I tried [trending {niche} trend] for 30 days", "format": "Challenge"},
            {"title": f"The {niche} tip that got me [result]", "format": "Tips"},
        ]
        return (niche_ideas + generic)[:8]

    def _build_posting_strategy(self, niche: str) -> dict:
        return {
            "frequency": {
                "TikTok": "1-3 posts/day (algorithm rewards consistency)",
                "YouTube_Shorts": "1 short/day + 1 long-form/week",
                "Instagram_Reels": "1-2 reels/day",
            },
            "content_mix": {
                "educational": "40% — builds authority",
                "entertaining": "30% — drives shares",
                "personal": "20% — builds connection",
                "promotional": "10% — monetization",
            },
            "repurposing_workflow": [
                "1. Record 1 video idea with hook + value + CTA",
                "2. Post raw cut on TikTok first (fastest feedback)",
                "3. Add captions + thumbnail → YouTube Shorts",
                "4. Crop to 9:16 + add music → Instagram Reels",
                "5. Screenshot best comments → Stories content",
            ],
            "niche": niche,
        }

    def _get_follower_tier(self, count: int) -> str:
        if count < 1000:
            return "nano (0-1K)"
        elif count < 10_000:
            return "micro (1K-10K)"
        elif count < 100_000:
            return "mid-tier (10K-100K)"
        elif count < 1_000_000:
            return "macro (100K-1M)"
        else:
            return "mega (1M+)"

    def _get_universal_tags(self, niche: str) -> list[str]:
        universal = ["#fyp", "#foryou", "#viral", "#trending"]
        niche_map = {
            "fitness": ["#fitness", "#gym", "#workout", "#health"],
            "fashion": ["#fashion", "#ootd", "#style", "#outfit"],
            "food": ["#food", "#recipe", "#foodie", "#cooking"],
            "beauty": ["#beauty", "#makeup", "#skincare", "#glam"],
            "finance": ["#money", "#finance", "#investing", "#entrepreneur"],
            "gaming": ["#gaming", "#gamer", "#gameplay", "#streamer"],
            "travel": ["#travel", "#wanderlust", "#explore", "#adventure"],
            "music": ["#music", "#newmusic", "#artist", "#song"],
        }
        return universal + niche_map.get(niche.lower(), [f"#{niche}"])
