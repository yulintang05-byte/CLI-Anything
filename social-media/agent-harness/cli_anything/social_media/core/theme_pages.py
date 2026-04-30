"""Theme page creation, management, and follower-to-customer conversion guide."""

from datetime import datetime


_PROVEN_NICHES: list[dict] = [
    {
        "niche": "Luxury Lifestyle",
        "competition": "high",
        "monetization_ease": "high",
        "avg_rpm": "$8–$20",
        "content_types": ["Luxury cars", "mansions", "watches", "travel"],
        "conversion_rate": "2–5%",
        "best_platforms": ["Instagram", "TikTok"],
        "example_accounts": ["Millionaire Mindset pages"],
    },
    {
        "niche": "Finance / Money",
        "competition": "medium",
        "monetization_ease": "very_high",
        "avg_rpm": "$15–$40",
        "content_types": ["Money tips", "investing", "passive income", "budgeting"],
        "conversion_rate": "3–8%",
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
        "example_accounts": ["Financial Freedom pages"],
    },
    {
        "niche": "Fitness / Gym",
        "competition": "very_high",
        "monetization_ease": "high",
        "avg_rpm": "$5–$15",
        "content_types": ["Workout clips", "transformations", "tips", "motivation"],
        "conversion_rate": "2–4%",
        "best_platforms": ["Instagram", "TikTok", "YouTube"],
        "example_accounts": ["Gym motivation pages"],
    },
    {
        "niche": "Quotes / Motivation",
        "competition": "very_high",
        "monetization_ease": "medium",
        "avg_rpm": "$3–$8",
        "content_types": ["Quote graphics", "motivational reels", "affirmations"],
        "conversion_rate": "1–3%",
        "best_platforms": ["Instagram", "Pinterest", "TikTok"],
        "example_accounts": ["Daily quotes pages"],
    },
    {
        "niche": "Entrepreneurship",
        "competition": "medium",
        "monetization_ease": "very_high",
        "avg_rpm": "$20–$50",
        "content_types": ["Business tips", "startup stories", "tool reviews", "income reports"],
        "conversion_rate": "4–10%",
        "best_platforms": ["LinkedIn", "TikTok", "YouTube"],
        "example_accounts": ["Startup/side hustle pages"],
    },
    {
        "niche": "Aesthetic / Fashion",
        "competition": "very_high",
        "monetization_ease": "medium",
        "avg_rpm": "$4–$12",
        "content_types": ["Outfit posts", "moodboards", "style tips", "hauls"],
        "conversion_rate": "1.5–4%",
        "best_platforms": ["Instagram", "Pinterest", "TikTok"],
        "example_accounts": ["OOTD / aesthetic pages"],
    },
    {
        "niche": "Food / Recipes",
        "competition": "high",
        "monetization_ease": "medium",
        "avg_rpm": "$4–$10",
        "content_types": ["Recipe videos", "restaurant visits", "food hacks", "mukbang"],
        "conversion_rate": "1–3%",
        "best_platforms": ["TikTok", "YouTube", "Instagram"],
        "example_accounts": ["Recipe/cooking pages"],
    },
    {
        "niche": "Mindfulness / Mental Health",
        "competition": "medium",
        "monetization_ease": "medium",
        "avg_rpm": "$5–$15",
        "content_types": ["Tips", "journaling prompts", "breathwork", "anxiety help"],
        "conversion_rate": "2–5%",
        "best_platforms": ["Instagram", "TikTok", "Pinterest"],
        "example_accounts": ["Mindfulness / self-care pages"],
    },
]

_CONVERSION_FUNNEL: dict = {
    "stages": [
        {
            "stage": 1,
            "name": "Awareness",
            "goal": "Get discovered by new followers",
            "tactics": [
                "Post viral-format content using trending sounds",
                "Use 3-5 high-volume hashtags per post",
                "Collab with accounts in adjacent niches",
                "Post Reels/Shorts daily for algorithmic push",
            ],
            "content_split": "80% top-of-funnel entertainment/education",
        },
        {
            "stage": 2,
            "name": "Interest",
            "goal": "Convert profile visitors to followers",
            "tactics": [
                "Optimize bio with clear value proposition + CTA",
                "Pin 3 best posts that showcase niche authority",
                "Use carousel posts for high saves (signals quality to algorithm)",
                "Reply to every comment in first 60 minutes of posting",
            ],
            "content_split": "Mixed: viral content + deeper dives",
        },
        {
            "stage": 3,
            "name": "Trust Building",
            "goal": "Build community and authority",
            "tactics": [
                "Post consistently (same days/times each week)",
                "Share authentic behind-the-scenes content",
                "Run polls, Q&As, and interactive stories",
                "Feature follower wins/testimonials",
            ],
            "content_split": "60% educational + 40% personal/community",
        },
        {
            "stage": 4,
            "name": "Conversion",
            "goal": "Turn followers into buyers/leads",
            "tactics": [
                "Soft pitch: 'More details in my bio link'",
                "DM automation: send lead magnet to new followers",
                "Story swipe-up / link sticker for direct traffic",
                "Shoutout-for-shoutout (SFS) to expand reach",
                "Create a 'freebie' to capture emails from followers",
            ],
            "content_split": "Max 20% promotional — never hard-sell",
        },
        {
            "stage": 5,
            "name": "Monetization",
            "goal": "Generate revenue from audience",
            "tactics": [
                "Paid shoutouts to other creators/brands ($50–$500+)",
                "Affiliate links (Amazon, ClickBank, digital products)",
                "Sell your own digital products (ebooks, templates, courses)",
                "Brand sponsorships (pitch at 10K+ followers)",
                "Build email list via lead magnet → sell in email",
            ],
            "content_split": "Maintain 80/20 value-to-promo ratio always",
        },
    ]
}

