"""TikTok trend intelligence backend.

Supports two modes:
  1. yt-dlp mode (default) — fetches public TikTok content metadata without credentials.
     Install: pip install yt-dlp
  2. Research API mode — set TIKTOK_CLIENT_KEY + TIKTOK_CLIENT_SECRET env vars.
     Apply at: https://developers.tiktok.com/products/research-api/

Both modes return the same normalised schema so callers are backend-agnostic.
"""

import os
import json
import subprocess
import urllib.request
import urllib.parse
import urllib.error
from typing import Any

_TIKTOK_API_BASE = "https://open.tiktokapis.com/v2"

# Niche → seed hashtags used when live data is unavailable
_NICHE_SEED_HASHTAGS: dict[str, list[str]] = {
    "fitness": ["#fitness", "#gym", "#workout", "#fitspo", "#gains", "#bodybuilding",
                "#homeworkout", "#fitnessmotivation", "#cardio", "#weightloss"],
    "food": ["#food", "#foodtok", "#cooking", "#recipe", "#foodie", "#easyrecipe",
             "#mealprep", "#healthyfood", "#tasty", "#dinnerideas"],
    "fashion": ["#fashion", "#ootd", "#style", "#outfitinspo", "#aesthetic",
                "#fashiontok", "#thrifted", "#streetwear", "#outfitcheck", "#wiwt"],
    "beauty": ["#beauty", "#makeup", "#skincare", "#glowup", "#makeuptutorial",
               "#skincareroutine", "#grwm", "#selfcare", "#foundation", "#lipsync"],
    "finance": ["#finance", "#money", "#investing", "#sidehustle", "#budgeting",
                "#personalfinance", "#financetok", "#stockmarket", "#passiveincome", "#wealth"],
    "travel": ["#travel", "#traveltok", "#wanderlust", "#adventure", "#backpacking",
               "#travellife", "#explore", "#vacation", "#roadtrip", "#travelblog"],
    "gaming": ["#gaming", "#gamer", "#twitch", "#fortnite", "#minecraft", "#fps",
               "#gamingsetup", "#streamer", "#ps5", "#pcgaming"],
    "motivation": ["#motivation", "#mindset", "#success", "#grindset", "#discipline",
                   "#hustle", "#entrepreneurship", "#goals", "#dailymotivation", "#growth"],
    "comedy": ["#comedy", "#funny", "#memes", "#humor", "#foryou", "#lol",
               "#relatable", "#skit", "#trending", "#viral"],
    "education": ["#learnontiktok", "#edutok", "#tutorial", "#howto", "#facts",
                  "#didyouknow", "#lifehacks", "#tips", "#studytok", "#knowledge"],
    "pets": ["#pets", "#dogs", "#cats", "#dogsoftiktok", "#catsoftiktok",
             "#cutepets", "#petlife", "#funnypets", "#animals", "#puppy"],
    "diy": ["#diy", "#crafts", "#homedecor", "#upcycle", "#satisfying",
            "#transformation", "#makingwith", "#creative", "#handmade", "#trending"],
    "music": ["#music", "#singersoftiktok", "#newmusic", "#artist", "#producer",
              "#beat", "#rap", "#rnb", "#musician", "#originalsong"],
    "general": ["#fyp", "#foryou", "#viral", "#trending", "#foryoupage",
                "#explore", "#tiktok", "#satisfying", "#relatable", "#aesthetic"],
}

# Best-performing TikTok sound categories (updated May 2025)
_TRENDING_SOUND_CATEGORIES = [
    "Viral remix / sped-up tracks",
    "Lo-fi beats / study music",
    "Afrobeats / Amapiano",
    "Pop hooks (trending choruses)",
    "Emotional/cinematic piano",
    "Hyperpop / electronic",
    "Country pop crossover",
    "90s/2000s nostalgia remixes",
    "Original audio challenges",
    "Motivational speech overlays",
]


def _has_ytdlp() -> bool:
    return subprocess.run(["yt-dlp", "--version"], capture_output=True).returncode == 0


