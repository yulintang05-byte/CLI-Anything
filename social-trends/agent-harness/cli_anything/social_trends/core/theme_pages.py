"""Theme page strategy — creation, growth, and conversion guide.

A theme page is a niche content aggregator account that curates and reposts
content around a specific topic (e.g. luxury cars, motivation quotes, travel,
fitness) to build a large following and then monetizes via affiliate links,
shoutouts, digital products, or brand deals.
"""

from typing import Optional


# ── Niche profiles ─────────────────────────────────────────────────────────────

THEME_NICHES = {
    "motivation": {
        "description": "Inspirational quotes, success stories, mindset content",
        "platforms": ["instagram", "tiktok", "youtube"],
        "difficulty": "easy",
        "monetization_potential": "medium",
        "avg_growth_rate": "fast",
        "content_sources": [
            "Repost motivational clips (credit original creator)",
            "Create quote graphics on Canva",
            "Compile 'best of' speech clips (MLK, Goggins, Hormozi)",
        ],
        "monetization": ["affiliate books/courses", "digital planners", "coaching upsell", "brand shoutouts"],
        "hashtags": ["#motivation", "#mindset", "#success", "#hustle", "#inspiration", "#goals"],
    },
    "luxury": {
        "description": "Luxury cars, watches, real estate, jets, lifestyle",
        "platforms": ["instagram", "tiktok"],
        "difficulty": "easy",
        "monetization_potential": "high",
        "avg_growth_rate": "medium",
        "content_sources": [
            "Repost luxury brand content (tag source)",
            "Compile 'top 10 most expensive X' videos",
            "Behind-the-scenes of billionaire lifestyles (YouTube clips)",
        ],
        "monetization": ["brand partnerships", "affiliate luxury goods", "shoutouts ($50-$500)", "OnlyFans redirect"],
        "hashtags": ["#luxury", "#supercars", "#lifestyle", "#wealthy", "#millionaire", "#richlife"],
    },
    "fitness": {
        "description": "Workout clips, transformation stories, nutrition tips",
        "platforms": ["instagram", "tiktok", "youtube"],
        "difficulty": "medium",
        "monetization_potential": "very_high",
        "avg_growth_rate": "medium",
        "content_sources": [
            "Repost transformation content (ask permission or use royalty-free)",
            "Create workout-of-the-day clips",
            "Nutrition fact videos",
        ],
        "monetization": ["supplement affiliates (Amazon, MyProtein)", "workout programs", "1-on-1 coaching", "fitness app affiliates"],
        "hashtags": ["#fitness", "#workout", "#gym", "#gains", "#fitcheck", "#transformation"],
    },
    "finance": {
        "description": "Money tips, investing, passive income, financial freedom",
        "platforms": ["tiktok", "youtube", "instagram"],
        "difficulty": "medium",
        "monetization_potential": "very_high",
        "avg_growth_rate": "fast",
        "content_sources": [
            "Summarize finance YouTube videos into short clips",
            "Share financial tips as text/voice-over videos",
            "Stock market updates, crypto news recaps",
        ],
        "monetization": ["brokerage affiliates (Webull, Public)", "financial courses", "Amazon books", "newsletter"],
        "hashtags": ["#finance", "#investing", "#passiveincome", "#money", "#financetips", "#stockmarket"],
    },
    "travel": {
        "description": "Exotic destinations, travel hacks, cheap flights",
        "platforms": ["instagram", "tiktok", "youtube"],
        "difficulty": "easy",
        "monetization_potential": "high",
        "avg_growth_rate": "medium",
        "content_sources": [
            "Repost travel clips from YouTube/TikTok (credit source)",
            "Compile 'top 5 cheapest countries' style content",
            "Travel hack tips (points, luggage, apps)",
        ],
        "monetization": ["hotel/flight affiliates", "travel credit card affiliates (highest CPL)", "travel guides/ebooks"],
        "hashtags": ["#travel", "#wanderlust", "#adventure", "#explore", "#travelgram", "#trip"],
    },
    "food": {
        "description": "Recipes, restaurant reviews, food aesthetics, mukbang",
        "platforms": ["tiktok", "instagram", "youtube"],
        "difficulty": "easy",
        "monetization_potential": "medium",
        "avg_growth_rate": "fast",
        "content_sources": [
            "Repost recipe videos (tag creator)",
            "Compile 'best street food in X country'",
            "Create satisfying food compilation reels",
        ],
        "monetization": ["kitchen affiliate products", "recipe ebooks", "restaurant/meal kit affiliates"],
        "hashtags": ["#food", "#recipe", "#cooking", "#foodie", "#yummy", "#easyrecipe"],
    },
    "beauty": {
        "description": "Makeup tutorials, skincare routines, glow-ups",
        "platforms": ["tiktok", "instagram", "youtube"],
        "difficulty": "medium",
        "monetization_potential": "very_high",
        "avg_growth_rate": "fast",
        "content_sources": [
            "Repost GRWM and tutorial videos",
            "Skincare routine breakdowns",
            "Product review compilations",
        ],
        "monetization": ["beauty affiliate (Amazon, Sephora)", "brand collaborations", "digital beauty guides"],
        "hashtags": ["#beauty", "#makeup", "#skincare", "#glow", "#grwm", "#beautytips"],
    },
    "crypto": {
        "description": "Crypto news, NFTs, Web3, DeFi, trading",
        "platforms": ["twitter", "tiktok", "youtube"],
        "difficulty": "hard",
        "monetization_potential": "very_high",
        "avg_growth_rate": "volatile",
        "content_sources": [
            "Summarize crypto news into short takes",
            "Explain blockchain concepts simply",
            "Price analysis & chart breakdowns",
        ],
        "monetization": ["exchange affiliates (Coinbase, Binance)", "trading courses", "newsletter"],
        "hashtags": ["#crypto", "#bitcoin", "#ethereum", "#defi", "#nft", "#blockchain"],
    },
    "pets": {
        "description": "Cute animals, dog/cat content, pet care tips",
        "platforms": ["tiktok", "instagram", "youtube"],
        "difficulty": "very_easy",
        "monetization_potential": "medium",
        "avg_growth_rate": "fast",
        "content_sources": [
            "Curate cute animal videos from Reddit/YouTube",
            "Pet care tip carousels",
            "Compilation of funny pet moments",
        ],
        "monetization": ["pet supply affiliates (Chewy, Amazon)", "brand deals with pet brands"],
        "hashtags": ["#pets", "#dogs", "#cats", "#animals", "#cute", "#funny"],
    },
    "relationships": {
        "description": "Dating advice, couple goals, relationship tips",
        "platforms": ["tiktok", "instagram"],
        "difficulty": "easy",
        "monetization_potential": "high",
        "avg_growth_rate": "fast",
        "content_sources": [
            "Clip relationship advice videos",
            "'Couple goals' aesthetic content",
            "Dating tips as POV-style TikToks",
        ],
        "monetization": ["dating app affiliates", "relationship courses/books", "coaching"],
        "hashtags": ["#relationships", "#dating", "#love", "#couplegoals", "#relationshiptips"],
    },
}


