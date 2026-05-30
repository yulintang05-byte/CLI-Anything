#!/usr/bin/env python3
"""Theme page niche database with conversion potential, competition level, and strategy notes."""

from typing import Optional


NICHE_DATABASE = {
    "luxury_lifestyle": {
        "name": "Luxury Lifestyle",
        "description": "High-end cars, yachts, mansions, private jets, watches",
        "monetization": ["affiliate_links", "sponsored_posts", "digital_products", "dropshipping"],
        "competition": "medium",
        "conversion_potential": "very_high",
        "avg_cpm_usd": 12.5,
        "target_audience": "aspirational 18-35 male, finance professionals",
        "best_platforms": ["instagram", "tiktok", "youtube"],
        "content_mix": {
            "repost_curated": 60,
            "original_commentary": 20,
            "educational_facts": 15,
            "promotional": 5,
        },
        "growth_speed": "fast",
        "monetization_timeline_days": 90,
        "strategy_notes": (
            "Easiest to grow fast due to aspirational nature. "
            "Affiliate luxury goods (watches, cars) pay $50-500/sale. "
            "Build to 10K then approach luxury brands directly. "
            "Key hook: 'You've never seen anything like this' + extreme wealth content."
        ),
        "example_accounts": ["@luxurylistings", "@millionairemindset"],
        "hashtags": ["#luxury", "#rich", "#wealth", "#millionaire", "#lifestyle"],
    },
    "fitness_motivation": {
        "name": "Fitness & Motivation",
        "description": "Gym transformations, workout tips, body goals, motivation",
        "monetization": ["supplement_affiliate", "fitness_programs", "coaching", "apparel"],
        "competition": "very_high",
        "conversion_potential": "high",
        "avg_cpm_usd": 8.0,
        "target_audience": "18-35 both genders, health-conscious",
        "best_platforms": ["tiktok", "instagram", "youtube"],
        "content_mix": {
            "transformation_videos": 30,
            "workout_clips": 30,
            "motivational_quotes": 20,
            "educational_tips": 15,
            "promotional": 5,
        },
        "growth_speed": "medium",
        "monetization_timeline_days": 120,
        "strategy_notes": (
            "Very saturated — differentiate by sub-niching: "
            "'calisthenics for beginners', 'gym moms', '50+ fitness'. "
            "Supplement affiliates pay 10-30% commission. "
            "Custom workout programs ($27-97) convert extremely well. "
            "Use before/after transformation content for highest saves."
        ),
        "example_accounts": ["@gymshark", "@fitnesspage"],
        "hashtags": ["#fitness", "#gym", "#workout", "#fitnessmotivation", "#bodygoals"],
    },
    "quotes_mindset": {
        "name": "Quotes & Mindset",
        "description": "Motivational quotes, mindset shifts, success principles",
        "monetization": ["digital_products", "coaching", "affiliate_books", "sponsored_posts"],
        "competition": "very_high",
        "conversion_potential": "medium",
        "avg_cpm_usd": 4.0,
        "target_audience": "18-45 mixed, entrepreneurs, students",
        "best_platforms": ["instagram", "tiktok", "pinterest"],
        "content_mix": {
            "quote_graphics": 50,
            "video_quotes": 30,
            "storytime": 10,
            "promotional": 10,
        },
        "growth_speed": "slow",
        "monetization_timeline_days": 180,
        "strategy_notes": (
            "Extremely saturated. Only viable with unique aesthetic or sub-niche "
            "(stoicism, stoic-finance, female empowerment, etc.). "
            "Low CPM — monetize through digital products ($7-47 ebooks). "
            "Pair with business/finance content to increase CPM. "
            "Pinterest is underrated for this niche — high traffic, low competition."
        ),
        "example_accounts": ["@mindsetquotes", "@dailymotivation"],
        "hashtags": ["#motivation", "#mindset", "#quotes", "#success", "#inspiration"],
    },
    "finance_investing": {
        "name": "Finance & Investing",
        "description": "Stock market, crypto, personal finance, passive income, wealth building",
        "monetization": ["trading_affiliate", "courses", "newsletter", "sponsored_posts"],
        "competition": "high",
        "conversion_potential": "very_high",
        "avg_cpm_usd": 18.0,
        "target_audience": "22-45 male-skewed, income earners",
        "best_platforms": ["youtube", "tiktok", "instagram", "twitter"],
        "content_mix": {
            "educational_finance": 40,
            "news_commentary": 25,
            "tips_tricks": 20,
            "product_reviews": 10,
            "promotional": 5,
        },
        "growth_speed": "medium",
        "monetization_timeline_days": 90,
        "strategy_notes": (
            "Highest CPM of any theme page niche ($15-25). "
            "Trading/investing affiliate programs pay $50-200 per referral. "
            "Build email list from day 1 — finance audience converts on email 3x social. "
            "Create 'crash course' pinned video as lead magnet. "
            "Be careful with financial advice disclaimers. "
            "Stock/crypto hot takes go viral fast."
        ),
        "example_accounts": ["@financetok", "@investingwithrose"],
        "hashtags": ["#finance", "#investing", "#stockmarket", "#personalfinance", "#money"],
    },
    "food_recipes": {
        "name": "Food & Recipes",
        "description": "Quick recipes, cooking hacks, food porn, restaurant reviews",
        "monetization": ["cookbook", "cooking_courses", "kitchen_affiliate", "brand_deals"],
        "competition": "high",
        "conversion_potential": "high",
        "avg_cpm_usd": 7.0,
        "target_audience": "25-50 female-skewed, home cooks",
        "best_platforms": ["tiktok", "youtube", "instagram", "pinterest"],
        "content_mix": {
            "quick_recipes": 40,
            "cooking_hacks": 25,
            "food_reviews": 20,
            "product_features": 10,
            "promotional": 5,
        },
        "growth_speed": "fast",
        "monetization_timeline_days": 90,
        "strategy_notes": (
            "Evergreen niche with strong saves (algorithm loves saves). "
            "Sub-niches: 5-ingredient meals, air fryer, high-protein, budget meals. "
            "Amazon affiliate for kitchen products pays 3-8%. "
            "Self-published recipe books on Gumroad/Etsy convert well ($15-35). "
            "Hook formula: 'This [X] changed my [Y]' + satisfying food ASMR."
        ),
        "example_accounts": ["@foodtok", "@tasty"],
        "hashtags": ["#food", "#recipe", "#cooking", "#foodtok", "#easyrecipes"],
    },
    "travel": {
        "name": "Travel",
        "description": "Destinations, travel hacks, budget travel, luxury travel",
        "monetization": ["booking_affiliate", "credit_card_affiliate", "travel_guides", "brand_deals"],
        "competition": "medium",
        "conversion_potential": "very_high",
        "avg_cpm_usd": 9.0,
        "target_audience": "22-45 mixed, adventure seekers",
        "best_platforms": ["tiktok", "youtube", "instagram"],
        "content_mix": {
            "destination_content": 40,
            "travel_hacks": 25,
            "itineraries": 20,
            "gear_reviews": 10,
            "promotional": 5,
        },
        "growth_speed": "medium",
        "monetization_timeline_days": 120,
        "strategy_notes": (
            "Travel credit card affiliates pay $200-500 per approval — highest CPA of any niche. "
            "Booking.com/Hotels.com pay 4-8% commission. "
            "Create 'ultimate guide to X destination' as pinned content. "
            "Budget travel content gets 5x more engagement than luxury travel. "
            "Combine with finance angle: 'how I travel for free with points'."
        ),
        "example_accounts": ["@traveltok", "@budgettravel"],
        "hashtags": ["#travel", "#traveltok", "#wanderlust", "#travelgram", "#travelhacks"],
    },
    "pets_animals": {
        "name": "Pets & Animals",
        "description": "Cute pets, animal facts, pet care tips, funny animal clips",
        "monetization": ["pet_affiliate", "brand_deals", "digital_care_guides", "print_on_demand"],
        "competition": "medium",
        "conversion_potential": "medium",
        "avg_cpm_usd": 5.5,
        "target_audience": "all ages, pet owners",
        "best_platforms": ["tiktok", "instagram", "youtube"],
        "content_mix": {
            "cute_clips": 50,
            "care_tips": 25,
            "funny_compilations": 15,
            "product_reviews": 5,
            "promotional": 5,
        },
        "growth_speed": "very_fast",
        "monetization_timeline_days": 90,
        "strategy_notes": (
            "Easiest niche to grow organically — cute animal content is universally shared. "
            "Monetize with pet supply affiliates (Chewy 4%, Amazon 3%). "
            "Print-on-demand merch (mugs, shirts with cute animals) converts well. "
            "Build community angle: specific breed communities (French Bulldog owners, etc). "
            "Lowest effort content creation of any niche."
        ),
        "example_accounts": ["@dogsooftiktok", "@animalsdoingthings"],
        "hashtags": ["#pets", "#dogsoftiktok", "#catsoftiktok", "#animals", "#cute"],
    },
    "tech_gadgets": {
        "name": "Tech & Gadgets",
        "description": "Latest gadgets, tech reviews, productivity tools, AI news",
        "monetization": ["amazon_affiliate", "sponsored_reviews", "tech_courses", "newsletter"],
        "competition": "high",
        "conversion_potential": "very_high",
        "avg_cpm_usd": 14.0,
        "target_audience": "18-40 male-skewed, early adopters",
        "best_platforms": ["youtube", "tiktok", "twitter"],
        "content_mix": {
            "product_reviews": 35,
            "tech_news": 30,
            "tutorials": 20,
            "ai_tools": 10,
            "promotional": 5,
        },
        "growth_speed": "medium",
        "monetization_timeline_days": 60,
        "strategy_notes": (
            "AI/automation sub-niche is exploding — lowest competition, highest engagement in 2024. "
            "Amazon affiliate 3-8% on electronics + bonus for high volume. "
            "Tech companies pay premium for sponsored reviews ($500-5000). "
            "Create 'tools I use daily' roundup content for passive affiliate income. "
            "First-to-cover new AI tool releases = instant viral potential."
        ),
        "example_accounts": ["@techhacks", "@aitools"],
        "hashtags": ["#tech", "#gadgets", "#ai", "#technology", "#productivity"],
    },
    "beauty_skincare": {
        "name": "Beauty & Skincare",
        "description": "Makeup tutorials, skincare routines, product reviews, GRWM",
        "monetization": ["beauty_affiliate", "brand_deals", "own_products", "ugc_creator"],
        "competition": "very_high",
        "conversion_potential": "very_high",
        "avg_cpm_usd": 11.0,
        "target_audience": "16-35 female-skewed",
        "best_platforms": ["tiktok", "youtube", "instagram"],
        "content_mix": {
            "tutorials": 35,
            "product_reviews": 30,
            "grwm": 20,
            "skincare_education": 10,
            "promotional": 5,
        },
        "growth_speed": "fast",
        "monetization_timeline_days": 90,
        "strategy_notes": (
            "Sub-niche is critical: affordable beauty, clean beauty, dark skin tones, mature skin. "
            "Sephora/Ulta affiliate programs. Amazon storefront. LTK. "
            "UGC creator role for brands pays $100-500/video without needing a large following. "
            "Duet/stitch product launches = viral potential. "
            "'Get ready with me' format has 40% higher retention than tutorials."
        ),
        "example_accounts": ["@beautytok", "@glowwithava"],
        "hashtags": ["#beauty", "#skincare", "#makeup", "#grwm", "#skintok"],
    },
}


