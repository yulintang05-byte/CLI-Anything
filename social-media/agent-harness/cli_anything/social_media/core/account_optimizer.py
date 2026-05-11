"""Account optimization engine.

Analyzes account profiles and trend data to generate concrete
optimization recommendations for YouTube and TikTok accounts.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


# ── Account data model ────────────────────────────────────────────────

@dataclass
class AccountProfile:
    platform: str          # 'youtube' | 'tiktok' | 'instagram'
    username: str
    display_name: str
    bio: str
    follower_count: int
    following_count: int
    post_count: int
    avg_views: int
    avg_likes: int
    avg_comments: int
    niche: str
    posting_frequency: str  # e.g., 'daily', '3x/week', 'weekly'
    content_types: list[str]  # e.g., ['shorts', 'tutorials', 'vlogs']
    current_hashtags: list[str]
    profile_url: str
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def engagement_rate(self) -> float:
        if self.avg_views == 0:
            return 0.0
        return round((self.avg_likes + self.avg_comments) / self.avg_views * 100, 4)


@dataclass
class OptimizationScore:
    overall: int            # 0-100
    profile_completeness: int
    content_strategy: int
    hashtag_quality: int
    posting_consistency: int
    engagement_health: int
    growth_trajectory: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class OptimizationReport:
    generated_at: str
    account: AccountProfile
    score: OptimizationScore
    critical_fixes: list[str]       # Must-do items blocking growth
    quick_wins: list[str]           # Easy improvements with big impact
    strategic_recommendations: list[str]  # Medium-term strategic moves
    hashtag_overhaul: dict          # {remove: [], add: [], priority: []}
    bio_rewrite: str                # Suggested bio
    content_calendar: list[dict]    # Suggested posting schedule
    competitor_gap_analysis: list[str]
    monetization_opportunities: list[str]

    def to_dict(self) -> dict:
        return {
            "generated_at": self.generated_at,
            "account": self.account.to_dict(),
            "score": self.score.to_dict(),
            "critical_fixes": self.critical_fixes,
            "quick_wins": self.quick_wins,
            "strategic_recommendations": self.strategic_recommendations,
            "hashtag_overhaul": self.hashtag_overhaul,
            "bio_rewrite": self.bio_rewrite,
            "content_calendar": self.content_calendar,
            "competitor_gap_analysis": self.competitor_gap_analysis,
            "monetization_opportunities": self.monetization_opportunities,
        }


# ── Account storage (local JSON registry) ────────────────────────────

_ACCOUNTS_DIR = Path.home() / ".cli-anything-social-media"
_ACCOUNTS_FILE = _ACCOUNTS_DIR / "accounts.json"


def _load_accounts() -> dict[str, dict]:
    if not _ACCOUNTS_FILE.exists():
        return {}
    try:
        return json.loads(_ACCOUNTS_FILE.read_text())
    except Exception:
        return {}


def _save_accounts(accounts: dict[str, dict]) -> None:
    _ACCOUNTS_DIR.mkdir(parents=True, exist_ok=True)
    _ACCOUNTS_FILE.write_text(json.dumps(accounts, indent=2))


def register_account(profile: AccountProfile) -> None:
    """Save an account profile to local registry."""
    accounts = _load_accounts()
    key = f"{profile.platform}:{profile.username.lower()}"
    accounts[key] = profile.to_dict()
    _save_accounts(accounts)


def get_account(platform: str, username: str) -> Optional[AccountProfile]:
    """Load an account profile from local registry."""
    accounts = _load_accounts()
    key = f"{platform.lower()}:{username.lower()}"
    data = accounts.get(key)
    if not data:
        return None
    return AccountProfile(**data)


def list_accounts() -> list[AccountProfile]:
    """List all registered accounts."""
    accounts = _load_accounts()
    result = []
    for data in accounts.values():
        try:
            result.append(AccountProfile(**data))
        except Exception:
            continue
    return result


def remove_account(platform: str, username: str) -> bool:
    """Remove an account from local registry."""
    accounts = _load_accounts()
    key = f"{platform.lower()}:{username.lower()}"
    if key in accounts:
        del accounts[key]
        _save_accounts(accounts)
        return True
    return False


# ── Scoring engine ────────────────────────────────────────────────────

_PLATFORM_BENCHMARKS = {
    "youtube": {
        "good_engagement": 3.0,       # percent
        "great_engagement": 6.0,
        "ideal_posting_freq": 3,      # per week
        "min_bio_len": 100,
        "ideal_hashtags": (3, 8),
    },
    "tiktok": {
        "good_engagement": 5.0,
        "great_engagement": 12.0,
        "ideal_posting_freq": 7,      # per week (daily)
        "min_bio_len": 80,
        "ideal_hashtags": (4, 9),
    },
    "instagram": {
        "good_engagement": 2.0,
        "great_engagement": 5.0,
        "ideal_posting_freq": 5,      # per week
        "min_bio_len": 80,
        "ideal_hashtags": (5, 15),
    },
}

_DEFAULT_BENCHMARKS = _PLATFORM_BENCHMARKS["tiktok"]


def _score_profile_completeness(account: AccountProfile) -> int:
    score = 0
    if account.display_name and account.display_name != account.username:
        score += 20
    if len(account.bio) >= _PLATFORM_BENCHMARKS.get(
            account.platform, _DEFAULT_BENCHMARKS).get("min_bio_len", 80):
        score += 25
    if account.niche:
        score += 20
    if account.content_types:
        score += 20
    if account.profile_url:
        score += 15
    return min(score, 100)


def _score_hashtag_quality(account: AccountProfile) -> int:
    benchmarks = _PLATFORM_BENCHMARKS.get(account.platform, _DEFAULT_BENCHMARKS)
    ideal_min, ideal_max = benchmarks["ideal_hashtags"]
    count = len(account.current_hashtags)
    if count == 0:
        return 10
    if ideal_min <= count <= ideal_max:
        return 90
    if count < ideal_min:
        return max(30, 90 - (ideal_min - count) * 10)
    return max(40, 90 - (count - ideal_max) * 5)


def _score_posting_consistency(account: AccountProfile) -> int:
    freq = account.posting_frequency.lower()
    platform = account.platform.lower()

    if "daily" in freq or "every day" in freq or "7x" in freq:
        return 95 if platform == "tiktok" else 85
    if "3x" in freq or "three" in freq:
        return 90 if platform == "youtube" else 75
    if "2x" in freq or "twice" in freq:
        return 75
    if "weekly" in freq or "1x" in freq:
        return 50
    if "bi" in freq or "2 week" in freq:
        return 25
    return 40  # unknown


def _score_engagement_health(account: AccountProfile) -> int:
    benchmarks = _PLATFORM_BENCHMARKS.get(account.platform, _DEFAULT_BENCHMARKS)
    eng = account.engagement_rate()
    good = benchmarks["good_engagement"]
    great = benchmarks["great_engagement"]
    if eng >= great:
        return 95
    if eng >= good:
        return 75
    if eng >= good * 0.5:
        return 55
    if eng > 0:
        return 35
    return 10


def _compute_score(account: AccountProfile) -> OptimizationScore:
    completeness = _score_profile_completeness(account)
    hashtag = _score_hashtag_quality(account)
    consistency = _score_posting_consistency(account)
    engagement = _score_engagement_health(account)
    content = 70 if account.content_types else 30
    growth = min(90, max(20, int(account.follower_count / 10000 * 10 + 40)))

    overall = int(
        completeness * 0.20
        + content * 0.15
        + hashtag * 0.15
        + consistency * 0.20
        + engagement * 0.20
        + growth * 0.10
    )

    return OptimizationScore(
        overall=min(overall, 100),
        profile_completeness=completeness,
        content_strategy=content,
        hashtag_quality=hashtag,
        posting_consistency=consistency,
        engagement_health=engagement,
        growth_trajectory=growth,
    )


# ── Recommendation engine ─────────────────────────────────────────────

def _critical_fixes(account: AccountProfile, score: OptimizationScore) -> list[str]:
    fixes = []

    if score.profile_completeness < 50:
        fixes.append(
            "PROFILE: Fill out every bio field — incomplete profiles lose 40-60% of profile visitors"
        )

    if score.engagement_health < 40:
        fixes.append(
            "ENGAGEMENT: Your engagement rate is below platform average — "
            "stop posting and focus on replying to ALL comments on existing videos for 7 days"
        )

    if score.posting_consistency < 30:
        fixes.append(
            "CONSISTENCY: Irregular posting signals low quality to the algorithm — "
            "commit to a fixed schedule even if less frequent"
        )

    if score.hashtag_quality < 40:
        fixes.append(
            "HASHTAGS: Your current hashtag strategy is broken — "
            "see 'hashtag_overhaul' for a replacement set"
        )

    if account.follower_count > 1000 and account.avg_views < account.follower_count * 0.05:
        fixes.append(
            "SHADOW-ISSUE: Views far below follower count — "
            "check for shadow restrictions, clear browser cookies, "
            "avoid banned hashtags, wait 24h between posts"
        )

    return fixes


def _quick_wins(account: AccountProfile) -> list[str]:
    wins = []

    # Bio CTA
    if "link" not in account.bio.lower() and "follow" not in account.bio.lower():
        niche_or_content = account.niche or "content"
        wins.append(
            "BIO CTA: Add a clear call-to-action to your bio — "
            f"'Follow for daily {niche_or_content}' or a link to your lead magnet"
        )

    # Pinned post
    wins.append(
        "PIN YOUR BEST VIDEO: Pin your highest-performing video — "
        "new profile visitors see it first, boosting follow conversion"
    )

    # Reply to comments
    wins.append(
        "REPLY LOOP: Reply to every comment within the first hour of posting — "
        "early engagement signals boost algorithmic distribution by 2-3x"
    )

    # Cover/thumbnail consistency
    wins.append(
        "VISUAL BRAND: Use identical thumbnail/cover style for every post — "
        "consistent color palette + font builds instant recognizability"
    )

    # Posting time
    wins.append(
        "BEST TIMES: Post at 7am, 12pm, or 7pm in your primary audience timezone — "
        "these windows catch morning commute, lunch break, and evening scroll sessions"
    )

    return wins


def _strategic_recs(account: AccountProfile) -> list[str]:
    recs = []

    # Series content
    recs.append(
        "CONTENT SERIES: Create a recurring series (e.g., 'Monday Motivation', '#TipTuesday') — "
        "serialized content builds return viewers and habit loops"
    )

    # Collab strategy
    recs.append(
        "COLLABORATION: Partner with 3-5 accounts in your niche with 10-50% more followers — "
        "cross-promotions are the fastest organic growth lever"
    )

    # Repurposing
    recs.append(
        "REPURPOSE: Convert every TikTok to a YouTube Short and every YouTube Short to an Instagram Reel — "
        "3x distribution, 1x production effort"
    )

    # Trending audio
    recs.append(
        "TRENDING AUDIO: Use audio from the 'Trending' sounds section within 48h of it appearing — "
        "early adopters of trending sounds get 3-5x more impressions"
    )

    # Community building
    recs.append(
        "COMMUNITY: Go Live at least 1x/week — live sessions push your profile to followers "
        "who haven't seen your content recently, re-engaging dormant followers"
    )

    # Platform-specific
    if account.platform == "youtube":
        recs.append(
            "CHAPTERS: Add timestamps/chapters to every video — "
            "increases average view duration by 15-25% and improves SEO indexing"
        )
        recs.append(
            "SHORTS FUNNEL: Post YouTube Shorts that tease your long-form content — "
            "Shorts subscribers convert to long-form viewers at ~12% rate"
        )
    elif account.platform == "tiktok":
        recs.append(
            "STITCH STRATEGY: Stitch a viral video in your niche weekly — "
            "borrowing a viral video's momentum gives your response video early algorithmic lift"
        )
        recs.append(
            "SERIES PLAYLIST: Create a 'series' of 3-5 related videos and link them in captions — "
            "binge-watching boosts your 'watch time' score in TikTok's algorithm"
        )

    return recs


def _build_hashtag_overhaul(
    account: AccountProfile,
    trending_tags: Optional[list[str]] = None,
) -> dict:
    """Build a hashtag replacement strategy."""
    niche = account.niche.lower() if account.niche else "content"
    platform = account.platform.lower()

    # Determine tier sizes based on platform
    if platform == "tiktok":
        # Small niche (50k-500k), Medium (500k-5M), Broad (5M+)
        structure = "3 niche + 3 mid-range + 1 broad"
    elif platform == "youtube":
        structure = "2 niche + 2 mid-range + 1 broad"
    else:  # instagram
        structure = "5 niche + 5 mid-range + 3 broad"

    # Generate niche-specific suggestions
    niche_suggestions = {
        "fitness": ["gymlife", "fitnessmotivation", "workoutdaily", "fitfam", "bodybuilding"],
        "finance": ["personalfinance", "moneyhabits", "financialliteracy", "investing101", "wealthmindset"],
        "food": ["foodie", "homecooking", "easyrecipes", "mealprep", "foodlover"],
        "beauty": ["beautytips", "skincareroutine", "makeuptutorial", "glowup", "selfcare"],
        "travel": ["travelblogger", "wanderlust", "travelgram", "adventuretime", "traveladdict"],
        "fashion": ["ootd", "fashionstyle", "streetwear", "styleinspo", "fashionblogger"],
        "education": ["learnontiktok", "didyouknow", "funfacts", "knowledgebomb", "edutok"],
        "comedy": ["funny", "humor", "comedyskits", "relatable", "lol"],
    }

    suggested_tags = niche_suggestions.get(niche, [f"{niche}tips", f"{niche}life", niche])
    if trending_tags:
        suggested_tags = trending_tags[:5] + suggested_tags

    return {
        "remove": account.current_hashtags,
        "add_niche": [f"#{t}" for t in suggested_tags[:5]],
        "add_trending": trending_tags[:3] if trending_tags else [],
        "add_broad": [f"#{niche}", f"#{niche}content", "viral", "fyp", "trending"],
        "structure": structure,
        "instructions": (
            f"Use this structure for every post on {platform}: "
            f"{structure}. Rotate hashtags every 3-5 posts to avoid pattern detection."
        ),
    }


def _build_content_calendar(account: AccountProfile) -> list[dict]:
    """Generate a 7-day content calendar template."""
    niche = account.niche or "your niche"
    platform = account.platform

    calendar = [
        {
            "day": "Monday",
            "theme": "Motivation/Inspiration",
            "format": "15-30s clip" if platform == "tiktok" else "YouTube Short",
            "hook": f"'Start your week with this {niche} tip...'",
            "hashtags": ["mondaymotivation", f"{niche}tips", "weeklygoals"],
        },
        {
            "day": "Tuesday",
            "theme": "Tutorial/How-To",
            "format": "60s video" if platform == "tiktok" else "5-10 min video",
            "hook": f"'The easiest way to [solve {niche} problem] in 60 seconds'",
            "hashtags": ["tutorial", f"howto{niche}", "learnontiktok"],
        },
        {
            "day": "Wednesday",
            "theme": "Behind the Scenes / Relatable",
            "format": "30-60s casual",
            "hook": "'POV: You're trying to [relatable scenario]...'",
            "hashtags": ["behindthescenes", "reallife", f"{niche}life"],
        },
        {
            "day": "Thursday",
            "theme": "Trending Sound / Duet / Stitch",
            "format": "15-30s trending format",
            "hook": "Hop on the #1 trending sound in your niche",
            "hashtags": ["trending", "viral", f"{niche}"],
        },
        {
            "day": "Friday",
            "theme": "Value Bomb / Knowledge Drop",
            "format": "60s educational",
            "hook": f"'3 things every {niche} creator gets wrong...'",
            "hashtags": ["didyouknow", f"{niche}facts", "valuebomb"],
        },
        {
            "day": "Saturday",
            "theme": "Community / Poll / Question",
            "format": "Any format",
            "hook": "'Comment your answer: [controversial or fun question]'",
            "hashtags": ["community", "questionoftheday", f"{niche}fam"],
        },
        {
            "day": "Sunday",
            "theme": "Top Performer Repost / Throwback",
            "format": "Re-share best performing video from the week",
            "hook": "Repost your best performing content from this week",
            "hashtags": ["throwback", "fanfavorite", f"best{niche}"],
        },
    ]
    return calendar


def _monetization_opportunities(account: AccountProfile) -> list[str]:
    """Identify monetization paths based on account size and niche."""
    follower_count = account.follower_count
    niche = account.niche.lower() if account.niche else ""
    opportunities = []

    # Tier-based monetization
    if follower_count >= 10_000:
        opportunities.append(
            "BRAND DEALS: You qualify for micro-influencer sponsorships — "
            "reach out to 10 brands in your niche with your media kit (avg views, engagement rate)"
        )
    if follower_count >= 1_000:
        opportunities.append(
            "AFFILIATE MARKETING: Join Amazon Associates, Impact, or ShareASale — "
            "add affiliate links to bio and mention products naturally in content"
        )
    if follower_count >= 500:
        opportunities.append(
            "DIGITAL PRODUCTS: Create a $7-$27 digital guide, template, or mini-course in your niche — "
            "direct traffic from bio link via Stan Store or Gumroad"
        )
    if account.platform == "youtube" and follower_count >= 1_000:
        opportunities.append(
            "YOUTUBE PARTNER PROGRAM: You may qualify for YPP (1,000 subs + 4,000 watch hours) — "
            "enable ads for passive income"
        )
    if account.platform == "tiktok" and follower_count >= 10_000:
        opportunities.append(
            "TIKTOK CREATOR FUND / CREATIVITY PROGRAM: Apply for the Creativity Program (18+, 10K followers) — "
            "pays per 1,000 qualified views (avg $0.02-$0.08/view)"
        )

    # Niche-specific
    niche_paths = {
        "fitness": "Sell custom workout plans ($15-$97) via direct message or Patreon",
        "finance": "Promote financial products (credit cards, brokerages) — high affiliate commissions ($50-$200/signup)",
        "food": "Partner with meal kit services (HelloFresh, EveryPlate) for CPA deals",
        "beauty": "Join Sephora Affiliates, e.l.f. Beauty creator program, or Ulta affiliate",
        "travel": "Promote hotel booking platforms (Booking.com, Hotels.com) — 4-8% commission per booking",
        "education": "Launch a paid community (Skool, Discord) or online course (Teachable, Kajabi)",
    }
    if niche in niche_paths:
        opportunities.append(f"NICHE SPECIFIC: {niche_paths[niche]}")

    # Universal
    opportunities.append(
        "SHOUTOUTS/PROMOS: Sell shoutouts to smaller accounts in your niche ($10-$500/post "
        "depending on your audience size) via DM or a public rate card"
    )

    return opportunities


# ── Public API ────────────────────────────────────────────────────────

def optimize_account(
    account: AccountProfile,
    trending_tags: Optional[list[str]] = None,
) -> OptimizationReport:
    """Generate a full optimization report for an account.

    Args:
        account: The account profile to analyze.
        trending_tags: Optional list of trending hashtags to incorporate.

    Returns:
        OptimizationReport with scored analysis and recommendations.
    """
    score = _compute_score(account)
    critical = _critical_fixes(account, score)
    wins = _quick_wins(account)
    strategic = _strategic_recs(account)
    hashtag_plan = _build_hashtag_overhaul(account, trending_tags)
    calendar = _build_content_calendar(account)
    monetization = _monetization_opportunities(account)

    # Bio rewrite
    niche = account.niche or "lifestyle"
    bio_rewrite = (
        f"📍 {niche.title()} content | "
        f"{'Tips & tutorials' if 'education' in niche.lower() else 'Daily inspiration'} | "
        f"Follow for {niche} content every {'day' if 'tiktok' in account.platform else 'week'} "
        f"⬇️ Free [lead magnet] in bio"
    )

    # Competitor gap
    competitor_gap = [
        f"Search top 5 accounts in #{niche} — study their hooks, caption length, and hashtag patterns",
        "Identify their top 3 performing posts (by views) and reverse-engineer the format",
        "Find gaps in their content (topics they haven't covered) — those are your content opportunities",
        "Note when they post — avoid posting at the exact same time as larger competitors",
    ]

    return OptimizationReport(
        generated_at=datetime.utcnow().isoformat() + "Z",
        account=account,
        score=score,
        critical_fixes=critical,
        quick_wins=wins,
        strategic_recommendations=strategic,
        hashtag_overhaul=hashtag_plan,
        bio_rewrite=bio_rewrite,
        content_calendar=calendar,
        competitor_gap_analysis=competitor_gap,
        monetization_opportunities=monetization,
    )


def optimize_all_accounts(
    trending_tags: Optional[list[str]] = None,
) -> list[OptimizationReport]:
    """Optimize all registered accounts.

    Args:
        trending_tags: Optional trending hashtags to incorporate into all reports.

    Returns:
        List of OptimizationReport, one per registered account.
    """
    accounts = list_accounts()
    if not accounts:
        return []
    return [optimize_account(acc, trending_tags) for acc in accounts]
