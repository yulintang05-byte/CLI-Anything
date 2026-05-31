"""Theme page creation guide, niche research, and monetization strategies."""

from typing import Any, Dict, List, Optional


# Proven theme page niches ranked by monetization potential
NICHE_DATABASE: Dict[str, Dict[str, Any]] = {
    "fitness": {
        "demand": "very high",
        "competition": "high",
        "monetization_potential": 9,
        "avg_cpm": "$8-15",
        "content_sources": ["repost with credit", "original clips", "transformation posts"],
        "monetization": ["brand deals", "affiliate (supplements/gear)", "digital products", "coaching"],
        "target_audience": "18-35, health-conscious, gym-goers",
        "platform_fit": ["instagram", "tiktok", "youtube"],
        "growth_speed": "fast",
    },
    "luxury": {
        "demand": "high",
        "competition": "medium",
        "monetization_potential": 10,
        "avg_cpm": "$15-40",
        "content_sources": ["car photos", "mansion tours", "lifestyle clips"],
        "monetization": ["brand deals (luxury brands)", "affiliate (watches/cars)", "DM/consulting"],
        "target_audience": "25-45, aspirational buyers",
        "platform_fit": ["instagram", "tiktok", "youtube"],
        "growth_speed": "medium",
    },
    "motivation": {
        "demand": "very high",
        "competition": "very high",
        "monetization_potential": 7,
        "avg_cpm": "$3-8",
        "content_sources": ["speech clips", "quote graphics", "documentary snippets"],
        "monetization": ["digital products", "merch", "coaching", "affiliate"],
        "target_audience": "16-30, students, entrepreneurs",
        "platform_fit": ["instagram", "tiktok", "youtube"],
        "growth_speed": "fast",
    },
    "finance": {
        "demand": "very high",
        "competition": "medium",
        "monetization_potential": 10,
        "avg_cpm": "$20-60",
        "content_sources": ["stock charts", "news clips", "explainer animations"],
        "monetization": ["affiliate (brokers/apps)", "courses", "newsletter", "consulting"],
        "target_audience": "22-40, income-builders, investors",
        "platform_fit": ["twitter", "youtube", "tiktok"],
        "growth_speed": "medium",
    },
    "gaming": {
        "demand": "very high",
        "competition": "very high",
        "monetization_potential": 7,
        "avg_cpm": "$3-7",
        "content_sources": ["highlight clips", "viral moments", "pro plays"],
        "monetization": ["YouTube AdSense", "sponsorships (gaming peripherals)", "Twitch subs"],
        "target_audience": "13-28, gamers",
        "platform_fit": ["youtube", "tiktok", "twitch"],
        "growth_speed": "fast",
    },
    "food": {
        "demand": "very high",
        "competition": "high",
        "monetization_potential": 7,
        "avg_cpm": "$4-10",
        "content_sources": ["recipe videos", "restaurant reviews", "mukbang clips"],
        "monetization": ["brand deals (food brands)", "affiliate (kitchen gear)", "cookbook"],
        "target_audience": "20-45, food lovers",
        "platform_fit": ["instagram", "tiktok", "youtube"],
        "growth_speed": "fast",
    },
    "travel": {
        "demand": "high",
        "competition": "medium",
        "monetization_potential": 8,
        "avg_cpm": "$5-15",
        "content_sources": ["destination clips", "hotel reviews", "travel tips"],
        "monetization": ["affiliate (booking.com/hotels)", "brand deals", "digital guides"],
        "target_audience": "22-40, travelers, aspirational",
        "platform_fit": ["instagram", "tiktok", "youtube"],
        "growth_speed": "medium",
    },
    "pets": {
        "demand": "very high",
        "competition": "medium",
        "monetization_potential": 7,
        "avg_cpm": "$3-8",
        "content_sources": ["cute animal clips", "training videos", "pet products"],
        "monetization": ["affiliate (pet supplies)", "brand deals", "merchandise"],
        "target_audience": "all ages, pet owners",
        "platform_fit": ["instagram", "tiktok", "youtube"],
        "growth_speed": "very fast",
    },
    "beauty": {
        "demand": "very high",
        "competition": "very high",
        "monetization_potential": 9,
        "avg_cpm": "$8-20",
        "content_sources": ["makeup tutorials", "skincare routines", "product reviews"],
        "monetization": ["affiliate (Sephora/ULTA)", "brand deals", "digital courses"],
        "target_audience": "16-35, beauty enthusiasts",
        "platform_fit": ["instagram", "tiktok", "youtube"],
        "growth_speed": "fast",
    },
    "crypto": {
        "demand": "high",
        "competition": "medium",
        "monetization_potential": 9,
        "avg_cpm": "$15-50",
        "content_sources": ["price charts", "news analysis", "explainers"],
        "monetization": ["affiliate (exchanges)", "newsletter", "courses", "consulting"],
        "target_audience": "20-40, crypto investors",
        "platform_fit": ["twitter", "youtube", "tiktok"],
        "growth_speed": "variable (bull market dependent)",
    },
}


