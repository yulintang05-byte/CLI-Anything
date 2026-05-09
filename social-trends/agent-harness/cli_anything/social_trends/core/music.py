"""Trending music and audio intelligence for TikTok and YouTube.

Covers:
  - Fetching trending sounds per niche
  - Analysing optimal audio for specific content types
  - Music licensing guidance (royalty-free vs licensed)
  - Audio strategy for growth
"""

from cli_anything.social_trends.utils import tiktok_backend as tt

# Royalty-free music sources trusted by creators
_ROYALTY_FREE_SOURCES = [
    {
        "name": "YouTube Audio Library",
        "url": "https://studio.youtube.com/channel/music",
        "cost": "Free",
        "best_for": "YouTube content, Shorts",
        "notes": "Safe for monetised YouTube channels; some tracks need attribution",
    },
    {
        "name": "TikTok Commercial Music Library",
        "url": "https://ads.tiktok.com/business/creativecenter/inspiration/popular/music",
        "cost": "Free",
        "best_for": "TikTok business accounts",
        "notes": "Required for business/brand accounts on TikTok",
    },
    {
        "name": "Epidemic Sound",
        "url": "https://www.epidemicsound.com",
        "cost": "$15/month personal",
        "best_for": "YouTube, Instagram, TikTok, podcasts",
        "notes": "Industry standard; unlimited use, full licensing",
    },
    {
        "name": "Artlist",
        "url": "https://artlist.io",
        "cost": "$9.99/month",
        "best_for": "All platforms including film/TV",
        "notes": "Annual license covers retroactive use",
    },
    {
        "name": "Musicbed",
        "url": "https://www.musicbed.com",
        "cost": "$14.99/month creator",
        "best_for": "High-quality cinematic content",
        "notes": "Premium catalog; great for vlogs and travel content",
    },
    {
        "name": "Pixabay Music",
        "url": "https://pixabay.com/music/",
        "cost": "Free",
        "best_for": "Any platform, no attribution needed",
        "notes": "CC0 license — completely free to use commercially",
    },
    {
        "name": "Free Music Archive",
        "url": "https://freemusicarchive.org",
        "cost": "Free",
        "best_for": "Podcast, YouTube",
        "notes": "Check individual licenses (CC0, CC BY, etc.)",
    },
]

# Audio strategy per content type
_CONTENT_AUDIO_STRATEGY: dict[str, dict] = {
    "tutorial": {
        "recommended": "Soft lo-fi, ambient background music",
        "bpm_range": "60–90 BPM",
        "volume": "Background (20–30% of voice volume)",
        "rationale": "Music should support comprehension, not distract",
        "avoid": "Lyrics, fast-tempo, trending viral sounds",
    },
    "vlog": {
        "recommended": "Upbeat indie-pop, acoustic guitar, lifestyle beats",
        "bpm_range": "90–120 BPM",
        "volume": "Mixed (ducked under voiceover, full during b-roll)",
        "rationale": "Energetic but not overwhelming; match mood to visuals",
        "avoid": "Monotone ambient; copyrighted chart music",
    },
    "motivation": {
        "recommended": "Cinematic orchestral, trap beats, epic builds",
        "bpm_range": "100–140 BPM",
        "volume": "Moderate to high (emotions-forward)",
        "rationale": "High-energy sound amplifies motivational messaging",
        "avoid": "Soft/relaxing music that undermines urgency",
    },
    "fitness": {
        "recommended": "High-energy EDM, hip-hop instrumentals, heavy trap",
        "bpm_range": "120–160 BPM",
        "volume": "High (matches workout intensity)",
        "rationale": "BPM should match or exceed training heart rate feel",
        "avoid": "Ballads, slow acoustic, ambient",
    },
    "food": {
        "recommended": "Warm acoustic, bossa nova, light jazz, upbeat pop",
        "bpm_range": "80–110 BPM",
        "volume": "Light background; ASMR cooking sounds should be audible",
        "rationale": "Food content benefits from cozy, inviting sound design",
        "avoid": "Heavy metal, intense EDM, lyrics that overshadow ASMR",
    },
    "comedy": {
        "recommended": "Trending viral sounds (use for maximum reach on TikTok)",
        "bpm_range": "Varies with viral sound",
        "volume": "Match original sound levels",
        "rationale": "Algorithm boosts trending sound usage; timing is critical",
        "avoid": "Original unknown music (misses viral sound discoverability)",
    },
    "travel": {
        "recommended": "Cinematic strings, world music, atmospheric pads",
        "bpm_range": "70–100 BPM",
        "volume": "Moderate; fade under natural ambient audio",
        "rationale": "Immersive audio transports the viewer",
        "avoid": "Generic copyright, jarring music changes",
    },
    "beauty": {
        "recommended": "Trending TikTok pop, soft R&B, ambient pop",
        "bpm_range": "85–115 BPM",
        "volume": "Mid-range; voice must be clear for tutorial steps",
        "rationale": "Aesthetic vibes drive beauty content engagement",
        "avoid": "Heavy bass, hard trap, mismatched genre",
    },
    "review": {
        "recommended": "Neutral lo-fi, subtle electronic background",
        "bpm_range": "70–90 BPM",
        "volume": "Very light background only",
        "rationale": "Reviewer credibility relies on clear voice; music is secondary",
        "avoid": "Any music with recognisable lyrics",
    },
}

