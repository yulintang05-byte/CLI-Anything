"""Theme page creation, conversion strategy, and monetization playbook.

A "theme page" is a niche-focused social account that curates, reposts,
and creates content around a specific topic/aesthetic. This module:
  - Provides step-by-step setup guides for any niche
  - Generates content calendars
  - Calculates monetization potential
  - Tracks conversion milestones (0→1K→10K→100K→1M)
  - Gives engagement pod strategies for early growth
"""

import json
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta, timezone
from typing import Optional


NICHES = {
    "fitness": {
        "content_pillars": ["workout tutorials", "progress photos", "nutrition tips", "motivation quotes", "gear reviews"],
        "reputable_sources": ["@nike", "@gymshark", "@menshealth", "r/fitness"],
        "posting_frequency": {"tiktok": 3, "youtube": 3, "instagram": 1},
        "monetization": ["fitness app affiliates", "supplement brands", "gym wear brands", "online coaching"],
        "avg_rpm_youtube": 3.50,
        "tiktok_creator_fund_rpm": 0.03,
    },
    "food": {
        "content_pillars": ["recipes", "restaurant reviews", "food challenges", "cooking hacks", "aesthetic plating"],
        "reputable_sources": ["@tasty", "@bonappetit", "@gordonramsay"],
        "posting_frequency": {"tiktok": 2, "youtube": 2, "instagram": 1},
        "monetization": ["kitchen affiliate", "meal kit sponsors", "cookware brands", "food delivery apps"],
        "avg_rpm_youtube": 5.00,
        "tiktok_creator_fund_rpm": 0.025,
    },
    "travel": {
        "content_pillars": ["destination guides", "travel hacks", "budget tips", "hidden gems", "gear reviews"],
        "reputable_sources": ["@lonelyplanet", "@natgeotravel"],
        "posting_frequency": {"tiktok": 2, "youtube": 1, "instagram": 1},
        "monetization": ["booking.com/hotels.com affiliate", "travel cards", "gear affiliate", "presets/LUTs"],
        "avg_rpm_youtube": 8.00,
        "tiktok_creator_fund_rpm": 0.02,
    },
    "finance": {
        "content_pillars": ["investing tips", "budgeting hacks", "passive income ideas", "stock picks", "crypto"],
        "reputable_sources": ["@grahamstephan", "@andrei jikh", "r/personalfinance"],
        "posting_frequency": {"tiktok": 2, "youtube": 2, "instagram": 1},
        "monetization": ["robinhood/webull/moomoo referrals", "credit card affiliates", "courses", "paid newsletter"],
        "avg_rpm_youtube": 18.00,
        "tiktok_creator_fund_rpm": 0.04,
    },
    "motivation": {
        "content_pillars": ["quotes", "success stories", "book summaries", "mindset tips", "habits"],
        "reputable_sources": ["@tonyrobbins", "@davidgoggins", "@jockowillink"],
        "posting_frequency": {"tiktok": 3, "youtube": 3, "instagram": 2},
        "monetization": ["book affiliates", "courses", "merch", "coaching calls"],
        "avg_rpm_youtube": 4.00,
        "tiktok_creator_fund_rpm": 0.03,
    },
    "beauty": {
        "content_pillars": ["makeup tutorials", "skincare routines", "product reviews", "GRWM", "drugstore dupes"],
        "reputable_sources": ["@nikkietutorials", "@jamescharles", "@hudabeauty"],
        "posting_frequency": {"tiktok": 2, "youtube": 2, "instagram": 1},
        "monetization": ["sephora affiliate", "brand deals", "LTK", "amazon storefront"],
        "avg_rpm_youtube": 6.00,
        "tiktok_creator_fund_rpm": 0.03,
    },
    "gaming": {
        "content_pillars": ["gameplay highlights", "tutorials", "reviews", "news", "funny moments"],
        "reputable_sources": ["@markiplier", "@pewdiepie", "@jacksepticeye"],
        "posting_frequency": {"tiktok": 3, "youtube": 4, "instagram": 1},
        "monetization": ["twitch subs", "gaming chair/PC affiliate", "game sponsorships", "merch"],
        "avg_rpm_youtube": 2.50,
        "tiktok_creator_fund_rpm": 0.02,
    },
    "fashion": {
        "content_pillars": ["outfit ideas", "style tips", "hauls", "brand reviews", "trend alerts"],
        "reputable_sources": ["@emilychamberlain", "@nzingaknights"],
        "posting_frequency": {"tiktok": 2, "youtube": 2, "instagram": 1},
        "monetization": ["LTK", "amazon storefront", "brand deals", "depop/poshmark"],
        "avg_rpm_youtube": 4.50,
        "tiktok_creator_fund_rpm": 0.025,
    },
}

