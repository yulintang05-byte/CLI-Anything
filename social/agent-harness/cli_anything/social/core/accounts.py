"""Account optimization — profile audits, bio generation, posting strategy.

Provides data-driven recommendations for optimising social media accounts
across TikTok, YouTube, and Instagram. Pulls public profile stats via
platform APIs where available and produces structured audit reports.

YouTube: requires YouTube Data API v3 key.
TikTok:  uses TikTok web API (sessionid cookie for authenticated access).
Instagram: uses public profile JSON endpoint (no auth required).
"""

import re
import json
import datetime
import requests
from typing import Optional

from cli_anything.social.core.trends import (
    YOUTUBE_API_BASE,
    TIKTOK_API_BASE,
    TIKTOK_HEADERS,
    _safe_int,
    _now_iso,
)

# ── Platform best-practice benchmarks ────────────────────────────────────────

PLATFORM_BENCHMARKS = {
    "tiktok": {
        "bio_max_chars": 80,
        "username_max_chars": 24,
        "daily_post_target": (1, 4),          # (min, max) posts per day
        "optimal_video_length_sec": (21, 34),  # proven FYP range
        "max_hashtags_per_post": 5,
        "min_hashtags_per_post": 3,
        "engagement_good": 5.0,               # % engagement rate threshold
        "engagement_great": 15.0,
    },
    "youtube": {
        "bio_max_chars": 1000,
        "title_max_chars": 100,
        "description_first_line_chars": 157,  # visible before "show more"
        "daily_post_target": (0, 1),
        "weekly_post_target": (3, 5),
        "optimal_video_length_min": (8, 15),   # minutes for watch time
        "shorts_length_sec": (15, 60),
        "max_tags": 15,
        "engagement_good": 4.0,
        "engagement_great": 8.0,
    },
    "instagram": {
        "bio_max_chars": 150,
        "username_max_chars": 30,
        "daily_post_target": (1, 2),
        "reels_length_sec": (7, 30),
        "max_hashtags_per_post": 30,
        "min_hashtags_per_post": 10,
        "engagement_good": 3.0,
        "engagement_great": 6.0,
    },
}

# ── Niche-specific keyword banks ──────────────────────────────────────────────

NICHE_KEYWORDS: dict[str, list[str]] = {
    "fitness": [
        "workout", "gains", "fitlife", "gym", "motivation", "shred",
        "protein", "transform", "strength", "cardio",
    ],
    "beauty": [
        "makeup", "skincare", "glow", "tutorial", "routine", "glam",
        "aesthetic", "beauty", "hair", "nails",
    ],
    "finance": [
        "money", "investing", "wealth", "budget", "stocks", "crypto",
        "passive income", "financial freedom", "savings", "side hustle",
    ],
    "food": [
        "recipe", "foodie", "cooking", "delicious", "eats", "homemade",
        "viral recipe", "mukbang", "restaurant", "healthy eating",
    ],
    "travel": [
        "travel", "wanderlust", "adventure", "explore", "destination",
        "backpacking", "luxury travel", "hidden gems", "road trip", "solo travel",
    ],
    "gaming": [
        "gaming", "gameplay", "gamer", "esports", "streamer", "twitch",
        "playthrough", "tips", "pro", "highlights",
    ],
    "lifestyle": [
        "lifestyle", "vlog", "day in my life", "aesthetic", "routine",
        "minimalist", "self care", "productivity", "morning routine", "habits",
    ],
    "tech": [
        "tech", "review", "unboxing", "tutorial", "ai", "gadgets",
        "smartphone", "software", "coding", "innovation",
    ],
    "motivation": [
        "motivation", "mindset", "success", "grind", "hustle", "inspire",
        "goals", "discipline", "growth", "believe",
    ],
    "entertainment": [
        "viral", "funny", "trending", "comedy", "reactions", "challenge",
        "duet", "prank", "storytelling", "drama",
    ],
}


# ── YouTube account audit ─────────────────────────────────────────────────────

