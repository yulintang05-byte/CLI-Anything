"""Theme Page Playbook — Niche selection, monetization strategy, and conversion systems."""

from typing import Optional


_NICHES: dict[str, dict] = {
    "luxury_lifestyle": {
        "description": "Luxury cars, watches, mansions, and aspirational content",
        "difficulty": "medium",
        "monetization": ["brand_deals", "digital_products", "affiliate"],
        "avg_cpm": 8.50,
        "follower_to_revenue_ratio": 0.008,
        "top_hashtags": ["#luxury", "#rich", "#lifestyle", "#wealthy", "#flexing"],
        "content_sources": ["Pinterest", "Instagram Reels", "YouTube compilations"],
        "posting_frequency": "3x/day",
        "growth_speed": "fast",
        "notes": "High engagement, easily scalable. Source content ethically. Focus on aspirational storytelling.",
    },
    "motivation_mindset": {
        "description": "Motivational quotes, success stories, and mindset content",
        "difficulty": "low",
        "monetization": ["digital_products", "courses", "affiliate", "brand_deals"],
        "avg_cpm": 5.00,
        "follower_to_revenue_ratio": 0.006,
        "top_hashtags": ["#motivation", "#mindset", "#success", "#hustle", "#entrepreneur"],
        "content_sources": ["YouTube speeches", "Podcasts", "Books", "Twitter/X threads"],
        "posting_frequency": "2-4x/day",
        "growth_speed": "fast",
        "notes": "Saturated but still effective. Differentiate with a specific sub-niche (e.g., female entrepreneurs).",
    },
    "fitness_health": {
        "description": "Workout clips, diet tips, body transformations",
        "difficulty": "medium",
        "monetization": ["fitness_programs", "affiliate", "brand_deals", "membership"],
        "avg_cpm": 6.00,
        "follower_to_revenue_ratio": 0.01,
        "top_hashtags": ["#fitness", "#workout", "#gym", "#health", "#transformation"],
        "content_sources": ["Workout clips (with permission)", "Original content", "Stock footage"],
        "posting_frequency": "1-2x/day",
        "growth_speed": "medium",
        "notes": "Strong buyer intent. Great for supplement and course affiliates. Need disclaimer for medical claims.",
    },
    "finance_investing": {
        "description": "Stock tips, crypto, budgeting hacks, passive income",
        "difficulty": "high",
        "monetization": ["affiliate", "courses", "newsletter", "sponsored"],
        "avg_cpm": 15.00,
        "follower_to_revenue_ratio": 0.02,
        "top_hashtags": ["#investing", "#stocks", "#crypto", "#passiveincome", "#finance"],
        "content_sources": ["News articles", "SEC filings", "Analyst reports"],
        "posting_frequency": "1-2x/day",
        "growth_speed": "slow",
        "notes": "Highest CPM niche. Requires disclaimers. Regulated content — avoid definitive buy/sell advice.",
    },
    "animals_pets": {
        "description": "Cute and funny animal compilations",
        "difficulty": "low",
        "monetization": ["brand_deals", "merch", "pet_affiliate"],
        "avg_cpm": 3.00,
        "follower_to_revenue_ratio": 0.003,
        "top_hashtags": ["#pets", "#animals", "#cute", "#dog", "#cat"],
        "content_sources": ["Reddit", "Twitter/X", "Submitted clips", "Original filming"],
        "posting_frequency": "3-5x/day",
        "growth_speed": "very_fast",
        "notes": "Easiest to grow but lowest monetization. Great as a starter page. Scale to 1M before monetizing.",
    },
    "cooking_food": {
        "description": "Recipes, restaurant reviews, food hacks",
        "difficulty": "medium",
        "monetization": ["brand_deals", "cookbook", "affiliate", "courses"],
        "avg_cpm": 5.50,
        "follower_to_revenue_ratio": 0.007,
        "top_hashtags": ["#food", "#recipe", "#cooking", "#foodtok", "#chef"],
        "content_sources": ["Original recipes", "Restaurant clips", "YouTube shorts repurpose"],
        "posting_frequency": "2-3x/day",
        "growth_speed": "medium",
        "notes": "High engagement, easy to get brand deals (food brands love micro-influencers).",
    },
    "beauty_skincare": {
        "description": "Makeup tutorials, skincare routines, product reviews",
        "difficulty": "medium",
        "monetization": ["affiliate", "brand_deals", "own_product_line"],
        "avg_cpm": 7.00,
        "follower_to_revenue_ratio": 0.012,
        "top_hashtags": ["#beauty", "#makeup", "#skincare", "#grwm", "#tutorial"],
        "content_sources": ["Original tutorials", "Product reviews", "Before/after"],
        "posting_frequency": "1-2x/day",
        "growth_speed": "medium",
        "notes": "Highest affiliate conversion rate of any niche. Amazon affiliate + LTK work extremely well.",
    },
    "entertainment_memes": {
        "description": "Viral memes, pop culture, trending moments",
        "difficulty": "low",
        "monetization": ["brand_deals", "merch", "shoutouts"],
        "avg_cpm": 2.50,
        "follower_to_revenue_ratio": 0.002,
        "top_hashtags": ["#meme", "#funny", "#viral", "#trending", "#comedy"],
        "content_sources": ["Reddit", "Twitter/X", "YouTube", "9GAG"],
        "posting_frequency": "5-10x/day",
        "growth_speed": "very_fast",
        "notes": "Easy to grow fast but hard to monetize. Best strategy: grow to 500K then sell the page.",
    },
}

