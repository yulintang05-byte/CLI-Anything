"""Trend scraping — YouTube Data API v3 + TikTok web API.

Fetches trending videos, hashtags, and music from both platforms.
Outputs structured dicts suitable for JSON serialization.

YouTube: requires a YouTube Data API v3 key (free tier, 10K units/day).
TikTok:  uses TikTok's undocumented web API endpoints; pass a valid
         sessionid cookie for authenticated requests (higher rate limits).
"""

import re
import json
import time
import hashlib
import datetime
from collections import Counter
from typing import Optional

import requests

# ── Constants ─────────────────────────────────────────────────────────────────

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

YOUTUBE_CATEGORIES = {
    "0":  "All",
    "1":  "Film & Animation",
    "2":  "Autos & Vehicles",
    "10": "Music",
    "15": "Pets & Animals",
    "17": "Sports",
    "19": "Travel & Events",
    "20": "Gaming",
    "22": "People & Blogs",
    "23": "Comedy",
    "24": "Entertainment",
    "25": "News & Politics",
    "26": "How-to & Style",
    "27": "Education",
    "28": "Science & Technology",
    "29": "Nonprofits & Activism",
}

TIKTOK_WEB_BASE = "https://www.tiktok.com"
TIKTOK_API_BASE = "https://www.tiktok.com/api"

TIKTOK_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
    "Origin": "https://www.tiktok.com",
}

_HASHTAG_RE = re.compile(r"#(\w+)", re.UNICODE)


# ── YouTube ───────────────────────────────────────────────────────────────────

def fetch_youtube_trending(
    api_key: str,
    region: str = "US",
    category: str = "0",
    max_results: int = 20,
) -> dict:
    """Fetch trending YouTube videos and extract hashtags + music cues.

    Args:
        api_key: YouTube Data API v3 key.
        region: ISO 3166-1 alpha-2 country code (e.g. 'US', 'GB', 'BR').
        category: Video category ID (see YOUTUBE_CATEGORIES). '0' = all.
        max_results: Number of videos to fetch (max 50 per request).

    Returns:
        Dict with keys:
            platform, region, category_name, fetched_at,
            trending_videos, trending_hashtags, trending_topics,
            total_fetched.
    """
    params = {
        "key": api_key,
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region,
        "videoCategoryId": category,
        "maxResults": min(max_results, 50),
    }
    resp = requests.get(
        f"{YOUTUBE_API_BASE}/videos", params=params, timeout=20
    )
    resp.raise_for_status()
    data = resp.json()

    if "error" in data:
        err = data["error"]
        raise RuntimeError(
            f"YouTube API error {err.get('code')}: {err.get('message')}"
        )

    videos = []
    all_hashtags: list[str] = []
    title_words: list[str] = []

    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})

        title = snippet.get("title", "")
        description = snippet.get("description", "")
        tags = snippet.get("tags", [])

        # Extract inline hashtags from title + description
        inline = _HASHTAG_RE.findall(title + " " + description)
        inline_lower = [h.lower() for h in inline]

        # Normalise tag list
        tag_lower = [t.lower().replace(" ", "") for t in tags if t]

        all_hashtags.extend(inline_lower)
        all_hashtags.extend(tag_lower)

        # Collect plain title words for topic detection
        words = re.findall(r"\b[a-zA-Z]{4,}\b", title.lower())
        title_words.extend(words)

        view_count = _safe_int(stats.get("viewCount", 0))
        like_count = _safe_int(stats.get("likeCount", 0))
        comment_count = _safe_int(stats.get("commentCount", 0))

        videos.append({
            "id": item.get("id"),
            "title": title,
            "channel": snippet.get("channelTitle", ""),
            "published_at": snippet.get("publishedAt", ""),
            "category_id": snippet.get("categoryId", ""),
            "view_count": view_count,
            "like_count": like_count,
            "comment_count": comment_count,
            "engagement_rate": _engagement_rate(view_count, like_count, comment_count),
            "hashtags": inline_lower[:10],
            "tags": tag_lower[:10],
            "thumbnail": (
                snippet.get("thumbnails", {}).get("high", {}).get("url", "")
            ),
            "url": f"https://www.youtube.com/watch?v={item.get('id')}",
        })

    # Top hashtags across all videos
    hashtag_counts = Counter(all_hashtags)
    trending_hashtags = [
        {"hashtag": f"#{tag}", "count": cnt}
        for tag, cnt in hashtag_counts.most_common(25)
        if len(tag) > 1
    ]

    # Top trending topic words (exclude common stopwords)
    _STOPWORDS = {
        "this", "that", "with", "from", "they", "have", "will", "your",
        "what", "when", "were", "been", "more", "than", "also", "some",
        "just", "like", "there", "about", "which", "their", "would",
    }
    word_counts = Counter(w for w in title_words if w not in _STOPWORDS)
    trending_topics = [
        {"topic": word, "count": cnt}
        for word, cnt in word_counts.most_common(15)
    ]

    return {
        "platform": "youtube",
        "region": region,
        "category": category,
        "category_name": YOUTUBE_CATEGORIES.get(category, "Unknown"),
        "fetched_at": _now_iso(),
        "trending_videos": videos,
        "trending_hashtags": trending_hashtags,
        "trending_topics": trending_topics,
        "total_fetched": len(videos),
    }


