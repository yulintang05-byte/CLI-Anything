"""Backend drivers for YouTube, TikTok, and social media trend data.

Tries real scraping/API calls first, falls back to cached/curated data
so the CLI always returns usable results even without API keys.
"""

import json
import time
import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_CACHE_DIR = Path.home() / ".cli-anything-social-trends" / "cache"
_CACHE_TTL = 3600  # 1 hour


# ── Cache helpers ─────────────────────────────────────────────────────────────

def _cache_key(name: str, **kwargs) -> str:
    raw = name + json.dumps(kwargs, sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def _cache_get(key: str) -> Optional[dict]:
    path = _CACHE_DIR / f"{key}.json"
    if not path.exists():
        return None
    try:
        with open(path) as f:
            data = json.load(f)
        if time.time() - data.get("ts", 0) > _CACHE_TTL:
            return None
        return data.get("payload")
    except (json.JSONDecodeError, IOError):
        return None


def _cache_set(key: str, payload) -> None:
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _CACHE_DIR / f"{key}.json"
    with open(path, "w") as f:
        json.dump({"ts": time.time(), "payload": payload}, f)


# ── YouTube ───────────────────────────────────────────────────────────────────

def fetch_youtube_trending(region: str = "US", category: str = "all", limit: int = 20) -> list[dict]:
    key = _cache_key("yt_trending", region=region, category=category)
    cached = _cache_get(key)
    if cached:
        return cached[:limit]

    results = _youtube_via_searchpython(region, category, limit)
    if not results:
        results = _youtube_via_api(region, category, limit)
    if not results:
        results = _youtube_fallback(category, limit)

    _cache_set(key, results)
    return results[:limit]


def _youtube_via_searchpython(region: str, category: str, limit: int) -> list[dict]:
    try:
        from youtubesearchpython import Trending
        t = Trending()
        raw = t.get_trending_videos(count=limit)
        if not raw:
            return []
        out = []
        for v in raw:
            out.append({
                "id": v.get("id", ""),
                "title": v.get("title", ""),
                "channel": v.get("channel", {}).get("name", ""),
                "views": v.get("viewCount", {}).get("short", ""),
                "duration": v.get("duration", ""),
                "published": v.get("publishedTime", ""),
                "category": v.get("category", ""),
                "tags": [],
                "source": "youtube",
            })
        return out
    except Exception:
        return []


def _youtube_via_api(region: str, category: str, limit: int) -> list[dict]:
    api_key = os.environ.get("YOUTUBE_API_KEY") or _load_config().get("youtube_api_key")
    if not api_key:
        return []
    try:
        import requests
        cat_map = {
            "music": "10", "gaming": "20", "news": "25",
            "sports": "17", "entertainment": "24", "science": "28",
            "tech": "28", "all": "0",
        }
        cat_id = cat_map.get(category.lower(), "0")
        params = {
            "part": "snippet,statistics",
            "chart": "mostPopular",
            "regionCode": region,
            "maxResults": min(limit, 50),
            "key": api_key,
        }
        if cat_id != "0":
            params["videoCategoryId"] = cat_id
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params=params, timeout=10
        )
        if resp.status_code != 200:
            return []
        items = resp.json().get("items", [])
        out = []
        for item in items:
            snip = item.get("snippet", {})
            stats = item.get("statistics", {})
            out.append({
                "id": item.get("id", ""),
                "title": snip.get("title", ""),
                "channel": snip.get("channelTitle", ""),
                "views": stats.get("viewCount", "0"),
                "likes": stats.get("likeCount", "0"),
                "comments": stats.get("commentCount", "0"),
                "duration": "",
                "published": snip.get("publishedAt", "")[:10],
                "category": snip.get("categoryId", ""),
                "tags": snip.get("tags", [])[:10],
                "source": "youtube_api",
            })
        return out
    except Exception:
        return []


