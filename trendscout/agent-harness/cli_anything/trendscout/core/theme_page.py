"""TrendScout – Theme page strategy playbook.

A theme page (or "fan/niche page") curates content around a specific topic
rather than a personal brand. This module provides the full playbook:
creation, content strategy, monetization, and conversion tactics.
"""

from typing import Any, Dict, List
from datetime import datetime, timezone


# ── Master playbook ───────────────────────────────────────────────────────────

NICHES_WITH_CPM = [
    {"niche": "Finance / Investing", "audience_size": "massive", "cpm": "high ($15–$45)", "monetization": ["AdSense", "Affiliate (broker/app referrals)", "Digital products", "Paid community"], "competition": "high"},
    {"niche": "Tech / AI Tools", "audience_size": "large", "cpm": "high ($12–$35)", "monetization": ["Affiliate (SaaS tools)", "Sponsorships", "Courses"], "competition": "medium-high"},
    {"niche": "Fitness / Gym", "audience_size": "massive", "cpm": "medium ($6–$18)", "monetization": ["Supplement affiliate", "Program sales", "Merch"], "competition": "very high"},
    {"niche": "Beauty / Skincare", "audience_size": "massive", "cpm": "medium ($5–$15)", "monetization": ["Amazon affiliate", "Brand deals", "Digital lookbooks"], "competition": "very high"},
    {"niche": "Luxury Lifestyle", "audience_size": "medium", "cpm": "very high ($20–$60)", "monetization": ["High-ticket affiliate", "Luxury brand deals", "Newsletter"], "competition": "medium"},
    {"niche": "Travel", "audience_size": "large", "cpm": "medium-high ($8–$25)", "monetization": ["Booking affiliate", "Credit card affiliate", "Guides"], "competition": "high"},
    {"niche": "Food / Recipes", "audience_size": "massive", "cpm": "low-medium ($3–$10)", "monetization": ["Cookbook sales", "AdSense", "Kitchen affiliate"], "competition": "very high"},
    {"niche": "Pets (Cats/Dogs)", "audience_size": "massive", "cpm": "medium ($5–$14)", "monetization": ["Pet product affiliate", "Branded content", "Merch"], "competition": "high"},
    {"niche": "Gaming", "audience_size": "massive", "cpm": "medium ($5–$15)", "monetization": ["Sponsorships", "Twitch/YouTube revenue", "Merch"], "competition": "very high"},
    {"niche": "Motivation / Mindset", "audience_size": "large", "cpm": "medium ($5–$18)", "monetization": ["Digital products", "Courses", "Coaching"], "competition": "high"},
    {"niche": "Relationship / Dating", "audience_size": "large", "cpm": "high ($10–$30)", "monetization": ["Courses", "Coaching", "eBooks"], "competition": "medium"},
    {"niche": "Parenting / Moms", "audience_size": "large", "cpm": "medium ($6–$16)", "monetization": ["Amazon affiliate", "Brand deals", "Digital products"], "competition": "medium"},
    {"niche": "Crypto / NFT", "audience_size": "medium", "cpm": "very high ($20–$70)", "monetization": ["Exchange affiliate", "Paid newsletter", "Consulting"], "competition": "medium"},
    {"niche": "Astrology / Spirituality", "audience_size": "large", "cpm": "medium ($5–$15)", "monetization": ["Readings", "Digital products", "Merch"], "competition": "low-medium"},
    {"niche": "Horror / Creepy", "audience_size": "medium", "cpm": "low-medium ($3–$10)", "monetization": ["AdSense", "Merchandise", "Community"], "competition": "low"},
    {"niche": "True Crime", "audience_size": "medium-large", "cpm": "medium ($6–$18)", "monetization": ["Podcast ads", "Patreon", "Books"], "competition": "medium"},
    {"niche": "Entrepreneurship / Business", "audience_size": "large", "cpm": "very high ($15–$50)", "monetization": ["Courses", "Consulting", "SaaS affiliate"], "competition": "high"},
    {"niche": "Study / Productivity", "audience_size": "medium", "cpm": "medium ($5–$15)", "monetization": ["App affiliate", "Notion templates", "Courses"], "competition": "low-medium"},
    {"niche": "Art / Design", "audience_size": "medium", "cpm": "low-medium ($3–$10)", "monetization": ["Print-on-demand", "Commissions", "Presets/brushes"], "competition": "low"},
    {"niche": "Cars / Automotive", "audience_size": "large", "cpm": "high ($10–$30)", "monetization": ["Insurance affiliate", "Parts affiliate", "Sponsorships"], "competition": "medium"},
]

