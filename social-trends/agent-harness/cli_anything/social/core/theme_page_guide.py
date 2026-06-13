"""
Theme page creation, growth & monetization guide.
A 'theme page' is a niche curation account that reposts / curates content
around one topic and monetizes through paid promos, affiliate, and direct offers.
"""
from typing import List, Dict, Any

# ── Niche research ────────────────────────────────────────────────────────────

HIGH_CONVERTING_NICHES = [
    {
        "niche":          "Finance / Money",
        "difficulty":     "Medium",
        "monetization":   "Very High",
        "avg_cpm":        "$8–25",
        "best_platforms": ["Instagram", "TikTok", "YouTube"],
        "content_type":   "Money tips, investing, side hustles, budgeting",
        "example_accs":   ["@wealthyminds", "@financialeducation"],
        "affiliate_cos":  ["Robinhood", "Coinbase", "eToro", "Credit Karma"],
        "why_convert":    "High purchase intent — audience wants to spend money to make money",
    },
    {
        "niche":          "Fitness / Weight Loss",
        "difficulty":     "High (saturated)",
        "monetization":   "High",
        "avg_cpm":        "$5–15",
        "best_platforms": ["Instagram", "TikTok", "YouTube"],
        "content_type":   "Workouts, meal prep, transformations, supplements",
        "example_accs":   ["@fitmotivation", "@gains.daily"],
        "affiliate_cos":  ["MyProtein", "Gymshark", "BetterHelp", "Noom"],
        "why_convert":    "High emotion = high spend. Pain + aspiration = perfect sales funnel",
    },
    {
        "niche":          "Business / Entrepreneurship",
        "difficulty":     "Medium",
        "monetization":   "Very High",
        "avg_cpm":        "$10–30",
        "best_platforms": ["Instagram", "TikTok", "Twitter/X"],
        "content_type":   "Startup stories, income screenshots, marketing hacks, mindset",
        "example_accs":   ["@entrepreneur", "@businessclass"],
        "affiliate_cos":  ["Shopify", "Kajabi", "ClickFunnels", "Fiverr"],
        "why_convert":    "Audience is already spending money on tools — they buy recs instantly",
    },
    {
        "niche":          "Luxury / Motivation",
        "difficulty":     "Low",
        "monetization":   "Medium",
        "avg_cpm":        "$3–8",
        "best_platforms": ["Instagram", "TikTok"],
        "content_type":   "Cars, mansions, quotes, lifestyle, aspirational content",
        "example_accs":   ["@luxury", "@mindofriches"],
        "affiliate_cos":  ["Dropshipping stores", "Watch brands", "Travel agencies"],
        "why_convert":    "Massive reach, easy to grow. Shoutouts are main revenue ($50–500/post)",
    },
    {
        "niche":          "Relationships / Dating",
        "difficulty":     "Low-Medium",
        "monetization":   "High",
        "avg_cpm":        "$6–18",
        "best_platforms": ["TikTok", "Instagram"],
        "content_type":   "Couple goals, dating tips, toxic traits, red flags, love quotes",
        "example_accs":   ["@couplegoals", "@datingadvice"],
        "affiliate_cos":  ["Hinge", "Bumble", "TherapyTribe", "Self-help books"],
        "why_convert":    "Emotionally charged niche — audience takes action when they feel understood",
    },
    {
        "niche":          "Mental Health / Self-Improvement",
        "difficulty":     "Low",
        "monetization":   "Medium-High",
        "avg_cpm":        "$5–14",
        "best_platforms": ["TikTok", "Instagram", "Twitter/X"],
        "content_type":   "Anxiety tips, therapy alternatives, stoicism, self-help, journaling",
        "example_accs":   ["@selfimprovementdaily", "@themindfulmvmt"],
        "affiliate_cos":  ["BetterHelp", "Headspace", "Calm", "Notion"],
        "why_convert":    "Pain-driven niche — people actively seek solutions (high conversion)",
    },
    {
        "niche":          "Travel",
        "difficulty":     "Medium",
        "monetization":   "Medium",
        "avg_cpm":        "$4–12",
        "best_platforms": ["Instagram", "TikTok", "YouTube"],
        "content_type":   "Hidden gems, travel hacks, budget tips, aesthetic destinations",
        "example_accs":   ["@travel", "@budgettravel"],
        "affiliate_cos":  ["Booking.com", "Airbnb", "SafetyWing", "NordVPN"],
        "why_convert":    "High aspiration → high spend. Booking commissions are lucrative",
    },
    {
        "niche":          "Food / Recipes",
        "difficulty":     "Medium",
        "monetization":   "Medium",
        "avg_cpm":        "$3–9",
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
        "content_type":   "Quick recipes, food hacks, meal prep, aesthetic plates, restaurant finds",
        "example_accs":   ["@tasty", "@quickrecipes"],
        "affiliate_cos":  ["HelloFresh", "Home Chef", "Instacart", "kitchen gadgets"],
        "why_convert":    "Universal audience — monetize through kitchen affiliates and meal kits",
    },
]

