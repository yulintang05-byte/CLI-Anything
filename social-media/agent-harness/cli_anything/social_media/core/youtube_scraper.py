"""YouTube trend scraper - extracts viral videos, hashtags, and music."""

import json
import re
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import yt_dlp
    HAS_YTDLP = True
except ImportError:
    HAS_YTDLP = False

TRENDING_CATEGORIES = {
    "now":       "https://www.youtube.com/feed/trending",
    "music":     "https://www.youtube.com/feed/trending?bp=4gINGgt5dG1hX2NoYXJ0cw%3D%3D",
    "gaming":    "https://www.youtube.com/feed/trending?bp=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D",
    "movies":    "https://www.youtube.com/feed/trending?bp=4gIKGgh0cmFpbGVycw%3D%3D",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def _extract_initial_data(html: str) -> Optional[Dict]:
    """Pull ytInitialData JSON blob from YouTube page HTML."""
    match = re.search(r"var ytInitialData\s*=\s*(\{.+?\});\s*</script>", html, re.DOTALL)
    if not match:
        match = re.search(r"ytInitialData\s*=\s*(\{.+?\});\s*(?:var |window\.)", html, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def _parse_trending_items(data: Dict) -> List[Dict[str, Any]]:
    """Walk ytInitialData tree to extract video cards from trending feed."""
    results = []
    try:
        tabs = (
            data.get("contents", {})
            .get("twoColumnBrowseResultsRenderer", {})
            .get("tabs", [])
        )
        for tab in tabs:
            content = tab.get("tabRenderer", {}).get("content", {})
            sections = (
                content.get("sectionListRenderer", {})
                .get("contents", [])
            )
            for section in sections:
                items = (
                    section.get("itemSectionRenderer", {})
                    .get("contents", [])
                )
                for item in items:
                    renderer = item.get("videoRenderer") or item.get("compactVideoRenderer")
                    if not renderer:
                        shelf = item.get("shelfRenderer", {})
                        shelf_items = (
                            shelf.get("content", {})
                            .get("expandedShelfContentsRenderer", {})
                            .get("items", [])
                        )
                        for si in shelf_items:
                            r = si.get("videoRenderer") or si.get("compactVideoRenderer")
                            if r:
                                results.append(_parse_renderer(r))
                        continue
                    results.append(_parse_renderer(renderer))
    except Exception:
        pass
    return [r for r in results if r]


def _parse_renderer(r: Dict) -> Optional[Dict[str, Any]]:
    try:
        video_id = r.get("videoId", "")
        title_runs = r.get("title", {}).get("runs", [])
        title = "".join(x.get("text", "") for x in title_runs)

        channel_runs = (
            r.get("ownerText", {}).get("runs", [])
            or r.get("shortBylineText", {}).get("runs", [])
        )
        channel = "".join(x.get("text", "") for x in channel_runs)

        view_text = (
            r.get("viewCountText", {}).get("simpleText", "")
            or r.get("viewCountText", {}).get("runs", [{}])[0].get("text", "")
        )

        badges = []
        for badge in r.get("badges", []):
            label = (
                badge.get("metadataBadgeRenderer", {}).get("label", "")
                or badge.get("metadataBadgeRenderer", {}).get("accessibilityData", {}).get("label", "")
            )
            if label:
                badges.append(label)

        description_runs = r.get("descriptionSnippet", {}).get("runs", [])
        description = "".join(x.get("text", "") for x in description_runs)

        hashtags = re.findall(r"#(\w+)", description + " " + title)

        published = r.get("publishedTimeText", {}).get("simpleText", "")

        thumbnail_url = ""
        thumbnails = r.get("thumbnail", {}).get("thumbnails", [])
        if thumbnails:
            thumbnail_url = thumbnails[-1].get("url", "")

        return {
            "video_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}" if video_id else "",
            "title": title,
            "channel": channel,
            "views": view_text,
            "published": published,
            "badges": badges,
            "hashtags": list(set(hashtags)),
            "description_snippet": description,
            "thumbnail": thumbnail_url,
        }
    except Exception:
        return None


def _scrape_with_requests(category: str = "now") -> List[Dict[str, Any]]:
    if not HAS_REQUESTS:
        raise RuntimeError("requests not installed. Run: pip install requests")
    url = TRENDING_CATEGORIES.get(category, TRENDING_CATEGORIES["now"])
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    data = _extract_initial_data(resp.text)
    if not data:
        return []
    return _parse_trending_items(data)


def _scrape_with_ytdlp(category: str = "now") -> List[Dict[str, Any]]:
    """Use yt-dlp to fetch trending playlist metadata."""
    if not HAS_YTDLP:
        raise RuntimeError("yt-dlp not installed. Run: pip install yt-dlp")

    playlist_urls = {
        "now":    "https://www.youtube.com/feed/trending",
        "music":  "https://www.youtube.com/playlist?list=PLbpi6ZahtOH6Ar_3GPy3workshift",
    }
    url = playlist_urls.get(category, playlist_urls["now"])

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "playlist_items": "1:50",
    }
    results = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        entries = info.get("entries", []) if info else []
        for entry in entries:
            if not entry:
                continue
            vid_id = entry.get("id", "")
            hashtags = re.findall(r"#(\w+)", entry.get("description", "") or "")
            results.append({
                "video_id": vid_id,
                "url": f"https://www.youtube.com/watch?v={vid_id}",
                "title": entry.get("title", ""),
                "channel": entry.get("uploader", "") or entry.get("channel", ""),
                "views": str(entry.get("view_count", "")),
                "published": entry.get("upload_date", ""),
                "hashtags": list(set(hashtags)),
                "description_snippet": (entry.get("description", "") or "")[:200],
                "thumbnail": entry.get("thumbnail", ""),
                "badges": [],
            })
    return results


def scrape_trending(
    category: str = "now",
    region: str = "US",
    limit: int = 25,
    use_ytdlp: bool = False,
) -> Dict[str, Any]:
    """
    Scrape YouTube trending videos.

    Args:
        category: 'now' | 'music' | 'gaming' | 'movies'
        region: ISO country code (used with yt-dlp)
        limit: max videos to return
        use_ytdlp: prefer yt-dlp over requests scraping

    Returns:
        dict with videos list and aggregated hashtags/stats
    """
    videos = []
    method = "unknown"
    error = None

    if use_ytdlp and HAS_YTDLP:
        try:
            videos = _scrape_with_ytdlp(category)
            method = "yt-dlp"
        except Exception as e:
            error = str(e)

    if not videos and HAS_REQUESTS:
        try:
            videos = _scrape_with_requests(category)
            method = "requests"
        except Exception as e:
            error = str(e)

    if not videos and HAS_YTDLP:
        try:
            videos = _scrape_with_ytdlp(category)
            method = "yt-dlp"
        except Exception as e:
            error = str(e)

    videos = videos[:limit]

    all_hashtags: Dict[str, int] = {}
    for v in videos:
        for tag in v.get("hashtags", []):
            all_hashtags[tag.lower()] = all_hashtags.get(tag.lower(), 0) + 1

    top_hashtags = sorted(all_hashtags.items(), key=lambda x: x[1], reverse=True)[:20]

    return {
        "scraped_at": datetime.now().isoformat(),
        "category": category,
        "region": region,
        "method": method,
        "total_videos": len(videos),
        "videos": videos,
        "top_hashtags": [{"tag": f"#{t}", "count": c} for t, c in top_hashtags],
        "error": error,
    }


def extract_hashtags_from_videos(videos: List[Dict]) -> List[Dict[str, Any]]:
    """Aggregate and rank hashtags from a list of video results."""
    freq: Dict[str, int] = {}
    for v in videos:
        for tag in v.get("hashtags", []):
            clean = tag.lower().lstrip("#")
            freq[clean] = freq.get(clean, 0) + 1
    ranked = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [{"hashtag": f"#{t}", "appearances": c, "virality_score": min(c * 10, 100)} for t, c in ranked]


def get_video_details(video_url: str) -> Dict[str, Any]:
    """Get detailed metadata for a single YouTube video via yt-dlp."""
    if not HAS_YTDLP:
        raise RuntimeError("yt-dlp not installed. Run: pip install yt-dlp")
    ydl_opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
    if not info:
        return {}
    hashtags = re.findall(r"#(\w+)", info.get("description", "") or "")
    tags = info.get("tags", []) or []
    return {
        "video_id": info.get("id", ""),
        "title": info.get("title", ""),
        "channel": info.get("uploader", "") or info.get("channel", ""),
        "views": info.get("view_count", 0),
        "likes": info.get("like_count", 0),
        "comments": info.get("comment_count", 0),
        "duration": info.get("duration", 0),
        "upload_date": info.get("upload_date", ""),
        "description": (info.get("description", "") or "")[:500],
        "hashtags": list(set(hashtags)),
        "tags": tags[:20],
        "categories": info.get("categories", []),
        "thumbnail": info.get("thumbnail", ""),
        "url": video_url,
    }
