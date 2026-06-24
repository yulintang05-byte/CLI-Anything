#!/usr/bin/env python3
"""Theme page creation, monetization, and conversion strategy engine.

Theme pages (also called "faceless" accounts) are niche-focused social media
accounts that curate and create content around a specific topic — without
the creator showing their face. They convert followers to revenue through
affiliate marketing, paid promotions, digital products, and memberships.

This module provides:
  - Theme page setup guides by niche
  - Monetization strategy playbooks
  - Conversion funnel frameworks
  - Multi-page scaling blueprints
  - Platform-specific theme page strategies
"""

from typing import Optional


THEME_PAGE_NICHES = {
    "motivation": {
        "description": "Inspirational quotes, success mindset, and personal development content",
        "target_audience": "18-35 year olds seeking improvement, entrepreneurs, students",
        "content_sources": ["BrainyQuote", "Goodreads", "YouTube speeches", "Reddit r/getmotivated"],
        "monetization_potential": "High",
        "competition": "Very High",
        "time_to_monetize_days": 60,
        "avg_monthly_revenue_range": "$500 - $5,000",
        "affiliate_programs": ["Audible", "Skillshare", "MasterClass", "Blinkist", "Mindvalley"],
    },
    "luxury_lifestyle": {
        "description": "Luxury cars, watches, real estate, travel, and wealth aesthetics",
        "target_audience": "Aspirational 18-40 year olds, high earners, entrepreneurs",
        "content_sources": ["YouTube car channels", "Instagram luxury accounts", "Pinterest boards"],
        "monetization_potential": "Very High",
        "competition": "High",
        "time_to_monetize_days": 45,
        "avg_monthly_revenue_range": "$1,000 - $10,000",
        "affiliate_programs": ["Amazon Luxury", "Blueground", "NET-A-PORTER", "luxury watch affiliates"],
    },
    "fitness_transformation": {
        "description": "Body transformation progress, workout clips, nutrition tips",
        "target_audience": "18-45, fitness enthusiasts, people starting their journey",
        "content_sources": ["Reddit r/progresspics", "YouTube fitness channels", "Stock fitness content"],
        "monetization_potential": "Very High",
        "competition": "Very High",
        "time_to_monetize_days": 90,
        "avg_monthly_revenue_range": "$500 - $8,000",
        "affiliate_programs": ["MyProtein", "Gymshark", "Amazon supplements", "ebooks/programs"],
    },
    "nature_travel": {
        "description": "Scenic nature clips, aerial footage, travel destinations",
        "target_audience": "25-50, travel lovers, nature enthusiasts",
        "content_sources": ["Pexels", "Unsplash", "YouTube travel vlogs", "Drone footage sites"],
        "monetization_potential": "Medium",
        "competition": "Medium",
        "time_to_monetize_days": 90,
        "avg_monthly_revenue_range": "$200 - $3,000",
        "affiliate_programs": ["Booking.com", "Airbnb", "TravelPayouts", "GetYourGuide"],
    },
    "cooking_recipes": {
        "description": "Recipe tutorials, food hacks, meal prep, cooking tips",
        "target_audience": "18-55, home cooks, health-conscious individuals",
        "content_sources": ["YouTube cooking channels", "Food blogs", "Pinterest recipes", "TikTok food"],
        "monetization_potential": "High",
        "competition": "High",
        "time_to_monetize_days": 75,
        "avg_monthly_revenue_range": "$300 - $5,000",
        "affiliate_programs": ["Amazon Kitchen", "HelloFresh", "Thrive Market", "cookbooks"],
    },
    "finance_wealth": {
        "description": "Money tips, investing basics, side hustles, frugal living",
        "target_audience": "20-45, young professionals, aspiring investors",
        "content_sources": ["Reddit r/personalfinance", "Finance YouTube", "Business news"],
        "monetization_potential": "Very High",
        "competition": "High",
        "time_to_monetize_days": 60,
        "avg_monthly_revenue_range": "$1,000 - $15,000",
        "affiliate_programs": ["Robinhood", "Acorns", "Credit cards", "courses", "books"],
    },
    "animals_pets": {
        "description": "Cute/funny animal videos, pet care tips, heartwarming clips",
        "target_audience": "All ages, pet owners, animal lovers",
        "content_sources": ["Reddit r/aww", "YouTube pet channels", "Instagram pet accounts"],
        "monetization_potential": "Medium",
        "competition": "High",
        "time_to_monetize_days": 120,
        "avg_monthly_revenue_range": "$200 - $2,000",
        "affiliate_programs": ["Chewy", "PetSmart", "Amazon pet supplies", "pet insurance"],
    },
    "tech_gadgets": {
        "description": "Tech reviews, gadget unboxings, software tips, AI tools",
        "target_audience": "18-40, tech enthusiasts, early adopters",
        "content_sources": ["YouTube tech channels", "Product launches", "Reddit r/gadgets"],
        "monetization_potential": "Very High",
        "competition": "Very High",
        "time_to_monetize_days": 60,
        "avg_monthly_revenue_range": "$500 - $10,000",
        "affiliate_programs": ["Amazon Associates (high AOV)", "Newegg", "Best Buy", "tech SaaS"],
    },
}

