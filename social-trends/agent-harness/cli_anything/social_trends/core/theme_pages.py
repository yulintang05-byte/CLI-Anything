"""Social Trends CLI - Theme page strategy, creation, and conversion education."""

from typing import Dict, Any, List, Optional
from datetime import datetime

from cli_anything.social_trends.core.session import Session


_NICHE_DATABASE: Dict[str, Dict[str, Any]] = {
    "luxury_lifestyle": {
        "display": "Luxury Lifestyle",
        "difficulty": "easy",
        "competition": "high",
        "monetization_potential": "very_high",
        "avg_cpm": "$15-40",
        "content_sources": ["Pinterest", "YouTube", "Getty Images (licensed)", "Canva Pro"],
        "monetization_paths": ["Amazon affiliate (luxury products)", "Brand deals", "Dropshipping", "Digital products"],
        "target_audience": "18-34, aspirational earners",
        "growth_speed": "fast",
        "example_pages": ["@luxuryworldofficial", "@richlifestyle"],
    },
    "fitness_motivation": {
        "display": "Fitness Motivation",
        "difficulty": "easy",
        "competition": "very_high",
        "monetization_potential": "high",
        "avg_cpm": "$8-20",
        "content_sources": ["YouTube fitness creators", "Transformation Reddit posts", "AI-generated workout visuals"],
        "monetization_paths": ["Supplement affiliate", "Workout program sales", "Merch", "Coaching"],
        "target_audience": "18-45, fitness enthusiasts",
        "growth_speed": "fast",
    },
    "money_mindset": {
        "display": "Money & Wealth Mindset",
        "difficulty": "medium",
        "competition": "high",
        "monetization_potential": "very_high",
        "avg_cpm": "$20-60",
        "content_sources": ["Business book quotes", "Entrepreneur interviews", "Finance memes"],
        "monetization_paths": ["Finance app affiliate ($50-200/signup)", "Digital courses", "Coaching", "Newsletter"],
        "target_audience": "22-40, ambitious earners",
        "growth_speed": "medium",
    },
    "travel_aesthetic": {
        "display": "Travel Aesthetic",
        "difficulty": "easy",
        "competition": "medium",
        "monetization_potential": "high",
        "avg_cpm": "$10-25",
        "content_sources": ["Unsplash", "Pexels", "Creator reposts (with permission)", "AI landscape generation"],
        "monetization_paths": ["Travel affiliate (Booking.com, Airbnb)", "Brand deals", "LTK/Amazon storefront"],
        "target_audience": "20-35, travelers and dreamers",
        "growth_speed": "fast",
    },
    "dark_motivation": {
        "display": "Dark / Anti-Motivational",
        "difficulty": "easy",
        "competition": "medium",
        "monetization_potential": "medium",
        "avg_cpm": "$5-12",
        "content_sources": ["Philosophical quotes", "Movie clips (fair use edits)", "Aesthetic dark visuals"],
        "monetization_paths": ["Digital wallpacks", "Merch", "Brand deals (limited)"],
        "target_audience": "16-30, philosophical types",
        "growth_speed": "very_fast",
    },
    "pet_content": {
        "display": "Cute Pets / Animals",
        "difficulty": "easy",
        "competition": "very_high",
        "monetization_potential": "medium",
        "avg_cpm": "$6-15",
        "content_sources": ["Reddit r/aww", "User submissions", "Your own pet", "AI pet art"],
        "monetization_paths": ["Pet product affiliate", "Sponsorships", "Merch"],
        "target_audience": "all ages, pet lovers",
        "growth_speed": "very_fast",
    },
    "entrepreneurship": {
        "display": "Entrepreneurship & Business",
        "difficulty": "medium",
        "competition": "high",
        "monetization_potential": "very_high",
        "avg_cpm": "$25-80",
        "content_sources": ["Business book summaries", "Founder stories", "Startup news"],
        "monetization_paths": ["Course sales ($500-5000)", "Coaching", "SaaS affiliate", "Newsletter monetization"],
        "target_audience": "22-45, aspiring founders",
        "growth_speed": "medium",
    },
    "relationship_advice": {
        "display": "Relationships & Dating",
        "difficulty": "easy",
        "competition": "medium",
        "monetization_potential": "high",
        "avg_cpm": "$10-30",
        "content_sources": ["Reddit stories", "Anonymous DM submissions", "Book quotes"],
        "monetization_paths": ["Dating app affiliate", "Relationship coaching", "eBook sales"],
        "target_audience": "18-40, singles and couples",
        "growth_speed": "fast",
    },
}

