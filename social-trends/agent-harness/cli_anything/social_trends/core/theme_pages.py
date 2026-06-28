"""Theme page creation, niche research, and conversion strategy."""

from cli_anything.social_trends.utils.social_backend import (
    get_theme_page_niches,
    get_theme_page_guide,
    THEME_PAGE_NICHES,
)


def list_niches(sort_by: str = "conversion_rate") -> dict:
    """List all supported theme page niches with scores."""
    niches = get_theme_page_niches(sort_by=sort_by)

    conversion_rank = {"Very High": 4, "High": 3, "Medium": 3, "Medium-High": 3, "Low": 1}
    difficulty_rank = {"Low": 3, "Medium": 2, "High": 1}

    scored = []
    for n in niches:
        conv_score = conversion_rank.get(n.get("conversion_rate", ""), 1)
        diff_score = difficulty_rank.get(n.get("difficulty", ""), 1)
        score = int((conv_score * 0.6 + diff_score * 0.4) / 4 * 100)
        scored.append({**n, "opportunity_score": score})

    if sort_by == "conversion_rate":
        scored.sort(key=lambda x: x["opportunity_score"], reverse=True)
    elif sort_by == "difficulty":
        scored.sort(key=lambda x: difficulty_rank.get(x.get("difficulty", ""), 0), reverse=True)

    return {
        "total_niches": len(scored),
        "sort_by": sort_by,
        "niches": scored,
        "recommendation": (
            "Top picks for beginners: Motivation (Low difficulty, High conversion) and "
            "Finance (Medium difficulty, Very High conversion). "
            "Start with ONE niche and master it before expanding."
        ),
    }


def get_guide() -> dict:
    """Get the complete theme page creation and conversion guide."""
    return get_theme_page_guide()


def niche_research(niche: str) -> dict:
    """Deep-dive research for a specific theme page niche."""
    niche_key = niche.lower()

    niche_data = next(
        (n for n in THEME_PAGE_NICHES if niche_key in n["niche"].lower()),
        None,
    )

    if not niche_data:
        return {
            "error": f"Niche '{niche}' not in database.",
            "available": [n["niche"] for n in THEME_PAGE_NICHES],
        }

    # Expand with deep research
    affiliate_programs = {
        "luxury lifestyle": [
            {"program": "Farfetch Affiliate", "commission": "4-10%", "avg_order": "$300+"},
            {"program": "SSENSE Affiliate", "commission": "4-7%", "avg_order": "$250+"},
            {"program": "Watchfinder & Co", "commission": "5-8%", "avg_order": "$2000+"},
        ],
        "motivational / quotes": [
            {"program": "Audible Affiliate (Amazon)", "commission": "$5-15/signup", "avg_order": "subscription"},
            {"program": "Masterclass Affiliate", "commission": "25%", "avg_order": "$120+"},
            {"program": "Blinkist Affiliate", "commission": "20%", "avg_order": "$80/year"},
        ],
        "finance / wealth": [
            {"program": "Webull (US)", "commission": "$12-30/signup", "avg_order": "account open"},
            {"program": "Coinbase Affiliate", "commission": "$10/qualified referral", "avg_order": "varies"},
            {"program": "Personal Capital", "commission": "$50-100/qualified lead", "avg_order": "high-value"},
            {"program": "Fundrise", "commission": "$50-250/investor", "avg_order": "investment"},
        ],
        "fitness / health": [
            {"program": "MyProtein Affiliate", "commission": "8%", "avg_order": "$50+"},
            {"program": "Gymshark Affiliate", "commission": "6%", "avg_order": "$80+"},
            {"program": "Noom Affiliate", "commission": "$30-40/trial", "avg_order": "subscription"},
        ],
        "pet / animals": [
            {"program": "Chewy Affiliate", "commission": "4%", "avg_order": "$60+"},
            {"program": "BarkBox Affiliate", "commission": "$18/subscription", "avg_order": "subscription"},
            {"program": "Petco Affiliate", "commission": "4%", "avg_order": "$50+"},
        ],
        "tech / gadgets": [
            {"program": "Amazon Associates", "commission": "1-10% (varies by category)", "avg_order": "$100+"},
            {"program": "Newegg Affiliate", "commission": "1-4%", "avg_order": "$150+"},
            {"program": "B&H Photo", "commission": "2-3%", "avg_order": "$200+"},
        ],
        "aesthetic / visual": [
            {"program": "VSCO Affiliate (presets)", "commission": "20-30%", "avg_order": "$20+"},
            {"program": "Lightroom Preset marketplaces", "commission": "30-50% (own products)", "avg_order": "$15-50"},
            {"program": "Society6 / Redbubble (print-on-demand)", "commission": "10-20%", "avg_order": "$30+"},
        ],
        "real estate / entrepreneur": [
            {"program": "BiggerPockets Affiliate", "commission": "varies", "avg_order": "course/membership"},
            {"program": "Teachable (own courses)", "commission": "0% (keep all)", "avg_order": "$97-997"},
            {"program": "ClickFunnels Affiliate", "commission": "40%", "avg_order": "$97/mo"},
        ],
    }

    niche_lower = niche_data["niche"].lower()
    affiliates = affiliate_programs.get(niche_lower, [])

    content_templates = _get_content_templates(niche_lower)

    return {
        "niche": niche_data["niche"],
        "overview": niche_data,
        "affiliate_programs": affiliates,
        "content_templates": content_templates,
        "account_names_ideas": _generate_account_name_ideas(niche_lower),
        "bio_template": _generate_bio_template(niche_lower),
        "first_10_posts": _get_starter_content(niche_lower),
        "30_day_goal": (
            "1,000+ followers, 5+ affiliate clicks/day, 1 brand DM received. "
            "Post 2x/day with trending sounds. Engage 30 min after each post."
        ),
    }


