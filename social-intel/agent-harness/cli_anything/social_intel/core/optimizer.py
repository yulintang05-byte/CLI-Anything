"""Account optimization engine.

Generates platform-specific optimization reports covering:
- Bio structure and CTAs
- Posting cadence and best times
- Content-mix ratios
- Hashtag strategy (size, mix, placement)
- Profile completeness checklist
- Hook formula recommendations
- Theme page monetization paths
"""

from datetime import datetime

BEST_TIMES = {
    "tiktok": {
        "Monday":    ["6:00", "10:00", "22:00"],
        "Tuesday":   ["2:00", "4:00", "9:00"],
        "Wednesday": ["7:00", "8:00", "23:00"],
        "Thursday":  ["9:00", "12:00", "19:00"],
        "Friday":    ["5:00", "13:00", "15:00"],
        "Saturday":  ["11:00", "19:00", "20:00"],
        "Sunday":    ["7:00", "8:00", "16:00"],
    },
    "youtube_shorts": {
        "Monday":    ["14:00", "17:00"],
        "Tuesday":   ["14:00", "17:00"],
        "Wednesday": ["14:00", "17:00"],
        "Thursday":  ["14:00", "17:00"],
        "Friday":    ["14:00", "17:00"],
        "Saturday":  ["9:00", "11:00"],
        "Sunday":    ["9:00", "11:00"],
    },
    "instagram_reels": {
        "Monday":    ["11:00", "14:00"],
        "Tuesday":   ["10:00", "14:00"],
        "Wednesday": ["11:00", "15:00"],
        "Thursday":  ["11:00", "15:00"],
        "Friday":    ["11:00", "14:00"],
        "Saturday":  ["10:00", "13:00"],
        "Sunday":    ["10:00", "13:00"],
    },
}

HASHTAG_STRATEGY = {
    "tiktok": {
        "total_tags": "3–5 (TikTok penalizes hashtag spam)",
        "size_mix": {
            "mega": "1 tag  (>1B views) — discoverability anchor",
            "large": "1 tag  (100M–1B views) — broad reach",
            "medium": "1 tag  (10M–100M views) — niche reach",
            "small": "1–2 tags (<10M views) — highest conversion",
        },
        "placement": "Caption, NOT comments",
        "must_include": ["#fyp", "#foryou", "#viral"],
        "avoid": "Banned/shadowbanned tags — check via social-intel tiktok hashtag <tag>",
    },
    "youtube_shorts": {
        "total_tags": "3–5 hashtags in description (first 3 show under title)",
        "size_mix": "Mix of niche-specific and broad trending tags",
        "placement": "First 3 lines of description",
        "must_include": ["#Shorts", "#YouTubeShorts"],
        "avoid": "Keyword stuffing — YouTube's algorithm deprioritizes it",
    },
    "instagram_reels": {
        "total_tags": "5–10 (sweet spot; 30 max but quality > quantity)",
        "size_mix": {
            "small": "3–4 tags (<50K posts) — highest chance of Top Posts",
            "medium": "3–4 tags (50K–500K posts)",
            "large": "2–3 tags (500K–1M posts)",
        },
        "placement": "Caption OR first comment (both work equally well)",
        "must_include": ["#reels", "#reelsinstagram"],
    },
}

HOOK_FORMULAS = [
    {
        "name": "Pattern Interrupt",
        "template": "Wait— [unexpected fact/statement]",
        "example": "Wait— most people post at the WRONG time and wonder why views tank",
        "best_for": ["tiktok", "reels"],
    },
    {
        "name": "Curiosity Gap",
        "template": "Here's the [adjective] thing about [topic] nobody talks about",
        "example": "Here's the dark thing about viral hashtags nobody talks about",
        "best_for": ["tiktok", "youtube_shorts", "reels"],
    },
    {
        "name": "Result Promise",
        "template": "How I [achieved result] in [timeframe] (step by step)",
        "example": "How I grew from 0 to 10K followers in 30 days (step by step)",
        "best_for": ["youtube_shorts", "reels"],
    },
    {
        "name": "Controversy Bait",
        "template": "[Popular belief] is actually [wrong/right] — here's why",
        "example": "Posting every day is actually HURTING your growth — here's why",
        "best_for": ["tiktok", "youtube_shorts"],
    },
    {
        "name": "Relatable Pain",
        "template": "If you [relatable situation], this is for you",
        "example": "If you've been posting for months with zero views, this is for you",
        "best_for": ["tiktok", "reels"],
    },
    {
        "name": "Number Hook",
        "template": "[Number] [platform] hacks most people don't know",
        "example": "5 TikTok hacks that will 10x your views overnight",
        "best_for": ["youtube_shorts", "reels", "tiktok"],
    },
]

