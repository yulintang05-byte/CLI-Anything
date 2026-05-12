"""Theme page strategy guide and automation helpers.

A "theme page" (also called a "niche page") is a social media account that
curates and repurposes viral content within a specific niche without necessarily
showing the creator's face. They are one of the fastest ways to grow a large
audience and monetize social media.

This module provides:
  - Niche scoring / selection
  - Content sourcing strategy
  - Repurposing workflows
  - Monetization roadmap
  - Growth milestones tracker
"""

from __future__ import annotations

from typing import Any


# ── Niche catalog ──────────────────────────────────────────────────────

NICHES: dict[str, dict[str, Any]] = {
    "luxury_lifestyle": {
        "name": "Luxury Lifestyle",
        "description": "Private jets, supercars, mansions, watches, designer goods",
        "avg_cpm": 8.50,
        "competition": "medium",
        "monetization_ease": "high",
        "top_platforms": ["instagram", "tiktok", "youtube"],
        "hashtags": ["luxury", "rich", "lifestyle", "wealth", "millionaire", "luxurylife"],
        "content_sources": ["Reddit r/luxury", "YouTube luxury channels", "Pinterest", "Billionaire news"],
        "avg_follower_growth": "500-2000/week at 10k followers",
        "notes": "CPM is high due to affluent audience. Affiliate for luxury products is lucrative.",
    },
    "motivation_quotes": {
        "name": "Motivation & Mindset",
        "description": "Inspirational quotes, success stories, self-improvement content",
        "avg_cpm": 4.00,
        "competition": "high",
        "monetization_ease": "medium",
        "top_platforms": ["instagram", "tiktok"],
        "hashtags": ["motivation", "mindset", "success", "grind", "hustle", "selfimprovement"],
        "content_sources": ["Goodreads quotes", "BrainyQuote", "Reddit r/GetMotivated"],
        "avg_follower_growth": "1000-3000/week at 10k followers",
        "notes": "High competition but enormous audience. Works well with Canva quote graphics.",
    },
    "fitness_wellness": {
        "name": "Fitness & Wellness",
        "description": "Workout clips, transformation stories, nutrition, mental health",
        "avg_cpm": 5.50,
        "competition": "high",
        "monetization_ease": "very high",
        "top_platforms": ["tiktok", "instagram", "youtube"],
        "hashtags": ["fitness", "workout", "gym", "transformation", "wellness", "health"],
        "content_sources": ["Fitness YouTube channels", "Reddit r/fitness", "Instagram fitness pages"],
        "avg_follower_growth": "800-2500/week at 10k followers",
        "notes": "Supplement affiliate programs pay 20-40% commission. Very monetizable.",
    },
    "funny_animals": {
        "name": "Funny Animals & Pets",
        "description": "Cute/funny pet videos, animal fails, wholesome moments",
        "avg_cpm": 3.00,
        "competition": "medium",
        "monetization_ease": "medium",
        "top_platforms": ["tiktok", "instagram", "youtube"],
        "hashtags": ["animals", "pets", "funny", "cute", "cats", "dogs", "fyp"],
        "content_sources": ["Reddit r/AnimalsBeingBros", "TikTok stitch", "YouTube compilations"],
        "avg_follower_growth": "2000-5000/week at 10k followers",
        "notes": "Viral potential is massive. Lower CPM but easier to grow.",
    },
    "tech_gadgets": {
        "name": "Tech & Gadgets",
        "description": "New product reveals, unboxings, reviews, tech life hacks",
        "avg_cpm": 9.00,
        "competition": "medium",
        "monetization_ease": "high",
        "top_platforms": ["youtube", "tiktok", "instagram"],
        "hashtags": ["tech", "gadgets", "apple", "android", "unboxing", "technews"],
        "content_sources": ["Product Hunt", "Tech YouTube channels", "Reddit r/gadgets"],
        "avg_follower_growth": "300-1500/week at 10k followers",
        "notes": "Highest CPM niches. Amazon Associates + tech affiliate = very profitable.",
    },
    "food_recipes": {
        "name": "Food & Recipes",
        "description": "Quick recipes, food hacks, restaurant reviews, ASMR cooking",
        "avg_cpm": 4.50,
        "competition": "high",
        "monetization_ease": "high",
        "top_platforms": ["tiktok", "instagram", "youtube", "pinterest"],
        "hashtags": ["food", "recipe", "cooking", "foodtok", "easyrecipes", "mealprep"],
        "content_sources": ["TikTok food creators", "YouTube recipes", "AllRecipes", "Food52"],
        "avg_follower_growth": "1500-4000/week at 10k followers",
        "notes": "Pinterest + food blog traffic can be enormous. Recipe ebook sales work well.",
    },
    "travel": {
        "name": "Travel & Adventure",
        "description": "Destination guides, hidden gems, travel hacks, drone footage",
        "avg_cpm": 6.00,
        "competition": "medium",
        "monetization_ease": "high",
        "top_platforms": ["instagram", "youtube", "tiktok"],
        "hashtags": ["travel", "wanderlust", "adventure", "explore", "travelgram", "traveltok"],
        "content_sources": ["Unsplash", "Travel YouTube", "Reddit r/travel", "TikTok travel"],
        "avg_follower_growth": "400-1500/week at 10k followers",
        "notes": "Hotel/airline affiliate pays well. Travel credit cards = high commissions.",
    },
    "finance_investing": {
        "name": "Finance & Investing",
        "description": "Stock market, crypto, passive income, financial freedom",
        "avg_cpm": 12.00,
        "competition": "medium",
        "monetization_ease": "very high",
        "top_platforms": ["youtube", "tiktok", "instagram"],
        "hashtags": ["finance", "investing", "stocks", "crypto", "passiveincome", "money"],
        "content_sources": ["CNBC", "WSJ", "Reddit r/investing", "Financial Twitter/X"],
        "avg_follower_growth": "300-1000/week at 10k followers",
        "notes": "Highest CPM niche on YouTube ($10-30 RPM). Brokerage affiliates pay $50-200 per signup.",
    },
    "gaming_clips": {
        "name": "Gaming Highlights",
        "description": "Funny fails, clutch plays, game trailers, gaming memes",
        "avg_cpm": 2.50,
        "competition": "very high",
        "monetization_ease": "medium",
        "top_platforms": ["youtube", "tiktok"],
        "hashtags": ["gaming", "gamer", "clips", "viral", "gamingmemes"],
        "content_sources": ["Twitch clips", "Reddit r/gaming", "Discord servers"],
        "avg_follower_growth": "500-3000/week at 10k followers",
        "notes": "Gaming merchandise + Twitch affiliate can supplement ad revenue.",
    },
    "aesthetic_photography": {
        "name": "Aesthetic / Photography",
        "description": "Minimalist aesthetics, nature photography, architecture, color themes",
        "avg_cpm": 3.50,
        "competition": "low",
        "monetization_ease": "medium",
        "top_platforms": ["instagram", "pinterest"],
        "hashtags": ["aesthetic", "photography", "minimal", "inspo", "vsco"],
        "content_sources": ["Unsplash", "Pinterest", "500px", "VSCO community"],
        "avg_follower_growth": "600-2000/week at 10k followers",
        "notes": "Preset sales and print-on-demand work extremely well here.",
    },
}


