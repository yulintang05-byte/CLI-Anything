"""Theme / niche page conversion playbook.

A theme page (also called niche page) curates content around a single
topic — finance, motivation, pets, aesthetic, etc. — without the creator
being on camera.

This module provides:
- Full niche guide (branding, content, monetization)
- Conversion-optimised page strategy
- Content calendar generator
- Monetization path analysis
- Bio + handle templates
"""

from __future__ import annotations

import math
from datetime import date, timedelta
from typing import Optional

from .trends import NICHE_KEYWORDS, get_hashtag_suggestions

# ── Niche data ────────────────────────────────────────────────────────

NICHE_DATA: dict[str, dict] = {
    "finance": {
        "description": "Money tips, investing, budgeting, wealth building",
        "monetization": ["affiliate (budgeting apps, brokerages)", "digital products (courses, templates)", "sponsorships (fintech)", "AdSense"],
        "viral_formats": ["'I saved $X in Y days'", "myth busting (5 money lies)", "before/after wealth journey", "simple explainers"],
        "repurpose_sources": ["Reddit r/personalfinance (text posts)", "public SEC filings", "news articles (summarise)"],
        "difficulty": "medium",
        "monetization_speed": "fast",
        "avg_cpm": "$8–$15",
        "content_pillars": ["Money tips", "Investing basics", "Budget hacks", "Success stories"],
        "handle_examples": ["wealthbuilder", "moneymoves", "investsmart", "cashflow.page"],
        "tone": "authoritative but accessible",
        "format_mix": {"short_form": 70, "long_form": 30},
    },
    "motivation": {
        "description": "Quotes, mindset, success stories, productivity",
        "monetization": ["affiliate (books, courses, Audible)", "digital products (planners, journals)", "sponsorships", "merchandise"],
        "viral_formats": ["quote over aesthetic video", "story: 'I failed for X years then...'", "top 5 habits of successful people"],
        "repurpose_sources": ["Books (public domain)", "Podcasts (summarise)", "Reddit AMA posts"],
        "difficulty": "easy",
        "monetization_speed": "medium",
        "avg_cpm": "$3–$6",
        "content_pillars": ["Daily quotes", "Mindset tips", "Success stories", "Productivity hacks"],
        "handle_examples": ["dailydrive", "riseandgrind", "mindsetshift", "levelup.page"],
        "tone": "inspirational, punchy",
        "format_mix": {"short_form": 85, "long_form": 15},
    },
    "fitness": {
        "description": "Workouts, nutrition, transformation, health tips",
        "monetization": ["affiliate (supplements, gear)", "coaching programs", "digital products (meal plans)", "sponsorships"],
        "viral_formats": ["transformation reveal", "30-day challenge results", "'Do this every morning'", "gym mistakes to avoid"],
        "repurpose_sources": ["PubMed abstracts (simplify)", "fitness YouTube channels (inspiration, not copy)", "Reddit r/fitness"],
        "difficulty": "medium",
        "monetization_speed": "fast",
        "avg_cpm": "$5–$10",
        "content_pillars": ["Workout routines", "Nutrition tips", "Transformations", "Motivation"],
        "handle_examples": ["fitdaily", "gainzone", "sweatlife", "bodybuild.page"],
        "tone": "energetic, direct",
        "format_mix": {"short_form": 75, "long_form": 25},
    },
    "beauty": {
        "description": "Makeup, skincare, haircare, beauty hacks",
        "monetization": ["affiliate (Sephora, Amazon beauty)", "brand sponsorships", "digital (guides)", "LTK/ShopMy"],
        "viral_formats": ["product dupe reveals", "under $20 routine", "hack you didn't know", "before/after routine results"],
        "repurpose_sources": ["Reddit r/SkincareAddiction", "beauty YouTubers (inspiration)", "brand press releases"],
        "difficulty": "medium",
        "monetization_speed": "fast",
        "avg_cpm": "$4–$8",
        "content_pillars": ["Product reviews", "Tutorials", "Skincare routines", "Budget finds"],
        "handle_examples": ["beautypage", "glowguide", "skinscoop", "glamcurate"],
        "tone": "friendly, aspirational",
        "format_mix": {"short_form": 80, "long_form": 20},
    },
    "pets": {
        "description": "Dogs, cats, cute animals, pet care tips",
        "monetization": ["affiliate (Chewy, pet products)", "merchandise", "sponsorships", "digital (training guides)"],
        "viral_formats": ["puppy/kitten first day home", "dog does something funny", "pet meets baby", "before/after rescue"],
        "repurpose_sources": ["Reddit r/aww", "public domain pet footage", "animal shelters (UGC)"],
        "difficulty": "easy",
        "monetization_speed": "slow",
        "avg_cpm": "$2–$4",
        "content_pillars": ["Cute moments", "Training tips", "Care advice", "Rescue stories"],
        "handle_examples": ["pawspage", "fluffydaily", "petlovers", "animalvibes"],
        "tone": "warm, playful",
        "format_mix": {"short_form": 90, "long_form": 10},
    },
    "food": {
        "description": "Recipes, cooking hacks, restaurant reviews, food culture",
        "monetization": ["affiliate (kitchen gear, meal kits)", "sponsorships", "digital (recipe books)", "AdSense"],
        "viral_formats": ["5-ingredient recipe", "restaurant secret revealed", "cheap vs expensive ingredient", "satisfying food prep"],
        "repurpose_sources": ["Public domain cookbooks", "Reddit r/food", "restaurant menus"],
        "difficulty": "medium",
        "monetization_speed": "medium",
        "avg_cpm": "$3–$7",
        "content_pillars": ["Quick recipes", "Cooking hacks", "Restaurant intel", "Healthy eating"],
        "handle_examples": ["foodpage", "chefdigest", "eatgood", "tastecurate"],
        "tone": "appetising, approachable",
        "format_mix": {"short_form": 75, "long_form": 25},
    },
    "travel": {
        "description": "Destinations, hacks, budget travel, luxury escapes",
        "monetization": ["affiliate (Booking.com, Airbnb, credit cards)", "sponsorships", "digital (itineraries)", "AdSense"],
        "viral_formats": ["hidden gems in X city", "$50/day in [country]", "travel hack saves $X", "before/after itinerary"],
        "repurpose_sources": ["Public travel photography", "Reddit r/travel", "tourism board press releases"],
        "difficulty": "medium",
        "monetization_speed": "medium",
        "avg_cpm": "$6–$12",
        "content_pillars": ["Destinations", "Budget hacks", "Packing tips", "Itineraries"],
        "handle_examples": ["wanderpage", "traveldigest", "exploreworld", "roamguide"],
        "tone": "adventurous, wanderlust-inducing",
        "format_mix": {"short_form": 65, "long_form": 35},
    },
    "tech": {
        "description": "Gadgets, AI, software, coding, tech news",
        "monetization": ["affiliate (Amazon, tech stores)", "sponsorships (SaaS)", "digital (courses)", "AdSense"],
        "viral_formats": ["AI tool you didn't know", "5 apps that replace X", "honest review under 60s", "before/after AI workflow"],
        "repurpose_sources": ["Product Hunt launches", "Hacker News", "GitHub trending", "tech press releases"],
        "difficulty": "medium",
        "monetization_speed": "fast",
        "avg_cpm": "$8–$18",
        "content_pillars": ["Product reviews", "AI tips", "How-to guides", "Industry news"],
        "handle_examples": ["techbyte", "aidigest", "gadgetpage", "devdaily"],
        "tone": "sharp, informative",
        "format_mix": {"short_form": 70, "long_form": 30},
    },
}

