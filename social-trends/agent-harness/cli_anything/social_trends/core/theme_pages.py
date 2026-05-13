"""Theme page strategy — creating, growing, and monetizing niche content aggregator accounts."""
from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class ThemePageNiche:
    name: str
    difficulty: str  # "Beginner", "Intermediate", "Advanced"
    competition: str  # "Low", "Medium", "High"
    monetization_potential: str  # "$", "$$", "$$$"
    time_to_first_1k_followers: str
    avg_monthly_revenue_at_10k: str
    content_sources: list[str]
    monetization_methods: list[str]
    key_platforms: list[str]
    example_accounts: list[str]
    pro_tips: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ConversionStrategy:
    stage: str
    goal: str
    tactics: list[str]
    kpis: list[str]
    tools: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


_NICHES: list[dict] = [
    {
        "name": "Luxury & Cars",
        "difficulty": "Beginner",
        "competition": "Medium",
        "monetization_potential": "$$$",
        "time_to_first_1k_followers": "2-4 weeks",
        "avg_monthly_revenue_at_10k": "$800-$3,000",
        "content_sources": [
            "Reddit (r/carporn, r/Autos)",
            "Pinterest luxury boards",
            "YouTube supercar channels",
            "Instagram @supercarsoflondon style accounts",
            "Getty Images for editorial use",
        ],
        "monetization_methods": [
            "Car insurance affiliate programs (high CPC)",
            "Luxury goods affiliate (watches, clothing)",
            "Sponsored posts from luxury brands",
            "Amazon affiliate (car accessories)",
            "Print-on-demand merch",
        ],
        "key_platforms": ["Instagram", "TikTok", "Pinterest"],
        "example_accounts": ["@supercarblondie", "@carinstagram", "@luxurylifestyle"],
        "pro_tips": [
            "Use high-quality 4K content — quality IS the brand for luxury",
            "Post at 7PM EST for maximum engagement from US aspirational audience",
            "Caption formula: aspirational statement + question + CTA",
            "Compile content from YouTube (with credit) + original commentary",
            "Insurance affiliate can pay $40-200 per lead — top earner in this niche",
        ],
    },
    {
        "name": "Fitness Motivation",
        "difficulty": "Beginner",
        "competition": "High",
        "monetization_potential": "$$",
        "time_to_first_1k_followers": "3-6 weeks",
        "avg_monthly_revenue_at_10k": "$500-$2,000",
        "content_sources": [
            "Reddit (r/fitness, r/bodybuilding)",
            "YouTube fitness channels (repost with credit)",
            "Free stock fitness photos (Pexels, Unsplash)",
            "Twitter fitness community content",
            "User-submitted transformation photos",
        ],
        "monetization_methods": [
            "Supplement affiliate programs (20-40% commission)",
            "Fitness program affiliate (ClickBank, ShareASale)",
            "Workout app partnerships",
            "Shoutout packages ($50-500)",
            "E-book/PDF workout plans ($9-29)",
        ],
        "key_platforms": ["Instagram", "TikTok", "YouTube Shorts"],
        "example_accounts": ["@gymfailsonly", "@fitnessmotivation.co", "@workoutholic"],
        "pro_tips": [
            "Before/after content gets 5-10x more saves than standard posts",
            "Transformation Tuesday and Flex Friday are reliable engagement boosters",
            "Build an email list early — supplements pay well via email funnels",
            "Repost with permission or use royalty-free content to avoid strikes",
        ],
    },
    {
        "name": "Finance & Wealth",
        "difficulty": "Intermediate",
        "competition": "Medium",
        "monetization_potential": "$$$",
        "time_to_first_1k_followers": "4-8 weeks",
        "avg_monthly_revenue_at_10k": "$1,500-$6,000",
        "content_sources": [
            "Bloomberg, CNBC, Forbes articles (summarize + credit)",
            "Reddit (r/personalfinance, r/investing)",
            "YouTube finance channels",
            "Twitter/X financial commentary",
            "Your own finance tips and analysis",
        ],
        "monetization_methods": [
            "Trading platform referrals ($50-200 per signup)",
            "Credit card affiliate programs ($100-300 CPA)",
            "Personal finance app affiliates",
            "Sponsored newsletter content",
            "Paid Discord or community ($29-99/month)",
        ],
        "key_platforms": ["Instagram", "TikTok", "YouTube", "Twitter/X"],
        "example_accounts": ["@marketmakers", "@wealthgang", "@richhabits"],
        "pro_tips": [
            "Finance affiliate pays the highest CPA of any niche — prioritize it",
            "Educational content that simplifies complex concepts goes viral",
            "Screenshot tweets from finance influencers and add commentary",
            "Credit card referrals can be $200+ per conversion",
            "Start a newsletter early — finance email lists convert 3x better",
        ],
    },
    {
        "name": "Aesthetic / Visual Art",
        "difficulty": "Beginner",
        "competition": "Medium",
        "monetization_potential": "$$",
        "time_to_first_1k_followers": "2-3 weeks",
        "avg_monthly_revenue_at_10k": "$400-$1,500",
        "content_sources": [
            "Pinterest aesthetic boards",
            "Unsplash / Pexels (royalty-free)",
            "DeviantArt (with permission)",
            "Midjourney AI-generated art (original)",
            "Architecture and travel photography",
        ],
        "monetization_methods": [
            "Print-on-demand (Society6, Redbubble, Printful)",
            "Presets / Lightroom pack sales ($15-49)",
            "Digital wallpaper packs",
            "Shopify store with aesthetic products",
            "Brand partnerships with aesthetic brands",
        ],
        "key_platforms": ["Instagram", "Pinterest", "TikTok"],
        "example_accounts": ["@aestheticpages", "@minimalmovement", "@aesthbr"],
        "pro_tips": [
            "Consistency in color palette builds strong brand recognition fast",
            "Midjourney AI content can be posted as original — massive time saver",
            "Pinterest drives passive traffic for years — create boards, not just posts",
            "Presets sell well because your followers want to recreate YOUR aesthetic",
        ],
    },
    {
        "name": "Pets & Animals",
        "difficulty": "Beginner",
        "competition": "High",
        "monetization_potential": "$$",
        "time_to_first_1k_followers": "2-4 weeks",
        "avg_monthly_revenue_at_10k": "$400-$1,200",
        "content_sources": [
            "Reddit (r/aww, r/dogs, r/cats)",
            "YouTube pet compilation channels",
            "User-submitted pet photos (DM campaigns)",
            "TikTok pet viral videos (repost with credit)",
        ],
        "monetization_methods": [
            "Pet product affiliate programs (Chewy, PetSmart — up to 10%)",
            "Pet insurance affiliate ($40-80 per lead)",
            "Shoutout packages for pet businesses",
            "Sponsored posts from pet food brands",
            "Custom pet portrait commissions referrals",
        ],
        "key_platforms": ["Instagram", "TikTok", "YouTube Shorts"],
        "example_accounts": ["@cutepetclub", "@we_rate_dogs", "@dogsbeingbasic"],
        "pro_tips": [
            "Run DM campaigns asking followers to submit pet photos — free UGC",
            "Dog content outperforms cat content by ~30% in engagement",
            "Funny captions on pet content go viral faster than heartwarming",
            "Post 2-3x daily early on — pet accounts grow fast with volume",
        ],
    },
    {
        "name": "Travel & Wanderlust",
        "difficulty": "Intermediate",
        "competition": "High",
        "monetization_potential": "$$$",
        "time_to_first_1k_followers": "4-8 weeks",
        "avg_monthly_revenue_at_10k": "$1,000-$5,000",
        "content_sources": [
            "YouTube travel vlogs (compilations with credit)",
            "Unsplash / Pexels travel photography",
            "Reddit travel communities",
            "Your own travel content (if applicable)",
            "Tourism board free media packs",
        ],
        "monetization_methods": [
            "Travel booking affiliate (Booking.com 25-40% commission)",
            "Airbnb referral program",
            "Travel credit card affiliate ($200-400 CPA)",
            "Luggage and travel gear affiliate",
            "VPN affiliate (popular with travel audience)",
        ],
        "key_platforms": ["Instagram", "YouTube", "Pinterest", "TikTok"],
        "example_accounts": ["@beautifuldestinations", "@earthpix", "@natgeotravel"],
        "pro_tips": [
            "Travel credit card affiliate is the highest-paying offer in this niche",
            "Carousel posts of destinations get 3x more saves than single images",
            "Film vertical content specifically — most travel browsing is on mobile",
            "Tourism boards often provide FREE media kits — contact them directly",
        ],
    },
    {
        "name": "Quotes & Mindset",
        "difficulty": "Beginner",
        "competition": "Very High",
        "monetization_potential": "$",
        "time_to_first_1k_followers": "1-2 weeks",
        "avg_monthly_revenue_at_10k": "$200-$800",
        "content_sources": [
            "BrainyQuote / Goodreads",
            "Reddit (r/quotes, r/stoicism)",
            "Your own original quotes",
            "Books (paraphrase + credit)",
            "Twitter thought leaders",
        ],
        "monetization_methods": [
            "Print-on-demand (quote posters)",
            "Journal / planner affiliate",
            "Book affiliate (Amazon)",
            "Coaching program promotion",
            "Paid shoutouts from coaches",
        ],
        "key_platforms": ["Instagram", "Pinterest", "Twitter/X"],
        "example_accounts": ["@positiveenergy", "@thegoodquote", "@mindset.therapy"],
        "pro_tips": [
            "Design matters — use Canva templates to look premium, not generic",
            "Controversial quotes outperform agreeable ones (sparks comments)",
            "Pair quotes with relevant aesthetic backgrounds for more saves",
            "Pinterest is gold for quote pages — content lives there for years",
        ],
    },
    {
        "name": "Tech & Gadgets",
        "difficulty": "Intermediate",
        "competition": "Medium",
        "monetization_potential": "$$$",
        "time_to_first_1k_followers": "4-6 weeks",
        "avg_monthly_revenue_at_10k": "$1,200-$4,000",
        "content_sources": [
            "YouTube tech channels (clips with credit)",
            "Reddit (r/technology, r/gadgets, r/battlestations)",
            "Twitter tech announcements",
            "Product launch press coverage",
            "Manufacturer press kits",
        ],
        "monetization_methods": [
            "Amazon affiliate (3-8% on tech products)",
            "Best Buy / Newegg affiliate",
            "VPN affiliate programs ($40-100 CPA)",
            "Software affiliate programs",
            "Sponsored posts from tech brands",
        ],
        "key_platforms": ["Instagram", "TikTok", "YouTube", "Twitter/X"],
        "example_accounts": ["@technews", "@gadgetflow", "@battlestations"],
        "pro_tips": [
            "Unboxing and review compilations get huge engagement",
            "Focus on Apple product content — highest engagement of any tech brand",
            "VPN affiliates pay extremely well and convert to tech audiences",
            "Launch-day content (new iPhone, PS6, etc.) can go massively viral",
        ],
    },
]


