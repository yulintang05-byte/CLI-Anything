"""Theme page creation guide — niches, content strategy, and monetization."""

from typing import Any, Dict, List, Optional


# Proven high-converting theme page niches
_NICHES: List[Dict[str, Any]] = [
    {
        "name": "Luxury Lifestyle",
        "slug": "luxury",
        "platforms": ["instagram", "tiktok"],
        "competition": "high",
        "monetization_potential": "very_high",
        "avg_cpm": "$8–$20",
        "content_types": ["car reveals", "mansion tours", "watches", "jets", "fashion hauls"],
        "hashtags": ["#luxurylifestyle", "#richlife", "#millionairemindset", "#luxury", "#wealth"],
        "audience_size_estimate": "50M+ on IG",
        "why_it_converts": "Aspirational content drives high affiliate + brand deals + digital product sales",
        "starter_accounts_to_model": ["@luxuryliving", "@rich.motivation"],
        "monetization_paths": ["luxury brand affiliates", "courses on wealth building", "sponsored posts", "dropshipping luxury alternatives"],
    },
    {
        "name": "Motivation / Success Mindset",
        "slug": "motivation",
        "platforms": ["instagram", "tiktok", "youtube"],
        "competition": "very_high",
        "monetization_potential": "high",
        "avg_cpm": "$5–$15",
        "content_types": ["quote graphics", "success story clips", "morning routine POVs", "speech edits"],
        "hashtags": ["#motivation", "#successmindset", "#entrepreneur", "#grindset", "#dailymotivation"],
        "audience_size_estimate": "200M+ across platforms",
        "why_it_converts": "Evergreen demand. Low content costs (repurpose speech clips + quotes).",
        "starter_accounts_to_model": ["@motivationmafia", "@goalcast"],
        "monetization_paths": ["digital planners/journals", "courses", "coaching upsells", "affiliate (books, apps)"],
    },
    {
        "name": "Dark Humor / Memes",
        "slug": "memes",
        "platforms": ["instagram", "tiktok", "twitter"],
        "competition": "high",
        "monetization_potential": "medium",
        "avg_cpm": "$2–$6",
        "content_types": ["meme reposts", "relatable edits", "reaction videos", "trend commentary"],
        "hashtags": ["#memes", "#funnymemes", "#relatable", "#humor", "#trending"],
        "audience_size_estimate": "500M+ reach potential",
        "why_it_converts": "Massive shareability = viral spikes. Monetizes via merch + shoutouts.",
        "starter_accounts_to_model": ["@pubity", "@9gag"],
        "monetization_paths": ["shoutout packages", "merch", "brand sponsorships", "Patreon"],
    },
    {
        "name": "Fitness / Body Transformation",
        "slug": "fitness",
        "platforms": ["instagram", "tiktok", "youtube"],
        "competition": "high",
        "monetization_potential": "very_high",
        "avg_cpm": "$10–$30",
        "content_types": ["transformation before/afters", "workout clips", "nutrition tips", "gym fails", "form checks"],
        "hashtags": ["#fitness", "#transformation", "#gym", "#workout", "#fatloss"],
        "audience_size_estimate": "100M+ across platforms",
        "why_it_converts": "High-intent buyers for supplements, programs, apparel",
        "starter_accounts_to_model": ["@gymshark", "@athleanx"],
        "monetization_paths": ["fitness programs", "supplement affiliates", "custom workout plans", "sportswear brands"],
    },
    {
        "name": "Finance / Money Tips",
        "slug": "finance",
        "platforms": ["tiktok", "instagram", "youtube"],
        "competition": "medium",
        "monetization_potential": "very_high",
        "avg_cpm": "$15–$50",
        "content_types": ["money tips", "investing explainers", "side hustle ideas", "budget hacks", "passive income"],
        "hashtags": ["#personalfinance", "#investing", "#sidehustle", "#moneytips", "#financialfreedom"],
        "audience_size_estimate": "40M+ on FinTok",
        "why_it_converts": "Finance CPM is highest across all niches. Buyers have money to spend.",
        "starter_accounts_to_model": ["@humphreytalks", "@andreijikh"],
        "monetization_paths": ["brokerage affiliates", "budget courses", "credit card referrals", "sponsored content"],
    },
    {
        "name": "Pet / Animals",
        "slug": "pets",
        "platforms": ["tiktok", "instagram", "youtube"],
        "competition": "medium",
        "monetization_potential": "high",
        "avg_cpm": "$5–$12",
        "content_types": ["cute pet clips", "training tips", "pet product reviews", "funny moments", "breed spotlights"],
        "hashtags": ["#dogsoftiktok", "#catsoftiktok", "#petlover", "#animals", "#cutepets"],
        "audience_size_estimate": "70M+ on TikTok",
        "why_it_converts": "Pet owners spend $100B+/yr. Product affiliate rates are strong.",
        "starter_accounts_to_model": ["@jiffpom", "@grumpycat"],
        "monetization_paths": ["pet product affiliates (Chewy, Amazon)", "custom pet portraits", "brand deals", "Merch"],
    },
    {
        "name": "Food / Recipes",
        "slug": "food",
        "platforms": ["tiktok", "instagram", "youtube"],
        "competition": "high",
        "monetization_potential": "high",
        "avg_cpm": "$5–$15",
        "content_types": ["recipe videos", "restaurant reviews", "food hacks", "ASMR cooking", "meal prep"],
        "hashtags": ["#foodtok", "#recipe", "#cooking", "#foodie", "#easyrecipes"],
        "audience_size_estimate": "100M+ on FoodTok",
        "why_it_converts": "Meal kit + kitchen affiliate programs pay well. Brand deals are plentiful.",
        "starter_accounts_to_model": ["@cookingwithlynja", "@gordonramsay"],
        "monetization_paths": ["cookbook sales", "meal kit affiliates", "cookware affiliates", "sponsored posts"],
    },
    {
        "name": "Travel",
        "slug": "travel",
        "platforms": ["instagram", "tiktok", "youtube"],
        "competition": "high",
        "monetization_potential": "very_high",
        "avg_cpm": "$8–$25",
        "content_types": ["destination showcases", "budget travel tips", "hotel reviews", "packing hacks", "travel fails"],
        "hashtags": ["#travel", "#wanderlust", "#travelgram", "#traveltiktok", "#budgettravel"],
        "audience_size_estimate": "200M+ on Instagram",
        "why_it_converts": "Booking.com, Hotels.com, credit card affiliates pay up to $150/conversion",
        "starter_accounts_to_model": ["@humansofny", "@expertvagabond"],
        "monetization_paths": ["hotel/flight affiliates", "travel card referrals", "guided tour partnerships", "Ebooks"],
    },
    {
        "name": "Gaming",
        "slug": "gaming",
        "platforms": ["tiktok", "youtube", "twitter"],
        "competition": "very_high",
        "monetization_potential": "high",
        "avg_cpm": "$3–$10",
        "content_types": ["highlight clips", "tips/tricks", "game reviews", "stream highlights", "meme edits"],
        "hashtags": ["#gaming", "#gamer", "#videogames", "#fps", "#gameplay"],
        "audience_size_estimate": "3B+ gamers worldwide",
        "why_it_converts": "Gaming accessories + subscription services are easy affiliate plays",
        "starter_accounts_to_model": ["@pewdiepie", "@ninja"],
        "monetization_paths": ["gaming peripheral affiliates", "subscription box deals", "sponsored streams", "merchandise"],
    },
    {
        "name": "Crypto / Web3",
        "slug": "crypto",
        "platforms": ["twitter", "tiktok", "youtube"],
        "competition": "medium",
        "monetization_potential": "very_high",
        "avg_cpm": "$20–$60",
        "content_types": ["coin analysis", "NFT spotlights", "airdrop alerts", "exchange tutorials", "market updates"],
        "hashtags": ["#crypto", "#bitcoin", "#web3", "#nft", "#defi"],
        "audience_size_estimate": "50M+ on CryptoTwitter",
        "why_it_converts": "Crypto exchange affiliate programs pay $50–$500 per referral",
        "starter_accounts_to_model": ["@coinbureau", "@aantonop"],
        "monetization_paths": ["exchange referrals (Coinbase, Binance)", "NFT royalties", "consulting", "sponsored newsletters"],
    },
]


