"""YouTube hashtag tools — extract, suggest, and strategize."""

from __future__ import annotations

from cli_anything.youtube.utils.yt_backend import (
    get_video_metadata,
    extract_channel_hashtags,
    get_niche_keywords,
    NICHE_KEYWORDS,
)


def extract_from_video(video_url: str, api_key: str | None = None) -> dict:
    """Extract hashtags and tags from a YouTube video."""
    meta = get_video_metadata(video_url, api_key=api_key)
    return {
        "url": video_url,
        "title": meta.get("title", ""),
        "hashtags": meta.get("hashtags", []),
        "tags": meta.get("tags", []),
        "channel": meta.get("channel", ""),
        "total_found": len(meta.get("hashtags", [])) + len(meta.get("tags", [])),
    }


def extract_from_channel(channel_url: str, limit: int = 20) -> dict:
    """Extract top hashtags used by a channel."""
    return extract_channel_hashtags(channel_url, limit=limit)


def suggest_for_niche(niche: str, limit: int = 20) -> dict:
    """Return keyword/hashtag suggestions for a YouTube niche."""
    keywords = get_niche_keywords(niche, limit=limit)
    hashtags = [f"#{k.replace(' ', '')}" for k in keywords[:10]]
    return {
        "niche": niche,
        "search_keywords": keywords,
        "hashtags": hashtags,
        "title_formulas": _title_formulas(niche, keywords[:3]),
        "strategy": (
            "YouTube hashtags: use 3-5 per video. "
            "Add 1 channel hashtag, 1 broad niche tag, 1 specific keyword tag. "
            "Do NOT use 15+ hashtags — YouTube may ignore all of them."
        ),
    }


def list_niches() -> list[str]:
    return sorted(NICHE_KEYWORDS.keys())


def _title_formulas(niche: str, top_keywords: list[str]) -> list[str]:
    formulas = []
    if top_keywords:
        kw = top_keywords[0]
        formulas = [
            f"How to {kw} (Complete Guide for Beginners)",
            f"I Tried {kw.title()} for 30 Days — Here's What Happened",
            f"The TRUTH About {kw.title()} Nobody Talks About",
            f"Top 10 {kw.title()} Tips That Actually Work",
            f"{kw.title()} Mistakes EVERY Beginner Makes",
        ]
    return formulas
