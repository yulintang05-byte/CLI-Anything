"""Theme page strategy — niches, growth playbook, content plans, monetization."""

from datetime import datetime, timedelta


# ── Niche profiles ────────────────────────────────────────────────────────────

PROFITABLE_NICHES: list[dict] = [
    {
        "niche": "finance",
        "display": "Finance & Money",
        "difficulty": "MEDIUM",
        "monetization_potential": "VERY HIGH",
        "avg_rpm": "$8–$25",
        "brand_deal_range": "$500–$10K/post",
        "audience": "18–35, aspiring investors, people in debt, hustlers",
        "top_formats": ["Talking head finance tips", "Screen recordings of investing apps", "Income transparency"],
        "example_pages": ["@humphreytalks", "@grahamstephan", "@andrei_jikh"],
        "growth_speed": "MEDIUM",
        "content_difficulty": "MEDIUM",
        "trend_longevity": "HIGH",
    },
    {
        "niche": "fitness",
        "display": "Fitness & Health",
        "difficulty": "MEDIUM",
        "monetization_potential": "HIGH",
        "avg_rpm": "$3–$8",
        "brand_deal_range": "$200–$5K/post",
        "audience": "18–40, gym beginners, weight loss seekers",
        "top_formats": ["Workout demos", "Before/after transformations", "Meal prep"],
        "example_pages": ["@natacha.oceane", "@blogilates", "@athleanx"],
        "growth_speed": "MEDIUM",
        "content_difficulty": "LOW",
        "trend_longevity": "HIGH",
    },
    {
        "niche": "motivation",
        "display": "Motivation & Mindset",
        "difficulty": "LOW",
        "monetization_potential": "MEDIUM",
        "avg_rpm": "$2–$6",
        "brand_deal_range": "$100–$2K/post",
        "audience": "15–30, students, entrepreneurs, depressed scrollers",
        "top_formats": ["Quote graphics + trending audio", "Storytime motivation", "Speech clips over b-roll"],
        "example_pages": ["@motivationmafia", "@goalcast"],
        "growth_speed": "HIGH",
        "content_difficulty": "LOW",
        "trend_longevity": "MEDIUM",
        "theme_page_note": "Classic theme page model — repost + credit is the fastest growth play.",
    },
    {
        "niche": "luxury_lifestyle",
        "display": "Luxury Lifestyle",
        "difficulty": "LOW",
        "monetization_potential": "HIGH",
        "avg_rpm": "$3–$8",
        "brand_deal_range": "$300–$5K/post",
        "audience": "18–35, aspirational audience, people who want to level up",
        "top_formats": ["Luxury car/home/watch content", "Wealth display reels", "\"How rich people live\" format"],
        "example_pages": ["@luxurylistings"],
        "growth_speed": "VERY HIGH",
        "content_difficulty": "LOW",
        "trend_longevity": "HIGH",
        "theme_page_note": "Pure content curation model. No face needed. Use royalty-free luxury content.",
    },
    {
        "niche": "fashion",
        "display": "Fashion & Style",
        "difficulty": "MEDIUM",
        "monetization_potential": "HIGH",
        "avg_rpm": "$2–$6",
        "brand_deal_range": "$200–$8K/post",
        "audience": "16–30 females, fashion-forward consumers",
        "top_formats": ["OOTD Reels", "Outfit inspiration carousels", "Trend roundups"],
        "example_pages": ["@rewardstyle", "@thefashionspot"],
        "growth_speed": "MEDIUM",
        "content_difficulty": "MEDIUM",
        "trend_longevity": "HIGH",
    },
    {
        "niche": "food",
        "display": "Food & Recipes",
        "difficulty": "LOW",
        "monetization_potential": "MEDIUM",
        "avg_rpm": "$2–$5",
        "brand_deal_range": "$200–$3K/post",
        "audience": "25–45, home cooks, food lovers, parents",
        "top_formats": ["Quick recipe videos", "Food hacks", "\"I made X for $Y\" videos"],
        "example_pages": ["@tasty", "@bonappetitmag"],
        "growth_speed": "HIGH",
        "content_difficulty": "LOW",
        "trend_longevity": "VERY HIGH",
    },
    {
        "niche": "travel",
        "display": "Travel & Adventure",
        "difficulty": "HIGH",
        "monetization_potential": "HIGH",
        "avg_rpm": "$4–$10",
        "brand_deal_range": "$500–$10K/post",
        "audience": "22–40, adventure seekers, bucket-list travelers",
        "top_formats": ["Destination reels", "Travel hacks", "Budget travel breakdowns"],
        "example_pages": ["@nomadicmatt", "@expertvagabond"],
        "growth_speed": "SLOW",
        "content_difficulty": "HIGH",
        "trend_longevity": "VERY HIGH",
    },
    {
        "niche": "beauty",
        "display": "Beauty & Skincare",
        "difficulty": "MEDIUM",
        "monetization_potential": "HIGH",
        "avg_rpm": "$3–$8",
        "brand_deal_range": "$300–$7K/post",
        "audience": "16–35 females, beauty enthusiasts",
        "top_formats": ["Skincare routines", "Product reviews/hauls", "GRWM"],
        "example_pages": ["@hyramhair", "@skkn", "@drpimplepopper"],
        "growth_speed": "MEDIUM",
        "content_difficulty": "MEDIUM",
        "trend_longevity": "HIGH",
    },
    {
        "niche": "pets",
        "display": "Pets & Animals",
        "difficulty": "LOW",
        "monetization_potential": "MEDIUM",
        "avg_rpm": "$2–$5",
        "brand_deal_range": "$200–$3K/post",
        "audience": "All ages, pet owners, animal lovers",
        "top_formats": ["Cute pet moments", "Training tips", "\"A day with my pet\" vlogs"],
        "example_pages": ["@jiffpom", "@noodleandbean"],
        "growth_speed": "VERY HIGH",
        "content_difficulty": "LOW",
        "trend_longevity": "VERY HIGH",
        "theme_page_note": "Viral potential is extremely high. Cute pet content is evergreen.",
    },
    {
        "niche": "business",
        "display": "Business & Entrepreneurship",
        "difficulty": "MEDIUM",
        "monetization_potential": "VERY HIGH",
        "avg_rpm": "$8–$20",
        "brand_deal_range": "$500–$15K/post",
        "audience": "20–40, side-hustlers, founders, aspiring entrepreneurs",
        "top_formats": ["Business breakdowns", "\"How I made X\"", "Tools/software reviews"],
        "example_pages": ["@alilevin", "@patflynn"],
        "growth_speed": "MEDIUM",
        "content_difficulty": "MEDIUM",
        "trend_longevity": "HIGH",
    },
]


