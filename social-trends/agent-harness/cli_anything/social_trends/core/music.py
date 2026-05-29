"""Trending audio & music tracker for TikTok and YouTube."""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from cli_anything.social_trends.core.store import Store

# ── Mock trending music data ──────────────────────────────────────────────────

_TIKTOK_TRENDING_MUSIC: List[Dict[str, Any]] = [
    {"rank": 1,  "platform": "tiktok", "title": "Rich Girl",              "artist": "Gwen Stefani",     "genre": "pop",        "uses": "8.2M",  "bpm": 140, "duration": "0:29", "trending_since": "2025-05-01"},
    {"rank": 2,  "platform": "tiktok", "title": "Money Trees",            "artist": "Kendrick Lamar",   "genre": "hiphop",     "uses": "7.1M",  "bpm": 85,  "duration": "0:30", "trending_since": "2025-04-28"},
    {"rank": 3,  "platform": "tiktok", "title": "Golden Hour",            "artist": "JVKE",             "genre": "indie pop",  "uses": "6.4M",  "bpm": 120, "duration": "0:28", "trending_since": "2025-05-05"},
    {"rank": 4,  "platform": "tiktok", "title": "Lose Yourself",          "artist": "Eminem",           "genre": "hiphop",     "uses": "5.8M",  "bpm": 171, "duration": "0:30", "trending_since": "2025-05-10"},
    {"rank": 5,  "platform": "tiktok", "title": "Eye of the Tiger",       "artist": "Survivor",         "genre": "rock",       "uses": "5.2M",  "bpm": 109, "duration": "0:27", "trending_since": "2025-05-08"},
    {"rank": 6,  "platform": "tiktok", "title": "Enchanted",              "artist": "Taylor Swift",     "genre": "pop",        "uses": "4.9M",  "bpm": 129, "duration": "0:30", "trending_since": "2025-05-03"},
    {"rank": 7,  "platform": "tiktok", "title": "INDUSTRY BABY",          "artist": "Lil Nas X",        "genre": "pop rap",    "uses": "4.5M",  "bpm": 149, "duration": "0:28", "trending_since": "2025-05-12"},
    {"rank": 8,  "platform": "tiktok", "title": "Money",                  "artist": "Pink Floyd",       "genre": "rock",       "uses": "4.2M",  "bpm": 121, "duration": "0:30", "trending_since": "2025-05-06"},
    {"rank": 9,  "platform": "tiktok", "title": "Levitating",             "artist": "Dua Lipa",         "genre": "dance pop",  "uses": "3.9M",  "bpm": 103, "duration": "0:29", "trending_since": "2025-05-14"},
    {"rank": 10, "platform": "tiktok", "title": "Started From the Bottom", "artist": "Drake",           "genre": "hiphop",     "uses": "3.7M",  "bpm": 80,  "duration": "0:28", "trending_since": "2025-05-09"},
    {"rank": 11, "platform": "tiktok", "title": "STAY",                   "artist": "The Kid LAROI",    "genre": "pop",        "uses": "3.4M",  "bpm": 170, "duration": "0:27", "trending_since": "2025-05-15"},
    {"rank": 12, "platform": "tiktok", "title": "Heat Waves",             "artist": "Glass Animals",    "genre": "indie pop",  "uses": "3.1M",  "bpm": 80,  "duration": "0:30", "trending_since": "2025-05-11"},
    {"rank": 13, "platform": "tiktok", "title": "Blinding Lights",        "artist": "The Weeknd",       "genre": "synth pop",  "uses": "2.9M",  "bpm": 171, "duration": "0:28", "trending_since": "2025-05-02"},
    {"rank": 14, "platform": "tiktok", "title": "Sunflower",              "artist": "Post Malone",      "genre": "pop rap",    "uses": "2.7M",  "bpm": 90,  "duration": "0:30", "trending_since": "2025-05-07"},
    {"rank": 15, "platform": "tiktok", "title": "As It Was",              "artist": "Harry Styles",     "genre": "pop",        "uses": "2.5M",  "bpm": 174, "duration": "0:29", "trending_since": "2025-05-13"},
]