_MONETIZATION_METHODS: dict[str, dict] = {
    "brand_deals": {
        "description": "Paid partnerships with brands",
        "when": "10K+ followers",
        "avg_rate_per_post": {"tiktok": "$100-500 per 100K followers", "instagram": "$100-1000 per 100K followers"},
        "how_to_get": ["Create media kit", "DM brands in your niche", "Use Creator Marketplace", "Join influencer platforms"],
        "platforms": ["AspireIQ", "Creator.co", "TikTok Creator Marketplace", "Instagram Branded Content"],
    },
    "digital_products": {
        "description": "Sell e-books, presets, templates, guides",
        "when": "1K+ highly engaged followers",
        "avg_rate_per_post": {"all": "$20-197 per product sale"},
        "how_to_get": ["Create on Gumroad/Stan Store", "Add link to bio", "Create a lead magnet funnel"],
        "platforms": ["Gumroad", "Stan Store", "Beacons", "Payhip"],
    },
    "affiliate": {
        "description": "Earn commission promoting others' products",
        "when": "Any size — start day 1",
        "avg_rate_per_post": {"all": "5-30% commission per sale"},
        "how_to_get": ["Join Amazon Associates", "Apply to niche affiliate programs", "Use ShareASale/CJ"],
        "platforms": ["Amazon Associates", "ShareASale", "Impact", "LTK", "ClickBank"],
    },
    "courses": {
        "description": "Teach your skill/knowledge at scale",
        "when": "Authority established (5K+ engaged followers)",
        "avg_rate_per_post": {"all": "$97-997+ per enrollment"},
        "how_to_get": ["Build with Teachable/Kajabi", "Create free lead magnet first", "Email list essential"],
        "platforms": ["Teachable", "Kajabi", "Thinkific", "Skool"],
    },
    "merch": {
        "description": "Branded merchandise (print-on-demand or custom)",
        "when": "50K+ brand recognition",
        "avg_rate_per_post": {"all": "$8-25 profit per item"},
        "how_to_get": ["Start with Printful/Printify (no upfront cost)", "Design 3-5 hero items", "Promote with limited drops"],
        "platforms": ["Printful", "Printify", "Shopify", "Spring (Teespring)"],
    },
}


def niche_overview(niche: Optional[str] = None) -> list[dict] | dict:
    if niche:
        n = _NICHES.get(niche.lower().replace(" ", "_"))
        if not n:
            available = list(_NICHES.keys())
            return {"error": f"Unknown niche '{niche}'. Available: {available}"}
        return {"niche": niche, **n}
    return [{"niche": k, **v} for k, v in _NICHES.items()]


