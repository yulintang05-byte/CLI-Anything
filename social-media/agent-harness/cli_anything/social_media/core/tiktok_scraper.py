"""TikTok trend scraper - viral hashtags, sounds, and content data."""

import json
import re
import time
import random
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# TikTok's internal explore/trending endpoints (public, no auth)
_TIKTOK_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
    "sec-fetch-site": "same-origin",
}

_DISCOVER_URL = "https://www.tiktok.com/api/explore/item_list/"
_HASHTAG_URL = "https://www.tiktok.com/api/challenge/item_list/"
_TRENDING_PAGE_URL = "https://www.tiktok.com/trending"

# Fallback: TikTok Discover page scrape
_DISCOVER_PAGE_URL = "https://www.tiktok.com/discover"


def _random_delay(lo: float = 0.5, hi: float = 1.5):
    time.sleep(random.uniform(lo, hi))


def _get_tiktok_page(url: str) -> Optional[str]:
    if not HAS_REQUESTS:
        return None
    try:
        resp = requests.get(url, headers=_TIKTOK_HEADERS, timeout=20)
        if resp.status_code == 200:
            return resp.text
    except Exception:
        pass
    return None


def _parse_sigi_state(html: str) -> Optional[Dict]:
    """Extract __NEXT_DATA__ or SIGI_STATE JSON from TikTok page."""
    for pattern in [
        r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>',
        r'window\["SIGI_STATE"\]\s*=\s*(\{.+?\});\s*window\[',
        r'<script>window\.__NEXT_DATA__\s*=\s*(\{.+?\})</script>',
    ]:
        match = re.search(pattern, html, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                continue
    return None


def _extract_hashtags_from_page(html: str) -> List[Dict[str, Any]]:
    """Pull trending hashtag data from TikTok discover/trending HTML."""
    hashtags = []
    seen = set()

    # Pattern 1: JSON embedded data
    data = _parse_sigi_state(html)
    if data:
        try:
            challenges = (
                data.get("props", {})
                .get("pageProps", {})
                .get("itemList", [])
            )
            for item in challenges:
                desc = item.get("desc", "")
                tags = re.findall(r"#(\w+)", desc)
                for tag in tags:
                    if tag.lower() not in seen:
                        seen.add(tag.lower())
                        hashtags.append({
                            "hashtag": f"#{tag}",
                            "platform": "tiktok",
                            "source": "embedded_json",
                        })
        except Exception:
            pass

    # Pattern 2: Hashtags in raw HTML text
    raw_tags = re.findall(r'challengeName["\s:]+([A-Za-z0-9_]+)', html)
    for tag in raw_tags:
        if tag.lower() not in seen:
            seen.add(tag.lower())
            hashtags.append({
                "hashtag": f"#{tag}",
                "platform": "tiktok",
                "source": "html_parse",
            })

    # Pattern 3: Hashtag links
    link_tags = re.findall(r'/tag/([A-Za-z0-9_]+)', html)
    for tag in link_tags:
        if tag.lower() not in seen and len(tag) > 1:
            seen.add(tag.lower())
            hashtags.append({
                "hashtag": f"#{tag}",
                "platform": "tiktok",
                "source": "tag_link",
            })

    return hashtags


def _extract_sounds_from_page(html: str) -> List[Dict[str, Any]]:
    """Extract trending sound/music data from TikTok page HTML."""
    sounds = []
    seen = set()

    # Sound titles from JSON
    data = _parse_sigi_state(html)
    if data:
        try:
            items = (
                data.get("props", {})
                .get("pageProps", {})
                .get("itemList", [])
            )
            for item in items:
                music = item.get("music", {})
                if not music:
                    continue
                mid = music.get("id", "")
                if mid in seen:
                    continue
                seen.add(mid)
                sounds.append({
                    "id": str(mid),
                    "title": music.get("title", ""),
                    "author": music.get("authorName", ""),
                    "duration": music.get("duration", 0),
                    "platform": "tiktok",
                    "url": f"https://www.tiktok.com/music/{music.get('title','').replace(' ','-')}-{mid}",
                })
        except Exception:
            pass

    # Sound titles from raw HTML
    raw_sounds = re.findall(r'"musicName"\s*:\s*"([^"]+)"', html)
    for s in raw_sounds:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            sounds.append({
                "id": "",
                "title": s,
                "author": "",
                "duration": 0,
                "platform": "tiktok",
                "url": "",
            })

    return sounds[:30]


def _scrape_discover_page() -> Dict[str, Any]:
    """Scrape TikTok's discover page for trending hashtags and sounds."""
    html = _get_tiktok_page(_DISCOVER_PAGE_URL)
    if not html:
        html = _get_tiktok_page(_TRENDING_PAGE_URL)
    if not html:
        return {"hashtags": [], "sounds": [], "error": "Could not fetch TikTok page"}

    hashtags = _extract_hashtags_from_page(html)
    sounds = _extract_sounds_from_page(html)
    return {
        "hashtags": hashtags,
        "sounds": sounds,
        "error": None,
    }


def _get_known_viral_hashtags_2026() -> List[Dict[str, Any]]:
    """
    Curated snapshot of TikTok viral hashtags as of 2026.
    Updated periodically — use live scraping for real-time data.
    """
    return [
        {"hashtag": "#fyp", "category": "reach", "avg_views": "1B+", "type": "discovery"},
        {"hashtag": "#foryou", "category": "reach", "avg_views": "900B+", "type": "discovery"},
        {"hashtag": "#foryoupage", "category": "reach", "avg_views": "500B+", "type": "discovery"},
        {"hashtag": "#viral", "category": "reach", "avg_views": "400B+", "type": "discovery"},
        {"hashtag": "#trending", "category": "reach", "avg_views": "200B+", "type": "discovery"},
        {"hashtag": "#tiktok", "category": "platform", "avg_views": "300B+", "type": "discovery"},
        {"hashtag": "#duet", "category": "engagement", "avg_views": "80B+", "type": "feature"},
        {"hashtag": "#stitch", "category": "engagement", "avg_views": "60B+", "type": "feature"},
        {"hashtag": "#learnontiktok", "category": "education", "avg_views": "300B+", "type": "niche"},
        {"hashtag": "#tiktoktaughtme", "category": "education", "avg_views": "50B+", "type": "niche"},
        {"hashtag": "#lifehack", "category": "education", "avg_views": "80B+", "type": "niche"},
        {"hashtag": "#smallbusiness", "category": "business", "avg_views": "100B+", "type": "niche"},
        {"hashtag": "#entrepreneur", "category": "business", "avg_views": "60B+", "type": "niche"},
        {"hashtag": "#sidehustle", "category": "business", "avg_views": "40B+", "type": "niche"},
        {"hashtag": "#passiveincome", "category": "business", "avg_views": "30B+", "type": "niche"},
        {"hashtag": "#fashion", "category": "lifestyle", "avg_views": "200B+", "type": "niche"},
        {"hashtag": "#ootd", "category": "fashion", "avg_views": "100B+", "type": "niche"},
        {"hashtag": "#skincare", "category": "beauty", "avg_views": "100B+", "type": "niche"},
        {"hashtag": "#makeup", "category": "beauty", "avg_views": "150B+", "type": "niche"},
        {"hashtag": "#fitness", "category": "health", "avg_views": "100B+", "type": "niche"},
        {"hashtag": "#workout", "category": "health", "avg_views": "80B+", "type": "niche"},
        {"hashtag": "#weightloss", "category": "health", "avg_views": "60B+", "type": "niche"},
        {"hashtag": "#recipe", "category": "food", "avg_views": "80B+", "type": "niche"},
        {"hashtag": "#foodtok", "category": "food", "avg_views": "60B+", "type": "niche"},
        {"hashtag": "#cooking", "category": "food", "avg_views": "70B+", "type": "niche"},
        {"hashtag": "#travel", "category": "travel", "avg_views": "100B+", "type": "niche"},
        {"hashtag": "#gaming", "category": "gaming", "avg_views": "80B+", "type": "niche"},
        {"hashtag": "#booktok", "category": "education", "avg_views": "50B+", "type": "community"},
        {"hashtag": "#motivation", "category": "mindset", "avg_views": "70B+", "type": "niche"},
        {"hashtag": "#storytime", "category": "entertainment", "avg_views": "90B+", "type": "format"},
    ]


def scrape_trending_hashtags(
    live: bool = True,
    niche: Optional[str] = None,
    limit: int = 30,
) -> Dict[str, Any]:
    """
    Get trending TikTok hashtags.

    Args:
        live: attempt live scrape (falls back to curated list if blocked)
        niche: filter by category (business, beauty, fitness, food, etc.)
        limit: max hashtags to return

    Returns:
        dict with hashtags list, sounds, and metadata
    """
    scraped = {"hashtags": [], "sounds": [], "error": None}
    method = "curated"

    if live and HAS_REQUESTS:
        _random_delay()
        scraped = _scrape_discover_page()
        if scraped["hashtags"]:
            method = "live_scrape"

    # Merge with curated list to ensure useful results
    curated = _get_known_viral_hashtags_2026()
    live_tags = {h["hashtag"].lower() for h in scraped["hashtags"]}

    for entry in curated:
        if entry["hashtag"].lower() not in live_tags:
            scraped["hashtags"].append({
                "hashtag": entry["hashtag"],
                "platform": "tiktok",
                "source": "curated_2026",
                "category": entry.get("category", ""),
                "avg_views": entry.get("avg_views", ""),
                "type": entry.get("type", ""),
            })

    hashtags = scraped["hashtags"]
    if niche:
        hashtags = [
            h for h in hashtags
            if niche.lower() in h.get("category", "").lower()
            or niche.lower() in h.get("hashtag", "").lower()
        ]

    hashtags = hashtags[:limit]

    return {
        "scraped_at": datetime.now().isoformat(),
        "platform": "tiktok",
        "method": method,
        "total": len(hashtags),
        "hashtags": hashtags,
        "trending_sounds": scraped["sounds"][:10],
        "error": scraped.get("error"),
        "tip": (
            "For real-time TikTok data, consider TikTok Research API (academic/business accounts) "
            "or services like EnsembleData / Apify TikTok scrapers."
        ),
    }


def scrape_hashtag_videos(hashtag: str, limit: int = 20) -> Dict[str, Any]:
    """Fetch videos under a specific TikTok hashtag."""
    tag = hashtag.lstrip("#")
    url = f"https://www.tiktok.com/tag/{tag}"
    html = _get_tiktok_page(url)

    videos = []
    if html:
        data = _parse_sigi_state(html)
        if data:
            try:
                items = (
                    data.get("props", {})
                    .get("pageProps", {})
                    .get("itemList", [])
                    or data.get("ItemModule", {}).values()
                )
                for item in list(items)[:limit]:
                    if isinstance(item, dict):
                        videos.append(_parse_video_item(item))
            except Exception:
                pass

        # Fallback: count from HTML
        if not videos:
            view_counts = re.findall(r'"playCount"\s*:\s*(\d+)', html)
            desc_list = re.findall(r'"desc"\s*:\s*"([^"]+)"', html)
            for i, (views, desc) in enumerate(zip(view_counts, desc_list)):
                if i >= limit:
                    break
                tags_in_desc = re.findall(r"#(\w+)", desc)
                videos.append({
                    "title": desc[:100],
                    "views": int(views),
                    "hashtags": tags_in_desc,
                    "platform": "tiktok",
                })

    return {
        "hashtag": f"#{tag}",
        "url": url,
        "scraped_at": datetime.now().isoformat(),
        "video_count": len(videos),
        "videos": videos,
    }


def _parse_video_item(item: Dict) -> Dict[str, Any]:
    desc = item.get("desc", "")
    hashtags = re.findall(r"#(\w+)", desc)
    music = item.get("music", {})
    stats = item.get("stats", {})
    author = item.get("author", {})
    vid_id = item.get("id", "")
    return {
        "id": vid_id,
        "url": f"https://www.tiktok.com/@{author.get('uniqueId','')}/video/{vid_id}",
        "description": desc[:200],
        "hashtags": hashtags,
        "views": stats.get("playCount", 0),
        "likes": stats.get("diggCount", 0),
        "comments": stats.get("commentCount", 0),
        "shares": stats.get("shareCount", 0),
        "author": author.get("uniqueId", ""),
        "music_title": music.get("title", ""),
        "music_author": music.get("authorName", ""),
        "music_id": str(music.get("id", "")),
        "platform": "tiktok",
    }
