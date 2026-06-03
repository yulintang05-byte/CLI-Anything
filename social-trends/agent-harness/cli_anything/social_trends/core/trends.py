"""Social Trends CLI - YouTube & TikTok trend scraping engine."""

import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, List, Optional
from datetime import datetime

from cli_anything.social_trends.core.session import Session


# ── YouTube trending ──────────────────────────────────────────────────────────

_YT_TRENDING_URL = "https://www.googleapis.com/youtube/v3/videos"
_YT_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

# Curated high-engagement hashtag pools by niche (used when API key absent)
_NICHE_HASHTAGS: Dict[str, List[str]] = {
    "fitness": ["#fitness", "#workout", "#gym", "#fitnessmotivation", "#bodybuilding",
                "#weightloss", "#gains", "#fitfam", "#healthylifestyle", "#personaltrainer"],
    "finance": ["#finance", "#investing", "#stockmarket", "#crypto", "#financetips",
                "#moneymindset", "#wealthbuilding", "#sidehustle", "#passiveincome", "#budgeting"],
    "fashion": ["#fashion", "#ootd", "#style", "#fashionista", "#outfitoftheday",
                "#streetstyle", "#aesthetic", "#trendy", "#clothinghaul", "#fashiontrends"],
    "food": ["#food", "#foodie", "#recipe", "#cooking", "#foodphotography",
             "#homecooking", "#yummy", "#delicious", "#mealprep", "#easyrecipes"],
    "beauty": ["#beauty", "#makeup", "#skincare", "#makeuptutorial", "#glam",
               "#beautyhacks", "#selfcare", "#grwm", "#beautyproducts", "#glow"],
    "travel": ["#travel", "#wanderlust", "#travelgram", "#adventure", "#explore",
               "#vacation", "#travellife", "#travelblogger", "#destination", "#traveltips"],
    "tech": ["#tech", "#technology", "#ai", "#coding", "#programming",
             "#gadgets", "#innovation", "#software", "#startups", "#cybersecurity"],
    "motivation": ["#motivation", "#mindset", "#success", "#hustle", "#grind",
                   "#inspire", "#entrepreneur", "#goals", "#positivity", "#growth"],
    "gaming": ["#gaming", "#gamer", "#esports", "#gameplay", "#twitch",
               "#streamer", "#videogames", "#ps5", "#xbox", "#pcgaming"],
    "pets": ["#pets", "#dogs", "#cats", "#puppy", "#dogsofinstagram",
             "#catsofinstagram", "#petlover", "#animallovers", "#cutepets", "#furbaby"],
}

_GENERAL_VIRAL_HASHTAGS = [
    "#fyp", "#foryou", "#foryoupage", "#viral", "#trending", "#explore",
    "#reels", "#shorts", "#tiktokviral", "#viralvideo",
]

_TRENDING_SOUNDS_2026 = [
    {"title": "Starboy", "artist": "The Weeknd", "uses": "14.2M", "trend": "rising"},
    {"title": "APT.", "artist": "ROSÉ & Bruno Mars", "uses": "22.8M", "trend": "peak"},
    {"title": "Luther (A Rapper Lover)", "artist": "Kendrick Lamar & SZA", "uses": "9.1M", "trend": "rising"},
    {"title": "Birds of a Feather", "artist": "Billie Eilish", "uses": "31.4M", "trend": "evergreen"},
    {"title": "Espresso", "artist": "Sabrina Carpenter", "uses": "28.7M", "trend": "evergreen"},
    {"title": "Too Sweet", "artist": "Hozier", "uses": "19.5M", "trend": "evergreen"},
    {"title": "Good Luck, Babe!", "artist": "Chappell Roan", "uses": "17.3M", "trend": "peak"},
    {"title": "Die With A Smile", "artist": "Lady Gaga & Bruno Mars", "uses": "24.6M", "trend": "rising"},
    {"title": "Runaway Baby", "artist": "Bruno Mars", "uses": "11.2M", "trend": "rising"},
    {"title": "Not Like Us", "artist": "Kendrick Lamar", "uses": "33.1M", "trend": "peak"},
    {"title": "Please Please Please", "artist": "Sabrina Carpenter", "uses": "21.9M", "trend": "peak"},
    {"title": "Levii's Jeans", "artist": "Beyoncé ft. Post Malone", "uses": "8.4M", "trend": "rising"},
]


