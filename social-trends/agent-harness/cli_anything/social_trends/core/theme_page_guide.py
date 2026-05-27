"""Theme page creation & conversion guide.

Covers: niche selection, content sourcing, account setup, audience building,
and the complete monetisation/conversion funnel for theme pages.

'Theme pages' (also called niche pages) are social media accounts that curate
and create content around a specific topic. 'Converting' means turning
followers into revenue through affiliate marketing, shoutouts, digital
products, DM funnels, and other strategies.
"""

from __future__ import annotations

# ── Niche data ────────────────────────────────────────────────────────────────

NICHES = {
    "motivation": {
        "description": "Quotes, mindset, hustle culture, success stories",
        "platforms": ["instagram", "tiktok", "twitter"],
        "competition": "high",
        "monetisation": ["shoutouts", "digital-products", "affiliate"],
        "content_types": ["quote graphics", "short clips", "transformation stories"],
        "avg_cpm": "$3-8",
        "viral_potential": "high",
    },
    "fitness": {
        "description": "Workouts, nutrition, body transformation, supplements",
        "platforms": ["tiktok", "instagram", "youtube"],
        "competition": "very-high",
        "monetisation": ["affiliate", "coaching", "digital-products", "brand-deals"],
        "content_types": ["workout clips", "before/after", "recipe videos", "tips"],
        "avg_cpm": "$5-15",
        "viral_potential": "high",
    },
    "finance": {
        "description": "Investing, budgeting, side hustles, financial freedom",
        "platforms": ["tiktok", "youtube", "instagram"],
        "competition": "medium",
        "monetisation": ["affiliate", "courses", "newsletter", "brand-deals"],
        "content_types": ["tips carousels", "explainers", "income breakdowns"],
        "avg_cpm": "$15-40",
        "viral_potential": "medium",
    },
    "luxury": {
        "description": "Cars, watches, fashion, travel, lifestyle flexing",
        "platforms": ["instagram", "tiktok", "youtube"],
        "competition": "medium",
        "monetisation": ["shoutouts", "brand-deals", "affiliate"],
        "content_types": ["showcases", "reviews", "vlogs"],
        "avg_cpm": "$8-20",
        "viral_potential": "high",
    },
    "travel": {
        "description": "Destinations, travel hacks, vanlife, digital nomad",
        "platforms": ["tiktok", "instagram", "youtube"],
        "competition": "high",
        "monetisation": ["affiliate", "presets", "brand-deals", "courses"],
        "content_types": ["destination reels", "travel tips", "packing hacks"],
        "avg_cpm": "$5-12",
        "viral_potential": "high",
    },
    "pets": {
        "description": "Dogs, cats, funny animal moments",
        "platforms": ["tiktok", "instagram", "youtube"],
        "competition": "medium",
        "monetisation": ["shoutouts", "affiliate", "merch"],
        "content_types": ["cute clips", "training tips", "product reviews"],
        "avg_cpm": "$3-8",
        "viral_potential": "very-high",
    },
    "relationships": {
        "description": "Dating advice, red flags, relationship tips, breakups",
        "platforms": ["tiktok", "instagram"],
        "competition": "medium",
        "monetisation": ["courses", "consulting", "digital-products"],
        "content_types": ["advice clips", "reenactments", "story time"],
        "avg_cpm": "$4-10",
        "viral_potential": "very-high",
    },
    "cooking": {
        "description": "Recipes, meal prep, food hacks, restaurant reviews",
        "platforms": ["tiktok", "instagram", "youtube"],
        "competition": "high",
        "monetisation": ["affiliate", "brand-deals", "cookbook", "courses"],
        "content_types": ["recipe reels", "time-lapses", "reviews"],
        "avg_cpm": "$4-10",
        "viral_potential": "high",
    },
    "memes": {
        "description": "Pop culture memes, relatable humour, commentary",
        "platforms": ["instagram", "twitter", "tiktok"],
        "competition": "very-high",
        "monetisation": ["shoutouts", "paid-promos"],
        "content_types": ["meme reposts", "edits", "reaction clips"],
        "avg_cpm": "$1-5",
        "viral_potential": "very-high",
    },
    "crypto-nft": {
        "description": "Crypto, web3, NFT news and analysis",
        "platforms": ["twitter", "tiktok", "youtube"],
        "competition": "medium",
        "monetisation": ["affiliate", "courses", "paid-communities", "consulting"],
        "content_types": ["news updates", "analysis", "tutorials"],
        "avg_cpm": "$20-60",
        "viral_potential": "medium",
    },
    "fashion": {
        "description": "Style tips, outfit inspiration, brand reviews, thrift hauls",
        "platforms": ["tiktok", "instagram", "youtube"],
        "competition": "high",
        "monetisation": ["affiliate", "brand-deals", "presets"],
        "content_types": ["OOTD", "hauls", "try-ons", "styling tips"],
        "avg_cpm": "$5-15",
        "viral_potential": "high",
    },
    "study-productivity": {
        "description": "Study tips, productivity hacks, note-taking, student life",
        "platforms": ["tiktok", "youtube", "instagram"],
        "competition": "medium",
        "monetisation": ["digital-products", "affiliate", "courses"],
        "content_types": ["study with me", "tips carousels", "app reviews"],
        "avg_cpm": "$4-10",
        "viral_potential": "medium",
    },
}

