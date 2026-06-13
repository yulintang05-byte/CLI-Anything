"""Social media account optimizer — posting times, bio, content strategy, growth tactics."""
from typing import List, Dict, Any, Optional
import json

# Research-backed optimal posting times (local timezone)
POSTING_TIMES: Dict[str, Dict[str, List[str]]] = {
    "tiktok": {
        "Monday":    ["6 AM", "10 AM", "10 PM"],
        "Tuesday":   ["2 AM", "4 AM", "9 AM"],
        "Wednesday": ["7 AM", "8 AM", "11 PM"],
        "Thursday":  ["9 AM", "12 PM", "7 PM"],
        "Friday":    ["5 AM", "1 PM", "3 PM"],
        "Saturday":  ["11 AM", "7 PM", "8 PM"],
        "Sunday":    ["7 AM", "8 AM", "4 PM"],
    },
    "instagram": {
        "Monday":    ["7 AM", "11 AM", "1 PM"],
        "Tuesday":   ["8 AM", "1 PM", "2 PM"],
        "Wednesday": ["9 AM", "11 AM", "1 PM"],
        "Thursday":  ["7 AM", "1 PM", "3 PM"],
        "Friday":    ["9 AM", "11 AM", "2 PM"],
        "Saturday":  ["9 AM", "10 AM", "6 PM"],
        "Sunday":    ["10 AM", "6 PM", "8 PM"],
    },
    "youtube": {
        "Monday":    ["3 PM", "4 PM", "5 PM"],
        "Tuesday":   ["3 PM", "4 PM", "5 PM"],
        "Wednesday": ["3 PM", "4 PM", "5 PM"],
        "Thursday":  ["12 PM", "3 PM", "6 PM"],
        "Friday":    ["12 PM", "3 PM", "5 PM"],
        "Saturday":  ["9 AM", "11 AM", "3 PM"],
        "Sunday":    ["9 AM", "11 AM", "12 PM"],
    },
    "twitter": {
        "Monday":    ["8 AM", "12 PM", "4 PM"],
        "Tuesday":   ["8 AM", "12 PM", "4 PM"],
        "Wednesday": ["9 AM", "12 PM", "3 PM"],
        "Thursday":  ["8 AM", "12 PM", "4 PM"],
        "Friday":    ["8 AM", "10 AM", "2 PM"],
        "Saturday":  ["9 AM", "12 PM"],
        "Sunday":    ["10 AM", "12 PM"],
    },
}

# Platform-specific posting frequency recommendations
POSTING_FREQUENCY = {
    "tiktok":    {"min": 1, "optimal": 3, "max": 5,  "unit": "per day"},
    "instagram": {"min": 1, "optimal": 2, "max": 3,  "unit": "per day (mix Reels + Stories)"},
    "youtube":   {"min": 1, "optimal": 2, "max": 3,  "unit": "per week"},
    "twitter":   {"min": 3, "optimal": 5, "max": 10, "unit": "per day"},
    "threads":   {"min": 2, "optimal": 4, "max": 8,  "unit": "per day"},
}