BIO_TEMPLATE = {
    "tiktok": {
        "line_1": "What you do / niche keyword (searchable)",
        "line_2": "Who you help OR your unique angle",
        "line_3": "Social proof or credibility (10K+ sold / featured in X)",
        "line_4": "CTA — link in bio / DM me / join free [X]",
        "emoji_use": "1–2 max; use to replace filler words",
        "link": "One link only — use Linktree/Stan Store to house multiple destinations",
    },
    "youtube": {
        "channel_description": "First 200 chars are visible in search — lead with niche + value prop",
        "keywords": "Add 10–15 channel tags in YouTube Studio > Customization > Basic info",
        "watermark": "Add a subscribe watermark in Branding tab",
        "banner_cta": "Put upload schedule in channel art banner",
    },
    "instagram": {
        "name_field": "Include niche keyword here (searchable, not just your name)",
        "bio_lines": [
            "Line 1: What you do (keyword-rich)",
            "Line 2: For whom / results you deliver",
            "Line 3: Social proof",
            "Line 4: CTA + link",
        ],
        "category": "Set a business category in Edit Profile — boosts discoverability",
        "highlights": "Organize highlights as: FAQ / Reviews / Products / How it Works",
    },
}


def generate_report(platform: str, niche: str = "") -> dict:
    """Generate a full account optimization report for a platform.

    Args:
        platform: tiktok | youtube | youtube_shorts | instagram | instagram_reels.
        niche: Your content niche for personalized hashtag suggestions.

    Returns:
        Full optimization report dict.
    """
    platform_key = platform.lower().replace(" ", "_").replace("-", "_")

    # Normalize common aliases
    alias_map = {
        "yt": "youtube",
        "yt_shorts": "youtube_shorts",
        "shorts": "youtube_shorts",
        "ig": "instagram",
        "ig_reels": "instagram_reels",
        "tt": "tiktok",
    }
    platform_key = alias_map.get(platform_key, platform_key)

    times_key = platform_key if platform_key in BEST_TIMES else "tiktok"
    hashtag_key = platform_key if platform_key in HASHTAG_STRATEGY else "tiktok"
    bio_key = "tiktok" if "tiktok" in platform_key else (
        "youtube" if "youtube" in platform_key else "instagram"
    )

    report = {
        "platform": platform_key,
        "niche": niche or "general",
        "generated_at": datetime.utcnow().isoformat(),
        "best_posting_times_utc": BEST_TIMES.get(times_key, BEST_TIMES["tiktok"]),
        "posting_cadence": _posting_cadence(platform_key),
        "hashtag_strategy": HASHTAG_STRATEGY.get(hashtag_key, HASHTAG_STRATEGY["tiktok"]),
        "hook_formulas": HOOK_FORMULAS,
        "bio_optimization": BIO_TEMPLATE.get(bio_key, BIO_TEMPLATE["tiktok"]),
        "content_mix": _content_mix(platform_key),
        "profile_checklist": _checklist(platform_key),
        "growth_levers": _growth_levers(platform_key),
    }
    return report


def _posting_cadence(platform: str) -> dict:
    cadence = {
        "tiktok": {
            "minimum": "1x/day",
            "recommended": "2–3x/day",
            "rationale": "TikTok's algorithm rewards consistency; more shots at virality",
            "gap_between_posts": "At least 1–2 hours so posts don't cannibalize each other",
        },
        "youtube_shorts": {
            "minimum": "3x/week",
            "recommended": "1x/day",
            "rationale": "Shorts feed is discovery-driven; volume increases surface area",
            "gap_between_posts": "At least 4 hours",
        },
        "instagram_reels": {
            "minimum": "3–4x/week",
            "recommended": "5–7x/week",
            "rationale": "Reels get 22% more interaction than regular posts on average",
            "gap_between_posts": "At least 3 hours",
        },
        "instagram": {
            "minimum": "3x/week",
            "recommended": "5x/week",
            "rationale": "Mix Reels (reach) with carousels (saves/shares) and stories (retention)",
        },
        "youtube": {
            "minimum": "1x/week",
            "recommended": "2x/week",
            "rationale": "Consistency matters more than frequency; subscriber expectations",
        },
    }
    return cadence.get(platform, cadence["tiktok"])


