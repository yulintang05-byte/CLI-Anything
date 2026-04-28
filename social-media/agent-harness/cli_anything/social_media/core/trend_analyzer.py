"""Cross-platform trend analyzer - ranks and scores viral content signals."""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import Counter


def _normalize_tag(tag: str) -> str:
    return tag.lower().lstrip("#").strip()


def score_hashtag(
    tag: str,
    yt_count: int = 0,
    tt_count: int = 0,
    tt_views_str: str = "",
) -> float:
    """
    Compute a 0-100 virality score for a hashtag.

    Scoring factors:
    - Cross-platform presence (highest signal)
    - TikTok view volume
    - YouTube trending appearances
    """
    score = 0.0

    # Cross-platform bonus (both YT + TT)
    if yt_count > 0 and tt_count > 0:
        score += 40

    # YouTube trending appearances (max 30)
    score += min(yt_count * 5, 30)

    # TikTok presence
    if tt_count > 0:
        score += min(tt_count * 3, 20)

    # TikTok view volume bonus
    if tt_views_str:
        num = _parse_view_string(tt_views_str)
        if num >= 1_000_000_000:
            score += 10
        elif num >= 100_000_000:
            score += 7
        elif num >= 10_000_000:
            score += 4

    return round(min(score, 100), 1)


def _parse_view_string(s: str) -> int:
    s = s.strip().upper().replace(",", "").rstrip("+")
    multipliers = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}
    for suffix, mult in multipliers.items():
        if s.endswith(suffix):
            try:
                return int(float(s[:-1]) * mult)
            except ValueError:
                return 0
    try:
        return int(s)
    except ValueError:
        return 0