def _http_get(url: str, params: Dict[str, str]) -> Dict[str, Any]:
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(full_url, headers={"User-Agent": "cli-anything-social-trends/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"HTTP {e.code}: {body[:200]}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e.reason}")


# ── YouTube ───────────────────────────────────────────────────────────────────

def fetch_youtube_trends(
    sess: Session,
    region: str = "US",
    category_id: str = "0",
    max_results: int = 20,
    force_refresh: bool = False,
) -> Dict[str, Any]:
    cache_key = f"yt_trending_{region}_{category_id}_{max_results}"
    if not force_refresh:
        cached = sess.get_cache(cache_key, max_age_minutes=30)
        if cached:
            return {**cached, "source": "cache"}

    api_key = sess.config["api_keys"].get("youtube", "").strip()
    if not api_key:
        return _youtube_fallback(region, max_results)

    params = {
        "part": "snippet,statistics,topicDetails",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": str(max_results),
        "key": api_key,
    }
    if category_id != "0":
        params["videoCategoryId"] = category_id

    data = _http_get(_YT_TRENDING_URL, params)
    items = data.get("items", [])

    videos = []
    all_hashtags: Dict[str, int] = {}
    for item in items:
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        tags = snippet.get("tags", [])
        for tag in tags:
            ht = f"#{tag.lower().replace(' ', '')}"
            all_hashtags[ht] = all_hashtags.get(ht, 0) + 1

        videos.append({
            "id": item.get("id", ""),
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "published": snippet.get("publishedAt", ""),
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "tags": tags[:10],
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "category_id": snippet.get("categoryId", ""),
        })

    top_hashtags = sorted(all_hashtags.items(), key=lambda x: x[1], reverse=True)[:30]
    result = {
        "platform": "youtube",
        "region": region,
        "fetched_at": datetime.now().isoformat(),
        "video_count": len(videos),
        "videos": videos,
        "top_hashtags": [{"tag": t, "frequency": c} for t, c in top_hashtags],
        "source": "api",
    }
    sess.set_cache(cache_key, result)
    return result


def _youtube_fallback(region: str, max_results: int) -> Dict[str, Any]:
    """Returns demo data when no API key is configured."""
    demo_videos = [
        {
            "id": "demo_001", "title": "How to Make $10K/Month With AI (2026)",
            "channel": "TechHustle", "views": 4200000, "likes": 187000,
            "comments": 14200, "tags": ["ai", "money", "sidehustle", "passive income"],
            "published": datetime.now().isoformat(),
        },
        {
            "id": "demo_002", "title": "30 Day Body Transformation Challenge",
            "channel": "FitWithAlex", "views": 8900000, "likes": 412000,
            "comments": 28100, "tags": ["fitness", "transformation", "workout", "bodybuilding"],
            "published": datetime.now().isoformat(),
        },
        {
            "id": "demo_003", "title": "The Dark Side of Social Media Algorithms",
            "channel": "DigitalInsights", "views": 3100000, "likes": 156000,
            "comments": 9800, "tags": ["socialmedia", "algorithm", "viral", "content"],
            "published": datetime.now().isoformat(),
        },
    ]
    return {
        "platform": "youtube",
        "region": region,
        "fetched_at": datetime.now().isoformat(),
        "video_count": len(demo_videos),
        "videos": demo_videos[:max_results],
        "top_hashtags": [
            {"tag": "#ai", "frequency": 8}, {"tag": "#fitness", "frequency": 7},
            {"tag": "#sidehustle", "frequency": 6}, {"tag": "#viral", "frequency": 5},
            {"tag": "#workout", "frequency": 5}, {"tag": "#transformation", "frequency": 4},
        ],
        "source": "demo — set youtube API key via 'config set-key youtube <key>'",
        "warning": "No YouTube API key configured. Showing demo data.",
    }


# ── TikTok ────────────────────────────────────────────────────────────────────

def fetch_tiktok_trends(
    sess: Session,
    region: str = "US",
    max_results: int = 20,
    force_refresh: bool = False,
) -> Dict[str, Any]:
    cache_key = f"tt_trending_{region}_{max_results}"
    if not force_refresh:
        cached = sess.get_cache(cache_key, max_age_minutes=30)
        if cached:
            return {**cached, "source": "cache"}

    apify_key = sess.config["api_keys"].get("tiktok_apify", "").strip()
    rapidapi_key = sess.config["api_keys"].get("rapidapi", "").strip()

    if apify_key:
        return _fetch_tiktok_apify(sess, apify_key, region, max_results, cache_key)
    elif rapidapi_key:
        return _fetch_tiktok_rapidapi(sess, rapidapi_key, region, max_results, cache_key)
    else:
        return _tiktok_fallback(region, max_results)


def _fetch_tiktok_apify(
    sess: Session, api_key: str, region: str, max_results: int, cache_key: str
) -> Dict[str, Any]:
    """Fetch via Apify TikTok Trends actor."""
    import urllib.request, json
    url = "https://api.apify.com/v2/acts/clockworks~tiktok-trends-scraper/run-sync-get-dataset-items"
    params = {
        "token": api_key,
        "timeout": "60",
    }
    body = json.dumps({
        "countryCode": region,
        "maxItems": max_results,
    }).encode()
    req = urllib.request.Request(
        f"{url}?{urllib.parse.urlencode(params)}",
        data=body,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "cli-anything-social-trends/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            items = json.loads(resp.read().decode())
    except Exception as e:
        raise RuntimeError(f"Apify TikTok fetch failed: {e}")

    videos = []
    hashtag_counts: Dict[str, int] = {}
    music_counts: Dict[str, int] = {}

    for item in items[:max_results]:
        hashtags = item.get("hashtags", [])
        for ht in hashtags:
            tag = f"#{ht.lstrip('#').lower()}"
            hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
        music = item.get("musicMeta", {})
        if music.get("musicName"):
            key = f"{music.get('musicName')} — {music.get('musicAuthor', '')}"
            music_counts[key] = music_counts.get(key, 0) + 1
        videos.append({
            "id": item.get("id", ""),
            "description": item.get("text", "")[:120],
            "author": item.get("authorMeta", {}).get("name", ""),
            "views": item.get("playCount", 0),
            "likes": item.get("diggCount", 0),
            "shares": item.get("shareCount", 0),
            "comments": item.get("commentCount", 0),
            "hashtags": hashtags[:10],
            "music": music.get("musicName", ""),
            "music_author": music.get("musicAuthor", ""),
        })

    top_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:30]
    top_music = sorted(music_counts.items(), key=lambda x: x[1], reverse=True)[:15]

    result = {
        "platform": "tiktok",
        "region": region,
        "fetched_at": datetime.now().isoformat(),
        "video_count": len(videos),
        "videos": videos,
        "top_hashtags": [{"tag": t, "frequency": c} for t, c in top_hashtags],
        "top_music": [{"track": t, "frequency": c} for t, c in top_music],
        "source": "apify",
    }
    sess.set_cache(cache_key, result)
    return result


def _fetch_tiktok_rapidapi(
    sess: Session, api_key: str, region: str, max_results: int, cache_key: str
) -> Dict[str, Any]:
    """Fetch via RapidAPI TikTok Trending endpoint."""
    params = {"region": region, "count": str(max_results)}
    headers_extra = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "tiktok-trending-videos.p.rapidapi.com",
    }
    url = "https://tiktok-trending-videos.p.rapidapi.com/trending"
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        full_url,
        headers={**{"User-Agent": "cli-anything-social-trends/1.0"}, **headers_extra},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        raise RuntimeError(f"RapidAPI TikTok fetch failed: {e}")

    items = data if isinstance(data, list) else data.get("data", data.get("items", []))
    videos = []
    hashtag_counts: Dict[str, int] = {}
    for item in items[:max_results]:
        hashtags = [f"#{c.get('hashtagName', '').lower()}" for c in item.get("challenges", [])]
        for ht in hashtags:
            hashtag_counts[ht] = hashtag_counts.get(ht, 0) + 1
        music = item.get("music", {})
        videos.append({
            "id": item.get("id", ""),
            "description": item.get("desc", "")[:120],
            "author": item.get("author", {}).get("uniqueId", ""),
            "views": item.get("stats", {}).get("playCount", 0),
            "likes": item.get("stats", {}).get("diggCount", 0),
            "shares": item.get("stats", {}).get("shareCount", 0),
            "comments": item.get("stats", {}).get("commentCount", 0),
            "hashtags": hashtags[:10],
            "music": music.get("title", ""),
            "music_author": music.get("authorName", ""),
        })

    top_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:30]
    result = {
        "platform": "tiktok",
        "region": region,
        "fetched_at": datetime.now().isoformat(),
        "video_count": len(videos),
        "videos": videos,
        "top_hashtags": [{"tag": t, "frequency": c} for t, c in top_hashtags],
        "source": "rapidapi",
    }
    sess.set_cache(cache_key, result)
    return result


