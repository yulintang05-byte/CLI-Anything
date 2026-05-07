"""Account optimization — posting times, bio, content strategy, engagement."""

from cli_anything.social_trends.utils.social_backend import get_posting_times


# ── Bio optimization ──────────────────────────────────────────────────────────

BIO_FORMULAS = {
    "tiktok": {
        "formula": "[Hook/Identity] | [Value You Provide] | [CTA with Link]",
        "char_limit": 80,
        "examples": [
            "Fitness coach helping busy moms lose 20lbs | Free workout plan 👇",
            "Making $10K/mo online | I teach YOU how → Free guide below",
            "Travel the world on a budget ✈️ | New video every Mon/Thu | 👇 Free itinerary",
        ],
        "tips": [
            "Lead with the value you provide, not your title",
            "Include one CTA pointing to your link-in-bio",
            "Use 1–2 emojis max to break up text",
            "State a specific result (20lbs, $10K) not generic claims",
            "Update bio to match your latest pinned video theme",
        ],
    },
    "instagram": {
        "formula": "[Title/Niche] + [Who you help] + [What result] + [CTA]",
        "char_limit": 150,
        "examples": [
            "Personal Trainer 💪\nHelping men 30+ build muscle without steroids\nFree 12-Week Program 👇",
            "Finance Creator 📈\nFrom $0 to $50K invested by 25\nFree investing guide linked below ↓",
            "Food Blogger 🍽️\n5-ingredient recipes for busy people\nNew recipe every day | Save this for later ⬇️",
        ],
        "tips": [
            "Use line breaks for readability (Shift+Enter or draft in Notes)",
            "Include your city if local business",
            "Add a keyword (e.g., 'Personal Trainer') for Instagram search",
            "Keep CTA to ONE action — don't confuse with multiple links",
            "Add story highlight covers that match your bio theme",
        ],
    },
    "youtube": {
        "formula": "[Channel topic] + [Upload schedule] + [Reason to subscribe]",
        "char_limit": 1000,
        "examples": [
            "I make finance simple for everyday people. New videos every Tuesday and Friday. No fluff, just actionable advice to build wealth from scratch.",
            "Gaming channel focused on RPGs and hidden gems. Upload every Wednesday. I find the games you've never heard of but will love.",
        ],
        "tips": [
            "Front-load keywords in the first 100 characters (shown in search)",
            "State your upload schedule to build habit viewers",
            "Mention what makes your channel unique",
            "Add social media links in About section",
            "Keep it conversational, not corporate",
        ],
    },
}


def get_bio_optimization(platform: str) -> dict:
    p = platform.lower()
    guide = BIO_FORMULAS.get(p, BIO_FORMULAS.get("tiktok", {}))
    return {"platform": p, **guide}


# ── Content strategy ──────────────────────────────────────────────────────────

CONTENT_PILLARS: dict[str, list[dict]] = {
    "general": [
        {"pillar": "Education", "pct": 40, "desc": "Teach your audience something valuable", "examples": ["How-to guides", "Tips & tricks", "Myth busting", "Tutorials"]},
        {"pillar": "Inspiration", "pct": 25, "desc": "Motivate and connect emotionally", "examples": ["Success stories", "Transformations", "Quotes + context", "Behind the scenes"]},
        {"pillar": "Entertainment", "pct": 20, "desc": "Keep them watching and coming back", "examples": ["Trends/challenges", "Relatable humor", "Reaction content", "Storytimes"]},
        {"pillar": "Promotion", "pct": 15, "desc": "Soft and hard sell content", "examples": ["Product reveals", "Testimonials", "Offers", "CTAs to link"]},
    ],
    "fitness": [
        {"pillar": "Workout Content", "pct": 35, "desc": "Exercises, routines, form guides"},
        {"pillar": "Nutrition", "pct": 25, "desc": "Meal prep, macros, diet tips"},
        {"pillar": "Transformation / Progress", "pct": 20, "desc": "Before/after, milestone checks"},
        {"pillar": "Lifestyle / Mindset", "pct": 20, "desc": "Discipline, recovery, mental health"},
    ],
    "finance": [
        {"pillar": "Education", "pct": 40, "desc": "How investing, budgeting, taxes work"},
        {"pillar": "Income Transparency", "pct": 25, "desc": "Income reports, portfolio updates"},
        {"pillar": "Storytime / Experience", "pct": 20, "desc": "Mistakes, wins, lessons learned"},
        {"pillar": "Tools / Resources", "pct": 15, "desc": "App reviews, book summaries, course promos"},
    ],
    "food": [
        {"pillar": "Recipes", "pct": 50, "desc": "Original recipes, hacks, recreations"},
        {"pillar": "Reviews", "pct": 20, "desc": "Restaurant, product, snack reviews"},
        {"pillar": "Culture / Exploration", "pct": 20, "desc": "Food history, travel food, culture"},
        {"pillar": "Behind the Scenes", "pct": 10, "desc": "Kitchen setup, prep process, fails"},
    ],
}