# ── Phase-by-phase growth blueprint ──────────────────────────────────────────

GROWTH_PHASES = [
    {
        "phase":    "Phase 1: Setup (Day 1–3)",
        "goal":     "Create infrastructure for a professional, algorithm-ready account",
        "actions":  [
            "Choose ONE niche. Commit to it for minimum 90 days. No pivoting early.",
            "Research your top 10 competitor accounts — analyze their best posts, captions, hashtags.",
            "Set up a Creator/Business account (never use personal accounts for theme pages).",
            "Optimize profile: name (keyword), bio (value prop + CTA), link (Linktree), profile photo.",
            "Create a content folder: collect 50+ pieces of viral niche content before posting.",
            "Set up Linktree or Beacons with: your best offer, email signup, affiliate links.",
        ],
    },
    {
        "phase":    "Phase 2: Content Foundation (Day 4–30)",
        "goal":     "Build posting habit and initial audience with viral seed content",
        "actions":  [
            "Post 3x/day on TikTok + 2x/day on Instagram Reels minimum.",
            "Always credit original creators (reduces copyright issues + builds trust).",
            "Use trending sounds on EVERY video — even if the music doesn't perfectly match.",
            "Analyze each post at 24h and 48h — note which format/time performs best.",
            "Engage: comment 100 times/day on similar niche accounts (genuine comments, not spam).",
            "Do NOT change posting style or frequency in the first 30 days — consistency is key.",
            "Reach 10K followers before attempting ANY monetization.",
        ],
    },
    {
        "phase":    "Phase 3: Growth Acceleration (Day 31–90)",
        "goal":     "Scale what works, cut what doesn't, build email list",
        "actions":  [
            "Double down on your top 20% of content formats — replicate, don't reinvent.",
            "Start collaborating: reach out to 5 similar-sized accounts per week for shoutout swaps.",
            "Launch a lead magnet (free PDF, checklist, template) to build email list.",
            "Begin engaging with followers via DMs — build authentic community.",
            "Test paid promotion: boost top organic posts with $5–20 budget to test CPM.",
            "Cross-post all content to Pinterest, Twitter/X, YouTube Shorts for free traffic.",
            "Target: 50K–100K followers before charging for paid posts.",
        ],
    },
    {
        "phase":    "Phase 4: Monetization (90+ days / 50K+ followers)",
        "goal":     "Convert audience into consistent revenue streams",
        "actions":  [
            "Charge for shoutouts/paid promos (see rate card below).",
            "Apply to affiliate programs in your niche (Amazon Associates, ShareASale, impact.com).",
            "Sell a digital product: guide, template, preset, or mini-course ($27–97 price point).",
            "Create a media kit: follower count, engagement rate, audience demographics, rates.",
            "Join TikTok Creator Fund / YouTube Partner Program for ad revenue.",
            "Reach out to brands directly (don't wait for inbound) — 10 cold DMs per day.",
        ],
    },
]

# ── Monetization rate card ────────────────────────────────────────────────────

