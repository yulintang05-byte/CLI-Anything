"""Theme page conversion — niche research, monetisation playbooks, revenue modelling.

A "theme page" (also called a "niche page" or "fan page") is a social media
account built around a specific topic rather than a personal brand.  Examples:
@fitnessmotivation, @luxurycarsworld, @dailymindset, @cryptonews.

Theme pages scale faster than personal brands because:
  - Content can be repurposed/curated (no need to show your face)
  - Multiple pages can run simultaneously
  - Easier to sell/exit (no individual tied to it)

This module provides:
  - Niche opportunity scoring
  - Step-by-step theme page launch playbooks
  - Monetisation strategy recommendations
  - Revenue estimates based on niche + follower count
  - Viral content formulas per niche
  - Account flip / exit strategy guidance
"""

import datetime
from typing import Optional


# ── Niche database ────────────────────────────────────────────────────────────

NICHE_DATA: dict[str, dict] = {
    "fitness": {
        "display": "Fitness & Gym",
        "competition": "high",
        "monetisation_potential": "high",
        "avg_cpm_usd": 8.50,
        "affiliate_commission": "8-15%",
        "brand_deal_cpm": 25.0,
        "content_types": [
            "workout clips", "transformation videos", "form breakdowns",
            "supplement reviews", "motivational edits",
        ],
        "top_hashtags": [
            "#fitness", "#gym", "#workout", "#motivation", "#gains",
            "#fitlife", "#bodybuilding", "#personaltrainer",
        ],
        "viral_formula": "Before/After transformation + trending audio + 3-step result",
        "target_audience": "18-35 year olds, male-skewed, fitness-conscious",
        "best_platforms": ["tiktok", "instagram", "youtube"],
        "curation_sources": [
            "Reddit r/fitness", "YouTube fitness channels (with permission)",
            "User-generated content with credit", "Stock workout footage",
        ],
    },
    "luxury": {
        "display": "Luxury Lifestyle",
        "competition": "medium",
        "monetisation_potential": "very_high",
        "avg_cpm_usd": 15.0,
        "affiliate_commission": "3-8%",
        "brand_deal_cpm": 50.0,
        "content_types": [
            "supercar compilations", "yacht/jet content", "luxury real estate",
            "watches/jewellery", "penthouse tours",
        ],
        "top_hashtags": [
            "#luxury", "#supercar", "#lamborghini", "#ferrari", "#yacht",
            "#privatjet", "#luxurylife", "#millionairlife",
        ],
        "viral_formula": "Aspirational montage + lo-fi/phonk music + minimal text overlay",
        "target_audience": "16-30, aspirational, male-skewed",
        "best_platforms": ["tiktok", "instagram"],
        "curation_sources": [
            "DuCars, exotic car dealers (tag them for reposts)",
            "Luxury brand press kits",
            "Supercar events and public roads",
        ],
    },
    "finance": {
        "display": "Personal Finance & Investing",
        "competition": "medium",
        "monetisation_potential": "very_high",
        "avg_cpm_usd": 22.0,
        "affiliate_commission": "20-50%",
        "brand_deal_cpm": 40.0,
        "content_types": [
            "money tips (21-30s)", "stock/crypto alerts", "budgeting hacks",
            "side hustle ideas", "wealth mindset",
        ],
        "top_hashtags": [
            "#money", "#investing", "#personalfinance", "#stocks",
            "#crypto", "#passiveincome", "#financialfreedom", "#wealthmindset",
        ],
        "viral_formula": "Shocking money fact + 3 actionable steps + CTA to follow",
        "target_audience": "22-40, ambitious, mixed gender",
        "best_platforms": ["tiktok", "youtube", "instagram"],
        "curation_sources": [
            "Financial news (Reuters, Bloomberg — summarise, don't copy)",
            "Public domain finance books",
            "Your own financial journey",
        ],
    },
    "motivation": {
        "display": "Motivation & Mindset",
        "competition": "very_high",
        "monetisation_potential": "medium",
        "avg_cpm_usd": 5.0,
        "affiliate_commission": "10-30%",
        "brand_deal_cpm": 15.0,
        "content_types": [
            "quote graphics", "speech edits", "mindset clips",
            "success story re-edits", "daily affirmations",
        ],
        "top_hashtags": [
            "#motivation", "#mindset", "#success", "#hustle", "#inspire",
            "#believe", "#discipline", "#grindset",
        ],
        "viral_formula": "Powerful speech clip + cinematic music + bold text overlay + shocking stat",
        "target_audience": "16-35, ambitious, mixed gender",
        "best_platforms": ["tiktok", "instagram", "youtube"],
        "curation_sources": [
            "Speeches (check licensing)", "Podcast clips (with permission)",
            "Public domain motivational content",
        ],
        "note": "High competition — differentiate by pairing with a sub-niche (e.g. 'entrepreneur motivation')",
    },
    "food": {
        "display": "Food & Recipes",
        "competition": "very_high",
        "monetisation_potential": "medium",
        "avg_cpm_usd": 7.0,
        "affiliate_commission": "5-15%",
        "brand_deal_cpm": 20.0,
        "content_types": [
            "15s recipe videos", "food compilation", "taste tests",
            "cooking hacks", "restaurant reviews",
        ],
        "top_hashtags": [
            "#food", "#recipe", "#cooking", "#foodie", "#eats",
            "#homecooking", "#viralrecipe", "#foodtok",
        ],
        "viral_formula": "Satisfying cooking process + ASMR audio + 'Try this tonight' text",
        "target_audience": "25-45, mixed gender, home cooks",
        "best_platforms": ["tiktok", "instagram", "youtube"],
        "curation_sources": [
            "User recipes (with credit/permission)", "Original cooking videos",
            "Restaurant collaborations",
        ],
    },
    "travel": {
        "display": "Travel & Adventure",
        "competition": "high",
        "monetisation_potential": "high",
        "avg_cpm_usd": 12.0,
        "affiliate_commission": "3-10%",
        "brand_deal_cpm": 35.0,
        "content_types": [
            "destination highlights", "travel hacks", "budget travel tips",
            "hidden gems", "travel vlogs (cinematic)",
        ],
        "top_hashtags": [
            "#travel", "#wanderlust", "#explore", "#adventure", "#travelblogger",
            "#travelgram", "#hiddenGems", "#bucketlist",
        ],
        "viral_formula": "Jaw-dropping scenery + dreamy music + '5 things you didn't know about X'",
        "target_audience": "20-40, mixed gender, wanderlusters",
        "best_platforms": ["instagram", "tiktok", "youtube"],
        "curation_sources": [
            "Creative Commons travel footage (Pexels, Pixabay)",
            "Local tourism boards (often provide free media)",
            "Your own travel footage",
        ],
    },
    "pets": {
        "display": "Pets & Animals",
        "competition": "high",
        "monetisation_potential": "medium",
        "avg_cpm_usd": 6.0,
        "affiliate_commission": "8-20%",
        "brand_deal_cpm": 18.0,
        "content_types": [
            "cute pet compilations", "funny animal moments", "pet care tips",
            "product reviews", "breed spotlights",
        ],
        "top_hashtags": [
            "#dog", "#cat", "#pets", "#dogsofinstagram", "#animals",
            "#cutepets", "#funnypets", "#animallovers",
        ],
        "viral_formula": "Unexpected pet reaction + relatable caption + trending audio",
        "target_audience": "All ages, pet owners, female-skewed",
        "best_platforms": ["tiktok", "instagram", "youtube"],
        "curation_sources": [
            "UGC from followers (repost with credit)",
            "Free stock animal footage",
            "Your own pet content",
        ],
    },
    "gaming": {
        "display": "Gaming",
        "competition": "very_high",
        "monetisation_potential": "high",
        "avg_cpm_usd": 4.5,
        "affiliate_commission": "3-10%",
        "brand_deal_cpm": 12.0,
        "content_types": [
            "highlight clips", "fails & wins compilations", "tips & tricks",
            "game reviews", "speedruns",
        ],
        "top_hashtags": [
            "#gaming", "#gamer", "#gameplay", "#twitch", "#esports",
            "#gamingcommunity", "#pcgaming", "#xbox",
        ],
        "viral_formula": "Insane/impossible play + reaction audio + 'How?!' text hook",
        "target_audience": "13-30, male-skewed, gamers",
        "best_platforms": ["tiktok", "youtube", "instagram"],
        "curation_sources": [
            "Twitch clips (check terms)", "YouTube highlights (with permission)",
            "Original gameplay",
        ],
    },
    "beauty": {
        "display": "Beauty & Makeup",
        "competition": "very_high",
        "monetisation_potential": "very_high",
        "avg_cpm_usd": 14.0,
        "affiliate_commission": "10-25%",
        "brand_deal_cpm": 30.0,
        "content_types": [
            "makeup tutorials", "skincare routines", "product reviews",
            "transformation videos", "GRWM (get ready with me)",
        ],
        "top_hashtags": [
            "#makeup", "#beauty", "#skincare", "#glam", "#GRWM",
            "#makeuptutorial", "#beautytips", "#skincareroutine",
        ],
        "viral_formula": "Bare face to full glam in 30s + satisfying audio + product reveal CTA",
        "target_audience": "16-35, female-skewed",
        "best_platforms": ["tiktok", "instagram", "youtube"],
        "curation_sources": [
            "Original tutorials", "UGC with permission",
            "Brand-provided content (sponsorships)",
        ],
    },
    "crypto": {
        "display": "Crypto & Web3",
        "competition": "medium",
        "monetisation_potential": "very_high",
        "avg_cpm_usd": 25.0,
        "affiliate_commission": "20-50%",
        "brand_deal_cpm": 60.0,
        "content_types": [
            "price alerts", "coin explainers", "wallet tutorials",
            "NFT/DeFi breakdowns", "macro analysis",
        ],
        "top_hashtags": [
            "#crypto", "#bitcoin", "#ethereum", "#blockchain", "#nft",
            "#defi", "#altcoins", "#cryptonews",
        ],
        "viral_formula": "Price prediction or breaking news + data visual + 'What this means for you'",
        "target_audience": "18-35, tech-savvy, male-skewed",
        "best_platforms": ["twitter", "youtube", "tiktok"],
        "curation_sources": [
            "CoinDesk, CoinTelegraph (summarise with attribution)",
            "Official project announcements",
            "On-chain data (Dune Analytics, Nansen)",
        ],
        "note": "High CPM and affiliate earnings but requires compliance awareness",
    },
}

