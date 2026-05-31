"""Theme page intelligence — niche selection, curation, and conversion strategy.

A "theme page" is a social media account built around a specific topic
(fitness, cars, quotes, travel, pets, etc.) that curates content from
creators in that niche rather than creating original content from scratch.

"Converting" means turning followers/views into monetization:
  - Shoutout-for-pay (SFS/paid promo)
  - Affiliate marketing
  - Digital product sales
  - Brand sponsorships
  - Newsletter/email list building
  - Driving traffic to a Linktree/store

This module provides:
  - Niche scoring (profitability, competition, content availability)
  - Curation workflow (where to find content, how to repurpose legally)
  - Monetization roadmap by follower tier
  - Conversion funnel builder
  - Content calendar templates
"""

from datetime import datetime


NICHE_DATABASE = {
    "fitness": {
        "sub_niches": ["home workouts", "gym aesthetic", "calisthenics", "weight loss transformation", "girl gains"],
        "monetization_score": 9,
        "competition": "very_high",
        "content_availability": "very_high",
        "avg_cpm_usd": 8.50,
        "best_platforms": ["instagram", "tiktok", "youtube"],
        "affiliate_programs": ["MyProtein", "Gymshark", "Amazon fitness", "Whoop", "Beachbody"],
        "content_sources": ["YouTube (fair use clips)", "Reddit r/fitness", "Instagram reels reposts"],
        "hook_topics": ["transformations", "workout fails", "gym tips", "nutrition facts"],
    },
    "cars": {
        "sub_niches": ["supercars", "jdm", "muscle cars", "car mods", "car reviews"],
        "monetization_score": 8,
        "competition": "high",
        "content_availability": "high",
        "avg_cpm_usd": 12.00,
        "best_platforms": ["instagram", "tiktok", "youtube"],
        "affiliate_programs": ["Amazon auto parts", "RevZilla", "Advance Auto Parts"],
        "content_sources": ["YouTube clips", "car shows", "auto influencer reposts"],
        "hook_topics": ["supercars spotted", "insane builds", "price reveals", "vs comparisons"],
    },
    "motivational_quotes": {
        "sub_niches": ["hustle mindset", "self-improvement", "stoicism", "wealth mindset", "discipline"],
        "monetization_score": 6,
        "competition": "very_high",
        "content_availability": "very_high",
        "avg_cpm_usd": 3.50,
        "best_platforms": ["instagram", "tiktok"],
        "affiliate_programs": ["Audible", "Blinkist", "self-help books (Amazon)"],
        "content_sources": ["Canva quote graphics", "AI-generated voiceovers", "stock footage"],
        "hook_topics": ["controversial takes", "daily discipline", "rich mindset vs poor mindset"],
    },
    "travel": {
        "sub_niches": ["budget travel", "luxury travel", "solo female travel", "van life", "hidden gems"],
        "monetization_score": 8,
        "competition": "high",
        "content_availability": "high",
        "avg_cpm_usd": 10.00,
        "best_platforms": ["instagram", "youtube", "tiktok"],
        "affiliate_programs": ["Booking.com", "Airbnb", "Skyscanner", "GetYourGuide", "TripAdvisor"],
        "content_sources": ["Creative Commons footage", "travel YouTubers (with permission)", "Pexels/Unsplash"],
        "hook_topics": ["hidden destinations", "budget hacks", "travel fails", "flight deals"],
    },
    "food": {
        "sub_niches": ["restaurant reviews", "cooking hacks", "mukbang", "healthy recipes", "street food"],
        "monetization_score": 7,
        "competition": "high",
        "content_availability": "very_high",
        "avg_cpm_usd": 5.00,
        "best_platforms": ["tiktok", "instagram", "youtube"],
        "affiliate_programs": ["HelloFresh", "Home Chef", "Amazon kitchen", "DoorDash referral"],
        "content_sources": ["Restaurant-shared content (ask permission)", "cooking channels", "food festivals"],
        "hook_topics": ["weird food combos", "food hacks", "restaurant secrets", "price reactions"],
    },
    "luxury_lifestyle": {
        "sub_niches": ["watches", "yachts", "private jets", "mansions", "luxury brands"],
        "monetization_score": 9,
        "competition": "medium",
        "content_availability": "medium",
        "avg_cpm_usd": 15.00,
        "best_platforms": ["instagram", "youtube"],
        "affiliate_programs": ["Chrono24 (watches)", "luxury hotel affiliates", "Rakuten luxury"],
        "content_sources": ["YouTube tours", "press releases", "manufacturer media kits"],
        "hook_topics": ["price reveals", "billionaire habits", "affordable vs luxury", "unboxings"],
    },
    "pets": {
        "sub_niches": ["dogs", "cats", "exotic pets", "pet training", "cute compilations"],
        "monetization_score": 7,
        "competition": "high",
        "content_availability": "very_high",
        "avg_cpm_usd": 6.00,
        "best_platforms": ["tiktok", "instagram", "youtube"],
        "affiliate_programs": ["Chewy", "PetSmart", "BarkBox", "Amazon pet supplies"],
        "content_sources": ["Reddit r/aww", "Facebook groups (with permission)", "Twitter/X"],
        "hook_topics": ["animal reactions", "training wins/fails", "rescue stories", "cute compilations"],
    },
    "finance_crypto": {
        "sub_niches": ["personal finance", "stock picks", "crypto news", "real estate investing", "side hustles"],
        "monetization_score": 10,
        "competition": "high",
        "content_availability": "high",
        "avg_cpm_usd": 25.00,
        "best_platforms": ["youtube", "tiktok", "instagram"],
        "affiliate_programs": ["Coinbase", "Robinhood", "Webull", "Credit Karma", "NerdWallet"],
        "content_sources": ["Financial news clips", "earnings calls", "expert interview clips"],
        "hook_topics": ["money mistakes", "passive income", "market crashes", "get rich strategies"],
    },
    "gaming": {
        "sub_niches": ["fps clips", "speedruns", "gaming fails", "game reviews", "esports highlights"],
        "monetization_score": 7,
        "competition": "very_high",
        "content_availability": "very_high",
        "avg_cpm_usd": 4.00,
        "best_platforms": ["youtube", "tiktok"],
        "affiliate_programs": ["Amazon gaming gear", "Razer affiliate", "G2A", "Humble Bundle"],
        "content_sources": ["Twitch clips (with permission)", "YouTube gameplay", "esports official content"],
        "hook_topics": ["insane plays", "game glitches", "pro player moments", "world records"],
    },
    "fashion": {
        "sub_niches": ["streetwear", "thrift flips", "outfit inspiration", "sneakers", "designer hauls"],
        "monetization_score": 8,
        "competition": "very_high",
        "content_availability": "high",
        "avg_cpm_usd": 7.00,
        "best_platforms": ["instagram", "tiktok"],
        "affiliate_programs": ["ASOS", "Revolve", "Depop referral", "StockX", "LTK (LikeToKnowIt)"],
        "content_sources": ["Brand lookbooks", "runway clips", "thrift/haul videos"],
        "hook_topics": ["outfit dupes", "thrift finds", "style transformations", "budget vs luxury"],
    },
}

