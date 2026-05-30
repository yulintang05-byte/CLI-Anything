"""Cross-platform trend aggregation and virality scoring."""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Any


def aggregate_trends(
    youtube_data: dict | None = None,
    tiktok_data: dict | None = None,
    top_n: int = 20,
) -> dict:
    """
    Merge and rank trends from YouTube and TikTok.

    Returns a unified trend report with cross-platform hashtags,
    top music, and a virality score for each item.
    """
    combined_hashtags: dict[str, dict] = {}
    combined_music: list[dict] = []

    if youtube_data:
        for h in youtube_data.get("hashtags", []):
            tag = h["tag"].lower()
            entry = combined_hashtags.setdefault(tag, {"tag": tag, "yt_score": 0, "tt_score": 0, "platforms": []})
            entry["yt_score"] = h.get("score", 0)
            if "youtube" not in entry["platforms"]:
                entry["platforms"].append("youtube")

        for m in youtube_data.get("music", []):
            combined_music.append({**m, "platform": "youtube"})

    if tiktok_data:
        for h in tiktok_data.get("hashtags", []):
            tag = h["tag"].lower()
            entry = combined_hashtags.setdefault(tag, {"tag": tag, "yt_score": 0, "tt_score": 0, "platforms": []})
            entry["tt_score"] = h.get("score", 0)
            if "tiktok" not in entry["platforms"]:
                entry["platforms"].append("tiktok")

        for m in tiktok_data.get("music", []):
            combined_music.append({**m, "platform": "tiktok"})

    # Virality score: cross-platform presence doubles the score
    for entry in combined_hashtags.values():
        yt = entry["yt_score"]
        tt = entry["tt_score"]
        cross_platform_bonus = 2.0 if len(entry["platforms"]) > 1 else 1.0
        entry["virality_score"] = int((yt + tt) * cross_platform_bonus)
        entry["cross_platform"] = len(entry["platforms"]) > 1

    ranked_hashtags = sorted(
        combined_hashtags.values(),
        key=lambda x: x["virality_score"],
        reverse=True,
    )[:top_n]

    # Deduplicate music by title+artist
    seen_music = set()
    unique_music = []
    for m in combined_music:
        key = f"{m.get('title', '').lower()}|{m.get('artist', '').lower()}"
        if key not in seen_music:
            seen_music.add(key)
            unique_music.append(m)

    top_videos = _merge_top_videos(youtube_data, tiktok_data, top_n=10)

    return {
        "hashtags": ranked_hashtags,
        "music": unique_music[:20],
        "top_videos": top_videos,
        "cross_platform_hashtags": [h for h in ranked_hashtags if h["cross_platform"]],
        "sources": _collect_sources(youtube_data, tiktok_data),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _merge_top_videos(yt: dict | None, tt: dict | None, top_n: int) -> list[dict]:
    videos: list[dict] = []

    if yt:
        for v in yt.get("videos", [])[:top_n]:
            videos.append({
                "platform": "youtube",
                "title": v.get("title", ""),
                "channel": v.get("channel", ""),
                "view_count": v.get("view_count", 0),
                "url": v.get("url", ""),
                "hashtags": v.get("hashtags", []),
            })

    if tt:
        for v in tt.get("videos", [])[:top_n]:
            videos.append({
                "platform": "tiktok",
                "title": v.get("description", "")[:100],
                "channel": v.get("author", ""),
                "view_count": v.get("play_count", 0),
                "url": v.get("url", ""),
                "hashtags": v.get("hashtags", []),
            })

    return sorted(videos, key=lambda x: x["view_count"], reverse=True)[:top_n]


def _collect_sources(yt: dict | None, tt: dict | None) -> list[str]:
    sources = []
    if yt:
        sources.append(yt.get("source", "youtube"))
    if tt:
        sources.append(tt.get("source", "tiktok"))
    return sources


def build_hashtag_set(
    trends: dict,
    niche: str = "",
    max_tags: int = 30,
    strategy: str = "mixed",
) -> dict:
    """
    Build an optimal hashtag set for a post.

    Args:
        trends: aggregated trends dict from aggregate_trends()
        niche: your content niche (e.g. 'fitness', 'food', 'finance')
        max_tags: max hashtags to include (TikTok: 5-8, YouTube: 15-30)
        strategy: 'viral' (all big tags), 'niche' (niche-targeted), 'mixed' (recommended)

    Returns:
        dict with tiktok_set, youtube_set, instagram_set, and strategy_notes
    """
    all_tags = [h["tag"] for h in trends.get("hashtags", [])]
    cross_platform = [h["tag"] for h in trends.get("hashtags", []) if h.get("cross_platform")]
    mega_tags = ["#fyp", "#foryou", "#foryoupage", "#viral", "#trending"]

    niche_tags = _niche_hashtags(niche) if niche else []

    if strategy == "viral":
        core = (mega_tags + cross_platform + all_tags)[:max_tags]
    elif strategy == "niche":
        core = (niche_tags + cross_platform + all_tags)[:max_tags]
    else:
        # Mixed: some mega, some niche, some trending
        core = list(dict.fromkeys(
            mega_tags[:3] + niche_tags[:5] + cross_platform[:5] + all_tags[:max_tags]
        ))[:max_tags]

    tiktok_set = list(dict.fromkeys(mega_tags[:3] + niche_tags[:3] + core[:5]))[:8]
    youtube_set = list(dict.fromkeys(niche_tags[:5] + core[:20]))[:30]
    instagram_set = list(dict.fromkeys(mega_tags[:2] + niche_tags[:8] + core[:10]))[:15]

    return {
        "tiktok_set": tiktok_set,
        "youtube_set": youtube_set,
        "instagram_set": instagram_set,
        "niche": niche,
        "strategy": strategy,
        "strategy_notes": {
            "tiktok": "3-8 tags — mix 1-2 mega (#fyp), 2-3 niche, 1-2 trending",
            "youtube": "15-30 tags in description — mix broad + niche + trending",
            "instagram": "10-15 tags — 2-3 broad + niche-specific + location",
        },
    }


def _niche_hashtags(niche: str) -> list[str]:
    """Return niche-specific hashtag recommendations."""
    niche_map = {
        "fitness": ["#fitness", "#gym", "#workout", "#fitlife", "#bodybuilding", "#health", "#fitspo", "#gains"],
        "food": ["#food", "#foodie", "#cooking", "#recipe", "#foodtok", "#foodlover", "#homecooking", "#easyrecipes"],
        "finance": ["#money", "#finance", "#investing", "#stockmarket", "#crypto", "#personalfinance", "#moneytips", "#financetok"],
        "fashion": ["#fashion", "#ootd", "#style", "#streetstyle", "#outfitinspo", "#fashiontok", "#clothing"],
        "beauty": ["#beauty", "#makeup", "#skincare", "#glam", "#beautytips", "#makeuptutorial", "#skincareroutine"],
        "travel": ["#travel", "#wanderlust", "#traveltok", "#adventure", "#explore", "#travelgram", "#vacation"],
        "gaming": ["#gaming", "#gamer", "#gameplay", "#twitch", "#streamer", "#gamertok", "#esports"],
        "tech": ["#tech", "#technology", "#coding", "#programming", "#developer", "#techtok", "#ai"],
        "motivation": ["#motivation", "#mindset", "#success", "#hustle", "#entrepreneur", "#selfimprovement"],
        "comedy": ["#comedy", "#funny", "#humor", "#memes", "#relatable", "#laugh", "#lol"],
        "lifestyle": ["#lifestyle", "#dayinmylife", "#vlog", "#aesthetic", "#dailylife", "#routine"],
        "music": ["#music", "#musician", "#singer", "#producer", "#newmusic", "#musictok", "#original"],
        "business": ["#business", "#entrepreneur", "#startup", "#marketing", "#digitalmarketing", "#ecommerce"],
    }
    return niche_map.get(niche.lower(), [f"#{niche}", f"#{niche}tok"])