MILESTONES = {
    "tiktok": [
        (0,       1_000,   "Foundation",    "Post 21 videos in 7 days. Use trending sounds. Hook in first 0.5s."),
        (1_000,   10_000,  "Early Growth",  "Duet 1 viral video/day. Reply to every comment. Post 3x/day."),
        (10_000,  100_000, "Momentum",      "Identify top 3 performing video formats. Double down. Collab with peers."),
        (100_000, 1_000_000,"Scale",        "Brand deal outreach. TikTok LIVE 3x/week. Series content for retention."),
        (1_000_000, None,  "Mega Creator",  "Diversify to YouTube/Instagram. Launch product/course. Management team."),
    ],
    "youtube": [
        (0,       100,     "Setup",         "Optimize channel art, trailer, and playlists. Post 8 videos in 30 days."),
        (100,     1_000,   "Foundation",    "3 videos/week. Focus on searchable topics. Build email list."),
        (1_000,   10_000,  "Monetization",  "Apply for YPP (1K subs + 4K watch hours). Affiliate links in descriptions."),
        (10_000,  100_000, "Growth",        "Shorts + long form balance. Community tab engagement. Collab series."),
        (100_000, None,    "Authority",     "Sponsors. Merchandise. Online course. Speaking. Book deal."),
    ],
}


