"""Account optimization logic for TikTok, YouTube, and Instagram."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


# Posting frequency recommendations per platform
_POSTING_SCHEDULE = {
    "tiktok": {
        "frequency": "1-4 videos per day",
        "best_times": ["7 AM", "12 PM", "7 PM", "9 PM"],
        "timezone_tip": "Post in your audience's timezone. Use TikTok Analytics > Followers tab.",
        "video_length": "15-60 s for FYP reach; 3-5 min for Watch Time / RPM",
    },
    "youtube": {
        "frequency": "3-5 Shorts/day for growth; 1-2 long-form/week for monetisation",
        "best_times": ["12 PM", "3 PM", "5 PM"],
        "timezone_tip": "Check YouTube Studio Analytics > Audience tab for your peak hours.",
        "video_length": "Shorts: under 60 s | Long-form: 8-15 min for mid-roll ads",
    },
    "instagram": {
        "frequency": "1-2 Reels/day + 3-7 Stories/day",
        "best_times": ["6 AM", "12 PM", "7 PM"],
        "timezone_tip": "Instagram Insights > Most Active Times.",
        "video_length": "Reels: 15-30 s for reach; up to 90 s for saves",
    },
}

_PROFILE_CHECKLIST = {
    "tiktok": [
        "Profile photo: high-contrast, face visible, 200×200 px minimum",
        "Bio: niche keyword in first 5 words + clear value prop + CTA",
        "Link in bio: use link-in-bio tool (Beacons, Linktree) to consolidate",
        "Username: short, memorable, niche-relevant, same across all platforms",
        "Pinned videos: 3 best-performing or intro videos pinned to top",
        "Series/Playlists: group related content so viewers binge-watch",
        "LIVE eligibility: 1k+ followers unlocks LIVE; use it weekly for retention",
    ],
    "youtube": [
        "Channel art: 2560×1440 px banner with niche/value prop",
        "Profile photo: consistent with other platforms",
        "Channel description: keyword-rich first 2 lines (shown in search)",
        "Channel trailer: 60-90 s hook video for non-subscribers",
        "Featured video: different from trailer — show best content to subscribers",
        "Playlists: organise by topic; increases session time",
        "End screens + cards on every video pointing to subscribe / next video",
        "Community tab (500+ subs): post polls weekly to spike engagement",
        "Chapters in description: improves search impressions",
        "Custom thumbnails: face + bold text + high contrast; A/B test via YouTube Studio",
    ],
    "instagram": [
        "Business / Creator account: required for analytics + monetisation",
        "Username match: same as TikTok / YouTube handle",
        "Bio: niche keyword + emoji bullets + CTA + link in bio",
        "Highlight covers: branded, consistent colour palette",
        "Reels cover images: bright, text overlay so they stand out on grid",
        "Grid aesthetic: consistent filter / colour grade for theme pages",
        "Story engagement: polls, questions, quizzes daily — raise DM rate",
        "Collab posts: partner with accounts in same niche for cross-reach",
    ],
}

_SEO_TIPS = {
    "tiktok": [
        "Say your keyword aloud in the first 3 s — TikTok's audio transcription boosts search",
        "Put primary keyword + top hashtags in caption (not stuffed, natural sentence)",
        "Add text overlay with keyword on screen within first 2 frames",
        "Use TikTok Search to find high-volume, low-competition keywords",
        "Reply to comments with video — search indexes comment-reply videos well",
    ],
    "youtube": [
        "Primary keyword in title within first 50 characters",
        "Keyword in first 25 words of description + naturally throughout",
        "Custom thumbnail CTR target: >6% (check YouTube Studio Reach tab)",
        "Use VidIQ or TubeBuddy for keyword research and tag suggestions",
        "Chapters auto-create key moments in search results — add timestamps",
        "Subtitles / CC improve accessibility and indexation",
    ],
    "instagram": [
        "Use Instagram Search bar to find autocomplete hashtags — those are high-volume",
        "Alt text on posts: manually write keyword-rich alt text (Edit > Advanced Settings)",
        "Reel audio: trending audio adds a 'trending' badge and boosts distribution",
        "Keyword in caption first sentence (truncated after ~125 chars in feed)",
        "Location tags increase local discovery",
    ],
}


def get_optimization_report(platform: str) -> dict[str, Any]:
    platform = platform.lower()
    supported = list(_POSTING_SCHEDULE.keys())
    if platform not in supported:
        raise ValueError(f"Platform '{platform}' not supported. Choose: {supported}")

    return {
        "platform": platform,
        "generated_at": _now(),
        "profile_checklist": _PROFILE_CHECKLIST[platform],
        "posting_schedule": _POSTING_SCHEDULE[platform],
        "seo_tips": _SEO_TIPS[platform],
        "score_estimate": _score_platform(platform),
    }


def get_all_optimization_report() -> dict[str, Any]:
    return {
        "generated_at": _now(),
        "platforms": {p: get_optimization_report(p) for p in _POSTING_SCHEDULE},
        "cross_platform_tips": [
            "Repurpose every long-form YouTube video into 5-10 TikTok/Reels clips",
            "Keep branding consistent: same handle, colours, font across all platforms",
            "Post TikTok first (fastest algo feedback), then repost to Reels + Shorts",
            "Watermark removal: use SnapTik or similar before reposting to other platforms",
            "Schedule in batches: film 7-10 videos per session, post daily via Later/Buffer",
            "Reply to every comment in first 60 min — all algorithms reward engagement velocity",
            "Cross-promote: end TikToks with 'Full video on YouTube' to drive subscribers",
        ],
    }


def _score_platform(platform: str) -> dict:
    """Return potential reach metrics for a new account hitting benchmarks."""
    benchmarks = {
        "tiktok": {
            "day_30": "500-2k followers with 1-4 posts/day + trending audio",
            "month_3": "5k-50k followers; first viral possible at week 2-4",
            "monetisation_threshold": "10k followers (Creator Marketplace) / 1k for LIVE gifts",
        },
        "youtube": {
            "day_30": "50-500 subs with daily Shorts + 1 long-form/week",
            "month_3": "500-5k subs; Partner Program at 1k subs + 4k watch hours",
            "monetisation_threshold": "500 subs (Channel Memberships) / 1k for YPP ad revenue",
        },
        "instagram": {
            "day_30": "200-2k followers with 1-2 Reels/day + Stories",
            "month_3": "2k-20k followers; Reels Bonus (invite-only) pays per play",
            "monetisation_threshold": "Subscriptions at 10k; Brand deals from 5k niche accounts",
        },
    }
    return benchmarks[platform]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
