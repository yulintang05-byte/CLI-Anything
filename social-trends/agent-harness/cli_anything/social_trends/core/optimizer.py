"""Account optimizer — generate per-account action plans from trend data."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from cli_anything.social_trends.utils.social_trends_backend import (
    CONFIG_DIR, SUPPORTED_NICHES,
)

ACCOUNTS_FILE = CONFIG_DIR / "accounts.json"

PLATFORM_BEST_TIMES: dict[str, list[str]] = {
    "tiktok":    ["6:00 AM", "10:00 AM", "7:00 PM", "9:00 PM", "11:00 PM"],
    "instagram": ["6:00 AM", "12:00 PM", "7:00 PM", "8:00 PM"],
    "youtube":   ["9:00 AM", "12:00 PM", "3:00 PM", "5:00 PM"],
    "twitter":   ["8:00 AM", "12:00 PM", "5:00 PM"],
}

PLATFORM_POSTING_FREQ: dict[str, str] = {
    "tiktok":    "3-5 videos/day",
    "instagram": "1-2 posts + 5-10 stories/day",
    "youtube":   "1 video/day or 3-4 Shorts/day",
    "twitter":   "5-10 tweets/day",
}

HASHTAG_STRATEGY: dict[str, dict] = {
    "tiktok":    {"total": 5, "mega": 1, "large": 2, "niche": 2},
    "instagram": {"total": 20, "mega": 3, "large": 7, "niche": 10},
    "youtube":   {"total": 8, "mega": 2, "large": 3, "niche": 3},
}


# ── Account Registry ───────────────────────────────────────────────────

def load_accounts() -> list[dict]:
    if not ACCOUNTS_FILE.exists():
        return []
    try:
        with open(ACCOUNTS_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_accounts(accounts: list[dict]):
    ACCOUNTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f, indent=2)
    ACCOUNTS_FILE.chmod(0o600)


def add_account(platform: str, username: str, niche: str, follower_count: int = 0) -> dict:
    accounts = load_accounts()
    account = {
        "platform": platform.lower(),
        "username": username,
        "niche": niche.lower(),
        "follower_count": follower_count,
        "added_at": datetime.now().isoformat(),
    }
    accounts = [a for a in accounts if not (a["platform"] == platform.lower() and a["username"] == username)]
    accounts.append(account)
    save_accounts(accounts)
    return account


def remove_account(platform: str, username: str) -> bool:
    accounts = load_accounts()
    before = len(accounts)
    accounts = [a for a in accounts if not (a["platform"] == platform.lower() and a["username"] == username)]
    if len(accounts) == before:
        return False
    save_accounts(accounts)
    return True


def list_accounts() -> list[dict]:
    return load_accounts()


# ── Optimizer ──────────────────────────────────────────────────────────

def optimize_account(
    platform: str,
    niche: str,
    trend_data: dict,
    follower_count: int = 0,
    username: str | None = None,
    *,
    followers: int | None = None,
) -> dict:
    """Generate a comprehensive optimization plan for one account.

    Args:
        trend_data: Output from trends.analyze_trends()

    Returns:
        Full optimization plan with hashtags, posting schedule, content ideas,
        bio recommendations, and monetization next steps.
    """
    if followers is not None:
        follower_count = followers
    platform = platform.lower()
    niche = niche.lower()

    top_hashtags = trend_data.get("top_hashtags", [])
    trending_sounds = trend_data.get("trending_sounds", [])
    content_patterns = trend_data.get("content_patterns", {})
    keywords = [kw["word"] for kw in content_patterns.get("top_keywords", [])[:10]]

    hashtag_plan = _build_hashtag_plan(platform, niche, top_hashtags)
    schedule = _build_posting_schedule(platform)
    content_ideas = _generate_content_ideas(niche, keywords, content_patterns)
    bio_tips = _bio_recommendations(platform, niche, follower_count)
    monetization = _monetization_roadmap(platform, niche, follower_count)
    sound_tips = _sound_recommendations(trending_sounds, platform)

    return {
        "account": {"platform": platform, "username": username or "your account", "niche": niche},
        "optimization_score": _compute_optimization_score(follower_count, platform),
        "hashtag_plan": hashtag_plan,
        "posting_schedule": schedule,
        "content_ideas": content_ideas,
        "bio_recommendations": bio_tips,
        "trending_sounds_to_use": sound_tips,
        "monetization_roadmap": monetization,
        "quick_wins": _quick_wins(platform, niche, top_hashtags),
    }


def _build_hashtag_plan(platform: str, niche: str, top_hashtags: list[dict]) -> dict:
    strategy = HASHTAG_STRATEGY.get(platform, {"total": 10, "mega": 2, "large": 4, "niche": 4})

    # Filter hashtags relevant to niche
    niche_words = set(niche.lower().split() + [niche])
    niche_tags = [h for h in top_hashtags if any(w in h["hashtag"].lower() for w in niche_words)]
    general_tags = [h for h in top_hashtags if h not in niche_tags]

    mega = [h["hashtag"] for h in general_tags[:strategy["mega"]]]
    large = [h["hashtag"] for h in general_tags[strategy["mega"]:strategy["mega"]+strategy["large"]]]
    niche_specific = [h["hashtag"] for h in niche_tags[:strategy["niche"]]]

    # Fill remaining with general if not enough niche tags
    deficit = strategy["niche"] - len(niche_specific)
    if deficit > 0:
        extra_start = strategy["mega"] + strategy["large"]
        niche_specific += [h["hashtag"] for h in general_tags[extra_start:extra_start+deficit]]

    return {
        "platform": platform,
        "recommended_total": strategy["total"],
        "mega_hashtags": mega,
        "large_hashtags": large,
        "niche_hashtags": niche_specific,
        "example_combo": (mega[:1] + large[:2] + niche_specific[:2])[:strategy["total"]],
        "tip": f"Rotate 3-5 different combos to avoid shadowban on {platform}",
    }


def _build_posting_schedule(platform: str) -> dict:
    best_times = PLATFORM_BEST_TIMES.get(platform, ["9:00 AM", "5:00 PM"])
    freq = PLATFORM_POSTING_FREQ.get(platform, "1-3/day")

    # Generate a 7-day calendar
    today = datetime.now()
    calendar = []
    for i in range(7):
        day = today + timedelta(days=i)
        times_today = best_times[: (2 if i % 2 == 0 else 3)]
        calendar.append({
            "date": day.strftime("%Y-%m-%d"),
            "day": day.strftime("%A"),
            "post_times": times_today,
            "post_count": len(times_today),
        })

    return {
        "platform": platform,
        "recommended_frequency": freq,
        "best_times": best_times,
        "timezone": "EST (adjust to your audience timezone)",
        "7_day_calendar": calendar,
        "tip": "Consistency beats virality — post at the same times daily for 30 days",
    }


def _generate_content_ideas(niche: str, keywords: list[str], patterns: dict) -> list[dict]:
    formats = patterns.get("title_formats", {})
    ideas = []

    templates = [
        ("List video", f"[Number] {niche.title()} Tips That Actually Work"),
        ("How-to", f"How To [Action] Your {niche.title()} In 60 Seconds"),
        ("Reaction/Review", f"I Tried [Viral {niche.title()} Trend] — Here's What Happened"),
        ("Storytime", f"The {niche.title()} Secret No One Talks About"),
        ("Day in the Life", f"Day In The Life Of A Successful {niche.title()} Creator"),
        ("Hot Takes", f"Unpopular Opinion: [Controversial {niche.title()} Take]"),
        ("Comparison", f"[Option A] vs [Option B] {niche.title()} — Which Is Better?"),
        ("Tutorial", f"Beginner {niche.title()} Tutorial (0 To 10K Followers)"),
        ("Trend response", f"Reacting To The Latest {niche.title()} Trend 👀"),
        ("Behind the scenes", f"Behind The Scenes Of My {niche.title()} Content"),
    ]

    # Weight towards formats that are actually trending
    if formats.get("list_videos_pct", 0) > 20:
        templates = [templates[0]] * 2 + templates[1:]
    if formats.get("howto_videos_pct", 0) > 15:
        templates = [templates[1]] * 2 + templates

    for fmt, title_template in templates[:8]:
        kw_inject = keywords[0] if keywords else niche
        ideas.append({
            "format": fmt,
            "title_template": title_template,
            "suggested_keywords": keywords[:3],
            "hook_tip": f"Start with: 'If you're into {kw_inject}, watch this…'",
        })
    return ideas


def _bio_recommendations(platform: str, niche: str, followers: int) -> list[str]:
    tips = [
        f"Clear niche statement: '{niche.title()} content daily' or '{niche.title()} tips + tricks'",
        "Include 1 clear CTA: 'Follow for daily [niche] content'",
        "Add a link-in-bio tool (Linktree, Stan Store, or Beacons) with your best offers",
        "Use 1-2 relevant emojis to break up text visually",
        "State WHO you help: 'Helping [audience] achieve [outcome] with [niche]'",
    ]
    if platform == "tiktok":
        tips.append("Add your Instagram/YouTube handle to drive cross-platform followers")
    if platform == "instagram":
        tips.append("Use all 150 bio characters — SEO keywords help discoverability")
        tips.append("Pinned stories as bio extension: Products, About, Links")
    if followers > 10000:
        tips.append("Add social proof: '100K+ followers' or 'Featured in [outlet]'")
    return tips


def _monetization_roadmap(platform: str, niche: str, followers: int) -> list[dict]:
    stages = []

    if followers < 1000:
        stages.append({
            "stage": "0-1K: Foundation",
            "focus": "Build content library, establish niche authority",
            "actions": [
                "Post 3-5x/day minimum",
                "Engage in comments of similar accounts",
                "Join niche communities and collaborate",
                "Set up email capture (free lead magnet)",
            ],
            "monetization": "Not yet — focus on growth",
        })
    elif followers < 10000:
        stages.append({
            "stage": "1K-10K: Early Monetization",
            "focus": "Affiliate marketing + paid shoutouts",
            "actions": [
                "Join affiliate programs (Amazon Associates, impact.com, ShareASale)",
                "Sell shoutouts at $10-50/post",
                "Create a simple digital product (PDF guide, template)",
                "Apply for brand partnerships in your niche",
            ],
            "monetization": "Affiliate links, shoutouts ($10-50), digital products ($9-47)",
        })
    elif followers < 100000:
        stages.append({
            "stage": "10K-100K: Scale Revenue",
            "focus": "Brand deals + own products",
            "actions": [
                "Pitch brands directly (email in bio or via Instagram DMs)",
                "Price shoutouts at $100-500/post",
                "Launch a paid community or membership ($9-49/month)",
                "Create a course or coaching offer ($97-997)",
            ],
            "monetization": "Brand deals ($100-500), courses ($97+), memberships ($9-49/mo)",
        })
    else:
        stages.append({
            "stage": "100K+: Maximize Revenue",
            "focus": "Premium deals + recurring revenue",
            "actions": [
                "Negotiate brand exclusivity deals ($1,000-10,000/post)",
                "Launch own product line or SaaS",
                "Hire a social media manager to scale content",
                "Speaking engagements and events",
            ],
            "monetization": "Brand exclusives ($1K-10K), products, courses, events",
        })

    platform_specific = {
        "tiktok": "Apply for TikTok Creator Rewards Program (min 10K followers + 100K views/30 days)",
        "instagram": "Enable Instagram Subscriptions for exclusive content ($0.99-99/month)",
        "youtube": "Monetize with AdSense once 1,000 subscribers + 4,000 watch hours",
    }
    if platform in platform_specific:
        stages.append({
            "stage": "Platform Monetization",
            "focus": platform_specific[platform],
            "actions": [],
            "monetization": platform_specific[platform],
        })

    return stages


def _sound_recommendations(trending_sounds: list[dict], platform: str) -> list[dict]:
    if platform != "tiktok" or not trending_sounds:
        return []
    tips = []
    for sound in trending_sounds[:5]:
        tips.append({
            "title": sound.get("title", ""),
            "artist": sound.get("artist", ""),
            "video_count": sound.get("video_count", 0),
            "action": f"Use this sound NOW — {sound.get('video_count',0)} trending videos using it",
        })
    return tips


def _quick_wins(platform: str, niche: str, top_hashtags: list[dict]) -> list[str]:
    wins = [
        f"Pin your best-performing {niche} video to the top of your profile",
        "Reply to every comment in the first hour after posting (boosts algorithm)",
        f"Duet or stitch a viral {niche} video to piggyback on existing momentum",
    ]
    if top_hashtags:
        wins.append(
            f"Post under {top_hashtags[0]['hashtag']} in the next 24h — "
            f"it has {top_hashtags[0].get('total_views', 0):,} total trend views"
        )
    if platform == "tiktok":
        wins.append("Go LIVE for 30+ min/day — TikTok heavily rewards live accounts")
    if platform == "instagram":
        wins.append("Post a Reel using a trending audio from TikTok within 48h of it trending")
    return wins


def _compute_optimization_score(followers: int, platform: str) -> dict:
    score = min(100, max(0, int(50 + (followers / 1000) * 2)))
    level = "Starter" if score < 40 else ("Growing" if score < 70 else ("Established" if score < 90 else "Authority"))
    return {
        "score": score,
        "level": level,
        "next_milestone": _next_milestone(followers),
    }


def _next_milestone(followers: int) -> str:
    milestones = [100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]
    for m in milestones:
        if followers < m:
            return f"{m:,} followers"
    return "1M+ (mega-influencer)"


def optimize_all_accounts(trend_data: dict) -> list[dict]:
    """Run optimization for all registered accounts."""
    accounts = load_accounts()
    if not accounts:
        return []
    results = []
    for acc in accounts:
        plan = optimize_account(
            platform=acc["platform"],
            niche=acc["niche"],
            trend_data=trend_data,
            follower_count=acc.get("follower_count", 0),
            username=acc.get("username"),
        )
        results.append(plan)
    return results
