"""Account Optimizer — Audit reports and posting schedule recommendations.

All recommendations are derived from publicly documented platform best practices
and industry research. Actual performance depends on your specific audience.
"""

from __future__ import annotations

BEST_POSTING_TIMES: dict[str, dict] = {
    "instagram": {
        "schedule": [
            {"day": "Monday",    "peak1": "9:00 AM",  "peak2": "7:00 PM",  "score": "8/10"},
            {"day": "Tuesday",   "peak1": "8:00 AM",  "peak2": "1:00 PM",  "score": "9/10"},
            {"day": "Wednesday", "peak1": "11:00 AM", "peak2": "8:00 PM",  "score": "10/10"},
            {"day": "Thursday",  "peak1": "12:00 PM", "peak2": "7:00 PM",  "score": "9/10"},
            {"day": "Friday",    "peak1": "10:00 AM", "peak2": "8:00 PM",  "score": "8/10"},
            {"day": "Saturday",  "peak1": "9:00 AM",  "peak2": "7:00 PM",  "score": "7/10"},
            {"day": "Sunday",    "peak1": "10:00 AM", "peak2": "2:00 PM",  "score": "7/10"},
        ],
        "frequency": "1-2 posts/day Reels + 5-7 Stories/day",
        "note": "Wednesday and Tuesday show highest average engagement. Always check YOUR audience insights — generic best-times are a starting point only.",
    },
    "tiktok": {
        "schedule": [
            {"day": "Monday",    "peak1": "6:00 AM",  "peak2": "10:00 PM", "score": "7/10"},
            {"day": "Tuesday",   "peak1": "9:00 AM",  "peak2": "9:00 PM",  "score": "8/10"},
            {"day": "Wednesday", "peak1": "7:00 AM",  "peak2": "9:00 PM",  "score": "9/10"},
            {"day": "Thursday",  "peak1": "9:00 AM",  "peak2": "8:00 PM",  "score": "8/10"},
            {"day": "Friday",    "peak1": "5:00 AM",  "peak2": "3:00 PM",  "score": "10/10"},
            {"day": "Saturday",  "peak1": "11:00 AM", "peak2": "7:00 PM",  "score": "9/10"},
            {"day": "Sunday",    "peak1": "7:00 AM",  "peak2": "4:00 PM",  "score": "8/10"},
        ],
        "frequency": "1-4 videos/day for maximum algorithm exposure",
        "note": "Consistency matters more than timing on TikTok. Post at the same time every day so the algorithm learns your pattern.",
    },
    "youtube": {
        "schedule": [
            {"day": "Monday",    "peak1": "2:00 PM",  "peak2": "9:00 PM",  "score": "7/10"},
            {"day": "Tuesday",   "peak1": "3:00 PM",  "peak2": "7:00 PM",  "score": "8/10"},
            {"day": "Wednesday", "peak1": "3:00 PM",  "peak2": "7:00 PM",  "score": "9/10"},
            {"day": "Thursday",  "peak1": "12:00 PM", "peak2": "7:00 PM",  "score": "8/10"},
            {"day": "Friday",    "peak1": "12:00 PM", "peak2": "4:00 PM",  "score": "9/10"},
            {"day": "Saturday",  "peak1": "9:00 AM",  "peak2": "11:00 AM", "score": "10/10"},
            {"day": "Sunday",    "peak1": "9:00 AM",  "peak2": "11:00 AM", "score": "10/10"},
        ],
        "frequency": "1-3 videos/week (quality over quantity)",
        "note": "Saturday morning is the #1 YouTube viewership slot globally. For Shorts: post 3-5/week.",
    },
    "twitter": {
        "schedule": [
            {"day": "Monday",    "peak1": "8:00 AM",  "peak2": "4:00 PM",  "score": "8/10"},
            {"day": "Tuesday",   "peak1": "9:00 AM",  "peak2": "2:00 PM",  "score": "9/10"},
            {"day": "Wednesday", "peak1": "9:00 AM",  "peak2": "3:00 PM",  "score": "10/10"},
            {"day": "Thursday",  "peak1": "9:00 AM",  "peak2": "2:00 PM",  "score": "9/10"},
            {"day": "Friday",    "peak1": "9:00 AM",  "peak2": "1:00 PM",  "score": "8/10"},
            {"day": "Saturday",  "peak1": "9:00 AM",  "peak2": "12:00 PM", "score": "6/10"},
            {"day": "Sunday",    "peak1": "9:00 AM",  "peak2": "12:00 PM", "score": "6/10"},
        ],
        "frequency": "3-5 tweets/day for growth accounts",
        "note": "Engage with trending topics within the first 15 minutes for maximum reach.",
    },
}

