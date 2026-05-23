"""Theme page creation, growth, and conversion/monetization guide."""
from typing import Any, Dict, List, Optional
from datetime import datetime


# Profitable niches ranked by monetization potential (2024-2025 data)
PROFITABLE_NICHES = [
    {
        "rank": 1, "niche": "Finance & Investing",
        "sub_niches": ["crypto", "stocks", "passive income", "budget tips", "frugal living"],
        "avg_cpm": "$8-$15", "affiliate_potential": "HIGH",
        "best_platforms": ["YouTube", "TikTok", "Twitter"],
        "content_types": ["screen recordings", "charts/graphs", "explainer videos", "reaction"],
        "monetization": ["AdSense", "Affiliate (Coinbase, Robinhood, Webull)", "Course sales"],
        "example_accounts": ["@CashNewsDaily", "@StockBros", "@CryptoWaves"],
        "difficulty": "Medium", "competition": "High",
        "why_profitable": "High-value affiliate programs ($50-$200 per signup)",
    },
    {
        "rank": 2, "niche": "Fitness & Weight Loss",
        "sub_niches": ["gym tips", "home workouts", "meal prep", "weight loss journey", "supplements"],
        "avg_cpm": "$4-$8", "affiliate_potential": "HIGH",
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
        "content_types": ["transformation videos", "workout demos", "before/after", "meal prep"],
        "monetization": ["Brand deals", "Affiliate (MyProtein, Amazon)", "Coaching"],
        "difficulty": "Low", "competition": "Very High",
        "why_profitable": "Huge audience, year-round demand, repeat purchases",
    },
    {
        "rank": 3, "niche": "Motivational / Self-Improvement",
        "sub_niches": ["mindset", "productivity", "morning routines", "book summaries", "stoicism"],
        "avg_cpm": "$3-$7", "affiliate_potential": "MEDIUM",
        "best_platforms": ["TikTok", "Instagram", "YouTube Shorts"],
        "content_types": ["quote videos", "speech clips", "AI voiceover compilations", "tips"],
        "monetization": ["AdSense", "Merch", "Digital products", "Brand deals"],
        "difficulty": "Low", "competition": "Very High",
        "why_profitable": "Easy to create (repurpose speeches/quotes), massive audience",
    },
    {
        "rank": 4, "niche": "Luxury / Wealth Lifestyle",
        "sub_niches": ["supercars", "mansions", "yacht life", "rich lifestyle", "billionaires"],
        "avg_cpm": "$3-$6", "affiliate_potential": "MEDIUM",
        "best_platforms": ["TikTok", "Instagram", "YouTube Shorts"],
        "content_types": ["compilation videos", "showcase videos", "reaction content"],
        "monetization": ["AdSense", "Dropshipping promotion", "Account flips"],
        "difficulty": "Low", "competition": "High",
        "why_profitable": "Pure aspirational content — easy to create, great for account flipping",
    },
    {
        "rank": 5, "niche": "Tech & AI",
        "sub_niches": ["AI tools", "gadgets", "productivity apps", "software reviews", "coding"],
        "avg_cpm": "$6-$12", "affiliate_potential": "HIGH",
        "best_platforms": ["YouTube", "TikTok", "Twitter"],
        "content_types": ["screen demos", "tutorials", "unboxings", "comparisons"],
        "monetization": ["Affiliate (software SaaS)", "Sponsorships", "Course sales"],
        "difficulty": "Medium", "competition": "Medium",
        "why_profitable": "SaaS affiliate programs pay $30-$200 recurring commissions",
    },
    {
        "rank": 6, "niche": "Food & Recipes",
        "sub_niches": ["quick meals", "aesthetic food", "budget cooking", "baking", "restaurant reviews"],
        "avg_cpm": "$2-$5", "affiliate_potential": "MEDIUM",
        "best_platforms": ["TikTok", "Instagram", "YouTube Shorts"],
        "content_types": ["recipe videos", "POV cooking", "food tours", "taste tests"],
        "monetization": ["Brand deals (kitchen brands)", "Affiliate (Amazon kitchen)", "Cookbook"],
        "difficulty": "Low", "competition": "Very High",
        "why_profitable": "Consistent daily demand, low barrier to entry",
    },
    {
        "rank": 7, "niche": "Entertainment / Memes",
        "sub_niches": ["funny videos", "memes", "fails", "compilations", "reaction"],
        "avg_cpm": "$1-$3", "affiliate_potential": "LOW",
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
        "content_types": ["viral reposts", "compilations", "POV comedy", "duets"],
        "monetization": ["AdSense", "Account flips", "Shoutout sales"],
        "difficulty": "Very Low", "competition": "Extreme",
        "why_profitable": "Easiest to grow fast — perfect for theme page flipping",
    },
    {
        "rank": 8, "niche": "Pets & Animals",
        "sub_niches": ["dogs", "cats", "exotic pets", "wildlife", "animal facts"],
        "avg_cpm": "$2-$4", "affiliate_potential": "MEDIUM",
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
        "content_types": ["cute compilations", "funny moments", "facts videos"],
        "monetization": ["Brand deals (pet brands)", "Affiliate (Chewy, Amazon)", "Account flips"],
        "difficulty": "Low", "competition": "High",
        "why_profitable": "Universal appeal, algorithm-friendly, easy content creation",
    },
]

