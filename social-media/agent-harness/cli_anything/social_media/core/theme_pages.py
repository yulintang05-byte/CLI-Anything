"""Theme page strategy — how to build, run, and monetize niche content aggregator accounts."""

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class ThemePageBlueprint:
    niche: str
    page_name_ideas: list[str]
    content_strategy: dict
    sourcing_methods: list[str]
    repost_rules: list[str]
    monetization_stack: list[dict]
    conversion_funnel: list[str]
    growth_timeline: list[dict]
    tools_needed: list[dict]
    common_mistakes: list[str]
    legal_notes: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ConversionStrategy:
    page_type: str
    traffic_sources: list[str]
    lead_capture_methods: list[str]
    offers: list[dict]
    funnel_stages: list[dict]
    email_sequence: list[str]
    revenue_targets: dict

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Niche-specific blueprints
# ---------------------------------------------------------------------------

_NICHES = {
    "motivation": {
        "names": ["DailyHustle", "MindsetShift", "GrindNation", "ElevateDaily", "WinnersMindset"],
        "content_ratio": "60% motivational quotes/clips, 25% success stories, 15% productivity tips",
        "repost_sources": ["r/GetMotivated", "successful creator clips (with credit)", "book summaries"],
        "best_formats": ["Text on dark background (60s)", "Spoken-word over b-roll", "Quote card carousels"],
        "monetization": [
            {"method": "Affiliate — motivational books (Amazon Associates)", "rev": "$0.50-2.00 per click"},
            {"method": "Digital product — '30-Day Mindset Journal' PDF", "rev": "$7-27 one-time"},
            {"method": "Brand deals — productivity apps, supplements", "rev": "$200-5K per post at 50K+"},
            {"method": "TikTok Creator Fund", "rev": "$0.02-0.04 per 1K views"},
        ],
    },
    "finance": {
        "names": ["WealthMoves", "MoneyClips", "CashFlowDaily", "RichMindset", "InvestorFeed"],
        "content_ratio": "40% financial tips, 30% income/success stories, 20% market news, 10% tools",
        "repost_sources": ["Financial Twitter/X clips", "CNBC/Bloomberg short clips (fair use)", "Reddit r/personalfinance"],
        "best_formats": ["Data visualization + voice-over", "Screen recording of apps/charts", "Text explainers"],
        "monetization": [
            {"method": "Affiliate — trading apps (Webull, Public, Acorns)", "rev": "$5-50 per referral"},
            {"method": "Affiliate — credit cards (NerdWallet links)", "rev": "$50-300 per approval"},
            {"method": "Digital product — budget template / investment tracker", "rev": "$9-47 each"},
            {"method": "Paid newsletter or community ($7-29/month)", "rev": "Recurring MRR"},
        ],
    },
    "fitness": {
        "names": ["GymFeed", "IronDaily", "FitClips", "GainsNation", "BuildDaily"],
        "content_ratio": "50% workout tutorials/clips, 25% transformation stories, 15% nutrition, 10% gear",
        "repost_sources": ["Athlete YouTube clips", "Fitness Reddit", "Competitor workout posts (with credit)"],
        "best_formats": ["Fast-cut workout demos", "Body transformation time-lapses", "Reaction to form videos"],
        "monetization": [
            {"method": "Affiliate — supplements (MyProtein, Legion)", "rev": "$5-20 per sale"},
            {"method": "Affiliate — gym equipment (Amazon)", "rev": "3-8% commission"},
            {"method": "Online coaching program or PDF plan", "rev": "$27-197 each"},
            {"method": "Brand deals — sportswear, protein brands", "rev": "$300-10K per post at 100K+"},
        ],
    },
    "aesthetic": {
        "names": ["DreamFeed", "AuraVibes", "SoftLifeDaily", "AestheticMood", "CurationByX"],
        "content_ratio": "70% curated aesthetic content, 20% lifestyle tips, 10% product showcases",
        "repost_sources": ["Pinterest boards", "Instagram aesthetic creators (with credit)", "Unsplash/Pexels visuals"],
        "best_formats": ["Photo montages with ambient music", "Room/outfit inspo carousels", "Color-palette themed reels"],
        "monetization": [
            {"method": "Affiliate — Amazon home/lifestyle products", "rev": "3-10% commission"},
            {"method": "LTK / ShopMy storefront", "rev": "$20-200 per sale"},
            {"method": "Preset packs for Lightroom/VSCO", "rev": "$7-27 digital download"},
            {"method": "Brand deals — fashion, home decor, skincare", "rev": "$200-5K per post"},
        ],
    },
    "food": {
        "names": ["FoodDaily", "RecipeDrop", "TastyClips", "EatWell", "CookFeed"],
        "content_ratio": "60% recipe clips, 20% restaurant/food reviews, 15% food hacks, 5% product reviews",
        "repost_sources": ["Food creators (with permission/credit)", "Recipe sites (short clips)", "Restaurant social content"],
        "best_formats": ["Overhead cooking shots", "ASMR ingredient prep", "30-second recipe reels"],
        "monetization": [
            {"method": "Affiliate — kitchen equipment (Instant Pot, KitchenAid)", "rev": "$10-50 per sale"},
            {"method": "Recipe e-book / meal plan PDF", "rev": "$9-29 each"},
            {"method": "Brand deals — food brands, meal kits", "rev": "$300-5K per post"},
            {"method": "YouTube long-form recipe channel (AdSense)", "rev": "$3-8 CPM"},
        ],
    },
}

