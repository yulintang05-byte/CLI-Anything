"""Cross-platform trend analysis — aggregates and ranks trends from YouTube + TikTok."""

from datetime import datetime, timezone
from typing import Optional


def _normalize_tag(tag: str) -> str:
    return tag.lower().lstrip("#").strip()


def aggregate_hashtags(
    yt_data: Optional[dict] = None,
    tt_data: Optional[dict] = None,
    top_n: int = 30,
) -> list[dict]:
    """Merge hashtag data from both platforms and produce a unified ranked list."""
    scores: dict[str, dict] = {}

    if yt_data:
        for item in yt_data.get("hashtags", []):
            key = _normalize_tag(item["tag"])
            if key not in scores:
                scores[key] = {"tag": f"#{key}", "yt_count": 0, "tt_count": 0, "total": 0}
            scores[key]["yt_count"] += item["count"]

    if tt_data:
        for item in tt_data.get("hashtags", []):
            key = _normalize_tag(item["tag"])
            if key not in scores:
                scores[key] = {"tag": f"#{key}", "yt_count": 0, "tt_count": 0, "total": 0}
            scores[key]["tt_count"] += item["count"]

    for v in scores.values():
        # Cross-platform tags get a 2× bonus (virality multiplier)
        cross = 2 if v["yt_count"] > 0 and v["tt_count"] > 0 else 1
        v["total"] = (v["yt_count"] + v["tt_count"]) * cross
        v["cross_platform"] = cross == 2

    ranked = sorted(scores.values(), key=lambda x: x["total"], reverse=True)
    return ranked[:top_n]


def aggregate_music(
    yt_music: Optional[list] = None,
    tt_music: Optional[list] = None,
    top_n: int = 20,
) -> list[dict]:
    """Merge music trends from both platforms."""
    tracks: dict[str, dict] = {}

    if yt_music:
        for t in yt_music:
            key = _normalize_tag(t.get("track", ""))
            if key not in tracks:
                tracks[key] = {
                    "track": t.get("track", ""),
                    "artist": t.get("artist", ""),
                    "yt_url": t.get("video_url", ""),
                    "tt_video_count": 0,
                    "platforms": ["youtube"],
                }
            elif "youtube" not in tracks[key]["platforms"]:
                tracks[key]["platforms"].append("youtube")

    if tt_music:
        for m in tt_music:
            title = m.get("title", "")
            key = _normalize_tag(title)
            if key not in tracks:
                tracks[key] = {
                    "track": title,
                    "artist": m.get("author", ""),
                    "yt_url": "",
                    "tt_video_count": m.get("video_count", 0),
                    "platforms": ["tiktok"],
                }
            else:
                if "tiktok" not in tracks[key]["platforms"]:
                    tracks[key]["platforms"].append("tiktok")
                tracks[key]["tt_video_count"] = m.get("video_count", 0)

    def _score(t: dict) -> int:
        return t["tt_video_count"] * (2 if len(t["platforms"]) > 1 else 1)

    ranked = sorted(tracks.values(), key=_score, reverse=True)
    return ranked[:top_n]


def score_content_opportunity(hashtags: list[dict], music: list[dict]) -> dict:
    """
    Score content opportunities: which hashtag + sound combos are highest-value right now.
    Returns a prioritized list of content ideas.
    """
    opportunities = []

    cross_tags = [h for h in hashtags if h.get("cross_platform")]
    hot_tags = hashtags[:10]

    cross_music = [m for m in music if len(m.get("platforms", [])) > 1]
    hot_music = music[:5]

    for tag in (cross_tags or hot_tags)[:5]:
        for sound in (cross_music or hot_music)[:3]:
            opportunities.append({
                "type": "hashtag+sound",
                "hashtag": tag["tag"],
                "sound": f"{sound['artist']} - {sound['track']}",
                "score": tag["total"] + sound.get("tt_video_count", 0),
                "cross_platform": tag.get("cross_platform", False) or len(sound.get("platforms", [])) > 1,
                "recommendation": (
                    f"Create a short-form video using {tag['tag']} + "
                    f"'{sound['track']}' by {sound['artist']}. "
                    "High virality potential based on cross-platform momentum."
                ),
            })

    opportunities.sort(key=lambda x: x["score"], reverse=True)

    return {
        "top_hashtags": hot_tags[:10],
        "top_sounds": hot_music[:5],
        "content_opportunities": opportunities[:10],
        "scored_at": datetime.now(timezone.utc).isoformat(),
    }


def niche_hashtag_strategy(niche: str, hashtags: list[dict]) -> dict:
    """Filter and adapt trending hashtags for a specific niche/theme."""
    # Simple keyword matching for niche relevance
    niche_keywords = niche.lower().split()

    relevant = []
    general_viral = []

    for h in hashtags:
        tag_text = h["tag"].lower()
        if any(kw in tag_text for kw in niche_keywords):
            relevant.append({**h, "relevance": "direct"})
        elif h["total"] >= 3 or h.get("cross_platform"):
            general_viral.append({**h, "relevance": "trending_general"})

    strategy_tags = relevant[:5] + general_viral[:10]

    return {
        "niche": niche,
        "strategy": {
            "niche_specific": relevant[:5],
            "trending_general": general_viral[:10],
            "recommended_mix": strategy_tags[:15],
            "caption_template": (
                f"[Your {niche} content] "
                + " ".join(h["tag"] for h in strategy_tags[:5])
                + " #fyp #foryou #viral"
            ),
        },
        "tip": (
            "Use 3-5 niche tags + 3-5 viral tags per post. "
            "Niche tags reach your core audience; viral tags boost discovery. "
            "Rotate combinations to avoid shadowban risk."
        ),
    }
