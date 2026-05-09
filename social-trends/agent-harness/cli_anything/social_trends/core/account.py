"""Account optimisation engine.

Covers:
  - Platform-specific optimisation for TikTok, Instagram, YouTube
  - Bio optimisation, posting schedule, content pillar strategy
  - Engagement rate benchmarks and growth diagnostics
  - Cross-platform account linking strategy
"""

from typing import Any

# Engagement rate benchmarks by platform and follower tier
_ENGAGEMENT_BENCHMARKS: dict[str, dict[str, dict[str, float]]] = {
    "instagram": {
        "nano (1K–10K)":    {"good": 4.0, "excellent": 8.0, "unit": "%"},
        "micro (10K–50K)":  {"good": 2.5, "excellent": 5.0, "unit": "%"},
        "mid (50K–500K)":   {"good": 1.5, "excellent": 3.0, "unit": "%"},
        "macro (500K+)":    {"good": 0.8, "excellent": 2.0, "unit": "%"},
    },
    "tiktok": {
        "nano (1K–10K)":    {"good": 6.0, "excellent": 12.0, "unit": "%"},
        "micro (10K–50K)":  {"good": 4.0, "excellent": 8.0, "unit": "%"},
        "mid (50K–500K)":   {"good": 2.5, "excellent": 5.0, "unit": "%"},
        "macro (500K+)":    {"good": 1.5, "excellent": 3.5, "unit": "%"},
    },
    "youtube": {
        "nano (1K–10K)":    {"good": 3.0, "excellent": 6.0, "unit": "% likes/views"},
        "micro (10K–50K)":  {"good": 2.0, "excellent": 4.0, "unit": "% likes/views"},
        "mid (50K–500K)":   {"good": 1.0, "excellent": 2.5, "unit": "% likes/views"},
        "macro (500K+)":    {"good": 0.5, "excellent": 1.5, "unit": "% likes/views"},
    },
}

# Optimal profile bio templates per niche
_BIO_TEMPLATES: dict[str, dict[str, str]] = {
    "fitness": {
        "tiktok": "💪 [Your transformation story in 5 words]\n🏋️ [Your specialty: HIIT / Strength / Weight loss]\n📲 Free workout guide 👇",
        "instagram": "💪 [Transformation: e.g. Lost 50lbs, Built lean muscle]\n🏋️ [Specialty] | [Location optional]\n📩 Coaching DMs open\n👇 Free training program",
        "youtube": "[Name] — [Specialty Fitness Channel]\n💪 [Posting schedule: New videos every Mon/Thu]\n📧 [Email for collabs]\n👇 Free guide in links",
    },
    "food": {
        "tiktok": "🍳 Easy [cuisine type] recipes\n⏱️ [Time promise: 30-min meals, 5-ingredient recipes]\n📲 Full recipes 👇",
        "instagram": "🍳 [Cuisine/Specialty] recipes\n🌱 [Diet: Vegan / Keto / Budget-friendly]\n📍 [Location optional]\n👇 Recipe book / blog link",
        "youtube": "[Name] — [Cuisine/Style] Cooking Channel\n🍳 [Posting frequency]\n📧 Collab inquiries: [email]",
    },
    "finance": {
        "tiktok": "💰 [Promise: Saved $10K in 1 year]\n📊 [Strategy: Index investing / Side hustles]\n🆓 Free budget template 👇",
        "instagram": "💰 [Financial promise or journey]\n📊 Personal finance | Investing | Side hustles\n🎓 [Credential if any]\n👇 Free budget template",
        "youtube": "[Name] — Personal Finance & Investing\n💰 [Niche: Beginner investing / FIRE / Side hustle]\n📊 New videos every [day]",
    },
    "general": {
        "tiktok": "✨ [Value proposition in 1 line]\n🎯 [Niche/specialty]\n👇 [CTA: Free resource / Link in bio]",
        "instagram": "✨ [Value proposition]\n🎯 [Niche]\n📍 [Location optional]\n👇 [Primary CTA]",
        "youtube": "[Channel Name] — [What you make]\n📅 [Upload schedule]\n📧 Business: [email]",
    },
}