_CONTENT_SOURCING_METHODS = [
    "Screen-record publicly posted content and repost with full credit (@creator in caption)",
    "Download with yt-dlp or SnapTik and re-upload with watermark removed and caption credited",
    "Create original content inspired by trending formats — same idea, your execution",
    "Curate from royalty-free sources: Pexels, Pixabay, Mixkit for b-roll",
    "Compile listicles / montages from multiple creators (transformative = fair use)",
    "Partner with small creators: they get exposure, you get content",
    "Use AI tools (Runway, ElevenLabs, HeyGen) to generate original niche content at scale",
    "Film reaction/commentary to existing content (adds transformation for fair use)",
]

_REPOST_RULES = [
    "ALWAYS credit the original creator in caption (@username on source platform)",
    "Never remove original watermarks without creator permission",
    "DM creators before reposting — many will say yes and even share your post",
    "Add value: your caption, a hook, or commentary must differ from the original",
    "Do not repost accounts with 'do not repost' in bio — respect boundaries",
    "Transformative content (commentary, compilations, reactions) has stronger fair use protection",
    "Avoid reposting content from people who actively DMCA — stick to creator-friendly sources",
    "Build relationships with 10-20 core creators who consistently allow reposts",
]

_CONVERSION_FUNNEL = [
    "1. AWARENESS — Viral short-form content (TikTok/Reels) attracts cold audience",
    "2. INTEREST — Profile visit: bio explains who you help, link-in-bio visible",
    "3. CONSIDERATION — Follow + engage with content series (save/share worthy posts)",
    "4. CAPTURE — CTA to free lead magnet (email list, community, free resource)",
    "5. NURTURE — Email sequence (5-7 emails) builds trust, delivers value",
    "6. CONVERT — Offer paid product/service/affiliate (warmed audience buys)",
    "7. RETAIN — Community, repeat content, upsells keep them in ecosystem",
]

_GROWTH_TIMELINE = [
    {"week": "1-2", "goal": "Set up profiles, choose niche, create 20 test posts", "metric": "0-100 followers"},
    {"week": "3-4", "goal": "Post 3x/day, engage 30min/day, identify top formats", "metric": "100-500 followers"},
    {"week": "5-8", "goal": "Double down on top 2 formats, add trending sounds", "metric": "500-2,000 followers"},
    {"week": "9-12", "goal": "First viral video, analyze and replicate its structure", "metric": "2K-10K followers"},
    {"week": "13-16", "goal": "Monetize: set up affiliate links, launch lead magnet", "metric": "10K-25K followers"},
    {"week": "17-24", "goal": "Brand deals, digital product launch, email list 1K+", "metric": "25K-100K followers"},
    {"week": "25+", "goal": "Scale: hire editor/VA, expand platforms, compound revenue", "metric": "100K+ followers"},
]

_TOOLS_NEEDED = [
    {"tool": "CapCut", "purpose": "Free mobile/desktop video editor with trending templates", "cost": "Free"},
    {"tool": "Canva", "purpose": "Thumbnail design, quote cards, carousel posts", "cost": "Free / $15/mo Pro"},
    {"tool": "Later / Buffer", "purpose": "Schedule posts across platforms in advance", "cost": "$18-40/mo"},
    {"tool": "Stan Store / Linktree", "purpose": "Link-in-bio hub for offers and lead capture", "cost": "Free / $9/mo"},
    {"tool": "ConvertKit / Beehiiv", "purpose": "Email list capture and automated sequences", "cost": "Free up to 1K subs"},
    {"tool": "yt-dlp", "purpose": "Download videos for re-editing and repurposing (with permission)", "cost": "Free (CLI)"},
    {"tool": "TrendTok / Tokboard", "purpose": "TikTok trend analytics and competitor analysis", "cost": "$15-49/mo"},
    {"tool": "ElevenLabs", "purpose": "AI voiceover for content at scale", "cost": "$5-22/mo"},
    {"tool": "Notion / Airtable", "purpose": "Content calendar and idea database", "cost": "Free tier available"},
    {"tool": "Amazon Associates", "purpose": "Affiliate links for product recommendations", "cost": "Free (commission-based)"},
]

_COMMON_MISTAKES = [
    "Choosing too broad a niche — 'motivation' beats nothing, but 'motivation for new dads' beats 'motivation'",
    "Posting inconsistently — going viral once then disappearing kills momentum permanently",
    "Reposting without credit — destroys reputation and risks DMCA strikes",
    "Not building an email list — if the platform bans you, you lose everything",
    "Trying to monetize too early (before 5K engaged followers) — audience isn't warm yet",
    "Ignoring analytics — post what works, kill what doesn't within 2 weeks of data",
    "Copying competitors exactly instead of finding your unique angle",
    "Posting only in one timezone — your audience is global, test timing",
    "Never showing a face or voice — faceless works but face content converts 3x better",
    "Not reinvesting in equipment/editing quality as revenue grows",
]

