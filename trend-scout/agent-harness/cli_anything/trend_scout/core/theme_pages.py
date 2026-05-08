"""Theme page strategy: how to create, grow, and monetize niche theme pages."""

from datetime import datetime
from typing import Any


PROFITABLE_NICHES = {
    "luxury_lifestyle": {
        "description": "Private jets, mansions, supercars, watches, travel",
        "monetization": ["Affiliate (luxury brands)", "Paid promos", "Dropshipping luxury goods"],
        "difficulty": "Low",
        "avg_rpm": "$15-$40",
        "best_platforms": ["Instagram", "TikTok", "YouTube"],
    },
    "motivation_mindset": {
        "description": "Success quotes, entrepreneur stories, mindset content",
        "monetization": ["Affiliate (courses, books)", "Paid promos", "Own course"],
        "difficulty": "Low",
        "avg_rpm": "$8-$20",
        "best_platforms": ["Instagram", "TikTok", "YouTube"],
    },
    "fitness_body": {
        "description": "Workout clips, transformations, gym culture, nutrition",
        "monetization": ["Supplement affiliate", "Paid promos", "Fitness program"],
        "difficulty": "Low-Medium",
        "avg_rpm": "$10-$25",
        "best_platforms": ["Instagram", "TikTok", "YouTube"],
    },
    "relationship_dating": {
        "description": "Dating advice, red flags, relationship psychology",
        "monetization": ["Dating app affiliate", "Coaching", "Ebook"],
        "difficulty": "Low",
        "avg_rpm": "$5-$15",
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
    },
    "travel_adventure": {
        "description": "Scenic destinations, travel hacks, budget travel, luxury travel",
        "monetization": ["Hotel/booking affiliate", "Travel cards", "Paid promos"],
        "difficulty": "Medium",
        "avg_rpm": "$12-$30",
        "best_platforms": ["Instagram", "TikTok", "YouTube"],
    },
    "food_recipes": {
        "description": "Recipe videos, restaurant reviews, food aesthetics",
        "monetization": ["Food delivery affiliate", "Cookbook", "Brand deals"],
        "difficulty": "Low",
        "avg_rpm": "$8-$18",
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
    },
    "finance_wealth": {
        "description": "Investing tips, side hustles, wealth building, crypto",
        "monetization": ["Brokerage affiliate", "Course", "Paid newsletter"],
        "difficulty": "Medium",
        "avg_rpm": "$20-$60",
        "best_platforms": ["YouTube", "TikTok", "Twitter"],
    },
    "animals_pets": {
        "description": "Cute animals, pet care, funny clips",
        "monetization": ["Pet supply affiliate", "Paid promos", "Merch"],
        "difficulty": "Very Low",
        "avg_rpm": "$5-$12",
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
    },
    "horror_mystery": {
        "description": "True crime, scary stories, paranormal, unsolved mysteries",
        "monetization": ["Podcast sponsorship", "Merchandise", "Patreon"],
        "difficulty": "Low",
        "avg_rpm": "$10-$22",
        "best_platforms": ["YouTube", "TikTok", "Instagram"],
    },
    "gaming_esports": {
        "description": "Gameplay clips, esports highlights, gaming news",
        "monetization": ["Gaming gear affiliate", "Twitch subs", "Sponsorship"],
        "difficulty": "Medium",
        "avg_rpm": "$8-$20",
        "best_platforms": ["YouTube", "TikTok", "Twitch"],
    },
}

