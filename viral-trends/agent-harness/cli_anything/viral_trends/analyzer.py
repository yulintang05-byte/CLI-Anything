"""Cross-platform trend analysis and scoring."""
from __future__ import annotations
from collections import Counter
from typing import Any


def score_hashtag(tag: str, yt_freq: int, tt_freq: int) -> float:
    """
    Composite virality score: weights TikTok 60%, YouTube 40%.
    Returns 0-100 float.
    """
    return round((tt_freq * 0.6 + yt_freq * 0.4) * 10, 2)


def cross_platform_hashtags(
    yt_tags: list[dict],
    tt_tags: list[dict],
    top_n: int = 20,
) -> list[dict]:
    """
    Merge YouTube and TikTok hashtag frequency lists into a unified ranking.

    Each input list has dicts: {hashtag: "#foo", frequency: N}
    Returns top_n dicts: {hashtag, yt_frequency, tt_frequency, score, cross_platform}
    """
    yt_map = {d["hashtag"].lower(): d["frequency"] for d in yt_tags}
    tt_map = {d["hashtag"].lower(): d["frequency"] for d in tt_tags}
    all_tags = set(yt_map) | set(tt_map)

    scored = []
    for tag in all_tags:
        yf = yt_map.get(tag, 0)
        tf = tt_map.get(tag, 0)
        scored.append({
            "hashtag": tag,
            "yt_frequency": yf,
            "tt_frequency": tf,
            "score": score_hashtag(tag, yf, tf),
            "cross_platform": yf > 0 and tf > 0,
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n]


def trending_music_report(tt_sounds: list[dict]) -> list[dict]:
    """
    Format TikTok sound data into a clean report.
    Adds a virality tier: hot (freq>=5), rising (2-4), emerging (1).
    """
    result = []
    for s in tt_sounds:
        freq = s.get("frequency", 0)
        if freq >= 5:
            tier = "hot"
        elif freq >= 2:
            tier = "rising"
        else:
            tier = "emerging"
        result.append({**s, "tier": tier})
    return result


def niche_opportunity_tags(
    yt_tags: list[dict],
    tt_tags: list[dict],
    max_yt_freq: int = 3,
    min_tt_freq: int = 2,
) -> list[dict]:
    """
    Find tags that are viral on TikTok but not yet saturated on YouTube.
    These represent untapped cross-posting opportunities.
    """
    yt_map = {d["hashtag"].lower(): d["frequency"] for d in yt_tags}
    tt_map = {d["hashtag"].lower(): d["frequency"] for d in tt_tags}

    opportunities = []
    for tag, tf in tt_map.items():
        yf = yt_map.get(tag, 0)
        if tf >= min_tt_freq and yf <= max_yt_freq:
            opportunities.append({
                "hashtag": tag,
                "tt_frequency": tf,
                "yt_frequency": yf,
                "opportunity_score": round(tf / max(yf, 1) * 10, 1),
            })

    return sorted(opportunities, key=lambda x: x["opportunity_score"], reverse=True)


def summarize_report(
    platform: str,
    top_hashtags: list[dict],
    top_music: list[dict] | None = None,
    opportunities: list[dict] | None = None,
) -> dict[str, Any]:
    """Compile all analysis into a single structured report dict."""
    report: dict[str, Any] = {
        "platform": platform,
        "top_hashtags": top_hashtags[:15],
    }
    if top_music:
        report["trending_music"] = top_music[:10]
    if opportunities:
        report["niche_opportunities"] = opportunities[:10]
    return report
