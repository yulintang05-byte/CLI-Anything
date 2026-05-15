"""
Theme page strategy engine.
Theme pages: niche content pages that curate + repost viral content to build
an audience, then monetize via shoutouts, brand deals, or product sales.
"""

from typing import Optional


# Proven theme page niches ranked by monetization potential
NICHE_DATABASE = {
    "luxury_lifestyle": {
        "name": "Luxury Lifestyle",
        "description": "Supercars, private jets, mansions, luxury brands",
        "monetization_potential": "VERY HIGH",
        "avg_cpm": "$8-25",
        "brand_deal_rate": "$500-5000/post at 100K followers",
        "ctr_products": "High — aspirational audience buys premium",
        "content_sources": [
            "YouTube: supercar/luxury channels",
            "Instagram: billionaire pages",
            "TikTok: #luxurylifestyle #billionairelifestyle",
        ],
        "conversion_niches": ["wealth_mindset", "investing", "real_estate"],
        "top_hashtags": [
            "#luxurylifestyle", "#rich", "#millionaire", "#supercar",
            "#mansion", "#privatejet", "#luxury", "#fyp",
        ],
        "posting_strategy": "2-3x daily. Mix: 60% visual flex content, 30% aspirational quotes, 10% 'how they made it'",
        "monetization_paths": [
            "Shoutouts: $50-500/shoutout at 50K+",
            "Brand deals: luxury watches, cars, hotels",
            "Affiliate: luxury fashion, investment apps",
            "Own product: 'mindset' ebook or course",
        ],
    },
    "fitness_motivation": {
        "name": "Fitness & Body Transformation",
        "description": "Workout clips, transformations, gym motivation",
        "monetization_potential": "HIGH",
        "avg_cpm": "$5-15",
        "brand_deal_rate": "$200-2000/post at 100K followers",
        "ctr_products": "Very high — fitness products impulse buy",
        "content_sources": [
            "YouTube: fitness channels (yt-dlp public content)",
            "TikTok: #gymtok #fitnessmotivation",
            "Reddit: r/progresspics (with permission)",
        ],
        "conversion_niches": ["nutrition", "supplements", "sports_apparel"],
        "top_hashtags": [
            "#fitness", "#gym", "#workout", "#transformation",
            "#bodybuilding", "#fitnessmotivation", "#fyp", "#fitspo",
        ],
        "posting_strategy": "3-4x daily. Mix: 50% transformation/before-after, 30% workout clips, 20% motivation quotes",
        "monetization_paths": [
            "Supplement affiliate: MyProtein, Gymshark (8-15% commission)",
            "Workout program sales: $27-97",
            "Fitness app affiliate: Whoop, Peloton ($20-50/signup)",
            "Brand deals: activewear brands",
        ],
    },
    "financial_freedom": {
        "name": "Financial Freedom / Wealth",
        "description": "Investing, side hustles, passive income, crypto",
        "monetization_potential": "VERY HIGH",
        "avg_cpm": "$10-40",
        "brand_deal_rate": "$500-10000/post at 100K followers",
        "ctr_products": "Extremely high — high intent audience",
        "content_sources": [
            "YouTube: finance/investing channels",
            "TikTok: #FinTok #stockmarket #crypto",
            "Twitter/X: finance influencers",
        ],
        "conversion_niches": ["investing", "crypto", "real_estate", "entrepreneurship"],
        "top_hashtags": [
            "#financialfreedom", "#investing", "#passiveincome",
            "#stocks", "#crypto", "#sidehustle", "#money", "#fyp",
        ],
        "posting_strategy": "2-3x daily. Mix: 40% money tips/hacks, 30% motivation, 20% market updates, 10% memes",
        "monetization_paths": [
            "Trading platform affiliate: Coinbase, Webull ($20-200/signup)",
            "Finance course sales: $97-997",
            "Newsletter monetization (high CPM)",
            "Premium Discord/community: $25-50/month",
        ],
    },
    "aesthetic_nature": {
        "name": "Aesthetic / Nature / Chill",
        "description": "Satisfying videos, nature clips, aesthetic edits, lofi vibes",
        "monetization_potential": "MEDIUM",
        "avg_cpm": "$2-6",
        "brand_deal_rate": "$100-800/post at 100K followers",
        "ctr_products": "Medium — broad audience, lower intent",
        "content_sources": [
            "YouTube: nature/aesthetic channels",
            "TikTok: #aesthetic #satisfying #chill",
            "Pexels/Pixabay: free footage",
        ],
        "conversion_niches": ["mental_health", "travel", "home_decor"],
        "top_hashtags": [
            "#aesthetic", "#satisfying", "#nature", "#chill",
            "#lofi", "#relaxing", "#fyp", "#beautiful",
        ],
        "posting_strategy": "4-5x daily. Fully automated repost with light editing. High volume strategy.",
        "monetization_paths": [
            "Ad revenue (high CPM on YouTube)",
            "Print-on-demand: Redbubble/Printful",
            "Meditation app affiliate: Calm, Headspace",
            "Sell page at 100K+ ($1000-5000)",
        ],
    },
    "comedy_memes": {
        "name": "Comedy / Memes",
        "description": "Viral memes, funny clips, relatable humor",
        "monetization_potential": "MEDIUM-HIGH",
        "avg_cpm": "$3-10",
        "brand_deal_rate": "$200-3000/post at 100K followers",
        "ctr_products": "High — young engaged audience",
        "content_sources": [
            "Reddit: r/funny r/dankmemes",
            "TikTok: #fyp #funny #memes",
            "YouTube Shorts: comedy channels",
        ],
        "conversion_niches": ["gaming", "entertainment", "apparel"],
        "top_hashtags": [
            "#memes", "#funny", "#comedy", "#relatable",
            "#trending", "#viral", "#fyp", "#lol",
        ],
        "posting_strategy": "5-8x daily. Fully volume-based. First-mover on new meme formats wins.",
        "monetization_paths": [
            "Merchandise: funny shirts/merch (Printify)",
            "Shoutouts: $50-300 at 100K",
            "Promote other pages (page network)",
            "Brand deals: gaming/tech brands love meme pages",
        ],
    },
    "pets_animals": {
        "name": "Pets & Animals",
        "description": "Cute dogs, cats, animals — high shareability",
        "monetization_potential": "MEDIUM-HIGH",
        "avg_cpm": "$4-12",
        "brand_deal_rate": "$200-2000/post at 100K followers",
        "ctr_products": "Very high — pet owners spend heavily",
        "content_sources": [
            "TikTok: #dogsoftiktok #catsoftiktok",
            "YouTube: pet channels",
            "Reddit: r/aww r/dogs r/cats",
        ],
        "conversion_niches": ["pet_food", "accessories", "veterinary"],
        "top_hashtags": [
            "#dogsoftiktok", "#catsoftiktok", "#pets", "#cute",
            "#animals", "#puppies", "#kittens", "#fyp",
        ],
        "posting_strategy": "3-5x daily. Cute content performs at any time. Include animal facts for value.",
        "monetization_paths": [
            "Pet product affiliate: Chewy, Petco (4-8% commission)",
            "Pet insurance affiliate: $20-50/signup",
            "Brand deals: pet food brands pay well",
            "Sell compilations to pet brands",
        ],
    },
}

