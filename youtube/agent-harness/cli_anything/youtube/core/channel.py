"""YouTube channel analysis and optimization."""

from __future__ import annotations

from cli_anything.youtube.utils.yt_backend import (
    channel_audit_tips,
    extract_channel_hashtags,
    get_niche_keywords,
)


def audit(channel_url: str = "", niche: str = "", api_key: str | None = None) -> dict:
    """Full channel audit with optimization recommendations."""
    return channel_audit_tips(channel_url=channel_url, niche=niche)


def analyze_competitor(channel_url: str, limit: int = 20) -> dict:
    """Analyze a competitor channel's hashtag and keyword strategy."""
    hashtag_data = extract_channel_hashtags(channel_url, limit=limit)
    return {
        "channel_url": channel_url,
        "videos_analyzed": hashtag_data["videos_analyzed"],
        "top_hashtags": hashtag_data["top_hashtags"],
        "insights": [
            "These are the hashtags driving their reach — include the top 5 in your next video",
            "Low-competition hashtags in this list are fastest to rank for",
            "If a hashtag appears on 3+ of their top videos, it's a strong niche signal",
        ],
    }


def keyword_research(niche: str, limit: int = 20) -> dict:
    """Generate keyword and title ideas for a YouTube niche."""
    keywords = get_niche_keywords(niche, limit=limit)
    return {
        "niche": niche,
        "keywords": keywords,
        "count": len(keywords),
        "how_to_use": [
            "Include target keyword in video title (ideally first 40 chars)",
            "Put keyword in the first line of the video description",
            "Add keyword as a tag in YouTube Studio",
            "Say the keyword in the video (YouTube auto-transcribes and indexes speech)",
            "Use keyword in chapter titles for Featured Snippet eligibility",
        ],
    }