MONETIZATION_METHODS = {
    "affiliate_marketing": {
        "description": "Earn commissions promoting other people's products",
        "difficulty": "Easy",
        "startup_cost": "$0",
        "time_to_first_dollar": "1-4 weeks",
        "income_ceiling": "Unlimited",
        "follower_requirement": "0 (but 1K+ helps)",
        "steps": [
            "Pick 2-3 affiliate programs aligned with your niche",
            "Create a free Linktree or Beacons page to house all links",
            "Include affiliate link in bio + every relevant post caption",
            "Create content that naturally leads to the product",
            "Disclose with #affiliate or #ad (FTC requirement)",
            "Track clicks/conversions and double down on what converts",
        ],
        "best_programs": {
            "general": ["Amazon Associates (1-10% commission)", "ShareASale", "Commission Junction"],
            "digital": ["ClickBank (50-75%)", "Gumroad (10%)", "Teachable affiliates"],
            "software": ["ConvertKit ($100+/sale)", "Shopify ($58-$2000/sale)", "SEMrush ($200/sale)"],
        },
        "pro_tips": [
            "Focus on products with recurring commissions (SaaS tools pay every month)",
            "High-ticket ($100+) products need fewer conversions for good income",
            "Create 'best of' or 'top X products' posts — these convert extremely well",
            "Use a URL shortener with tracking so you know which posts drive sales",
        ],
    },
    "paid_promotions": {
        "description": "Charge brands to feature their product in your content",
        "difficulty": "Medium",
        "startup_cost": "$0",
        "time_to_first_dollar": "3-6 months (needs audience)",
        "income_ceiling": "$50K+/month at scale",
        "follower_requirement": "5K+ engaged (not just followers)",
        "steps": [
            "Build a media kit (audience demographics, engagement rate, past work)",
            "Create a 'Work With Me' highlight on Instagram or page on link-in-bio",
            "Research brands in your niche who work with creators (look at competitor tags)",
            "DM or email brands directly with your media kit",
            "Start with gifted collabs to build portfolio",
            "Once you have proof of results, charge 1000 followers = $100-300 per post (rough rate)",
        ],
        "rate_calculator": {
            "nano_1k_10k": "$50-$500 per post",
            "micro_10k_100k": "$500-$5,000 per post",
            "mid_tier_100k_1m": "$5,000-$50,000 per post",
            "macro_1m_plus": "$50,000+ per post",
        },
        "pro_tips": [
            "Engagement rate matters MORE than follower count — brands know this",
            "Never post more than 1 sponsored post per 4 organic posts",
            "Negotiate content usage rights separately (adds 20-50% to rate)",
            "Always disclose sponsorships — your audience's trust is your real asset",
        ],
    },
    "digital_products": {
        "description": "Sell your own ebooks, templates, presets, or courses",
        "difficulty": "Hard",
        "startup_cost": "$0-$100",
        "time_to_first_dollar": "1-3 months to create + launch",
        "income_ceiling": "Unlimited (100% margin)",
        "follower_requirement": "1K+ who trust you",
        "steps": [
            "Identify the #1 pain point your audience has",
            "Create a solution: ebook, notion template, Lightroom preset, mini-course",
            "Use Gumroad, Payhip, or Teachable (all free to start)",
            "Price between $9-$47 for entry-level products",
            "Create a 'launch sequence': tease → reveal → FOMO → offer",
            "Continue promoting evergreen via pinned post and bio link",
        ],
        "product_ideas": {
            "motivation": ["Habit tracker PDF", "Journal prompts ebook", "Affirmation card pack"],
            "fitness": ["Workout program PDF", "Meal plan template", "Progress tracker sheet"],
            "finance": ["Budget spreadsheet", "Investment calculator", "Side hustle guide"],
            "fashion": ["Capsule wardrobe guide", "Style quiz", "Shopping list templates"],
            "business": ["Content calendar template", "Brand kit template", "Pitch deck template"],
        },
        "pro_tips": [
            "Start with a low-cost offer ($7-$27) to build buyer list, then upsell",
            "Bundle products for higher perceived value",
            "Use email list to re-market to existing buyers (free money)",
            "Survey your audience first — build what they ask for, not what you assume",
        ],
    },
    "subscriptions_memberships": {
        "description": "Recurring monthly payments for exclusive content or community",
        "difficulty": "Hard",
        "startup_cost": "$0",
        "time_to_first_dollar": "3-6 months to build value proposition",
        "income_ceiling": "Unlimited (scales with subscribers)",
        "follower_requirement": "5K+ loyal followers",
        "steps": [
            "Define what exclusive value members get (extra content, community, 1:1 access)",
            "Pick a platform: Patreon, Substack, Discord + Stripe, or Instagram Subscriptions",
            "Set pricing tiers ($5, $15, $50/month)",
            "Launch with founding member discount (creates urgency)",
            "Deliver on promises consistently — churn is your biggest enemy",
            "Upsell members to higher tiers with premium perks",
        ],
        "platform_comparison": {
            "Patreon": "Best for creators, 8-12% fee, large existing user base",
            "Substack": "Best for writers/newsletters, 10% fee, built-in discovery",
            "Beehiiv": "Newsletter platform, 0% fee on Grow plan, $42/month",
            "Discord + Stripe": "Best for communities, full control, 2.9% Stripe fee",
        },
        "pro_tips": [
            "100 subscribers at $10/month = $1,000 MRR — achievable faster than you think",
            "Offer annual subscriptions at 20% discount — improves cash flow and retention",
            "Community is more sticky than content — build relationships, not just content",
            "Survey members monthly — act on feedback quickly to reduce churn",
        ],
    },
    "account_flipping": {
        "description": "Build themed accounts to a follower threshold, then sell them",
        "difficulty": "Medium",
        "startup_cost": "$0-$200 (automation tools)",
        "time_to_first_dollar": "3-12 months per account",
        "income_ceiling": "$50K+ per account sale",
        "follower_requirement": "N/A — you're selling the account",
        "steps": [
            "Pick a high-demand niche: pets, motivation, nature, humor, fitness",
            "Build to 10K-50K real, engaged followers (niches with broad appeal sell better)",
            "Document growth metrics: reach, engagement rate, impressions history",
            "List on Flippa, FameSwap, or Social Tradia",
            "Valuations: typically 12-36x monthly monetization potential",
            "Sell or keep — once you know the system, replicate at scale",
        ],
        "valuation_guide": {
            "10K followers, high engagement": "$500 - $2,000",
            "50K followers, high engagement": "$2,000 - $10,000",
            "100K followers, monetized": "$10,000 - $50,000",
            "500K followers, monetized": "$50,000 - $250,000",
        },
        "pro_tips": [
            "Never buy followers — it destroys engagement rate and thus sale price",
            "Consistent posting history and upward growth trend = higher valuation",
            "Niche matters: finance/business/fitness accounts sell for MORE than meme pages",
            "Get an audit report from HypeAuditor before listing to prove authenticity",
        ],
    },
}

