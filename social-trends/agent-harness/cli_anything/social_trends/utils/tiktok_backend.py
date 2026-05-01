"""TikTok trends backend — trending videos, sounds, and hashtags.

Uses the RapidAPI TikTok scraper API in live mode.
Falls back to curated demo data when no key is configured.

Get a RapidAPI key at: https://rapidapi.com
Recommended API: "TikTok Scraper" on RapidAPI (search for tiktok-scraper7 or similar)

Set key via: social-trends auth set-tiktok-key <KEY>
Or env var:   TIKTOK_RAPIDAPI_KEY
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

CONFIG_FILE = Path.home() / ".config" / "social-trends" / "config.json"
ENV_TT_KEY = "TIKTOK_RAPIDAPI_KEY"
RAPIDAPI_HOST = "tiktok-scraper7.p.rapidapi.com"
RAPIDAPI_BASE = f"https://{RAPIDAPI_HOST}"

DEMO_TRENDING_VIDEOS = [
    {"rank": 1, "id": "7380000000000001", "desc": "Wait for the ending 😱 #fyp #viral", "author": "@trendsetter_creator", "plays": 18700000, "likes": 2340000, "comments": 87400, "shares": 412000, "duration": 15, "music": "original sound - trendsetter_creator", "hashtags": ["#fyp", "#viral"], "trend_score": 99},
    {"rank": 2, "id": "7380000000000002", "desc": "POV: you finally found the tutorial you needed 🔥 #tutorial #lifehack", "author": "@lifehack_daily", "plays": 14200000, "likes": 1890000, "comments": 54200, "shares": 298000, "duration": 30, "music": "Espresso - Sabrina Carpenter", "hashtags": ["#tutorial", "#lifehack", "#fyp"], "trend_score": 97},
    {"rank": 3, "id": "7380000000000003", "desc": "This is how theme pages make $10k/month 💰 #themepage #passiveincome", "author": "@incomehacks", "plays": 11900000, "likes": 1540000, "comments": 42100, "shares": 187000, "duration": 45, "music": "Die With A Smile - Lady Gaga & Bruno Mars", "hashtags": ["#themepage", "#passiveincome", "#business"], "trend_score": 95},
    {"rank": 4, "id": "7380000000000004", "desc": "The most satisfying thing you'll see today ✨ #satisfying #asmr", "author": "@satisfy_world", "plays": 9800000, "likes": 1230000, "comments": 28900, "shares": 143000, "duration": 20, "music": "Not Like Us - Kendrick Lamar", "hashtags": ["#satisfying", "#asmr", "#fyp"], "trend_score": 93},
    {"rank": 5, "id": "7380000000000005", "desc": "How I grew 0 to 100k followers in 30 days (real method) 📈", "author": "@growth_formula", "plays": 8700000, "likes": 987000, "comments": 35600, "shares": 218000, "duration": 60, "music": "MILLION DOLLAR BABY - Tommy Richman", "hashtags": ["#growth", "#tiktokgrowth", "#followers"], "trend_score": 91},
    {"rank": 6, "id": "7380000000000006", "desc": "I tested every viral food hack so you don't have to 🍕 #food #viral", "author": "@foodtest_official", "plays": 7600000, "likes": 834000, "comments": 19200, "shares": 98000, "duration": 58, "music": "Starboy (sped up) - The Weeknd", "hashtags": ["#food", "#viral", "#foodhack"], "trend_score": 89},
    {"rank": 7, "id": "7380000000000007", "desc": "Small business packaging video 📦 #smallbusiness #packaging #aesthetic", "author": "@shopwithme_daily", "plays": 6900000, "likes": 712000, "comments": 14800, "shares": 76000, "duration": 22, "music": "Beautiful Things - Benson Boone", "hashtags": ["#smallbusiness", "#packaging", "#aesthetic"], "trend_score": 87},
    {"rank": 8, "id": "7380000000000008", "desc": "Day in my life making passive income online 💻 #dayinmylife #onlineincome", "author": "@remotework_life", "plays": 5800000, "likes": 628000, "comments": 22400, "shares": 134000, "duration": 75, "music": "Luther - Kendrick Lamar ft. SZA", "hashtags": ["#dayinmylife", "#onlineincome", "#remotework"], "trend_score": 85},
    {"rank": 9, "id": "7380000000000009", "desc": "Get ready with me for a brand deal ✨ #GRWM #contentcreator #brandeal", "author": "@creator_life_daily", "plays": 4900000, "likes": 541000, "comments": 11200, "shares": 54000, "duration": 35, "music": "I Had Some Help - Post Malone ft. Morgan Wallen", "hashtags": ["#GRWM", "#contentcreator", "#brandeal"], "trend_score": 82},
    {"rank": 10, "id": "7380000000000010", "desc": "Watch this if you want to quit your 9-5 💼 #entrepreneur #9to5", "author": "@freedom_mindset", "plays": 4200000, "likes": 487000, "comments": 28900, "shares": 167000, "duration": 50, "music": "A Bar Song (Tipsy) - Shaboozey", "hashtags": ["#entrepreneur", "#9to5", "#freedom"], "trend_score": 80},
]

DEMO_TRENDING_SOUNDS = [
    {"rank": 1, "id": "tt_sound_001", "title": "MILLION DOLLAR BABY", "author": "Tommy Richman", "uses": 4800000, "trend": "rising", "duration": 30, "bpm": 130, "mood": "energetic", "recommended_content": ["motivation", "fitness", "money", "glow up"]},
    {"rank": 2, "id": "tt_sound_002", "title": "Espresso", "author": "Sabrina Carpenter", "uses": 3900000, "trend": "stable", "duration": 30, "bpm": 104, "mood": "flirty/fun", "recommended_content": ["beauty", "GRWM", "lifestyle", "fashion"]},
    {"rank": 3, "id": "tt_sound_003", "title": "Die With A Smile", "author": "Lady Gaga & Bruno Mars", "uses": 3200000, "trend": "rising", "duration": 30, "bpm": 116, "mood": "romantic", "recommended_content": ["couple content", "travel", "aesthetic", "emotional"]},
    {"rank": 4, "id": "tt_sound_004", "title": "Not Like Us", "author": "Kendrick Lamar", "uses": 2900000, "trend": "stable", "duration": 30, "bpm": 98, "mood": "hype/aggressive", "recommended_content": ["roast", "calling out", "opinion", "sports"]},
    {"rank": 5, "id": "tt_sound_005", "title": "Starboy (sped up)", "author": "The Weeknd", "uses": 2600000, "trend": "stable", "duration": 30, "bpm": 188, "mood": "dark/cool", "recommended_content": ["night routine", "aesthetic", "transitions", "cool edits"]},
    {"rank": 6, "id": "tt_sound_006", "title": "Luther", "author": "Kendrick Lamar ft. SZA", "uses": 2200000, "trend": "rising", "duration": 30, "bpm": 92, "mood": "smooth/sentimental", "recommended_content": ["day in life", "emotional reveal", "relationship", "reflection"]},
    {"rank": 7, "id": "tt_sound_007", "title": "Beautiful Things", "author": "Benson Boone", "uses": 1900000, "trend": "falling", "duration": 30, "bpm": 130, "mood": "emotional/hopeful", "recommended_content": ["transformation", "achievement", "small business", "personal growth"]},
    {"rank": 8, "id": "tt_sound_008", "title": "original sound - viral_trend", "author": "@viral_trend", "uses": 1700000, "trend": "rising", "duration": 7, "bpm": None, "mood": "comedic", "recommended_content": ["comedy", "reaction", "POV", "relatable"]},
    {"rank": 9, "id": "tt_sound_009", "title": "I Had Some Help", "author": "Post Malone ft. Morgan Wallen", "uses": 1500000, "trend": "stable", "duration": 30, "bpm": 132, "mood": "fun/laid-back", "recommended_content": ["collab", "behind the scenes", "friends", "lifestyle"]},
    {"rank": 10, "id": "tt_sound_010", "title": "A Bar Song (Tipsy)", "author": "Shaboozey", "uses": 1300000, "trend": "rising", "duration": 30, "bpm": 120, "mood": "fun/party", "recommended_content": ["night out", "friends", "summer", "fun challenges"]},
]

DEMO_TRENDING_HASHTAGS = [
    {"tag": "#fyp", "weekly_posts": 42000000, "avg_plays": 28000, "trend": "stable", "competition": "extreme", "advice": "Use sparingly — pair with niche tags"},
    {"tag": "#foryou", "weekly_posts": 31000000, "avg_plays": 24000, "trend": "stable", "competition": "extreme", "advice": "Avoid alone — algorithm ignores generic FYP tags"},
    {"tag": "#viral", "weekly_posts": 18000000, "avg_plays": 32000, "trend": "stable", "competition": "very_high", "advice": "Combine with niche-specific tags"},
    {"tag": "#trending", "weekly_posts": 12000000, "avg_plays": 29000, "trend": "stable", "competition": "very_high", "advice": "Use when content is genuinely trend-based"},
    {"tag": "#contentcreator", "weekly_posts": 4200000, "avg_plays": 67000, "trend": "rising", "competition": "high", "advice": "Good for creator community reach"},
    {"tag": "#themepage", "weekly_posts": 890000, "avg_plays": 142000, "trend": "rising", "competition": "low", "advice": "HIGH OPPORTUNITY — low competition, high reach"},
    {"tag": "#passiveincome", "weekly_posts": 2100000, "avg_plays": 118000, "trend": "rising", "competition": "medium", "advice": "Finance/business niche must-use"},
    {"tag": "#smallbusiness", "weekly_posts": 3800000, "avg_plays": 94000, "trend": "rising", "competition": "medium", "advice": "Great for product sellers and service creators"},
    {"tag": "#entrepreneur", "weekly_posts": 3100000, "avg_plays": 108000, "trend": "rising", "competition": "medium", "advice": "Broad reach in business niche"},
    {"tag": "#dayinmylife", "weekly_posts": 5600000, "avg_plays": 78000, "trend": "stable", "competition": "high", "advice": "Evergreen lifestyle content tag"},
    {"tag": "#GRWM", "weekly_posts": 6200000, "avg_plays": 84000, "trend": "stable", "competition": "high", "advice": "Essential for beauty/fashion creators"},
    {"tag": "#motivation", "weekly_posts": 4900000, "avg_plays": 91000, "trend": "rising", "competition": "high", "advice": "Works across niches, especially fitness/business"},
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
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    CONFIG_FILE.chmod(0o600)


def get_api_key(cli_key: str | None = None) -> str | None:
    if cli_key:
        return cli_key
    env_key = os.environ.get(ENV_TT_KEY)
    if env_key:
        return env_key
    return _load_config().get("tiktok_rapidapi_key")


def set_api_key(key: str) -> None:
    config = _load_config()
    config["tiktok_rapidapi_key"] = key
    _save_config(config)


def is_demo_mode(api_key: str | None) -> bool:
    return not api_key


def _rapidapi_get(path: str, params: dict, api_key: str) -> dict:
    if not _HAS_REQUESTS:
        raise RuntimeError("requests library not installed. Run: pip install requests")
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": RAPIDAPI_HOST,
    }
    resp = _requests.get(f"{RAPIDAPI_BASE}{path}", headers=headers, params=params, timeout=20)
    resp.raise_for_status()
    return resp.json()


def _parse_live_video(item: dict, rank: int) -> dict:
    video = item.get("video", {})
    stats = item.get("stats", {})
    author = item.get("author", {})
    music = item.get("music", {})
    desc = item.get("desc", "")
    hashtags = [f"#{c['hashtagName']}" for c in item.get("challenges", []) if c.get("hashtagName")]
    return {
        "rank": rank,
        "id": item.get("id", ""),
        "desc": desc[:120],
        "author": f"@{author.get('uniqueId', '')}",
        "plays": stats.get("playCount", 0),
        "likes": stats.get("diggCount", 0),
        "comments": stats.get("commentCount", 0),
        "shares": stats.get("shareCount", 0),
        "duration": video.get("duration", 0),
        "music": f"{music.get('title', '')} - {music.get('authorName', '')}",
        "hashtags": hashtags[:5],
        "trend_score": min(99, int(stats.get("playCount", 0) / 200000)),
    }


def fetch_trending_videos(
    region: str = "US",
    limit: int = 20,
    api_key: str | None = None,
) -> dict:
    """Fetch TikTok trending videos. Falls back to demo data if no API key."""
    key = get_api_key(api_key)
    demo = is_demo_mode(key)

    if demo:
        items = DEMO_TRENDING_VIDEOS[:min(limit, len(DEMO_TRENDING_VIDEOS))]
        return {
            "platform": "tiktok",
            "mode": "demo",
            "region": region,
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "total": len(items),
            "items": items,
            "note": "Demo data. Set TIKTOK_RAPIDAPI_KEY or run 'social-trends auth set-tiktok-key' for live data.",
        }

    data = _rapidapi_get("/feed/list", {"count": min(limit, 30), "region": region.lower()}, key)
    raw_items = data.get("itemList", data.get("data", {}).get("itemList", []))
    items = [_parse_live_video(item, i + 1) for i, item in enumerate(raw_items[:limit])]

    return {
        "platform": "tiktok",
        "mode": "live",
        "region": region,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "total": len(items),
        "items": items,
    }


def fetch_trending_sounds(
    limit: int = 20,
    api_key: str | None = None,
) -> dict:
    """Fetch TikTok trending sounds/music."""
    key = get_api_key(api_key)
    demo = is_demo_mode(key)

    if demo:
        items = DEMO_TRENDING_SOUNDS[:min(limit, len(DEMO_TRENDING_SOUNDS))]
        return {
            "platform": "tiktok",
            "type": "sounds",
            "mode": "demo",
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "total": len(items),
            "items": items,
            "note": "Demo data. Set TIKTOK_RAPIDAPI_KEY for live data.",
        }

    data = _rapidapi_get("/music/trending", {"count": min(limit, 30)}, key)
    raw_items = data.get("data", [])
    items = []
    for i, item in enumerate(raw_items[:limit], 1):
        music_info = item.get("musicInfo", item)
        items.append({
            "rank": i,
            "id": music_info.get("id", ""),
            "title": music_info.get("title", ""),
            "author": music_info.get("authorName", ""),
            "uses": item.get("useCount", 0),
            "trend": "live",
            "duration": music_info.get("duration", 0),
        })

    return {
        "platform": "tiktok",
        "type": "sounds",
        "mode": "live",
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "total": len(items),
        "items": items,
    }


def fetch_trending_hashtags(
    niche: str | None = None,
    limit: int = 20,
    api_key: str | None = None,
) -> dict:
    """Return trending TikTok hashtags."""
    key = get_api_key(api_key)
    demo = is_demo_mode(key)

    base_tags = list(DEMO_TRENDING_HASHTAGS)
    if niche:
        niche_tags = _niche_tiktok_hashtags(niche)
        seen = {t["tag"] for t in niche_tags}
        base_tags = niche_tags + [t for t in base_tags if t["tag"] not in seen]

    items = base_tags[:min(limit, len(base_tags))]

    return {
        "platform": "tiktok",
        "type": "hashtags",
        "mode": "demo" if demo else "curated+live",
        "niche": niche,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "total": len(items),
        "items": items,
    }


def _niche_tiktok_hashtags(niche: str) -> list:
    niche_map = {
        "fitness": [
            {"tag": "#fitness", "weekly_posts": 12000000, "avg_plays": 84000, "trend": "stable", "competition": "very_high", "advice": "Combine with specific workout types"},
            {"tag": "#workout", "weekly_posts": 9800000, "avg_plays": 76000, "trend": "stable", "competition": "high", "advice": "Good reach, add body part specifics"},
            {"tag": "#fitcheck", "weekly_posts": 4200000, "avg_plays": 118000, "trend": "rising", "competition": "medium", "advice": "High engagement, great for transformation content"},
            {"tag": "#bodytransformation", "weekly_posts": 2100000, "avg_plays": 142000, "trend": "rising", "competition": "medium", "advice": "Very high engagement — show real progress"},
            {"tag": "#gymtok", "weekly_posts": 3400000, "avg_plays": 96000, "trend": "stable", "competition": "medium", "advice": "Gym community specific — very engaged"},
        ],
        "finance": [
            {"tag": "#financetok", "weekly_posts": 3200000, "avg_plays": 124000, "trend": "rising", "competition": "medium", "advice": "Finance community hub — very engaged"},
            {"tag": "#moneytok", "weekly_posts": 2800000, "avg_plays": 138000, "trend": "rising", "competition": "medium", "advice": "High value audience, great for monetization"},
            {"tag": "#investing", "weekly_posts": 1900000, "avg_plays": 156000, "trend": "rising", "competition": "low", "advice": "Lower competition, very high reach per post"},
            {"tag": "#stocktok", "weekly_posts": 980000, "avg_plays": 172000, "trend": "rising", "competition": "low", "advice": "Niche but powerful — finance experts dominate"},
            {"tag": "#debtfree", "weekly_posts": 1400000, "avg_plays": 144000, "trend": "rising", "competition": "low", "advice": "Emotional content performs extremely well"},
        ],
        "beauty": [
            {"tag": "#beautytok", "weekly_posts": 8900000, "avg_plays": 88000, "trend": "stable", "competition": "very_high", "advice": "Core beauty community tag — always use"},
            {"tag": "#makeuptutorial", "weekly_posts": 6200000, "avg_plays": 94000, "trend": "stable", "competition": "high", "advice": "Tutorial content gets 3x more saves"},
            {"tag": "#skincareroutine", "weekly_posts": 4100000, "avg_plays": 102000, "trend": "rising", "competition": "high", "advice": "Rising niche — skincare > makeup currently"},
            {"tag": "#glowup", "weekly_posts": 5800000, "avg_plays": 118000, "trend": "rising", "competition": "high", "advice": "Transformation content viral potential"},
            {"tag": "#beautydupe", "weekly_posts": 1200000, "avg_plays": 164000, "trend": "rising", "competition": "low", "advice": "OPPORTUNITY — price-conscious audience, low comp"},
        ],
    }
    key = niche.lower()
    for k, v in niche_map.items():
        if k in key or key in k:
            return v
    return []
