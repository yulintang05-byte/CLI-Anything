"""TikTok data backend — fetches trends, hashtags, and sounds via yt-dlp + public endpoints."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable

try:
    import requests
except ImportError:
    print("requests not found. Install with: pip3 install requests", file=sys.stderr)
    sys.exit(1)

CONFIG_DIR = Path.home() / ".config" / "cli-anything-tiktok"
CONFIG_FILE = CONFIG_DIR / "config.json"

TIKTOK_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
}

# ── Curated hashtag packs per niche ──────────────────────────────────────

NICHE_HASHTAGS: dict[str, list[str]] = {
    "fitness": [
        "fitness", "workout", "gym", "fitnessmotivation", "exercise",
        "bodybuilding", "weightloss", "fitlife", "health", "training",
        "motivation", "fitnessjourney", "cardio", "gains", "abs",
        "personaltrainer", "homeworkout", "fit", "healthy", "strength",
        "gymlife", "gymrat", "physique", "crossfit", "powerlifting",
        "running", "yoga", "pilates", "nutrition", "dietitian",
    ],
    "food": [
        "food", "foodie", "recipe", "cooking", "chef", "foodtok",
        "delicious", "yummy", "homecooking", "foodlover", "mealprep",
        "baking", "healthyfood", "vegan", "vegetarian", "dinner",
        "lunch", "breakfast", "dessert", "snacks", "foodphotography",
        "tasty", "easyrecipes", "quickmeals", "foodhacks", "mukbang",
        "asmrfood", "streetfood", "restaurant", "homechef",
    ],
    "fashion": [
        "fashion", "ootd", "style", "outfit", "fashionista", "trending",
        "aesthetic", "streetstyle", "fashiontok", "lookbook", "haul",
        "thrifted", "vintage", "luxury", "streetwear", "styleinspiration",
        "mensfashion", "womensfashion", "fashionblogger", "outfitinspo",
        "clothinghaul", "fashionadvice", "summerfashion", "winterfashion",
        "casualoutfit", "formalwear", "sneakers", "accessories", "jewelry",
    ],
    "beauty": [
        "beauty", "makeup", "skincare", "glam", "tutorial", "makeupartist",
        "beautytips", "grwm", "skincareroutine", "hairtutorial", "nails",
        "eyeshadow", "lipstick", "foundation", "highlighter", "contour",
        "makeuptransformation", "naturalbeauty", "glowup", "beautyhacks",
        "drugstorebeauty", "luxurybeauty", "skintok", "acne", "antiaging",
        "haircare", "hairstyle", "curls", "blowout", "manicure",
    ],
    "travel": [
        "travel", "wanderlust", "traveltok", "adventure", "explore",
        "vacation", "travelgram", "holiday", "roadtrip", "backpacking",
        "travelblogger", "worldtravel", "photography", "nature", "beach",
        "mountains", "city", "luxurytravel", "budgettravel", "solotravel",
        "traveltips", "destination", "europe", "asia", "america",
        "hidden gems", "airbnb", "hotel", "flight", "passport",
    ],
    "finance": [
        "finance", "investing", "money", "financetok", "stocks",
        "crypto", "personalfinance", "budgeting", "savemoney", "wealth",
        "financialfreedom", "investing101", "stockmarket", "realestate",
        "sidehustle", "passiveincome", "entrepreneur", "business",
        "moneytips", "creditcard", "debt", "savings", "retirement",
        "401k", "dividends", "etf", "options", "daytrading", "nft", "defi",
    ],
    "gaming": [
        "gaming", "gamer", "videogames", "gamertok", "esports",
        "fps", "rpg", "minecraft", "fortnite", "valorant", "gta",
        "twitch", "streamer", "pcgaming", "consolegaming", "playstation",
        "xbox", "nintendo", "indiegame", "gamingsetup", "gameplay",
        "gaming_community", "gg", "pro", "speedrun", "gaming_clips",
        "highlights", "gamepass", "steam", "gamedev",
    ],
    "music": [
        "music", "musician", "singer", "artist", "newmusic", "musictok",
        "song", "original", "cover", "producer", "beatmaker", "rap",
        "hiphop", "pop", "rnb", "alternative", "indie", "edm",
        "acoustic", "guitar", "piano", "vocals", "studio", "recording",
        "musicvideo", "playlist", "vibes", "fyp", "trending", "viral",
    ],
    "motivation": [
        "motivation", "mindset", "success", "hustle", "grind", "inspire",
        "positivity", "selfimprovement", "personaldevelopment", "goals",
        "discipline", "hardwork", "focus", "mentality", "winner",
        "neverquit", "believe", "habits", "routine", "morning",
        "growth", "levelup", "entrepreneur", "boss", "dailymotivation",
        "quotes", "affirmations", "manifestation", "law of attraction",
    ],
    "pets": [
        "pets", "dog", "cat", "cute", "animals", "pettok", "puppy",
        "kitten", "dogsofttiktok", "catsooftiktok", "animalvideos",
        "funnyanimals", "petlife", "dogtraining", "catlover",
        "adoptdontshop", "rescue", "fur", "paws", "animallover",
        "bunny", "hamster", "bird", "fish", "reptile",
        "exoticpets", "wildlife", "zooanimals", "doglovers",
    ],
    "comedy": [
        "comedy", "funny", "humor", "lol", "memes", "comedytok",
        "sketch", "skit", "prank", "viral", "trending", "relatable",
        "funnymemes", "standupcomedy", "satire", "parody", "trend",
        "funnyvideos", "laugh", "jokes", "comedyvideo", "roast",
        "funnyclips", "hilarious", "entertainme", "wtf", "cringe",
        "ironic", "dark humor",
    ],
}

# ── Best posting times per platform ──────────────────────────────────────

POSTING_SCHEDULE = {
    "tiktok": {
        "monday":    ["06:00-10:00", "19:00-21:00"],
        "tuesday":   ["09:00-11:00", "19:00-21:00"],
        "wednesday": ["07:00-09:00", "17:00-19:00"],
        "thursday":  ["09:00-12:00", "19:00-21:00"],
        "friday":    ["05:00-09:00", "14:00-16:00"],
        "saturday":  ["11:00-13:00", "20:00-22:00"],
        "sunday":    ["07:00-09:00", "16:00-18:00"],
    },
    "youtube_shorts": {
        "monday":    ["12:00-14:00", "17:00-20:00"],
        "tuesday":   ["12:00-15:00", "19:00-21:00"],
        "wednesday": ["12:00-14:00", "17:00-21:00"],
        "thursday":  ["12:00-15:00", "19:00-21:00"],
        "friday":    ["12:00-15:00", "17:00-20:00"],
        "saturday":  ["09:00-11:00", "20:00-22:00"],
        "sunday":    ["09:00-11:00", "17:00-20:00"],
    },
    "instagram_reels": {
        "monday":    ["11:00-13:00", "19:00-21:00"],
        "tuesday":   ["08:00-10:00", "19:00-21:00"],
        "wednesday": ["11:00-13:00", "19:00-21:00"],
        "thursday":  ["11:00-13:00", "20:00-22:00"],
        "friday":    ["10:00-12:00", "19:00-21:00"],
        "saturday":  ["09:00-11:00", "20:00-22:00"],
        "sunday":    ["10:00-12:00", "19:00-21:00"],
    },
}


# ── Config ────────────────────────────────────────────────────────────────

def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)
    CONFIG_FILE.chmod(0o600)


def get_session_cookie(cli_cookie: str | None = None) -> str | None:
    if cli_cookie:
        return cli_cookie
    env = os.environ.get("TIKTOK_SESSION_ID")
    if env:
        return env
    return load_config().get("session_id")


# ── yt-dlp helpers ────────────────────────────────────────────────────────

def _ytdlp_available() -> bool:
    try:
        r = subprocess.run(["yt-dlp", "--version"], capture_output=True, timeout=5)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _run_ytdlp(url: str, extra_args: list | None = None, limit: int = 20) -> list[dict]:
    """Run yt-dlp with --dump-json and return list of video metadata dicts."""
    if not _ytdlp_available():
        raise RuntimeError(
            "yt-dlp not found. Install with: pip3 install yt-dlp\n"
            "Or: brew install yt-dlp"
        )

    cmd = [
        "yt-dlp",
        "--dump-json",
        "--no-download",
        "--quiet",
        "--no-warnings",
        "--playlist-end", str(limit),
    ]
    if extra_args:
        cmd.extend(extra_args)
    cmd.append(url)

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60
        )
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"yt-dlp timed out fetching {url}")

    if result.returncode not in (0, 1):
        err = result.stderr[:400].strip()
        raise RuntimeError(f"yt-dlp error: {err}")

    videos = []
    for line in result.stdout.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            videos.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return videos


def _parse_tiktok_video(raw: dict) -> dict:
    """Normalize a yt-dlp TikTok video dict into our standard format."""
    desc = raw.get("description") or raw.get("title") or ""
    hashtags = re.findall(r"#(\w+)", desc)

    sound = {
        "title": raw.get("track") or "",
        "artist": raw.get("artist") or raw.get("creator") or "",
        "id": raw.get("track_id") or "",
    }

    return {
        "id": raw.get("id") or "",
        "url": raw.get("webpage_url") or raw.get("url") or "",
        "description": desc[:200],
        "creator": raw.get("uploader") or raw.get("creator") or "",
        "creator_url": raw.get("uploader_url") or "",
        "view_count": raw.get("view_count") or 0,
        "like_count": raw.get("like_count") or 0,
        "comment_count": raw.get("comment_count") or 0,
        "share_count": raw.get("repost_count") or 0,
        "duration": raw.get("duration") or 0,
        "upload_date": raw.get("upload_date") or "",
        "hashtags": hashtags,
        "sound": sound,
    }


# ── Core fetch functions ──────────────────────────────────────────────────

def get_trending_videos(region: str = "US", limit: int = 20,
                        session_id: str | None = None) -> list[dict]:
    """Fetch trending TikTok videos via yt-dlp."""
    url = "https://www.tiktok.com/trending"
    try:
        raw = _run_ytdlp(url, limit=limit)
        return [_parse_tiktok_video(v) for v in raw]
    except RuntimeError as e:
        raise RuntimeError(f"Failed to fetch TikTok trending: {e}") from e


def get_hashtag_videos(tag: str, limit: int = 20,
                       session_id: str | None = None) -> list[dict]:
    """Fetch top videos for a specific hashtag."""
    tag = tag.lstrip("#").strip()
    url = f"https://www.tiktok.com/tag/{tag}"
    try:
        raw = _run_ytdlp(url, limit=limit)
        return [_parse_tiktok_video(v) for v in raw]
    except RuntimeError as e:
        raise RuntimeError(f"Failed to fetch hashtag #{tag}: {e}") from e


def extract_trends_from_videos(videos: list[dict]) -> dict:
    """Analyze a list of videos to surface trending hashtags and sounds."""
    hashtag_counts: dict[str, int] = {}
    sound_counts: dict[str, dict] = {}

    for v in videos:
        for tag in v.get("hashtags", []):
            t = tag.lower()
            hashtag_counts[t] = hashtag_counts.get(t, 0) + 1

        snd = v.get("sound", {})
        title = snd.get("title", "").strip()
        if title and title.lower() not in ("", "original sound"):
            key = title.lower()
            if key not in sound_counts:
                sound_counts[key] = {"title": title, "artist": snd.get("artist", ""), "count": 0}
            sound_counts[key]["count"] += 1

    top_hashtags = sorted(
        [{"hashtag": k, "appearances": v} for k, v in hashtag_counts.items()],
        key=lambda x: x["appearances"],
        reverse=True,
    )[:30]

    top_sounds = sorted(
        list(sound_counts.values()),
        key=lambda x: x["count"],
        reverse=True,
    )[:20]

    return {"trending_hashtags": top_hashtags, "trending_sounds": top_sounds}


def get_niche_hashtags(niche: str, limit: int = 30) -> list[str]:
    """Return curated hashtag list for a niche."""
    key = niche.lower().strip()
    for name, tags in NICHE_HASHTAGS.items():
        if key in name or name in key:
            return tags[:limit]
    # Fuzzy fallback — return motivation pack if nothing matches
    return NICHE_HASHTAGS.get("motivation", [])[:limit]


def list_niches() -> list[str]:
    return sorted(NICHE_HASHTAGS.keys())


def get_posting_schedule(platform: str = "tiktok") -> dict:
    """Return best posting times for a platform."""
    key = platform.lower().replace(" ", "_").replace("-", "_")
    if key not in POSTING_SCHEDULE:
        key = "tiktok"
    return POSTING_SCHEDULE[key]


def account_audit_tips(handle: str = "", niche: str = "", platform: str = "tiktok") -> dict:
    """Return account optimization recommendations."""
    tips = {
        "profile": [
            "Use a clear, high-resolution profile picture (your face or brand logo)",
            "Write a bio that states your niche in the first line (algorithm reads it)",
            "Add a call-to-action in bio (e.g. 'New video every day' or link in bio)",
            "Keep your username consistent across all platforms",
            "Use your niche keyword in your display name if possible",
        ],
        "content": [
            "Hook the viewer in the first 0-2 seconds — no slow intros",
            "Keep videos 15-30 seconds for max completion rate (boosts distribution)",
            "Use trending sounds (even quietly in the background) to get on sound's explore page",
            "Add 3-5 hashtags: 1 mega (#fitness), 1 niche (#homeworkout), 1 micro (#morningworkout)",
            "Post your best content between 6-9am or 7-9pm in your audience's timezone",
            "Film vertically at 1080x1920 (9:16 ratio), minimum 60fps looks more professional",
            "Use captions/subtitles — 80%+ of users watch without sound in many scenarios",
            "Re-use audio from your own viral videos to create series",
        ],
        "growth": [
            "Reply to EVERY comment in the first hour after posting (signals engagement)",
            "Create content series (Part 1, Part 2) to drive followers to your page",
            "Duet and Stitch viral videos in your niche while adding your perspective",
            "Collaborate with 2-3 accounts in the same niche tier as you",
            "Cross-post to YouTube Shorts and Instagram Reels for 3x content reach",
            "Post 1-3 times per day consistently for 30 days to find your content-market fit",
        ],
        "algorithm": [
            "The first 500 views reveal your audience — don't delete videos early",
            "Watch time > like rate in the algorithm; make people rewatch",
            "Saves and shares are the strongest engagement signals",
            "Going live 2-3x per week boosts organic push of your regular videos",
            "If a video gets 10%+ share rate, boost it with TikTok Promote ($5-20)",
        ],
    }

    if niche:
        niche_specific = NICHE_HASHTAGS.get(niche.lower(), [])
        if niche_specific:
            tips["hashtags"] = [
                f"Top hashtags for #{niche}: " + " ".join([f"#{t}" for t in niche_specific[:10]]),
                "Rotate hashtag packs every 7 days to avoid shadowban",
                "Never use the same set of hashtags on every video",
                "Research competitor hashtags — use their same 3-5 niche tags",
            ]

    return {
        "handle": handle or "your account",
        "platform": platform,
        "niche": niche or "general",
        "tips": tips,
        "score_factors": {
            "posting_consistency": "High impact — aim for daily posting",
            "hook_quality": "Critical — first 2 seconds decide everything",
            "sound_selection": "High impact — trending sounds = free discoverability",
            "engagement_response": "Medium-high — fast replies multiply reach",
            "hashtag_strategy": "Medium — over-rated but still useful",
        },
    }
