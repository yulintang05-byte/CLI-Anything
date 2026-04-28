"""Theme page creation, conversion optimization, and monetization guide."""

from typing import Dict, Any, List, Optional
from datetime import datetime


# Proven theme page niches ranked by monetization potential in 2026
NICHE_DATABASE = {
    "finance": {
        "monetization_score": 95,
        "avg_cpm": "$15-40",
        "conversion_rate": "2-5%",
        "audience": "18-35 male skew",
        "content_types": ["tips", "news", "tools", "mistakes-to-avoid"],
        "monetization": ["affiliate (robo-advisors, brokers)", "digital products", "newsletters", "consulting"],
        "top_hashtags": ["#personalfinance", "#investing", "#financialtips", "#stockmarket", "#wealthbuilding"],
        "competitors_to_study": ["@financialtips", "finance-related creators"],
        "conversion_hook": "Free money tips / stock watchlist / budget template",
    },
    "fitness": {
        "monetization_score": 88,
        "avg_cpm": "$8-20",
        "conversion_rate": "1.5-4%",
        "audience": "18-40 mixed",
        "content_types": ["workout-demos", "nutrition", "transformation", "tips"],
        "monetization": ["supplements affiliate", "workout programs", "1-on-1 coaching", "merchandise"],
        "top_hashtags": ["#fitness", "#workout", "#gymtok", "#fitnessmotivation", "#weightloss"],
        "conversion_hook": "Free workout plan / meal prep guide / progress tracker",
    },
    "beauty": {
        "monetization_score": 92,
        "avg_cpm": "$10-25",
        "conversion_rate": "2-6%",
        "audience": "16-35 female skew",
        "content_types": ["tutorials", "reviews", "hauls", "dupes", "routines"],
        "monetization": ["brand deals", "affiliate (Amazon beauty)", "own brand", "digital lookbooks"],
        "top_hashtags": ["#beauty", "#makeup", "#skincare", "#beautytips", "#glowup"],
        "conversion_hook": "Skincare routine / makeup dupe list / brand discount codes",
    },
    "business": {
        "monetization_score": 97,
        "avg_cpm": "$20-60",
        "conversion_rate": "3-7%",
        "audience": "22-45 mixed",
        "content_types": ["case-studies", "tools", "strategies", "income-reports", "mistakes"],
        "monetization": ["courses", "consulting", "SaaS affiliate", "newsletters", "masterminds"],
        "top_hashtags": ["#entrepreneur", "#businesstips", "#sidehustle", "#passiveincome", "#smallbusiness"],
        "conversion_hook": "Free business template / case study / tool list",
    },
    "food": {
        "monetization_score": 80,
        "avg_cpm": "$6-15",
        "conversion_rate": "1-3%",
        "audience": "25-50 mixed",
        "content_types": ["recipes", "reviews", "mukbang", "meal-prep", "hacks"],
        "monetization": ["brand deals", "cookbook", "meal kit affiliate", "ads revenue"],
        "top_hashtags": ["#food", "#recipe", "#foodtok", "#cooking", "#mealprep"],
        "conversion_hook": "Free recipe ebook / meal plan / restaurant guide",
    },
    "tech": {
        "monetization_score": 90,
        "avg_cpm": "$12-35",
        "conversion_rate": "2-5%",
        "audience": "18-35 male skew",
        "content_types": ["reviews", "tutorials", "comparisons", "news", "listicles"],
        "monetization": ["Amazon affiliate", "SaaS affiliate", "YouTube AdSense", "sponsorships"],
        "top_hashtags": ["#tech", "#technology", "#gadgets", "#ai", "#programming"],
        "conversion_hook": "Free tool recommendations / software comparison / discount codes",
    },
    "travel": {
        "monetization_score": 82,
        "avg_cpm": "$8-22",
        "conversion_rate": "1.5-4%",
        "audience": "22-40 mixed",
        "content_types": ["destinations", "tips", "budget-travel", "vlogs", "guides"],
        "monetization": ["hotel/booking affiliate", "travel credit cards", "travel insurance", "guides"],
        "top_hashtags": ["#travel", "#travellife", "#travelgram", "#wanderlust", "#traveltok"],
        "conversion_hook": "Free packing list / destination guide / points hacking guide",
    },
    "relationships": {
        "monetization_score": 85,
        "avg_cpm": "$7-18",
        "conversion_rate": "2-5%",
        "audience": "18-40 mixed",
        "content_types": ["advice", "storytime", "red-flags", "green-flags", "dating-tips"],
        "monetization": ["digital courses", "coaching", "dating app affiliate", "books"],
        "top_hashtags": ["#relationships", "#datingadvice", "#selfimprovement", "#redflags", "#mentalhealth"],
        "conversion_hook": "Free communication scripts / boundary guide / self-assessment quiz",
    },
    "ai_tools": {
        "monetization_score": 99,
        "avg_cpm": "$25-70",
        "conversion_rate": "4-10%",
        "audience": "20-45 mixed",
        "content_types": ["tutorials", "tools-roundup", "prompts", "use-cases", "news"],
        "monetization": ["AI tool affiliate programs", "prompt packs", "courses", "consulting"],
        "top_hashtags": ["#ai", "#artificialintelligence", "#chatgpt", "#aitools", "#automation"],
        "conversion_hook": "Free AI prompt library / tool comparison / automation template",
    },
    "real_estate": {
        "monetization_score": 96,
        "avg_cpm": "$20-55",
        "conversion_rate": "2-6%",
        "audience": "25-50 mixed",
        "content_types": ["tips", "market-updates", "investing", "flipping", "beginner-guides"],
        "monetization": ["lead generation", "affiliate (loans, tools)", "courses", "mentorship"],
        "top_hashtags": ["#realestate", "#realestateinvesting", "#househunting", "#propertyinvesting", "#realtortok"],
        "conversion_hook": "Free market analysis / investment calculator / first-time buyer guide",
    },
}

