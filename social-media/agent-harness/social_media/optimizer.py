"""
Account optimizer — scores your posts and profile against trending signals
and generates actionable recommendations.
"""
import re
from typing import Optional


# ── Scoring helpers ──────────────────────────────────────────────────────────

def _engagement_rate(likes: int, comments: int, shares: int, followers: int) -> float:
    if followers == 0:
        return 0.0
    return ((likes + comments + shares) / followers) * 100


def _hashtag_overlap(post_tags: list[str], trending_tags: list[str]) -> float:
    post_set = {t.lower().lstrip("#") for t in post_tags}
    trend_set = {t.lower().lstrip("#") for t in trending_tags}
    if not trend_set:
        return 0.0
    return len(post_set & trend_set) / len(trend_set) * 100


# ── Bio optimizer ────────────────────────────────────────────────────────────

def optimize_bio(
    current_bio: str,
    niche: str,
    trending_hashtags: list[str],
    platform: str = "tiktok",
) -> dict:
    """
    Score and rewrite a profile bio for maximum discoverability.
    Returns score + rewrite suggestions.
    """
    issues = []
    score = 100

    # Length check
    limits = {"tiktok": 80, "youtube": 1000, "instagram": 150}
    limit = limits.get(platform, 150)
    if len(current_bio) > limit:
        issues.append(f"Bio too long ({len(current_bio)} chars). Keep under {limit}.")
        score -= 10
    if len(current_bio) < 20:
        issues.append("Bio too short — add a niche keyword and CTA.")
        score -= 15

    # CTA check
    cta_patterns = [r"follow", r"link in bio", r"check out", r"dm", r"subscribe", r"click"]
    has_cta = any(re.search(p, current_bio, re.IGNORECASE) for p in cta_patterns)
    if not has_cta:
        issues.append("Add a call-to-action (e.g. 'Follow for daily tips' or 'Link in bio').")
        score -= 10

    # Niche keyword
    if niche.lower() not in current_bio.lower():
        issues.append(f"Include your niche keyword '{niche}' in the bio.")
        score -= 10

    # Trending tag in bio (TikTok/Instagram only)
    if platform in ("tiktok", "instagram"):
        bio_tags = re.findall(r"#\w+", current_bio)
        overlap = _hashtag_overlap(bio_tags, trending_hashtags[:5])
        if overlap == 0 and trending_hashtags:
            issues.append(
                f"Add a trending hashtag to bio e.g. {trending_hashtags[0]}."
            )
            score -= 5

    # Generate rewrite suggestion
    top_tag = trending_hashtags[0] if trending_hashtags else f"#{niche}"
    rewrite = (
        f"{niche.title()} content | Daily {niche} tips & trends "
        f"| Follow for more {top_tag} | Link in bio"
    )

    return {
        "score": max(score, 0),
        "issues": issues,
        "suggested_bio": rewrite,
    }


# ── Post optimizer ───────────────────────────────────────────────────────────

