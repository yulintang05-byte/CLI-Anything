"""Theme page conversion strategy — turn theme pages into revenue machines.

A theme page is an account centered on a topic/niche (not a personal brand).
This module provides research-backed strategies for building, growing, and
monetizing theme pages across TikTok, Instagram, YouTube, and Twitter/X.
"""
from datetime import datetime

# ── High-converting niches with monetization data ────────────────────────────

_NICHES = {
    "luxury_lifestyle": {
        "name": "Luxury Lifestyle",
        "platforms": ["instagram", "tiktok", "youtube"],
        "avg_rpm": "$8-15",
        "monetization": ["brand deals", "affiliate (luxury products)", "paid shoutouts"],
        "content_types": ["luxury cars", "mansions", "travel", "watches", "fashion hauls"],
        "difficulty": "Medium",
        "conversion_rate": "HIGH",
        "why": "Aspirational content drives high engagement. Brands pay premium for luxury audience.",
        "starter_accounts": 1,
        "time_to_monetize": "3-6 months",
    },
    "motivation": {
        "name": "Motivation / Success Mindset",
        "platforms": ["tiktok", "instagram", "youtube"],
        "avg_rpm": "$3-8",
        "monetization": ["YouTube ads", "courses", "affiliate (books/apps)", "brand deals"],
        "content_types": ["speech clips", "quote edits", "success stories", "daily motivation"],
        "difficulty": "Low",
        "conversion_rate": "VERY HIGH",
        "why": "Easy to repurpose existing content. Evergreen. Massive audience size.",
        "starter_accounts": 1,
        "time_to_monetize": "2-4 months",
    },
    "finance_money": {
        "name": "Personal Finance / Money",
        "platforms": ["tiktok", "youtube", "twitter"],
        "avg_rpm": "$15-30",
        "monetization": ["affiliate (trading apps, cards)", "courses", "newsletter", "brand deals"],
        "content_types": ["money tips", "investing basics", "side hustle ideas", "debt payoff"],
        "difficulty": "Medium",
        "conversion_rate": "VERY HIGH",
        "why": "Finance affiliate programs pay $50-200 per lead. Highest CPC on YouTube.",
        "starter_accounts": 1,
        "time_to_monetize": "3-5 months",
    },
    "fitness_health": {
        "name": "Fitness & Health",
        "platforms": ["instagram", "tiktok", "youtube"],
        "avg_rpm": "$4-10",
        "monetization": ["supplements affiliate", "workout programs", "coaching", "brand deals"],
        "content_types": ["transformations", "workout demos", "meal prep", "gym tips"],
        "difficulty": "Low-Medium",
        "conversion_rate": "HIGH",
        "why": "Visual transformation content drives viral spread. Supplement commissions are lucrative.",
        "starter_accounts": 1,
        "time_to_monetize": "2-4 months",
    },
    "pets": {
        "name": "Pet Content",
        "platforms": ["tiktok", "instagram", "youtube"],
        "avg_rpm": "$3-6",
        "monetization": ["pet brand deals", "affiliate (pet products)", "merchandise"],
        "content_types": ["funny moments", "tricks", "day-in-life", "pet tips"],
        "difficulty": "Very Low",
        "conversion_rate": "MEDIUM",
        "why": "Viral spread is natural. Low barrier to entry. Loyal audience.",
        "starter_accounts": 2,
        "time_to_monetize": "4-8 months",
    },
    "relationship_dating": {
        "name": "Relationships & Dating",
        "platforms": ["tiktok", "twitter", "instagram"],
        "avg_rpm": "$5-12",
        "monetization": ["dating app affiliates", "books", "coaching", "brand deals"],
        "content_types": ["dating advice", "red flags", "relationship tips", "green flags"],
        "difficulty": "Low",
        "conversion_rate": "HIGH",
        "why": "Extremely shareable. Dating app affiliates pay well. Discussion content = comments.",
        "starter_accounts": 1,
        "time_to_monetize": "2-5 months",
    },
    "tech_gadgets": {
        "name": "Tech & Gadgets",
        "platforms": ["youtube", "tiktok", "twitter"],
        "avg_rpm": "$8-20",
        "monetization": ["Amazon affiliate", "brand deals", "YouTube ads"],
        "content_types": ["product reviews", "tech tips", "gadget unboxings", "comparisons"],
        "difficulty": "Medium",
        "conversion_rate": "HIGH",
        "why": "Amazon affiliate conversions are strong. Tech buyers are high-intent.",
        "starter_accounts": 1,
        "time_to_monetize": "3-6 months",
    },
    "spiritual_mindfulness": {
        "name": "Spirituality & Mindfulness",
        "platforms": ["tiktok", "instagram", "youtube"],
        "avg_rpm": "$4-9",
        "monetization": ["courses", "app affiliates (meditation)", "books", "coaching"],
        "content_types": ["affirmations", "manifestation", "meditation", "spiritual tips"],
        "difficulty": "Low",
        "conversion_rate": "HIGH",
        "why": "Deep community loyalty. Low content production cost. Course sales convert well.",
        "starter_accounts": 1,
        "time_to_monetize": "3-6 months",
    },
}

