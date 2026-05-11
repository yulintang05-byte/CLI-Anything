"""Account optimization engine.

Generates platform-specific action plans, profile audit checklists, and
posting-schedule recommendations for TikTok, YouTube, and Instagram.

All output is JSON-serialisable so agents can pipe the data into downstream
tools (Clipper, OBS, etc.) or feed it back to an LLM for caption generation.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

# ──────────────────────────────────────────────────────────────────────────────
# Platform-specific optimisation playbooks
# ──────────────────────────────────────────────────────────────────────────────

_PLATFORM_PLAYBOOKS: Dict[str, Dict[str, Any]] = {
    "tiktok": {
        "algorithm_signals": [
            "Completion rate (watch all the way through is the #1 signal)",
            "Re-watch rate (loop plays counted separately)",
            "Shares to external platforms (highest-weight interaction)",
            "Comments → reply engagement (replies to comments boost reach)",
            "Saves (playlist saves weighted heavily in 2024+ algo)",
            "Profile clicks after video view",
            "Stitch / Duet rate",
        ],
        "profile_checklist": [
            {"item": "Profile photo", "tip": "Clear face or brand logo; no text overlay."},
            {"item": "Username", "tip": "Under 20 chars; searchable keyword in username if possible."},
            {"item": "Bio", "tip": "3 lines max: WHO you are | WHAT value you give | CTA (link/follow)."},
            {"item": "Link in bio", "tip": "Use Linktree or Beacons; update monthly for fresh link juice."},
            {"item": "Pinned videos", "tip": "Pin your 3 best-performing or best-representative videos."},
            {"item": "Series / Playlists", "tip": "Organise content into TikTok Series for retention."},
            {"item": "Creator tools enabled", "tip": "Switch to Creator account to unlock analytics."},
            {"item": "TikTok LIVE schedule", "tip": "Go LIVE once a week minimum to boost organic reach."},
        ],
        "posting_schedule": {
            "frequency": "1-4 videos/day for growth phase; 1/day for maintenance",
            "best_times_utc": ["06:00-09:00", "12:00-14:00", "19:00-23:00"],
            "best_days": ["Tuesday", "Thursday", "Friday", "Saturday"],
            "consistency_note": "Post at the SAME 2 times daily for 30+ days to train the algorithm.",
        },
        "content_pillars": [
            "Educational/How-to (highest save rate)",
            "Entertainment/Comedy (highest share rate)",
            "Relatable/POV (highest comment rate)",
            "Trending sounds + your niche (discoverability)",
            "Behind-the-scenes (builds trust and follow rate)",
        ],
        "hook_formulas": [
            "POV: [relatable scenario]",
            "Things [niche audience] will understand …",
            "I tried [trend] for 30 days — here's what happened",
            "Stop [common mistake] — do THIS instead",
            "The [niche] tip no one talks about",
            "[Number] [niche] hacks you need RIGHT NOW",
        ],
        "growth_tactics": [
            "Reply to EVERY comment in first 30 min after posting (algo reward)",
            "Stitch or Duet viral videos in your niche (inherit their reach)",
            "Use 3-5 trending hashtags + 3-5 niche hashtags per video",
            "Add closed captions — boosts completion rate by 15-25%",
            "Post a 'part 2' when a video hits 100K+ to capture momentum",
            "Cross-post Reels simultaneously for compounded reach",
            "Collaborate with creators at 2-5x your follower count",
        ],
    },
    "youtube": {
        "algorithm_signals": [
            "Click-through rate (CTR) — thumbnail + title is the entry gate",
            "Average view duration (AVD) and percentage watched",
            "Session time (YouTube rewards content that keeps users on platform)",
            "Likes and comments in first 24 hours",
            "Shares and embed plays",
            "Subscriber conversion rate from video",
            "Return viewers percentage",
        ],
        "profile_checklist": [
            {"item": "Channel art / banner", "tip": "2560×1440px; show posting schedule and niche."},
            {"item": "Channel icon", "tip": "800×800px; brand logo or clear headshot."},
            {"item": "Channel description", "tip": "First 150 chars show in search — pack with keywords."},
            {"item": "Channel trailer", "tip": "60-90 sec trailer for non-subscribers explaining the channel."},
            {"item": "Sections / Playlists", "tip": "Organise by topic; playlists dramatically increase session time."},
            {"item": "Featured channels", "tip": "Collaborate with similar creators for mutual exposure."},
            {"item": "Channel keywords", "tip": "Set in Studio → Settings → Channel; include 5-10 keywords."},
            {"item": "End screens & cards", "tip": "Add end screens to every video to chain views."},
            {"item": "Custom thumbnails", "tip": "Bright colors, close face, large bold text, curiosity gap."},
        ],
        "posting_schedule": {
            "frequency": "2-3 videos/week for Shorts; 1-2/week for long-form",
            "best_times_utc": ["14:00-16:00", "19:00-21:00"],
            "best_days": ["Thursday", "Friday", "Saturday"],
            "consistency_note": "Upload same day(s) every week for 90 days to build subscriber habits.",
        },
        "content_pillars": [
            "How-to / Tutorial (search-evergreen, long tail)",
            "List / Top-N videos (high CTR format)",
            "Review / Comparison (high-intent search)",
            "Vlog / Day-in-life (brand/trust builder)",
            "Reaction / Commentary (trend-hijacking)",
            "Documentary / Deep dive (high AVD, prestige)",
        ],
        "title_formulas": [
            "How to [achieve result] in [timeframe] (even if [objection])",
            "I [did extreme thing] for [duration] — here's what happened",
            "[Number] [niche] mistakes that are KILLING your [result]",
            "Why [common belief] is WRONG (and what to do instead)",
            "The TRUTH about [controversial topic in niche]",
            "[Number] things I wish I knew before [relevant experience]",
        ],
        "growth_tactics": [
            "Research keywords with YouTube search autosuggest before filming",
            "Pin a comment immediately after posting to seed discussion",
            "Create a 'best of' playlist and feature it on homepage",
            "Repurpose long-form into 3-5 Shorts per video",
            "Add chapters (timestamps) — increases search discovery",
            "Respond to comments with questions to fuel algorithmic engagement",
            "Submit top videos to YouTube Partner Program creator newsletters",
        ],
    },
    "instagram": {
        "algorithm_signals": [
            "Sends (shares via DM) — the #1 signal in current Reels algo",
            "Saves — highest weight for feed posts",
            "Watch time / Replays for Reels",
            "Comments (meaningful interactions > emoji comments)",
            "Likes (lesser weight but still matters)",
            "Profile visits after Reel view",
            "Story swipe-ups and poll responses",
        ],
        "profile_checklist": [
            {"item": "Profile photo", "tip": "High-res; same as other platforms for brand consistency."},
            {"item": "Username", "tip": "Match your TikTok/YouTube handle for cross-platform discovery."},
            {"item": "Name field", "tip": "Use name + keyword (e.g. 'Jane | Fitness Coach') — this is searchable."},
            {"item": "Bio", "tip": "Niche → transformation you offer → CTA → link. Use line breaks."},
            {"item": "Link in bio", "tip": "Use multi-link tool; update when promoting new content."},
            {"item": "Story Highlights", "tip": "Create 5-7 Highlights covering FAQs, services, testimonials, content categories."},
            {"item": "Grid aesthetic", "tip": "First 9 posts should represent your brand at a glance."},
            {"item": "Creator / Business account", "tip": "Switch for access to insights and scheduling tools."},
        ],
        "posting_schedule": {
            "frequency": "3-5 Reels/week; 1 feed post/day; 5-10 Stories/day",
            "best_times_utc": ["11:00-13:00", "17:00-19:00"],
            "best_days": ["Monday", "Wednesday", "Friday"],
            "consistency_note": "Stories daily keep you top-of-mind; Reels 3x/week sustains Explore reach.",
        },
        "content_pillars": [
            "Educational carousels (highest save rate → reach booster)",
            "Reels with trending audio (Explore page discovery)",
            "Stories with polls/questions (engagement signal)",
            "User-generated content reposts (community trust)",
            "Behind-the-scenes (human connection → DMs and saves)",
        ],
        "growth_tactics": [
            "Respond to every DM and comment within 1 hour of posting",
            "Use 'Add Yours' sticker on Stories to spark chain engagement",
            "Collab posts (co-author) to appear on both audiences' feeds",
            "Pin a comment with your main call-to-action on every Reel",
            "Engage in your niche for 20 min before and after posting",
            "Repost top Stories to feed as a carousel for second-life reach",
            "Host giveaways with follow + share entry to spike follower count",
        ],
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# Cross-platform posting calendar generator
# ──────────────────────────────────────────────────────────────────────────────

_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

_WEEKLY_TEMPLATE: Dict[str, List[Dict[str, Any]]] = {
    "Monday":    [{"platform": "instagram", "type": "Reel", "note": "Educational / how-to"},
                  {"platform": "tiktok", "type": "Video", "note": "Trending audio + niche"}],
    "Tuesday":   [{"platform": "youtube", "type": "Short", "note": "Quick tip repurposed from long-form"},
                  {"platform": "tiktok", "type": "Video", "note": "POV or storytime"}],
    "Wednesday": [{"platform": "instagram", "type": "Carousel", "note": "Tips list (save bait)"},
                  {"platform": "tiktok", "type": "Video", "note": "Trending challenge + your niche"}],
    "Thursday":  [{"platform": "youtube", "type": "Long-form", "note": "Main weekly video"},
                  {"platform": "tiktok", "type": "Video", "note": "Behind-the-scenes / day-in-life"}],
    "Friday":    [{"platform": "instagram", "type": "Reel", "note": "Trending audio + lifestyle"},
                  {"platform": "tiktok", "type": "Video", "note": "Comedy or relatable skit"}],
    "Saturday":  [{"platform": "youtube", "type": "Short", "note": "Repurpose top TikTok of the week"},
                  {"platform": "tiktok", "type": "Video", "note": "Collab or Stitch / Duet"}],
    "Sunday":    [{"platform": "instagram", "type": "Stories-only", "note": "Polls / Q&A / preview upcoming week"},
                  {"platform": "tiktok", "type": "Video", "note": "Motivational / weekly reflection"}],
}


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def audit_account(
    platform: str,
    follower_count: int = 0,
    avg_views: int = 0,
    posts_per_week: float = 0,
    niche: Optional[str] = None,
) -> Dict[str, Any]:
    """Run an account health audit and return prioritised action items."""
    plat = _resolve_platform(platform)
    playbook = _PLATFORM_PLAYBOOKS[plat]

    actions: List[Dict] = []
    score = 100

    # Engagement rate estimate
    if follower_count > 0 and avg_views > 0:
        eng_rate = avg_views / follower_count
        if eng_rate < 0.05:
            actions.append({
                "priority": "HIGH",
                "action": "Boost engagement rate",
                "detail": (
                    f"Your estimated view/follower ratio is {eng_rate:.1%} — below 5% threshold. "
                    "Post more consistently, reply to all comments, and review hook strength."
                ),
            })
            score -= 20
        elif eng_rate < 0.15:
            actions.append({
                "priority": "MEDIUM",
                "action": "Improve engagement rate",
                "detail": f"View/follower ratio is {eng_rate:.1%}. Target 15%+ for strong algorithmic push.",
            })
            score -= 10

    # Posting frequency
    rec_freq = playbook["posting_schedule"]["frequency"]
    if posts_per_week < 1:
        actions.append({
            "priority": "HIGH",
            "action": "Increase posting frequency",
            "detail": f"You're posting less than once a week. Recommended: {rec_freq}",
        })
        score -= 25
    elif posts_per_week < 3 and plat == "tiktok":
        actions.append({
            "priority": "MEDIUM",
            "action": "Post more frequently on TikTok",
            "detail": f"TikTok rewards volume. Recommended: {rec_freq}",
        })
        score -= 10

    # Profile checklist items
    profile_actions = [
        {"priority": "MEDIUM", "action": f"Audit: {item['item']}", "detail": item["tip"]}
        for item in playbook["profile_checklist"]
    ]
    actions.extend(profile_actions[:3])

    # Growth tactics top 3
    for tactic in playbook["growth_tactics"][:3]:
        actions.append({"priority": "LOW", "action": "Growth tactic", "detail": tactic})

    # Deduplicate and sort
    seen_actions: set = set()
    unique_actions = []
    for a in actions:
        key = a["action"]
        if key not in seen_actions:
            seen_actions.add(key)
            unique_actions.append(a)

    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    unique_actions.sort(key=lambda a: priority_order.get(a["priority"], 3))

    return {
        "platform": plat,
        "niche": niche,
        "follower_count": follower_count,
        "avg_views": avg_views,
        "posts_per_week": posts_per_week,
        "health_score": max(0, score),
        "health_label": _score_label(score),
        "action_items": unique_actions,
        "algorithm_signals": playbook["algorithm_signals"],
        "profile_checklist": playbook["profile_checklist"],
        "posting_schedule": playbook["posting_schedule"],
    }


def get_optimization_plan(platform: str) -> Dict[str, Any]:
    """Return the full optimisation playbook for a platform."""
    plat = _resolve_platform(platform)
    return {
        "platform": plat,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        **_PLATFORM_PLAYBOOKS[plat],
    }


def get_posting_calendar(platforms: Optional[List[str]] = None) -> Dict[str, Any]:
    """Return a 7-day cross-platform content calendar."""
    target_platforms = [_resolve_platform(p) for p in (platforms or ["tiktok", "youtube", "instagram"])]

    calendar: Dict[str, List] = {}
    for day in _DAYS:
        posts = [
            post for post in _WEEKLY_TEMPLATE[day]
            if _resolve_platform(post["platform"]) in target_platforms
        ]
        calendar[day] = posts

    return {
        "platforms": target_platforms,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "calendar": calendar,
        "notes": [
            "Batch-create content 1 week ahead and schedule via Creator Studio / Later / Buffer.",
            "Repurpose every long-form video into 3-5 short clips across platforms.",
            "Track performance every Friday — double down on what worked.",
            "Rotate through all content pillars weekly to avoid algorithmic fatigue.",
        ],
    }


def get_hook_formulas(platform: str) -> Dict[str, Any]:
    """Return proven hook formulas for a platform."""
    plat = _resolve_platform(platform)
    playbook = _PLATFORM_PLAYBOOKS[plat]
    formulas_key = "hook_formulas" if "hook_formulas" in playbook else "title_formulas"
    return {
        "platform": plat,
        "formulas": playbook.get(formulas_key, []),
        "content_pillars": playbook.get("content_pillars", []),
    }


def list_platforms() -> List[str]:
    """List supported platforms."""
    return list(_PLATFORM_PLAYBOOKS.keys())


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _resolve_platform(platform: str) -> str:
    aliases = {
        "tiktok": "tiktok",
        "tt": "tiktok",
        "youtube": "youtube",
        "yt": "youtube",
        "instagram": "instagram",
        "ig": "instagram",
        "insta": "instagram",
    }
    key = aliases.get(platform.lower().strip())
    if key is None:
        valid = list(_PLATFORM_PLAYBOOKS.keys())
        raise ValueError(f"Unknown platform '{platform}'. Valid: {valid}")
    return key


def _score_label(score: int) -> str:
    if score >= 80:
        return "Excellent"
    if score >= 60:
        return "Good"
    if score >= 40:
        return "Needs Work"
    return "Critical"
