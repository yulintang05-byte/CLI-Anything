from typing import Any, Dict, List

PROFITABLE_NICHES: Dict[str, Dict[str, Any]] = {
    "finance_investing": {
        "cpm_range": "$20-60",
        "avg_rpm": "$40",
        "audience": "22-40, middle-to-high income",
        "monetization": ["affiliate (financial products)", "courses", "consulting"],
        "difficulty": "High",
        "competition": "Medium-High",
        "growth_speed": "Slow",
        "conversion_rate": "3-8%",
    },
    "make_money_online": {
        "cpm_range": "$15-45",
        "avg_rpm": "$30",
        "audience": "18-35, income-seekers",
        "monetization": ["course sales", "affiliate", "coaching"],
        "difficulty": "Medium",
        "competition": "Very High",
        "growth_speed": "Fast",
        "conversion_rate": "5-10%",
    },
    "tech_ai": {
        "cpm_range": "$15-40",
        "avg_rpm": "$30",
        "audience": "20-40, tech-savvy",
        "monetization": ["software affiliates", "courses", "consulting"],
        "difficulty": "Medium-High",
        "competition": "Medium",
        "growth_speed": "Very Fast",
        "conversion_rate": "4-8%",
    },
    "luxury_lifestyle": {
        "cpm_range": "$15-50",
        "avg_rpm": "$25",
        "audience": "25-45, high income",
        "monetization": ["luxury brand affiliates", "sponsored posts", "digital products"],
        "difficulty": "Medium",
        "competition": "High",
        "growth_speed": "Slow-Medium",
        "conversion_rate": "2-5%",
    },
    "motivation_mindset": {
        "cpm_range": "$10-25",
        "avg_rpm": "$18",
        "audience": "18-35, self-improvement focused",
        "monetization": ["courses", "ebooks", "coaching", "affiliate"],
        "difficulty": "Low-Medium",
        "competition": "High",
        "growth_speed": "Fast",
        "conversion_rate": "3-7%",
    },
    "fitness_health": {
        "cpm_range": "$8-20",
        "avg_rpm": "$12",
        "audience": "18-35, health-conscious",
        "monetization": ["supplement affiliates", "fitness programs", "coaching"],
        "difficulty": "Medium",
        "competition": "Very High",
        "growth_speed": "Fast",
        "conversion_rate": "2-4%",
    },
    "pets": {
        "cpm_range": "$8-18",
        "avg_rpm": "$12",
        "audience": "25-45, pet owners",
        "monetization": ["pet product affiliates", "ebooks", "training guides"],
        "difficulty": "Low",
        "competition": "Medium",
        "growth_speed": "Fast",
        "conversion_rate": "4-8%",
    },
    "travel": {
        "cpm_range": "$5-15",
        "avg_rpm": "$8",
        "audience": "25-45, travel enthusiasts",
        "monetization": ["booking affiliates", "travel card affiliate", "photography presets"],
        "difficulty": "High",
        "competition": "High",
        "growth_speed": "Medium",
        "conversion_rate": "1-3%",
    },
    "beauty_fashion": {
        "cpm_range": "$5-15",
        "avg_rpm": "$10",
        "audience": "16-30, fashion-forward",
        "monetization": ["brand deals", "affiliate (fashion/beauty)", "digital lookbooks"],
        "difficulty": "Medium",
        "competition": "Very High",
        "growth_speed": "Fast",
        "conversion_rate": "3-6%",
    },
    "food_cooking": {
        "cpm_range": "$5-12",
        "avg_rpm": "$8",
        "audience": "25-50, home cooks",
        "monetization": ["kitchen affiliates", "cookbooks", "meal plans"],
        "difficulty": "Low-Medium",
        "competition": "Very High",
        "growth_speed": "Medium-Fast",
        "conversion_rate": "2-4%",
    },
}

