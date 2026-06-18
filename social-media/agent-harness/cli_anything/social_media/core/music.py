"""Music trend tracker — trending sounds on TikTok and YouTube music charts."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

_CACHE_PATH = Path.home() / ".cli-anything-social" / "music_cache.json"

# Content creator guidance — what types of sound work for each content type
_SOUND_STRATEGY: dict[str, dict] = {
    "dance": {
        "best_bpm_range": (120, 150),
        "ideal_duration": (15, 30),
        "tips": [
            "Use sounds with a strong beat drop for transition content",
            "Mirror the tempo in your editing cuts",
            "Trending dance sounds have 2–4x organic reach boost on TikTok",
        ],
    },
    "motivation": {
        "best_bpm_range": (90, 130),
        "ideal_duration": (30, 60),
        "tips": [
            "Cinematic/orchestral sounds work best for success content",
            "Lo-fi beats complement productivity/study content",
            "Use sounds from trending motivational creators",
        ],
    },
    "comedy": {
        "best_bpm_range": (100, 160),
        "ideal_duration": (7, 20),
        "tips": [
            "Comedy sounds trend fastest — use within 24h of discovery",
            "Sound-reaction combos get 3x more shares",
            "Silence with sudden audio drops gets high completion rates",
        ],
    },
    "lifestyle": {
        "best_bpm_range": (80, 110),
        "ideal_duration": (15, 60),
        "tips": [
            "Chill/aesthetic sounds increase save rate",
            "Morning routine videos + lo-fi sounds perform best",
            "Use sounds from 100K–1M video count range for max discovery",
        ],
    },
    "food": {
        "best_bpm_range": (95, 130),
        "ideal_duration": (15, 45),
        "tips": [
            "ASMR cooking sounds outperform music in food content",
            "Upbeat pop sounds for recipe reveals",
            "Seasonal songs timed to holidays get algorithm boost",
        ],
    },
    "fitness": {
        "best_bpm_range": (130, 180),
        "ideal_duration": (30, 60),
        "tips": [
            "High-BPM EDM/hip-hop drives the highest workout engagement",
            "Match reps/sets to the beat for satisfying completion",
            "Hype sounds from rap artists get more shares in gym content",
        ],
    },
}

# Spotify chart categories → YouTube/TikTok crossover signals
_CHART_CATEGORIES = [
    "Global Top 50",
    "USA Top 50",
    "Viral 50 — Global",
    "Viral 50 — USA",
    "Dance/Electronic",
    "Hip-Hop",
    "Pop",
    "Latin",
    "R&B",
]


@dataclass
class TrackInfo:
    title: str
    artist: str
    platform: str        # "tiktok" | "youtube" | "spotify"
    video_count: int     # times used (TikTok) or views (YouTube)
    trend_velocity: str  # "rising" | "peak" | "declining"
    bpm: int | None
    duration_seconds: int
    tags: list[str]
    url: str
    captured_at: str


def classify_trend_velocity(video_count: int, prev_count: int | None) -> str:
    if prev_count is None:
        return "unknown"
    delta = video_count - prev_count
    if delta > video_count * 0.2:
        return "rising"
    if delta < -video_count * 0.1:
        return "declining"
    return "peak"


def format_music_report(
    yt_tracks: list[dict],
    tt_sounds: list[dict],
    content_type: str = "general",
) -> dict:
    """Build a unified music trend report with creator recommendations."""
    now = datetime.now(timezone.utc).isoformat()

    yt_formatted = []
    for v in yt_tracks:
        yt_formatted.append({
            "title": v.get("title", ""),
            "channel": v.get("channel", ""),
            "views": v.get("views", 0),
            "likes": v.get("likes", 0),
            "url": v.get("url", ""),
            "tags": v.get("tags", [])[:8],
            "platform": "youtube",
        })

    tt_formatted = []
    for s in tt_sounds:
        tt_formatted.append({
            "title": s.get("title", ""),
            "artist": s.get("author", ""),
            "video_count": s.get("video_count", 0),
            "duration": s.get("duration", 0),
            "is_original": s.get("is_original", False),
            "platform": "tiktok",
        })

    strategy = _SOUND_STRATEGY.get(content_type, {})

    return {
        "generated_at": now,
        "youtube_trending_music": yt_formatted[:15],
        "tiktok_trending_sounds": tt_formatted[:15],
        "sound_strategy": strategy,
        "creator_tips": _build_creator_tips(yt_formatted, tt_formatted, content_type),
        "chart_categories": _CHART_CATEGORIES,
    }


def _build_creator_tips(
    yt: list[dict],
    tt: list[dict],
    content_type: str,
) -> list[str]:
    tips = [
        "Use trending sounds within the first 48h for the algorithm boost.",
        "Sounds with 100K–500K uses on TikTok hit the sweet spot: viral but not oversaturated.",
        "Always credit the original artist in your caption for good faith.",
        "Stitch/duet trending sound videos to inherit their existing algorithm momentum.",
    ]

    strategy = _SOUND_STRATEGY.get(content_type, {})
    if strategy:
        tips.extend(strategy.get("tips", []))
        bpm = strategy.get("best_bpm_range")
        dur = strategy.get("ideal_duration")
        if bpm:
            tips.append(f"Target sounds in {bpm[0]}–{bpm[1]} BPM range for {content_type} content.")
        if dur:
            tips.append(f"Ideal clip duration for {content_type}: {dur[0]}–{dur[1]} seconds.")

    if tt:
        top_sound = tt[0]
        tips.append(
            f"Top TikTok sound right now: '{top_sound.get('title', 'N/A')}' "
            f"by {top_sound.get('artist', 'N/A')} "
            f"({top_sound.get('video_count', 0):,} videos)."
        )
    if yt:
        top_yt = yt[0]
        tips.append(
            f"Trending on YouTube: '{top_yt.get('title', 'N/A')}' "
            f"by {top_yt.get('channel', 'N/A')} "
            f"({top_yt.get('views', 0):,} views)."
        )

    return tips


def save_music_report(report: dict, path: Path | None = None) -> Path:
    out = path or (Path.home() / ".cli-anything-social" / "music_reports")
    out.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fpath = out / f"music_report_{ts}.json"
    fpath.write_text(json.dumps(report, indent=2))
    return fpath


def available_content_types() -> list[str]:
    return sorted(_SOUND_STRATEGY.keys()) + ["general"]
