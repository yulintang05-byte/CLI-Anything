"""Social Trends - Theme page strategy, niche selection, and content pillars.

Theme pages (also called "niche pages") curate and repost content around
a specific topic to build audiences without original content creation.
"""

from typing import Dict, Any, List, Optional

THEME_PAGE_NICHES: Dict[str, Dict[str, Any]] = {
    "luxury_lifestyle": {
        "label": "Luxury Lifestyle",
        "description": "Supercars, private jets, mansions, yachts, high fashion",
        "difficulty": "easy",
        "monetization_potential": "very high",
        "best_platforms": ["tiktok", "instagram"],
        "content_pillars": [
            "Supercar reveals and reviews",
            "Luxury real estate tours",
            "Designer unboxings",
            "Celebrity lifestyle",
            "Private jet/yacht content",
        ],
        "top_hashtags": ["#luxury", "#luxurylifestyle", "#rich", "#supercars", "#millionairemindset"],
        "repost_sources": ["luxury car dealers", "real estate influencers", "fashion brands"],
        "avg_cpm": 15.0,
        "monetization_paths": ["brand deals", "affiliate (luxury products)", "merch", "subscription"],
        "growth_rate": "fast",
        "competition": "high",
        "follower_targets": {"month_1": 5000, "month_3": 25000, "month_6": 100000},
    },
    "motivation": {
        "label": "Motivation & Success",
        "description": "Inspirational quotes, entrepreneur stories, mindset content",
        "difficulty": "easy",
        "monetization_potential": "high",
        "best_platforms": ["tiktok", "instagram", "youtube"],
        "content_pillars": [
            "Morning motivation quotes",
            "Entrepreneur success stories",
            "Book summaries (mindset)",
            "Daily affirmations",
            "Failure-to-success stories",
        ],
        "top_hashtags": ["#motivation", "#success", "#mindset", "#entrepreneur", "#dailymotivation"],
        "repost_sources": ["business podcasts", "entrepreneur channels", "speaker clips"],
        "avg_cpm": 8.0,
        "monetization_paths": ["digital products", "coaching", "affiliate (courses)", "Adsense"],
        "growth_rate": "fast",
        "competition": "very high",
        "follower_targets": {"month_1": 8000, "month_3": 40000, "month_6": 150000},
    },
    "fitness": {
        "label": "Fitness & Health",
        "description": "Workout tutorials, transformation stories, nutrition tips",
        "difficulty": "medium",
        "monetization_potential": "very high",
        "best_platforms": ["tiktok", "instagram", "youtube"],
        "content_pillars": [
            "Workout of the day",
            "Body transformation stories",
            "Nutrition tips & meal ideas",
            "Supplement reviews",
            "Celebrity fitness routines",
        ],
        "top_hashtags": ["#fitness", "#workout", "#fitnessmotivation", "#gym", "#transformation"],
        "repost_sources": ["personal trainers", "athlete channels", "fitness brands"],
        "avg_cpm": 12.0,
        "monetization_paths": ["supplement affiliate", "workout programs", "brand sponsorships", "Adsense"],
        "growth_rate": "medium",
        "competition": "high",
        "follower_targets": {"month_1": 3000, "month_3": 15000, "month_6": 60000},
    },
    "finance_money": {
        "label": "Finance & Money",
        "description": "Investing tips, money hacks, wealth building, passive income",
        "difficulty": "medium",
        "monetization_potential": "very high",
        "best_platforms": ["tiktok", "youtube", "instagram"],
        "content_pillars": [
            "Investing 101 tips",
            "Passive income ideas",
            "Stock/crypto market updates",
            "Money saving hacks",
            "Financial freedom stories",
        ],
        "top_hashtags": ["#money", "#investing", "#passiveincome", "#financialfreedom", "#stockmarket"],
        "repost_sources": ["finance YouTubers", "trading channels", "financial news clips"],
        "avg_cpm": 25.0,
        "monetization_paths": ["affiliate (brokers/apps)", "financial courses", "brand deals", "Adsense"],
        "growth_rate": "medium",
        "competition": "medium",
        "follower_targets": {"month_1": 2000, "month_3": 10000, "month_6": 50000},
    },
    "dark_humor": {
        "label": "Dark Humor & Memes",
        "description": "Edgy comedy, memes, trending humor, viral jokes",
        "difficulty": "easy",
        "monetization_potential": "medium",
        "best_platforms": ["tiktok", "instagram", "twitter"],
        "content_pillars": [
            "Trending memes",
            "Situational comedy clips",
            "Relatable life content",
            "Pop culture jokes",
            "Reaction-bait content",
        ],
        "top_hashtags": ["#memes", "#funny", "#comedy", "#relatable", "#darkhumor"],
        "repost_sources": ["Reddit clips", "Twitter screenshots", "comedy accounts"],
        "avg_cpm": 3.0,
        "monetization_paths": ["merch", "shoutouts", "brand deals (gaming/tech)"],
        "growth_rate": "very fast",
        "competition": "extreme",
        "follower_targets": {"month_1": 15000, "month_3": 75000, "month_6": 300000},
    },
    "travel": {
        "label": "Travel & Adventure",
        "description": "Travel destinations, tips, budget travel, hidden gems",
        "difficulty": "hard",
        "monetization_potential": "high",
        "best_platforms": ["tiktok", "instagram", "youtube"],
        "content_pillars": [
            "Destination highlights",
            "Budget travel hacks",
            "Hidden gem locations",
            "Travel packing tips",
            "Local food experiences",
        ],
        "top_hashtags": ["#travel", "#wanderlust", "#travelgram", "#adventure", "#explore"],
        "repost_sources": ["travel vloggers", "tourism boards", "drone footage channels"],
        "avg_cpm": 10.0,
        "monetization_paths": ["affiliate (booking/hotels)", "travel brand deals", "Adsense"],
        "growth_rate": "slow",
        "competition": "high",
        "follower_targets": {"month_1": 1500, "month_3": 8000, "month_6": 30000},
    },
    "gaming": {
        "label": "Gaming Highlights",
        "description": "Gaming clips, fails, wins, esports highlights",
        "difficulty": "easy",
        "monetization_potential": "high",
        "best_platforms": ["tiktok", "youtube", "twitter"],
        "content_pillars": [
            "Funny gaming fails",
            "Insane gameplay moments",
            "Esports highlights",
            "Game reveals & trailers",
            "Gaming setup tours",
        ],
        "top_hashtags": ["#gaming", "#gamer", "#gamingclips", "#esports", "#twitch"],
        "repost_sources": ["Twitch clips", "gaming subreddits", "esports organizations"],
        "avg_cpm": 5.0,
        "monetization_paths": ["gaming affiliate (peripherals)", "sponsorships (energy drinks)", "Adsense"],
        "growth_rate": "fast",
        "competition": "very high",
        "follower_targets": {"month_1": 5000, "month_3": 30000, "month_6": 100000},
    },
    "beauty_makeup": {
        "label": "Beauty & Makeup",
        "description": "Makeup tutorials, skincare routines, beauty hacks, product reviews",
        "difficulty": "medium",
        "monetization_potential": "very high",
        "best_platforms": ["tiktok", "instagram", "youtube"],
        "content_pillars": [
            "Makeup tutorials (trending looks)",
            "Skincare morning/night routines",
            "Product reviews & dupes",
            "Beauty hacks & tips",
            "Celebrity makeup recreations",
        ],
        "top_hashtags": ["#beauty", "#makeup", "#skincare", "#makeuptutorial", "#glowup"],
        "repost_sources": ["beauty influencers", "brand official content", "transformation clips"],
        "avg_cpm": 15.0,
        "monetization_paths": ["affiliate (Sephora/beauty brands)", "brand sponsorships", "merch"],
        "growth_rate": "medium",
        "competition": "high",
        "follower_targets": {"month_1": 3000, "month_3": 18000, "month_6": 70000},
    },
    "pets_animals": {
        "label": "Pets & Animals",
        "description": "Cute animal clips, pet tips, funny pet moments",
        "difficulty": "very easy",
        "monetization_potential": "medium",
        "best_platforms": ["tiktok", "instagram", "youtube"],
        "content_pillars": [
            "Cute/funny pet moments",
            "Animal facts & trivia",
            "Pet product reviews",
            "Exotic animal content",
            "Pet training tips",
        ],
        "top_hashtags": ["#pets", "#dogs", "#cats", "#animals", "#dogsoftiktok"],
        "repost_sources": ["viral animal accounts", "shelter pages", "pet brand channels"],
        "avg_cpm": 4.0,
        "monetization_paths": ["pet affiliate (food/accessories)", "brand deals", "merch"],
        "growth_rate": "very fast",
        "competition": "medium",
        "follower_targets": {"month_1": 10000, "month_3": 50000, "month_6": 200000},
    },
}