_FUNNEL_TYPES: Dict[str, Dict[str, Any]] = {
    "dm_funnel": {
        "display": "DM Conversion Funnel",
        "complexity": "low",
        "conversion_rate": "3-8%",
        "description": "Drive followers to DM you a keyword → automated or manual reply → offer",
        "steps": [
            "1. CTA in video: 'DM me [KEYWORD] for the free [resource]'",
            "2. Pin a comment or note with the keyword",
            "3. When they DM: send lead magnet or product link immediately",
            "4. Follow up 24h later with value + soft sell",
            "5. Close with offer or upsell",
        ],
        "tools": ["ManyChat (automated DMs)", "Instagram DMs", "TikTok DMs"],
        "best_for": ["coaching", "digital products", "services", "affiliate"],
    },
    "link_in_bio_funnel": {
        "display": "Link-in-Bio Funnel",
        "complexity": "low",
        "conversion_rate": "1-3%",
        "description": "Drive traffic to a Linktree/Beacons page → email capture or direct sale",
        "steps": [
            "1. Create Linktree/Beacons/Stan Store page",
            "2. Add: free lead magnet, product, affiliate links",
            "3. Every CTA in content: 'Link in bio'",
            "4. Free resource → email capture → email sequence → paid offer",
        ],
        "tools": ["Linktree", "Beacons.ai", "Stan Store", "Gumroad", "Mailchimp/Klaviyo"],
        "best_for": ["all niches", "beginners"],
    },
    "email_list_funnel": {
        "display": "Email List → Sales Funnel",
        "complexity": "medium",
        "conversion_rate": "2-5%",
        "description": "Convert followers to email subscribers → nurture → pitch",
        "steps": [
            "1. Create a high-value lead magnet (checklist, template, mini-course)",
            "2. Drive to squeeze page (single opt-in form)",
            "3. Welcome sequence: 5-7 value emails over 10 days",
            "4. Introduce offer with scarcity/deadline",
            "5. Cart close email sequence (3 emails in final 24h)",
        ],
        "tools": ["ConvertKit", "Mailchimp", "Beehiiv (newsletter)", "ClickFunnels"],
        "best_for": ["finance", "education", "coaching", "software"],
        "avg_revenue_per_subscriber": "$1-3/month",
    },
    "affiliate_review_funnel": {
        "display": "Affiliate Review Funnel",
        "complexity": "low",
        "conversion_rate": "0.5-2%",
        "description": "Content reviews or recommendations → affiliate link click → commission",
        "steps": [
            "1. Research high-commission products in your niche (20-50% commission)",
            "2. Create honest review or 'best of' content",
            "3. Include affiliate link in bio, pinned comment, or description",
            "4. Disclose affiliation (required by FTC)",
        ],
        "tools": ["Amazon Associates", "ShareASale", "Impact.com", "PartnerStack"],
        "commission_examples": {
            "Finance apps": "$50-200/signup",
            "SaaS tools": "20-40% recurring",
            "Courses": "30-50% one-time",
            "Amazon products": "1-10%",
        },
        "best_for": ["tech", "beauty", "finance", "lifestyle"],
    },
    "paid_community_funnel": {
        "display": "Paid Community Funnel",
        "complexity": "high",
        "conversion_rate": "0.3-1%",
        "description": "Free content builds trust → premium community or membership",
        "steps": [
            "1. Build audience with free consistent content (90+ days)",
            "2. Tease exclusive value: 'I share this only inside my community'",
            "3. Launch community with founding member pricing (scarcity)",
            "4. Onboard members, deliver value, show wins",
            "5. Open cart monthly or quarterly",
        ],
        "tools": ["Skool", "Discord", "Telegram", "Circle", "Kajabi"],
        "price_range": "$27-97/month",
        "best_for": ["fitness", "business", "education", "lifestyle"],
    },
}

