"""TikTok trend research client.

Uses the TikTok Research API (https://developers.tiktok.com/products/research-api/)
for authorized research access, and TikTok for Developers Creative API for
sound/hashtag discovery.

Environment variables:
    TIKTOK_CLIENT_KEY     — TikTok app client key
    TIKTOK_CLIENT_SECRET  — TikTok app client secret

Apply for Research API access at: https://developers.tiktok.com/
For hashtag/sound data without Research API, the module provides
estimated trend data via heuristic scoring.
"""

from __future__ import annotations

import os
import time
from typing import Any


# ── Credential helpers ─────────────────────────────────────────────────

def _get_credentials() -> tuple[str, str]:
    key = os.environ.get("TIKTOK_CLIENT_KEY", "")
    secret = os.environ.get("TIKTOK_CLIENT_SECRET", "")
    if not key or not secret:
        raise EnvironmentError(
            "TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET not set.\n"
            "Apply for TikTok Research API access at: https://developers.tiktok.com/\n"
            "Use --mock flag to run with sample data."
        )
    return key, secret


def _get_access_token(client_key: str, client_secret: str) -> str:
    """Obtain a client credentials access token from TikTok OAuth 2.0."""
    import urllib.request
    import urllib.parse
    import json

    data = urllib.parse.urlencode({
        "client_key": client_key,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }).encode()

    req = urllib.request.Request(
        "https://open.tiktokapis.com/v2/oauth/token/",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())["access_token"]


# ── Research API queries ───────────────────────────────────────────────

