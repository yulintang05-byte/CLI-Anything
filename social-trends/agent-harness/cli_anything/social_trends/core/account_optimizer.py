"""Account Optimizer — generates data-driven optimization recommendations.

Takes trending data from YouTube/TikTok and produces:
- Posting schedule recommendations
- Hashtag strategy
- Content gap analysis
- Engagement rate benchmarks
- Niche-specific growth tactics
"""

from typing import Optional

# Engagement rate benchmarks by follower tier (industry standards 2024-2025)
_YT_BENCHMARKS = {
    "nano":   {"followers": "1K–10K",   "good_er": 8.0,  "avg_er": 5.0},
    "micro":  {"followers": "10K–100K", "good_er": 5.0,  "avg_er": 3.0},
    "mid":    {"followers": "100K–1M",  "good_er": 3.0,  "avg_er": 1.5},
    "macro":  {"followers": "1M+",      "good_er": 1.5,  "avg_er": 0.8},
}

_TT_BENCHMARKS = {
    "nano":   {"followers": "1K–10K",   "good_er": 18.0, "avg_er": 10.0},
    "micro":  {"followers": "10K–100K", "good_er": 12.0, "avg_er": 7.0},
    "mid":    {"followers": "100K–1M",  "good_er": 7.0,  "avg_er": 4.0},
    "macro":  {"followers": "1M+",      "good_er": 4.0,  "avg_er": 2.0},
}

# Best posting times (UTC) by day — derived from platform analytics studies
_YT_BEST_TIMES = {
    "Monday":    ["14:00", "17:00"],
    "Tuesday":   ["14:00", "17:00"],
    "Wednesday": ["12:00", "16:00"],
    "Thursday":  ["12:00", "16:00"],
    "Friday":    ["14:00", "19:00"],
    "Saturday":  ["10:00", "14:00"],
    "Sunday":    ["10:00", "14:00"],
}

_TT_BEST_TIMES = {
    "Monday":    ["06:00", "10:00", "22:00"],
    "Tuesday":   ["02:00", "04:00", "09:00"],
    "Wednesday": ["07:00", "08:00", "23:00"],
    "Thursday":  ["09:00", "12:00", "19:00"],
    "Friday":    ["05:00", "13:00", "15:00"],
    "Saturday":  ["11:00", "19:00", "20:00"],
    "Sunday":    ["07:00", "08:00", "16:00"],
}

# Niche-specific hashtag strategies
_NICHE_HASHTAGS = {
    "finance": {
        "evergreen": ["#personalfinance", "#investing", "#money", "#financialtips", "#wealthbuilding"],
        "trending_triggers": ["#stockmarket", "#crypto", "#passiveincome", "#sidehustle"],
        "community": ["#financetok", "#moneytok", "#investingtips"],
    },
    "fitness": {
        "evergreen": ["#fitness", "#workout", "#gym", "#healthylifestyle", "#fitnessmotivation"],
        "trending_triggers": ["#weightloss", "#bodybuilding", "#homeworkout", "#transformation"],
        "community": ["#fitnesscommunity", "#gymtok", "#fitnessjourney"],
    },
    "motivation": {
        "evergreen": ["#motivation", "#mindset", "#success", "#selfimprovement", "#growthmindset"],
        "trending_triggers": ["#discipline", "#hustle", "#entrepreneurship", "#dailymotivation"],
        "community": ["#motivationtok", "#successmindset", "#selfdevelopment"],
    },
    "luxury": {
        "evergreen": ["#luxury", "#lifestyle", "#wealthy", "#richlifestyle", "#luxuryliving"],
        "trending_triggers": ["#lambo", "#mansion", "#designer", "#premiumlife"],
        "community": ["#luxurylife", "#luxurytok", "#richlife"],
    },
    "pets": {
        "evergreen": ["#pets", "#dogs", "#cats", "#animals", "#petsofinstagram"],
        "trending_triggers": ["#dogsoftiktok", "#catsoftiktok", "#funny", "#cute"],
        "community": ["#pettok", "#dogtok", "#cattok"],
    },
    "food": {
        "evergreen": ["#food", "#recipe", "#cooking", "#foodie", "#yummy"],
        "trending_triggers": ["#easyrecipe", "#mealprep", "#foodhacks", "#viral"],
        "community": ["#foodtok", "#cookingtok", "#recipeofthedaay"],
    },
    "fashion": {
        "evergreen": ["#fashion", "#ootd", "#style", "#outfitoftheday", "#fashionista"],
        "trending_triggers": ["#fashiontrends", "#outfitinspo", "#aesthetic", "#styling"],
        "community": ["#fashiontok", "#styletok", "#outfitcheck"],
    },
    "tech": {
        "evergreen": ["#tech", "#technology", "#ai", "#gadgets", "#techreview"],
        "trending_triggers": ["#artificialintelligence", "#newtech", "#techshorts", "#innovation"],
        "community": ["#techtok", "#technerds", "#techhacks"],
    },
    "gaming": {
        "evergreen": ["#gaming", "#gamer", "#videogames", "#gameplay", "#gamingcommunity"],
        "trending_triggers": ["#gamingclips", "#viral", "#fps", "#rpg"],
        "community": ["#gamingtok", "#gamersoftiktok", "#twitchclips"],
    },
    "entertainment": {
        "evergreen": ["#entertainment", "#funny", "#comedy", "#viral", "#trending"],
        "trending_triggers": ["#fyp", "#foryou", "#viral", "#trending"],
        "community": ["#entertainmenttok", "#comedytok"],
    },
}


