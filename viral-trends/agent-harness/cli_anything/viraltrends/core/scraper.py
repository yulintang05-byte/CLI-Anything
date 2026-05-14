"""Scraping backends for YouTube and TikTok public trending data.

Uses yt-dlp subprocess for YouTube (no API key required) and
requests + public TikTok endpoints for TikTok trending data.
"""

import json
import subprocess
import time
import re
from typing import Any
from collections import Counter
import urllib.request
import urllib.parse
import urllib.error


# ── YouTube ───────────────────────────────────────────────────────────────────

_YT_TRENDING_URLS = {
    "US": "https://www.youtube.com/feed/trending",
    "now":   "https://www.youtube.com/feed/trending?bp=4gINGgt5dGQtdHJlbmRpbmcy",
    "music": "https://www.youtube.com/feed/trending?bp=4gIuGgtndXpfdHJlbmRpbmcqCwoJqAEB",
    "gaming": "https://www.youtube.com/feed/trending?bp=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D",
}


def _yt_dlp_available() -> bool:
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def youtube_trending(region: str = "US", category: str = "now", limit: int = 20) -> list[dict]:
    """Fetch YouTube trending videos using yt-dlp."""
    url = _YT_TRENDING_URLS.get(category, _YT_TRENDING_URLS["now"])
    if region and region.upper() != "US":
        # yt-dlp geo-bypass hint
        extra = ["--geo-bypass-country", region.upper()]
    else:
        extra = []

    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--print", "%(id)s\t%(title)s\t%(uploader)s\t%(view_count)s\t%(like_count)s\t%(duration)s\t%(description)s",
        "--playlist-end", str(limit),
        *extra,
        url,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            return _yt_fallback_trending(region, limit)
        return _parse_yt_dlp_output(result.stdout, category)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return _yt_fallback_trending(region, limit)


def _parse_yt_dlp_output(stdout: str, category: str) -> list[dict]:
    videos = []
    for i, line in enumerate(stdout.strip().splitlines()):
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        vid_id = parts[0] if parts[0] != "NA" else ""
        title = parts[1] if len(parts) > 1 else ""
        uploader = parts[2] if len(parts) > 2 and parts[2] != "NA" else ""
        views = _safe_int(parts[3] if len(parts) > 3 else "")
        likes = _safe_int(parts[4] if len(parts) > 4 else "")
        duration = _safe_int(parts[5] if len(parts) > 5 else "")
        description = parts[6] if len(parts) > 6 and parts[6] != "NA" else ""

        hashtags = _extract_hashtags(title + " " + description)
        videos.append({
            "rank": i + 1,
            "platform": "youtube",
            "category": category,
            "id": vid_id,
            "url": f"https://www.youtube.com/watch?v={vid_id}" if vid_id else "",
            "title": title,
            "channel": uploader,
            "views": views,
            "likes": likes,
            "duration_sec": duration,
            "hashtags": hashtags,
        })
    return videos


