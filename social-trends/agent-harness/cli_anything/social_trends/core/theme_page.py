"""Theme Page Strategy — complete guide to building converting theme pages.

A 'converting theme page' is a niche content account that:
1. Reposts/curates viral content around a specific theme
2. Grows a large, targeted following quickly (no original content needed)
3. Monetizes through affiliate links, shoutouts, digital products, or brand deals

This module provides:
- Niche selection scoring
- Step-by-step launch playbook
- Monetization blueprints by follower milestone
- Content sourcing strategy
- CTA and conversion optimization
"""

from typing import Optional


# Top converting niches ranked by monetization potential + growth speed
THEME_PAGE_NICHES = [
    {
        "niche": "Personal Finance / Wealth",
        "monetization": 10,
        "growth_speed": 8,
        "competition": 7,
        "cpm": "HIGH",
        "affiliate_examples": ["Credit cards (Chase, Amex)", "Robinhood", "Coinbase", "Acorns",
                               "Tax software (TurboTax)", "Courses (Udemy finance)"],
        "why_converts": "Audience is actively seeking solutions — high buyer intent",
        "content_sources": ["r/personalfinance", "Yahoo Finance clips", "FinanceTok creators",
                            "CNBC short clips", "Financial news threads"],
        "platforms": ["Instagram", "TikTok", "YouTube Shorts"],
        "best_ctas": ["'Save this before your next paycheck'",
                      "'Follow to learn what schools never taught you'",
                      "'Link in bio for free budget spreadsheet'"],
    },
    {
        "niche": "Fitness / Body Transformation",
        "monetization": 9,
        "growth_speed": 9,
        "competition": 9,
        "cpm": "HIGH",
        "affiliate_examples": ["Gymshark", "MyProtein", "Amazon supplements",
                               "Fitness courses", "Meal prep apps"],
        "why_converts": "Visual results drive emotional buying — transformation = trust",
        "content_sources": ["Reddit r/fitness transformations", "YouTube fitness channels",
                            "Gym motivation TikToks", "Before/after repost with credit"],
        "platforms": ["TikTok", "Instagram", "YouTube Shorts"],
        "best_ctas": ["'Save this workout'", "'Follow for daily fitness motivation'",
                      "'Free workout plan — link in bio'"],
    },
    {
        "niche": "Luxury Lifestyle / Motivation",
        "monetization": 8,
        "growth_speed": 10,
        "competition": 8,
        "cpm": "MEDIUM-HIGH",
        "affiliate_examples": ["Watches (affiliate programs)", "Courses on entrepreneurship",
                               "NordVPN/ExpressVPN", "Trading platforms"],
        "why_converts": "Aspirational content triggers impulse purchases",
        "content_sources": ["YouTube luxury channels", "Supercar clips", "Mansion tours",
                            "CEO interview clips", "Motivational speech clips"],
        "platforms": ["TikTok", "Instagram", "YouTube Shorts"],
        "best_ctas": ["'Follow if you want this life'",
                      "'Save this for when you need motivation'",
                      "'Link in bio — how I built this'"],
    },
    {
        "niche": "Pets / Cute Animals",
        "monetization": 7,
        "growth_speed": 10,
        "competition": 6,
        "cpm": "MEDIUM",
        "affiliate_examples": ["Chewy affiliate", "Amazon pet supplies", "Pet insurance",
                               "CBD for pets", "Training courses"],
        "why_converts": "Emotional connection + impulse gifting for pet owners",
        "content_sources": ["Reddit r/aww", "r/dogs", "r/cats", "ViralHog licensed clips",
                            "Pet owner TikToks (with permission/credit)"],
        "platforms": ["TikTok", "Instagram", "YouTube Shorts"],
        "best_ctas": ["'Follow for daily dose of happiness'",
                      "'Tag a pet owner who needs to see this'",
                      "'Best pet products — link in bio'"],
    },
    {
        "niche": "Food / Recipes / Cooking Hacks",
        "monetization": 7,
        "growth_speed": 9,
        "competition": 7,
        "cpm": "MEDIUM",
        "affiliate_examples": ["HelloFresh", "Blue Apron", "Kitchen Amazon products",
                               "Cooking courses", "Cookware brands"],
        "why_converts": "Daily need content — everyone eats. High save/revisit rate.",
        "content_sources": ["Recipe TikToks", "Food YouTube channels",
                            "Reddit r/GifRecipes", "AllRecipes", "Food blogger clips"],
        "platforms": ["TikTok", "Instagram", "YouTube Shorts", "Pinterest"],
        "best_ctas": ["'Save this recipe before you lose it'",
                      "'Follow for a new recipe every day'",
                      "'My must-have kitchen tools — link in bio'"],
    },
    {
        "niche": "Tech / AI Tools",
        "monetization": 9,
        "growth_speed": 8,
        "competition": 5,
        "cpm": "HIGH",
        "affiliate_examples": ["AI tools (Jasper, Copy.ai)", "VPN services", "Web hosting",
                               "Coding courses", "Software (affiliate SaaS)"],
        "why_converts": "Tech-savvy audience with high purchasing power",
        "content_sources": ["Product Hunt launches", "Tech YouTube channels",
                            "Hacker News top posts", "AI tool demos", "Tech TikTok creators"],
        "platforms": ["TikTok", "YouTube Shorts", "Twitter/X", "LinkedIn"],
        "best_ctas": ["'Save this list of AI tools'",
                      "'Follow for daily tech discoveries'",
                      "'Free AI toolkit — link in bio'"],
    },
    {
        "niche": "Relationships / Dating Advice",
        "monetization": 8,
        "growth_speed": 9,
        "competition": 6,
        "cpm": "MEDIUM-HIGH",
        "affiliate_examples": ["Dating apps (Bumble, Hinge affiliate)",
                               "Self-help books", "Coaching programs", "Courses"],
        "why_converts": "High emotional stakes = high willingness to pay",
        "content_sources": ["Reddit r/relationship_advice", "Dating coach clips",
                            "Psychology of attraction content", "Breakup/healing content"],
        "platforms": ["TikTok", "Instagram", "YouTube Shorts"],
        "best_ctas": ["'Save this — you might need it'",
                      "'Follow if you want to attract the right person'",
                      "'Free guide — link in bio'"],
    },
    {
        "niche": "Mental Health / Self-Care",
        "monetization": 7,
        "growth_speed": 8,
        "competition": 5,
        "cpm": "MEDIUM",
        "affiliate_examples": ["Calm app", "BetterHelp", "Meditation apps",
                               "Journals (Amazon affiliate)", "Supplements"],
        "why_converts": "Growing demand, underserved niches, strong community loyalty",
        "content_sources": ["Therapy tips TikTok", "Anxiety/depression awareness content",
                            "Self-care routines", "Mindfulness creators"],
        "platforms": ["TikTok", "Instagram"],
        "best_ctas": ["'Save this for your next hard day'",
                      "'Follow — your mental health matters'",
                      "'Free mental health resource — link in bio'"],
    },
]


