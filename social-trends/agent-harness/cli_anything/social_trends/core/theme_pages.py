"""Theme page creation, conversion, and monetization playbook.

A theme page (also called a niche page) is an account that curates and
reposts content around a specific topic rather than personal content.
This module provides everything needed to build, convert, and scale one.

Key concepts:
- Content curation: repost viral content from your niche with credit
- Consistent branding: handle, bio, visual identity all match the niche
- Monetization: sponsorships, affiliate links, digital products, shoutouts
- Growth: engagement pods, collab posts, hashtag strategies
"""

from typing import Any


def get_niche_database() -> list[dict]:
    """Return the full niche database with profitability and difficulty ratings.

    Returns:
        List of niche dicts with {name, category, profitability, competition,
        growth_rate, avg_followers_to_monetize, monetization_methods, examples}.
    """
    return _NICHE_DATABASE


def get_niche_info(niche: str) -> dict:
    """Get detailed info for a specific niche.

    Args:
        niche: Niche name (partial match supported).

    Returns:
        Niche info dict or None if not found.
    """
    niche_lower = niche.lower()
    for n in _NICHE_DATABASE:
        if niche_lower in n["name"].lower() or n["name"].lower() in niche_lower:
            return n
    return {
        "name": niche,
        "category": "custom",
        "profitability": "unknown",
        "competition": "unknown",
        "growth_rate": "unknown",
        "avg_followers_to_monetize": 10_000,
        "monetization_methods": ["sponsorships", "affiliate marketing", "digital products"],
        "examples": [],
        "content_pillars": [f"{niche} tips", f"{niche} news", f"{niche} inspiration"],
    }


def get_conversion_playbook(current_niche: str, target_niche: str,
                             current_followers: int) -> dict:
    """Generate a step-by-step playbook to convert an account to a theme page.

    Args:
        current_niche: What the account currently posts about.
        target_niche: The theme/niche to convert to.
        current_followers: Current follower count.

    Returns:
        Dict with conversion roadmap, timeline, and risk assessment.
    """
    niche_info = get_niche_info(target_niche)

    # Risk: converting vs. starting fresh
    if current_followers > 50_000:
        risk = "medium-high"
        risk_note = (
            f"With {current_followers:,} followers, a hard pivot risks losing 30-60% "
            f"of your audience. Consider starting a NEW account for the theme page "
            f"and redirecting traffic from this one."
        )
        recommended = "start_fresh"
    elif current_followers > 10_000:
        risk = "medium"
        risk_note = (
            "A gradual pivot (mixing old + new content over 4-6 weeks) minimizes "
            "audience loss. Announce the change clearly."
        )
        recommended = "gradual_pivot"
    else:
        risk = "low"
        risk_note = (
            "Low follower count = low risk. A hard pivot is fine. "
            "This is the best time to rebrand."
        )
        recommended = "hard_pivot"

    return {
        "current_niche": current_niche,
        "target_niche": target_niche,
        "current_followers": current_followers,
        "conversion_type": recommended,
        "risk_level": risk,
        "risk_note": risk_note,
        "niche_info": niche_info,
        "roadmap": _get_conversion_roadmap(recommended, target_niche, niche_info),
        "branding_checklist": _get_branding_checklist(target_niche),
        "first_30_days": _get_first_30_days_plan(target_niche, niche_info),
        "monetization_timeline": _get_monetization_timeline(
            current_followers, niche_info
        ),
    }


