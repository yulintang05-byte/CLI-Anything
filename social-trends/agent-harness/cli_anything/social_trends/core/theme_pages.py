"""Theme page strategy knowledge base — niches, content strategy, monetization, conversion."""

from datetime import datetime, timezone

# ── Niche database ────────────────────────────────────────────────────────────

_NICHES = {
    "luxury-lifestyle": {
        "name": "Luxury Lifestyle",
        "difficulty": "easy",
        "competition": "medium",
        "monetization_potential": "very-high",
        "content_types": ["luxury cars", "mansions", "travel", "watches", "fashion"],
        "target_audience": "aspirational 18-34",
        "avg_engagement_rate": "4-8%",
        "monetization_paths": ["affiliate (luxury brands)", "brand deals", "dropshipping", "course"],
        "content_sources": ["Instagram repost (with permission)", "YouTube clips", "original shoots"],
        "growth_speed": "fast",
        "description": "Showcase luxury items, lifestyle, and wealth. High share-rate because people tag friends.",
        "example_accounts": ["@luxuryreels", "@dreamcarsworld", "@millionaireplans"],
        "hashtags": ["luxury", "rich", "lifestyle", "lamborghini", "luxurylife", "millionaire"],
        "conversion_path": "Followers → Email list → Digital product or affiliate offer",
    },
    "motivation-quotes": {
        "name": "Motivation & Mindset",
        "difficulty": "easy",
        "competition": "very-high",
        "monetization_potential": "medium",
        "content_types": ["quote graphics", "speech clips", "success stories", "daily affirmations"],
        "target_audience": "18-45 entrepreneurs and students",
        "avg_engagement_rate": "3-6%",
        "monetization_paths": ["digital products", "affiliate (books/courses)", "merch", "coaching"],
        "content_sources": ["Quote libraries", "public domain speeches", "original content"],
        "growth_speed": "medium",
        "description": "Evergreen niche — motivation never goes out of style. Easy to produce at scale.",
        "example_accounts": ["@motivated_humans", "@mindsetflip", "@goalcrusher"],
        "hashtags": ["motivation", "mindset", "success", "goals", "grindset", "inspiration"],
        "conversion_path": "Followers → Free ebook → Email → Course or coaching",
    },
    "ai-tools": {
        "name": "AI Tools & Productivity",
        "difficulty": "medium",
        "competition": "low-medium",
        "monetization_potential": "very-high",
        "content_types": ["AI tool demos", "tutorials", "before/after", "productivity hacks"],
        "target_audience": "25-45 professionals and creators",
        "avg_engagement_rate": "5-10%",
        "monetization_paths": ["affiliate (AI tools)", "sponsored content", "newsletter", "course"],
        "content_sources": ["Original demos", "AI tool websites", "Twitter/X viral posts"],
        "growth_speed": "very-fast",
        "description": "Fastest growing niche in 2025. High-value audience. Most tools offer 30-50% affiliate commissions.",
        "example_accounts": ["@ai.toolbox", "@futuretools", "@aibreakfast"],
        "hashtags": ["ai", "artificialintelligence", "chatgpt", "productivity", "futuretech", "aitools"],
        "conversion_path": "Followers → Tool affiliate links → Newsletter → Premium course",
        "top_affiliate_programs": [
            "Jasper AI (30% recurring)",
            "Copy.ai (45% first month)",
            "Midjourney (referral program)",
            "Notion AI (25% recurring)",
        ],
    },
    "finance-investing": {
        "name": "Finance & Investing",
        "difficulty": "medium",
        "competition": "high",
        "monetization_potential": "very-high",
        "content_types": ["stock tips", "budgeting", "passive income ideas", "investing basics"],
        "target_audience": "22-40 young professionals",
        "avg_engagement_rate": "4-7%",
        "monetization_paths": ["affiliate (brokers/apps)", "paid newsletter", "course", "consulting"],
        "content_sources": ["Financial news", "Reddit r/investing", "original analysis"],
        "growth_speed": "medium",
        "description": "High-value audience willing to pay. Requires disclaimer about non-financial advice.",
        "example_accounts": ["@minority.mindset", "@humphreytalks", "@andrei.jikh"],
        "hashtags": ["investing", "stocks", "personalfinance", "financetips", "moneymanagement", "wealth"],
        "conversion_path": "Followers → Free investing guide → Paid course or newsletter",
        "disclaimer": "Always include: 'Not financial advice. For educational purposes only.'",
    },
    "fitness-wellness": {
        "name": "Fitness & Wellness",
        "difficulty": "medium",
        "competition": "very-high",
        "monetization_potential": "high",
        "content_types": ["workout clips", "meal prep", "transformation stories", "tips"],
        "target_audience": "18-35 health-conscious",
        "avg_engagement_rate": "5-9%",
        "monetization_paths": ["online coaching", "meal plans", "supplement affiliate", "course"],
        "content_sources": ["Original content", "permission reposts", "transformation submissions"],
        "growth_speed": "medium",
        "description": "Visual niche — transformations go viral easily. January always spikes this niche.",
        "example_accounts": ["@gymfeed", "@bodybuildingcom", "@growingannanas"],
        "hashtags": ["fitness", "workout", "gym", "fitspo", "fitnessmotivation", "healthylifestyle"],
        "conversion_path": "Followers → Free workout plan → Paid coaching or program",
    },
    "relationship-advice": {
        "name": "Relationship & Dating",
        "difficulty": "easy",
        "competition": "medium",
        "monetization_potential": "high",
        "content_types": ["dating tips", "red flags", "relationship advice", "romance stories"],
        "target_audience": "18-35 singles and couples",
        "avg_engagement_rate": "6-12%",
        "monetization_paths": ["digital products", "dating app affiliate", "coaching", "ebook"],
        "content_sources": ["Twitter/X viral posts", "Reddit relationships", "original scripts"],
        "growth_speed": "fast",
        "description": "Extremely high share rate — people tag significant others and friends constantly.",
        "example_accounts": ["@modernlove", "@datingadvice", "@toxicfreerelationship"],
        "hashtags": ["relationship", "dating", "love", "relationshipadvice", "redflags", "couplegoals"],
        "conversion_path": "Followers → 'Red flags' ebook → Dating course or community",
    },
    "food-recipes": {
        "name": "Food & Recipes",
        "difficulty": "medium",
        "competition": "high",
        "monetization_potential": "medium-high",
        "content_types": ["quick recipes", "food hacks", "restaurant reviews", "meal prep"],
        "target_audience": "25-45 home cooks",
        "avg_engagement_rate": "5-8%",
        "monetization_paths": ["cookbook affiliate", "kitchen product affiliate", "brand deals", "own cookbook"],
        "content_sources": ["Original recipes", "permission reposts from food creators", "viral recipes"],
        "growth_speed": "medium",
        "description": "Evergreen niche with consistent demand. Kitchen gadget affiliate pays well ($20-80/sale).",
        "example_accounts": ["@tasty", "@delish", "@buzzfeedtasty"],
        "hashtags": ["recipe", "foodtok", "easyrecipes", "mealprep", "homecooking", "foodie"],
        "conversion_path": "Followers → Recipe ebook → Cooking course or brand partnership",
    },
    "gaming": {
        "name": "Gaming",
        "difficulty": "hard",
        "competition": "very-high",
        "monetization_potential": "high",
        "content_types": ["gameplay clips", "gaming tips", "game reviews", "viral moments"],
        "target_audience": "13-30 gamers",
        "avg_engagement_rate": "4-8%",
        "monetization_paths": ["YouTube AdSense", "streaming donations", "merch", "brand deals"],
        "content_sources": ["Own gameplay", "clip submissions from community", "viral Twitch clips"],
        "growth_speed": "slow-medium",
        "description": "Saturated but loyal audience. Best angle: niche down to one game with community building.",
        "example_accounts": ["@fortniteclips", "@valoranthighlights", "@minecraftbuilds"],
        "hashtags": ["gaming", "gamer", "games", "gamingclips", "twitch", "streamer"],
        "conversion_path": "Followers → Discord community → Merch or donations",
    },
    "fashion-style": {
        "name": "Fashion & Style",
        "difficulty": "medium",
        "competition": "high",
        "monetization_potential": "high",
        "content_types": ["outfit ideas", "hauls", "styling tips", "trend roundups"],
        "target_audience": "16-35 fashion-conscious",
        "avg_engagement_rate": "4-7%",
        "monetization_paths": ["LTK/affiliate shopping links", "brand deals", "dropshipping", "own store"],
        "content_sources": ["Instagram repost", "original OOTD", "Pinterest inspiration"],
        "growth_speed": "medium",
        "description": "Direct path to dropshipping or LTK affiliate. High CPM from fashion brands.",
        "example_accounts": ["@outfitinspo", "@fashionwithfaith", "@mensfashionpost"],
        "hashtags": ["fashion", "ootd", "style", "outfitinspo", "fashiontok", "styleinspo"],
        "conversion_path": "Followers → LTK links / Shop → Own Shopify dropship store",
    },
    "crypto-web3": {
        "name": "Crypto & Web3",
        "difficulty": "hard",
        "competition": "medium",
        "monetization_potential": "very-high",
        "content_types": ["coin analysis", "news updates", "NFT content", "DeFi explainers"],
        "target_audience": "20-40 crypto-curious",
        "avg_engagement_rate": "5-10%",
        "monetization_paths": ["exchange affiliate (Binance 40%)", "paid newsletter", "consulting"],
        "content_sources": ["CoinGecko data", "CryptoTwitter reposts", "original analysis"],
        "growth_speed": "fast during bull market",
        "description": "Extremely high affiliate commissions from exchanges. Volatile — bull markets are explosive growth.",
        "example_accounts": ["@altcoinbuzz", "@coinbureau", "@cryptobanter"],
        "hashtags": ["crypto", "bitcoin", "ethereum", "web3", "blockchain", "nft", "defi"],
        "conversion_path": "Followers → Exchange referral link → Newsletter",
        "disclaimer": "Always include 'Not financial advice' disclaimer.",
    },
}