CONVERSION_FUNNEL_STAGES = [
    {
        "stage": 1,
        "name": "Awareness",
        "goal": "Stop the scroll — earn attention",
        "tactics": [
            "Hook in first 2 seconds (text overlay + verbal)",
            "Thumbnail/cover that creates curiosity gap",
            "Post at peak algorithm times (see optimizer)",
            "Use 3-5 highly relevant hashtags",
        ],
        "metric": "Views / Impressions",
        "benchmark": "1K+ views per post in first 24h",
    },
    {
        "stage": 2,
        "name": "Engagement",
        "goal": "Make them save, share, or comment",
        "tactics": [
            "CTA at 50% mark: 'Save this for later'",
            "Ask a question in the caption",
            "Create controversy or debate-worthy takes",
            "Use cliffhanger mid-video: 'But here's what most people miss...'",
        ],
        "metric": "Save rate + Share rate",
        "benchmark": "5%+ save rate, 1%+ share rate",
    },
    {
        "stage": 3,
        "name": "Profile Visit",
        "goal": "Convert viewer to profile visitor",
        "tactics": [
            "Consistent posting (algorithm channels recurring viewers to profile)",
            "Series content ('Part 1 of 5...')",
            "Mention 'more on my page'",
            "Pinned videos that best represent your value",
        ],
        "metric": "Profile visits per post",
        "benchmark": "5-10% of viewers visit profile",
    },
    {
        "stage": 4,
        "name": "Follow",
        "goal": "Convert visitor to follower",
        "tactics": [
            "Bio clearly states what you post and how often",
            "Pinned video: 'Follow me if you want X every week'",
            "Bio CTA: 'Follow for daily [niche] tips'",
            "Consistent aesthetic/theme on profile grid",
        ],
        "metric": "Follow rate from profile visits",
        "benchmark": "20-40% of profile visitors follow",
    },
    {
        "stage": 5,
        "name": "Trust",
        "goal": "Build parasocial trust for conversion",
        "tactics": [
            "Show face (even occasionally) — trust increases 3x",
            "Share personal story or struggle",
            "Consistent posting — reliability = trust",
            "Engage with comments publicly",
        ],
        "metric": "Comment depth + DM rate",
        "benchmark": "Regular commenters, DMs asking for advice",
    },
    {
        "stage": 6,
        "name": "Conversion",
        "goal": "Turn follower into customer/lead",
        "tactics": [
            "Lead magnet in bio (free guide/template/checklist)",
            "Mention product/offer subtly in 1 of every 5 posts",
            "Limited-time offers create urgency",
            "Social proof: 'X people already got [result] with this'",
        ],
        "metric": "Link-in-bio clicks + email opt-ins + purchases",
        "benchmark": "1-5% conversion rate of engaged followers",
    },
    {
        "stage": 7,
        "name": "Retention",
        "goal": "Keep customers returning + referring",
        "tactics": [
            "Email list for platform-independent reach",
            "Exclusive content for buyers/members",
            "Community (Discord, private group)",
            "Regular value emails/updates",
        ],
        "metric": "Repeat purchase rate + referral rate",
        "benchmark": "30%+ customer return rate",
    },
]

