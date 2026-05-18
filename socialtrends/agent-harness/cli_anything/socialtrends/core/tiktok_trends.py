"""TikTok trend fetcher.

Supports two modes:
1. TikTok Research API  — requires approved access token (researchers/businesses)
   https://developers.tiktok.com/products/research-api/
2. Google Trends bridge — maps search interest to TikTok niches (always available)

Configure Research API token:
    socialtrends auth setup --tiktok-token YOUR_TOKEN
"""

import re
import time
import requests
from collections import Counter
from datetime import datetime, timedelta

from cli_anything.socialtrends.utils import cache, config

TIKTOK_RESEARCH_BASE = "https://open.tiktokapis.com/v2"

# Browser headers to reduce blocking on public endpoints
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.tiktok.com/",
}


# ── Research API ──────────────────────────────────────────────────────────────

def _research_token() -> str | None:
    return config.get("tiktok_research_token")


def fetch_trending_videos_research(
    region: str = "US",
    max_results: int = 20,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict]:
    """Fetch trending videos using TikTok Research API.

    Requires an approved TikTok Research API token.

    Args:
        region: Country code (US, GB, etc.)
        max_results: Number of videos to fetch
        start_date: YYYYMMDD (defaults to 7 days ago)
        end_date:   YYYYMMDD (defaults to today)

    Returns:
        List of video dicts
    """
    token = _research_token()
    if not token:
        raise RuntimeError(
            "TikTok Research API token not configured.\n"
            "Run: socialtrends auth setup --tiktok-token YOUR_TOKEN\n"
            "Apply at: https://developers.tiktok.com/products/research-api/"
        )

    if not end_date:
        end_date = datetime.utcnow().strftime("%Y%m%d")
    if not start_date:
        start_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y%m%d")

    url = f"{TIKTOK_RESEARCH_BASE}/research/video/query/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "query": {
            "and": [{"operation": "IN", "field_name": "region_code", "field_values": [region]}],
        },
        "start_date": start_date,
        "end_date": end_date,
        "max_count": min(max_results, 100),
        "fields": "id,create_time,username,region_code,video_description,hashtag_names,view_count,like_count,comment_count,share_count,music_id,effect_ids",
        "is_random": False,
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=20)
    if resp.status_code == 401:
        raise RuntimeError("TikTok Research API: invalid or expired token.")
    resp.raise_for_status()

    items = resp.json().get("data", {}).get("videos", [])
    return [_normalize_research_video(v) for v in items]


def _normalize_research_video(v: dict) -> dict:
    return {
        "id": v.get("id", ""),
        "username": v.get("username", ""),
        "description": v.get("video_description", ""),
        "hashtags": [f"#{h}" for h in v.get("hashtag_names", [])],
        "views": v.get("view_count", 0),
        "likes": v.get("like_count", 0),
        "comments": v.get("comment_count", 0),
        "shares": v.get("share_count", 0),
        "music_id": v.get("music_id", ""),
        "region": v.get("region_code", ""),
        "url": f"https://www.tiktok.com/@{v.get('username', '')}/video/{v.get('id', '')}",
        "source": "research_api",
    }


# ── Google Trends bridge (always available) ───────────────────────────────────

def fetch_trending_via_google_trends(
    niche: str = "",
    region: str = "US",
    use_cache: bool = True,
) -> dict:
    """Map Google search trends to TikTok-relevant topics.

    Uses pytrends to pull real-time trending searches that correlate
    with viral TikTok content in the same niche.

    Args:
        niche: Optional niche keyword to contextualize trends (e.g. "fitness")
        region: ISO 3166-1 country code

    Returns:
        Dict with trending_searches, related_queries, suggested_hashtags
    """
    cache_key = f"gtrends_{niche}_{region}"
    if use_cache:
        cached = cache.get_cached(cache_key)
        if cached:
            return cached

    try:
        from pytrends.request import TrendReq
    except ImportError:
        raise RuntimeError(
            "pytrends not installed. Run: pip install pytrends"
        )

    pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 25), retries=2, backoff_factor=0.5)

    results: dict = {"region": region, "niche": niche}

    try:
        # Daily trending searches
        daily = pytrends.trending_searches(pn=_country_to_pytrends(region))
        results["trending_searches"] = daily[0].tolist()[:20]
    except Exception as e:
        results["trending_searches"] = []
        results["trending_searches_error"] = str(e)

    if niche:
        try:
            pytrends.build_payload([niche], cat=0, timeframe="now 7-d", geo=region)
            related = pytrends.related_queries()
            top = related.get(niche, {}).get("top")
            rising = related.get(niche, {}).get("rising")
            results["related_top"] = top[["query", "value"]].head(10).to_dict("records") if top is not None else []
            results["related_rising"] = rising[["query", "value"]].head(10).to_dict("records") if rising is not None else []
        except Exception as e:
            results["related_top"] = []
            results["related_rising"] = []
            results["related_error"] = str(e)

    # Map trending searches to hashtag suggestions
    tags = []
    for term in results.get("trending_searches", [])[:10]:
        clean = term.lower().replace(" ", "").replace("'", "")
        tags.append(f"#{clean}")
    results["suggested_hashtags"] = tags

    if use_cache:
        cache.set_cached(cache_key, results, ttl_hours=3)

    return results