# Current trending audio archetypes (May 2025)
_TRENDING_AUDIO_ARCHETYPES = [
    {
        "name": "Sped-up remix",
        "description": "Sped-up versions of popular songs (1.25–1.5x)",
        "best_niches": ["fashion", "beauty", "food", "comedy"],
        "engagement_boost": "High — triggers nostalgia + novelty",
        "how_to_use": "Layer under any content type; energy matches visual cuts",
    },
    {
        "name": "Drill/UK Drill beat",
        "description": "Dark melodic trap with sliding 808s",
        "best_niches": ["fitness", "motivation", "fashion", "gaming"],
        "engagement_boost": "Very high in male 18–24 demographic",
        "how_to_use": "Use for GRWM, gym reels, before/after transformations",
    },
    {
        "name": "Viral speech overlay",
        "description": "Motivational or emotional speech clip over music",
        "best_niches": ["motivation", "fitness", "education", "finance"],
        "engagement_boost": "High — hooks viewers emotionally within 3 seconds",
        "how_to_use": "Match visual B-roll to emotional arc of speech",
    },
    {
        "name": "Original lo-fi beat",
        "description": "Chill hip-hop beats, vinyl crackle, mellow vibe",
        "best_niches": ["education", "study", "productivity", "food"],
        "engagement_boost": "Medium — strong for watch time / study-with-me",
        "how_to_use": "Background for screen recordings, tutorials, cozy content",
    },
    {
        "name": "Trending pop hook",
        "description": "Chorus or hook from a chart-topping song",
        "best_niches": ["comedy", "beauty", "fashion", "general"],
        "engagement_boost": "Extremely high while trending (1–2 week window)",
        "how_to_use": "Act fast — post within 72h of the sound going viral",
    },
    {
        "name": "Afrobeats / Amapiano",
        "description": "West African / South African rhythmic dance music",
        "best_niches": ["fashion", "dance", "food", "travel", "beauty"],
        "engagement_boost": "High and growing globally",
        "how_to_use": "Match cuts to the beat; use for aesthetic montages",
    },
    {
        "name": "Hyperpop / 100 Gecs style",
        "description": "Distorted, chaotic, high-energy electronic",
        "best_niches": ["comedy", "gaming", "gen-z lifestyle"],
        "engagement_boost": "High in Gen-Z niche; polarising broadly",
        "how_to_use": "Match to chaotic visuals; great for meme content",
    },
    {
        "name": "Cinematic/orchestral build",
        "description": "Epic rising orchestral score with percussion",
        "best_niches": ["motivation", "travel", "fitness", "transformation"],
        "engagement_boost": "High for before/after and montage content",
        "how_to_use": "Time the drop to a visual reveal or transformation moment",
    },
]


