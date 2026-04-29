"""Theme page creation, conversion, and monetization strategy engine.

A "theme page" is a content aggregation account that curates content
around a specific niche (e.g. @luxurycars, @motivationalquotes, @doglovers)
without the owner's face or original production. They can generate $500–$50K+/month.
"""

from __future__ import annotations

from typing import Optional


# ── Niche database ────────────────────────────────────────────────────────────

PROFITABLE_NICHES: list[dict] = [
    {
        "niche": "Luxury Lifestyle",
        "keywords": ["luxury", "cars", "watches", "mansions", "yachts"],
        "avg_cpm": "$8–$25",
        "monetization": ["Affiliate (car/watch brands)", "Sponsored posts", "Print-on-demand merch"],
        "content_sources": ["YouTube", "Reddit r/cars", "Unsplash", "Instagram reposts"],
        "difficulty": "Medium",
        "saturation": "High",
        "growth_speed": "Fast",
        "platforms": ["TikTok", "Instagram", "YouTube Shorts"],
    },
    {
        "niche": "Motivation / Mindset",
        "keywords": ["motivation", "mindset", "success", "discipline", "grind"],
        "avg_cpm": "$3–$12",
        "monetization": ["Digital products (ebooks, courses)", "Affiliate (self-help books)", "Sponsorships"],
        "content_sources": ["YouTube speeches", "Podcast clips", "Quote cards"],
        "difficulty": "Easy",
        "saturation": "Very High",
        "growth_speed": "Medium",
        "platforms": ["TikTok", "Instagram", "YouTube Shorts"],
    },
    {
        "niche": "Finance / Investing",
        "keywords": ["finance", "investing", "stocks", "crypto", "passive income", "money"],
        "avg_cpm": "$15–$50",
        "monetization": ["Affiliate (brokerage apps, courses)", "Digital products", "Sponsorships"],
        "content_sources": ["Bloomberg clips", "Earnings reports", "Market data charts"],
        "difficulty": "Medium",
        "saturation": "Medium",
        "growth_speed": "Medium",
        "platforms": ["YouTube", "TikTok", "Twitter/X"],
    },
    {
        "niche": "Fitness / Gym",
        "keywords": ["fitness", "gym", "workout", "bodybuilding", "calisthenics"],
        "avg_cpm": "$5–$20",
        "monetization": ["Affiliate (supplements, gear)", "Training programs", "Sponsorships"],
        "content_sources": ["Reddit r/fitness", "YouTube workout clips", "Original footage"],
        "difficulty": "Medium",
        "saturation": "High",
        "growth_speed": "Fast",
        "platforms": ["TikTok", "Instagram", "YouTube Shorts"],
    },
    {
        "niche": "Animals / Pets",
        "keywords": ["dogs", "cats", "pets", "animals", "cute animals"],
        "avg_cpm": "$2–$8",
        "monetization": ["AdSense", "Pet affiliate (Chewy, Amazon)", "Merch"],
        "content_sources": ["Reddit r/aww", "User submissions", "Stock footage"],
        "difficulty": "Easy",
        "saturation": "High",
        "growth_speed": "Very Fast",
        "platforms": ["YouTube", "TikTok", "Instagram"],
    },
    {
        "niche": "Food / Recipes",
        "keywords": ["food", "recipes", "cooking", "baking", "meal prep"],
        "avg_cpm": "$4–$15",
        "monetization": ["AdSense", "Recipe ebooks", "Affiliate (kitchen gear)", "Sponsorships"],
        "content_sources": ["Recipe blogs", "Restaurant visits", "Trending TikTok recipes"],
        "difficulty": "Easy",
        "saturation": "Medium",
        "growth_speed": "Fast",
        "platforms": ["TikTok", "Instagram", "YouTube", "Pinterest"],
    },
    {
        "niche": "Tech / AI",
        "keywords": ["tech", "AI", "gadgets", "software", "tools", "productivity"],
        "avg_cpm": "$12–$40",
        "monetization": ["Affiliate (SaaS tools)", "Sponsorships", "Courses"],
        "content_sources": ["Product launches", "Tech YouTube", "AI news"],
        "difficulty": "Medium",
        "saturation": "Low",
        "growth_speed": "Fast",
        "platforms": ["YouTube", "TikTok", "Twitter/X", "LinkedIn"],
    },
    {
        "niche": "Travel",
        "keywords": ["travel", "explore", "destinations", "backpacking", "luxury travel"],
        "avg_cpm": "$6–$20",
        "monetization": ["Affiliate (Booking.com, hotels)", "Sponsorships", "Presets/guides"],
        "content_sources": ["YouTube travel vlogs", "Drone footage", "Stock footage"],
        "difficulty": "Hard",
        "saturation": "Medium",
        "growth_speed": "Slow",
        "platforms": ["Instagram", "YouTube", "TikTok", "Pinterest"],
    },
    {
        "niche": "Gaming",
        "keywords": ["gaming", "esports", "game clips", "highlights", "fails"],
        "avg_cpm": "$2–$10",
        "monetization": ["AdSense", "Gaming affiliate", "Channel memberships", "Sponsorships"],
        "content_sources": ["Twitch clips", "Reddit", "Player-submitted clips"],
        "difficulty": "Easy",
        "saturation": "Very High",
        "growth_speed": "Fast",
        "platforms": ["YouTube", "TikTok", "Instagram"],
    },
    {
        "niche": "Real Estate",
        "keywords": ["real estate", "property", "housing", "investing", "airbnb"],
        "avg_cpm": "$20–$60",
        "monetization": ["Affiliate (courses, tools)", "Sponsorships (lenders)", "Own courses"],
        "content_sources": ["Zillow listings", "Market reports", "Case studies"],
        "difficulty": "Hard",
        "saturation": "Low",
        "growth_speed": "Medium",
        "platforms": ["YouTube", "TikTok", "Instagram"],
    },
]


