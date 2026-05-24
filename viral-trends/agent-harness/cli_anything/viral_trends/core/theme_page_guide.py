"""Theme page conversion guide — building, growing, and monetizing theme pages."""

from datetime import datetime, timezone


NICHES_BY_CPM = [
    {"niche": "Finance / Investing",    "cpm_range": "$15-$45", "difficulty": "Medium", "conversion_rate": "High"},
    {"niche": "Business / Entrepreneur","cpm_range": "$12-$35", "difficulty": "Medium", "conversion_rate": "High"},
    {"niche": "Health / Fitness",       "cpm_range": "$8-$25",  "difficulty": "Low",    "conversion_rate": "High"},
    {"niche": "Tech / AI",              "cpm_range": "$10-$30", "difficulty": "Medium", "conversion_rate": "Medium"},
    {"niche": "Luxury / Lifestyle",     "cpm_range": "$8-$20",  "difficulty": "Low",    "conversion_rate": "Medium"},
    {"niche": "Motivation / Mindset",   "cpm_range": "$6-$18",  "difficulty": "Low",    "conversion_rate": "Medium"},
    {"niche": "Comedy / Entertainment", "cpm_range": "$3-$10",  "difficulty": "Low",    "conversion_rate": "Low"},
    {"niche": "Gaming",                 "cpm_range": "$3-$8",   "difficulty": "Medium", "conversion_rate": "Low"},
    {"niche": "Travel",                 "cpm_range": "$5-$15",  "difficulty": "Medium", "conversion_rate": "Medium"},
    {"niche": "Food / Recipes",         "cpm_range": "$5-$12",  "difficulty": "Low",    "conversion_rate": "Medium"},
    {"niche": "Pets / Animals",         "cpm_range": "$4-$10",  "difficulty": "Low",    "conversion_rate": "Low"},
    {"niche": "Relationship / Dating",  "cpm_range": "$5-$15",  "difficulty": "Low",    "conversion_rate": "High"},
]

THEME_PAGE_PHASES = [
    {
        "phase": 1,
        "name": "Foundation (Days 1–7)",
        "goals": ["Profile setup", "Niche lock-in", "Content sourcing system"],
        "actions": [
            "Pick ONE niche — the riches are in the niches",
            "Create a catchy, keyword-rich username (e.g., @dailyfinancetips, @luxurylifedaily)",
            "Design logo/avatar in Canva: bold, legible at 40px, matches niche aesthetic",
            "Write bio using the template: What you do | Who it's for | CTA + link",
            "Set up link-in-bio (Beacons, Stan Store, or Linktree)",
            "Find 5-10 content sources in your niche (Reddit, other pages, news, quotes)",
            "Create a content bank of 30 posts BEFORE you go live",
            "Follow 100 accounts in your niche on day 1",
        ],
        "tools": ["Canva (design)", "Beacons.ai (link in bio)", "CapCut (video editing)", "Notion (content bank)"],
    },
    {
        "phase": 2,
        "name": "Launch & Volume (Days 8–30)",
        "goals": ["Post consistently", "Learn the algorithm", "Get first 1K followers"],
        "actions": [
            "Post 3-5x per day on TikTok, 1-2x YouTube Shorts, 1-2x Instagram Reels",
            "Use trending sounds within 24-48h of them spiking",
            "Engage: reply to EVERY comment for the first 30 min after posting",
            "Do 10 minutes of niche engagement daily (like/comment on trending niche posts)",
            "Study your analytics weekly — double down on what works",
            "Test 3 different content formats in week 1 (text overlay, voiceover, compilation)",
            "Repurpose every TikTok to Shorts and Reels (remove watermark)",
        ],
        "kpis": ["1K followers by day 30", "One video hitting 10K+ views", "Average watch time > 50%"],
        "tools": ["CapCut (remove watermark + edit)", "TikTok Creative Center (trend research)", "Later or Buffer (scheduling)"],
    },
    {
        "phase": 3,
        "name": "Monetization (Day 31–90)",
        "goals": ["First $100", "Diversify revenue", "Build email list"],
        "actions": [
            "Enable TikTok LIVE at 1K followers — stream 30 min/day for gifts",
            "Apply for TikTok Creator Fund + YouTube Partner Program when eligible",
            "Reach out to brands in your niche for paid UGC/shoutouts ($50–$500/post)",
            "Add affiliate links to bio (Amazon, ClickBank, ShareASale based on niche)",
            "Create a free lead magnet (PDF checklist, guide) to build email list",
            "Sell shoutouts on other theme pages (start at $10-$50/post)",
            "Explore selling the account once it hits 50K–100K followers",
        ],
        "revenue_streams": [
            "Brand deals / shoutouts",
            "Affiliate marketing",
            "TikTok Creator Fund / YouTube AdSense",
            "Selling the account",
            "Digital products (guides, templates)",
            "LIVE gifts (TikTok/Instagram)",
        ],
        "kpis": ["10K followers", "First paid deal", "Email list started"],
    },
    {
        "phase": 4,
        "name": "Scale & Sell (Day 90+)",
        "goals": ["100K+ followers", "Passive income", "Account sale or agency model"],
        "actions": [
            "Hire a virtual assistant ($5-$15/hr) to handle reposting and engagement",
            "Build 3-5 theme pages in the same niche for portfolio",
            "Sell accounts on Fameswap, Flippa, or direct DM deals",
            "Launch a paid community (Discord, Telegram, Circle) around the niche",
            "Create a course teaching others your process",
            "Agency: manage theme pages for brands/clients ($500-$2K/month/client)",
        ],
        "exit_multiples": {
            "account_sale": "3-5× monthly revenue or $10-$30 per 1K followers",
            "best_platforms_to_sell": ["Fameswap.com", "Flippa.com", "PlayerUp.com", "Direct DM deals"],
        },
    },
]

