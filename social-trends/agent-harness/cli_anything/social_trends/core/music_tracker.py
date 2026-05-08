"""Viral music and sound tracker.

Aggregates trending audio from TikTok Creative Center and YouTube Music
into a unified feed, ranked by virality signals.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import requests


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

_CC_BASE = "https://ads.tiktok.com/creative_radar_api/v1"


@dataclass
class TrackEntry:
    title: str
    artist: str
    platform: str            # "tiktok" | "youtube" | "both"
    clip_count: int          # number of videos using this track
    trend_score: float       # platform-specific trend score
    duration_seconds: int
    cover_url: str
    track_url: str
    rank: int
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "title": self.title,
            "artist": self.artist,
            "platform": self.platform,
            "clip_count": self.clip_count,
            "trend_score": self.trend_score,
            "duration_seconds": self.duration_seconds,
            "cover_url": self.cover_url,
            "track_url": self.track_url,
            "tags": self.tags,
        }

    @property
    def virality_label(self) -> str:
        if self.clip_count >= 1_000_000:
            return "MEGA VIRAL"
        if self.clip_count >= 100_000:
            return "VIRAL"
        if self.clip_count >= 10_000:
            return "TRENDING"
        return "RISING"


def fetch_tiktok_music(
    region: str = "US",
    niche: str = "all",
    limit: int = 20,
) -> list[TrackEntry]:
    """Fetch trending TikTok sounds from Creative Center."""
    from cli_anything.social_trends.core.tiktok_trends import (
        fetch_trending_sounds,
        NICHE_IDS,
    )

    sounds = fetch_trending_sounds(region=region, niche=niche, limit=limit)
    tracks: list[TrackEntry] = []
    for s in sounds:
        tracks.append(
            TrackEntry(
                title=s.title,
                artist=s.artist,
                platform="tiktok",
                clip_count=s.clip_count,
                trend_score=s.trend_score,
                duration_seconds=s.duration_seconds,
                cover_url=s.cover_url,
                track_url=f"https://www.tiktok.com/music/{s.id}",
                rank=s.rank,
            )
        )
    return tracks


def fetch_youtube_music_charts(
    region: str = "US",
    limit: int = 20,
    api_key: str | None = None,
) -> list[TrackEntry]:
    """Fetch trending music videos from YouTube (music category).

    Uses the youtube_trends module — requires YOUTUBE_API_KEY or yt-dlp.
    """
    import os
    from cli_anything.social_trends.core.youtube_trends import fetch_trending

    key = api_key or os.environ.get("YOUTUBE_API_KEY")
    videos = fetch_trending(region=region, category="music", max_results=limit, api_key=key)

    tracks: list[TrackEntry] = []
    for rank, v in enumerate(videos, start=1):
        tracks.append(
            TrackEntry(
                title=v.title,
                artist=v.channel,
                platform="youtube",
                clip_count=v.view_count,
                trend_score=float(v.engagement_rate),
                duration_seconds=0,
                cover_url=v.thumbnail_url,
                track_url=v.url,
                rank=rank,
                tags=v.tags[:10],
            )
        )
    return tracks


def merge_tracks(
    tiktok: list[TrackEntry],
    youtube: list[TrackEntry],
) -> list[TrackEntry]:
    """Merge TikTok and YouTube tracks, boosting cross-platform presence."""
    index: dict[str, TrackEntry] = {}

    def _key(t: TrackEntry) -> str:
        return f"{t.title.lower().strip()}|{t.artist.lower().strip()}"

    for t in tiktok:
        index[_key(t)] = t

    merged: list[TrackEntry] = list(index.values())
    for yt in youtube:
        k = _key(yt)
        if k in index:
            existing = index[k]
            existing.platform = "both"
            existing.trend_score = round(existing.trend_score * 1.3, 2)
            existing.tags = list(set(existing.tags + yt.tags))
        else:
            merged.append(yt)

    merged.sort(key=lambda t: t.trend_score + t.clip_count / 1e6, reverse=True)
    for i, t in enumerate(merged, start=1):
        t.rank = i
    return merged


def search_track_virality(
    title: str,
    artist: str = "",
) -> dict:
    """Look up a specific song's TikTok usage stats.

    Queries Creative Center search endpoint.
    """
    params = {
        "keyword": f"{title} {artist}".strip(),
        "sort_by": "popular",
        "page": 1,
        "limit": 5,
    }
    try:
        resp = requests.get(
            f"{_CC_BASE}/popular/music/search",
            headers=_HEADERS,
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        items = data.get("data", {}).get("list") or []
        if not items:
            return {"found": False, "title": title, "artist": artist, "results": []}

        results = []
        for item in items[:3]:
            results.append({
                "title": item.get("music_name", ""),
                "artist": item.get("author", ""),
                "clip_count": int(item.get("clip_count", 0)),
                "trend_score": float(item.get("trend", 0)),
                "url": f"https://www.tiktok.com/music/{item.get('music_id', '')}",
            })
        return {"found": True, "title": title, "artist": artist, "results": results}
    except Exception as exc:
        return {"found": False, "error": str(exc), "title": title, "artist": artist}


def identify_trending_genres(tracks: list[TrackEntry]) -> dict[str, int]:
    """Heuristically bucket tracks into genre groups by keyword matching."""
    GENRE_KEYWORDS: dict[str, list[str]] = {
        "hip_hop_rap": ["rap", "hip hop", "drill", "trap", "bars", "flow"],
        "pop": ["pop", "radio", "hit", "chart"],
        "electronic_edm": ["edm", "house", "techno", "dnb", "rave", "beat", "loop"],
        "rnb_soul": ["r&b", "rnb", "soul", "smooth"],
        "latin": ["reggaeton", "latin", "salsa", "cumbia", "bachata"],
        "country": ["country", "western", "bluegrass"],
        "rock_alternative": ["rock", "metal", "punk", "indie", "alternative"],
        "phonk": ["phonk", "drift"],
        "afrobeats": ["afro", "amapiano", "afrobeats"],
        "other": [],
    }

    genre_counts: dict[str, int] = {g: 0 for g in GENRE_KEYWORDS}
    for track in tracks:
        text = (track.title + " " + track.artist).lower()
        matched = False
        for genre, keywords in GENRE_KEYWORDS.items():
            if genre == "other":
                continue
            for kw in keywords:
                if kw in text:
                    genre_counts[genre] += 1
                    matched = True
                    break
            if matched:
                break
        if not matched:
            genre_counts["other"] += 1

    return {k: v for k, v in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True) if v > 0}