# Bio templates by goal
BIO_TEMPLATES = {
    "theme_page": {
        "formula":  "[Niche Emoji] [What you curate] | [Frequency] | [CTA with link]",
        "examples": [
            "🔥 Daily motivation & mindset | New posts every AM | ↓ Free guide below",
            "💰 Business tips for entrepreneurs | 3x daily | ↓ Join 50K+ in bio",
            "🎯 Fitness transformations | Daily inspo | ↓ Free plan in bio",
        ],
        "rules": [
            "Put the most important word in line 1 (above the fold)",
            "Include exactly ONE call-to-action link",
            "Use 1–3 emojis max — don't spam",
            "State your value proposition in 5 words or less",
        ],
    },
    "personal_brand": {
        "formula":  "[Title] | [Who you help] | [Result you deliver] | [Social proof] | [CTA]",
        "examples": [
            "Marketing Coach | I help brands 10x their reach | 100K+ students | ↓ Free course",
            "Fitness Trainer | Helping busy people lose 20lbs | 500+ clients | ↓ DM 'START'",
        ],
        "rules": [
            "Lead with your title or niche keyword for SEO",
            "Include a specific result or number",
            "Social proof (followers, clients, sales) builds immediate trust",
            "DM CTA converts higher than link CTA on some platforms",
        ],
    },
    "business": {
        "formula":  "[Product/Service] | [Unique value prop] | [Offer or discount] | [CTA]",
        "examples": [
            "🛍️ Handmade jewelry | Ships worldwide | Use code SAVE15 | ↓ Shop below",
            "📱 Social media agency | Guaranteed results | Free audit → DM 'AUDIT'",
        ],
        "rules": [
            "Lead with what you sell",
            "Include a limited-time offer or urgency trigger",
            "Make the CTA extremely specific ('DM AUDIT', not 'DM me')",
        ],
    },
}

# Content pillars framework
CONTENT_PILLARS = {
    "4_pillar": {
        "description": "Balanced content mix for consistent growth",
        "pillars": [
            {"name": "Educate",   "pct": 40, "desc": "How-tos, tips, tutorials, explainers"},
            {"name": "Entertain", "pct": 30, "desc": "Humor, relatable, reactions, trends"},
            {"name": "Inspire",   "pct": 20, "desc": "Transformations, stories, motivation"},
            {"name": "Promote",   "pct": 10, "desc": "Products, services, CTAs (max 10%)"},
        ],
    },
    "3_pillar_growth": {
        "description": "Aggressive growth focus — maximize reach",
        "pillars": [
            {"name": "Trending",  "pct": 50, "desc": "Trend chasing, sounds, challenges"},
            {"name": "Value",     "pct": 35, "desc": "Practical tips, tutorials, hacks"},
            {"name": "Personal",  "pct": 15, "desc": "BTS, personality, day in my life"},
        ],
    },
    "theme_page": {
        "description": "Theme page / curation account framework",
        "pillars": [
            {"name": "Viral Reposts",  "pct": 60, "desc": "Curate best content from niche — credit creators"},
            {"name": "Original Mix",   "pct": 25, "desc": "Your original takes on niche topics"},
            {"name": "Monetization",   "pct": 15, "desc": "Shoutouts, affiliate, sponsored posts"},
        ],
    },
}

# Platform-specific SEO tips
PLATFORM_SEO = {
    "tiktok": [
        "Put your main keyword in the FIRST LINE of your caption — TikTok indexes captions for search.",
        "Use full sentences in captions (not just hashtags) — TikTok's search uses semantic NLP.",
        "Your username and display name are searchable — include your niche keyword.",
        "Enable 'Suggest your account to others' in privacy settings.",
        "Respond to ALL comments in the first hour — algorithm rewards engagement velocity.",
    ],
    "instagram": [
        "Alt text on every image (Edit > Advanced Settings) boosts SEO significantly.",
        "Put keywords in your name field (not username) for search ranking.",
        "Use Instagram's keyword search to find what your audience actually types.",
        "Carousel posts get 3x more reach than single images — prioritize carousels.",
        "Reels get the most reach, Stories get the most engagement — use both daily.",
    ],
    "youtube": [
        "First 100 characters of description = most important for SEO (appears in search snippet).",
        "Include 3–5 keyword tags max — don't spam tags.",
        "Add closed captions manually — auto-captions hurt SEO on mispronunciations.",
        "Chapter markers (timestamps in description) boost watch time and SEO.",
        "End screen + cards appear at 20+ second mark — always use them for subscriber CTA.",
    ],
}

