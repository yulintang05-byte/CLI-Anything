"""Social media account optimization engine."""
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


# Optimal posting windows (UTC hours) per platform
_BEST_POSTING_HOURS = {
    "tiktok": [6, 9, 12, 15, 19, 21],       # 6am, 9am, noon, 3pm, 7pm, 9pm
    "youtube": [14, 15, 16, 17, 18],          # 2-6pm (audience largest)
    "instagram": [8, 11, 14, 17, 19, 21],
    "twitter": [8, 9, 12, 17, 18, 19],
    "facebook": [9, 10, 11, 14, 15],
}

_BEST_POSTING_DAYS = {
    "tiktok": ["Tuesday", "Thursday", "Friday", "Saturday"],
    "youtube": ["Thursday", "Friday", "Saturday", "Sunday"],
    "instagram": ["Monday", "Wednesday", "Friday"],
    "twitter": ["Wednesday", "Thursday", "Friday"],
    "facebook": ["Wednesday", "Thursday", "Friday"],
}

_IDEAL_FREQUENCIES = {
    "tiktok": {"min": 1, "max": 4, "unit": "day", "note": "1-4 videos/day; volume drives reach"},
    "youtube": {"min": 1, "max": 3, "unit": "week", "note": "Consistency over frequency"},
    "instagram_reels": {"min": 1, "max": 2, "unit": "day", "note": "Reels get 2x reach of posts"},
    "instagram_posts": {"min": 3, "max": 5, "unit": "week", "note": "Quality over quantity"},
    "twitter": {"min": 3, "max": 10, "unit": "day", "note": "Threads perform 3x better"},
    "facebook": {"min": 1, "max": 2, "unit": "day", "note": "Videos get 3x organic reach"},
}

_BIO_KEYWORDS = [
    "creator", "official", "page", "content", "daily", "tips", "news",
    "lifestyle", "entertainment", "education", "motivation", "comedy",
    "fitness", "food", "travel", "tech", "finance", "fashion", "beauty",
    "gaming", "sports", "music", "art", "business", "entrepreneur",
]

_CTA_TEMPLATES = {
    "follow": [
        "Follow for daily {niche} content!",
        "Follow to never miss a {niche} update",
        "Hit follow for {niche} content every day",
    ],
    "engagement": [
        "Drop a 🔥 if you agree",
        "Comment your thoughts below!",
        "Share this with someone who needs to see it",
        "Save this for later!",
    ],
    "link": [
        "Link in bio for more!",
        "Check the link in bio 👆",
        "Full guide in bio ↑",
    ],
}

_PROFILE_CHECKLIST = {
    "profile_picture": {
        "required": True,
        "tips": [
            "Use a clear, high-contrast face or logo",
            "Consistent across all platforms = instant recognition",
            "Avoid text (too small to read at thumbnail size)",
            "Use warm colors — they outperform cool colors by 38%",
        ],
    },
    "username": {
        "required": True,
        "tips": [
            "Keep it short (under 15 chars) and memorable",
            "Same handle across all platforms",
            "Avoid numbers and underscores if possible",
            "Include niche keyword for discoverability",
        ],
    },
    "bio": {
        "required": True,
        "tips": [
            "First line: who you are + what value you provide",
            "Second line: social proof (followers, achievements)",
            "Third line: CTA + link",
            "Use emojis to break up text visually",
            "Include 1-3 niche keywords for search",
        ],
    },
    "link_in_bio": {
        "required": True,
        "tips": [
            "Use Linktree, Beacons, or Stan.store",
            "Always link to your money page or highest-value asset",
            "Update it to match current content/offers",
        ],
    },
    "highlights": {
        "required": False,
        "platforms": ["instagram"],
        "tips": [
            "Create 5-8 story highlights",
            "Cover: About, FAQ, Products/Links, Reviews, Behind the Scenes",
            "Custom highlight covers in your brand colors",
        ],
    },
    "pinned_posts": {
        "required": False,
        "platforms": ["tiktok", "twitter"],
        "tips": [
            "Pin your best-performing video",
            "Pin a 'welcome' video explaining your account",
            "Update pins when a new viral piece drops",
        ],
    },
}