# Content pillar frameworks by niche (80/20 split: 80% value, 20% promo)
_CONTENT_PILLARS: dict[str, list[dict[str, Any]]] = {
    "fitness": [
        {"pillar": "Education", "percentage": 30, "examples": ["Exercise tutorials", "Form checks", "Science of X"]},
        {"pillar": "Transformation/Results", "percentage": 25, "examples": ["Before/After", "Progress updates", "Client results"]},
        {"pillar": "Entertainment/Relatable", "percentage": 25, "examples": ["Gym fails", "Expectations vs reality", "Fitness memes"]},
        {"pillar": "Lifestyle", "percentage": 10, "examples": ["Day in my life", "What I eat", "Morning routine"]},
        {"pillar": "Promotion", "percentage": 10, "examples": ["Coaching offer", "Product review", "Program launch"]},
    ],
    "food": [
        {"pillar": "Recipes", "percentage": 40, "examples": ["Full recipes", "Ingredient highlights", "Technique demos"]},
        {"pillar": "Hacks/Tips", "percentage": 25, "examples": ["Kitchen hacks", "Grocery tips", "Storage tricks"]},
        {"pillar": "Reviews", "percentage": 20, "examples": ["Restaurant reviews", "Product reviews", "Taste tests"]},
        {"pillar": "Storytelling", "percentage": 10, "examples": ["Recipe origin", "Food travel", "Family recipes"]},
        {"pillar": "Promotion", "percentage": 5, "examples": ["Cookbook", "Course", "Sponsored ingredient"]},
    ],
    "finance": [
        {"pillar": "Education", "percentage": 35, "examples": ["Concept explainers", "Step-by-step guides", "Tool reviews"]},
        {"pillar": "Inspiration/Results", "percentage": 25, "examples": ["Net worth updates", "Savings milestones", "Success stories"]},
        {"pillar": "Opinion/Commentary", "percentage": 20, "examples": ["Market takes", "Finance myths debunked", "Trend analysis"]},
        {"pillar": "Lifestyle Integration", "percentage": 10, "examples": ["Frugal living", "FIRE journey", "Investment diary"]},
        {"pillar": "Promotion", "percentage": 10, "examples": ["Course", "Tool affiliate", "Book recommendation"]},
    ],
    "general": [
        {"pillar": "Education/Value", "percentage": 40, "examples": ["How-to guides", "Tips and tricks", "Explainers"]},
        {"pillar": "Entertainment", "percentage": 25, "examples": ["Relatable content", "Trends", "Challenges"]},
        {"pillar": "Personal/Authentic", "percentage": 20, "examples": ["Behind the scenes", "Your story", "Opinion pieces"]},
        {"pillar": "Community", "percentage": 10, "examples": ["Q&A", "Collaborations", "Fan features"]},
        {"pillar": "Promotion", "percentage": 5, "examples": ["Product/service", "Affiliate", "Brand deal"]},
    ],
}

# Growth diagnostics: common issues and fixes
_GROWTH_DIAGNOSTICS: list[dict[str, str]] = [
    {
        "symptom": "High views but low followers",
        "cause": "Videos don't clearly show why to follow; no strong hook for channel identity",
        "fix": "Add CTA 'follow for more X' at second 15, update bio to clearly state value, post a 'subscribe bait' video",
    },
    {
        "symptom": "Low views on new videos",
        "cause": "Weak hook, posting at wrong time, inconsistent niche, hashtag issues",
        "fix": "A/B test different hook styles, check posting time analytics, ensure niche consistency across last 5 posts",
    },
    {
        "symptom": "Good followers but low engagement",
        "cause": "Content shifted niche, audience grew stale, engagement bait missing",
        "fix": "Add questions to captions, create poll stickers in Stories, respond to every comment for 2 weeks",
    },
    {
        "symptom": "Stuck at a follower plateau",
        "cause": "Algorithm stagnation, no viral content, too much promotional posting",
        "fix": "Try trending sounds/formats, post 3x more value content vs promo, collab with 3 creators in your niche",
    },
    {
        "symptom": "Low watch time / completion rate",
        "cause": "Videos too long, slow intros, information not matching hook",
        "fix": "Cut first 5 seconds of all videos, hook must deliver on its promise, use pattern interrupts every 15–20 seconds",
    },
    {
        "symptom": "Growing on one platform, silent on others",
        "cause": "Cross-posting without platform-native optimisation",
        "fix": "Adapt captions and CTAs per platform, use platform-native sounds, vary aspect ratios and thumbnail styles",
    },
]


