"""Theme page strategy: niche selection, content sourcing, monetization, and conversion."""

from datetime import datetime
from typing import Any


NICHE_DATABASE: dict[str, dict] = {
    "motivation": {
        "description": "Inspirational quotes, success stories, mindset content",
        "audience": "18–35 entrepreneurs, students, self-improvement seekers",
        "monetization": ["brand deals (coaching apps, supplements)", "digital products (ebooks, planners)", "affiliate (Audible, courses)", "paid community"],
        "content_mix": {"quotes": 40, "reels_stories": 30, "personal_development": 20, "news": 10},
        "avg_cpm": "$8–15",
        "growth_rate": "high",
        "competition": "very high",
        "recommended_platforms": ["instagram", "tiktok", "youtube_shorts"],
        "top_accounts_example": ["@thegoodquote", "@dailymotivation", "@successmindset_official"],
    },
    "cars": {
        "description": "Supercars, JDM, modified vehicles, car culture",
        "audience": "16–40 male-skewed automotive enthusiasts",
        "monetization": ["brand deals (car brands, accessories)", "affiliate (AutoZone, car parts)", "merch", "car shows/events"],
        "content_mix": {"car_spotting": 35, "reviews": 25, "mods": 20, "news": 20},
        "avg_cpm": "$12–25",
        "growth_rate": "medium",
        "competition": "medium",
        "recommended_platforms": ["instagram", "youtube", "tiktok"],
        "top_accounts_example": ["@exoticsonIG", "@thesupercarblog"],
    },
    "fitness": {
        "description": "Workouts, nutrition, body transformation, gym culture",
        "audience": "18–45 health-conscious individuals",
        "monetization": ["brand deals (supplements, apparel)", "coaching/programs", "digital products", "affiliate (Amazon fitness gear)"],
        "content_mix": {"workout_videos": 40, "before_after": 20, "nutrition": 20, "tips": 20},
        "avg_cpm": "$15–30",
        "growth_rate": "high",
        "competition": "high",
        "recommended_platforms": ["instagram", "tiktok", "youtube"],
        "top_accounts_example": ["@cbum", "@jeffnippard"],
    },
    "anime": {
        "description": "Anime edits, clips, reviews, manga, cosplay",
        "audience": "13–28 anime fans",
        "monetization": ["merch (anime prints, figures)", "affiliate (Crunchyroll)", "brand deals (gaming peripherals)", "Patreon"],
        "content_mix": {"edits": 50, "reviews": 20, "news": 20, "memes": 10},
        "avg_cpm": "$5–10",
        "growth_rate": "very high",
        "competition": "very high",
        "recommended_platforms": ["tiktok", "instagram", "youtube_shorts"],
        "top_accounts_example": ["@animeindia", "@otakumemes_official"],
    },
    "finance": {
        "description": "Stock market, investing, crypto, personal finance, wealth building",
        "audience": "21–45 income earners wanting financial literacy",
        "monetization": ["sponsored content (brokers, fintech apps)", "courses", "affiliate (trading platforms)", "consulting"],
        "content_mix": {"market_updates": 30, "tips": 30, "case_studies": 25, "news": 15},
        "avg_cpm": "$25–60",
        "growth_rate": "high",
        "competition": "medium",
        "recommended_platforms": ["youtube", "tiktok", "twitter_x"],
        "top_accounts_example": ["@minoritymindset", "@grahamstephan"],
    },
    "food": {
        "description": "Recipes, restaurant reviews, mukbang, food travel",
        "audience": "18–55 food lovers, home cooks",
        "monetization": ["brand deals (food brands, kitchen tools)", "affiliate (Amazon kitchen)", "cookbooks", "meal kits"],
        "content_mix": {"recipes": 45, "restaurant_reviews": 25, "food_hacks": 20, "mukbang": 10},
        "avg_cpm": "$8–18",
        "growth_rate": "medium",
        "competition": "very high",
        "recommended_platforms": ["tiktok", "instagram", "youtube"],
        "top_accounts_example": ["@salt.fat.acid.heat", "@tasty"],
    },
    "luxury": {
        "description": "High-end fashion, watches, travel, lifestyle",
        "audience": "25–55 aspirational consumers and high-net-worth individuals",
        "monetization": ["brand deals (luxury brands)", "affiliate (high-ticket items)", "consulting", "events"],
        "content_mix": {"showcasing": 50, "reviews": 25, "lifestyle": 25},
        "avg_cpm": "$30–80",
        "growth_rate": "medium",
        "competition": "low-medium",
        "recommended_platforms": ["instagram", "youtube", "tiktok"],
        "top_accounts_example": ["@mrporter", "@hodinkee"],
    },
    "gaming": {
        "description": "Gameplay, reviews, esports, gaming news, streaming highlights",
        "audience": "13–30 gamers across PC, console, mobile",
        "monetization": ["Twitch/YouTube ad revenue", "brand deals (gaming peripherals)", "merch", "affiliate (game keys)"],
        "content_mix": {"highlights": 40, "tutorials": 25, "reviews": 20, "news": 15},
        "avg_cpm": "$5–12",
        "growth_rate": "high",
        "competition": "very high",
        "recommended_platforms": ["youtube", "tiktok", "twitch"],
        "top_accounts_example": ["@markiplier", "@mrbeast (gaming channel)"],
    },
}

