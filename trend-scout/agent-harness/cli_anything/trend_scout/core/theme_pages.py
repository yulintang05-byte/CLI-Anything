"""Theme page guide: what they are, how to start, how to convert to cash.

A theme page (also called a 'niche page' or 'faceless account') curates and
reposts content from a specific niche instead of creating original content.
The goal is to build a large, engaged audience and then convert it to revenue.
"""

import time


# ── Theme page knowledge base ─────────────────────────────────────────────────

THEME_PAGE_NICHES = {
    "motivation": {
        "description": "Quotes, success stories, mindset content",
        "content_sources": ["Reddit r/GetMotivated", "Goodreads quotes", "TED talks clips", "book summaries"],
        "avg_cpm": "$3-8",
        "competition": "high",
        "monetization": ["brand deals", "digital products", "affiliate", "coaching"],
        "tools": ["Canva", "CapCut", "Notion"],
        "growth_speed": "fast",
    },
    "luxury": {
        "description": "Luxury cars, watches, real estate, lifestyle",
        "content_sources": ["YouTube channels", "Instagram reposts", "stock footage", "manufacturer press releases"],
        "avg_cpm": "$8-15",
        "competition": "medium",
        "monetization": ["affiliate (luxury goods)", "brand deals", "lead gen for brokers"],
        "tools": ["CapCut", "Splice", "Lightroom"],
        "growth_speed": "medium",
    },
    "animals": {
        "description": "Cute/funny animal compilations",
        "content_sources": ["Reddit r/aww", "ViralHog", "TikTok reposts", "YouTube compilations"],
        "avg_cpm": "$2-5",
        "competition": "very high",
        "monetization": ["brand deals (pet brands)", "Redbubble merch", "affiliate"],
        "tools": ["CapCut", "iMovie"],
        "growth_speed": "very fast",
    },
    "finance": {
        "description": "Money tips, investing, passive income, frugality",
        "content_sources": ["Reddit r/personalfinance", "financial news", "YouTube clips", "books"],
        "avg_cpm": "$12-25",
        "competition": "medium",
        "monetization": ["affiliate (brokerages, cards)", "courses", "sponsorships"],
        "tools": ["Canva", "Descript", "Notion"],
        "growth_speed": "medium",
    },
    "fitness": {
        "description": "Workout tips, transformations, nutrition hacks",
        "content_sources": ["YouTube workout channels", "Reddit r/fitness", "before/after reposts"],
        "avg_cpm": "$5-12",
        "competition": "high",
        "monetization": ["supplement affiliate", "workout programs", "brand deals"],
        "tools": ["CapCut", "Canva", "InShot"],
        "growth_speed": "fast",
    },
    "food": {
        "description": "Recipes, restaurant reviews, food hacks",
        "content_sources": ["YouTube recipes", "TikTok food creators", "Reddit r/food"],
        "avg_cpm": "$3-7",
        "competition": "very high",
        "monetization": ["kitchen affiliate", "brand deals", "cookbooks"],
        "tools": ["CapCut", "Canva", "Tasty-style templates"],
        "growth_speed": "very fast",
    },
    "travel": {
        "description": "Destinations, travel hacks, hidden gems",
        "content_sources": ["YouTube travel vlogs", "Instagram reposts", "stock footage (Pexels)"],
        "avg_cpm": "$4-9",
        "competition": "medium",
        "monetization": ["affiliate (Booking.com, hotels)", "brand deals", "travel guides"],
        "tools": ["CapCut", "Adobe Premiere Rush", "Lightroom"],
        "growth_speed": "medium",
    },
    "tech": {
        "description": "Tech reviews, AI tools, gadgets, software",
        "content_sources": ["YouTube tech channels", "Product Hunt", "Reddit r/technology"],
        "avg_cpm": "$10-20",
        "competition": "medium",
        "monetization": ["affiliate (Amazon, software)", "sponsored reviews", "courses"],
        "tools": ["OBS", "DaVinci Resolve", "Canva"],
        "growth_speed": "medium",
    },
    "fashion": {
        "description": "Outfit ideas, trends, styling tips, hauls",
        "content_sources": ["Pinterest", "Instagram", "TikTok reposts", "brand lookbooks"],
        "avg_cpm": "$4-8",
        "competition": "very high",
        "monetization": ["LTK affiliate", "brand deals", "Depop/reselling"],
        "tools": ["CapCut", "VSCO", "Canva"],
        "growth_speed": "fast",
    },
    "gaming": {
        "description": "Gameplay clips, tips, gaming news, esports",
        "content_sources": ["Twitch clips", "YouTube gaming", "Reddit r/gaming"],
        "avg_cpm": "$2-5",
        "competition": "very high",
        "monetization": ["gaming affiliate", "channel memberships", "brand deals"],
        "tools": ["OBS", "CapCut", "DaVinci Resolve"],
        "growth_speed": "fast",
    },
}

