"""Viral content strategy engine."""

from typing import Any, Dict, List, Optional


# Proven content frameworks for going viral
VIRAL_FRAMEWORKS = [
    {
        "name": "Problem-Agitate-Solve (PAS)",
        "structure": "Hook: present a painful problem → Agitate it → Show your solution",
        "best_for": ["finance", "fitness", "education", "motivation"],
        "example": "Struggling to save money? Most people fail because of THIS one mistake. Here's how to fix it in 30 days.",
    },
    {
        "name": "Curiosity Gap",
        "structure": "Tease an unexpected outcome in the first 2s without revealing it",
        "best_for": ["all"],
        "example": "I lost 10k followers doing this... (end: then gained 50k)",
    },
    {
        "name": "Transformation",
        "structure": "Before → During → After. Show dramatic change over time.",
        "best_for": ["fitness", "beauty", "lifestyle", "education"],
        "example": "0 to 100k followers in 90 days — full breakdown",
    },
    {
        "name": "Contrarian Take",
        "structure": "Challenge the conventional wisdom in your niche boldly",
        "best_for": ["finance", "fitness", "marketing", "motivation"],
        "example": "Why you should STOP counting calories (most fitness influencers are wrong)",
    },
    {
        "name": "Numbered List / Ranking",
        "structure": "Top X things that [result]. Viewers watch to see if they agree.",
        "best_for": ["all"],
        "example": "5 apps that replaced my $2000/month software stack",
    },
    {
        "name": "Story Arc",
        "structure": "Personal story with setback → breakthrough → lesson",
        "best_for": ["motivation", "lifestyle", "finance", "education"],
        "example": "I was $40k in debt at 23. Here's exactly how I paid it off.",
    },
    {
        "name": "Tutorial / How-To",
        "structure": "Show exactly how to do one specific thing step by step",
        "best_for": ["howto", "education", "cooking", "tech"],
        "example": "How to make $500 this weekend (without quitting your job)",
    },
    {
        "name": "React & Comment",
        "structure": "React to trending content or news in your niche",
        "best_for": ["gaming", "entertainment", "sports", "news"],
        "example": "Reacting to the most hated gym advice on the internet",
    },
]

HOOK_TEMPLATES = [
    "Nobody is talking about {topic}...",
    "I spent {time} testing {topic} so you don't have to",
    "The {niche} industry doesn't want you to know this",
    "Stop doing {mistake} if you want to {goal}",
    "How I {result} in {timeframe} with no {resource}",
    "POV: You finally figured out {topic}",
    "The reason 99% of people fail at {topic}",
    "{number} {niche} mistakes that are costing you {resource}",
    "This {niche} hack changed everything for me",
    "I tried every {topic} method so you don't have to",
]

CTA_TEMPLATES = {
    "tiktok": [
        "Follow for more {niche} tips every day",
        "Save this if it helped you!",
        "Part 2 coming tomorrow — follow so you don't miss it",
        "Comment '{word}' if you want the free guide",
    ],
    "youtube": [
        "Subscribe for weekly {niche} breakdowns",
        "Watch this video next → [linked video title]",
        "Get my free {niche} checklist — link in description",
        "If this helped you, hit like — it really helps the channel",
    ],
    "instagram": [
        "Save this post — you'll need it later",
        "Tag someone who needs to see this",
        "Follow @{handle} for daily {niche} content",
        "Link in bio for the full breakdown",
    ],
    "twitter": [
        "RT if this helped you",
        "Follow for more threads like this every week",
        "Reply with your biggest {niche} question",
    ],
}


def get_viral_frameworks(niche: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return viral content frameworks, filtered by niche if provided."""
    if not niche:
        return VIRAL_FRAMEWORKS
    niche_lower = niche.lower()
    return [
        f for f in VIRAL_FRAMEWORKS
        if "all" in f["best_for"] or niche_lower in f["best_for"]
    ]


def get_hook_templates(niche: str, count: int = 5) -> List[str]:
    """Return hook templates with niche filled in."""
    templates = HOOK_TEMPLATES[:count]
    return [t.replace("{niche}", niche).replace("{topic}", niche) for t in templates]


def get_cta_templates(platform: str, niche: str = "content", handle: str = "you") -> List[str]:
    """Return CTA templates for a platform."""
    platform = platform.lower()
    templates = CTA_TEMPLATES.get(platform, CTA_TEMPLATES["tiktok"])
    return [t.replace("{niche}", niche).replace("{handle}", handle) for t in templates]


def generate_content_plan(
    niche: str,
    platform: str,
    posts_per_week: int = 7,
) -> List[Dict[str, Any]]:
    """Generate a 7-day content plan for a niche and platform."""
    frameworks = get_viral_frameworks(niche)
    plan = []

    framework_cycle = frameworks * (posts_per_week // max(len(frameworks), 1) + 1)
    hooks = get_hook_templates(niche, posts_per_week)
    ctas = get_cta_templates(platform, niche)

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for i in range(min(posts_per_week, 7)):
        fw = framework_cycle[i % len(framework_cycle)]
        plan.append({
            "day": days[i],
            "framework": fw["name"],
            "structure": fw["structure"],
            "suggested_hook": hooks[i % len(hooks)],
            "suggested_cta": ctas[i % len(ctas)],
            "content_type": _content_type_for_day(platform, days[i]),
        })

    return plan


def _content_type_for_day(platform: str, day: str) -> str:
    if platform == "tiktok":
        weekend = {"Saturday", "Sunday"}
        if day in weekend:
            return "Entertainment / trending challenge"
        return "Educational / value content"
    if platform == "youtube":
        if day in ("Saturday", "Sunday"):
            return "Long-form video"
        return "YouTube Short or mid-length video"
    if platform == "instagram":
        if day in ("Tuesday", "Wednesday", "Thursday"):
            return "Reel (peak engagement days)"
        return "Carousel or Story"
    return "Standard post"


def viral_checklist(platform: str) -> List[Dict[str, str]]:
    """Return a pre-post viral checklist for a platform."""
    common = [
        {"item": "Hook is in first 1-2 seconds", "check": "Does your opening immediately grab attention?"},
        {"item": "Clear value proposition", "check": "Does the viewer know what they'll get in 3s?"},
        {"item": "Loop or rewatch value", "check": "Will viewers watch it again (boosts algorithm)?"},
        {"item": "Strong CTA at the end", "check": "Follow / save / share / comment prompt present?"},
        {"item": "Trending element used", "check": "Trending sound, hashtag, or format incorporated?"},
    ]
    platform_specific = {
        "tiktok": [
            {"item": "Video length 15-60s", "check": "Is it under 60s for max completion rate?"},
            {"item": "Captions on", "check": "Auto-captions enabled for silent viewers?"},
            {"item": "No watermark", "check": "No TikTok watermark if repurposed from elsewhere?"},
        ],
        "youtube": [
            {"item": "Thumbnail A/B tested", "check": "Created 2+ thumbnail options to test?"},
            {"item": "Description has keywords", "check": "First 2 sentences contain primary keyword?"},
            {"item": "Chapters added", "check": "Timestamps in description for long-form?"},
        ],
        "instagram": [
            {"item": "Cover frame optimized", "check": "First frame looks good as a feed thumbnail?"},
            {"item": "Text overlay readable", "check": "Text is legible in 9:16 and square crop?"},
        ],
    }
    return common + platform_specific.get(platform.lower(), [])