CONTENT_SOURCING_METHODS = {
    "repost_with_credit": {
        "description": "Repost viral content from original creators with credit tag",
        "legality": "Gray area — always credit. Best practice: DM for permission",
        "effort": "low",
        "risk": "medium (DMCA if music/video copyrighted)",
        "tools": ["CapCut (add watermarks/logos)", "InShot", "Canva"],
    },
    "curated_quotes": {
        "description": "Create quote graphics from public domain or credited sources",
        "legality": "Legal if properly credited or using own designs",
        "effort": "low",
        "risk": "low",
        "tools": ["Canva", "Adobe Express", "Unfold"],
    },
    "original_edits": {
        "description": "Create original video edits using publicly available clips (with license)",
        "legality": "Legal if using licensed footage (Pexels, Pixabay) or fair use clips",
        "effort": "medium",
        "risk": "low",
        "tools": ["CapCut", "Premiere Pro", "DaVinci Resolve"],
    },
    "ugc_aggregation": {
        "description": "Aggregate user-generated content with creator permission",
        "legality": "Legal with explicit written permission",
        "effort": "medium",
        "risk": "low",
        "tools": ["DM templates", "Google Forms for permission"],
    },
    "ai_generated": {
        "description": "AI-generated images, voiceovers, and content",
        "legality": "Legal in most jurisdictions; disclose AI use per platform rules",
        "effort": "low-medium",
        "risk": "low",
        "tools": ["Midjourney", "ElevenLabs", "Sora", "Runway ML"],
    },
}

CONVERSION_STRATEGIES = {
    "lead_magnet": {
        "what": "Offer free value (ebook, template, checklist) in exchange for email",
        "cta": "'DM me FREE GUIDE' or link in bio → opt-in page",
        "conversion_rate": "3–8% of followers",
        "monetization_path": "Email list → product launches → recurring revenue",
    },
    "community": {
        "what": "Paid group (Discord, Telegram, Circle) for exclusive content + community",
        "cta": "Join our premium community — link in bio",
        "conversion_rate": "0.5–2% of followers",
        "monetization_path": "$15–50/month/member",
    },
    "digital_products": {
        "what": "Sell downloadable products (presets, templates, courses, ebooks)",
        "cta": "Get my [niche] pack — link in bio",
        "conversion_rate": "1–5% of followers",
        "monetization_path": "$10–500 per sale, Gumroad/Stan Store",
    },
    "affiliate": {
        "what": "Promote products and earn commission on sales",
        "cta": "Shop my favorites at [link]",
        "conversion_rate": "2–10% click-through, 1–5% purchase",
        "monetization_path": "Amazon Associates (4–8%), ShareASale, Impact",
    },
    "brand_deals": {
        "what": "Paid partnerships with brands in your niche",
        "cta": "N/A — brands reach out or you pitch via email",
        "conversion_rate": "Requires 10K+ followers (micro-influencer tier starts here)",
        "monetization_path": "$100–$500 per post at 10K; $1K–5K at 100K",
    },
    "creator_fund": {
        "what": "Platform native monetization (TikTok Creator Rewards, YT Partner Program)",
        "cta": "N/A — automatic after eligibility",
        "conversion_rate": "Requires 10K followers + 100K views/month (TikTok); 1K subs + 4K hours (YT)",
        "monetization_path": "TikTok: $0.02–0.04/1K views; YT: $2–15 CPM",
    },
}

