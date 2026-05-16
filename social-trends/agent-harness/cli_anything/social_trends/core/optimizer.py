"""Account optimization engine — scores and recommends improvements.

Works with pre-fetched audit data (no live API calls) so agents can
run it offline after fetching account data.
"""

from typing import Any

PLATFORM_BEST_PRACTICES = {
    "youtube": {
        "post_frequency":    "1–2 videos/week",
        "ideal_length":      "8–15 min (Shorts: 15–60 sec)",
        "peak_times":        "Thu–Sat 2–4 PM local time",
        "title_length":      "60–70 characters",
        "description_length": "200–500 characters with 3–5 keywords",
        "thumbnail":         "High-contrast face/text, 1280×720",
        "hashtags_per_post": "3–5 relevant hashtags in description",
        "cta_placement":     "First 30 seconds + end screen",
        "chapters":          "Add timestamps every 2–3 minutes",
        "end_screen":        "Subscribe + 1–2 video recommendations",
    },
    "tiktok": {
        "post_frequency":    "1–4 videos/day",
        "ideal_length":      "21–34 sec (sweet spot), up to 3 min",
        "peak_times":        "6–10 AM and 7–11 PM local time",
        "caption_length":    "100–150 characters + hashtags",
        "hashtags_per_post": "3–5 (mix niche + trending + broad)",
        "hook_window":       "First 1–3 seconds must be the hook",
        "trending_audio":    "Use trending sounds for +30% reach",
        "duet_stitch":       "Enable both for collaboration reach",
        "text_overlay":      "Add captions — 85% watch without sound",
        "loop_design":       "Engineer videos to loop seamlessly",
    },
    "instagram": {
        "post_frequency":    "3–5 Reels/week + 1–2 feed posts",
        "ideal_length":      "Reels: 15–30 sec; carousel: 5–10 slides",
        "peak_times":        "Mon–Fri 9 AM, 12 PM, 5 PM",
        "caption_length":    "138–150 characters (first line before fold)",
        "hashtags_per_post": "5–10 niche hashtags",
        "story_frequency":   "2–7 stories/day",
        "bio_link":          "Use link-in-bio tool (Linktree etc.)",
        "cover_images":      "Consistent branded thumbnail style",
        "collab_posts":      "Use Collab feature for double reach",
        "audio":             "Use Trending audio for Reels boost",
    },
}

HASHTAG_STRATEGY = {
    "tier_1_broad":  "1–2 very large (1M+ posts) — discoverability",
    "tier_2_mid":    "2–3 medium (100K–1M posts) — competition balance",
    "tier_3_niche":  "3–5 small (<100K posts) — ranking easier",
    "branded":       "1 unique branded hashtag for community",
    "trending":      "1–2 trending sounds/events (refresh weekly)",
}


def score_account(
    platform: str,
    bio: str,
    follower_count: int,
    avg_views: int,
    post_count: int,
    avg_hashtags: int,
    has_profile_pic: bool,
    has_link: bool,
    posting_frequency_per_week: float,
) -> dict:
    """Return a score 0–100 and actionable recommendations."""
    platform = platform.lower()
    score = 0
    recs = []

    # Bio / description
    if bio and len(bio) > 50:
        score += 15
    elif bio:
        score += 8
        recs.append("Expand bio/description — include keywords and a clear value proposition")
    else:
        recs.append("Add a bio/description with keywords and niche focus")

    # Profile completeness
    if has_profile_pic:
        score += 10
    else:
        recs.append("Upload a professional profile picture (faces outperform logos 2:1)")

    if has_link:
        score += 10
    else:
        recs.append("Add a link-in-bio to drive traffic off-platform")

    # Posting cadence
    bp = PLATFORM_BEST_PRACTICES.get(platform, {})
    if platform == "tiktok":
        ideal_low, ideal_high = 7.0, 28.0
    elif platform == "youtube":
        ideal_low, ideal_high = 1.0, 2.0
    else:
        ideal_low, ideal_high = 3.0, 5.0

    if ideal_low <= posting_frequency_per_week <= ideal_high:
        score += 20
    elif posting_frequency_per_week > 0:
        score += 10
        recs.append(f"Adjust posting frequency — target: {bp.get('post_frequency', 'consistent')}")
    else:
        recs.append(f"Start posting consistently — {bp.get('post_frequency', '3–5x/week')}")

    # Hashtag usage
    if platform == "tiktok":
        ideal_tags = (3, 7)
    else:
        ideal_tags = (3, 10)
    if ideal_tags[0] <= avg_hashtags <= ideal_tags[1]:
        score += 15
    elif avg_hashtags > 0:
        score += 8
        recs.append(f"Refine hashtag count — target {ideal_tags[0]}–{ideal_tags[1]} per post (mix niche + trending)")
    else:
        recs.append(f"Use {ideal_tags[0]}–{ideal_tags[1]} hashtags per post")

    # Engagement proxy (views/followers)
    if follower_count > 0:
        view_rate = avg_views / follower_count
        if view_rate >= 0.1:
            score += 20
        elif view_rate >= 0.05:
            score += 12
            recs.append("Improve CTR: test stronger thumbnails/hooks in first 3 seconds")
        else:
            score += 5
            recs.append("Low views-to-followers ratio — audit thumbnails, titles, and hook quality")

    # Content volume
    if post_count >= 50:
        score += 10
    elif post_count >= 10:
        score += 5
        recs.append("Build a content library — consistency signals credibility to algorithms")
    else:
        recs.append("Post more content — algorithms favor accounts with 30+ posts before boosting")

    return {
        "platform": platform,
        "score": min(score, 100),
        "grade": _grade(score),
        "recommendations": recs,
        "best_practices": bp,
        "hashtag_strategy": HASHTAG_STRATEGY,
    }


def generate_posting_schedule(
    platform: str,
    timezone_offset: int = -5,
    posts_per_week: int = 5,
) -> list[dict]:
    """Return an optimized weekly posting schedule."""
    platform = platform.lower()

    schedules = {
        "tiktok": [
            {"day": "Monday",    "times": ["7:00 AM", "12:00 PM", "9:00 PM"]},
            {"day": "Tuesday",   "times": ["7:00 AM", "2:00 PM"]},
            {"day": "Wednesday", "times": ["8:00 AM", "12:00 PM", "7:00 PM"]},
            {"day": "Thursday",  "times": ["7:00 AM", "3:00 PM", "9:00 PM"]},
            {"day": "Friday",    "times": ["8:00 AM", "12:00 PM", "8:00 PM"]},
            {"day": "Saturday",  "times": ["9:00 AM", "2:00 PM", "8:00 PM"]},
            {"day": "Sunday",    "times": ["10:00 AM", "6:00 PM"]},
        ],
        "youtube": [
            {"day": "Thursday",  "times": ["2:00 PM"]},
            {"day": "Saturday",  "times": ["3:00 PM"]},
        ],
        "instagram": [
            {"day": "Monday",    "times": ["9:00 AM", "5:00 PM"]},
            {"day": "Wednesday", "times": ["12:00 PM"]},
            {"day": "Friday",    "times": ["9:00 AM", "5:00 PM"]},
        ],
    }

    base = schedules.get(platform, schedules["instagram"])
    result = []
    total = 0
    for slot in base:
        if total >= posts_per_week:
            break
        day_times = slot["times"][:max(1, posts_per_week - total)]
        result.append({"day": slot["day"], "post_times": day_times})
        total += len(day_times)

    return result


def _grade(score: int) -> str:
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    if score >= 50:
        return "D"
    return "F"
