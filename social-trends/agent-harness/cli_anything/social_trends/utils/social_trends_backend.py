"""Social Trends backend — config, YouTube scraping via yt-dlp, TikTok scraping via requests/TikTokApi."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable

CONFIG_DIR = Path.home() / ".config" / "social-trends"
CONFIG_FILE = CONFIG_DIR / "config.json"
CACHE_DIR = CONFIG_DIR / "cache"
ENV_YOUTUBE_API_KEY = "YOUTUBE_API_KEY"
ENV_TIKTOK_SESSION_ID = "TIKTOK_SESSION_ID"

SUPPORTED_PLATFORMS = ["youtube", "tiktok", "all"]
SUPPORTED_NICHES = [
    "fitness", "travel", "food", "fashion", "beauty", "tech", "finance",
    "crypto", "motivational", "humor", "pets", "gaming", "music",
    "lifestyle", "luxury", "relationships", "education", "news",
]


# ── Config ─────────────────────────────────────────────────────────────

def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)
    CONFIG_FILE.chmod(0o600)


def get_youtube_api_key(cli_key: str | None = None) -> str | None:
    if cli_key:
        return cli_key
    env = os.environ.get(ENV_YOUTUBE_API_KEY)
    if env:
        return env
    return load_config().get("youtube_api_key")


def get_tiktok_session(cli_val: str | None = None) -> str | None:
    if cli_val:
        return cli_val
    env = os.environ.get(ENV_TIKTOK_SESSION_ID)
    if env:
        return env
    return load_config().get("tiktok_session_id")


# ── Cache ──────────────────────────────────────────────────────────────

def _cache_path(key: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    safe = key.replace("/", "_").replace(":", "_")
    return CACHE_DIR / f"{safe}.json"


def load_cache(key: str, max_age_secs: int = 3600) -> dict | None:
    path = _cache_path(key)
    if not path.exists():
        return None
    try:
        with open(path) as f:
            data = json.load(f)
        if time.time() - data.get("_ts", 0) > max_age_secs:
            return None
        return data.get("payload")
    except (json.JSONDecodeError, IOError):
        return None


def save_cache(key: str, payload: Any):
    path = _cache_path(key)
    with open(path, "w") as f:
        json.dump({"_ts": time.time(), "payload": payload}, f)


# ── YouTube ────────────────────────────────────────────────────────────

def _find_ytdlp() -> str:
    for name in ("yt-dlp", "yt_dlp", "youtube-dl"):
        import shutil
        found = shutil.which(name)
        if found:
            return found
    raise RuntimeError(
        "yt-dlp not found. Install with: pip install yt-dlp\n"
        "  Or: sudo apt install yt-dlp"
    )


def scrape_youtube_trending(
    country_code: str = "US",
    limit: int = 30,
    use_cache: bool = True,
    on_progress: Callable | None = None,
) -> list[dict]:
    """Fetch YouTube trending videos via yt-dlp.

    Returns list of dicts: {title, channel, views, likes, tags, hashtags,
    description, url, thumbnail, duration, upload_date, music_used}.
    """
    cache_key = f"yt_trending_{country_code}_{limit}"
    if use_cache:
        cached = load_cache(cache_key, max_age_secs=1800)
        if cached:
            return cached

    ytdlp = _find_ytdlp()
    url = f"https://www.youtube.com/feed/trending?gl={country_code}"

    if on_progress:
        on_progress("Fetching YouTube trending feed…", 10)

    cmd = [
        ytdlp,
        "--dump-json",
        "--no-warnings",
        "--quiet",
        "--playlist-end", str(limit),
        "--socket-timeout", "30",
        url,
    ]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("yt-dlp timed out fetching YouTube trending")

    videos = []
    for line in result.stdout.strip().splitlines():
        if not line.strip():
            continue
        try:
            info = json.loads(line)
        except json.JSONDecodeError:
            continue

        desc = info.get("description", "") or ""
        hashtags = _extract_hashtags(desc) + _extract_hashtags(info.get("title", ""))
        tags = info.get("tags") or []

        videos.append({
            "platform": "youtube",
            "title": info.get("title", ""),
            "channel": info.get("uploader", info.get("channel", "")),
            "views": info.get("view_count", 0),
            "likes": info.get("like_count", 0),
            "tags": tags[:20],
            "hashtags": list(set(hashtags + [f"#{t.replace(' ','')}" for t in tags[:5]])),
            "description": desc[:500],
            "url": info.get("webpage_url", f"https://youtube.com/watch?v={info.get('id','')}"),
            "thumbnail": info.get("thumbnail", ""),
            "duration": info.get("duration", 0),
            "upload_date": info.get("upload_date", ""),
            "categories": info.get("categories", []),
            "music_used": _extract_yt_music(info),
        })

    if on_progress:
        on_progress(f"Scraped {len(videos)} YouTube trending videos", 100)

    if videos:
        save_cache(cache_key, videos)
    return videos


def _extract_hashtags(text: str) -> list[str]:
    import re
    return list(set(re.findall(r"#\w+", text)))


def _extract_yt_music(info: dict) -> dict | None:
    track = info.get("track") or info.get("music_track")
    artist = info.get("artist") or info.get("music_artist")
    if track or artist:
        return {"track": track, "artist": artist}
    return None


def scrape_youtube_trending_via_api(api_key: str, country_code: str = "US", limit: int = 50) -> list[dict]:
    """Use YouTube Data API v3 videocategory/trending endpoint."""
    try:
        import requests as req
    except ImportError:
        raise RuntimeError("requests not installed: pip install requests")

    cache_key = f"yt_api_trending_{country_code}_{limit}"
    cached = load_cache(cache_key, max_age_secs=1800)
    if cached:
        return cached

    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics,topicDetails",
        "chart": "mostPopular",
        "regionCode": country_code,
        "maxResults": min(limit, 50),
        "key": api_key,
    }
    resp = req.get(url, params=params, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"YouTube API error ({resp.status_code}): {resp.text[:200]}")

    data = resp.json()
    videos = []
    for item in data.get("items", []):
        snip = item.get("snippet", {})
        stats = item.get("statistics", {})
        vid_id = item.get("id", "")
        desc = snip.get("description", "") or ""
        tags = snip.get("tags") or []
        hashtags = _extract_hashtags(desc) + _extract_hashtags(snip.get("title", ""))
        videos.append({
            "platform": "youtube",
            "title": snip.get("title", ""),
            "channel": snip.get("channelTitle", ""),
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "tags": tags[:20],
            "hashtags": list(set(hashtags + [f"#{t.replace(' ','')}" for t in tags[:5]])),
            "description": desc[:500],
            "url": f"https://youtube.com/watch?v={vid_id}",
            "thumbnail": snip.get("thumbnails", {}).get("high", {}).get("url", ""),
            "duration": 0,
            "upload_date": snip.get("publishedAt", "")[:10].replace("-", ""),
            "categories": item.get("topicDetails", {}).get("relevantTopicIds", []),
            "music_used": None,
        })

    save_cache(cache_key, videos)
    return videos


# ── TikTok ─────────────────────────────────────────────────────────────

_TIKTOK_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
        "TikTok/26.2.0"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
}


def _requests_lib():
    try:
        import requests
        return requests
    except ImportError:
        raise RuntimeError("requests not installed: pip install requests")


def scrape_tiktok_trending(
    limit: int = 30,
    session_id: str | None = None,
    use_cache: bool = True,
    on_progress: Callable | None = None,
) -> list[dict]:
    """Scrape TikTok trending videos.

    Tries TikTokApi (Playwright) first if installed, then falls back to
    direct requests against TikTok's internal explore endpoint.
    """
    cache_key = f"tt_trending_{limit}"
    if use_cache:
        cached = load_cache(cache_key, max_age_secs=1800)
        if cached:
            return cached

    if on_progress:
        on_progress("Connecting to TikTok…", 10)

    # Try TikTokApi package first
    try:
        return _scrape_tiktok_via_lib(limit, session_id, on_progress, cache_key)
    except (ImportError, Exception):
        pass

    # Fall back to direct requests
    try:
        return _scrape_tiktok_via_requests(limit, session_id, on_progress, cache_key)
    except Exception as e:
        raise RuntimeError(
            f"TikTok scraping failed: {e}\n"
            "Try installing TikTokApi: pip install TikTokApi\n"
            "Or set your session_id: social-trends config set tiktok_session_id <value>"
        )


def _scrape_tiktok_via_lib(
    limit: int, session_id: str | None, on_progress: Callable | None, cache_key: str
) -> list[dict]:
    """Use the unofficial TikTokApi (davidteather) with Playwright."""
    import asyncio
    from TikTokApi import TikTokApi  # type: ignore

    async def _fetch():
        videos = []
        ms_token = session_id
        async with TikTokApi() as api:
            if ms_token:
                await api.create_sessions(ms_tokens=[ms_token], num_sessions=1,
                                          sleep_after=3)
            else:
                await api.create_sessions(num_sessions=1, sleep_after=3,
                                          headless=True)
            async for video in api.trending.videos(count=limit):
                v = video.as_dict
                videos.append(_normalize_tiktok_video(v))
                if len(videos) >= limit:
                    break
        return videos

    if on_progress:
        on_progress("Fetching via TikTokApi…", 30)
    videos = asyncio.run(_fetch())

    if videos:
        save_cache(cache_key, videos)
    return videos


def _scrape_tiktok_via_requests(
    limit: int, session_id: str | None, on_progress: Callable | None, cache_key: str
) -> list[dict]:
    """Fallback: direct requests to TikTok's internal explore endpoint."""
    req = _requests_lib()
    session = req.Session()
    session.headers.update(_TIKTOK_HEADERS)

    if session_id:
        session.cookies.set("sessionid", session_id, domain=".tiktok.com")

    params = {
        "aid": "1988",
        "count": str(min(limit, 30)),
        "itemID": "1",
        "address_code": "5344085",
        "app_language": "en",
        "app_name": "tiktok_web",
    }

    if on_progress:
        on_progress("Fetching TikTok explore feed…", 30)

    resp = session.get(
        "https://www.tiktok.com/api/explore/item_list/",
        params=params,
        timeout=30,
    )

    if resp.status_code != 200:
        raise RuntimeError(f"TikTok API returned {resp.status_code}")

    try:
        data = resp.json()
    except json.JSONDecodeError:
        raise RuntimeError("TikTok returned non-JSON response (rate limited?)")

    items = data.get("itemList", [])
    videos = [_normalize_tiktok_video(v) for v in items[:limit]]

    if on_progress:
        on_progress(f"Scraped {len(videos)} TikTok trending videos", 80)

    if videos:
        save_cache(cache_key, videos)
    return videos