MONETIZATION_ROADMAP = {
    "0–1K": {
        "label": "Foundation Phase",
        "focus": "Build consistent posting habit and define niche",
        "monetization": [
            "No direct monetization yet — focus on quality and growth",
            "Start building email list from day 1 (free Mailchimp)",
            "Set up affiliate links NOW so they're ready when traffic comes",
            "Document your journey — meta-content performs well",
        ],
        "kpis": ["Follower growth rate", "Average views per post", "Profile visit to follow rate"],
    },
    "1K–5K": {
        "label": "Early Monetization Phase",
        "focus": "Prove engagement, start affiliate testing",
        "monetization": [
            "Affiliate marketing (Amazon Associates, niche-specific programs)",
            "Micro-shoutouts ($25–$100/post depending on engagement)",
            "Sell a low-ticket digital product ($7–$27 ebook, preset pack, template)",
            "TikTok Creator Fund (1K+ required — low payout but signals legitimacy)",
        ],
        "kpis": ["Engagement rate (aim for >3%)", "Link in bio click rate", "Email list size"],
    },
    "5K–25K": {
        "label": "Scaling Phase",
        "focus": "Systematize content, build multiple income streams",
        "monetization": [
            "Paid shoutouts ($100–$500/post)",
            "Brand micro-deals ($250–$1K/post for micro-influencer rates)",
            "Mid-ticket products ($27–$97) — courses, coaching sessions",
            "Newsletter monetization — sponsored issues",
            "Instagram/TikTok Subscriptions (if eligible)",
        ],
        "kpis": ["Revenue per post", "Email open rate", "Avg shoutout inquiry/week"],
    },
    "25K–100K": {
        "label": "Authority Phase",
        "focus": "Brand partnerships, premium offers",
        "monetization": [
            "Macro brand deals ($1K–$10K/post)",
            "High-ticket offers ($500–$2K coaching, masterminds)",
            "Affiliate revenue at scale ($2K–$10K/month)",
            "YouTube monetization (if cross-posting Shorts → long-form)",
            "Merchandise via Printify/Printful (zero upfront cost)",
        ],
        "kpis": ["Monthly recurring revenue", "Sponsorship close rate", "Community retention"],
    },
    "100K+": {
        "label": "Business Phase",
        "focus": "Build a media company, not just an account",
        "monetization": [
            "Premium brand exclusives ($10K–$100K+ deals)",
            "Own product line (supplements, apparel, SaaS tool in niche)",
            "Speaking engagements and appearances",
            "Agency: manage other theme pages, charge management fee",
            "Sell the account (theme pages sell for 12–36x monthly revenue)",
        ],
        "kpis": ["Brand deal pipeline value", "LTV per customer", "Multiple income streams count"],
    },
}