THEME_PAGE_GUIDE: List[Dict[str, Any]] = [
    {
        "phase": 1,
        "title": "Choose Your Niche",
        "steps": [
            "Research 3-5 niches using the 'niche' command",
            "Pick a niche where monetization potential × your interest overlap",
            "Validate: search the niche on TikTok/IG — are there accounts with 100k+ followers?",
            "Niche down: don't do 'fitness', do 'calisthenics transformation' or 'gym motivation'",
        ],
        "time_estimate": "1-2 days",
    },
    {
        "phase": 2,
        "title": "Build the Brand",
        "steps": [
            "Create accounts on target platforms with consistent handles (@[niche]daily, @[niche]world)",
            "Design logo using Canva (1000×1000px, simple, readable at 50px)",
            "Write bio: niche keyword + value prop + CTA + link (max 150 chars on IG)",
            "Set up Linktree/link-in-bio page with affiliate links from day 1",
            "Create a content folder structure: Saved → Sort by platform & content type",
        ],
        "time_estimate": "1 day",
    },
    {
        "phase": 3,
        "title": "Content Sourcing Strategy",
        "steps": [
            "Follow 20+ top creators in your niche — source their viral content (repost ethically)",
            "Use TrendScout to find top-performing videos in niche",
            "Create a content pipeline: collect 20-30 pieces before launching",
            "Edit reposted content: trim, add text overlays, music, and your handle watermark",
            "IMPORTANT: Always credit original creators to avoid copyright strikes",
            "Best tools: CapCut (mobile), DaVinci Resolve (desktop), Canva (graphics)",
        ],
        "time_estimate": "Ongoing",
    },
    {
        "phase": 4,
        "title": "Growth Phase (0 → 10k)",
        "steps": [
            "Post 3-5× daily on TikTok for first 30 days (volume is key to algorithmic discovery)",
            "Engage 30+ mins/day: like, comment on top posts in niche (builds algorithmic relationships)",
            "Use trending sounds within 48h of trending — this is the #1 organic reach hack on TikTok",
            "Follow-for-follow in niche is slow; focus on content quality instead",
            "Cross-post to Instagram Reels and YouTube Shorts (same video, platform-optimized covers)",
            "Pin your 3 best-performing videos to your TikTok profile",
        ],
        "time_estimate": "30-90 days",
    },
    {
        "phase": 5,
        "title": "Growth Phase (10k → 100k)",
        "steps": [
            "Analyze top 10 performing posts — double down on that exact format",
            "Start going LIVE on TikTok 3-5× per week (LIVE pushes your account to For You page)",
            "Collaborate: duet/stitch top creators in niche",
            "Test paid promotion on your best organic posts ($20-50 TikTok Spark Ads)",
            "Build email list via bio link — most monetizable long-term asset",
            "Start posting original content alongside reposts as trust grows",
        ],
        "time_estimate": "90-180 days",
    },
    {
        "phase": 6,
        "title": "Monetization (100k+)",
        "steps": [
            "Apply for TikTok Creator Fund / YouTube Partner Program",
            "DM brands in your niche for paid promotions (rate: $500-2000 per post at 100k)",
            "Join affiliate programs: Amazon, ShareASale, Impact, ClickBank",
            "Create a digital product: ebook, course, template, guide ($27-197)",
            "Sell shoutouts to smaller accounts in your niche ($50-200 per post)",
            "Explore brand acquisition: growing then selling theme pages for $X×monthly revenue",
        ],
        "time_estimate": "Ongoing",
    },
]

CONVERTING_GUIDE: List[Dict[str, Any]] = [
    {
        "stage": "Cold Traffic → Follower",
        "tactics": [
            "Cliffhanger content: 'Part 2 tomorrow — follow so you don't miss it'",
            "Value dump: give your best tips free, with 'more like this if you follow'",
            "Relatability: 'POV: you're a [niche person]' — viewer sees themselves",
            "Pinned comment: 'Follow for daily [niche] tips'",
        ],
    },
    {
        "stage": "Follower → Engaged Fan",
        "tactics": [
            "Reply to every comment for first 30 days — creates loyalty",
            "Ask questions in captions to drive comments (boosts reach)",
            "Polls in Stories/Community posts — makes followers feel heard",
            "Behind-the-scenes content — humanizes theme page",
        ],
    },
    {
        "stage": "Engaged Fan → Email Subscriber",
        "tactics": [
            "Offer a free lead magnet in bio (checklist, guide, template)",
            "Story/post: 'I made a free [resource] — link in bio'",
            "Comment-to-DM automation: 'Comment GUIDE for the free resource'",
        ],
    },
    {
        "stage": "Email Subscriber → Buyer",
        "tactics": [
            "Nurture sequence: 5-email educational series before any pitch",
            "Social proof: show testimonials/results from your content",
            "Limited-time offer: scarcity converts fence-sitters",
            "Bundle value: combine multiple products at a discount",
        ],
    },
]


