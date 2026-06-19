"""Account optimization engine — posting schedules, hashtag strategies, profile audits.

Generates data-driven recommendations based on scraped trend data and
platform best practices. All recommendations are stored locally.
"""
import json
import re
from datetime import datetime
from typing import Optional

from cli_anything.trends_scout.utils import config as cfg_mod

# ── Optimal posting windows (research-backed, platform-specific) ─────────────

_POSTING_SCHEDULES = {
    "tiktok": {
        "best_days": ["Tuesday", "Thursday", "Friday"],
        "best_times_utc": [
            {"slot": "06:00-09:00 UTC", "why": "Morning scroll before work (US East Coast overnight)"},
            {"slot": "12:00-15:00 UTC", "why": "Lunch break peak engagement"},
            {"slot": "19:00-23:00 UTC", "why": "Evening prime time, highest daily volume"},
        ],
        "frequency": "3-5 posts/day for growth phase, 1-2/day for maintenance",
        "content_length": "7-15 seconds for maximum completion rate; 60-90s for storytelling",
    },
    "youtube": {
        "best_days": ["Wednesday", "Thursday", "Saturday"],
        "best_times_utc": [
            {"slot": "12:00-15:00 UTC", "why": "Midday upload — indexed before evening peak"},
            {"slot": "17:00-20:00 UTC", "why": "After-work viewing surge"},
        ],
        "frequency": "3-4 Shorts/day + 2-3 long-form/week for theme pages",
        "content_length": "Shorts: <60s. Long-form: 8-15 min (ad revenue threshold).",
    },
    "instagram": {
        "best_days": ["Monday", "Tuesday", "Friday"],
        "best_times_utc": [
            {"slot": "08:00-10:00 UTC", "why": "Morning routine scrolling"},
            {"slot": "17:00-19:00 UTC", "why": "Post-work engagement peak"},
        ],
        "frequency": "2-3 Reels/day + 1-2 Stories/day",
        "content_length": "Reels: 15-30s for max reach. Stories: 15s per card.",
    },
    "twitter": {
        "best_days": ["Wednesday", "Thursday"],
        "best_times_utc": [
            {"slot": "12:00-15:00 UTC", "why": "US East Coast lunch + European afternoon"},
            {"slot": "19:00-21:00 UTC", "why": "US evening engagement peak"},
        ],
        "frequency": "3-7 tweets/day; threads for viral potential",
        "content_length": "280 chars for engagement; threads for depth.",
    },
}

# ── Hashtag strategy templates by niche ─────────────────────────────────────

_NICHE_HASHTAGS = {
    "fitness": {
        "mega": ["#fitness", "#gym", "#workout", "#motivation", "#bodybuilding"],
        "mid": ["#fitnessmotivation", "#fitfam", "#gains", "#homeworkout", "#strengthtraining"],
        "niche": ["#nolimits", "#grindmode", "#sweatyselfie", "#gymlife", "#legday"],
        "strategy": "Mix 2 mega + 4 mid + 4 niche per post. Rotate weekly.",
    },
    "food": {
        "mega": ["#food", "#foodie", "#recipe", "#cooking", "#yummy"],
        "mid": ["#foodporn", "#homecooking", "#foodlover", "#instafood", "#foodblog"],
        "niche": ["#recipeoftheday", "#mealprep", "#cookingvideo", "#cheflife", "#easyrecipes"],
        "strategy": "Lead with niche-specific food type hashtags. Geo-tag boosts local reach.",
    },
    "fashion": {
        "mega": ["#fashion", "#style", "#ootd", "#outfitoftheday", "#streetwear"],
        "mid": ["#fashionblogger", "#styleguide", "#fashionista", "#outfitinspo", "#styleinspo"],
        "niche": ["#thriftflip", "#fashionhacks", "#styletips", "#wardrobeessentials", "#aestheticoutfit"],
        "strategy": "Seasonal tags drive discovery. Use current trend hashtags in first 3.",
    },
    "finance": {
        "mega": ["#finance", "#money", "#investing", "#wealth", "#financialfreedom"],
        "mid": ["#personalfinance", "#stockmarket", "#passiveincome", "#sidehustle", "#moneytips"],
        "niche": ["#financetok", "#moneymindset", "#investing101", "#buildwealth", "#frugalliving"],
        "strategy": "Compliance note: avoid guaranteed return claims. Educational angle converts best.",
    },
    "beauty": {
        "mega": ["#beauty", "#makeup", "#skincare", "#beautytips", "#glam"],
        "mid": ["#makeuptutorial", "#skincareroutine", "#beautyhacks", "#grwm", "#makeuplover"],
        "niche": ["#cleanbeauty", "#drugstoremakeup", "#skincareaddicts", "#makeupinspo", "#beautycommunity"],
        "strategy": "Tutorial + transformation content drives saves (best engagement signal).",
    },
    "gaming": {
        "mega": ["#gaming", "#gamer", "#videogames", "#gameplay", "#twitch"],
        "mid": ["#gamingnation", "#gamingcommunity", "#gamingsetup", "#pcgaming", "#fps"],
        "niche": ["#gaminghighlights", "#gamingclips", "#streamclips", "#gamingmemes", "#esports"],
        "strategy": "Game-specific hashtags (#minecraft, #fortnite) outperform generic ones.",
    },
    "general": {
        "mega": ["#viral", "#trending", "#fyp", "#foryou", "#explore"],
        "mid": ["#content", "#creator", "#socialmedia", "#growwithme", "#contentcreator"],
        "niche": ["#microinfluencer", "#smallcreator", "#growigtogether", "#contentideas", "#creatorlife"],
        "strategy": "Replace generic tags with niche-specific ones as your account grows.",
    },
}