def get_niche_score(niche_name: str) -> Optional[dict]:
    """Return full niche data for a specific niche."""
    niche_lower = niche_name.lower()
    for n in THEME_PAGE_NICHES:
        if niche_lower in n["niche"].lower():
            score = (n["monetization"] * 0.4 + n["growth_speed"] * 0.4
                     + (10 - n["competition"]) * 0.2)
            return {**n, "overall_score": round(score, 1)}
    return None


def get_all_niches_ranked() -> list[dict]:
    """Return all niches ranked by overall score."""
    ranked = []
    for n in THEME_PAGE_NICHES:
        score = (n["monetization"] * 0.4 + n["growth_speed"] * 0.4
                 + (10 - n["competition"]) * 0.2)
        ranked.append({**n, "overall_score": round(score, 1)})
    return sorted(ranked, key=lambda x: -x["overall_score"])


def get_launch_playbook(niche: str, platform: str = "tiktok") -> dict:
    """30-day launch playbook for a new theme page."""
    niche_data = get_niche_score(niche) or get_all_niches_ranked()[0]

    return {
        "niche": niche,
        "platform": platform.title(),
        "phases": [
            {
                "phase": "Week 1 — Foundation",
                "days": "1-7",
                "tasks": [
                    "Create account with niche keyword in username (e.g. @WealthMindsetDaily)",
                    "Write bio using formula: Who + What + CTA + Link",
                    "Set profile picture: high-res niche-related image or branded logo",
                    "Post 2-3x/day minimum — repost trending content from your niche",
                    "Follow 50 accounts in your niche (triggers follow-backs)",
                    "Engage (comment meaningfully) on 20 posts/day in your niche",
                    "Use ALL relevant hashtags — research top 10 in niche",
                    "Do NOT monetize yet — focus 100% on growth",
                ],
                "goal": "First 100-500 followers, understand what content gets the most engagement",
            },
            {
                "phase": "Week 2 — Content Optimization",
                "days": "8-14",
                "tasks": [
                    "Analyze your top 3 performing posts — double down on that content style",
                    "Test 3 different caption styles (question, statement, list)",
                    "Introduce 1 original piece of content (doesn't need to be perfect)",
                    "Start saving viral audio — post one video using trending sound",
                    "Post behind-the-scenes or 'About this page' intro video",
                    "Join 2-3 niche-specific Facebook groups or Discord servers for sourcing",
                    "Set up Linktree or single landing page (even if blank for now)",
                ],
                "goal": "500-2,000 followers, 5%+ engagement rate",
            },
            {
                "phase": "Week 3 — Momentum",
                "days": "15-21",
                "tasks": [
                    "Post a collaboration with another account in your niche (DM them)",
                    "Run a 'Tag a friend' post — dramatically boosts reach",
                    "Test a controversial opinion post ('Hot take: ___') — drives comments",
                    "Set up affiliate account (Amazon Associates takes 1-3 days to approve)",
                    "Add first affiliate link to Linktree (keep it relevant to your niche)",
                    "Create a 'Free resource' post to drive link-in-bio clicks",
                    "Start tracking: which day/time drives the most reach?",
                ],
                "goal": "2,000-10,000 followers, first affiliate clicks",
            },
            {
                "phase": "Week 4 — Monetization Activation",
                "days": "22-30",
                "tasks": [
                    "Add 2-3 affiliate links to Linktree (product reviews in your niche)",
                    "Post one 'soft sell' piece of content per week",
                    "DM 5 brands for gifted product collabs (use media kit template)",
                    "Offer paid shoutouts if you have 5K+ engaged followers",
                    "Create first digital product: PDF guide, template, or checklist ($7-$27)",
                    "Set up email capture: offer freebie for email signup",
                    "Review analytics: double-down on top 3 content formats",
                ],
                "goal": "First $100-$500 in affiliate/shoutout revenue",
            },
        ],
        "content_sources": niche_data.get("content_sources", []),
        "best_ctas": niche_data.get("best_ctas", []),
        "monetization_timeline": get_monetization_blueprint(),
    }


