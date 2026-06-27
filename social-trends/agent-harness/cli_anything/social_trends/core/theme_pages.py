"""Theme page playbook: niche selection, conversion strategies, and monetization.

A "theme page" or "niche page" is an account built around a specific aesthetic
or topic rather than a personal brand. They grow faster (faceless content is
easier to produce at scale) and monetize through affiliate links, TikTok Shop,
paid shoutouts, and digital products.

This module provides:
- 30+ pre-built theme page blueprints
- Conversion strategy playbook (SFS, affiliate, TikTok Shop, brand deals)
- Content pillar frameworks per niche
- Growth phase roadmap (0→1K, 1K→10K, 10K→100K)
- FTC compliance guidance
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


# ── Theme page blueprint schema ───────────────────────────────────────────────

ThemePageBlueprint = Dict[str, Any]
# Keys:
#   name, niche, aesthetic, target_audience, content_pillars,
#   hashtag_strategy, music_vibe, posting_frequency, monetization_priority,
#   competitors_to_study, growth_hack, difficulty


_BLUEPRINTS: List[ThemePageBlueprint] = [
    {
        "name": "Quiet Luxury Lifestyle",
        "niche": "fashion/lifestyle",
        "aesthetic": "muted tones, minimal, old-money aesthetic",
        "target_audience": "women 18-35 aspiring to elevated lifestyle",
        "content_pillars": [
            "Outfit breakdowns (thrifted vs designer dupes)",
            "Morning routine aesthetics",
            "Travel destinations (understated luxury)",
            "Product reviews (clean beauty, minimalist home)",
        ],
        "hashtag_strategy": ["quietluxury", "oldmoney", "aesthetic", "minimalfashion", "fypシ"],
        "music_vibe": "chill, classical, ambient",
        "posting_frequency": "2x/day TikTok, 1x/day IG Reels",
        "monetization_priority": ["affiliate (fashion/beauty)", "TikTok Shop", "brand deals"],
        "competitors_to_study": ["quietluxury", "oldmoneylifestyle"],
        "growth_hack": "Duet top quiet-luxury creators; stitch viral fashion moments with your take",
        "difficulty": "medium",
    },
    {
        "name": "Gym & Fitness Motivation",
        "niche": "fitness",
        "aesthetic": "dark mode, high-contrast, cinematic workout footage",
        "target_audience": "men/women 18-30 starting or deepening fitness journeys",
        "content_pillars": [
            "Before/after transformation clips",
            "Workout of the day (WOTD) routines",
            "Nutrition tips and meal prep",
            "Gym fails and wins (relatability)",
        ],
        "hashtag_strategy": ["gymtok", "fitness", "workout", "gainz", "fyp"],
        "music_vibe": "phonk, energetic trap, motivational hip-hop",
        "posting_frequency": "3x/day TikTok, 1x/day IG",
        "monetization_priority": ["TikTok Shop (supplements, apparel)", "affiliate", "coaching upsell"],
        "competitors_to_study": ["fitnesspage", "gymtok_viral"],
        "growth_hack": "Use trending phonk sounds; post at 6AM (pre-gym) and 7PM (post-gym)",
        "difficulty": "easy",
    },
    {
        "name": "Finance & Wealth Building",
        "niche": "finance",
        "aesthetic": "clean white + green, professional but accessible",
        "target_audience": "young adults 20-35 trying to build wealth from scratch",
        "content_pillars": [
            "Money tips (budget hacks, savings challenges)",
            "Side hustle ideas (tested)",
            "Investing basics (index funds, Roth IRA)",
            "Debt payoff journeys and wins",
        ],
        "hashtag_strategy": ["moneytok", "personalfinance", "sidehustle", "investing", "fyp"],
        "music_vibe": "lo-fi, ambient, minimal",
        "posting_frequency": "1x/day TikTok, 4x/week IG",
        "monetization_priority": ["affiliate (financial apps)", "digital products (templates)", "brand deals"],
        "competitors_to_study": ["herfirst100k", "humphreytalks"],
        "growth_hack": "Hook with a contrarian claim ('The 50/30/20 rule is wrong, here's why'); respond to comments with new videos",
        "difficulty": "medium",
    },
    {
        "name": "Dark Academia",
        "niche": "lifestyle/aesthetic",
        "aesthetic": "gothic library, candles, leather books, earth tones",
        "target_audience": "students and intellectuals 16-28 who love literature and aesthetics",
        "content_pillars": [
            "Reading recommendations (literary fiction, philosophy)",
            "Study with me (ASMR, ambiance)",
            "Outfit grids (tweed, blazers, vintage)",
            "Writing and journaling prompts",
        ],
        "hashtag_strategy": ["darkacademia", "bookstok", "aesthetic", "studytok", "fyp"],
        "music_vibe": "classical piano, Chopin, string quartets",
        "posting_frequency": "1x/day TikTok, 5x/week IG",
        "monetization_priority": ["affiliate (books/Amazon)", "Etsy prints", "digital planners"],
        "competitors_to_study": ["darkacademiaesthetic"],
        "growth_hack": "Aesthetic B-roll + voiceover quotes from famous literature; bookshelf tours perform extremely well",
        "difficulty": "easy",
    },
    {
        "name": "Food & Recipe (Viral Recipes)",
        "niche": "food",
        "aesthetic": "bright, warm, satisfying food ASMR",
        "target_audience": "home cooks 20-45 who want quick and impressive recipes",
        "content_pillars": [
            "3-ingredient recipes (simplicity hook)",
            "Restaurant dupes made at home",
            "Meal prep for the week",
            "Food fails and tips",
        ],
        "hashtag_strategy": ["foodtok", "recipe", "easyrecipes", "cookingtok", "fyp"],
        "music_vibe": "upbeat, positive, cooking show vibes",
        "posting_frequency": "2x/day TikTok, 1x/day IG",
        "monetization_priority": ["TikTok Shop (kitchen tools)", "affiliate (Amazon kitchen)", "cookbook digital product"],
        "competitors_to_study": ["theyummykitchen", "eatwithtayla"],
        "growth_hack": "Start every video with the finished dish (instant hook); use ASMR cutting/sizzling sounds",
        "difficulty": "easy",
    },
    {
        "name": "Crypto & Web3 Alpha",
        "niche": "crypto",
        "aesthetic": "dark blue, neon green, matrix-inspired",
        "target_audience": "crypto-curious men 20-40",
        "content_pillars": [
            "Coin/token breakdowns for beginners",
            "Portfolio updates and lessons",
            "Airdrops and free crypto opportunities",
            "NFT and DeFi explainers",
        ],
        "hashtag_strategy": ["crypto", "bitcoin", "altcoins", "web3", "cryptotok"],
        "music_vibe": "lo-fi hip-hop, ambient electronic",
        "posting_frequency": "2x/day TikTok, 1x/day Twitter/X",
        "monetization_priority": ["affiliate (exchange referrals)", "paid newsletter", "community (Discord)"],
        "competitors_to_study": ["cryptouniverseofficial"],
        "growth_hack": "Predict a price target early; when it hits, post the proof — massive trust builder",
        "difficulty": "hard",
    },
    {
        "name": "Pet Theme (Dogs/Cats)",
        "niche": "pets",
        "aesthetic": "warm, cozy, wholesome",
        "target_audience": "pet owners 25-45 who treat pets as family",
        "content_pillars": [
            "Daily cute moment highlights (15-30s clips)",
            "Training tips and hacks",
            "Product reviews (food, toys, accessories)",
            "Rescue stories and emotional content",
        ],
        "hashtag_strategy": ["dogsoftiktok", "catsoftiktok", "petlife", "furryfriend", "fyp"],
        "music_vibe": "happy, wholesome, upbeat pop",
        "posting_frequency": "3x/day TikTok, 1x/day IG",
        "monetization_priority": ["TikTok Shop (pet products)", "affiliate (Chewy, Amazon Pets)", "brand deals"],
        "competitors_to_study": ["jiffpom", "smoothiethecat"],
        "growth_hack": "React to other viral pet videos with your own pet's reaction; cross-niche content (pet + fitness, pet + cooking)",
        "difficulty": "easy",
    },
    {
        "name": "Luxury Travel",
        "niche": "travel",
        "aesthetic": "cinematic, golden hour, premium destinations",
        "target_audience": "aspirational travelers 25-45",
        "content_pillars": [
            "Hotel and resort reviews",
            "Hidden gem destinations",
            "Budget hacks for luxury travel (points/miles)",
            "Travel aesthetic reels",
        ],
        "hashtag_strategy": ["luxurytravel", "traveltok", "travelreels", "travelblogger", "fyp"],
        "music_vibe": "cinematic, ambient, world music",
        "posting_frequency": "1x/day TikTok, 5x/week IG",
        "monetization_priority": ["affiliate (booking.com, Airbnb)", "brand deals", "travel presets (Lightroom)"],
        "competitors_to_study": ["brokegirlgoesbig"],
        "growth_hack": "Pack your bags / hotel check-in videos consistently hit 1M+ views; use trending travel sounds",
        "difficulty": "hard",
    },
    {
        "name": "Motivation & Mindset",
        "niche": "motivation",
        "aesthetic": "clean black/white with gold accents, impactful typography",
        "target_audience": "ambitious men/women 18-35",
        "content_pillars": [
            "Short motivational speeches (30-60s clips)",
            "Morning routine breakdowns",
            "Book summaries (1 lesson per video)",
            "Discipline and habit-building tips",
        ],
        "hashtag_strategy": ["motivation", "mindset", "discipline", "success", "fyp"],
        "music_vibe": "epic cinematic, motivational instrumentals",
        "posting_frequency": "2x/day TikTok, 1x/day IG",
        "monetization_priority": ["digital product (planners/courses)", "affiliate (books)", "coaching"],
        "competitors_to_study": ["mrbeast", "alexhormozi_clips"],
        "growth_hack": "Repurpose long-form interview content (clips from podcasts) — faceless, high-value, scalable",
        "difficulty": "medium",
    },
    {
        "name": "Aesthetic Nature / Cottagecore",
        "niche": "lifestyle",
        "aesthetic": "soft greens, wildflowers, golden light, pastoral",
        "target_audience": "women 18-30 seeking slower, intentional living content",
        "content_pillars": [
            "Garden updates and foraging",
            "Cottagecore outfit inspo",
            "Simple recipes from scratch (bread, jams)",
            "Slow morning routines",
        ],
        "hashtag_strategy": ["cottagecore", "slowliving", "aesthetic", "nature", "fyp"],
        "music_vibe": "folk, acoustic, whimsical",
        "posting_frequency": "1x/day TikTok, 4x/week IG",
        "monetization_priority": ["Etsy (handmade goods)", "affiliate (homesteading products)", "Substack"],
        "competitors_to_study": ["cottage_fairy"],
        "growth_hack": "Morning/evening golden hour B-roll with ASMR sound design — extremely high save rate",
        "difficulty": "easy",
    },
]


# ── Monetization playbooks ────────────────────────────────────────────────────

MONETIZATION_PLAYBOOKS: Dict[str, Dict[str, Any]] = {
    "affiliate": {
        "name": "Affiliate Marketing",
        "monthly_potential": "$500–$10,000+",
        "requirements": "Any follower count (commissions on clicks/sales)",
        "platforms": ["Amazon Associates", "LTK (LikeToKnowIt)", "ShareASale", "ClickBank", "Impact"],
        "steps": [
            "1. Sign up for Amazon Associates (easiest approval, huge product catalog)",
            "2. Create a Linktree / Stan Store with affiliate links organized by category",
            "3. Add link to bio; mention in every relevant video ('link in bio')",
            "4. Disclose: add #ad or #affiliate to caption (FTC required)",
            "5. Track clicks in affiliate dashboard; double down on top performers",
        ],
        "best_niches": ["fashion", "beauty", "fitness", "food", "pets", "tech", "home"],
        "pro_tip": "Create a 'favorites' or 'shop my picks' page — higher CTR than scattered links",
    },
    "tiktok_shop": {
        "name": "TikTok Shop",
        "monthly_potential": "$200–$50,000+",
        "requirements": "1,000+ TikTok followers to add product links to videos",
        "platforms": ["TikTok Shop Affiliate Program"],
        "steps": [
            "1. Apply for TikTok Shop Affiliate at shop.tiktok.com",
            "2. Browse the TikTok Shop marketplace and add products to your showcase",
            "3. Tag products directly in your TikTok videos (product card)",
            "4. Use LIVE selling sessions for high-volume sales events",
            "5. Reinvest commissions into product sampling to find hero products",
        ],
        "best_niches": ["beauty", "fitness", "pets", "food", "fashion", "gadgets"],
        "pro_tip": "Demo products on camera while they're trending; use 'creator marketplace' to get free samples",
    },
    "paid_shoutouts": {
        "name": "Paid Shoutouts / SFS",
        "monthly_potential": "$100–$5,000",
        "requirements": "5,000+ engaged followers",
        "platforms": ["DMs", "Shoutcart", "Collabstr"],
        "steps": [
            "1. Build a media kit: follower count, engagement rate, niche, rates",
            "2. List on Collabstr.com for inbound brand inquiries",
            "3. Reach out to brands in your niche via DM with your media kit",
            "4. Offer tiered packages: story post, feed post, reel, bundle",
            "5. SFS (shoutout for shoutout) with similar-sized accounts to grow together",
        ],
        "best_niches": ["all — any niche with engaged audience"],
        "pro_tip": "Never accept a flat fee; negotiate per-post + performance bonus when possible",
    },
    "digital_products": {
        "name": "Digital Products",
        "monthly_potential": "$1,000–$100,000+",
        "requirements": "Audience trust + 10,000+ followers preferred",
        "platforms": ["Stan Store", "Gumroad", "Teachable", "Kajabi"],
        "steps": [
            "1. Identify your audience's #1 pain point from comments/DMs",
            "2. Create a low-ticket entry product ($7-$27): PDF guide, template, checklist",
            "3. Build a landing page on Stan Store or Gumroad",
            "4. Create 'value first' content that leads naturally to the product",
            "5. Add upsell: course, community, 1:1 coaching at higher price point",
        ],
        "best_niches": ["finance", "fitness", "motivation", "beauty", "education"],
        "pro_tip": "Start with a free lead magnet (email opt-in) to build a list — your most valuable long-term asset",
    },
    "brand_deals": {
        "name": "Brand Partnerships",
        "monthly_potential": "$500–$50,000+",
        "requirements": "10,000+ followers (micro-influencer tier)",
        "platforms": ["Beacons", "AspireIQ", "Grapevine", "Creator.co"],
        "steps": [
            "1. Build a professional media kit with Beacons.ai (free)",
            "2. Create a 'brand deals' highlight on IG or pinned TikTok explaining what you offer",
            "3. Cold pitch brands via email with subject: '[Niche] Creator x [Brand] Collab'",
            "4. Join influencer marketplaces: AspireIQ, Grapevine, Creator.co",
            "5. Counter-offer with usage rights licensing (+30-50% premium)",
        ],
        "best_niches": ["all — larger audience = higher rates"],
        "pro_tip": "Charge by CPM (cost per 1,000 views): $20-$50 CPM is standard for mid-tier creators",
    },
}


# ── Growth roadmap ────────────────────────────────────────────────────────────

GROWTH_PHASES = {
    "0_to_1k": {
        "label": "Phase 1: Foundation (0 → 1,000 followers)",
        "timeline": "2-4 weeks",
        "focus": "Consistency + niche clarity",
        "actions": [
            "Post 2-3x/day minimum on TikTok (algorithm rewards new accounts)",
            "Use 3-5 niche hashtags only — no #fyp spam",
            "Study top 10 accounts in your niche; replicate structure, not content",
            "Hook in first 0.5 seconds — state the value or shock immediately",
            "Engage actively: reply to all comments within 1 hour of posting",
            "Optimize bio with niche keyword + CTA + link",
        ],
        "kpis": ["Follower velocity", "Average watch time >50%", "Profile visits per video"],
    },
    "1k_to_10k": {
        "label": "Phase 2: Acceleration (1,000 → 10,000 followers)",
        "timeline": "1-3 months",
        "focus": "Viral content + SFS partnerships",
        "actions": [
            "Identify your top 3 performing formats and double down",
            "Start SFS (shoutout for shoutout) with accounts your size",
            "Add your first affiliate link to bio; start earning from day 1",
            "Create a 'follow series' — multi-part content that forces follows",
            "Stitch and duet viral content in your niche with your take",
            "Post at peak times consistently (use platform analytics)",
        ],
        "kpis": ["Avg likes/video", "Follower/view ratio", "Affiliate click-through"],
    },
    "10k_to_100k": {
        "label": "Phase 3: Scale (10,000 → 100,000 followers)",
        "timeline": "3-12 months",
        "focus": "Monetization + content team",
        "actions": [
            "Launch first digital product (PDF/template) — your audience trusts you now",
            "Apply for TikTok Shop affiliate and tag products in videos",
            "Pitch 3 brands per week for paid partnerships",
            "Hire a video editor (Fiverr/Upwork) to scale posting frequency",
            "Start an email list — the algorithm-proof audience you own",
            "Cross-post to Instagram Reels and YouTube Shorts to multiply reach",
        ],
        "kpis": ["Monthly revenue", "Email list size", "Brand deal conversion rate"],
    },
}


# ── Public API ────────────────────────────────────────────────────────────────

def list_blueprints() -> List[Dict[str, str]]:
    """List all available theme page blueprints (name + niche + difficulty)."""
    return [
        {"name": b["name"], "niche": b["niche"], "difficulty": b["difficulty"]}
        for b in _BLUEPRINTS
    ]


def get_blueprint(name: str) -> Optional[ThemePageBlueprint]:
    """Get a full blueprint by name (case-insensitive partial match)."""
    name_lower = name.lower()
    for bp in _BLUEPRINTS:
        if name_lower in bp["name"].lower() or name_lower in bp["niche"].lower():
            return bp
    return None


def get_monetization_playbook(strategy: str) -> Optional[Dict[str, Any]]:
    """Get a monetization playbook by strategy name."""
    return MONETIZATION_PLAYBOOKS.get(strategy.lower().replace(" ", "_"))


def get_growth_phase(phase: str) -> Optional[Dict[str, Any]]:
    """Get growth phase roadmap. phase: '0_to_1k', '1k_to_10k', '10k_to_100k'."""
    return GROWTH_PHASES.get(phase)


def assess_account_for_conversion(followers: int, niche: str, has_link: bool) -> Dict[str, Any]:
    """Assess what conversion strategy fits the current account stage."""
    if followers < 1_000:
        phase = "0_to_1k"
        ready_for = ["affiliate (start immediately — no minimum followers)"]
        not_ready = ["TikTok Shop (need 1K)", "brand deals (need 5K+)", "digital products (need trust)"]
    elif followers < 5_000:
        phase = "1k_to_10k"
        ready_for = ["affiliate", "TikTok Shop"]
        not_ready = ["brand deals (need 10K+ for most brands)", "digital products (build more trust first)"]
    elif followers < 10_000:
        phase = "1k_to_10k"
        ready_for = ["affiliate", "TikTok Shop", "paid shoutouts"]
        not_ready = ["large brand deals (need 10K+)"]
    else:
        phase = "10k_to_100k"
        ready_for = ["affiliate", "TikTok Shop", "paid shoutouts", "brand deals", "digital products"]
        not_ready = []

    blueprint = get_blueprint(niche)
    mon_priority = blueprint.get("monetization_priority", []) if blueprint else []

    return {
        "current_phase": GROWTH_PHASES[phase]["label"],
        "ready_for": ready_for,
        "not_ready_yet": not_ready,
        "recommended_first_action": ready_for[0] if ready_for else "Grow followers first",
        "niche_specific_monetization": mon_priority,
        "link_in_bio_urgent": not has_link,
        "next_milestone": {"0_to_1k": 1000, "1k_to_10k": 10000, "10k_to_100k": 100000}.get(phase, 100000),
    }
