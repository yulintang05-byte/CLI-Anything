"""Theme page strategy — creation, growth, monetization, and conversion playbook.

A "theme page" is a niche content aggregation account that reposts/curates viral
content around a specific topic (e.g., @fitnessmotivation, @luxurycars, @quotes).
They can grow to 100k-1M+ followers in months and convert to significant income.
"""

from dataclasses import dataclass, field


# ── Niche viability matrix ────────────────────────────────────────────────────

NICHE_VIABILITY: dict[str, dict] = {
    "fitness": {
        "competition": "high",
        "monetization_ease": "high",
        "cpm_estimate": "$8-15",
        "audience_buying_power": "high",
        "content_availability": "abundant",
        "best_sub_niches": ["home_workout", "calisthenics", "female_fitness", "weight_loss_over_40"],
        "monetization_methods": ["affiliate (Amazon, supplements)", "digital products", "coaching upsell", "brand deals"],
    },
    "luxury_lifestyle": {
        "competition": "medium",
        "monetization_ease": "medium",
        "cpm_estimate": "$12-25",
        "audience_buying_power": "high",
        "content_availability": "abundant",
        "best_sub_niches": ["supercars", "watches", "private_jets", "mansions"],
        "monetization_methods": ["affiliate (luxury brands)", "dropshipping (luxury replicas)", "shoutouts", "brand deals"],
    },
    "motivation_quotes": {
        "competition": "very_high",
        "monetization_ease": "medium",
        "cpm_estimate": "$5-10",
        "audience_buying_power": "medium",
        "content_availability": "unlimited",
        "best_sub_niches": ["stoicism", "entrepreneur_mindset", "late_night_thoughts", "dark_academia"],
        "monetization_methods": ["digital products (ebooks)", "online courses", "affiliate", "print-on-demand merch"],
    },
    "animals_pets": {
        "competition": "medium",
        "monetization_ease": "medium",
        "cpm_estimate": "$6-12",
        "audience_buying_power": "medium",
        "content_availability": "abundant",
        "best_sub_niches": ["dogs", "cats", "exotic_pets", "wildlife", "rescue_stories"],
        "monetization_methods": ["pet product affiliate", "merch", "brand deals", "adsense"],
    },
    "food_recipes": {
        "competition": "high",
        "monetization_ease": "high",
        "cpm_estimate": "$8-18",
        "audience_buying_power": "medium",
        "content_availability": "abundant",
        "best_sub_niches": ["budget_meals", "5min_recipes", "keto_diet", "vegan", "mukbang"],
        "monetization_methods": ["recipe ebook", "cooking course", "kitchen affiliate", "brand deals"],
    },
    "finance_investing": {
        "competition": "medium",
        "monetization_ease": "very_high",
        "cpm_estimate": "$20-40",
        "audience_buying_power": "very_high",
        "content_availability": "medium",
        "best_sub_niches": ["crypto", "options_trading", "real_estate", "frugal_living", "side_hustles"],
        "monetization_methods": ["course sales", "newsletter", "affiliate (brokers/tools)", "paid community", "consulting"],
    },
    "gaming": {
        "competition": "very_high",
        "monetization_ease": "medium",
        "cpm_estimate": "$4-8",
        "audience_buying_power": "medium",
        "content_availability": "unlimited",
        "best_sub_niches": ["fortnite_clips", "minecraft", "mobile_gaming", "gaming_fails", "gaming_setup"],
        "monetization_methods": ["gaming affiliate (hardware)", "twitch subs", "brand deals", "merch"],
    },
    "travel": {
        "competition": "high",
        "monetization_ease": "medium",
        "cpm_estimate": "$10-20",
        "audience_buying_power": "high",
        "content_availability": "abundant",
        "best_sub_niches": ["budget_travel", "solo_female_travel", "luxury_travel", "van_life", "digital_nomad"],
        "monetization_methods": ["affiliate (hotels/gear)", "travel course", "ebook", "brand deals"],
    },
}

# ── Step-by-step playbooks ────────────────────────────────────────────────────