CURATION_WORKFLOW = {
    "legal_guidelines": [
        "Always credit the original creator — tag them in caption or overlay",
        "Download and re-upload (don't just repost) to avoid link attrition",
        "Add value: commentary, reaction text, compilation editing, or narration",
        "For YouTube content: clips under 30 seconds generally qualify as fair use commentary",
        "For music: use royalty-free audio or TikTok/Reels licensed library sounds",
        "DM creators to ask permission — many say yes and appreciate the exposure",
        "Meme/viral clip pages have a gray area — transformative use and crediting help",
    ],
    "content_sources": {
        "free_no_permission_needed": [
            "Pexels (CC0 video and photos)",
            "Pixabay (CC0)",
            "Unsplash (CC0 photos)",
            "YouTube Creative Commons filter",
            "NASA/government public domain content",
            "CapCut templates (platform-native remixing)",
        ],
        "permission_recommended": [
            "Reddit top posts (link in comments, credit OP)",
            "Twitter/X viral clips (DM for permission)",
            "Instagram creators (ask to reshare, tag them)",
            "TikTok stitches and duets (built-in credit mechanism)",
        ],
        "paid_licensed": [
            "Storyblocks ($15/mo unlimited stock video)",
            "Envato Elements ($16.50/mo)",
            "Artgrid ($99/yr)",
        ],
    },
    "tools": {
        "repurposing": [
            "CapCut — remove watermarks, add captions, trending templates",
            "Canva — quote graphics, carousels, thumbnail design",
            "Descript — AI captions, audio cleanup, B-roll matching",
            "OpusClip — AI clip extraction from long videos",
        ],
        "scheduling": [
            "Buffer (free tier: 3 channels)",
            "Later (free tier: 14 posts/month per channel)",
            "Metricool (free tier: 1 brand)",
            "TikTok/Instagram native scheduling (in-app, free)",
        ],
        "analytics": [
            "TikTok Analytics (in-app, free)",
            "YouTube Studio (free)",
            "Instagram Insights (free)",
            "Social Blade (competitive benchmarking, free)",
            "Phlanx (engagement rate calculator, free)",
        ],
    },
}

