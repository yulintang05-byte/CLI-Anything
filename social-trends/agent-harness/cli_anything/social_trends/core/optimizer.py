"""Account optimization engine.

Generates platform-specific optimization recommendations for social media
accounts based on current trends, posting patterns, and best practices.
"""

from datetime import datetime, timezone

# Best posting times per platform (hour in 24h, UTC-friendly advice)
_BEST_TIMES = {
    "tiktok": [
        {"day": "Tuesday", "time": "9:00 AM", "tz": "EST", "reason": "Morning commute scrolling peak"},
        {"day": "Thursday", "time": "12:00 PM", "tz": "EST", "reason": "Lunch break engagement spike"},
        {"day": "Friday", "time": "5:00 PM", "tz": "EST", "reason": "End-of-week dopamine seeking"},
        {"day": "Saturday", "time": "11:00 AM", "tz": "EST", "reason": "Weekend leisure browsing"},
        {"day": "Sunday", "time": "7:00 PM", "tz": "EST", "reason": "Pre-week anxiety scroll"},
    ],
    "youtube": [
        {"day": "Saturday", "time": "12:00 PM", "tz": "EST", "reason": "Weekend binge-watch prime time"},
        {"day": "Sunday", "time": "11:00 AM", "tz": "EST", "reason": "Lazy Sunday viewing peak"},
        {"day": "Wednesday", "time": "3:00 PM", "tz": "EST", "reason": "Mid-week afternoon dip"},
        {"day": "Thursday", "time": "7:00 PM", "tz": "EST", "reason": "Pre-weekend entertainment"},
        {"day": "Friday", "time": "4:00 PM", "tz": "EST", "reason": "End-of-school/work release"},
    ],
    "instagram": [
        {"day": "Monday", "time": "11:00 AM", "tz": "EST", "reason": "Post-weekend engagement"},
        {"day": "Wednesday", "time": "10:00 AM", "tz": "EST", "reason": "Midweek engagement peak"},
        {"day": "Friday", "time": "10:00 AM", "tz": "EST", "reason": "TGIF mood boost browsing"},
        {"day": "Saturday", "time": "9:00 AM", "tz": "EST", "reason": "Morning inspiration seeking"},
        {"day": "Sunday", "time": "6:00 PM", "tz": "EST", "reason": "Evening relaxation content"},
    ],
    "twitter": [
        {"day": "Tuesday", "time": "8:00 AM", "tz": "EST", "reason": "Morning news consumption"},
        {"day": "Wednesday", "time": "9:00 AM", "tz": "EST", "reason": "Peak Twitter active hours"},
        {"day": "Thursday", "time": "10:00 AM", "tz": "EST", "reason": "Industry conversation peak"},
    ],
}

