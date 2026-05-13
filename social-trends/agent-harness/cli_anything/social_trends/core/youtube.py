"""YouTube trend scraper — Data API v3 + web fallback."""

import re
import json
import requests
from datetime import datetime, timezone
from typing import Optional

_API_BASE = "https://www.googleapis.com/youtube/v3"

_CATEGORY_IDS = {
    "all": "0",
    "film": "1",
    "autos": "2",
    "music": "10",
    "pets": "15",
    "sports": "17",
    "gaming": "20",
    "people": "22",
    "comedy": "23",
    "entertainment": "24",
    "news": "25",
    "howto": "26",
    "education": "27",
    "science": "28",
}

_BEST_TIMES = {
    "monday": ["12:00", "15:00", "20:00"],
    "tuesday": ["12:00", "14:00", "20:00"],
    "wednesday": ["12:00", "15:00", "21:00"],
    "thursday": ["12:00", "15:00", "20:00"],
    "friday": ["12:00", "15:00", "17:00"],
    "saturday": ["10:00", "13:00", "20:00"],
    "sunday": ["10:00", "13:00", "17:00"],
}


def fetch_trending(
    api_key: str,
    region: str = "US",
    max_results: int = 50,
    category: str = "all",
) -> dict:
    """Fetch trending YouTube videos via Data API v3."""
    if not api_key:
        raise ValueError(
            "YouTube API key required. Get one free at: "
            "https://console.cloud.google.com/apis/library/youtube.googleapis.com"
        )

    category_id = _CATEGORY_IDS.get(category.lower(), "0")
    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "maxResults": min(max_results, 50),
        "regionCode": region.upper(),
        "key": api_key,
    }
    if category_id != "0":
        params["videoCategoryId"] = category_id

    resp = requests.get(f"{_API_BASE}/videos", params=params, timeout=12)

    if resp.status_code == 403:
        raise PermissionError(
            "YouTube API key invalid or quota exceeded. "
            "Check quota at: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas"
        )
    resp.raise_for_status()

    items = resp.json().get("items", [])
    videos = [_parse_video(item) for item in items]
    videos.sort(key=lambda v: v["views"], reverse=True)

    return {
        "platform": "youtube",
        "region": region.upper(),
        "category": category,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "video_count": len(videos),
        "videos": videos,
        "trending_hashtags": _aggregate_hashtags(videos),
        "trending_music": extract_music(videos),
        "top_channels": _top_channels(videos),
    }


def _parse_video(item: dict) -> dict:
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    desc = snippet.get("description", "")
    title = snippet.get("title", "")
    tags = snippet.get("tags", [])

    hashtags = list(set(
        [h.lower() for h in re.findall(r"#(\w+)", desc + " " + title)]
        + [t.replace(" ", "").lower() for t in tags[:15]]
    ))

    return {
        "id": item.get("id", ""),
        "title": title,
        "channel": snippet.get("channelTitle", ""),
        "channel_id": snippet.get("channelId", ""),
        "published_at": snippet.get("publishedAt", ""),
        "views": int(stats.get("viewCount", 0)),
        "likes": int(stats.get("likeCount", 0)),
        "comments": int(stats.get("commentCount", 0)),
        "hashtags": hashtags[:25],
        "thumbnail": (snippet.get("thumbnails", {}).get("high", {}) or {}).get("url", ""),
        "description_preview": desc[:300],
        "url": f"https://youtube.com/watch?v={item.get('id', '')}",
    }


def _aggregate_hashtags(videos: list) -> list:
    totals: dict = {}
    for v in videos:
        for h in v["hashtags"]:
            if h not in totals:
                totals[h] = {"hashtag": h, "video_count": 0, "total_views": 0}
            totals[h]["video_count"] += 1
            totals[h]["total_views"] += v["views"]
    return sorted(totals.values(), key=lambda x: x["total_views"], reverse=True)[:30]


def extract_music(videos: list) -> list:
    """Extract trending music/audio mentions from video descriptions."""
    patterns = [
        r"(?:song|music|audio|soundtrack|beat|track|ft\.|feat\.)[:\s]+([^\n#|]{4,60})",
        r"[🎵🎶♪]\s*([^\n#|]{4,60})",
        r"Music[:\s]+([^\n#|]{4,60})",
    ]
    found: dict = {}
    for v in videos:
        text = v.get("description_preview", "") + " " + v.get("title", "")
        for pat in patterns:
            for m in re.findall(pat, text, re.IGNORECASE):
                cleaned = m.strip().strip("()-[]\"'")[:60]
                if 4 <= len(cleaned) <= 60:
                    key = cleaned.lower()
                    if key not in found:
                        found[key] = {"title": cleaned, "mention_count": 0, "total_views": 0}
                    found[key]["mention_count"] += 1
                    found[key]["total_views"] += v.get("views", 0)
    return sorted(found.values(), key=lambda x: x["total_views"], reverse=True)[:20]