# ── Theme page guide ──────────────────────────────────────────────────────────

def get_theme_page_guide() -> dict:
    """Complete theme page playbook."""
    return {
        "what_is_a_theme_page": {
            "definition": "A theme page is a social media account built around a specific topic or aesthetic — not a personal brand. The creator curates, reposts, or creates content within that niche without necessarily showing their face.",
            "examples": ["Luxury car pages", "Motivation quote pages", "Nature photography pages", "Finance tip pages", "Cute animal pages"],
            "why_it_works": "Lower barrier to entry (no personal brand), faster growth via curation, easier to sell or hand off, can run multiple accounts simultaneously.",
        },
        "phases": [
            {
                "phase": 1,
                "title": "Pick Your Niche & Position",
                "duration": "Day 1",
                "actions": [
                    "Choose a niche with high monetization potential (finance, fitness, motivation, luxury)",
                    "Narrow it: Not 'fitness' but 'home workouts for busy moms'",
                    "Research 10 competing theme pages — note their posting frequency, engagement rate, and monetization methods",
                    "Register a clean, niche-relevant username on all platforms (even if you won't use them all immediately)",
                ],
            },
            {
                "phase": 2,
                "title": "Account Setup & Branding",
                "duration": "Days 1–3",
                "actions": [
                    "Create a consistent visual identity: 1 color palette, 1–2 fonts, 1 logo/avatar style",
                    "Write an optimized bio (use the bio formula from 'account optimize bio --platform X')",
                    "Set up link-in-bio tool (Beacons.ai, Stan Store, or Linktree)",
                    "Create 5–7 pre-launch posts before going live",
                    "Set up email list (ConvertKit free tier) connected to link-in-bio",
                ],
            },
            {
                "phase": 3,
                "title": "Content Strategy & Growth (Weeks 1–8)",
                "duration": "8 weeks",
                "actions": [
                    "Post 3–5x/day on TikTok, 1–2x/day on Instagram, 2–3x/week on YouTube Shorts",
                    "First 30 days: 80% reposts with credit, 20% original content",
                    "Weeks 5–8: 60% original, 40% curated — build your unique voice",
                    "Engage aggressively: comment on 20 posts/day in your niche",
                    "Duet/stitch viral content in your niche to piggyback reach",
                    "Track what performs — double down on your top 3 content formats",
                ],
            },
            {
                "phase": 4,
                "title": "Monetization Activation (Month 2+)",
                "duration": "Month 2 onward",
                "actions": [
                    "Launch a free lead magnet to build email list",
                    "Apply for affiliate programs (Amazon, ShareASale, ClickBank, niche-specific)",
                    "Reach out to micro-brands for paid partnerships once you hit 5K followers",
                    "Create a low-ticket digital product ($7–$27) — template, guide, or checklist",
                    "Add TikTok Series or YouTube memberships once eligible",
                ],
            },
        ],
        "repost_guide": {
            "always_credit": "Tag the original creator in caption and on-screen text. This is both ethical and strategic (they may reshare).",
            "permission_tip": "DM creators before reposting — many say yes and may even promote you.",
            "original_overlay": "Add your logo/watermark to reposted content so followers associate it with your page.",
            "curation_value": "Add your commentary, rating, or context to make reposts feel curated, not lazy.",
        },
    }


