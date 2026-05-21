"""
Account optimization engine.

Covers: posting schedules, bio optimization, content pillars,
engagement strategy, growth levers, and cross-platform linking.
"""
from typing import Dict, List, Optional


# ─── Posting schedule data (based on aggregated creator economy research) ─────

POSTING_SCHEDULES: Dict[str, Dict] = {
    "tiktok": {
        "minimum":  "1x/day",
        "optimal":  "3-5x/day",
        "maximum":  "5-7x/day",
        "best_times_est": ["7-9 AM", "12-3 PM", "7-9 PM"],
        "best_days":      ["Tuesday", "Thursday", "Friday", "Saturday"],
        "consistency_rule": "Posting consistently matters MORE than posting volume. 1/day every day beats 7/day once a week.",
        "new_account_ramp": "Post 3x/day for the first 2 weeks to accelerate the algorithm learning your audience.",
    },
    "instagram": {
        "minimum":  "1x/day Reels + 3 Stories",
        "optimal":  "1 Reel/day + 5-7 Stories/day + 3 Carousels/week",
        "maximum":  "3 Reels/day",
        "best_times_est": ["6-9 AM", "11 AM-1 PM", "7-9 PM"],
        "best_days":      ["Monday", "Wednesday", "Thursday"],
        "consistency_rule": "Reels > Carousels > Feed Photos for organic reach in 2024-2025.",
        "new_account_ramp": "Start with 1 Reel/day for 30 days to build initial data for the algorithm.",
    },
    "youtube": {
        "minimum":  "1x/week",
        "optimal":  "2-3x/week",
        "maximum":  "1/day",
        "best_times_est": ["2-4 PM", "8-11 PM"],
        "best_days":      ["Thursday", "Friday", "Saturday"],
        "consistency_rule": "Upload day/time consistency trains subscribers to expect content.",
        "new_account_ramp": "Publish 30 videos before judging channel performance — algorithm needs data.",
    },
    "twitter": {
        "minimum":  "3x/day",
        "optimal":  "5-7x/day",
        "maximum":  "15x/day",
        "best_times_est": ["8-10 AM", "12-1 PM", "5-6 PM"],
        "best_days":      ["Tuesday", "Wednesday", "Thursday"],
        "consistency_rule": "Twitter rewards high-frequency posting. Threads perform significantly better than single tweets.",
        "new_account_ramp": "Reply to large accounts in your niche for the first 2 weeks to build impressions.",
    },
}


# ─── Bio optimization templates ───────────────────────────────────────────────

BIO_TEMPLATES: Dict[str, Dict] = {
    "tiktok": {
        "character_limit": 80,
        "formula":         "[What you do] | [Who you help] | [CTA or hook]",
        "examples": [
            "Fitness coach helping busy moms lose 20lbs | Free plan in bio link",
            "Stock market breakdowns, daily | Follow for weekly picks",
            "NYC chef | 5-ingredient meals that slap | New video every day",
        ],
        "rules": [
            "Include 1 clear CTA (call to action) pointing to your link-in-bio.",
            "Use line breaks to make it scannable.",
            "Emojis add personality but don't overuse — max 2-3.",
            "State your niche in the first 5 words so TikTok can categorize you.",
        ],
    },
    "instagram": {
        "character_limit": 150,
        "formula":         "[Role/Identity] | [Value proposition] | [Social proof] | [CTA]",
        "examples": [
            "Personal Finance Coach 📈\nHelping 20-somethings build wealth\n10K+ students | Forbes featured\n👇 Free budget template",
            "Travel Creator ✈️\nShowing you how to travel for FREE\n50+ countries | 1M+ views\n👇 Get my packing guide",
        ],
        "rules": [
            "Put your most important keyword in your Name field (not just bio) — it's searchable.",
            "Link-in-bio tools (Linktree, Beacons, Stan Store) let you monetize directly from bio.",
            "Add your location if you're a local business.",
            "Update your bio CTA to match your current promotion/content push.",
        ],
    },
    "youtube": {
        "character_limit": 1000,
        "formula":         "[Channel mission] | [Upload schedule] | [What subscribers get] | [Links]",
        "examples": [
            "Teaching you how to build profitable online businesses from scratch.\nNew videos every Tuesday and Friday.\nSubscribe for actionable strategies, not theory.",
        ],
        "rules": [
            "First 100 characters show in search — make them hook.",
            "Include your upload schedule to set subscriber expectations.",
            "Add keywords naturally — YouTube uses channel description for search.",
            "Include links to all your other platforms.",
        ],
    },
}


# ─── Content pillars framework ────────────────────────────────────────────────

CONTENT_PILLARS = {
    "entertainment":  "Pure entertainment — hooks, trends, skits, humor. No niche expertise required.",
    "education":      "Teach something valuable in your niche. 'How to', tutorials, breakdowns.",
    "inspiration":    "Motivate or transform. Before/after, transformations, success stories.",
    "connection":     "Be relatable. GRWM, day-in-the-life, opinions, Q&A, behind the scenes.",
    "promotion":      "Soft or hard sell of your product/service/affiliate. Max 20% of content.",
}

