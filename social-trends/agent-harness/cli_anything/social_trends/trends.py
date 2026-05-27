"""Scrapers for YouTube and TikTok viral trending content."""
from __future__ import annotations
import json
import re
import time
from typing import Any
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

_YT_TRENDING_URL = "https://www.youtube.com/feed/trending"
_YT_INITIAL_DATA_RE = re.compile(r"var ytInitialData\s*=\s*(\{.+?\});\s*</script>", re.S)


def fetch_youtube_trending(
    category: str = "now",
    country: str = "US",
    limit: int = 20,
) -> list[dict[str, Any]]:
    """
    Scrape YouTube trending page and return structured video records.

    category: 'now' | 'music' | 'gaming' | 'movies'
    """
    params: dict[str, str] = {"gl": country}
    cat_map = {"now": "", "music": "10", "gaming": "20", "movies": "30"}
    if category in cat_map and cat_map[category]:
        params["bp"] = _yt_category_bp(cat_map[category])

    try:
        r = requests.get(_YT_TRENDING_URL, headers=HEADERS, params=params, timeout=15)
        r.raise_for_status()
    except requests.RequestException as exc:
        return [{"error": str(exc), "source": "youtube"}]

    m = _YT_INITIAL_DATA_RE.search(r.text)
    if not m:
        return [{"error": "could not parse ytInitialData", "source": "youtube"}]

    try:
        data = json.loads(m.group(1))
        items = _walk_yt_data(data)[:limit]
    except Exception as exc:  # noqa: BLE001
        return [{"error": f"parse error: {exc}", "source": "youtube"}]

    return items


def _yt_category_bp(cat_id: str) -> str:
    """Build YouTube category browse param."""
    bp_map = {"10": "4gINGgt5dG1hX2NoYXJ0cw%3D%3D", "20": "4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D", "30": "4gIKGghmaWxtc19hbmQ%3D"}
    return bp_map.get(cat_id, "")


def _walk_yt_data(data: dict) -> list[dict[str, Any]]:
    """Recursively walk ytInitialData to find video renderer items."""
    results: list[dict[str, Any]] = []

    def _recurse(obj: Any) -> None:
        if isinstance(obj, dict):
            if "videoRenderer" in obj:
                vr = obj["videoRenderer"]
                results.append(_parse_video_renderer(vr))
            else:
                for v in obj.values():
                    _recurse(v)
        elif isinstance(obj, list):
            for item in obj:
                _recurse(item)

    _recurse(data)
    return results


def _parse_video_renderer(vr: dict) -> dict[str, Any]:
    title = _run_text(vr.get("title", {}))
    channel = _run_text(vr.get("ownerText", {}))
    vid_id = vr.get("videoId", "")
    views = _run_text(vr.get("viewCountText", {}))
    published = _run_text(vr.get("publishedTimeText", {}))
    duration = _run_text(vr.get("lengthText", {}))
    description = _run_text(vr.get("descriptionSnippet", {}))

    hashtags: list[str] = []
    for b in vr.get("badges", []):
        label = _run_text(b.get("metadataBadgeRenderer", {}).get("label", {}))
        if label:
            hashtags.append(label)

    return {
        "source": "youtube",
        "video_id": vid_id,
        "url": f"https://www.youtube.com/watch?v={vid_id}",
        "title": title,
        "channel": channel,
        "views": views,
        "published": published,
        "duration": duration,
        "description_snippet": description,
        "badges": hashtags,
    }


def _run_text(obj: Any) -> str:
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        if "simpleText" in obj:
            return obj["simpleText"]
        if "runs" in obj:
            return "".join(r.get("text", "") for r in obj["runs"])
    return ""


# ── TikTok ────────────────────────────────────────────────────────────────────

_TT_DISCOVER_URL = "https://www.tiktok.com/api/explore/item_list/"
_TT_TRENDING_URL = "https://www.tiktok.com/trending"


def fetch_tiktok_trending(limit: int = 20, region: str = "US") -> list[dict[str, Any]]:
    """
    Fetch TikTok trending videos via the explore API endpoint.
    Falls back to scraping the trending page if the API is blocked.
    """
    results = _tt_api(limit, region)
    if results and "error" not in results[0]:
        return results
    return _tt_scrape(limit)