_ACCOUNT_CHECKLIST = {
    "tiktok": [
        {
            "category": "Profile",
            "items": [
                "Profile photo: clear face or bold brand logo (400x400px min)",
                "Bio: niche keyword + value prop + call-to-action in ≤150 chars",
                "Link in bio: use Linktree or direct landing page",
                "Username: short, memorable, matches other platforms",
                "Category: set correct Business/Creator category for FYP prioritization",
            ],
        },
        {
            "category": "Content Strategy",
            "items": [
                "Post 1-4x/day — consistency > quantity for algorithm",
                "First 1-2 seconds must hook: shock, question, or bold statement",
                "Use trending audio within 48-72h of it going viral",
                "Add 3-5 niche hashtags + 1-2 broad (fyp/foryoupage) per post",
                "Captions: ask a question to boost comment engagement",
                "Video length sweet spot: 7-15s (loop), 30-60s (watch time), or 3-5min (deep engagement)",
                "Use auto-captions/subtitles — 80% of viewers watch without sound",
            ],
        },
        {
            "category": "Engagement Optimization",
            "items": [
                "Reply to every comment in first hour after posting",
                "Pin your best 3 videos to profile",
                "Use Duet/Stitch on viral content in your niche",
                "Go live 2x/week — TikTok boosts live creators in FYP",
                "Respond to DMs within 24h for creator score",
            ],
        },
        {
            "category": "Analytics",
            "items": [
                "Switch to Pro/Creator account for analytics access",
                "Check 'Audience Insights' weekly — optimize for your most active follower time zone",
                "Monitor 'Video Insights' — focus on Average Watch Time % and rewatch rate",
                "Track follower growth rate — aim for 3-5% monthly growth minimum",
                "Identify top-performing content type and double down",
            ],
        },
    ],
    "youtube": [
        {
            "category": "Channel Setup",
            "items": [
                "Channel art: 2560x1440px banner with value prop visible on all devices",
                "Profile pic: high contrast, recognizable at 98px",
                "About section: keyword-rich description with links to all social platforms",
                "Channel keywords: add 15-20 in Studio > Settings > Channel > Basic Info",
                "Sections: organize homepage with curated playlists",
                "Channel trailer: 60-90s hook for non-subscribers",
            ],
        },
        {
            "category": "Video SEO",
            "items": [
                "Title: 60 chars max, front-load primary keyword",
                "Description: 200+ words, keyword in first 2 sentences, chapters with timestamps",
                "Tags: 10-15 tags — mix broad, specific, and channel-brand tags",
                "Thumbnail: 1280x720, faces with expression, text overlay ≤6 words, high contrast",
                "Custom URL: claim yours once you hit 100 subscribers",
                "End screen: add subscribe button + 2 video cards at -20s mark",
            ],
        },
        {
            "category": "Growth Tactics",
            "items": [
                "Upload on consistent schedule — same day/time weekly builds habit",
                "Community posts: share polls, updates, behind-scenes to notify subscribers",
                "Shorts strategy: post 3-5 Shorts/week to feed algorithm with high impressions",
                "Collaborate with creators in your niche (similar or 2-10x your size)",
                "Reply to all comments in first 24h — boosts ranking signal",
                "Playlists: group content into themed playlists for session watch time",
            ],
        },
    ],
    "instagram": [
        {
            "category": "Profile",
            "items": [
                "Username: consistent with TikTok/YouTube for cross-platform discoverability",
                "Bio: 150 chars, keyword + niche + CTA + emoji for visual breaks",
                "Link in bio: updated landing page or Linktree with 5+ destinations",
                "Story Highlights: branded covers, organized by content category",
                "Business Account: required for analytics, ads, and shopping features",
            ],
        },
        {
            "category": "Reels (Priority Format)",
            "items": [
                "Reels get 22% more engagement than regular videos — post 4-7 Reels/week",
                "Use trending audio (check TikTok trends first, they migrate 48-72h later)",
                "9:16 aspect ratio (1080x1920) — square content gets fewer Reel impressions",
                "Add keywords to Reels caption — Instagram now indexes video speech/text",
                "Share Reels to Stories immediately after posting for initial push",
            ],
        },
        {
            "category": "Feed & Carousels",
            "items": [
                "Carousels get 3x more reach than single images — use for tutorials/lists",
                "First slide is everything — treat it like a thumbnail",
                "Alt text on every post for SEO (Settings > Accessibility > Alt Text)",
                "Cross-post TikToks without watermark using SnapTik or SSSTikTok",
            ],
        },
    ],
}

