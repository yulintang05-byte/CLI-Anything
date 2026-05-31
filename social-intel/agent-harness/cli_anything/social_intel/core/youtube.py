"""YouTube Data API v3 — trending videos, hashtags, and music.

Endpoints used:
  videos.list?chart=mostPopular  — regional trending videos
  search.list                    — keyword/hashtag search
  videoCategories.list           — category metadata

Free quota: 10,000 units/day. mostPopular costs 1 unit per call.
"""

import re
from collections import Counter
from typing import Optional

import requests

from cli_anything.social_intel.utils.backend import get_api_key, save_cache

_BASE = "https://www.googleapis.com/youtube/v3"


def _api_key() -> str:
    key = get_api_key("youtube")
    if not key:
        raise RuntimeError(
            "YouTube API key not set. Run: social-intel auth setup "
            "--youtube-api-key YOUR_KEY\n"
            "Get a free key at: https://console.developers.google.com"
        )
    return key


def _get(endpoint: str, params: dict) -> dict:
    params["key"] = _api_key()
    r = requests.get(f"{_BASE}/{endpoint}", params=params, timeout=15)
    r.raise_for_status()
    return r.json()


# ── Trending Videos ──────────────────────────────────────────────

def get_trending_videos(
    region_code: str = "US",
    category_id: str = "0",
    max_results: int = 25,
) -> dict:
    """Fetch the most popular videos for a region.

    Args:
        region_code: ISO 3166-1 alpha-2 (US, GB, AU, …).
        category_id: YouTube category (0=all, 10=music, 17=sports, 20=gaming, 24=entertainment).
        max_results: 1–50.

    Returns:
        Dict with trending_videos list and extracted hashtags/tags.
    """
    data = _get("videos", {
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular",
        "regionCode": region_code,
        "videoCategoryId": category_id,
        "maxResults": max_results,
    })

    videos = []
    all_tags: list[str] = []
    all_hashtags: list[str] = []

    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        tags = snippet.get("tags", [])
        title = snippet.get("title", "")
        description = snippet.get("description", "")

        # Extract hashtags from title + description
        hashtags = re.findall(r"#(\w+)", title + " " + description)

        all_tags.extend([t.lower() for t in tags])
        all_hashtags.extend([h.lower() for h in hashtags])

        videos.append({
            "id": item["id"],
            "title": title,
            "channel": snippet.get("channelTitle", ""),
            "category_id": snippet.get("categoryId", ""),
            "published_at": snippet.get("publishedAt", ""),
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
            "tags": tags[:10],
            "hashtags": hashtags,
            "url": f"https://youtube.com/watch?v={item['id']}",
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
        })

    top_tags = [t for t, _ in Counter(all_tags).most_common(20)]
    top_hashtags = [f"#{h}" for h, _ in Counter(all_hashtags).most_common(20)]

    result = {
        "region": region_code,
        "category_id": category_id,
        "total": len(videos),
        "trending_videos": videos,
        "top_tags": top_tags,
        "top_hashtags": top_hashtags,
    }
    save_cache("youtube_trending", result)
    return result


# ── Trending Music ───────────────────────────────────────────────

def get_trending_music(
    region_code: str = "US",
    max_results: int = 25,
) -> dict:
    """Fetch trending music videos (category 10).

    Returns title, artist, view count, and audio cues for reuse on Shorts/TikTok.
    """
    data = get_trending_videos(region_code=region_code, category_id="10",
                               max_results=max_results)

    music = []
    for v in data["trending_videos"]:
        title = v["title"]
        # Heuristic: parse "Artist - Song" or "Song (Official Video)"
        artist, song = _parse_music_title(title)
        music.append({
            "title": title,
            "artist": artist,
            "song": song,
            "view_count": v["view_count"],
            "url": v["url"],
            "channel": v["channel"],
            "thumbnail": v["thumbnail"],
            "tiktok_safe": _is_likely_tiktok_safe(v),
        })

    result = {
        "region": region_code,
        "total": len(music),
        "trending_music": music,
    }
    save_cache("youtube_music", result)
    return result


def _parse_music_title(title: str) -> tuple[str, str]:
    for sep in [" - ", " – ", " — ", ": "]:
        if sep in title:
            parts = title.split(sep, 1)
            return parts[0].strip(), parts[1].strip()
    return "", title.strip()


def _is_likely_tiktok_safe(video: dict) -> bool:
    """Heuristic: big label artists are usually licensed on TikTok."""
    channel = video.get("channel", "").lower()
    blocklist = ["vevo", "records", "music", "official"]
    # Major label channels tend to be licensed on TikTok
    return any(w in channel for w in blocklist)


# ── Hashtag Search ───────────────────────────────────────────────

def search_hashtag(
    hashtag: str,
    max_results: int = 20,
    order: str = "relevance",
) -> dict:
    """Search videos for a given hashtag and return engagement stats.

    Args:
        hashtag: Hashtag without the # prefix.
        max_results: 1–50.
        order: relevance | date | viewCount | rating.

    Returns:
        Dict with video results and aggregate engagement metrics.
    """
    data = _get("search", {
        "part": "snippet",
        "q": f"#{hashtag}",
        "type": "video",
        "order": order,
        "maxResults": max_results,
    })

    video_ids = [i["id"]["videoId"] for i in data.get("items", [])]
    if not video_ids:
        return {"hashtag": hashtag, "videos": [], "total_views": 0}

    stats_data = _get("videos", {
        "part": "statistics,snippet",
        "id": ",".join(video_ids),
    })

    videos = []
    total_views = 0
    total_likes = 0

    for item in stats_data.get("items", []):
        stats = item.get("statistics", {})
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        total_views += views
        total_likes += likes
        videos.append({
            "id": item["id"],
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "view_count": views,
            "like_count": likes,
            "url": f"https://youtube.com/watch?v={item['id']}",
        })

    avg_views = total_views // len(videos) if videos else 0
    engagement_rate = round(total_likes / total_views * 100, 2) if total_views else 0

    return {
        "hashtag": hashtag,
        "total_videos_sampled": len(videos),
        "total_views": total_views,
        "avg_views": avg_views,
        "total_likes": total_likes,
        "engagement_rate_pct": engagement_rate,
        "competition_level": _competition_level(avg_views),
        "videos": videos,
    }


def _competition_level(avg_views: int) -> str:
    if avg_views > 1_000_000:
        return "very_high"
    if avg_views > 100_000:
        return "high"
    if avg_views > 10_000:
        return "medium"
    return "low"


# ── Category List ────────────────────────────────────────────────

def list_categories(region_code: str = "US") -> dict:
    """Return YouTube video categories for a region."""
    data = _get("videoCategories", {
        "part": "snippet",
        "regionCode": region_code,
        "hl": "en_US",
    })
    categories = [
        {"id": i["id"], "title": i["snippet"]["title"]}
        for i in data.get("items", [])
        if i["snippet"].get("assignable", False)
    ]
    return {"region": region_code, "categories": categories}
