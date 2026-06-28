"""Account optimization recommendations for YouTube, TikTok, and Instagram."""

from cli_anything.social_trends.utils.social_backend import (
    yt_channel_stats,
    yt_trending_videos,
)


POSTING_SCHEDULES = {
    "tiktok": {
        "best_days": ["Tuesday", "Thursday", "Friday"],
        "best_times_utc": {
            "morning": "06:00-09:00 UTC",
            "evening": "19:00-21:00 UTC",
        },
        "frequency": {
            "growth_phase": "2-3 posts/day for first 30 days",
            "maintenance": "1 post/day minimum",
            "scaling": "3-5 posts/day when testing new content formats",
        },
        "note": "Adjust UTC times to match your TARGET AUDIENCE's timezone, not your own.",
    },
    "youtube": {
        "best_days": ["Wednesday", "Thursday", "Friday", "Saturday"],
        "best_times_utc": {
            "morning": "14:00-16:00 UTC (morning US East Coast)",
            "evening": "21:00-23:00 UTC (evening US East Coast)",
        },
        "frequency": {
            "growth_phase": "2-3 videos/week (long-form) + daily Shorts",
            "maintenance": "1 video/week (long-form) + 3-5 Shorts/week",
            "scaling": "Add community posts and YouTube Stories between uploads",
        },
        "note": "YouTube Shorts get separate algorithm distribution from long-form. Post both independently.",
    },
    "instagram": {
        "best_days": ["Monday", "Wednesday", "Friday"],
        "best_times_utc": {
            "morning": "09:00-11:00 UTC",
            "afternoon": "14:00-16:00 UTC",
            "evening": "19:00-21:00 UTC",
        },
        "frequency": {
            "growth_phase": "1 Reel/day + 2 Stories/day",
            "maintenance": "3-5 Reels/week + daily Stories",
            "scaling": "Add Carousels and Guides for saves (saves = best signal for Explore)",
        },
        "note": "Instagram Reels cross-post to Facebook automatically — double distribution for free.",
    },
}


CONTENT_MIX_FORMULA = {
    "tiktok": {
        "trend_riding": {"percentage": 40, "description": "Content using current trending sounds/formats"},
        "original_value": {"percentage": 40, "description": "Your core niche value content (tips, tutorials, info)"},
        "personality": {"percentage": 20, "description": "Behind-the-scenes, personal moments, community engagement"},
    },
    "youtube": {
        "evergreen_seo": {"percentage": 50, "description": "Keyword-optimized long-form content (search discovery)"},
        "trend_response": {"percentage": 30, "description": "Topical content responding to current trends/news in niche"},
        "community": {"percentage": 20, "description": "Vlogs, Q&As, community polls, Shorts repurposing long-form"},
    },
    "instagram": {
        "reels": {"percentage": 50, "description": "Short-form video (max reach)"},
        "carousels": {"percentage": 30, "description": "Multi-image posts (highest save rate = Explore push)"},
        "stories": {"percentage": 20, "description": "Daily engagement, polls, questions, behind-scenes"},
    },
}


def get_posting_schedule(platform: str = "all") -> dict:
    """Return optimized posting schedule for a platform."""
    if platform == "all":
        return {"platforms": POSTING_SCHEDULES}

    platform_key = platform.lower()
    if platform_key not in POSTING_SCHEDULES:
        raise ValueError(f"Platform '{platform}' not found. Options: {list(POSTING_SCHEDULES.keys())}, 'all'")

    return {
        "platform": platform,
        "schedule": POSTING_SCHEDULES[platform_key],
        "content_mix": CONTENT_MIX_FORMULA.get(platform_key, {}),
    }


def get_content_mix(platform: str = "tiktok") -> dict:
    """Return recommended content type mix for a platform."""
    platform_key = platform.lower()
    if platform_key not in CONTENT_MIX_FORMULA:
        raise ValueError(f"Platform '{platform}' not recognized. Options: {list(CONTENT_MIX_FORMULA.keys())}")

    mix = CONTENT_MIX_FORMULA[platform_key]
    return {
        "platform": platform,
        "content_mix": mix,
        "weekly_plan": _generate_weekly_mix(platform_key, mix),
        "tip": "The 40/40/20 or 50/30/20 mix prevents algorithm fatigue and builds a multi-dimensional audience.",
    }


