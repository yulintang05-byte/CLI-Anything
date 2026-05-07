"""Account optimization engine — bio, posting schedule, content mix, and growth strategies."""

from datetime import datetime, timezone
from typing import Optional


# Optimal posting windows (UTC hour ranges) by platform and day
POSTING_WINDOWS: dict[str, dict[str, list[tuple[int, int]]]] = {
    "tiktok": {
        "monday":    [(6, 10), (19, 23)],
        "tuesday":   [(6, 9), (14, 16), (19, 22)],
        "wednesday": [(7, 9), (19, 22)],
        "thursday":  [(9, 12), (19, 23)],
        "friday":    [(5, 8), (13, 15), (19, 23)],
        "saturday":  [(11, 14), (19, 23)],
        "sunday":    [(7, 11), (19, 22)],
    },
    "youtube": {
        "monday":    [(14, 17)],
        "tuesday":   [(14, 17)],
        "wednesday": [(14, 17)],
        "thursday":  [(14, 17)],
        "friday":    [(14, 18)],
        "saturday":  [(9, 12), (15, 18)],
        "sunday":    [(9, 13)],
    },
    "instagram": {
        "monday":    [(8, 10), (18, 21)],
        "tuesday":   [(8, 10), (18, 21)],
        "wednesday": [(8, 11), (17, 20)],
        "thursday":  [(7, 9), (18, 21)],
        "friday":    [(7, 9), (16, 19)],
        "saturday":  [(9, 12), (19, 22)],
        "sunday":    [(10, 13), (19, 22)],
    },
}

# Content mix recommendations by platform and account type
CONTENT_MIX: dict[str, dict[str, dict[str, int]]] = {
    "tiktok": {
        "theme_page": {
            "reposted_viral": 40,
            "original_commentary": 20,
            "trend_participation": 25,
            "promotional": 10,
            "community_engagement": 5,
        },
        "creator": {
            "original_content": 50,
            "trend_participation": 30,
            "behind_the_scenes": 10,
            "promotional": 5,
            "community_engagement": 5,
        },
        "brand": {
            "product_showcase": 30,
            "educational": 30,
            "entertainment": 25,
            "ugc_reposts": 10,
            "promotional_cta": 5,
        },
    },
    "youtube": {
        "theme_page": {
            "curated_compilations": 45,
            "original_commentary": 25,
            "trend_roundups": 20,
            "promotional": 10,
        },
        "creator": {
            "long_form_original": 40,
            "shorts": 30,
            "tutorials": 15,
            "vlogs": 10,
            "promotional": 5,
        },
    },
    "instagram": {
        "theme_page": {
            "reposted_aesthetic": 35,
            "original_quotes": 25,
            "reels": 25,
            "stories": 10,
            "promotional": 5,
        },
        "creator": {
            "original_posts": 40,
            "reels": 35,
            "stories_daily": 15,
            "collabs": 10,
        },
    },
}

# Bio templates by account type and niche
BIO_TEMPLATES: dict[str, dict[str, str]] = {
    "tiktok": {
        "motivation": "🔥 Daily fuel for your grind\n⬇️ Follow for mindset shifts\n💡 {niche} tips + collab ↓",
        "fitness": "💪 {niche} → Real results\n🏆 {followers}+ transforming their lives\n📩 DM for coaching | Link ↓",
        "luxury": "✨ Curating the finer side of life\n🚗💎 {niche} content daily\n👑 Business: DM or link ↓",
        "aesthetic": "🌙 Curating beauty, one frame at a time\n📸 {niche} ∙ vibes ∙ inspiration\n↓ New drops weekly",
        "finance": "📈 Helping you build real wealth\n💰 {niche} tips every day\n🔗 Free resources ↓ | DM for 1:1",
        "themepage": "🌐 Curating the best {niche} content\n🔥 New posts daily\n📩 Collabs & shoutouts ↓",
        "food": "🍴 {niche} recipes & reviews\n😋 New video daily\n🔗 Full recipes ↓",
        "travel": "✈️ Exploring the world on a budget\n🌍 {niche} content weekly\n💼 Collabs → link ↓",
    },
    "youtube": {
        "general": "Subscribe for weekly {niche} content 🔔\n{followers}+ subscribers and growing!\n📧 Business: [email]",
    },
    "instagram": {
        "general": "✨ {niche} inspiration daily\n🔗 {link_text} ↓\n📩 Collab? DM me",
    },
}