_AFFILIATE_PROGRAMS: Dict[str, List[Dict[str, str]]] = {
    "finance_investing": [
        {"name": "Robinhood", "commission": "$5-15/signup", "cookie": "30 days"},
        {"name": "Coinbase", "commission": "$10/signup", "cookie": "30 days"},
        {"name": "Personal Capital", "commission": "$100/lead", "cookie": "30 days"},
        {"name": "Credit Karma", "commission": "$2-5/lead", "cookie": "30 days"},
    ],
    "make_money_online": [
        {"name": "ClickBank (MMO products)", "commission": "50-75%", "cookie": "60 days"},
        {"name": "Hostinger", "commission": "60-80%", "cookie": "30 days"},
        {"name": "Convertkit", "commission": "30% recurring", "cookie": "60 days"},
        {"name": "Shopify", "commission": "$150/referral", "cookie": "30 days"},
    ],
    "tech_ai": [
        {"name": "Jasper AI", "commission": "30% recurring", "cookie": "60 days"},
        {"name": "NordVPN", "commission": "40-100%", "cookie": "30 days"},
        {"name": "Coursera", "commission": "15-45%", "cookie": "30 days"},
        {"name": "AppSumo", "commission": "5-100%", "cookie": "30 days"},
    ],
    "fitness_health": [
        {"name": "MyProtein", "commission": "8%", "cookie": "30 days"},
        {"name": "GNC", "commission": "5-8%", "cookie": "7 days"},
        {"name": "ClickBank (fitness products)", "commission": "50-75%", "cookie": "60 days"},
        {"name": "Amazon (sports & outdoors)", "commission": "3-4%", "cookie": "24 hours"},
    ],
    "beauty_fashion": [
        {"name": "Sephora", "commission": "5-10%", "cookie": "24 hours"},
        {"name": "SHEIN", "commission": "10-20%", "cookie": "30 days"},
        {"name": "LTK / RewardStyle", "commission": "10-20%", "cookie": "30 days"},
        {"name": "Amazon Fashion", "commission": "4-10%", "cookie": "24 hours"},
    ],
}

_DEFAULT_AFFILIATES = [
    {"name": "Amazon Associates", "commission": "1-10%", "cookie": "24 hours"},
    {"name": "ShareASale", "commission": "Varies", "cookie": "30-90 days"},
    {"name": "ClickBank", "commission": "50-75%", "cookie": "60 days"},
    {"name": "Impact.com", "commission": "Varies", "cookie": "Varies"},
]

_PLATFORM_PICKS: Dict[str, List[Dict[str, str]]] = {
    "finance_investing": [
        {"platform": "TikTok", "reason": "#FinTok community is massive", "priority": "1"},
        {"platform": "YouTube", "reason": "High CPM ($20-60), loyal audience", "priority": "2"},
        {"platform": "Twitter/X", "reason": "Finance debates drive newsletter subs", "priority": "3"},
    ],
    "tech_ai": [
        {"platform": "TikTok", "reason": "#TechTok growing fastest of any niche", "priority": "1"},
        {"platform": "YouTube", "reason": "High CPM, tutorial content dominates SEO", "priority": "2"},
        {"platform": "Twitter/X", "reason": "Thought leadership, dev community", "priority": "3"},
    ],
    "beauty_fashion": [
        {"platform": "TikTok", "reason": "Viral potential is highest here", "priority": "1"},
        {"platform": "Instagram", "reason": "Visual platform, brand deal pipeline", "priority": "2"},
        {"platform": "Pinterest", "reason": "Long-tail traffic drives affiliate sales", "priority": "3"},
    ],
    "fitness_health": [
        {"platform": "TikTok", "reason": "Transformation content goes viral fast", "priority": "1"},
        {"platform": "Instagram", "reason": "Strong fitness community, brand deals", "priority": "2"},
        {"platform": "YouTube", "reason": "Long-form workouts earn recurring subs", "priority": "3"},
    ],
}

_DEFAULT_PLATFORMS = [
    {"platform": "TikTok", "reason": "Highest organic reach potential for new accounts", "priority": "1"},
    {"platform": "Instagram", "reason": "Brand deals, shopping features, Reels reach", "priority": "2"},
    {"platform": "YouTube", "reason": "Long-term revenue, evergreen SEO, high CPM", "priority": "3"},
]

_CONTENT_IDEAS: Dict[str, List[str]] = {
    "finance_investing": [
        "How I made my first $1,000 online",
        "Investing $100/month for 10 years (compound interest reveal)",
        "Side hustles that actually work in 2025",
        "Things wealthy people do that broke people don't",
        "How to build passive income from scratch",
        "Credit score hacks most people don't know",
        "My investing portfolio breakdown (transparent)",
    ],
    "tech_ai": [
        "AI tools that will save you 10 hours a week",
        "ChatGPT prompts nobody talks about",
        "I tested 10 AI tools so you don't have to",
        "Free tools that replaced $500/month of software",
        "How I use AI to make money online",
        "My full home office / tech setup tour",
        "The software that 10x'd my productivity",
    ],
    "fitness_health": [
        "5-minute morning workout anyone can do",
        "What I eat in a day (high protein, easy meals)",
        "Gym beginner mistakes that kill progress",
        "Before/after 90-day transformation reveal",
        "Reviewing viral workout trends (honest takes)",
        "Foods that accelerate fat loss",
        "My full weekly training split",
    ],
    "beauty_fashion": [
        "Dupe for $500 luxury item that costs $30",
        "Get ready with me (GRWM) for event",
        "Ranking viral beauty trends: hot or not?",
        "Outfits under $50 that look expensive",
        "My 5-step skincare routine for glowing skin",
        "Full glam using only drugstore products",
        "Unboxing the most hyped products of the month",
    ],
}

