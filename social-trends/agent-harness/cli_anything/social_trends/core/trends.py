"""Trend orchestrator — fetch, cache, and analyze cross-platform trends."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cli_anything.social_trends.utils import tiktok_scraper, youtube_scraper

CACHE_DIR = Path.home() / ".cli-anything-social-trends" / "cache"
CACHE_TTL_SECONDS = 3600  # 1 hour


def _cache_path(key: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    safe = key.replace("/", "_").replace(":", "_")
    return CACHE_DIR / f"{safe}.json"


def _load_cache(key: str) -> dict | None:
    p = _cache_path(key)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text())
        age = time.time() - data.get("_cached_at", 0)
        if age > CACHE_TTL_SECONDS:
            return None
        return data
    except (json.JSONDecodeError, KeyError):
        return None


def _save_cache(key: str, data: dict) -> None:
    data["_cached_at"] = time.time()
    _cache_path(key).write_text(json.dumps(data, indent=2, default=str))


def fetch_tiktok_trends(
    country: str = "US",
    period: int = 7,
    hashtag_limit: int = 20,
    sound_limit: int = 20,
    video_limit: int = 10,
    creator_limit: int = 10,
    use_cache: bool = True,
    delay: float = 0.5,
) -> dict:
    """Fetch and optionally cache TikTok trend report."""
    cache_key = f"tiktok_{country.upper()}_{period}d"
    if use_cache:
        cached = _load_cache(cache_key)
        if cached:
            cached["from_cache"] = True
            return cached

    report = tiktok_scraper.full_trend_report(
        country=country,
        period=period,
        hashtag_limit=hashtag_limit,
        sound_limit=sound_limit,
        video_limit=video_limit,
        creator_limit=creator_limit,
        delay=delay,
    )
    if use_cache:
        _save_cache(cache_key, report)
    report["from_cache"] = False
    return report


def fetch_youtube_trends(
    region: str = "US",
    limit: int = 20,
    api_key: str | None = None,
    use_cache: bool = True,
    delay: float = 0.5,
) -> dict:
    """Fetch and optionally cache YouTube trend report."""
    cache_key = f"youtube_{region.upper()}"
    if use_cache:
        cached = _load_cache(cache_key)
        if cached:
            cached["from_cache"] = True
            return cached

    report = youtube_scraper.full_trend_report(
        region=region,
        limit=limit,
        api_key=api_key,
        delay=delay,
    )
    if use_cache:
        _save_cache(cache_key, report)
    report["from_cache"] = False
    return report


def cross_platform_report(
    country: str = "US",
    period: int = 7,
    youtube_api_key: str | None = None,
    limit: int = 20,
    use_cache: bool = True,
) -> dict:
    """Combined TikTok + YouTube trend analysis with cross-platform insights.

    Returns:
        Report with platform data, shared trending audio, overlapping hashtags,
        and actionable content recommendations.
    """
    tiktok = fetch_tiktok_trends(
        country=country, period=period,
        hashtag_limit=limit, sound_limit=limit,
        video_limit=limit // 2, creator_limit=10,
        use_cache=use_cache,
    )
    youtube = fetch_youtube_trends(
        region=country, limit=limit,
        api_key=youtube_api_key, use_cache=use_cache,
    )

    # Extract top hashtags from TikTok
    top_hashtags = [h["name"] for h in tiktok.get("hashtags", [])[:10]]

    # Extract top sounds from TikTok
    top_sounds = [
        {"title": s["title"], "artist": s["artist"], "usage_count": s["usage_count"]}
        for s in tiktok.get("sounds", [])[:10]
    ]

    # Extract YouTube trending titles to find shared themes
    yt_titles = [v.get("title", "") for v in youtube.get("trending_all", [])[:10]]
    yt_music_titles = [v.get("title", "") for v in youtube.get("trending_music", [])[:10]]

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "country": country.upper(),
        "period_days": period,
        "tiktok": tiktok,
        "youtube": youtube,
        "insights": {
            "top_tiktok_hashtags": top_hashtags,
            "top_tiktok_sounds": top_sounds,
            "youtube_trending_videos": yt_titles,
            "youtube_trending_music": yt_music_titles,
            "content_opportunities": _derive_opportunities(
                top_hashtags, top_sounds, yt_titles, yt_music_titles
            ),
        },
    }
    return report


def _derive_opportunities(
    hashtags: list[str],
    sounds: list[dict],
    yt_titles: list[str],
    yt_music: list[str],
) -> list[dict]:
    """Derive content opportunities from cross-platform trends."""
    opportunities = []

    # Hashtag-based opportunities
    for tag in hashtags[:5]:
        opportunities.append({
            "type": "hashtag_trend",
            "action": f"Create content around #{tag}",
            "platforms": ["TikTok", "Instagram Reels", "YouTube Shorts"],
            "priority": "high",
        })

    # Sound-based opportunities
    for sound in sounds[:3]:
        opportunities.append({
            "type": "trending_sound",
            "action": f"Use trending sound: '{sound['title']}' by {sound['artist']}",
            "platforms": ["TikTok", "Instagram Reels"],
            "usage_count": sound.get("usage_count", 0),
            "priority": "high",
        })

    # YouTube topic cross-posting
    for title in yt_titles[:3]:
        # Shorten to a topic hint
        short = title[:60] + "..." if len(title) > 60 else title
        opportunities.append({
            "type": "cross_platform_topic",
            "action": f"Create short-form version of trending topic: '{short}'",
            "platforms": ["YouTube Shorts", "TikTok"],
            "priority": "medium",
        })

    return opportunities


def clear_cache(country: str | None = None) -> dict:
    """Clear cached trend data."""
    if not CACHE_DIR.exists():
        return {"cleared": 0}

    cleared = 0
    for f in CACHE_DIR.glob("*.json"):
        if country is None or country.upper() in f.name.upper():
            f.unlink()
            cleared += 1
    return {"cleared": cleared}


def list_cached() -> list[dict]:
    """List all cached trend reports."""
    if not CACHE_DIR.exists():
        return []
    results = []
    for f in sorted(CACHE_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            age_s = time.time() - data.get("_cached_at", 0)
            results.append({
                "file": f.name,
                "platform": data.get("platform", "unknown"),
                "country": data.get("country", data.get("region", "?")),
                "age_minutes": round(age_s / 60, 1),
                "expired": age_s > CACHE_TTL_SECONDS,
            })
        except Exception:
            pass
    return results
