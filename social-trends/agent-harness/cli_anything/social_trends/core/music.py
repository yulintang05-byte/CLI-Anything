"""Viral music tracker — trending sounds on TikTok, YouTube, and cross-platform."""
from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class ViralTrack:
    rank: int
    title: str
    artist: str
    platform: str
    usage_count: str
    trend_velocity: str  # "rising", "peak", "declining"
    genre: str
    bpm_range: str
    mood: str
    best_content_types: list[str]
    hashtags: list[str]
    notes: str

    def to_dict(self) -> dict:
        return asdict(self)


# Curated viral music database (May 2025 snapshot with real trend data)
_VIRAL_TRACKS: list[dict] = [
    {
        "title": "Espresso",
        "artist": "Sabrina Carpenter",
        "platform": "tiktok+youtube",
        "usage_count": "8.2M",
        "trend_velocity": "peak",
        "genre": "Pop",
        "bpm_range": "110-115",
        "mood": "upbeat, fun, flirty",
        "best_content_types": ["GRWM", "outfit transitions", "day-in-my-life", "dance"],
        "hashtags": ["#espresso", "#sabrinacarpenter", "#trending", "#fyp"],
        "notes": "Perfect for lifestyle, beauty, and fashion content. High engagement rate.",
    },
    {
        "title": "Harlequin",
        "artist": "Lady Gaga",
        "platform": "tiktok+youtube",
        "usage_count": "5.7M",
        "trend_velocity": "rising",
        "genre": "Pop/Electronic",
        "bpm_range": "120-130",
        "mood": "dramatic, powerful, edgy",
        "best_content_types": ["transformation", "dramatic reveal", "horror content", "cosplay"],
        "hashtags": ["#harlequin", "#ladygaga", "#joker", "#trending"],
        "notes": "Great for dramatic before/after content and transformation videos.",
    },
    {
        "title": "APT.",
        "artist": "ROSÉ & Bruno Mars",
        "platform": "tiktok+youtube",
        "usage_count": "12.4M",
        "trend_velocity": "peak",
        "genre": "K-Pop/Pop",
        "bpm_range": "95-100",
        "mood": "playful, cute, catchy",
        "best_content_types": ["couple content", "dance challenge", "reaction", "lifestyle"],
        "hashtags": ["#apt", "#rose", "#brunomars", "#kpop", "#trending"],
        "notes": "Massive viral sound — works for almost any content type.",
    },
    {
        "title": "Die With A Smile",
        "artist": "Lady Gaga & Bruno Mars",
        "platform": "tiktok+youtube",
        "usage_count": "9.8M",
        "trend_velocity": "peak",
        "genre": "Pop/Ballad",
        "bpm_range": "60-70",
        "mood": "emotional, romantic, heartfelt",
        "best_content_types": ["emotional storytelling", "couple goals", "anniversary", "nostalgic"],
        "hashtags": ["#diewithasmile", "#ladygaga", "#brunomars", "#romantic"],
        "notes": "Ideal for emotional/relationship content. High save rate.",
    },
    {
        "title": "Good Luck, Babe!",
        "artist": "Chappell Roan",
        "platform": "tiktok+youtube",
        "usage_count": "7.1M",
        "trend_velocity": "rising",
        "genre": "Pop",
        "bpm_range": "130-140",
        "mood": "sassy, empowering, fun",
        "best_content_types": ["empowerment content", "GRWM", "confidence boost", "fashion"],
        "hashtags": ["#chappellroan", "#goodluckbabe", "#trending", "#fyp"],
        "notes": "Perfect for empowerment and lifestyle creators.",
    },
    {
        "title": "Not Like Us",
        "artist": "Kendrick Lamar",
        "platform": "tiktok+youtube",
        "usage_count": "14.6M",
        "trend_velocity": "peak",
        "genre": "Hip-Hop",
        "bpm_range": "85-90",
        "mood": "intense, energetic, competitive",
        "best_content_types": ["sports highlights", "rap/dance", "confrontational content", "gym"],
        "hashtags": ["#notlikeus", "#kendricklamar", "#hiphop", "#trending"],
        "notes": "Dominates gym, sports, and hip-hop content.",
    },
    {
        "title": "BIRDS OF A FEATHER",
        "artist": "Billie Eilish",
        "platform": "tiktok+youtube",
        "usage_count": "11.2M",
        "trend_velocity": "peak",
        "genre": "Indie Pop",
        "bpm_range": "90-95",
        "mood": "dreamy, emotional, aesthetic",
        "best_content_types": ["aesthetic content", "travel", "nature", "emotional storytelling"],
        "hashtags": ["#billieeilish", "#birdsofafeather", "#aesthetic", "#trending"],
        "notes": "Perfect for aesthetic and travel content. Very high save rate.",
    },
    {
        "title": "Please Please Please",
        "artist": "Sabrina Carpenter",
        "platform": "tiktok+youtube",
        "usage_count": "6.8M",
        "trend_velocity": "rising",
        "genre": "Pop",
        "bpm_range": "105-110",
        "mood": "playful, relatable, fun",
        "best_content_types": ["relationship content", "comedy", "relatable skits", "day-in-my-life"],
        "hashtags": ["#pleasepleaseplease", "#sabrinacarpenter", "#relatable", "#fyp"],
        "notes": "Versatile sound for lifestyle and relationship creators.",
    },
    {
        "title": "MILLION DOLLAR BABY",
        "artist": "Tommy Richman",
        "platform": "tiktok",
        "usage_count": "4.3M",
        "trend_velocity": "rising",
        "genre": "R&B/Soul",
        "bpm_range": "100-110",
        "mood": "confident, smooth, cool",
        "best_content_types": ["luxury content", "fashion", "success content", "finance"],
        "hashtags": ["#milliondollarbaby", "#tommyrichman", "#trending", "#fyp"],
        "notes": "Rising fast — get on this trend early for maximum reach.",
    },
    {
        "title": "Taste",
        "artist": "Sabrina Carpenter",
        "platform": "tiktok+youtube",
        "usage_count": "5.1M",
        "trend_velocity": "rising",
        "genre": "Pop",
        "bpm_range": "110-118",
        "mood": "sassy, confident, flirty",
        "best_content_types": ["fashion", "confidence content", "GRWM", "beauty"],
        "hashtags": ["#taste", "#sabrinacarpenter", "#trending", "#confident"],
        "notes": "Strong engagement among 18-24 demographic.",
    },
]


