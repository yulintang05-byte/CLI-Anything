"""Account optimizer — generates data-driven recommendations for social media accounts."""

import json
from typing import Any


PLATFORM_BEST_PRACTICES = {
    "tiktok": {
        "post_frequency": "1-3x per day",
        "best_times": ["7-9 AM", "12-3 PM", "7-11 PM"],
        "video_length": "15-60s (Shorts/Reels), 3-5min (storytelling)",
        "caption_length": "< 150 chars + 3-5 hashtags",
        "hashtag_count": "3-5 targeted + 1-2 broad",
        "hook_window_seconds": 3,
        "cta_types": ["Follow for more", "Part 2 in comments", "Duet this", "Link in bio"],
        "content_pillars": ["Education", "Entertainment", "Inspiration", "Community"],
        "growth_hacks": [
            "Reply to comments with a video response",
            "Use trending sounds within 48h of them breaking",
            "Stitch popular videos in your niche",
            "Post at your audience's peak activity time",
            "Use 1 mega-niche + 2 broad hashtags per post",
        ],
    },
    "youtube": {
        "post_frequency": "1-3x per week (long-form), daily (Shorts)",
        "best_times": ["12-3 PM", "5-9 PM weekdays"],
        "video_length": "8-15min (long-form for ad revenue), 60s (Shorts)",
        "caption_length": "1000-2000 chars, keyword-rich first 200",
        "hashtag_count": "3-5 in description",
        "hook_window_seconds": 30,
        "cta_types": ["Subscribe", "Like & comment", "Watch next", "Join membership"],
        "content_pillars": ["Tutorials", "Reviews", "Vlogs", "Listicles", "Reactions"],
        "growth_hacks": [
            "Front-load keywords in title (first 40 chars)",
            "Custom thumbnails with faces + bold text get 30% more CTR",
            "Add chapters to boost search ranking",
            "End screen + cards on every video",
            "Respond to every comment in first 24h",
        ],
    },
    "instagram": {
        "post_frequency": "4-7x per week (Reels), 3-5x (Feed)",
        "best_times": ["11 AM-1 PM", "7-9 PM"],
        "video_length": "15-90s (Reels), 60s (Stories)",
        "caption_length": "< 2200 chars, key info in first 125",
        "hashtag_count": "5-15 targeted",
        "hook_window_seconds": 3,
        "cta_types": ["Save this", "Share with a friend", "Link in bio", "DM for info"],
        "content_pillars": ["Aesthetic", "Value", "Relatable", "BTS"],
        "growth_hacks": [
            "Post Reels to maximize reach vs. static posts",
            "Collab posts reach both audiences",
            "Add alt text with keywords for SEO",
            "Stories polls/questions boost engagement rate",
            "Consistent aesthetic = higher follow rate",
        ],
    },
}

NICHE_HASHTAG_STACKS = {
    "fitness": ["#fitnessmotivation", "#workout", "#gym", "#health", "#fitness"],
    "finance": ["#personalfinance", "#investing", "#money", "#wealth", "#financetips"],
    "travel": ["#travel", "#wanderlust", "#travelgram", "#adventure", "#explore"],
    "food": ["#foodie", "#recipe", "#cooking", "#instafood", "#homecooking"],
    "beauty": ["#beauty", "#makeup", "#skincare", "#beautytips", "#glowup"],
    "motivation": ["#motivation", "#mindset", "#success", "#hustle", "#grind"],
    "tech": ["#tech", "#technology", "#ai", "#coding", "#startup"],
    "fashion": ["#fashion", "#style", "#ootd", "#outfitinspo", "#fashionblogger"],
}