# ── Monetisation strategies ───────────────────────────────────────────────────

MONETISATION_STRATEGIES: dict[str, dict] = {
    "affiliate_marketing": {
        "display": "Affiliate Marketing",
        "min_followers": 500,
        "description": "Earn commission by promoting products with trackable links.",
        "best_niches": ["finance", "beauty", "fitness", "tech", "travel"],
        "platforms": ["tiktok", "instagram", "youtube"],
        "setup_steps": [
            "Sign up for Amazon Associates, ShareASale, or niche-specific programs.",
            "Get your unique affiliate link for each product.",
            "Add link to bio via Linktree (supports multiple links).",
            "Disclose affiliate relationships in every post (#ad, #affiliate).",
            "Post authentic reviews — forced promotions lose trust fast.",
        ],
        "earnings_per_1k_followers": "$5-$50",
        "time_to_first_dollar": "1-4 weeks after reaching 500 followers",
    },
    "brand_deals": {
        "display": "Brand Sponsorships & Deals",
        "min_followers": 5000,
        "description": "Brands pay you to feature their product/service in content.",
        "best_niches": ["beauty", "fitness", "travel", "food", "luxury"],
        "platforms": ["tiktok", "instagram", "youtube"],
        "setup_steps": [
            "Build a media kit (follower count, engagement rate, audience demographics).",
            "Reach out to brands in your niche — start with small/medium brands.",
            "Join creator marketplaces: AspireIQ, Grapevine, TikTok Creator Marketplace.",
            "Set your rate: CPM × engagement rate. Start at $50-$100/post at 5K followers.",
            "Negotiate: request free product + cash. Always sign a contract.",
        ],
        "earnings_per_1k_followers": "$10-$100 per post",
        "time_to_first_dollar": "1-3 months with active outreach",
    },
    "account_flipping": {
        "display": "Account Flipping (Sell the Page)",
        "min_followers": 10000,
        "description": "Grow theme pages to 10K-100K followers and sell them.",
        "best_niches": ["motivation", "luxury", "fitness", "pets", "gaming"],
        "platforms": ["instagram", "tiktok"],
        "setup_steps": [
            "Build to 10K+ followers with strong engagement (>3%).",
            "Document growth metrics (weekly follower growth, avg likes, reach).",
            "List on Flippa, FameSwap, Social Tradia, or DM buyers directly.",
            "Price = monthly revenue × 12-24 (or $X per 1K followers based on niche).",
            "Transfer account via platform tools — always get paid first.",
        ],
        "earnings_per_1k_followers": "$20-$100 per 1K followers at sale",
        "time_to_first_dollar": "3-6 months (build to 10K+)",
    },
    "ugc_content": {
        "display": "UGC (User Generated Content) Creator",
        "min_followers": 0,
        "description": "Brands pay you to create content FOR them (no posting required).",
        "best_niches": ["beauty", "fitness", "food", "tech", "lifestyle"],
        "platforms": ["tiktok", "instagram"],
        "setup_steps": [
            "Build a portfolio of 3-5 sample UGC videos in your niche.",
            "Create a UGC rate card ($150-$500 per video is typical for beginners).",
            "DM brands on Instagram: 'I create UGC for [niche] brands. Here's my portfolio'.",
            "Join UGC communities on Twitter, TikTok, and Discord.",
            "Deliver fast, iterate on feedback — repeat buyers are the goal.",
        ],
        "earnings_per_1k_followers": "N/A — per-video rate regardless of followers",
        "time_to_first_dollar": "1-4 weeks after outreach",
    },
    "digital_products": {
        "display": "Sell Digital Products",
        "min_followers": 1000,
        "description": "Sell ebooks, templates, courses, or presets related to your niche.",
        "best_niches": ["finance", "fitness", "motivation", "beauty", "travel"],
        "platforms": ["tiktok", "instagram", "youtube"],
        "setup_steps": [
            "Identify the #1 pain point your audience has.",
            "Create a minimal digital product: PDF guide, Notion template, Lightroom preset.",
            "Host on Gumroad, Stan.store, or Payhip (free to start).",
            "Price at $7-$47 for entry products.",
            "Promote via story swipe-ups or bio link.",
        ],
        "earnings_per_1k_followers": "$50-$500 per launch",
        "time_to_first_dollar": "2-6 weeks after launch",
    },
    "platform_monetisation": {
        "display": "Platform Native Monetisation",
        "min_followers": 10000,
        "description": "YouTube AdSense, TikTok Creator Fund / LIVE gifts, Instagram Reels bonus.",
        "best_niches": ["finance", "fitness", "travel", "gaming", "beauty"],
        "platforms": ["youtube", "tiktok", "instagram"],
        "setup_steps": [
            "YouTube: Reach 1K subs + 4K watch hours → apply for Partner Program.",
            "TikTok: 10K followers + 18 years old → Creator Fund or Series subscription.",
            "Instagram: Meet Reels Play bonus invite criteria (invitation only).",
            "Optimise for watch time and saves — these boost the algorithm AND ad revenue.",
        ],
        "earnings_per_1k_followers": "$1-$5 (Fund) to $20+ (AdSense)",
        "time_to_first_dollar": "1-6 months depending on platform",
    },
}


