"""TikTok trend analysis using public data and official Creative Center guidance."""

from cli_anything.social_trends.utils.social_backend import (
    tiktok_trending_hashtags_public,
    tiktok_trending_sounds_guide,
    _tiktok_static_fallback_hashtags,
)


def get_trending_hashtags(count: int = 30) -> dict:
    """Fetch trending TikTok hashtags from public data."""
    hashtags = tiktok_trending_hashtags_public(count=count)
    # Score and annotate
    scored = []
    for ht in hashtags:
        views = ht.get("views", 0)
        name = ht.get("name", "")
        viral_score = min(100, int(min(views / 1_000_000_000, 1) * 80 + min(len(name) / 20, 1) * 20))
        scored.append({
            "hashtag": f"#{name}",
            "views": views,
            "video_count": ht.get("video_count", 0),
            "viral_score": viral_score,
            "note": ht.get("note", ""),
        })
    scored.sort(key=lambda x: x["viral_score"], reverse=True)
    return {
        "source": "TikTok public discover",
        "total": len(scored),
        "hashtags": scored,
        "strategy": (
            "Stack 3-5 niche hashtags + 1-2 mega tags (#fyp, #viral). "
            "Post within 2 hours of a trend appearing for maximum reach."
        ),
    }


def get_trending_sounds() -> dict:
    """Return a guide for finding trending TikTok sounds and music."""
    sources = tiktok_trending_sounds_guide()
    return {
        "overview": (
            "Trending sounds are TikTok's #1 distribution signal. "
            "Videos using a trending sound in its first 24-72 hours of virality "
            "receive 3-10x more FYP distribution than non-trending sounds."
        ),
        "finding_trending_sounds": sources,
        "sound_strategy": [
            {
                "tactic": "Early Adopter Boost",
                "description": (
                    "Check TikTok's Discover page every morning. "
                    "Use any sound with rapid view growth (10K→100K+ in <24h). "
                    "Being early amplifies algorithmic push."
                ),
            },
            {
                "tactic": "Sound Recycling",
                "description": (
                    "Sounds that went viral 3-6 months ago often resurface. "
                    "Search for a sound in TikTok and sort by 'Most Recent' — "
                    "a new wave of creators using it signals a comeback trend."
                ),
            },
            {
                "tactic": "Niche Sound Stacking",
                "description": (
                    "Use the most popular sound IN YOUR NICHE rather than the overall #1. "
                    "A niche sound with 500K videos sends your content to the right audience, "
                    "not a general mega-sound with 10M videos where you get lost."
                ),
            },
            {
                "tactic": "Original Audio Strategy",
                "description": (
                    "Record a catchy hook or phrase and upload original audio. "
                    "If it goes viral and others use your sound, you get promoted "
                    "every time someone else uses it."
                ),
            },
        ],
        "music_rights": (
            "IMPORTANT: For commercial accounts, only use TikTok's Commercial Music Library "
            "(available in TikTok Sound settings). Personal accounts can use any sound, "
            "but commercial/business accounts are restricted to avoid copyright strikes."
        ),
    }


