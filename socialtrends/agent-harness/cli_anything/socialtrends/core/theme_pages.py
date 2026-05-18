"""Theme page creation, conversion strategy, and monetization guide.

A "theme page" is a social media account focused on a specific
niche/aesthetic rather than a personal brand. The account reposts,
curates, or creates content around a topic (luxury cars, fitness quotes,
travel aesthetics, etc.) and monetizes through multiple channels.

This module provides:
1. Profitable niche database with revenue potential data
2. Complete conversion funnel blueprints
3. Content sourcing strategies (legal + ethical)
4. Monetization method guides
5. Step-by-step growth playbook

Revenue potential based on aggregated creator economy data (2025–2026).
"""

from __future__ import annotations

# ── Profitable niches database ────────────────────────────────────────────────

PROFITABLE_NICHES: list[dict] = [
    {
        "name": "Luxury Lifestyle",
        "slug": "luxury",
        "difficulty": "medium",
        "competition": "high",
        "monetization_potential": "very high",
        "avg_rpm_per_1k_views": "$8–25",
        "typical_brand_deal_range": "$500–15,000 per post",
        "best_platforms": ["Instagram", "TikTok", "YouTube"],
        "content_types": [
            "Luxury cars & supercars",
            "Private jets & yachts",
            "High-end real estate tours",
            "Luxury watches & jewelry",
            "5-star hotel & resort content",
            "Billionaire lifestyle quotes",
        ],
        "target_audience": "Aspirational 18–35 year olds, entrepreneurs, finance bros",
        "top_monetization": ["Brand deals (luxury brands)", "Affiliate (luxury products)", "Info products"],
        "fastest_path_to_revenue": "Shoutouts to smaller luxury pages — $50–$500/post from day 30",
        "growth_speed": "Fast — aspirational content is naturally shareable",
    },
    {
        "name": "Fitness & Body Transformation",
        "slug": "fitness",
        "difficulty": "medium",
        "competition": "very high",
        "monetization_potential": "very high",
        "avg_rpm_per_1k_views": "$5–15",
        "typical_brand_deal_range": "$200–8,000 per post",
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
        "content_types": [
            "Before/after transformations",
            "Home workout videos",
            "Gym motivation clips",
            "Nutrition tips & meal preps",
            "Supplement reviews",
            "Fitness challenges (75Hard, etc.)",
        ],
        "target_audience": "18–40 year olds seeking physical transformation",
        "top_monetization": [
            "Supplement affiliate (8–15% commission — huge volume)",
            "Fitness program sales ($27–$297)",
            "Brand deals (supplement brands, gym wear)",
            "1-on-1 coaching upsell",
        ],
        "fastest_path_to_revenue": "Amazon affiliate for supplements + protein powder = $500–$2k/month at 50k followers",
        "growth_speed": "Fast — transformation content is extremely shareable",
    },
    {
        "name": "Personal Finance & Investing",
        "slug": "finance",
        "difficulty": "medium",
        "competition": "medium",
        "monetization_potential": "very high",
        "avg_rpm_per_1k_views": "$15–45",
        "typical_brand_deal_range": "$1,000–50,000 per post",
        "best_platforms": ["YouTube", "TikTok", "Instagram"],
        "content_types": [
            "Investing tips for beginners",
            "Side hustle income reports",
            "Budget breakdown (paycheck walkthroughs)",
            "How I make $X/month passive income",
            "Stock market explanations",
            "Real estate investing basics",
        ],
        "target_audience": "22–40 year olds wanting to build wealth",
        "top_monetization": [
            "Trading app affiliate (Robinhood, Webull — $50–100/referral)",
            "Online course sales ($97–$997)",
            "Financial SaaS affiliate (budgeting apps, tax software)",
            "High-value brand deals (fintech companies)",
        ],
        "fastest_path_to_revenue": "Referral programs — some pay $100+ per signup with minimal followers",
        "growth_speed": "Medium — educational content slower but extremely sticky",
    },
    {
        "name": "Motivation & Mindset",
        "slug": "motivation",
        "difficulty": "easy",
        "competition": "very high",
        "monetization_potential": "medium",
        "avg_rpm_per_1k_views": "$3–8",
        "typical_brand_deal_range": "$100–3,000 per post",
        "best_platforms": ["Instagram", "TikTok", "YouTube"],
        "content_types": [
            "Quote graphics with cinematic background",
            "Motivational speech clips (fair use)",
            "Success story shorts",
            "Daily mindset tips",
            "Book summary clips",
        ],
        "target_audience": "Students, entrepreneurs, anyone feeling stuck (age 16–35)",
        "top_monetization": [
            "Shoutouts (scale to $500+/day at 100k+)",
            "E-book / digital product ($17–$47)",
            "Affiliate for self-help products/books",
            "Brand deals (productivity apps, journals)",
        ],
        "fastest_path_to_revenue": "Sell shoutouts at 10k followers — charge $20–50/post",
        "growth_speed": "Very fast — quote content goes viral easily",
    },
    {
        "name": "Travel & Adventure",
        "slug": "travel",
        "difficulty": "medium",
        "competition": "high",
        "monetization_potential": "high",
        "avg_rpm_per_1k_views": "$6–18",
        "typical_brand_deal_range": "$500–25,000 per post",
        "best_platforms": ["Instagram", "TikTok", "YouTube"],
        "content_types": [
            "Aesthetic destination clips (repost with credit)",
            "Budget travel tips",
            "Hidden gems / underrated destinations",
            "Hotel & hostel reviews",
            "Packing tips",
            "Cheapest flights hacks",
        ],
        "target_audience": "18–35 year olds who dream of traveling",
        "top_monetization": [
            "Travel booking affiliate (Booking.com, Airbnb — 4–25%)",
            "Flight deal affiliate (Scott's Cheap Flights, etc.)",
            "Brand deals (luggage, travel apps, airlines)",
            "Travel photography presets ($15–$50)",
        ],
        "fastest_path_to_revenue": "Affiliate links in bio from day 1 — travel affiliate pays on every booking",
        "growth_speed": "Medium — requires good visual content",
    },
    {
        "name": "Real Estate",
        "slug": "real_estate",
        "difficulty": "medium",
        "competition": "medium",
        "monetization_potential": "very high",
        "avg_rpm_per_1k_views": "$12–35",
        "typical_brand_deal_range": "$1,000–30,000 per post",
        "best_platforms": ["TikTok", "YouTube", "Instagram"],
        "content_types": [
            "Luxury home tours (with or without agent partnership)",
            "Real estate investing tips",
            "First-time homebuyer guides",
            "House flipping transformations",
            "Market updates & analysis",
            "Rental property income breakdowns",
        ],
        "target_audience": "25–45 year olds interested in property/investing",
        "top_monetization": [
            "Real estate lead gen (sell leads to agents — $50–500/lead)",
            "Course sales ($297–$1,997 on investing strategies)",
            "Mortgage affiliate ($500–$2,000/referral)",
            "Brand deals (proptech companies, home improvement brands)",
        ],
        "fastest_path_to_revenue": "Partner with local real estate agents — they pay for leads immediately",
        "growth_speed": "Medium — high-value audience makes up for slower growth",
    },
    {
        "name": "Food & Recipe",
        "slug": "food",
        "difficulty": "easy",
        "competition": "very high",
        "monetization_potential": "medium-high",
        "avg_rpm_per_1k_views": "$4–12",
        "typical_brand_deal_range": "$200–5,000 per post",
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
        "content_types": [
            "Quick recipes (60 seconds or less)",
            "Budget meals (eating healthy for $X/day)",
            "Viral food trends & reactions",
            "Restaurant reviews",
            "Meal prep walkthroughs",
            "International cuisine exploration",
        ],
        "target_audience": "18–45 home cooks looking for inspiration",
        "top_monetization": [
            "Kitchen equipment affiliate (Amazon — high purchase intent)",
            "Meal kit affiliate (HelloFresh, etc. — $20–50/referral)",
            "Cookbook / recipe ebook ($12–$37)",
            "Brand deals (food brands, cookware companies)",
        ],
        "fastest_path_to_revenue": "Amazon affiliate for kitchen tools — high conversion + no follower minimum",
        "growth_speed": "Fast — food content naturally viral",
    },
    {
        "name": "Pets & Animals",
        "slug": "pets",
        "difficulty": "easy",
        "competition": "high",
        "monetization_potential": "medium",
        "avg_rpm_per_1k_views": "$3–10",
        "typical_brand_deal_range": "$100–5,000 per post",
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
        "content_types": [
            "Funny/cute animal clips (repost, fair use credit)",
            "Pet care tips & tricks",
            "Dog/cat product reviews",
            "Before/after rescue stories",
            "Training tutorials",
        ],
        "target_audience": "Pet owners aged 18–55",
        "top_monetization": [
            "Pet product affiliate (Chewy, Amazon Pets — huge spend)",
            "Pet insurance affiliate ($30–80/referral)",
            "Brand deals (pet food, accessories)",
            "Merchandise (cute pet-themed products)",
        ],
        "fastest_path_to_revenue": "Chewy affiliate + Amazon — pet owners buy consistently",
        "growth_speed": "Very fast — cute animal content reliably goes viral",
    },
    {
        "name": "Tech & AI",
        "slug": "tech",
        "difficulty": "medium",
        "competition": "medium",
        "monetization_potential": "very high",
        "avg_rpm_per_1k_views": "$10–30",
        "typical_brand_deal_range": "$500–20,000 per post",
        "best_platforms": ["YouTube", "TikTok", "Twitter/X"],
        "content_types": [
            "AI tool tutorials & reviews",
            "Tech gadget unboxings",
            "Productivity software tips",
            "Coding shortcuts",
            "Tech news explainers",
            "Futurism / AI predictions",
        ],
        "target_audience": "18–40 year old tech enthusiasts, professionals, entrepreneurs",
        "top_monetization": [
            "SaaS affiliate (AI tools, productivity apps — 20–40% recurring)",
            "Brand deals (tech companies — highest CPM niche)",
            "Online courses ($197–$997 on AI/tech skills)",
            "YouTube AdSense (very high CPM niche)",
        ],
        "fastest_path_to_revenue": "SaaS affiliate — tools like Jasper, Notion, etc. pay recurring commissions",
        "growth_speed": "Fast in 2024–2026 due to AI hype cycle",
    },
]


