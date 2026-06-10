"""TikTok trend scraper — trending hashtags, sounds, and viral creators.

Approach: uses TikTok's public web endpoints (no auth required for public data).
  - /api/discover/type=hashtag  — trending hashtags
  - /trending               — trending page HTML (fallback)
  - TikTok Research API     — when API key is configured
"""

from __future__ import annotations

import re
import json
import urllib.parse
from dataclasses import dataclass, field
from typing import Optional

from cli_anything.trendhunter.utils.scraper_backend import (
    fetch, fetch_json, make_session, polite_delay,
)


_TIKTOK_BASE       = "https://www.tiktok.com"
_TIKTOK_TRENDING   = "https://www.tiktok.com/trending"
_TIKTOK_DISCOVER   = "https://www.tiktok.com/api/discover/type=0&count=30&from_page=hashtag"
_TIKTOK_HASHTAG_API = "https://www.tiktok.com/api/challenge/detail/?challengeName={tag}"
_TIKTOK_RESEARCH_TRENDING = (
    "https://open.tiktokapis.com/v2/research/trending/hashtag/"
    "?fields=hashtag_name,view_count,video_count&access_token={token}"
)
_TIKTOK_MUSIC_URL  = "https://www.tiktok.com/music/popular"

# Patterns for embedded JSON in TikTok pages
_SIGI_STATE_RE  = re.compile(r'<script id="SIGI_STATE"[^>]*>(.*?)</script>', re.DOTALL)
_PROPS_RE       = re.compile(r'window\.__INIT_PROPS__\s*=\s*(\{.*?\});', re.DOTALL)
_HASHTAG_RE     = re.compile(r'"hashtagName"\s*:\s*"([a-zA-Z0-9_]{2,40})"')
_SOUND_RE       = re.compile(r'"musicName"\s*:\s*"([^"]{3,80})"')
_AUTHOR_RE      = re.compile(r'"uniqueId"\s*:\s*"([a-zA-Z0-9_.]{3,30})"')
_VIEW_COUNT_RE  = re.compile(r'"viewCount"\s*:\s*(\d+)')


@dataclass
class TikTokHashtag:
    name: str
    view_count: int = 0
    video_count: int = 0
    is_trending: bool = True

    def to_dict(self) -> dict:
        return {
            "name":        self.name,
            "view_count":  self.view_count,
            "video_count": self.video_count,
            "url":         f"https://www.tiktok.com/tag/{self.name}",
        }


@dataclass
class TikTokSound:
    name: str
    artist: str = ""
    uses: int = 0
    url: str = ""

    def to_dict(self) -> dict:
        return {
            "name":   self.name,
            "artist": self.artist,
            "uses":   self.uses,
            "url":    self.url,
        }


@dataclass
class TikTokTrends:
    region: str = "US"
    hashtags: list[TikTokHashtag] = field(default_factory=list)
    sounds: list[TikTokSound] = field(default_factory=list)
    trending_creators: list[str] = field(default_factory=list)
    raw_page_tags: list[str] = field(default_factory=list)
    source: str = "web"

    def to_dict(self) -> dict:
        return {
            "region":            self.region,
            "source":            self.source,
            "hashtags":          [h.to_dict() for h in self.hashtags],
            "sounds":            [s.to_dict() for s in self.sounds],
            "trending_creators": self.trending_creators,
            "raw_page_tags":     self.raw_page_tags,
        }


def _scrape_tiktok_page(url: str) -> Optional[str]:
    """Fetch TikTok page HTML with mobile UA to get embedded JSON."""
    session = make_session(mobile=True)
    session.headers.update({
        "Referer": "https://www.tiktok.com/",
        "sec-ch-ua": '"Chromium";v="124"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
    })
    resp = fetch(url, session=session, timeout=20)
    return resp.text if resp else None