CONTENT_FORMATS = {
    "tiktok": [
        {"format": "Trend hijack", "description": "Ride a viral trend/sound with a niche-specific twist", "virality": "very high", "effort": "low"},
        {"format": "Hot take / Opinion", "description": "Controversial opinion in your niche gets shares + comments", "virality": "high", "effort": "low"},
        {"format": "Value dump", "description": "'5 things you didn't know about [niche]' — fast-paced", "virality": "high", "effort": "medium"},
        {"format": "Story time", "description": "Personal narrative with a niche lesson. Hooks with 'Nobody talks about this...'", "virality": "high", "effort": "medium"},
        {"format": "Tutorial / How-to", "description": "Step-by-step process in 30–60 seconds", "virality": "medium", "effort": "medium"},
        {"format": "Curation showcase", "description": "Best of [niche]: 'Top 5 X' compiled from other sources (perfect for theme pages)", "virality": "medium", "effort": "very low"},
        {"format": "Reaction / Duet", "description": "React to a viral video in your niche. Built-in discovery from original creator's audience", "virality": "medium-high", "effort": "very low"},
        {"format": "Challenge", "description": "Start or participate in a niche-specific challenge. Ask followers to duet", "virality": "very high", "effort": "medium"},
        {"format": "Day-in-the-life POV", "description": "'POV: You're a [niche person]' format", "virality": "high", "effort": "low"},
        {"format": "Before/After transformation", "description": "Transformation content in any niche. Highly shareable", "virality": "very high", "effort": "medium"},
    ],
    "youtube": [
        {"format": "Listicle", "description": "'Top 10 [niche things]' — evergreen search content", "virality": "medium", "effort": "medium"},
        {"format": "Deep dive / Documentary", "description": "Long-form investigation into a niche topic. High watch time = algorithm boost", "virality": "medium-high", "effort": "high"},
        {"format": "Tutorial / Course-style", "description": "Complete guide on a niche skill. Evergreen traffic", "virality": "medium", "effort": "high"},
        {"format": "Compilation", "description": "Best-of compilations from public domain content. Low effort, consistent views", "virality": "low-medium", "effort": "low"},
        {"format": "Reaction / Commentary", "description": "React to viral content in your niche. Low production barrier", "virality": "medium", "effort": "low"},
        {"format": "Challenge / Experiment", "description": "'I tried X for 30 days' — high completion rate and shares", "virality": "high", "effort": "medium"},
        {"format": "Shorts (vertical)", "description": "Repurpose TikTok content. Shorts introduced to new audience who migrates", "virality": "medium-high", "effort": "very low"},
        {"format": "Collab / Interview", "description": "Feature other creators. Cross-promotion doubles reach", "virality": "medium", "effort": "medium"},
    ],
}