_DM_SCRIPTS: dict = {
    "new_follower_welcome": (
        "Hey {name}! Thanks for following 🙌 "
        "I share {niche_value} every week. "
        "I just dropped a free {lead_magnet} — want me to send it over?"
    ),
    "lead_magnet_delivery": (
        "Here's your free {lead_magnet}: {link}\n\n"
        "This covers {benefit_1}, {benefit_2}, and {benefit_3}. "
        "Let me know what you think!"
    ),
    "soft_pitch": (
        "Quick question — are you currently trying to {pain_point}? "
        "I created something that helped me {result}. "
        "Want details?"
    ),
    "engagement_opener": (
        "Loved your comment on my {topic} post! "
        "Are you currently working on {related_goal}? "
        "Would love to know more about where you're at."
    ),
}

_CONTENT_SOURCING: list[str] = [
    "Repurpose viral content from your niche (add your commentary — don't copy verbatim)",
    "Use royalty-free footage from Pexels, Pixabay, or Coverr for b-roll",
    "Curate Twitter/Reddit threads into TikTok/Reels (credit the source)",
    "Screenshot viral tweets/quotes → add your reaction",
    "Use Canva Pro templates for aesthetic graphics and carousels",
    "Create faceless content: screen recordings, text animations, stock footage",
    "Use AI tools (Midjourney, DALL-E) for unique visual content",
    "Stitch/duet trending videos with your own take (huge reach hack on TikTok)",
]


def get_conversion_guide(niche: str = "general") -> dict:
    """Get the full theme page to paying customer conversion guide."""
    return {
        "niche": niche,
        "guide_type": "theme_page_conversion",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "conversion_funnel": _CONVERSION_FUNNEL,
        "dm_scripts": _DM_SCRIPTS,
        "content_sourcing": _CONTENT_SOURCING,
        "monetization_methods": _monetization_methods(niche),
        "scaling_strategy": _scaling_strategy(),
        "tools": _recommended_tools(),
    }


def get_niche_guide(niche: str) -> dict:
    """Get detailed guide for a specific niche."""
    niche_data = next(
        (n for n in _PROVEN_NICHES if n["niche"].lower().startswith(niche.lower())),
        None,
    )
    if not niche_data:
        niche_data = {
            "niche": niche,
            "note": "Custom niche — apply general principles below",
        }

    return {
        "niche": niche,
        "data": niche_data,
        "setup_steps": _setup_steps(niche),
        "content_calendar": _content_calendar_template(niche),
        "monetization_methods": _monetization_methods(niche),
        "growth_hacks": _growth_hacks(niche),
    }


def list_niches() -> list[dict]:
    """List all proven theme page niches."""
    return [
        {
            "niche": n["niche"],
            "competition": n["competition"],
            "monetization_ease": n["monetization_ease"],
            "best_platforms": n["best_platforms"],
            "avg_rpm": n.get("avg_rpm", "varies"),
        }
        for n in _PROVEN_NICHES
    ]


def get_funnel_stage(stage: int) -> dict:
    """Get details for a specific funnel stage (1-5)."""
    stages = _CONVERSION_FUNNEL["stages"]
    if stage < 1 or stage > len(stages):
        raise ValueError(f"Stage must be 1-{len(stages)}")
    return stages[stage - 1]


def get_dm_scripts() -> dict:
    """Get all DM automation scripts."""
    return {
        "scripts": _DM_SCRIPTS,
        "tips": [
            "Personalize every DM — {{name}} fields must be filled in.",
            "Send welcome DMs within 5 minutes of someone following.",
            "Never lead with a sale — always lead with value.",
            "DM tools: ManyChat (Instagram/FB), AutoDM.io, or Manychat for TikTok.",
            "Stay within platform DM limits: 50-100 DMs/day max.",
        ],
    }