# ── Conversion strategy blueprints ────────────────────────────────────────────

CONVERSION_STRATEGIES: dict[str, dict] = {
    "link_in_bio_funnel": {
        "name": "Link-in-Bio Conversion Funnel",
        "difficulty": "beginner",
        "tools": ["Linktree (free)", "Beacons (free)", "Stan Store ($29/mo)", "Gumroad (free)"],
        "steps": [
            "1. Set up Linktree/Beacons with 3–5 key links",
            "2. Link 1: Lead magnet (free guide/checklist) → captures email",
            "3. Link 2: Main product/service (paid offer)",
            "4. Link 3: Community (Discord, Telegram, Patreon)",
            "5. Link 4: Best content (viral post or YouTube video)",
            "6. In every caption: 'Link in bio for [specific benefit]'",
            "7. In every TikTok/Reel: mention 'link in bio' verbally",
        ],
        "conversion_rate_benchmark": "1–3% of profile visitors click through",
        "revenue_potential": "If 100 people/day visit profile → 1–3 email signups → $0.50–2 per email/month",
    },
    "story_funnel": {
        "name": "Instagram/TikTok Story Funnel",
        "difficulty": "intermediate",
        "tools": ["Instagram Stories with Link sticker", "TikTok Series", "ManyChat DM automation"],
        "steps": [
            "1. Post a regular feed post teasing a secret tip/resource",
            "2. In caption: 'Comment WORD for access' or 'DM me WORD'",
            "3. Use ManyChat to auto-reply with link when someone comments the word",
            "4. Link leads to landing page with opt-in form",
            "5. Once on email list: automated sequence → pitch product at email 3–5",
            "6. Story series: Day 1 problem agitation, Day 2 solution preview, Day 3 offer",
        ],
        "conversion_rate_benchmark": "Comment trigger campaigns get 10–40% DM opt-in rate",
        "revenue_potential": "Best converting funnel for Instagram — used by 7-figure creators",
    },
    "email_list_building": {
        "name": "Email List as Core Asset",
        "difficulty": "intermediate",
        "tools": ["ConvertKit (free up to 1k)", "Mailchimp (free)", "Beehiiv ($42/mo)", "Substack (free)"],
        "steps": [
            "1. Create a high-value lead magnet (PDF guide, template, checklist, mini-course)",
            "2. Make the lead magnet extremely specific: 'The 7-Day Fitness Plan for Busy Moms'",
            "3. Drive ALL platforms to the email opt-in page",
            "4. Set up 5-email welcome sequence:",
            "   Email 1: Deliver lead magnet + who you are",
            "   Email 2: Share your best piece of content (builds trust)",
            "   Email 3: Common mistake in your niche + how to avoid",
            "   Email 4: Social proof / transformation story",
            "   Email 5: Pitch your core product",
            "5. Weekly email to keep list warm",
            "6. Monetize via affiliate promotions + own products",
        ],
        "conversion_rate_benchmark": "Email list = $1–5 per subscriber per month (industry average)",
        "revenue_potential": "1,000 email subscribers → $1,000–5,000/month potential",
    },
    "shoutout_model": {
        "name": "Shoutout / Paid Promotion Model",
        "difficulty": "beginner",
        "tools": ["Shoutcart", "FameBit (YouTube)", "DM-based negotiation"],
        "steps": [
            "1. Grow account to 10k+ followers in a clear niche",
            "2. Create a media kit (follower count, ER%, niche, audience demographics)",
            "3. Set pricing: 10k followers = $20–50/post, 100k = $200–500, 1M = $2k+",
            "4. List on Shoutcart or reach out directly to brands in your niche",
            "5. Also sell shoutouts to smaller accounts wanting to grow",
            "6. Create packages: Story shoutout ($X), Feed post ($Y), Video mention ($Z)",
        ],
        "conversion_rate_benchmark": "Shoutouts convert 0.5–2% of audience to page visits",
        "revenue_potential": "100k followers, 1 shoutout/day = $100–500/day = $3k–15k/month",
    },
    "digital_products": {
        "name": "Digital Product Sales Funnel",
        "difficulty": "intermediate",
        "tools": ["Gumroad (free)", "Stan Store ($29/mo)", "Teachable ($39/mo)", "Lemon Squeezy"],
        "steps": [
            "1. Identify your audience's #1 pain point in your niche",
            "2. Create a digital product that solves it:",
            "   - PDF guide: $7–$37 (low price, high volume)",
            "   - Template pack: $17–$67 (Notion, Canva, Excel)",
            "   - Mini-course (5–10 videos): $47–$197",
            "   - Full course: $197–$997",
            "3. Create a simple sales page on Gumroad/Stan Store",
            "4. Feature the product in 30% of your content",
            "5. Create dedicated 'pitch content' (shows what's inside the product)",
            "6. Testimonials from beta users → social proof loop",
        ],
        "conversion_rate_benchmark": "0.1–0.5% of followers buy a digital product per month",
        "revenue_potential": "100k followers × 0.2% × $47 average = $9,400/month",
    },
    "affiliate_marketing": {
        "name": "Affiliate Marketing Flywheel",
        "difficulty": "beginner",
        "tools": ["Amazon Associates", "ShareASale", "Commission Junction", "Impact.com", "PartnerStack"],
        "steps": [
            "1. Sign up for affiliate programs in your niche (Amazon requires no minimum)",
            "2. Create authentic product review/comparison content",
            "3. Link in bio → affiliate landing page with multiple product links",
            "4. Create a 'favorites' or 'shop my picks' Linktree page",
            "5. Add affiliate links to all relevant content captions/descriptions",
            "6. YouTube: affiliate links in description are highest converting",
            "7. Track what converts → double down on those products/categories",
            "8. Build comparison content ('Product A vs Product B') — high buyer intent",
        ],
        "conversion_rate_benchmark": "1–5% of clicks convert to purchases",
        "revenue_potential": "50k followers, fitness niche → $500–$3,000/month affiliate",
    },
}


