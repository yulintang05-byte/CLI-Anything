"""Account optimization engine — profile, posting schedule, and content strategy."""

from datetime import datetime, timezone
from typing import Optional


# Optimal posting windows by platform (UTC hour ranges, ranked by engagement)
POSTING_WINDOWS = {
    "tiktok": [
        {"days": ["Tue", "Thu", "Fri"], "hours_utc": [13, 14, 15], "label": "Peak — Lunch"},
        {"days": ["Mon", "Wed"], "hours_utc": [18, 19, 20], "label": "Peak — Evening"},
        {"days": ["Sat", "Sun"], "hours_utc": [9, 10, 11], "label": "Good — Weekend Morning"},
    ],
    "youtube_shorts": [
        {"days": ["Mon", "Wed", "Fri"], "hours_utc": [15, 16, 17], "label": "Peak — Afternoon"},
        {"days": ["Sat", "Sun"], "hours_utc": [11, 12, 13], "label": "Good — Weekend Midday"},
    ],
    "instagram_reels": [
        {"days": ["Mon", "Tue", "Fri"], "hours_utc": [11, 12, 13], "label": "Peak — Midday"},
        {"days": ["Wed", "Thu"], "hours_utc": [18, 19], "label": "Peak — Evening"},
    ],
    "youtube": [
        {"days": ["Thu", "Fri", "Sat"], "hours_utc": [16, 17, 18], "label": "Peak — Afternoon/Eve"},
        {"days": ["Mon", "Tue"], "hours_utc": [14, 15], "label": "Solid — Afternoon"},
    ],
}

# Niche-specific optimal posting frequencies
POSTING_FREQUENCY = {
    "theme_page":       {"tiktok": 3, "youtube_shorts": 2, "instagram_reels": 2, "note": "3-5 posts/day max"},
    "personal_brand":   {"tiktok": 1, "youtube_shorts": 1, "instagram_reels": 1, "note": "Quality > Quantity"},
    "entertainment":    {"tiktok": 3, "youtube_shorts": 3, "instagram_reels": 2, "note": "Consistency is key"},
    "educational":      {"tiktok": 1, "youtube_shorts": 1, "instagram_reels": 1, "note": "High-value content"},
    "news":             {"tiktok": 5, "youtube_shorts": 3, "instagram_reels": 2, "note": "Trend speed matters"},
    "fitness":          {"tiktok": 2, "youtube_shorts": 1, "instagram_reels": 1, "note": "Routine builds trust"},
    "finance":          {"tiktok": 1, "youtube_shorts": 1, "instagram_reels": 1, "note": "Trust > Volume"},
    "fashion":          {"tiktok": 2, "youtube_shorts": 1, "instagram_reels": 2, "note": "Visual consistency"},
}

BIO_TEMPLATES = {
    "theme_page": (
        "{emoji} {niche} content daily\n"
        "📲 Follow for {benefit}\n"
        "👇 DM for collabs\n"
        "{cta_link}"
    ),
    "personal_brand": (
        "{emoji} {role} | {value_prop}\n"
        "📍 {location}\n"
        "🔗 {cta_link}"
    ),
    "entertainment": (
        "{emoji} {content_type} every day\n"
        "🔔 Turn on notifications\n"
        "↓ New video below"
    ),
    "educational": (
        "Teaching {niche} for free 📚\n"
        "💡 {videos_count}+ tips & tricks\n"
        "👇 Start learning here\n"
        "{cta_link}"
    ),
}

PROFILE_CHECKLIST = [
    {"item": "Profile picture", "tip": "High-contrast, recognizable at 40×40px. No text. Face or bold logo."},
    {"item": "Username", "tip": "Short, memorable, searchable. Include niche keyword if possible."},
    {"item": "Display name", "tip": "Include 1 keyword for SEO (e.g., 'Finance Tips | John'). Under 30 chars."},
    {"item": "Bio", "tip": "State what you do + who it's for + CTA. 3 lines max. Add link-in-bio tool."},
    {"item": "Link in bio", "tip": "Use Linktree/Beacons/Stan Store. Include: lead magnet, main offer, socials."},
    {"item": "Pinned posts", "tip": "Pin 3 best-performing posts. First pin = best hook. Shows new visitors your value."},
    {"item": "Highlights (Instagram)", "tip": "Name them benefits not categories. 'Get Rich' > 'Finance Tips'."},
    {"item": "Banner/header", "tip": "State your value proposition in 5 words. Include profile picture echo."},
]

