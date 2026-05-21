"""Theme page conversion system — creation guide, monetization, and optimization."""

from typing import Optional

# Proven theme page niches ranked by monetization potential
NICHES = {
    "luxury_lifestyle": {
        "description": "Expensive cars, watches, mansions, private jets",
        "monetization": ["brand deals", "dropshipping", "affiliate (Amazon, eBay luxury)"],
        "avg_rpm": "$8-25 CPM",
        "competition": "high",
        "growth_speed": "fast",
        "content_types": ["repost viral clips", "compilations", "aspirational quotes"],
    },
    "fitness_motivation": {
        "description": "Workout videos, body transformations, nutrition tips",
        "monetization": ["supplement affiliates", "fitness programs", "merch"],
        "avg_rpm": "$5-15 CPM",
        "competition": "very high",
        "growth_speed": "moderate",
        "content_types": ["before/after", "workout clips", "motivation quotes"],
    },
    "finance_money": {
        "description": "Investing, crypto, side hustles, financial tips",
        "monetization": ["course sales", "affiliate (Robinhood, Coinbase)", "consulting"],
        "avg_rpm": "$15-50 CPM",
        "competition": "high",
        "growth_speed": "moderate",
        "content_types": ["tips & tricks", "case studies", "news commentary"],
    },
    "pets": {
        "description": "Cute/funny animal videos",
        "monetization": ["pet product affiliates", "merch", "sponsorships"],
        "avg_rpm": "$3-8 CPM",
        "competition": "moderate",
        "growth_speed": "very fast",
        "content_types": ["viral animal clips", "compilations", "memes"],
    },
    "food": {
        "description": "Recipes, restaurant reviews, food porn",
        "monetization": ["kitchen product affiliates", "food delivery partnerships", "cookbooks"],
        "avg_rpm": "$4-12 CPM",
        "competition": "high",
        "growth_speed": "fast",
        "content_types": ["recipes", "ASMR cooking", "taste tests"],
    },
    "relationships": {
        "description": "Dating tips, couple goals, relationship advice",
        "monetization": ["dating app affiliates", "coaching", "digital products"],
        "avg_rpm": "$4-10 CPM",
        "competition": "moderate",
        "growth_speed": "fast",
        "content_types": ["tips", "storytime", "couple content"],
    },
    "tech": {
        "description": "Gadgets, software, AI tools, reviews",
        "monetization": ["tech affiliate (Amazon, Best Buy)", "sponsorships", "courses"],
        "avg_rpm": "$10-30 CPM",
        "competition": "high",
        "growth_speed": "moderate",
        "content_types": ["reviews", "tutorials", "news"],
    },
    "mindset_motivation": {
        "description": "Self-improvement, productivity, success mindset",
        "monetization": ["course sales", "book affiliates", "coaching"],
        "avg_rpm": "$6-18 CPM",
        "competition": "very high",
        "growth_speed": "moderate",
        "content_types": ["quote edits", "speech clips", "tips"],
    },
    "beauty_fashion": {
        "description": "Makeup tutorials, outfits, style tips",
        "monetization": ["beauty affiliates (LTK, Sephora)", "brand deals", "merch"],
        "avg_rpm": "$5-15 CPM",
        "competition": "very high",
        "growth_speed": "fast",
        "content_types": ["tutorials", "hauls", "GRWM"],
    },
    "travel": {
        "description": "Destinations, travel hacks, vlogs",
        "monetization": ["hotel affiliates (Booking.com)", "tour partnerships", "presets"],
        "avg_rpm": "$8-20 CPM",
        "competition": "high",
        "growth_speed": "moderate",
        "content_types": ["destination clips", "travel hacks", "vlogs"],
    },
}

