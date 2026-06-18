"""Account optimization engine — bio, posting schedule, engagement, growth hacks."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_PROFILES_PATH = Path.home() / ".cli-anything-social" / "accounts"

# ── Best posting times (all times in user's LOCAL timezone) ──────────────────

_BEST_TIMES: dict[str, dict[str, list[str]]] = {
    "tiktok": {
        "Monday":    ["6:00 AM", "10:00 AM", "10:00 PM"],
        "Tuesday":   ["2:00 AM",  "4:00 AM",  "9:00 AM"],
        "Wednesday": ["7:00 AM",  "8:00 AM", "11:00 PM"],
        "Thursday":  ["9:00 AM", "12:00 PM",  "7:00 PM"],
        "Friday":    ["5:00 AM", "1:00 PM",   "3:00 PM"],
        "Saturday":  ["11:00 AM","7:00 PM",   "8:00 PM"],
        "Sunday":    ["7:00 AM",  "8:00 AM",  "4:00 PM"],
    },
    "instagram": {
        "Monday":    ["6:00 AM", "11:00 AM",  "1:00 PM"],
        "Tuesday":   ["8:00 AM", "11:00 AM",  "1:00 PM"],
        "Wednesday": ["9:00 AM", "11:00 AM",  "1:00 PM"],
        "Thursday":  ["12:00 PM","1:00 PM",   "5:00 PM"],
        "Friday":    ["5:00 AM", "12:00 PM",  "1:00 PM"],
        "Saturday":  ["11:00 AM","12:00 PM",  "1:00 PM"],
        "Sunday":    ["7:00 AM", "8:00 AM",  "12:00 PM"],
    },
    "youtube": {
        "Monday":    ["2:00 PM",  "3:00 PM",  "4:00 PM"],
        "Tuesday":   ["2:00 PM",  "3:00 PM",  "4:00 PM"],
        "Wednesday": ["2:00 PM",  "3:00 PM",  "4:00 PM"],
        "Thursday":  ["12:00 PM", "1:00 PM",  "3:00 PM"],
        "Friday":    ["12:00 PM", "1:00 PM",  "2:00 PM"],
        "Saturday":  ["9:00 AM", "10:00 AM", "11:00 AM"],
        "Sunday":    ["9:00 AM", "10:00 AM", "11:00 AM"],
    },
    "twitter": {
        "Monday":    ["8:00 AM",  "12:00 PM",  "5:00 PM"],
        "Tuesday":   ["9:00 AM",  "12:00 PM",  "5:00 PM"],
        "Wednesday": ["9:00 AM",  "12:00 PM",  "4:00 PM"],
        "Thursday":  ["9:00 AM",  "12:00 PM",  "5:00 PM"],
        "Friday":    ["8:00 AM",  "12:00 PM",  "3:00 PM"],
        "Saturday":  ["9:00 AM",  "12:00 PM",  "1:00 PM"],
        "Sunday":    ["9:00 AM",  "12:00 PM",  "1:00 PM"],
    },
}

# ── Engagement rate benchmarks by platform ────────────────────────────────────

_ENGAGEMENT_BENCHMARKS: dict[str, dict[str, dict[str, float]]] = {
    "instagram": {
        "poor":    {"min": 0.0,  "max": 1.0},
        "average": {"min": 1.0,  "max": 3.5},
        "good":    {"min": 3.5,  "max": 6.0},
        "great":   {"min": 6.0,  "max": 10.0},
        "viral":   {"min": 10.0, "max": 100.0},
    },
    "tiktok": {
        "poor":    {"min": 0.0,  "max": 3.0},
        "average": {"min": 3.0,  "max": 6.0},
        "good":    {"min": 6.0,  "max": 12.0},
        "great":   {"min": 12.0, "max": 20.0},
        "viral":   {"min": 20.0, "max": 100.0},
    },
    "youtube": {
        "poor":    {"min": 0.0,  "max": 1.0},
        "average": {"min": 1.0,  "max": 2.0},
        "good":    {"min": 2.0,  "max": 4.0},
        "great":   {"min": 4.0,  "max": 8.0},
        "viral":   {"min": 8.0,  "max": 100.0},
    },
}


@dataclass
class AccountProfile:
    platform: str
    handle: str
    niche: str
    bio: str = ""
    followers: int = 0
    following: int = 0
    posts: int = 0
    avg_likes: float = 0.0
    avg_comments: float = 0.0
    avg_views: float = 0.0
    avg_shares: float = 0.0
    posting_frequency: float = 1.0  # posts/day
    account_age_days: int = 0
    timezone: str = "US/Eastern"
    link_in_bio: str = ""
    notes: str = ""
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def save_profile(profile: AccountProfile) -> Path:
    _PROFILES_PATH.mkdir(parents=True, exist_ok=True)
    path = _PROFILES_PATH / f"{profile.platform}_{profile.handle}.json"
    path.write_text(json.dumps(asdict(profile), indent=2))
    return path


def load_profile(platform: str, handle: str) -> AccountProfile | None:
    path = _PROFILES_PATH / f"{platform}_{handle}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return AccountProfile(**data)
    except Exception:
        return None


def list_profiles() -> list[dict]:
    _PROFILES_PATH.mkdir(parents=True, exist_ok=True)
    profiles = []
    for p in sorted(_PROFILES_PATH.glob("*.json")):
        try:
            data = json.loads(p.read_text())
            profiles.append({
                "platform": data.get("platform"),
                "handle": data.get("handle"),
                "niche": data.get("niche"),
                "followers": data.get("followers", 0),
                "updated_at": data.get("updated_at", ""),
            })
        except Exception:
            continue
    return profiles


# ── Bio analysis ──────────────────────────────────────────────────────────────

def analyze_bio(bio: str, platform: str, niche: str) -> dict:
    """Score and improve a social media bio."""
    suggestions: list[str] = []
    score = 0

    if not bio:
        return {
            "score": 0,
            "suggestions": ["Add a bio — accounts with bios get 70% more profile visits."],
            "improved_bio": f"🎯 [Niche] content | [Value prop] | [CTA] ↓",
        }

    # Length check
    limits = {"tiktok": 80, "instagram": 150, "youtube": 1000, "twitter": 160}
    limit = limits.get(platform, 150)
    if len(bio) > limit:
        suggestions.append(f"Bio is too long for {platform} (max {limit} chars). Trim to essentials.")
    elif len(bio) < 30:
        suggestions.append("Bio is too short — add more value and context.")
    else:
        score += 20

    # CTA check
    cta_patterns = [r"link.*bio", r"click.*below", r"follow", r"dm", r"check", r"shop", r"get"]
    has_cta = any(re.search(p, bio.lower()) for p in cta_patterns)
    if has_cta:
        score += 20
    else:
        suggestions.append("Add a clear CTA: 'Link below ↓', 'DM me', 'Shop now'.")

    # Emoji check
    emoji_count = len(re.findall(r'[^\x00-\x7F]', bio))
    if 1 <= emoji_count <= 5:
        score += 15
    elif emoji_count == 0:
        suggestions.append("Add 1–3 emojis — they increase visual scanning and click-through.")
    else:
        suggestions.append("Too many emojis — keep to 3–5 max for professionalism.")

    # Keyword check
    if niche.lower() in bio.lower():
        score += 20
    else:
        suggestions.append(f"Include your niche keyword '{niche}' in the bio for search visibility.")

    # Line breaks (Instagram)
    if platform == "instagram" and "\n" not in bio:
        suggestions.append("Use line breaks in your Instagram bio — it's easier to scan.")
        suggestions.append("Format: Line 1: Who you are | Line 2: What you post | Line 3: CTA")

    # Value proposition
    value_words = ["tips", "how to", "learn", "guide", "hacks", "best", "top", "free"]
    has_value = any(w in bio.lower() for w in value_words)
    if has_value:
        score += 15
    else:
        suggestions.append("Add a value proposition: tell visitors WHAT they gain by following.")

    # Link in bio
    has_link = "link" in bio.lower() or "↓" in bio or "bio" in bio.lower()
    if has_link:
        score += 10
    else:
        suggestions.append("Reference your link: 'Free guide in link below ↓'")

    # Build improved version
    niche_emoji = {"fitness": "💪", "finance": "💰", "food": "🍴", "travel": "✈️",
                   "fashion": "👗", "beauty": "💄", "tech": "💻", "gaming": "🎮",
                   "motivation": "🔥", "pets": "🐾", "luxury lifestyle": "💎"}.get(niche, "🎯")

    improved = (
        f"{niche_emoji} {niche.title()} content & tips\n"
        f"📌 [Your unique value prop]\n"
        f"👇 Free [resource] in link below"
    )

    return {
        "score": min(100, score),
        "rating": "great" if score >= 80 else "good" if score >= 60 else "needs work",
        "suggestions": suggestions,
        "improved_bio": improved,
        "character_count": len(bio),
        "platform_limit": limit,
    }


# ── Engagement analysis ───────────────────────────────────────────────────────

def engagement_rate_analysis(
    followers: int,
    avg_likes: float,
    avg_comments: float,
    avg_views: float = 0,
    avg_shares: float = 0,
    platform: str = "instagram",
) -> dict:
    """Calculate and benchmark engagement rate."""
    if followers == 0:
        return {"error": "followers cannot be 0"}

    base = avg_views if platform == "tiktok" and avg_views > 0 else followers
    eng_rate = ((avg_likes + avg_comments * 2 + avg_shares * 3) / base) * 100

    benchmarks = _ENGAGEMENT_BENCHMARKS.get(platform, _ENGAGEMENT_BENCHMARKS["instagram"])
    tier = "poor"
    for t_name, t_range in benchmarks.items():
        if t_range["min"] <= eng_rate < t_range["max"]:
            tier = t_name
            break

    suggestions = []
    if tier in ("poor", "average"):
        suggestions.extend([
            "Post in the first hour: reply to every comment to signal engagement to the algorithm.",
            "Ask a question in your caption to drive comments.",
            "Share your post to Stories immediately after posting (Instagram).",
            "Repost to TikTok from Instagram to cross-pollinate engagement.",
            "Use polls and Q&As in Stories — they count toward engagement.",
        ])
    elif tier == "good":
        suggestions.extend([
            "Test different hook styles — you're on the right track but can go further.",
            "Experiment with carousels on Instagram (highest save rate).",
            "Add a strong CTA at the end of every video.",
        ])
    else:
        suggestions.append("Strong engagement! Focus on converting this audience to email/product buyers.")

    return {
        "engagement_rate": round(eng_rate, 2),
        "tier": tier,
        "benchmark_context": benchmarks,
        "follower_count": followers,
        "avg_likes": avg_likes,
        "avg_comments": avg_comments,
        "suggestions": suggestions,
    }


# ── Posting schedule optimizer ────────────────────────────────────────────────

def optimize_posting_schedule(
    platform: str,
    niche: str,
    posts_per_week: int = 7,
    timezone_str: str = "US/Eastern",
) -> dict:
    """Return the optimal posting schedule for a platform + niche combo."""
    schedule = _BEST_TIMES.get(platform, _BEST_TIMES["instagram"])
    days = list(schedule.keys())

    # Weight weekend higher for lifestyle niches, weekdays for finance/tech
    lifestyle_niches = {"fitness", "beauty", "food", "travel", "fashion", "pets", "motivation"}
    finance_niches = {"personal finance", "crypto / web3", "tech"}

    if niche in lifestyle_niches:
        preferred = ["Saturday", "Sunday", "Friday", "Monday", "Tuesday", "Wednesday", "Thursday"]
    elif niche in finance_niches:
        preferred = ["Tuesday", "Wednesday", "Thursday", "Monday", "Friday", "Saturday", "Sunday"]
    else:
        preferred = days

    selected_days = preferred[:posts_per_week]
    posting_plan = []

    for day in selected_days:
        times = schedule.get(day, ["12:00 PM"])
        posting_plan.append({
            "day": day,
            "times": times[:2],
            "content_tip": _content_tip_for_day(day, niche),
        })

    return {
        "platform": platform,
        "niche": niche,
        "timezone": timezone_str,
        "posts_per_week": posts_per_week,
        "schedule": posting_plan,
        "general_advice": [
            f"On {platform}, the algorithm rewards consistent posting over sporadic bursts.",
            "Batch-create content once or twice a week to stay ahead.",
            "Post at the same times daily to train your audience.",
            f"{'3x/day is optimal for TikTok growth' if platform == 'tiktok' else '1x/day is optimal for Instagram growth' if platform == 'instagram' else 'Upload 2–3x/week for YouTube'}.",
        ],
    }


def _content_tip_for_day(day: str, niche: str) -> str:
    tips: dict[str, str] = {
        "Monday":    "Motivational content — people need encouragement to start the week.",
        "Tuesday":   "Educational content — audience is focused and receptive mid-week.",
        "Wednesday": "Tutorial/how-to — high engagement day for practical content.",
        "Thursday":  "Product/review content — buying intent is highest Thu–Fri.",
        "Friday":    "Relatable/humorous content — people are in a good mood.",
        "Saturday":  "Aspirational/lifestyle content — people are in discovery mode.",
        "Sunday":    "Inspirational/planning content — people are prepping for the week.",
    }
    return tips.get(day, "Consistent posting is more important than perfect timing.")


# ── Full account audit ────────────────────────────────────────────────────────

def full_account_audit(profile: AccountProfile) -> dict:
    """Run a comprehensive account audit with actionable improvements."""
    bio_analysis = analyze_bio(profile.bio, profile.platform, profile.niche)
    eng_analysis = engagement_rate_analysis(
        followers=profile.followers,
        avg_likes=profile.avg_likes,
        avg_comments=profile.avg_comments,
        avg_views=profile.avg_views,
        avg_shares=profile.avg_shares,
        platform=profile.platform,
    )
    schedule = optimize_posting_schedule(
        platform=profile.platform,
        niche=profile.niche,
        posts_per_week=7,
        timezone_str=profile.timezone,
    )

    # Overall score
    scores = {
        "bio": bio_analysis.get("score", 0),
        "engagement": {
            "viral": 100, "great": 85, "good": 65, "average": 45, "poor": 20
        }.get(eng_analysis.get("tier", "poor"), 20),
        "posting_frequency": min(100, profile.posting_frequency * 33),
        "link_in_bio": 100 if profile.link_in_bio else 0,
    }
    overall = sum(scores.values()) / len(scores)

    growth_hacks = _platform_growth_hacks(profile.platform, profile.niche, profile.followers)

    return {
        "platform": profile.platform,
        "handle": f"@{profile.handle}",
        "niche": profile.niche,
        "overall_score": round(overall, 1),
        "scores": scores,
        "bio_analysis": bio_analysis,
        "engagement_analysis": eng_analysis,
        "posting_schedule": schedule,
        "growth_hacks": growth_hacks,
        "quick_wins": _quick_wins(profile, bio_analysis, eng_analysis),
        "audited_at": datetime.now(timezone.utc).isoformat(),
    }


def _quick_wins(
    profile: AccountProfile,
    bio: dict,
    eng: dict,
) -> list[str]:
    wins = []
    if not profile.link_in_bio:
        wins.append("Add a link in bio immediately (Stan.store or Beacons.ai — free).")
    if bio.get("score", 0) < 60:
        wins.append("Rewrite your bio using the improved template provided.")
    if eng.get("tier") in ("poor", "average"):
        wins.append("Reply to every comment within the first 60 min of posting — boosts distribution.")
    if profile.posting_frequency < 1:
        wins.append("Post at least once daily. Consistency beats quality in the growth phase.")
    if profile.following > profile.followers * 2:
        wins.append("High following-to-follower ratio hurts credibility. Clean up your following list.")
    wins.append("Add a Highlights cover on Instagram with niche-relevant icons from Canva.")
    wins.append("Pin your best-performing post to the top of your profile.")
    return wins


def _platform_growth_hacks(platform: str, niche: str, followers: int) -> list[str]:
    base = [
        "Comment first on big creator posts in your niche — early comments get visibility.",
        "Use 'search SEO' — include your niche keyword in your username and bio.",
        "Repost your best-performing content 6 weeks later (audiences rotate).",
    ]
    platform_specific: dict[str, list[str]] = {
        "tiktok": [
            "Go live for 30 min daily once you hit 1,000 followers — massive reach boost.",
            "Duet/stitch viral content in your niche within 24h of it trending.",
            "Post 3 videos per day during your first 30 days — raw volume beats everything.",
            "Reply to comments with video replies — they appear in For You Pages.",
            "Use TikTok's Text-to-Speech or trending voiceover sounds.",
        ],
        "instagram": [
            "Reels get 2–3x the reach of regular posts — make every post a Reel.",
            "Carousels get the most saves — target 'saved' posts for compounding traffic.",
            "Use 3–5 specific hashtags rather than 30 random ones (2024 algorithm).",
            "Post Stories 5–7x/day to stay at the top of followers' feeds.",
            "Collab posts (Collaboration feature) instantly double your reach.",
        ],
        "youtube": [
            "Front-load your video title with the keyword (YouTube is Google-owned).",
            "Custom thumbnails with faces + bold text outperform by 38%.",
            "Chapters (timestamps) increase watch time and searchability.",
            "Reply to every comment in the first 24h to boost comment velocity.",
            "Post YouTube Shorts of your best clips to drive traffic to long-form.",
        ],
        "twitter": [
            "Tweet threads outperform single tweets by 5x for reach.",
            "Engage with 10 viral tweets per day by adding value in comments.",
            "Schedule tweets at 8AM, 12PM, 5PM for maximum visibility.",
            "Use Twitter Spaces to build community and gain followers fast.",
        ],
    }
    return base + platform_specific.get(platform, [])
