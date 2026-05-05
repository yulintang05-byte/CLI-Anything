"""Account optimizer — data-driven recommendations for TikTok & YouTube.

Generates a full optimization playbook for any account given platform,
niche, current stats, and posting habits. All logic is deterministic and
backed by established creator-economy best practices (2024-2025).
"""

from __future__ import annotations

from typing import Any


# Best posting times by platform (UTC-adjusted ranges, local time labels)
_BEST_TIMES: dict[str, list[str]] = {
    "tiktok": [
        "6am–8am (morning commuters)",
        "12pm–2pm (lunch scroll)",
        "7pm–10pm (prime evening)",
        "Tue/Thu/Fri perform best overall",
    ],
    "youtube": [
        "2pm–4pm (after-school / pre-work peak)",
        "6pm–9pm (primetime)",
        "Sat/Sun 10am–12pm (weekend binge)",
    ],
    "instagram": [
        "7am–9am (morning)",
        "12pm–1pm (lunch)",
        "6pm–8pm (evening)",
        "Mon/Wed/Thu historically highest engagement",
    ],
}

_POSTING_FREQUENCY: dict[str, str] = {
    "tiktok":    "3–5 videos/day for growth phase; 1–2/day for maintenance",
    "youtube":   "2–3 videos/week (Shorts: daily); consistency > volume",
    "instagram": "1 Reel/day + 3–5 Stories/day + 3–4 feed posts/week",
}

_HOOK_FORMULAS: list[str] = [
    "POV: [relatable situation]",
    "I tried [thing] for 30 days — here's what happened",
    "Nobody talks about this but...",
    "This [niche] hack changed my life",
    "Stop doing [common mistake] — do this instead",
    "How I [achieved result] in [short time] with no [resource]",
    "The [superlative] [thing] I've ever seen",
    "Wait for it... 🤯",
    "[Number] things only [niche audience] understands",
    "Tell me you're a [identity] without telling me you're a [identity]",
]

_CONTENT_PILLARS: dict[str, list[str]] = {
    "fitness":    ["Workout tutorials", "Transformation content", "Nutrition tips", "Gym fails/humor", "Progress updates"],
    "fashion":    ["OOTD reveals", "Styling tips", "Haul videos", "Trend breakdowns", "Thrift flips"],
    "food":       ["Recipe walkthroughs", "Taste tests", "Kitchen hacks", "Restaurant reviews", "Meal prep"],
    "beauty":     ["GRWM (Get Ready With Me)", "Product reviews", "Transformation tutorials", "Skincare routines", "Dupes"],
    "finance":    ["Money tips", "Side hustle ideas", "Investment breakdowns", "Budget challenges", "Success stories"],
    "motivation": ["Mindset shifts", "Day-in-the-life", "Failure-to-success arcs", "Productivity hacks", "Book summaries"],
    "gaming":     ["Gameplay highlights", "Game reviews", "Tips & tricks", "Gaming setup tours", "Reaction/commentary"],
    "travel":     ["Destination guides", "Travel hacks", "Hidden gems", "Budget travel", "Day-in-the-life abroad"],
    "pets":       ["Cute clips", "Training tips", "Pet products", "Funny moments", "Pet transformations"],
    "education":  ["Quick facts", "Explainer videos", "Myth-busting", "Historical moments", "Science visuals"],
    "general":    ["Trending audios", "Challenges", "Duets/collabs", "Tutorial/how-to", "Storytelling"],
}

_MONETIZATION_PATHS: dict[str, list[str]] = {
    "tiktok": [
        "TikTok Creator Fund / Creativity Program (1M+ views/month threshold)",
        "TikTok LIVE gifts (go live daily 15-30 min)",
        "Brand deals via creator marketplace (10K+ followers)",
        "Affiliate links in bio (Amazon, ClickBank, ShareASale)",
        "Sell digital products / courses via link-in-bio",
        "Drive traffic to YouTube for higher CPM revenue",
    ],
    "youtube": [
        "YouTube Partner Program (1K subs + 4K watch hours or 10M Shorts views)",
        "Channel memberships ($1.99–$49.99/mo tiers)",
        "Super Thanks / Super Chats on livestreams",
        "Brand sponsorships (typically $20–$50 per 1K views)",
        "Affiliate marketing in descriptions",
        "Sell merchandise via YouTube Shopping",
        "Offer courses / coaching via link in description",
    ],
}