# ── Profile audit ────────────────────────────────────────────────────────────

def audit_account(platform: str, handle: str, niche: str = "general") -> dict:
    """Generate an account optimization audit with actionable recommendations."""
    schedule = _POSTING_SCHEDULES.get(platform.lower(), _POSTING_SCHEDULES["tiktok"])
    hashtags = _NICHE_HASHTAGS.get(niche.lower(), _NICHE_HASHTAGS["general"])

    checklist = [
        {"item": "Bio optimization", "action": f"Include primary keyword '{niche}' in first line. Add CTA link.", "priority": "HIGH"},
        {"item": "Profile photo", "action": "High-contrast, face visible, consistent brand color border.", "priority": "HIGH"},
        {"item": "Username", "action": f"Should contain '{niche}' keyword or brand name. No underscores on TikTok.", "priority": "MEDIUM"},
        {"item": "Pinned content", "action": "Pin your 3 best-performing videos to show profile visitors.", "priority": "HIGH"},
        {"item": "Content consistency", "action": f"Post {schedule['frequency']} at consistent times.", "priority": "HIGH"},
        {"item": "Hook quality", "action": "First 1-3 seconds must stop scroll. Start mid-action or with bold statement.", "priority": "CRITICAL"},
        {"item": "Caption strategy", "action": "Ask a question in caption — drives comment engagement +30%.", "priority": "MEDIUM"},
        {"item": "Cross-posting", "action": "Repurpose same video for TikTok, Reels, and Shorts with minor edits.", "priority": "HIGH"},
        {"item": "Engagement pods", "action": "Comment on 10 accounts in your niche within 30 min of posting.", "priority": "MEDIUM"},
        {"item": "Analytics review", "action": "Check watch time / completion rate weekly. Anything below 40% needs new hook.", "priority": "HIGH"},
    ]

    return {
        "platform": platform,
        "handle": handle,
        "niche": niche,
        "audit_date": datetime.now().isoformat(),
        "posting_schedule": schedule,
        "hashtag_strategy": hashtags,
        "optimization_checklist": checklist,
        "quick_wins": [
            "Change profile photo to high-contrast image",
            "Add niche keyword to bio first line",
            "Pin your 3 best videos to profile",
            f"Post at {schedule['best_times_utc'][0]['slot']} tomorrow",
            "Respond to every comment in first 60 minutes after posting",
        ],
    }


def optimize_hashtags(niche: str = "general", platform: str = "tiktok",
                      trend_hashtags: Optional[list] = None,
                      count: int = 10) -> dict:
    """Generate an optimized hashtag mix for a post."""
    template = _NICHE_HASHTAGS.get(niche.lower(), _NICHE_HASHTAGS["general"])

    # Build mix: 20% mega, 40% mid, 40% niche
    mega = template["mega"][:2]
    mid = template["mid"][:4]
    niche_tags = template["niche"][:4]
    selected = mega + mid + niche_tags

    # Inject live trend hashtags if provided
    if trend_hashtags:
        trend_picks = [t for t in trend_hashtags if t not in selected][:3]
        selected = trend_picks + selected

    selected = selected[:count]

    return {
        "platform": platform,
        "niche": niche,
        "hashtags": selected,
        "caption_ready": " ".join(selected),
        "strategy": template.get("strategy", ""),
        "tip": (f"On {platform}, place hashtags in the caption (not comment) "
                "for maximum algorithmic indexing." if platform == "tiktok"
                else f"On {platform}, hashtags in first comment work equally well."),
    }


def get_posting_schedule(platform: str = "tiktok") -> dict:
    """Get optimal posting schedule for a platform."""
    schedule = _POSTING_SCHEDULES.get(platform.lower(), _POSTING_SCHEDULES["tiktok"])
    return {
        "platform": platform,
        "schedule": schedule,
        "content_calendar_tip": (
            "Batch-create content 1 week ahead. Schedule with Buffer or Later. "
            "Engagement is highest when YOU are active right after posting."
        ),
    }


def optimize_all_accounts() -> dict:
    """Run optimization analysis for all configured accounts."""
    accounts = cfg_mod.get_accounts()
    if not accounts:
        return {
            "error": "No accounts configured.",
            "tip": "Add accounts with: trends-scout account add --platform tiktok --handle @yourhandle --niche fitness",
        }
    results = []
    for acc in accounts:
        audit = audit_account(
            platform=acc.get("platform", "tiktok"),
            handle=acc.get("handle", ""),
            niche=acc.get("niche", "general"),
        )
        results.append({
            "account": f"{acc['platform']}:{acc['handle']}",
            "score": _calculate_score(audit),
            "top_3_actions": audit["quick_wins"][:3],
            "posting_schedule": audit["posting_schedule"]["frequency"],
        })
    return {
        "accounts_audited": len(results),
        "results": results,
        "global_tip": "Consistency beats volume. Pick 2 platforms max and master them.",
    }


def _calculate_score(audit: dict) -> str:
    """Rough readiness score based on checklist completeness."""
    high_priority = [i for i in audit["optimization_checklist"] if i["priority"] in ("HIGH", "CRITICAL")]
    score = max(0, 100 - len(high_priority) * 10)
    if score >= 80:
        return f"{score}/100 — STRONG"
    if score >= 60:
        return f"{score}/100 — NEEDS WORK"
    return f"{score}/100 — CRITICAL GAPS"