CONVERSION_FUNNEL = {
    "stages": [
        {
            "stage": 1,
            "name": "Awareness",
            "goal": "New eyes on your content",
            "tactics": [
                "Trending sounds and hashtags",
                "Collab/duet/stitch with larger accounts",
                "Posting at peak algorithm times",
                "Content that gets shared (emotional or useful)",
            ],
            "metric": "Impressions / Reach",
        },
        {
            "stage": 2,
            "name": "Interest",
            "goal": "Convert viewers to followers",
            "tactics": [
                "Strong profile bio with clear value prop",
                "Pinned 'best of' video or carousel",
                "Consistent niche identity (no random content)",
                "CTA at end of every video: 'Follow for more [X]'",
            ],
            "metric": "Follower conversion rate (aim for 5-15%)",
        },
        {
            "stage": 3,
            "name": "Nurture",
            "goal": "Build trust and authority",
            "tactics": [
                "Stories / behind-the-scenes content",
                "Reply to every comment",
                "Q&A and poll content",
                "Valuable educational content they save and share",
            ],
            "metric": "Engagement rate (aim for 3-8%)",
        },
        {
            "stage": 4,
            "name": "Conversion",
            "goal": "Turn followers into buyers/leads",
            "tactics": [
                "Bio link to lead magnet or product",
                "Soft pitch content (social proof + offer)",
                "Limited-time promotions (urgency)",
                "Email list capture for owned audience",
            ],
            "metric": "Link clicks, leads, sales",
        },
        {
            "stage": 5,
            "name": "Retention",
            "goal": "Keep buyers buying and fans engaged",
            "tactics": [
                "Email sequences to nurture buyers",
                "Exclusive member content",
                "Product upsells and bundles",
                "Community building (Discord, Telegram)",
            ],
            "metric": "LTV (lifetime value per follower)",
        },
    ],
}

