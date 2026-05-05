"""Theme page creation, growth, and monetization conversion guide.

A theme page curates and reposts content around a single topic/aesthetic
(e.g. "luxury cars", "anime", "travel inspo") rather than being a personal
creator brand. This module provides comprehensive strategy data for building
and monetizing theme pages from scratch.
"""

from __future__ import annotations

from typing import Any


# Proven theme page niches ranked by monetization potential
PROFITABLE_NICHES: list[dict] = [
    {"niche": "Luxury Lifestyle",     "difficulty": "Medium", "monetization": "Very High", "avg_cpm": "$15–$40", "tags": ["luxury", "rich", "millionaire", "lamborghini", "yacht"]},
    {"niche": "Fitness Motivation",   "difficulty": "High",   "monetization": "High",      "avg_cpm": "$8–$20",  "tags": ["fitness", "gym", "workout", "gains", "motivation"]},
    {"niche": "Finance & Investing",  "difficulty": "Medium", "monetization": "Very High", "avg_cpm": "$20–$60", "tags": ["investing", "stocks", "crypto", "money", "wealth"]},
    {"niche": "Anime",                "difficulty": "Low",    "monetization": "Medium",    "avg_cpm": "$3–$8",   "tags": ["anime", "manga", "otaku", "naruto", "aot"]},
    {"niche": "Dogs / Pets",          "difficulty": "Low",    "monetization": "Medium",    "avg_cpm": "$5–$12",  "tags": ["dogs", "cats", "pets", "animals", "cute"]},
    {"niche": "Travel & Exploration", "difficulty": "Medium", "monetization": "High",      "avg_cpm": "$10–$25", "tags": ["travel", "wanderlust", "explore", "hidden", "gems"]},
    {"niche": "Cars & Automotive",    "difficulty": "Medium", "monetization": "Very High", "avg_cpm": "$15–$35", "tags": ["cars", "supercar", "automotive", "drift", "jdm"]},
    {"niche": "Dark Humor / Memes",   "difficulty": "Low",    "monetization": "Low",       "avg_cpm": "$1–$4",   "tags": ["memes", "funny", "humor", "relatable", "darkhumor"]},
    {"niche": "Quotes / Mindset",     "difficulty": "Low",    "monetization": "Medium",    "avg_cpm": "$4–$10",  "tags": ["quotes", "mindset", "motivation", "success", "wisdom"]},
    {"niche": "Cooking / Food",       "difficulty": "Medium", "monetization": "High",      "avg_cpm": "$8–$18",  "tags": ["food", "recipes", "cooking", "yummy", "easyrecipes"]},
]

CREATION_STEPS: list[dict] = [
    {
        "step": 1,
        "title": "Choose Your Niche",
        "actions": [
            "Pick ONE niche — hyper-specific beats broad (e.g. 'luxury watches' > 'luxury')",
            "Validate via TikTok/YouTube search: are there 100M+ views on the topic?",
            "Check monetization: finance/automotive/tech niches = high ad rates",
            "Avoid copyright-heavy niches (movie clips, music) unless you have rights",
        ],
    },
    {
        "step": 2,
        "title": "Set Up Your Accounts",
        "actions": [
            "Create consistent username across TikTok, Instagram, YouTube (same handle)",
            "Use Canva to design a clean logo — simple, niche-related icon + name",
            "Write niche-keyword bio: 'Daily [niche] content | Follow for [value]'",
            "Set up link-in-bio (Stan.store, Beacons, or Linktree) from day 1",
            "Switch all accounts to CREATOR or BUSINESS accounts",
        ],
    },
    {
        "step": 3,
        "title": "Content Sourcing Strategy",
        "actions": [
            "Follow 50+ top accounts in your niche — be first to repost viral content",
            "Use yt-dlp to download YouTube videos for repurposing",
            "Sources: Reddit, Pinterest, Imgur, Twitter/X, YouTube — save everything",
            "Remove watermarks: SnapTik (TikTok), SaveFrom (YouTube), Instafinsta (IG)",
            "Always credit original creators in comments (reduces copyright risk)",
            "Create a content bank of 50+ posts before launching",
        ],
    },
    {
        "step": 4,
        "title": "Posting & Growth System",
        "actions": [
            "TikTok: 3–5 posts/day during growth (6am, 12pm, 7pm optimal)",
            "Instagram: 1 Reel + 5–7 Stories/day",
            "YouTube: 2–3 Shorts/day + 1 long-form/week",
            "Use scheduling tools: Later, Buffer, or TikTok's native scheduler",
            "Add 3–5 niche hashtags + 1–2 viral boosters (#fyp, #viral)",
            "Engage: reply to all comments in first 30 minutes after posting",
        ],
    },
    {
        "step": 5,
        "title": "Monetization (the Convert phase)",
        "actions": [
            "1K followers: Add affiliate links (Amazon, ClickBank) to bio",
            "5K followers: Charge $50–$200 for shoutouts / paid promos",
            "10K followers: Apply to brand deals on AspireIQ, CreatorIQ, Grapevine",
            "50K followers: Charge $500–$2,000 per sponsored post",
            "100K+ followers: Launch digital product (ebook, preset, course) — $5K–$20K/launch",
            "Sell the account: theme pages sell for 12–36x monthly revenue on Flippa",
        ],
    },
]

