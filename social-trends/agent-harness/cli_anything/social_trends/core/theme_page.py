"""Theme page strategy — complete guide to building converting theme pages."""

from __future__ import annotations

from typing import Any

PROVEN_NICHES: dict[str, dict] = {
    "motivational": {
        "description": "Inspirational quotes, success mindset, daily motivation",
        "avg_engagement": "4-8%",
        "monetization": ["digital products", "coaching", "affiliate (books/courses)", "shoutouts"],
        "content_ratio": {"quotes": 50, "tips": 30, "stories": 20},
        "best_platforms": ["instagram", "tiktok"],
        "example_accounts": ["motivated.mindset", "dailymotivation"],
        "posting_cadence": "5-7x/day on TikTok, 3-5x/day on Instagram",
        "converting_tip": "Add 'Get my FREE [niche] guide → link in bio' to every 3rd post",
    },
    "fitness": {
        "description": "Workouts, nutrition, body transformation, fitness tips",
        "avg_engagement": "3-6%",
        "monetization": ["fitness programs", "meal plans", "supplements affiliate", "coaching"],
        "content_ratio": {"workouts": 40, "nutrition": 30, "transformation": 30},
        "best_platforms": ["instagram", "tiktok", "youtube"],
        "posting_cadence": "2-4x/day on TikTok, 1-2x/day on Instagram",
        "converting_tip": "Before/after content converts 5x better — lead with transformation stories",
    },
    "finance": {
        "description": "Money tips, investing, passive income, financial freedom",
        "avg_engagement": "5-10%",
        "monetization": ["financial courses", "affiliate (brokerages, apps)", "paid community", "consulting"],
        "content_ratio": {"tips": 50, "case_studies": 30, "tools": 20},
        "best_platforms": ["tiktok", "instagram", "youtube"],
        "posting_cadence": "3-5x/day on TikTok",
        "converting_tip": "Use curiosity hooks: 'The #1 thing rich people do that poor people don't…'",
    },
    "travel": {
        "description": "Destinations, travel hacks, budget travel, luxury travel",
        "avg_engagement": "4-7%",
        "monetization": ["booking affiliate (hotels.com, booking.com)", "tour affiliate", "digital guides", "brand deals"],
        "content_ratio": {"destinations": 50, "hacks": 30, "gear": 20},
        "best_platforms": ["instagram", "tiktok", "youtube"],
        "posting_cadence": "2-4x/day",
        "converting_tip": "Travel booking links convert best — use booking.com or TripAdvisor affiliate",
    },
    "beauty": {
        "description": "Makeup tutorials, skincare routines, beauty hacks",
        "avg_engagement": "5-9%",
        "monetization": ["amazon affiliate", "brand deals", "LTK commission", "own products"],
        "content_ratio": {"tutorials": 50, "reviews": 30, "hacks": 20},
        "best_platforms": ["tiktok", "instagram", "youtube"],
        "posting_cadence": "3-5x/day on TikTok",
        "converting_tip": "Always tag products in Reels/TikToks — make buying frictionless",
    },
    "pets": {
        "description": "Cute animals, pet care, training tips, funny moments",
        "avg_engagement": "8-15%",
        "monetization": ["pet affiliate (Chewy, PetSmart)", "merch", "brand deals", "shoutouts"],
        "content_ratio": {"funny": 50, "tips": 30, "products": 20},
        "best_platforms": ["tiktok", "instagram"],
        "posting_cadence": "5-10x/day (repost viral pet content)",
        "converting_tip": "Pets = highest organic reach. Use Chewy affiliate + Redbubble merch",
    },
    "luxury": {
        "description": "Luxury lifestyle, supercars, mansions, expensive watches",
        "avg_engagement": "3-5%",
        "monetization": ["aspirational brand deals", "affiliate luxury goods", "paid community"],
        "content_ratio": {"lifestyle": 60, "reviews": 25, "tours": 15},
        "best_platforms": ["instagram", "tiktok", "youtube"],
        "posting_cadence": "2-3x/day",
        "converting_tip": "Aspirational content works as top-of-funnel — funnel to paid community",
    },
    "food": {
        "description": "Recipes, food reviews, cooking hacks, mukbang",
        "avg_engagement": "4-7%",
        "monetization": ["cooking affiliate", "recipe books (Gumroad)", "kitchen gear affiliate", "brand deals"],
        "content_ratio": {"recipes": 50, "hacks": 30, "reviews": 20},
        "best_platforms": ["tiktok", "instagram", "youtube"],
        "posting_cadence": "3-5x/day",
        "converting_tip": "Recipe PDFs convert well at $7-17 — sell via Stan Store or Gumroad",
    },
    "crypto": {
        "description": "Crypto news, altcoin picks, DeFi, NFTs, Web3",
        "avg_engagement": "5-12%",
        "monetization": ["exchange affiliate (Binance, Coinbase)", "paid signals group", "courses", "consulting"],
        "content_ratio": {"news": 40, "analysis": 40, "education": 20},
        "best_platforms": ["twitter", "tiktok", "youtube"],
        "posting_cadence": "5-10x/day on Twitter, 2-3x/day on TikTok",
        "converting_tip": "Telegram/Discord VIP groups convert at $49-99/month for signal followers",
    },
    "humor": {
        "description": "Memes, relatable comedy, viral reposts, funny edits",
        "avg_engagement": "6-12%",
        "monetization": ["shoutouts ($100-1000 at 100K)", "merch", "brand deals", "creator fund"],
        "content_ratio": {"memes": 60, "relatable": 30, "original": 10},
        "best_platforms": ["instagram", "tiktok"],
        "posting_cadence": "8-15x/day (curation model)",
        "converting_tip": "Humor pages scale fastest via shoutout network — get in meme pods",
    },
}

