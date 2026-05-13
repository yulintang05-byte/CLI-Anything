"""Account optimization — posting schedules, bio optimization, content strategy."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class PostingSlot:
    day: str
    time_utc: str
    time_est: str
    time_pst: str
    engagement_score: int  # 1-10
    audience_size_peak: str
    content_type: str
    notes: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AccountAudit:
    platform: str
    issues: list[str]
    wins: list[str]
    quick_wins: list[str]
    estimated_improvement: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BioTemplate:
    platform: str
    niche: str
    template: str
    cta: str
    keywords: list[str]
    character_count: int
    tips: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


# Peak posting windows by platform (research-backed, May 2025)
_POSTING_WINDOWS: dict[str, list[dict]] = {
    "tiktok": [
        {"day": "Monday", "slots": ["06:00", "10:00", "19:00"], "score": 7},
        {"day": "Tuesday", "slots": ["09:00", "12:00", "21:00"], "score": 8},
        {"day": "Wednesday", "slots": ["08:00", "11:00", "19:00"], "score": 9},
        {"day": "Thursday", "slots": ["09:00", "12:00", "20:00"], "score": 8},
        {"day": "Friday", "slots": ["05:00", "13:00", "20:00"], "score": 9},
        {"day": "Saturday", "slots": ["09:00", "12:00", "16:00"], "score": 8},
        {"day": "Sunday", "slots": ["07:00", "11:00", "19:00"], "score": 7},
    ],
    "instagram": [
        {"day": "Monday", "slots": ["08:00", "12:00", "19:00"], "score": 7},
        {"day": "Tuesday", "slots": ["09:00", "13:00", "20:00"], "score": 8},
        {"day": "Wednesday", "slots": ["09:00", "11:00", "18:00"], "score": 9},
        {"day": "Thursday", "slots": ["11:00", "14:00", "20:00"], "score": 9},
        {"day": "Friday", "slots": ["10:00", "13:00", "19:00"], "score": 8},
        {"day": "Saturday", "slots": ["09:00", "12:00", "17:00"], "score": 7},
        {"day": "Sunday", "slots": ["10:00", "13:00", "18:00"], "score": 6},
    ],
    "youtube": [
        {"day": "Monday", "slots": ["14:00", "17:00", "20:00"], "score": 7},
        {"day": "Tuesday", "slots": ["14:00", "17:00", "20:00"], "score": 7},
        {"day": "Wednesday", "slots": ["14:00", "17:00", "21:00"], "score": 8},
        {"day": "Thursday", "slots": ["15:00", "18:00", "21:00"], "score": 9},
        {"day": "Friday", "slots": ["15:00", "18:00", "21:00"], "score": 9},
        {"day": "Saturday", "slots": ["10:00", "14:00", "18:00"], "score": 8},
        {"day": "Sunday", "slots": ["11:00", "14:00", "17:00"], "score": 8},
    ],
}


def _utc_to_est(t: str) -> str:
    h, m = map(int, t.split(":"))
    est_h = (h - 5) % 24
    return f"{est_h:02d}:{m:02d}"


def _utc_to_pst(t: str) -> str:
    h, m = map(int, t.split(":"))
    pst_h = (h - 8) % 24
    return f"{pst_h:02d}:{m:02d}"


_CONTENT_TYPE_BY_DAY = {
    "Monday": "Motivational / educational",
    "Tuesday": "Tutorial / how-to",
    "Wednesday": "Trending / challenge",
    "Thursday": "Behind-the-scenes / personal",
    "Friday": "Entertainment / high energy",
    "Saturday": "Lifestyle / casual",
    "Sunday": "Reflection / week recap",
}

_DAY_NOTES = {
    "Monday": "Lower competition — good for educational content that ages well",
    "Tuesday": "Mid-week ramp — tutorial content performs best",
    "Wednesday": "Hump day peak — trending challenges pop here",
    "Thursday": "Pre-weekend surge — high platform activity",
    "Friday": "Biggest organic reach window — prioritize your best content",
    "Saturday": "Leisure browsing — lifestyle and casual content wins",
    "Sunday": "Story-driven content — audiences are reflective",
}


def generate_posting_schedule(
    platform: str = "tiktok",
    posts_per_week: int = 7,
    niche: str = "general",
) -> list[PostingSlot]:
    """
    Generate an optimized posting schedule for a given platform.
    Returns sorted slots by engagement score (highest first).
    """
    platform_lower = platform.lower()
    windows = _POSTING_WINDOWS.get(platform_lower, _POSTING_WINDOWS["tiktok"])

    # Sort by score descending, pick top N days, then take best slot per day
    sorted_windows = sorted(windows, key=lambda w: w["score"], reverse=True)
    selected = sorted_windows[:min(posts_per_week, 7)]

    slots: list[PostingSlot] = []
    for w in selected:
        best_slot = w["slots"][0]  # highest-priority slot per day
        day = w["day"]
        slots.append(
            PostingSlot(
                day=day,
                time_utc=best_slot,
                time_est=_utc_to_est(best_slot),
                time_pst=_utc_to_pst(best_slot),
                engagement_score=w["score"],
                audience_size_peak="Highest 25% of weekly traffic",
                content_type=_CONTENT_TYPE_BY_DAY.get(day, "Mixed"),
                notes=_DAY_NOTES.get(day, ""),
            )
        )

    # Re-sort chronologically by day
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    slots.sort(key=lambda s: day_order.index(s.day))
    return slots


def audit_account(
    platform: str,
    followers: int = 0,
    posts: int = 0,
    avg_views: int = 0,
    bio_filled: bool = False,
    profile_pic: bool = False,
    link_in_bio: bool = False,
    posts_per_week: float = 0.0,
    uses_hashtags: bool = False,
    uses_trending_audio: bool = False,
) -> AccountAudit:
    """Audit an account and return actionable optimization advice."""
    issues: list[str] = []
    wins: list[str] = []
    quick_wins: list[str] = []

    if not profile_pic:
        issues.append("Missing profile picture — accounts with photos get 3x more profile visits")
        quick_wins.append("Add a high-quality, on-brand profile photo immediately")

    if not bio_filled:
        issues.append("Bio is empty or incomplete — missing conversion opportunity")
        quick_wins.append("Write a keyword-rich bio with a clear CTA (call to action)")
    else:
        wins.append("Bio is filled — good for discoverability")

    if not link_in_bio:
        issues.append("No link in bio — losing traffic to your website/product")
        quick_wins.append("Add a Linktree or direct link to monetize traffic")
    else:
        wins.append("Link in bio present — capturing traffic correctly")

    if posts_per_week < 3:
        issues.append(f"Posting frequency too low ({posts_per_week:.1f}/week) — algorithms favor consistent creators")
        quick_wins.append("Increase to minimum 3-5 posts/week on TikTok/Instagram Reels")
    elif posts_per_week >= 5:
        wins.append(f"Strong posting frequency: {posts_per_week:.1f}/week")

    if not uses_hashtags:
        issues.append("Not using hashtags — missing out on discovery traffic")
        quick_wins.append("Use 3-7 targeted hashtags per post (avoid generic mega-tags only)")
    else:
        wins.append("Using hashtags — good for discoverability")

    if not uses_trending_audio:
        issues.append("Not leveraging trending audio — TikTok/Reels pushes trending sound videos 2-3x harder")
        quick_wins.append("Check trending sounds weekly and use them within 72 hours of going viral")
    else:
        wins.append("Using trending audio — algorithm boost active")

    if followers > 0 and avg_views > 0:
        ratio = avg_views / followers
        if ratio < 0.1:
            issues.append(f"Low view/follower ratio ({ratio:.2f}x) — content may not be resonating with algorithm")
        elif ratio > 0.5:
            wins.append(f"Strong view/follower ratio ({ratio:.2f}x) — content is performing above average")

    if posts < 12:
        issues.append(f"Low post count ({posts}) — accounts need 12+ posts for algorithm to understand content category")
        quick_wins.append("Batch-create and schedule 12-20 posts to build your content library")

    improvement = "30-60% increase in reach" if len(quick_wins) >= 3 else "15-30% increase in reach"

    return AccountAudit(
        platform=platform,
        issues=issues,
        wins=wins,
        quick_wins=quick_wins,
        estimated_improvement=improvement,
    )


def generate_bio(platform: str, niche: str, username: str = "", cta_type: str = "link") -> BioTemplate:
    """Generate an optimized bio template for a given platform and niche."""
    BIOS: dict[str, dict[str, str]] = {
        "tiktok": {
            "fitness": "💪 {niche} Creator | Helping you build your dream body\n🏆 [Your Achievement]\n📱 Free workout guide 👇",
            "beauty": "✨ {niche} & Skincare Addict | {location}\n💄 New tutorials every week\n🛍 Shop my faves 👇",
            "food": "🍴 Home cook turning recipes into viral moments\n🥘 New recipe drops {days}\n📩 Collab? DM me",
            "finance": "💰 Teaching you to make money work for YOU\n📈 {achievement}\n🎯 Free guide 👇",
            "fashion": "👗 {niche} Inspo | Outfits for every budget\n🌟 New looks daily\n🛒 Shop my outfits 👇",
            "default": "🔥 {niche} Creator | {value_prop}\n📲 New content {frequency}\n👇 {cta}",
        },
        "instagram": {
            "fitness": "💪 {niche} | Certified Trainer\n🏆 Helping {audience} reach their goals\n📩 Coaching inquiries DM me\n👇 Free program",
            "beauty": "✨ {niche} Artist | {location}\n💋 Tutorials · Reviews · Inspo\n💌 Collabs: {email}\n👇 Shop my look",
            "food": "🍴 Food Creator & Home Chef\n🥗 Healthy recipes made easy\n📌 New post every {days}\n👇 Free cookbook",
            "finance": "📊 Personal Finance Coach\n💸 {achievement} in {timeframe}\n🎯 DM 'MONEY' for free guide\n👇 Resources",
            "default": "✨ {niche} Content Creator\n🎯 {value_prop}\n📩 Business: {email}\n👇 {cta}",
        },
        "youtube": {
            "default": "Welcome to my channel! I post {niche} content every {frequency}.\n{value_prop}\nSubscribe for {benefit}!",
        },
    }

    platform_bios = BIOS.get(platform, BIOS.get("tiktok", {}))
    template = platform_bios.get(niche.lower(), platform_bios.get("default", ""))

    cta_map = {
        "link": "Check the link below",
        "follow": "Follow for daily tips",
        "dm": "DM me to get started",
        "shop": "Shop the look below",
    }
    cta = cta_map.get(cta_type, cta_type)

    template = template.replace("{niche}", niche.title()).replace("{cta}", cta)

    limits = {"tiktok": 80, "instagram": 150, "youtube": 1000, "twitter": 160}

    return BioTemplate(
        platform=platform,
        niche=niche,
        template=template,
        cta=cta,
        keywords=[niche.lower(), f"{niche.lower()} tips", f"{niche.lower()} content", "creator"],
        character_count=len(template),
        tips=[
            f"Keep bio under {limits.get(platform, 150)} characters for mobile visibility",
            "Include 1-2 emojis max per line for readability",
            "Always end with a clear CTA (call to action)",
            "Include your niche keyword in the first line for SEO",
            "Update your bio CTA when you launch new offers",
        ],
    )


def content_pillars(niche: str, posts_per_week: int = 5) -> dict:
    """
    Define content pillars — the categories of content types for a niche.
    Returns a balanced weekly content mix.
    """
    PILLARS: dict[str, list[dict]] = {
        "fitness": [
            {"pillar": "Education", "weight": 0.30, "examples": ["Form tips", "Myth busting", "Science of muscle growth"]},
            {"pillar": "Motivation", "weight": 0.20, "examples": ["Progress reveals", "Transformation stories", "Mindset"]},
            {"pillar": "Entertainment", "weight": 0.20, "examples": ["Gym fails", "Day-in-my-life", "Challenges"]},
            {"pillar": "Tutorial", "weight": 0.20, "examples": ["Workout demos", "Meal prep", "Recovery routines"]},
            {"pillar": "Promotion", "weight": 0.10, "examples": ["Product reviews", "Program drops", "Affiliate"]},
        ],
        "beauty": [
            {"pillar": "Tutorial", "weight": 0.35, "examples": ["Makeup looks", "Skincare routines", "GRWM"]},
            {"pillar": "Review", "weight": 0.25, "examples": ["Product tests", "Dupes", "Sephora hauls"]},
            {"pillar": "Inspiration", "weight": 0.20, "examples": ["Trending looks", "Celebrity dupes", "Seasonal looks"]},
            {"pillar": "Education", "weight": 0.10, "examples": ["Ingredient breakdowns", "Skin type guides"]},
            {"pillar": "Promotion", "weight": 0.10, "examples": ["Brand collabs", "Affiliate links", "Codes"]},
        ],
        "finance": [
            {"pillar": "Education", "weight": 0.40, "examples": ["Investing basics", "Budget templates", "Tax tips"]},
            {"pillar": "Motivation", "weight": 0.20, "examples": ["Income reveals", "Milestone celebrations"]},
            {"pillar": "Case Studies", "weight": 0.20, "examples": ["Portfolio breakdowns", "Side hustle stories"]},
            {"pillar": "News", "weight": 0.10, "examples": ["Market updates", "Economic events"]},
            {"pillar": "Promotion", "weight": 0.10, "examples": ["Courses", "Tools", "Affiliate"]},
        ],
    }

    pillars = PILLARS.get(niche.lower(), [
        {"pillar": "Education", "weight": 0.30, "examples": [f"{niche} tips", f"{niche} how-to"]},
        {"pillar": "Entertainment", "weight": 0.25, "examples": ["Trending challenges", "Fun content"]},
        {"pillar": "Inspiration", "weight": 0.25, "examples": ["Success stories", "Transformation"]},
        {"pillar": "Behind-the-scenes", "weight": 0.10, "examples": ["Day in my life", "Process videos"]},
        {"pillar": "Promotion", "weight": 0.10, "examples": ["Products", "Services", "Affiliate"]},
    ])

    # Assign post count per pillar
    for p in pillars:
        p["posts_this_week"] = max(1, round(p["weight"] * posts_per_week))

    return {
        "niche": niche,
        "posts_per_week": posts_per_week,
        "pillars": pillars,
        "rule": "80/20 — 80% value content, 20% promotional. Never lead with the sell.",
    }
