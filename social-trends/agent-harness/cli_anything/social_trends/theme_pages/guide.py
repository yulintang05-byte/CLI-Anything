"""Theme page creation, conversion, and monetization playbook."""
from __future__ import annotations

import time
from typing import Any


# A theme page (or "niche page") is an account built around a topic, not a person.
# It reposts/curates content in a niche rather than creating original content.

PROFITABLE_NICHES = {
    "motivation": {
        "label": "Motivation / Success Mindset",
        "monetization": ["link in bio (courses)", "affiliate (books, apps)", "shoutouts"],
        "content_sources": ["Motivational speeches (repost with credit)", "Quote graphics", "Success stories"],
        "avg_rpm": "$2–8",
        "competition": "high",
        "growth_speed": "fast",
        "tip": "Compound effect content — short clips of famous speeches + dramatic music",
    },
    "luxury": {
        "label": "Luxury / Lifestyle",
        "monetization": ["affiliate (luxury brands, cars)", "shoutouts", "brand deals"],
        "content_sources": ["Car dealership walkthrough videos", "Real estate tours", "Luxury hotel content"],
        "avg_rpm": "$5–15",
        "competition": "medium",
        "growth_speed": "medium",
        "tip": "Aspirational content converts best — 'a day in the life of a billionaire'",
    },
    "finance": {
        "label": "Personal Finance / Investing",
        "monetization": ["affiliate (brokerage apps)", "AdSense (high CPM $15–40)", "courses"],
        "content_sources": ["Stock/crypto market news reposts", "Financial tip compilations", "Money myth debunking"],
        "avg_rpm": "$15–40",
        "competition": "high",
        "growth_speed": "medium",
        "tip": "Highest CPM niche on YouTube — even 100k views = $2k–4k AdSense",
    },
    "fitness": {
        "label": "Fitness / Gym",
        "monetization": ["affiliate (supplements, gear)", "workout plans", "coaching"],
        "content_sources": ["Transformation videos (with permission)", "Workout clips", "Nutrition tips"],
        "avg_rpm": "$3–10",
        "competition": "very high",
        "growth_speed": "fast",
        "tip": "Before/after transformation content consistently goes viral",
    },
    "animals": {
        "label": "Animals / Pets",
        "monetization": ["AdSense", "pet product affiliate", "merchandise"],
        "content_sources": ["Cute pet compilations", "Animal rescue stories", "Wildlife clips"],
        "avg_rpm": "$2–6",
        "competition": "medium",
        "growth_speed": "very fast",
        "tip": "Easiest niche to grow — emotional content, universal appeal",
    },
    "humor": {
        "label": "Humor / Memes",
        "monetization": ["shoutouts", "merchandise", "brand deals"],
        "content_sources": ["Viral meme reposts", "Trending audio skits", "Reaction compilations"],
        "avg_rpm": "$1–3",
        "competition": "very high",
        "growth_speed": "very fast",
        "tip": "Lowest CPM but fastest growth — monetize through shoutouts at 50k+",
    },
    "beauty": {
        "label": "Beauty / Skincare",
        "monetization": ["affiliate (beauty products)", "brand deals", "courses"],
        "content_sources": ["Product review compilations", "Tutorial reposts", "Before/after content"],
        "avg_rpm": "$5–12",
        "competition": "high",
        "growth_speed": "fast",
        "tip": "Affiliate commissions can exceed AdSense — Sephora pays 5–10% per sale",
    },
    "food": {
        "label": "Food / Recipes",
        "monetization": ["AdSense", "cookbook affiliate", "brand deals (kitchen)"],
        "content_sources": ["Recipe compilations", "Food challenges", "Restaurant reviews"],
        "avg_rpm": "$2–8",
        "competition": "high",
        "growth_speed": "fast",
        "tip": "ASMR food content has 3x average watch time — algorithm loves it",
    },
    "tech": {
        "label": "Tech / AI / Gadgets",
        "monetization": ["affiliate (Amazon tech)", "AdSense (high CPM)", "brand deals"],
        "content_sources": ["Product review reposts", "Tech news clips", "AI tool demos"],
        "avg_rpm": "$8–25",
        "competition": "medium",
        "growth_speed": "medium",
        "tip": "AI content is the fastest-growing sub-niche in 2024–2025",
    },
    "travel": {
        "label": "Travel / Adventure",
        "monetization": ["affiliate (booking, gear)", "sponsorships", "presets/LUTs"],
        "content_sources": ["Drone footage reposts", "Hidden gem compilations", "Travel hack tips"],
        "avg_rpm": "$3–10",
        "competition": "medium",
        "growth_speed": "medium",
        "tip": "Geographic-specific pages (e.g., 'Best of Japan') convert well with travel affiliate",
    },
}

