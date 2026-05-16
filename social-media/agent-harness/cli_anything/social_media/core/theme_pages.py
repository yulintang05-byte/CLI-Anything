"""Theme page strategy: how to build & monetize converting theme pages."""

from datetime import datetime


THEME_PAGE_NICHES = {
    "motivation_luxury": {
        "name": "Motivation & Luxury Lifestyle",
        "description": "Repost motivational quotes over luxury/car/mansion footage",
        "monetization": ["Digital products", "Affiliate (Amazon/ClickBank)", "Shoutouts", "Coaching"],
        "content_ratio": {"reposts": 70, "original": 30},
        "avg_cpm": "$8-15",
        "time_to_5k": "30-60 days with daily posting",
        "example_accounts": ["@millionaire_mentor", "@luxurymindset"],
        "tools": ["CapCut", "Canva", "Epidemic Sound"],
    },
    "fitness_aesthetics": {
        "name": "Fitness & Body Transformation",
        "description": "Before/after transformations, workout clips, fit aesthetic shots",
        "monetization": ["Fitness programs", "Supplement affiliate", "Coaching DMs", "Merch"],
        "content_ratio": {"reposts": 60, "original": 40},
        "avg_cpm": "$6-12",
        "time_to_5k": "45-90 days",
        "example_accounts": ["@aestheticmotivation_", "@gymrat"],
        "tools": ["CapCut", "Lightroom presets", "Epidemic Sound"],
    },
    "finance_mindset": {
        "name": "Finance & Money Mindset",
        "description": "Money tips, investing basics, passive income, wealth mindset",
        "monetization": ["Course sales", "Affiliate (credit cards, brokers)", "Newsletter", "Consulting"],
        "content_ratio": {"educational": 60, "inspirational": 30, "promotional": 10},
        "avg_cpm": "$15-30",
        "time_to_5k": "60-120 days (harder niche, higher reward)",
        "tools": ["Canva", "CapCut", "Notion"],
    },
    "relationship_dating": {
        "name": "Relationship & Dating Advice",
        "description": "Red flag/green flag content, dating tips, self-improvement for dating",
        "monetization": ["Dating ebooks", "Coaching", "Affiliate products"],
        "content_ratio": {"reposts": 50, "original": 50},
        "avg_cpm": "$4-8",
        "time_to_5k": "30-45 days (very viral niche)",
        "tools": ["CapCut", "Canva"],
    },
    "food_recipe": {
        "name": "Food & Recipe Reposts",
        "description": "Repost viral recipe videos with your own branding/overlay",
        "monetization": ["Kitchen affiliate", "Sponsored posts", "Recipe ebooks", "AdSense (YouTube)"],
        "content_ratio": {"reposts": 80, "original": 20},
        "avg_cpm": "$5-10",
        "time_to_5k": "30-60 days",
        "tools": ["CapCut", "Canva", "Amazon Associates"],
    },
    "travel_adventure": {
        "name": "Travel & Adventure",
        "description": "Stunning travel clips, destination guides, travel hacks",
        "monetization": ["Booking affiliate", "Travel brand deals", "Presets/filters", "Guides"],
        "content_ratio": {"reposts": 60, "original": 40},
        "avg_cpm": "$8-18",
        "time_to_5k": "60-120 days",
        "tools": ["LightRoom", "CapCut", "Canva"],
    },
    "quote_aesthetic": {
        "name": "Quote & Aesthetic Page",
        "description": "Dark/light aesthetic quotes, poetry, relatable content",
        "monetization": ["Print-on-demand merch", "Shoutouts", "Presets"],
        "content_ratio": {"reposts": 80, "original": 20},
        "avg_cpm": "$3-6",
        "time_to_5k": "14-30 days (easiest to grow)",
        "tools": ["Canva", "Pinterest", "Unsplash"],
    },
    "tech_ai": {
        "name": "Tech & AI News",
        "description": "AI tools, tech news, future predictions, coding tips",
        "monetization": ["SaaS affiliate", "Courses", "Newsletter", "Consulting"],
        "content_ratio": {"educational": 70, "entertaining": 20, "promotional": 10},
        "avg_cpm": "$20-40",
        "time_to_5k": "90-180 days (slow but extremely valuable)",
        "tools": ["CapCut", "Canva", "ChatGPT for scripting"],
    },
}

