"""Theme page strategy engine — niche selection, conversion, monetization."""

from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------------------
# Niche database — research-backed saturation, CPM, and monetization potential
# ---------------------------------------------------------------------------

NICHES: dict[str, dict] = {
    "finance": {
        "display": "Finance / Money",
        "saturation": "high",
        "cpm_usd": 15,
        "affiliate_potential": "very_high",
        "brand_deal_avg_usd": 2500,
        "audience_purchase_intent": "very_high",
        "content_types": ["financial tips", "investing 101", "income breakdowns", "debt payoff journeys"],
        "monetization": ["affiliate (courses/software)", "brand deals (fintech apps)", "digital products", "consulting"],
        "keywords": ["money", "investing", "wealth", "financial freedom", "budgeting", "stocks", "crypto", "passive income"],
        "competitor_saturation_note": "High saturation but very high CPM makes it worth it. Differentiate by sub-niche.",
        "sub_niches": ["crypto", "real estate investing", "stock market", "budgeting for beginners", "side hustles"],
    },
    "fitness": {
        "display": "Fitness / Health",
        "saturation": "very_high",
        "cpm_usd": 8,
        "affiliate_potential": "high",
        "brand_deal_avg_usd": 1500,
        "audience_purchase_intent": "high",
        "content_types": ["workout tutorials", "transformation stories", "nutrition tips", "gym motivation"],
        "monetization": ["supplement affiliates", "fitness app affiliates", "merch", "online coaching"],
        "keywords": ["workout", "fitness", "gym", "health", "nutrition", "weight loss", "muscle gain"],
        "competitor_saturation_note": "Very saturated but consistent demand. Win with transformation stories.",
        "sub_niches": ["home workouts", "calisthenics", "women's fitness", "running", "yoga"],
    },
    "beauty": {
        "display": "Beauty / Skincare",
        "saturation": "very_high",
        "cpm_usd": 10,
        "affiliate_potential": "very_high",
        "brand_deal_avg_usd": 2000,
        "audience_purchase_intent": "very_high",
        "content_types": ["product reviews", "GRWM", "skincare routines", "makeup tutorials", "dupes"],
        "monetization": ["affiliate (Amazon, Sephora)", "brand deals", "merch", "own product line"],
        "keywords": ["skincare", "makeup", "beauty", "glow", "routine", "review", "dupe"],
        "competitor_saturation_note": "Extremely saturated. Sub-niche into specific demographics (men's skincare, mature skin).",
        "sub_niches": ["men's grooming", "natural beauty", "k-beauty", "drugstore dupes", "mature skincare"],
    },
    "travel": {
        "display": "Travel",
        "saturation": "medium",
        "cpm_usd": 9,
        "affiliate_potential": "high",
        "brand_deal_avg_usd": 3000,
        "audience_purchase_intent": "medium",
        "content_types": ["destination guides", "travel tips", "budget travel", "luxury travel", "hidden gems"],
        "monetization": ["hotel/flight affiliates", "brand deals", "YouTube AdSense", "travel presets/guides"],
        "keywords": ["travel", "wanderlust", "destination", "explore", "vacation", "hidden gems"],
        "competitor_saturation_note": "Medium saturation. Budget + hidden gems angle cuts through.",
        "sub_niches": ["solo travel", "budget travel", "luxury travel", "van life", "digital nomad"],
    },
    "gaming": {
        "display": "Gaming",
        "saturation": "very_high",
        "cpm_usd": 5,
        "affiliate_potential": "high",
        "brand_deal_avg_usd": 1200,
        "audience_purchase_intent": "medium",
        "content_types": ["gameplay clips", "tutorials", "tier lists", "news/reactions", "setup tours"],
        "monetization": ["affiliate (gaming gear)", "brand deals", "Twitch subs", "merchandise"],
        "keywords": ["gaming", "gameplay", "tutorial", "guide", "tips", "highlights", "streaming"],
        "competitor_saturation_note": "Huge but long-tail game niches still low-competition.",
        "sub_niches": ["mobile gaming", "retro gaming", "indie games", "speedrunning", "specific game titles"],
    },
    "education": {
        "display": "Education / Learning",
        "saturation": "medium",
        "cpm_usd": 12,
        "affiliate_potential": "high",
        "brand_deal_avg_usd": 2000,
        "audience_purchase_intent": "high",
        "content_types": ["explainer videos", "study tips", "book summaries", "career advice", "how-tos"],
        "monetization": ["course sales", "affiliate (Skillshare, Udemy)", "brand deals", "consulting"],
        "keywords": ["learn", "education", "study", "how to", "explained", "tips", "guide"],
        "competitor_saturation_note": "Medium saturation with high CPM. Own a specific subject or skill.",
        "sub_niches": ["language learning", "programming", "math", "history", "science explained"],
    },
    "motivation": {
        "display": "Motivation / Mindset",
        "saturation": "high",
        "cpm_usd": 6,
        "affiliate_potential": "medium",
        "brand_deal_avg_usd": 800,
        "audience_purchase_intent": "medium",
        "content_types": ["speech compilations", "quotes", "success stories", "mindset tips"],
        "monetization": ["merchandise", "digital products", "affiliate (books/courses)", "YouTube AdSense"],
        "keywords": ["motivation", "mindset", "success", "hustle", "inspiration", "grind", "discipline"],
        "competitor_saturation_note": "Easy to start but hard to differentiate. Combine with a specific niche.",
        "sub_niches": ["stoicism", "discipline", "morning routines", "entrepreneur mindset", "sports motivation"],
    },
    "pets": {
        "display": "Pets / Animals",
        "saturation": "medium",
        "cpm_usd": 7,
        "affiliate_potential": "medium",
        "brand_deal_avg_usd": 1000,
        "audience_purchase_intent": "high",
        "content_types": ["pet vlogs", "training tips", "funny pet moments", "product reviews"],
        "monetization": ["affiliate (pet products)", "brand deals", "merchandise", "AdSense"],
        "keywords": ["dog", "cat", "pet", "puppy", "kitten", "training", "cute animals"],
        "competitor_saturation_note": "Viral potential is very high. Consistent personality-driven content wins.",
        "sub_niches": ["dog training", "exotic pets", "rescue stories", "cat behavior", "pet gear reviews"],
    },
    "food": {
        "display": "Food / Cooking",
        "saturation": "very_high",
        "cpm_usd": 9,
        "affiliate_potential": "high",
        "brand_deal_avg_usd": 1500,
        "audience_purchase_intent": "high",
        "content_types": ["recipes", "cooking tutorials", "food reviews", "meal prep", "restaurant tours"],
        "monetization": ["cookbook/recipe digital products", "brand deals (kitchen brands)", "affiliate", "AdSense"],
        "keywords": ["recipe", "cooking", "food", "delicious", "meal prep", "healthy", "easy recipe"],
        "competitor_saturation_note": "High saturation. Win with format: super fast (15s), ASMR cooking, or hyper-specific diet niche.",
        "sub_niches": ["vegan cooking", "meal prep", "street food", "baking", "5-ingredient meals"],
    },
    "tech": {
        "display": "Tech / Gadgets",
        "saturation": "medium",
        "cpm_usd": 18,
        "affiliate_potential": "very_high",
        "brand_deal_avg_usd": 3500,
        "audience_purchase_intent": "very_high",
        "content_types": ["product reviews", "unboxings", "comparisons", "tutorials", "news"],
        "monetization": ["affiliate (Amazon, Best Buy)", "brand deals (tech companies)", "AdSense", "sponsorships"],
        "keywords": ["tech", "gadget", "review", "unboxing", "best", "vs", "setup", "AI"],
        "competitor_saturation_note": "High CPM, high affiliate value. Best ROI for review channels.",
        "sub_niches": ["AI tools", "Apple products", "budget tech", "smart home", "productivity apps"],
    },
}