CONTENT_SOURCING_METHODS = {
    "repost_with_credit": {
        "description": "Repost viral content from other creators with permission or credit",
        "pros": ["No filming required", "Proven content already performs", "Fast to scale"],
        "cons": ["Copyright risk if not careful", "Builds someone else's brand", "Lower engagement long-term"],
        "best_for": "Starting out (0-10K followers)",
        "tools": ["CapCut (edit + watermark removal)", "Canva (add your branding)", "SaveTok/SnapTok (download)"],
        "legal_tip": "Always credit original creator. DM for permission when possible. Use clips under 30s = safer.",
    },
    "curate_and_edit": {
        "description": "Download, edit, and add value before reposting (voiceover, text, music)",
        "pros": ["Your brand on content", "Higher perceived value", "Better engagement"],
        "cons": ["Requires basic editing skills", "More time per post"],
        "best_for": "10K-100K growth phase",
        "tools": ["CapCut", "Premiere Pro", "DaVinci Resolve (free)"],
    },
    "faceless_original": {
        "description": "Create original content without showing face (screen recordings, AI voiceover, animations)",
        "pros": ["Fully original", "Scales well", "Privacy maintained"],
        "cons": ["Requires more planning", "AI tools have learning curve"],
        "best_for": "Any stage — most scalable long-term",
        "tools": ["ElevenLabs (AI voice)", "Pictory (text-to-video)", "Canva", "CapCut", "Midjourney (images)"],
    },
    "ugc_aggregator": {
        "description": "Aggregate user-generated content (ask followers to submit, run challenges)",
        "pros": ["Community-driven", "Free content", "High authenticity"],
        "cons": ["Need audience first", "Quality control required"],
        "best_for": "50K+ accounts",
    },
}

CONVERSION_STRATEGIES = {
    "affiliate_link": {
        "description": "Earn commission promoting products in your niche",
        "platforms": ["Amazon Associates (1-10%)", "ShareASale", "Impact", "ClickBank", "LTK (LikeToKnow.it)"],
        "implementation": [
            "Sign up for affiliate program",
            "Get your unique tracking link",
            "Add to bio/Linktree",
            "Mention naturally in content: 'link in bio'",
            "Create dedicated product review videos",
        ],
        "earnings": "$0.01-$200+ per sale depending on product",
    },
    "brand_deals": {
        "description": "Partner with brands for sponsored content",
        "pricing_formula": "Nano: $10-$100/post | Micro: $100-$1K | Mid: $1K-$10K | Macro: $10K+",
        "how_to_get": [
            "Create a media kit (follower count, engagement rate, niche, demographics)",
            "Use Creator Marketplaces: TikTok Creator Marketplace, YouTube BrandConnect",
            "Sign up for Aspire, Grin, Influencer.co",
            "DM brands directly with your stats and a pitch",
            "Wait for inbounds once you hit 10K+ (they'll find you)",
        ],
        "negotiation_tips": [
            "Always counter: initial offer is rarely final",
            "Bundle platforms (TikTok + Instagram + YouTube = higher rate)",
            "Charge extra for exclusivity, usage rights, and reposts",
            "Get contracts in writing — protect yourself",
        ],
    },
    "digital_products": {
        "description": "Sell your own ebooks, templates, courses, presets",
        "products_by_niche": {
            "fitness": ["Workout plan PDF", "Meal prep guide", "Supplement stack ebook"],
            "finance": ["Budget template", "Investment tracker", "Side hustle guide"],
            "fashion": ["Style guide", "Capsule wardrobe template", "Outfit formula ebook"],
            "food": ["Recipe ebook", "Meal planning template"],
            "motivation": ["Goal-setting workbook", "Morning routine guide"],
        },
        "platforms": ["Gumroad (free to start)", "Stan.store", "Beacons.ai Shop", "Payhip", "Teachable"],
        "pricing_tip": "Start at $7-$27. Low price = more sales = more testimonials = can raise price",
    },
    "subscription_community": {
        "description": "Monthly recurring revenue from dedicated fans",
        "platforms": ["Patreon", "Discord (with paid roles)", "Substack", "TikTok LIVE Gifts", "YouTube Memberships"],
        "tiers": [
            "$5/mo: Access to exclusive content",
            "$15/mo: Monthly Q&A or live session",
            "$50/mo: 1-on-1 access or personalized advice",
        ],
        "requires": "Engaged audience — focus on free value first (usually 10K+ followers)",
    },
}


