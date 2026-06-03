"""Social Trends CLI - Account management & optimization engine."""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from cli_anything.social_trends.core.session import Session


_PLATFORM_LIMITS = {
    "tiktok":    {"bio": 80,  "username": 24, "name": 30},
    "instagram": {"bio": 150, "username": 30, "name": 30},
    "youtube":   {"bio": 1000, "username": 100, "name": 100},
    "twitter":   {"bio": 160, "username": 15, "name": 50},
}

_PLATFORM_BEST_PRACTICES = {
    "tiktok": {
        "posting_frequency": "1-3x per day",
        "optimal_video_length": "7-60 seconds",
        "key_features": ["Duets", "Stitches", "Sounds", "Effects", "Live"],
        "algorithm_factors": ["completion rate", "rewatches", "shares", "early engagement"],
        "monetization": ["Creator Rewards Program ($0.40-$0.80/1K views)", "TikTok Shop",
                         "Brand deals", "Live gifts", "Affiliate links in bio"],
        "content_pillars": 3,
    },
    "instagram": {
        "posting_frequency": "3-5x Reels/week + 1-2 Stories/day",
        "optimal_video_length": "15-30 seconds Reels, 60s for conversions",
        "key_features": ["Reels", "Stories", "Broadcast Channels", "Collab posts"],
        "algorithm_factors": ["saves", "shares", "DMs", "comments depth"],
        "monetization": ["Brand deals", "Affiliate", "Digital products",
                         "Subscriptions (10K+ required)", "Shop"],
        "content_pillars": 3,
    },
    "youtube": {
        "posting_frequency": "2-4x Shorts/day + 1-2 long-form/week",
        "optimal_video_length": "Shorts: 30-45s, Long-form: 8-15 min",
        "key_features": ["Shorts", "Community posts", "Chapters", "End screens"],
        "algorithm_factors": ["CTR", "watch time %", "session time", "satisfaction"],
        "monetization": ["AdSense", "Channel memberships", "Super Thanks",
                         "Merch shelf", "Sponsorships"],
        "content_pillars": 2,
    },
}


def add_account(
    sess: Session,
    platform: str,
    username: str,
    niche: str,
    followers: int = 0,
    bio: str = "",
    goals: Optional[List[str]] = None,
) -> Dict[str, Any]:
    platform = platform.lower()
    if platform not in _PLATFORM_BEST_PRACTICES:
        raise ValueError(
            f"Unknown platform '{platform}'. "
            f"Supported: {', '.join(_PLATFORM_BEST_PRACTICES.keys())}"
        )
    sess.snapshot(f"add account {platform}/{username}")
    account_id = f"{platform}_{username.lower().replace('@', '')}"
    account = {
        "id": account_id,
        "platform": platform,
        "username": username.lstrip("@"),
        "niche": niche,
        "followers": followers,
        "bio": bio,
        "goals": goals or ["grow followers", "increase engagement"],
        "content_score": None,
        "last_audit": None,
        "created": datetime.now().isoformat(),
    }
    sess.config["accounts"][account_id] = account
    return {"success": True, "account_id": account_id, "account": account}


def remove_account(sess: Session, account_id: str) -> Dict[str, Any]:
    if account_id not in sess.config["accounts"]:
        raise KeyError(f"Account '{account_id}' not found.")
    sess.snapshot(f"remove account {account_id}")
    account = sess.config["accounts"].pop(account_id)
    return {"success": True, "removed": account_id, "username": account["username"]}


def list_accounts(sess: Session) -> List[Dict[str, Any]]:
    accounts = list(sess.config["accounts"].values())
    return sorted(accounts, key=lambda a: a["platform"])


def get_account(sess: Session, account_id: str) -> Dict[str, Any]:
    if account_id not in sess.config["accounts"]:
        raise KeyError(f"Account '{account_id}' not found. Run 'accounts list' to see IDs.")
    return sess.config["accounts"][account_id]


