"""TikTok viral trend scraper — public endpoints + discovery page parsing."""
import re
import json
import time
import random
from typing import List, Dict, Any, Optional

import requests
from bs4 import BeautifulSoup

from cli_anything.social.utils.scraper import RateLimitedSession, TIKTOK_HEADERS

# Public TikTok discovery endpoints (no auth required)
TIKTOK_DISCOVER_URL  = "https://www.tiktok.com/api/discover/item_list/"
TIKTOK_TRENDING_URL  = "https://www.tiktok.com/foryou"
TIKTOK_HASHTAG_URL   = "https://www.tiktok.com/tag/{hashtag}"
TIKTOK_EXPLORE_URL   = "https://www.tiktok.com/explore"

# Verified trending discovery params (public, no auth)
_DISCOVER_PARAMS = {
    "aid":           "1988",
    "app_language":  "en",
    "count":         "30",
    "discoverType":  "0",
    "offset":        "0",
    "type":          "0",
}


def _session() -> RateLimitedSession:
    s = RateLimitedSession(min_delay=2.0, max_delay=4.5)
    s.session.headers.update(TIKTOK_HEADERS)
    return s


def scrape_trending_hashtags(max_results: int = 30) -> List[Dict]:
    """Scrape trending hashtags from TikTok's explore/discover page."""
    session = _session()

    # Try the explore page first (HTML parse)
    try:
        resp = session.get(TIKTOK_EXPLORE_URL, headers=TIKTOK_HEADERS)
        soup = BeautifulSoup(resp.text, "lxml")

        tags = []
        # TikTok embeds __UNIVERSAL_DATA_FOR_REHYDRATION__ in a script tag
        for script in soup.find_all("script"):
            text = script.string or ""
            if "UNIVERSAL_DATA_FOR_REHYDRATION" in text:
                data = _extract_json_blob(text, "UNIVERSAL_DATA_FOR_REHYDRATION")
                if data:
                    tags = _parse_explore_data(data)
                    break

        # Fallback: scrape any #hashtag anchors visible in the page
        if not tags:
            anchors = soup.find_all("a", href=re.compile(r"/tag/"))
            seen = set()
            for a in anchors:
                href = a.get("href", "")
                m = re.search(r"/tag/([^/?]+)", href)
                if m:
                    tag = m.group(1).lower()
                    if tag not in seen:
                        seen.add(tag)
                        tags.append({"hashtag": f"#{tag}", "views": None, "source": "explore"})

        return tags[:max_results]
    except Exception:
        pass

    return _fallback_trending_hashtags()[:max_results]


def scrape_trending_sounds(max_results: int = 20) -> List[Dict]:
    """Scrape trending sounds/music from TikTok's public data."""
    session = _session()
    sounds = []

    try:
        resp = session.get(TIKTOK_EXPLORE_URL, headers=TIKTOK_HEADERS)
        soup = BeautifulSoup(resp.text, "lxml")

        for script in soup.find_all("script"):
            text = script.string or ""
            if "musicList" in text or "soundList" in text or "music" in text.lower():
                data = _extract_json_blob(text, "UNIVERSAL_DATA_FOR_REHYDRATION")
                if data:
                    sounds = _parse_sound_data(data)
                    if sounds:
                        break

        # Fallback: extract music mentions from page text
        if not sounds:
            music_section = soup.find_all(attrs={"data-e2e": re.compile(r"music|sound", re.I)})
            for el in music_section:
                title = el.get_text(strip=True)
                if title:
                    sounds.append({"title": title, "artist": "Unknown", "source": "explore"})

    except Exception:
        pass

    if not sounds:
        sounds = _fallback_trending_sounds()

    return sounds[:max_results]


def scrape_hashtag_videos(hashtag: str, max_results: int = 15) -> List[Dict]:
    """Scrape recent videos for a specific TikTok hashtag."""
    session = _session()
    hashtag = hashtag.lstrip("#")
    url = TIKTOK_HASHTAG_URL.format(hashtag=hashtag)

    try:
        resp = session.get(url, headers=TIKTOK_HEADERS)
        soup = BeautifulSoup(resp.text, "lxml")

        videos = []
        for script in soup.find_all("script"):
            text = script.string or ""
            if "itemList" in text or "videoList" in text:
                data = _extract_json_blob(text, "UNIVERSAL_DATA_FOR_REHYDRATION")
                if data:
                    videos = _parse_video_list(data)
                    if videos:
                        break

        return [{"hashtag": f"#{hashtag}", **v} for v in videos[:max_results]]
    except Exception:
        return []


def get_tiktok_trends(max_hashtags: int = 30, max_sounds: int = 20) -> Dict[str, Any]:
    """Main entry point: return TikTok trending hashtags, sounds, and insights."""
    hashtags = scrape_trending_hashtags(max_results=max_hashtags)
    sounds   = scrape_trending_sounds(max_results=max_sounds)

    return {
        "platform":  "tiktok",
        "hashtags":  hashtags,
        "sounds":    sounds,
        "insights":  _generate_tiktok_insights(hashtags, sounds),
        "count": {
            "hashtags": len(hashtags),
            "sounds":   len(sounds),
        },
    }


# ── parsers ───────────────────────────────────────────────────────────────────