def generate_optimisation_report(platform: str, niche: str,
                                 handle: str = "",
                                 followers: int = 0) -> dict:
    """Generate a comprehensive account optimisation report."""
    platform_lower = platform.lower()
    niche_lower = niche.lower() if niche.lower() in _CONTENT_PILLARS else "general"

    report = {
        "account": {
            "handle": handle,
            "platform": platform_lower,
            "niche": niche,
            "followers": followers,
        },
        "bio_template": _BIO_TEMPLATES.get(niche_lower, _BIO_TEMPLATES["general"]).get(
            platform_lower, _BIO_TEMPLATES["general"]["tiktok"]
        ),
        "content_pillars": _CONTENT_PILLARS.get(niche_lower, _CONTENT_PILLARS["general"]),
        "posting_schedule": _optimal_schedule(platform_lower, niche_lower),
        "engagement_benchmarks": _engagement_for_size(platform_lower, followers),
        "profile_checklist": _profile_checklist(platform_lower),
        "growth_tactics": _growth_tactics(platform_lower, niche_lower),
        "monetisation_roadmap": _monetisation_roadmap(followers, niche_lower),
    }
    return report


def diagnose_growth_issues(symptoms: list[str]) -> list[dict]:
    """Match described growth symptoms to causes and fixes."""
    results = []
    for symptom in symptoms:
        s_lower = symptom.lower()
        for diag in _GROWTH_DIAGNOSTICS:
            if any(word in diag["symptom"].lower() for word in s_lower.split()):
                results.append(diag)
                break
        else:
            results.append({
                "symptom": symptom,
                "cause": "Needs more context to diagnose",
                "fix": "Run 'social-trends account diagnose' and describe your specific metrics",
            })
    return results


def get_engagement_benchmarks(platform: str) -> dict:
    """Return engagement rate benchmarks for a platform."""
    platform_lower = platform.lower()
    return _ENGAGEMENT_BENCHMARKS.get(platform_lower, {
        "note": f"No benchmarks found for '{platform}'. Available: {', '.join(_ENGAGEMENT_BENCHMARKS.keys())}"
    })


def calculate_engagement_rate(likes: int, comments: int, shares: int,
                               views: int, followers: int) -> dict:
    """Calculate engagement rate using multiple methods."""
    if views > 0:
        views_er = round((likes + comments + shares) / views * 100, 2)
    else:
        views_er = 0.0
    if followers > 0:
        followers_er = round((likes + comments + shares) / followers * 100, 2)
    else:
        followers_er = 0.0
    return {
        "engagement_rate_by_views": f"{views_er}%",
        "engagement_rate_by_followers": f"{followers_er}%",
        "total_engagements": likes + comments + shares,
        "interpretation": _interpret_er(max(views_er, followers_er)),
    }


def list_all_diagnostics() -> list[dict]:
    """Return all growth diagnostics."""
    return _GROWTH_DIAGNOSTICS


def _optimal_schedule(platform: str, niche: str) -> dict:
    times = {
        "fitness": {"tiktok": ["6–8 AM", "12–1 PM", "6–8 PM"], "instagram": ["7–9 AM", "12–2 PM", "5–7 PM"], "youtube": ["Mon 8 AM", "Thu 8 AM", "Sat 10 AM"]},
        "food":    {"tiktok": ["11 AM–1 PM", "5–7 PM", "8–10 PM"], "instagram": ["11 AM–1 PM", "7–9 PM"], "youtube": ["Fri 6 PM", "Sun 12 PM"]},
        "finance": {"tiktok": ["7–9 AM", "12–1 PM", "6–8 PM"], "instagram": ["7–9 AM", "6–8 PM"], "youtube": ["Mon 9 AM", "Wed 9 AM"]},
        "general": {"tiktok": ["9–11 AM", "12–3 PM", "7–9 PM"], "instagram": ["8–10 AM", "12–2 PM", "7–9 PM"], "youtube": ["Fri 8 PM", "Sat 10 AM"]},
    }
    niche_times = times.get(niche, times["general"])
    posting_times = niche_times.get(platform, niche_times.get("tiktok", ["12 PM"]))

    freq = {
        "tiktok": "1–3 posts/day (minimum 1 for consistent growth)",
        "instagram": "4–7 feed posts/week + 5–7 Stories/day",
        "youtube": "1–2 videos/week (consistent schedule matters most)",
        "reels": "7–14 Reels/week for aggressive growth",
    }.get(platform, "Daily posting recommended")

    return {
        "best_times": posting_times,
        "frequency": freq,
        "consistency_tip": "Same posting schedule every week trains your audience and the algorithm",
        "warmup_strategy": "New accounts: post 3x/day for the first 2 weeks to build algorithm trust",
    }


def _engagement_for_size(platform: str, followers: int) -> dict:
    if followers == 0:
        return {"note": "Provide follower count for personalised benchmarks"}
    tier = (
        "nano (1K–10K)" if followers < 10_000 else
        "micro (10K–50K)" if followers < 50_000 else
        "mid (50K–500K)" if followers < 500_000 else
        "macro (500K+)"
    )
    benchmarks = _ENGAGEMENT_BENCHMARKS.get(platform, {}).get(tier, {})
    return {"tier": tier, "followers": followers, "benchmarks": benchmarks}


