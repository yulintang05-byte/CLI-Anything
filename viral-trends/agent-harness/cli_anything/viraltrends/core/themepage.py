"""Theme page (niche page) creation guide, niche research, and monetization roadmap.

A "theme page" is a social media account built around a specific niche/topic
rather than a personal brand — enabling rapid growth and monetization via
reposting, curation, and community building.
"""

from __future__ import annotations


# ── Niche Database ────────────────────────────────────────────────────────────

NICHES: dict[str, dict] = {
    "motivation": {
        "name": "Motivation / Mindset",
        "difficulty": "low",
        "competition": "very high",
        "cpm_range": "$2-8",
        "monetization": ["AdSense", "Digital products (courses/ebooks)", "Merch", "Affiliate"],
        "content_types": ["Quote graphics", "Speech clips", "Success stories", "Morning routines"],
        "top_hashtags": ["#motivation", "#mindset", "#success", "#dailymotivation", "#grindset"],
        "posting_frequency": "3-5x/day on TikTok, 2x/day on IG",
        "growth_rate": "fast",
        "notes": "Saturated but evergreen. Differentiate with sub-niche (e.g., female entrepreneurs).",
    },
    "finance": {
        "name": "Personal Finance / Investing",
        "difficulty": "medium",
        "competition": "high",
        "cpm_range": "$15-40",
        "monetization": ["Affiliate (brokerage/apps)", "Sponsored posts", "Courses", "Newsletter"],
        "content_types": ["Money tips", "Budget breakdowns", "Stock/crypto news", "Savings challenges"],
        "top_hashtags": ["#personalfinance", "#investing", "#moneytips", "#stockmarket", "#financialfreedom"],
        "posting_frequency": "1-2x/day",
        "growth_rate": "medium",
        "notes": "High CPM. Need disclaimers. Sub-niche: frugal living, side hustles, teen investing.",
    },
    "fitness": {
        "name": "Fitness / Gym",
        "difficulty": "medium",
        "competition": "very high",
        "cpm_range": "$4-12",
        "monetization": ["Fitness programs", "Supplement affiliate", "Merch", "1-on-1 coaching"],
        "content_types": ["Workout clips", "Transformation videos", "Nutrition tips", "Form checks"],
        "top_hashtags": ["#fitness", "#gym", "#workout", "#fitnessmotivation", "#gains"],
        "posting_frequency": "1-2x/day",
        "growth_rate": "medium",
        "notes": "Visual platform. Sub-niche is critical: calisthenics, women's fitness, 30-day challenges.",
    },
    "luxury": {
        "name": "Luxury Lifestyle",
        "difficulty": "high",
        "competition": "medium",
        "cpm_range": "$8-20",
        "monetization": ["Affiliate (luxury brands)", "Sponsored posts", "Dropshipping", "Whop"],
        "content_types": ["Car/watch/jet content", "Mansion tours", "Entrepreneur stories", "Travel"],
        "top_hashtags": ["#luxury", "#luxurylifestyle", "#lifestyle", "#rich", "#millionaire"],
        "posting_frequency": "1x/day",
        "growth_rate": "fast",
        "notes": "Curate aspirational content. Easy to grow via reposting. Need quality visuals.",
    },
    "animals": {
        "name": "Animals / Cute Pets",
        "difficulty": "low",
        "competition": "high",
        "cpm_range": "$1-4",
        "monetization": ["Pet product affiliate", "Merch", "Sponsored posts", "Donations"],
        "content_types": ["Cute animal clips", "Rescue stories", "Pet tips", "Funny compilations"],
        "top_hashtags": ["#animals", "#pets", "#dogs", "#cats", "#cutepets"],
        "posting_frequency": "3-5x/day",
        "growth_rate": "very fast",
        "notes": "Massive virality potential. Low CPM but huge volume. Great starter niche.",
    },
    "cooking": {
        "name": "Food / Recipes",
        "difficulty": "low-medium",
        "competition": "high",
        "cpm_range": "$3-10",
        "monetization": ["Recipe ebooks", "Kitchen affiliate", "Brand deals", "Meal plan subscriptions"],
        "content_types": ["Recipe videos", "Food hacks", "Restaurant reviews", "Cultural cuisine"],
        "top_hashtags": ["#food", "#recipe", "#cooking", "#foodie", "#easyrecipes"],
        "posting_frequency": "1-2x/day",
        "growth_rate": "medium-fast",
        "notes": "Sub-niche heavily: keto, vegan, 5-minute meals, budget cooking.",
    },
    "gaming": {
        "name": "Gaming",
        "difficulty": "medium-high",
        "competition": "very high",
        "cpm_range": "$3-8",
        "monetization": ["YouTube AdSense", "Twitch subs/bits", "Affiliate (peripherals)", "Sponsored"],
        "content_types": ["Gameplay clips", "Tips & tricks", "Reviews", "Gaming news", "Montages"],
        "top_hashtags": ["#gaming", "#gamer", "#gameplay", "#fyp", "#twitch"],
        "posting_frequency": "1-2x/day clips + stream",
        "growth_rate": "slow-medium",
        "notes": "Highly competitive. Clip-focused theme pages easier than personal gaming brands.",
    },
    "fashion": {
        "name": "Fashion / Style",
        "difficulty": "medium",
        "competition": "very high",
        "cpm_range": "$4-15",
        "monetization": ["LTK/affiliate", "Brand deals", "Dropshipping", "Presets/courses"],
        "content_types": ["OOTD", "Hauls", "Style tips", "Trend alerts", "Brand reviews"],
        "top_hashtags": ["#fashion", "#style", "#ootd", "#outfitinspo", "#streetstyle"],
        "posting_frequency": "1-2x/day",
        "growth_rate": "medium-fast",
        "notes": "Highly visual. TikTok + Instagram essential. Sub-niche: men's fashion, thrift, y2k.",
    },
    "crypto": {
        "name": "Crypto / Web3",
        "difficulty": "high",
        "competition": "medium",
        "cpm_range": "$20-60",
        "monetization": ["Exchange affiliate", "NFT drops", "Courses", "Newsletter", "Token"],
        "content_types": ["Price analysis", "Project spotlights", "News", "Educational explainers"],
        "top_hashtags": ["#crypto", "#bitcoin", "#ethereum", "#defi", "#web3"],
        "posting_frequency": "2-3x/day",
        "growth_rate": "volatile",
        "notes": "Highest CPM. Risky in bear markets. Need strong legal disclaimers.",
    },
}