def analyze_account_profile(
    platform: str,
    handle: str,
    niche: str = "",
    bio_text: str = "",
    follower_count: int = 0,
    post_count: int = 0,
    avg_views: int = 0,
) -> Dict[str, Any]:
    """
    Analyze a social media account and return optimization recommendations.

    Works with data provided (no login required).
    """
    platform = platform.lower().strip()
    score = 0
    issues = []
    wins = []
    recommendations = []

    # --- Bio analysis ---
    if bio_text:
        bio_len = len(bio_text)
        has_cta = any(w in bio_text.lower() for w in ["follow", "link", "click", "check", "visit", "subscribe"])
        has_keywords = any(k in bio_text.lower() for k in _BIO_KEYWORDS)
        has_niche = niche.lower() in bio_text.lower() if niche else True
        has_emoji = bool(re.search(r"[\U0001F300-\U0001FFFF]|[☀-➿]", bio_text))

        if bio_len < 50:
            issues.append("Bio is too short — add more value proposition and keywords")
            score += 1
        elif bio_len > 30:
            score += 10
            wins.append("Bio has good length")

        if has_cta:
            score += 10
            wins.append("Bio contains a call-to-action")
        else:
            issues.append("Bio missing CTA — add 'Follow for daily [niche] content!' or 'Link in bio'")

        if has_keywords:
            score += 5
            wins.append("Bio contains niche keywords (good for search)")
        else:
            issues.append(f"Bio missing niche keywords — add words like '{niche}', 'content', 'creator'")

        if has_emoji:
            score += 5
            wins.append("Bio uses emojis (improves readability)")
        else:
            recommendations.append("Add 2-3 relevant emojis to bio for visual appeal")

        if not has_niche and niche:
            issues.append(f"Bio doesn't mention your niche '{niche}' — hurts discoverability")
    else:
        issues.append("No bio provided for analysis — add a bio to your account")
        recommendations.append("Write a bio: 'I post [niche] content | [CTA] | [Link]'")

    # --- Follower/engagement analysis ---
    if follower_count > 0 and avg_views > 0:
        view_rate = avg_views / follower_count
        if view_rate >= 0.3:
            score += 20
            wins.append(f"Strong view rate: {view_rate:.0%} of followers watch each video")
        elif view_rate >= 0.1:
            score += 10
            wins.append(f"Average view rate: {view_rate:.0%}")
        else:
            issues.append(
                f"Low view rate ({view_rate:.1%}). Fix: post more consistently, "
                "use trending hashtags, improve hooks in first 3 seconds"
            )

    # --- Posting frequency analysis ---
    if post_count > 0 and follower_count > 0:
        posts_per_follower = post_count / max(follower_count, 1)
        freq_data = _IDEAL_FREQUENCIES.get(platform, {})
        recommendations.append(
            f"Ideal posting: {freq_data.get('min', 1)}-{freq_data.get('max', 3)} "
            f"times/{freq_data.get('unit', 'week')} — {freq_data.get('note', '')}"
        )

    # --- Platform-specific checks ---
    platform_rec = _platform_specific_checks(platform, niche, follower_count)
    recommendations.extend(platform_rec)

    # --- Hashtag strategy ---
    recommendations.append(
        f"Run `social hashtags generate --niche \"{niche}\" --platform {platform}` "
        f"to get optimized hashtags for your niche"
    )

    # --- Growth stage assessment ---
    growth_stage = _assess_growth_stage(platform, follower_count)

    # --- Compile profile checklist ---
    checklist = []
    for item, data in _PROFILE_CHECKLIST.items():
        platforms_needed = data.get("platforms")
        if platforms_needed and platform not in platforms_needed:
            continue
        checklist.append({
            "item": item.replace("_", " ").title(),
            "required": data["required"],
            "tips": data["tips"],
        })

    # Finalize score
    score = min(100, score + 50)  # Base 50 for having an account

    return {
        "platform": platform,
        "handle": handle,
        "niche": niche,
        "optimization_score": score,
        "growth_stage": growth_stage,
        "wins": wins,
        "issues": issues,
        "recommendations": recommendations,
        "profile_checklist": checklist,
        "posting_schedule": get_optimal_schedule(platform),
        "cta_templates": {
            k: [t.format(niche=niche or "your niche") for t in v]
            for k, v in _CTA_TEMPLATES.items()
        },
        "next_steps": _generate_next_steps(growth_stage, platform, niche, issues),
        "analyzed_at": datetime.utcnow().isoformat(),
    }


def _platform_specific_checks(
    platform: str, niche: str, followers: int
) -> List[str]:
    recs = []
    if platform == "tiktok":
        recs += [
            "TikTok: First 2-3 seconds are critical — start with a hook/pattern interrupt",
            "Use trending sounds (check 'Trending' in TikTok Creator Tools)",
            "Reply to comments with video replies to boost engagement signals",
            "Post 1-3x/day for fastest growth — consistency beats perfection",
            "Use the Creator Marketplace once you hit 10K followers for brand deals",
        ]
    elif platform == "youtube":
        recs += [
            "YouTube: Thumbnail + title drive 80% of clicks — A/B test both",
            "First 30 seconds determine watch time — deliver value immediately",
            "Add chapters/timestamps to boost search rankings",
            "Post every Thursday-Sunday for maximum initial views",
            "End screen CTAs boost subscriber conversion by 40%",
        ]
    elif platform == "instagram":
        recs += [
            "Instagram Reels get 2x more reach than static posts — prioritize Reels",
            "Use carousel posts for educational content (avg 3x more saves = algorithm boost)",
            "Stories: 7-10 story frames per day keeps you top-of-mind",
            "Collaborate with accounts 2-5x your size for follower boosts",
        ]
    elif platform == "twitter":
        recs += [
            "Twitter: Threads (5+ tweets) get 10x more engagement than single tweets",
            "Post at 8am-9am your audience's timezone for max reach",
            "Reply to trending topics early to ride virality waves",
        ]
    return recs


