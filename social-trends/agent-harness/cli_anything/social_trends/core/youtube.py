"""YouTube trends scraper — fetches trending videos, shorts, music, and hashtags."""
from __future__ import annotations

import json
import re
import subprocess
import urllib.request
import urllib.error
from dataclasses import dataclass, asdict
from typing import Optional


TRENDING_URLS = {
    "now": "https://www.youtube.com/feed/trending",
    "music": "https://www.youtube.com/feed/trending?bp=4gINGgt5dG1hX2NoYXJ0cw%3D%3D",
    "gaming": "https://www.youtube.com/feed/trending?bp=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D",
    "movies": "https://www.youtube.com/feed/trending?bp=4gIKGgh0cmFpbGVycw%3D%3D",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


@dataclass
class YTVideo:
    rank: int
    video_id: str
    title: str
    channel: str
    views: str
    duration: str
    hashtags: list[str]
    description_snippet: str
    url: str
    thumbnail: str
    category: str

    def to_dict(self) -> dict:
        return asdict(self)


def _fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error fetching {url}: {exc}") from exc


def _extract_initial_data(html: str) -> dict:
    """Pull ytInitialData JSON from a YouTube page."""
    match = re.search(r"var ytInitialData\s*=\s*(\{.+?\});\s*</script>", html, re.DOTALL)
    if not match:
        match = re.search(r"ytInitialData\s*=\s*(\{.+?\});", html, re.DOTALL)
    if not match:
        raise RuntimeError("Could not locate ytInitialData in page HTML")
    return json.loads(match.group(1))


def _safe_str(obj, *keys, default="") -> str:
    for k in keys:
        if isinstance(obj, dict):
            obj = obj.get(k, {})
        elif isinstance(obj, list):
            obj = obj[0] if obj else {}
        else:
            return default
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return obj.get("simpleText", obj.get("runs", [{}])[0].get("text", default) if obj.get("runs") else default)
    return default


def _extract_runs_text(obj) -> str:
    if isinstance(obj, dict):
        if "simpleText" in obj:
            return obj["simpleText"]
        if "runs" in obj:
            return "".join(r.get("text", "") for r in obj["runs"])
    return ""


def _parse_video_renderer(renderer: dict, rank: int, category: str) -> Optional[YTVideo]:
    vid_id = renderer.get("videoId", "")
    if not vid_id:
        return None

    title = _extract_runs_text(renderer.get("title", {}))
    channel = _extract_runs_text(renderer.get("ownerText", renderer.get("shortBylineText", {})))
    views = _safe_str(renderer.get("viewCountText", {}), "simpleText") or _extract_runs_text(
        renderer.get("viewCountText", {})
    )
    duration = _safe_str(renderer.get("lengthText", {}), "simpleText") or _extract_runs_text(
        renderer.get("lengthText", {})
    )
    desc_obj = renderer.get("detailedMetadataSnippets", [{}])
    snippet_text = ""
    if desc_obj and isinstance(desc_obj, list):
        snippet_text = _extract_runs_text(desc_obj[0].get("snippetText", {}))

    # Pull hashtags from badges and title
    hashtags: list[str] = []
    for badge in renderer.get("badges", []):
        label = _safe_str(badge.get("metadataBadgeRenderer", {}), "label")
        if label:
            hashtags.append(label)
    for word in (title + " " + snippet_text).split():
        if word.startswith("#") and len(word) > 1:
            tag = word.rstrip(".,!?").lower()
            if tag not in hashtags:
                hashtags.append(tag)

    thumb_list = renderer.get("thumbnail", {}).get("thumbnails", [])
    thumbnail = thumb_list[-1].get("url", "") if thumb_list else ""

    return YTVideo(
        rank=rank,
        video_id=vid_id,
        title=title,
        channel=channel,
        views=views,
        duration=duration,
        hashtags=hashtags,
        description_snippet=snippet_text[:200],
        url=f"https://www.youtube.com/watch?v={vid_id}",
        thumbnail=thumbnail,
        category=category,
    )


def _walk_renderers(data: dict) -> list[dict]:
    """DFS through ytInitialData to find all videoRenderer nodes."""
    results: list[dict] = []
    stack = [data]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            if "videoRenderer" in node:
                results.append(node["videoRenderer"])
            for v in node.values():
                stack.append(v)
        elif isinstance(node, list):
            stack.extend(node)
    return results


def fetch_trending(category: str = "now", limit: int = 20) -> list[YTVideo]:
    """Return up to `limit` trending YouTube videos for the given category."""
    url = TRENDING_URLS.get(category, TRENDING_URLS["now"])
    html = _fetch_html(url)
    data = _extract_initial_data(html)
    renderers = _walk_renderers(data)
    videos: list[YTVideo] = []
    for i, r in enumerate(renderers[:limit], start=1):
        vid = _parse_video_renderer(r, i, category)
        if vid:
            videos.append(vid)
    return videos


def fetch_trending_via_ytdlp(category: str = "now", limit: int = 20) -> list[YTVideo]:
    """Fallback: use yt-dlp to fetch trending (requires yt-dlp installed)."""
    url = TRENDING_URLS.get(category, TRENDING_URLS["now"])
    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--flat-playlist", "--playlist-end", str(limit), url],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except FileNotFoundError:
        raise RuntimeError("yt-dlp not found. Install with: pip install yt-dlp")
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp error: {result.stderr[:300]}")

    videos: list[YTVideo] = []
    for i, line in enumerate(result.stdout.strip().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        vid_id = entry.get("id", "")
        hashtags = [t for t in entry.get("tags", []) if t.startswith("#")]
        videos.append(
            YTVideo(
                rank=i,
                video_id=vid_id,
                title=entry.get("title", ""),
                channel=entry.get("uploader", entry.get("channel", "")),
                views=str(entry.get("view_count", "")),
                duration=str(entry.get("duration_string", entry.get("duration", ""))),
                hashtags=hashtags,
                description_snippet=(entry.get("description") or "")[:200],
                url=entry.get("webpage_url", f"https://www.youtube.com/watch?v={vid_id}"),
                thumbnail=entry.get("thumbnail", ""),
                category=category,
            )
        )
    return videos


def fetch_trending_best(category: str = "now", limit: int = 20) -> list[YTVideo]:
    """Try HTML scrape first; fall back to yt-dlp."""
    try:
        videos = fetch_trending(category=category, limit=limit)
        if videos:
            return videos
    except Exception:
        pass
    return fetch_trending_via_ytdlp(category=category, limit=limit)


def extract_top_hashtags(videos: list[YTVideo], top_n: int = 30) -> list[dict]:
    """Aggregate hashtag frequency across video list."""
    counts: dict[str, int] = {}
    for v in videos:
        for tag in v.hashtags:
            counts[tag] = counts.get(tag, 0) + 1
    sorted_tags = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [{"hashtag": t, "occurrences": c} for t, c in sorted_tags[:top_n]]


def extract_top_channels(videos: list[YTVideo], top_n: int = 10) -> list[dict]:
    counts: dict[str, int] = {}
    for v in videos:
        if v.channel:
            counts[v.channel] = counts.get(v.channel, 0) + 1
    sorted_ch = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [{"channel": c, "trending_videos": n} for c, n in sorted_ch[:top_n]]