CONVERSION_PLAYBOOK = {
    "phase_1_build": {
        "name": "Phase 1: Content Machine (0-10K followers)",
        "duration": "1-3 months",
        "goal": "Reach 10K followers with a consistent posting rhythm",
        "actions": [
            "Post 2-4 times daily (TikTok) or 1 Reel/day (Instagram)",
            "Batch-create 1 week of content at a time (Sunday production day)",
            "Use trending sounds on 50% of posts",
            "Engage in comments for 30 min after posting",
            "Study your top 3 competitors and reverse-engineer their hooks",
            "Use CapCut templates for fast video production",
            "Set up Link-in-bio (Linktree / Stan Store / Beacons)",
        ],
        "metrics_to_track": ["follower growth rate", "average views per post", "engagement rate"],
        "avoid": [
            "Buying followers (kills engagement rate)",
            "Watermarked reposts (platforms suppress them)",
            "Inconsistent posting breaks (algorithm punishes gaps)",
        ],
    },
    "phase_2_monetize": {
        "name": "Phase 2: First Dollar (10K-50K followers)",
        "duration": "2-4 months",
        "goal": "First $500/month from the account",
        "actions": [
            "Apply for Creator Rewards / YPP / Instagram monetization",
            "Join affiliate programs: Amazon Associates, Impact, ShareASale",
            "Create a simple digital product (PDF guide, template pack): $9-27",
            "DM 5 small brands per week in your niche for gifted collabs",
            "Add 'Shop my favorites' link to bio with affiliate products",
            "Cross-promote between TikTok and Instagram for double reach",
        ],
        "revenue_targets": {
            "platform_revenue": "$50-200/month",
            "affiliate": "$100-500/month",
            "digital_product": "$100-1,000/month",
            "brand_deals": "$0-500/month (gifted first)",
        },
    },
    "phase_3_scale": {
        "name": "Phase 3: Scale to Full-Time (50K-200K followers)",
        "duration": "3-6 months",
        "goal": "Replace a full-time income ($3,000-10,000/month)",
        "actions": [
            "Hire a video editor (Fiverr/Upwork) to 2x content output",
            "Launch a course or membership ($27-197)",
            "Negotiate paid brand deals ($500-2,000/post)",
            "Build an email list — social media followers are rented, email is owned",
            "Create a 'theme page bundle' and sell accounts in your niche",
            "Expand to 3-4 platforms simultaneously",
            "Automate content scheduling with Buffer, Later, or Publer",
        ],
        "revenue_targets": {
            "platform_revenue": "$500-2,000/month",
            "affiliate": "$500-2,000/month",
            "digital_products": "$1,000-5,000/month",
            "brand_deals": "$1,000-5,000/month",
        },
    },
    "phase_4_sell": {
        "name": "Phase 4: Flip or Multiply",
        "duration": "ongoing",
        "goal": "Sell accounts at 24-36x monthly revenue, or build a network",
        "actions": [
            "List accounts on Flippa, Empire Flippers, or Acquire.com",
            "Build 3-5 theme pages in the same niche for portfolio sale",
            "Document SOPs so accounts are 'turnkey' for buyers",
            "Use proceeds to fund larger accounts or new niches",
        ],
        "valuation_formula": "Monthly net revenue × 24-36x multiplier",
    },
}