def audit_account(sess: Session, account_id: str) -> Dict[str, Any]:
    account = get_account(sess, account_id)
    platform = account["platform"]
    limits = _PLATFORM_LIMITS.get(platform, {})
    practices = _PLATFORM_BEST_PRACTICES.get(platform, {})

    issues: List[Dict[str, str]] = []
    wins: List[str] = []
    score = 100

    # Bio audit
    bio = account.get("bio", "")
    bio_limit = limits.get("bio", 150)
    if not bio:
        issues.append({"severity": "high", "field": "bio",
                       "issue": "Bio is empty — add a value-driven bio with CTA"})
        score -= 20
    elif len(bio) < 30:
        issues.append({"severity": "medium", "field": "bio",
                       "issue": f"Bio too short ({len(bio)} chars). Aim for 80+ chars."})
        score -= 10
    elif len(bio) > bio_limit:
        issues.append({"severity": "low", "field": "bio",
                       "issue": f"Bio exceeds {bio_limit} char limit — will be truncated."})
        score -= 5
    else:
        wins.append("Bio length is within optimal range")

    # Bio keywords
    if bio:
        has_cta = any(w in bio.lower() for w in
                      ["link", "shop", "dm", "join", "follow", "click", "get", "free"])
        has_niche = account.get("niche", "").lower() in bio.lower()
        if not has_cta:
            issues.append({"severity": "medium", "field": "bio",
                           "issue": "No CTA in bio. Add 'DM for collabs', 'Link below', etc."})
            score -= 8
        else:
            wins.append("Bio has a call-to-action")
        if not has_niche:
            issues.append({"severity": "low", "field": "bio",
                           "issue": f"Bio doesn't mention niche '{account['niche']}' — add keywords."})
            score -= 5

    # Followers
    followers = account.get("followers", 0)
    if followers == 0:
        issues.append({"severity": "info", "field": "followers",
                       "issue": "Followers not set — update via 'accounts update'"})
    elif followers < 1000:
        issues.append({"severity": "info", "field": "followers",
                       "issue": f"Under 1K followers ({followers}). Focus on consistent posting + trending sounds."})
    elif followers >= 10000:
        wins.append(f"10K+ followers unlocks additional monetization features")

    # Niche
    if not account.get("niche"):
        issues.append({"severity": "high", "field": "niche",
                       "issue": "No niche defined — niche accounts grow 4x faster than general."})
        score -= 15
    else:
        wins.append(f"Niche defined: {account['niche']}")

    score = max(0, min(100, score))

    # Recommendations
    recommendations = _generate_recommendations(account, platform, issues, practices)

    result = {
        "account_id": account_id,
        "platform": platform,
        "username": account["username"],
        "score": score,
        "grade": _score_to_grade(score),
        "issues": issues,
        "wins": wins,
        "recommendations": recommendations,
        "best_practices": practices,
        "audited_at": datetime.now().isoformat(),
    }

    # Save audit result
    sess.config["accounts"][account_id]["last_audit"] = result["audited_at"]
    sess.config["accounts"][account_id]["content_score"] = score
    return result


def _generate_recommendations(
    account: Dict[str, Any],
    platform: str,
    issues: List[Dict[str, str]],
    practices: Dict[str, Any],
) -> List[Dict[str, str]]:
    recs: List[Dict[str, str]] = []
    followers = account.get("followers", 0)
    niche = account.get("niche", "")

    recs.append({
        "priority": "1",
        "action": f"Post {practices.get('posting_frequency', '1-3x/day')}",
        "why": "Consistency is the #1 algorithm factor — irregular posters lose 40% of reach.",
    })
    recs.append({
        "priority": "2",
        "action": f"Use trending sounds in the first 24h of them going viral",
        "why": "Early adopters of rising sounds get 3-5x organic reach boost.",
    })
    recs.append({
        "priority": "3",
        "action": "Hook in the first 1-2 seconds — text overlay + verbal hook simultaneously",
        "why": "80% of viewers decide to scroll within the first 2 seconds.",
    })

    if followers < 1000:
        recs.append({
            "priority": "4",
            "action": "Comment on 10-15 accounts in your niche daily (genuine engagement)",
            "why": "Engagement pods accelerate discoverability before the algorithm knows you.",
        })
    elif followers < 10000:
        recs.append({
            "priority": "4",
            "action": "Do 1-2 collab posts/week with accounts of similar size",
            "why": "Cross-account exposure is the fastest follower growth strategy at this stage.",
        })
    else:
        recs.append({
            "priority": "4",
            "action": "Launch a lead magnet (free resource) to convert followers → email list",
            "why": "Email list = owned audience that can't be algorithm'd away.",
        })

    recs.append({
        "priority": "5",
        "action": f"Pin your 3 best-performing videos to your profile",
        "why": "Profile visitors decide to follow based on the first 3 posts they see.",
    })

    if niche:
        recs.append({
            "priority": "6",
            "action": f"Create a '{niche} 101' or '5 things about {niche}' series",
            "why": "Educational series content drives follows because viewers want to see part 2.",
        })

    return recs


def _score_to_grade(score: int) -> str:
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 50:
        return "D"
    return "F"