_THEME_PAGE_GUIDE = {
    "concept": (
        "A theme page curates content around a specific topic/niche without showing your face. "
        "You repost (with credit), create compilations, or post niche-specific content. "
        "This model scales faster because: no personal brand dependency, multiple accounts possible, "
        "easy to outsource, and highly monetizable via shoutouts, affiliate links, and brand deals."
    ),
    "profitable_niches": [
        {
            "niche": "Luxury Lifestyle",
            "platforms": ["Instagram", "TikTok"],
            "monetization": ["Brand deals", "Affiliate (cars, watches)", "Shoutouts $50-500"],
            "difficulty": "Low",
            "monthly_potential": "$500-5000",
        },
        {
            "niche": "Fitness Motivation",
            "platforms": ["Instagram", "TikTok", "YouTube Shorts"],
            "monetization": ["Supplement affiliate (20-30% commission)", "Program sales", "Shoutouts"],
            "difficulty": "Low",
            "monthly_potential": "$300-3000",
        },
        {
            "niche": "Quotes / Mindset",
            "platforms": ["Instagram", "Pinterest", "TikTok"],
            "monetization": ["Print-on-demand", "Course affiliate", "Shoutouts"],
            "difficulty": "Very Low",
            "monthly_potential": "$200-2000",
        },
        {
            "niche": "Cooking / Recipes",
            "platforms": ["TikTok", "YouTube", "Instagram"],
            "monetization": ["Kitchen affiliate (Amazon Associates)", "Cookbook sales", "Brand deals"],
            "difficulty": "Medium",
            "monthly_potential": "$500-8000",
        },
        {
            "niche": "Animals / Pets",
            "platforms": ["Instagram", "TikTok", "YouTube"],
            "monetization": ["Pet product affiliate", "Brand deals", "Merch"],
            "difficulty": "Very Low",
            "monthly_potential": "$300-4000",
        },
        {
            "niche": "Finance / Investing",
            "platforms": ["TikTok", "YouTube", "Twitter"],
            "monetization": ["Brokerage affiliate ($50-200/signup)", "Course sales", "Newsletter"],
            "difficulty": "Medium",
            "monthly_potential": "$1000-15000",
        },
        {
            "niche": "Travel",
            "platforms": ["Instagram", "TikTok", "YouTube"],
            "monetization": ["Hotel/flight affiliate", "Presets/LUTs sale", "Brand deals"],
            "difficulty": "Medium",
            "monthly_potential": "$500-6000",
        },
        {
            "niche": "AI / Tech",
            "platforms": ["Twitter/X", "TikTok", "YouTube"],
            "monetization": ["SaaS affiliate (30-50% recurring)", "Newsletter", "Consulting"],
            "difficulty": "Medium",
            "monthly_potential": "$1000-20000",
        },
    ],
    "step_by_step": [
        "1. Pick niche: high passion + high CPM + clear monetization path",
        "2. Research: find top 10 accounts in niche, analyze their best content",
        "3. Brand: username, logo (use Canva), consistent color palette, bio",
        "4. Content sourcing: Reddit, Pinterest, YouTube (repost w/ credit), or create originals",
        "5. Posting schedule: 3-5x/day TikTok, 1-2x/day Instagram, daily Shorts",
        "6. Growth hack: engage with top posts in niche (comment value-adds in first 30min)",
        "7. Monetize at 5K followers: open DMs for shoutouts ($20-50 initially)",
        "8. Scale: hire VA ($3-8/hr) to find/post content, focus on strategy + deals",
        "9. Diversify: add email list, sell digital products, launch YouTube long-form",
        "10. Automate: Buffer/Later for scheduling, Zapier for cross-posting",
    ],
    "content_sourcing": {
        "free_sources": [
            "Reddit (r/niche) — top posts of the week",
            "Pinterest — trending boards in your niche",
            "YouTube — embed highlights (always credit)",
            "Unsplash / Pexels — free stock for image posts",
            "CapCut templates — viral video formats",
            "Canva — quote graphics, carousels, thumbnails",
        ],
        "tools": [
            "SnapTik / SSSTikTok — download TikToks without watermark",
            "4K Video Downloader — download YouTube content",
            "Repurpose.io — auto cross-post to all platforms",
            "Metricool — free scheduling + analytics dashboard",
            "Canva Pro — brand kit + bulk create",
        ],
    },
    "converting_theme_pages": {
        "meaning": (
            "Converting = turning followers into buyers/revenue. "
            "Most theme pages fail here. The key is: trust → offer → urgency."
        ),
        "conversion_tactics": [
            "Bio link funnel: free lead magnet → email list → paid offer",
            "Story CTA: 'Link in bio' after every viral post",
            "Pinned post: best-performing post with clear CTA overlay",
            "Comment-to-DM automation: 'Comment GUIDE for free resource' (ManyChat)",
            "Shoutout pricing: research competitors, undercut by 20% to fill calendar",
            "Affiliate disclosure: stay FTC compliant — 'paid partnership' or #ad",
            "Story polls/quizzes: warm up audience before pitching",
            "Limited drops: 'Only 3 spots for shoutout this week' — creates urgency",
        ],
        "funnel_blueprint": [
            "Step 1 — Attract: Viral content with trending audio/hashtags",
            "Step 2 — Retain: Follow CTA in first 3 seconds ('Follow for daily X')",
            "Step 3 — Engage: Question in caption, reply to all comments",
            "Step 4 — Convert: Story with link-in-bio, limited offer, DM automation",
            "Step 5 — Monetize: Shoutout, affiliate click, digital product purchase",
            "Step 6 — Retain buyers: Email list, exclusive content, community",
        ],
    },
}


def get_account_checklist(platform: str = "all") -> dict:
    """Return optimization checklist for one or all platforms."""
    platform = platform.lower()
    if platform == "all":
        return _ACCOUNT_CHECKLIST
    return {platform: _ACCOUNT_CHECKLIST.get(platform, [])}


def get_best_posting_times(platform: str = "all") -> dict:
    """Return best posting times for one or all platforms."""
    platform = platform.lower()
    if platform == "all":
        return _BEST_TIMES
    return {platform: _BEST_TIMES.get(platform, [])}


def get_theme_page_guide() -> dict:
    """Return complete theme page creation + conversion guide."""
    return _THEME_PAGE_GUIDE


