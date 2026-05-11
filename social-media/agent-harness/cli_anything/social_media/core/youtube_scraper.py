"""YouTube viral trends, hashtags, and music scraper.

Uses yt-dlp for metadata extraction (no API key needed) and the optional
YouTube Data API v3 for trending/popular content.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class YouTubeTrend:
    title: str
    video_id: str
    channel: str
    view_count: int
    like_count: int
    comment_count: int
    upload_date: str
    duration: int          # seconds
    hashtags: list[str]
    music_track: str       # detected background music if any
    description_snippet: str
    thumbnail_url: str
    tags: list[str]
    category: str
    engagement_rate: float  # (likes + comments) / views * 100

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TrendingMusic:
    title: str
    artist: str
    video_ids: list[str]   # videos using this music
    use_count: int
    avg_views: int
    trend_score: float     # composite score


@dataclass
class YouTubeTrendsResult:
    scraped_at: str
    region: str
    category: str
    trends: list[YouTubeTrend]
    top_hashtags: list[dict]     # [{tag, count, avg_views}]
    trending_music: list[TrendingMusic]
    viral_patterns: list[str]    # observed content patterns

    def to_dict(self) -> dict:
        return {
            "scraped_at": self.scraped_at,
            "region": self.region,
            "category": self.category,
            "trends": [t.to_dict() for t in self.trends],
            "top_hashtags": self.top_hashtags,
            "trending_music": [asdict(m) for m in self.trending_music],
            "viral_patterns": self.viral_patterns,
        }


# ── Hashtag extraction ────────────────────────────────────────────────

def extract_hashtags(text: str) -> list[str]:
    """Extract #hashtags from title, description, or tags."""
    return [tag.lower() for tag in re.findall(r"#(\w+)", text)]


def _compute_engagement(views: int, likes: int, comments: int) -> float:
    if views == 0:
        return 0.0
    return round((likes + comments) / views * 100, 4)


# ── yt-dlp backend ────────────────────────────────────────────────────

def _ytdlp_available() -> bool:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--version"],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def _fetch_video_info(url: str) -> Optional[dict]:
    """Fetch metadata for a single video using yt-dlp."""
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "yt_dlp",
                "--dump-json",
                "--no-playlist",
                "--skip-download",
                "--quiet",
                url,
            ],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            return None
        return json.loads(result.stdout.strip())
    except Exception:
        return None


def _fetch_playlist_info(url: str, max_items: int = 25) -> list[dict]:
    """Fetch metadata for a playlist (e.g., YouTube trending page)."""
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "yt_dlp",
                "--dump-json",
                "--flat-playlist",
                "--playlist-end", str(max_items),
                "--quiet",
                url,
            ],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            return []
        lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
        items = []
        for line in lines:
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return items
    except Exception:
        return []


def _parse_video_to_trend(info: dict) -> YouTubeTrend:
    """Convert yt-dlp video info dict to a YouTubeTrend."""
    vid_id = info.get("id", "")
    title = info.get("title", "")
    channel = info.get("uploader", info.get("channel", ""))
    view_count = info.get("view_count", 0) or 0
    like_count = info.get("like_count", 0) or 0
    comment_count = info.get("comment_count", 0) or 0
    duration = info.get("duration", 0) or 0
    upload_date = info.get("upload_date", "")
    description = (info.get("description", "") or "")[:500]
    thumbnail = info.get("thumbnail", "")
    tags = info.get("tags", []) or []
    category = info.get("categories", [""])[0] if info.get("categories") else ""

    # Collect hashtags from title + description + tags
    raw_hashtags = (
        extract_hashtags(title)
        + extract_hashtags(description)
        + [t.lower().replace(" ", "") for t in tags if t]
    )
    hashtags = list(dict.fromkeys(raw_hashtags))[:20]  # dedupe, cap at 20

    # Attempt to detect music from description or chapters
    music_track = _detect_music(info)

    engagement = _compute_engagement(view_count, like_count, comment_count)

    return YouTubeTrend(
        title=title,
        video_id=vid_id,
        channel=channel,
        view_count=view_count,
        like_count=like_count,
        comment_count=comment_count,
        upload_date=upload_date,
        duration=duration,
        hashtags=hashtags,
        music_track=music_track,
        description_snippet=description[:300],
        thumbnail_url=thumbnail,
        tags=tags[:30],
        category=category,
        engagement_rate=engagement,
    )


