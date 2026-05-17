"""Trending music and sound tracker across YouTube and TikTok.

Surfaces viral tracks, TikTok sounds, and audio trends so creators
can use trending audio to boost algorithmic distribution.
"""

import json
import re
from collections import Counter
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional


MUSIC_KEYWORDS = re.compile(
    r"(official\s+(audio|video|mv)|lyric\s+video|music\s+video|"
    r"\bft\.\b|\bfeat\.\b|\bprod\.\b|\bremix\b|\bcover\b|"
    r"\(official\)|\[official\]|audio\s+only)",
    re.IGNORECASE,
)
ARTIST_SONG_PATTERN = re.compile(
    r"^(?P<artist>.+?)\s*[-–—]\s*(?P<song>.+?)(?:\s*[\(\[].+)?$"
)


@dataclass
class TrendingTrack:
    id: str
    title: str
    artist: str
    platform: str
    use_count: int        # how many trending videos use this sound
    est_reach: int        # estimated total views of videos using it
    velocity: float       # use_count / days tracked (virality rate)
    tiktok_sound_url: Optional[str]
    youtube_url: Optional[str]
    is_original_sound: bool
    niche_affinity: list[str]
    recommendation: str


class MusicTracker:
    def __init__(self):
        self._yt_tracks: list[dict] = []
        self._tt_sounds: list[dict] = []
        self._days_tracked: int = 1

    # ── Feed data in ──────────────────────────────────────────────────

    def feed_youtube_tracks(self, tracks: list[dict]) -> None:
        """Ingest YouTube music video data from YouTubeScraper."""
        self._yt_tracks.extend(tracks)

    def feed_tiktok_sounds(self, sounds: list[dict]) -> None:
        """Ingest TikTok sound data from TikTokScraper.get_trending_sounds()."""
        self._tt_sounds.extend(sounds)

    def feed_tiktok_videos(self, videos: list[dict]) -> None:
        """Extract sounds from raw TikTok video list."""
        sound_counts: Counter = Counter()
        sound_details: dict[str, dict] = {}
        for v in videos:
            sound = v.get("sound") or {}
            sid = str(sound.get("id", ""))
            if sid:
                sound_counts[sid] += 1
                if sid not in sound_details:
                    sound_details[sid] = {
                        "id": sid,
                        "title": sound.get("title", ""),
                        "artist": sound.get("author_name", "Unknown"),
                        "duration": sound.get("duration", 0),
                        "is_original": sound.get("is_original", False),
                    }
                sound_details[sid]["video_count"] = sound_counts[sid]
                # Accumulate reach
                current_reach = sound_details[sid].get("est_reach", 0)
                sound_details[sid]["est_reach"] = (
                    current_reach + v.get("play_count", 0)
                )
        merged = [
            {**sound_details[sid], "video_count": cnt}
            for sid, cnt in sound_counts.most_common()
            if sid in sound_details
        ]
        self._tt_sounds.extend(merged)

    def set_days_tracked(self, days: int) -> None:
        self._days_tracked = max(1, days)

    # ── Analysis ──────────────────────────────────────────────────────

    def get_top_tiktok_sounds(self, limit: int = 20) -> list[TrendingTrack]:
        """Return most-used TikTok sounds ranked by video count × reach."""
        merged = _merge_tt_sounds(self._tt_sounds)
        results = []
        for s in sorted(merged, key=lambda x: x.get("video_count", 0) * (x.get("est_reach", 1) ** 0.3), reverse=True)[:limit]:
            results.append(TrendingTrack(
                id=str(s.get("id", "")),
                title=s.get("title", "Unknown"),
                artist=s.get("artist", "Unknown"),
                platform="tiktok",
                use_count=s.get("video_count", 0),
                est_reach=s.get("est_reach", 0),
                velocity=round(s.get("video_count", 0) / self._days_tracked, 1),
                tiktok_sound_url=_tt_sound_url(s.get("id", "")),
                youtube_url=None,
                is_original_sound=s.get("is_original", False),
                niche_affinity=_detect_niche(s.get("title", "")),
                recommendation=_sound_recommendation(s.get("video_count", 0), self._days_tracked),
            ))
        return results

    def get_top_youtube_tracks(self, limit: int = 20) -> list[TrendingTrack]:
        """Return trending YouTube tracks ranked by view count."""
        results = []
        for t in sorted(self._yt_tracks, key=lambda x: x.get("view_count", 0), reverse=True)[:limit]:
            results.append(TrendingTrack(
                id=t.get("id", ""),
                title=t.get("title", "Unknown"),
                artist=t.get("artist", t.get("channel", "Unknown")),
                platform="youtube",
                use_count=1,
                est_reach=t.get("view_count", 0),
                velocity=round(t.get("view_count", 0) / self._days_tracked / 1000, 1),
                tiktok_sound_url=None,
                youtube_url=t.get("url"),
                is_original_sound=False,
                niche_affinity=_detect_niche(t.get("title", "")),
                recommendation=_yt_track_recommendation(t.get("view_count", 0)),
            ))
        return results

    def get_cross_platform_tracks(self, limit: int = 15) -> list[TrendingTrack]:
        """Tracks that appear trending on BOTH platforms (highest signal)."""
        yt_titles = {_normalize_title(t["title"]): t for t in self._yt_tracks}
        tt_titles = {_normalize_title(s.get("title", "")): s for s in self._tt_sounds}

        cross = []
        for norm_title, yt_track in yt_titles.items():
            if norm_title in tt_titles:
                tt = tt_titles[norm_title]
                cross.append(TrendingTrack(
                    id=yt_track.get("id", ""),
                    title=yt_track.get("title", "Unknown"),
                    artist=yt_track.get("artist", yt_track.get("channel", "Unknown")),
                    platform="both",
                    use_count=tt.get("video_count", 0),
                    est_reach=yt_track.get("view_count", 0) + tt.get("est_reach", 0),
                    velocity=round(tt.get("video_count", 0) / self._days_tracked, 1),
                    tiktok_sound_url=_tt_sound_url(tt.get("id", "")),
                    youtube_url=yt_track.get("url"),
                    is_original_sound=False,
                    niche_affinity=_detect_niche(yt_track.get("title", "")),
                    recommendation="HIGHEST PRIORITY — trending on both platforms. Use immediately.",
                ))
        return sorted(cross, key=lambda x: x.est_reach, reverse=True)[:limit]

    def export_report(self) -> dict:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "days_tracked": self._days_tracked,
            "top_tiktok_sounds": [asdict(t) for t in self.get_top_tiktok_sounds()],
            "top_youtube_tracks": [asdict(t) for t in self.get_top_youtube_tracks()],
            "cross_platform_hits": [asdict(t) for t in self.get_cross_platform_tracks()],
        }

    def to_json(self) -> str:
        return json.dumps(self.export_report(), indent=2, default=str)


