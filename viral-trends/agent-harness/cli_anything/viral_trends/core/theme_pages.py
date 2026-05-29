"""Viral Trends CLI - Theme page strategy guides.

All guide content is defined as module-level dicts so tests can validate
content without invoking Click. The CLI calls guide_content(key) to retrieve.
"""

from typing import Dict, Any


GUIDES: Dict[str, Dict[str, Any]] = {
    "overview": {
        "title": "Viral Trends — Platform Overview",
        "sections": [
            {
                "heading": "What This Tool Does",
                "body": (
                    "viral-trends is an agent-native CLI for discovering trending content on YouTube "
                    "and TikTok, optimizing your posting strategy, and building a 7-day content calendar. "
                    "It works offline using curated mock trend data, or live with yt-dlp installed."
                ),
            },
            {
                "heading": "Quick Start",
                "body": "Create a workspace, fetch trends, optimize your profile, and generate a schedule.",
                "commands": [
                    "viral-trends workspace new --name my_page --niche gaming -o page.json",
                    "viral-trends --workspace page.json trends fetch --platform youtube",
                    "viral-trends --workspace page.json optimize profile --niche gaming",
                    "viral-trends --workspace page.json schedule generate --niche gaming --platforms tiktok",
                    "viral-trends --workspace page.json schedule calendar",
                ],
            },
            {
                "heading": "Available Niches",
                "body": "gaming, finance, fitness, cooking, tech, beauty, motivation, entertainment",
            },
            {
                "heading": "Platform Support",
                "body": "YouTube (trending videos via yt-dlp), TikTok (trending hashtags), Instagram (scheduling only)",
            },
        ],
        "quick_commands": [
            "viral-trends guide theme-page",
            "viral-trends guide hashtags",
            "viral-trends guide posting-times",
            "viral-trends guide converting",
        ],
    },

    "theme-page": {
        "title": "Theme Page Masterclass",
        "sections": [
            {
                "heading": "What Is a Theme Page",
                "body": (
                    "A theme page is an anonymous social media account built around a specific niche or topic "
                    "rather than a personal brand. The page curates, reposts, and creates content around one "
                    "clear theme — e.g. @DailyFinanceTips, @GamingHighlights, @FitnessMotivation. "
                    "Theme pages scale faster than personal brands because:\n"
                    "  • No on-camera requirement — you never show your face\n"
                    "  • Content is evergreen and reusable\n"
                    "  • Multiple niches can run simultaneously\n"
                    "  • Monetization is immediate via affiliate links and shoutouts"
                ),
            },
            {
                "heading": "Niche Selection (The Foundation)",
                "body": (
                    "The niche determines everything. Profitable criteria:\n\n"
                    "  HIGH VALUE niches (strong monetization):\n"
                    "  • Finance: CPMs $15-40, affiliate commissions 20-50%\n"
                    "  • Tech: CPMs $12-30, product affiliate rates 3-10%\n"
                    "  • Fitness: CPMs $8-20, supplement affiliate 15-30%\n\n"
                    "  HIGH VOLUME niches (fast follower growth):\n"
                    "  • Gaming: 6.3M TikTok posts, massive youth demographic\n"
                    "  • Entertainment: 21M TikTok posts, broadest reach\n"
                    "  • Beauty: 9.8M TikTok posts, strong purchase intent\n\n"
                    "  SWEET SPOT: Choose a niche with both. Motivation + finance is the #1 theme page niche."
                ),
                "tips": [
                    "Avoid 'general funny' — too broad, no monetization angle",
                    "Pick a niche you can produce 30+ content ideas for immediately",
                    "Test 3 niches with 10 posts each before committing",
                    "Micro-niches outperform macro in 2025: 'AI tools for students' > 'technology'",
                ],
            },
            {
                "heading": "Content Pillars",
                "body": (
                    "Every theme page needs 3-5 recurring content formats that define the page:\n\n"
                    "  Pillar 1 — Educational (40%): Tips, how-tos, explanations\n"
                    "  Pillar 2 — Entertaining (30%): Memes, compilations, reactions\n"
                    "  Pillar 3 — Motivational (20%): Quotes, transformations, success stories\n"
                    "  Pillar 4 — Promotional (10%): Product mentions, affiliate links, shoutouts\n\n"
                    "Never exceed 10% promotional content or your organic reach tanks."
                ),
            },
            {
                "heading": "Page Branding",
                "body": (
                    "Brand elements that signal authority at a glance:\n\n"
                    "  Username: @[Niche][Action] — e.g. @TradingTips, @GymFuel, @AIDaily\n"
                    "  Bio: 3 lines: what you do | who it's for | CTA with link\n"
                    "  Profile photo: Logo or niche-related image (no face needed)\n"
                    "  Color palette: Pick 2 colors and use them in every post thumbnail\n"
                    "  Font: One bold font for all text overlays — consistency = recognition"
                ),
                "tips": [
                    "Use Canva for free branded templates",
                    "Add a Linktree or Beacons link aggregator in bio immediately",
                    "Watermark every piece of content with your handle @username",
                ],
            },
            {
                "heading": "Content Creation Workflow",
                "body": (
                    "The batch-and-schedule method (saves 80% of time):\n\n"
                    "  Step 1: Trend research (30 min/week)\n"
                    "    → Run: viral-trends trends fetch --platform tiktok\n"
                    "    → Identify 7 trending topics in your niche\n\n"
                    "  Step 2: Content batch (2-3 hours once/week)\n"
                    "    → Create all 7-14 posts in one session\n"
                    "    → Repurpose one idea across 3 formats: video + image + text\n\n"
                    "  Step 3: Schedule (15 min)\n"
                    "    → Run: viral-trends schedule generate --niche [niche] --platforms tiktok,youtube\n"
                    "    → Upload to scheduling tool (Buffer, Later, or native schedulers)\n\n"
                    "  Step 4: Engage (20 min/day)\n"
                    "    → Reply to every comment in the first hour after posting\n"
                    "    → Like/comment on 10 posts from top creators in your niche"
                ),
            },
            {
                "heading": "Growth Hacking Tactics",
                "body": (
                    "Proven tactics for 0→10K followers:\n\n"
                    "  1. Trend Hijacking: Post on trending audio/hashtags within 2 hours of them breaking\n"
                    "  2. Duet/Stitch (TikTok): Stitch viral videos with your commentary\n"
                    "  3. Comment Farming: Leave hot takes on viral posts in your niche\n"
                    "  4. Series Content: 'Day 1 of X', multi-part series keeps people coming back\n"
                    "  5. Cross-Platform Repurposing: TikTok → YouTube Shorts → Instagram Reels (same video)\n"
                    "  6. Posting Frequency: 2x/day TikTok, 1x/day YouTube Shorts for maximum algorithmic push\n"
                    "  7. Hook optimization: First 0-2 seconds determine 90% of watch time — test constantly"
                ),
            },
        ],
        "quick_commands": [
            "viral-trends trends fetch --platform tiktok --niche gaming",
            "viral-trends optimize profile --niche gaming --platform tiktok",
            "viral-trends schedule generate --niche gaming --platforms tiktok,youtube",
            "viral-trends guide converting",
        ],
    },

    "converting": {
        "title": "Converting Followers to Buyers",
        "sections": [
            {
                "heading": "The Conversion Funnel",
                "body": (
                    "Follower → Engaged fan → Email subscriber → Buyer\n\n"
                    "Most theme pages stop at 'follower' and leave all the money on the table. "
                    "The conversion funnel moves people deeper:\n\n"
                    "  TOFU (Top of Funnel): Free viral content → Followers\n"
                    "  MOFU (Middle of Funnel): Lead magnets → Email list\n"
                    "  BOFU (Bottom of Funnel): Offers, products, affiliate links → Revenue"
                ),
            },
            {
                "heading": "Revenue Streams by Follower Count",
                "body": (
                    "1K-5K followers:\n"
                    "  • Affiliate marketing: Add affiliate links to bio (Amazon, ClickBank, ShareASale)\n"
                    "  • Expected: $50-300/month\n\n"
                    "5K-50K followers:\n"
                    "  • Shoutouts: Charge $50-500 per sponsored post\n"
                    "  • Digital products: eBooks, templates, presets ($7-47)\n"
                    "  • Expected: $500-3,000/month\n\n"
                    "50K-500K followers:\n"
                    "  • Brand deals: $500-5,000 per post\n"
                    "  • Courses/memberships: $97-497 products\n"
                    "  • YouTube AdSense: $2-15 CPM\n"
                    "  • Expected: $3,000-15,000/month\n\n"
                    "500K+ followers:\n"
                    "  • Full brand partnership deals: $5,000-50,000\n"
                    "  • Own product line, SaaS, coaching\n"
                    "  • Expected: $15,000-100,000+/month"
                ),
            },
            {
                "heading": "Affiliate Marketing Setup",
                "body": (
                    "The fastest monetization path for new pages:\n\n"
                    "  Step 1: Join affiliate programs relevant to your niche\n"
                    "    Finance: Robinhood, Coinbase, Personal Capital\n"
                    "    Fitness: MyProtein, GNC, Amazon fitness gear\n"
                    "    Tech: Amazon Associates, Best Buy affiliate, Adobe\n"
                    "    Beauty: Sephora, Ulta, Makeup.com\n\n"
                    "  Step 2: Create a Linktree/Beacons page with your links\n"
                    "  Step 3: Add 'Link in bio' CTA to 30% of posts\n"
                    "  Step 4: Create 'review' or 'best of' content that naturally links to products\n"
                    "  Step 5: Track clicks weekly and double down on what converts"
                ),
            },
            {
                "heading": "Email List Building",
                "body": (
                    "Your email list is the only asset you truly own. Social platforms can ban you overnight.\n\n"
                    "  Lead Magnet Ideas by Niche:\n"
                    "  Finance: 'My Top 10 Stock Picks This Month' PDF\n"
                    "  Fitness: '30-Day Workout Plan' PDF\n"
                    "  Gaming: 'Pro Settings for [Game]' guide\n"
                    "  Beauty: 'Morning Skincare Routine Checklist'\n"
                    "  Tech: 'Top 20 AI Tools That Save Hours Daily'\n\n"
                    "  Tools: ConvertKit (free to 1K subs), Mailchimp, Beehiiv\n"
                    "  Goal: Convert 1-3% of followers to email list\n"
                    "  Value: Email subscribers are worth 10x social followers for revenue"
                ),
            },
            {
                "heading": "Shoutout Business Model",
                "body": (
                    "Selling shoutouts is the fastest cash flow for 5K+ accounts:\n\n"
                    "  Pricing Formula: (followers / 1000) × $1-5 per post\n"
                    "  Example: 50K followers = $50-250 per shoutout\n\n"
                    "  Where to find buyers:\n"
                    "  • ShoutoutGigs.com\n"
                    "  • Shoutcart.com\n"
                    "  • Collabstr.com\n"
                    "  • Direct DM outreach to brands in your niche\n\n"
                    "  Rules:\n"
                    "  • Never do more than 1 shoutout per 10 organic posts\n"
                    "  • Only promote products you'd actually use\n"
                    "  • Disclose sponsorships (#ad) — it actually increases trust"
                ),
            },
            {
                "heading": "Digital Product Creation",
                "body": (
                    "The highest-margin revenue stream. Create once, sell forever.\n\n"
                    "  Quick Digital Products (1-3 days to create):\n"
                    "  • PDF guide/ebook: $7-27 — Canva, Google Docs\n"
                    "  • Notion template: $17-47 — duplicate your own workflow\n"
                    "  • Preset pack: $17-37 — Lightroom/VSCO presets for your niche\n"
                    "  • Prompt pack: $17-47 — AI prompt collections\n\n"
                    "  Where to sell:\n"
                    "  • Gumroad (free to start, 10% fee)\n"
                    "  • Lemon Squeezy (3.5% fee)\n"
                    "  • Etsy (for templates/printables)\n\n"
                    "  Sales funnel:\n"
                    "  Post viral content → Bio link → Free lead magnet → Email sequence → Product offer"
                ),
            },
            {
                "heading": "Automation Workflow",
                "body": (
                    "Scaling to 10+ accounts with minimal daily time:\n\n"
                    "  Scheduling: Buffer, Later, or TikTok/YouTube native scheduler\n"
                    "  Repurposing: Record once → Kapwing or Opus Clip for multi-platform cuts\n"
                    "  Caption generation: Use AI (Claude, ChatGPT) with the hooks from 'viral-trends optimize hooks'\n"
                    "  Hashtag research: 'viral-trends optimize hashtags --niche [niche]' weekly\n"
                    "  Trend monitoring: 'viral-trends trends fetch --platform both' daily\n\n"
                    "  Time budget for running 3 theme pages:\n"
                    "  • 2 hours/week content creation (batch)\n"
                    "  • 20 min/day engagement\n"
                    "  • 30 min/week trend research and scheduling\n"
                    "  Total: ~4 hours/week for 3 monetized accounts"
                ),
            },
        ],
        "quick_commands": [
            "viral-trends optimize profile --niche finance --platform tiktok",
            "viral-trends optimize hashtags --niche finance --platform tiktok",
            "viral-trends schedule generate --niche finance --platforms tiktok,youtube",
            "viral-trends guide theme-page",
        ],
    },

    "hashtags": {
        "title": "Hashtag Strategy Guide",
        "sections": [
            {
                "heading": "The Hashtag Pyramid Strategy",
                "body": (
                    "Use a mix of hashtag sizes for maximum algorithmic reach:\n\n"
                    "  Mega (100M+ posts): #fyp, #viral, #trending — broad discovery\n"
                    "  Large (10M-100M posts): #gaming, #fitness — niche discovery\n"
                    "  Medium (1M-10M posts): #gamingcommunity, #fitfam — targeted\n"
                    "  Small (100K-1M posts): #soloranked, #gymtok2025 — niche community\n\n"
                    "  Recommended mix per post:\n"
                    "  TikTok: 2 mega + 3 large + 3 medium + 2 small = 10 total\n"
                    "  YouTube: 3-5 large/medium hashtags (less is more)\n"
                    "  Instagram: 5 large + 5 medium + 5 small = 15 total"
                ),
            },
            {
                "heading": "Platform-Specific Rules",
                "body": (
                    "TikTok:\n"
                    "  • Add hashtags IN the caption, not as a comment\n"
                    "  • 3-7 hashtags optimal (more can look spammy)\n"
                    "  • Always include #fyp or #foryou as one of them\n"
                    "  • Trending hashtags visible in TikTok Discover tab\n\n"
                    "YouTube:\n"
                    "  • First 3 hashtags in description appear above video title\n"
                    "  • Keep to 3-5 relevant hashtags\n"
                    "  • Don't use irrelevant hashtags — YouTube will suppress the video\n\n"
                    "Instagram:\n"
                    "  • Add hashtags at end of caption or in first comment\n"
                    "  • 10-15 is the current sweet spot\n"
                    "  • Rotate sets to avoid 'shadowban'"
                ),
            },
            {
                "heading": "Finding Trending Hashtags",
                "body": (
                    "Real-time discovery methods:\n\n"
                    "  1. viral-trends trends fetch --platform tiktok --live (requires network)\n"
                    "  2. TikTok Discover tab → filter by 'This week'\n"
                    "  3. YouTube Trending tab → note the video topics, not just tags\n"
                    "  4. RiteTag.com — real-time hashtag analytics\n"
                    "  5. Flick.tech — hashtag research tool with engagement rates"
                ),
            },
        ],
        "quick_commands": [
            "viral-trends optimize hashtags --niche gaming",
            "viral-trends optimize hashtags --niche finance --platform youtube",
            "viral-trends trends fetch --platform tiktok",
        ],
    },

    "posting-times": {
        "title": "Optimal Posting Times Guide",
        "sections": [
            {
                "heading": "Why Timing Matters",
                "body": (
                    "Algorithms reward early engagement. The first 30 minutes after posting are critical — "
                    "the platform decides whether to push your content to a wider audience based on initial "
                    "likes, comments, shares, and watch time. Posting when your audience is active means "
                    "more eyes in that critical window."
                ),
            },
            {
                "heading": "Best Times by Platform (EST)",
                "body": (
                    "TikTok (highest engagement windows):\n"
                    "  Friday 8pm-11pm — score 95/100\n"
                    "  Sunday 8am-11am — score 91/100\n"
                    "  Saturday 7pm-11pm — score 94/100\n"
                    "  Wednesday 7pm-10pm — score 90/100\n\n"
                    "YouTube (best upload times):\n"
                    "  Saturday 9am-1pm — score 91/100\n"
                    "  Friday 12pm-4pm — score 90/100\n"
                    "  Sunday 9am-1pm — score 89/100\n\n"
                    "Instagram:\n"
                    "  Friday 8am-11am / 4pm-8pm — score 92/100\n"
                    "  Saturday 8am-12pm — score 90/100\n"
                    "  Wednesday 8am-11am — score 89/100"
                ),
            },
            {
                "heading": "Niche-Specific Adjustments",
                "body": (
                    "Finance/Business: Add 2 hours — audience is morning commuters (6-9am)\n"
                    "Fitness: Subtract 2 hours — audience posts early morning workouts (5-8am)\n"
                    "Gaming: Post evening/late night — audience is 14-24, school/work schedules\n"
                    "Cooking: Align with meal times — 5-7pm for dinner content\n"
                    "Beauty: Evening/weekend — discovery browsing time"
                ),
            },
            {
                "heading": "Using viral-trends for Timing",
                "body": "Get platform-specific posting windows automatically.",
                "commands": [
                    "viral-trends optimize times --platform tiktok",
                    "viral-trends optimize times --platform youtube --day friday",
                    "viral-trends optimize times --platform instagram",
                ],
            },
        ],
        "quick_commands": [
            "viral-trends optimize times --platform tiktok",
            "viral-trends optimize times --platform youtube",
            "viral-trends schedule generate --niche gaming --platforms tiktok,youtube",
        ],
    },

    "hooks": {
        "title": "Caption Hooks — Stop the Scroll",
        "sections": [
            {
                "heading": "The 2-Second Rule",
                "body": (
                    "Viewers decide in the first 1-2 seconds whether to keep watching. Your opening "
                    "line (hook) must:\n"
                    "  1. Interrupt the scroll mentally\n"
                    "  2. Promise a clear payoff ('you'll learn X', 'see what happened when Y')\n"
                    "  3. Create an open loop the viewer must close (curiosity gap)\n\n"
                    "For video: The visual hook (first frame) AND verbal hook (first words) must both work."
                ),
            },
            {
                "heading": "The 5 Hook Frameworks",
                "body": (
                    "1. CURIOSITY: 'Nobody talks about this, but...' — creates an information gap\n"
                    "2. URGENCY: 'Do this NOW before it's too late' — creates FOMO\n"
                    "3. AUTHORITY: 'After testing 50 strategies...' — builds credibility\n"
                    "4. RELATABILITY: 'POV: You finally understood X' — emotional connection\n"
                    "5. CONTROVERSY: 'Hot take: everyone is wrong about X' — provokes engagement\n\n"
                    "Rotate these frameworks. Audiences become immune to the same hook style."
                ),
            },
            {
                "heading": "Hook Templates by Niche",
                "body": (
                    "Finance: 'This one investing mistake costs most people $50K+'\n"
                    "Gaming: 'POV: You just discovered the most broken strat in [game]'\n"
                    "Fitness: 'Stop doing [common exercise] — here's why'\n"
                    "Beauty: 'I tried every viral skincare routine so you don't have to'\n"
                    "Tech: 'This AI tool is replacing [job/task] — here's the proof'\n"
                    "Motivation: 'The mindset shift that took me from broke to [result]'"
                ),
            },
        ],
        "quick_commands": [
            "viral-trends optimize hooks --type curiosity --niche gaming",
            "viral-trends optimize hooks --type authority --niche finance",
            "viral-trends optimize hooks --type controversy --niche tech",
        ],
    },

    "youtube": {
        "title": "YouTube Trending — Platform Guide",
        "sections": [
            {
                "heading": "How YouTube Trending Works",
                "body": (
                    "YouTube's trending tab surfaces videos based on:\n"
                    "  • View velocity (views per hour, not total views)\n"
                    "  • Engagement rate (likes, comments, shares per view)\n"
                    "  • Watch time percentage (how much of the video people watch)\n"
                    "  • Click-through rate from thumbnails\n\n"
                    "For theme pages: study WHAT trending videos have in common (format, length, hook) "
                    "more than the specific content. Then replicate the format for your niche."
                ),
            },
            {
                "heading": "Content Formats That Trend",
                "body": (
                    "YouTube Shorts (under 60s):\n"
                    "  • Fastest growth path in 2025\n"
                    "  • Algorithm treats them like TikTok\n"
                    "  • Best: quick tips, transformations, reactions\n\n"
                    "Long-form (8-15 min):\n"
                    "  • Best: tutorials, reviews, 'I tried X for 30 days'\n"
                    "  • Thumbnail + title = 70% of click decision\n\n"
                    "Faceless video formats (for theme pages):\n"
                    "  • Screen recordings + voiceover\n"
                    "  • Stock footage + AI voiceover\n"
                    "  • Listicle/slideshow style\n"
                    "  • Animated explainer"
                ),
            },
            {
                "heading": "YouTube SEO Basics",
                "body": (
                    "Title: Include main keyword in first 5 words\n"
                    "Description: First 2 lines are indexed — put keyword-rich summary there\n"
                    "Tags: 5-10 specific tags + 3-5 broad category tags\n"
                    "Thumbnail: High contrast, 1-3 words of text, face with expression (if any)\n"
                    "Chapters: Add timestamps for videos over 5 min — improves retention signal"
                ),
            },
        ],
        "quick_commands": [
            "viral-trends trends fetch --platform youtube",
            "viral-trends trends fetch --platform youtube --live",
            "viral-trends optimize hashtags --niche gaming --platform youtube",
        ],
    },

    "tiktok": {
        "title": "TikTok Viral Content — Platform Guide",
        "sections": [
            {
                "heading": "How the TikTok Algorithm Works",
                "body": (
                    "TikTok's algorithm is the most egalitarian of all platforms:\n"
                    "  • Every video gets shown to a test batch of ~300-500 users\n"
                    "  • If engagement % (likes, comments, shares, rewatches) exceeds threshold → wider batch\n"
                    "  • Follower count matters far less than on YouTube/Instagram\n"
                    "  • A brand new account CAN go viral with the first video\n\n"
                    "Key metrics TikTok watches:\n"
                    "  1. Completion rate (most important — do people watch till the end?)\n"
                    "  2. Rewatch rate\n"
                    "  3. Share rate\n"
                    "  4. Comment rate"
                ),
            },
            {
                "heading": "Viral Video Blueprint",
                "body": (
                    "The STAR formula for TikTok:\n\n"
                    "  S — STOP the scroll (0-2s): Visual hook + text overlay\n"
                    "  T — TEASE the payoff (2-5s): 'By the end of this you'll know...'\n"
                    "  A — ADD value (5-50s): The actual content — tip, story, demo\n"
                    "  R — REQUEST action (last 5s): 'Follow for more [niche] tips'\n\n"
                    "Length sweet spot: 21-34 seconds has highest average completion rate.\n"
                    "Add subtitles/captions: 92% of TikTok users watch with sound off sometimes."
                ),
            },
            {
                "heading": "Trending Audio Strategy",
                "body": (
                    "Using trending audio is the #1 free growth hack on TikTok:\n\n"
                    "  How to find trending sounds:\n"
                    "  1. TikTok → + → flip to 'sounds' → 'trending'\n"
                    "  2. Look for the 'trending' arrow on sounds in your For You page\n"
                    "  3. Check what sounds top creators in your niche are using\n\n"
                    "  Rules:\n"
                    "  • Use trending sound within 24-48h of it trending for max boost\n"
                    "  • Sound must fit the video — forced audio tanks retention\n"
                    "  • Instrumental/background tracks work for any content type"
                ),
            },
        ],
        "quick_commands": [
            "viral-trends trends fetch --platform tiktok",
            "viral-trends trends fetch --platform tiktok --niche gaming",
            "viral-trends optimize profile --niche gaming --platform tiktok",
        ],
    },

    "schedule": {
        "title": "Content Scheduling Guide",
        "sections": [
            {
                "heading": "Why Consistent Scheduling Wins",
                "body": (
                    "Algorithms on TikTok, YouTube, and Instagram reward consistency:\n"
                    "  • Posting at the same times trains the algorithm and your audience\n"
                    "  • Consistency signals you're a serious creator → more distribution\n"
                    "  • Minimum viable posting frequency: 1x/day TikTok, 3x/week YouTube\n"
                    "  • Optimal: 2x/day TikTok, 1x/day YouTube Shorts, 1x/day Instagram"
                ),
            },
            {
                "heading": "The Batch-and-Schedule System",
                "body": (
                    "Create all content in one session, post over 7 days:\n\n"
                    "  Sunday (2-3 hours):\n"
                    "  1. Run trend research: viral-trends trends fetch --platform both\n"
                    "  2. Pick 7-14 content ideas from trends\n"
                    "  3. Film/create all content in one session\n"
                    "  4. Edit and export\n"
                    "  5. Schedule: viral-trends schedule generate --niche [niche]\n"
                    "  6. Upload to platform schedulers\n\n"
                    "  Daily (20 min):\n"
                    "  • Reply to all comments\n"
                    "  • Engage with 10 posts in your niche\n"
                    "  • Check what's performing → note for next week"
                ),
            },
        ],
        "quick_commands": [
            "viral-trends schedule generate --niche gaming --platforms tiktok,youtube --posts-per-day 2",
            "viral-trends schedule calendar",
            "viral-trends schedule list --platform tiktok",
        ],
    },
}


def guide_content(key: str) -> Dict[str, Any]:
    """Get guide content by key.

    Args:
        key: Guide key (overview, theme-page, converting, hashtags, etc.)

    Returns:
        Guide content dict with title and sections.

    Raises:
        ValueError: If key is not found.
    """
    if key not in GUIDES:
        available = list(GUIDES.keys())
        raise ValueError(f"Unknown guide '{key}'. Available: {available}")
    return GUIDES[key]


def list_guides() -> list:
    """List all available guide keys with titles."""
    return [{"key": k, "title": v["title"]} for k, v in GUIDES.items()]
