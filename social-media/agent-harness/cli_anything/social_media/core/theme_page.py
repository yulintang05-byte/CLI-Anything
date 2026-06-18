"""Theme page strategy engine — niche selection, content calendar, monetization roadmap.

A "theme page" is a niche social account that curates & reposts content around
a specific topic (e.g., @luxury.cars, @aesthetic.nature, @finance.gems) and
monetizes through shoutouts, affiliate links, and brand deals.

"Converting" = turning followers into revenue.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Any

# ── Niche database ────────────────────────────────────────────────────────────

@dataclass
class Niche:
    name: str
    category: str
    difficulty: str          # "easy" | "medium" | "hard"
    monetization_potential: str   # "low" | "medium" | "high" | "very_high"
    avg_cpm: float           # advertising CPM in USD
    affiliate_friendly: bool
    shoutout_rate_10k: int   # USD per shoutout at 10K followers
    shoutout_rate_100k: int  # USD per shoutout at 100K followers
    avg_growth_rate: float   # monthly % follower growth for active accounts
    content_lifespan: str    # "hours" | "days" | "weeks" | "evergreen"
    description: str
    sub_niches: list[str]
    competing_accounts: list[str]  # example accounts for inspiration


NICHES: list[Niche] = [
    Niche(
        name="personal finance",
        category="finance",
        difficulty="medium",
        monetization_potential="very_high",
        avg_cpm=18.0,
        affiliate_friendly=True,
        shoutout_rate_10k=150,
        shoutout_rate_100k=1200,
        avg_growth_rate=8.5,
        content_lifespan="evergreen",
        description="Money tips, investing, budgeting, wealth mindset.",
        sub_niches=["crypto", "stock market", "budgeting", "real estate investing", "side hustles", "FIRE movement"],
        competing_accounts=["@financialeducation", "@markiplierfinance", "@grahamstephan"],
    ),
    Niche(
        name="fitness",
        category="health",
        difficulty="medium",
        monetization_potential="high",
        avg_cpm=8.0,
        affiliate_friendly=True,
        shoutout_rate_10k=80,
        shoutout_rate_100k=700,
        avg_growth_rate=10.2,
        content_lifespan="evergreen",
        description="Workouts, nutrition, body transformation, motivation.",
        sub_niches=["home workouts", "powerlifting", "calisthenics", "yoga", "meal prep", "supplements"],
        competing_accounts=["@gymshark", "@cbumfitness", "@athleanx"],
    ),
    Niche(
        name="luxury lifestyle",
        category="aspirational",
        difficulty="easy",
        monetization_potential="very_high",
        avg_cpm=22.0,
        affiliate_friendly=True,
        shoutout_rate_10k=200,
        shoutout_rate_100k=1800,
        avg_growth_rate=14.0,
        content_lifespan="days",
        description="Luxury cars, watches, mansions, jets, yachts.",
        sub_niches=["luxury cars", "luxury watches", "luxury real estate", "private jets", "fashion"],
        competing_accounts=["@luxurylifestyle", "@millionairementor", "@luxurycarsworld"],
    ),
    Niche(
        name="motivation",
        category="mindset",
        difficulty="easy",
        monetization_potential="medium",
        avg_cpm=6.0,
        affiliate_friendly=True,
        shoutout_rate_10k=60,
        shoutout_rate_100k=500,
        avg_growth_rate=12.5,
        content_lifespan="days",
        description="Motivational quotes, success mindset, entrepreneurship.",
        sub_niches=["stoicism", "self-discipline", "morning routine", "productivity", "entrepreneur mindset"],
        competing_accounts=["@thinkgrowprosper", "@dailyquotes", "@success"],
    ),
    Niche(
        name="beauty",
        category="lifestyle",
        difficulty="hard",
        monetization_potential="high",
        avg_cpm=10.0,
        affiliate_friendly=True,
        shoutout_rate_10k=100,
        shoutout_rate_100k=900,
        avg_growth_rate=7.0,
        content_lifespan="weeks",
        description="Makeup tutorials, skincare, beauty tips, product reviews.",
        sub_niches=["skincare", "K-beauty", "clean beauty", "drugstore makeup", "natural beauty"],
        competing_accounts=["@nikkietutorials", "@jamescharles", "@hudabeauty"],
    ),
    Niche(
        name="travel",
        category="lifestyle",
        difficulty="medium",
        monetization_potential="high",
        avg_cpm=12.0,
        affiliate_friendly=True,
        shoutout_rate_10k=90,
        shoutout_rate_100k=800,
        avg_growth_rate=9.0,
        content_lifespan="weeks",
        description="Travel destinations, tips, guides, visual content.",
        sub_niches=["budget travel", "luxury travel", "solo travel", "van life", "digital nomad", "hidden gems"],
        competing_accounts=["@hecktic_travels", "@expertvagabond", "@nomadicmatt"],
    ),
    Niche(
        name="food",
        category="lifestyle",
        difficulty="easy",
        monetization_potential="medium",
        avg_cpm=7.0,
        affiliate_friendly=True,
        shoutout_rate_10k=70,
        shoutout_rate_100k=600,
        avg_growth_rate=11.0,
        content_lifespan="days",
        description="Recipes, restaurant reviews, food aesthetics, cooking tips.",
        sub_niches=["vegan", "keto", "meal prep", "baking", "street food", "restaurant reviews"],
        competing_accounts=["@chefsteps", "@tasty", "@bon_appetit"],
    ),
    Niche(
        name="pets",
        category="entertainment",
        difficulty="easy",
        monetization_potential="medium",
        avg_cpm=5.0,
        affiliate_friendly=True,
        shoutout_rate_10k=50,
        shoutout_rate_100k=400,
        avg_growth_rate=15.0,
        content_lifespan="days",
        description="Cute animals, pet care tips, funny pet videos.",
        sub_niches=["dogs", "cats", "exotic pets", "pet training", "rescue stories"],
        competing_accounts=["@thedodo", "@dogsofinstagram", "@catsofinstagram"],
    ),
    Niche(
        name="tech",
        category="education",
        difficulty="hard",
        monetization_potential="very_high",
        avg_cpm=15.0,
        affiliate_friendly=True,
        shoutout_rate_10k=120,
        shoutout_rate_100k=1100,
        avg_growth_rate=6.0,
        content_lifespan="weeks",
        description="Gadgets, software reviews, AI tools, programming.",
        sub_niches=["AI tools", "smartphones", "productivity apps", "gaming gear", "smart home"],
        competing_accounts=["@mkbhd", "@linustechtips", "@unboxtherapy"],
    ),
    Niche(
        name="fashion",
        category="lifestyle",
        difficulty="medium",
        monetization_potential="high",
        avg_cpm=9.0,
        affiliate_friendly=True,
        shoutout_rate_10k=90,
        shoutout_rate_100k=800,
        avg_growth_rate=8.0,
        content_lifespan="days",
        description="Style inspiration, OOTD, fashion tips, outfit ideas.",
        sub_niches=["streetwear", "luxury fashion", "thrift/vintage", "minimalist", "sustainable fashion"],
        competing_accounts=["@zara", "@hypebeast", "@highsnobiety"],
    ),
    Niche(
        name="crypto / web3",
        category="finance",
        difficulty="hard",
        monetization_potential="very_high",
        avg_cpm=25.0,
        affiliate_friendly=True,
        shoutout_rate_10k=200,
        shoutout_rate_100k=2000,
        avg_growth_rate=20.0,
        content_lifespan="hours",
        description="Cryptocurrency, NFTs, DeFi, blockchain news.",
        sub_niches=["bitcoin", "altcoins", "NFT", "DeFi", "web3 startups"],
        competing_accounts=["@cryptowendyo", "@anthonypompliano", "@coinbureau"],
    ),
]

# Indexed by name for fast lookup
_NICHE_BY_NAME = {n.name: n for n in NICHES}


# ── Content pillars ───────────────────────────────────────────────────────────

_CONTENT_PILLARS: dict[str, list[dict]] = {
    "personal finance": [
        {"type": "education", "pct": 40, "examples": ["5 ways to save $500/month", "How I paid off $30K debt", "Investing 101"]},
        {"type": "inspiration", "pct": 25, "examples": ["Zero to $1M stories", "Financial freedom milestones", "Income milestones"]},
        {"type": "news", "pct": 15, "examples": ["Fed rate changes", "Stock market today", "New tax law breakdown"]},
        {"type": "tools", "pct": 15, "examples": ["Best budgeting apps", "My investment portfolio", "Credit card rewards hack"]},
        {"type": "community", "pct": 5, "examples": ["Financial fails", "Q&A sessions", "Polls: save or invest?"]},
    ],
    "fitness": [
        {"type": "workouts", "pct": 40, "examples": ["10-min ab workout", "Push day routine", "Beginner full body"]},
        {"type": "nutrition", "pct": 25, "examples": ["Meal prep Sunday", "High protein meals", "Pre-workout meals"]},
        {"type": "transformation", "pct": 20, "examples": ["Before/after", "12-week progress", "Body recomp tips"]},
        {"type": "education", "pct": 10, "examples": ["How muscles grow", "Sleep and recovery", "Supplement science"]},
        {"type": "motivation", "pct": 5, "examples": ["Gym fails", "Day in the life", "Q&A"]},
    ],
    "luxury lifestyle": [
        {"type": "aspirational", "pct": 50, "examples": ["$10M mansion tour", "Lamborghini review", "Bali resort"]},
        {"type": "tips", "pct": 20, "examples": ["How to book business class cheap", "Best credit cards for travel", "Entry-level luxury watches"]},
        {"type": "reviews", "pct": 20, "examples": ["Worth it?", "Honest review", "Unboxing"]},
        {"type": "motivation", "pct": 10, "examples": ["Road to wealth", "Success habits", "Mindset of the rich"]},
    ],
    "default": [
        {"type": "education", "pct": 30, "examples": ["How-to guides", "Tips & tricks", "Tutorials"]},
        {"type": "inspiration", "pct": 25, "examples": ["Success stories", "Transformation", "Before/after"]},
        {"type": "entertainment", "pct": 25, "examples": ["Trending content", "Challenges", "Reactions"]},
        {"type": "promotion", "pct": 10, "examples": ["Product features", "Reviews", "Affiliate content"]},
        {"type": "community", "pct": 10, "examples": ["Q&A", "Polls", "Giveaways"]},
    ],
}


# ── Content calendar ──────────────────────────────────────────────────────────

def generate_content_calendar(
    niche: str,
    days: int = 30,
    posts_per_day: dict[str, int] | None = None,
    start_date: datetime | None = None,
) -> list[dict]:
    """Generate a day-by-day content posting calendar."""
    if posts_per_day is None:
        posts_per_day = {"tiktok": 3, "instagram": 1, "youtube": 1}

    pillars = _CONTENT_PILLARS.get(niche, _CONTENT_PILLARS["default"])
    start = start_date or datetime.now()
    calendar = []

    for day in range(days):
        date = start + timedelta(days=day)
        day_posts = []
        day_name = date.strftime("%A")

        for platform, count in posts_per_day.items():
            for _ in range(count):
                # Rotate through pillars based on percentage weighting
                pillar = _weighted_pillar(pillars, day, platform)
                day_posts.append({
                    "platform": platform,
                    "content_type": pillar["type"],
                    "example": pillar["examples"][day % len(pillar["examples"])],
                    "posting_time": _best_time(platform, day_name),
                    "hashtag_count": 25 if platform == "instagram" else 5 if platform == "youtube" else 3,
                    "trending_audio": platform == "tiktok",
                })

        calendar.append({
            "date": date.strftime("%Y-%m-%d"),
            "day": day_name,
            "posts": day_posts,
        })

    return calendar


def _weighted_pillar(pillars: list[dict], day: int, platform: str) -> dict:
    """Select a content pillar based on weighted percentages."""
    import random
    random.seed(day * 17 + hash(platform) % 100)
    weights = [p["pct"] for p in pillars]
    total = sum(weights)
    r = random.uniform(0, total)
    cum = 0
    for pillar, weight in zip(pillars, weights):
        cum += weight
        if r <= cum:
            return pillar
    return pillars[-1]


def _best_time(platform: str, day_name: str) -> str:
    """Return the best posting time for platform + day combo."""
    times: dict[str, dict[str, str]] = {
        "tiktok": {
            "Monday": "6:00 AM", "Tuesday": "2:00 AM", "Wednesday": "7:00 AM",
            "Thursday": "9:00 AM", "Friday": "5:00 AM", "Saturday": "11:00 AM",
            "Sunday": "7:00 AM",
        },
        "instagram": {
            "Monday": "11:00 AM", "Tuesday": "8:00 AM", "Wednesday": "11:00 AM",
            "Thursday": "11:00 AM", "Friday": "10:00 AM", "Saturday": "10:00 AM",
            "Sunday": "7:00 AM",
        },
        "youtube": {
            "Monday": "2:00 PM", "Tuesday": "2:00 PM", "Wednesday": "2:00 PM",
            "Thursday": "12:00 PM", "Friday": "12:00 PM", "Saturday": "9:00 AM",
            "Sunday": "9:00 AM",
        },
    }
    return times.get(platform, {}).get(day_name, "12:00 PM")


# ── Monetization roadmap ──────────────────────────────────────────────────────

def monetization_roadmap(niche: str, follower_count: int) -> dict:
    """Return a monetization roadmap based on current follower count."""
    n = _NICHE_BY_NAME.get(niche)
    cpm = n.avg_cpm if n else 8.0
    shoutout_10k = n.shoutout_rate_10k if n else 60
    shoutout_100k = n.shoutout_rate_100k if n else 500
    is_affiliate = n.affiliate_friendly if n else True

    phases = []

    if follower_count < 1000:
        phases.append({
            "phase": "Foundation (0–1K)",
            "status": "current" if follower_count < 1000 else "completed",
            "focus": "Content quality, consistency, niche positioning",
            "actions": [
                "Post 3x/day on TikTok, 1x/day on Instagram",
                "Follow 50 accounts in your niche daily",
                "Engage with top 10 creators in your niche",
                "Build a content bank of 30+ posts",
                "A/B test different hooks and formats",
            ],
            "revenue_potential": "$0–$50/month",
            "timeline": "2–4 weeks",
        })

    if follower_count < 10000:
        phases.append({
            "phase": "Early Monetization (1K–10K)",
            "status": "current" if 1000 <= follower_count < 10000 else ("upcoming" if follower_count < 1000 else "completed"),
            "focus": "Engagement rate, shoutout-for-shoutout (SFS), early affiliate",
            "actions": [
                "Apply for affiliate programs (Amazon, niche-specific)",
                "Add link-in-bio (Linktree/Stan.store)",
                "Start SFS with accounts in same niche",
                "Sell shoutouts ($10–$50 per post)",
                "Launch a digital product (eBook, preset, guide) for $7–$27",
                f"Estimated CPM earnings: ${cpm:.0f}/1K views on YouTube",
            ],
            "revenue_potential": f"${shoutout_10k // 4}–${shoutout_10k}/month",
            "timeline": "4–12 weeks",
        })

    if follower_count < 100000:
        phases.append({
            "phase": "Scaling (10K–100K)",
            "status": "current" if 10000 <= follower_count < 100000 else ("upcoming" if follower_count < 10000 else "completed"),
            "focus": "Paid shoutouts, high-ticket affiliate, brand deals",
            "actions": [
                f"Charge ${shoutout_10k}–${shoutout_10k * 3} per shoutout post",
                "Reach out to 10 brands/week for paid partnerships",
                "Promote high-commission affiliates (finance, software, fitness = $30–$150/sale)",
                "Build an email list for off-platform monetization",
                "Create a paid community (Patreon/Discord) at $5–$15/month",
                "License your content to brands",
            ],
            "revenue_potential": f"${shoutout_100k // 4}–${shoutout_100k}/month",
            "timeline": "3–6 months from 10K",
        })

    if follower_count >= 100000:
        phases.append({
            "phase": "Established Creator (100K+)",
            "status": "current",
            "focus": "Premium brand deals, course sales, own product line",
            "actions": [
                f"Charge ${shoutout_100k}–${shoutout_100k * 5} per brand deal",
                "Launch a premium course/membership at $97–$497",
                "Create your own product line (merch, supplements, software)",
                "Hire a VA/team to manage posting and DMs",
                "Diversify to YouTube for long-form + AdSense revenue",
                "Explore speaking engagements and consulting",
            ],
            "revenue_potential": f"${shoutout_100k}–${shoutout_100k * 20}/month",
            "timeline": "Ongoing",
        })

    return {
        "niche": niche,
        "follower_count": follower_count,
        "phases": phases,
        "affiliate_programs": _affiliate_programs(niche),
        "brand_outreach_template": _brand_outreach_template(niche, follower_count),
    }


def _affiliate_programs(niche: str) -> list[dict]:
    programs: dict[str, list[dict]] = {
        "personal finance": [
            {"name": "Robinhood", "commission": "$5–$10/signup", "cookie": "30 days"},
            {"name": "Coinbase", "commission": "$10/signup", "cookie": "30 days"},
            {"name": "Personal Capital", "commission": "$100+/lead", "cookie": "30 days"},
            {"name": "Credit Karma", "commission": "$1–$3/signup", "cookie": "45 days"},
            {"name": "Acorns", "commission": "$5/signup", "cookie": "30 days"},
        ],
        "fitness": [
            {"name": "MyProtein", "commission": "8% per sale", "cookie": "30 days"},
            {"name": "Gymshark", "commission": "5–10%", "cookie": "30 days"},
            {"name": "Bodybuilding.com", "commission": "8%", "cookie": "30 days"},
            {"name": "Whoop", "commission": "$30/signup", "cookie": "30 days"},
        ],
        "tech": [
            {"name": "Amazon Associates", "commission": "3–10%", "cookie": "24 hours"},
            {"name": "Best Buy", "commission": "1–2%", "cookie": "1 day"},
            {"name": "Apple", "commission": "2–7%", "cookie": "24 hours"},
            {"name": "NordVPN", "commission": "30–40%", "cookie": "30 days"},
        ],
        "beauty": [
            {"name": "Sephora", "commission": "5–10%", "cookie": "30 days"},
            {"name": "Ulta Beauty", "commission": "5%", "cookie": "30 days"},
            {"name": "NARS Cosmetics", "commission": "5%", "cookie": "30 days"},
        ],
        "travel": [
            {"name": "Booking.com", "commission": "25–40% of commission", "cookie": "30 days"},
            {"name": "Airbnb", "commission": "$50–$75/booking", "cookie": "30 days"},
            {"name": "TripAdvisor", "commission": "50% of revenue", "cookie": "14 days"},
            {"name": "SafetyWing", "commission": "10%", "cookie": "30 days"},
        ],
        "default": [
            {"name": "Amazon Associates", "commission": "3–10%", "cookie": "24 hours"},
            {"name": "ShareASale", "commission": "varies", "cookie": "30 days"},
            {"name": "ClickBank", "commission": "up to 75%", "cookie": "60 days"},
            {"name": "Impact", "commission": "varies", "cookie": "30 days"},
        ],
    }
    return programs.get(niche, programs["default"])


def _brand_outreach_template(niche: str, followers: int) -> str:
    return f"""Subject: Partnership Opportunity — {niche.title()} Niche Creator

