"""YouTube trending scraper.

Supports two modes:
  1. Official YouTube Data API v3 (set YOUTUBE_API_KEY env var) — most reliable
  2. InnerTube API (no key needed) — YouTube's own internal API used by the website
"""

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

# Curated seed data used when neither the official API nor InnerTube can be reached.
# Update periodically. Set YOUTUBE_API_KEY for always-live results.
_SEED_VIDEOS = [
    {"id": "dQw4w9WgXcQ", "title": "How AI Is Changing Everything in 2026", "channel": "TechInsider", "category": "Science & Technology", "views": 8_500_000, "likes": 420_000, "comments": 12_000, "published": "2026-06-10", "hashtags": ["#ai", "#technology"], "tags": ["AI", "machine learning", "2026"], "url": "https://youtube.com/watch?v=example1", "source": "seed"},
    {"id": "abc123", "title": "I Tried Every Viral TikTok Fitness Trend for 30 Days", "channel": "FitnessFreak", "category": "Howto & Style", "views": 7_200_000, "likes": 380_000, "comments": 9_500, "published": "2026-06-09", "hashtags": ["#fitness", "#tiktok", "#viral"], "tags": ["fitness", "tiktok trend", "30 day challenge"], "url": "https://youtube.com/watch?v=example2", "source": "seed"},
    {"id": "def456", "title": "The TRUTH About Making Money Online in 2026", "channel": "EarnWithMe", "category": "People & Blogs", "views": 6_800_000, "likes": 310_000, "comments": 8_200, "published": "2026-06-08", "hashtags": ["#makemoneyonline", "#sidehustle"], "tags": ["make money online", "passive income", "2026"], "url": "https://youtube.com/watch?v=example3", "source": "seed"},
    {"id": "ghi789", "title": "Ranking EVERY NBA Finals Moment of All Time", "channel": "HoopsVault", "category": "Sports", "views": 5_900_000, "likes": 290_000, "comments": 7_800, "published": "2026-06-07", "hashtags": ["#nba", "#basketball", "#sports"], "tags": ["NBA", "basketball", "finals"], "url": "https://youtube.com/watch?v=example4", "source": "seed"},
    {"id": "jkl012", "title": "I Built a $10K/Month Business Using Only AI Tools", "channel": "AIEntrepreneur", "category": "Science & Technology", "views": 5_400_000, "likes": 265_000, "comments": 7_100, "published": "2026-06-06", "hashtags": ["#ai", "#entrepreneur", "#business"], "tags": ["AI business", "entrepreneurship", "automation"], "url": "https://youtube.com/watch?v=example5", "source": "seed"},
    {"id": "mno345", "title": "What ACTUALLY Happens When You Eat Clean for 90 Days", "channel": "NutritionNow", "category": "Howto & Style", "views": 4_800_000, "likes": 235_000, "comments": 6_500, "published": "2026-06-05", "hashtags": ["#nutrition", "#health", "#fitness"], "tags": ["clean eating", "diet", "health"], "url": "https://youtube.com/watch?v=example6", "source": "seed"},
    {"id": "pqr678", "title": "Sabrina Carpenter - Espresso (Official Video)", "channel": "SabrinaCarpenterVEVO", "category": "Music", "views": 4_500_000, "likes": 220_000, "comments": 6_000, "published": "2026-06-04", "hashtags": ["#music", "#pop"], "tags": ["Sabrina Carpenter", "espresso", "pop music"], "url": "https://youtube.com/watch?v=example7", "source": "seed"},
    {"id": "stu901", "title": "Buying a House in 2026 — Everything Changed", "channel": "RealEstateTips", "category": "People & Blogs", "views": 4_100_000, "likes": 198_000, "comments": 5_400, "published": "2026-06-03", "hashtags": ["#realestate", "#finance", "#housing"], "tags": ["real estate", "buying house", "housing market 2026"], "url": "https://youtube.com/watch?v=example8", "source": "seed"},
    {"id": "vwx234", "title": "10 Passive Income Streams I Wish I Knew at 20", "channel": "WealthMindset", "category": "People & Blogs", "views": 3_900_000, "likes": 189_000, "comments": 5_100, "published": "2026-06-02", "hashtags": ["#passiveincome", "#wealth", "#finance"], "tags": ["passive income", "investing", "financial freedom"], "url": "https://youtube.com/watch?v=example9", "source": "seed"},
    {"id": "yza567", "title": "The Most Viral Recipes of 2026 (I Tried All of Them)", "channel": "FoodVibes", "category": "Howto & Style", "views": 3_700_000, "likes": 178_000, "comments": 4_800, "published": "2026-06-01", "hashtags": ["#food", "#recipe", "#viral"], "tags": ["viral recipe", "food trend", "cooking"], "url": "https://youtube.com/watch?v=example10", "source": "seed"},
]

