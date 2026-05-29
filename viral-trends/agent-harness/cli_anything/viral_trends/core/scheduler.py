"""Viral Trends CLI - 7-day content calendar generation."""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from cli_anything.viral_trends.core.session import Session


DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
PLATFORMS = ["tiktok", "youtube", "instagram"]
CONTENT_TYPES = ["video", "reel", "short", "post", "story"]
STATUSES = ["planned", "drafted", "published"]

# Rotating hook types for auto-generation
_HOOK_ROTATION = ["curiosity", "authority", "relatability", "urgency", "controversy"]


def _parse_time(t: str) -> str:
    """Validate and normalize HH:MM time string."""
    if not re.match(r"^\d{1,2}:\d{2}$", t):
        raise ValueError(f"Invalid time '{t}'. Use HH:MM format (e.g. 19:00)")
    parts = t.split(":")
    h, m = int(parts[0]), int(parts[1])
    if not (0 <= h <= 23):
        raise ValueError(f"Hour must be 0-23, got {h}")
    if not (0 <= m <= 59):
        raise ValueError(f"Minute must be 0-59, got {m}")
    return f"{h:02d}:{m:02d}"


def _next_id(items: List[Dict], prefix: str) -> str:
    """Generate a sequential ID like sched0, sched1, ..."""
    used = {item.get("entry_id", "") for item in items}
    i = 0
    while f"{prefix}{i}" in used:
        i += 1
    return f"{prefix}{i}"


def _find_entry(workspace: Dict[str, Any], entry_id: str) -> Dict[str, Any]:
    """Find a schedule entry by ID or raise ValueError."""
    for entry in workspace.get("schedule", []):
        if entry["entry_id"] == entry_id:
            return entry
    raise ValueError(f"Schedule entry not found: '{entry_id}'")


def add_entry(
    session: Session,
    day: str,
    time: str,
    platform: str,
    content_type: str = "video",
    topic: str = "",
    hashtag_set: Optional[str] = None,
    hook_type: str = "curiosity",
    notes: str = "",
) -> Dict[str, Any]:
    """Add a single schedule entry.

    Args:
        session: Active session.
        day: Day of week (monday..sunday).
        time: Post time in HH:MM format.
        platform: tiktok, youtube, or instagram.
        content_type: video, reel, short, post, or story.
        topic: Content topic/description.
        hashtag_set: Hashtag set name from optimizer.
        hook_type: Caption hook style.
        notes: Optional notes.

    Returns:
        Dict with the created entry and success flag.
    """
    day = day.lower()
    if day not in DAYS:
        raise ValueError(f"Invalid day '{day}'. Use: {', '.join(DAYS)}")
    if platform.lower() not in PLATFORMS:
        raise ValueError(f"Invalid platform '{platform}'. Use: {', '.join(PLATFORMS)}")
    if content_type.lower() not in CONTENT_TYPES:
        raise ValueError(f"Invalid content_type '{content_type}'. Use: {', '.join(CONTENT_TYPES)}")
    if hook_type not in _HOOK_ROTATION:
        raise ValueError(f"Invalid hook_type '{hook_type}'. Use: {', '.join(_HOOK_ROTATION)}")

    parsed_time = _parse_time(time)
    workspace = session.get_project()

    entry_id = _next_id(workspace["schedule"], "sched")

    entry = {
        "entry_id": entry_id,
        "day": day,
        "time": parsed_time,
        "platform": platform.lower(),
        "content_type": content_type.lower(),
        "topic": topic,
        "hashtag_set": hashtag_set or "",
        "hook_type": hook_type,
        "status": "planned",
        "notes": notes,
        "created": datetime.now().isoformat(),
    }

    session.snapshot(f"Add schedule entry {entry_id}")
    workspace["schedule"].append(entry)

    return {"success": True, "entry": entry}


def remove_entry(session: Session, entry_id: str) -> Dict[str, Any]:
    """Remove a schedule entry by ID."""
    workspace = session.get_project()
    entry = _find_entry(workspace, entry_id)
    session.snapshot(f"Remove schedule entry {entry_id}")
    workspace["schedule"] = [e for e in workspace["schedule"] if e["entry_id"] != entry_id]
    return {"success": True, "removed": entry_id, "entry": entry}


def update_entry(session: Session, entry_id: str, **kwargs) -> Dict[str, Any]:
    """Update fields of an existing schedule entry.

    Accepted kwargs: topic, notes, hashtag_set, hook_type, status, time, platform, content_type.
    """
    workspace = session.get_project()
    entry = _find_entry(workspace, entry_id)

    allowed = {"topic", "notes", "hashtag_set", "hook_type", "status", "time", "platform", "content_type"}
    unknown = set(kwargs.keys()) - allowed
    if unknown:
        raise ValueError(f"Unknown field(s): {unknown}. Allowed: {allowed}")

    if "time" in kwargs:
        kwargs["time"] = _parse_time(kwargs["time"])
    if "platform" in kwargs and kwargs["platform"] not in PLATFORMS:
        raise ValueError(f"Invalid platform. Use: {', '.join(PLATFORMS)}")
    if "content_type" in kwargs and kwargs["content_type"] not in CONTENT_TYPES:
        raise ValueError(f"Invalid content_type. Use: {', '.join(CONTENT_TYPES)}")
    if "status" in kwargs and kwargs["status"] not in STATUSES:
        raise ValueError(f"Invalid status. Use: {', '.join(STATUSES)}")
    if "hook_type" in kwargs and kwargs["hook_type"] not in _HOOK_ROTATION:
        raise ValueError(f"Invalid hook_type. Use: {', '.join(_HOOK_ROTATION)}")

    session.snapshot(f"Update schedule entry {entry_id}")
    entry.update(kwargs)
    return {"success": True, "entry": entry}