# Theme page conversion (selling) value multipliers by follower count
_SELL_MULTIPLIERS = {
    "tiktok": {1_000: 0.5, 5_000: 1.0, 10_000: 2.0, 50_000: 5.0, 100_000: 10.0},
    "instagram": {1_000: 1.0, 5_000: 2.5, 10_000: 5.0, 50_000: 20.0, 100_000: 50.0},
    "youtube": {1_000: 5.0, 5_000: 15.0, 10_000: 30.0, 50_000: 100.0, 100_000: 250.0},
    "twitter": {1_000: 0.3, 5_000: 1.0, 10_000: 2.0, 50_000: 5.0, 100_000: 10.0},
}

# Marketplace sites for selling/buying social media accounts
ACCOUNT_MARKETPLACES = [
    {
        "name": "Fameswap",
        "url": "fameswap.com",
        "platforms": ["Instagram", "TikTok", "YouTube", "Twitter"],
        "fee": "15% seller fee",
        "best_for": "Instagram accounts",
        "trust_level": "HIGH",
    },
    {
        "name": "Social Tradia",
        "url": "socialtradia.com",
        "platforms": ["Instagram", "TikTok"],
        "fee": "10% fee",
        "best_for": "Instagram accounts over 10K",
        "trust_level": "HIGH",
    },
    {
        "name": "Flippa",
        "url": "flippa.com",
        "platforms": ["YouTube", "Websites", "Apps"],
        "fee": "10-15% + listing fee",
        "best_for": "Monetized YouTube channels",
        "trust_level": "HIGH",
    },
    {
        "name": "PlayerUp",
        "url": "playerup.com",
        "platforms": ["All"],
        "fee": "15% middleman service",
        "best_for": "All platforms, larger accounts",
        "trust_level": "MEDIUM",
    },
    {
        "name": "Accs-market",
        "url": "accs-market.com",
        "platforms": ["All"],
        "fee": "Varies",
        "best_for": "Aged accounts, smaller accounts",
        "trust_level": "MEDIUM",
    },
]

_CONTENT_REPURPOSING_STRATEGY = {
    "one_to_many": {
        "description": "Create ONE piece of content and post it to EVERY platform",
        "workflow": [
            "Film/create primary video (vertical 9:16 format)",
            "Post to TikTok first (highest organic reach)",
            "Cross-post to Instagram Reels (same video, no watermark)",
            "Post to YouTube Shorts",
            "Cut to horizontal for YouTube long-form if applicable",
            "Create static image from thumbnail → post to Twitter/Facebook",
        ],
        "tools": ["CapCut (free)", "InShot (free)", "Canva (captions/thumbnails)"],
        "time_saved": "80% vs creating separate content per platform",
    },
}