# ── Content sourcing guide ────────────────────────────────────────────────────

CONTENT_SOURCING: dict[str, dict] = {
    "repost_with_credit": {
        "method": "Repost & Credit Original Creator",
        "legality": "Generally safe when crediting — but NOT a long-term strategy",
        "how_to": [
            "Always credit original creator in caption (@username)",
            "Only repost viral content (1M+ views) for reach",
            "Add your own commentary, insight, or caption value",
            "DM original creators for permission when possible",
            "Never monetize purely reposted content with ads",
        ],
        "risk": "Copyright claim risk — some creators DMCA aggressively",
        "recommendation": "Use only as a starting strategy (first 30 days) while building original content pipeline",
    },
    "royalty_free_content": {
        "method": "Royalty-Free & Creative Commons Content",
        "legality": "Fully safe when following license terms",
        "sources": [
            "Pexels (free stock video + photos, commercial use OK)",
            "Pixabay (free, commercial use OK)",
            "Unsplash (photos only, commercial use OK)",
            "Videvo (free video clips, check license per clip)",
            "NASA Media Library (US government, fully public domain)",
            "Archive.org (public domain films, music, etc.)",
            "YouTube Creative Commons filter (reuse allowed videos)",
        ],
        "how_to": [
            "Search for your niche keywords on Pexels/Pixabay",
            "Download HD video clips",
            "Edit together with CapCut or DaVinci Resolve",
            "Add trending music + captions + your unique commentary",
        ],
        "recommendation": "Best sustainable sourcing method for theme pages",
    },
    "user_generated_content": {
        "method": "UGC (User-Generated Content) Curation",
        "legality": "Safe when getting permission or using within platform tools (Collab posts)",
        "how_to": [
            "Run a hashtag campaign in your niche",
            "Feature community submissions — builds community AND content",
            "Instagram Collabs: co-author posts with other creators",
            "TikTok Duet/Stitch: adds your reaction to existing viral content",
            "Always get written permission before cross-platform reposting",
        ],
        "recommendation": "Excellent at 10k+ followers — scales with community",
    },
    "original_content": {
        "method": "Original Content Creation",
        "legality": "100% yours",
        "tools": [
            "CapCut (free, mobile — best for TikTok/Reels)",
            "Canva Pro (graphics, carousels, quote cards)",
            "DaVinci Resolve (free, professional video editing)",
            "ElevenLabs (AI voiceover — $5/mo)",
            "Pictory.ai (text → video — $19/mo)",
            "Descript (screen recording + AI voice cloning)",
        ],
        "content_angles": [
            "Educational: 'How to do X in 60 seconds'",
            "Listicle: 'Top 5 X you didn't know about'",
            "Before/after: show transformation (fitness, design, etc.)",
            "Reaction: react to trending content in your niche",
            "Storytime: personal story with niche lesson",
            "Tutorial: step-by-step how-to",
        ],
        "recommendation": "Only path to sustainable, monetizable, brand-safe growth",
    },
}


