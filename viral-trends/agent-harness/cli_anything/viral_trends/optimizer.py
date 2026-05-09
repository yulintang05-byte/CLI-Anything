"""Account optimization recommendations engine."""
from __future__ import annotations
from typing import Any


# Best posting windows by platform (UTC hour ranges)
_OPTIMAL_HOURS = {
    "tiktok":   [(6, 10), (12, 15), (19, 23)],
    "youtube":  [(14, 16), (17, 21)],
    "instagram": [(8, 11), (19, 22)],
}

# Hashtag strategy: how many to use per platform
_HASHTAG_COUNTS = {
    "tiktok":   {"min": 3, "max": 5, "strategy": "mix niche + trending"},
    "youtube":  {"min": 5, "max": 15, "strategy": "SEO-first then trending"},
    "instagram": {"min": 10, "max": 30, "strategy": "niche-heavy with 2-3 viral"},
}


def posting_schedule(platform: str) -> dict[str, Any]:
    """Return optimal posting time windows for a platform."""
    platform = platform.lower()
    windows = _OPTIMAL_HOURS.get(platform, [(12, 18)])
    formatted = [f"{s:02d}:00–{e:02d}:00 UTC" for s, e in windows]
    return {
        "platform": platform,
        "optimal_windows_utc": formatted,
        "note": "Adjust to your audience's local timezone. Post within 1h of window start.",
    }


def hashtag_strategy(
    platform: str,
    trending_tags: list[dict],
    niche_tags: list[str] | None = None,
) -> dict[str, Any]:
    """
    Build a tailored hashtag set for a post on the given platform.

    trending_tags: from cross_platform_hashtags() or top_hashtags_from_trending()
    niche_tags: user-supplied niche/brand hashtags
    """
    platform = platform.lower()
    cfg = _HASHTAG_COUNTS.get(platform, _HASHTAG_COUNTS["tiktok"])

    niche = [t.strip("#").lower() for t in (niche_tags or [])]
    viral = [d["hashtag"].strip("#").lower() for d in trending_tags if d.get("cross_platform")]
    hot   = [d["hashtag"].strip("#").lower() for d in trending_tags if not d.get("cross_platform")]

    chosen: list[str] = []
    # 1-2 niche tags
    chosen += niche[: min(2, len(niche))]
    # Cross-platform viral tags (high priority)
    for tag in viral:
        if tag not in chosen and len(chosen) < cfg["max"]:
            chosen.append(tag)
    # Fill with hot platform-specific tags
    for tag in hot:
        if tag not in chosen and len(chosen) < cfg["max"]:
            chosen.append(tag)

    chosen = chosen[: cfg["max"]]
    return {
        "platform": platform,
        "strategy": cfg["strategy"],
        "recommended_count": f"{cfg['min']}–{cfg['max']}",
        "hashtags": [f"#{t}" for t in chosen],
        "caption_placement": (
            "Put 3 hashtags inline in caption, rest in first comment" if platform == "instagram"
            else "Append all hashtags at end of caption"
        ),
    }


def content_pillars(niche: str) -> dict[str, Any]:
    """
    Return a content pillar framework for a theme/niche page.
    Includes post-type mix and frequency.
    """
    return {
        "niche": niche,
        "pillars": [
            {"name": "Educational",  "share": "30%", "formats": ["carousel", "talking-head", "voiceover"]},
            {"name": "Entertaining", "share": "40%", "formats": ["trending-sound", "skit", "reaction"]},
            {"name": "Promotional",  "share": "15%", "formats": ["product-demo", "CTA", "link-in-bio"]},
            {"name": "Community",    "share": "15%", "formats": ["Q&A", "poll", "duet/stitch"]},
        ],
        "posting_frequency": {
            "tiktok":   "2-3x per day",
            "youtube_shorts": "1x per day",
            "instagram_reels": "1-2x per day",
        },
        "repurpose_workflow": (
            "Film once → post on TikTok first (test virality) → "
            "repost best performers to Shorts + Reels same day"
        ),
    }


def bio_optimization(platform: str, niche: str, cta: str = "link in bio") -> dict[str, Any]:
    """Generate an optimized bio template for a theme page."""
    templates = {
        "tiktok": f"✦ {niche.title()} content daily\n📌 Save this for later\n👇 {cta}",
        "youtube": (
            f"Welcome to the #{niche} hub.\n"
            f"New videos every week. Subscribe for more.\n👇 {cta}"
        ),
        "instagram": (
            f"🔥 {niche.title()} tips & trends\n"
            f"💡 New posts daily\n📩 DM for collabs\n👇 {cta}"
        ),
    }
    return {
        "platform": platform,
        "bio_template": templates.get(platform.lower(), templates["tiktok"]),
        "tips": [
            "Include 1 keyword agents/search can index",
            "Lead with value prop in first line (shown above fold)",
            "One clear CTA only — more than one splits attention",
        ],
    }


def full_account_audit(
    platform: str,
    niche: str,
    trending_tags: list[dict],
    niche_tags: list[str] | None = None,
    cta: str = "link in bio",
) -> dict[str, Any]:
    """Run all optimization checks and return a complete audit report."""
    return {
        "platform": platform,
        "niche": niche,
        "posting_schedule": posting_schedule(platform),
        "hashtag_strategy": hashtag_strategy(platform, trending_tags, niche_tags),
        "content_pillars": content_pillars(niche),
        "bio_optimization": bio_optimization(platform, niche, cta),
    }