def account_checklist() -> dict:
    """Return a TikTok account optimization checklist."""
    return {
        "profile_optimization": [
            {"item": "Username", "tip": "Use niche keywords (e.g. @dailyfinancetips). Keep it ≤15 chars. No underscores."},
            {"item": "Profile Photo", "tip": "High-contrast image visible at 150x150px. Avoid text. Faces outperform logos."},
            {"item": "Bio", "tip": "3 lines max. Line 1: Who you help. Line 2: What you post. Line 3: CTA with emoji."},
            {"item": "Link in Bio", "tip": "Use Beacons.ai or Linktree to host affiliate links, lead magnets, products."},
            {"item": "Account Type", "tip": "Switch to Creator Account for analytics, sound access, and creator tools."},
            {"item": "Pinned Videos", "tip": "Pin your 3 best-performing or most representative videos at top of profile."},
        ],
        "content_optimization": [
            {"item": "Hook (0-2s)", "tip": "Open with a bold visual or text hook. Curiosity gap or bold claim works best."},
            {"item": "Video Length", "tip": "7-15s for pure entertainment, 30-60s for tutorials, 2-3min for storytelling."},
            {"item": "Captions", "tip": "Add text captions — 80% of TikTok is watched without sound."},
            {"item": "Trending Sound", "tip": "Use a trending sound every post. Check 'Sounds' in TikTok Creator Center."},
            {"item": "Hashtags", "tip": "3-5 niche hashtags + #fyp + 1 community tag. Put them in caption, not comments."},
            {"item": "Posting Time", "tip": "Best: 6-10 AM and 7-9 PM local to YOUR target audience's timezone."},
            {"item": "Frequency", "tip": "Minimum 1x/day for growth. 2-3x/day in first 30 days for algorithm favor."},
            {"item": "Reply with Video", "tip": "Reply to top comments with a video reply — doubles content output."},
        ],
        "engagement_tactics": [
            {"item": "Golden Hour", "tip": "Respond to ALL comments in first 30 minutes post goes live."},
            {"item": "Comment Seeding", "tip": "Leave meaningful comments on viral posts in your niche — drives profile visits."},
            {"item": "Duet/Stitch", "tip": "Duet or Stitch a viral video in your niche — borrows their algorithm momentum."},
            {"item": "Live Sessions", "tip": "Go Live 2-3x/week for 30+ minutes. Lives boost overall account reach."},
        ],
        "analytics_targets": {
            "view_rate": "Aim for >50% of followers watching past 3 seconds",
            "completion_rate": "Target 30%+ video completion (shorter videos help)",
            "profile_visit_rate": "1%+ of viewers visiting your profile",
            "follow_rate": "5%+ of profile visitors following",
            "engagement_rate": "5-15% (likes+comments+shares / views)",
        },
    }


def content_calendar(niche: str = "general", posts_per_day: int = 2) -> dict:
    """Generate a 7-day TikTok content calendar for a niche."""
    templates = {
        "general": [
            "POV: [Relatable situation in your niche]",
            "Things nobody tells you about [topic]",
            "[Number] signs you're doing [thing] wrong",
            "Watch me [demonstrate skill/result]",
            "The truth about [common misconception]",
            "Day in the life of [your niche persona]",
            "Before vs After [transformation in niche]",
        ],
        "finance": [
            "How I turned $[X] into $[Y] in [timeframe]",
            "[Number] money habits that changed my life",
            "This one finance mistake is costing you $[X]/year",
            "Rich people do THIS with their money",
            "The $0 budget hack that actually works",
            "Investing mistake I made so you don't have to",
            "How to make money while you sleep (realistically)",
        ],
        "fitness": [
            "[X]-day transformation (no equipment)",
            "Why you're not losing weight (the real reason)",
            "This 5-min morning routine changed everything",
            "Foods that burn fat while you sleep",
            "Gym intimidation? Watch this first",
            "What I eat in a day to stay lean",
            "The workout mistake most beginners make",
        ],
        "motivation": [
            "If you're struggling, watch this",
            "[Quote] — this hit different",
            "One year from now you'll wish you started today",
            "The mindset shift that changed everything",
            "Stop doing this if you want to succeed",
            "What successful people do differently",
            "Hard truth nobody wants to hear about [topic]",
        ],
    }

    niche_key = niche.lower() if niche.lower() in templates else "general"
    content_templates = templates[niche_key]

    calendar = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for i, day in enumerate(days):
        day_posts = []
        for j in range(posts_per_day):
            template_idx = (i * posts_per_day + j) % len(content_templates)
            day_posts.append({
                "post_number": j + 1,
                "template": content_templates[template_idx],
                "sound_tip": "Use a trending sound from the last 24h",
                "hashtags": f"#fyp #viral #{niche_key} #foryou",
                "best_time": "7:00 AM" if j == 0 else "7:00 PM",
            })
        calendar.append({"day": day, "posts": day_posts})

    return {
        "niche": niche,
        "posts_per_day": posts_per_day,
        "weekly_total": len(days) * posts_per_day,
        "calendar": calendar,
        "pro_tip": (
            "Batch-create all 7 days of content in one 2-3 hour session. "
            "Use TikTok's built-in scheduler (or Buffer) to auto-post at optimal times."
        ),
    }