class ThemePageStrategist:
    """Generates comprehensive theme page creation and monetization strategies."""

    def get_theme_page_guide(self, niche: str = "") -> dict:
        """Return a complete guide to creating and monetizing a theme page."""
        return {
            "what_is_a_theme_page": self._explain_theme_pages(),
            "choosing_your_niche": self._niche_selection_guide(niche),
            "setup_checklist": self._setup_checklist(),
            "content_sourcing": CONTENT_SOURCING_METHODS,
            "growth_phases": self._growth_phases(),
            "monetization_methods": CONVERSION_STRATEGIES,
            "tools_stack": self._get_tools_stack(),
            "common_mistakes": self._common_mistakes(),
            "90_day_action_plan": self._ninety_day_plan(niche),
            "generated_at": datetime.utcnow().isoformat(),
        }

    def get_niche_analysis(self, niche: str) -> dict:
        """Return detailed analysis of a specific theme page niche."""
        niche_lower = niche.lower().replace(" ", "_")
        niche_data = PROFITABLE_NICHES.get(niche_lower, self._generic_niche(niche))
        return {
            "niche": niche,
            **niche_data,
            "account_names_formula": self._name_formulas(niche),
            "content_pillars": self._content_pillars(niche),
            "monetization_path": self._monetization_path(niche_data),
            "competitor_research": self._competitor_research_guide(niche),
            "estimated_timeline": self._estimate_timeline(niche_data.get("difficulty", "Medium")),
        }

    def get_all_profitable_niches(self) -> list[dict]:
        """Return all profitable theme page niches ranked by earning potential."""
        niches = []
        for key, data in PROFITABLE_NICHES.items():
            niches.append({
                "niche": key.replace("_", " ").title(),
                "difficulty": data["difficulty"],
                "avg_rpm": data["avg_rpm"],
                "best_platforms": data["best_platforms"],
                "description": data["description"],
                "top_monetization": data["monetization"][0],
            })
        def _max_rpm(rpm_str: str) -> int:
            import re as _re
            nums = _re.findall(r"\d+", rpm_str)
            return max(int(n) for n in nums) if nums else 0

        return sorted(niches, key=lambda x: _max_rpm(x["avg_rpm"]), reverse=True)

    def get_conversion_playbook(self, niche: str, followers: int = 0) -> dict:
        """Return a step-by-step monetization playbook based on follower count."""
        if followers < 1000:
            phase = "pre_monetization"
            strategy = {
                "focus": "Build audience first — monetizing too early kills growth",
                "actions": [
                    "Set up affiliate links now (earn from day 1 even with small audience)",
                    "Create a free lead magnet to build email list",
                    "Build Linktree/Beacons with affiliate links",
                    "Document your journey — this IS content",
                ],
                "monetization_to_avoid": "Paid promos — you have no leverage yet",
            }
        elif followers < 10_000:
            phase = "early_monetization"
            strategy = {
                "focus": "Affiliate + digital products",
                "actions": [
                    "Launch your first digital product ($7-$27)",
                    "Join 2-3 affiliate programs in your niche",
                    "DM micro-brands for gifted collabs (even unpaid builds portfolio)",
                    "Launch TikTok LIVE for gift revenue",
                ],
                "expected_monthly": "$50-$500",
            }
        elif followers < 100_000:
            phase = "scaling_monetization"
            strategy = {
                "focus": "Brand deals + own products + affiliate",
                "actions": [
                    "Create media kit and pitch 5 brands/week",
                    "Raise product prices (you have social proof now)",
                    "Launch a subscription community ($5-$15/mo)",
                    "Apply for YouTube Partner Program (1K subs + 4K watch hours)",
                ],
                "expected_monthly": "$500-$10,000",
            }
        else:
            phase = "full_monetization"
            strategy = {
                "focus": "Multiple revenue streams simultaneously",
                "actions": [
                    "Premium brand deals ($5K-$50K+ per post)",
                    "High-ticket course or coaching ($500-$5,000)",
                    "Merchandise line",
                    "Licensing your content",
                    "Speaking engagements",
                ],
                "expected_monthly": "$10,000-$100,000+",
            }

        return {
            "niche": niche,
            "follower_count": followers,
            "phase": phase,
            "strategy": strategy,
            "conversion_methods": CONVERSION_STRATEGIES,
            "generated_at": datetime.utcnow().isoformat(),
        }

    def get_account_conversion_checklist(self, from_type: str = "personal", to_type: str = "theme_page") -> dict:
        """Checklist for converting an existing account into a theme page."""
        return {
            "from": from_type,
            "to": to_type,
            "conversion_steps": [
                {
                    "step": 1,
                    "action": "Choose your niche",
                    "detail": "Pick ONE specific niche — not 'lifestyle', but 'luxury men's fashion under 30'",
                },
                {
                    "step": 2,
                    "action": "Archive or delete off-niche content",
                    "detail": "Any content that doesn't fit your new niche confuses the algorithm — archive first",
                },
                {
                    "step": 3,
                    "action": "Update profile completely",
                    "detail": "New username (if needed), niche-specific bio, relevant profile photo",
                },
                {
                    "step": 4,
                    "action": "Post 9 pieces of on-niche content immediately",
                    "detail": "9-grid strategy: your profile needs to look established when people visit",
                },
                {
                    "step": 5,
                    "action": "Set up monetization infrastructure",
                    "detail": "Linktree/Beacons with affiliate links, product pages, contact form",
                },
                {
                    "step": 6,
                    "action": "Commit to 30-day content blitz",
                    "detail": "Post 1-3x/day for 30 days — algorithm needs time to re-learn your niche",
                },
                {
                    "step": 7,
                    "action": "Engage aggressively in niche",
                    "detail": "Comment on top creators in your niche daily — be genuinely helpful",
                },
                {
                    "step": 8,
                    "action": "Track metrics weekly",
                    "detail": "Follower growth rate, reach, engagement rate, clicks to link",
                },
            ],
            "warning": "Expect a dip in reach for 1-2 weeks after switching niche — this is normal",
            "timeline": "30-90 days to see results from conversion",
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _explain_theme_pages(self) -> dict:
        return {
            "definition": "A theme page is a social media account built around a specific topic or aesthetic, not a personal brand. You don't show your face — you curate, create, or aggregate content around one niche.",
            "why_it_works": [
                "No personal brand required — anyone can run one",
                "Scales faster than personal brands (less friction to post)",
                "Can be sold for 24-36x monthly profit (high asset value)",
                "Multiple income streams from day one",
                "Can operate 100% faceless and anonymous",
            ],
            "examples": [
                "@cars.daily (Instagram) — 15M+ followers, car content, makes $50K+/mo",
                "@successvibes (Instagram) — motivation quotes, 8M followers",
                "@luxuryhouses (Instagram) — luxury real estate, affiliate income",
                "Anonymous finance TikTok pages — $10K+/mo from affiliate + courses",
            ],
            "vs_personal_brand": {
                "theme_page_pros": "No face, scalable, sellable, less personal risk",
                "personal_brand_pros": "Higher trust, better brand deals, easier to monetize at small scale",
                "recommendation": "Start with theme page → build personal brand once you understand what content performs",
            },
        }

    def _niche_selection_guide(self, niche: str = "") -> dict:
        if niche and niche.lower().replace(" ", "_") in PROFITABLE_NICHES:
            selected = PROFITABLE_NICHES[niche.lower().replace(" ", "_")]
            return {"selected_niche": niche, **selected, "verdict": "Good choice — profitable niche with clear monetization path"}

        return {
            "criteria": [
                "You can post about this daily without burning out",
                "There are products/services to promote (affiliate revenue)",
                "The niche has active communities on each platform",
                "High enough CPM/RPM for ads ($5+ RPM minimum)",
                "Content is easy to source (lots of shareable material exists)",
            ],
            "top_profitable_niches": [
                {"niche": n.replace("_", " ").title(), "rpm": d["avg_rpm"], "difficulty": d["difficulty"]}
                for n, d in list(PROFITABLE_NICHES.items())[:8]
            ],
            "avoid": [
                "Oversaturated without clear USP (generic quotes, generic memes)",
                "Niches with no monetization path",
                "Topics where you'd post legally risky content",
            ],
        }

    def _setup_checklist(self) -> list[dict]:
        return [
            {"task": "Choose niche and target audience", "priority": "MUST", "time": "1 day"},
            {"task": "Research top 10 accounts in chosen niche", "priority": "MUST", "time": "2 hours"},
            {"task": "Create accounts on TikTok + Instagram + YouTube", "priority": "MUST", "time": "1 hour"},
            {"task": "Set up Linktree or Beacons.ai", "priority": "MUST", "time": "30 min"},
            {"task": "Join 2 affiliate programs in your niche", "priority": "MUST", "time": "1 hour"},
            {"task": "Install CapCut for editing", "priority": "MUST", "time": "15 min"},
            {"task": "Create 9 pieces of content before going public", "priority": "MUST", "time": "2-3 days"},
            {"task": "Set up content calendar", "priority": "SHOULD", "time": "1 hour"},
            {"task": "Create branded watermark/logo in Canva", "priority": "SHOULD", "time": "30 min"},
            {"task": "Set up Google Sheets tracker for analytics", "priority": "SHOULD", "time": "1 hour"},
        ]

    def _growth_phases(self) -> list[dict]:
        return [
            {
                "phase": "Phase 1: Launch (0-1K)",
                "duration": "30-60 days",
                "focus": "Volume and testing",
                "daily_actions": ["Post 2-3x/day", "Engage 30 min/day in niche", "Study analytics daily"],
                "success_metric": "Find 1-2 content formats that outperform others",
            },
            {
                "phase": "Phase 2: Growth (1K-10K)",
                "duration": "2-6 months",
                "focus": "Consistency and optimization",
                "daily_actions": ["Post 1-2x/day (quality improving)", "Collaborate with similar accounts", "Expand to second platform"],
                "success_metric": "1-5% engagement rate, consistent weekly growth",
            },
            {
                "phase": "Phase 3: Scale (10K-100K)",
                "duration": "6-18 months",
                "focus": "Systems and monetization",
                "daily_actions": ["Post 1x/day (batch content weekly)", "Brand deals + affiliate promotion", "Build email list"],
                "success_metric": "$500-$5K monthly revenue",
            },
            {
                "phase": "Phase 4: Authority (100K+)",
                "duration": "Ongoing",
                "focus": "Multiple revenue streams",
                "daily_actions": ["Delegate content creation", "Focus on high-ticket monetization", "Consider selling account or building portfolio"],
                "success_metric": "$5K-$100K+ monthly revenue",
            },
        ]

    def _get_tools_stack(self) -> dict:
        return {
            "free_tools": [
                "CapCut — video editing + TikTok templates",
                "Canva — graphics, thumbnails, logos",
                "Beacons.ai — bio link + simple storefront",
                "Google Sheets — analytics tracking",
                "Notion — content calendar",
                "TikTok Creative Center — trend research (free)",
            ],
            "paid_tools_worth_it": [
                "Adobe Premiere Pro ($22/mo) — professional editing",
                "ElevenLabs ($5/mo) — AI voiceover for faceless content",
                "Pictory ($19/mo) — text-to-video",
                "Publer ($12/mo) — multi-platform scheduling",
                "Later ($16/mo) — Instagram + TikTok scheduling",
            ],
            "ai_tools": [
                "ChatGPT — caption writing, content ideas, scripts",
                "Claude — strategy, research, long-form content",
                "Midjourney — AI images for faceless content",
                "ElevenLabs — voice cloning/AI narration",
                "Runway ML — AI video generation",
            ],
        }

    def _common_mistakes(self) -> list[dict]:
        return [
            {"mistake": "Posting inconsistently", "fix": "Batch create content on Sunday, schedule for the week"},
            {"mistake": "Copying competitors without adding value", "fix": "Put your own spin: different hook, different angle, your commentary"},
            {"mistake": "Monetizing too early", "fix": "Wait until you have 1K+ engaged followers — build trust first"},
            {"mistake": "Ignoring analytics", "fix": "Check weekly: what got the most reach? Replicate it immediately"},
            {"mistake": "Too broad of a niche", "fix": "Niche down: not 'fitness' but 'home workouts for busy moms'"},
            {"mistake": "No CTA", "fix": "Every post needs an action: 'Follow', 'Save', 'Comment', 'Link in bio'"},
            {"mistake": "Quitting before 90 days", "fix": "Algorithm takes 30-90 days to understand new accounts — commit"},
            {"mistake": "Not building an email list", "fix": "Offer a freebie via Linktree to capture emails from day 1"},
        ]

    def _ninety_day_plan(self, niche: str) -> dict:
        return {
            "week_1-2": {
                "title": "Setup & Research",
                "tasks": [
                    f"Study top 20 {niche} accounts on TikTok + Instagram",
                    "Create all social accounts with optimized bios",
                    "Join 2 affiliate programs",
                    "Create first 9 pieces of content",
                    "Set up Linktree with affiliate links",
                ],
            },
            "week_3-4": {
                "title": "Launch & Volume",
                "tasks": [
                    "Post 2-3x/day on TikTok (test formats)",
                    "Post 1x/day on Instagram Reels",
                    "Engage 30 min/day in niche communities",
                    "Identify which content format performs best",
                ],
            },
            "month_2": {
                "title": "Double Down",
                "tasks": [
                    "Post more of what's working, cut what's not",
                    "Start posting on YouTube Shorts",
                    "Reach out to 5 brands for gifted collabs",
                    "Build content batching workflow",
                ],
            },
            "month_3": {
                "title": "Monetize & Scale",
                "tasks": [
                    "Launch first digital product or Patreon",
                    "Pitch 10 brands with media kit",
                    "Set up email list with free lead magnet",
                    "Evaluate: which platform is growing fastest? Double down there",
                    "Reinvest earnings into tools or outsourcing",
                ],
            },
            "success_metric": "By day 90: 1K-10K followers + first $100 earned",
            "niche": niche or "your chosen niche",
        }

    def _name_formulas(self, niche: str) -> list[str]:
        n = niche.lower()
        return [
            f"@{n}.daily",
            f"@the{n}page",
            f"@{n}empire",
            f"@{n}vibes",
            f"@best{n}clips",
            f"@{n}world",
            f"@{n}culture",
            f"@{n}lifestyle",
        ]

    def _content_pillars(self, niche: str) -> list[dict]:
        return [
            {"pillar": "Educational", "percentage": "30%", "example": f"'5 things about {niche} nobody tells you'"},
            {"pillar": "Inspirational", "percentage": "25%", "example": f"Success stories within {niche}"},
            {"pillar": "Entertaining", "percentage": "25%", "example": f"Funny/relatable {niche} moments"},
            {"pillar": "Trending", "percentage": "15%", "example": f"{niche} version of current trend/challenge"},
            {"pillar": "Promotional", "percentage": "5%", "example": "Soft affiliate mention or product review"},
        ]

    def _monetization_path(self, niche_data: dict) -> list[str]:
        methods = niche_data.get("monetization", ["Affiliate marketing", "Brand deals"])
        return [
            f"Month 1-2: Set up affiliate links ({methods[0] if methods else 'Amazon Associates'})",
            "Month 2-3: First brand gifted collab (even unpaid, for portfolio)",
            "Month 3-4: Launch first digital product ($7-$27)",
            "Month 4-6: Paid brand deals (once you have 5K+ followers + engagement proof)",
            "Month 6+: Scale with multiple revenue streams simultaneously",
        ]

    def _competitor_research_guide(self, niche: str) -> dict:
        return {
            "step_1": f"Search TikTok for #{niche} and sort by Most Liked",
            "step_2": "Find top 10 accounts — note their username, follower count, posting frequency",
            "step_3": "Identify their top 5 videos — what makes them work? Hook, format, sound?",
            "step_4": "Find gaps: what topics do they NOT cover that their audience would want?",
            "step_5": "Note what products/affiliates they promote — these convert in your niche",
            "tools": ["TikTok Creative Center (free)", "Socialinsider (paid)", "Phlanx (engagement calculator)"],
        }

    def _estimate_timeline(self, difficulty: str) -> dict:
        timelines = {
            "Very Low": {"first_1k": "7-30 days", "first_10k": "1-3 months", "first_income": "2-4 weeks"},
            "Low": {"first_1k": "14-45 days", "first_10k": "2-4 months", "first_income": "1-2 months"},
            "Low-Medium": {"first_1k": "30-60 days", "first_10k": "3-6 months", "first_income": "2-3 months"},
            "Medium": {"first_1k": "45-90 days", "first_10k": "4-8 months", "first_income": "2-4 months"},
            "High": {"first_1k": "60-120 days", "first_10k": "6-12 months", "first_income": "3-6 months"},
        }
        return timelines.get(difficulty, timelines["Medium"])

    def _generic_niche(self, niche: str) -> dict:
        return {
            "description": f"{niche} content for engaged audience",
            "monetization": ["Affiliate marketing", "Brand deals", "Digital products"],
            "difficulty": "Medium",
            "avg_rpm": "$5-$15",
            "best_platforms": ["TikTok", "Instagram", "YouTube"],
        }