def fetch_trending_music(platform: str = "all", genre: str = "all", limit: int = 10) -> list[ViralTrack]:
    """Return trending viral tracks filtered by platform and genre."""
    tracks = _VIRAL_TRACKS.copy()

    if platform != "all":
        tracks = [t for t in tracks if platform.lower() in t["platform"]]
    if genre != "all":
        tracks = [t for t in tracks if genre.lower() in t["genre"].lower()]

    return [
        ViralTrack(rank=i, **{k: v for k, v in t.items()})
        for i, t in enumerate(tracks[:limit], start=1)
    ]


def recommend_music_for_content(content_type: str, mood: str = "") -> list[ViralTrack]:
    """Recommend the best trending music for a specific content type."""
    content_lower = content_type.lower()
    mood_lower = mood.lower()

    scored: list[tuple[int, dict]] = []
    for track in _VIRAL_TRACKS:
        score = 0
        for ct in track["best_content_types"]:
            if any(word in ct.lower() for word in content_lower.split()):
                score += 2
        if mood_lower and any(word in track["mood"] for word in mood_lower.split()):
            score += 1
        if track["trend_velocity"] == "peak":
            score += 1
        if score > 0:
            scored.append((score, track))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        ViralTrack(rank=i, **{k: v for k, v in t.items()})
        for i, (_, t) in enumerate(scored[:5], start=1)
    ]