def generate_account_report(account: dict, trend_data: list[dict] | None = None) -> dict:
    """
    Generate optimization recommendations for an account profile.

    account dict keys:
      - platform: str (tiktok/youtube/instagram)
      - niche: str
      - followers: int
      - avg_views: int
      - avg_likes: int
      - avg_comments: int
      - post_frequency: str (optional)
      - hashtags_used: list[str] (optional)
    """
    platform = account.get("platform", "tiktok").lower()
    niche = account.get("niche", "general").lower()
    followers = account.get("followers", 0)
    avg_views = account.get("avg_views", 0)
    avg_likes = account.get("avg_likes", 0)
    avg_comments = account.get("avg_comments", 0)

    bp = PLATFORM_BEST_PRACTICES.get(platform, PLATFORM_BEST_PRACTICES["tiktok"])
    niche_tags = NICHE_HASHTAG_STACKS.get(niche, [])

    # Engagement rate
    eng_rate = 0.0
    if followers > 0:
        eng_rate = round(((avg_likes + avg_comments) / followers) * 100, 2)

    # View ratio
    view_ratio = round(avg_views / max(followers, 1), 2) if followers > 0 else 0

    # Tier classification
    if followers < 1_000:
        tier = "nano"
    elif followers < 10_000:
        tier = "micro"
    elif followers < 100_000:
        tier = "mid"
    elif followers < 1_000_000:
        tier = "macro"
    else:
        tier = "mega"

    # Build action items
    actions = []

    if eng_rate < 1.0:
        actions.append({
            "priority": "HIGH",
            "area": "Engagement",
            "issue": f"Engagement rate {eng_rate}% is below 1% threshold",
            "fix": "End every video with a direct question. Reply to all comments within 1h of posting.",
        })
    elif eng_rate < 3.0:
        actions.append({
            "priority": "MEDIUM",
            "area": "Engagement",
            "issue": f"Engagement rate {eng_rate}% is below 3% target",
            "fix": "Add polls/questions in Stories. Use CTAs like 'Comment your answer below'.",
        })

    if view_ratio < 0.5:
        actions.append({
            "priority": "HIGH",
            "area": "Reach",
            "issue": f"View-to-follower ratio {view_ratio} is low — content not reaching followers",
            "fix": "Post during peak hours, use trending sounds, improve hook in first 3 seconds.",
        })

    hashtags_used = account.get("hashtags_used", [])
    if len(hashtags_used) > 20:
        actions.append({
            "priority": "MEDIUM",
            "area": "Hashtags",
            "issue": "Too many hashtags — dilutes reach",
            "fix": f"Reduce to {bp['hashtag_count']}. Mix niche + broad tags.",
        })
    elif len(hashtags_used) < 3:
        actions.append({
            "priority": "MEDIUM",
            "area": "Hashtags",
            "issue": "Too few hashtags",
            "fix": f"Use {bp['hashtag_count']} per post. Suggested: {', '.join(niche_tags[:5])}",
        })

    # Add trend-based recommendations
    trend_recs = []
    if trend_data:
        from cli_anything.viral_trends.core.analyzer import extract_hashtags, extract_music
        top_tags = extract_hashtags(trend_data, top=5)
        top_music = extract_music(trend_data, top=3)
        if top_tags:
            trend_recs.append({
                "type": "trending_hashtags",
                "items": [h["hashtag"] for h in top_tags],
                "note": "Add 1-2 of these to your next post",
            })
        if top_music:
            trend_recs.append({
                "type": "trending_music",
                "items": [f"{m['track']} — {m['artist']}" for m in top_music],
                "note": "Use trending sounds within 48h of them breaking for maximum boost",
            })

    return {
        "account": {
            "platform": platform,
            "niche": niche,
            "followers": followers,
            "tier": tier,
        },
        "metrics": {
            "avg_views": avg_views,
            "avg_likes": avg_likes,
            "avg_comments": avg_comments,
            "engagement_rate_pct": eng_rate,
            "view_to_follower_ratio": view_ratio,
        },
        "platform_best_practices": bp,
        "niche_hashtag_stack": niche_tags,
        "action_items": actions,
        "trend_recommendations": trend_recs,
        "content_pillars": bp["content_pillars"],
        "growth_hacks": bp["growth_hacks"],
    }


def generate_template() -> dict:
    """Return an empty account profile template."""
    return {
        "platform": "tiktok",
        "niche": "fitness",
        "followers": 0,
        "avg_views": 0,
        "avg_likes": 0,
        "avg_comments": 0,
        "post_frequency": "3x per week",
        "hashtags_used": [],
    }


def optimize_multiple(accounts: list[dict], trend_data: list[dict] | None = None) -> list[dict]:
    """Optimize a list of account profiles."""
    return [generate_account_report(acc, trend_data) for acc in accounts]
