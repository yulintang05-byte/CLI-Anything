"""Theme page strategy guide — building, growing, and converting theme pages.

A theme page is a niche social account that curates content around a topic
(luxury cars, motivation quotes, travel aesthetics, fitness, etc.) rather than
personal branding. They can be built, monetized, and sold at scale.

This module provides:
- Niche selection and research
- Growth playbooks per platform
- Monetization strategy breakdowns
- Page conversion (traffic → $) tactics
- Page flipping (buy/grow/sell) framework
"""
from __future__ import annotations

from datetime import datetime
from typing import Any


NICHES: dict[str, dict] = {
    "motivation": {
        "saturation": "HIGH",
        "monetization_potential": "MEDIUM",
        "avg_cpm_usd": 3.5,
        "best_platforms": ["instagram", "tiktok", "twitter"],
        "content_difficulty": "LOW",
        "growth_speed": "FAST",
        "description": "Inspirational quotes, success stories, mindset content",
        "monetization_methods": ["shoutouts", "digital_products", "affiliate", "coaching"],
    },
    "luxury": {
        "saturation": "MEDIUM",
        "monetization_potential": "VERY_HIGH",
        "avg_cpm_usd": 12.0,
        "best_platforms": ["instagram", "tiktok", "youtube"],
        "content_difficulty": "MEDIUM",
        "growth_speed": "MEDIUM",
        "description": "Supercars, yachts, mansions, private jets, designer goods",
        "monetization_methods": ["shoutouts", "affiliate", "brand_deals", "page_flipping"],
    },
    "fitness": {
        "saturation": "HIGH",
        "monetization_potential": "HIGH",
        "avg_cpm_usd": 7.0,
        "best_platforms": ["instagram", "tiktok", "youtube"],
        "content_difficulty": "MEDIUM",
        "growth_speed": "MEDIUM",
        "description": "Workouts, transformations, nutrition, supplements",
        "monetization_methods": ["affiliate", "digital_products", "coaching", "brand_deals"],
    },
    "finance": {
        "saturation": "MEDIUM",
        "monetization_potential": "VERY_HIGH",
        "avg_cpm_usd": 18.0,
        "best_platforms": ["twitter", "instagram", "tiktok", "youtube"],
        "content_difficulty": "MEDIUM",
        "growth_speed": "MEDIUM",
        "description": "Investing, stocks, crypto, passive income, frugality",
        "monetization_methods": ["affiliate", "digital_products", "sponsorships", "newsletter"],
    },
    "cars": {
        "saturation": "LOW",
        "monetization_potential": "HIGH",
        "avg_cpm_usd": 9.0,
        "best_platforms": ["instagram", "tiktok", "youtube"],
        "content_difficulty": "LOW",
        "growth_speed": "FAST",
        "description": "Supercars, modified cars, car reviews, automotive news",
        "monetization_methods": ["affiliate", "shoutouts", "brand_deals", "page_flipping"],
    },
    "travel": {
        "saturation": "HIGH",
        "monetization_potential": "HIGH",
        "avg_cpm_usd": 6.5,
        "best_platforms": ["instagram", "tiktok", "youtube", "pinterest"],
        "content_difficulty": "MEDIUM",
        "growth_speed": "SLOW",
        "description": "Destinations, travel hacks, hidden gems, bucket list spots",
        "monetization_methods": ["affiliate", "brand_deals", "digital_products", "sponsorships"],
    },
    "food": {
        "saturation": "HIGH",
        "monetization_potential": "MEDIUM",
        "avg_cpm_usd": 4.5,
        "best_platforms": ["instagram", "tiktok", "youtube", "pinterest"],
        "content_difficulty": "MEDIUM",
        "growth_speed": "FAST",
        "description": "Recipes, restaurant reviews, food art, cooking hacks",
        "monetization_methods": ["affiliate", "brand_deals", "digital_products"],
    },
    "gaming": {
        "saturation": "VERY_HIGH",
        "monetization_potential": "HIGH",
        "avg_cpm_usd": 5.0,
        "best_platforms": ["tiktok", "youtube", "twitter", "twitch"],
        "content_difficulty": "HIGH",
        "growth_speed": "SLOW",
        "description": "Gameplay clips, gaming news, tips, esports",
        "monetization_methods": ["sponsorships", "affiliate", "merch", "streaming"],
    },
    "aesthetics": {
        "saturation": "LOW",
        "monetization_potential": "MEDIUM",
        "avg_cpm_usd": 5.5,
        "best_platforms": ["instagram", "pinterest", "tiktok"],
        "content_difficulty": "LOW",
        "growth_speed": "FAST",
        "description": "Dark academia, cottagecore, Y2K, lofi, urban aesthetics",
        "monetization_methods": ["affiliate", "shoutouts", "page_flipping", "digital_products"],
    },
    "pets": {
        "saturation": "HIGH",
        "monetization_potential": "MEDIUM",
        "avg_cpm_usd": 5.0,
        "best_platforms": ["instagram", "tiktok", "youtube"],
        "content_difficulty": "LOW",
        "growth_speed": "FAST",
        "description": "Cute animals, pet care, funny pets, exotic animals",
        "monetization_methods": ["affiliate", "brand_deals", "shoutouts"],
    },
    "crypto": {
        "saturation": "MEDIUM",
        "monetization_potential": "VERY_HIGH",
        "avg_cpm_usd": 20.0,
        "best_platforms": ["twitter", "tiktok", "youtube"],
        "content_difficulty": "HIGH",
        "growth_speed": "FAST_DURING_BULL",
        "description": "Bitcoin, altcoins, DeFi, NFTs, blockchain news",
        "monetization_methods": ["affiliate", "sponsorships", "paid_groups", "newsletter"],
    },
}

