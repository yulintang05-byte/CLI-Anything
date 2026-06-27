"""YouTube trend scraper — uses YouTube Data API v3 (requires API key)
and a public trending fallback via yt-trending pages for basic data."""

import json
import re
from typing import Optional
import requests

YT_API_BASE = "https://www.googleapis.com/youtube/v3"

# YouTube Music charts (no auth needed) — public Trending page scrape
YT_TRENDING_URL = "https://www.youtube.com/feed/trending"
YT_MUSIC_TRENDING_URL = "https://www.youtube.com/feed/trending?bp=4gINGgt5dG1hX2NoYXJ0cw%3D%3D"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


# ── API-based (requires key) ─────────────────────────────────────

def fetch_trending_videos(api_key: str, region: str = "US", max_results: int = 25, category_id: str = "0") -> list:
    """Fetch trending videos from YouTube Data API v3."""
    params = {
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": max_results,
        "videoCategoryId": category_id,
        "key": api_key,
    }
    resp = requests.get(f"{YT_API_BASE}/videos", params=params, timeout=15)
    resp.raise_for_status()
    items = resp.json().get("items", [])
    results = []
    for item in items:
        snip = item.get("snippet", {})
        stats = item.get("statistics", {})
        results.append({
            "id": item["id"],
            "title": snip.get("title", ""),
            "channel": snip.get("channelTitle", ""),
            "published_at": snip.get("publishedAt", ""),
            "description": snip.get("description", "")[:200],
            "tags": snip.get("tags", [])[:10],
            "category_id": snip.get("categoryId", ""),
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
            "thumbnail": snip.get("thumbnails", {}).get("high", {}).get("url", ""),
            "url": f"https://www.youtube.com/watch?v={item['id']}",
        })
    return results


def fetch_trending_music(api_key: str, region: str = "US", max_results: int = 25) -> list:
    """Fetch trending music videos (category 10 = Music)."""
    return fetch_trending_videos(api_key, region, max_results, category_id="10")


def search_hashtag(api_key: str, hashtag: str, max_results: int = 20, region: str = "US") -> list:
    """Search YouTube videos by hashtag."""
    tag = hashtag.lstrip("#")
    params = {
        "part": "snippet",
        "q": f"#{tag}",
        "type": "video",
        "order": "viewCount",
        "regionCode": region,
        "maxResults": max_results,
        "key": api_key,
    }
    resp = requests.get(f"{YT_API_BASE}/search", params=params, timeout=15)
    resp.raise_for_status()
    items = resp.json().get("items", [])
    results = []
    for item in items:
        snip = item.get("snippet", {})
        vid_id = item.get("id", {}).get("videoId", "")
        results.append({
            "id": vid_id,
            "title": snip.get("title", ""),
            "channel": snip.get("channelTitle", ""),
            "published_at": snip.get("publishedAt", ""),
            "description": snip.get("description", "")[:200],
            "thumbnail": snip.get("thumbnails", {}).get("high", {}).get("url", ""),
            "url": f"https://www.youtube.com/watch?v={vid_id}" if vid_id else "",
        })
    return [r for r in results if r["id"]]


def get_video_categories(api_key: str, region: str = "US") -> list:
    """List available video categories for a region."""
    params = {
        "part": "snippet",
        "regionCode": region,
        "hl": "en_US",
        "key": api_key,
    }
    resp = requests.get(f"{YT_API_BASE}/videoCategories", params=params, timeout=15)
    resp.raise_for_status()
    return [
        {"id": item["id"], "title": item["snippet"]["title"]}
        for item in resp.json().get("items", [])
        if item["snippet"].get("assignable", False)
    ]


# ── No-auth public scrape ────────────────────────────────────────

def _extract_initial_data(html: str) -> Optional[dict]:
    """Extract ytInitialData JSON from a YouTube HTML page."""
    match = re.search(r"var ytInitialData\s*=\s*(\{.+?\});\s*(?:var |<\/script>)", html, re.DOTALL)
    if not match:
        match = re.search(r"ytInitialData\s*=\s*(\{.+?\});", html, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    return None


def _walk_renderers(obj, depth=0) -> list:
    """Recursively walk ytInitialData to find videoRenderer items."""
    results = []
    if depth > 15:
        return results
    if isinstance(obj, dict):
        if "videoRenderer" in obj:
            r = obj["videoRenderer"]
            vid_id = r.get("videoId", "")
            title = ""
            if "title" in r:
                runs = r["title"].get("runs", [])
                title = "".join(run.get("text", "") for run in runs)
            channel = ""
            if "longBylineText" in r:
                runs = r["longBylineText"].get("runs", [])
                channel = "".join(run.get("text", "") for run in runs)
            elif "ownerText" in r:
                runs = r["ownerText"].get("runs", [])
                channel = "".join(run.get("text", "") for run in runs)
            views = ""
            if "viewCountText" in r:
                views = r["viewCountText"].get("simpleText", "") or "".join(
                    run.get("text", "") for run in r["viewCountText"].get("runs", [])
                )
            results.append({
                "id": vid_id,
                "title": title,
                "channel": channel,
                "views": views,
                "url": f"https://www.youtube.com/watch?v={vid_id}" if vid_id else "",
                "thumbnail": f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg" if vid_id else "",
            })
        else:
            for v in obj.values():
                results.extend(_walk_renderers(v, depth + 1))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(_walk_renderers(item, depth + 1))
    return results


def scrape_trending_no_auth(music_only: bool = False, max_results: int = 25) -> list:
    """Scrape YouTube trending page without API key. Returns partial metadata."""
    url = YT_MUSIC_TRENDING_URL if music_only else YT_TRENDING_URL
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch YouTube trending page: {e}") from e

    data = _extract_initial_data(resp.text)
    if not data:
        return []

    videos = _walk_renderers(data)
    seen = set()
    unique = []
    for v in videos:
        if v["id"] and v["id"] not in seen and v["title"]:
            seen.add(v["id"])
            unique.append(v)
    return unique[:max_results]


def extract_trending_hashtags_from_titles(videos: list) -> list:
    """Extract and count hashtags from video titles and descriptions."""
    from collections import Counter
    counts = Counter()
    for v in videos:
        text = f"{v.get('title', '')} {v.get('description', '')} {' '.join(v.get('tags', []))}"
        tags = re.findall(r"#(\w+)", text)
        counts.update(t.lower() for t in tags)
    return [{"hashtag": f"#{tag}", "count": cnt} for tag, cnt in counts.most_common(30)]
