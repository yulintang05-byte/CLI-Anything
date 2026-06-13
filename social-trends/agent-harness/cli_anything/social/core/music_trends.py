"""Trending music & audio analyzer — cross-platform music signal extraction."""
from typing import List, Dict, Any, Optional

from cli_anything.social.utils.scraper import RateLimitedSession


# Curated trending genres and moods for content creators (updated regularly)
TRENDING_GENRES = [
    {"genre": "Phonk",         "platform": "TikTok",  "use_case": "gym, motivation, dark aesthetic"},
    {"genre": "Hyperpop",      "platform": "TikTok",  "use_case": "chaotic edits, gen-z aesthetic"},
    {"genre": "Afrobeats",     "platform": "Both",    "use_case": "dance, lifestyle, summer content"},
    {"genre": "Lo-fi Hip Hop", "platform": "YouTube", "use_case": "study, chill, background vibes"},
    {"genre": "Bedroom Pop",   "platform": "Both",    "use_case": "aesthetic, personal vlogs"},
    {"genre": "EDM / Future",  "platform": "Both",    "use_case": "transitions, hype, sports"},
    {"genre": "Sad Rap",       "platform": "TikTok",  "use_case": "emotional storytelling"},
    {"genre": "Reggaeton",     "platform": "Both",    "use_case": "dance, lifestyle"},
    {"genre": "Y2K Pop",       "platform": "Both",    "use_case": "nostalgia, fashion, throwback"},
    {"genre": "Drill",         "platform": "TikTok",  "use_case": "street, fashion, aggressive edits"},
]

# Royalty-free music sources safe for monetized content
ROYALTY_FREE_SOURCES = [
    {
        "name":        "YouTube Audio Library",
        "url":         "https://studio.youtube.com/channel/audio",
        "cost":        "Free",
        "use":         "YouTube, Reels, TikTok (with attribution check)",
        "best_for":    "Background music, vlogs, b-roll",
    },
    {
        "name":        "Epidemic Sound",
        "url":         "https://www.epidemicsound.com",
        "cost":        "$15/mo Creator plan",
        "use":         "All platforms, full monetization",
        "best_for":    "Consistent branding, cinematic tracks",
    },
    {
        "name":        "Artlist",
        "url":         "https://artlist.io",
        "cost":        "$9.99/mo",
        "use":         "All platforms, unlimited downloads",
        "best_for":    "Indie, cinematic, documentary",
    },
    {
        "name":        "TikTok Sound Library",
        "url":         "https://www.tiktok.com/music",
        "cost":        "Free (TikTok only)",
        "use":         "TikTok only — NOT for cross-posting",
        "best_for":    "Viral trends, FYP boost",
    },
    {
        "name":        "Pixabay Music",
        "url":         "https://pixabay.com/music",
        "cost":        "Free, no attribution",
        "use":         "All platforms",
        "best_for":    "Quick projects, no budget",
    },
    {
        "name":        "Musicbed",
        "url":         "https://www.musicbed.com",
        "cost":        "$16.99/mo",
        "use":         "All platforms, sync licensing",
        "best_for":    "Commercial / brand content",
    },
]

# Music strategy by content type
MUSIC_STRATEGY = {
    "viral_content": {
        "rule":    "Use current TikTok trending sound — check For You Page for the #1 track.",
        "timing":  "Add trending sound within 24–72h of it going viral for maximum FYP push.",
        "tip":     "Even if music doesn't match your video, add it low volume under voiceover.",
    },
    "brand_content": {
        "rule":    "Use royalty-free licensed music. Never use trending sounds for paid promos.",
        "timing":  "Match music energy to the CTA — upbeat = purchase, slow = contemplation.",
        "tip":     "Epidemic Sound or Artlist subscription pays for itself with one brand deal.",
    },
    "theme_page": {
        "rule":    "Rotate between 2–3 sounds that fit your niche aesthetic.",
        "timing":  "If a sound starts trending, post content using it within 48h.",
        "tip":     "Curate a playlist of 10–15 sounds that define your page's vibe.",
    },
    "educational": {
        "rule":    "Keep music subtle — 20–30% volume under your voice.",
        "timing":  "Use neutral, non-distracting lo-fi or ambient tracks.",
        "tip":     "Consistency in background music builds audio branding for your page.",
    },
}


def get_music_trends(
    yt_music_data: Optional[List[Dict]] = None,
    tt_sounds_data: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """Compile music trend report from YouTube + TikTok data."""
    yt_music  = yt_music_data  or []
    tt_sounds = tt_sounds_data or []

    # Cross-platform signal: songs appearing in both platforms
    yt_titles  = {m.get("title", "").lower() for m in yt_music}
    tt_titles  = {s.get("title", "").lower() for s in tt_sounds}
    cross      = yt_titles & tt_titles

    combined = []
    for s in tt_sounds:
        is_cross = s.get("title", "").lower() in cross
        combined.append({**s, "platforms": ["youtube", "tiktok"] if is_cross else ["tiktok"], "cross_platform": is_cross})
    for m in yt_music:
        if m.get("title", "").lower() not in tt_titles:
            combined.append({**m, "platforms": ["youtube"], "cross_platform": False})

    # Sort: cross-platform first
    combined.sort(key=lambda x: x.get("cross_platform", False), reverse=True)

    return {
        "trending_tracks":      combined[:20],
        "trending_genres":      TRENDING_GENRES,
        "royalty_free_sources": ROYALTY_FREE_SOURCES,
        "strategy":             MUSIC_STRATEGY,
        "action_items":         _music_action_items(combined),
    }


def _music_action_items(tracks: List[Dict]) -> List[str]:
    actions = [
        "Open TikTok FYP right now — scroll 5 minutes and note which song repeats most. Post with it today.",
        "Check https://www.tiktok.com/music for trending sound charts in your region.",
        "Search your niche + 'sound 2025' on TikTok — curate 10 sounds into a saved playlist.",
        "Subscribe to Epidemic Sound if you post branded or monetized content (avoids copyright strikes).",
        "Set a weekly reminder to refresh your trending sounds list every Monday.",
    ]
    if tracks:
        top = tracks[0]
        actions.insert(0, f"PRIORITY: \"{top.get('title','?')}\" by {top.get('artist','?')} — cross-platform viral, use NOW.")
    return actions
