"""Trending music/sound tracker for TikTok and YouTube."""
from __future__ import annotations
from collections import Counter
from typing import Any

from .trends import fetch_tiktok_trending, fetch_youtube_trending, HEADERS

import requests


def fetch_trending_music(
    platform: str = "all",
    limit: int = 20,
    region: str = "US",
) -> list[dict[str, Any]]:
    """
    Aggregate trending music from TikTok and/or YouTube.

    platform: 'tiktok' | 'youtube' | 'all'
    """
    results: list[dict[str, Any]] = []

    if platform in ("tiktok", "all"):
        tt_items = fetch_tiktok_trending(limit=50, region=region)
        results.extend(_extract_tt_music(tt_items, limit))

    if platform in ("youtube", "all"):
        yt_items = fetch_youtube_trending(category="music", country=region, limit=50)
        results.extend(_extract_yt_music(yt_items, limit))

    return _deduplicate_music(results)[:limit]


def _extract_tt_music(items: list[dict], top_n: int) -> list[dict[str, Any]]:
    """Count and rank TikTok sounds by how many trending videos use them."""
    counts: Counter[str] = Counter()
    meta: dict[str, dict] = {}

    for item in items:
        if "error" in item:
            continue
        mid = item.get("music_id", "")
        title = item.get("music_title", "")
        author = item.get("music_author", "")
        if not mid and not title:
            continue
        key = mid or title
        counts[key] += 1
        if key not in meta:
            meta[key] = {
                "source": "tiktok",
                "music_id": mid,
                "title": title,
                "artist": author,
                "url": f"https://www.tiktok.com/music/{title.replace(' ', '-')}-{mid}" if mid else "",
            }

    ranked = []
    for key, count in counts.most_common(top_n):
        entry = {**meta[key], "trending_video_count": count}
        ranked.append(entry)
    return ranked


def _extract_yt_music(items: list[dict], top_n: int) -> list[dict[str, Any]]:
    """Convert YouTube music trending videos into music records."""
    results = []
    for item in items[:top_n]:
        if "error" in item:
            continue
        results.append(
            {
                "source": "youtube",
                "video_id": item.get("video_id", ""),
                "title": item.get("title", ""),
                "artist": item.get("channel", ""),
                "views": item.get("views", ""),
                "url": item.get("url", ""),
                "duration": item.get("duration", ""),
                "published": item.get("published", ""),
            }
        )
    return results


def _deduplicate_music(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for item in items:
        key = (item.get("music_id") or item.get("video_id") or item.get("title", "")).lower()
        if key and key not in seen:
            seen.add(key)
            out.append(item)
    return out


def fetch_tiktok_sounds_chart(limit: int = 20) -> list[dict[str, Any]]:
    """
    Pull TikTok Creative Center trending sounds (public endpoint).
    """
    url = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/music/list"
    params = {
        "page": 1,
        "limit": limit,
        "period": 7,
        "country_code": "US",
    }
    headers = {
        **HEADERS,
        "Referer": "https://ads.tiktok.com/business/creativecenter/music/pc/en",
    }
    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        music_list = data.get("data", {}).get("music_list", [])
        return [_parse_cc_music(m) for m in music_list[:limit]]
    except Exception as exc:  # noqa: BLE001
        return [{"error": str(exc), "source": "tiktok_creative_center"}]


def _parse_cc_music(m: dict) -> dict[str, Any]:
    return {
        "source": "tiktok_creative_center",
        "music_id": str(m.get("music_id", "")),
        "title": m.get("music_title", ""),
        "artist": m.get("author", ""),
        "clip_url": m.get("clip_url", ""),
        "duration": m.get("duration", 0),
        "rank": m.get("rank", 0),
        "rank_diff": m.get("rank_diff", 0),
        "usage_count": m.get("item_count", 0),
        "cover_url": m.get("cover_url", ""),
    }
