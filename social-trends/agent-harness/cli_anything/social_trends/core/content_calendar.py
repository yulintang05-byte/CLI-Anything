"""Social Trends - Content calendar generation and management."""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from cli_anything.social_trends.core.session import Session

CONTENT_TYPES = [
    "trending_repost",
    "original_video",
    "tutorial",
    "behind_scenes",
    "motivation_quote",
    "product_review",
    "compilation",
    "qa_session",
    "duet_stitch",
    "trend_participate",
]

OPTIMAL_TIMES: Dict[str, List[str]] = {
    "tiktok":    ["7:00 AM", "12:00 PM", "7:00 PM", "9:00 PM"],
    "instagram": ["6:00 AM", "12:00 PM", "7:00 PM"],
    "youtube":   ["2:00 PM", "5:00 PM"],
    "twitter":   ["8:00 AM", "12:00 PM", "5:00 PM", "9:00 PM"],
    "facebook":  ["1:00 PM", "3:00 PM"],
}


def generate_calendar(
    session: Session,
    platform: str,
    niche: str,
    weeks: int = 4,
    posts_per_day: int = 2,
) -> Dict[str, Any]:
    """Generate a content calendar for the specified platform and niche."""
    project = session.get_project()

    times = OPTIMAL_TIMES.get(platform.lower(), OPTIMAL_TIMES["tiktok"])
    entries: List[Dict[str, Any]] = []

    base = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # Start from next day
    base = base + timedelta(days=1)

    content_pillar_cycle = _get_pillars(niche)
    hashtag_sets = project.get("hashtag_sets", [])
    trending = project.get("trends", [])

    for day in range(weeks * 7):
        date = base + timedelta(days=day)
        date_str = date.strftime("%Y-%m-%d")
        day_name = date.strftime("%A")

        # Skip Sundays for YouTube (lower performance)
        if platform.lower() == "youtube" and day_name == "Sunday":
            continue

        day_posts = min(posts_per_day, len(times))
        for i in range(day_posts):
            pillar_index = (day * posts_per_day + i) % len(content_pillar_cycle)
            pillar = content_pillar_cycle[pillar_index]

            content_type = _pick_content_type(day, i, platform)
            time_slot = times[i % len(times)]

            # Suggest trending content if available
            trend_suggestion = None
            if content_type == "trending_repost" and trending:
                trend_suggestion = _pick_trend(trending, niche, day)

            # Suggest hashtag set
            hashtag_set = None
            for hs in hashtag_sets:
                if hs.get("platform") == platform:
                    hashtag_set = hs.get("caption_ready", "")
                    break

            entry: Dict[str, Any] = {
                "id": str(uuid.uuid4())[:8],
                "date": date_str,
                "day_of_week": day_name,
                "time": time_slot,
                "platform": platform,
                "niche": niche,
                "content_pillar": pillar,
                "content_type": content_type,
                "status": "planned",
                "title": f"[{pillar}] {content_type.replace('_', ' ').title()}",
                "notes": _content_note(content_type, niche, pillar),
                "hashtags": hashtag_set or "",
                "trend_reference": trend_suggestion,
            }
            entries.append(entry)

    session.snapshot(f"generate {weeks}-week calendar for {platform}")
    project.setdefault("calendar", []).extend(entries)

    return {
        "success": True,
        "platform": platform,
        "niche": niche,
        "weeks": weeks,
        "total_entries": len(entries),
        "entries_preview": entries[:7],
        "summary": {
            "posts_per_day": posts_per_day,
            "total_posts": len(entries),
            "time_slots": times,
            "content_types_used": list({e["content_type"] for e in entries}),
        },
    }


