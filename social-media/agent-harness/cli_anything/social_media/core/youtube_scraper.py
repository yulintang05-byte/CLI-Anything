"""YouTube trend scraper — parses ytInitialData embedded in trending pages.

No API key required. Uses publicly accessible YouTube trending pages.
"""

import json
import re
import time
from typing import Optional

try:
    import requests
    from bs4 import BeautifulSoup
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

from . import cache as _cache

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

_CATEGORY_MAP = {
    "now": "0",
    "music": "10",
    "gaming": "20",
    "movies": "30",
}


def _fetch_trending_page(region: str = "US", category: str = "now") -> Optional[dict]:
    """Fetch and parse YouTube trending page, return ytInitialData dict."""
    if not _REQUESTS_OK:
        raise RuntimeError("requests and beautifulsoup4 required: pip install requests beautifulsoup4")

    cat_id = _CATEGORY_MAP.get(category.lower(), "0")
    url = f"https://www.youtube.com/feed/trending?bp=4gINGgt{cat_id}&gl={region}&hl=en"

    try:
        resp = requests.get(url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"Failed to fetch YouTube trending: {e}") from e

    # ytInitialData is embedded as a JS variable in the page
    match = re.search(r"var ytInitialData\s*=\s*(\{.+?\});\s*</script>", resp.text, re.DOTALL)
    if not match:
        # Alternate pattern
        match = re.search(r"ytInitialData\s*=\s*(\{.+?\});\s*(?:var|let|const|</script>)", resp.text, re.DOTALL)
    if not match:
        raise RuntimeError("Could not extract ytInitialData from YouTube page — page structure may have changed")

    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse ytInitialData JSON: {e}") from e


def _extract_text(obj) -> str:
    """Recursively extract text from YouTube's nested {runs: [{text}]} format."""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        if "simpleText" in obj:
            return obj["simpleText"]
        if "runs" in obj:
            return "".join(r.get("text", "") for r in obj["runs"])
    return ""


def _parse_video_renderer(renderer: dict) -> Optional[dict]:
    """Extract structured data from a videoRenderer dict."""
    try:
        video_id = renderer.get("videoId", "")
        title = _extract_text(renderer.get("title", {}))
        channel = _extract_text(renderer.get("longBylineText") or renderer.get("shortBylineText") or {})
        views_raw = _extract_text(renderer.get("viewCountText") or renderer.get("shortViewCountText") or {})
        duration = _extract_text(renderer.get("lengthText") or {})
        published = _extract_text(renderer.get("publishedTimeText") or {})
        description = _extract_text(renderer.get("descriptionSnippet") or {})

        # Extract hashtags from title/description
        hashtags = list({tag.lower() for tag in re.findall(r"#(\w+)", title + " " + description)})

        thumbnail_url = ""
        thumbs = renderer.get("thumbnail", {}).get("thumbnails", [])
        if thumbs:
            thumbnail_url = thumbs[-1].get("url", "")

        return {
            "platform": "youtube",
            "id": video_id,
            "title": title,
            "channel": channel,
            "views_raw": views_raw,
            "duration": duration,
            "published": published,
            "description_snippet": description[:200],
            "hashtags": hashtags,
            "thumbnail_url": thumbnail_url,
            "url": f"https://www.youtube.com/watch?v={video_id}" if video_id else "",
        }
    except Exception:
        return None


def _walk_renderers(obj, results: list, limit: int) -> None:
    """Recursively walk ytInitialData looking for videoRenderer nodes."""
    if len(results) >= limit:
        return
    if isinstance(obj, dict):
        if "videoRenderer" in obj:
            parsed = _parse_video_renderer(obj["videoRenderer"])
            if parsed and parsed["title"]:
                results.append(parsed)
            return
        for v in obj.values():
            _walk_renderers(v, results, limit)
            if len(results) >= limit:
                return
    elif isinstance(obj, list):
        for item in obj:
            _walk_renderers(item, results, limit)
            if len(results) >= limit:
                return


def get_trending(region: str = "US", limit: int = 20, category: str = "now",
                 use_cache: bool = True) -> dict:
    """Fetch trending YouTube videos.

    Args:
        region: ISO country code (US, GB, IN, etc.)
        limit: Max number of results
        category: now | music | gaming | movies
        use_cache: Use cached results if fresh

    Returns:
        dict with keys: videos, region, category, scraped_at, count
    """
    cache_key = f"yt_trending_{region}_{category}"
    if use_cache:
        cached = _cache.get(cache_key)
        if cached:
            cached["from_cache"] = True
            return cached

    data = _fetch_trending_page(region, category)
    videos = []
    _walk_renderers(data, videos, limit)

    result = {
        "platform": "youtube",
        "region": region,
        "category": category,
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "count": len(videos),
        "videos": videos[:limit],
        "from_cache": False,
    }
    _cache.set(cache_key, result)
    return result


def get_trending_music(region: str = "US", limit: int = 20, use_cache: bool = True) -> dict:
    """Fetch YouTube trending music. Convenience wrapper around get_trending."""
    return get_trending(region=region, limit=limit, category="music", use_cache=use_cache)


def get_all_hashtags(region: str = "US", limit_per_category: int = 20) -> dict:
    """Aggregate all hashtags appearing across YouTube trending categories."""
    hashtag_freq: dict[str, int] = {}
    videos_seen = []

    for cat in ("now", "music"):
        try:
            result = get_trending(region=region, limit=limit_per_category, category=cat)
            for v in result.get("videos", []):
                videos_seen.append(v)
                for tag in v.get("hashtags", []):
                    hashtag_freq[tag] = hashtag_freq.get(tag, 0) + 1
        except Exception:
            pass

    sorted_tags = sorted(hashtag_freq.items(), key=lambda x: x[1], reverse=True)
    return {
        "platform": "youtube",
        "region": region,
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "hashtags": [{"tag": f"#{t}", "frequency": f} for t, f in sorted_tags],
        "total_videos_analyzed": len(videos_seen),
    }
