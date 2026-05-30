"""Theme page playbook — niches, monetization, content strategy, and conversion funnel."""

from __future__ import annotations
from datetime import datetime, timezone

# ── Niche Database ─────────────────────────────────────────────────────────────

NICHES = {
    "luxury_lifestyle": {
        "name": "Luxury Lifestyle",
        "description": "Supercars, mansions, yachts, watches, travel",
        "difficulty": "easy",
        "monetization_potential": "high",
        "avg_cpm": "$8-20",
        "best_platforms": ["instagram", "tiktok", "youtube"],
        "content_types": ["repost curated content", "motivational quotes over luxury b-roll", "CEO mindset"],
        "target_audience": "18-35 aspirational males",
        "example_accounts": ["TheLuxuryLife", "MillionaireMindset"],
        "growth_speed": "fast",
        "saturated": False,
    },
    "fitness_motivation": {
        "name": "Fitness & Motivation",
        "description": "Workout clips, body transformations, gym motivation",
        "difficulty": "medium",
        "monetization_potential": "very_high",
        "avg_cpm": "$5-12",
        "best_platforms": ["tiktok", "instagram", "youtube"],
        "content_types": ["transformation videos", "workout clips", "nutrition tips", "before/after"],
        "target_audience": "18-35 both genders",
        "example_accounts": ["GymMotivation", "FitInspire"],
        "growth_speed": "medium",
        "saturated": True,
    },
    "finance_investing": {
        "name": "Finance & Investing",
        "description": "Stock tips, crypto, personal finance, wealth building",
        "difficulty": "medium",
        "monetization_potential": "very_high",
        "avg_cpm": "$15-40",
        "best_platforms": ["youtube", "tiktok", "twitter"],
        "content_types": ["market analysis", "investment tips", "financial education", "wealth tips"],
        "target_audience": "22-45 professionals",
        "example_accounts": ["FinanceTok", "InvestingDaily"],
        "growth_speed": "medium",
        "saturated": False,
    },
    "food_recipes": {
        "name": "Food & Recipes",
        "description": "Easy recipes, food hacks, restaurant reviews, mukbang",
        "difficulty": "easy",
        "monetization_potential": "high",
        "avg_cpm": "$4-10",
        "best_platforms": ["tiktok", "youtube", "instagram"],
        "content_types": ["quick recipes", "food hacks", "restaurant tours", "kitchen gadgets"],
        "target_audience": "All ages, 60% female",
        "example_accounts": ["FoodTok", "EasyRecipes"],
        "growth_speed": "fast",
        "saturated": True,
    },
    "celebrity_gossip": {
        "name": "Celebrity & Pop Culture",
        "description": "Celebrity news, drama, entertainment industry",
        "difficulty": "easy",
        "monetization_potential": "medium",
        "avg_cpm": "$2-6",
        "best_platforms": ["tiktok", "instagram", "twitter"],
        "content_types": ["news updates", "drama breakdowns", "rankings", "commentary"],
        "target_audience": "13-30 female skew",
        "example_accounts": ["CelebUpdate", "PopCultureDaily"],
        "growth_speed": "very_fast",
        "saturated": True,
    },
    "travel_adventure": {
        "name": "Travel & Adventure",
        "description": "Travel destinations, travel hacks, hotel reviews, hidden gems",
        "difficulty": "medium",
        "monetization_potential": "high",
        "avg_cpm": "$6-15",
        "best_platforms": ["instagram", "youtube", "tiktok"],
        "content_types": ["destination showcases", "travel hacks", "itineraries", "hotel tours"],
        "target_audience": "25-45 aspirational travelers",
        "example_accounts": ["TravelHacks", "HiddenGems"],
        "growth_speed": "medium",
        "saturated": False,
    },
    "productivity_mindset": {
        "name": "Productivity & Mindset",
        "description": "Study tips, morning routines, discipline, success habits",
        "difficulty": "easy",
        "monetization_potential": "high",
        "avg_cpm": "$8-18",
        "best_platforms": ["tiktok", "youtube", "instagram"],
        "content_types": ["morning routines", "study with me", "book summaries", "habit tips"],
        "target_audience": "16-28 students/young professionals",
        "example_accounts": ["StudyWithMe", "MindsetDaily"],
        "growth_speed": "fast",
        "saturated": False,
    },
    "fashion_streetwear": {
        "name": "Fashion & Streetwear",
        "description": "Outfit ideas, streetwear drops, hauls, styling tips",
        "difficulty": "medium",
        "monetization_potential": "high",
        "avg_cpm": "$5-12",
        "best_platforms": ["instagram", "tiktok", "youtube"],
        "content_types": ["outfit of the day", "haul videos", "sneaker drops", "styling tips"],
        "target_audience": "14-30 fashion-forward",
        "example_accounts": ["StreetStyle", "FashionHaul"],
        "growth_speed": "fast",
        "saturated": True,
    },
    "tech_ai": {
        "name": "Tech & AI",
        "description": "AI tools, tech news, gadget reviews, coding",
        "difficulty": "medium",
        "monetization_potential": "very_high",
        "avg_cpm": "$12-30",
        "best_platforms": ["youtube", "tiktok", "twitter"],
        "content_types": ["AI tool tutorials", "tech news", "gadget reviews", "coding tips"],
        "target_audience": "18-40 tech-savvy",
        "example_accounts": ["AIDaily", "TechNews"],
        "growth_speed": "very_fast",
        "saturated": False,
    },
    "pets_animals": {
        "name": "Pets & Animals",
        "description": "Cute animal content, pet training, funny animals",
        "difficulty": "easy",
        "monetization_potential": "medium",
        "avg_cpm": "$3-7",
        "best_platforms": ["tiktok", "instagram", "youtube"],
        "content_types": ["cute clips", "training tips", "pet hacks", "funny moments"],
        "target_audience": "All ages, broad",
        "example_accounts": ["PetsOfTikTok", "FunnyAnimals"],
        "growth_speed": "very_fast",
        "saturated": True,
    },
}

