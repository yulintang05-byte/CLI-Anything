"""Theme page strategy module.

A theme page (also called a niche page or faceless page) is a content account
built around a topic/niche rather than a personal brand. This module provides
structured guidance for creating and monetizing theme pages.
"""

from typing import Optional


PROFITABLE_NICHES = [
    {
        "niche":        "Luxury Lifestyle",
        "platforms":    ["Instagram", "TikTok", "YouTube"],
        "content_type": "Cars, watches, mansions, jets — aspirational montages",
        "monetization": ["Brand deals", "Affiliate (luxury goods)", "Digital products"],
        "difficulty":   "Easy",
        "avg_rpm":      "$4–12",
        "notes":        "High CPM advertisers; easy to source royalty-free clips",
    },
    {
        "niche":        "Motivational / Quotes",
        "platforms":    ["TikTok", "Instagram", "YouTube Shorts"],
        "content_type": "Text overlays on B-roll, voiceover compilations",
        "monetization": ["AdSense", "Affiliate", "Courses", "Merch"],
        "difficulty":   "Very Easy",
        "avg_rpm":      "$2–6",
        "notes":        "Simplest to start; saturated — differentiate with sub-niche",
    },
    {
        "niche":        "Finance / Investing",
        "platforms":    ["YouTube", "TikTok", "Twitter/X"],
        "content_type": "Stock tips, crypto analysis, wealth mindset",
        "monetization": ["AdSense (high CPM)", "Affiliate (brokers)", "Paid newsletter"],
        "difficulty":   "Medium",
        "avg_rpm":      "$15–40",
        "notes":        "Highest CPM niche; requires accuracy to maintain trust",
    },
    {
        "niche":        "Tech & Gadgets",
        "platforms":    ["YouTube", "TikTok", "Instagram"],
        "content_type": "Unboxings, reviews, best-of lists",
        "monetization": ["Amazon affiliate", "AdSense", "Sponsored reviews"],
        "difficulty":   "Medium",
        "avg_rpm":      "$8–20",
        "notes":        "Strong affiliate commissions on Amazon; evergreen content",
    },
    {
        "niche":        "Food & Recipes",
        "platforms":    ["TikTok", "Instagram", "YouTube"],
        "content_type": "Recipe videos, food hacks, restaurant finds",
        "monetization": ["AdSense", "Brand deals (food brands)", "Cookbooks"],
        "difficulty":   "Easy",
        "avg_rpm":      "$3–8",
        "notes":        "Mass-market appeal; pair with affiliate links to ingredients/tools",
    },
    {
        "niche":        "Fitness & Health",
        "platforms":    ["Instagram", "TikTok", "YouTube"],
        "content_type": "Workout routines, transformation stories, nutrition tips",
        "monetization": ["Supplements affiliate", "Workout programs", "Brand deals"],
        "difficulty":   "Medium",
        "avg_rpm":      "$5–15",
        "notes":        "High supplement affiliate commissions; visual results = social proof",
    },
    {
        "niche":        "AI & Productivity",
        "platforms":    ["YouTube", "TikTok", "Twitter/X"],
        "content_type": "AI tool tutorials, productivity hacks, automation workflows",
        "monetization": ["SaaS affiliate", "AdSense", "Digital courses"],
        "difficulty":   "Medium",
        "avg_rpm":      "$10–30",
        "notes":        "Explosive growth niche 2024–2026; high-ticket SaaS affiliate programs",
    },
    {
        "niche":        "Pets & Animals",
        "platforms":    ["TikTok", "Instagram", "YouTube"],
        "content_type": "Cute animal compilations, pet care tips",
        "monetization": ["AdSense", "Pet product affiliate", "Brand deals"],
        "difficulty":   "Easy",
        "avg_rpm":      "$2–5",
        "notes":        "Viral potential is very high; low barrier to entry",
    },
]

CONTENT_PILLARS = {
    "educate":   "How-to, tips, tutorials, explainers (builds authority)",
    "entertain": "Humor, surprising facts, reactions (drives shares)",
    "inspire":   "Quotes, transformations, success stories (drives saves)",
    "engage":    "Polls, questions, challenges (drives comments)",
    "promote":   "Soft sells, product features (converts to revenue)",
}

CONTENT_RATIO = {
    "educate":   40,
    "entertain": 30,
    "inspire":   15,
    "engage":    10,
    "promote":   5,
}

MONETIZATION_THRESHOLDS = {
    "youtube_adsense":    {"subscribers": 1000, "watch_hours": 4000},
    "youtube_shopping":   {"subscribers": 10000},
    "tiktok_creator_fund": {"followers": 10000, "views_30d": 100000},
    "tiktok_series":      {"followers": 10000},
    "instagram_bonuses":  {"followers": 10000},
    "brand_deals_min":    {"followers": 1000, "note": "Micro-influencer deals start at 1K"},
    "amazon_affiliate":   {"followers": 0, "note": "No minimum — start day 1"},
}

