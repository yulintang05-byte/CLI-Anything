"""YouTube & TikTok viral trend scraping with graceful mock fallback."""

import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from cli_anything.social_trends.core.store import Store

# ── Mock trend data ───────────────────────────────────────────────────────────

_YOUTUBE_MOCK: List[Dict[str, Any]] = [
    {"rank": 1,  "platform": "youtube", "title": "Mr. Beast's Extreme Challenge #100",    "views": "42M",  "hashtags": ["#MrBeast", "#challenge", "#viral"], "audio": None,           "category": "Entertainment", "url": "https://youtube.com/trending"},
    {"rank": 2,  "platform": "youtube", "title": "How I Made $1M in 30 Days (Step by Step)", "views": "18M", "hashtags": ["#finance", "#money", "#howto"], "audio": None,           "category": "Finance",       "url": "https://youtube.com/trending"},
    {"rank": 3,  "platform": "youtube", "title": "React JS Full Course 2025 — Zero to Hero",  "views": "9M",  "hashtags": ["#coding", "#webdev", "#react"], "audio": None,           "category": "Education",     "url": "https://youtube.com/trending"},
    {"rank": 4,  "platform": "youtube", "title": "Top 10 Travel Destinations You MUST Visit", "views": "7M",  "hashtags": ["#travel", "#wanderlust", "#explore"], "audio": None,      "category": "Travel",        "url": "https://youtube.com/trending"},
    {"rank": 5,  "platform": "youtube", "title": "Ultimate Home Workout — No Equipment Needed","views": "6M", "hashtags": ["#fitness", "#workout", "#health"], "audio": None,          "category": "Fitness",       "url": "https://youtube.com/trending"},
    {"rank": 6,  "platform": "youtube", "title": "World Record Speedrun — Under 2 Minutes",   "views": "5M",  "hashtags": ["#gaming", "#speedrun", "#world_record"], "audio": None,   "category": "Gaming",        "url": "https://youtube.com/trending"},
    {"rank": 7,  "platform": "youtube", "title": "Gordon Ramsay Makes the Perfect Pasta",     "views": "4M",  "hashtags": ["#food", "#cooking", "#recipe"], "audio": None,             "category": "Food",          "url": "https://youtube.com/trending"},
    {"rank": 8,  "platform": "youtube", "title": "Bitcoin 2025 — What Nobody Is Telling You", "views": "3M",  "hashtags": ["#crypto", "#bitcoin", "#investing"], "audio": None,       "category": "Crypto",        "url": "https://youtube.com/trending"},
    {"rank": 9,  "platform": "youtube", "title": "iPhone 18 Pro Hands-On Review",             "views": "3M",  "hashtags": ["#tech", "#apple", "#iphone"], "audio": None,              "category": "Tech",          "url": "https://youtube.com/trending"},
    {"rank": 10, "platform": "youtube", "title": "Luxury Apartment Tour — Dubai Penthouse",   "views": "2M",  "hashtags": ["#luxury", "#realestate", "#dubai"], "audio": None,        "category": "Luxury",        "url": "https://youtube.com/trending"},
]

_TIKTOK_MOCK: List[Dict[str, Any]] = [
    {"rank": 1,  "platform": "tiktok", "title": "POV: You're rich and nobody knows it",     "views": "80M",  "hashtags": ["#pov", "#rich", "#luxury", "#fyp"],       "audio": "Rich Girl - Gwen Stefani (sped up)", "category": "Luxury"},
    {"rank": 2,  "platform": "tiktok", "title": "Day in my life as a trader 💸",            "views": "55M",  "hashtags": ["#dayinmylife", "#trader", "#finance", "#fyp"], "audio": "Money Trees - Kendrick Lamar",     "category": "Finance"},
    {"rank": 3,  "platform": "tiktok", "title": "Calisthenics transformation 30 days",      "views": "48M",  "hashtags": ["#transformation", "#fitness", "#calisthenics", "#fyp"], "audio": "Eye of the Tiger - Survivor", "category": "Fitness"},
    {"rank": 4,  "platform": "tiktok", "title": "Aesthetic travel dump — Santorini 🇬🇷",    "views": "39M",  "hashtags": ["#travel", "#aesthetics", "#santorini", "#fyp"],  "audio": "Golden Hour - JVKE",             "category": "Travel"},
    {"rank": 5,  "platform": "tiktok", "title": "5 foods that changed my life",             "views": "33M",  "hashtags": ["#food", "#healthyfood", "#diet", "#fyp"],         "audio": "Levitating - Dua Lipa",          "category": "Food"},
    {"rank": 6,  "platform": "tiktok", "title": "Every gamer needs this setup 🎮",          "views": "28M",  "hashtags": ["#gaming", "#setup", "#pcmasterrace", "#fyp"],     "audio": "INDUSTRY BABY - Lil Nas X",      "category": "Gaming"},
    {"rank": 7,  "platform": "tiktok", "title": "Crypto explained in 60 seconds",           "views": "25M",  "hashtags": ["#crypto", "#bitcoin", "#blockchain", "#fyp"],     "audio": "Money - Pink Floyd",             "category": "Crypto"},
    {"rank": 8,  "platform": "tiktok", "title": "Outfit of the day — dark academia 🖤",     "views": "22M",  "hashtags": ["#ootd", "#fashion", "#darkacademia", "#fyp"],     "audio": "Enchanted - Taylor Swift",       "category": "Fashion"},
    {"rank": 9,  "platform": "tiktok", "title": "motivational speech compilation #1",       "views": "19M",  "hashtags": ["#motivation", "#mindset", "#success", "#fyp"],    "audio": "Lose Yourself - Eminem",         "category": "Motivational"},
    {"rank": 10, "platform": "tiktok", "title": "NBA highlight reel that broke the internet","views": "17M",  "hashtags": ["#nba", "#sports", "#basketball", "#fyp"],         "audio": "Started From the Bottom - Drake","category": "Sports"},
]


