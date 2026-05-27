"""Hashtag extraction, ranking, and trend scoring."""
from __future__ import annotations
import re
from collections import Counter
from typing import Any

try:
    from pytrends.request import TrendReq
    _PYTRENDS_AVAILABLE = True
except ImportError:
    _PYTRENDS_AVAILABLE = False


def extract_hashtags(items: list[dict[str, Any]]) -> list[str]:
    """Extract all hashtags from a list of trend records (YouTube + TikTok)."""
    tags: list[str] = []
    for item in items:
        # TikTok direct hashtags list
        for h in item.get("hashtags", []):
            if h:
                tags.append(h.lower().lstrip("#"))
        # Parse from description text
        for desc_field in ("description", "title", "description_snippet"):
            text = item.get(desc_field, "") or ""
            tags.extend(_parse_inline_hashtags(text))
    return tags


def _parse_inline_hashtags(text: str) -> list[str]:
    return [m.lower() for m in re.findall(r"#(\w+)", text)]


def rank_hashtags(
    items: list[dict[str, Any]],
    top_n: int = 30,
    weight_engagement: bool = True,
) -> list[dict[str, Any]]:
    """
    Rank hashtags by frequency and (optionally) weighted by engagement.

    Returns list of {tag, count, score, engagement_weighted} dicts sorted desc.
    """
    freq: Counter[str] = Counter()
    eng: Counter[str] = Counter()

    for item in items:
        all_tags: list[str] = []
        for h in item.get("hashtags", []):
            if h:
                all_tags.append(h.lower().lstrip("#"))
        for field in ("description", "title", "description_snippet"):
            text = item.get(field, "") or ""
            all_tags.extend(_parse_inline_hashtags(text))

        engagement = (
            item.get("likes", 0)
            + item.get("comments", 0) * 3
            + item.get("shares", 0) * 5
            + (item.get("plays", 0) or 0) // 1000
        )
        # YouTube proxy: parse view count string
        if not engagement and item.get("views"):
            engagement = _parse_view_count(item["views"])

        seen = set()
        for tag in all_tags:
            freq[tag] += 1
            if tag not in seen:
                eng[tag] += engagement
                seen.add(tag)

    if not freq:
        return []

    max_eng = max(eng.values()) or 1
    max_freq = max(freq.values()) or 1

    ranked = []
    for tag, count in freq.most_common(top_n):
        eng_norm = eng[tag] / max_eng
        freq_norm = count / max_freq
        score = round(0.4 * freq_norm + 0.6 * eng_norm, 4) if weight_engagement else round(freq_norm, 4)
        ranked.append(
            {
                "tag": f"#{tag}",
                "count": count,
                "engagement_score": round(eng[tag]),
                "viral_score": score,
            }
        )

    ranked.sort(key=lambda x: x["viral_score"], reverse=True)
    return ranked[:top_n]


def _parse_view_count(views_str: str) -> int:
    """Parse '1.2M views' → 1200000."""
    s = views_str.replace(",", "").strip()
    m = re.search(r"([\d.]+)\s*([KMB]?)", s, re.I)
    if not m:
        return 0
    num = float(m.group(1))
    suffix = m.group(2).upper()
    mult = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}.get(suffix, 1)
    return int(num * mult)


def get_google_trends(keywords: list[str], timeframe: str = "now 7-d") -> dict[str, Any]:
    """Query Google Trends for keyword interest over time (requires pytrends)."""
    if not _PYTRENDS_AVAILABLE:
        return {"error": "pytrends not installed. Run: pip install pytrends"}
    if not keywords:
        return {"error": "no keywords provided"}

    try:
        pt = TrendReq(hl="en-US", tz=360)
        pt.build_payload(keywords[:5], timeframe=timeframe)
        df = pt.interest_over_time()
        if df.empty:
            return {"keywords": keywords, "data": []}
        return {
            "keywords": keywords,
            "timeframe": timeframe,
            "data": df.drop(columns=["isPartial"], errors="ignore").tail(7).to_dict(orient="records"),
        }
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}