# Content types that work well as theme pages (no face required)
FACELESS_CONTENT_TYPES = [
    "Screen recordings with voiceover",
    "Text-over-stock-video (B-roll)",
    "Image slideshows with background music",
    "Infographic animations",
    "Quote cards over aesthetic footage",
    "Compilation / curation with commentary captions",
    "AI voiceover over relevant footage",
    "Whiteboard / animated explainer style",
]

# Conversion funnel for theme pages
CONVERSION_FUNNEL = """
DISCOVERY (Trending hashtags → algorithm push)
         ↓
PROFILE VISIT (Optimised bio + pinned content → follow)
         ↓
FOLLOW (Consistent posting → engagement loop)
         ↓
TRUST (Value-add content, CTA in videos → link clicks)
         ↓
CONVERSION (Affiliate link / digital product / DM)
         ↓
RETENTION (Story/community content → loyal audience)
"""


def get_niche_guide(niche: str) -> dict:
    """Return the full playbook for building a converting theme page.

    Args:
        niche: Content niche (fitness, finance, beauty, etc.)

    Returns:
        Complete guide dict with strategy, content plan, monetization, etc.
    """
    niche = niche.lower().strip()
    data = NICHE_DATA.get(niche, _build_generic_niche(niche))

    hashtags = get_hashtag_suggestions(niche, "tiktok", count=20)

    return {
        "niche": niche,
        "description": data["description"],
        "difficulty": data.get("difficulty", "medium"),
        "monetization_speed": data.get("monetization_speed", "medium"),
        "avg_cpm": data.get("avg_cpm", "$3–$8"),
        "content_pillars": data["content_pillars"],
        "viral_formats": data["viral_formats"],
        "monetization_paths": data["monetization"],
        "repurpose_sources": data["repurpose_sources"],
        "handle_ideas": data["handle_examples"],
        "tone": data["tone"],
        "format_mix_pct": data["format_mix"],
        "hashtags": hashtags,
        "faceless_formats": FACELESS_CONTENT_TYPES[:5],
        "posting_frequency": {
            "tiktok": "1-3x / day",
            "youtube_shorts": "1x / day",
            "youtube_long": "2-3x / week",
        },
        "conversion_funnel": CONVERSION_FUNNEL.strip(),
        "quick_start_steps": _get_quick_start(niche, data),
    }