# Engagement rate benchmarks
ENGAGEMENT_BENCHMARKS = {
    "tiktok":    {"poor": "<2%", "average": "2–5%", "good": "5–9%", "viral": ">9%"},
    "instagram": {"poor": "<1%", "average": "1–3%", "good": "3–6%", "viral": ">6%"},
    "youtube":   {"poor": "<2%", "average": "2–5%", "good": "5–10%", "viral": ">10%"},
    "twitter":   {"poor": "<0.5%", "average": "0.5–1%", "good": "1–3%", "viral": ">3%"},
}


def optimize_account(platform: str, niche: str, goal: str = "growth") -> Dict[str, Any]:
    """Generate a full account optimization report for a platform/niche combo."""
    platform = platform.lower()
    times = POSTING_TIMES.get(platform, {})
    freq  = POSTING_FREQUENCY.get(platform, {"optimal": 2, "unit": "per day"})

    # Best 3 posting days (highest-traffic)
    best_days = _best_days(platform)

    return {
        "platform":         platform,
        "niche":            niche,
        "goal":             goal,
        "posting_schedule": {
            "frequency":    f"{freq['optimal']} {freq['unit']}",
            "best_days":    best_days,
            "best_times":   {d: times.get(d, [])[:2] for d in best_days},
        },
        "bio_template":     BIO_TEMPLATES.get(goal, BIO_TEMPLATES["theme_page"]),
        "content_pillars":  CONTENT_PILLARS.get("4_pillar" if goal == "growth" else "theme_page"),
        "seo_tips":         PLATFORM_SEO.get(platform, []),
        "engagement_benchmarks": ENGAGEMENT_BENCHMARKS.get(platform, {}),
        "growth_tactics":   _growth_tactics(platform, goal),
        "quick_wins":       _quick_wins(platform),
    }


def optimize_all_platforms(niche: str, goal: str = "growth") -> Dict[str, Any]:
    """Optimization report across all supported platforms."""
    platforms = ["tiktok", "instagram", "youtube", "twitter"]
    return {
        platform: optimize_account(platform, niche, goal)
        for platform in platforms
    }


def generate_content_calendar(
    niche: str,
    platform: str,
    weeks: int = 4,
    pillars: str = "4_pillar",
) -> List[Dict]:
    """Generate a content calendar with post ideas per day."""
    pillar_cfg = CONTENT_PILLARS.get(pillars, CONTENT_PILLARS["4_pillar"])
    pillar_list = pillar_cfg["pillars"]
    freq = POSTING_FREQUENCY.get(platform.lower(), {"optimal": 2})["optimal"]
    calendar = []

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    times_cfg    = POSTING_TIMES.get(platform.lower(), {})

    day_counter = 0
    for week in range(1, weeks + 1):
        for day_name in days_of_week:
            posts = []
            for post_idx in range(freq):
                pillar = pillar_list[(day_counter + post_idx) % len(pillar_list)]
                post_time = (times_cfg.get(day_name, ["12 PM"])[post_idx % len(times_cfg.get(day_name, ["12 PM"]))])
                posts.append({
                    "time":   post_time,
                    "pillar": pillar["name"],
                    "type":   _content_type(platform, pillar["name"]),
                    "prompt": _content_idea(niche, pillar["name"]),
                })
            calendar.append({"week": week, "day": day_name, "posts": posts})
            day_counter += 1

    return calendar


# ── helpers ───────────────────────────────────────────────────────────────────

def _best_days(platform: str) -> List[str]:
    best = {
        "tiktok":    ["Tuesday", "Thursday", "Friday"],
        "instagram": ["Tuesday", "Wednesday", "Thursday"],
        "youtube":   ["Thursday", "Friday", "Saturday"],
        "twitter":   ["Wednesday", "Thursday", "Friday"],
    }
    return best.get(platform, ["Tuesday", "Thursday", "Friday"])


