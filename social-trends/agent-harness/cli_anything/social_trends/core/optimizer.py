"""Account optimizer — cross-platform hashtag strategy, posting schedules, content calendars."""

from datetime import datetime, timedelta, timezone
from typing import Optional

# Hashtag tiers by reach — used for building mixed-reach strategies
_HASHTAG_TIERS = {
    "mega": {"min_views": 1_000_000_000, "label": "mega (>1B views)", "max_per_post": 1},
    "large": {"min_views": 100_000_000, "label": "large (100M-1B views)", "max_per_post": 2},
    "medium": {"min_views": 10_000_000, "label": "medium (10M-100M views)", "max_per_post": 2},
    "niche": {"min_views": 1_000_000, "label": "niche (1M-10M views)", "max_per_post": 3},
    "micro": {"min_views": 0, "label": "micro (<1M views)", "max_per_post": 2},
}

_NICHE_HASHTAG_MAP = {
    "fitness": {
        "mega": ["fyp", "foryou", "viral"],
        "large": ["fitness", "workout", "gym"],
        "medium": ["fitnessmotivation", "gymlife", "healthylifestyle"],
        "niche": ["workoutmotivation", "fitnesscommunity", "homeworkout"],
        "micro": ["fitnesstransformation", "gymrat", "sweatyselfie"],
    },
    "finance": {
        "mega": ["fyp", "foryou", "viral"],
        "large": ["money", "investing", "finance"],
        "medium": ["financetips", "passiveincome", "sidehustle"],
        "niche": ["wealthbuilding", "stockmarket", "cryptoinvesting"],
        "micro": ["financialfreedom", "moneycoach", "budgeting"],
    },
    "food": {
        "mega": ["fyp", "foryou", "viral"],
        "large": ["food", "foodtok", "recipe"],
        "medium": ["cooking", "foodie", "easyrecipes"],
        "niche": ["mealprep", "veganrecipes", "quickmeals"],
        "micro": ["foodblogger", "healthyeating", "cookwithme"],
    },
    "beauty": {
        "mega": ["fyp", "foryou", "viral"],
        "large": ["beauty", "makeup", "skincare"],
        "medium": ["makeuphacks", "skincareaddict", "beautytips"],
        "niche": ["drugstorebeauty", "glowup", "grwm"],
        "micro": ["cleanbeauty", "makeuptutorial", "skincareroutine"],
    },
    "business": {
        "mega": ["fyp", "foryou", "viral"],
        "large": ["entrepreneur", "business", "smallbusiness"],
        "medium": ["businesstips", "startuplife", "growthhack"],
        "niche": ["entrepreneurship", "onlinebusiness", "digitalmarketing"],
        "micro": ["businessmindset", "ceolife", "ecommerce"],
    },
    "education": {
        "mega": ["fyp", "foryou", "viral"],
        "large": ["learn", "tutorial", "howto"],
        "medium": ["learnontiktok", "education", "knowledge"],
        "niche": ["studywithme", "factsyoudidntknow", "didyouknow"],
        "micro": ["studymotivation", "lifetips", "learnsomething"],
    },
    "lifestyle": {
        "mega": ["fyp", "foryou", "viral"],
        "large": ["lifestyle", "dayinmylife", "vlog"],
        "medium": ["productivity", "morningroutine", "selfimprovement"],
        "niche": ["minimalism", "aesthetic", "selflove"],
        "micro": ["slowliving", "dailyroutine", "luxurylifestyle"],
    },
    "gaming": {
        "mega": ["fyp", "foryou", "viral"],
        "large": ["gaming", "gamer", "games"],
        "medium": ["gamingclips", "twitch", "gamertok"],
        "niche": ["fps", "rpggaming", "mobilegaming"],
        "micro": ["gamingcommunity", "speedrun", "gamereviews"],
    },
    "travel": {
        "mega": ["fyp", "foryou", "viral"],
        "large": ["travel", "wanderlust", "travelgram"],
        "medium": ["traveltok", "travellife", "travelguide"],
        "niche": ["solotravel", "budgettravel", "hiddengems"],
        "micro": ["travelblogger", "roadtrip", "traveldiary"],
    },
    "fashion": {
        "mega": ["fyp", "foryou", "viral"],
        "large": ["fashion", "style", "ootd"],
        "medium": ["fashiontok", "styleinspo", "outfitoftheday"],
        "niche": ["thriftflip", "fashionhacks", "streetstyle"],
        "micro": ["fashionblogger", "ootdinspo", "capsulewardrobe"],
    },
    "general": {
        "mega": ["fyp", "foryou", "viral"],
        "large": ["trending", "explore", "viral"],
        "medium": ["contentcreator", "creatortips", "socialmedia"],
        "niche": ["themepage", "nichepage", "growthhack"],
        "micro": ["contentmarketing", "socialmediatips", "creatoreconomy"],
    },
}


