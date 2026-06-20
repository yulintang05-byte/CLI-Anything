"""Theme page creation, niche selection, and monetisation strategy."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


_NICHES = {
    "luxury_lifestyle": {
        "description": "Aspirational wealth — cars, watches, mansions, travel",
        "platforms": ["instagram", "tiktok"],
        "cpm_estimate": "$12-30",
        "best_monetisation": ["affiliate (luxury brands)", "shoutouts", "dropshipping"],
        "content_sources": ["Pinterest", "YouTube reposts", "stock footage"],
        "competition": "high",
        "conversion_rate_est": "2-5%",
    },
    "motivation_mindset": {
        "description": "Success quotes, entrepreneur stories, discipline content",
        "platforms": ["instagram", "tiktok", "youtube"],
        "cpm_estimate": "$8-18",
        "best_monetisation": ["digital products (courses/ebooks)", "affiliate (courses)", "community"],
        "content_sources": ["YouTube speeches", "book summaries", "quote carousels"],
        "competition": "very_high",
        "conversion_rate_est": "3-8%",
    },
    "fitness_gym": {
        "description": "Workout tips, body transformation, nutrition",
        "platforms": ["tiktok", "instagram", "youtube"],
        "cpm_estimate": "$10-25",
        "best_monetisation": ["supplement affiliate", "workout plans", "coaching"],
        "content_sources": ["gym footage", "transformation reposts", "tutorial clips"],
        "competition": "high",
        "conversion_rate_est": "4-9%",
    },
    "pets_animals": {
        "description": "Cute/funny pet videos — dogs, cats, exotic animals",
        "platforms": ["tiktok", "instagram", "youtube"],
        "cpm_estimate": "$5-12",
        "best_monetisation": ["pet product affiliate", "merchandise", "brand deals"],
        "content_sources": ["user-submitted clips", "Reddit r/aww", "stock footage"],
        "competition": "medium",
        "conversion_rate_est": "5-12%",
    },
    "tech_ai": {
        "description": "AI tools, gadgets, software tutorials, tech news",
        "platforms": ["youtube", "tiktok"],
        "cpm_estimate": "$15-40",
        "best_monetisation": ["SaaS affiliate (high CPA)", "sponsors", "newsletter"],
        "content_sources": ["product demos", "AI tool showcases", "news commentary"],
        "competition": "medium",
        "conversion_rate_est": "6-15%",
    },
    "food_recipes": {
        "description": "Quick recipes, food hacks, restaurant reviews, ASMR eating",
        "platforms": ["tiktok", "instagram", "youtube"],
        "cpm_estimate": "$6-14",
        "best_monetisation": ["kitchen affiliate", "recipe ebooks", "meal kit sponsor"],
        "content_sources": ["original cooking", "recipe cards", "food blogs"],
        "competition": "high",
        "conversion_rate_est": "3-7%",
    },
    "finance_money": {
        "description": "Investing, budgeting, side hustles, crypto",
        "platforms": ["youtube", "tiktok", "instagram"],
        "cpm_estimate": "$20-60",
        "best_monetisation": ["financial product affiliate", "courses", "newsletter sub"],
        "content_sources": ["news commentary", "explainer graphics", "interviews"],
        "competition": "high",
        "conversion_rate_est": "8-20%",
    },
    "relationship_dating": {
        "description": "Dating advice, red flags, relationship tips",
        "platforms": ["tiktok", "instagram"],
        "cpm_estimate": "$7-16",
        "best_monetisation": ["dating app affiliate", "ebooks", "coaching DMs"],
        "content_sources": ["POV skits", "Q&A responses", "comment reply videos"],
        "competition": "medium",
        "conversion_rate_est": "4-10%",
    },
    "diy_life_hacks": {
        "description": "Life hacks, home improvement, organisation tips",
        "platforms": ["tiktok", "instagram", "youtube"],
        "cpm_estimate": "$8-18",
        "best_monetisation": ["Amazon affiliate", "brand deals", "Etsy products"],
        "content_sources": ["original demos", "Pinterest ideas", "Reddit hacks"],
        "competition": "medium",
        "conversion_rate_est": "5-12%",
    },
    "gaming_esports": {
        "description": "Game highlights, tutorials, esports news",
        "platforms": ["youtube", "tiktok"],
        "cpm_estimate": "$5-15",
        "best_monetisation": ["gaming peripheral affiliate", "stream donations", "subs"],
        "content_sources": ["own gameplay", "clip compilations", "news"],
        "competition": "very_high",
        "conversion_rate_est": "3-8%",
    },
}

_CONVERSION_PLAYBOOK = [
    {
        "phase": "1 – Hook (0-3 s)",
        "goal": "Stop the scroll",
        "tactics": [
            "Lead with the payoff, not the setup ('Here's how I made $12k from this niche')",
            "Text hook on screen before any audio",
            "Pattern interrupt: unexpected visual or statement",
        ],
    },
    {
        "phase": "2 – Deliver Value (3-30 s)",
        "goal": "Build trust fast",
        "tactics": [
            "Give the most useful insight immediately — don't build suspense",
            "Show, don't tell: screen recordings, before/afters, demos outperform talking heads",
            "Use captions; 85% watch without sound",
        ],
    },
    {
        "phase": "3 – CTA (last 5 s)",
        "goal": "Convert viewer to follower / customer",
        "tactics": [
            "One CTA only: 'Follow for part 2' OR 'Link in bio for the free guide' — not both",
            "Use urgency if genuine ('dropping the full tutorial tomorrow')",
            "Comment baiting: 'Comment GUIDE and I'll DM you the link'",
        ],
    },
]

_MONETISATION_TIERS = [
    {
        "tier": "0-1k followers",
        "strategies": [
            "Start collecting emails from day 1 (free Beehiiv newsletter)",
            "Post affiliate links via link-in-bio (ClickBank, Amazon, ShareASale)",
            "Digital downloads on Gumroad — no follower minimum",
        ],
    },
    {
        "tier": "1k-10k followers",
        "strategies": [
            "TikTok Creator Marketplace (brand deals from 10k; direct outreach earlier)",
            "YouTube Partner Programme at 1k subs + 4k watch hours",
            "Paid shoutouts to smaller pages ($50-$500 per post)",
            "Affiliate: push 1-2 high-converting products with dedicated reviews",
        ],
    },
    {
        "tier": "10k-100k followers",
        "strategies": [
            "Brand sponsorships: $500-$5k per post in high-CPM niches",
            "Launch a low-ticket digital product ($9-$47) — email list converts best",
            "Community membership (Discord/Patreon) $10-$50/month",
            "UGC content creation (charge $200-$800 per video, no following required)",
        ],
    },
    {
        "tier": "100k+ followers",
        "strategies": [
            "Premium sponsorships ($5k-$50k per integration)",
            "High-ticket coaching / masterminds ($1k-$10k)",
            "Own product lines (merch, supplements, software, courses)",
            "Sell the page: theme pages at 100k+ sell for 12-36× monthly revenue",
        ],
    },
]


def get_niche_guide(niche: str = "") -> dict[str, Any]:
    if niche:
        key = niche.lower().replace(" ", "_").replace("-", "_")
        if key in _NICHES:
            return {"niche": key, **_NICHES[key], "generated_at": _now()}
        # fuzzy match
        for k in _NICHES:
            if niche.lower() in k or k in niche.lower():
                return {"niche": k, **_NICHES[k], "generated_at": _now()}
        return {
            "error": f"Niche '{niche}' not in database.",
            "available_niches": list(_NICHES.keys()),
        }
    return {
        "generated_at": _now(),
        "niches": _NICHES,
        "selection_criteria": (
            "Pick a niche where: (1) CPM > $10, (2) competition is medium or lower, "
            "(3) you can source/create content consistently, "
            "(4) at least one affiliate programme pays > 20% commission."
        ),
    }


def get_conversion_playbook() -> dict[str, Any]:
    return {
        "generated_at": _now(),
        "topic": "Converting Theme Page Content Framework",
        "phases": _CONVERSION_PLAYBOOK,
        "golden_rule": (
            "Every piece of content must do ONE of: grow following, "
            "capture email, or drive a sale. If it doesn't serve one of these, cut it."
        ),
        "ab_test_priority": [
            "Hook text (highest impact on view rate)",
            "Thumbnail / cover frame",
            "CTA wording",
            "Video length",
        ],
    }


def get_monetisation_roadmap() -> dict[str, Any]:
    return {
        "generated_at": _now(),
        "roadmap": _MONETISATION_TIERS,
        "fastest_path_to_revenue": (
            "1. Create content → 2. Put affiliate link in bio from day 1 → "
            "3. At 1k followers start charging for shoutouts → "
            "4. At 5k launch a $9 PDF / digital product → "
            "5. At 10k pitch brands directly. Don't wait for a platform to invite you."
        ),
        "page_valuation": (
            "Theme pages typically sell for 12-36× monthly net revenue on Flippa or "
            "via direct broker. A page making $2k/month can sell for $24k-$72k."
        ),
    }


def get_content_calendar(niche: str = "", platform: str = "tiktok") -> dict[str, Any]:
    """Generate a 7-day content calendar framework for a theme page."""
    schedule = {
        "Monday": "Educational / How-to (highest saves day of week)",
        "Tuesday": "Trend-hop: use this week's viral audio / hashtag challenge",
        "Wednesday": "Social proof / testimonials / transformation content",
        "Thursday": "Controversial opinion or POV (drives comments)",
        "Friday": "Entertainment / trending format (peak engagement day)",
        "Saturday": "Community content: Q&A, polls, comment-reply video",
        "Sunday": "Behind-the-scenes / personal story (builds parasocial connection)",
    }
    return {
        "generated_at": _now(),
        "platform": platform,
        "niche": niche or "general",
        "weekly_framework": schedule,
        "repurposing_tip": (
            "Film Monday's educational video → clip into 5×15 s TikToks → "
            "convert to carousel for Instagram → upload long cut to YouTube. "
            "One filming session = 7+ pieces of content."
        ),
    }


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
