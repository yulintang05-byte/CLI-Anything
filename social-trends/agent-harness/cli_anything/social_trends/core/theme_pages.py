"""Converting theme pages — the complete playbook.

A theme page is a faceless social media account built around a topic (niche)
rather than a personal brand. Because you curate and repost content, you can
run multiple pages simultaneously, scale without showing your face, and
monetize through affiliate links, digital products, and sponsorships.

This module provides:
  - Top converting niches (ranked by monetization potential)
  - Step-by-step page setup guide
  - Content sourcing strategies (legal repurposing)
  - Conversion funnel architecture
  - Monetization playbook
  - Common mistakes to avoid
"""

from __future__ import annotations

from typing import Any


CONVERTING_NICHES = [
    {
        "niche": "Personal Finance & Investing",
        "monetization_potential": "$$$$",
        "why": "High CPM ($8–30 on YouTube), affiliate commissions $50–500/referral (brokers, budgeting apps)",
        "best_platforms": ["YouTube", "TikTok", "Instagram"],
        "content_types": ["Tips & tricks", "Tool reviews", "Case studies", "News commentary"],
        "affiliate_programs": ["Robinhood", "Acorns", "Personal Capital", "Credit Karma", "Coinbase"],
        "avg_rpm_youtube": "$12–30",
        "example_accounts": ["@financetok", "r/personalfinance", "The Budget Mom"],
    },
    {
        "niche": "Weight Loss & Fitness",
        "monetization_potential": "$$$$",
        "why": "Evergreen demand, massive affiliate market — supplements, programs, equipment",
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
        "content_types": ["Before/after", "Workout clips", "Meal prep", "Product reviews"],
        "affiliate_programs": ["MyFitnessPal", "Beachbody", "Amazon (equipment)", "Athletic Greens"],
        "avg_rpm_youtube": "$5–15",
        "example_accounts": ["@weightlossmotivation", "@fitnessgirls"],
    },
    {
        "niche": "Luxury Lifestyle & Wealth",
        "monetization_potential": "$$$",
        "why": "High engagement, luxury brand deals, crypto/forex affiliate programs",
        "best_platforms": ["Instagram", "TikTok"],
        "content_types": ["Luxury cars", "Mansions", "Travel", "Watch/jewelry collections"],
        "affiliate_programs": ["Luxury travel programs", "Trading platforms", "Luxury real estate leads"],
        "avg_rpm_youtube": "$3–8",
        "example_accounts": ["@luxurylifestyle", "@richlifestyle"],
    },
    {
        "niche": "Relationships & Dating",
        "monetization_potential": "$$$",
        "why": "Dating apps pay $2–5 CPI, courses sell for $97–497, evergreen topic",
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
        "content_types": ["Dating tips", "Red flags", "Psychology", "Success stories"],
        "affiliate_programs": ["Bumble", "Hinge", "eHarmony", "dating courses"],
        "avg_rpm_youtube": "$8–20",
        "example_accounts": ["@datingadvicepage", "@psychologyoflove"],
    },
    {
        "niche": "Entrepreneurship & Side Hustles",
        "monetization_potential": "$$$$",
        "why": "Course sales ($200–2000+), SaaS tools ($50–200/mo commissions), high-intent audience",
        "best_platforms": ["YouTube", "TikTok", "Instagram"],
        "content_types": ["Income reports", "Business ideas", "Tool reviews", "How-to guides"],
        "affiliate_programs": ["Shopify", "Clickfunnels", "Kajabi", "ConvertKit", "Canva Pro"],
        "avg_rpm_youtube": "$10–25",
        "example_accounts": ["@sidehustleinspiration", "@entrepreneurmindset"],
    },
    {
        "niche": "Mental Health & Mindset",
        "monetization_potential": "$$$",
        "why": "Growing rapidly post-2020, meditation/therapy app affiliate programs, digital products",
        "best_platforms": ["Instagram", "TikTok", "YouTube"],
        "content_types": ["Affirmations", "Psychology tips", "Journaling prompts", "Coping strategies"],
        "affiliate_programs": ["BetterHelp", "Calm", "Headspace", "Noom", "journals/planners"],
        "avg_rpm_youtube": "$5–15",
        "example_accounts": ["@mentalhealth", "@psychologyfacts"],
    },
    {
        "niche": "AI & Tech",
        "monetization_potential": "$$$$",
        "why": "Hottest sector 2024–2026, SaaS tools pay 20–40% recurring commissions",
        "best_platforms": ["YouTube", "TikTok", "Instagram"],
        "content_types": ["AI tool demos", "Productivity hacks", "News commentary", "Tutorials"],
        "affiliate_programs": ["Jasper", "Copy.ai", "Midjourney", "Notion", "ChatGPT Plus referrals"],
        "avg_rpm_youtube": "$15–40",
        "example_accounts": ["@aitools", "@futuretech"],
    },
    {
        "niche": "Pets (especially dogs/cats)",
        "monetization_potential": "$$",
        "why": "Extremely high engagement, pet owners spend $1200+/year on pets",
        "best_platforms": ["TikTok", "Instagram"],
        "content_types": ["Cute clips", "Training tips", "Product reviews", "Day-in-life"],
        "affiliate_programs": ["Chewy", "BarkBox", "Amazon pet", "pet insurance programs"],
        "avg_rpm_youtube": "$3–8",
        "example_accounts": ["@dogsofinstagram", "@catsofinstagram"],
    },
]