# ── Content repurposing system ───────────────────────────────────────────────

_REPURPOSE_MATRIX = {
    "tiktok_video": {
        "sources": [
            "YouTube clips (with credit or original content)",
            "Reddit posts → video format",
            "Twitter threads → slideshow",
            "News articles → quick explainer",
            "Your own daily moments",
        ],
        "tools": ["CapCut (free)", "InShot (free)", "Canva (captions)", "Descript (AI captions)"],
        "tip": "Hook in first 1.5s. Always add captions (85% watch muted). CTA at 80% mark.",
    },
    "youtube_shorts": {
        "sources": [
            "Repurpose TikTok content (remove TikTok watermark with SnapTik)",
            "Cut long-form YouTube video into Shorts",
            "Reaction to trending topics",
            "Quick how-to / tips format",
        ],
        "tools": ["YouTube Studio (built-in)", "CapCut", "Adobe Express"],
        "tip": "Upload Shorts separately from long-form. Use #Shorts in title.",
    },
    "instagram_reels": {
        "sources": [
            "Repurpose TikToks (remove watermark)",
            "Behind-the-scenes content",
            "Before/After transformations",
            "Trending audio + niche visuals",
        ],
        "tools": ["Instagram native editor", "CapCut", "VSCO"],
        "tip": "Reels get 2x organic reach vs feed posts. Cover photo matters for profile grid.",
    },
    "twitter_thread": {
        "sources": [
            "Expand TikTok script into thread",
            "List format ('10 things about X')",
            "Controversial/debate topic",
            "Story format (thread = mini-blog)",
        ],
        "tools": ["Typefully", "Hypefury", "Thread Creator (free)"],
        "tip": "First tweet = hook. Numbered threads get more replies. End with CTA.",
    },
}

# ── Theme page growth playbook ───────────────────────────────────────────────

_GROWTH_PHASES = [
    {
        "phase": "Phase 1: Foundation (Days 1-30)",
        "goal": "100-500 followers per account",
        "actions": [
            "Post 3-5 TikToks/day using trending sounds + niche hashtags",
            "Study top 10 accounts in your niche — model their format (NOT copy)",
            "Engage 30 min/day: comment on niche accounts with value-add replies",
            "Test 5-10 different video formats — track which gets highest completion rate",
            "Build content library: batch 20 videos in advance",
        ],
        "metrics_to_track": ["follower growth rate", "average views per video", "completion rate"],
    },
    {
        "phase": "Phase 2: Momentum (Days 31-90)",
        "goal": "1K-10K followers",
        "actions": [
            "Double down on the 2-3 video formats with highest views",
            "Start cross-posting: same video on TikTok, Reels, Shorts",
            "Identify your first viral video — make 5 variations of that format",
            "Create a content series (part 1, 2, 3...) to drive follows",
            "Begin building email list / Discord (platform-independent audience)",
        ],
        "metrics_to_track": ["shares per video", "profile visits per video", "follower conversion rate"],
    },
    {
        "phase": "Phase 3: Scale (Days 91-180)",
        "goal": "10K-100K followers",
        "actions": [
            "Hire a video editor or use AI tools to increase output volume",
            "Launch first monetization: digital product, affiliate link in bio",
            "Collaborate with similar-size accounts for cross-promotion",
            "Create a signature series format that audiences expect weekly",
            "Optimize bio + link-in-bio page for monetization",
        ],
        "metrics_to_track": ["revenue per 1K followers", "link-in-bio click rate", "email list growth"],
    },
    {
        "phase": "Phase 4: Monetize (180+ days)",
        "goal": "Consistent monthly revenue",
        "actions": [
            "Apply for TikTok Creator Rewards Program (10K+ followers, 100K views/month)",
            "Apply for YouTube Partner Program (1K subscribers, 4K watch hours)",
            "Pitch brands directly in your niche for sponsored posts",
            "Launch a paid community or course",
            "Hire VA to handle engagement and comments",
        ],
        "metrics_to_track": ["CPM", "affiliate commissions", "brand deal rate per post"],
    },
]