def _extract_json_blob(text: str, key: str) -> Optional[Dict]:
    """Pull a JSON blob assigned to `key` out of a JS script block."""
    pattern = rf'"{key}"\s*:\s*(\{{.*?\}})'
    m = re.search(pattern, text, re.DOTALL)
    if not m:
        # Try assignment form
        pattern2 = rf'var\s+{key}\s*=\s*(\{{.*?\}})\s*;'
        m = re.search(pattern2, text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        # Try to extract up to first balanced brace close
        return None


def _parse_explore_data(data: Dict) -> List[Dict]:
    tags = []
    def _recurse(obj):
        if isinstance(obj, dict):
            # Look for challengeInfo or hashtagList structures
            if "challengeName" in obj or "hashtagName" in obj or "title" in obj:
                name = obj.get("challengeName") or obj.get("hashtagName") or obj.get("title", "")
                if name and not name.startswith("http"):
                    views = obj.get("viewCount") or obj.get("stats", {}).get("viewCount")
                    tags.append({
                        "hashtag": f"#{name.lower().replace(' ', '')}",
                        "views": _fmt_views(views),
                        "source": "explore",
                    })
            for v in obj.values():
                _recurse(v)
        elif isinstance(obj, list):
            for item in obj:
                _recurse(item)
    _recurse(data)
    return tags


def _parse_sound_data(data: Dict) -> List[Dict]:
    sounds = []
    def _recurse(obj):
        if isinstance(obj, dict):
            if "musicName" in obj or "music" in obj:
                music = obj.get("music") if isinstance(obj.get("music"), dict) else obj
                title  = music.get("musicName") or music.get("title", "")
                artist = music.get("authorName") or music.get("artistName", "Unknown")
                if title:
                    sounds.append({
                        "title":  title,
                        "artist": artist,
                        "id":     music.get("musicId") or music.get("id", ""),
                        "source": "explore",
                    })
            for v in obj.values():
                _recurse(v)
        elif isinstance(obj, list):
            for item in obj:
                _recurse(item)
    _recurse(data)
    return sounds


def _parse_video_list(data: Dict) -> List[Dict]:
    videos = []
    def _recurse(obj):
        if isinstance(obj, dict):
            if "desc" in obj and "stats" in obj:
                stats = obj.get("stats", {})
                videos.append({
                    "desc":       obj.get("desc", ""),
                    "views":      _fmt_views(stats.get("playCount", 0)),
                    "likes":      _fmt_views(stats.get("diggCount", 0)),
                    "shares":     stats.get("shareCount", 0),
                    "author":     obj.get("author", {}).get("uniqueId", ""),
                })
            for v in obj.values():
                _recurse(v)
        elif isinstance(obj, list):
            for item in obj:
                _recurse(item)
    _recurse(data)
    return videos


def _generate_tiktok_insights(hashtags: List[Dict], sounds: List[Dict]) -> List[str]:
    insights = []
    if hashtags:
        top3 = [h["hashtag"] for h in hashtags[:3]]
        insights.append(f"Top trending hashtags right now: {', '.join(top3)}")
    if sounds:
        top_sound = sounds[0]
        insights.append(f"Most viral sound: \"{top_sound.get('title','?')}\" by {top_sound.get('artist','?')}")
    insights += [
        "Post between 6–10 AM or 7–11 PM in your audience's timezone for peak reach.",
        "Use 3–5 niche hashtags + 1–2 trending ones per post for best discoverability.",
        "Duets and Stitches of viral content can 3x your organic reach.",
        "First 1–3 seconds must hook: start mid-action, never a blank intro.",
        "Trending sounds boost FYP distribution — add them even to unrelated content.",
    ]
    return insights


# ── fallbacks (curated evergreen data when scraping is blocked) ───────────────

def _fallback_trending_hashtags() -> List[Dict]:
    """Return a curated seed list when live scraping fails."""
    return [
        {"hashtag": "#fyp",          "views": "7.6T", "source": "fallback"},
        {"hashtag": "#foryou",       "views": "5.2T", "source": "fallback"},
        {"hashtag": "#viral",        "views": "2.1T", "source": "fallback"},
        {"hashtag": "#trending",     "views": "1.4T", "source": "fallback"},
        {"hashtag": "#foryoupage",   "views": "1.3T", "source": "fallback"},
        {"hashtag": "#tiktok",       "views": "934B", "source": "fallback"},
        {"hashtag": "#funny",        "views": "800B", "source": "fallback"},
        {"hashtag": "#dance",        "views": "590B", "source": "fallback"},
        {"hashtag": "#lifestyle",    "views": "342B", "source": "fallback"},
        {"hashtag": "#motivation",   "views": "225B", "source": "fallback"},
        {"hashtag": "#business",     "views": "180B", "source": "fallback"},
        {"hashtag": "#moneytiktok",  "views": "92B",  "source": "fallback"},
        {"hashtag": "#entrepreneur", "views": "78B",  "source": "fallback"},
        {"hashtag": "#themepage",    "views": "45B",  "source": "fallback"},
        {"hashtag": "#niche",        "views": "32B",  "source": "fallback"},
    ]


def _fallback_trending_sounds() -> List[Dict]:
    return [
        {"title": "Espresso",          "artist": "Sabrina Carpenter",  "source": "fallback"},
        {"title": "Beautiful Things",  "artist": "Benson Boone",       "source": "fallback"},
        {"title": "Harleys in Hawaii", "artist": "Katy Perry",         "source": "fallback"},
        {"title": "Die With A Smile",  "artist": "Lady Gaga & Bruno",  "source": "fallback"},
        {"title": "APT.",              "artist": "ROSÉ & Bruno Mars",  "source": "fallback"},
        {"title": "Birds of a Feather","artist": "Billie Eilish",      "source": "fallback"},
        {"title": "Too Sweet",         "artist": "Hozier",             "source": "fallback"},
        {"title": "Taste",             "artist": "Sabrina Carpenter",  "source": "fallback"},
    ]


def _fmt_views(n) -> str:
    if n is None:
        return "N/A"
    try:
        n = int(n)
    except (TypeError, ValueError):
        return str(n)
    if n >= 1_000_000_000_000:
        return f"{n/1_000_000_000_000:.1f}T"
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)
