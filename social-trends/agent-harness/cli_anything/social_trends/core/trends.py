"""Trend scraping and caching for YouTube and TikTok."""

import json
import os
import time
from datetime import datetime
from typing import Any

_CACHE_DIR = os.path.expanduser("~/.social-trends")
_CACHE_FILE = os.path.join(_CACHE_DIR, "trends_cache.json")

# Curated seed trends (updated May 2026) — used as fallback when live fetch fails
_SEED_TRENDS: dict[str, list[dict]] = {
    "tiktok": [
        {
            "id": "tt_001", "title": "Follow That Tune", "category": "music",
            "sound": "Madonna — Into The Groove (remix)",
            "description": "Dance trend using Madonna's Into The Groove viral remix",
            "hashtags": ["#followthattune", "#madonnachallenge", "#fyp", "#viral", "#dancechallenge"],
            "views_est": "2.8B", "peak_date": "2026-04", "status": "peaking",
        },
        {
            "id": "tt_002", "title": "Bridgerton Dance", "category": "dance",
            "sound": "Bridgerton Waltz — orchestral pop edit",
            "description": "Formal-to-casual outfit transformation with Bridgerton-style dance intro",
            "hashtags": ["#bridgerton", "#outfittransformation", "#fyp", "#dancechallenge", "#aesthetic"],
            "views_est": "1.4B", "peak_date": "2026-04", "status": "growing",
        },
        {
            "id": "tt_003", "title": "What Were You Like in the 90s?", "category": "nostalgia",
            "sound": "Various 90s throwback tracks",
            "description": "Throwback photo trend showing childhood/teen photos from the 90s",
            "hashtags": ["#90s", "#throwback", "#nostalgia", "#90skid", "#childhood", "#fyp"],
            "views_est": "900M", "peak_date": "2026-05", "status": "peaking",
        },
        {
            "id": "tt_004", "title": "Phonk Dance Challenge", "category": "dance",
            "sound": "Various Phonk tracks (DRIFT PHONK, Brazilian phonk)",
            "description": "High-energy phonk-driven dance challenge — replicable format drives mass participation",
            "hashtags": ["#phonk", "#phonkmusic", "#dancechallenge", "#fyp", "#viral", "#phonkdance"],
            "views_est": "3.1B", "peak_date": "2026-03", "status": "evergreen",
        },
        {
            "id": "tt_005", "title": "Emotional ROI Storytime", "category": "storytelling",
            "sound": "Soft cinematic background — no specific sound",
            "description": "Purchase-verification storytelling: creators share buying decisions TikTok influenced",
            "hashtags": ["#storytime", "#worthit", "#tiktokshop", "#review", "#fyp", "#honestreviews"],
            "views_est": "600M", "peak_date": "2026-05", "status": "growing",
        },
        {
            "id": "tt_006", "title": "Mini Egg Crunch Cake", "category": "food",
            "sound": "ASMR kitchen sounds",
            "description": "Viral recipe: chocolate cake + ganache + chocolate cornflakes + Mini Eggs",
            "hashtags": ["#minieggcake", "#viralrecipe", "#foodtiktok", "#baking", "#fyp", "#asmr"],
            "views_est": "450M", "peak_date": "2026-04", "status": "fading",
        },
        {
            "id": "tt_007", "title": "Slow-Living Morning Routine", "category": "lifestyle",
            "sound": "Lo-fi / ambient morning sounds",
            "description": "Cozy, unhurried morning routines — realism over aspirational perfection",
            "hashtags": ["#slowliving", "#morningroutine", "#cozy", "#minimalist", "#fyp", "#peaceful"],
            "views_est": "1.2B", "peak_date": "2026-05", "status": "peaking",
        },
        {
            "id": "tt_008", "title": "AI Side Hustle Reveal", "category": "business",
            "sound": "Money counting sound effect",
            "description": "Creators reveal AI-powered income streams with proof-of-earnings screenshots",
            "hashtags": ["#sidehustle", "#makemoneyonline", "#ai", "#passiveincome", "#fyp", "#entrepreneur"],
            "views_est": "800M", "peak_date": "2026-05", "status": "peaking",
        },
    ],
    "youtube": [
        {
            "id": "yt_001", "title": "Chaos Culture Compilations", "category": "entertainment",
            "description": "Rapid-fire compilation of chaotic, unhinged real-world moments",
            "hashtags": ["#viral", "#chaosculture", "#shorts", "#funny", "#compilation"],
            "views_est": "500M+/video", "peak_date": "2026-05", "status": "peaking",
        },
        {
            "id": "yt_002", "title": "Micro-Drama Storytelling (Shorts)", "category": "drama",
            "description": "60-second dramatic stories with cliffhangers — high retention, bingeable series",
            "hashtags": ["#shorts", "#drama", "#storytime", "#viral", "#series"],
            "views_est": "200M+/video", "peak_date": "2026-04", "status": "growing",
        },
        {
            "id": "yt_003", "title": "Nostalgic Edit Series", "category": "nostalgia",
            "description": "Aesthetic video essays revisiting 2000s-2010s pop culture with modern commentary",
            "hashtags": ["#nostalgia", "#2000s", "#aesthetic", "#vlog", "#memories"],
            "views_est": "50M+/video", "peak_date": "2026-05", "status": "peaking",
        },
        {
            "id": "yt_004", "title": "Current-Event Speed Explainers", "category": "news",
            "description": "Under-5-minute breakdowns of current events — heavy on graphics and pacing",
            "hashtags": ["#news", "#explained", "#shorts", "#trending", "#viral"],
            "views_est": "100M+/video", "peak_date": "2026-05", "status": "evergreen",
        },
        {
            "id": "yt_005", "title": "Personality-Led Education", "category": "education",
            "description": "Strong personal brand + entertaining teaching format — science, history, finance",
            "hashtags": ["#learnontiktok", "#education", "#science", "#history", "#finance"],
            "views_est": "75M+/video", "peak_date": "2026-04", "status": "growing",
        },
        {
            "id": "yt_006", "title": "Creator Swarm Campaigns", "category": "collab",
            "description": "Multiple creators simultaneously cover same topic/challenge — algorithmic surge",
            "hashtags": ["#collab", "#challenge", "#viral", "#trending", "#youtube"],
            "views_est": "300M+ combined", "peak_date": "2026-05", "status": "growing",
        },
        {
            "id": "yt_007", "title": "Sports Recap Shorts", "category": "sports",
            "description": "15-60 second highlight reels of viral sports moments with reaction overlay",
            "hashtags": ["#sports", "#shorts", "#viral", "#highlights", "#gaming"],
            "views_est": "150M+/video", "peak_date": "2026-05", "status": "evergreen",
        },
        {
            "id": "yt_008", "title": "Cozy Slow-Living Vlogs", "category": "lifestyle",
            "description": "Unfiltered, peaceful daily life content — cottage core, minimalism, nature",
            "hashtags": ["#slowliving", "#cozy", "#vlog", "#cottagecore", "#minimalist"],
            "views_est": "40M+/video", "peak_date": "2026-05", "status": "peaking",
        },
    ],
}