def get_theme_page_guide(niche: str = "", platform: str = "all") -> Dict[str, Any]:
    """
    Complete guide for creating and converting (monetizing/selling) theme pages.
    """
    niche_data = None
    if niche:
        niche_lower = niche.lower()
        for n in PROFITABLE_NICHES:
            if niche_lower in n["niche"].lower() or any(
                niche_lower in sub for sub in n["sub_niches"]
            ):
                niche_data = n
                break

    guide = {
        "what_is_theme_page": {
            "definition": (
                "A theme page is a social media account built around a specific topic/niche "
                "rather than a personal brand. Content is curated, reposted, or created around "
                "the theme. The owner stays anonymous — the THEME is the brand."
            ),
            "examples": [
                "@NatureEarth (nature content) — 10M+ followers",
                "@MotivationMafia (quote/speech clips) — built to 500K, sold for $12K",
                "@LuxuryCarsDaily (supercar content) — 1M followers, $2K/month AdSense",
                "@CryptoNewsNow (finance news) — built to 50K in 3 months",
            ],
            "why_theme_pages": [
                "No face on camera required",
                "Easy to scale with a posting schedule",
                "Can be built and sold ('flipped') for profit",
                "Multiple accounts = multiple income streams",
                "Outsource to a VA once profitable",
            ],
        },
        "phase_1_setup": {
            "title": "Phase 1: Account Setup (Day 1-3)",
            "steps": [
                {
                    "step": 1,
                    "action": "Choose your niche",
                    "detail": (
                        f"{'Your niche: ' + niche if niche else 'Pick from profitable niches list'}"
                        " — Focus on ONE sub-niche for faster algorithm trust"
                    ),
                },
                {
                    "step": 2,
                    "action": "Create the account",
                    "detail": (
                        "Username: [niche][keyword][word] e.g. 'WealthWavesDaily', "
                        "'MotivationNationFit'. Same username across all platforms."
                    ),
                },
                {
                    "step": 3,
                    "action": "Optimize profile",
                    "detail": (
                        "Profile pic: eye-catching niche image or clean logo. "
                        "Bio: '[Niche content] daily | Follow for [value] | Link in bio'. "
                        "Add Linktree/Beacons link immediately."
                    ),
                },
                {
                    "step": 4,
                    "action": "Content bank",
                    "detail": (
                        "Before posting, prepare 30 pieces of content. "
                        "Sources: Reddit, Pinterest, YouTube, other viral accounts "
                        "(always credit original creators to avoid strikes)."
                    ),
                },
                {
                    "step": 5,
                    "action": "Branding",
                    "detail": (
                        "Create a consistent visual style: color palette, font, watermark. "
                        "Use Canva for free templates. Apply to ALL content."
                    ),
                },
            ],
        },
        "phase_2_growth": {
            "title": "Phase 2: Growth Strategy (Day 4-90)",
            "strategies": [
                {
                    "strategy": "Volume Posting",
                    "platform": "TikTok",
                    "detail": "Post 3-5x/day for first 30 days. Volume is king on TikTok.",
                    "expected_result": "1K-10K followers in first month",
                },
                {
                    "strategy": "Follow/Engage Loop",
                    "platform": "Instagram",
                    "detail": (
                        "Follow 50 accounts in niche/day. "
                        "Like + comment 100 posts/day. "
                        "1-3% will follow back."
                    ),
                    "expected_result": "500-2K followers/month organic",
                },
                {
                    "strategy": "Trending Audio Hijack",
                    "platform": "TikTok/Reels",
                    "detail": (
                        "Find a trending sound → create content with that sound → "
                        "get pushed to trending page. Check weekly with this tool."
                    ),
                    "expected_result": "Potential 10K-1M views per viral post",
                },
                {
                    "strategy": "Hashtag Stacking",
                    "platform": "All",
                    "detail": (
                        "Use 3 niche-specific + 3 mid-size + 3 broad hashtags. "
                        "Rotate your hashtag sets to avoid shadowban."
                    ),
                    "expected_result": "3-5x more discoverability",
                },
                {
                    "strategy": "Shoutout For Shoutout (S4S)",
                    "platform": "Instagram/TikTok",
                    "detail": (
                        "DM similar-sized accounts for mutual shoutouts. "
                        "Target accounts 0.5x-2x your follower count."
                    ),
                    "expected_result": "Consistent +200-1000 followers per swap",
                },
                {
                    "strategy": "Paid Shoutouts",
                    "platform": "Instagram",
                    "detail": (
                        "Buy shoutouts from larger accounts in your niche. "
                        "Budget: $10-$50 per shoutout. ROI: 50-500 new followers."
                    ),
                    "expected_result": "Fast track to 10K",
                },
            ],
        },
        "phase_3_monetization": {
            "title": "Phase 3: Monetization (After 1K+ followers)",
            "revenue_streams": [
                {
                    "method": "Affiliate Marketing",
                    "when_to_start": "Immediately (even at 0 followers)",
                    "how": (
                        "Add affiliate links to bio (Linktree). "
                        "Create content that naturally recommends products. "
                        "Best programs: Amazon Associates, ClickBank, ShareASale, "
                        "individual brand programs."
                    ),
                    "earning_potential": "$100-$10K+/month depending on niche and traffic",
                },
                {
                    "method": "Paid Shoutouts (Selling)",
                    "when_to_start": "10K+ followers",
                    "how": (
                        "Brands and other creators pay YOU to post. "
                        "Rate: $10-$50 per post at 10K, $100-$500 at 100K. "
                        "Use platforms: Shoutcart, Collabstr, direct DMs."
                    ),
                    "earning_potential": "$500-$5K/month at 50K followers",
                },
                {
                    "method": "AdSense / TikTok Creator Fund",
                    "when_to_start": "YouTube: 1K subs + 4K watch hours | TikTok: 10K followers",
                    "how": "Enable monetization in platform settings. Passive income.",
                    "earning_potential": "$1-$5 per 1K views (varies by niche/CPM)",
                },
                {
                    "method": "Digital Products",
                    "when_to_start": "5K+ engaged followers",
                    "how": (
                        "Create an ebook, template, or mini-course. "
                        "Price: $7-$97. Sell via Gumroad or Beacons. "
                        "One post can generate $500-$5K in sales."
                    ),
                    "earning_potential": "$500-$50K+ per product launch",
                },
                {
                    "method": "Account Flipping (Selling the Account)",
                    "when_to_start": "10K-100K followers",
                    "how": (
                        "Build account to target follower count → List on Fameswap/Flippa. "
                        "Include engagement rate, niche, and growth screenshots. "
                        "Negotiate via escrow for safety."
                    ),
                    "earning_potential": (
                        "10K Instagram: $500-$2K | "
                        "50K Instagram: $2K-$10K | "
                        "100K TikTok: $500-$3K | "
                        "10K YouTube (monetized): $3K-$15K"
                    ),
                },
            ],
        },
        "phase_4_selling": {
            "title": "Phase 4: Selling the Account (Account Flipping)",
            "preparation": [
                "Document all account stats: followers, avg views, engagement rate, monthly growth",
                "Screenshot your analytics from platform's Creator Studio",
                "Note any brand deals or affiliate income (proof of monetization = higher price)",
                "Remove personal info if you want anonymity",
                "Ensure account has no copyright strikes or TOS violations",
            ],
            "pricing_formula": (
                "Instagram: $10 per 1,000 followers (engaged) — MINIMUM price. "
                "Monetized accounts: 12-24x monthly revenue. "
                "YouTube channels: 24-48x monthly AdSense. "
                "High-engagement = higher multiplier."
            ),
            "marketplaces": ACCOUNT_MARKETPLACES,
            "negotiation_tips": [
                "Never transfer before payment — use escrow.com or platform escrow",
                "Provide a video walkthrough of account analytics",
                "Start price 30% higher than target to allow negotiation room",
                "Bundle multiple accounts for higher total price",
                "Fastest sales: niche pages with proven engagement > 3% rate",
            ],
            "watch_out": [
                "Never give login details before payment clears",
                "Beware of 'PayPal Friends & Family' scams — use escrow",
                "Some buyers will claim the account was 'different than described' for refunds",
                "Bot followers destroy account value — keep organic only",
            ],
        },
        "content_repurposing": _CONTENT_REPURPOSING_STRATEGY,
        "tools_stack": {
            "content_creation": [
                "CapCut — free video editing, trending effects",
                "Canva — graphics, thumbnails, story templates",
                "InShot — quick mobile video editing",
            ],
            "scheduling": [
                "Later — Instagram/TikTok scheduler",
                "Buffer — multi-platform scheduler (free tier)",
                "TikTok Creator Studio — native scheduling",
            ],
            "analytics": [
                "Social Blade — free follower growth tracking",
                "HypeAuditor — engagement rate checker",
                "TikTok Creator Studio — built-in analytics",
            ],
            "sourcing_content": [
                "Pinterest — viral image/video ideas",
                "Reddit (r/all, niche subs) — trending topics",
                "YouTube Trending — repurpose for Shorts/Reels",
                "Google Trends — topic popularity over time",
            ],
            "monetization": [
                "Linktree / Beacons — link in bio page",
                "Gumroad — sell digital products",
                "ClickBank / ShareASale — affiliate programs",
                "Shoutcart / Collabstr — sell shoutouts",
                "Fameswap / Flippa — sell accounts",
            ],
        },
        "30_day_action_plan": _build_30_day_plan(niche or "your niche"),
        "scraped_at": datetime.utcnow().isoformat(),
    }

    if niche_data:
        guide["your_niche_analysis"] = niche_data

    return guide