def _content_mix(platform: str) -> dict:
    mixes = {
        "tiktok": {
            "viral_hooks_trends": "40% — ride trending sounds/challenges for new reach",
            "educational_value": "30% — builds authority and saves",
            "behind_scenes_personal": "20% — builds parasocial connection",
            "promotional_cta": "10% — sell, promote, or redirect",
        },
        "youtube_shorts": {
            "trending_clips": "30%",
            "tutorials_howto": "40%",
            "entertainment": "20%",
            "promotional": "10%",
        },
        "instagram_reels": {
            "trending_audio_content": "35%",
            "value_carousels": "30%",
            "personal_brand": "25%",
            "promotional": "10%",
        },
    }
    key = platform if platform in mixes else "tiktok"
    return mixes[key]


def _checklist(platform: str) -> list[dict]:
    common = [
        {"item": "Profile photo — high-contrast, face-forward or clear logo", "priority": "high"},
        {"item": "Username — short, memorable, niche-relevant, same across all platforms", "priority": "high"},
        {"item": "Bio optimized with niche keyword + CTA", "priority": "high"},
        {"item": "Link in bio set up (Linktree, Stan Store, or Beacons)", "priority": "high"},
        {"item": "At least 9 posts before aggressive growth push", "priority": "medium"},
        {"item": "Consistent visual aesthetic / color palette", "priority": "medium"},
    ]
    platform_specific = {
        "tiktok": [
            {"item": "TikTok LIVE access enabled (requires 1K followers)", "priority": "medium"},
            {"item": "Creator tools enabled in settings", "priority": "low"},
            {"item": "Series / playlist feature used for multi-part content", "priority": "low"},
        ],
        "youtube": [
            {"item": "Channel verified (phone number)", "priority": "high"},
            {"item": "Custom URL set (requires 100 subscribers)", "priority": "medium"},
            {"item": "End screens added to all videos (final 20 seconds)", "priority": "high"},
            {"item": "Info cards added at key moments", "priority": "medium"},
            {"item": "Chapters added to video descriptions", "priority": "low"},
            {"item": "Thumbnails A/B tested (YouTube Studio analytics)", "priority": "high"},
        ],
        "instagram": [
            {"item": "Professional account (Creator or Business)", "priority": "high"},
            {"item": "Contact info added", "priority": "medium"},
            {"item": "Story highlights organized (4–6 categories)", "priority": "medium"},
            {"item": "Instagram Shop set up (if selling products)", "priority": "low"},
        ],
    }
    base_key = "tiktok" if "tiktok" in platform else (
        "youtube" if "youtube" in platform else "instagram"
    )
    return common + platform_specific.get(base_key, [])


def _growth_levers(platform: str) -> list[dict]:
    return [
        {
            "lever": "Reply to every comment in first 30 minutes",
            "impact": "high",
            "reason": "Boosts engagement signals that trigger algorithmic distribution",
        },
        {
            "lever": "Post when your audience is ONLINE (check analytics)",
            "impact": "high",
            "reason": "Early engagement velocity determines whether the algorithm pushes your content",
        },
        {
            "lever": "Use trending audio (TikTok/Reels) or trending topics (YouTube)",
            "impact": "high",
            "reason": "Algorithm promotes content using trending sounds to wider audiences",
        },
        {
            "lever": "Cross-post across platforms (TikTok → Reels → Shorts)",
            "impact": "medium",
            "reason": "3x reach from single content piece; remove watermarks before cross-posting",
        },
        {
            "lever": "Collaborate via duets, stitches, or collabs",
            "impact": "medium",
            "reason": "Borrow audience trust from established creators in your niche",
        },
        {
            "lever": "Pin your best 3 posts to profile",
            "impact": "medium",
            "reason": "First impression determines follow rate of profile visitors",
        },
        {
            "lever": "Hook in first 1–3 seconds (pattern interrupt)",
            "impact": "very_high",
            "reason": "Completion rate and rewatch rate are the #1 signals on all platforms",
        },
        {
            "lever": "Ask a question in your caption or at video end",
            "impact": "medium",
            "reason": "Comments signal content quality; higher comment count = more distribution",
        },
    ]
