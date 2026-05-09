"""Theme page creation and conversion strategy guide.

A "theme page" (also called a "niche page" or "curator page") is an account that
curates and reposts content from a specific niche rather than producing original content.
The goal is rapid growth + monetisation through:
  - Brand deals / sponsorships
  - Affiliate marketing
  - Selling shoutouts / promotions
  - Flipping the account
  - Driving traffic to owned products

This module provides:
  - Niche selection matrix and scoring
  - Content curation workflow
  - Reposting strategy (with proper credit)
  - Converting from theme page to personal brand
  - Monetisation playbook
"""

from typing import Any

# Scored niche matrix: each niche rated across key dimensions
_NICHE_MATRIX: list[dict[str, Any]] = [
    {
        "niche": "Fitness & Gym",
        "growth_speed": 9,
        "monetisation": 9,
        "competition": 8,
        "content_availability": 10,
        "longevity": 10,
        "recommended_platforms": ["Instagram", "TikTok"],
        "sub_niches": ["Calisthenics", "Female fitness", "Home workout", "Powerlifting", "Yoga", "Weight loss"],
        "monetisation_methods": ["Supplement affiliates (high CPM)", "Training programs", "Gym wear brands", "Coaching leads"],
        "starter_strategy": "Repost motivational clips + transformation videos. Post 5–10x/day for 30 days.",
    },
    {
        "niche": "Personal Finance & Investing",
        "growth_speed": 7,
        "monetisation": 10,
        "competition": 7,
        "content_availability": 9,
        "longevity": 10,
        "recommended_platforms": ["TikTok", "Instagram", "YouTube"],
        "sub_niches": ["Stock market", "Crypto", "Real estate", "FIRE movement", "Side hustles", "Budgeting"],
        "monetisation_methods": ["Finance app affiliates ($50–200/signup)", "Trading courses", "Credit card affiliates", "Broker referrals"],
        "starter_strategy": "Share financial tips and motivational finance quotes. Build trust before promoting products.",
    },
    {
        "niche": "Luxury & Wealth Lifestyle",
        "growth_speed": 10,
        "monetisation": 8,
        "competition": 9,
        "content_availability": 10,
        "longevity": 8,
        "recommended_platforms": ["Instagram", "TikTok"],
        "sub_niches": ["Supercars", "Yachts", "Luxury watches", "Private jets", "Mansions", "Designer fashion"],
        "monetisation_methods": ["Luxury brand deals", "Watch/car affiliate links", "High-ticket coaching clients", "Shoutouts to aspirational brands"],
        "starter_strategy": "Repost aspirational content consistently. Follower base converts well to high-ticket offers.",
    },
    {
        "niche": "Food & Recipes",
        "growth_speed": 8,
        "monetisation": 7,
        "competition": 9,
        "content_availability": 10,
        "longevity": 10,
        "recommended_platforms": ["TikTok", "Instagram", "YouTube"],
        "sub_niches": ["Easy recipes", "Healthy eating", "Vegan", "Desserts", "Budget meals", "Restaurant reviews"],
        "monetisation_methods": ["Kitchen product affiliates", "Cookbook sales", "Food brand deals", "Meal kit affiliates"],
        "starter_strategy": "Focus on satisfying food videos (ASMR, colour, texture). Tag original creators for reposts.",
    },
    {
        "niche": "Nature & Wildlife",
        "growth_speed": 8,
        "monetisation": 5,
        "competition": 5,
        "content_availability": 9,
        "longevity": 10,
        "recommended_platforms": ["Instagram", "YouTube"],
        "sub_niches": ["Ocean/marine life", "Forest/wilderness", "Aerial/drone", "Macro photography", "Space/astronomy"],
        "monetisation_methods": ["Print-on-demand, merchandise", "Eco brand deals", "Patreon", "Stock photo licensing"],
        "starter_strategy": "High-quality visual content drives passive growth. Lower monetisation but very evergreen.",
    },
    {
        "niche": "Fashion & Style",
        "growth_speed": 9,
        "monetisation": 9,
        "competition": 10,
        "content_availability": 10,
        "longevity": 9,
        "recommended_platforms": ["Instagram", "TikTok"],
        "sub_niches": ["Streetwear", "Sustainable fashion", "Luxury fashion", "Thrift/vintage", "Men's style", "Women's fashion"],
        "monetisation_methods": ["Fashion brand deals", "LTK/Shopify affiliate", "Own clothing brand", "Styling services"],
        "starter_strategy": "Aesthetic curation is key. Develop a recognizable visual identity within your style sub-niche.",
    },
    {
        "niche": "Pets & Animals",
        "growth_speed": 9,
        "monetisation": 6,
        "competition": 7,
        "content_availability": 10,
        "longevity": 10,
        "recommended_platforms": ["TikTok", "Instagram", "YouTube"],
        "sub_niches": ["Dogs", "Cats", "Exotic pets", "Wildlife rescue", "Funny animals"],
        "monetisation_methods": ["Pet product affiliates", "Pet food/supply deals", "Vet service promos", "Merchandise"],
        "starter_strategy": "Fastest-growing content category. Extremely high shareability and virality.",
    },
    {
        "niche": "Motivation & Mindset",
        "growth_speed": 8,
        "monetisation": 7,
        "competition": 9,
        "content_availability": 9,
        "longevity": 9,
        "recommended_platforms": ["Instagram", "TikTok", "YouTube"],
        "sub_niches": ["Entrepreneurship mindset", "Stoicism", "Productivity", "Success stories", "Morning routines"],
        "monetisation_methods": ["Course sales", "Coaching programs", "Book affiliates", "Merchandise/apparel"],
        "starter_strategy": "Text-over-video and speech clips perform well. Build a strong quote identity.",
    },
    {
        "niche": "Gaming",
        "growth_speed": 7,
        "monetisation": 7,
        "competition": 10,
        "content_availability": 10,
        "longevity": 9,
        "recommended_platforms": ["TikTok", "YouTube", "Twitch"],
        "sub_niches": ["Clips/highlights", "Game reviews", "Esports", "Gaming setup", "Retro gaming", "Speedruns"],
        "monetisation_methods": ["Gaming peripheral affiliates", "Game key sites", "Streaming platform revenue", "Brand deals"],
        "starter_strategy": "Viral clip compilations grow fastest. Focus on one popular game for algorithm categorisation.",
    },
    {
        "niche": "DIY & Home Improvement",
        "growth_speed": 7,
        "monetisation": 8,
        "competition": 6,
        "content_availability": 8,
        "longevity": 10,
        "recommended_platforms": ["TikTok", "YouTube", "Instagram"],
        "sub_niches": ["Home renovation", "Small DIY projects", "Upcycling", "Woodworking", "Crafts", "Organising"],
        "monetisation_methods": ["Tool affiliates (high AOV)", "Home decor brand deals", "Own product line", "Courses"],
        "starter_strategy": "Transformation content (before/after) performs extremely well. Strong Pinterest crossover.",
    },
]

