"""Theme page strategy guide and toolkit.

Theme pages (aka "repost pages", "niche curator accounts") are social media
accounts that aggregate and repost viral content around a specific niche.
They build large followings quickly and monetize via:
  - Shoutouts / paid promos
  - Affiliate marketing
  - Selling the account
  - Driving traffic to owned products

This module provides:
  - Niche selection scoring
  - Content sourcing strategy
  - Repost schedule automation
  - Monetization roadmap
  - Complete playbook per niche
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


# ── Data models ───────────────────────────────────────────────────────────────

@dataclass
class NicheScore:
    niche: str
    monetization_potential: int    # 1–10
    competition_level: str         # "low", "medium", "high"
    content_availability: int      # 1–10 (how easy to source viral content)
    audience_size: str             # "niche", "medium", "mass"
    recommended_platforms: List[str]
    estimated_months_to_10k: int
    verdict: str

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ContentSource:
    platform: str
    method: str
    query: str
    repost_permission: str  # "credit only", "ask first", "public domain", "original"
    notes: str

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class MonetizationTier:
    follower_threshold: str
    monthly_revenue_range: str
    methods: List[str]
    action_steps: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ThemePagePlaybook:
    niche: str
    platform: str
    username_formula: str
    bio_template: str
    posting_frequency: str
    content_sources: List[ContentSource]
    hashtag_strategy: str
    monetization_path: List[MonetizationTier]
    common_mistakes: List[str]
    success_examples: List[str]
    week1_checklist: List[str]

    def to_dict(self) -> Dict:
        return {
            "niche": self.niche,
            "platform": self.platform,
            "username_formula": self.username_formula,
            "bio_template": self.bio_template,
            "posting_frequency": self.posting_frequency,
            "content_sources": [s.to_dict() for s in self.content_sources],
            "hashtag_strategy": self.hashtag_strategy,
            "monetization_path": [m.to_dict() for m in self.monetization_path],
            "common_mistakes": self.common_mistakes,
            "success_examples": self.success_examples,
            "week1_checklist": self.week1_checklist,
        }


# ── Niche scoring database ────────────────────────────────────────────────────

NICHE_SCORES: Dict[str, NicheScore] = {
    "motivation": NicheScore(
        niche="motivation",
        monetization_potential=8,
        competition_level="high",
        content_availability=10,
        audience_size="mass",
        recommended_platforms=["tiktok", "instagram", "youtube"],
        estimated_months_to_10k=2,
        verdict="Best for beginners. Endless viral content to repost. Hard to stand out — pick a sub-niche (e.g., stoicism, discipline, sports motivation).",
    ),
    "fitness": NicheScore(
        niche="fitness",
        monetization_potential=9,
        competition_level="high",
        content_availability=9,
        audience_size="mass",
        recommended_platforms=["tiktok", "instagram"],
        estimated_months_to_10k=3,
        verdict="High CPM + affiliate potential (supplements, programs). Sub-niche into calisthenics, women's fitness, or sport-specific.",
    ),
    "luxury": NicheScore(
        niche="luxury",
        monetization_potential=9,
        competition_level="medium",
        content_availability=7,
        audience_size="medium",
        recommended_platforms=["tiktok", "instagram"],
        estimated_months_to_10k=3,
        verdict="High-spending audience. Monetize with luxury brand partnerships, real estate affiliates. Use lifestyle + aspirational content.",
    ),
    "cars": NicheScore(
        niche="cars",
        monetization_potential=9,
        competition_level="medium",
        content_availability=8,
        audience_size="medium",
        recommended_platforms=["tiktok", "youtube"],
        estimated_months_to_10k=4,
        verdict="High male demographic, excellent CPM. Sub-niche: supercars, tuner culture, budget builds, or specific brands.",
    ),
    "food": NicheScore(
        niche="food",
        monetization_potential=7,
        competition_level="high",
        content_availability=10,
        audience_size="mass",
        recommended_platforms=["tiktok", "instagram"],
        estimated_months_to_10k=2,
        verdict="Easiest content to source. Monetize with affiliate programs (meal kits, kitchen tools). Low barrier to entry.",
    ),
    "crypto": NicheScore(
        niche="crypto",
        monetization_potential=10,
        competition_level="high",
        content_availability=7,
        audience_size="niche",
        recommended_platforms=["tiktok", "youtube"],
        estimated_months_to_10k=4,
        verdict="Highest CPM on YouTube. Volatile niche — grows in bull markets. Requires trust; controversial to repost without expertise.",
    ),
    "relationships": NicheScore(
        niche="relationships",
        monetization_potential=7,
        competition_level="medium",
        content_availability=8,
        audience_size="mass",
        recommended_platforms=["tiktok", "instagram"],
        estimated_months_to_10k=3,
        verdict="High shareability — content gets saved and shared. Monetize with dating apps, courses, books. Female-skewed audience.",
    ),
    "entrepreneurship": NicheScore(
        niche="entrepreneurship",
        monetization_potential=10,
        competition_level="medium",
        content_availability=8,
        audience_size="medium",
        recommended_platforms=["tiktok", "instagram", "youtube"],
        estimated_months_to_10k=4,
        verdict="Highest affiliate commissions (courses, SaaS tools). Audience willing to spend. Credibility matters — curate carefully.",
    ),
    "animals": NicheScore(
        niche="animals",
        monetization_potential=5,
        competition_level="low",
        content_availability=10,
        audience_size="mass",
        recommended_platforms=["tiktok", "instagram"],
        estimated_months_to_10k=1,
        verdict="Easiest to grow — cute content always works. Low CPM. Best for account flipping or pet product affiliates.",
    ),
    "fashion": NicheScore(
        niche="fashion",
        monetization_potential=8,
        competition_level="high",
        content_availability=8,
        audience_size="medium",
        recommended_platforms=["tiktok", "instagram"],
        estimated_months_to_10k=3,
        verdict="Strong affiliate potential (SHEIN, Amazon fashion, LTK). Sub-niche by style (streetwear, luxury, thrift, y2k).",
    ),
    "sports": NicheScore(
        niche="sports",
        monetization_potential=8,
        competition_level="medium",
        content_availability=7,
        audience_size="mass",
        recommended_platforms=["tiktok", "youtube"],
        estimated_months_to_10k=3,
        verdict="Strong audience loyalty. Sub-niche by sport for faster growth. Monetize with betting affiliates, gear, highlights clips.",
    ),
    "travel": NicheScore(
        niche="travel",
        monetization_potential=8,
        competition_level="medium",
        content_availability=8,
        audience_size="medium",
        recommended_platforms=["tiktok", "instagram", "youtube"],
        estimated_months_to_10k=4,
        verdict="High affiliate rates (hotels, booking, credit cards). Aspirational content = high save rate. Best paired with original content.",
    ),
}

# ── Monetization tiers ────────────────────────────────────────────────────────

MONETIZATION_TIERS = [
    MonetizationTier(
        follower_threshold="0–1K",
        monthly_revenue_range="$0",
        methods=["None yet — focus 100% on growth"],
        action_steps=[
            "Post 3–5x daily (TikTok) or 1–2x/day (Instagram)",
            "Repost viral content with credit to original creator",
            "Engage with similar accounts (comment, follow)",
            "Study your analytics — double down on what gets views",
        ],
    ),
    MonetizationTier(
        follower_threshold="1K–10K",
        monthly_revenue_range="$50–$300",
        methods=[
            "Affiliate links in bio (Amazon, ClickBank, ShareASale)",
            "Shoutout4Shoutout (S4S) with similar accounts",
        ],
        action_steps=[
            "Sign up for 2–3 affiliate programs in your niche",
            "Add affiliate link to Linktree/Beacons in bio",
            "Add a CTA to bio: 'Link in bio for [niche] resources'",
            "Reach out to 5 accounts similar in size for S4S",
        ],
    ),
    MonetizationTier(
        follower_threshold="10K–50K",
        monthly_revenue_range="$200–$1,500",
        methods=[
            "Paid shoutouts ($20–$200 per post)",
            "Affiliate marketing (higher conversion)",
            "TikTok Creator Fund or Series (TikTok)",
            "YouTube Shorts monetization (YouTube)",
        ],
        action_steps=[
            "Set shoutout prices: ~$1 per 100 followers as baseline",
            "Create a media kit (screenshot analytics, niche, audience demo)",
            "DM smaller brands in your niche with your media kit",
            "Post shoutout availability in bio or story highlights",
        ],
    ),
    MonetizationTier(
        follower_threshold="50K–200K",
        monthly_revenue_range="$1,000–$5,000",
        methods=[
            "Brand deals ($500–$5,000 per post)",
            "Digital product sales (eBooks, presets, templates)",
            "Subscription (exclusive content via Patreon, TikTok LIVE gifts)",
            "Account sale ($2K–$20K)",
        ],
        action_steps=[
            "Join influencer platforms: Creator.co, AspireIQ, Grin",
            "Launch a simple digital product using your niche expertise",
            "Negotiate 3-month brand ambassador deals (better rates)",
            "If not monetizing well, consider selling — 50K accounts sell for $2K–$10K",
        ],
    ),
    MonetizationTier(
        follower_threshold="200K+",
        monthly_revenue_range="$5,000–$50,000+",
        methods=[
            "Premium brand deals ($5K–$50K per campaign)",
            "Own product lines (merchandise, courses, apps)",
            "Agency model (manage other theme pages)",
            "Account portfolio (build + sell multiple pages)",
        ],
        action_steps=[
            "Hire a manager or join a talent agency",
            "Launch signature course or product in your niche",
            "Build a portfolio of 3–5 theme pages in different niches",
            "Consider converting to a media company",
        ],
    ),
]

# ── Playbook generator ────────────────────────────────────────────────────────

_BIO_TEMPLATES = {
    "motivation": "Daily {niche} 🔥 | Fueling your grind | New drops every day ⬇️",
    "fitness":    "Your daily fitness inspo 💪 | Workouts · Nutrition · Mindset | Link ⬇️",
    "food":       "Viral recipes & food inspo 🍕 | New daily | Save for later ⬇️",
    "luxury":     "Luxury lifestyle & inspiration ✨ | Daily posts | Dream big ⬇️",
    "cars":       "Cars that make you look twice 🚗💨 | Daily drops | Link ⬇️",
    "crypto":     "Crypto education & alpha 📈 | DYOR · NFA | Updates daily ⬇️",
    "fashion":    "Your daily style inspo 👗 | Trends · Fits · Deals | Shop ⬇️",
    "animals":    "Daily animal cuteness 🐾 | Guaranteed to make you smile | Follow ⬇️",
    "travel":     "The world is calling ✈️ | Daily travel inspo | Plan your trip ⬇️",
    "entrepreneurship": "Building empires one idea at a time 💼 | Business · Money · Growth ⬇️",
}

_DEFAULT_SOURCES = [
    ContentSource(
        platform="tiktok",
        method="Search trending hashtag + duet/stitch",
        query='#[niche] sort:popular',
        repost_permission="credit only",
        notes="Always tag @originalcreator. Many creators appreciate the exposure.",
    ),
    ContentSource(
        platform="youtube",
        method="Download top shorts + repost to TikTok/Reels with credit",
        query="[niche] shorts site:youtube.com",
        repost_permission="ask first",
        notes="Use yt-dlp to download. DM creator for permission if < 100K subscribers.",
    ),
    ContentSource(
        platform="reddit",
        method="Download top posts from niche subreddits",
        query="subreddit:[niche] top:week",
        repost_permission="credit only",
        notes="Most Reddit content is free to repost with credit. Check post license.",
    ),
    ContentSource(
        platform="twitter_x",
        method="Repost viral tweets as screenshots",
        query="#[niche] filter:videos min_faves:1000",
        repost_permission="credit only",
        notes="Screenshot + credit @handle. Very low friction for motivation/quote content.",
    ),
]


def get_playbook(niche: str, platform: str = "tiktok") -> ThemePagePlaybook:
    """Generate a complete theme page playbook for a niche + platform.

    Args:
        niche: Content niche (e.g., motivation, fitness, food, cars)
        platform: Target platform (tiktok, instagram, youtube)

    Returns:
        ThemePagePlaybook with everything needed to start today.
    """
    niche_lower = niche.lower()
    bio = _BIO_TEMPLATES.get(niche_lower, f"Daily {niche} content | Follow for more ⬇️")

    if platform == "tiktok":
        freq = "3–5 posts per day (consistency > quality for theme pages)"
        hashtag_strat = "Use 15–20 hashtags: mix mega (3), large (5), medium (5), niche (4). Add #fyp and #viral always."
    elif platform == "youtube":
        freq = "1–2 Shorts per day + 1 long-form per week"
        hashtag_strat = "Use 8–12 hashtags in description. Include 1 keyword hashtag as first tag (#motivationshorts, etc.)"
    else:  # instagram
        freq = "2–3 Reels/day + 4–6 Stories/day"
        hashtag_strat = "30 hashtags per post: 10 large, 10 medium, 10 niche. Rotate sets to avoid shadowban."

    sources = []
    for s in _DEFAULT_SOURCES:
        sources.append(ContentSource(
            platform=s.platform,
            method=s.method,
            query=s.query.replace("[niche]", niche_lower),
            repost_permission=s.repost_permission,
            notes=s.notes,
        ))

    username_formula = (
        f"[adjective]{niche_lower} | daily{niche_lower} | {niche_lower}empire | "
        f"the{niche_lower}page | {niche_lower}central"
    )

    common_mistakes = [
        "Reposting without crediting the original creator (ruins trust + risks reports)",
        "Posting inconsistently — 1 post/day is better than 10 posts then nothing",
        "Ignoring analytics — double down on what works, kill what doesn't",
        "Switching niches too early — stick with it for at least 90 days",
        "Not engaging with comments — reply to every comment in your first 1K followers",
        "Using the same 30 hashtags on every post (Instagram shadowban risk)",
        "Building an audience before having a monetization plan",
    ]

    success_examples = [
        "@millionaire_mentor (motivation) — 4.2M TikTok followers, $15K+/month shoutouts",
        "@luxurylifestyle (luxury) — 8M+ combined, monetizes via high-ticket brand deals",
        "Gymshark-era fitness pages — built brand partnerships from 0→100K in 6 months",
        "Anonymous food pages on Instagram regularly sell for $10K–$100K at 100K followers",
    ]

    week1_checklist = [
        f"[ ] Create new {platform} account with niche username",
        f"[ ] Write bio: \"{bio}\"",
        "[ ] Create or commission a profile avatar (Canva — free)",
        f"[ ] Follow 50 accounts in the {niche} niche to calibrate algorithm",
        "[ ] Set up Linktree or Beacons with affiliate links",
        f"[ ] Source 15 pieces of viral {niche} content (TikTok, Reddit, YouTube)",
        "[ ] Post first 3 videos/posts TODAY",
        "[ ] Engage: comment on 20 posts in your niche",
        "[ ] Schedule next 7 days of content using your posting schedule",
        "[ ] Join 2–3 Facebook groups or Discord servers for {niche} creators",
    ]

    return ThemePagePlaybook(
        niche=niche,
        platform=platform,
        username_formula=username_formula,
        bio_template=bio,
        posting_frequency=freq,
        content_sources=sources,
        hashtag_strategy=hashtag_strat,
        monetization_path=MONETIZATION_TIERS,
        common_mistakes=common_mistakes,
        success_examples=success_examples,
        week1_checklist=week1_checklist,
    )


def score_niches(niches: Optional[List[str]] = None) -> List[NicheScore]:
    """Score and rank niches by opportunity.

    Args:
        niches: List of niches to score. If None, scores all known niches.

    Returns:
        List of NicheScore sorted by composite score (monetization × availability).
    """
    targets = niches or list(NICHE_SCORES.keys())
    results = []

    for niche in targets:
        if niche in NICHE_SCORES:
            results.append(NICHE_SCORES[niche])
        else:
            results.append(NicheScore(
                niche=niche,
                monetization_potential=5,
                competition_level="unknown",
                content_availability=5,
                audience_size="unknown",
                recommended_platforms=["tiktok", "instagram"],
                estimated_months_to_10k=6,
                verdict="Unknown niche — research manually before committing.",
            ))

    results.sort(
        key=lambda n: n.monetization_potential * n.content_availability,
        reverse=True,
    )
    return results


def get_conversion_guide() -> Dict:
    """Return a complete guide on converting a theme page into a business.

    Returns:
        Dict with phased conversion strategy.
    """
    return {
        "title": "How to Convert a Theme Page Into a Real Business",
        "phases": [
            {
                "phase": "1 — Build the Asset (0–10K followers)",
                "goal": "Establish credibility and algorithm trust",
                "actions": [
                    "Post consistently in ONE niche — no topic drift",
                    "Study viral content patterns: hook style, format, pacing",
                    "Engage with every comment to boost early posts",
                    "Don't monetize yet — pure growth focus",
                ],
                "kpis": ["Follower growth rate", "Average views per post", "Follower-to-view ratio"],
            },
            {
                "phase": "2 — Monetize Early Wins (10K–50K followers)",
                "goal": "Start generating revenue while continuing to grow",
                "actions": [
                    "Add affiliate links for 2–3 products your audience would buy",
                    "Offer shoutout packages ($50–$200 per post)",
                    "Collect emails via a free lead magnet (checklist, guide)",
                    "Start building a secondary platform (don't rely on one)",
                ],
                "kpis": ["Monthly revenue", "Email list size", "Affiliate click-through rate"],
            },
            {
                "phase": "3 — Convert to Brand (50K–200K followers)",
                "goal": "Transform from curator to brand with owned products",
                "actions": [
                    "Launch a digital product (eBook, course, template pack) — $27–$97",
                    "Negotiate 3-month brand ambassador deals (better ROI than one-offs)",
                    "Introduce your face/voice gradually if anonymous — builds trust",
                    "Build a content team: editor, graphic designer, VA",
                ],
                "kpis": ["Product revenue %", "Email open rate", "Brand deal value"],
            },
            {
                "phase": "4 — Scale or Exit (200K+ followers)",
                "goal": "Build a media company or sell for maximum value",
                "actions": [
                    "Launch premium membership or subscription ($9–$49/month)",
                    "Build a portfolio of 3–5 pages in adjacent niches",
                    "Document SOPs so the account runs without you (sellable asset)",
                    "List account on Flippa, Empire Flippers, or Acquire.com",
                ],
                "kpis": ["Monthly recurring revenue", "Page valuation multiple", "Number of managed accounts"],
            },
        ],
        "valuation_multiples": {
            "tiktok":    "10K followers ≈ $200–$500 | 100K ≈ $2K–$10K | 1M ≈ $20K–$100K",
            "instagram": "10K followers ≈ $500–$2K  | 100K ≈ $5K–$25K | 1M ≈ $50K–$200K",
            "youtube":   "Based on monthly revenue × 24–36x multiple",
        },
        "key_success_factors": [
            "Niche consistency — never post off-topic content",
            "Posting volume — more posts = more chances to go viral",
            "Hook quality — first 1–3 seconds determine if content spreads",
            "Algorithm timing — post when your audience is most active",
            "Engagement loops — reply, duet, stitch to boost distribution",
            "Cross-platform presence — build on 2–3 platforms simultaneously",
        ],
    }
