#!/usr/bin/env python3
"""Theme page creation and conversion guide — full playbook for building, growing,
and monetizing theme pages on TikTok, YouTube, and Instagram."""

from datetime import datetime
from typing import Optional


THEME_PAGE_PLAYBOOK = {
    "what_is_a_theme_page": {
        "title": "What Is a Theme Page?",
        "content": (
            "A theme page is an account centered around a specific topic or aesthetic — "
            "not a personal brand. You curate, repost, and create content around that theme. "
            "Examples: @luxurylifestyle, @dogsooftiktok, @motivationquotes. "
            "You can run multiple theme pages simultaneously. "
            "Theme pages are the fastest path to monetization without showing your face."
        ),
    },
    "why_theme_pages_work": {
        "title": "Why Theme Pages Work (The Business Model)",
        "content": (
            "Theme pages work because: "
            "(1) You don't need original content — curate what already works. "
            "(2) You can automate and outsource most tasks. "
            "(3) Multiple revenue streams: ads, affiliates, sponsored posts, digital products. "
            "(4) Proven demand — you're joining a topic people already love. "
            "(5) Scale: one person can run 5-20 theme pages simultaneously."
        ),
    },
    "phase_1_setup": {
        "title": "Phase 1: Setup (Days 1-7)",
        "steps": [
            {
                "step": 1,
                "action": "Choose your niche",
                "detail": (
                    "Pick ONE niche. Use the 'profitable triangle': passion OR knowledge + "
                    "proven demand + monetization path. Run 'social-trends theme-pages niches' "
                    "to see ranked niches by conversion potential and competition."
                ),
            },
            {
                "step": 2,
                "action": "Create accounts on all platforms simultaneously",
                "detail": (
                    "Create TikTok + YouTube + Instagram accounts with the same username. "
                    "Don't put all eggs in one basket — platform bans are real. "
                    "Same content, different optimization per platform."
                ),
            },
            {
                "step": 3,
                "action": "Optimize profiles completely",
                "detail": (
                    "Profile photo: high-quality, on-brand image. "
                    "Username: niche keyword + memorable word (e.g., @luxurycarsdaily). "
                    "Bio: what you post + why to follow + CTA. "
                    "Link: use Beacons.ai or Stan Store — free with powerful features."
                ),
            },
            {
                "step": 4,
                "action": "Set up content sourcing pipeline",
                "detail": (
                    "Sources: Reddit (r/[niche] top posts), Pinterest, other creators' content, "
                    "stock footage (Pexels, Pixabay), AI-generated visuals. "
                    "Tools: CapCut (editing), Canva (graphics), TubeBuddy (YouTube), "
                    "Later/Buffer (scheduling)."
                ),
            },
            {
                "step": 5,
                "action": "Create your first 10 posts before posting anything",
                "detail": (
                    "Batch-create 10 posts before going live. This ensures consistency "
                    "when you start. Post 1-3/day from day 1 — the first 2 weeks are "
                    "critical for algorithmic trust-building."
                ),
            },
        ],
    },
    "phase_2_growth": {
        "title": "Phase 2: Growth (Days 8-90)",
        "steps": [
            {
                "step": 1,
                "action": "Post 1-3x daily on TikTok, 3-5x Shorts, 1x Instagram",
                "detail": (
                    "Consistency beats quality at this stage. "
                    "Use trending audio on TikTok (check the 'sounds' section). "
                    "On YouTube Shorts, post the same content but re-edit for 9:16."
                ),
            },
            {
                "step": 2,
                "action": "Engage in the first 60 minutes of every post",
                "detail": (
                    "Reply to every comment within 1 hour of posting. "
                    "Ask a question in the comments yourself to spark engagement. "
                    "Like 50-100 posts in your niche daily to get follow-backs."
                ),
            },
            {
                "step": 3,
                "action": "Track what works and double down",
                "detail": (
                    "After 30 posts, analyze: which format gets most views? "
                    "Most saves? Most shares? Double output of that format. "
                    "A/B test thumbnails (YouTube) and cover frames (TikTok)."
                ),
            },
            {
                "step": 4,
                "action": "Use the 80/20 content rule",
                "detail": (
                    "80% proven content (repost/recreate what already went viral in your niche), "
                    "20% original experiments. Don't reinvent the wheel — study what works "
                    "for top accounts in your niche and replicate the format, not the content."
                ),
            },
            {
                "step": 5,
                "action": "Collaborate and duet/stitch",
                "detail": (
                    "Duet viral videos in your niche with your reaction/commentary. "
                    "This borrows the viral video's distribution. "
                    "Comment on large accounts' posts early when they post — "
                    "your comment gets seen by their entire audience."
                ),
            },
        ],
    },
    "phase_3_monetization": {
        "title": "Phase 3: Monetization (90+ days, 5K+ followers)",
        "revenue_streams": [
            {
                "stream": "Affiliate Marketing",
                "when_to_start": "Day 1",
                "earning_potential": "$500-$10,000/month",
                "how": (
                    "Sign up for: Amazon Associates, ShareASale, Impact, Commission Junction. "
                    "Add affiliate links in bio via Linktree/Beacons. "
                    "Create 'best products for [niche]' content. "
                    "Disclose affiliates as required by FTC."
                ),
                "best_niches": ["tech", "beauty", "fitness", "home", "pets"],
            },
            {
                "stream": "TikTok Creator Fund / YouTube AdSense",
                "when_to_start": "At 10K followers (TikTok) / 1K subs + 4K hours (YouTube)",
                "earning_potential": "$50-$500/month at start",
                "how": (
                    "Not a primary income source. TikTok pays $0.02-$0.04 per 1000 views. "
                    "YouTube pays $2-$8 CPM for Shorts, $5-$25 for long-form. "
                    "Enable it but don't rely on it."
                ),
                "best_niches": ["finance", "tech", "education"],
            },
            {
                "stream": "Sponsored Posts",
                "when_to_start": "10K+ followers",
                "earning_potential": "$100-$5,000 per post",
                "how": (
                    "DM brands in your niche with a media kit. "
                    "Use platforms: AspireIQ, Influencer.co, Creator.co, TikTok Creator Marketplace. "
                    "Rate formula: $10-20 per 1,000 followers per post on Instagram, "
                    "$50-100 per 1,000 views expected on TikTok."
                ),
                "best_niches": ["beauty", "fitness", "food", "travel", "fashion"],
            },
            {
                "stream": "Digital Products",
                "when_to_start": "5K+ followers",
                "earning_potential": "$1,000-$50,000/month",
                "how": (
                    "Create: ebooks ($7-47), templates ($15-97), courses ($97-497), presets. "
                    "Sell via Gumroad, Stan Store, Teachable, or Etsy. "
                    "Use your theme page to drive traffic. "
                    "This is the highest-margin income stream — 90%+ profit margin."
                ),
                "best_niches": ["finance", "fitness", "beauty", "tech", "travel"],
            },
            {
                "stream": "Selling the Page",
                "when_to_start": "50K+ followers",
                "earning_potential": "$5,000-$100,000+ per sale",
                "how": (
                    "Theme pages sell for 12-36x monthly revenue on platforms like "
                    "Flippa, Motion Invest, or direct sale to brands. "
                    "A page earning $1,000/month can sell for $15,000-$36,000. "
                    "This is the 'exit strategy' for theme page builders."
                ),
                "best_niches": ["all"],
            },
        ],
    },
    "phase_4_scaling": {
        "title": "Phase 4: Scaling (Multiple Pages)",
        "content": (
            "Once your first page hits 10K+ and earns $500+/month consistently: "
            "(1) Document your exact content process into SOPs. "
            "(2) Hire a VA ($300-500/month) on Upwork/Fiverr to handle posting + engagement. "
            "(3) Launch a second page in a complementary niche. "
            "(4) Use automation tools: ManyChat (DM automation), Later (scheduling), "
            "    Buffer (cross-posting), Repurpose.io (auto-cross-post). "
            "(5) Target: 5 pages x $2,000/month = $10,000/month passive income."
        ),
    },
    "common_mistakes": {
        "title": "Common Mistakes That Kill Theme Pages",
        "mistakes": [
            "Posting inconsistently — the algorithm punishes gaps",
            "Niching too broadly (fitness) instead of specifically (home gym for women 30+)",
            "Ignoring engagement — posting and ghosting",
            "Not building an email list from day 1",
            "Relying solely on platform ad revenue",
            "Copying content exactly instead of remaking it in your own style",
            "Buying followers — kills engagement rate and algorithmic trust",
            "Not testing different content formats for first 30 days",
            "Starting monetization too early (before 1K engaged followers)",
            "Using the wrong hashtags (mega tags only, or hashtag stuffing)",
        ],
    },
    "tools_stack": {
        "title": "Essential Tools Stack",
        "free": [
            "CapCut — video editing, trending templates, auto-captions",
            "Canva — graphics, thumbnails, story templates",
            "Pexels/Pixabay — free stock video",
            "Beacons.ai — link in bio, digital product sales",
            "Google Trends — trend research",
            "TikTok Creative Center — official trend data",
            "YouTube Trending (youtube.com/feed/trending) — trending content",
        ],
        "paid": [
            "TubeBuddy ($9/mo) — YouTube SEO optimization",
            "VidIQ ($10/mo) — YouTube keyword research",
            "Later/Buffer ($15/mo) — cross-platform scheduling",
            "Repurpose.io ($25/mo) — auto cross-post TikTok to YouTube Shorts/Instagram",
            "Epidemic Sound ($15/mo) — royalty-free music for YouTube",
            "ManyChat ($15/mo) — comment automation and DM funnels",
        ],
    },
    "content_reposting_rules": {
        "title": "Content Reposting — Legal & Ethical Guidelines",
        "rules": [
            "Always credit original creators in caption or on-screen text",
            "Transform content — add commentary, subtitles, music, overlays",
            "Never repost content with original creator's watermark (especially TikTok → YouTube)",
            "If asked to remove content, comply immediately",
            "Original + transformed content always outperforms pure reposts",
            "Use the 'duet/stitch' feature on TikTok — this is platform-native and safe",
            "Stock footage, public domain, and creative commons content = safest bet",
        ],
    },
}