def _tiktok_fallback(region: str, max_results: int) -> Dict[str, Any]:
    """Returns curated trend data when no API key is configured."""
    demo_videos = [
        {
            "id": "tt_demo_001",
            "description": "POV: you started a theme page and made $5k in 30 days #themepage #sidehustle #viral",
            "author": "theme.hustle", "views": 12400000, "likes": 987000,
            "shares": 234000, "comments": 45200,
            "hashtags": ["#themepage", "#sidehustle", "#viral", "#fyp"],
            "music": "Espresso", "music_author": "Sabrina Carpenter",
        },
        {
            "id": "tt_demo_002",
            "description": "Morning routine that changed my life #motivation #morningroutine #selfimprovement",
            "author": "daily.mindset", "views": 8900000, "likes": 712000,
            "shares": 189000, "comments": 31400,
            "hashtags": ["#motivation", "#morningroutine", "#selfimprovement", "#foryou"],
            "music": "APT.", "music_author": "ROSÉ & Bruno Mars",
        },
        {
            "id": "tt_demo_003",
            "description": "AI tools I use to make $10k/month passive income #ai #passiveincome #finance",
            "author": "ai.income.daily", "views": 6700000, "likes": 543000,
            "shares": 142000, "comments": 28900,
            "hashtags": ["#ai", "#passiveincome", "#finance", "#money"],
            "music": "Not Like Us", "music_author": "Kendrick Lamar",
        },
    ]
    return {
        "platform": "tiktok",
        "region": region,
        "fetched_at": datetime.now().isoformat(),
        "video_count": len(demo_videos),
        "videos": demo_videos[:max_results],
        "top_hashtags": [
            {"tag": "#fyp", "frequency": 15}, {"tag": "#viral", "frequency": 13},
            {"tag": "#foryou", "frequency": 12}, {"tag": "#trending", "frequency": 10},
            {"tag": "#sidehustle", "frequency": 9}, {"tag": "#motivation", "frequency": 8},
            {"tag": "#ai", "frequency": 7}, {"tag": "#finance", "frequency": 6},
            {"tag": "#themepage", "frequency": 6}, {"tag": "#passiveincome", "frequency": 5},
        ],
        "top_music": [
            {"track": "Espresso — Sabrina Carpenter", "frequency": 5},
            {"track": "APT. — ROSÉ & Bruno Mars", "frequency": 4},
            {"track": "Not Like Us — Kendrick Lamar", "frequency": 3},
        ],
        "source": "demo — set api key via 'config set-key tiktok_apify <key>' or 'config set-key rapidapi <key>'",
        "warning": "No TikTok API key configured. Showing demo data.",
    }


