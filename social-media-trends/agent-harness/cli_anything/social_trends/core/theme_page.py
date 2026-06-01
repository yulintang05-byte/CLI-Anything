#!/usr/bin/env python3
"""Theme page strategy engine — conversion-focused niche page playbook."""


PROFITABLE_NICHES = {
    "finance": {
        "cpm_potential": "high",
        "monetization": ["affiliate (Robinhood, Coinbase, Acorns)", "digital products (ebook, course)", "newsletter", "consulting"],
        "content_pillars": ["money mistakes", "passive income ideas", "investing for beginners", "debt payoff", "side hustles"],
        "viral_formats": ["storytime earnings", "cashflow screenshots", "react to bad money advice", "before/after savings"],
        "conversion_funnel": "TikTok/YT → link in bio → free lead magnet → email list → paid offer",
        "avg_rpm": "$8-15",
        "competition": "high",
        "trend_score": 95,
    },
    "fitness": {
        "cpm_potential": "medium-high",
        "monetization": ["coaching DMs", "workout programs (Gumroad/Whop)", "supplement affiliate", "brand deals"],
        "content_pillars": ["transformation stories", "workout of the day", "nutrition myths", "home workout hacks", "gym fails"],
        "viral_formats": ["30-day transformation", "react to bad fitness advice", "hidden gym tips", "calorie reveals"],
        "conversion_funnel": "Reel/Short → profile → free training PDF → DM coaching → program sale",
        "avg_rpm": "$4-8",
        "competition": "very high",
        "trend_score": 88,
    },
    "motivation": {
        "cpm_potential": "medium",
        "monetization": ["digital journals (Etsy/Gumroad)", "affiliate (books, courses)", "speaking", "membership community"],
        "content_pillars": ["mindset shifts", "morning routines", "success stories", "book summaries", "daily affirmations"],
        "viral_formats": ["life-changing quotes with visuals", "CEO morning routine", "react to success stories", "1 tip per day series"],
        "conversion_funnel": "YT/TikTok → free ebook → email nurture → paid course/community",
        "avg_rpm": "$3-6",
        "competition": "medium",
        "trend_score": 82,
    },
    "luxury_lifestyle": {
        "cpm_potential": "high",
        "monetization": ["brand deals (hotels, watches, fashion)", "affiliate luxury items", "travel consulting"],
        "content_pillars": ["luxury hotel reviews", "luxury car content", "expensive experiences", "rich lifestyle tips"],
        "viral_formats": ["price reveals", "luxury vs budget", "unboxings", "day in the life"],
        "conversion_funnel": "Content → link in bio → booking/affiliate links",
        "avg_rpm": "$10-20",
        "competition": "medium",
        "trend_score": 79,
    },
    "tech": {
        "cpm_potential": "high",
        "monetization": ["tech affiliate (Amazon, Best Buy)", "sponsored reviews", "AdSense", "AI tool affiliate"],
        "content_pillars": ["AI tools", "phone/laptop reviews", "coding tips", "tech hacks", "new releases"],
        "viral_formats": ["tools you didn't know existed", "AI that changes everything", "vs comparisons", "budget vs premium"],
        "conversion_funnel": "YouTube → description links → affiliate purchases",
        "avg_rpm": "$6-12",
        "competition": "high",
        "trend_score": 91,
    },
    "beauty": {
        "cpm_potential": "medium-high",
        "monetization": ["brand deals", "affiliate (Amazon, Sephora)", "digital look books", "UGC content creation"],
        "content_pillars": ["get-ready-with-me", "product reviews", "drugstore vs high-end", "skincare routines", "tutorials"],
        "viral_formats": ["product dupes", "makeup transformations", "react to beauty hacks", "GRWM storytimes"],
        "conversion_funnel": "TikTok GRWM → link in bio → LTK/Amazon storefront → commission",
        "avg_rpm": "$4-9",
        "competition": "very high",
        "trend_score": 85,
    },
}

