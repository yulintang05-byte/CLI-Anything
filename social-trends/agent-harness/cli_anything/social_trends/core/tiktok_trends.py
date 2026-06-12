"""TikTok trend scraper — fetches viral videos, hashtags, and sounds.

Data sources (tried in order):
  1. TikTokApi (playwright-based)   — pip install TikTokApi playwright
  2. TikTok Research API            — requires TIKTOK_CLIENT_KEY + TIKTOK_CLIENT_SECRET
  3. Public /trending endpoint      — no auth, best-effort scraping
"""

import os
import re
import json
import time
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict

from cli_anything.social_trends.utils.http_client import (
    get_session, rate_limited_get, safe_json
)

# ── Data models ───────────────────────────────────────────────────────────────

@dataclass
class TikTokVideo:
    video_id: str
    description: str
    author: str
    author_followers: int
    plays: int
    likes: int
    comments: int
    shares: int
    hashtags: List[str]
    sound_id: str
    sound_title: str
    sound_author: str
    created_at: str
    url: str
    platform: str = "tiktok"

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TikTokSound:
    sound_id: str
    title: str
    author: str
    usage_count: int
    platform: str = "tiktok"
    original: bool = False

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TikTokHashtag:
    tag: str
    video_count: int
    view_count: int
    platform: str = "tiktok"

    def to_dict(self) -> Dict:
        return asdict(self)


# ── TikTok Research API ───────────────────────────────────────────────────────

_RESEARCH_TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
_RESEARCH_QUERY_URL = "https://open.tiktokapis.com/v2/research/video/query/"