MONETIZATION_GUIDES: Dict[str, Dict[str, Any]] = {
    "brand_deals": {
        "label": "Brand Sponsorships",
        "min_followers": {"tiktok": 10_000, "instagram": 5_000, "youtube": 1_000},
        "typical_rate": "10K: $50-200/post | 100K: $500-2000/post | 1M: $5000-20000/post",
        "how_to": [
            "Create a media kit (follower count, engagement rate, niche stats)",
            "List yourself on creator marketplaces: Creator.co, AspireIQ, GrapeVine",
            "DM brands in your niche directly when you hit 5K+ followers",
            "Join TikTok Creator Marketplace at 10K followers",
            "Join YouTube BrandConnect at 1K subscribers",
        ],
        "best_for": ["luxury", "fitness", "beauty", "travel", "gaming"],
    },
    "affiliate": {
        "label": "Affiliate Marketing",
        "min_followers": {"tiktok": 1_000, "instagram": 1_000, "youtube": 500},
        "typical_rate": "3-15% commission per sale; $0.01-5.00 per click",
        "how_to": [
            "Join Amazon Associates for broad product coverage",
            "Find niche-specific programs: ShareASale, CJ Affiliate, Impact",
            "Add affiliate links to your link-in-bio (Linktree, Beacons)",
            "Create content that naturally features products",
            "Disclose affiliate relationships with #ad or #affiliate",
        ],
        "best_for": ["finance", "fitness", "beauty", "tech", "travel"],
    },
    "digital_products": {
        "label": "Digital Products & Courses",
        "min_followers": {"tiktok": 5_000, "instagram": 2_000, "youtube": 1_000},
        "typical_rate": "$10-500+ per product; 90%+ profit margin",
        "how_to": [
            "Create an ebook, preset pack, or mini-course",
            "Sell via Gumroad, Stan Store, or Payhip",
            "Use Teachable or Kajabi for full courses",
            "Tease content on social to drive traffic to products",
            "Price test: start low, raise as audience grows",
        ],
        "best_for": ["motivation", "finance", "fitness", "beauty"],
    },
    "ads_adsense": {
        "label": "Ad Revenue (Adsense/Creator Fund)",
        "min_followers": {"tiktok": 10_000, "instagram": 0, "youtube": 1_000},
        "typical_rate": "TikTok: $0.02-0.04/1K views | YouTube: $2-25 RPM",
        "how_to": [
            "TikTok: Join Creator Rewards Program at 10K+ followers, 100K+ views/30 days",
            "YouTube: Join Partner Program at 1K subs + 4K watch hours",
            "Instagram: Enable Reels bonuses (invite-only)",
            "Focus on 9:16 vertical video for highest payouts",
            "Longer watch time = higher CPM across all platforms",
        ],
        "best_for": ["all niches — high CPM niches: finance, tech, business"],
    },
    "subscription": {
        "label": "Subscription & Membership",
        "min_followers": {"tiktok": 1_000, "instagram": 1_000, "youtube": 1_000},
        "typical_rate": "$5-50/month per subscriber",
        "how_to": [
            "YouTube: Channel Memberships at 500+ subscribers",
            "TikTok: LIVE subscriptions during streams",
            "Patreon for platform-independent subscriptions",
            "Offer exclusive content, early access, or community access",
            "Discord communities at $5-10/month work at any follower count",
        ],
        "best_for": ["gaming", "motivation", "fitness", "finance"],
    },
}