def list_niches(sort_by: str = "monetization_ease") -> list[dict[str, Any]]:
    """List all available niches sorted by a metric.

    Args:
        sort_by: "monetization_ease", "avg_cpm", or "competition".
    """
    order = {"very high": 4, "high": 3, "medium": 2, "low": 1, "very low": 0}
    niches = []
    for key, data in NICHES.items():
        niches.append({"key": key, **data})

    if sort_by == "avg_cpm":
        niches.sort(key=lambda n: n.get("avg_cpm", 0), reverse=True)
    elif sort_by == "competition":
        niches.sort(key=lambda n: order.get(n.get("competition", "medium"), 2))
    else:
        niches.sort(key=lambda n: order.get(n.get("monetization_ease", "medium"), 2), reverse=True)

    return niches


def get_niche(niche_key: str) -> dict[str, Any] | None:
    """Get full niche data by key."""
    return NICHES.get(niche_key)


def score_niche(niche_key: str) -> dict[str, Any]:
    """Generate a numerical score breakdown for a niche.

    Returns: total_score, monetization_score, growth_score, competition_score.
    """
    niche = NICHES.get(niche_key)
    if not niche:
        return {"error": f"Unknown niche: {niche_key}"}

    ease_map = {"very high": 5, "high": 4, "medium": 3, "low": 2, "very low": 1}
    comp_map = {"very high": 1, "high": 2, "medium": 3, "low": 4, "very low": 5}

    mon_score = ease_map.get(niche.get("monetization_ease", "medium"), 3) * 20
    cpm_score = min(niche.get("avg_cpm", 3) / 15 * 100, 100)
    comp_score = comp_map.get(niche.get("competition", "medium"), 3) * 20

    total = round((mon_score * 0.4 + cpm_score * 0.3 + comp_score * 0.3), 1)

    return {
        "niche": niche["name"],
        "total_score": total,
        "monetization_score": round(mon_score, 1),
        "cpm_score": round(cpm_score, 1),
        "competition_score": round(comp_score, 1),
        "recommendation": _niche_recommendation(total),
    }