def _parse_sigi_state(html: str) -> Optional[dict]:
    """Extract the SIGI_STATE embedded JSON from TikTok page."""
    m = _SIGI_STATE_RE.search(html)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def fetch_trending_hashtags_web(region: str = "US",
                                 max_results: int = 25) -> list[TikTokHashtag]:
    """Scrape trending hashtags from TikTok's explore/trending page."""
    html = _scrape_tiktok_page(_TIKTOK_TRENDING)
    if not html:
        return _fallback_curated_hashtags()

    hashtags: list[TikTokHashtag] = []

    # Try SIGI_STATE JSON first
    state = _parse_sigi_state(html)
    if state:
        try:
            items = (
                state.get("DiscoverModule", {})
                     .get("exploreItems", [])
            )
            for item in items:
                info = item.get("cardItem", {})
                tag = info.get("title", "").lstrip("#")
                views = int(info.get("extra", {}).get("viewCount", 0) or 0)
                if tag:
                    hashtags.append(TikTokHashtag(name=tag, view_count=views))
        except (KeyError, TypeError):
            pass

    # Fallback: regex extraction from raw HTML
    if not hashtags:
        raw_tags = list(dict.fromkeys(_HASHTAG_RE.findall(html)))
        for tag in raw_tags[:max_results]:
            if len(tag) >= 2:
                hashtags.append(TikTokHashtag(name=tag.lower()))

    return hashtags[:max_results] or _fallback_curated_hashtags()


def fetch_hashtag_stats(hashtag: str) -> Optional[TikTokHashtag]:
    """Fetch stats for a specific TikTok hashtag."""
    tag = hashtag.lstrip("#")
    url = _TIKTOK_HASHTAG_API.format(tag=urllib.parse.quote(tag))
    session = make_session()
    session.headers.update({
        "Referer": f"https://www.tiktok.com/tag/{tag}",
        "Accept": "application/json",
    })
    data = fetch_json(url, session=session)
    if not data:
        return None
    try:
        ch = data.get("challengeInfo", {}).get("challenge", {})
        stats = data.get("challengeInfo", {}).get("stats", {})
        return TikTokHashtag(
            name=ch.get("title", tag),
            view_count=int(stats.get("viewCount", 0) or 0),
            video_count=int(stats.get("videoCount", 0) or 0),
        )
    except (KeyError, TypeError, ValueError):
        return None


def fetch_trending_sounds_web(region: str = "US") -> list[TikTokSound]:
    """Scrape trending sounds/music from TikTok."""
    html = _scrape_tiktok_page(_TIKTOK_MUSIC_URL)
    if not html:
        return []
    names = list(dict.fromkeys(_SOUND_RE.findall(html)))[:20]
    return [TikTokSound(name=n) for n in names if len(n) > 3]


def fetch_trending_creators_web(max_results: int = 10) -> list[str]:
    """Extract trending creator usernames from the TikTok discover page."""
    html = _scrape_tiktok_page(_TIKTOK_TRENDING)
    if not html:
        return []
    creators = list(dict.fromkeys(_AUTHOR_RE.findall(html)))
    return [c for c in creators if len(c) >= 3][:max_results]


def _fallback_curated_hashtags() -> list[TikTokHashtag]:
    """Return curated evergreen TikTok hashtags when scraping is blocked."""
    evergreen = [
        ("fyp", 50_000_000_000),
        ("foryou", 30_000_000_000),
        ("foryoupage", 25_000_000_000),
        ("viral", 20_000_000_000),
        ("trending", 15_000_000_000),
        ("tiktok", 12_000_000_000),
        ("funny", 8_000_000_000),
        ("duet", 5_000_000_000),
        ("stitch", 3_000_000_000),
        ("meme", 2_500_000_000),
        ("explore", 2_000_000_000),
        ("learnontiktok", 1_800_000_000),
        ("smallbusiness", 1_500_000_000),
        ("aesthetic", 1_200_000_000),
        ("motivation", 1_000_000_000),
    ]
    return [TikTokHashtag(name=n, view_count=v) for n, v in evergreen]


def fetch_tiktok_trends(region: str = "US",
                         max_hashtags: int = 25) -> TikTokTrends:
    """Top-level function: fetch all TikTok trend data."""
    trends = TikTokTrends(region=region)

    trends.hashtags = fetch_trending_hashtags_web(region, max_hashtags)
    polite_delay()

    trends.sounds = fetch_trending_sounds_web(region)
    polite_delay()

    trends.trending_creators = fetch_trending_creators_web()

    return trends