# ── Core functions ────────────────────────────────────────────────────────────

def get_niche_analysis(niche: str) -> dict:
    """Return a full analysis of a content niche.

    Args:
        niche: Niche name (e.g. 'fitness', 'finance', 'luxury').

    Returns:
        Dict with competition level, monetisation potential, content types,
        hashtags, viral formula, and differentiation tips.
    """
    niche_lower = niche.lower()
    data = NICHE_DATA.get(niche_lower)

    if not data:
        # Fuzzy match
        matches = [k for k in NICHE_DATA if niche_lower in k or k in niche_lower]
        if matches:
            data = NICHE_DATA[matches[0]]
            niche_lower = matches[0]
        else:
            return {
                "error": f"Niche '{niche}' not in database.",
                "available_niches": list(NICHE_DATA.keys()),
            }

    competition_score = {"low": 3, "medium": 6, "high": 8, "very_high": 10}
    monetisation_score = {"low": 3, "medium": 6, "high": 8, "very_high": 10}

    comp = data.get("competition", "medium")
    mon = data.get("monetisation_potential", "medium")

    opportunity_score = (
        monetisation_score.get(mon, 6) * 2 - competition_score.get(comp, 6)
    ) / 10 * 100

    differentiation_tips = _get_differentiation_tips(niche_lower, comp)

    return {
        "niche": niche_lower,
        "display_name": data.get("display", niche.title()),
        "competition": comp,
        "monetisation_potential": mon,
        "opportunity_score": round(min(opportunity_score, 100), 1),
        "avg_cpm_usd": data.get("avg_cpm_usd", 5.0),
        "affiliate_commission_range": data.get("affiliate_commission", "5-15%"),
        "brand_deal_cpm_usd": data.get("brand_deal_cpm", 15.0),
        "target_audience": data.get("target_audience", "General"),
        "best_platforms": data.get("best_platforms", ["tiktok", "instagram"]),
        "content_types": data.get("content_types", []),
        "top_hashtags": data.get("top_hashtags", []),
        "viral_formula": data.get("viral_formula", ""),
        "curation_sources": data.get("curation_sources", []),
        "differentiation_tips": differentiation_tips,
        "notes": data.get("note", ""),
        "analysed_at": _now_iso(),
    }


