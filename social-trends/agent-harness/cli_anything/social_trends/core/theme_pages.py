"""Theme page intelligence — strategies, templates, and monetization playbooks.

A theme page (aka 'niche page' or 'fan page') is a social media account
built around a topic rather than a personal brand. This module provides:
  - Niche evaluation and scoring
  - Page setup checklists
  - Content calendar templates
  - Monetization strategy blueprints
  - Conversion optimization (turning followers into revenue)
"""

from typing import Optional


# Proven high-converting theme page niches ranked by monetization potential
NICHE_DATABASE = {
    "luxury_lifestyle": {
        "platforms": ["instagram", "tiktok"],
        "monetization_ceiling": "very_high",
        "avg_cpm": "$8–$18",
        "first_revenue_milestone": "5K followers",
        "content_types": ["luxury cars", "mansions", "watches", "yachts", "jets"],
        "monetization_paths": [
            "Shoutouts ($20–$500 per post at 10K–100K followers)",
            "Luxury brand affiliates (3–10% commission, high AOV)",
            "Sell the page ($500–$50K depending on size and engagement)",
        ],
        "difficulty": "easy",
        "saturation": "medium",
        "tip": "Aggregate content from verified luxury accounts. Consistent aesthetic = faster follow.",
    },
    "fitness_motivation": {
        "platforms": ["instagram", "tiktok", "youtube"],
        "monetization_ceiling": "high",
        "avg_cpm": "$5–$12",
        "first_revenue_milestone": "3K followers",
        "content_types": ["transformation videos", "workout clips", "motivational quotes", "diet tips"],
        "monetization_paths": [
            "Supplement affiliate (MyProtein, GNC pay 8–20%)",
            "Fitness app promotions ($50–$300 per post at 10K)",
            "Sell workout PDFs/ebooks via Gumroad",
            "Coaching upsell funnel",
        ],
        "difficulty": "easy",
        "saturation": "high",
        "tip": "Before/after transformation content has the highest share rate in this niche.",
    },
    "finance_investing": {
        "platforms": ["youtube", "tiktok", "instagram"],
        "monetization_ceiling": "very_high",
        "avg_cpm": "$15–$40",
        "first_revenue_milestone": "1K followers (newsletter list)",
        "content_types": ["stock tips", "crypto news", "personal finance hacks", "passive income"],
        "monetization_paths": [
            "Trading platform affiliates (Webull pays $5–$15/signup)",
            "Newsletter sponsorships at 5K subscribers",
            "YouTube AdSense (highest RPM niche at $15–$40 CPM)",
            "Paid Discord/community membership",
            "Sell courses via Teachable/Gumroad",
        ],
        "difficulty": "medium",
        "saturation": "medium",
        "tip": "Finance content requires disclaimer text. Build email list from day 1 — it compounds.",
    },
    "pet_animals": {
        "platforms": ["tiktok", "instagram", "youtube"],
        "monetization_ceiling": "medium",
        "avg_cpm": "$3–$7",
        "first_revenue_milestone": "10K followers",
        "content_types": ["cute animal clips", "funny pet videos", "pet care tips", "rescue stories"],
        "monetization_paths": [
            "Chewy/PetSmart affiliate program (4–8%)",
            "Pet brand sponsorships at 20K+",
            "Merchandise (custom pet art prints)",
            "Facebook/YouTube monetization (evergreen content pays long-term)",
        ],
        "difficulty": "very_easy",
        "saturation": "high",
        "tip": "Emotional content (rescue stories, reunions) goes viral consistently — lead with emotion.",
    },
    "travel_adventure": {
        "platforms": ["instagram", "youtube", "tiktok"],
        "monetization_ceiling": "high",
        "avg_cpm": "$6–$14",
        "first_revenue_milestone": "5K followers",
        "content_types": ["destination guides", "travel hacks", "budget travel", "hidden gems"],
        "monetization_paths": [
            "Booking.com / Airbnb affiliate (4–8% on hotel bookings)",
            "Travel insurance affiliates (SafetyWing pays $30–$50/sale)",
            "Tourism board paid partnerships at 20K+",
            "YouTube AdSense for destination guides",
        ],
        "difficulty": "medium",
        "saturation": "medium",
        "tip": "Budget travel content massively outperforms luxury in engagement rate.",
    },
    "quotes_motivation": {
        "platforms": ["instagram", "tiktok"],
        "monetization_ceiling": "medium",
        "avg_cpm": "$3–$8",
        "first_revenue_milestone": "20K followers",
        "content_types": ["daily motivational quotes", "success mindset", "entrepreneur tips"],
        "monetization_paths": [
            "Shoutouts (easiest entry point for new pages)",
            "Book affiliate links (Amazon Associates 4.5%)",
            "Digital product sales (journals, planners via Etsy/Gumroad)",
            "Course promotion for business/mindset coaches",
        ],
        "difficulty": "very_easy",
        "saturation": "very_high",
        "tip": "Differentiate with a hyper-specific sub-niche (e.g. 'quotes for nurses' vs generic 'motivation').",
    },
    "food_recipes": {
        "platforms": ["tiktok", "youtube", "instagram"],
        "monetization_ceiling": "high",
        "avg_cpm": "$4–$10",
        "first_revenue_milestone": "5K followers",
        "content_types": ["quick recipes", "cooking hacks", "restaurant reviews", "food challenges"],
        "monetization_paths": [
            "Kitchen gadget affiliate (Amazon Associates, Impact)",
            "Meal kit sponsorships (HelloFresh pays well at 20K+)",
            "Cookbook/recipe PDF sales",
            "YouTube AdSense (food CPM is solid at $4–$10)",
        ],
        "difficulty": "easy",
        "saturation": "high",
        "tip": "Recipe reveal in first 3 seconds + beautiful final shot = completion rate formula.",
    },
    "tech_gadgets": {
        "platforms": ["youtube", "tiktok", "instagram"],
        "monetization_ceiling": "very_high",
        "avg_cpm": "$8–$20",
        "first_revenue_milestone": "1K followers (review products)",
        "content_types": ["unboxing", "reviews", "tech comparisons", "setup tours"],
        "monetization_paths": [
            "Amazon affiliate (electronics 2.5–4% but high AOV)",
            "Brand deals for free review units at 5K+",
            "Sponsored reviews at 20K+ ($200–$2000)",
            "YouTube AdSense (tech CPM $8–$20)",
        ],
        "difficulty": "medium",
        "saturation": "medium",
        "tip": "First-to-review new product launches captures massive search traffic.",
    },
}

