#!/usr/bin/env python3
"""Account optimization engine — generates platform-specific growth strategies."""

from typing import Optional

_PLATFORM_TIPS = {
    "tiktok": {
        "bio": [
            "Keep bio under 80 characters — punchy, clear value prop",
            "Add ONE clear call-to-action (e.g., 'Link in bio for X')",
            "Use 1-2 relevant emojis max — they add personality without clutter",
            "Include your niche keyword so TikTok's algorithm categorizes you correctly",
            "Add your other platform handles (IG, YouTube) to funnel followers",
        ],
        "content": [
            "Hook in the FIRST 0-3 seconds — text overlay or action that creates a scroll-stop",
            "Videos 21-34 seconds get 3x more completions than 60+ second videos",
            "Use trending sounds — TikTok pushes content that uses trending audio",
            "Caption should add context, not repeat what's on screen",
            "Post 1-3x/day consistently — TikTok rewards high posting frequency",
            "Reply to ALL comments in the first hour to boost engagement signals",
            "Use the stitch/duet feature with viral content to borrow audience",
            "Add on-screen captions — 85% of TikTok is watched without sound",
        ],
        "hashtags": [
            "Use 3-5 hashtags max — more dilutes reach, less is actually more effective",
            "Mix: 1 mega tag (1B+ views), 2 niche tags (10M-500M views), 1 micro tag (1M-10M views)",
            "Always include #FYP or #ForYou as one of your tags",
            "Research niche-specific hashtags in For You Page to find your community",
            "Rotate hashtags across posts — don't use the exact same set every time",
        ],
        "growth": [
            "Engage with 10-20 creators in your niche BEFORE posting each day",
            "Collaborate with creators in the 10k-100k range (they have hungry engaged audiences)",
            "Go LIVE at least 1x/week — TikTok heavily rewards live streamers with reach",
            "Pin your 3 best-performing videos to your profile",
            "Respond to comments with a new video ('Reply to comment' feature = free content idea)",
            "Cross-post TikToks to Instagram Reels and YouTube Shorts (remove TikTok watermark first)",
        ],
        "posting_schedule": {
            "best_times": ["6-9 AM", "12-3 PM", "7-11 PM"],
            "best_days": ["Tuesday", "Thursday", "Friday", "Saturday"],
            "frequency": "1-3 posts/day",
            "live_frequency": "2-3x per week",
        },
    },
    "youtube": {
        "bio": [
            "Fill all 1,000 characters of your channel description",
            "Include your main keywords in the first 100-150 characters (visible in search)",
            "Add your upload schedule (e.g., 'New videos every Tuesday & Friday')",
            "Link to your website, social profiles, and a lead magnet",
            "Add channel keywords in YouTube Studio > Customization > Basic Info",
        ],
        "content": [
            "Thumbnail is 90% of the click — use faces, bold text, contrasting colors",
            "Title should be 60-70 chars max, include primary keyword near the front",
            "Hook viewers in the first 30 seconds or they'll bounce (hurts watch time)",
            "Aim for 8-15 minute videos for max ad revenue without losing retention",
            "Use chapters (timestamps in description) — improves SEO and watch time",
            "End screen + cards push 15-25% of viewers to another video",
            "Ask for likes/subscribes in the video at a natural high point, not at the end",
            "Create playlists for every content series — keeps viewers watching longer",
        ],
        "hashtags": [
            "Add 3 hashtags in the description — YouTube shows them above the title",
            "Use hashtags that match your video topic for discovery tab visibility",
            "Research competitor videos — use their top-performing hashtags",
            "Community hashtag (#YourChannelName) trains algorithm for your brand",
        ],
        "seo": [
            "Do keyword research with TubeBuddy or VidIQ before every video",
            "Include primary keyword in: title, first sentence of description, tags, file name",
            "Write a 200+ word description with keywords naturally woven in",
            "Add 5-15 tags (mix broad + specific + long-tail)",
            "Add closed captions/subtitles — YouTube indexes them for search",
            "Publish when your audience is active (check YouTube Analytics > Audience tab)",
        ],
        "posting_schedule": {
            "best_times": ["2-4 PM", "8-11 PM"],
            "best_days": ["Thursday", "Friday", "Saturday"],
            "frequency": "1-2 videos/week minimum",
            "shorts_frequency": "3-5 Shorts/week (separate algorithm boost)",
        },
    },
    "instagram": {
        "bio": [
            "Name field = SEO goldmine — put your keyword here, not just your name",
            "Bio line 1: What you do and WHO you help",
            "Bio line 2: Proof/credibility (followers, results, press)",
            "Bio line 3: CTA with link (use Linktree or direct link)",
            "Add location if you're a local business",
            "Switch to Creator or Business account for analytics",
        ],
        "content": [
            "Reels get 3-5x more reach than static posts — prioritize Reels",
            "Carousels have highest save rate of any format (saves = algorithm boost)",
            "Post Reels 4-5x/week, Stories daily, static posts 2-3x/week",
            "First Reel frame must stop the scroll — treat it like a thumbnail",
            "Save-worthy content = lists, tutorials, checklists, infographics",
            "Share-worthy content = relatable, funny, inspiring, controversial",
            "Batch create content and schedule in advance with Later or Buffer",
        ],
        "hashtags": [
            "Use 3-5 highly relevant hashtags (Instagram's official recommendation)",
            "Put hashtags in the caption, not comments (algorithm change 2022)",
            "Research niche hashtags under 500K posts — you can actually rank in them",
            "Mix: 1 branded hashtag, 2-3 niche hashtags, 1 trending hashtag",
        ],
        "posting_schedule": {
            "best_times": ["6-9 AM", "12-2 PM", "5-7 PM"],
            "best_days": ["Monday", "Tuesday", "Wednesday", "Friday"],
            "frequency": "4-7 posts/week",
            "stories_frequency": "5-10 Stories/day",
        },
    },
}