# ── Conversion guide ──────────────────────────────────────────────────────────

CONVERSION_GUIDE: dict = {
    "title": "How to Create & Monetize a Viral Theme Page",
    "overview": (
        "A theme page curates niche content without requiring your face or original production. "
        "The model: find viral content → repost/remix with credit → grow audience → monetize. "
        "Top theme pages earn $1K–$50K+/month from ads, affiliates, and sponsorships."
    ),
    "phases": [
        {
            "phase": 1,
            "name": "Niche Selection",
            "duration": "1–2 days",
            "actions": [
                "Pick a niche you can post in daily without burning out",
                "Validate: search niche on TikTok — if top accounts have 100K+ followers, demand exists",
                "Choose sub-niche over broad niche (e.g. 'German Shepherd dogs' > 'pets')",
                "Check monetization: does this niche have affiliate programs or brand spend?",
            ],
            "tools": ["TikTok search", "Google Trends", "YouTube trending"],
        },
        {
            "phase": 2,
            "name": "Account Setup",
            "duration": "1 day",
            "actions": [
                "Username: @[niche]daily, @[niche]hub, @[niche]world (short, memorable)",
                "Profile pic: clean logo or niche-relevant image (use Canva)",
                "Bio: value prop + CTA + link-in-bio (Beacons or Stan Store)",
                "Set account to Creator/Business for analytics access",
                "Link all platforms: TikTok ↔ Instagram ↔ YouTube Shorts",
            ],
            "tools": ["Canva (graphics)", "Beacons.ai (link-in-bio)", "Later (scheduling)"],
        },
        {
            "phase": 3,
            "name": "Content Sourcing & Posting",
            "duration": "Ongoing",
            "actions": [
                "Source viral content: Reddit, YouTube, TikTok search, Twitter/X",
                "ALWAYS credit original creator in caption to avoid strikes",
                "Repost natively (download without watermark using SnapTik or SSSTikTok)",
                "Add your own text overlay, voiceover, or hook to add value",
                "Post 2–4x/day on TikTok in first 30 days (algorithm rewards consistency)",
                "Post same content to Instagram Reels and YouTube Shorts same day",
            ],
            "tools": ["SnapTik (TikTok downloader)", "CapCut (editing)", "VidIQ (YouTube SEO)"],
        },
        {
            "phase": 4,
            "name": "Growth Optimization",
            "duration": "Months 1–3",
            "actions": [
                "Track: check analytics daily, double down on formats with >500K views",
                "Hook formula: first 1 second must create curiosity or emotion",
                "Use trending sounds in every TikTok video",
                "Engage: reply to all comments in first hour, duet/stitch viral videos",
                "Post at 6AM, 12PM, 7PM in your primary audience timezone",
                "Run giveaways at 1K, 5K, 10K milestones to spike follows",
            ],
            "kpis": ["Profile visits", "Follow rate", "Average watch time", "Share rate"],
        },
        {
            "phase": 5,
            "name": "Monetization",
            "duration": "Month 3+",
            "actions": [
                "AdSense / TikTok Creator Fund (10K+ followers)",
                "Affiliate marketing: add Amazon/brand links in bio (start immediately)",
                "Shoutout-for-shoutout (SFS): grow by cross-promoting similar-size pages",
                "Paid shoutouts: charge $50–$500 per post at 50K+ followers",
                "Digital products: sell niche-specific presets, guides, templates",
                "Brand sponsorships: pitch brands in your niche at 10K+ followers",
            ],
            "income_timeline": {
                "1K–10K": "$0–$100/month (affiliate commissions)",
                "10K–50K": "$100–$1K/month (affiliates + small sponsorships)",
                "50K–200K": "$1K–$5K/month (sponsorships + digital products)",
                "200K–1M": "$5K–$20K/month (multiple streams)",
                "1M+": "$20K–$100K+/month",
            },
        },
    ],
    "common_mistakes": [
        "Posting without credit → strikes and account bans",
        "Inconsistent posting → algorithm stops distributing content",
        "Choosing too broad a niche → hard to attract loyal followers",
        "Not adding link-in-bio from day 1 → missed affiliate revenue",
        "Ignoring comments → low engagement kills reach",
        "Switching niche after 2 weeks → restart the algorithm clock",
    ],
    "legal_considerations": [
        "Always credit the original creator",
        "Use royalty-free music or platform-licensed sounds only",
        "Don't repost content if creator has explicitly said no",
        "Register as a business once earning $500+/month for tax purposes",
        "Disclose sponsored content with #ad or #sponsored",
    ],
}


