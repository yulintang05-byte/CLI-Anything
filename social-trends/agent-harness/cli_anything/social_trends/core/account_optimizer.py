"""Account optimization engine for YouTube and TikTok.

Generates data-driven recommendations for bio, hashtag strategy,
posting schedule, content mix, and growth tactics.
"""

from __future__ import annotations

import os
from typing import Optional
import requests


# ── Posting schedule database (based on aggregated public research) ───────────

_POSTING_SCHEDULES: dict[str, dict] = {
    "tiktok": {
        "best_days": ["Tuesday", "Thursday", "Friday"],
        "best_times_utc": ["06:00", "10:00", "19:00", "22:00"],
        "frequency": "1-4 posts/day for growth phase, 1/day for maintenance",
        "notes": "Post consistently; TikTok rewards daily activity with distribution boosts.",
    },
    "youtube": {
        "best_days": ["Thursday", "Friday", "Saturday"],
        "best_times_utc": ["14:00", "17:00", "20:00"],
        "frequency": "2-3 videos/week for growth, 1/week minimum for maintenance",
        "notes": "Publish 2-3 hours before peak viewership window in your target timezone.",
    },
    "instagram": {
        "best_days": ["Monday", "Tuesday", "Wednesday", "Friday"],
        "best_times_utc": ["09:00", "12:00", "17:00"],
        "frequency": "1 Reel/day + 3-5 Stories/day for growth",
        "notes": "Reels get 3× more reach than static posts. Carousel posts have highest saves.",
    },
}

_NICHE_HASHTAG_COUNTS: dict[str, int] = {
    "tiktok": 3,   # TikTok: 3-5 targeted hashtags outperform keyword-stuffing
    "youtube": 5,  # YouTube: 5-8 in description (not title)
    "instagram": 10,  # IG: mix of small (10k-100k), medium (100k-1M), large (1M+)
}

_CONTENT_MIX: dict[str, list[dict]] = {
    "tiktok": [
        {"type": "Trending sound duet/stitch", "share": 30, "purpose": "rides algorithm boost"},
        {"type": "Educational/value content", "share": 30, "purpose": "saves + shares = reach"},
        {"type": "Behind-the-scenes/POV", "share": 20, "purpose": "authenticity & retention"},
        {"type": "Trending challenge", "share": 10, "purpose": "discoverability"},
        {"type": "Repurposed YouTube/long-form", "share": 10, "purpose": "content efficiency"},
    ],
    "youtube": [
        {"type": "SEO-optimized tutorials", "share": 40, "purpose": "search-driven long-tail traffic"},
        {"type": "Trending topic response", "share": 25, "purpose": "timeliness boost"},
        {"type": "List/compilation", "share": 20, "purpose": "watch time & session duration"},
        {"type": "Community/Q&A", "share": 15, "purpose": "audience retention and loyalty"},
    ],
}

_GROWTH_PHASES: list[dict] = [
    {
        "phase": "0–1K followers",
        "strategy": "Post daily. Focus on trending sounds and hashtags. Hook in first 1 second.",
        "key_metric": "Profile visits → followers conversion",
        "content_tip": "Keep videos under 15s. Use text overlays for silent viewers.",
    },
    {
        "phase": "1K–10K followers",
        "strategy": "Niche down. Consistent posting 1-2x/day. Engage all comments within 1hr.",
        "key_metric": "Watch completion rate (aim >60%)",
        "content_tip": "Start series content. Tease next video to drive profile visits.",
    },
    {
        "phase": "10K–100K followers",
        "strategy": "Collaborate with creators in niche. Cross-post to YouTube Shorts/IG Reels.",
        "key_metric": "Share rate (viral coefficient)",
        "content_tip": "Add CTA to follow at the 80% watch mark, not the beginning.",
    },
    {
        "phase": "100K+ followers",
        "strategy": "Monetize via brand deals, affiliate links, digital products. Diversify platforms.",
        "key_metric": "Revenue per 1000 views (RPM)",
        "content_tip": "Pin a converting video to profile. Update bio with monetization link.",
    },
]


