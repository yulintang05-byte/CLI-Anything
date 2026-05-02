"""Theme page strategy engine — niche playbooks, content calendars, and monetization."""

from typing import Any
from datetime import date, timedelta

# Profitable niche database with key metrics (May 2026)
_NICHES: dict[str, dict[str, Any]] = {
    "motivation": {
        "name": "Motivation / Mindset",
        "difficulty": "low",
        "saturation": "high",
        "avg_rpm": "$2-4",
        "monetization": ["affiliate", "digital_products", "sponsorships"],
        "content_types": ["quote graphics", "voiceover clips", "transformation stories", "book summaries"],
        "target_audience": "18-35, goal-oriented, self-improvement seekers",
        "top_platforms": ["instagram", "tiktok", "youtube"],
        "brand_voice": "Inspirational, direct, aspirational",
        "conversion_hook": "Free eBook or mini-course in bio — motivation audience converts well",
        "monthly_potential": "$500-$5,000 per page (beginner to advanced)",
        "growth_speed": "fast",
        "best_post_formats": ["quote overlay video", "60-sec book summary", "POV storytime"],
    },
    "finance": {
        "name": "Personal Finance / Wealth",
        "difficulty": "medium",
        "saturation": "medium",
        "avg_rpm": "$8-15",
        "monetization": ["affiliate", "digital_products", "youtube_ads", "sponsorships"],
        "content_types": ["money tips", "investing breakdowns", "income reveal", "budget walkthroughs"],
        "target_audience": "22-45, income earners, want financial independence",
        "top_platforms": ["youtube", "tiktok", "instagram"],
        "brand_voice": "Authoritative, clear, actionable, trust-building",
        "conversion_hook": "Free budget template or compound interest calculator — high intent audience",
        "monthly_potential": "$2,000-$20,000 per page",
        "growth_speed": "medium",
        "best_post_formats": ["listicle Shorts", "screen-record walkthrough", "reaction to financial news"],
    },
    "fitness": {
        "name": "Fitness / Body Transformation",
        "difficulty": "medium",
        "saturation": "high",
        "avg_rpm": "$3-7",
        "monetization": ["affiliate", "digital_products", "sponsorships", "subscriptions"],
        "content_types": ["workout clips", "transformation before/after", "diet tips", "supplement reviews"],
        "target_audience": "18-40, gym-goers and home workout enthusiasts",
        "top_platforms": ["tiktok", "instagram", "youtube"],
        "brand_voice": "Energetic, motivating, knowledgeable",
        "conversion_hook": "Free workout plan PDF — captures email for backend funnel",
        "monthly_potential": "$1,000-$15,000 per page",
        "growth_speed": "fast",
        "best_post_formats": ["workout demo", "transformation reveal", "food prep ASMR"],
    },
    "ai_tools": {
        "name": "AI Tools / Automation",
        "difficulty": "low-medium",
        "saturation": "low",
        "avg_rpm": "$10-20",
        "monetization": ["affiliate", "digital_products", "youtube_ads", "sponsored"],
        "content_types": ["AI tool demos", "side hustle reveals", "automation tutorials", "prompt engineering"],
        "target_audience": "20-40, tech-curious, entrepreneurs, creators",
        "top_platforms": ["youtube", "tiktok", "instagram"],
        "brand_voice": "Forward-thinking, practical, slightly futuristic",
        "conversion_hook": "Free AI prompts pack or 'make money with AI' guide — extremely high conversion",
        "monthly_potential": "$3,000-$30,000 per page",
        "growth_speed": "very fast",
        "best_post_formats": ["screen-capture demo", 'before/after "I used AI to..." reveal', "tool comparison"],
    },
    "luxury_aesthetic": {
        "name": "Quiet Luxury / Aesthetic Lifestyle",
        "difficulty": "low",
        "saturation": "medium",
        "avg_rpm": "$4-8",
        "monetization": ["affiliate", "brand_deals", "tiktok_shop"],
        "content_types": ["outfit showcases", "home tours", "travel clips", "morning routines"],
        "target_audience": "18-35, aspirational lifestyle seekers, fashion-forward",
        "top_platforms": ["instagram", "tiktok", "pinterest"],
        "brand_voice": "Elegant, minimal, aspirational but accessible",
        "conversion_hook": "Amazon storefront or LTK affiliate links — fashion audience shops impulsively",
        "monthly_potential": "$500-$8,000 per page",
        "growth_speed": "fast",
        "best_post_formats": ["OOTD Reel", "get ready with me", "room tour"],
    },
    "crypto_web3": {
        "name": "Crypto / Web3 / DeFi",
        "difficulty": "high",
        "saturation": "medium",
        "avg_rpm": "$15-30",
        "monetization": ["affiliate", "sponsored", "youtube_ads", "digital_products"],
        "content_types": ["market analysis", "coin breakdowns", "NFT news", "DeFi tutorials"],
        "target_audience": "21-40, investors, tech-native, risk-tolerant",
        "top_platforms": ["youtube", "twitter/x", "tiktok"],
        "brand_voice": "Analytical, confident, data-driven",
        "conversion_hook": "Free crypto portfolio tracker or 'top 5 altcoins' report — very high CTR",
        "monthly_potential": "$5,000-$50,000 per page",
        "growth_speed": "medium",
        "best_post_formats": ["chart analysis Short", "coin spotlight", "market news recap"],
    },
    "gaming": {
        "name": "Gaming / Esports",
        "difficulty": "medium",
        "saturation": "high",
        "avg_rpm": "$2-5",
        "monetization": ["youtube_ads", "sponsorships", "affiliates", "subscriptions"],
        "content_types": ["gameplay clips", "fail compilations", "gaming news", "reviews"],
        "target_audience": "13-30, gamers across all platforms",
        "top_platforms": ["youtube", "tiktok", "twitch"],
        "brand_voice": "Energetic, community-focused, authentic gamer personality",
        "conversion_hook": "Discord server + affiliate gaming gear links",
        "monthly_potential": "$500-$10,000 per page",
        "growth_speed": "fast",
        "best_post_formats": ["highlight clip", "funny fail compilation", "game review Short"],
    },
    "food": {
        "name": "Food / Recipes / Cooking",
        "difficulty": "low",
        "saturation": "high",
        "avg_rpm": "$3-6",
        "monetization": ["affiliate", "brand_deals", "digital_products", "youtube_ads"],
        "content_types": ["recipe videos", "ASMR cooking", "restaurant reviews", "food hacks"],
        "target_audience": "18-50, home cooks, foodies, meal preppers",
        "top_platforms": ["tiktok", "instagram", "youtube"],
        "brand_voice": "Warm, instructional, sensory-rich",
        "conversion_hook": "Free recipe eBook or meal plan — converts to email list very well",
        "monthly_potential": "$500-$7,000 per page",
        "growth_speed": "fast",
        "best_post_formats": ["30-sec recipe Short", "ASMR cooking ASMR", "viral trend recipe recreation"],
    },
    "self_improvement": {
        "name": "Self-Improvement / Productivity",
        "difficulty": "medium",
        "saturation": "medium",
        "avg_rpm": "$5-10",
        "monetization": ["digital_products", "affiliate", "youtube_ads", "subscriptions"],
        "content_types": ["habit tracking", "book reviews", "productivity systems", "morning routines"],
        "target_audience": "20-40, ambitious, type-A personalities, students",
        "top_platforms": ["youtube", "tiktok", "instagram"],
        "brand_voice": "Smart, clear, systems-focused, relatable",
        "conversion_hook": "Notion template or habit tracker — productivity audience loves tools",
        "monthly_potential": "$1,500-$15,000 per page",
        "growth_speed": "medium-fast",
        "best_post_formats": ["day-in-my-life", "book summary", "habit system breakdown"],
    },
}

