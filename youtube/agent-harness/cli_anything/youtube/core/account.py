"""YouTube channel optimization and analytics."""

from cli_anything.youtube.utils.youtube_backend import (
    load_config, save_config,
    fetch_channel_info,
    get_api_key,
)


def setup_api(api_key: str) -> dict:
    cfg = load_config()
    cfg["api_key"] = api_key
    save_config(cfg)
    return {
        "status": "configured",
        "api_key_preview": api_key[:8] + "...",
    }


def get_api_status() -> dict:
    cfg = load_config()
    key = cfg.get("api_key")
    return {
        "api_key_set": bool(key),
        "api_key_preview": key[:8] + "..." if key else None,
        "mode": "live" if key else "demo",
        "quota_note": "YouTube Data API v3 free tier: 10,000 units/day",
    }


def audit_channel(channel_handle: str) -> dict:
    """Audit a YouTube channel and return optimization recommendations."""
    info = fetch_channel_info(channel_handle)
    subs = info.get("subscribers", 0)
    views = info.get("total_views", 0)
    videos = info.get("video_count", 0)

    avg_views_per_video = views // videos if videos else 0
    recommendations = []
    health_score = 0

    # Subscriber-based guidance
    if subs < 1000:
        recommendations.append("🎯 Focus on Shorts (60s) — they get 10-30x more exposure for new channels.")
        health_score += 10
    elif subs < 10000:
        recommendations.append("📈 You're past 1K — apply for YouTube Partner Program (YPP). Post 3x/week.")
        health_score += 30
    elif subs < 100000:
        recommendations.append("💡 Strong base — A/B test thumbnails using TubeBuddy/VidIQ.")
        health_score += 60
    else:
        recommendations.append("🌟 Large channel — focus on Memberships, Super Thanks, and brand deals.")
        health_score += 90

    if avg_views_per_video < subs * 0.05:
        recommendations.append("⚠️  Low view/sub ratio — titles may not be compelling. Test curiosity-gap titles.")
    elif avg_views_per_video > subs * 0.2:
        recommendations.append("🔥 Strong view/sub ratio — you're punching above your weight. Scale content output.")
        health_score += 10

    if not info.get("description"):
        recommendations.append("📝 Channel has no description — add keywords + links in About section.")

    ypp_eligible = subs >= 1000 and views >= 4000
    monetization_tips = []
    if subs >= 500:
        monetization_tips.append("Channel Memberships (apply via YouTube Studio)")
    if ypp_eligible:
        monetization_tips.append("YouTube Partner Program — AdSense revenue sharing")
        monetization_tips.append("Super Thanks / Super Chats on live streams")
    if subs >= 1000:
        monetization_tips.append("Affiliate links in video descriptions")
        monetization_tips.append("Brand sponsorships (use AspireIQ, Grin, or direct outreach)")
    if not monetization_tips:
        monetization_tips.append("Grow to 500 subs to unlock Memberships, 1K for YPP")

    return {
        "channel": info,
        "metrics": {
            "subscribers": subs,
            "total_views": views,
            "videos": videos,
            "avg_views_per_video": avg_views_per_video,
            "health_score": f"{min(health_score, 100)}/100",
        },
        "ypp_eligible": ypp_eligible,
        "ypp_requirements": {
            "subscribers_needed": max(0, 1000 - subs),
            "watch_hours_needed": "4,000 public watch hours in last 12 months",
        },
        "recommendations": recommendations,
        "monetization_tips": monetization_tips,
    }


def get_optimization_checklist() -> dict:
    return {
        "channel_branding": [
            "Channel art (2560x1440px) — brand colors, tagline",
            "Profile picture (800x800px) — logo or face (high contrast)",
            "Channel description: 150 words with keywords in first 100 chars",
            "Custom URL (@yourname) — requires 100 subs",
            "Featured channels: 5-10 similar channels for discovery",
            "Channel trailer: 60-90s hook video for non-subscribers",
            "Channel sections: organize playlists by topic",
        ],
        "video_optimization": [
            "Title: 60 chars max, keyword first, curiosity gap or number",
            "Thumbnail: 1280x720px, <2MB, bright colors, <3 words of text",
            "Description: 200-500 words, keyword in first 100 chars, links below",
            "Tags: 5-10 specific tags (primary keyword, variations, category)",
            "End screen: Add subscribe button + video card (last 20 seconds)",
            "Cards: Add at 20%, 50%, 80% timestamps for viewer retention",
            "Chapters: Timestamps in description (boosts SEO + watch time)",
            "Subtitles: Upload SRT file for accessibility + search indexing",
        ],
        "growth_tactics": [
            "Post Shorts (60s) 3-5x per week alongside long-form",
            "Respond to every comment in first 48 hours",
            "Premiere videos to build real-time community",
            "Collab with channels in same subscriber range",
            "Post at peak: Thursdays-Saturdays, 12pm-4pm target timezone",
            "Create series/playlists to increase session time",
            "Pin a comment with 'like + subscribe' prompt",
            "Embed videos in blog posts or Quora answers",
        ],
        "analytics_to_track": [
            "Click-through rate (CTR) — aim for 5-10%",
            "Average view duration — aim for 40-60%+",
            "Impressions from Browse features (home page recommendation)",
            "Traffic source: suggested videos indicates algorithm health",
            "Subscriber conversion rate per video",
            "Revenue per mille (RPM) after YPP approval",
        ],
    }
