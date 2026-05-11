"""TikTok viral trends, hashtags, and music scraper.

Uses yt-dlp for video metadata (no account required) and optional
unofficial TikTok API for deeper trend data.
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
class TikTokTrend:
    title: str
    video_id: str
    author: str
    author_followers: int
    play_count: int
    like_count: int
    comment_count: int
    share_count: int
    duration: int          # seconds
    hashtags: list[str]
    music_title: str
    music_author: str
    music_is_original: bool
    upload_date: str
    thumbnail_url: str
    video_url: str
    engagement_rate: float  # (likes + comments + shares) / plays * 100
    virality_score: float   # composite: plays/followers, shares, etc.

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TikTokMusicTrend:
    music_id: str
    title: str
    artist: str
    video_count: int       # videos using this sound
    avg_plays: int
    is_original: bool
    trend_score: float


@dataclass
class TikTokTrendsResult:
    scraped_at: str
    region: str
    trends: list[TikTokTrend]
    top_hashtags: list[dict]      # [{tag, count, avg_plays, trend_score}]
    trending_music: list[TikTokMusicTrend]
    viral_patterns: list[str]
    content_strategy: list[str]   # recommended actions

    def to_dict(self) -> dict:
        return {
            "scraped_at": self.scraped_at,
            "region": self.region,
            "trends": [t.to_dict() for t in self.trends],
            "top_hashtags": self.top_hashtags,
            "trending_music": [asdict(m) for m in self.trending_music],
            "viral_patterns": self.viral_patterns,
            "content_strategy": self.content_strategy,
        }


# ── Helpers ───────────────────────────────────────────────────────────

def _extract_hashtags(text: str) -> list[str]:
    return [tag.lower() for tag in re.findall(r"#(\w+)", text)]


def _compute_engagement(plays: int, likes: int, comments: int, shares: int) -> float:
    if plays == 0:
        return 0.0
    return round((likes + comments + shares) / plays * 100, 4)


def _compute_virality(plays: int, likes: int, shares: int, followers: int) -> float:
    """Virality = weighted score of raw plays, share ratio, and follower multiplier."""
    share_ratio = shares / max(plays, 1)
    follower_mult = plays / max(followers, 1)
    raw = plays / 1_000_000
    return round(raw * 0.5 + share_ratio * 30 + follower_mult * 0.2, 4)


def _ytdlp_available() -> bool:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--version"],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def _fetch_tiktok_video(url: str) -> Optional[dict]:
    """Fetch TikTok video metadata via yt-dlp."""
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


def _search_tiktok(query: str, max_results: int = 20) -> list[dict]:
    """Search TikTok via yt-dlp search."""
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "yt_dlp",
                "--dump-json",
                "--flat-playlist",
                "--playlist-end", str(max_results),
                "--quiet",
                f"tiktoksearch{max_results}:{query}",
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


def _fetch_tiktok_user_feed(username: str, max_results: int = 30) -> list[dict]:
    """Fetch recent videos from a TikTok user's profile."""
    try:
        url = f"https://www.tiktok.com/@{username.lstrip('@')}"
        result = subprocess.run(
            [
                sys.executable, "-m", "yt_dlp",
                "--dump-json",
                "--flat-playlist",
                "--playlist-end", str(max_results),
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


def _parse_tiktok_info(info: dict) -> TikTokTrend:
    """Convert yt-dlp TikTok info dict into a TikTokTrend."""
    vid_id = info.get("id", "")
    title = info.get("title", info.get("description", ""))[:300]
    author = info.get("uploader", info.get("creator", ""))
    followers = info.get("channel_follower_count", 0) or 0
    plays = info.get("view_count", 0) or 0
    likes = info.get("like_count", 0) or 0
    comments = info.get("comment_count", 0) or 0
    shares = info.get("repost_count", info.get("share_count", 0)) or 0
    duration = info.get("duration", 0) or 0
    upload_date = info.get("upload_date", "")
    thumbnail = info.get("thumbnail", "")
    webpage_url = info.get("webpage_url", f"https://www.tiktok.com/video/{vid_id}")

    # Hashtags from description/title
    hashtags = list(dict.fromkeys(_extract_hashtags(title)))[:20]

    # Music info
    music_title = ""
    music_author = ""
    music_original = False
    if "music" in info:
        m = info["music"]
        music_title = m.get("title", "")
        music_author = m.get("author", "")
        music_original = m.get("original", False)
    elif info.get("track"):
        music_title = info.get("track", "")
        music_author = info.get("artist", "")

    engagement = _compute_engagement(plays, likes, comments, shares)
    virality = _compute_virality(plays, likes, shares, followers)

    return TikTokTrend(
        title=title,
        video_id=vid_id,
        author=author,
        author_followers=followers,
        play_count=plays,
        like_count=likes,
        comment_count=comments,
        share_count=shares,
        duration=duration,
        hashtags=hashtags,
        music_title=music_title,
        music_author=music_author,
        music_is_original=music_original,
        upload_date=upload_date,
        thumbnail_url=thumbnail,
        video_url=webpage_url,
        engagement_rate=engagement,
        virality_score=virality,
    )


def _aggregate_hashtags(trends: list[TikTokTrend]) -> list[dict]:
    tag_stats: dict[str, dict] = {}
    for t in trends:
        for tag in t.hashtags:
            if tag not in tag_stats:
                tag_stats[tag] = {"tag": tag, "count": 0, "total_plays": 0}
            tag_stats[tag]["count"] += 1
            tag_stats[tag]["total_plays"] += t.play_count
    result = []
    for stats in tag_stats.values():
        avg_plays = stats["total_plays"] // max(stats["count"], 1)
        result.append({
            "tag": stats["tag"],
            "count": stats["count"],
            "avg_plays": avg_plays,
            "trend_score": round(stats["count"] * (avg_plays / 500_000), 3),
        })
    result.sort(key=lambda x: x["trend_score"], reverse=True)
    return result[:50]


def _aggregate_music(trends: list[TikTokTrend]) -> list[TikTokMusicTrend]:
    music_map: dict[str, dict] = {}
    for t in trends:
        if not t.music_title:
            continue
        key = (t.music_title + t.music_author).lower()
        if key not in music_map:
            music_map[key] = {
                "id": key, "title": t.music_title, "artist": t.music_author,
                "count": 0, "total_plays": 0, "is_original": t.music_is_original
            }
        music_map[key]["count"] += 1
        music_map[key]["total_plays"] += t.play_count

    result = []
    for m in music_map.values():
        avg_plays = m["total_plays"] // max(m["count"], 1)
        score = round(m["count"] * (avg_plays / 500_000), 3)
        result.append(TikTokMusicTrend(
            music_id=m["id"],
            title=m["title"],
            artist=m["artist"],
            video_count=m["count"],
            avg_plays=avg_plays,
            is_original=m["is_original"],
            trend_score=score,
        ))
    result.sort(key=lambda x: x.trend_score, reverse=True)
    return result


def _detect_viral_patterns(trends: list[TikTokTrend]) -> list[str]:
    patterns = []

    if not trends:
        return patterns

    # Duration analysis
    shorts = [t for t in trends if 0 < t.duration <= 15]
    mid = [t for t in trends if 15 < t.duration <= 60]
    long_ = [t for t in trends if t.duration > 60]

    if len(shorts) > len(trends) * 0.4:
        patterns.append("Ultra-short clips (≤15s) going viral — hook in first 2 seconds")
    if len(mid) > len(trends) * 0.4:
        patterns.append("15-60s format dominates — complete story arc within the scroll")
    if len(long_) > len(trends) * 0.3:
        patterns.append("Long-form TikToks (60s+) gaining traction — depth content rising")

    # Hashtag count analysis
    avg_tags = sum(len(t.hashtags) for t in trends) / max(len(trends), 1)
    patterns.append(f"Average {avg_tags:.1f} hashtags per viral post — use 3-7 niche tags + 1-2 broad tags")

    # Engagement benchmarks
    avg_eng = sum(t.engagement_rate for t in trends) / max(len(trends), 1)
    patterns.append(f"Benchmark engagement rate: {avg_eng:.2f}% — aim above this to signal virality to algorithm")

    # Original vs. licensed music
    original_count = sum(1 for t in trends if t.music_is_original)
    licensed_count = len(trends) - original_count
    if licensed_count > original_count:
        patterns.append("Licensed/trending sounds boost reach — use sounds already in the TikTok ecosystem")
    else:
        patterns.append("Original audio in top videos — create ownable sounds for brand recognition")

    # High share-ratio content
    high_share = [t for t in trends if t.share_count > t.like_count * 0.05]
    if len(high_share) > len(trends) * 0.3:
        patterns.append("High share-to-like ratio — 'share-worthy' content (educational, emotional, funny) outperforms")

    return patterns


def _generate_content_strategy(
    trends: list[TikTokTrend],
    hashtags: list[dict],
    music: list[TikTokMusicTrend],
) -> list[str]:
    """Generate concrete posting and content strategy from scraped data."""
    strategy = []

    # Top hashtags
    if hashtags:
        top_tags = [h["tag"] for h in hashtags[:5]]
        strategy.append(f"Priority hashtags to use NOW: #{' #'.join(top_tags)}")

    # Trending sounds
    if music:
        top_sound = music[0]
        strategy.append(
            f"Trending sound to use: '{top_sound.title}' by {top_sound.artist} "
            f"(used in {top_sound.video_count} viral videos)"
        )

    # Posting time recommendation
    strategy.append(
        "Optimal posting windows: 6-9am, 12-3pm, 7-11pm in your audience's timezone — "
        "post 1-4x per day for algorithmic momentum"
    )

    # Content hook
    strategy.append(
        "Hook formula: First 1-3 seconds must include text overlay + voiceover + visual action simultaneously"
    )

    # CTA
    strategy.append(
        "End-card CTA: 'Follow for more [niche] content' + pin a comment to drive early engagement"
    )

    # Duet/Stitch
    high_viral = sorted(trends, key=lambda x: x.virality_score, reverse=True)[:3]
    if high_viral:
        vid = high_viral[0]
        strategy.append(
            f"Duet or Stitch this viral video for easy reach: @{vid.author} ({vid.play_count:,} plays)"
        )

    return strategy


# ── Public API ────────────────────────────────────────────────────────

# Trending niche search terms
_NICHE_SEARCHES = {
    "fitness":   ["gym motivation", "workout tips", "fitness transformation"],
    "finance":   ["money tips", "financial freedom", "passive income"],
    "food":      ["recipe hack", "easy recipe", "food asmr"],
    "beauty":    ["makeup tutorial", "skincare routine", "glow up"],
    "travel":    ["travel vlog", "hidden gems travel", "budget travel"],
    "fashion":   ["outfit ideas", "style tips", "fashion haul"],
    "comedy":    ["funny video", "relatable humor", "comedy skit"],
    "education": ["learn something new", "did you know", "life hack"],
    "general":   ["viral video 2025", "trending tiktok", "for you page"],
}


def scrape_tiktok_trending(
    niche: str = "general",
    region: str = "US",
    max_results: int = 30,
) -> TikTokTrendsResult:
    """Scrape TikTok trending content for a given niche.

    Args:
        niche: Content niche — 'fitness', 'finance', 'food', 'beauty',
               'travel', 'fashion', 'comedy', 'education', or 'general'.
        region: Target region (informational — TikTok geo-targets by IP).
        max_results: Max videos per search query to analyze.

    Returns:
        TikTokTrendsResult with full trend data.

    Raises:
        RuntimeError: If yt-dlp is not installed.
    """
    if not _ytdlp_available():
        raise RuntimeError(
            "yt-dlp is required. Install with: pip install yt-dlp"
        )

    search_terms = _NICHE_SEARCHES.get(niche.lower(), _NICHE_SEARCHES["general"])
    all_trends: list[TikTokTrend] = []
    seen_ids: set[str] = set()

    for term in search_terms:
        items = _search_tiktok(term, max_results=max_results // len(search_terms) + 5)
        for item in items:
            vid_id = item.get("id", item.get("url", ""))
            if not vid_id or vid_id in seen_ids:
                continue
            seen_ids.add(vid_id)
            # Get full metadata if we only have flat info
            if "view_count" not in item:
                url = item.get("url", f"https://www.tiktok.com/video/{vid_id}")
                full_info = _fetch_tiktok_video(url)
                if full_info:
                    all_trends.append(_parse_tiktok_info(full_info))
            else:
                all_trends.append(_parse_tiktok_info(item))

    # Sort by virality
    all_trends.sort(key=lambda x: x.virality_score, reverse=True)
    top_trends = all_trends[:max_results]

    top_hashtags = _aggregate_hashtags(top_trends)
    trending_music = _aggregate_music(top_trends)
    viral_patterns = _detect_viral_patterns(top_trends)
    content_strategy = _generate_content_strategy(top_trends, top_hashtags, trending_music)

    return TikTokTrendsResult(
        scraped_at=datetime.utcnow().isoformat() + "Z",
        region=region,
        trends=top_trends,
        top_hashtags=top_hashtags,
        trending_music=trending_music,
        viral_patterns=viral_patterns,
        content_strategy=content_strategy,
    )


def scrape_tiktok_user(
    username: str,
    max_videos: int = 30,
) -> TikTokTrendsResult:
    """Scrape a specific TikTok user's content for trend analysis.

    Args:
        username: TikTok username (with or without @).
        max_videos: Max videos to analyze.

    Returns:
        TikTokTrendsResult populated from user's content.
    """
    if not _ytdlp_available():
        raise RuntimeError("yt-dlp is required. Install with: pip install yt-dlp")

    items = _fetch_tiktok_user_feed(username, max_results=max_videos)
    trends: list[TikTokTrend] = []

    for item in items:
        vid_id = item.get("id", item.get("url", ""))
        if not vid_id:
            continue
        if "view_count" not in item:
            url = item.get("url", f"https://www.tiktok.com/video/{vid_id}")
            full_info = _fetch_tiktok_video(url)
            if full_info:
                trends.append(_parse_tiktok_info(full_info))
        else:
            trends.append(_parse_tiktok_info(item))

    trends.sort(key=lambda x: x.virality_score, reverse=True)
    top_hashtags = _aggregate_hashtags(trends)
    trending_music = _aggregate_music(trends)
    viral_patterns = _detect_viral_patterns(trends)
    content_strategy = _generate_content_strategy(trends, top_hashtags, trending_music)

    return TikTokTrendsResult(
        scraped_at=datetime.utcnow().isoformat() + "Z",
        region="user-specific",
        trends=trends,
        top_hashtags=top_hashtags,
        trending_music=trending_music,
        viral_patterns=viral_patterns,
        content_strategy=content_strategy,
    )