def get_theme_page_guide(niche_key: str = "") -> dict[str, Any]:
    """Return the full theme page creation guide for a specific niche or general.

    Covers: setup, content strategy, growth, monetization milestones.
    """
    niche_data = NICHES.get(niche_key, {})
    niche_name = niche_data.get("name", "Your Niche")

    return {
        "title": f"Theme Page Creation Guide: {niche_name}",
        "overview": _overview(niche_name),
        "account_setup": _account_setup(niche_key, niche_data),
        "content_strategy": _content_strategy(niche_key, niche_data),
        "content_sourcing": _content_sourcing(niche_data),
        "growth_playbook": _growth_playbook(),
        "monetization_roadmap": _monetization_roadmap(niche_data),
        "milestones": _growth_milestones(),
        "common_mistakes": _common_mistakes(),
        "tools": _recommended_tools(),
    }


# ── Guide builders ─────────────────────────────────────────────────────

def _overview(niche_name: str) -> str:
    return (
        f"A {niche_name} theme page is a social media account that curates and "
        "repurposes the best viral content in the niche. You don't need to show "
        "your face, own original footage, or have special skills. The strategy is "
        "simple: find what's already working, put your spin on it, and post consistently."
    )


def _account_setup(niche_key: str, niche_data: dict[str, Any]) -> dict[str, Any]:
    platforms = niche_data.get("top_platforms", ["tiktok", "instagram"])
    hashtags = niche_data.get("hashtags", [])
    name = niche_data.get("name", "Niche")

    return {
        "steps": [
            "Choose a memorable, niche-specific username (e.g., @dailyluxury, @fitnation)",
            "Write a bio that states exactly what you post and why to follow",
            "Use a clean, on-brand profile picture (logo, niche image, or icon)",
            "Set your account to Creator/Business for analytics access",
            "Link a Linktree or link-in-bio page to all your platforms",
            "Create accounts on ALL top platforms simultaneously — repurpose one video everywhere",
        ],
        "username_formula": f"[niche_keyword] + [action/community word] (e.g., luxury.daily, fit.nation, wealth.moves)",
        "bio_template": f"✨ Best {name} content daily\n📲 New post every day\n👇 Follow for more {name.lower()}",
        "recommended_platforms": platforms,
        "starter_hashtags": hashtags[:8],
        "brand_colors": _niche_brand_colors(niche_key),
    }


def _content_strategy(niche_key: str, niche_data: dict[str, Any]) -> dict[str, Any]:
    return {
        "post_frequency": "1-3x per day on TikTok, 1x per day on Instagram Reels, 2-3x per week on YouTube",
        "content_mix": {
            "60%": "Curated/repurposed viral content (with credit)",
            "30%": "Original commentary or reaction on trends",
            "10%": "Personal/BTS to build authenticity",
        },
        "video_format": {
            "length": "7-15 seconds for hooks, 30-60 seconds for full videos",
            "aspect_ratio": "9:16 vertical for TikTok/Reels, 16:9 for YouTube",
            "resolution": "1080x1920px minimum",
            "captions": "Always add — 80% watch without sound",
        },
        "repurposing_workflow": [
            "Step 1: Find viral video in niche (TikTok, YouTube, Reddit)",
            "Step 2: Download with SnapTik / y2mate (ensure ToS compliance / get permission)",
            "Step 3: Add intro text, outro CTA, your watermark",
            "Step 4: Add trending sound from your platform's trending list",
            "Step 5: Write caption with hook + hashtags + CTA",
            "Step 6: Post on TikTok first, then cross-post to Reels/Shorts",
        ],
        "caption_formula": "[Hook/question] + [1-2 sentences of value] + [CTA] + [hashtags]",
        "hook_examples": [
            "Wait until the end...",
            "This is why most people fail at [niche]...",
            "Nobody talks about this but...",
            "POV: You just discovered [niche]...",
        ],
    }