def _load_cache() -> dict:
    if os.path.exists(_CACHE_FILE):
        try:
            with open(_CACHE_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"fetched_at": None, "platforms": {}}


def _save_cache(cache: dict) -> None:
    os.makedirs(_CACHE_DIR, exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def _try_yt_dlp_trending(platform: str) -> list[dict]:
    """Attempt live fetch via yt-dlp. Returns [] on failure."""
    try:
        import subprocess
        if platform == "youtube":
            url = "https://www.youtube.com/feed/trending"
        else:
            return []

        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--dump-json", "--playlist-end", "20", url],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return []

        items = []
        for line in result.stdout.strip().splitlines():
            try:
                item = json.loads(line)
                items.append({
                    "id": f"yt_live_{item.get('id', '')}",
                    "title": item.get("title", ""),
                    "category": item.get("categories", ["unknown"])[0] if item.get("categories") else "unknown",
                    "description": item.get("description", "")[:120],
                    "hashtags": [f"#{t.replace(' ', '')}" for t in (item.get("tags") or [])[:5]],
                    "views_est": str(item.get("view_count", "unknown")),
                    "peak_date": datetime.now().strftime("%Y-%m"),
                    "status": "live",
                    "url": item.get("webpage_url", ""),
                })
            except (json.JSONDecodeError, KeyError):
                continue
        return items
    except (ImportError, FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return []


def fetch_trends(platform: str = "all", force: bool = False) -> dict[str, Any]:
    """Fetch trends for a platform. Uses cache (24h TTL) or live data."""
    cache = _load_cache()
    now = time.time()
    ttl = 86400  # 24 hours

    platforms = ["tiktok", "youtube"] if platform == "all" else [platform]
    result: dict[str, Any] = {"fetched_at": datetime.now().isoformat(), "sources": {}}

    for p in platforms:
        cached_ts = cache.get("platforms", {}).get(p, {}).get("fetched_at_ts", 0)
        if not force and (now - cached_ts) < ttl:
            result["sources"][p] = {"status": "cached", "count": len(cache["platforms"][p]["trends"])}
            continue

        live = _try_yt_dlp_trending(p)
        if live:
            trends = live
            source = "live"
        else:
            trends = _SEED_TRENDS.get(p, [])
            source = "seed"

        cache.setdefault("platforms", {})[p] = {
            "trends": trends,
            "fetched_at_ts": now,
            "fetched_at": datetime.now().isoformat(),
            "source": source,
        }
        result["sources"][p] = {"status": source, "count": len(trends)}

    _save_cache(cache)
    return result


def list_trends(platform: str = "all") -> list[dict]:
    """List cached trends. Fetches seed data if cache is empty."""
    cache = _load_cache()
    platforms = ["tiktok", "youtube"] if platform == "all" else [platform]

    output = []
    for p in platforms:
        plat_data = cache.get("platforms", {}).get(p, {})
        trends = plat_data.get("trends", _SEED_TRENDS.get(p, []))
        for t in trends:
            output.append({**t, "platform": p})
    return output


def show_trend(trend_id: str) -> dict:
    """Show detailed info about a specific trend."""
    for trend in list_trends():
        if trend.get("id") == trend_id:
            return trend
    raise ValueError(f"Trend '{trend_id}' not found. Run 'trends list' to see available IDs.")


def add_custom_trend(platform: str, title: str, category: str, description: str,
                     hashtags: list[str], sound: str = "") -> dict:
    """Add a manually observed trend to the local cache."""
    cache = _load_cache()
    existing = cache.get("platforms", {}).get(platform, {}).get("trends", list(_SEED_TRENDS.get(platform, [])))

    trend_id = f"{platform[:2]}_custom_{int(time.time())}"
    trend = {
        "id": trend_id,
        "title": title,
        "category": category,
        "description": description,
        "hashtags": hashtags,
        "sound": sound,
        "views_est": "tracking",
        "peak_date": datetime.now().strftime("%Y-%m"),
        "status": "tracking",
    }
    existing.append(trend)
    cache.setdefault("platforms", {})[platform] = {
        "trends": existing,
        "fetched_at_ts": cache.get("platforms", {}).get(platform, {}).get("fetched_at_ts", 0),
        "source": "mixed",
    }
    _save_cache(cache)
    return trend


def get_cache_info() -> dict:
    """Return metadata about the current cache state."""
    cache = _load_cache()
    info: dict[str, Any] = {"cache_file": _CACHE_FILE, "platforms": {}}
    for p, data in cache.get("platforms", {}).items():
        info["platforms"][p] = {
            "trend_count": len(data.get("trends", [])),
            "source": data.get("source", "unknown"),
            "fetched_at": data.get("fetched_at", "never"),
        }
    return info