# ── Growth playbook ────────────────────────────────────────────────────────────

GROWTH_PLAYBOOKS: dict[str, list[dict]] = {
    "0_to_10k": [
        {"week": "1–2", "focus": "Setup & Research", "actions": [
            "Choose ONE niche and ONE primary platform",
            "Create optimized profile (bio, link, profile pic)",
            "Study top 10 accounts in your niche — what works?",
            "Post 3 test videos in different formats to see what resonates",
            "Spend 1h/day engaging with your target audience's content",
        ]},
        {"week": "3–4", "focus": "Volume & Consistency", "actions": [
            "Post 1–2 times/day (never miss a day)",
            "Use trending sounds within 24h of them peaking",
            "Spend 30min/day on comment engagement (reply to everyone)",
            "Study your analytics: which content got most views? Double down.",
            "Batch create 1 week of content on weekends",
        ]},
        {"week": "5–8", "focus": "Virality Hunting", "actions": [
            "Create 1 viral-attempt video per day (high hook, trending topic)",
            "Repurpose each TikTok to Instagram Reels and YouTube Shorts",
            "Reach 10 creators in your niche for engagement pods",
            "Run a giveaway requiring follow + share (cheap follower boost)",
            "Start capturing emails — add lead magnet to bio",
        ]},
    ],
    "10k_to_100k": [
        {"phase": "Content Upgrade", "actions": [
            "Improve production quality — better lighting, audio, editing",
            "Develop a signature content format you're known for",
            "Create a series (5-part educational series keeps viewers returning)",
            "Start cross-platform repurposing systematically",
        ]},
        {"phase": "Community Building", "actions": [
            "Respond to every comment — builds loyal community",
            "Go Live 1–2x/week (TikTok Lives get extra distribution)",
            "Start Discord/Telegram community — deepens audience",
            "Feature community members in content — massive loyalty",
        ]},
        {"phase": "Monetization Activation", "actions": [
            "Launch first digital product (start small: $7–$27)",
            "Apply for all platform monetization programs",
            "Reach out to 10 brands in your niche for deals",
            "Sign up for top 3 affiliate programs in your niche",
        ]},
    ],
    "100k_plus": [
        {"phase": "Systematize & Scale", "actions": [
            "Hire a video editor ($300–$1,000/month)",
            "Create content calendar 2 weeks ahead",
            "Expand to adjacent niches without losing core audience",
            "Launch second account in adjacent niche (clone winning formula)",
        ]},
        {"phase": "Revenue Diversification", "actions": [
            "Launch premium course ($197–$997)",
            "Build Patreon/membership ($5–$50/month subscription)",
            "Speaking engagements / consulting",
            "Write a book or comprehensive guide",
            "White-label products in your niche",
        ]},
    ],
}


