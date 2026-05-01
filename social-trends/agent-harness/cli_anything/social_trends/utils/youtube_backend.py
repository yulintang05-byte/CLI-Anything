"""YouTube Data API v3 backend — trending videos, hashtags, and music discovery.

Supports full live mode (YouTube Data API v3 key) and demo mode with curated
sample data when no key is configured.

Live API docs: https://developers.google.com/youtube/v3/docs
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

API_BASE = "https://www.googleapis.com/youtube/v3"
CONFIG_DIR = Path.home() / ".config" / "social-trends"
CONFIG_FILE = CONFIG_DIR / "config.json"
ENV_YT_KEY = "YOUTUBE_API_KEY"

CATEGORY_IDS = {
    "all": "0",
    "music": "10",
    "gaming": "20",
    "entertainment": "24",
    "news": "25",
    "sports": "17",
    "howto": "26",
    "comedy": "23",
    "beauty": "26",
    "tech": "28",
    "food": "26",
}

DEMO_TRENDING = [
    {"rank": 1, "id": "dQw4w9WgXcQ", "title": "How to go viral in 2025 (complete guide)", "channel": "CreatorPro", "views": 4200000, "likes": 312000, "comments": 18500, "duration": "PT14M32S", "published": "2025-04-28T10:00:00Z", "hashtags": ["#viral", "#youtube", "#creator"], "category": "howto", "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg"},
    {"rank": 2, "id": "abc123xyz01", "title": "This AI tool changed my content strategy forever", "channel": "TechCreator", "views": 3100000, "likes": 198000, "comments": 9200, "duration": "PT8M15S", "published": "2025-04-27T14:00:00Z", "hashtags": ["#AI", "#contentcreator", "#youtube"], "category": "tech", "thumbnail": ""},
    {"rank": 3, "id": "abc123xyz02", "title": "I posted every day for 30 days — here's what happened", "channel": "GrowthHacker", "views": 2900000, "likes": 241000, "comments": 14300, "duration": "PT11M08S", "published": "2025-04-26T09:00:00Z", "hashtags": ["#30daychallenge", "#youtube", "#growth"], "category": "entertainment", "thumbnail": ""},
    {"rank": 4, "id": "abc123xyz03", "title": "Trending beats compilation April 2025 (No Copyright)", "channel": "FreeBeats4You", "views": 2700000, "likes": 89000, "comments": 3400, "duration": "PT45M00S", "published": "2025-04-25T16:00:00Z", "hashtags": ["#music", "#beats", "#nocopyright"], "category": "music", "thumbnail": ""},
    {"rank": 5, "id": "abc123xyz04", "title": "The algorithm HATES this but I'm posting it anyway", "channel": "RealCreator", "views": 2300000, "likes": 178000, "comments": 22100, "duration": "PT9M44S", "published": "2025-04-24T18:00:00Z", "hashtags": ["#youtube", "#algorithm", "#honest"], "category": "entertainment", "thumbnail": ""},
    {"rank": 6, "id": "abc123xyz05", "title": "How I make $50k/month with theme pages (full breakdown)", "channel": "PassiveIncome101", "views": 1900000, "likes": 132000, "comments": 8700, "duration": "PT22M17S", "published": "2025-04-23T12:00:00Z", "hashtags": ["#themepages", "#passiveincome", "#instagram"], "category": "howto", "thumbnail": ""},
    {"rank": 7, "id": "abc123xyz06", "title": "Morning routine that made me 1M subscribers", "channel": "LifeByDesign", "views": 1700000, "likes": 91000, "comments": 5600, "duration": "PT7M32S", "published": "2025-04-22T07:00:00Z", "hashtags": ["#morningroutine", "#productivity", "#1million"], "category": "howto", "thumbnail": ""},
    {"rank": 8, "id": "abc123xyz07", "title": "POV: You found the most satisfying video on the internet", "channel": "SatisfyingWorld", "views": 1600000, "likes": 74000, "comments": 2800, "duration": "PT3M12S", "published": "2025-04-21T20:00:00Z", "hashtags": ["#satisfying", "#pov", "#trending"], "category": "entertainment", "thumbnail": ""},
    {"rank": 9, "id": "abc123xyz08", "title": "New viral sound that's everywhere right now 🔥", "channel": "SoundTrends", "views": 1450000, "likes": 67000, "comments": 4100, "duration": "PT2M08S", "published": "2025-04-20T15:00:00Z", "hashtags": ["#sound", "#viral", "#trending"], "category": "music", "thumbnail": ""},
    {"rank": 10, "id": "abc123xyz09", "title": "I tried every viral recipe from TikTok so you don't have to", "channel": "FoodReacts", "views": 1300000, "likes": 103000, "comments": 7200, "duration": "PT16M55S", "published": "2025-04-19T11:00:00Z", "hashtags": ["#tiktokfood", "#viral", "#recipe"], "category": "food", "thumbnail": ""},
]

DEMO_MUSIC_TRENDING = [
    {"rank": 1, "title": "MILLION DOLLAR BABY", "artist": "Tommy Richman", "uses_on_shorts": 2100000, "trend": "rising", "bpm": 130, "mood": "energetic", "genre": "pop/rnb"},
    {"rank": 2, "title": "Not Like Us", "artist": "Kendrick Lamar", "uses_on_shorts": 1850000, "trend": "stable", "bpm": 98, "mood": "aggressive", "genre": "hip-hop"},
    {"rank": 3, "title": "Espresso", "artist": "Sabrina Carpenter", "uses_on_shorts": 1700000, "trend": "stable", "bpm": 104, "mood": "flirty", "genre": "pop"},
    {"rank": 4, "title": "Die With A Smile", "artist": "Lady Gaga & Bruno Mars", "uses_on_shorts": 1600000, "trend": "rising", "bpm": 116, "mood": "romantic", "genre": "pop"},
    {"rank": 5, "title": "Starboy (sped up)", "artist": "The Weeknd", "uses_on_shorts": 1400000, "trend": "stable", "bpm": 188, "mood": "dark/cool", "genre": "pop/rnb"},
    {"rank": 6, "title": "Beautiful Things", "artist": "Benson Boone", "uses_on_shorts": 1350000, "trend": "falling", "bpm": 130, "mood": "emotional", "genre": "pop/rock"},
    {"rank": 7, "title": "Luther", "artist": "Kendrick Lamar ft. SZA", "uses_on_shorts": 1200000, "trend": "rising", "bpm": 92, "mood": "smooth", "genre": "hip-hop/rnb"},
    {"rank": 8, "title": "I Had Some Help", "artist": "Post Malone ft. Morgan Wallen", "uses_on_shorts": 1100000, "trend": "stable", "bpm": 132, "mood": "country-pop", "genre": "country/pop"},
    {"rank": 9, "title": "A Bar Song (Tipsy)", "artist": "Shaboozey", "uses_on_shorts": 980000, "trend": "rising", "bpm": 120, "mood": "fun", "genre": "country"},
    {"rank": 10, "title": "Lose Control", "artist": "Teddy Swims", "uses_on_shorts": 870000, "trend": "stable", "bpm": 75, "mood": "soulful", "genre": "rnb/soul"},
]

DEMO_HASHTAGS = [
    {"tag": "#viral", "weekly_posts": 8200000, "avg_views": 145000, "trend": "rising", "competition": "very_high"},
    {"tag": "#fyp", "weekly_posts": 12400000, "avg_views": 89000, "trend": "stable", "competition": "very_high"},
    {"tag": "#trending", "weekly_posts": 6100000, "avg_views": 112000, "trend": "stable", "competition": "high"},
    {"tag": "#shorts", "weekly_posts": 9800000, "avg_views": 74000, "trend": "rising", "competition": "very_high"},
    {"tag": "#contentcreator", "weekly_posts": 2300000, "avg_views": 58000, "trend": "rising", "competition": "medium"},
    {"tag": "#youtube", "weekly_posts": 4100000, "avg_views": 67000, "trend": "stable", "competition": "high"},
    {"tag": "#motivation", "weekly_posts": 3700000, "avg_views": 92000, "trend": "rising", "competition": "high"},
    {"tag": "#entrepreneur", "weekly_posts": 1900000, "avg_views": 78000, "trend": "rising", "competition": "medium"},
    {"tag": "#passiveincome", "weekly_posts": 890000, "avg_views": 134000, "trend": "rising", "competition": "medium"},
    {"tag": "#themepages", "weekly_posts": 340000, "avg_views": 210000, "trend": "rising", "competition": "low"},
]


def _load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_config(config: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    CONFIG_FILE.chmod(0o600)


def get_api_key(cli_key: str | None = None) -> str | None:
    if cli_key:
        return cli_key
    env_key = os.environ.get(ENV_YT_KEY)
    if env_key:
        return env_key
    return _load_config().get("youtube_api_key")


def set_api_key(key: str) -> None:
    config = _load_config()
    config["youtube_api_key"] = key
    _save_config(config)


def is_demo_mode(api_key: str | None) -> bool:
    return not api_key


def _get(endpoint: str, params: dict, api_key: str) -> dict:
    if not _HAS_REQUESTS:
        raise RuntimeError("requests library not installed. Run: pip install requests")
    params["key"] = api_key
    resp = _requests.get(f"{API_BASE}/{endpoint}", params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def fetch_trending_videos(
    region: str = "US",
    category: str = "all",
    limit: int = 20,
    api_key: str | None = None,
) -> dict:
    """Fetch trending YouTube videos. Falls back to demo data if no API key."""
    key = get_api_key(api_key)
    demo = is_demo_mode(key)

    if demo:
        items = DEMO_TRENDING[:min(limit, len(DEMO_TRENDING))]
        return {
            "platform": "youtube",
            "mode": "demo",
            "region": region,
            "category": category,
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "total": len(items),
            "items": items,
            "note": "Demo data. Set YOUTUBE_API_KEY or run 'social-trends auth set-youtube-key' for live data.",
        }

    cat_id = CATEGORY_IDS.get(category.lower(), "0")
    params = {
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular",
        "regionCode": region.upper(),
        "maxResults": min(limit, 50),
    }
    if cat_id != "0":
        params["videoCategoryId"] = cat_id

    data = _get("videos", params, key)
    items = []
    for i, item in enumerate(data.get("items", []), 1):
        snip = item.get("snippet", {})
        stats = item.get("statistics", {})
        tags = snip.get("tags", [])
        hashtags = [f"#{t.replace(' ', '')}" for t in tags[:5] if t]
        items.append({
            "rank": i,
            "id": item.get("id", ""),
            "title": snip.get("title", ""),
            "channel": snip.get("channelTitle", ""),
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "duration": item.get("contentDetails", {}).get("duration", ""),
            "published": snip.get("publishedAt", ""),
            "hashtags": hashtags,
            "category": category,
            "thumbnail": snip.get("thumbnails", {}).get("high", {}).get("url", ""),
        })

    return {
        "platform": "youtube",
        "mode": "live",
        "region": region,
        "category": category,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "total": len(items),
        "items": items,
    }


def fetch_trending_music(
    region: str = "US",
    limit: int = 20,
    api_key: str | None = None,
) -> dict:
    """Fetch trending YouTube music videos."""
    key = get_api_key(api_key)
    demo = is_demo_mode(key)

    if demo:
        items = DEMO_MUSIC_TRENDING[:min(limit, len(DEMO_MUSIC_TRENDING))]
        return {
            "platform": "youtube",
            "type": "music",
            "mode": "demo",
            "region": region,
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "total": len(items),
            "items": items,
            "note": "Demo data. Set YOUTUBE_API_KEY for live data.",
        }

    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region.upper(),
        "videoCategoryId": CATEGORY_IDS["music"],
        "maxResults": min(limit, 50),
    }
    data = _get("videos", params, key)
    items = []
    for i, item in enumerate(data.get("items", []), 1):
        snip = item.get("snippet", {})
        stats = item.get("statistics", {})
        items.append({
            "rank": i,
            "title": snip.get("title", ""),
            "channel": snip.get("channelTitle", ""),
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "published": snip.get("publishedAt", ""),
            "thumbnail": snip.get("thumbnails", {}).get("high", {}).get("url", ""),
        })

    return {
        "platform": "youtube",
        "type": "music",
        "mode": "live",
        "region": region,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "total": len(items),
        "items": items,
    }


def fetch_trending_hashtags(
    niche: str | None = None,
    limit: int = 20,
    api_key: str | None = None,
) -> dict:
    """Return trending YouTube hashtags (curated + search-based in live mode)."""
    key = get_api_key(api_key)
    demo = is_demo_mode(key)

    base_tags = list(DEMO_HASHTAGS)
    if niche:
        niche_tags = _niche_hashtags("youtube", niche)
        base_tags = niche_tags + [t for t in base_tags if t not in niche_tags]

    items = base_tags[:min(limit, len(base_tags))]

    return {
        "platform": "youtube",
        "type": "hashtags",
        "mode": "demo" if demo else "curated+live",
        "niche": niche,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "total": len(items),
        "items": items,
    }


def _niche_hashtags(platform: str, niche: str) -> list:
    niche_map = {
        "fitness": [
            {"tag": "#fitness", "weekly_posts": 5100000, "avg_views": 88000, "trend": "stable", "competition": "very_high"},
            {"tag": "#workout", "weekly_posts": 3200000, "avg_views": 72000, "trend": "stable", "competition": "high"},
            {"tag": "#gym", "weekly_posts": 4400000, "avg_views": 65000, "trend": "stable", "competition": "high"},
            {"tag": "#weightloss", "weekly_posts": 2100000, "avg_views": 97000, "trend": "rising", "competition": "high"},
            {"tag": "#homeworkout", "weekly_posts": 1800000, "avg_views": 84000, "trend": "rising", "competition": "medium"},
        ],
        "finance": [
            {"tag": "#finance", "weekly_posts": 1900000, "avg_views": 102000, "trend": "rising", "competition": "medium"},
            {"tag": "#investing", "weekly_posts": 1400000, "avg_views": 125000, "trend": "rising", "competition": "medium"},
            {"tag": "#stockmarket", "weekly_posts": 980000, "avg_views": 141000, "trend": "rising", "competition": "medium"},
            {"tag": "#crypto", "weekly_posts": 2800000, "avg_views": 89000, "trend": "volatile", "competition": "high"},
            {"tag": "#budgeting", "weekly_posts": 760000, "avg_views": 118000, "trend": "rising", "competition": "low"},
        ],
        "beauty": [
            {"tag": "#makeup", "weekly_posts": 6200000, "avg_views": 71000, "trend": "stable", "competition": "very_high"},
            {"tag": "#skincare", "weekly_posts": 4800000, "avg_views": 83000, "trend": "rising", "competition": "very_high"},
            {"tag": "#GRWM", "weekly_posts": 2900000, "avg_views": 94000, "trend": "rising", "competition": "high"},
            {"tag": "#beautyhacks", "weekly_posts": 1100000, "avg_views": 108000, "trend": "rising", "competition": "medium"},
            {"tag": "#dupes", "weekly_posts": 890000, "avg_views": 131000, "trend": "rising", "competition": "low"},
        ],
        "food": [
            {"tag": "#foodie", "weekly_posts": 5400000, "avg_views": 68000, "trend": "stable", "competition": "very_high"},
            {"tag": "#recipe", "weekly_posts": 3700000, "avg_views": 79000, "trend": "stable", "competition": "high"},
            {"tag": "#cooking", "weekly_posts": 4100000, "avg_views": 72000, "trend": "stable", "competition": "high"},
            {"tag": "#foodhacks", "weekly_posts": 1600000, "avg_views": 110000, "trend": "rising", "competition": "medium"},
            {"tag": "#mukbang", "weekly_posts": 1200000, "avg_views": 96000, "trend": "stable", "competition": "medium"},
        ],
        "travel": [
            {"tag": "#travel", "weekly_posts": 7100000, "avg_views": 62000, "trend": "stable", "competition": "very_high"},
            {"tag": "#wanderlust", "weekly_posts": 2800000, "avg_views": 58000, "trend": "stable", "competition": "high"},
            {"tag": "#travelvlog", "weekly_posts": 1900000, "avg_views": 87000, "trend": "rising", "competition": "medium"},
            {"tag": "#budgettravel", "weekly_posts": 780000, "avg_views": 122000, "trend": "rising", "competition": "low"},
            {"tag": "#solotravel", "weekly_posts": 920000, "avg_views": 104000, "trend": "rising", "competition": "medium"},
        ],
    }
    key = niche.lower()
    for k, v in niche_map.items():
        if k in key or key in k:
            return v
    return []
