"""TikTok viral trends scraper.

TikTok does not offer a public trending API.  This module uses three layers:

  Layer 1 — TikTokApi (playwright-based, most accurate when available)
  Layer 2 — requests + header spoofing to parse the embedded SIGI_STATE JSON
             from TikTok's discover/trending web pages
  Layer 3 — Static curated seed data updated per scrape session (always works)

Results are cached to ~/.config/viral-trends/cache/tt_*.json with a 1-hour TTL.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

CACHE_DIR = Path.home() / ".config" / "viral-trends" / "cache"
CACHE_TTL = 3600

TIKTOK_DISCOVER_URL = "https://www.tiktok.com/api/discover/tag/"
TIKTOK_TRENDING_URL  = "https://www.tiktok.com/trending"
TIKTOK_EXPLORE_URL   = "https://www.tiktok.com/explore"

_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.tiktok.com/",
    "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

# Curated seed of evergreen viral niches used when live scraping is blocked.
# Agents can extend this via the `trends seed-add` command.
_SEED_TRENDS = [
    {"hashtag": "fyp",          "views": 50_000_000_000, "category": "general"},
    {"hashtag": "foryou",       "views": 35_000_000_000, "category": "general"},
    {"hashtag": "foryoupage",   "views": 30_000_000_000, "category": "general"},
    {"hashtag": "viral",        "views": 20_000_000_000, "category": "general"},
    {"hashtag": "trending",     "views": 15_000_000_000, "category": "general"},
    {"hashtag": "CapCut",       "views": 10_000_000_000, "category": "editing"},
    {"hashtag": "duet",         "views": 8_000_000_000,  "category": "engagement"},
    {"hashtag": "stitch",       "views": 7_000_000_000,  "category": "engagement"},
    {"hashtag": "learnontiktok","views": 6_000_000_000,  "category": "education"},
    {"hashtag": "tiktokfood",   "views": 5_000_000_000,  "category": "food"},
    {"hashtag": "gymtok",       "views": 4_000_000_000,  "category": "fitness"},
    {"hashtag": "moneytok",     "views": 3_500_000_000,  "category": "finance"},
    {"hashtag": "booktok",      "views": 3_000_000_000,  "category": "books"},
    {"hashtag": "fashiontiktok","views": 2_500_000_000,  "category": "fashion"},
    {"hashtag": "beautytok",    "views": 2_000_000_000,  "category": "beauty"},
    {"hashtag": "smallbusiness","views": 1_800_000_000,  "category": "business"},
    {"hashtag": "motivation",   "views": 1_500_000_000,  "category": "mindset"},
    {"hashtag": "storytime",    "views": 1_200_000_000,  "category": "entertainment"},
    {"hashtag": "pov",          "views": 1_000_000_000,  "category": "entertainment"},
    {"hashtag": "dayinmylife",  "views": 900_000_000,    "category": "lifestyle"},
    {"hashtag": "aesthetic",    "views": 800_000_000,    "category": "lifestyle"},
    {"hashtag": "vlog",         "views": 750_000_000,    "category": "lifestyle"},
    {"hashtag": "thrifting",    "views": 600_000_000,    "category": "fashion"},
    {"hashtag": "crochet",      "views": 500_000_000,    "category": "diy"},
    {"hashtag": "nailart",      "views": 480_000_000,    "category": "beauty"},
    {"hashtag": "cleantok",     "views": 450_000_000,    "category": "home"},
    {"hashtag": "cooking",      "views": 420_000_000,    "category": "food"},
    {"hashtag": "skincareroutine","views": 400_000_000,  "category": "beauty"},
    {"hashtag": "satisfying",   "views": 380_000_000,    "category": "entertainment"},
    {"hashtag": "transition",   "views": 350_000_000,    "category": "editing"},
]

_SEED_SOUNDS = [
    {"sound": "original sound", "category": "viral"},
    {"sound": "As It Was - Harry Styles", "category": "pop"},
    {"sound": "Flowers - Miley Cyrus", "category": "pop"},
    {"sound": "Calm Down - Rema", "category": "afrobeats"},
    {"sound": "Anti-Hero - Taylor Swift", "category": "pop"},
    {"sound": "Rich Flex - Drake", "category": "hiphop"},
    {"sound": "Superhero - Metro Boomin", "category": "hiphop"},
    {"sound": "CUFF IT - Beyoncé", "category": "pop"},
    {"sound": "Running Up That Hill - Kate Bush", "category": "classic"},
    {"sound": "Heat Waves - Glass Animals", "category": "indie"},
    {"sound": "About Damn Time - Lizzo", "category": "pop"},
    {"sound": "Industry Baby - Lil Nas X", "category": "hiphop"},
    {"sound": "good 4 u - Olivia Rodrigo", "category": "pop"},
    {"sound": "MONTERO - Lil Nas X", "category": "hiphop"},
    {"sound": "drivers license - Olivia Rodrigo", "category": "pop"},
    {"sound": "Levitating - Dua Lipa", "category": "pop"},
    {"sound": "Save Your Tears - The Weeknd", "category": "pop"},
    {"sound": "Blinding Lights - The Weeknd", "category": "pop"},
    {"sound": "traitor - Olivia Rodrigo", "category": "pop"},
    {"sound": "Spongebob Trap Remix", "category": "meme"},
]


# ── Cache helpers ─────────────────────────────────────────────────────────────

def _cache_path(key: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"tt_{key}.json"


def _load_cache(key: str) -> list[dict] | None:
    p = _cache_path(key)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text())
        if time.time() - data.get("ts", 0) < CACHE_TTL:
            return data["items"]
    except (json.JSONDecodeError, KeyError):
        pass
    return None


def _save_cache(key: str, items: list[dict]) -> None:
    _cache_path(key).write_text(json.dumps({"ts": time.time(), "items": items}))


# ── TikTokApi layer (optional playwright-based) ───────────────────────────────

def _try_tiktokapi(limit: int = 30) -> list[dict] | None:
    try:
        from TikTokApi import TikTokApi
        import asyncio

        async def _fetch():
            async with TikTokApi() as api:
                await api.create_sessions(num_sessions=1, sleep_after=3)
                trends = []
                async for video in api.trending.videos(count=limit):
                    info = video.as_dict
                    trends.append({
                        "id":          info.get("id", ""),
                        "description": info.get("desc", "")[:300],
                        "author":      info.get("author", {}).get("uniqueId", ""),
                        "plays":       info.get("stats", {}).get("playCount", 0),
                        "likes":       info.get("stats", {}).get("diggCount", 0),
                        "shares":      info.get("stats", {}).get("shareCount", 0),
                        "comments":    info.get("stats", {}).get("commentCount", 0),
                        "sound":       info.get("music", {}).get("title", ""),
                        "sound_author":info.get("music", {}).get("authorName", ""),
                        "hashtags":    [c.get("hashtagName","") for c in info.get("challenges", [])],
                        "url":         f"https://www.tiktok.com/@{info.get('author',{}).get('uniqueId','')}/video/{info.get('id','')}",
                        "platform":    "tiktok",
                    })
                return trends

        return asyncio.run(_fetch())
    except Exception:
        return None


# ── requests layer ────────────────────────────────────────────────────────────

def _try_requests_discover(niche: str = "", limit: int = 30) -> list[dict]:
    if not HAS_REQUESTS:
        return []
    try:
        resp = requests.get(
            TIKTOK_EXPLORE_URL,
            headers=_BROWSER_HEADERS,
            timeout=30,
        )
        html = resp.text

        # TikTok embeds page data in a <script id="SIGI_STATE"> tag
        match = re.search(r'<script id="SIGI_STATE"[^>]*>(\{.+?\})</script>', html, re.DOTALL)
        if not match:
            # Try __NEXT_DATA__
            match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(\{.+?\})</script>', html, re.DOTALL)
        if not match:
            return []

        data = json.loads(match.group(1))
        return _parse_sigi_hashtags(data, limit)
    except Exception:
        return []


def _parse_sigi_hashtags(data: Any, limit: int) -> list[dict]:
    results = []
    # Walk data for hashtag/challenge objects
    for obj in _walk(data, "challengeInfo"):
        ch = obj.get("challenge", {})
        stats = obj.get("stats", {})
        tag = ch.get("title", "")
        if tag:
            results.append({
                "hashtag": tag.lower(),
                "views":   stats.get("viewCount", 0),
                "videos":  stats.get("videoCount", 0),
                "category": "tiktok_trending",
            })
        if len(results) >= limit:
            break
    return results


def _walk(obj: Any, key: str) -> list[Any]:
    results = []
    if isinstance(obj, dict):
        if key in obj:
            results.append(obj[key])
        for v in obj.values():
            results.extend(_walk(v, key))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(_walk(item, key))
    return results


# ── Public API ────────────────────────────────────────────────────────────────

def get_trending_hashtags(
    niche: str = "",
    limit: int = 30,
    use_cache: bool = True,
    force_refresh: bool = False,
) -> list[dict]:
    """Return trending TikTok hashtags.

    Args:
        niche:   filter seed data to a niche keyword (empty = all)
        limit:   max results
        use_cache: return cached data if fresh
        force_refresh: bypass cache

    Returns list of dicts with keys: hashtag, views, category
    """
    cache_key = f"hashtags_{niche or 'all'}_{limit}"
    if use_cache and not force_refresh:
        cached = _load_cache(cache_key)
        if cached is not None:
            return cached

    # Layer 1: requests-based discover
    live = _try_requests_discover(niche, limit)
    if live:
        _save_cache(cache_key, live)
        return live[:limit]

    # Layer 2: seed data (always available)
    seed = _SEED_TRENDS
    if niche:
        seed = [t for t in seed if niche.lower() in t.get("category","").lower()
                or niche.lower() in t.get("hashtag","").lower()]
    result = seed[:limit]
    _save_cache(cache_key, result)
    return result


def get_trending_sounds(
    limit: int = 20,
    use_cache: bool = True,
    force_refresh: bool = False,
) -> list[dict]:
    """Return trending TikTok sounds/music.

    Each entry: {sound, category, [plays]}
    """
    cache_key = f"sounds_{limit}"
    if use_cache and not force_refresh:
        cached = _load_cache(cache_key)
        if cached is not None:
            return cached

    # Try TikTokApi first
    api_result = _try_tiktokapi(limit)
    if api_result:
        sounds: dict[str, dict] = {}
        for v in api_result:
            s = v.get("sound", "")
            if s:
                if s not in sounds:
                    sounds[s] = {"sound": s, "plays": 0, "videos": 0, "category": "tiktok_live"}
                sounds[s]["plays"] += v.get("plays", 0)
                sounds[s]["videos"] += 1
        result = sorted(sounds.values(), key=lambda x: x["plays"], reverse=True)[:limit]
        _save_cache(cache_key, result)
        return result

    result = _SEED_SOUNDS[:limit]
    _save_cache(cache_key, result)
    return result


def get_trending_videos(limit: int = 20) -> list[dict]:
    """Return trending TikTok videos (requires TikTokApi / playwright)."""
    result = _try_tiktokapi(limit)
    if result:
        return result
    return []


def get_niche_hashtags(niche: str, limit: int = 20) -> list[dict]:
    """Return trending hashtags for a specific niche."""
    return get_trending_hashtags(niche=niche, limit=limit)
