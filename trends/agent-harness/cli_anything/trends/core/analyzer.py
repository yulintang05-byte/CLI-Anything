"""Cross-platform trend analyzer — merges YouTube + TikTok signals into unified rankings."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Optional


def merge_hashtags(
    youtube_hashtags: list[dict],
    tiktok_hashtags: list[dict],
) -> list[dict]:
    """Merge and cross-score hashtags from both platforms.

    Tags present on both platforms get a virality multiplier.
    """
    combined: dict[str, dict] = {}

    for h in youtube_hashtags:
        tag = h["hashtag"].lower()
        combined[tag] = {
            "hashtag": tag,
            "youtube_score": h.get("score", 0),
            "youtube_views": h.get("total_views", 0),
            "youtube_video_count": h.get("video_count", 0),
            "tiktok_score": 0,
            "tiktok_views": 0,
            "tiktok_video_count": 0,
            "platforms": ["youtube"],
        }

    for h in tiktok_hashtags:
        tag = h["hashtag"].lower()
        if tag in combined:
            combined[tag]["tiktok_score"] = h.get("score", 0)
            combined[tag]["tiktok_views"] = h.get("total_views", h.get("view_count", 0))
            combined[tag]["tiktok_video_count"] = h.get("video_count", 0)
            combined[tag]["platforms"].append("tiktok")
        else:
            combined[tag] = {
                "hashtag": tag,
                "youtube_score": 0,
                "youtube_views": 0,
                "youtube_video_count": 0,
                "tiktok_score": h.get("score", 0),
                "tiktok_views": h.get("total_views", h.get("view_count", 0)),
                "tiktok_video_count": h.get("video_count", 0),
                "platforms": ["tiktok"],
            }

    results = []
    for tag, d in combined.items():
        cross_platform = len(d["platforms"]) > 1
        # Cross-platform bonus: 2x multiplier
        base_score = d["youtube_score"] + d["tiktok_score"]
        final_score = base_score * (2.0 if cross_platform else 1.0)
        results.append({
            **d,
            "cross_platform": cross_platform,
            "combined_score": round(final_score, 2),
            "total_views": d["youtube_views"] + d["tiktok_views"],
        })

    return sorted(results, key=lambda x: x["combined_score"], reverse=True)


def merge_videos(
    youtube_videos: list[dict],
    tiktok_videos: list[dict],
) -> list[dict]:
    """Combine and rank videos from both platforms by engagement rate."""
    all_videos = []

    for v in youtube_videos:
        views = v.get("views", 0)
        likes = v.get("likes", 0)
        er = (likes / views * 100) if views > 0 else 0
        all_videos.append({**v, "engagement_rate": round(er, 2)})

    for v in tiktok_videos:
        views = v.get("views", 0)
        likes = v.get("likes", 0)
        er = (likes / views * 100) if views > 0 else 0
        all_videos.append({**v, "engagement_rate": round(er, 2)})

    return sorted(all_videos, key=lambda x: x.get("views", 0), reverse=True)


def extract_trending_topics(videos: list[dict], top_n: int = 20) -> list[dict]:
    """Extract recurring topic keywords from video titles/descriptions."""
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "is", "was", "are", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "must", "can", "this", "that", "these",
        "those", "i", "you", "he", "she", "it", "we", "they", "what", "which",
        "who", "how", "when", "where", "why", "all", "not", "no", "so", "if",
        "my", "your", "his", "her", "its", "our", "their", "new", "just",
        "more", "get", "got", "go", "going", "from", "by", "as", "up", "out",
        "video", "watch", "like", "subscribe", "comment", "share",
    }

    word_freq: dict[str, int] = defaultdict(int)
    word_views: dict[str, int] = defaultdict(int)

    for v in videos:
        text = f"{v.get('title', '')} {v.get('description', '')}"
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        views = v.get("views", 0)
        for word in words:
            if word not in stop_words:
                word_freq[word] += 1
                word_views[word] += views

    results = [
        {
            "topic": word,
            "frequency": freq,
            "total_views": word_views[word],
            "score": round(freq * 5 + word_views[word] / 1_000_000, 2),
        }
        for word, freq in word_freq.items()
        if freq >= 2
    ]

    return sorted(results, key=lambda x: x["score"], reverse=True)[:top_n]


def identify_content_themes(videos: list[dict]) -> list[dict]:
    """Group videos into broad content themes for niche targeting."""
    theme_keywords = {
        "fitness": ["workout", "gym", "fitness", "exercise", "health", "body", "muscle", "training", "diet"],
        "food": ["food", "recipe", "cooking", "eat", "chef", "restaurant", "meal", "delicious", "taste"],
        "fashion": ["fashion", "style", "outfit", "clothing", "wear", "trend", "luxury", "brand", "design"],
        "travel": ["travel", "trip", "vacation", "destination", "explore", "adventure", "country", "city", "beach"],
        "tech": ["tech", "technology", "phone", "app", "software", "ai", "coding", "programming", "gadget"],
        "beauty": ["beauty", "makeup", "skincare", "hair", "cosmetics", "glow", "tutorial", "product"],
        "finance": ["money", "invest", "finance", "crypto", "stock", "wealth", "income", "passive", "side hustle"],
        "gaming": ["game", "gaming", "play", "esports", "stream", "console", "pc", "mobile"],
        "motivation": ["motivation", "success", "mindset", "inspire", "hustle", "grind", "life", "goal"],
        "comedy": ["funny", "comedy", "laugh", "joke", "humor", "prank", "hilarious", "meme"],
        "music": ["music", "song", "artist", "album", "track", "beat", "rap", "pop", "viral"],
        "lifestyle": ["lifestyle", "day", "routine", "vlog", "daily", "morning", "night", "home"],
    }

    theme_scores: dict[str, dict] = {
        t: {"theme": t, "video_count": 0, "total_views": 0, "sample_titles": []}
        for t in theme_keywords
    }

    for v in videos:
        text = f"{v.get('title', '')} {v.get('description', '')}".lower()
        views = v.get("views", 0)
        for theme, kws in theme_keywords.items():
            if any(kw in text for kw in kws):
                theme_scores[theme]["video_count"] += 1
                theme_scores[theme]["total_views"] += views
                if len(theme_scores[theme]["sample_titles"]) < 3:
                    title = v.get("title", "")
                    if title:
                        theme_scores[theme]["sample_titles"].append(title)

    results = [
        d for d in theme_scores.values() if d["video_count"] > 0
    ]
    return sorted(results, key=lambda x: x["total_views"], reverse=True)


def build_trend_report(
    youtube_data: Optional[dict] = None,
    tiktok_data: Optional[dict] = None,
    region: str = "US",
) -> dict:
    """Build a unified trend report from available platform data."""
    youtube_videos = (youtube_data or {}).get("videos", [])
    tiktok_videos = (tiktok_data or {}).get("videos", [])
    youtube_hashtags = (youtube_data or {}).get("hashtags", [])
    tiktok_hashtags = (tiktok_data or {}).get("hashtags", [])

    all_videos = merge_videos(youtube_videos, tiktok_videos)
    unified_hashtags = merge_hashtags(youtube_hashtags, tiktok_hashtags)
    topics = extract_trending_topics(all_videos, top_n=15)
    themes = identify_content_themes(all_videos)

    # Top performing hashtags (cross-platform preferred)
    cross_platform_tags = [h for h in unified_hashtags if h.get("cross_platform")]
    single_platform_tags = [h for h in unified_hashtags if not h.get("cross_platform")]

    return {
        "region": region,
        "platforms_analyzed": [p for p in ["youtube", "tiktok"] if p in [
            (youtube_data or {}).get("platform"),
            (tiktok_data or {}).get("platform"),
        ]],
        "total_videos_analyzed": len(all_videos),
        "cross_platform_hashtags": cross_platform_tags[:15],
        "top_hashtags": unified_hashtags[:30],
        "trending_topics": topics,
        "content_themes": themes[:8],
        "top_videos": all_videos[:10],
        "music_trends": (youtube_data or {}).get("music_trends", [])[:10],
        "tiktok_sounds": (tiktok_data or {}).get("sounds", [])[:10],
    }