def _get_conversion_roadmap(conv_type: str, niche: str, info: dict) -> list[dict]:
    """Build week-by-week conversion roadmap."""
    if conv_type == "start_fresh":
        return [
            {"week": "Week 1", "action": f"Create new account: @{niche.lower()}daily or @best{niche.lower()}",
             "focus": "Setup: profile, bio, link, first 3 posts"},
            {"week": "Week 2", "action": "Post 2-3x per day from day 1",
             "focus": "Establish content rhythm and niche authority"},
            {"week": "Week 3-4", "action": "Engage with top creators in niche — comment, collab",
             "focus": "Network and cross-promote from old account"},
            {"week": "Month 2", "action": "Pin your 3 best performing posts",
             "focus": "Double down on whatever format is working"},
            {"week": "Month 3+", "action": "Begin monetization outreach",
             "focus": f"First sponsor target: small {niche} brands"},
        ]
    elif conv_type == "gradual_pivot":
        return [
            {"week": "Week 1", "action": "Rebrand profile (username, bio, profile pic)",
             "focus": "Signal the new direction without losing existing audience"},
            {"week": "Week 2-3", "action": "Mix 50% old content / 50% new niche content",
             "focus": "Warm audience to new direction gradually"},
            {"week": "Week 4-5", "action": "Increase to 80% new niche content",
             "focus": "Watch analytics — retain followers who like the new direction"},
            {"week": "Week 6", "action": "Full pivot to theme page",
             "focus": "Remove/archive old non-niche content if needed"},
        ]
    else:  # hard_pivot
        return [
            {"week": "Day 1", "action": "Change username, bio, profile pic to match niche",
             "focus": "Complete visual rebrand in one day"},
            {"week": "Day 2-7", "action": "Post 2-3x per day of new niche content",
             "focus": "Flood feed with high-quality niche content to signal algorithm"},
            {"week": "Week 2-4", "action": "Engage with niche community — follow, comment, collab",
             "focus": "Build network and grow faster"},
            {"week": "Month 2+", "action": "Content series and consistent format",
             "focus": "Build brand identity and audience expectations"},
        ]


def _get_branding_checklist(niche: str) -> list[dict]:
    """Return a branding setup checklist for a theme page."""
    return [
        {"item": "Username", "guidance": f"Use @{niche}daily, @best{niche}, @{niche}hub, or @{niche}world"},
        {"item": "Profile Picture", "guidance": "Use a logo or branded image — NOT a personal photo"},
        {"item": "Bio", "guidance": f"State exactly what you post: '{niche.title()} content daily | Follow for the best {niche}'"},
        {"item": "Link in Bio", "guidance": "Linktree or Beacons page: affiliate products, digital products, contact for promos"},
        {"item": "Color Palette", "guidance": "Pick 2-3 consistent brand colors. Use Canva templates"},
        {"item": "Cover/Banner", "guidance": "YouTube/Twitter: create a banner with your posting schedule"},
        {"item": "Pinned Post", "guidance": "Pin your most viral video or a 'Welcome to the page' post"},
        {"item": "Highlights (Instagram)", "guidance": "Create IG Story Highlights: FAQ, Best Posts, Collab Info, Products"},
        {"item": "Content Calendar", "guidance": "Plan 2 weeks of content in advance. Use Notion or Google Sheets"},
        {"item": "Watermark", "guidance": "Add your @handle as a subtle watermark on curated content"},
    ]


def _get_first_30_days_plan(niche: str, info: dict) -> list[dict]:
    """Return a 30-day action plan for a new theme page."""
    return [
        {"days": "1-7", "goal": "Post foundation content",
         "actions": [
             f"Post 2-3 high-quality {niche} videos/posts per day",
             "Use a mix of trending sounds + niche hashtags",
             "Engage with every comment within 1 hour of posting",
             "Follow and engage with 20-30 similar accounts daily",
         ]},
        {"days": "8-14", "goal": "Analyze and double down",
         "actions": [
             "Review analytics: which posts got most reach?",
             "Replicate the format/style of your best performer",
             "Start engaging with trending posts in your niche",
             "DM 3-5 similar accounts for shoutout-for-shoutout (S4S)",
         ]},
        {"days": "15-21", "goal": "Content series and consistency",
         "actions": [
             f"Launch a recurring series (e.g., 'Daily {niche.title()} Tip')",
             "Create shareable content: lists, before/after, hot takes",
             "Optimize your profile based on what new followers respond to",
             "Set up affiliate links if you haven't already",
         ]},
        {"days": "22-30", "goal": "Growth acceleration",
         "actions": [
             "Duet/stitch trending videos in your niche for extra reach",
             "Run a giveaway if you've reached 1K+ followers",
             "Batch-create 2 weeks of content for consistency",
             "First outreach to small brands for gifted collabs",
         ]},
    ]


