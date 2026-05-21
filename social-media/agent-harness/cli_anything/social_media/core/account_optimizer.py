"""Account optimization engine — scoring, bio analysis, posting schedule, and growth tips."""

import re
from datetime import datetime, timezone
from typing import Optional

# Optimal posting windows by platform (UTC hours)
OPTIMAL_HOURS = {
    "tiktok": [7, 9, 12, 17, 19, 21],
    "youtube": [14, 15, 16, 17, 18, 20],
    "instagram": [8, 11, 17, 19, 21],
}

# Ideal posting frequency per week
IDEAL_FREQUENCY = {
    "tiktok": {"min": 7, "max": 21, "sweet_spot": 14},
    "youtube": {"min": 1, "max": 5, "sweet_spot": 3},
    "instagram": {"min": 4, "max": 14, "sweet_spot": 7},
}

POWER_WORDS = [
    "viral", "trending", "secret", "proven", "shocking", "insane",
    "unbelievable", "tutorial", "hack", "tips", "how to", "best",
    "top", "ultimate", "exposed", "hidden", "free",
]

BANNED_SHADOW_WORDS = [
    "coronavirus", "covid", "suicide", "self-harm", "violence",
    "spam", "follow for follow", "f4f", "like for like",
]


def analyze_account(profile: dict) -> dict:
    """
    Score an account profile and return optimization recommendations.

    profile keys: handle, platform, bio, follower_count, following_count,
                  post_count, avg_views, avg_likes, avg_comments,
                  posting_frequency_per_week, niche, last_posts (list of dicts)
    """
    score = 0
    max_score = 100
    recommendations = []
    strengths = []

    platform = profile.get("platform", "tiktok").lower()
    bio = profile.get("bio", "")
    followers = profile.get("follower_count", 0)
    following = profile.get("following_count", 0)
    avg_views = profile.get("avg_views", 0)
    avg_likes = profile.get("avg_likes", 0)
    avg_comments = profile.get("avg_comments", 0)
    freq = profile.get("posting_frequency_per_week", 0)
    niche = profile.get("niche", "")
    last_posts = profile.get("last_posts", [])

    # --- Bio score (20 pts) ---
    bio_score, bio_recs, bio_strengths = _score_bio(bio, platform)
    score += bio_score
    recommendations.extend(bio_recs)
    strengths.extend(bio_strengths)

    # --- Engagement rate (25 pts) ---
    eng_score, eng_recs, eng_strengths = _score_engagement(
        followers, avg_views, avg_likes, avg_comments, platform
    )
    score += eng_score
    recommendations.extend(eng_recs)
    strengths.extend(eng_strengths)

    # --- Posting frequency (20 pts) ---
    freq_score, freq_recs, freq_strengths = _score_frequency(freq, platform)
    score += freq_score
    recommendations.extend(freq_recs)
    strengths.extend(freq_strengths)

    # --- Follower-to-following ratio (15 pts) ---
    ratio_score, ratio_recs, ratio_strengths = _score_ratio(followers, following)
    score += ratio_score
    recommendations.extend(ratio_recs)
    strengths.extend(ratio_strengths)

    # --- Content quality signals (20 pts) ---
    content_score, content_recs, content_strengths = _score_content(last_posts, platform)
    score += content_score
    recommendations.extend(content_recs)
    strengths.extend(content_strengths)

    grade = _score_to_grade(score)
    best_post_times = _get_best_posting_times(platform)
    ideal_freq = IDEAL_FREQUENCY.get(platform, {})
    hashtag_strategy = _hashtag_strategy(niche, platform)
    growth_hacks = _growth_hacks(platform, score, followers)

    return {
        "handle": profile.get("handle", ""),
        "platform": platform,
        "score": score,
        "max_score": max_score,
        "grade": grade,
        "strengths": strengths,
        "recommendations": recommendations,
        "best_posting_times_utc": best_post_times,
        "ideal_frequency_per_week": ideal_freq,
        "hashtag_strategy": hashtag_strategy,
        "growth_hacks": growth_hacks,
        "engagement_rate": _calc_engagement_rate(followers, avg_likes, avg_comments),
    }