def optimize_account(
    platform: str,
    niche: str,
    followers: int = 0,
    avg_views: int = 0,
    posts_per_week: int = 0,
    goals: str = "growth",
) -> dict[str, Any]:
    """
    Generate a full account optimization playbook.

    Args:
        platform: tiktok | youtube | instagram
        niche: content niche (fitness, food, beauty, etc.)
        followers: current follower count
        avg_views: average views per post
        posts_per_week: current weekly post count
        goals: growth | monetization | engagement

    Returns optimization playbook dict.
    """
    platform = platform.lower()
    niche_key = niche.lower() if niche.lower() in _CONTENT_PILLARS else "general"

    # Engagement rate calculation
    eng_rate = (avg_views / followers * 100) if followers > 0 else 0
    eng_verdict = (
        "Excellent (above average)" if eng_rate > 10
        else "Good" if eng_rate > 5
        else "Below average — focus on hook quality and watch time"
        if followers > 0 else "N/A — build baseline audience first"
    )

    # Growth stage
    if followers < 1_000:
        stage = "Seed Stage (0–1K) — focus 100% on content quality and consistency"
    elif followers < 10_000:
        stage = "Early Growth (1K–10K) — double down on what's working, post daily"
    elif followers < 100_000:
        stage = "Mid Growth (10K–100K) — optimize hooks, collabs, and trending audio"
    elif followers < 1_000_000:
        stage = "Creator Phase (100K–1M) — monetize, brand deals, and cross-platform"
    else:
        stage = "Established Creator (1M+) — diversify revenue, build brand assets"

    # Frequency recommendation
    target_freq = _POSTING_FREQUENCY.get(platform, _POSTING_FREQUENCY["tiktok"])
    freq_gap = ""
    if platform == "tiktok" and posts_per_week < 14:
        freq_gap = f"You're posting ~{posts_per_week}x/week. TikTok rewards 3-5x/DAY during growth. Increase cadence."
    elif platform == "youtube" and posts_per_week < 2:
        freq_gap = f"You're posting ~{posts_per_week}x/week. Aim for 2-3 videos/week + daily Shorts."

    content_pillars = _CONTENT_PILLARS.get(niche_key, _CONTENT_PILLARS["general"])
    best_times = _BEST_TIMES.get(platform, _BEST_TIMES["tiktok"])
    monetization = _MONETIZATION_PATHS.get(platform, _MONETIZATION_PATHS["tiktok"])

    # Profile checklist
    profile_checklist = [
        "Profile photo: High-contrast, face clearly visible (or brand logo)",
        "Bio: State EXACTLY who you help + what you post in ≤150 chars",
        "Bio link: Use link-in-bio tool (Linktree / Stan.store / Beacons) with CTA",
        "Username: Simple, searchable, consistent across ALL platforms",
        "Pinned posts: Pin your 3 best-performing or most representative videos",
        "Profile keyword: Include your niche keyword in display name (e.g. 'John | Fitness Tips')",
    ]

    # Content quick-wins based on goals
    quick_wins = {
        "growth": [
            "React to a trending video in your niche within 24h of it going viral",
            "Stitch / Duet top creators — borrow their audience",
            "Post a controversial (but safe) opinion in your niche",
            "Create a 'series' — viewers follow to see the next part",
            "Use ONLY trending audio from the past 7 days",
        ],
        "monetization": [
            "Add affiliate link to bio IMMEDIATELY — even 1K followers converts",
            "Mention your product/service in 1 of every 4 posts naturally",
            "Create a freebie lead magnet → email list → paid offer funnel",
            "Apply for brand deals via creator marketplaces at 10K followers",
            "Launch a paid community (Discord/Skool) — even 50 members at $10/mo = $500/mo",
        ],
        "engagement": [
            "End every video with a question to drive comments",
            "Reply to EVERY comment in first hour (boosts algorithmic push)",
            "Go LIVE weekly — live viewers are your most loyal fans",
            "Create 'comment bait' — incomplete statements viewers want to correct",
            "Post 'relatable' content — shared experience = shared + save",
        ],
    }.get(goals, [])

    return {
        "platform": platform,
        "niche": niche_key,
        "account_stage": stage,
        "current_stats": {
            "followers": followers,
            "avg_views": avg_views,
            "engagement_rate": f"{eng_rate:.1f}%",
            "engagement_verdict": eng_verdict,
        },
        "posting_strategy": {
            "recommended_frequency": target_freq,
            "frequency_gap": freq_gap or "Frequency looks good — maintain consistency",
            "best_times_to_post": best_times,
        },
        "content_pillars": content_pillars,
        "hook_formulas": _HOOK_FORMULAS[:6],
        "profile_checklist": profile_checklist,
        "monetization_roadmap": monetization,
        "quick_wins": quick_wins,
        "cross_platform_tip": (
            "Repurpose every TikTok → YouTube Shorts → Instagram Reel. "
            "ONE video = THREE platforms. Remove TikTok watermark with SnapTik before uploading."
        ),
    }