MONETIZATION_METHODS: dict[str, dict] = {
    "shoutouts": {
        "description": "Charge other accounts to post their content/mention them",
        "difficulty": "EASY",
        "timing": "500+ followers",
        "income_range_usd": {"min": 5, "max": 500, "note": "per post, scales with followers"},
        "how_to": [
            "Add 'DM for promo' in bio once you hit 500+ followers",
            "Price based on engagement: 1-3% engagement = $0.01-$0.03 per follower",
            "Use Shoutcart, Fameswap, or DM outreach to find clients",
            "Offer packages: 1 post, 3 posts, story + post bundle",
            "Only accept accounts in same niche — protects your engagement",
        ],
        "pitfalls": [
            "Too many shoutouts kills organic reach — max 1-2/day",
            "Never shoutout scams or low-quality accounts — damages trust",
            "Screenshot all deals — disputes happen",
        ],
    },
    "affiliate": {
        "description": "Earn commission by promoting products/services with tracked links",
        "difficulty": "MEDIUM",
        "timing": "1,000+ followers or any size with right content",
        "income_range_usd": {"min": 50, "max": 10_000, "note": "monthly, scales with traffic"},
        "how_to": [
            "Join affiliate networks: Amazon Associates, ShareASale, Impact, ClickBank, Digistore24",
            "Choose products that match your niche exactly",
            "Add affiliate link in bio via Linktree, Stan.store, or Beacons.ai",
            "Create 'value first' content then soft-sell the product",
            "Track clicks and conversion — kill low performers fast",
        ],
        "pitfalls": [
            "Disclose affiliate links (#ad) — required by FTC in US",
            "Don't promote products you haven't researched — ruins trust",
            "Amazon cookies last 24h only — use a landing page to warm up traffic",
        ],
        "top_programs": {
            "fitness": ["BodyBuilding.com (5-10%)", "MyProtein (8-10%)", "Gymshark affiliate"],
            "finance": ["Robinhood ($20/signup)", "Coinbase ($10/signup)", "NerdWallet CPA"],
            "travel": ["Booking.com (4-6%)", "Airbnb ($75/first booking)", "TripAdvisor"],
            "tech": ["Amazon (1-4%)", "Best Buy", "Wirecutter equivalent programs"],
            "software": ["ConvertKit (30% recurring)", "Canva Pro (up to $36/signup)"],
        },
    },
    "digital_products": {
        "description": "Sell downloadable products: eBooks, presets, templates, courses",
        "difficulty": "MEDIUM",
        "timing": "2,000+ engaged followers",
        "income_range_usd": {"min": 200, "max": 50_000, "note": "monthly, highly scalable"},
        "how_to": [
            "Identify #1 pain point your audience has (use polls/DMs to confirm)",
            "Create solution as PDF guide, Notion template, video course, or preset pack",
            "Host on Gumroad, Stan.store, Payhip, or Lemon Squeezy (low fees)",
            "Price anchoring: offer low-ticket ($7-$27) first, upsell higher ($97-$297)",
            "Use 'soft launch' to your warmest followers first — validate before scaling",
            "Re-purpose every piece of organic content into a proof-of-expertise",
        ],
        "pitfalls": [
            "Don't build a product before validating demand",
            "Refund policy required — have one ready",
            "Customer support takes time — build FAQ into the product",
        ],
    },
    "brand_deals": {
        "description": "Paid partnerships with brands for sponsored content",
        "difficulty": "MEDIUM",
        "timing": "10,000+ followers (micro-influencer threshold)",
        "income_range_usd": {"min": 100, "max": 100_000, "note": "per post, depends on niche and reach"},
        "how_to": [
            "Build a media kit: follower count, engagement rate, audience demographics, niche",
            "Pitch cold: find brands via Instagram search and DM their marketing email",
            "List on influencer platforms: AspireIQ, Grin, Creator.co, Influencity",
            "Always negotiate: starting offer is rarely final",
            "Rate formula: (followers × engagement_rate × 0.01) + platform multiplier",
        ],
        "pitfalls": [
            "Disclose sponsored content legally required (#ad, #sponsored)",
            "Vet brands before promoting — audience trust is your #1 asset",
            "Get contracts in writing — verbal deals don't hold up",
        ],
    },
    "page_flipping": {
        "description": "Build a theme page from 0, grow it to 10k-100k, sell it for profit",
        "difficulty": "MEDIUM",
        "timing": "Any size — sell at 10k+ for best ROI",
        "income_range_usd": {"min": 500, "max": 50_000, "note": "per sale, depends on size and niche"},
        "how_to": [
            "Choose low-saturation, high-CPM niche (luxury, finance, crypto)",
            "Post 3-5x/day using viral content repurposed from Reddit, Twitter, or YouTube",
            "Add original touches: unique font, color scheme, caption style",
            "Grow to 10k-50k organically using trending hashtags and content hooks",
            "List for sale on Fameswap, Swapd, or EpicNPC",
            "Typical valuation: 10-30× monthly revenue OR $50-200 per 1000 followers",
        ],
        "pitfalls": [
            "Verify buyer legitimacy — use escrow services for large deals",
            "Keep growth organic — bought followers are detectable and kill sale price",
            "Niche consistency — scattered content tanks engagement and value",
        ],
        "platforms_for_selling": ["Fameswap.com", "Swapd.co", "EpicNPC.com", "Player.me"],
    },
    "paid_community": {
        "description": "Monetize audience via paid Discord, Telegram, or Skool community",
        "difficulty": "HIGH",
        "timing": "5,000+ highly engaged followers",
        "income_range_usd": {"min": 500, "max": 20_000, "note": "monthly recurring"},
        "how_to": [
            "Create free community first — build trust and demonstrate value",
            "Identify premium value-adds: live Q&As, exclusive content, signal groups",
            "Charge $5-$50/month on Patreon, Discord, or Skool",
            "Tease community benefits in organic content",
            "Keep churn low with consistent schedule and active moderation",
        ],
    },
    "newsletter": {
        "description": "Build email list from social → monetize via ads, products, or sponsors",
        "difficulty": "HIGH",
        "timing": "1,000+ followers (start list-building day 1)",
        "income_range_usd": {"min": 100, "max": 50_000, "note": "monthly, highly scalable"},
        "how_to": [
            "Offer a lead magnet (free PDF, checklist, template) for email sign-ups",
            "Use Beehiiv, ConvertKit, or Substack (free tiers available)",
            "Drive traffic via bio link and 'link in bio' CTAs in every post",
            "Send weekly valuable content — aim for 40%+ open rate",
            "Monetize at 1,000 subscribers: sponsorships ($50-$500/issue), affiliate, products",
        ],
    },
}