# Growth playbooks by account stage
GROWTH_PLAYBOOKS: dict[str, dict] = {
    "0-1k": {
        "label": "Foundation (0-1K followers)",
        "priority": "Consistency and niche clarity",
        "daily_actions": [
            "Post 2-3x per day on TikTok, 1x on Instagram",
            "Comment meaningfully on 20 accounts in your niche daily",
            "Follow 50 accounts in your niche (unfollow non-followers after 3 days)",
            "Study your 3 biggest competitor accounts — mirror their top content",
            "Use trending sounds on every TikTok video",
        ],
        "avoid": [
            "Posting in multiple unrelated niches",
            "Using mega hashtags only (#fyp with nothing else)",
            "Ignoring comments on your own posts",
            "Deleting posts that underperform — they still contribute to SEO",
        ],
        "kpis": {"weekly_posts": 15, "engagement_target": "5%+", "follow_ratio": "1:1"},
    },
    "1k-10k": {
        "label": "Growth (1K-10K followers)",
        "priority": "Viral hooks and algorithm testing",
        "daily_actions": [
            "A/B test video hooks — compare first 3 seconds across posts",
            "Analyze your top 5 posts weekly — double down on that content style",
            "Engage every comment within 1 hour of posting (boosts distribution)",
            "Start an email list or Discord now while growth is cheap",
            "Duet or stitch 2x/week with creators in your niche (bigger audience reach)",
        ],
        "avoid": [
            "Changing your niche or content style after early success",
            "Buying fake followers — kills engagement rate permanently",
            "Posting all content at once — space posts 4+ hours apart",
        ],
        "kpis": {"weekly_posts": 12, "engagement_target": "4%+", "monthly_follower_growth": "15-30%"},
    },
    "10k-100k": {
        "label": "Scale (10K-100K followers)",
        "priority": "Monetization and community building",
        "daily_actions": [
            "Apply for TikTok Creator Fund and YouTube Partner Program",
            "Begin affiliate marketing with 2-3 relevant products",
            "Post consistently: quality > quantity at this stage (1-2x/day TikTok)",
            "Launch a Patreon, newsletter, or course with your engaged audience",
            "Collab with creators at 2-5x your size for crossover exposure",
        ],
        "monetization": [
            "TikTok Series (paid content gating)",
            "Affiliate links in bio (Amazon, ShareASale, Impact)",
            "Sponsored posts ($0.01-0.05 per follower per post)",
            "Digital products (presets, ebooks, templates)",
            "Brand deals — pitch brands in your niche proactively",
        ],
        "kpis": {"weekly_posts": 10, "engagement_target": "3%+", "monthly_revenue_target": "$500-5000"},
    },
    "100k+": {
        "label": "Authority (100K+ followers)",
        "priority": "Brand equity and scalable revenue",
        "daily_actions": [
            "Hire a video editor or VA — your time is worth $100+/hour",
            "Develop a signature content format you own (your 'series')",
            "Launch a paid community or premium tier",
            "Negotiate long-term brand partnerships (not one-off posts)",
            "Cross-post to all platforms with platform-native edits",
        ],
        "monetization": [
            "YouTube AdSense ($3-10 RPM for general, $15-50 for finance/tech)",
            "TikTok Pulse (premium ad share program)",
            "Live gifting and TikTok Shop affiliate",
            "Speaking engagements and brand ambassador roles",
            "Your own product line or SaaS",
        ],
        "kpis": {"weekly_posts": 7, "engagement_target": "2%+", "monthly_revenue_target": "$5000-50000+"},
    },
}