def optimize_bio(
    sess: Session,
    account_id: str,
    niche: str,
    tone: str = "professional",
    include_cta: bool = True,
    cta_type: str = "link",
) -> Dict[str, Any]:
    account = get_account(sess, account_id)
    platform = account["platform"]
    limits = _PLATFORM_LIMITS.get(platform, {"bio": 150})
    max_len = limits["bio"]

    cta_map = {
        "link": "↓ Free guide below",
        "dm": "DM 'START' to begin",
        "shop": "Shop link below ↓",
        "collab": "Collabs: DM me",
        "follow": "Follow for daily tips",
        "subscribe": "Subscribe for more",
    }
    cta_text = cta_map.get(cta_type, cta_map["link"])

    emoji_map = {
        "fitness": "💪", "finance": "💰", "fashion": "👗", "food": "🍳",
        "beauty": "✨", "travel": "✈️", "tech": "🤖", "motivation": "🔥",
        "gaming": "🎮", "pets": "🐾",
    }
    niche_emoji = emoji_map.get(niche.lower(), "⭐")

    tone_templates = {
        "professional": f"{niche_emoji} {niche.title()} Expert\nHelping you master {niche} | Daily tips\n{cta_text}",
        "casual": f"{niche_emoji} your go-to for {niche} content\ndaily inspo & real talk\n{cta_text}",
        "authority": f"#{niche.title()} Creator | {niche.title()} Coach\nTrusted by 10K+ | No fluff, just results\n{cta_text}",
        "community": f"Building the best {niche} community 🌍\nJoin {niche} lovers worldwide\n{cta_text}",
    }

    templates: List[Dict[str, str]] = []
    for tone_name, template in tone_templates.items():
        char_count = len(template)
        templates.append({
            "tone": tone_name,
            "bio": template,
            "char_count": str(char_count),
            "within_limit": str(char_count <= max_len),
        })

    primary = tone_templates.get(tone, tone_templates["professional"])

    return {
        "account_id": account_id,
        "platform": platform,
        "char_limit": max_len,
        "recommended_bio": primary,
        "char_count": len(primary),
        "alternatives": templates,
        "tips": [
            "Put the most important info in line 1 (shown in previews)",
            f"Keep under {max_len} chars to avoid truncation",
            "Include niche keywords for search discoverability",
            "Use line breaks to improve readability",
            "Update bio every 30-60 days to reflect current offers",
        ],
    }


def update_account(
    sess: Session,
    account_id: str,
    **kwargs: Any,
) -> Dict[str, Any]:
    if account_id not in sess.config["accounts"]:
        raise KeyError(f"Account '{account_id}' not found.")
    sess.snapshot(f"update account {account_id}")
    account = sess.config["accounts"][account_id]
    allowed = {"bio", "followers", "niche", "goals", "username"}
    updated = []
    for k, v in kwargs.items():
        if k in allowed and v is not None:
            account[k] = v
            updated.append(k)
    return {"success": True, "account_id": account_id, "updated_fields": updated}


def bulk_audit(sess: Session) -> Dict[str, Any]:
    accounts = sess.config.get("accounts", {})
    if not accounts:
        raise RuntimeError("No accounts configured. Add accounts with 'accounts add'.")

    results = []
    for account_id in accounts:
        try:
            audit = audit_account(sess, account_id)
            results.append({
                "account_id": account_id,
                "username": audit["username"],
                "platform": audit["platform"],
                "score": audit["score"],
                "grade": audit["grade"],
                "issue_count": len(audit["issues"]),
                "top_issue": audit["issues"][0]["issue"] if audit["issues"] else "None",
            })
        except Exception as e:
            results.append({"account_id": account_id, "error": str(e)})

    results.sort(key=lambda r: r.get("score", 0))
    return {
        "total_accounts": len(results),
        "avg_score": round(
            sum(r.get("score", 0) for r in results) / len(results), 1
        ) if results else 0,
        "accounts": results,
        "audited_at": datetime.now().isoformat(),
    }


def get_posting_schedule(
    sess: Session,
    account_id: str,
    frequency: str = "daily",
) -> Dict[str, Any]:
    account = get_account(sess, account_id)
    platform = account["platform"]
    configured_times = sess.config.get("posting_times", {}).get(platform, [])

    schedules = {
        "daily": {
            "posts_per_day": 1,
            "times": configured_times[:1] or ["7:00 PM EST"],
        },
        "aggressive": {
            "posts_per_day": 3,
            "times": configured_times or ["7:00 AM", "12:00 PM", "7:00 PM"],
        },
        "weekly": {
            "posts_per_week": 5,
            "days": ["Monday", "Tuesday", "Thursday", "Friday", "Saturday"],
            "times": configured_times[:1] or ["6:00 PM EST"],
        },
    }

    schedule = schedules.get(frequency, schedules["daily"])
    return {
        "account_id": account_id,
        "platform": platform,
        "niche": account.get("niche", ""),
        "frequency": frequency,
        "schedule": schedule,
        "content_calendar_template": _content_calendar(account.get("niche", "general"), platform),
        "tip": "Batch-create 7 days of content in 1 session to stay consistent.",
    }


def _content_calendar(niche: str, platform: str) -> List[Dict[str, str]]:
    """Weekly content template by niche."""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    templates = {
        "fitness": ["Workout tutorial", "Transformation story", "Myth busting", "Q&A / tips",
                    "Trending sound + exercise", "Rest day motivation", "Week recap"],
        "finance": ["Money tip", "Mistake to avoid", "Success story", "Tool review",
                    "POV money scenario", "Weekend challenge", "Week recap"],
        "motivation": ["Morning motivation", "Mindset shift", "Story time", "Quote breakdown",
                       "Challenge day", "Community post", "Week reflection"],
    }
    template = templates.get(niche.lower(), [
        "Educational tip", "Story/POV", "Tutorial", "Trending sound post",
        "Community/Q&A", "Behind the scenes", "Week recap",
    ])
    return [{"day": days[i], "content_type": template[i]} for i in range(7)]