@dataclass
class ThemePagePlan:
    niche: str
    platform: str
    current_followers: int
    current_milestone: str
    next_milestone: str
    milestone_actions: list[str]
    content_pillars: list[str]
    weekly_content_calendar: list[dict]
    content_sourcing_strategy: list[str]
    monetization_roadmap: list[str]
    monetization_potential_monthly: dict
    engagement_pod_strategy: list[str]
    account_branding_checklist: list[str]
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ThemePageConverter:
    """Full theme page conversion playbook for any niche."""

    def __init__(self):
        self._trending_hashtags: list[str] = []
        self._trending_sounds: list[dict] = []

    def set_trending_data(self, hashtags: list[str], sounds: list[dict]) -> None:
        self._trending_hashtags = hashtags
        self._trending_sounds = sounds

    def create_plan(
        self,
        niche: str,
        platform: str,
        current_followers: int = 0,
        page_name: str = "YourPage",
    ) -> ThemePagePlan:
        niche_data = NICHES.get(niche.lower(), NICHES["motivation"])
        milestones = MILESTONES.get(platform, MILESTONES["tiktok"])

        current_ms, next_ms, ms_actions = _get_milestone(milestones, current_followers)

        calendar = self._generate_calendar(niche, platform, niche_data)
        sourcing = self._sourcing_strategy(niche, niche_data)
        monetization_roadmap = self._monetization_roadmap(niche, niche_data, current_followers)
        revenue = self._estimate_revenue(niche_data, platform, current_followers)
        pod_strategy = _engagement_pod_strategy(platform)
        branding = _branding_checklist(platform, niche, page_name)

        return ThemePagePlan(
            niche=niche,
            platform=platform,
            current_followers=current_followers,
            current_milestone=current_ms,
            next_milestone=next_ms,
            milestone_actions=ms_actions,
            content_pillars=niche_data["content_pillars"],
            weekly_content_calendar=calendar,
            content_sourcing_strategy=sourcing,
            monetization_roadmap=monetization_roadmap,
            monetization_potential_monthly=revenue,
            engagement_pod_strategy=pod_strategy,
            account_branding_checklist=branding,
        )

    def get_conversion_guide(self, niche: str) -> dict:
        """Full step-by-step guide to convert ANY existing account into a theme page."""
        niche_data = NICHES.get(niche.lower(), NICHES["motivation"])
        return {
            "niche": niche,
            "phase_1_account_reset": [
                f"Change username to something niche-specific (e.g. @daily{niche}tips, @{niche}world)",
                "Update bio to clearly state your niche, posting schedule, and CTA",
                "Change profile picture to a clean logo or aesthetic image (Canva — free)",
                "Archive or delete off-niche content from existing account",
                "Set up a Linktree with links to all platforms + any products",
            ],
            "phase_2_content_strategy": [
                f"Choose 2-3 content pillars from: {', '.join(niche_data['content_pillars'])}",
                "Create 30 content ideas before you start posting (use ChatGPT if needed)",
                "Batch-film 10 videos in one day to get ahead of schedule",
                "Study top 10 accounts in your niche — copy the FORMAT not the content",
                "Use trending sounds within 48 hours of them going viral",
            ],
            "phase_3_growth_tactics": [
                "Follow 50-100 accounts in your niche daily (follow/unfollow strategy)",
                "Comment meaningfully on 20 viral posts in your niche each day",
                "Join 3-5 engagement pods (Telegram groups for your niche)",
                "Post during peak hours: " + str(_POSTING_SCHEDULE_SIMPLE(niche)),
                "Respond to ALL comments within 60 minutes of posting",
            ],
            "phase_4_monetization": niche_data["monetization"],
            "content_sourcing": [
                "Repost viral content (always credit original creator in caption)",
                "Use CapCut to edit + add your watermark to curated content",
                "Compile 'best of' roundups from niche creators",
                "Screenshot and explain trending memes/posts in your niche",
                "React/commentary videos to viral content in your space",
            ],
            "tools_needed": {
                "editing": ["CapCut (free)", "InShot (free)", "Canva (free tier)"],
                "scheduling": ["Later", "Buffer", "TikTok native scheduler"],
                "analytics": ["TikTok Analytics (built-in)", "YouTube Studio", "Social Blade"],
                "trend_finding": ["cli-anything-social-trends (this tool)", "Google Trends", "TikTok Discover"],
                "monetization": ["LTK (LikeToKnowIt)", "Amazon Associates", "ShareASale"],
            },
            "realistic_timeline": {
                "week_1-2": "0-500 followers — learning phase, testing content formats",
                "week_3-4": "500-2K followers — identifying what works, doubling down",
                "month_2-3": "2K-10K followers — consistent growth, first brand inquiries",
                "month_4-6": "10K-50K followers — monetization begins, $100-$1K/month",
                "month_7-12": "50K-200K followers — full-time income potential, $1K-$10K/month",
                "year_2+": "200K+ followers — brand deals, products, multiple revenue streams",
            },
            "common_mistakes_to_avoid": [
                "Posting inconsistently — algorithm punishes gaps > 3 days",
                "Ignoring comments — kills your engagement rate",
                "Copying content without adding value — gets flagged/removed",
                "Using all 30 hashtags with no strategy — dilutes reach",
                "Not using trending sounds — huge missed algorithm boost",
                "Switching niches mid-growth — resets your audience trust",
                "Buying followers — destroys engagement rate, useless for monetization",
            ],
        }

    def _generate_calendar(self, niche: str, platform: str, niche_data: dict) -> list[dict]:
        pillars = niche_data["content_pillars"]
        freq = niche_data["posting_frequency"].get(platform, 2)
        sounds = [s.get("title", "") for s in self._trending_sounds[:3]]
        calendar = []
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        post_days = days[:freq + 1] if freq <= 5 else days

        for i, day in enumerate(post_days):
            pillar = pillars[i % len(pillars)]
            sound = sounds[i % len(sounds)] if sounds else "trending sound of the week"
            tags = self._trending_hashtags[i*3:(i*3)+5]
            calendar.append({
                "day": day,
                "content_type": pillar,
                "sound": sound,
                "hashtags": [f"#{t}" for t in tags],
                "hook_idea": f"Hook: 'The {niche} secret nobody talks about...' or question format",
                "notes": "Film in good lighting. First 0.5 seconds must hook — no intros.",
            })
        return calendar

    def _sourcing_strategy(self, niche: str, niche_data: dict) -> list[str]:
        sources = niche_data.get("reputable_sources", [])
        return [
            f"Monitor {', '.join(sources)} daily for viral content to curate",
            f"Set Google Alerts for '{niche} viral' and '{niche} trending'",
            "Use Reddit r/" + niche.replace(" ", "") + " for grassroots content ideas",
            "Follow 200+ creators in your niche — your FYP/feed becomes a content engine",
            "Use cli-anything-social-trends to auto-scrape new trends daily",
            "Save viral content immediately with screen recording or SnapTik/SSSTik",
            "Always add your commentary, watermark, or unique angle when reposting",
        ]

    def _monetization_roadmap(self, niche: str, niche_data: dict, followers: int) -> list[str]:
        sources = niche_data.get("monetization", [])
        return [
            "PHASE 1 (0-1K followers): Affiliate links — Amazon Associates, LTK, ShareASale. No-cost, immediate.",
            f"PHASE 2 (1K-10K): Join Creator funds + pitch micro-brand deals for {niche} products",
            f"PHASE 3 (10K-50K): Charge $50-$200/post. Platforms: {', '.join(sources[:2])}",
            f"PHASE 4 (50K-200K): Premium sponsorships $200-$2K/post. Launch Linktree storefront.",
            f"PHASE 5 (200K+): $2K-$20K/post. Launch own product, course, or membership. Agency rep.",
        ]

    def _estimate_revenue(self, niche_data: dict, platform: str, followers: int) -> dict:
        rpm_yt = niche_data.get("avg_rpm_youtube", 4.0)
        rpm_tt = niche_data.get("tiktok_creator_fund_rpm", 0.03)
        # Estimate monthly views from follower count
        yt_views_per_month = followers * 0.15 * 4  # ~15% view rate, 4 videos/month
        tt_views_per_month = followers * 0.30 * 20  # ~30% reach, 20 posts/month

        yt_adsense = round(yt_views_per_month / 1000 * rpm_yt, 2)
        tt_fund = round(tt_views_per_month / 1000 * rpm_tt, 2)
        affiliate_est = round(followers * 0.001 * 5, 2)  # ~0.1% CTR, $5 avg commission
        brand_deals = 0
        if followers >= 10_000:
            brand_deals = round(followers / 10_000 * 100, 0)

        return {
            "platform": platform,
            "estimated_followers": followers,
            "youtube_adsense_monthly": f"${yt_adsense:,.2f}",
            "tiktok_creator_fund_monthly": f"${tt_fund:,.2f}",
            "affiliate_commissions_monthly": f"${affiliate_est:,.2f}",
            "brand_deals_monthly": f"${brand_deals:,.0f}",
            "total_estimated_monthly": f"${yt_adsense + tt_fund + affiliate_est + brand_deals:,.2f}",
            "note": "Estimates only. Actual revenue varies significantly by content quality and engagement.",
        }

    def to_json(self, plan: ThemePagePlan) -> str:
        return json.dumps(asdict(plan), indent=2, default=str)


