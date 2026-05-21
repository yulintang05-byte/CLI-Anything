"""
YouTube and TikTok viral trend scrapers.

YouTube:  uses the YouTube Data API v3 when YOUTUBE_API_KEY env var is set;
          falls back to parsing the embedded ytInitialData JSON from the
          trending feed page (no key required).

TikTok:   uses TikTok Creative Center public endpoints — no auth required.
          Endpoint docs: https://ads.tiktok.com/business/creativecenter/
"""
import json
import os
import re
import time
from typing import Any, Dict, List, Optional

# ─── YouTube ─────────────────────────────────────────────────────────────────

_YT_TRENDING_URL = "https://www.youtube.com/feed/trending"
_YT_API_URL = "https://www.googleapis.com/youtube/v3/videos"

# YouTube category IDs relevant to viral/entertainment content
YOUTUBE_CATEGORIES = {
    "all":       "0",
    "music":     "10",
    "gaming":    "20",
    "sports":    "17",
    "tech":      "28",
    "entertainment": "24",
    "news":      "25",
}


def _yt_api_trending(region: str, category: str, limit: int, api_key: str) -> List[Dict]:
    """Fetch trending via YouTube Data API v3."""
    from cli_anything.social.utils.http import get_json
    params = {
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular",
        "regionCode": region.upper(),
        "maxResults": min(limit, 50),
        "key": api_key,
    }
    cat_id = YOUTUBE_CATEGORIES.get(category.lower(), "0")
    if cat_id != "0":
        params["videoCategoryId"] = cat_id
    data = get_json(_YT_API_URL, params=params)
    results = []
    for item in data.get("items", []):
        s = item.get("snippet", {})
        st = item.get("statistics", {})
        results.append({
            "rank":          len(results) + 1,
            "id":            item.get("id", ""),
            "title":         s.get("title", ""),
            "channel":       s.get("channelTitle", ""),
            "published":     s.get("publishedAt", "")[:10],
            "views":         int(st.get("viewCount", 0)),
            "likes":         int(st.get("likeCount", 0)),
            "comments":      int(st.get("commentCount", 0)),
            "url":           f"https://youtu.be/{item.get('id','')}",
            "tags":          s.get("tags", [])[:10],
            "category_id":   s.get("categoryId", ""),
            "source":        "youtube_api",
        })
    return results


