"""YouTube trending video scraper.

Uses the YouTube Data API v3 when YOUTUBE_API_KEY is set, otherwise
falls back to yt-dlp which parses the public YouTube trending page.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Any

# googleapiclient is imported lazily inside _fetch_via_api to avoid
# Rust/cffi crashes in environments where the cryptography wheel is broken.


# YouTube category ID → friendly name mapping
_CATEGORY_MAP: dict[str, str] = {
    "0":  "all",
    "1":  "film_animation",
    "2":  "autos_vehicles",
    "10": "music",
    "15": "pets_animals",
    "17": "sports",
    "19": "travel_events",
    "20": "gaming",
    "22": "people_blogs",
    "23": "comedy",
    "24": "entertainment",
    "25": "news_politics",
    "26": "howto_style",
    "27": "education",
    "28": "science_technology",
    "29": "nonprofits_activism",
}
_CATEGORY_NAME_TO_ID = {v: k for k, v in _CATEGORY_MAP.items()}


@dataclass
class YouTubeVideo:
    video_id: str
    title: str
    channel: str
    view_count: int
    like_count: int
    comment_count: int
    tags: list[str]
    description_snippet: str
    published_at: str
    duration: str
    category: str
    thumbnail_url: str
    url: str = field(init=False)

    def __post_init__(self):
        self.url = f"https://www.youtube.com/watch?v={self.video_id}"

    def to_dict(self) -> dict:
        return {
            "video_id": self.video_id,
            "title": self.title,
            "channel": self.channel,
            "url": self.url,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "comment_count": self.comment_count,
            "tags": self.tags,
            "description_snippet": self.description_snippet,
            "published_at": self.published_at,
            "duration": self.duration,
            "category": self.category,
            "thumbnail_url": self.thumbnail_url,
        }

    @property
    def engagement_rate(self) -> float:
        if self.view_count == 0:
            return 0.0
        return round((self.like_count + self.comment_count) / self.view_count * 100, 3)


def _category_id(category: str) -> str:
    """Convert friendly category name to YouTube API category ID."""
    category = category.lower().replace(" ", "_")
    if category in _CATEGORY_NAME_TO_ID:
        return _CATEGORY_NAME_TO_ID[category]
    if category in _CATEGORY_MAP:
        return category
    return "0"


def _duration_seconds(iso: str) -> int:
    """Parse ISO 8601 duration string (PT4M13S) into total seconds."""
    import re
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    if not match:
        return 0
    h, m, s = (int(x or 0) for x in match.groups())
    return h * 3600 + m * 60 + s


def _format_duration(iso: str) -> str:
    total = _duration_seconds(iso)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


# ── API path ──────────────────────────────────────────────────────────────────

def _fetch_via_api(
    api_key: str,
    region: str,
    category: str,
    max_results: int,
) -> list[YouTubeVideo]:
    try:
        from googleapiclient.discovery import build as yt_build
    except Exception as exc:
        raise RuntimeError(
            "google-api-python-client unavailable in this environment. "
            "Falling back to yt-dlp. Error: " + str(exc)
        ) from exc

    youtube = yt_build("youtube", "v3", developerKey=api_key)
    cat_id = _category_id(category)

    response = (
        youtube.videos()
        .list(
            part="snippet,statistics,contentDetails",
            chart="mostPopular",
            regionCode=region.upper(),
            videoCategoryId=cat_id if cat_id != "0" else "",
            maxResults=min(max_results, 50),
        )
        .execute()
    )

    videos: list[YouTubeVideo] = []
    for item in response.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        details = item.get("contentDetails", {})
        video_id = item["id"]
        desc = snippet.get("description", "")
        desc_snippet = desc[:200] + "..." if len(desc) > 200 else desc

        cat_name = _CATEGORY_MAP.get(snippet.get("categoryId", "0"), "unknown")
        thumbnails = snippet.get("thumbnails", {})
        thumb = (
            thumbnails.get("maxres", {}).get("url")
            or thumbnails.get("high", {}).get("url")
            or ""
        )

        videos.append(
            YouTubeVideo(
                video_id=video_id,
                title=snippet.get("title", ""),
                channel=snippet.get("channelTitle", ""),
                view_count=int(stats.get("viewCount", 0)),
                like_count=int(stats.get("likeCount", 0)),
                comment_count=int(stats.get("commentCount", 0)),
                tags=snippet.get("tags", []),
                description_snippet=desc_snippet,
                published_at=snippet.get("publishedAt", ""),
                duration=_format_duration(details.get("duration", "PT0S")),
                category=cat_name,
                thumbnail_url=thumb,
            )
        )
    return videos


# ── yt-dlp fallback ───────────────────────────────────────────────────────────

def _fetch_via_ytdlp(region: str, category: str, max_results: int) -> list[YouTubeVideo]:
    """Scrape YouTube trending page using yt-dlp (no API key needed)."""
    cat_id = _category_id(category)
    url = f"https://www.youtube.com/feed/trending?gl={region.upper()}&bp={cat_id}"

    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--flat-playlist",
        "--dump-single-json",
        "--playlist-end", str(max_results),
        "--no-warnings",
        "--quiet",
        url,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

    if result.returncode != 0:
        # Try with yt-dlp directly
        cmd[0] = "yt-dlp"
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

    if result.returncode != 0:
        raise RuntimeError(
            f"yt-dlp failed: {result.stderr[:300]}\n"
            "Ensure yt-dlp is installed: pip install yt-dlp"
        )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse yt-dlp output: {exc}") from exc

    entries = data.get("entries", [])
    videos: list[YouTubeVideo] = []
    for entry in entries[:max_results]:
        vid_id = entry.get("id", "")
        views = entry.get("view_count") or 0
        likes = entry.get("like_count") or 0
        comments = entry.get("comment_count") or 0
        thumbnails = entry.get("thumbnails") or []
        thumb = thumbnails[-1]["url"] if thumbnails else ""

        videos.append(
            YouTubeVideo(
                video_id=vid_id,
                title=entry.get("title", ""),
                channel=entry.get("uploader", entry.get("channel", "")),
                view_count=int(views),
                like_count=int(likes),
                comment_count=int(comments),
                tags=entry.get("tags") or [],
                description_snippet=(entry.get("description") or "")[:200],
                published_at=str(entry.get("upload_date", "")),
                duration=str(entry.get("duration_string", entry.get("duration", ""))),
                category=category,
                thumbnail_url=thumb,
            )
        )
    return videos


# ── Public interface ──────────────────────────────────────────────────────────

def fetch_trending(
    region: str = "US",
    category: str = "all",
    max_results: int = 25,
    api_key: str | None = None,
) -> list[YouTubeVideo]:
    """Return a list of trending YouTube videos.

    Args:
        region: ISO 3166-1 alpha-2 country code (US, GB, IN, …).
        category: Content category slug (all, music, gaming, sports, …).
        max_results: How many videos to return (max 50 via API, 50 via yt-dlp).
        api_key: YouTube Data API v3 key. Falls back to YOUTUBE_API_KEY env var,
                 then yt-dlp if neither is set.
    """
    key = api_key or os.environ.get("YOUTUBE_API_KEY")
    if key:
        try:
            return _fetch_via_api(key, region, category, max_results)
        except RuntimeError:
            pass  # fall through to yt-dlp
    return _fetch_via_ytdlp(region, category, max_results)


def extract_top_tags(videos: list[YouTubeVideo], top_n: int = 20) -> list[tuple[str, int]]:
    """Count and rank tags across all fetched videos."""
    from collections import Counter
    counter: Counter[str] = Counter()
    for v in videos:
        for tag in v.tags:
            counter[tag.lower().strip()] += 1
    return counter.most_common(top_n)


def list_categories() -> list[str]:
    """Return all supported category slugs."""
    return sorted(_CATEGORY_MAP.values())