def _setup_steps(niche: str) -> list[dict]:
    return [
        {"step": 1, "title": "Choose your sub-niche", "action": f"Don't just pick '{niche}' — narrow it. Example: 'budget travel for solo women under 30'"},
        {"step": 2, "title": "Create accounts", "action": "Create consistent username across TikTok, Instagram, YouTube Shorts. Use niche keywords in username."},
        {"step": 3, "title": "Optimize profiles", "action": "Write bio: Who you help + What you give them + CTA. Profile photo: clear, bright, branded."},
        {"step": 4, "title": "Build content bank", "action": "Create 30 pieces of content BEFORE posting. Batch produce 3-5 videos per session."},
        {"step": 5, "title": "Post aggressively", "action": "Post 1-3x daily for first 30 days. Volume and consistency beat perfection."},
        {"step": 6, "title": "Engage for growth", "action": "Comment on 50-100 posts in your niche daily. Reply to every comment on your content."},
        {"step": 7, "title": "Set up monetization", "action": "Affiliate links ready, lead magnet created, Linktree/Beacons bio link set up."},
        {"step": 8, "title": "Analyze and double down", "action": "After 30 days, identify top 3 content types and make 80% of future content that format."},
    ]


def _content_calendar_template(niche: str) -> dict:
    return {
        "week_1": "Pure value content — establish authority in niche",
        "week_2": "Mix of educational + relatable/personal content",
        "week_3": "Trending formats + niche-specific content",
        "week_4": "Community engagement + soft intro of offer/lead magnet",
        "monthly_theme_rotation": [
            "Month 1: Foundation — pure value",
            "Month 2: Trust — behind the scenes + community",
            "Month 3: Authority — case studies + results",
            "Month 4: Conversion — soft pitches + lead magnets",
        ],
    }


def _monetization_methods(niche: str) -> list[dict]:
    methods = [
        {"method": "Paid Shoutouts", "earning_range": "$20–$500 per post", "requirement": "5K+ followers", "effort": "low"},
        {"method": "Affiliate Marketing", "earning_range": "$0.50–$50 per sale", "requirement": "Any size", "effort": "low"},
        {"method": "Digital Products", "earning_range": "$5–$197 per sale", "requirement": "Any size + credibility", "effort": "medium"},
        {"method": "Brand Sponsorships", "earning_range": "$100–$10,000+ per post", "requirement": "10K+ followers", "effort": "medium"},
        {"method": "UGC (User Generated Content)", "earning_range": "$150–$500 per video", "requirement": "No followers needed", "effort": "low"},
        {"method": "Email List + Newsletter", "earning_range": "$1–$5 per subscriber/month", "requirement": "Any size", "effort": "high"},
        {"method": "Coaching / Consulting", "earning_range": "$97–$5,000 per client", "requirement": "Established authority", "effort": "high"},
        {"method": "Membership / Community", "earning_range": "$10–$97/month recurring", "requirement": "Engaged audience", "effort": "high"},
    ]
    return methods


def _scaling_strategy() -> list[dict]:
    return [
        {"phase": "0-10K", "focus": "Content quality + posting volume + niche clarity"},
        {"phase": "10K-100K", "focus": "Collaborations + cross-platform repurposing + first monetization"},
        {"phase": "100K-1M", "focus": "Team building + systematize content production + own products"},
        {"phase": "1M+", "focus": "Brand partnerships + investing in other creators + diversifying income"},
    ]


def _growth_hacks(niche: str) -> list[str]:
    return [
        "Collab with 5 accounts in adjacent niches — cross-audience exposure is free growth.",
        "Use the 'Follow-Unfollow' method carefully on Instagram (max 50/day to avoid restrictions).",
        "Comment meaningfully on viral posts in your niche — your comment can get thousands of views.",
        "Stitch or duet the most viral videos in your niche with your take.",
        "Share your TikToks to Instagram Reels and YouTube Shorts — same content, 3× the distribution.",
        "Repost your best content every 3-4 months — new followers haven't seen it.",
        "Run a giveaway requiring follow + tag — boosts followers 20-50% in 48 hours.",
        "Go live weekly — live streams get massive algorithmic priority on TikTok and Instagram.",
    ]


def _recommended_tools() -> list[dict]:
    return [
        {"tool": "Canva Pro", "use": "Content creation, carousels, thumbnails", "cost": "$13/month"},
        {"tool": "CapCut", "use": "TikTok/Reels video editing", "cost": "Free"},
        {"tool": "Beacons.ai", "use": "Link in bio + DM automation", "cost": "Free / $10/month"},
        {"tool": "ManyChat", "use": "Instagram DM automation", "cost": "Free / $15/month"},
        {"tool": "Later / Buffer", "use": "Content scheduling", "cost": "$15–$25/month"},
        {"tool": "TikTok Analytics", "use": "Track performance natively", "cost": "Free"},
        {"tool": "Metricool", "use": "Cross-platform analytics", "cost": "Free / $18/month"},
        {"tool": "Epidemic Sound", "use": "Copyright-free music for YT/cross-posting", "cost": "$15/month"},
        {"tool": "ChatGPT", "use": "Caption writing, hook generation, content ideas", "cost": "Free / $20/month"},
    ]