def niche_research(keyword: str) -> Dict[str, Any]:
    """Return detailed niche data for a keyword."""
    niche = keyword.lower()
    if niche in NICHE_DATABASE:
        return {"keyword": keyword, **NICHE_DATABASE[niche]}
    # Generic fallback
    return {
        "keyword": keyword,
        "demand": "unknown — research manually",
        "competition": "unknown",
        "monetization_potential": 6,
        "avg_cpm": "$3-10 (estimate)",
        "content_sources": ["viral videos in niche", "educational content", "news clips"],
        "monetization": ["brand deals", "affiliate", "digital products"],
        "target_audience": "niche-specific",
        "platform_fit": ["tiktok", "instagram", "youtube"],
        "growth_speed": "varies",
        "note": f"No built-in data for '{keyword}'. Run TrendScout to find real trending data.",
    }


def list_niches(min_monetization: int = 0) -> List[Dict[str, Any]]:
    """List all niches sorted by monetization potential."""
    niches = []
    for name, data in NICHE_DATABASE.items():
        if data["monetization_potential"] >= min_monetization:
            niches.append({
                "niche": name,
                "demand": data["demand"],
                "competition": data["competition"],
                "monetization": data["monetization_potential"],
                "avg_cpm": data["avg_cpm"],
                "growth_speed": data["growth_speed"],
                "platforms": ", ".join(data["platform_fit"]),
            })
    return sorted(niches, key=lambda x: x["monetization"], reverse=True)


def get_creation_guide(phase: Optional[int] = None) -> List[Dict[str, Any]]:
    """Return theme page creation guide, optionally filtered to a phase."""
    if phase is not None:
        return [p for p in THEME_PAGE_GUIDE if p["phase"] == phase]
    return THEME_PAGE_GUIDE


def get_converting_guide() -> List[Dict[str, Any]]:
    """Return the follower → buyer conversion funnel guide."""
    return CONVERTING_GUIDE


def monetization_strategies(niche: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return monetization strategies, optionally niche-specific."""
    general = [
        {
            "strategy": "Brand Deals",
            "description": "Brands pay to feature their product in your content",
            "entry_point": "10k-50k followers",
            "revenue_range": "$50-$50,000+ per post",
            "best_platforms": ["tiktok", "instagram", "youtube"],
        },
        {
            "strategy": "Affiliate Marketing",
            "description": "Earn commission on sales you drive via tracked links",
            "entry_point": "Any size",
            "revenue_range": "5-30% per sale, passive income",
            "best_platforms": ["all"],
        },
        {
            "strategy": "Digital Products",
            "description": "Ebooks, courses, templates, presets — high margin, no fulfillment",
            "entry_point": "5k+ engaged followers",
            "revenue_range": "$27-$997 per product sale",
            "best_platforms": ["instagram", "youtube", "tiktok"],
        },
        {
            "strategy": "Selling the Page",
            "description": "Grow a theme page and sell it for 12-36× monthly revenue",
            "entry_point": "50k+ followers, proven engagement",
            "revenue_range": "$1,000-$100,000+ per sale",
            "best_platforms": ["instagram", "tiktok"],
        },
        {
            "strategy": "Ad Revenue",
            "description": "YouTube Partner Program or TikTok Creator Fund",
            "entry_point": "YT: 1k subs + 4k hrs  |  TT: 10k followers",
            "revenue_range": "$1-$10 per 1,000 views",
            "best_platforms": ["youtube", "tiktok"],
        },
        {
            "strategy": "Paid Shoutouts",
            "description": "Sell promotion slots to smaller accounts in your niche",
            "entry_point": "10k+ followers",
            "revenue_range": "$30-$500 per shoutout",
            "best_platforms": ["instagram", "tiktok"],
        },
        {
            "strategy": "Newsletter / Email List",
            "description": "Platform-independent audience — most valuable long-term asset",
            "entry_point": "Any size",
            "revenue_range": "$1-5 per subscriber per month (sponsorships + products)",
            "best_platforms": ["all"],
        },
    ]
    if niche:
        niche_data = NICHE_DATABASE.get(niche.lower(), {})
        niche_specific = niche_data.get("monetization", [])
        for item in general:
            if item["strategy"].lower().replace(" ", "_") in [m.lower().replace(" ", "_") for m in niche_specific]:
                item["recommended_for_niche"] = True
    return general