def _youtube_fallback(category: str, limit: int) -> list[dict]:
    """Curated snapshot of typical YouTube trending content by category."""
    templates = {
        "music": [
            {"title": "Official Music Video - Latest Pop Hit", "channel": "VEVO", "views": "12M", "tags": ["music", "pop", "newmusic"]},
            {"title": "Viral Dance Challenge - Original Audio", "channel": "DanceChannel", "views": "8M", "tags": ["dance", "viral", "challenge"]},
            {"title": "Chill Lofi Hip Hop - Study Beats 24/7", "channel": "LofiGirl", "views": "5M", "tags": ["lofi", "study", "chill"]},
            {"title": "Top 50 Songs This Week 2025 - Billboard Hot 100", "channel": "ChartTV", "views": "3M", "tags": ["top50", "billboard", "2025"]},
        ],
        "gaming": [
            {"title": "I Beat the Impossible Challenge", "channel": "TopGamer", "views": "9M", "tags": ["gaming", "challenge", "minecraft"]},
            {"title": "New Season Update - Everything You Need to Know", "channel": "GameNews", "views": "6M", "tags": ["gaming", "update", "newseason"]},
            {"title": "Unboxing the Most Expensive Gaming Setup", "channel": "TechGamer", "views": "4M", "tags": ["gaming", "setup", "unboxing"]},
        ],
        "all": [
            {"title": "I Spent 24 Hours in the World's Tallest Building", "channel": "ViralVlogs", "views": "15M", "tags": ["viral", "challenge", "24hours"]},
            {"title": "I Tried Every Menu Item at McDonald's", "channel": "FoodReviewer", "views": "11M", "tags": ["food", "mcdonalds", "review"]},
            {"title": "Watch This Before You Buy a House in 2025", "channel": "FinanceHub", "views": "9M", "tags": ["finance", "realestate", "2025"]},
            {"title": "I Lost 30 lbs in 90 Days - Full Transformation", "channel": "FitnessJourney", "views": "7M", "tags": ["fitness", "transformation", "weightloss"]},
            {"title": "This AI Tool Will Change Everything", "channel": "TechExplained", "views": "6M", "tags": ["AI", "tech", "future"]},
        ],
    }
    pool = templates.get(category.lower(), templates["all"])
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    results = []
    for i, item in enumerate(pool[:limit]):
        results.append({
            "id": f"fallback_{i}",
            "title": item["title"],
            "channel": item["channel"],
            "views": item["views"],
            "likes": "",
            "duration": "",
            "published": now,
            "category": category,
            "tags": item.get("tags", []),
            "source": "curated",
        })
    return results


# ── TikTok ────────────────────────────────────────────────────────────────────

def fetch_tiktok_trending_hashtags(limit: int = 30) -> list[dict]:
    key = _cache_key("tt_hashtags", limit=limit)
    cached = _cache_get(key)
    if cached:
        return cached[:limit]

    results = _tiktok_via_pyktok(limit)
    if not results:
        results = _tiktok_hashtags_fallback(limit)

    _cache_set(key, results)
    return results[:limit]


def fetch_tiktok_trending_sounds(limit: int = 20) -> list[dict]:
    key = _cache_key("tt_sounds", limit=limit)
    cached = _cache_get(key)
    if cached:
        return cached[:limit]

    results = _tiktok_sounds_fallback(limit)
    _cache_set(key, results)
    return results[:limit]


def _tiktok_via_pyktok(limit: int) -> list[dict]:
    try:
        import pyktok as pyk
        # pyktok fetches trending videos — extract hashtags from them
        browser = os.environ.get("PYKTOK_BROWSER", "chrome")
        pyk.specify_browser(browser)
        raw = pyk.get_trending_videos()
        if not raw:
            return []
        tag_counts: dict[str, int] = {}
        for video in raw:
            for tag in video.get("textExtra", []):
                ht = tag.get("hashtagName", "")
                if ht:
                    tag_counts[ht] = tag_counts.get(ht, 0) + 1
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return [
            {"tag": f"#{t}", "name": t, "post_count": "", "rank": i + 1, "source": "tiktok"}
            for i, (t, _) in enumerate(sorted_tags[:limit])
        ]
    except Exception:
        return []


