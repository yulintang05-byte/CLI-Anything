#!/usr/bin/env python3
"""Theme page creation, conversion, and monetization guide."""

import time


_THEME_NICHES = {
    "luxury_lifestyle": {
        "description": "Luxury cars, watches, jets, mansions, aspirational content",
        "target_audience": "18-35 aspirational males",
        "content_sources": ["YouTube compilations", "Unsplash", "Reddit r/Justrolledintotheshop", "Reddit r/carporn"],
        "platforms": ["Instagram", "TikTok", "Pinterest"],
        "avg_monetization_start": "10k followers",
        "monetization": ["luxury brand deals", "affiliate (luxury watches, cars)", "digital guides"],
        "difficulty": "medium",
        "content_frequency": "3-5x/day",
        "notes": "No face required — pure repost/curation model. Add value with captions.",
    },
    "motivational_quotes": {
        "description": "Mindset quotes, hustle culture, success photos with text overlays",
        "target_audience": "18-40 entrepreneurs and goal-setters",
        "content_sources": ["BrainyQuote", "Goodreads", "AZ Quotes", "create in Canva"],
        "platforms": ["Instagram", "TikTok", "Pinterest", "Facebook"],
        "avg_monetization_start": "5k followers",
        "monetization": ["digital courses affiliate", "self-help books", "coaching program"],
        "difficulty": "easy",
        "content_frequency": "3-5x/day",
        "notes": "Highest competition niche — differentiate by sub-niche (e.g., female entrepreneurs only)",
    },
    "fitness_transformation": {
        "description": "Before/after transformations, workout clips, diet tips",
        "target_audience": "18-45 fitness aspirants",
        "content_sources": ["Reddit r/progresspics", "YouTube clips (with credit)", "original UGC"],
        "platforms": ["TikTok", "Instagram", "YouTube Shorts"],
        "avg_monetization_start": "15k followers",
        "monetization": ["supplement affiliate", "fitness app affiliate", "gym gear", "workout plans"],
        "difficulty": "medium",
        "content_frequency": "2-3x/day",
        "notes": "Always credit original creators — builds community goodwill and avoids DMCA.",
    },
    "pet_content": {
        "description": "Cute animal videos, pet tips, funny clips",
        "target_audience": "all demographics — pets are universal",
        "content_sources": ["Reddit r/aww", "YouTube compilations", "TikTok saves", "owner UGC submissions"],
        "platforms": ["TikTok", "Instagram", "YouTube", "Facebook"],
        "avg_monetization_start": "20k followers",
        "monetization": ["pet food affiliate", "pet store deals", "pet insurance affiliate"],
        "difficulty": "easy",
        "content_frequency": "2-4x/day",
        "notes": "High organic virality. Partner with pet owners for exclusive content submissions.",
    },
    "travel_destinations": {
        "description": "Stunning travel videos and photos from around the world",
        "target_audience": "25-45 travel dreamers",
        "content_sources": ["Unsplash", "Pexels", "YouTube travel vlogs (with permission)", "Reddit r/travel"],
        "platforms": ["Instagram", "Pinterest", "TikTok", "YouTube"],
        "avg_monetization_start": "25k followers",
        "monetization": ["booking affiliate", "hotel affiliate", "travel credit cards", "travel insurance"],
        "difficulty": "medium",
        "content_frequency": "2-3x/day",
        "notes": "Sub-niche by region (e.g., 'Hidden Europe') for faster growth.",
    },
    "finance_tips": {
        "description": "Money tips, investing basics, wealth mindset",
        "target_audience": "22-40 young professionals",
        "content_sources": ["original research", "news articles (summarized)", "infographic creation"],
        "platforms": ["TikTok", "Instagram", "YouTube", "Twitter/X"],
        "avg_monetization_start": "5k followers",
        "monetization": ["investment app affiliate", "fintech affiliate", "financial course affiliate"],
        "difficulty": "medium-hard",
        "content_frequency": "1-2x/day",
        "notes": "Highest CPM niche. Requires factual accuracy — verify all claims.",
    },
    "aesthetic_food": {
        "description": "Beautifully filmed recipe videos, restaurant content, food art",
        "target_audience": "18-40 food lovers",
        "content_sources": ["original filming", "food blogger YouTube", "TikTok saves"],
        "platforms": ["TikTok", "Instagram", "Pinterest", "YouTube"],
        "avg_monetization_start": "10k followers",
        "monetization": ["kitchen affiliate", "meal kit sponsors", "restaurant partnerships", "cookbook"],
        "difficulty": "medium",
        "content_frequency": "2-3x/day",
        "notes": "Good food lighting is 90% of success in this niche.",
    },
    "tech_reviews": {
        "description": "Gadget reviews, tech unboxings, app tips, productivity",
        "target_audience": "16-40 tech enthusiasts",
        "content_sources": ["original reviews", "YouTube clips (with permission)", "press releases"],
        "platforms": ["YouTube", "TikTok", "Instagram", "Twitter/X"],
        "avg_monetization_start": "5k subscribers",
        "monetization": ["Amazon affiliate", "tech brand sponsorships", "digital product affiliate"],
        "difficulty": "medium",
        "content_frequency": "3-5x/week",
        "notes": "Amazon affiliate links can monetize from day 1 with any traffic.",
    },
}