# ── Public API ────────────────────────────────────────────────────────────────

def list_niches(sort_by: str = "monetization") -> list[dict]:
    """List all profitable niches.

    Args:
        sort_by: "monetization", "difficulty", or "growth_speed"

    Returns:
        List of niche dicts
    """
    niches = PROFITABLE_NICHES[:]
    order = {"very high": 0, "high": 1, "medium-high": 2, "medium": 3, "low": 4}
    if sort_by == "monetization":
        niches.sort(key=lambda n: order.get(n["monetization_potential"], 9))
    elif sort_by == "difficulty":
        d_order = {"easy": 0, "medium": 1, "hard": 2}
        niches.sort(key=lambda n: d_order.get(n["difficulty"], 9))
    return niches


def get_niche(slug: str) -> dict:
    """Get full details for a specific niche.

    Args:
        slug: Niche slug (luxury, fitness, finance, etc.)

    Returns:
        Niche dict or error
    """
    for n in PROFITABLE_NICHES:
        if n["slug"] == slug.lower() or n["name"].lower() == slug.lower():
            return n
    return {"error": f"Niche '{slug}' not found.", "available": [n["slug"] for n in PROFITABLE_NICHES]}


def get_conversion_strategy(strategy: str) -> dict:
    """Get a full conversion strategy blueprint.

    Args:
        strategy: link_in_bio_funnel, story_funnel, email_list_building,
                  shoutout_model, digital_products, affiliate_marketing

    Returns:
        Strategy blueprint dict
    """
    result = CONVERSION_STRATEGIES.get(strategy)
    if not result:
        return {
            "error": f"Strategy '{strategy}' not found.",
            "available": list(CONVERSION_STRATEGIES.keys()),
        }
    return result