CONVERTING_ELEMENTS = {
    "bio_formula": (
        "[Emoji] [What you do] for [target audience]\n"
        "[Emoji] [Benefit/result they get]\n"
        "[Emoji] [Social proof or achievement]\n"
        "[Emoji] [CTA] → [link]"
    ),
    "bio_examples": {
        "fitness": (
            "💪 Daily fitness tips for busy professionals\n"
            "📉 Lost 50lbs using these exact methods\n"
            "🏆 100K followers can't be wrong\n"
            "👇 Get my FREE 7-day plan → [link]"
        ),
        "finance": (
            "💰 Making money work harder for you\n"
            "📈 From broke to $50K saved in 2 years\n"
            "🎯 Followed by 200K+ money-minded people\n"
            "👇 Free investing starter guide → [link]"
        ),
        "motivational": (
            "🔥 Daily motivation to level up your life\n"
            "✅ Mindset shifts that changed everything\n"
            "👥 500K+ people growing daily\n"
            "👇 Free success roadmap → [link]"
        ),
    },
    "link_in_bio_stack": [
        "1. Free lead magnet (builds email list — most valuable asset)",
        "2. Best-selling digital product ($7-47 low-ticket)",
        "3. Main offer ($97-997 course or coaching)",
        "4. Affiliate top-pick (most relevant product to niche)",
        "5. Latest video / social links",
    ],
    "story_highlights_structure": [
        "START HERE — intro video, what you post about",
        "FREE STUFF — link to lead magnet / freebies",
        "RESULTS — testimonials, before/afters, social proof",
        "SHOP / LINKS — products, affiliate links, merch",
        "ABOUT ME — personal story (builds trust and connection)",
    ],
}

CONTENT_CALENDAR_TEMPLATE = {
    "monday": {"theme": "Motivation Monday", "format": "inspirational quote or tip"},
    "tuesday": {"theme": "Tutorial Tuesday", "format": "how-to or educational"},
    "wednesday": {"theme": "Win Wednesday", "format": "case study or transformation"},
    "thursday": {"theme": "Throwback / Trend Thursday", "format": "trending audio + your niche content"},
    "friday": {"theme": "Feature Friday", "format": "product review or affiliate feature"},
    "saturday": {"theme": "Story Saturday", "format": "personal story or behind-the-scenes"},
    "sunday": {"theme": "Strategy Sunday", "format": "tip list or 'week ahead' content"},
}