# ── Content sourcing strategies ───────────────────────────────────────────────

SOURCING_STRATEGIES = {
    "repost_with_credit": {
        "name": "Repost with Credit",
        "description": "Curate viral content from others, always credit original creator",
        "effort": "low",
        "originality": "low",
        "risk": "medium (copyright claims possible)",
        "best_for": ["memes", "motivation", "pets", "luxury"],
        "steps": [
            "Find viral content in your niche using in-app trending pages",
            "Save/download with a tool (CapCut, Repost apps)",
            "Add your watermark or small branding overlay",
            "Credit original creator in caption",
            "Post consistently — 3-5x daily for theme pages",
        ],
    },
    "original_branded_content": {
        "name": "Original Branded Content",
        "description": "Create your own content with a consistent aesthetic/style",
        "effort": "high",
        "originality": "high",
        "risk": "low",
        "best_for": ["fitness", "cooking", "finance", "fashion", "travel"],
        "steps": [
            "Define your unique angle/POV before filming anything",
            "Batch-film 20-30 pieces of content per session",
            "Edit with consistent fonts, colours, and music style",
            "Apply content templates to maintain aesthetic",
            "Schedule posts via Buffer/Later for consistency",
        ],
    },
    "aggregator_compilations": {
        "name": "Compilation Aggregator",
        "description": "Edit multiple viral clips together into themed compilations",
        "effort": "medium",
        "originality": "medium",
        "risk": "medium",
        "best_for": ["motivation", "pets", "luxury", "travel"],
        "steps": [
            "Search keywords on TikTok/YouTube for source clips",
            "Download clips (ensure they are CC-licensed or get permission)",
            "Edit into 30-60s themed compilation with music",
            "Add branding intro/outro (2-3s each)",
            "Include 'Follow for daily [niche]' CTA on screen",
        ],
    },
    "ai_assisted": {
        "name": "AI-Assisted Content",
        "description": "Use AI tools to help script, write captions, and generate graphics",
        "effort": "low-medium",
        "originality": "medium",
        "risk": "low",
        "best_for": ["motivation", "finance", "study-productivity", "relationships"],
        "steps": [
            "Use Claude/ChatGPT to generate scripts and captions in bulk",
            "Use Canva/Adobe Express for branded quote graphics",
            "Use ElevenLabs for voiceovers",
            "Use CapCut for auto-captions and editing",
            "Always review and add your personality before posting",
        ],
    },
}