# ── Monetization thresholds ──────────────────────────────────────────────────

_MONETIZATION_TIERS = {
    "tiktok": [
        {"tier": "Creator Fund (old)", "requirement": "10K followers + 100K views/30d", "avg_monthly": "$20-80", "note": "Low payout, being phased out"},
        {"tier": "Creator Rewards Program", "requirement": "10K followers + 100K views/30d + 1-min videos", "avg_monthly": "$100-500", "note": "New program, ~$0.40-1.00 per 1K views"},
        {"tier": "LIVE Gifts", "requirement": "1K followers", "avg_monthly": "Variable", "note": "Depends on live streaming frequency"},
        {"tier": "Brand Deals", "requirement": "5K-10K followers (nano-influencer)", "avg_monthly": "$50-500/deal", "note": "DM brands or join Creator Marketplace"},
        {"tier": "TikTok Shop Affiliate", "requirement": "1K followers", "avg_monthly": "5-20% commission", "note": "Highest ROI for e-commerce niches"},
    ],
    "youtube": [
        {"tier": "YouTube Partner Program", "requirement": "1K subs + 4K watch hours OR 1K subs + 10M Shorts views", "avg_monthly": "$1-5 RPM", "note": "Ad revenue varies wildly by niche"},
        {"tier": "YouTube Shopping", "requirement": "YPP member", "avg_monthly": "Variable", "note": "Tag products in videos"},
        {"tier": "Super Thanks / Memberships", "requirement": "500+ subscribers (for memberships)", "avg_monthly": "Variable", "note": "Community-dependent"},
        {"tier": "Brand Deals", "requirement": "1K+ subscribers", "avg_monthly": "$100-5000/deal", "note": "Finance/tech niches pay most"},
    ],
    "instagram": [
        {"tier": "Instagram Bonuses (varies by country)", "requirement": "Invite-only", "avg_monthly": "Variable", "note": "Not reliably available"},
        {"tier": "Brand Deals", "requirement": "1K-10K followers", "avg_monthly": "$50-500/post", "note": "Nano-influencer rates"},
        {"tier": "Affiliate (Link in Bio)", "requirement": "Any size", "avg_monthly": "Commission-based", "note": "Use Linktree or Stan.store"},
        {"tier": "Instagram Subscriptions", "requirement": "Any size (US)", "avg_monthly": "$0.99-99/month per subscriber", "note": "Premium content paywall"},
    ],
}


# ── Public API ──────────────────────────────────────────────────────────────