CONVERSION_FUNNEL = {
    "awareness": {
        "goal": "Get content on Explore/FYP/trending",
        "tactics": [
            "Use trending audio/sounds",
            "Trending hashtags + niche hashtags mix",
            "Post at peak hours for your audience",
            "Hook in first 1 second (text overlay or visual pattern interrupt)",
        ],
    },
    "interest": {
        "goal": "Get them to follow and visit profile",
        "tactics": [
            "End video with a follow CTA ('Follow for more [niche] content')",
            "Pin best 3 posts to show value immediately",
            "Consistent aesthetic makes profile look professional",
            "Story highlights act as a 'website' for new visitors",
        ],
    },
    "desire": {
        "goal": "Build trust to the point of click or purchase",
        "tactics": [
            "Post testimonials/social proof (screenshots, DMs)",
            "Share results and transformations",
            "Use storytelling format (problem → attempt → solution)",
            "Answer objections in content before they're voiced",
        ],
    },
    "action": {
        "goal": "Drive click, sale, or sign-up",
        "tactics": [
            "Single clear CTA per video (don't say 'follow AND comment AND click')",
            "Urgency: limited time, limited spots, price going up",
            "Link in bio tool with clear labels (Free Guide / Shop / Book a Call)",
            "Reply 'INFO' or 'LINK' to DM-blast interested followers (ManyChat)",
        ],
    },
    "retention": {
        "goal": "Turn buyers into repeat customers and advocates",
        "tactics": [
            "Email list — the only asset you own (Instagram/TikTok can ban you)",
            "Private community (Discord, Skool, or Facebook Group)",
            "Loyalty discounts and early access",
            "Feature customer results in your content (UGC loop)",
        ],
    },
}


def score_niche(niche_name: str) -> dict:
    """Score a niche by profitability, competition, and growth potential.

    Args:
        niche_name: Name of the niche (e.g., "fitness", "cars").

    Returns:
        Full niche analysis dict.
    """
    key = niche_name.lower().replace(" ", "_").replace("-", "_")
    niche = NICHE_DATABASE.get(key)

    if not niche:
        close = [k for k in NICHE_DATABASE if niche_name.lower() in k or k in niche_name.lower()]
        return {
            "error": f"Niche '{niche_name}' not in database",
            "available_niches": list(NICHE_DATABASE.keys()),
            "closest_matches": close,
        }

    competition_score = {"low": 10, "medium": 7, "high": 4, "very_high": 2}
    content_score = {"low": 3, "medium": 6, "high": 8, "very_high": 10}

    overall = (
        niche["monetization_score"] * 0.4
        + competition_score.get(niche["competition"], 5) * 0.3
        + content_score.get(niche["content_availability"], 5) * 0.3
    )

    return {
        "niche": key,
        "sub_niches": niche["sub_niches"],
        "scores": {
            "monetization": f"{niche['monetization_score']}/10",
            "competition": niche["competition"],
            "content_availability": niche["content_availability"],
            "overall_opportunity": f"{overall:.1f}/10",
        },
        "avg_cpm_usd": niche["avg_cpm_usd"],
        "best_platforms": niche["best_platforms"],
        "affiliate_programs": niche["affiliate_programs"],
        "content_sources": niche["content_sources"],
        "hook_topics": niche["hook_topics"],
        "recommendation": _niche_recommendation(overall, niche["competition"]),
    }


def _niche_recommendation(score: float, competition: str) -> str:
    if score >= 8:
        return "STRONG PICK — high revenue potential, get in now"
    if score >= 6:
        return "SOLID PICK — sustainable with consistent effort"
    if competition == "very_high" and score < 6:
        return "PROCEED WITH CAUTION — saturated niche, differentiate hard or pick a sub-niche"
    return "NICHE PICK — lower competition but smaller audience; great for authority building"


def list_niches() -> dict:
    """Return all available niches with quick scoring."""
    result = []
    for name, data in NICHE_DATABASE.items():
        result.append({
            "niche": name,
            "monetization_score": f"{data['monetization_score']}/10",
            "competition": data["competition"],
            "avg_cpm_usd": data["avg_cpm_usd"],
            "best_platforms": data["best_platforms"],
        })
    # Sort by monetization score desc
    result.sort(key=lambda x: -float(x["monetization_score"].split("/")[0]))
    return {"niches": result}


