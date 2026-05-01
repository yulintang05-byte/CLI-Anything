"""Theme page strategy engine — niches, conversion guides, and monetization.

A "theme page" (also called "niche page" or "fan page") aggregates and reposts
content around a specific theme (e.g., luxury cars, motivational quotes, travel).
They can grow to massive followings with minimal original content creation.

This module provides:
- Niche discovery and analysis
- Step-by-step conversion guides
- Niche-to-niche switching strategy
- Monetization methods per niche
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional


NICHES = {
    "luxury_lifestyle": {
        "name": "Luxury Lifestyle",
        "description": "Luxury cars, watches, jets, mansions, and high-end travel",
        "difficulty": "easy",
        "growth_speed": "very_fast",
        "monetization_potential": "very_high",
        "avg_monthly_revenue": "$2k–$20k",
        "content_sources": ["YouTube (no copyright)", "luxury brand accounts", "car shows", "Reddit"],
        "best_platforms": ["TikTok", "Instagram", "YouTube Shorts"],
        "target_audience": "Males 18–35, aspirational buyers, entrepreneurs",
        "content_formats": ["Car reveals", "Mansion tours", "Watch collections", "Jet life vlogs"],
        "top_hashtags": ["#luxury", "#luxurylifestyle", "#supercar", "#watch", "#mansion"],
        "monetization": ["Brand sponsorships (luxury brands)", "Affiliate (car insurance, finance)", "Digital products (mindset guides)", "Paid promo posts"],
        "conversion_rate": "high",
        "notes": "Easiest niche to start — massive amount of royalty-free/repostable content available",
    },
    "motivation_mindset": {
        "name": "Motivation & Mindset",
        "description": "Motivational quotes, success stories, mindset clips, entrepreneur content",
        "difficulty": "easy",
        "growth_speed": "fast",
        "monetization_potential": "high",
        "avg_monthly_revenue": "$1k–$10k",
        "content_sources": ["Podcast clips", "YouTube speeches", "Books", "Reddit AMA posts"],
        "best_platforms": ["TikTok", "Instagram", "YouTube Shorts"],
        "target_audience": "18–34, students, early-career professionals, entrepreneurs",
        "content_formats": ["Quote graphics", "Speech clips", "Book summaries", "Success story breakdowns"],
        "top_hashtags": ["#motivation", "#mindset", "#success", "#entrepreneur", "#grindset"],
        "monetization": ["Digital products (eBooks, courses)", "Affiliate (books, apps)", "Sponsorships (supplements, productivity tools)", "Newsletter monetization"],
        "conversion_rate": "very_high",
        "notes": "Highest share rate of any niche — content goes viral organically",
    },
    "fitness_gym": {
        "name": "Fitness & Gym",
        "description": "Workout clips, transformations, nutrition tips, gym culture",
        "difficulty": "medium",
        "growth_speed": "fast",
        "monetization_potential": "very_high",
        "avg_monthly_revenue": "$3k–$30k",
        "content_sources": ["Repost with credit", "YouTube fitness channels", "Reddit r/fitness"],
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
        "target_audience": "18–35 all genders, health-conscious, gym-goers",
        "content_formats": ["Transformation videos", "Exercise tutorials", "Meal prep", "Gym fails/wins"],
        "top_hashtags": ["#fitness", "#gym", "#workout", "#transformation", "#gymtok"],
        "monetization": ["Supplement affiliate (20–30% commission)", "Fitness app affiliate", "Custom workout plans", "Coaching offers", "Merch"],
        "conversion_rate": "very_high",
        "notes": "Supplement affiliate alone can generate $5k+/month at 50k followers",
    },
    "finance_money": {
        "name": "Finance & Money",
        "description": "Investing tips, budgeting hacks, wealth building, passive income",
        "difficulty": "medium",
        "growth_speed": "medium",
        "monetization_potential": "extreme",
        "avg_monthly_revenue": "$5k–$50k",
        "content_sources": ["Finance YouTube channels", "Reddit r/personalfinance", "Financial news"],
        "best_platforms": ["YouTube", "TikTok", "Instagram"],
        "target_audience": "22–45, employed, debt-conscious, aspiring investors",
        "content_formats": ["Money tips", "Budget templates", "Investment breakdowns", "Debt payoff stories"],
        "top_hashtags": ["#finance", "#investing", "#moneytok", "#financetok", "#passiveincome"],
        "monetization": ["Financial product affiliate (credit cards, brokerages — $50–$500/signup)", "Digital courses", "Newsletter with sponsors", "Paid community"],
        "conversion_rate": "high",
        "notes": "Highest CPM on YouTube ($15–$50). Finance affiliate pays the most of any niche.",
    },
    "travel": {
        "name": "Travel",
        "description": "Destinations, travel hacks, budget travel, luxury travel experiences",
        "difficulty": "medium",
        "growth_speed": "medium",
        "monetization_potential": "high",
        "avg_monthly_revenue": "$2k–$15k",
        "content_sources": ["Travel YouTubers (with permission)", "Your own travel content", "Destination tourism boards"],
        "best_platforms": ["Instagram", "TikTok", "YouTube"],
        "target_audience": "25–45, middle-to-upper income, wanderlust-driven",
        "content_formats": ["Destination reveals", "Travel hacks", "Budget breakdowns", "Hotel reviews"],
        "top_hashtags": ["#travel", "#wanderlust", "#travelTikTok", "#budgettravel", "#travelhacks"],
        "monetization": ["Hotel/booking affiliate (Booking.com, Hotels.com)", "Credit card affiliate (travel cards)", "Destination sponsorships", "Presets/photo editing guides"],
        "conversion_rate": "medium",
        "notes": "Seasonal niche — plan content 2–3 months ahead for peak travel seasons",
    },
    "beauty_fashion": {
        "name": "Beauty & Fashion",
        "description": "Makeup tutorials, skincare routines, OOTD, fashion hauls",
        "difficulty": "medium",
        "growth_speed": "fast",
        "monetization_potential": "very_high",
        "avg_monthly_revenue": "$3k–$25k",
        "content_sources": ["Brand press content", "Product reviews", "Tutorials with permission"],
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
        "target_audience": "16–35 female primary, growing male audience",
        "content_formats": ["Get Ready With Me", "Dupes", "Product reviews", "Trend forecasts"],
        "top_hashtags": ["#beauty", "#GRWM", "#skincare", "#makeup", "#beautytok"],
        "monetization": ["LTK/Amazon affiliate", "Brand deals (biggest payer in beauty)", "Sephora/Ulta affiliate", "Subscription boxes affiliate"],
        "conversion_rate": "very_high",
        "notes": "Beauty brands pay premium rates — even micro influencers get $500–$5k/post",
    },
    "gaming": {
        "name": "Gaming",
        "description": "Gameplay highlights, gaming news, tutorials, gaming culture",
        "difficulty": "high",
        "growth_speed": "medium",
        "monetization_potential": "high",
        "avg_monthly_revenue": "$1k–$20k",
        "content_sources": ["Own gameplay", "Clip submissions", "eSports coverage"],
        "best_platforms": ["YouTube", "TikTok", "Twitch clips"],
        "target_audience": "13–30 male primary",
        "content_formats": ["Gameplay clips", "Game reviews", "Gaming tutorials", "Gaming news"],
        "top_hashtags": ["#gaming", "#gamer", "#fyp", "#xbox", "#playstation"],
        "monetization": ["Gaming peripheral affiliate", "Discord paid community", "Sponsorships (energy drinks, chairs)", "Channel memberships"],
        "conversion_rate": "medium",
        "notes": "Highly competitive but deeply loyal audience — community is key",
    },
    "pets_animals": {
        "name": "Pets & Animals",
        "description": "Cute animals, pet care tips, funny pet videos",
        "difficulty": "easy",
        "growth_speed": "very_fast",
        "monetization_potential": "medium",
        "avg_monthly_revenue": "$500–$8k",
        "content_sources": ["Reddit r/aww", "Viral pet videos (with credit)", "Own pets"],
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
        "target_audience": "All ages, pet owners 25–55",
        "content_formats": ["Cute compilations", "Pet care tips", "Funny clips", "Before/after training"],
        "top_hashtags": ["#dogtok", "#catsoftiktok", "#petsoftiktok", "#animals", "#cute"],
        "monetization": ["Pet product affiliate", "Chewy/Petco affiliate", "Pet insurance affiliate", "Merch with pet themes"],
        "conversion_rate": "medium",
        "notes": "Easiest viral niche — but lower CPM. Great for building large audience quickly.",
    },
}

CONVERSION_GUIDE = {
    "steps": [
        {
            "step": 1,
            "title": "Choose Your Niche",
            "duration": "Day 1",
            "actions": [
                "Pick ONE niche from the profitable niches list",
                "Verify: Can you find 20+ pieces of postable content per day in this niche?",
                "Verify: Does this niche have buyers? (products, services, or affiliate offers exist)",
                "Commit to 90 days minimum — niches need time to compound",
            ],
            "tools": ["social-trends theme niches", "Google Trends", "TikTok search"],
            "common_mistakes": ["Choosing a niche you 'love' but has no monetization path", "Picking too broad a niche (e.g., 'food' vs 'healthy meal prep for busy moms')"],
        },
        {
            "step": 2,
            "title": "Set Up Your Accounts",
            "duration": "Day 1–2",
            "actions": [
                "Create accounts on TikTok + Instagram + YouTube (same username on all)",
                "Write niche-optimized bio using templates (run: social-trends optimize bio)",
                "Upload a clear profile photo (face or branded logo)",
                "Set up Linktree or Beacons.ai as your link-in-bio hub",
                "Connect all platforms to the link-in-bio tool",
            ],
            "tools": ["social-trends optimize bio", "Canva (graphics)", "Linktree/Beacons.ai"],
            "common_mistakes": ["Different usernames on different platforms", "Bio that talks about YOU instead of what you offer viewers"],
        },
        {
            "step": 3,
            "title": "Content Sourcing System",
            "duration": "Day 2–3",
            "actions": [
                "Create a folder system: /Pending, /Edited, /Posted, /Archive",
                "Set up content source feeds (Reddit, YouTube search, TikTok search)",
                "Download CapCut or similar free editor for quick edits",
                "Learn basic reposting rules: always credit original creator",
                "Build a 7-day content buffer before going live",
            ],
            "tools": ["CapCut", "SnapTik (TikTok downloader)", "4K Video Downloader (YouTube)", "Notion for content calendar"],
            "common_mistakes": ["Posting raw reposts without any added value", "Not crediting original creators (risk of strikes/bans)", "Running out of content after 3 days"],
        },
        {
            "step": 4,
            "title": "Add Value Layer",
            "duration": "Ongoing",
            "actions": [
                "Add text overlays: questions, commentary, or context",
                "Add your branding: watermark/logo in corner",
                "Write engaging captions with call-to-action",
                "Add trending sounds to silent videos",
                "Create original 'compilation' or 'ranking' formats",
            ],
            "tools": ["CapCut", "InShot", "Canva", "social-trends trends music (for trending sounds)"],
            "common_mistakes": ["Adding zero value — purely reposting kills reach long-term", "Inconsistent branding across posts"],
        },
        {
            "step": 5,
            "title": "Posting Strategy",
            "duration": "Day 3 onward",
            "actions": [
                "Post 1–3x per day on TikTok for first 30 days",
                "Post 1 Reel/day + 3–5 Stories on Instagram",
                "Post 3–5 Shorts/week on YouTube",
                "Use trending sounds (< 72 hours old) on TikTok",
                "Post at peak times (run: social-trends optimize schedule)",
                "Engage with every comment in first 2 hours",
            ],
            "tools": ["social-trends optimize schedule", "Later or Buffer for scheduling"],
            "common_mistakes": ["Posting randomly without a schedule", "Ignoring comments (algorithm punishes low engagement)"],
        },
        {
            "step": 6,
            "title": "Growth Acceleration (Day 30–90)",
            "duration": "Month 2–3",
            "actions": [
                "Double down on your top 3 performing content formats",
                "Duet/stitch trending creators in your niche for borrowed reach",
                "Engage with top 5 accounts in your niche daily (real comments)",
                "Cross-promote: put TikTok content on Reels and Shorts",
                "Start building email list from day 1 — platform-independent asset",
                "Test one new content format per week",
            ],
            "tools": ["social-trends trends all", "Beehiiv or ConvertKit (email)"],
            "common_mistakes": ["Quitting before the 90-day compound effect kicks in", "Not cross-posting across platforms"],
        },
        {
            "step": 7,
            "title": "Monetization (Day 60+)",
            "duration": "Month 2 onward",
            "actions": [
                "Join affiliate programs in your niche",
                "Start posting affiliate links in bio/link-in-bio",
                "Apply for TikTok Creator Fund / YouTube Partner Program",
                "DM brands for sponsorships once you hit 5k–10k followers",
                "Create and sell a simple digital product ($7–$47)",
                "Build a paid Discord/Telegram community",
            ],
            "tools": ["Amazon Associates", "ShareASale", "Impact (brand deals)", "Gumroad/Stan.store (digital products)"],
            "common_mistakes": ["Waiting until 100k followers to monetize — start at 1k", "Relying on one revenue stream"],
        },
    ],
    "timeline": {
        "day_1_7": "Setup, content sourcing system, first 7 posts",
        "day_8_30": "Consistency phase — post daily, learn your analytics",
        "day_31_60": "Optimization phase — double down on winners, cut losers",
        "day_61_90": "Growth phase — cross-posting, engagement strategy, first monetization",
        "day_90_plus": "Scale — multiple platforms, multiple revenue streams, delegation",
    },
    "reality_check": {
        "average_time_to_first_1k": "2–4 weeks with daily posting",
        "average_time_to_10k": "1–3 months",
        "average_time_to_100k": "3–12 months",
        "hours_per_day": "1–2 hours for sourcing, editing, posting, engaging",
        "success_rate": "~30% of accounts that post daily for 90 days reach 10k+ followers",
        "biggest_killer": "Inconsistency — most people quit before the algorithm learns their content",
    },
}

NICHE_CONVERSION_STRATEGIES = {
    "luxury_to_finance": {
        "from": "luxury_lifestyle",
        "to": "finance_money",
        "difficulty": "easy",
        "steps": [
            "Start mixing 'how they afford it' content into luxury posts",
            "Post: 'How [rich person] built their wealth' style videos",
            "Gradually shift to 'financial freedom unlocks luxury lifestyle' framing",
            "Add finance hashtags alongside luxury tags",
            "Pin a new 'finance' video to signal the pivot to algorithm",
        ],
        "transition_time": "4–6 weeks",
        "audience_retention": "60–70%",
    },
    "general_to_niche": {
        "from": "general",
        "to": "any_niche",
        "difficulty": "medium",
        "steps": [
            "Identify which niche content already performs best on your account",
            "Post 80% new niche content, 20% old content for 2 weeks",
            "Update bio to reflect the new niche",
            "Create a pinned 'welcome to the new focus' video",
            "Unfollow/re-engage with accounts in the new niche for algorithm signals",
        ],
        "transition_time": "3–4 weeks",
        "audience_retention": "40–60%",
    },
}


def list_niches(filter_type: str = "all") -> dict:
    niches = list(NICHES.values())

    if filter_type == "growing":
        niches = [n for n in niches if n["growth_speed"] in ("fast", "very_fast")]
    elif filter_type == "easy":
        niches = [n for n in niches if n["difficulty"] == "easy"]
    elif filter_type == "high_income":
        niches = [n for n in niches if n["monetization_potential"] in ("very_high", "extreme")]

    return {
        "filter": filter_type,
        "total": len(niches),
        "niches": [
            {
                "name": n["name"],
                "difficulty": n["difficulty"],
                "growth_speed": n["growth_speed"],
                "monetization_potential": n["monetization_potential"],
                "avg_monthly_revenue": n["avg_monthly_revenue"],
                "best_platforms": n["best_platforms"],
            }
            for n in niches
        ],
    }


def get_niche_strategy(niche: str, platform: str = "all") -> dict:
    niche_key = None
    for k, v in NICHES.items():
        if niche.lower() in k or k in niche.lower() or niche.lower() in v["name"].lower():
            niche_key = k
            break

    if not niche_key:
        return {
            "error": f"Niche '{niche}' not found. Run 'social-trends theme niches' to see available niches.",
            "available_niches": list(NICHES.keys()),
        }

    niche_data = NICHES[niche_key]
    strategy = {
        "niche": niche_data["name"],
        "platform": platform,
        "overview": niche_data,
        "quick_start": [
            f"1. Search '{niche_data['name'].lower()}' on TikTok — study top 20 posts",
            f"2. Set up accounts with bio keyword: '{niche_data['name'].lower()}'",
            f"3. Post from these sources: {', '.join(niche_data['content_sources'][:2])}",
            f"4. Use these hashtags from day 1: {', '.join(niche_data['top_hashtags'][:3])}",
            f"5. Start with this content format: {niche_data['content_formats'][0]}",
        ],
        "monetization_roadmap": [
            f"Week 1–4: Build audience with free value content",
            f"Month 2: Join affiliate programs — {niche_data['monetization'][0]}",
            f"Month 3: First sponsorship pitch at 5k–10k followers",
            f"Month 4+: Launch digital product — target ${niche_data['avg_monthly_revenue'].split('–')[0].replace('$', '').replace('k', '000')} monthly",
        ],
        "content_mix": {
            "educational": "40% — teach something valuable",
            "entertaining": "30% — funny, surprising, or emotional",
            "promotional": "20% — your offers/affiliate links",
            "community": "10% — questions, polls, replies",
        },
        "notes": niche_data.get("notes", ""),
    }

    if platform.lower() in ("tiktok", "youtube", "instagram"):
        strategy["platform_specific"] = {
            "is_best_platform": platform.title() in niche_data["best_platforms"],
            "recommendation": f"{'Great choice!' if platform.title() in niche_data['best_platforms'] else 'Consider also trying: ' + ', '.join(niche_data['best_platforms'][:2])}",
        }

    return strategy


def get_conversion_guide(from_niche: str | None = None, to_niche: str | None = None) -> dict:
    if from_niche and to_niche:
        key = f"{from_niche.lower().replace(' ', '_')}_to_{to_niche.lower().replace(' ', '_')}"
        specific = NICHE_CONVERSION_STRATEGIES.get(key)
        if specific:
            return {
                "type": "specific_conversion",
                "from": from_niche,
                "to": to_niche,
                **specific,
                "full_guide": CONVERSION_GUIDE,
            }

    return {
        "type": "general_conversion_guide",
        "from_niche": from_niche,
        "to_niche": to_niche,
        "guide": CONVERSION_GUIDE,
        "available_specific_conversions": list(NICHE_CONVERSION_STRATEGIES.keys()),
    }


def get_monetization_strategy(niche: str) -> dict:
    niche_key = None
    for k, v in NICHES.items():
        if niche.lower() in k or k in niche.lower() or niche.lower() in v["name"].lower():
            niche_key = k
            break

    if not niche_key:
        return {
            "error": f"Niche '{niche}' not found.",
            "available": list(NICHES.keys()),
        }

    niche_data = NICHES[niche_key]

    return {
        "niche": niche_data["name"],
        "avg_monthly_revenue": niche_data["avg_monthly_revenue"],
        "monetization_potential": niche_data["monetization_potential"],
        "revenue_streams": niche_data["monetization"],
        "follower_milestones": {
            "1k_followers": "Affiliate links in bio — start earning immediately",
            "5k_followers": "First brand deal pitch — expect $50–$500/post",
            "10k_followers": "TikTok Series monetization, first digital product launch",
            "50k_followers": "Consistent brand deals $500–$5k/post, paid community",
            "100k_followers": "Full-time income potential — $5k–$50k/month across streams",
        },
        "fastest_monetization": niche_data["monetization"][0],
        "highest_earner": niche_data["monetization"][-1] if len(niche_data["monetization"]) > 1 else niche_data["monetization"][0],
        "platform_revenue": {
            "tiktok": "Creator Fund ($0.02–$0.04/1k views) + TikTok Shop + brand deals",
            "youtube": f"AdSense (${15 if 'finance' in niche_key else 5}–${50 if 'finance' in niche_key else 15}/1k views) + memberships + super thanks",
            "instagram": "Brand deals + affiliate + Instagram Subscriptions + badges in Live",
        },
    }