MONETIZATION_RATE_CARD = {
    "paid_shoutouts": [
        {"followers": "10K–50K",   "tiktok": "$25–100",   "instagram": "$50–150",  "note": "Story + post"},
        {"followers": "50K–200K",  "tiktok": "$100–400",  "instagram": "$150–600", "note": "Reel + Story"},
        {"followers": "200K–500K", "tiktok": "$400–1,200","instagram": "$600–2,000","note": "Reel + 24h Story"},
        {"followers": "500K–1M",   "tiktok": "$1,200–4,000","instagram": "$2,000–8,000","note": "Package pricing"},
    ],
    "affiliate_commissions": {
        "Amazon":        "1–10%",
        "ClickFunnels":  "30–40% recurring",
        "Shopify":       "$150–500 per referral",
        "BetterHelp":    "$100–200 per signup",
        "NordVPN":       "$30–100 per sale",
        "Hostinger":     "60% commission",
        "Kajabi":        "30% recurring",
    },
    "digital_products": {
        "E-book / PDF Guide":     "$9–47",
        "Template Pack":          "$17–97",
        "Mini-Course (5–10 vids)":"$47–197",
        "Full Course":            "$197–997",
        "Monthly Membership":     "$7–47/mo",
        "1:1 Coaching":           "$100–500/hr",
    },
    "creator_funds": {
        "TikTok Creator Rewards": "$0.02–$0.04 per 1,000 views (1M+ views/mo to be worth it)",
        "YouTube Partner":        "$1–5 CPM ($1 per 1,000 views avg across niches)",
        "Instagram Reels Bonus":  "Invite-only, $0–35,000/mo (US creators)",
        "Snapchat Spotlight":     "$250+ per viral snap (unpredictable)",
    },
}

# ── DM funnel templates ───────────────────────────────────────────────────────

DM_FUNNEL_TEMPLATES = {
    "warm_lead_opener": (
        "Hey [Name]! Saw you've been following [your page] — appreciate the support! "
        "I just dropped a free [resource] for people in [niche]. Want me to send it over?"
    ),
    "cold_brand_outreach": (
        "Hi [Brand Name] team! I run @[your handle] ({followers}K followers in [niche]). "
        "I'd love to feature [product] to my audience — I think it's a great fit. "
        "Open to discussing a collaboration? Happy to share my media kit."
    ),
    "paid_promo_rate": (
        "Hey! Thanks for reaching out. Here's my rate card:\n"
        "• Story (24h): $[X]\n"
        "• Feed Post: $[X]\n"
        "• Reel: $[X]\n"
        "• Bundle (Story + Post + Reel): $[X]\n\n"
        "Posts go live within 48h. Analytics report provided after. Lmk if you'd like to proceed!"
    ),
    "follow_up": (
        "Hey [Name], just following up on my message from [day]. "
        "Totally understand if the timing isn't right — happy to revisit when it works for you. "
        "Let me know!"
    ),
}

# ── Learning resources ────────────────────────────────────────────────────────