def _get_content_templates(niche: str) -> list:
    templates = {
        "luxury lifestyle": [
            "Things billionaires do differently that nobody talks about",
            "This is what $[X] buys you [before/after comparison]",
            "POV: You have unlimited money and zero obligations",
            "Luxury vs. Ultra-luxury: What's the actual difference?",
            "The most expensive [item] in the world (and why it's worth it)",
        ],
        "motivational / quotes": [
            "'[Quote]' — This hit different. Save this.",
            "If you're struggling with [pain point], watch this until the end",
            "The difference between successful people and everyone else",
            "Nobody talks about how hard [universal struggle] is",
            "One year ago I was [relatable low]. Today I am [aspirational high].",
        ],
        "finance / wealth": [
            "How to turn $[X] into $[Y] legally in [timeframe]",
            "This one money mistake is silently stealing from you",
            "[Number] ways to make money while you sleep in [year]",
            "Why your [savings account / 401k / investment] is losing you money",
            "The wealth-building hack banks don't want you to know",
        ],
        "fitness / health": [
            "[X]-day transformation (starting with zero equipment)",
            "The workout that burns fat 24 hours after you stop",
            "Why you're not losing weight despite trying everything",
            "What I eat in a day to maintain [physique goal]",
            "The 5-minute morning routine that actually changed my body",
        ],
        "pet / animals": [
            "My [pet] learned [trick] in [timeframe] using this method",
            "Signs your [pet] loves you that you might be missing",
            "The funniest thing my [pet] does when I'm not home",
            "How to train your [pet] to [behavior] in 3 steps",
            "This [pet] reaction to [situation] has me crying laughing",
        ],
    }
    return templates.get(niche, [
        "Did you know [niche fact]? This changed everything.",
        "[Number] things about [niche] I wish I knew earlier",
        "The truth about [niche topic] nobody talks about",
        "How [niche topic] changed my life in [timeframe]",
        "POV: You discover [niche result] for the first time",
    ])


def _generate_account_name_ideas(niche: str) -> list:
    name_parts = {
        "luxury lifestyle": ["luxury", "elite", "opulent", "prestige", "lavish"],
        "motivational / quotes": ["daily", "grind", "mindset", "elevate", "ascend"],
        "finance / wealth": ["wealth", "money", "finance", "capital", "rich"],
        "fitness / health": ["fit", "gains", "shred", "health", "physique"],
        "pet / animals": ["paws", "fur", "pets", "animals", "whiskers"],
        "tech / gadgets": ["tech", "gadget", "digital", "cyber", "geek"],
        "aesthetic / visual": ["aesthetic", "vibes", "curated", "visual", "mood"],
    }

    suffixes = ["hq", "daily", "hub", "world", "zone", "feeds", "official", "media"]
    parts = name_parts.get(niche, ["niche", "page", "hub"])

    ideas = []
    for p in parts[:3]:
        for s in suffixes[:3]:
            ideas.append(f"@{p}{s}")

    return ideas[:9]


