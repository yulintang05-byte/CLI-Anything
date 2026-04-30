"""YouTube trending scraper — fetches viral trends via yt-dlp and RSS fallback."""

import subprocess
import json
import re
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional


_YT_TRENDING_RSS = "https://www.youtube.com/feeds/videos.xml?chart=trending&gl={country}"
_YT_TRENDING_URL = "https://www.youtube.com/results?search_query=trending&sp=CAM%253D"


def _run_ytdlp(args: list[str]) -> Optional[dict]:
    """Run yt-dlp and return parsed JSON output, or None if unavailable."""
    try:
        result = subprocess.run(
            ["yt-dlp"] + args,
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        pass
    return None


def fetch_youtube_trending(country: str = "US", limit: int = 20) -> dict:
    """Fetch trending videos from YouTube for a given country.

    Tries yt-dlp first (most detailed), falls back to public RSS feed.
    Returns a unified structure with titles, views, hashtags, and channel info.
    """
    # Attempt via yt-dlp
    ytdlp_data = _fetch_via_ytdlp(country, limit)
    if ytdlp_data:
        return ytdlp_data

    # Fallback to RSS
    rss_data = _fetch_via_rss(country, limit)
    if rss_data:
        return rss_data

    return _mock_trending_data(country, limit)


def _fetch_via_ytdlp(country: str, limit: int) -> Optional[dict]:
    """Fetch YouTube trending using yt-dlp."""
    url = f"https://www.youtube.com/feed/trending?gl={country}"
    data = _run_ytdlp([
        "--dump-json", "--flat-playlist",
        "--playlist-items", f"1-{limit}",
        "--no-warnings",
        url,
    ])
    if not data:
        return None

    # yt-dlp returns one JSON object per line for flat playlists
    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--flat-playlist",
             "--playlist-items", f"1-{limit}", "--no-warnings", url],
            capture_output=True, text=True, timeout=45,
        )
        if result.returncode != 0:
            return None

        videos = []
        for line in result.stdout.strip().splitlines():
            try:
                v = json.loads(line)
                hashtags = _extract_hashtags(v.get("description", "") + " " + v.get("title", ""))
                videos.append({
                    "rank": len(videos) + 1,
                    "title": v.get("title", ""),
                    "channel": v.get("uploader", v.get("channel", "")),
                    "views": v.get("view_count", 0),
                    "duration": v.get("duration", 0),
                    "upload_date": v.get("upload_date", ""),
                    "video_id": v.get("id", ""),
                    "url": f"https://youtube.com/watch?v={v.get('id', '')}",
                    "hashtags": hashtags,
                    "thumbnail": v.get("thumbnail", ""),
                    "description_snippet": (v.get("description", "") or "")[:200],
                })
            except json.JSONDecodeError:
                continue

        if not videos:
            return None

        return {
            "source": "youtube",
            "method": "yt-dlp",
            "country": country,
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "count": len(videos),
            "videos": videos,
            "trending_hashtags": _aggregate_hashtags(videos),
            "top_channels": _aggregate_channels(videos),
        }
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def _fetch_via_rss(country: str, limit: int) -> Optional[dict]:
    """Fetch YouTube trending via the public RSS/Atom feed."""
    url = _YT_TRENDING_RSS.format(country=country)
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; CLI-Anything/1.0)"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            xml_data = resp.read().decode("utf-8")

        root = ET.fromstring(xml_data)
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "yt": "http://www.youtube.com/xml/schemas/2015",
            "media": "http://search.yahoo.com/mrss/",
        }

        videos = []
        for entry in root.findall("atom:entry", ns)[:limit]:
            title = entry.findtext("atom:title", "", ns)
            video_id = entry.findtext("yt:videoId", "", ns)
            channel = entry.findtext("atom:author/atom:name", "", ns)
            published = entry.findtext("atom:published", "", ns)
            hashtags = _extract_hashtags(title)

            views_el = entry.find("media:group/media:community/media:statistics", ns)
            views = int(views_el.get("views", 0)) if views_el is not None else 0

            videos.append({
                "rank": len(videos) + 1,
                "title": title,
                "channel": channel,
                "views": views,
                "duration": 0,
                "upload_date": published[:10].replace("-", "") if published else "",
                "video_id": video_id,
                "url": f"https://youtube.com/watch?v={video_id}",
                "hashtags": hashtags,
                "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                "description_snippet": "",
            })

        if not videos:
            return None

        return {
            "source": "youtube",
            "method": "rss",
            "country": country,
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "count": len(videos),
            "videos": videos,
            "trending_hashtags": _aggregate_hashtags(videos),
            "top_channels": _aggregate_channels(videos),
        }
    except (urllib.error.URLError, ET.ParseError, Exception):
        return None