HASHTAG_STRATEGY = {
    "tiktok": {
        "total_recommended": "5-7",
        "structure": [
            "1-2 niche-specific (small, 10K–500K views)",
            "2-3 mid-tier (500K–5M views)",
            "1-2 viral/broad (#fyp, #viral, #foryoupage)",
        ],
        "avoid": ["Using the same set every post", "Banned/flagged hashtags", "Irrelevant hashtags"],
        "tip": "Rotate your hashtag sets. TikTok's algorithm rewards diversity.",
    },
    "youtube": {
        "total_recommended": "3-5 in title, 5-10 in description",
        "structure": [
            "1 primary keyword hashtag in title",
            "2-3 niche hashtags in description",
            "2-3 broad discovery hashtags",
        ],
        "tip": "YouTube hashtags show above title. First 3 tags shown = make them count.",
    },
    "instagram": {
        "total_recommended": "10-15 for Reels",
        "structure": [
            "3-5 niche (under 500K posts)",
            "3-5 mid-tier (500K–2M posts)",
            "3-5 broad-viral",
        ],
        "tip": "Put hashtags in caption (not comments) for Reels. Instagram confirmed caption placement works better.",
    },
}


def generate_profile_audit(
    platform: str,
    account_type: str = "theme_page",
    niche: str = "",
    current_bio: str = "",
) -> dict:
    """Generate a full profile optimization audit."""
    plat = platform.lower()
    acct = account_type.lower().replace(" ", "_")

    freq = POSTING_FREQUENCY.get(acct, POSTING_FREQUENCY["theme_page"])
    windows = POSTING_WINDOWS.get(plat, POSTING_WINDOWS.get("tiktok", []))
    bio_template = BIO_TEMPLATES.get(acct, BIO_TEMPLATES["theme_page"])
    hash_strat = HASHTAG_STRATEGY.get(plat, HASHTAG_STRATEGY["tiktok"])

    issues = []
    if current_bio and len(current_bio) > 150:
        issues.append("Bio too long — cut to 3 lines. Viewers skim, not read.")
    if current_bio and "http" not in current_bio.lower():
        issues.append("No link in bio detected — add a link-in-bio tool immediately.")
    if not niche:
        issues.append("Niche not defined — pick ONE clear topic. Algorithms reward specificity.")

    return {
        "platform": platform,
        "account_type": account_type,
        "niche": niche or "Not specified",
        "audit_date": datetime.now(timezone.utc).isoformat(),
        "profile_checklist": PROFILE_CHECKLIST,
        "bio_issues": issues,
        "bio_template": bio_template,
        "posting_schedule": {
            "recommended_per_day": freq.get(plat, 1),
            "note": freq.get("note", ""),
            "best_windows": windows[:3],
        },
        "hashtag_strategy": hash_strat,
        "quick_wins": [
            "Respond to every comment for first 30 min after posting — boosts algorithmic push",
            "Use trending sounds within 48h of them going viral for maximum reach",
            "First 1-3 seconds of video are critical — hook immediately, no slow intros",
            "Post consistently for 30 days before judging performance",
            "Engage with 10 accounts in your niche before posting each day",
        ],
    }


def generate_content_calendar(
    niche: str,
    platforms: list[str],
    days: int = 7,
    trending_hashtags: Optional[list[dict]] = None,
    trending_music: Optional[list[dict]] = None,
) -> dict:
    """Generate a weekly content calendar based on trends and niche."""
    hashtags = trending_hashtags or []
    music = trending_music or []

    top_tags = [h["tag"] for h in hashtags[:5]]
    top_sounds = [f"{m.get('artist','?')} - {m.get('track','?')}" for m in music[:3]]

    content_types = [
        "Trending hook reel/short",
        "Educational tip (saves = reach)",
        "Behind-the-scenes / relatable",
        "Trending sound + niche overlay",
        "User comment reply video",
        "Product/collab/CTA post",
        "Repurpose best-performing post",
    ]

    calendar = []
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for i in range(min(days, 7)):
        day = day_names[i % 7]
        content_type = content_types[i % len(content_types)]
        suggested_tags = top_tags[i % len(top_tags) : i % len(top_tags) + 3] if top_tags else ["#fyp", "#viral"]
        sound = top_sounds[i % len(top_sounds)] if top_sounds else "Trending sound of the week"

        calendar.append({
            "day": day,
            "content_type": content_type,
            "niche_angle": f"{niche} — {content_type.lower()}",
            "suggested_hashtags": suggested_tags + ["#fyp", f"#{niche.replace(' ', '')}"],
            "suggested_sound": sound,
            "platforms": platforms,
            "notes": f"Post at peak time. Engage for 30 min after. Reply to comments fast.",
        })

    return {
        "niche": niche,
        "platforms": platforms,
        "week_calendar": calendar,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repurposing_tip": (
            "Every piece of content should live on 3+ platforms. "
            "TikTok → YouTube Shorts → Instagram Reels. "
            "Remove TikTok watermark before cross-posting (use CapCut or Canva)."
        ),
    }