def _normalize_tiktok_video(v: dict) -> dict:
    desc = v.get("desc", "") or ""
    author = v.get("author", {}) or {}
    stats = v.get("stats", {}) or {}
    music = v.get("music", {}) or {}
    video_info = v.get("video", {}) or {}

    hashtags = _extract_hashtags(desc)
    challenges = [c.get("title", "") for c in (v.get("challenges") or [])]
    hashtags += [f"#{c}" for c in challenges if c]

    return {
        "platform": "tiktok",
        "title": desc[:200],
        "channel": author.get("uniqueId", author.get("nickname", "")),
        "views": stats.get("playCount", 0),
        "likes": stats.get("diggCount", 0),
        "shares": stats.get("shareCount", 0),
        "comments": stats.get("commentCount", 0),
        "tags": challenges[:10],
        "hashtags": list(set(hashtags))[:20],
        "description": desc[:500],
        "url": f"https://www.tiktok.com/@{author.get('uniqueId','')}/video/{v.get('id','')}",
        "thumbnail": video_info.get("cover", ""),
        "duration": video_info.get("duration", 0),
        "upload_date": str(v.get("createTime", "")),
        "categories": challenges[:5],
        "music_used": {
            "title": music.get("title", ""),
            "artist": music.get("authorName", ""),
            "id": str(music.get("id", "")),
            "duration": music.get("duration", 0),
        } if music.get("title") else None,
    }