# Monetization path playbooks
MONETIZATION_PLAYBOOKS = {
    "shoutouts": {
        "description": "Charge other accounts to be featured/mentioned in your posts.",
        "when_to_start": "5K+ followers with >3% engagement rate",
        "pricing_guide": {
            "5K–10K": "$10–$50 per post",
            "10K–50K": "$50–$200 per post",
            "50K–100K": "$200–$500 per post",
            "100K–500K": "$500–$2000 per post",
        },
        "platforms": ["instagram", "tiktok"],
        "tips": [
            "Use shoutout-for-shoutout (S4S) to grow before charging.",
            "Create a rate card Google Doc and share with DMs.",
            "Only promote accounts within your niche — audience trust > one-time income.",
        ],
    },
    "affiliate_marketing": {
        "description": "Earn commission by driving sales for brands via tracked links.",
        "when_to_start": "1K+ engaged followers — quality > quantity for affiliates.",
        "top_programs": [
            "Amazon Associates (1–10% commission, easy approval)",
            "ShareASale (thousands of brands, 5–30% commissions)",
            "Impact Radius (premium brands, requires some following)",
            "CJ Affiliate (enterprise brands)",
            "Individual brand programs (check brand website for 'affiliate')",
        ],
        "platforms": ["all"],
        "tips": [
            "Put affiliate links in bio (Linktree) and story swipe-ups.",
            "Disclose affiliate partnerships legally (#ad, #affiliate).",
            "Use link tracking (Bitly, Pretty Links) to measure what converts.",
            "High-ticket items ($100+) pay more even at lower conversion rate.",
        ],
    },
    "digital_products": {
        "description": "Sell downloadable content: ebooks, templates, presets, courses.",
        "when_to_start": "2K–5K followers with strong niche authority.",
        "product_ideas": {
            "fitness": "Workout plan PDFs, nutrition guides",
            "finance": "Budgeting spreadsheets, investment tracker",
            "photography": "Lightroom presets, posing guides",
            "business": "Content calendars, client onboarding templates",
            "cooking": "Recipe books, meal prep guides",
        },
        "platforms": ["gumroad", "etsy", "teachable", "stan_store"],
        "tips": [
            "Price test: start at $7, then raise to $27 as social proof builds.",
            "Offer a free lead magnet to build email list before selling.",
            "Stan Store integrates directly in TikTok/Instagram bio — friction-free.",
        ],
    },
    "page_flipping": {
        "description": "Grow a theme page and sell it for a lump sum.",
        "when_to_start": "Build to 10K–100K followers at 3%+ engagement rate, then sell.",
        "when_to_sell": "10K–100K followers at 3%+ engagement rate",
        "valuation_formula": "~$10–$50 per 1K followers (varies by niche and ER)",
        "where_to_sell": [
            "Flippa.com (marketplace for social accounts and websites)",
            "FameSwap.com (Instagram/TikTok accounts)",
            "PlayerUp.com (gaming + social)",
            "Direct outreach to brands in your niche",
        ],
        "tips": [
            "Document all content sources, posting schedules, and analytics before sale.",
            "Higher engagement rate = higher multiple — optimize ER in final 30 days.",
            "Escrow payment (Flippa's built-in) protects both parties.",
            "Niches with high ad spend (finance, tech, luxury) sell for highest multiples.",
        ],
    },
    "brand_deals": {
        "description": "Paid partnerships where brands pay you to feature their product.",
        "when_to_start": "10K+ followers, 3%+ engagement rate",
        "rate_guide": {
            "10K followers": "$50–$200 per post",
            "50K followers": "$200–$800 per post",
            "100K followers": "$500–$2000 per post",
            "500K followers": "$2000–$10000 per post",
        },
        "how_to_land": [
            "Email brands directly with a media kit (PDF with stats + niche overview).",
            "Join influencer platforms: AspireIQ, Grin, Collabstr, Influence.co.",
            "Reply to competitors' sponsor disclosures — brand is likely still buying.",
            "Attend local brand events in your niche.",
        ],
        "tips": [
            "Charge 1.5x your post rate for Stories (higher action rate).",
            "Charge 2–3x for exclusivity (brand doesn't want you working with competitors).",
            "Whitelisting (brand runs ads from your account) can pay 3–5x post rate.",
        ],
    },
}