# ── Theme page education ───────────────────────────────────────────────────────

def get_niches(sort_by: str = "monetization_potential") -> list:
    """List all niches with key metrics."""
    niche_list = []
    for key, n in _NICHES.items():
        niche_list.append({
            "id": key,
            "name": n["name"],
            "difficulty": n["difficulty"],
            "competition": n["competition"],
            "monetization_potential": n["monetization_potential"],
            "growth_speed": n["growth_speed"],
            "avg_engagement_rate": n["avg_engagement_rate"],
            "top_monetization": n["monetization_paths"][0] if n["monetization_paths"] else "",
        })

    order = {"very-high": 0, "high": 1, "medium-high": 2, "medium": 3, "low": 4}
    if sort_by == "monetization_potential":
        niche_list.sort(key=lambda x: order.get(x["monetization_potential"], 5))
    elif sort_by == "growth_speed":
        speed_order = {"very-fast": 0, "fast": 1, "medium": 2, "slow-medium": 3, "slow": 4}
        niche_list.sort(key=lambda x: speed_order.get(x["growth_speed"], 5))
    elif sort_by == "difficulty":
        diff_order = {"easy": 0, "medium": 1, "hard": 2}
        niche_list.sort(key=lambda x: diff_order.get(x["difficulty"], 3))

    return niche_list