def _try_fetch_youtube(limit: int, category: Optional[str]) -> List[Dict[str, Any]]:
    """Attempt to scrape YouTube trending via yt-initial-data JSON embedded in HTML."""
    try:
        import requests  # type: ignore
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }
        resp = requests.get("https://www.youtube.com/feed/trending", headers=headers, timeout=10)
        resp.raise_for_status()

        match = re.search(r"var ytInitialData\s*=\s*(\{.+?\});\s*</script>", resp.text, re.DOTALL)
        if not match:
            return []

        data = json.loads(match.group(1))
        tabs = (
            data.get("contents", {})
            .get("twoColumnBrowseResultsRenderer", {})
            .get("tabs", [])
        )

        items = []
        for tab in tabs:
            contents = (
                tab.get("tabRenderer", {})
                .get("content", {})
                .get("sectionListRenderer", {})
                .get("contents", [])
            )
            for section in contents:
                items.extend(
                    section.get("itemSectionRenderer", {})
                    .get("contents", [{}])[0]
                    .get("shelfRenderer", {})
                    .get("content", {})
                    .get("expandedShelfContentsRenderer", {})
                    .get("items", [])
                )

        results = []
        for idx, item in enumerate(items[:limit], 1):
            vr = item.get("videoRenderer", {})
            if not vr:
                continue
            title = vr.get("title", {}).get("runs", [{}])[0].get("text", "")
            views_str = (
                vr.get("viewCountText", {}).get("simpleText", "")
                or vr.get("viewCountText", {}).get("runs", [{}])[0].get("text", "")
            )
            vid_id = vr.get("videoId", "")
            results.append({
                "rank": idx,
                "platform": "youtube",
                "title": title,
                "views": views_str,
                "hashtags": [],
                "audio": None,
                "category": category or "Trending",
                "url": f"https://youtube.com/watch?v={vid_id}",
                "source": "live",
            })
        return results

    except Exception:
        return []


def _try_fetch_tiktok(limit: int, category: Optional[str]) -> List[Dict[str, Any]]:
    """Attempt TikTok trending via Research API (TIKTOK_API_TOKEN env var required)."""
    token = os.environ.get("TIKTOK_API_TOKEN")
    if not token:
        return []
    try:
        import requests  # type: ignore
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        body: Dict[str, Any] = {
            "query": {"and": [{"operation": "EQ", "field_name": "region_code", "field_values": ["US"]}]},
            "max_count": min(limit, 20),
            "cursor": 0,
        }
        resp = requests.post(
            "https://open.tiktokapis.com/v2/video/query/",
            headers=headers,
            json=body,
            timeout=15,
        )
        resp.raise_for_status()
        videos = resp.json().get("data", {}).get("videos", [])
        results = []
        for idx, v in enumerate(videos[:limit], 1):
            results.append({
                "rank": idx,
                "platform": "tiktok",
                "title": v.get("video_description", ""),
                "views": str(v.get("view_count", 0)),
                "hashtags": [f"#{h}" for h in v.get("hashtag_names", [])],
                "audio": v.get("music_id", ""),
                "category": category or "Trending",
                "url": f"https://tiktok.com/@{v.get('username', '')}",
                "source": "live",
            })
        return results
    except Exception:
        return []


def fetch_trends(
    store: Store,
    platform: str = "both",
    category: Optional[str] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    if platform in ("youtube", "both"):
        yt = _try_fetch_youtube(limit, category)
        if not yt:
            raw = _YOUTUBE_MOCK
            if category:
                raw = [t for t in raw if t["category"].lower() == category.lower()] or raw
            yt = [dict(t, source="mock") for t in raw[:limit]]
        results.extend(yt)

    if platform in ("tiktok", "both"):
        tt = _try_fetch_tiktok(limit, category)
        if not tt:
            raw = _TIKTOK_MOCK
            if category:
                raw = [t for t in raw if t["category"].lower() == category.lower()] or raw
            tt = [dict(t, source="mock") for t in raw[:limit]]
        results.extend(tt)

    for i, t in enumerate(results):
        t["fetched_at"] = datetime.now().isoformat()
        if "id" not in t:
            t["id"] = f"trend{i}"

    store.trends = results
    store.save()
    return results


def list_trends(store: Store) -> List[Dict[str, Any]]:
    return store.trends


def search_trends(store: Store, keyword: str, platform: Optional[str] = None) -> List[Dict[str, Any]]:
    kw = keyword.lower()
    results = [
        t for t in store.trends
        if kw in t.get("title", "").lower()
        or any(kw in h.lower() for h in t.get("hashtags", []))
    ]
    if platform:
        results = [t for t in results if t.get("platform") == platform]
    return results


def export_trends(store: Store, path: str) -> Dict[str, Any]:
    data = {"trends": store.trends, "exported_at": datetime.now().isoformat()}
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    return {"success": True, "path": path, "count": len(store.trends)}
