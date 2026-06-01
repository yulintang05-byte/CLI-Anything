#!/usr/bin/env python3
"""Cross-platform trends analyzer — merges YouTube + TikTok signals."""

from collections import Counter, defaultdict
from typing import Optional
import re


STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "this", "that", "these",
    "those", "it", "its", "you", "your", "we", "our", "they", "their",
    "i", "my", "he", "she", "his", "her", "not", "no", "so", "if", "as",
    "up", "out", "how", "what", "when", "where", "who", "why", "all",
    "new", "like", "just", "get", "got", "more", "also",
}


def merge_hashtags(
    yt_hashtags: list[dict],
    tt_hashtags: list[dict],
    yt_weight: float = 0.4,
    tt_weight: float = 0.6,
) -> list[dict]:
    """Merge and normalize hashtag scores from both platforms."""
    combined: Counter = Counter()

    # Normalize YouTube hashtag scores to 0-100
    yt_max = max((h["score"] for h in yt_hashtags), default=1)
    for h in yt_hashtags:
        tag = h["hashtag"].lstrip("#").lower()
        combined[tag] += (h["score"] / yt_max) * 100 * yt_weight

    # Normalize TikTok scores
    tt_key = "view_count" if "view_count" in (tt_hashtags[0] if tt_hashtags else {}) else "engagement_score"
    tt_max = max((h.get(tt_key, 0) for h in tt_hashtags), default=1)
    for h in tt_hashtags:
        tag = h["hashtag"].lstrip("#").lower()
        combined[tag] += (h.get(tt_key, 0) / tt_max) * 100 * tt_weight

    return [
        {
            "hashtag": f"#{tag}",
            "cross_platform_score": round(score, 2),
            "rank": i + 1,
        }
        for i, (tag, score) in enumerate(combined.most_common(50))
    ]


def build_hashtag_sets(merged_hashtags: list[dict], niche: str = "") -> dict:
    """Build ready-to-use hashtag sets (broad, mid, niche) for a post."""
    all_tags = [h["hashtag"] for h in merged_hashtags]

    # Split into tiers by rank
    broad = all_tags[:10]    # highest reach, most competitive
    mid = all_tags[10:25]    # balanced reach/competition
    niche_tags = all_tags[25:40]  # lower reach, highly targeted

    if niche:
        niche_tags = [f"#{niche.replace(' ', '')}"] + niche_tags[:9]

    return {
        "broad": broad,
        "mid_tier": mid,
        "niche": niche_tags,
        "recommended_mix": broad[:3] + mid[:5] + niche_tags[:7],
        "caption_ready": " ".join(broad[:3] + mid[:4] + niche_tags[:3]),
    }


def identify_trend_topics(
    yt_videos: list[dict],
    tt_videos: list[dict],
    top_n: int = 15,
) -> list[dict]:
    """Extract key trending topics from video titles/descriptions."""
    word_score: Counter = Counter()

    for v in yt_videos:
        text = f"{v.get('title', '')} {v.get('description', '')}"
        views = v.get("view_count", 1000)
        words = re.findall(r"\b[a-z]{4,20}\b", text.lower())
        for w in words:
            if w not in STOP_WORDS:
                word_score[w] += views

    for v in tt_videos:
        if "error" in v:
            continue
        text = v.get("description", "")
        engagement = v.get("view_count", 1000)
        words = re.findall(r"\b[a-z]{4,20}\b", text.lower())
        for w in words:
            if w not in STOP_WORDS:
                word_score[w] += engagement

    return [
        {"topic": word, "trend_score": score, "rank": i + 1}
        for i, (word, score) in enumerate(word_score.most_common(top_n))
    ]


def score_content_idea(
    title: str,
    merged_hashtags: list[dict],
    trend_topics: list[dict],
) -> dict:
    """Score a content idea against current trends (0–100)."""
    title_lower = title.lower()
    tag_set = {h["hashtag"].lstrip("#") for h in merged_hashtags[:20]}
    topic_set = {t["topic"] for t in trend_topics[:15]}

    hashtag_hits = sum(1 for t in tag_set if t in title_lower)
    topic_hits = sum(1 for t in topic_set if t in title_lower)
    word_count = len(title.split())

    score = min(100, hashtag_hits * 20 + topic_hits * 15 + min(word_count, 5) * 2)
    return {
        "title": title,
        "trend_score": score,
        "hashtag_hits": hashtag_hits,
        "topic_hits": topic_hits,
        "verdict": "viral_potential" if score >= 60 else "moderate" if score >= 30 else "low",
        "suggestions": _suggest_improvements(title, tag_set, topic_set),
    }


def _suggest_improvements(
    title: str, tag_set: set, topic_set: set
) -> list[str]:
    tips = []
    if len(title) < 20:
        tips.append("Make title longer and more descriptive (20-60 chars ideal)")
    if not any(t in title.lower() for t in topic_set):
        top_topics = list(topic_set)[:3]
        tips.append(f"Consider weaving in trending topics: {', '.join(top_topics)}")
    if len(title.split()) < 4:
        tips.append("Add more keywords for better discoverability")
    if "?" not in title and "!" not in title:
        tips.append("Questions and exclamations increase click-through rate")
    return tips