def optimize_post(
    caption: str,
    hashtags: list[str],
    trending_hashtags: list[str],
    trending_music: list[dict],
    platform: str = "tiktok",
    current_likes: int = 0,
    current_comments: int = 0,
    current_shares: int = 0,
    followers: int = 1000,
) -> dict:
    """Score a post and return hashtag + caption + music recommendations."""
    score = 100
    suggestions = []

    # Caption length
    cap_limits = {"tiktok": 2200, "youtube": 5000, "instagram": 2200}
    cap_limit = cap_limits.get(platform, 2200)
    if len(caption) > cap_limit:
        suggestions.append(f"Caption over limit ({len(caption)}/{cap_limit} chars).")
        score -= 5

    # Hashtag count
    tag_targets = {"tiktok": (3, 5), "youtube": (5, 15), "instagram": (5, 10)}
    lo, hi = tag_targets.get(platform, (3, 10))
    if len(hashtags) < lo:
        suggestions.append(f"Use {lo}–{hi} hashtags. You have {len(hashtags)}.")
        score -= 15
    elif len(hashtags) > hi:
        suggestions.append(f"Too many hashtags ({len(hashtags)}). Keep to {hi} max.")
        score -= 5

    # Trending hashtag overlap
    overlap_pct = _hashtag_overlap(hashtags, [h["hashtag"] for h in trending_hashtags])
    if overlap_pct < 20:
        top5 = [h["hashtag"] for h in trending_hashtags[:5]]
        suggestions.append(f"Low trend overlap ({overlap_pct:.0f}%). Add: {', '.join(top5)}")
        score -= 20

    # Recommended hashtag set
    current_tags = {t.lower() for t in hashtags}
    recommended = []
    for h in trending_hashtags:
        if h["hashtag"].lower() not in current_tags:
            recommended.append(h["hashtag"])
        if len(recommended) >= 5:
            break
    final_hashtags = hashtags + recommended

    # Music recommendation
    music_recs = []
    for m in (trending_music or [])[:3]:
        music_recs.append({
            "title": m.get("title") or m.get("name"),
            "artist": m.get("author") or m.get("music_author"),
            "use_count": m.get("use_count"),
        })

    # Engagement rate
    er = _engagement_rate(current_likes, current_comments, current_shares, followers)
    er_benchmark = {"tiktok": 5.0, "youtube": 2.0, "instagram": 3.0}.get(platform, 3.0)
    if er < er_benchmark:
        suggestions.append(
            f"Engagement rate {er:.1f}% below {er_benchmark}% benchmark. "
            "Post at peak hours (6–9 PM local), ask a question in caption."
        )
        score -= 10

    return {
        "score": max(score, 0),
        "engagement_rate": round(er, 2),
        "suggestions": suggestions,
        "recommended_hashtags_to_add": recommended,
        "optimized_hashtags": final_hashtags[:hi],
        "trending_music_recommendations": music_recs,
    }


# ── Account health report ────────────────────────────────────────────────────

def account_health_report(
    platform: str,
    username: str,
    followers: int,
    following: int,
    total_posts: int,
    avg_views: float,
    avg_likes: float,
    avg_comments: float,
    avg_shares: float,
    niche: str,
    trending_hashtags: list[dict],
) -> dict:
    """
    Generate a full account health report with growth recommendations.
    """
    er = _engagement_rate(
        int(avg_likes), int(avg_comments), int(avg_shares), followers
    )
    ff_ratio = followers / max(following, 1)

    score = 100
    issues = []
    recommendations = []

    # Engagement benchmarks
    er_benchmarks = {"tiktok": 5.0, "youtube": 2.0, "instagram": 3.0}
    er_bench = er_benchmarks.get(platform, 3.0)
    if er < er_bench:
        score -= 20
        issues.append(f"Low engagement rate {er:.1f}% (benchmark: {er_bench}%)")
        recommendations.append("Pin your best-performing post to profile.")
        recommendations.append("Reply to every comment in first 30 min after posting.")

    # Posting frequency (assume we'd check post timestamps but use avg_views as proxy)
    if total_posts < 10:
        score -= 15
        issues.append("Not enough content — less than 10 posts.")
        recommendations.append("Post at least 1x per day to build momentum.")

    # F/F ratio
    if ff_ratio < 0.5:
        score -= 10
        issues.append(f"Following too many ({following}) vs followers ({followers}).")
        recommendations.append("Unfollow inactive accounts. Aim for F/F ratio > 1.")

    # Views vs followers
    view_ratio = avg_views / max(followers, 1)
    if view_ratio < 0.1:
        score -= 10
        issues.append("Views are low vs follower count — possible shadowban or poor hook.")
        recommendations.append(
            "Change first 3 seconds of video. Start with a bold hook/question."
        )

    # Theme page growth tactics
    growth_plays = [
        f"Use trending sounds from TikTok (top 3: {', '.join(h['hashtag'] for h in trending_hashtags[:3])}).",
        "Duet/stitch viral content in your niche to ride their algorithm wave.",
        "Post 3x/day: morning (7-9am), lunch (12-1pm), evening (7-9pm).",
        "Batch-create 7 days of content every Sunday.",
        "Reply to comments with a video reply to double your content output.",
        "Cross-post to YouTube Shorts and Instagram Reels simultaneously.",
    ]

    return {
        "platform": platform,
        "username": username,
        "health_score": max(score, 0),
        "engagement_rate": round(er, 2),
        "follower_following_ratio": round(ff_ratio, 2),
        "issues": issues,
        "recommendations": recommendations,
        "growth_playbook": growth_plays,
        "niche": niche,
    }