def _get_differentiation_tips(niche: str, competition: str) -> list[str]:
    tips = []

    if competition in ("high", "very_high"):
        tips.append(
            f"The {niche} niche is saturated — niche DOWN. "
            f"Examples: '{niche} for beginners', '{niche} over 40', "
            f"'{niche} on a budget', 'female {niche}'."
        )

    tips += [
        "Pick a unique visual style (colour palette, font, editing style) and stick to it.",
        "Post at a higher frequency than competitors for the first 60 days.",
        "Engage daily: reply to every comment in your first 30 days to boost algorithm.",
        "Cross-post to multiple platforms — TikTok content repurposes perfectly to Reels.",
    ]

    return tips


def get_conversion_strategies(
    niche: str,
    platform: str = "tiktok",
    followers: int = 0,
) -> dict:
    """Return ranked monetisation strategies for a specific account.

    Args:
        niche: Content niche.
        platform: Primary platform.
        followers: Current follower count (used to filter viable strategies).

    Returns:
        Dict with ranked strategies and implementation steps.
    """
    niche_data = NICHE_DATA.get(niche.lower(), {})
    best_niches_by_strategy = {
        k: v.get("best_niches", []) for k, v in MONETISATION_STRATEGIES.items()
    }

    viable = []
    for strat_key, strat in MONETISATION_STRATEGIES.items():
        min_followers = strat.get("min_followers", 0)
        if followers >= min_followers and platform in strat.get("platforms", []):
            niche_match = (
                niche.lower() in strat.get("best_niches", [])
                or not strat.get("best_niches")
            )
            priority = 1 if niche_match else 2
            viable.append({
                "strategy": strat_key,
                "display": strat.get("display", strat_key),
                "description": strat.get("description", ""),
                "earnings_per_1k_followers": strat.get("earnings_per_1k_followers", ""),
                "time_to_first_dollar": strat.get("time_to_first_dollar", ""),
                "setup_steps": strat.get("setup_steps", []),
                "min_followers_required": min_followers,
                "niche_fit": "excellent" if niche_match else "good",
                "priority": priority,
            })

    viable.sort(key=lambda x: (x["priority"], x["min_followers_required"]))

    # Revenue projection
    revenue_projection = estimate_revenue(niche, followers, platform)

    return {
        "niche": niche,
        "platform": platform,
        "current_followers": followers,
        "viable_strategies": viable,
        "revenue_projection": revenue_projection,
        "quick_wins": [s for s in viable if s["min_followers_required"] == 0][:2],
        "generated_at": _now_iso(),
    }