# ── Public API ────────────────────────────────────────────────────────────────

def audit_account(platform: str, username: str) -> dict:
    """
    Audit a public account and return optimization recommendations.

    For YouTube: uses YouTube Data API if YOUTUBE_API_KEY is set.
    For TikTok: uses web scraping.
    """
    platform = platform.lower()
    if platform == "youtube":
        return _audit_youtube_channel(username)
    elif platform == "tiktok":
        return _audit_tiktok_account(username)
    else:
        raise ValueError(f"Unsupported platform: {platform}. Use 'youtube' or 'tiktok'.")


def get_posting_schedule(platform: str, niche: Optional[str] = None) -> dict:
    """Return the optimal posting schedule for a platform."""
    schedule = _POSTING_SCHEDULES.get(platform.lower(), _POSTING_SCHEDULES["tiktok"])
    result = {"platform": platform, **schedule}
    if niche:
        result["niche_tip"] = _get_niche_posting_tip(niche, platform)
    return result


def get_content_mix(platform: str) -> list[dict]:
    """Return the recommended content type mix for a platform."""
    return _CONTENT_MIX.get(platform.lower(), _CONTENT_MIX["tiktok"])


def get_growth_roadmap(current_followers: int) -> dict:
    """Return the growth phase strategy for current follower count."""
    for phase in _GROWTH_PHASES:
        label = phase["phase"]
        lower, upper = _parse_follower_range(label)
        if lower <= current_followers < upper:
            return phase
    return _GROWTH_PHASES[-1]  # 100K+


def generate_optimization_report(platform: str, username: str, niche: Optional[str] = None) -> dict:
    """Generate a comprehensive optimization report for an account."""
    audit = audit_account(platform, username)
    followers = audit.get("followers", 0)
    roadmap = get_growth_roadmap(followers)
    schedule = get_posting_schedule(platform, niche)
    mix = get_content_mix(platform)
    hashtag_count = _NICHE_HASHTAG_COUNTS.get(platform.lower(), 5)

    issues = _identify_issues(audit)
    quick_wins = _generate_quick_wins(audit, platform, niche)

    return {
        "account": {"platform": platform, "username": username, **audit},
        "growth_phase": roadmap,
        "posting_schedule": schedule,
        "content_mix": mix,
        "hashtag_strategy": {
            "recommended_count": hashtag_count,
            "tip": _hashtag_strategy_tip(platform, niche),
        },
        "issues_found": issues,
        "quick_wins": quick_wins,
        "monetization_readiness": _monetization_readiness(audit, platform),
    }


def get_bio_template(platform: str, niche: str, cta: str = "Follow for daily tips") -> dict:
    """Return a high-converting bio template for a platform and niche."""
    templates = {
        "tiktok": (
            f"🎯 {niche.title()} tips & trends\n"
            f"📲 {cta}\n"
            "🔗 Link in bio → [your link]"
        ),
        "youtube": (
            f"Welcome! I post {niche} content every week.\n"
            f"{cta} for more.\n"
            "👇 Free resource: [link]"
        ),
        "instagram": (
            f"✨ {niche.title()} creator\n"
            f"📩 Collabs: [email]\n"
            f"👇 {cta}"
        ),
    }
    return {
        "platform": platform,
        "niche": niche,
        "bio": templates.get(platform.lower(), templates["tiktok"]),
        "character_limits": {"tiktok": 80, "youtube": 1000, "instagram": 150},
        "tips": [
            "Lead with your value proposition (who you help + how)",
            "Include one clear CTA",
            "Add a link-in-bio tool (Linktree, Beacons, Stan Store)",
            "Use emojis to break up text visually",
        ],
    }


# ── Platform-specific auditors ────────────────────────────────────────────────