# ── Theme Page SOP ────────────────────────────────────────────────────────────

def niche_research(niche_key: str | None = None) -> dict | list[dict]:
    """Get niche details or list all niches with key metrics."""
    if niche_key:
        key = niche_key.lower().replace(" ", "_")
        info = NICHES.get(key)
        if not info:
            # fuzzy match
            for k, v in NICHES.items():
                if niche_key.lower() in v["name"].lower() or niche_key.lower() in k:
                    info = {**v, "key": k}
                    break
        if info:
            return {**info, "key": key}
        return {"error": f"Niche '{niche_key}' not found", "available": list(NICHES.keys())}
    return [
        {
            "key": k,
            "name": v["name"],
            "difficulty": v["difficulty"],
            "competition": v["competition"],
            "cpm_range": v["cpm_range"],
            "growth_rate": v["growth_rate"],
        }
        for k, v in NICHES.items()
    ]


def theme_page_playbook(niche_key: str, platform: str = "tiktok") -> dict:
    """Full step-by-step theme page creation playbook for a niche + platform."""
    niche = NICHES.get(niche_key.lower(), NICHES.get("motivation"))
    platform = platform.lower()

    phases = {
        "phase_1_setup": {
            "title": "Account Setup (Day 1)",
            "steps": [
                f"Create a new account — username: [niche keyword] + [descriptor] (e.g., 'dailyfinancetips')",
                "Profile photo: High-res niche-relevant image or logo (NOT your face for theme pages)",
                f"Bio: State niche clearly + value prop + CTA (e.g., 'Daily {niche['name']} content | Follow for tips')",
                "Link in bio: Linktree/Stan.store pointing to affiliate or product",
                "Set account to PUBLIC immediately",
                "Do NOT follow/unfollow spam — it flags accounts",
            ],
        },
        "phase_2_content_sourcing": {
            "title": "Content Sourcing (Days 1-7)",
            "steps": [
                f"Find top {niche['name']} creators — study their top 10 videos",
                "Source viral content: Reddit (r/videos, niche subs), Pinterest, Tumblr, other platforms",
                "Download with: yt-dlp (YouTube), saved TikTok videos, Screenshot + Canva for graphics",
                "ALWAYS credit original creators in caption or as on-screen text",
                "Remove original watermarks only if you're adding substantial value (compilation, commentary)",
                "Build a 2-week content buffer before posting",
            ],
            "tools": ["yt-dlp", "Clipper (this repo)", "Canva", "CapCut", "InShot"],
        },
        "phase_3_posting_strategy": {
            "title": "Posting Strategy (Weeks 1-4)",
            "steps": [
                f"Post frequency: {niche['posting_frequency']}",
                f"Best times: See 'viraltrends account schedule {platform}' for optimal times",
                f"Hashtags: {', '.join(niche['top_hashtags'][:5])}",
                "First 3 seconds MUST hook — start with a question, bold claim, or visual shock",
                "Caption: Describe + hashtags + CTA ('Follow for more')",
                "Engage with comments in first 30 min after posting — boosts distribution",
                "Repost your best content after 2-3 weeks (new audience won't have seen it)",
            ],
        },
        "phase_4_growth": {
            "title": "Growth Acceleration (Month 2+)",
            "steps": [
                "Duet/Stitch trending videos in your niche (TikTok) — borrow their momentum",
                "Collab with similar theme pages (shoutout for shoutout, S4S)",
                "Cross-post to Instagram Reels + YouTube Shorts for 3x reach from same content",
                "Trend-jack: react to viral news/events in your niche within 24h",
                "Giveaway at milestones (1K, 10K) to spike follows — require follow + share to enter",
                "Study your analytics weekly — double down on your top-performing content type",
            ],
        },
        "phase_5_monetization": {
            "title": "Monetization (after 1K-10K followers)",
            "steps": [
                f"Primary monetization options for {niche['name']}: {', '.join(niche['monetization'])}",
                f"Expected CPM once monetized: {niche['cpm_range']}",
                "Start affiliate ASAP — no follower minimum, earns from day 1",
                "Sell digital products at 10K+ followers (courses, templates, ebooks)",
                "Brand deals at 10K+ (micro-influencer rates: $50-500/post)",
                "Sell the account at 50K-100K if you want to cash out ($500-5K+ depending on niche)",
            ],
        },
    }

    return {
        "niche": niche["name"],
        "platform": platform,
        "difficulty": niche["difficulty"],
        "expected_growth_rate": niche["growth_rate"],
        "top_hashtags": niche["top_hashtags"],
        "content_types": niche["content_types"],
        "monetization_paths": niche["monetization"],
        "notes": niche["notes"],
        "playbook": phases,
    }