def mark_status(session: Session, entry_id: str, status: str) -> Dict[str, Any]:
    """Set the status of a schedule entry."""
    if status not in STATUSES:
        raise ValueError(f"Invalid status '{status}'. Use: {', '.join(STATUSES)}")
    return update_entry(session, entry_id, status=status)


def list_entries(
    session: Session,
    day: Optional[str] = None,
    platform: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """List schedule entries, optionally filtered by day and/or platform."""
    workspace = session.get_project()
    entries = workspace.get("schedule", [])

    if day:
        day = day.lower()
        if day not in DAYS:
            raise ValueError(f"Invalid day '{day}'. Use: {', '.join(DAYS)}")
        entries = [e for e in entries if e.get("day") == day]

    if platform:
        platform = platform.lower()
        if platform not in PLATFORMS:
            raise ValueError(f"Invalid platform '{platform}'. Use: {', '.join(PLATFORMS)}")
        entries = [e for e in entries if e.get("platform") == platform]

    return sorted(entries, key=lambda e: (DAYS.index(e.get("day", "monday")), e.get("time", "00:00")))


def show_calendar(session: Session) -> Dict[str, List[Dict[str, Any]]]:
    """Return all entries grouped by day of week."""
    workspace = session.get_project()
    calendar: Dict[str, List] = {day: [] for day in DAYS}

    for entry in workspace.get("schedule", []):
        day = entry.get("day", "monday")
        if day in calendar:
            calendar[day].append(entry)

    for day in calendar:
        calendar[day].sort(key=lambda e: e.get("time", "00:00"))

    return calendar


def generate_week(
    session: Session,
    niche: str,
    platforms: List[str],
    posts_per_day: int = 2,
    overwrite: bool = False,
) -> Dict[str, Any]:
    """Auto-generate a 7-day content schedule from optimal posting windows.

    Args:
        session: Active session.
        niche: Content niche to optimize for.
        platforms: List of platforms to schedule for.
        posts_per_day: Number of posts per day per platform.
        overwrite: If True, clears existing schedule first.

    Returns:
        Dict with entries_created count and schedule preview.
    """
    from cli_anything.viral_trends.core.workspace import NICHES
    from cli_anything.viral_trends.core.optimizer import (
        POSTING_WINDOWS, HASHTAG_SETS, get_hashtags
    )

    if niche not in NICHES:
        raise ValueError(f"Unknown niche '{niche}'. Available: {list(NICHES.keys())}")

    for p in platforms:
        if p not in PLATFORMS:
            raise ValueError(f"Invalid platform '{p}'. Use: {', '.join(PLATFORMS)}")

    workspace = session.get_project()

    if workspace["schedule"] and not overwrite:
        raise RuntimeError(
            f"Schedule already has {len(workspace['schedule'])} entries. "
            "Use --overwrite to replace it."
        )

    if overwrite:
        session.snapshot("Clear schedule for regeneration")
        workspace["schedule"] = []

    session.snapshot(f"Generate 7-day schedule for {niche}")

    entries_created = 0

    for platform in platforms:
        platform_windows = POSTING_WINDOWS.get(platform, POSTING_WINDOWS["tiktok"])

        # Get best hashtag set for this niche+platform
        try:
            hset = get_hashtags(niche=niche, platform=platform)
            hashtag_set_name = hset["set_name"]
        except (ValueError, KeyError):
            hashtag_set_name = ""

        for day_idx, day_data in enumerate(platform_windows):
            day = day_data["day"]
            windows = sorted(day_data["windows"], key=lambda w: w["score"], reverse=True)

            for post_idx in range(posts_per_day):
                win = windows[post_idx % len(windows)]
                # Pick time = start of window
                post_time = win["start"]

                # If we need a 2nd post in the same window, offset by 30min
                if post_idx >= len(windows):
                    h, m = map(int, post_time.split(":"))
                    m = (m + 30) % 60
                    post_time = f"{h:02d}:{m:02d}"

                hook_type = _HOOK_ROTATION[(day_idx + post_idx) % len(_HOOK_ROTATION)]

                content_map = {
                    "tiktok": "video",
                    "youtube": "short" if posts_per_day > 1 else "video",
                    "instagram": "reel",
                }
                content_type = content_map.get(platform, "video")

                entry_id = _next_id(workspace["schedule"], "sched")
                entry = {
                    "entry_id": entry_id,
                    "day": day,
                    "time": post_time,
                    "platform": platform,
                    "content_type": content_type,
                    "topic": f"{niche} content — {hook_type} hook",
                    "hashtag_set": hashtag_set_name,
                    "hook_type": hook_type,
                    "status": "planned",
                    "notes": f"Auto-generated for {niche} on {platform}",
                    "created": datetime.now().isoformat(),
                }
                workspace["schedule"].append(entry)
                entries_created += 1

    calendar = show_calendar(session)
    preview = {day: len(entries) for day, entries in calendar.items()}

    return {
        "success": True,
        "niche": niche,
        "platforms": platforms,
        "entries_created": entries_created,
        "posts_per_day_per_platform": posts_per_day,
        "schedule_preview": preview,
    }
