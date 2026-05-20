"""Content calendar, hook library, and viral post templates."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional


# ──────────────────────────────────────────────
#  Hook library (proven viral openers)
# ──────────────────────────────────────────────

HOOK_TEMPLATES = {
    "curiosity": [
        "Nobody talks about this {niche} secret...",
        "The {niche} trick that changed everything for me",
        "I wish someone told me this before I started {niche}",
        "Stop doing this if you want to grow your {niche}",
        "This is why your {niche} isn't working (and how to fix it)",
    ],
    "fear_of_missing_out": [
        "{number} {niche} mistakes you're probably making right now",
        "You're losing money every day you don't know this",
        "Everyone in {niche} is doing this — are you?",
        "If you're not doing this in 2025, you're already behind",
        "Warning: This {niche} hack expires soon",
    ],
    "aspirational": [
        "How I went from 0 to {result} in {timeframe}",
        "This is what {result} looks like in {niche}",
        "Day in the life of someone who mastered {niche}",
        "What {niche} success actually looks like",
        "The lifestyle {niche} can give you (if done right)",
    ],
    "educational": [
        "{number} {niche} rules every beginner needs to know",
        "The only {niche} guide you'll ever need (save this)",
        "How {niche} actually works (simplified)",
        "{niche} explained in 60 seconds",
        "The {niche} framework that actually works",
    ],
    "social_proof": [
        "I tested every {niche} strategy so you don't have to",
        "After studying 100 {niche} accounts, here's what I found",
        "Why {niche} experts don't want you to know this",
        "Unpopular {niche} opinion that most people won't say",
        "Real talk: here's what {niche} actually takes",
    ],
}

CTA_TEMPLATES = {
    "save": ["Save this before you forget", "Bookmark this — you'll thank me later", "Save for reference"],
    "follow": ["Follow for daily {niche} tips", "Follow if you want more like this", "Hit follow — I post {niche} content every day"],
    "comment": ["Comment below: what's your biggest {niche} challenge?", "Drop a '{emoji}' if this helped you", "Comment 'YES' if you needed to hear this"],
    "share": ["Share this with someone who needs it", "Send this to a friend in {niche}", "Tag someone who needs to see this"],
    "link": ["Link in bio for the full guide", "Grab the free resource in my bio", "Full checklist in bio"],
}


def generate_hooks(niche: str, hook_type: str = "all", count: int = 5) -> dict:
    """Generate viral hook options for a given niche."""
    niche_clean = niche.strip()

    if hook_type == "all":
        types_to_use = list(HOOK_TEMPLATES.keys())
    elif hook_type in HOOK_TEMPLATES:
        types_to_use = [hook_type]
    else:
        return {
            "error": f"Hook type '{hook_type}' not found",
            "available": list(HOOK_TEMPLATES.keys()),
        }

    hooks = []
    for ht in types_to_use:
        for template in HOOK_TEMPLATES[ht]:
            hooks.append({
                "type": ht,
                "hook": template.format(
                    niche=niche_clean,
                    number="5",
                    result="10K followers",
                    timeframe="30 days",
                    emoji="🔥",
                ),
            })

    return {
        "niche": niche,
        "hooks": hooks[:count],
        "tip": "Use the first 0.5-1 second to deliver the hook. Pair with a visual action simultaneously.",
    }


# ──────────────────────────────────────────────
#  Content calendar generator
# ──────────────────────────────────────────────

CONTENT_TYPES = {
    "monday":    ["Educational tip", "Hook: curiosity"],
    "tuesday":   ["Social proof / case study", "Hook: aspirational"],
    "wednesday": ["Trending audio + niche content", "Hook: FOMO"],
    "thursday":  ["List post (5 tips / mistakes)", "Hook: educational"],
    "friday":    ["Engagement post (question/poll)", "Hook: social proof"],
    "saturday":  ["Behind-the-scenes / personal", "Hook: aspirational"],
    "sunday":    ["Motivation / mindset post", "Hook: FOMO or curiosity"],
}


def generate_content_calendar(niche: str, weeks: int = 2, start_date: Optional[str] = None) -> dict:
    """Generate a content calendar for `weeks` weeks."""
    if start_date:
        try:
            base = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            base = datetime.today()
    else:
        base = datetime.today()

    # Start on Monday
    days_until_monday = (7 - base.weekday()) % 7
    start = base + timedelta(days=days_until_monday if days_until_monday > 0 else 0)

    calendar = []
    for week in range(weeks):
        for day_offset, (day_name, content_info) in enumerate(CONTENT_TYPES.items()):
            date = start + timedelta(weeks=week, days=day_offset)
            content_type, hook_type = content_info
            raw_hook_type = hook_type.replace("Hook: ", "").lower().replace(" ", "_").replace("/", "_")
            hooks = HOOK_TEMPLATES.get(raw_hook_type, HOOK_TEMPLATES["curiosity"])
            hook = hooks[week % len(hooks)].format(
                niche=niche, number="5", result="10K followers",
                timeframe="30 days", emoji="🔥",
            )
            calendar.append({
                "date": date.strftime("%Y-%m-%d"),
                "day": day_name,
                "week": week + 1,
                "content_type": content_type,
                "hook": hook,
                "posting_times": ["07:00", "19:00"],
                "hashtag_tip": f"Use 3 #{niche}-specific tags + #fyp + #viral",
            })

    return {
        "niche": niche,
        "weeks": weeks,
        "total_posts": len(calendar),
        "calendar": calendar,
        "batch_tip": f"Batch create all {len(calendar)} posts in one 3-hour session on Sunday.",
    }


def get_viral_templates(niche: str) -> dict:
    """Return fill-in-the-blank viral post templates for a niche."""
    templates = [
        {
            "title": "The List Post",
            "format": "[Number] {niche} secrets that nobody tells you:\n\n1. [secret 1]\n2. [secret 2]\n3. [secret 3]\n\nSave this — you'll need it. Follow for more {niche} content.",
            "why_it_works": "Lists trigger curiosity gaps and are save-worthy",
            "best_for": ["TikTok", "Instagram Reels", "YouTube Shorts"],
        },
        {
            "title": "The Mistake Post",
            "format": "Stop doing this in {niche}:\n\n❌ [wrong thing]\n✅ [right thing]\n\nThis single change got me [result].",
            "why_it_works": "Fear-of-loss is 2x more motivating than gain",
            "best_for": ["TikTok", "Instagram"],
        },
        {
            "title": "The Journey Post",
            "format": "How I went from [start] to [result] in {niche}:\n\nWeek 1: [action]\nWeek 2: [action]\nWeek 4: [result]\n\nHere's exactly what I did 👇",
            "why_it_works": "Storytelling creates emotional connection + aspiration",
            "best_for": ["Instagram", "YouTube", "TikTok"],
        },
        {
            "title": "The Question Hook",
            "format": "Would you rather [option A] or [option B] in {niche}?\n\nMost people pick [wrong answer] but here's why [right answer] wins every time...",
            "why_it_works": "Questions force mental engagement and comment responses",
            "best_for": ["TikTok", "Instagram Stories"],
        },
        {
            "title": "The Comparison Post",
            "format": "What most people do in {niche} vs what actually works:\n\n❌ Most people: [common approach]\n✅ What works: [better approach]\n\nSave this for reference 📌",
            "why_it_works": "Comparison content positions you as the expert",
            "best_for": ["Instagram", "TikTok", "YouTube Shorts"],
        },
    ]
    return {
        "niche": niche,
        "templates": [
            {**t, "filled": t["format"].format(niche=niche)}
            for t in templates
        ],
        "posting_tip": "Pick one template/week. Consistency beats variety for theme pages.",
    }
