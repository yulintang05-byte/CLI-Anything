#!/usr/bin/env python3
"""TikTok trends scraper.

Primary: TikTok Research API (requires approved developer account).
Fallback: Public TikTok Creative Center endpoints (no auth needed, rate-limited).
"""

import os
import json
import re
import urllib.request
import urllib.parse
from collections import Counter
from typing import Optional

TIKTOK_RESEARCH_BASE = "https://open.tiktokapis.com/v2"
CREATIVE_CENTER_BASE = "https://ads.tiktok.com/creative_radar_api/v1"


def _get_research_token() -> Optional[str]:
    return os.environ.get("TIKTOK_RESEARCH_TOKEN", "")


def _cc_get(path: str, params: dict = None) -> dict:
    """Call TikTok Creative Center public endpoint (no auth needed)."""
    base = f"{CREATIVE_CENTER_BASE}/{path}"
    if params:
        base += f"?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        base,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e), "data": {}}


def get_trending_hashtags_cc(
    region: str = "US", period: int = 7, limit: int = 30
) -> list[dict]:
    """Fetch trending hashtags from TikTok Creative Center (public, no key needed)."""
    data = _cc_get(
        "popular_trend/hashtag/list",
        {"period": period, "country_code": region, "page_size": limit, "page": 1},
    )
    results = []
    for item in data.get("data", {}).get("list", []):
        results.append(
            {
                "hashtag": f"#{item.get('hashtag_name', '')}",
                "video_count": item.get("video_count", 0),
                "view_count": item.get("view_sum", 0),
                "publish_count": item.get("publish_cnt", 0),
                "rank": item.get("rank", 0),
                "trend": item.get("trend", ""),
            }
        )
    return results


def get_trending_songs_cc(
    region: str = "US", period: int = 7, limit: int = 30
) -> list[dict]:
    """Fetch trending songs/sounds from TikTok Creative Center."""
    data = _cc_get(
        "popular_trend/music/list",
        {"period": period, "country_code": region, "page_size": limit, "page": 1},
    )
    results = []
    for item in data.get("data", {}).get("music_list", []):
        results.append(
            {
                "music_id": item.get("music_id", ""),
                "title": item.get("music_name", ""),
                "artist": item.get("author", ""),
                "duration": item.get("duration", 0),
                "video_count": item.get("video_count", 0),
                "clip_count": item.get("clip_count", 0),
                "rank": item.get("rank", 0),
                "trend": item.get("trend", ""),
                "cover_url": item.get("cover_url", ""),
            }
        )
    return results


def get_trending_creators_cc(
    region: str = "US", period: int = 7, limit: int = 20
) -> list[dict]:
    """Fetch trending TikTok creators."""
    data = _cc_get(
        "popular_trend/creator/list",
        {"period": period, "country_code": region, "page_size": limit, "page": 1},
    )
    results = []
    for item in data.get("data", {}).get("creator_list", []):
        results.append(
            {
                "creator_id": item.get("user_id", ""),
                "username": item.get("nick_name", ""),
                "follower_count": item.get("follower_count", 0),
                "like_count": item.get("like_count", 0),
                "video_count": item.get("video_count", 0),
                "category": item.get("category", ""),
                "rank": item.get("rank", 0),
            }
        )
    return results


def get_trending_videos_research(
    max_results: int = 20,
    region: str = "US",
    days_back: int = 7,
) -> list[dict]:
    """Fetch trending videos via TikTok Research API (requires approved token)."""
    token = _get_research_token()
    if not token:
        return [
            {
                "error": "TIKTOK_RESEARCH_TOKEN not set",
                "note": "Apply at https://developers.tiktok.com/products/research-api/",
            }
        ]
    from datetime import datetime, timedelta, timezone

    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days_back)
    payload = json.dumps(
        {
            "query": {
                "and": [
                    {"field_name": "region_code", "filter_value": [region], "operation": "IN"},
                    {"field_name": "create_date", "filter_value": [
                        start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d")
                    ], "operation": "BETWEEN"},
                ]
            },
            "start_date": start_date.strftime("%Y%m%d"),
            "end_date": end_date.strftime("%Y%m%d"),
            "max_count": min(max_results, 100),
            "fields": "id,create_time,username,region_code,video_description,hashtag_names,like_count,comment_count,share_count,view_count,music_id",
        }
    ).encode()
    req = urllib.request.Request(
        f"{TIKTOK_RESEARCH_BASE}/research/video/query/",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
        return [
            {
                "video_id": v.get("id", ""),
                "username": v.get("username", ""),
                "description": v.get("video_description", ""),
                "hashtags": v.get("hashtag_names", []),
                "like_count": v.get("like_count", 0),
                "comment_count": v.get("comment_count", 0),
                "share_count": v.get("share_count", 0),
                "view_count": v.get("view_count", 0),
                "music_id": v.get("music_id", ""),
                "url": f"https://www.tiktok.com/@{v.get('username','')}/video/{v.get('id','')}",
            }
            for v in data.get("data", {}).get("videos", [])
        ]
    except Exception as e:
        return [{"error": str(e)}]


def extract_hashtags_from_videos(videos: list[dict], top_n: int = 30) -> list[dict]:
    """Rank hashtags by weighted engagement from a list of TikTok videos."""
    counter: Counter = Counter()
    for v in videos:
        if "error" in v:
            continue
        engagement = v.get("like_count", 0) + v.get("share_count", 0) * 3 + v.get("comment_count", 0) * 2
        for ht in v.get("hashtags", []):
            counter[ht.lower()] += max(engagement, 1)
        # Also parse from description
        for ht in re.findall(r"#(\w+)", v.get("description", "")):
            counter[ht.lower()] += max(engagement // 2, 1)
    return [
        {"hashtag": f"#{tag}", "engagement_score": score, "rank": i + 1}
        for i, (tag, score) in enumerate(counter.most_common(top_n))
    ]