CONVERSION_FUNNEL = {
    "stages": [
        {"stage": 1, "name": "Awareness", "goal": "Viral reach", "metric": "Views & impressions"},
        {"stage": 2, "name": "Interest", "goal": "Follow/subscribe", "metric": "Follower growth rate"},
        {"stage": 3, "name": "Engagement", "goal": "Comments, saves, shares", "metric": "Engagement rate"},
        {"stage": 4, "name": "Trust", "goal": "Return viewers", "metric": "Repeat view rate"},
        {"stage": 5, "name": "Conversion", "goal": "Click to offer", "metric": "CTR on link-in-bio"},
        {"stage": 6, "name": "Revenue", "goal": "Buyer/subscriber", "metric": "Revenue per 1K followers"},
    ],
    "optimization": {
        "Awareness": "Use trending sounds, hashtags, and post at peak times",
        "Interest": "Consistent niche content; clear value prop in bio",
        "Engagement": "Respond to comments; ask questions; use polls",
        "Trust": "Post consistently; deliver on content promises",
        "Conversion": "Strong CTA in every post; optimized link-in-bio",
        "Revenue": "Test price points; diversify monetization streams",
    },
}


def list_niches() -> List[Dict[str, Any]]:
    """List all supported theme page niches with key metrics."""
    return [
        {
            "niche_key": key,
            "label": data["label"],
            "difficulty": data["difficulty"],
            "monetization_potential": data["monetization_potential"],
            "growth_rate": data["growth_rate"],
            "competition": data["competition"],
            "best_platforms": data["best_platforms"],
        }
        for key, data in THEME_PAGE_NICHES.items()
    ]