def _score_bio(bio: str, platform: str) -> tuple[int, list, list]:
    score = 0
    recs = []
    strengths = []
    if not bio:
        recs.append("Add a bio — accounts with bios get 30%+ more profile visits.")
        return score, recs, strengths

    if len(bio) >= 50:
        score += 5
        strengths.append("Bio has good length.")
    else:
        recs.append(f"Expand your bio (currently {len(bio)} chars). Include your niche, value prop, and CTA.")

    has_emoji = bool(re.search(r"[\U00010000-\U0010ffff]|[☀-➿]", bio))
    if has_emoji:
        score += 3
        strengths.append("Bio uses emojis — good for visual scanning.")
    else:
        recs.append("Add 2-3 relevant emojis to your bio for visual appeal.")

    has_cta = any(kw in bio.lower() for kw in ["link", "shop", "dm", "follow", "subscribe", "click", "bio"])
    if has_cta:
        score += 5
        strengths.append("Bio has a call-to-action.")
    else:
        recs.append("Add a CTA to your bio: 'New video every day ↓' or 'DM for collabs'.")

    has_niche = len(bio.split()) >= 3
    if has_niche:
        score += 4
        strengths.append("Bio communicates your niche.")
    else:
        recs.append("Clearly state your niche in your bio so visitors know what to expect.")

    shadow = [w for w in BANNED_SHADOW_WORDS if w in bio.lower()]
    if shadow:
        recs.append(f"Remove potentially shadowbanned words from bio: {shadow}")
    else:
        score += 3

    return min(score, 20), recs, strengths


def _score_engagement(
    followers: int, avg_views: int, avg_likes: int, avg_comments: int, platform: str
) -> tuple[int, list, list]:
    score = 0
    recs = []
    strengths = []
    if followers == 0:
        recs.append("Build your initial audience by posting consistently for 30 days.")
        return score, recs, strengths

    eng_rate = _calc_engagement_rate(followers, avg_likes, avg_comments)

    # Platform benchmarks
    benchmarks = {"tiktok": 5.0, "youtube": 3.5, "instagram": 3.0}
    good_eng = benchmarks.get(platform, 4.0)

    if eng_rate >= good_eng * 1.5:
        score = 25
        strengths.append(f"Excellent engagement rate: {eng_rate:.1f}% (benchmark: {good_eng}%)")
    elif eng_rate >= good_eng:
        score = 18
        strengths.append(f"Good engagement rate: {eng_rate:.1f}%")
    elif eng_rate >= good_eng * 0.5:
        score = 10
        recs.append(
            f"Engagement rate is {eng_rate:.1f}% (benchmark: {good_eng}%). "
            "Ask questions in captions, use polls, and reply to every comment to boost it."
        )
    else:
        score = 3
        recs.append(
            f"Low engagement rate: {eng_rate:.1f}%. Focus on hook-driven content. "
            "First 3 seconds must stop the scroll. End with a question or CTA."
        )

    # View ratio for TikTok/YouTube
    if avg_views > 0 and followers > 0:
        view_ratio = avg_views / followers
        if view_ratio >= 0.3:
            strengths.append(f"Strong view-to-follower ratio: {view_ratio:.1%}")
        elif view_ratio < 0.1:
            recs.append(
                "Views per post are low relative to followers. "
                "Test different posting times and use trending sounds/hashtags."
            )

    return min(score, 25), recs, strengths