CONTENT_CALENDAR_TEMPLATES = {
    "7_day_theme_page": {
        "day_1": {"type": "trending_viral_repost", "hook": "Did you know..."},
        "day_2": {"type": "educational_carousel", "hook": "5 things about [niche]"},
        "day_3": {"type": "motivation_quote", "hook": "[Famous person] on [topic]"},
        "day_4": {"type": "trending_audio_video", "hook": "POV: You discovered [niche]"},
        "day_5": {"type": "product_affiliate", "hook": "The [product] every [audience] needs"},
        "day_6": {"type": "community_question", "hook": "Drop your [niche] tip below 👇"},
        "day_7": {"type": "high_value_tutorial", "hook": "How to [desired outcome] in 60s"},
    },
    "30_day_growth_sprint": {
        "week_1": "Post 3x/day. Zero monetization. 100% pure value/viral content.",
        "week_2": "Post 2x/day. Start soft affiliate drops. Build email list with lead magnet.",
        "week_3": "Post 1–2x/day. Launch digital product or shoutout offering.",
        "week_4": "Post 1x/day. Optimize best-performing content. Reach out to brand deals.",
        "kpis": {
            "week_1_target": "500+ followers",
            "week_2_target": "1K+ followers",
            "week_3_target": "2K+ followers, first $100 revenue",
            "week_4_target": "3K+ followers, $500 revenue",
        },
    },
}