GROWTH_PLAYBOOKS: dict[str, list[str]] = {
    "tiktok": [
        "Post 3-5× per day during launch phase (first 90 days) — volume wins",
        "Use trending sounds — TikTok algorithmically boosts content using viral audio",
        "Identify 3-5 viral videos in your niche and recreate with your spin (trend jack)",
        "Hook in first 1-2 seconds: text on screen, pattern interrupt, surprising visual",
        "Reply to comments with video responses — doubles comment engagement",
        "Duet or stitch viral content in your niche for instant audience borrowing",
        "Post at 6-9am, 12-3pm, 7-10pm in your audience's timezone",
        "Use 3-5 niche hashtags + 1-2 broad — avoid #fyp spam (algorithm ignores it)",
        "Cross-post to Instagram Reels for 2× reach from same content",
        "Study your analytics after 30 posts — double down on what works",
    ],
    "instagram": [
        "Reels are king — prioritize video content over static for 3-5× organic reach",
        "Post Reels daily + 3 Stories/day for full algorithm coverage",
        "Use carousel posts for educational content — saves = algorithmic boost",
        "Collabs with same-niche accounts double your audience exposure",
        "Reply to every comment in first 60 minutes — critical engagement signal",
        "Use location tags and niche-specific hashtags (avoid generic like #love)",
        "Pin your 3 best posts (highest reach) to profile top",
        "Add CTA to every caption: question, save, share, or tag",
        "Story polls, quizzes, and 'this or that' increase watch-through rate",
        "Consistency > quality at early stage — 1 good post/day beats sporadic great posts",
    ],
    "youtube": [
        "Shorts feed the algorithm for your long-form — post both",
        "First 30 seconds retention is everything — hook immediately",
        "A/B test thumbnails (same video, 2 different thumbnails via YouTube Studio)",
        "Title formula: [Number] + [Benefit/Curiosity] + [Timeframe] = click bait (good way)",
        "Chapters + pinned comment with timestamps reduces bounce rate",
        "Post on Thursday/Friday for weekend view spike",
        "Build a content series — viewers binge and subscribe",
        "End screen subscriber CTA in last 20 seconds of every video",
        "Engage with comments first 24 hours — YouTube rewards active creators",
        "Cross-promote in community posts (available at 500+ subscribers)",
    ],
    "twitter": [
        "Tweet threads outperform single tweets 10× for impressions and follows",
        "Post 3-5 tweets/day at business hours (8am-6pm local time)",
        "Reply to trending topics and viral tweets in your niche early for borrowed reach",
        "Quotetweeting viral posts with your take is the fastest growth hack on Twitter",
        "Pinned tweet = most valuable real estate — make it your best work",
        "List building via lead magnet in pinned tweet or bio",
        "Use Spaces for live audio — Twitter promotes it heavily",
        "Niche down ruthlessly — generalist accounts grow slower on Twitter",
    ],
}