MONETIZATION_METHODS = [
    {
        "method": "Affiliate Marketing",
        "difficulty": "easy",
        "time_to_revenue": "0–4 weeks",
        "income_potential": "$100–$10,000+/mo",
        "how_to": "Join Amazon Associates, ShareASale, or niche-specific programs. Link products in bio/description.",
        "best_for": ["beauty", "tech", "fitness", "food", "pets"],
    },
    {
        "method": "Brand Sponsorships",
        "difficulty": "medium",
        "time_to_revenue": "3–12 months (usually 10k+ followers)",
        "income_potential": "$200–$50,000+ per post",
        "how_to": "Build a media kit (stats + audience demographics). Pitch brands in your niche cold or via FameBit/AspireIQ.",
        "best_for": ["all niches"],
    },
    {
        "method": "Digital Products (eBooks, Presets, Templates)",
        "difficulty": "medium",
        "time_to_revenue": "2–8 weeks",
        "income_potential": "$500–$20,000+/mo",
        "how_to": "Create a Notion template, Lightroom preset, or eBook. Sell via Gumroad or Stan.store.",
        "best_for": ["motivation", "art", "finance", "productivity"],
    },
    {
        "method": "Online Courses",
        "difficulty": "hard",
        "time_to_revenue": "1–6 months",
        "income_potential": "$1,000–$100,000+/launch",
        "how_to": "Use Teachable, Skool, or Kajabi. Validate with a live cohort before recording.",
        "best_for": ["fitness", "finance", "marketing", "tech"],
    },
    {
        "method": "Paid Newsletter / Community (Substack, Patreon)",
        "difficulty": "medium",
        "time_to_revenue": "1–3 months",
        "income_potential": "$500–$30,000+/mo",
        "how_to": "Move your deepest fans to a paid tier. Offer exclusive analysis, early content, or a community.",
        "best_for": ["finance", "crypto", "true crime", "gaming"],
    },
    {
        "method": "YouTube AdSense",
        "difficulty": "easy (once qualified)",
        "time_to_revenue": "4–12 months (1,000 subs + 4,000h watch time)",
        "income_potential": "$1–$30 CPM",
        "how_to": "Enable monetization in YouTube Studio once thresholds are hit. High-CPM niches: finance, law, tech.",
        "best_for": ["finance", "tech", "luxury", "crypto"],
    },
    {
        "method": "TikTok Creator Fund / Series",
        "difficulty": "easy",
        "time_to_revenue": "Ongoing (low pay)",
        "income_potential": "$0.02–$0.04 per 1,000 views",
        "how_to": "Enable in TikTok settings (10k+ followers, 18+). Better: use TikTok Series (paywall for exclusive content).",
        "best_for": ["all niches (supplement, not primary)"],
    },
    {
        "method": "Merchandise (Print-on-Demand)",
        "difficulty": "easy",
        "time_to_revenue": "2–6 weeks",
        "income_potential": "$200–$10,000+/mo",
        "how_to": "Printful or Printify + Shopify. Create designs around inside jokes, catchphrases, or niche symbols.",
        "best_for": ["gaming", "pets", "humor", "art", "sports"],
    },
    {
        "method": "Consulting / Coaching (1:1)",
        "difficulty": "easy to start",
        "time_to_revenue": "1–4 weeks",
        "income_potential": "$100–$1,000/session",
        "how_to": "Offer 30-min calls via Calendly. Price based on outcome value, not hourly rate.",
        "best_for": ["fitness", "finance", "marketing", "business"],
    },
    {
        "method": "Page Flipping (Sell the Account)",
        "difficulty": "medium",
        "time_to_revenue": "3–18 months to build, instant payout",
        "income_potential": "2x–6x monthly revenue at exit",
        "how_to": "Build a theme page to 50k–500k followers, monetize it lightly, then sell on FameSwap or Influencers.club.",
        "best_for": ["all niches — especially ones with clear CPM value"],
    },
]