CONVERSION_PLAYBOOK = {
    "funnel_stages": {
        "awareness": "Viral content → Get views & followers (FYP/trending hooks)",
        "interest": "Consistent value → Build trust (niche content, series)",
        "desire": "Social proof + results → They want what you offer",
        "action": "CTA → DM/link-in-bio/landing page → Sale or lead",
    },
    "bio_link_strategy": [
        "Use Linktree, Stan Store, or Beacons.ai as your bio link hub",
        "Landing page should match your niche aesthetic exactly",
        "Lead magnet: free PDF/checklist to capture emails (email list = real asset)",
        "Email sequence (3-7 emails) selling your core product automatically",
    ],
    "dms_to_sales": [
        "Reply to EVERY comment with a question to spark DM conversation",
        "Story poll: 'Want my free {X}?' → Yes/No → DMs open",
        "Use ManyChat or similar to auto-DM link when they comment a keyword",
        "DM script: open with value, ask their pain point, offer solution",
    ],
    "viral_content_formula": {
        "hook": "First 1-3 seconds must stop the scroll — question, shock, or relatable pain",
        "value": "Deliver on the hook immediately — no fluff",
        "retention": "Pattern interrupts every 3-5 seconds: cuts, text, music change",
        "cta": "End with: follow, comment, share, or DM me '{keyword}'",
    },
}

REPOST_LEGAL_GUIDE = {
    "safe_methods": [
        "Duet/Stitch (TikTok native — always safe with credit)",
        "Ask permission via DM (screenshot + post shows credibility)",
        "Use royalty-free/Creative Commons content from Pexels, Pixabay, Unsplash",
        "Purchase license for premium content (Storyblocks, Artgrid)",
    ],
    "risks": [
        "Direct repost without permission = copyright strike risk",
        "Music without license = muted audio or takedown",
        "Watermarked reposts (TikTok logo) get suppressed by other platforms' algorithms",
    ],
    "watermark_removal": [
        "SnapTik.app, SSSTik — download TikTok without watermark (for personal study)",
        "Always add YOUR OWN overlay, text, or audio before reposting",
        "Transform the content: crop, add voiceover, add text — makes it your edit",
    ],
    "disclaimer": "Always credit original creators. When in doubt, ask first. Copyright law varies by country.",
}

MONETIZATION_ROADMAP = [
    {"stage": "0-1K followers", "focus": "Consistency + niche clarity. No monetization yet.",
     "actions": ["Post daily", "Study top 10 accounts in your niche", "Engage for 30 min/day"]},
    {"stage": "1K-5K followers", "focus": "Build email list. Start affiliate links.",
     "actions": ["Add lead magnet to bio link", "Sign up for Amazon Associates + ClickBank",
                 "Post 1 story/day with CTA to bio link"]},
    {"stage": "5K-10K followers", "focus": "Shoutout deals + digital products.",
     "actions": ["List yourself on Shoutcart/GrapeVine", "Launch $7-27 ebook or preset pack",
                 "Pitch brands in your niche for free product first, then paid"]},
    {"stage": "10K-50K followers", "focus": "Premium products + brand deals.",
     "actions": ["Launch $97-297 course or coaching", "Approach brands for $500-2000/post deals",
                 "Add YouTube for AdSense income"]},
    {"stage": "50K+ followers", "focus": "Scale all channels, hire editor/VA.",
     "actions": ["$2000-10000/month realistic target", "Batch-create with a team",
                 "Build second/third niche account"]},
]