def get_niche_analysis(niche: str) -> dict[str, Any]:
    """Return detailed analysis for a specific niche."""
    data = NICHES.get(niche.lower())
    if not data:
        return {
            "error": f"Niche '{niche}' not found",
            "available_niches": list(NICHES.keys()),
        }
    methods = {m: MONETIZATION_METHODS[m] for m in data["monetization_methods"] if m in MONETIZATION_METHODS}
    return {
        "niche": niche,
        "analysis": data,
        "monetization_breakdown": methods,
        "recommendation": _niche_recommendation(niche, data),
    }


def compare_niches(niches: list[str] | None = None) -> dict[str, Any]:
    """Compare multiple niches side-by-side for strategic decision-making."""
    targets = niches or list(NICHES.keys())
    comparison = []
    for niche in targets:
        data = NICHES.get(niche.lower())
        if not data:
            continue
        score = _niche_score(data)
        comparison.append({
            "niche": niche,
            "score": score,
            "saturation": data["saturation"],
            "monetization_potential": data["monetization_potential"],
            "avg_cpm_usd": data["avg_cpm_usd"],
            "growth_speed": data["growth_speed"],
            "best_platforms": data["best_platforms"],
        })
    comparison.sort(key=lambda x: x["score"], reverse=True)
    return {
        "comparison": comparison,
        "top_recommendation": comparison[0]["niche"] if comparison else None,
        "best_for_beginners": _best_for_beginners(comparison),
        "best_for_monetization": _best_for_monetization(comparison),
    }