# ── Conversion/monetisation strategies ───────────────────────────────────────

MONETISATION_STRATEGIES = {
    "shoutouts": {
        "name": "Shoutout for Shoutout (S4S) & Paid Shoutouts",
        "min_followers": 5_000,
        "description": "Charge other accounts in your niche to promote them to your audience",
        "rates": {
            "5K-10K followers": "$20-75 per post",
            "10K-50K followers": "$75-300 per post",
            "50K-100K followers": "$300-800 per post",
            "100K+ followers": "$800-3000+ per post",
        },
        "implementation": [
            "Create a simple media kit (screenshot of stats + rates)",
            "DM theme pages in your niche offering paid S4S",
            "Use Telegram groups for theme page deals (search '[niche] theme page')",
            "Post 'DM for promo' or 'Promotion available' in bio",
            "Track results and adjust rates quarterly",
        ],
    },
    "affiliate_marketing": {
        "name": "Affiliate Marketing",
        "min_followers": 100,
        "description": "Earn commission by promoting products your audience wants to buy",
        "platforms": ["Amazon Associates (3-10%)", "ShareASale", "Impact",
                      "ClickBank (20-75%)", "CJ Affiliate",
                      "Brand-direct affiliate programmes"],
        "implementation": [
            "Sign up for 2-3 affiliate programmes in your niche",
            "Add your affiliate link to bio link tool (Linktree/Beacons)",
            "Create 'link in bio' CTAs in every piece of content",
            "Review/recommend products organically in content",
            "Build a landing page with your top product recommendations",
            "Email list converts affiliate offers 5-10x better than social",
        ],
        "tips": [
            "Only promote products you believe in — audience trust is your asset",
            "Disclose affiliate relationships (#ad or 'affiliate link')",
            "High-ticket affiliate programmes ($100-500+ commissions) > low-ticket",
        ],
    },
    "digital_products": {
        "name": "Digital Products",
        "min_followers": 500,
        "description": "Sell your own e-books, templates, presets, courses, or guides",
        "product_ideas": {
            "motivation": ["Mindset Journal PDF", "Morning Routine Guide", "Goal-Setting Workbook"],
            "fitness": ["Workout Plan PDF", "Meal Prep Guide", "Progress Tracker"],
            "finance": ["Budget Spreadsheet", "Investing Starter Guide", "Side Hustle Playbook"],
            "travel": ["Travel Hacking Guide", "Packing List Template", "Destination Guides"],
            "fashion": ["Capsule Wardrobe Guide", "Style Templates", "Thrifting Guide"],
            "study-productivity": ["Study Schedule Templates", "Note-Taking System", "Flashcard Packs"],
        },
        "platforms": ["Gumroad", "Stan Store", "Payhip", "Podia", "Lemon Squeezy"],
        "implementation": [
            "Create your first product in Canva or Google Docs — 1 weekend",
            "Price between $7-47 for entry-level products",
            "Add to link-in-bio immediately — start collecting purchases",
            "Create a free lead magnet to build email list first",
            "Upsell from free lead magnet to paid product via email sequence",
        ],
    },
    "paid_community": {
        "name": "Paid Community / Subscription",
        "min_followers": 1_000,
        "description": "Charge monthly for exclusive content, group access, or mentorship",
        "platforms": ["Patreon", "Discord (role-gated)", "Telegram Premium",
                      "Substack", "Circle.so"],
        "pricing": "$5-97/month depending on value provided",
        "implementation": [
            "Start with Patreon or Discord at $9.99/month",
            "Offer exclusive: early content, live Q&As, templates, community",
            "Announce to your existing audience first",
            "Aim for 50 paying members = $500/month recurring base",
        ],
    },
    "brand_deals": {
        "name": "Brand Sponsorships & Partnerships",
        "min_followers": 3_000,
        "description": "Paid collaborations with brands in your niche",
        "implementation": [
            "Create a media kit: stats, demographics, examples, rates",
            "Reach out to 10 brands/week via DM or email",
            "Use AspireIQ, Creator.co, or Influencer.co to find deals",
            "Charge: followers / 100 as minimum $/post (e.g. 10K = $100)",
            "Negotiate: story + post bundle, affiliate bonus, exclusivity fees",
            "Always disclose sponsored content (#ad, #sponsored)",
        ],
    },
    "dm_funnel": {
        "name": "DM Funnel / Lead Generation",
        "min_followers": 500,
        "description": "Use automated or manual DMs to convert followers into buyers",
        "implementation": [
            "CTA in content: 'Comment [keyword] and I'll DM you the free guide'",
            "Use ManyChat to auto-send resources when followers comment a keyword",
            "DM sequence: Day 0 — send freebie, Day 1 — follow-up value, Day 3 — offer",
            "Personalise DMs — never send copy-paste spam",
            "Track open rates and optimise your message",
        ],
        "tools": ["ManyChat (comment automation)", "Manychat DM flows",
                  "Instagram/TikTok native DMs", "Beehiiv for email follow-up"],
    },
}