def audit_youtube_channel(
    channel_id: str,
    api_key: str,
) -> dict:
    """Fetch and audit a YouTube channel's public stats.

    Args:
        channel_id: YouTube channel ID (UCxxxxxxxx) or handle (@username).
        api_key: YouTube Data API v3 key.

    Returns:
        Dict with channel stats, engagement metrics, and optimization tips.
    """
    # Resolve handle to channel ID if needed
    if channel_id.startswith("@"):
        channel_id = _resolve_youtube_handle(channel_id, api_key)

    params = {
        "key": api_key,
        "part": "snippet,statistics,brandingSettings",
        "id": channel_id,
    }
    resp = requests.get(
        f"{YOUTUBE_API_BASE}/channels", params=params, timeout=20
    )
    resp.raise_for_status()
    data = resp.json()

    if not data.get("items"):
        raise RuntimeError(f"YouTube channel not found: {channel_id}")

    item = data["items"][0]
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    branding = item.get("brandingSettings", {}).get("channel", {})

    subscribers = _safe_int(stats.get("subscriberCount", 0))
    view_count = _safe_int(stats.get("viewCount", 0))
    video_count = _safe_int(stats.get("videoCount", 0))
    avg_views = view_count // max(video_count, 1)

    bio = snippet.get("description", "")
    bio_score = _score_bio(bio, "youtube")

    tips = _generate_youtube_tips(
        bio=bio,
        subscribers=subscribers,
        avg_views=avg_views,
        video_count=video_count,
        branding=branding,
    )

    return {
        "platform": "youtube",
        "channel_id": channel_id,
        "handle": snippet.get("customUrl", ""),
        "name": snippet.get("title", ""),
        "bio": bio,
        "created_at": snippet.get("publishedAt", ""),
        "country": snippet.get("country", ""),
        "subscribers": subscribers,
        "total_views": view_count,
        "video_count": video_count,
        "avg_views_per_video": avg_views,
        "bio_score": bio_score,
        "keywords": snippet.get("keywords", ""),
        "audit_at": _now_iso(),
        "tips": tips,
    }


def _resolve_youtube_handle(handle: str, api_key: str) -> str:
    """Resolve a @handle to a channel ID via YouTube search."""
    params = {
        "key": api_key,
        "part": "snippet",
        "q": handle,
        "type": "channel",
        "maxResults": 1,
    }
    resp = requests.get(
        f"{YOUTUBE_API_BASE}/search", params=params, timeout=20
    )
    resp.raise_for_status()
    items = resp.json().get("items", [])
    if not items:
        raise RuntimeError(f"Could not resolve YouTube handle: {handle}")
    return items[0]["id"]["channelId"]


def _score_bio(bio: str, platform: str) -> dict:
    """Score a bio on a 0-100 scale across key dimensions."""
    benchmarks = PLATFORM_BENCHMARKS.get(platform, {})
    max_chars = benchmarks.get("bio_max_chars", 150)
    length = len(bio)

    scores = {}

    # Length score (penalise empty or too-short; reward filling the space)
    if length == 0:
        scores["length"] = 0
    elif length < 20:
        scores["length"] = 20
    elif length <= max_chars:
        scores["length"] = min(100, int(length / max_chars * 100) + 30)
    else:
        scores["length"] = 60  # too long

    # Call-to-action score
    cta_patterns = [
        r"link in bio", r"follow", r"subscribe", r"dm me", r"click",
        r"shop now", r"book", r"join", r"sign up", r"check out",
    ]
    has_cta = any(re.search(p, bio, re.IGNORECASE) for p in cta_patterns)
    scores["has_cta"] = 100 if has_cta else 0

    # Emoji score (emojis increase engagement on TikTok/Instagram)
    emoji_count = len(re.findall(
        r"[\U0001F300-\U0001FFFF☀-⛿✀-➿]", bio
    ))
    if platform in ("tiktok", "instagram"):
        scores["emojis"] = min(100, emoji_count * 25) if emoji_count else 0
    else:
        scores["emojis"] = 50  # neutral for YouTube

    # Keyword clarity score
    word_count = len(bio.split())
    scores["clarity"] = min(100, word_count * 8) if word_count else 0

    overall = int(sum(scores.values()) / len(scores))
    return {"overall": overall, "breakdown": scores}


