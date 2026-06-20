"""Theme page strategy engine — creating and monetizing niche theme pages.

A 'theme page' is a niche-content account that curates and reposts
(with permission) or creates content around a specific theme/interest.
Think: @fitnessmotivation, @luxurycars, @mindsetquotes, @foodporn.

This module provides:
- Niche selection framework with saturation analysis
- Content calendar generation
- Monetization roadmap
- Conversion optimization (link-in-bio, DM funnel, affiliate)
"""

from __future__ import annotations

from datetime import datetime, date, timedelta, timezone
from typing import Any


THEME_NICHES = {
    "fitness_motivation": {
        "description": "Workout clips, transformation stories, gym tips",
        "monetization": ["affiliate (supplements, gym gear)", "coaching upsell", "ebook"],
        "avg_cpm_usd": 4.50,
        "competition": "high",
        "growth_speed": "fast",
        "content_sources": ["repost with credit", "original workout clips", "quotes"],
    },
    "luxury_lifestyle": {
        "description": "Cars, watches, real estate, travel",
        "monetization": ["affiliate (luxury brands)", "lead gen (finance/RE)", "brand deals"],
        "avg_cpm_usd": 8.00,
        "competition": "medium",
        "growth_speed": "medium",
        "content_sources": ["repost with credit", "original shoots", "compilations"],
    },
    "mindset_quotes": {
        "description": "Motivational quotes, success mindset, productivity",
        "monetization": ["digital products", "course/coaching", "affiliate (books/apps)"],
        "avg_cpm_usd": 3.00,
        "competition": "very_high",
        "growth_speed": "fast",
        "content_sources": ["quote graphics (Canva)", "voiceover clips", "book summaries"],
    },
    "finance_education": {
        "description": "Investing, crypto, budgeting, side hustles",
        "monetization": ["affiliate (brokers, cards)", "course", "newsletter"],
        "avg_cpm_usd": 12.00,
        "competition": "high",
        "growth_speed": "medium",
        "content_sources": ["original explainers", "reaction to news", "tips threads"],
    },
    "food_recipes": {
        "description": "Recipe videos, restaurant reviews, cooking hacks",
        "monetization": ["affiliate (kitchen gear)", "brand deals (food brands)", "cookbook"],
        "avg_cpm_usd": 5.00,
        "competition": "very_high",
        "growth_speed": "fast",
        "content_sources": ["original recipe videos", "repost with credit", "compilations"],
    },
    "pet_content": {
        "description": "Cute animals, training tips, pet product reviews",
        "monetization": ["affiliate (pet food, toys)", "brand deals", "merch"],
        "avg_cpm_usd": 4.00,
        "competition": "medium",
        "growth_speed": "fast",
        "content_sources": ["repost with credit", "original clips", "UGC"],
    },
    "travel_inspo": {
        "description": "Destinations, travel tips, budget travel, vlogs",
        "monetization": ["affiliate (hotels, gear, insurance)", "brand deals", "presets"],
        "avg_cpm_usd": 6.50,
        "competition": "high",
        "growth_speed": "medium",
        "content_sources": ["repost with credit", "original travel clips", "guides"],
    },
    "beauty_fashion": {
        "description": "Makeup tutorials, OOTD, skincare, hauls",
        "monetization": ["affiliate (LTK, Amazon)", "brand deals", "own brand"],
        "avg_cpm_usd": 6.00,
        "competition": "very_high",
        "growth_speed": "fast",
        "content_sources": ["original GRWM", "hauls", "tutorials", "repost with credit"],
    },
    "tech_gadgets": {
        "description": "Product reviews, tech news, unboxings",
        "monetization": ["affiliate (Amazon, Best Buy)", "brand deals", "YouTube AdSense"],
        "avg_cpm_usd": 9.00,
        "competition": "medium",
        "growth_speed": "medium",
        "content_sources": ["original reviews", "unboxings", "reaction to reveals"],
    },
    "meme_humor": {
        "description": "Memes, relatable comedy, reaction content",
        "monetization": ["merch", "brand deals (entertainment)", "community"],
        "avg_cpm_usd": 2.50,
        "competition": "very_high",
        "growth_speed": "very_fast",
        "content_sources": ["curated memes", "original skits", "reaction videos"],
    },
}