def estimate_revenue(
    niche: str,
    followers: int,
    platform: str = "tiktok",
) -> dict:
    """Estimate monthly revenue across monetisation channels.

    Args:
        niche: Content niche.
        followers: Follower count.
        platform: Primary platform.

    Returns:
        Dict with low/mid/high revenue estimates per channel.
    """
    niche_data = NICHE_DATA.get(niche.lower(), {})
    cpm = niche_data.get("avg_cpm_usd", 5.0)
    brand_cpm = niche_data.get("brand_deal_cpm", 15.0)

    # Assume avg views = 15% of followers for TikTok/IG, 5% for YouTube
    view_rate = {"tiktok": 0.15, "instagram": 0.12, "youtube": 0.05}
    avg_views = followers * view_rate.get(platform, 0.10)

    # Platform ad revenue
    ad_monthly = avg_views * (cpm / 1000) * 30  # ~30 posts/mo

    # Brand deals: 1-4 per month depending on size
    brand_deals = 1 if followers < 10000 else (2 if followers < 100000 else 4)
    brand_deal_rate = (followers / 1000) * brand_cpm
    brand_monthly = brand_deals * brand_deal_rate

    # Affiliate: ~1% of followers click, ~3% buy, avg $30 item, avg 15% commission
    affiliate_monthly = followers * 0.01 * 0.03 * 30 * 0.15

    # Digital product: 0.1% of followers buy at $27 once a month
    product_monthly = followers * 0.001 * 27

    return {
        "platform": platform,
        "niche": niche,
        "followers": followers,
        "estimated_monthly_revenue": {
            "platform_ads": {
                "low": round(ad_monthly * 0.5, 2),
                "mid": round(ad_monthly, 2),
                "high": round(ad_monthly * 2.0, 2),
            },
            "brand_deals": {
                "low": round(brand_monthly * 0.3, 2),
                "mid": round(brand_monthly, 2),
                "high": round(brand_monthly * 2.0, 2),
            },
            "affiliate_marketing": {
                "low": round(affiliate_monthly * 0.3, 2),
                "mid": round(affiliate_monthly, 2),
                "high": round(affiliate_monthly * 3.0, 2),
            },
            "digital_products": {
                "low": round(product_monthly * 0.2, 2),
                "mid": round(product_monthly, 2),
                "high": round(product_monthly * 4.0, 2),
            },
        },
        "total_estimate": {
            "low": round(
                ad_monthly * 0.5 + brand_monthly * 0.3
                + affiliate_monthly * 0.3 + product_monthly * 0.2, 2
            ),
            "mid": round(
                ad_monthly + brand_monthly + affiliate_monthly + product_monthly, 2
            ),
            "high": round(
                ad_monthly * 2 + brand_monthly * 2
                + affiliate_monthly * 3 + product_monthly * 4, 2
            ),
        },
        "note": (
            "Estimates are based on industry averages. Actual results vary "
            "significantly based on engagement rate, content quality, and "
            "active monetisation effort."
        ),
    }


