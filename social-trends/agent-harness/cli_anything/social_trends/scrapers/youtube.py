#!/usr/bin/env python3
"""YouTube trending scraper using the Innertube API (no API key required)."""

import json
import time
import requests
from typing import Optional

_INNERTUBE_URL = "https://www.youtube.com/youtubei/v1/browse"
# Key is optional — YouTube accepts keyless requests from browser-like clients
_INNERTUBE_KEY = ""

_CATEGORY_PARAMS = {
    "all": "",
    "music": "4gINGgt5dG1hX2NoYXJ0cw%3D%3D",
    "gaming": "4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D",
    "movies": "4gIKGgh0cmFpbGVycw%3D%3D",
}

_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.youtube.com/",
}


def _innertube_payload(params: str = "") -> dict:
    body = {
        "context": {
            "client": {
                "clientName": "WEB",
                "clientVersion": "2.20240101.01.00",
                "hl": "en",
                "gl": "US",
            }
        },
        "browseId": "FEtrending",
    }
    if params:
        body["params"] = params
    return body


def _parse_video_renderer(renderer: dict) -> Optional[dict]:
    try:
        vid_id = renderer.get("videoId", "")
        title_runs = renderer.get("title", {}).get("runs", [])
        title = title_runs[0].get("text", "") if title_runs else ""
        channel_runs = (
            renderer.get("ownerText", {}).get("runs", [])
            or renderer.get("shortBylineText", {}).get("runs", [])
        )
        channel = channel_runs[0].get("text", "") if channel_runs else ""
        views_text = (
            renderer.get("viewCountText", {}).get("simpleText", "")
            or renderer.get("viewCountText", {}).get("runs", [{}])[0].get("text", "")
        )
        published = renderer.get("publishedTimeText", {}).get("simpleText", "")
        length = renderer.get("lengthText", {}).get("simpleText", "")
        description_snippet = (
            renderer.get("descriptionSnippet", {})
            .get("runs", [{}])[0]
            .get("text", "")
        )
        badges = [
            b.get("metadataBadgeRenderer", {}).get("label", "")
            for b in renderer.get("badges", [])
        ]
        return {
            "video_id": vid_id,
            "url": f"https://www.youtube.com/watch?v={vid_id}",
            "title": title,
            "channel": channel,
            "views": views_text,
            "published": published,
            "length": length,
            "description_snippet": description_snippet,
            "badges": [b for b in badges if b],
        }
    except Exception:
        return None


def _walk_items(data: dict) -> list[dict]:
    """Recursively walk the innertube response to extract video renderers."""
    videos = []
    if isinstance(data, dict):
        if "videoRenderer" in data:
            v = _parse_video_renderer(data["videoRenderer"])
            if v and v["title"]:
                videos.append(v)
        else:
            for v in data.values():
                videos.extend(_walk_items(v))
    elif isinstance(data, list):
        for item in data:
            videos.extend(_walk_items(item))
    return videos


def fetch_trending(category: str = "all", max_results: int = 30) -> dict:
    """
    Fetch YouTube trending videos for the given category.

    Args:
        category: "all", "music", "gaming", or "movies"
        max_results: cap on number of results returned

    Returns:
        dict with keys: platform, category, videos, hashtags, music_tracks, fetched_at
    """
    params = _CATEGORY_PARAMS.get(category, "")
    url = f"{_INNERTUBE_URL}?key={_INNERTUBE_KEY}&prettyPrint=false"
    payload = _innertube_payload(params)

    # Try without key first; fall back to keyed endpoint if needed
    try:
        url_no_key = _INNERTUBE_URL + "?prettyPrint=false"
        resp = requests.post(url_no_key, json=payload, headers=_HEADERS, timeout=15)
        if resp.status_code != 200:
            url_keyed = f"{_INNERTUBE_URL}?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&prettyPrint=false"
            resp = requests.post(url_keyed, json=payload, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        raw = resp.json()
    except requests.RequestException as e:
        return {"error": str(e), "platform": "youtube", "category": category, "videos": [],
                "note": "YouTube scraping may be blocked in your environment. Try from a residential IP."}

    videos = _walk_items(raw)
    # Deduplicate by video_id
    seen = set()
    unique = []
    for v in videos:
        if v["video_id"] not in seen:
            seen.add(v["video_id"])
            unique.append(v)

    unique = unique[:max_results]

    # Extract hashtags from titles/descriptions
    hashtags = _extract_hashtags(unique)
    music_tracks = _extract_music_tracks(unique, category)

    return {
        "platform": "youtube",
        "category": category,
        "total_found": len(unique),
        "videos": unique,
        "hashtags": hashtags,
        "music_tracks": music_tracks,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def _extract_hashtags(videos: list[dict]) -> list[dict]:
    """Pull hashtag-style keywords from video titles and descriptions."""
    import re
    freq: dict[str, int] = {}
    for v in videos:
        text = f"{v['title']} {v['description_snippet']}"
        tags = re.findall(r"#(\w+)", text)
        for t in tags:
            t_lower = t.lower()
            freq[t_lower] = freq.get(t_lower, 0) + 1

    # Also extract trending keywords from titles (capitalized multi-word phrases)
    for v in videos:
        words = v["title"].split()
        for w in words:
            clean = w.strip(".,!?#@()")
            if len(clean) > 4 and clean.isalpha():
                freq[clean.lower()] = freq.get(clean.lower(), 0) + 1

    sorted_tags = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [{"hashtag": f"#{t}", "frequency": c} for t, c in sorted_tags[:30]]


def _extract_music_tracks(videos: list[dict], category: str) -> list[dict]:
    """For music category, interpret video titles as potential music tracks."""
    if category != "music":
        return []
    tracks = []
    for v in videos:
        title = v["title"]
        channel = v["channel"]
        tracks.append({
            "track": title,
            "artist": channel,
            "url": v["url"],
            "views": v["views"],
            "video_id": v["video_id"],
        })
    return tracks[:20]


def fetch_trending_music(max_results: int = 20) -> dict:
    """Convenience wrapper to fetch music-specific trending data."""
    return fetch_trending(category="music", max_results=max_results)
