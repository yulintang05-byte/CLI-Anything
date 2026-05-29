"""Theme page strategy, niche data, and conversion guide."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from cli_anything.social_trends.core.store import Store

# ── Niche intelligence database ──────────────────────────────────────────────

NICHE_DATA: Dict[str, Dict[str, Any]] = {
    "fitness": {
        "name": "Fitness",
        "conversion_potential": 9.2,
        "estimated_rpm": "$4-8",
        "estimated_cpm": "$6-12",
        "conversion_rate_benchmark": "2.5-4.0%",
        "avg_follower_value": "$0.05-$0.15",
        "best_content_formats": [
            "Before/after transformation reels (60-90s)",
            "Quick workout tutorials (15-30s)",
            "Day-in-life fitness vlogs",
            "Nutrition myth-busting",
            "Motivation compilations with trending audio",
        ],
        "monetization_strategies": [
            "Custom workout plans ($19-$49)",
            "Online coaching ($99-$499/month)",
            "Supplement affiliate programs (10-30% commission)",
            "Brand sponsorships (sports brands, apparel)",
            "YouTube AdSense (high RPM niche)",
            "Paid community / Discord ($9-$29/month)",
        ],
        "conversion_tactics": [
            "Use before/after hooks in first 3 seconds",
            "Give free value then pitch paid program",
            "Build email list with free workout plan lead magnet",
            "Testimonial content builds social proof",
            "Story polls to understand audience pain points",
        ],
        "audience_demographics": "18-35, 60% female, health-conscious, aspirational",
        "top_platforms": ["instagram", "tiktok", "youtube"],
        "competitor_examples": [
            "Large transformation-focused page (1M+ followers, sells coaching)",
            "Calisthenics tutorial page (500K+, sells PDF programs)",
            "Nutrition education page (800K+, sells meal plans)",
        ],
        "content_cadence": "3-5x/day TikTok, 1-2x/day Instagram, 3x/week YouTube",
        "avg_growth_rate": "2-5% per week if consistent",
    },
    "finance": {
        "name": "Finance",
        "conversion_potential": 9.8,
        "estimated_rpm": "$8-20",
        "estimated_cpm": "$15-40",
        "conversion_rate_benchmark": "3.0-5.5%",
        "avg_follower_value": "$0.10-$0.40",
        "best_content_formats": [
            "Money tips in under 60 seconds",
            "Reaction to financial news",
            "Step-by-step investment breakdowns",
            "Personal finance storytelling",
            "Income/savings milestones",
        ],
        "monetization_strategies": [
            "Financial courses ($97-$497)",
            "Affiliate: brokerage platforms (up to $500/referral)",
            "Affiliate: credit cards & banks ($50-$200/signup)",
            "Newsletter sponsorships ($500-$5000/issue at scale)",
            "YouTube AdSense (highest RPM niche)",
            "1-on-1 financial coaching ($150-$500/hour)",
        ],
        "conversion_tactics": [
            "Use specific numbers in hooks ('I saved $50K at 25')",
            "Create urgency with limited spots for coaching",
            "Lead magnet: free budget template or investment tracker",
            "Compare: show what money could be doing vs. what it is",
            "Pin your best educational post for first impressions",
        ],
        "audience_demographics": "22-45, 55% male, career-driven, wants financial independence",
        "top_platforms": ["tiktok", "youtube", "instagram", "twitter/x"],
        "competitor_examples": [
            "Finance education page (2M+ TikTok, runs course funnel)",
            "Stock tips page (1M+, earns via affiliate broker deals)",
            "FIRE movement page (500K+, sells financial independence program)",
        ],
        "content_cadence": "1-3x/day TikTok, 1x/day Instagram, 2-3x/week YouTube",
        "avg_growth_rate": "3-7% per week if consistent with trending topics",
    },
    "luxury": {
        "name": "Luxury Lifestyle",
        "conversion_potential": 8.5,
        "estimated_rpm": "$5-12",
        "estimated_cpm": "$10-25",
        "conversion_rate_benchmark": "1.5-3.0%",
        "avg_follower_value": "$0.08-$0.25",
        "best_content_formats": [
            "Luxury property / car tour videos",
            "POV rich lifestyle content",
            "Aspirational travel reels",
            "Unboxing high-end products",
            "Day-in-the-life of wealthy persona",
        ],
        "monetization_strategies": [
            "Luxury brand partnerships ($500-$10K/post at scale)",
            "Affiliate: luxury travel (5-10% commission, high AOV)",
            "Affiliate: watches, jewelry, fashion (5-15%)",
            "'How I achieved this' course ($197-$997)",
            "Travel agency referrals",
            "Dropshipping / print-on-demand luxury aesthetics",
        ],
        "conversion_tactics": [
            "Never show price — let audience fantasize",
            "Aspirational hooks: 'POV: you're a millionaire'",
            "Use high-production value even for short clips",
            "Tell the story behind the luxury (earned it, not inherited)",
            "Mix aspirational with educational to build trust",
        ],
        "audience_demographics": "18-40, mixed gender, aspirational middle-class, dreams of wealth",
        "top_platforms": ["tiktok", "instagram", "youtube"],
        "competitor_examples": [
            "Luxury car & lifestyle page (3M+ TikTok, brand deals)",
            "Real estate luxury tours page (800K+, referral fees)",
            "Aspirational travel page (1.5M+, affiliate travel links)",
        ],
        "content_cadence": "2-4x/day TikTok, 1-2x/day Instagram Stories + 1 feed post",
        "avg_growth_rate": "4-8% per week (aspirational content drives shares)",
    },
    "travel": {
        "name": "Travel",
        "conversion_potential": 8.0,
        "estimated_rpm": "$3-7",
        "estimated_cpm": "$5-15",
        "conversion_rate_benchmark": "2.0-4.0%",
        "avg_follower_value": "$0.04-$0.12",
        "best_content_formats": [
            "Destination reels with trending audio",
            "Budget travel hacks",
            "Travel mistake / warning videos",
            "Hidden gem destination spotlights",
            "Packing & gear content",
        ],
        "monetization_strategies": [
            "Affiliate: booking.com, Airbnb, Expedia (4-7%)",
            "Brand travel partnerships ($300-$3000/post)",
            "Travel preset packs & LUTs ($19-$49)",
            "Travel guide eBooks ($9-$29)",
            "YouTube travel vlogs (AdSense + sponsorships)",
            "Hotel & airline affiliate deals",
        ],
        "conversion_tactics": [
            "Budget angle converts well ('$500 for 2 weeks in Bali')",
            "Use 'Things nobody tells you about [place]' hook",
            "Build trust: share real costs and logistics",
            "Lead magnet: free destination guide PDF",
            "Use location tags aggressively for local discovery",
        ],
        "audience_demographics": "22-40, mixed, adventurous, disposable income, values experiences",
        "top_platforms": ["instagram", "tiktok", "youtube", "pinterest"],
        "competitor_examples": [
            "Budget travel page (1M+, affiliate heavy, digital products)",
            "Solo female travel page (700K+, brand partnerships)",
            "Hidden gems discovery page (2M+, viral short-form content)",
        ],
        "content_cadence": "2-3x/day TikTok/Reels, 1x/day feed, weekly YouTube vlog",
        "avg_growth_rate": "2-4% per week (seasonal spikes around holidays)",
    },
    "food": {
        "name": "Food",
        "conversion_potential": 7.8,
        "estimated_rpm": "$2-6",
        "estimated_cpm": "$4-10",
        "conversion_rate_benchmark": "1.5-3.0%",
        "avg_follower_value": "$0.03-$0.10",
        "best_content_formats": [
            "Quick recipe videos (15-60s)",
            "ASMR cooking content",
            "Restaurant / food review",
            "'What I eat in a day' series",
            "Viral food trend recreation",
        ],
        "monetization_strategies": [
            "Cookbook / recipe eBook ($9-$29)",
            "Cooking course ($49-$197)",
            "Kitchen affiliate products (5-10%)",
            "Food brand sponsorships",
            "YouTube AdSense",
            "Meal plan subscription service ($19-$49/month)",
        ],
        "conversion_tactics": [
            "Satisfaction hooks: show final dish first",
            "Use 'only 3 ingredients' or '10-minute' angles",
            "Weekly series creates appointment viewing",
            "Cross-sell: recipe card → email list → cookbook",
            "Seasonal content spikes (holidays, summer BBQ, etc.)",
        ],
        "audience_demographics": "25-45, 70% female, home cooks, health-conscious",
        "top_platforms": ["instagram", "tiktok", "youtube", "pinterest"],
        "competitor_examples": [
            "Viral recipe page (5M+ TikTok, sells cookbook)",
            "Healthy eating page (1.2M+, affiliate kitchen tools)",
            "Restaurant reviewer page (800K+, local brand deals)",
        ],
        "content_cadence": "1-3x/day TikTok, 1x/day Instagram, 2x/week YouTube",
        "avg_growth_rate": "2-5% per week (food content is evergreen)",
    },
    "gaming": {
        "name": "Gaming",
        "conversion_potential": 7.5,
        "estimated_rpm": "$3-7",
        "estimated_cpm": "$5-12",
        "conversion_rate_benchmark": "2.0-4.5%",
        "avg_follower_value": "$0.04-$0.15",
        "best_content_formats": [
            "Gameplay highlight clips",
            "Top 10 / best moments compilations",
            "Tutorial / tips & tricks",
            "Gaming setup tour",
            "Reaction to viral gaming moments",
        ],
        "monetization_strategies": [
            "Twitch/YouTube subscriptions & donations",
            "Gaming peripheral affiliates (10-15%)",
            "Sponsorships: gaming chairs, headsets, peripherals",
            "Game-key affiliate sites (5-10%)",
            "Discord community ($5-$15/month)",
            "Exclusive coaching: pro gameplay ($50-$200/hour)",
        ],
        "conversion_tactics": [
            "Clip-first format: show the insane moment immediately",
            "Series content keeps viewers coming back",
            "Challenge community: 'can you beat this?'",
            "First impressions content converts curiosity well",
            "Build Discord first, then monetize community",
        ],
        "audience_demographics": "13-30, 75% male, tech-savvy, loyal to creators",
        "top_platforms": ["tiktok", "youtube", "twitch", "instagram"],
        "competitor_examples": [
            "Gaming highlight page (4M+ TikTok, merch and sponsorships)",
            "PC build guide page (1M+ YouTube, affiliate heavy)",
            "Speedrun / world record page (500K+, donation-based monetization)",
        ],
        "content_cadence": "3-5x/day TikTok, daily YouTube Shorts, 3x/week long-form",
        "avg_growth_rate": "3-6% per week (viral clips drive spikes)",
    },
    "crypto": {
        "name": "Crypto",
        "conversion_potential": 9.5,
        "estimated_rpm": "$10-25",
        "estimated_cpm": "$20-50",
        "conversion_rate_benchmark": "3.5-6.0%",
        "avg_follower_value": "$0.15-$0.50",
        "best_content_formats": [
            "Price prediction / market analysis (short)",
            "Beginner explainer content",
            "Breaking news reaction",
            "Portfolio reveal / update",
            "Altcoin spotlight / gem finding",
        ],
        "monetization_strategies": [
            "Exchange affiliates (Binance, Coinbase: up to $1000/referral)",
            "Paid signals / alpha community ($49-$199/month)",
            "Crypto course ($197-$997)",
            "Newsletter / Substack sponsorships",
            "YouTube AdSense (2nd highest RPM after finance)",
            "Token promotions / sponsored mentions (ethical only)",
        ],
        "conversion_tactics": [
            "Create FOMO: 'this altcoin did 10x last cycle'",
            "Educate first: trust before pitch",
            "Free signals channel → paid premium tier",
            "Live market analysis builds real-time community",
            "Fear/greed index content drives engagement during volatility",
        ],
        "audience_demographics": "18-40, 80% male, tech-savvy, high disposable income, risk-tolerant",
        "top_platforms": ["twitter/x", "tiktok", "youtube", "telegram"],
        "competitor_examples": [
            "Crypto education page (2M+ TikTok, exchange affiliate income)",
            "Altcoin gems page (600K+, paid signals community $99/month)",
            "Bitcoin maximalist page (1M+ Twitter/X, Substack revenue)",
        ],
        "content_cadence": "3-5x/day TikTok, 5-10x/day Twitter/X, 1x/week YouTube deep-dive",
        "avg_growth_rate": "5-15% per week during bull markets",
    },
    "fashion": {
        "name": "Fashion",
        "conversion_potential": 8.2,
        "estimated_rpm": "$3-7",
        "estimated_cpm": "$5-12",
        "conversion_rate_benchmark": "2.0-4.0%",
        "avg_follower_value": "$0.05-$0.20",
        "best_content_formats": [
            "Outfit of the day reels",
            "Haul videos",
            "Style tips and tricks",
            "Thrift flip transformations",
            "Aesthetic lookbooks with trending audio",
        ],
        "monetization_strategies": [
            "LTK / Amazon storefront affiliate (5-10%)",
            "Brand collaboration & gifting → paid deals",
            "Dropshipping fashion items",
            "Style guide eBook ($9-$29)",
            "Personal styling coaching ($100-$300/session)",
            "Fashion presets / templates",
        ],
        "conversion_tactics": [
            "Show total outfit cost in thumbnail/caption",
            "Mix luxury with affordable dupes for mass appeal",
            "LTK links in bio for passive income",
            "Seasonal content: summer essentials, winter fits",
            "Trend-first: jump on fashion trends within 24 hours",
        ],
        "audience_demographics": "16-35, 75% female, style-conscious, active shoppers",
        "top_platforms": ["instagram", "tiktok", "pinterest", "youtube"],
        "competitor_examples": [
            "Thrift flip page (3M+ TikTok, brand deals + digital products)",
            "Affordable fashion curator (1.5M+ Instagram, LTK affiliate income)",
            "Aesthetic fashion page (1M+, dropshop + brand deals)",
        ],
        "content_cadence": "2-4x/day TikTok, 1-2x/day Instagram, Pinterest daily",
        "avg_growth_rate": "3-6% per week (visual content has high share rate)",
    },
    "motivational": {
        "name": "Motivational",
        "conversion_potential": 8.8,
        "estimated_rpm": "$4-10",
        "estimated_cpm": "$8-18",
        "conversion_rate_benchmark": "2.5-5.0%",
        "avg_follower_value": "$0.06-$0.20",
        "best_content_formats": [
            "Motivational speech compilations",
            "Daily quote graphics with music",
            "Success story mini-documentaries",
            "Book summary clips",
            "Morning routine / discipline content",
        ],
        "monetization_strategies": [
            "Mindset course ($97-$497)",
            "Coaching / mentorship ($200-$1000/month)",
            "Motivational merch (print-on-demand)",
            "Book affiliate links (Amazon Associates)",
            "Speaking engagements (advanced)",
            "Podcast sponsorships (audio extension)",
        ],
        "conversion_tactics": [
            "Identity-based hooks: 'this is for people who want to win'",
            "Consistency is your brand: post daily",
            "CTA: 'follow for daily motivation'",
            "Series: '30 days of mindset' drives follow-through",
            "Personal story builds parasocial relationship",
        ],
        "audience_demographics": "18-40, mixed, ambitious, entrepreneurs, students",
        "top_platforms": ["tiktok", "instagram", "youtube", "twitter/x"],
        "competitor_examples": [
            "Daily motivation page (8M+ TikTok, course funnel)",
            "Self-improvement page (2M+, coaching program $299/month)",
            "Book summaries page (3M+ YouTube, Amazon affiliate)",
        ],
        "content_cadence": "3-5x/day TikTok, 2x/day Instagram, 1x/day Twitter/X",
        "avg_growth_rate": "4-8% per week (shareable content drives growth)",
    },
    "sports": {
        "name": "Sports",
        "conversion_potential": 7.8,
        "estimated_rpm": "$4-9",
        "estimated_cpm": "$7-15",
        "conversion_rate_benchmark": "2.0-4.0%",
        "avg_follower_value": "$0.05-$0.18",
        "best_content_formats": [
            "Viral highlight clip reactions",
            "Top 10 moments of the week",
            "Athlete news & trade reactions",
            "Sports betting analysis (check local regulations)",
            "Training & fitness content crossover",
        ],
        "monetization_strategies": [
            "Sports apparel affiliate (5-10%)",
            "Fantasy sports platform affiliate ($20-$100/signup)",
            "Brand deals: sports gear brands",
            "YouTube AdSense (sports has solid RPM)",
            "NFT collectibles / digital memorabilia",
            "Fan subscription community ($9-$29/month)",
        ],
        "conversion_tactics": [
            "Real-time content wins: post immediately after viral moments",
            "Hot takes drive engagement and shares",
            "Fantasy sports angle has very high conversion",
            "Local team content builds loyal regional community",
            "Nostalgia content: throwback highlights",
        ],
        "audience_demographics": "16-40, 80% male, sports-passionate, tribal",
        "top_platforms": ["tiktok", "instagram", "youtube", "twitter/x"],
        "competitor_examples": [
            "NBA highlights page (5M+ TikTok, AdSense + brand deals)",
            "Sports reaction page (2M+, AdSense + fantasy affiliates)",
            "Soccer/football clips page (3M+, global audience, sponsorships)",
        ],
        "content_cadence": "3-7x/day TikTok (event-driven), daily Twitter/X, 2-3x/week YouTube",
        "avg_growth_rate": "5-10% per week around major sporting events",
    },
}


def list_niches() -> List[Dict[str, Any]]:
    return [
        {
            "niche": k,
            "name": v["name"],
            "conversion_potential": v["conversion_potential"],
            "estimated_rpm": v["estimated_rpm"],
            "avg_follower_value": v["avg_follower_value"],
            "top_platforms": v["top_platforms"],
        }
        for k, v in sorted(NICHE_DATA.items(), key=lambda x: x[1]["conversion_potential"], reverse=True)
    ]


def get_guide(niche: str) -> Dict[str, Any]:
    key = _match_niche(niche)
    data = NICHE_DATA[key]
    return {
        "niche": key,
        "name": data["name"],
        "guide": {
            "step_1_setup": {
                "title": "Account Setup",
                "actions": [
                    f"Create account with niche-relevant username (include '{key}' or related keyword)",
                    "Upload high-quality profile picture (face or brand logo)",
                    "Write bio with value prop + CTA + link (see template below)",
                    "Set account to Business/Creator mode for analytics",
                    "Create Linktree or Beacons page as your link-in-bio hub",
                ],
            },
            "step_2_content": {
                "title": "Content Strategy",
                "best_formats": data["best_content_formats"],
                "cadence": data["content_cadence"],
                "first_30_days": [
                    "Post 30 pieces of content in 30 days to find your format",
                    "Test at least 3 different content formats",
                    "Study what your top competitors post (don't copy, get inspired)",
                    "Engage with comments for the first hour after each post",
                    "Use trending audio from trending music list",
                ],
            },
            "step_3_growth": {
                "title": "Growth Tactics",
                "actions": [
                    "Post at optimal times: " + data["content_cadence"],
                    "Use hashtag mix: 30% high / 40% medium / 30% low competition",
                    f"Expected growth rate: {data['avg_growth_rate']}",
                    "Collab with 3-5 similar-sized accounts monthly",
                    "Repurpose: TikTok → Instagram Reels → YouTube Shorts",
                    "Reply to every comment in first 2 hours (boosts algorithm)",
                ],
            },
            "step_4_monetization": {
                "title": "Monetization Paths",
                "strategies": data["monetization_strategies"],
                "conversion_rate_benchmark": data["conversion_rate_benchmark"],
                "estimated_rpm": data["estimated_rpm"],
                "timeline": {
                    "month_1_2":  "Build audience, test content, grow to 1K",
                    "month_3_4":  "First monetization: affiliate links, UGC deals",
                    "month_5_6":  "Brand deals, digital product launch",
                    "month_7_12": "Scale: courses, communities, recurring revenue",
                },
            },
            "step_5_theme_page": {
                "title": "Theme Page Conversion",
                "conversion_tactics": data["conversion_tactics"],
                "audience": data["audience_demographics"],
            },
        },
        "competitor_examples": data["competitor_examples"],
    }


def get_strategy(niche: str) -> Dict[str, Any]:
    key = _match_niche(niche)
    data = NICHE_DATA[key]
    return {
        "niche": key,
        "name": data["name"],
        "conversion_potential_score": data["conversion_potential"],
        "content_mix": {
            "educational": "40%",
            "entertaining": "30%",
            "promotional": "10%",
            "trending": "20%",
        },
        "posting_cadence": data["content_cadence"],
        "monetization_paths": data["monetization_strategies"],
        "conversion_tactics": data["conversion_tactics"],
        "link_in_bio_strategy": [
            "Free lead magnet (builds email list)",
            "Top product/affiliate link (primary revenue)",
            "Social proof / testimonials page",
            "Secondary platform (YouTube, Podcast, Newsletter)",
        ],
        "brand_deal_guide": {
            "how_to_pitch": [
                "Build a media kit: follower count, engagement rate, demographics",
                "Cold DM: short, specific, show you know their product",
                "Join creator marketplaces: Creator.co, Aspire, Grin",
                "Reply to brand comments on their posts",
            ],
            "rate_card": {
                "1k-10k":   "$50-$200 per post",
                "10k-50k":  "$200-$800 per post",
                "50k-100k": "$800-$2500 per post",
                "100k-500k":"$2500-$10000 per post",
                "500k+":    "$10000+ per post",
            },
        },
        "digital_products": {
            "easiest_to_create": [
                "PDF guide or checklist ($9-$29)",
                "Templates or presets ($19-$49)",
                "Mini course via Gumroad/Teachable ($47-$197)",
                "eBook ($9-$29)",
            ],
            "highest_margin": "Digital products: 80-95% margin",
            "tools": ["Gumroad", "Stanstore", "Beacons", "Teachable", "Kajabi"],
        },
        "competitor_benchmarks": data["competitor_examples"],
    }


def get_conversion_plan(store: Store, account_id: str, target_niche: str) -> Dict[str, Any]:
    account = store.get_account(account_id)
    current_niche = account.get("niche", "unknown")
    target_key = _match_niche(target_niche)
    target_data = NICHE_DATA[target_key]

    plan = {
        "account_id": account_id,
        "from_niche": current_niche,
        "to_niche": target_key,
        "username": account.get("username"),
        "platform": account.get("platform"),
        "conversion_plan": {
            "week_1": [
                f"Audit existing content — archive posts that don't fit '{target_key}' theme",
                f"Update bio to reflect '{target_key}' niche with clear value proposition",
                f"Create 5 pieces of '{target_key}' content to signal the pivot to algorithm",
                "Update profile picture if needed (niche-relevant)",
                "Research top 10 accounts in target niche",
            ],
            "week_2_3": [
                f"Post {target_data['content_cadence']} of pure '{target_key}' content",
                "Use niche-specific hashtags exclusively",
                f"Engage with target niche community (comment, collab)",
                "Run a poll/Q&A to understand what new audience wants",
                "Update link-in-bio to match new niche offer",
            ],
            "week_4_plus": [
                "Evaluate analytics: is new content outperforming old?",
                "Double down on highest-performing new format",
                f"First monetization attempt for '{target_key}': {target_data['monetization_strategies'][0]}",
                "Start building email list with niche-relevant lead magnet",
            ],
        },
        "risk_factors": [
            "Existing followers may unfollow if pivot is too abrupt",
            "Algorithm may take 2-4 weeks to re-categorize your account",
            "Engagement may temporarily dip during transition",
        ],
        "success_metrics": [
            "New content engagement rate ≥ pre-pivot rate within 4 weeks",
            f"First {target_key} monetization event within 60 days",
            "Net follower growth positive within 30 days",
        ],
        "estimated_time_to_full_pivot": "4-8 weeks",
    }

    store.update_account(account_id, {"target_niche": target_key, "in_conversion": True})
    store.save()
    return plan


def _match_niche(niche: str) -> str:
    key = niche.lower().replace(" ", "_").replace("-", "_")
    if key in NICHE_DATA:
        return key
    for k in NICHE_DATA:
        if k in key or key in k:
            return k
    return "motivational"