# Theme page conversion roadmap
CONVERSION_ROADMAP = [
    {
        "phase": 1,
        "name": "Setup & Niche Selection",
        "followers_target": "0 → 1,000",
        "timeline": "Week 1-2",
        "actions": [
            "Choose ONE niche from the database above",
            "Create accounts on TikTok, Instagram Reels, YouTube Shorts (all three)",
            "Set up consistent branding: logo (Canva), username, bio with keyword",
            "Create a content calendar template",
            "Install CapCut or InShot for quick video editing",
            "Source your first 30 pieces of content from the listed sources",
            "Run social-trends scrape tiktok and social-trends scrape youtube to find what's viral NOW",
        ],
        "kpi": "Post 3-5x daily. Track which content type gets highest completion rate.",
    },
    {
        "phase": 2,
        "name": "Content System & First Traction",
        "followers_target": "1,000 → 10,000",
        "timeline": "Week 2-6",
        "actions": [
            "Identify your 3 best-performing content formats",
            "Build a content batch system: create 7 days of content in one sitting",
            "Use trending sounds (from social-trends scrape tiktok --type sounds)",
            "Engage: comment on top 10 same-niche pages within 30 min of their post",
            "Post at peak times from social-trends optimize schedule",
            "A/B test 5 different hook styles in first 2 seconds",
            "Start cross-posting all content to all 3 platforms",
        ],
        "kpi": "10% completion rate on TikTok. 500+ views per post average.",
    },
    {
        "phase": 3,
        "name": "Viral Breakthrough",
        "followers_target": "10,000 → 50,000",
        "timeline": "Month 2-3",
        "actions": [
            "Study top 3 viral posts in your niche each week",
            "Create content inspired by trends within 24h of trend emerging",
            "Use social-trends dashboard to monitor viral topics daily",
            "Start building a brand identity (consistent editing style, music, colors)",
            "Collab/duet with similar-sized pages",
            "Add CTA: 'Follow for daily [niche content]'",
            "Repurpose each video into 3 formats: clip, quote card, carousel",
        ],
        "kpi": "One 100K+ view video. Engagement rate >5%.",
    },
    {
        "phase": 4,
        "name": "Monetization Activation",
        "followers_target": "50,000 → 100,000",
        "timeline": "Month 3-5",
        "actions": [
            "Apply for TikTok Creator Marketplace",
            "Apply for YouTube Partner Program (1K subs + 4K hours OR 10M Shorts views)",
            "Set up affiliate links (choose from niche monetization paths above)",
            "Add Linktree or Beacons.ai with affiliate links",
            "DM 10 brands for gifted partnerships (even nano-influencers get free products)",
            "Create a shoutout rate card (CPM-based pricing)",
            "Build an email list with a lead magnet (free checklist/guide in your niche)",
        ],
        "kpi": "First $100/month from affiliate or shoutout revenue.",
    },
    {
        "phase": 5,
        "name": "Scale & Systematize",
        "followers_target": "100,000+",
        "timeline": "Month 5+",
        "actions": [
            "Hire a video editor ($5-15/video on Fiverr/Upwork)",
            "Build a page network (run 2-3 pages in complementary niches)",
            "Sell shoutouts via Shoutcart or direct DM at $100-1000/post",
            "Launch own product (ebook, course, merch) tailored to your audience",
            "Negotiate brand deals: minimum $10 per 1K followers per post",
            "Consider selling the page ($2-5 per follower on Fameswap/ViralAccounts)",
            "Start YouTube long-form to capture high AdSense CPM",
        ],
        "kpi": "$1,000+/month. Multiple revenue streams active.",
    },
]