CONVERSION_STRATEGIES = {
    "follow_to_engagement": {
        "name": "Follow → Engagement Conversion",
        "goal": "Turn followers into active, loyal community members",
        "tactics": [
            "Pin a welcome video asking followers to comment their #1 goal",
            "Reply to every comment within the first hour of posting",
            "Use polls and Q&A in stories/community posts weekly",
            "Create series content that requires following to catch the next part",
            "Shout out top commenters in videos",
        ],
        "kpis": ["comment rate", "save rate", "profile visit rate", "DM volume"],
        "expected_timeline_days": 30,
    },
    "engagement_to_leads": {
        "name": "Engagement → Lead Conversion",
        "goal": "Turn viewers into email subscribers or DM contacts",
        "tactics": [
            "Offer a free resource (checklist, template, guide) in the bio link",
            "Say 'DM me [keyword]' to automate lead collection via ManyChat",
            "Use link-in-bio tools (Linktree, Stan.store) with lead capture",
            "Create 'part 2 in my free newsletter' hooks",
            "Run giveaways requiring email signup to enter",
        ],
        "kpis": ["bio link clicks", "email opt-in rate", "DM volume", "landing page CVR"],
        "expected_timeline_days": 60,
    },
    "leads_to_customers": {
        "name": "Leads → Customer Conversion",
        "goal": "Monetize your audience through products/services/affiliates",
        "tactics": [
            "Send a 5-email welcome sequence to new subscribers",
            "Share case studies / transformations of past customers",
            "Create urgency with limited-time offers (48hr window)",
            "Use video testimonials from satisfied customers",
            "Soft-sell in 1 of every 5 posts; over-selling kills trust",
        ],
        "kpis": ["email open rate", "click-through rate", "conversion rate", "revenue per subscriber"],
        "expected_timeline_days": 90,
    },
    "page_to_brand_deals": {
        "name": "Theme Page → Brand Deal Pipeline",
        "goal": "Land paid sponsorships from brands in your niche",
        "tactics": [
            "Hit 10K followers first — brands rarely respond below this",
            "Build a media kit: niche, audience demographics, avg views, engagement rate",
            "Cold DM 10 brands per week that sponsor similar creators",
            "Create 1-2 'spec' branded posts to show production quality",
            "Join influencer marketplaces: AspireIQ, Creator.co, Grin, Modash",
        ],
        "kpis": ["outreach response rate", "deals closed", "average deal value", "recurring partners"],
        "expected_timeline_days": 90,
    },
}