LAUNCH_PLAYBOOK: list[dict] = [
    {
        "phase": 1,
        "name": "Niche & Platform Selection",
        "days": "Day 1-2",
        "actions": [
            "Pick a niche with high content availability and clear monetization path",
            "Choose primary platform: TikTok (fastest growth) or Instagram (better monetization)",
            "Research 10 competitors — note their follower count, posting frequency, and content style",
            "Identify the gap: what are competitors NOT covering that the audience wants?",
            "Register handle (same name across all platforms — even if you don't use them yet)",
        ],
        "tools": ["Google Trends", "TikTok Search", "Instagram Explore"],
    },
    {
        "phase": 2,
        "name": "Account Setup & Branding",
        "days": "Day 2-3",
        "actions": [
            "Create a professional logo/icon (Canva free, Looka, or AI logo tools)",
            "Write bio: '[Niche] content daily | [benefit statement] | [CTA with link]'",
            "Set up Linktree or Stan Store as your bio link hub",
            "Create content pillars: 3-5 recurring content formats",
            "Design cover/banner template in Canva for visual consistency",
        ],
        "tools": ["Canva", "Linktree", "Stan Store", "Looka"],
    },
    {
        "phase": 3,
        "name": "Content Library Build",
        "days": "Day 3-7",
        "actions": [
            "Source 50+ pieces of viral content in your niche to repurpose",
            "Tools for sourcing: Pinterest, Reddit, Twitter, YouTube, TikTok Discover",
            "Edit clips for your platform: add your watermark/logo overlay",
            "Reframe titles/captions from your unique angle",
            "Schedule 2 weeks of content in advance using Buffer, Later, or TikTok scheduler",
        ],
        "tools": ["CapCut", "InShot", "Canva", "Buffer", "Later"],
    },
    {
        "phase": 4,
        "name": "Posting & Engagement Blitz",
        "days": "Week 1-4",
        "actions": [
            "Post 2-3 times/day minimum (TikTok) or 1 Reel + 3 Stories (Instagram)",
            "Engage with top accounts in your niche — comment thoughtfully to get their followers' attention",
            "Reply to EVERY comment on your posts within first hour",
            "Use trending sounds on every video",
            "Analyze insights after 48 hours — double down on formats that perform",
        ],
        "tools": ["Native analytics", "Social Blade"],
    },
    {
        "phase": 5,
        "name": "First 1K → 10K Growth Sprint",
        "days": "Month 1-3",
        "actions": [
            "Identify your best 5 posts — recreate them in different formats/angles",
            "Test different thumbnail/cover styles to increase CTR",
            "Cross-post: share TikToks to Instagram Reels (and vice versa)",
            "Collab with accounts at similar follower count for shoutout swaps",
            "Join engagement pods in your niche (Telegram/Discord groups)",
        ],
        "tools": ["Telegram pods", "TikTok analytics", "Instagram insights"],
    },
    {
        "phase": 6,
        "name": "Monetization Activation",
        "days": "At 5K-10K followers",
        "actions": [
            "Enable affiliate links (Amazon Associates, ShareASale, niche-specific programs)",
            "Create a simple digital product: ebook, template pack, or mini-course",
            "Start selling shoutouts ($25-$100 depending on niche/engagement)",
            "Apply for brand deals in your niche (direct outreach to small brands)",
            "Set up email list capture via lead magnet (free checklist, guide)",
        ],
        "tools": ["Gumroad", "Payhip", "Amazon Associates", "ConvertKit", "Mailchimp"],
    },
    {
        "phase": 7,
        "name": "Scaling & Automation",
        "days": "Month 3+",
        "actions": [
            "Hire a VA ($5-15/hr) to source and schedule content",
            "Build a content bank of 100+ posts to maintain consistency during travel/breaks",
            "Launch second account in adjacent niche (cross-promote)",
            "Create YouTube channel to repurpose long-form content for ad revenue",
            "Build email list to 1000+ subscribers for platform-independent audience",
        ],
        "tools": ["Upwork", "Fiverr", "Zapier for automation", "ConvertKit"],
    },
]