def get_niche_strategy(niche_key: str) -> Optional[dict]:
    """Get full strategy for a specific niche."""
    return NICHE_DATABASE.get(niche_key)


def get_all_niches() -> list[dict]:
    """Return all niches with summary info."""
    return [
        {
            "key": k,
            "name": v["name"],
            "monetization_potential": v["monetization_potential"],
            "avg_cpm": v["avg_cpm"],
            "description": v["description"],
        }
        for k, v in NICHE_DATABASE.items()
    ]


def get_conversion_roadmap(current_followers: int = 0) -> list[dict]:
    """Return roadmap starting from the relevant phase."""
    if current_followers == 0:
        return CONVERSION_ROADMAP
    # Find the right phase
    thresholds = [0, 1_000, 10_000, 50_000, 100_000]
    phase_idx = 0
    for i, threshold in enumerate(thresholds):
        if current_followers >= threshold:
            phase_idx = i
    return CONVERSION_ROADMAP[phase_idx:]


def estimate_revenue(
    followers: int,
    platform: str,
    niche_key: str,
    posts_per_week: int = 7,
) -> dict:
    """Estimate monthly revenue potential for an account."""
    niche = NICHE_DATABASE.get(niche_key, NICHE_DATABASE["aesthetic_nature"])

    # Parse CPM range
    cpm_str = niche.get("avg_cpm", "$3-8")
    cpm_nums = [float(x.replace("$", "")) for x in cpm_str.split("-")]
    avg_cpm = sum(cpm_nums) / len(cpm_nums)

    # Estimate views/month based on followers + platform
    view_rates = {"tiktok": 0.15, "youtube": 0.3, "instagram": 0.08}
    view_rate = view_rates.get(platform, 0.1)
    monthly_views = followers * view_rate * posts_per_week * 4  # 4 weeks

    # Ad revenue (CPM / 1000 * views) — applies mainly to YouTube
    ad_revenue = (avg_cpm / 1000 * monthly_views) if platform == "youtube" else 0

    # Shoutout revenue
    shoutout_rate = max(10, followers / 1000 * 1)  # ~$1 per 1K followers per shoutout
    shoutouts_per_month = 4 if followers > 10_000 else 1
    shoutout_revenue = shoutout_rate * shoutouts_per_month

    # Affiliate estimate (1% CTR, 3% conversion, avg $30 commission)
    affiliate_revenue = monthly_views * 0.01 * 0.03 * 30 if followers > 5_000 else 0

    total = ad_revenue + shoutout_revenue + affiliate_revenue

    return {
        "platform": platform,
        "niche": niche["name"],
        "followers": followers,
        "estimated_monthly_views": int(monthly_views),
        "revenue_breakdown": {
            "ad_revenue": f"${ad_revenue:.0f}",
            "shoutouts": f"${shoutout_revenue:.0f}",
            "affiliate": f"${affiliate_revenue:.0f}",
        },
        "total_monthly_estimate": f"${total:.0f}",
        "monetization_paths": niche["monetization_paths"],
        "note": "Estimates based on industry averages. Actual results vary significantly.",
    }