def fetch_youtube_search_trending(
    api_key: str,
    query: str,
    region: str = "US",
    max_results: int = 20,
    order: str = "viewCount",
) -> dict:
    """Search YouTube for content around a trending keyword.

    Args:
        api_key: YouTube Data API v3 key.
        query: Search query (hashtag, topic, keyword).
        region: Region code.
        max_results: Number of results.
        order: 'viewCount', 'relevance', 'date', 'rating'.

    Returns:
        Dict with matching videos and extracted hashtags.
    """
    params = {
        "key": api_key,
        "part": "snippet",
        "q": query,
        "type": "video",
        "regionCode": region,
        "maxResults": min(max_results, 50),
        "order": order,
        "safeSearch": "none",
        "videoDuration": "short",  # Prioritise short-form (Shorts-friendly)
    }
    resp = requests.get(
        f"{YOUTUBE_API_BASE}/search", params=params, timeout=20
    )
    resp.raise_for_status()
    data = resp.json()

    if "error" in data:
        err = data["error"]
        raise RuntimeError(
            f"YouTube API error {err.get('code')}: {err.get('message')}"
        )

    videos = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        vid_id = item.get("id", {}).get("videoId", "")
        title = snippet.get("title", "")
        hashtags = _HASHTAG_RE.findall(title + " " + snippet.get("description", ""))
        videos.append({
            "id": vid_id,
            "title": title,
            "channel": snippet.get("channelTitle", ""),
            "published_at": snippet.get("publishedAt", ""),
            "hashtags": [h.lower() for h in hashtags],
            "thumbnail": (
                snippet.get("thumbnails", {}).get("high", {}).get("url", "")
            ),
            "url": f"https://www.youtube.com/watch?v={vid_id}" if vid_id else "",
        })

    return {
        "platform": "youtube",
        "query": query,
        "region": region,
        "order": order,
        "fetched_at": _now_iso(),
        "results": videos,
        "total_fetched": len(videos),
    }


# ── TikTok ────────────────────────────────────────────────────────────────────