MULTI_PAGE_SYSTEM = {
    "concept": (
        "The real money in theme pages comes from SCALE. One page = one income stream. "
        "10 pages in different niches = 10 income streams. The system is replicable once proven."
    ),
    "phases": [
        {
            "phase": 1,
            "name": "Proof of Concept (Month 1-3)",
            "goal": "Build and monetize ONE page to $500+/month",
            "actions": [
                "Pick highest potential niche (motivation, fitness, finance)",
                "Build to 10K followers using proven content framework",
                "Set up affiliate links and digital product",
                "Document EXACTLY what worked (your Standard Operating Procedure)",
            ],
        },
        {
            "phase": 2,
            "name": "Replication (Month 4-6)",
            "goal": "Clone the system across 3-5 new pages",
            "actions": [
                "Hire a content editor / VA to handle repurposing ($5-15/hour)",
                "Systematize content: templated formats, scheduled posting",
                "Test 2-3 niches simultaneously — let data decide winners",
                "Reinvest revenue into tools (scheduling, analytics, content)",
            ],
        },
        {
            "phase": 3,
            "name": "Scale (Month 7-12)",
            "goal": "10+ pages running semi-autonomously",
            "actions": [
                "Full team: editor, scheduler, community manager",
                "Automate scheduling with Buffer, Later, or Metricool",
                "Introduce cross-promotion between your own pages",
                "Begin selling underperforming pages, keeping winners",
                "Explore your own product across all pages",
            ],
        },
    ],
    "tools": {
        "Scheduling": ["Buffer (free)", "Later (free tier)", "Metricool (free)", "Publer"],
        "Analytics": ["Meta Business Suite", "TikTok Analytics", "Social Blade", "HypeAuditor"],
        "Content": ["Canva Pro", "CapCut", "InShot", "Pexels/Pixabay (free stock)"],
        "Monetization": ["Beacons.ai (link-in-bio)", "Gumroad", "Patreon", "Linktree"],
        "Research": ["TrendTok", "Exploding Topics", "Google Trends", "Answer The Public"],
    },
}