PAGE_ARCHETYPES = {
    "curator": {
        "description": "Aggregates the best content in a niche without creating original content.",
        "effort": "Low",
        "scale_potential": "High",
        "examples": ["Quote pages", "Meme pages", "News aggregators", "Highlight reels"],
        "how_to": [
            "Find 5-10 sources in your niche (Reddit, Twitter, YouTube, industry news)",
            "Curate the best 3-5 pieces daily",
            "Add your commentary/perspective (value-add)",
            "Credit original sources (reduces copyright issues)",
            "Monetize via shoutouts, affiliate links, or driving traffic to owned asset",
        ],
        "monetization": ["shoutouts/promos ($50-500/post at 50K+)", "affiliate links", "newsletter"],
        "time_to_1k": "30-60 days with 2-3 posts/day",
    },
    "educator": {
        "description": "Teaches a specific skill or knowledge set consistently.",
        "effort": "Medium-High",
        "scale_potential": "Very High",
        "examples": ["Finance tips", "Coding tutorials", "Language learning", "DIY skills"],
        "how_to": [
            "Master one sub-niche (e.g. 'Roth IRA for beginners', not 'finance')",
            "Create a 'starter series' — 5-10 foundational posts",
            "Build a free resource as lead magnet",
            "Progress to paid content once trust is established",
        ],
        "monetization": ["courses ($97-997)", "1-on-1 coaching", "affiliate products", "sponsorships"],
        "time_to_1k": "45-90 days with consistent 3-4 posts/week",
    },
    "entertainer": {
        "description": "Builds audience through humor, drama, or personality-driven content.",
        "effort": "High (requires charisma/personality)",
        "scale_potential": "Highest",
        "examples": ["Comedy skits", "Reaction content", "Storytime", "Challenge content"],
        "how_to": [
            "Identify your unique personality angle",
            "Study 3 successful accounts in your format",
            "Post daily for first 30 days to find what resonates",
            "Double down on what gets the best response",
        ],
        "monetization": ["brand deals", "platform funds (TikTok Creator Rewards)", "merch"],
        "time_to_1k": "15-45 days if content resonates quickly",
    },
    "product_reviewer": {
        "description": "Tests and reviews products in a niche — builds affiliate income.",
        "effort": "Medium",
        "scale_potential": "High",
        "examples": ["Tech reviews", "Beauty product reviews", "Kitchen gadgets", "Books"],
        "how_to": [
            "Pick a niche with strong Amazon affiliate payouts",
            "Create honest, detailed reviews (trust = conversion)",
            "Use affiliate links in bio + comments",
            "Build a 'best of' list as sticky/pinned content",
        ],
        "monetization": ["Amazon affiliate (1-10%)", "direct brand deals", "sponsored reviews"],
        "time_to_1k": "45-90 days for product-specific niches",
    },
    "community_builder": {
        "description": "Creates identity-based content that makes followers feel 'part of something'.",
        "effort": "Medium",
        "scale_potential": "High",
        "examples": ["Entrepreneur mindset pages", "Fitness motivation", "Sobriety community", "Parenting"],
        "how_to": [
            "Define the identity your audience has or aspires to",
            "Use 'we' language — build a tribe",
            "Feature UGC (follower transformations/wins)",
            "Create a community hashtag",
        ],
        "monetization": ["paid community (Discord/Circle)", "merchandise", "events", "masterminds"],
        "time_to_1k": "30-60 days with strong emotional resonance",
    },
}