CONVERSION_STRATEGIES: dict[str, dict] = {
    "affiliate": {
        "name": "Affiliate Marketing",
        "how": "Join Amazon Associates, ShareASale, Impact, or ClickBank. Add link to bio. Mention products naturally in captions.",
        "earning_potential": "$100–$5,000/month per account",
        "best_niches": ["fitness", "beauty", "tech", "finance", "food"],
        "tools": ["linktr.ee", "stan.store", "beacons.ai"],
    },
    "shoutouts": {
        "name": "Paid Shoutouts / Promos",
        "how": "DM businesses in your niche offering promo posts. Use platforms like Shoutcart or Famebit.",
        "earning_potential": "$50–$2,000 per post (scales with followers)",
        "best_niches": ["fitness", "beauty", "fashion", "food", "travel"],
        "tools": ["shoutcart.com", "famebit", "grapevine.io"],
    },
    "digital_products": {
        "name": "Digital Products",
        "how": "Create an ebook, Lightroom preset, workout plan, or recipe guide. Sell via Gumroad, Stan.store, or Payhip.",
        "earning_potential": "$500–$20,000/month",
        "best_niches": ["fitness", "finance", "travel", "food", "motivation"],
        "tools": ["gumroad.com", "stan.store", "payhip.com"],
    },
    "account_flipping": {
        "name": "Account Flipping (Sell the Page)",
        "how": "Grow to 50K–500K followers, then sell on Flippa, Social Tradia, or via DMs. Pages sell for 12–36x monthly revenue.",
        "earning_potential": "$500–$50,000 per sale",
        "best_niches": ["luxury", "cars", "fitness", "travel", "memes"],
        "tools": ["flippa.com", "socialtradia.com", "fameswap.com"],
    },
    "email_list": {
        "name": "Email List → High-Ticket Funnel",
        "how": "Offer a free lead magnet (PDF/checklist) to capture emails. Nurture list. Sell high-ticket offers ($97–$997).",
        "earning_potential": "$1,000–$50,000/month at scale",
        "best_niches": ["finance", "fitness", "motivation", "education"],
        "tools": ["convertkit.com", "mailchimp.com", "beehiiv.com"],
    },
    "ugc_creator": {
        "name": "UGC (User Generated Content) Creator",
        "how": "Pitch brands to create raw content FOR them (not posting on your page). No follower minimum needed.",
        "earning_potential": "$150–$500 per video for brands",
        "best_niches": ["beauty", "food", "fitness", "tech", "pets"],
        "tools": ["billo.app", "minisocial.com", "fiverr"],
    },
}

GROWTH_HACKS: list[str] = [
    "Post within 30 min of waking — algorithm rewards early posters",
    "Cross-post TikTok Reels to Instagram with DIFFERENT captions (avoid duplicate detection)",
    "Comment on posts from viral creators in your niche — top comments = free exposure",
    "Do 'collab posts' with similar-sized theme pages — swap audiences",
    "Create 'part 1 of X' series — forces follows to see the next part",
    "Jump on EVERY trending sound within 24h — TikTok gives new sounds extra reach",
    "Post at 3am–6am occasionally — less competition for FYP slots",
    "Use YouTube Shorts to drive traffic to main TikTok/IG pages",
    "Run giveaways at 5K/10K/50K milestones — 'Follow + share to enter'",
    "Make 'account for [city/country]' sub-pages — geo-targeted growth",
    "Batch-create 30 posts in one session, schedule for 2 weeks — never run dry",
    "React videos (split-screen duets) borrow views from already-viral content",
]