def _detect_music(info: dict) -> str:
    """Heuristically detect music from description or chapters."""
    desc = info.get("description", "") or ""
    # Look for "Music: ...", "Song: ...", "Artist: ..." patterns
    patterns = [
        r"(?:music|song|track|audio)[:\s]+([^\n]+)",
        r"(?:produced by|ft\.|feat\.)[:\s]+([^\n,]+)",
    ]
    for pat in patterns:
        m = re.search(pat, desc, re.IGNORECASE)
        if m:
            return m.group(1).strip()[:100]
    return ""


# ── Trending URL builder ──────────────────────────────────────────────

# YouTube country-specific trending URLs (YouTube Music Charts / Trending page)
_TRENDING_URLS = {
    "music":    "https://www.youtube.com/playlist?list=PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-",
    "gaming":   "https://www.youtube.com/playlist?list=PLrEnWoR732-BJbr5wsKIbVkqNloM3tFoY",
    "movies":   "https://www.youtube.com/playlist?list=PLrEnWoR732-BDXKngJBU5xXKb-TBzXMDe",
    "trending": "https://www.youtube.com/feed/trending",
}

_SEARCH_URL = "https://www.youtube.com/results?search_query={query}&sp=CAMSAhAB"  # sort by view count


def _aggregate_hashtags(trends: list[YouTubeTrend]) -> list[dict]:
    """Count hashtag frequency and compute average views across trends."""
    tag_stats: dict[str, dict] = {}
    for t in trends:
        for tag in t.hashtags:
            if tag not in tag_stats:
                tag_stats[tag] = {"tag": tag, "count": 0, "total_views": 0}
            tag_stats[tag]["count"] += 1
            tag_stats[tag]["total_views"] += t.view_count
    result = []
    for stats in tag_stats.values():
        avg_views = stats["total_views"] // max(stats["count"], 1)
        result.append({
            "tag": stats["tag"],
            "count": stats["count"],
            "avg_views": avg_views,
            "trend_score": round(stats["count"] * (avg_views / 1_000_000), 3),
        })
    result.sort(key=lambda x: x["trend_score"], reverse=True)
    return result[:50]


def _aggregate_music(trends: list[YouTubeTrend]) -> list[TrendingMusic]:
    """Find repeated music tracks across trends."""
    music_map: dict[str, dict] = {}
    for t in trends:
        track = t.music_track.strip()
        if not track:
            continue
        key = track.lower()
        if key not in music_map:
            music_map[key] = {
                "title": track, "artist": "", "video_ids": [],
                "total_views": 0, "count": 0
            }
        music_map[key]["video_ids"].append(t.video_id)
        music_map[key]["total_views"] += t.view_count
        music_map[key]["count"] += 1

    result = []
    for m in music_map.values():
        avg_views = m["total_views"] // max(m["count"], 1)
        score = round(m["count"] * (avg_views / 500_000), 3)
        result.append(TrendingMusic(
            title=m["title"],
            artist=m["artist"],
            video_ids=m["video_ids"],
            use_count=m["count"],
            avg_views=avg_views,
            trend_score=score,
        ))
    result.sort(key=lambda x: x.trend_score, reverse=True)
    return result


def _detect_viral_patterns(trends: list[YouTubeTrend]) -> list[str]:
    """Identify recurring viral content patterns from top trends."""
    patterns = []

    # Title patterns
    titles = [t.title.lower() for t in trends]
    number_titles = sum(1 for t in titles if re.search(r"\b\d+\b", t))
    if number_titles > len(trends) * 0.4:
        patterns.append("Number-based titles are trending (e.g., '10 Ways to...', '5 Secrets...')")

    question_titles = sum(1 for t in titles if "?" in t)
    if question_titles > len(trends) * 0.3:
        patterns.append("Question-format titles driving high CTR")

    # Duration patterns
    shorts = [t for t in trends if 0 < t.duration <= 60]
    if len(shorts) > len(trends) * 0.4:
        patterns.append("YouTube Shorts (≤60s) dominating — prioritize short-form content")

    mid_form = [t for t in trends if 300 <= t.duration <= 900]
    if len(mid_form) > len(trends) * 0.35:
        patterns.append("Mid-form content (5-15 min) getting highest engagement")

    long_form = [t for t in trends if t.duration > 900]
    if len(long_form) > len(trends) * 0.35:
        patterns.append("Long-form content (15+ min) dominating views — depth wins")

    # Engagement patterns
    high_eng = [t for t in trends if t.engagement_rate > 5.0]
    if high_eng:
        avg_eng = sum(t.engagement_rate for t in high_eng) / len(high_eng)
        patterns.append(f"Top videos average {avg_eng:.1f}% engagement rate — call-to-action critical")

    # Top categories
    cats = {}
    for t in trends:
        cats[t.category] = cats.get(t.category, 0) + 1
    top_cat = max(cats, key=cats.get) if cats else ""
    if top_cat:
        patterns.append(f"Dominant category: {top_cat} — align content to category signals")

    return patterns