MONETIZATION_METHODS = {
    "sponsored_posts": {
        "description": "Brands pay you to feature their products",
        "follower_minimum": 5_000,
        "rate_range": "$50 - $50,000+ per post",
        "how_to_get": [
            "Apply to influencer marketplaces (AspireIQ, Creator.co, GRIN)",
            "Reach out cold to brands in your niche via DM/email",
            "Use your media kit — even at 5K followers",
            "Join TikTok Creator Marketplace",
        ],
    },
    "affiliate_marketing": {
        "description": "Earn commission on products you recommend",
        "follower_minimum": 0,
        "rate_range": "5-50% commission per sale",
        "how_to_get": [
            "Amazon Associates (3-10% commission)",
            "LTK / RewardStyle (fashion/beauty focused)",
            "ClickBank (digital products, high commission)",
            "ShareASale / CJ Affiliate (broad merchant network)",
            "Impact.com (premium brand partnerships)",
        ],
    },
    "digital_products": {
        "description": "Sell your own ebooks, courses, presets, templates",
        "follower_minimum": 0,
        "rate_range": "Keep 100% of profit",
        "how_to_get": [
            "Create on Gumroad, Stan.store, or Payhip",
            "Start with a $7-27 entry product",
            "Build up to a flagship $97-497 course",
            "Use Kajabi or Teachable for full course hosting",
        ],
    },
    "creator_funds": {
        "description": "Platform-native monetization programs",
        "follower_minimum": 10_000,
        "rate_range": "$0.002 - $0.05 per view",
        "programs": [
            "TikTok Creativity Program Beta (10K followers, 100K views/30 days)",
            "YouTube Partner Program (1K subs + 4K watch hours)",
            "Instagram Reels Play Bonus (invite only)",
            "Snapchat Spotlight ($1M/day pool)",
        ],
    },
    "merchandise": {
        "description": "Branded merchandise for your community",
        "follower_minimum": 50_000,
        "rate_range": "20-40% profit margin",
        "how_to_get": [
            "Printful + Shopify (print-on-demand, zero upfront cost)",
            "Printify for lower base costs",
            "Spring (formerly Teespring) for creator-first platform",
            "YouTube Merch Shelf (10K+ subscribers)",
        ],
    },
    "subscriptions": {
        "description": "Recurring revenue from your most dedicated fans",
        "follower_minimum": 1_000,
        "rate_range": "$3-50/month per subscriber",
        "how_to_get": [
            "Patreon — best for community + exclusive content",
            "YouTube Channel Memberships",
            "TikTok LIVE Gifts + Subscriptions",
            "Instagram Subscriptions",
            "Substack for newsletter monetization",
        ],
    },
}

