"""TikTok trend discovery via yt-dlp and public endpoints.

No API key required — uses yt-dlp to fetch public TikTok metadata and
the public discover endpoint for hashtag/sound trends.

Install yt-dlp: pip install yt-dlp
"""

import re
import json
import subprocess
import sys
from collections import Counter
from typing import Optional

import requests

_DISCOVER_URL = "https://www.tiktok.com/api/discover/type/"
_TRENDING_URL = "https://www.tiktok.com/api/trending/feed/"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.tiktok.com/",
    "Accept-Language": "en-US,en;q=0.9",
}


class TikTokTrends:
    """Fetch trending TikTok videos, hashtags, and sounds."""

    def __init__(self, cookie: Optional[str] = None):
        self.session = requests.Session()
        self.session.headers.update(_HEADERS)
        if cookie:
            self.session.headers["Cookie"] = cookie

    # ── Video trends ──────────────────────────────────────────────────────────

    def get_trending_videos(self, count: int = 30) -> list[dict]:
        """Fetch trending TikTok videos using yt-dlp."""
        try:
            return self._fetch_via_ytdlp(count)
        except Exception as e:
            return [{"error": f"yt-dlp fetch failed: {e}", "tip": "Run: pip install yt-dlp"}]

    def _fetch_via_ytdlp(self, count: int) -> list[dict]:
        """Use yt-dlp subprocess to get trending TikTok video metadata."""
        cmd = [
            sys.executable, "-m", "yt_dlp",
            "--dump-json",
            "--flat-playlist",
            "--playlist-end", str(count),
            "--no-warnings",
            "--quiet",
            "https://www.tiktok.com/trending",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        videos = []
        for line in proc.stdout.strip().splitlines():
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            description = item.get("description") or item.get("title") or ""
            videos.append({
                "id": item.get("id", ""),
                "title": description[:150],
                "author": item.get("uploader") or item.get("channel") or "",
                "like_count": item.get("like_count", 0) or 0,
                "view_count": item.get("view_count", 0) or 0,
                "comment_count": item.get("comment_count", 0) or 0,
                "duration": item.get("duration", 0) or 0,
                "hashtags": _extract_hashtags(description),
                "music_title": _safe_get(item, "music", "title"),
                "music_author": _safe_get(item, "music", "author"),
                "url": item.get("webpage_url") or f"https://www.tiktok.com/@{item.get('uploader', '')}/video/{item.get('id', '')}",
                "thumbnail": item.get("thumbnail", ""),
            })
        return videos

    # ── Hashtag trends ────────────────────────────────────────────────────────

    def get_trending_hashtags(self, top_n: int = 30) -> list[dict]:
        """Aggregate trending hashtags from TikTok discover endpoint + video metadata."""
        hashtags: list[dict] = []

        # Try TikTok discover API (type=1 = hashtags)
        try:
            resp = self.session.get(
                _DISCOVER_URL,
                params={"discoverType": 1, "needItemList": False, "keyWord": "", "offset": 0, "count": top_n},
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("challengeInfoList", []):
                    info = item.get("challengeInfo", {})
                    stats = item.get("stats", {})
                    hashtags.append({
                        "hashtag": f"#{info.get('challengeName', '')}",
                        "view_count": int(stats.get("viewCount", 0)),
                        "video_count": int(stats.get("videoCount", 0)),
                        "type": "tiktok_discover",
                    })
        except Exception:
            pass

        # Fallback: extract from trending videos
        if not hashtags:
            try:
                videos = self.get_trending_videos(count=50)
                counter: Counter = Counter()
                view_weight: dict = {}
                for v in videos:
                    views = v.get("view_count", 0) or 0
                    for tag in v.get("hashtags", []):
                        tl = tag.lower().strip()
                        if tl:
                            counter[tl] += 1
                            view_weight[tl] = view_weight.get(tl, 0) + views
                for tag, count in counter.most_common(top_n):
                    hashtags.append({
                        "hashtag": f"#{tag}",
                        "appearances_in_trending": count,
                        "total_views": view_weight.get(tag, 0),
                        "type": "extracted_from_trending_videos",
                    })
            except Exception:
                pass

        return hashtags[:top_n]

    # ── Sound / music trends ──────────────────────────────────────────────────

    def get_trending_sounds(self, top_n: int = 30) -> list[dict]:
        """Extract trending sounds/music from TikTok trending videos."""
        try:
            videos = self.get_trending_videos(count=50)
        except Exception:
            return []

        music_counter: Counter = Counter()
        music_meta: dict = {}
        for v in videos:
            mt = v.get("music_title") or ""
            ma = v.get("music_author") or ""
            if mt:
                key = mt.lower()
                music_counter[key] += 1
                views = v.get("view_count", 0) or 0
                if key not in music_meta:
                    music_meta[key] = {"title": mt, "author": ma, "total_views": 0, "video_count": 0}
                music_meta[key]["total_views"] += views
                music_meta[key]["video_count"] += 1

        ranked = sorted(music_counter.keys(), key=lambda k: music_counter[k], reverse=True)[:top_n]
        return [
            {
                "music_title": music_meta[k]["title"],
                "artist": music_meta[k]["author"],
                "trending_videos_count": music_meta[k]["video_count"],
                "total_views": music_meta[k]["total_views"],
            }
            for k in ranked
            if k in music_meta
        ]

    # ── User profile metadata ─────────────────────────────────────────────────

    def get_user_videos(self, username: str, count: int = 20) -> list[dict]:
        """Fetch recent public videos for a TikTok user via yt-dlp."""
        url = f"https://www.tiktok.com/@{username.lstrip('@')}"
        cmd = [
            sys.executable, "-m", "yt_dlp",
            "--dump-json",
            "--flat-playlist",
            "--playlist-end", str(count),
            "--no-warnings",
            "--quiet",
            url,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        videos = []
        for line in proc.stdout.strip().splitlines():
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            desc = item.get("description") or item.get("title") or ""
            videos.append({
                "id": item.get("id", ""),
                "title": desc[:150],
                "like_count": item.get("like_count", 0) or 0,
                "view_count": item.get("view_count", 0) or 0,
                "comment_count": item.get("comment_count", 0) or 0,
                "duration": item.get("duration", 0) or 0,
                "hashtags": _extract_hashtags(desc),
                "upload_date": item.get("upload_date", ""),
                "url": item.get("webpage_url", ""),
            })
        return videos


# ── Helpers ────────────────────────────────────────────────────────────────────

def _extract_hashtags(text: str) -> list[str]:
    return [m.lstrip("#").lower() for m in re.findall(r"#\w+", text)]


def _safe_get(d: dict, *keys):
    val = d
    for k in keys:
        if not isinstance(val, dict):
            return ""
        val = val.get(k, "")
    return val or ""