def _score_frequency(freq: float, platform: str) -> tuple[int, list, list]:
    score = 0
    recs = []
    strengths = []
    ideal = IDEAL_FREQUENCY.get(platform, {"min": 3, "max": 14, "sweet_spot": 7})

    if freq == 0:
        recs.append(f"Start posting! Aim for {ideal['sweet_spot']}x/week on {platform}.")
        return score, recs, strengths

    if ideal["min"] <= freq <= ideal["max"]:
        score = 20
        strengths.append(f"Posting frequency ({freq:.1f}x/week) is in the ideal range.")
    elif freq < ideal["min"]:
        score = 8
        recs.append(
            f"Post more frequently. You're at {freq:.1f}x/week; "
            f"aim for {ideal['sweet_spot']}x/week to grow faster on {platform}."
        )
    else:
        score = 14
        recs.append(
            f"Posting very frequently ({freq:.1f}x/week). "
            "Maintain quality over quantity — one great post beats three mediocre ones."
        )

    return min(score, 20), recs, strengths


def _score_ratio(followers: int, following: int) -> tuple[int, list, list]:
    score = 0
    recs = []
    strengths = []

    if following == 0:
        score = 15
        strengths.append("Clean following ratio.")
        return score, recs, strengths

    ratio = followers / following if following > 0 else followers

    if ratio >= 10:
        score = 15
        strengths.append(f"Excellent follower/following ratio: {ratio:.0f}:1")
    elif ratio >= 3:
        score = 10
        strengths.append(f"Good follower/following ratio: {ratio:.1f}:1")
    elif ratio >= 1:
        score = 6
        recs.append(
            f"Follower/following ratio is {ratio:.1f}:1. "
            "Unfollow inactive or irrelevant accounts to improve credibility."
        )
    else:
        score = 2
        recs.append(
            f"You follow more people than follow you ({following} following, {followers} followers). "
            "This hurts credibility. Unfollow non-reciprocal accounts."
        )

    return min(score, 15), recs, strengths


def _score_content(posts: list[dict], platform: str) -> tuple[int, list, list]:
    score = 0
    recs = []
    strengths = []

    if not posts:
        recs.append("Provide recent post data for content analysis.")
        return 10, recs, strengths  # Neutral score when no data

    titles = [p.get("title", p.get("description", "")) for p in posts]

    # Check for power words
    power_hits = sum(
        1 for t in titles
        if any(pw in t.lower() for pw in POWER_WORDS)
    )
    power_ratio = power_hits / len(titles) if titles else 0

    if power_ratio >= 0.5:
        score += 8
        strengths.append(f"{power_hits}/{len(titles)} posts use engagement-driving words.")
    elif power_ratio >= 0.25:
        score += 4
        recs.append("Use more power words in titles/descriptions: 'viral', 'secret', 'how to', 'tips'.")
    else:
        recs.append(
            "Your titles/captions lack hooks. Start with curiosity gaps: "
            "'The secret most [niche] creators don't tell you...'"
        )

    # Check hashtag usage
    avg_hashtags = sum(len(p.get("hashtags", [])) for p in posts) / len(posts)
    if platform == "tiktok":
        if 3 <= avg_hashtags <= 8:
            score += 6
            strengths.append(f"Good hashtag count (avg {avg_hashtags:.1f} per post).")
        elif avg_hashtags < 3:
            recs.append("Add 3-8 relevant hashtags per TikTok post (mix trending + niche).")
            score += 2
        else:
            recs.append("Too many hashtags per post. Stick to 3-8 highly relevant ones.")
            score += 3
    elif platform == "youtube":
        if avg_hashtags >= 3:
            score += 6
        else:
            recs.append("Add 3-5 hashtags to YouTube video descriptions for discoverability.")
            score += 2

    # Consistency check
    score += 6  # Bonus for having posts at all
    strengths.append("Content exists — consistency is key.")

    return min(score, 20), recs, strengths


def _calc_engagement_rate(followers: int, avg_likes: int, avg_comments: int) -> float:
    if followers == 0:
        return 0.0
    return round(((avg_likes + avg_comments) / followers) * 100, 2)