def _generate_weekly_mix(platform: str, mix: dict) -> list:
    """Generate a 7-day content type distribution."""
    weekly = []
    total = sum(v["percentage"] for v in mix.values())
    categories = list(mix.items())

    for day_num in range(7):
        posts = []
        cat_idx = day_num % len(categories)
        cat_name, cat_data = categories[cat_idx]
        posts.append({
            "type": cat_name,
            "description": cat_data["description"],
        })
        if platform == "tiktok" and day_num in [1, 3, 5]:
            posts.append({
                "type": "bonus",
                "description": "Trend-response post (react to something going viral today)",
            })
        weekly.append({"day": day_num + 1, "posts": posts})
    return weekly


def audit_youtube_channel(channel_id: str) -> dict:
    """Full optimization audit for a YouTube channel."""
    from cli_anything.social_trends.core.youtube import channel_audit
    return channel_audit(channel_id)


def get_optimization_checklist(platform: str = "all") -> dict:
    """Return a complete optimization checklist for one or all platforms."""
    checklists = {
        "youtube": {
            "profile": [
                "Channel name includes niche keyword (e.g. 'John Finance' not 'John123')",
                "Channel art matches niche — consistent brand colors",
                "Profile picture: clear, professional, visible at 80x80px",
                "Channel description: 500+ chars, niche keywords in first 150 chars, links",
                "Channel keywords filled in (YouTube Studio > Customization > Basic Info)",
                "Featured video set (your best performing or trailer)",
                "Playlists created for content series (increases watch time 40-80%)",
                "Channel trailer enabled for non-subscribers",
                "End screens and cards added to all videos",
                "Shorts shelf created for short-form content",
            ],
            "video_seo": [
                "Title: 60 chars max, main keyword near start, curiosity gap included",
                "Description: 1000+ chars, keyword in first sentence, chapters timestamps, links",
                "Tags: 5-10 tags mixing broad + specific (not more than 10)",
                "Custom thumbnail: high contrast, face if possible, text <6 words",
                "Hashtags: 3 hashtags in description (first 3 appear above title)",
                "Category correctly selected",
                "Language and captions configured (auto-generated + edited)",
                "Cards linked to related videos at 20% and 70% of video duration",
            ],
            "engagement": [
                "Reply to comments within first 2 hours of posting",
                "Pin a comment with a question to boost comment engagement",
                "Post community post within 1h of video going live",
                "Cross-post Shorts version to Shorts shelf",
                "Share in relevant subreddits, Discord servers, Facebook groups",
            ],
        },
        "tiktok": {
            "profile": [
                "Username: niche keyword included, ≤15 chars, no underscores",
                "Bio: 3-line formula (Who → What → CTA), includes keyword",
                "Profile photo: high contrast, emotion-driven or niche-themed",
                "Link in bio: Beacons.ai or Linktree with affiliate links + lead magnet",
                "Creator account enabled (not Personal account)",
                "Pinned videos: 3 best performing or content-type examples",
                "TikTok LIVE configured (requires 1K followers)",
            ],
            "content": [
                "Hook in first 1-2 seconds (visual or text overlay)",
                "Trending sound used from last 24h",
                "Text captions added (auto-caption enabled or manual)",
                "Hashtags: 3-5 niche + #fyp in caption",
                "Posting time: 6-9 AM or 7-9 PM target audience timezone",
                "Call-to-action at end (follow, comment, share, link in bio)",
                "Video length optimized for content type (7-15s clips, 30-60s tutorials)",
            ],
            "growth": [
                "Respond to ALL comments in first 30 minutes",
                "Reply to top comments with video response",
                "Duet or Stitch 1 viral video per week in your niche",
                "Go LIVE 2-3x per week after reaching 1K followers",
                "Use TikTok Creator Center for trend research daily",
            ],
        },
        "instagram": {
            "profile": [
                "Username: searchable, niche keyword included",
                "Name field: keyword-rich (searchable in Instagram search)",
                "Bio: 150 chars, emoji bullets, CTA with link",
                "Profile photo: clear, branded, no text",
                "Business/Creator account enabled",
                "Category set (e.g. 'Digital Creator', 'Health/Beauty', 'Business')",
                "Contact info filled (email for brand deals)",
                "Story Highlights: 4-6 with custom covers aligned to brand",
                "Pinned Posts: 3 best-performing Reels pinned to grid top",
            ],
            "reels": [
                "First 3 seconds hook (no intro/logo)",
                "Trending audio from Instagram Reels trending section",
                "Cover image: custom thumbnail, not random frame",
                "Caption: 150-300 chars, call to action, 5-10 hashtags",
                "Location tag added (boosts local discovery 20-30%)",
                "Cross-share to Stories and Feed simultaneously",
            ],
        },
    }

    if platform == "all":
        return {"checklists": checklists}

    platform_key = platform.lower()
    if platform_key not in checklists:
        raise ValueError(f"Platform '{platform}' not found. Options: {list(checklists.keys())}, 'all'")

    return {
        "platform": platform,
        "checklist": checklists[platform_key],
        "total_items": sum(len(v) for v in checklists[platform_key].values()),
    }