def generate_hashtag_strategy(
    niche: str = "general",
    platform: str = "tiktok",
    count: int = 10,
    trending_hashtags: Optional[list] = None,
) -> dict:
    """Build a tiered hashtag strategy for a niche and platform."""
    niche_lower = niche.lower()
    base = _NICHE_HASHTAG_MAP.get(niche_lower, _NICHE_HASHTAG_MAP["general"])

    # Build the recommended set
    selected = []
    selected += base["mega"][:1]
    selected += base["large"][:2]
    selected += base["medium"][:2]
    selected += base["niche"][:3]
    selected += base["micro"][:2]

    # Inject live trending hashtags if provided (excluding mega discovery tags)
    if trending_hashtags:
        for h in trending_hashtags[:5]:
            tag = h.get("hashtag", "") if isinstance(h, dict) else str(h)
            if tag and tag not in selected and tag not in ("fyp", "foryou", "foryoupage"):
                selected.append(tag)

    # Dedupe while preserving order
    seen = set()
    unique = []
    for h in selected:
        if h not in seen:
            seen.add(h)
            unique.append(h)

    all_recommended = unique  # full deduplicated set including trending injections

    platform_rules = {
        "tiktok": {"max_hashtags": 5, "caption_limit": 2200, "note": "3-5 hashtags optimal; more dilutes reach"},
        "youtube": {"max_hashtags": 15, "caption_limit": 5000, "note": "First 3 hashtags appear above title"},
        "instagram": {"max_hashtags": 30, "caption_limit": 2200, "note": "5-10 in caption, rest in first comment"},
    }
    rules = platform_rules.get(platform.lower(), platform_rules["tiktok"])

    # strategy = platform-capped set for direct use; all_recommended = full pool
    strategy = all_recommended[:min(count, rules["max_hashtags"])]

    return {
        "niche": niche,
        "platform": platform,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "strategy": strategy,
        "all_recommended": all_recommended,
        "by_tier": {
            "mega": base["mega"][:1],
            "large": base["large"][:2],
            "medium": base["medium"][:2],
            "niche": base["niche"][:3],
            "micro": base["micro"][:2],
        },
        "platform_rules": rules,
        "caption_template": _caption_template(niche, strategy[:rules["max_hashtags"]]),
        "rotation_tip": (
            "Rotate your niche and micro hashtags every 5-7 posts to avoid shadow limiting. "
            "Keep mega discovery tags (#fyp, #foryou) constant."
        ),
    }


def _caption_template(niche: str, hashtags: list) -> str:
    tags_str = " ".join(f"#{h}" for h in hashtags)
    return f"[Hook sentence — ask a question or make a bold claim]\n\n[1-2 sentence value delivery]\n\n[CTA: Comment, Save, or Follow]\n\n{tags_str}"