def converting_guide() -> dict:
    """Guide on converting theme page followers into revenue (the 'converting' in the ask)."""
    return {
        "title": "Converting Theme Page Followers to Revenue",
        "overview": (
            "A theme page 'converts' when followers take a desired action: click a link, "
            "buy a product, sign up for a newsletter, or DM you. "
            "Conversion requires trust, consistency, and a clear offer."
        ),
        "conversion_funnels": [
            {
                "name": "Affiliate Funnel",
                "steps": [
                    "Post value content (TikTok/IG/YT)",
                    "CTA in bio: 'Link in bio for [tool/product]'",
                    "Linktree → Affiliate link (Amazon, Impact, ClickBank, etc.)",
                    "Earn 5-50% commission per sale",
                ],
                "best_for": "Beginner theme pages (0 followers needed)",
                "avg_conversion_rate": "1-3% of link clicks → purchase",
            },
            {
                "name": "Lead Magnet Funnel",
                "steps": [
                    "Offer free value (PDF, checklist, mini-course)",
                    "Collect email via Beehiiv/ConvertKit/Stan.store",
                    "Nurture via weekly email newsletter",
                    "Sell digital product or paid community at backend",
                ],
                "best_for": "Finance, fitness, education niches",
                "avg_conversion_rate": "10-30% of landing page visitors → email opt-in",
            },
            {
                "name": "DM Funnel",
                "steps": [
                    "Post content with CTA 'Comment [keyword] and I'll DM you'",
                    "Auto-DM via ManyChat (IG/TikTok automation)",
                    "Send value + soft pitch in DM sequence",
                    "Convert to sale or booked call",
                ],
                "best_for": "Coaching, services, high-ticket offers",
                "avg_conversion_rate": "5-15% of DM conversations → sale",
            },
            {
                "name": "Community Funnel",
                "steps": [
                    "Build free community (Discord/Telegram/Whop)",
                    "Grow community via organic content CTAs",
                    "Monetize via paid tier, courses, or sponsorships",
                ],
                "best_for": "Gaming, crypto, finance, fitness niches",
                "avg_conversion_rate": "2-8% of followers → community join",
            },
        ],
        "conversion_optimization_tips": [
            "Strong bio CTA: 'Get free [X] → link in bio' outperforms generic 'link in bio'",
            "Post 'link in bio' verbally in video — not just in caption (many don't read captions)",
            "Pin your best-converting video at the top of your profile",
            "Use Stan.store or Linktree with a clean, fast-loading landing page",
            "A/B test different CTAs weekly — track clicks in Linktree analytics",
            "Consistency = trust. 90 days of daily posting before judging conversion results",
            "Engage comments to build community — commenters are 3x more likely to convert",
        ],
        "tools": {
            "link_in_bio": ["Linktree", "Stan.store", "Beacons.ai", "bio.link"],
            "email_marketing": ["Beehiiv", "ConvertKit", "MailerLite"],
            "dm_automation": ["ManyChat", "Manychat for TikTok (beta)"],
            "payments": ["Gumroad", "Whop", "Stripe", "Patreon"],
            "analytics": ["TikTok Analytics", "YouTube Studio", "Later", "Metricool"],
        },
    }


