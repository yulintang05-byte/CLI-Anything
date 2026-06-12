"""Trending music/sound tracker for YouTube and TikTok.

TikTok sounds drive virality — a rising sound means opportunity.
This module tracks, scores, and recommends sounds to use NOW (velocity > reach).
"""

import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict

# ── Data models ───────────────────────────────────────────────────────────────

@dataclass
class SoundTrend:
    sound_id: str
    title: str
    artist: str
    platform: str
    usage_count: int
    velocity_score: float   # rising fast = high score
    recommendation: str     # "use now", "rising", "peak", "declining"
    sample_url: str = ""
    original_audio: bool = False

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class MusicInsight:
    platform: str
    top_sounds: List[SoundTrend]
    rising_sounds: List[SoundTrend]
    insight_summary: str

    def to_dict(self) -> Dict:
        return {
            "platform": self.platform,
            "top_sounds": [s.to_dict() for s in self.top_sounds],
            "rising_sounds": [s.to_dict() for s in self.rising_sounds],
            "insight_summary": self.insight_summary,
        }


# ── TikTok viral sound patterns ───────────────────────────────────────────────

_VELOCITY_THRESHOLDS = {
    "use now":   0.8,   # high velocity + not yet peaked
    "rising":    0.5,
    "peak":      0.3,
    "declining": 0.0,
}


def _score_velocity(usage_count: int, position: int, total: int) -> float:
    """
    Estimate velocity from position in trending list + usage count.
    Top positions with high counts = already peaked.
    Mid-to-low positions with high counts = rising.
    """
    position_score = 1.0 - (position / max(total, 1))
    count_normalized = min(usage_count / 100.0, 1.0)
    combined = (position_score * 0.4) + (count_normalized * 0.6)
    return round(combined, 3)


def _recommend(velocity: float) -> str:
    for label, threshold in _VELOCITY_THRESHOLDS.items():
        if velocity >= threshold:
            return label
    return "declining"


def analyze_sounds(
    tiktok_sounds: List,  # List[TikTokSound]
    youtube_music: List,  # List[MusicTrack]
) -> MusicInsight:
    """Merge and analyze sounds from both platforms into actionable insights.

    Args:
        tiktok_sounds: Output of tiktok_trends.get_trending_sounds()
        youtube_music: Output of youtube_trends.get_trending_music()

    Returns:
        MusicInsight with scored + recommended sounds.
    """
    all_sounds: List[SoundTrend] = []
    total = len(tiktok_sounds)

    for i, sound in enumerate(tiktok_sounds):
        velocity = _score_velocity(sound.usage_count, i, total)
        all_sounds.append(SoundTrend(
            sound_id=sound.sound_id,
            title=sound.title or "Original Sound",
            artist=sound.author,
            platform="tiktok",
            usage_count=sound.usage_count,
            velocity_score=velocity,
            recommendation=_recommend(velocity),
            original_audio=(not sound.title or "original" in sound.title.lower()),
        ))

    total_yt = len(youtube_music)
    for i, track in enumerate(youtube_music):
        velocity = _score_velocity(track.usage_count, i, total_yt)
        all_sounds.append(SoundTrend(
            sound_id=track.sample_video_id,
            title=track.title,
            artist=track.artist,
            platform="youtube",
            usage_count=track.usage_count,
            velocity_score=velocity,
            recommendation=_recommend(velocity),
            sample_url=f"https://www.youtube.com/watch?v={track.sample_video_id}" if track.sample_video_id else "",
        ))

    all_sounds.sort(key=lambda s: (s.usage_count, s.velocity_score), reverse=True)
    rising = [s for s in all_sounds if s.recommendation in ("use now", "rising")]
    rising.sort(key=lambda s: s.velocity_score, reverse=True)

    top5 = all_sounds[:5]
    use_now_count = sum(1 for s in all_sounds if s.recommendation == "use now")
    summary = (
        f"Analyzed {len(all_sounds)} sounds across YouTube + TikTok. "
        f"{use_now_count} sounds flagged 'use now' (rising velocity, not yet saturated). "
        f"Top sound: '{top5[0].title}' by {top5[0].artist or 'Unknown'} "
        f"({top5[0].usage_count} uses, {top5[0].recommendation})."
        if top5 else "No sound data available."
    )

    return MusicInsight(
        platform="all",
        top_sounds=all_sounds[:10],
        rising_sounds=rising[:10],
        insight_summary=summary,
    )


def get_sound_strategy(niche: str) -> Dict:
    """Return a sound strategy guide for a given niche.

    Args:
        niche: Content niche (fitness, beauty, food, etc.)

    Returns:
        Dict with strategy tips for using trending sounds effectively.
    """
    strategies = {
        "fitness": {
            "sound_types": ["high-energy hip-hop", "EDM drops", "motivational speech clips"],
            "timing": "Use a sound within 48h of it appearing in your FYP",
            "tips": [
                "Cut video to match the beat drop for max retention",
                "Use rising sounds before they hit 500K videos for algorithm boost",
                "Motivational audio works best on Sunday morning + Monday posts",
            ],
        },
        "beauty": {
            "sound_types": ["pop hits", "chill R&B", "trending audio memes"],
            "timing": "GRWM videos perform best with conversational or podcast audio",
            "tips": [
                "Mirror popular creators' sound choices in your niche",
                "Tutorial videos can go sound-off — focus on captions",
                "Use TikTok's sound search to find sounds with < 10K videos (early mover)",
            ],
        },
        "food": {
            "sound_types": ["ASMR cooking sounds", "upbeat pop", "lo-fi"],
            "timing": "Post food content at 11am–1pm and 5pm–7pm in target timezone",
            "tips": [
                "ASMR sounds (sizzle, crunch) + no music = high completion rate",
                "Use trending audio to piggyback viral moments",
                "Silence can outperform music for recipe tutorials",
            ],
        },
        "motivation": {
            "sound_types": ["speech clips", "cinematic builds", "lo-fi hip-hop"],
            "timing": "Post Monday 6–9am for peak motivation engagement",
            "tips": [
                "Clip 5–15 second excerpts from speeches (check copyright)",
                "Build → Drop → Message structure syncs well with cinematic sounds",
                "Original voiceover over trending music = algorithm + authenticity",
            ],
        },
    }

    default = {
        "sound_types": ["trending pop", "viral audio memes", "original voiceover"],
        "timing": "Post when your target audience is most active (check analytics)",
        "tips": [
            "Use sounds with < 50K videos for first-mover advantage",
            "Trending sounds get pushed by the FYP algorithm — always check Discover",
            "Match your video pacing to the beat for higher completion rates",
        ],
    }

    return strategies.get(niche.lower(), default)