# Step-by-step theme page playbook
_LAUNCH_PLAYBOOK: list[dict[str, Any]] = [
    {
        "phase": "1 — Niche Selection (Day 1–2)",
        "actions": [
            "Use the niche matrix to select your niche (score 7+ on growth + monetisation)",
            "Pick a specific sub-niche to start (easier to rank and build authority)",
            "Research top 20 accounts in that niche — note their posting style, frequency, and content type",
            "Confirm there are 50+ active creators producing content to curate from",
        ],
        "deliverable": "Finalised niche + sub-niche decision",
    },
    {
        "phase": "2 — Account Setup (Day 2–3)",
        "actions": [
            "Create account with a niche-keyword username (e.g., @gymmoment, @wealthdaily)",
            "Use a simple but eye-catching profile picture (relevant to niche, not personal photo)",
            "Write a clear bio: what the page is about + follow CTA",
            "Set up link in bio (Linktree or Stan Store) even if empty initially",
            "Follow 50 top accounts in your niche (signals to algorithm)",
        ],
        "deliverable": "Fully set up account ready for posting",
    },
    {
        "phase": "3 — Content Pipeline (Day 3–7)",
        "actions": [
            "Identify 10–20 creators to curate content from (always credit in caption)",
            "Download/save 50–100 pieces of top-performing content as your queue",
            "Use yt-dlp or SnapTik to download TikTok/Instagram videos for reposting",
            "Create a simple Notion/sheet to track: Source, Date posted, Performance",
            "Caption formula: [Hook or quote] + [Relevant hashtags] + [Credit: @creator]",
        ],
        "deliverable": "50+ pieces of content ready to post",
    },
    {
        "phase": "4 — Aggressive Launch (Week 1–2)",
        "actions": [
            "Post 5–10 times per day on TikTok / 3–5 times on Instagram",
            "Test 5 different content formats in first week to find what resonates",
            "Engage on every comment you receive — respond within 1 hour",
            "Leave thoughtful comments on top creators' recent posts (not spam)",
            "Use trending sounds on every TikTok post",
        ],
        "deliverable": "100+ posts live, first viral hit identified",
    },
    {
        "phase": "5 — Optimise & Scale (Week 3–8)",
        "actions": [
            "Analyse which content type drives the most followers (not just views)",
            "Double down on the top 2 content formats",
            "Reduce posting to 3–5x/day as quality improves",
            "Start building an email list via bio link (even for theme pages)",
            "Research and join 2–3 creator communities in your niche for collab opportunities",
        ],
        "deliverable": "1,000–10,000 followers, monetisation-ready profile",
    },
    {
        "phase": "6 — First Monetisation (10K+ followers)",
        "actions": [
            "Apply to affiliate programs relevant to your niche",
            "Reach out to 10 micro-brands for paid promotion deals ($50–$300/post range)",
            "Create a simple media kit (Canva): follower count, engagement rate, niche overview",
            "Offer shoutout-for-shoutout (S4S) with similar-size accounts to grow faster",
            "Start documenting your theme page journey — this itself becomes content",
        ],
        "deliverable": "First monetised post, $100–$500/month income started",
    },
]

