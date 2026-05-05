"""TikTok viral trends scraper — no API key required.

Pulls trending hashtags, sounds/music, and topics from TikTok's
public discovery endpoints. Uses multiple strategies with graceful fallback.
"""

from __future__ import annotations

import json
import re
import urllib.request
import urllib.parse
from typing import Any


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.0 Mobile/15E148 Safari/604.1"
    ),
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
}

# TikTok trending hashtags via web API (no auth)
_TRENDING_HASHTAG_URL = (
    "https://www.tiktok.com/api/discover/challenge/?"
    "aid=1988&count=30&discoverType=0&needItemList=false&scene=24"
)

# TikTok trending sounds/music
_TRENDING_MUSIC_URL = (
    "https://www.tiktok.com/api/discover/music/?"
    "aid=1988&count=30&discoverType=0&scene=24"
)

# TikTok explore page
_EXPLORE_URL = "https://www.tiktok.com/explore"

# Known viral TikTok hashtag categories for proactive seeding
_NICHE_HASHTAG_SEEDS: dict[str, list[str]] = {
    "fitness":    ["fitness", "workout", "gym", "fyp", "fitspo", "healthylifestyle", "gains", "calisthenics"],
    "fashion":    ["fashion", "ootd", "style", "aesthetic", "outfitinspo", "fashiontok", "streetwear"],
    "food":       ["food", "foodtok", "recipe", "cooking", "easyrecipe", "foodie", "mukbang", "asmr"],
    "beauty":     ["beauty", "makeup", "skincare", "glowup", "beautytok", "grwm", "skincareroutine"],
    "finance":    ["finance", "moneytok", "sidehustle", "investing", "passiveincome", "financialtips"],
    "motivation": ["motivation", "mindset", "success", "entrepreneur", "grindset", "hustle", "dailymotivation"],
    "gaming":     ["gaming", "gametok", "twitch", "fyp", "gamingsetup", "esports", "pcgaming"],
    "travel":     ["travel", "traveltok", "wanderlust", "explore", "adventure", "traveltheworld"],
    "pets":       ["pets", "dogsoftiktok", "catsoftiktok", "animalsoftiktok", "funnypets", "petsoftiktok"],
    "education":  ["learnontiktok", "edutok", "didyouknow", "facts", "science", "history", "lifehacks"],
    "general":    ["fyp", "foryou", "foryoupage", "viral", "trending", "explore", "xyzbca", "4u"],
}


def _fetch_url(url: str, timeout: int = 12) -> dict | str:
    """Fetch a URL and return parsed JSON or raw text."""
    try:
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                return body
    except Exception as exc:
        return {"_error": str(exc)}


def _parse_trending_hashtags(data: Any) -> list[dict]:
    """Parse TikTok challenge/hashtag discover response."""
    if not isinstance(data, dict):
        return []
    items = data.get("challengeInfoList") or data.get("itemList") or []
    results = []
    for item in items:
        challenge = item.get("challengeInfo", {}).get("challenge", item)
        name = challenge.get("title", "") or challenge.get("desc", "")
        view_count = challenge.get("stats", {}).get("videoCount", 0)
        if name:
            results.append({
                "hashtag": f"#{name}",
                "video_count": view_count,
                "url": f"https://www.tiktok.com/tag/{urllib.parse.quote(name)}",
            })
    return results


def _parse_trending_music(data: Any) -> list[dict]:
    """Parse TikTok music discover response."""
    if not isinstance(data, dict):
        return []
    items = data.get("musicInfoList") or []
    results = []
    for item in items:
        music = item.get("music", item)
        title = music.get("title", "")
        author = music.get("authorName", "")
        play_url = music.get("playUrl", "")
        use_count = music.get("stats", {}).get("videoCount", 0)
        if title:
            results.append({
                "title": title,
                "artist": author,
                "use_count": use_count,
                "preview_url": play_url,
            })
    return results


def _scrape_explore_html(html: str) -> list[str]:
    """Extract hashtag names from TikTok explore page HTML."""
    tags = re.findall(r'#(\w{2,30})', html)
    # Also grab JSON-embedded challenge titles
    for m in re.finditer(r'"title"\s*:\s*"([^"]{2,40})"', html):
        tags.append(m.group(1).replace(" ", ""))
    seen: list[str] = []
    for t in tags:
        if t.lower() not in [x.lower() for x in seen]:
            seen.append(t)
    return seen[:30]


def fetch_tiktok_trends(niche: str = "general", max_items: int = 30) -> dict[str, Any]:
    """
    Fetch TikTok trending hashtags, sounds, and topics.

    Args:
        niche: one of fitness/fashion/food/beauty/finance/motivation/gaming/travel/pets/education/general
        max_items: max number of results per category

    Returns dict with:
      - hashtags: trending hashtag objects
      - music: trending sounds/music
      - niche_hashtags: curated hashtags for the specified niche
      - viral_topics: keyword topics extracted from trends
    """
    # Try live API endpoints
    hashtag_data = _fetch_url(_TRENDING_HASHTAG_URL)
    music_data = _fetch_url(_TRENDING_MUSIC_URL)

    live_hashtags = _parse_trending_hashtags(hashtag_data)
    live_music = _parse_trending_music(music_data)

    # If live data is empty / blocked, fallback to explore page HTML scraping
    if not live_hashtags:
        explore_raw = _fetch_url(_EXPLORE_URL)
        if isinstance(explore_raw, str):
            scraped = _scrape_explore_html(explore_raw)
            live_hashtags = [{"hashtag": f"#{t}", "video_count": 0,
                              "url": f"https://www.tiktok.com/tag/{urllib.parse.quote(t)}"}
                             for t in scraped]

    # Curated niche hashtags (always available)
    niche_key = niche.lower() if niche.lower() in _NICHE_HASHTAG_SEEDS else "general"
    niche_tags = [f"#{t}" for t in _NICHE_HASHTAG_SEEDS[niche_key]]
    # Add general viral boosters
    for tag in _NICHE_HASHTAG_SEEDS["general"]:
        htag = f"#{tag}"
        if htag not in niche_tags:
            niche_tags.append(htag)

    # Extract viral topics
    all_tag_names = [h["hashtag"].lstrip("#") for h in live_hashtags]
    viral_topics = list(dict.fromkeys(all_tag_names[:15]))

    # Build trending sounds list — merge live + known viral sounds
    known_sounds = [
        {"title": "original sound", "artist": "creator", "use_count": 0, "preview_url": ""},
        {"title": "trending audio", "artist": "viral", "use_count": 0, "preview_url": ""},
    ]
    all_music = (live_music or []) + known_sounds

    return {
        "platform": "tiktok",
        "niche": niche_key,
        "total_hashtags": len(live_hashtags),
        "hashtags": live_hashtags[:max_items],
        "music": all_music[:20],
        "niche_hashtags": niche_tags[:25],
        "viral_topics": viral_topics,
        "pro_tip": (
            f"For the '{niche_key}' niche, post 3-5 videos/day using a mix of "
            "niche-specific + 1-2 mega viral tags (#fyp, #viral). "
            "Use trending sounds within 24-48h of them going viral for max reach."
        ),
    }
