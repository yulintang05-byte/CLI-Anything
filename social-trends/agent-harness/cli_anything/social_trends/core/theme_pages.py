"""Theme page creation, conversion, and monetisation strategies.

A theme page is a niche-focused account that curates, reposts, or
produces content around a single topic (e.g. luxury cars, cute animals,
fitness motivation) rather than a personal brand.

This module provides:
- A complete guide to starting and converting theme pages
- Niche selection with monetisation potential scores
- Content sourcing and reposting strategies (legally)
- Conversion tactics (turning followers into buyers)
- Monetisation blueprints per niche
- 30-day content calendars
"""

from __future__ import annotations
from typing import Literal

NicheKey = Literal[
    "luxury", "fitness", "food", "animals", "travel", "quotes",
    "fashion", "beauty", "gaming", "crypto", "cars", "nature",
    "comedy", "relationship", "business", "education", "celebrity",
]

# Niche data: monetisation potential, best platform, audience size, competitiveness
NICHE_DATA: dict[str, dict] = {
    "luxury": {
        "monetisation_potential": 10,
        "best_platforms": ["Instagram", "TikTok", "YouTube"],
        "audience_size": "Massive",
        "competition": "High",
        "avg_rpm": "$15-40",
        "top_monetisation": ["Luxury brand deals", "Affiliate (Amazon luxury)", "NFT/crypto communities"],
        "content_types": ["Mansion tours", "Supercar spotting", "Yacht/jet content", "Lifestyle clips"],
        "content_sources": ["YouTube (repost with credit)", "Reddit r/ultraexpensive", "Car shows", "Instagram pages"],
    },
    "fitness": {
        "monetisation_potential": 9,
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
        "audience_size": "Massive",
        "competition": "Very High",
        "avg_rpm": "$8-25",
        "top_monetisation": ["Supplement affiliates", "Workout programs", "Gym equipment affiliate", "Brand deals"],
        "content_types": ["Transformation videos", "Workout clips", "Nutrition tips", "Gym motivation"],
        "content_sources": ["User submissions", "YouTube creators (with permission)", "Reddit r/progresspics"],
    },
    "food": {
        "monetisation_potential": 8,
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
        "audience_size": "Massive",
        "competition": "High",
        "avg_rpm": "$5-15",
        "top_monetisation": ["Restaurant deals", "Delivery app affiliates", "Cookware affiliate", "Recipe ebooks"],
        "content_types": ["Restaurant reviews", "Recipe clips", "Food hacks", "Mukbang"],
        "content_sources": ["Creator submissions (DM for rights)", "Local restaurant visits", "UGC"],
    },
    "animals": {
        "monetisation_potential": 7,
        "best_platforms": ["TikTok", "Instagram", "YouTube Shorts"],
        "audience_size": "Massive",
        "competition": "Medium",
        "avg_rpm": "$3-10",
        "top_monetisation": ["Pet supply affiliates", "Brand deals (pet brands)", "Merch (cute designs)"],
        "content_types": ["Cute pet clips", "Animal rescues", "Wild animal facts", "Pet reactions"],
        "content_sources": ["Reddit r/aww, r/veryangrydog", "Creator UGC submissions", "Shelter partnerships"],
    },
    "travel": {
        "monetisation_potential": 9,
        "best_platforms": ["Instagram", "YouTube", "TikTok"],
        "audience_size": "Large",
        "competition": "High",
        "avg_rpm": "$10-30",
        "top_monetisation": ["Hotel/booking affiliate", "Travel card affiliates", "Tourism board deals"],
        "content_types": ["Destination reels", "Travel hacks", "Budget vs luxury", "Hidden gems"],
        "content_sources": ["YouTube (repost with credit)", "Tourism board media kits", "Hotel partnerships"],
    },
    "quotes": {
        "monetisation_potential": 6,
        "best_platforms": ["Instagram", "TikTok", "Pinterest"],
        "audience_size": "Massive",
        "competition": "Very High",
        "avg_rpm": "$1-5",
        "top_monetisation": ["Print-on-demand merch", "Digital journals/planners", "Coaching programs"],
        "content_types": ["Motivational quote cards", "Animated quotes", "Text on aesthetic backgrounds"],
        "content_sources": ["Public domain quotes", "Original writing", "Canva templates"],
    },
    "cars": {
        "monetisation_potential": 9,
        "best_platforms": ["Instagram", "YouTube", "TikTok"],
        "audience_size": "Large",
        "competition": "Medium",
        "avg_rpm": "$12-35",
        "top_monetisation": ["Car part affiliates", "Auto insurance affiliates", "Detailing product deals"],
        "content_types": ["Supercar spotting", "Drift videos", "Car reviews", "Before/after detailing"],
        "content_sources": ["YouTube spotters", "Reddit r/spotted", "Car meets", "Press release media"],
    },
    "gaming": {
        "monetisation_potential": 8,
        "best_platforms": ["YouTube", "TikTok", "Twitch"],
        "audience_size": "Massive",
        "competition": "Very High",
        "avg_rpm": "$5-20",
        "top_monetisation": ["Gaming peripheral affiliates", "Twitch donations", "Game key affiliates"],
        "content_types": ["Clip compilations", "Game tips", "New game trailers", "Funny fails"],
        "content_sources": ["Twitch clips", "Reddit r/gaming", "YouTube Shorts repurpose", "UGC"],
    },
    "crypto": {
        "monetisation_potential": 10,
        "best_platforms": ["Twitter/X", "YouTube", "TikTok"],
        "audience_size": "Large",
        "competition": "High",
        "avg_rpm": "$20-60",
        "top_monetisation": ["Exchange referrals", "Sponsored news posts", "Paid community/Discord"],
        "content_types": ["Price updates", "Project reviews", "Chart analysis clips", "News summaries"],
        "content_sources": ["CoinDesk", "Twitter/X aggregation", "Project press releases"],
    },
    "beauty": {
        "monetisation_potential": 9,
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
        "audience_size": "Massive",
        "competition": "Very High",
        "avg_rpm": "$8-25",
        "top_monetisation": ["Sephora/Ulta affiliates", "Beauty brand deals", "Amazon storefront"],
        "content_types": ["Makeup tutorials", "Skincare routines", "Product reviews", "GRWM"],
        "content_sources": ["Creator submissions", "Brand-provided samples", "Drugstore hauls"],
    },
    "business": {
        "monetisation_potential": 10,
        "best_platforms": ["LinkedIn", "YouTube", "TikTok"],
        "audience_size": "Medium",
        "competition": "Medium",
        "avg_rpm": "$15-50",
        "top_monetisation": ["Online courses", "Coaching/consulting", "SaaS tool affiliates"],
        "content_types": ["Business tips", "Entrepreneur stories", "Side hustle ideas", "Case studies"],
        "content_sources": ["Original research", "News aggregation", "Interview clips"],
    },
    "fashion": {
        "monetisation_potential": 8,
        "best_platforms": ["Instagram", "TikTok", "Pinterest"],
        "audience_size": "Massive",
        "competition": "Very High",
        "avg_rpm": "$6-20",
        "top_monetisation": ["SHEIN/Revolve affiliate", "Amazon storefront", "Brand collaborations"],
        "content_types": ["OOTD", "Outfit inspiration", "Trend forecasting", "Fashion week clips"],
        "content_sources": ["Brand lookbooks", "Creator UGC", "Street style shoots"],
    },
    "nature": {
        "monetisation_potential": 6,
        "best_platforms": ["YouTube", "Instagram", "TikTok"],
        "audience_size": "Large",
        "competition": "Low",
        "avg_rpm": "$5-12",
        "top_monetisation": ["Eco brand deals", "National park tourism boards", "Print merch"],
        "content_types": ["Drone footage", "Wildlife clips", "Nature facts", "Timelapse"],
        "content_sources": ["NASA public domain", "National Geographic licensed", "Creative Commons"],
    },
    "education": {
        "monetisation_potential": 8,
        "best_platforms": ["YouTube", "TikTok", "Instagram"],
        "audience_size": "Large",
        "competition": "Medium",
        "avg_rpm": "$10-30",
        "top_monetisation": ["Online courses (Teachable/Gumroad)", "Book affiliates", "SaaS referrals"],
        "content_types": ["Facts/trivia", "Study tips", "Explainer clips", "Book summaries"],
        "content_sources": ["Wikipedia research", "Academic papers", "Original content"],
    },
    "relationship": {
        "monetisation_potential": 7,
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
        "audience_size": "Massive",
        "competition": "High",
        "avg_rpm": "$4-15",
        "top_monetisation": ["Dating app affiliates", "Coaching programs", "Ebook products"],
        "content_types": ["Dating tips", "Red flags/green flags", "Couple goals", "Storytime"],
        "content_sources": ["Original scripts", "Reddit r/AmITheAsshole", "UGC submissions"],
    },
    "celebrity": {
        "monetisation_potential": 7,
        "best_platforms": ["Instagram", "TikTok", "Twitter/X"],
        "audience_size": "Massive",
        "competition": "Very High",
        "avg_rpm": "$5-15",
        "top_monetisation": ["Fashion/beauty affiliate links", "News aggregator ads", "Sponsored posts"],
        "content_types": ["News updates", "Award show clips", "Interview highlights", "Drama updates"],
        "content_sources": ["Press release media", "Red carpet footage (licensed)", "YouTube interviews"],
    },
    "comedy": {
        "monetisation_potential": 7,
        "best_platforms": ["TikTok", "Instagram", "YouTube Shorts"],
        "audience_size": "Massive",
        "competition": "High",
        "avg_rpm": "$3-10",
        "top_monetisation": ["Merch", "Brand deals", "AdSense (YouTube)"],
        "content_types": ["Meme compilations", "Reaction videos", "Sketch clips", "Relatable content"],
        "content_sources": ["Reddit memes", "Twitter/X viral posts", "Original creation"],
    },
}