# Converting theme page to personal brand
_CONVERSION_STRATEGY: list[dict[str, Any]] = [
    {
        "step": "1. Start adding your face/voice (gradually)",
        "how": "Begin with 1 personal video per 10 curation posts. Introduce yourself as 'the curator behind @pagename'.",
        "when": "After reaching 5K followers on TikTok or 2K on Instagram",
        "why": "Personal brand has 10x higher monetisation ceiling than anonymous theme pages",
    },
    {
        "step": "2. Share your personal story/journey",
        "how": "Create a 'story behind the page' video explaining why you started it and your personal connection to the niche.",
        "when": "First month of adding personal content",
        "why": "Story drives follow-through and builds loyal community vs. passive followers",
    },
    {
        "step": "3. Shift content ratio",
        "how": "Month 1: 10% personal / 90% curated. Month 3: 30% / 70%. Month 6: 60% / 40%. Month 12: 80% / 20%.",
        "when": "Gradual transition over 6–12 months",
        "why": "Sudden shifts cause follower drop. Gradual transition retains audience while building new identity",
    },
    {
        "step": "4. Build your unique angle/perspective",
        "how": "Add commentary to curated posts ('My take: ...'), share opinions, develop a signature content format.",
        "when": "Start from day 1 of personal content",
        "why": "Unique perspective is what converts theme page followers to personal brand fans",
    },
    {
        "step": "5. Launch your first owned product",
        "how": "Start with a free lead magnet (PDF, checklist, template), then a low-ticket digital product ($9–$47).",
        "when": "After reaching 10K followers and consistent personal content",
        "why": "Own product = own income stream not dependent on brand deals or platform algorithms",
    },
    {
        "step": "6. Build off-platform assets",
        "how": "Email list (most important), website/blog, YouTube channel, community (Discord/Circle).",
        "when": "Parallel to all other steps — start email list immediately",
        "why": "Platform algorithms change; you need owned distribution channels",
    },
]