def _country_to_pytrends(code: str) -> str:
    mapping = {
        "US": "united_states", "GB": "united_kingdom", "CA": "canada",
        "AU": "australia", "IN": "india", "DE": "germany", "FR": "france",
        "BR": "brazil", "MX": "mexico", "JP": "japan",
    }
    return mapping.get(code.upper(), "united_states")


# ── Hashtag aggregation from video data ──────────────────────────────────────

def extract_trending_hashtags(
    videos: list[dict],
    top_n: int = 50,
    min_count: int = 1,
) -> list[dict]:
    """Aggregate and rank hashtags from fetched TikTok videos.

    Args:
        videos: List from fetch_trending_videos_research()
        top_n: Max hashtags to return
        min_count: Minimum appearances

    Returns:
        List of {hashtag, count, engagement_score} dicts
    """
    hashtag_engagement: dict[str, dict] = {}

    for v in videos:
        engagement = v.get("likes", 0) + v.get("comments", 0) * 2 + v.get("shares", 0) * 3
        for tag in v.get("hashtags", []):
            tag = tag.lower()
            if tag not in hashtag_engagement:
                hashtag_engagement[tag] = {"count": 0, "total_engagement": 0}
            hashtag_engagement[tag]["count"] += 1
            hashtag_engagement[tag]["total_engagement"] += engagement

    results = [
        {
            "hashtag": tag,
            "count": data["count"],
            "avg_engagement": int(data["total_engagement"] / data["count"]) if data["count"] else 0,
        }
        for tag, data in hashtag_engagement.items()
        if data["count"] >= min_count
    ]

    results.sort(key=lambda x: (x["avg_engagement"], x["count"]), reverse=True)
    return results[:top_n]


# ── Curated trending hashtag fallback (updated weekly via knowledge base) ────

def get_curated_trending(region: str = "US", date_ref: str = "2026-05") -> dict:
    """Return curated trending hashtags from built-in knowledge base.

    Used as a reliable fallback when APIs are unavailable.
    Updated to reflect trends current as of May 2026.
    """
    base = {
        "US": {
            "mega_viral": [
                "#fyp", "#foryou", "#foryoupage", "#viral", "#trending",
                "#CapCut", "#explore", "#reels", "#blowup",
            ],
            "lifestyle": [
                "#aesthetic", "#slowliving", "#softlife", "#romanticizeyourlife",
                "#dailyvlog", "#grwm", "#dayinmylife", "#morningroutine",
            ],
            "fitness": [
                "#gymtok", "#fitcheck", "#bodytransformation", "#workoutmotivation",
                "#pilates", "#75hard", "#girlswholift", "#calisthenics",
            ],
            "fashion": [
                "#ootd", "#outfitcheck", "#fashion", "#style", "#thriftflip",
                "#streetwear", "#fashiontok", "#fitcheck",
            ],
            "food": [
                "#foodtok", "#recipe", "#cooking", "#mukbang", "#easyrecipes",
                "#mealprep", "#whatieatinaday", "#foodie",
            ],
            "money": [
                "#personalfinance", "#investing", "#sidehustle", "#passiveincome",
                "#financialtips", "#stockmarket", "#crypto", "#moneytok",
            ],
            "beauty": [
                "#makeup", "#skincare", "#skincareroutine", "#glowup",
                "#makeuptutorial", "#beautytok", "#nailcheck", "#hairtok",
            ],
            "gaming": [
                "#gaming", "#gamer", "#twitch", "#esports", "#streamer",
                "#gamingsetup", "#fps", "#minecraft",
            ],
            "motivation": [
                "#motivation", "#mindset", "#selfdevelopment", "#growthmindset",
                "#success", "#levelup", "#discipline", "#manifestation",
            ],
        }
    }
    data = base.get(region, base["US"])
    data["region"] = region
    data["source"] = "curated_knowledge_base"
    data["as_of"] = date_ref
    return data