CONVERSION_PLAYBOOK = [
    {
        "phase": "1 — Foundation (Week 1–2)",
        "tasks": [
            "Pick 1 hyper-specific niche (e.g. 'AI tools for students' not 'AI')",
            "Create accounts on TikTok, Instagram, YouTube (same handle everywhere)",
            "Design logo + color palette (use Canva free)",
            "Write keyword-rich bios on each platform",
            "Set up a link-in-bio page (Linktree/Stan.store/Beacons)",
            "Create a content bank of 30 ideas before posting",
            "Batch-record/create 10–15 pieces of content",
        ],
    },
    {
        "phase": "2 — Content Engine (Week 3–8)",
        "tasks": [
            "Post 1–4x/day on TikTok, 3–5x/week on Instagram Reels, 1–2x/week on YouTube",
            "Use trending sounds on TikTok within 48h of going viral",
            "Repurpose every TikTok to Instagram Reels and YouTube Shorts",
            "Study analytics weekly — double down on top-performing formats",
            "Engage: reply to every comment in first hour after posting",
            "Collab/duet/stitch with accounts in your niche (1–3x/week)",
            "Test 3 different hook styles per week and track retention",
        ],
    },
    {
        "phase": "3 — Growth Hack (Month 2–3)",
        "tasks": [
            "Run a giveaway (follow + share = entry) to spike followers",
            "Post a viral 'challenge' or trend adaptation for your niche",
            "Guest post / collab with 5–10 similar-size accounts",
            "Cross-promote: put YouTube link in TikTok bio and vice versa",
            "Optimize your top 20% content — reshoot/repost with better hooks",
            "Build an email list from day 1 — offer a free lead magnet",
        ],
    },
    {
        "phase": "4 — Monetize (Month 3+)",
        "tasks": [
            "Apply for TikTok Creator Fund / YouTube Partner Program",
            "Reach out to brands in your niche with a media kit",
            "Add affiliate links to your link-in-bio for top products in niche",
            "Create a simple digital product (guide, preset, template) — $7–$27",
            "Set up a paid community (Discord / Patreon / Telegram)",
            "Launch merchandise when followers exceed 10K",
        ],
    },
]

FACELESS_CONTENT_TOOLS = {
    "video_editing":   ["CapCut (free)", "DaVinci Resolve (free)", "Clipper (this repo)"],
    "ai_voiceover":    ["ElevenLabs", "Play.ht", "Murf.ai"],
    "b_roll_sources":  ["Pexels", "Pixabay", "Coverr", "Mixkit"],
    "music":           ["TikTok Sounds", "YouTube Audio Library", "Epidemic Sound"],
    "graphics":        ["Canva", "Adobe Express", "Figma"],
    "thumbnail":       ["Canva", "Photoshop", "Snappa"],
    "scheduling":      ["Buffer (free)", "Later", "Publer"],
    "analytics":       ["TikTok Analytics", "YouTube Studio", "Social Blade"],
    "trend_research":  ["social-trends CLI (this tool)", "Google Trends", "TrendTok"],
}


def get_niche_list(difficulty: Optional[str] = None) -> list[dict]:
    """Return all profitable niches, optionally filtered by difficulty."""
    if difficulty:
        return [n for n in PROFITABLE_NICHES if n["difficulty"].lower() == difficulty.lower()]
    return PROFITABLE_NICHES


def get_niche_info(niche_name: str) -> dict:
    """Return info for a specific niche (case-insensitive partial match)."""
    needle = niche_name.lower()
    for n in PROFITABLE_NICHES:
        if needle in n["niche"].lower():
            return n
    raise ValueError(f"Niche '{niche_name}' not found. Run 'theme-page niches' to list all.")


def get_conversion_playbook(phase: Optional[int] = None) -> list[dict]:
    """Return the full conversion playbook or a single phase."""
    if phase is not None:
        idx = phase - 1
        if 0 <= idx < len(CONVERSION_PLAYBOOK):
            return [CONVERSION_PLAYBOOK[idx]]
        raise ValueError(f"Phase must be 1–{len(CONVERSION_PLAYBOOK)}")
    return CONVERSION_PLAYBOOK


def get_content_pillars() -> dict:
    return {
        "pillars": CONTENT_PILLARS,
        "recommended_ratio_pct": CONTENT_RATIO,
    }


def get_monetization_thresholds() -> dict:
    return MONETIZATION_THRESHOLDS


def get_tools() -> dict:
    return FACELESS_CONTENT_TOOLS


def build_launch_checklist(niche: str, platforms: list[str]) -> dict:
    """Generate a personalized launch checklist for a given niche and platform set."""
    try:
        niche_data = get_niche_info(niche)
    except ValueError:
        niche_data = {"niche": niche, "content_type": "", "monetization": [], "avg_rpm": "unknown"}

    tasks = []
    tasks.append(f"Register handle @{niche.lower().replace(' ', '')} on: {', '.join(platforms)}")
    tasks.append("Create branded profile picture and banner (1500×500 for YouTube/Twitter)")
    tasks.append(f"Write keyword-optimized bio mentioning: '{niche_data['niche']}'")
    tasks.append("Set up link-in-bio with affiliate links and lead magnet")
    tasks.append("Install social-trends CLI and run: social-trends trends fetch tiktok")
    tasks.append("Identify 5 top competitors and study their top 10 videos")
    tasks.append("Build a swipe file of 20 hooks from viral videos in your niche")
    tasks.append("Batch-create 15 pieces of content before publishing anything")
    tasks.append(f"Identify monetization path: {', '.join(niche_data.get('monetization', ['Brand deals']))}")
    tasks.append("Schedule first 2 weeks of content in advance")

    return {
        "niche": niche_data["niche"],
        "platforms": platforms,
        "content_type": niche_data.get("content_type", ""),
        "estimated_rpm": niche_data.get("avg_rpm", "unknown"),
        "checklist": tasks,
        "content_pillars": CONTENT_PILLARS,
        "tools": FACELESS_CONTENT_TOOLS,
    }
