"""TikTok trend scraping — Creative Center public API + trending page."""

import re
from typing import Any, Dict, List, Optional

from cli_anything.social_trends.utils.http import get_json, _TIKTOK_HEADERS

# TikTok Creative Center public endpoints (no auth required)
_CC_BASE = "https://ads.tiktok.com/creative_radar_api/v1"
_CC_HASHTAGS = f"{_CC_BASE}/popular_trend/hashtag/list"
_CC_MUSIC = f"{_CC_BASE}/popular_trend/music/list"
_CC_CREATORS = f"{_CC_BASE}/popular_trend/creator/list"

# Period options: 7 = last 7 days, 30 = last 30 days, 120 = last 120 days
PERIOD_OPTIONS = [7, 30, 120]

# TikTok country codes for major markets
COUNTRY_CODES = {
    "US": "US",
    "UK": "GB",
    "CA": "CA",
    "AU": "AU",
    "IN": "IN",
    "BR": "BR",
    "MX": "MX",
    "DE": "DE",
    "FR": "FR",
    "JP": "JP",
    "KR": "KR",
    "ID": "ID",
    "TH": "TH",
    "VN": "VN",
    "PH": "PH",
}


def fetch_trending_hashtags(
    region: str = "US",
    period_days: int = 7,
    limit: int = 20,
    page: int = 1,
) -> Dict[str, Any]:
    """
    Fetch trending hashtags from TikTok Creative Center.

    No authentication required — uses TikTok's public Creative Center API.
    period_days: 7, 30, or 120
    """
    if period_days not in PERIOD_OPTIONS:
        period_days = 7
    country_code = COUNTRY_CODES.get(region.upper(), region.upper())

    params = {
        "period": period_days,
        "page": page,
        "limit": min(limit, 50),
        "country_code": country_code,
    }

    try:
        data = get_json(_CC_HASHTAGS, params=params, headers=_TIKTOK_HEADERS)
        return _parse_hashtag_response(data, region, period_days)
    except Exception as e:
        raise RuntimeError(
            f"TikTok Creative Center request failed. "
            f"The endpoint may be rate-limited — try again in a minute. Error: {e}"
        )


def _parse_hashtag_response(data: Dict, region: str, period: int) -> Dict[str, Any]:
    hashtags = []
    raw_list = (data.get("data") or {}).get("list") or []
    for item in raw_list:
        hashtags.append({
            "hashtag": f"#{item.get('hashtag_name', '')}",
            "rank": item.get("rank", 0),
            "video_count": item.get("video_views", 0),
            "post_count": item.get("publish_cnt", 0),
            "trend": item.get("trend", "stable"),
            "related_hashtags": item.get("core_hashtag_list", [])[:5],
        })
    return {
        "source": "tiktok_creative_center",
        "region": region,
        "period_days": period,
        "total": len(hashtags),
        "hashtags": hashtags,
    }


def fetch_trending_music(
    region: str = "US",
    period_days: int = 7,
    limit: int = 20,
) -> Dict[str, Any]:
    """
    Fetch trending sounds/music from TikTok Creative Center.

    Returns title, artist, clip count, duration, and a link to the sound.
    """
    if period_days not in PERIOD_OPTIONS:
        period_days = 7
    country_code = COUNTRY_CODES.get(region.upper(), region.upper())

    params = {
        "period": period_days,
        "page": 1,
        "limit": min(limit, 50),
        "country_code": country_code,
    }

    try:
        data = get_json(_CC_MUSIC, params=params, headers=_TIKTOK_HEADERS)
        return _parse_music_response(data, region, period_days)
    except Exception as e:
        raise RuntimeError(f"TikTok music fetch failed: {e}")


def _parse_music_response(data: Dict, region: str, period: int) -> Dict[str, Any]:
    sounds = []
    raw_list = (data.get("data") or {}).get("list") or []
    for item in raw_list:
        clip_count = item.get("clip_count", 0) or item.get("video_views", 0)
        sounds.append({
            "rank": item.get("rank", 0),
            "title": item.get("music_name") or item.get("title", ""),
            "artist": item.get("author") or item.get("artist_name", "Unknown"),
            "clip_count": clip_count,
            "duration_sec": item.get("duration", 0),
            "music_id": item.get("music_id") or item.get("id", ""),
            "cover_url": item.get("cover_url", ""),
            "trend": item.get("trend", "stable"),
        })
    return {
        "source": "tiktok_creative_center",
        "region": region,
        "period_days": period,
        "total": len(sounds),
        "sounds": sounds,
    }


def fetch_trending_creators(
    region: str = "US",
    period_days: int = 7,
    limit: int = 20,
) -> Dict[str, Any]:
    """Fetch trending creators from TikTok Creative Center."""
    if period_days not in PERIOD_OPTIONS:
        period_days = 7
    country_code = COUNTRY_CODES.get(region.upper(), region.upper())

    params = {
        "period": period_days,
        "page": 1,
        "limit": min(limit, 50),
        "country_code": country_code,
    }

    try:
        data = get_json(_CC_CREATORS, params=params, headers=_TIKTOK_HEADERS)
        return _parse_creators_response(data, region, period_days)
    except Exception as e:
        raise RuntimeError(f"TikTok creator fetch failed: {e}")


def _parse_creators_response(data: Dict, region: str, period: int) -> Dict[str, Any]:
    creators = []
    raw_list = (data.get("data") or {}).get("list") or []
    for item in raw_list:
        creators.append({
            "rank": item.get("rank", 0),
            "nickname": item.get("nick_name") or item.get("username", ""),
            "follower_count": item.get("follower_cnt", 0),
            "follower_growth": item.get("follower_growth_rate", 0),
            "avg_views": item.get("avg_views", 0),
            "niche": item.get("category_name", ""),
            "bio": (item.get("bio_description") or "")[:150],
            "url": f"https://www.tiktok.com/@{item.get('unique_id', '')}",
        })
    return {
        "source": "tiktok_creative_center",
        "region": region,
        "period_days": period,
        "total": len(creators),
        "creators": creators,
    }


def analyze_niche_hashtags(
    niche_keywords: List[str],
    region: str = "US",
    period_days: int = 7,
) -> Dict[str, Any]:
    """
    Given a list of niche keywords, fetch trending hashtags and filter
    those relevant to the niche.
    """
    all_data = fetch_trending_hashtags(region=region, period_days=period_days, limit=50)
    hashtags = all_data.get("hashtags", [])

    pattern = re.compile("|".join(re.escape(k) for k in niche_keywords), re.IGNORECASE)
    relevant = [h for h in hashtags if pattern.search(h.get("hashtag", ""))]
    others = [h for h in hashtags if not pattern.search(h.get("hashtag", ""))]

    return {
        "niche_keywords": niche_keywords,
        "region": region,
        "period_days": period_days,
        "niche_hashtags": relevant,
        "general_trending": others[:10],
        "recommendation": (
            f"Found {len(relevant)} niche-relevant trending hashtags. "
            f"Mix {min(5, len(relevant))} niche tags with 3-5 general trending tags per post."
        ),
    }
