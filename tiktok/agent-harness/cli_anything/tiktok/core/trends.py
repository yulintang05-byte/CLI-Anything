"""TikTok trending content discovery."""

from cli_anything.tiktok.utils.tiktok_backend import (
    fetch_trending_videos,
    fetch_trending_hashtags,
    fetch_trending_music,
    fetch_hashtag_analytics,
)


def get_trending_videos(region: str = "US", limit: int = 20) -> dict:
    videos = fetch_trending_videos(region=region, limit=limit)
    if not videos:
        return {"videos": [], "count": 0}

    # Extract trending hashtags from video descriptions
    hashtag_freq: dict = {}
    music_freq: dict = {}
    for v in videos:
        for tag in v.get("hashtags", []):
            if tag:
                hashtag_freq[tag] = hashtag_freq.get(tag, 0) + 1
        music_key = v.get("music_title", "")
        if music_key:
            music_freq[music_key] = music_freq.get(music_key, 0) + 1

    top_hashtags = sorted(hashtag_freq.items(), key=lambda x: -x[1])[:10]
    top_music = sorted(music_freq.items(), key=lambda x: -x[1])[:5]

    return {
        "videos": videos,
        "count": len(videos),
        "region": region,
        "top_hashtags_in_trending": [{"tag": t, "appearances": c} for t, c in top_hashtags],
        "top_music_in_trending": [{"title": m, "appearances": c} for m, c in top_music],
    }


def get_trending_hashtags(keyword: str = "", region: str = "US", limit: int = 30) -> dict:
    hashtags = fetch_trending_hashtags(keyword=keyword, region=region, limit=limit)
    # Sort by views descending
    hashtags = sorted(hashtags, key=lambda x: x.get("views", 0), reverse=True)
    return {
        "hashtags": hashtags,
        "count": len(hashtags),
        "region": region,
        "keyword_filter": keyword or "(none)",
    }


def get_trending_music(region: str = "US", limit: int = 20) -> dict:
    music = fetch_trending_music(region=region, limit=limit)
    music = sorted(music, key=lambda x: x.get("video_count", 0), reverse=True)
    return {
        "music": music,
        "count": len(music),
        "region": region,
    }


def analyze_hashtag(hashtag: str) -> dict:
    hashtag = hashtag.lstrip("#")
    data = fetch_hashtag_analytics(hashtag)
    views = data.get("views", 0)
    videos = data.get("videos", 0)
    avg_views_per_video = views // videos if videos else 0
    size = (
        "mega (>10B views)" if views > 10_000_000_000 else
        "large (1B-10B views)" if views > 1_000_000_000 else
        "medium (100M-1B views)" if views > 100_000_000 else
        "niche (<100M views)"
    )
    data["avg_views_per_video"] = avg_views_per_video
    data["audience_size"] = size
    data["recommendation"] = (
        "Great for discovery but high competition — pair with niche tags." if views > 5_000_000_000 else
        "Strong reach with moderate competition — include in every post." if views > 500_000_000 else
        "Niche audience — excellent for targeted reach and higher engagement rates."
    )
    return data


def build_hashtag_strategy(niche: str, region: str = "US") -> dict:
    """Generate a hashtag mix strategy for a given niche."""
    # Trending general tags (always include)
    general_tags = ["#fyp", "#foryoupage", "#viral", "#trending"]
    # Niche-specific tag suggestions
    niche_map = {
        "fitness": ["#fitness", "#workout", "#gym", "#fitnessmotivation", "#health"],
        "food": ["#foodtok", "#recipe", "#cooking", "#foodie", "#homecooking"],
        "fashion": ["#fashion", "#ootd", "#style", "#aesthetic", "#outfitinspo"],
        "business": ["#businesstips", "#entrepreneur", "#makemoney", "#sidehustle", "#passiveincome"],
        "beauty": ["#beauty", "#makeup", "#skincare", "#glowup", "#beautyhaul"],
        "travel": ["#travel", "#wanderlust", "#traveltok", "#adventure", "#explore"],
        "finance": ["#moneytips", "#investing", "#personalfinance", "#wealthbuilding", "#finance"],
        "tech": ["#tech", "#ai", "#coding", "#technology", "#techtok"],
        "comedy": ["#comedy", "#funny", "#humor", "#relatable", "#memes"],
        "motivation": ["#motivation", "#mindset", "#successmindset", "#inspiration", "#dailymotivation"],
    }
    niche_lower = niche.lower()
    matched_niche = None
    for k in niche_map:
        if k in niche_lower or niche_lower in k:
            matched_niche = k
            break

    niche_tags = niche_map.get(matched_niche, [f"#{niche_lower.replace(' ', '')}"])
    custom_niche_tag = f"#{niche_lower.replace(' ', '')}"

    return {
        "niche": niche,
        "strategy": {
            "mega_tags": general_tags,
            "niche_tags": niche_tags,
            "custom_tag": custom_niche_tag,
            "recommended_mix": general_tags[:2] + niche_tags[:3] + [custom_niche_tag],
        },
        "formula": "2 mega + 3 niche + 1 custom = 6 hashtags per post",
        "tip": "Use 3-6 hashtags max. More is not better on TikTok — relevance beats quantity.",
        "posting_times": {
            "best_days": ["Tuesday", "Thursday", "Friday"],
            "peak_hours_UTC": ["06:00-09:00", "12:00-15:00", "19:00-23:00"],
        },
    }
