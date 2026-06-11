"""TikTok sound/music tools — extract and surface trending audio."""

from __future__ import annotations

from cli_anything.tiktok.utils.tiktok_backend import (
    get_trending_videos,
    get_hashtag_videos,
    extract_trends_from_videos,
)


def get_trending_sounds(region: str = "US", limit: int = 20) -> dict:
    """Fetch trending sounds from the TikTok trending feed."""
    videos = get_trending_videos(region=region, limit=limit)
    analysis = extract_trends_from_videos(videos)
    sounds = analysis["trending_sounds"]

    return {
        "region": region,
        "sounds": sounds,
        "count": len(sounds),
        "tips": _sound_tips(),
    }


def get_sounds_for_niche(niche: str, limit: int = 20) -> dict:
    """Fetch trending sounds within a specific niche hashtag."""
    from cli_anything.tiktok.utils.tiktok_backend import get_niche_hashtags
    tags = get_niche_hashtags(niche, limit=3)
    if not tags:
        raise ValueError(f"Unknown niche: {niche}")

    all_sounds: dict[str, dict] = {}
    for tag in tags[:2]:
        try:
            vids = get_hashtag_videos(tag, limit=max(limit // 2, 10))
            analysis = extract_trends_from_videos(vids)
            for s in analysis["trending_sounds"]:
                key = s["title"].lower()
                if key not in all_sounds:
                    all_sounds[key] = s
                else:
                    all_sounds[key]["count"] += s["count"]
        except RuntimeError:
            continue

    sounds = sorted(all_sounds.values(), key=lambda x: x["count"], reverse=True)

    return {
        "niche": niche,
        "sounds": sounds[:limit],
        "count": len(sounds[:limit]),
        "tips": _sound_tips(),
    }


def _sound_tips() -> list[str]:
    return [
        "Use a trending sound even at low volume (10-20%) to appear on its Explore page",
        "Choose sounds under 7 days old for maximum trend momentum",
        "Check the 'Trending' section in TikTok's sound picker before posting",
        "Viral original sounds boost your following — create unique audio hooks",
        "Duet popular sound trends with your own twist for guaranteed reach",
        "Save sounds from trending competitors and recreate similar content",
    ]