# ── Setup checklist ───────────────────────────────────────────────────────────

SETUP_CHECKLIST = [
    {
        "step": 1,
        "title": "Choose Your Niche",
        "tasks": [
            "Pick a niche you can create content about for 12+ months",
            "Verify there's an audience: search the niche on TikTok/IG",
            "Verify there's money: check what brands advertise in the niche",
            "Find your unique angle (sub-niche or unique POV)",
        ],
    },
    {
        "step": 2,
        "title": "Set Up Your Account(s)",
        "tasks": [
            "Create separate accounts for each platform (brand consistency)",
            "Username: same across all platforms if possible",
            "Profile photo: professional and niche-relevant",
            "Bio: niche keyword + hook + CTA (link in bio)",
            "Set up link-in-bio tool (Beacons recommended — free tier)",
        ],
    },
    {
        "step": 3,
        "title": "Build Your Content System",
        "tasks": [
            "Define 3-5 content 'pillars' (content categories you rotate)",
            "Create a content calendar (minimum 30 days ahead)",
            "Batch-create 20 pieces of content before going live",
            "Set up your editing workflow (CapCut, Canva, or Premiere)",
            "Create a brand kit (colours, fonts, logo, music style)",
        ],
    },
    {
        "step": 4,
        "title": "Grow to 1K (First Milestone)",
        "tasks": [
            "Post 2-3x daily on TikTok, 1-2x daily on IG",
            "Engage 30-60 min/day in your niche community",
            "Comment on 30-50 viral posts/day",
            "Do 5-10 S4S (shoutout for shoutout) with similar-size accounts",
            "Track analytics weekly — double down on what works",
        ],
    },
    {
        "step": 5,
        "title": "Monetise (1K-10K Range)",
        "tasks": [
            "Launch your first digital product",
            "Join 2-3 affiliate programmes",
            "Set up your DM funnel (ManyChat for comment automation)",
            "Start pitching micro-brand deals",
            "Build your email list — aim for 100 subscribers first",
        ],
    },
    {
        "step": 6,
        "title": "Scale (10K+ Range)",
        "tasks": [
            "Hire a VA to manage daily posting and engagement",
            "Test paid promotion to amplify best-performing posts",
            "Launch a paid community or course",
            "Negotiate brand retainers (monthly $500-5000+)",
            "Expand to a second platform",
        ],
    },
]


# ── Guide functions ───────────────────────────────────────────────────────────

def get_niche_info(niche: str) -> dict:
    """Get info for a specific niche."""
    key = niche.lower().replace(" ", "-")
    if key not in NICHES:
        available = list(NICHES.keys())
        raise ValueError(
            f"Niche '{niche}' not found. Available: {', '.join(available)}"
        )
    return {"niche": key, **NICHES[key]}


