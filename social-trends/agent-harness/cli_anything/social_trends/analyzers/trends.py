"""Trend analyzer — cross-platform hashtag, music, and topic intelligence."""
from __future__ import annotations

import re
from collections import Counter
from typing import Any


# Common stop words to exclude from topic extraction
_STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "this", "that",
    "these", "those", "i", "you", "he", "she", "it", "we", "they", "me",
    "him", "her", "us", "them", "my", "your", "his", "its", "our", "their",
    "what", "which", "who", "how", "when", "where", "why", "all", "more",
    "most", "some", "any", "no", "not", "so", "if", "as", "than", "then",
    "up", "out", "about", "into", "than", "just", "now", "new", "get",
    "got", "go", "going", "come", "coming", "make", "made", "take", "taken",
    "see", "seen", "know", "like", "time", "year", "day", "week", "watch",
    "video", "subscribe", "channel", "follow", "share", "comment", "link",
}


def analyze_hashtags(
    youtube_data: dict | None = None,
    tiktok_data: dict | None = None,
) -> dict:
    """
    Cross-platform hashtag analysis.
    Merges YouTube and TikTok hashtag signals into a unified ranked list.
    """
    combined: dict[str, dict] = {}

    if youtube_data:
        for video in youtube_data.get("videos", []):
            text = f"{video.get('title','')} {video.get('description','')} {' '.join(video.get('tags',[]))}"
            for tag in re.findall(r"#(\w+)", text, re.IGNORECASE):
                t = tag.lower()
                if t not in combined:
                    combined[t] = {"tag": f"#{t}", "youtube_count": 0, "tiktok_count": 0, "total": 0}
                combined[t]["youtube_count"] += 1
            for tag in video.get("tags", []):
                t = tag.lower().replace(" ", "")
                if len(t) > 1:
                    if t not in combined:
                        combined[t] = {"tag": f"#{t}", "youtube_count": 0, "tiktok_count": 0, "total": 0}
                    combined[t]["youtube_count"] += 1

    if tiktok_data:
        for ht in tiktok_data.get("hashtags", []):
            raw = ht.get("tag", "").lstrip("#").lower()
            if not raw:
                continue
            if raw not in combined:
                combined[raw] = {"tag": f"#{raw}", "youtube_count": 0, "tiktok_count": 0, "total": 0}
            combined[raw]["tiktok_count"] += ht.get("video_count", 1)
            combined[raw]["view_count"] = ht.get("view_count", 0)
            combined[raw]["rank"] = ht.get("rank", 999)

        for video in tiktok_data.get("videos", []):
            for tag in video.get("hashtags", []):
                t = tag.lstrip("#").lower()
                if t and t not in combined:
                    combined[t] = {"tag": f"#{t}", "youtube_count": 0, "tiktok_count": 0, "total": 0}
                if t:
                    combined[t]["tiktok_count"] += 1

    # Score: tiktok volume is weighted higher (faster-moving platform)
    for entry in combined.values():
        entry["total"] = entry["youtube_count"] + entry["tiktok_count"] * 3

    ranked = sorted(combined.values(), key=lambda x: x["total"], reverse=True)

    # Classify tags
    for entry in ranked:
        entry["platform"] = _classify_platform(entry)

    return {
        "top_hashtags": ranked[:50],
        "cross_platform": [h for h in ranked if h["youtube_count"] > 0 and h["tiktok_count"] > 0][:20],
        "tiktok_only": [h for h in ranked if h["youtube_count"] == 0 and h["tiktok_count"] > 0][:20],
        "youtube_only": [h for h in ranked if h["youtube_count"] > 0 and h["tiktok_count"] == 0][:20],
        "total_unique_tags": len(ranked),
    }


def _classify_platform(entry: dict) -> str:
    yt = entry["youtube_count"]
    tt = entry["tiktok_count"]
    if yt > 0 and tt > 0:
        return "cross-platform"
    if tt > 0:
        return "tiktok"
    return "youtube"


def analyze_trending_music(tiktok_data: dict | None = None) -> dict:
    """
    Extract and rank trending sounds/music from TikTok data.
    Music trends on TikTok drive YouTube Shorts and Instagram Reels adoption.
    """
    if not tiktok_data:
        return {"sounds": [], "insights": []}

    sounds = tiktok_data.get("sounds", [])

    # Also extract music from individual videos
    music_from_videos: dict[str, dict] = {}
    for video in tiktok_data.get("videos", []):
        music = video.get("music", {})
        mid = music.get("id", "")
        if not mid or music.get("is_original"):
            continue
        if mid not in music_from_videos:
            music_from_videos[mid] = {
                "id": mid,
                "title": music.get("title", ""),
                "author": music.get("author", ""),
                "use_count": 0,
            }
        music_from_videos[mid]["use_count"] += 1

    all_sounds = list(sounds)
    for s in music_from_videos.values():
        if not any(x.get("id") == s["id"] for x in all_sounds):
            all_sounds.append(s)

    all_sounds.sort(key=lambda x: x.get("use_count", 0) or x.get("rank", 999), reverse=True)

    insights = _generate_music_insights(all_sounds)

    return {
        "sounds": all_sounds[:30],
        "original_sounds": [s for s in all_sounds if s.get("is_original")][:10],
        "licensed_music": [s for s in all_sounds if not s.get("is_original")][:20],
        "insights": insights,
    }