PLATFORM_STRATEGIES = {
    "tiktok": {
        "algorithm": "Content-first — TikTok shows content to non-followers first via FYP.",
        "key_metrics": ["completion rate", "shares", "watch time"],
        "growth_strategy": [
            "Post 1-3x/day in the first 60 days.",
            "Use trending sounds within 24-48 hours of them trending.",
            "Engage with the top 5 posts in your niche daily (genuine comments).",
            "Stitch or duet viral videos with your own take.",
            "Use the 3-second hook rule — grab attention instantly.",
        ],
        "theme_page_tips": [
            "Repost viral content with your own overlay/edit + original commentary.",
            "Build a recognizable visual brand (color palette, font, watermark).",
            "Use a consistent posting time — TikTok rewards accounts with predictable schedules.",
            "Create a series format (e.g., 'Day X of...') to drive return visits.",
        ],
        "conversion_cta": "Put link in bio, say 'link in bio' in video and caption.",
    },
    "youtube": {
        "algorithm": "Search + Suggested — keywords matter as much as thumbnails.",
        "key_metrics": ["click-through rate", "average view duration", "session time"],
        "growth_strategy": [
            "Target 'low competition, high intent' keywords.",
            "Create Shorts to feed subscribers to long-form content.",
            "Post long-form 2-3x/week, Shorts daily.",
            "Study competitors' most-viewed videos and make better versions.",
            "Build playlists to chain autoplay and extend session time.",
        ],
        "theme_page_tips": [
            "Curate and add commentary to viral clips (Fair Use compilations).",
            "Build 'best of' compilations in your niche.",
            "Always add a brand watermark and consistent thumbnail style.",
            "End every video with a pinned comment asking a question.",
        ],
        "conversion_cta": "Add links to description, pinned comment, and end screen cards.",
    },
    "instagram": {
        "algorithm": "Relationship + Relevance — engagement from existing followers boosts reach.",
        "key_metrics": ["saves", "shares", "profile visits"],
        "growth_strategy": [
            "Post Reels 5-7x/week for reach; carousel posts for saves.",
            "Use location tags on posts for local discoverability.",
            "Engage in Story polls, questions, and quizzes for algorithm signals.",
            "Collaborate with accounts in your niche via collabs posts.",
        ],
        "theme_page_tips": [
            "Maintain a cohesive grid aesthetic — use the same filter/preset.",
            "Watermark all reposts with your handle.",
            "Always credit original creators to avoid strikes.",
            "Use carousel posts for 'swipe' engagement.",
        ],
        "conversion_cta": "Use link-in-bio tools (Linktree, Stan Store). Add swipe-up in Stories.",
    },
}

CONTENT_REPURPOSING_WORKFLOW = [
    "1. Find viral content (use trend scraper: `social-media trends fetch --platform all`)",
    "2. Download and trim to best 15-60 seconds.",
    "3. Add your watermark, brand colors, and optional text overlay.",
    "4. Record a short reaction/commentary clip (adds Fair Use protection).",
    "5. Upload to TikTok with trending sound + 5 hashtags.",
    "6. Cross-post to YouTube Shorts and Instagram Reels.",
    "7. Track performance at 24h and 48h — boost top performers.",
]

MONETIZATION_MILESTONES = {
    "tiktok": {
        "1k_followers": "Unlock TikTok LIVE and gifts.",
        "10k_followers": "Brand deal outreach begins. Aim for $50-200/post.",
        "50k_followers": "TikTok Creator Fund ($20-40/month at this stage).",
        "100k_followers": "Serious brand deals ($500-2000/post). Apply for TikTok Series.",
        "500k_followers": "$2000-10000/post for brand deals. Launch your own product.",
        "1m_followers": "Full monetization: brand deals, merchandise, courses, events.",
    },
    "youtube": {
        "500_subscribers": "Apply for YouTube Partner Program (needs 3000 watch hours too).",
        "1000_subscribers": "Monetization eligible (with 4000 watch hours). Earn $1-5 RPM.",
        "10k_subscribers": "Significant ad revenue + brand deal outreach.",
        "100k_subscribers": "$500-5000/video from ads. Major brand deals.",
        "1m_subscribers": "Full monetization: ads, memberships, Super Thanks, sponsorships.",
    },
}


def get_niche_analysis(niche: str) -> dict:
    """Return detailed analysis and strategy for a specific niche."""
    key = niche.lower().replace(" ", "_")
    niche_data = NICHES.get(key)

    if not niche_data:
        # Fuzzy match
        for k, v in NICHES.items():
            if niche.lower() in k or any(niche.lower() in word for word in k.split("_")):
                niche_data = v
                key = k
                break

    if not niche_data:
        return {
            "error": f"Niche '{niche}' not in database.",
            "available_niches": list(NICHES.keys()),
        }

    return {
        "niche": key,
        **niche_data,
        "recommended_platforms": _recommend_platforms(niche_data),
        "90_day_roadmap": _build_roadmap(key, niche_data),
        "content_calendar": _build_content_calendar(niche_data),
    }


def _recommend_platforms(niche_data: dict) -> list[str]:
    content_types = niche_data.get("content_types", [])
    visual_heavy = any(t in str(content_types).lower() for t in ["video", "clip", "visual", "asmr", "tutorial"])
    if visual_heavy:
        return ["tiktok", "youtube_shorts", "instagram_reels"]
    return ["tiktok", "instagram", "youtube"]