def _growth_tactics(platform: str, goal: str) -> List[str]:
    base = [
        "Reply to every comment within 60 minutes of posting — early engagement signals boost reach.",
        "Collaborate with accounts in your niche (2x–5x follower count range) for exposure.",
        "Cross-post your content to all platforms within 24h of initial post.",
        "Pin your 3 best-performing posts to the top of your profile.",
        "Go Live once per week — platforms prioritize live creators in discovery.",
    ]
    platform_specific = {
        "tiktok": [
            "Post at least 3x daily — TikTok rewards consistency with algorithmic reach.",
            "Comment on trending posts in your niche (50+ comments per day builds authority).",
            "Use TikTok's 'Promote' feature ($5–20) on your best organic posts.",
        ],
        "instagram": [
            "Use Instagram Collabs feature — post appears on both accounts' grids.",
            "Respond to Stories replies — DM conversation boosts relationship score.",
            "Broadcast Channel for direct-to-follower content (high open rate).",
        ],
        "youtube": [
            "Community posts between videos keep subscribers engaged and signal activity.",
            "Optimize thumbnails A/B test with YouTube Studio analytics.",
            "Reply to comments within 24h — comment velocity affects search ranking.",
        ],
    }
    tactics = base + platform_specific.get(platform, [])
    if goal == "monetization":
        tactics += [
            "Add a Linktree or Beacons page linking all your offers.",
            "DM your top engaged followers offering exclusive content — converts to paid.",
        ]
    return tactics


def _quick_wins(platform: str) -> List[str]:
    wins = {
        "tiktok": [
            "Change profile photo to a high-contrast, face-forward image (CTR +23%).",
            "Enable TikTok Creator Marketplace — brands find you automatically.",
            "Add your niche keyword to your TikTok name field right now.",
            "Pin your best-performing video at the top of your grid.",
        ],
        "instagram": [
            "Switch to Creator or Business account for analytics access.",
            "Add 'Linktree' or 'bio.site' URL with all your links.",
            "Create 5 Instagram Story Highlights covering your best content categories.",
            "Add location tags to Reels for local discovery.",
        ],
        "youtube": [
            "Enable channel memberships (1,000 subs required) — immediate passive revenue.",
            "Add end screens to ALL existing videos pointing to your subscribe button.",
            "Update all video thumbnails to have bold text + face (if applicable).",
            "Enable auto-generated chapters in YouTube Studio.",
        ],
        "twitter": [
            "Pin a tweet showcasing your best content or offer.",
            "Enable Twitter/X subscriptions for paid content.",
            "Join 3 Spaces per week — Twitter boosts Space hosts in discovery.",
        ],
    }
    return wins.get(platform, [])


def _content_type(platform: str, pillar: str) -> str:
    type_map = {
        ("tiktok", "Educate"):    "60-90s tutorial video",
        ("tiktok", "Entertain"):  "Trend/challenge video with trending sound",
        ("tiktok", "Inspire"):    "Transformation or story video",
        ("tiktok", "Promote"):    "Soft-sell product demo or review",
        ("instagram", "Educate"): "Carousel (10 slides)",
        ("instagram", "Entertain"): "Reel with trending audio",
        ("instagram", "Inspire"): "Before/after or quote carousel",
        ("instagram", "Promote"): "Product Reel with CTA sticker",
    }
    return type_map.get((platform, pillar), "Short-form video")


def _content_idea(niche: str, pillar: str) -> str:
    ideas = {
        "Educate":   f"5 things most {niche} beginners don't know",
        "Entertain": f"POV: you're a {niche} expert [trend audio]",
        "Inspire":   f"How I went from 0 to [result] with {niche}",
        "Promote":   f"Why [product] changed my {niche} routine",
        "Viral Reposts": f"Best {niche} transformation this week (credit in caption)",
        "Original Mix":  f"My honest take on the latest {niche} trend",
        "Monetization":  f"Paid shoutout / affiliate recommendation for {niche} audience",
        "Trending":      f"Doing [trending challenge] but make it {niche}",
        "Value":         f"The {niche} hack that got me [specific result]",
        "Personal":      f"A day in my life as a {niche} creator",
    }
    return ideas.get(pillar, f"{pillar} content for {niche} audience")