THEME_PAGE_PLAYBOOK: list[dict] = [
    {
        "phase": 1,
        "name": "Niche Selection & Research",
        "duration": "Week 1",
        "steps": [
            "Choose 1 niche with: high CPM (>$7), audience purchase intent, and sub-niche potential",
            "Identify top 10 creators in the niche — analyze their top 20 videos each",
            "Note: what hooks they use, video length, posting frequency, hashtags, engagement",
            "Identify content gaps: what topics aren't being covered well?",
            "Define your unique angle: same niche, different voice, format, or audience segment",
        ],
        "tools": ["SocialBlade", "NotJustAnalytics", "TikTok search", "YouTube search"],
        "deliverable": "Niche brief: niche, angle, top 5 competitors, 20 content ideas",
    },
    {
        "phase": 2,
        "name": "Brand Setup",
        "duration": "Week 1-2",
        "steps": [
            "Create accounts on: TikTok, Instagram, YouTube Shorts (same handle everywhere)",
            "Design profile: logo (Canva), banner, optimized bio with keyword + CTA",
            "Set up bio link (Stan.store or Linktree) with: free resource, main offer, social links",
            "Create 3-5 highlight covers for Instagram (Canva templates)",
            "Source content library: 50+ pieces of curated content for initial batch",
        ],
        "tools": ["Canva", "Stan.store", "Linktree", "CapCut"],
        "deliverable": "Fully set up profile on all platforms",
    },
    {
        "phase": 3,
        "name": "Content System",
        "duration": "Week 2-3",
        "steps": [
            "Batch create 21 videos in one session (3 weeks of content)",
            "Format: hook (3s) → value (15-45s) → CTA (3s). No intros.",
            "Use trending sounds from TikTok's 'viral sounds' tab",
            "Add captions to every video (80% of views are without sound)",
            "Create 3 content pillars (e.g., Finance: tips / stories / news)",
        ],
        "tools": ["CapCut", "InShot", "Adobe Express", "Canva", "Descript"],
        "deliverable": "21-video content batch ready to schedule",
    },
    {
        "phase": 4,
        "name": "Growth Phase",
        "duration": "Week 3-12",
        "steps": [
            "Post 1-2x/day consistently — consistency beats quality in the algorithm",
            "Engage: reply to ALL comments in the first 60 minutes of posting",
            "Collaborate: duet/stitch top creators in your niche weekly",
            "Trend-jack: post your niche take on every viral trend within 24 hours",
            "Track weekly: which videos hit >1x follower views (algorithm push)",
            "Double down: recreate winning video formats with new topics",
        ],
        "tools": ["Later", "Buffer", "TikTok Creator Portal", "YouTube Studio"],
        "deliverable": "10K followers milestone",
    },
    {
        "phase": 5,
        "name": "Monetization",
        "duration": "Month 3+",
        "steps": [
            "Join affiliate programs: Amazon Associates, ShareASale, ClickBank, impact.com",
            "Apply to TikTok Creator Fund (10K followers, 100K views/30 days)",
            "Apply to YouTube Partner Program (1K subs + 4K watch hours)",
            "Cold pitch 10 brands/week with your media kit",
            "Launch a digital product: ebook, template, mini-course ($27-$97)",
            "Add email list — owned audience is your most valuable asset",
        ],
        "tools": ["Gumroad", "Stan.store", "Beehiiv", "ConvertKit", "impact.com"],
        "deliverable": "First $1,000/month from content",
    },
    {
        "phase": 6,
        "name": "Scale",
        "duration": "Month 6+",
        "steps": [
            "Hire video editor ($200-500/mo on Fiverr/Upwork) to double output",
            "Build systems: content calendar, editing SOP, publishing checklist",
            "Expand to 3+ platforms with repurposing (1 video → 3 platforms)",
            "Launch higher-ticket offer ($297-$997): coaching, community, course",
            "Negotiate long-term brand deals (3-6 month retainers)",
            "Build email list to 1K+ and monetize with weekly newsletter",
        ],
        "tools": ["Fiverr", "Upwork", "Kajabi", "Circle.so", "Beehiiv"],
        "deliverable": "$5K-$10K/month milestone",
    },
]

