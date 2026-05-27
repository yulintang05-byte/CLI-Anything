"""Theme page creation and conversion guide — structured knowledge base."""
from __future__ import annotations
from typing import Any


def get_theme_page_guide(
    niche: str = "general",
    goal: str = "monetize",
    current_followers: int = 0,
) -> dict[str, Any]:
    """
    Return a comprehensive guide for creating or converting to a theme page.

    niche: the content theme (e.g. 'fitness', 'cars', 'luxury', 'quotes')
    goal: 'monetize' | 'grow' | 'convert' (converting existing personal page)
    """
    return {
        "overview": _theme_page_overview(),
        "niche_analysis": _niche_analysis(niche),
        "setup_checklist": _setup_checklist(niche),
        "content_strategy": _content_strategy(niche),
        "monetization_roadmap": _monetization_roadmap(goal, current_followers),
        "conversion_guide": _conversion_guide(goal),
        "growth_hacks": _growth_hacks(niche),
        "posting_tools": _posting_tools(),
        "common_mistakes": _common_mistakes(),
    }


def _theme_page_overview() -> dict[str, Any]:
    return {
        "what_is_theme_page": (
            "A theme page is a content account built around a TOPIC, not a person. "
            "It curates, reposts, or creates content within one niche "
            "(e.g. @luxurycars, @motivationquotes, @funnydogs). "
            "The creator stays anonymous — the NICHE is the brand."
        ),
        "why_theme_pages_work": [
            "No face needed — post from anywhere, anytime",
            "Scale by running 10+ pages simultaneously",
            "Can be sold as digital assets ($500–$50K+ per page)",
            "Algorithm loves consistent niche signals",
            "Low effort: repurpose/curate existing viral content",
        ],
        "income_potential": {
            "10K followers": "$100-300/month (brand shoutouts)",
            "50K followers": "$500-1500/month (sponsorships + link in bio)",
            "100K followers": "$1000-5000/month (UGC deals, affiliate, shoutouts)",
            "500K+ followers": "$5000-20000+/month (major brand deals, page sales)",
        },
    }


def _niche_analysis(niche: str) -> dict[str, Any]:
    niche_data: dict[str, dict] = {
        "luxury": {
            "competition": "medium",
            "monetization_ease": "high",
            "content_sources": ["YouTube car/house tours", "Instagram luxury accounts", "Pinterest boards"],
            "best_platforms": ["Instagram", "TikTok"],
            "revenue_methods": ["Car dealer sponsorships", "Luxury brand affiliates", "Shoutouts to other pages"],
            "trending_formats": ["Before/after luxury transformations", "Price reveals", "Rate my setup"],
        },
        "motivation": {
            "competition": "very high",
            "monetization_ease": "medium",
            "content_sources": ["Book quotes", "Interview clips (fair use)", "Original voiceover content"],
            "best_platforms": ["TikTok", "Instagram", "YouTube Shorts"],
            "revenue_methods": ["Digital products (ebooks)", "Affiliate (Audible, courses)", "Shoutouts"],
            "trending_formats": ["Cinematic quote videos", "POV motivational hooks", "Before/after mindset stories"],
        },
        "fitness": {
            "competition": "high",
            "monetization_ease": "very high",
            "content_sources": ["Workout tutorials", "Transformation stories", "Nutrition tips"],
            "best_platforms": ["TikTok", "Instagram", "YouTube"],
            "revenue_methods": ["Supplement affiliates", "Workout program sales", "1-on-1 coaching", "Gym partnerships"],
            "trending_formats": ["30-day challenge results", 'What I eat in a day', "Gym fail/win compilation"],
        },
        "finance": {
            "competition": "medium",
            "monetization_ease": "very high",
            "content_sources": ["News reframes", "Book summaries", "Personal finance tips"],
            "best_platforms": ["TikTok", "YouTube", "Twitter/X"],
            "revenue_methods": ["Affiliate (Robinhood, Coinbase)", "Financial courses", "Newsletter subscriptions"],
            "trending_formats": ["'$X to $X in X months' stories", "Stock market reactions", "Money mistakes I made"],
        },
        "pets": {
            "competition": "medium",
            "monetization_ease": "medium",
            "content_sources": ["Viral pet clips (credit in caption)", "Original pet content", "Rescue stories"],
            "best_platforms": ["TikTok", "Instagram", "YouTube Shorts"],
            "revenue_methods": ["Pet product affiliates (Chewy, Amazon)", "Brand deals", "Merchandise"],
            "trending_formats": ["Reaction videos", "Cute/funny compilations", "Day in the life"],
        },
    }

    niche_lower = niche.lower()
    matched = "motivation"
    for key in niche_data:
        if key in niche_lower or niche_lower in key:
            matched = key
            break

    data = niche_data.get(matched, niche_data["motivation"])
    return {"niche": niche, "matched_template": matched, **data}