def get_profitable_niches(sort_by: str = "monetization") -> list[dict]:
    """Return niches sorted by key metric."""
    sort_map = {
        "monetization": lambda n: {"VERY HIGH": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(n["monetization_potential"], 4),
        "growth_speed": lambda n: {"VERY HIGH": 0, "HIGH": 1, "MEDIUM": 2, "SLOW": 3}.get(n["growth_speed"], 4),
        "difficulty": lambda n: {"LOW": 0, "MEDIUM": 1, "HIGH": 2}.get(n["difficulty"], 3),
        "ease": lambda n: {"LOW": 0, "MEDIUM": 1, "HIGH": 2}.get(n["content_difficulty"], 3),
    }
    key = sort_map.get(sort_by, sort_map["monetization"])
    return sorted(PROFITABLE_NICHES, key=key)


def generate_content_plan(niche: str, days: int = 7, platform: str = "tiktok") -> dict:
    """Generate a day-by-day content plan for a theme page."""
    niche_info = next((n for n in PROFITABLE_NICHES if n["niche"] == niche.lower()), None)
    formats = niche_info["top_formats"] if niche_info else ["Educational tip", "Trend content", "Storytime"]

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pillars = ["Education", "Inspiration", "Entertainment", "Trending", "Social Proof", "Behind Scenes", "CTA/Promotion"]
    hooks = [
        "Nobody tells you this about [topic]...",
        "POV: You finally discovered [result]",
        "Stop scrolling — you need to see this",
        "I tested [claim] for 30 days and here's what happened",
        "The [niche] hack that changed everything for me",
        "Why 90% of people fail at [goal] (and how to not be one of them)",
        "Day [X] of [challenge] — shocking results",
    ]

    plan = []
    for i in range(days):
        day = days_of_week[i % 7]
        pillar = pillars[i % len(pillars)]
        fmt = formats[i % len(formats)]
        hook = hooks[i % len(hooks)]
        plan.append({
            "day": i + 1,
            "day_of_week": day,
            "pillar": pillar,
            "content_format": fmt,
            "hook_template": hook,
            "caption_tip": f"End with a question: 'Have you tried this? Comment below 👇'",
            "hashtag_set": f"Run 'hashtags optimize --niche {niche} --platform {platform}' for this post",
        })

    return {
        "niche": niche,
        "platform": platform,
        "days": days,
        "plan": plan,
        "pro_tip": "Batch-create all content for the week in one session. Use CapCut or your preferred editor with saved templates.",
        "repurpose_tip": "Each piece of content should be reformatted for at least 2 platforms (e.g., TikTok → Instagram Reel → YouTube Short).",
    }


# ── Monetization strategies ───────────────────────────────────────────────────

def get_monetization_strategies(niche: str = "") -> dict:
    """Comprehensive monetization playbook."""
    strategies = [
        {
            "method": "Affiliate Marketing",
            "timeline": "Immediate",
            "earning_potential": "$100–$10K/month",
            "effort": "LOW",
            "how": "Promote products/services in your niche and earn commissions (5–50%). Use a link-in-bio tool to track clicks.",
            "best_for": ["motivation", "fitness", "finance", "beauty", "food", "business"],
            "programs": ["Amazon Associates", "ShareASale", "ClickBank", "CJ Affiliate", "Niche brand programs"],
            "tips": ["Promote products you actually use", "Create 'honest review' content to drive affiliate clicks", "Use discount codes for tracking"],
        },
        {
            "method": "Brand Partnerships / Sponsorships",
            "timeline": "Month 2–3 (1K+ followers)",
            "earning_potential": "$100–$50K/post",
            "effort": "MEDIUM",
            "how": "Brands pay you to feature their product. Outreach proactively or use platforms like AspireIQ, Grapevine, Creator.co.",
            "best_for": ["fitness", "fashion", "beauty", "food", "travel", "lifestyle"],
            "programs": ["AspireIQ", "Grapevine Logic", "Creator.co", "Influencer.co", "TikTok Creator Marketplace"],
            "tips": ["Pitch micro-brands first (higher acceptance rate)", "Show engagement rate, not just follower count", "Create a media kit with your stats and rates"],
        },
        {
            "method": "Digital Products",
            "timeline": "Month 1–2",
            "earning_potential": "$500–$20K/month",
            "effort": "MEDIUM",
            "how": "Sell guides, templates, courses, or ebooks. Create once, sell forever. Best margin of any method.",
            "best_for": ["finance", "fitness", "business", "motivation", "beauty"],
            "programs": ["Gumroad", "Stan Store", "Payhip", "Beacons", "Teachable"],
            "tips": ["Start with a $7–$27 product to reduce friction", "Use DM funnels to convert followers to buyers", "Offer a free version to build email list first"],
        },
        {
            "method": "Platform Ad Revenue",
            "timeline": "Month 3–6 (after eligibility)",
            "earning_potential": "$100–$5K/month",
            "effort": "LOW (passive)",
            "how": "TikTok Creator Fund / Pulse, YouTube Partner Program, Instagram Bonuses pay per view/engagement.",
            "requirements": {
                "tiktok": "10K followers + 100K views (30 days) for Creator Fund",
                "youtube": "1K subscribers + 4K watch hours for AdSense",
                "instagram": "Invite-only Bonuses program",
            },
            "tips": ["Don't rely on this as primary income — CPMs are low", "Use platform money to reinvest in content quality"],
        },
        {
            "method": "Email List + Newsletter",
            "timeline": "Month 1 (build from day 1)",
            "earning_potential": "$500–$50K/month (at scale)",
            "effort": "MEDIUM",
            "how": "Build an email list using a free lead magnet. Monetize via affiliate promos, course sales, or paid newsletter tier.",
            "best_for": ["finance", "business", "motivation", "fitness"],
            "programs": ["ConvertKit (free to 1K)", "Beehiiv", "Substack", "MailerLite"],
            "tips": ["Offer a free guide/template/checklist as lead magnet", "Email list is the only audience you truly own", "Mail 1–3x/week with value + one CTA"],
        },
        {
            "method": "Selling the Account",
            "timeline": "6–12 months",
            "earning_potential": "$1K–$500K",
            "effort": "LOW (then high upfront)",
            "how": "Build a theme page to 50K–500K followers, then sell on Fameswap, Flippa, or direct outreach.",
            "tips": ["Document all growth methods — buyers pay more for proven playbooks", "Accounts sell for 10–30x monthly revenue", "Diversified monetization = higher sale price"],
        },
    ]
    if niche:
        n = niche.lower()
        niche_info = next((ni for ni in PROFITABLE_NICHES if ni["niche"] == n), None)
        if niche_info:
            relevant = [s for s in strategies if not s.get("best_for") or n in s.get("best_for", [])]
            return {
                "niche": n,
                "niche_monetization_potential": niche_info["monetization_potential"],
                "avg_brand_deal": niche_info["brand_deal_range"],
                "strategies": relevant,
                "recommended_order": [s["method"] for s in relevant[:3]],
            }
    return {
        "niche": "general",
        "strategies": strategies,
        "recommended_order": ["Affiliate Marketing", "Digital Products", "Brand Partnerships / Sponsorships"],
    }


def get_conversion_tactics() -> dict:
    """Follower-to-customer conversion tactics."""
    return {
        "funnel_overview": {
            "stage_1": "Awareness (Viral content → New followers)",
            "stage_2": "Engagement (Comments, saves → Warm audience)",
            "stage_3": "Conversion (DMs, link-in-bio → Buyers/subscribers)",
        },
        "dm_funnels": [
            {
                "tactic": "Comment Trigger",
                "desc": "Post 'Comment X to get [freebie]' — use ManyChat or Manychat-like tool to auto-DM",
                "conversion_rate": "15–30%",
                "example": "\"Comment GUIDE and I'll DM you my free $0-to-$10K investing checklist 📊\"",
            },
            {
                "tactic": "Story Poll → DM",
                "desc": "Run a poll in Stories. DM everyone who voted with a personalized follow-up",
                "conversion_rate": "10–20%",
                "example": "Poll: 'Want a free [niche] guide?' → Yes voters get auto-DM with link",
            },
            {
                "tactic": "Video CTA → DM Ask",
                "desc": "End video with 'DM me [keyword] for more info' — creates high-intent leads",
                "conversion_rate": "5–15%",
                "example": "\"DM me 'RESULTS' and I'll send you my exact routine\"",
            },
        ],
        "link_in_bio_strategy": {
            "priority_order": [
                "1. Free lead magnet (captures email)",
                "2. Best-selling product",
                "3. Top affiliate link",
                "4. Latest content / YouTube channel",
                "5. Community / Discord / Newsletter",
            ],
            "tools": ["Beacons.ai (free, best for creators)", "Stan Store (best for selling)", "Linktree (simple, free)", "Koji (interactive)"],
            "tip": "Limit to 4–5 links max. More choices = decision paralysis = no clicks.",
        },
        "email_conversion": {
            "welcome_sequence": [
                "Email 1 (Immediate): Deliver the lead magnet + introduce yourself",
                "Email 2 (Day 2): Share your best piece of content / biggest tip",
                "Email 3 (Day 4): Case study or social proof",
                "Email 4 (Day 7): Soft pitch — your product or top affiliate",
            ],
            "conversion_rate": "2–5% of email list buys something in first 30 days",
        },
        "social_proof_plays": [
            "Screenshot testimonials and post as content",
            "Ask buyers/followers to tag you in results",
            "Create a 'Results' highlight on Instagram for transformations",
            "Pin your best review/result in TikTok comments",
        ],
    }