AUDIT_RECOMMENDATIONS: dict[str, dict[str, list[str]]] = {
    "instagram": {
        "profile_optimization": [
            "Use a clear, high-contrast profile photo (800×800px min) — recognizable at thumbnail size",
            "Bio line 1: What you do. Line 2: Who you help or value you deliver. Line 3: CTA with link",
            "Use keywords in your name field (e.g. 'Alex | Fitness Coach') — it's searchable",
            "Add a link-in-bio tool (Beacons, Linktree, or Later) to capture multiple link destinations",
            "Switch to a Creator or Business account for full analytics access",
        ],
        "content_strategy": [
            "Post 4-7 Reels per week — Reels receive 3× more reach than static posts on average",
            "Hook the first 1-2 seconds: bold text on screen + movement stops the scroll",
            "Carousels get 3× more saves than single images — use for educational content",
            "Post Stories daily to maintain top-of-feed presence for existing followers",
            "End every caption with ONE clear CTA: save this, tag a friend, or comment your answer",
            "Respond to every comment in the first hour — early engagement signals boost distribution",
        ],
        "growth_tactics": [
            "Comment meaningfully (not just 'great post') on 10-20 niche accounts daily",
            "Collaborate with accounts 10-20% larger using Instagram's Collab post feature",
            "Use trending audio within 48 hours of it spiking for algorithm push",
            "Post your best-performing Reel to TikTok and YouTube Shorts simultaneously",
            "Go live once per week — Lives boost organic reach for your next 3-4 posts",
        ],
        "analytics_actions": [
            "Track reach-to-follower ratio — healthy accounts hit 20-40% for small pages",
            "Identify which posts drive the most profile visits and follows (best content signal)",
            "Check which hashtags consistently appear in reach sources and double down on those themes",
            "A/B test caption style: question vs. bold statement, short vs. long — for 2 weeks each",
        ],
    },
    "tiktok": {
        "profile_optimization": [
            "Username: short, memorable, and identical across platforms for brand consistency",
            "Bio: 1-2 lines max — niche keyword + value prop + optional CTA emoji",
            "Link to your highest-converting destination (Instagram, link-in-bio, or website)",
            "Profile photo: bright, high-contrast, recognizable at 40×40px small size",
            "Pin 3 best-performing videos to your profile top (use the pin feature in the video menu)",
            "Switch to Business account to unlock the email CTA button in bio",
        ],
        "content_strategy": [
            "Hook in first 0-2 seconds: say or show something that stops a scrolling thumb",
            "Use trending sounds within 24-48 hours of them appearing in the Creative Center",
            "Film vertically 1080×1920 — add text overlay so content works with sound off",
            "Post 1-4 videos daily for maximum For You Page distribution",
            "Series content ('Part 1 of 3') drives return viewers and completion rate",
            "Stitch or duet top creators in your niche — their audience sees your response",
            "Reply to comments with a video reply to create new content with built-in audience",
        ],
        "growth_tactics": [
            "Hop on trends within 24-48 hours — TikTok heavily rewards early adopters of sounds/effects",
            "3-5 hashtags only: 1 broad (fyp/viral), 2-3 niche-specific — keyword-rich hashtags",
            "Comment back on every comment within the first 30 minutes to signal creator activity",
            "Cross-post top TikToks to Instagram Reels and YouTube Shorts (remove TikTok watermark first)",
            "Use Creator Collaboration for mutual follower exchanges with similar-size accounts",
        ],
        "analytics_actions": [
            "Target 70%+ average watch percentage — below 50% means your hook needs work",
            "Traffic source breakdown: 'For You' % shows how much the algorithm is pushing you",
            "Track which video formats and topics drive the most new followers (not just views)",
            "Monitor when your followers are most active in Analytics → Followers tab",
        ],
    },
    "youtube": {
        "profile_optimization": [
            "Channel banner: 2560×1440px, show exactly what viewers get + upload schedule",
            "Channel description: primary keyword in first 2-3 sentences for SEO",
            "Channel trailer: 60-90 seconds of your best content + clear subscribe CTA",
            "Add channel keywords: YouTube Studio → Settings → Channel → Basic Info",
            "Create organized playlists by series or topic — improves session watch time",
            "Enable Community tab (at 500 subscribers) for between-video engagement",
        ],
        "content_strategy": [
            "Thumbnail: bright colors, expressive face, 6-8 words max, 1280×720px",
            "Title: primary keyword in first 60 chars — create a curiosity gap",
            "Hook in first 30 seconds: deliver on the title promise immediately, no intros",
            "Add timestamps (chapters) for any video over 5 minutes",
            "Always add 2 end screen video cards + subscribe button (final 20 seconds)",
            "Post YouTube Shorts 3-5×/week to grow subscribers who then watch long-form",
        ],
        "growth_tactics": [
            "SEO: research keywords in YouTube Search Autocomplete + TubeBuddy/VidIQ before filming",
            "Click-through rate (CTR) target: 4-10% from impressions — thumbnail is everything",
            "Reply to every comment in the first 48 hours to boost comment velocity",
            "Evergreen tutorials rank in search for years — balance trending + timeless content",
            "Collaborate: appear on other channels and invite them to yours",
        ],
        "analytics_actions": [
            "Average view duration: aim for 40-60% retention — drop-off graphs show where to improve",
            "Impressions vs. click-through: high impressions + low CTR = thumbnail problem",
            "Traffic sources: 'Suggested videos' is the biggest growth lever on YouTube",
            "Subscriber conversion rate per video: which video types turn viewers into subscribers?",
        ],
    },
}