def _generate_youtube_tips(
    bio: str,
    subscribers: int,
    avg_views: int,
    video_count: int,
    branding: dict,
) -> list[str]:
    tips = []

    if not bio or len(bio) < 50:
        tips.append(
            "Bio is too short. Add your niche, upload schedule, "
            "and a call-to-action. Aim for 150-300 characters."
        )

    if subscribers < 1000:
        tips.append(
            "Focus on YouTube Shorts (60s) to accelerate early growth. "
            "Shorts get boosted distribution for channels under 1K subs."
        )

    if video_count < 10:
        tips.append(
            "Post at least 20 videos before judging performance. "
            "Consistency in the first 90 days is the #1 growth factor."
        )

    if avg_views < 500 and subscribers > 500:
        tips.append(
            "Low avg views relative to subscribers — improve your "
            "thumbnails (add text overlay + face) and title hooks."
        )

    if not branding.get("keywords"):
        tips.append(
            "Add channel keywords in YouTube Studio > Customisation > Basic Info. "
            "Use 5-10 niche-specific keywords for better search discovery."
        )

    if not branding.get("unsubscribedTrailer"):
        tips.append(
            "Add a channel trailer — it's shown to non-subscribers and "
            "significantly improves subscription rate."
        )

    return tips


# ── TikTok account audit ──────────────────────────────────────────────────────

def audit_tiktok_account(
    username: str,
    session_cookie: str = "",
) -> dict:
    """Fetch and audit a TikTok account's public stats.

    Args:
        username: TikTok username (without @).
        session_cookie: TikTok sessionid cookie (optional).

    Returns:
        Dict with account stats and optimization tips.
    """
    cookies: dict = {}
    if session_cookie:
        cookies["sessionid"] = session_cookie

    username = username.lstrip("@")

    try:
        resp = requests.get(
            f"https://www.tiktok.com/@{username}",
            headers=TIKTOK_HEADERS,
            cookies=cookies,
            timeout=20,
        )
        resp.raise_for_status()
        html = resp.text
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to fetch TikTok profile: {exc}") from exc

    # Extract __UNIVERSAL_DATA__ JSON
    match = re.search(
        r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.+?)</script>',
        html,
        re.DOTALL,
    )
    if not match:
        raise RuntimeError(
            f"Could not parse TikTok profile page for @{username}. "
            "The page structure may have changed."
        )

    page_data = json.loads(match.group(1))
    user_info = (
        page_data
        .get("__DEFAULT_SCOPE__", {})
        .get("webapp.user-detail", {})
        .get("userInfo", {})
    )

    user = user_info.get("user", {})
    stats = user_info.get("stats", {})

    followers = _safe_int(stats.get("followerCount", 0))
    following = _safe_int(stats.get("followingCount", 0))
    hearts = _safe_int(stats.get("heartCount", 0))
    video_count = _safe_int(stats.get("videoCount", 0))

    bio = user.get("signature", "")
    bio_score = _score_bio(bio, "tiktok")

    avg_hearts = hearts // max(video_count, 1)

    tips = _generate_tiktok_tips(
        bio=bio,
        followers=followers,
        following=following,
        hearts=hearts,
        video_count=video_count,
        avg_hearts=avg_hearts,
        verified=user.get("verified", False),
    )

    return {
        "platform": "tiktok",
        "username": f"@{username}",
        "display_name": user.get("nickname", ""),
        "bio": bio,
        "followers": followers,
        "following": following,
        "total_hearts": hearts,
        "video_count": video_count,
        "avg_hearts_per_video": avg_hearts,
        "verified": user.get("verified", False),
        "private": user.get("privateAccount", False),
        "bio_score": bio_score,
        "audit_at": _now_iso(),
        "tips": tips,
    }