THEME_PAGE_PLAYBOOK_STEPS = [
    {
        "step": 1,
        "title": "Pick Your Niche",
        "details": [
            "Choose a niche with: high passion (you or your target audience), clear monetization path, and manageable competition.",
            "Use the 'theme-page niches' command to compare CPM and competition levels.",
            "Narrower wins: 'Luxury watches under $5k' beats 'Watches'. 'Vegan athlete fitness' beats 'Fitness'.",
            "Validate: search the niche on TikTok/YouTube. If top accounts have 100k–5M followers, there's room.",
        ],
    },
    {
        "step": 2,
        "title": "Set Up Your Account Brand",
        "details": [
            "Username: [niche_keyword] + [word] (e.g. @luxury_moves, @techpills, @financedaily).",
            "Profile photo: Logo or stylized icon (theme pages use brand logos, not faces).",
            "Bio formula: 'We post [content type] about [niche]. Follow for [specific value].'",
            "Use a consistent color palette in all content (pick 2–3 colors max).",
        ],
    },
    {
        "step": 3,
        "title": "Content Strategy (The 80/20 Curation Model)",
        "details": [
            "80% curated content: Find the best content in your niche and repost/adapt it with your watermark and commentary.",
            "20% original content: Your own takes, hot takes, compilations, tutorials.",
            "CRITICAL for curation: Always credit original creators OR use public domain content to avoid copyright strikes.",
            "Source curated content from: Reddit, Twitter, news articles, public domain video, with-permission creators.",
        ],
    },
    {
        "step": 4,
        "title": "Content Production Workflow",
        "details": [
            "Batch create: dedicate 2–4 hours twice/week to produce 10–14 pieces of content.",
            "Use CapCut (TikTok) or DaVinci Resolve (YouTube) for editing.",
            "Add captions to all videos (85% of social media video is watched muted).",
            "Create templates in Canva for thumbnails (YouTube) and quote cards (Instagram).",
        ],
    },
    {
        "step": 5,
        "title": "Growth Hacking Tactics",
        "details": [
            "First 1,000 followers: Focus on trending sounds + niche-relevant hashtags. Post 2x/day.",
            "1k–10k: Engage with every comment. Do 'engagement pods' with similar-size accounts.",
            "10k–100k: Launch a viral challenge or hashtag. Do collabs. Repurpose across all platforms.",
            "100k+: Introduce monetization. Focus on saving views (saves = YouTube algorithm gold).",
            "The 'Snowball Trick': When a video hits 2x your average views, reply to every comment in the first hour to trigger a second wave.",
        ],
    },
    {
        "step": 6,
        "title": "Monetization Timing",
        "details": [
            "0–1k followers: Build trust, do NOT monetize yet. Only value, value, value.",
            "1k–10k followers: Introduce affiliate links (low-pressure). Grow your email list.",
            "10k–50k: Pitch micro-brand deals. Launch a low-ticket digital product.",
            "50k+: High-ticket sponsorships, courses, paid community, or page flipping.",
            "NEVER monetize before you've built genuine trust in the niche.",
        ],
    },
    {
        "step": 7,
        "title": "Converting & Scaling",
        "details": [
            "Social → Email: Use a lead magnet (free checklist, template, or guide) to build your list.",
            "Use Beehiiv or ConvertKit. A 10k email list > 100k TikTok followers for revenue.",
            "Cross-post: Each TikTok → Instagram Reel → YouTube Short → Twitter. 1 piece of content, 4 platforms.",
            "If organic growth slows: $50/day on TikTok Spark Ads for your best-performing organic video.",
            "Exit strategy: FameSwap.com, BrandSnag, or Influencers.club to sell pages for 3–5x monthly revenue.",
        ],
    },
]


def get_playbook() -> Dict[str, Any]:
    """Return the complete theme page creation playbook."""
    return {
        "title": "Complete Theme Page Creation & Monetization Playbook",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "steps": THEME_PAGE_PLAYBOOK_STEPS,
        "total_steps": len(THEME_PAGE_PLAYBOOK_STEPS),
    }


def get_playbook_step(step_number: int) -> Dict[str, Any]:
    """Return a single step of the playbook with detailed guidance."""
    if step_number < 1 or step_number > len(THEME_PAGE_PLAYBOOK_STEPS):
        raise ValueError(f"Step {step_number} not found. Valid range: 1–{len(THEME_PAGE_PLAYBOOK_STEPS)}")
    step = THEME_PAGE_PLAYBOOK_STEPS[step_number - 1]
    return {
        "step": step["step"],
        "title": step["title"],
        "action_items": step["details"],
        "total_steps": len(THEME_PAGE_PLAYBOOK_STEPS),
        "next_step": step_number + 1 if step_number < len(THEME_PAGE_PLAYBOOK_STEPS) else None,
    }