def get_niche_guide(niche: str) -> Dict[str, Any]:
    """Get the complete theme page guide for a niche."""
    niche = niche.lower().replace(" ", "_").replace("-", "_")
    if niche not in THEME_PAGE_NICHES:
        available = list(THEME_PAGE_NICHES.keys())
        raise ValueError(f"Unknown niche '{niche}'. Available: {available}")
    return dict(THEME_PAGE_NICHES[niche])


def get_strategy(niche: str, monetization: str = "all") -> Dict[str, Any]:
    """Get a full theme page strategy for a niche."""
    niche_data = get_niche_guide(niche)
    niche_key = niche.lower().replace(" ", "_").replace("-", "_")

    # Filter monetization paths
    if monetization == "all":
        money_guides = MONETIZATION_GUIDES
    else:
        money_guides = {
            k: v for k, v in MONETIZATION_GUIDES.items()
            if monetization.lower() in k or any(monetization.lower() in b for b in v.get("best_for", []))
        }

    return {
        "niche": niche_data["label"],
        "overview": niche_data["description"],
        "difficulty": niche_data["difficulty"],
        "best_platforms": niche_data["best_platforms"],
        "content_pillars": niche_data["content_pillars"],
        "repost_sources": niche_data["repost_sources"],
        "top_hashtags": niche_data["top_hashtags"],
        "monetization": {
            path: {
                "rate": guide["typical_rate"],
                "steps": guide["how_to"],
                "min_followers_needed": guide["min_followers"],
            }
            for path, guide in money_guides.items()
            if niche_key in guide.get("best_for", []) or "all niches" in " ".join(guide.get("best_for", []))
        },
        "follower_milestones": niche_data["follower_targets"],
        "avg_cpm": f"${niche_data['avg_cpm']:.2f} CPM",
        "conversion_funnel": CONVERSION_FUNNEL,
    }


