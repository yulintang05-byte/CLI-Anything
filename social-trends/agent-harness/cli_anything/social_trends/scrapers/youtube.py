"""YouTube trending scraper — no API key required (uses yt-dlp + HTML fallback)."""

import json
import subprocess
import re
import time
from typing import Optional
import urllib.request
import urllib.parse
import urllib.error


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

_TRENDING_URL = "https://www.youtube.com/feed/trending"
_TRENDING_MUSIC_URL = "https://www.youtube.com/feed/trending?bp=4gINGgt5dG1hX2NoYXJ0cw%3D%3D"
_YT_SEARCH_API = "https://www.youtube.com/youtubei/v1/search"


def _yt_initial_data(html: str) -> Optional[dict]:
    """Extract ytInitialData JSON blob from YouTube HTML page."""
    match = re.search(r"var ytInitialData\s*=\s*(\{.*?\});</script>", html, re.DOTALL)
    if not match:
        match = re.search(r"ytInitialData\s*=\s*(\{.*?\});", html, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def _fetch_url(url: str, timeout: int = 15) -> Optional[str]:
    req = urllib.request.Request(url, headers=_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def _extract_videos_from_ytdata(data: dict) -> list[dict]:
    """Walk ytInitialData to pull video items."""
    results = []
    try:
        # Navigate into the trending feed sections
        tabs = (
            data.get("contents", {})
            .get("twoColumnBrowseResultsRenderer", {})
            .get("tabs", [])
        )
        for tab in tabs:
            content = tab.get("tabRenderer", {}).get("content", {})
            sections = content.get("sectionListRenderer", {}).get("contents", [])
            for section in sections:
                items = (
                    section.get("itemSectionRenderer", {}).get("contents", [])
                )
                for item in items:
                    shelf = item.get("shelfRenderer", {})
                    shelf_items = (
                        shelf.get("content", {})
                        .get("expandedShelfContentsRenderer", {})
                        .get("items", [])
                    )
                    for si in shelf_items:
                        vr = si.get("videoRenderer", {})
                        if not vr:
                            continue
                        vid_id = vr.get("videoId", "")
                        title_runs = vr.get("title", {}).get("runs", [])
                        title = "".join(r.get("text", "") for r in title_runs)
                        channel_runs = (
                            vr.get("ownerText", {}).get("runs", [])
                            or vr.get("longBylineText", {}).get("runs", [])
                        )
                        channel = "".join(r.get("text", "") for r in channel_runs)
                        views_text = vr.get("viewCountText", {}).get("simpleText", "")
                        badges = [
                            b.get("metadataBadgeRenderer", {}).get("label", "")
                            for b in vr.get("badges", [])
                        ]
                        results.append(
                            {
                                "video_id": vid_id,
                                "url": f"https://www.youtube.com/watch?v={vid_id}",
                                "title": title,
                                "channel": channel,
                                "views": views_text,
                                "badges": [b for b in badges if b],
                            }
                        )
    except Exception:
        pass
    return results


def _try_yt_dlp(url: str, max_items: int = 30) -> list[dict]:
    """Use yt-dlp to pull feed metadata if available."""
    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--flat-playlist",
                "--dump-single-json",
                "--playlist-end",
                str(max_items),
                "--no-warnings",
                "--quiet",
                url,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            entries = data.get("entries", [])
            items = []
            for e in entries:
                if not e:
                    continue
                items.append(
                    {
                        "video_id": e.get("id", ""),
                        "url": e.get("webpage_url") or f"https://www.youtube.com/watch?v={e.get('id','')}",
                        "title": e.get("title", ""),
                        "channel": e.get("uploader") or e.get("channel", ""),
                        "views": str(e.get("view_count", "")),
                        "badges": [],
                    }
                )
            return items
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return []


def get_trending_videos(region: str = "US", max_results: int = 30) -> list[dict]:
    """
    Fetch YouTube trending videos.
    Tries yt-dlp first, falls back to HTML scraping.
    """
    # Try yt-dlp first (most reliable)
    items = _try_yt_dlp(
        f"https://www.youtube.com/feed/trending?gl={region}", max_results
    )
    if items:
        return items[:max_results]

    # Fallback: direct HTML scrape
    html = _fetch_url(f"{_TRENDING_URL}?gl={region}")
    if not html:
        return []
    data = _yt_initial_data(html)
    if not data:
        return []
    return _extract_videos_from_ytdata(data)[:max_results]


def get_trending_music(region: str = "US", max_results: int = 20) -> list[dict]:
    """Fetch YouTube Music trending chart."""
    items = _try_yt_dlp(
        f"{_TRENDING_MUSIC_URL}&gl={region}", max_results
    )
    if items:
        return items[:max_results]

    html = _fetch_url(f"{_TRENDING_MUSIC_URL}&gl={region}")
    if not html:
        return []
    data = _yt_initial_data(html)
    if not data:
        return []
    return _extract_videos_from_ytdata(data)[:max_results]


def extract_hashtags_from_titles(videos: list[dict]) -> list[dict]:
    """
    Pull hashtags from video titles + derive top hashtag candidates
    from common words in trending titles.
    """
    import re
    from collections import Counter

    hashtags: list[str] = []
    word_counter: Counter = Counter()

    for v in videos:
        title = v.get("title", "")
        # Explicit hashtags in title
        for tag in re.findall(r"#(\w+)", title):
            hashtags.append(tag.lower())
        # Count meaningful words (len >= 4, skip common stopwords)
        stopwords = {
            "with", "this", "that", "from", "have", "your", "what",
            "will", "been", "they", "when", "were", "their", "about",
            "into", "than", "then", "more", "also", "only", "some",
        }
        for word in re.findall(r"\b[a-zA-Z]{4,}\b", title.lower()):
            if word not in stopwords:
                word_counter[word] += 1

    # Explicit hashtag frequency
    tag_counter = Counter(hashtags)
    result = []

    # Explicit hashtags first
    for tag, count in tag_counter.most_common(15):
        result.append({"hashtag": f"#{tag}", "source": "explicit", "frequency": count})

    # Derived hashtag candidates from popular title words
    for word, count in word_counter.most_common(20):
        if count >= 2 and f"#{word}" not in [r["hashtag"] for r in result]:
            result.append({"hashtag": f"#{word}", "source": "derived", "frequency": count})

    return result


def search_trending_topic(query: str, max_results: int = 10) -> list[dict]:
    """Search YouTube for a trending topic via yt-dlp."""
    items = _try_yt_dlp(
        f"ytsearch{max_results}:{query}", max_results
    )
    return items