def _setup_checklist(niche: str) -> list[dict[str, str]]:
    return [
        {"step": "1", "task": "Choose a brandable page name", "detail": f"Format: @[niche][descriptor] e.g. @{niche.lower()}daily, @best{niche.lower()}, @{niche.lower()}world"},
        {"step": "2", "task": "Create accounts on TikTok + Instagram + YouTube Shorts", "detail": "Use same username across all platforms for SEO + cross-promo"},
        {"step": "3", "task": "Set profile picture", "detail": "Use a logo (Canva free) or niche-relevant stock image. NO personal photos."},
        {"step": "4", "task": "Write optimized bio", "detail": f"'Daily {niche} content 🔥 | Follow for more | [CTA]'"},
        {"step": "5", "task": "Create 9 posts before going public (Instagram grid)", "detail": "Never launch with an empty profile. Pre-load 9 pieces of content."},
        {"step": "6", "task": "Find your top 20 competitor pages", "detail": "Study their top posts, hooks, posting schedule, and captions"},
        {"step": "7", "task": "Build a content bank of 30+ posts", "detail": "Schedule out 2 weeks minimum before launch. Use Buffer, Later, or Metricool."},
        {"step": "8", "task": "Set up link-in-bio page", "detail": "Use Linktree or Stan.store. Add affiliate links and contact email."},
        {"step": "9", "task": "Create posting schedule", "detail": "TikTok: 1-3x/day. Instagram Reels: 1x/day. YouTube Shorts: 1x/day."},
        {"step": "10", "task": "Enable Creator monetization tools", "detail": "TikTok Creator Fund/Series, Instagram Subscriptions/Bonuses, YouTube Partner Program"},
    ]


def _content_strategy(niche: str) -> dict[str, Any]:
    return {
        "content_pillars": [
            f"Educational — teach something about {niche}",
            f"Inspirational — show aspirational {niche} content",
            f"Entertaining — funny/surprising {niche} moments",
            f"Relatable — 'If you love {niche}...' content",
            f"Trending — put a {niche} twist on platform-wide trends",
        ],
        "content_sourcing_methods": {
            "reposting_legal": [
                "Credit original creator in caption (@username)",
                "Only repost content older than 48 hours",
                "Use 'Sound on' + add your own caption value",
                "On TikTok: use Duet/Stitch (built-in credit)",
            ],
            "original_content": [
                f"Screen-record yourself reacting to viral {niche} videos",
                f"Voiceover slideshows (CapCut, InShot)",
                f"Text-on-screen listicles with trending audio",
                f"'Compilation' format with your own intro/outro",
            ],
            "tools": [
                "CapCut — free video editor, trending templates",
                "Canva — graphics, carousels, quote cards",
                "InShot — mobile editing",
                "Pinterest — content inspiration board",
                f"Reddit r/{niche} — find raw viral material",
            ],
        },
        "viral_formula": {
            "hook": "First 1-3 seconds: bold statement, unexpected visual, or question",
            "body": "Deliver value fast — no fluff. Cut every unnecessary second.",
            "cta": "End with: 'Follow for more [niche] content daily'",
            "caption": f"Short, punchy. Include 1 question to drive comments. Add hashtags.",
            "audio": "Use trending sounds in first 48-72 hours of trend",
        },
    }


