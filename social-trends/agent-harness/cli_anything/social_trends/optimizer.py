"""Account optimization engine — audits and improvement recommendations."""
from __future__ import annotations
from typing import Any
import re


# ── Scoring weights ────────────────────────────────────────────────────────────

_PLATFORM_BEST_PRACTICES: dict[str, dict] = {
    "tiktok": {
        "bio_max_chars": 80,
        "username_max": 24,
        "posting_frequency": "1-4 times/day",
        "peak_times": ["7-9am", "12-3pm", "7-11pm"],
        "ideal_video_length": "15-60 seconds (sweet spot: 21-34s)",
        "caption_max": 150,
        "hashtag_count": "3-5 niche + 1-2 broad",
        "hashtag_strategy": "Mix niche (100K-1M), mid (1M-10M), viral (10M+) tags",
        "hook_window": "First 1-3 seconds must hook viewer",
        "cta": "Always end with a call-to-action (comment, share, follow)",
        "trending_audio": "Use trending sounds in first 72 hours of trend emergence",
        "duet_stitch": "Enable duet/stitch for maximum reach",
        "profile_pic": "Clear face or brand logo, high contrast",
    },
    "youtube": {
        "bio_max_chars": 1000,
        "shorts_length": "Under 60 seconds for Shorts, 60% of traffic",
        "posting_frequency": "2-4 times/week minimum",
        "peak_times": ["2-4pm", "8-11pm weekdays", "9am-11am weekends"],
        "thumbnail_rule": "High contrast, expressive face, bold text (3 words max)",
        "title_max": 60,
        "description_seo": "First 150 chars are preview — pack keywords there",
        "hashtag_count": "3-5 in description",
        "chapters": "Add timestamps for videos > 5 min",
        "end_screen": "Always add end screen at 20-25s from end",
        "cards": "Add cards at 20% and 70% of video duration",
        "shorts_hook": "First frame must be compelling — no black screens",
    },
    "instagram": {
        "bio_max_chars": 150,
        "posting_frequency": "3-5x/week feed, 5-7 stories/day",
        "reels_length": "7-15 seconds optimal, max 90s",
        "hashtag_count": "5-10 (Instagram algo change 2023)",
        "caption_length": "Under 125 chars show without cut-off",
        "peak_times": ["6-9am", "12-2pm", "5-8pm"],
        "story_engagement": "Use polls/questions/countdowns to boost reach",
        "reel_cover": "Always set a custom cover frame",
        "collab": "Use collab feature — posts appear on both accounts",
    },
    "x_twitter": {
        "bio_max_chars": 160,
        "tweet_max": 280,
        "posting_frequency": "3-6 tweets/day for growth",
        "peak_times": ["8-10am", "12-1pm", "6-9pm"],
        "thread_strategy": "First tweet is the hook — don't reveal punchline",
        "hashtag_count": "1-2 max",
        "media": "Tweets with video get 10x more engagement",
        "reply_farming": "Reply to viral tweets in your niche within first 30 min",
    },
}

_NICHE_HASHTAG_SETS: dict[str, list[str]] = {
    "fitness": ["#fitness", "#gym", "#workout", "#fitlife", "#health", "#bodybuilding", "#personaltrainer", "#fitnessmotivation"],
    "food": ["#food", "#foodie", "#cooking", "#recipe", "#foodphotography", "#foodblogger", "#homecooking", "#foodlover"],
    "fashion": ["#fashion", "#style", "#ootd", "#outfitoftheday", "#streetwear", "#streetstyle", "#fashionblogger", "#trending"],
    "finance": ["#finance", "#money", "#investing", "#stockmarket", "#crypto", "#personalfinance", "#financetips", "#wealth"],
    "motivation": ["#motivation", "#mindset", "#success", "#hustle", "#entrepreneur", "#grindset", "#selfimprovement", "#dailymotivation"],
    "beauty": ["#beauty", "#makeup", "#skincare", "#glam", "#beautytips", "#makeuptutorial", "#skincareroutine", "#grwm"],
    "travel": ["#travel", "#wanderlust", "#travelgram", "#explore", "#adventure", "#travelblogger", "#vacation", "#traveling"],
    "gaming": ["#gaming", "#gamer", "#twitch", "#youtube", "#ps5", "#xbox", "#pcgaming", "#esports"],
    "pets": ["#pets", "#dog", "#cat", "#dogsofinstagram", "#catsoftiktok", "#petlife", "#animals", "#cutepets"],
    "comedy": ["#comedy", "#funny", "#humor", "#memes", "#viral", "#trending", "#lol", "#relatable"],
}