def get_content_calendar(platform: str, posts_per_week: int = 7) -> list[dict]:
    """Generate a 1-week content calendar for the given platform."""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    formats: dict[str, list[str]] = {
        "tiktok": ["Trending Sound Video", "Tutorial/How-To", "POV Story", "Duet/Stitch Trend",
                   "Day-in-Life Vlog", "Comedy Skit", "Motivational Quote Overlay"],
        "youtube": ["Long-Form Tutorial", "YouTube Short (trend)", "Vlog", "Reaction Video",
                    "List Video (Top 10)", "Collab", "YouTube Short (original)"],
        "instagram": ["Reel (trending audio)", "Carousel (tips/value)", "Story Poll + CTA",
                      "Reel (tutorial)", "Quote Graphic", "Reel (personal/BTS)", "Carousel (OOTD/lifestyle)"],
    }

    platform = platform.lower()
    fmt_list = formats.get(platform, formats["tiktok"])

    calendar = []
    for i, day in enumerate(days[:posts_per_week]):
        fmt = fmt_list[i % len(fmt_list)]
        times = _BEST_TIMES.get(platform, _BEST_TIMES["tiktok"])
        post_time = times[i % len(times)]
        calendar.append({
            "day": day,
            "format": fmt,
            "platform": platform,
            "suggested_time": post_time["time"],
            "timezone": post_time["tz"],
            "tip": post_time["reason"],
        })

    return calendar


def get_growth_hacks(platform: str = "tiktok") -> list[dict]:
    """Return actionable growth hacks for the given platform."""
    hacks: dict[str, list[dict]] = {
        "tiktok": [
            {
                "hack": "The 30-30-30 Comment Strategy",
                "description": "In first 30min after posting: reply to 30 comments on COMPETING accounts' viral videos. Gets your profile seen by their engaged audience.",
                "effort": "Medium",
                "impact": "High",
            },
            {
                "hack": "Trending Audio Front-Running",
                "description": "Check TikTok Creative Center for songs with 'rising' status. Use them 24-48h before they peak. Early adopters get massive reach boost.",
                "effort": "Low",
                "impact": "Very High",
            },
            {
                "hack": "Series Content with Cliffhangers",
                "description": "Multi-part content ('Part 1 of 3') forces follows to see continuation. Follow rate 3-5x higher than standalone videos.",
                "effort": "Medium",
                "impact": "High",
            },
            {
                "hack": "The Stitch Funnel",
                "description": "Stitch viral videos with your take/reaction. Borrow their algorithm juice. Aim for creators with 100K-1M followers in your niche.",
                "effort": "Low",
                "impact": "High",
            },
            {
                "hack": "Live Q&A After Viral Posts",
                "description": "When a post goes viral (>50K views), go live immediately. New followers see you live in notification + TikTok boosts live to FYP.",
                "effort": "Low",
                "impact": "Very High",
            },
            {
                "hack": "Niche Community Takeover",
                "description": "Comment the single most valuable, insightful comment on the top 20 posts in your niche daily. Build recognition before posting.",
                "effort": "High",
                "impact": "High",
            },
        ],
        "youtube": [
            {
                "hack": "Shorts-to-Long-Form Pipeline",
                "description": "Post a Short teasing your long-form video. End with 'full video on channel.' Drives Shorts viewers to become subscribers.",
                "effort": "Low",
                "impact": "High",
            },
            {
                "hack": "Keyword Cannibalization Attack",
                "description": "Search your niche keyword, note what the top 5 videos are missing. Fill that gap. YouTube rewards completeness over production quality.",
                "effort": "Medium",
                "impact": "Very High",
            },
            {
                "hack": "The 0-48h Engagement Sprint",
                "description": "In first 48h, get 10 friends to watch full video + comment + like. YouTube interprets high CTR/watch time as quality signal.",
                "effort": "Medium",
                "impact": "Very High",
            },
        ],
        "instagram": [
            {
                "hack": "Reel SEO Keywords",
                "description": "Instagram now reads Reel captions and spoken words. Repeat your keyword 2-3x naturally in video speech + caption.",
                "effort": "Low",
                "impact": "High",
            },
            {
                "hack": "Story Reply Loop",
                "description": "Post a controversial opinion as a Story poll. DM everyone who votes with a follow-up question. Triggers story algorithm.",
                "effort": "Medium",
                "impact": "High",
            },
        ],
    }

    platform = platform.lower()
    result = hacks.get(platform, hacks["tiktok"])
    return result