def _audit_youtube_channel(username: str) -> dict:
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        return _youtube_audit_stub(username)

    try:
        # Search for channel
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "key": api_key,
                "q": username,
                "type": "channel",
                "part": "snippet",
                "maxResults": 1,
            },
            timeout=15,
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])
        if not items:
            return {"error": f"Channel not found: {username}"}

        channel_id = items[0]["id"]["channelId"]
        snippet = items[0]["snippet"]

        # Get channel statistics
        stats_resp = requests.get(
            "https://www.googleapis.com/youtube/v3/channels",
            params={
                "key": api_key,
                "id": channel_id,
                "part": "statistics,brandingSettings,contentDetails",
            },
            timeout=15,
        )
        stats_resp.raise_for_status()
        channel_data = stats_resp.json().get("items", [{}])[0]
        stats = channel_data.get("statistics", {})

        followers = int(stats.get("subscriberCount", 0))
        video_count = int(stats.get("videoCount", 0))
        total_views = int(stats.get("viewCount", 0))
        avg_views = total_views // max(video_count, 1)

        return {
            "username": username,
            "channel_id": channel_id,
            "display_name": snippet.get("channelTitle", username),
            "description": snippet.get("description", "")[:300],
            "followers": followers,
            "video_count": video_count,
            "total_views": total_views,
            "avg_views_per_video": avg_views,
            "views_per_subscriber": round(total_views / max(followers, 1), 2),
            "channel_url": f"https://youtube.com/channel/{channel_id}",
        }
    except Exception as e:
        return {"error": str(e), "username": username}


def _audit_tiktok_account(username: str) -> dict:
    clean = username.lstrip("@")
    try:
        resp = requests.get(
            f"https://www.tiktok.com/@{clean}",
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            },
            timeout=20,
        )
        resp.raise_for_status()
        from bs4 import BeautifulSoup
        import json

        soup = BeautifulSoup(resp.text, "lxml")
        script = soup.find("script", {"id": "__NEXT_DATA__"})
        if script:
            data = json.loads(script.string)
            user_info = (
                data.get("props", {})
                .get("pageProps", {})
                .get("userInfo", {})
            )
            user = user_info.get("user", {})
            stats = user_info.get("stats", {})
            return {
                "username": clean,
                "display_name": user.get("nickname", clean),
                "bio": user.get("signature", ""),
                "followers": stats.get("followerCount", 0),
                "following": stats.get("followingCount", 0),
                "likes": stats.get("heartCount", 0),
                "video_count": stats.get("videoCount", 0),
                "avg_likes_per_video": stats.get("heartCount", 0) // max(stats.get("videoCount", 1), 1),
                "verified": user.get("verified", False),
                "profile_url": f"https://www.tiktok.com/@{clean}",
            }
    except Exception:
        pass
    return _tiktok_audit_stub(username)


def _youtube_audit_stub(username: str) -> dict:
    return {
        "username": username,
        "note": "Set YOUTUBE_API_KEY for live data. Showing template audit.",
        "followers": 0,
        "video_count": 0,
        "total_views": 0,
        "avg_views_per_video": 0,
    }


def _tiktok_audit_stub(username: str) -> dict:
    return {
        "username": username,
        "note": "Could not fetch live data (TikTok scraping may be blocked). Showing template audit.",
        "followers": 0,
        "video_count": 0,
        "likes": 0,
    }


# ── Analysis helpers ──────────────────────────────────────────────────────────

def _identify_issues(audit: dict) -> list[str]:
    issues = []
    if not audit.get("bio", "").strip() and not audit.get("description", "").strip():
        issues.append("Empty bio — add a value proposition, niche, and CTA")
    followers = audit.get("followers", 0)
    video_count = audit.get("video_count", 0)
    if video_count < 10:
        issues.append("Low video count — publish at least 30 videos before analyzing performance")
    if followers > 0 and video_count > 0:
        avg_views = audit.get("avg_views_per_video", 0) or audit.get("avg_likes_per_video", 0)
        if avg_views < followers * 0.05:
            issues.append(
                "Low engagement rate — views/likes < 5% of followers. Audit posting times and hooks."
            )
    return issues if issues else ["No critical issues found — focus on growth tactics."]


