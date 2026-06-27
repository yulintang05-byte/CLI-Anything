"""Theme page creation guide — strategies, niche research,
monetization paths, and conversion optimization for theme pages."""

from typing import Optional

# ── What is a theme page ──────────────────────────────────────────

THEME_PAGE_EXPLAINER = """
WHAT IS A THEME PAGE?
━━━━━━━━━━━━━━━━━━━━
A theme page (also called a "content curation page" or "niche page") is a
social media account built around a single topic — e.g., Luxury Cars,
Motivational Quotes, Cute Dogs, Travel Destinations, Memes — where you
aggregate and post curated content (with proper credit or original edits)
rather than filming yourself.

WHY THEME PAGES WORK:
• No face required — lower barrier to start
• Scale multiple accounts simultaneously
• Build large audiences fast with trending + evergreen content
• Monetize via shoutout sales, affiliate links, digital products, brand deals
• Each account is a passive income asset that grows in value
"""

# ── High-converting niches ────────────────────────────────────────

TOP_NICHES = [
    {
        "niche": "Luxury Lifestyle",
        "keywords": ["luxury", "wealth", "millionaire", "lambo", "mansions"],
        "monetization": ["Shoutouts", "Affiliate (watches, cars, fashion)", "Digital products"],
        "avg_cpm": "high",
        "competition": "high",
        "difficulty": 6,
        "tip": "Repurpose public viral luxury content. Hook: 'When you make $10M/year...'",
    },
    {
        "niche": "Motivation / Mindset",
        "keywords": ["motivation", "success", "hustle", "mindset", "grind"],
        "monetization": ["Shoutouts", "Ebooks", "Online course affiliate", "Supplements"],
        "avg_cpm": "medium-high",
        "competition": "very high",
        "difficulty": 4,
        "tip": "Pair quotes with satisfying video (nature, drone, time-lapse). Short = viral.",
    },
    {
        "niche": "Cute Animals / Pets",
        "keywords": ["dogs", "cats", "puppies", "kittens", "animals"],
        "monetization": ["Shoutouts", "Pet product affiliate", "Merchandise"],
        "avg_cpm": "medium",
        "competition": "high",
        "difficulty": 3,
        "tip": "Easiest to grow. Repurpose Reddit r/aww, r/AnimalsBeingBros clips.",
    },
    {
        "niche": "Dark Humor / Memes",
        "keywords": ["memes", "funny", "humor", "comedy", "trending"],
        "monetization": ["Shoutouts", "Merch", "Membership"],
        "avg_cpm": "medium",
        "competition": "high",
        "difficulty": 5,
        "tip": "Stay 24h ahead of meme cycles. Join meme subreddits and Twitter to source early.",
    },
    {
        "niche": "Finance / Side Hustles",
        "keywords": ["money", "invest", "sidehustle", "passive income", "crypto"],
        "monetization": ["Affiliate (credit cards, brokers, courses)", "Paid newsletter", "Ebooks"],
        "avg_cpm": "very high",
        "competition": "medium",
        "difficulty": 7,
        "tip": "Finance has highest CPM on YouTube. Pair real data with simple graphics.",
    },
    {
        "niche": "Travel / Aesthetic",
        "keywords": ["travel", "wanderlust", "destinations", "explore", "views"],
        "monetization": ["Shoutouts", "Travel affiliate (Booking, Hotels)", "Presets & LUTs"],
        "avg_cpm": "medium",
        "competition": "high",
        "difficulty": 5,
        "tip": "Use drone footage + chill lo-fi music. Amalfi Coast, Santorini, Bali = reliable viral.",
    },
    {
        "niche": "Fitness / Body Transformation",
        "keywords": ["fitness", "workout", "gym", "transformation", "bodybuilding"],
        "monetization": ["Supplement affiliate", "Coaching programs", "Ebooks", "Shoutouts"],
        "avg_cpm": "high",
        "competition": "very high",
        "difficulty": 6,
        "tip": "Transformation time-lapses and before/after get 10× more saves than regular content.",
    },
    {
        "niche": "Quotes / Aesthetic Text",
        "keywords": ["quotes", "aesthetic", "words", "life", "poetry"],
        "monetization": ["Shoutouts", "Print-on-demand merch", "Digital downloads"],
        "avg_cpm": "low",
        "competition": "medium",
        "difficulty": 2,
        "tip": "Easiest to create (Canva). Batch 30 posts in 2 hours. Use Pinterest as source.",
    },
    {
        "niche": "Cars / Automotive",
        "keywords": ["cars", "supercars", "racing", "exotic cars", "automotive"],
        "monetization": ["Shoutouts", "Car affiliate", "Parts affiliate", "Auto insurance affiliate"],
        "avg_cpm": "high",
        "competition": "medium",
        "difficulty": 5,
        "tip": "Ferrari / Lamborghini content is evergreen. Use @supercarblondie style.",
    },
    {
        "niche": "Food / Recipes",
        "keywords": ["food", "recipe", "cooking", "foodie", "asmr"],
        "monetization": ["Brand deals", "Recipe ebook", "Kitchen affiliate", "Cooking courses"],
        "avg_cpm": "medium",
        "competition": "high",
        "difficulty": 6,
        "tip": "ASMR cooking content + simple 60-sec recipes dominate TikTok and YouTube Shorts.",
    },
]