def get_niches(monetization_filter: str = "all") -> list[dict]:
    """Return ranked list of converting niches, optionally filtered by monetization tier."""
    if monetization_filter == "all":
        return CONVERTING_NICHES
    tier_map = {"high": "$$$$", "medium": "$$$", "low": "$$"}
    target = tier_map.get(monetization_filter, monetization_filter)
    return [n for n in CONVERTING_NICHES if n["monetization_potential"] == target]


def get_setup_guide(niche: str = "your niche") -> dict[str, Any]:
    """Full step-by-step setup guide for a converting theme page."""
    return {
        "overview": "A theme page is a faceless, topic-based account. You curate content, build an audience, then monetize through affiliate links, digital products, and brand deals.",
        "phase_1_setup": {
            "title": "Phase 1: Foundation (Week 1)",
            "steps": [
                f"1. Pick ONE niche with $ potential (e.g., '{niche}'). Niche down — 'fitness' is too broad, 'postpartum fitness for new moms' converts.",
                "2. Create accounts: Use a descriptive handle like @[NicheKeyword][Motivation/Tips/Daily]",
                "3. Write a converting bio: [Hook] | [Credibility] | [CTA with link-in-bio]",
                "4. Set up link-in-bio tool: Stan Store (best for monetization) or Linktree (free)",
                "5. Create a Canva template kit: matching colors, fonts, and style for your niche",
                "6. Set up Notion content calendar: plan 30 days of content before going live",
            ],
        },
        "phase_2_content": {
            "title": "Phase 2: Content Engine (Week 2–4)",
            "steps": [
                "1. FIND content: TikTok Discover tab, YouTube trending, Reddit hot posts, Pinterest trending",
                "2. REPOST ethically: Always credit original creator. Repurpose, don't just screenshot.",
                "3. ADD VALUE: Every post needs YOUR take — a caption tip, a data point, a question.",
                "4. CREATE original: At minimum 30% original content. Reposts build audience, originals build trust.",
                "5. Content ratio: 40% educational | 30% entertainment | 20% social proof | 10% promotional",
                "6. Batch create: Film/make 7 days of content in 2 hours on Sunday",
            ],
            "sourcing_tools": [
                "Pinterest Trends (trends.pinterest.com) — free, shows what's spiking",
                "Google Trends — validates topic interest over time",
                "TikTok Discover + Creative Center (this tool's tiktok trends command)",
                "YouTube Trending (this tool's youtube trends command)",
                "Exploding Topics (explodingtopics.com) — emerging trend discovery",
                "Reddit (subreddits in your niche) — raw community content",
            ],
        },
        "phase_3_growth": {
            "title": "Phase 3: Algorithmic Growth (Month 1–3)",
            "tiktok": [
                "Post 3x/day for first 30 days. The algorithm rewards consistency.",
                "Use trending audio within 48 hours of it trending",
                "Engage in your niche: comment on 20 posts/day from similar accounts",
                "Stitch/Duet bigger creators — you borrow their audience",
            ],
            "instagram": [
                "Carousels get 3x more reach than static posts — always use carousel format",
                "Post 1 Reel + 1 Carousel + 3 Stories per day",
                "Use all 30 hashtag slots. Mix sizes: mega, medium, small, branded",
                "Collab with accounts of similar size for combined audience reach",
            ],
            "youtube": [
                "Shorts feed is separate from main feed — post Shorts daily even as a small channel",
                "Title + thumbnail is 80% of your success — test 3 thumbnail styles",
                "End screen + cards direct traffic to your best content",
                "Reply to every comment in first 2 hours — signals engagement to algorithm",
            ],
        },
        "phase_4_convert": {
            "title": "Phase 4: The Conversion System",
            "funnel": [
                "AWARENESS: Viral/trending content (TikTok, Reels, Shorts) → drives to profile",
                "INTEREST: Bio + pinned post explains what you offer → follows/subscribes",
                "CONSIDERATION: Value content (carousels, tutorials) builds trust",
                "CONVERSION: Soft CTA in posts → link in bio → freebie email capture → email sequence → offer",
                "RETENTION: Email list + story polls + comments → repeat buyers",
            ],
            "cta_templates": [
                "'Save this post for later 📌' — highest save rate CTA",
                "'Comment [keyword] and I'll DM you the free guide' — drives DMs + comments",
                "'Follow for more [niche] tips daily' — follow CTA",
                "'Link in bio to get started' — traffic driver",
                "'Share this with someone who needs to hear this' — viral CTA",
            ],
            "link_in_bio_structure": [
                "Free lead magnet (builds email list) — ALWAYS first link",
                "Best-selling affiliate product",
                "Your digital product (if you have one)",
                "Latest content / YouTube channel",
                "Contact/collab inquiry",
            ],
        },
        "monetization": {
            "title": "Monetization Stack (stack these in order)",
            "tier_1_beginner": [
                "Amazon Associates (3–10% commission, easy approval, any niche)",
                "Platform-specific affiliate programs for tools in your niche",
                "Sponsored shoutouts from smaller brands",
            ],
            "tier_2_intermediate": [
                "ShareASale / CJ Affiliate / Impact (higher commission programs)",
                "Digital products: Templates, guides, presets — $7–97 price point",
                "Paid shoutouts to brands at 10K+ followers ($50–500/post)",
            ],
            "tier_3_advanced": [
                "High-ticket affiliate programs ($100–500/sale): SaaS, courses, finance tools",
                "Your own course or coaching: $200–2000 price point",
                "Brand deals and long-term partnerships: $500–10K+/month",
                "Managing multiple theme pages as a portfolio business",
            ],
            "income_projections": {
                "0_to_10k_followers": "$100–500/month (affiliate links, small shoutouts)",
                "10k_to_50k_followers": "$500–3000/month (brand deals, digital products)",
                "50k_to_200k_followers": "$3000–15000/month (premium sponsorships, course sales)",
                "200k_plus_followers": "$10000–100000/month+ (portfolio of pages, agency model)",
            },
        },
        "common_mistakes": [
            "Trying to be everywhere: Start with ONE platform and ONE niche. Scale later.",
            "Posting without a strategy: Every post needs a goal (awareness, engagement, or conversion).",
            "Ignoring the email list: Social platforms can ban you overnight. Email is forever.",
            "Not tracking metrics: Check insights weekly. Double down on what works. Kill what doesn't.",
            "Monetizing too early: Build 1K+ engaged followers before pushing offers.",
            "Copying without crediting: Gets accounts banned. Always give credit or transform content.",
            "Inconsistency: 3 posts/day for 1 week beats 21 posts in one day + silence for 2 weeks.",
            "Perfect over published: Post B+ content consistently. A+ content occasionally. Never 0 posts.",
        ],
        "tools_stack": {
            "content_creation": ["Canva Pro (templates, reels, carousels)", "CapCut (free TikTok/Reels editor)", "Descript (video editing with AI)"],
            "scheduling": ["Buffer (free tier)", "Later (Instagram-focused)", "TikTok Scheduler (native, free)"],
            "analytics": ["Social Blade (growth tracking)", "Metricool (cross-platform analytics)", "Instagram/TikTok native insights"],
            "monetization": ["Stan Store (all-in-one: link in bio + digital products)", "Gumroad (digital product sales)", "ConvertKit (email list)"],
            "trend_research": ["This CLI tool (social-trends)", "Pinterest Trends", "Google Trends", "TikTok Creative Center"],
        },
    }