TOOLS_STACK = {
    "content_creation": {
        "video_editing": ["CapCut (free, best for TikTok/Reels)", "DaVinci Resolve (free, pro)", "Premiere Pro"],
        "design": ["Canva (free tier enough)", "Adobe Express"],
        "audio": ["Epidemic Sound ($15/mo)", "Artlist ($200/yr)", "TikTok native sounds (free)"],
        "ai_tools": ["ChatGPT — scripts, captions, hooks", "ElevenLabs — AI voiceover",
                     "Runway/Pika — AI video clips", "Midjourney — thumbnail backgrounds"],
    },
    "scheduling": {
        "free": ["Buffer (3 channels free)", "Later (10 posts/mo free)", "TikTok native scheduler"],
        "paid": ["Publer ($12/mo)", "Metricool ($22/mo)", "Hootsuite ($99/mo)"],
    },
    "analytics": {
        "free": ["Platform native analytics (TikTok/YouTube Studio)",
                 "Google Trends (spot rising topics)", "Exploding Topics"],
        "paid": ["Social Blade (track competitors)", "Tubular Labs", "Sprout Social"],
    },
    "monetization": {
        "link_in_bio": ["Stan Store (5% fee, best for creators)", "Beacons.ai (free)", "Linktree"],
        "digital_products": ["Gumroad (10% fee)", "Lemon Squeezy (5%)", "Teachable (courses)"],
        "affiliate": ["Amazon Associates", "ClickBank", "ShareASale", "Impact.com"],
        "brand_deals": ["AspireIQ", "Grapevine", "Shoutcart", "direct DM to brands"],
    },
}


def get_niche_playbook(niche: str) -> dict:
    """Get full playbook for a specific theme page niche."""
    key = niche.lower().replace(" ", "_").replace("-", "_")
    # Fuzzy match
    for k, v in THEME_PAGE_NICHES.items():
        if key == k or key in k or k in key:
            return {
                "niche_key": k,
                **v,
                "conversion_playbook": CONVERSION_PLAYBOOK,
                "monetization_roadmap": MONETIZATION_ROADMAP,
                "legal_guide": REPOST_LEGAL_GUIDE,
                "tools_stack": TOOLS_STACK,
                "generated_at": datetime.utcnow().isoformat() + "Z",
            }
    return {
        "error": f"Niche '{niche}' not found.",
        "available_niches": list(THEME_PAGE_NICHES.keys()),
        "tip": "Pick the closest niche or use 'all' to see everything.",
    }


def list_niches() -> dict:
    return {
        "available_niches": [
            {"key": k, "name": v["name"], "avg_cpm": v["avg_cpm"], "time_to_5k": v["time_to_5k"]}
            for k, v in THEME_PAGE_NICHES.items()
        ],
        "recommendation": "Finance & Tech have highest CPM. Quote & Relationship grow fastest.",
        "tools_stack": TOOLS_STACK,
    }


def full_theme_page_guide() -> dict:
    return {
        "niches": THEME_PAGE_NICHES,
        "conversion_playbook": CONVERSION_PLAYBOOK,
        "monetization_roadmap": MONETIZATION_ROADMAP,
        "legal_guide": REPOST_LEGAL_GUIDE,
        "tools_stack": TOOLS_STACK,
        "quick_start_steps": [
            "1. Pick ONE niche from the list above",
            "2. Create accounts on TikTok + Instagram Reels (max cross-post reach)",
            "3. Optimise bio with hook + emoji + CTA + niche keywords",
            "4. Set up Stan Store or Beacons.ai as bio link",
            "5. Study top 5 accounts in your niche — notice patterns",
            "6. Post 1-3 times/day using trending sounds & hashtag formula",
            "7. Engage: reply to every comment for first 1 hour post-publish",
            "8. Track: keep posting formats that get >2% engagement, cut the rest",
            "9. At 1K followers: add lead magnet & affiliate links",
            "10. At 5K followers: launch first digital product ($7-27 entry point)",
        ],
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
