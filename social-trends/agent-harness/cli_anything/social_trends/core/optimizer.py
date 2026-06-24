"""Account optimizer — cross-platform analysis and actionable recommendations.

Pulls trend data from both YouTube and TikTok, then scores each piece of
data against engagement signals to produce ranked recommendations for:
  - Optimal posting times (by platform norms)
  - Hashtag strategy (volume + relevance)
  - Content format mix (Shorts vs long-form, TikTok vs Reels)
  - Music selection for TikTok/Reels
  - Niche positioning vs trending pivot opportunities
"""

from typing import Optional


# Platform-specific best-practice data (distilled from platform docs + studies)
POSTING_WINDOWS = {
    "tiktok": {
        "best_days": ["Tuesday", "Thursday", "Friday", "Saturday"],
        "best_hours_utc": ["06:00", "09:00", "12:00", "19:00", "21:00"],
        "cadence": "1–4 posts/day",
        "note": "TikTok algorithm heavily rewards consistency and completion rate.",
    },
    "youtube": {
        "best_days": ["Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "best_hours_utc": ["14:00", "15:00", "16:00", "17:00"],
        "cadence": "2–3 videos/week for growth; daily Shorts optional",
        "note": "Upload 48h before your target audience peak time to allow indexing.",
    },
    "instagram": {
        "best_days": ["Monday", "Tuesday", "Wednesday"],
        "best_hours_utc": ["06:00", "09:00", "12:00"],
        "cadence": "1 Reel/day + 1–3 Stories/day",
        "note": "Reels get 22% more interaction than regular video on average.",
    },
}

HASHTAG_STRATEGY = {
    "tiktok": {
        "recommended_count": "3–5",
        "mix": "1 mega (>1B views) + 2 niche (<500M) + 1 micro (<50M)",
        "tip": "Use #fyp sparingly — it's oversaturated. Niche tags drive qualified views.",
    },
    "youtube": {
        "recommended_count": "3–5 in description",
        "mix": "1 broad + 2 mid-tail + 1 brand/series hashtag",
        "tip": "YouTube shows only the first 3 hashtags above the title.",
    },
    "instagram": {
        "recommended_count": "5–10 in caption",
        "mix": "2 mega + 4 medium + 4 niche",
        "tip": "Rotate hashtag sets to avoid shadow-filtering.",
    },
}

CONTENT_FORMAT_MIX = {
    "tiktok": {
        "primary": "15–60s vertical video (highest reach)",
        "secondary": "3–10 min TikTok LIVE (community building)",
        "avoid": "Landscape video without crops — algorithm deprioritizes it",
        "hooks": "First 2s must contain movement or spoken hook",
    },
    "youtube": {
        "primary": "8–15 min evergreen tutorials / vlogs (ad revenue sweet spot)",
        "secondary": "YouTube Shorts <60s (discovery funnel into long-form)",
        "avoid": "Videos under 4 min for monetization purposes",
        "hooks": "First 30s retention is the #1 ranking signal",
    },
    "instagram": {
        "primary": "Reels 15–30s (maximum algorithmic push)",
        "secondary": "Carousel posts (highest save rate of all formats)",
        "avoid": "Native Instagram Stories as growth driver — use for community only",
        "hooks": "On-screen text in first frame captures silent scroll viewers",
    },
}

ENGAGEMENT_BENCHMARKS = {
    "tiktok": {
        "micro": {"followers": "<10K", "avg_er": "8–15%"},
        "mid": {"followers": "10K–100K", "avg_er": "5–8%"},
        "macro": {"followers": "100K–1M", "avg_er": "3–5%"},
        "mega": {"followers": ">1M", "avg_er": "1–3%"},
    },
    "youtube": {
        "micro": {"subscribers": "<10K", "avg_vr": "20–40%"},
        "mid": {"subscribers": "10K–100K", "avg_vr": "10–20%"},
        "macro": {"subscribers": "100K–1M", "avg_vr": "5–10%"},
        "mega": {"subscribers": ">1M", "avg_vr": "2–5%"},
    },
}


def analyze_hashtag_opportunity(
    platform_hashtags: list[dict],
    niche_keywords: list[str],
) -> dict:
    """Score and rank hashtags by trending relevance + niche fit.

    Args:
        platform_hashtags: Output of youtube.extract_trending_hashtags() or
            tiktok.get_trending_hashtags() — list of {tag, count, platform}.
        niche_keywords: Keywords describing the account's niche
            (e.g. ['fitness', 'workout', 'gym']).

    Returns:
        Ranked hashtag recommendations split into tiers.
    """
    if not platform_hashtags:
        return {"recommendations": [], "note": "No hashtag data provided."}

    niche_lower = {kw.lower() for kw in niche_keywords}
    scored = []
    for entry in platform_hashtags:
        tag = entry.get("tag", "").lstrip("#").lower()
        count = entry.get("count", 0)
        platform = entry.get("platform", "unknown")

        relevance_score = sum(1 for kw in niche_lower if kw in tag or tag in kw)
        viral_score = min(count / 5, 10)  # cap at 10
        total_score = viral_score + (relevance_score * 3)

        tier = "mega"
        if count <= 2:
            tier = "micro"
        elif count <= 5:
            tier = "niche"
        elif count <= 10:
            tier = "mid"

        scored.append({
            "tag": f"#{tag}",
            "platform": platform,
            "trend_count": count,
            "tier": tier,
            "relevance_to_niche": relevance_score,
            "score": round(total_score, 2),
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    strategy = HASHTAG_STRATEGY.get(scored[0]["platform"] if scored else "tiktok", {})

    return {
        "total_analyzed": len(scored),
        "top_recommendations": scored[:15],
        "suggested_set": [h["tag"] for h in scored[:5]],
        "strategy": strategy,
    }


def get_posting_schedule(platforms: list[str], timezone_offset: int = 0) -> dict:
    """Return optimal posting schedule for given platforms.

    Args:
        platforms: List of platform names ('tiktok', 'youtube', 'instagram').
        timezone_offset: Hours from UTC (e.g. -5 for EST).
    """
    schedule = {}
    for platform in platforms:
        if platform not in POSTING_WINDOWS:
            continue
        pw = POSTING_WINDOWS[platform].copy()
        if timezone_offset != 0:
            adjusted_hours = []
            for h in pw["best_hours_utc"]:
                hh, mm = map(int, h.split(":"))
                adjusted = (hh + timezone_offset) % 24
                adjusted_hours.append(f"{adjusted:02d}:{mm:02d}")
            pw["best_hours_local"] = adjusted_hours
            pw["timezone_offset"] = f"UTC{timezone_offset:+d}"
        schedule[platform] = pw

    return {"posting_schedule": schedule}


def get_content_strategy(
    platforms: list[str],
    niche: str,
    follower_tier: str = "micro",
) -> dict:
    """Return a complete content strategy for the given platforms and niche.

    Args:
        platforms: Target platforms.
        niche: Account niche description (e.g. 'fitness', 'finance', 'cooking').
        follower_tier: 'micro' | 'mid' | 'macro' | 'mega'.
    """
    strategies = {}
    for platform in platforms:
        fmt = CONTENT_FORMAT_MIX.get(platform, {})
        benchmarks = ENGAGEMENT_BENCHMARKS.get(platform, {}).get(follower_tier, {})
        strategies[platform] = {
            "content_format": fmt,
            "engagement_benchmark": benchmarks,
            "hashtag_strategy": HASHTAG_STRATEGY.get(platform, {}),
        }

    niche_tips = _niche_specific_tips(niche)

    return {
        "niche": niche,
        "follower_tier": follower_tier,
        "platform_strategies": strategies,
        "niche_tips": niche_tips,
    }


def _niche_specific_tips(niche: str) -> list[str]:
    """Return niche-specific growth tips."""
    niche_lower = niche.lower()
    tips_db = {
        "fitness": [
            "30-day challenge series dramatically increase return viewers.",
            "Transformation thumbnails have 40% higher CTR in fitness.",
            "Post workout tutorials Mon/Wed/Fri to match gym-goer schedules.",
            "Collab with supplement brands at 10K+ followers for first sponsorship.",
        ],
        "finance": [
            "News-reactive content (market drops, rate changes) can 10x impressions.",
            "'Stock of the week' series builds appointment viewing.",
            "Use plain language disclaimers to avoid demonetization.",
            "Finance content has highest RPM ($15–$30) on YouTube — prioritize long-form.",
        ],
        "cooking": [
            "Recipe reveal at 0:03 then show full process — avoids front-loaded skip.",
            "Ingredient lists on screen at all times boost completion rate 20%.",
            "Seasonal content (holiday recipes) spikes search traffic 10–20x.",
            "Kitchenware brand deals are easiest first sponsorship at 5K followers.",
        ],
        "beauty": [
            "Get ready with me (GRWM) is consistently TikTok's top beauty format.",
            "Product dupes content has 3x average shares vs regular reviews.",
            "Shade-match and skin-tone inclusivity content drives saves heavily.",
            "Amazon affiliate links with beauty hauls convert at 5–12%.",
        ],
        "gaming": [
            "First-to-upload on new game launches captures long-tail search traffic.",
            "Highlight clips under 60s drive YouTube channel discovery.",
            "Rage/skill clips get 2x shares vs tutorial content.",
            "Gaming sponsors (VPNs, chairs) activate at ~5K followers.",
        ],
        "travel": [
            "Cinematic B-roll with trending audio is the TikTok winning formula.",
            "Budget travel content outperforms luxury 3:1 by engagement rate.",
            "Local food/hidden gems series builds stronger community than hotel tours.",
            "Travel content earns 60% of revenue off-season — plan sponsorships early.",
        ],
        "education": [
            "'Things school never taught you' hooks consistently go viral.",
            "Subtitles on every video boost completion rate 15% globally.",
            "Short explainer series (5 episodes) outperforms one-off deep dives.",
            "B2B LinkedIn cross-post amplifies educational content reach 5x.",
        ],
    }

    for key in tips_db:
        if key in niche_lower:
            return tips_db[key]

    return [
        "Hook in first 2 seconds is the #1 factor for completion rate.",
        "Consistent upload schedule matters more than upload frequency.",
        "Engage with every comment in the first hour — boosts distribution.",
        "A/B test 3 thumbnail variants per video to optimize CTR.",
        "Cross-post Shorts/Reels/TikToks to multiply reach from one asset.",
    ]


def score_viral_potential(videos: list[dict]) -> list[dict]:
    """Score a list of normalized video dicts for viral potential.

    Uses engagement rate and share ratio as primary signals.
    Returns videos sorted by viral score descending.
    """
    scored = []
    for video in videos:
        views = max(video.get("views", 0), 1)
        likes = video.get("likes", 0)
        comments = video.get("comments", 0)
        shares = video.get("shares", 0)

        engagement_rate = (likes + comments + shares) / views * 100
        share_ratio = shares / max(likes, 1)
        viral_score = engagement_rate * (1 + share_ratio * 2)

        scored.append({
            **video,
            "engagement_rate_pct": round(engagement_rate, 3),
            "share_ratio": round(share_ratio, 4),
            "viral_score": round(viral_score, 3),
        })

    scored.sort(key=lambda x: x["viral_score"], reverse=True)
    return scored


def get_optimization_report(
    platforms: list[str],
    niche: str,
    region: str = "US",
    follower_tier: str = "micro",
    timezone_offset: int = 0,
    trending_hashtags: Optional[list[dict]] = None,
    niche_keywords: Optional[list[str]] = None,
) -> dict:
    """Generate a full optimization report for an account.

    This is the top-level function that agents should call.
    Combines all optimizer sub-functions into a single actionable report.
    """
    if niche_keywords is None:
        niche_keywords = [niche]

    hashtag_report = {}
    if trending_hashtags:
        hashtag_report = analyze_hashtag_opportunity(trending_hashtags, niche_keywords)

    schedule = get_posting_schedule(platforms, timezone_offset)
    strategy = get_content_strategy(platforms, niche, follower_tier)

    return {
        "account_summary": {
            "niche": niche,
            "platforms": platforms,
            "region": region,
            "follower_tier": follower_tier,
        },
        "posting_schedule": schedule["posting_schedule"],
        "content_strategy": strategy["platform_strategies"],
        "niche_tips": strategy["niche_tips"],
        "hashtag_report": hashtag_report,
        "quick_wins": [
            "Post at least once today at an optimal time (see posting_schedule).",
            f"Use this hashtag set in your next post: {hashtag_report.get('suggested_set', [])}",
            "Reply to every comment within the first 60 minutes of posting.",
            "Add closed captions to every video — boosts watch time and accessibility.",
            "Pin your best-performing comment on new posts to guide conversation.",
        ],
    }
