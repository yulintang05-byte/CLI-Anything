"""Account optimization engine: analyze and improve social media profiles."""

import json
import re
from datetime import datetime
from typing import Optional


NICHE_KEYWORDS = {
    "fitness": ["gym", "workout", "fit", "health", "gains", "muscle", "cardio"],
    "finance": ["money", "invest", "crypto", "stocks", "wealth", "income", "passive"],
    "fashion": ["outfit", "style", "ootd", "fashion", "clothes", "aesthetic"],
    "food": ["recipe", "food", "eat", "cook", "meal", "foodie", "delicious"],
    "travel": ["travel", "trip", "adventure", "explore", "wanderlust", "vacation"],
    "beauty": ["makeup", "skincare", "beauty", "glow", "routine", "tutorial"],
    "gaming": ["gaming", "game", "gamer", "stream", "twitch", "console", "fps"],
    "motivation": ["motivation", "mindset", "grind", "success", "hustle", "inspire"],
    "tech": ["tech", "code", "programming", "software", "ai", "developer", "startup"],
    "luxury": ["luxury", "rich", "villa", "yacht", "ferrari", "mansion", "lifestyle"],
}

POSTING_SCHEDULE = {
    "tiktok": {
        "best_times": ["6-10 AM", "12-3 PM", "7-11 PM"],
        "best_days": ["Tuesday", "Thursday", "Friday", "Saturday"],
        "frequency": "1-3 posts/day",
        "max_hashtags": 5,
        "caption_length": "under 150 chars for hook, hashtags separate",
    },
    "youtube": {
        "best_times": ["2-4 PM", "8-11 PM"],
        "best_days": ["Thursday", "Friday", "Saturday", "Sunday"],
        "frequency": "2-3 videos/week for growth, 1/week for retention",
        "max_hashtags": 15,
        "description_tip": "First 3 lines matter most for SEO + CTR",
    },
    "instagram": {
        "best_times": ["9-11 AM", "3-5 PM"],
        "best_days": ["Monday", "Wednesday", "Thursday"],
        "frequency": "1 Reel/day + 3-5 Stories/day",
        "max_hashtags": 5,
        "reel_tip": "Hook in first 1-2 seconds, trending audio boosts reach 3x",
    },
}

BIO_TEMPLATES = {
    "fitness": "🏋️ {niche} | {value_prop} | {cta}\n📍 {location} | 💪 {transformation}",
    "finance": "💰 {niche} | Helping {audience} {outcome}\n📈 Free resources 👇",
    "fashion": "✨ {niche} aesthetic | {style_desc}\n🛍️ Shop my looks 👇",
    "motivation": "🔥 {niche} | {tagline}\n📲 Daily content for {audience}",
    "default": "🎯 {niche} | {value_prop}\n👇 {cta}",
}

VIRAL_HOOKS = [
    "POV: {scenario}",
    "Nobody is talking about this...",
    "I tried {X} for 30 days. Here's what happened:",
    "Stop scrolling. You need to hear this.",
    "The reason you're not {achieving X} (it's not what you think)",
    "How I went from {before} to {after}",
    "Things successful people do that nobody talks about:",
    "Rate my {topic} 1-10 in the comments",
    "This changed my life: {tip}",
    "Day {N} of {challenge} (watch till end)",
]

CONTENT_PILLARS = {
    "educational": "Teach something. 30% of content.",
    "entertaining": "Make them laugh/feel. 30% of content.",
    "inspirational": "Motivate/aspire. 20% of content.",
    "promotional": "Sell/promote. Max 20% — any more kills reach.",
    "trending": "Hop on trends with your niche twist. Use as needed.",
}


def detect_niche(bio: str, handle: str = "") -> dict:
    """Detect account niche from bio/handle text."""
    text = f"{bio} {handle}".lower()
    scores: dict[str, int] = {}
    for niche, keywords in NICHE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score:
            scores[niche] = score
    if not scores:
        return {"niche": "general", "confidence": "low", "keywords_matched": []}
    top = max(scores, key=scores.__getitem__)
    return {
        "niche": top,
        "confidence": "high" if scores[top] >= 3 else "medium",
        "keywords_matched": [kw for kw in NICHE_KEYWORDS[top] if kw in text],
        "secondary_niches": [n for n, s in sorted(scores.items(), key=lambda x: -x[1]) if n != top][:2],
    }


def analyze_bio(bio: str, platform: str = "tiktok") -> dict:
    """Score and improve a social media bio."""
    issues = []
    suggestions = []
    score = 100

    if len(bio) < 20:
        issues.append("Bio is too short — you're leaving reach on the table.")
        score -= 30
    if len(bio) > 150:
        issues.append("Bio too long — most users won't read past line 2.")
        score -= 10

    emoji_count = len(re.findall(r'[\U0001F300-\U0001FFFF]', bio))
    if emoji_count == 0:
        issues.append("No emojis — emojis increase bio engagement by ~25%.")
        suggestions.append("Add 2-3 relevant emojis to break up text.")
        score -= 15
    elif emoji_count > 8:
        issues.append("Too many emojis — looks spammy.")
        score -= 10

    has_cta = any(w in bio.lower() for w in ["link", "👇", "check", "follow", "dm", "shop", "click"])
    if not has_cta:
        issues.append("No call-to-action (CTA).")
        suggestions.append("Add a CTA: 'Follow for daily tips 👇' or 'Link in bio 👇'")
        score -= 20

    has_value = any(w in bio.lower() for w in ["help", "teach", "tips", "learn", "guide", "free"])
    if not has_value:
        suggestions.append("State your value prop: what does following you give the viewer?")
        score -= 10

    niche = detect_niche(bio)
    template = BIO_TEMPLATES.get(niche["niche"], BIO_TEMPLATES["default"])

    return {
        "platform": platform,
        "bio_score": max(0, score),
        "grade": "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 50 else "D",
        "niche_detected": niche,
        "issues": issues,
        "suggestions": suggestions,
        "bio_template": template,
        "viral_hooks": VIRAL_HOOKS[:3],
    }


