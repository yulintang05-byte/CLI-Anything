"""Viral trend scrapers for YouTube and TikTok."""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field, asdict
from typing import Optional

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class Trend:
    rank: int
    title: str
    platform: str
    url: str
    views: Optional[int] = None
    likes: Optional[int] = None
    hashtags: list[str] = field(default_factory=list)
    music: Optional[str] = None
    creator: Optional[str] = None
    category: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TrendsResult:
    platform: str
    region: str
    category: str
    fetched_at: str
    trends: list[Trend]

    def to_dict(self) -> dict:
        return {
            "platform": self.platform,
            "region": self.region,
            "category": self.category,
            "fetched_at": self.fetched_at,
            "count": len(self.trends),
            "trends": [t.to_dict() for t in self.trends],
        }


# ---------------------------------------------------------------------------
# YouTube trending (YouTube Data API v3)
# ---------------------------------------------------------------------------

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

YOUTUBE_CATEGORY_IDS = {
    "all": "0",
    "film": "1",
    "music": "10",
    "gaming": "20",
    "news": "25",
    "sports": "17",
    "entertainment": "24",
    "howto": "26",
    "science": "28",
    "travel": "19",
    "people": "22",
    "comedy": "23",
    "education": "27",
    "fashion": "30",
    "autos": "2",
    "pets": "15",
}


def _yt_api_get(endpoint: str, params: dict, api_key: str) -> dict:
    params["key"] = api_key
    url = f"{YOUTUBE_API_BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"YouTube API error {e.code}: {body}") from e


def fetch_youtube_trending(
    api_key: str,
    region: str = "US",
    category: str = "all",
    limit: int = 25,
) -> TrendsResult:
    """
    Fetch trending YouTube videos via the official YouTube Data API v3.

    Requires a free API key from https://console.cloud.google.com/ with
    YouTube Data API v3 enabled. Costs 1 unit per call (free quota = 10k/day).
    """
    cat_id = YOUTUBE_CATEGORY_IDS.get(category.lower(), "0")
    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region.upper(),
        "videoCategoryId": cat_id,
        "maxResults": min(limit, 50),
    }
    data = _yt_api_get("videos", params, api_key)

    trends: list[Trend] = []
    for rank, item in enumerate(data.get("items", []), start=1):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        vid_id = item.get("id", "")
        tags = snippet.get("tags", [])
        hashtags = [t for t in tags if t.startswith("#")]
        if not hashtags:
            hashtags = ["#" + t.replace(" ", "") for t in tags[:5]]

        trends.append(Trend(
            rank=rank,
            title=snippet.get("title", ""),
            platform="youtube",
            url=f"https://youtu.be/{vid_id}",
            views=int(stats.get("viewCount", 0)),
            likes=int(stats.get("likeCount", 0)),
            hashtags=hashtags,
            creator=snippet.get("channelTitle", ""),
            category=snippet.get("categoryId", ""),
        ))

    return TrendsResult(
        platform="youtube",
        region=region.upper(),
        category=category,
        fetched_at=_now_iso(),
        trends=trends,
    )


def fetch_youtube_trending_no_key(region: str = "US", limit: int = 25) -> TrendsResult:
    """
    Scrape YouTube trending page without an API key using the public RSS feed
    and the hidden trending endpoint. Less reliable — use the API key version
    in production.
    """
    url = (
        f"https://www.youtube.com/feed/trending?gl={region.upper()}&hl=en"
    )
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        raise RuntimeError(f"Failed to fetch YouTube trending page: {e}") from e

    # Extract initial data JSON blob
    match = re.search(
        r"var ytInitialData\s*=\s*(\{.*?\});\s*(?:var |</script>)", html, re.DOTALL
    )
    if not match:
        raise RuntimeError("Could not parse YouTube trending page (page structure may have changed)")

    try:
        yt_data = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse ytInitialData: {e}") from e

    trends: list[Trend] = []
    rank = 1

    def _walk(node: object) -> None:
        nonlocal rank
        if rank > limit:
            return
        if isinstance(node, dict):
            # videoRenderer contains trending video info
            if "videoRenderer" in node:
                vr = node["videoRenderer"]
                vid_id = vr.get("videoId", "")
                title_runs = vr.get("title", {}).get("runs", [])
                title = "".join(r.get("text", "") for r in title_runs)
                channel_runs = (
                    vr.get("ownerText", {}).get("runs", [])
                    or vr.get("shortBylineText", {}).get("runs", [])
                )
                creator = "".join(r.get("text", "") for r in channel_runs)

                view_text = (
                    vr.get("viewCountText", {}).get("simpleText", "")
                    or vr.get("viewCountText", {}).get("runs", [{}])[0].get("text", "")
                )
                views = _parse_view_count(view_text)

                badges = [
                    b.get("metadataBadgeRenderer", {}).get("label", "")
                    for b in vr.get("badges", [])
                ]
                category = ", ".join(b for b in badges if b)

                if title and vid_id:
                    trends.append(Trend(
                        rank=rank,
                        title=title,
                        platform="youtube",
                        url=f"https://youtu.be/{vid_id}",
                        views=views,
                        creator=creator,
                        category=category or "Trending",
                        hashtags=_extract_hashtags_from_text(title),
                    ))
                    rank += 1
            for v in node.values():
                _walk(v)
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(yt_data)

    return TrendsResult(
        platform="youtube",
        region=region.upper(),
        category="all",
        fetched_at=_now_iso(),
        trends=trends,
    )


# ---------------------------------------------------------------------------
# TikTok trending (web scraping — no official public API)
# ---------------------------------------------------------------------------

TIKTOK_TRENDING_URL = "https://www.tiktok.com/trending"
TIKTOK_CREATIVE_CENTER = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en"