def get_niche_strategy(niche_id: str) -> dict:
    """Get full strategy for a specific niche."""
    n = _NICHES.get(niche_id)
    if not n:
        available = list(_NICHES.keys())
        raise ValueError(f"Unknown niche '{niche_id}'. Available: {available}")

    return {
        "niche_id": niche_id,
        **n,
        "30_day_action_plan": _30_day_plan(niche_id, n),
        "content_calendar_framework": _content_framework(n),
        "monetization_roadmap": _monetization_roadmap(n),
        "tools_needed": _tools_for_niche(n),
    }


def get_roadmap(experience_level: str = "beginner") -> dict:
    """Get the full theme page creation and monetization roadmap."""
    return {
        "what_is_a_theme_page": (
            "A theme page (or niche page) is a social media account built around a specific topic — "
            "not around a personal brand. You curate, repost, and create content about ONE niche. "
            "The creator can stay anonymous. Income comes from affiliate links, brand deals, digital "
            "products, and ad revenue."
        ),
        "why_theme_pages_work": [
            "Anonymous — no need to show your face (speeds up content creation 5x)",
            "Scalable — one person can run 3-10 theme pages simultaneously",
            "Compounding — accounts grow on autopilot once established",
            "Multiple income streams from a single account",
            "Low startup cost ($0-$50 to start)",
        ],
        "success_formula": {
            "niche": "One specific topic — narrow enough to dominate, broad enough for daily content",
            "consistency": "Post 1-3x daily minimum for first 90 days",
            "value": "Educational, entertaining, or inspirational — every post must do one of these",
            "cta": "Every post directs traffic (comment, follow, save, click link)",
        },
        "phases": _roadmap_phases(experience_level),
        "common_mistakes": _common_mistakes(),
        "income_timeline": _income_timeline(),
        "tools_stack": _recommended_tools(),
    }


