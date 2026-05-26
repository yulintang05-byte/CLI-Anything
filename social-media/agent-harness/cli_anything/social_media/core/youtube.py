"""YouTube trend scraping — trending videos, hashtags, and music."""

import json
import re
import time
from dataclasses import dataclass, field, asdict
from typing import Optional
from urllib.request import urlopen, Request
from urllib.parse import urlencode, quote
from urllib.error import URLError

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
TRENDING_RSS = "https://www.youtube.com/feed/trending"


@dataclass
class TrendingVideo:
    video_id: str
    title: str
    channel: str
    view_count: int
    like_count: int
    comment_count: int
    published_at: str
    description_snippet: str
    hashtags: list[str]
    category: str
    thumbnail_url: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TrendResult:
    platform: str = "youtube"
    fetched_at: str = ""
    region: str = "US"
    category: str = "all"
    videos: list[TrendingVideo] = field(default_factory=list)
    top_hashtags: list[dict] = field(default_factory=list)
    top_music: list[str] = field(default_factory=list)
    insights: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


CATEGORY_IDS = {
    "all": "0",
    "music": "10",
    "gaming": "20",
    "entertainment": "24",
    "news": "25",
    "sports": "17",
    "tech": "28",
}

REGION_CODES = {
    "us": "US", "uk": "GB", "ca": "CA", "au": "AU",
    "in": "IN", "br": "BR", "de": "DE", "fr": "FR",
    "jp": "JP", "kr": "KR", "mx": "MX",
}


def _api_get(endpoint: str, params: dict, api_key: str) -> dict:
    params["key"] = api_key
    url = f"{YOUTUBE_API_BASE}/{endpoint}?{urlencode(params)}"
    req = Request(url, headers={"User-Agent": "CLI-Anything-SocialMedia/1.0"})
    with urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def _extract_hashtags(text: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"#(\w+)", text)))


def _extract_music_from_titles(titles: list[str]) -> list[str]:
    music_keywords = ["official audio", "official video", "lyric", "music video",
                      "ft.", "feat.", "prod.", "remix", "cover"]
    music = []
    for title in titles:
        if any(kw in title.lower() for kw in music_keywords):
            music.append(title)
    return music[:10]


def _count_hashtags(all_tags: list[str]) -> list[dict]:
    counts: dict[str, int] = {}
    for tag in all_tags:
        t = tag.lower()
        counts[t] = counts.get(t, 0) + 1
    sorted_tags = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [{"hashtag": f"#{t}", "count": c} for t, c in sorted_tags[:20]]


def _build_insights(videos: list[TrendingVideo], region: str) -> list[str]:
    if not videos:
        return ["No data available."]

    avg_views = sum(v.view_count for v in videos) // max(len(videos), 1)
    top = videos[0] if videos else None
    insights = [
        f"Average views for trending videos in {region}: {avg_views:,}",
        f"Top trending: '{top.title}' by {top.channel} ({top.view_count:,} views)" if top else "",
        f"Best time to post: Mirror upload times of top 3 trending creators.",
        "Use 3-5 trending hashtags per video for maximum discoverability.",
        "Shorts (under 60s) dominate trending on mobile — consider a Shorts strategy.",
        "Thumbnail text + bold contrast colors drive higher CTR on trending topics.",
    ]
    return [i for i in insights if i]


def fetch_trending(
    api_key: str,
    region: str = "US",
    category: str = "all",
    max_results: int = 20,
) -> TrendResult:
    """Fetch trending YouTube videos using the Data API v3."""
    from datetime import datetime, timezone

    region = REGION_CODES.get(region.lower(), region.upper())
    cat_id = CATEGORY_IDS.get(category.lower(), "0")

    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": min(max_results, 50),
        "videoCategoryId": cat_id,
    }

    data = _api_get("videos", params, api_key)
    videos: list[TrendingVideo] = []
    all_tags: list[str] = []
    all_titles: list[str] = []

    for item in data.get("items", []):
        snip = item.get("snippet", {})
        stats = item.get("statistics", {})
        title = snip.get("title", "")
        desc = snip.get("description", "")[:200]
        tags = _extract_hashtags(title + " " + desc)
        all_tags.extend(tags)
        all_titles.append(title)

        videos.append(TrendingVideo(
            video_id=item.get("id", ""),
            title=title,
            channel=snip.get("channelTitle", ""),
            view_count=int(stats.get("viewCount", 0)),
            like_count=int(stats.get("likeCount", 0)),
            comment_count=int(stats.get("commentCount", 0)),
            published_at=snip.get("publishedAt", ""),
            description_snippet=desc,
            hashtags=tags,
            category=snip.get("categoryId", cat_id),
            thumbnail_url=snip.get("thumbnails", {}).get("high", {}).get("url", ""),
        ))

    videos.sort(key=lambda v: v.view_count, reverse=True)

    return TrendResult(
        platform="youtube",
        fetched_at=datetime.now(timezone.utc).isoformat(),
        region=region,
        category=category,
        videos=videos,
        top_hashtags=_count_hashtags(all_tags),
        top_music=_extract_music_from_titles(all_titles),
        insights=_build_insights(videos, region),
    )


