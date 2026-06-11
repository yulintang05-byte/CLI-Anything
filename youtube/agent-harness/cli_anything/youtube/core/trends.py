"""YouTube trend fetching and analysis."""

from __future__ import annotations

from cli_anything.youtube.utils.yt_backend import (
    get_trending_videos_api,
    get_trending_videos_ytdlp,
    CATEGORY_IDS,
    REGIONS,
)


def fetch_trending(
    region: str = "US",
    category: str = "all",
    limit: int = 25,
    api_key: str | None = None,
) -> dict:
    """Fetch trending YouTube videos, using API if key available, else yt-dlp."""
    if api_key:
        videos = get_trending_videos_api(
            region=region, category=category, limit=limit, api_key=api_key
        )
        source = "youtube_data_api_v3"
    else:
        videos = get_trending_videos_ytdlp(region=region, limit=limit)
        source = "yt-dlp"

    return {
        "region": region,
        "category": category,
        "source": source,
        "video_count": len(videos),
        "videos": videos,
        "trending_tags": _extract_top_tags(videos),
        "trending_keywords": _extract_top_keywords(videos),
    }


def _extract_top_tags(videos: list[dict]) -> list[dict]:
    counts: dict[str, int] = {}
    for v in videos:
        for tag in v.get("hashtags", []) + v.get("tags", []):
            t = tag.lower().strip()
            if t:
                counts[t] = counts.get(t, 0) + 1
    return sorted(
        [{"tag": k, "appearances": c} for k, c in counts.items()],
        key=lambda x: x["appearances"],
        reverse=True,
    )[:25]


def _extract_top_keywords(videos: list[dict]) -> list[str]:
    import re
    from collections import Counter

    stop_words = {
        "the", "a", "an", "is", "in", "it", "to", "of", "and", "or",
        "for", "with", "on", "at", "by", "from", "this", "my", "your",
        "i", "you", "we", "they", "how", "what", "why", "when", "where",
        "be", "are", "was", "were", "will", "can", "do", "did",
    }
    words: list[str] = []
    for v in videos:
        title = v.get("title", "").lower()
        words += [w for w in re.findall(r"\b[a-z]{4,}\b", title) if w not in stop_words]
    counter = Counter(words)
    return [w for w, _ in counter.most_common(20)]


def list_categories() -> list[str]:
    return sorted(CATEGORY_IDS.keys())


def list_regions() -> list[str]:
    return sorted(REGIONS)