LEARNING_RESOURCES = {
    "free": [
        {
            "title":    "TikTok Creator Academy",
            "url_hint": "tiktok.com/creators/creator-portal",
            "what":     "Platform-specific growth strategies, monetization rules, algorithm insights",
        },
        {
            "title":    "YouTube Creator Academy",
            "url_hint": "creatoracademy.youtube.com",
            "what":     "SEO, channel strategy, audience building, monetization qualification",
        },
        {
            "title":    "Meta Blueprint (Instagram)",
            "url_hint": "facebook.com/business/learn",
            "what":     "Instagram algorithm, paid promotions, Reels best practices",
        },
        {
            "title":    "Grow with Google: Digital Marketing",
            "url_hint": "grow.google",
            "what":     "SEO, analytics, digital advertising foundations",
        },
    ],
    "paid": [
        {
            "title":     "Theme Page Blueprint (Alex Rivera)",
            "price":     "~$297",
            "what":      "Step-by-step theme page setup, scaling to 6-figures in shoutout revenue",
        },
        {
            "title":     "The Influence School",
            "price":     "~$497",
            "what":      "Content strategy, brand deal negotiation, influencer monetization",
        },
        {
            "title":     "Copy.ai + Notion CMS",
            "price":     "$49/mo",
            "what":      "AI-powered caption generation + content calendar system",
        },
    ],
    "tools": [
        {"tool": "CapCut",        "use": "Free video editing — TikTok native, trending templates"},
        {"tool": "Canva",         "use": "Graphics, carousel posts, media kits, thumbnails"},
        {"tool": "Later.com",     "use": "Content scheduling across all platforms"},
        {"tool": "Beacons.ai",    "use": "Link-in-bio with monetization tools built in"},
        {"tool": "Repurpose.io",  "use": "Auto-cross-post TikTok → Reels → Shorts"},
        {"tool": "Metricool",     "use": "Analytics + competitor tracking across platforms"},
        {"tool": "Brand24",       "use": "Track brand mentions and find collab opportunities"},
        {"tool": "Phlanx",        "use": "Engagement rate calculator for competitor analysis"},
    ],
}


def get_theme_page_guide(niche: str = "general") -> Dict[str, Any]:
    """Return the full theme page creation and monetization guide."""
    # Find matching niche
    matching = next(
        (n for n in HIGH_CONVERTING_NICHES if niche.lower() in n["niche"].lower()),
        HIGH_CONVERTING_NICHES[0],
    )

    return {
        "niche_analysis":       matching,
        "all_niches":           HIGH_CONVERTING_NICHES,
        "growth_phases":        GROWTH_PHASES,
        "monetization":         MONETIZATION_RATE_CARD,
        "dm_templates":         DM_FUNNEL_TEMPLATES,
        "learning_resources":   LEARNING_RESOURCES,
        "30_day_action_plan":   _30_day_plan(niche),
        "key_rules":            _key_rules(),
    }


def _30_day_plan(niche: str) -> List[Dict]:
    return [
        {"days": "1–3",   "focus": "Setup",         "task": f"Choose final niche ({niche}), optimize profile, collect 50+ content pieces"},
        {"days": "4–7",   "focus": "First Posts",    "task": "Post 3x/day TikTok, 2x/day IG. No quality filter — just ship and learn"},
        {"days": "8–14",  "focus": "Analyze & Adapt","task": "Identify top 2–3 best formats. Double down. Start commenting 100x/day"},
        {"days": "15–21", "focus": "Consistency",    "task": "Maintain posting schedule. Reach out to 5 accounts for shoutout swaps"},
        {"days": "22–30", "focus": "Foundation",     "task": "Build email list with lead magnet. Pin best post. Set up Linktree"},
        {"days": "31–60", "focus": "Acceleration",   "task": "Scale to 50K followers. Begin soft monetization (affiliate links)"},
        {"days": "61–90", "focus": "Monetization",   "task": "100K target. Charge for paid promos. Sell first digital product"},
    ]


def _key_rules() -> List[str]:
    return [
        "ONE NICHE ONLY — generalist pages never convert. Niche = trust = money.",
        "VOLUME BEATS PERFECTION — 3 good posts beat 1 perfect post every time.",
        "STUDY YOUR ANALYTICS WEEKLY — double what works, kill what doesn't.",
        "NEVER BUY FOLLOWERS — fake followers destroy engagement rate and brand deals.",
        "BUILD AN EMAIL LIST from day 1 — platforms die, email lists don't.",
        "CREDIT CREATORS — always tag original creator. It's ethical AND builds goodwill.",
        "FIRST 90 DAYS = zero monetization — focus only on growth and learning.",
        "REPURPOSE EVERYTHING — 1 TikTok video → IG Reel → YouTube Short → Twitter clip.",
        "THE MONEY IS IN THE DMs — proactive outreach beats waiting for inbound.",
        "CONSISTENCY > VIRALITY — one viral video won't sustain growth; daily posting will.",
    ]
