"""Trending music and audio research for social media content."""

from cli_anything.social_trends.utils.social_backend import (
    tiktok_trending_sounds_guide,
    yt_search_videos,
)


MUSIC_GENRE_SIGNALS = {
    "hype": {
        "description": "High-energy, beat-heavy tracks for action/transformation content",
        "best_for": ["fitness", "sports", "business wins", "before/after"],
        "search_terms": ["hype beat no copyright", "trap instrumental viral", "hard hitting beat 2024"],
        "platforms": ["YouTube Audio Library", "Pixabay Music", "Epidemic Sound"],
    },
    "chill_lo_fi": {
        "description": "Relaxed, atmospheric beats for aesthetic/lifestyle content",
        "best_for": ["aesthetic", "study", "lifestyle", "day-in-the-life"],
        "search_terms": ["lo fi hip hop aesthetic", "chill beats no copyright", "aesthetic music viral"],
        "platforms": ["YouTube Audio Library", "SoundCloud (free license)", "Lofi Records"],
    },
    "cinematic": {
        "description": "Epic orchestral/film-score style for dramatic reveals and motivation",
        "best_for": ["motivation", "transformation", "luxury", "inspiration"],
        "search_terms": ["cinematic motivation music", "epic background music no copyright", "dramatic build up"],
        "platforms": ["YouTube Audio Library", "Artlist.io", "Musicbed"],
    },
    "pop_trending": {
        "description": "Current popular songs (use only personal accounts to avoid copyright)",
        "best_for": ["dancing", "lip-sync", "reactions", "general entertainment"],
        "search_terms": ["top 50 trending tiktok songs 2024", "viral tiktok sounds this week"],
        "platforms": ["TikTok Sound Library", "Spotify (find song, use in TikTok app)"],
        "warning": "Commercial accounts must use TikTok/Instagram's licensed commercial sound libraries only.",
    },
    "podcast_style": {
        "description": "Subtle background ambiance for talking-head educational content",
        "best_for": ["finance tips", "how-to", "explainers", "commentary"],
        "search_terms": ["podcast background music free", "subtle talking head background", "corporate music"],
        "platforms": ["YouTube Audio Library", "Free Music Archive"],
    },
}


def get_music_guide() -> dict:
    """Comprehensive guide to finding and using trending music legally."""
    sound_sources = tiktok_trending_sounds_guide()
    return {
        "overview": (
            "Music and sound are the #1 algorithmic signal on TikTok/Reels. "
            "Using a trending sound in the first 24-72h of its virality gives 3-10x more reach. "
            "For YouTube Shorts, trending music boosts discovery in the Shorts shelf."
        ),
        "rights_guide": {
            "personal_accounts": "Can use most popular songs via TikTok/Instagram/YouTube's licensed libraries in-app.",
            "business_commercial_accounts": [
                "TikTok: Use Commercial Music Library only (toggle in app settings)",
                "Instagram/Facebook: Use Meta Sound Collection for licensed tracks",
                "YouTube Shorts: Use YouTube Audio Library for copyright-free music",
                "Universal safe choice: Epidemic Sound, Artlist.io, or Musicbed (paid, full licensing)",
            ],
            "free_legal_options": [
                "YouTube Audio Library (free, no attribution needed for most tracks)",
                "Pixabay Music (CC0 license — fully free commercial use)",
                "Free Music Archive (check license per track)",
                "SoundCloud (check 'Free Download' + license type)",
                "Incompetech by Kevin MacLeod (CC-BY attribution required)",
            ],
        },
        "genre_guide": MUSIC_GENRE_SIGNALS,
        "trending_sound_sources": sound_sources,
        "viral_sound_tactics": [
            {
                "tactic": "Morning Trend Hunt",
                "how": (
                    "Every morning, open TikTok → 'Sounds' → 'Trending'. "
                    "Filter to sounds used in 50K-500K videos (emerging sweet spot). "
                    "Create content within 4 hours and post immediately."
                ),
            },
            {
                "tactic": "Billboard Tracker Method",
                "how": (
                    "Chart-climbing songs on Spotify/Apple Music often go viral on TikTok 1-2 weeks later. "
                    "Monitor the Hot 100 and prepare content using new chart entries before they peak on TikTok."
                ),
            },
            {
                "tactic": "Stitch the Sound Creator",
                "how": (
                    "Find the original video of a trending sound. "
                    "Stitch it with your niche-relevant content. "
                    "You inherit the sound's momentum AND the original creator's audience."
                ),
            },
        ],
    }


def get_music_by_niche(niche: str) -> dict:
    """Get music recommendations tailored to a specific content niche."""
    niche_music_map = {
        "finance": ["cinematic", "hype", "podcast_style"],
        "fitness": ["hype", "pop_trending", "cinematic"],
        "motivation": ["cinematic", "hype", "pop_trending"],
        "luxury": ["cinematic", "chill_lo_fi", "pop_trending"],
        "aesthetic": ["chill_lo_fi", "pop_trending", "cinematic"],
        "tech": ["hype", "podcast_style", "chill_lo_fi"],
        "pets": ["chill_lo_fi", "pop_trending"],
        "general": ["pop_trending", "hype", "chill_lo_fi"],
    }

    niche_key = niche.lower() if niche.lower() in niche_music_map else "general"
    recommended_genres = niche_music_map[niche_key]

    result = {
        "niche": niche,
        "recommended_genres": [],
        "quick_picks": [],
    }

    for genre_key in recommended_genres:
        genre = MUSIC_GENRE_SIGNALS.get(genre_key, {})
        result["recommended_genres"].append({
            "genre": genre_key,
            "description": genre.get("description", ""),
            "best_for": genre.get("best_for", []),
            "where_to_find": genre.get("platforms", []),
        })
        result["quick_picks"].extend(genre.get("search_terms", [])[:1])

    result["youtube_search_tip"] = (
        f"Search YouTube for: '{result['quick_picks'][0]} no copyright' "
        f"to find free-to-use music for {niche} content."
    ) if result["quick_picks"] else ""

    return result


def find_viral_music_youtube(niche: str = "motivation", limit: int = 10) -> dict:
    """Search YouTube for trending music in a niche using YouTube Data API."""
    niche_key = niche.lower() if niche.lower() in MUSIC_GENRE_SIGNALS else "general"
    genre_info = MUSIC_GENRE_SIGNALS.get(niche_key, MUSIC_GENRE_SIGNALS["hype"])
    search_terms = genre_info.get("search_terms", ["viral background music no copyright"])
    query = search_terms[0]

    try:
        videos = yt_search_videos(
            query=f"{query} 2024",
            order="viewCount",
            max_results=limit,
        )
        return {
            "niche": niche,
            "search_query": query,
            "music_tracks": [
                {
                    "title": v["title"],
                    "channel": v["channel"],
                    "url": v["url"],
                    "published": v["published_at"][:10],
                }
                for v in videos
            ],
            "usage_note": (
                "Download via YouTube Audio Library or verify each track's license "
                "in the video description before using commercially."
            ),
        }
    except Exception as e:
        return {
            "niche": niche,
            "error": str(e),
            "fallback": (
                "YouTube API not configured. "
                "Search 'no copyright music [your niche]' on YouTube directly. "
                "Run: social-trends auth setup --youtube-api-key <KEY>"
            ),
        }