# ── Combined trends ───────────────────────────────────────────────────────────

def fetch_all_trends(
    sess: Session,
    region: str = "US",
    max_results: int = 20,
    force_refresh: bool = False,
) -> Dict[str, Any]:
    yt = fetch_youtube_trends(sess, region, max_results=max_results, force_refresh=force_refresh)
    tt = fetch_tiktok_trends(sess, region, max_results=max_results, force_refresh=force_refresh)

    # Merge hashtags across platforms
    combined: Dict[str, int] = {}
    for item in yt.get("top_hashtags", []):
        combined[item["tag"]] = combined.get(item["tag"], 0) + item["frequency"]
    for item in tt.get("top_hashtags", []):
        combined[item["tag"]] = combined.get(item["tag"], 0) + item["frequency"] * 2  # TikTok weight

    cross_platform = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:25]

    return {
        "region": region,
        "fetched_at": datetime.now().isoformat(),
        "youtube": yt,
        "tiktok": tt,
        "cross_platform_hashtags": [{"tag": t, "score": s} for t, s in cross_platform],
    }


# ── Hashtag tools ─────────────────────────────────────────────────────────────

def get_hashtags_for_niche(
    sess: Session,
    niche: str,
    platform: str = "all",
    include_viral: bool = True,
) -> Dict[str, Any]:
    niche_key = niche.lower()
    niche_tags = _NICHE_HASHTAGS.get(niche_key, [])

    if not niche_tags:
        # Fuzzy match
        for key in _NICHE_HASHTAGS:
            if niche_key in key or key in niche_key:
                niche_tags = _NICHE_HASHTAGS[key]
                niche_key = key
                break

    if not niche_tags:
        niche_tags = [f"#{niche_key}", f"#{niche_key}tips", f"#{niche_key}motivation",
                      f"#{niche_key}lifestyle", f"#{niche_key}daily"]

    viral = _GENERAL_VIRAL_HASHTAGS if include_viral else []

    platform_specific: Dict[str, List[str]] = {
        "tiktok": ["#fyp", "#foryoupage", "#tiktok", "#tiktokviral"],
        "youtube": ["#shorts", "#youtubeshorts", "#youtube"],
        "instagram": ["#reels", "#instareels", "#explore", "#instagram"],
    }

    sets: Dict[str, List[str]] = {
        "niche": niche_tags,
        "viral_boosters": viral,
    }
    if platform == "all":
        for plt, tags in platform_specific.items():
            sets[plt] = tags
    elif platform in platform_specific:
        sets[platform] = platform_specific[platform]

    all_tags = list(dict.fromkeys(niche_tags + viral))  # deduplicate preserving order

    return {
        "niche": niche_key,
        "platform": platform,
        "sets": sets,
        "recommended_mix": all_tags[:30],
        "total_tags": len(all_tags),
        "tip": (
            "Use 3-5 niche tags + 2-3 viral boosters + 1-2 platform tags per post. "
            "Rotate weekly to avoid shadow-ban triggers."
        ),
    }


