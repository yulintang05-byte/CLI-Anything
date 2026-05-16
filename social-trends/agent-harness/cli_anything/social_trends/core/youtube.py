"""YouTube trends fetcher via YouTube Data API v3 and RSS fallback."""

import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from typing import Optional

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

CATEGORY_IDS = {
    "all":       "0",
    "music":     "10",
    "gaming":    "20",
    "news":      "25",
    "entertainment": "24",
    "sports":    "17",
    "tech":      "28",
    "film":      "1",
    "comedy":    "23",
    "education": "27",
    "fashion":   "26",
    "howto":     "26",
}


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "CLI-Anything/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def fetch_trending(
    api_key: str,
    region: str = "US",
    category: str = "all",
    max_results: int = 20,
) -> list[dict]:
    """Return trending YouTube videos with engagement stats."""
    cat_id = CATEGORY_IDS.get(category.lower(), "0")
    params = urllib.parse.urlencode({
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region.upper(),
        "videoCategoryId": cat_id,
        "maxResults": min(max_results, 50),
        "key": api_key,
    })
    data = _get(f"{YOUTUBE_API_BASE}/videos?{params}")
    results = []
    for item in data.get("items", []):
        snip = item.get("snippet", {})
        stats = item.get("statistics", {})
        tags = snip.get("tags", [])
        results.append({
            "id": item["id"],
            "title": snip.get("title", ""),
            "channel": snip.get("channelTitle", ""),
            "published_at": snip.get("publishedAt", ""),
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "engagement_rate": _engagement(stats),
            "tags": tags[:10],
            "top_hashtags": _extract_hashtags(snip.get("description", ""), tags),
            "url": f"https://youtube.com/watch?v={item['id']}",
        })
    return results


def fetch_trending_hashtags(
    api_key: str,
    region: str = "US",
    category: str = "all",
    max_results: int = 20,
    top_n: int = 30,
) -> list[dict]:
    """Return ranked hashtags extracted from trending videos."""
    videos = fetch_trending(api_key, region, category, max_results)
    counts: dict[str, int] = {}
    for v in videos:
        for tag in v["top_hashtags"]:
            t = tag.lower().lstrip("#")
            counts[t] = counts.get(t, 0) + 1
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return [{"hashtag": f"#{h}", "frequency": f} for h, f in ranked]


def fetch_trending_music(api_key: str, region: str = "US", max_results: int = 20) -> list[dict]:
    """Return trending music videos from the Music category."""
    return fetch_trending(api_key, region, "music", max_results)


def fetch_channel_audit(api_key: str, channel_id: str) -> dict:
    """Fetch channel stats for optimization auditing."""
    params = urllib.parse.urlencode({
        "part": "snippet,statistics,brandingSettings",
        "id": channel_id,
        "key": api_key,
    })
    data = _get(f"{YOUTUBE_API_BASE}/channels?{params}")
    items = data.get("items", [])
    if not items:
        raise ValueError(f"Channel not found: {channel_id}")
    item = items[0]
    snip = item.get("snippet", {})
    stats = item.get("statistics", {})
    branding = item.get("brandingSettings", {}).get("channel", {})
    subs = int(stats.get("subscriberCount", 0))
    videos_count = int(stats.get("videoCount", 0))
    views = int(stats.get("viewCount", 0))
    return {
        "channel_id": channel_id,
        "title": snip.get("title", ""),
        "description": snip.get("description", "")[:200],
        "created_at": snip.get("publishedAt", ""),
        "country": snip.get("country", ""),
        "subscribers": subs,
        "total_views": views,
        "video_count": videos_count,
        "avg_views_per_video": views // max(videos_count, 1),
        "keywords": branding.get("keywords", ""),
        "optimization_score": _channel_score(snip, stats, branding),
        "recommendations": _channel_recommendations(snip, stats, branding),
    }


def _engagement(stats: dict) -> float:
    views = int(stats.get("viewCount", 1)) or 1
    likes = int(stats.get("likeCount", 0))
    comments = int(stats.get("commentCount", 0))
    return round((likes + comments) / views * 100, 2)


def _extract_hashtags(description: str, tags: list[str]) -> list[str]:
    hashtags = [w for w in description.split() if w.startswith("#")]
    tag_hashtags = [f"#{t.replace(' ', '')}" for t in tags]
    seen = set()
    combined = []
    for h in hashtags + tag_hashtags:
        key = h.lower()
        if key not in seen:
            seen.add(key)
            combined.append(h)
    return combined[:15]


def _channel_score(snip: dict, stats: dict, branding: dict) -> int:
    score = 0
    if snip.get("description", ""):
        score += 20
    if len(snip.get("description", "")) > 100:
        score += 10
    if snip.get("customUrl"):
        score += 15
    if branding.get("keywords"):
        score += 15
    if snip.get("country"):
        score += 10
    subs = int(stats.get("subscriberCount", 0))
    if subs > 1000:
        score += 10
    if subs > 10000:
        score += 10
    if subs > 100000:
        score += 10
    return min(score, 100)


def _channel_recommendations(snip: dict, stats: dict, branding: dict) -> list[str]:
    recs = []
    if not snip.get("description"):
        recs.append("Add a channel description with keywords")
    elif len(snip.get("description", "")) < 100:
        recs.append("Expand channel description (aim for 200+ characters with keywords)")
    if not branding.get("keywords"):
        recs.append("Add channel keywords in Studio > Customization > Basic info")
    if not snip.get("country"):
        recs.append("Set your country/region for better local search ranking")
    if not snip.get("customUrl"):
        recs.append("Claim a custom URL (requires 100+ subscribers)")
    subs = int(stats.get("subscriberCount", 0))
    if subs < 1000:
        recs.append("Focus on consistent posting (1-2x/week) to reach 1K subscriber threshold")
    return recs