_DEFAULT_IDEAS = [
    "{niche} tips beginners need to know",
    "The truth about {niche} nobody tells you",
    "My {niche} journey: 0 to results",
    "Viral {niche} trends ranked",
    "Common {niche} mistakes to avoid",
    "How to get started with {niche} in 2025",
    "Best free {niche} resources",
]

THEME_PAGE_PLAYBOOK = """
╔══════════════════════════════════════════════════════════════╗
║           THEME PAGE COMPLETE PLAYBOOK (2025)               ║
╚══════════════════════════════════════════════════════════════╝

PHASE 1 — NICHE SELECTION (Week 1)
────────────────────────────────────
Pick a niche where:
  • CPM / RPM is $10+ (run: social-trends theme-pages niches)
  • You have a knowledge or passion edge
  • Clear affiliate/product monetisation path exists
  • Competitor accounts at 100K-1M have good engagement

Validate before posting:
  1. Search niche on TikTok → look for 50-200K accounts doing well
  2. Check if brand sponsorships are active in that niche
  3. Find 3+ affiliate programs paying 10%+ commission
  4. Confirm search volume via Google Trends

PHASE 2 — ACCOUNT SETUP (Week 1)
───────────────────────────────────
Username pattern: [niche]_[descriptor]
  Examples: luxury_mindset, tech_alpha, daily_finance_tips

Profile optimisation:
  ✓ HD, on-brand profile photo
  ✓ Bio: keyword-rich + clear CTA ("Follow for daily X tips")
  ✓ Link-in-bio tool: Beacons, Stan Store, or Linktree
  ✓ Creator/Business account enabled
  ✓ Affiliate accounts registered BEFORE first post

Run: social-trends optimize audit <platform> <username>
for a full profile checklist.

PHASE 3 — CONTENT PRODUCTION (Ongoing)
─────────────────────────────────────────
Content pillars (rotate 3-5 themes):
  40% Educational (how-to, tips, facts, data)
  30% Entertainment (relatable, funny, trending)
  20% Promotional (products — MAX 20%)
  10% Community (polls, Q&A, comments response)

Viral format checklist:
  ✓ Hook in first 1-3 seconds (question, shock stat, visual)
  ✓ 15-60 second runtime for maximum completion rate
  ✓ "Part 1 of..." series → drives follows
  ✓ Trending audio (check TikTok Discover + YouTube trending)
  ✓ Subtitles/captions (85% watch on mute)
  ✓ Loop structure (last frame → first frame)

Run: social-trends tiktok sounds  — for trending audio
Run: social-trends youtube music  — for trending music

PHASE 4 — GROWTH STRATEGY (Months 1-3)
─────────────────────────────────────────
Posting frequency:
  TikTok:           3-5 videos/day
  Instagram Reels:  1-2/day + 5 Stories
  YouTube Shorts:   1-2/day

Algorithm triggers:
  ✓ Strong watch-time (aim >80% completion)
  ✓ High save rate (save = strongest signal on IG/TT)
  ✓ Reply to EVERY comment for first 24h after posting
  ✓ Stitch/Duet trending content in your niche
  ✓ Post at peak times (run: social-trends optimize posting-times)

Hashtag strategy by platform:
  TikTok:    3-5 tags → run: social-trends optimize hashtags tiktok <niche>
  Instagram: 15-20 tags → run: social-trends optimize hashtags instagram <niche>
  YouTube:   3-5 tags in title + description

PHASE 5 — MONETISATION (10K+ followers)
──────────────────────────────────────────
Revenue streams (stack them):

1. AFFILIATE MARKETING
   • Add affiliate links to bio (Linktree)
   • Create "products I use" content
   • Run: social-trends theme-pages analyze <niche> → see affiliate programs

2. BRAND SPONSORSHIPS
   • Outreach template: "I noticed you worked with [similar creator]..."
   • Rates: $50-$300 per 10K followers per post
   • Create a media kit (follower count, engagement rate, niche, demographics)

3. DIGITAL PRODUCTS (highest margin)
   • Ebook: $7-$47 (1-2 weeks to create)
   • Template pack: $17-$97
   • Mini course: $97-$497
   • 1:1 coaching: $100-$1,000/session

4. PLATFORM NATIVE
   • TikTok Creator Fund / LIVE gifts
   • YouTube AdSense (1K subs + 4K watch hours)
   • Instagram Bonus / Gifts

5. SHOUTOUTS (side income while growing)
   • Sell promo slots to smaller accounts ($50-$500/post)
   • List yourself on Shoutcart or direct DMs

PHASE 6 — SCALING (Months 3-6+)
──────────────────────────────────
Scale operations:
  1. Hire video editor (Fiverr $5-$50/video) — removes bottleneck
  2. Batch-produce content 2-3x/week → queue for daily posting
  3. Build 2-5 theme pages in related niches
  4. Cross-promote between your own accounts

Own your audience:
  • Email list via lead magnet (free guide in bio)
  • Build community: Discord, Telegram, or Circle
  • Email newsletter → highest conversion rate of any channel

Diversify platforms (in this order):
  TikTok → Instagram → YouTube Shorts → Pinterest → Twitter/X

CONVERTING YOUR THEME PAGE
═══════════════════════════
"Converting" = turning followers into revenue.

Conversion tactics (stack all of these):
  1. CTA in EVERY post caption ("Comment X", "Link in bio")
  2. Story highlights for products/services
  3. Bridge content → teaches value then directs to offer
  4. Retargeting pixel on your website (Meta Pixel, TT Pixel)
  5. Email capture with irresistible lead magnet
  6. Limited-time offers to trigger urgency
  7. Social proof (testimonials, screenshots, income reveal)
  8. Community building → high-LTV customers

REVENUE BENCHMARKS (by follower count)
────────────────────────────────────────
  10K followers  →  $100-$500/month
  50K followers  →  $500-$2,500/month
  100K followers →  $1,000-$10,000/month
  500K followers →  $5,000-$50,000/month
  1M+ followers  →  $10,000-$100,000+/month

Note: Varies widely by niche CPM, engagement rate, and
monetisation diversity. Finance/Tech niches earn 3-5x
more than Beauty/Food at the same follower count.

Run: social-trends theme-pages analyze <niche>
for revenue estimates specific to your niche.
"""