def list_niches(
    sort_by: str = "monetization",
    difficulty: str = "all",
    platform: str = "all",
) -> list[ThemePageNiche]:
    """List all theme page niches with optional filtering and sorting."""
    niches = [ThemePageNiche(**n) for n in _NICHES]

    if difficulty != "all":
        niches = [n for n in niches if n.difficulty.lower() == difficulty.lower()]
    if platform != "all":
        niches = [n for n in niches if any(platform.lower() in p.lower() for p in n.key_platforms)]

    money_map = {"$": 1, "$$": 2, "$$$": 3}
    diff_map = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
    comp_map = {"Low": 1, "Medium": 2, "High": 3, "Very High": 4}

    if sort_by == "monetization":
        niches.sort(key=lambda n: money_map.get(n.monetization_potential, 0), reverse=True)
    elif sort_by == "difficulty":
        niches.sort(key=lambda n: diff_map.get(n.difficulty, 0))
    elif sort_by == "competition":
        niches.sort(key=lambda n: comp_map.get(n.competition, 0))
    elif sort_by == "speed":
        # Sort by time_to_1k (extract week number)
        def extract_weeks(n: ThemePageNiche) -> int:
            parts = n.time_to_first_1k_followers.split("-")
            try:
                return int(parts[0].strip().split()[0])
            except (ValueError, IndexError):
                return 99
        niches.sort(key=extract_weeks)

    return niches