THEME_PAGE_GUIDE = {
    "what_is_theme_page": (
        "A theme page is a niche account that posts curated or original content around ONE "
        "specific topic — it is NOT a personal brand. The account is built around the niche, "
        "not you as a person. Examples: @luxurycars.daily, @fitnessmotivation.co, @petlovers."
    ),
    "advantages": [
        "Can grow faster than personal brands (no face required)",
        "Easier to sell/transfer (the niche IS the asset)",
        "Can run multiple simultaneously",
        "Content creation is faster (curation vs creation)",
        "More scalable — hire VAs to run accounts",
    ],
    "disadvantages": [
        "Harder to monetise than personal brands initially",
        "Content rights/copyright must be managed carefully",
        "Lower trust factor — audience doesn't know YOU",
        "Platform algorithm shifts can wipe growth overnight",
        "Requires large volume of content",
    ],
    "starting_steps": [
        "Step 1: Pick ONE niche with proven demand (use 'theme-pages guide --niche' for data)",
        "Step 2: Research top 5 accounts in that niche — study content format, hooks, hashtags",
        "Step 3: Create the account — optimise profile (name, bio, logo, link)",
        "Step 4: Source 30 days of content before launching (content bank)",
        "Step 5: Post 3-5x/day for first 30 days — quantity drives algorithm exposure",
        "Step 6: Engage: reply to comments, DM new followers, interact with niche content",
        "Step 7: At 1K followers — test monetisation (affiliate links in bio)",
        "Step 8: At 10K followers — pitch brands for $50-200 sponsored posts",
        "Step 9: At 100K followers — hire VA, diversify revenue, consider selling",
    ],
    "content_rights_rules": [
        "Always credit the original creator (tag their handle)",
        "DM creators for explicit permission before reposting high-quality content",
        "Use 'share' buttons where available (TikTok Duet/Repost, Instagram Share)",
        "Never claim others' content as your own",
        "Use royalty-free or Creative Commons content where possible",
        "Original content is always safest — even 30% original content protects the account",
    ],
}

