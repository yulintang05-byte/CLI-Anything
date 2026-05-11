"""YouTube trending scraper.

Fetches trending videos from YouTube's public Trending page and optionally
from the YouTube Data API v3 (when an API key is provided).  No authentication
is needed for the web-scrape path.

Returned dicts are always JSON-serialisable.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any, Dict, List, Optional

from cli_anything.social_trends.utils.scraper import fetch_html, shorten_number

# YouTube Trending page sections mapped to category filter codes
_TRENDING_URLS: Dict[str, str] = {
    "now":       "https://www.youtube.com/feed/trending",
    "music":     "https://www.youtube.com/feed/trending?bp=4gINGgt5dG1hX2NoYXJ0cw%3D%3D",
    "gaming":    "https://www.youtube.com/feed/trending?bp=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D",
    "movies":    "https://www.youtube.com/feed/trending?bp=4gIKGgh0cmFpbGVycw%3D%3D",
}

# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

def _extract_initial_data(html: str) -> Optional[Dict]:
    """Pull ytInitialData JSON from the page source."""
    m = re.search(r'var ytInitialData\s*=\s*(\{.*?\});\s*(?:var |window\.|</script)', html, re.DOTALL)
    if not m:
        m = re.search(r'ytInitialData\s*=\s*(\{.*?\});\s*</script', html, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    return None


def _parse_video_renderer(renderer: Dict) -> Optional[Dict]:
    """Convert a videoRenderer dict into a normalised trend entry."""
    try:
        vid_id = renderer.get("videoId", "")
        title_runs = renderer.get("title", {}).get("runs", [])
        title = "".join(r.get("text", "") for r in title_runs)

        channel_name = (
            renderer.get("longBylineText", {}).get("runs", [{}])[0].get("text", "")
            or renderer.get("shortBylineText", {}).get("runs", [{}])[0].get("text", "")
        )

        view_count_text = (
            renderer.get("viewCountText", {}).get("simpleText", "")
            or renderer.get("viewCountText", {}).get("runs", [{}])[0].get("text", "")
        )
        view_count_raw = re.sub(r"[^0-9]", "", view_count_text)
        view_count = int(view_count_raw) if view_count_raw else 0

        published = (
            renderer.get("publishedTimeText", {}).get("simpleText", "")
        )
        description_snippet = (
            renderer.get("descriptionSnippet", {}).get("runs", [{}])[0].get("text", "")
        )

        badges = [
            b.get("metadataBadgeRenderer", {}).get("label", "")
            for b in renderer.get("badges", [])
        ]

        duration = (
            renderer.get("lengthText", {}).get("simpleText", "")
            or renderer.get("lengthText", {}).get("accessibility", {})
               .get("accessibilityData", {}).get("label", "")
        )

        return {
            "video_id": vid_id,
            "url": f"https://www.youtube.com/watch?v={vid_id}",
            "title": title,
            "channel": channel_name,
            "view_count": view_count,
            "view_count_fmt": shorten_number(view_count) if view_count else view_count_text,
            "published": published,
            "duration": duration,
            "description_snippet": description_snippet[:200],
            "badges": [b for b in badges if b],
        }
    except Exception:
        return None


def _walk_renderers(obj: Any, results: List[Dict], limit: int) -> None:
    """Recursively walk ytInitialData looking for videoRenderer nodes."""
    if len(results) >= limit:
        return
    if isinstance(obj, dict):
        if "videoRenderer" in obj:
            entry = _parse_video_renderer(obj["videoRenderer"])
            if entry and entry["video_id"]:
                results.append(entry)
        else:
            for v in obj.values():
                if len(results) >= limit:
                    return
                _walk_renderers(v, results, limit)
    elif isinstance(obj, list):
        for item in obj:
            if len(results) >= limit:
                return
            _walk_renderers(item, results, limit)


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def fetch_trending(
    category: str = "now",
    limit: int = 25,
    region: str = "US",
) -> Dict[str, Any]:
    """Fetch YouTube trending videos for a category.

    Args:
        category: one of "now" | "music" | "gaming" | "movies"
        limit:    max number of videos to return
        region:   ISO-3166 country code (default US); injected into cookie

    Returns dict with keys: category, region, fetched_at, count, videos
    """
    cat = category.lower()
    if cat not in _TRENDING_URLS:
        valid = list(_TRENDING_URLS.keys())
        raise ValueError(f"Unknown category '{category}'. Valid: {valid}")

    url = _TRENDING_URLS[cat]
    if region and region.upper() != "US":
        url += ("&" if "?" in url else "?") + f"gl={region.upper()}"

    html = fetch_html(url)
    yt_data = _extract_initial_data(html)

    videos: List[Dict] = []
    if yt_data:
        _walk_renderers(yt_data, videos, limit)

    # Fallback: extract video IDs from raw HTML when ytInitialData parse fails
    if not videos:
        ids = re.findall(r'"videoId"\s*:\s*"([A-Za-z0-9_-]{11})"', html)
        titles = re.findall(r'"title"\s*:\s*\{"runs"\s*:\s*\[\{"text"\s*:\s*"([^"]{3,100})"', html)
        for i, vid_id in enumerate(dict.fromkeys(ids)[:limit]):
            videos.append({
                "video_id": vid_id,
                "url": f"https://www.youtube.com/watch?v={vid_id}",
                "title": titles[i] if i < len(titles) else "",
                "channel": "",
                "view_count": 0,
                "view_count_fmt": "",
                "published": "",
                "duration": "",
                "description_snippet": "",
                "badges": [],
            })

    return {
        "platform": "youtube",
        "category": cat,
        "region": region.upper(),
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "count": len(videos),
        "videos": videos[:limit],
    }


def fetch_trending_all_categories(limit_per_cat: int = 10, region: str = "US") -> Dict[str, Any]:
    """Fetch trending across all YouTube categories."""
    all_results: Dict[str, List] = {}
    errors: Dict[str, str] = {}

    for cat in _TRENDING_URLS:
        try:
            result = fetch_trending(cat, limit=limit_per_cat, region=region)
            all_results[cat] = result["videos"]
        except Exception as e:
            errors[cat] = str(e)
        time.sleep(0.5)

    return {
        "platform": "youtube",
        "region": region.upper(),
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "categories": all_results,
        "errors": errors,
    }


def extract_hashtags_from_videos(videos: List[Dict]) -> List[Dict[str, Any]]:
    """Mine hashtag mentions from video titles and descriptions."""
    counts: Dict[str, int] = {}
    for v in videos:
        text = (v.get("title", "") + " " + v.get("description_snippet", "")).lower()
        for tag in re.findall(r'#(\w+)', text):
            counts[tag] = counts.get(tag, 0) + 1

    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [{"hashtag": f"#{tag}", "mentions": n} for tag, n in ranked]


def extract_music_from_videos(videos: List[Dict]) -> List[Dict[str, Any]]:
    """Heuristically identify music tracks referenced in YouTube video metadata."""
    music_entries: List[Dict] = []
    seen: set = set()

    music_patterns = [
        r'(?:song|music|audio|beat|track|prod\.?|ft\.?|feat\.?)[:\s]+([^\|\n\[\]]{5,60})',
        r'\(([^()]{5,60})\)',
        r'\[([^\[\]]{5,60})\]',
    ]

    for v in videos:
        text = v.get("title", "") + " " + v.get("description_snippet", "")
        for pat in music_patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                track = m.group(1).strip()
                if track and track.lower() not in seen and len(track) > 4:
                    seen.add(track.lower())
                    music_entries.append({
                        "track": track,
                        "source_video": v.get("video_id", ""),
                        "source_title": v.get("title", ""),
                        "channel": v.get("channel", ""),
                    })

    return music_entries[:50]