MONETIZATION_CALCULATOR = {
    "tiktok_creator_fund": {"rate_per_1k_views": 0.02, "min_followers": 10000},
    "youtube_adsense": {"cpm_range": [2, 10], "avg_rpm": 3.5},
    "instagram_reels_bonus": {"rate_per_1k_plays": 0.01, "available": "US creators only"},
    "brand_deal_rates": {
        "1K-10K":    {"tiktok": 50, "instagram": 100, "youtube": 200},
        "10K-50K":   {"tiktok": 300, "instagram": 500, "youtube": 1000},
        "50K-100K":  {"tiktok": 800, "instagram": 1500, "youtube": 3000},
        "100K-500K": {"tiktok": 2000, "instagram": 5000, "youtube": 8000},
        "500K+":     {"tiktok": 5000, "instagram": 15000, "youtube": 25000},
    },
    "affiliate_avg_commission_pct": {"amazon": 3, "clickbank": 30, "software": 25, "courses": 40},
}


def score_niche(niche_key: str) -> dict:
    """Return a composite score for a niche based on multiple factors."""
    if niche_key not in NICHES:
        return {"error": f"Unknown niche: {niche_key}. Available: {list(NICHES.keys())}"}
    n = NICHES[niche_key]
    sat_score = {"low": 30, "medium": 20, "high": 10, "very_high": 5}.get(n["saturation"], 10)
    cpm_score = min(30, int(n["cpm_usd"] * 1.5))
    aff_score = {"very_high": 25, "high": 18, "medium": 10, "low": 5}.get(n["affiliate_potential"], 10)
    intent_score = {"very_high": 15, "high": 10, "medium": 6, "low": 3}.get(n["audience_purchase_intent"], 6)
    total = sat_score + cpm_score + aff_score + intent_score
    return {
        "niche": niche_key,
        "display": n["display"],
        "total_score": total,
        "max_score": 100,
        "breakdown": {
            "low_competition": sat_score,
            "ad_revenue_potential": cpm_score,
            "affiliate_potential": aff_score,
            "audience_intent": intent_score,
        },
        "grade": "A" if total >= 70 else "B" if total >= 55 else "C" if total >= 40 else "D",
        "recommendation": n["competitor_saturation_note"],
    }