def fetch_tiktok_trending(limit: int = 25, region: str = "US") -> TrendsResult:
    """
    Scrape TikTok's public trending / discover page.

    TikTok's trending data is rendered client-side via React, so this uses
    the hidden __NEXT_DATA__ JSON blob embedded in the page HTML.
    Falls back to TikTok Creative Center hashtag data when the main page
    doesn't yield results.
    """
    trends = _scrape_tiktok_discover(limit, region)
    if not trends:
        trends = _scrape_tiktok_creative_center(limit, region)

    return TrendsResult(
        platform="tiktok",
        region=region.upper(),
        category="viral",
        fetched_at=_now_iso(),
        trends=trends,
    )


def _tiktok_headers(region: str = "US") -> dict:
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.tiktok.com/",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
    }


def _scrape_tiktok_discover(limit: int, region: str) -> list[Trend]:
    """Try the main TikTok discover / search trending endpoint."""
    urls_to_try = [
        "https://www.tiktok.com/discover",
        f"https://www.tiktok.com/tag/trending?region={region}",
    ]
    for url in urls_to_try:
        try:
            req = urllib.request.Request(url, headers=_tiktok_headers(region))
            with urllib.request.urlopen(req, timeout=15) as resp:
                import gzip, io
                raw = resp.read()
                if resp.info().get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
                html = raw.decode("utf-8", errors="replace")

            trends = _parse_tiktok_next_data(html, limit)
            if trends:
                return trends
        except Exception:
            continue
    return []


def _parse_tiktok_next_data(html: str, limit: int) -> list[Trend]:
    """Extract video info from TikTok's __NEXT_DATA__ JSON blob."""
    match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(\{.*?\})</script>', html, re.DOTALL)
    if not match:
        return []
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return []

    trends: list[Trend] = []
    rank = 1

    def _walk(node: object) -> None:
        nonlocal rank
        if rank > limit:
            return
        if isinstance(node, dict):
            # TikTok video item structure
            if "video" in node and "author" in node and "stats" in node:
                author = node.get("author", {})
                stats = node.get("stats", {})
                desc = node.get("desc", "")
                vid_id = node.get("id", "")
                music_info = node.get("music", {})

                hashtags = re.findall(r"#(\w+)", desc)
                creator = author.get("uniqueId") or author.get("nickname", "")

                trends.append(Trend(
                    rank=rank,
                    title=desc[:120] if desc else f"TikTok #{rank}",
                    platform="tiktok",
                    url=f"https://www.tiktok.com/@{creator}/video/{vid_id}" if vid_id else TIKTOK_TRENDING_URL,
                    views=stats.get("playCount", 0),
                    likes=stats.get("diggCount", 0),
                    hashtags=["#" + h for h in hashtags],
                    music=music_info.get("title"),
                    creator=creator,
                ))
                rank += 1
            for v in node.values():
                _walk(v)
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(data)
    return trends


def _scrape_tiktok_creative_center(limit: int, region: str) -> list[Trend]:
    """
    Fetch trending hashtags from TikTok Creative Center public API.
    This endpoint is publicly accessible and used by the TikTok Business ads dashboard.
    """
    api_url = (
        "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list"
        f"?period=7&region_code={region.upper()}&page=1&limit={min(limit, 50)}"
        "&country_code=US&language=en"
    )
    req = urllib.request.Request(
        api_url,
        headers={
            **_tiktok_headers(region),
            "Origin": "https://ads.tiktok.com",
            "Referer": "https://ads.tiktok.com/",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        raise RuntimeError(f"TikTok Creative Center fetch failed: {e}") from e

    trends: list[Trend] = []
    items = (
        data.get("data", {}).get("list", [])
        or data.get("data", {}).get("hashtag_list", [])
        or []
    )
    for rank, item in enumerate(items[:limit], start=1):
        name = item.get("hashtag_name") or item.get("name", "")
        count = item.get("video_views") or item.get("publish_cnt", 0)
        trends.append(Trend(
            rank=rank,
            title=f"#{name}",
            platform="tiktok",
            url=f"https://www.tiktok.com/tag/{name}",
            views=count,
            hashtags=[f"#{name}"],
            category="hashtag",
        ))
    return trends


# ---------------------------------------------------------------------------
# Combined / cross-platform
# ---------------------------------------------------------------------------

def fetch_all_trending(
    youtube_api_key: Optional[str] = None,
    region: str = "US",
    limit: int = 20,
) -> dict:
    """Fetch trending from both YouTube and TikTok, return combined JSON."""
    results: dict = {"youtube": None, "tiktok": None, "errors": {}}

    try:
        if youtube_api_key:
            yt = fetch_youtube_trending(youtube_api_key, region=region, limit=limit)
        else:
            yt = fetch_youtube_trending_no_key(region=region, limit=limit)
        results["youtube"] = yt.to_dict()
    except Exception as e:
        results["errors"]["youtube"] = str(e)

    try:
        tt = fetch_tiktok_trending(limit=limit, region=region)
        results["tiktok"] = tt.to_dict()
    except Exception as e:
        results["errors"]["tiktok"] = str(e)

    return results


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    import datetime
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_view_count(text: str) -> Optional[int]:
    if not text:
        return None
    text = text.lower().replace(",", "").replace(" views", "").strip()
    try:
        if "b" in text:
            return int(float(text.replace("b", "")) * 1_000_000_000)
        if "m" in text:
            return int(float(text.replace("m", "")) * 1_000_000)
        if "k" in text:
            return int(float(text.replace("k", "")) * 1_000)
        return int(text)
    except (ValueError, TypeError):
        return None


def _extract_hashtags_from_text(text: str) -> list[str]:
    return re.findall(r"#\w+", text)