# Legal/ethical considerations
_ETHICAL_GUIDELINES: list[str] = [
    "Always credit original creators in your caption (e.g., 'Credit: @originalcreator')",
    "For TikTok: use the 'Duet' or 'Stitch' feature when reposting instead of direct download + re-upload",
    "For Instagram: tag original creator in the image AND caption",
    "Do NOT remove watermarks from videos — it's unethical and violates platform terms",
    "If a creator asks you to remove their content, do so immediately and respectfully",
    "Music: use original video's audio (native platform features) to avoid copyright claims",
    "Business account disclosure: if you're being paid to post, disclose with #ad or #sponsored",
    "Some niches (medical, legal, financial) have stricter rules — always disclaim you are not a professional",
]


def get_niche_recommendations(min_growth: int = 7, min_monetisation: int = 7) -> list[dict]:
    """Return niches that meet minimum growth and monetisation thresholds."""
    qualified = [
        n for n in _NICHE_MATRIX
        if n["growth_speed"] >= min_growth and n["monetisation"] >= min_monetisation
    ]
    # Score = average of growth + monetisation, penalised for very high competition
    scored = sorted(
        qualified,
        key=lambda n: (n["growth_speed"] + n["monetisation"]) - (n["competition"] * 0.3),
        reverse=True,
    )
    return scored


def get_niche_details(niche: str) -> dict | None:
    """Return full details for a specific niche."""
    niche_lower = niche.lower()
    for n in _NICHE_MATRIX:
        if niche_lower in n["niche"].lower():
            return n
    return None


def get_launch_playbook() -> list[dict]:
    """Return the complete theme page launch playbook."""
    return _LAUNCH_PLAYBOOK


def get_conversion_strategy() -> list[dict]:
    """Return steps to convert a theme page to a personal brand."""
    return _CONVERSION_STRATEGY


def get_ethical_guidelines() -> list[str]:
    """Return ethical and legal guidelines for theme page operators."""
    return _ETHICAL_GUIDELINES


def score_niche(niche_name: str) -> dict:
    """Get a detailed score breakdown for a niche."""
    details = get_niche_details(niche_name)
    if not details:
        return {"error": f"Niche '{niche_name}' not found. Run 'theme-page niches' to see available options."}

    overall = round((
        details["growth_speed"] * 0.25 +
        details["monetisation"] * 0.35 +
        (10 - details["competition"]) * 0.15 +
        details["content_availability"] * 0.15 +
        details["longevity"] * 0.10
    ), 1)

    return {
        **details,
        "overall_score": overall,
        "verdict": (
            "Excellent choice" if overall >= 7.5 else
            "Good choice" if overall >= 6.0 else
            "Risky — high competition or low monetisation"
        ),
    }


def generate_content_plan(niche: str, platform: str = "tiktok",
                           days: int = 7) -> list[dict]:
    """Generate a content plan for a theme page."""
    details = get_niche_details(niche)
    if not details:
        return [{"error": f"Niche '{niche}' not found"}]

    formats = {
        "tiktok": ["Motivational clip", "Transformation video", "Tutorial repost", "Funny/relatable clip", "Before/after"],
        "instagram": ["Quote graphic", "Carousel tips", "Reels clip", "Story poll", "Infographic"],
        "youtube": ["Compilation video", "Tutorial repost", "Commentary/reaction", "Best-of playlist"],
    }
    platform_formats = formats.get(platform.lower(), formats["tiktok"])

    plan = []
    from datetime import date, timedelta
    for day in range(days):
        post_date = date.today() + timedelta(days=day)
        daily_posts = []
        posts_per_day = 5 if platform.lower() == "tiktok" else 2
        for i in range(posts_per_day):
            fmt = platform_formats[i % len(platform_formats)]
            daily_posts.append({
                "post_number": i + 1,
                "format": fmt,
                "niche": niche,
                "hashtags_hint": f"Use niche hashtags for {niche}",
                "caption_formula": f"[Hook related to {niche}] + [Credit: @original_creator] + [Hashtags]",
            })
        plan.append({
            "date": post_date.isoformat(),
            "day": post_date.strftime("%A"),
            "posts": daily_posts,
        })
    return plan
