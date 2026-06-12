"""YouTube trend scraper — fetches viral videos, hashtags, and music.

Data sources (tried in order):
  1. YouTube Data API v3   — requires YOUTUBE_API_KEY env var
  2. InnerTube API         — YouTube's own internal JSON API (no key needed)
  3. youtubesearchpython  — pip install youtubesearchpython (no key needed)
"""

import os
import re
import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict

from cli_anything.social_trends.utils.http_client import (
    get_session, rate_limited_get, safe_json
)

# ── Data models ───────────────────────────────────────────────────────────────

@dataclass
class TrendingVideo:
    video_id: str
    title: str
    channel: str
    views: int
    likes: int
    published_at: str
    duration: str
    hashtags: List[str]
    music: Optional[str]
    thumbnail: str
    url: str
    platform: str = "youtube"

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class HashtagCount:
    tag: str
    count: int
    avg_views: int
    platform: str = "youtube"

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class MusicTrack:
    title: str
    artist: str
    usage_count: int
    platform: str = "youtube"
    sample_video_id: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


# ── YouTube category IDs ──────────────────────────────────────────────────────

CATEGORIES = {
    "all":           "0",
    "music":         "10",
    "gaming":        "20",
    "entertainment": "24",
    "news":          "25",
    "howto":         "26",
    "film":          "1",
    "comedy":        "23",
    "sports":        "17",
    "beauty":        "26",
}

# ── InnerTube API (no API key required) ───────────────────────────────────────

_INNERTUBE_URL = "https://www.youtube.com/youtubei/v1/browse"
_INNERTUBE_KEY = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"  # public web client key

_INNERTUBE_CONTEXT = {
    "client": {
        "clientName": "WEB",
        "clientVersion": "2.20240101.01.00",
        "hl": "en",
        "gl": "US",
    }
}


def _innertube_trending(category_id: str = "0", region: str = "US") -> List[Dict]:
    """Fetch trending videos via InnerTube browse API."""
    payload = {
        "context": _INNERTUBE_CONTEXT,
        "browseId": "FEtrending",
        "params": _category_param(category_id),
    }

    session = get_session({"Content-Type": "application/json"})
    try:
        resp = session.post(
            _INNERTUBE_URL,
            params={"key": _INNERTUBE_KEY, "prettyPrint": "false"},
            json=payload,
            timeout=20,
        )
        if resp.status_code != 200:
            return []
        data = resp.json()
        return _parse_innertube_response(data)
    except Exception:
        return []


def _category_param(category_id: str) -> str:
    """Encode category ID into InnerTube browse params."""
    params_map = {
        "0":  "4gINGgt5dFZrb3dxd1VFQg%3D%3D",
        "10": "4gIKGgh5dFZrb3d3d0I%3D",
        "20": "4gIKGgh5dFZrb3d3d0I%3D",
        "24": "4gIKGgh5dFZrb3d3d0I%3D",
    }
    return params_map.get(category_id, "4gINGgt5dFZrb3dxd1VFQg%3D%3D")


def _parse_innertube_response(data: Dict) -> List[Dict]:
    """Walk InnerTube JSON to extract video items."""
    videos = []
    try:
        tabs = data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]
        for tab in tabs:
            tab_content = tab.get("tabRenderer", {}).get("content", {})
            section_list = tab_content.get("sectionListRenderer", {})
            for section in section_list.get("contents", []):
                item_section = section.get("itemSectionRenderer", {})
                for item in item_section.get("contents", []):
                    shelf = item.get("shelfRenderer", {})
                    shelf_content = shelf.get("content", {})
                    expanded = shelf_content.get("expandedShelfContentsRenderer", {})
                    for video_item in expanded.get("items", []):
                        vr = video_item.get("videoRenderer", {})
                        if vr:
                            videos.append(_parse_video_renderer(vr))
    except (KeyError, TypeError):
        pass
    return [v for v in videos if v]


def _parse_video_renderer(vr: Dict) -> Optional[Dict]:
    """Extract fields from a videoRenderer object."""
    try:
        video_id = vr.get("videoId", "")
        title = _get_text(vr.get("title", {}))
        channel = _get_text(vr.get("ownerText", {}))
        views_text = _get_text(vr.get("viewCountText", {}))
        views = _parse_count(views_text)
        published = _get_text(vr.get("publishedTimeText", {}))
        duration = _get_text(vr.get("lengthText", {}))
        description = _get_text(vr.get("descriptionSnippet", {}))
        thumbnails = vr.get("thumbnail", {}).get("thumbnails", [])
        thumbnail = thumbnails[-1].get("url", "") if thumbnails else ""

        hashtags = _extract_hashtags(title + " " + description)

        return {
            "video_id": video_id,
            "title": title,
            "channel": channel,
            "views": views,
            "likes": 0,
            "published_at": published,
            "duration": duration,
            "hashtags": hashtags,
            "music": None,
            "thumbnail": thumbnail,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "platform": "youtube",
        }
    except Exception:
        return None


def _get_text(obj: Dict) -> str:
    """Extract text from YouTube's runs/simpleText structure."""
    if not obj:
        return ""
    if "simpleText" in obj:
        return obj["simpleText"]
    if "runs" in obj:
        return "".join(r.get("text", "") for r in obj["runs"])
    return ""


def _parse_count(text: str) -> int:
    """Parse '1.2M views' → 1200000."""
    text = text.lower().replace(",", "").replace(" views", "").strip()
    try:
        if "b" in text:
            return int(float(text.replace("b", "")) * 1_000_000_000)
        if "m" in text:
            return int(float(text.replace("m", "")) * 1_000_000)
        if "k" in text:
            return int(float(text.replace("k", "")) * 1_000)
        return int(text) if text.isdigit() else 0
    except (ValueError, AttributeError):
        return 0