def get_content_repurposing_guide() -> dict[str, Any]:
    """How to repurpose one piece of content into 10+ assets across platforms."""
    return {
        "core_concept": "Create Once, Distribute Everywhere (CODE). One long-form piece of content becomes 10+ short-form assets.",
        "workflow": [
            "1. Create ONE long-form piece: YouTube video (8–15 min) OR blog post OR podcast episode",
            "2. Extract 5–7 key points as individual TikToks/Reels (60s each)",
            "3. Turn key points into carousel slides (IG + LinkedIn)",
            "4. Pull quotes as static posts",
            "5. Thread the key points on X/Twitter",
            "6. Send top 3 points as an email newsletter",
            "7. Pin the best clip as YouTube Short",
        ],
        "platform_specs": {
            "tiktok": "9:16 vertical, 1080x1920, 15–60s sweet spot, auto-captions required",
            "instagram_reels": "9:16 vertical, 1080x1920, max 90s, no TikTok watermark",
            "youtube_shorts": "9:16 vertical, 1080x1920, max 60s, #Shorts in title",
            "instagram_carousel": "1:1 square 1080x1080, 10 slides max, heavy text allowed",
            "youtube_long": "16:9 landscape, 1920x1080, 8–15 min optimal watch time",
        },
        "watermark_removal": "Use SnapTik.app or SSSTik.io to download TikToks without watermark before cross-posting to Instagram Reels.",
    }