def get_trending_sounds(niche: str = "general", platform: str = "tiktok") -> dict:
    """Return trending audio recommendations for a niche and platform."""
    if platform.lower() == "tiktok":
        live_data = tt.fetch_trending_sounds(niche=niche)
        niche_archetype = _niche_best_archetypes(niche)
        return {
            "platform": "tiktok",
            "niche": niche,
            "live_trends": live_data,
            "audio_archetypes": niche_archetype,
            "royalty_free_sources": _ROYALTY_FREE_SOURCES[:4],
            "pro_tips": [
                "Check TikTok Creative Center daily: ads.tiktok.com/business/creativecenter",
                "Sounds with 10K–500K uses have the best discoverability-to-competition ratio",
                "Save trending sounds immediately; use within 48–72h for peak impact",
                "Create your own sounds — original audio can go viral and build brand identity",
            ],
        }

    if platform.lower() == "youtube":
        return {
            "platform": "youtube",
            "niche": niche,
            "audio_strategy": _CONTENT_AUDIO_STRATEGY.get(niche.lower(), _CONTENT_AUDIO_STRATEGY.get("vlog", {})),
            "recommended_sources": _ROYALTY_FREE_SOURCES,
            "copyright_warning": (
                "YouTube Content ID will flag copyrighted music even if used briefly. "
                "Always use royalty-free music or YouTube Audio Library tracks for monetised channels."
            ),
            "shorts_tip": "YouTube Shorts with trending audio get an algorithm boost — use YouTube's built-in sound library in the Shorts editor",
        }

    return {
        "platform": platform,
        "niche": niche,
        "audio_archetypes": _trending_audio_archetypes_for_niche(niche),
        "royalty_free_sources": _ROYALTY_FREE_SOURCES,
    }


def get_audio_strategy(content_type: str) -> dict:
    """Return audio strategy for a specific content type."""
    content_key = content_type.lower()
    strategy = _CONTENT_AUDIO_STRATEGY.get(content_key)
    if not strategy:
        closest = _find_closest_content_type(content_key)
        return {
            "content_type": content_type,
            "note": f"No exact match found. Closest: '{closest}'",
            "strategy": _CONTENT_AUDIO_STRATEGY.get(closest, {}),
            "available_types": list(_CONTENT_AUDIO_STRATEGY.keys()),
        }
    return {"content_type": content_type, "strategy": strategy}


def list_royalty_free_sources() -> list[dict]:
    """Return all known royalty-free music sources."""
    return _ROYALTY_FREE_SOURCES


def analyse_trending_archetypes(niche: str = "general") -> list[dict]:
    """Return trending audio archetypes ranked for a niche."""
    return _niche_best_archetypes(niche)


def _niche_best_archetypes(niche: str) -> list[dict]:
    niche_lower = niche.lower()
    scored = []
    for arch in _TRENDING_AUDIO_ARCHETYPES:
        score = 2 if niche_lower in [n.lower() for n in arch["best_niches"]] else 0
        scored.append({**arch, "relevance_score": score})
    scored.sort(key=lambda x: x["relevance_score"], reverse=True)
    return scored


def _trending_audio_archetypes_for_niche(niche: str) -> list[dict]:
    return [a for a in _TRENDING_AUDIO_ARCHETYPES
            if niche.lower() in [n.lower() for n in a.get("best_niches", [])]]


def _find_closest_content_type(query: str) -> str:
    mapping = {
        "education": "tutorial", "gym": "fitness", "travel vlog": "vlog",
        "skincare": "beauty", "makeup": "beauty", "food review": "review",
        "podcast": "tutorial", "grwm": "beauty", "transformation": "motivation",
        "comedy skit": "comedy", "storytime": "vlog",
    }
    return mapping.get(query, "vlog")
