"""Account optimizer — scores trending data and generates posting recommendations."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any


# ── Posting time intelligence ────────────────────────────────────────────────

# Engagement windows (UTC hours) by platform and day bucket
# Sources: SproutSocial, Later, HootSuite meta-analyses (2024-2025)
_BEST_TIMES: dict[str, dict[str, list[int]]] = {
    "tiktok": {
        "weekday": [6, 7, 10, 19, 20, 21, 22],
        "weekend": [9, 10, 11, 12, 13, 16, 20, 21],
    },
    "youtube": {
        "weekday": [12, 13, 14, 17, 18, 19, 20],
        "weekend": [9, 10, 11, 15, 16, 17, 18, 19],
    },
    "instagram": {
        "weekday": [6, 7, 11, 12, 18, 19, 20, 21],
        "weekend": [9, 10, 11, 12, 13],
    },
}

_CADENCE: dict[str, str] = {
    "tiktok": "3-5 posts/day for rapid growth; minimum 1/day to stay in algorithm",
    "youtube": "1-3 videos/week; Shorts: 1/day",
    "instagram": "1-2 feed posts/day + 5-10 Stories/day",
}


def get_best_posting_times(platform: str) -> dict:
    p = platform.lower()
    times = _BEST_TIMES.get(p, {})
    cadence = _CADENCE.get(p, "Unknown — check platform analytics")
    now_utc = datetime.now(timezone.utc)
    is_weekend = now_utc.weekday() >= 5
    bucket = "weekend" if is_weekend else "weekday"
    best_hours = times.get(bucket, times.get("weekday", []))
    now_h = now_utc.hour
    next_slot = min(best_hours, key=lambda h: (h - now_h) % 24) if best_hours else None
    hours_until = ((next_slot - now_h) % 24) if next_slot is not None else None
    return {
        "platform": p,
        "cadence": cadence,
        "best_hours_utc": best_hours,
        "current_utc_hour": now_h,
        "next_optimal_slot_utc": next_slot,
        "hours_until_next_slot": hours_until,
    }


# ── Caption / hashtag optimizer ──────────────────────────────────────────────

_PLATFORM_HASHTAG_LIMITS = {
    "tiktok": 5,
    "youtube": 15,
    "instagram": 30,
}

_CAPTION_HOOKS = [
    "POV: {topic}",
    "Nobody is talking about this {topic} hack 👇",
    "I tried {topic} for 30 days. Here's what happened.",
    "This {topic} tip changed everything for me",
    "Wait till the end 🤯 | {topic}",
    "The honest truth about {topic}",
    "{topic} tier list (not clickbait)",
]


def generate_caption_hooks(topic: str, count: int = 5) -> list[str]:
    return [h.replace("{topic}", topic) for h in _CAPTION_HOOKS[:count]]


def build_hashtag_set(
    trending_hashtags: list[dict],
    niche_tags: list[str],
    platform: str,
    top_trending: int = 3,
) -> list[str]:
    """Blend top trending tags with niche tags, respecting platform limits."""
    limit = _PLATFORM_HASHTAG_LIMITS.get(platform.lower(), 10)
    trending = [t["hashtag"] for t in trending_hashtags[:top_trending]]
    niche = [f"#{t.lstrip('#')}" for t in niche_tags]
    combined = list(dict.fromkeys(trending + niche))
    return combined[:limit]


# ── Engagement scoring ───────────────────────────────────────────────────────

def engagement_rate(likes: int, comments: int, shares: int, views: int) -> float:
    if views == 0:
        return 0.0
    return round((likes + comments * 2 + shares * 3) / views * 100, 4)


def score_trending_videos(videos: list[dict]) -> list[dict]:
    scored = []
    for v in videos:
        v = dict(v)
        v["engagement_rate"] = engagement_rate(
            v.get("like_count", 0),
            v.get("comment_count", 0),
            v.get("share_count", 0),
            max(v.get("view_count", 1), 1),
        )
        scored.append(v)
    return sorted(scored, key=lambda x: x["engagement_rate"], reverse=True)


# ── Profile optimization checklist ──────────────────────────────────────────

_PROFILE_CHECKLIST: dict[str, list[str]] = {
    "tiktok": [
        "Bio ≤ 80 chars — lead with value prop, not your name",
        "Include 1 niche keyword in username or display name",
        "Profile photo: high-contrast face or bold logo (no text under 60px)",
        "Pin 3 best-performing videos (rotate monthly)",
        "Link in bio: use link-in-bio aggregator (Linktree, Beacons, Stan.store)",
        "Enable Creator Account for analytics access",
        "Category set to your niche (affects recommendation algorithm)",
        "Auto-captions ON — boosts watch time 10-15%",
    ],
    "youtube": [
        "Channel name: keyword-forward (e.g. 'QuickFitness' not 'JohnDoeLife')",
        "Banner art: show your upload schedule (e.g. 'New videos Tue & Fri')",
        "Channel description: 2-3 sentences, include top 3 keywords in first line",
        "Featured/trailer video: 60-90 seconds, hook in first 5s",
        "Organize playlists by topic/series — boosts session watch time",
        "Custom thumbnails on every video (CTR target: ≥ 6%)",
        "End screens on all videos (last 20 seconds)",
        "Channel keywords set in YouTube Studio > Settings > Channel",
        "Shorts tab pinned if you're posting Shorts",
    ],
    "instagram": [
        "Username: lowercase, no special chars, niche-relevant",
        "Profile photo: same as other platforms for brand recognition",
        "Bio: problem → solution → CTA (link in bio)",
        "Reels cover images: consistent color palette / template",
        "Story Highlights: organize by topic (FAQ, Results, Services, etc.)",
        "Switch to Creator or Business account for insights",
        "Keyword in name field (bold in search ranking)",
        "Post all content types: Reels, Carousels, Stories, Lives",
    ],
}


def get_profile_checklist(platform: str) -> list[str]:
    return _PROFILE_CHECKLIST.get(platform.lower(), ["Platform not yet supported."])


# ── Full optimization report ─────────────────────────────────────────────────

def generate_optimization_report(
    platform: str,
    trending_videos: list[dict],
    trending_hashtags: list[dict],
    niche_tags: list[str],
    topic: str,
) -> dict:
    scored = score_trending_videos(trending_videos)
    hashtag_set = build_hashtag_set(trending_hashtags, niche_tags, platform)
    posting = get_best_posting_times(platform)
    hooks = generate_caption_hooks(topic)
    checklist = get_profile_checklist(platform)

    return {
        "platform": platform,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "top_trending_videos": scored[:5],
        "recommended_hashtags": hashtag_set,
        "posting_schedule": posting,
        "caption_hooks": hooks,
        "profile_checklist": checklist,
        "top_hashtags_raw": trending_hashtags[:10],
    }
