"""TikTok trends scraper — trending hashtags, sounds, and creators."""

import re
import json
import time
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional


_TT_BASE = "https://www.tiktok.com"
_TT_TRENDING_TAGS = "https://www.tiktok.com/api/explore/item_list/"
_TT_DISCOVER = "https://www.tiktok.com/discover"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.0 Mobile/15E148 Safari/604.1"
    ),
    "Referer": "https://www.tiktok.com/",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json, text/javascript, */*; q=0.01",
}


def _http_get(url: str, headers: Optional[dict] = None, timeout: int = 15) -> str:
    req_headers = dict(_HEADERS)
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


# ── TikTok trending hashtags (web scrape) ────────────────────────


def fetch_trending_hashtags(region: str = "US", max_results: int = 30) -> list[dict]:
    """Scrape TikTok's discover/trending page for top hashtags."""
    try:
        html = _http_get(f"{_TT_DISCOVER}?lang=en&region={region}")
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch TikTok discover page: {exc}") from exc

    hashtags = _parse_hashtags_from_html(html, max_results)
    if not hashtags:
        hashtags = _fallback_hashtags(region)
    return hashtags


def _parse_hashtags_from_html(html: str, max_results: int) -> list[dict]:
    """Extract hashtag data from TikTok page's __UNIVERSAL_DATA_FOR_REHYDRATION__."""
    # TikTok embeds page state in a script tag
    match = re.search(
        r'id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(\{.+?\})</script>',
        html,
        re.DOTALL,
    )
    if not match:
        return []

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return []

    results = []
    _walk_for_hashtags(data, results, max_results)
    return results[:max_results]


def _walk_for_hashtags(node, results: list, max_results: int):
    if len(results) >= max_results:
        return
    if isinstance(node, dict):
        # Look for challenge/hashtag objects
        if "title" in node and "stats" in node:
            stats = node.get("stats", {})
            if "videoCount" in stats or "viewCount" in stats:
                results.append({
                    "hashtag": "#" + node.get("title", "").lstrip("#"),
                    "video_count": stats.get("videoCount", 0),
                    "view_count": stats.get("viewCount", 0),
                    "description": node.get("desc", ""),
                })
                return
        for v in node.values():
            _walk_for_hashtags(v, results, max_results)
    elif isinstance(node, list):
        for item in node:
            _walk_for_hashtags(item, results, max_results)


def _fallback_hashtags(region: str) -> list[dict]:
    """Return well-known evergreen trending hashtags as a fallback."""
    base = [
        {"hashtag": "#fyp", "video_count": 0, "view_count": 0, "description": "For You Page — universal discovery tag"},
        {"hashtag": "#foryou", "video_count": 0, "view_count": 0, "description": "For You — broad reach"},
        {"hashtag": "#viral", "video_count": 0, "view_count": 0, "description": "Viral content tag"},
        {"hashtag": "#trending", "video_count": 0, "view_count": 0, "description": "Trending content"},
        {"hashtag": "#foryoupage", "video_count": 0, "view_count": 0, "description": "For You Page"},
        {"hashtag": "#tiktok", "video_count": 0, "view_count": 0, "description": "Platform tag"},
        {"hashtag": "#xyzbca", "video_count": 0, "view_count": 0, "description": "Algorithm trigger tag"},
        {"hashtag": "#explore", "video_count": 0, "view_count": 0, "description": "Explore tab tag"},
        {"hashtag": "#video", "video_count": 0, "view_count": 0, "description": "Generic video tag"},
        {"hashtag": "#creator", "video_count": 0, "view_count": 0, "description": "Creator community"},
    ]
    for item in base:
        item["note"] = "fallback — live scrape unavailable"
    return base


# ── TikTok trending sounds/music ─────────────────────────────────


def fetch_trending_sounds(region: str = "US", max_results: int = 20) -> list[dict]:
    """Scrape TikTok for currently trending sounds/music."""
    try:
        html = _http_get(f"{_TT_BASE}/music?lang=en")
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch TikTok music page: {exc}") from exc

    sounds = _parse_sounds_from_html(html, max_results)
    if not sounds:
        sounds = _fallback_sounds()
    return sounds


def _parse_sounds_from_html(html: str, max_results: int) -> list[dict]:
    match = re.search(
        r'id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(\{.+?\})</script>',
        html,
        re.DOTALL,
    )
    if not match:
        return []
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return []

    results: list[dict] = []
    _walk_for_sounds(data, results, max_results)
    return results[:max_results]


def _walk_for_sounds(node, results: list, max_results: int):
    if len(results) >= max_results:
        return
    if isinstance(node, dict):
        if "music" in node and isinstance(node["music"], dict):
            music = node["music"]
            if "title" in music and "authorName" in music:
                entry = {
                    "title": music.get("title", ""),
                    "artist": music.get("authorName", ""),
                    "id": music.get("id", ""),
                    "duration": music.get("duration", 0),
                    "cover": music.get("coverThumb", "") or music.get("coverMedium", ""),
                    "url": f"https://www.tiktok.com/music/{music.get('id', '')}",
                }
                if entry not in results:
                    results.append(entry)
                return
        for v in node.values():
            _walk_for_sounds(v, results, max_results)
    elif isinstance(node, list):
        for item in node:
            _walk_for_sounds(item, results, max_results)


def _fallback_sounds() -> list[dict]:
    return [
        {"title": "Unavailable — scrape blocked", "artist": "n/a", "id": "", "note": "Try with a session cookie"},
    ]


# ── Niche-specific trending tags ─────────────────────────────────


NICHE_HASHTAGS: dict[str, list[str]] = {
    "fitness": [
        "#fitness", "#gym", "#workout", "#fitnessmotivation", "#fitspo",
        "#bodybuilding", "#weightloss", "#healthylifestyle", "#personaltrainer",
        "#fitlife", "#gains", "#gymlife", "#cardio", "#strength", "#wellness",
    ],
    "beauty": [
        "#beauty", "#makeup", "#skincare", "#glam", "#makeuptutorial",
        "#grwm", "#skincareroutine", "#beautyadvice", "#GRWM", "#makeupartist",
        "#foundation", "#eyeshadow", "#lipstick", "#selfcare", "#glow",
    ],
    "food": [
        "#food", "#foodie", "#recipe", "#cooking", "#foodtok",
        "#easyrecipes", "#mealprep", "#homecooking", "#tasty", "#yummy",
        "#dinnerideas", "#lunchideas", "#healthyfood", "#snacks", "#dessert",
    ],
    "fashion": [
        "#fashion", "#ootd", "#style", "#outfit", "#fashiontiktok",
        "#outfitoftheday", "#streetstyle", "#fashionista", "#clothes", "#styling",
        "#fashiontrends", "#aesthetic", "#fashionblogger", "#lookbook", "#vintage",
    ],
    "finance": [
        "#finance", "#money", "#investing", "#personalfinance", "#financialliteracy",
        "#stocks", "#crypto", "#budgeting", "#savingmoney", "#debtfree",
        "#moneytips", "#wealthbuilding", "#passiveincome", "#sidehustle", "#entrepreneur",
    ],
    "travel": [
        "#travel", "#travelTikTok", "#wanderlust", "#explore", "#adventure",
        "#travelhacks", "#travelguide", "#vacation", "#travelwithme", "#roadtrip",
        "#backpacking", "#digitalnomad", "#traveltips", "#worldtravel", "#solo",
    ],
    "gaming": [
        "#gaming", "#gamer", "#videogames", "#gamingTikTok", "#gameplay",
        "#twitch", "#esports", "#streamer", "#xbox", "#playstation",
        "#pcgaming", "#mobilegaming", "#gamingreels", "#gamingcommunity", "#fps",
    ],
    "motivation": [
        "#motivation", "#mindset", "#success", "#grind", "#hustle",
        "#selfimprovement", "#personaldevelopment", "#productivity", "#goals", "#growth",
        "#positivity", "#inspiration", "#dailymotivation", "#entrepreneur", "#level up",
    ],
}


def get_niche_hashtags(niche: str, include_universal: bool = True) -> list[str]:
    """Get curated hashtags for a specific niche."""
    niche_tags = NICHE_HASHTAGS.get(niche.lower(), [])
    if include_universal:
        universal = ["#fyp", "#foryou", "#viral", "#trending", "#foryoupage"]
        # Mix: niche tags first, then fill with universal
        combined = niche_tags + [t for t in universal if t not in niche_tags]
        return combined
    return niche_tags


def list_niches() -> list[str]:
    return sorted(NICHE_HASHTAGS.keys())