CONTENT_REPURPOSING_TOOLS = [
    {"name": "CapCut", "purpose": "Video editing + templates", "cost": "Free/Pro $10/mo", "platform": "all"},
    {"name": "Canva", "purpose": "Graphics, quote cards, thumbnails", "cost": "Free/Pro $15/mo", "platform": "all"},
    {"name": "Descript", "purpose": "AI video editing, auto-captions", "cost": "$12/mo", "platform": "YouTube/podcast"},
    {"name": "Repurpose.io", "purpose": "Auto-cross-post between platforms", "cost": "$25/mo", "platform": "all"},
    {"name": "Buffer", "purpose": "Scheduling across 6+ platforms", "cost": "Free/Essentials $6/mo", "platform": "all"},
    {"name": "Metricool", "purpose": "Analytics + scheduling + competitor tracking", "cost": "$22/mo", "platform": "all"},
    {"name": "Invideo AI", "purpose": "Turn articles → videos", "cost": "$20/mo", "platform": "YouTube/TikTok"},
    {"name": "ElevenLabs", "purpose": "AI voiceover for faceless videos", "cost": "$5-22/mo", "platform": "all"},
    {"name": "Pexels/Pixabay", "purpose": "Free stock footage and images", "cost": "Free", "platform": "all"},
    {"name": "Remove.bg", "purpose": "Background removal for thumbnails", "cost": "Free/credits", "platform": "YouTube/IG"},
]

ACCOUNT_SELLING_PLATFORMS = [
    {"name": "Flippa", "url": "flippa.com", "fee": "5-15% success fee", "best_for": "accounts $1K-$500K"},
    {"name": "FameSwap", "url": "fameswap.com", "fee": "15% fee", "best_for": "Instagram/TikTok accounts"},
    {"name": "Social Tradia", "url": "socialtradia.com", "fee": "negotiable", "best_for": "Instagram accounts"},
    {"name": "Acquire.com", "url": "acquire.com", "fee": "5% fee", "best_for": "accounts $50K+"},
    {"name": "Player Up", "url": "playerup.com", "fee": "10% fee", "best_for": "gaming/social accounts"},
]


# ── Public API ────────────────────────────────────────────────────────────────

def list_niches() -> list[dict]:
    """Return all supported theme page niches with key stats."""
    return [
        {
            "niche": niche,
            "description": data["description"],
            "avg_cpm": data["avg_cpm"],
            "competition": data["competition"],
            "growth_speed": data["growth_speed"],
            "top_monetization": data["monetization"][:2],
        }
        for niche, data in THEME_PAGE_NICHES.items()
    ]


def get_niche_guide(niche: str) -> dict:
    """Get a full theme page guide for a specific niche."""
    niche = niche.lower()
    if niche not in THEME_PAGE_NICHES:
        available = ", ".join(THEME_PAGE_NICHES.keys())
        raise ValueError(f"Unknown niche '{niche}'. Available: {available}")

    data = THEME_PAGE_NICHES[niche]
    return {
        "niche": niche,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        **data,
        "content_repurposing_tools": CONTENT_REPURPOSING_TOOLS[:5],
        "quick_start_checklist": [
            f"1. Create accounts on TikTok, Instagram Reels, YouTube Shorts (all same @handle)",
            f"2. Set up bio: clear niche + value prop + link-in-bio",
            f"3. Identify 10 creators in {niche} to draw inspiration from",
            f"4. Batch-create 7 days of content using tools: {', '.join(data['tools'])}",
            f"5. Source content legally from: {', '.join(data['content_sources'][:2])}",
            f"6. Post first video, engage with comments, analyze metrics after 48h",
            f"7. Repeat daily — volume + consistency = algorithm favor",
        ],
    }


_PHASE_KEYS = {
    "1": "phase_1_build",
    "2": "phase_2_monetize",
    "3": "phase_3_scale",
    "4": "phase_4_sell",
}


def get_conversion_playbook(phase: str | None = None) -> dict:
    """Get the theme page conversion/monetization playbook."""
    if phase:
        phase_key = _PHASE_KEYS.get(str(phase))
        if not phase_key or phase_key not in CONVERSION_PLAYBOOK:
            raise ValueError(f"Unknown phase '{phase}'. Choose from: 1, 2, 3, 4")
        return {
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            **CONVERSION_PLAYBOOK[phase_key],
        }

    return {
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "overview": "4-phase system from 0 to full-time income",
        "phases": list(CONVERSION_PLAYBOOK.values()),
        "total_timeline": "6-18 months to full-time income",
        "key_principle": (
            "A theme page is a media business. Treat content as product, "
            "audience as customer acquisition, and monetization as revenue operations."
        ),
    }


def get_tools() -> list[dict]:
    """List all recommended tools for running theme pages."""
    return CONTENT_REPURPOSING_TOOLS


def get_selling_platforms() -> list[dict]:
    """List platforms where you can buy or sell social media accounts."""
    return ACCOUNT_SELLING_PLATFORMS