# ── Public API ────────────────────────────────────────────────────────────────

def get_profitable_niches(
    sort_by: str = "growth_speed",
    max_results: int = 10,
    difficulty: Optional[str] = None,
    platform: Optional[str] = None,
) -> list[dict]:
    """Return ranked profitable theme page niches."""
    niches = PROFITABLE_NICHES.copy()
    if difficulty:
        niches = [n for n in niches if n["difficulty"].lower() == difficulty.lower()]
    if platform:
        niches = [n for n in niches if platform.lower() in [p.lower() for p in n["platforms"]]]

    speed_order = {"Very Fast": 0, "Fast": 1, "Medium": 2, "Slow": 3}
    difficulty_order = {"Easy": 0, "Medium": 1, "Hard": 2}

    if sort_by == "growth_speed":
        niches.sort(key=lambda x: speed_order.get(x["growth_speed"], 99))
    elif sort_by == "difficulty":
        niches.sort(key=lambda x: difficulty_order.get(x["difficulty"], 99))
    elif sort_by == "saturation":
        sat_order = {"Low": 0, "Medium": 1, "High": 2, "Very High": 3}
        niches.sort(key=lambda x: sat_order.get(x["saturation"], 99))

    return niches[:max_results]


def generate_strategy(niche: str, platform: str = "tiktok") -> dict:
    """Generate a detailed theme page strategy for a specific niche."""
    niche_data = _find_niche(niche)
    return {
        "niche": niche,
        "platform": platform,
        "summary": (
            f"Build a {niche} theme page on {platform.title()}. "
            f"Expected difficulty: {niche_data.get('difficulty', 'Medium')}. "
            f"Growth speed: {niche_data.get('growth_speed', 'Medium')}."
        ),
        "recommended_username_formats": [
            f"@{niche.lower().replace(' ', '')}daily",
            f"@{niche.lower().replace(' ', '')}hub",
            f"@best{niche.lower().replace(' ', '')}",
            f"@the{niche.lower().replace(' ', '')}page",
        ],
        "content_pillars": _content_pillars(niche),
        "posting_schedule": _niche_posting_schedule(platform),
        "monetization_path": niche_data.get("monetization", []),
        "content_sources": niche_data.get("content_sources", []),
        "hashtag_starter_pack": _starter_hashtags(niche),
        "first_30_days_plan": _thirty_day_plan(niche, platform),
        "kpis_to_track": [
            "Daily follower growth",
            "Average view duration (aim >50%)",
            "Profile visit-to-follow rate (aim >15%)",
            "Link-in-bio click rate",
        ],
    }


def get_conversion_guide(section: Optional[str] = None) -> dict:
    """Return the full theme page creation guide or a specific section."""
    if section:
        section_lower = section.lower()
        for phase in CONVERSION_GUIDE["phases"]:
            if section_lower in phase["name"].lower():
                return phase
        return {"error": f"Section '{section}' not found", "available": [p["name"] for p in CONVERSION_GUIDE["phases"]]}
    return CONVERSION_GUIDE


def compare_niches(niche_a: str, niche_b: str) -> dict:
    """Side-by-side comparison of two niches."""
    a = _find_niche(niche_a)
    b = _find_niche(niche_b)
    return {
        "comparison": [
            {
                "metric": k,
                niche_a: a.get(k, "N/A"),
                niche_b: b.get(k, "N/A"),
            }
            for k in ["difficulty", "saturation", "growth_speed", "avg_cpm", "platforms"]
        ],
        "recommendation": _recommend_between(a, b, niche_a, niche_b),
    }


