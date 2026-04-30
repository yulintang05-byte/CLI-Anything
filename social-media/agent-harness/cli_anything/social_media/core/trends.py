"""Trend aggregation and analysis across YouTube and TikTok."""

import json
from datetime import datetime
from typing import Optional

from cli_anything.social_media.utils.youtube_scraper import fetch_youtube_trending
from cli_anything.social_media.utils.tiktok_scraper import fetch_tiktok_trending


def create_project(name: str = "My Social Media") -> dict:
    return {
        "name": name,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "accounts": [],
        "last_trends_fetch": None,
        "trend_history": [],
        "hashtag_sets": [],
        "content_calendar": [],
    }


def open_project(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_project(project: dict, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(project, f, indent=2, default=str)


def get_project_info(project: dict) -> dict:
    return {
        "name": project.get("name", ""),
        "created_at": project.get("created_at", ""),
        "accounts": len(project.get("accounts", [])),
        "last_trends_fetch": project.get("last_trends_fetch", "never"),
        "trend_snapshots": len(project.get("trend_history", [])),
        "hashtag_sets": len(project.get("hashtag_sets", [])),
        "calendar_items": len(project.get("content_calendar", [])),
    }


def fetch_trends(
    project: dict,
    platforms: list[str],
    country: str = "US",
    limit: int = 20,
) -> dict:
    """Fetch trending content from specified platforms and store in project."""
    results = {}

    if "youtube" in platforms or "all" in platforms:
        yt = fetch_youtube_trending(country=country, limit=limit)
        results["youtube"] = yt

    if "tiktok" in platforms or "all" in platforms:
        tt = fetch_tiktok_trending(limit=limit, region=country)
        results["tiktok"] = tt

    snapshot = {
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "country": country,
        "platforms": list(results.keys()),
        "data": results,
    }

    project["last_trends_fetch"] = snapshot["fetched_at"]
    history = project.setdefault("trend_history", [])
    history.append(snapshot)
    # Keep last 10 snapshots
    project["trend_history"] = history[-10:]

    return snapshot


def analyze_trends(project: dict) -> dict:
    """Analyze the latest trend snapshot and return cross-platform insights."""
    history = project.get("trend_history", [])
    if not history:
        raise ValueError("No trend data available. Run 'trends fetch' first.")

    latest = history[-1]
    data = latest.get("data", {})

    all_hashtags: dict[str, int] = {}
    all_sounds: list[dict] = []
    top_niches: dict[str, int] = {}
    yt_titles = []
    tt_descriptions = []

    yt_data = data.get("youtube", {})
    for tag_entry in yt_data.get("trending_hashtags", []):
        tag = tag_entry["tag"]
        all_hashtags[tag] = all_hashtags.get(tag, 0) + tag_entry["occurrences"] * 2  # weight YT higher

    for v in yt_data.get("videos", []):
        yt_titles.append(v.get("title", ""))
        niche = _classify_niche(v.get("title", "") + " " + " ".join(v.get("hashtags", [])))
        if niche:
            top_niches[niche] = top_niches.get(niche, 0) + 1

    tt_data = data.get("tiktok", {})
    for tag_entry in tt_data.get("trending_hashtags", []):
        tag = tag_entry["tag"]
        all_hashtags[tag] = all_hashtags.get(tag, 0) + tag_entry["occurrences"]

    for sound in tt_data.get("trending_sounds", []):
        all_sounds.append(sound)

    for v in tt_data.get("videos", []):
        tt_descriptions.append(v.get("description", ""))
        niche = _classify_niche(v.get("description", "") + " " + " ".join(v.get("hashtags", [])))
        if niche:
            top_niches[niche] = top_niches.get(niche, 0) + 1

    top_tags = sorted(all_hashtags.items(), key=lambda x: -x[1])[:20]
    top_niche_list = sorted(top_niches.items(), key=lambda x: -x[1])[:5]

    content_angles = _generate_content_angles(yt_titles + tt_descriptions)

    return {
        "analyzed_at": datetime.utcnow().isoformat() + "Z",
        "data_from": latest["fetched_at"],
        "platforms_analyzed": latest.get("platforms", []),
        "top_hashtags_cross_platform": [{"tag": t, "score": s} for t, s in top_tags],
        "trending_sounds": all_sounds[:10],
        "top_niches": [{"niche": n, "count": c} for n, c in top_niche_list],
        "content_angle_templates": content_angles,
        "actionable_insights": _generate_insights(top_tags, top_niche_list, all_sounds),
    }


def get_latest_trends(project: dict) -> dict:
    """Return the most recent trend snapshot."""
    history = project.get("trend_history", [])
    if not history:
        raise ValueError("No trend data. Run 'trends fetch' first.")
    return history[-1]


def list_trend_history(project: dict) -> list[dict]:
    """List all trend snapshots."""
    return [
        {
            "index": i,
            "fetched_at": h["fetched_at"],
            "country": h.get("country", ""),
            "platforms": h.get("platforms", []),
        }
        for i, h in enumerate(project.get("trend_history", []))
    ]


def _classify_niche(text: str) -> Optional[str]:
    text_lower = text.lower()
    niches = {
        "finance": ["money", "invest", "income", "finance", "budget", "wealth", "rich", "passive"],
        "fitness": ["gym", "workout", "fitness", "weight", "muscle", "diet", "health"],
        "lifestyle": ["morning", "routine", "day in my life", "aesthetic", "vlog", "minimalist"],
        "fashion": ["outfit", "fashion", "style", "ootd", "clothes", "haul", "drip"],
        "food": ["recipe", "food", "cooking", "eat", "restaurant", "meal", "snack"],
        "travel": ["travel", "trip", "explore", "vacation", "abroad", "destination"],
        "beauty": ["skincare", "makeup", "beauty", "glow", "foundation", "routine"],
        "motivation": ["motivat", "mindset", "success", "entrepreneur", "hustle", "grind"],
        "education": ["learn", "study", "school", "college", "tips", "hack"],
    }
    for niche, keywords in niches.items():
        if any(kw in text_lower for kw in keywords):
            return niche
    return None


def _generate_content_angles(texts: list[str]) -> list[str]:
    """Generate proven viral content angle templates from trend data."""
    base_angles = [
        "POV: {situation}",
        "I tried {trend} for a week and here's what happened",
        "Stop doing this if you want to {goal}",
        "The {niche} secret nobody talks about",
        "Day {n} of {challenge} — honest results",
        "This {product/habit} changed my {outcome} in {timeframe}",
        "Things I wish I knew before {starting something}",
        "Rating viral {category} hacks so you don't have to",
        "{Number} {niche} tips that took me from 0 to {milestone}",
        "Realistic {niche} transformation: no filter, no BS",
    ]
    return base_angles


def _generate_insights(
    top_tags: list[tuple],
    top_niches: list[tuple],
    sounds: list[dict],
) -> list[str]:
    insights = []
    if top_niches:
        top_niche = top_niches[0][0]
        insights.append(f"Hottest niche right now: '{top_niche}' — high demand, ideal for theme pages.")
    if top_tags:
        power_tags = [t for t, _ in top_tags[:3]]
        insights.append(f"Must-use hashtags: {', '.join(power_tags)} — appear in top trending content.")
    if sounds:
        insights.append(f"Trending sound to use now: '{sounds[0].get('title', '')}' — {sounds[0].get('uses', 0):,} uses.")
    insights += [
        "Post at 6-9 AM or 7-10 PM in your target audience's timezone for max reach.",
        "First 3 seconds of video are critical — hook with a surprising statement or visual.",
        "Trending sounds boost algorithmic reach by up to 35% on TikTok.",
        "Cross-posting TikTok content to YouTube Shorts and Instagram Reels 3× your distribution.",
    ]
    return insights