def optimize_posting_schedule(platform: str, timezone: str = "EST") -> dict:
    """Return optimized posting schedule for given platform."""
    sched = POSTING_SCHEDULE.get(platform.lower(), {})
    if not sched:
        return {"error": f"Unknown platform: {platform}. Supported: {list(POSTING_SCHEDULE.keys())}"}
    return {
        "platform": platform,
        "timezone": timezone,
        "schedule": sched,
        "content_pillars": CONTENT_PILLARS,
        "pro_tips": [
            f"Post at the START of each best window for maximum early engagement.",
            "Batch-create content 1 week ahead so you never miss a post.",
            f"Respond to ALL comments in the first hour — algorithm rewards creator engagement.",
            "Pin your best-performing post to drive follows from new visitors.",
        ],
    }


def hashtag_strategy(niche: str, platform: str = "tiktok", trending_tags: list = None) -> dict:
    """Generate hashtag strategy for a niche."""
    niche_tags = {
        "fitness": ["#fitness", "#gym", "#workout", "#gains", "#fitlife", "#bodybuilding", "#cardio"],
        "finance": ["#finance", "#investing", "#money", "#wealth", "#crypto", "#stockmarket", "#passiveincome"],
        "fashion": ["#fashion", "#ootd", "#style", "#outfit", "#aesthetic", "#streetwear"],
        "food": ["#food", "#foodie", "#recipe", "#cooking", "#eats", "#homecook"],
        "travel": ["#travel", "#wanderlust", "#adventure", "#explore", "#travelblogger"],
        "beauty": ["#beauty", "#skincare", "#makeup", "#glowup", "#selfcare", "#beautytips"],
        "motivation": ["#motivation", "#mindset", "#success", "#hustle", "#grind", "#inspire"],
        "tech": ["#tech", "#coding", "#programming", "#ai", "#developer", "#startup"],
        "gaming": ["#gaming", "#gamer", "#videogames", "#stream", "#esports"],
        "luxury": ["#luxury", "#lifestyle", "#rich", "#motivation", "#success"],
    }

    mega_tags = ["#fyp", "#foryou", "#foryoupage", "#viral", "#trending"]
    mid_tags = niche_tags.get(niche.lower(), ["#content", "#creator", "#socialmedia"])
    small_tags = [f"#{niche}tips", f"#{niche}life", f"#{niche}motivation"]

    all_tags = (trending_tags or [])[:3] + mega_tags[:2] + mid_tags[:5] + small_tags[:2]
    platform_limit = 5 if platform == "tiktok" else 15 if platform == "youtube" else 10

    return {
        "platform": platform,
        "niche": niche,
        "strategy": {
            "mega_tags_100M+": mega_tags,
            "mid_tags_1M_10M": mid_tags,
            "niche_tags_under_1M": small_tags,
            "trending_tags": trending_tags or [],
        },
        "recommended_mix": all_tags[:platform_limit],
        "formula": f"2 mega + 3 mid + {platform_limit - 5} niche = max discoverability",
        "platform_limit": platform_limit,
    }


def full_account_audit(
    handle: str,
    bio: str,
    platform: str,
    niche: str = "",
    followers: int = 0,
    avg_views: int = 0,
    avg_likes: int = 0,
) -> dict:
    """Run a full account optimization audit."""
    bio_analysis = analyze_bio(bio, platform)
    niche_info = detect_niche(bio, handle) if not niche else {"niche": niche}
    detected_niche = niche or niche_info.get("niche", "general")
    schedule = optimize_posting_schedule(platform)
    hashtags = hashtag_strategy(detected_niche, platform)

    engagement_rate = (avg_likes / max(avg_views, 1)) * 100 if avg_views else None
    engagement_grade = (
        "Excellent" if engagement_rate and engagement_rate > 5
        else "Good" if engagement_rate and engagement_rate > 3
        else "Average" if engagement_rate and engagement_rate > 1
        else "Needs Work" if engagement_rate
        else "N/A"
    )

    priority_actions = []
    if bio_analysis["bio_score"] < 70:
        priority_actions.append(f"[HIGH] Rewrite your bio — currently scored {bio_analysis['bio_score']}/100")
    if not engagement_rate or engagement_rate < 3:
        priority_actions.append("[HIGH] Hook viewers in first 1-3 seconds — improve watch time")
        priority_actions.append("[HIGH] Add clear CTA at end of every video: 'Follow for more'")
    priority_actions.append("[MEDIUM] Post consistently at best times for your timezone")
    priority_actions.append("[MEDIUM] Engage with 10-20 accounts in your niche daily")
    priority_actions.append("[LOW] Collaborate with creators at similar follower count")

    return {
        "audit": {
            "handle": handle,
            "platform": platform,
            "niche": detected_niche,
            "followers": followers,
            "engagement_rate_pct": round(engagement_rate, 2) if engagement_rate else None,
            "engagement_grade": engagement_grade,
        },
        "bio_analysis": bio_analysis,
        "posting_schedule": schedule,
        "hashtag_strategy": hashtags,
        "priority_actions": priority_actions,
        "viral_hooks": VIRAL_HOOKS,
        "content_pillars": CONTENT_PILLARS,
        "audited_at": datetime.utcnow().isoformat() + "Z",
    }