def list_niches(
    min_monetization: Optional[str] = None,
    platform_filter: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List available theme page niches with optional filters.

    min_monetization: 'medium', 'high', or 'very_high'
    platform_filter: 'tiktok', 'instagram', 'youtube', etc.
    """
    niches = _NICHES

    if min_monetization:
        rank = {"medium": 0, "high": 1, "very_high": 2}
        min_rank = rank.get(min_monetization.lower(), 0)
        niches = [n for n in niches if rank.get(n["monetization_potential"], 0) >= min_rank]

    if platform_filter:
        pf = platform_filter.lower()
        niches = [n for n in niches if pf in n["platforms"]]

    return {
        "total": len(niches),
        "filters_applied": {
            "min_monetization": min_monetization,
            "platform": platform_filter,
        },
        "niches": niches,
    }


def get_niche_details(slug: str) -> Dict[str, Any]:
    """Get full details for a specific niche."""
    for niche in _NICHES:
        if niche["slug"] == slug.lower():
            return niche
    available = [n["slug"] for n in _NICHES]
    raise ValueError(f"Niche '{slug}' not found. Available: {available}")


def get_theme_page_launch_plan(
    niche_slug: str,
    platform: str = "instagram",
    budget_usd: int = 0,
) -> Dict[str, Any]:
    """
    Generate a step-by-step launch plan for a new theme page.
    """
    niche = get_niche_details(niche_slug)
    platform = platform.lower()

    steps = [
        {
            "step": 1,
            "title": "Choose & Lock Your Sub-Niche",
            "description": (
                f"Don't just do '{niche['name']}' — pick a narrower angle. "
                "Niche accounts grow 3x faster than broad ones. "
                "Example: instead of 'Fitness', do 'Home Workouts for Busy Moms'."
            ),
            "time_estimate": "30 minutes",
            "tools": ["TikTok Creative Center (niche hashtag research)", "This CLI: social-trends trends tiktok"],
        },
        {
            "step": 2,
            "title": "Set Up Your Profile",
            "description": (
                "Username: keyword-based (e.g. @homegymhacks, not @user1234). "
                "Bio: 1 line what you do + 1 line for who + CTA. "
                "PFP: clean logo or lifestyle photo. "
                "Link in bio: Stan Store or Linktree pointing to your #1 offer."
            ),
            "time_estimate": "1 hour",
            "tools": ["Canva (logo/PFP)", "Stan Store (link in bio page)", "Namecheckr (username availability)"],
        },
        {
            "step": 3,
            "title": "Source Content (Day 1–7)",
            "description": (
                f"You don't need to create original content to start. "
                f"Find the top-performing content in {niche['name']} on TikTok/YouTube. "
                f"Download, repost with credit, add your own caption layer. "
                f"Use trending sounds from: social-trends trends tiktok-music"
            ),
            "time_estimate": "2 hours/day",
            "tools": ["SnapTik (TikTok downloader, no watermark)", "4K Video Downloader (YouTube)", "This CLI: social-trends trends youtube"],
            "legal_note": "Always credit the original creator in captions. Some platforms allow reposting with permission.",
        },
        {
            "step": 4,
            "title": "Post 3x/Day for First 30 Days",
            "description": (
                "Volume beats perfection in the first month. "
                "Post at peak times (run: social-trends account posting-times). "
                "Use 5-7 niche hashtags + 2 trending ones per post. "
                "Engage with comments within the first 30 minutes of posting."
            ),
            "time_estimate": "1–2 hours/day",
            "tools": ["Later.com (scheduling)", "Buffer (cross-post)", "This CLI: social-trends account posting-times"],
        },
        {
            "step": 5,
            "title": "Analyze & Double Down (Day 30)",
            "description": (
                "After 30 days, look at your top 3 posts by views and saves. "
                "What format do they share? Same music? Same hook type? "
                "Kill underperforming formats. Go 80% of content = that winning format."
            ),
            "time_estimate": "2 hours (monthly review)",
            "tools": ["Platform native analytics", "Metricool (cross-platform analytics)"],
        },
        {
            "step": 6,
            "title": "Introduce Monetization (Day 45–60)",
            "description": (
                f"Start with affiliate links in bio (low friction). "
                f"Best first monetizations for {niche['name']}: {', '.join(niche['monetization_paths'][:2])}. "
                "Add a free lead magnet to build your email list (most valuable long-term asset)."
            ),
            "time_estimate": "1 day to set up",
            "tools": ["Amazon Associates", "ShareASale", "LTK (LikeToKnowIt)", "Gumroad (digital products)"],
        },
    ]

    budget_breakdown = {}
    if budget_usd > 0:
        budget_breakdown = {
            "tools_monthly": min(50, budget_usd * 0.3),
            "paid_ads": min(budget_usd * 0.5, 200),
            "content_creation": budget_usd * 0.2,
            "note": "With $0 budget, focus entirely on organic posting volume and engagement.",
        }

    return {
        "niche": niche["name"],
        "platform": platform,
        "budget_usd": budget_usd,
        "estimated_time_to_1k_followers": "2–4 weeks (posting 3x/day)",
        "estimated_time_to_10k_followers": "2–4 months",
        "estimated_time_to_first_revenue": "Day 45–60 with affiliate links",
        "steps": steps,
        "budget_breakdown": budget_breakdown,
        "hashtags_to_use": niche["hashtags"],
        "content_types": niche["content_types"],
        "monetization_paths": niche["monetization_paths"],
        "success_metrics": {
            "week_1": "100 followers, 3 posts/day habit",
            "month_1": "500–2K followers, found winning content format",
            "month_3": "5K–20K followers, first affiliate revenue",
            "month_6": "50K+ followers, $500+/month from multiple streams",
        },
    }


def get_content_repurposing_guide(niche_slug: str) -> Dict[str, Any]:
    """
    Generate a content repurposing guide for a theme page niche.
    Shows how to turn 1 piece of source content into 10+ posts.
    """
    niche = get_niche_details(niche_slug)

    return {
        "niche": niche["name"],
        "principle": "Create Once, Distribute Everywhere — 1 piece of content = 10+ posts",
        "repurposing_tree": {
            "source": "1 long-form video or post (YouTube 10 min / TikTok 3-5 min)",
            "derivatives": [
                "TikTok/Reels: Extract 5 x 15–30s highlights",
                "Twitter Thread: Turn main points into 7–10 tweet thread",
                "Instagram Carousel: 7–10 slide breakdown of key insight",
                "YouTube Short: Best 60s moment",
                "Instagram Story: Behind-the-scenes of filming",
                "Quote Graphic: Pull strongest 1-liner → Canva design",
                "Pinterest Pin: Infographic summary",
                "Newsletter/Email: Expand into 300-word email for list",
                "Blog Post: Full write-up for SEO",
                "Podcast Clip: Audio version for podcast platforms",
            ],
        },
        "tools": {
            "video_clipping": "Clipper CLI (this toolkit): cli-anything-clipper",
            "captions_auto": "Kapwing or Submagic",
            "graphic_design": "Canva",
            "scheduling": "Buffer, Later, or Metricool",
            "removal_of_watermarks": "SnapTik (TikTok), SssTikTok",
        },
        "weekly_workflow": {
            "Monday": "Film/source 1 long-form content piece",
            "Tuesday": "Edit into 5 short-form clips (use Clipper CLI)",
            "Wednesday": "Post clip 1 + create 3 quote graphics from it",
            "Thursday": "Post clip 2 + write Twitter thread",
            "Friday": "Post clip 3 + create carousel from thread",
            "Saturday": "Post clip 4 + analyze week performance",
            "Sunday": "Post clip 5 + plan next week's trend hooks (use this CLI)",
        },
    }


def get_converting_cta_templates(niche_slug: str, platform: str = "tiktok") -> Dict[str, Any]:
    """
    Return proven call-to-action templates for theme pages.
    """
    niche = get_niche_details(niche_slug)
    platform = platform.lower()

    caption_ctas = {
        "tiktok": [
            "Follow for daily {niche} tips that nobody tells you 👇",
            "Save this for when you need it most 🔖",
            "Share this with someone who needs to see it 🚀",
            "Comment '{keyword}' and I'll DM you the free guide",
            "Which one surprised you most? Comment below 👇",
        ],
        "instagram": [
            "Save this post — you'll want to come back to it 📌",
            "Tag a friend who needs to hear this today ❤️",
            "Double-tap if this hit different",
            "Follow @{handle} for more {niche} content",
            "Link in bio for the full breakdown →",
        ],
        "youtube": [
            "Subscribe for weekly {niche} breakdowns",
            "Like if this was valuable — helps the algorithm show this to more people",
            "Comment your biggest takeaway below",
            "Click the bell so you never miss a {niche} video",
            "Check out the full playlist in the description",
        ],
    }

    hook_templates = [
        "POV: You just discovered the {niche} secret nobody talks about",
        "I went from 0 to {metric} in {timeframe} doing this one thing",
        "Stop doing this if you're serious about {niche} 🚫",
        "The {niche} hack that changed everything for me",
        "Things I wish I knew before starting {niche}",
        "Why 99% of people fail at {niche} (and how to be in the 1%)",
        "Day {n} of {niche} — here's what happened",
        "Replying to: '{common_question}' here's the real answer",
    ]

    return {
        "niche": niche["name"],
        "platform": platform,
        "caption_ctas": [
            t.replace("{niche}", niche["name"]) for t in caption_ctas.get(platform, caption_ctas["tiktok"])
        ],
        "hook_templates": [
            t.replace("{niche}", niche["name"]) for t in hook_templates
        ],
        "dm_funnel": {
            "step_1": "Post: 'Comment GUIDE and I'll send you the free resource'",
            "step_2": "Auto-DM the free resource (use ManyChat or Manychat)",
            "step_3": "Follow-up DM after 24h with a low-ticket offer ($7–$27)",
            "step_4": "Upsell to main product/service",
            "tools": ["ManyChat (Instagram/Facebook DM automation)", "Instachamp", "TikTok Creator Marketplace"],
        },
        "monetization_sequence": niche["monetization_paths"],
    }