Hi [Brand Name] Team,

I'm a content creator in the {niche} space with {followers:,} engaged followers across TikTok and Instagram.

My audience demographic: [age range], [location], [interests matching your product].

I'd love to explore a paid partnership that authentically integrates your product into my content. My typical content gets [X]% engagement rate, which is above the {niche} niche average.

What I offer:
• Dedicated video/reel featuring your product
• 3–5 story mentions over 48 hours
• Link in bio for 30 days
• Usage rights for your marketing materials

Investment: $[YOUR_RATE] per post

Please find my media kit attached. I'm happy to jump on a quick call to discuss.

Best,
[Your Name]
[Link to your profile]"""


# ── Niche suggestions ─────────────────────────────────────────────────────────

def suggest_niches(
    interests: list[str],
    monetization_priority: bool = True,
    max_suggestions: int = 5,
) -> list[dict]:
    """Suggest niches based on user interests and goals."""
    scored: list[tuple[float, Niche]] = []

    for niche in NICHES:
        score = 0.0
        for interest in interests:
            interest_lower = interest.lower()
            if interest_lower in niche.name:
                score += 50
            elif interest_lower in niche.category:
                score += 30
            elif any(interest_lower in sub for sub in niche.sub_niches):
                score += 20

        if monetization_priority:
            mon_map = {"very_high": 40, "high": 30, "medium": 20, "low": 10}
            score += mon_map.get(niche.monetization_potential, 0)

        score += niche.avg_growth_rate * 0.5

        if interests:
            scored.append((score, niche))
        else:
            scored.append((niche.avg_growth_rate * 2 + mon_map.get(niche.monetization_potential, 0), niche))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [
        {
            "niche": n.name,
            "category": n.category,
            "difficulty": n.difficulty,
            "monetization": n.monetization_potential,
            "monthly_growth_rate": f"{n.avg_growth_rate:.1f}%",
            "shoutout_at_10k": f"${n.shoutout_rate_10k}",
            "shoutout_at_100k": f"${n.shoutout_rate_100k}",
            "sub_niches": n.sub_niches[:4],
            "match_score": round(s, 1),
        }
        for s, n in scored[:max_suggestions]
    ]


def theme_page_guide() -> dict:
    """Return the complete theme page creation & conversion guide."""
    return {
        "overview": (
            "A theme page is a niche social media account that aggregates and reposts "
            "content around a specific topic. Unlike personal brands, theme pages are "
            "anonymous, scalable, and can be sold for 24–36x monthly revenue."
        ),
        "phases": [
            {
                "phase": "1. Niche Selection (Week 1)",
                "actions": [
                    "Pick a niche with high CPM (finance, tech, business) OR high virality (pets, humor, luxury)",
                    "Validate: search the niche on TikTok — 100M+ views on top videos = demand exists",
                    "Choose a sub-niche for less competition (e.g., 'personal finance for Gen Z')",
                    "Register a memorable handle on all platforms simultaneously",
                ],
            },
            {
                "phase": "2. Account Setup (Week 1)",
                "actions": [
                    "Professional logo using Canva or hire on Fiverr ($5–$15)",
                    "Compelling bio: [niche emoji] [what you post] [CTA link]",
                    "Link in bio tool (Stan.store, Beacons.ai, or Linktree)",
                    "Set account to Business/Creator on all platforms",
                    "Cross-link all platforms from each other",
                ],
            },
            {
                "phase": "3. Content Strategy (Weeks 2–4)",
                "actions": [
                    "80% reposted content (always credit original creators)",
                    "20% original content (commentary, reaction, compilation, original takes)",
                    "Post 3x/day minimum on TikTok, 1x/day on Instagram, 1x/week on YouTube",
                    "Always use trending audio on TikTok within 48h of detection",
                    "Front-load hooks: first 3 seconds make or break retention",
                    "Add subtitles/captions — 85% watch without sound",
                ],
            },
            {
                "phase": "4. Growth Hacking (Month 2)",
                "actions": [
                    "SFS (Shoutout for Shoutout) with 5–10 accounts in your niche weekly",
                    "Engage with every comment in first 30 min after posting",
                    "Follow 50–100 targeted accounts daily (follow/unfollow if aggressive growth needed)",
                    "Stitch and duet viral videos in your niche",
                    "Comment on influencers' posts to get their followers",
                    "Run niche-specific hashtag challenges",
                ],
            },
            {
                "phase": "5. Converting Followers to Revenue (Month 3+)",
                "actions": [
                    "Start selling shoutouts at 1K followers ($10–$25/post)",
                    "Add affiliate links for products your niche loves (3–75% commission)",
                    "Build email list — offer a free resource (guide, checklist) in link bio",
                    "Create low-ticket digital product ($7–$27) — packaged knowledge of your niche",
                    "Pitch brands directly via DM/email when hitting milestones",
                    "Consider a paid community (Discord) at $5–$15/month",
                ],
            },
            {
                "phase": "6. Scaling & Selling (Month 6+)",
                "actions": [
                    "Hire a VA ($3–$8/hr) to handle posting and DMs",
                    "Replicate the model in adjacent niches",
                    "Pages with $1K+/month revenue can sell for $24K–$36K on Flippa/Empire Flippers",
                    "Document all SOPs before selling",
                ],
            },
        ],
        "content_sourcing": {
            "repost_sources": [
                "Reddit subreddits (r/niche for text/meme content)",
                "Pinterest for visual content",
                "YouTube channels (download + repost on TikTok)",
                "Twitter/X viral posts",
                "Other TikTok/Instagram accounts (always credit)",
            ],
            "tools": [
                "SnapTik / SSSTik — download TikTok videos without watermark",
                "4K Video Downloader — YouTube content",
                "Canva — create graphics/quotes",
                "CapCut — free video editing with trending templates",
                "InShot — quick mobile video editing",
            ],
            "legal_note": (
                "Always credit original creators. Most creators won't DMCA "
                "if you credit them and drive them traffic. "
                "For monetized accounts, create more original content (50%+)."
            ),
        },
        "monetization_methods": [
            {
                "method": "Paid Shoutouts",
                "difficulty": "easy",
                "income_potential": "$50–$5,000/month",
                "when": "1K+ followers",
                "how": "Brands and other creators pay you to post about them. Join ShoutCart or DM potential buyers.",
            },
            {
                "method": "Affiliate Marketing",
                "difficulty": "easy",
                "income_potential": "$100–$10,000/month",
                "when": "Any follower count (focus on quality over quantity)",
                "how": "Promote products with tracked links. Finance/software niches pay $30–$150/conversion.",
            },
            {
                "method": "Digital Products",
                "difficulty": "medium",
                "income_potential": "$200–$5,000/month",
                "when": "1K+ followers, engaged audience",
                "how": "Sell eBooks, presets, templates, courses, swipe files. Use Gumroad or Stan.store.",
            },
            {
                "method": "Brand Deals",
                "difficulty": "medium",
                "income_potential": "$500–$50,000+/month",
                "when": "10K+ followers",
                "how": "Direct outreach + join creator marketplaces (AspireIQ, Creator.co, Grapevine).",
            },
            {
                "method": "AdSense / TikTok Creator Fund",
                "difficulty": "easy",
                "income_potential": "$50–$2,000/month",
                "when": "YouTube: 1,000 subs + 4,000 watch hours. TikTok: 10K followers + 100K views/30 days",
                "how": "Enable monetization in platform settings.",
            },
            {
                "method": "Paid Community",
                "difficulty": "medium",
                "income_potential": "$200–$20,000/month",
                "when": "5K+ engaged followers",
                "how": "Discord/Patreon at $5–$15/month. Give exclusive content, live Q&As.",
            },
            {
                "method": "Selling the Page",
                "difficulty": "hard",
                "income_potential": "24–36x monthly revenue",
                "when": "Consistent $1K+/month revenue for 6+ months",
                "how": "List on Flippa, Empire Flippers, or broker directly. Verify revenue with screenshots.",
            },
        ],
        "conversion_checklist": [
            "Link in bio is set up (Stan.store recommended for creators)",
            "Lead magnet exists (free PDF, checklist, swipe file)",
            "Email list collecting (ConvertKit/Mailchimp free tier)",
            "At least one affiliate link active",
            "DMs open with auto-reply pointing to link in bio",
            "Analytics tracking engagement rate (target: >3%)",
            "Posting consistently for 30+ days",
        ],
    }