def _generate_bio_template(niche: str) -> str:
    templates = {
        "luxury lifestyle": "✈️ Daily luxury inspiration\n💎 The finer things in life\n🔗 Shop our picks ↓",
        "motivational / quotes": "🔥 Daily motivation for go-getters\n📈 Mindset | Success | Growth\n👇 Free guide at link",
        "finance / wealth": "💰 Building wealth, one tip at a time\n📊 Finance | Investing | Freedom\n👇 Free wealth guide ↓",
        "fitness / health": "💪 Your daily fitness dose\n🥗 Health | Gains | Results\n👇 Free workout plan ↓",
        "pet / animals": "🐾 Making pet owners smile daily\n🐶🐱 Cute | Funny | Helpful\n👇 Best pet products ↓",
        "tech / gadgets": "⚡️ The coolest tech, daily\n🤖 Gadgets | AI | Innovation\n👇 Our top picks ↓",
        "aesthetic / visual": "🎨 Curated aesthetics, daily\n✨ Beauty | Vibes | Mood\n👇 Presets & more ↓",
    }
    return templates.get(niche, "🔥 Daily [niche] content\n📈 [Value prop]\n👇 [CTA] at link ↓")


def _get_starter_content(niche: str) -> list:
    """Return first 10 posts to create for a theme page."""
    return [
        {"post": 1, "type": "Introduction", "angle": "Welcome post — what this page is about and what to expect"},
        {"post": 2, "type": "Viral Repurpose", "angle": "Find the #1 most-viewed video in your niche and recreate your version"},
        {"post": 3, "type": "Value Drop", "angle": "Top [5] [niche] tips you wish someone told you earlier"},
        {"post": 4, "type": "Social Proof", "angle": "Before/after or result showcase (your niche topic)"},
        {"post": 5, "type": "Trending Sound", "angle": "Use today's #1 trending sound with your niche overlay"},
        {"post": 6, "type": "Myth Bust", "angle": "The biggest [niche] myth most people believe (and the truth)"},
        {"post": 7, "type": "Story Arc", "angle": "How [niche result] changed everything — personal or curated story"},
        {"post": 8, "type": "List Format", "angle": "10 things every [niche audience] needs to know"},
        {"post": 9, "type": "Engagement Bait", "angle": "Would you rather [A] or [B]? Comment below! (niche-relevant)"},
        {"post": 10, "type": "CTA Post", "angle": "Free [niche resource] at link in bio — tell them what it is and why to get it"},
    ]


def compare_niches(niche1: str, niche2: str) -> dict:
    """Side-by-side comparison of two theme page niches."""
    def find_niche(name):
        return next(
            (n for n in THEME_PAGE_NICHES if name.lower() in n["niche"].lower()),
            None,
        )

    n1 = find_niche(niche1)
    n2 = find_niche(niche2)

    if not n1:
        return {"error": f"Niche '{niche1}' not found. Available: {[n['niche'] for n in THEME_PAGE_NICHES]}"}
    if not n2:
        return {"error": f"Niche '{niche2}' not found. Available: {[n['niche'] for n in THEME_PAGE_NICHES]}"}

    conv_map = {"Very High": 5, "High": 4, "Medium-High": 3, "Medium": 2, "Low": 1}
    diff_map = {"Low": 1, "Medium": 2, "High": 3}

    n1_score = conv_map.get(n1["conversion_rate"], 1) - diff_map.get(n1["difficulty"], 2)
    n2_score = conv_map.get(n2["conversion_rate"], 1) - diff_map.get(n2["difficulty"], 2)

    winner = n1["niche"] if n1_score >= n2_score else n2["niche"]

    return {
        "comparison": {
            n1["niche"]: n1,
            n2["niche"]: n2,
        },
        "recommendation": winner,
        "reason": (
            f"{winner} wins on the opportunity score (conversion potential minus difficulty). "
            "That said, choose the niche you'd genuinely consume content in — authenticity "
            "still matters even for anonymous theme pages."
        ),
    }
