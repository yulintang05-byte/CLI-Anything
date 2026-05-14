"""Trending music and audio tracker for TikTok and YouTube Shorts/Reels."""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass, field, asdict
from typing import Optional


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class TrendingSound:
    rank: int
    title: str
    artist: str
    platform: str
    url: str
    use_count: Optional[int] = None
    duration_seconds: Optional[int] = None
    mood: Optional[str] = None
    bpm: Optional[int] = None
    genre: Optional[str] = None
    viral_niches: list[str] = field(default_factory=list)
    is_original: bool = False  # TikTok original sound vs licensed track

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MusicTrendsResult:
    platform: str
    region: str
    fetched_at: str
    sounds: list[TrendingSound]

    def to_dict(self) -> dict:
        return {
            "platform": self.platform,
            "region": self.region,
            "fetched_at": self.fetched_at,
            "count": len(self.sounds),
            "sounds": [s.to_dict() for s in self.sounds],
        }


# ---------------------------------------------------------------------------
# TikTok trending sounds (Creative Center)
# ---------------------------------------------------------------------------

TIKTOK_MUSIC_API = (
    "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/sound/list"
)


def _cc_headers() -> dict:
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://ads.tiktok.com",
        "Referer": "https://ads.tiktok.com/",
    }


def fetch_tiktok_trending_sounds(
    region: str = "US",
    period: int = 7,
    limit: int = 25,
) -> MusicTrendsResult:
    """
    Fetch trending sounds from TikTok Creative Center (public endpoint).
    period: 1, 7, 30 (days)
    """
    url = (
        f"{TIKTOK_MUSIC_API}"
        f"?period={period}&region_code={region.upper()}"
        f"&page=1&limit={min(limit, 50)}&country_code=US&language=en"
    )
    req = urllib.request.Request(url, headers=_cc_headers())
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(
            f"TikTok Creative Center sounds error {e.code}: {e.read().decode()}"
        ) from e
    except Exception as e:
        raise RuntimeError(f"Failed to fetch TikTok trending sounds: {e}") from e

    items = (
        data.get("data", {}).get("list", [])
        or data.get("data", {}).get("sound_list", [])
        or []
    )

    sounds: list[TrendingSound] = []
    for rank, item in enumerate(items[:limit], start=1):
        name = item.get("sound_name") or item.get("title", "Unknown")
        artist = item.get("author_name") or item.get("artist", "")
        sound_id = item.get("sound_id") or item.get("id", "")
        uses = item.get("video_cnt") or item.get("use_count", 0)
        duration = item.get("duration") or item.get("duration_in_sec")

        sounds.append(TrendingSound(
            rank=rank,
            title=name,
            artist=artist,
            platform="tiktok",
            url=f"https://www.tiktok.com/music/{urllib.parse.quote(name)}-{sound_id}" if sound_id else "https://www.tiktok.com/music/",
            use_count=uses,
            duration_seconds=duration,
            is_original=not bool(artist),
        ))

    return MusicTrendsResult(
        platform="tiktok",
        region=region.upper(),
        fetched_at=_now_iso(),
        sounds=sounds,
    )


# ---------------------------------------------------------------------------
# YouTube trending music (via YouTube Data API music category)
# ---------------------------------------------------------------------------

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


def fetch_youtube_trending_music(
    api_key: str,
    region: str = "US",
    limit: int = 25,
) -> MusicTrendsResult:
    """Fetch trending music videos from YouTube Data API v3 (category=10 = Music)."""
    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region.upper(),
        "videoCategoryId": "10",
        "maxResults": min(limit, 50),
        "key": api_key,
    }
    url = f"{YOUTUBE_API_BASE}/videos?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"YouTube API error {e.code}: {e.read().decode()}") from e

    sounds: list[TrendingSound] = []
    for rank, item in enumerate(data.get("items", []), start=1):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        vid_id = item.get("id", "")
        title = snippet.get("title", "")
        channel = snippet.get("channelTitle", "")
        tags = snippet.get("tags", [])
        genre = _infer_genre_from_tags(tags)

        sounds.append(TrendingSound(
            rank=rank,
            title=title,
            artist=channel,
            platform="youtube",
            url=f"https://youtu.be/{vid_id}",
            use_count=int(stats.get("viewCount", 0)),
            genre=genre,
            viral_niches=_infer_niches_from_tags(tags),
        ))

    return MusicTrendsResult(
        platform="youtube",
        region=region.upper(),
        fetched_at=_now_iso(),
        sounds=sounds,
    )


# ---------------------------------------------------------------------------
# Music strategy guide — which sounds to use and when
# ---------------------------------------------------------------------------