def find_profitable_niches(
    filter_difficulty: Optional[str] = None,
    filter_platform: Optional[str] = None,
    sort_by: str = "rank",
) -> List[Dict]:
    """Return ranked list of profitable niches with filters."""
    results = PROFITABLE_NICHES.copy()

    if filter_difficulty:
        results = [n for n in results if n["difficulty"].lower() == filter_difficulty.lower()]
    if filter_platform:
        results = [
            n for n in results
            if any(filter_platform.lower() in p.lower() for p in n["best_platforms"])
        ]

    if sort_by == "affiliate_potential":
        order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        results = sorted(results, key=lambda x: order.get(x["affiliate_potential"], 3))
    elif sort_by == "difficulty":
        order = {"Very Low": 0, "Low": 1, "Medium": 2, "High": 3, "Very High": 4}
        results = sorted(results, key=lambda x: order.get(x["difficulty"], 5))

    return results


def estimate_account_value(
    platform: str,
    followers: int,
    monthly_revenue: float = 0.0,
    engagement_rate: float = 0.0,
    niche: str = "",
) -> Dict[str, Any]:
    """Estimate the sale value of a social media account."""
    platform = platform.lower()

    # Base value from follower count
    multipliers = _SELL_MULTIPLIERS.get(platform, _SELL_MULTIPLIERS["instagram"])
    thresholds = sorted(multipliers.keys())

    base_per_k = 1.0
    for t in thresholds:
        if followers >= t:
            base_per_k = multipliers[t]
    base_value = (followers / 1000) * base_per_k

    # Revenue multiplier
    if monthly_revenue > 0:
        revenue_value = monthly_revenue * 24  # 24x monthly revenue
        value = max(base_value, revenue_value)
    else:
        value = base_value

    # Engagement rate bonus
    if engagement_rate >= 5.0:
        value *= 2.0
        engagement_tier = "Excellent (2x multiplier)"
    elif engagement_rate >= 3.0:
        value *= 1.5
        engagement_tier = "Good (1.5x multiplier)"
    elif engagement_rate >= 1.0:
        engagement_tier = "Average (no bonus)"
    else:
        value *= 0.5
        engagement_tier = "Poor (0.5x penalty)"

    # Niche premium
    high_value_niches = ["finance", "investing", "crypto", "tech", "ai", "health", "fitness"]
    niche_multiplier = 1.0
    if niche and any(kw in niche.lower() for kw in high_value_niches):
        niche_multiplier = 1.3
        niche_note = f"High-value niche (+30% premium)"
    else:
        niche_note = "Standard niche"

    value *= niche_multiplier
    low_est = value * 0.7
    high_est = value * 1.4

    return {
        "platform": platform,
        "followers": followers,
        "estimated_value_usd": round(value, 2),
        "value_range": f"${low_est:,.0f} - ${high_est:,.0f}",
        "base_value": round(base_value, 2),
        "revenue_multiplier": f"{monthly_revenue * 24:,.0f} (24x monthly)" if monthly_revenue else "N/A",
        "engagement_tier": engagement_tier,
        "niche_note": niche_note,
        "where_to_sell": [m["name"] for m in ACCOUNT_MARKETPLACES[:3]],
        "tips": [
            "Higher engagement rate = higher price (always)",
            "Monetized accounts sell for 3-10x non-monetized",
            "Package with sister accounts for bundle premium",
            "Best time to sell: after a viral spike in growth",
        ],
    }