# ── Conversion tactics ─────────────────────────────────────────────────────────

CONVERSION_TACTICS = {
    "bio_cta": {
        "name": "Bio CTA Optimization",
        "description": "Turn profile visitors into leads/buyers",
        "steps": [
            "1. Headline: State your niche value in 5 words max (e.g. 'Daily Finance Tips 💰')",
            "2. Social proof: '150K followers trust us' or '1M+ views this month'",
            "3. CTA: 'Click link for FREE [X]' or 'DM me [keyword] for [resource]'",
            "4. Link: Use Linktree or Stan Store — link to lead magnet, not homepage",
        ],
        "conversion_rate": "2-8% of profile visitors",
    },
    "lead_magnet": {
        "name": "Free Lead Magnet",
        "description": "Give away something valuable to capture email addresses",
        "examples": [
            "Free PDF: '10 Things Rich People Do Every Morning' (finance niche)",
            "Free Workout Plan (fitness niche)",
            "Free Travel Packing List (travel niche)",
            "Free Recipe Book (food niche)",
        ],
        "tools": ["Beehiiv (newsletter)", "ConvertKit", "Gumroad (free tier)", "Google Forms + Drive"],
        "conversion_rate": "15-40% of link clicks",
    },
    "shoutout_sales": {
        "name": "Paid Shoutouts (Fast Cash)",
        "description": "Sell shoutouts to other accounts or brands",
        "rate_guide": {
            "1k-5k followers": "$5-$25 per story shoutout",
            "5k-20k followers": "$25-$75 per post",
            "20k-100k followers": "$75-$300 per post",
            "100k-500k followers": "$300-$1500 per post",
            "500k+ followers": "$1500+ per post, $500+ story",
        },
        "platforms": ["ShoutcartHQ", "Influencer.co", "direct DM outreach"],
    },
    "affiliate_links": {
        "name": "Affiliate Marketing",
        "description": "Earn commissions recommending products",
        "top_programs": [
            "Amazon Associates (3-10% commission, universal products)",
            "ShareASale (various brands, up to 30%)",
            "Impact.com (brand deals, 5-50%)",
            "ClickBank (digital products, 50-75%)",
            "Digistore24 (digital products, high commissions)",
            "Whop (digital products marketplace)",
        ],
        "strategy": "Create 'best X products' style posts with affiliate links in bio/Linktree",
    },
    "digital_products": {
        "name": "Digital Products (Highest Margin)",
        "description": "Sell info products with 95%+ profit margin",
        "products": [
            "PDF guides / eBooks ($7-$47)",
            "Preset packs / templates ($9-$37)",
            "Mini courses ($27-$97)",
            "Full courses ($97-$497)",
            "Coaching calls ($97-$500/hr)",
            "Community membership ($10-$50/month)",
        ],
        "tools": ["Gumroad", "Whop", "Stan.store", "Payhip", "Teachable"],
    },
    "brand_deals": {
        "name": "Brand Deals",
        "description": "Get paid by brands to feature their products",
        "steps": [
            "1. Reach 10K+ followers with strong engagement (>2% ER)",
            "2. Build a media kit (Canva template) — shows stats, audience demographics",
            "3. Outreach: DM/email brands you already use",
            "4. Use platforms: AspireIQ, Creator.co, Grapevine, Upfluence",
        ],
        "rate_guide": {
            "10k followers": "$50-$200 per post",
            "50k followers": "$200-$750 per post",
            "100k followers": "$500-$2000 per post",
        },
    },
}

