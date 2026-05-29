"""Account profile management and optimization engine."""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from cli_anything.social_trends.core.store import Store

# ── Platform best-practice data ───────────────────────────────────────────────

_PLATFORM_BEST_TIMES: Dict[str, Dict[str, List[str]]] = {
    "tiktok": {
        "monday":    ["6:00 AM", "10:00 AM", "7:00 PM"],
        "tuesday":   ["9:00 AM", "12:00 PM", "8:00 PM"],
        "wednesday": ["7:00 AM", "11:00 AM", "9:00 PM"],
        "thursday":  ["7:00 AM", "12:00 PM", "7:00 PM"],
        "friday":    ["5:00 AM", "1:00 PM",  "6:00 PM"],
        "saturday":  ["11:00 AM", "7:00 PM", "8:00 PM"],
        "sunday":    ["7:00 AM", "8:00 AM",  "4:00 PM"],
    },
    "youtube": {
        "monday":    ["2:00 PM", "4:00 PM"],
        "tuesday":   ["2:00 PM", "4:00 PM"],
        "wednesday": ["2:00 PM", "4:00 PM"],
        "thursday":  ["12:00 PM", "3:00 PM"],
        "friday":    ["12:00 PM", "3:00 PM"],
        "saturday":  ["9:00 AM", "11:00 AM"],
        "sunday":    ["9:00 AM", "11:00 AM"],
    },
    "instagram": {
        "monday":    ["6:00 AM", "10:00 AM", "7:00 PM"],
        "tuesday":   ["8:00 AM", "2:00 PM"],
        "wednesday": ["9:00 AM", "3:00 PM", "6:00 PM"],
        "thursday":  ["7:00 AM", "11:00 AM", "7:00 PM"],
        "friday":    ["5:00 AM", "1:00 PM",  "3:00 PM"],
        "saturday":  ["11:00 AM", "2:00 PM"],
        "sunday":    ["10:00 AM", "12:00 PM"],
    },
}

_POSTING_FREQUENCY: Dict[str, Dict[str, str]] = {
    "tiktok":    {"min": "1x/day", "optimal": "3-5x/day", "max": "7x/day"},
    "youtube":   {"min": "1x/week", "optimal": "3x/week", "max": "1x/day"},
    "instagram": {"min": "3x/week", "optimal": "1x/day (feed) + 5-7x Stories", "max": "3x/day"},
}

_CONTENT_PILLARS: Dict[str, List[str]] = {
    "fitness":       ["Workout tutorials", "Transformation stories", "Nutrition tips", "Mindset & motivation", "Equipment reviews"],
    "finance":       ["Money tips", "Investment breakdowns", "Budget walkthroughs", "Success stories", "Financial news"],
    "luxury":        ["Lifestyle tours", "Product reviews", "Travel vlogs", "Behind-the-scenes", "Aspirational content"],
    "travel":        ["Destination guides", "Budget vs luxury", "Travel tips", "Hidden gems", "Day-in-life vlogs"],
    "food":          ["Recipes", "Restaurant reviews", "Meal prep", "Taste tests", "Cooking hacks"],
    "gaming":        ["Gameplay highlights", "Reviews", "Tutorials", "Setup tours", "Reaction videos"],
    "crypto":        ["Price analysis", "Project spotlights", "News breakdowns", "Portfolio tips", "Beginner guides"],
    "fashion":       ["Outfit ideas", "Hauls", "Style tips", "Brand spotlights", "Seasonal lookbooks"],
    "motivational":  ["Daily quotes", "Success stories", "Self-improvement tips", "Book summaries", "Morning routines"],
    "sports":        ["Highlight clips", "Training tips", "Match analysis", "Athlete stories", "Fan reactions"],
}

_BIO_TEMPLATES: Dict[str, str] = {
    "fitness":      "💪 {username} | Helping you build your dream body\n🔥 {follower_goal}k strong\n👇 Free workout plan below",
    "finance":      "💰 {username} | Financial freedom educator\n📈 Sharing what's actually working\n👇 Free money guide below",
    "luxury":       "✨ {username} | Luxury lifestyle curator\n🌍 Inspiring your best life\n👇 Collab inquiries below",
    "travel":       "✈️ {username} | World explorer\n🗺️ {countries}+ countries & counting\n👇 Travel guide below",
    "food":         "🍴 {username} | Food lover & recipe creator\n👨‍🍳 Sharing recipes that slap\n👇 Free cookbook below",
    "gaming":       "🎮 {username} | Gamer & content creator\n🏆 {platform} streamer\n👇 Join the Discord",
    "crypto":       "₿ {username} | Crypto analyst\n📊 Daily market insights\n👇 Free crypto guide below",
    "fashion":      "👗 {username} | Style curator\n🛍️ Fashion for everyone\n👇 Shop my looks below",
    "motivational": "🧠 {username} | Mindset coach\n🚀 Helping you reach your potential\n👇 Free mindset guide below",
    "sports":       "⚽ {username} | Sports content creator\n🏆 Daily highlights & analysis\n👇 Follow for daily posts",
}


def _score_account(account: Dict[str, Any]) -> int:
    """Score an account's optimization level 0-100."""
    score = 0
    if account.get("bio"):           score += 15
    if account.get("profile_pic"):   score += 10
    if account.get("link_in_bio"):   score += 15
    if account.get("niche"):         score += 10
    if account.get("content_pillars"): score += 15
    if account.get("posting_schedule"): score += 15
    if account.get("hashtag_strategy"): score += 10
    if account.get("pinned_post"):   score += 10
    return score


