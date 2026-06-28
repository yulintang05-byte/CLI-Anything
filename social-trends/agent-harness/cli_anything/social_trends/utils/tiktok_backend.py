"""TikTok trend and sound discovery backend.

Uses yt-dlp (which supports TikTok) to fetch public trending metadata.
No credentials or API keys required for public trend data.
"""

import json
import subprocess
from typing import Dict, Any, List, Optional


TIKTOK_TRENDING_URLS = {
    "": "https://www.tiktok.com/trending",
    "dance": "https://www.tiktok.com/tag/dance",
    "comedy": "https://www.tiktok.com/tag/comedy",
    "food": "https://www.tiktok.com/tag/food",
    "beauty": "https://www.tiktok.com/tag/beauty",
    "fitness": "https://www.tiktok.com/tag/fitness",
    "fashion": "https://www.tiktok.com/tag/fashion",
    "music": "https://www.tiktok.com/tag/music",
    "travel": "https://www.tiktok.com/tag/travel",
    "pets": "https://www.tiktok.com/tag/pets",
    "sports": "https://www.tiktok.com/tag/sports",
    "education": "https://www.tiktok.com/tag/education",
}


class TikTokBackend:
    """Fetches TikTok trending content metadata via yt-dlp."""

    def fetch_trending(
        self,
        category: str = "",
        region: str = "US",
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Fetch trending TikTok videos for a category."""
        url = TIKTOK_TRENDING_URLS.get(category.lower(), TIKTOK_TRENDING_URLS[""])

        try:
            return self._run_ytdlp(url, limit)
        except RuntimeError:
            # Fallback to hashtag search if trending page fails
            if category:
                fallback_url = f"https://www.tiktok.com/tag/{category}"
                try:
                    return self._run_ytdlp(fallback_url, limit)
                except RuntimeError:
                    pass
            return []

    def fetch_trending_sounds(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Extract unique sounds/music from trending TikTok videos."""
        videos = self.fetch_trending(limit=min(limit * 2, 40))
        sounds: Dict[str, Dict[str, Any]] = {}

        for video in videos:
            sound_id = video.get("sound_id")
            if not sound_id:
                continue
            if sound_id not in sounds:
                sounds[sound_id] = {
                    "track_id": f"tt_{sound_id}",
                    "title": video.get("sound_title", "Original Sound"),
                    "artist": video.get("sound_author", "Unknown Artist"),
                    "genre": "trending",
                    "mood": "varies",
                    "use_count": video.get("view_count", 0),
                    "is_trending": True,
                    "source_url": video.get("url", ""),
                    "duration_sec": video.get("duration_sec", 0),
                    "video_count": 1,
                }
            else:
                sounds[sound_id]["use_count"] += video.get("view_count", 0)
                sounds[sound_id]["video_count"] += 1

        result = sorted(sounds.values(), key=lambda s: s["use_count"], reverse=True)
        return result[:limit]

    def _run_ytdlp(self, url: str, limit: int) -> List[Dict[str, Any]]:
        """Run yt-dlp to extract video metadata from a TikTok URL."""
        try:
            cmd = [
                "yt-dlp",
                "--dump-json",
                "--flat-playlist",
                "--playlist-end", str(min(limit, 30)),
                "--no-warnings",
                "--quiet",
                "--user-agent",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
                url,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        except FileNotFoundError:
            raise RuntimeError(
                "yt-dlp not found. Install with: pip install yt-dlp\n"
                "TikTok trend fetching requires yt-dlp."
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("yt-dlp timed out fetching TikTok trending.")

        if result.returncode != 0 and not result.stdout.strip():
            raise RuntimeError(f"yt-dlp TikTok failed: {result.stderr[:300]}")

        results = []
        for line in result.stdout.strip().splitlines():
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue

            tags = item.get("tags") or []
            description = item.get("description") or item.get("title", "")

            # Extract hashtags from description
            hashtags = list({
                word.lower() for word in description.split()
                if word.startswith("#")
            })
            for tag in tags:
                formatted = f"#{tag.lower().replace(' ', '')}"
                if formatted not in hashtags:
                    hashtags.append(formatted)

            # Extract sound info
            music = item.get("music_info") or {}
            sound_id = (
                music.get("id") or
                item.get("music_id") or
                str(hash(music.get("title", "")))[:8]
            )

            results.append({
                "video_id": item.get("id", ""),
                "platform": "tiktok",
                "title": item.get("title") or description[:100],
                "description": description[:200],
                "author": item.get("uploader") or item.get("creator", ""),
                "published_at": item.get("upload_date", ""),
                "region": item.get("region", ""),
                "view_count": item.get("view_count") or 0,
                "like_count": item.get("like_count") or 0,
                "comment_count": item.get("comment_count") or 0,
                "share_count": item.get("repost_count") or 0,
                "hashtags": hashtags[:15],
                "thumbnail": item.get("thumbnail", ""),
                "url": item.get("webpage_url") or f"https://www.tiktok.com/@{item.get('uploader', '')}/video/{item.get('id', '')}",
                "duration_sec": item.get("duration") or 0,
                "sound_id": sound_id,
                "sound_title": music.get("title") or item.get("music", ""),
                "sound_author": music.get("author") or "",
                "source": "yt-dlp",
            })

        return results