def scrape_tiktok_hashtag(
    hashtag: str,
    limit: int = 30,
    session_id: str | None = None,
    use_cache: bool = True,
) -> list[dict]:
    """Scrape videos for a specific TikTok hashtag challenge."""
    cache_key = f"tt_hashtag_{hashtag}_{limit}"
    if use_cache:
        cached = load_cache(cache_key, max_age_secs=3600)
        if cached:
            return cached

    req = _requests_lib()
    session = req.Session()
    session.headers.update(_TIKTOK_HEADERS)
    if session_id:
        session.cookies.set("sessionid", session_id, domain=".tiktok.com")

    # First get hashtag challenge ID
    resp = session.get(
        f"https://www.tiktok.com/tag/{hashtag.lstrip('#')}",
        timeout=30,
        allow_redirects=True,
    )
    # Extract challenge data from page or use challenge search API
    params = {
        "challengeName": hashtag.lstrip("#"),
        "aid": "1988",
    }
    resp2 = session.get(
        "https://www.tiktok.com/api/challenge/detail/",
        params=params,
        timeout=30,
    )
    challenge_id = None
    if resp2.status_code == 200:
        try:
            challenge_data = resp2.json()
            challenge_id = challenge_data.get("challengeInfo", {}).get("challenge", {}).get("id")
        except json.JSONDecodeError:
            pass

    videos = []
    if challenge_id:
        cursor = 0
        while len(videos) < limit:
            params2 = {
                "aid": "1988",
                "challengeID": challenge_id,
                "count": "30",
                "cursor": str(cursor),
            }
            r = session.get(
                "https://www.tiktok.com/api/challenge/item_list/",
                params=params2,
                timeout=30,
            )
            if r.status_code != 200:
                break
            data = r.json()
            items = data.get("itemList", [])
            if not items:
                break
            videos.extend(_normalize_tiktok_video(v) for v in items)
            cursor = data.get("cursor", cursor + 30)
            if not data.get("hasMore", False):
                break

    videos = videos[:limit]
    if videos:
        save_cache(cache_key, videos)
    return videos