def growth_hacks(platform: str, account_type: str = "theme_page") -> dict:
    """Return platform-specific growth hacks and proven tactics."""
    hacks = {
        "tiktok": [
            {
                "hack": "Follow-Unfollow 2.0",
                "detail": "Follow 50 accounts in niche, engage (like + comment), unfollow after 3 days. Drives profile visits.",
                "risk": "Low",
                "effort": "Medium",
            },
            {
                "hack": "Duet/Stitch Hijacking",
                "detail": "Duet or stitch viral videos in your niche and add your commentary. You piggyback their algorithm momentum.",
                "risk": "None",
                "effort": "Low",
            },
            {
                "hack": "Comment bait",
                "detail": "End every video with a controversial/open question. Comments × 10 > likes for the algorithm.",
                "risk": "None",
                "effort": "None",
            },
            {
                "hack": "Trend audio within 48h",
                "detail": "When a sound hits the 'trending' shelf use it IMMEDIATELY. The algo favors early adopters.",
                "risk": "None",
                "effort": "Low",
            },
            {
                "hack": "Series content",
                "detail": "Create multi-part series (Part 1, Part 2…). Hooks viewers to follow for the next part.",
                "risk": "None",
                "effort": "Medium",
            },
        ],
        "youtube": [
            {
                "hack": "Shorts-to-long pipeline",
                "detail": "Post a Short that teases your long-form video. CTA: 'Full video on channel.' Drives subs.",
                "risk": "None",
                "effort": "Low",
            },
            {
                "hack": "SEO thumbnail strategy",
                "detail": "Thumbnail + Title = the only click decision. A/B test thumbnails. Bold text, face emotion, contrast.",
                "risk": "None",
                "effort": "Medium",
            },
            {
                "hack": "End screen optimization",
                "detail": "Place end screen at 20s before end. Link best-performing video + subscribe button.",
                "risk": "None",
                "effort": "None",
            },
            {
                "hack": "Community tab polls",
                "detail": "Post polls asking what content to make next. Drives engagement + tells you what to create.",
                "risk": "None",
                "effort": "Low",
            },
        ],
        "instagram": [
            {
                "hack": "Collab posts",
                "detail": "Collab tag accounts in your niche. Post appears on BOTH profiles. Instant audience sharing.",
                "risk": "None",
                "effort": "Medium",
            },
            {
                "hack": "Story polls / questions",
                "detail": "Post polls daily. Every story interaction boosts your Reels reach.",
                "risk": "None",
                "effort": "Low",
            },
        ],
    }

    theme_page_extras = [
        {
            "hack": "Repost viral content fast",
            "detail": "Monitor TikTok/Reddit for viral content in your niche. Repost within 12h with credit. Theme pages thrive on curation.",
            "risk": "Low (credit creators)",
            "effort": "Low",
        },
        {
            "hack": "SFS (Shoutout for Shoutout)",
            "detail": "Partner with 3-5 theme pages in adjacent niches. Cross-shoutout = free audience overlap.",
            "risk": "None",
            "effort": "Medium",
        },
        {
            "hack": "Username SEO",
            "detail": "Change username to include your niche keyword. People search '[niche] page' on TikTok/IG.",
            "risk": "None",
            "effort": "None",
        },
    ]

    platform_hacks = hacks.get(platform.lower(), hacks["tiktok"])
    if "theme" in account_type.lower():
        platform_hacks = theme_page_extras + platform_hacks

    return {
        "platform": platform,
        "account_type": account_type,
        "growth_hacks": platform_hacks,
        "monetization_unlock_milestones": {
            "tiktok": "10K followers = LIVE gifts; 100K = Creator Fund; 1K followers + 10K views = TikTok Shop",
            "youtube": "1K subs + 4K watch hours = AdSense; 500 subs = Shorts monetization",
            "instagram": "No follower minimum for Creator Marketplace; 10K for link-in-stories (all accounts now)",
        },
    }