CONTENT_FORMATS = {
    "trending_audio_clip": {"avg_views_multiplier": 2.5, "effort": "low", "virality": "high"},
    "educational_tips": {"avg_views_multiplier": 1.8, "effort": "medium", "virality": "medium"},
    "before_after": {"avg_views_multiplier": 3.0, "effort": "medium", "virality": "very_high"},
    "storytime": {"avg_views_multiplier": 2.0, "effort": "high", "virality": "medium"},
    "duet_stitch": {"avg_views_multiplier": 2.2, "effort": "low", "virality": "high"},
    "pov_scenario": {"avg_views_multiplier": 2.8, "effort": "medium", "virality": "high"},
    "listicle": {"avg_views_multiplier": 1.6, "effort": "medium", "virality": "medium"},
    "reaction": {"avg_views_multiplier": 1.9, "effort": "low", "virality": "medium"},
    "tutorial": {"avg_views_multiplier": 1.7, "effort": "high", "virality": "low"},
    "trending_challenge": {"avg_views_multiplier": 3.5, "effort": "low", "virality": "very_high"},
}

MONETIZATION_STAGES = {
    0: {"followers_needed": 0, "strategies": ["build audience", "establish niche authority"]},
    1000: {"followers_needed": 1_000, "strategies": ["affiliate links in bio", "start email list"]},
    5000: {"followers_needed": 5_000, "strategies": [
        "TikTok Creator Marketplace eligibility",
        "paid shoutouts to similar accounts",
        "digital product (ebook, template)",
    ]},
    10000: {"followers_needed": 10_000, "strategies": [
        "Instagram Creator Marketplace",
        "brand deal outreach (micro-deal $50-500/post)",
        "coaching/consulting 1:1",
    ]},
    50000: {"followers_needed": 50_000, "strategies": [
        "agency-represented brand deals",
        "YouTube Shorts monetization eligibility",
        "online course launch",
    ]},
    100000: {"followers_needed": 100_000, "strategies": [
        "TikTok Series (paid content)",
        "community subscription (Discord, Patreon)",
        "product line / merch drop",
    ]},
    500000: {"followers_needed": 500_000, "strategies": [
        "YouTube AdSense ($5-12 CPM)",
        "speaking engagements",
        "own brand/product line",
    ]},
}

CONVERSION_FUNNEL = {
    "tiktok_to_link": {
        "steps": [
            "CTA in final 3s: 'Link in bio for [specific value]'",
            "Pin comment with link context",
            "Bio: single clear CTA + link (use Linktree/Beacons)",
        ],
        "avg_ctr_from_video": 0.02,
    },
    "instagram_to_link": {
        "steps": [
            "Caption CTA: 'Link in bio'",
            "Story with link sticker (swipe up)",
            "Highlights: 'Resources' or 'Links' folder",
            "DM automation: comment trigger → auto-DM with link",
        ],
        "avg_ctr_from_video": 0.035,
    },
    "dm_funnel": {
        "steps": [
            "Caption: 'Comment WORD below and I'll DM you [resource]'",
            "Set up ManyChat/Manychat-style automation",
            "DM sequence: resource → nurture → offer",
            "Response rate: 40-60% typical for comment trigger DMs",
        ],
    },
}