def _get_monetization_timeline(current_followers: int, info: dict) -> list[dict]:
    """Generate a monetization roadmap based on follower count."""
    methods = info.get("monetization_methods", [])
    timeline = []

    if current_followers < 1_000:
        timeline.append({
            "milestone": "0 → 1K followers",
            "focus": "Build audience, not monetization",
            "actions": ["Set up affiliate links early (Amazon, etc.)", "Document your journey — become relatable"],
        })

    if current_followers < 10_000:
        timeline.append({
            "milestone": "1K → 10K followers",
            "revenue_streams": ["Affiliate marketing (link in bio)", "Digital products (Notion templates, guides)", "Paid story shoutouts ($25-$100)"],
            "estimated_monthly": "$50-$500",
        })

    if current_followers >= 1_000:
        timeline.append({
            "milestone": "10K → 50K followers",
            "revenue_streams": ["Micro-influencer brand deals ($200-$1,000/post)", "TikTok/IG subscriptions", "Email list building → newsletter sponsors", "Your own course/ebook"],
            "estimated_monthly": "$500-$3,000",
        })

    if current_followers >= 10_000:
        timeline.append({
            "milestone": "50K → 100K followers",
            "revenue_streams": ["Mid-tier brand deals ($1,000-$5,000/post)", "YouTube AdSense (if cross-posting)", "Group coaching or community", "Merchandise"],
            "estimated_monthly": "$3,000-$10,000",
        })

    timeline.append({
        "milestone": "100K+ followers",
        "revenue_streams": ["Premium brand deals ($5,000-$50,000/post)", "Agency model (manage other theme pages)", "SaaS products for your niche", "Speaking/consulting"],
        "estimated_monthly": "$10,000+",
    })

    return timeline