def _tiktok_hashtags_fallback(limit: int) -> list[dict]:
    tags = [
        ("fyp", "For You Page", "500B+"),
        ("foryou", "For You", "400B+"),
        ("viral", "Viral", "300B+"),
        ("trending", "Trending", "200B+"),
        ("foryoupage", "For You Page", "150B+"),
        ("tiktok", "TikTok", "100B+"),
        ("funny", "Funny", "80B+"),
        ("dance", "Dance", "70B+"),
        ("love", "Love", "65B+"),
        ("music", "Music", "60B+"),
        ("comedy", "Comedy", "55B+"),
        ("food", "Food", "50B+"),
        ("fitness", "Fitness", "45B+"),
        ("fashion", "Fashion", "40B+"),
        ("beauty", "Beauty", "38B+"),
        ("travel", "Travel", "35B+"),
        ("motivation", "Motivation", "30B+"),
        ("business", "Business", "28B+"),
        ("money", "Money", "25B+"),
        ("skincare", "Skincare", "22B+"),
        ("workout", "Workout", "20B+"),
        ("recipe", "Recipe", "18B+"),
        ("aesthetic", "Aesthetic", "16B+"),
        ("satisfying", "Satisfying", "15B+"),
        ("diy", "DIY", "14B+"),
        ("storytime", "Story Time", "13B+"),
        ("vlog", "Vlog", "12B+"),
        ("pov", "Point of View", "11B+"),
        ("grwm", "Get Ready With Me", "10B+"),
        ("greenscreen", "Green Screen", "9B+"),
    ]
    return [
        {"tag": f"#{t}", "name": t, "post_count": count, "rank": i + 1, "source": "curated"}
        for i, (t, _, count) in enumerate(tags[:limit])
    ]


def _tiktok_sounds_fallback(limit: int) -> list[dict]:
    sounds = [
        {"title": "Espresso", "artist": "Sabrina Carpenter", "uses": "15M+", "genre": "Pop"},
        {"title": "APT.", "artist": "ROSÉ & Bruno Mars", "uses": "12M+", "genre": "Pop"},
        {"title": "luther", "artist": "Kendrick Lamar & SZA", "uses": "10M+", "genre": "R&B"},
        {"title": "Die With A Smile", "artist": "Lady Gaga & Bruno Mars", "uses": "9M+", "genre": "Pop"},
        {"title": "Birds of a Feather", "artist": "Billie Eilish", "uses": "8M+", "genre": "Indie Pop"},
        {"title": "original sound - motivational speech", "artist": "Various", "uses": "7M+", "genre": "Motivation"},
        {"title": "Hypnotize (sped up)", "artist": "Biggie", "uses": "6M+", "genre": "Hip Hop"},
        {"title": "CARNIVAL", "artist": "¥$, Kanye West & Ty Dolla $ign", "uses": "5M+", "genre": "Hip Hop"},
        {"title": "Bohemian Rhapsody (sped up)", "artist": "Queen", "uses": "4M+", "genre": "Rock"},
        {"title": "Calm Lo-Fi Beat", "artist": "LoFi Mix", "uses": "4M+", "genre": "Lo-Fi"},
        {"title": "I Like The Way You Kiss Me", "artist": "Artemas", "uses": "3.5M+", "genre": "Alt Pop"},
        {"title": "Good Luck, Babe!", "artist": "Chappell Roan", "uses": "3M+", "genre": "Pop"},
        {"title": "Six Feet Under", "artist": "Billie Eilish", "uses": "2.8M+", "genre": "Pop"},
        {"title": "Too Sweet", "artist": "Hozier", "uses": "2.5M+", "genre": "Folk Pop"},
        {"title": "Beautiful Things", "artist": "Benson Boone", "uses": "2.2M+", "genre": "Pop Rock"},
        {"title": "What Was I Made For?", "artist": "Billie Eilish", "uses": "2M+", "genre": "Pop"},
        {"title": "Water", "artist": "Tyla", "uses": "1.8M+", "genre": "Afropop"},
        {"title": "Hiss", "artist": "Megan Thee Stallion", "uses": "1.5M+", "genre": "Hip Hop"},
        {"title": "Snooze", "artist": "SZA", "uses": "1.3M+", "genre": "R&B"},
        {"title": "Flowers", "artist": "Miley Cyrus", "uses": "1.2M+", "genre": "Pop"},
    ]
    for i, s in enumerate(sounds):
        s["rank"] = i + 1
        s["source"] = "curated"
    return sounds[:limit]


# ── Config ────────────────────────────────────────────────────────────────────

_CONFIG_FILE = Path.home() / ".cli-anything-social-trends" / "config.json"