def get_monetization_strategy(method: str) -> dict[str, Any]:
    """Get detailed guide for a specific monetization method."""
    data = MONETIZATION_METHODS.get(method.lower())
    if not data:
        return {
            "error": f"Method '{method}' not found",
            "available_methods": list(MONETIZATION_METHODS.keys()),
        }
    return {"method": method, **data}


def get_growth_playbook(platform: str) -> dict[str, Any]:
    """Get platform-specific growth playbook."""
    playbook = GROWTH_PLAYBOOKS.get(platform.lower())
    if not playbook:
        return {
            "error": f"Platform '{platform}' not found",
            "available_platforms": list(GROWTH_PLAYBOOKS.keys()),
        }
    return {
        "platform": platform,
        "steps": playbook,
        "estimated_timeline": _growth_timeline(platform),
        "common_mistakes": _common_mistakes(platform),
    }


def page_flip_roadmap(
    niche: str = "luxury",
    platform: str = "instagram",
    target_followers: int = 50_000,
    starting_budget_usd: int = 0,
) -> dict[str, Any]:
    """Generate a page-flipping roadmap: build → grow → sell."""
    niche_data = NICHES.get(niche, NICHES["luxury"])
    est_value = _estimate_flip_value(niche, target_followers)
    timeline = _flip_timeline(target_followers, niche_data["growth_speed"])

    return {
        "niche": niche,
        "platform": platform,
        "target_followers": target_followers,
        "starting_budget_usd": starting_budget_usd,
        "estimated_sell_value_usd": est_value,
        "estimated_timeline_months": timeline,
        "roi_estimate": f"{int((est_value / max(starting_budget_usd, 1)) * 100)}×" if starting_budget_usd else "N/A (organic)",
        "phases": _flip_phases(niche, platform, target_followers, niche_data),
        "selling_platforms": MONETIZATION_METHODS["page_flipping"]["platforms_for_selling"],
        "valuation_guide": {
            "formula": "10-30× monthly revenue OR $50-$200 per 1,000 followers",
            "premium_multipliers": {
                "high_engagement": "1.5-2×",
                "monetized_account": "2-3×",
                "email_list": "+$5-10 per subscriber",
                "proven_revenue": "Direct multiplier on LTM earnings",
            },
        },
    }