def get_niche_guide(niche_name: str) -> dict:
    """Get a full guide for a specific theme page niche."""
    niche_lower = niche_name.lower()
    match = next(
        (n for n in _NICHES if niche_lower in n["name"].lower()),
        None,
    )
    if not match:
        return {"error": f"Niche '{niche_name}' not found. Run 'social-trends theme-page niches' to list all."}
    return ThemePageNiche(**match).to_dict()


def conversion_funnel(niche: str = "general") -> list[ConversionStrategy]:
    """
    Return the full conversion funnel strategy for a theme page.
    Converts followers → email subscribers → customers.
    """
    return [
        ConversionStrategy(
            stage="1. Attract (Top of Funnel)",
            goal="Get discovered and followed by your target audience",
            tactics=[
                "Post 3-5x daily using trending hashtags and viral audio",
                "Engage with comments within the first 30 minutes of posting",
                "Duet/stitch viral content in your niche with your take",
                "Run 'follow for more' CTAs in every caption",
                "Use the trending sound format: hook (3s) → value → CTA",
            ],
            kpis=["Follower growth rate", "Profile visit rate", "Reach per post"],
            tools=["TikTok Analytics", "Instagram Insights", "Social Blade"],
        ),
        ConversionStrategy(
            stage="2. Engage (Middle of Funnel)",
            goal="Turn followers into loyal community members",
            tactics=[
                "Reply to EVERY comment in the first hour after posting",
                "Pin a comment on each post to guide the conversation",
                "Post polls and questions in Stories to boost engagement",
                "Go live weekly to build parasocial connection with audience",
                "Share behind-the-scenes content to humanize the page",
            ],
            kpis=["Comment rate", "Save rate", "Story view rate", "Live viewers"],
            tools=["Instagram Stories", "TikTok Q&A", "YouTube Community Posts"],
        ),
        ConversionStrategy(
            stage="3. Capture (Email/Community)",
            goal="Move audience off-platform to owned channels",
            tactics=[
                "Offer a free lead magnet (PDF, checklist, guide) via link in bio",
                "Tease 'exclusive' content only available via email list",
                "Create a free Discord or Telegram community for followers",
                "Run a giveaway requiring email signup to enter",
                "Post 'Comment GUIDE and I'll DM you my free resource' posts",
            ],
            kpis=["Email opt-in rate", "Lead magnet downloads", "List growth/week"],
            tools=["Beehiiv", "ConvertKit", "MailerLite", "Linktree", "Stan Store"],
        ),
        ConversionStrategy(
            stage="4. Convert (Revenue)",
            goal="Monetize your audience through products and partnerships",
            tactics=[
                "Email your list 2-3x per week with value + soft sell",
                "Launch your first low-ticket offer ($9-29) to warm buyers",
                "Pitch affiliate products that align with your niche content",
                "Negotiate brand deals at $100 per 10K followers baseline rate",
                "Upsell buyers from low-ticket → mid-ticket ($99-299) offer",
            ],
            kpis=["Revenue per email subscriber", "Conversion rate", "AOV (avg order value)"],
            tools=["Gumroad", "Stan Store", "Kajabi", "ShareASale", "Impact.com"],
        ),
        ConversionStrategy(
            stage="5. Retain & Scale",
            goal="Keep customers buying and scale what works",
            tactics=[
                "Create a membership community ($29-99/month recurring)",
                "Cross-promote across 3+ platforms for diversified reach",
                "Hire a VA to handle content curation and repurposing",
                "Test paid ads to amplify organic-performing content",
                "Launch a higher-ticket program ($499-1997) once trust is built",
            ],
            kpis=["Churn rate", "LTV (lifetime value)", "MRR growth"],
            tools=["Skool", "Circle", "Patreon", "Meta Ads", "TikTok Ads"],
        ),
    ]