CONVERSION_STRATEGIES: list[dict] = [
    {
        "strategy": "Link in Bio Funnel",
        "description": "Drive followers to a Linktree/Stan Store with multiple CTAs",
        "conversion_rate": "1-5% of profile visitors click",
        "setup": [
            "Create Linktree with: Free gift → Email capture → Product page → DM contact",
            "Pin a post/video that says 'Link in bio for the free [resource]'",
            "Add 'link in bio' CTA verbally in every video",
        ],
    },
    {
        "strategy": "DM Automation Funnel",
        "description": "Use ManyChat to auto-send DMs when users comment a keyword",
        "conversion_rate": "10-30% of DM recipients convert",
        "setup": [
            "Create a ManyChat bot triggered by keyword (e.g., 'FREE')",
            "Post 'Comment FREE and I'll DM you my [resource]' as CTA",
            "DM sequence: resource → follow-up value → soft product offer",
        ],
        "tools": ["ManyChat", "Instagram DM Automations"],
    },
    {
        "strategy": "Lead Magnet → Email List",
        "description": "Offer a free resource in exchange for email address",
        "conversion_rate": "20-40% of landing page visitors opt in",
        "setup": [
            "Create PDF checklist, template, or mini-guide (Canva, 1-2 hours)",
            "Host on Beehiiv, ConvertKit, or Gumroad (free tier)",
            "Promote in every 3rd-4th post caption: 'Get my free [X] — link in bio'",
        ],
    },
    {
        "strategy": "Shoutout-for-Shoutout (SFS)",
        "description": "Trade shoutouts with accounts of similar size for mutual growth",
        "conversion_rate": "1-10% follower conversion per SFS",
        "setup": [
            "Find 5-10 accounts in your niche with similar follower count",
            "DM them: 'Hey! Love your content. Would you be up for a SFS this week?'",
            "Post a story/post recommending their account and ask them to do the same",
        ],
    },
    {
        "strategy": "Product in Comments",
        "description": "Answer niche questions in comments, mention your product naturally",
        "conversion_rate": "2-8% of engaged commenters",
        "setup": [
            "Find viral posts in your niche on Reddit/Twitter/TikTok",
            "Add genuinely helpful comment + 'I cover this in depth on my page'",
            "Never spam — provide value first, promote second",
        ],
    },
]


@dataclass
class ThemePagePlan:
    niche: str
    platform: str
    target_followers_90d: int = 10000
    monetization_goal: str = "affiliate"
    notes: list[str] = field(default_factory=list)

    def generate_roadmap(self) -> dict:
        viability = NICHE_VIABILITY.get(self.niche.lower().replace(" ", "_"), {})
        return {
            "niche": self.niche,
            "platform": self.platform,
            "target_followers_90d": self.target_followers_90d,
            "monetization_goal": self.monetization_goal,
            "niche_viability": viability,
            "phases": LAUNCH_PLAYBOOK,
            "conversion_strategies": CONVERSION_STRATEGIES[:3],
        }

    def to_dict(self) -> dict:
        return {
            "niche": self.niche,
            "platform": self.platform,
            "target_followers_90d": self.target_followers_90d,
            "monetization_goal": self.monetization_goal,
        }


def get_launch_playbook() -> list[dict]:
    return LAUNCH_PLAYBOOK


def get_conversion_strategies() -> list[dict]:
    return CONVERSION_STRATEGIES


def get_niche_viability(niche: str | None = None) -> dict:
    if niche:
        key = niche.lower().replace(" ", "_")
        result = NICHE_VIABILITY.get(key)
        if not result:
            # Fuzzy match
            for k, v in NICHE_VIABILITY.items():
                if niche.lower() in k or k in niche.lower():
                    return {k: v}
            return {"error": f"Niche '{niche}' not found", "available": list(NICHE_VIABILITY.keys())}
        return {key: result}
    return NICHE_VIABILITY


def list_niches() -> list[str]:
    return list(NICHE_VIABILITY.keys())