def _flip_phases(niche: str, platform: str, target: int, niche_data: dict) -> list[dict]:
    return [
        {
            "phase": 1,
            "name": "Setup & Brand Identity",
            "duration": "Week 1-2",
            "actions": [
                f"Create account with keyword-rich username (e.g. @{niche.lower()}.daily)",
                "Design consistent visual identity: color palette, font, logo",
                "Write optimized bio with keyword + CTA + link",
                "Set up Linktree or Stan.store for future monetization",
                "Research top 10 accounts in niche — model their best content",
            ],
            "goal": "Professional account ready to post",
        },
        {
            "phase": 2,
            "name": "Content Flood (0-1K followers)",
            "duration": "Weeks 2-6",
            "actions": [
                "Post 3-5× daily using viral content repurposed from Reddit/Twitter/YouTube",
                "Use trending sounds (TikTok) or trending hashtags (Instagram)",
                "Engage aggressively: comment on top posts in niche daily",
                "Follow 20-50 accounts/day in niche (use their follower lists)",
                "Track which content types get most reach/saves",
            ],
            "goal": "1,000 followers + identify your best content format",
        },
        {
            "phase": 3,
            "name": "Growth Acceleration (1K-10K)",
            "duration": "Months 2-4",
            "actions": [
                "Double down on your top-performing content format",
                "Collab/duet with 5K-50K accounts in same niche",
                "Start building email list (lead magnet in bio)",
                "First soft monetization: shoutouts at 2K+ followers",
                "Post consistently at optimal times (use analytics)",
            ],
            "goal": "10,000 followers + first $100/month revenue",
        },
        {
            "phase": 4,
            "name": "Monetization Layer (10K-50K)",
            "duration": "Months 4-8",
            "actions": [
                "Activate all monetization streams: shoutouts, affiliate, digital product",
                "Reach out to brands for sponsorship deals",
                "Build media kit and list on influencer platforms",
                "Start documenting monthly revenue (critical for page valuation)",
                "Consider creating YouTube/newsletter extension for multi-platform presence",
            ],
            "goal": f"{target:,} followers + $500-$2,000/month revenue",
        },
        {
            "phase": 5,
            "name": "Exit / Flip",
            "duration": "Month 8+",
            "actions": [
                "Compile performance data: followers, engagement, monthly revenue, growth rate",
                "Create listing on Fameswap or Swapd with proof of stats",
                "Set asking price using 15-30× monthly revenue or follower-based valuation",
                "Use escrow for security (Escrow.com or platform-native)",
                "Reinvest proceeds into next page — repeat the cycle",
            ],
            "goal": f"Sell page for ${_estimate_flip_value(niche, target):,}+",
        },
    ]


