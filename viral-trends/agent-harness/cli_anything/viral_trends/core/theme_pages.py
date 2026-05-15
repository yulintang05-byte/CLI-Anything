"""Theme page guide — converting niche pages, monetization strategies, and growth playbooks."""

CONVERTING_NICHES = {
    "fitness": {
        "description": "Workout routines, transformation content, supplements, diet tips",
        "monetization": ["Affiliate (supplements, gear)", "Digital products (programs)", "Coaching DMs", "Brand deals"],
        "content_mix": {"educational": 40, "entertainment": 30, "promotional": 15, "community": 15},
        "avg_cpm": "$4-8",
        "conversion_rate": "2-5%",
        "top_ctas": ["Free workout in bio", "DM 'PLAN' for program", "Link for 20% off"],
        "difficulty": "Medium",
        "competition": "High",
    },
    "finance": {
        "description": "Investing tips, budgeting, side hustles, financial freedom",
        "monetization": ["Affiliate (apps, brokers)", "Digital products (spreadsheets, courses)", "Paid newsletter", "Consulting"],
        "content_mix": {"educational": 60, "entertainment": 20, "promotional": 10, "community": 10},
        "avg_cpm": "$8-15",
        "conversion_rate": "3-8%",
        "top_ctas": ["Free budget template in bio", "DM 'START' for guide", "Join free Discord"],
        "difficulty": "Low",
        "competition": "Medium",
    },
    "travel": {
        "description": "Destinations, travel hacks, budget travel, hotel/flight deals",
        "monetization": ["Affiliate (hotels, booking)", "Brand collabs", "Presets/guides", "Tourism boards"],
        "content_mix": {"educational": 25, "entertainment": 50, "promotional": 15, "community": 10},
        "avg_cpm": "$3-6",
        "conversion_rate": "1-3%",
        "top_ctas": ["Save for your next trip", "Full guide in bio", "DM for itinerary"],
        "difficulty": "High",
        "competition": "Very High",
    },
    "motivation": {
        "description": "Mindset content, success stories, self-improvement, hustle culture",
        "monetization": ["Affiliate (courses, books)", "Paid community", "Merchandise", "Brand deals"],
        "content_mix": {"educational": 30, "entertainment": 40, "promotional": 15, "community": 15},
        "avg_cpm": "$2-5",
        "conversion_rate": "1-3%",
        "top_ctas": ["Follow for daily mindset", "Link to free course", "Join the community"],
        "difficulty": "Low",
        "competition": "Very High",
    },
    "tech": {
        "description": "AI tools, gadgets, software reviews, coding tips, startup news",
        "monetization": ["Affiliate (SaaS, tools)", "Sponsored posts", "Courses", "Newsletter"],
        "content_mix": {"educational": 55, "entertainment": 25, "promotional": 15, "community": 5},
        "avg_cpm": "$10-20",
        "conversion_rate": "4-10%",
        "top_ctas": ["Link to free AI tools list", "Subscribe to newsletter", "DM for tool stack"],
        "difficulty": "Medium",
        "competition": "Low-Medium",
    },
    "beauty": {
        "description": "Makeup tutorials, skincare routines, product reviews, GRWM",
        "monetization": ["Affiliate (Amazon, Sephora)", "Brand deals", "LTK", "Courses"],
        "content_mix": {"educational": 35, "entertainment": 35, "promotional": 20, "community": 10},
        "avg_cpm": "$3-7",
        "conversion_rate": "3-6%",
        "top_ctas": ["Products linked in bio", "Save this routine", "Shop my look"],
        "difficulty": "Medium",
        "competition": "Very High",
    },
    "food": {
        "description": "Recipes, restaurant reviews, meal prep, cooking hacks",
        "monetization": ["Affiliate (kitchenware, groceries)", "Cookbook/ebook", "Brand deals", "Cooking classes"],
        "content_mix": {"educational": 40, "entertainment": 40, "promotional": 15, "community": 5},
        "avg_cpm": "$3-5",
        "conversion_rate": "2-4%",
        "top_ctas": ["Full recipe in caption", "Save for meal prep", "Cookbook link in bio"],
        "difficulty": "Low",
        "competition": "High",
    },
    "fashion": {
        "description": "OOTDs, styling tips, trend alerts, budget dupes, hauls",
        "monetization": ["LTK/affiliate", "Brand collabs", "Styling services", "Own brand"],
        "content_mix": {"educational": 20, "entertainment": 50, "promotional": 25, "community": 5},
        "avg_cpm": "$3-6",
        "conversion_rate": "3-7%",
        "top_ctas": ["Shop linked in bio", "Save this outfit", "Dupe in comments"],
        "difficulty": "Medium",
        "competition": "Very High",
    },
}