def list_niches(sort_by: str = "difficulty") -> list:
    """Return niches sorted by difficulty or competition."""
    if sort_by == "difficulty":
        return sorted(TOP_NICHES, key=lambda x: x["difficulty"])
    return TOP_NICHES


# ── Step-by-step playbook ─────────────────────────────────────────

THEME_PAGE_PLAYBOOK = [
    {
        "step": 1,
        "title": "Pick Your Niche",
        "actions": [
            "Choose a niche you understand (or can research quickly)",
            "Validate demand: search the niche on TikTok/YouTube — are there accounts with 100k+ followers?",
            "Check monetization FIRST — will brands pay for shoutouts in this niche?",
            "Avoid overly broad niches (e.g. 'lifestyle') — be specific (e.g. 'solo female travel')",
        ],
        "tools": ["cli-anything-social-trends themes list-niches", "Google Trends", "Social Blade"],
    },
    {
        "step": 2,
        "title": "Set Up Your Accounts",
        "actions": [
            "Create username: short, memorable, niche-relevant (e.g. @LuxCarDaily, @QuoteVault)",
            "Same handle across ALL platforms for brand consistency",
            "Profile photo: high-quality niche image (not a selfie for theme pages)",
            "Bio: state exactly what value you deliver + CTA",
            "Set account to Creator mode on TikTok and Instagram",
        ],
        "tools": ["cli-anything-social-trends account add", "Canva for profile art"],
    },
    {
        "step": 3,
        "title": "Content Sourcing System",
        "actions": [
            "Build a content bank of 30+ posts BEFORE you launch",
            "Sources: Reddit (r/[niche]), Pinterest, YouTube, Instagram Reels, Twitter/X",
            "ALWAYS credit original creators in caption or tag them",
            "Edit slightly to avoid re-upload flags: add music, text overlay, or trim ends",
            "Tools: CapCut (mobile), InShot, Canva, Adobe Express",
        ],
        "tools": ["CapCut", "Canva", "Pinterest", "Reddit"],
    },
    {
        "step": 4,
        "title": "Content Format Strategy",
        "actions": [
            "TikTok/Reels/Shorts: 15–60 second vertical videos get max distribution",
            "Instagram feed: aesthetic grid — use same filter/color palette",
            "YouTube: 3–8 minute 'compilation' format for theme pages",
            "Ratio: 80% entertaining content, 20% educational, 0% selling (for first 90 days)",
            "First 3 seconds MUST hook — text overlay + movement",
        ],
        "tools": ["cli-anything-social-trends trends fetch --platform tiktok", "YouTube Shorts"],
    },
    {
        "step": 5,
        "title": "Growth Acceleration (Days 1–90)",
        "actions": [
            "Post 2–3× per day on TikTok for first 30 days",
            "Engage 15 min BEFORE posting: like, comment on 10 similar accounts",
            "Use trending sounds even if unrelated (set to 5% volume under your audio)",
            "Participate in trending challenges — add your niche spin",
            "Pin your best-performing video immediately after it hits 5k views",
            "Run 'Stitch' campaigns: stitch viral videos in your niche with a take",
        ],
        "tools": ["cli-anything-social-trends trends fetch", "cli-anything-social-trends account optimize"],
    },
    {
        "step": 6,
        "title": "Monetization Activation (After 1k–10k Followers)",
        "actions": [
            "Shoutout-for-shoutout (SFS) with similar accounts to cross-promote",
            "Open shoutout sales at 10k followers ($25–$50/post on TikTok to start)",
            "Add affiliate links in bio (Amazon, ShareASale, ClickBank, Impact.com)",
            "Create a simple digital product (ebook, preset pack, template) to sell",
            "Apply for TikTok Creator Fund / YouTube Partner Program",
            "Pitch brands directly via DM — keep it short, include your stats",
        ],
        "tools": ["Linktree", "Gumroad", "Stan Store", "Impact.com"],
    },
    {
        "step": 7,
        "title": "Scale: Build a Portfolio",
        "actions": [
            "Once Account 1 is running smoothly, launch Account 2 in adjacent niche",
            "Repurpose same content across TikTok + Instagram Reels + YouTube Shorts",
            "Build a content team: hire 1 editor on Fiverr for $5–10/post",
            "Automate scheduling with Buffer, Later, or TikTok's built-in scheduler",
            "Track metrics weekly: follower growth, engagement rate, revenue",
        ],
        "tools": ["Buffer", "Later", "Fiverr", "Notion for tracking"],
    },
]