def generate_posting_schedule(
    platforms: list,
    niche: str = "general",
    posts_per_day: int = 2,
    days: int = 7,
    timezone_label: str = "EST",
) -> dict:
    """Generate a 7-day posting schedule optimized for each platform."""
    schedule = {}

    platform_times = {
        "tiktok": {
            "monday": ["06:00", "19:00", "22:00"],
            "tuesday": ["09:00", "12:00", "21:00"],
            "wednesday": ["07:00", "15:00", "23:00"],
            "thursday": ["09:00", "12:00", "19:00"],
            "friday": ["05:00", "13:00", "15:00"],
            "saturday": ["11:00", "19:00", "20:00"],
            "sunday": ["07:00", "16:00", "21:00"],
        },
        "youtube": {
            "monday": ["12:00", "20:00"],
            "tuesday": ["12:00", "20:00"],
            "wednesday": ["12:00", "21:00"],
            "thursday": ["12:00", "20:00"],
            "friday": ["12:00", "17:00"],
            "saturday": ["10:00", "20:00"],
            "sunday": ["10:00", "17:00"],
        },
        "instagram": {
            "monday": ["11:00", "14:00", "20:00"],
            "tuesday": ["09:00", "14:00", "20:00"],
            "wednesday": ["11:00", "14:00", "20:00"],
            "thursday": ["11:00", "14:00", "20:00"],
            "friday": ["11:00", "14:00"],
            "saturday": ["09:00", "19:00"],
            "sunday": ["10:00", "19:00"],
        },
    }

    days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    for platform in platforms:
        p_lower = platform.lower()
        times = platform_times.get(p_lower, platform_times["tiktok"])
        schedule[platform] = {}
        for day in days_of_week[:days]:
            day_times = times.get(day, ["12:00", "20:00"])
            schedule[platform][day] = day_times[:posts_per_day]

    return {
        "niche": niche,
        "platforms": platforms,
        "posts_per_day": posts_per_day,
        "timezone": timezone_label,
        "schedule": schedule,
        "weekly_total": sum(
            posts_per_day * 7 for _ in platforms
        ),
        "tips": [
            "Use a scheduling tool (Buffer, Later, or native schedulers) to automate posts",
            "Batch-create content 1 week ahead — shoot 14 videos in one session",
            "Check platform Analytics weekly and shift times based on your actual follower activity",
            "Repurpose each video across all platforms — shoot once, post everywhere",
        ],
    }


def generate_content_calendar(
    niche: str,
    platforms: list,
    trending_hashtags: Optional[list] = None,
    trending_sounds: Optional[list] = None,
    weeks: int = 2,
) -> dict:
    """Generate a content calendar with video ideas mapped to trends."""
    ideas = _content_ideas_for_niche(niche)
    sounds = [s["title"] for s in (trending_sounds or [])][:5] or ["Trending sound", "Original audio"]
    hashtags = generate_hashtag_strategy(niche, platforms[0] if platforms else "tiktok", 8, trending_hashtags)

    calendar = []
    idea_idx = 0
    for week in range(1, weeks + 1):
        for day_offset in range(7):
            idea = ideas[idea_idx % len(ideas)]
            sound = sounds[day_offset % len(sounds)]
            calendar.append({
                "week": week,
                "day_of_week": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][day_offset],
                "content_type": idea["type"],
                "video_idea": idea["idea"],
                "hook": idea["hook"],
                "trending_sound": sound,
                "hashtags": hashtags["strategy"],
                "cta": idea["cta"],
                "platforms": platforms,
            })
            idea_idx += 1

    return {
        "niche": niche,
        "platforms": platforms,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "weeks": weeks,
        "total_posts": len(calendar),
        "calendar": calendar,
        "hashtag_strategy": hashtags["by_tier"],
    }