def get_full_playbook() -> dict:
    """Return the complete theme page playbook."""
    return {
        "title": "Complete Theme Page Creation & Conversion Playbook",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "sections": list(THEME_PAGE_PLAYBOOK.keys()),
        **THEME_PAGE_PLAYBOOK,
    }


def get_section(section_key: str) -> Optional[dict]:
    """Get a specific section of the playbook."""
    return THEME_PAGE_PLAYBOOK.get(section_key)


def get_quick_start(niche: str = "general") -> dict:
    """Return a condensed quick-start action list for a new theme page."""
    return {
        "niche": niche,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "week_1": [
            f"Choose final niche (you said: {niche})",
            "Create TikTok + YouTube + Instagram accounts with same username",
            "Optimize all three profiles (bio, photo, link in bio)",
            "Research top 10 accounts in your niche — note their format, hashtags, posting times",
            "Sign up for 2-3 affiliate programs in your niche",
            "Batch-create first 10 pieces of content",
            "Schedule and post 2x/day starting Day 7",
        ],
        "week_2_4": [
            "Post 2-3x/day on TikTok",
            "Reply to every comment within 1 hour",
            "Engage 30 min/day in niche (like, comment on similar content)",
            "Track metrics weekly — double down on what works",
            "Add trending audio to every TikTok post",
            "Start building email list via Beacons/Stan Store lead magnet",
        ],
        "month_2_3": [
            "Analyze top 10 posts — identify winning format",
            "Create a simple digital product (ebook, template, guide) — $7-47",
            "Reach out to 5 small brands for sponsored post opportunities",
            "Apply for TikTok Creator Rewards Program (10K followers required)",
            "Post Reels/Shorts versions of top TikTok posts",
        ],
        "key_metrics_to_track": [
            "Follower growth rate (target: 100-500/week initially)",
            "Average views per post",
            "Engagement rate (target: 5%+ on TikTok, 2%+ on YouTube)",
            "Profile visits (high = strong hook, low = fix thumbnails/titles)",
            "Link in bio clicks (target: 1-3% of views)",
        ],
    }