CONTENT_RATIOS = {
    "new_account":    {"entertainment": 40, "education": 30, "inspiration": 20, "connection": 10, "promotion": 0},
    "growing":        {"entertainment": 30, "education": 30, "inspiration": 20, "connection": 15, "promotion": 5},
    "monetized":      {"entertainment": 25, "education": 25, "inspiration": 20, "connection": 15, "promotion": 15},
}


def optimize_account(
    platform: str,
    niche: str = "",
    stage: str = "growing",
) -> Dict:
    """Return full account optimization plan for a platform and growth stage."""
    platform_key = platform.lower()
    schedule = POSTING_SCHEDULES.get(platform_key, POSTING_SCHEDULES["tiktok"])
    bio_tmpl  = BIO_TEMPLATES.get(platform_key, BIO_TEMPLATES["tiktok"])
    ratio     = CONTENT_RATIOS.get(stage, CONTENT_RATIOS["growing"])

    return {
        "platform":        platform,
        "niche":           niche,
        "stage":           stage,
        "posting_schedule": schedule,
        "bio_optimization": bio_tmpl,
        "content_pillars":  CONTENT_PILLARS,
        "content_ratio":    ratio,
        "growth_levers":    growth_levers(platform_key),
        "engagement_rules": engagement_rules(platform_key),
        "monetization_path": monetization_path(platform_key, stage),
    }


def growth_levers(platform: str) -> List[Dict]:
    """Return top growth levers for the platform."""
    levers = {
        "tiktok": [
            {"lever": "Hook quality", "impact": "HIGH", "tip": "First 1-3 seconds determine 80% of video performance. Test multiple hooks."},
            {"lever": "Trending audio", "impact": "HIGH", "tip": "Use trending sounds within 24-72h for algorithmic boost."},
            {"lever": "Duets & Stitches", "impact": "MED", "tip": "Engage viral creators — their audience becomes your audience."},
            {"lever": "Posting frequency", "impact": "MED", "tip": "More at-bats = more chances for a viral video. Post 3x/day."},
            {"lever": "Comment engagement", "impact": "HIGH", "tip": "Reply to every comment for the first hour after posting — it signals engagement to the algorithm."},
            {"lever": "Watch time", "impact": "HIGH", "tip": "Create loops — content that makes viewers rewatch. TikTok loves completion rate + replays."},
            {"lever": "Niche consistency", "impact": "MED", "tip": "TikTok builds a 'topic cluster' for your account. Stay on-topic to build an engaged audience faster."},
        ],
        "instagram": [
            {"lever": "Reels",              "impact": "HIGH", "tip": "Reels get 3x the organic reach of feed photos. Shift 80% of content to Reels."},
            {"lever": "Stories daily",      "impact": "MED",  "tip": "Daily Stories keep you top-of-mind and maintain your relationship with existing followers."},
            {"lever": "Collaborations",     "impact": "HIGH", "tip": "Instagram's 'Collab' feature shares a post to both audiences simultaneously."},
            {"lever": "Carousel posts",     "impact": "MED",  "tip": "Carousels have the highest save rate — saves signal quality content to Instagram."},
            {"lever": "Response speed",     "impact": "MED",  "tip": "Respond to comments and DMs within 1 hour of posting for algorithmic boost."},
            {"lever": "Cross-post Reels from TikTok", "impact": "HIGH", "tip": "Repurpose TikTok content to Instagram Reels. Remove watermark first (use SnapTik)."},
        ],
        "youtube": [
            {"lever": "Thumbnail CTR",      "impact": "HIGH", "tip": "Thumbnail is the #1 factor for click-through rate. A/B test thumbnails using YouTube Studio."},
            {"lever": "Titles (SEO)",       "impact": "HIGH", "tip": "Research keywords using TubeBuddy or VidIQ. Include the keyword in the first 60 chars."},
            {"lever": "Retention",          "impact": "HIGH", "tip": "Average view duration > 50% signals quality. Use pattern interrupts every 60-90 seconds."},
            {"lever": "Playlists",          "impact": "MED",  "tip": "Playlists increase session time and recommended video probability."},
            {"lever": "End screens + cards","impact": "MED",  "tip": "Direct viewers to related videos — keeps them in your channel ecosystem."},
            {"lever": "Community posts",    "impact": "LOW",  "tip": "Available at 500+ subscribers. Drives engagement between uploads."},
        ],
    }
    return levers.get(platform, levers["tiktok"])