# ── Public API ────────────────────────────────────────────────────────

def scrape_youtube_trending(
    category: str = "trending",
    region: str = "US",
    max_results: int = 25,
) -> YouTubeTrendsResult:
    """Scrape YouTube trending videos, hashtags, and music.

    Args:
        category: One of 'trending', 'music', 'gaming', 'movies'.
        region: ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB', 'IN').
        max_results: Max number of trending videos to analyze.

    Returns:
        YouTubeTrendsResult with all scraped data.

    Raises:
        RuntimeError: If yt-dlp is not installed.
    """
    if not _ytdlp_available():
        raise RuntimeError(
            "yt-dlp is required. Install with: pip install yt-dlp"
        )

    url = _TRENDING_URLS.get(category.lower(), _TRENDING_URLS["trending"])

    # Flat-playlist fetch for speed; get video IDs first
    flat_items = _fetch_playlist_info(url, max_items=max_results)

    trends: list[YouTubeTrend] = []
    for item in flat_items:
        vid_id = item.get("id", item.get("url", ""))
        if not vid_id:
            continue
        video_url = f"https://www.youtube.com/watch?v={vid_id}"
        info = _fetch_video_info(video_url)
        if info:
            trends.append(_parse_video_to_trend(info))

    # Fallback: if playlist fetch yielded nothing (yt-dlp may need login for feed)
    # search for trending content by keyword
    if not trends:
        search_terms = {
            "music": "trending music 2025",
            "gaming": "viral gaming 2025",
            "movies": "new movies trailer 2025",
            "trending": "viral video 2025",
        }
        keyword = search_terms.get(category.lower(), "viral 2025")
        search_url = f"ytsearch{max_results}:{keyword}"
        flat_items = _fetch_playlist_info(search_url, max_items=max_results)
        for item in flat_items:
            vid_id = item.get("id", item.get("url", ""))
            if not vid_id:
                continue
            video_url = f"https://www.youtube.com/watch?v={vid_id}"
            info = _fetch_video_info(video_url)
            if info:
                trends.append(_parse_video_to_trend(info))

    top_hashtags = _aggregate_hashtags(trends)
    trending_music = _aggregate_music(trends)
    viral_patterns = _detect_viral_patterns(trends)

    return YouTubeTrendsResult(
        scraped_at=datetime.utcnow().isoformat() + "Z",
        region=region,
        category=category,
        trends=trends,
        top_hashtags=top_hashtags,
        trending_music=trending_music,
        viral_patterns=viral_patterns,
    )


def search_youtube_hashtag(
    hashtag: str,
    max_results: int = 20,
) -> list[YouTubeTrend]:
    """Fetch videos for a specific hashtag to gauge its performance.

    Args:
        hashtag: Hashtag to search (with or without #).
        max_results: Max videos to retrieve.

    Returns:
        List of YouTubeTrend objects.
    """
    if not _ytdlp_available():
        raise RuntimeError("yt-dlp is required. Install with: pip install yt-dlp")

    tag = hashtag.lstrip("#")
    search_url = f"ytsearch{max_results}:#{tag}"
    flat_items = _fetch_playlist_info(search_url, max_items=max_results)

    trends = []
    for item in flat_items:
        vid_id = item.get("id", item.get("url", ""))
        if not vid_id:
            continue
        info = _fetch_video_info(f"https://www.youtube.com/watch?v={vid_id}")
        if info:
            trends.append(_parse_video_to_trend(info))
    return trends