def get_niche(niche_key: str) -> Optional[dict]:
    """Get full niche data by key."""
    return NICHE_DATABASE.get(niche_key)


def list_niches(
    sort_by: str = "conversion_potential",
    min_competition: Optional[str] = None,
    platform: Optional[str] = None,
) -> list[dict]:
    """List niches filtered and sorted.

    Args:
        sort_by: conversion_potential | growth_speed | avg_cpm_usd | competition
        min_competition: filter out niches above this competition level
                         (low | medium | high | very_high)
        platform: filter to niches available on this platform

    Returns:
        List of niche dicts sorted by the specified metric
    """
    competition_rank = {"low": 0, "medium": 1, "high": 2, "very_high": 3}
    conversion_rank = {"low": 0, "medium": 1, "high": 2, "very_high": 3}
    growth_rank = {"slow": 0, "medium": 1, "fast": 2, "very_fast": 3}

    results = []
    for key, niche in NICHE_DATABASE.items():
        if platform and platform.lower() not in [p.lower() for p in niche.get("best_platforms", [])]:
            continue
        if min_competition:
            comp_val = competition_rank.get(niche.get("competition", "high"), 2)
            max_val = competition_rank.get(min_competition, 2)
            if comp_val > max_val:
                continue
        results.append({"key": key, **niche})

    if sort_by == "conversion_potential":
        results.sort(key=lambda x: conversion_rank.get(x.get("conversion_potential", "medium"), 0), reverse=True)
    elif sort_by == "growth_speed":
        results.sort(key=lambda x: growth_rank.get(x.get("growth_speed", "medium"), 0), reverse=True)
    elif sort_by == "avg_cpm_usd":
        results.sort(key=lambda x: x.get("avg_cpm_usd", 0), reverse=True)
    elif sort_by == "competition":
        results.sort(key=lambda x: competition_rank.get(x.get("competition", "high"), 2))

    return results


def search_niches(query: str) -> list[dict]:
    """Search niches by keyword."""
    query = query.lower()
    results = []
    for key, niche in NICHE_DATABASE.items():
        searchable = (
            niche.get("name", "")
            + " " + niche.get("description", "")
            + " " + " ".join(niche.get("hashtags", []))
        ).lower()
        if query in searchable:
            results.append({"key": key, **niche})
    return results
