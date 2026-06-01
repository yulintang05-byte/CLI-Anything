#!/usr/bin/env python3
"""Account optimizer — generates data-driven improvement recommendations."""

from datetime import datetime
from typing import Optional


BEST_POST_TIMES = {
    "tiktok": {
        "Mon": ["6-10am", "7-9pm"],
        "Tue": ["2-9am", "4pm", "9pm"],
        "Wed": ["7-8am", "11pm"],
        "Thu": ["9am", "12pm", "7pm"],
        "Fri": ["5am", "1-3pm"],
        "Sat": ["11am", "7-8pm"],
        "Sun": ["7-8am", "4pm"],
    },
    "youtube": {
        "Mon": ["2-4pm"],
        "Tue": ["2-4pm"],
        "Wed": ["2-4pm"],
        "Thu": ["12-3pm"],
        "Fri": ["12-3pm"],
        "Sat": ["9-11am"],
        "Sun": ["9-11am"],
    },
}

IDEAL_POSTING_FREQUENCY = {
    "tiktok": {"min_per_day": 1, "max_per_day": 4, "ideal_per_day": 2},
    "youtube_shorts": {"min_per_week": 3, "max_per_week": 7, "ideal_per_week": 5},
    "youtube_long": {"min_per_week": 1, "max_per_week": 3, "ideal_per_week": 2},
    "instagram_reels": {"min_per_week": 3, "max_per_week": 7, "ideal_per_week": 4},
}

BIO_KEYWORDS_BY_NICHE = {
    "fitness": ["transform", "coach", "results", "free workout", "dm for coaching"],
    "finance": ["free guide", "make money", "passive income", "financial freedom", "link below"],
    "fashion": ["daily outfits", "style tips", "shop my look", "link in bio"],
    "food": ["recipes", "easy meals", "cook with me", "new video daily"],
    "gaming": ["daily streams", "clips", "collab open", "join discord"],
    "motivation": ["daily mindset", "level up", "free ebook", "dm for mentorship"],
    "tech": ["reviews", "tutorials", "honest takes", "new drops"],
    "beauty": ["tutorials", "product reviews", "collab", "dm for gifting"],
}


def audit_account_profile(
    username: str,
    platform: str,
    bio: str,
    follower_count: int,
    following_count: int,
    post_count: int,
    avg_views: int,
    avg_likes: int,
    avg_comments: int,
    niche: str = "",
    profile_has_link: bool = True,
) -> dict:
    """Audit an account profile and return optimization recommendations."""
    issues = []
    wins = []
    score = 0

    # Engagement rate
    if follower_count > 0:
        eng_rate = (avg_likes + avg_comments) / follower_count * 100
    else:
        eng_rate = 0

    if eng_rate >= 5:
        wins.append(f"Strong engagement rate: {eng_rate:.1f}% (industry avg: 2-5%)")
        score += 25
    elif eng_rate >= 2:
        issues.append(f"Engagement rate {eng_rate:.1f}% is average — boost with CTAs in every post")
        score += 12
    else:
        issues.append(f"Low engagement rate {eng_rate:.1f}% — prioritize reply-baiting and question CTAs")

    # Following/follower ratio
    if following_count > 0:
        ratio = follower_count / following_count
        if ratio >= 5:
            wins.append(f"Excellent follower/following ratio: {ratio:.1f}x")
            score += 15
        elif ratio >= 1:
            issues.append(f"Follow ratio {ratio:.1f}x — unfollow inactive/irrelevant accounts to improve authority signals")
            score += 5
        else:
            issues.append("Following more than followers — mass unfollow non-reciprocal accounts ASAP")

    # Bio quality
    bio_len = len(bio)
    if bio_len == 0:
        issues.append("Empty bio — add a clear value proposition + CTA + link")
    elif bio_len < 50:
        issues.append("Bio too short — add niche keywords, a hook, and a CTA (aim for 100-150 chars)")
        score += 5
    elif bio_len <= 150:
        wins.append("Bio length is good")
        score += 15
    else:
        issues.append("Bio may be too long on mobile — trim to 150 chars max")
        score += 8

    # Bio keywords check
    if niche and niche.lower() in BIO_KEYWORDS_BY_NICHE:
        kws = BIO_KEYWORDS_BY_NICHE[niche.lower()]
        found = [k for k in kws if k.lower() in bio.lower()]
        if len(found) >= 2:
            wins.append(f"Bio contains strong niche keywords: {found}")
            score += 10
        else:
            issues.append(f"Add power words to bio for {niche}: {kws[:3]}")

    # Link in bio
    if not profile_has_link:
        issues.append("MISSING link in bio — every account MUST have a link (Linktree, Beacons, or direct)")
    else:
        wins.append("Has link in bio")
        score += 10

    # View/follower rate
    if follower_count > 0 and avg_views > 0:
        vfr = avg_views / follower_count * 100
        if vfr >= 20:
            wins.append(f"High view/follower rate: {vfr:.0f}% — algorithm is pushing content")
            score += 15
        elif vfr >= 5:
            score += 8
        else:
            issues.append(f"Low view/follower rate {vfr:.1f}% — experiment with trending audio and new hook formats")

    # Posting cadence guess
    if post_count < 10:
        issues.append("Very few posts — post at least 30 times before analyzing performance")
    elif post_count >= 50:
        wins.append(f"Consistent posting history: {post_count} posts")
        score += 10

    return {
        "username": username,
        "platform": platform,
        "overall_score": min(score, 100),
        "grade": _score_to_grade(min(score, 100)),
        "engagement_rate_pct": round(eng_rate, 2),
        "wins": wins,
        "issues_to_fix": issues,
        "priority_actions": _build_priority_actions(issues),
        "posting_schedule": BEST_POST_TIMES.get(platform.lower(), {}),
        "ideal_frequency": IDEAL_POSTING_FREQUENCY.get(platform.lower(), {}),
    }