COMMON_MISTAKES: list[str] = [
    "Posting inconsistently — the algorithm punishes gaps; batch and schedule",
    "Ignoring comments — engagement in first hour is the #1 ranking signal",
    "Overusing the same hashtags — rotate your hashtag sets",
    "No clear niche — jack-of-all-trades pages grow 10x slower",
    "Deleting low-performing videos — they may catch fire weeks later via 'zombie virality'",
    "Using copyrighted music on YouTube — instant demonetization",
    "Not watermarking your own original content",
    "Buying followers — destroys engagement rate, tanks organic reach permanently",
    "Giving up before 90 days — most accounts see inflection point at 60-90 days",
]


def get_theme_page_guide(niche: str = "general", monetization: str = "affiliate") -> dict[str, Any]:
    """
    Return a complete theme page creation + monetization guide.

    Args:
        niche: content niche to focus on
        monetization: primary monetization strategy (affiliate/shoutouts/digital_products/account_flipping/email_list/ugc_creator)

    Returns comprehensive guide dict.
    """
    niche_lower = niche.lower()
    # Find niche match
    niche_info = next(
        (n for n in PROFITABLE_NICHES if niche_lower in n["niche"].lower()),
        PROFITABLE_NICHES[-2]  # default to quotes/mindset
    )

    mon_key = monetization.lower().replace(" ", "_").replace("-", "_")
    mon_strategy = CONVERSION_STRATEGIES.get(mon_key, CONVERSION_STRATEGIES["affiliate"])

    # Revenue projections
    def _project_revenue(followers: int) -> dict:
        if followers < 1_000:
            return {"monthly": "$0–$50", "method": "Build audience first"}
        if followers < 10_000:
            return {"monthly": "$50–$300", "method": "Affiliate links + shoutouts"}
        if followers < 100_000:
            return {"monthly": "$300–$2,000", "method": "Brand deals + affiliate"}
        if followers < 500_000:
            return {"monthly": "$2,000–$10,000", "method": "Sponsorships + digital products"}
        return {"monthly": "$10,000+", "method": "Full brand partnership + product launches"}

    return {
        "guide_type": "theme_page",
        "niche": niche_info["niche"],
        "niche_difficulty": niche_info["difficulty"],
        "niche_monetization_potential": niche_info["monetization"],
        "recommended_hashtags": [f"#{t}" for t in niche_info["tags"]],
        "creation_roadmap": CREATION_STEPS,
        "primary_monetization_strategy": mon_strategy,
        "all_monetization_paths": list(CONVERSION_STRATEGIES.keys()),
        "revenue_projections": {
            "at_1k_followers":   _project_revenue(1_000),
            "at_10k_followers":  _project_revenue(10_000),
            "at_100k_followers": _project_revenue(100_000),
            "at_500k_followers": _project_revenue(500_000),
        },
        "growth_hacks": GROWTH_HACKS,
        "common_mistakes_to_avoid": COMMON_MISTAKES,
        "profitable_niches_ranked": PROFITABLE_NICHES,
        "tools_stack": {
            "content_download":    ["yt-dlp (YouTube)", "SnapTik (TikTok)", "Instafinsta (Instagram)"],
            "design":              ["Canva (free)", "Adobe Express", "CapCut (video editing)"],
            "scheduling":          ["Later.com", "Buffer", "TikTok native scheduler"],
            "link_in_bio":         ["stan.store", "beacons.ai", "linktree"],
            "monetization":        ["Gumroad", "Stan.store", "Amazon Associates", "ShareASale"],
            "analytics":           ["Social Blade", "TikTok Analytics", "YouTube Studio"],
            "account_sales":       ["Flippa.com", "SocialTradia.com", "FameSwap.com"],
        },
        "90_day_action_plan": [
            "Days 1–7:   Set up all accounts, design branding, build content bank of 50 posts",
            "Days 8–30:  Post 3–5x/day on TikTok, 1 Reel/day IG, 2 Shorts/day YT. Zero monetization — pure growth",
            "Days 31–60: Analyze top performers, double down on formats that work. Add bio link",
            "Days 61–90: First monetization (affiliate / shoutouts). Start email list. Begin cross-platform push",
            "Day 90+:    Review metrics, negotiate brand deals, consider launching digital product",
        ],
    }