def evaluate_niche(niche: str) -> dict:
    """Evaluate a niche for theme page potential.

    Args:
        niche: Niche name or keyword (e.g. 'luxury', 'fitness', 'finance').

    Returns:
        Evaluation dict with score, monetization info, and actionable plan.
    """
    niche_lower = niche.lower()
    match = None
    for key, data in NICHE_DATABASE.items():
        if any(part in niche_lower for part in key.split("_")):
            match = (key, data)
            break

    if match:
        key, data = match
        return {
            "niche": key.replace("_", " ").title(),
            "input": niche,
            "found": True,
            **data,
        }

    return {
        "niche": niche,
        "input": niche,
        "found": False,
        "note": f"'{niche}' is not in our curated database. General tips apply.",
        "general_monetization_paths": list(MONETIZATION_PLAYBOOKS.keys()),
        "recommendations": [
            "Search for existing successful accounts in this niche and study their content.",
            "Join Facebook groups for creators in this niche to find brand deal networks.",
            "Use Google Trends to verify the niche has rising search interest.",
        ],
    }


def get_monetization_playbook(strategy: str) -> dict:
    """Get detailed playbook for a monetization strategy.

    Args:
        strategy: One of: 'shoutouts', 'affiliate_marketing', 'digital_products',
            'page_flipping', 'brand_deals'.
    """
    if strategy not in MONETIZATION_PLAYBOOKS:
        available = list(MONETIZATION_PLAYBOOKS.keys())
        raise ValueError(f"Unknown strategy '{strategy}'. Available: {available}")
    return MONETIZATION_PLAYBOOKS[strategy]


def get_content_calendar(template: str = "7_day_theme_page") -> dict:
    """Return a content calendar template.

    Args:
        template: '7_day_theme_page' or '30_day_growth_sprint'.
    """
    if template not in CONTENT_CALENDAR_TEMPLATES:
        available = list(CONTENT_CALENDAR_TEMPLATES.keys())
        raise ValueError(f"Unknown template '{template}'. Available: {available}")
    return {
        "template": template,
        "calendar": CONTENT_CALENDAR_TEMPLATES[template],
    }


def get_page_setup_checklist(platform: str, niche: str) -> dict:
    """Return a complete page setup checklist for a new theme page.

    Args:
        platform: 'tiktok', 'instagram', or 'youtube'.
        niche: Account niche/topic.
    """
    common = [
        "Choose a memorable, niche-specific username (not your real name).",
        "Write a keyword-rich bio: What you post | Who it's for | Call to action.",
        "Add link-in-bio tool (Stan.store or Linktree) from day 1.",
        "Use a high-contrast profile picture (logo or themed image).",
        "Create a pinned intro/best-of post before marketing the account.",
        "Set account to Public (never Private for growth).",
        "Connect all platforms and cross-promote from launch.",
    ]

    platform_specific = {
        "tiktok": [
            "Switch to TikTok Business Account for analytics (free).",
            "Fill in all profile fields including website.",
            "Set up TikTok Shopping if selling physical products.",
            "Enable Creator Marketplace at 10K followers for brand partnerships.",
            "Add a Series (paid content) option at 10K followers.",
        ],
        "instagram": [
            "Switch to Creator or Professional Account for insights.",
            "Set primary category matching your niche.",
            "Enable Instagram Shopping if selling products.",
            "Add at least 9 posts before promoting (avoid empty grid).",
            "Create a saved Stories Highlight for 'About Me' and 'Reviews'.",
            "Use consistent filter/preset for all grid posts (aesthetic coherence).",
        ],
        "youtube": [
            "Complete channel branding: banner (2560x1440), icon (800x800), watermark.",
            "Write a 200+ word channel description with keywords.",
            "Create a channel trailer (60–90s) that hooks viewers in first 5s.",
            "Set up channel sections: Playlists, Featured, Popular uploads.",
            "Enable community tab at 500+ subscribers.",
            "Apply for YouTube Partner Program at 1K subs + 4K watch hours.",
        ],
    }

    content_strategy = _niche_setup_content_plan(niche, platform)

    return {
        "platform": platform,
        "niche": niche,
        "universal_checklist": common,
        "platform_checklist": platform_specific.get(platform, []),
        "first_30_days_content_plan": content_strategy,
        "monetization_unlock_milestones": {
            "day_1": "Set up bio link and affiliate account (Amazon Associates takes 1–3 days to approve).",
            "500_followers": "Enable Pinterest/Pinterest ads for additional traffic source.",
            "1K_followers": "Join creator programs (TikTok Creativity Program, YouTube Partner).",
            "5K_followers": "Start accepting shoutout requests. Create media kit PDF.",
            "10K_followers": "Reach out to brands directly. Join aspireIQ / Collabstr.",
            "50K_followers": "Negotiate exclusivity bonuses with sponsors (+50% rate).",
        },
    }