_YOUTUBE_TRENDING_MUSIC: List[Dict[str, Any]] = [
    {"rank": 1,  "platform": "youtube", "title": "APT.",                       "artist": "ROSÉ & Bruno Mars",    "genre": "pop",        "views": "580M", "duration": "2:57", "trending_since": "2025-04-20"},
    {"rank": 2,  "platform": "youtube", "title": "Die With A Smile",           "artist": "Lady Gaga & Bruno Mars","genre": "pop",        "views": "420M", "duration": "4:10", "trending_since": "2025-04-15"},
    {"rank": 3,  "platform": "youtube", "title": "Espresso",                   "artist": "Sabrina Carpenter",    "genre": "pop",        "views": "390M", "duration": "2:55", "trending_since": "2025-04-18"},
    {"rank": 4,  "platform": "youtube", "title": "Not Like Us",                "artist": "Kendrick Lamar",       "genre": "hiphop",     "views": "360M", "duration": "4:34", "trending_since": "2025-04-22"},
    {"rank": 5,  "platform": "youtube", "title": "Cruel Summer",               "artist": "Taylor Swift",         "genre": "pop",        "views": "320M", "duration": "2:58", "trending_since": "2025-04-25"},
    {"rank": 6,  "platform": "youtube", "title": "Beautiful Things",           "artist": "Benson Boone",         "genre": "pop rock",   "views": "280M", "duration": "3:13", "trending_since": "2025-04-28"},
    {"rank": 7,  "platform": "youtube", "title": "Stick Season",               "artist": "Noah Kahan",           "genre": "folk pop",   "views": "245M", "duration": "3:24", "trending_since": "2025-05-01"},
    {"rank": 8,  "platform": "youtube", "title": "Flowers",                    "artist": "Miley Cyrus",          "genre": "pop",        "views": "220M", "duration": "3:21", "trending_since": "2025-05-03"},
    {"rank": 9,  "platform": "youtube", "title": "Calm Down",                  "artist": "Rema",                 "genre": "afrobeats",  "views": "195M", "duration": "3:38", "trending_since": "2025-05-05"},
    {"rank": 10, "platform": "youtube", "title": "Cupid (Twin Ver.)",          "artist": "FIFTY FIFTY",          "genre": "k-pop",      "views": "175M", "duration": "2:37", "trending_since": "2025-05-07"},
]


def _try_fetch_tiktok_music(limit: int, genre: Optional[str]) -> List[Dict[str, Any]]:
    token = os.environ.get("TIKTOK_API_TOKEN")
    if not token:
        return []
    try:
        import requests  # type: ignore
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        resp = requests.post(
            "https://open.tiktokapis.com/v2/research/music/trending/",
            headers=headers,
            json={"region_code": "US", "max_count": min(limit, 20)},
            timeout=15,
        )
        resp.raise_for_status()
        tracks = resp.json().get("data", {}).get("music_list", [])
        results = []
        for idx, t in enumerate(tracks[:limit], 1):
            results.append({
                "rank": idx,
                "platform": "tiktok",
                "title": t.get("title", ""),
                "artist": t.get("author", ""),
                "genre": genre or "unknown",
                "uses": str(t.get("use_count", 0)),
                "bpm": t.get("bpm", 0),
                "duration": t.get("duration", ""),
                "trending_since": t.get("create_time", ""),
                "source": "live",
            })
        return results
    except Exception:
        return []


def fetch_music(
    store: Store,
    platform: str = "both",
    genre: Optional[str] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    if platform in ("tiktok", "both"):
        live = _try_fetch_tiktok_music(limit, genre)
        if not live:
            raw = _TIKTOK_TRENDING_MUSIC
            if genre:
                raw = [m for m in raw if genre.lower() in m["genre"].lower()] or raw
            live = [dict(m, source="mock") for m in raw[:limit]]
        results.extend(live)

    if platform in ("youtube", "both"):
        raw = _YOUTUBE_TRENDING_MUSIC
        if genre:
            raw = [m for m in raw if genre.lower() in m["genre"].lower()] or raw
        results.extend([dict(m, source="mock") for m in raw[:limit]])

    for i, m in enumerate(results):
        if "id" not in m:
            m["id"] = f"music{i}"
        if "fetched_at" not in m:
            m["fetched_at"] = datetime.now().isoformat()

    store.music = results
    store.save()
    return results


def list_music(store: Store) -> List[Dict[str, Any]]:
    return store.music


def search_music(store: Store, query: str) -> List[Dict[str, Any]]:
    q = query.lower()
    return [
        m for m in store.music
        if q in m.get("title", "").lower() or q in m.get("artist", "").lower()
    ]


def export_music(store: Store, path: str) -> Dict[str, Any]:
    data = {"music": store.music, "exported_at": datetime.now().isoformat()}
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    return {"success": True, "path": path, "count": len(store.music)}