def get_theme_page_blueprint(niche: str) -> dict:
    """Get a complete theme page creation blueprint for a given niche."""
    niche_data = THEME_PAGE_NICHES.get(niche.lower())
    if not niche_data:
        available = ", ".join(sorted(THEME_PAGE_NICHES.keys()))
        raise ValueError(f"Unknown niche '{niche}'. Available: {available}")

    return {
        "niche": niche,
        "niche_overview": niche_data,
        "setup_checklist": _get_setup_checklist(niche),
        "content_strategy": _get_content_strategy(niche),
        "monetization_roadmap": _get_monetization_roadmap(niche, niche_data),
        "conversion_funnel": CONVERSION_FUNNEL,
        "90_day_plan": _get_90_day_plan(niche),
    }


def get_monetization_strategy(method: str) -> dict:
    """Get detailed monetization strategy for a specific method."""
    method_data = MONETIZATION_METHODS.get(method.lower())
    if not method_data:
        available = ", ".join(MONETIZATION_METHODS.keys())
        raise ValueError(f"Unknown method '{method}'. Available: {available}")
    return {"method": method, **method_data}


def get_all_monetization_methods() -> list[dict]:
    """List all monetization methods with overview."""
    return [
        {
            "method": key,
            "description": val["description"],
            "difficulty": val["difficulty"],
            "startup_cost": val["startup_cost"],
            "time_to_first_dollar": val["time_to_first_dollar"],
            "follower_requirement": val["follower_requirement"],
            "income_ceiling": val["income_ceiling"],
        }
        for key, val in MONETIZATION_METHODS.items()
    ]


def get_conversion_funnel() -> dict:
    """Return the full 5-stage conversion funnel framework."""
    return CONVERSION_FUNNEL


def get_multi_page_scaling_plan() -> dict:
    """Return the multi-page theme account scaling blueprint."""
    return MULTI_PAGE_SYSTEM


def list_available_niches() -> list[str]:
    return sorted(THEME_PAGE_NICHES.keys())


def _get_setup_checklist(niche: str) -> list[dict]:
    return [
        {
            "step": 1,
            "task": "Choose platform",
            "detail": "TikTok for fastest growth (2026), Instagram for best monetization, YouTube Shorts for longevity",
            "time": "10 minutes",
        },
        {
            "step": 2,
            "task": "Create account",
            "detail": "Use a niche-descriptive handle (e.g., @daily_motivation_clips, @fitness_goals_daily)",
            "time": "5 minutes",
        },
        {
            "step": 3,
            "task": "Optimize profile",
            "detail": "Profile pic (logo or relevant image), bio with niche + CTA, link-in-bio page",
            "time": "30 minutes",
        },
        {
            "step": 4,
            "task": "Set up link-in-bio",
            "detail": "Create Beacons.ai or Linktree with: affiliate links, lead magnet, social links",
            "time": "1 hour",
        },
        {
            "step": 5,
            "task": "Source first 10 pieces of content",
            "detail": f"Find royalty-free content for {niche} niche from Pexels, YouTube (with permission), Reddit",
            "time": "2-3 hours",
        },
        {
            "step": 6,
            "task": "Create content templates",
            "detail": "Build 3 Canva/CapCut templates you can reuse: text overlay, quote card, montage",
            "time": "2 hours",
        },
        {
            "step": 7,
            "task": "Build content bank (10 posts)",
            "detail": "Have 10 posts ready before going live — consistency is critical at launch",
            "time": "4-6 hours",
        },
        {
            "step": 8,
            "task": "Set up affiliate accounts",
            "detail": f"Join relevant affiliate programs for {niche} niche",
            "time": "1-2 hours",
        },
        {
            "step": 9,
            "task": "Launch and post first 3 posts",
            "detail": "Post at peak hours. Engage with every comment for 2 hours post-publish",
            "time": "Ongoing",
        },
        {
            "step": 10,
            "task": "Start email list",
            "detail": "Use MailerLite (free up to 1K) or ConvertKit free tier — collect emails from day 1",
            "time": "1 hour setup",
        },
    ]