def _niche_score(data: dict) -> float:
    sat_score = {"LOW": 3, "MEDIUM": 2, "HIGH": 1, "VERY_HIGH": 0}.get(data["saturation"], 1)
    mon_score = {"VERY_HIGH": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(data["monetization_potential"], 2)
    speed_score = {"FAST": 3, "FAST_DURING_BULL": 2.5, "MEDIUM": 2, "SLOW": 1}.get(data["growth_speed"], 2)
    return (sat_score * 2 + mon_score * 3 + speed_score + data["avg_cpm_usd"] * 0.2)


def _best_for_beginners(comparison: list[dict]) -> str:
    low_sat = [n for n in comparison if n["saturation"] in ("LOW", "MEDIUM")]
    fast_growth = [n for n in low_sat if n["growth_speed"] in ("FAST", "MEDIUM")]
    if fast_growth:
        return fast_growth[0]["niche"]
    return comparison[0]["niche"] if comparison else "cars"


def _best_for_monetization(comparison: list[dict]) -> str:
    high_mon = [n for n in comparison if n["monetization_potential"] == "VERY_HIGH"]
    if high_mon:
        high_mon.sort(key=lambda x: x["avg_cpm_usd"], reverse=True)
        return high_mon[0]["niche"]
    return "finance"


def _niche_recommendation(niche: str, data: dict) -> str:
    lines = []
    if data["saturation"] == "LOW":
        lines.append(f"{niche.title()} has LOW competition — great time to enter.")
    elif data["saturation"] == "VERY_HIGH":
        lines.append(f"{niche.title()} is highly saturated — niche down further (e.g. 'vintage cars' not 'cars').")
    else:
        lines.append(f"{niche.title()} has moderate competition — differentiation is key.")

    if data["monetization_potential"] == "VERY_HIGH":
        lines.append(f"Monetization potential is excellent (CPM ${data['avg_cpm_usd']}/1000 impressions).")

    lines.append(f"Best platforms: {', '.join(data['best_platforms'])}.")
    lines.append(f"Recommended monetization: {', '.join(data['monetization_methods'][:3])}.")
    return " ".join(lines)


def _estimate_flip_value(niche: str, followers: int) -> int:
    base = (followers / 1000) * 100
    premiums = {"finance": 2.5, "crypto": 3.0, "luxury": 2.0, "fitness": 1.5, "motivation": 1.0, "cars": 1.8}
    return int(base * premiums.get(niche, 1.2))


def _flip_timeline(target: int, growth_speed: str) -> int:
    base_months = target // 5000
    speed_mult = {"FAST": 0.5, "FAST_DURING_BULL": 0.7, "MEDIUM": 1.0, "SLOW": 1.5}
    return max(1, int(base_months * speed_mult.get(growth_speed, 1.0)))


def _growth_timeline(platform: str) -> str:
    timelines = {
        "tiktok": "0-10K: 1-3 months | 10K-100K: 3-8 months (if going viral)",
        "instagram": "0-10K: 3-6 months | 10K-100K: 6-18 months",
        "youtube": "0-1K: 3-6 months | 1K-100K: 1-2+ years",
        "twitter": "0-10K: 2-6 months | 10K-100K: 6-24 months",
    }
    return timelines.get(platform, "Varies based on posting frequency and content quality")


def _common_mistakes(platform: str) -> list[str]:
    mistakes = {
        "tiktok": [
            "Using too many hashtags (5 max — quality over quantity)",
            "Not hooking viewers in first 1-2 seconds",
            "Deleting videos — even low views contribute to algorithm profile",
            "Not posting consistently — TikTok rewards daily creators",
            "Posting landscape video — always use 9:16 vertical format",
        ],
        "instagram": [
            "Ignoring Reels for static posts — Reels have 3-5× organic reach",
            "Using irrelevant hashtags just because they're big",
            "Buying followers — Instagram detects and penalizes fake engagement",
            "Ghosting your audience — no replies to DMs or comments",
            "No CTA in caption — always tell people what to do next",
        ],
        "youtube": [
            "Keyword-stuffing titles instead of making them click-worthy",
            "Bad thumbnails — this is your #1 lever for views",
            "No chapters/timestamps — reduces watch time",
            "Inconsistent upload schedule",
            "Not linking to related videos in end screen",
        ],
        "twitter": [
            "Tweeting random thoughts instead of building authority in a niche",
            "No thread strategy — single tweets have low ceiling",
            "Not engaging with bigger accounts for borrowed reach",
            "Posting too infrequently — Twitter's shelf life per tweet is 18 minutes",
        ],
    }
    return mistakes.get(platform, ["Inconsistent posting", "No defined niche", "No clear CTA"])


def list_all_strategies() -> dict[str, Any]:
    """Return a summary of all available monetization methods and niches."""
    return {
        "available_niches": {k: {"cpm": v["avg_cpm_usd"], "potential": v["monetization_potential"], "saturation": v["saturation"]} for k, v in NICHES.items()},
        "monetization_methods": {k: {"difficulty": v["difficulty"], "timing": v["timing"]} for k, v in MONETIZATION_METHODS.items()},
        "growth_playbooks_available": list(GROWTH_PLAYBOOKS.keys()),
        "quick_start_recommendation": "Start with 'cars' or 'luxury' niche on TikTok/Instagram — low saturation, fast growth, high CPM. Use page_flip_roadmap() for full 5-phase plan.",
    }