def _profile_checklist(platform: str) -> list[dict]:
    base = [
        {"item": "Profile photo", "spec": "Clear face/logo, 400x400px minimum, high contrast"},
        {"item": "Username", "spec": "Easy to spell/remember, consistent across all platforms"},
        {"item": "Display name", "spec": "Include 1–2 niche keywords for SEO discoverability"},
        {"item": "Bio/About", "spec": "Clear value proposition + CTA + relevant keywords"},
        {"item": "Link in bio", "spec": "Use Linktree/Beacons/Stan Store for multiple links"},
    ]
    platform_specific = {
        "tiktok": [
            {"item": "TikTok Series", "spec": "Group related content into Series for authority"},
            {"item": "Fixed pinned videos", "spec": "Pin your 3 best performing or intro videos"},
        ],
        "instagram": [
            {"item": "Highlights", "spec": "Create 5–8 Story Highlights with clear cover icons"},
            {"item": "Grid aesthetic", "spec": "Plan a consistent colour palette and layout style"},
            {"item": "Alt text on posts", "spec": "Add alt text for accessibility and SEO"},
        ],
        "youtube": [
            {"item": "Channel art/banner", "spec": "2560x1440px, include posting schedule"},
            {"item": "Channel description", "spec": "Include keywords, posting schedule, contact email"},
            {"item": "Playlists", "spec": "Organise videos into playlists immediately on upload"},
            {"item": "End screens & cards", "spec": "Set default end screen template with next video + subscribe"},
        ],
    }
    return base + platform_specific.get(platform, [])


def _growth_tactics(platform: str, niche: str) -> list[str]:
    base = [
        "Engage in comments of top creators in your niche (not spam — add genuine value)",
        "Duet/Stitch (TikTok) or Collab posts (Instagram) with niche creators",
        "Reply to every comment for the first hour after posting (signals engagement to algorithm)",
        "Cross-promote your best content on all platforms within 24h",
        "Run a niche-specific challenge or campaign every 30–45 days",
        "Use trending audio within 48h of it peaking",
    ]
    platform_tactics = {
        "tiktok": [
            "Go Live 2–3x/week (1h minimum) — TikTok heavily boosts Live creators",
            "Post 3 videos/day for 2 weeks then analyse which performs best",
            "Use the Q&A feature to turn comments into new video ideas",
        ],
        "instagram": [
            "Story polls and question boxes daily to boost account activity",
            "Post Reels on weekdays, carousel posts on weekends",
            "Use Close Friends for premium/exclusive content",
        ],
        "youtube": [
            "Post a Shorts for every long-form video to capture different audiences",
            "Optimise thumbnail CTR: test multiple designs, track analytics",
            "Respond to every comment in the first 48h post-upload",
        ],
    }
    return base + platform_tactics.get(platform, [])


def _monetisation_roadmap(followers: int, niche: str) -> list[dict]:
    return [
        {
            "stage": "0–1K followers",
            "monetisation": "Not yet; focus on content quality and consistency",
            "focus": "Build proof of concept content; define content pillars",
        },
        {
            "stage": "1K–10K followers",
            "monetisation": "Affiliate marketing (Amazon, niche products), digital products",
            "focus": "Email list building, first product launch, affiliate links in bio",
        },
        {
            "stage": "10K–50K followers",
            "monetisation": "Brand deals, sponsored content, own digital product",
            "income_range": "$500–$3,000/month (varies by niche)",
            "focus": "Media kit creation, agency outreach, Patreon/membership",
        },
        {
            "stage": "50K–100K followers",
            "monetisation": "Premium brand deals, courses, coaching, merchandise",
            "income_range": "$3,000–$15,000/month",
            "focus": "Own platform (email, website), recurring revenue products",
        },
        {
            "stage": "100K+ followers",
            "monetisation": "Full creator economy — ad revenue, licensing, speaking, books",
            "income_range": "$10,000–$100,000+/month",
            "focus": "Team building, evergreen products, brand licensing",
        },
    ]


def _interpret_er(er: float) -> str:
    if er >= 8:
        return "Excellent — highly engaged community"
    if er >= 4:
        return "Good — above average engagement"
    if er >= 2:
        return "Average — room for improvement"
    if er >= 1:
        return "Below average — review content quality and posting consistency"
    return "Low — significant engagement issue; audit content, posting time, and audience fit"