def _content_ideas_for_niche(niche: str) -> list:
    base = {
        "finance": [
            {"type": "educational", "idea": "5 money mistakes to avoid in your 20s", "hook": "I wasted $10K before learning this...", "cta": "Save this for later"},
            {"type": "tutorial", "idea": "How I set up passive income in 30 days", "hook": "This changed my bank account forever", "cta": "Follow for Part 2"},
            {"type": "trending", "idea": "React to viral 'I quit my job' money story", "hook": "Did they make the right call?", "cta": "Comment your thoughts"},
            {"type": "listicle", "idea": "Top 3 apps that pay you to invest", "hook": "These apps gave me free money", "cta": "Share with someone who needs this"},
            {"type": "storytime", "idea": "How I went from $0 to $5k/month online", "hook": "Nobody told me this was possible", "cta": "Ask me anything in comments"},
            {"type": "myth-bust", "idea": "Debunking 'you need money to make money'", "hook": "This is completely FALSE and here's proof", "cta": "Drop a 🔥 if you agree"},
            {"type": "trending", "idea": "Side hustle tier list 2025", "hook": "Ranking every side hustle honestly", "cta": "Comment which one you're trying"},
        ],
        "fitness": [
            {"type": "tutorial", "idea": "5-minute morning routine that burns fat all day", "hook": "This is scientifically proven to work", "cta": "Save this for tomorrow morning"},
            {"type": "transformation", "idea": "30-day workout challenge results", "hook": "I did this for 30 days and...", "cta": "Follow to see week 1"},
            {"type": "educational", "idea": "Why you're not losing weight (real reason)", "hook": "It's not what you think", "cta": "Comment if this was eye-opening"},
            {"type": "trending", "idea": "Trying viral workout trend", "hook": "Does this actually work?", "cta": "Drop a ✅ if you want more"},
            {"type": "myth-bust", "idea": "Debunking 'no pain no gain'", "hook": "This advice is ruining your progress", "cta": "Share with your gym buddy"},
            {"type": "listicle", "idea": "3 exercises gym bros get wrong", "hook": "Stop doing these if you want to grow", "cta": "Save to fix your form"},
            {"type": "lifestyle", "idea": "Day in my life as someone who actually goes to the gym", "hook": "What 5am gym people actually look like", "cta": "Comment 🏋️ if you relate"},
        ],
        "business": [
            {"type": "educational", "idea": "How to start a business with $0", "hook": "I built 6 figures with no startup money", "cta": "Save this step-by-step"},
            {"type": "storytime", "idea": "How I got my first 1,000 customers", "hook": "This was the weirdest strategy", "cta": "Comment for a follow-up video"},
            {"type": "listicle", "idea": "5 free tools every entrepreneur needs", "hook": "Stop paying for apps you don't need", "cta": "Drop your fave tool below"},
            {"type": "myth-bust", "idea": "Why most business advice is wrong", "hook": "Gurus won't tell you this part", "cta": "Follow for the real playbook"},
            {"type": "trending", "idea": "Rating viral business ideas from Reddit", "hook": "Which one would actually work?", "cta": "Comment your best idea"},
            {"type": "tutorial", "idea": "How to write a viral ad in 10 minutes", "hook": "This framework made me $10K", "cta": "Save and try it today"},
            {"type": "educational", "idea": "Passive income vs active income — the real difference", "hook": "Most people have this backwards", "cta": "Share with your entrepreneur friend"},
        ],
    }
    default = [
        {"type": "educational", "idea": f"Top 5 things nobody tells you about {niche}", "hook": f"I wish someone told me this about {niche}", "cta": "Save this for later"},
        {"type": "tutorial", "idea": f"Beginner's guide to {niche}", "hook": f"Start here if you're new to {niche}", "cta": "Follow for more"},
        {"type": "trending", "idea": f"Reacting to viral {niche} content", "hook": f"This {niche} video broke the internet", "cta": "Comment your thoughts"},
        {"type": "listicle", "idea": f"3 mistakes beginners make in {niche}", "hook": f"Stop making mistake #2 immediately", "cta": "Share with someone who needs this"},
        {"type": "storytime", "idea": f"My {niche} journey — what I wish I knew", "hook": f"I wasted 2 years before learning this", "cta": "Ask me anything below"},
        {"type": "myth-bust", "idea": f"Biggest {niche} myths debunked", "hook": f"Everyone in {niche} has this wrong", "cta": "Drop a 🔥 if you agree"},
        {"type": "trending", "idea": f"{niche} trend tier list", "hook": f"Ranking everything honestly in {niche}", "cta": "Comment what I missed"},
    ]
    return base.get(niche.lower(), default)


