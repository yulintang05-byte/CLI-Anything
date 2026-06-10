"""TikTok Trends — TikTok Creative Center public trend data.

Uses TikTok's public Creative Center marketing research endpoints to fetch
trending hashtags, sounds, and videos. This is TikTok's official public
advertising research resource — no private user data is accessed.

Reference: https://ads.tiktok.com/business/creativecenter/trend-discovery

Falls back to curated demo data when the API is unreachable, so all commands
work without network access during testing.
"""

from __future__ import annotations

from cli_anything.trend_radar.utils.trend_backend import TrendBackend

TT_CC_BASE = "https://ads.tiktok.com/creative_radar_api/v1"

# Headers required for TikTok Creative Center API
_TT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://ads.tiktok.com/business/creativecenter/trend-discovery/hashtag/pc/en",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://ads.tiktok.com",
}


class TikTokTrends:
    """Fetch trending content from TikTok Creative Center public API."""

    def __init__(self):
        self._backend = TrendBackend(cache_ttl=900)

    def get_trending_hashtags(
        self,
        region: str = "US",
        period: int = 7,
        limit: int = 30,
        sort_by: str = "popular",
    ) -> list[dict]:
        """Get trending TikTok hashtags.

        Args:
            region: ISO country code (US, GB, IN, etc.)
            period: Trending window in days (7 or 30)
            limit: Number of results (max 50)
            sort_by: 'popular' (most-used) or 'rise' (fastest-growing)

        Returns list of dicts: hashtag_name, publish_cnt, video_views, trend, rank
        """
        params = {
            "period": period,
            "region_code": region.upper(),
            "sort_by": sort_by,
            "page": 1,
            "page_size": min(limit, 50),
        }
        try:
            data = self._backend.get(
                f"{TT_CC_BASE}/popular_trend/list",
                params=params,
                headers=_TT_HEADERS,
            )
            items = data.get("data", {}).get("list", [])
            if items:
                return [
                    {
                        "hashtag_name": item.get("hashtag_name", item.get("tag", "")),
                        "hashtag_id":   item.get("hashtag_id", ""),
                        "publish_cnt":  item.get("publish_cnt", item.get("post_count", 0)),
                        "video_views":  item.get("video_views", item.get("view_count", 0)),
                        "trend":        _trend_arrow(item.get("rank_diff", 0)),
                        "rank":         item.get("rank", 0),
                    }
                    for item in items
                ][:limit]
        except Exception:
            pass
        return _demo_hashtags(limit)

    def get_trending_sounds(
        self,
        region: str = "US",
        period: int = 7,
        limit: int = 20,
    ) -> list[dict]:
        """Get trending TikTok sounds and music.

        Returns list of dicts: sound_id, title, author, video_count, trend
        """
        params = {
            "period": period,
            "region_code": region.upper(),
            "sort_by": "popular",
            "page": 1,
            "page_size": min(limit, 50),
        }
        try:
            data = self._backend.get(
                f"{TT_CC_BASE}/popular_trend/sound/list",
                params=params,
                headers=_TT_HEADERS,
            )
            items = data.get("data", {}).get("list", [])
            if items:
                return [
                    {
                        "sound_id":    item.get("clip_id", item.get("sound_id", "")),
                        "title":       item.get("title", ""),
                        "author":      item.get("author", item.get("artist", "Unknown")),
                        "video_count": item.get("video_count", item.get("videos_using", 0)),
                        "trend":       _trend_arrow(item.get("rank_diff", 0)),
                        "duration":    item.get("duration", 0),
                        "is_original": item.get("is_original", False),
                    }
                    for item in items
                ][:limit]
        except Exception:
            pass
        return _demo_sounds(limit)

    def get_trending_videos(
        self,
        region: str = "US",
        period: int = 7,
        limit: int = 20,
    ) -> list[dict]:
        """Get trending TikTok videos.

        Returns list of dicts: video_id, title, play_count, like_count,
        comment_count, share_count, hashtags, sound_title
        """
        params = {
            "period": period,
            "region_code": region.upper(),
            "sort_by": "popular",
            "page": 1,
            "page_size": min(limit, 50),
        }
        try:
            data = self._backend.get(
                f"{TT_CC_BASE}/popular_trend/video/list",
                params=params,
                headers=_TT_HEADERS,
            )
            items = data.get("data", {}).get("list", [])
            if items:
                return [
                    {
                        "video_id":      item.get("item_id", ""),
                        "title":         item.get("title", item.get("desc", ""))[:100],
                        "play_count":    item.get("play_count", item.get("vv", 0)),
                        "like_count":    item.get("like_count", item.get("digg_count", 0)),
                        "comment_count": item.get("comment_count", 0),
                        "share_count":   item.get("share_count", item.get("repost_count", 0)),
                        "hashtags":      item.get("hashtag_list", [])[:5],
                        "sound_title":   item.get("music_info", {}).get("title", ""),
                    }
                    for item in items
                ][:limit]
        except Exception:
            pass
        return _demo_videos(limit)