CONVERSION_FUNNEL = {
    "awareness": {
        "goal": "New eyes on your content",
        "tactics": [
            "Use trending sounds/hashtags",
            "Stitch or duet viral content in your niche",
            "Post Reels and Shorts (highest reach format)",
            "Collaborate with accounts of similar size",
        ],
    },
    "interest": {
        "goal": "Get them to follow + engage",
        "tactics": [
            "Hook in first 2 seconds — tease the payoff",
            "Use pattern interrupts (unexpected cuts, text overlays)",
            "End with a soft CTA: 'Follow for more [niche] tips'",
            "Respond to every comment to boost visibility",
        ],
    },
    "desire": {
        "goal": "Move followers toward your offer",
        "tactics": [
            "Share results, testimonials, before/afters",
            "Use social proof: 'X people already got results with this'",
            "Give valuable free content that teases your paid offer",
            "Email capture: 'DM me [keyword] for the free guide'",
        ],
    },
    "action": {
        "goal": "Drive conversion (click, buy, DM)",
        "tactics": [
            "Clear CTA every 3rd post: 'Link in bio for [offer]'",
            "Story polls and question boxes to qualify buyers",
            "Limited-time offers: '24h flash sale — link in bio'",
            "DM automation: auto-reply with link when someone comments keyword",
        ],
    },
}

GROWTH_PLAYBOOK = {
    "week_1_3": {
        "phase": "Content Foundation",
        "actions": [
            "Post 3-5x/day for 21 days straight — no breaks",
            "Identify your 3 best-performing formats and double down",
            "Engage 30 min/day on other accounts in your niche",
            "Set up link-in-bio with free lead magnet",
        ],
        "kpi": "100+ followers and 1 piece of content with 10K+ views",
    },
    "week_4_8": {
        "phase": "Audience Building",
        "actions": [
            "Collaborate with 2-3 accounts of similar size weekly",
            "Test paid promotion ($5-10/day) on top-performing posts",
            "Launch first digital product ($7-17) to gauge demand",
            "Build email list to 100+ subscribers",
        ],
        "kpi": "1,000+ followers and consistent $100/month from digital products",
    },
    "month_3_6": {
        "phase": "Monetization Scale",
        "actions": [
            "Pitch 5 brands/week for paid deals",
            "Raise product prices as social proof builds",
            "Launch a $47-97 offer (mini-course, coaching call pack)",
            "Hire VA to handle comment engagement",
        ],
        "kpi": "10,000+ followers and $500-2,000/month revenue",
    },
    "month_6_plus": {
        "phase": "Authority and Automation",
        "actions": [
            "Systematize content creation (batching, templates)",
            "Diversify to 2nd platform",
            "Launch premium offer ($297-997)",
            "Build affiliate income stream",
        ],
        "kpi": "50K+ followers and $5,000+/month",
    },
}


def get_niche_guide(niche: str) -> dict:
    """Return the full guide for a specific niche."""
    niche = niche.lower()
    if niche not in PROVEN_NICHES:
        # Return generic guide with closest match
        close = [n for n in PROVEN_NICHES if niche in n or n in niche]
        if close:
            niche = close[0]
        else:
            return _generic_guide(niche)

    data = PROVEN_NICHES[niche]
    return {
        "niche": niche,
        "overview": data,
        "bio_formula": CONVERTING_ELEMENTS["bio_formula"],
        "bio_example": CONVERTING_ELEMENTS["bio_examples"].get(niche, _default_bio_example(niche)),
        "link_in_bio_stack": CONVERTING_ELEMENTS["link_in_bio_stack"],
        "story_highlights": CONVERTING_ELEMENTS["story_highlights_structure"],
        "content_calendar": CONTENT_CALENDAR_TEMPLATE,
        "conversion_funnel": CONVERSION_FUNNEL,
        "growth_playbook": GROWTH_PLAYBOOK,
    }


