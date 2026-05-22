"""
Theme page playbook — everything needed to build a profitable converting theme page.

A theme page aggregates content around a niche without the creator appearing on camera.
This module generates niche analysis, monetization roadmaps, and content calendars.
"""
from typing import Optional


NICHES = {
    "motivation": {
        "description": "Motivational quotes, success stories, mindset content",
        "monetization": ["digital products", "affiliate (books/courses)", "brand deals"],
        "content_types": ["quote clips", "success story edits", "audio montages"],
        "target_er": 6.0,
        "peak_post_times": ["6:00 AM", "12:00 PM", "9:00 PM"],
        "top_hashtags": ["#motivation", "#mindset", "#success", "#grindset", "#hustle"],
        "avg_cpm_usd": 3.5,
    },
    "finance": {
        "description": "Money tips, investing, financial freedom content",
        "monetization": ["affiliate (trading apps)", "paid newsletters", "courses"],
        "content_types": ["stat callouts", "myth-busting", "how-to clips"],
        "target_er": 4.5,
        "peak_post_times": ["7:00 AM", "12:30 PM", "6:00 PM"],
        "top_hashtags": ["#personalfinance", "#investing", "#moneytips", "#financialfreedom"],
        "avg_cpm_usd": 8.0,
    },
    "fitness": {
        "description": "Workout clips, transformation content, diet tips",
        "monetization": ["supplement affiliate", "training programs", "brand deals"],
        "content_types": ["workout clips", "transformation reels", "tip videos"],
        "target_er": 5.5,
        "peak_post_times": ["5:30 AM", "12:00 PM", "6:30 PM"],
        "top_hashtags": ["#fitness", "#workout", "#gym", "#gains", "#fatloss"],
        "avg_cpm_usd": 4.0,
    },
    "luxury": {
        "description": "Luxury lifestyle, cars, watches, real estate",
        "monetization": ["affiliate luxury goods", "brand deals", "dropshipping"],
        "content_types": ["showcase clips", "aspirational edits", "location tours"],
        "target_er": 4.0,
        "peak_post_times": ["8:00 AM", "1:00 PM", "8:00 PM"],
        "top_hashtags": ["#luxury", "#lifestyle", "#rich", "#supercar", "#wealth"],
        "avg_cpm_usd": 6.0,
    },
    "relationships": {
        "description": "Dating advice, couple goals, psychology of attraction",
        "monetization": ["dating app affiliate", "ebooks", "courses"],
        "content_types": ["tip videos", "reaction clips", "quote edits"],
        "target_er": 7.0,
        "peak_post_times": ["7:00 AM", "12:00 PM", "10:00 PM"],
        "top_hashtags": ["#dating", "#relationships", "#love", "#couplegoals"],
        "avg_cpm_usd": 3.0,
    },
    "food": {
        "description": "Food hacks, restaurant reviews, recipe shorts",
        "monetization": ["food delivery affiliate", "cookbooks", "brand deals"],
        "content_types": ["recipe clips", "reaction videos", "ASMR cooking"],
        "target_er": 5.0,
        "peak_post_times": ["11:00 AM", "5:00 PM", "8:00 PM"],
        "top_hashtags": ["#food", "#recipe", "#foodhack", "#cooking", "#foodtok"],
        "avg_cpm_usd": 2.5,
    },
    "pets": {
        "description": "Cute animals, pet care tips, funny pet clips",
        "monetization": ["pet product affiliate", "merch", "brand deals"],
        "content_types": ["cute clips", "funny compilations", "care tips"],
        "target_er": 8.0,
        "peak_post_times": ["8:00 AM", "12:00 PM", "7:00 PM"],
        "top_hashtags": ["#pets", "#dogsoftiktok", "#catsoftiktok", "#petcare"],
        "avg_cpm_usd": 2.0,
    },
}


def list_niches() -> list[dict]:
    """List all supported niches with brief descriptions."""
    return [{"niche": k, "description": v["description"]} for k, v in NICHES.items()]


def niche_analysis(niche: str) -> dict:
    """Full analysis for a given niche including monetization and content strategy."""
    niche = niche.lower()
    if niche not in NICHES:
        closest = [n for n in NICHES if niche in n or n in niche]
        return {
            "error": f"Niche '{niche}' not found.",
            "available_niches": list(NICHES.keys()),
            "closest_match": closest,
        }
    data = NICHES[niche]
    # Revenue estimate at 10k/50k/100k followers
    cpm = data["avg_cpm_usd"]
    revenue_estimates = {
        "10k_followers": {
            "monthly_views_est": 50_000,
            "ad_revenue_usd": round(50_000 / 1000 * cpm, 0),
            "affiliate_revenue_usd": "50–200",
            "total_est_usd": "~100–500",
        },
        "50k_followers": {
            "monthly_views_est": 300_000,
            "ad_revenue_usd": round(300_000 / 1000 * cpm, 0),
            "affiliate_revenue_usd": "200–800",
            "total_est_usd": "~1,000–3,000",
        },
        "100k_followers": {
            "monthly_views_est": 700_000,
            "ad_revenue_usd": round(700_000 / 1000 * cpm, 0),
            "affiliate_revenue_usd": "500–2000",
            "total_est_usd": "~3,000–10,000",
        },
    }
    return {
        "niche": niche,
        **data,
        "revenue_estimates": revenue_estimates,
    }