def get_niches(sort_by: str = "conversion_rate") -> dict:
    """List all high-converting theme page niches."""
    niches = []
    for key, data in _NICHES.items():
        niches.append({
            "niche": key,
            "name": data["name"],
            "platforms": data["platforms"],
            "difficulty": data["difficulty"],
            "conversion_rate": data["conversion_rate"],
            "time_to_monetize": data["time_to_monetize"],
            "avg_rpm": data["avg_rpm"],
            "monetization": data["monetization"],
        })
    # Sort by conversion rate (simple ordering)
    order = {"VERY HIGH": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    if sort_by == "conversion_rate":
        niches.sort(key=lambda x: order.get(x["conversion_rate"], 99))
    return {"niches": niches, "total": len(niches)}


def get_niche_strategy(niche: str) -> dict:
    """Get detailed strategy for a specific niche."""
    data = _NICHES.get(niche.lower().replace(" ", "_"))
    if not data:
        available = list(_NICHES.keys())
        return {
            "error": f"Niche '{niche}' not found.",
            "available": available,
        }
    return {
        "niche": niche,
        **data,
        "repurpose_strategy": _REPURPOSE_MATRIX.get("tiktok_video", {}),
        "growth_phases": _GROWTH_PHASES,
        "90_day_action_plan": _generate_90_day_plan(data),
    }


def _generate_90_day_plan(niche_data: dict) -> list[dict]:
    return [
        {
            "week": "1-2",
            "actions": [
                f"Create 30 content pieces around: {', '.join(niche_data['content_types'][:3])}",
                "Set up accounts on: " + ", ".join(niche_data["platforms"]),
                "Study top 5 theme pages in this niche. Screenshot their best-performing posts.",
                "Run trends-scout to get current trending hashtags for your niche.",
            ],
        },
        {
            "week": "3-4",
            "actions": [
                "Publish 3-5 pieces/day. Track completion rate in analytics.",
                "Identify which content type gets highest completion/shares.",
                "Create a posting schedule and stick to it (consistency > volume).",
                "Start engaging with your target audience's comments on large accounts.",
            ],
        },
        {
            "week": "5-8",
            "actions": [
                "Double down on top-performing content format.",
                "Cross-post all content to every platform in the mix.",
                "Set up link-in-bio page with affiliate links for your niche.",
                "DM 3 brands/week in your niche about potential collaboration.",
            ],
        },
        {
            "week": "9-12",
            "actions": [
                "Launch first monetization: TikTok Shop or Amazon affiliate links.",
                f"Expected revenue start: {niche_data['time_to_monetize']}",
                "Begin building email list from most engaged followers.",
                "Plan a content series to push follower growth to next tier.",
            ],
        },
    ]


def get_repurpose_guide(platform: str = "tiktok_video") -> dict:
    """Get content repurposing guide for a platform."""
    guide = _REPURPOSE_MATRIX.get(platform.lower().replace(" ", "_").replace("-", "_"))
    if not guide:
        return {
            "error": f"Platform '{platform}' not found.",
            "available": list(_REPURPOSE_MATRIX.keys()),
        }
    return {"platform": platform, **guide}


def get_monetization_roadmap(platform: str = "tiktok") -> dict:
    """Get monetization tiers and thresholds for a platform."""
    tiers = _MONETIZATION_TIERS.get(platform.lower())
    if not tiers:
        return {
            "error": f"Platform '{platform}' not found.",
            "available": list(_MONETIZATION_TIERS.keys()),
        }
    return {
        "platform": platform,
        "monetization_tiers": tiers,
        "pro_tip": (
            "Don't wait for platform monetization. Brand deals and affiliate marketing "
            "activate at 1K followers — far before platform programs. "
            "Start pitching brands at 500 followers with strong engagement rate."
        ),
    }


def get_growth_roadmap() -> dict:
    """Get the full theme page growth playbook."""
    return {
        "title": "Theme Page Growth Roadmap (0 to Monetization)",
        "philosophy": (
            "Theme pages succeed because you're not the product — your NICHE is. "
            "You can repurpose content, stay anonymous, and scale to multiple accounts."
        ),
        "phases": _GROWTH_PHASES,
        "key_metrics": {
            "completion_rate": "Target >40%. Below 30% = rework your hook.",
            "follower_rate": "Healthy: 1-3% of viewers follow. Exceptional: >5%.",
            "engagement_rate": "Good: 3-6%. Great: >6%. Low: <1% (audit your content).",
        },
        "tools": {
            "free": ["CapCut (editing)", "Canva (graphics)", "Later (scheduling free tier)", "Google Trends", "this CLI"],
            "paid": ["VidIQ ($7/mo)", "Metricool ($18/mo)", "Hypefury ($19/mo)", "Epidemic Sound ($15/mo for music)"],
        },
    }