def _yt_scrape_trending(region: str, limit: int) -> List[Dict]:
    """Scrape YouTube trending page — no API key needed."""
    from cli_anything.social.utils.http import get
    url = _YT_TRENDING_URL
    params = {"gl": region.upper(), "hl": "en"}
    resp = get(url, params=params, headers={"Accept": "text/html"})
    text = resp.text

    # YouTube embeds all page data in window["ytInitialData"] = {...};
    match = re.search(r'var ytInitialData\s*=\s*(\{.+?\});\s*</script>', text, re.DOTALL)
    if not match:
        match = re.search(r'window\["ytInitialData"\]\s*=\s*(\{.+?\});\s*</script>', text, re.DOTALL)
    if not match:
        raise RuntimeError("Could not locate ytInitialData in YouTube trending page")

    raw = json.loads(match.group(1))

    # Navigate the nested JSON to reach video renderer items
    results: List[Dict] = []
    try:
        tabs = (
            raw["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]
        )
        for tab in tabs:
            tab_content = tab.get("tabRenderer", {}).get("content", {})
            sections = tab_content.get("sectionListRenderer", {}).get("contents", [])
            for section in sections:
                items = (
                    section
                    .get("itemSectionRenderer", {})
                    .get("contents", [])
                )
                for item in items:
                    vr = item.get("videoRenderer") or item.get("gridVideoRenderer")
                    if not vr:
                        continue
                    vid_id = vr.get("videoId", "")
                    title = _yt_text(vr.get("title"))
                    channel = _yt_text(vr.get("ownerText") or vr.get("shortBylineText"))
                    views_raw = _yt_text(vr.get("viewCountText") or vr.get("shortViewCountText"))
                    results.append({
                        "rank":    len(results) + 1,
                        "id":      vid_id,
                        "title":   title,
                        "channel": channel,
                        "views":   _parse_view_str(views_raw),
                        "views_raw": views_raw,
                        "url":     f"https://youtu.be/{vid_id}",
                        "tags":    [],
                        "source":  "youtube_scrape",
                    })
                    if len(results) >= limit:
                        return results
    except (KeyError, TypeError):
        pass
    return results


def _yt_text(node: Any) -> str:
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    runs = node.get("runs", [])
    if runs:
        return "".join(r.get("text", "") for r in runs)
    return node.get("simpleText", "")


def _parse_view_str(s: str) -> int:
    s = s.lower().replace(",", "").replace(" views", "").strip()
    try:
        if s.endswith("b"):
            return int(float(s[:-1]) * 1_000_000_000)
        if s.endswith("m"):
            return int(float(s[:-1]) * 1_000_000)
        if s.endswith("k"):
            return int(float(s[:-1]) * 1_000)
        return int(s)
    except (ValueError, IndexError):
        return 0


def youtube_trending(
    region: str = "US",
    category: str = "all",
    limit: int = 20,
    api_key: Optional[str] = None,
) -> List[Dict]:
    """Return trending YouTube videos. Uses API if key present, else scrapes."""
    key = api_key or os.environ.get("YOUTUBE_API_KEY", "")
    if key:
        return _yt_api_trending(region, category, limit, key)
    return _yt_scrape_trending(region, limit)[:limit]


# ─── TikTok Creative Center ───────────────────────────────────────────────────

_TT_BASE = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend"
_TT_HEADERS = {
    "Referer": "https://ads.tiktok.com/business/creativecenter/inspiration/popular/pc/en",
    "Origin":  "https://ads.tiktok.com",
}


def tiktok_trending_hashtags(
    region: str = "US",
    period: int = 7,
    limit: int = 30,
) -> List[Dict]:
    """Return trending TikTok hashtags from Creative Center."""
    from cli_anything.social.utils.http import get_json
    url = f"{_TT_BASE}/hashtag/list"
    params = {
        "period":       period,
        "page":         1,
        "limit":        min(limit, 50),
        "country_code": region.upper(),
        "sort_by":      "popular",
    }
    data = get_json(url, params=params, headers=_TT_HEADERS)
    items = data.get("data", {}).get("list", [])
    results = []
    for i, item in enumerate(items[:limit]):
        results.append({
            "rank":        i + 1,
            "hashtag":     item.get("hashtag_name", ""),
            "posts":       item.get("publish_cnt", 0),
            "views":       item.get("video_views", 0),
            "trend":       item.get("trend", ""),
            "is_promoted": item.get("is_promoted", False),
            "link":        f"https://www.tiktok.com/tag/{item.get('hashtag_name','')}",
            "source":      "tiktok_creative_center",
        })
    return results


def tiktok_trending_music(
    region: str = "US",
    period: int = 7,
    limit: int = 20,
) -> List[Dict]:
    """Return trending TikTok sounds/music from Creative Center."""
    from cli_anything.social.utils.http import get_json
    url = f"{_TT_BASE}/music/list"
    params = {
        "period":       period,
        "page":         1,
        "limit":        min(limit, 50),
        "country_code": region.upper(),
        "sort_by":      "popular",
    }
    data = get_json(url, params=params, headers=_TT_HEADERS)
    items = data.get("data", {}).get("music_list", [])
    results = []
    for i, item in enumerate(items[:limit]):
        results.append({
            "rank":      i + 1,
            "title":     item.get("music_name", ""),
            "artist":    item.get("author", ""),
            "duration":  item.get("duration", 0),
            "uses":      item.get("use_cnt", 0),
            "views":     item.get("video_views", 0),
            "trend":     item.get("trend", ""),
            "preview":   item.get("play_url", ""),
            "cover":     item.get("cover", ""),
            "source":    "tiktok_creative_center",
        })
    return results


def tiktok_trending_creators(
    region: str = "US",
    period: int = 7,
    limit: int = 20,
) -> List[Dict]:
    """Return trending TikTok creators from Creative Center."""
    from cli_anything.social.utils.http import get_json
    url = f"{_TT_BASE}/creator/list"
    params = {
        "period":       period,
        "page":         1,
        "limit":        min(limit, 50),
        "country_code": region.upper(),
        "sort_by":      "popular",
    }
    data = get_json(url, params=params, headers=_TT_HEADERS)
    items = data.get("data", {}).get("creator_list", [])
    results = []
    for i, item in enumerate(items[:limit]):
        results.append({
            "rank":        i + 1,
            "handle":      item.get("nick_name", ""),
            "followers":   item.get("follower_cnt", 0),
            "avg_views":   item.get("avg_views", 0),
            "niche":       item.get("industry_v2_name", ""),
            "country":     item.get("country", ""),
            "verified":    item.get("is_verified", False),
            "profile_url": f"https://www.tiktok.com/@{item.get('unique_id','')}",
            "source":      "tiktok_creative_center",
        })
    return results


def youtube_trending_music(region: str = "US", limit: int = 20) -> List[Dict]:
    """Wrapper: get YouTube trending filtered to music category."""
    return youtube_trending(region=region, category="music", limit=limit)