def add_account(
    store: Store,
    platform: str,
    username: str,
    niche: str,
) -> Dict[str, Any]:
    account_id = f"acc_{uuid.uuid4().hex[:8]}"
    account: Dict[str, Any] = {
        "id": account_id,
        "platform": platform.lower(),
        "username": username,
        "niche": niche.lower(),
        "bio": None,
        "profile_pic": None,
        "link_in_bio": None,
        "content_pillars": None,
        "posting_schedule": None,
        "hashtag_strategy": None,
        "pinned_post": None,
        "created_at": datetime.now().isoformat(),
        "optimization_score": 0,
    }
    account["optimization_score"] = _score_account(account)
    store.add_account(account)
    store.save()
    return account


def list_accounts(store: Store) -> List[Dict[str, Any]]:
    return store.accounts


def optimize_account(store: Store, account_id: str) -> Dict[str, Any]:
    account = store.get_account(account_id)
    niche = account.get("niche", "motivational")
    platform = account.get("platform", "tiktok")
    username = account.get("username", "your_account")

    # Build optimization report
    bio_template = _BIO_TEMPLATES.get(niche, _BIO_TEMPLATES["motivational"])
    suggested_bio = bio_template.format(
        username=username,
        follower_goal="10",
        countries="20",
        platform=platform.capitalize(),
    )

    pillars = _CONTENT_PILLARS.get(niche, _CONTENT_PILLARS["motivational"])
    best_times = _PLATFORM_BEST_TIMES.get(platform, _PLATFORM_BEST_TIMES["tiktok"])
    frequency = _POSTING_FREQUENCY.get(platform, _POSTING_FREQUENCY["tiktok"])

    report: Dict[str, Any] = {
        "account_id": account_id,
        "platform": platform,
        "username": username,
        "niche": niche,
        "suggested_bio": suggested_bio,
        "content_pillars": pillars,
        "best_posting_times": best_times,
        "posting_frequency": frequency,
        "hashtag_strategy": {
            "total_per_post": 20 if platform == "tiktok" else 10,
            "mix": "30% high-competition / 40% medium / 30% low",
            "rotation": "Change hashtag sets every 14 days",
            "placement": "First comment (TikTok) or caption (Instagram)",
        },
        "profile_checklist": [
            "✓ Profile picture: high-quality, recognizable face or brand logo",
            "✓ Username: short, memorable, niche-relevant",
            "✓ Bio: clear value prop + call-to-action + link",
            "✓ Link in bio: Linktree or landing page with lead magnet",
            "✓ Pinned post: your best-performing or most representative video",
            "✓ Highlights (Instagram): save evergreen story content",
        ],
        "growth_actions": [
            "Post consistently using optimal schedule above",
            "Engage with comments within first 30 mins of posting",
            "Collaborate with 3-5 accounts of similar size in your niche",
            "Use trending audio within 48 hours of it peaking",
            "Repurpose top content across platforms (TikTok → Reels → Shorts)",
            "Run polls and Q&As to boost engagement rate",
            "Cross-promote: mention your other platforms in bio",
        ],
        "monetization_timeline": {
            "0-1k followers":   "Build content library, test formats, grow organically",
            "1k-10k followers": "Start affiliate marketing, brand gifting, UGC deals",
            "10k-50k followers":"Brand sponsorships ($100-$500/post), digital products",
            "50k-100k followers":"Premium sponsorships ($500-$2000/post), courses, memberships",
            "100k+ followers":  "Agency deals, $2000+ sponsorships, product lines",
        },
    }

    # Persist the optimization to the account
    store.update_account(account_id, {
        "bio": suggested_bio,
        "content_pillars": pillars,
        "posting_schedule": best_times,
        "hashtag_strategy": report["hashtag_strategy"],
        "optimization_score": 85,
        "last_optimized": datetime.now().isoformat(),
    })
    store.save()
    return report


def score_account(store: Store, account_id: str) -> Dict[str, Any]:
    account = store.get_account(account_id)
    score = _score_account(account)
    account["optimization_score"] = score

    breakdown = {
        "bio":              15 if account.get("bio") else 0,
        "profile_pic":      10 if account.get("profile_pic") else 0,
        "link_in_bio":      15 if account.get("link_in_bio") else 0,
        "niche_defined":    10 if account.get("niche") else 0,
        "content_pillars":  15 if account.get("content_pillars") else 0,
        "posting_schedule": 15 if account.get("posting_schedule") else 0,
        "hashtag_strategy": 10 if account.get("hashtag_strategy") else 0,
        "pinned_post":      10 if account.get("pinned_post") else 0,
    }
    grade = "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 50 else "D"
    suggestion = (
        "Excellent optimization! Focus on consistency."
        if score >= 85 else
        "Good foundation. Fill in missing profile elements."
        if score >= 70 else
        "Needs work. Run `accounts optimize` to get a full plan."
    )
    store.save()
    return {
        "account_id": account_id,
        "score": score,
        "grade": grade,
        "breakdown": breakdown,
        "suggestion": suggestion,
    }


def export_accounts(store: Store, path: str) -> Dict[str, Any]:
    data = {"accounts": store.accounts, "exported_at": datetime.now().isoformat()}
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    return {"success": True, "path": path, "count": len(store.accounts)}
