#!/usr/bin/env python3
"""TikTok trending scraper using public web endpoints."""

import json
import re
import time
import requests
from typing import Optional

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.0 Mobile/15E148 Safari/604.1"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
}

_DISCOVER_URL = "https://www.tiktok.com/api/discover/challenge/"
_TRENDING_FEED_URL = "https://www.tiktok.com/api/recommend/item_list/"
_MUSIC_URL = "https://www.tiktok.com/api/music/list/"

# Curated trending niches for when live scraping is blocked
_CURATED_NICHES = [
    "fitness", "cooking", "travel", "fashion", "beauty",
    "gaming", "comedy", "dance", "motivation", "tech",
    "pets", "diy", "finance", "education", "lifestyle",
]


def _make_request(url: str, params: dict) -> Optional[dict]:
    try:
        resp = requests.get(url, headers=_HEADERS, params=params, timeout=12)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


def fetch_trending_hashtags(count: int = 30) -> list[dict]:
    """
    Fetch TikTok trending hashtags/challenges.
    Falls back to curated data if the endpoint is blocked.
    """
    params = {"count": count, "from": 0, "type": 1}
    data = _make_request(_DISCOVER_URL, params)

    if data and "challengeInfoList" in data:
        tags = []
        for item in data.get("challengeInfoList", []):
            ch = item.get("challengeInfo", {}) or item.get("challenge", {})
            stats = item.get("stats", {})
            tags.append({
                "hashtag": f"#{ch.get('title', '')}",
                "description": ch.get("desc", ""),
                "video_count": stats.get("videoCount", 0),
                "view_count": stats.get("viewCount", 0),
                "source": "live",
            })
        return tags[:count]

    # Fallback: return curated trending categories as hashtag templates
    return _curated_hashtag_fallback(count)


def _curated_hashtag_fallback(count: int) -> list[dict]:
    """Curated list of evergreen + likely-trending hashtags."""
    tags = [
        {"hashtag": "#fyp", "description": "For You Page — highest reach tag", "source": "curated"},
        {"hashtag": "#foryou", "description": "For You feed", "source": "curated"},
        {"hashtag": "#foryoupage", "description": "For You Page", "source": "curated"},
        {"hashtag": "#viral", "description": "Viral content", "source": "curated"},
        {"hashtag": "#trending", "description": "Trending content", "source": "curated"},
        {"hashtag": "#tiktok", "description": "Platform tag", "source": "curated"},
        {"hashtag": "#viralvideo", "description": "Viral video", "source": "curated"},
        {"hashtag": "#explore", "description": "Exploration feed", "source": "curated"},
        {"hashtag": "#fitness", "description": "Fitness & workout content", "source": "curated"},
        {"hashtag": "#gym", "description": "Gym culture", "source": "curated"},
        {"hashtag": "#workout", "description": "Workout routines", "source": "curated"},
        {"hashtag": "#recipe", "description": "Food recipes", "source": "curated"},
        {"hashtag": "#foodtok", "description": "Food TikTok community", "source": "curated"},
        {"hashtag": "#travel", "description": "Travel content", "source": "curated"},
        {"hashtag": "#fashion", "description": "Fashion & OOTD", "source": "curated"},
        {"hashtag": "#ootd", "description": "Outfit of the Day", "source": "curated"},
        {"hashtag": "#beauty", "description": "Beauty & makeup", "source": "curated"},
        {"hashtag": "#skincare", "description": "Skincare routines", "source": "curated"},
        {"hashtag": "#comedy", "description": "Comedy skits", "source": "curated"},
        {"hashtag": "#dance", "description": "Dance content", "source": "curated"},
        {"hashtag": "#motivation", "description": "Motivational content", "source": "curated"},
        {"hashtag": "#mindset", "description": "Mindset & growth", "source": "curated"},
        {"hashtag": "#money", "description": "Finance & money tips", "source": "curated"},
        {"hashtag": "#investing", "description": "Investment tips", "source": "curated"},
        {"hashtag": "#learnontiktok", "description": "Educational content", "source": "curated"},
        {"hashtag": "#howto", "description": "How-to tutorials", "source": "curated"},
        {"hashtag": "#pets", "description": "Pet content", "source": "curated"},
        {"hashtag": "#dogsoftiktok", "description": "Dog content", "source": "curated"},
        {"hashtag": "#gaming", "description": "Gaming content", "source": "curated"},
        {"hashtag": "#storytime", "description": "Storytime content", "source": "curated"},
    ]
    return tags[:count]