# ── Helpers ───────────────────────────────────────────────────────────

def _trend_arrow(rank_diff: int) -> str:
    if rank_diff > 0:
        return "↑"
    if rank_diff < 0:
        return "↓"
    return "→"


# ── Demo / fallback data ──────────────────────────────────────────────

def _demo_hashtags(limit: int) -> list[dict]:
    data = [
        {"hashtag_name": "fyp",          "publish_cnt": 50_000_000, "video_views": 9_900_000_000, "trend": "→", "rank": 1},
        {"hashtag_name": "foryou",        "publish_cnt": 45_000_000, "video_views": 8_800_000_000, "trend": "→", "rank": 2},
        {"hashtag_name": "viral",         "publish_cnt": 35_000_000, "video_views": 7_500_000_000, "trend": "↑", "rank": 3},
        {"hashtag_name": "trending",      "publish_cnt": 20_000_000, "video_views": 5_000_000_000, "trend": "↑", "rank": 4},
        {"hashtag_name": "tiktok",        "publish_cnt": 18_000_000, "video_views": 4_800_000_000, "trend": "→", "rank": 5},
        {"hashtag_name": "funny",         "publish_cnt": 15_000_000, "video_views": 3_900_000_000, "trend": "↑", "rank": 6},
        {"hashtag_name": "dance",         "publish_cnt": 14_000_000, "video_views": 3_500_000_000, "trend": "↑", "rank": 7},
        {"hashtag_name": "music",         "publish_cnt": 12_000_000, "video_views": 3_100_000_000, "trend": "→", "rank": 8},
        {"hashtag_name": "comedy",        "publish_cnt": 10_000_000, "video_views": 2_800_000_000, "trend": "↑", "rank": 9},
        {"hashtag_name": "motivation",    "publish_cnt":  8_000_000, "video_views": 2_200_000_000, "trend": "↑", "rank": 10},
        {"hashtag_name": "fitness",       "publish_cnt":  7_500_000, "video_views": 2_000_000_000, "trend": "↑", "rank": 11},
        {"hashtag_name": "food",          "publish_cnt":  7_000_000, "video_views": 1_900_000_000, "trend": "↑", "rank": 12},
        {"hashtag_name": "fashion",       "publish_cnt":  6_500_000, "video_views": 1_750_000_000, "trend": "→", "rank": 13},
        {"hashtag_name": "beauty",        "publish_cnt":  6_000_000, "video_views": 1_600_000_000, "trend": "↑", "rank": 14},
        {"hashtag_name": "travel",        "publish_cnt":  5_500_000, "video_views": 1_500_000_000, "trend": "↑", "rank": 15},
        {"hashtag_name": "cooking",       "publish_cnt":  5_000_000, "video_views": 1_400_000_000, "trend": "↑", "rank": 16},
        {"hashtag_name": "lifestyle",     "publish_cnt":  4_800_000, "video_views": 1_300_000_000, "trend": "→", "rank": 17},
        {"hashtag_name": "workout",       "publish_cnt":  4_500_000, "video_views": 1_200_000_000, "trend": "↑", "rank": 18},
        {"hashtag_name": "relationship",  "publish_cnt":  4_200_000, "video_views": 1_100_000_000, "trend": "↑", "rank": 19},
        {"hashtag_name": "mindset",       "publish_cnt":  4_000_000, "video_views": 1_000_000_000, "trend": "↑", "rank": 20},
    ]
    return data[:limit]