def get_monetization_timeline(niche: str) -> dict:
    """Return expected income timeline for a theme page in this niche."""
    niche_data = _find_niche(niche)
    return {
        "niche": niche,
        "income_by_stage": CONVERSION_GUIDE["phases"][-1].get("income_timeline", {}),
        "monetization_methods": niche_data.get("monetization", []),
        "cpm_range": niche_data.get("avg_cpm", "$3–$15"),
        "fastest_monetization": (
            "Affiliate links — add from day 1. No follower minimum required. "
            "Focus on products your niche audience actually buys."
        ),
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _find_niche(niche: str) -> dict:
    niche_lower = niche.lower()
    for n in PROFITABLE_NICHES:
        if niche_lower in n["niche"].lower():
            return n
        if any(k in niche_lower for k in n["keywords"]):
            return n
    return {"niche": niche, "difficulty": "Unknown", "saturation": "Unknown", "growth_speed": "Unknown",
            "monetization": ["Affiliate marketing", "Sponsorships", "Digital products"],
            "content_sources": ["YouTube", "Reddit", "TikTok search"], "avg_cpm": "$3–$15"}


def _content_pillars(niche: str) -> list[dict]:
    return [
        {"pillar": "Education/Tips", "share": 35, "example": f"'5 things you didn't know about {niche}'"},
        {"pillar": "Inspiration/Motivation", "share": 25, "example": f"'This {niche} transformation will inspire you'"},
        {"pillar": "Entertainment/Humor", "share": 20, "example": f"'Only {niche} people will understand this'"},
        {"pillar": "Trending/News", "share": 15, "example": f"'The biggest {niche} news this week'"},
        {"pillar": "Community/UGC", "share": 5, "example": f"'Send me your {niche} content to be featured'"},
    ]


def _starter_hashtags(niche: str) -> dict:
    clean = niche.lower().replace(" ", "")
    return {
        "niche_specific": [f"#{clean}", f"#{clean}tips", f"#{clean}daily", f"#{clean}lover"],
        "broad": ["#viral", "#foryou", "#trending"],
        "community": [f"#{clean}community", f"#{clean}life", f"#{clean}tok"],
        "strategy": "Use 3-5 total. Rotate to find which combo drives most reach.",
    }


def _niche_posting_schedule(platform: str) -> dict:
    from .account_optimizer import _POSTING_SCHEDULES
    return _POSTING_SCHEDULES.get(platform.lower(), _POSTING_SCHEDULES["tiktok"])


def _thirty_day_plan(niche: str, platform: str) -> list[dict]:
    return [
        {
            "week": 1,
            "goal": "Set up + publish 14 pieces of content",
            "actions": [
                "Create account, write bio, add link-in-bio",
                "Research top 20 accounts in niche — analyze their best videos",
                "Post 2x/day — pure reposts with credit + trending sound",
                "Set up affiliate links (Amazon Associates minimum)",
            ],
        },
        {
            "week": 2,
            "goal": "Find your first viral format",
            "actions": [
                "Check analytics — find your top 3 posts, double down on that format",
                "Post 2–3x/day — start mixing in value-added content (add text overlay or voiceover)",
                "Comment on 20 videos/day in your niche to drive profile visits",
                "Set up cross-posting to Instagram Reels + YouTube Shorts",
            ],
        },
        {
            "week": 3,
            "goal": "Build community signals",
            "actions": [
                "Run first poll or question-sticker story to get engagement data",
                "Reply to EVERY comment — algorithm rewards high comment engagement",
                "Do a SFS (shoutout for shoutout) with 2–3 accounts at similar size",
                "Post a 'comment your [niche question]' video for comment bait",
            ],
        },
        {
            "week": 4,
            "goal": "Optimize and scale",
            "actions": [
                "Audit: which content type drives most followers per view?",
                "Cut formats not working. Add 1 new experimental format.",
                "Push hardest monetization method (affiliate link in bio CTA)",
                "Plan month 2: set specific follower and revenue targets",
            ],
        },
    ]


def _recommend_between(a: dict, b: dict, name_a: str, name_b: str) -> str:
    speed_order = {"Very Fast": 4, "Fast": 3, "Medium": 2, "Slow": 1}
    sat_order = {"Low": 4, "Medium": 3, "High": 2, "Very High": 1}
    diff_order = {"Easy": 3, "Medium": 2, "Hard": 1}

    score_a = (
        speed_order.get(a.get("growth_speed", "Medium"), 2)
        + sat_order.get(a.get("saturation", "Medium"), 2)
        + diff_order.get(a.get("difficulty", "Medium"), 2)
    )
    score_b = (
        speed_order.get(b.get("growth_speed", "Medium"), 2)
        + sat_order.get(b.get("saturation", "Medium"), 2)
        + diff_order.get(b.get("difficulty", "Medium"), 2)
    )

    winner = name_a if score_a >= score_b else name_b
    return (
        f"We recommend starting with {winner}. "
        "Consider your personal interest — passion reduces burnout risk for long-term consistency."
    )