def _yt_fallback_trending(region: str, limit: int) -> list[dict]:
    """Fallback: hit YouTube's internal API endpoint used by the trending page."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    payload = json.dumps({
        "context": {
            "client": {
                "clientName": "WEB",
                "clientVersion": "2.20240101",
                "gl": region.upper() if region else "US",
                "hl": "en",
            }
        },
        "browseId": "FEtrending",
    }).encode()

    req = urllib.request.Request(
        "https://www.youtube.com/youtubei/v1/browse?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
        data=payload,
        headers={**headers, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        return _parse_yt_browse_response(data, limit)
    except Exception:
        return []


def _parse_yt_browse_response(data: dict, limit: int) -> list[dict]:
    videos = []
    try:
        tabs = data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]
        for tab in tabs:
            items = (
                tab.get("tabRenderer", {})
                .get("content", {})
                .get("sectionListRenderer", {})
                .get("contents", [])
            )
            for section in items:
                for item in section.get("itemSectionRenderer", {}).get("contents", []):
                    for shelf in item.get("shelfRenderer", {}).get("content", {}).get("expandedShelfContentsRenderer", {}).get("items", []):
                        vr = shelf.get("videoRenderer", {})
                        if not vr:
                            continue
                        vid_id = vr.get("videoId", "")
                        title = vr.get("title", {}).get("runs", [{}])[0].get("text", "")
                        channel = vr.get("ownerText", {}).get("runs", [{}])[0].get("text", "")
                        views_str = vr.get("viewCountText", {}).get("simpleText", "0")
                        videos.append({
                            "rank": len(videos) + 1,
                            "platform": "youtube",
                            "id": vid_id,
                            "url": f"https://www.youtube.com/watch?v={vid_id}",
                            "title": title,
                            "channel": channel,
                            "views": _parse_view_count(views_str),
                            "hashtags": _extract_hashtags(title),
                        })
                        if len(videos) >= limit:
                            return videos
    except (KeyError, IndexError, TypeError):
        pass
    return videos


# ── TikTok ────────────────────────────────────────────────────────────────────

_TT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
}


def tiktok_trending(region: str = "US", limit: int = 20) -> list[dict]:
    """Fetch TikTok trending videos via public discover endpoint."""
    results = _tiktok_discover(region, limit)
    if not results:
        results = _tiktok_trending_hashtags_page(limit)
    return results


def _tiktok_discover(region: str, limit: int) -> list[dict]:
    params = urllib.parse.urlencode({
        "count": min(limit, 30),
        "id": 1,
        "type": 5,
        "secUid": "",
        "maxCursor": 0,
        "minCursor": 0,
        "shareUid": "",
        "recType": 3,
        "lang": "en",
        "region": region.upper(),
    })
    url = f"https://www.tiktok.com/api/explore/item_list/?{params}"
    req = urllib.request.Request(url, headers=_TT_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        return _parse_tiktok_items(data.get("itemList", []))
    except Exception:
        return []


def _tiktok_trending_hashtags_page(limit: int) -> list[dict]:
    """Fallback: scrape TikTok trending hashtags from discover page HTML."""
    req = urllib.request.Request(
        "https://www.tiktok.com/trending",
        headers={**_TT_HEADERS, "Accept": "text/html,application/xhtml+xml"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        # Extract SIGI_STATE JSON blob
        match = re.search(r'<script id="SIGI_STATE"[^>]*>(.*?)</script>', html, re.DOTALL)
        if not match:
            return []
        state = json.loads(match.group(1))
        items = state.get("ItemModule", {})
        results = []
        for i, (_, item) in enumerate(items.items()):
            if i >= limit:
                break
            results.append(_parse_tiktok_item(item, i + 1))
        return results
    except Exception:
        return []


def _parse_tiktok_items(items: list) -> list[dict]:
    return [_parse_tiktok_item(item, i + 1) for i, item in enumerate(items)]


def _parse_tiktok_item(item: dict, rank: int) -> dict:
    desc = item.get("desc", "")
    stats = item.get("stats", item.get("statsV2", {}))
    music = item.get("music", {})
    author = item.get("author", {})
    challenges = item.get("challenges", [])

    hashtags = [c.get("title", "") for c in challenges if c.get("title")]
    hashtags += _extract_hashtags(desc)
    hashtags = list(dict.fromkeys(h for h in hashtags if h))  # dedup

    return {
        "rank": rank,
        "platform": "tiktok",
        "id": item.get("id", ""),
        "url": f"https://www.tiktok.com/@{author.get('uniqueId','')}/video/{item.get('id','')}",
        "description": desc[:200],
        "author": author.get("uniqueId", ""),
        "author_followers": _safe_int(str(author.get("followerCount", 0))),
        "plays": _safe_int(str(stats.get("playCount", stats.get("play_count", 0)))),
        "likes": _safe_int(str(stats.get("diggCount", stats.get("digg_count", 0)))),
        "comments": _safe_int(str(stats.get("commentCount", stats.get("comment_count", 0)))),
        "shares": _safe_int(str(stats.get("shareCount", stats.get("share_count", 0)))),
        "hashtags": hashtags[:10],
        "music_title": music.get("title", ""),
        "music_author": music.get("authorName", ""),
        "music_id": str(music.get("id", "")),
        "duration_sec": item.get("video", {}).get("duration", 0),
    }


# ── Trending Hashtags ─────────────────────────────────────────────────────────

def youtube_trending_hashtags(region: str = "US", limit: int = 50) -> list[dict]:
    videos = youtube_trending(region=region, limit=50)
    counter: Counter = Counter()
    for v in videos:
        for tag in v.get("hashtags", []):
            if tag:
                counter[tag.lower().lstrip("#")] += 1
    return [
        {"tag": f"#{tag}", "count": cnt, "platform": "youtube"}
        for tag, cnt in counter.most_common(limit)
    ]


def tiktok_trending_hashtags(region: str = "US", limit: int = 50) -> list[dict]:
    """Fetch trending TikTok hashtags from discover/challenge endpoint."""
    params = urllib.parse.urlencode({
        "discoverType": 0,
        "needItemList": False,
        "keyWord": "",
        "offset": 0,
        "count": 30,
        "useRecommend": False,
        "language": "en",
    })
    url = f"https://www.tiktok.com/api/discover/challenge/?{params}"
    req = urllib.request.Request(url, headers=_TT_HEADERS)
    tags = []
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        for item in data.get("challengeInfoList", [])[:limit]:
            ch = item.get("challengeInfo", {}).get("challenge", {})
            stats = item.get("challengeInfo", {}).get("stats", {})
            tags.append({
                "tag": "#" + ch.get("title", "").lstrip("#"),
                "video_count": _safe_int(str(stats.get("videoCount", 0))),
                "view_count": _safe_int(str(stats.get("viewCount", 0))),
                "platform": "tiktok",
            })
    except Exception:
        pass

    if not tags:
        # Derive from trending videos
        videos = tiktok_trending(region=region, limit=30)
        counter: Counter = Counter()
        for v in videos:
            for tag in v.get("hashtags", []):
                if tag:
                    counter[tag.lower().lstrip("#")] += 1
        tags = [
            {"tag": f"#{t}", "video_count": c, "view_count": 0, "platform": "tiktok"}
            for t, c in counter.most_common(limit)
        ]
    return tags[:limit]


# ── Trending Music ────────────────────────────────────────────────────────────

def tiktok_trending_music(region: str = "US", limit: int = 20) -> list[dict]:
    """Fetch trending TikTok sounds/music."""
    params = urllib.parse.urlencode({
        "discoverType": 0,
        "needItemList": False,
        "keyWord": "",
        "offset": 0,
        "count": 30,
        "useRecommend": False,
        "language": "en",
    })
    url = f"https://www.tiktok.com/api/discover/music/?{params}"
    req = urllib.request.Request(url, headers=_TT_HEADERS)
    sounds = []
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        for i, item in enumerate(data.get("musicInfo", [])[:limit]):
            music = item.get("music", {})
            sounds.append({
                "rank": i + 1,
                "platform": "tiktok",
                "id": str(music.get("id", "")),
                "title": music.get("title", ""),
                "author": music.get("authorName", ""),
                "duration_sec": music.get("duration", 0),
                "url": f"https://www.tiktok.com/music/{str(music.get('id',''))}",
                "is_original": music.get("original", False),
            })
    except Exception:
        pass

    if not sounds:
        sounds = _derive_music_from_trending(region, limit)
    return sounds


def _derive_music_from_trending(region: str, limit: int) -> list[dict]:
    videos = tiktok_trending(region=region, limit=40)
    counter: dict[str, dict] = {}
    for v in videos:
        mid = v.get("music_id", "")
        if not mid:
            continue
        if mid not in counter:
            counter[mid] = {
                "rank": len(counter) + 1,
                "platform": "tiktok",
                "id": mid,
                "title": v.get("music_title", ""),
                "author": v.get("music_author", ""),
                "uses": 0,
                "url": f"https://www.tiktok.com/music/{mid}",
            }
        counter[mid]["uses"] += 1

    return sorted(counter.values(), key=lambda x: x["uses"], reverse=True)[:limit]


def youtube_trending_music(region: str = "US", limit: int = 20) -> list[dict]:
    """Fetch YouTube music trending (Music category)."""
    videos = youtube_trending(region=region, category="music", limit=limit)
    return [
        {
            "rank": v["rank"],
            "platform": "youtube",
            "title": v["title"],
            "channel": v["channel"],
            "views": v["views"],
            "url": v["url"],
            "hashtags": v.get("hashtags", []),
        }
        for v in videos
    ]


# ── Utilities ─────────────────────────────────────────────────────────────────

def _extract_hashtags(text: str) -> list[str]:
    return list(dict.fromkeys(
        m.group(0).lower()
        for m in re.finditer(r"#\w+", text)
    ))


def _safe_int(val: str) -> int:
    try:
        return int(str(val).replace(",", "").strip())
    except (ValueError, TypeError):
        return 0


def _parse_view_count(text: str) -> int:
    text = text.lower().replace(",", "").replace(" views", "").strip()
    multipliers = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}
    for suffix, mult in multipliers.items():
        if text.endswith(suffix):
            try:
                return int(float(text[:-1]) * mult)
            except ValueError:
                return 0
    return _safe_int(text)