def _get_content_strategy(niche: str) -> dict:
    sourcing = THEME_PAGE_NICHES.get(niche.lower(), {}).get("content_sources", [])
    return {
        "content_sourcing": sourcing,
        "content_types": {
            "quote_cards": "Text overlay on aesthetic background (easiest to produce at scale)",
            "video_compilations": "Curated clips with music — high share potential",
            "tutorials": "Step-by-step how-tos — high save rate (algorithm loves this)",
            "news_commentary": "React to trending news in your niche — timely = viral",
            "user_generated": "Repost (with credit) user content — builds community",
        },
        "repurposing_workflow": [
            "Create one piece of 'pillar' content (60s video or carousel)",
            "Clip 3-4 short segments from it for TikTok/Reels/Shorts",
            "Pull key points for quote card posts",
            "Write caption as thread for Twitter/X",
            "Expand into email newsletter (if applicable)",
        ],
        "attribution_rules": [
            "Always credit original creator when repurposing their content",
            "Get written permission for any commercial repurposing",
            "Use royalty-free stock from Pexels, Unsplash, Pixabay for safety",
            "Add your own commentary/value to avoid pure re-upload copyright issues",
        ],
    }


def _get_monetization_roadmap(niche: str, niche_data: dict) -> list[dict]:
    affiliate_progs = niche_data.get("affiliate_programs", [])
    days = niche_data.get("time_to_monetize_days", 90)
    return [
        {
            "milestone": "Day 1",
            "action": "Set up affiliate accounts",
            "expected_revenue": "$0",
            "programs": affiliate_progs[:3],
        },
        {
            "milestone": f"Day {days // 3}",
            "action": "First affiliate commission from bio link clicks",
            "expected_revenue": "$10-$100",
            "programs": affiliate_progs,
        },
        {
            "milestone": f"Day {days}",
            "action": "Consistent affiliate income + first paid promotion inquiry",
            "expected_revenue": "$100-$500/month",
            "programs": [],
        },
        {
            "milestone": f"Month {days // 30 + 2}",
            "action": "Launch first digital product",
            "expected_revenue": "$500-$2,000/month",
            "programs": [],
        },
        {
            "milestone": "Month 6+",
            "action": "Multiple income streams running",
            "expected_revenue": niche_data.get("avg_monthly_revenue_range", "$500+"),
            "programs": [],
        },
    ]


def _get_90_day_plan(niche: str) -> list[dict]:
    return [
        {
            "days": "1-7",
            "focus": "Setup & Foundation",
            "goals": ["Account created and optimized", "10 posts in content bank", "Affiliate accounts active"],
            "kpi": "0 followers → 100 followers",
        },
        {
            "days": "8-30",
            "focus": "Content Volume & Consistency",
            "goals": ["Post 1-3x/day", "Engage 30 mins/day in niche", "Test 3 different content formats"],
            "kpi": "100 → 1,000 followers",
        },
        {
            "days": "31-60",
            "focus": "Engagement & First Revenue",
            "goals": ["First affiliate commission earned", "2 collabs/shoutout swaps done", "Email list started"],
            "kpi": "1,000 → 5,000 followers | $50-$500 revenue",
        },
        {
            "days": "61-90",
            "focus": "Monetization Activation",
            "goals": ["First digital product created", "First paid promo deal pitched", "Multi-platform presence"],
            "kpi": "5,000 → 10,000 followers | $500-$2,000 revenue",
        },
    ]