CONVERSION_STRATEGIES = {
    "bio_conversion": [
        "Use a benefit-driven bio: 'Daily luxury inspo → free lifestyle guide 👇'",
        "Single clear CTA: one link, one ask",
        "Urgency or exclusivity: 'Join 50K+ luxury fans'",
    ],
    "content_conversion": [
        "CTA in every caption: 'Follow for daily [niche] content'",
        "Tease a 'free guide' or 'checklist' to drive link clicks",
        "Use last slide of carousels as a CTA card",
        "Add text overlay CTA to end of every video",
        "Pin a 'Welcome / How to work with us' post",
    ],
    "dms_conversion": [
        "Auto-DM new followers with a value message + soft offer",
        "Reply to story interactions with personalised messages",
        "Share exclusive offers/content via DMs to build intimacy",
    ],
    "funnel_structure": {
        "top_of_funnel": "Viral/entertainment content → mass reach",
        "middle_of_funnel": "Educational/value content → trust building",
        "bottom_of_funnel": "Testimonials, offers, scarcity → conversion",
        "ratio": "70% top + 20% middle + 10% bottom",
    },
    "email_list_building": [
        "Offer a free resource (guide, checklist, template) for email",
        "Use Beehiiv, ConvertKit, or MailerLite (free tiers available)",
        "Send weekly newsletter to own your audience outside the algorithm",
        "Gate premium content behind email signup",
    ],
}