def _generate_quick_wins(audit: dict, platform: str, niche: Optional[str]) -> list[str]:
    wins = [
        "Pin your best-performing video to the top of your profile",
        "Add a link-in-bio tool (Beacons, Stan Store, or Linktree) with one clear CTA",
        "Reply to every comment in the first 60 minutes after posting to boost reach",
        "Use 1 viral trending sound in your next 3 videos",
    ]
    if niche:
        wins.append(f"Search '{niche}' on TikTok/YouTube, analyze top 10 videos — steal their hook structure")
    if platform == "tiktok":
        wins.append("Post a 'Day in my life' video — POV content consistently outperforms on TikTok")
    elif platform == "youtube":
        wins.append("Add end screens and cards to your top 5 videos to increase session watch time")
    return wins


def _hashtag_strategy_tip(platform: str, niche: Optional[str]) -> str:
    tips = {
        "tiktok": (
            "Use 3-5 hashtags: 1 niche-specific (<500K views), 1 broad (#fyp is optional), "
            "1 trending. Avoid spamming #fyp #foryou — they add noise."
        ),
        "youtube": (
            "Add 5-8 hashtags in description (not title). First 3 appear above the title. "
            "Mix: 2 niche-specific, 2 mid-size, 1 branded."
        ),
        "instagram": (
            "Use 10-15 hashtags. Mix: 30% small (10K-100K), 50% medium (100K-1M), 20% large (1M+). "
            "Put them in first comment to keep caption clean."
        ),
    }
    return tips.get(platform.lower(), tips["tiktok"])


def _monetization_readiness(audit: dict, platform: str) -> dict:
    followers = audit.get("followers", 0)
    thresholds = {
        "tiktok": {"creator_fund": 10000, "live_gifts": 1000, "series": 10000},
        "youtube": {"partner_program": 1000, "channel_memberships": 500, "super_thanks": 500},
    }
    t = thresholds.get(platform.lower(), thresholds["tiktok"])
    return {
        "current_followers": followers,
        "milestones": [
            {
                "feature": k,
                "required": v,
                "unlocked": followers >= v,
                "remaining": max(0, v - followers),
            }
            for k, v in t.items()
        ],
    }


def _get_niche_posting_tip(niche: str, platform: str) -> str:
    niche_lower = niche.lower()
    if any(w in niche_lower for w in ["finance", "money", "invest", "crypto"]):
        return "Finance content performs best Monday morning — people plan budgets at week start."
    if any(w in niche_lower for w in ["fitness", "workout", "gym", "health"]):
        return "Post fitness content Sunday evening — people plan workout weeks ahead."
    if any(w in niche_lower for w in ["food", "recipe", "cook", "bake"]):
        return "Food content peaks Thursday–Sunday — weekend meal planning window."
    if any(w in niche_lower for w in ["fashion", "style", "outfit", "ootd"]):
        return "Fashion content peaks Friday afternoon — weekend outfit planning."
    if any(w in niche_lower for w in ["tech", "gaming", "software", "coding"]):
        return "Tech content peaks Tuesday/Wednesday — mid-week decision makers."
    return f"For {niche}: track your own analytics for 4+ weeks to find your audience's peak window."


def _parse_follower_range(label: str) -> tuple[int, int]:
    import re
    nums = re.findall(r"[\d,]+[KkMm]?", label)
    def parse_num(s: str) -> int:
        s = s.replace(",", "")
        if s.endswith(("K", "k")):
            return int(float(s[:-1]) * 1_000)
        if s.endswith(("M", "m")):
            return int(float(s[:-1]) * 1_000_000)
        return int(s)
    if len(nums) >= 2:
        return parse_num(nums[0]), parse_num(nums[1])
    if len(nums) == 1:
        return parse_num(nums[0]), 10_000_000
    return 0, 10_000_000
