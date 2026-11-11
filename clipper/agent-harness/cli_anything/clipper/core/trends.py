"""Trend snapshots -> hashtag/sound/caption suggestions for short-form posts.

Snapshots live in ``data/trends/YYYY-MM-DD.json``. Each one records trending
hashtags, sounds and formats for TikTok and YouTube Shorts, plus evergreen
niche tags. Trends go stale within days, so ``load_snapshot`` reports the
snapshot's age and callers should refresh when it is old.
"""

from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "trends"

PLATFORMS = ("tiktok", "youtube_shorts")

# Hashtag counts that perform best per platform (small, relevant sets beat
# walls of tags). Shorts only shows the first 3 above the title.
TAG_LIMITS = {"tiktok": 5, "youtube_shorts": 3}

STALE_AFTER_DAYS = 7


def list_snapshots(data_dir: Path = DATA_DIR) -> List[str]:
    return sorted(p.stem for p in Path(data_dir).glob("*.json"))


def load_snapshot(date: Optional[str] = None, data_dir: Path = DATA_DIR,
                  today: Optional[_dt.date] = None) -> Dict[str, Any]:
    snaps = list_snapshots(data_dir)
    if not snaps:
        raise FileNotFoundError(f"No trend snapshots in {data_dir}")
    name = date or snaps[-1]
    if name not in snaps:
        raise ValueError(f"No snapshot '{name}'. Available: {snaps}")
    data = json.loads((Path(data_dir) / f"{name}.json").read_text())
    today = today or _dt.date.today()
    age = (today - _dt.date.fromisoformat(data["date"])).days
    data["age_days"] = age
    data["stale"] = age > STALE_AFTER_DAYS
    return data


def _check_platform(platform: str) -> None:
    if platform not in PLATFORMS:
        raise ValueError(f"Unknown platform '{platform}'. Available: {list(PLATFORMS)}")


def suggest_hashtags(snapshot: Dict[str, Any], platform: str,
                     niche: Optional[str] = None,
                     limit: Optional[int] = None) -> List[str]:
    """Mix: platform-required tag, niche-matching trending tags, evergreen niche tags.

    Trending tags unrelated to the niche are skipped on purpose — off-topic
    trend-jacking hurts retention and can get a post shown to the wrong audience.
    """
    _check_platform(platform)
    limit = limit or TAG_LIMITS[platform]
    niche = (niche or "").lower().strip() or None
    tags: List[str] = []

    def add(t: str) -> None:
        t = t.lower()
        if t not in tags:
            tags.append(t)

    plat = snapshot.get(platform, {})
    trending = sorted(plat.get("hashtags", []),
                      key=lambda h: h.get("growth_pct") or 0, reverse=True)
    for h in trending:
        if "*" in h.get("niches", []):
            add(h["tag"])
    for h in trending:
        if niche and niche in h.get("niches", []):
            add(h["tag"])
    evergreen = snapshot.get("evergreen", {})
    for t in evergreen.get(niche or "", []):
        add(t)
    for t in evergreen.get("default", []):
        add(t)
    return tags[:limit]


def suggest_sounds(snapshot: Dict[str, Any], platform: str,
                   mood: Optional[str] = None, limit: int = 5) -> List[Dict[str, str]]:
    _check_platform(platform)
    sounds = snapshot.get(platform, {}).get("sounds", [])
    if mood:
        matched = [s for s in sounds if s.get("mood") == mood.lower()]
        sounds = matched + [s for s in sounds if s not in matched]
    return sounds[:limit]


def build_caption(hook: str, platform: str, snapshot: Dict[str, Any],
                  niche: Optional[str] = None, cta: Optional[str] = None) -> Dict[str, Any]:
    """Caption = hook line + optional CTA + hashtags. Hook comes first because
    only the first ~80 characters show before 'more'."""
    tags = suggest_hashtags(snapshot, platform, niche)
    if cta is None:
        cta = "Follow for part 2" if platform == "tiktok" else "Subscribe for more"
    lines = [hook.strip()]
    if cta:
        lines.append(cta.strip())
    caption = "\n".join(lines) + "\n" + " ".join(tags)
    return {
        "platform": platform,
        "caption": caption,
        "hashtags": tags,
        "sounds": suggest_sounds(snapshot, platform),
        "snapshot_date": snapshot.get("date"),
        "stale": snapshot.get("stale", False),
    }