def get_theme_page_playbook(
    niche: str,
    platform: str = "tiktok",
    followers_goal: int = 10000,
) -> dict:
    """Generate a step-by-step theme page launch and growth playbook.

    Args:
        niche: Content niche.
        platform: Target platform.
        followers_goal: Target follower milestone.

    Returns:
        Dict with phased action plan, daily tasks, and milestones.
    """
    niche_data = get_niche_analysis(niche)
    if "error" in niche_data:
        return niche_data

    viral_formula = niche_data.get("viral_formula", "")
    content_types = niche_data.get("content_types", [])
    hashtags = niche_data.get("top_hashtags", [])

    phases = _build_playbook_phases(niche, platform, followers_goal, content_types)
    daily_tasks = _get_daily_tasks(platform, niche)
    milestones = _get_milestones(platform, followers_goal)

    return {
        "niche": niche,
        "platform": platform,
        "followers_goal": followers_goal,
        "estimated_time_to_goal": _estimate_growth_time(platform, followers_goal),
        "viral_formula": viral_formula,
        "phases": phases,
        "daily_tasks": daily_tasks,
        "milestones": milestones,
        "tools_needed": _get_tools(platform, niche),
        "content_bank_target": 30,
        "pro_tips": _get_pro_tips(niche, platform),
        "generated_at": _now_iso(),
    }


