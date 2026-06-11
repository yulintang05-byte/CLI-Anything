"""YouTube data backend — fetches trends, hashtags, and channel data.

Primary methods:
  - YouTube Data API v3 (requires YT_API_KEY)
  - yt-dlp as no-key fallback for trending/video metadata
"""

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

CONFIG_DIR = Path.home() / ".config" / "cli-anything-youtube"
CONFIG_FILE = CONFIG_DIR / "config.json"
ENV_API_KEY = "YT_API_KEY"

# YouTube Data API v3
YT_API_BASE = "https://www.googleapis.com/youtube/v3"

# Valid category IDs for YouTube trending
CATEGORY_IDS = {
    "all":       "0",
    "music":     "10",
    "gaming":    "20",
    "sports":    "17",
    "news":      "25",
    "comedy":    "23",
    "education": "27",
    "science":   "28",
    "travel":    "19",
    "howto":     "26",
    "film":      "1",
}

# Supported region codes
REGIONS = [
    "US", "GB", "CA", "AU", "IN", "BR", "DE", "FR", "JP", "KR",
    "MX", "IT", "ES", "NL", "PL", "SE", "NO", "DK", "FI", "NZ",
]

# ── Niche keyword packs for YouTube SEO ──────────────────────────────────

NICHE_KEYWORDS: dict[str, list[str]] = {
    "fitness": [
        "workout routine", "home workout", "weight loss tips", "muscle building",
        "gym motivation", "beginner workout", "cardio workout", "hiit workout",
        "diet plan", "healthy eating", "meal prep", "protein recipes",
        "6 pack abs", "leg day", "chest workout", "back workout",
        "full body workout", "calisthenics", "yoga for beginners", "pilates",
    ],
    "cooking": [
        "easy recipes", "quick meals", "healthy recipes", "meal prep",
        "cooking for beginners", "budget cooking", "5 ingredient meals",
        "one pot meals", "air fryer recipes", "instant pot recipes",
        "pasta recipes", "chicken recipes", "vegan recipes", "keto recipes",
        "baking from scratch", "dessert recipes", "breakfast ideas",
        "lunch ideas", "dinner ideas", "cooking hacks",
    ],
    "finance": [
        "how to invest", "stock market basics", "passive income ideas",
        "budgeting tips", "save money fast", "make money online",
        "real estate investing", "cryptocurrency guide", "index funds",
        "financial freedom", "side hustle ideas", "multiple income streams",
        "credit score improvement", "debt payoff strategy",
        "retirement planning", "tax saving tips", "emergency fund",
        "compound interest", "dividend investing", "ETF investing",
    ],
    "tech": [
        "best apps", "tech review", "phone comparison", "laptop review",
        "programming tutorial", "python for beginners", "web development",
        "AI tools", "productivity apps", "software tutorial",
        "how to use", "tech tips", "setup tour", "desk setup",
        "gaming PC build", "smartphone tips", "iPhone vs Android",
        "smart home setup", "budget tech", "tech under 100",
    ],
    "gaming": [
        "game review", "best games 2024", "gameplay walkthrough",
        "gaming tips", "how to get better", "beginner guide",
        "gaming setup", "game highlights", "funny moments",
        "speedrun", "challenge run", "mod showcase", "gaming news",
        "upcoming games", "free games", "game comparison",
        "streaming setup", "gaming PC", "console gaming",
    ],
    "lifestyle": [
        "day in my life", "morning routine", "night routine", "productivity",
        "minimalism", "self improvement", "mental health", "journaling",
        "habits", "goal setting", "life hacks", "organization tips",
        "study with me", "work from home tips", "reading list",
        "book recommendations", "travel tips", "travel vlog",
        "apartment tour", "room makeover",
    ],
    "beauty": [
        "makeup tutorial", "skincare routine", "grwm", "drugstore makeup",
        "hair tutorial", "natural hair", "nail art", "beauty hacks",
        "affordable skincare", "holy grail products", "beauty review",
        "foundation routine", "contouring tutorial", "eye makeup",
        "lip combo", "no makeup makeup", "glam makeup", "everyday makeup",
        "skincare tips", "anti-aging routine",
    ],
    "education": [
        "learn", "tutorial", "explained", "for beginners", "crash course",
        "how to", "guide", "tips and tricks", "mistakes to avoid",
        "study tips", "exam preparation", "online learning",
        "skill building", "language learning", "coding tutorial",
        "math explained", "science explained", "history", "documentary",
    ],
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


def get_api_key(cli_key: str | None = None) -> str | None:
    if cli_key:
        return cli_key
    env = os.environ.get(ENV_API_KEY)
    if env:
        return env
    return load_config().get("api_key")


# ── yt-dlp helpers ────────────────────────────────────────────────────────

def _ytdlp_available() -> bool:
    try:
        r = subprocess.run(["yt-dlp", "--version"], capture_output=True, timeout=5)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _run_ytdlp(url: str, extra_args: list | None = None, limit: int = 25) -> list[dict]:
    if not _ytdlp_available():
        raise RuntimeError(
            "yt-dlp not found. Install with: pip3 install yt-dlp"
        )
    cmd = [
        "yt-dlp", "--dump-json", "--no-download",
        "--quiet", "--no-warnings",
        "--playlist-end", str(limit),
    ]
    if extra_args:
        cmd.extend(extra_args)
    cmd.append(url)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"yt-dlp timed out for {url}")

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


