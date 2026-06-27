"""Account optimization engine.

Audits and scores social media account configurations across:
- Bio quality (CTA, keywords, link-in-bio)
- Posting schedule (frequency, consistency, peak times)
- Content mix (variety, format distribution)
- Engagement health (rate benchmarks by follower tier)
- Link-in-bio tool recommendations
- Platform-specific best practices (TikTok vs Instagram vs YouTube)

All accounts are stored as plain dicts (AccountProfile schema).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


# ── Account schema ────────────────────────────────────────────────────────────

AccountProfile = Dict[str, Any]
# Keys:
#   username, platform, followers, following, posts_count,
#   bio, has_link, link_url, link_tool,
#   avg_likes, avg_comments, avg_shares, avg_views,
#   post_frequency_per_week, niche, content_types (list),
#   account_type ("personal" | "creator" | "business" | "theme_page")


# ── Engagement benchmarks by follower tier ────────────────────────────────────

_ENGAGEMENT_BENCHMARKS = {
    # (follower_min, follower_max): (tiktok_rate, instagram_rate)
    (0,      1_000):   (0.20, 0.15),
    (1_000,  10_000):  (0.12, 0.08),
    (10_000, 100_000): (0.07, 0.04),
    (100_000, 1_000_000): (0.04, 0.02),
    (1_000_000, 999_999_999): (0.02, 0.01),
}


def _benchmark_engagement(followers: int, platform: str) -> float:
    """Return the expected engagement rate for a follower count."""
    for (lo, hi), (tt_rate, ig_rate) in _ENGAGEMENT_BENCHMARKS.items():
        if lo <= followers < hi:
            return tt_rate if "tiktok" in platform.lower() else ig_rate
    return 0.02


# ── Peak posting times ────────────────────────────────────────────────────────

_PEAK_TIMES = {
    "tiktok": {
        "mon": ["06:00", "10:00", "19:00"],
        "tue": ["09:00", "12:00", "19:00"],
        "wed": ["07:00", "11:00", "19:00"],
        "thu": ["09:00", "12:00", "19:00"],
        "fri": ["05:00", "13:00", "20:00"],
        "sat": ["11:00", "19:00", "20:00"],
        "sun": ["07:00", "08:00", "16:00"],
    },
    "instagram": {
        "mon": ["06:00", "12:00", "21:00"],
        "tue": ["08:00", "14:00", "21:00"],
        "wed": ["09:00", "15:00", "21:00"],
        "thu": ["08:00", "12:00", "17:00"],
        "fri": ["07:00", "13:00", "20:00"],
        "sat": ["09:00", "11:00", "19:00"],
        "sun": ["09:00", "10:00", "18:00"],
    },
    "youtube": {
        "mon": ["15:00", "17:00"],
        "tue": ["15:00", "17:00"],
        "wed": ["15:00", "17:00"],
        "thu": ["15:00", "17:00"],
        "fri": ["15:00", "17:00"],
        "sat": ["09:00", "11:00"],
        "sun": ["09:00", "11:00"],
    },
}

_FREQUENCY_RECOMMENDATIONS = {
    "tiktok":    {"min": 1, "ideal": 3, "max": 5, "unit": "per day"},
    "instagram": {"min": 3, "ideal": 5, "max": 7, "unit": "per week"},
    "youtube":   {"min": 1, "ideal": 2, "max": 3, "unit": "per week"},
}


# ── Bio analysis ──────────────────────────────────────────────────────────────

_BIO_KEYWORDS = {
    "cta": ["link below", "click link", "shop now", "tap link", "check link", "dm for", "order now"],
    "niche": [],  # populated dynamically
    "emoji_heavy": None,  # heuristic
}


def audit_bio(bio: str, has_link: bool, platform: str) -> Dict[str, Any]:
    """Score and audit a social media bio."""
    issues = []
    score = 0

    # Length check
    if len(bio) < 20:
        issues.append("Bio is too short — add a value proposition and CTA")
    elif len(bio) > 150:
        issues.append("Bio may be too long — keep the key hook in the first 80 chars")
    else:
        score += 20

    # CTA check
    bio_lower = bio.lower()
    has_cta = any(kw in bio_lower for kw in _BIO_KEYWORDS["cta"])
    if has_cta:
        score += 25
    else:
        issues.append("No call-to-action (CTA) detected — add 'link below', 'DM for info', etc.")

    # Link check
    if has_link:
        score += 25
    else:
        issues.append("No link in bio — add a link-in-bio tool (Linktree, Stan Store, Beacons)")

    # Emoji check (emojis increase engagement on TikTok/IG)
    emoji_count = sum(1 for c in bio if ord(c) > 0x1F300)
    if emoji_count > 0:
        score += 10
    else:
        if platform.lower() in ("tiktok", "instagram"):
            issues.append("Consider adding 1-3 emojis to make the bio scannable and engaging")

    # Niche signal
    if any(len(w) > 5 and w.isalpha() for w in bio.split()):
        score += 20

    return {
        "score": min(score, 100),
        "grade": "A" if score >= 80 else ("B" if score >= 60 else ("C" if score >= 40 else "D")),
        "issues": issues,
        "has_cta": has_cta,
        "has_link": has_link,
        "char_count": len(bio),
    }


# ── Engagement audit ──────────────────────────────────────────────────────────

def audit_engagement(profile: AccountProfile) -> Dict[str, Any]:
    """Compare account engagement to platform benchmarks."""
    followers = profile.get("followers", 0)
    platform = profile.get("platform", "tiktok")
    avg_likes = profile.get("avg_likes", 0)
    avg_comments = profile.get("avg_comments", 0)
    avg_views = profile.get("avg_views", followers)

    benchmark = _benchmark_engagement(followers, platform)
    actual_rate = (avg_likes + avg_comments) / max(avg_views, 1)
    ratio = actual_rate / benchmark if benchmark > 0 else 1.0

    if ratio >= 1.2:
        status = "excellent"
        note = "Engagement is above benchmark — algorithm is likely boosting your content"
    elif ratio >= 0.8:
        status = "good"
        note = "Engagement is on par with similar accounts"
    elif ratio >= 0.5:
        status = "below average"
        note = "Engagement is below benchmark — improve hook quality and posting times"
    else:
        status = "poor"
        note = "Engagement is significantly below benchmark — consider a content strategy reset"

    return {
        "actual_rate_pct": round(actual_rate * 100, 2),
        "benchmark_rate_pct": round(benchmark * 100, 2),
        "ratio": round(ratio, 2),
        "status": status,
        "note": note,
    }


# ── Posting schedule ──────────────────────────────────────────────────────────

def recommend_schedule(
    platform: str,
    frequency_per_week: int = 0,
    timezone: str = "EST",
) -> Dict[str, Any]:
    """Recommend an optimal posting schedule."""
    platform_lower = platform.lower()
    rec = _FREQUENCY_RECOMMENDATIONS.get(platform_lower, _FREQUENCY_RECOMMENDATIONS["tiktok"])
    times = _PEAK_TIMES.get(platform_lower, _PEAK_TIMES["tiktok"])

    issues = []
    if frequency_per_week > 0:
        freq_per_unit = frequency_per_week
        if platform_lower == "tiktok":
            freq_per_unit = frequency_per_week / 7  # per day
        if freq_per_unit < rec["min"]:
            issues.append(f"Posting too infrequently — aim for {rec['ideal']} {rec['unit']}")
        elif freq_per_unit > rec["max"]:
            issues.append(f"May be over-posting — quality > quantity; {rec['ideal']} {rec['unit']} is ideal")

    # Build 7-day schedule
    schedule = {}
    days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    for day in days:
        schedule[day] = times.get(day, ["12:00"])[:2]  # top 2 slots

    return {
        "platform": platform,
        "recommended_frequency": f"{rec['ideal']} {rec['unit']}",
        "timezone_note": f"Times shown in EST — adjust ±hours for your audience's {timezone}",
        "peak_times": schedule,
        "issues": issues,
    }


# ── Link-in-bio recommendations ───────────────────────────────────────────────

_LINK_IN_BIO_TOOLS = [
    {
        "name": "Stan Store",
        "url": "stan.store",
        "best_for": "Creators selling digital products, coaching, subscriptions",
        "free_plan": True,
        "commission": "0%",
        "highlights": ["Built-in store", "Email capture", "Course hosting", "0% transaction fee on free plan"],
    },
    {
        "name": "Beacons",
        "url": "beacons.ai",
        "best_for": "Multi-platform creators, brand deals management",
        "free_plan": True,
        "commission": "9% on free",
        "highlights": ["Brand deal CRM", "Media kit generator", "Analytics", "Multiple link blocks"],
    },
    {
        "name": "Linktree",
        "url": "linktr.ee",
        "best_for": "Simple multi-link pages, beginners",
        "free_plan": True,
        "commission": "0%",
        "highlights": ["Simplest setup", "Most recognized brand", "App integrations"],
    },
    {
        "name": "Taplink",
        "url": "taplink.cc",
        "best_for": "E-commerce, WhatsApp/messenger CTA, lead generation",
        "free_plan": True,
        "commission": "0%",
        "highlights": ["Payment forms", "Appointment booking", "Messenger CTA buttons"],
    },
]


def recommend_link_in_bio(account_type: str, monetization: str = "") -> List[Dict[str, Any]]:
    """Recommend the best link-in-bio tool for an account type."""
    mon_lower = monetization.lower()
    if "product" in mon_lower or "course" in mon_lower or "digital" in mon_lower:
        order = ["Stan Store", "Beacons", "Taplink", "Linktree"]
    elif "brand" in mon_lower or "deal" in mon_lower or "sponsor" in mon_lower:
        order = ["Beacons", "Stan Store", "Linktree", "Taplink"]
    elif "affiliate" in mon_lower:
        order = ["Linktree", "Beacons", "Stan Store", "Taplink"]
    else:
        order = ["Stan Store", "Beacons", "Linktree", "Taplink"]

    tool_map = {t["name"]: t for t in _LINK_IN_BIO_TOOLS}
    return [tool_map[name] for name in order if name in tool_map]


# ── Full account audit ────────────────────────────────────────────────────────

def full_audit(profile: AccountProfile) -> Dict[str, Any]:
    """Run a complete account optimization audit."""
    bio_audit = audit_bio(
        profile.get("bio", ""),
        profile.get("has_link", False),
        profile.get("platform", "tiktok"),
    )
    eng_audit = audit_engagement(profile)
    schedule = recommend_schedule(
        profile.get("platform", "tiktok"),
        profile.get("post_frequency_per_week", 0),
    )
    link_recs = recommend_link_in_bio(
        profile.get("account_type", "creator"),
        profile.get("monetization", ""),
    )

    # Overall score
    bio_score = bio_audit["score"]
    eng_score = 100 if eng_audit["status"] == "excellent" else (
        80 if eng_audit["status"] == "good" else (
        50 if eng_audit["status"] == "below average" else 25))
    freq_score = 80 if not schedule["issues"] else 50
    overall = round((bio_score + eng_score + freq_score) / 3)

    priority_actions = []
    if not profile.get("has_link"):
        priority_actions.append(f"Add link in bio using {link_recs[0]['name']} ({link_recs[0]['url']})")
    if bio_audit["score"] < 60:
        priority_actions.extend(bio_audit["issues"][:2])
    if eng_audit["status"] in ("poor", "below average"):
        priority_actions.append(eng_audit["note"])
    if schedule["issues"]:
        priority_actions.extend(schedule["issues"])

    return {
        "username": profile.get("username", "unknown"),
        "platform": profile.get("platform", "unknown"),
        "overall_score": overall,
        "grade": "A" if overall >= 80 else ("B" if overall >= 60 else ("C" if overall >= 40 else "D")),
        "bio_audit": bio_audit,
        "engagement": eng_audit,
        "schedule": schedule,
        "link_in_bio": link_recs[:2],
        "priority_actions": priority_actions[:5],
    }


def create_account(username: str, platform: str, **kwargs) -> AccountProfile:
    """Create a new account profile dict."""
    return {
        "username": username,
        "platform": platform.lower(),
        "followers": kwargs.get("followers", 0),
        "following": kwargs.get("following", 0),
        "posts_count": kwargs.get("posts_count", 0),
        "bio": kwargs.get("bio", ""),
        "has_link": kwargs.get("has_link", False),
        "link_url": kwargs.get("link_url", ""),
        "link_tool": kwargs.get("link_tool", ""),
        "avg_likes": kwargs.get("avg_likes", 0),
        "avg_comments": kwargs.get("avg_comments", 0),
        "avg_shares": kwargs.get("avg_shares", 0),
        "avg_views": kwargs.get("avg_views", 0),
        "post_frequency_per_week": kwargs.get("post_frequency_per_week", 0),
        "niche": kwargs.get("niche", ""),
        "content_types": kwargs.get("content_types", []),
        "account_type": kwargs.get("account_type", "creator"),
        "monetization": kwargs.get("monetization", ""),
    }