def _mock_trending_data(country: str, limit: int) -> dict:
    """Return curated trending patterns when live data is unavailable."""
    trends = [
        {"title": "POV: you found the perfect morning routine", "channel": "LifestyleVibes", "views": 4200000, "hashtags": ["#morningroutine", "#aesthetic", "#wellness", "#productivity"]},
        {"title": "I tried viral TikTok food hacks for a week", "channel": "FoodExperiments", "views": 3800000, "hashtags": ["#foodhack", "#viral", "#cooking", "#tiktokfood"]},
        {"title": "Budget travel tips that actually work", "channel": "TravelSmart", "views": 2900000, "hashtags": ["#travel", "#budgettravel", "#travelguide", "#digitalnomad"]},
        {"title": "Day in my life as a self-employed creator", "channel": "CreatorLife", "views": 2600000, "hashtags": ["#dayinmylife", "#contentcreator", "#entrepreneur", "#sidehustle"]},
        {"title": "Outfit formula that goes viral every time", "channel": "StyleFormula", "views": 2400000, "hashtags": ["#outfit", "#fashion", "#ootd", "#styleinspo"]},
        {"title": "Money habits that changed my life at 25", "channel": "FinanceWith", "views": 2200000, "hashtags": ["#money", "#personalfinance", "#investing", "#savingmoney"]},
        {"title": "Gym transformation: realistic 90-day results", "channel": "FitnessReal", "views": 2100000, "hashtags": ["#gym", "#transformation", "#fitness", "#workout"]},
        {"title": "10 things I stopped buying to save money", "channel": "MinimalistMind", "views": 1900000, "hashtags": ["#minimalism", "#savemoney", "#frugal", "#lifestyle"]},
        {"title": "Aesthetic room makeover under $100", "channel": "RoomDecor", "views": 1800000, "hashtags": ["#roomdecor", "#aesthetic", "#homedecor", "#diy"]},
        {"title": "Passive income streams that work in 2025", "channel": "IncomeHacks", "views": 1700000, "hashtags": ["#passiveincome", "#makemoneyonline", "#sidehustle", "#entrepreneur"]},
    ]

    videos = []
    for i, t in enumerate(trends[:limit]):
        videos.append({
            "rank": i + 1,
            "title": t["title"],
            "channel": t["channel"],
            "views": t["views"],
            "duration": 0,
            "upload_date": "",
            "video_id": f"mock_{i}",
            "url": "",
            "hashtags": t["hashtags"],
            "thumbnail": "",
            "description_snippet": "",
        })

    return {
        "source": "youtube",
        "method": "curated-fallback",
        "country": country,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "count": len(videos),
        "videos": videos,
        "trending_hashtags": _aggregate_hashtags(videos),
        "top_channels": _aggregate_channels(videos),
        "note": "Live scraping unavailable — using curated trend patterns. Install yt-dlp for live data.",
    }


def _extract_hashtags(text: str) -> list[str]:
    """Extract hashtags from a text string."""
    return list(dict.fromkeys(re.findall(r"#\w+", text.lower())))


def _aggregate_hashtags(videos: list[dict]) -> list[dict]:
    """Count and rank hashtags across all videos."""
    counts: dict[str, int] = {}
    for v in videos:
        for tag in v.get("hashtags", []):
            counts[tag] = counts.get(tag, 0) + 1
    return [
        {"tag": tag, "occurrences": count}
        for tag, count in sorted(counts.items(), key=lambda x: -x[1])
    ]


def _aggregate_channels(videos: list[dict]) -> list[dict]:
    """Rank channels by views."""
    channel_views: dict[str, int] = {}
    for v in videos:
        ch = v.get("channel", "")
        if ch:
            channel_views[ch] = channel_views.get(ch, 0) + v.get("views", 0)
    return [
        {"channel": ch, "total_views": views}
        for ch, views in sorted(channel_views.items(), key=lambda x: -x[1])[:10]
    ]


def extract_music_cues(videos: list[dict]) -> list[str]:
    """Extract music-related keywords from video titles and descriptions."""
    music_patterns = [
        r"\busing\s+(.+?)\s+by\b",
        r"\bsound\s*:\s*(.+?)(?:\s|$)",
        r"\baudio\s*:\s*(.+?)(?:\s|$)",
    ]
    cues = []
    for v in videos:
        text = v.get("title", "") + " " + v.get("description_snippet", "")
        for pattern in music_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            cues.extend(matches)
    return list(dict.fromkeys(cues))