def _parse_yt_video(raw: dict) -> dict:
    title = raw.get("title") or ""
    desc = raw.get("description") or ""
    combined = f"{title} {desc[:500]}"
    hashtags = list(dict.fromkeys(re.findall(r"#(\w+)", combined)))

    return {
        "id": raw.get("id") or "",
        "url": raw.get("webpage_url") or f"https://youtu.be/{raw.get('id', '')}",
        "title": title,
        "channel": raw.get("uploader") or raw.get("channel") or "",
        "channel_url": raw.get("uploader_url") or "",
        "view_count": raw.get("view_count") or 0,
        "like_count": raw.get("like_count") or 0,
        "comment_count": raw.get("comment_count") or 0,
        "duration": raw.get("duration") or 0,
        "upload_date": raw.get("upload_date") or "",
        "hashtags": hashtags[:20],
        "description_snippet": desc[:200],
        "categories": raw.get("categories") or [],
        "tags": (raw.get("tags") or [])[:15],
    }


# ── YouTube Data API v3 fetchers ──────────────────────────────────────────

def _yt_api_request(endpoint: str, params: dict, api_key: str) -> dict:
    params["key"] = api_key
    resp = requests.get(f"{YT_API_BASE}/{endpoint}", params=params, timeout=15)
    if resp.status_code == 403:
        raise RuntimeError(
            "YouTube API quota exceeded or key invalid. "
            "Get a free key at https://console.cloud.google.com → YouTube Data API v3"
        )
    if resp.status_code != 200:
        raise RuntimeError(f"YouTube API error (HTTP {resp.status_code}): {resp.text[:300]}")
    return resp.json()


def get_trending_videos_api(
    region: str = "US",
    category: str = "all",
    limit: int = 25,
    api_key: str | None = None,
) -> list[dict]:
    """Fetch trending YouTube videos via YouTube Data API v3."""
    if not api_key:
        raise RuntimeError(
            "YouTube API key required. Provide via:\n"
            "  1. --api-key YOUR_KEY\n"
            f"  2. export {ENV_API_KEY}=YOUR_KEY\n"
            "  3. cli-anything-youtube config set api_key YOUR_KEY\n"
            "  Get a free key: https://console.cloud.google.com → YouTube Data API v3"
        )

    cat_id = CATEGORY_IDS.get(category.lower(), "0")
    params = {
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular",
        "regionCode": region.upper(),
        "maxResults": min(limit, 50),
    }
    if cat_id != "0":
        params["videoCategoryId"] = cat_id

    data = _yt_api_request("videos", params, api_key)
    items = data.get("items", [])

    videos = []
    for item in items:
        snip = item.get("snippet", {})
        stats = item.get("statistics", {})
        title = snip.get("title", "")
        desc = snip.get("description", "")
        combined = f"{title} {desc[:300]}"
        hashtags = list(dict.fromkeys(re.findall(r"#(\w+)", combined)))

        videos.append({
            "id": item.get("id", ""),
            "url": f"https://youtu.be/{item.get('id', '')}",
            "title": title,
            "channel": snip.get("channelTitle", ""),
            "channel_id": snip.get("channelId", ""),
            "view_count": int(stats.get("viewCount") or 0),
            "like_count": int(stats.get("likeCount") or 0),
            "comment_count": int(stats.get("commentCount") or 0),
            "upload_date": snip.get("publishedAt", "")[:10],
            "category": category,
            "hashtags": hashtags[:15],
            "tags": (snip.get("tags") or [])[:10],
            "description_snippet": desc[:200],
            "duration": item.get("contentDetails", {}).get("duration", ""),
        })
    return videos


def get_trending_videos_ytdlp(region: str = "US", limit: int = 25) -> list[dict]:
    """Fetch trending YouTube videos via yt-dlp (no API key needed)."""
    url = f"https://www.youtube.com/feed/trending?gl={region.upper()}"
    raw = _run_ytdlp(url, limit=limit)
    return [_parse_yt_video(v) for v in raw]


def get_video_metadata(video_url: str, api_key: str | None = None) -> dict:
    """Extract metadata and hashtags from a YouTube video URL."""
    # Try yt-dlp first (works without key)
    if _ytdlp_available():
        raw = _run_ytdlp(video_url, limit=1)
        if raw:
            return _parse_yt_video(raw[0])

    raise RuntimeError(f"Could not fetch metadata for {video_url}")