CONVERSION_TACTICS = [
    {
        "tactic": "The 'Value Bomb' CTA",
        "description": (
            "End every video with a freebie offer: 'Comment FREE and I'll DM you the full guide.' "
            "This spikes comments (boosts algo) and collects leads simultaneously."
        ),
        "conversion_rate": "High",
        "works_on": ["TikTok", "Instagram", "YouTube"],
    },
    {
        "tactic": "Link-in-bio optimization",
        "description": (
            "Your link-in-bio is your storefront. Structure: "
            "(1) Lead magnet above fold, (2) Main offer, (3) Other socials. "
            "Use heat map tools to see where people click."
        ),
        "conversion_rate": "Medium-High",
        "works_on": ["All platforms"],
    },
    {
        "tactic": "Story → DM funnel (Instagram)",
        "description": (
            "Post a Story poll: 'Want my free [niche] checklist? Vote YES.' "
            "DM everyone who votes YES with the freebie + a soft pitch."
        ),
        "conversion_rate": "High",
        "works_on": ["Instagram"],
    },
    {
        "tactic": "Pinned comment with link",
        "description": (
            "Pin your own comment on every video with the link/offer. "
            "TikTok and YT users check pinned comments — it's prime real estate."
        ),
        "conversion_rate": "Medium",
        "works_on": ["TikTok", "YouTube"],
    },
    {
        "tactic": "Email capture giveaway",
        "description": (
            "Run a niche giveaway (free product, coaching call, digital guide). "
            "Entry = email + follow + tag 2 friends. Grows list AND followers simultaneously."
        ),
        "conversion_rate": "High",
        "works_on": ["Instagram", "TikTok"],
    },
    {
        "tactic": "Series cliffhanger",
        "description": (
            "Create multi-part content: 'Part 2 drops tomorrow — follow so you don't miss it.' "
            "Drives follows and return viewers. Finance/business niches convert best."
        ),
        "conversion_rate": "High",
        "works_on": ["TikTok", "YouTube Shorts"],
    },
    {
        "tactic": "Social proof stacking",
        "description": (
            "Screenshot DMs/comments of people saying your content helped them. "
            "Post as social proof. Trust = conversions."
        ),
        "conversion_rate": "Medium-High",
        "works_on": ["Instagram Stories", "TikTok"],
    },
]