def account_selling_guide() -> dict:
    """Guide on selling theme page accounts for profit."""
    return {
        "title": "Selling Theme Pages for Profit",
        "overview": "A theme page is a digital asset. Accounts with engaged audiences sell for 12-36x monthly revenue.",
        "valuation": {
            "formula": "Monthly revenue × 12-36 (depending on niche, growth, engagement)",
            "examples": [
                {"followers": "10K", "niche": "motivation", "est_value": "$50-200"},
                {"followers": "50K", "niche": "finance", "est_value": "$500-2,000"},
                {"followers": "100K", "niche": "crypto", "est_value": "$2,000-10,000"},
                {"followers": "500K", "niche": "fitness", "est_value": "$5,000-25,000"},
            ],
        },
        "marketplaces": [
            "Flippa.com — largest digital asset marketplace",
            "FameSwap.com — specialized in social accounts",
            "Social Tradia — Instagram/TikTok focused",
            "EmpireFlippers — for revenue-generating accounts",
            "Direct DM to buyers in your niche",
        ],
        "what_buyers_want": [
            "Consistent posting history (no gaps > 2 weeks)",
            "Real engagement (not bot inflated)",
            "Monetization already set up (even if small)",
            "Niche clarity — one focused topic only",
            "Growth trajectory — upward trend, not declining",
        ],
    }