def get_monetization_roadmap(follower_count: int) -> dict:
    """Return the monetization roadmap for a given follower count.

    Args:
        follower_count: Current follower/subscriber count.

    Returns:
        Current tier roadmap + next tier preview.
    """
    tiers = [
        ("0–1K", 1_000),
        ("1K–5K", 5_000),
        ("5K–25K", 25_000),
        ("25K–100K", 100_000),
        ("100K+", float("inf")),
    ]

    current_tier = "100K+"
    for tier_name, max_val in tiers:
        if follower_count < max_val:
            current_tier = tier_name
            break

    current = MONETIZATION_ROADMAP[current_tier].copy()
    current["tier"] = current_tier
    current["follower_count"] = follower_count

    # Find next tier
    tier_names = list(MONETIZATION_ROADMAP.keys())
    idx = tier_names.index(current_tier)
    next_tier = tier_names[idx + 1] if idx + 1 < len(tier_names) else None
    if next_tier:
        current["next_tier_preview"] = MONETIZATION_ROADMAP[next_tier]

    return current


def get_curation_guide() -> dict:
    """Return the full content curation workflow and legal guidelines."""
    return CURATION_WORKFLOW


def get_conversion_funnel() -> dict:
    """Return the full AIDA-based conversion funnel for theme pages."""
    return {
        "model": "Awareness → Interest → Desire → Action → Retention",
        "funnel": CONVERSION_FUNNEL,
        "key_insight": (
            "Most theme pages stop at Awareness (views). "
            "Converting means adding a structured path from view → follow → click → buy → repeat. "
            "The email list is the most important asset — build it from day 1."
        ),
    }


def generate_content_calendar(niche: str, platform: str, posts_per_week: int = 7) -> dict:
    """Generate a 1-week content calendar template for a theme page.

    Args:
        niche: Your niche (e.g., "fitness").
        platform: tiktok | instagram | youtube.
        posts_per_week: 3–21.

    Returns:
        7-day content calendar dict.
    """
    niche_data = NICHE_DATABASE.get(niche.lower(), {})
    hooks = niche_data.get("hook_topics", ["transformation", "tips", "facts", "behind the scenes"])
    sources = niche_data.get("content_sources", ["YouTube", "Reddit", "User-generated content"])

    content_types = [
        "trending_audio_clip",
        "educational_tip",
        "transformation_story",
        "question_or_poll",
        "behind_scenes",
        "product_recommendation",
        "curated_compilation",
    ]

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    posts_per_day = max(1, posts_per_week // 7)

    calendar = {}
    type_idx = 0
    hook_idx = 0

    for day in days:
        posts = []
        for p in range(posts_per_day):
            ct = content_types[type_idx % len(content_types)]
            hook = hooks[hook_idx % len(hooks)]
            posts.append({
                "post_number": p + 1,
                "content_type": ct,
                "hook_idea": hook,
                "source_suggestion": sources[type_idx % len(sources)],
                "cta": _cta_for_type(ct),
            })
            type_idx += 1
            hook_idx += 1
        calendar[day] = posts

    return {
        "niche": niche,
        "platform": platform,
        "posts_per_week": posts_per_week,
        "week_calendar": calendar,
        "reminders": [
            "Batch-create content 1 week ahead — never scramble same-day",
            "Check trending sounds every morning (TikTok Discover tab)",
            "Engage with comments within 30 min of posting",
            "Review analytics every Sunday — double down on what worked",
        ],
    }


def _cta_for_type(content_type: str) -> str:
    ctas = {
        "trending_audio_clip": "Follow for more [niche] content",
        "educational_tip": "Save this — you'll thank yourself later",
        "transformation_story": "Comment your story below",
        "question_or_poll": "Drop your answer in comments",
        "behind_scenes": "Follow to see what happens next",
        "product_recommendation": "Link in bio — use code [CODE] for discount",
        "curated_compilation": "Share this with someone who needs to see it",
    }
    return ctas.get(content_type, "Follow for more")