def _content_sourcing(niche_data: dict[str, Any]) -> dict[str, Any]:
    sources = niche_data.get("content_sources", ["TikTok", "YouTube", "Reddit"])
    return {
        "primary_sources": sources,
        "discovery_tools": [
            "TikTok: Sort by 'Most Liked' in your niche hashtag — find viral videos",
            "YouTube: Sort search by 'View Count' + 'Last week' filter",
            "Reddit: Top posts this week in niche subreddits",
            "Pinterest: Trending pins in your niche category",
            "Google Trends: track what's spiking in search interest",
            "Exploding Topics (explodingtopics.com): rising trends before they peak",
        ],
        "important_note": (
            "Always credit original creators. Many successful theme pages "
            "DM creators for permission — this also builds relationships and can "
            "lead to collaboration opportunities."
        ),
        "curation_criteria": [
            "1M+ views on the original (proven viral content)",
            "Posted within the last 30 days (freshness matters)",
            "High comment engagement (controversy or emotion = shares)",
            "Visually captivating in the first 2 seconds",
            "Relevant to your specific niche angle",
        ],
    }


def _growth_playbook() -> list[dict[str, str]]:
    return [
        {
            "phase": "0-1K followers",
            "strategy": "Post 3x/day consistently. Follow-for-follow in niche. Comment on viral posts in your niche. Mass hashtag research.",
            "timeframe": "Week 1-4",
        },
        {
            "phase": "1K-10K followers",
            "strategy": "Identify your 2-3 best performing content formats. Double down on those. Do 5 shoutout exchanges per week. Optimize posting times with analytics.",
            "timeframe": "Month 1-3",
        },
        {
            "phase": "10K-100K followers",
            "strategy": "Launch first monetization (affiliate links, brand deals). Build email list. Create a 'hero' viral video with high production value. Go live 2x/week.",
            "timeframe": "Month 3-8",
        },
        {
            "phase": "100K+ followers",
            "strategy": "Premium brand deals. Launch own product (digital or physical). Build second niche page. Hire VA to help with content curation.",
            "timeframe": "Month 6-18",
        },
    ]


def _monetization_roadmap(niche_data: dict[str, Any]) -> list[dict[str, str]]:
    cpm = niche_data.get("avg_cpm", 4.0)
    return [
        {
            "milestone": "0-1,000 followers",
            "method": "Affiliate marketing (Amazon Associates, ClickBank, ShareASale)",
            "action": "Add affiliate link in bio. Mention products naturally in content.",
            "est_monthly": "$0-50",
        },
        {
            "milestone": "1,000-10,000 followers",
            "method": "Micro brand deals + affiliate",
            "action": "Pitch to small brands in your niche. Rate: $50-200/post.",
            "est_monthly": "$50-500",
        },
        {
            "milestone": "10,000-50,000 followers",
            "method": "Mid-tier brand deals + digital products",
            "action": "Launch an eBook, preset pack, or course. Rate: $200-1000/post.",
            "est_monthly": "$500-3000",
        },
        {
            "milestone": "50,000-100,000 followers",
            "method": "Premium sponsorships + YouTube AdSense",
            "action": f"YouTube CPM for {niche_data.get('name', 'your niche')}: ~${cpm:.2f}. Rate: $1000-5000/post.",
            "est_monthly": "$3000-10000",
        },
        {
            "milestone": "100,000+ followers",
            "method": "Agency rates + own product line",
            "action": "Build brand equity. Launch membership, merchandise, consulting.",
            "est_monthly": "$10,000+",
        },
    ]


def _growth_milestones() -> list[dict[str, str]]:
    return [
        {"milestone": "First 100 followers", "action": "Validate niche choice. Keep posting."},
        {"milestone": "First 1,000 followers", "action": "Add affiliate link in bio. Analyze top posts."},
        {"milestone": "First viral post (100K+ views)", "action": "Replicate that format every 2-3 posts."},
        {"milestone": "10,000 followers", "action": "Apply for creator monetization programs. Start brand deal outreach."},
        {"milestone": "First paid collaboration", "action": "Create media kit. Build rates card."},
        {"milestone": "50,000 followers", "action": "Consider hiring a VA. Launch your first product."},
        {"milestone": "100,000 followers", "action": "Reassess strategy. Expand to new platforms."},
        {"milestone": "1,000,000 followers", "action": "You're a brand. Licensing, speaking, enterprise deals."},
    ]