def view_calendar(
    session: Session,
    platform: Optional[str] = None,
    status: Optional[str] = None,
    week: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """View calendar entries, optionally filtered."""
    project = session.get_project()
    entries = project.get("calendar", [])

    if platform:
        entries = [e for e in entries if e.get("platform") == platform]
    if status:
        entries = [e for e in entries if e.get("status") == status]
    if week is not None:
        base = datetime.now()
        start = base + timedelta(weeks=week)
        end = start + timedelta(weeks=1)
        entries = [
            e for e in entries
            if _in_date_range(e.get("date", ""), start, end)
        ]

    return sorted(entries, key=lambda e: (e.get("date", ""), e.get("time", "")))


def add_calendar_entry(
    session: Session,
    date: str,
    platform: str,
    content_type: str,
    title: str,
    niche: str = "",
    hashtags: str = "",
    notes: str = "",
    time: str = "12:00 PM",
) -> Dict[str, Any]:
    """Add a manual calendar entry."""
    project = session.get_project()

    if content_type not in CONTENT_TYPES:
        raise ValueError(f"Unknown content type '{content_type}'. Valid: {CONTENT_TYPES}")

    entry: Dict[str, Any] = {
        "id": str(uuid.uuid4())[:8],
        "date": date,
        "day_of_week": "",
        "time": time,
        "platform": platform,
        "niche": niche,
        "content_type": content_type,
        "title": title,
        "status": "planned",
        "hashtags": hashtags,
        "notes": notes,
        "trend_reference": None,
    }

    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        entry["day_of_week"] = dt.strftime("%A")
    except ValueError:
        pass

    session.snapshot(f"add calendar entry {date}")
    project.setdefault("calendar", []).append(entry)
    return entry


def update_entry_status(
    session: Session,
    entry_id: str,
    status: str,
    notes: str = "",
) -> Dict[str, Any]:
    """Mark a calendar entry as planned/ready/posted/skipped."""
    valid = ["planned", "ready", "posted", "skipped"]
    if status not in valid:
        raise ValueError(f"Invalid status '{status}'. Valid: {valid}")

    project = session.get_project()
    for entry in project.get("calendar", []):
        if entry["id"] == entry_id:
            session.snapshot(f"update entry {entry_id} -> {status}")
            entry["status"] = status
            if notes:
                entry["notes"] = notes
            if status == "posted":
                entry["posted_at"] = datetime.now().isoformat()
            return entry

    raise ValueError(f"Entry '{entry_id}' not found.")


def export_calendar(
    session: Session,
    fmt: str = "json",
    platform: Optional[str] = None,
) -> Dict[str, Any]:
    """Export calendar in JSON, CSV, or plain-text format."""
    entries = view_calendar(session, platform=platform)

    if fmt == "json":
        return {"format": "json", "entries": entries, "count": len(entries)}

    if fmt == "csv":
        header = "id,date,day,time,platform,content_type,title,status,hashtags\n"
        rows = []
        for e in entries:
            row = ",".join([
                str(e.get(f, ""))
                for f in ["id", "date", "day_of_week", "time", "platform", "content_type", "title", "status", "hashtags"]
            ])
            rows.append(row)
        return {"format": "csv", "content": header + "\n".join(rows), "count": len(entries)}

    if fmt == "text":
        lines = []
        current_date = ""
        for e in entries:
            if e["date"] != current_date:
                current_date = e["date"]
                lines.append(f"\n=== {e['date']} ({e.get('day_of_week', '')}) ===")
            lines.append(
                f"  [{e['time']}] {e['platform'].upper()} | {e['content_type']} | {e['title']} [{e['status']}]"
            )
            if e.get("hashtags"):
                lines.append(f"    Tags: {e['hashtags'][:80]}...")
        return {"format": "text", "content": "\n".join(lines), "count": len(entries)}

    raise ValueError(f"Unknown format '{fmt}'. Valid: json, csv, text")


def _get_pillars(niche: str) -> List[str]:
    from cli_anything.social_trends.core.theme_pages import THEME_PAGE_NICHES
    niche_key = niche.lower().replace(" ", "_").replace("-", "_")
    data = THEME_PAGE_NICHES.get(niche_key)
    if data:
        return data["content_pillars"]
    return ["Educational", "Entertainment", "Inspiration", "Product Showcase", "Behind the Scenes"]


def _pick_content_type(day: int, slot: int, platform: str) -> str:
    # Rotate through types with platform-appropriate weighting
    rotation = [
        "trending_repost",
        "original_video",
        "trending_repost",
        "tutorial",
        "trending_repost",
        "motivation_quote",
        "trending_repost",
        "compilation",
        "trending_repost",
        "duet_stitch" if platform == "tiktok" else "product_review",
    ]
    return rotation[(day * 2 + slot) % len(rotation)]


def _pick_trend(trends: List[Dict[str, Any]], niche: str, day: int) -> Optional[Dict[str, str]]:
    niche_lower = niche.lower()
    relevant = [
        t for t in trends
        if niche_lower in t.get("title", "").lower() or
           niche_lower in " ".join(t.get("hashtags", [])).lower()
    ]
    if not relevant:
        relevant = sorted(trends, key=lambda t: t.get("view_count", 0), reverse=True)

    if not relevant:
        return None

    t = relevant[day % len(relevant)]
    return {
        "title": t.get("title", ""),
        "platform": t.get("platform", ""),
        "views": t.get("view_count", 0),
        "video_id": t.get("video_id", ""),
    }


def _content_note(content_type: str, niche: str, pillar: str) -> str:
    notes = {
        "trending_repost": f"Find a viral {niche} video about '{pillar}'. Add text overlay + credit creator.",
        "original_video": f"Create original content about '{pillar}'. Hook in first 3 seconds.",
        "tutorial": f"Step-by-step tutorial on '{pillar}'. Use clear text overlays.",
        "motivation_quote": f"Design a quote graphic in your niche style. Use trending sound.",
        "compilation": f"Compile 3-5 clips about '{pillar}'. Keep under 60 seconds.",
        "duet_stitch": f"Duet or Stitch a viral {niche} creator's content about '{pillar}'.",
        "product_review": f"Review or showcase a product related to '{pillar}'.",
        "trend_participate": f"Join current trending challenge or sound in {niche} context.",
        "behind_scenes": f"Show your content creation process for '{pillar}' content.",
        "qa_session": f"Answer top questions about '{pillar}' in your niche.",
    }
    return notes.get(content_type, f"Create content about '{pillar}'.")


def _in_date_range(date_str: str, start: datetime, end: datetime) -> bool:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return start <= dt < end
    except ValueError:
        return False