def analyze_account(
    followers: int,
    platform: str,
    niche: str = "entertainment",
    avg_views: Optional[int] = None,
    avg_likes: Optional[int] = None,
    posts_per_week: Optional[int] = None,
) -> dict:
    """Generate optimization recommendations for an account."""
    platform = platform.lower()
    benchmarks = _YT_BENCHMARKS if platform == "youtube" else _TT_BENCHMARKS
    niche_lower = niche.lower()

    # Determine tier
    if followers < 10_000:
        tier = "nano"
    elif followers < 100_000:
        tier = "micro"
    elif followers < 1_000_000:
        tier = "mid"
    else:
        tier = "macro"

    bench = benchmarks[tier]
    best_times = _YT_BEST_TIMES if platform == "youtube" else _TT_BEST_TIMES
    hashtag_strategy = _NICHE_HASHTAGS.get(niche_lower, _NICHE_HASHTAGS["entertainment"])

    # Engagement rate calculation
    er = None
    er_rating = None
    if avg_views and avg_likes:
        er = round((avg_likes / avg_views) * 100, 2)
        if er >= bench["good_er"]:
            er_rating = "EXCELLENT"
        elif er >= bench["avg_er"]:
            er_rating = "GOOD"
        else:
            er_rating = "BELOW AVERAGE — focus on hook quality and CTAs"

    # Frequency recommendation
    freq_rec = _frequency_recommendation(platform, tier, posts_per_week)

    # Growth tactics by tier
    growth_tactics = _growth_tactics(platform, tier, niche_lower)

    return {
        "platform": platform.upper(),
        "niche": niche,
        "tier": tier,
        "follower_range": bench["followers"],
        "engagement_rate": {"current": er, "rating": er_rating, "benchmark_good": bench["good_er"],
                            "benchmark_avg": bench["avg_er"]},
        "posting_schedule": {
            "recommended_frequency": freq_rec,
            "best_times_utc": best_times,
        },
        "hashtag_strategy": {
            "evergreen": hashtag_strategy["evergreen"],
            "trending_triggers": hashtag_strategy["trending_triggers"],
            "community": hashtag_strategy["community"],
            "formula": f"3 niche + 2 trending + 2 community + 1 branded",
            "max_hashtags": 5 if platform == "youtube" else 8,
        },
        "growth_tactics": growth_tactics,
        "bio_optimization": _bio_tips(platform),
        "content_pillars": _content_pillars(niche_lower),
    }


def _frequency_recommendation(platform: str, tier: str, current: Optional[int]) -> dict:
    targets = {
        "youtube": {"nano": 2, "micro": 3, "mid": 3, "macro": 2},
        "tiktok":  {"nano": 3, "micro": 3, "mid": 2, "macro": 2},
    }
    target = targets.get(platform, targets["tiktok"])[tier]
    gap = None
    if current is not None:
        gap = target - current
    return {
        "target_per_week": target,
        "shorts_reels_per_week": target * 2 if platform == "youtube" else target,
        "current_per_week": current,
        "gap": gap,
        "note": "Consistency > quantity — same day/time builds algorithmic trust",
    }