def get_tiktok_trending_sounds(videos: list[dict]) -> list[dict]:
    """Extract and rank trending sounds from a list of TikTok videos."""
    sound_counts: dict[str, dict] = {}
    for v in videos:
        music = v.get("music_used")
        if not music or not music.get("title"):
            continue
        key = f"{music.get('title','')}__{music.get('artist','')}"
        if key not in sound_counts:
            sound_counts[key] = {
                "title": music["title"],
                "artist": music.get("artist", ""),
                "id": music.get("id", ""),
                "duration": music.get("duration", 0),
                "video_count": 0,
                "total_views": 0,
            }
        sound_counts[key]["video_count"] += 1
        sound_counts[key]["total_views"] += v.get("views", 0)

    ranked = sorted(sound_counts.values(), key=lambda x: x["video_count"], reverse=True)
    return ranked


def get_trending_hashtags(videos: list[dict], top_n: int = 30) -> list[dict]:
    """Extract and rank hashtags from scraped videos."""
    counts: dict[str, dict] = {}
    for v in videos:
        views = v.get("views", 0)
        for tag in v.get("hashtags", []):
            tag = tag.lower().strip()
            if not tag or tag == "#":
                continue
            if tag not in counts:
                counts[tag] = {"hashtag": tag, "appearances": 0, "total_views": 0, "platform": v.get("platform", "")}
            counts[tag]["appearances"] += 1
            counts[tag]["total_views"] += views

    ranked = sorted(counts.values(), key=lambda x: x["total_views"], reverse=True)
    return ranked[:top_n]