CONTENT_REPURPOSING_TOOLS = [
    {"tool": "CapCut", "free": True, "use": "TikTok watermark removal, auto-captions, templates"},
    {"tool": "Canva", "free": True, "use": "Quote graphics, thumbnails, carousels"},
    {"tool": "InShot", "free": True, "use": "Mobile video editing, aspect ratio conversion"},
    {"tool": "Opus Clip", "free": False, "use": "AI-powered viral clip extraction from long-form video"},
    {"tool": "Repurpose.io", "free": False, "use": "Auto-cross-post TikTok → YouTube Shorts → Reels"},
    {"tool": "HitFilm Express", "free": True, "use": "Desktop editing for complex compositions"},
    {"tool": "Streamlabs Clip", "free": True, "use": "Gaming clip extraction"},
]

MONETIZATION_PATHS = {
    "shoutouts": {
        "description": "Paid promotions for other accounts or brands",
        "how_to": [
            "Create a media kit (follower count, engagement rate, niche, demographics)",
            "List on Shoutcart, Plug.co, or direct DM approach",
            "Rate formula: $10–20 per 10k followers per post (adjust for engagement rate)",
            "Always charge upfront — never post before payment",
        ],
        "when": "As early as 10k followers with good engagement rate (>3%)",
    },
    "affiliate": {
        "description": "Earn commission promoting products with tracked links",
        "how_to": [
            "Amazon Associates: 1–10% commission, easy approval",
            "ShareASale, CJ Affiliate, Impact.com: higher rates, brand-specific",
            "ClickBank: digital products 30–75% commission",
            "Use link-in-bio tools: Linktree, Stan.store, Beacons.ai",
            "Disclose affiliate relationships (#ad, #affiliate) — FTC required",
        ],
        "when": "Day 1 — no follower minimum needed",
    },
    "adsense": {
        "description": "YouTube ad revenue through Partner Program",
        "how_to": [
            "Requirements: 1,000 subscribers + 4,000 watch hours (or 10M Shorts views in 90 days)",
            "Apply via YouTube Studio → Monetization",
            "Shorts RPM: $0.03–0.07 per 1k views",
            "Long-form RPM: $2–40+ per 1k views (niche-dependent)",
        ],
        "when": "After hitting YouTube Partner Program threshold",
    },
    "digital_products": {
        "description": "Sell your own courses, presets, templates, e-books",
        "how_to": [
            "Host on Gumroad (free), Teachable (5%), Stan.store (9%), or Kajabi ($149/mo)",
            "Price: $7–27 entry-level, $97–497 main offer, $1k+ premium/coaching",
            "Build using pain points your audience DMs you about",
            "Launch to email list before social — email converts 5x better than social",
        ],
        "when": "After 10k+ followers with proven audience trust",
    },
    "brand_deals": {
        "description": "Sponsored content for brands",
        "how_to": [
            "Calculate rate: CPM-based (viewcount × $0.05–0.20 for TikTok, $0.10–0.30 for YouTube)",
            "Find deals: AspireIQ, Creator.co, Grin, TikTok Creator Marketplace, direct outreach",
            "Negotiate usage rights — brands pay extra for repurposing your content in ads",
            "Always get contract: deliverables, payment terms, revision rounds, exclusivity clauses",
            "FTC disclosure required: #ad or 'paid partnership' label",
        ],
        "when": "After 50k+ followers, but micro-influencer deals start at 10k",
    },
}