POSTING_FREQUENCY: dict[str, dict] = {
    "tiktok":    {"min": 1, "recommended": 3, "max": 5, "unit": "per day",   "note": "More = more chances at virality. Quality over quantity after 1/day baseline."},
    "instagram": {"min": 1, "recommended": 1, "max": 2, "unit": "per day",   "note": "1 Reel/day + 3–5 Stories/day is ideal. Feed posts 4–7x/week."},
    "youtube":   {"min": 1, "recommended": 2, "max": 3, "unit": "per week",  "note": "Consistency beats frequency. Pick a schedule and stick to it."},
    "twitter":   {"min": 3, "recommended": 5, "max": 10, "unit": "per day",  "note": "Threads and replies count. Engage with trending conversations."},
}


def get_content_strategy(platform: str, niche: str) -> dict:
    p = platform.lower()
    n = niche.lower()
    pillars = CONTENT_PILLARS.get(n, CONTENT_PILLARS["general"])
    frequency = POSTING_FREQUENCY.get(p, POSTING_FREQUENCY["tiktok"])
    times = get_posting_times(p, n)

    return {
        "platform": p,
        "niche": n,
        "content_pillars": pillars,
        "posting_frequency": frequency,
        "best_times": times,
        "content_calendar_tip": f"Plan {frequency['recommended']} posts/day. Batch-create 1 week of content in one sitting.",
        "repurposing_tip": "1 YouTube video = 5 TikToks + 5 Instagram Reels + 10 tweet clips. Work smarter.",
    }


def get_posting_schedule(platform: str, niche: str, posts_per_week: int = 7) -> dict:
    """Generate a weekly posting schedule."""
    times = get_posting_times(platform.lower(), niche.lower())
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pillars = CONTENT_PILLARS.get(niche.lower(), CONTENT_PILLARS["general"])

    schedule = []
    for i, day in enumerate(days[:posts_per_week]):
        pillar = pillars[i % len(pillars)]
        time_slot = times[i % len(times)] if times else "7:00 PM"
        schedule.append({
            "day": day,
            "time": time_slot,
            "pillar": pillar["pillar"],
            "content_type": pillar.get("examples", [pillar.get("desc", "")])[0] if pillar.get("examples") else pillar.get("desc", ""),
        })
    return {
        "platform": platform,
        "niche": niche,
        "posts_per_week": posts_per_week,
        "schedule": schedule,
        "tip": "Set phone reminders 30min before each post time. Engage with comments for 1hr post-publish to boost algorithm.",
    }


# ── Engagement tactics ────────────────────────────────────────────────────────

ENGAGEMENT_TACTICS: dict[str, list[dict]] = {
    "tiktok": [
        {"tactic": "Comment Bait", "impact": "HIGH", "desc": "End videos with a question that requires a short answer", "example": "\"Comment your age and I'll tell you what to start doing NOW\""},
        {"tactic": "Reply with Video", "impact": "HIGH", "desc": "Reply to comments with a new video — algorithm double-dips", "example": "Take the most asked question and reply with a video, keeping the conversation thread alive"},
        {"tactic": "Duet/Stitch Bait", "impact": "MEDIUM", "desc": "End video with a cliffhanger that begs a duet or stitch", "example": "\"Duet me trying this\" or \"Someone stitch this with your results\""},
        {"tactic": "Pinned Comment Strategy", "impact": "MEDIUM", "desc": "Pin a comment that extends the conversation or adds value", "example": "Pin a comment with a link, bonus tip, or response to FAQ"},
        {"tactic": "First-Hour Engagement", "impact": "VERY HIGH", "desc": "Engage with every comment in the first 60 minutes of posting", "example": "Set a timer — the first hour determines if TikTok pushes your video wider"},
        {"tactic": "Watch-Time Hooks", "impact": "VERY HIGH", "desc": "Use pattern interrupts every 3–5 seconds to keep viewers watching", "example": "\"Wait for it...\" text overlays, cuts, or reveals that tease what's coming"},
    ],
    "instagram": [
        {"tactic": "Stories Poll/Quiz", "impact": "HIGH", "desc": "Post interactive stories daily to boost account reach", "example": "\"Which outfit? 👗A or B\" — simple polls get 30–40% response rates"},
        {"tactic": "Save-Worthy Carousels", "impact": "VERY HIGH", "desc": "Carousels get 3x more reach — make slide 1 a hook, last slide a CTA", "example": "\"Save this for later\" explicit CTA on final slide"},
        {"tactic": "Collab Posts", "impact": "HIGH", "desc": "Use Instagram Collabs to reach a partner's audience", "example": "Find a non-competing creator in same niche for mutual collab post"},
        {"tactic": "Reel Remix Bait", "impact": "MEDIUM", "desc": "Create content that invites remix/response Reels", "example": "\"Try this with your [product/routine]\" challenges"},
        {"tactic": "DM Funnel", "impact": "HIGH", "desc": "\"Comment X to get [freebie]\" — auto-DM tools send lead magnets", "example": "\"Comment GUIDE below and I'll DM you my free [resource]\""},
    ],
    "youtube": [
        {"tactic": "End Screen CTAs", "impact": "HIGH", "desc": "Use all 4 end screen elements — 2 videos, subscribe, channel", "example": "Show face, say \"Click that video\" while pointing to end screen"},
        {"tactic": "Pinned Comment Value", "impact": "MEDIUM", "desc": "Pin a comment with timestamps, resources, or the next step", "example": "Timestamps with jump links + link to your lead magnet in pinned comment"},
        {"tactic": "Community Posts", "impact": "MEDIUM", "desc": "Use Community tab to poll subscribers and drive back to old videos", "example": "\"Which topic should I cover next?\" poll linking to related previous video"},
        {"tactic": "Comment Heart Strategy", "impact": "HIGH", "desc": "Heart every comment in first 48hrs — subscribers get notified", "example": "Each hearted comment is a notification to that viewer to return"},
    ],
}