def _build_playbook_phases(
    niche: str,
    platform: str,
    goal: int,
    content_types: list[str],
) -> list[dict]:
    return [
        {
            "phase": 1,
            "name": "Foundation (Week 1-2)",
            "goal": "Set up + create content bank",
            "tasks": [
                f"Choose a niche-specific username (e.g. @daily{niche}, @{niche}hub).",
                "Write an optimised bio using the 'optimize bio' command.",
                "Set up a Linktree with affiliate links and future product links.",
                f"Create 30 pieces of {niche} content BEFORE posting anything.",
                "Study the top 10 accounts in your niche — note their content patterns.",
                "Build a content template: hooks, edits, fonts, colour palette.",
            ],
        },
        {
            "phase": 2,
            "name": "Launch Sprint (Week 3-6)",
            "goal": f"Hit first 1,000 followers on {platform}",
            "tasks": [
                f"Post {3 if platform == 'tiktok' else 1}x per day at optimal times.",
                "Use ONLY niche + medium hashtags (avoid #fyp spam in first 30 posts).",
                "Reply to every single comment within 30 minutes of posting.",
                "Duet/Stitch top performers in your niche (TikTok) or collab tag (IG).",
                f"Use trending audio on every video — check 'trends music' command daily.",
                "A/B test 2 different hooks per week and double-down on what works.",
            ],
        },
        {
            "phase": 3,
            "name": "Growth Engine (Month 2-3)",
            "goal": f"Scale to {goal // 2:,} followers",
            "tasks": [
                "Identify your top 3 performing content formats and produce 10x more.",
                "Add a 'series' format (e.g. #FinanceFriday, #MondayMotivation).",
                "Start building email list via bio link — even 100 emails = revenue.",
                "Begin affiliate marketing — add your first affiliate link.",
                "Cross-post to a second platform (TikTok → Instagram Reels or vice versa).",
            ],
        },
        {
            "phase": 4,
            "name": "Monetisation (Month 4+)",
            "goal": f"Hit {goal:,} followers + first revenue",
            "tasks": [
                "Reach out to 3 micro-brands for your first collaboration deal.",
                "Launch a low-ticket digital product ($7-$27) to your audience.",
                "Apply for platform monetisation (TikTok Creator Fund / YouTube Partner).",
                "Build a weekly newsletter or community (Telegram, Discord).",
                f"Consider account flip if not monetising — list on FameSwap at {goal:,}+.",
            ],
        },
    ]


def _get_daily_tasks(platform: str, niche: str) -> list[str]:
    tasks = [
        "Check 'trends hashtags' — update your hashtag set if new ones appeared.",
        "Check 'trends music' — swap to trending audio if a new track is spiking.",
        f"Post your scheduled {niche} content at the optimal time.",
        "Spend 15 min engaging: reply to comments, follow niche accounts, like top content.",
    ]
    if platform == "tiktok":
        tasks.append("Watch your analytics — if a video has <200 views at 2 hours, tweak the hook.")
    elif platform == "youtube":
        tasks.append("Optimise your latest video thumbnail — run A/B tests via YouTube Studio.")
    return tasks


def _get_milestones(platform: str, goal: int) -> list[dict]:
    milestones = [
        {"followers": 100,    "unlock": "First algorithm test — TikTok will distribute to small audience"},
        {"followers": 500,    "unlock": "Affiliate marketing viable — add your first link"},
        {"followers": 1000,   "unlock": "YouTube monetisation milestone / IG story links"},
        {"followers": 5000,   "unlock": "Brand deal outreach becomes viable ($50-$200/post)"},
        {"followers": 10000,  "unlock": "Account flip value: $200-$500 / TikTok LIVE access"},
        {"followers": 50000,  "unlock": "Mid-tier brand deals ($500-$2000/post)"},
        {"followers": 100000, "unlock": "Major brand deals ($1000-$10000+/post) / YouTube milestone"},
    ]
    return [m for m in milestones if m["followers"] <= goal * 1.5]


def _estimate_growth_time(platform: str, goal: int) -> str:
    """Rough estimate assuming consistent daily posting + engagement."""
    rates = {
        "tiktok": 500,      # followers/week with 3x daily posts
        "instagram": 200,
        "youtube": 100,
    }
    weeks_per_follower = rates.get(platform, 300)
    weeks = goal / weeks_per_follower
    if weeks < 4:
        return f"{int(weeks * 7)} days"
    elif weeks < 12:
        return f"{int(weeks)} weeks"
    else:
        return f"{int(weeks / 4.3)} months"


def _get_tools(platform: str, niche: str) -> list[dict]:
    tools = [
        {"tool": "CapCut", "use": "Video editing (free, TikTok-native)", "cost": "Free"},
        {"tool": "Canva", "use": "Thumbnails, story graphics, templates", "cost": "Free / $13/mo"},
        {"tool": "Linktree", "use": "Multi-link bio page", "cost": "Free / $6/mo"},
        {"tool": "Buffer / Later", "use": "Content scheduling", "cost": "Free tier / $18/mo"},
        {"tool": "cli-anything-social", "use": "Trend scraping + account audits", "cost": "Free"},
    ]
    if niche in ("finance", "crypto"):
        tools.append({
            "tool": "TradingView",
            "use": "Chart screenshots for content",
            "cost": "Free",
        })
    if platform == "youtube":
        tools.append({
            "tool": "TubeBuddy",
            "use": "YouTube SEO + keyword research",
            "cost": "Free / $9/mo",
        })
    return tools