def _generate_tiktok_tips(
    bio: str,
    followers: int,
    following: int,
    hearts: int,
    video_count: int,
    avg_hearts: int,
    verified: bool,
) -> list[str]:
    tips = []

    if not bio or len(bio) < 20:
        tips.append(
            "Bio is too short. Use all 80 characters. Include: "
            "niche descriptor | what viewers get | link-in-bio CTA."
        )
    elif "link" not in bio.lower() and "bio" not in bio.lower():
        tips.append(
            "Add 'link in bio' to your bio. It drives traffic to "
            "your Linktree/website and is expected by followers."
        )

    if video_count < 30:
        tips.append(
            "Post daily for the first 30 days — this is TikTok's "
            "golden window. Quantity beats quality at this stage."
        )

    if followers > 1000 and avg_hearts < followers * 0.05:
        tips.append(
            "Low heart rate vs followers. Use trending audio on every "
            "video and hook viewers in the first 0.5 seconds."
        )

    if following > followers * 2:
        tips.append(
            "Follow/follower ratio looks follow-heavy. Unfollow "
            "inactive accounts to improve credibility signals."
        )

    if video_count > 50 and avg_hearts < 100:
        tips.append(
            "Consider a niche reset. Go deep into one content vertical "
            "instead of posting mixed content — the algorithm rewards "
            "accounts with a clear niche."
        )

    tips.append(
        "Post between 6-9 AM, 12-3 PM, or 7-11 PM in your audience's "
        "timezone. These windows have the highest TikTok active user density."
    )

    return tips


# ── Bio optimiser ─────────────────────────────────────────────────────────────

def optimize_bio(
    platform: str,
    niche: str,
    goal: str = "followers",
    current_bio: str = "",
    cta_url: str = "",
) -> dict:
    """Generate an optimised bio for a given platform and niche.

    Args:
        platform: 'tiktok', 'youtube', or 'instagram'.
        niche: Content niche (e.g. 'fitness', 'finance', 'gaming').
        goal: Primary account goal ('followers', 'sales', 'traffic', 'brand').
        current_bio: Existing bio to score and compare.
        cta_url: URL to include in CTA (e.g. Linktree).

    Returns:
        Dict with bio templates, score comparison, and tips.
    """
    benchmarks = PLATFORM_BENCHMARKS.get(platform, {})
    max_chars = benchmarks.get("bio_max_chars", 150)
    keywords = NICHE_KEYWORDS.get(niche.lower(), [])

    # CTA by goal
    cta_map = {
        "followers": f"Follow for daily {niche} content",
        "sales":     f"Shop my {niche} picks 👇" if cta_url else f"DM for collab",
        "traffic":   f"Free guide 👇" if cta_url else f"Link in bio 👇",
        "brand":     f"Collabs & promos 📩 DM",
    }
    cta = cta_map.get(goal, cta_map["followers"])
    if cta_url:
        cta = f"{cta}\n{cta_url}"

    # Platform-specific templates
    templates = _bio_templates(platform, niche, cta, keywords, max_chars)

    result = {
        "platform": platform,
        "niche": niche,
        "goal": goal,
        "max_chars": max_chars,
        "templates": templates,
        "tips": _bio_tips(platform, niche),
    }

    if current_bio:
        before = _score_bio(current_bio, platform)
        after = _score_bio(templates[0], platform)
        result["current_bio"] = current_bio
        result["current_score"] = before
        result["optimised_score"] = after
        result["improvement"] = after["overall"] - before["overall"]

    return result


def _bio_templates(
    platform: str,
    niche: str,
    cta: str,
    keywords: list[str],
    max_chars: int,
) -> list[str]:
    niche_cap = niche.capitalize()
    kw = keywords[:3]
    kw_str = " | ".join(kw) if kw else niche

    if platform == "tiktok":
        return [
            f"{niche_cap} tips daily 🔥 | {kw_str}\n{cta}"[:max_chars],
            f"Your {niche_cap} guide 💪 | {kw_str}\n{cta}"[:max_chars],
            f"I post {niche} content so you don't have to search 🙌\n{cta}"[:max_chars],
        ]
    elif platform == "youtube":
        return [
            (
                f"Welcome to {niche_cap} Central! 🎯\n"
                f"I upload {niche} {kw_str} every week.\n"
                f"Hit subscribe to never miss a video.\n{cta}"
            )[:max_chars],
            (
                f"Your #1 source for {niche} content.\n"
                f"New videos every week covering {kw_str}.\n"
                f"Subscribe & turn on notifications 🔔\n{cta}"
            )[:max_chars],
        ]
    elif platform == "instagram":
        return [
            f"✨ {niche_cap} creator\n📍 {kw_str}\n📲 {cta}"[:max_chars],
            f"🔥 {niche_cap} | {kw_str}\n👇 {cta}"[:max_chars],
            f"{niche_cap} tips & inspo 💡\n{kw_str}\n{cta}"[:max_chars],
        ]
    return [f"{niche_cap} content | {cta}"[:max_chars]]


