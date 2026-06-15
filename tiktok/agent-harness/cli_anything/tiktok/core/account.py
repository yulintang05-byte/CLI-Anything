"""TikTok account optimization and analytics."""

from cli_anything.tiktok.utils.tiktok_backend import (
    load_config, save_config,
    fetch_account_info,
    get_rapidapi_key, get_apify_token,
)


def setup_api(rapidapi_key: str = "", apify_token: str = "") -> dict:
    cfg = load_config()
    if rapidapi_key:
        cfg["rapidapi_key"] = rapidapi_key
    if apify_token:
        cfg["apify_token"] = apify_token
    save_config(cfg)
    return {
        "status": "configured",
        "rapidapi_key_set": bool(cfg.get("rapidapi_key")),
        "apify_token_set": bool(cfg.get("apify_token")),
    }


def get_api_status() -> dict:
    cfg = load_config()
    return {
        "rapidapi_key_set": bool(cfg.get("rapidapi_key")),
        "apify_token_set": bool(cfg.get("apify_token")),
        "rapidapi_key_preview": cfg.get("rapidapi_key", "")[:8] + "..." if cfg.get("rapidapi_key") else None,
        "mode": "live" if (cfg.get("rapidapi_key") or cfg.get("apify_token")) else "demo",
    }


def audit_account(username: str) -> dict:
    """Audit a TikTok account and return optimization recommendations."""
    info = fetch_account_info(username)
    followers = info.get("followers", 0)
    likes = info.get("likes", 0)
    videos = info.get("videos", 0)

    # Engagement rate estimate
    avg_likes_per_video = likes // videos if videos else 0
    engagement_rate = round((avg_likes_per_video / followers * 100), 2) if followers else 0

    # Score account health
    health_score = 0
    recommendations = []

    if followers < 1000:
        recommendations.append("🚀 Focus on posting 2-3x daily with trending sounds to build initial followers.")
        health_score += 10
    elif followers < 10000:
        recommendations.append("📈 You're past 1K — consistency is key. Post daily and engage with comments within 1hr.")
        health_score += 30
    elif followers < 100000:
        recommendations.append("💪 Strong base — start collaborating with similar accounts via duet/stitch.")
        health_score += 60
    else:
        recommendations.append("🌟 Large audience — diversify income: affiliate links, merch, brand deals.")
        health_score += 90

    if not info.get("bio"):
        recommendations.append("📝 Add a bio with your niche + call-to-action (e.g., 'Follow for daily tips ↓').")
    else:
        health_score += 5

    if engagement_rate < 1:
        recommendations.append("⚠️  Low engagement rate — hook viewers in first 0.5 seconds, end with a question.")
    elif engagement_rate < 5:
        recommendations.append("👍 Decent engagement — experiment with POV format and 'story time' hooks.")
    else:
        recommendations.append("🔥 Excellent engagement — double down on what's working, scale with paid promotion.")
        health_score += 10

    if info.get("private"):
        recommendations.append("🔓 Account is PRIVATE — switch to public to appear in FYP and searches.")

    monetization_unlocked = followers >= 10000
    monetization_tips = []
    if followers >= 10000:
        monetization_tips.append("TikTok Creator Fund (apply in app)")
        monetization_tips.append("TikTok LIVE gifts (go live regularly)")
    if followers >= 1000:
        monetization_tips.append("Affiliate marketing via bio link")
        monetization_tips.append("Brand deals (reach out to brands in your niche)")
    if not monetization_tips:
        monetization_tips.append("Grow to 1K followers to unlock link-in-bio, then affiliate marketing")

    return {
        "account": info,
        "metrics": {
            "followers": followers,
            "avg_likes_per_video": avg_likes_per_video,
            "estimated_engagement_rate": f"{engagement_rate}%",
            "health_score": f"{health_score}/100",
        },
        "recommendations": recommendations,
        "monetization_unlocked": monetization_unlocked,
        "monetization_tips": monetization_tips,
    }


def get_optimization_checklist(username: str = "") -> dict:
    """Return a universal account optimization checklist."""
    return {
        "profile_optimization": [
            "Profile picture: clear, high-contrast, niche-relevant",
            "Username: short, memorable, brand-consistent",
            "Display name: include 1-2 keywords (e.g., 'Fitness Tips | Coach Mike')",
            "Bio: niche + value prop + CTA in 80 chars (e.g., 'Daily money tips 💰 | Link below 👇')",
            "Link in bio: use Linktree or direct link to offer",
            "Add TikTok Series for long-form content monetization",
        ],
        "content_strategy": [
            "Post 1-3 times daily at peak hours (6-9am, 12-3pm, 7-11pm local)",
            "Hook in first 1-3 seconds (text overlay or action)",
            "Use trending sounds at low usage (before they peak)",
            "Reply to ALL comments in first 2 hours (boosts algorithm)",
            "End every video with a question to drive comments",
            "Use 3-6 hashtags: 2 mega + 3 niche-specific",
            "Batch create 14-21 videos on weekends for the week",
        ],
        "growth_tactics": [
            "Duet/stitch viral videos in your niche",
            "Post behind-the-scenes and 'how I did X' content",
            "Run 'comment a number' or 'drop a ❤️' engagement bait",
            "Cross-post to Instagram Reels and YouTube Shorts",
            "Go LIVE 2-3x per week (boosts organic reach)",
            "Collaborate with 5-50K accounts (similar follower count)",
        ],
        "analytics_to_track": [
            "Profile views (track weekly)",
            "Follower growth rate",
            "Average watch time % (aim for >50%)",
            "Traffic source (FYP % indicates viral potential)",
            "Best performing video format",
        ],
    }
