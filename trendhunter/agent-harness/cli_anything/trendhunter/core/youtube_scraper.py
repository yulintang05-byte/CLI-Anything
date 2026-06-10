"""YouTube trend scraper — trending videos, hashtags, and viral music.

Data sources (no API key required):
  - YouTube RSS trending feed
  - YouTube public trending page HTML
  - YouTube Music trending charts
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional

from cli_anything.trendhunter.utils.scraper_backend import (
    fetch, fetch_json, make_session, polite_delay,
)


_YT_RSS_TRENDING = "https://www.youtube.com/feeds/videos.xml?chart=popular&regionCode={region}"
_YT_TRENDING_URL = "https://www.youtube.com/feed/trending"
_YT_SHORTS_URL   = "https://www.youtube.com/shorts"
_YT_MUSIC_CHARTS = "https://charts.youtube.com/charts/TrendingVideos/{region}"

_YT_API_TRENDING = (
    "https://www.googleapis.com/youtube/v3/videos"
    "?part=snippet,statistics&chart=mostPopular&regionCode={region}"
    "&maxResults={max_results}&key={api_key}"
)

# Regex to extract hashtags from YouTube video titles / descriptions
_HASHTAG_RE = re.compile(r"#(\w+)")


@dataclass
class YouTubeVideo:
    video_id: str
    title: str
    channel: str
    published: str
    views: int = 0
    likes: int = 0
    hashtags: list[str] = field(default_factory=list)
    thumbnail: str = ""
    url: str = ""

    def to_dict(self) -> dict:
        return {
            "video_id":  self.video_id,
            "title":     self.title,
            "channel":   self.channel,
            "published": self.published,
            "views":     self.views,
            "likes":     self.likes,
            "hashtags":  self.hashtags,
            "url":       self.url,
        }


@dataclass
class YouTubeTrends:
    region: str
    videos: list[YouTubeVideo] = field(default_factory=list)
    trending_hashtags: list[str] = field(default_factory=list)
    trending_music: list[dict] = field(default_factory=list)
    shorts_trends: list[str] = field(default_factory=list)
    source: str = "rss"

    def to_dict(self) -> dict:
        return {
            "region":            self.region,
            "source":            self.source,
            "videos":            [v.to_dict() for v in self.videos],
            "trending_hashtags": self.trending_hashtags,
            "trending_music":    self.trending_music,
            "shorts_trends":     self.shorts_trends,
        }


def fetch_trending_via_rss(region: str = "US",
                           max_results: int = 25) -> list[YouTubeVideo]:
    """Fetch trending YouTube videos via the public RSS feed (no API key needed)."""
    url = _YT_RSS_TRENDING.format(region=region)
    resp = fetch(url)
    if resp is None:
        return []

    videos: list[YouTubeVideo] = []
    try:
        root = ET.fromstring(resp.content)
        ns = {
            "atom":  "http://www.w3.org/2005/Atom",
            "media": "http://search.yahoo.com/mrss/",
            "yt":    "http://www.youtube.com/xml/schemas/2015",
        }
        for entry in root.findall("atom:entry", ns)[:max_results]:
            vid_id  = (entry.findtext("yt:videoId", "", ns) or "").strip()
            title   = (entry.findtext("atom:title", "", ns) or "").strip()
            channel = ""
            author  = entry.find("atom:author", ns)
            if author is not None:
                channel = (author.findtext("atom:name", "", ns) or "").strip()
            published = (entry.findtext("atom:published", "", ns) or "").strip()
            tags = _HASHTAG_RE.findall(title)
            url = f"https://www.youtube.com/watch?v={vid_id}" if vid_id else ""
            videos.append(YouTubeVideo(
                video_id=vid_id, title=title, channel=channel,
                published=published, hashtags=tags, url=url,
            ))
    except ET.ParseError:
        pass
    return videos


def fetch_trending_via_api(region: str = "US", max_results: int = 25,
                           api_key: str = "") -> list[YouTubeVideo]:
    """Fetch trending videos via YouTube Data API v3 (requires API key)."""
    if not api_key:
        return []
    url = _YT_API_TRENDING.format(
        region=region, max_results=max_results, api_key=api_key
    )
    data = fetch_json(url)
    if not data or "items" not in data:
        return []

    videos: list[YouTubeVideo] = []
    for item in data["items"]:
        snippet = item.get("snippet", {})
        stats   = item.get("statistics", {})
        vid_id  = item.get("id", "")
        tags    = snippet.get("tags", [])
        hashtags = [t.lstrip("#") for t in tags if t.startswith("#")]
        # Also grab from title
        hashtags += _HASHTAG_RE.findall(snippet.get("title", ""))
        videos.append(YouTubeVideo(
            video_id=vid_id,
            title=snippet.get("title", ""),
            channel=snippet.get("channelTitle", ""),
            published=snippet.get("publishedAt", ""),
            views=int(stats.get("viewCount", 0) or 0),
            likes=int(stats.get("likeCount", 0) or 0),
            hashtags=list(dict.fromkeys(hashtags)),
            thumbnail=snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            url=f"https://www.youtube.com/watch?v={vid_id}",
        ))
    return videos


def extract_hashtags_from_videos(videos: list[YouTubeVideo],
                                  top_n: int = 20) -> list[str]:
    """Count and rank hashtags across a list of trending videos."""
    counts: dict[str, int] = {}
    for v in videos:
        for tag in v.hashtags:
            tag_lower = tag.lower()
            counts[tag_lower] = counts.get(tag_lower, 0) + 1
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [tag for tag, _ in ranked[:top_n]]


def fetch_trending_music_yt(region: str = "US") -> list[dict]:
    """Scrape YouTube Music trending chart titles."""
    session = make_session()
    # YouTube Music trending endpoint (public web)
    url = f"https://music.youtube.com/charts"
    resp = fetch(url, session=session, headers={
        "Accept": "text/html",
        "Referer": "https://music.youtube.com/",
    })
    if resp is None:
        return []

    # Parse song titles from the embedded JSON data blob
    pattern = re.compile(r'"title"\s*:\s*\{"runs"\s*:\s*\[\{"text"\s*:\s*"([^"]{3,80})"')
    titles = list(dict.fromkeys(pattern.findall(resp.text)))[:20]

    results = []
    for t in titles:
        if any(skip in t.lower() for skip in ["trending", "chart", "youtube", "music"]):
            continue
        results.append({"title": t, "source": "youtube_music"})
    return results[:15]


def scrape_shorts_trending_tags(region: str = "US") -> list[str]:
    """Extract trending topic tags referenced in YouTube Shorts explore page."""
    session = make_session(mobile=True)
    resp = fetch(_YT_SHORTS_URL, session=session)
    if resp is None:
        return []
    # Pull hashtag-style chips / category labels from the page
    tags = list(dict.fromkeys(re.findall(r'#([A-Za-z]\w{2,30})', resp.text)))
    return tags[:20]


def fetch_youtube_trends(region: str = "US", max_results: int = 25,
                          api_key: str = "") -> YouTubeTrends:
    """Top-level function: fetch all YouTube trend data for a region."""
    trends = YouTubeTrends(region=region)

    # Prefer API when key provided, fall back to RSS
    if api_key:
        trends.videos = fetch_trending_via_api(region, max_results, api_key)
        trends.source = "api"
    else:
        trends.videos = fetch_trending_via_rss(region, max_results)
        trends.source = "rss"

    polite_delay()
    trends.trending_hashtags = extract_hashtags_from_videos(trends.videos, top_n=20)

    polite_delay()
    trends.trending_music = fetch_trending_music_yt(region)

    polite_delay()
    trends.shorts_trends = scrape_shorts_trending_tags(region)

    return trends