THEME_PAGE_SOP = {
    "phase_1_setup": {
        "label": "Account Setup (Day 1)",
        "steps": [
            "Choose niche using profit matrix: CPM × growth_speed × passion score",
            "Create business account (not personal) on all target platforms",
            "Username: @[niche][keyword] — short, memorable, no numbers/underscores",
            "Profile photo: high-quality niche-relevant image (no face needed for theme pages)",
            "Bio: value prop + niche keyword + CTA + link",
            "Set up Linktree or Stan.store with affiliate links before first post",
            "Create content bank: source and download 30–50 pieces of niche content",
        ],
    },
    "phase_2_content": {
        "label": "Content Engine (Days 2–30)",
        "steps": [
            "Post 2–3x/day on TikTok, 1x/day on YouTube Shorts, 1x/day on Instagram Reels",
            "Source content: YouTube (Creative Commons), Reddit, Twitter/X embeds, with-permission reposts",
            "ALWAYS credit original creators (@username in caption or on-screen text)",
            "Add value: captions, context, your commentary overlay, or audio commentary",
            "Remove platform watermarks before cross-posting (CapCut → download without watermark)",
            "Batch production: dedicate 2–3 hours per session to create a week's content",
            "Use trending audio from TikTok — search 'viral sounds this week'",
        ],
    },
    "phase_3_grow": {
        "label": "Growth Hacking (Days 15–60)",
        "steps": [
            "Engage in comments of top creators in your niche — be first, be insightful",
            "Duet/stitch trending niche content weekly",
            "Follow-unfollow strategy (sparingly): follow engaged users in your niche",
            "Post your best-performing video as a Story with a poll/question",
            "Create a 'save this' style video (resource compilations drive saves → algorithm boost)",
            "Reply to ALL comments in first 2 hours after posting",
        ],
    },
    "phase_4_monetize": {
        "label": "Monetization (60 days+)",
        "steps": [
            "Audit engagement rate: likes+comments / followers — target >3%",
            "Join TikTok Creator Marketplace + YouTube BrandConnect",
            "Set up affiliate links for your top 3 product categories",
            "Post your media kit to your bio as a PDF download",
            "DM 5 small brands in your niche per week with collab proposal",
            "Launch first digital product once you understand audience pain points",
        ],
    },
}


