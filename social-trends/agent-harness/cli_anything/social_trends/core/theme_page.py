"""Theme page creation & monetization playbook.

A 'theme page' (also called a niche page or faceless account) re-posts or
curates content around a single topic without the creator appearing on camera.
This module provides structured guidance for finding, building, growing, and
monetizing them.
"""

from __future__ import annotations

NICHES: list[dict] = [
    {
        "niche": "Luxury Lifestyle",
        "platforms": ["TikTok", "Instagram"],
        "monetization": ["Brand deals", "Affiliate (watches, cars, hotels)", "Dropshipping"],
        "avg_cpm": "$8-20",
        "competition": "High",
        "growth_speed": "Fast",
        "content_sources": ["Reddit r/luxurylifestyle", "YouTube reposts", "Pexels luxury clips"],
    },
    {
        "niche": "Motivation / Success Mindset",
        "platforms": ["TikTok", "Instagram", "YouTube Shorts"],
        "monetization": ["Courses", "Affiliate (books, apps)", "Adsense", "Patreon"],
        "avg_cpm": "$4-12",
        "competition": "Very High",
        "growth_speed": "Very Fast",
        "content_sources": ["Podcast clips", "Book summaries", "Speech archives"],
    },
    {
        "niche": "Pet / Animals",
        "platforms": ["TikTok", "Instagram", "YouTube"],
        "monetization": ["Pet product affiliate", "Merch", "Adsense"],
        "avg_cpm": "$3-8",
        "competition": "Medium",
        "growth_speed": "Very Fast",
        "content_sources": ["Reddit r/aww", "User submissions", "Pexels animal clips"],
    },
    {
        "niche": "Finance / Crypto",
        "platforms": ["YouTube", "TikTok", "Instagram"],
        "monetization": ["Affiliate (exchanges, brokers)", "Courses", "Newsletter"],
        "avg_cpm": "$15-40",
        "competition": "High",
        "growth_speed": "Moderate",
        "content_sources": ["News aggregation", "Public earnings calls", "Twitter/X threads"],
    },
    {
        "niche": "Fitness / Weight Loss",
        "platforms": ["TikTok", "Instagram", "YouTube"],
        "monetization": ["Supplement affiliate", "Training programs", "Coaching"],
        "avg_cpm": "$6-18",
        "competition": "High",
        "growth_speed": "Fast",
        "content_sources": ["Transformation reposts (with permission)", "Exercise clips", "Nutrition facts"],
    },
    {
        "niche": "Facts / Did You Know",
        "platforms": ["TikTok", "YouTube Shorts", "Instagram Reels"],
        "monetization": ["Adsense", "Merch", "Affiliate"],
        "avg_cpm": "$2-6",
        "competition": "Medium",
        "growth_speed": "Very Fast",
        "content_sources": ["Wikipedia", "Reddit", "Science journals", "History archives"],
    },
    {
        "niche": "Travel",
        "platforms": ["Instagram", "TikTok", "YouTube"],
        "monetization": ["Hotel/flight affiliate", "Travel insurance affiliate", "Tourism boards"],
        "avg_cpm": "$5-15",
        "competition": "Medium-High",
        "growth_speed": "Moderate",
        "content_sources": ["Pexels/Unsplash travel footage", "Drone footage marketplaces"],
    },
    {
        "niche": "AI / Tech",
        "platforms": ["YouTube", "TikTok", "Twitter/X"],
        "monetization": ["SaaS affiliate", "Courses", "Consulting", "Newsletter"],
        "avg_cpm": "$12-35",
        "competition": "Growing",
        "growth_speed": "Very Fast",
        "content_sources": ["Product launches", "GitHub trending", "HackerNews", "ArXiv papers"],
    },
]


GROWTH_PLAYBOOK: list[dict] = [
    {
        "phase": "0-1K followers",
        "duration": "Days 1-30",
        "focus": "Volume & consistency",
        "tactics": [
            "Post 3-5x/day on TikTok, 2x/day on Instagram Reels",
            "Use 3-5 trending hashtags + 2-3 niche hashtags per post",
            "Ride trending sounds within 24-48h of them peaking",
            "Engage on top posts in your niche (first comments = visibility)",
            "Reply to every comment in the first hour of posting",
            "Cross-post every piece of content on all platforms",
        ],
        "goal": "Find your first viral format",
    },
    {
        "phase": "1K-10K followers",
        "duration": "Month 2-3",
        "focus": "Doubling down on what works",
        "tactics": [
            "Identify top 3 performing post formats and create series",
            "Start A/B testing thumbnails / first frames",
            "Join engagement groups (pods) in your niche — DM other creators",
            "Maintain 2-3 posts/day minimum",
            "Start building an email list or Telegram channel",
            "Collab with accounts at similar size",
        ],
        "goal": "10% follower-to-view ratio on average",
    },
    {
        "phase": "10K-100K followers",
        "duration": "Month 3-6",
        "focus": "Monetization & authority",
        "tactics": [
            "Apply for TikTok Creator Rewards Program (10K+ required)",
            "Pitch brands directly — use a media kit (Canva template)",
            "Launch first affiliate link (Amazon, ClickBank, ShareASale)",
            "Post 1-2 'pillar' pieces of content per week for long-term SEO",
            "Build a content calendar 2 weeks in advance",
            "Use analytics to post at YOUR specific audience peak times",
        ],
        "goal": "First $1,000/month from content",
    },
    {
        "phase": "100K+ followers",
        "duration": "Month 6+",
        "focus": "Scaling & diversification",
        "tactics": [
            "Hire a video editor (Upwork/Fiverr) — batch produce 2 weeks at once",
            "License your content to brands directly",
            "Launch a paid community (Skool, Patreon, Discord)",
            "Create a digital product (ebook, template, course)",
            "Repurpose long-form → short clips → newsletter → tweets",
            "Build a second account in a related niche",
        ],
        "goal": "Multiple revenue streams, $5K-20K/month",
    },
]


