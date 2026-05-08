"""Account optimization engine.

Generates actionable checklists, posting schedules, and bio/profile
recommendations for TikTok and YouTube accounts based on niche.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Platform = Literal["tiktok", "youtube", "instagram", "all"]


@dataclass
class OptimizationItem:
    category: str
    action: str
    priority: Literal["critical", "high", "medium", "low"]
    impact: str
    done: bool = False

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "action": self.action,
            "priority": self.priority,
            "impact": self.impact,
            "done": self.done,
        }


@dataclass
class PostingSlot:
    day: str
    time_utc: str
    local_note: str
    engagement_score: float    # 0-10 estimated engagement multiplier

    def to_dict(self) -> dict:
        return {
            "day": self.day,
            "time_utc": self.time_utc,
            "local_note": self.local_note,
            "engagement_score": self.engagement_score,
        }


# ── Optimal posting schedules ─────────────────────────────────────────────────

_TIKTOK_SCHEDULE: list[PostingSlot] = [
    PostingSlot("Tuesday",   "06:00", "6 AM EST / 3 AM PST", 9.2),
    PostingSlot("Thursday",  "09:00", "9 AM EST / 6 AM PST", 9.0),
    PostingSlot("Friday",    "05:00", "5 AM EST / 2 AM PST", 8.8),
    PostingSlot("Monday",    "12:00", "12 PM EST / 9 AM PST", 8.5),
    PostingSlot("Wednesday", "19:00", "7 PM EST / 4 PM PST", 8.4),
    PostingSlot("Saturday",  "11:00", "11 AM EST / 8 AM PST", 8.2),
    PostingSlot("Sunday",    "16:00", "4 PM EST / 1 PM PST", 7.9),
]

_YOUTUBE_SCHEDULE: list[PostingSlot] = [
    PostingSlot("Friday",    "15:00", "3 PM EST / 12 PM PST", 9.5),
    PostingSlot("Thursday",  "15:00", "3 PM EST / 12 PM PST", 9.1),
    PostingSlot("Wednesday", "15:00", "3 PM EST / 12 PM PST", 8.9),
    PostingSlot("Saturday",  "09:00", "9 AM EST / 6 AM PST",  8.6),
    PostingSlot("Tuesday",   "14:00", "2 PM EST / 11 AM PST", 8.3),
    PostingSlot("Monday",    "14:00", "2 PM EST / 11 AM PST", 8.0),
    PostingSlot("Sunday",    "14:00", "2 PM EST / 11 AM PST", 7.8),
]

_INSTAGRAM_SCHEDULE: list[PostingSlot] = [
    PostingSlot("Wednesday", "11:00", "11 AM EST / 8 AM PST", 9.3),
    PostingSlot("Friday",    "10:00", "10 AM EST / 7 AM PST", 9.0),
    PostingSlot("Tuesday",   "11:00", "11 AM EST / 8 AM PST", 8.7),
    PostingSlot("Thursday",  "14:00", "2 PM EST / 11 AM PST", 8.5),
    PostingSlot("Monday",    "09:00", "9 AM EST / 6 AM PST",  8.2),
    PostingSlot("Saturday",  "08:00", "8 AM EST / 5 AM PST",  7.9),
    PostingSlot("Sunday",    "11:00", "11 AM EST / 8 AM PST", 7.7),
]


def get_posting_schedule(platform: str) -> list[PostingSlot]:
    """Return optimal posting schedule sorted by engagement score."""
    p = platform.lower()
    if p == "youtube":
        return sorted(_YOUTUBE_SCHEDULE, key=lambda s: s.engagement_score, reverse=True)
    if p == "instagram":
        return sorted(_INSTAGRAM_SCHEDULE, key=lambda s: s.engagement_score, reverse=True)
    return sorted(_TIKTOK_SCHEDULE, key=lambda s: s.engagement_score, reverse=True)


# ── Optimization checklists ───────────────────────────────────────────────────

def _tiktok_checklist(niche: str) -> list[OptimizationItem]:
    return [
        # Profile
        OptimizationItem("Profile", "Use a high-quality, well-lit profile photo or brand logo", "critical", "First impression — affects follow rate by ~30%"),
        OptimizationItem("Profile", f"Set username to include niche keyword (e.g. @{niche.lower()}tips or @{niche.lower()}daily)", "critical", "Keyword in username improves discoverability in search"),
        OptimizationItem("Profile", f"Write a bio under 80 chars: WHO you help + HOW + niche hook for {niche}", "critical", "Clear value prop lifts follow-through rate"),
        OptimizationItem("Profile", "Add a link-in-bio (Linktree or direct) if monetised", "high", "Drives off-platform conversions"),
        OptimizationItem("Profile", "Switch to Creator or Business account for analytics", "high", "Unlocks Analytics, LIVE gifts, TikTok Shop"),
        # Content
        OptimizationItem("Content", "Hook in first 1-2 seconds: text overlay + strong visual/audio", "critical", "Retention drop-off is highest in first 3s — hook keeps viewers"),
        OptimizationItem("Content", "Post at optimal times (see `account schedule` command)", "high", "Timing affects initial distribution 2-5x"),
        OptimizationItem("Content", "Use trending sounds from TikTok Creative Center", "high", "Trending audio boosts FYP push by algorithm"),
        OptimizationItem("Content", "Add 3-5 targeted hashtags (not 30 generic ones)", "high", "Fewer, precise hashtags outperform spam sets"),
        OptimizationItem("Content", f"Create a series format specific to {niche} (Part 1, 2, 3…)", "high", "Series drives profile visits + follows"),
        OptimizationItem("Content", "Use captions (text overlay) — 80% watch without sound", "medium", "Captions increase watch-time and accessibility"),
        OptimizationItem("Content", "Post 1-4 times per day during growth phase", "medium", "Consistency signals authority to algorithm"),
        OptimizationItem("Content", "Reply to every comment in first 30 min after posting", "high", "Comment engagement boosts distribution in early window"),
        OptimizationItem("Content", "Stitch or Duet trending content in your niche", "medium", "Piggybacks existing viral momentum"),
        # Analytics
        OptimizationItem("Analytics", "Check Analytics > Followers > Territories to confirm your region audience", "high", "Ensures posting time matches audience timezone"),
        OptimizationItem("Analytics", "Track Average Watch Time — aim for >50% retention", "critical", "Watch time is TikTok's #1 ranking signal"),
        OptimizationItem("Analytics", "Monitor Traffic Source: For You vs. Following — FYP > 60% = healthy reach", "high", "FYP distribution = viral headroom"),
        OptimizationItem("Analytics", "A/B test thumbnails (cover frames) for every video", "medium", "Cover art affects CTR on profile and FYP"),
        # Growth
        OptimizationItem("Growth", "Engage with 5-10 accounts in your niche daily (likes, comments)", "medium", "Signals to algorithm your niche affinity"),
        OptimizationItem("Growth", "Cross-post Reels version to Instagram simultaneously", "high", "Doubles distribution, same content effort"),
        OptimizationItem("Growth", "Pin 3 best-performing videos to your profile", "high", "First-impression content for new visitors"),
    ]


def _youtube_checklist(niche: str) -> list[OptimizationItem]:
    return [
        # Channel
        OptimizationItem("Channel", "Custom channel URL (requires 100 subs): @yourchannelname", "high", "Easier to share, looks more professional"),
        OptimizationItem("Channel", f"Channel art (2560×1440px banner) with clear {niche} branding", "high", "Branding consistency drives subscribe rate"),
        OptimizationItem("Channel", f"Channel description: include main keywords for {niche}, upload schedule, and value prop", "critical", "Indexed by YouTube search — affects discovery"),
        OptimizationItem("Channel", "Add channel trailer (30-90s) that auto-plays for non-subscribers", "critical", "Good trailers lift subscribe conversion by 20-40%"),
        OptimizationItem("Channel", "Set up 3-5 Playlists grouping videos by subtopic", "high", "Playlists increase session watch time (multiple videos)"),
        OptimizationItem("Channel", "Enable channel membership and Super Thanks when eligible", "medium", "Additional revenue stream"),
        # Video
        OptimizationItem("Video", f"Title: include primary keyword for {niche} in first 60 chars", "critical", "Title keyword is #1 YouTube search ranking factor"),
        OptimizationItem("Video", "Custom thumbnail: bold text + face + high-contrast colour", "critical", "CTR is YouTube's key distribution signal — thumbnails drive CTR"),
        OptimizationItem("Video", f"Description first 2 lines: repeat keyword + hook (visible without 'show more')", "critical", "Affects search snippet and early retention"),
        OptimizationItem("Video", "Add 5-8 hashtags in description (YouTube shows top 3 above title)", "high", "Hashtags enable hashtag page discovery"),
        OptimizationItem("Video", "Add cards and end screens to reduce bounce, increase session length", "high", "Keeps viewers in your ecosystem — improves ranking"),
        OptimizationItem("Video", "Upload SRT captions — or enable auto-captions + fix errors", "medium", "Captions improve SEO and accessibility"),
        OptimizationItem("Video", "First 30 seconds: deliver on title promise — no long intros", "critical", "Click-through abandonment in first 30s kills distribution"),
        # Analytics
        OptimizationItem("Analytics", "Target >40% Click-Through Rate on impressions", "critical", "CTR × Watch Time = YouTube's core ranking formula"),
        OptimizationItem("Analytics", "Target >50% Average View Duration", "critical", "AVD is the strongest signal for recommended videos"),
        OptimizationItem("Analytics", "Check 'Traffic Sources > YouTube search' for keyword gaps", "high", "Reveals untapped search demand in your niche"),
    ]


def build_checklist(platform: str, niche: str) -> list[OptimizationItem]:
    """Return full optimisation checklist for the given platform and niche."""
    p = platform.lower()
    if p in ("tiktok", "all"):
        return _tiktok_checklist(niche)
    if p == "youtube":
        return _youtube_checklist(niche)
    return _tiktok_checklist(niche) + _youtube_checklist(niche)


def generate_bio(platform: str, niche: str, handle: str = "") -> dict:
    """Generate optimised bio templates for the given niche and platform."""
    handle_str = f"@{handle.lstrip('@')} " if handle else ""

    templates: dict[str, list[str]] = {
        "tiktok": [
            f"📍 {niche.title()} tips that actually work\n✅ {niche.title()} → results in 30 days\n👇 Free guide below",
            f"Your daily dose of {niche} content 🔥\nHelping you level up your {niche} game\n⬇️ Join the community",
            f"I share everything about {niche} so you don't have to Google it 🧠\nNew videos daily ↓",
        ],
        "youtube": [
            f"Welcome! I post {niche} videos every week 🎬\nMy goal: help you master {niche} faster than I did.\n✅ Subscribe for weekly uploads.",
            f"The #{niche.lower()} channel that cuts through the noise.\nReal tips. Real results. No fluff.\nNew video every Friday.",
        ],
        "instagram": [
            f"✨ {niche.title()} content creator\n📲 Daily {niche} inspo\n🔗 Collab/DM open",
            f"🌟 Helping {niche} lovers level up\n📍 Posts daily\n👇 Follow for more",
        ],
    }

    return {
        "platform": platform,
        "niche": niche,
        "templates": templates.get(platform.lower(), templates["tiktok"]),
        "tips": [
            "Keep bio under 80 characters per line",
            "Include 1 emoji per line max",
            "End with a clear CTA (subscribe, link, DM)",
            f"Include the word '{niche}' for keyword discoverability",
        ],
    }
