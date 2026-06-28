"""Hashtag research, scoring, and strategy for YouTube and TikTok."""

from cli_anything.social_trends.utils.social_backend import (
    yt_trending_videos,
    yt_search_videos,
    extract_hashtags_from_videos,
    score_hashtag,
    get_youtube_api_key,
)


NICHE_HASHTAG_SETS = {
    "finance": {
        "mega": ["#money", "#finance", "#investing", "#rich", "#wealth"],
        "mid": ["#personalfinance", "#stockmarket", "#passiveincome", "#budgeting", "#financetips"],
        "niche": ["#financialliteracy", "#dividends", "#realestateinvesting", "#debtfree", "#frugal"],
    },
    "fitness": {
        "mega": ["#fitness", "#workout", "#gym", "#health", "#fit"],
        "mid": ["#weightloss", "#bodybuilding", "#nutrition", "#exercise", "#gains"],
        "niche": ["#homeworkout", "#calisthenics", "#mealprep", "#fitfam", "#fatloss"],
    },
    "motivation": {
        "mega": ["#motivation", "#success", "#mindset", "#hustle", "#grind"],
        "mid": ["#selfdevelopment", "#entrepreneur", "#goals", "#positivity", "#mentalhealth"],
        "niche": ["#dailymotivation", "#growthmindset", "#selfimprovement", "#personaldevelopment", "#levelup"],
    },
    "luxury": {
        "mega": ["#luxury", "#lifestyle", "#rich", "#wealth", "#expensive"],
        "mid": ["#luxurycar", "#luxurylife", "#millionaire", "#billionaire", "#success"],
        "niche": ["#luxurywatch", "#privatejet", "#yacht", "#luxuryhomes", "#highend"],
    },
    "tech": {
        "mega": ["#tech", "#technology", "#gadgets", "#ai", "#coding"],
        "mid": ["#programming", "#software", "#startup", "#innovation", "#developer"],
        "niche": ["#machinelearning", "#cybersecurity", "#webdev", "#ux", "#3dprinting"],
    },
    "aesthetic": {
        "mega": ["#aesthetic", "#vibes", "#mood", "#chill", "#art"],
        "mid": ["#aestheticvideo", "#darkacademia", "#cottagecore", "#softlife", "#moodboard"],
        "niche": ["#aestheticedit", "#colorgrading", "#cinematography", "#visualstory", "#aestheticoutfit"],
    },
    "pets": {
        "mega": ["#dog", "#cat", "#pets", "#animals", "#cute"],
        "mid": ["#dogsoftiktok", "#catsoftiktok", "#petsofinstagram", "#funnypets", "#animallover"],
        "niche": ["#dogtraining", "#catbehavior", "#exoticpets", "#rescuedog", "#petcare"],
    },
}


def get_niche_hashtags(niche: str) -> dict:
    """Return a curated hashtag set for a specific niche."""
    niche_key = niche.lower()
    if niche_key not in NICHE_HASHTAG_SETS:
        available = list(NICHE_HASHTAG_SETS.keys())
        raise ValueError(f"Niche '{niche}' not found. Available: {available}")

    tags = NICHE_HASHTAG_SETS[niche_key]
    return {
        "niche": niche,
        "hashtag_strategy": {
            "mega_tags": {
                "description": "Massive reach, very competitive (use 1-2 per post)",
                "tags": tags["mega"],
            },
            "mid_tier_tags": {
                "description": "Strong reach, moderate competition (use 2-3 per post)",
                "tags": tags["mid"],
            },
            "niche_tags": {
                "description": "Targeted audience, lower competition (use 2-3 per post)",
                "tags": tags["niche"],
            },
        },
        "recommended_combo": (
            f"{tags['mega'][0]} {tags['mega'][1]} "
            f"{tags['mid'][0]} {tags['mid'][1]} "
            f"{tags['niche'][0]} {tags['niche'][1]} #fyp"
        ),
        "posting_formula": "1-2 mega + 2-3 mid-tier + 2-3 niche + #fyp = optimal mix",
        "available_niches": list(NICHE_HASHTAG_SETS.keys()),
    }