def _get_pro_tips(niche: str, platform: str) -> list[str]:
    tips = [
        "The first 3 seconds decide everything — write your hook LAST, after you know the content.",
        "Save 20% of your best posts and re-upload them in 3 months — TikTok's algorithm resets.",
        "Go LIVE once you have 1K followers — LIVE sessions dramatically boost profile visibility.",
        f"Study your competitors' most viral {niche} videos and reverse-engineer the format.",
        "Never delete posts with low views — they can blow up days or weeks later.",
    ]
    if platform == "tiktok":
        tips.append(
            "Stitch trending videos in your niche — TikTok pushes stitch content to "
            "the same audience as the original."
        )
    return tips


def get_account_flip_valuation(
    niche: str,
    platform: str,
    followers: int,
    avg_monthly_revenue: float = 0.0,
    engagement_rate: float = 0.0,
) -> dict:
    """Estimate the sale value of a theme page.

    Args:
        niche: Content niche.
        platform: Platform.
        followers: Follower count.
        avg_monthly_revenue: Verified average monthly revenue ($).
        engagement_rate: Engagement rate percentage (0-100).

    Returns:
        Dict with estimated valuation range and selling tips.
    """
    niche_data = NICHE_DATA.get(niche.lower(), {})

    # Base price per 1K followers (varies by niche and engagement)
    base_per_1k = {
        "crypto": 40, "finance": 35, "beauty": 30, "fitness": 25,
        "luxury": 30, "travel": 25, "motivation": 15, "food": 15,
        "gaming": 12, "pets": 18,
    }
    per_1k = base_per_1k.get(niche.lower(), 15)

    # Engagement multiplier
    if engagement_rate >= 8:
        eng_mult = 2.0
    elif engagement_rate >= 4:
        eng_mult = 1.5
    elif engagement_rate >= 2:
        eng_mult = 1.0
    else:
        eng_mult = 0.7

    base_value = (followers / 1000) * per_1k * eng_mult

    # Revenue multiple (if monetised, sell for 12-24x monthly revenue)
    revenue_value = avg_monthly_revenue * 18 if avg_monthly_revenue > 0 else 0

    valuation = max(base_value, revenue_value)

    return {
        "niche": niche,
        "platform": platform,
        "followers": followers,
        "engagement_rate": engagement_rate,
        "avg_monthly_revenue": avg_monthly_revenue,
        "estimated_value": {
            "low": round(valuation * 0.7, 2),
            "mid": round(valuation, 2),
            "high": round(valuation * 1.5, 2),
        },
        "marketplaces": [
            "FameSwap.com — largest social media account marketplace",
            "SocialTradia.com — vetted buyers, higher average prices",
            "Flippa.com — broader audience, good for monetised pages",
            "PlayerUp.com — gaming-focused but accepts all niches",
            "Direct DMs to buyers in niche Facebook groups / Discord",
        ],
        "sale_tips": [
            "Provide 30 days of analytics screenshots as proof of stats.",
            "Warm up the account by posting consistently for 2 weeks before listing.",
            "Use an escrow service (Flippa, Escrow.com) — never accept PayPal for high-value sales.",
            "Transfer via the platform's official account transfer process.",
            "Include a 7-day handover period to teach the buyer your content strategy.",
        ],
        "valuation_note": (
            "Theme pages without revenue sell at $10-$40 per 1K followers. "
            "Monetised pages sell at 12-24× monthly revenue. "
            "Engagement rate is the biggest value multiplier."
        ),
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def list_available_niches() -> list[dict]:
    """Return all available niches with key metrics."""
    return [
        {
            "niche": key,
            "display": data["display"],
            "competition": data["competition"],
            "monetisation": data["monetisation_potential"],
            "best_platforms": data["best_platforms"],
        }
        for key, data in NICHE_DATA.items()
    ]