# ── Pure helpers ──────────────────────────────────────────────────────────

def _get_milestone(milestones: list, followers: int) -> tuple[str, str, list[str]]:
    for i, (lo, hi, label, actions) in enumerate(milestones):
        hi = hi or float("inf")
        if lo <= followers < hi:
            current = f"{label} ({lo:,}–{int(hi):,} followers)" if hi != float("inf") else f"{label} ({lo:,}+ followers)"
            if i + 1 < len(milestones):
                _, next_hi, next_label, _ = milestones[i + 1]
                next_ms = f"{next_label} (reach {next_hi:,} followers)"
            else:
                next_ms = "Peak Tier — diversify revenue streams"
            return current, next_ms, actions.split(". ")
    return "Unknown", "Start posting", ["Post consistently", "Engage with community"]


def _engagement_pod_strategy(platform: str) -> list[str]:
    return [
        f"Join 3-5 Telegram engagement groups for {platform} creators in your niche",
        "Agree to: like, comment, and share within 30 minutes of each other's posts",
        "Do NOT join pods with >50 members — engagement becomes too thin",
        "Reciprocate every interaction — reliability keeps you in the pod",
        "Rotate pods every 3 months — platforms detect static engagement patterns",
        f"Find pods by searching '{platform} engagement group [niche]' on Telegram or Discord",
    ]


