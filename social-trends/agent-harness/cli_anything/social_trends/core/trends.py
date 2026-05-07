"""Trend fetching — YouTube trending videos, TikTok hashtags and sounds."""

from typing import Optional
from cli_anything.social_trends.utils.social_backend import (
    fetch_youtube_trending,
    fetch_tiktok_trending_hashtags,
    fetch_tiktok_trending_sounds,
)


def get_youtube_trending(
    region: str = "US",
    category: str = "all",
    limit: int = 20,
) -> dict:
    videos = fetch_youtube_trending(region=region, category=category, limit=limit)
    tags: dict[str, int] = {}
    for v in videos:
        for t in v.get("tags", []):
            tags[t] = tags.get(t, 0) + 1
    top_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)[:15]
    return {
        "platform": "youtube",
        "region": region,
        "category": category,
        "count": len(videos),
        "videos": videos,
        "extracted_tags": [t for t, _ in top_tags],
    }


def get_tiktok_trending(limit: int = 30) -> dict:
    hashtags = fetch_tiktok_trending_hashtags(limit=limit)
    sounds = fetch_tiktok_trending_sounds(limit=10)
    return {
        "platform": "tiktok",
        "hashtag_count": len(hashtags),
        "hashtags": hashtags,
        "trending_sounds": sounds[:5],
    }


def get_all_trending(
    region: str = "US",
    category: str = "all",
    limit: int = 20,
) -> dict:
    yt = get_youtube_trending(region=region, category=category, limit=limit)
    tt = get_tiktok_trending(limit=30)
    return {
        "youtube": yt,
        "tiktok": tt,
        "combined_tags": list(
            dict.fromkeys(
                [f"#{t}" for t in yt["extracted_tags"]]
                + [h["tag"] for h in tt["hashtags"][:15]]
            )
        )[:25],
    }


def get_trending_music(platform: str = "all", limit: int = 20) -> dict:
    sounds = fetch_tiktok_trending_sounds(limit=limit)
    if platform.lower() in ("tiktok", "all"):
        return {
            "platform": platform,
            "count": len(sounds),
            "sounds": sounds,
        }
    return {
        "platform": platform,
        "count": len(sounds),
        "sounds": sounds,
        "note": "Music data sourced from TikTok trending sounds (cross-platform popularity).",
    }


def get_viral_content_signals(niche: str = "", limit: int = 10) -> dict:
    """Identify viral content patterns for a given niche."""
    patterns = _viral_patterns(niche)
    hooks = _viral_hooks(niche)
    formats = _viral_formats(niche)
    return {
        "niche": niche or "general",
        "viral_patterns": patterns[:limit],
        "proven_hooks": hooks[:8],
        "best_formats": formats,
    }


# ── Viral intelligence data ───────────────────────────────────────────────────

def _viral_patterns(niche: str) -> list[dict]:
    general = [
        {"pattern": "Before & After", "desc": "Transformation reveals — maximum curiosity gap", "platforms": ["tiktok", "instagram", "youtube"]},
        {"pattern": "Storytime", "desc": "Personal story with emotional arc and lesson", "platforms": ["tiktok", "youtube"]},
        {"pattern": "POV (Point of View)", "desc": "Immersive first-person scenario content", "platforms": ["tiktok", "instagram"]},
        {"pattern": "Day in the Life", "desc": "Authentic behind-the-scenes lifestyle content", "platforms": ["tiktok", "youtube", "instagram"]},
        {"pattern": "React / Respond", "desc": "Responding to viral or trending content", "platforms": ["tiktok", "youtube"]},
        {"pattern": "Myth vs Fact", "desc": "Debunking common misconceptions in your niche", "platforms": ["tiktok", "instagram", "youtube"]},
        {"pattern": "Tutorial / How-To", "desc": "Step-by-step value content with quick results", "platforms": ["tiktok", "youtube", "instagram"]},
        {"pattern": "Challenge Attempt", "desc": "Riding trending challenges in your niche context", "platforms": ["tiktok", "instagram"]},
        {"pattern": "List / Countdown", "desc": "\"5 things you didn't know\" format", "platforms": ["tiktok", "youtube"]},
        {"pattern": "Duet / Collaboration", "desc": "Duet or collab with viral content for exposure", "platforms": ["tiktok"]},
    ]
    niche_specific = {
        "fitness": [{"pattern": "Workout Transformation", "desc": "Progress photos + workout reveal", "platforms": ["tiktok", "instagram"]}],
        "finance": [{"pattern": "Income Report", "desc": "Transparent earnings breakdown builds trust", "platforms": ["tiktok", "youtube"]}],
        "food": [{"pattern": "Recipe Hack", "desc": "\"Restaurant dish for $2\" style value content", "platforms": ["tiktok", "instagram"]}],
        "fashion": [{"pattern": "Outfit Check", "desc": "Rate my outfit / roast my wardrobe", "platforms": ["tiktok", "instagram"]}],
    }
    extra = niche_specific.get(niche.lower(), [])
    return extra + general


def _viral_hooks(niche: str) -> list[str]:
    hooks = [
        "I wish someone told me this earlier...",
        "POV: You finally figured out [result]",
        "Stop doing this if you want [goal]",
        "This changed everything for me...",
        "Nobody talks about this but...",
        "How I [result] in [short timeframe]",
        "Things I learned after [experience]",
        "Day [X] of [challenge] — here's what happened",
        "The truth about [niche topic] nobody admits",
        "If you're [target audience], watch this",
        "I tested [claim] so you don't have to",
        "The one thing separating [success] from [failure]",
    ]
    niche_hooks = {
        "fitness": ["How I dropped [X] lbs without the gym", "This 10-min workout beats 1-hour gym sessions"],
        "finance": ["I invested $100 and here's what happened", "How broke 22-year-olds build wealth"],
        "food": ["$5 meal that tastes like $50", "The hack chefs don't want you to know"],
        "motivation": ["The mindset shift that fixed everything", "Hard truth: this is why you're stuck"],
    }
    extras = niche_hooks.get(niche.lower(), [])
    return extras + hooks


def _viral_formats(niche: str) -> list[dict]:
    return [
        {"format": "Vertical Short-Form (9:16)", "length": "15–60s", "best_for": "TikTok, Reels, Shorts", "priority": "HIGH"},
        {"format": "Talking Head", "length": "30s–3min", "best_for": "TikTok, YouTube", "priority": "HIGH"},
        {"format": "Screen Recording", "length": "30s–2min", "best_for": "Finance, Tech, Business TikTok", "priority": "MEDIUM"},
        {"format": "Carousel / Slides", "length": "5–10 slides", "best_for": "Instagram, LinkedIn", "priority": "HIGH"},
        {"format": "Long-form Tutorial", "length": "8–20min", "best_for": "YouTube", "priority": "MEDIUM"},
        {"format": "Photo + Trending Audio", "length": "Photo", "best_for": "Instagram Reels", "priority": "MEDIUM"},
    ]