def create_theme_page_plan(
    niche: str,
    archetype: str = "educator",
    platforms: Optional[List[str]] = None,
    monetization_goals: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Generate a complete theme page launch plan with conversion strategy.

    Args:
        niche: content niche (finance, fitness, beauty, business, etc.)
        archetype: page style (curator, educator, entertainer, product_reviewer, community_builder)
        platforms: list of platforms to target
        monetization_goals: list of monetization methods to pursue

    Returns:
        Complete launch plan with 90-day roadmap
    """
    platforms = platforms or ["tiktok", "instagram_reels", "youtube_shorts"]
    niche_lower = niche.lower()
    niche_data = next(
        (v for k, v in NICHE_DATABASE.items() if k in niche_lower or niche_lower in k),
        NICHE_DATABASE["business"],
    )
    arch_data = PAGE_ARCHETYPES.get(archetype.lower(), PAGE_ARCHETYPES["educator"])
    monetization_goals = monetization_goals or niche_data.get("monetization", [])[:2]

    return {
        "created_at": datetime.now().isoformat(),
        "niche": niche,
        "archetype": archetype,
        "platforms": platforms,
        "niche_analysis": {
            "monetization_score": niche_data["monetization_score"],
            "avg_cpm": niche_data["avg_cpm"],
            "conversion_rate": niche_data["conversion_rate"],
            "target_audience": niche_data["audience"],
        },
        "archetype_details": {
            "description": arch_data["description"],
            "effort_level": arch_data["effort"],
            "scale_potential": arch_data["scale_potential"],
            "expected_time_to_1k_followers": arch_data["time_to_1k"],
        },
        "launch_steps": arch_data["how_to"],
        "top_hashtags": niche_data["top_hashtags"],
        "conversion_hook": niche_data["conversion_hook"],
        "monetization_path": monetization_goals,
        "conversion_funnel": CONVERSION_FUNNEL_STAGES,
        "90_day_roadmap": _build_90_day_roadmap(niche, archetype, platforms),
        "account_setup_checklist": _account_setup_checklist(niche, arch_data),
        "content_pillars": _content_pillars(niche, archetype),
    }


def _build_90_day_roadmap(niche: str, archetype: str, platforms: List[str]) -> List[Dict]:
    return [
        {
            "days": "1-7",
            "phase": "Foundation",
            "focus": "Setup + research",
            "tasks": [
                f"Audit top 5 {niche} accounts on each platform",
                "Set up all platform profiles with optimized bio + link in bio",
                f"Create lead magnet (free {niche} resource) for email list",
                "Identify your unique angle/hook that differentiates you",
                "Film first 5 videos (don't publish yet)",
            ],
        },
        {
            "days": "8-30",
            "phase": "Content Testing",
            "focus": "Volume + format experimentation",
            "tasks": [
                "Publish 3-4 videos/week across all platforms",
                "Test 3 different hook styles (curiosity, shock, how-to)",
                "Track which format gets highest completion rate",
                "Reply to every single comment within 1 hour",
                "Start email list with lead magnet CTA",
            ],
        },
        {
            "days": "31-60",
            "phase": "Optimization",
            "focus": "Double down on what works",
            "tasks": [
                "Analyze top 5 performing posts — identify patterns",
                "Create series content (3-5 part series performs best)",
                "Start cross-promoting across platforms",
                "Begin reaching out to micro-brands for first deals (1K+ needed)",
                "Grow email list to 100+ subscribers",
            ],
        },
        {
            "days": "61-90",
            "phase": "Monetization Launch",
            "focus": "Revenue activation",
            "tasks": [
                "Launch first monetization channel (affiliate links/digital product)",
                "Post income report or social proof content",
                "Set up affiliate accounts for top 3 niche-relevant products",
                "Create 'best of' pinned post that showcases value and drives follows",
                "Test paid promotion of top-performing organic post",
            ],
        },
    ]


def _account_setup_checklist(niche: str, arch_data: Dict) -> List[Dict]:
    return [
        {"item": "Username", "status": "todo", "tip": "Use niche keyword in username for SEO (e.g. @financewithX)"},
        {"item": "Profile photo", "status": "todo", "tip": "High contrast, recognizable at small size. Face = trust."},
        {"item": "Bio (line 1)", "status": "todo", "tip": f"What you do: 'Daily {niche} tips'"},
        {"item": "Bio (line 2)", "status": "todo", "tip": f"Who it's for: 'For [target audience]'"},
        {"item": "Bio (line 3)", "status": "todo", "tip": f"CTA: '{arch_data.get('conversion_hook', 'Free guide below')} ↓'"},
        {"item": "Link in bio", "status": "todo", "tip": "Linktree or direct to lead magnet landing page"},
        {"item": "Lead magnet", "status": "todo", "tip": "PDF guide, template, checklist, or email course — deliver via email"},
        {"item": "Email list", "status": "todo", "tip": "Beehiiv, ConvertKit, or Mailchimp — platform-independent audience"},
        {"item": "Content calendar", "status": "todo", "tip": "Plan 2 weeks ahead. Film in batches."},
        {"item": "Analytics setup", "status": "todo", "tip": "Switch to Creator/Business account for analytics on all platforms"},
        {"item": "Pinned posts", "status": "todo", "tip": "Pin your best-performing and most representative content"},
        {"item": "Affiliate accounts", "status": "todo", "tip": "Sign up for relevant affiliate programs before you need them"},
    ]


def _content_pillars(niche: str, archetype: str) -> List[Dict]:
    """
    Return 4 content pillars that balance entertainment, education, and conversion.
    The 70-20-10 rule: 70% value, 20% personality, 10% promotional.
    """
    return [
        {
            "pillar": "Educational (40%)",
            "purpose": "Drive saves and shares — algorithm fuel",
            "examples": [f"How to [do something in {niche}]", f"5 {niche} mistakes beginners make", f"The truth about [myth in {niche}]"],
            "cta": "Save this + follow for more",
        },
        {
            "pillar": "Trending/Timely (30%)",
            "purpose": "Ride viral waves for reach",
            "examples": [f"My take on [trending {niche} news]", f"Reacting to viral {niche} post", f"This {niche} trend everyone's trying"],
            "cta": "Comment your opinion",
        },
        {
            "pillar": "Personal/Story (20%)",
            "purpose": "Build parasocial trust — conversion multiplier",
            "examples": [f"My {niche} journey: what worked and what failed", f"Behind the scenes of my {niche} process", "Honest update on my results"],
            "cta": "DM me if you relate to this",
        },
        {
            "pillar": "Promotional (10%)",
            "purpose": "Monetization — 1 in 10 posts max",
            "examples": [f"The {niche} tool I use every day (link in bio)", f"Free {niche} resource → grab it before it's gone", f"How I help people with {niche} (link in bio)"],
            "cta": "Link in bio",
        },
    ]


def get_niche_list() -> Dict[str, Any]:
    """Return all available niches with key metrics."""
    return {
        "niches": [
            {
                "name": niche,
                "monetization_score": data["monetization_score"],
                "avg_cpm": data["avg_cpm"],
                "conversion_rate": data["conversion_rate"],
                "top_monetization": data["monetization"][0] if data["monetization"] else "",
            }
            for niche, data in sorted(
                NICHE_DATABASE.items(),
                key=lambda x: x[1]["monetization_score"],
                reverse=True,
            )
        ],
        "archetypes": list(PAGE_ARCHETYPES.keys()),
        "tip": "Higher monetization score = easier to generate revenue at smaller audience sizes.",
    }