def generate_account_audit(
    platform: str,
    username: str,
    niche: str = "",
    current_followers: int = 0,
    avg_views: int = 0,
    avg_likes: int = 0,
    bio: str = "",
    posting_frequency: str = "",
    current_hashtags: list[str] | None = None,
) -> dict[str, Any]:
    """
    Generate a structured account audit with scoring and recommendations.
    """
    platform_key = platform.lower().replace(" ", "_").replace("-", "_")
    bp = _PLATFORM_BEST_PRACTICES.get(platform_key, {})
    current_hashtags = current_hashtags or []

    issues: list[dict] = []
    wins: list[str] = []
    score = 100

    # Bio check
    if bio:
        bio_max = bp.get("bio_max_chars", 150)
        if len(bio) > bio_max:
            issues.append({"field": "bio", "severity": "medium", "issue": f"Bio too long ({len(bio)} chars, max {bio_max})", "fix": f"Trim to {bio_max} chars. Lead with your value prop."})
            score -= 5
        if not any(kw in bio.lower() for kw in ["follow", "link", "shop", "dm", "contact", "subscribe", "|", "↓", "👇"]):
            issues.append({"field": "bio", "severity": "low", "issue": "Bio lacks a CTA", "fix": "Add 'Follow for daily tips' or 'Link in bio' to drive action."})
            score -= 3
        else:
            wins.append("Bio has a CTA")
    else:
        issues.append({"field": "bio", "severity": "high", "issue": "No bio provided — cannot audit", "fix": "Fill out your bio completely."})
        score -= 10

    # Engagement rate
    if current_followers > 0 and avg_likes > 0:
        eng_rate = (avg_likes / current_followers) * 100
        if eng_rate < 1.0:
            issues.append({"field": "engagement", "severity": "high", "issue": f"Low engagement rate: {eng_rate:.2f}% (good = 3-6%)", "fix": "Post more question-based captions. Reply to every comment in first hour. Use polls/challenges."})
            score -= 20
        elif eng_rate < 3.0:
            issues.append({"field": "engagement", "severity": "medium", "issue": f"Below-average engagement: {eng_rate:.2f}%", "fix": "Run a giveaway or challenge to spike engagement. Engage with similar accounts."})
            score -= 10
        else:
            wins.append(f"Healthy engagement rate: {eng_rate:.2f}%")

    # Views vs followers
    if current_followers > 0 and avg_views > 0:
        view_ratio = avg_views / current_followers
        if view_ratio < 0.1:
            issues.append({"field": "reach", "severity": "high", "issue": f"Views ({avg_views:,}) = {view_ratio:.1%} of followers — very low organic reach", "fix": "Your content isn't triggering the algorithm. Try trending audio, new hook styles, and post at peak times."})
            score -= 15

    # Hashtag audit
    if current_hashtags:
        ideal = bp.get("hashtag_count", "3-5")
        h_count = len(current_hashtags)
        if platform_key == "tiktok" and h_count > 8:
            issues.append({"field": "hashtags", "severity": "medium", "issue": f"Too many hashtags ({h_count}). TikTok prefers 3-5.", "fix": "Use 2 niche + 2 mid-range + 1 broad hashtag."})
            score -= 5
        elif platform_key == "instagram" and h_count > 15:
            issues.append({"field": "hashtags", "severity": "medium", "issue": f"{h_count} hashtags is spammy on Instagram post-2023", "fix": "Cut to 5-10 targeted hashtags. Mix sizes."})
            score -= 5
    else:
        issues.append({"field": "hashtags", "severity": "high", "issue": "No hashtags detected", "fix": f"Add {bp.get('hashtag_count', '3-5')} strategic hashtags per post."})
        score -= 15

    # Posting frequency
    if not posting_frequency:
        issues.append({"field": "consistency", "severity": "medium", "issue": "Posting frequency unknown", "fix": f"Aim for {bp.get('posting_frequency', '3-5x/week')} consistently."})
        score -= 5

    # Niche hashtag recommendations
    niche_tags = _recommend_hashtags(niche, platform_key)

    score = max(0, min(100, score))
    grade = _score_to_grade(score)

    return {
        "platform": platform,
        "username": username,
        "niche": niche or "unspecified",
        "score": score,
        "grade": grade,
        "wins": wins,
        "issues": sorted(issues, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["severity"]]),
        "best_practices": bp,
        "recommended_hashtags": niche_tags,
        "action_plan": _build_action_plan(issues, platform_key, niche, bp),
    }


def optimize_profile(
    platform: str,
    niche: str,
    current_bio: str = "",
    username: str = "",
) -> dict[str, Any]:
    """Generate an optimized bio, username tips, and content calendar skeleton."""
    platform_key = platform.lower().replace(" ", "_")
    bp = _PLATFORM_BEST_PRACTICES.get(platform_key, {})
    niche_tags = _recommend_hashtags(niche, platform_key)

    bio_formula = _bio_formula(platform_key, niche, current_bio)
    content_calendar = _content_calendar(platform_key)
    hook_templates = _hook_templates(niche)

    return {
        "platform": platform,
        "niche": niche,
        "optimized_bio": bio_formula,
        "username_tips": _username_tips(platform_key),
        "hashtag_stack": niche_tags,
        "content_calendar_skeleton": content_calendar,
        "hook_templates": hook_templates,
        "peak_posting_times": bp.get("peak_times", []),
        "posting_frequency": bp.get("posting_frequency", ""),
    }