def engagement_rules(platform: str) -> List[str]:
    rules = {
        "tiktok": [
            "Reply to top comments with a video response — these appear in comments and discover feeds.",
            "Pin a comment asking a question to encourage responses ('Comment your answer below').",
            "Like every comment within the first hour — increases algorithmic confidence.",
            "Use the 'Q&A' feature to answer audience questions as video replies.",
            "Go live 1-2x per week once you hit 1K followers — lives boost overall account reach.",
        ],
        "instagram": [
            "Reply to all comments within the first 30 minutes of posting.",
            "Use Instagram's 'Close Friends' for exclusive content — drives Story views.",
            "Add interactive elements to Stories: polls, questions, quizzes, sliders.",
            "DM new followers personally (or with automation) to start a conversation.",
            "Comment meaningfully on 10-20 posts in your niche every day ('reciprocal engagement').",
        ],
        "youtube": [
            "Respond to 100% of comments for the first 500 subscribers.",
            "Heart comments — it notifies the commenter and drives them back.",
            "Pin a comment asking a question to boost comment count.",
            "Create 'Community' posts to keep subscribers engaged between uploads.",
            "Reply to comments asking questions with a link to a related video.",
        ],
    }
    return rules.get(platform, rules["tiktok"])


def monetization_path(platform: str, stage: str) -> Dict:
    paths = {
        "tiktok": {
            "milestones": [
                {"followers": "1K",  "unlock": "Live streaming"},
                {"followers": "10K", "unlock": "Link in bio + TikTok Shop"},
                {"followers": "10K + 100K views/30d", "unlock": "TikTok Creator Rewards ($0.02-0.04/1K views)"},
            ],
            "revenue_streams": [
                "Brand deals (DM outreach at 10K+, incoming at 50K+)",
                "TikTok Shop affiliate — promote products for 5-30% commission",
                "Digital products via link-in-bio (Stan Store, Beacons)",
                "TikTok Creator Rewards Program",
                "Coaching or consulting offers",
            ],
            "early_strategy": "Don't chase followers — chase email list. Add lead magnet to bio link from day 1.",
        },
        "instagram": {
            "milestones": [
                {"followers": "1K",  "unlock": "Instagram Shopping basics"},
                {"followers": "10K", "unlock": "Link in bio clicks trackable, influencer deals viable"},
                {"followers": "100K","unlock": "Meta Creator Bonus (invite-only), major brand deals"},
            ],
            "revenue_streams": [
                "Sponsored posts ($100-$2,000/post at 10K-100K followers)",
                "Instagram Subscriptions (exclusive content for monthly fee)",
                "Affiliate marketing via link-in-bio",
                "Digital products (presets, templates, courses)",
                "Lead generation for local businesses",
            ],
            "early_strategy": "Build a micro-niche audience of 1K-10K with high engagement. Brands pay CPM on engagement, not follower count.",
        },
        "youtube": {
            "milestones": [
                {"subscribers": "500",   "unlock": "Community posts"},
                {"subscribers": "1K + 4K watch hours", "unlock": "YouTube Partner Program (AdSense ~$3-10 RPM)"},
                {"subscribers": "20K",   "unlock": "Channel memberships"},
                {"subscribers": "100K",  "unlock": "Super Thanks, significant brand deal rates"},
            ],
            "revenue_streams": [
                "AdSense revenue (avg $2-10 per 1,000 views by niche)",
                "Channel memberships ($4.99-$49.99/month)",
                "Super Thanks / Super Chat from live streams",
                "Affiliate links in descriptions (Amazon, software, courses)",
                "Sponsorships (typical rate: $20-$50 per 1,000 views)",
                "Courses and digital products sold via end screens",
            ],
            "early_strategy": "Finance, tech, and business niches earn 3-10x more from AdSense than entertainment. Pick niche based on CPM, not passion alone.",
        },
    }
    return paths.get(platform, paths["tiktok"])


def audit_account(handle: str, platform: str) -> Dict:
    """Return a structured audit checklist for an account."""
    return {
        "handle":   handle,
        "platform": platform,
        "checklist": [
            {"item": "Profile photo",          "question": "High-res, face visible, consistent across platforms?"},
            {"item": "Username",               "question": "Short, memorable, searchable, no underscores/numbers?"},
            {"item": "Bio",                    "question": "Clear niche, value prop, CTA, and relevant keywords?"},
            {"item": "Link in bio",            "question": "Pointing to a lead magnet or monetized destination?"},
            {"item": "Pinned posts/videos",    "question": "Best-performing or introductory content pinned?"},
            {"item": "Content consistency",    "question": "Visual brand (colors, font, style) consistent?"},
            {"item": "Posting frequency",      "question": "Posting at least minimum frequency for platform?"},
            {"item": "Niche focus",            "question": "Does every post serve the same core audience?"},
            {"item": "Hook quality",           "question": "Do first 3 seconds of each video stop the scroll?"},
            {"item": "Hashtag strategy",       "question": "Using relevant, non-banned hashtags on each post?"},
            {"item": "Cross-promotion",        "question": "Linking to other platforms in bio and videos?"},
            {"item": "Email list",             "question": "Capturing emails via lead magnet linked from bio?"},
        ],
        "next_steps": [
            "Run through each checklist item and score 1 (missing) to 3 (excellent).",
            "Fix all score-1 items before optimizing score-2 items.",
            "Re-audit after 30 days of consistent posting.",
        ],
    }