def generate_content_calendar(
    platform: str,
    niche: str,
    trending_hashtags: list[dict],
    trending_topics: list[dict],
    days: int = 7,
) -> list[dict]:
    """Generate a 7-day content calendar based on current trends."""
    top_tags = [h["hashtag"] for h in trending_hashtags[:12]]
    top_topics = [t["topic"] for t in trending_topics[:10]]
    freq = IDEAL_POSTING_FREQUENCY.get(platform.lower(), {})
    posts_per_day = freq.get("ideal_per_day", 1)

    calendar = []
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for day_idx in range(days):
        day_name = day_names[day_idx % 7]
        best_times = BEST_POST_TIMES.get(platform.lower(), {}).get(day_name[:3], ["12pm"])
        for post_num in range(posts_per_day):
            topic_idx = (day_idx * posts_per_day + post_num) % max(len(top_topics), 1)
            tag_start = (day_idx * 3) % max(len(top_tags), 1)
            post_tags = top_tags[tag_start: tag_start + 5]
            if len(post_tags) < 5 and top_tags:
                post_tags += top_tags[: 5 - len(post_tags)]

            calendar.append(
                {
                    "day": day_name,
                    "post_number": post_num + 1,
                    "suggested_time": best_times[post_num % len(best_times)],
                    "content_angle": _get_content_angle(niche, top_topics[topic_idx] if top_topics else niche),
                    "hook_idea": _get_hook(niche, top_topics[topic_idx] if top_topics else "this"),
                    "hashtags": post_tags,
                    "cta": _get_cta(platform, niche),
                }
            )
    return calendar


def generate_bio_templates(niche: str, platform: str, cta_url: str = "") -> list[str]:
    """Generate optimized bio templates for a niche."""
    kws = BIO_KEYWORDS_BY_NICHE.get(niche.lower(), ["tips", "daily content", "follow for more"])
    link_part = f"\n🔗 {cta_url}" if cta_url else "\n🔗 Link in bio"
    templates = [
        f"Daily {niche} content | {kws[0].title()} | {kws[1].title() if len(kws) > 1 else ''}{link_part}",
        f"🚀 {niche.title()} tips that actually work\n💡 {kws[0].title()}\n📩 DM to collab{link_part}",
        f"Helping you master {niche} 🔥\n{kws[0].title()} • {kws[1].title() if len(kws) > 1 else 'Daily posts'}{link_part}",
    ]
    return templates


def _score_to_grade(score: int) -> str:
    if score >= 85:
        return "A - Excellent"
    if score >= 70:
        return "B - Good"
    if score >= 55:
        return "C - Average"
    if score >= 40:
        return "D - Needs Work"
    return "F - Critical Issues"


def _build_priority_actions(issues: list[str]) -> list[str]:
    # Put link-in-bio and bio issues first, they have biggest ROI
    priority = []
    rest = []
    for issue in issues:
        if any(kw in issue.lower() for kw in ["link", "bio", "engagement"]):
            priority.append(issue)
        else:
            rest.append(issue)
    return (priority + rest)[:5]


def _get_content_angle(niche: str, topic: str) -> str:
    angles = [
        f"How {topic} is changing {niche} (educational)",
        f"5 {niche} mistakes that are costing you (listicle)",
        f"My honest take on {topic} in {niche} (opinion)",
        f"Step-by-step {niche} tutorial using {topic} (tutorial)",
        f"Reacting to viral {topic} trend in {niche} (reaction)",
        f"{topic.title()} proof that {niche} works (proof/case study)",
    ]
    return angles[hash(topic) % len(angles)]


def _get_hook(niche: str, topic: str) -> str:
    hooks = [
        f"POV: You just discovered the {topic} secret in {niche}...",
        f"Stop making this {topic} mistake in {niche}",
        f"Nobody in {niche} is talking about {topic} (but they should be)",
        f"I tried {topic} for 30 days in {niche} — here's what happened",
        f"The {topic} strategy that grew my {niche} account 10x",
    ]
    return hooks[hash(topic + niche) % len(hooks)]


def _get_cta(platform: str, niche: str) -> str:
    ctas = {
        "tiktok": [
            f"Follow for daily {niche} tips",
            "Save this + share with someone who needs it",
            "Comment your biggest question below",
            "Duet this with your results",
        ],
        "youtube": [
            "Subscribe for weekly videos",
            "Like + comment your biggest takeaway",
            "Watch the next video in the series",
            "Join the free community — link in description",
        ],
    }
    options = ctas.get(platform.lower(), ctas["tiktok"])
    return options[hash(niche) % len(options)]
