"""YouTube trending scraper — uses yt-dlp as backend."""
import json
import subprocess
import re
from typing import Any


_YT_TRENDING_URL = "https://www.youtube.com/feed/trending"
_YT_TRENDING_MUSIC_URL = "https://www.youtube.com/feed/trending?bp=4gINGgt5dE1QQ2hhcnRz"

# Trending category IDs for yt-dlp playlist extraction
_TRENDING_PLAYLISTS = {
    "general":   "https://www.youtube.com/feed/trending",
    "music":     "https://www.youtube.com/feed/trending?bp=4gINGgt5dE1QQ2hhcnRz",
    "gaming":    "https://www.youtube.com/feed/trending?bp=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D",
    "films":     "https://www.youtube.com/feed/trending?bp=4gIKGgh0cmFpbGVycw%3D%3D",
}


def _run_ytdlp(args: list[str], timeout: int = 60) -> dict[str, Any]:
    """Run yt-dlp and return parsed JSON, or raise on failure."""
    cmd = ["yt-dlp", "--no-warnings", "--quiet"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def _extract_hashtags(text: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"#(\w+)", text or "")))


def fetch_trending(category: str = "general", limit: int = 20) -> list[dict]:
    """
    Fetch YouTube trending videos using yt-dlp.

    Returns a list of dicts with keys:
      id, title, channel, views, duration, hashtags, url, thumbnail
    """
    url = _TRENDING_PLAYLISTS.get(category, _TRENDING_PLAYLISTS["general"])

    ytdlp_args = [
        "--flat-playlist",
        "--playlist-end", str(limit),
        "--dump-single-json",
        url,
    ]

    try:
        data = _run_ytdlp(ytdlp_args, timeout=90)
    except (RuntimeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"YouTube scrape failed: {exc}") from exc

    entries = data.get("entries") or []
    results = []
    for entry in entries:
        if not entry:
            continue
        vid_id = entry.get("id", "")
        title = entry.get("title", "")
        tags = entry.get("tags") or []
        desc = entry.get("description") or ""
        hashtags = _extract_hashtags(desc) + _extract_hashtags(title)
        # merge with explicit tags, deduplicate
        all_tags = list(dict.fromkeys([t.lower() for t in tags + hashtags]))
        results.append({
            "id": vid_id,
            "title": title,
            "channel": entry.get("channel") or entry.get("uploader", ""),
            "views": entry.get("view_count", 0),
            "duration": entry.get("duration", 0),
            "hashtags": all_tags,
            "url": f"https://www.youtube.com/watch?v={vid_id}",
            "thumbnail": entry.get("thumbnail", ""),
        })
    return results


def fetch_video_details(video_id: str) -> dict:
    """Fetch full metadata for a single YouTube video."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        data = _run_ytdlp(["--dump-single-json", "--skip-download", url])
    except (RuntimeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"YouTube detail fetch failed: {exc}") from exc

    desc = data.get("description") or ""
    tags = data.get("tags") or []
    hashtags = _extract_hashtags(desc) + _extract_hashtags(data.get("title", ""))
    all_tags = list(dict.fromkeys([t.lower() for t in tags + hashtags]))

    return {
        "id": data.get("id", ""),
        "title": data.get("title", ""),
        "channel": data.get("channel") or data.get("uploader", ""),
        "views": data.get("view_count", 0),
        "likes": data.get("like_count", 0),
        "comments": data.get("comment_count", 0),
        "duration": data.get("duration", 0),
        "hashtags": all_tags,
        "description": desc[:500],
        "upload_date": data.get("upload_date", ""),
        "url": url,
    }


def top_hashtags_from_trending(category: str = "general", limit: int = 20) -> list[dict]:
    """Aggregate and rank hashtags across all trending videos."""
    videos = fetch_trending(category=category, limit=limit)
    counts: dict[str, int] = {}
    for v in videos:
        for tag in v.get("hashtags", []):
            counts[tag] = counts.get(tag, 0) + 1

    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [{"hashtag": f"#{t}", "frequency": c} for t, c in ranked]
