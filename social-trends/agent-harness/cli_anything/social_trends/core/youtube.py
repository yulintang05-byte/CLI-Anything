"""YouTube trending content analysis via YouTube Data API v3."""

from cli_anything.social_trends.utils.social_backend import (
    yt_trending_videos,
    yt_search_videos,
    yt_video_categories,
    yt_channel_stats,
    extract_hashtags_from_videos,
    score_hashtag,
)


def get_trending(region: str = "US", category: str = "0",
                 limit: int = 25) -> dict:
    """Fetch trending YouTube videos with engagement analytics."""
    videos = yt_trending_videos(region_code=region, category_id=category,
                                max_results=limit)
    if not videos:
        return {"region": region, "category": category, "videos": [], "summary": {}}

    total_views = sum(v["views"] for v in videos)
    avg_views = total_views // len(videos) if videos else 0
    avg_likes = sum(v["likes"] for v in videos) // len(videos) if videos else 0
    top = videos[0] if videos else {}

    return {
        "region": region,
        "category_id": category,
        "total_results": len(videos),
        "summary": {
            "total_views": total_views,
            "avg_views": avg_views,
            "avg_likes": avg_likes,
            "top_video": top.get("title", ""),
            "top_channel": top.get("channel", ""),
        },
        "videos": videos,
    }


def search_trends(query: str, order: str = "viewCount",
                  limit: int = 20, region: str = "US",
                  days: int = 0) -> dict:
    """Search YouTube for trending content around a keyword."""
    published_after = None
    if days > 0:
        import datetime
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        published_after = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")

    videos = yt_search_videos(query=query, order=order, max_results=limit,
                              region_code=region, published_after=published_after)
    return {
        "query": query,
        "order": order,
        "region": region,
        "days_filter": days,
        "total_results": len(videos),
        "videos": videos,
    }


def list_categories(region: str = "US") -> dict:
    """List available YouTube video categories for a region."""
    categories = yt_video_categories(region_code=region)
    return {"region": region, "categories": categories}


def channel_audit(channel_id: str) -> dict:
    """Audit a YouTube channel and return optimization insights."""
    stats = yt_channel_stats(channel_id)
    insights = []

    if stats["subscribers"] < 1000:
        insights.append({
            "area": "Subscribers",
            "status": "Growing",
            "advice": "Focus on 2-3 videos/week with keyword-rich titles. "
                      "Aim for 4,000 watch hours to unlock monetization.",
        })
    elif stats["subscribers"] < 10_000:
        insights.append({
            "area": "Subscribers",
            "status": "Building",
            "advice": "Create a channel trailer and featured video. "
                      "Start a playlist for your best content to increase watch time.",
        })
    else:
        insights.append({
            "area": "Subscribers",
            "status": "Established",
            "advice": "Focus on community posts, Shorts repurposing, and membership perks.",
        })

    if not stats.get("keywords"):
        insights.append({
            "area": "Channel Keywords",
            "status": "Missing",
            "advice": "Add 10-15 niche-specific keywords in YouTube Studio > Customization > Basic info. "
                      "This boosts suggested video placement.",
        })

    if len(stats.get("description", "")) < 200:
        insights.append({
            "area": "Channel Description",
            "status": "Too Short",
            "advice": "Write a 500+ character description with your main keywords in the first 150 chars. "
                      "Include upload schedule and links.",
        })

    views_per_video = (stats["total_views"] // stats["video_count"]
                       if stats["video_count"] > 0 else 0)
    if views_per_video < 1000:
        insights.append({
            "area": "Average Views/Video",
            "status": f"{views_per_video:,} (Low)",
            "advice": "A/B test thumbnails with high contrast and faces. "
                      "Titles should include searchable keywords + curiosity gap. "
                      "First 30 seconds must hook viewers to improve CTR.",
        })

    return {
        "channel": stats,
        "insights": insights,
        "overall_score": min(100, int(50 + min(stats["subscribers"] / 10_000, 1) * 30
                                      + min(views_per_video / 10_000, 1) * 20)),
    }


def extract_trending_hashtags(region: str = "US", category: str = "0",
                               limit: int = 50) -> dict:
    """Extract and rank hashtags from trending YouTube videos."""
    videos = yt_trending_videos(region_code=region, category_id=category,
                                max_results=limit)
    tag_counts = extract_hashtags_from_videos(videos)
    total = len(videos)
    scored = [score_hashtag(tag, count, total) for tag, count in tag_counts.items()]
    scored.sort(key=lambda x: x["score"], reverse=True)
    return {
        "region": region,
        "analyzed_videos": total,
        "top_hashtags": scored[:30],
        "usage_tip": (
            "Use 3-5 of these tags per video. Mix 1-2 high-volume tags "
            "with 2-3 mid-tier niche tags for best reach."
        ),
    }
