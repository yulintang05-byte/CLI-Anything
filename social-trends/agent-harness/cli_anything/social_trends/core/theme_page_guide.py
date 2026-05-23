"""Theme page guide — complete strategy for building and monetizing niche pages.

A "theme page" is a social media account built around a specific niche
(luxury, fitness, crypto, motivational, cars, etc.) that aggregates viral
content to build a large engaged following, then monetizes through multiple
revenue streams.

"Converting" = turning followers/viewers into revenue via shoutouts,
affiliate sales, DM funnels, brand deals, or flipping the account.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict


# ── High-Converting Niches ─────────────────────────────────────────────

HIGH_CONVERTING_NICHES = {
    "finance": {
        "name": "Finance / Make Money Online",
        "monetization_potential": "⭐⭐⭐⭐⭐",
        "difficulty": "Medium",
        "avg_rpm_usd": 8.50,
        "best_platforms": ["TikTok", "YouTube", "Instagram"],
        "example_handles": ["@yourrichbff", "@humphreytalks", "@andreijikh"],
        "content_types": ["tips", "explainers", "before/after", "reactions"],
        "shoutout_rate_per_post": "$200-800",
        "target_hashtags": ["#personalfinance", "#investing", "#stocks", "#moneytips", "#financetok"],
    },
    "luxury": {
        "name": "Luxury Lifestyle",
        "monetization_potential": "⭐⭐⭐⭐⭐",
        "difficulty": "Low-Medium",
        "avg_rpm_usd": 4.00,
        "best_platforms": ["Instagram", "TikTok", "YouTube"],
        "example_handles": ["@luxurylaunches", "@richkidsofinstagram"],
        "content_types": ["showcases", "aspirational", "reviews", "estate tours"],
        "shoutout_rate_per_post": "$300-1500",
        "target_hashtags": ["#luxury", "#luxurylifestyle", "#rich", "#billionaire", "#millionaire"],
    },
    "fitness": {
        "name": "Fitness / Body Transformation",
        "monetization_potential": "⭐⭐⭐⭐",
        "difficulty": "Medium",
        "avg_rpm_usd": 3.50,
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
        "example_handles": ["@cbum", "@andywarski"],
        "content_types": ["workouts", "transformations", "tips", "routines", "nutrition"],
        "shoutout_rate_per_post": "$100-500",
        "target_hashtags": ["#fitness", "#workout", "#gym", "#bodybuilding", "#fitnesstok"],
    },
    "motivation": {
        "name": "Motivation / Mindset",
        "monetization_potential": "⭐⭐⭐",
        "difficulty": "Low",
        "avg_rpm_usd": 2.00,
        "best_platforms": ["TikTok", "Instagram", "YouTube Shorts"],
        "example_handles": ["@motivationmafia", "@success.reminder"],
        "content_types": ["quotes", "speeches", "clips", "affirmations"],
        "shoutout_rate_per_post": "$50-200",
        "target_hashtags": ["#motivation", "#mindset", "#success", "#hustle", "#motivational"],
    },
    "crypto": {
        "name": "Crypto / Web3",
        "monetization_potential": "⭐⭐⭐⭐⭐",
        "difficulty": "High",
        "avg_rpm_usd": 12.00,
        "best_platforms": ["Twitter/X", "YouTube", "TikTok"],
        "example_handles": ["@coin_bureau", "@cryptosrus"],
        "content_types": ["analysis", "news", "NFT reviews", "project spotlights"],
        "shoutout_rate_per_post": "$500-5000",
        "target_hashtags": ["#crypto", "#bitcoin", "#ethereum", "#nft", "#web3"],
    },
    "cars": {
        "name": "Cars / Automotive",
        "monetization_potential": "⭐⭐⭐⭐",
        "difficulty": "Medium",
        "avg_rpm_usd": 5.00,
        "best_platforms": ["YouTube", "TikTok", "Instagram"],
        "example_handles": ["@supercarblondie", "@mrbeast_cars"],
        "content_types": ["reviews", "showcases", "mods", "meets", "stories"],
        "shoutout_rate_per_post": "$200-1000",
        "target_hashtags": ["#cars", "#supercar", "#automotive", "#carporn", "#carsoftiktok"],
    },
    "food": {
        "name": "Food / Recipes",
        "monetization_potential": "⭐⭐⭐",
        "difficulty": "Low",
        "avg_rpm_usd": 2.50,
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
        "example_handles": ["@thefoodbeast", "@gordonramsay"],
        "content_types": ["recipes", "mukbang", "restaurant reviews", "cooking tips"],
        "shoutout_rate_per_post": "$100-400",
        "target_hashtags": ["#foodtok", "#recipe", "#cooking", "#foodie", "#mukbang"],
    },
    "fashion": {
        "name": "Fashion / OOTD",
        "monetization_potential": "⭐⭐⭐⭐",
        "difficulty": "Low-Medium",
        "avg_rpm_usd": 3.00,
        "best_platforms": ["TikTok", "Instagram", "Pinterest"],
        "example_handles": ["@emmachamberlain", "@lexi_wood"],
        "content_types": ["ootd", "hauls", "styling tips", "brand reviews", "trend alerts"],
        "shoutout_rate_per_post": "$150-800",
        "target_hashtags": ["#fashion", "#ootd", "#style", "#outfitinspo", "#fashiontok"],
    },
}


# ── Strategy Models ────────────────────────────────────────────────────

@dataclass
class ThemePagePlan:
    niche: str
    niche_info: dict = field(default_factory=dict)
    phase_1_setup: list[str] = field(default_factory=list)
    phase_2_growth: list[str] = field(default_factory=list)
    phase_3_monetization: list[str] = field(default_factory=list)
    content_calendar: list[str] = field(default_factory=list)
    dm_scripts: list[str] = field(default_factory=list)
    account_valuation: str = ""
    red_flags_to_avoid: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


# ── Guide Generator ────────────────────────────────────────────────────

class ThemePageGuide:
    """Generate a complete theme page strategy for any niche."""

    def generate_plan(self, niche: str, current_followers: int = 0) -> ThemePagePlan:
        """Generate a comprehensive theme page plan.

        Args:
            niche: One of the keys in HIGH_CONVERTING_NICHES or any custom niche string.
            current_followers: Current follower count (0 = starting from scratch).
        """
        niche_key = niche.lower().replace(" ", "_")
        niche_info = HIGH_CONVERTING_NICHES.get(niche_key, self._generic_niche_info(niche))

        return ThemePagePlan(
            niche=niche,
            niche_info=niche_info,
            phase_1_setup=self._phase_1_setup(niche, niche_info),
            phase_2_growth=self._phase_2_growth(niche, niche_info),
            phase_3_monetization=self._phase_3_monetization(niche, niche_info, current_followers),
            content_calendar=self._content_calendar(niche_info),
            dm_scripts=self._dm_scripts(niche_info),
            account_valuation=self._valuation_formula(current_followers, niche_info),
            red_flags_to_avoid=self._red_flags(),
        )

    def _generic_niche_info(self, niche: str) -> dict:
        return {
            "name": niche.title(),
            "monetization_potential": "⭐⭐⭐",
            "difficulty": "Medium",
            "avg_rpm_usd": 2.50,
            "best_platforms": ["TikTok", "Instagram", "YouTube"],
            "example_handles": ["Research top accounts in this niche"],
            "content_types": ["educational", "entertainment", "trending"],
            "shoutout_rate_per_post": "$50-200",
            "target_hashtags": [f"#{niche.lower()}", f"#{niche.lower()}tok"],
        }

    def _phase_1_setup(self, niche: str, info: dict) -> list[str]:
        return [
            "── PHASE 1: SETUP (Days 1-7) ──",
            f"1. Choose handle: @[niche keyword]+[shortword] e.g. @financefix, @luxuryspot",
            f"2. Profile photo: Clean, high-contrast logo or aspirational niche image (no selfies for theme pages)",
            f"3. Bio formula: '{info['name']} 📍 | [value prop] | New content daily 🔥 | ↓ [CTA]'",
            f"4. Link in bio: Create Linktree/Stan Store with affiliate links + contact email",
            f"5. Username strategy: Include niche keyword for SEO (TikTok + YouTube search)",
            f"6. Study 10 top accounts in {niche} — reverse-engineer their top 3 posts",
            f"7. Create a content bank: Collect 30 pieces of viral {niche} content to repost",
            f"8. Set up Canva template: Consistent overlay/watermark branding for all posts",
            f"9. Best platforms for {niche}: {', '.join(info.get('best_platforms', ['TikTok']))}",
            f"10. Research copyright: Most viral repost niches are fine; avoid direct music/movie clips",
        ]

    def _phase_2_growth(self, niche: str, info: dict) -> list[str]:
        return [
            "── PHASE 2: GROWTH (Days 7-90) ──",
            "POSTING SCHEDULE: 2-3x/day TikTok; 1x/day Instagram Reels; 1-2x/day YouTube Shorts",
            "WEEK 1-2: Post 15-20 pieces of viral content — identify which formats your audience engages with most",
            "WEEK 3-4: Double down on your top 3 content formats. Eliminate low performers",
            "MONTH 2: Start Duet/Stitch strategy — piggyback on viral accounts in your niche",
            "MONTH 3: Begin collaborations with accounts similar size — cross-promote for free",
            "TREND RESPONSE: Have a 'content on call' workflow — post trend content within 2-4h of trend breaking",
            f"TOP CONTENT TYPES FOR {niche.upper()}: " + ", ".join(info.get("content_types", ["trending"])),
            "ENGAGEMENT RULE: Reply to every comment for first 30 minutes post-upload",
            "HASHTAG STACK: " + " ".join(info.get("target_hashtags", [])[:5]),
            "SAVE-BAIT: End videos with 'Save this for later' — saves are the #1 ranking signal",
            "GROWTH HACK: Comment on viral posts in your niche with value-add comments (not spam)",
            "CONSISTENCY CHECK: Miss 0 days for first 60 days — algorithm rewards streaks",
        ]

    def _phase_3_monetization(self, niche: str, info: dict, followers: int) -> list[str]:
        plans = [
            "── PHASE 3: MONETIZATION (From Day 30+) ──",
        ]
        shoutout_rate = info.get("shoutout_rate_per_post", "$50-200")

        # Always available
        plans += [
            f"1. AFFILIATE MARKETING (Start immediately at any size)",
            f"   - Sign up: Amazon Associates, ShareASale, Impact, ClickBank",
            f"   - Find {niche}-specific affiliate programs (Google: '{niche} affiliate program')",
            f"   - Add links to Linktree bio — earn 5-20% per sale passively",
            f"   - Estimated: $50-500/month at 1k-10k followers with right products",
        ]

        if followers >= 1_000 or followers == 0:
            plans += [
                f"2. SHOUTOUTS / PAID PROMOTIONS ({shoutout_rate}/post)",
                f"   - Post rates in bio: 'DM for promo rates'",
                f"   - Join shoutout groups: Instagram/Facebook creator marketplace groups",
                f"   - Message smaller accounts: 'I charge {shoutout_rate} for a 24h feature'",
                f"   - Offer bundle: 3 posts for 2x single rate",
                f"   - Use Shoutcart, Influencer.co, or direct DM outreach",
            ]

        if followers >= 5_000 or followers == 0:
            plans += [
                f"3. BRAND DEALS (5k+ followers)",
                f"   - Create a simple media kit (PDF): metrics, audience demographics, rates",
                f"   - Cold email brands in your niche: Subject line: 'Partnership Opportunity — {niche.title()} Page ({followers:,} engaged followers)'",
                f"   - Use: AspireIQ, Creator.co, Grapevine for brand connections",
                f"   - Rate card: 10k followers = ~$100-300/post (adjust per niche)",
            ]

        plans += [
            f"4. DIGITAL PRODUCTS (passive income)",
            f"   - Create a {niche} ebook/guide ($9-47) — takes 1 weekend",
            f"   - Sell on Gumroad, Stan Store, or Payhip",
            f"   - Drive sales via 'link in bio' CTA in every post",
            f"5. ACCOUNT FLIPPING",
            f"   - Build to 10k-50k engaged followers, then sell",
            f"   - {niche.title()} page valuations: 1-3x monthly revenue OR $1-3 per follower",
            f"   - List on: Flippa, FameSwap, PlayerUp",
            f"   - 10k follower account in high-value niche: $500-3,000",
            f"   - 100k follower account: $5,000-30,000+",
            f"6. DM FUNNEL",
            f"   - Broadcast value content to DMs via ManyChat/Instagram DM automations",
            f"   - Auto-DM anyone who comments a keyword (e.g., 'INFO') with your affiliate link",
            f"   - Converts at 5-15% when done with warm audiences",
        ]
        return plans

    def _content_calendar(self, info: dict) -> list[str]:
        content_types = info.get("content_types", ["educational", "trending", "entertainment"])
        return [
            "── WEEKLY CONTENT CALENDAR ──",
            "MONDAY: Educational/value post — 'Did you know...' or '5 tips for [niche]'",
            "TUESDAY: Trending audio/challenge — use #1 trending sound in your niche",
            "WEDNESDAY: Viral repost — find top performing content from last 7 days and put your spin on it",
            "THURSDAY: Behind-the-scenes / relatable — humanize the page",
            "FRIDAY: Entertainment/comedy — higher share rate on Fridays",
            "SATURDAY: Aspirational / motivational — save-bait, 'screenshot this' content",
            "SUNDAY: Community engagement — poll, Q&A, or 'which would you choose?'",
            "",
            "DAILY MINIMUM: 1 post + 30 min engaging with niche accounts",
            f"CONTENT SOURCES: Reddit (r/{info.get('name','niche').lower()}), Pinterest, Twitter trending, competitor posts",
            "TOOLS: CapCut (editing), Canva (graphics), Linktree (bio), Later (scheduling)",
        ]

    def _dm_scripts(self, info: dict) -> list[str]:
        rate = info.get("shoutout_rate_per_post", "$100")
        return [
            "── DM SCRIPTS FOR SELLING SHOUTOUTS ──",
            "",
            "Script 1 — Cold outreach to smaller accounts:",
            "  'Hey [name]! Love your content. I run a [niche] page with [X]k followers "
            "(ER [X]%). I offer paid features — your account gets seen by our engaged audience. "
            f"Starting at {rate}/post. Interested? I can send our media kit 🙏'",
            "",
            "Script 2 — Responding to inbound DMs:",
            f"  'Thanks for reaching out! Our current rate is {rate} for a 24h feed post "
            "(story add-on $[X]). Includes: dedicated post, custom caption, tagged credit. "
            "We post within 24h of payment. Payment via PayPal/CashApp/Venmo. "
            "Want to move forward?'",
            "",
            "Script 3 — Following up on no-response:",
            "  'Hey! Just following up on my last message about featuring your account on ours. "
            "We have a slot opening this week and wanted to give you first option. "
            "Let me know if you're interested!'",
            "",
            "Script 4 — Brand deal cold email subject:",
            "  'Partnership Inquiry: [Brand Name] x [Your Handle] — [Niche] Audience'",
            "",
            "Script 5 — Affiliate push via story/post:",
            "  'Swipe up / Link in bio for the [product] I use daily for [result]. "
            "Code [CODE] gets you [X]% off — deal ends [date]'",
        ]

    def _valuation_formula(self, followers: int, info: dict) -> str:
        rpm = info.get("avg_rpm_usd", 2.50)
        if followers <= 0:
            return (
                "Account Valuation Formula:\n"
                "  Method 1 — Revenue multiple: Monthly revenue × 12-24\n"
                "  Method 2 — Per follower: $1-3 per follower for engaged niche accounts\n"
                "  Method 3 — Earnings: (monthly views / 1000) × RPM × 12 × 12-24\n"
                f"  This niche RPM estimate: ${rpm:.2f}\n"
                "  Example: 50k followers, 500k views/month → $1,250/mo → sell for $15,000-30,000"
            )
        monthly_views_est = followers * 2  # conservative 2x views per follower per month
        monthly_revenue_est = (monthly_views_est / 1000) * rpm
        low_val = monthly_revenue_est * 12
        high_val = monthly_revenue_est * 24
        per_follower_low = followers * 1
        per_follower_high = followers * 3
        return (
            f"Your account ({followers:,} followers) estimated value:\n"
            f"  Revenue method: ${low_val:,.0f} – ${high_val:,.0f} (based on {monthly_views_est:,} est. views/mo)\n"
            f"  Per-follower method: ${per_follower_low:,.0f} – ${per_follower_high:,.0f}\n"
            f"  Recommended sale price: ${max(low_val, per_follower_low):,.0f} – ${max(high_val, per_follower_high):,.0f}\n"
            "  Where to sell: Flippa.com, FameSwap.com, PlayerUp.com"
        )

    def _red_flags(self) -> list[str]:
        return [
            "❌ NEVER buy fake followers — engagement rate tanks, brands won't pay",
            "❌ NEVER post copyrighted music/movie clips directly — DMCA strike kills account",
            "❌ NEVER use follow/unfollow bots — platform bans are permanent",
            "❌ NEVER accept payment outside agreed platform terms without due diligence",
            "❌ NEVER post adult content on a theme page unless on adult platforms",
            "❌ NEVER neglect analytics — check insights weekly to see what's working",
            "❌ NEVER ghost your audience — respond to comments for first 30 min post-post",
            "❌ NEVER post the same hashtag set every post — triggers spam filters",
            "❌ NEVER skip watermarking reposts — watermark protects your brand and attribution",
            "⚠️  ALWAYS have multiple monetization streams — single-stream accounts are fragile",
            "⚠️  ALWAYS disclose paid partnerships per FTC guidelines (#ad, #sponsored)",
            "⚠️  ALWAYS back up your content library and follower DM list externally",
        ]

    def list_niches(self) -> list[dict]:
        """Return all available niches with their metadata."""
        result = []
        for key, info in HIGH_CONVERTING_NICHES.items():
            result.append({
                "key": key,
                "name": info["name"],
                "monetization_potential": info["monetization_potential"],
                "difficulty": info["difficulty"],
                "best_platforms": info["best_platforms"],
                "shoutout_rate": info["shoutout_rate_per_post"],
            })
        return result
