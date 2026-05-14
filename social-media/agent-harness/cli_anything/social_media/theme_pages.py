"""
Theme page creation, growth, and conversion playbook.

A "theme page" (also called a "niche page" or "content aggregator") is an
account that curates content around a specific topic rather than a personal
brand. Examples: @MotivationDaily, @FitnessInspo, @TravelVibes.

Theme pages are powerful because:
 - No face/personal brand required
 - Fast to scale (repost + curate)
 - Easier to sell or partner once established
 - Multiple pages can run in parallel
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class ThemePageBlueprint:
    niche: str
    page_name_ideas: list[str] = field(default_factory=list)
    bio_template: str = ""
    content_strategy: list[str] = field(default_factory=list)
    monetization_methods: list[str] = field(default_factory=list)
    estimated_time_to_1k: str = ""
    difficulty: str = ""
    competition_level: str = ""
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Proven niche blueprints
# ---------------------------------------------------------------------------

THEME_PAGE_NICHES: dict[str, dict] = {
    "motivation": {
        "description": "Daily quotes, success mindset, discipline content",
        "difficulty": "beginner",
        "competition_level": "high",
        "estimated_time_to_1k": "7-14 days with consistent posting",
        "page_name_ideas": [
            "DailyMindset", "GrindNation", "ElevateDaily",
            "WinnersMindset", "BuildDiscipline", "StayFocused",
        ],
        "bio_template": "🔥 Daily motivation for go-getters\n✅ Mindset | Discipline | Success\nNew post every day — follow so you never miss it 💪",
        "content_strategy": [
            "Repost viral quote videos with your own caption (always credit)",
            "Text-over-video motivational clips with trending audio",
            "POV / story-style motivation ('Day 1 vs Day 365')",
            "'What I wish I knew at 20' style videos",
            "Screen-record viral motivational clips and add your watermark",
            "Daily 'Do This Today' challenge posts",
        ],
        "content_sources": [
            "Reddit r/GetMotivated, r/Entrepreneur",
            "YouTube motivational channels (with credit)",
            "Canva templates for quote graphics",
            "CapCut trending templates",
        ],
        "monetization": [
            "Affiliate marketing (books, courses, productivity apps)",
            "Digital products (mindset journal, planner PDFs)",
            "Brand sponsorships (supplement companies, apps)",
            "Sell the page once it hits 50K+",
            "Shoutout-for-shoutout (S4S) to grow faster",
        ],
        "notes": "Motivation niche is saturated but still grows fast. Differentiate with a specific sub-niche (e.g. gym motivation, female entrepreneurs, teen success).",
    },
    "fitness": {
        "description": "Workout clips, transformation content, gym lifestyle",
        "difficulty": "beginner-intermediate",
        "competition_level": "very high",
        "estimated_time_to_1k": "14-21 days",
        "page_name_ideas": [
            "GainMode", "SweatNation", "IronMindset",
            "LiftEveryday", "FitVibes", "GymMotivation",
        ],
        "bio_template": "💪 Daily fitness motivation\n🏋️ Workout tips | Transformations | Gains\n📲 New content daily — tap follow!",
        "content_strategy": [
            "Repost impressive workout clips (credit creator in caption)",
            "Before/after transformations (with permission or from willing users)",
            "Top 3 exercises for [muscle group] with text overlay",
            "Day in the life of a gym person",
            "Common workout mistakes (educational + entertaining)",
            "Gym outfit of the day (fashion crossover)",
            "Progress update series",
        ],
        "content_sources": [
            "TikTok fitness creators (repost with credit, DM for permission)",
            "Instagram fitness hashtags",
            "Reddit r/fitness, r/bodybuilding",
            "YouTube fitness channels",
        ],
        "monetization": [
            "Supplement affiliate links (MyProtein, Optimum Nutrition, etc.)",
            "Gym wear affiliate (Gymshark, Alphalete)",
            "Workout plan / PDF programs (sell on Gumroad)",
            "Online coaching upsell",
            "Brand partnerships",
        ],
        "notes": "Sub-niche for faster growth: focus on one specific goal (e.g., abs, glutes, home workouts, beginners, over-40 fitness).",
    },
    "luxury": {
        "description": "Cars, watches, houses, lifestyle aspirational content",
        "difficulty": "beginner",
        "competition_level": "medium",
        "estimated_time_to_1k": "7-14 days",
        "page_name_ideas": [
            "LuxuryVibes", "WealthMindset", "EliteLifestyle",
            "MillionaireMoves", "LuxuryGoals", "RichLifestyle",
        ],
        "bio_template": "🏆 Luxury lifestyle inspiration\n🚗 Supercars | Watches | Dream Homes\nFollow for daily luxury motivation 👑",
        "content_strategy": [
            "Supercar reveal videos (compilations from YouTube)",
            "Watch unboxings / collection tours",
            "Private jet / yacht content",
            "'If you had $1M what would you buy?' polls",
            "Wealth mindset quotes over luxury b-roll",
            "Luxury real estate tours",
            "'Earn it, don't wish for it' educational posts",
        ],
        "monetization": [
            "Luxury affiliate programs (watches, cars, fashion)",
            "Financial product affiliates (investment apps, credit cards)",
            "Business / side hustle course affiliates",
            "Sell the page (high demand from brands)",
        ],
        "notes": "Works extremely well on TikTok and Instagram. Content is easy to source from YouTube.",
    },
    "relationships": {
        "description": "Dating advice, couple goals, relationship tips",
        "difficulty": "beginner",
        "competition_level": "medium-high",
        "estimated_time_to_1k": "7-14 days",
        "page_name_ideas": [
            "CoupleGoals", "LoveAndLife", "DatingAdvice",
            "RelationshipTips", "HeartMatters", "WiseInLove",
        ],
        "bio_template": "❤️ Relationship tips & couple goals\n💑 Love | Growth | Communication\nFollow for daily relationship wisdom 💌",
        "content_strategy": [
            "Couple goals videos (with credit)",
            "Dating red flags / green flags lists",
            "'Signs they like you' educational posts",
            "Relationship advice voiceovers",
            "POV: healthy relationship scenarios",
            "Love language explainers",
            "Trending relationship questions / polls",
        ],
        "monetization": [
            "Dating app affiliate programs (Bumble, Hinge, eHarmony)",
            "Couples counseling / therapy affiliates",
            "Books on relationships (Amazon affiliate)",
            "Digital products (dating guide, communication scripts)",
        ],
        "notes": "Very sticky content — high saves and shares. Blend entertainment with genuine value.",
    },
    "cooking": {
        "description": "Recipes, food hacks, restaurant reviews",
        "difficulty": "beginner-intermediate",
        "competition_level": "high",
        "estimated_time_to_1k": "14-30 days",
        "page_name_ideas": [
            "EasyMeals", "QuickRecipes", "HomeCooking",
            "TastyVibes", "FoodHacks", "MealInspiration",
        ],
        "bio_template": "🍳 Easy recipes for busy people\n🥗 Quick | Healthy | Delicious\nNew recipe daily — save it for later! 💾",
        "content_strategy": [
            "Short recipe tutorials (60 seconds or less)",
            "'5-ingredient meals' series",
            "Grocery budget meals (budget cooking niche)",
            "Restaurant dupe recipes",
            "Meal prep Sunday content",
            "Trending recipes (recreate what's going viral)",
            "Food hacks and kitchen tips",
        ],
        "monetization": [
            "Meal kit affiliate (HelloFresh, Factor, etc.)",
            "Kitchen product affiliate (Amazon)",
            "Digital cookbook / meal plan PDF",
            "Brand partnerships with food companies",
        ],
        "notes": "Recipe content gets massive saves (saves boost the algorithm). Focus on simplicity — viewers want easy, fast meals.",
    },
    "memes": {
        "description": "Relatable comedy, internet humor, viral memes",
        "difficulty": "intermediate",
        "competition_level": "high",
        "estimated_time_to_1k": "3-7 days (if a post goes viral)",
        "page_name_ideas": [
            "RelatableVibes", "ModernProblems", "LaughNation",
            "MoodBoard", "ItsGivingFunny", "ThatFeelWhen",
        ],
        "bio_template": "😂 Relatable content that hits different\n🤣 Memes | Humor | Real Life\nFollow so your FYP stays funny 🔥",
        "content_strategy": [
            "Curate the most relatable memes from Reddit",
            "Reaction videos to viral content",
            "POV series (relatable scenarios with twist endings)",
            "Text-over-video 'nobody:' format memes",
            "Trending audio + relatable situation",
            "'Things that just make sense' lists",
            "Gen Z / millennial cultural humor",
        ],
        "monetization": [
            "Brand partnerships (brands love meme pages for authenticity)",
            "Promoted posts / shoutouts",
            "Merchandise (meme-based merch)",
            "Sell the page",
        ],
        "notes": "Fastest niche to go viral but also hardest to sustain. Trend cycle is very fast — must post daily.",
    },
    "pets": {
        "description": "Cute animals, pet care tips, funny pet content",
        "difficulty": "beginner",
        "competition_level": "medium",
        "estimated_time_to_1k": "7-14 days",
        "page_name_ideas": [
            "DailyDogs", "PawNation", "FurBabyVibes",
            "CuteOverload", "PetParent", "FluffyFeed",
        ],
        "bio_template": "🐾 Daily cute animal content\n🐶🐱 Dogs | Cats | All the fluff\nFollow for your daily dose of cute! 🥰",
        "content_strategy": [
            "Repost viral pet videos (always credit)",
            "Funny pet behavior compilations",
            "'Dogs react to...' series",
            "Pet of the day features",
            "Cat vs dog debates",
            "Heartwarming rescue stories",
            "Pet product reviews/recommendations",
        ],
        "monetization": [
            "Pet product affiliate (Chewy, Amazon pet store)",
            "Pet insurance affiliates",
            "Pet food brand partnerships",
            "Digital guides (pet training, care)",
        ],
        "notes": "Extremely high engagement. Pet content rarely gets hate. Great for brand partnerships since audience is passionate buyers.",
    },
    "finance": {
        "description": "Money tips, investing basics, side hustles",
        "difficulty": "intermediate",
        "competition_level": "medium",
        "estimated_time_to_1k": "21-45 days",
        "page_name_ideas": [
            "MoneyMoves", "WealthTips", "FinanceFuel",
            "SideHustleNation", "InvestingSimple", "CashFlowDaily",
        ],
        "bio_template": "💰 Money tips nobody taught you in school\n📈 Investing | Side Hustles | Budgeting\nFollow to build real wealth 🏦",
        "content_strategy": [
            "'Money rule' posts (60-second finance lessons)",
            "'This is how I made $X in Y days' (side hustle content)",
            "Investment explainers (stocks, ETFs, crypto — simplified)",
            "'Bad money habits to stop TODAY'",
            "Paycheck budgeting formulas (50/30/20 etc.)",
            "Passive income ideas lists",
            "'What I'd do with $1,000' scenarios",
        ],
        "monetization": [
            "Investment app affiliate (Robinhood, Acorns, M1 Finance)",
            "Credit card affiliate (high commission — $50-300 per signup)",
            "Online course affiliate (financial literacy courses)",
            "Digital products (budget templates, investing guides)",
            "Consulting / coaching",
        ],
        "notes": "Finance niche has the highest affiliate commissions. Credit card affiliates pay $50-300 per approved application. Build trust before heavy promotion.",
    },
}


def get_niche_blueprint(niche: str) -> ThemePageBlueprint:
    """Get a full theme page blueprint for a specific niche."""
    key = niche.lower().replace(" ", "").replace("-", "")
    if key not in THEME_PAGE_NICHES:
        available = ", ".join(THEME_PAGE_NICHES.keys())
        raise ValueError(f"No blueprint for '{niche}'. Available niches: {available}")

    data = THEME_PAGE_NICHES[key]
    return ThemePageBlueprint(
        niche=niche,
        page_name_ideas=data.get("page_name_ideas", []),
        bio_template=data.get("bio_template", ""),
        content_strategy=data.get("content_strategy", []),
        monetization_methods=data.get("monetization", []),
        estimated_time_to_1k=data.get("estimated_time_to_1k", ""),
        difficulty=data.get("difficulty", ""),
        competition_level=data.get("competition_level", ""),
        notes=data.get("notes", ""),
    )


def list_niches() -> list[dict]:
    """List all available theme page niches with summary info."""
    return [
        {
            "niche": k,
            "description": v["description"],
            "difficulty": v["difficulty"],
            "competition": v["competition_level"],
            "time_to_1k": v["estimated_time_to_1k"],
        }
        for k, v in THEME_PAGE_NICHES.items()
    ]


# ---------------------------------------------------------------------------
# Conversion strategy — turning an existing page into a money-maker
# ---------------------------------------------------------------------------

CONVERSION_STAGES = [
    {
        "stage": 1,
        "name": "Foundation (0-1K followers)",
        "goal": "Establish niche identity and build trust",
        "actions": [
            "Pick ONE specific niche and commit for 90 days",
            "Optimize bio with clear value proposition",
            "Post 5-7x per week using trending audio",
            "Use balanced hashtag strategy (3 broad + 8 niche + 3 micro)",
            "Engage 30 min/day with accounts in your niche",
            "Set up Linktree or link-in-bio (even if not monetizing yet)",
            "Batch-create 1 week of content every Sunday",
        ],
        "avoid": [
            "Switching niches before 90 days",
            "Promoting products before establishing trust",
            "Inconsistent posting gaps longer than 3 days",
            "Buying followers (destroys engagement rate)",
        ],
    },
    {
        "stage": 2,
        "name": "Growth (1K-10K followers)",
        "goal": "Establish authority and test monetization",
        "actions": [
            "Post 1x daily minimum at peak times",
            "Launch a recurring series (builds return visits)",
            "Collaborate with similar-sized creators in your niche",
            "Start collecting emails (free resource in bio)",
            "Test first soft monetization (affiliate link in bio)",
            "Cross-post to a second platform (don't watermark when cross-posting)",
            "Run polls and Q&As to understand your audience",
        ],
        "avoid": [
            "Heavy promotion before 5K followers",
            "Posting purely promotional content",
            "Ignoring DMs and comments",
            "Cross-posting watermarked TikTok videos to Instagram Reels",
        ],
    },
    {
        "stage": 3,
        "name": "Monetization (10K-50K followers)",
        "goal": "Turn audience into revenue",
        "actions": [
            "Pitch brands for paid partnerships ($150-500 per post at this stage)",
            "Launch your first digital product (guide, template, course)",
            "Add affiliate links to all relevant posts",
            "Build email list aggressively (offer free resource)",
            "Create 'premium' content for paid community (Patreon, Discord)",
            "Post on YouTube for long-form authority content",
            "Optimize top-performing posts with better CTAs",
        ],
        "revenue_benchmarks": {
            "brand_deal_rate": "$150-500 per post (10K followers)",
            "affiliate_monthly": "$200-1,000+ (depends on niche + traffic)",
            "digital_product": "$1,000-5,000/month with good funnel",
        },
    },
    {
        "stage": 4,
        "name": "Scale (50K-500K followers)",
        "goal": "Systemize, automate, and maximize revenue",
        "actions": [
            "Hire a video editor (outsource content production)",
            "Post 2x daily minimum using batched content",
            "Negotiate brand deals at $500-5,000+ per post",
            "Launch premium course or coaching program",
            "Build sales funnel: Content → Email → Offer",
            "Consider launching additional theme pages in adjacent niches",
            "Explore page acquisition (buy established pages to fast-track growth)",
        ],
        "revenue_benchmarks": {
            "brand_deal_rate": "$1,000-10,000 per post (100K+ followers)",
            "affiliate_monthly": "$2,000-20,000+ (niche-dependent)",
            "course_monthly": "$5,000-50,000+ with right audience",
        },
    },
]


def get_conversion_roadmap() -> list[dict]:
    """Return the full theme page → money conversion roadmap."""
    return CONVERSION_STAGES


def get_conversion_stage(followers: int) -> dict:
    """Return the relevant conversion stage based on follower count."""
    if followers < 1000:
        return CONVERSION_STAGES[0]
    elif followers < 10000:
        return CONVERSION_STAGES[1]
    elif followers < 50000:
        return CONVERSION_STAGES[2]
    else:
        return CONVERSION_STAGES[3]


# ---------------------------------------------------------------------------
# Page acquisition guide (buying existing theme pages)
# ---------------------------------------------------------------------------

PAGE_ACQUISITION_GUIDE = {
    "overview": (
        "Acquiring (buying) an existing theme page lets you skip the early growth "
        "phase. Established pages with real engagement can be purchased and redirected "
        "to your niche/monetization strategy."
    ),
    "where_to_buy": [
        "Fameswap.com — marketplace for Instagram/TikTok/YouTube pages",
        "Social Tradia — verified social media page sales",
        "EmpireFlippers.com — for larger, monetized accounts",
        "Flippa.com — for pages with revenue history",
        "Facebook groups — 'Instagram page sales', 'TikTok page marketplace'",
        "Direct outreach — DM theme pages in your niche and ask if they're selling",
    ],
    "what_to_look_for": [
        "Engagement rate above 3% (views/followers) — not just follower count",
        "Niche alignment with your monetization plan",
        "No history of fake followers (check with HypeAuditor or modash.io)",
        "Active posting history (not dormant for months)",
        "Clear ownership transfer process (email linked to account)",
        "Audience demographics matching your target buyer",
    ],
    "red_flags": [
        "Engagement rate below 1% — fake follower history",
        "Sudden follower spikes in analytics",
        "Account name not matching niche",
        "Seller won't provide account analytics screenshots",
        "Price seems too good to be true",
        "No established email connected or 2FA issues",
    ],
    "pricing_benchmarks": {
        "1K-10K (low engagement)": "$50-200",
        "1K-10K (high engagement)": "$100-500",
        "10K-50K (avg engagement)": "$300-2,000",
        "50K-100K (avg engagement)": "$1,000-8,000",
        "100K+ (avg engagement)": "$3,000-50,000+",
        "monetized accounts": "3-12x monthly revenue",
    },
    "conversion_strategy": [
        "Step 1: Gradually shift content to new niche (don't abrupt-change)",
        "Step 2: Update bio and profile photo to match new direction",
        "Step 3: Maintain posting frequency to keep algorithm happy",
        "Step 4: Start engaging with new niche community to attract right followers",
        "Step 5: Monetize once you've established the new identity (30-60 days)",
    ],
    "tools": {
        "analytics_audit": ["HypeAuditor", "modash.io", "Social Blade"],
        "valuation": ["Fameswap calculator", "Social Tradia estimator"],
        "fake_follower_check": ["HypeAuditor", "IG Audit (free)", "Noxinfluencer"],
    },
}


def get_acquisition_guide() -> dict:
    """Return the page acquisition guide for buying existing theme pages."""
    return PAGE_ACQUISITION_GUIDE


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def recommend_niche(
    interests: list[str],
    risk_tolerance: str = "medium",
    time_available: str = "1-2 hours/day",
) -> list[dict]:
    """
    Recommend theme page niches based on personal preferences.
    risk_tolerance: low | medium | high
    time_available: <1 hour/day | 1-2 hours/day | 3+ hours/day
    """
    scored: list[dict] = []

    difficulty_map = {"beginner": 3, "beginner-intermediate": 2, "intermediate": 1}
    time_map = {"<1 hour/day": 1, "1-2 hours/day": 2, "3+ hours/day": 3}
    time_score = time_map.get(time_available, 2)

    for niche_key, niche_data in THEME_PAGE_NICHES.items():
        match_score = 0

        # Check if any interest matches niche keywords
        for interest in interests:
            if interest.lower() in niche_key or niche_key in interest.lower():
                match_score += 30

        # Difficulty preference
        diff = difficulty_map.get(niche_data.get("difficulty", ""), 1)
        if risk_tolerance == "low" and diff >= 2:
            match_score += 15
        elif risk_tolerance == "medium" and diff >= 1:
            match_score += 10
        else:
            match_score += 5

        # Time compatibility
        comp_score = diff * time_score
        match_score += comp_score * 2

        scored.append({
            "niche": niche_key,
            "description": niche_data["description"],
            "difficulty": niche_data["difficulty"],
            "competition": niche_data["competition_level"],
            "match_score": match_score,
            "time_to_1k": niche_data["estimated_time_to_1k"],
        })

    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return scored[:5]