# Monetization strategy details
_MONETIZATION_METHODS: dict[str, dict[str, Any]] = {
    "affiliate": {
        "name": "Affiliate Marketing",
        "setup_time": "1-2 days",
        "earning_potential": "$100-$10,000+/month",
        "platforms": ["Amazon Associates", "ShareASale", "Impact", "ClickBank", "TikTok Shop"],
        "requirements": "Link in bio or swipe-up; no follower minimum",
        "best_for": ["fashion", "tech", "fitness", "food", "home"],
        "action_steps": [
            "Sign up for Amazon Associates or TikTok Shop affiliate program",
            "Create a Linktree or Stan.store page with affiliate links",
            "Add link to every bio immediately",
            "Make 2-3 'product recommendation' posts per week naturally woven into content",
            "Track which products convert best in affiliate dashboard",
        ],
    },
    "digital_products": {
        "name": "Digital Products",
        "setup_time": "3-7 days",
        "earning_potential": "$500-$50,000+/month",
        "platforms": ["Gumroad", "Stan.store", "Payhip", "Teachable", "Podia"],
        "requirements": "Audience trust (usually 1K+ engaged followers)",
        "best_for": ["finance", "self_improvement", "fitness", "ai_tools", "motivation"],
        "action_steps": [
            "Identify #1 question your audience asks repeatedly",
            "Create PDF guide, Notion template, or mini-course answering it",
            "Price between $9-$49 (impulse purchase range)",
            "Add to Stan.store or Gumroad (Stan.store integrates with IG/TikTok bio)",
            "Create dedicated 'product demo' Reel/TikTok showing transformation from using it",
        ],
    },
    "brand_deals": {
        "name": "Brand Deals / Sponsorships",
        "setup_time": "2-4 weeks to first deal",
        "earning_potential": "$200-$20,000+/post",
        "platforms": ["Direct DM outreach", "AspireIQ", "Creator.co", "Whop"],
        "requirements": "Usually 5K-10K+ followers in a targeted niche",
        "best_for": ["fitness", "beauty", "tech", "gaming", "luxury_aesthetic"],
        "action_steps": [
            "Build a media kit (follower count, engagement rate, audience demographics, niche)",
            "List on creator marketplaces (AspireIQ, Creator.co, Whop)",
            "Cold DM 5 brands in your niche per week with specific pitch",
            "Start with free product deals to build portfolio",
            "Charge CPM-based rate: (followers ÷ 1000) × $15-30 for TikTok/IG",
        ],
    },
    "youtube_ads": {
        "name": "YouTube Ad Revenue (YPP)",
        "setup_time": "Time to reach 1K subs + 4K hours watch time",
        "earning_potential": "$1-$10+ per 1000 views (varies by niche)",
        "platforms": ["YouTube Partner Program"],
        "requirements": "1,000 subscribers + 4,000 watch hours OR 10M Shorts views in 90 days",
        "best_for": ["finance", "tech", "crypto_web3", "education", "gaming"],
        "action_steps": [
            "Apply for YPP once thresholds are met",
            "Focus on finance/tech niches for highest RPM ($8-$20 vs $2-$4 for entertainment)",
            "Longer videos (8+ min) allow mid-roll ads = 2-3× revenue",
            "Use chapters to improve retention and ad placement",
            "Combine with affiliate links in description for 2× income per video",
        ],
    },
    "tiktok_shop": {
        "name": "TikTok Shop Affiliate",
        "setup_time": "1-3 days",
        "earning_potential": "$200-$20,000+/month",
        "platforms": ["TikTok Shop"],
        "requirements": "1,000+ followers (TikTok Shop affiliate threshold)",
        "best_for": ["fashion", "beauty", "food", "fitness", "tech_gadgets"],
        "action_steps": [
            "Apply for TikTok Shop affiliate program (need 1K followers)",
            "Browse 'Find Products' in TikTok Shop dashboard for top sellers in your niche",
            "Add product links directly to your videos (tap-to-buy overlay)",
            "Create 'unboxing' and 'review' content formats — highest TikTok Shop CVR",
            "Track conversion rate per product and drop anything under 1%",
        ],
    },
}


