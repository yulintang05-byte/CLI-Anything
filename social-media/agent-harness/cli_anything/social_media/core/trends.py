"""Viral trend intelligence — aggregates YouTube & TikTok trending signals."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPORTS_PATH = Path.home() / ".cli-anything-social" / "trend_reports"


@dataclass
class TrendItem:
    platform: str          # "youtube" | "tiktok"
    type: str              # "video" | "hashtag" | "sound"
    title: str
    score: float           # 0–100 virality score
    views: int
    engagement: float      # engagement rate 0–1
    tags: list[str]
    url: str
    captured_at: str


def compute_virality_score(views: int, likes: int, comments: int, shares: int = 0) -> float:
    """Compute a 0–100 virality score from raw engagement metrics."""
    if views == 0:
        return 0.0
    engagement_rate = (likes + comments * 2 + shares * 3) / max(views, 1)
    view_score = min(100, (views / 1_000_000) * 50)
    eng_score = min(50, engagement_rate * 500)
    return round(min(100, view_score + eng_score), 1)


def aggregate_trends(
    yt_videos: list[dict],
    yt_hashtags: list[dict],
    yt_music: list[dict],
    tt_hashtags: list[dict],
    tt_sounds: list[dict],
    tt_videos: list[dict],
) -> dict[str, Any]:
    """Combine YouTube + TikTok trend data into a unified report."""
    now = datetime.now(timezone.utc).isoformat()
    items: list[TrendItem] = []

    for v in yt_videos:
        items.append(TrendItem(
            platform="youtube",
            type="video",
            title=v.get("title", ""),
            score=compute_virality_score(
                v.get("views", 0), v.get("likes", 0), v.get("comments", 0)
            ),
            views=v.get("views", 0),
            engagement=(v.get("likes", 0) + v.get("comments", 0)) / max(v.get("views", 1), 1),
            tags=v.get("tags", []),
            url=v.get("url", ""),
            captured_at=now,
        ))

    for h in yt_hashtags:
        items.append(TrendItem(
            platform="youtube",
            type="hashtag",
            title=h.get("hashtag", ""),
            score=min(100, h.get("score", 0) * 10),
            views=h.get("total_views", 0),
            engagement=0.0,
            tags=[h.get("hashtag", "").lstrip("#")],
            url=f"https://www.youtube.com/hashtag/{h.get('hashtag','').lstrip('#')}",
            captured_at=now,
        ))

    for t in tt_hashtags:
        vc = t.get("view_count") or 0
        items.append(TrendItem(
            platform="tiktok",
            type="hashtag",
            title=t.get("hashtag", ""),
            score=min(100, (vc / 1_000_000_000) * 100) if vc else 50.0,
            views=vc,
            engagement=0.0,
            tags=[t.get("hashtag", "").lstrip("#")],
            url=f"https://www.tiktok.com/tag/{t.get('hashtag','').lstrip('#')}",
            captured_at=now,
        ))

    for s in tt_sounds:
        items.append(TrendItem(
            platform="tiktok",
            type="sound",
            title=f"{s.get('title', '')} – {s.get('author', '')}",
            score=min(100, (s.get("video_count", 0) / 1_000_000) * 50),
            views=s.get("video_count", 0),
            engagement=0.0,
            tags=[],
            url="",
            captured_at=now,
        ))

    for v in tt_videos:
        items.append(TrendItem(
            platform="tiktok",
            type="video",
            title=v.get("description", "")[:80],
            score=compute_virality_score(
                v.get("plays", 0), v.get("likes", 0), v.get("comments", 0), v.get("shares", 0)
            ),
            views=v.get("plays", 0),
            engagement=(v.get("likes", 0) + v.get("comments", 0)) / max(v.get("plays", 1), 1),
            tags=v.get("hashtags", []),
            url=v.get("url", ""),
            captured_at=now,
        ))

    items.sort(key=lambda x: x.score, reverse=True)

    # Extract cross-platform hashtag overlap (signal amplification opportunities)
    yt_tags = {h.get("hashtag", "").lstrip("#").lower() for h in yt_hashtags}
    tt_tags = {t.get("hashtag", "").lstrip("#").lower() for t in tt_hashtags}
    cross_platform = sorted(yt_tags & tt_tags)

    return {
        "generated_at": now,
        "item_count": len(items),
        "top_viral": [asdict(i) for i in items[:20]],
        "youtube": {
            "trending_videos": yt_videos[:10],
            "trending_hashtags": yt_hashtags[:15],
            "trending_music": yt_music[:10],
        },
        "tiktok": {
            "trending_hashtags": tt_hashtags[:15],
            "trending_sounds": tt_sounds[:10],
            "trending_videos": tt_videos[:10],
        },
        "cross_platform_hashtags": cross_platform,
        "insight": _generate_insight(items, cross_platform),
    }


def _generate_insight(items: list[TrendItem], cross_platform: list[str]) -> dict:
    """Summarize actionable insights from trend data."""
    top_tags: dict[str, int] = {}
    for item in items:
        for tag in item.tags:
            t = tag.lower().strip()
            if t:
                top_tags[t] = top_tags.get(t, 0) + 1

    hot_tags = sorted(top_tags.items(), key=lambda x: x[1], reverse=True)[:10]

    yt_items = [i for i in items if i.platform == "youtube"]
    tt_items = [i for i in items if i.platform == "tiktok"]

    avg_yt = sum(i.score for i in yt_items) / max(len(yt_items), 1)
    avg_tt = sum(i.score for i in tt_items) / max(len(tt_items), 1)

    return {
        "hottest_tags": [{"tag": f"#{t}", "frequency": c} for t, c in hot_tags],
        "cross_platform_opportunities": cross_platform[:10],
        "avg_youtube_virality": round(avg_yt, 1),
        "avg_tiktok_virality": round(avg_tt, 1),
        "recommendation": (
            "Focus on cross-platform hashtags for maximum reach. "
            + (f"YouTube trending: {yt_items[0].title[:40]!r}. " if yt_items else "")
            + (f"TikTok trending: {tt_items[0].title[:40]!r}." if tt_items else "")
        ),
    }


def save_report(report: dict, name: str | None = None) -> Path:
    _REPORTS_PATH.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"{name or 'trend_report'}_{ts}.json"
    path = _REPORTS_PATH / fname
    path.write_text(json.dumps(report, indent=2))
    return path


def load_last_report() -> dict | None:
    if not _REPORTS_PATH.exists():
        return None
    reports = sorted(_REPORTS_PATH.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not reports:
        return None
    try:
        return json.loads(reports[0].read_text())
    except Exception:
        return None


def diff_reports(old: dict, new: dict) -> dict:
    """Compute what changed between two trend reports."""
    old_titles = {i["title"] for i in old.get("top_viral", [])}
    new_titles = {i["title"] for i in new.get("top_viral", [])}

    old_tags = set(old.get("cross_platform_hashtags", []))
    new_tags = set(new.get("cross_platform_hashtags", []))

    return {
        "new_viral": list(new_titles - old_titles),
        "dropped_viral": list(old_titles - new_titles),
        "new_cross_platform_tags": list(new_tags - old_tags),
        "dropped_cross_platform_tags": list(old_tags - new_tags),
        "time_delta": _time_delta(old.get("generated_at", ""), new.get("generated_at", "")),
    }


def _time_delta(t1: str, t2: str) -> str:
    try:
        d1 = datetime.fromisoformat(t1.replace("Z", "+00:00"))
        d2 = datetime.fromisoformat(t2.replace("Z", "+00:00"))
        delta = abs((d2 - d1).total_seconds())
        if delta < 3600:
            return f"{int(delta // 60)}m"
        if delta < 86400:
            return f"{delta / 3600:.1f}h"
        return f"{delta / 86400:.1f}d"
    except Exception:
        return "unknown"