def analyze_account_metrics(
    platform: str,
    followers: int,
    avg_views: int,
    avg_likes: int,
    avg_comments: int,
    post_frequency_per_week: int,
) -> dict:
    """Score an account and generate actionable optimization priorities."""
    engagement_rate = 0.0
    if avg_views > 0:
        engagement_rate = round((avg_likes + avg_comments) / avg_views * 100, 2)

    view_to_follower = round(avg_views / max(followers, 1) * 100, 2)

    score = 100
    priorities = []

    if engagement_rate < 3:
        score -= 25
        priorities.append({
            "issue": f"Low engagement rate ({engagement_rate}% — target >5%)",
            "fix": "Add a question in every caption. Reply to every comment in first 30 minutes.",
            "impact": "high",
        })

    if view_to_follower < 10:
        score -= 20
        priorities.append({
            "issue": f"Low view/follower ratio ({view_to_follower}% — target >30%)",
            "fix": "Revamp thumbnails and titles/hooks. First 3 seconds must create a pattern interrupt.",
            "impact": "high",
        })

    if post_frequency_per_week < 5 and platform.lower() == "tiktok":
        score -= 15
        priorities.append({
            "issue": f"Posting frequency too low ({post_frequency_per_week}x/week — TikTok needs 7-21x/week)",
            "fix": "Batch record 7-10 videos in one session every Sunday for the whole week.",
            "impact": "high",
        })

    if post_frequency_per_week < 3 and platform.lower() == "youtube":
        score -= 15
        priorities.append({
            "issue": f"Posting frequency low ({post_frequency_per_week}x/week — YouTube target 3-5x/week)",
            "fix": "Supplement long-form with Shorts. Shorts algorithm is separate — post them daily.",
            "impact": "medium",
        })

    growth_stage = "nano" if followers < 1_000 else \
                   "micro" if followers < 10_000 else \
                   "mid" if followers < 100_000 else \
                   "macro" if followers < 1_000_000 else "mega"

    return {
        "platform": platform,
        "metrics": {
            "followers": followers,
            "avg_views": avg_views,
            "avg_likes": avg_likes,
            "avg_comments": avg_comments,
            "engagement_rate_pct": engagement_rate,
            "view_to_follower_pct": view_to_follower,
            "post_frequency_per_week": post_frequency_per_week,
        },
        "growth_stage": growth_stage,
        "optimization_score": max(score, 0),
        "priorities": priorities,
        "monetization_readiness": _monetization_readiness(platform, followers, engagement_rate),
        "next_milestone": _next_milestone(platform, followers),
    }


def _monetization_readiness(platform: str, followers: int, engagement_rate: float) -> dict:
    thresholds = {
        "tiktok": {
            "creator_fund": 10_000,
            "creator_marketplace": 10_000,
            "live_gifts": 1_000,
            "brand_deals_minimum": 5_000,
        },
        "youtube": {
            "adsense": 1_000,  # subscribers + 4k watch hours
            "channel_memberships": 30_000,
            "super_thanks": 1_000,
            "brand_deals_minimum": 5_000,
        },
    }
    t = thresholds.get(platform.lower(), thresholds["tiktok"])
    ready = {k: followers >= v for k, v in t.items()}
    return {"thresholds": t, "currently_eligible": {k: v for k, v in ready.items() if v}}


def _next_milestone(platform: str, followers: int) -> dict:
    milestones = [1_000, 5_000, 10_000, 50_000, 100_000, 500_000, 1_000_000]
    for m in milestones:
        if followers < m:
            days_estimate = max(1, (m - followers) // 100)
            return {
                "target": m,
                "gap": m - followers,
                "estimated_days_at_100_per_day": days_estimate,
                "unlock": _milestone_unlock(platform, m),
            }
    return {"target": "10M", "gap": 10_000_000 - followers, "unlock": "Celebrity tier"}


def _milestone_unlock(platform: str, milestone: int) -> str:
    unlocks = {
        "tiktok": {
            1_000: "Live streaming enabled",
            5_000: "Creator Marketplace access",
            10_000: "Creator Fund eligible",
            50_000: "Brand deal mid-tier",
            100_000: "100K badge + major brand deals",
        },
        "youtube": {
            1_000: "YouTube Partner Program (with 4K watch hours)",
            5_000: "Mid-tier brand deals",
            10_000: "Consistent sponsorship offers",
            50_000: "Silver Play Button eligible",
            100_000: "Silver Play Button + major sponsorships",
        },
    }
    return unlocks.get(platform.lower(), {}).get(milestone, "Growth milestone")