def query_videos(
    keywords: list[str],
    region: str = "US",
    max_count: int = 20,
    days_back: int = 7,
) -> list[dict[str, Any]]:
    """Query TikTok Research API for videos matching keywords.

    Requires approved Research API access.

    Args:
        keywords: List of search keywords / hashtags (without #).
        region:   ISO region code.
        max_count: Max videos to return (API max = 100).
        days_back: Search window in days from today.

    Returns:
        List of video dicts with: id, author, create_time, view_count,
        like_count, comment_count, share_count, hashtag_names, music_id,
        music_title, url, score.
    """
    import json
    import datetime
    import urllib.request

    client_key, client_secret = _get_credentials()
    token = _get_access_token(client_key, client_secret)

    now = datetime.datetime.utcnow()
    start = now - datetime.timedelta(days=days_back)

    payload = json.dumps({
        "query": {
            "and": [
                {"operation": "IN", "field_name": "keyword", "field_values": keywords},
                {"operation": "EQ", "field_name": "region_code", "field_values": [region]},
            ]
        },
        "start_date": start.strftime("%Y%m%d"),
        "end_date": now.strftime("%Y%m%d"),
        "max_count": min(max_count, 100),
        "cursor": 0,
        "search_id": "",
        "fields": (
            "id,author_name,create_time,view_count,like_count,"
            "comment_count,share_count,hashtag_names,music_id,video_description"
        ),
    }).encode()

    req = urllib.request.Request(
        "https://open.tiktokapis.com/v2/research/video/query/",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=20) as resp:
        body = json.loads(resp.read())

    videos = body.get("data", {}).get("videos", [])
    results = []
    for v in videos:
        score = _score_tiktok(v)
        results.append({
            "id": v.get("id", ""),
            "author": v.get("author_name", ""),
            "created_at": v.get("create_time", ""),
            "views": v.get("view_count", 0),
            "likes": v.get("like_count", 0),
            "comments": v.get("comment_count", 0),
            "shares": v.get("share_count", 0),
            "hashtags": v.get("hashtag_names", []),
            "description": v.get("video_description", ""),
            "music_id": v.get("music_id", ""),
            "url": f"https://www.tiktok.com/@{v.get('author_name', 'user')}/video/{v.get('id', '')}",
            "score": score,
            "region": region,
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)


def query_trending_hashtags(
    keywords: list[str],
    region: str = "US",
    days_back: int = 3,
    top_n: int = 30,
) -> list[dict[str, Any]]:
    """Derive trending hashtags from video query results.

    Returns dicts with: tag, frequency, avg_views, avg_likes, score, platform.
    """
    videos = query_videos(keywords, region=region, days_back=days_back, max_count=100)
    return _aggregate_hashtags(videos, top_n=top_n)


def query_trending_sounds(
    keywords: list[str],
    region: str = "US",
    days_back: int = 7,
    top_n: int = 20,
) -> list[dict[str, Any]]:
    """Derive trending music/sounds from video query results.

    Returns dicts with: music_id, frequency, avg_views, score, platform.
    """
    videos = query_videos(keywords, region=region, days_back=days_back, max_count=100)
    return _aggregate_sounds(videos, top_n=top_n)


# ── Mock data (for demo / testing without API key) ────────────────────

MOCK_TIKTOK_TRENDS = [
    {
        "id": "mock_001", "author": "trendsetter99", "created_at": "2025-01-01T00:00:00Z",
        "views": 4_200_000, "likes": 380_000, "comments": 12_000, "shares": 45_000,
        "hashtags": ["fyp", "viral", "trending", "motivation", "grwm"],
        "description": "Morning routine that changed my life #fyp #viral #motivation",
        "music_id": "7000001", "url": "https://www.tiktok.com/@trendsetter99/video/mock_001",
        "score": 920.5, "region": "US",
    },
    {
        "id": "mock_002", "author": "luxurylifestyle", "created_at": "2025-01-02T00:00:00Z",
        "views": 3_100_000, "likes": 290_000, "comments": 8_500, "shares": 31_000,
        "hashtags": ["luxury", "lifestyle", "aesthetic", "fyp", "rich"],
        "description": "Day in my life as a millionaire #luxury #lifestyle #fyp",
        "music_id": "7000002", "url": "https://www.tiktok.com/@luxurylifestyle/video/mock_002",
        "score": 880.2, "region": "US",
    },
    {
        "id": "mock_003", "author": "fitnessguru", "created_at": "2025-01-03T00:00:00Z",
        "views": 2_800_000, "likes": 270_000, "comments": 9_200, "shares": 28_000,
        "hashtags": ["fitness", "workout", "gym", "fyp", "transformation"],
        "description": "6 month body transformation #fitness #gym #transformation",
        "music_id": "7000003", "url": "https://www.tiktok.com/@fitnessguru/video/mock_003",
        "score": 850.1, "region": "US",
    },
    {
        "id": "mock_004", "author": "foodcreator", "created_at": "2025-01-04T00:00:00Z",
        "views": 5_600_000, "likes": 490_000, "comments": 15_000, "shares": 62_000,
        "hashtags": ["food", "recipe", "cooking", "fyp", "foodtok"],
        "description": "Viral pasta recipe everyone is making #food #recipe #foodtok",
        "music_id": "7000004", "url": "https://www.tiktok.com/@foodcreator/video/mock_004",
        "score": 960.8, "region": "US",
    },
    {
        "id": "mock_005", "author": "smallbusiness", "created_at": "2025-01-05T00:00:00Z",
        "views": 1_900_000, "likes": 180_000, "comments": 7_800, "shares": 22_000,
        "hashtags": ["smallbusiness", "entrepreneur", "hustle", "fyp", "money"],
        "description": "How I made $10k last month from my phone #smallbusiness #entrepreneur",
        "music_id": "7000005", "url": "https://www.tiktok.com/@smallbusiness/video/mock_005",
        "score": 810.4, "region": "US",
    },
]

MOCK_SOUNDS = [
    {"music_id": "7000001", "title": "MONTAGEM ORBITAL", "artist": "DJ HB", "frequency": 45, "avg_views": 3_200_000, "score": 980},
    {"music_id": "7000002", "title": "Cruel Summer", "artist": "Taylor Swift", "frequency": 38, "avg_views": 2_800_000, "score": 940},
    {"music_id": "7000003", "title": "Espresso", "artist": "Sabrina Carpenter", "frequency": 42, "avg_views": 3_500_000, "score": 970},
    {"music_id": "7000004", "title": "Harleys in Hawaii", "artist": "Katy Perry", "frequency": 29, "avg_views": 1_900_000, "score": 890},
    {"music_id": "7000005", "title": "Original Sound", "artist": "@viral_audio", "frequency": 62, "avg_views": 4_100_000, "score": 995},
]


def fetch_mock_trends(region: str = "US") -> list[dict[str, Any]]:
    """Return mock TikTok trend data for demo/testing."""
    return [dict(t, region=region) for t in MOCK_TIKTOK_TRENDS]


def fetch_mock_sounds() -> list[dict[str, Any]]:
    """Return mock trending sounds for demo/testing."""
    return list(MOCK_SOUNDS)


# ── Internal helpers ───────────────────────────────────────────────────

def _score_tiktok(v: dict[str, Any]) -> float:
    import math
    views = v.get("view_count", 0)
    likes = v.get("like_count", 0)
    comments = v.get("comment_count", 0)
    shares = v.get("share_count", 0)
    if views == 0:
        return 0.0
    engagement = (likes + comments * 2 + shares * 3) / views * 1000
    return round(engagement * math.log10(max(views, 1)), 2)


def _aggregate_hashtags(videos: list[dict[str, Any]], top_n: int = 30) -> list[dict[str, Any]]:
    from collections import defaultdict
    import math
    tag_data: dict[str, dict[str, Any]] = defaultdict(lambda: {"count": 0, "total_views": 0, "total_likes": 0})
    for v in videos:
        views = v.get("views", v.get("view_count", 0))
        likes = v.get("likes", v.get("like_count", 0))
        for tag in v.get("hashtags", v.get("hashtag_names", [])):
            tag_data[tag]["count"] += 1
            tag_data[tag]["total_views"] += views
            tag_data[tag]["total_likes"] += likes

    results = []
    for tag, data in tag_data.items():
        count = data["count"]
        avg_views = data["total_views"] // count if count else 0
        score = round(count * math.log10(max(avg_views, 10)), 2)
        results.append({
            "tag": tag,
            "frequency": count,
            "avg_views": avg_views,
            "avg_likes": data["total_likes"] // count if count else 0,
            "score": score,
            "platform": "tiktok",
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)[:top_n]


def _aggregate_sounds(videos: list[dict[str, Any]], top_n: int = 20) -> list[dict[str, Any]]:
    from collections import defaultdict
    import math
    sound_data: dict[str, dict[str, Any]] = defaultdict(lambda: {"count": 0, "total_views": 0})
    for v in videos:
        mid = v.get("music_id", "")
        if not mid:
            continue
        views = v.get("views", v.get("view_count", 0))
        sound_data[mid]["count"] += 1
        sound_data[mid]["total_views"] += views

    results = []
    for mid, data in sound_data.items():
        count = data["count"]
        avg_views = data["total_views"] // count if count else 0
        score = round(count * math.log10(max(avg_views, 10)), 2)
        results.append({
            "music_id": mid,
            "title": f"Sound {mid}",
            "frequency": count,
            "avg_views": avg_views,
            "score": score,
            "platform": "tiktok",
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)[:top_n]