def _monetization_roadmap(goal: str, followers: int) -> list[dict[str, Any]]:
    stages = [
        {
            "stage": "0-1K followers",
            "timeline": "Weeks 1-4",
            "focus": "Content consistency + algorithm learning",
            "actions": [
                "Post 2-3x/day minimum",
                "Engage with 20 accounts in niche daily",
                "Study analytics every 3 days — double down on what works",
                "No monetization yet — focus 100% on growth",
            ],
            "revenue": "$0 (investment phase)",
        },
        {
            "stage": "1K-10K followers",
            "timeline": "Month 2-4",
            "focus": "Build authority + start affiliate",
            "actions": [
                "Add affiliate links to bio (Amazon, ShareASale, Impact)",
                "Start email list (free ConvertKit)",
                "DM micro-brands for free product in exchange for posts",
                "Create one digital product (PDF guide: $7-27)",
            ],
            "revenue": "$50-300/month",
        },
        {
            "stage": "10K-50K followers",
            "timeline": "Month 4-8",
            "focus": "Shoutout marketplace + brand deals",
            "actions": [
                "List on Shoutcart, GrapeVine, or Collaborate",
                "DM 5 brands/day in your niche for sponsorships",
                "Launch paid shoutout pricing: $20-100 per post",
                "Offer page management service to local businesses",
            ],
            "revenue": "$300-1500/month",
        },
        {
            "stage": "50K-100K followers",
            "timeline": "Month 8-18",
            "focus": "Scale content + sell the playbook",
            "actions": [
                "Launch a paid course: 'How I grew to 100K in [niche]'",
                "Hire VA to help with content curation ($3-8/hr)",
                "Apply to TikTok Creator Marketplace",
                "Consider selling page ($5K-20K range at this size)",
            ],
            "revenue": "$1500-5000/month",
        },
        {
            "stage": "100K+ followers",
            "timeline": "18+ months",
            "focus": "Brand + passive income",
            "actions": [
                "Agency/management deal with major brands",
                "Launch merchandise (Printful/Printify)",
                "YouTube monetization ($1-3 RPM on Shorts, $5-30 on long form)",
                "Sell page for 12-24x monthly revenue",
            ],
            "revenue": "$5000-20000+/month",
        },
    ]

    # Find current stage
    follower_ranges = [(0, 1000), (1000, 10000), (10000, 50000), (50000, 100000), (100000, float("inf"))]
    current_stage_idx = 0
    for i, (lo, hi) in enumerate(follower_ranges):
        if lo <= followers < hi:
            current_stage_idx = i
            break

    return [
        {**stage, "is_current": i == current_stage_idx}
        for i, stage in enumerate(stages)
    ]


def _conversion_guide(goal: str) -> dict[str, Any]:
    if goal != "convert":
        return {"note": "Set goal='convert' for personal-to-theme-page conversion guide."}

    return {
        "overview": "Converting a personal account to a theme page without losing followers",
        "risk_assessment": "You WILL lose some followers (10-30%) — this is normal and healthy",
        "step_by_step": [
            {"step": "1", "action": "Announce the rebrand", "detail": "Post: 'This page is shifting focus to [niche]. Stick around if you're into it!'"},
            {"step": "2", "action": "Archive personal posts", "detail": "Archive (don't delete) all off-niche content. Keep your top performers if relevant."},
            {"step": "3", "action": "Update profile completely", "detail": "New username (if possible), new bio, new profile pic — all niche-aligned."},
            {"step": "4", "action": "Post 20+ niche pieces before promoting", "detail": "Fill the grid/feed before telling anyone about the rebrand."},
            {"step": "5", "action": "Go hard for 30 days", "detail": "Algorithm re-learning takes 2-4 weeks. Daily posting minimum."},
            {"step": "6", "action": "Engage aggressively in new niche", "detail": "Comment on 30+ niche posts/day. Follow niche leaders. Join niche Discords/groups."},
        ],
        "what_to_expect": [
            "Week 1-2: Reach drops (algorithm confused)",
            "Week 3-4: Reach recovers as algorithm reclassifies you",
            "Month 2+: New niche audience starts growing",
        ],
    }


