"""Cross-platform trend aggregation and scoring.

Combines YouTube + TikTok data to surface cross-platform opportunities
and rank trends by viral potential.
"""

import time
from collections import Counter
from typing import Optional

from . import youtube_scraper as yt
from . import tiktok_scraper as tt
from . import cache as _cache


def _normalize_tag(tag: str) -> str:
    return tag.lstrip("#").lower().strip()


def aggregate_hashtags(
    platforms: list = None,
    region: str = "US",
    limit: int = 50,
    use_cache: bool = True,
) -> dict:
    """Merge hashtag data from YouTube and TikTok, rank by cross-platform frequency.

    Args:
        platforms: ["youtube", "tiktok"] or None for both
        region: YouTube region code
        limit: max hashtags to return
        use_cache: use cached data

    Returns:
        dict with ranked hashtag list, cross-platform flags, and per-platform counts
    """
    if platforms is None:
        platforms = ["youtube", "tiktok"]

    cache_key = f"agg_hashtags_{'+'.join(sorted(platforms))}_{region}"
    if use_cache:
        cached = _cache.get(cache_key, ttl=3600)
        if cached:
            cached["from_cache"] = True
            return cached

    tag_data: dict[str, dict] = {}
    errors = []

    if "youtube" in platforms:
        try:
            yt_result = yt.get_all_hashtags(region=region, limit_per_category=30)
            for item in yt_result.get("hashtags", []):
                key = _normalize_tag(item["tag"])
                if key not in tag_data:
                    tag_data[key] = {"tag": f"#{key}", "youtube_freq": 0, "tiktok_freq": 0,
                                     "total_score": 0, "platforms": []}
                tag_data[key]["youtube_freq"] += item["frequency"]
                if "youtube" not in tag_data[key]["platforms"]:
                    tag_data[key]["platforms"].append("youtube")
        except Exception as e:
            errors.append(f"youtube: {e}")

    if "tiktok" in platforms:
        try:
            tt_result = tt.get_trending_hashtags(limit=50, use_cache=use_cache)
            for item in tt_result.get("hashtags", []):
                key = _normalize_tag(item["tag"])
                if key not in tag_data:
                    tag_data[key] = {"tag": f"#{key}", "youtube_freq": 0, "tiktok_freq": 0,
                                     "total_score": 0, "platforms": []}
                view_score = min(item.get("view_count", 0) // 1_000_000, 100)
                tag_data[key]["tiktok_freq"] += max(1, view_score)
                tag_data[key]["tiktok_views"] = item.get("view_count", 0)
                tag_data[key]["tiktok_video_count"] = item.get("video_count", 0)
                if "tiktok" not in tag_data[key]["platforms"]:
                    tag_data[key]["platforms"].append("tiktok")
        except Exception as e:
            errors.append(f"tiktok: {e}")

    # Score: cross-platform tags get a 2x multiplier
    for key, d in tag_data.items():
        base = d["youtube_freq"] * 1 + d["tiktok_freq"] * 2
        cross = len(d["platforms"]) >= 2
        d["total_score"] = base * (2 if cross else 1)
        d["cross_platform"] = cross

    ranked = sorted(tag_data.values(), key=lambda x: x["total_score"], reverse=True)

    result = {
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "platforms_queried": platforms,
        "region": region,
        "count": len(ranked[:limit]),
        "hashtags": ranked[:limit],
        "errors": errors,
        "from_cache": False,
    }
    _cache.set(cache_key, result)
    return result


def aggregate_music(
    region: str = "US",
    limit: int = 30,
    use_cache: bool = True,
) -> dict:
    """Aggregate trending music/sounds from YouTube and TikTok."""
    cache_key = f"agg_music_{region}"
    if use_cache:
        cached = _cache.get(cache_key, ttl=3600)
        if cached:
            cached["from_cache"] = True
            return cached

    tracks = []
    errors = []

    # YouTube music trending
    try:
        yt_result = yt.get_trending_music(region=region, limit=20)
        for v in yt_result.get("videos", []):
            tracks.append({
                "platform": "youtube",
                "title": v["title"],
                "artist": v["channel"],
                "views_raw": v["views_raw"],
                "duration": v["duration"],
                "url": v["url"],
                "hashtags": v["hashtags"],
                "type": "music_video",
            })
    except Exception as e:
        errors.append(f"youtube_music: {e}")

    # TikTok trending sounds
    try:
        tt_result = tt.get_trending_sounds(limit=30, use_cache=use_cache)
        for s in tt_result.get("sounds", []):
            tracks.append({
                "platform": "tiktok",
                "title": s["title"],
                "artist": s["artist"],
                "duration": s["duration"],
                "use_count": s["use_count"],
                "is_original": s["is_original"],
                "type": "sound",
            })
    except Exception as e:
        errors.append(f"tiktok_sounds: {e}")

    result = {
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "region": region,
        "count": len(tracks[:limit]),
        "tracks": tracks[:limit],
        "errors": errors,
        "from_cache": False,
    }
    _cache.set(cache_key, result)
    return result


def find_opportunities(
    niche: str,
    region: str = "US",
    use_cache: bool = True,
) -> dict:
    """Find trending content opportunities relevant to a specific niche.

    Scores trends by relevance to the niche using keyword matching.
    """
    niche_words = set(_normalize_tag(w) for w in niche.lower().split())

    hashtag_result = aggregate_hashtags(region=region, limit=100, use_cache=use_cache)
    video_result = {}
    errors = list(hashtag_result.get("errors", []))

    try:
        video_result = yt.get_trending(region=region, limit=30, use_cache=use_cache)
    except Exception as e:
        errors.append(f"yt_videos: {e}")

    # Score hashtags by niche relevance
    relevant_tags = []
    for tag in hashtag_result.get("hashtags", []):
        tag_words = set(_normalize_tag(w) for w in tag["tag"].lstrip("#").split("_"))
        overlap = len(niche_words & tag_words)
        if overlap > 0 or tag["cross_platform"]:
            relevant_tags.append({**tag, "niche_relevance": overlap})

    # Score videos by niche relevance
    relevant_videos = []
    for v in video_result.get("videos", []):
        text = (v["title"] + " " + v["description_snippet"]).lower()
        score = sum(1 for w in niche_words if w in text)
        if score > 0:
            relevant_videos.append({**v, "niche_relevance": score})

    relevant_tags.sort(key=lambda x: (x["niche_relevance"], x["total_score"]), reverse=True)
    relevant_videos.sort(key=lambda x: x["niche_relevance"], reverse=True)

    return {
        "niche": niche,
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "relevant_hashtags": relevant_tags[:20],
        "relevant_videos": relevant_videos[:10],
        "top_cross_platform_tags": [
            t for t in hashtag_result.get("hashtags", [])[:50]
            if t.get("cross_platform")
        ][:10],
        "errors": errors,
    }