THEME_PAGE_PHASES = [
    {
        "phase": 1,
        "name": "Foundation (Days 1-30)",
        "goal": "0 → 1,000 followers",
        "tasks": [
            "Pick ONE niche — do not mix content types",
            "Set up optimized bio: who you help + CTA + link",
            "Post 1-2x daily using trending audio/hashtags",
            "Study top 10 accounts in your niche — model their hooks",
            "Engage 30 min/day: comment on similar content",
            "Profile pic + banner must match niche aesthetic",
        ],
        "kpi": "1,000 followers, 3%+ engagement rate",
    },
    {
        "phase": 2,
        "name": "Growth (Days 31-90)",
        "goal": "1K → 10K followers",
        "tasks": [
            "Find your 3 best performing content formats and double down",
            "Introduce soft CTAs: 'Follow for part 2', 'Save this'",
            "Start building an email list (free lead magnet)",
            "Collab or duet with accounts at similar size",
            "Add 1 affiliate link — test one product naturally",
            "Post Stories daily + use polls to boost engagement",
        ],
        "kpi": "10,000 followers, 5%+ engagement, first $100 from affiliate",
    },
    {
        "phase": 3,
        "name": "Monetization (Days 91-180)",
        "goal": "10K → 50K followers",
        "tasks": [
            "Launch a low-ticket digital product ($7-$27)",
            "Pitch 3-5 brands for sponsored posts",
            "Set up a paid community (Discord/Telegram) at $9.99/mo",
            "Use content repurposing: 1 long-form → 5 short clips",
            "Implement email sequences (welcome → value → offer)",
            "Track analytics weekly — kill underperforming content types",
        ],
        "kpi": "$1,000+/month, 10+ brand inquiries",
    },
    {
        "phase": 4,
        "name": "Scale (Day 181+)",
        "goal": "50K → 500K followers",
        "tasks": [
            "Hire a video editor + content manager",
            "Post on all platforms (TikTok + YT Shorts + Reels simultaneously)",
            "Launch a $97-$297 course or coaching program",
            "Negotiate long-term brand deals (3-6 month contracts)",
            "Build a waitlist for premium products",
            "Consider running paid ads to top-performing organic posts",
        ],
        "kpi": "$10,000+/month, diversified income streams",
    },
]

PERSONAL_TO_THEME_CONVERSION = {
    "steps": [
        {
            "step": 1,
            "action": "Niche audit",
            "detail": "Identify your top 3 performing content topics. Pick 1 to double down on.",
        },
        {
            "step": 2,
            "action": "Username + bio overhaul",
            "detail": "Change username to niche-related (e.g., @fitnesswith_[name]). Rewrite bio: [What you do] | [Who you help] | [CTA + link]",
        },
        {
            "step": 3,
            "action": "Archive off-niche content",
            "detail": "Archive (not delete) any content that doesn't fit the new niche. This resets your algorithm signal without losing the posts.",
        },
        {
            "step": 4,
            "action": "Post 10 on-niche pieces back-to-back",
            "detail": "Signal the algorithm your new direction by posting 10 niche-specific posts within 7-10 days.",
        },
        {
            "step": 5,
            "action": "Update all links",
            "detail": "Replace personal links with niche-relevant: lead magnet, affiliate product, or free resource.",
        },
        {
            "step": 6,
            "action": "Engage in the niche community",
            "detail": "Comment 20-30 times per day on top niche hashtags to pull new followers.",
        },
        {
            "step": 7,
            "action": "Pin a value post",
            "detail": "Pin your highest-value or highest-performing post to show new visitors what you're about.",
        },
    ],
    "timeline": "Expect 2-4 weeks for algorithm to recalibrate. Follower dips are normal — they stabilize.",
    "warning": "Do not switch niches more than once — it permanently damages algorithm trust.",
}

HOOK_FORMULAS = [
    "Stop scrolling if you [desire/problem]",
    "I made $X in 30 days doing this [niche tip]",
    "Nobody talks about this [niche] hack",
    "POV: You finally [achieved outcome]",
    "This [niche] mistake is costing you [loss]",
    "The [niche] secret [authority figure] doesn't want you to know",
    "Rate my [niche thing] 1-10",
    "Watch until the end — you'll thank me",
    "Things I wish I knew before [starting niche activity]",
    "[Number] [niche] tips that changed my life",
]


def get_niche_guide(niche: str) -> dict:
    """Return a full guide for a specific converting niche."""
    niche = niche.lower()
    if niche not in CONVERTING_NICHES:
        return {
            "error": f"Niche '{niche}' not found",
            "available": list(CONVERTING_NICHES.keys()),
        }
    info = CONVERTING_NICHES[niche]
    return {
        "niche": niche,
        **info,
        "growth_phases": THEME_PAGE_PHASES,
        "hook_formulas": HOOK_FORMULAS,
    }


def list_niches() -> list[dict]:
    """Return all converting niches with summary metrics."""
    return [
        {
            "niche": k,
            "description": v["description"],
            "avg_cpm": v["avg_cpm"],
            "conversion_rate": v["conversion_rate"],
            "difficulty": v["difficulty"],
            "competition": v["competition"],
            "top_monetization": v["monetization"][0],
        }
        for k, v in CONVERTING_NICHES.items()
    ]


def get_conversion_guide() -> dict:
    """Return the personal-to-theme-page conversion playbook."""
    return {
        "title": "Personal → Theme Page Conversion Playbook",
        **PERSONAL_TO_THEME_CONVERSION,
        "growth_phases": THEME_PAGE_PHASES,
        "hook_formulas": HOOK_FORMULAS,
    }


def get_growth_phases() -> list[dict]:
    return THEME_PAGE_PHASES