def fetch_tiktok_trending_hashtags(
    session_cookie: str = "",
    count: int = 20,
) -> dict:
    """Fetch trending hashtags from TikTok's discover endpoint.

    Args:
        session_cookie: TikTok sessionid cookie value (optional).
                        Without it, public discover data is returned.
        count: Number of hashtags to fetch.

    Returns:
        Dict with trending hashtags and challenge info.
    """
    cookies: dict = {}
    if session_cookie:
        cookies["sessionid"] = session_cookie

    params = {
        "discoverType": "0",
        "needItemList": "false",
        "keyWord": "",
        "offset": "0",
        "count": str(count),
        "useRecommend": "false",
        "language": "en",
    }

    try:
        resp = requests.get(
            f"{TIKTOK_API_BASE}/discover/type/",
            params=params,
            headers=TIKTOK_HEADERS,
            cookies=cookies,
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.HTTPError as exc:
        raise RuntimeError(
            f"TikTok API returned HTTP {exc.response.status_code}. "
            "You may need to supply a valid sessionid cookie."
        ) from exc
    except requests.RequestException as exc:
        raise RuntimeError(f"TikTok request failed: {exc}") from exc

    hashtags = []
    for item in data.get("challengeInfoList", []):
        challenge = item.get("challengeInfo", {}).get("challenge", {})
        stats = item.get("challengeInfo", {}).get("stats", {})
        title = challenge.get("title", "")
        if title:
            hashtags.append({
                "hashtag": f"#{title}",
                "video_count": _safe_int(stats.get("videoCount", 0)),
                "view_count": _safe_int(stats.get("viewCount", 0)),
                "description": challenge.get("desc", ""),
            })

    # If API returned nothing, fallback to known stable TikTok discover page
    if not hashtags:
        hashtags = _scrape_tiktok_discover_fallback(session_cookie, count)

    return {
        "platform": "tiktok",
        "type": "hashtags",
        "fetched_at": _now_iso(),
        "trending_hashtags": hashtags,
        "total_fetched": len(hashtags),
    }


def fetch_tiktok_trending_music(
    session_cookie: str = "",
    count: int = 20,
) -> dict:
    """Fetch trending music/sounds from TikTok.

    Args:
        session_cookie: TikTok sessionid cookie value (optional).
        count: Number of music items to fetch.

    Returns:
        Dict with trending audio tracks.
    """
    cookies: dict = {}
    if session_cookie:
        cookies["sessionid"] = session_cookie

    params = {
        "discoverType": "1",
        "needItemList": "false",
        "keyWord": "",
        "offset": "0",
        "count": str(count),
        "useRecommend": "false",
        "language": "en",
    }

    try:
        resp = requests.get(
            f"{TIKTOK_API_BASE}/discover/type/",
            params=params,
            headers=TIKTOK_HEADERS,
            cookies=cookies,
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.HTTPError as exc:
        raise RuntimeError(
            f"TikTok API returned HTTP {exc.response.status_code}."
        ) from exc
    except requests.RequestException as exc:
        raise RuntimeError(f"TikTok request failed: {exc}") from exc

    music_list = []
    for item in data.get("musicInfoList", []):
        music = item.get("music", {})
        stats = item.get("stats", {})
        music_list.append({
            "id": music.get("id", ""),
            "title": music.get("title", ""),
            "author": music.get("authorName", ""),
            "album": music.get("album", ""),
            "duration": music.get("duration", 0),
            "play_url": music.get("playUrl", ""),
            "cover_url": music.get("coverMedium", ""),
            "video_count": _safe_int(stats.get("videoCount", 0)),
            "is_original": music.get("original", False),
        })

    return {
        "platform": "tiktok",
        "type": "music",
        "fetched_at": _now_iso(),
        "trending_music": music_list,
        "total_fetched": len(music_list),
    }


def fetch_tiktok_trending_videos(
    session_cookie: str = "",
    count: int = 20,
    region: str = "US",
) -> dict:
    """Fetch the TikTok For-You feed trending items.

    Uses TikTok's recommend item list endpoint. Extracts hashtags,
    music, and author info from each video.

    Args:
        session_cookie: TikTok sessionid cookie value.
        count: Number of feed items to fetch.
        region: Region code for localised trending.

    Returns:
        Dict with trending videos, extracted hashtags, and music.
    """
    cookies: dict = {}
    if session_cookie:
        cookies["sessionid"] = session_cookie

    params = {
        "count": str(count),
        "id": "1",
        "sourceType": "12",
        "itemID": "1",
        "insertedItemList": "",
        "region": region,
        "priority_region": region,
        "language": "en",
    }

    try:
        resp = requests.get(
            f"{TIKTOK_API_BASE}/recommend/item_list/",
            params=params,
            headers=TIKTOK_HEADERS,
            cookies=cookies,
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.HTTPError as exc:
        raise RuntimeError(
            f"TikTok API returned HTTP {exc.response.status_code}."
        ) from exc
    except requests.RequestException as exc:
        raise RuntimeError(f"TikTok request failed: {exc}") from exc

    videos: list[dict] = []
    hashtags_seen: list[str] = []
    music_seen: list[dict] = []

    for item in data.get("itemList", []):
        vid_id = item.get("id", "")
        desc = item.get("desc", "")
        author = item.get("author", {})
        stats = item.get("stats", {})
        music = item.get("music", {})

        # Extract hashtags from description
        tags = [c.get("hashtagName", "") for c in item.get("challenges", [])]
        inline_tags = _HASHTAG_RE.findall(desc)
        all_tags = list({t.lower() for t in tags + inline_tags if t})
        hashtags_seen.extend(all_tags)

        # Music info
        if music.get("title"):
            music_seen.append({
                "id": music.get("id", ""),
                "title": music.get("title", ""),
                "author": music.get("authorName", ""),
                "duration": music.get("duration", 0),
            })

        videos.append({
            "id": vid_id,
            "description": desc[:200],
            "author": author.get("uniqueId", ""),
            "author_followers": _safe_int(
                item.get("authorStats", {}).get("followerCount", 0)
            ),
            "view_count": _safe_int(stats.get("playCount", 0)),
            "like_count": _safe_int(stats.get("diggCount", 0)),
            "comment_count": _safe_int(stats.get("commentCount", 0)),
            "share_count": _safe_int(stats.get("shareCount", 0)),
            "hashtags": all_tags,
            "music_title": music.get("title", ""),
            "music_author": music.get("authorName", ""),
            "url": f"https://www.tiktok.com/@{author.get('uniqueId', '')}/video/{vid_id}",
        })

    # Aggregate hashtag counts
    hashtag_counts = Counter(hashtags_seen)
    top_hashtags = [
        {"hashtag": f"#{tag}", "count": cnt}
        for tag, cnt in hashtag_counts.most_common(20)
        if len(tag) > 1
    ]

    # Aggregate music counts
    music_counts: dict[str, int] = Counter(
        f"{m['title']}||{m['author']}" for m in music_seen
    )
    top_music = []
    seen_keys = set()
    for m in music_seen:
        key = f"{m['title']}||{m['author']}"
        if key not in seen_keys:
            seen_keys.add(key)
            top_music.append({**m, "video_count": music_counts[key]})
    top_music.sort(key=lambda x: x["video_count"], reverse=True)

    return {
        "platform": "tiktok",
        "type": "feed",
        "region": region,
        "fetched_at": _now_iso(),
        "trending_videos": videos,
        "trending_hashtags": top_hashtags,
        "trending_music": top_music[:15],
        "total_fetched": len(videos),
    }


# ── Cross-platform unified trends ─────────────────────────────────────────────

def get_cross_platform_trends(
    youtube_api_key: str = "",
    tiktok_session: str = "",
    region: str = "US",
    max_results: int = 20,
) -> dict:
    """Aggregate trending data across YouTube and TikTok into a unified report.

    Args:
        youtube_api_key: YouTube Data API v3 key (omit to skip YouTube).
        tiktok_session: TikTok sessionid cookie (omit to skip TikTok).
        region: Region code for both platforms.
        max_results: Videos/items to fetch per platform.

    Returns:
        Unified dict with cross-platform trends, overlapping hashtags,
        top music, and actionable content recommendations.
    """
    results: dict = {
        "fetched_at": _now_iso(),
        "region": region,
        "youtube": None,
        "tiktok_hashtags": None,
        "tiktok_music": None,
        "tiktok_feed": None,
        "cross_platform_hashtags": [],
        "recommendations": [],
        "errors": [],
    }

    yt_hashtags: list[str] = []
    tt_hashtags: list[str] = []

    # YouTube
    if youtube_api_key:
        try:
            yt_data = fetch_youtube_trending(
                youtube_api_key, region=region, max_results=max_results
            )
            results["youtube"] = yt_data
            yt_hashtags = [
                h["hashtag"].lstrip("#")
                for h in yt_data.get("trending_hashtags", [])
            ]
        except Exception as exc:
            results["errors"].append({"platform": "youtube", "error": str(exc)})

    # TikTok
    if tiktok_session:
        try:
            tt_tags = fetch_tiktok_trending_hashtags(tiktok_session, count=max_results)
            results["tiktok_hashtags"] = tt_tags
            tt_hashtags = [
                h["hashtag"].lstrip("#")
                for h in tt_tags.get("trending_hashtags", [])
            ]
        except Exception as exc:
            results["errors"].append({"platform": "tiktok_hashtags", "error": str(exc)})

        try:
            results["tiktok_music"] = fetch_tiktok_trending_music(
                tiktok_session, count=max_results
            )
        except Exception as exc:
            results["errors"].append({"platform": "tiktok_music", "error": str(exc)})

        try:
            results["tiktok_feed"] = fetch_tiktok_trending_videos(
                tiktok_session, count=max_results, region=region
            )
            feed_tags = [
                h["hashtag"].lstrip("#")
                for h in (results["tiktok_feed"] or {}).get("trending_hashtags", [])
            ]
            tt_hashtags = list(set(tt_hashtags + feed_tags))
        except Exception as exc:
            results["errors"].append({"platform": "tiktok_feed", "error": str(exc)})

    # Cross-platform overlap — hashtags trending on BOTH
    if yt_hashtags and tt_hashtags:
        yt_set = set(yt_hashtags)
        tt_set = set(tt_hashtags)
        overlap = sorted(yt_set & tt_set)
        results["cross_platform_hashtags"] = [f"#{t}" for t in overlap]

    # Actionable recommendations
    results["recommendations"] = _build_recommendations(results)

    return results


# ── Hashtag utilities ─────────────────────────────────────────────────────────

def extract_hashtags(text: str) -> list[str]:
    """Extract all #hashtags from a text string."""
    return [f"#{h.lower()}" for h in _HASHTAG_RE.findall(text)]


def filter_hashtags_by_volume(
    hashtags: list[dict],
    min_count: int = 0,
    max_count: int = 0,
) -> list[dict]:
    """Filter a hashtag list by count thresholds.

    Args:
        hashtags: List of {'hashtag': str, 'count': int} dicts.
        min_count: Minimum occurrence count (0 = no minimum).
        max_count: Maximum occurrence count (0 = no maximum).

    Returns:
        Filtered list sorted by count descending.
    """
    result = hashtags
    if min_count > 0:
        result = [h for h in result if h.get("count", 0) >= min_count]
    if max_count > 0:
        result = [h for h in result if h.get("count", 0) <= max_count]
    return sorted(result, key=lambda h: h.get("count", 0), reverse=True)


# ── Fallback scraper ──────────────────────────────────────────────────────────

def _scrape_tiktok_discover_fallback(
    session_cookie: str = "",
    count: int = 20,
) -> list[dict]:
    """Fallback: scrape TikTok discover page HTML for hashtag data."""
    cookies: dict = {}
    if session_cookie:
        cookies["sessionid"] = session_cookie

    try:
        resp = requests.get(
            f"{TIKTOK_WEB_BASE}/explore",
            headers=TIKTOK_HEADERS,
            cookies=cookies,
            timeout=20,
        )
        html = resp.text
        # Extract __UNIVERSAL_DATA__ JSON blob
        match = re.search(
            r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.+?)</script>',
            html,
            re.DOTALL,
        )
        if not match:
            return []
        page_data = json.loads(match.group(1))
        # Navigate to hashtag data
        explore = (
            page_data
            .get("__DEFAULT_SCOPE__", {})
            .get("webapp.explore-page", {})
            .get("exploreList", [])
        )
        hashtags = []
        for entry in explore[:count]:
            card = entry.get("cardItem", {})
            if card.get("type") == 1:  # hashtag type
                challenge = card.get("data", {}).get("challengeInfo", {})
                title = challenge.get("challenge", {}).get("title", "")
                if title:
                    hashtags.append({
                        "hashtag": f"#{title}",
                        "video_count": 0,
                        "view_count": 0,
                        "description": challenge.get("challenge", {}).get("desc", ""),
                    })
        return hashtags
    except Exception:
        return []


# ── Helpers ───────────────────────────────────────────────────────────────────

def _safe_int(val) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


def _engagement_rate(views: int, likes: int, comments: int) -> float:
    if views == 0:
        return 0.0
    return round((likes + comments) / views * 100, 2)


def _now_iso() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _build_recommendations(data: dict) -> list[str]:
    """Generate actionable content recommendations from trend data."""
    recs = []

    yt = data.get("youtube")
    tt_feed = data.get("tiktok_feed")
    tt_music = data.get("tiktok_music")
    cross = data.get("cross_platform_hashtags", [])

    if cross:
        recs.append(
            f"PRIORITY: Use cross-platform hashtags {', '.join(cross[:5])} — "
            "trending on BOTH YouTube and TikTok right now."
        )

    if yt:
        top_tags = [h["hashtag"] for h in yt.get("trending_hashtags", [])[:5]]
        if top_tags:
            recs.append(
                f"YouTube: Add {', '.join(top_tags)} to your video title, "
                "description, and first comment."
            )
        top_topics = [t["topic"] for t in yt.get("trending_topics", [])[:3]]
        if top_topics:
            recs.append(
                f"YouTube: Create content around topics: {', '.join(top_topics)} — "
                "appearing in most trending titles today."
            )

    if tt_feed:
        top_tt_tags = [h["hashtag"] for h in tt_feed.get("trending_hashtags", [])[:5]]
        if top_tt_tags:
            recs.append(
                f"TikTok: Use hashtags {', '.join(top_tt_tags)} in your caption."
            )

    if tt_music:
        top_tracks = tt_music.get("trending_music", [])[:3]
        if top_tracks:
            titles = [f'"{t["title"]}" by {t["author"]}' for t in top_tracks]
            recs.append(
                f"TikTok: Use trending audio: {'; '.join(titles)}. "
                "Videos using viral audio get 2-5x more FYP exposure."
            )

    if not recs:
        recs.append(
            "No trend data fetched. Provide a YouTube API key (--yt-key) "
            "and/or TikTok session cookie (--tt-session) to see recommendations."
        )

    return recs