def fetch_trending_no_api(region: str = "US", max_results: int = 10) -> TrendResult:
    """Fallback: scrape YouTube trending page (no API key needed, limited data)."""
    from datetime import datetime, timezone

    url = f"https://www.youtube.com/feed/trending?gl={region}"
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    })

    try:
        with urlopen(req, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except URLError as e:
        raise RuntimeError(f"Failed to fetch YouTube trending page: {e}") from e

    # Extract video titles from ytInitialData JSON blob
    match = re.search(r"var ytInitialData\s*=\s*(\{.+?\});\s*</script>", html, re.DOTALL)
    if not match:
        # Try alternate pattern
        match = re.search(r"ytInitialData\s*=\s*(\{.+?\});\s*var ", html, re.DOTALL)

    videos: list[TrendingVideo] = []
    all_tags: list[str] = []

    if match:
        try:
            yt_data = json.loads(match.group(1))
            # Walk the nested structure to find video renderers
            items_path = (
                yt_data.get("contents", {})
                .get("twoColumnBrowseResultsRenderer", {})
                .get("tabs", [{}])[0]
                .get("tabRenderer", {})
                .get("content", {})
                .get("sectionListRenderer", {})
                .get("contents", [])
            )
            count = 0
            for section in items_path:
                for shelf in section.get("itemSectionRenderer", {}).get("contents", []):
                    for item in shelf.get("shelfRenderer", {}).get("content", {}).get(
                        "expandedShelfContentsRenderer", {}
                    ).get("items", []):
                        vr = item.get("videoRenderer", {})
                        if not vr or count >= max_results:
                            continue
                        title_runs = vr.get("title", {}).get("runs", [])
                        title = "".join(r.get("text", "") for r in title_runs)
                        channel_runs = (
                            vr.get("ownerText", {}).get("runs", [])
                            or vr.get("longBylineText", {}).get("runs", [])
                        )
                        channel = "".join(r.get("text", "") for r in channel_runs)
                        vid_id = vr.get("videoId", "")
                        view_text = (
                            vr.get("viewCountText", {}).get("simpleText", "")
                            or vr.get("viewCountText", {}).get("runs", [{}])[0].get("text", "")
                        )
                        view_count = _parse_view_count(view_text)
                        tags = _extract_hashtags(title)
                        all_tags.extend(tags)

                        videos.append(TrendingVideo(
                            video_id=vid_id,
                            title=title,
                            channel=channel,
                            view_count=view_count,
                            like_count=0,
                            comment_count=0,
                            published_at="",
                            description_snippet="",
                            hashtags=tags,
                            category="trending",
                            thumbnail_url=f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg",
                        ))
                        count += 1
        except (KeyError, IndexError, json.JSONDecodeError):
            pass

    if not videos:
        # Last resort: regex-extract titles
        titles = re.findall(r'"title":\{"runs":\[{"text":"([^"]+)"', html)[:max_results]
        for i, title in enumerate(titles):
            tags = _extract_hashtags(title)
            all_tags.extend(tags)
            videos.append(TrendingVideo(
                video_id=f"scraped_{i}",
                title=title,
                channel="",
                view_count=0,
                like_count=0,
                comment_count=0,
                published_at="",
                description_snippet="",
                hashtags=tags,
                category="trending",
                thumbnail_url="",
            ))

    return TrendResult(
        platform="youtube",
        fetched_at=datetime.now(timezone.utc).isoformat(),
        region=region,
        category="trending",
        videos=videos,
        top_hashtags=_count_hashtags(all_tags),
        top_music=_extract_music_from_titles([v.title for v in videos]),
        insights=_build_insights(videos, region),
    )


def _parse_view_count(text: str) -> int:
    text = text.lower().replace(",", "").strip()
    if "b" in text:
        return int(float(text.replace("b", "")) * 1_000_000_000)
    if "m" in text:
        return int(float(text.replace("m", "")) * 1_000_000)
    if "k" in text:
        return int(float(text.replace("k", "")) * 1_000)
    try:
        return int("".join(c for c in text if c.isdigit()))
    except ValueError:
        return 0