_CONTENT_STRATEGIES: Dict[str, List[str]] = {
    "repost_curate": [
        "Find viral content in niche (TikTok, YouTube, Pinterest)",
        "Download and re-edit: add text overlays, music, transitions",
        "Always credit original creator or use royalty-free sources",
        "Post at optimal times with niche hashtags",
        "Engage with every comment in first 30 mins",
    ],
    "ai_generated": [
        "Use Midjourney/DALL-E for images, ElevenLabs for voiceover",
        "Script content with ChatGPT, then record or use AI voice",
        "Use CapCut/Descript for editing + auto-captions",
        "Batch create 30 pieces of content in one session",
        "A/B test hooks — only scale winners",
    ],
    "ugc_submissions": [
        "Create a form: 'Submit your [niche] story/photo'",
        "Feature submissions weekly — builds community and generates content",
        "Credit submitters to incentivize more submissions",
        "Run contests: 'Submit your best [niche] transformation'",
        "Tag submitters for cross-promotion reach",
    ],
    "aggregator": [
        "Set Google Alerts for niche keywords",
        "Monitor Reddit/Twitter for viral stories",
        "Summarize and repackage news as short-form video",
        "Be the 'news desk' of your niche",
        "Source breaking niche content before competitors",
    ],
}


def list_niches(
    category: Optional[str] = None,
    sort_by: str = "monetization",
) -> List[Dict[str, Any]]:
    niches = []
    for key, data in _NICHE_DATABASE.items():
        niches.append({
            "id": key,
            "display": data["display"],
            "difficulty": data["difficulty"],
            "competition": data["competition"],
            "monetization_potential": data["monetization_potential"],
            "avg_cpm": data["avg_cpm"],
            "growth_speed": data["growth_speed"],
        })

    sort_map = {
        "monetization": lambda n: ["low", "medium", "high", "very_high"].index(
            n.get("monetization_potential", "low")),
        "growth": lambda n: ["slow", "medium", "fast", "very_fast"].index(
            n.get("growth_speed", "slow")),
        "difficulty_asc": lambda n: ["hard", "medium", "easy"].index(n.get("difficulty", "hard")),
    }
    sort_fn = sort_map.get(sort_by, sort_map["monetization"])
    niches.sort(key=sort_fn, reverse=True)
    return niches


def get_niche_detail(niche_id: str) -> Dict[str, Any]:
    if niche_id not in _NICHE_DATABASE:
        available = list(_NICHE_DATABASE.keys())
        raise KeyError(f"Niche '{niche_id}' not found. Available: {', '.join(available)}")
    data = _NICHE_DATABASE[niche_id].copy()
    data["id"] = niche_id
    return data


def create_theme_page(
    sess: Session,
    name: str,
    niche_id: str,
    platforms: List[str],
    content_strategy: str = "repost_curate",
) -> Dict[str, Any]:
    if niche_id not in _NICHE_DATABASE:
        raise KeyError(f"Niche '{niche_id}' not found. Run 'theme-page niches' to see options.")

    page_id = name.lower().replace(" ", "_").replace("@", "")
    niche = _NICHE_DATABASE[niche_id]
    strategy_steps = _CONTENT_STRATEGIES.get(content_strategy, _CONTENT_STRATEGIES["repost_curate"])

    sess.snapshot(f"create theme page {page_id}")
    page = {
        "id": page_id,
        "name": name,
        "niche_id": niche_id,
        "niche_display": niche["display"],
        "platforms": platforms,
        "content_strategy": content_strategy,
        "strategy_steps": strategy_steps,
        "monetization_paths": niche["monetization_paths"],
        "created": datetime.now().isoformat(),
        "status": "planning",
        "milestones": _get_milestones(niche_id),
    }
    sess.config["theme_pages"][page_id] = page
    return {
        "success": True,
        "page_id": page_id,
        "page": page,
        "quick_start": _quick_start_guide(niche_id, platforms, content_strategy),
    }