def _ytdlp_fetch(url: str, extra_args: list[str] | None = None) -> list[dict]:
    """Run yt-dlp and return parsed metadata entries."""
    cmd = ["yt-dlp", "--flat-playlist", "--dump-json", "--no-warnings", "--quiet"]
    if extra_args:
        cmd.extend(extra_args)
    cmd.append(url)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        entries = []
        for line in result.stdout.strip().splitlines():
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return entries
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def _get_research_token() -> str | None:
    """Obtain OAuth2 token from TikTok Research API credentials."""
    client_key = os.environ.get("TIKTOK_CLIENT_KEY", "")
    client_secret = os.environ.get("TIKTOK_CLIENT_SECRET", "")
    if not client_key or not client_secret:
        return None

    payload = urllib.parse.urlencode({
        "client_key": client_key,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }).encode()
    req = urllib.request.Request(
        "https://open.tiktokapis.com/v2/oauth/token/",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return data.get("access_token")
    except Exception:
        return None


def _research_api_query(endpoint: str, payload: dict, token: str) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{_TIKTOK_API_BASE}/{endpoint}",
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def fetch_trending_hashtags(niche: str = "general", region: str = "US") -> dict:
    """Return trending TikTok hashtags for a niche."""
    niche_key = niche.lower() if niche.lower() in _NICHE_SEED_HASHTAGS else "general"
    base_tags = _NICHE_SEED_HASHTAGS[niche_key]

    token = _get_research_token()
    if token:
        try:
            resp = _research_api_query("research/hashtag/query/", {
                "query": {"and": [{"operation": "IN", "field_name": "region_code", "field_values": [region]}]},
                "start_date": _days_ago(7),
                "end_date": _today(),
                "max_count": 20,
            }, token)
            hashtags = resp.get("data", {}).get("hashtags", [])
            if hashtags:
                return {
                    "source": "tiktok_research_api",
                    "niche": niche,
                    "region": region,
                    "hashtags": [{"name": h["name"], "view_count": h.get("view_count", 0)} for h in hashtags],
                }
        except Exception:
            pass

    # Seed-based fallback enriched with cross-niche trending tags
    cross_platform = ["#fyp", "#viral", "#trending", "#foryou", "#explore"]
    all_tags = list(dict.fromkeys(base_tags + cross_platform))
    return {
        "source": "curated_seed_data",
        "niche": niche,
        "region": region,
        "hashtags": [{"name": t, "tier": _hashtag_tier(t)} for t in all_tags],
        "setup_hint": "Set TIKTOK_CLIENT_KEY + TIKTOK_CLIENT_SECRET for live TikTok data",
    }


def fetch_trending_sounds(niche: str = "general") -> dict:
    """Return trending audio/music on TikTok."""
    # yt-dlp can extract audio metadata from individual TikTok videos
    # For broad sound trends we return curated categories + instructions
    niche_sounds = {
        "fitness": ["Eye of the Tiger - Rocky", "Survivor - Eye of the Tiger (sped up)",
                    "Motivational speech overlays", "Trap beats 140 BPM"],
        "food": ["Cooking ASMR", "Upbeat kitchen pop", "Italian/Mediterranean vibes"],
        "fashion": ["Trendy pop hooks", "Y2K throwbacks", "Indie aesthetic tracks"],
        "beauty": ["GRWM ambient pop", "Self-care lo-fi", "Tutorial background beats"],
        "finance": ["Success mindset speeches", "Corporate lo-fi", "Motivational overlays"],
        "general": _TRENDING_SOUND_CATEGORIES,
    }.get(niche.lower(), _TRENDING_SOUND_CATEGORIES)

    return {
        "source": "curated_trend_data",
        "niche": niche,
        "trending_sound_categories": niche_sounds,
        "how_to_find_live_sounds": [
            "Open TikTok → Discover tab → Sounds",
            "Check TikTok Creative Center: ads.tiktok.com/business/creativecenter/inspiration/popular/music",
            "Use yt-dlp on trending TikTok videos to extract audio metadata",
            "Monitor 'sounds used in trending videos' on your niche For You Page",
        ],
        "pro_tip": "Use sounds with 10k-500k videos for best discoverability. Mega-viral sounds (1M+) are saturated.",
    }


def fetch_tiktok_video_metadata(url: str) -> dict:
    """Fetch metadata for a specific TikTok video via yt-dlp."""
    if not _has_ytdlp():
        return {"error": "yt-dlp not installed. Run: pip install yt-dlp"}
    cmd = ["yt-dlp", "--dump-json", "--no-warnings", "--quiet", url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            data = json.loads(result.stdout.strip())
            return {
                "id": data.get("id", ""),
                "title": data.get("title", ""),
                "uploader": data.get("uploader", ""),
                "view_count": data.get("view_count", 0),
                "like_count": data.get("like_count", 0),
                "comment_count": data.get("comment_count", 0),
                "duration": data.get("duration", 0),
                "hashtags": [t.get("tag", "") for t in data.get("tags", [])],
                "music_title": data.get("track", ""),
                "music_artist": data.get("artist", ""),
                "upload_date": data.get("upload_date", ""),
                "url": url,
            }
        return {"error": result.stderr[:300]}
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        return {"error": str(e)}


def fetch_creator_videos(username: str, max_results: int = 10) -> list[dict]:
    """Fetch recent videos from a TikTok creator via yt-dlp."""
    if not _has_ytdlp():
        return [{"error": "yt-dlp not installed. Run: pip install yt-dlp"}]
    url = f"https://www.tiktok.com/@{username.lstrip('@')}"
    entries = _ytdlp_fetch(url, ["--playlist-end", str(max_results)])
    if not entries:
        return [{"note": f"No data fetched for @{username}. Ensure yt-dlp is installed and the account is public."}]
    return [{
        "id": e.get("id", ""),
        "title": e.get("title", ""),
        "url": e.get("url") or e.get("webpage_url", ""),
        "view_count": e.get("view_count", 0),
        "duration": e.get("duration", 0),
    } for e in entries]


def _hashtag_tier(tag: str) -> str:
    mega = {"#fyp", "#foryou", "#viral", "#trending", "#foryoupage", "#tiktok"}
    if tag in mega:
        return "mega (1B+ views — broad reach, high competition)"
    large = {"#explore", "#aesthetic", "#motivation", "#gym", "#food", "#fashion",
              "#beauty", "#travel", "#gaming", "#comedy"}
    if tag in large:
        return "large (100M–1B views — good reach)"
    return "niche (< 100M views — targeted, lower competition)"


def _days_ago(n: int) -> str:
    from datetime import date, timedelta
    return (date.today() - timedelta(days=n)).strftime("%Y%m%d")


def _today() -> str:
    from datetime import date
    return date.today().strftime("%Y%m%d")