def get_conversion_guide() -> dict:
    """Return the master theme page conversion guide.

    Covers the complete lifecycle from zero to monetising a theme page.
    """
    return {
        "title": "Theme Page Conversion Masterclass",
        "phases": [
            {
                "phase": 1,
                "name": "Foundation (Week 1-2)",
                "tasks": [
                    "Choose ONE niche — the more specific the better (e.g., 'budget travel Europe' vs 'travel').",
                    "Research: spend 3 days consuming top content in your niche on TikTok + YouTube.",
                    "Choose a handle: short, memorable, niche-relevant (e.g., @wealthmoves, @fitmiracle).",
                    "Set up accounts: TikTok, YouTube Shorts, optionally Instagram Reels.",
                    "Create 10-15 pieces of content BEFORE posting — so you have a buffer.",
                    "Optimise bio: niche keyword + value prop + CTA (link in bio / DM me).",
                    "Pin your 3 best videos when they get traction.",
                ],
            },
            {
                "phase": 2,
                "name": "Growth (Week 3-8)",
                "tasks": [
                    "Post consistently: 1-3x / day on TikTok, 1x / day on Shorts.",
                    "Use 3-5 hashtags per post: 1 broad (#fyp), 2 mid (#fitness), 2 niche (#homeworkout).",
                    "Hook in first 2 seconds: question, shocking stat, bold claim.",
                    "Use trending audio (check TikTok's trending sounds weekly).",
                    "Reply to every comment for the first 1 hour after posting.",
                    "Cross-post to YouTube Shorts and Instagram Reels (repurpose, don't re-record).",
                    "Study analytics weekly — double down on what works.",
                ],
            },
            {
                "phase": 3,
                "name": "Monetization (Month 2-3)",
                "tasks": [
                    "Join affiliate programs: Amazon Associates, ShareASale, Impact, or niche-specific.",
                    "Add link-in-bio tool (Linktree, Stan Store, Beacons) with affiliate links.",
                    "Create a free lead magnet (PDF guide, checklist) to build email list.",
                    "Pitch brands in your niche via email once you hit 10k followers.",
                    "YouTube: apply for YPP at 1k subs + 4k watch hours (or 10M Shorts views).",
                    "TikTok: apply for Creator Fund or TikTok Series at 10k followers.",
                    "Consider a $17-$27 digital product (template, mini-course, guide).",
                ],
            },
            {
                "phase": 4,
                "name": "Scale (Month 3+)",
                "tasks": [
                    "Hire a virtual assistant to repurpose your content across platforms.",
                    "Build a system: content batch → edit → schedule → engage.",
                    "A/B test hooks and thumbnails to improve CTR.",
                    "Expand to second niche page using the same playbook.",
                    "Launch a paid community (Patreon, Circle, Discord) for super-fans.",
                    "Build email list to 1k+ as algorithm-independent asset.",
                ],
            },
        ],
        "common_mistakes": [
            "Posting inconsistently — algorithm rewards consistency above all else.",
            "Copying instead of reinterpreting — stay inspired, add your spin.",
            "Ignoring analytics — data tells you what to double down on.",
            "Monetising too early — build trust first, sell second.",
            "Too many niches on one account — confuses the algorithm.",
            "Not hooking in the first 2 seconds — viewers scroll instantly.",
        ],
        "tools_needed": [
            "CapCut or VN (free video editor with trending templates)",
            "Canva (thumbnails, graphics, quote cards)",
            "yt-dlp (download your own uploaded videos for repurposing)",
            "Linktree or Stan Store (link-in-bio)",
            "Later or Buffer (scheduling)",
            "Google Sheets (content calendar)",
        ],
    }


def get_monetization_strategies(niche: str) -> list[dict]:
    """Return ranked monetization strategies for a niche.

    Args:
        niche: Content niche.

    Returns:
        List of monetization dicts sorted by income potential.
    """
    niche = niche.lower()
    data = NICHE_DATA.get(niche, _build_generic_niche(niche))
    strategies = []
    for i, path in enumerate(data["monetization"]):
        strategies.append({
            "rank": i + 1,
            "path": path,
            "difficulty": ["easy", "medium", "medium", "hard"][min(i, 3)],
            "time_to_first_dollar": ["2-4 weeks", "1-2 months", "2-4 months", "4-6 months"][min(i, 3)],
        })
    # Add universal strategies
    strategies.append({
        "rank": len(strategies) + 1,
        "path": "UGC creator (User Generated Content) for brands",
        "difficulty": "easy",
        "time_to_first_dollar": "1-2 months at 5k-10k followers",
    })
    strategies.append({
        "rank": len(strategies) + 1,
        "path": "Sell shoutouts / collab slots to smaller creators",
        "difficulty": "easy",
        "time_to_first_dollar": "2-3 months at 20k+ followers",
    })
    return strategies