def _tt_api(limit: int, region: str) -> list[dict[str, Any]]:
    params = {
        "aid": "1988",
        "count": str(limit),
        "itemList": "1",
        "region": region,
        "type": "1",
        "secUid": "",
        "maxCursor": "0",
        "minCursor": "0",
        "sourceType": "12",
        "appId": "1233",
        "language": "en",
    }
    headers = {
        **HEADERS,
        "Referer": "https://www.tiktok.com/",
        "X-Requested-With": "XMLHttpRequest",
    }
    try:
        r = requests.get(_TT_DISCOVER_URL, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        body = r.json()
        items = body.get("itemList", [])
        return [_parse_tt_item(i) for i in items[:limit]]
    except Exception as exc:  # noqa: BLE001
        return [{"error": str(exc), "source": "tiktok"}]


def _tt_scrape(limit: int) -> list[dict[str, Any]]:
    """Scrape TikTok trending page for hashtag/challenge cards."""
    try:
        r = requests.get(_TT_TRENDING_URL, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")

        results: list[dict[str, Any]] = []
        # Extract any embedded JSON state
        for tag in soup.find_all("script", id="SIGI_STATE"):
            try:
                state = json.loads(tag.string or "{}")
                items = (
                    state.get("ItemModule", {})
                    or state.get("HomeModule", {}).get("feedItems", {})
                )
                if isinstance(items, dict):
                    for vid_id, item in list(items.items())[:limit]:
                        results.append(_parse_sigi_item(vid_id, item))
                    if results:
                        return results
            except Exception:  # noqa: BLE001
                continue

        # Fallback: pull challenge/hashtag links visible on the page
        for a in soup.select("a[href*='/tag/']")[:limit]:
            tag_name = a.get_text(strip=True)
            href = a.get("href", "")
            results.append({"source": "tiktok", "type": "hashtag", "tag": tag_name, "url": href})
        return results or [{"error": "no trending data extracted", "source": "tiktok"}]
    except Exception as exc:  # noqa: BLE001
        return [{"error": str(exc), "source": "tiktok"}]


def _parse_tt_item(item: dict) -> dict[str, Any]:
    desc = item.get("desc", "")
    author = item.get("author", {})
    stats = item.get("stats", {})
    music = item.get("music", {})
    hashtags = [c.get("hashtagName", "") for c in item.get("challenges", []) if c.get("hashtagName")]

    return {
        "source": "tiktok",
        "video_id": item.get("id", ""),
        "url": f"https://www.tiktok.com/@{author.get('uniqueId', '')}/video/{item.get('id', '')}",
        "description": desc,
        "author": author.get("uniqueId", ""),
        "author_followers": author.get("stats", {}).get("followerCount", 0),
        "likes": stats.get("diggCount", 0),
        "comments": stats.get("commentCount", 0),
        "shares": stats.get("shareCount", 0),
        "plays": stats.get("playCount", 0),
        "hashtags": hashtags,
        "music_title": music.get("title", ""),
        "music_author": music.get("authorName", ""),
        "music_id": music.get("id", ""),
    }


def _parse_sigi_item(vid_id: str, item: dict) -> dict[str, Any]:
    desc = item.get("desc", "")
    stats = item.get("stats", {})
    author = item.get("author", "")
    music = item.get("music", {})
    hashtags = [c.get("title", "") for c in item.get("challenges", []) if c.get("title")]

    return {
        "source": "tiktok",
        "video_id": vid_id,
        "url": f"https://www.tiktok.com/@{author}/video/{vid_id}",
        "description": desc,
        "author": author,
        "likes": stats.get("diggCount", 0),
        "comments": stats.get("commentCount", 0),
        "shares": stats.get("shareCount", 0),
        "plays": stats.get("playCount", 0),
        "hashtags": hashtags,
        "music_title": music.get("title", ""),
        "music_author": music.get("authorName", ""),
        "music_id": str(music.get("id", "")),
    }