def get_content_pillars(niche: str) -> Dict[str, Any]:
    """Get content pillar breakdown for a niche."""
    niche_data = get_niche_guide(niche)
    pillars = niche_data["content_pillars"]

    return {
        "niche": niche_data["label"],
        "pillars": [
            {
                "name": p,
                "post_frequency": "2-3x/week",
                "formats": _pillar_formats(i),
                "tips": _pillar_tip(p),
            }
            for i, p in enumerate(pillars)
        ],
        "content_mix": {
            "educational": "30%",
            "entertaining": "40%",
            "inspirational": "20%",
            "promotional": "10%",
        },
        "repost_guidelines": [
            "Always credit original creator in caption",
            "Add your own text overlay or commentary",
            "Check content license before reposting",
            "Engage with comments on reposted content",
            "Mix reposts (60%) with original content (40%) as you grow",
        ],
    }


def get_posting_schedule(niche: str, platform: str) -> Dict[str, Any]:
    """Get optimal posting schedule for a niche+platform combo."""
    niche_data = get_niche_guide(niche)

    schedules: Dict[str, Any] = {
        "tiktok": {
            "daily_posts": 2,
            "times": ["7:00 AM", "7:00 PM"],
            "best_days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "content_rotation": _content_rotation(niche_data["content_pillars"]),
        },
        "instagram": {
            "daily_posts": 1,
            "times": ["8:00 AM", "6:00 PM"],
            "best_days": ["Mon", "Wed", "Fri", "Sat"],
            "content_rotation": _content_rotation(niche_data["content_pillars"]),
        },
        "youtube": {
            "weekly_posts": 3,
            "times": ["3:00 PM"],
            "best_days": ["Tue", "Thu", "Sat"],
            "content_rotation": _content_rotation(niche_data["content_pillars"]),
        },
    }

    schedule = schedules.get(platform.lower(), schedules["tiktok"])
    return {
        "niche": niche_data["label"],
        "platform": platform,
        **schedule,
        "consistency_tip": "Post at the same times daily. The algorithm rewards consistency.",
        "warmup_strategy": "Week 1-2: 1x/day. Week 3-4: 2x/day. Month 2+: 3-4x/day.",
    }