def get_optimization_checklist(platform: str) -> dict:
    """Return full optimization checklist for a platform."""
    p = platform.lower()
    if p not in _PLATFORM_TIPS:
        available = ", ".join(_PLATFORM_TIPS.keys())
        raise ValueError(f"Unknown platform '{platform}'. Available: {available}")
    return {
        "platform": p,
        "checklist": _PLATFORM_TIPS[p],
    }


def get_posting_schedule(platform: str) -> dict:
    """Return optimal posting schedule for a platform."""
    p = platform.lower()
    tips = _PLATFORM_TIPS.get(p, {})
    sched = tips.get("posting_schedule", {})
    return {
        "platform": p,
        "schedule": sched,
    }


def get_bio_template(platform: str, niche: str = "content creator") -> dict:
    """Generate a bio template tailored to platform and niche."""
    templates = {
        "tiktok": (
            f"[Niche keyword] tips & tricks 🔥\n"
            f"Helping [audience] achieve [result]\n"
            f"📲 More {niche} content on IG & YT ↓"
        ),
        "youtube": (
            f"Welcome! I'm [Name] — {niche} sharing [value prop].\n"
            f"New videos every [day] • Subscribe for [benefit]\n"
            f"Business: [email] | IG: @[handle]"
        ),
        "instagram": (
            f"[Keyword-rich name/title]\n"
            f"Helping [specific audience] [specific result]\n"
            f"[Social proof — followers/press/credentials]\n"
            f"👇 [CTA + link]"
        ),
    }
    p = platform.lower()
    return {
        "platform": p,
        "niche": niche,
        "template": templates.get(p, "Platform not found. Use: tiktok, youtube, instagram"),
        "tips": _PLATFORM_TIPS.get(p, {}).get("bio", []),
    }


def get_hashtag_strategy(platform: str, trends: Optional[list[dict]] = None) -> dict:
    """Build a hashtag strategy incorporating current trends."""
    p = platform.lower()
    strategy = {
        "platform": p,
        "rules": _PLATFORM_TIPS.get(p, {}).get("hashtags", []),
    }
    if trends:
        top_tags = [
            t.get("hashtag", t.get("title", ""))
            for t in sorted(trends, key=lambda x: x.get("virality_score", x.get("post_count", 0)), reverse=True)
            if t.get("hashtag") or t.get("title")
        ][:10]
        strategy["trending_now"] = top_tags
        strategy["recommended_mix"] = {
            "mega_tags": [t for t in top_tags[:3]],
            "niche_tags": "[Add 2-3 niche-specific hashtags from your content area]",
            "micro_tags": "[Add 1-2 community hashtags under 1M posts]",
        }
    return strategy


def get_full_optimization_report(platform: str, niche: str = "content creator", trends: Optional[list[dict]] = None) -> dict:
    """Return a complete optimization report for an account."""
    p = platform.lower()
    report = {
        "platform": p,
        "niche": niche,
        "bio_optimization": get_bio_template(p, niche),
        "posting_schedule": get_posting_schedule(p),
        "hashtag_strategy": get_hashtag_strategy(p, trends),
        "checklist": get_optimization_checklist(p),
        "priority_actions": _get_priority_actions(p),
    }
    return report


def _get_priority_actions(platform: str) -> list[str]:
    """Return the 5 highest-ROI actions to take TODAY for each platform."""
    actions = {
        "tiktok": [
            "1. Post your first video TODAY — imperfect action beats perfect inaction",
            "2. Use a trending sound from the Discover page in your first post",
            "3. Engage with 20 videos in your niche before posting (warms up the algorithm)",
            "4. Optimize your profile: photo, bio keyword, pinned videos",
            "5. Stitch or duet one viral video this week to borrow its audience",
        ],
        "youtube": [
            "1. Update all video thumbnails with faces + bold text if not already done",
            "2. Add 3 relevant hashtags to your top 10 performing videos' descriptions",
            "3. Create a 'Best Of' playlist linking your top videos to increase session time",
            "4. Film a YouTube Short today using a trending topic (separate traffic source)",
            "5. Respond to every comment on your last 5 videos (boosts community signal)",
        ],
        "instagram": [
            "1. Convert to Creator account and enable professional dashboard",
            "2. Post a Reel TODAY — even low-quality Reels outperform polished static posts",
            "3. Update your name field with your niche keyword (e.g., 'John | Fitness Tips')",
            "4. Follow and genuinely engage with 10 accounts in your niche this hour",
            "5. Create a 10-slide carousel on your best knowledge topic — carousels get 3x saves",
        ],
    }
    return actions.get(platform, ["Focus on consistency: post daily for 30 days and track your analytics"])