def generate_content_calendar(
    niche: str,
    platform: str = "tiktok",
    start_date: Optional[date] = None,
    days: int = 30,
    posts_per_day: int = 1,
) -> list[dict]:
    """Generate a content calendar for a theme page.

    Args:
        niche: Content niche.
        platform: 'tiktok' or 'youtube'.
        start_date: First date (defaults to today).
        days: Number of days to plan.
        posts_per_day: Daily post count.

    Returns:
        List of calendar entry dicts.
    """
    niche = niche.lower()
    data = NICHE_DATA.get(niche, _build_generic_niche(niche))
    pillars = data["content_pillars"]
    formats = data["viral_formats"]

    hashtags = get_hashtag_suggestions(niche, platform, count=10)

    if start_date is None:
        start_date = date.today()

    calendar: list[dict] = []
    pillar_idx = 0
    format_idx = 0

    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        day_name = current_date.strftime("%A")

        for post_num in range(posts_per_day):
            pillar = pillars[pillar_idx % len(pillars)]
            fmt = formats[format_idx % len(formats)]
            pillar_idx += 1
            format_idx += 1

            # Vary hashtag sets slightly per post
            tag_offset = (day_offset * posts_per_day + post_num) % 5
            post_tags = hashtags[:3] + hashtags[3 + tag_offset:3 + tag_offset + 5]

            calendar.append({
                "date": current_date.isoformat(),
                "day": day_name,
                "post_number": post_num + 1,
                "content_pillar": pillar,
                "format_idea": fmt,
                "hashtags": post_tags,
                "platform": platform,
                "status": "planned",
                "notes": "",
            })

    return calendar


# ── Helpers ───────────────────────────────────────────────────────────

def _get_quick_start(niche: str, data: dict) -> list[str]:
    return [
        f"1. Create @{data['handle_examples'][0]} style handle — short + niche-relevant.",
        f"2. Write bio: '{data['content_pillars'][0]} | {data['content_pillars'][1]} | {data['content_pillars'][2]}'.",
        f"3. First 3 videos: {' | '.join(data['viral_formats'][:3])}.",
        f"4. Post {data['format_mix']['short_form']}% short-form, {data['format_mix']['long_form']}% long-form.",
        f"5. Monetise first via: {data['monetization'][0]}.",
        f"6. Use these hashtags every post: {' '.join(get_hashtag_suggestions(niche, 'tiktok', 6))}.",
        "7. Reply to all comments within 1 hour of posting (huge algorithm signal).",
        "8. Batch-create 7 days of content at a time to stay ahead of schedule.",
    ]


def _build_generic_niche(niche: str) -> dict:
    keywords = NICHE_KEYWORDS.get(niche, [niche])
    return {
        "description": f"Content curated around {niche}",
        "monetization": [
            "affiliate marketing (niche-relevant products)",
            "brand sponsorships",
            "digital products (guides, templates)",
            "AdSense / creator fund",
        ],
        "viral_formats": [
            f"Top 5 {niche} tips",
            f"{niche} myth busting",
            f"Before/after {niche} transformation",
            "POV: [relatable scenario]",
        ],
        "repurpose_sources": [
            "Reddit communities",
            "News articles (summarise + add value)",
            "YouTube (inspiration, not copying)",
        ],
        "difficulty": "medium",
        "monetization_speed": "medium",
        "avg_cpm": "$3–$8",
        "content_pillars": [
            f"{niche.title()} tips",
            f"{niche.title()} news",
            f"Community highlights",
            f"Product/tool reviews",
        ],
        "handle_examples": [
            f"{niche}daily",
            f"{niche}page",
            f"{niche}hub",
            f"the{niche}life",
        ],
        "tone": "informative and engaging",
        "format_mix": {"short_form": 75, "long_form": 25},
    }


def list_niches() -> list[dict]:
    """Return all supported niches with key stats."""
    result = []
    for niche, data in NICHE_DATA.items():
        result.append({
            "niche": niche,
            "description": data["description"],
            "difficulty": data.get("difficulty"),
            "monetization_speed": data.get("monetization_speed"),
            "avg_cpm": data.get("avg_cpm"),
        })
    return result