def _quick_start_guide(niche_id: str, platforms: List[str], strategy: str) -> List[str]:
    niche = _NICHE_DATABASE.get(niche_id, {})
    return [
        f"WEEK 1: Set up accounts on {', '.join(platforms)} with optimized bio + profile photo",
        f"WEEK 1: Source first 30 pieces of content from: {', '.join(niche.get('content_sources', ['Pinterest', 'YouTube'])[:2])}",
        f"WEEK 2-4: Post {3 if 'tiktok' in platforms else 1}x daily using '{strategy}' strategy",
        "WEEK 2-4: Engage 30min/day — reply to comments, DM interested followers",
        "WEEK 4+: Analyze top 3 performing posts — create 5 variations of each",
        f"MONTH 2: Set up first monetization: {niche.get('monetization_paths', ['affiliate'])[0]}",
        "MONTH 3+: Add second income stream, start email list capture",
    ]


def _get_milestones(niche_id: str) -> List[Dict[str, str]]:
    return [
        {"target": "100 followers", "focus": "Prove concept, test content formats"},
        {"target": "1K followers", "focus": "First affiliate link in bio, track clicks"},
        {"target": "5K followers", "focus": "Launch lead magnet, start email list"},
        {"target": "10K followers", "focus": "Unlock Instagram Subscription/TikTok Creator Fund"},
        {"target": "50K followers", "focus": "Brand deal outreach, $500-2K/month range"},
        {"target": "100K followers", "focus": "Full monetization suite, $2K-10K/month potential"},
    ]


def get_conversion_playbook(
    sess: Session,
    funnel_type: str = "dm_funnel",
    niche: Optional[str] = None,
) -> Dict[str, Any]:
    if funnel_type not in _FUNNEL_TYPES:
        available = list(_FUNNEL_TYPES.keys())
        raise KeyError(f"Funnel '{funnel_type}' not found. Available: {', '.join(available)}")

    funnel = _FUNNEL_TYPES[funnel_type].copy()
    result = {
        "funnel_type": funnel_type,
        **funnel,
        "niche_specific_tips": _niche_funnel_tips(niche, funnel_type),
        "kpis_to_track": [
            "Reach → Profile visits (aim for 5%+ click-through)",
            "Profile visits → Bio link clicks (aim for 10%+)",
            "Link clicks → Conversions (aim for 2-5%)",
            "Followers → DM rate (aim for 1-3% per viral post)",
        ],
        "red_flags_to_avoid": [
            "Never buy followers — kills organic reach permanently",
            "Don't pitch before you've given value (rule: 80% value, 20% promotion)",
            "Avoid over-automation — platforms penalize bot-like behavior",
            "Don't ignore DMs — 1h response time doubles conversion rates",
        ],
    }
    return result


def _niche_funnel_tips(niche: Optional[str], funnel_type: str) -> List[str]:
    tips_map: Dict[str, Dict[str, List[str]]] = {
        "finance": {
            "dm_funnel": ["Offer a free 'Wealth Audit' via DM", "Use scarcity: 'Only helping 10 people this month'"],
            "email_list_funnel": ["Lead magnet: 'Budget Template That Saved Me $500/month'"],
            "affiliate_review_funnel": ["High-value: Robinhood ($20), Coinbase, budget apps ($10-50/ref)"],
        },
        "fitness": {
            "dm_funnel": ["Offer free workout plan via DM 'GAINS'"],
            "link_in_bio_funnel": ["Stan Store works best — sell $27 workout programs directly"],
            "paid_community_funnel": ["Skool community: 90-day transformation challenge group"],
        },
    }

    if not niche:
        return ["Set a niche with 'theme-page create' for personalized tips"]

    niche_key = niche.lower().split("_")[0]
    niche_tips = tips_map.get(niche_key, {})
    return niche_tips.get(funnel_type, [
        f"Create a '{niche} starter kit' as your lead magnet",
        f"Research top affiliate programs for {niche} on ShareASale/Impact",
        f"Study top 3 converting {niche} theme pages for funnel inspiration",
    ])