def _score_to_grade(score: int) -> str:
    if score >= 85:
        return "A+"
    elif score >= 75:
        return "A"
    elif score >= 65:
        return "B+"
    elif score >= 55:
        return "B"
    elif score >= 45:
        return "C+"
    elif score >= 35:
        return "C"
    return "D"


def _get_best_posting_times(platform: str) -> list[str]:
    hours = OPTIMAL_HOURS.get(platform.lower(), [9, 12, 17, 20])
    return [f"{h:02d}:00 UTC" for h in hours]


def _hashtag_strategy(niche: str, platform: str) -> dict:
    strategies = {
        "tiktok": {
            "formula": "2 mega (1M+) + 3 mid (100K-1M) + 3 niche (<100K) per post",
            "avoid": "#fyp #foryou #foryoupage alone (too broad, no targeting)",
            "tips": [
                "Always include 1-2 trending hashtags from the Discover page.",
                f"Use niche-specific tags like #{niche.replace(' ', '').lower()} if applicable.",
                "Rotate hashtag sets — don't use the same set every post.",
                "Put hashtags in the caption, not comments (TikTok ranks them differently).",
            ],
        },
        "youtube": {
            "formula": "3-5 hashtags in description, first 3 appear above title",
            "avoid": "Misleading hashtags that don't match content (YouTube penalizes this)",
            "tips": [
                "First hashtag = your main keyword.",
                "Include your channel name as a hashtag for brand discoverability.",
                f"Use #{niche.replace(' ', '').lower()} as a consistent branded hashtag.",
                "Research competitors' hashtags with YouTube Studio.",
            ],
        },
        "instagram": {
            "formula": "5-15 hashtags: mix of sizes (avoid only mega-hashtags)",
            "avoid": "Banned hashtags — check before using niche tags.",
            "tips": [
                "Use a content pillar hashtag strategy: 30% mega, 40% mid, 30% micro.",
                "Create a branded hashtag and encourage followers to use it.",
                "Hide hashtags in first comment to keep captions clean.",
            ],
        },
    }
    return strategies.get(platform.lower(), strategies["tiktok"])


def _growth_hacks(platform: str, score: int, followers: int) -> list[str]:
    hacks = []

    if platform == "tiktok":
        hacks = [
            "Stitch/Duet trending videos in your niche — these get extra reach from the original's audience.",
            "Post within 2 hours of a trending sound going viral — early adoption gets algorithmic push.",
            "Reply to comments with VIDEO replies — they get additional distribution.",
            "Post at least 1 video/day for 30 days straight to trigger TikTok's growth algorithm.",
            "Use the 'viral thumbnail' trick: pause-worthy first frame with text overlay.",
            "Cross-post your TikToks to YouTube Shorts and Instagram Reels — triple exposure.",
        ]
    elif platform == "youtube":
        hacks = [
            "Publish within 2 hours of peak search time for your keyword (use Google Trends).",
            "Create 'topic cluster' playlists — group related videos to increase session time.",
            "Use 'open loop' hooks: state a problem at start, delay the solution by 30+ seconds.",
            "Add chapters to all videos — boosts average view duration and search rankings.",
            "Optimize thumbnails with faces showing extreme emotion + bold 3-word text.",
            "Collab with channels 10-20% smaller than yours for mutual audience sharing.",
        ]

    if followers < 1000:
        hacks.insert(0, "Focus on consistency over virality at this stage — post daily for 60 days.")
    elif followers < 10000:
        hacks.insert(0, "Engage with 10 accounts in your niche every day — genuine comments, not 'nice post'.")
    else:
        hacks.insert(0, "Leverage your existing audience: pin a call-to-action comment and create a community post.")

    return hacks[:8]


def batch_analyze_accounts(profiles: list[dict]) -> list[dict]:
    """Analyze multiple accounts and return sorted by score."""
    results = [analyze_account(p) for p in profiles]
    return sorted(results, key=lambda r: r["score"], reverse=True)