def _assess_growth_stage(platform: str, followers: int) -> Dict[str, Any]:
    stages = [
        (0, 1_000, "Nano", "Focus on content quality and consistency. No brand deals yet."),
        (1_000, 10_000, "Micro", "Build community. Affiliate marketing starts here."),
        (10_000, 50_000, "Growing", "Brand deals available. Theme page flips possible."),
        (50_000, 100_000, "Established", "Premium brand deals. Course sales viable."),
        (100_000, 500_000, "Macro", "Multiple revenue streams. Hire a VA."),
        (500_000, float("inf"), "Mega", "Full agency/team needed. Licensing deals."),
    ]
    for low, high, name, advice in stages:
        if low <= followers < high:
            return {
                "stage": name,
                "follower_range": f"{low:,}-{int(high):,}" if high != float("inf") else f"{low:,}+",
                "advice": advice,
                "monetization_unlocked": _monetization_at_stage(name),
            }
    return {"stage": "Nano", "advice": "Start posting consistently"}


def _monetization_at_stage(stage: str) -> List[str]:
    tiers = {
        "Nano": ["Affiliate links", "Digital products"],
        "Micro": ["Affiliate links", "Digital products", "Paid shoutouts ($20-$100/post)"],
        "Growing": [
            "Affiliate links", "Digital products", "Brand deals ($100-$500/post)",
            "Theme page flips ($500-$2K)", "UGC creator",
        ],
        "Established": [
            "Brand deals ($500-$5K/post)", "Courses/coaching",
            "Theme page network", "Agency services",
        ],
        "Macro": [
            "Premium brand deals ($5K-$50K/post)", "Own product line",
            "Speaking/appearances", "Investment partnerships",
        ],
        "Mega": ["Licensing", "Equity deals", "Production company"],
    }
    return tiers.get(stage, [])


def get_optimal_schedule(platform: str) -> Dict[str, Any]:
    """Return optimal posting schedule for a platform."""
    platform = platform.lower()
    hours = _BEST_POSTING_HOURS.get(platform, [12, 18])
    days = _BEST_POSTING_DAYS.get(platform, ["Wednesday", "Friday", "Saturday"])
    freq = _IDEAL_FREQUENCIES.get(platform, {"min": 1, "max": 3, "unit": "week", "note": ""})

    # Build a weekly schedule
    all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    schedule = {}
    for day in all_days:
        if day in days:
            post_hours = [f"{h:02d}:00 UTC" for h in hours[:2]]
            schedule[day] = {"post": True, "times": post_hours}
        else:
            schedule[day] = {"post": False, "times": []}

    return {
        "platform": platform,
        "frequency": freq,
        "best_days": days,
        "best_hours_utc": [f"{h:02d}:00" for h in hours],
        "weekly_schedule": schedule,
        "note": f"Adjust times to match YOUR audience's timezone. {freq.get('note', '')}",
    }


def _generate_next_steps(
    growth_stage: Dict, platform: str, niche: str, issues: List[str]
) -> List[str]:
    steps = []
    stage = growth_stage.get("stage", "Nano")

    # Fix critical issues first
    if issues:
        steps.append(f"🔴 Fix immediately: {issues[0]}")
    if len(issues) > 1:
        steps.append(f"🟡 Then fix: {issues[1]}")

    # Stage-specific next steps
    if stage == "Nano":
        steps += [
            f"Post {niche} content 3x this week without overthinking quality",
            "Find 10 accounts in your niche and engage genuinely with their content",
            "Study top 3 viral videos in your niche — reverse-engineer the format",
        ]
    elif stage == "Micro":
        steps += [
            "Join 2-3 affiliate programs in your niche (Amazon, ShareASale, etc.)",
            "Create a simple Linktree with your top affiliate links",
            "DM 5 creators at your level for a collab or shoutout swap",
        ]
    elif stage in ("Growing", "Established"):
        steps += [
            "Create a media kit (follower count, demographics, avg engagement rate)",
            "Pitch 3 brands in your niche this week",
            "Launch a digital product or course — your audience will buy",
        ]

    steps.append(
        f"Run `social optimize hashtags --niche \"{niche}\" --platform {platform}` "
        "for a fresh hashtag set"
    )
    return steps


def batch_optimize_accounts(accounts: List[Dict]) -> List[Dict]:
    """Run optimization analysis on multiple accounts."""
    results = []
    for acc in accounts:
        result = analyze_account_profile(
            platform=acc.get("platform", "tiktok"),
            handle=acc.get("handle", ""),
            niche=acc.get("niche", ""),
            bio_text=acc.get("bio", ""),
            follower_count=acc.get("followers", 0),
            post_count=acc.get("posts", 0),
            avg_views=acc.get("avg_views", 0),
        )
        results.append(result)
    return results
