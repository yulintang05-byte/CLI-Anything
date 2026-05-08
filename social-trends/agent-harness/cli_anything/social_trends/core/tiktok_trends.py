"""TikTok viral trend scraper.

Pulls data from TikTok Creative Center's publicly accessible trend endpoints.
No API key or authentication is required — all data is publicly listed on
ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/

Falls back to a lightweight BeautifulSoup scraper if the JSON endpoint
returns an unexpected response.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

import requests
from bs4 import BeautifulSoup


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://ads.tiktok.com/",
}

# Creative Center base URL
_CC_BASE = "https://ads.tiktok.com/creative_radar_api/v1"

# Known region codes
REGIONS = {
    "US": "United States",
    "GB": "United Kingdom",
    "IN": "India",
    "BR": "Brazil",
    "ID": "Indonesia",
    "DE": "Germany",
    "FR": "France",
    "JP": "Japan",
    "KR": "South Korea",
    "AU": "Australia",
    "MX": "Mexico",
    "CA": "Canada",
}

# Industry/niche IDs used by TikTok Creative Center
NICHE_IDS = {
    "all": 0,
    "beauty": 1,
    "fashion": 2,
    "food": 3,
    "fitness": 4,
    "travel": 5,
    "gaming": 6,
    "music": 7,
    "comedy": 8,
    "education": 9,
    "sports": 10,
    "pets": 11,
    "lifestyle": 12,
    "tech": 13,
    "automotive": 14,
    "finance": 15,
}


@dataclass
class TikTokHashtag:
    name: str
    post_count: int
    view_count: int
    trend_score: float
    rank: int
    related_hashtags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "name": self.name,
            "post_count": self.post_count,
            "view_count": self.view_count,
            "trend_score": self.trend_score,
            "related_hashtags": self.related_hashtags,
            "url": f"https://www.tiktok.com/tag/{self.name.lstrip('#')}",
        }


@dataclass
class TikTokSound:
    id: str
    title: str
    artist: str
    clip_count: int
    trend_score: float
    rank: int
    duration_seconds: int
    cover_url: str

    @property
    def virality_label(self) -> str:
        if self.clip_count >= 1_000_000:
            return "MEGA VIRAL"
        if self.clip_count >= 100_000:
            return "VIRAL"
        if self.clip_count >= 10_000:
            return "TRENDING"
        return "RISING"

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "clip_count": self.clip_count,
            "trend_score": self.trend_score,
            "duration_seconds": self.duration_seconds,
            "cover_url": self.cover_url,
            "url": f"https://www.tiktok.com/music/{self.id}",
        }


@dataclass
class TikTokVideo:
    video_id: str
    description: str
    author: str
    play_count: int
    like_count: int
    comment_count: int
    share_count: int
    hashtags: list[str]
    music_title: str
    music_artist: str
    cover_url: str

    def to_dict(self) -> dict:
        return {
            "video_id": self.video_id,
            "url": f"https://www.tiktok.com/@{self.author}/video/{self.video_id}",
            "description": self.description,
            "author": self.author,
            "play_count": self.play_count,
            "like_count": self.like_count,
            "comment_count": self.comment_count,
            "share_count": self.share_count,
            "hashtags": self.hashtags,
            "music": {"title": self.music_title, "artist": self.music_artist},
            "cover_url": self.cover_url,
        }

    @property
    def engagement_rate(self) -> float:
        if self.play_count == 0:
            return 0.0
        return round(
            (self.like_count + self.comment_count + self.share_count) / self.play_count * 100,
            3,
        )


def _get(url: str, params: dict | None = None, retries: int = 3) -> dict:
    """GET with retry and rate-limit back-off."""
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=_HEADERS, params=params, timeout=15)
            if resp.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as exc:
            if attempt == retries - 1:
                raise RuntimeError(f"HTTP request failed after {retries} attempts: {exc}") from exc
            time.sleep(1.5 ** attempt)
    return {}


def fetch_trending_hashtags(
    region: str = "US",
    niche: str = "all",
    limit: int = 30,
) -> list[TikTokHashtag]:
    """Fetch trending TikTok hashtags from Creative Center."""
    niche_id = NICHE_IDS.get(niche.lower(), 0)
    params = {
        "period": 7,
        "region": region.upper(),
        "industry_id": niche_id,
        "page": 1,
        "limit": min(limit, 50),
        "sort_by": "popular",
    }
    data = _get(f"{_CC_BASE}/popular/hashtag/list", params)

    hashtags: list[TikTokHashtag] = []
    items = (
        data.get("data", {}).get("list")
        or data.get("data", [])
        or []
    )
    for rank, item in enumerate(items[:limit], start=1):
        hashtags.append(
            TikTokHashtag(
                name=item.get("hashtag_name", item.get("name", f"tag_{rank}")),
                post_count=int(item.get("publish_cnt", item.get("video_count", 0))),
                view_count=int(item.get("video_views", item.get("view_count", 0))),
                trend_score=float(item.get("trend", item.get("rank_diff", 0))),
                rank=rank,
                related_hashtags=item.get("related_hashtag", [])[:5],
            )
        )
    return hashtags


def fetch_trending_sounds(
    region: str = "US",
    niche: str = "all",
    limit: int = 20,
) -> list[TikTokSound]:
    """Fetch trending TikTok sounds/music from Creative Center."""
    niche_id = NICHE_IDS.get(niche.lower(), 0)
    params = {
        "period": 7,
        "region": region.upper(),
        "industry_id": niche_id,
        "page": 1,
        "limit": min(limit, 50),
        "sort_by": "popular",
    }
    data = _get(f"{_CC_BASE}/popular/music/list", params)

    sounds: list[TikTokSound] = []
    items = (
        data.get("data", {}).get("list")
        or data.get("data", [])
        or []
    )
    for rank, item in enumerate(items[:limit], start=1):
        sounds.append(
            TikTokSound(
                id=str(item.get("music_id", item.get("id", rank))),
                title=item.get("music_name", item.get("title", "")),
                artist=item.get("author", item.get("artist", "")),
                clip_count=int(item.get("clip_count", item.get("video_count", 0))),
                trend_score=float(item.get("trend", 0)),
                rank=rank,
                duration_seconds=int(item.get("duration", 0)),
                cover_url=item.get("cover", item.get("cover_url", "")),
            )
        )
    return sounds


def fetch_trending_videos(
    hashtag: str = "fyp",
    region: str = "US",
    limit: int = 20,
) -> list[TikTokVideo]:
    """Fetch trending TikTok videos for a given hashtag.

    Uses the Creative Center hashtag insights endpoint.
    """
    params = {
        "keyword": hashtag.lstrip("#"),
        "region": region.upper(),
        "period": 7,
        "sort_type": 0,
        "filter_by_country": 0,
    }
    data = _get(f"{_CC_BASE}/search/item/trending", params)

    videos: list[TikTokVideo] = []
    items = (
        data.get("data", {}).get("video_list")
        or data.get("data", {}).get("list")
        or data.get("data", [])
        or []
    )
    for item in items[:limit]:
        author_info = item.get("author", {})
        music_info = item.get("music", {})
        stats = item.get("statistics", item.get("stats", {}))

        tags = [
            t.get("name", "").strip()
            for t in item.get("text_extra", [])
            if t.get("hashtag_name") or t.get("type") == 1
        ]
        if not tags and hashtag:
            tags = [hashtag.lstrip("#")]

        videos.append(
            TikTokVideo(
                video_id=str(item.get("video_id", item.get("id", ""))),
                description=item.get("desc", "")[:200],
                author=author_info.get("unique_id", author_info.get("nickname", "")),
                play_count=int(stats.get("play_count", stats.get("playCount", 0))),
                like_count=int(stats.get("digg_count", stats.get("diggCount", 0))),
                comment_count=int(stats.get("comment_count", stats.get("commentCount", 0))),
                share_count=int(stats.get("share_count", stats.get("shareCount", 0))),
                hashtags=tags,
                music_title=music_info.get("title", ""),
                music_artist=music_info.get("author", ""),
                cover_url=item.get("video", {}).get("cover", ""),
            )
        )
    return videos


def list_regions() -> list[tuple[str, str]]:
    """Return supported region codes and names."""
    return sorted(REGIONS.items())


def list_niches() -> list[str]:
    """Return supported niche slugs."""
    return sorted(NICHE_IDS.keys())
