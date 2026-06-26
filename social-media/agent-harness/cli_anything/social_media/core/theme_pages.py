"""Theme page creation and conversion strategy engine.

A theme page is a faceless niche account built around a topic (not a person).
This module generates niche recommendations, content calendars, conversion
funnels, and monetization strategies for any theme page.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ThemePage:
    niche: str
    sub_niche: str = ""
    platform: str = "tiktok"
    monetization: str = "affiliate"
    target_audience: str = ""


# ── High-converting theme page niches (June 2026) ─────────────────────────────

HIGH_CONVERTING_NICHES = [
    {
        "niche": "Money Mindset / Wealth",
        "examples": ["@dailywealthtips", "@moneymindsethq", "@richhabitsdaily"],
        "why_converts": "High-intent audience actively seeking financial change",
        "monetization": ["Affiliate (Robinhood, Acorns, credit cards)", "Digital products (budget templates)", "Course (investing basics)"],
        "avg_cpm": "$8–$22",
        "content_pillars": ["Wealth facts", "Rich vs poor mindset", "Net worth reveals", "Investment tips", "Passive income ideas"],
        "cta_style": "Lead magnet: free '$0 to $1K' PDF or budget template",
    },
    {
        "niche": "Relationship / Dating",
        "examples": ["@modernloveadvice", "@redflags.daily", "@datingtips2026"],
        "why_converts": "Massive evergreen audience, high emotion = high engagement + shares",
        "monetization": ["Affiliate (dating apps, Tinder Gold)", "Digital products (communication scripts)", "Paid community"],
        "avg_cpm": "$4–$9",
        "content_pillars": ["Red flags", "Green flags", "Text response scripts", "Attachment styles", "Glow-up tips"],
        "cta_style": "Lead magnet: '10 texts that make them chase you' PDF",
    },
    {
        "niche": "AI Tools / Productivity",
        "examples": ["@aitoolsdaily", "@productivityhacks2026", "@aiforeveryone"],
        "why_converts": "Huge B2B crossover — followers buy tools, courses, and SaaS subscriptions",
        "monetization": ["Affiliate (Jasper, Notion, Cursor AI)", "Sponsorships (SaaS tools)", "Paid newsletter"],
        "avg_cpm": "$15–$40",
        "content_pillars": ["Tool of the day", "AI prompt hacks", "Automation workflows", "Time-saving tutorials", "AI vs human comparisons"],
        "cta_style": "Free resource: 'Top 50 AI Tools in 2026' Notion doc",
    },
    {
        "niche": "Side Hustle / Online Income",
        "examples": ["@sidehustleclub", "@makemoneyonline.daily", "@incomereports"],
        "why_converts": "Action-oriented audience; high affiliate conversion rates",
        "monetization": ["Affiliate (Fiverr, Canva Pro, domain registrars)", "Digital course", "Coaching"],
        "avg_cpm": "$10–$25",
        "content_pillars": ["Income reports", "Side hustle ideas", "Passive income breakdowns", "Freelancing tips", "Print-on-demand tutorials"],
        "cta_style": "Lead magnet: 'Free 5-Day Side Hustle Challenge' email sequence",
    },
    {
        "niche": "Gym / Fitness Motivation",
        "examples": ["@gainsdaily", "@aestheticphysique", "@gymtok.official"],
        "why_converts": "Passionate audience + recurring product purchases (supplements, gear)",
        "monetization": ["Affiliate (Gymshark, MyProtein, Amazon supplements)", "Custom workout plans PDF", "1-on-1 coaching"],
        "avg_cpm": "$3–$7",
        "content_pillars": ["Gym transformation clips", "Workout tips", "Diet hacks", "Supplement reviews", "Form checks"],
        "cta_style": "Free PDF: 'Beginner's 12-Week Program'",
    },
    {
        "niche": "Luxury Lifestyle / Aesthetic",
        "examples": ["@luxurylifestyledaily", "@millionairethings", "@aestheticrich"],
        "why_converts": "Aspirational content drives impulse clicks on high-ticket affiliates",
        "monetization": ["Affiliate (luxury brands, travel, real estate leads)", "Sponsorships", "Luxury brand collabs"],
        "avg_cpm": "$5–$12",
        "content_pillars": ["Luxury cars", "Mansions", "Private jets", "Designer unboxings", "High-end travel"],
        "cta_style": "Aspirational CTA: 'Link in bio to see how they afford this'",
    },
    {
        "niche": "Mental Health / Mindfulness",
        "examples": ["@mindfulmoments.daily", "@anxietytips", "@therapist.explains"],
        "why_converts": "Deep emotional resonance = high saves, shares, and community loyalty",
        "monetization": ["Affiliate (BetterHelp, Calm, Headspace)", "Digital journal templates", "Online course"],
        "avg_cpm": "$6–$14",
        "content_pillars": ["Therapy tips", "Anxiety hacks", "Daily affirmations", "Trauma healing", "Nervous system regulation"],
        "cta_style": "Lead magnet: 'Free 7-Day Mindfulness Challenge'",
    },
    {
        "niche": "Business / Entrepreneurship",
        "examples": ["@foundersdaily", "@startupfacts", "@ceo.mindset"],
        "why_converts": "High-income audience; strong B2B affiliate potential",
        "monetization": ["Affiliate (Shopify, HubSpot, business books)", "Mastermind community", "Consulting"],
        "avg_cpm": "$18–$45",
        "content_pillars": ["Founder stories", "Business lessons", "Startup failures", "Revenue milestones", "Productivity systems"],
        "cta_style": "CTA: 'Join 10K entrepreneurs in our free newsletter'",
    },
]

CONVERSION_FUNNEL = {
    "stage_1_awareness": {
        "goal": "Stop the scroll — earn a view",
        "tactics": [
            "Hook in first 1–2 seconds: bold claim, question, or shocking stat",
            "Use trending audio to get algorithmic push",
            "Post at peak hours for your audience timezone",
        ],
    },
    "stage_2_engagement": {
        "goal": "Turn viewer into a follower",
        "tactics": [
            "End video with 'Follow for more [niche] tips'",
            "Pin a comment with your value promise",
            "Ask a yes/no question to drive comments (algorithm boost)",
            "Story arc: setup → conflict → payoff in under 30s",
        ],
    },
    "stage_3_warmup": {
        "goal": "Turn follower into a subscriber / email lead",
        "tactics": [
            "Post 5–7x value videos before ANY promotion",
            "Tease lead magnet: 'Free PDF in my bio — 10K downloads'",
            "Use 'link in bio' CTA sparingly (overuse kills watch time)",
            "Create a highlights/pinned post series that tells your story",
        ],
    },
    "stage_4_conversion": {
        "goal": "Turn lead into a buyer",
        "tactics": [
            "Email sequence: Day 1 lead magnet, Day 3 value, Day 5 soft pitch, Day 7 offer",
            "Social proof: screenshot results, testimonials, DMs as content",
            "Urgency: limited spots for coaching, limited-time discount",
            "Objection handling: FAQ video or carousel addressing top 5 objections",
        ],
    },
    "stage_5_retention": {
        "goal": "Turn buyer into a loyal repeat customer",
        "tactics": [
            "Paid community (Discord, Skool, Circle) for premium members",
            "Monthly live Q&A for customers",
            "Upsell ladder: free PDF → $27 course → $97 workshop → $997 coaching",
            "Referral program: 'Refer 3, get next product free'",
        ],
    },
}

CONTENT_CALENDAR_TEMPLATE = {
    "monday": "Educational / 'Did you know' fact post (saves + shares)",
    "tuesday": "Trending audio + niche content (reach + new followers)",
    "wednesday": "Social proof / transformation / result post (trust building)",
    "thursday": "Controversial opinion or hot take (comments + debate = algorithm gold)",
    "friday": "Personal story or behind-the-scenes (connection + loyalty)",
    "saturday": "Trending format or challenge in your niche (virality attempt)",
    "sunday": "Recap / 'Top 5' carousel or series (saves + profile visits)",
    "daily_stories": "5–10 Stories: 1 poll, 1 Q&A box, 1 swipe-up CTA, rest value/entertainment",
}

THEME_PAGE_SETUP_STEPS = [
    {
        "step": 1,
        "title": "Pick Your Niche",
        "action": "Choose ONE niche from the list above. Niche down further: not 'fitness' but 'women's morning workout routines'",
        "tool": "Use 'social-media themes niche-ideas --keywords <interest>' to get AI niche suggestions",
    },
    {
        "step": 2,
        "title": "Create Your Brand Identity",
        "action": "Name, logo, color palette, tone of voice. Faceless = consistent visual identity is 10x more important",
        "tool": "Design in Canva: logo + 3 brand colors + 2 fonts. Stay consistent across all platforms",
    },
    {
        "step": 3,
        "title": "Set Up All Accounts Simultaneously",
        "action": "Claim @handle on TikTok + YouTube + Instagram + X at once. Same username everywhere",
        "tool": "Use 'social-media accounts audit --platform all' to get setup checklist per platform",
    },
    {
        "step": 4,
        "title": "Source + Repurpose Content",
        "action": "For faceless pages: curate from Reddit, YouTube, Twitter with credit OR generate with AI tools",
        "tool": "Canva, CapCut, ElevenLabs (AI voiceover), Pictory.ai for video automation",
    },
    {
        "step": 5,
        "title": "Build Content in Batches",
        "action": "Create 30 pieces of content before launching. Post 2x/day for first 30 days without gaps",
        "tool": "Buffer or Later for scheduling. Aim for 60 posts in 30 days minimum",
    },
    {
        "step": 6,
        "title": "Set Up Monetization Infrastructure",
        "action": "Beacons or Stan.store link-in-bio page. TikTok Shop affiliate. Amazon affiliate for YT",
        "tool": "Beacons.ai (free tier) links to: affiliate, digital product, email opt-in, calendar",
    },
    {
        "step": 7,
        "title": "Track & Optimize Weekly",
        "action": "Every Monday: check which 3 posts got most reach. Double down on those formats",
        "tool": "Use 'social-media trends --platform tiktok' to stay on top of what's working NOW",
    },
]


def get_niche_recommendations(keywords: Optional[list] = None, monetization: str = "any") -> list:
    """Return matching high-converting niches, optionally filtered by keyword interest."""
    niches = HIGH_CONVERTING_NICHES
    if keywords:
        kw_lower = [k.lower() for k in keywords]
        niches = [
            n for n in niches
            if any(kw in n["niche"].lower() or
                   any(kw in p.lower() for p in n["content_pillars"])
                   for kw in kw_lower)
        ]
    if not niches:
        niches = HIGH_CONVERTING_NICHES

    if monetization != "any":
        niches = [n for n in niches if any(monetization.lower() in m.lower() for m in n["monetization"])]

    return niches or HIGH_CONVERTING_NICHES


def get_conversion_funnel(niche: str = "") -> dict:
    """Return the full conversion funnel with niche-specific tips."""
    funnel = dict(CONVERSION_FUNNEL)
    if niche:
        matching = [n for n in HIGH_CONVERTING_NICHES if niche.lower() in n["niche"].lower()]
        if matching:
            n = matching[0]
            funnel["niche_specific"] = {
                "lead_magnet": n["cta_style"],
                "monetization": n["monetization"],
                "content_pillars": n["content_pillars"],
            }
    return funnel


def get_content_calendar(niche: str = "") -> dict:
    """Return weekly content calendar template."""
    return {
        "weekly_schedule": CONTENT_CALENDAR_TEMPLATE,
        "daily_target": "2–3 posts (TikTok/Shorts) + 5–10 Stories (Instagram)",
        "content_ratio": "80% value / 10% entertainment / 10% promotion",
        "batch_strategy": "Film 10–15 videos per session, 2–3 sessions/week",
        "niche": niche or "all niches",
    }


def get_setup_guide() -> list:
    """Return the full step-by-step theme page setup guide."""
    return THEME_PAGE_SETUP_STEPS