SOUND_STRATEGY = {
    "viral_original": {
        "description": "TikTok original sounds that are blowing up right now",
        "best_for": ["memes", "trends", "relatable content", "duets", "stitches"],
        "tips": [
            "Use the sound within the first 24-48 hours of it going viral.",
            "Search the sound's page to see what content is performing best.",
            "Add your own spin — don't just copy the trend exactly.",
            "Use the sound at the correct timestamp (usually the hook).",
        ],
    },
    "popular_licensed": {
        "description": "Licensed pop/hip-hop tracks with millions of uses",
        "best_for": ["dancing", "fashion", "lifestyle", "GRWM", "vlogs"],
        "tips": [
            "These sounds give discoverability boost because TikTok promotes them.",
            "Use the trending clip (specific 15-30 second section everyone uses).",
            "Pair with trending visual effects or transitions.",
            "Post during peak hours for your audience (7pm-10pm local time).",
        ],
    },
    "niche_specific": {
        "description": "Sounds popular within your specific niche community",
        "best_for": ["niche retention", "community building", "credibility"],
        "tips": [
            "These build trust with your niche audience faster.",
            "Check which sounds top creators in your niche use.",
            "Recurring sounds help followers recognize your style.",
            "Good for educational, POV, or niche-specific content.",
        ],
    },
    "original_audio": {
        "description": "Your own voiceover, music, or created audio",
        "best_for": ["brand building", "viral hooks", "educational content"],
        "tips": [
            "If your original audio goes viral, you get massive exposure.",
            "Clear, confident voiceovers perform well on educational content.",
            "Add background lo-fi or ambient music behind voice.",
            "Keep it under 15 seconds for maximum shareability.",
        ],
    },
}


def get_sound_strategy(content_type: str) -> dict:
    """
    Return recommended sound strategy for a given content type.
    content_type: one of viral_original, popular_licensed, niche_specific, original_audio
    """
    if content_type not in SOUND_STRATEGY:
        available = ", ".join(SOUND_STRATEGY.keys())
        raise ValueError(f"Unknown content_type '{content_type}'. Available: {available}")
    return {"content_type": content_type, **SOUND_STRATEGY[content_type]}


def list_sound_strategies() -> list[dict]:
    """List all available sound strategies."""
    return [
        {"content_type": k, **v}
        for k, v in SOUND_STRATEGY.items()
    ]


# ---------------------------------------------------------------------------
# Best times to post with music trends
# ---------------------------------------------------------------------------

PEAK_POSTING_WINDOWS = {
    "tiktok": {
        "US": [
            {"day": "Tuesday", "windows": ["6am-9am", "7pm-10pm"]},
            {"day": "Thursday", "windows": ["7am-9am", "7pm-10pm"]},
            {"day": "Friday", "windows": ["5am-8am", "6pm-10pm"]},
            {"day": "Saturday", "windows": ["11am-1pm", "7pm-9pm"]},
            {"day": "Sunday", "windows": ["7am-10am", "6pm-9pm"]},
        ],
        "UK": [
            {"day": "Tuesday", "windows": ["6am-8am", "7pm-10pm"]},
            {"day": "Friday", "windows": ["5pm-8pm"]},
            {"day": "Saturday", "windows": ["10am-1pm", "7pm-9pm"]},
        ],
    },
    "instagram": {
        "US": [
            {"day": "Monday", "windows": ["11am-1pm", "7pm-9pm"]},
            {"day": "Wednesday", "windows": ["11am-1pm", "5pm-7pm"]},
            {"day": "Friday", "windows": ["10am-12pm", "6pm-9pm"]},
            {"day": "Saturday", "windows": ["9am-11am"]},
        ],
    },
    "youtube": {
        "US": [
            {"day": "Thursday", "windows": ["12pm-4pm"]},
            {"day": "Friday", "windows": ["12pm-4pm"]},
            {"day": "Saturday", "windows": ["9am-11am"]},
            {"day": "Sunday", "windows": ["9am-11am"]},
        ],
    },
}


def get_peak_posting_times(platform: str, region: str = "US") -> list[dict]:
    """Return peak posting windows for a platform and region."""
    platform = platform.lower()
    if platform not in PEAK_POSTING_WINDOWS:
        raise ValueError(f"Platform '{platform}' not in data. Choose: {', '.join(PEAK_POSTING_WINDOWS)}")
    region_data = PEAK_POSTING_WINDOWS[platform]
    key = region.upper() if region.upper() in region_data else "US"
    return region_data[key]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    import datetime
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _infer_genre_from_tags(tags: list[str]) -> Optional[str]:
    tag_str = " ".join(tags).lower()
    genre_map = {
        "hiphop": ["rap", "hiphop", "trap", "drill"],
        "pop": ["pop", "kpop", "bop"],
        "rnb": ["rnb", "r&b", "soul", "neo soul"],
        "electronic": ["edm", "electronic", "house", "techno", "dubstep"],
        "rock": ["rock", "alternative", "indie", "metal"],
        "country": ["country", "country music"],
        "latin": ["latin", "reggaeton", "bachata", "salsa"],
        "lo-fi": ["lofi", "lo-fi", "chill", "study"],
    }
    for genre, keywords in genre_map.items():
        if any(kw in tag_str for kw in keywords):
            return genre
    return None


def _infer_niches_from_tags(tags: list[str]) -> list[str]:
    tag_str = " ".join(tags).lower()
    niche_map = {
        "fitness": ["gym", "workout", "fitness"],
        "fashion": ["fashion", "style", "ootd"],
        "gaming": ["gaming", "gamer", "esports"],
        "vlog": ["vlog", "lifestyle", "daily"],
        "dance": ["dance", "choreography", "dancer"],
    }
    found = []
    for niche, keywords in niche_map.items():
        if any(kw in tag_str for kw in keywords):
            found.append(niche)
    return found
