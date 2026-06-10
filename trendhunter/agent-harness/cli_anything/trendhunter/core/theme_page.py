"""Theme page playbook — niche selection, conversion funnels, monetization, and growth strategy.

A "theme page" (or niche page) is an account built around a topic (not a personality)
that curates/creates content, grows an audience, and converts them to revenue via
affiliate links, shoutouts, newsletters, digital products, or brand deals.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# Niche selection matrix with monetization potential scores
_NICHE_MATRIX: dict[str, dict] = {
    "luxury_lifestyle": {
        "monetization_score": 9,
        "growth_speed":       "fast",
        "competition":        "high",
        "avg_cpm":            "$12-25",
        "best_platforms":     ["instagram", "tiktok"],
        "revenue_streams":    ["affiliate (luxury brands)", "shoutouts", "brand deals"],
        "starter_tip":        "Repost aspirational content, add value-add captions",
    },
    "finance_money": {
        "monetization_score": 10,
        "growth_speed":       "medium",
        "competition":        "medium",
        "avg_cpm":            "$15-40",
        "best_platforms":     ["youtube", "tiktok", "instagram"],
        "revenue_streams":    ["affiliate (brokers/cards)", "digital products", "newsletter"],
        "starter_tip":        "Money tips + stats posts perform extremely well",
    },
    "fitness_gym": {
        "monetization_score": 8,
        "growth_speed":       "fast",
        "competition":        "very_high",
        "avg_cpm":            "$8-18",
        "best_platforms":     ["tiktok", "instagram", "youtube"],
        "revenue_streams":    ["affiliate (supplements)", "programs", "shoutouts"],
        "starter_tip":        "Transformation content + specific workout clips drive fastest growth",
    },
    "beauty_skincare": {
        "monetization_score": 9,
        "growth_speed":       "fast",
        "competition":        "very_high",
        "avg_cpm":            "$10-20",
        "best_platforms":     ["tiktok", "instagram", "youtube"],
        "revenue_streams":    ["affiliate (Amazon, Sephora)", "brand deals", "UGC"],
        "starter_tip":        "Before/after content + product reviews have highest conversion",
    },
    "pets_animals": {
        "monetization_score": 7,
        "growth_speed":       "very_fast",
        "competition":        "medium",
        "avg_cpm":            "$6-14",
        "best_platforms":     ["tiktok", "instagram", "youtube"],
        "revenue_streams":    ["affiliate (pet products)", "merch", "shoutouts"],
        "starter_tip":        "Easiest virality — funny/cute clips almost always work",
    },
    "motivational_quotes": {
        "monetization_score": 6,
        "growth_speed":       "fast",
        "competition":        "very_high",
        "avg_cpm":            "$4-10",
        "best_platforms":     ["instagram", "tiktok"],
        "revenue_streams":    ["shoutouts", "digital products (ebooks)", "print-on-demand merch"],
        "starter_tip":        "Layer trending audio under quote videos for 3x more reach",
    },
    "travel_wanderlust": {
        "monetization_score": 8,
        "growth_speed":       "medium",
        "competition":        "high",
        "avg_cpm":            "$12-22",
        "best_platforms":     ["instagram", "tiktok", "youtube"],
        "revenue_streams":    ["affiliate (booking, hotels)", "presets", "brand trips"],
        "starter_tip":        "B-roll cinematic clips + destination caption format grows fast",
    },
    "tech_ai": {
        "monetization_score": 9,
        "growth_speed":       "fast",
        "competition":        "medium",
        "avg_cpm":            "$18-45",
        "best_platforms":     ["youtube", "tiktok", "twitter/x"],
        "revenue_streams":    ["affiliate (software/tools)", "sponsorships", "courses"],
        "starter_tip":        "AI tools tutorials are the fastest-growing niche right now (2025)",
    },
    "food_recipes": {
        "monetization_score": 7,
        "growth_speed":       "fast",
        "competition":        "very_high",
        "avg_cpm":            "$6-14",
        "best_platforms":     ["tiktok", "instagram", "youtube"],
        "revenue_streams":    ["affiliate (kitchen gear, groceries)", "cookbook", "Patreon"],
        "starter_tip":        "30-second recipe format dominates — no talking needed",
    },
    "fashion_streetwear": {
        "monetization_score": 8,
        "growth_speed":       "fast",
        "competition":        "high",
        "avg_cpm":            "$8-18",
        "best_platforms":     ["tiktok", "instagram"],
        "revenue_streams":    ["affiliate (ASOS, Shein, Amazon fashion)", "brand deals", "shoutouts"],
        "starter_tip":        "Haul content + outfit rating = best engagement combo",
    },
}


@dataclass
class ThemePage:
    niche: str
    platform: str = "tiktok"
    username: str = ""
    followers: int = 0
    link_in_bio_url: str = ""
    primary_cta: str = ""

    def to_dict(self) -> dict:
        return {
            "niche":              self.niche,
            "platform":          self.platform,
            "username":          self.username,
            "followers":         self.followers,
            "link_in_bio_url":   self.link_in_bio_url,
            "primary_cta":       self.primary_cta,
        }


@dataclass
class ConversionFunnel:
    stages: list[dict] = field(default_factory=list)
    cta_templates: list[str] = field(default_factory=list)
    link_in_bio_tools: list[dict] = field(default_factory=list)
    funnel_metrics: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "stages":            self.stages,
            "cta_templates":     self.cta_templates,
            "link_in_bio_tools": self.link_in_bio_tools,
            "funnel_metrics":    self.funnel_metrics,
        }


def get_niche_analysis(niche: str) -> dict:
    """Return monetization and growth analysis for a niche."""
    niche_lower = niche.lower().replace(" ", "_")

    # Try exact match first
    data = _NICHE_MATRIX.get(niche_lower)

    # Try partial match
    if not data:
        for key, val in _NICHE_MATRIX.items():
            if niche_lower in key or key in niche_lower:
                data = val
                break

    if not data:
        data = {
            "monetization_score": 6,
            "growth_speed":       "medium",
            "competition":        "medium",
            "avg_cpm":            "$8-15",
            "best_platforms":     ["tiktok", "instagram"],
            "revenue_streams":    ["affiliate", "shoutouts", "digital products"],
            "starter_tip":        "Find your unique angle in the niche to stand out",
        }

    return {"niche": niche, **data}


def get_conversion_funnel(niche: str = "", platform: str = "tiktok") -> ConversionFunnel:
    """Build a complete conversion funnel for a theme page."""
    funnel = ConversionFunnel()

    funnel.stages = [
        {
            "stage":       "1. Awareness — Scroll Stop",
            "goal":        "Get the viewer to stop scrolling",
            "tactics":     [
                "Hook in first 1-2 seconds (visual or text)",
                "Trending sound or audio",
                "Pattern interrupt (unexpected visual/edit)",
                "Bold text overlay with emotional hook",
            ],
            "kpi":          "3-second retention rate > 60%",
        },
        {
            "stage":       "2. Interest — Watch Time",
            "goal":        "Keep them watching through the content",
            "tactics":     [
                "Deliver the promise of the hook immediately",
                "Use cuts every 1-2 seconds (TikTok pacing)",
                "Build curiosity loop ('Wait for the end...')",
                "Text overlays reinforcing key points",
            ],
            "kpi":          "Full video completion rate > 30%",
        },
        {
            "stage":       "3. Desire — Profile Visit",
            "goal":        "Make them want to see more / follow",
            "tactics":     [
                "End CTA: 'Follow for more [niche] content'",
                "Profile must be optimized (bio + pinned post)",
                "Pinned video = best-performing content",
                "Consistent aesthetic = instant follow impulse",
            ],
            "kpi":          "Follower conversion rate > 2% of views",
        },
        {
            "stage":       "4. Action — Link Click",
            "goal":        "Drive traffic to link in bio / offer",
            "tactics":     [
                "CTA: 'Link in bio for [free resource/deal]'",
                "Create a Linktree / Beacons page with 1 primary CTA",
                "Pin comment with link on every post",
                "Story highlights linking to offers",
            ],
            "kpi":          "Link CTR > 0.5% of followers per post",
        },
        {
            "stage":       "5. Conversion — Revenue",
            "goal":        "Convert link click to revenue",
            "tactics":     [
                "Landing page must match the promise from content",
                "Minimal steps to purchase/signup",
                "Social proof on landing page",
                "Email capture for retargeting",
            ],
            "kpi":          "Landing page conversion rate > 3%",
        },
    ]

    funnel.cta_templates = get_cta_templates(niche, platform)

    funnel.link_in_bio_tools = [
        {"tool": "Beacons.ai",   "best_for": "Creators — free tier generous, analytics included"},
        {"tool": "Linktree",     "best_for": "Simple multi-link pages — most recognized"},
        {"tool": "Stan Store",   "best_for": "Selling digital products directly"},
        {"tool": "Gumroad",      "best_for": "Digital product sales with affiliate program"},
        {"tool": "Koji",         "best_for": "TikTok-native storefront integration"},
        {"tool": "Later Link in Bio", "best_for": "Instagram shoppable feed + scheduling"},
    ]

    funnel.funnel_metrics = calculate_conversion_rate(10000, link_clicks=200, sales=6)

    return funnel


def get_cta_templates(niche: str = "", platform: str = "tiktok") -> list[str]:
    """Return platform-optimized CTA templates."""
    niche_str = niche or "this niche"
    templates = [
        f"Follow for daily {niche_str} content 🔥",
        f"Link in bio — free {niche_str} guide 👇",
        f"Save this for later ✅",
        f"Comment '{niche_str[:4].upper() if niche_str else 'YES'}' and I'll DM you the full guide",
        f"Turn on notifications so you never miss a {niche_str} tip",
        f"Share this with someone who needs to see it 🙏",
        f"Follow + like if this helped you",
        f"Check my profile for more {niche_str} content",
    ]
    if platform.lower() == "youtube":
        templates += [
            "Subscribe for weekly [niche] videos",
            "Hit the bell 🔔 to never miss a video",
            "Drop your question in the comments — I reply to all",
        ]
    return templates


def get_monetization_strategies(niche: str = "") -> list[dict]:
    """Return monetization strategies ranked by effort vs reward."""
    return [
        {
            "method":       "Affiliate Marketing",
            "effort":       "low",
            "income_range": "$100-$10,000+/mo",
            "timeline":     "1-3 months",
            "how":          "Join Amazon Associates, ShareASale, or niche-specific programs. "
                            "Link in bio + mention in content.",
            "best_niches":  ["finance", "beauty", "tech", "fitness", "food"],
        },
        {
            "method":       "Shoutouts / Paid Promos",
            "effort":       "low",
            "income_range": "$20-$500 per post",
            "timeline":     "3-6 months (needs ~10K followers)",
            "how":          "List on Shoutcart, Fameswap, or DM brands directly. "
                            "Charge based on engagement rate not just follower count.",
            "best_niches":  ["all niches"],
        },
        {
            "method":       "Digital Products",
            "effort":       "medium",
            "income_range": "$500-$50,000+/mo",
            "timeline":     "2-4 months",
            "how":          "Create ebook, preset pack, course, or template. "
                            "Sell via Gumroad or Stan Store.",
            "best_niches":  ["finance", "fitness", "photography", "business"],
        },
        {
            "method":       "Newsletter / Email List",
            "effort":       "medium",
            "income_range": "$1,000-$100,000+/mo",
            "timeline":     "6-12 months",
            "how":          "Convert followers to email subscribers. "
                            "Monetize via sponsorships, affiliate, or own products.",
            "best_niches":  ["finance", "tech", "business", "lifestyle"],
        },
        {
            "method":       "Brand Deals / Sponsorships",
            "effort":       "low (at scale)",
            "income_range": "$500-$50,000+ per deal",
            "timeline":     "6-18 months",
            "how":          "Apply to creator marketplaces: AspireIQ, Grin, Creator.co. "
                            "Build a media kit showing engagement metrics.",
            "best_niches":  ["all niches with >50K followers"],
        },
        {
            "method":       "Account Flipping",
            "effort":       "medium",
            "income_range": "$500-$20,000 per account",
            "timeline":     "1-6 months build cycle",
            "how":          "Build niche account to 10K-100K, then sell on Fameswap "
                            "or Social Tradia. Repeat.",
            "best_niches":  ["pets", "quotes", "humor", "sports"],
        },
        {
            "method":       "TikTok Creator Fund / YT AdSense",
            "effort":       "zero (passive)",
            "income_range": "$0.02-$0.05 per 1K views",
            "timeline":     "Immediate (once eligible)",
            "how":          "Apply when eligible. Supplementary income only — "
                            "not a primary strategy.",
            "best_niches":  ["all"],
        },
    ]


def get_growth_playbook(niche: str, platform: str = "tiktok") -> list[dict]:
    """Step-by-step growth playbook for a new theme page."""
    return [
        {
            "phase":   "Phase 1: Setup (Days 1-3)",
            "actions": [
                f"Pick username: {niche.lower().replace(' ', '')}hub or {niche.lower().replace(' ', '')}daily",
                "Write bio using the hook formula: [Niche emoji] [What you post] | Follow for [benefit] 👇",
                "Set profile picture to niche-related graphic (not a face)",
                "Create 3-5 pieces of content BEFORE posting anything",
                "Follow 50-100 accounts in your niche to train the algorithm",
            ],
        },
        {
            "phase":   "Phase 2: Research (Days 2-7)",
            "actions": [
                "Identify top 10 accounts in your niche — reverse-engineer their top posts",
                "Note which content formats get most engagement (talking head, b-roll, text-only)",
                "Save 20+ trending sounds relevant to your niche",
                "Build a swipe file of hooks that performed well",
                "Run TrendHunter: fetch-trends to get current hashtag data",
            ],
        },
        {
            "phase":   "Phase 3: Post Consistently (Weeks 1-4)",
            "actions": [
                "Post 1-3x per day on TikTok | 1x per day on Instagram",
                "Use trending sounds in 50% of posts",
                "A/B test: one post per day with different hook styles",
                "Engage with every comment within the first hour",
                "Repost your top content to YouTube Shorts / Instagram Reels",
            ],
        },
        {
            "phase":   "Phase 4: Optimize (Month 2)",
            "actions": [
                "Audit analytics: identify your top 3 content formats",
                "Double down on what works — eliminate what doesn't",
                "Add affiliate links to bio (Amazon, etc.)",
                "Reach out to 5 accounts in your niche for collaboration/duet",
                "Start building email list with lead magnet",
            ],
        },
        {
            "phase":   "Phase 5: Monetize (Month 3+)",
            "actions": [
                "Apply to affiliate programs in your niche",
                "Create a simple digital product (guide, template, preset)",
                "List account on shoutout marketplaces",
                "Pitch 3 brands per week for sponsorships",
                "Consider building a second account to diversify",
            ],
        },
    ]


def calculate_conversion_rate(followers: int, link_clicks: int = 0,
                               sales: int = 0) -> dict:
    """Calculate and benchmark key conversion metrics."""
    if followers <= 0:
        return {}

    ctr = (link_clicks / followers * 100) if link_clicks else None
    conv = (sales / link_clicks * 100) if link_clicks and sales else None

    benchmarks = {
        "link_ctr_good":     "0.5-2%",
        "link_ctr_great":    ">2%",
        "conversion_good":   "1-3%",
        "conversion_great":  ">5%",
    }

    return {
        "followers":         followers,
        "link_clicks":       link_clicks,
        "link_ctr":          f"{ctr:.2f}%" if ctr is not None else "N/A",
        "sales":             sales,
        "conversion_rate":   f"{conv:.2f}%" if conv is not None else "N/A",
        "benchmarks":        benchmarks,
        "assessment": (
            "Strong CTR!" if (ctr or 0) > 2
            else "Good CTR" if (ctr or 0) > 0.5
            else "Optimize your CTA and bio link placement"
        ),
    }