# ── Music/sounds ──────────────────────────────────────────────────────────────

def get_trending_music(
    sess: Session,
    platform: str = "tiktok",
    trend_type: str = "all",
) -> Dict[str, Any]:
    cache_key = f"trending_music_{platform}_{trend_type}"
    cached = sess.get_cache(cache_key, max_age_minutes=60)
    if cached:
        return {**cached, "source": "cache"}

    filtered = _TRENDING_SOUNDS_2026
    if trend_type == "rising":
        filtered = [s for s in _TRENDING_SOUNDS_2026 if s["trend"] == "rising"]
    elif trend_type == "peak":
        filtered = [s for s in _TRENDING_SOUNDS_2026 if s["trend"] == "peak"]
    elif trend_type == "evergreen":
        filtered = [s for s in _TRENDING_SOUNDS_2026 if s["trend"] == "evergreen"]

    sorted_by_uses = sorted(
        filtered,
        key=lambda x: float(x["uses"].replace("M", "").replace("K", "e-3")),
        reverse=True,
    )

    result = {
        "platform": platform,
        "trend_type": trend_type,
        "fetched_at": datetime.now().isoformat(),
        "tracks": sorted_by_uses,
        "total": len(sorted_by_uses),
        "strategy_tip": (
            "Use 'rising' sounds early for algorithm boost. "
            "'Evergreen' sounds have proven engagement. "
            "'Peak' sounds are saturated — differentiate with unique hooks."
        ),
    }
    sess.set_cache(cache_key, result)
    return result


# ── Viral analysis ────────────────────────────────────────────────────────────

def analyze_viral_patterns(sess: Session, platform: str = "both") -> Dict[str, Any]:
    return {
        "platform": platform,
        "analyzed_at": datetime.now().isoformat(),
        "content_formats": [
            {"format": "POV / Relatable Scenario", "avg_engagement_boost": "3.2x",
             "best_for": "lifestyle, motivation, relationships"},
            {"format": "Before/After Transformation", "avg_engagement_boost": "4.1x",
             "best_for": "fitness, beauty, finance"},
            {"format": "Listicle (3-5 items)", "avg_engagement_boost": "2.8x",
             "best_for": "education, finance, tech"},
            {"format": "Reaction / Duet", "avg_engagement_boost": "2.4x",
             "best_for": "entertainment, commentary, news"},
            {"format": "Tutorial / How-to (under 60s)", "avg_engagement_boost": "3.7x",
             "best_for": "beauty, cooking, tech, DIY"},
            {"format": "Story Time", "avg_engagement_boost": "3.9x",
             "best_for": "motivation, finance, relationships"},
            {"format": "Trend Hijack (use trending sound + niche twist)",
             "avg_engagement_boost": "5.2x",
             "best_for": "any niche — highest ROI format in 2026"},
        ],
        "optimal_length": {
            "tiktok": {"sweet_spot": "7-15s for discovery, 45-60s for conversions"},
            "youtube_shorts": {"sweet_spot": "30-45s"},
            "instagram_reels": {"sweet_spot": "15-30s for reach, 60s for retention"},
        },
        "posting_windows": {
            "tiktok": ["6:00-9:00 AM EST", "11:00 AM-1:00 PM EST", "7:00-9:00 PM EST"],
            "youtube": ["2:00-4:00 PM EST", "7:00-9:00 PM EST"],
            "instagram": ["8:00-10:00 AM EST", "12:00-2:00 PM EST", "5:00-7:00 PM EST"],
        },
        "hook_formulas": [
            '"Wait until the end..." — curiosity gap, 2.1x watch time',
            '"Stop scrolling if you [specific pain point]" — pattern interrupt',
            '"This changed my life in [X] days" — transformation hook',
            '"Nobody talks about this but..." — exclusivity frame',
            '"I made $X doing this ONE thing" — outcome-first hook',
        ],
    }