def merge_platform_trends(
    youtube_data: Dict[str, Any],
    tiktok_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Merge YouTube and TikTok trend data into a unified ranked list.

    Returns cross-platform hot tags, sounds, and content format signals.
    """
    # Collect YouTube hashtags
    yt_tags: Counter = Counter()
    for h in youtube_data.get("top_hashtags", []):
        tag = _normalize_tag(h.get("tag", ""))
        if tag:
            yt_tags[tag] += h.get("count", 1)

    for v in youtube_data.get("videos", []):
        for tag in v.get("hashtags", []):
            yt_tags[_normalize_tag(tag)] += 1

    # Collect TikTok hashtags
    tt_tags: Counter = Counter()
    tt_tag_meta: Dict[str, Dict] = {}
    for h in tiktok_data.get("hashtags", []):
        tag = _normalize_tag(h.get("hashtag", ""))
        if tag:
            tt_tags[tag] += 1
            tt_tag_meta[tag] = h

    # Union of all tags
    all_tags = set(yt_tags.keys()) | set(tt_tags.keys())

    ranked = []
    for tag in all_tags:
        if not tag or len(tag) < 2:
            continue
        meta = tt_tag_meta.get(tag, {})
        views_str = meta.get("avg_views", "")
        vscore = score_hashtag(
            tag,
            yt_count=yt_tags.get(tag, 0),
            tt_count=tt_tags.get(tag, 0),
            tt_views_str=views_str,
        )
        ranked.append({
            "hashtag": f"#{tag}",
            "virality_score": vscore,
            "on_youtube": yt_tags.get(tag, 0) > 0,
            "on_tiktok": tt_tags.get(tag, 0) > 0,
            "cross_platform": yt_tags.get(tag, 0) > 0 and tt_tags.get(tag, 0) > 0,
            "yt_appearances": yt_tags.get(tag, 0),
            "tt_appearances": tt_tags.get(tag, 0),
            "category": meta.get("category", ""),
            "avg_views": views_str,
            "type": meta.get("type", ""),
        })

    ranked.sort(key=lambda x: x["virality_score"], reverse=True)

    # Extract top sounds from TikTok
    sounds = tiktok_data.get("trending_sounds", [])

    # Identify content format trends (what video styles are viral)
    content_signals = _detect_content_signals(youtube_data, tiktok_data)

    return {
        "analyzed_at": datetime.now().isoformat(),
        "total_tags_analyzed": len(ranked),
        "top_hashtags": ranked[:30],
        "cross_platform_hits": [t for t in ranked if t["cross_platform"]][:10],
        "youtube_only": [t for t in ranked if t["on_youtube"] and not t["on_tiktok"]][:10],
        "tiktok_only": [t for t in ranked if t["on_tiktok"] and not t["on_youtube"]][:10],
        "trending_sounds": sounds,
        "content_signals": content_signals,
        "recommended_hashtag_mix": _build_hashtag_mix(ranked),
    }


def _detect_content_signals(yt: Dict, tt: Dict) -> List[Dict[str, Any]]:
    """Infer what content formats are trending from video titles."""
    format_keywords = {
        "tutorial/how-to": ["how to", "tutorial", "guide", "learn", "diy", "tips", "tricks"],
        "storytime": ["storytime", "story time", "i tried", "i did", "what happened"],
        "reaction": ["reacting to", "reaction", "watch me", "my reaction"],
        "challenge": ["challenge", "trend", "try this", "attempting"],
        "educational": ["did you know", "facts about", "explained", "science of", "history of"],
        "motivational": ["motivation", "mindset", "success", "grind", "hustle"],
        "product-review": ["review", "honest review", "testing", "worth it", "unboxing"],
        "day-in-life": ["day in my life", "vlog", "come with me", "a day as"],
        "transformation": ["transformation", "before and after", "glow up", "makeover"],
        "listicle": ["top 10", "top 5", "best", "worst", "ranked", "tier list"],
    }

    detected: Dict[str, int] = Counter()
    titles = [v.get("title", "").lower() for v in yt.get("videos", [])]

    for title in titles:
        for fmt, keywords in format_keywords.items():
            if any(kw in title for kw in keywords):
                detected[fmt] += 1

    signals = []
    for fmt, count in sorted(detected.items(), key=lambda x: x[1], reverse=True):
        signals.append({
            "format": fmt,
            "trending_videos": count,
            "recommendation": _format_recommendation(fmt),
        })

    if not signals:
        signals = [
            {"format": "educational", "trending_videos": 0, "recommendation": "Educational content drives 70%+ completion — great for algorithm favor in 2026."},
            {"format": "storytime", "trending_videos": 0, "recommendation": "Storytime hooks spike early watch time — strong FYP signal."},
        ]
    return signals[:8]


def _format_recommendation(fmt: str) -> str:
    recs = {
        "tutorial/how-to": "How-to content earns saves (2x algorithm boost). Lead with the end result in the first 3 seconds.",
        "storytime": "Storytime format drives completion rate. Open with a cliffhanger or shocking statement.",
        "reaction": "Reaction videos get high share rates. React to content already going viral for bonus reach.",
        "challenge": "Challenges spread via Duet/Stitch. Create a template others can replicate easily.",
        "educational": "Educational content earns saves and shares. Use 3-5 relevant hashtags + spoken keywords.",
        "motivational": "Motivational content peaks Mon/Tue mornings. Pair with trending audio for wider reach.",
        "product-review": "Reviews drive affiliate conversions. Pin the product link in bio for direct monetization.",
        "day-in-life": "Day-in-life builds parasocial trust — essential for theme page brand deals and selling.",
        "transformation": "Before/after has the highest rewatch rate of any format. Maximize hook in first frame.",
        "listicle": "Listicles get commented on ('I'm #3!'). Boost engagement signals significantly.",
    }
    return recs.get(fmt, "High-performing format. Keep under 60 seconds for max completion rate.")


def _build_hashtag_mix(ranked: List[Dict]) -> Dict[str, Any]:
    """
    Build a 3-5 hashtag posting strategy based on 2026 algorithm research.
    Mix: 1 mega + 1-2 niche + 1-2 trending = optimal reach without dilution.
    """
    mega = [t for t in ranked if t.get("avg_views", "").endswith("B+")][:1]
    niche = [t for t in ranked if t.get("type") == "niche" and t["virality_score"] > 30][:2]
    trending = [t for t in ranked if t["cross_platform"] or t["virality_score"] > 50][:2]

    mix = []
    seen = set()
    for group in [mega, trending, niche]:
        for t in group:
            tag = t["hashtag"]
            if tag not in seen:
                seen.add(tag)
                mix.append(tag)
    mix = mix[:5]

    return {
        "hashtags": mix,
        "strategy": (
            "Post 3-5 hashtags per video. "
            "1 broad discovery tag (#fyp), 1-2 trending tags, 1-2 tight niche tags. "
            "Include spoken keywords matching hashtags — TikTok 2026 reads audio for indexing."
        ),
        "posting_frequency": "3-4 high-quality videos/week beats daily low-effort posting (2026 algorithm update).",
        "best_post_times": {
            "tiktok": ["6-9am", "12-3pm", "7-11pm"],
            "youtube_shorts": ["9am-12pm", "5-8pm"],
            "note": "Times in your audience's primary timezone. Check analytics for your specific audience.",
        },
    }


def generate_content_calendar(
    niche: str,
    platforms: List[str],
    posts_per_week: int = 4,
    weeks: int = 2,
) -> Dict[str, Any]:
    """Generate a content calendar based on viral trend patterns."""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    formats_by_niche = {
        "business": ["tutorial", "storytime", "listicle", "motivational", "product-review"],
        "fitness": ["tutorial", "transformation", "challenge", "day-in-life", "educational"],
        "beauty": ["tutorial", "transformation", "product-review", "reaction", "day-in-life"],
        "food": ["tutorial", "listicle", "reaction", "day-in-life", "challenge"],
        "gaming": ["reaction", "tutorial", "challenge", "listicle", "storytime"],
        "fashion": ["day-in-life", "transformation", "tutorial", "product-review", "challenge"],
        "finance": ["educational", "listicle", "storytime", "motivational", "tutorial"],
        "travel": ["day-in-life", "listicle", "storytime", "tutorial", "reaction"],
    }
    niche_lower = niche.lower()
    formats = next(
        (v for k, v in formats_by_niche.items() if k in niche_lower),
        ["tutorial", "educational", "storytime", "listicle", "motivational"],
    )

    # Distribute posts across high-engagement days
    high_days = [0, 2, 4, 5]  # Mon, Wed, Fri, Sat
    post_days = (high_days * 10)[:posts_per_week]

    calendar = []
    fmt_cycle = (formats * 10)[:posts_per_week * weeks]
    for week in range(1, weeks + 1):
        for i, day_idx in enumerate(post_days):
            slot_idx = (week - 1) * posts_per_week + i
            fmt = fmt_cycle[slot_idx % len(fmt_cycle)]
            calendar.append({
                "week": week,
                "day": days[day_idx],
                "format": fmt,
                "platforms": platforms,
                "hook_template": _hook_template(fmt, niche),
                "hashtag_focus": niche_lower,
                "tip": _format_recommendation(fmt),
            })

    return {
        "niche": niche,
        "platforms": platforms,
        "posts_per_week": posts_per_week,
        "weeks": weeks,
        "calendar": calendar,
        "repurpose_tip": (
            "Shoot once, repurpose everywhere: "
            "TikTok vertical → YouTube Shorts → Instagram Reels. "
            "Remove watermarks before cross-posting (platforms penalize them)."
        ),
    }


def _hook_template(fmt: str, niche: str) -> str:
    hooks = {
        "tutorial": f"Here's the {niche} trick nobody tells you (saves hours)...",
        "storytime": f"I almost quit {niche} until this happened...",
        "listicle": f"5 {niche} mistakes that are costing you money/time...",
        "motivational": f"If you're struggling with {niche}, watch this...",
        "product-review": f"I tested every {niche} tool so you don't have to...",
        "educational": f"The {niche} secret they don't want you to know...",
        "challenge": f"Try this {niche} challenge for 7 days and tell me what changes...",
        "transformation": f"My {niche} journey: 0 to [result] in [timeframe]...",
        "day-in-life": f"A day in my life as a {niche} creator...",
        "reaction": f"Reacting to the most viral {niche} content this week...",
    }
    return hooks.get(fmt, f"The truth about {niche} nobody talks about...")