def _get_research_token() -> Optional[str]:
    """Exchange client credentials for a Research API access token."""
    client_key = os.environ.get("TIKTOK_CLIENT_KEY", "")
    client_secret = os.environ.get("TIKTOK_CLIENT_SECRET", "")
    if not (client_key and client_secret):
        return None

    session = get_session()
    try:
        resp = session.post(
            _RESEARCH_TOKEN_URL,
            data={
                "client_key": client_key,
                "client_secret": client_secret,
                "grant_type": "client_credentials",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        data = safe_json(resp)
        return data.get("access_token")
    except Exception:
        return None


def _research_api_trending(max_results: int = 50) -> List[Dict]:
    """Query TikTok Research API for trending videos."""
    token = _get_research_token()
    if not token:
        return []

    from datetime import datetime, timedelta
    end = datetime.utcnow()
    start = end - timedelta(days=7)

    payload = {
        "query": {
            "and": [
                {"operation": "GT", "field_name": "like_count", "field_values": ["10000"]},
            ]
        },
        "start_date": start.strftime("%Y%m%d"),
        "end_date": end.strftime("%Y%m%d"),
        "max_count": min(max_results, 100),
        "fields": "id,create_time,username,region_code,video_description,music_id,like_count,comment_count,share_count,view_count,hashtag_names,sound_name,sound_author_name",
        "sort_type": "0",
    }

    session = get_session()
    session.headers["Authorization"] = f"Bearer {token}"
    try:
        resp = session.post(_RESEARCH_QUERY_URL, json=payload, timeout=20)
        data = safe_json(resp)
        videos_raw = data.get("data", {}).get("videos", [])
        return [_parse_research_video(v) for v in videos_raw]
    except Exception:
        return []


def _parse_research_video(v: Dict) -> Dict:
    desc = v.get("video_description", "")
    hashtags = v.get("hashtag_names", []) or _extract_hashtags(desc)
    return {
        "video_id": str(v.get("id", "")),
        "description": desc,
        "author": v.get("username", ""),
        "author_followers": 0,
        "plays": int(v.get("view_count", 0)),
        "likes": int(v.get("like_count", 0)),
        "comments": int(v.get("comment_count", 0)),
        "shares": int(v.get("share_count", 0)),
        "hashtags": [f"#{t.lstrip('#')}" for t in hashtags],
        "sound_id": str(v.get("music_id", "")),
        "sound_title": v.get("sound_name", ""),
        "sound_author": v.get("sound_author_name", ""),
        "created_at": str(v.get("create_time", "")),
        "url": f"https://www.tiktok.com/@{v.get('username', '')}/video/{v.get('id', '')}",
        "platform": "tiktok",
    }


# ── TikTokApi (playwright-based) ──────────────────────────────────────────────

def _playwright_trending(max_results: int = 30) -> List[Dict]:
    """Use TikTokApi library if installed."""
    try:
        import asyncio
        from TikTokApi import TikTokApi

        async def _fetch():
            results = []
            async with TikTokApi() as api:
                await api.create_sessions(
                    ms_tokens=[os.environ.get("TIKTOK_MS_TOKEN", "")],
                    num_sessions=1,
                    sleep_after=2,
                )
                async for video in api.trending.videos(count=max_results):
                    results.append(_parse_tiktokapi_video(video))
            return results

        return asyncio.run(_fetch())
    except ImportError:
        return []
    except Exception:
        return []


def _parse_tiktokapi_video(video) -> Dict:
    try:
        desc = video.desc or ""
        hashtags = [f"#{c.hashtag_name}" for c in (video.challenges or [])]
        if not hashtags:
            hashtags = _extract_hashtags(desc)
        sound = video.music
        return {
            "video_id": str(video.id),
            "description": desc,
            "author": video.author.unique_id if video.author else "",
            "author_followers": getattr(video.author, "follower_count", 0) or 0,
            "plays": video.stats.play_count if video.stats else 0,
            "likes": video.stats.digg_count if video.stats else 0,
            "comments": video.stats.comment_count if video.stats else 0,
            "shares": video.stats.share_count if video.stats else 0,
            "hashtags": hashtags,
            "sound_id": str(sound.id) if sound else "",
            "sound_title": sound.title if sound else "",
            "sound_author": sound.author if sound else "",
            "created_at": str(video.create_time),
            "url": f"https://www.tiktok.com/@{video.author.unique_id}/video/{video.id}" if video.author else "",
            "platform": "tiktok",
        }
    except Exception:
        return {}


# ── Public endpoint fallback ──────────────────────────────────────────────────

_DISCOVER_URL = "https://www.tiktok.com/api/explore/item_list/"


def _public_trending(max_results: int = 30) -> List[Dict]:
    """Scrape TikTok's public explore/discover endpoint."""
    session = get_session({
        "Referer": "https://www.tiktok.com/",
        "Accept": "application/json, text/plain, */*",
        "x-tt-params": "",
    })
    params = {
        "aid": "1988",
        "app_language": "en",
        "app_name": "tiktok_web",
        "count": str(min(max_results, 30)),
        "from_page": "fyp",
        "itemType": "1",
        "language": "en",
        "region": "US",
        "type": "1",
    }
    try:
        resp = rate_limited_get(_DISCOVER_URL, session=session, params=params, timeout=15)
        if resp.status_code != 200:
            return []
        data = safe_json(resp)
        items = data.get("itemList", [])
        return [_parse_public_item(item) for item in items if item]
    except Exception:
        return []


def _parse_public_item(item: Dict) -> Dict:
    desc = item.get("desc", "")
    challenges = item.get("challenges", [])
    hashtags = [f"#{c.get('title', '')}" for c in challenges if c.get("title")]
    if not hashtags:
        hashtags = _extract_hashtags(desc)

    music = item.get("music", {})
    stats = item.get("stats", {})
    author = item.get("author", {})
    author_stats = item.get("authorStats", {})

    return {
        "video_id": item.get("id", ""),
        "description": desc,
        "author": author.get("uniqueId", ""),
        "author_followers": author_stats.get("followerCount", 0),
        "plays": stats.get("playCount", 0),
        "likes": stats.get("diggCount", 0),
        "comments": stats.get("commentCount", 0),
        "shares": stats.get("shareCount", 0),
        "hashtags": hashtags,
        "sound_id": str(music.get("id", "")),
        "sound_title": music.get("title", ""),
        "sound_author": music.get("authorName", ""),
        "created_at": str(item.get("createTime", "")),
        "url": f"https://www.tiktok.com/@{author.get('uniqueId', '')}/video/{item.get('id', '')}",
        "platform": "tiktok",
    }


def _extract_hashtags(text: str) -> List[str]:
    return list(dict.fromkeys(
        f"#{tag.lower()}" for tag in re.findall(r"#(\w+)", text)
    ))


# ── Public API ────────────────────────────────────────────────────────────────

def get_trending(max_results: int = 50) -> List[TikTokVideo]:
    """Fetch trending TikTok videos.

    Tries in order: TikTok Research API → TikTokApi (playwright) → public endpoint.

    Set environment variables for enhanced access:
      TIKTOK_CLIENT_KEY + TIKTOK_CLIENT_SECRET  → Research API
      TIKTOK_MS_TOKEN                            → TikTokApi (playwright)

    Args:
        max_results: Max number of trending videos to return.

    Returns:
        List of TikTokVideo sorted by plays (highest first).
    """
    raw: List[Dict] = []

    raw = _research_api_trending(max_results)

    if not raw:
        raw = _playwright_trending(max_results)

    if not raw:
        raw = _public_trending(max_results)

    videos = []
    for r in raw[:max_results]:
        if not r:
            continue
        try:
            videos.append(TikTokVideo(**{
                k: r.get(k, v if not isinstance(v, list) else [])
                for k, v in TikTokVideo.__dataclass_fields__.items()
            }))
        except Exception:
            continue

    videos.sort(key=lambda v: v.plays, reverse=True)
    return videos


def get_trending_hashtags(videos: List[TikTokVideo], top_n: int = 30) -> List[TikTokHashtag]:
    """Aggregate hashtag stats from trending videos."""
    tag_data: Dict[str, Dict] = {}
    for v in videos:
        for tag in v.hashtags:
            clean = tag.lstrip("#").lower()
            if clean not in tag_data:
                tag_data[clean] = {"video_count": 0, "view_count": 0}
            tag_data[clean]["video_count"] += 1
            tag_data[clean]["view_count"] += v.plays

    results = [
        TikTokHashtag(
            tag=f"#{k}",
            video_count=v["video_count"],
            view_count=v["view_count"],
            platform="tiktok",
        )
        for k, v in tag_data.items()
    ]
    results.sort(key=lambda h: (h.view_count, h.video_count), reverse=True)
    return results[:top_n]


def get_trending_sounds(videos: List[TikTokVideo], top_n: int = 20) -> List[TikTokSound]:
    """Aggregate sound usage from trending videos."""
    sound_data: Dict[str, Dict] = {}
    for v in videos:
        if v.sound_id:
            sid = v.sound_id
            if sid not in sound_data:
                sound_data[sid] = {
                    "title": v.sound_title,
                    "author": v.sound_author,
                    "count": 0,
                }
            sound_data[sid]["count"] += 1

    results = [
        TikTokSound(
            sound_id=sid,
            title=d["title"],
            author=d["author"],
            usage_count=d["count"],
            platform="tiktok",
        )
        for sid, d in sound_data.items()
    ]
    results.sort(key=lambda s: s.usage_count, reverse=True)
    return results[:top_n]
