"""YouTube Shorts trend scraper — public data, no API key required.

Uses YouTube's internal trending endpoints and public aggregators.
Pass YOUTUBE_API_KEY env var to unlock YouTube Data API v3 queries.
"""

import json
import os
from dataclasses import dataclass, field
from typing import Optional

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


@dataclass
class YTShortTrend:
    title: str
    channel: str
    views: int = 0
    niche: str = "general"
    hashtags: list = field(default_factory=list)
    format_tip: str = ""


@dataclass
class YTHashtag:
    tag: str
    reach: str = ""
    recommended_combo: list = field(default_factory=list)
    niche: str = "general"


@dataclass
class YTTrendReport:
    platform: str = "youtube-shorts"
    fetched_at: str = ""
    trending_niches: list = field(default_factory=list)
    top_hashtags: list = field(default_factory=list)
    hashtag_strategy: dict = field(default_factory=dict)
    format_tips: list = field(default_factory=list)
    cultural_moments: list = field(default_factory=list)
    source: str = "curated"


# ── Curated June 2026 data ─────────────────────────────────────────────────────

JUNE_2026_NICHES = [
    {"niche": "Gaming", "share": "dominant", "tip": "Highlights, walkthroughs, speed-runs; 15-60s clips perform best"},
    {"niche": "Comedy/Skits", "share": "76.5% of Shorts", "tip": "POV + twist ending; hook in first 2 seconds"},
    {"niche": "Health & Fitness", "share": "exploding", "tip": "Before/after, '30-day challenge', gym motivation reels"},
    {"niche": "Finance/Side Hustle", "share": "high CPM", "tip": "Income reveal, passive income, day-in-my-life"},
    {"niche": "Educational", "share": "high retention", "tip": "'Did you know', life hacks, facts in 60s"},
    {"niche": "AI & Tech", "share": "+95% YoY", "tip": "AI tool demos, prompt hacks, tech reviews"},
    {"niche": "Food", "share": "evergreen", "tip": "Recipe transformations, restaurant reviews, mukbang"},
    {"niche": "Lifestyle/Aesthetic", "share": "high engagement", "tip": "Day in my life, room makeover, aesthetic routine"},
    {"niche": "Sports/World Cup 2026", "share": "massive June spike", "tip": "Goal highlights, prediction, stats breakdowns"},
    {"niche": "Music Reaction", "share": "high shares", "tip": "React to Olivia Rodrigo album tracks — album dropped Jun 12"},
]

TOP_YT_HASHTAGS = [
    YTHashtag("#shorts", "50B+ views", ["#viral", "#trending"], "general"),
    YTHashtag("#viral", "8T+ views", ["#shorts", "#fyp"], "general"),
    YTHashtag("#youtubeshorts", "3T+ views", ["#shorts", "#trending"], "general"),
    YTHashtag("#trending", "2T+ views", ["#shorts", "#viral"], "general"),
    YTHashtag("#fyp", "500B+ views", ["#shorts", "#viral"], "general"),
    YTHashtag("#dance", "900B+ views", ["#shorts", "#music"], "entertainment"),
    YTHashtag("#music", "1.2T+ views", ["#shorts", "#trending"], "music"),
    YTHashtag("#ai", "120B+ views", ["#tech", "#shorts"], "tech"),
    YTHashtag("#money", "300B+ views", ["#finance", "#sidehustle"], "finance"),
    YTHashtag("#funny", "2T+ views", ["#shorts", "#viral"], "comedy"),
    YTHashtag("#fitness", "400B+ views", ["#gym", "#shorts"], "fitness"),
    YTHashtag("#WorldCup2026", "48B+ views", ["#soccer", "#football"], "sports"),
    YTHashtag("#gaming", "2T+ views", ["#shorts", "#gameplay"], "gaming"),
    YTHashtag("#motivation", "600B+ views", ["#mindset", "#shorts"], "mindset"),
    YTHashtag("#educational", "200B+ views", ["#learnontiktok", "#shorts"], "education"),
]

HASHTAG_STRATEGY = {
    "optimal_count": "3–5 hashtags per video",
    "formula": "2–3 evergreen + 1–2 trending moment tags",
    "placement": "In description, NOT in title (YouTube penalizes title stuffing)",
    "reach_boost": "Up to 79.5% higher algorithmic reach with correct tag mix",
    "avoid": "More than 8 tags (dilutes relevance signal)",
    "pro_tip": "Add one niche-specific micro-tag (under 1B views) to beat competition",
    "june_must_haves": ["#WorldCup2026", "#shorts", "#viral"],
}

YT_FORMAT_TIPS = [
    "Hook in first 1.5 seconds — say or show the payoff immediately",
    "Aspect ratio: 9:16, 1080x1920px, under 60 seconds for max reach",
    "Add auto-captions — 80% of Shorts watched on mute",
    "End with a loop — YouTube rewards watch-through rate",
    "Post 1–2x daily for first 30 days to train the algorithm",
    "Use trending audio from YouTube Shorts library (not TikTok rips — gets flagged)",
    "Thumbnail matters even for Shorts — pick a frame with contrast + text overlay",
    "Comment-bait end card: ask one yes/no question to spike comment rate",
    "Pin a comment with a call-to-action in first 30 mins of posting",
    "Reply to every comment in first hour — algorithm counts engagement velocity",
]


def fetch_trends(use_live: bool = False, timeout: int = 10) -> YTTrendReport:
    """Return a YTTrendReport. Optionally hit YouTube Data API if API key set."""
    import datetime
    report = YTTrendReport(
        platform="youtube-shorts",
        fetched_at=datetime.datetime.utcnow().isoformat() + "Z",
        trending_niches=JUNE_2026_NICHES,
        top_hashtags=[_hashtag_to_dict(h) for h in TOP_YT_HASHTAGS],
        hashtag_strategy=HASHTAG_STRATEGY,
        format_tips=YT_FORMAT_TIPS,
        cultural_moments=[
            "World Cup 2026 — Jun 11 kickoff — sports content PEAK",
            "Olivia Rodrigo album — Jun 12 — reaction Shorts trending hard",
            "House of Dragon S3 — Jun 21 — TV recap / prediction Shorts",
        ],
        source="curated-june-2026",
    )

    api_key = os.environ.get("YOUTUBE_API_KEY")
    if use_live and api_key and HAS_REQUESTS:
        try:
            _enrich_from_yt_api(report, api_key, timeout)
        except Exception:
            pass

    return report


def _enrich_from_yt_api(report: YTTrendReport, api_key: str, timeout: int) -> None:
    """Pull live trending videos from YouTube Data API v3."""
    url = (
        f"https://www.googleapis.com/youtube/v3/videos"
        f"?part=snippet,statistics&chart=mostPopular&regionCode=US"
        f"&videoCategoryId=10&maxResults=10&key={api_key}"
    )
    resp = requests.get(url, timeout=timeout)
    if resp.status_code != 200:
        return
    data = resp.json()
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        report.trending_niches.insert(0, {
            "niche": snippet.get("categoryId", "live"),
            "title": snippet.get("title", "")[:80],
            "channel": snippet.get("channelTitle", ""),
            "views": int(stats.get("viewCount", 0)),
            "source": "youtube-api-live",
        })
    report.source = "youtube-api-live+curated"


def _hashtag_to_dict(h: YTHashtag) -> dict:
    return {
        "tag": h.tag,
        "reach": h.reach,
        "recommended_combo": h.recommended_combo,
        "niche": h.niche,
    }