def get_conversion_guide() -> dict:
    """Get the theme page to income conversion playbook."""
    return {
        "conversion_funnel": {
            "top": "Social content (TikTok/YouTube/Instagram Reel)",
            "middle": "Link in bio → Landing page or Linktree",
            "bottom": "Email list or purchase",
        },
        "traffic_to_revenue_paths": [
            {
                "path": "Affiliate marketing",
                "how": "Include affiliate links in bio or captions. Review products organically.",
                "when": "Start immediately (day 1)",
                "income_range": "$500-$10K/month at scale",
                "best_niches": ["finance", "ai-tools", "beauty", "fashion", "crypto-web3"],
            },
            {
                "path": "Digital products",
                "how": "Create an ebook, template pack, or mini-course. Sell via Gumroad or Stan.store.",
                "when": "After 1K followers (you have an audience to sell to)",
                "income_range": "$1K-$20K/month",
                "best_niches": ["motivation-quotes", "finance-investing", "fitness-wellness", "business"],
            },
            {
                "path": "Brand deals / sponsorships",
                "how": "Reach out to brands in your niche at 5K+ followers with media kit.",
                "when": "5K-10K followers minimum",
                "income_range": "$200-$5K per post",
                "best_niches": ["luxury-lifestyle", "fitness-wellness", "food-recipes", "fashion-style"],
            },
            {
                "path": "Newsletter",
                "how": "Convert followers to email subscribers. Send weekly niche content + affiliate offers.",
                "when": "Start building from day 1",
                "income_range": "$500-$50K/month (email list owns the relationship)",
                "best_niches": ["ai-tools", "finance-investing", "crypto-web3"],
            },
            {
                "path": "Community / membership",
                "how": "Paid Discord or Skool community with exclusive content.",
                "when": "10K+ engaged followers",
                "income_range": "$2K-$30K/month recurring",
                "best_niches": ["fitness-wellness", "gaming", "finance-investing"],
            },
        ],
        "link_in_bio_optimization": {
            "tool_recommendations": ["Linktree", "Stan.store", "Beacons.ai", "Bio.link"],
            "what_to_include": [
                "Free lead magnet (ebook, checklist) to capture emails",
                "Top affiliate link",
                "Best-performing piece of content",
                "Direct purchase link if selling a product",
            ],
            "cta_formula": "Get [SPECIFIC BENEFIT] → [Free or Low-Cost Offer] — link in bio",
        },
        "email_list_strategy": {
            "lead_magnet_ideas": [
                "Free niche checklist (e.g. '10 AI tools that replace 5 paid subscriptions')",
                "Free mini ebook (5-10 pages, high-value, low effort to create)",
                "Free template pack (Notion, Canva, spreadsheet)",
                "Free email course (5-day series sent automatically)",
            ],
            "email_sequence": [
                "Day 0: Welcome + deliver free gift",
                "Day 1: Your story + why you created this page",
                "Day 3: Your top 3 tips in the niche (high-value)",
                "Day 5: Soft pitch — recommend your #1 affiliate product",
                "Day 7: Social proof + stronger CTA",
                "Weekly: Niche newsletter with 1 affiliate recommendation",
            ],
            "platforms": ["ConvertKit (free to 1K)", "Beehiiv (free to 2.5K)", "MailerLite (free to 1K)"],
        },
    }


