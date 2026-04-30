"""Trending music/sound identification and recommendations."""

from datetime import datetime
from cli_anything.social_media.utils.tiktok_scraper import fetch_trending_sounds
from cli_anything.social_media.utils.youtube_scraper import fetch_youtube_trending, extract_music_cues


_EVERGREEN_SOUNDS: list[dict] = [
    {"title": "Original Sound — POV hook transition", "platform": "tiktok", "category": "viral_format", "use_case": "POV storytelling videos"},
    {"title": "Lofi hip hop beats", "platform": "youtube", "category": "background", "use_case": "Study/aesthetic/morning routine"},
    {"title": "Epic cinematic build-up", "platform": "both", "category": "transformation", "use_case": "Before/after reveals, transformations"},
    {"title": "Upbeat pop instrumental", "platform": "both", "category": "energy", "use_case": "Lifestyle, travel, fitness content"},
    {"title": "Calm acoustic guitar", "platform": "both", "category": "ambient", "use_case": "Minimalism, journaling, slow life"},
]

_SOUND_CATEGORIES = {
    "viral_format": "Hook-driven sounds for viral formats (POV, duet, stitch)",
    "transformation": "Build-up/reveal sounds for before-after content",
    "energy": "Upbeat tracks for high-energy content",
    "ambient": "Calm background music for aesthetic/lifestyle",
    "trending_pop": "Currently charting pop music",
    "background": "Neutral background music (commentary, tutorials)",
}


def fetch_trending_music(platform: str = "tiktok", region: str = "US", limit: int = 20) -> dict:
    """Fetch trending music/sounds for a platform."""
    if platform in ("tiktok", "all"):
        tt_sounds = fetch_trending_sounds(limit=limit, region=region)
        return {
            "platform": platform,
            "region": region,
            "fetched_at": tt_sounds.get("fetched_at", datetime.utcnow().isoformat() + "Z"),
            "trending_sounds": tt_sounds.get("trending_sounds", []),
            "method": tt_sounds.get("method", ""),
            "usage_tips": _sound_usage_tips(),
        }

    if platform == "youtube":
        yt = fetch_youtube_trending(country=region, limit=limit)
        music_cues = extract_music_cues(yt.get("videos", []))
        return {
            "platform": "youtube",
            "region": region,
            "fetched_at": yt.get("fetched_at", datetime.utcnow().isoformat() + "Z"),
            "trending_sounds": [{"title": c, "platform": "youtube"} for c in music_cues[:limit]],
            "method": yt.get("method", ""),
            "usage_tips": _sound_usage_tips(),
        }

    return {
        "platform": platform,
        "region": region,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "trending_sounds": [],
        "error": f"Unsupported platform: {platform}",
    }


def recommend_sounds(niche: str, content_type: str = "general") -> dict:
    """Recommend sounds based on niche and content type."""
    niche_sound_map = {
        "finance": {
            "viral": "Trending pop/hip-hop — gives relatability to finance content",
            "category": "trending_pop",
            "examples": ["money-related trending sounds", "motivational build-ups"],
            "avoid": "Sad/slow music — kills engagement on money content",
        },
        "fitness": {
            "viral": "Energetic hip-hop, EDM, or motivational tracks",
            "category": "energy",
            "examples": ["gym motivation beats", "workout energy sounds"],
            "avoid": "Calm/ambient — mismatches high-energy fitness vibe",
        },
        "lifestyle": {
            "viral": "Trending pop or chill lo-fi",
            "category": "ambient",
            "examples": ["aesthetic playlist sounds", "morning coffee vibes"],
            "avoid": "Aggressive rap — clashes with soft lifestyle aesthetic",
        },
        "fashion": {
            "viral": "Trendy pop, especially chart-toppers",
            "category": "trending_pop",
            "examples": ["Sabrina Carpenter", "Charli XCX", "viral TikTok sounds"],
            "avoid": "Outdated sounds — fashion content must feel current",
        },
        "food": {
            "viral": "Upbeat, fun instrumentals or trending pop",
            "category": "energy",
            "examples": ["cooking montage beats", "restaurant ambiance sounds"],
            "avoid": "Serious/dramatic — food content should feel joyful",
        },
        "beauty": {
            "viral": "Aesthetic pop or trending girly sounds",
            "category": "ambient",
            "examples": ["GRWM playlist sounds", "girly pop trending"],
            "avoid": "Heavy bass/rap — doesn't fit beauty aesthetic",
        },
        "motivation": {
            "viral": "Epic build-up or motivational hip-hop",
            "category": "transformation",
            "examples": ["cinematic rise sounds", "motivational speech background"],
            "avoid": "Sad or slow — completely opposite energy",
        },
        "travel": {
            "viral": "Indie pop, world music, or adventure sounds",
            "category": "energy",
            "examples": ["adventure cinematic", "wanderlust playlist"],
            "avoid": "Generic background — travel needs adventurous energy",
        },
    }

    sound_rec = niche_sound_map.get(niche.lower(), {
        "viral": "Use currently trending sounds from the FYP",
        "category": "trending_pop",
        "examples": ["check TikTok trending sounds page"],
        "avoid": "Nothing specific — experiment with different styles",
    })

    return {
        "niche": niche,
        "content_type": content_type,
        "recommendation": sound_rec,
        "evergreen_options": _EVERGREEN_SOUNDS,
        "strategy": _music_strategy(niche),
        "copyright_tips": _copyright_tips(),
    }


def list_sound_categories() -> list[dict]:
    return [{"category": k, "description": v} for k, v in _SOUND_CATEGORIES.items()]


def _sound_usage_tips() -> list[str]:
    return [
        "Use full trending sounds (not just the trendy clip) to get maximum algorithm boost.",
        "Add sound BEFORE filming — TikTok's algorithm tracks sound usage from creation, not just posting.",
        "Sounds with 500k–2M uses hit the sweet spot: viral enough to boost, not so saturated you're invisible.",
        "Check TikTok's 'Trending' > 'Sounds' tab for sounds under 100k uses before they explode.",
        "YouTube Shorts: use YouTube's built-in audio library to avoid copyright strikes.",
        "Instagram Reels: use songs from Instagram's music library for stories/reels to avoid muting.",
        "Repurpose content: match your video edit to the trending sound's beat drops for higher saves.",
    ]


def _music_strategy(niche: str) -> list[str]:
    return [
        f"Monitor TikTok's 'Sounds' section daily for new {niche} trends.",
        "Create a saved playlist of 10-15 sounds that fit your niche and rotate them.",
        "When a sound hits 1M+ uses on TikTok, it's proven — use it immediately.",
        "Be an early adopter: sounds under 50k uses can make you 'the original' if you create a trend.",
        "Match your sound energy to your content hook — mismatches kill watch time.",
    ]


def _copyright_tips() -> list[str]:
    return [
        "TikTok: all sounds in the app are licensed — use freely within platform.",
        "YouTube Shorts: YouTube Studio Audio Library offers copyright-free music.",
        "Instagram: Instagram-licensed music shows a music note icon — safe to use.",
        "Cross-platform posting: never post TikTok audio to YouTube — use royalty-free alternatives.",
        "Epidemic Sound, Artlist, or YouTube Audio Library for copyright-safe music.",
        "Original sounds you create yourself have zero copyright risk and can go viral.",
    ]