def _build_30_day_plan(niche: str) -> List[Dict]:
    """Generate a 30-day theme page launch plan."""
    return [
        {
            "week": "Week 1 (Days 1-7)",
            "focus": "Setup & Content Bank",
            "tasks": [
                f"Day 1: Create accounts on TikTok + Instagram + YouTube (same handle)",
                "Day 1: Optimize all profiles (bio, pfp, Linktree with affiliate links)",
                f"Day 2-4: Source 30 pieces of {niche} content for your content bank",
                "Day 5: Create brand visuals (logo, color palette, watermark) in Canva",
                "Day 6-7: Edit and schedule first 7 posts (1/day on TikTok, 3 on Instagram)",
            ],
        },
        {
            "week": "Week 2 (Days 8-14)",
            "focus": "First 100 Followers",
            "tasks": [
                "Post 2x/day on TikTok, 1x/day on Instagram Reels",
                f"Engage 30 min/day: like + comment on top {niche} accounts",
                "Find 3 trending sounds and create content using them",
                "DM 5 similar-sized accounts for S4S (shoutout for shoutout)",
                "Track which posts perform best — double down on that format",
            ],
        },
        {
            "week": "Week 3 (Days 15-21)",
            "focus": "Hit 500-1K Followers",
            "tasks": [
                "Increase to 3x/day on TikTok during peak hours (6am, 12pm, 7pm)",
                "Identify your top 3 performing content formats — only post those",
                "Set up affiliate links for at least 2 programs in your niche",
                "Create your first 'value post' (tips/how-to) — saves = algorithm boost",
                "Cross-promote between platforms in every post caption",
            ],
        },
        {
            "week": "Week 4 (Days 22-30)",
            "focus": "Monetization Foundation",
            "tasks": [
                "Run `social trends combined` to catch the latest viral trends",
                "Create content around top 3 trending hashtags from this tool",
                "Join 2 affiliate programs and add links to Linktree",
                "At 1K followers: apply for TikTok Creator Fund",
                "Document your growth stats for potential future account sale",
                "Plan Month 2: scale what works, cut what doesn't",
            ],
        },
    ]