def fetch_trending_sounds(count: int = 20) -> list[dict]:
    """
    Fetch TikTok trending sounds/music.
    Returns curated data since the live API requires auth tokens.
    """
    # TikTok's sound trending endpoint requires session cookies we don't have,
    # so we return a structured guide to finding them programmatically.
    sounds = [
        {
            "title": "Original Sound (trending audio)",
            "usage": "Use sounds from videos with 100k+ uses",
            "how_to_find": "TikTok > Discover > Sounds tab > filter by Trending",
            "strategy": "Reuse trending sounds within 24-48h of peak for max reach",
            "source": "guide",
        },
        {
            "title": "Viral Remix / Mashup",
            "usage": "Remixed versions of popular songs often trend separately",
            "how_to_find": "Search original song + 'remix' on Discover",
            "strategy": "Add transition or speed ramp synced to beat drop",
            "source": "guide",
        },
        {
            "title": "Phonk / Drift Music",
            "usage": "High energy background for POV/transformation videos",
            "how_to_find": "Search #phonk or #drift on Discover",
            "strategy": "Use for gym, car, aesthetic, or transformation content",
            "source": "guide",
        },
        {
            "title": "Lo-fi Beats",
            "usage": "Study, productivity, relaxation content",
            "how_to_find": "Search #lofi on Discover",
            "strategy": "Layer with text-on-screen content for longer watch time",
            "source": "guide",
        },
        {
            "title": "Trending Pop Song (chorus hook)",
            "usage": "Dance, lip sync, or reaction content",
            "how_to_find": "Billboard Hot 100 + cross-check TikTok Discover",
            "strategy": "Post within 48h of song dropping to catch the wave",
            "source": "guide",
        },
        {
            "title": "Emotional / Cinematic Music",
            "usage": "Storytelling, travel, or transformation videos",
            "how_to_find": "Search #cinematic or #aesthetic on Discover",
            "strategy": "Match music mood to visual progression for emotional pull",
            "source": "guide",
        },
        {
            "title": "Trending Sound Effect",
            "usage": "Comedy, reaction, duet content",
            "how_to_find": "TikTok > Discover > filter Sounds by Most Used (7 days)",
            "strategy": "Subvert expectations — set up with sound then twist the delivery",
            "source": "guide",
        },
    ]
    return sounds[:count]


def fetch_trending_videos(count: int = 20) -> list[dict]:
    """
    Fetch TikTok trending video metadata.
    Returns structured guide since live feed requires authenticated session.
    """
    return {
        "note": "Live TikTok feed requires authenticated session token",
        "how_to_access": [
            "Use TikTok Creator Portal > Analytics > Trending tab",
            "Use TikTok Creative Center (ads.tiktok.com/creative) for trend data",
            "Use TikTokApi Python library with a real account session",
        ],
        "content_patterns": _get_viral_content_patterns(),
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def _get_viral_content_patterns() -> list[dict]:
    return [
        {
            "pattern": "POV (Point of View)",
            "description": "First-person scenario that hooks viewer in first 1s",
            "hook_formula": "POV: You [relatable situation]",
            "avg_completion_rate": "high",
            "best_niche": "comedy, romance, lifestyle, finance",
        },
        {
            "pattern": "Transformation / Before & After",
            "description": "Dramatic reveal split — before state vs after state",
            "hook_formula": "I [changed X] for [N] days — here's what happened",
            "avg_completion_rate": "very high",
            "best_niche": "fitness, beauty, home decor, finance",
        },
        {
            "pattern": "Tutorial (value bomb)",
            "description": "Quick actionable how-to in under 60s",
            "hook_formula": "Stop doing X. Do this instead:",
            "avg_completion_rate": "high",
            "best_niche": "cooking, tech, beauty, finance, fitness",
        },
        {
            "pattern": "Storytime",
            "description": "Personal narrative with emotional arc",
            "hook_formula": "I need to tell you what happened when I...",
            "avg_completion_rate": "medium-high",
            "best_niche": "lifestyle, fashion, travel, pets",
        },
        {
            "pattern": "List / Countdown",
            "description": "Numbered takeaways — viewer watches to see all items",
            "hook_formula": "[N] things [target audience] needs to know",
            "avg_completion_rate": "high",
            "best_niche": "finance, fitness, education, tech",
        },
        {
            "pattern": "Reaction / Duet",
            "description": "React to viral/controversial content in your niche",
            "hook_formula": "They said [claim]... but actually:",
            "avg_completion_rate": "medium",
            "best_niche": "comedy, news commentary, fitness, beauty",
        },
        {
            "pattern": "Trending Sound + Niche Twist",
            "description": "Adapt a trending audio format to your niche",
            "hook_formula": "Use the trending sound, make the content niche-specific",
            "avg_completion_rate": "very high (algorithm boost from trending audio)",
            "best_niche": "any — this is platform-universal",
        },
        {
            "pattern": "Behind the Scenes",
            "description": "Show the process/work behind a finished product",
            "hook_formula": "How I [impressive outcome] in [short time]",
            "avg_completion_rate": "high",
            "best_niche": "cooking, art, business, fitness, travel",
        },
    ]


def fetch_all_trends(max_hashtags: int = 30, max_sounds: int = 20) -> dict:
    """Fetch all TikTok trend data in one call."""
    return {
        "platform": "tiktok",
        "hashtags": fetch_trending_hashtags(max_hashtags),
        "sounds": fetch_trending_sounds(max_sounds),
        "viral_patterns": fetch_trending_videos()["content_patterns"],
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