CONTENT_REPURPOSING = {
    "workflow": [
        "Create ONE long-form YouTube video (10-20 min)",
        "Cut 3-5 YouTube Shorts from it",
        "Post best clip as TikTok",
        "Share top quote/moment on Instagram Reels",
        "Thread key insights on Twitter/X",
        "Turn key points into Instagram carousel",
        "Write a newsletter summarizing the topic",
    ],
    "tools": [
        "CapCut — auto-captions + mobile editing (free)",
        "Opus Clip — AI-powered clip extraction from long-form",
        "Canva — graphics, carousels, thumbnails",
        "Buffer / Later — schedule across platforms",
        "Metricool — analytics across all platforms",
    ],
}

THEME_PAGE_LAUNCH_CHECKLIST = [
    "Pick ONE niche with clear monetization path",
    "Research top 50 accounts in that niche",
    "Create accounts on TikTok, Instagram, YouTube Shorts",
    "Set up consistent branding (logo, colors, bio) across all",
    "Install CapCut on phone",
    "Source content legally (videos from creators who allow reposting, CC-licensed, or original)",
    "Post 3x/day for 30 days minimum",
    "Engage with 20 relevant accounts daily",
    "Track metrics weekly — double down on what works",
    "At 10K followers: sign up for affiliate programs",
    "At 50K followers: create a media kit and pitch brands",
    "At 100K followers: launch a digital product",
]

LEGAL_CONTENT_SOURCES = [
    {"source": "Pexels", "url": "pexels.com", "type": "Stock video", "license": "Free commercial use"},
    {"source": "Pixabay", "url": "pixabay.com", "type": "Stock video/images", "license": "Free commercial use"},
    {"source": "Coverr", "url": "coverr.co", "type": "Stock video", "license": "Free commercial use"},
    {"source": "Mixkit", "url": "mixkit.co", "type": "Stock video + music", "license": "Free commercial use"},
    {"source": "YouTube CC", "url": "youtube.com/results?sp=EgIgAQ==", "type": "Creative Commons video", "license": "CC BY 4.0"},
    {"source": "Uppbeat", "url": "uppbeat.io", "type": "Royalty-free music", "license": "Free for creators"},
    {"source": "Bensound", "url": "bensound.com", "type": "Royalty-free music", "license": "Free with attribution"},
    {"source": "Canva", "url": "canva.com", "type": "Graphics/templates", "license": "Commercial with account"},
]


def list_niches(
    sort_by: str = "monetization_potential",
    filter_difficulty: str | None = None,
    filter_platform: str | None = None,
) -> list[dict]:
    """
    List all theme page niches with ratings.

    Args:
        sort_by: 'monetization_potential', 'growth_speed', 'difficulty', 'name'
        filter_difficulty: 'easy', 'medium', 'hard'
        filter_platform: 'tiktok', 'youtube', 'instagram'

    Returns:
        list of niche dicts sorted by specified metric
    """
    results = []
    for key, niche in NICHES.items():
        if filter_difficulty and niche.get("difficulty") != filter_difficulty:
            continue
        if filter_platform and filter_platform not in niche.get("best_platforms", []):
            continue
        results.append({"id": key, **niche})

    order = {"easy": 0, "medium": 1, "hard": 2}
    pot_order = {"medium": 0, "high": 1, "very_high": 2}
    speed_order = {"slow": 0, "medium": 1, "fast": 2, "very_fast": 3}

    if sort_by == "monetization_potential":
        results.sort(key=lambda x: pot_order.get(x.get("monetization_potential", ""), 0), reverse=True)
    elif sort_by == "growth_speed":
        results.sort(key=lambda x: speed_order.get(x.get("growth_speed", ""), 0), reverse=True)
    elif sort_by == "difficulty":
        results.sort(key=lambda x: order.get(x.get("difficulty", ""), 99))
    else:
        results.sort(key=lambda x: x.get("name", ""))

    return results