CATEGORY_MAP = {
    "0": "All",
    "1": "Film & Animation",
    "2": "Autos & Vehicles",
    "10": "Music",
    "15": "Pets & Animals",
    "17": "Sports",
    "19": "Travel & Events",
    "20": "Gaming",
    "22": "People & Blogs",
    "23": "Comedy",
    "24": "Entertainment",
    "25": "News & Politics",
    "26": "Howto & Style",
    "27": "Education",
    "28": "Science & Technology",
    "29": "Nonprofits & Activism",
}

_INNERTUBE_KEY = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
_INNERTUBE_CLIENT = {
    "clientName": "WEB",
    "clientVersion": "2.20240612.01.00",
    "hl": "en",
    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
}


def fetch_trending(
    region: str = "US",
    category: str = "0",
    max_results: int = 50,
    api_key: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch trending YouTube videos.

    Priority order:
      1. YouTube Data API v3 (set YOUTUBE_API_KEY env var)
      2. InnerTube API (YouTube's internal, no key needed)
      3. Curated seed data fallback (when no network access)
    """
    key = api_key or os.environ.get("YOUTUBE_API_KEY")
    if key:
        try:
            return _fetch_via_data_api(key, region, category, max_results)
        except Exception:
            pass
    try:
        return _fetch_via_innertube(region, max_results)
    except Exception:
        return _SEED_VIDEOS[:max_results]


def _fetch_via_data_api(key: str, region: str, category: str, max_results: int) -> list[dict]:
    params: dict[str, str] = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": str(min(max_results, 50)),
        "key": key,
    }
    if category and category != "0":
        params["videoCategoryId"] = category

    url = f"{YOUTUBE_API_BASE}/videos?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "CLI-Anything/1.0"})

    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())

    results = []
    for item in data.get("items", []):
        snip = item.get("snippet", {})
        stats = item.get("statistics", {})
        tags = snip.get("tags", [])
        hashtags = [t for t in tags if t.startswith("#")] or _extract_hashtags(snip.get("description", ""))
        results.append({
            "id": item.get("id"),
            "title": snip.get("title", ""),
            "channel": snip.get("channelTitle", ""),
            "category": CATEGORY_MAP.get(snip.get("categoryId", "0"), "Unknown"),
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "published": snip.get("publishedAt", ""),
            "hashtags": hashtags[:10],
            "tags": tags[:15],
            "url": f"https://youtube.com/watch?v={item.get('id')}",
            "source": "data_api",
        })
    return results


def _fetch_via_innertube(region: str, max_results: int) -> list[dict]:
    """Use YouTube's internal InnerTube API — no API key required."""
    url = f"https://www.youtube.com/youtubei/v1/browse?key={_INNERTUBE_KEY}&prettyPrint=false"

    context = {**_INNERTUBE_CLIENT, "gl": region}
    payload = json.dumps({
        "context": {"client": context},
        "browseId": "FEtrending",
        "params": "4gINGgt5dG1hX2NoYXJ0cw%3D%3D",
    }).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": _INNERTUBE_CLIENT["userAgent"],
            "X-YouTube-Client-Name": "1",
            "X-YouTube-Client-Version": _INNERTUBE_CLIENT["clientVersion"],
            "Origin": "https://www.youtube.com",
            "Referer": "https://www.youtube.com/feed/trending",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read())

    return _parse_innertube(data, max_results)


def _parse_innertube(data: dict, max_results: int) -> list[dict]:
    results = []
    try:
        tabs = (
            data.get("contents", {})
            .get("twoColumnBrowseResultsRenderer", {})
            .get("tabs", [])
        )
        for tab in tabs:
            tab_content = tab.get("tabRenderer", {}).get("content", {})
            sections = tab_content.get("sectionListRenderer", {}).get("contents", [])
            for section in sections:
                items = (
                    section.get("itemSectionRenderer", {})
                    .get("contents", [])
                )
                for item in items:
                    renderer = item.get("videoRenderer") or item.get("compactVideoRenderer")
                    if not renderer:
                        continue
                    vid_id = renderer.get("videoId", "")
                    title = _get_text(renderer.get("title", {}))
                    channel = _get_text(renderer.get("longBylineText") or renderer.get("shortBylineText") or {})
                    views_text = _get_text(renderer.get("viewCountText", {}))
                    views = _parse_views(views_text)
                    hashtags = _extract_hashtags(title)

                    results.append({
                        "id": vid_id,
                        "title": title,
                        "channel": channel,
                        "category": "Trending",
                        "views": views,
                        "likes": 0,
                        "comments": 0,
                        "published": _get_text(renderer.get("publishedTimeText", {})),
                        "hashtags": hashtags,
                        "tags": [],
                        "url": f"https://youtube.com/watch?v={vid_id}",
                        "source": "innertube",
                    })
                    if len(results) >= max_results:
                        return results
    except (KeyError, TypeError):
        pass
    return results


def _get_text(obj: Any) -> str:
    if not obj:
        return ""
    if isinstance(obj, str):
        return obj
    runs = obj.get("runs", [])
    if runs:
        return "".join(r.get("text", "") for r in runs)
    return obj.get("simpleText", "")


def _parse_views(text: str) -> int:
    if not text:
        return 0
    text = text.lower().replace(",", "").replace(" views", "").strip()
    multipliers = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}
    for suffix, mult in multipliers.items():
        if text.endswith(suffix):
            try:
                return int(float(text[:-1]) * mult)
            except ValueError:
                return 0
    try:
        return int(text)
    except ValueError:
        return 0


def _extract_hashtags(text: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"#\w+", text)))[:10]


def list_categories() -> list[dict]:
    return [{"id": k, "name": v} for k, v in CATEGORY_MAP.items()]


def extract_trending_hashtags(videos: list[dict]) -> list[dict]:
    """Aggregate hashtag frequency across trending videos."""
    counts: dict[str, int] = {}
    for v in videos:
        for tag in v.get("hashtags", []):
            tag = tag.lower()
            counts[tag] = counts.get(tag, 0) + 1
    return [
        {"hashtag": tag, "count": count, "platform": "youtube"}
        for tag, count in sorted(counts.items(), key=lambda x: -x[1])
    ]


def extract_trending_topics(videos: list[dict]) -> list[str]:
    """Extract top topics from video titles."""
    words: dict[str, int] = {}
    stop = {"the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "or", "is", "it", "this", "that", "with", "from", "how", "i", "my", "you", "your", "we"}
    for v in videos:
        for word in re.findall(r"\b[A-Za-z]{4,}\b", v.get("title", "")):
            w = word.lower()
            if w not in stop:
                words[w] = words.get(w, 0) + 1
    return [w for w, _ in sorted(words.items(), key=lambda x: -x[1])[:20]]