def list_conversion_strategies() -> list[dict]:
    """List all available conversion strategies with brief summaries."""
    return [
        {
            "slug": k,
            "name": v["name"],
            "difficulty": v["difficulty"],
            "revenue_potential": v["revenue_potential"],
        }
        for k, v in CONVERSION_STRATEGIES.items()
    ]


def get_content_sourcing_guide(method: str | None = None) -> dict:
    """Get content sourcing guidance.

    Args:
        method: repost_with_credit, royalty_free_content, user_generated_content, original_content
                (None = return all methods summary)

    Returns:
        Content sourcing guide dict
    """
    if method:
        result = CONTENT_SOURCING.get(method)
        if not result:
            return {"error": f"Method '{method}' not found.", "available": list(CONTENT_SOURCING.keys())}
        return result
    return {k: {"method": v["method"], "legality": v["legality"], "recommendation": v["recommendation"]}
            for k, v in CONTENT_SOURCING.items()}


def get_growth_playbook(stage: str = "0_to_10k") -> list[dict]:
    """Get the growth playbook for a follower milestone range.

    Args:
        stage: 0_to_10k, 10k_to_100k, or 100k_plus

    Returns:
        List of phase/week action dicts
    """
    playbook = GROWTH_PLAYBOOKS.get(stage)
    if not playbook:
        return [{"error": f"Stage '{stage}' not found.", "available": list(GROWTH_PLAYBOOKS.keys())}]
    return playbook


