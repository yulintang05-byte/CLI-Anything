"""Content scheduler — manage, preview, and export a posting calendar."""

from __future__ import annotations

import json
import csv
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SCHEDULE_PATH = Path.home() / ".cli-anything-social" / "schedule.json"


@dataclass
class ScheduledPost:
    id: str
    platform: str
    content_type: str       # "video" | "reel" | "story" | "tweet" | "short"
    caption: str
    hashtags: list[str]
    scheduled_time: str     # ISO 8601
    status: str             # "scheduled" | "posted" | "cancelled"
    niche: str = ""
    media_path: str = ""    # local file path
    trending_audio: str = ""
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _load_schedule() -> list[ScheduledPost]:
    if not _SCHEDULE_PATH.exists():
        return []
    try:
        data = json.loads(_SCHEDULE_PATH.read_text())
        return [ScheduledPost(**item) for item in data]
    except Exception:
        return []


def _save_schedule(posts: list[ScheduledPost]) -> None:
    _SCHEDULE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _SCHEDULE_PATH.write_text(json.dumps([asdict(p) for p in posts], indent=2))


def _make_id() -> str:
    import uuid
    return str(uuid.uuid4())[:8]


def add_post(
    platform: str,
    content_type: str,
    caption: str,
    scheduled_time: str,
    hashtags: list[str] | None = None,
    niche: str = "",
    media_path: str = "",
    trending_audio: str = "",
    notes: str = "",
) -> ScheduledPost:
    posts = _load_schedule()
    post = ScheduledPost(
        id=_make_id(),
        platform=platform,
        content_type=content_type,
        caption=caption,
        hashtags=hashtags or [],
        scheduled_time=scheduled_time,
        status="scheduled",
        niche=niche,
        media_path=media_path,
        trending_audio=trending_audio,
        notes=notes,
    )
    posts.append(post)
    _save_schedule(posts)
    return post


def list_posts(
    platform: str | None = None,
    status: str | None = None,
    after: str | None = None,
    before: str | None = None,
) -> list[ScheduledPost]:
    posts = _load_schedule()
    if platform:
        posts = [p for p in posts if p.platform == platform]
    if status:
        posts = [p for p in posts if p.status == status]
    if after:
        posts = [p for p in posts if p.scheduled_time >= after]
    if before:
        posts = [p for p in posts if p.scheduled_time <= before]
    return sorted(posts, key=lambda p: p.scheduled_time)


def cancel_post(post_id: str) -> bool:
    posts = _load_schedule()
    for p in posts:
        if p.id == post_id:
            p.status = "cancelled"
            _save_schedule(posts)
            return True
    return False


def mark_posted(post_id: str) -> bool:
    posts = _load_schedule()
    for p in posts:
        if p.id == post_id:
            p.status = "posted"
            _save_schedule(posts)
            return True
    return False


def export_schedule_csv(path: Path | None = None) -> Path:
    posts = _load_schedule()
    out = path or (Path.home() / ".cli-anything-social" / "schedule_export.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "id", "platform", "content_type", "caption", "hashtags",
            "scheduled_time", "status", "niche", "media_path",
            "trending_audio", "notes", "created_at",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in sorted(posts, key=lambda x: x.scheduled_time):
            row = asdict(p)
            row["hashtags"] = " ".join(row["hashtags"])
            writer.writerow(row)
    return out


def export_schedule_json(path: Path | None = None) -> Path:
    posts = _load_schedule()
    out = path or (Path.home() / ".cli-anything-social" / "schedule_export.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps([asdict(p) for p in posts], indent=2))
    return out


def get_upcoming(days: int = 7) -> list[ScheduledPost]:
    now = datetime.now(timezone.utc).isoformat()
    posts = _load_schedule()
    from datetime import timedelta
    cutoff = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
    return [
        p for p in posts
        if p.status == "scheduled" and now <= p.scheduled_time <= cutoff
    ]


def summary() -> dict:
    posts = _load_schedule()
    by_platform: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for p in posts:
        by_platform[p.platform] = by_platform.get(p.platform, 0) + 1
        by_status[p.status] = by_status.get(p.status, 0) + 1
    upcoming = get_upcoming(7)
    return {
        "total_posts": len(posts),
        "by_platform": by_platform,
        "by_status": by_status,
        "upcoming_7_days": len(upcoming),
        "next_post": upcoming[0].scheduled_time if upcoming else None,
    }