def list_niches(sort_by: str = "cpm") -> Dict[str, Any]:
    """List profitable niches with CPM, competition, and monetization methods."""
    data = NICHES_WITH_CPM.copy()

    cpm_order = {"very high": 0, "high": 1, "medium-high": 2, "medium": 3, "low-medium": 4, "low": 5}
    comp_order = {"low": 0, "low-medium": 1, "medium": 2, "medium-high": 3, "high": 4, "very high": 5}

    if sort_by == "cpm":
        data.sort(key=lambda x: cpm_order.get(x["cpm"].split(" ")[0].lower(), 99))
    elif sort_by == "competition":
        data.sort(key=lambda x: comp_order.get(x["competition"].lower(), 99))
    elif sort_by == "opportunity":
        # Opportunity = high CPM + low competition
        data.sort(key=lambda x: (
            cpm_order.get(x["cpm"].split(" ")[0].lower(), 99) +
            comp_order.get(x["competition"].lower(), 99)
        ))
    else:
        raise ValueError(f"Unknown sort_by '{sort_by}'. Choose: cpm, competition, opportunity")

    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "sort_by": sort_by,
        "count": len(data),
        "niches": data,
    }


def list_content_formats(platform: str = "tiktok") -> Dict[str, Any]:
    """Return content format recommendations for a platform."""
    plat = platform.lower()
    if plat not in CONTENT_FORMATS:
        raise ValueError(f"Unknown platform '{platform}'. Choose: tiktok, youtube")

    formats = CONTENT_FORMATS[plat].copy()
    formats.sort(key=lambda x: {"very high": 0, "high": 1, "medium-high": 2, "medium": 3, "low-medium": 4, "low": 5}.get(x["virality"].lower(), 99))

    return {
        "platform": plat,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "count": len(formats),
        "formats": formats,
    }


def list_monetization_methods(niche: str = "all") -> Dict[str, Any]:
    """Return monetization strategies, optionally filtered by niche fit."""
    if niche.lower() == "all":
        methods = MONETIZATION_METHODS
    else:
        methods = [
            m for m in MONETIZATION_METHODS
            if niche.lower() in [b.lower() for b in m["best_for"]] or "all niches" in " ".join(m["best_for"]).lower()
        ]

    return {
        "niche_filter": niche,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "count": len(methods),
        "methods": methods,
    }


def quick_start_guide(niche: str, platform: str = "tiktok") -> Dict[str, Any]:
    """Generate a personalized quick-start guide for a niche + platform combo."""
    niche_lower = niche.lower()
    plat = platform.lower()

    # Find matching niche data
    niche_data = next((n for n in NICHES_WITH_CPM if niche_lower in n["niche"].lower()), None)

    # Get top content formats
    formats = CONTENT_FORMATS.get(plat, CONTENT_FORMATS["tiktok"])
    top_formats = sorted(
        formats,
        key=lambda x: {"very high": 0, "high": 1, "medium-high": 2, "medium": 3, "low-medium": 4, "low": 5}.get(x["virality"].lower(), 99)
    )[:3]

    # Get relevant monetization
    mono_methods = [
        m for m in MONETIZATION_METHODS
        if niche_lower in [b.lower() for b in m["best_for"]]
        or "all niches" in " ".join(m["best_for"]).lower()
    ][:3]

    week1 = [
        f"Register @[yourniche]_[keyword] on {plat}",
        "Complete your profile using the 'account audit' checklist",
        f"Study top 5 {niche_lower} accounts on {plat} — note their posting style, frequency, thumbnails",
        "Create a 30-day content calendar (mix of formats from this guide)",
        "Post your first 5 pieces of content to establish a baseline",
    ]

    return {
        "niche": niche,
        "platform": plat,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "niche_overview": niche_data,
        "week_1_actions": week1,
        "top_content_formats": top_formats,
        "recommended_monetization": mono_methods,
        "first_milestone": "1,000 followers — unlocks link-in-bio (TikTok) and affiliate partnerships",
        "pro_tip": (
            f"For {niche_lower} on {plat}: post when your target audience is most active (run 'trends times --platform {plat}'), "
            f"use 3–5 niche hashtags + 1 trending hashtag per post, and engage with every comment for the first 2 hours after posting."
        ),
    }
