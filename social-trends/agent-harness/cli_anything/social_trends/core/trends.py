"""Core trend aggregation — combines YouTube + TikTok data into unified reports."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from cli_anything.social_trends.utils import youtube_backend as yt
from cli_anything.social_trends.utils import tiktok_backend as tt


def fetch_all_trends(
    region: str = "US",
    limit: int = 10,
    yt_key: str | None = None,
    tt_key: str | None = None,
) -> dict:
    """Fetch trending content from both YouTube and TikTok in one call."""
    yt_trends = yt.fetch_trending_videos(region=region, limit=limit, api_key=yt_key)
    tt_trends = tt.fetch_trending_videos(region=region, limit=limit, api_key=tt_key)
    yt_music = yt.fetch_trending_music(region=region, limit=5, api_key=yt_key)
    tt_sounds = tt.fetch_trending_sounds(limit=5, api_key=tt_key)

    # Extract cross-platform music overlap
    yt_titles = {item["title"].lower() for item in yt_music.get("items", [])}
    tt_titles = {item["title"].lower() for item in tt_sounds.get("items", [])}
    cross_platform_music = [
        t for t in tt_sounds.get("items", [])
        if any(yt_t in t["title"].lower() or t["title"].lower() in yt_t for yt_t in yt_titles)
    ]

    # Aggregate top hashtags across platforms
    yt_tags = yt.fetch_trending_hashtags(limit=5, api_key=yt_key)
    tt_tags = tt.fetch_trending_hashtags(limit=5, api_key=tt_key)

    return {
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "region": region,
        "youtube": {
            "trending_videos": yt_trends["items"],
            "trending_music": yt_music["items"],
            "mode": yt_trends["mode"],
        },
        "tiktok": {
            "trending_videos": tt_trends["items"],
            "trending_sounds": tt_sounds["items"],
            "mode": tt_trends["mode"],
        },
        "cross_platform": {
            "music_on_both": cross_platform_music,
            "top_yt_hashtags": yt_tags["items"][:5],
            "top_tt_hashtags": tt_tags["items"][:5],
        },
        "insights": _generate_insights(yt_trends, tt_trends, yt_music, tt_sounds),
    }


def _generate_insights(yt_trends: dict, tt_trends: dict, yt_music: dict, tt_sounds: dict) -> list:
    insights = []

    # Top theme from YouTube
    if yt_trends.get("items"):
        top_yt = yt_trends["items"][0]
        insights.append({
            "type": "youtube_top",
            "message": f"YouTube #1 trending: '{top_yt['title']}' by {top_yt['channel']} — {top_yt['views']:,} views",
            "action": f"Create a response/reaction/analysis video on this topic",
        })

    # Top theme from TikTok
    if tt_trends.get("items"):
        top_tt = tt_trends["items"][0]
        insights.append({
            "type": "tiktok_top",
            "message": f"TikTok #1 trending: '{top_tt['desc'][:60]}' by {top_tt['author']} — {top_tt['plays']:,} plays",
            "action": f"Use this format/trend for your own niche content immediately",
        })

    # Top sound recommendation
    if tt_sounds.get("items"):
        top_sound = tt_sounds["items"][0]
        insights.append({
            "type": "trending_sound",
            "message": f"Hottest TikTok sound: '{top_sound['title']}' by {top_sound['author']} — {top_sound.get('uses', 0):,} uses",
            "action": f"Use this sound in your next post. Mood: {top_sound.get('mood', 'N/A')}. Best content types: {', '.join(top_sound.get('recommended_content', [])[:2])}",
        })

    insights.append({
        "type": "strategy",
        "message": "Post on BOTH platforms within 24h of a trend appearing for maximum reach",
        "action": "YouTube Shorts + TikTok same-day posting doubles discovery potential",
    })

    return insights