_LEGAL_NOTES = [
    "Copyright: Reposting requires either permission, proper credit, or transformative use (commentary/compilation)",
    "Fair Use (US) 4 factors: purpose, nature of original, amount used, market effect — compilations/reactions usually qualify",
    "Music: Always use TikTok/Reels licensed music library or royalty-free tracks to avoid muting/strikes",
    "FTC Disclosure: Mark ALL affiliate links and paid partnerships with #ad or #sponsored (legally required)",
    "Platform Terms: Read each platform's T&C on automated posting and mass reposting — limits vary",
    "Taxes: Report all income — affiliate commissions, brand deals, digital product sales are taxable",
    "Privacy: Never post identifiable minors or private individuals without consent",
]


def get_blueprint(niche: str = "motivation") -> ThemePageBlueprint:
    """Get a complete theme page blueprint for a niche."""
    niche = niche.lower()
    data = _NICHES.get(niche, _NICHES["motivation"])

    return ThemePageBlueprint(
        niche=niche,
        page_name_ideas=data["names"],
        content_strategy={
            "content_ratio": data["content_ratio"],
            "best_formats": data["best_formats"],
            "posting_frequency": "3-5x/day TikTok, 2-3x/day IG Reels, 1x/day YouTube Shorts",
        },
        sourcing_methods=_CONTENT_SOURCING_METHODS,
        repost_rules=_REPOST_RULES,
        monetization_stack=data["monetization"],
        conversion_funnel=_CONVERSION_FUNNEL,
        growth_timeline=_GROWTH_TIMELINE,
        tools_needed=_TOOLS_NEEDED,
        common_mistakes=_COMMON_MISTAKES,
        legal_notes=_LEGAL_NOTES,
    )


def get_conversion_strategy(
    page_type: str = "theme_page",
    niche: str = "motivation",
    follower_count: int = 0,
) -> ConversionStrategy:
    """Get a conversion strategy tailored to page type and growth stage."""
    niche_data = _NICHES.get(niche.lower(), _NICHES["motivation"])

    offers = [m.copy() for m in niche_data["monetization"]]
    for offer in offers:
        offer["recommended_for"] = (
            "0-10K followers" if "Fund" in offer["method"] or "Affiliate" in offer["method"]
            else "10K+ followers"
        )

    funnel_stages = [
        {
            "stage": s.split("—")[0].strip(),
            "description": s.split("—")[1].strip() if "—" in s else s,
        }
        for s in _CONVERSION_FUNNEL
    ]

    email_sequence = [
        "Email 1 (Day 0): Deliver free lead magnet + welcome + set expectations",
        "Email 2 (Day 1): Your story — who you are, why this niche, build trust",
        "Email 3 (Day 3): Pure value — your best tip/resource with zero pitch",
        "Email 4 (Day 5): Social proof — transformation story or result of using your method",
        "Email 5 (Day 7): Soft offer intro — 'I made X to help you do Y' with link",
        "Email 6 (Day 10): FAQ / objection handling — address top 3 reasons people don't buy",
        "Email 7 (Day 14): Hard close with scarcity or bonus — last chance CTA",
        "Email 8+ (Weekly): Nurture with value + periodic offers (don't go dark)",
    ]

    revenue_targets = {
        "0-1K followers": "$0-50/month (affiliate only)",
        "1K-10K followers": "$50-500/month (affiliate + digital products)",
        "10K-50K followers": "$500-3K/month (brand deals + products + affiliate)",
        "50K-100K followers": "$3K-10K/month (multiple streams)",
        "100K+": "$10K-100K+/month (scale all streams + high-ticket deals)",
    }

    return ConversionStrategy(
        page_type=page_type,
        traffic_sources=[
            "TikTok (primary viral engine — zero organic reach ceiling)",
            "Instagram Reels (repurpose TikTok content, wider demographic)",
            "YouTube Shorts (evergreen search traffic + suggested feed)",
            "Pinterest (passive visual traffic — great for aesthetic/food niches)",
            "X/Twitter (text + clips — great for finance/opinion niches)",
        ],
        lead_capture_methods=[
            "Link-in-bio → free lead magnet (PDF, checklist, template)",
            "'Comment [keyword] for free [resource]' → DM automation (ManyChat)",
            "Story poll → DM follow-up to engaged viewers",
            "YouTube description → email signup for bonus content",
            "Live streams → CTA to join newsletter for exclusive content",
        ],
        offers=offers,
        funnel_stages=funnel_stages,
        email_sequence=email_sequence,
        revenue_targets=revenue_targets,
    )


def list_niches() -> list[str]:
    """Return all supported niche blueprints."""
    return list(_NICHES.keys())
