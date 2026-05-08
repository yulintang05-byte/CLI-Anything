"""Theme page strategy, niche ranking, and conversion funnel builder.

A theme page (also called a "fan page" or "content aggregator page") is a
social media account that curates and reposts content around a specific niche
(travel, gym, quotes, luxury cars, etc.) rather than creating original content.

This module covers:
  1. Profitable niche ranking with monetisation potential scores
  2. Step-by-step page setup and growth roadmap
  3. Conversion funnel templates for turning followers into revenue
  4. Legal/ethical guidelines for reposting content
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class NicheProfile:
    name: str
    monetisation_score: float    # 0-100
    growth_speed: str            # "slow" | "medium" | "fast" | "explosive"
    competition: str             # "low" | "medium" | "high" | "saturated"
    avg_cpm_usd: float           # TikTok/YouTube ad revenue per 1000 views
    affiliate_potential: str     # "low" | "medium" | "high"
    shoutout_rate_usd: tuple[int, int]  # (min, max) per sponsored post at 100k
    top_content_types: list[str]
    best_platforms: list[str]
    notes: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "monetisation_score": self.monetisation_score,
            "growth_speed": self.growth_speed,
            "competition": self.competition,
            "avg_cpm_usd": self.avg_cpm_usd,
            "affiliate_potential": self.affiliate_potential,
            "shoutout_rate_range_usd": list(self.shoutout_rate_usd),
            "top_content_types": self.top_content_types,
            "best_platforms": self.best_platforms,
            "notes": self.notes,
        }


# Ranked by overall monetisation score
NICHE_DATABASE: list[NicheProfile] = [
    NicheProfile(
        name="Finance / Money",
        monetisation_score=95,
        growth_speed="fast",
        competition="high",
        avg_cpm_usd=18.50,
        affiliate_potential="high",
        shoutout_rate_usd=(500, 3000),
        top_content_types=["investing tips", "budgeting hacks", "passive income ideas", "wealth mindset clips"],
        best_platforms=["YouTube", "TikTok", "Instagram"],
        notes="Highest CPM niche. Affiliate programs (brokers, apps) pay $50-200 per lead.",
    ),
    NicheProfile(
        name="Fitness / Gym",
        monetisation_score=88,
        growth_speed="fast",
        competition="high",
        avg_cpm_usd=8.20,
        affiliate_potential="high",
        shoutout_rate_usd=(300, 2000),
        top_content_types=["transformation clips", "workout reels", "gym fails", "nutrition tips"],
        best_platforms=["TikTok", "Instagram", "YouTube Shorts"],
        notes="Supplement affiliate programs (MyProtein, GNC) pay 10-20% commission. High engagement niche.",
    ),
    NicheProfile(
        name="Luxury / Lifestyle",
        monetisation_score=85,
        growth_speed="explosive",
        competition="medium",
        avg_cpm_usd=12.00,
        affiliate_potential="medium",
        shoutout_rate_usd=(400, 2500),
        top_content_types=["supercar clips", "mansion tours", "luxury hotels", "private jets"],
        best_platforms=["TikTok", "Instagram", "YouTube"],
        notes="Very high shoutout rates. Aspirational content gets massive organic reach.",
    ),
    NicheProfile(
        name="Travel",
        monetisation_score=80,
        growth_speed="medium",
        competition="medium",
        avg_cpm_usd=7.50,
        affiliate_potential="high",
        shoutout_rate_usd=(250, 1800),
        top_content_types=["hidden gem destinations", "travel hacks", "hotel reviews", "flight deals"],
        best_platforms=["YouTube", "TikTok", "Instagram"],
        notes="Hotels, booking platforms, travel insurance all offer affiliate. Seasonally viral.",
    ),
    NicheProfile(
        name="Beauty / Makeup",
        monetisation_score=82,
        growth_speed="fast",
        competition="high",
        avg_cpm_usd=6.00,
        affiliate_potential="high",
        shoutout_rate_usd=(200, 1500),
        top_content_types=["product reviews", "tutorials", "transformation", "dupes"],
        best_platforms=["TikTok", "Instagram", "YouTube"],
        notes="Amazon affiliate + brand deals. Duet/reaction format easy for theme pages.",
    ),
    NicheProfile(
        name="Motivation / Quotes",
        monetisation_score=65,
        growth_speed="explosive",
        competition="saturated",
        avg_cpm_usd=2.50,
        affiliate_potential="low",
        shoutout_rate_usd=(50, 400),
        top_content_types=["motivational clips", "success stories", "mindset quotes", "entrepreneur stories"],
        best_platforms=["TikTok", "Instagram"],
        notes="Easy to grow but low CPM and saturated. Best used as funnel top-of-funnel for courses.",
    ),
    NicheProfile(
        name="Food / Recipes",
        monetisation_score=72,
        growth_speed="fast",
        competition="high",
        avg_cpm_usd=4.00,
        affiliate_potential="medium",
        shoutout_rate_usd=(150, 800),
        top_content_types=["recipe videos", "restaurant reviews", "food hacks", "mukbang"],
        best_platforms=["TikTok", "YouTube", "Instagram"],
        notes="Kitchen gadget affiliate (Amazon) performs well. ASMR food content is explosive.",
    ),
    NicheProfile(
        name="Gaming",
        monetisation_score=78,
        growth_speed="fast",
        competition="high",
        avg_cpm_usd=5.50,
        affiliate_potential="medium",
        shoutout_rate_usd=(200, 1200),
        top_content_types=["highlights / clips", "fails & funny moments", "game reviews", "tutorials"],
        best_platforms=["YouTube", "TikTok", "Twitch"],
        notes="Large audience but young demographic lowers CPM. Brand deals with peripherals are lucrative.",
    ),
    NicheProfile(
        name="Pets / Animals",
        monetisation_score=68,
        growth_speed="explosive",
        competition="medium",
        avg_cpm_usd=3.50,
        affiliate_potential="medium",
        shoutout_rate_usd=(100, 600),
        top_content_types=["cute clips", "animal rescues", "funny pet moments", "pet care tips"],
        best_platforms=["TikTok", "Instagram", "YouTube Shorts"],
        notes="Easiest niche for viral organic reach. Pet product affiliate (Chewy, Amazon) is reliable.",
    ),
    NicheProfile(
        name="Fashion / Style",
        monetisation_score=76,
        growth_speed="medium",
        competition="high",
        avg_cpm_usd=5.00,
        affiliate_potential="high",
        shoutout_rate_usd=(200, 1500),
        top_content_types=["OOTD", "hauls", "style tips", "trend roundups"],
        best_platforms=["TikTok", "Instagram", "Pinterest"],
        notes="LTK and Amazon affiliate convert very well. Visual platform is advantage.",
    ),
]


@dataclass
class RoadmapStep:
    phase: int
    title: str
    duration: str
    actions: list[str]
    kpi: str

    def to_dict(self) -> dict:
        return {
            "phase": self.phase,
            "title": self.title,
            "duration": self.duration,
            "actions": self.actions,
            "kpi": self.kpi,
        }


def get_theme_page_roadmap(niche: str, platform: str = "tiktok") -> list[RoadmapStep]:
    """Return a 6-phase theme page launch and monetisation roadmap."""
    return [
        RoadmapStep(
            phase=1,
            title="Foundation Setup",
            duration="Day 1-3",
            actions=[
                f"Create account with keyword-rich username (e.g. @{niche.lower().replace(' ', '')}daily)",
                f"Write niche bio: '{niche.title()} content daily | Follow for [benefit]'",
                "Set profile picture: clean logo or niche-relevant image (Canva free)",
                "Follow 20-50 accounts in your niche to prime the algorithm",
                "Enable Creator/Business mode for analytics access",
                "Set up a Linktree or Beacons page (free) as your link-in-bio",
            ],
            kpi="Account fully optimised, 0 posts, 0 followers",
        ),
        RoadmapStep(
            phase=2,
            title="Content Seeding (0 → 1k followers)",
            duration="Week 1-2",
            actions=[
                "Post 2-4 times per day using trending sounds (from `music trending` command)",
                f"Repost the top 5 viral {niche} videos of the week with proper credit (tag original creator)",
                "Add value with text overlays: tips, captions, call-to-action",
                f"Use niche-specific hashtags: 3-5 targeted tags (from `hashtags suggest --niche {niche}`)",
                "Engage: reply to all comments within 30 minutes of posting",
                "Study your analytics: track which posts get most saves and shares",
            ],
            kpi="500-1,000 followers, 1+ video with 10k+ views",
        ),
        RoadmapStep(
            phase=3,
            title="Algorithm Lock-In (1k → 10k followers)",
            duration="Week 3-6",
            actions=[
                "Identify your 3 best-performing content formats and double down on them",
                "Create a content calendar: 14 posts planned in advance",
                "Start a recurring series (e.g. 'Monday Motivation', 'Friday Fail')",
                "Go LIVE 2x per week — TikTok LIVE boosts account reach significantly",
                "Cross-post every video to Instagram Reels and YouTube Shorts (3x reach, same content)",
                "Build email list via Linktree freebie — start capturing audience off-platform",
            ],
            kpi="5,000-10,000 followers, consistent 50k+ views per post",
        ),
        RoadmapStep(
            phase=4,
            title="Monetisation Activation (10k+)",
            duration="Month 2-3",
            actions=[
                "Apply for TikTok Creator Rewards Program (10k followers + 100k views in 30 days)",
                f"Join affiliate programs relevant to {niche} (Amazon, niche-specific brands)",
                "DM smaller brands in your niche for paid shoutout deals ($50-200 per post at this stage)",
                "Add affiliate links to Linktree for passive income on every post",
                "Create a digital product (PDF guide, template) specific to your niche — sell for $7-27",
                "Enable TikTok Shop affiliate if in eligible region",
            ],
            kpi="First $100-500 in monthly revenue, 15k+ followers",
        ),
        RoadmapStep(
            phase=5,
            title="Scale & Systematise (10k → 100k)",
            duration="Month 3-6",
            actions=[
                "Hire a VA ($5-15/hr) to handle content sourcing and scheduling",
                "Use scheduling tools (Later, TikTok Scheduler) to maintain 2-4 posts/day",
                "Launch a second account in a sub-niche to test new audiences",
                "Negotiate media kit deals: charge $200-800 per sponsored post at 50k",
                "Build a Discord or Telegram community for super-fans — monetise with paid tier",
                "Audit analytics monthly: double down on top 20% of content types",
            ],
            kpi="50k+ followers, $1,000-5,000 monthly revenue",
        ),
        RoadmapStep(
            phase=6,
            title="Authority & Full Monetisation (100k+)",
            duration="Month 6-12",
            actions=[
                "Launch your own course or coaching program ($97-497) targeting your audience pain points",
                "Apply for YouTube Partner Program if using YouTube Shorts simultaneously",
                "Negotiate long-term brand partnerships ($1,000-5,000/month retainer)",
                "Build a newsletter (Beehiiv free tier) and monetise with Boosts",
                "Consider flipping the account — 100k niche pages sell for $2,000-20,000+",
                "Start building next account in parallel — create a portfolio of pages",
            ],
            kpi="100k+ followers, $5,000-20,000+ monthly revenue",
        ),
    ]


@dataclass
class ConversionFunnel:
    name: str
    stage: str
    description: str
    tactics: list[str]
    tools: list[str]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "stage": self.stage,
            "description": self.description,
            "tactics": self.tactics,
            "tools": self.tools,
        }


def get_conversion_funnel(niche: str) -> list[ConversionFunnel]:
    """Return a conversion funnel optimised for theme page monetisation."""
    return [
        ConversionFunnel(
            name="Awareness",
            stage="Top of Funnel",
            description="Viral content gets you in front of cold audiences who don't know you yet.",
            tactics=[
                f"Post 3-4x/day: trending {niche} clips with trending sounds",
                "Use broad hashtags (#fyp, #viral) + 2-3 niche tags",
                "Hook in first 1s: text overlay asking a question or showing result",
                "Duet / Stitch viral content to piggyback its momentum",
            ],
            tools=["TikTok Creative Center", "CapCut (free editor)", "Canva (thumbnails)"],
        ),
        ConversionFunnel(
            name="Engagement",
            stage="Middle of Funnel",
            description="Convert viewers into followers who regularly consume your content.",
            tactics=[
                "Pin your 3 best videos to your profile",
                "Create a series (Part 1, 2, 3…) that forces profile visits",
                "Reply to every comment — comment sections grow organic reach",
                "Ask questions in captions to drive comment engagement",
                f"Post value-dense content: '{niche} tips you wish you knew sooner'",
            ],
            tools=["TikTok Analytics", "Later (scheduling)", "notion (content calendar)"],
        ),
        ConversionFunnel(
            name="Capture",
            stage="List Building",
            description="Move followers to an owned channel you control (email, Discord, SMS).",
            tactics=[
                "Offer a free lead magnet in bio: 'Free [niche] guide — link below'",
                "Tease exclusive content: 'Full version only in my email list'",
                "Run a giveaway requiring email signup to enter",
                "Create a Telegram or Discord for your 'inner circle' — free tier first",
            ],
            tools=["Linktree / Beacons (free)", "Beehiiv (email - free)", "Manychat (DM automation)"],
        ),
        ConversionFunnel(
            name="Monetisation",
            stage="Bottom of Funnel",
            description="Convert your audience into paying customers or generate ad/affiliate revenue.",
            tactics=[
                f"Affiliate: promote {niche}-relevant products with your unique link",
                "Paid shoutouts: brands pay $50-3,000/post depending on follower count",
                "Digital product: sell a PDF guide, template, or mini-course for $7-47",
                "Creator fund / Rewards Program for passive video revenue",
                "TikTok Shop affiliate: earn 5-20% commission on products you showcase",
            ],
            tools=["Amazon Associates", "Impact (affiliate network)", "Gumroad / Stan.store (digital products)", "TikTok Shop"],
        ),
        ConversionFunnel(
            name="Retention",
            stage="Loyalty Loop",
            description="Keep followers coming back and buying repeatedly.",
            tactics=[
                "Consistent posting schedule — same time every day builds habit",
                "Newsletter with exclusive tips not posted on social media",
                "Community (Discord/Telegram) for ongoing engagement",
                "Monthly subscriber-only content or live Q&A",
            ],
            tools=["Beehiiv", "Discord", "TikTok LIVE"],
        ),
    ]


def get_repost_ethics_guide() -> list[dict]:
    """Return ethical and legal guidelines for reposting content."""
    return [
        {
            "rule": "Always credit the original creator",
            "how": "Tag @originalcreator in caption and as a text overlay in the video",
            "why": "Avoids copyright strikes and maintains community goodwill",
        },
        {
            "rule": "Ask permission when possible",
            "how": "DM the creator: 'Can I share this on my page? I'll credit you.' Many say yes.",
            "why": "Permission = zero risk. Often leads to collaborations and mutual shoutouts",
        },
        {
            "rule": "Add value — don't just repost",
            "how": "Add captions, tips, reactions, or context that makes the post better",
            "why": "Pure reposting risks account bans; added value = transformative use",
        },
        {
            "rule": "Never repost copyrighted music or film clips",
            "how": "Use only clips that are already on the platform, replace audio with licensed sounds",
            "why": "Copyright holders actively DMCA-strike pages — this kills accounts",
        },
        {
            "rule": "Check for watermarks",
            "how": "Download with original watermark or use the platform's native Repost button",
            "why": "Removing creator watermarks is a platform ToS violation and unethical",
        },
        {
            "rule": "Don't use competitors' branded content",
            "how": "Avoid reposting content from accounts that monetise the same niche with their own brand",
            "why": "Direct competitors will file takedown requests",
        },
    ]


def rank_niches(sort_by: str = "monetisation_score") -> list[NicheProfile]:
    """Return niches sorted by the given attribute."""
    valid = {"monetisation_score", "avg_cpm_usd", "name"}
    if sort_by not in valid:
        sort_by = "monetisation_score"
    return sorted(NICHE_DATABASE, key=lambda n: getattr(n, sort_by), reverse=(sort_by != "name"))