MONETIZATION_METHODS: list[dict] = [
    {
        "method": "TikTok Creator Rewards Program",
        "minimum": "10K followers, 100K views in 30 days, 18+",
        "earnings": "$0.40-$1.00 per 1,000 views (Rewards Program 2.0)",
        "effort": "Low (existing content)",
        "timeline": "Immediate after approval",
    },
    {
        "method": "YouTube Partner Program",
        "minimum": "1,000 subscribers + 4,000 watch hours OR 10M Shorts views",
        "earnings": "$2-20 CPM (varies heavily by niche)",
        "effort": "Low (existing content)",
        "timeline": "Apply after hitting threshold",
    },
    {
        "method": "Affiliate Marketing",
        "minimum": "Any size — larger = more conversions",
        "earnings": "3-50% commission per sale",
        "effort": "Low-Medium",
        "timeline": "Start Day 1 — add link in bio",
        "top_programs": ["Amazon Associates", "ClickBank", "ShareASale", "Impact", "CJ Affiliate"],
    },
    {
        "method": "Brand Sponsorships",
        "minimum": "10K+ engaged followers typical",
        "earnings": "$50-500 per post at 10K; $500-5,000+ at 100K",
        "effort": "Medium (outreach + deliverables)",
        "timeline": "Month 2-3",
        "platforms": ["AspireIQ", "Creator.co", "Grin", "Influencer.co", "direct outreach"],
    },
    {
        "method": "Digital Products",
        "minimum": "Engaged audience of any size",
        "earnings": "$27-$497 per unit (high margin)",
        "effort": "High upfront, low recurring",
        "timeline": "Month 3-6",
        "examples": ["Presets, templates, swipe files, ebooks, mini-courses"],
    },
    {
        "method": "Shoutouts / Page Promotions",
        "minimum": "5K+ followers",
        "earnings": "$20-200 per shoutout post",
        "effort": "Very Low",
        "timeline": "Month 1-2",
    },
]


CONTENT_SOURCING: list[dict] = [
    {"source": "Pexels", "url": "https://pexels.com", "type": "Video/Photo", "license": "Free commercial use"},
    {"source": "Pixabay", "url": "https://pixabay.com", "type": "Video/Photo/Music", "license": "Free commercial use"},
    {"source": "Coverr", "url": "https://coverr.co", "type": "Video", "license": "Free commercial use"},
    {"source": "Mixkit", "url": "https://mixkit.co", "type": "Video/Audio/Templates", "license": "Free commercial use"},
    {"source": "CapCut Templates", "url": "https://capcut.com", "type": "Video templates", "license": "Platform use"},
    {"source": "Reddit (with credit)", "url": "https://reddit.com", "type": "Clips/Stories", "license": "Attribution required"},
    {"source": "YouTube (clip + commentary)", "url": "https://youtube.com", "type": "Video", "license": "Fair use with transformation"},
    {"source": "ElevenLabs", "url": "https://elevenlabs.io", "type": "AI Voiceover", "license": "Commercial available"},
    {"source": "Epidemic Sound", "url": "https://epidemicsound.com", "type": "Royalty-free music", "license": "Paid subscription"},
]


def get_niche_recommendations(keywords: list[str]) -> list[dict]:
    """Return niches that match keywords."""
    kw_lower = [k.lower() for k in keywords]
    matches = []
    for niche in NICHES:
        niche_text = (niche["niche"] + " " + " ".join(niche.get("monetization", []))).lower()
        if any(k in niche_text for k in kw_lower):
            matches.append(niche)
    return matches if matches else NICHES[:3]


def get_full_playbook() -> dict:
    return {
        "niches": NICHES,
        "growth_playbook": GROWTH_PLAYBOOK,
        "monetization_methods": MONETIZATION_METHODS,
        "content_sourcing": CONTENT_SOURCING,
    }
