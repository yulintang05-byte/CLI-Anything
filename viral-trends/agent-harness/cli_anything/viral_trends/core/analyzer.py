"""Trend analyzer — aggregates hashtags, music, and engagement signals from scraped data."""

from collections import Counter
from typing import Any


def extract_hashtags(videos: list[dict], top: int = 30) -> list[dict]:
    """Extract and rank hashtags from a list of scraped videos."""
    counter: Counter = Counter()
    view_weight: dict[str, int] = {}

    for v in videos:
        for tag in v.get("hashtags", []):
            t = tag.lower().lstrip("#")
            if not t or len(t) < 2:
                continue
            counter[t] += 1
            view_weight[t] = view_weight.get(t, 0) + (v.get("views") or 0)

    ranked = sorted(counter.keys(), key=lambda t: (counter[t], view_weight.get(t, 0)), reverse=True)
    return [
        {
            "hashtag": f"#{t}",
            "frequency": counter[t],
            "total_views": view_weight.get(t, 0),
            "score": counter[t] * 0.7 + (view_weight.get(t, 0) / 1_000_000) * 0.3,
        }
        for t in ranked[:top]
    ]


def extract_music(videos: list[dict], top: int = 20) -> list[dict]:
    """Extract and rank trending music from scraped videos."""
    music_map: dict[str, dict] = {}

    for v in videos:
        m = v.get("music")
        if not m or not isinstance(m, dict):
            continue
        track = m.get("track", "").strip()
        artist = m.get("artist", "").strip()
        if not track:
            continue
        key = f"{track}|{artist}".lower()
        if key in music_map:
            music_map[key]["use_count"] += 1
            music_map[key]["total_views"] += v.get("views") or 0
        else:
            music_map[key] = {
                "track": track,
                "artist": artist or "Unknown",
                "use_count": 1,
                "total_views": v.get("views") or 0,
                "platform": v.get("platform", ""),
            }

    ranked = sorted(music_map.values(), key=lambda x: (x["use_count"], x["total_views"]), reverse=True)
    return ranked[:top]


def engagement_score(v: dict) -> float:
    """Compute a normalized engagement score (0-100) for a video."""
    views = max(v.get("views") or 1, 1)
    likes = v.get("likes") or 0
    comments = v.get("comments") or 0
    shares = v.get("shares") or 0
    # Weighted engagement rate capped at 100
    rate = ((likes * 1.0 + comments * 2.0 + shares * 3.0) / views) * 100
    return round(min(rate, 100.0), 2)


def summarize_trends(videos: list[dict]) -> dict:
    """Produce a high-level trend summary from a mixed list of scraped videos."""
    if not videos:
        return {"error": "No video data to analyze"}

    platforms = Counter(v.get("platform", "unknown") for v in videos)
    all_views = [v.get("views") or 0 for v in videos if v.get("views")]
    avg_views = int(sum(all_views) / len(all_views)) if all_views else 0

    top_hashtags = extract_hashtags(videos, top=15)
    top_music = extract_music(videos, top=10)

    scores = [(v, engagement_score(v)) for v in videos]
    scores.sort(key=lambda x: x[1], reverse=True)
    top_videos = [
        {
            "title": v["title"][:80],
            "channel": v.get("channel", ""),
            "views": v.get("views", 0),
            "engagement_score": s,
            "url": v.get("url", ""),
            "platform": v.get("platform", ""),
            "hashtags": v.get("hashtags", [])[:5],
        }
        for v, s in scores[:10]
    ]

    return {
        "total_analyzed": len(videos),
        "platforms": dict(platforms),
        "avg_views": avg_views,
        "top_hashtags": top_hashtags,
        "top_music": top_music,
        "top_videos_by_engagement": top_videos,
        "recommended_hashtags": [h["hashtag"] for h in top_hashtags[:10]],
        "recommended_music": [
            f"{m['track']} — {m['artist']}" for m in top_music[:5]
        ],
    }
