"""Google Trends integration via unofficial RSS/JSON endpoints.

Uses Google's public trends endpoints — no API key required.
Supplements TikTok/YouTube data with broader cultural trend signals.
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone


GOOGLE_TRENDS_RSS = "https://trends.google.com/trends/trendingsearches/daily/rss"
GOOGLE_TRENDS_JSON = "https://trends.google.com/trends/api/dailytrends"


def _get(url: str, params: dict | None = None) -> str:
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch_daily_trends(geo: str = "US", limit: int = 20) -> list[dict]:
    """Return today's top trending searches from Google Trends.

    Tries the JSON API first, falls back to RSS if blocked.
    """
    try:
        return _fetch_daily_json(geo, limit)
    except Exception:
        pass
    # RSS fallback
    rss_items = fetch_realtime_trends(geo)
    return [
        {
            "query": item["query"],
            "traffic": item.get("approx_traffic", ""),
            "related_queries": [],
            "top_article_title": item["news"][0]["title"] if item.get("news") else "",
            "top_article_url": item["news"][0]["url"] if item.get("news") else "",
        }
        for item in rss_items[:limit]
    ]


def _fetch_daily_json(geo: str, limit: int) -> list[dict]:  # noqa: C901
    params = {
        "hl": "en-US",
        "tz": "-300",
        "geo": geo.upper(),
        "ns": "15",
    }
    raw = _get(GOOGLE_TRENDS_JSON, params)
    # Google wraps JSON with ")]}'\n"
    if raw.startswith(")]}'"):
        raw = raw[5:]
    elif "\n" in raw[:10]:
        raw = raw[raw.index("\n") + 1:]

    data = json.loads(raw)
    trends_data = (
        data.get("default", {})
        .get("trendingSearchesDays", [{}])[0]
        .get("trendingSearches", [])
    )

    results = []
    for item in trends_data[:limit]:
        title = item.get("title", {}).get("query", "")
        traffic = item.get("formattedTraffic", "")
        articles = item.get("articles", [])
        results.append({
            "query": title,
            "traffic": traffic,
            "related_queries": [
                rq.get("query", "") for rq in item.get("relatedQueries", [])[:5]
            ],
            "top_article_title": articles[0].get("title", "") if articles else "",
            "top_article_url": articles[0].get("url", "") if articles else "",
        })
    return results


def fetch_realtime_trends(geo: str = "US", category: str = "all") -> list[dict]:
    """Return real-time trending searches via RSS feed."""
    params = {"geo": geo.upper()}
    if category != "all":
        params["cat"] = category
    try:
        raw = _get(GOOGLE_TRENDS_RSS, params)
    except Exception as e:
        raise RuntimeError(
            f"Google Trends RSS blocked ({e}). "
            "This can happen in restricted network environments. "
            "Try running locally or use 'trends fetch youtube/tiktok' instead."
        ) from e
    items = _parse_rss(raw)
    return items[:30]


def _parse_rss(xml: str) -> list[dict]:
    """Minimal RSS parser — no external dependencies."""
    results = []
    # Split on <item> tags
    parts = xml.split("<item>")
    for part in parts[1:]:
        title = _extract_tag(part, "title")
        approx_traffic = _extract_tag(part, "ht:approx_traffic")
        pub_date = _extract_tag(part, "pubDate")
        news_items = []
        for news_part in part.split("<ht:news_item>")[1:]:
            news_title = _extract_tag(news_part, "ht:news_item_title")
            news_url = _extract_tag(news_part, "ht:news_item_url")
            if news_title:
                news_items.append({"title": news_title, "url": news_url})
        results.append({
            "query": title,
            "approx_traffic": approx_traffic,
            "published": pub_date,
            "news": news_items[:3],
        })
    return results


def _extract_tag(text: str, tag: str) -> str:
    start = text.find(f"<{tag}>")
    end = text.find(f"</{tag}>")
    if start == -1 or end == -1:
        return ""
    return text[start + len(tag) + 2: end].strip()