def research_hashtag(tag: str) -> dict:
    """Research a specific hashtag using YouTube search as a proxy for trend strength."""
    # Use YouTube search to gauge content volume and engagement
    tag_clean = tag.lstrip("#")
    try:
        videos = yt_search_videos(query=f"#{tag_clean}", order="viewCount", max_results=10)
        if not videos:
            videos = yt_search_videos(query=tag_clean, order="viewCount", max_results=10)

        total_vids = len(videos)
        tag_counts = extract_hashtags_from_videos(videos)
        related = list(tag_counts.keys())[:10]

        return {
            "hashtag": f"#{tag_clean}",
            "youtube_proxy": {
                "videos_found": total_vids,
                "top_video": videos[0]["title"] if videos else "",
                "top_channel": videos[0]["channel"] if videos else "",
            },
            "related_tags": [f"#{t}" for t in related if t != tag_clean],
            "recommendation": (
                "High-volume tag — competitive but proven reach" if total_vids >= 8
                else "Mid-volume tag — good balance of reach vs competition" if total_vids >= 4
                else "Emerging/niche tag — less competition, targeted audience"
            ),
        }
    except Exception as e:
        return {
            "hashtag": f"#{tag_clean}",
            "error": str(e),
            "fallback": f"Check #{tag_clean} directly on TikTok/YouTube for live volume data.",
        }


def analyze_competitor_hashtags(channel_id: str) -> dict:
    """Analyze what hashtags a YouTube competitor channel's videos use."""
    from cli_anything.social_trends.utils.social_backend import yt_channel_stats
    try:
        # Get recent videos from channel
        import urllib.parse
        import urllib.request
        import json
        from cli_anything.social_trends.utils.social_backend import get_youtube_api_key, YOUTUBE_API_BASE

        params = {
            "part": "snippet",
            "channelId": channel_id,
            "order": "date",
            "type": "video",
            "maxResults": "20",
            "key": get_youtube_api_key(),
        }
        url = f"{YOUTUBE_API_BASE}/search?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url, timeout=15) as resp:
            search_data = json.loads(resp.read().decode())

        video_ids = [
            item.get("id", {}).get("videoId", "")
            for item in search_data.get("items", [])
            if item.get("id", {}).get("videoId")
        ]

        if not video_ids:
            return {"channel_id": channel_id, "error": "No videos found for this channel"}

        # Get video details with tags
        params2 = {
            "part": "snippet,statistics",
            "id": ",".join(video_ids[:20]),
            "key": get_youtube_api_key(),
        }
        url2 = f"{YOUTUBE_API_BASE}/videos?{urllib.parse.urlencode(params2)}"
        with urllib.request.urlopen(url2, timeout=15) as resp2:
            vids_data = json.loads(resp2.read().decode())

        videos = []
        for item in vids_data.get("items", []):
            snip = item.get("snippet", {})
            stats = item.get("statistics", {})
            videos.append({
                "title": snip.get("title", ""),
                "tags": snip.get("tags", []),
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
            })

        tag_counts = extract_hashtags_from_videos(videos)
        total = len(videos)
        scored = [score_hashtag(t, c, total) for t, c in list(tag_counts.items())[:20]]
        scored.sort(key=lambda x: x["score"], reverse=True)

        return {
            "channel_id": channel_id,
            "videos_analyzed": total,
            "top_hashtags": scored[:15],
            "insight": "These are the hashtags your competitor uses most. Focus on mid-tier ones where you can rank.",
        }
    except Exception as e:
        return {"channel_id": channel_id, "error": str(e)}


def suggest_hashtag_combo(niche: str, platform: str = "both") -> dict:
    """Suggest an optimized hashtag combination for posting."""
    niche_data = get_niche_hashtags(niche)
    tags = NICHE_HASHTAG_SETS.get(niche.lower(), {})

    platform_universal = ["#fyp", "#foryou", "#viral", "#trending"]
    yt_universal = ["#youtube", "#youtubevideos", "#youtubeshorts"]
    tt_universal = ["#fyp", "#foryoupage", "#viral", "#tiktok"]

    combo = {
        "niche": niche,
        "platform": platform,
    }

    if platform in ("tiktok", "both"):
        tt_tags = (
            tags.get("mega", [])[:2]
            + tags.get("mid", [])[:3]
            + tags.get("niche", [])[:2]
            + tt_universal[:2]
        )
        combo["tiktok_combo"] = " ".join(tt_tags[:9])
        combo["tiktok_note"] = "Max 9 hashtags for TikTok. Put in caption, not first comment."

    if platform in ("youtube", "both"):
        yt_tags = (
            tags.get("mega", [])[:3]
            + tags.get("mid", [])[:4]
            + tags.get("niche", [])[:3]
            + yt_universal[:2]
        )
        combo["youtube_combo"] = " ".join(yt_tags[:15])
        combo["youtube_note"] = "Add hashtags to video description. First 3 show above title."

    combo["cross_platform_tip"] = (
        "Use the same core niche hashtags across TikTok, Instagram Reels, and YouTube Shorts "
        "to build SEO equity across all platforms simultaneously."
    )
    return combo
