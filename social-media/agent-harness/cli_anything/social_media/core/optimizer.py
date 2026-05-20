"""Account optimization engine — bio, posting schedule, content pillars, growth levers."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional


# ──────────────────────────────────────────────
#  Platform best-practice data (2025)
# ──────────────────────────────────────────────

PLATFORM_SPECS = {
    "tiktok": {
        "bio_limit": 80,
        "username_tips": ["short", "memorable", "niche-relevant", "no underscores if possible"],
        "best_post_times_utc": {
            "monday":    ["06:00", "10:00", "22:00"],
            "tuesday":   ["09:00", "12:00", "19:00"],
            "wednesday": ["07:00", "08:00", "23:00"],
            "thursday":  ["12:00", "15:00", "19:00"],
            "friday":    ["05:00", "13:00", "20:00"],
            "saturday":  ["11:00", "19:00", "20:00"],
            "sunday":    ["07:00", "08:00", "16:00"],
        },
        "ideal_video_length": "7-15 seconds (hook) or 60-90 seconds (value)",
        "ideal_caption_length": "100-150 characters + hashtags",
        "hashtag_count": "3-5 targeted + 2-3 discovery",
        "posting_frequency": "1-4 posts/day",
        "algorithm_signals": [
            "Watch time / completion rate (most important)",
            "Shares (2nd most weighted)",
            "Comments (engagement depth)",
            "Likes (baseline signal)",
            "Profile visits after watching",
            "Re-watches",
        ],
        "growth_tactics": [
            "Hook in first 0.5 seconds — text overlay + visual action",
            "Use trending audio within 48 hours of it going viral",
            "Stitch/Duet top creators in your niche for borrowed audience",
            "Reply to comments with video responses (huge reach boost)",
            "Post original sound clips — if it goes viral you get creator credit",
            "Go live 2-3x/week to boost algorithmic favorability",
            "Engage on 10-15 posts in your niche before posting (warm the algo)",
            "Cross-post Reels to Instagram within 24 hours of TikTok post",
        ],
    },
    "instagram": {
        "bio_limit": 150,
        "username_tips": ["professional", "consistent with other platforms", "searchable keyword"],
        "best_post_times_utc": {
            "monday":    ["08:00", "17:00"],
            "tuesday":   ["08:00", "14:00"],
            "wednesday": ["11:00", "17:00"],
            "thursday":  ["11:00", "14:00", "17:00"],
            "friday":    ["11:00", "17:00"],
            "saturday":  ["09:00", "11:00"],
            "sunday":    ["10:00", "20:00"],
        },
        "ideal_video_length": "15-30s Reels for discovery; 60-90s for saves",
        "ideal_caption_length": "150-300 characters (first line is the hook)",
        "hashtag_count": "5-15 (avoid 30 — signals spam)",
        "posting_frequency": "3-5 Reels/week + 1-2 Stories/day",
        "algorithm_signals": [
            "Saves (most important for feed)",
            "Shares (Reels discovery)",
            "Comments (relationship signal)",
            "Watch time (Reels)",
            "Profile visits",
            "Story interactions (poll/question stickers)",
        ],
        "growth_tactics": [
            "Lead with a strong hook in caption first line (shown before 'More')",
            "End every Reel with a save-worthy CTA: 'Save this for later'",
            "Use location tags for local reach",
            "Collaborate feature — co-author Reels with complementary creators",
            "Stories with polls/questions every day to boost DM conversations",
            "Respond to every comment in the first hour (golden window)",
            "Cross-promote TikTok content as Reels (remove watermark first)",
            "Pin 3 best-performing posts to profile grid",
        ],
    },
    "youtube": {
        "bio_limit": 1000,
        "username_tips": ["keyword-rich channel name", "niche-specific", "searchable"],
        "best_post_times_utc": {
            "thursday": ["17:00", "20:00"],
            "friday":   ["15:00", "21:00"],
            "saturday": ["09:00", "11:00"],
            "sunday":   ["09:00", "11:00"],
        },
        "ideal_video_length": "8-15 min (long-form), <60s (Shorts)",
        "ideal_caption_length": "500+ characters with keywords in first 150",
        "hashtag_count": "3-5 in description (YouTube specific)",
        "posting_frequency": "1-2 long-form/week + 3-5 Shorts/week",
        "algorithm_signals": [
            "Click-through rate (thumbnail + title = #1 lever)",
            "Watch time and retention",
            "Session time (keeps viewers on YouTube)",
            "Likes and comments",
            "Subscriber conversion rate",
        ],
        "growth_tactics": [
            "A/B test thumbnails using YouTube's built-in feature",
            "Put primary keyword in title within first 3 words",
            "Create playlists to boost session time",
            "End screen with subscribe button + next video",
            "Upload Shorts of key clips from long-form videos",
            "Optimize description with keyword in first 2 sentences",
            "Use chapters — improves search and retention",
            "Respond to every comment in first 24 hours",
        ],
    },
}


# ──────────────────────────────────────────────
#  Bio generator
# ──────────────────────────────────────────────

BIO_TEMPLATES = {
    "themepage": (
        "📌 {niche} inspiration daily\n"
        "💡 Tips to grow your {niche} mindset\n"
        "👇 New video every day"
    ),
    "personal_brand": (
        "Helping {audience} {outcome} 🚀\n"
        "{credibility}\n"
        "📩 DM for collabs | ⬇️ {cta}"
    ),
    "business": (
        "{what_you_do} for {audience}\n"
        "📦 {offer}\n"
        "🔗 Link below"
    ),
    "fitness": (
        "💪 {transformation_stat}\n"
        "Helping you {outcome}\n"
        "📲 Free program ⬇️"
    ),
    "finance": (
        "💰 {result_claim}\n"
        "Teaching {audience} to {outcome}\n"
        "📊 Free resources ⬇️"
    ),
}


def generate_bio(platform: str, account_type: str, **kwargs) -> dict:
    """Generate an optimized bio for a given platform and account type."""
    specs = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["tiktok"])
    template = BIO_TEMPLATES.get(account_type, BIO_TEMPLATES["themepage"])

    try:
        bio_text = template.format(**kwargs)
    except KeyError as e:
        bio_text = template  # return template if params missing

    return {
        "platform": platform,
        "account_type": account_type,
        "bio": bio_text,
        "char_limit": specs["bio_limit"],
        "char_count": len(bio_text),
        "fits": len(bio_text) <= specs["bio_limit"],
        "tips": [
            f"Keep under {specs['bio_limit']} characters",
            "Include 1 emoji per line maximum",
            "End with a clear CTA (call-to-action)",
            "Include a keyword your audience searches for",
            "Add a link-in-bio tool (Linktree, Stan.store, etc.)",
        ],
    }


# ──────────────────────────────────────────────
#  Posting schedule optimizer
# ──────────────────────────────────────────────

def get_posting_schedule(platform: str, timezone_offset: int = 0) -> dict:
    """Return optimal posting times for a platform adjusted to a UTC offset."""
    specs = PLATFORM_SPECS.get(platform)
    if specs is None:
        return {"error": f"Unknown platform '{platform}'. Options: {list(PLATFORM_SPECS.keys())}"}

    schedule = {}
    for day, times in specs["best_post_times_utc"].items():
        adjusted = []
        for t in times:
            h, m = map(int, t.split(":"))
            h = (h + timezone_offset) % 24
            adjusted.append(f"{h:02d}:{m:02d}")
        schedule[day] = adjusted

    return {
        "platform": platform,
        "timezone_offset_hours": timezone_offset,
        "schedule": schedule,
        "frequency": specs["posting_frequency"],
        "note": "These are peak engagement windows — post 30 min before for indexing buffer.",
    }


# ──────────────────────────────────────────────
#  Account audit
# ──────────────────────────────────────────────

def audit_account(
    platform: str,
    follower_count: int,
    avg_views: int,
    avg_likes: int,
    avg_comments: int,
    posting_days_per_week: int,
    has_cta_in_bio: bool = False,
    has_link_in_bio: bool = False,
) -> dict:
    """Score an account and generate a prioritized action list."""
    specs = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["tiktok"])

    # Engagement rate
    if follower_count > 0:
        er = (avg_likes + avg_comments) / follower_count * 100
    else:
        er = 0.0

    # View-to-follower ratio (virality indicator)
    vfr = avg_views / max(follower_count, 1) * 100

    score = 0
    issues = []
    wins = []
    actions = []

    # Engagement rate benchmarks
    if er >= 6:
        score += 25
        wins.append(f"Excellent engagement rate: {er:.1f}% (industry avg: 2-4%)")
    elif er >= 3:
        score += 15
        wins.append(f"Good engagement rate: {er:.1f}%")
    elif er >= 1:
        score += 5
        issues.append(f"Low engagement rate: {er:.1f}%. Focus on comment-triggering hooks.")
        actions.append("Ask a question at the end of every caption/video")
    else:
        issues.append(f"Very low engagement: {er:.1f}%. Content may not be resonating.")
        actions.append("Study top posts in your niche and model their hook style")

    # Posting frequency
    if posting_days_per_week >= 5:
        score += 20
        wins.append(f"Consistent posting: {posting_days_per_week}x/week")
    elif posting_days_per_week >= 3:
        score += 10
        wins.append(f"Moderate posting: {posting_days_per_week}x/week")
    else:
        score += 0
        issues.append(f"Low posting frequency: {posting_days_per_week}x/week")
        actions.append("Increase to at least 5 posts/week to feed the algorithm")

    # View-to-follower ratio
    if vfr >= 100:
        score += 25
        wins.append(f"Viral reach: {vfr:.0f}% view/follower ratio (content reaching non-followers)")
    elif vfr >= 30:
        score += 15
        wins.append(f"Good reach: {vfr:.0f}% view/follower ratio")
    else:
        score += 0
        issues.append(f"Low reach: only {vfr:.0f}% of followers seeing content")
        actions.append("Test trending audio + stronger thumbnail/cover images")

    # Bio quality
    if has_cta_in_bio:
        score += 10
        wins.append("Bio has a CTA")
    else:
        issues.append("No CTA in bio — losing conversion opportunities")
        actions.append("Add CTA to bio: 'Free guide ⬇️' or 'DM me GROW'")

    if has_link_in_bio:
        score += 10
        wins.append("Bio link active")
    else:
        issues.append("No link in bio — missing traffic conversion")
        actions.append("Add Linktree / Stan.store / Beacons link to bio")

    # Algorithm signals
    if score < 30:
        actions.append("Post at optimal times: " + str(specs["best_post_times_utc"].get("friday", [])))
        actions.append("Engage 15 min before + after posting (engagement bait for algo)")

    grade = "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D"

    return {
        "platform": platform,
        "score": score,
        "grade": grade,
        "metrics": {
            "followers": follower_count,
            "avg_views": avg_views,
            "avg_likes": avg_likes,
            "avg_comments": avg_comments,
            "engagement_rate_pct": round(er, 2),
            "view_to_follower_ratio_pct": round(vfr, 1),
        },
        "wins": wins,
        "issues": issues,
        "priority_actions": actions,
        "algorithm_signals": specs["algorithm_signals"],
        "growth_tactics": specs["growth_tactics"][:5],
    }


def platform_specs(platform: str) -> dict:
    specs = PLATFORM_SPECS.get(platform)
    if specs is None:
        return {"error": f"Unknown platform '{platform}'", "available": list(PLATFORM_SPECS.keys())}
    return {"platform": platform, **specs}