CONVERSION_FUNNEL_STAGES = [
    {
        "stage": 1,
        "name": "Awareness",
        "platform": "TikTok / YouTube Shorts",
        "goal": "Stop the scroll — get views",
        "tactics": [
            "Use trending audio in first 3 seconds",
            "Open with a bold hook or controversial statement",
            "Show end result immediately (transformation, money, etc.)",
            "Post at peak times (see schedule command)",
        ],
        "kpi": "Views, profile visits",
    },
    {
        "stage": 2,
        "name": "Profile Visit",
        "platform": "TikTok / YouTube Channel",
        "goal": "Convert viewer to follower",
        "tactics": [
            "Pinned posts must be your BEST performing content",
            "Bio must clearly state WHO you help and HOW",
            "Consistent aesthetic and niche (no off-topic posts visible)",
            "Include social proof (followers, results) in bio if possible",
        ],
        "kpi": "Follow rate, profile-to-follow conversion",
    },
    {
        "stage": 3,
        "name": "Link Click",
        "platform": "Link in Bio (Beacons / Linktree / Stan Store)",
        "goal": "Drive traffic off-platform",
        "tactics": [
            "Mention 'link in bio' every 3rd post minimum",
            "Offer a free lead magnet (checklist, guide, mini-course)",
            "Use 'grab the free [X]' CTA — specific > vague",
            "Link page should have ONE clear primary CTA, not 10 links",
        ],
        "kpi": "Link click rate, CTR",
    },
    {
        "stage": 4,
        "name": "Lead Capture",
        "platform": "Landing Page / Email Opt-in",
        "goal": "Capture email or DM",
        "tactics": [
            "Landing page headline must match the promise from the video",
            "Offer is specific: '5-day email course', '10-page PDF guide'",
            "Remove all navigation — one action only",
            "Social proof above the fold (# of subscribers, testimonials)",
        ],
        "kpi": "Opt-in rate (aim for 30%+)",
    },
    {
        "stage": 5,
        "name": "Nurture",
        "platform": "Email / DM Sequence",
        "goal": "Build trust, deliver value, make offer",
        "tactics": [
            "Welcome email delivers freebie immediately",
            "3-5 value emails before any sales pitch",
            "Share your story / transformation",
            "Address top 3 objections your audience has",
        ],
        "kpi": "Open rate (>25%), click rate (>3%)",
    },
    {
        "stage": 6,
        "name": "Conversion",
        "platform": "Sales Page / DM",
        "goal": "Make the sale",
        "tactics": [
            "Offer must be an obvious YES (clear ROI > price)",
            "Scarcity/urgency (limited spots, price increase)",
            "Money-back guarantee removes risk",
            "Multiple testimonials and case studies",
        ],
        "kpi": "Conversion rate (aim for 2-5% of email list)",
    },
]

THEME_PAGE_MISTAKES = [
    "Posting inconsistently — algorithm punishes gaps > 3 days",
    "No clear niche — posting random content confuses the algorithm AND audience",
    "Missing link in bio or linking to homepage instead of lead magnet",
    "Never mentioning 'link in bio' in videos",
    "Copying trends without adapting to your niche",
    "Not engaging with comments — kills engagement rate",
    "Buying followers — destroys engagement rate and shadowbans account",
    "Giving up before 90 days — most pages don't gain traction until month 2-3",
    "Only posting when inspiration hits — treat it like a business, not a hobby",
    "No email list — social platforms can suspend accounts; own your audience",
]


def get_niche_playbook(niche: str) -> dict:
    """Return full monetization and growth playbook for a niche."""
    niche_lower = niche.lower()
    # Find closest match
    data = PROFITABLE_NICHES.get(niche_lower)
    if not data:
        for key in PROFITABLE_NICHES:
            if key in niche_lower or niche_lower in key:
                data = PROFITABLE_NICHES[key]
                break
    if not data:
        data = PROFITABLE_NICHES["motivation"]  # Default fallback

    return {
        "niche": niche,
        "profitability": data["cpm_potential"],
        "trend_score": data["trend_score"],
        "competition_level": data["competition"],
        "monetization_methods": data["monetization"],
        "content_pillars": data["content_pillars"],
        "viral_content_formats": data["viral_formats"],
        "conversion_funnel": data["conversion_funnel"],
        "estimated_rpm": data["avg_rpm"],
        "90_day_roadmap": _build_90_day_roadmap(niche, data),
    }


def get_conversion_funnel(niche: str = "") -> list[dict]:
    """Return the 6-stage conversion funnel with niche-specific tactics."""
    return CONVERSION_FUNNEL_STAGES


def list_profitable_niches() -> list[dict]:
    """Rank niches by profitability + trend score."""
    return sorted(
        [
            {
                "niche": k,
                "trend_score": v["trend_score"],
                "cpm_potential": v["cpm_potential"],
                "competition": v["competition"],
                "top_monetization": v["monetization"][0],
                "estimated_rpm": v["avg_rpm"],
            }
            for k, v in PROFITABLE_NICHES.items()
        ],
        key=lambda x: x["trend_score"],
        reverse=True,
    )


def get_mistakes_to_avoid() -> list[dict]:
    """Return common theme page mistakes ranked by impact."""
    return [{"rank": i + 1, "mistake": m} for i, m in enumerate(THEME_PAGE_MISTAKES)]


def _build_90_day_roadmap(niche: str, data: dict) -> list[dict]:
    return [
        {
            "phase": "Days 1-30: Foundation",
            "goals": [
                "Post 1-2x/day consistently",
                f"Master 2-3 content pillars: {', '.join(data['content_pillars'][:2])}",
                "Set up link in bio with free lead magnet",
                "Engage on every comment for first 30 days",
                "Research top 10 accounts in your niche",
            ],
            "target_metric": "500-1,000 followers, find what resonates",
        },
        {
            "phase": "Days 31-60: Growth",
            "goals": [
                "Double down on top-performing content formats",
                f"Test viral formats: {data['viral_formats'][0]}",
                "Launch email list / lead magnet",
                "Collaborate with 2-3 accounts in your niche",
                "Optimize bio based on which content converts best",
            ],
            "target_metric": "2,000-5,000 followers, 100+ email subscribers",
        },
        {
            "phase": "Days 61-90: Monetize",
            "goals": [
                f"Launch first offer: {data['monetization'][0]}",
                "Build email nurture sequence (5 emails)",
                "Apply for brand deal outreach (100+ DMs if needed)",
                "Create evergreen lead magnet + automated funnel",
                "Test paid promotion on best-performing post",
            ],
            "target_metric": f"5,000-10,000 followers, first revenue, RPM target: {data['avg_rpm']}",
        },
    ]