def _niche_setup_content_plan(niche: str, platform: str) -> list[str]:
    """Return a first-content-plan for a new page."""
    return [
        f"Post 1: Introduce the page — 'This account is all about {niche}. Follow for daily {niche} content.'",
        f"Post 2: Your highest-quality curated/original {niche} content (set the bar).",
        "Post 3: Trending audio + niche-relevant visuals (ride the algorithm).",
        f"Post 4: Educational carousel — '5 things every {niche} lover should know'.",
        "Post 5: Behind-the-scenes or process content (builds authenticity).",
        "Post 6: Question/poll to the community (drives comments = algorithmic boost).",
        "Post 7: Viral repost or duet/stitch (if allowed) of top account in niche.",
    ]


def list_available_niches() -> dict:
    """List all available niche evaluations in the database."""
    return {
        "available_niches": [
            {
                "key": key,
                "name": key.replace("_", " ").title(),
                "platforms": data["platforms"],
                "difficulty": data["difficulty"],
                "monetization_ceiling": data["monetization_ceiling"],
            }
            for key, data in NICHE_DATABASE.items()
        ],
        "total": len(NICHE_DATABASE),
    }


def list_monetization_strategies() -> dict:
    """List all available monetization strategies."""
    return {
        "strategies": [
            {
                "key": key,
                "description": data["description"],
                "when_to_start": data["when_to_start"],
            }
            for key, data in MONETIZATION_PLAYBOOKS.items()
        ],
        "total": len(MONETIZATION_PLAYBOOKS),
    }


def get_full_theme_page_guide(
    niche: str,
    platform: str,
    monetization_goal: str = "affiliate_marketing",
) -> dict:
    """Master function — returns a complete theme page creation guide.

    Args:
        niche: The content niche for the page.
        platform: Primary platform ('tiktok', 'instagram', 'youtube').
        monetization_goal: Primary monetization strategy.
    """
    niche_eval = evaluate_niche(niche)
    setup = get_page_setup_checklist(platform, niche)
    calendar = get_content_calendar("7_day_theme_page")
    playbook = get_monetization_playbook(monetization_goal) if monetization_goal in MONETIZATION_PLAYBOOKS else {}
    sprint = get_content_calendar("30_day_growth_sprint")

    return {
        "guide_title": f"Complete Theme Page Guide: {niche.title()} on {platform.title()}",
        "niche_evaluation": niche_eval,
        "page_setup_checklist": setup,
        "week_1_content_calendar": calendar,
        "30_day_growth_sprint": sprint,
        "monetization_playbook": playbook,
        "conversion_optimization": {
            "bio_cta": f"Follow for daily {niche} content 🔥 | Link below 👇",
            "pinned_post_formula": "Hook (problem) → Value (solution) → CTA (follow/save/link)",
            "email_capture": "Offer a free resource (PDF/checklist) in bio link to build list.",
            "social_proof": "Pin best-performing post and enable comment pinning.",
        },
    }