def get_niche_detail(niche_id: str) -> dict:
    """Get full details for a specific niche."""
    if niche_id not in NICHES:
        raise ValueError(f"Unknown niche '{niche_id}'. Run 'theme-page niches' to see options.")
    return {"id": niche_id, **NICHES[niche_id]}


def get_launch_checklist() -> list[dict]:
    """Return the theme page launch checklist with status tracking."""
    return [{"step": i + 1, "action": item, "done": False} for i, item in enumerate(THEME_PAGE_LAUNCH_CHECKLIST)]


def get_monetization_guide(method: str | None = None) -> dict:
    """Get monetization strategy guide."""
    if method:
        if method not in MONETIZATION_METHODS:
            raise ValueError(f"Unknown method '{method}'. Options: {list(MONETIZATION_METHODS.keys())}")
        return {method: MONETIZATION_METHODS[method]}
    return MONETIZATION_METHODS


def get_content_repurposing_guide() -> dict:
    """Get the content repurposing workflow and tools."""
    return CONTENT_REPURPOSING


def get_legal_sources() -> list[dict]:
    """Get list of legal content sources for theme pages."""
    return LEGAL_CONTENT_SOURCES


def generate_content_plan(
    niche_id: str,
    platforms: list[str] | None = None,
    weeks: int = 4,
) -> dict:
    """
    Generate a content calendar for a theme page.

    Args:
        niche_id: niche identifier from list_niches()
        platforms: list of platforms to create content for
        weeks: number of weeks to plan

    Returns:
        dict with weekly content plan and content ideas
    """
    if niche_id not in NICHES:
        raise ValueError(f"Unknown niche '{niche_id}'.")

    niche = NICHES[niche_id]
    if not platforms:
        platforms = niche["best_platforms"][:2]

    content_types = niche["content_types"]
    plan = []

    for week in range(1, weeks + 1):
        week_content = []
        for i, ct in enumerate(content_types * 2):
            if len(week_content) >= 5:
                break
            week_content.append({
                "day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"][i % 5],
                "content_type": ct,
                "platforms": platforms,
                "format": _content_format_for_type(ct, platforms),
                "tip": _tip_for_content_type(ct),
            })
        plan.append({"week": week, "posts": week_content})

    return {
        "niche": niche["name"],
        "platforms": platforms,
        "weeks": weeks,
        "weekly_plan": plan,
        "content_sources": [s["source"] for s in LEGAL_CONTENT_SOURCES[:4]],
        "general_strategy": (
            f"Theme pages in '{niche['name']}' grow best by consistently posting "
            f"{niche['content_types'][0]} content. "
            f"Target: {niche['target_audience']}."
        ),
    }


def _content_format_for_type(content_type: str, platforms: list[str]) -> str:
    formats = {
        "repost curated content": "15-60s vertical video",
        "motivational quotes": "Text overlay on b-roll",
        "transformation videos": "Before/after split screen",
        "workout clips": "9:16 vertical, 15-30s",
        "quick recipes": "POV cooking, 15-60s",
        "market analysis": "Screen recording + voiceover",
        "outfit of the day": "Mirror selfie or outfit flat-lay",
        "morning routines": "Day-in-my-life style vlog",
        "news updates": "Text recap + trending audio",
    }
    for key, fmt in formats.items():
        if key in content_type.lower():
            return fmt
    return "9:16 vertical video"


def _tip_for_content_type(content_type: str) -> str:
    tips = {
        "repost": "Always credit original creator in caption",
        "motivational": "Use dramatic music + cinematic b-roll for emotion",
        "transformation": "Show contrast clearly — viewers scroll for the payoff",
        "workout": "Sync transitions to music beat drops",
        "recipes": "Show finished dish in first 2 seconds as hook",
        "market": "Be confident and contrarian — that's what goes viral",
        "outfit": "Good lighting is non-negotiable for fashion content",
        "morning": "Film in real-time — authenticity beats production quality",
        "news": "Speed matters — be first, then be thorough",
    }
    for key, tip in tips.items():
        if key in content_type.lower():
            return tip
    return "Hook viewers in the first 1-3 seconds"