def list_niches(sort_by: str = "viral_potential") -> list[dict]:
    """List all niches, optionally sorted."""
    result = [{"niche": k, **v} for k, v in NICHES.items()]
    order = {"very-high": 4, "high": 3, "medium": 2, "low": 1}
    if sort_by == "viral_potential":
        result.sort(key=lambda x: -order.get(x.get("viral_potential", ""), 0))
    elif sort_by == "competition":
        result.sort(key=lambda x: order.get(x.get("competition", ""), 0))
    elif sort_by == "avg_cpm":
        def cpm_min(x):
            try:
                return int(x.get("avg_cpm", "$0").split("$")[1].split("-")[0])
            except Exception:
                return 0
        result.sort(key=cpm_min, reverse=True)
    return result


def get_sourcing_strategy(strategy: str | None = None) -> list[dict] | dict:
    """Get content sourcing strategies."""
    if strategy:
        key = strategy.lower().replace(" ", "_").replace("-", "_")
        if key not in SOURCING_STRATEGIES:
            raise ValueError(f"Unknown strategy: {strategy}")
        return {"strategy": key, **SOURCING_STRATEGIES[key]}
    return [{"strategy": k, **v} for k, v in SOURCING_STRATEGIES.items()]


def get_monetisation_strategy(strategy: str | None = None,
                              followers: int = 0) -> list[dict] | dict:
    """Get monetisation strategies, filtered by follower count if provided."""
    if strategy:
        key = strategy.lower().replace(" ", "_").replace("-", "_")
        if key not in MONETISATION_STRATEGIES:
            raise ValueError(f"Unknown strategy: {strategy}")
        return {"strategy": key, **MONETISATION_STRATEGIES[key]}

    result = [{"strategy": k, **v} for k, v in MONETISATION_STRATEGIES.items()]
    if followers:
        result = [r for r in result if followers >= r.get("min_followers", 0)]
    return result


def get_setup_checklist() -> list[dict]:
    """Return the complete theme page setup checklist."""
    return SETUP_CHECKLIST


def get_conversion_funnel(niche: str = "", followers: int = 0) -> dict:
    """Generate a personalised conversion funnel recommendation."""
    niche_data = NICHES.get(niche.lower(), {})
    best_mono = niche_data.get("monetisation", ["affiliate", "shoutouts"])

    available = []
    for key, strategy in MONETISATION_STRATEGIES.items():
        if followers >= strategy.get("min_followers", 0):
            if not best_mono or any(k in key for k in best_mono):
                available.append({
                    "strategy": key,
                    "name": strategy["name"],
                    "priority": "primary" if key in best_mono else "secondary",
                })

    return {
        "niche": niche or "general",
        "followers": followers,
        "funnel_stages": [
            {
                "stage": "Awareness",
                "action": "Post viral content with #fyp, trending sounds",
                "goal": "Reach non-followers",
            },
            {
                "stage": "Interest",
                "action": "Value-packed content, save-worthy carousels",
                "goal": "Earn follows and saves",
            },
            {
                "stage": "Consideration",
                "action": "CTA: 'Comment X for free [resource]' → DM funnel",
                "goal": "Move followers to DMs or email list",
            },
            {
                "stage": "Conversion",
                "action": "Offer digital product, affiliate link, or paid service",
                "goal": "Turn engaged followers into buyers",
            },
            {
                "stage": "Retention",
                "action": "Email list, paid community, ongoing content value",
                "goal": "Repeat purchases and referrals",
            },
        ],
        "recommended_strategies": available,
        "immediate_actions": [
            f"Set up link-in-bio page (Beacons.ai — free)",
            f"Join {'Amazon Associates' if 'affiliate' in best_mono else 'a relevant affiliate programme'}",
            "Create one free lead magnet this week to start building email list",
            "Post one piece of content with 'Comment [word] for free guide' CTA",
        ],
    }