NICHE_TIPS: dict[str, list[str]] = {
    "fitness": [
        "Post before-and-after transformations (your own) — consistently outperform other formats",
        "Share workouts with exact sets/reps/weights — specificity builds trust faster than vague advice",
        "Morning workout content (6-8 AM posts) reaches people before their own gym session",
        "Turn critical comments into video replies — 'this doesn't work for me' becomes new content",
    ],
    "food": [
        "Overhead shots and extreme close-ups of textures perform best across all platforms",
        "'Under 500 calories' and '10-minute' hooks drive the most shares in food content",
        "Post at 11 AM and 5 PM — people browse food content at meal planning time",
        "Make every recipe recreatable: show every step, every ingredient, every measurement",
    ],
    "finance": [
        "Replace generic advice ('save money!') with specific stories ('I paid off $30K in 18 months')",
        "Finance content that makes viewers feel smart outperforms content that lectures them",
        "Use real numbers: income breakdowns, exact portfolio sizes, specific debt amounts",
        "Morning commute (7-9 AM) is peak finance content consumption time",
    ],
    "travel": [
        "Film B-roll while traveling, batch-edit at home — do not try to edit while traveling",
        "Budget breakdowns and 'total trip cost' reveals drive 3-5× more shares than scenery posts",
        "Destination-specific content ranks in search and brings steady views for years",
        "Tag exact locations to appear in TikTok and Instagram location-based explore feeds",
    ],
    "tech": [
        "Tutorial content ('how to build X') gets shared in Slack and Discord — high reach multiplier",
        "Opinion/hot-take content drives comments: 'X framework is overrated' outperforms tutorials",
        "Demo-first, explanation-second: show the result in the first 3 seconds",
        "AI tool roundups and comparisons are extremely high-engagement in 2024-2025",
    ],
}


class AccountOptimizer:
    """Generate account audits and posting schedule recommendations."""

    def audit(
        self,
        platform: str,
        niche: str,
        username: str = "",
    ) -> dict:
        """Generate a full account audit with categorized recommendations.

        Returns dict of category_name → list of action items.
        """
        base = dict(AUDIT_RECOMMENDATIONS.get(platform, AUDIT_RECOMMENDATIONS["instagram"]))
        niche_tips = NICHE_TIPS.get(niche.lower(), [])
        if niche_tips:
            base["niche_specific"] = niche_tips
        return base

    def get_best_times(
        self,
        platform: str,
        niche: str = "general",
        timezone: str = "US/Eastern",
    ) -> dict:
        """Get the optimal posting schedule for a platform.

        When platform='all', returns a dict of platform → schedule data.
        Otherwise returns the schedule data dict directly.
        """
        if platform == "all":
            return dict(BEST_POSTING_TIMES)
        return BEST_POSTING_TIMES.get(platform, BEST_POSTING_TIMES["instagram"])
