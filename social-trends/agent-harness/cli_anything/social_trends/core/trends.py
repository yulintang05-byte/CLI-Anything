#!/usr/bin/env python3
"""Core trend data models and cross-platform aggregation."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class HashtagTrend:
    hashtag: str
    platform: str  # youtube | tiktok | combined
    video_count: Optional[int] = None
    total_views: Optional[int] = None
    score: Optional[float] = None
    source: str = "scrape"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MusicTrack:
    title: str
    artist: str
    platform: str
    sound_id: Optional[str] = None
    video_count: Optional[int] = None
    total_views: Optional[int] = None
    duration_seconds: Optional[int] = None
    url: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TrendReport:
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    region: str = "US"
    platforms: list[str] = field(default_factory=list)
    top_hashtags: list[dict] = field(default_factory=list)
    top_music: list[dict] = field(default_factory=list)
    top_videos: list[dict] = field(default_factory=list)
    cross_platform_hashtags: list[dict] = field(default_factory=list)
    insights: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def merge_platform_trends(
    youtube_data: Optional[dict],
    tiktok_data: Optional[dict],
    region: str = "US",
) -> TrendReport:
    """Merge YouTube and TikTok trend data into a single TrendReport.

    Cross-references hashtags and music that appear on both platforms,
    which are the strongest signal for truly viral content.
    """
    report = TrendReport(region=region)

    yt_hashtags: dict[str, dict] = {}
    tt_hashtags: dict[str, dict] = {}
    all_music: list[dict] = []
    all_videos: list[dict] = []

    if youtube_data:
        report.platforms.append("youtube")
        for ht in youtube_data.get("hashtags", []):
            key = ht["hashtag"].lower()
            yt_hashtags[key] = {
                "hashtag": ht["hashtag"],
                "platform": "youtube",
                "weighted_views": ht.get("weighted_views", 0),
            }
        for m in youtube_data.get("music_tracks", []):
            all_music.append({**m, "platform": "youtube"})
        for v in youtube_data.get("videos", [])[:10]:
            all_videos.append({**v, "platform": "youtube"})

    if tiktok_data:
        report.platforms.append("tiktok")
        for ht in tiktok_data.get("hashtags", []):
            key = ht["hashtag"].lower()
            tt_hashtags[key] = {
                "hashtag": ht["hashtag"],
                "platform": "tiktok",
                "video_count": ht.get("video_count", 0),
                "total_views": ht.get("total_views", 0),
            }
        for s in tiktok_data.get("trending_sounds", []):
            all_music.append({**s, "platform": "tiktok"})
        for v in tiktok_data.get("videos", [])[:10]:
            all_videos.append({**v, "platform": "tiktok"})

    # Cross-platform hashtags appear on both — highest signal
    cross = []
    for key in set(yt_hashtags) & set(tt_hashtags):
        yt = yt_hashtags[key]
        tt = tt_hashtags[key]
        cross.append({
            "hashtag": yt["hashtag"],
            "platforms": ["youtube", "tiktok"],
            "yt_weighted_views": yt.get("weighted_views"),
            "tt_video_count": tt.get("video_count"),
            "tt_total_views": tt.get("total_views"),
            "cross_platform_score": (yt.get("weighted_views", 0) or 0)
            + (tt.get("total_views", 0) or 0),
        })
    cross.sort(key=lambda x: x["cross_platform_score"], reverse=True)
    report.cross_platform_hashtags = cross

    # Unified top hashtags
    combined: dict[str, dict] = {}
    for key, ht in yt_hashtags.items():
        combined[key] = {
            "hashtag": ht["hashtag"],
            "platforms": ["youtube"],
            "score": ht.get("weighted_views", 0) or 0,
        }
    for key, ht in tt_hashtags.items():
        tt_score = (ht.get("total_views") or 0) + (ht.get("video_count") or 0) * 1000
        if key in combined:
            combined[key]["platforms"].append("tiktok")
            combined[key]["score"] = combined[key]["score"] + tt_score
        else:
            combined[key] = {
                "hashtag": ht["hashtag"],
                "platforms": ["tiktok"],
                "score": tt_score,
            }

    report.top_hashtags = sorted(
        combined.values(), key=lambda x: x["score"], reverse=True
    )[:50]

    report.top_music = sorted(
        all_music,
        key=lambda x: (x.get("total_views") or 0) + (x.get("video_count") or 0) * 500,
        reverse=True,
    )[:20]

    report.top_videos = all_videos[:20]

    report.insights = _generate_insights(report)

    return report


def _generate_insights(report: TrendReport) -> list[str]:
    """Generate actionable insight strings from merged trend data."""
    insights = []

    cross = report.cross_platform_hashtags
    if cross:
        top3 = ", ".join(h["hashtag"] for h in cross[:3])
        insights.append(
            f"Cross-platform signals (highest priority): {top3} — trending on both YouTube and TikTok simultaneously."
        )

    if report.top_music:
        top_track = report.top_music[0]
        title = top_track.get("title") or top_track.get("track", "")
        artist = top_track.get("artist", "")
        platform = top_track.get("platform", "")
        if title:
            insights.append(
                f"Hottest audio: '{title}' by {artist} ({platform}) — use this sound immediately for maximum reach."
            )

    if len(report.platforms) == 1:
        insights.append(
            "Only one platform scraped. Cross-posting to both YouTube Shorts and TikTok maximizes reach — run both scrapers."
        )

    if report.top_hashtags:
        density_tip = (
            "Use 3-5 hashtags per post (not 20+). Hashtag stuffing hurts reach on both platforms as of 2024."
        )
        insights.append(density_tip)

    insights.append(
        "Post within 1-3 hours of identifying a trend — viral windows on TikTok average 24-48h, YouTube Shorts 48-72h."
    )

    return insights