def _recommend_hashtags(niche: str, platform: str) -> dict[str, list[str]]:
    niche_lower = niche.lower()
    matched_niche = "motivation"
    for key in _NICHE_HASHTAG_SETS:
        if key in niche_lower or niche_lower in key:
            matched_niche = key
            break

    tags = _NICHE_HASHTAG_SETS.get(matched_niche, _NICHE_HASHTAG_SETS["motivation"])
    broad = ["#viral", "#trending", "#fyp", "#foryou", "#explore"]
    if platform == "youtube":
        broad = ["#shorts", "#youtube", "#trending"]

    return {
        "niche_tags": tags[:5],
        "broad_tags": broad[:3],
        "strategy": f"Use {tags[0]}, {tags[1]} (niche), {broad[0]} (reach booster)",
    }


def _bio_formula(platform: str, niche: str, current: str) -> dict[str, str]:
    templates = {
        "tiktok": f"[Hook line about {niche}] 🔥\n[Who you help / what you do]\n[CTA: Follow for daily {niche} tips] 👇",
        "youtube": f"[Channel about {niche}]\n[Upload schedule, e.g. 'New videos every Tuesday']\n[Credentials / Social proof]\n[Link in bio CTA]",
        "instagram": f"[Role/Identity] | [{niche} content]\n[Value prop in 1 line]\n👇 [CTA with link]",
        "x_twitter": f"[Bold claim about {niche}] | [Credibility signal] | [CTA]",
    }
    template = templates.get(platform, templates["instagram"])
    return {
        "template": template,
        "current": current,
        "tips": [
            "Lead with WHO you help, not just what you do",
            "Add emojis as bullet separators, not decoration",
            "Include a keyword your audience searches",
            f"End with a single clear CTA",
        ],
    }


def _username_tips(platform: str) -> list[str]:
    return [
        "Keep it under 20 characters — memorable and typed-friendly",
        "Use your niche keyword if available (e.g. @fitwithjohn, @cookingwithsara)",
        "Avoid numbers/underscores unless it's your brand",
        "Match your username across ALL platforms for SEO",
        "No hyphens — hard to say out loud in shoutouts",
    ]


def _content_calendar(platform: str) -> list[dict[str, str]]:
    calendars = {
        "tiktok": [
            {"slot": "Monday", "type": "Educational", "hook": "POV: You didn't know this about [niche]"},
            {"slot": "Tuesday", "type": "Trending Audio", "hook": "Use top trending sound + [niche] twist"},
            {"slot": "Wednesday", "type": "Story/Personal", "hook": "My honest take on [controversial niche topic]"},
            {"slot": "Thursday", "type": "Tutorial", "hook": "I tested [X] so you don't have to"},
            {"slot": "Friday", "type": "Trend Duet/Stitch", "hook": "React to viral [niche] video"},
            {"slot": "Saturday", "type": "Behind the Scenes", "hook": "A day in my life as a [niche]"},
            {"slot": "Sunday", "type": "Engagement Bait", "hook": "Comment your [niche] question and I'll answer"},
        ],
        "youtube": [
            {"slot": "Tuesday", "type": "Shorts (trending)", "hook": "30-sec [niche] tip everyone gets wrong"},
            {"slot": "Thursday", "type": "Long-form Tutorial", "hook": "Complete guide to [niche topic] in [timeframe]"},
            {"slot": "Saturday", "type": "Shorts (entertaining)", "hook": "Watch me [challenge/experiment in niche]"},
        ],
        "instagram": [
            {"slot": "Mon/Wed/Fri", "type": "Reels", "hook": "Hook in first frame, trending audio"},
            {"slot": "Daily", "type": "Stories", "hook": "Poll + question box for engagement"},
            {"slot": "Tuesday", "type": "Carousel", "hook": "'Swipe to see [transformation/list/tips]'"},
        ],
    }
    return calendars.get(platform, calendars["tiktok"])


def _hook_templates(niche: str) -> list[str]:
    return [
        f"POV: You're finally learning the truth about {niche}",
        f"Nobody talks about this {niche} secret...",
        f"I tested [X {niche} thing] for 30 days — here's what happened",
        f"Stop doing this if you're into {niche}",
        f"The {niche} hack that changed everything for me",
        f"Things I wish I knew before starting {niche}",
        f"This {niche} mistake is killing your results",
        f"Rate my {niche} [item/routine/setup] 1-10",
        f"Tell me you're obsessed with {niche} without telling me",
        f"Replying to @[commenter]: the truth about {niche}",
    ]


def _build_action_plan(issues: list[dict], platform: str, niche: str, bp: dict) -> list[str]:
    plan: list[str] = []

    high_issues = [i for i in issues if i["severity"] == "high"]
    for issue in high_issues[:3]:
        plan.append(f"URGENT: {issue['fix']}")

    plan.append(f"Post at {bp.get('peak_times', ['12pm'])[0]} daily for the next 2 weeks")
    plan.append(f"Research 3 viral videos in your {niche} niche — identify their hook format")
    plan.append("Spend 30 min/day engaging with accounts in your niche (genuine comments)")
    plan.append("Use one trending sound per day on TikTok/Reels")

    return plan


def _score_to_grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"