def converting_theme_page_guide() -> Dict[str, Any]:
    """Complete step-by-step guide to building a converting theme page."""
    return {
        "title": "How to Build a Converting Theme Page (Full Guide)",
        "overview": (
            "A theme page curates and reposts viral content in a specific niche. "
            "The goal is to build an audience, then convert them into revenue via ads, "
            "affiliate links, digital products, or brand deals."
        ),
        "phases": [
            {
                "phase": 1,
                "name": "Setup & Positioning (Days 1-7)",
                "steps": [
                    "Pick 1 niche with high monetization potential (finance, fitness, luxury, beauty)",
                    "Create accounts on TikTok + Instagram (minimum). Add YouTube later.",
                    "Profile picture: clean logo or lifestyle image (use Canva)",
                    "Username: @[niche]world, @[niche]daily, @[niche]hub — keep it short",
                    "Bio: '👇 [What you post] | Follow for daily [niche] content' + link",
                    "Set up Linktree or Beacons.ai for link-in-bio",
                    "Connect all platforms so cross-posting is easy",
                ],
            },
            {
                "phase": 2,
                "name": "Content Curation & Reposts (Days 1-30)",
                "steps": [
                    "Find viral content: TikTok Discover tab, YouTube trending, Reddit, Twitter",
                    "Download with SnapTok (TikTok) or yt-dlp (YouTube) — no watermark versions",
                    "Add text overlays with your niche quote or commentary (CapCut/Canva)",
                    "Always credit creators: 'Credit: @originalcreator' in caption",
                    "Post 2-4 times per day on TikTok, 1-2 times on Instagram",
                    "Hook first 3 seconds: bold text + trending sound = algorithm boost",
                    "Use relevant hashtag sets (3-5 on TikTok, 15-20 on Instagram)",
                ],
            },
            {
                "phase": 3,
                "name": "Audience Growth (Days 30-90)",
                "steps": [
                    "Analyze first 30 days: which content got most views/saves?",
                    "Double down on top-performing content types",
                    "Engage: reply to EVERY comment in the first hour after posting",
                    "Duet/Stitch viral content on TikTok to borrow existing virality",
                    "Collaborate: shoutout-for-shoutout (S4S) with accounts in same niche",
                    "Follow 20-30 accounts in your niche per day to get follow-backs",
                    "Track growth weekly. Goal: 10K followers by month 3",
                ],
            },
            {
                "phase": 4,
                "name": "Monetization Activation (Month 2+)",
                "steps": [
                    "Set up affiliate links: Amazon Associates, ShareASale, niche programs",
                    "Add affiliate links to Linktree/Beacons bio page",
                    "At 10K TikTok followers: apply for Creator Rewards Program",
                    "At 10K Instagram: activate shopping tags if applicable",
                    "Create first digital product: PDF guide, template pack, or mini-course",
                    "Reach out to 3-5 small brands for sponsored posts at 5K+ followers",
                    "Join creator marketplaces: Creator.co, Collabstr, AspireIQ",
                ],
            },
            {
                "phase": 5,
                "name": "Scaling & Automation (Month 3+)",
                "steps": [
                    "Batch-create 2 weeks of content in advance",
                    "Schedule posts with Later.com (Instagram) or TikTok scheduler",
                    "Build a Google Sheet content calendar to track performance",
                    "Test paid promotions: $5-10/day on top-performing organic posts",
                    "Expand to a 2nd niche or 2nd account in the same niche",
                    "Hire a VA ($5-15/hr) to handle reposting and scheduling",
                    "Reinvest first $500 into content creation tools and ads",
                ],
            },
        ],
        "tools_needed": {
            "free": ["CapCut (video editing)", "Canva (graphics)", "Linktree (bio link)", "TikTok scheduler"],
            "paid": ["Later.com ($18/mo scheduling)", "Beacons.ai ($10/mo bio)", "Adobe Express ($10/mo)"],
            "downloader": ["SnapTok (TikTok no watermark)", "yt-dlp (YouTube)", "SaveFrom.net"],
        },
        "income_timeline": {
            "month_1": "$0-50 (building audience)",
            "month_2": "$50-300 (affiliate starts)",
            "month_3": "$300-1000 (brand deals begin)",
            "month_6": "$1000-5000 (multiple streams)",
            "month_12": "$5000-20000+ (established brand)",
        },
        "common_mistakes": [
            "Posting too infrequently (need 2+ times/day on TikTok to beat algorithm)",
            "Picking a niche with no monetization (cute animals = low CPM)",
            "Stealing content without credit (risks bans and lawsuits)",
            "Ignoring analytics (track what works, cut what doesn't)",
            "Too broad a niche (pick a SUB-niche: not 'fitness' but 'home workouts')",
            "Giving up before 90 days (most pages take 60-90 days to gain traction)",
        ],
    }


def _pillar_formats(index: int) -> List[str]:
    format_sets = [
        ["Short clip (15-30s)", "Text-over-video", "Voiceover"],
        ["Tutorial video (60s)", "Step-by-step carousel (Instagram)", "Before/after"],
        ["Compilation (30-60s)", "Countdown list", "Reaction format"],
        ["Quote graphic", "Story poll", "Caption-heavy post"],
        ["Duet/Stitch (TikTok)", "Collaboration post", "Interview clip"],
    ]
    return format_sets[index % len(format_sets)]


def _pillar_tip(pillar: str) -> str:
    return f"Research top 10 viral posts about '{pillar}' and recreate the format with your spin."


def _content_rotation(pillars: List[str]) -> List[Dict[str, str]]:
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    rotation = []
    for i, day in enumerate(days):
        rotation.append({
            "day": day,
            "pillar": pillars[i % len(pillars)],
        })
    return rotation