def get_monetization_timeline(niche_slug: str, followers: int) -> dict:
    """Estimate realistic revenue based on niche and follower count.

    Args:
        niche_slug: Niche identifier
        followers: Current follower count

    Returns:
        Dict with revenue estimates and next milestone actions
    """
    niche = get_niche(niche_slug)
    if "error" in niche:
        return niche

    revenue_estimates: dict[str, str] = {}

    if followers < 1000:
        revenue_estimates = {
            "affiliate_marketing": "$0–$50/month (start now, volume comes later)",
            "shoutouts": "Not yet — need 10k minimum",
            "brand_deals": "Not yet",
            "digital_products": "Can launch, but low traffic = low sales ($0–$100)",
        }
        next_milestone = "Focus 100% on growth. Post daily. Target 10k."
    elif followers < 10000:
        revenue_estimates = {
            "affiliate_marketing": "$50–$300/month",
            "shoutouts": "Starting to attract micro-deals — $20–100/post",
            "brand_deals": "Micro brand deals possible ($50–$500/post)",
            "digital_products": "$100–$1,000/month with consistent promotion",
        }
        next_milestone = "Launch your first digital product. Build email list."
    elif followers < 100000:
        revenue_estimates = {
            "affiliate_marketing": "$300–$3,000/month",
            "shoutouts": "$100–$1,000/post depending on niche",
            "brand_deals": f"$500–$5,000/post ({niche['typical_brand_deal_range']})",
            "digital_products": "$1,000–$10,000/month",
            "platform_monetization": "$100–$1,000/month (YouTube/TikTok Creator Fund)",
        }
        next_milestone = "Scale content production. Apply to creator programs. Launch a course."
    else:
        revenue_estimates = {
            "affiliate_marketing": "$3,000–$20,000+/month",
            "shoutouts": "$500–$5,000/post",
            "brand_deals": f"{niche['typical_brand_deal_range']} per post",
            "digital_products": "$10,000–$100,000+/month",
            "platform_monetization": "$1,000–$10,000+/month",
            "speaking_consulting": "$2,000–$20,000/event",
        }
        next_milestone = "Hire a team. Systematize. Launch a premium course or membership."

    return {
        "niche": niche["name"],
        "followers": followers,
        "revenue_estimates": revenue_estimates,
        "fastest_path": niche.get("fastest_path_to_revenue", ""),
        "next_milestone_actions": next_milestone,
        "top_monetization_for_niche": niche.get("top_monetization", []),
    }