def load_config() -> dict:
    if not _CONFIG_FILE.exists():
        return {}
    try:
        with open(_CONFIG_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _load_config() -> dict:
    return load_config()


def save_config(cfg: dict) -> None:
    _CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


def get_api_key(opt: Optional[str] = None, service: str = "youtube") -> Optional[str]:
    if opt:
        return opt
    env_map = {"youtube": "YOUTUBE_API_KEY", "tiktok": "TIKTOK_API_KEY"}
    env_key = os.environ.get(env_map.get(service, ""))
    if env_key:
        return env_key
    return load_config().get(f"{service}_api_key")


# ── Niche hashtag database ────────────────────────────────────────────────────

NICHE_HASHTAGS: dict[str, dict[str, list[str]]] = {
    "fitness": {
        "mega":   ["#fitness", "#workout", "#gym", "#health", "#fitlife"],
        "large":  ["#fitnessmotivation", "#workoutmotivation", "#bodybuilding", "#weightloss", "#healthylifestyle"],
        "medium": ["#gymlife", "#fitnessjourney", "#personaltrainer", "#strengthtraining", "#cardio"],
        "niche":  ["#homeworkout", "#calisthenics", "#crossfit", "#functionalfitness", "#progressovertime"],
    },
    "food": {
        "mega":   ["#food", "#foodie", "#cooking", "#recipe", "#yummy"],
        "large":  ["#foodphotography", "#homecooking", "#healthyfood", "#foodlover", "#delicious"],
        "medium": ["#mealprep", "#foodblogger", "#instafood", "#dinnerrecipes", "#easyrecipes"],
        "niche":  ["#glutenfree", "#veganrecipes", "#keto", "#airfryer", "#5ingredientmeals"],
    },
    "fashion": {
        "mega":   ["#fashion", "#style", "#ootd", "#outfit", "#clothing"],
        "large":  ["#fashionblogger", "#streetstyle", "#fashionista", "#outfitoftheday", "#styleinspo"],
        "medium": ["#womensfashion", "#mensfashion", "#fashiontrends", "#casualstyle", "#aestheticoutfit"],
        "niche":  ["#thriftedoutfit", "#capsulewardrobe", "#cottagecore", "#darkacademia", "#y2kfashion"],
    },
    "travel": {
        "mega":   ["#travel", "#wanderlust", "#vacation", "#adventure", "#explore"],
        "large":  ["#travelblogger", "#travelgram", "#traveling", "#travelphotography", "#traveltips"],
        "medium": ["#solotravel", "#budgettravel", "#roadtrip", "#backpacking", "#luxurytravel"],
        "niche":  ["#hiddengems", "#digitalnomaд", "#vanlife", "#travelitinerary", "#travelhacks"],
    },
    "finance": {
        "mega":   ["#money", "#finance", "#investing", "#wealth", "#financialfreedom"],
        "large":  ["#personalfinance", "#investing101", "#stockmarket", "#passiveincome", "#budgeting"],
        "medium": ["#moneytips", "#financialliteracy", "#buildingwealth", "#savingmoney", "#entrepreneur"],
        "niche":  ["#dividendinvesting", "#realestateinvesting", "#sidehustle", "#frugalliving", "#FIRE"],
    },
    "motivation": {
        "mega":   ["#motivation", "#mindset", "#success", "#inspiration", "#goals"],
        "large":  ["#motivationalquotes", "#personaldevelopment", "#selfimprovement", "#positivity", "#mindfulness"],
        "medium": ["#growthmindset", "#dailymotivation", "#successmindset", "#levelup", "#discipline"],
        "niche":  ["#morningroutine", "#stoicism", "#atomichabits", "#deepwork", "#intentionalliving"],
    },
    "beauty": {
        "mega":   ["#beauty", "#makeup", "#skincare", "#cosmetics", "#glam"],
        "large":  ["#makeupartist", "#makeuptutorial", "#skincareroutine", "#naturalmakeup", "#beautytips"],
        "medium": ["#drugstorebeauty", "#cleanbeauty", "#grwm", "#nofilter", "#beautyhacks"],
        "niche":  ["#dewyskim", "#slugging", "#glassskim", "#koreanbeauty", "#acneprone"],
    },
    "gaming": {
        "mega":   ["#gaming", "#gamer", "#games", "#videogames", "#gamingcommunity"],
        "large":  ["#twitch", "#gamingclips", "#gaminglife", "#pcgaming", "#consolegaming"],
        "medium": ["#gamingsetup", "#fps", "#rpg", "#streamer", "#esports"],
        "niche":  ["#indiegames", "#retrogaming", "#cozy games", "#gamedev", "#soulslike"],
    },
    "music": {
        "mega":   ["#music", "#newmusic", "#song", "#artist", "#musician"],
        "large":  ["#hiphop", "#rnb", "#pop", "#indie", "#musicvideo"],
        "medium": ["#producer", "#beatmaker", "#singersongwriter", "#musicproducer", "#newartist"],
        "niche":  ["#undergroundmusic", "#lofi", "#alternativemusic", "#musicproduction", "#sounddesign"],
    },
    "business": {
        "mega":   ["#business", "#entrepreneur", "#startup", "#marketing", "#success"],
        "large":  ["#smallbusiness", "#businessowner", "#entrepreneurship", "#digitalmarketing", "#branding"],
        "medium": ["#ecommerce", "#contentcreator", "#growthhacking", "#businesstips", "#onlinebusiness"],
        "niche":  ["#dropshipping", "#smma", "#freelancing", "#saas", "#productlaunch"],
    },
    "pets": {
        "mega":   ["#pets", "#dogs", "#cats", "#animals", "#dogsofinstagram"],
        "large":  ["#puppy", "#kitten", "#petlover", "#dogsofig", "#animallover"],
        "medium": ["#dogtraining", "#adoptdontshop", "#rescuedog", "#catlover", "#petcare"],
        "niche":  ["#dogmom", "#catdad", "#zoomies", "#petsoftiktok", "#petblogger"],
    },
}


def get_niche_hashtags(niche: str) -> dict[str, list[str]]:
    return NICHE_HASHTAGS.get(niche.lower(), NICHE_HASHTAGS.get("motivation", {}))


def list_niches() -> list[str]:
    return sorted(NICHE_HASHTAGS.keys())


# ── Posting time data ─────────────────────────────────────────────────────────

POSTING_TIMES: dict[str, dict[str, list[str]]] = {
    "tiktok": {
        "general":   ["6:00 AM–10:00 AM", "12:00 PM–3:00 PM", "7:00 PM–11:00 PM"],
        "fitness":   ["5:30 AM–7:30 AM", "12:00 PM–1:00 PM", "5:00 PM–7:00 PM"],
        "food":      ["11:00 AM–1:00 PM", "5:00 PM–7:00 PM", "8:00 PM–10:00 PM"],
        "finance":   ["7:00 AM–9:00 AM", "12:00 PM–2:00 PM", "6:00 PM–8:00 PM"],
        "fashion":   ["8:00 AM–10:00 AM", "2:00 PM–4:00 PM", "7:00 PM–10:00 PM"],
        "motivation":["6:00 AM–8:00 AM", "12:00 PM–1:00 PM", "9:00 PM–11:00 PM"],
    },
    "instagram": {
        "general":   ["6:00 AM–9:00 AM", "12:00 PM–2:00 PM", "5:00 PM–8:00 PM"],
        "fitness":   ["6:00 AM–8:00 AM", "5:00 PM–7:00 PM"],
        "food":      ["10:00 AM–1:00 PM", "6:00 PM–9:00 PM"],
        "finance":   ["8:00 AM–10:00 AM", "6:00 PM–8:00 PM"],
        "fashion":   ["8:00 AM–11:00 AM", "1:00 PM–3:00 PM", "7:00 PM–9:00 PM"],
        "motivation":["7:00 AM–9:00 AM", "6:00 PM–9:00 PM"],
    },
    "youtube": {
        "general":   ["2:00 PM–4:00 PM (Fri–Sun)", "12:00 PM–3:00 PM (Weekdays)"],
        "gaming":    ["3:00 PM–6:00 PM", "9:00 PM–11:00 PM"],
        "education": ["10:00 AM–12:00 PM", "2:00 PM–4:00 PM"],
        "finance":   ["9:00 AM–11:00 AM", "6:00 PM–8:00 PM"],
    },
}


def get_posting_times(platform: str, niche: str) -> list[str]:
    plat = POSTING_TIMES.get(platform.lower(), POSTING_TIMES["tiktok"])
    return plat.get(niche.lower(), plat.get("general", []))