def create_theme_page(niche: str) -> dict[str, Any]:
    """Generate a complete theme page blueprint for a niche."""
    if niche not in _NICHES:
        available = ", ".join(_NICHES.keys())
        raise ValueError(f"Unknown niche '{niche}'. Available: {available}")

    n = _NICHES[niche]
    mon_methods = [_MONETIZATION_METHODS[m] for m in n["monetization"] if m in _MONETIZATION_METHODS]

    return {
        "niche": niche,
        "name": n["name"],
        "difficulty": n["difficulty"],
        "saturation": n["saturation"],
        "avg_rpm": n["avg_rpm"],
        "monthly_potential": n["monthly_potential"],
        "growth_speed": n["growth_speed"],
        "brand_voice": n["brand_voice"],
        "target_audience": n["target_audience"],
        "top_platforms": n["top_platforms"],
        "content_types": n["content_types"],
        "best_post_formats": n["best_post_formats"],
        "conversion_hook": n["conversion_hook"],
        "monetization_stack": [m["name"] for m in mon_methods],
        "first_30_days": [
            f"Day 1-3: Set up accounts on {', '.join(n['top_platforms'][:2])} — complete profile 100%",
            "Day 4-7: Publish 5 pieces of content in your niche format to test what resonates",
            "Day 8-14: Double-down on format that got most engagement; post 1-2x/day",
            f"Day 15-21: Add affiliate link to bio ({n['monetization'][0]} program)",
            "Day 22-30: Analyze analytics, cut 2 worst-performing formats, scale the best",
        ],
        "setup_action_plan": [
            f"1. Research top 10 accounts in {n['name']} niche — save best-performing videos",
            "2. Create account with niche-specific name + branded logo (use Canva)",
            "3. Write bio with: who you help + how + CTA + link",
            "4. Create 10 content pieces before posting (content bank)",
            f"5. Sign up for {n['monetization'][0]} program immediately",
            "6. Set posting schedule (consistency beats volume at start)",
        ],
    }


