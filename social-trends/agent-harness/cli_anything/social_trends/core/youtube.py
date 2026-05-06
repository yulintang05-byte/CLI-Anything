"""YouTube trends scraper — trending videos, hashtags, and music."""

import re
import json
import time
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional


_YT_TRENDING_URL = "https://www.youtube.com/feed/trending"
_YT_API_BASE = "https://www.googleapis.com/youtube/v3"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _http_get(url: str, headers: Optional[dict] = None, timeout: int = 15) -> str:
    req_headers = dict(_HEADERS)
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


# ── YouTube Data API v3 (requires API key) ────────────────────────


def fetch_trending_api(
    api_key: str,
    region: str = "US",
    category_id: str = "0",
    max_results: int = 50,
) -> list[dict]:
    """Fetch trending videos via YouTube Data API v3."""
    params = urllib.parse.urlencode({
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region,
        "videoCategoryId": category_id,
        "maxResults": min(max_results, 50),
        "key": api_key,
    })
    url = f"{_YT_API_BASE}/videos?{params}"
    raw = _http_get(url)
    data = json.loads(raw)

    videos = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        title = snippet.get("title", "")
        description = snippet.get("description", "")
        tags = snippet.get("tags", [])
        hashtags = _extract_hashtags(title + " " + description)

        videos.append({
            "id": item.get("id", ""),
            "title": title,
            "channel": snippet.get("channelTitle", ""),
            "published_at": snippet.get("publishedAt", ""),
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
            "tags": tags[:20],
            "hashtags": hashtags,
            "category_id": snippet.get("categoryId", ""),
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "url": f"https://www.youtube.com/watch?v={item.get('id', '')}",
        })
    return videos


def fetch_trending_categories_api(api_key: str, region: str = "US") -> list[dict]:
    """Fetch video category list via YouTube Data API v3."""
    params = urllib.parse.urlencode({
        "part": "snippet",
        "regionCode": region,
        "key": api_key,
    })
    url = f"{_YT_API_BASE}/videoCategories?{params}"
    raw = _http_get(url)
    data = json.loads(raw)
    return [
        {"id": item["id"], "title": item["snippet"]["title"]}
        for item in data.get("items", [])
        if item.get("snippet", {}).get("assignable", False)
    ]


# ── Free scraping fallback (no API key) ──────────────────────────


def fetch_trending_scrape(region: str = "US", max_results: int = 20) -> list[dict]:
    """Scrape YouTube trending page without an API key."""
    url = f"{_YT_TRENDING_URL}?gl={region}"
    try:
        html = _http_get(url)
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch YouTube trending page: {exc}") from exc

    # YouTube inlines initial data as a JS variable
    match = re.search(
        r"var ytInitialData\s*=\s*(\{.+?\});\s*</script>",
        html,
        re.DOTALL,
    )
    if not match:
        raise RuntimeError("Could not parse YouTube trending data (page structure may have changed)")

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"JSON parse error in YouTube data: {exc}") from exc

    videos = _extract_videos_from_yt_data(data, max_results)
    return videos


def _extract_videos_from_yt_data(data: dict, max_results: int) -> list[dict]:
    """Walk ytInitialData structure to extract video entries."""
    videos: list[dict] = []

    def walk(node):
        if len(videos) >= max_results:
            return
        if isinstance(node, dict):
            # videoRenderer is the main video card
            if "videoRenderer" in node:
                vr = node["videoRenderer"]
                vid = _parse_video_renderer(vr)
                if vid:
                    videos.append(vid)
            else:
                for v in node.values():
                    walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return videos[:max_results]


def _parse_video_renderer(vr: dict) -> Optional[dict]:
    vid_id = vr.get("videoId", "")
    if not vid_id:
        return None

    title_runs = vr.get("title", {}).get("runs", [])
    title = "".join(r.get("text", "") for r in title_runs)

    channel_runs = (
        vr.get("longBylineText", {}).get("runs", [])
        or vr.get("shortBylineText", {}).get("runs", [])
    )
    channel = "".join(r.get("text", "") for r in channel_runs)

    view_text = (
        vr.get("viewCountText", {}).get("simpleText", "")
        or vr.get("viewCountText", {}).get("runs", [{}])[0].get("text", "")
    )

    hashtags = _extract_hashtags(title)

    return {
        "id": vid_id,
        "title": title,
        "channel": channel,
        "view_text": view_text,
        "hashtags": hashtags,
        "url": f"https://www.youtube.com/watch?v={vid_id}",
        "thumbnail": f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg",
    }


# ── Hashtag & keyword helpers ─────────────────────────────────────


def _extract_hashtags(text: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"#(\w+)", text)))


def aggregate_trending_hashtags(videos: list[dict], top_n: int = 30) -> list[dict]:
    """Count hashtag frequency across a video list and return ranked results."""
    counts: dict[str, int] = {}
    for v in videos:
        for tag in v.get("hashtags", []) + v.get("tags", []):
            tag_clean = tag.lstrip("#").lower()
            if tag_clean:
                counts[tag_clean] = counts.get(tag_clean, 0) + 1
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [{"hashtag": f"#{t}", "count": c} for t, c in ranked[:top_n]]


def aggregate_top_channels(videos: list[dict], top_n: int = 10) -> list[dict]:
    """Identify channels with most trending videos."""
    counts: dict[str, int] = {}
    for v in videos:
        ch = v.get("channel", "").strip()
        if ch:
            counts[ch] = counts.get(ch, 0) + 1
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [{"channel": ch, "trending_videos": n} for ch, n in ranked[:top_n]]