def get_guide(niche: str = "") -> dict:
    """Return the complete theme page creation guide.

    Args:
        niche: Optional niche for tailored data (e.g. "luxury", "fitness").

    Returns:
        Dict with guide, steps, conversion strategies, and niche data.
    """
    result = {
        "guide": THEME_PAGE_GUIDE,
        "conversion_strategies": CONVERSION_STRATEGIES,
    }

    if niche:
        niche_lower = niche.lower()
        niche_info = NICHE_DATA.get(niche_lower)
        if niche_info:
            result["niche_data"] = {"niche": niche_lower, **niche_info}
        else:
            # Find closest match
            matches = [k for k in NICHE_DATA if niche_lower in k or k in niche_lower]
            if matches:
                result["niche_data"] = {"niche": matches[0], **NICHE_DATA[matches[0]]}
            else:
                result["niche_not_found"] = (
                    f"'{niche}' not in database. Available niches: {', '.join(NICHE_DATA.keys())}"
                )

    return result


def get_niche_rankings(sort_by: str = "monetisation_potential", top_n: int = 10) -> dict:
    """Rank niches by monetisation potential, competition, or audience size.

    Args:
        sort_by: Sort key — "monetisation_potential" or "competition".
        top_n: Number of results to return.

    Returns:
        Ranked list of niches with key metrics.
    """
    order_key = sort_by if sort_by == "monetisation_potential" else "monetisation_potential"
    sorted_niches = sorted(
        NICHE_DATA.items(),
        key=lambda x: x[1].get(order_key, 0),
        reverse=True,
    )

    rankings = []
    for rank, (niche, data) in enumerate(sorted_niches[:top_n], 1):
        rankings.append({
            "rank": rank,
            "niche": niche,
            "monetisation_potential": f"{data['monetisation_potential']}/10",
            "best_platforms": data["best_platforms"],
            "competition": data["competition"],
            "avg_rpm": data.get("avg_rpm", "N/A"),
            "top_monetisation": data["top_monetisation"][:2],
        })

    return {
        "sorted_by": sort_by,
        "total_niches": len(NICHE_DATA),
        "rankings": rankings,
    }