ACCOUNT_SALE_CALCULATOR = {
    "description": "Estimate your account's sale value",
    "formula": "Monthly Revenue × 3-5x multiplier OR Followers / 1000 × $10-30",
    "examples": [
        {"followers": "10K",  "monthly_revenue": "$0",   "est_sale_value": "$100-$300"},
        {"followers": "50K",  "monthly_revenue": "$200",  "est_sale_value": "$600-$1,500"},
        {"followers": "100K", "monthly_revenue": "$500",  "est_sale_value": "$2,500-$5,000"},
        {"followers": "500K", "monthly_revenue": "$2,000","est_sale_value": "$10,000-$20,000"},
        {"followers": "1M",   "monthly_revenue": "$5,000","est_sale_value": "$25,000-$50,000"},
    ],
    "value_boosters": [
        "Email list attached (+30-50% value)",
        "Engaged audience (>5% engagement rate) (+20% value)",
        "Monetization already active (+40% value)",
        "Niche is high-CPM (+25% value)",
    ],
}

TOOLS_STACK = {
    "content_creation": [
        {"name": "CapCut", "use": "Video editing, removing TikTok watermarks", "cost": "Free"},
        {"name": "Canva", "use": "Thumbnails, templates, graphic posts", "cost": "Free/Pro"},
        {"name": "Captions.ai", "use": "Auto-captions for videos", "cost": "$12/mo"},
        {"name": "ElevenLabs", "use": "AI voiceover for faceless content", "cost": "$5/mo"},
    ],
    "scheduling": [
        {"name": "Later", "use": "Schedule Instagram/TikTok posts", "cost": "Free/Paid"},
        {"name": "Buffer", "use": "Multi-platform scheduling", "cost": "Free/Paid"},
        {"name": "TikTok Studio", "use": "Native TikTok scheduling", "cost": "Free"},
    ],
    "research": [
        {"name": "TikTok Creative Center", "use": "Trending hashtags, sounds, videos", "cost": "Free"},
        {"name": "vidIQ / TubeBuddy", "use": "YouTube keyword + trend research", "cost": "Free/Paid"},
        {"name": "Exploding Topics", "use": "Emerging trends before they peak", "cost": "Free/Paid"},
        {"name": "Google Trends", "use": "Search trend comparison", "cost": "Free"},
    ],
    "monetization": [
        {"name": "Stan Store", "use": "Sell digital products from link-in-bio", "cost": "$29/mo"},
        {"name": "Beacons.ai", "use": "Link-in-bio with monetization features", "cost": "Free/Paid"},
        {"name": "Grin / AspireIQ", "use": "Brand deal marketplace", "cost": "Free to join"},
        {"name": "Amazon Associates", "use": "Affiliate links for any product", "cost": "Free"},
    ],
    "analytics": [
        {"name": "TikTok Analytics (native)", "use": "Follower growth, video performance", "cost": "Free"},
        {"name": "YouTube Studio", "use": "Complete YouTube analytics", "cost": "Free"},
        {"name": "Social Blade", "use": "Track competitor growth", "cost": "Free"},
        {"name": "Metricool", "use": "Cross-platform analytics dashboard", "cost": "Free/Paid"},
    ],
}


def get_niche_recommendations(budget: str = "zero") -> dict:
    """Return best niches to start a theme page in based on budget."""
    best_zero_budget = [n for n in NICHES_BY_CPM if n["difficulty"] in ("Low", "Medium")]
    return {
        "budget": budget,
        "top_niches": best_zero_budget[:6],
        "recommendation": (
            "Start with Finance, Business, or Health for highest CPM and conversion. "
            "These niches have built-in buyer intent — followers actively want to improve their situation."
        ),
        "all_niches": NICHES_BY_CPM,
    }


def get_full_roadmap(niche: str = "", current_followers: int = 0) -> dict:
    """Return the full theme page creation and monetization roadmap."""
    current_phase = 1
    if current_followers >= 100000:
        current_phase = 4
    elif current_followers >= 10000:
        current_phase = 3
    elif current_followers >= 1000:
        current_phase = 2

    return {
        "niche": niche or "Not specified — pick one!",
        "current_followers": current_followers,
        "current_phase": current_phase,
        "phases": THEME_PAGE_PHASES,
        "conversion_tactics": CONVERSION_TACTICS,
        "account_sale_guide": ACCOUNT_SALE_CALCULATOR,
        "tools_stack": TOOLS_STACK,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pro_tip": (
            "The #1 mistake: switching niches. Pick one. Post 60 days. Then judge. "
            "The algorithm needs 30-60 days of consistent data before it knows who to show your content to."
        ),
    }