def _build_roadmap(niche: str, niche_data: dict) -> list[str]:
    return [
        f"Week 1-2: Set up accounts on TikTok, YouTube Shorts, Instagram Reels with consistent branding.",
        f"Week 2-4: Post 2x/day on TikTok, daily on Shorts/Reels. Focus on {niche_data['content_types'][0]}.",
        f"Month 2: Identify top 3 performing content formats. Double down on winners.",
        f"Month 2-3: Reach out to micro-brands for first sponsorship ($25-100/post).",
        f"Month 3: Launch affiliate link in bio ({niche_data['monetization'][0] if niche_data['monetization'] else 'relevant products'}).",
        f"Month 3+: Build email list via lead magnet to own your audience.",
    ]


def _build_content_calendar(niche_data: dict) -> dict:
    types = niche_data.get("content_types", ["content"])
    return {
        "monday": f"{types[0]} — start week strong with your best content type",
        "tuesday": "Trending sound + hashtag challenge content",
        "wednesday": f"{types[1] if len(types) > 1 else types[0]} — mid-week engagement post",
        "thursday": "Educational/informational post in your niche",
        "friday": "Viral/entertainment post (highest share potential day)",
        "saturday": "Behind-the-scenes or personal connection content",
        "sunday": f"Recap/compilation or {types[-1]} post",
    }


def get_platform_strategy(platform: str) -> dict:
    """Return full strategy for a specific platform."""
    strategy = PLATFORM_STRATEGIES.get(platform.lower())
    if not strategy:
        return {
            "error": f"Platform '{platform}' not supported.",
            "supported": list(PLATFORM_STRATEGIES.keys()),
        }
    return {
        "platform": platform,
        **strategy,
        "content_repurposing_workflow": CONTENT_REPURPOSING_WORKFLOW,
        "monetization_milestones": MONETIZATION_MILESTONES.get(platform.lower(), {}),
    }


def get_conversion_optimization(
    platform: str,
    current_conversion_rate: Optional[float] = None,
    goal: str = "sales",
) -> dict:
    """Return conversion rate optimization tactics for a theme page."""
    base = PLATFORM_STRATEGIES.get(platform.lower(), {})
    cta = base.get("conversion_cta", "Add link in bio.")

    tactics = {
        "sales": [
            "Lead with the problem, not the product — show the pain point first.",
            "Use social proof: 'X people bought this' or 'sold out 3x'.",
            "Create urgency: 'Only available this week' or 'Price going up'.",
            "Add a testimonial or before/after as a pinned post.",
            "Price anchor: show original price crossed out vs. your affiliate link.",
        ],
        "follows": [
            "End every video with a direct 'follow for more X' CTA.",
            "Create serialized content: 'Part 1 of 7 — follow to see the rest'.",
            "Pin a 'New here? Start here' video to profile.",
            "Collaborate with similar accounts for shoutout exchanges.",
        ],
        "email_signups": [
            "Offer a free lead magnet (checklist, template, mini-course).",
            "Tease the lead magnet in video: 'I have a free [X] in my bio'.",
            "Use a bridge page (not direct affiliate) to capture emails first.",
            "Post a story poll then DM participants with the freebie link.",
        ],
        "affiliate_clicks": [
            "Create 'honest review' content — authenticity drives clicks.",
            "Do a comparison video: product A vs. B (with your affiliate link for winner).",
            "Use a short domain or link-in-bio tool (Linktree, Stan Store).",
            "Say the product name on screen — hearing + reading increases recall.",
        ],
    }

    result = {
        "platform": platform,
        "goal": goal,
        "cta_placement": cta,
        "conversion_tactics": tactics.get(goal, tactics["sales"]),
        "funnel_stages": [
            "Awareness → Hook (first 3 seconds of video)",
            "Interest → Content body (deliver value)",
            "Desire → Social proof / demonstration",
            "Action → Clear CTA at end + bio link",
        ],
    }

    if current_conversion_rate is not None:
        if current_conversion_rate < 0.5:
            result["diagnosis"] = "Very low conversion. Focus on CTA clarity and bio link optimization."
        elif current_conversion_rate < 2.0:
            result["diagnosis"] = "Below average. Test different CTAs and landing pages."
        elif current_conversion_rate < 5.0:
            result["diagnosis"] = "Average. A/B test your hook and CTA timing."
        else:
            result["diagnosis"] = "Good conversion rate. Scale with paid promotion."

    return result


def list_all_niches() -> list[dict]:
    return [
        {
            "niche": k,
            "description": v["description"],
            "monetization": v["monetization"],
            "competition": v["competition"],
            "growth_speed": v["growth_speed"],
        }
        for k, v in NICHES.items()
    ]