# ── 30-Day Action Plan ─────────────────────────────────────────────────────────

THEME_PAGE_30_DAY_PLAN = [
    {"days": "1-3", "phase": "Setup", "tasks": [
        "Choose your niche (pick from top 10 above based on your interest)",
        "Create account: Professional username (e.g. @dailyfinancetips, @luxurylifestylehub)",
        "Profile photo: Use high-quality niche-related image or branded logo",
        "Write bio with CTA and link to free lead magnet",
        "Set up Linktree/Stan Store with affiliate links",
    ]},
    {"days": "4-7", "phase": "Content Baseline", "tasks": [
        "Post 3x/day: curated content from YouTube/TikTok (credit original creators)",
        "Use trending hashtags from cli-anything-social-trends hashtag optimize",
        "Use trending audio on every video",
        "Engage: reply to all comments, DM every new follower",
    ]},
    {"days": "8-14", "phase": "Find Your Hook", "tasks": [
        "Analyze which of your first 21 posts got most views/engagement",
        "Double down on that format: post 2x more of what worked",
        "Start testing original content: voiceover a trending topic in your niche",
        "Reach out to 5 accounts in niche for collaboration/shoutout swap",
    ]},
    {"days": "15-21", "phase": "Growth Push", "tasks": [
        "Run a 'Follow for [benefit]' call to action in every post caption",
        "Go live once — algorithm boost + connect with audience",
        "Post a 'controversial take' in your niche — debate = views",
        "Start collecting emails via free PDF lead magnet",
    ]},
    {"days": "22-30", "phase": "Monetization Intro", "tasks": [
        "Post your first affiliate product recommendation (3-5% of posts max)",
        "Sell your first paid shoutout to a smaller account in your niche",
        "Create a simple $7 PDF guide and promote it in bio",
        "Track: followers gained, engagement rate, email signups, revenue",
    ]},
]


