"""Account optimization: posting times, bio, hashtags, engagement tactics."""

from datetime import datetime, time
from typing import Any


# Empirically established best-posting windows (UTC offsets provided separately)
BEST_POSTING_TIMES: dict[str, dict[str, list[str]]] = {
    "tiktok": {
        "Monday":    ["06:00", "10:00", "22:00"],
        "Tuesday":   ["02:00", "04:00", "09:00"],
        "Wednesday": ["07:00", "08:00", "23:00"],
        "Thursday":  ["09:00", "12:00", "19:00"],
        "Friday":    ["05:00", "13:00", "15:00"],
        "Saturday":  ["11:00", "19:00", "20:00"],
        "Sunday":    ["07:00", "08:00", "16:00"],
    },
    "youtube": {
        "Monday":    ["14:00", "15:00", "16:00"],
        "Tuesday":   ["14:00", "15:00", "16:00"],
        "Wednesday": ["14:00", "15:00", "16:00"],
        "Thursday":  ["12:00", "15:00", "16:00"],
        "Friday":    ["12:00", "14:00", "15:00"],
        "Saturday":  ["09:00", "10:00", "11:00"],
        "Sunday":    ["09:00", "10:00", "11:00"],
    },
    "instagram": {
        "Monday":    ["06:00", "11:00", "17:00"],
        "Tuesday":   ["09:00", "13:00", "18:00"],
        "Wednesday": ["07:00", "13:00", "20:00"],
        "Thursday":  ["08:00", "14:00", "18:00"],
        "Friday":    ["07:00", "12:00", "17:00"],
        "Saturday":  ["09:00", "11:00", "14:00"],
        "Sunday":    ["10:00", "13:00", "18:00"],
    },
}

NICHE_HASHTAG_LIMITS = {
    "tiktok": {"caption_limit": 2200, "recommended_hashtags": 5},
    "youtube": {"description_limit": 5000, "recommended_hashtags": 10},
    "instagram": {"caption_limit": 2200, "recommended_hashtags": 30},
}

PROFILE_CHECKLIST = {
    "tiktok": [
        "Profile photo: high-contrast, face-forward, 400×400+",
        "Bio: 80 chars max, include niche keyword + CTA (link in bio, DM for X)",
        "Username: short, memorable, searchable keyword if possible",
        "Pinned videos: 3 best-performing or hook videos",
        "Link in bio: Linktree or direct product/landing page",
        "TikTok LIVE: go live 2–3x/week for algorithmic boost",
        "Duet/Stitch: enable to allow community engagement",
        "Creator Account: switch to maximize analytics access",
    ],
    "youtube": [
        "Channel art: 2560×1440px, brand colors + niche visuals",
        "Profile photo: professional headshot or logo, 800×800px",
        "Channel description: first 100 chars must hook (shown in search)",
        "Channel keywords: 10–15 niche-relevant terms in settings",
        "Featured channels: related creators for credibility",
        "Custom URL: claim /c/yourname once eligible (100 subs)",
        "Sections: organize playlists by content pillar",
        "Thumbnails: A/B test with CTR-optimized designs (30%+ CTR target)",
        "End screens: 20 seconds, always include subscribe + video card",
        "Chapters: add timestamps to every video for search",
    ],
    "instagram": [
        "Bio: keyword in name field (not just username), niche + CTA",
        "Category: set business/creator category in settings",
        "Link in bio: Linktree with all monetization links",
        "Highlights: 5–8 permanent story highlights with branded covers",
        "Grid aesthetic: consistent color palette and posting style",
        "Reels priority: Instagram pushes Reels over static posts (post 4–7/week)",
        "Story polls/questions: daily story interactions boost reach",
        "Collab posts: use Collab feature with similar-size creators",
    ],
}

ENGAGEMENT_TACTICS: dict[str, list[str]] = {
    "tiktok": [
        "Hook in first 0.5 seconds — viewer retention is the #1 signal",
        "Reply to EVERY comment in first hour — algorithm rewards engagement velocity",
        "Use trending sounds (even briefly at start) for FYP boost",
        "Post 3 videos/day for first 30 days to find your hook style",
        "Stitch viral videos in your niche with your take",
        "Pin a comment with a CTA (follow for part 2, DM me)",
        "Go LIVE after posting to boost the video algorithmically",
        "Use text overlays — 40% of viewers watch without sound",
    ],
    "youtube": [
        "CTR goal: 4–10% (optimize thumbnail and title A/B test)",
        "AVD goal: >50% of video length (structure content to hold attention)",
        "First 30 seconds: state the exact value/promise of the video",
        "Pattern interrupt every 60–90 seconds (cut, zoom, graphic, music shift)",
        "End with a direct subscribe ask + related video card",
        "Community posts: post 3–5x/week on Community tab",
        "Comment bait: ask a specific question at end of video",
        "Shorts: cross-post clips as Shorts for algorithmic cross-promotion",
    ],
    "instagram": [
        "Reels: first 3 seconds must show the payoff, not the intro",
        "Carousel posts get 2–3x more reach — use for educational content",
        "DM new followers within 24 hours to build retention",
        "Story CTA: 'DM me X' outperforms link taps for engagement signal",
        "Collab with creators in 10–20% larger accounts",
        "Hashtag mix: 3 large (1M+), 3 medium (100K–1M), 3 small (<100K)",
        "Alt text: add keyword-rich alt text to every post",
        "Caption: 3–5 lines max before 'more' — lead with the hook",
    ],
}