def _bio_tips(platform: str, niche: str) -> list[str]:
    common = [
        "Use your niche + value prop in the first 5 words — that's all most people read.",
        "Include exactly ONE call-to-action. Multiple CTAs reduce conversions.",
        "Update your bio every time you launch a new offer, challenge, or collab.",
    ]
    platform_tips = {
        "tiktok": [
            "TikTok bios are limited to 80 chars — every word must earn its place.",
            "Include 1-2 emojis to increase tap-through rate by ~18%.",
            "Add your posting schedule (e.g. 'Daily tips') to set expectations.",
        ],
        "youtube": [
            "The first 100 characters appear in Google search results — front-load keywords.",
            "Add your upload schedule (e.g. 'New video every Tuesday').",
            "Include social links and a content playlist in the featured section.",
        ],
        "instagram": [
            "Instagram bios are indexed by keywords — include your niche + city if local.",
            "Line breaks make bios more readable on mobile.",
            "Use the 'Name' field for an SEO keyword, not just your real name.",
        ],
    }
    return common + platform_tips.get(platform, [])


# ── Hashtag strategy ──────────────────────────────────────────────────────────

def get_hashtag_strategy(
    platform: str,
    niche: str,
    account_size: str = "small",
) -> dict:
    """Generate a hashtag strategy based on platform, niche, and account size.

    Args:
        platform: 'tiktok', 'youtube', or 'instagram'.
        niche: Content niche.
        account_size: 'small' (<10K), 'medium' (10K-100K), 'large' (100K+).

    Returns:
        Dict with tiered hashtag recommendations and usage guidelines.
    """
    benchmarks = PLATFORM_BENCHMARKS.get(platform, {})
    niche_kw = NICHE_KEYWORDS.get(niche.lower(), [niche])

    # Tiered hashtag strategy (small/medium/large views respectively)
    if platform == "tiktok":
        tier_sizes = {
            "small":  {"niche": 2, "medium": 2, "broad": 1},
            "medium": {"niche": 2, "medium": 2, "broad": 1},
            "large":  {"niche": 1, "medium": 2, "broad": 2},
        }
        niche_tags = [f"#{kw.replace(' ', '')}" for kw in niche_kw[:4]]
        medium_tags = [f"#{niche}tips", f"#{niche}101", f"#{niche}hack"]
        broad_tags = ["#fyp", "#foryoupage", "#viral", "#trending"]
    elif platform == "instagram":
        tier_sizes = {
            "small":  {"niche": 10, "medium": 12, "broad": 8},
            "medium": {"niche": 8, "medium": 12, "broad": 10},
            "large":  {"niche": 5, "medium": 10, "broad": 15},
        }
        niche_tags = [f"#{kw.replace(' ', '')}" for kw in niche_kw]
        medium_tags = [f"#{niche}community", f"#{niche}daily", f"#{niche}goals"]
        broad_tags = ["#explorepage", "#reels", "#viral", "#trending", "#instagood"]
    else:  # youtube
        tier_sizes = {
            "small":  {"niche": 5, "medium": 5, "broad": 5},
            "medium": {"niche": 4, "medium": 6, "broad": 5},
            "large":  {"niche": 3, "medium": 5, "broad": 7},
        }
        niche_tags = [f"#{kw.replace(' ', '')}" for kw in niche_kw[:5]]
        medium_tags = [f"#{niche}tutorial", f"#{niche}tips", f"#{niche}2024"]
        broad_tags = ["#shorts", "#youtube", "#viral", "#howto"]

    size_config = tier_sizes.get(account_size, tier_sizes["small"])

    return {
        "platform": platform,
        "niche": niche,
        "account_size": account_size,
        "recommended_total": sum(size_config.values()),
        "tiers": {
            "niche_specific": {
                "tags": niche_tags[:size_config["niche"]],
                "rationale": "High relevance, lower competition — your best chance to appear",
                "count": size_config["niche"],
            },
            "medium_competition": {
                "tags": medium_tags[:size_config["medium"]],
                "rationale": "Balanced reach and discoverability",
                "count": size_config["medium"],
            },
            "broad_reach": {
                "tags": broad_tags[:size_config["broad"]],
                "rationale": "High volume — algorithm signals but low organic click-through",
                "count": size_config["broad"],
            },
        },
        "usage_notes": [
            f"Use {sum(size_config.values())} hashtags per post on {platform}.",
            "Rotate hashtag sets every 3-5 posts to avoid shadowban flags.",
            "Never use banned/flagged hashtags — check with TikTok's Creator Portal.",
            "Niche hashtags drive the most qualified followers.",
        ],
    }