def list_supported_niches() -> list[str]:
    return sorted(PROVEN_NICHES.keys())


def get_conversion_tips(platform: str, niche: str, current_followers: int = 0) -> list[str]:
    tips = [
        "=== TOP CONVERTING ACTIONS ===",
        "",
        "PROFILE OPTIMIZATION:",
        f"  • {CONVERTING_ELEMENTS['bio_formula'].split(chr(10))[0]}",
        "  • Link-in-bio: Lead magnet → Low-ticket product → Main offer",
        "  • Profile picture: High-contrast, recognizable at thumbnail size",
        "  • Username: Easy to spell, niche keyword if possible",
        "",
        "CONTENT STRATEGY:",
        "  • Hook in 1-2 seconds: tease the payoff immediately",
        "  • Ratio: 80% value / 20% promotional content",
        "  • Batch-create: film 10-15 videos in one session",
        "  • Repurpose: one idea → TikTok + Reel + YouTube Short + Tweet",
        "",
        "CONVERSION TRIGGERS:",
        "  • Every 3rd post: soft CTA ('Link in bio for free [niche] guide')",
        "  • Comment keyword automation (ManyChat): reply with link when they comment",
        "  • Story swipe-up (or link sticker) daily when promoting",
        "  • DM strategy: engage new followers personally within 24h",
        "",
        "THEME PAGE SPECIFIC:",
        "  • Never show your face — 'theme page' means faceless by design",
        "  • Brand colors + consistent aesthetic = instant recognition",
        "  • Curate + credit: repost viral content with your branding + CTA",
        "  • Post in advance: schedule 1 week ahead so you never miss",
    ]

    niche_data = PROVEN_NICHES.get(niche, {})
    if niche_data.get("converting_tip"):
        tips.insert(2, f"\nNICHE-SPECIFIC TIP FOR {niche.upper()}:")
        tips.insert(3, f"  • {niche_data['converting_tip']}")
        tips.insert(4, "")

    if current_followers >= 1000:
        tips.extend([
            "",
            "MONETIZATION (you're ready):",
            "  • Shoutouts: DM similar-size accounts to set a rate card",
            "  • Affiliate: Pick 1-3 products you'd genuinely recommend",
            "  • Digital product: Create a $17-47 niche guide this week",
        ])

    return tips


def _default_bio_example(niche: str) -> str:
    return (
        f"🔥 Daily {niche} content for serious people\n"
        f"📈 Level up your {niche} game\n"
        f"👥 Join [X]K+ people winning daily\n"
        f"👇 Free {niche} starter guide → [link]"
    )


def _generic_guide(niche: str) -> dict:
    return {
        "niche": niche,
        "overview": {
            "description": f"Theme page focused on {niche} content",
            "avg_engagement": "3-8%",
            "monetization": ["affiliate marketing", "shoutouts", "digital products", "brand deals"],
            "content_ratio": {"educational": 40, "entertaining": 40, "promotional": 20},
            "best_platforms": ["tiktok", "instagram"],
            "posting_cadence": "3-5x/day",
            "converting_tip": f"Build authority in {niche} by being consistent and value-first",
        },
        "bio_formula": CONVERTING_ELEMENTS["bio_formula"],
        "bio_example": _default_bio_example(niche),
        "link_in_bio_stack": CONVERTING_ELEMENTS["link_in_bio_stack"],
        "story_highlights": CONVERTING_ELEMENTS["story_highlights_structure"],
        "content_calendar": CONTENT_CALENDAR_TEMPLATE,
        "conversion_funnel": CONVERSION_FUNNEL,
        "growth_playbook": GROWTH_PLAYBOOK,
    }