def theme_page_roadmap(niche: str, current_followers: int = 0) -> dict:
    """Return a milestone-based roadmap for growing a theme page."""
    n = _NICHES.get(niche.lower().replace(" ", "_"), _NICHES["motivation_mindset"])

    milestones = [
        {
            "milestone": "0 → 1,000 followers",
            "focus": "Content testing",
            "actions": [
                f"Post {n['posting_frequency']} for 30 days straight — do NOT skip",
                "Test 10+ different content styles/angles",
                "Identify your top 3 performing content formats",
                "Optimize bio, profile photo, and display name",
                "Engage with 50 accounts in your niche daily",
            ],
            "monetization": "None yet — focus 100% on growth",
        },
        {
            "milestone": "1,000 → 10,000 followers",
            "focus": "Double down on winners",
            "actions": [
                "Replicate your top performing posts (same format, fresh content)",
                "Add a link in bio (Linktree/Stan Store) with a free lead magnet",
                "Start building an email list — this is your real asset",
                "Test affiliate links in bio/caption",
                "Engage with every comment — algorithm rewards this",
            ],
            "monetization": "Affiliate marketing (start small), digital products if ready",
        },
        {
            "milestone": "10,000 → 100,000 followers",
            "focus": "Consistency + monetization",
            "actions": [
                "Create your first digital product or course ($17-47 entry price)",
                "DM brands in your niche with your media kit",
                "Start running shoutout-for-shoutout (S4S) with similar-sized pages",
                "Launch an email newsletter (ConvertKit/Beehiiv — free to start)",
                "Cross-post to all platforms to maximize reach",
            ],
            "monetization": "Brand deals, affiliate links, digital products",
        },
        {
            "milestone": "100,000 → 1,000,000 followers",
            "focus": "Scale and diversify",
            "actions": [
                "Hire a VA to handle engagement and content repurposing",
                "Build a premium offer ($97-497+)",
                "Launch a membership community",
                "Start a YouTube channel for evergreen SEO traffic",
                "Consider selling a theme page for 12-24x monthly revenue",
            ],
            "monetization": "Full stack: brand deals + products + courses + affiliate + membership",
        },
    ]

    current_phase = 0
    if current_followers >= 100000:
        current_phase = 3
    elif current_followers >= 10000:
        current_phase = 2
    elif current_followers >= 1000:
        current_phase = 1

    return {
        "niche": niche,
        "current_followers": current_followers,
        "current_phase": current_phase,
        "current_milestone": milestones[current_phase]["milestone"],
        "all_milestones": milestones,
        "content_sources": n["content_sources"],
        "top_hashtags": n["top_hashtags"],
        "difficulty": n["difficulty"],
        "growth_speed": n["growth_speed"],
        "notes": n["notes"],
    }


def monetization_guide(method: Optional[str] = None) -> list[dict] | dict:
    """Return monetization strategy guide."""
    if method:
        m = _MONETIZATION_METHODS.get(method.lower().replace(" ", "_"))
        if not m:
            return {"error": f"Unknown method. Available: {list(_MONETIZATION_METHODS.keys())}"}
        return {"method": method, **m}
    return [{"method": k, **v} for k, v in _MONETIZATION_METHODS.items()]


def conversion_optimization_tips(platform: str) -> list[dict]:
    """Return conversion optimization tactics for turning followers into buyers on a platform."""
    tips = {
        "tiktok": [
            {"tactic": "Link-in-bio funnel", "description": "Use Stan Store or Beacons. Offer a free lead magnet to capture emails first."},
            {"tactic": "CTA in every video", "description": "End each video with 'Link in bio for [specific benefit]' — be explicit."},
            {"tactic": "Pinned video", "description": "Pin your best-performing sales/conversion video at the top of profile."},
            {"tactic": "Comment pinning", "description": "Pin a comment with your link/CTA on viral videos."},
            {"tactic": "TikTok Shop", "description": "If eligible, use TikTok Shop for in-video product tags — converts 3x better than bio links."},
        ],
        "youtube": [
            {"tactic": "End screens", "description": "Add clickable end screens for your products/links in the last 20 seconds."},
            {"tactic": "Cards", "description": "Use YouTube Cards to link to relevant videos and your product mid-video."},
            {"tactic": "Description links", "description": "First line of description should be your CTA link — most viewers don't scroll."},
            {"tactic": "Pinned comment", "description": "Pin a comment with your offer link and add it within 30 min of posting."},
            {"tactic": "Community tab", "description": "Use Community tab to announce products, run polls, and keep audience warm."},
        ],
        "instagram": [
            {"tactic": "Link in bio", "description": "Use Linktree/Beacons with 3-5 options max — fewer choices = higher conversions."},
            {"tactic": "Story swipe-ups", "description": "Use link stickers in Stories (available to all users) for time-sensitive CTAs."},
            {"tactic": "Close Friends", "description": "Offer exclusive content via Close Friends list to build premium community."},
            {"tactic": "Story highlights", "description": "Create Highlights for: Testimonials, Products, Free Resources, About Me."},
            {"tactic": "DM automation", "description": "Use ManyChat to auto-DM your link when users comment a keyword (e.g., 'INFO')."},
        ],
    }
    return tips.get(platform, tips["tiktok"])