def get_conversion_guide(current_followers: int, platform: str) -> dict:
    """Get conversion strategy based on current account size."""
    if current_followers < 1000:
        phase = "building_trust"
        strategies = [
            "Focus 100% on content quality and consistency — don't monetize yet",
            "Build email list from day 1 with a free lead magnet",
            "Engage aggressively — reply to every comment",
            "No sponsored posts until 1K — looks desperate and damages credibility",
        ]
        primary_goal = "Hit 1K followers with 5%+ engagement rate"
    elif current_followers < 10000:
        phase = "early_monetization"
        strategies = [
            "Add affiliate links to bio — low friction, immediate revenue",
            "Create first digital product ($7-27 entry level)",
            "DM micro-brands for gifted/paid partnerships",
            "Start building a 'best of [niche]' content series for evergreen traffic",
            f"Apply for {platform} creator programs (TikTok needs 10K)",
        ]
        primary_goal = "Generate first $500/month"
    elif current_followers < 100000:
        phase = "scaling_revenue"
        strategies = [
            "Charge $200-2,000 per sponsored post",
            "Create a premium digital product ($97-497)",
            "Diversify across all platforms (cross-post everything)",
            "Build email list aggressively — offer lead magnet on every post",
            "Consider hiring VA for scheduling and engagement",
            "Sell page or launch second page",
        ]
        primary_goal = "Hit $5,000/month recurring revenue"
    else:
        phase = "business_operations"
        strategies = [
            "Hire full team: VA, video editor, content manager",
            "Launch multiple revenue streams simultaneously",
            "Approach top-tier brand deals ($5K-50K/post range)",
            "Create membership community or subscription",
            "Build your own product line",
            "Consider selling page for $50K-500K",
        ]
        primary_goal = "Build sustainable $10K-100K/month business"

    return {
        "platform": platform,
        "followers": current_followers,
        "phase": phase,
        "primary_goal": primary_goal,
        "strategies": strategies,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