def _extract_hashtags(text: str) -> List[str]:
    """Extract #hashtags from text."""
    return list(dict.fromkeys(
        tag.lower() for tag in re.findall(r"#(\w+)", text)
    ))


# ── YouTube Data API v3 ───────────────────────────────────────────────────────

def _api_trending(
    api_key: str,
    category_id: str = "0",
    region: str = "US",
    max_results: int = 50,
) -> List[Dict]:
    """Fetch trending via official Data API v3."""
    params = {
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": min(max_results, 50),
        "key": api_key,
    }
    if category_id and category_id != "0":
        params["videoCategoryId"] = category_id

    session = get_session()
    try:
        resp = session.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params=params,
            timeout=15,
        )
        data = safe_json(resp)
        return [_parse_api_item(item) for item in data.get("items", [])]
    except Exception:
        return []


def _parse_api_item(item: Dict) -> Dict:
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    details = item.get("contentDetails", {})
    video_id = item.get("id", "")
    desc = snippet.get("description", "")
    title = snippet.get("title", "")
    tags = snippet.get("tags", [])

    hashtags = _extract_hashtags(title + " " + desc)
    hashtags.extend([f"#{t.lower().replace(' ', '')}" for t in tags[:5]])
    hashtags = list(dict.fromkeys(hashtags))

    return {
        "video_id": video_id,
        "title": title,
        "channel": snippet.get("channelTitle", ""),
        "views": int(stats.get("viewCount", 0)),
        "likes": int(stats.get("likeCount", 0)),
        "published_at": snippet.get("publishedAt", ""),
        "duration": details.get("duration", ""),
        "hashtags": hashtags,
        "music": None,
        "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "platform": "youtube",
    }


# ── youtubesearchpython fallback ──────────────────────────────────────────────

def _search_trending_fallback(query: str = "trending 2024", max_results: int = 20) -> List[Dict]:
    """Use youtubesearchpython as a last-resort fallback."""
    try:
        from youtubesearchpython import VideosSearch
        search = VideosSearch(query, limit=max_results)
        results = search.result()
        videos = []
        for item in results.get("result", []):
            video_id = item.get("id", "")
            title = item.get("title", "")
            hashtags = _extract_hashtags(title)
            videos.append({
                "video_id": video_id,
                "title": title,
                "channel": item.get("channel", {}).get("name", ""),
                "views": _parse_count(item.get("viewCount", {}).get("short", "0")),
                "likes": 0,
                "published_at": item.get("publishedTime", ""),
                "duration": item.get("duration", ""),
                "hashtags": hashtags,
                "music": None,
                "thumbnail": item.get("thumbnails", [{}])[0].get("url", ""),
                "url": item.get("link", f"https://www.youtube.com/watch?v={video_id}"),
                "platform": "youtube",
            })
        return videos
    except ImportError:
        return []
    except Exception:
        return []


# ── Public API ────────────────────────────────────────────────────────────────

def get_trending(
    category: str = "all",
    region: str = "US",
    max_results: int = 50,
) -> List[TrendingVideo]:
    """Fetch trending YouTube videos.

    Args:
        category: One of: all, music, gaming, entertainment, news, howto, film, comedy, sports
        region: ISO 3166-1 alpha-2 country code (US, GB, IN, …)
        max_results: Maximum number of videos to return

    Returns:
        List of TrendingVideo objects sorted by view count.
    """
    category_id = CATEGORIES.get(category.lower(), "0")
    api_key = os.environ.get("YOUTUBE_API_KEY", "")
    raw: List[Dict] = []

    if api_key:
        raw = _api_trending(api_key, category_id, region, max_results)

    if not raw:
        raw = _innertube_trending(category_id, region)

    if not raw:
        raw = _search_trending_fallback(
            f"trending {category} 2024" if category != "all" else "trending 2024",
            max_results,
        )

    videos = []
    for r in raw[:max_results]:
        if r:
            videos.append(TrendingVideo(**{k: r.get(k, v) for k, v in TrendingVideo.__dataclass_fields__.items()}))

    videos.sort(key=lambda v: v.views, reverse=True)
    return videos


def get_trending_hashtags(videos: List[TrendingVideo], top_n: int = 30) -> List[HashtagCount]:
    """Aggregate hashtag frequency from a list of trending videos."""
    tag_views: Dict[str, List[int]] = {}
    for v in videos:
        for tag in v.hashtags:
            tag_views.setdefault(tag, []).append(v.views)

    results = []
    for tag, view_list in tag_views.items():
        results.append(HashtagCount(
            tag=f"#{tag}" if not tag.startswith("#") else tag,
            count=len(view_list),
            avg_views=int(sum(view_list) / len(view_list)),
            platform="youtube",
        ))

    results.sort(key=lambda h: (h.count, h.avg_views), reverse=True)
    return results[:top_n]


def get_trending_music(videos: List[TrendingVideo]) -> List[MusicTrack]:
    """Extract music mentions from trending videos in the Music category."""
    music_counts: Dict[str, Dict] = {}
    for v in videos:
        if v.music:
            key = v.music.lower()
            if key not in music_counts:
                music_counts[key] = {"title": v.music, "artist": "", "count": 0, "video_id": v.video_id}
            music_counts[key]["count"] += 1

    tracks = []
    for data in music_counts.values():
        tracks.append(MusicTrack(
            title=data["title"],
            artist=data["artist"],
            usage_count=data["count"],
            platform="youtube",
            sample_video_id=data["video_id"],
        ))

    tracks.sort(key=lambda t: t.usage_count, reverse=True)
    return tracks