def get_monetisation_strategies(niche: str) -> dict:
    """Return monetisation blueprint for a niche.

    Args:
        niche: Content niche.

    Returns:
        Dict with monetisation methods, thresholds, and action plan.
    """
    niche_lower = niche.lower()
    data = NICHE_DATA.get(niche_lower)

    if not data:
        matches = [k for k in NICHE_DATA if niche_lower in k]
        if matches:
            data = NICHE_DATA[matches[0]]
            niche_lower = matches[0]
        else:
            return {
                "error": f"Niche '{niche}' not found",
                "available": list(NICHE_DATA.keys()),
            }

    return {
        "niche": niche_lower,
        "monetisation_potential": f"{data['monetisation_potential']}/10",
        "avg_rpm": data.get("avg_rpm", "N/A"),
        "monetisation_methods": data["top_monetisation"],
        "best_platforms": data["best_platforms"],
        "milestone_plan": {
            "0-1K followers": "Build content bank; post 3-5x/day; no monetisation yet",
            "1K-10K": "Add affiliate link in bio; test product placement; join creator programs",
            "10K-50K": "Pitch brands ($50-200/post); launch digital product ($7-27 offer)",
            "50K-100K": "Raise brand deal rates ($500-1500/post); launch course/coaching",
            "100K+": "Premium brand deals ($2K-10K+); consider selling account ($5K-50K+)",
        },
        "quick_wins": [
            f"Add {data['top_monetisation'][0]} affiliate link in bio TODAY",
            "Create a 'free guide' PDF to capture emails",
            "DM 5 brands in your niche offering a free collab post",
        ],
        "content_types": data["content_types"],
        "content_sources": data["content_sources"],
    }


def get_content_calendar(niche: str, platform: str = "tiktok", weeks: int = 4) -> dict:
    """Generate a content calendar for a theme page.

    Args:
        niche: Content niche.
        platform: Target platform.
        weeks: Number of weeks to plan.

    Returns:
        Dict with weekly content plan.
    """
    niche_lower = niche.lower()
    data = NICHE_DATA.get(niche_lower, {})
    content_types = data.get("content_types", ["Value post", "Trend post", "Promo post", "Engagement post"])

    freq_map = {
        "tiktok": 4,
        "youtube": 2,
        "instagram": 5,
    }
    posts_per_day = freq_map.get(platform, 3)

    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    calendar = []

    for week in range(1, weeks + 1):
        week_plan = {"week": week, "days": []}
        for day in DAYS:
            posts = []
            for post_num in range(min(posts_per_day, len(content_types))):
                content_type = content_types[post_num % len(content_types)]
                posts.append({
                    "post_number": post_num + 1,
                    "content_type": content_type,
                    "format": _suggest_format(platform, post_num),
                    "cta": _suggest_cta(post_num, week),
                })
            week_plan["days"].append({"day": day, "posts": posts})
        calendar.append(week_plan)

    return {
        "niche": niche,
        "platform": platform,
        "weeks": weeks,
        "posts_per_day": posts_per_day,
        "total_posts": posts_per_day * 7 * weeks,
        "calendar": calendar,
        "content_bank_needed": posts_per_day * 7 * weeks,
        "tip": (
            f"Batch-create {posts_per_day * 7} posts per week in one session. "
            "Schedule with Later, Buffer, or TikTok Scheduler."
        ),
    }


def _suggest_format(platform: str, index: int) -> str:
    formats = {
        "tiktok": ["Talking head (30s)", "Trending sound clip", "Text overlay video", "Duet/Stitch"],
        "youtube": ["Shorts (60s)", "Long-form (8-15min)", "Shorts (30s)", "Long-form (5-8min)"],
        "instagram": ["Reel (15-30s)", "Carousel (5-8 slides)", "Reel (30-60s)", "Single image", "Story series"],
    }
    options = formats.get(platform, ["Video clip", "Carousel", "Image post"])
    return options[index % len(options)]


def _suggest_cta(post_num: int, week: int) -> str:
    ctas = [
        "Follow for daily content",
        "Comment your thoughts below",
        "Save this for later",
        "Share with someone who needs this",
        "Click link in bio",
        "Tag a friend",
        "Like if you agree",
    ]
    return ctas[(post_num + week) % len(ctas)]
