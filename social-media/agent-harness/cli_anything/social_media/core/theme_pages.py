"""Theme page creation and conversion guide.

A theme page is a niche-focused social account that curates/reposts
content from its topic rather than creating original content, then
monetizes through affiliate marketing, sponsored posts, shoutouts,
and digital product sales.

This module provides:
- Niche selection and validation
- Step-by-step launch playbook
- Monetization path analysis
- Content sourcing strategies
- Conversion optimization tactics
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


# ── Data models ───────────────────────────────────────────────────────

@dataclass
class NicheAnalysis:
    niche: str
    competition_level: str        # 'low' | 'medium' | 'high'
    monetization_potential: str   # 'low' | 'medium' | 'high' | 'very high'
    growth_speed: str             # 'slow' | 'medium' | 'fast' | 'explosive'
    avg_cpm: float                # Estimated CPM in USD
    affiliate_commissions: str    # Typical % or flat fee
    top_platforms: list[str]
    content_difficulty: str       # 'easy' | 'medium' | 'hard'
    audience_demographics: str
    top_hashtags: list[str]
    monetization_paths: list[str]
    notes: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ThemePagePlaybook:
    niche: str
    platform: str
    phase_1_launch: list[str]     # Days 1-7
    phase_2_growth: list[str]     # Days 8-30
    phase_3_scale: list[str]      # Days 31-90
    phase_4_monetize: list[str]   # Day 90+
    content_sources: list[str]
    posting_schedule: dict
    hashtag_sets: list[list[str]]  # Rotate through these
    bio_templates: list[str]
    monetization_timeline: list[dict]
    tools_needed: list[dict]       # [{tool, purpose, cost}]
    common_mistakes: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ConversionStrategy:
    """Strategies for converting followers into revenue."""
    strategy_name: str
    description: str
    setup_time: str
    income_potential: str         # e.g., '$50-$500/month'
    difficulty: str               # 'beginner' | 'intermediate' | 'advanced'
    steps: list[str]
    tools: list[str]
    examples: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


# ── Niche database ────────────────────────────────────────────────────

_NICHES: dict[str, NicheAnalysis] = {
    "luxury_lifestyle": NicheAnalysis(
        niche="luxury_lifestyle",
        competition_level="high",
        monetization_potential="very high",
        growth_speed="fast",
        avg_cpm=15.0,
        affiliate_commissions="3-8% (luxury goods, travel, cars)",
        top_platforms=["instagram", "tiktok", "youtube"],
        content_difficulty="easy",
        audience_demographics="18-35, aspirational, high-income or income-aspiring",
        top_hashtags=["luxurylifestyle", "rich", "luxury", "millionairemindset",
                      "wealthymindset", "richlife", "goals"],
        monetization_paths=[
            "Luxury brand affiliate programs (Net-A-Porter, Farfetch, luxury watch brands)",
            "High-ticket travel partnerships (hotel chains, private charter companies)",
            "Selling shoutouts ($100-$5,000/post at scale)",
            "Coaching/consulting on 'living wealthy'",
            "Private Discord/community ($50-$200/month subscription)",
        ],
        notes="High CPM due to affluent audience. Repost luxury car/mansion/travel content. "
              "Use 'aspiration gap' — show a lifestyle slightly above your audience.",
    ),
    "fitness": NicheAnalysis(
        niche="fitness",
        competition_level="very high",
        monetization_potential="high",
        growth_speed="medium",
        avg_cpm=8.0,
        affiliate_commissions="5-15% (supplements, equipment, apparel)",
        top_platforms=["tiktok", "instagram", "youtube"],
        content_difficulty="medium",
        audience_demographics="16-35, health-conscious, motivated",
        top_hashtags=["fitness", "gym", "workout", "fitfam", "gains",
                      "bodybuilding", "fitnessmotivation"],
        monetization_paths=[
            "Supplement affiliate programs (MyProtein, GNC, Optimum Nutrition) — 10-15% commission",
            "Fitness apparel (Gymshark affiliate, AYBL, Alphalete) — 10-20%",
            "Custom workout plans via Gumroad ($15-$97)",
            "1-on-1 online coaching ($150-$500/month)",
            "Fitness equipment affiliate (Amazon, Rogue, REP Fitness)",
        ],
        notes="Sub-niches perform better: calisthenics, powerlifting, women's fitness, "
              "fat loss, home workouts. Transformation content goes viral.",
    ),
    "personal_finance": NicheAnalysis(
        niche="personal_finance",
        competition_level="high",
        monetization_potential="very high",
        growth_speed="medium",
        avg_cpm=25.0,
        affiliate_commissions="$50-$300 CPA (credit cards, brokerages, robo-advisors)",
        top_platforms=["tiktok", "youtube", "instagram"],
        content_difficulty="medium",
        audience_demographics="22-45, financially motivated, aspiring to financial freedom",
        top_hashtags=["personalfinance", "moneyhabits", "investing", "wealthbuilding",
                      "financialfreedom", "moneymanagement", "passiveincome"],
        monetization_paths=[
            "Credit card affiliate (Chase, Capital One, Amex) — $50-$200/approval",
            "Brokerage referrals (Webull, M1 Finance, Robinhood) — $5-$75/signup",
            "Digital products: budget templates, investment calculators ($7-$47)",
            "Online course: 'How to Invest' ($97-$497)",
            "High CPM YouTube channel on finance topics ($20-$50 CPM)",
        ],
        notes="Highest CPM niche. Evergreen content. 'Money tips' and 'saving hacks' go viral. "
              "YMYL niche — be accurate to avoid account strikes.",
    ),
    "travel": NicheAnalysis(
        niche="travel",
        competition_level="high",
        monetization_potential="high",
        growth_speed="fast",
        avg_cpm=12.0,
        affiliate_commissions="3-8% (hotels, flights, tours)",
        top_platforms=["instagram", "tiktok", "youtube"],
        content_difficulty="medium",
        audience_demographics="20-40, travel-enthusiastic, moderate-high income",
        top_hashtags=["travel", "wanderlust", "travelgram", "adventure",
                      "travelblogger", "exploremore", "traveltheworld"],
        monetization_paths=[
            "Hotel/accommodation affiliate (Booking.com 4%, Hotels.com, Airbnb)",
            "Travel insurance affiliate (SafetyWing, World Nomads) — $25-$50/sale",
            "Tour operator partnerships",
            "Credit card travel affiliate (high commissions)",
            "Travel guide/ebook ($7-$27)",
        ],
        notes="'Hidden gems' and 'budget travel' sub-niches growing fastest. "
              "Repost stunning destination photos/videos. B-roll reposts work extremely well.",
    ),
    "motivation": NicheAnalysis(
        niche="motivation",
        competition_level="medium",
        monetization_potential="medium",
        growth_speed="explosive",
        avg_cpm=5.0,
        affiliate_commissions="5-20% (books, courses, productivity apps)",
        top_platforms=["tiktok", "instagram", "youtube"],
        content_difficulty="easy",
        audience_demographics="16-35, goal-oriented, ambitious",
        top_hashtags=["motivation", "mindset", "successmindset", "motivationalquotes",
                      "hustle", "grindset", "growthmindset"],
        monetization_paths=[
            "Book affiliate (Amazon Associates) — promotion of self-help books",
            "Online course promotion (Udemy, Coursera) — 15-30% commission",
            "Productivity app affiliate (Notion, Todoist)",
            "Selling motivation e-book or quote packs ($5-$27)",
            "Shoutouts to other motivational accounts ($20-$500/post)",
        ],
        notes="Easiest niche to grow. Lowest CPM. Repurpose famous speech clips, "
              "motivational quotes on aesthetic backgrounds. Explosive growth potential.",
    ),
    "food": NicheAnalysis(
        niche="food",
        competition_level="high",
        monetization_potential="medium",
        growth_speed="fast",
        avg_cpm=7.0,
        affiliate_commissions="3-10% (meal kits, appliances, cookbooks)",
        top_platforms=["tiktok", "instagram", "youtube"],
        content_difficulty="easy",
        audience_demographics="18-45, home cooks, food enthusiasts",
        top_hashtags=["foodie", "recipe", "easyrecipes", "homecooking",
                      "mealprep", "foodlover", "yummy"],
        monetization_paths=[
            "Meal kit affiliate (HelloFresh, EveryPlate) — $15-$30/signup",
            "Kitchen appliance affiliate (Amazon, Williams-Sonoma)",
            "Cookbook affiliate",
            "Selling recipe e-books ($7-$47)",
            "Brand deals with food brands",
        ],
        notes="ASMR cooking and 'recipe hack' formats explode on TikTok. "
              "Repost satisfying cooking videos from recipe creators.",
    ),
    "pets": NicheAnalysis(
        niche="pets",
        competition_level="medium",
        monetization_potential="medium",
        growth_speed="fast",
        avg_cpm=6.0,
        affiliate_commissions="4-10% (pet food, accessories, insurance)",
        top_platforms=["tiktok", "instagram", "youtube"],
        content_difficulty="easy",
        audience_demographics="18-55, pet owners — extremely loyal and emotionally engaged",
        top_hashtags=["pets", "dogs", "cats", "dogsoftiktok", "catsoftiktok",
                      "animallover", "petvideo"],
        monetization_paths=[
            "Pet food affiliate (Chewy 4-6%, Amazon pet products)",
            "Pet insurance affiliate (Lemonade, Spot) — $25-$75/signup",
            "Pet accessory affiliate",
            "Custom pet portrait digital product ($15-$97)",
            "Pet training guide/course ($27-$197)",
        ],
        notes="Extremely viral. Cute animals = emotion = shares. "
              "Dog and cat sub-niches are biggest. Highest share-to-view ratio of any niche.",
    ),
    "tech": NicheAnalysis(
        niche="tech",
        competition_level="very high",
        monetization_potential="very high",
        growth_speed="medium",
        avg_cpm=20.0,
        affiliate_commissions="2-8% (Amazon electronics, software, VPNs)",
        top_platforms=["youtube", "tiktok", "instagram"],
        content_difficulty="hard",
        audience_demographics="18-40, tech-savvy, higher disposable income",
        top_hashtags=["tech", "technology", "gadgets", "techreview",
                      "newtech", "technews", "techhacks"],
        monetization_paths=[
            "Amazon Associates for electronics (2-4%)",
            "VPN affiliate (NordVPN, ExpressVPN) — $40-$100/sale",
            "Software/SaaS affiliate (high commissions)",
            "Tech course affiliate",
            "Sponsored tech reviews",
        ],
        notes="High CPM due to male tech audience. 'Tech hacks' and 'best tech under $X' "
              "formats perform well. Requires some technical knowledge.",
    ),
}


# ── Playbook builder ──────────────────────────────────────────────────

def _build_playbook(niche: str, platform: str) -> ThemePagePlaybook:
    """Build a full launch playbook for a theme page."""
    niche_data = _NICHES.get(niche.lower(), _NICHES.get("motivation"))  # default to motivation
    niche_name = niche_data.niche if niche_data else niche
    top_tags = niche_data.top_hashtags if niche_data else []

    # Phase 1: Launch (Days 1-7)
    phase_1 = [
        f"Day 1: Create account with keyword-rich username (e.g., '@{niche_name.replace('_','')}.daily' "
        f"or '@the{niche_name.replace('_','')}page')",
        "Day 1: Set up profile — keyword in bio, link in bio (Stan Store or Linktree), "
        "niche-specific profile picture",
        f"Day 1-3: Follow 50-100 accounts in the #{niche_name} niche — "
        "follow-back rate fills initial follower count",
        "Day 1-7: Post 3x per day — morning (7am), afternoon (12pm), evening (8pm) "
        "in your target audience's timezone",
        "Day 1-7: Source 21+ pieces of content from these platforms before you start: "
        "Reddit, Pinterest, other theme pages, creator accounts",
        "Day 3: Engage with 20 posts/day using your target hashtags — "
        "like, comment with value (not just emojis)",
        "Day 5: Post a 'community' video asking followers a question — "
        "comments boost algorithmic reach",
        "Day 7: Analyze which posts performed best — double down on that format",
    ]

    # Phase 2: Growth (Days 8-30)
    phase_2 = [
        "Days 8-30: Maintain 3x/day posting — consistency is non-negotiable",
        "Days 8-14: Start testing trending sounds/music on every post",
        "Day 10: Duet or Stitch a viral post in your niche — "
        "borrow momentum from existing viral content",
        "Day 14: Go Live for the first time — even 15 minutes boosts profile visibility",
        "Days 15-30: DM 5 accounts/day in your niche for shoutout-for-shoutout (S4S) exchanges",
        "Day 20: Create a series (e.g., 'Day [X] of posting about [niche]') — "
        "series build habitual viewers",
        "Day 25: Submit your account to niche-specific feature pages for a free shoutout",
        "Day 30: Audit your analytics — identify your best posting time and top-performing format",
    ]

    # Phase 3: Scale (Days 31-90)
    phase_3 = [
        "Days 31-60: Post 1-2x higher quality > 3x lower quality — now quality > quantity",
        "Day 35: Set up affiliate links in bio and start mentioning products naturally in captions",
        "Day 40: Reach out to 3 brands in your niche for a free product collab",
        "Day 45: Launch your first digital product (guide or template) — price $7-$27",
        "Day 50: Cross-post your content to a second platform "
        "(if on TikTok → also post to Instagram Reels and YouTube Shorts)",
        "Day 60: Create a 'Best of [Month]' compilation — repurposes existing content for new reach",
        "Day 75: If 10K+ followers, reach out to brands with a media kit for paid deals",
        "Day 90: Evaluate which monetization path is generating the most revenue — scale that",
    ]

    # Phase 4: Monetize (Day 90+)
    phase_4 = [
        "Set up a shoutout rate card and post it publicly (e.g., in your highlights/pinned post)",
        "Apply to 3+ affiliate programs in your niche this month",
        "Launch a second digital product at a higher price point ($27-$97)",
        "Build a 'free value → paid offer' funnel: Free tip → Free lead magnet → Paid product",
        "Create a newsletter/email list — algorithms come and go, email is owned media",
        "If 50K+ followers: hire a virtual assistant to handle DMs, comments, and content scheduling",
        "Consider 'selling' the theme page to another creator once valued — "
        "pages sell for 24-36x monthly revenue",
    ]

    # Content sources
    content_sources = [
        "Reddit: Browse r/{niche_name}, sort by Hot/Top All Time — screenshot/repost text posts",
        "Pinterest: Search [niche] inspiration — download viral pins",
        "YouTube: Download viral shorts with yt-dlp (credit creator in caption)",
        "Other theme pages: Repost their viral content (credit with @mention to build goodwill)",
        "Canva: Create quote graphics using free templates — fastest original content",
        "CapCut: Edit clips together using trending templates — no video skills needed",
        "Pexels / Unsplash: Free stock video and photos for aesthetic posts",
    ]

    # Posting schedule
    posting_schedule = {
        "platform": platform,
        "frequency": "3x per day (weeks 1-4), 1-2x per day (month 2+)",
        "best_times": ["7:00 AM", "12:00 PM", "7:00 PM"],
        "timezone_note": "Use your largest audience's timezone (check analytics after week 1)",
        "days": "Every day — never skip more than 1 day or you reset the algorithm",
    }

    # Hashtag rotation sets
    hashtag_sets = [
        top_tags[:4] + ["viral", "fyp"],
        top_tags[2:6] + ["trending", "foryoupage"],
        top_tags[1:5] + ["explore", "content"],
    ]

    # Bio templates
    bio_templates = [
        f"Daily {niche_name.replace('_',' ')} inspiration | "
        f"Follow for the best {niche_name.replace('_',' ')} content | "
        f"Link below for free [lead magnet]",
        f"#{niche_name.replace('_','')} obsessed | "
        f"Curating the best content so you don't have to | "
        f"New post every day",
        f"The #{1} {niche_name.replace('_',' ')} page | "
        f"[X]K+ followers growing | "
        f"DM for collabs",
    ]

    # Monetization timeline
    monetization_timeline = [
        {
            "milestone": "0-1K followers",
            "action": "Set up affiliate links in bio — even 1K followers can generate $50-$200/month",
            "expected_income": "$0-$50/month",
        },
        {
            "milestone": "1K-10K followers",
            "action": "Launch digital product ($7-$27), start S4S exchanges for exposure",
            "expected_income": "$50-$500/month",
        },
        {
            "milestone": "10K-50K followers",
            "action": "Sell shoutouts ($25-$200/post), pitch brands for paid deals",
            "expected_income": "$300-$2,000/month",
        },
        {
            "milestone": "50K-100K followers",
            "action": "Agency-level brand deals, scale digital products, build email list",
            "expected_income": "$1,000-$10,000/month",
        },
        {
            "milestone": "100K+ followers",
            "action": "Long-term brand partnerships, launch premium community, consider selling page",
            "expected_income": "$5,000-$50,000+/month",
        },
    ]

    # Tools
    tools_needed = [
        {"tool": "CapCut", "purpose": "Free video editing with trending templates", "cost": "Free"},
        {"tool": "Canva", "purpose": "Quote graphics, thumbnails, story templates", "cost": "Free / $12.99/mo Pro"},
        {"tool": "Later / Buffer", "purpose": "Schedule posts in advance", "cost": "Free tier available"},
        {"tool": "Stan Store / Gumroad", "purpose": "Sell digital products + link in bio", "cost": "Free / 9% transaction fee"},
        {"tool": "Linktree", "purpose": "Multi-link bio page if not using Stan Store", "cost": "Free"},
        {"tool": "yt-dlp (this tool)", "purpose": "Download and analyze viral content for reposting", "cost": "Free"},
        {"tool": "Notion", "purpose": "Content calendar and strategy tracking", "cost": "Free"},
    ]

    # Common mistakes
    common_mistakes = [
        "Choosing a niche you have no interest in — you'll burn out within 30 days",
        "Posting inconsistently — 3 posts then nothing for a week resets your algorithmic momentum",
        "Using the same 5 hashtags on every post — platforms penalize repetitive hashtag use",
        "Not engaging with comments — the algorithm rewards accounts that spark conversation",
        "Monetizing too early (before 1K followers) — prioritize growth first, monetization second",
        "Reposting without crediting original creators — leads to strikes and reputation damage",
        "Ignoring analytics — your top-performing posts tell you exactly what to make more of",
        "Quitting before 60 days — most theme pages see exponential growth in months 2-3",
        "Using copyrighted music for ad-eligible content — use royalty-free music instead",
        "Buying followers — kills engagement rate and trust signals, often gets accounts banned",
    ]

    return ThemePagePlaybook(
        niche=niche,
        platform=platform,
        phase_1_launch=phase_1,
        phase_2_growth=phase_2,
        phase_3_scale=phase_3,
        phase_4_monetize=phase_4,
        content_sources=content_sources,
        posting_schedule=posting_schedule,
        hashtag_sets=hashtag_sets,
        bio_templates=bio_templates,
        monetization_timeline=monetization_timeline,
        tools_needed=tools_needed,
        common_mistakes=common_mistakes,
    )


# ── Conversion strategies ─────────────────────────────────────────────

_CONVERSION_STRATEGIES: list[ConversionStrategy] = [
    ConversionStrategy(
        strategy_name="Bio Link Funnel",
        description="Convert profile visitors into leads and buyers via an optimized bio link page",
        setup_time="1-2 hours",
        income_potential="$100-$5,000/month",
        difficulty="beginner",
        steps=[
            "Create a Stan Store or Gumroad account",
            "Add a freebie (e.g., '5 Viral Caption Templates') to capture emails",
            "Add your paid digital product ($7-$97) below the freebie",
            "Add affiliate links for 2-3 products you genuinely recommend",
            "Link this page in your bio",
            "In every video, mention 'link in bio' to drive traffic",
        ],
        tools=["Stan Store (free)", "Gumroad (free)", "Canva (for product creation)"],
        examples=[
            "Fitness page: Free '7-Day Workout Plan' → paid '$47 Full Program'",
            "Finance page: Free 'Budget Template' → paid '$27 Investment Guide'",
            "Travel page: Free 'Packing List' → affiliate hotel booking links",
        ],
    ),
    ConversionStrategy(
        strategy_name="Shoutout Business",
        description="Sell promotional posts to brands and smaller accounts in your niche",
        setup_time="30 minutes",
        income_potential="$200-$10,000/month",
        difficulty="beginner",
        steps=[
            "Create a simple rate card: 1 post = $X, Story = $Y, Bundle = $Z",
            "Post rate card in your bio highlights or pinned post",
            "DM 10 smaller accounts in your niche offering a free first shoutout for a review",
            "Set up a simple booking system (just a DM or a Calendly link)",
            "Deliver shoutouts that actually perform — your reputation is your product",
            "Raise rates every time you hit a new follower milestone",
        ],
        tools=["DMs", "Calendly (free)", "PayPal or Venmo for payment"],
        examples=[
            "5K followers: $25-$75/post",
            "20K followers: $100-$300/post",
            "100K followers: $500-$2,500/post",
        ],
    ),
    ConversionStrategy(
        strategy_name="Affiliate Marketing Stack",
        description="Build a passive income stream by promoting relevant products in every post",
        setup_time="3-5 hours (setup) then passive",
        income_potential="$50-$3,000/month",
        difficulty="beginner",
        steps=[
            "Join Amazon Associates (easiest approval, massive product selection)",
            "Join 1-2 niche-specific affiliate programs (high commission rates)",
            "Create an 'affiliate link' collection page on your link-in-bio",
            "Weave product mentions naturally into captions ('I use [product] for...')",
            "Create 'products I use' content — these convert 3-5x better than direct ads",
            "Track which links convert and double down on those products",
        ],
        tools=["Amazon Associates", "Impact.com", "ShareASale", "your bio link page"],
        examples=[
            "Fitness: 'My favorite pre-workout' → Amazon link ($3-$8/sale)",
            "Finance: 'Best investing app for beginners' → Webull referral ($75/signup)",
            "Travel: 'Best travel credit card' → Chase referral ($100-$200/approval)",
        ],
    ),
    ConversionStrategy(
        strategy_name="Digital Product Ladder",
        description="Create a tiered product suite that takes followers from free to premium",
        setup_time="10-20 hours total",
        income_potential="$500-$20,000/month",
        difficulty="intermediate",
        steps=[
            "Tier 1 (Free): Create a valuable freebie to build email list — PDF guide, template, checklist",
            "Tier 2 ($7-$27): Create a low-ticket digital product (extended guide, video mini-course)",
            "Tier 3 ($97-$297): Create a mid-ticket course or coaching package",
            "Set up email automation: freebie → thank you email → value emails → paid pitch",
            "Use your social content as top-of-funnel traffic to this product ladder",
            "Optimize conversion: A/B test pricing, add testimonials, add payment plan option",
        ],
        tools=["Gumroad / Stan Store", "Mailchimp (free up to 500 subs)", "Canva", "Loom (for video)"],
        examples=[
            "Fitness: Free workout → $17 full plan → $197 coaching program",
            "Finance: Free budget sheet → $27 investing guide → $197 financial freedom course",
            "Travel: Free packing list → $17 travel hacks guide → $97 full nomad blueprint",
        ],
    ),
    ConversionStrategy(
        strategy_name="Paid Community",
        description="Build a recurring revenue subscription community around your niche",
        setup_time="5-10 hours setup",
        income_potential="$500-$50,000/month (recurring)",
        difficulty="intermediate",
        steps=[
            "Choose a platform: Skool ($99/mo), Discord (free), Patreon (free + fee), Circle",
            "Define the value: exclusive content, live Q&As, accountability groups, templates",
            "Offer a founding member rate to first 20-50 members ($10-$50/month)",
            "Promote the community every week in your content",
            "Deliver massive value in first 30 days to reduce churn",
            "Use community testimonials as social proof to grow membership",
        ],
        tools=["Skool", "Discord (free)", "Patreon", "Circle"],
        examples=[
            "Fitness: $27/month for 'accountability club' with weekly live workouts",
            "Finance: $47/month for 'investment research group' with stock picks",
            "Motivation: $17/month for '30-day challenge community' with daily prompts",
        ],
    ),
]


# ── Public API ────────────────────────────────────────────────────────

def get_niche_analysis(niche: str) -> Optional[NicheAnalysis]:
    """Get analysis for a specific niche.

    Args:
        niche: Niche name (e.g., 'fitness', 'personal_finance', 'travel').

    Returns:
        NicheAnalysis object or None if niche not found.
    """
    return _NICHES.get(niche.lower())


def list_niches() -> list[NicheAnalysis]:
    """Return all available niche analyses."""
    return list(_NICHES.values())


def get_playbook(niche: str, platform: str = "tiktok") -> ThemePagePlaybook:
    """Generate a complete theme page launch playbook.

    Args:
        niche: Content niche (e.g., 'fitness', 'motivation', 'travel').
        platform: Target platform ('tiktok', 'instagram', 'youtube').

    Returns:
        ThemePagePlaybook with step-by-step instructions.
    """
    return _build_playbook(niche, platform)


def get_conversion_strategies(
    difficulty: Optional[str] = None,
) -> list[ConversionStrategy]:
    """Get conversion strategies, optionally filtered by difficulty.

    Args:
        difficulty: Filter by 'beginner', 'intermediate', or 'advanced'.
                    None returns all strategies.

    Returns:
        List of ConversionStrategy objects.
    """
    if difficulty:
        return [s for s in _CONVERSION_STRATEGIES if s.difficulty == difficulty.lower()]
    return _CONVERSION_STRATEGIES


def compare_niches(niches: list[str]) -> list[NicheAnalysis]:
    """Compare multiple niches side by side.

    Args:
        niches: List of niche names to compare.

    Returns:
        List of NicheAnalysis objects for the requested niches.
    """
    result = []
    for niche in niches:
        analysis = _NICHES.get(niche.lower())
        if analysis:
            result.append(analysis)
    return result