def _common_mistakes() -> list[str]:
    return [
        "Posting inconsistently — the algorithm punishes gaps. Post daily, no exceptions.",
        "Using too many hashtags — 3-5 targeted hashtags beat 30 random ones on TikTok.",
        "Ignoring the first 2 seconds — if the hook doesn't grab, nothing else matters.",
        "Not engaging in comments — the algorithm rewards accounts that create conversation.",
        "Copying exact content without adding value — add text, commentary, or editing.",
        "Giving up before 90 days — almost all theme pages grow slowly at first, then explode.",
        "Posting at wrong times — schedule posts during peak hours for your audience's timezone.",
        "Not repurposing cross-platform — one piece of content should be on 3+ platforms.",
        "Ignoring analytics — post more of what works, stop posting what doesn't.",
        "Trying to be everything — hyper-niche pages grow 3-5x faster than general ones.",
    ]


def _recommended_tools() -> dict[str, list[str]]:
    return {
        "content_creation": [
            "CapCut (free, mobile) — for quick video edits with auto-captions",
            "Canva (free/pro) — for graphics, quote cards, thumbnail design",
            "InShot (free) — mobile video editing for repurposing",
            "Adobe Express (free) — quick social media graphics",
        ],
        "scheduling_analytics": [
            "Later.com — visual content calendar + best time to post",
            "Buffer — cross-platform scheduling",
            "TikTok Analytics (built-in) — free, use after switching to creator account",
            "Instagram Insights (built-in) — track Reels performance",
        ],
        "content_discovery": [
            "Google Trends — free, see what's spiking",
            "Exploding Topics — find trends before they peak",
            "TrendTok Analytics — TikTok trend research",
            "Ahrefs Keyword Explorer (paid) — for YouTube SEO",
        ],
        "monetization": [
            "Linktree / Stan.store — link in bio hub",
            "Gumroad / Payhip — sell digital products",
            "Amazon Associates — affiliate for physical products",
            "AspireIQ / Grin — brand deal marketplace",
        ],
        "productivity": [
            "Notion — content calendar and idea bank",
            "Trello — content pipeline management",
            "Google Sheets — track metrics weekly",
        ],
    }


def _niche_recommendation(score: float) -> str:
    if score >= 75:
        return "Excellent choice — high revenue potential with manageable competition"
    if score >= 55:
        return "Good choice — solid opportunity, execute consistently"
    if score >= 40:
        return "Viable — will require more effort to stand out"
    return "Challenging — consider pivoting to a more lucrative niche"


def _niche_brand_colors(niche_key: str) -> dict[str, str]:
    color_map = {
        "luxury_lifestyle": {"primary": "#C9A84C", "secondary": "#1A1A1A", "accent": "#FFFFFF"},
        "motivation_quotes": {"primary": "#FF4500", "secondary": "#1A1A1A", "accent": "#FFD700"},
        "fitness_wellness": {"primary": "#00C851", "secondary": "#212121", "accent": "#FF6B6B"},
        "funny_animals": {"primary": "#FF9F43", "secondary": "#FFEAA7", "accent": "#6C5CE7"},
        "tech_gadgets": {"primary": "#0984E3", "secondary": "#2D3436", "accent": "#00CEC9"},
        "food_recipes": {"primary": "#E17055", "secondary": "#FDCB6E", "accent": "#FFFFFF"},
        "travel": {"primary": "#0652DD", "secondary": "#1289A7", "accent": "#C4E538"},
        "finance_investing": {"primary": "#00B894", "secondary": "#2D3436", "accent": "#FDCB6E"},
        "gaming_clips": {"primary": "#6C5CE7", "secondary": "#2D3436", "accent": "#FD79A8"},
        "aesthetic_photography": {"primary": "#B2BEC3", "secondary": "#FFFFFF", "accent": "#636E72"},
    }
    return color_map.get(niche_key, {"primary": "#333333", "secondary": "#FFFFFF", "accent": "#4ECDC4"})