# ── Posting time optimiser ────────────────────────────────────────────────────

# Data sourced from platform analytics studies (2024-2025 aggregates).
_POSTING_TIMES: dict[str, dict[str, list[str]]] = {
    "tiktok": {
        "US": ["6:00 AM", "10:00 AM", "7:00 PM", "9:00 PM"],
        "UK": ["7:00 AM", "11:00 AM", "7:00 PM", "10:00 PM"],
        "AU": ["6:00 AM", "9:00 AM", "7:00 PM", "9:00 PM"],
        "global": ["6:00 AM", "12:00 PM", "7:00 PM", "10:00 PM"],
    },
    "youtube": {
        "US": ["9:00 AM", "12:00 PM", "3:00 PM", "5:00 PM"],
        "UK": ["2:00 PM", "4:00 PM", "7:00 PM", "9:00 PM"],
        "AU": ["8:00 AM", "12:00 PM", "5:00 PM", "8:00 PM"],
        "global": ["12:00 PM", "3:00 PM", "5:00 PM", "8:00 PM"],
    },
    "instagram": {
        "US": ["6:00 AM", "12:00 PM", "3:00 PM", "7:00 PM"],
        "UK": ["6:00 AM", "12:00 PM", "5:00 PM", "8:00 PM"],
        "AU": ["6:00 AM", "11:00 AM", "4:00 PM", "9:00 PM"],
        "global": ["6:00 AM", "12:00 PM", "5:00 PM", "9:00 PM"],
    },
}

_BEST_DAYS: dict[str, list[str]] = {
    "tiktok":    ["Tuesday", "Thursday", "Friday", "Saturday"],
    "youtube":   ["Thursday", "Friday", "Saturday", "Sunday"],
    "instagram": ["Monday", "Wednesday", "Thursday", "Friday"],
}


def get_optimal_posting_times(
    platform: str,
    region: str = "US",
    niche: str = "",
) -> dict:
    """Return optimal posting times for a platform and region.

    Args:
        platform: 'tiktok', 'youtube', or 'instagram'.
        region: Audience region code ('US', 'UK', 'AU', 'global').
        niche: Content niche (used for niche-specific adjustments).

    Returns:
        Dict with best times, best days, and scheduling advice.
    """
    platform_times = _POSTING_TIMES.get(platform, _POSTING_TIMES.get("tiktok", {}))
    region_times = platform_times.get(region, platform_times.get("global", []))
    best_days = _BEST_DAYS.get(platform, [])

    # Niche-specific adjustments
    niche_notes = []
    if niche in ("finance", "tech", "motivation"):
        niche_notes.append(
            f"{niche.capitalize()} content peaks on weekday mornings (6-9 AM) "
            "when audiences are commuting or starting their day."
        )
    elif niche in ("food", "travel", "lifestyle"):
        niche_notes.append(
            f"{niche.capitalize()} content peaks on weekends and evenings "
            "when people are relaxed and in discovery mode."
        )
    elif niche in ("gaming", "entertainment"):
        niche_notes.append(
            f"{niche.capitalize()} content peaks on evenings and weekends "
            "(7-11 PM weekdays, all day weekends)."
        )

    return {
        "platform": platform,
        "region": region,
        "niche": niche,
        "best_times": region_times,
        "best_days": best_days,
        "frequency": PLATFORM_BENCHMARKS.get(platform, {}).get(
            "daily_post_target", (1, 2)
        ),
        "niche_notes": niche_notes,
        "scheduling_tips": [
            "Use a scheduler (Buffer, Later, TikTok's own scheduler) — "
            "consistent timing trains the algorithm.",
            "Post within the optimal window, not outside it — late beats never.",
            "Monitor your own analytics after 30 posts to find YOUR peak hours.",
            "Respond to comments within the first 30 minutes post-publish — "
            "early engagement signals boost distribution.",
        ],
    }