def _30_day_plan(niche_id: str, niche: dict) -> list:
    return [
        {"week": 1, "focus": "Setup & Foundation", "tasks": [
            f"Create accounts on TikTok, YouTube Shorts, and Instagram Reels (all same handle)",
            f"Design profile: logo, bio with '{niche['name']}' keyword, link in bio",
            f"Research top 10 accounts in the {niche['name']} space — note what performs best",
            "Create Linktree with lead magnet + top affiliate link",
            f"Produce 14 videos in one batch session using content ideas from this niche",
        ]},
        {"week": 2, "focus": "Content Velocity", "tasks": [
            "Post 2x daily on TikTok, 1x daily on YouTube Shorts and Instagram Reels",
            "Use trending sounds + niche hashtags on every post",
            "Reply to every comment within 1 hour of posting",
            "Track which content type gets highest completion rate",
            "Set up email capture via landing page (free lead magnet offer)",
        ]},
        {"week": 3, "focus": "Optimization & Doubling Down", "tasks": [
            "Identify top 2-3 performing content types — make 80% of content in that format",
            "A/B test different hooks (first 3 seconds) on same topic",
            "Start collecting email subscribers by mentioning lead magnet in captions",
            "Reach out to 5 micro-influencers in your niche for potential collabs",
            "Apply to relevant affiliate programs",
        ]},
        {"week": 4, "focus": "Monetization Activation", "tasks": [
            "Post first soft-sell video (affiliate recommendation disguised as review)",
            "Send first email to your list with value content + affiliate mention",
            "Plan your first digital product based on what followers ask most",
            "Track all metrics: views, followers, clicks, email sign-ups",
            "Scale what's working — double posting on best-performing platform",
        ]},
    ]


def _content_framework(niche: dict) -> dict:
    return {
        "pillar_ratio": {"educational": "40%", "entertaining": "30%", "inspirational": "20%", "promotional": "10%"},
        "formats": niche["content_types"],
        "viral_triggers": [
            "Controversy or counterintuitive claim ('The #1 investing mistake everyone makes')",
            "Social proof ('How I made $X in Y days')",
            "Lists ('5 things you didn't know about...')",
            "Before/after transformations",
            "React/duet trending viral videos",
        ],
        "hook_templates": [
            "If you [do X], stop immediately — here's why",
            "Nobody talks about this [niche] secret...",
            "I went from [bad state] to [good state] by doing one thing",
            "The [#] biggest [niche] mistakes (and how to fix them)",
            "This [niche] trend is about to blow up — get in early",
        ],
    }


def _monetization_roadmap(niche: dict) -> list:
    return [
        {"milestone": "0-1K followers", "focus": "Content quality + consistency", "income": "$0-$50/mo", "action": "Set up affiliate links, start email list"},
        {"milestone": "1K-5K followers", "income": "$50-$500/mo", "focus": "Affiliate marketing", "action": "Post affiliate content 2x/week, grow email list to 100"},
        {"milestone": "5K-10K followers", "income": "$500-$2K/mo", "focus": "First brand deal + digital product", "action": "Pitch 10 brands/week, create first ebook"},
        {"milestone": "10K-50K followers", "income": "$2K-$10K/mo", "focus": "Scale content + multiple income streams", "action": "Hire VA for content scheduling, launch course"},
        {"milestone": "50K-100K followers", "income": "$10K-$30K/mo", "focus": "Premium brand deals + community", "action": "Charge $3K-$10K/post, launch paid community"},
        {"milestone": "100K+ followers", "income": "$30K+/mo", "focus": "Build media company", "action": "Hire team, launch multiple theme pages, speaking/consulting"},
    ]


def _tools_for_niche(niche: dict) -> dict:
    return {
        "content_creation": ["CapCut (free, TikTok-native)", "Canva Pro ($13/mo)", "InShot (mobile)"],
        "scheduling": ["Buffer (free tier)", "Later ($18/mo)", "TikTok/YouTube native scheduler"],
        "email_marketing": ["ConvertKit (free to 1K subs)", "Beehiiv (free to 2.5K)", "MailerLite"],
        "landing_page": ["Stan.store (5% fee)", "Gumroad (10% fee)", "Beacons.ai (free)"],
        "affiliate_networks": ["Amazon Associates", "ShareASale", "Impact.com", "ClickBank"],
        "analytics": ["TikTok Analytics (native)", "YouTube Studio", "Social Blade (free)"],
    }


