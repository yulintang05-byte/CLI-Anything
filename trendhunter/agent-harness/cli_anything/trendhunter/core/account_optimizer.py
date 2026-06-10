"""Account optimizer — posting schedules, hashtag strategy, bio optimization, and growth tactics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# Peak engagement windows by platform (UTC hour, audience type)
_POSTING_WINDOWS: dict[str, dict[str, list[tuple[int, str]]]] = {
    "tiktok": {
        "global": [
            (6,  "Morning burst — high scroll rate"),
            (10, "Mid-morning — commuters & students"),
            (14, "Afternoon lull — boredom scroll"),
            (19, "Prime time — highest engagement"),
            (22, "Night owls — long sessions"),
        ],
        "us_east": [
            (7,  "EST morning"),
            (12, "Lunch scroll"),
            (17, "After school/work"),
            (20, "Peak engagement window"),
            (23, "Late night"),
        ],
        "us_west": [
            (7,  "PST morning"),
            (12, "Lunch"),
            (17, "Post-work"),
            (20, "Prime time"),
            (22, "Night"),
        ],
    },
    "youtube": {
        "global": [
            (8,  "Early risers — before work"),
            (12, "Lunch break"),
            (17, "Post-school"),
            (20, "Prime time — peak views"),
            (22, "Late evening"),
        ],
        "shorts": [
            (7,  "Morning commute"),
            (12, "Lunch"),
            (16, "After school"),
            (19, "Evening"),
            (21, "Night"),
        ],
    },
    "instagram": {
        "global": [
            (6,  "Early morning"),
            (11, "Mid-morning"),
            (13, "Lunch"),
            (19, "Evening — top engagement"),
            (21, "Night"),
        ],
        "reels": [
            (7,  "Morning"),
            (11, "Late morning"),
            (15, "Afternoon"),
            (19, "Evening peak"),
            (22, "Night"),
        ],
    },
}

# Ideal frequency by platform (posts per week)
_IDEAL_FREQUENCY: dict[str, dict[str, int]] = {
    "tiktok":    {"starter": 1, "growing": 3, "scale": 5},
    "youtube":   {"starter": 2, "growing": 3, "scale": 5},
    "instagram": {"starter": 3, "growing": 5, "scale": 7},
    "youtube_shorts": {"starter": 3, "growing": 7, "scale": 14},
}

# Bio formulas by platform
_BIO_FORMULAS: dict[str, list[str]] = {
    "tiktok": [
        "[What you do] + [Result for viewer] + [CTA with link]",
        "[Niche emoji] [Core value prop in 1 line] | [Link CTA]",
        "Helping [audience] [achieve result] 👇 [link]",
        "[Attention hook] → [Proof] → [CTA]",
    ],
    "youtube": [
        "[Channel topic] • [Upload schedule] • [Subscribe CTA]",
        "We post [content type] every [day] | [Subscriber milestone]",
        "[Transformation promise] | New video every [frequency]",
    ],
    "instagram": [
        "[Who you are] | [What you share] | [CTA + link]",
        "[Niche] creator sharing [value] 📲 [link]",
        "[Hook line] ↓ [Proof/credibility] ↓ [Link CTA]",
    ],
}

# Engagement tactic playbook
_ENGAGEMENT_TACTICS: list[dict] = [
    {
        "tactic": "Reply to every comment in the first hour",
        "platforms": ["tiktok", "youtube", "instagram"],
        "impact": "high",
        "why": "Early engagement signals trigger algorithm boost",
    },
    {
        "tactic": "Ask a question in every caption/description",
        "platforms": ["tiktok", "youtube", "instagram"],
        "impact": "high",
        "why": "Increases comment rate by 3-5x",
    },
    {
        "tactic": "Pin your best comment on TikTok",
        "platforms": ["tiktok"],
        "impact": "medium",
        "why": "Drives conversation thread and retention",
    },
    {
        "tactic": "Reply to comments WITH another video (TikTok)",
        "platforms": ["tiktok"],
        "impact": "high",
        "why": "Video replies get distributed as new content",
    },
    {
        "tactic": "Post at the START of a trend, not the peak",
        "platforms": ["tiktok", "youtube"],
        "impact": "very_high",
        "why": "Early trend content gets massive organic reach",
    },
    {
        "tactic": "Use 3-5 hashtags max on TikTok (not 30)",
        "platforms": ["tiktok"],
        "impact": "high",
        "why": "Focused tags improve FYP targeting accuracy",
    },
    {
        "tactic": "Optimize first 1-3 seconds for retention",
        "platforms": ["tiktok", "youtube", "instagram"],
        "impact": "very_high",
        "why": "Watch time in first 3s determines 70% of distribution",
    },
    {
        "tactic": "Cross-post TikTok to YouTube Shorts (no watermark)",
        "platforms": ["tiktok", "youtube"],
        "impact": "high",
        "why": "Double distribution, zero extra work",
    },
    {
        "tactic": "Use trending sounds within 24-48h of appearance",
        "platforms": ["tiktok", "instagram"],
        "impact": "very_high",
        "why": "Trending sounds get extra algorithmic push",
    },
    {
        "tactic": "Duet/Stitch high-performing content",
        "platforms": ["tiktok"],
        "impact": "high",
        "why": "Piggybacks on existing viral distribution",
    },
    {
        "tactic": "Batch 7 videos per session, post over 7 days",
        "platforms": ["tiktok", "youtube"],
        "impact": "medium",
        "why": "Consistency signals quality to algorithm",
    },
    {
        "tactic": "Use pattern interrupts in thumbnails/covers",
        "platforms": ["youtube", "tiktok"],
        "impact": "high",
        "why": "CTR directly drives YouTube recommendation ranking",
    },
]


@dataclass
class AccountProfile:
    platform: str
    username: str = ""
    niche: str = ""
    followers: int = 0
    stage: str = "starter"   # starter | growing | scale
    timezone: str = "us_east"

    def to_dict(self) -> dict:
        return {
            "platform":  self.platform,
            "username":  self.username,
            "niche":     self.niche,
            "followers": self.followers,
            "stage":     self.stage,
            "timezone":  self.timezone,
        }


@dataclass
class OptimizationReport:
    profile: AccountProfile
    posting_schedule: list[dict] = field(default_factory=list)
    recommended_frequency: int = 3
    bio_formulas: list[str] = field(default_factory=list)
    hashtag_strategy: dict = field(default_factory=dict)
    engagement_tactics: list[dict] = field(default_factory=list)
    content_pillars: list[str] = field(default_factory=list)
    growth_estimate: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "profile":               self.profile.to_dict(),
            "posting_schedule":      self.posting_schedule,
            "recommended_frequency": self.recommended_frequency,
            "bio_formulas":          self.bio_formulas,
            "hashtag_strategy":      self.hashtag_strategy,
            "engagement_tactics":    self.engagement_tactics,
            "content_pillars":       self.content_pillars,
            "growth_estimate":       self.growth_estimate,
        }


def get_posting_schedule(platform: str, timezone: str = "us_east",
                          format_type: str = "regular") -> list[dict]:
    """Return optimal posting times for a platform + timezone."""
    plat = platform.lower().replace(" ", "_")
    if plat == "youtube_shorts" or format_type == "shorts":
        windows = _POSTING_WINDOWS.get("youtube", {}).get("shorts", [])
    else:
        windows = (
            _POSTING_WINDOWS.get(plat, {}).get(timezone)
            or _POSTING_WINDOWS.get(plat, {}).get("global")
            or []
        )

    days_by_priority = ["Tuesday", "Wednesday", "Thursday", "Friday",
                         "Monday", "Saturday", "Sunday"]
    schedule = []
    for i, (hour, note) in enumerate(windows):
        ampm  = "AM" if hour < 12 else "PM"
        h12   = hour % 12 or 12
        schedule.append({
            "time":     f"{h12}:00 {ampm}",
            "hour_utc": hour,
            "note":     note,
            "best_day": days_by_priority[i % len(days_by_priority)],
        })
    return schedule


def get_bio_formulas(platform: str) -> list[str]:
    """Return bio copy formulas for a platform."""
    return _BIO_FORMULAS.get(platform.lower(), _BIO_FORMULAS["tiktok"])


def get_engagement_tactics(platform: Optional[str] = None) -> list[dict]:
    """Return engagement tactics, optionally filtered by platform."""
    if platform is None:
        return _ENGAGEMENT_TACTICS
    plat = platform.lower()
    return [t for t in _ENGAGEMENT_TACTICS if plat in t["platforms"]]


def estimate_growth(followers: int, stage: str,
                    posts_per_week: int = 3) -> dict:
    """Rough growth estimate based on stage and posting frequency."""
    base_rates = {
        "starter": 0.05,   # 5% weekly growth when consistent
        "growing": 0.03,
        "scale":   0.01,
    }
    weekly_rate = base_rates.get(stage, 0.03)
    freq_mult = min(posts_per_week / 3.0, 2.0)  # cap at 2x
    effective_rate = weekly_rate * freq_mult

    return {
        "current_followers":      followers,
        "posts_per_week":         posts_per_week,
        "estimated_weekly_growth": f"{effective_rate*100:.1f}%",
        "in_4_weeks":             int(followers * (1 + effective_rate) ** 4),
        "in_3_months":            int(followers * (1 + effective_rate) ** 12),
        "in_6_months":            int(followers * (1 + effective_rate) ** 24),
        "key_driver":             "Consistency + trending sounds + early trend adoption",
    }


def get_content_pillars(niche: str) -> list[str]:
    """Generate the 4-5 content pillars for a niche account."""
    pillar_map: dict[str, list[str]] = {
        "fitness":     ["Workout tutorials", "Transformation progress", "Nutrition tips",
                        "Myth-busting", "Gear reviews"],
        "beauty":      ["GRWM (Get Ready With Me)", "Product reviews", "Tutorials",
                        "Before/after", "Trend recreations"],
        "fashion":     ["Outfit of the day", "Thrift hauls", "Style tips",
                        "Brand reviews", "Seasonal trends"],
        "food":        ["Quick recipes", "Restaurant reviews", "Ingredient guides",
                        "Cooking hacks", "Taste tests"],
        "finance":     ["Money tips", "Investing basics", "Income streams",
                        "Budget breakdowns", "Financial wins/fails"],
        "gaming":      ["Gameplay highlights", "Tips & tricks", "Game reviews",
                        "Reaction/commentary", "Tier lists"],
        "travel":      ["Destination guides", "Travel hacks", "Budget tips",
                        "Hidden gems", "Culture & food"],
        "motivation":  ["Daily mindset", "Success stories", "Quotes + commentary",
                        "Routines", "Challenge recaps"],
        "comedy":      ["Skits", "Reaction content", "Storytime", "Rants", "Relatable moments"],
        "education":   ["Did you know?", "How-to tutorials", "Explainers",
                        "Myth vs fact", "Study tips"],
        "tech":        ["Product reviews", "How-to", "AI/trends news",
                        "Setup tours", "Comparisons"],
        "business":    ["How I made $X", "Business tips", "Behind the scenes",
                        "Tool reviews", "Case studies"],
    }
    niche_lower = niche.lower()
    for key, pillars in pillar_map.items():
        if key in niche_lower or niche_lower in key:
            return pillars
    # Generic fallback pillars
    return [
        "Educational tips",
        "Behind the scenes",
        "Q&A / Community",
        "Trending topic commentary",
        "Personal story / Transformation",
    ]


def optimize_account(profile: AccountProfile) -> OptimizationReport:
    """Generate a full optimization report for an account profile."""
    report = OptimizationReport(profile=profile)

    report.posting_schedule    = get_posting_schedule(profile.platform, profile.timezone)
    report.recommended_frequency = _ideal_frequency(profile.platform, profile.stage)
    report.bio_formulas        = get_bio_formulas(profile.platform)
    report.engagement_tactics  = get_engagement_tactics(profile.platform)
    report.content_pillars     = get_content_pillars(profile.niche)
    report.growth_estimate     = estimate_growth(
        profile.followers, profile.stage, report.recommended_frequency
    )
    report.hashtag_strategy = {
        "formula": "30% mega + 30% mid + 30% niche + 10% branded",
        "total":   "3-5 on TikTok | 5-10 on Instagram | in-description on YouTube",
        "tip":     "Rotate hashtag sets every 2 weeks to avoid shadowban",
    }
    return report


def _ideal_frequency(platform: str, stage: str) -> int:
    """Posts per week based on platform and growth stage."""
    plat = platform.lower().replace(" ", "_")
    return _IDEAL_FREQUENCY.get(plat, {}).get(stage, 3)
