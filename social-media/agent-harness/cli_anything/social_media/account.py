"""Account optimization strategies for TikTok, Instagram, and YouTube."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class AccountAudit:
    platform: str
    username: str
    score: int                      # 0-100
    grade: str                      # A / B / C / D / F
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)
    bio_score: int = 0
    content_score: int = 0
    posting_score: int = 0
    engagement_score: int = 0
    branding_score: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ContentPlan:
    niche: str
    platform: str
    posts_per_week: int
    schedule: list[dict] = field(default_factory=list)
    content_pillars: list[str] = field(default_factory=list)
    hook_templates: list[str] = field(default_factory=list)
    cta_templates: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Bio optimization
# ---------------------------------------------------------------------------

BIO_BEST_PRACTICES = {
    "tiktok": {
        "max_chars": 80,
        "must_haves": [
            "What you do (niche) in first 5 words",
            "Value proposition (why follow you?)",
            "Call to action (link in bio / DM for X)",
            "1-2 relevant emojis for scannability",
            "Keywords your audience searches",
        ],
        "avoid": [
            "Vague phrases like 'just vibing'",
            "Too many emojis (clutters readability)",
            "No clear niche or topic",
            "Asking follows without giving reason",
        ],
        "templates": [
            "{Niche} tips for {audience} 🔥\nHelping you {outcome}\n👇 Free {resource} below",
            "I help {audience} {achieve outcome} 💪\n{Niche} content daily\n📩 DM '{keyword}' for info",
            "{Adjective} {niche} creator | {credential}\n{Posting frequency} videos on {topics}\n🔗 {CTA}",
        ],
    },
    "instagram": {
        "max_chars": 150,
        "must_haves": [
            "Name field: use keywords, not just your name",
            "Niche + who you help in first line",
            "3-4 bullet points with emojis",
            "Link in bio CTA",
            "Location if local business",
        ],
        "avoid": [
            "Paragraph walls of text",
            "Hashtags in bio (don't boost reach)",
            "No clear value statement",
            "Broken or generic link in bio",
        ],
        "templates": [
            "{Title} | {Niche} 🎯\n✅ {Benefit 1}\n✅ {Benefit 2}\n✅ {Benefit 3}\n👇 {CTA}",
            "Helping {audience} {outcome} 🚀\n{Credential/proof}\n📲 New post every {frequency}\n🔗 {Resource/link}",
        ],
    },
    "youtube": {
        "max_chars": 1000,
        "must_haves": [
            "First 100 chars visible without 'Show More'",
            "Primary keyword in first sentence",
            "Upload schedule (builds expectation)",
            "What viewers gain from subscribing",
            "Social links and business email",
        ],
        "avoid": [
            "Keyword stuffing",
            "No subscribe CTA",
            "Missing upload schedule",
            "No contact info for brand deals",
        ],
        "templates": [
            "Welcome! I'm {name} — {niche} content every {frequency}.\n\nOn this channel you'll find:\n• {Topic 1}\n• {Topic 2}\n• {Topic 3}\n\nSubscribe for {outcome}!\n\n📧 Business: {email}\n📱 IG: {handle}",
        ],
    },
}


def get_bio_guide(platform: str) -> dict:
    """Return bio optimization guide for a platform."""
    platform = platform.lower()
    if platform not in BIO_BEST_PRACTICES:
        raise ValueError(f"Platform '{platform}' not supported. Choose: {', '.join(BIO_BEST_PRACTICES)}")
    return {"platform": platform, **BIO_BEST_PRACTICES[platform]}


def score_bio(bio: str, platform: str) -> dict:
    """Score a bio against platform best practices (0-100)."""
    platform = platform.lower()
    guide = BIO_BEST_PRACTICES.get(platform, BIO_BEST_PRACTICES["tiktok"])
    score = 0
    feedback = []

    char_limit = guide["max_chars"]
    if len(bio) == 0:
        return {"score": 0, "grade": "F", "feedback": ["Bio is empty — add one immediately!"]}

    if len(bio) <= char_limit:
        score += 20
    else:
        feedback.append(f"Bio is {len(bio) - char_limit} chars over limit ({char_limit} max).")

    has_emoji = any(ord(c) > 0x1F300 for c in bio)
    if has_emoji:
        score += 10
    else:
        feedback.append("Add 1-2 relevant emojis to improve scannability.")

    has_cta = any(kw in bio.lower() for kw in ["link", "dm", "click", "follow", "check", "↓", "👇", "🔗", "below"])
    if has_cta:
        score += 20
    else:
        feedback.append("Add a call-to-action (e.g., '👇 Link in bio' or 'DM me for...').")

    has_niche_signal = len(bio.split()) >= 5
    if has_niche_signal:
        score += 20
    else:
        feedback.append("Expand your bio — explain what you do and who you help.")

    has_value = any(kw in bio.lower() for kw in ["help", "teach", "learn", "tips", "guide", "best", "free", "daily"])
    if has_value:
        score += 15
    else:
        feedback.append("Add a value statement — why should someone follow you?")

    word_count = len(bio.split())
    if 8 <= word_count <= 30:
        score += 15
    elif word_count < 8:
        feedback.append("Bio is too short — add more detail.")
    else:
        feedback.append("Bio is quite long — trim it for mobile readability.")

    grade = _score_to_grade(score)
    return {"score": min(score, 100), "grade": grade, "feedback": feedback, "char_count": len(bio)}


# ---------------------------------------------------------------------------
# Content pillars + strategy
# ---------------------------------------------------------------------------

CONTENT_PILLARS: dict[str, list[str]] = {
    "fitness": [
        "Educational (form tips, workout science)",
        "Motivational (before/after, progress)",
        "Entertainment (gym fails, reactions)",
        "Personal brand (day in the life)",
        "Promotional (product / service plug)",
    ],
    "finance": [
        "Educational (financial concepts explained)",
        "Inspirational (wealth journeys, success stories)",
        "Controversy/Opinion (hot takes on money)",
        "Tools & Resources (app reviews, spreadsheets)",
        "Promotional (affiliate / consulting)",
    ],
    "fashion": [
        "Outfit inspo (OOTD, lookbooks)",
        "Educational (styling tips, fashion rules)",
        "Entertainment (fashion history, reactions)",
        "Shopping (hauls, thrifting, reviews)",
        "Promotional (brand collabs, affiliate)",
    ],
    "food": [
        "Recipes (tutorial-style, step-by-step)",
        "Reviews (restaurants, products)",
        "Entertainment (taste tests, mukbang)",
        "Educational (nutrition, cooking techniques)",
        "Promotional (restaurant features, brands)",
    ],
    "general": [
        "Educational (teach something valuable)",
        "Entertaining (make them laugh or feel)",
        "Inspirational (motivate or relate to them)",
        "Behind-the-scenes (build trust)",
        "Promotional (pitch your offer — max 20%)",
    ],
}

HOOK_TEMPLATES = [
    "POV: You {scenario that resonates with audience}",
    "The {number} things nobody tells you about {topic}",
    "Stop doing {common mistake}. Do this instead:",
    "I went from {before} to {after} in {timeframe} — here's how:",
    "This {simple thing} made me {impressive result}",
    "Day {number} of {challenge}: {what happened}",
    "If you {do X}, you NEED to watch this",
    "{Number} {niche} mistakes I wish I knew sooner",
    "Rating {popular thing} honestly as a {expert/creator}:",
    "The {dirty secret / truth} about {topic}:",
]

CTA_TEMPLATES = [
    "Follow for more {niche} content!",
    "Drop a {emoji} if this helped you!",
    "Save this for when you need it 🔖",
    "Share this with someone who needs to see it",
    "Comment '{word}' and I'll send you my free {resource}",
    "What's your biggest struggle with {topic}? Tell me below!",
    "Which tip was most helpful? Let me know! ⬇️",
    "Link in bio for more {offer}",
    "Subscribe — I post every {schedule}!",
    "Tag someone who needs to hear this 👇",
]


def get_content_plan(
    niche: str,
    platform: str = "tiktok",
    posts_per_week: int = 5,
) -> ContentPlan:
    """Generate a weekly content plan for a niche."""
    niche_key = niche.lower().replace(" ", "")
    pillars = CONTENT_PILLARS.get(niche_key, CONTENT_PILLARS["general"])

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    schedule = []
    for i in range(posts_per_week):
        day = days[i % 7]
        pillar = pillars[i % len(pillars)]
        time = _best_time_for_platform(platform, day)
        schedule.append({
            "day": day,
            "time": time,
            "content_pillar": pillar,
            "hook_idea": HOOK_TEMPLATES[i % len(HOOK_TEMPLATES)],
            "cta": CTA_TEMPLATES[i % len(CTA_TEMPLATES)],
        })

    return ContentPlan(
        niche=niche,
        platform=platform,
        posts_per_week=posts_per_week,
        schedule=schedule,
        content_pillars=pillars,
        hook_templates=HOOK_TEMPLATES[:5],
        cta_templates=CTA_TEMPLATES[:5],
    )


def _best_time_for_platform(platform: str, day: str) -> str:
    weekend = day in ("Saturday", "Sunday")
    times = {
        "tiktok": "7:00 PM" if not weekend else "11:00 AM",
        "instagram": "6:00 PM" if not weekend else "10:00 AM",
        "youtube": "2:00 PM" if not weekend else "9:00 AM",
    }
    return times.get(platform.lower(), "7:00 PM")


# ---------------------------------------------------------------------------
# Account audit
# ---------------------------------------------------------------------------

def audit_account(
    platform: str,
    username: str,
    bio: Optional[str] = None,
    posts_per_week: Optional[float] = None,
    avg_views: Optional[int] = None,
    follower_count: Optional[int] = None,
    has_profile_pic: bool = True,
    has_link_in_bio: bool = False,
    posts_consistent: bool = False,
    uses_trending_audio: bool = False,
    uses_hashtags: bool = False,
    has_branded_content: bool = False,
) -> AccountAudit:
    """
    Audit a social media account and produce a scored report.
    All fields except platform and username are optional — provide what you know.
    """
    strengths = []
    weaknesses = []
    actions = []

    bio_score = 0
    content_score = 0
    posting_score = 0
    engagement_score = 0
    branding_score = 0

    # --- Branding ---
    if has_profile_pic:
        branding_score += 20
        strengths.append("Has profile picture")
    else:
        weaknesses.append("No profile picture")
        actions.append("Add a high-quality profile picture (face or logo).")

    if has_branded_content:
        branding_score += 30
        strengths.append("Branded content style")
    else:
        actions.append("Develop a consistent visual style (colors, fonts, thumbnails).")

    # --- Bio ---
    if bio:
        bio_result = score_bio(bio, platform)
        bio_score = bio_result["score"]
        if bio_score >= 70:
            strengths.append(f"Strong bio (score: {bio_score}/100)")
        else:
            weaknesses.append(f"Weak bio (score: {bio_score}/100)")
            for fb in bio_result.get("feedback", []):
                actions.append(f"Bio: {fb}")
    else:
        bio_score = 0
        actions.append("Write an optimized bio using the 'socials account bio-guide' command.")

    if has_link_in_bio:
        branding_score += 25
        strengths.append("Link in bio present")
    else:
        weaknesses.append("No link in bio")
        actions.append("Add a Linktree or direct link to monetize traffic.")

    # --- Content ---
    if uses_trending_audio:
        content_score += 30
        strengths.append("Uses trending audio")
    else:
        weaknesses.append("Not using trending audio")
        actions.append("Use trending sounds — check 'socials music trending' for today's top sounds.")

    if uses_hashtags:
        content_score += 30
        strengths.append("Uses hashtags")
    else:
        weaknesses.append("Missing hashtags")
        actions.append("Add 3-15 targeted hashtags — use 'socials hashtags build' to generate a set.")

    # --- Posting consistency ---
    if posts_per_week is not None:
        if posts_per_week >= 5:
            posting_score += 50
            strengths.append(f"Posts {posts_per_week:.0f}x/week (high volume)")
        elif posts_per_week >= 3:
            posting_score += 30
            strengths.append(f"Posts {posts_per_week:.0f}x/week")
        elif posts_per_week >= 1:
            posting_score += 15
            weaknesses.append(f"Only posting {posts_per_week:.1f}x/week — algorithm needs more volume")
            actions.append("Increase to 5-7 posts/week during growth phase.")
        else:
            weaknesses.append("Posting less than once a week — algorithm won't push your content")
            actions.append("Post at least 3-5x per week for 90 days to build momentum.")

    if posts_consistent:
        posting_score += 30
        strengths.append("Consistent posting schedule")
    else:
        weaknesses.append("Inconsistent posting schedule")
        actions.append("Pick 3-5 days/week and post at the same times. Consistency signals reliability to the algorithm.")

    # --- Engagement ---
    if avg_views and follower_count and follower_count > 0:
        er = avg_views / follower_count
        if er >= 0.5:
            engagement_score = 100
            strengths.append(f"Excellent engagement rate ({er:.1%} views/follower)")
        elif er >= 0.1:
            engagement_score = 60
            strengths.append(f"Good engagement rate ({er:.1%} views/follower)")
        elif er >= 0.01:
            engagement_score = 30
            weaknesses.append(f"Low engagement rate ({er:.1%} views/follower)")
            actions.append("Focus on hooks — first 2 seconds must stop the scroll.")
        else:
            engagement_score = 10
            weaknesses.append(f"Very low engagement ({er:.1%} views/follower)")
            actions.append("Content may not be matching audience interest. Survey followers or try different formats.")

    # --- Composite score ---
    total_score = int(
        bio_score * 0.20
        + content_score * 0.25
        + posting_score * 0.25
        + engagement_score * 0.20
        + branding_score * 0.10
    )
    total_score = min(max(total_score, 0), 100)

    return AccountAudit(
        platform=platform,
        username=username,
        score=total_score,
        grade=_score_to_grade(total_score),
        strengths=strengths,
        weaknesses=weaknesses,
        action_items=actions,
        bio_score=bio_score,
        content_score=content_score,
        posting_score=posting_score,
        engagement_score=engagement_score,
        branding_score=branding_score,
    )


# ---------------------------------------------------------------------------
# Growth playbooks
# ---------------------------------------------------------------------------

GROWTH_PLAYBOOKS = {
    "0_to_1k": {
        "title": "0 → 1K Followers Playbook",
        "timeline": "30-60 days",
        "focus": "Content-market fit",
        "daily_actions": [
            "Post 1-2 pieces of content using trending audio",
            "Spend 20 mins engaging with 10 accounts in your niche (genuine comments)",
            "Research 3 trending hashtags in your niche",
            "Watch top 10 videos in your niche to identify patterns",
            "Reply to every comment on your posts within 1 hour",
        ],
        "weekly_actions": [
            "Post 5-7 times (test different content types)",
            "Review which posts performed best and double down",
            "Identify 5 trending sounds and incorporate into content",
            "Analyze competitor accounts for content gaps",
        ],
        "kpis": {
            "views_per_post": "500+",
            "weekly_follower_growth": "50-200",
            "engagement_rate": "5%+",
        },
    },
    "1k_to_10k": {
        "title": "1K → 10K Followers Playbook",
        "timeline": "60-90 days",
        "focus": "Content consistency + niche authority",
        "daily_actions": [
            "Post once per day at peak time for your audience",
            "Use trending audio within 24-48h of it going viral",
            "Engage with niche creators (builds community + exposure)",
            "Respond to all comments — algorithm rewards this",
            "Create or jump on 1 trend per day",
        ],
        "weekly_actions": [
            "Batch create 7 pieces of content (Sunday session)",
            "Deep-dive one trending topic in your niche",
            "Collaborate or duet/stitch with similar-sized creators",
            "Review analytics: top 3 performing posts — make more of those",
            "Update hashtag sets based on this week's trending data",
        ],
        "kpis": {
            "views_per_post": "2,000+",
            "weekly_follower_growth": "200-500",
            "engagement_rate": "8%+",
        },
    },
    "10k_to_100k": {
        "title": "10K → 100K Followers Playbook",
        "timeline": "3-6 months",
        "focus": "Brand + monetization + viral content",
        "daily_actions": [
            "Post 1-2x daily — one planned, one reactive to trends",
            "Create a viral-attempt video (high hook investment, shareable)",
            "Engage with followers who leave long comments — feature the best ones",
            "Cross-promote on a second platform (IG Reels if TikTok primary, etc.)",
        ],
        "weekly_actions": [
            "Run one collab with a creator in your niche (10K-100K range)",
            "Launch a series or recurring format viewers expect",
            "Post one 'long-form' piece (YouTube video or carousel) for depth",
            "Analyze follower demographics and refine content accordingly",
            "Start building email list or community (Discord, Telegram)",
        ],
        "kpis": {
            "views_per_post": "10,000+",
            "monthly_follower_growth": "5,000-20,000",
            "engagement_rate": "5%+",
            "monthly_reach": "500K+",
        },
    },
}


def get_growth_playbook(stage: str) -> dict:
    """
    Get actionable growth playbook for your follower stage.
    stage: "0_to_1k" | "1k_to_10k" | "10k_to_100k"
    """
    if stage not in GROWTH_PLAYBOOKS:
        available = ", ".join(GROWTH_PLAYBOOKS.keys())
        raise ValueError(f"Unknown stage '{stage}'. Available: {available}")
    return {"stage": stage, **GROWTH_PLAYBOOKS[stage]}


def list_growth_playbooks() -> list[dict]:
    return [{"stage": k, **v} for k, v in GROWTH_PLAYBOOKS.items()]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _score_to_grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"