def _growth_hacks(niche: str) -> list[dict[str, str]]:
    return [
        {"hack": "F/U Loop", "detail": "Follow 50-100 accounts in your niche daily → many follow back → unfollow after 48h if no follow-back (FollowingLike tool)"},
        {"hack": "Comment Farming", "detail": f"Drop thoughtful comments on viral {niche} posts FIRST (within 5 mins of posting) to get likes on your comment = free traffic"},
        {"hack": "Collab Shoutout-for-Shoutout", "detail": "DM pages your size: 'Want to do a S4S?' — post each other's pages in your story/post"},
        {"hack": "TikTok Pinned Reply", "detail": "Pin a comment on every post asking a question — drives comment loops the algo loves"},
        {"hack": "Cross-Platform Funnel", "detail": "Post on TikTok first. Take the viral TikToks and repost to Instagram Reels + YouTube Shorts with slight variation"},
        {"hack": "Trend Surfing", "detail": f"Every morning: check TikTok Discover, YouTube Trending, Twitter trending. Make a {niche} version of the #1 trend SAME DAY"},
        {"hack": "Hashtag Rotation", "detail": "Never use the SAME hashtag set twice in a row. Rotate 3-4 hashtag stacks to avoid shadow limits"},
        {"hack": "Engagement Pods", "detail": f"Join Telegram groups of {niche} creators (same size). Like/comment on each other's posts within first hour"},
    ]


def _posting_tools() -> dict[str, list[dict[str, str]]]:
    return {
        "scheduling": [
            {"tool": "Buffer", "url": "buffer.com", "note": "Free tier: 3 channels, 10 posts each. Best for cross-posting."},
            {"tool": "Later", "url": "later.com", "note": "Strong Instagram/TikTok scheduling. Visual calendar."},
            {"tool": "Metricool", "url": "metricool.com", "note": "Free analytics + scheduling for TikTok, Instagram, YouTube, Twitter."},
        ],
        "editing": [
            {"tool": "CapCut", "url": "capcut.com", "note": "Free, TikTok-native editor. Auto-captions, trending templates."},
            {"tool": "Canva", "url": "canva.com", "note": "Best for graphics, carousels, thumbnails. Free tier excellent."},
            {"tool": "InShot", "url": "inshot.com", "note": "Mobile video editor. Best for Reels/Shorts final polish."},
        ],
        "research": [
            {"tool": "TikTok Creative Center", "url": "ads.tiktok.com/business/creativecenter", "note": "FREE: trending hashtags, sounds, videos by region/industry."},
            {"tool": "vidIQ", "url": "vidiq.com", "note": "YouTube keyword/trend research. Free tier useful."},
            {"tool": "Exploding Topics", "url": "explodingtopics.com", "note": "Find trends BEFORE they go viral. 2-week free trial."},
        ],
        "analytics": [
            {"tool": "Social Blade", "url": "socialblade.com", "note": "Spy on competitor growth stats. 100% free."},
            {"tool": "HypeAuditor", "url": "hypeauditor.com", "note": "Fake follower detection + niche benchmarks."},
            {"tool": "Metricool", "url": "metricool.com", "note": "Multi-platform analytics dashboard. Free tier solid."},
        ],
    }


def _common_mistakes() -> list[dict[str, str]]:
    return [
        {"mistake": "Inconsistent posting", "fix": "Schedule 2 weeks ahead BEFORE you start. Gaps kill algorithm momentum."},
        {"mistake": "Copying content without adding value", "fix": "Always add something: your caption, a trending sound, a text overlay with your take."},
        {"mistake": "Too broad a niche", "fix": "'Health' is too broad. 'Keto meal prep for busy moms' is a niche. Niche down to grow faster."},
        {"mistake": "Ignoring analytics", "fix": "Check analytics every 3 days. Kill what doesn't work by week 2. Double what does."},
        {"mistake": "No CTA on every post", "fix": "Every video, every caption should have ONE call-to-action: follow, comment, share, or click link."},
        {"mistake": "Buying followers", "fix": "Kills your engagement rate forever. Algorithm shows your posts to fake accounts = no reach."},
        {"mistake": "Same hashtags every post", "fix": "Rotate 3-4 different hashtag stacks. Same tags every post triggers spam filters."},
        {"mistake": "Posting without a hook", "fix": "If the first 1-3 seconds don't stop a scroll, nothing else matters."},
        {"mistake": "Ignoring comments/DMs", "fix": "Reply to EVERY comment in the first hour. The algorithm counts comment interactions."},
    ]