GROWTH_ROADMAP = [
    {"phase": "0–1K", "focus": "Niche selection + content style testing (post 2–3x/day)", "goal": "Find your hook format"},
    {"phase": "1K–10K", "focus": "Double down on top 3 performing content types", "goal": "Establish content pillars"},
    {"phase": "10K–50K", "focus": "Add first monetization (affiliate + lead magnet)", "goal": "First dollar from content"},
    {"phase": "50K–100K", "focus": "Launch digital product or community", "goal": "$1K–5K/month recurring"},
    {"phase": "100K+", "focus": "Brand deals + course launch + team/VA for content", "goal": "$10K+/month"},
]


class ThemePageStrategy:
    """Complete theme page creation, conversion, and monetization guide."""

    # ------------------------------------------------------------------
    # Niche guide
    # ------------------------------------------------------------------

    def get_niche_guide(self, niche: str) -> dict:
        data = NICHE_DATABASE.get(niche.lower())
        if not data:
            available = list(NICHE_DATABASE.keys())
            return {"error": f"Niche '{niche}' not found. Available: {available}"}

        return {
            "niche": niche,
            **data,
            "launch_checklist": self._launch_checklist(niche, data),
            "first_30_days": self._first_30_days_plan(niche, data),
        }

    @staticmethod
    def _launch_checklist(niche: str, data: dict) -> list[str]:
        return [
            f"Choose primary platform: {data['recommended_platforms'][0]}",
            f"Set username: keyword-rich (e.g., @daily{niche}, @{niche}facts, @{niche}viral)",
            "Create 9–12 pieces of content BEFORE posting (content buffer)",
            "Design brand kit: 2 fonts, 3 colors, logo variant",
            "Optimize profile with niche keyword in bio name field",
            "Research top 20 accounts in niche — note their top posts",
            "Build content calendar for first 30 days",
            f"Join {niche} creator communities (Reddit, Discord, Facebook Groups)",
        ]

    @staticmethod
    def _first_30_days_plan(niche: str, data: dict) -> list[dict]:
        return [
            {"days": "1–7", "action": "Post 2–3x/day. Test 3 different content formats. No monetization."},
            {"days": "8–14", "action": "Identify top-performing format. Double down. Start engaging in comments of top creators."},
            {"days": "15–21", "action": "Collaborate/duet with similar accounts. Add first CTA: 'Follow for daily [niche]'."},
            {"days": "22–30", "action": "Analyze analytics. Double winner content type. Set up lead magnet if at 500+ followers."},
        ]

    # ------------------------------------------------------------------
    # Content sourcing guide
    # ------------------------------------------------------------------

    def get_content_sourcing_guide(self, budget: str = "zero") -> dict:
        """Return content sourcing methods appropriate for budget level."""
        if budget == "zero":
            methods = ["repost_with_credit", "curated_quotes", "ai_generated"]
        elif budget == "low":
            methods = ["curated_quotes", "original_edits", "ai_generated", "ugc_aggregation"]
        else:
            methods = list(CONTENT_SOURCING_METHODS.keys())

        return {
            "budget": budget,
            "methods": {k: CONTENT_SOURCING_METHODS[k] for k in methods},
            "recommended_workflow": self._content_workflow(budget),
        }

    @staticmethod
    def _content_workflow(budget: str) -> list[str]:
        zero_budget = [
            "1. Find top 10 viral posts in niche (TikTok search, YouTube trending)",
            "2. Download with SnapTik/SSSTikTok (no watermark) or YouTube-dl",
            "3. Re-edit in CapCut: add your logo, text overlay, different music",
            "4. Always tag original creator in caption",
            "5. Post on your branded account",
        ]
        if budget == "zero":
            return zero_budget
        return zero_budget + [
            "6. Commission original graphics on Fiverr ($5–15)",
            "7. Record voiceovers with ElevenLabs AI for professional audio",
            "8. Use Midjourney for unique AI thumbnails",
        ]

    # ------------------------------------------------------------------
    # Conversion and monetization plan
    # ------------------------------------------------------------------

    def get_conversion_plan(self, niche: str, follower_count: int) -> dict:
        niche_data = NICHE_DATABASE.get(niche.lower(), {})
        niche_monetization = niche_data.get("monetization", [])

        if follower_count < 1000:
            stage = "pre-monetization"
            strategies = ["creator_fund"]
        elif follower_count < 10000:
            stage = "early"
            strategies = ["affiliate", "lead_magnet"]
        elif follower_count < 100000:
            stage = "growth"
            strategies = ["affiliate", "digital_products", "lead_magnet", "community"]
        else:
            stage = "established"
            strategies = list(CONVERSION_STRATEGIES.keys())

        estimated_monthly = self._estimate_revenue(follower_count, niche_data.get("avg_cpm", "$5–10"))

        return {
            "niche": niche,
            "follower_count": follower_count,
            "stage": stage,
            "recommended_strategies": {k: CONVERSION_STRATEGIES[k] for k in strategies},
            "niche_brand_deal_niches": niche_monetization,
            "estimated_monthly_revenue": estimated_monthly,
            "growth_roadmap": GROWTH_ROADMAP,
        }

    @staticmethod
    def _estimate_revenue(followers: int, cpm_range: str) -> str:
        if followers < 1000:
            return "$0 (grow first)"
        if followers < 10000:
            return "$50–200/month (affiliate only)"
        if followers < 100000:
            return "$200–2,000/month (affiliate + digital products)"
        if followers < 500000:
            return "$2,000–10,000/month (brand deals + products)"
        return "$10,000–50,000+/month (full creator business)"

    # ------------------------------------------------------------------
    # Platform comparison for theme pages
    # ------------------------------------------------------------------

    def platform_comparison(self, niche: str) -> dict:
        niche_data = NICHE_DATABASE.get(niche.lower(), {})
        recommended = niche_data.get("recommended_platforms", ["tiktok", "instagram", "youtube"])

        comparison = {
            "tiktok": {
                "growth_speed": "fastest (can go viral with 0 followers)",
                "algorithm": "content-first (FYP serves to non-followers)",
                "monetization_entry": "10K followers + 100K views",
                "best_for": "short-form viral content, trends, sounds",
                "posting_frequency": "1–4/day",
            },
            "youtube": {
                "growth_speed": "slow (SEO-dependent, 6–12 months to momentum)",
                "algorithm": "intent-based (search + suggested)",
                "monetization_entry": "1K subs + 4K watch hours",
                "best_for": "long-form tutorials, reviews, education",
                "posting_frequency": "2–4/week",
            },
            "instagram": {
                "growth_speed": "medium (Reels get FYP-like reach)",
                "algorithm": "mixed (Reels = content-first; feed = follower-based)",
                "monetization_entry": "varies by method",
                "best_for": "visual brand building, product showcasing, Reels",
                "posting_frequency": "1/day feed + 5–7 stories/day",
            },
        }

        return {
            "niche": niche,
            "recommended_order": recommended,
            "platform_details": {p: comparison.get(p, {}) for p in recommended},
            "multi_platform_tip": "Cross-post the same content across all 3 platforms with minor tweaks. TikTok → Instagram Reels → YouTube Shorts.",
        }

    # ------------------------------------------------------------------
    # Theme page conversion guide (the full playbook)
    # ------------------------------------------------------------------

    def full_playbook(self, niche: str) -> dict:
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "niche_guide": self.get_niche_guide(niche),
            "content_sourcing": self.get_content_sourcing_guide("zero"),
            "conversion_plan_10k": self.get_conversion_plan(niche, 10000),
            "platform_comparison": self.platform_comparison(niche),
            "tools": self._recommended_tools(),
        }

    @staticmethod
    def _recommended_tools() -> dict:
        return {
            "content_creation": ["CapCut (mobile/desktop)", "Canva Pro", "InShot", "Lightroom Mobile"],
            "scheduling": ["Later", "Buffer", "Metricool", "TikTok built-in scheduler"],
            "analytics": ["Social Blade", "HypeAuditor", "TikTok Analytics", "YouTube Studio"],
            "monetization": ["Stan Store", "Gumroad", "Beacons.ai", "Linktree Pro"],
            "trend_research": ["TikTok Discover page", "YouTube Trending", "Google Trends", "cli-anything-social-trend-scout"],
            "ai_tools": ["ChatGPT (captions/scripts)", "ElevenLabs (voiceover)", "Midjourney (thumbnails)", "Descript (editing)"],
        }