def list_niches() -> dict:
    """List all supported theme page niches with key metadata."""
    niches = []
    for key, data in _THEME_NICHES.items():
        niches.append({
            "niche": key,
            "description": data["description"],
            "difficulty": data["difficulty"],
            "platforms": data["platforms"],
            "monetization_start": data["avg_monetization_start"],
        })
    return {
        "total": len(niches),
        "niches": niches,
    }


def get_niche_guide(niche: str) -> dict:
    """Get full theme page guide for a specific niche."""
    profile = _THEME_NICHES.get(niche.lower().replace(" ", "_"))
    if not profile:
        # Try partial match
        for key, data in _THEME_NICHES.items():
            if niche.lower() in key:
                profile = data
                niche = key
                break

    if not profile:
        return {
            "error": f"Niche '{niche}' not found",
            "available_niches": list(_THEME_NICHES.keys()),
        }

    return {
        "niche": niche,
        "guide": profile,
        "setup_checklist": _setup_checklist(niche, profile),
        "30_day_plan": _thirty_day_plan(niche, profile),
        "content_templates": _content_templates(niche, profile),
        "conversion_strategy": _conversion_strategy(niche, profile),
    }


def _setup_checklist(niche: str, profile: dict) -> list[dict]:
    return [
        {
            "step": 1,
            "task": "Choose your primary platform",
            "detail": f"Best platforms for {niche}: {', '.join(profile['platforms'][:2])}",
            "time_required": "5 min",
        },
        {
            "step": 2,
            "task": "Create accounts with niche-clear username",
            "detail": "Format: [Niche][Keyword] e.g. @DailyLuxury, @FitBodyDaily",
            "time_required": "10 min",
        },
        {
            "step": 3,
            "task": "Write a 150-char bio with value prop + CTA",
            "detail": "Example: 'Daily [niche] inspiration for [audience] | Follow for [value]'",
            "time_required": "15 min",
        },
        {
            "step": 4,
            "task": "Create profile picture and banner",
            "detail": "Use Canva — clean, niche-matching aesthetic. Consistent color palette.",
            "time_required": "30 min",
        },
        {
            "step": 5,
            "task": "Set up content sourcing pipeline",
            "detail": f"Sources: {', '.join(profile['content_sources'][:3])}",
            "time_required": "1 hour",
        },
        {
            "step": 6,
            "task": "Create content templates in Canva",
            "detail": "Make 3-5 reusable templates: quote template, carousel template, video cover",
            "time_required": "2 hours",
        },
        {
            "step": 7,
            "task": "Batch create your first 7 days of content",
            "detail": f"Post {profile['content_frequency']} — that's ~21-35 pieces needed for week 1",
            "time_required": "4-6 hours",
        },
        {
            "step": 8,
            "task": "Set up scheduling tool",
            "detail": "Buffer (free), Later, or Meta Business Suite for Instagram/Facebook",
            "time_required": "30 min",
        },
        {
            "step": 9,
            "task": "Set up link-in-bio page",
            "detail": "Linktree or Beacons.ai — add affiliate links from day 1",
            "time_required": "20 min",
        },
        {
            "step": 10,
            "task": "Follow 50 accounts in your niche on day 1",
            "detail": "This signals your niche to the algorithm and gets initial visibility",
            "time_required": "20 min",
        },
    ]