def list_niches() -> list[dict[str, Any]]:
    """List all available niches with key metrics."""
    return [
        {
            "niche": k,
            "name": v["name"],
            "difficulty": v["difficulty"],
            "growth_speed": v["growth_speed"],
            "monthly_potential": v["monthly_potential"],
            "saturation": v["saturation"],
        }
        for k, v in _NICHES.items()
    ]


def monetize(niche: str) -> dict[str, Any]:
    """Return detailed monetization strategy for a niche."""
    if niche not in _NICHES:
        raise ValueError(f"Unknown niche '{niche}'. Run 'theme-page niches' to see options.")

    n = _NICHES[niche]
    methods = [
        {**_MONETIZATION_METHODS[m], "method_id": m}
        for m in n["monetization"]
        if m in _MONETIZATION_METHODS
    ]

    return {
        "niche": niche,
        "name": n["name"],
        "primary_method": methods[0] if methods else None,
        "all_methods": methods,
        "monthly_potential": n["monthly_potential"],
        "stack_summary": " → ".join(m["name"] for m in methods),
        "diversification_note": "Creators with 3+ monetization streams earn 3.2× more than single-stream creators",
    }


def content_calendar(niche: str, days: int = 30) -> list[dict[str, Any]]:
    """Generate a content calendar for a theme page niche."""
    if niche not in _NICHES:
        raise ValueError(f"Unknown niche '{niche}'.")

    n = _NICHES[niche]
    formats = n["best_post_formats"]
    content_types = n["content_types"]

    start = date.today()
    calendar = []

    format_cycle = formats * (days // len(formats) + 2)
    type_cycle = content_types * (days // len(content_types) + 2)

    for i in range(days):
        post_date = start + timedelta(days=i)
        weekday = post_date.strftime("%A")
        is_peak = weekday in ["Tuesday", "Thursday", "Friday", "Saturday"]

        calendar.append({
            "day": i + 1,
            "date": post_date.isoformat(),
            "weekday": weekday,
            "is_peak_day": is_peak,
            "format": format_cycle[i % len(format_cycle)],
            "content_type": type_cycle[i % len(type_cycle)],
            "hook_idea": f"Hook: '{_hook_idea(niche, i)}'",
            "cta": _cta_for_day(i),
            "hashtag_note": "Use 'hashtags suggest' command for optimized tag set",
        })

    return calendar


def _hook_idea(niche: str, index: int) -> str:
    hooks: dict[str, list[str]] = {
        "motivation": [
            "Nobody tells you this about success...",
            "I wasted 3 years until I learned this one thing",
            "The mindset shift that changed everything for me",
            "Stop doing this if you want to be successful",
        ],
        "finance": [
            "How I made $X with zero experience",
            "The money mistake 90% of people make at 25",
            "This one investing habit will change your life",
            "Why your bank doesn't want you to know this",
        ],
        "fitness": [
            "The workout nobody tells beginners",
            "I lost X lbs doing just this one thing",
            "Stop doing this exercise — here's what actually works",
            "3-minute morning routine that actually works",
        ],
        "ai_tools": [
            "This AI tool made me $X in 24 hours",
            "Stop doing [task] manually — AI does it in 10 seconds",
            "I replaced my entire workflow with AI — here's how",
            "The AI tool nobody in [niche] knows about yet",
        ],
        "food": [
            "This 5-minute recipe went viral for a reason",
            "I made this every day for a week and...",
            "The one kitchen hack that saves me 2 hours",
            "Warning: this recipe is dangerously good",
        ],
    }
    default = [
        "Nobody talks about this...",
        "I wish I knew this sooner",
        "This changed everything for me",
        "Stop making this mistake",
    ]
    pool = hooks.get(niche, default)
    return pool[index % len(pool)]


def _cta_for_day(index: int) -> str:
    ctas = [
        "Follow for more [niche] tips",
        "Comment 'YES' if this helped",
        "Save this for later",
        "Tag someone who needs this",
        "Check link in bio for the full guide",
        "Drop your questions below",
        "Share with someone starting out",
    ]
    return ctas[index % len(ctas)]


def compare_niches(niches: list[str]) -> list[dict[str, Any]]:
    """Compare multiple niches side by side."""
    result = []
    for n in niches:
        if n not in _NICHES:
            raise ValueError(f"Unknown niche '{n}'.")
        d = _NICHES[n]
        result.append({
            "niche": n,
            "name": d["name"],
            "difficulty": d["difficulty"],
            "saturation": d["saturation"],
            "monthly_potential": d["monthly_potential"],
            "growth_speed": d["growth_speed"],
            "avg_rpm": d["avg_rpm"],
            "top_platforms": d["top_platforms"],
        })
    return result