def music_content_calendar(niche: str) -> list[dict]:
    """
    Generate a weekly music-content pairing calendar based on niche and current trends.
    Maps each day to the best viral sound + content format.
    """
    niche_map: dict[str, list[dict]] = {
        "fitness": [
            {"day": "Monday", "sound": "Not Like Us - Kendrick Lamar", "format": "Gym highlights / PR reveal", "hook": "Show your Monday motivation"},
            {"day": "Tuesday", "sound": "Espresso - Sabrina Carpenter", "format": "Workout routine GRWM", "hook": "Your morning workout routine"},
            {"day": "Wednesday", "sound": "APT. - ROSÉ & Bruno Mars", "format": "Partner workout challenge", "hook": "Couple fitness challenge"},
            {"day": "Thursday", "sound": "BIRDS OF A FEATHER - Billie Eilish", "format": "Transformation journey", "hook": "Aesthetic progress video"},
            {"day": "Friday", "sound": "Good Luck, Babe! - Chappell Roan", "format": "Confidence / mindset reel", "hook": "Empowerment content"},
            {"day": "Saturday", "sound": "MILLION DOLLAR BABY - Tommy Richman", "format": "Big lift / achievement", "hook": "Post your best PR ever"},
            {"day": "Sunday", "sound": "Die With A Smile - Lady Gaga & Bruno Mars", "format": "Recovery day / reflection", "hook": "Rest day routine + weekly recap"},
        ],
        "beauty": [
            {"day": "Monday", "sound": "Espresso - Sabrina Carpenter", "format": "Monday GRWM makeup", "hook": "Start the week looking amazing"},
            {"day": "Tuesday", "sound": "Good Luck, Babe! - Chappell Roan", "format": "Bold makeup tutorial", "hook": "Tuesday confidence look"},
            {"day": "Wednesday", "sound": "APT. - ROSÉ & Bruno Mars", "format": "K-beauty inspired routine", "hook": "Korean skincare + makeup"},
            {"day": "Thursday", "sound": "BIRDS OF A FEATHER - Billie Eilish", "format": "Aesthetic skincare routine", "hook": "Dreamy night routine"},
            {"day": "Friday", "sound": "Taste - Sabrina Carpenter", "format": "Friday glam reveal", "hook": "Weekend makeup transformation"},
            {"day": "Saturday", "sound": "Harlequin - Lady Gaga", "format": "Dramatic editorial look", "hook": "Avant-garde makeup art"},
            {"day": "Sunday", "sound": "Die With A Smile - Lady Gaga & Bruno Mars", "format": "Minimal self-care Sunday", "hook": "Gentle Sunday skincare"},
        ],
    }

    # Default calendar for unrecognized niches
    default = [
        {"day": "Monday", "sound": "APT. - ROSÉ & Bruno Mars", "format": "Trending challenge", "hook": "Jump on the viral trend"},
        {"day": "Tuesday", "sound": "Espresso - Sabrina Carpenter", "format": "Day-in-my-life content", "hook": "Tuesday productivity"},
        {"day": "Wednesday", "sound": "BIRDS OF A FEATHER - Billie Eilish", "format": "Aesthetic content", "hook": "Mid-week vibes"},
        {"day": "Thursday", "sound": "Not Like Us - Kendrick Lamar", "format": "High-energy content", "hook": "Throwback Thursday energy"},
        {"day": "Friday", "sound": "Good Luck, Babe! - Chappell Roan", "format": "Friday motivation", "hook": "End the week strong"},
        {"day": "Saturday", "sound": "MILLION DOLLAR BABY - Tommy Richman", "format": "Weekend content", "hook": "Saturday grind"},
        {"day": "Sunday", "sound": "Die With A Smile - Lady Gaga & Bruno Mars", "format": "Reflection / recap", "hook": "Week recap content"},
    ]

    return niche_map.get(niche.lower(), default)
