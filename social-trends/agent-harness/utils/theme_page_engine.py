"""
Theme page creation and conversion optimization engine.

A "theme page" is a niche-focused account that curates and reposts
trending content in a specific aesthetic/topic, grows a massive audience,
then monetizes through brand deals, affiliates, and digital products.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional


# ---------------------------------------------------------------------------
# Niche library
# ---------------------------------------------------------------------------

NICHES: dict[str, dict] = {
    "luxury_lifestyle": {
        "description": "Luxury cars, watches, travel, real estate",
        "avg_cpm_usd": 45,
        "saturation": "medium",
        "growth_speed": "fast",
        "best_platforms": ["instagram", "tiktok"],
        "content_pillars": ["car reveals", "penthouse tours", "watch collections",
                            "first-class travel", "lifestyle motivation"],
        "monetization": ["luxury brand deals", "affiliate (watch/car)", "presets"],
        "hook_templates": [
            "POV: you just bought your first Rolex...",
            "What $10M looks like in real life",
            "Billionaire morning routine (not what you think)",
        ],
        "viral_formula": "aspirational + unattainable + achievable tip at end",
    },
    "fitness_motivation": {
        "description": "Workout clips, body transformations, nutrition",
        "avg_cpm_usd": 12,
        "saturation": "high",
        "growth_speed": "medium",
        "best_platforms": ["tiktok", "instagram", "youtube"],
        "content_pillars": ["workout tutorials", "transformation stories",
                            "diet tips", "gym aesthetic", "recovery"],
        "monetization": ["supplement affiliate", "fitness programs", "merch"],
        "hook_templates": [
            "I lost 30lbs in 90 days doing THIS...",
            "The workout you're skipping that kills gains",
            "Gym hack that 99% of people miss",
        ],
        "viral_formula": "transformation + controversy + simple actionable tip",
    },
    "dark_academia": {
        "description": "Books, study aesthetic, classical education",
        "avg_cpm_usd": 8,
        "saturation": "low",
        "growth_speed": "slow_but_loyal",
        "best_platforms": ["tiktok", "instagram"],
        "content_pillars": ["booktok recommendations", "study with me",
                            "aesthetic libraries", "classical music", "journaling"],
        "monetization": ["book affiliate (Amazon)", "Notion templates", "course"],
        "hook_templates": [
            "Books that will make you dangerous...",
            "5 dark academia novels that changed my life",
            "Study aesthetic that actually works",
        ],
        "viral_formula": "aesthetics + knowledge + mystery",
    },
    "finance_hustle": {
        "description": "Money mindset, side hustles, investing basics",
        "avg_cpm_usd": 30,
        "saturation": "medium",
        "growth_speed": "fast",
        "best_platforms": ["tiktok", "youtube", "instagram"],
        "content_pillars": ["side hustle reveals", "investing 101",
                            "budget breakdowns", "passive income", "income reports"],
        "monetization": ["fintech affiliate", "courses", "ebooks", "coaching"],
        "hook_templates": [
            "How I made $5K last month with 0 followers",
            "The side hustle that nobody is talking about",
            "Stop buying coffee — invest in THIS instead",
        ],
        "viral_formula": "income claim + proof + replicable method",
    },
    "aesthetic_food": {
        "description": "Recipe videos, food prep, aesthetic meals",
        "avg_cpm_usd": 10,
        "saturation": "high",
        "growth_speed": "medium",
        "best_platforms": ["tiktok", "instagram", "youtube_shorts"],
        "content_pillars": ["15-second recipes", "meal prep sundays",
                            "aesthetic plating", "ingredient swaps", "restaurant dupes"],
        "monetization": ["kitchen affiliate", "cookbook", "meal plan subscriptions"],
        "hook_templates": [
            "5-ingredient dinner that looks $100...",
            "I tried this viral recipe so you don't have to",
            "The meal prep mistake costing you hours",
        ],
        "viral_formula": "visual satisfaction + speed + relatable problem solved",
    },
    "travel_minimalist": {
        "description": "Budget travel, van life, digital nomad",
        "avg_cpm_usd": 18,
        "saturation": "medium",
        "growth_speed": "medium",
        "best_platforms": ["youtube", "tiktok", "instagram"],
        "content_pillars": ["budget hacks", "hidden gems", "packing guides",
                            "remote work setups", "country comparisons"],
        "monetization": ["travel affiliate (booking/hotels)", "presets", "ebook"],
        "hook_templates": [
            "I traveled Europe for $15/day",
            "Places to visit before the tourists find out",
            "My van life setup cost less than rent",
        ],
        "viral_formula": "dream + affordability + actionable tips",
    },
    "tech_minimal": {
        "description": "Minimal desk setups, productivity tools, apps",
        "avg_cpm_usd": 25,
        "saturation": "medium",
        "growth_speed": "fast",
        "best_platforms": ["youtube", "tiktok", "twitter"],
        "content_pillars": ["desk setup tours", "app reviews", "productivity systems",
                            "tech unboxing", "workflow automations"],
        "monetization": ["tech affiliate (Amazon/Best Buy)", "notion templates", "courses"],
        "hook_templates": [
            "The app that 10x'd my productivity",
            "My $5000 desk setup (worth it?)",
            "Tools that saved me 10 hours this week",
        ],
        "viral_formula": "curiosity + proof + immediate value",
    },
    "mental_wellness": {
        "description": "Mindfulness, therapy tips, self-care routines",
        "avg_cpm_usd": 15,
        "saturation": "low",
        "growth_speed": "fast",
        "best_platforms": ["tiktok", "instagram"],
        "content_pillars": ["anxiety tips", "boundaries", "toxic pattern awareness",
                            "morning routines", "journaling prompts"],
        "monetization": ["wellness affiliate", "journal products", "coaching"],
        "hook_templates": [
            "Signs you grew up with emotional neglect",
            "The anxiety hack therapists don't advertise",
            "Stop saying sorry for these 5 things",
        ],
        "viral_formula": "vulnerable truth + universally relatable + empowerment",
    },
}


# ---------------------------------------------------------------------------
# Conversion strategies
# ---------------------------------------------------------------------------

CONVERSION_STRATEGIES: list[dict] = [
    {
        "name": "Bio CTA Funnel",
        "description": "Single link-in-bio pointing to lead magnet",
        "steps": [
            "Add one clear CTA in bio ('free checklist → link below')",
            "Use Linktree/Stan Store/Beacons as landing page",
            "Offer free lead magnet (PDF, template, mini-course)",
            "Capture email for long-term monetization",
        ],
        "conversion_rate": "2-5% of profile visitors",
        "time_to_implement": "2 hours",
    },
    {
        "name": "DM Funnel",
        "description": "Use comments to trigger DM sequences",
        "steps": [
            "Post: 'Comment GUIDE and I'll DM you the free resource'",
            "Use ManyChat/MobileMonkey to auto-DM commenters",
            "DM contains value + soft pitch to product",
            "Follow-up sequence over 3-5 days",
        ],
        "conversion_rate": "15-25% of DM recipients",
        "time_to_implement": "4 hours",
    },
    {
        "name": "Content Waterfall",
        "description": "Repurpose 1 piece of content across all platforms",
        "steps": [
            "Create long-form YouTube video (10-20 min)",
            "Extract 5-10 clips for TikTok/Reels/Shorts",
            "Pull quotes for Twitter/X threads",
            "Write email newsletter from transcript",
            "Create Pinterest infographic from key points",
        ],
        "conversion_rate": "3x content output from same effort",
        "time_to_implement": "2 hours extra per video",
    },
    {
        "name": "Social Proof Loop",
        "description": "Use early results to attract more followers",
        "steps": [
            "Screenshot/record early wins (first sale, first 1K, etc.)",
            "Post 'I did X in Y days' content",
            "Tag method/product that got the result",
            "Show before/after proof clearly",
        ],
        "conversion_rate": "5-8% follower-to-action rate",
        "time_to_implement": "30 min per post",
    },
    {
        "name": "Trending Audio Strategy",
        "description": "Use viral audio to get on FYP, then convert",
        "steps": [
            "Check TikTok trending sounds daily (Explore tab)",
            "Create content using trending audio in first 24h",
            "Ensure content is niche-relevant, not just audio-matching",
            "End video with strong hook to profile (follow for more X)",
        ],
        "conversion_rate": "10-15x normal video reach on TikTok",
        "time_to_implement": "30 min per video",
    },
    {
        "name": "Collab & Duet Strategy",
        "description": "Accelerate growth by reacting to viral content",
        "steps": [
            "Find trending videos in your niche",
            "Duet/stitch with your unique POV or counter-argument",
            "Add value — don't just agree, provide new insight",
            "Tag original creator (may get re-shared)",
        ],
        "conversion_rate": "3-5x baseline reach from borrowed audience",
        "time_to_implement": "20 min per collab",
    },
]


# ---------------------------------------------------------------------------
# Content calendar generator
# ---------------------------------------------------------------------------

CONTENT_TYPES = {
    "hook_listicle":     "Top 5/7/10 list with strong opener",
    "transformation":    "Before/after story arc",
    "controversy":       "Hot take that sparks debate (safe controversy)",
    "tutorial":          "Step-by-step how-to",
    "day_in_life":       "Day-in-the-life vlog for authenticity",
    "reaction":          "Duet/stitch of trending content",
    "trending_audio":    "Sync niche content to viral sound",
    "colllab_callout":   "Call out a myth in your niche",
    "community_engage":  "Poll/question post to drive comments",
    "product_showcase":  "Soft sell of affiliate/product (1 in 7 posts)",
}

WEEKLY_TEMPLATES: dict[str, list[str]] = {
    "3x_week": ["hook_listicle", "tutorial", "transformation"],
    "5x_week": ["hook_listicle", "trending_audio", "tutorial", "reaction", "transformation"],
    "daily":   ["hook_listicle", "tutorial", "trending_audio",
                "reaction", "transformation", "controversy", "community_engage"],
}


def generate_content_calendar(niche: str, frequency: str = "5x_week",
                               weeks: int = 4) -> list[dict]:
    """Generate a N-week content calendar for a theme page."""
    types = WEEKLY_TEMPLATES.get(frequency, WEEKLY_TEMPLATES["5x_week"])
    niche_data = NICHES.get(niche, {})
    pillars = niche_data.get("content_pillars", ["general content"])
    hooks = niche_data.get("hook_templates", ["Strong hook here..."])

    calendar = []
    day = 1
    for week in range(1, weeks + 1):
        for i, ct in enumerate(types):
            pillar = pillars[i % len(pillars)]
            hook = hooks[i % len(hooks)]
            calendar.append({
                "week":          week,
                "day":           day,
                "content_type":  ct,
                "description":   CONTENT_TYPES[ct],
                "content_pillar": pillar,
                "hook_example":  hook,
                "niche":         niche,
            })
            day += 1

    return calendar


# ---------------------------------------------------------------------------
# Theme page launch blueprint
# ---------------------------------------------------------------------------

def launch_blueprint(niche: str) -> dict:
    """Complete step-by-step launch plan for a new theme page."""
    niche_data = NICHES.get(niche)
    if not niche_data:
        return {"error": f"Niche '{niche}' not found. Available: {list(NICHES.keys())}"}

    return {
        "niche":          niche,
        "niche_data":     niche_data,
        "week1_goals":    [
            "Create account with keyword-rich username (@{niche}daily / @best{niche})",
            "Write bio: [Hook] | [Social proof/niche identity] | [CTA + link]",
            "Post 3 pieces of curated content using trending audio",
            "Follow 20 accounts in your niche, engage authentically",
            "Set up link-in-bio with free lead magnet",
        ],
        "week2_goals":    [
            "Post 5x/week minimum — prioritize trending sounds",
            "Comment on 20 viral posts per day in niche",
            "Reach out to 3 similar-sized accounts for shoutout-for-shoutout (S4S)",
            "Launch first DM funnel from a comment CTA post",
            "A/B test two different hook styles",
        ],
        "month1_targets": {
            "followers_min": 500,
            "followers_stretch": 2000,
            "posts": 20,
            "avg_engagement_pct": 5.0,
        },
        "month3_targets": {
            "followers_min": 5_000,
            "followers_stretch": 20_000,
            "posts": 60,
            "first_brand_deal": True,
        },
        "monetization_roadmap": [
            {"milestone": "1K followers", "action": "Start affiliate marketing"},
            {"milestone": "5K followers", "action": "Launch digital product (ebook/template)"},
            {"milestone": "10K followers", "action": "Open brand deal inquiries"},
            {"milestone": "50K followers", "action": "Launch paid community or coaching"},
            {"milestone": "100K followers", "action": "Negotiate exclusive sponsorships"},
        ],
        "viral_formula":   niche_data.get("viral_formula", "value + emotion + CTA"),
        "content_calendar": generate_content_calendar(niche, "5x_week", 2),
        "conversion_strategies": CONVERSION_STRATEGIES[:3],
        "best_platforms": niche_data.get("best_platforms", ["tiktok", "instagram"]),
        "avg_rpm_usd":    niche_data.get("avg_cpm_usd", 10),
    }


def list_niches() -> list[dict]:
    """Return all available niches with summary."""
    return [
        {
            "niche":         k,
            "description":   v["description"],
            "saturation":    v["saturation"],
            "growth_speed":  v["growth_speed"],
            "best_platforms": v["best_platforms"],
            "avg_cpm_usd":   v["avg_cpm_usd"],
        }
        for k, v in NICHES.items()
    ]


def get_hook_templates(niche: str) -> list[str]:
    """Return viral hook templates for a niche."""
    data = NICHES.get(niche, {})
    return data.get("hook_templates", ["Start with a bold claim or question..."])


def analyze_competitor(username: str, platform: str, stats: dict) -> dict:
    """Reverse-engineer a competitor's strategy from their stats."""
    followers  = int(stats.get("followers", 0))
    avg_likes  = int(stats.get("avg_likes", 0))
    post_count = int(stats.get("post_count", 10))
    age_days   = int(stats.get("account_age_days", 30))

    daily_growth = followers / max(1, age_days)
    er = (avg_likes / max(1, followers)) * 100

    insights = []
    if daily_growth > 100:
        insights.append("Growing 100+ followers/day — strong viral content strategy")
    if er > 5:
        insights.append("High ER — community-driven or controversy content style")
    if er < 1:
        insights.append("Low ER despite followers — may be bought or broad/generic content")
    if post_count / max(1, age_days) > 1:
        insights.append("Posting 1+ times daily — volume strategy")

    return {
        "username":       username,
        "platform":       platform,
        "followers":      followers,
        "engagement_rate": round(er, 2),
        "daily_growth":   round(daily_growth, 1),
        "posts_per_day":  round(post_count / max(1, age_days), 2),
        "insights":       insights,
        "replicate":      [
            f"Study their top 10 posts for hook patterns",
            f"Mirror their posting frequency ({round(post_count / max(1, age_days), 1)}x/day)",
            f"Use same hashtag groups but add 5 unique low-competition tags",
        ],
    }