def get_all_niches() -> List[Dict[str, Any]]:
    result = []
    for key, data in PROFITABLE_NICHES.items():
        result.append({
            "niche": key.replace("_", " ").title(),
            "cpm_range": data["cpm_range"],
            "avg_rpm": data["avg_rpm"],
            "difficulty": data["difficulty"],
            "competition": data["competition"],
            "growth_speed": data["growth_speed"],
            "top_monetization": data["monetization"][0] if data["monetization"] else "N/A",
        })
    result.sort(key=lambda x: float(x["avg_rpm"].replace("$", "")), reverse=True)
    return result


def get_niche_analysis(niche: str) -> Dict[str, Any]:
    key = niche.lower().replace(" ", "_").replace("-", "_")
    data = PROFITABLE_NICHES.get(key)
    if not data:
        for k, v in PROFITABLE_NICHES.items():
            if key in k or k in key:
                key, data = k, v
                break

    if not data:
        return {
            "niche": niche,
            "note": "Specific data not available — generic guidance below.",
            "recommendations": [
                "Search competitor accounts to gauge competition",
                "Find affiliate programs in this niche (ClickBank, Impact, ShareASale)",
                "Analyse CPM via YouTube Studio once you have a channel",
                "Reach out to brands in adjacent niches for early deals",
            ],
            "playbook": THEME_PAGE_PLAYBOOK,
        }

    avg_rpm = float(data["avg_rpm"].replace("$", ""))
    conv_low = float(data["conversion_rate"].split("-")[0].replace("%", "")) / 100

    return {
        "niche": key.replace("_", " ").title(),
        "data": data,
        "revenue_estimates": {
            "10K_followers": {
                "ad_rev_monthly": f"${int(10_000 * 0.001 * avg_rpm * 30):,}",
                "affiliate_monthly": f"${int(10_000 * conv_low * 0.05 * 30):,}",
                "brand_deals": "$100-$500/post",
            },
            "100K_followers": {
                "ad_rev_monthly": f"${int(100_000 * 0.001 * avg_rpm * 30):,}",
                "affiliate_monthly": f"${int(100_000 * conv_low * 0.05 * 30):,}",
                "brand_deals": "$500-$5,000/post",
            },
            "1M_followers": {
                "ad_rev_monthly": f"${int(1_000_000 * 0.001 * avg_rpm * 30):,}",
                "affiliate_monthly": f"${int(1_000_000 * conv_low * 0.05 * 30):,}",
                "brand_deals": "$5,000-$50,000/post",
            },
        },
        "recommended_platforms": _PLATFORM_PICKS.get(key, _DEFAULT_PLATFORMS),
        "affiliate_programs": _AFFILIATE_PROGRAMS.get(key, _DEFAULT_AFFILIATES),
        "content_ideas": _CONTENT_IDEAS.get(key, [t.format(niche=niche) for t in _DEFAULT_IDEAS]),
        "playbook_hint": "Run: social-trends theme-pages playbook  for the full step-by-step guide",
    }


def get_theme_page_playbook() -> str:
    return THEME_PAGE_PLAYBOOK