def generate_theme_page_guide(
    niche: str = "",
    current_followers: int = 0,
    target_platform: str = "all",
) -> dict:
    """
    Generate a complete theme page creation and conversion guide.

    Args:
        niche: Content niche (e.g., finance, fitness, motivation)
        current_followers: Current follower count (0 = starting fresh)
        target_platform: tiktok, youtube, instagram, or all
    """
    niche_key = _match_niche(niche)
    niche_data = PROFITABLE_NICHES.get(niche_key, {})

    # Rank all niches by profitability score
    niche_ranking = _rank_niches()

    phase = _current_phase(current_followers)

    return {
        "niche": niche or "not specified (see top niches)",
        "niche_data": niche_data,
        "top_10_niches_by_profit": niche_ranking[:10],
        "theme_page_sop": THEME_PAGE_SOP,
        "current_phase": phase,
        "monetization_paths": MONETIZATION_PATHS,
        "repurposing_tools": CONTENT_REPURPOSING_TOOLS,
        "legal_notes": _legal_notes(),
        "conversion_checklist": _conversion_checklist(niche_data),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def _match_niche(niche: str) -> str:
    niche_lower = niche.lower() if niche else ""
    for key in PROFITABLE_NICHES:
        if key in niche_lower or niche_lower in key:
            return key
    # Partial match
    for key in PROFITABLE_NICHES:
        if any(word in niche_lower for word in key.split("_")):
            return key
    return ""


def _rank_niches() -> list[dict]:
    def profit_score(data: dict) -> float:
        rpm_str = data.get("avg_rpm", "$0–0")
        nums = [float(x.replace("$", "").replace("+", "")) for x in rpm_str.split("–") if x.replace("$", "").replace("+", "").isdigit() or x.replace("$", "").replace("+", "").replace(".", "").isdigit()]
        avg_rpm = sum(nums) / len(nums) if nums else 1.0

        speed_map = {"very fast": 4, "fast": 3, "medium": 2, "slow": 1}
        comp_map = {"low": 3, "medium": 2, "high": 1, "very high": 0.5}
        speed = speed_map.get(data.get("growth_speed", "medium"), 2)
        comp = comp_map.get(data.get("competition", "high"), 1)
        return avg_rpm * speed * comp

    ranked = sorted(
        [
            {
                "niche": key,
                "label": data["label"],
                "avg_rpm": data["avg_rpm"],
                "growth_speed": data["growth_speed"],
                "competition": data["competition"],
                "monetization": data["monetization"],
                "tip": data["tip"],
                "profit_score": round(profit_score(data), 1),
            }
            for key, data in PROFITABLE_NICHES.items()
        ],
        key=lambda x: x["profit_score"],
        reverse=True,
    )
    return ranked


def _current_phase(followers: int) -> dict:
    if followers == 0:
        return {"phase": "pre-launch", "next_step": "Execute Phase 1 SOP — account setup"}
    if followers < 1000:
        return {"phase": "launch", "next_step": "Post 3x/day, focus on TikTok FYP reach"}
    if followers < 10000:
        return {"phase": "momentum", "next_step": "Establish content series, cross-post aggressively"}
    if followers < 100000:
        return {"phase": "scale", "next_step": "Launch affiliate + first brand deal outreach"}
    return {"phase": "authority", "next_step": "Digital product launch + brand partnership retainers"}


def _conversion_checklist(niche_data: dict) -> list[dict]:
    checks = [
        {"item": "Business account created on all target platforms", "priority": "critical"},
        {"item": "Niche keyword in username", "priority": "high"},
        {"item": "Professional profile photo (niche-relevant)", "priority": "high"},
        {"item": "Bio optimized with value prop + CTA + link", "priority": "critical"},
        {"item": "Link-in-bio tool set up (Linktree/Beacons/Stan.store)", "priority": "high"},
        {"item": "Content bank of 30+ pieces ready before launch", "priority": "critical"},
        {"item": "Affiliate links selected for top 3 niche products", "priority": "medium"},
        {"item": "Posting schedule locked in (same times daily)", "priority": "high"},
        {"item": "CapCut/InShot installed for watermark removal", "priority": "medium"},
        {"item": "Analytics tracking set up (platform native)", "priority": "high"},
    ]
    if niche_data:
        for source in niche_data.get("content_sources", []):
            checks.append({"item": f"Content source identified: {source}", "priority": "medium"})
    return checks


def _legal_notes() -> list[str]:
    return [
        "Copyright: Always credit original creators. For reposted content, get explicit written permission where possible.",
        "Fair Use (US): Commentary, criticism, and education may qualify — consult fair use guidelines.",
        "FTC Disclosure: Label ALL sponsored/affiliate content with #ad or #affiliate or 'paid partnership'.",
        "Platform ToS: Each platform prohibits certain repurposing — review community guidelines regularly.",
        "Music Licensing: Use royalty-free music (YouTube Audio Library, Epidemic Sound) for long-form YouTube to avoid demonetization.",
        "GDPR/CCPA: If collecting emails, ensure compliant privacy policy and opt-in mechanisms.",
    ]
