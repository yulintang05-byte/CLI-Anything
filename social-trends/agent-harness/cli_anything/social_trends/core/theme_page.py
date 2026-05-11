"""Theme page creation, monetisation, and conversion guide.

A theme page is an anonymous or persona-based social media account built
around a single topic (e.g. "luxury cars", "motivational quotes", "true crime")
rather than a personal brand.  They convert by:

  1. Aggregating viral content from creators  → re-posting with permission/credit
  2. Building an audience fast on a single passion niche
  3. Monetising via affiliate links, shoutout sales, digital products, or brand deals

This module provides:
- Niche profitability research data
- Step-by-step page launch playbook
- Conversion funnel templates (free → paid)
- Shoutout / sponsorship rate cards
- Content sourcing & reposting strategy
- Automation guidance compatible with the rest of CLI-Anything tools
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

# ──────────────────────────────────────────────────────────────────────────────
# Niche profitability data
# ──────────────────────────────────────────────────────────────────────────────

THEME_NICHES: Dict[str, Dict[str, Any]] = {
    "luxury_lifestyle": {
        "display_name": "Luxury Lifestyle",
        "platforms": ["instagram", "tiktok", "youtube"],
        "competition": "high",
        "monetisation_ceiling": "very_high",
        "avg_cpm_usd": 8.50,
        "best_monetisation": ["brand_deals", "affiliate_amazon", "shoutouts"],
        "avg_shoutout_rate_per_10k_followers": 25,
        "audience_buying_power": "high",
        "top_content_types": ["car reveals", "mansion tours", "watches", "jets", "fashion hauls"],
        "viral_hooks": [
            "Things only RICH people understand …",
            "POV: you're a billionaire for a day",
            "Rich vs broke habits (side by side)",
        ],
        "growth_speed": "fast",
        "notes": "Aspirational content is the easiest to go viral. Watch out for copyright on car/house content.",
    },
    "motivation_mindset": {
        "display_name": "Motivation & Mindset",
        "platforms": ["tiktok", "instagram", "youtube"],
        "competition": "very_high",
        "monetisation_ceiling": "high",
        "avg_cpm_usd": 4.00,
        "best_monetisation": ["ebook", "course", "affiliate_audible", "coaching", "shoutouts"],
        "avg_shoutout_rate_per_10k_followers": 15,
        "audience_buying_power": "medium",
        "top_content_types": ["quote videos", "speech clips", "before/after", "discipline habits", "success stories"],
        "viral_hooks": [
            "Most people will never understand this …",
            "The 1% mindset nobody talks about",
            "Stop doing THIS if you want to be successful",
        ],
        "growth_speed": "very_fast",
        "notes": "Quote pages are high volume; differentiate with unique voiceover or original edits.",
    },
    "fitness": {
        "display_name": "Fitness & Body Transformation",
        "platforms": ["tiktok", "instagram", "youtube"],
        "competition": "high",
        "monetisation_ceiling": "very_high",
        "avg_cpm_usd": 6.00,
        "best_monetisation": ["supplement_affiliate", "workout_plans", "coaching", "brand_deals"],
        "avg_shoutout_rate_per_10k_followers": 20,
        "audience_buying_power": "medium_high",
        "top_content_types": ["transformation montages", "workout clips", "nutrition tips", "gym fails", "progress updates"],
        "viral_hooks": [
            "My [X]-day transformation (no steroids)",
            "I did [celebrity workout] for 30 days",
            "Things my trainer told me NOT to share",
        ],
        "growth_speed": "fast",
        "notes": "Before/after content drives massive saves and shares. Partner with supplement brands early.",
    },
    "true_crime": {
        "display_name": "True Crime",
        "platforms": ["tiktok", "youtube"],
        "competition": "medium",
        "monetisation_ceiling": "high",
        "avg_cpm_usd": 9.00,
        "best_monetisation": ["youtube_adsense", "merchandise", "patreon", "podcast_affiliate"],
        "avg_shoutout_rate_per_10k_followers": 18,
        "audience_buying_power": "medium",
        "top_content_types": ["case summaries", "unsolved mysteries", "court footage reactions", "timeline breakdowns"],
        "viral_hooks": [
            "This case still gives me chills …",
            "The CCTV footage that caught the killer",
            "The detail everyone missed in the [famous case]",
        ],
        "growth_speed": "medium",
        "notes": "Very loyal audiences. YouTube AdSense CPM is among highest in this niche. TikTok monetises via LIVE gifts.",
    },
    "animals_pets": {
        "display_name": "Animals & Pets",
        "platforms": ["tiktok", "instagram", "youtube"],
        "competition": "medium",
        "monetisation_ceiling": "medium",
        "avg_cpm_usd": 3.50,
        "best_monetisation": ["pet_affiliate", "merchandise", "adsense", "shoutouts"],
        "avg_shoutout_rate_per_10k_followers": 12,
        "audience_buying_power": "medium",
        "top_content_types": ["funny clips", "rescue stories", "cute compilations", "training tips"],
        "viral_hooks": [
            "This dog does [impossible thing]",
            "We rescued this dog from the street — 6 months later …",
            "Animals that went viral this week",
        ],
        "growth_speed": "very_fast",
        "notes": "Easiest niche to go viral due to emotional content. Monetisation ceiling is lower — supplement with merch.",
    },
    "tech_ai": {
        "display_name": "Tech & AI",
        "platforms": ["youtube", "tiktok", "instagram"],
        "competition": "medium",
        "monetisation_ceiling": "very_high",
        "avg_cpm_usd": 12.00,
        "best_monetisation": ["saas_affiliate", "course", "newsletter_sponsorship", "brand_deals"],
        "avg_shoutout_rate_per_10k_followers": 30,
        "audience_buying_power": "very_high",
        "top_content_types": ["AI tool demos", "tech news", "product reviews", "coding tutorials", "future predictions"],
        "viral_hooks": [
            "This AI tool will replace [job/task]",
            "5 AI tools that feel illegal to know about",
            "The tech they DON'T want you to know",
        ],
        "growth_speed": "fast",
        "notes": "Highest CPM of all niches. SaaS affiliate commissions are recurring (20-40% monthly). Huge upside.",
    },
    "food": {
        "display_name": "Food & Recipes",
        "platforms": ["tiktok", "instagram", "youtube"],
        "competition": "very_high",
        "monetisation_ceiling": "high",
        "avg_cpm_usd": 4.50,
        "best_monetisation": ["kitchen_affiliate", "cookbook", "brand_deals", "adsense"],
        "avg_shoutout_rate_per_10k_followers": 14,
        "audience_buying_power": "medium",
        "top_content_types": ["recipe videos", "restaurant reviews", "cooking hacks", "mukbang", "budget meals"],
        "viral_hooks": [
            "The [X]-ingredient recipe that changed my life",
            "POV: you're eating at the #1 restaurant in [city]",
            "I tested [celebrity]'s recipe so you don't have to",
        ],
        "growth_speed": "very_fast",
        "notes": "Food content has the highest organic reach on all platforms. Kitchen gadget affiliate converts very well.",
    },
    "finance_investing": {
        "display_name": "Finance & Investing",
        "platforms": ["youtube", "tiktok", "instagram"],
        "competition": "high",
        "monetisation_ceiling": "very_high",
        "avg_cpm_usd": 15.00,
        "best_monetisation": ["brokerage_affiliate", "course", "newsletter", "ebook", "consulting"],
        "avg_shoutout_rate_per_10k_followers": 35,
        "audience_buying_power": "high",
        "top_content_types": ["stock picks", "side hustle ideas", "passive income breakdowns", "budget walkthroughs"],
        "viral_hooks": [
            "How I made $[X] in [timeframe] with [method]",
            "The investing mistake that cost me $[X]",
            "If I had $1,000 today I'd invest in THIS",
        ],
        "growth_speed": "medium",
        "notes": "Highest CPM + highest affiliate payouts. Requires trust-building. Very sticky audience once established.",
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# Launch playbook
# ──────────────────────────────────────────────────────────────────────────────

_LAUNCH_PLAYBOOK: List[Dict[str, Any]] = [
    {
        "phase": "Foundation (Days 1-3)",
        "steps": [
            "Choose ONE niche — use 'theme-page niches' command to compare profitability.",
            "Register a username on TikTok, Instagram, and YouTube simultaneously (matching handle).",
            "Set up profiles: photo, bio, link-in-bio (Beacons.ai or Linktree).",
            "Research 20-30 top creators in your niche — save their best-performing posts as inspiration.",
            "Create a content folder: collect 50+ pieces of raw content (clips, images, audio) before launching.",
        ],
    },
    {
        "phase": "Content Engine (Days 4-14)",
        "steps": [
            "Post 3-5 times/day on TikTok for the first 30 days (volume is fuel for the algorithm).",
            "Use trending audio on EVERY post — check 'social-trends tiktok sounds' command daily.",
            "Always credit original creators in your caption when reposting.",
            "Batch create: spend 2-3 hours every 3 days editing a week's content.",
            "Add captions/subtitles to all videos (15-25% completion rate boost).",
            "Engage: comment on top posts in your niche for 20 min/day to build relationships.",
        ],
    },
    {
        "phase": "Monetisation Activation (1K+ followers)",
        "steps": [
            "Add your first affiliate link to bio (Amazon, ClickBank, or niche-specific).",
            "Create a free lead magnet (PDF guide, checklist) to start email list.",
            "Open shoutout pricing at $5-15 per 10K followers (use Shoutcart or direct DMs).",
            "Apply for TikTok Creator Fund (10K+ followers required) — low payout but free money.",
            "Reach out to 3-5 micro-brands in your niche for barter deals (free product for posts).",
        ],
    },
    {
        "phase": "Scale (10K+ followers)",
        "steps": [
            "Hire a video editor on Fiverr ($5-15/video) to increase output volume.",
            "Launch a Patreon or 'exclusive group' (Discord/Telegram) for superfans.",
            "Raise shoutout prices to $25-50 per 10K followers.",
            "Negotiate paid brand deals ($100-500 per post at 10K-50K followers).",
            "Cross-platform: start YouTube Shorts using the same content for compounded reach.",
            "Start email newsletter — it's the only audience you truly own.",
        ],
    },
    {
        "phase": "Automation (50K+ followers)",
        "steps": [
            "Use scheduling tools (Buffer, Later) to automate posting across platforms.",
            "Use CLI-Anything Clipper to batch-process video edits programmatically.",
            "Build a VA (virtual assistant) team for comment replies and DM outreach.",
            "Create a digital product (course, ebook, template pack) for passive income.",
            "Negotiate long-term brand ambassador deals (monthly retainers $1K-5K+).",
        ],
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# Conversion funnel templates
# ──────────────────────────────────────────────────────────────────────────────

_CONVERSION_FUNNELS: Dict[str, Dict[str, Any]] = {
    "affiliate": {
        "name": "Affiliate Conversion Funnel",
        "stages": [
            {"stage": "Awareness", "action": "Viral content showcases a product naturally (no hard sell)"},
            {"stage": "Interest", "action": "Caption CTA: 'Link in bio for the exact [product] I use'"},
            {"stage": "Consideration", "action": "Bio link → Beacons page with affiliate link + short review"},
            {"stage": "Conversion", "action": "Viewer clicks affiliate link → purchases → you earn commission"},
            {"stage": "Retention", "action": "Post follow-up 'how to use' content → repeat purchases"},
        ],
        "avg_conversion_rate": "1-3%",
        "avg_commission_per_sale": "$5-50",
        "platforms": ["tiktok", "instagram", "youtube"],
        "tips": [
            "Never post affiliate link directly in video caption on TikTok (shadowban risk).",
            "Use 'link in bio' CTA — keeps you compliant and trackable.",
            "Stack multiple affiliate programs (Amazon + niche brand + digital product).",
        ],
    },
    "shoutout": {
        "name": "Shoutout / Sponsorship Funnel",
        "stages": [
            {"stage": "Proof of value", "action": "Build 5K+ engaged followers before selling shoutouts"},
            {"stage": "Pricing", "action": "Set rate: $5-25 per 10K followers (depends on niche and engagement)"},
            {"stage": "Listing", "action": "List on Shoutcart, Collabstr, or offer in your bio"},
            {"stage": "Delivery", "action": "Post dedicated video or Story mentioning client's product/page"},
            {"stage": "Report", "action": "Send client screenshot of views/reach as proof of delivery"},
        ],
        "avg_conversion_rate": "N/A (flat fee)",
        "avg_commission_per_sale": "$25-500 per post",
        "platforms": ["tiktok", "instagram"],
        "tips": [
            "Only sell shoutouts for products your audience would genuinely want.",
            "Limit to 1-2 paid posts per week to protect organic engagement.",
            "Raise rates every 10K new followers.",
        ],
    },
    "digital_product": {
        "name": "Digital Product Funnel",
        "stages": [
            {"stage": "Content", "action": "Educational content that leaves audience wanting MORE"},
            {"stage": "Lead magnet", "action": "Free PDF/checklist/template in bio link (builds email list)"},
            {"stage": "Email nurture", "action": "3-5 email sequence delivering value + soft pitch"},
            {"stage": "Offer", "action": "Launch $27-97 digital product (ebook, template, mini-course)"},
            {"stage": "Upsell", "action": "Offer $197-997 deep-dive course or 1:1 coaching after purchase"},
        ],
        "avg_conversion_rate": "2-5% of email list",
        "avg_commission_per_sale": "$27-997",
        "platforms": ["tiktok", "instagram", "youtube"],
        "tips": [
            "Use Gumroad, Payhip, or Stan.store for zero-friction digital product delivery.",
            "Price at $27, $47, or $97 — these convert better than round numbers.",
            "Survey your audience first — create what they ask for.",
        ],
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# Content sourcing strategy
# ──────────────────────────────────────────────────────────────────────────────

_CONTENT_SOURCING: Dict[str, Any] = {
    "legal_methods": [
        "Repost with explicit written permission from original creator (DM them).",
        "Use royalty-free stock (Pexels, Pixabay, Unsplash) for B-roll.",
        "License music via Epidemic Sound, Artlist, or TikTok's own sound library.",
        "Create original content using trending formats (no copyright exposure).",
        "Use clips from public domain or Creative Commons licensed sources.",
        "Interview / collab with creators — you both own the content.",
    ],
    "reposting_best_practices": [
        "Always tag original creator in caption AND video overlay.",
        "Download via SnapTik (TikTok) or Repost for Instagram — preserves watermark.",
        "Never remove watermarks — it's both unethical and risks account strikes.",
        "Add VALUE when reposting: a comment, reaction, educational overlay, or your own audio.",
        "Limit reposts to 30-40% of your content mix — create the rest originally.",
    ],
    "content_creation_tools": [
        "CapCut (mobile) — TikTok-native editing, trending templates, auto-captions.",
        "Canva — quote graphics, carousels, thumbnails.",
        "Descript — AI audio cleanup, transcription, auto-captions.",
        "CLI-Anything Clipper — batch clip extraction and export for multi-platform.",
        "CLI-Anything OBS — screen recording for tutorials and commentary content.",
    ],
    "automation_stack": [
        "Buffer / Later — schedule posts across TikTok, Instagram, YouTube simultaneously.",
        "Zapier — auto-post new YouTube videos to Instagram and TikTok (via Buffer).",
        "Make (Integromat) — scrape trending RSS feeds → push to content queue.",
        "CLI-Anything Clipper → FFmpeg pipeline — bulk vertical crop of horizontal content.",
    ],
}


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def list_niches(
    min_monetisation: Optional[str] = None,
    platform: Optional[str] = None,
) -> Dict[str, Any]:
    """Return all theme page niches, optionally filtered."""
    ceiling_rank = {"low": 0, "medium": 1, "high": 2, "very_high": 3}
    niches = []
    for key, data in THEME_NICHES.items():
        if platform and platform.lower() not in data.get("platforms", []):
            continue
        if min_monetisation:
            if ceiling_rank.get(data["monetisation_ceiling"], 0) < ceiling_rank.get(min_monetisation, 0):
                continue
        niches.append({
            "niche": key,
            "display_name": data["display_name"],
            "platforms": data["platforms"],
            "competition": data["competition"],
            "monetisation_ceiling": data["monetisation_ceiling"],
            "avg_cpm_usd": data["avg_cpm_usd"],
            "growth_speed": data["growth_speed"],
            "best_monetisation": data["best_monetisation"],
        })

    # Sort by CPM descending (proxy for profitability)
    niches.sort(key=lambda n: n["avg_cpm_usd"], reverse=True)

    return {
        "filter_platform": platform,
        "filter_min_monetisation": min_monetisation,
        "count": len(niches),
        "niches": niches,
    }


def get_niche_deep_dive(niche: str) -> Dict[str, Any]:
    """Return full detail for a single niche including hooks and monetisation."""
    key = niche.lower().replace(" ", "_").replace("-", "_")
    data = THEME_NICHES.get(key)
    if data is None:
        available = list(THEME_NICHES.keys())
        raise ValueError(f"Unknown niche '{niche}'. Available: {available}")

    shoutout_rates: Dict[str, str] = {}
    rate_per_10k = data["avg_shoutout_rate_per_10k_followers"]
    for followers in [1_000, 5_000, 10_000, 50_000, 100_000, 500_000]:
        rate = int(rate_per_10k * (followers / 10_000))
        shoutout_rates[f"{followers:,} followers"] = f"${max(5, rate)}/post"

    return {
        **data,
        "niche_key": key,
        "shoutout_rate_card": shoutout_rates,
    }


def get_launch_playbook() -> Dict[str, Any]:
    """Return the full step-by-step theme page launch playbook."""
    return {
        "title": "Theme Page Launch Playbook",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "phases": _LAUNCH_PLAYBOOK,
        "key_rules": [
            "CONSISTENCY beats quality in the growth phase — post even when it's not perfect.",
            "NICHE DOWN — 'fitness' is too broad; 'home workouts for busy moms' converts.",
            "BUILD YOUR EMAIL LIST from day 1 — it's the only asset you fully own.",
            "ENGAGE first 30 minutes after every post — algorithm rewards early interaction.",
            "DON'T monetise too early — wait until you have real engagement, not just followers.",
        ],
    }


def get_conversion_funnel(funnel_type: str) -> Dict[str, Any]:
    """Return a conversion funnel template."""
    key = funnel_type.lower().replace(" ", "_").replace("-", "_")
    funnel = _CONVERSION_FUNNELS.get(key)
    if funnel is None:
        valid = list(_CONVERSION_FUNNELS.keys())
        raise ValueError(f"Unknown funnel type '{funnel_type}'. Valid: {valid}")
    return funnel


def get_content_sourcing_guide() -> Dict[str, Any]:
    """Return the content sourcing and reposting strategy guide."""
    return {
        "title": "Content Sourcing & Reposting Strategy",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        **_CONTENT_SOURCING,
    }


def list_funnel_types() -> List[str]:
    """List available conversion funnel types."""
    return list(_CONVERSION_FUNNELS.keys())


def list_niche_keys() -> List[str]:
    """List all niche keys."""
    return list(THEME_NICHES.keys())