def _branding_checklist(platform: str, niche: str, page_name: str) -> list[str]:
    return [
        f"Username: @{page_name.lower().replace(' ','_')}_{niche[:5]} or @{niche[:8]}daily",
        "Profile photo: Clean, high-contrast logo or face (minimum 400x400px)",
        f"Bio line 1: What you post ('{niche.title()} tips & inspiration')",
        "Bio line 2: Posting schedule ('New content Mon/Wed/Fri')",
        "Bio line 3: CTA ('Follow for daily ' + niche + ' content')",
        "Bio link: Linktree with all platforms + affiliate/product links",
        "Content aesthetic: Pick 2-3 colors and stick to them (use Canva brand kit)",
        "Watermark: Add subtle logo/handle to every video (CapCut template)",
        "Highlight covers (Instagram): Consistent icon style in brand colors",
        "Banner/header (YouTube/Twitter): Professional design matching profile photo",
    ]


def _POSTING_SCHEDULE_SIMPLE(niche: str) -> str:
    s = _POSTING_HOURS.get(niche, _POSTING_HOURS["default"])
    return f"{s['days']} at {s['times']}"


_POSTING_HOURS = {
    "fitness":    {"days": "Mon/Wed/Fri/Sun", "times": "6am, 12pm, 5pm (local)"},
    "food":       {"days": "Tue/Thu/Sat/Sun", "times": "11am, 5pm, 8pm (local)"},
    "travel":     {"days": "Mon/Fri/Sat/Sun", "times": "7am, 1pm, 7pm (local)"},
    "tech":       {"days": "Mon-Thu",          "times": "9am, 3pm, 9pm (local)"},
    "beauty":     {"days": "Tue/Thu/Sat/Sun", "times": "10am, 4pm, 8pm (local)"},
    "gaming":     {"days": "Fri/Sat/Sun",      "times": "3pm, 7pm, 10pm (local)"},
    "motivation": {"days": "Mon/Wed/Fri",       "times": "6am, 7am, 5pm (local)"},
    "finance":    {"days": "Mon-Thu",           "times": "8am, 12pm, 6pm (local)"},
    "fashion":    {"days": "Tue/Thu/Sat",       "times": "10am, 3pm, 7pm (local)"},
    "comedy":     {"days": "Thu/Fri/Sat/Sun",   "times": "4pm, 8pm, 10pm (local)"},
    "default":    {"days": "Mon/Wed/Fri/Sat",   "times": "9am, 3pm, 8pm (local)"},
}