class AccountOptimizer:
    """Generate optimization plans, posting schedules, and growth tactics."""

    # ------------------------------------------------------------------
    # Posting schedule
    # ------------------------------------------------------------------

    def get_best_posting_times(self, platform: str, timezone: str = "UTC") -> dict:
        """Return optimal posting windows for a platform."""
        schedule = BEST_POSTING_TIMES.get(platform.lower(), {})
        if not schedule:
            return {"error": f"No schedule data for platform: {platform}"}

        import pytz
        from datetime import timedelta
        try:
            tz = pytz.timezone(timezone)
            utc_offset = tz.utcoffset(datetime.utcnow())
            offset_hours = int(utc_offset.total_seconds() // 3600)
        except Exception:
            offset_hours = 0

        localized = {}
        for day, times in schedule.items():
            local_times = []
            for t in times:
                h, m = map(int, t.split(":"))
                local_h = (h + offset_hours) % 24
                local_times.append(f"{local_h:02d}:{m:02d}")
            localized[day] = local_times

        return {
            "platform": platform,
            "timezone": timezone,
            "schedule": localized,
            "note": "Times are your local timezone. Adjust ±1 hour for audience timezone.",
        }

    # ------------------------------------------------------------------
    # Profile optimization checklist
    # ------------------------------------------------------------------

    def get_profile_checklist(self, platform: str, niche: str | None = None) -> dict:
        checklist = PROFILE_CHECKLIST.get(platform.lower(), [])
        if not checklist:
            return {"error": f"No profile checklist for: {platform}"}

        niche_tips = []
        if niche:
            niche_tips = self._niche_specific_tips(platform, niche)

        return {
            "platform": platform,
            "niche": niche or "general",
            "checklist": checklist,
            "niche_specific_tips": niche_tips,
            "priority": "Complete top 3 items first — they have the highest impact on reach",
        }

    @staticmethod
    def _niche_specific_tips(platform: str, niche: str) -> list[str]:
        tips_map = {
            "fitness": [
                "Pin a transformation video as first pinned content",
                "Include specific niche in bio: 'Fat loss coach' > 'fitness creator'",
                "Before/after content has highest repost rate in this niche",
            ],
            "finance": [
                "Add disclaimers (not financial advice) — required and trust-building",
                "Case studies outperform generic advice: '0→$10K story'",
                "Green/red performance overlays on screen resonate strongly",
            ],
            "beauty": [
                "Use product tags in every post for shoppable content",
                "Tutorial format (step-by-step) drives saves — a key ranking signal",
                "Duet with beauty product UGC for viral amplification",
            ],
            "gaming": [
                "Clip highlights perform 3x better than full gameplay",
                "React to viral gaming moments for search discoverability",
                "Tournament/challenge participation for community engagement",
            ],
        }
        return tips_map.get(niche.lower(), [f"Research top 10 {niche} creators and reverse-engineer their pinned content strategy"])

    # ------------------------------------------------------------------
    # Hashtag optimizer
    # ------------------------------------------------------------------

    def optimize_hashtags(
        self,
        platform: str,
        niche: str,
        trending_hashtags: list[dict],
        niche_hashtags: list[str] | None = None,
    ) -> dict:
        """Build an optimized hashtag set for a post."""
        limits = NICHE_HASHTAG_LIMITS.get(platform.lower(), {"recommended_hashtags": 10})
        target = limits["recommended_hashtags"]

        trending = [h["hashtag"] for h in trending_hashtags[:target // 2]]
        niche_specific = (niche_hashtags or [])[:target // 3]
        universal = ["#fyp", "#viral", "#trending"] if platform == "tiktok" else ["#youtube", "#youtuber"]

        combined = list(dict.fromkeys(trending + niche_specific + universal))[:target]

        return {
            "platform": platform,
            "niche": niche,
            "recommended_hashtags": combined,
            "usage_tip": f"Use all {len(combined)} in {platform} post. Vary order each post to avoid shadow-filtering.",
            "limits": limits,
        }

    # ------------------------------------------------------------------
    # Bio generator
    # ------------------------------------------------------------------

    def generate_bio(self, platform: str, niche: str, handle: str, cta: str = "link in bio") -> dict:
        """Generate optimized bio copy for a platform."""
        templates = {
            "tiktok": f"🔥 {niche.title()} content daily\n💡 Tips, trends & more\n👇 {cta}",
            "youtube": f"{niche.title()} videos every week\nSubscribe for {niche} tips, trends & guides\n👇 {cta}",
            "instagram": f"✨ {niche.title()} creator\n📲 Daily {niche} content\n🔗 {cta}",
        }
        bio = templates.get(platform.lower(), f"{niche.title()} content creator | {cta}")
        return {
            "platform": platform,
            "handle": handle,
            "bio": bio,
            "char_count": len(bio),
            "tip": "Include a searchable keyword in your name field (not just @handle)",
        }

    # ------------------------------------------------------------------
    # Engagement tactics
    # ------------------------------------------------------------------

    def get_engagement_tactics(self, platform: str) -> dict:
        tactics = ENGAGEMENT_TACTICS.get(platform.lower(), [])
        return {
            "platform": platform,
            "tactics": tactics,
            "golden_rule": "Consistency + Engagement in first hour = algorithmic favor",
        }

    # ------------------------------------------------------------------
    # Full account audit report
    # ------------------------------------------------------------------

    def full_audit(self, platform: str, niche: str, handle: str) -> dict:
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "account": {"platform": platform, "handle": handle, "niche": niche},
            "profile_checklist": self.get_profile_checklist(platform, niche),
            "best_posting_times": self.get_best_posting_times(platform),
            "engagement_tactics": self.get_engagement_tactics(platform),
            "bio_suggestion": self.generate_bio(platform, niche, handle),
        }