def _thirty_day_plan(niche: str, profile: dict) -> list[dict]:
    return [
        {
            "days": "1-7",
            "goal": "Establish presence & posting routine",
            "kpi": "50+ followers, 3 posts/day minimum",
            "focus": [
                "Post consistently at peak hours",
                "Use trending hashtags for your niche",
                "Engage with 20 posts/day in your niche",
                "Study top 5 accounts in your niche — note what works",
            ],
        },
        {
            "days": "8-14",
            "goal": "Find your viral content style",
            "kpi": "1 post with 5x average views",
            "focus": [
                "Identify your best-performing post type — double down",
                "A/B test: different caption styles, posting times",
                "Begin DM strategy: reach out to 3 similar accounts for shoutout swaps",
                "Add your first affiliate link to bio",
            ],
        },
        {
            "days": "15-21",
            "goal": "Accelerate growth with trending content",
            "kpi": "500+ followers or 10k+ total views",
            "focus": [
                "Create content around trending sounds/hashtags",
                "Launch a giveaway (follow + share for entry) — use collab partner",
                "Create a 'value series' (e.g., 5-part series on the niche topic)",
                "Pin your best post to top of profile",
            ],
        },
        {
            "days": "22-30",
            "goal": "Monetization foundation",
            "kpi": "First affiliate click or brand inquiry",
            "focus": [
                "Apply to affiliate programs: " + ", ".join(profile["monetization"][:2]),
                "Create a UGC-style post (feels native, converts well for affiliate)",
                "Reach out to 5 small brands for gifted partnerships",
                "Start building email list (add Beacons/Linktree with email capture)",
            ],
        },
    ]


def _content_templates(niche: str, profile: dict) -> list[dict]:
    templates = [
        {
            "type": "Repost with Value Caption",
            "format": "[Source content] + 2-3 lines of insight/commentary",
            "caption_formula": "[Hook statement]. [Context/insight]. [CTA: Follow @account for daily [niche]]",
            "usage": "60% of content mix",
        },
        {
            "type": "Quote/Text Overlay",
            "format": "Static image or video with text overlay (use Canva)",
            "caption_formula": "[Extended thought on the quote]. [Ask a question to drive comments]",
            "usage": "20% of content mix",
        },
        {
            "type": "Trending Sound + Niche Content",
            "format": "Use viral audio + show niche content over it",
            "caption_formula": "[Platform-specific hashtags]. [Niche hashtags]. #fyp #foryou",
            "usage": "15% of content mix",
        },
        {
            "type": "Educational Carousel/Slideshow",
            "format": "5-10 slide breakdown of a niche topic",
            "caption_formula": "Save this for later. [Topic] explained in [N] slides. Follow for more [niche] tips.",
            "usage": "5% of content mix — highest save rate",
        },
    ]
    return templates


def _conversion_strategy(niche: str, profile: dict) -> dict:
    """Strategy for converting a theme page from growth to revenue."""
    return {
        "phases": [
            {
                "phase": "Pre-monetization (0-10k followers)",
                "focus": "Build trust and audience",
                "actions": [
                    "Add affiliate links to bio from day 1 — even small traffic converts",
                    "Collect emails via a free lead magnet (e.g., 'Free [niche] guide')",
                    "Build posting consistency — algorithm rewards creators who don't stop",
                    "Document your growth journey — this becomes content AND builds credibility",
                ],
            },
            {
                "phase": "Early monetization (10k-50k followers)",
                "focus": "Activate multiple revenue streams",
                "actions": [
                    "Apply for: " + ", ".join(profile["monetization"][:2]),
                    "Offer shoutout packages to nano-influencers in your niche ($25-$100/post)",
                    "Create your first digital product: a PDF guide, template pack, or mini-course",
                    "Pitch gifted collaborations to brands in your niche (no charge yet)",
                ],
            },
            {
                "phase": "Scaling (50k+ followers)",
                "focus": "Convert audience to high-value revenue",
                "actions": [
                    "Negotiate paid brand deals: industry rate $100-$1000 per 10k followers",
                    "Launch a Patreon or exclusive community for super-fans",
                    "Create a course or coaching program for your niche ($97-$497 price point)",
                    "Explore agency deals: manage posting for brands in your niche",
                    "License your top content to other pages for monthly fee",
                ],
            },
        ],
        "tools": {
            "scheduling": ["Buffer", "Later", "Hootsuite", "Meta Business Suite"],
            "design": ["Canva Pro", "Adobe Express", "CapCut"],
            "analytics": ["Metricool", "Iconosquare", "TikTok Analytics", "YouTube Studio"],
            "monetization": ["LTK (LikeToKnowIt)", "Amazon Associates", "ShareASale", "Impact", "Linktree"],
            "sourcing": ["Pexels", "Unsplash", "Pixabay", "Pinterest", "Reddit"],
        },
        "key_mistakes_to_avoid": [
            "Posting inconsistently — take a week off = lose algorithm favor",
            "Using no-niche or banned hashtags — get shadowbanned",
            "Ignoring comments in first hour — kills reach",
            "Copying content without adding value — DMCA risk + trust loss",
            "Promoting too early (before trust is built) — kills engagement rate",
            "Not having a CTA in every post — followers don't know what to do next",
        ],
    }