class ThemePageGuide:
    """Theme page creation, growth, and conversion knowledge base."""

    def get_niche(self, niche: str) -> Optional[dict]:
        return THEME_NICHES.get(niche.lower())

    def list_niches(self) -> list[dict]:
        return [
            {
                "niche": niche,
                "difficulty": info["difficulty"],
                "monetization_potential": info["monetization_potential"],
                "growth_rate": info["avg_growth_rate"],
                "platforms": info["platforms"],
                "description": info["description"],
            }
            for niche, info in THEME_NICHES.items()
        ]

    def recommend_niche(self, goals: list[str]) -> list[dict]:
        """Recommend niches based on goals like 'fast_growth', 'high_income', 'easy_start'."""
        scored = []
        for niche, info in THEME_NICHES.items():
            score = 0
            if "fast_growth" in goals and info["avg_growth_rate"] == "fast":
                score += 3
            if "high_income" in goals and info["monetization_potential"] in ("high", "very_high"):
                score += 3
            if "easy_start" in goals and info["difficulty"] in ("easy", "very_easy"):
                score += 2
            scored.append({"niche": niche, "score": score, **info})
        return sorted(scored, key=lambda x: x["score"], reverse=True)[:5]

    def get_conversion_tactic(self, tactic: str) -> Optional[dict]:
        return CONVERSION_TACTICS.get(tactic.lower().replace(" ", "_").replace("-", "_"))

    def list_conversion_tactics(self) -> list[dict]:
        return [
            {"tactic": k, "name": v["name"], "description": v["description"]}
            for k, v in CONVERSION_TACTICS.items()
        ]

    def get_30_day_plan(self) -> list[dict]:
        return THEME_PAGE_30_DAY_PLAN

    def get_content_strategy(self, niche: str, platform: str) -> dict:
        """Return a full content strategy for a niche + platform combo."""
        niche_data = THEME_NICHES.get(niche.lower(), {})
        if not niche_data:
            return {"error": f"Unknown niche '{niche}'. Run `theme-pages niches` to see options."}

        strategy = {
            "niche": niche,
            "platform": platform,
            "content_mix": {
                "60%": "Curated / reposted content (trending, high-engagement)",
                "25%": "Original content (your face/voice/opinion on trends)",
                "15%": "Promotional (affiliate, own products, paid shoutouts)",
            },
            "posting_frequency": "3x/day for TikTok; 1-2x/day for Instagram; 3x/week YouTube",
            "content_sources": niche_data.get("content_sources", []),
            "monetization_stack": niche_data.get("monetization", []),
            "top_hashtags": niche_data.get("hashtags", []),
            "pro_tips": [
                f"The first 3 seconds of your video determine 80% of watch time. Hook hard.",
                f"Reply to top comments on viral videos in your niche — drives traffic to your profile.",
                f"Batch-create content: 5-7 videos in one session = consistency without burnout.",
                f"Pin your best-performing video to your profile to convert new visitors.",
            ],
        }
        return strategy

    def income_calculator(self, followers: int, engagement_rate: float, platform: str) -> dict:
        """Estimate monthly income potential at given follower/ER level."""
        shoutout_rate = 0
        if followers >= 1000:
            shoutout_rate = followers / 1000 * 5
        if followers >= 10_000:
            shoutout_rate = followers / 1000 * 8
        if followers >= 100_000:
            shoutout_rate = followers / 1000 * 15

        affiliate_monthly = followers * engagement_rate / 100 * 0.01 * 20  # 1% CTR, $20 avg commission
        shoutout_monthly = shoutout_rate * 4  # 4 shoutouts/month
        digital_product_monthly = followers * engagement_rate / 100 * 0.005 * 27  # 0.5% buy $27 product

        return {
            "followers": followers,
            "engagement_rate": f"{engagement_rate:.1f}%",
            "platform": platform,
            "monthly_estimates": {
                "shoutouts": f"${shoutout_monthly:,.0f}",
                "affiliate_commissions": f"${affiliate_monthly:,.0f}",
                "digital_products": f"${digital_product_monthly:,.0f}",
                "total_potential": f"${shoutout_monthly + affiliate_monthly + digital_product_monthly:,.0f}",
            },
            "note": "Estimates based on industry averages. Results vary widely by niche, content quality, and consistency.",
            "next_milestone": {
                "target_followers": _next_milestone(followers),
                "expected_income_increase": "2-3x current estimate",
            },
        }


def _next_milestone(followers: int) -> int:
    milestones = [1_000, 5_000, 10_000, 25_000, 50_000, 100_000, 250_000, 500_000, 1_000_000]
    for m in milestones:
        if m > followers:
            return m
    return followers * 2