def get_monetization_blueprint() -> list[dict]:
    """Monetization milestones and strategies by follower count."""
    return [
        {
            "milestone": "0–1,000 followers",
            "strategy": "Growth only — no monetization yet",
            "actions": [
                "Sign up for Amazon Associates (0 follower requirement)",
                "Apply for ClickBank, ShareASale affiliate programs",
                "Build posting consistency (2-3x/day)",
            ],
            "realistic_revenue": "$0–$50/month",
        },
        {
            "milestone": "1,000–5,000 followers",
            "strategy": "Affiliate marketing + first digital product",
            "actions": [
                "Add 3-5 relevant affiliate links to bio",
                "Create a $7-$17 digital product (PDF guide, template)",
                "Soft-sell 1-2x per week max",
                "Offer cheap shoutouts ($5-$25 per post)",
            ],
            "realistic_revenue": "$50–$300/month",
        },
        {
            "milestone": "5,000–25,000 followers",
            "strategy": "Brand deals + shoutout marketplace",
            "actions": [
                "List on shoutout marketplaces (Shoutcart, Buysellshoutouts)",
                "Pitch 10 brands per month for gifted/paid collabs",
                "Increase digital product price ($27-$97)",
                "Launch email list with lead magnet",
                "Apply for TikTok Creator Rewards / YouTube Partner Program",
            ],
            "realistic_revenue": "$300–$1,500/month",
        },
        {
            "milestone": "25,000–100,000 followers",
            "strategy": "Premium brand deals + community monetization",
            "actions": [
                "Charge $200-$1,000 per sponsored post",
                "Launch a community (Patreon, Discord, Substack)",
                "Create a mid-ticket course ($197-$497)",
                "Negotiate long-term brand partnerships",
                "Explore speaking/consulting in your niche",
            ],
            "realistic_revenue": "$1,500–$8,000/month",
        },
        {
            "milestone": "100,000+ followers",
            "strategy": "Scale and diversify revenue streams",
            "actions": [
                "Launch a high-ticket offer ($997-$2,997)",
                "Hire a virtual assistant for content management",
                "Build additional theme pages in adjacent niches",
                "Sell the page (theme pages sell for 12-36x monthly revenue)",
            ],
            "realistic_revenue": "$5,000–$50,000+/month",
        },
    ]


def get_content_sourcing_guide() -> dict:
    """Guide to ethically sourcing and reposting content."""
    return {
        "always_do": [
            "Credit the original creator in caption (@username or 'Credit: @username')",
            "Check if creator prefers DM permission before reposting",
            "Use 'Repost' apps (Repost for Instagram, CapCut for TikTok duets)",
            "Add your own commentary/text overlay to add value",
            "Prefer creators who have 'repost welcome' in bio",
        ],
        "content_sources": {
            "free_licensed": [
                "ViralHog.com — licensed viral video clips",
                "Pexels.com — royalty-free video and photo",
                "Pixabay.com — free media",
                "YouTube Creative Commons filtered search",
                "Reddit (contact OP for permission)",
            ],
            "repost_friendly_platforms": [
                "TikTok Duet/Stitch (built-in repost with credit)",
                "Instagram Collab posts (both accounts credited)",
                "Twitter/X Retweet (native feature)",
                "Reddit (share link, original poster credited)",
            ],
            "original_angle": [
                "Add your own text overlay with insight/commentary",
                "Create 'compilation' videos (5 clips = 1 new video)",
                "React to viral content (talking head style)",
                "Voiceover trending content with your take",
            ],
        },
        "avoid": [
            "Reposting without credit (risks account ban + legal issues)",
            "Removing watermarks from TikTok videos",
            "Bulk-downloading content without permission",
            "Reposting content from creators who explicitly say 'no reposts'",
        ],
    }