def generate_growth_plan(platform: str = "tiktok", niche: str = "general",
                         current_followers: int = 0) -> dict:
    """Generate a 90-day growth plan tailored to platform, niche, and current size."""
    milestones = []

    if platform.lower() == "tiktok":
        milestones = [
            {
                "days": "1-30",
                "goal": "First 1,000 followers",
                "actions": [
                    f"Post 2-3 {niche} videos/day using trending sounds",
                    "Find 3 viral videos in your niche and create your version",
                    "Comment on 10 viral posts in your niche daily",
                    "Use 5-7 hashtags per post mixing mega + niche",
                    "Analyze analytics daily — double down on what gets most views",
                ],
                "kpi": "500+ average views per video",
            },
            {
                "days": "31-60",
                "goal": "First 5,000 followers & first affiliate sale",
                "actions": [
                    "Add affiliate link to Linktree in bio",
                    "Create 1 'value-bomb' video per week (high-save content)",
                    "Start 1 Duet or Stitch per week with viral niche content",
                    "Reply to EVERY comment for first 30 min after posting",
                    "Research your top 5 competitor accounts and analyze their top videos",
                ],
                "kpi": "5%+ engagement rate, 1+ affiliate sale",
            },
            {
                "days": "61-90",
                "goal": "10,000 followers & $500+ revenue",
                "actions": [
                    "Launch a free lead magnet (PDF guide, checklist) to build email list",
                    "Reach out to 3 small brands in your niche for paid shoutout",
                    "Start cross-posting to Instagram Reels and YouTube Shorts",
                    "Go LIVE 2x/week to deepen audience relationship",
                    "Create a digital product (eBook or template) — launch at 7,500+ followers",
                ],
                "kpi": "10K followers, email list 500+, $500+/month revenue",
            },
        ]
    elif platform.lower() == "youtube":
        milestones = [
            {
                "days": "1-30",
                "goal": "100 subscribers & 500 watch hours",
                "actions": [
                    f"Upload 3 long-form {niche} videos/week (keyword-researched titles)",
                    "Post 5 Shorts/week (repurpose long-form highlights)",
                    "Set up channel fully (keywords, trailer, playlists, end screens)",
                    "Use VidIQ or TubeBuddy free tier for keyword research",
                    "Engage in 3-5 YouTube comments on related videos daily",
                ],
                "kpi": "Average 200+ views per video, 5%+ CTR on thumbnails",
            },
            {
                "days": "31-60",
                "goal": "500 subscribers & 2,000 watch hours",
                "actions": [
                    "A/B test 2 different thumbnail styles across 4 videos",
                    "Analyze top 3 performing videos — create series around same topic",
                    "Add YouTube cards linking high-traffic videos to monetizable content",
                    "Create a channel trailer optimized for conversion",
                    "Respond to all comments to boost engagement signals",
                ],
                "kpi": "4,000 watch hours (50% of YPP minimum), 500+ subscribers",
            },
            {
                "days": "61-90",
                "goal": "1,000 subscribers & monetization eligible",
                "actions": [
                    "Apply for YouTube Partner Program (YPP) at 1K subs + 4K watch hours",
                    "Add affiliate links to video descriptions (Amazon, relevant products)",
                    "Cross-promote with 2-3 creators in your niche (collab or shoutout swap)",
                    "Launch merchandise store or digital product to email subscribers",
                    "Analyze Search Console data to find ranking opportunity keywords",
                ],
                "kpi": "YPP approval, first $100 AdSense, email list 200+",
            },
        ]

    return {
        "platform": platform,
        "niche": niche,
        "current_followers": current_followers,
        "milestones": milestones,
        "overall_strategy": (
            f"For {niche} on {platform}: Consistency beats perfection. "
            "Post on schedule, analyze weekly, and double down on your top 20% of content. "
            "First 90 days are about data collection — test everything."
        ),
    }
