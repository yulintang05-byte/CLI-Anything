"""TikTok trends scraper — supports official Research API and web-scrape fallback."""

import re
import json
import time
import random
import hashlib
from datetime import datetime, timedelta
from collections import Counter
from typing import Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# ---------------------------------------------------------------------------
# TikTok Research API (requires approved developer account)
# Docs: https://developers.tiktok.com/products/research-api
# ---------------------------------------------------------------------------

TIKTOK_RESEARCH_BASE = "https://open.tiktokapis.com/v2"


def _research_headers(access_token: str) -> dict:
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


def fetch_tiktok_trending_research(
    access_token: str,
    hashtag: Optional[str] = None,
    region: str = "US",
    max_count: int = 50,
) -> list[dict]:
    """
    Fetch trending TikTok videos via the official Research API.
    Requires an approved TikTok Research API access token.
    """
    if not REQUESTS_AVAILABLE:
        raise RuntimeError("requests not installed. Run: pip install requests")

    week_ago = int((datetime.utcnow() - timedelta(days=7)).timestamp())
    now = int(datetime.utcnow().timestamp())

    query = {
        "and": [
            {"operation": "GTE", "field_name": "create_date", "field_values": [str(week_ago)]},
        ]
    }
    if region:
        query["and"].append({
            "operation": "IN",
            "field_name": "region_code",
            "field_values": [region.upper()],
        })
    if hashtag:
        query["and"].append({
            "operation": "IN",
            "field_name": "hashtag_name",
            "field_values": [hashtag.lstrip("#")],
        })

    payload = {
        "query": query,
        "start_date": datetime.fromtimestamp(week_ago).strftime("%Y%m%d"),
        "end_date": datetime.fromtimestamp(now).strftime("%Y%m%d"),
        "max_count": min(max_count, 100),
        "is_random": False,
        "sort_type": "0",
        "fields": "id,username,region_code,video_description,music_id,like_count,comment_count,share_count,view_count,hashtag_names,effect_ids,create_time",
    }

    resp = requests.post(
        f"{TIKTOK_RESEARCH_BASE}/research/video/query/",
        headers=_research_headers(access_token),
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    raw_videos = data.get("data", {}).get("videos", [])
    return [_normalize_research_video(v) for v in raw_videos]


def _normalize_research_video(v: dict) -> dict:
    desc = v.get("video_description", "")
    hashtags = [f"#{h}" for h in v.get("hashtag_names", [])]
    inline = re.findall(r"#(\w+)", desc)
    all_tags = list(dict.fromkeys(hashtags + [f"#{t}" for t in inline]))
    view_count = int(v.get("view_count", 0))
    like_count = int(v.get("like_count", 0))
    comment_count = int(v.get("comment_count", 0))
    share_count = int(v.get("share_count", 0))
    engagement = (like_count + comment_count + share_count) / max(view_count, 1) * 100
    return {
        "id": str(v.get("id", "")),
        "username": v.get("username", ""),
        "description": desc[:200],
        "hashtags": all_tags,
        "music_id": str(v.get("music_id", "")),
        "view_count": view_count,
        "like_count": like_count,
        "comment_count": comment_count,
        "share_count": share_count,
        "engagement_rate_pct": round(engagement, 3),
        "region": v.get("region_code", ""),
        "created_at": datetime.fromtimestamp(v.get("create_time", 0)).isoformat(),
        "url": f"https://www.tiktok.com/@{v.get('username', 'unknown')}/video/{v.get('id', '')}",
        "source": "research_api",
    }


# ---------------------------------------------------------------------------
# Web scrape fallback — TikTok trending page
# Note: TikTok aggressively blocks scrapers; use responsibly / with consent
# ---------------------------------------------------------------------------

_TIKTOK_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
}

_DISCOVERY_URL = "https://www.tiktok.com/api/explore/item_list/?aid=1988&count=30&itemID=&sourceType=24"
_HASHTAG_URL = "https://www.tiktok.com/api/challenge/item_list/?aid=1988&count=30&challengeID={challenge_id}&cursor=0"
_SEARCH_HASHTAG_URL = "https://www.tiktok.com/api/search/hashtag/full/?aid=1988&keyword={keyword}&count=20&cursor=0"