def _growth_tactics(platform: str, tier: str, niche: str) -> list[str]:
    universal = [
        "Hook in first 1-3 seconds — state the value or shock immediately",
        "End with a direct CTA: 'Follow for more [niche] content'",
        "Reply to every comment in first 60 minutes (signals engagement to algorithm)",
        "Cross-post to both platforms — repurpose same video with platform-specific captions",
        "Use trending audio within 48-72h of it going viral for maximum boost",
        "Post 3 times in first hour of a new video going live (comment, like, share yourself)",
    ]
    platform_specific = {
        "youtube": [
            "Optimize thumbnail: high contrast, face with emotion, bold 3-word text",
            "Title formula: '[Number] [Niche] [Outcome] in [Timeframe]' e.g. '5 Stocks That DOUBLED in 2025'",
            "Add chapters/timestamps to reduce drop-off and improve search ranking",
            "YouTube Shorts strategy: repost TikTok content (remove TikTok watermark first)",
            "End screen: add subscribe button + link to your most-viewed video",
            "Cards: link to related videos at 70% video completion mark",
        ],
        "tiktok": [
            "Post between 9-11 PM local time for maximum overnight distribution",
            "Use 3-5 hashtags max — oversaturation hurts reach",
            "Duet or stitch viral videos in your niche to ride existing momentum",
            "TikTok LIVE 2x per week builds loyal community faster than posts",
            "Comment on trending posts in your niche within minutes of them being posted",
            "Use trending sound BEFORE it peaks — check 'Trending' in Creator Marketplace",
        ],
    }
    tier_specific = {
        "nano":  ["Focus on one sub-niche only — being specific > being broad at this stage",
                  "Collaborate with accounts 2-3x your size for shoutouts"],
        "micro": ["Pitch brands for gifted collabs — 10K+ qualifies for most micro-deals",
                  "Create a media kit with your engagement rate and audience demographics"],
        "mid":   ["Diversify revenue: affiliate + brand deals + digital products",
                  "Build an email list from your audience — platform independence is key"],
        "macro": ["Launch your own product line or course",
                  "Hire a content manager to maintain posting consistency at scale"],
    }
    return (
        platform_specific.get(platform, [])
        + tier_specific.get(tier, [])
        + universal[:3]
    )


def _bio_tips(platform: str) -> list[str]:
    universal = [
        "Line 1: Who you help + what outcome ('I help [audience] achieve [result]')",
        "Line 2: Social proof or credibility ('500K+ reached', '10 years in [niche]')",
        "Line 3: CTA with link ('Free [resource] ↓')",
        "Use a Linktree or single landing page — don't waste the one link slot",
    ]
    if platform == "youtube":
        return universal + [
            "Add channel keywords in About section (boosts search discovery)",
            "Pin a 'Channel Trailer' for non-subscribers — 60 seconds max, hook immediately",
        ]
    return universal + [
        "Add emojis to break up text and guide the eye",
        "Include your posting schedule ('New videos every Mon/Wed/Fri')",
    ]


def _content_pillars(niche: str) -> list[dict]:
    """Return 4 content pillars for the niche — the 4E framework."""
    generic = [
        {"pillar": "Educate", "ratio": "40%",
         "examples": ["How-to tutorials", "Myths debunked", "Step-by-step guides"]},
        {"pillar": "Entertain", "ratio": "30%",
         "examples": ["Behind the scenes", "Reactions", "Challenges/trends"]},
        {"pillar": "Inspire", "ratio": "20%",
         "examples": ["Success stories", "Transformations", "Motivational moments"]},
        {"pillar": "Engage", "ratio": "10%",
         "examples": ["Polls & questions", "Q&A sessions", "Controversial takes"]},
    ]
    return generic


def score_video_idea(title: str, niche: str, trending_hashtags: list[str]) -> dict:
    """Score a content idea for viral potential (0-100)."""
    score = 50
    signals = []

    title_lower = title.lower()

    # Emotional trigger words
    power_words = ["secret", "mistake", "never", "always", "best", "worst", "why", "how",
                   "proven", "free", "viral", "shocking", "exposed", "truth", "ultimate"]
    matches = [w for w in power_words if w in title_lower]
    if matches:
        score += min(len(matches) * 5, 20)
        signals.append(f"Power words: {', '.join(matches)}")

    # Number in title
    import re
    if re.search(r'\d+', title):
        score += 10
        signals.append("Number in title (increases CTR)")

    # Trending hashtag overlap
    niche_tags = _NICHE_HASHTAGS.get(niche.lower(), {})
    all_tags = (niche_tags.get("evergreen", []) + niche_tags.get("trending_triggers", []))
    overlap = [t for t in trending_hashtags if any(t.lstrip("#") in at.lstrip("#") for at in all_tags)]
    if overlap:
        score += min(len(overlap) * 8, 25)
        signals.append(f"Aligns with trending tags: {', '.join(overlap[:3])}")

    score = min(score, 100)
    rating = "FIRE" if score >= 80 else "GOOD" if score >= 60 else "AVERAGE" if score >= 40 else "LOW"
    return {"score": score, "rating": rating, "signals": signals,
            "suggestion": "Add a number + power word to boost CTR" if score < 60 else "Strong idea — execute quickly"}