def learn_theme_page_basics() -> Dict[str, Any]:
    """Educational guide for beginners."""
    return {
        "what_is_a_theme_page": (
            "A theme page is a social media account built around a specific niche topic "
            "(not personal branding). You curate, create, or aggregate content for that niche. "
            "The account IS the product — you grow it, monetize it, or sell it."
        ),
        "why_theme_pages_work": [
            "Niche audiences convert 4x better than general audiences",
            "You don't need to show your face or be a 'creator'",
            "Multiple pages = multiple income streams",
            "Pages can be sold for 24-36x monthly revenue once established",
            "Scalable with systems and tools — near-passive once running",
        ],
        "the_5_page_types": [
            {
                "type": "Inspiration/Quote Pages",
                "example": "@dailymotivation, @luxurymindset",
                "effort": "low",
                "monetization": "medium",
                "best_for": "beginners",
            },
            {
                "type": "Educational/Tips Pages",
                "example": "@financetips, @fitnesshacks",
                "effort": "medium",
                "monetization": "high",
                "best_for": "anyone with niche knowledge",
            },
            {
                "type": "Humor/Meme Pages",
                "example": "niche-specific meme accounts",
                "effort": "medium",
                "monetization": "medium",
                "best_for": "people with good content radar",
            },
            {
                "type": "Aggregator/News Pages",
                "example": "@techdailynews, @fashionweekly",
                "effort": "medium",
                "monetization": "high",
                "best_for": "people who consume lots of niche content",
            },
            {
                "type": "Showcase/Portfolio Pages",
                "example": "@architecturebeast, @carlifestyle",
                "effort": "low",
                "monetization": "high (brand deals)",
                "best_for": "aesthetic niches",
            },
        ],
        "income_streams_ranked": [
            {"rank": 1, "stream": "Digital Products (courses, templates, ebooks)",
             "why": "Highest margin, no inventory, scales infinitely"},
            {"rank": 2, "stream": "High-ticket Affiliate Marketing",
             "why": "$50-500/conversion for finance/SaaS niches"},
            {"rank": 3, "stream": "Paid Communities (Skool, Discord)",
             "why": "Recurring $27-97/month per member"},
            {"rank": 4, "stream": "Brand Sponsorships",
             "why": "$500-50K/post at scale, but requires 50K+ followers"},
            {"rank": 5, "stream": "Platform Creator Funds",
             "why": "Lowest ROI — supplement only, never rely on this"},
        ],
        "30_day_action_plan": [
            "Days 1-3: Pick niche, set up accounts, write optimized bios",
            "Days 4-7: Create 20 pieces of content, schedule for Week 1-2",
            "Days 8-14: Post 2-3x daily, engage 30min/day, track what works",
            "Days 15-21: Double down on best-performing format, add hashtag strategy",
            "Days 22-28: Set up first monetization path (affiliate link in bio)",
            "Day 30: Analyze metrics, plan Month 2 with data-driven decisions",
        ],
        "mistakes_to_avoid": [
            "Switching niches in the first 90 days — algorithm needs consistency",
            "Buying followers — kills reach for months",
            "Posting inconsistently — algorithm punishes gaps over 3 days",
            "No CTA in bio or content — views don't convert without direction",
            "Choosing a niche you hate — you'll quit before it pays off",
            "Only relying on one platform — always cross-post",
        ],
        "resources": {
            "tools": ["CapCut (editing)", "Canva (graphics)", "ChatGPT (scripting)",
                      "ManyChat (DM automation)", "Beacons/Stan Store (link in bio)"],
            "analytics": ["TikTok Analytics", "Instagram Insights", "YouTube Studio",
                          "Social Blade (benchmarking)", "Phlanx (engagement rate)"],
            "content_sources": ["Pinterest", "YouTube", "Reddit (niche subreddits)",
                                 "Unsplash/Pexels (images)", "Epidemic Sound (music)"],
        },
    }


def list_theme_pages(sess: Session) -> List[Dict[str, Any]]:
    pages = list(sess.config.get("theme_pages", {}).values())
    return sorted(pages, key=lambda p: p.get("created", ""))


def get_theme_page(sess: Session, page_id: str) -> Dict[str, Any]:
    pages = sess.config.get("theme_pages", {})
    if page_id not in pages:
        raise KeyError(f"Theme page '{page_id}' not found.")
    return pages[page_id]


def list_funnels() -> List[Dict[str, str]]:
    return [
        {
            "id": k,
            "display": v["display"],
            "complexity": v["complexity"],
            "conversion_rate": v["conversion_rate"],
            "best_for": ", ".join(v.get("best_for", [])),
        }
        for k, v in _FUNNEL_TYPES.items()
    ]