def fetch_tiktok_trending_web(max_retries: int = 3) -> list[dict]:
    """
    Scrape TikTok trending page via unofficial web API.
    Returns normalized video dicts.
    """
    if not REQUESTS_AVAILABLE:
        raise RuntimeError("requests not installed. Run: pip install requests")

    session = requests.Session()
    session.headers.update(_TIKTOK_HEADERS)
    # Warm up session with homepage
    try:
        session.get("https://www.tiktok.com/", timeout=10)
    except Exception:
        pass

    for attempt in range(max_retries):
        try:
            resp = session.get(_DISCOVERY_URL, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("itemList", [])
                return [_normalize_web_video(item) for item in items]
            time.sleep(2 ** attempt)
        except Exception:
            time.sleep(2 ** attempt)
    return []


def _normalize_web_video(item: dict) -> dict:
    desc = item.get("desc", "")
    hashtags = [f"#{c.get('hashtagName', '')}" for c in item.get("challenges", [])]
    inline = [f"#{t}" for t in re.findall(r"#(\w+)", desc)]
    all_tags = list(dict.fromkeys(hashtags + inline))

    stats = item.get("stats", {})
    view_count = int(stats.get("playCount", 0))
    like_count = int(stats.get("diggCount", 0))
    comment_count = int(stats.get("commentCount", 0))
    share_count = int(stats.get("shareCount", 0))
    engagement = (like_count + comment_count + share_count) / max(view_count, 1) * 100

    author = item.get("author", {})
    music = item.get("music", {})
    video = item.get("video", {})
    item_id = item.get("id", "")

    return {
        "id": item_id,
        "username": author.get("uniqueId", ""),
        "author_nickname": author.get("nickname", ""),
        "description": desc[:200],
        "hashtags": all_tags,
        "music_id": str(music.get("id", "")),
        "music_title": music.get("title", ""),
        "music_author": music.get("authorName", ""),
        "music_original": music.get("original", False),
        "duration_seconds": int(video.get("duration", 0)),
        "view_count": view_count,
        "like_count": like_count,
        "comment_count": comment_count,
        "share_count": share_count,
        "engagement_rate_pct": round(engagement, 3),
        "created_at": datetime.fromtimestamp(item.get("createTime", 0)).isoformat() if item.get("createTime") else "",
        "url": f"https://www.tiktok.com/@{author.get('uniqueId', 'unknown')}/video/{item_id}",
        "source": "web_scrape",
    }


# ---------------------------------------------------------------------------
# Hashtag discovery & analysis
# ---------------------------------------------------------------------------

def fetch_hashtag_info(hashtag: str, session: "requests.Session | None" = None) -> dict:
    """
    Fetch TikTok hashtag stats via unofficial API.
    Returns view count, video count, description.
    """
    if not REQUESTS_AVAILABLE:
        raise RuntimeError("requests not installed. Run: pip install requests")
    tag = hashtag.lstrip("#")
    if session is None:
        session = requests.Session()
        session.headers.update(_TIKTOK_HEADERS)
        try:
            session.get("https://www.tiktok.com/", timeout=10)
        except Exception:
            pass

    url = f"https://www.tiktok.com/api/challenge/detail/?aid=1988&challengeName={tag}"
    try:
        resp = session.get(url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            ch = data.get("challengeInfo", {}).get("challenge", {})
            stats = data.get("challengeInfo", {}).get("statsV2", data.get("challengeInfo", {}).get("stats", {}))
            return {
                "hashtag": f"#{tag}",
                "id": ch.get("id", ""),
                "title": ch.get("title", ""),
                "description": ch.get("desc", "")[:150],
                "view_count": int(stats.get("viewCount", 0)),
                "video_count": int(stats.get("videoCount", 0)),
                "url": f"https://www.tiktok.com/tag/{tag}",
            }
    except Exception:
        pass
    return {"hashtag": f"#{tag}", "error": "could not fetch data"}


def extract_trending_hashtags(videos: list[dict], top_n: int = 30) -> list[dict]:
    """Rank hashtags by appearance and total views across scraped videos."""
    counter: Counter = Counter()
    views_map: dict[str, int] = {}
    for v in videos:
        views = v.get("view_count", 0)
        for tag in v.get("hashtags", []):
            t = tag.lower().lstrip("#")
            counter[t] += 1
            views_map[t] = views_map.get(t, 0) + views

    return [
        {
            "hashtag": f"#{tag}",
            "video_count": count,
            "total_views": views_map.get(tag, 0),
            "avg_views": views_map.get(tag, 0) // max(count, 1),
            "trend_score": round(count * 0.4 + (views_map.get(tag, 0) / 1_000_000) * 0.6, 2),
        }
        for tag, count in counter.most_common(top_n)
    ]


def extract_trending_sounds(videos: list[dict], top_n: int = 20) -> list[dict]:
    """Rank trending sounds/music from scraped TikTok videos."""
    sound_counter: Counter = Counter()
    sound_views: dict[str, int] = {}
    sound_meta: dict[str, dict] = {}

    for v in videos:
        mid = v.get("music_id", "")
        if not mid:
            continue
        sound_counter[mid] += 1
        sound_views[mid] = sound_views.get(mid, 0) + v.get("view_count", 0)
        if mid not in sound_meta:
            sound_meta[mid] = {
                "music_id": mid,
                "music_title": v.get("music_title", "Unknown"),
                "music_author": v.get("music_author", "Unknown"),
                "is_original": v.get("music_original", False),
            }

    results = []
    for sound_id, count in sound_counter.most_common(top_n):
        meta = sound_meta.get(sound_id, {})
        results.append({
            **meta,
            "usage_count": count,
            "total_views": sound_views.get(sound_id, 0),
            "avg_views_per_video": sound_views.get(sound_id, 0) // max(count, 1),
            "url": f"https://www.tiktok.com/music/-{sound_id}",
        })
    return results


def analyze_tiktok_patterns(videos: list[dict]) -> dict:
    """Analyze patterns across trending TikTok videos."""
    if not videos:
        return {}

    views = [v["view_count"] for v in videos if v.get("view_count", 0) > 0]
    durations = [v.get("duration_seconds", 0) for v in videos if v.get("duration_seconds", 0) > 0]
    engagement_rates = [v.get("engagement_rate_pct", 0) for v in videos]

    # Duration buckets (TikTok-specific)
    under_15 = sum(1 for d in durations if d <= 15)
    s15_30 = sum(1 for d in durations if 15 < d <= 30)
    s30_60 = sum(1 for d in durations if 30 < d <= 60)
    s60_180 = sum(1 for d in durations if 60 < d <= 180)
    over_180 = sum(1 for d in durations if d > 180)

    best_bucket = max(
        [("≤15s", under_15), ("15-30s", s15_30), ("30-60s", s30_60),
         ("60-180s", s60_180), (">180s", over_180)],
        key=lambda x: x[1],
    )

    hour_dist: Counter = Counter()
    for v in videos:
        ts = v.get("created_at", "")
        if ts and "T" in ts:
            try:
                hour = int(ts.split("T")[1].split(":")[0])
                hour_dist[hour] += 1
            except Exception:
                pass

    top_hours = [h for h, _ in hour_dist.most_common(3)]

    return {
        "total_videos_analyzed": len(videos),
        "avg_views": int(sum(views) / len(views)) if views else 0,
        "median_views": int(sorted(views)[len(views) // 2]) if views else 0,
        "avg_engagement_rate_pct": round(sum(engagement_rates) / len(engagement_rates), 3) if engagement_rates else 0,
        "avg_duration_seconds": round(sum(durations) / len(durations), 1) if durations else 0,
        "duration_breakdown": {
            "under_15s": under_15,
            "15_30s": s15_30,
            "30_60s": s30_60,
            "60_180s": s60_180,
            "over_180s": over_180,
        },
        "best_duration": best_bucket[0],
        "top_posting_hours_utc": top_hours,
        "top_hashtags": extract_trending_hashtags(videos, top_n=10),
        "top_sounds": extract_trending_sounds(videos, top_n=5),
    }


# ---------------------------------------------------------------------------
# Unified entry point — tries Research API first, falls back to web scrape
# ---------------------------------------------------------------------------

def fetch_tiktok_trends(
    access_token: Optional[str] = None,
    hashtag: Optional[str] = None,
    region: str = "US",
    max_results: int = 30,
) -> dict:
    """
    Fetch TikTok trending data.
    If access_token provided → uses Research API.
    Otherwise → falls back to web scraping.
    """
    source = "unknown"
    videos: list[dict] = []

    if access_token:
        try:
            videos = fetch_tiktok_trending_research(access_token, hashtag=hashtag, region=region, max_count=max_results)
            source = "research_api"
        except Exception as e:
            source = f"research_api_error: {e}"

    if not videos:
        videos = fetch_tiktok_trending_web(max_retries=3)
        source = "web_scrape"

    return {
        "source": source,
        "region": region,
        "fetched_at": datetime.utcnow().isoformat(),
        "video_count": len(videos),
        "videos": videos,
        "hashtags": extract_trending_hashtags(videos, top_n=25),
        "sounds": extract_trending_sounds(videos, top_n=15),
        "patterns": analyze_tiktok_patterns(videos),
    }
