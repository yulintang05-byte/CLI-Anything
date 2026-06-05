"""Social media backend helpers — platform clients, rate limiting, error handling."""

import time
import json
import subprocess
import sys
from typing import Optional
import requests

from cli_anything.social_trends.core.youtube_trends import YouTubeTrends
from cli_anything.social_trends.core.tiktok_trends import TikTokTrends


def get_youtube_client(api_key: str) -> YouTubeTrends:
    return YouTubeTrends(api_key=api_key)


def get_tiktok_client(cookie: Optional[str] = None) -> TikTokTrends:
    return TikTokTrends(cookie=cookie)


def check_ytdlp_available() -> bool:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--version"],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


def check_youtube_api_key(api_key: str) -> dict:
    try:
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={"part": "snippet", "chart": "mostPopular", "maxResults": 1, "key": api_key},
            timeout=10,
        )
        if resp.status_code == 200:
            return {"valid": True, "message": "YouTube API key is valid"}
        data = resp.json()
        error_msg = data.get("error", {}).get("message", "Unknown error")
        return {"valid": False, "message": error_msg}
    except Exception as e:
        return {"valid": False, "message": str(e)}


def merge_platform_trends(yt_hashtags: list[dict], tt_hashtags: list[dict], top_n: int = 20) -> list[dict]:
    """Merge YouTube and TikTok hashtag trends into a unified cross-platform list."""
    combined: dict[str, dict] = {}

    for item in yt_hashtags:
        tag = item.get("hashtag", "").lower()
        if tag:
            combined[tag] = {
                "hashtag": tag,
                "youtube_score": item.get("score", 0),
                "youtube_views": item.get("total_views_on_trending", 0),
                "tiktok_views": 0,
                "tiktok_appearances": 0,
                "platforms": ["youtube"],
            }

    for item in tt_hashtags:
        tag = item.get("hashtag", "").lower()
        if not tag:
            continue
        if tag in combined:
            combined[tag]["platforms"].append("tiktok")
            combined[tag]["tiktok_views"] = item.get("total_views", item.get("view_count", 0))
            combined[tag]["tiktok_appearances"] = item.get("appearances_in_trending", item.get("video_count", 0))
        else:
            combined[tag] = {
                "hashtag": tag,
                "youtube_score": 0,
                "youtube_views": 0,
                "tiktok_views": item.get("total_views", item.get("view_count", 0)),
                "tiktok_appearances": item.get("appearances_in_trending", item.get("video_count", 0)),
                "platforms": ["tiktok"],
            }

    # Score: cross-platform tags rank highest
    for tag, data in combined.items():
        cross_platform_bonus = 2.0 if len(data["platforms"]) > 1 else 1.0
        data["cross_platform_score"] = round(
            (data["youtube_score"] + data["tiktok_appearances"] * 2) * cross_platform_bonus, 2
        )

    ranked = sorted(combined.values(), key=lambda x: x["cross_platform_score"], reverse=True)
    return ranked[:top_n]