def get_content_pillars(niche: str, post_frequency: int = 14) -> dict:
    """Generate content pillars and a posting schedule for a theme page.

    Args:
        niche: Content niche.
        post_frequency: Target posts per week.

    Returns:
        Dict with {pillars, posting_schedule, content_ideas}.
    """
    niche_info = get_niche_info(niche)
    pillars = niche_info.get("content_pillars", [
        f"{niche} tips",
        f"{niche} inspiration",
        f"{niche} news",
        f"{niche} tutorials",
        f"{niche} transformations",
    ])

    ideas_per_pillar = max(3, post_frequency // len(pillars))

    return {
        "niche": niche,
        "pillars": pillars,
        "posts_per_week": post_frequency,
        "pillar_allocation": {p: f"{100 // len(pillars)}% of posts" for p in pillars},
        "content_ideas": _generate_content_ideas(niche, pillars),
        "posting_schedule_template": _build_posting_schedule(pillars),
        "viral_formats": _get_viral_formats(niche),
    }


def _generate_content_ideas(niche: str, pillars: list[str]) -> list[str]:
    """Generate 15 specific content ideas for a niche."""
    templates = [
        f"'5 {niche} mistakes beginners make'",
        f"'{niche} transformation: before vs after'",
        f"'Day in the life of a {niche} creator'",
        f"'Trending {niche} products ranked'",
        f"'I tried every popular {niche} hack — here's what worked'",
        f"'{niche} tips no one talks about'",
        f"'The {niche} routine that changed my life'",
        f"'Answering your {niche} questions'",
        f"'{niche} tier list 2024'",
        f"'What I wish I knew about {niche}'",
        f"'Dueting the most viral {niche} videos'",
        f"'{niche} product review — worth it?'",
        f"'Budget {niche} vs. expensive — which wins?'",
        f"'Following a viral {niche} trend for 30 days'",
        f"'The {niche} algorithm hack that got me 100K views'",
    ]
    return templates


def _build_posting_schedule(pillars: list[str]) -> list[dict]:
    """Build a weekly posting schedule rotating through pillars."""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    schedule = []
    for i, day in enumerate(days):
        pillar = pillars[i % len(pillars)]
        schedule.append({
            "day": day,
            "pillar": pillar,
            "content_type": "video" if i % 3 != 2 else "carousel/image",
            "best_time_utc": ["06:00", "10:00", "19:00"][i % 3],
        })
    return schedule


def _get_viral_formats(niche: str) -> list[dict]:
    """Return the highest-converting video formats for a niche."""
    universal = [
        {"format": "POV / storytime", "avg_retention": "75%", "example": f"POV: you discovered {niche}"},
        {"format": "Before & After", "avg_retention": "80%", "example": f"{niche} transformation in 30 days"},
        {"format": "Hot take / controversy", "avg_retention": "85%", "example": f"Unpopular opinion about {niche}"},
        {"format": "List / Countdown", "avg_retention": "70%", "example": f"5 {niche} tips ranked"},
        {"format": "Tutorial / How-to", "avg_retention": "65%", "example": f"How to start {niche} from zero"},
        {"format": "React / Duet", "avg_retention": "72%", "example": f"Reacting to viral {niche} videos"},
        {"format": "Day in the Life", "avg_retention": "68%", "example": f"Day in my life as a {niche} creator"},
    ]
    return universal


# ── Niche Database ────────────────────────────────────────────────────────

_NICHE_DATABASE = [
    {
        "name": "fitness",
        "category": "health & wellness",
        "profitability": "very high",
        "competition": "high",
        "growth_rate": "fast",
        "avg_followers_to_monetize": 5_000,
        "monetization_methods": ["gym supplements (affiliate)", "online coaching", "workout programs", "brand deals", "app partnerships"],
        "examples": ["@gymshark", "@leanbeefpatty", "@cbum"],
        "content_pillars": ["workout routines", "nutrition tips", "transformation stories", "gym motivation", "form tutorials"],
        "avg_cpm": "$8-$15",
    },
    {
        "name": "finance",
        "category": "money & business",
        "profitability": "very high",
        "competition": "medium",
        "growth_rate": "fast",
        "avg_followers_to_monetize": 3_000,
        "monetization_methods": ["investing apps (Webull, Robinhood)", "courses", "newsletters", "crypto platforms", "credit card referrals"],
        "examples": ["@andrei_jikh", "@grahamstephan"],
        "content_pillars": ["investing basics", "budget tips", "side hustles", "financial news", "success stories"],
        "avg_cpm": "$12-$25",
    },
    {
        "name": "cooking",
        "category": "food & lifestyle",
        "profitability": "high",
        "competition": "very high",
        "growth_rate": "steady",
        "avg_followers_to_monetize": 8_000,
        "monetization_methods": ["kitchen tools (affiliate)", "meal kits", "recipe books", "cooking courses", "brand deals"],
        "examples": ["@gordonramsay", "@tasty", "@twisted"],
        "content_pillars": ["quick recipes", "cooking hacks", "meal prep", "budget meals", "restaurant recreations"],
        "avg_cpm": "$5-$10",
    },
    {
        "name": "fashion",
        "category": "lifestyle",
        "profitability": "high",
        "competition": "very high",
        "growth_rate": "fast",
        "avg_followers_to_monetize": 5_000,
        "monetization_methods": ["LTK/RewardStyle", "brand collabs", "clothing drops", "styling services", "Depop/Poshmark"],
        "examples": ["@emilybader", "@daviddobrik"],
        "content_pillars": ["outfit ideas", "thrift flips", "trend reports", "style guides", "shopping hauls"],
        "avg_cpm": "$7-$12",
    },
    {
        "name": "motivation",
        "category": "personal development",
        "profitability": "high",
        "competition": "medium",
        "growth_rate": "very fast",
        "avg_followers_to_monetize": 2_000,
        "monetization_methods": ["courses", "coaching", "ebooks", "speaking", "newsletter"],
        "examples": ["@alexhormozi", "@garyvee"],
        "content_pillars": ["daily quotes", "success stories", "mindset tips", "entrepreneur content", "life lessons"],
        "avg_cpm": "$10-$20",
    },
    {
        "name": "beauty",
        "category": "health & lifestyle",
        "profitability": "very high",
        "competition": "very high",
        "growth_rate": "fast",
        "avg_followers_to_monetize": 3_000,
        "monetization_methods": ["Sephora/Ulta affiliate", "brand partnerships", "product launches", "makeup courses"],
        "examples": ["@nikkietutorials", "@jamescharles"],
        "content_pillars": ["tutorials", "product reviews", "skincare routines", "drugstore finds", "transformations"],
        "avg_cpm": "$8-$18",
    },
    {
        "name": "travel",
        "category": "lifestyle",
        "profitability": "high",
        "competition": "medium",
        "growth_rate": "steady",
        "avg_followers_to_monetize": 10_000,
        "monetization_methods": ["hotel/travel brand deals", "Booking.com affiliate", "travel presets/guides", "travel agency partnerships"],
        "examples": ["@kylieversailles", "@baldguytravels"],
        "content_pillars": ["destination guides", "travel hacks", "budget travel", "hidden gems", "vlog content"],
        "avg_cpm": "$6-$12",
    },
    {
        "name": "gaming",
        "category": "entertainment",
        "profitability": "high",
        "competition": "very high",
        "growth_rate": "fast",
        "avg_followers_to_monetize": 1_000,
        "monetization_methods": ["Twitch subs", "YouTube AdSense", "game sponsorships", "peripherals (affiliate)", "digital goods"],
        "examples": ["@xqc", "@pokimane", "@moistcritikal"],
        "content_pillars": ["gameplay clips", "game reviews", "tips & tricks", "gaming news", "reactions"],
        "avg_cpm": "$4-$8",
    },
    {
        "name": "tech",
        "category": "technology",
        "profitability": "very high",
        "competition": "medium",
        "growth_rate": "very fast",
        "avg_followers_to_monetize": 2_000,
        "monetization_methods": ["Amazon tech affiliate", "AI tool sponsorships", "SaaS products", "brand deals", "courses"],
        "examples": ["@mkbhd", "@fireship"],
        "content_pillars": ["AI tools", "product reviews", "tech news", "tutorials", "productivity tips"],
        "avg_cpm": "$15-$30",
    },
    {
        "name": "pets",
        "category": "lifestyle",
        "profitability": "medium",
        "competition": "medium",
        "growth_rate": "steady",
        "avg_followers_to_monetize": 10_000,
        "monetization_methods": ["pet food affiliate", "pet supplies", "brand deals", "merchandise"],
        "examples": ["@jiffpom", "@tunameltsmy heart"],
        "content_pillars": ["cute clips", "training tips", "pet care", "funny moments", "breed content"],
        "avg_cpm": "$4-$8",
    },
    {
        "name": "business",
        "category": "money & business",
        "profitability": "very high",
        "competition": "medium",
        "growth_rate": "fast",
        "avg_followers_to_monetize": 2_000,
        "monetization_methods": ["courses", "consulting", "SaaS tools", "masterminds", "brand deals"],
        "examples": ["@alexhormozi", "@patrickbet-david"],
        "content_pillars": ["case studies", "business tips", "entrepreneur stories", "marketing hacks", "how-to guides"],
        "avg_cpm": "$12-$25",
    },
    {
        "name": "crypto",
        "category": "money & tech",
        "profitability": "very high",
        "competition": "high",
        "growth_rate": "volatile",
        "avg_followers_to_monetize": 5_000,
        "monetization_methods": ["exchange referrals (Coinbase, Binance)", "premium newsletter", "trading courses", "NFT royalties"],
        "examples": ["@coinsider", "@bitboy_crypto"],
        "content_pillars": ["market news", "coin analysis", "DeFi tutorials", "NFT content", "wallets/security"],
        "avg_cpm": "$10-$20",
        "risk_note": "High volatility — audience can drop sharply in bear markets.",
    },
    {
        "name": "art",
        "category": "creative",
        "profitability": "medium",
        "competition": "medium",
        "growth_rate": "steady",
        "avg_followers_to_monetize": 5_000,
        "monetization_methods": ["print on demand", "commissions", "Patreon", "art supply affiliate", "digital downloads"],
        "examples": ["@loish", "@art_shinyobjects"],
        "content_pillars": ["speed paints", "tutorials", "process videos", "finished artwork", "critiques"],
        "avg_cpm": "$5-$10",
    },
]