def _roadmap_phases(level: str) -> list:
    return [
        {
            "phase": 1,
            "name": "Pick Your Niche",
            "duration": "1-2 days",
            "tasks": [
                "Run 'social-trends theme-page niches' to see ranked niche opportunities",
                "Choose based on: (1) You can post about it daily, (2) Has high monetization, (3) Not too competitive",
                "Validate: Can you create 100 video ideas in this niche right now?",
            ],
            "output": "One niche chosen. No second-guessing.",
        },
        {
            "phase": 2,
            "name": "Account Setup",
            "duration": "1 day",
            "tasks": [
                "Create accounts: TikTok + YouTube + Instagram (same username across all)",
                "Profile photo: High-res niche-related image (not your face if staying anonymous)",
                "Bio: '[Niche keyword] tips | [Benefit] | Link for [free resource] ↓'",
                "Set up Linktree with lead magnet + affiliate link",
                "Join 2-3 affiliate programs in your niche",
            ],
            "output": "Live accounts with optimized profiles.",
        },
        {
            "phase": 3,
            "name": "Content Production",
            "duration": "Day 3-7",
            "tasks": [
                "Batch-produce 21 videos in 2-3 sittings (3 weeks of content)",
                "Every video: strong hook (first 3s) + value + CTA",
                "Format: 30-60 second vertical video (works on all platforms)",
                "Add trending sound as background audio",
                "Export and store in organized folders by content type",
            ],
            "output": "21+ videos ready to post.",
        },
        {
            "phase": 4,
            "name": "Posting & Growth (30-90 days)",
            "duration": "30-90 days",
            "tasks": [
                "Post 2x daily on TikTok minimum",
                "Cross-post every video to YouTube Shorts and Instagram Reels",
                "Reply to every comment for first 6 months",
                "Track: completion rate, shares, saves — these predict virality",
                "Double down on whatever content type is performing best",
            ],
            "output": "1K-10K followers and first viral video.",
        },
        {
            "phase": 5,
            "name": "Monetization (Month 2+)",
            "duration": "Ongoing",
            "tasks": [
                "Post 1-2 affiliate recommendation videos per week",
                "Mention lead magnet in every video CTA",
                "Pitch brands for sponsorships when you hit 5K followers",
                "Create first digital product based on your top-performing content",
                "Build email list aggressively — this is your real business asset",
            ],
            "output": "First $500-$2K/month. Path to $10K+/month mapped.",
        },
    ]


def _common_mistakes() -> list:
    return [
        "Changing niches after 2 weeks — most accounts don't take off until week 8-12",
        "Posting inconsistently — the algorithm punishes gaps more than quality",
        "No CTA — every video must direct viewers to comment, follow, save, or click",
        "Ignoring analytics — check every 7 days and cut what's not working",
        "Not building an email list — platform bans can wipe out your entire business overnight",
        "Too broad a niche — 'health' is too big; 'gut health for busy moms over 40' is a niche",
        "Copying competitors exactly — differentiate by your unique angle or format",
        "Waiting for perfect before posting — volume beats perfection in the algorithm",
    ]


def _income_timeline() -> list:
    return [
        {"month": 1, "focus": "Growth", "realistic_income": "$0-$50", "milestone": "First 100 followers"},
        {"month": 2, "focus": "Growth + Affiliate Test", "realistic_income": "$50-$200", "milestone": "First 1K followers"},
        {"month": 3, "focus": "Affiliate + Email building", "realistic_income": "$200-$500", "milestone": "First 5K followers + 100 email subs"},
        {"month": 4, "focus": "First brand deal", "realistic_income": "$500-$1K", "milestone": "10K followers"},
        {"month": 6, "focus": "Digital product launch", "realistic_income": "$1K-$3K", "milestone": "25K followers + 500 email subs"},
        {"month": 9, "focus": "Scale and diversify", "realistic_income": "$3K-$8K", "milestone": "50K followers"},
        {"month": 12, "focus": "Media company", "realistic_income": "$8K-$20K+", "milestone": "100K followers + full funnel running"},
    ]


def _recommended_tools() -> dict:
    return {
        "free_to_start": [
            "CapCut — Video editing (mobile + desktop)",
            "Canva — Thumbnails, graphics, lead magnets",
            "ConvertKit — Email marketing (free to 1,000 subs)",
            "Beacons.ai — Link in bio with email capture",
            "TikTok/YouTube native schedulers",
        ],
        "paid_worth_it": [
            "Canva Pro ($13/mo) — Brand kit + magic resize for cross-platform",
            "Buffer ($6/mo) — Schedule all platforms from one dashboard",
            "stan.store ($29/mo) — Sell digital products + email list in one",
        ],
        "ai_tools": [
            "ChatGPT / Claude — Script writing and hook generation",
            "ElevenLabs — AI voiceover for faceless content",
            "Descript — Edit video by editing text transcript",
            "OpusClip — Auto-clip long videos into Shorts",
        ],
    }