def extract_channel_hashtags(channel_url: str, limit: int = 20) -> dict:
    """Extract common hashtags from a channel's recent videos."""
    raw = _run_ytdlp(channel_url, limit=limit)
    videos = [_parse_yt_video(v) for v in raw]

    hashtag_counts: dict[str, int] = {}
    for v in videos:
        for tag in v.get("hashtags", []):
            t = tag.lower()
            hashtag_counts[t] = hashtag_counts.get(t, 0) + 1
    top = sorted(
        [{"hashtag": k, "appearances": c} for k, c in hashtag_counts.items()],
        key=lambda x: x["appearances"],
        reverse=True,
    )[:30]

    return {
        "channel_url": channel_url,
        "videos_analyzed": len(videos),
        "top_hashtags": top,
    }


def search_videos(query: str, limit: int = 25, api_key: str | None = None) -> list[dict]:
    """Search YouTube for videos matching a query."""
    if api_key:
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "order": "relevance",
            "maxResults": min(limit, 50),
        }
        data = _yt_api_request("search", params, api_key)
        items = data.get("items", [])
        return [
            {
                "id": i.get("id", {}).get("videoId", ""),
                "url": f"https://youtu.be/{i.get('id', {}).get('videoId', '')}",
                "title": i.get("snippet", {}).get("title", ""),
                "channel": i.get("snippet", {}).get("channelTitle", ""),
                "publish_date": i.get("snippet", {}).get("publishedAt", "")[:10],
            }
            for i in items
        ]

    url = f"https://www.youtube.com/results?search_query={requests.utils.quote(query)}"
    raw = _run_ytdlp(url, limit=limit)
    return [_parse_yt_video(v) for v in raw]


def get_niche_keywords(niche: str, limit: int = 20) -> list[str]:
    key = niche.lower().strip()
    for name, kws in NICHE_KEYWORDS.items():
        if key in name or name in key:
            return kws[:limit]
    return NICHE_KEYWORDS.get("education", [])[:limit]


def channel_audit_tips(channel_url: str = "", niche: str = "") -> dict:
    """Return YouTube channel optimization recommendations."""
    tips = {
        "channel_setup": [
            "Choose a channel name that includes your main keyword (e.g. 'FitnessWithJohn')",
            "Write a channel description with 3-5 target keywords in the first 2 sentences",
            "Upload a professional banner (2560x1440px) and profile picture (800x800px)",
            "Add channel keywords in YouTube Studio → Customization → Basic Info",
            "Create a channel trailer under 60 seconds targeted at new visitors",
            "Organize your videos into playlists — playlists rank in YouTube search",
        ],
        "video_optimization": [
            "Title formula: [Number/Power Word] + [Keyword] + [Benefit] (max 60 chars)",
            "Put your target keyword in the first 25 words of the description",
            "Write a 250+ word description with related keywords naturally included",
            "Add 15 tags: start with exact title keyword, then variations, then broad",
            "Use a custom thumbnail with text overlay — higher CTR = more distribution",
            "Add chapters/timestamps — boosts watch time and captures featured snippets",
            "Add end screens at the 20s mark to keep viewers on your channel",
            "Pin a comment with your key links/timestamps immediately after upload",
        ],
        "algorithm": [
            "CTR (click-through rate) is the #1 factor — test thumbnail+title combos",
            "Watch time matters more than views — make compelling first 30 seconds",
            "Consistency beats frequency — pick a schedule and keep it for 90 days",
            "Upload within your audience's peak hours (check YouTube Analytics)",
            "Reply to every comment in the first 48h — boosts video ranking",
            "Use Cards and End Screens to build session watch time",
            "Premieres create an event and boost initial velocity of new videos",
        ],
        "growth": [
            "Create 'pillar' content (long deep dives) and 'cluster' content (shorts/clips)",
            "Repurpose long videos into YouTube Shorts for additional distribution",
            "Build a playlist strategy — playlists rank separately in search",
            "Collaborate with channels in the same niche tier (similar subscriber count)",
            "Cross-promote: post Shorts on TikTok and Instagram Reels for backlinks",
            "Community posts keep subscribers engaged between video uploads",
        ],
        "monetization": [
            "Hit 1,000 subs + 4,000 watch hours → YouTube Partner Program",
            "Diversify: ads + sponsorships + memberships + merchandise + courses",
            "Use 'Made for Kids' toggle correctly — it limits monetization",
            "Super Thanks and Super Chats monetize Premieres and Livestreams",
        ],
    }

    if niche and niche.lower() in NICHE_KEYWORDS:
        kws = NICHE_KEYWORDS[niche.lower()][:5]
        tips["seo_keywords"] = [
            f"Top search keywords for {niche}: " + ", ".join(f'"{k}"' for k in kws),
            "Use Google Trends to compare keyword volume before choosing titles",
            "Target 'low competition, medium volume' keywords to rank faster",
        ]

    return {
        "channel_url": channel_url or "your channel",
        "niche": niche or "general",
        "tips": tips,
        "quick_wins": [
            "Add missing chapters to your top 5 most-viewed videos",
            "Re-do thumbnails on videos with >5% impression CTR but low views",
            "Create a playlist for your top 10 related videos",
            "Add a pinned comment with value on your last 10 videos",
        ],
    }