# ── Pure helpers ──────────────────────────────────────────────────────────

def _merge_tt_sounds(sounds: list[dict]) -> list[dict]:
    merged: dict[str, dict] = {}
    for s in sounds:
        sid = str(s.get("id", ""))
        if not sid:
            continue
        if sid in merged:
            merged[sid]["video_count"] = merged[sid].get("video_count", 0) + s.get("video_count", 0)
            merged[sid]["est_reach"] = merged[sid].get("est_reach", 0) + s.get("est_reach", 0)
        else:
            merged[sid] = dict(s)
    return list(merged.values())


def _normalize_title(title: str) -> str:
    t = re.sub(r"[\(\[\{].*?[\)\]\}]", "", title).lower()
    t = re.sub(r"\b(official|audio|video|lyric|ft|feat|prod|remix|cover)\b", "", t)
    return re.sub(r"\s+", " ", t).strip()


def _tt_sound_url(sound_id: str) -> Optional[str]:
    if sound_id:
        return f"https://www.tiktok.com/music/-{sound_id}"
    return None


_NICHE_AUDIO_PATTERNS = {
    "fitness": re.compile(r"(gym|workout|pump|beast|hustle|motivation|run)", re.I),
    "gaming": re.compile(r"(game|epic|boss|battle|win|play|pixel)", re.I),
    "travel": re.compile(r"(journey|adventure|wander|explore|road|sunset)", re.I),
    "beauty": re.compile(r"(glam|glow|beauty|slay|chic|cute)", re.I),
    "comedy": re.compile(r"(funny|laugh|joke|meme|silly|clown)", re.I),
    "motivation": re.compile(r"(rise|grind|success|never\s+give|champion|believe)", re.I),
}


def _detect_niche(title: str) -> list[str]:
    return [niche for niche, pat in _NICHE_AUDIO_PATTERNS.items() if pat.search(title)]


def _sound_recommendation(video_count: int, days: int) -> str:
    velocity = video_count / max(days, 1)
    if velocity > 5000:
        return "VIRAL — use in next 24 hours before saturation"
    if velocity > 1000:
        return "TRENDING — strong signal, use this week"
    if velocity > 200:
        return "RISING — good timing to join early"
    return "STEADY — consistent performer, safe to use"


def _yt_track_recommendation(views: int) -> str:
    if views > 10_000_000:
        return "MEGA-VIRAL — peak mainstream attention"
    if views > 1_000_000:
        return "VIRAL — excellent for trend-riding content"
    if views > 100_000:
        return "POPULAR — solid choice for broad reach"
    return "NICHE — specific audience appeal"