def get_posting_schedule(
    platform: str = "tiktok",
    timezone_offset: int = 0,
    posts_per_day: int = 2,
    account_type: str = "theme_page",
) -> dict:
    """Generate an optimal posting schedule for the given platform."""
    platform = platform.lower()
    schedule = POSTING_WINDOWS.get(platform, POSTING_WINDOWS["tiktok"])

    week_schedule = []
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for day in days:
        windows = schedule.get(day, [(12, 14)])
        posts_today = []
        for i, (start, end) in enumerate(windows[:posts_per_day]):
            local_start = (start + timezone_offset) % 24
            local_end = (end + timezone_offset) % 24
            posts_today.append({
                "time_window": f"{local_start:02d}:00 - {local_end:02d}:00",
                "optimal_time": f"{(local_start + local_end) // 2:02d}:00",
                "post_number": i + 1,
            })
        week_schedule.append({"day": day.capitalize(), "posts": posts_today})

    mix = CONTENT_MIX.get(platform, {}).get(account_type, {})
    return {
        "platform": platform,
        "account_type": account_type,
        "posts_per_day": posts_per_day,
        "timezone_offset": f"UTC{'+' if timezone_offset >= 0 else ''}{timezone_offset}",
        "weekly_schedule": week_schedule,
        "content_mix_percent": mix,
        "schedule_tips": _schedule_tips(platform),
    }


def optimize_bio(
    platform: str = "tiktok",
    niche: str = "general",
    followers: int = 0,
    link_text: str = "Free guide",
) -> dict:
    """Generate an optimized bio for the given platform and niche."""
    templates = BIO_TEMPLATES.get(platform.lower(), BIO_TEMPLATES["tiktok"])
    template = templates.get(niche.lower(), templates.get("themepage", ""))

    formatted = template.format(
        niche=niche.capitalize(),
        followers=f"{followers:,}" if followers else "Growing",
        link_text=link_text,
    ) if template else f"✨ {niche.capitalize()} content daily\n🔗 {link_text} ↓\n📩 Collabs: DM"

    limits = {"tiktok": 80, "youtube": 1000, "instagram": 150}
    char_limit = limits.get(platform.lower(), 150)

    checklist = [
        {"item": "Clear niche statement in first line", "done": bool(niche)},
        {"item": "Call-to-action (CTA) present", "done": "↓" in formatted or "DM" in formatted},
        {"item": "Business contact method visible", "done": "DM" in formatted or "email" in formatted.lower()},
        {"item": "Within character limit", "done": len(formatted) <= char_limit},
        {"item": "Emoji used for visual scanning", "done": any(ord(c) > 127 for c in formatted)},
    ]

    score = sum(1 for c in checklist if c["done"]) * 20

    return {
        "platform": platform,
        "niche": niche,
        "bio": formatted,
        "character_count": len(formatted),
        "character_limit": char_limit,
        "optimization_score": score,
        "checklist": checklist,
        "bio_tips": _bio_tips(platform),
    }


def get_growth_playbook(follower_count: int, platform: str = "tiktok") -> dict:
    """Return the appropriate growth playbook based on follower count."""
    if follower_count < 1000:
        stage = "0-1k"
    elif follower_count < 10000:
        stage = "1k-10k"
    elif follower_count < 100000:
        stage = "10k-100k"
    else:
        stage = "100k+"

    playbook = GROWTH_PLAYBOOKS[stage].copy()
    playbook["current_followers"] = follower_count
    playbook["platform"] = platform
    playbook["next_milestone"] = {
        "0-1k": 1000, "1k-10k": 10000, "10k-100k": 100000, "100k+": None,
    }[stage]
    playbook["generated_at"] = datetime.now(timezone.utc).isoformat()
    return playbook