# ── Conversion optimization ───────────────────────────────────────

CONVERSION_TIPS = {
    "bio_cta": [
        "↓ New video every day — Follow to stay ahead",
        "Daily [niche] content — Follow + Turn on notifications 🔔",
        "The #1 [niche] page — [benefit]. Follow below ↓",
        "I post [niche] daily so you don't have to search. Follow ↓",
    ],
    "caption_hooks": [
        "Nobody is talking about this...",
        "POV: you just discovered [niche]",
        "The [niche] account you didn't know you needed 👀",
        "This is why [result] — follow for more",
        "Wait for it... [emoji]",
        "Drop a 🔥 if you want more like this",
        "Tag someone who needs to see this",
    ],
    "engagement_boosters": [
        "Ask a question in every caption ('Which is your favorite?')",
        "Create a 'Part 2' from high-performing content to drive comments",
        "Use 'duet this' or 'stitch this' as a CTA to multiply reach",
        "Reply to every comment as text comment to keep convo going",
        "Post polls in Stories to increase interactive engagement",
    ],
    "link_in_bio_stack": [
        "1. Primary product / affiliate offer",
        "2. Newsletter or email capture (most important asset you own)",
        "3. Main YouTube channel (cross-platform growth)",
        "4. Other platforms (Instagram ↔ TikTok cross-link)",
        "5. Shoutout inquiry form or media kit",
    ],
}


def get_playbook(step: Optional[int] = None) -> list:
    if step is not None:
        return [s for s in THEME_PAGE_PLAYBOOK if s["step"] == step]
    return THEME_PAGE_PLAYBOOK


def get_conversion_tips(category: Optional[str] = None) -> dict:
    if category:
        return {category: CONVERSION_TIPS.get(category, [])}
    return CONVERSION_TIPS


def get_niche_detail(niche_name: str) -> Optional[dict]:
    for n in TOP_NICHES:
        if n["niche"].lower() == niche_name.lower():
            return n
    # fuzzy match on keywords
    niche_name_lower = niche_name.lower()
    for n in TOP_NICHES:
        if any(kw in niche_name_lower or niche_name_lower in kw for kw in n["keywords"]):
            return n
    return None