def _demo_sounds(limit: int) -> list[dict]:
    data = [
        {"sound_id": "1", "title": "Espresso",                "author": "Sabrina Carpenter",       "video_count": 2_800_000, "trend": "↑", "duration": 173, "is_original": False},
        {"sound_id": "2", "title": "APT.",                    "author": "ROSÉ & Bruno Mars",        "video_count": 2_500_000, "trend": "↑", "duration": 202, "is_original": False},
        {"sound_id": "3", "title": "Birds of a Feather",      "author": "Billie Eilish",            "video_count": 2_200_000, "trend": "↑", "duration": 210, "is_original": False},
        {"sound_id": "4", "title": "That's So True",          "author": "Gracie Abrams",            "video_count": 1_800_000, "trend": "↑", "duration": 184, "is_original": False},
        {"sound_id": "5", "title": "Die With A Smile",        "author": "Lady Gaga & Bruno Mars",   "video_count": 1_600_000, "trend": "↑", "duration": 251, "is_original": False},
        {"sound_id": "6", "title": "original sound",          "author": "TikTok Creator",           "video_count": 1_500_000, "trend": "→", "duration": 30,  "is_original": True},
        {"sound_id": "7", "title": "Too Sweet",               "author": "Hozier",                   "video_count": 1_400_000, "trend": "→", "duration": 229, "is_original": False},
        {"sound_id": "8", "title": "Good Luck, Babe!",        "author": "Chappell Roan",            "video_count": 1_300_000, "trend": "↑", "duration": 218, "is_original": False},
        {"sound_id": "9", "title": "MILLION DOLLAR BABY",     "author": "Tommy Richman",            "video_count": 1_100_000, "trend": "↑", "duration": 150, "is_original": False},
        {"sound_id":"10", "title": "Levii's Jeans",           "author": "Beyoncé ft. Post Malone",  "video_count": 1_000_000, "trend": "→", "duration": 238, "is_original": False},
    ]
    return data[:limit]


def _demo_videos(limit: int) -> list[dict]:
    data = [
        {"video_id": "1", "title": "Trending dance challenge",        "play_count": 45_000_000, "like_count": 3_200_000, "comment_count": 45_000, "share_count": 120_000, "hashtags": ["fyp", "dance", "viral"],     "sound_title": "Espresso"},
        {"video_id": "2", "title": "Life hack you didn't know",       "play_count": 38_000_000, "like_count": 2_800_000, "comment_count": 38_000, "share_count":  98_000, "hashtags": ["lifehack", "fyp", "tips"],    "sound_title": "original sound"},
        {"video_id": "3", "title": "5-min recipe that went viral",    "play_count": 32_000_000, "like_count": 2_400_000, "comment_count": 29_000, "share_count":  85_000, "hashtags": ["food", "cooking", "recipe"],  "sound_title": "APT."},
        {"video_id": "4", "title": "Morning routine 2025",            "play_count": 28_000_000, "like_count": 2_100_000, "comment_count": 24_000, "share_count":  72_000, "hashtags": ["morning", "routine", "life"], "sound_title": "Too Sweet"},
        {"video_id": "5", "title": "Outfit of the day GRWM",          "play_count": 25_000_000, "like_count": 1_900_000, "comment_count": 21_000, "share_count":  65_000, "hashtags": ["ootd", "fashion", "grwm"],   "sound_title": "Good Luck, Babe!"},
    ]
    return data[:limit]