def get_niche_starter_kit(niche_key: str) -> dict:
    """Return a full starter kit for a niche."""
    if niche_key not in NICHES:
        return {"error": f"Unknown niche: {niche_key}. Available: {list(NICHES.keys())}"}
    n = NICHES[niche_key]
    return {
        "niche": niche_key,
        "display": n["display"],
        "cpm_usd": n["cpm_usd"],
        "saturation": n["saturation"],
        "sub_niches": n["sub_niches"],
        "content_types": n["content_types"],
        "monetization_methods": n["monetization"],
        "seed_keywords": n["keywords"],
        "saturation_note": n["competitor_saturation_note"],
        "score": score_niche(niche_key),
    }


def get_playbook(phase: Optional[int] = None) -> list[dict] | dict:
    """Return the full theme page playbook or a specific phase."""
    if phase is not None:
        for p in THEME_PAGE_PLAYBOOK:
            if p["phase"] == phase:
                return p
        return {"error": f"Phase {phase} not found. Available: 1-{len(THEME_PAGE_PLAYBOOK)}"}
    return THEME_PAGE_PLAYBOOK


def estimate_revenue(followers: int, platform: str, avg_views_per_post: int, niche: str) -> dict:
    """Estimate monthly revenue potential."""
    niche_data = NICHES.get(niche.lower(), {})
    cpm = niche_data.get("cpm_usd", 5)

    # Estimate posts/month
    posts_per_month = 30

    # AdSense/creator fund (YouTube)
    yt_monthly = (avg_views_per_post * posts_per_month / 1000) * (cpm * 0.45)

    # TikTok creator fund
    tk_fund_monthly = avg_views_per_post * posts_per_month / 1000 * MONETIZATION_CALCULATOR["tiktok_creator_fund"]["rate_per_1k_views"] * 1000

    # Brand deals
    follower_tier = "1K-10K"
    for tier in ["500K+", "100K-500K", "50K-100K", "10K-50K", "1K-10K"]:
        low = tier.replace("K+", "000").split("-")[0].replace("K", "000").replace("+", "")
        if followers >= int(low.replace("K", "000") if "K" in low else low):
            follower_tier = tier
            break
    brand_rates = MONETIZATION_CALCULATOR["brand_deal_rates"].get(follower_tier, {})
    brand_deal_monthly = brand_rates.get(platform.lower(), 0) * 2

    # Affiliate estimate
    affiliate_monthly = avg_views_per_post * posts_per_month * 0.001 * 15

    total_estimate = brand_deal_monthly + affiliate_monthly + (yt_monthly if platform == "youtube" else tk_fund_monthly)

    return {
        "followers": followers,
        "platform": platform,
        "niche": niche,
        "monthly_estimates_usd": {
            "platform_ads_fund": round(yt_monthly if platform == "youtube" else tk_fund_monthly, 2),
            "brand_deals": round(brand_deal_monthly, 2),
            "affiliate": round(affiliate_monthly, 2),
            "total": round(total_estimate, 2),
        },
        "follower_tier": follower_tier,
        "notes": [
            "Estimates based on industry averages. Actual results vary significantly.",
            "Brand deals are the highest ROI channel at most follower counts.",
            "Digital products (not included above) can 5-10x revenue once you have 10K+ engaged followers.",
        ],
    }


def compare_niches(niche_keys: list[str]) -> list[dict]:
    """Compare multiple niches side-by-side."""
    results = []
    for key in niche_keys:
        if key in NICHES:
            results.append(score_niche(key))
    results.sort(key=lambda x: x.get("total_score", 0), reverse=True)
    return results