def content_calendar(niche: str, days: int = 7) -> list[dict]:
    """Generate a posting calendar for the niche."""
    niche = niche.lower()
    info = NICHES.get(niche, {})
    content_types = info.get("content_types", ["educational clip", "trend clip", "tip video"])
    times = info.get("peak_post_times", ["8:00 AM", "12:00 PM", "7:00 PM"])
    tags = info.get("top_hashtags", [f"#{niche}"])

    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    formats_cycle = content_types * (days // len(content_types) + 1)

    calendar = []
    for i in range(days):
        fmt = formats_cycle[i]
        calendar.append({
            "day": day_names[i % 7],
            "content_format": fmt,
            "post_times": times,
            "hashtags": tags[:5],
            "hook_ideas": _hook_ideas(niche, fmt),
            "cta": _cta_for_niche(niche),
        })
    return calendar


def _hook_ideas(niche: str, content_type: str) -> list[str]:
    hooks = {
        "motivation": [
            "Nobody talks about this success secret…",
            "Do this every morning and watch your life change:",
            "This mindset shift made me $0 → $10k/month:",
        ],
        "finance": [
            "If you have $100, here's exactly what to do:",
            "Stop wasting money on this (most people do):",
            "The #1 money mistake young people make:",
        ],
        "fitness": [
            "You're doing this exercise WRONG (fix this now):",
            "Lost 20lbs in 60 days — here's exactly how:",
            "This 10-min morning routine changed everything:",
        ],
        "luxury": [
            "Inside a $10M penthouse — tour 👀",
            "Things only wealthy people do differently:",
            "How I went from broke to driving a Lamborghini:",
        ],
        "relationships": [
            "Red flag you're ignoring right now:",
            "Psychology trick to make anyone like you:",
            "The #1 sign they're the one — most people miss it:",
        ],
        "food": [
            "This $3 ingredient changes EVERYTHING:",
            "Restaurant trick most people don't know:",
            "Make this in 5 minutes — better than takeout:",
        ],
        "pets": [
            "My dog does THIS every morning (so cute):",
            "Warning: if your pet does this call a vet:",
            "Trick every dog owner needs to know:",
        ],
    }
    default = [
        f"Nobody talks about this {niche} secret…",
        f"The {niche} tip that changed everything:",
        f"Stop doing this if you're into {niche}:",
    ]
    return hooks.get(niche, default)


def _cta_for_niche(niche: str) -> str:
    ctas = {
        "motivation": "Follow for daily motivation that hits different 🔥",
        "finance": "Follow for money tips nobody teaches you in school 💰",
        "fitness": "Follow for daily fitness content that actually works 💪",
        "luxury": "Follow for luxury lifestyle inspo ✈️",
        "relationships": "Follow for relationship advice that actually helps ❤️",
        "food": "Follow for the best food hacks daily 🍕",
        "pets": "Follow for daily cute pet content 🐾",
    }
    return ctas.get(niche, f"Follow for the best {niche} content daily!")


def conversion_funnel_guide(niche: str) -> dict:
    """
    Returns the step-by-step funnel to convert followers to buyers.
    Covers: awareness → engagement → trust → conversion.
    """
    return {
        "niche": niche,
        "funnel_stages": [
            {
                "stage": "1. Awareness (Day 1–30)",
                "goal": "Hit 1k–10k followers, establish authority",
                "actions": [
                    "Post 3x/day using trending audio",
                    "Use viral hooks in first 3 seconds",
                    "Stitch/duet popular creators in your niche",
                    "Focus on reach: broad hashtags + 1–2 niche hashtags",
                ],
            },
            {
                "stage": "2. Engagement (Day 30–60)",
                "goal": "Build comment community, get DMs",
                "actions": [
                    "Ask questions in every caption",
                    "Reply to EVERY comment in first hour",
                    "Post 'comment X for the free guide' CTAs",
                    "Go live 2x/week to boost algorithm push",
                ],
            },
            {
                "stage": "3. Trust (Day 60–90)",
                "goal": "Position as authority, warm up audience",
                "actions": [
                    "Share case studies / proof content",
                    "Add bio link (Linktree/Beacons) → lead magnet",
                    "Start email list with free value offer",
                    "DM every new follower with a welcome message",
                ],
            },
            {
                "stage": "4. Conversion (Day 90+)",
                "goal": "Monetize — affiliate, digital product, brand deal",
                "actions": [
                    "Launch digital product ($7–$47 low ticket first)",
                    "Add affiliate links to bio + pin comment",
                    "Pitch brands in your niche (10k+ followers)",
                    "Run a 'limited time' offer story/video",
                    "Use ManyChat to automate DM funnels",
                ],
            },
        ],
        "tools_recommended": {
            "link_in_bio": ["Beacons.ai", "Linktree", "Stan.store"],
            "email_list": ["ConvertKit (free)", "Beehiiv", "Mailchimp"],
            "dm_automation": ["ManyChat", "Chatfuel"],
            "video_editing": ["CapCut", "InShot", "Splice"],
            "content_sourcing": ["Pinterest", "Reddit", "Google Trends", "YouTube trending"],
            "scheduling": ["Later", "Buffer", "TikTok native scheduler"],
            "analytics": ["TikTok Analytics", "Social Blade", "Metricool"],
        },
    }