def _top_channels(videos: list) -> list:
    channels: dict = {}
    for v in videos:
        cid = v["channel_id"]
        if cid not in channels:
            channels[cid] = {
                "channel": v["channel"],
                "channel_id": cid,
                "trending_video_count": 0,
                "total_views": 0,
                "url": f"https://youtube.com/channel/{cid}",
            }
        channels[cid]["trending_video_count"] += 1
        channels[cid]["total_views"] += v["views"]
    return sorted(channels.values(), key=lambda x: x["total_views"], reverse=True)[:10]


def get_channel_info(api_key: str, channel_id: str) -> dict:
    """Fetch channel statistics for optimization analysis."""
    params = {
        "part": "snippet,statistics,brandingSettings",
        "id": channel_id,
        "key": api_key,
    }
    resp = requests.get(f"{_API_BASE}/channels", params=params, timeout=12)
    resp.raise_for_status()
    items = resp.json().get("items", [])
    if not items:
        raise ValueError(f"Channel not found: {channel_id}")

    item = items[0]
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    branding = item.get("brandingSettings", {}).get("channel", {})

    subscribers = int(stats.get("subscriberCount", 0))
    video_count = int(stats.get("videoCount", 0))
    views = int(stats.get("viewCount", 0))

    score, issues = _score_channel(snippet, branding, subscribers, video_count, views)

    return {
        "channel_id": channel_id,
        "name": snippet.get("title", ""),
        "description": snippet.get("description", "")[:500],
        "subscribers": subscribers,
        "video_count": video_count,
        "total_views": views,
        "avg_views_per_video": views // max(video_count, 1),
        "country": snippet.get("country", "Unknown"),
        "created_at": snippet.get("publishedAt", ""),
        "keywords": branding.get("keywords", ""),
        "optimization_score": score,
        "issues": issues,
        "recommendations": _channel_recommendations(issues, subscribers),
        "best_posting_times": _BEST_TIMES,
    }


def _score_channel(snippet: dict, branding: dict, subscribers: int, video_count: int, views: int) -> tuple:
    score = 100
    issues = []

    desc = snippet.get("description", "")
    if len(desc) < 100:
        score -= 15
        issues.append({
            "severity": "high",
            "issue": "Channel description too short",
            "fix": "Write a 200-500 word description with keywords describing your niche",
        })

    if not branding.get("keywords"):
        score -= 10
        issues.append({
            "severity": "high",
            "issue": "No channel keywords set",
            "fix": "Add 10-15 relevant keywords in YouTube Studio > Customization > Basic Info",
        })

    if not snippet.get("country"):
        score -= 5
        issues.append({
            "severity": "medium",
            "issue": "Country not set",
            "fix": "Set your country to improve local trend matching",
        })

    if video_count > 0:
        avg_views = views // video_count
        if subscribers > 0 and avg_views < (subscribers * 0.05):
            score -= 20
            issues.append({
                "severity": "high",
                "issue": "Low view-to-subscriber ratio (<5%)",
                "fix": "Improve thumbnails, titles, and post during peak hours (12-3pm, 8-10pm)",
            })

    return max(score, 0), issues


def _channel_recommendations(issues: list, subscribers: int) -> list:
    recs = [
        {
            "priority": 1,
            "action": "Use trending hashtags in every video description",
            "impact": "Increases discoverability by 30-40%",
        },
        {
            "priority": 2,
            "action": "Post 3-5 times per week consistently",
            "impact": "Algorithm rewards consistent upload schedules",
        },
        {
            "priority": 3,
            "action": "First 30 seconds must hook viewer — ask a question or tease the payoff",
            "impact": "Improves average view duration, the #1 ranking factor",
        },
        {
            "priority": 4,
            "action": "Create Shorts versions of top videos",
            "impact": "Shorts feed drives 2-5x subscriber growth",
        },
        {
            "priority": 5,
            "action": "Add chapters/timestamps to all videos",
            "impact": "Improves watch time and search result snippet quality",
        },
    ]

    if subscribers < 1000:
        recs.insert(0, {
            "priority": 0,
            "action": "Focus on ONE niche — post 10 videos in 2 weeks to build library",
            "impact": "Essential for algorithm to understand and recommend your channel",
        })

    return recs


def list_categories() -> list:
    return [{"id": v, "name": k} for k, v in _CATEGORY_IDS.items()]


def get_best_posting_times() -> dict:
    return {
        "platform": "youtube",
        "timezone_note": "Times in creator's local timezone (EST/PST most relevant for US)",
        "schedule": _BEST_TIMES,
        "peak_days": ["Thursday", "Friday", "Saturday"],
        "notes": [
            "Thursday and Friday uploads get weekend algorithm boost",
            "12-3pm captures lunch break viewers",
            "8-10pm captures prime time viewers",
            "Shorts can be posted daily — algorithm is separate from long-form",
        ],
    }