def _generate_music_insights(sounds: list[dict]) -> list[str]:
    insights = []
    if not sounds:
        return ["No sound data available — run with fresh TikTok data"]

    top = sounds[:5]
    titles = [s.get("title", "") for s in top if s.get("title")]
    if titles:
        insights.append(f"Top trending sounds: {', '.join(titles[:3])}")

    original_count = sum(1 for s in sounds if s.get("is_original"))
    if original_count > len(sounds) * 0.3:
        insights.append("High original sound usage — opportunity for branded audio")
    else:
        insights.append("Licensed music dominates — use trending songs for maximum reach")

    insights.append("Pro tip: Using a trending sound in the first 24h of it going viral multiplies reach 3-5x")
    insights.append("TikTok sounds cross-pollinate to YouTube Shorts and Instagram Reels within 48-72h")
    return insights


def analyze_topics(
    youtube_data: dict | None = None,
    tiktok_data: dict | None = None,
) -> dict:
    """Extract trending topics and content angles from video titles and descriptions."""
    word_counts: Counter = Counter()
    bigram_counts: Counter = Counter()
    niche_signals: list[str] = []

    all_texts = []
    if youtube_data:
        for v in youtube_data.get("videos", []):
            all_texts.append(v.get("title", ""))
    if tiktok_data:
        for v in tiktok_data.get("videos", []):
            all_texts.append(v.get("description", ""))

    for text in all_texts:
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        filtered = [w for w in words if w not in _STOP_WORDS]
        word_counts.update(filtered)

        for i in range(len(filtered) - 1):
            bigram_counts[f"{filtered[i]} {filtered[i+1]}"] += 1

    top_words = word_counts.most_common(30)
    top_bigrams = bigram_counts.most_common(20)

    content_angles = _derive_content_angles(top_words, top_bigrams)

    return {
        "top_keywords": [{"word": w, "count": c} for w, c in top_words],
        "top_phrases": [{"phrase": p, "count": c} for p, c in top_bigrams],
        "content_angles": content_angles,
        "total_videos_analyzed": len(all_texts),
    }


def _derive_content_angles(
    top_words: list[tuple],
    top_bigrams: list[tuple],
) -> list[str]:
    """Convert keyword signals into actionable content angles."""
    angles = []
    word_set = {w for w, _ in top_words[:15]}

    if any(w in word_set for w in ("tutorial", "how", "diy", "learn", "guide")):
        angles.append("How-to/Tutorial content is trending — step-by-step format performs best")
    if any(w in word_set for w in ("best", "top", "ranked", "ultimate")):
        angles.append("Listicle/ranking format is high-performing — 'Top 5/10' style videos")
    if any(w in word_set for w in ("reaction", "react", "challenge", "try")):
        angles.append("Reaction and challenge content driving engagement — consider duet/collab format")
    if any(w in word_set for w in ("money", "income", "business", "earn", "profit")):
        angles.append("Finance/business niche trending — monetization content has strong CPM")
    if any(w in word_set for w in ("ai", "tech", "digital", "future", "tool")):
        angles.append("Tech/AI content trending — educational breakdowns of tools perform well")
    if any(w in word_set for w in ("food", "recipe", "cook", "eat", "taste")):
        angles.append("Food content is evergreen — cooking tutorials and taste tests drive shares")
    if any(w in word_set for w in ("fitness", "workout", "gym", "health", "diet")):
        angles.append("Fitness/health trending — transformation and routine videos spike in views")

    if not angles:
        angles.append("General entertainment trending — focus on relatable, shareable moments")

    angles.append("Short-form hook: front-load the payoff in first 2 seconds to beat algorithm churn")
    return angles


def generate_full_report(
    youtube_data: dict | None = None,
    tiktok_data: dict | None = None,
) -> dict:
    """Generate a unified trend intelligence report across both platforms."""
    hashtag_analysis = analyze_hashtags(youtube_data, tiktok_data)
    music_analysis = analyze_trending_music(tiktok_data)
    topic_analysis = analyze_topics(youtube_data, tiktok_data)

    summary = _build_summary(hashtag_analysis, music_analysis, topic_analysis)

    return {
        "summary": summary,
        "hashtags": hashtag_analysis,
        "music": music_analysis,
        "topics": topic_analysis,
        "action_items": _build_action_items(hashtag_analysis, music_analysis, topic_analysis),
    }


def _build_summary(ht: dict, music: dict, topics: dict) -> dict:
    top_tags = [h["tag"] for h in ht.get("top_hashtags", [])[:5]]
    top_sounds = [s.get("title", "") for s in music.get("sounds", [])[:3] if s.get("title")]
    top_keywords = [k["word"] for k in topics.get("top_keywords", [])[:5]]

    return {
        "top_5_hashtags": top_tags,
        "top_3_sounds": top_sounds,
        "top_5_keywords": top_keywords,
        "cross_platform_opportunities": len(ht.get("cross_platform", [])),
    }


def _build_action_items(ht: dict, music: dict, topics: dict) -> list[str]:
    items = []

    cross = ht.get("cross_platform", [])
    if cross:
        tags = " ".join(h["tag"] for h in cross[:5])
        items.append(f"Use cross-platform hashtags in ALL posts: {tags}")

    tiktok_only = ht.get("tiktok_only", [])
    if tiktok_only:
        tags = " ".join(h["tag"] for h in tiktok_only[:3])
        items.append(f"TikTok-specific tags to boost FYP reach: {tags}")

    sounds = music.get("sounds", [])
    if sounds:
        sound = sounds[0]
        items.append(
            f"Use trending sound NOW: '{sound.get('title','unknown')}' by {sound.get('author','unknown')} — "
            f"{sound.get('use_count', '?')} videos using it"
        )

    for angle in topics.get("content_angles", [])[:2]:
        items.append(angle)

    items.append("Post frequency: TikTok 1-3x/day, YouTube Shorts 1x/day, Instagram Reels 1x/day")
    items.append("Best posting windows: 6-9 AM, 12-3 PM, 7-11 PM (audience local time)")
    return items