def audit_account(
    platform: str,
    username: str,
    follower_count: int,
    following_count: int,
    post_count: int,
    avg_views: int,
    avg_likes: int,
    niche: str = "general",
    account_type: str = "creator",
) -> dict:
    """Run a full account audit and return optimization recommendations."""
    engagement_rate = (avg_likes / max(avg_views, 1)) * 100 if avg_views > 0 else 0
    follow_ratio = follower_count / max(following_count, 1)
    post_frequency = post_count / 30.0  # rough daily average

    benchmarks = {
        "tiktok": {"good_engagement": 5.0, "good_ratio": 3.0, "good_freq": 1.5},
        "youtube": {"good_engagement": 3.0, "good_ratio": 10.0, "good_freq": 0.5},
        "instagram": {"good_engagement": 3.0, "good_ratio": 3.0, "good_freq": 1.0},
    }
    b = benchmarks.get(platform.lower(), benchmarks["tiktok"])

    issues = []
    strengths = []
    recommendations = []

    if engagement_rate >= b["good_engagement"]:
        strengths.append(f"Strong engagement rate: {engagement_rate:.1f}%")
    else:
        issues.append(f"Low engagement rate: {engagement_rate:.1f}% (target: {b['good_engagement']}%+)")
        recommendations.append("Post at peak times and reply to every comment within 1 hour of posting.")

    if follow_ratio >= b["good_ratio"]:
        strengths.append(f"Good follower/following ratio: {follow_ratio:.1f}:1")
    else:
        issues.append(f"Poor follower/following ratio: {follow_ratio:.1f}:1 (target: {b['good_ratio']}:1+)")
        recommendations.append("Unfollow inactive or non-niche accounts to improve ratio.")

    if post_frequency >= b["good_freq"]:
        strengths.append(f"Consistent posting: {post_frequency:.1f} posts/day average")
    else:
        issues.append(f"Infrequent posting: {post_frequency:.1f} posts/day (target: {b['good_freq']}+/day)")
        recommendations.append("Increase posting frequency — consistency is the #1 growth driver.")

    health_score = max(0, 100 - (len(issues) * 25) + (len(strengths) * 10))

    return {
        "username": username,
        "platform": platform,
        "niche": niche,
        "account_type": account_type,
        "audited_at": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "followers": follower_count,
            "following": following_count,
            "posts": post_count,
            "avg_views": avg_views,
            "avg_likes": avg_likes,
            "engagement_rate_percent": round(engagement_rate, 2),
            "follower_following_ratio": round(follow_ratio, 2),
            "avg_daily_posts": round(post_frequency, 2),
        },
        "health_score": min(health_score, 100),
        "strengths": strengths,
        "issues": issues,
        "recommendations": recommendations,
        "next_steps": get_growth_playbook(follower_count, platform)["daily_actions"][:3],
    }


def _schedule_tips(platform: str) -> list[str]:
    tips = {
        "tiktok": [
            "Post your best content at peak windows, test new formats at off-peak times.",
            "Space posts 4-6 hours apart — back-to-back posts compete for the same audience.",
            "Thursday and Friday evenings (6-10 PM local) consistently produce highest reach.",
            "Weekend mornings work for aspirational content (travel, fitness, lifestyle).",
        ],
        "youtube": [
            "Upload 2-4 hours before your audience's peak viewing time so the algorithm has index time.",
            "Consistent upload day matters more than specific time for subscriber retention.",
            "Shorts can be posted daily; long-form 1-3x/week is the sweet spot.",
        ],
        "instagram": [
            "Post Reels early in the day — they're distributed throughout the following 24-48 hours.",
            "Stories should be posted 3-5x per day at any time — they're always in sequence.",
            "Weekday morning posts (7-9 AM) catch commuters; evening posts (7-9 PM) catch leisure time.",
        ],
    }
    return tips.get(platform, tips["tiktok"])


def _bio_tips(platform: str) -> list[str]:
    tips = {
        "tiktok": [
            "First 2 lines show on profile preview — make them hook immediately.",
            "Use line breaks (Enter key) to create scannable bios.",
            "Link in bio tools (Linktree, Stan.store) let you host multiple links.",
            "Add your posting schedule ('New video daily 6PM') to set expectations.",
        ],
        "youtube": [
            "YouTube description (About section) is indexed by Google — include keywords.",
            "Add all your social links and a business email.",
            "First 100 characters show in search results — lead with value proposition.",
        ],
        "instagram": [
            "Instagram bios are indexed in search — include your niche keyword.",
            "Use the 'name field' (not bio) for your keyword — it's searchable.",
            "Add a CTA to every bio: 'New post daily ↓', 'Link below ↓', 'DM for collab'.",
        ],
    }
    return tips.get(platform, tips["tiktok"])