def theme_page_blueprint(
    niche: str,
    platform: str = "tiktok",
    target_followers: int = 100_000,
    current_followers: int = 0,
    monetization_goal: str = "affiliate",
    trending_hashtags: list[str] | None = None,
    trending_sounds: list[dict] | None = None,
) -> dict:
    """Generate a complete theme page growth and monetization blueprint.

    Args:
        niche: Niche key from THEME_NICHES or custom niche description.
        platform: Primary platform ('tiktok', 'instagram', 'youtube_shorts').
        target_followers: Follower target.
        current_followers: Current follower count.
        monetization_goal: Primary monetization ('affiliate', 'course', 'brand_deals', 'product').
        trending_hashtags: From trend scraper to include in content calendar.
        trending_sounds: From TikTok scraper for audio recommendations.

    Returns:
        Full blueprint with content calendar, monetization roadmap, and conversion strategy.
    """
    niche_data = THEME_NICHES.get(niche, {
        "description": niche,
        "monetization": [monetization_goal],
        "avg_cpm_usd": 5.0,
        "competition": "unknown",
        "growth_speed": "medium",
        "content_sources": ["original content", "curated content with credit"],
    })

    # Content calendar (30 days)
    calendar = _generate_content_calendar(
        niche=niche,
        platform=platform,
        niche_data=niche_data,
        trending_hashtags=trending_hashtags or [],
        trending_sounds=trending_sounds or [],
    )

    # Monetization roadmap
    monetization_roadmap = _build_monetization_roadmap(
        current_followers=current_followers,
        target_followers=target_followers,
        niche_data=niche_data,
        goal=monetization_goal,
    )

    # Revenue projection
    revenue_projection = _project_revenue(
        followers=target_followers,
        niche_data=niche_data,
        goal=monetization_goal,
    )

    # Conversion strategy
    conversion = CONVERSION_FUNNEL.get(f"{platform}_to_link", CONVERSION_FUNNEL["tiktok_to_link"])

    # Content source strategy
    content_source_guide = _build_content_source_guide(niche_data)

    return {
        "niche": niche,
        "niche_description": niche_data["description"],
        "platform": platform,
        "competition_level": niche_data.get("competition", "unknown"),
        "growth_speed": niche_data.get("growth_speed", "medium"),
        "current_followers": current_followers,
        "target_followers": target_followers,
        "estimated_weeks_to_target": _estimate_weeks(current_followers, target_followers, niche_data),
        "monetization_goal": monetization_goal,
        "avg_cpm_usd": niche_data.get("avg_cpm_usd", 5.0),
        "revenue_projection": revenue_projection,
        "monetization_roadmap": monetization_roadmap,
        "content_calendar_30_days": calendar,
        "conversion_strategy": conversion,
        "content_source_guide": content_source_guide,
        "trending_hashtags_to_use": (trending_hashtags or [])[:10],
        "trending_sounds_to_use": [
            {"title": s.get("title", ""), "artist": s.get("artist", ""), "usage": s.get("usage_count", 0)}
            for s in (trending_sounds or [])[:5]
        ],
        "dm_funnel": CONVERSION_FUNNEL["dm_funnel"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def list_niches(sort_by: str = "avg_cpm_usd") -> list[dict]:
    """List all available theme page niches with key metrics.

    Args:
        sort_by: Sort field ('avg_cpm_usd', 'competition', 'growth_speed').
    """
    niches = []
    for key, data in THEME_NICHES.items():
        niches.append({
            "niche": key,
            "description": data["description"],
            "competition": data["competition"],
            "growth_speed": data["growth_speed"],
            "avg_cpm_usd": data["avg_cpm_usd"],
            "primary_monetization": data["monetization"][0] if data["monetization"] else "",
        })

    if sort_by == "avg_cpm_usd":
        niches.sort(key=lambda x: x["avg_cpm_usd"], reverse=True)
    elif sort_by == "competition":
        order = {"low": 0, "medium": 1, "high": 2, "very_high": 3}
        niches.sort(key=lambda x: order.get(x["competition"], 2))

    return niches


def content_formats_guide() -> list[dict]:
    """Return all content formats ranked by virality potential."""
    formats = []
    for name, data in CONTENT_FORMATS.items():
        formats.append({"format": name, **data})
    virality_order = {"very_high": 0, "high": 1, "medium": 2, "low": 3}
    formats.sort(key=lambda x: virality_order.get(x["virality"], 2))
    return formats


# ── Internal helpers ──────────────────────────────────────────────────

def _generate_content_calendar(
    niche: str,
    platform: str,
    niche_data: dict,
    trending_hashtags: list[str],
    trending_sounds: list[dict],
) -> list[dict]:
    """Build a 30-day content calendar with specific post ideas."""
    calendar = []
    start = date.today()

    # Rotate through high-virality formats
    high_virality = ["trending_challenge", "before_after", "pov_scenario", "trending_audio_clip", "duet_stitch"]
    medium_virality = ["educational_tips", "storytime", "reaction", "listicle"]
    all_formats = high_virality + medium_virality

    # Hashtag rotation
    ht_pool = trending_hashtags[:10] if trending_hashtags else []
    sound_pool = trending_sounds[:5] if trending_sounds else []

    for day in range(30):
        current_date = start + timedelta(days=day)
        day_of_week = current_date.strftime("%A")

        # Skip some days to maintain 4-5x/week pace
        if day_of_week in ("Tuesday", "Thursday") and day > 7:
            continue

        fmt = all_formats[day % len(all_formats)]
        fmt_data = CONTENT_FORMATS[fmt]

        # Pick a hashtag set for this post
        if ht_pool:
            ht_slice = ht_pool[day % max(1, len(ht_pool)):day % max(1, len(ht_pool)) + 3]
            if not ht_slice:
                ht_slice = ht_pool[:3]
            hashtags = [f"#{h}" for h in ht_slice] + [f"#{niche.replace('_', '')}"]
        else:
            hashtags = [f"#{niche.replace('_', '')}"]

        # Sound suggestion
        sound = None
        if sound_pool and platform in ("tiktok", "instagram"):
            sound = sound_pool[day % len(sound_pool)]

        calendar.append({
            "day": day + 1,
            "date": str(current_date),
            "day_of_week": day_of_week,
            "format": fmt,
            "virality_potential": fmt_data["virality"],
            "effort": fmt_data["effort"],
            "content_idea": _generate_idea(niche, fmt, niche_data),
            "hashtags": hashtags[:5],
            "trending_sound": (
                f"{sound['title']} — {sound['artist']}" if sound else None
            ),
            "platform": platform,
            "cta": _pick_cta(day),
        })

    return calendar


def _generate_idea(niche: str, fmt: str, niche_data: dict) -> str:
    """Generate a specific content idea for niche + format combination."""
    ideas = {
        ("fitness_motivation", "before_after"): "30-day transformation reveal with day-by-day breakdown",
        ("fitness_motivation", "trending_audio_clip"): "Gym montage synced to trending sound",
        ("fitness_motivation", "educational_tips"): "3 mistakes beginners make that kill gains",
        ("luxury_lifestyle", "pov_scenario"): "POV: You're test-driving a $200k car",
        ("luxury_lifestyle", "before_after"): "Budget hotel vs $5k/night suite reveal",
        ("mindset_quotes", "trending_audio_clip"): "Animated quote card synced to speech audio",
        ("finance_education", "educational_tips"): "5 things rich people do that you don't",
        ("finance_education", "storytime"): "How I went from broke to $X in 12 months",
        ("food_recipes", "tutorial"): "5-ingredient viral recipe in 60 seconds",
        ("food_recipes", "before_after"): "Worst vs best version of [dish]",
        ("meme_humor", "reaction"): "React to most relatable meme of the week",
        ("tech_gadgets", "before_after"): "Before/after switching to [product]",
    }

    key = (niche, fmt)
    if key in ideas:
        return ideas[key]

    # Generic fallback by format
    generic = {
        "trending_audio_clip": f"Trending audio applied to {niche_data.get('description', niche)} content",
        "before_after": f"Transformation/contrast reveal relevant to {niche}",
        "educational_tips": f"Top 3-5 tips about {niche} most people don't know",
        "storytime": f"Personal story related to {niche} with a lesson",
        "pov_scenario": f"POV: You're experiencing peak {niche} moment",
        "listicle": f"Ranking the best [items] in {niche} from worst to best",
        "reaction": f"Reacting to viral {niche} content with commentary",
        "tutorial": f"Step-by-step {niche} tutorial for beginners",
        "duet_stitch": f"Stitch/duet popular {niche} video with your take",
        "trending_challenge": f"Trending challenge adapted to {niche} theme",
    }
    return generic.get(fmt, f"Content about {niche}")


def _pick_cta(day: int) -> str:
    ctas = [
        "Follow for more [niche] content",
        "Comment your biggest [niche] struggle below",
        "Save this for later",
        "Share this with someone who needs it",
        "Link in bio for the full guide",
        "What would you add? Comment below",
        "Tag a friend who needs to see this",
        "Drop a [emoji] if this helped you",
    ]
    return ctas[day % len(ctas)]


def _build_monetization_roadmap(
    current_followers: int,
    target_followers: int,
    niche_data: dict,
    goal: str,
) -> list[dict]:
    """Build a stage-by-stage monetization roadmap."""
    roadmap = []
    thresholds = sorted(MONETIZATION_STAGES.keys())
    for threshold in thresholds:
        if threshold > target_followers and threshold > current_followers:
            break
        stage_data = MONETIZATION_STAGES[threshold]
        roadmap.append({
            "milestone_followers": threshold if threshold > 0 else "start",
            "unlocks": stage_data["strategies"],
            "reached": current_followers >= threshold,
        })

    # Add niche-specific monetization
    roadmap.append({
        "milestone_followers": "niche_specific",
        "unlocks": niche_data.get("monetization", [goal]),
        "reached": False,
        "note": "Niche-specific opportunities (start when audience trusts you)",
    })
    return roadmap


def _project_revenue(
    followers: int,
    niche_data: dict,
    goal: str,
) -> dict:
    """Simple revenue projection at target follower count."""
    cpm = niche_data.get("avg_cpm_usd", 5.0)

    # Assume 10% of followers see each video, 1 video/day
    avg_daily_views = followers * 0.10
    monthly_views = avg_daily_views * 30

    adsense_monthly = (monthly_views / 1000) * cpm

    # Affiliate estimate: 2% CTR, 3% conversion, $30 avg commission
    affiliate_monthly = monthly_views * 0.02 * 0.03 * 30

    # Brand deal estimate: 1 deal/month at $50 per 10k followers
    brand_deal_monthly = (followers / 10_000) * 50

    return {
        "at_followers": followers,
        "assumptions": {
            "reach_rate": "10% of followers per video",
            "videos_per_month": 20,
            "avg_cpm_usd": cpm,
        },
        "youtube_adsense_monthly_usd": round(adsense_monthly, 0),
        "affiliate_monthly_usd": round(affiliate_monthly, 0),
        "brand_deal_monthly_usd": round(brand_deal_monthly, 0),
        "total_monthly_usd": round(adsense_monthly + affiliate_monthly + brand_deal_monthly, 0),
        "note": "Estimates only — actual revenue varies significantly",
    }


def _build_content_source_guide(niche_data: dict) -> list[dict]:
    """Generate guidance on content sourcing."""
    sources = niche_data.get("content_sources", ["original content"])
    guide = []
    source_tips = {
        "repost with credit": (
            "Always credit original creator in caption (@username). "
            "DM for permission first when possible. "
            "Add your own commentary or caption to add value."
        ),
        "original content": (
            "Batch-record weekly (2-4h session = 7+ videos). "
            "Use natural light + decent mic — quality matters for retention. "
            "Film in vertical 9:16 at 1080p minimum."
        ),
        "compilations": (
            "Use royalty-free clips or credit all sources. "
            "Add voiceover commentary for differentiation. "
            "Keep clips short — 2-5 seconds each with fast cuts."
        ),
        "quote graphics (Canva)": (
            "Use Canva for fast design. "
            "Use trending audio under quote reveal for algorithm boost. "
            "Animate text appearance for higher watch time."
        ),
        "original recipe videos": (
            "Film overhead AND eye-level angles. "
            "Fast-cut cooking process with text overlays. "
            "Always show final result first (hook) then process."
        ),
        "UGC": (
            "Ask followers to tag you in their content. "
            "Repost with credit — this also builds community. "
            "DM top fans for collaboration."
        ),
    }
    for src in sources:
        guide.append({
            "source": src,
            "tips": source_tips.get(src, f"Source content ethically with proper attribution for: {src}"),
        })
    return guide


def _estimate_weeks(current: int, target: int, niche_data: dict) -> str:
    """Rough estimate of weeks to hit target at typical growth rate."""
    speed_weekly_pct = {
        "very_fast": 0.30,
        "fast": 0.20,
        "medium": 0.10,
        "slow": 0.05,
    }
    pct = speed_weekly_pct.get(niche_data.get("growth_speed", "medium"), 0.10)

    gap = max(0, target - current)
    if current <= 0:
        current = 1

    weeks = 0
    count = current
    while count < target and weeks < 520:
        count += max(50, count * pct)
        weeks += 1

    if weeks >= 520:
        return "10+ years at current growth estimates"
    if weeks > 52:
        return f"~{weeks // 52} years ({weeks} weeks)"
    return f"~{weeks} weeks"
