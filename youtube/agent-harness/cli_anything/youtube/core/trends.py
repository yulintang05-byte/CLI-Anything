"""YouTube trending content discovery and analysis."""

from cli_anything.youtube.utils.youtube_backend import (
    fetch_trending_videos,
    fetch_trending_music,
    fetch_hashtag_videos,
    fetch_trending_topics,
    CATEGORY_NAMES,
)


def get_trending_videos(region: str = "US", category: str = "all", limit: int = 20) -> dict:
    cat_id = "0"
    for cid, cname in CATEGORY_NAMES.items():
        if category.lower() in cname.lower() or category == cid:
            cat_id = cid
            break

    videos = fetch_trending_videos(region=region, category_id=cat_id, limit=limit)

    # Extract top hashtags
    hashtag_freq: dict = {}
    tag_freq: dict = {}
    for v in videos:
        for h in v.get("hashtags", []):
            if h:
                hashtag_freq[h] = hashtag_freq.get(h, 0) + 1
        for t in v.get("tags", []):
            if t:
                tag_freq[t] = tag_freq.get(t, 0) + 1

    top_hashtags = sorted(hashtag_freq.items(), key=lambda x: -x[1])[:10]
    top_tags = sorted(tag_freq.items(), key=lambda x: -x[1])[:10]

    total_views = sum(v.get("views", 0) for v in videos)
    avg_views = total_views // len(videos) if videos else 0

    return {
        "videos": videos,
        "count": len(videos),
        "region": region,
        "category": CATEGORY_NAMES.get(cat_id, "All"),
        "stats": {
            "total_views": total_views,
            "avg_views": avg_views,
            "avg_likes": sum(v.get("likes", 0) for v in videos) // len(videos) if videos else 0,
        },
        "trending_hashtags": [{"tag": t, "appearances": c} for t, c in top_hashtags],
        "trending_tags": [{"tag": t, "appearances": c} for t, c in top_tags[:10]],
    }


def get_trending_music(region: str = "US", limit: int = 20) -> dict:
    music = fetch_trending_music(region=region, limit=limit)
    return {
        "music_videos": music,
        "count": len(music),
        "region": region,
        "tip": "Use audio from these videos in your Shorts for a discoverability boost.",
    }


def search_by_hashtag(hashtag: str, limit: int = 20) -> dict:
    hashtag = hashtag.lstrip("#")
    videos = fetch_hashtag_videos(hashtag=hashtag, limit=limit)
    total_views = sum(v.get("views", 0) for v in videos)
    competition = (
        "Very high" if total_views > 100_000_000 else
        "High" if total_views > 10_000_000 else
        "Medium" if total_views > 1_000_000 else
        "Low (opportunity!)"
    )
    return {
        "hashtag": f"#{hashtag}",
        "videos": videos,
        "count": len(videos),
        "total_views_in_sample": total_views,
        "competition_level": competition,
        "recommendation": (
            "Very competitive — focus on Shorts format for faster traction." if total_views > 10_000_000 else
            "Good competition level — use this hashtag consistently."
        ),
    }


def get_trending_topics(region: str = "US") -> dict:
    topics = fetch_trending_topics(region)
    return {
        "topics": topics,
        "region": region,
        "top_opportunity": "How-to & Style and Science & Technology have highest CPM and advertiser demand in 2026.",
    }


def build_seo_strategy(niche: str, keywords: list = None) -> dict:
    """Build a YouTube SEO and content strategy for a niche."""
    if keywords is None:
        keywords = []

    niche_seo = {
        "fitness": {
            "title_formulas": [
                "I tried [X] for 30 days and here's what happened",
                "[N] minute [workout type] for [goal]",
                "How to [achieve result] WITHOUT [common sacrifice]",
            ],
            "top_keywords": ["workout routine", "lose weight fast", "home workout", "gym tips", "meal prep"],
            "best_length": "8-15 minutes (tutorials), 30-60 seconds (Shorts)",
            "upload_frequency": "3-5x per week",
            "monetization_cpm": "$6-12",
        },
        "finance": {
            "title_formulas": [
                "How I made $[amount] with [method] (step by step)",
                "[N] ways to make passive income in [year]",
                "Why 99% of people are BROKE (and how to fix it)",
            ],
            "top_keywords": ["passive income", "how to invest", "make money online", "budget", "financial freedom"],
            "best_length": "10-20 minutes",
            "upload_frequency": "2-3x per week",
            "monetization_cpm": "$15-35",
        },
        "tech": {
            "title_formulas": [
                "I tested [product] for [time] — honest review",
                "[Tool] just changed EVERYTHING for [use case]",
                "The AI tool that replaced my [expensive thing]",
            ],
            "top_keywords": ["ai tools", "best apps", "tech review", "how to use ai", "productivity tools"],
            "best_length": "8-15 minutes",
            "upload_frequency": "2-4x per week",
            "monetization_cpm": "$8-20",
        },
    }

    niche_lower = niche.lower()
    matched = None
    for k in niche_seo:
        if k in niche_lower:
            matched = k
            break

    data = niche_seo.get(matched, {
        "title_formulas": [
            f"[N] {niche} tips that actually work",
            f"I spent [time] learning {niche} — here's everything",
            f"The TRUTH about {niche} nobody tells you",
        ],
        "top_keywords": [niche, f"{niche} tips", f"{niche} for beginners", f"how to {niche}", f"best {niche}"],
        "best_length": "8-15 minutes",
        "upload_frequency": "2-3x per week",
        "monetization_cpm": "$5-10",
    })
    data["niche"] = niche
    data["seo_checklist"] = [
        "Include primary keyword in title (first 60 characters)",
        "Write 200-500 word description with keywords naturally placed",
        "Add 5-10 relevant tags (not 500 — quality over quantity)",
        "Create custom thumbnail: bright, high-contrast, <3 words of text",
        "Add chapters/timestamps (boosts watch time and search ranking)",
        "Pin a comment with resource links to boost engagement",
        "Add subtitles/captions (YouTube indexes them for SEO)",
        "Publish as unlisted first, schedule for peak time (Thu-Sat 12-4pm ET)",
    ]
    return data