def theme_page_sop(niche: str = "general") -> dict:
    """Return a complete Standard Operating Procedure for running a theme page."""
    return {
        "niche": niche,
        "daily_workflow": [
            "08:00 — Check trending sounds on TikTok Discover (5 min)",
            "08:15 — Curate 5-10 pieces of content from approved sources",
            "09:00 — Schedule posts for the day using Buffer or Later",
            "12:00 — Engage with all comments/DMs from morning posts",
            "15:00 — Post your highest-value piece of the day (peak window)",
            "17:00 — Create 2-3 Stories for Instagram to boost algorithm signal",
            "20:00 — Check analytics, note what performed well",
            "20:30 — Batch-create tomorrow's content using today's learnings",
        ],
        "weekly_workflow": [
            "Monday — Content audit: review what worked last week",
            "Tuesday — Hashtag refresh: rotate to new sets",
            "Wednesday — Competitor research: identify trending content in niche",
            "Thursday — Email your list (newsletter or promo)",
            "Friday — Go live or post your most viral piece",
            "Weekend — Schedule content for the following week",
        ],
        "content_rules": [
            "NEVER post low-res content — quality signals professionalism",
            "Always credit original creators when reposting",
            "Hook in first 3 seconds or lose the viewer",
            "End every post with a question or CTA to drive comments",
            "Post on ALL trending sounds within 72 hours of their peak",
            "70% educational/entertaining, 30% promotional",
            "Test 3 different hooks per week to find your best format",
        ],
        "growth_hacks": [
            "Engage with 50+ posts in your niche daily — comment genuinely",
            "Follow/unfollow is outdated — comment-pod your way to growth instead",
            "Collab with pages in adjacent niches for cross-promotion",
            "Submit to niche aggregator accounts for free shoutouts",
            "Use 'collab post' feature on Instagram for double-audience reach",
            "Reply to comments with videos (TikTok) — algorithm rewards this",
        ],
        "monetization_timeline": {
            "0-1K followers": "Focus ONLY on growth. Test content formats. Build the habit.",
            "1K-5K followers": "Start affiliate links. Build email list. Test what your audience wants.",
            "5K-10K followers": "Launch first paid product ($9-29). Pitch micro-brand deals.",
            "10K-50K followers": "Scale what works. Hire VA. Negotiate $500+ brand deals.",
            "50K+ followers": "Full monetization. Premium sponsorships. High-ticket offers.",
        },
    }