def get_engagement_tactics(platform: str) -> dict:
    p = platform.lower()
    tactics = ENGAGEMENT_TACTICS.get(p, ENGAGEMENT_TACTICS.get("tiktok", []))
    return {
        "platform": p,
        "tactic_count": len(tactics),
        "tactics": tactics,
        "priority_order": sorted(tactics, key=lambda x: {"VERY HIGH": 0, "HIGH": 1, "MEDIUM": 2}.get(x["impact"], 3)),
    }


# ── Full account audit ────────────────────────────────────────────────────────

def get_account_audit(platform: str, niche: str) -> dict:
    """Complete account optimization audit checklist."""
    checklist = _build_checklist(platform.lower(), niche.lower())
    return {
        "platform": platform.lower(),
        "niche": niche.lower(),
        "audit_checklist": checklist,
        "quick_wins": [item for item in checklist if item.get("effort") == "LOW"],
        "high_impact": [item for item in checklist if item.get("impact") == "HIGH"],
    }


def _build_checklist(platform: str, niche: str) -> list[dict]:
    items = [
        # Profile
        {"category": "Profile", "item": "Username is simple, memorable, and searchable", "impact": "HIGH", "effort": "LOW"},
        {"category": "Profile", "item": "Profile photo is a clear, high-res headshot or branded logo", "impact": "HIGH", "effort": "LOW"},
        {"category": "Profile", "item": "Bio uses the optimized formula with clear CTA", "impact": "HIGH", "effort": "LOW"},
        {"category": "Profile", "item": "Link-in-bio tool is set up (Linktree, Beacons, or Stan Store)", "impact": "HIGH", "effort": "LOW"},
        # Content
        {"category": "Content", "item": "Posting frequency is consistent (same days/times each week)", "impact": "VERY HIGH", "effort": "MEDIUM"},
        {"category": "Content", "item": "Content follows the 4-pillar model (Education/Inspiration/Entertainment/Promo)", "impact": "HIGH", "effort": "MEDIUM"},
        {"category": "Content", "item": "Each video has a strong hook in the first 1–3 seconds", "impact": "VERY HIGH", "effort": "LOW"},
        {"category": "Content", "item": "Captions include a question or CTA to drive comments", "impact": "HIGH", "effort": "LOW"},
        {"category": "Content", "item": "Trending audio is used where relevant", "impact": "MEDIUM", "effort": "LOW"},
        # Hashtags
        {"category": "Hashtags", "item": "Using platform-optimized hashtag count (not max)", "impact": "MEDIUM", "effort": "LOW"},
        {"category": "Hashtags", "item": "Rotating 3 different hashtag sets to avoid shadowban", "impact": "HIGH", "effort": "LOW"},
        {"category": "Hashtags", "item": "Hashtags match exact content (not generic)", "impact": "HIGH", "effort": "LOW"},
        # Engagement
        {"category": "Engagement", "item": "Responding to all comments within first hour of posting", "impact": "VERY HIGH", "effort": "MEDIUM"},
        {"category": "Engagement", "item": "Actively commenting on 10 accounts in same niche daily", "impact": "HIGH", "effort": "MEDIUM"},
        {"category": "Engagement", "item": "Pinned post/video is your best-performing or most valuable content", "impact": "MEDIUM", "effort": "LOW"},
        # Monetization
        {"category": "Monetization", "item": "Lead magnet is set up (free guide, checklist, template)", "impact": "HIGH", "effort": "MEDIUM"},
        {"category": "Monetization", "item": "Email list is connected to link-in-bio", "impact": "HIGH", "effort": "MEDIUM"},
        {"category": "Monetization", "item": "Affiliate links are set up for niche-relevant products", "impact": "HIGH", "effort": "MEDIUM"},
    ]
    return items
