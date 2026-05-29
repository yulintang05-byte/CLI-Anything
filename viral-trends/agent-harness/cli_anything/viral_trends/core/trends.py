"""Viral Trends CLI - YouTube and TikTok trend scrapers with mock fallbacks.

All public functions accept an optional `fetcher` parameter for testability.
Inject a mock callable in tests; leave None for production (uses real scraper).

The `live` flag controls whether real network fetching is attempted.
Without --live, mock data is always returned (safe for offline/demo use).
"""

import shutil
import subprocess
import json
import warnings
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

from cli_anything.viral_trends.core.session import Session


# ── Mock data ─────────────────────────────────────────────────────────────────

_MOCK_YT_TRENDS: List[Dict[str, Any]] = [
    {"rank": 1,  "title": "How AI is Changing Everything in 2025",    "channel": "TechExplained",    "views": 4_200_000, "likes": 180_000, "category": "Science & Tech",    "url": "https://youtube.com/watch?v=mock0001", "duration_seconds": 842},
    {"rank": 2,  "title": "I Turned $1000 Into $50K Trading Stocks",  "channel": "WealthBuilder",    "views": 3_800_000, "likes": 220_000, "category": "Finance",           "url": "https://youtube.com/watch?v=mock0002", "duration_seconds": 1204},
    {"rank": 3,  "title": "This NEW Game is INSANE (Full Playthrough)","channel": "GamingGod",       "views": 6_100_000, "likes": 340_000, "category": "Gaming",            "url": "https://youtube.com/watch?v=mock0003", "duration_seconds": 3600},
    {"rank": 4,  "title": "30-Minute Full Body Burn (No Equipment)",   "channel": "FitWithMike",     "views": 2_900_000, "likes": 195_000, "category": "Fitness",           "url": "https://youtube.com/watch?v=mock0004", "duration_seconds": 1800},
    {"rank": 5,  "title": "5 Recipes That Will Change Your Life",      "channel": "ChefDiana",       "views": 5_400_000, "likes": 410_000, "category": "Cooking",           "url": "https://youtube.com/watch?v=mock0005", "duration_seconds": 960},
    {"rank": 6,  "title": "The iPhone 17 is Actually Worth It",        "channel": "TechReviewPro",   "views": 7_200_000, "likes": 280_000, "category": "Science & Tech",    "url": "https://youtube.com/watch?v=mock0006", "duration_seconds": 720},
    {"rank": 7,  "title": "Skincare Routine That Cleared My Acne",     "channel": "GlowUp",          "views": 3_100_000, "likes": 260_000, "category": "Beauty",            "url": "https://youtube.com/watch?v=mock0007", "duration_seconds": 540},
    {"rank": 8,  "title": "The Mindset That Made Me a Millionaire",    "channel": "SuccessDaily",    "views": 2_600_000, "likes": 198_000, "category": "Motivation",        "url": "https://youtube.com/watch?v=mock0008", "duration_seconds": 1080},
    {"rank": 9,  "title": "Most VIRAL Moments This Week Compilation",  "channel": "ViralHub",        "views": 9_800_000, "likes": 520_000, "category": "Entertainment",     "url": "https://youtube.com/watch?v=mock0009", "duration_seconds": 1200},
    {"rank": 10, "title": "How to Build Passive Income With Zero Money","channel": "MoneyMoves",      "views": 4_400_000, "likes": 310_000, "category": "Finance",           "url": "https://youtube.com/watch?v=mock0010", "duration_seconds": 1560},
    {"rank": 11, "title": "Pro Gamer Reacts to Crazy Plays",           "channel": "ProReacts",       "views": 5_700_000, "likes": 380_000, "category": "Gaming",            "url": "https://youtube.com/watch?v=mock0011", "duration_seconds": 840},
    {"rank": 12, "title": "Science Behind Intermittent Fasting",       "channel": "HealthFirst",     "views": 2_100_000, "likes": 145_000, "category": "Fitness",           "url": "https://youtube.com/watch?v=mock0012", "duration_seconds": 1320},
    {"rank": 13, "title": "Gordon Ramsay's Easiest Pasta Recipe",      "channel": "CookingChannel",  "views": 8_900_000, "likes": 670_000, "category": "Cooking",           "url": "https://youtube.com/watch?v=mock0013", "duration_seconds": 480},
    {"rank": 14, "title": "Brutally Honest MacBook Pro M4 Review",     "channel": "AppleInsider",    "views": 3_300_000, "likes": 175_000, "category": "Science & Tech",    "url": "https://youtube.com/watch?v=mock0014", "duration_seconds": 1440},
    {"rank": 15, "title": "Nail Art Trends Taking Over TikTok",        "channel": "NailQueen",       "views": 1_800_000, "likes": 132_000, "category": "Beauty",            "url": "https://youtube.com/watch?v=mock0015", "duration_seconds": 360},
    {"rank": 16, "title": "Atomic Habits: How I Changed Everything",   "channel": "MindsetShift",    "views": 3_600_000, "likes": 290_000, "category": "Motivation",        "url": "https://youtube.com/watch?v=mock0016", "duration_seconds": 1680},
    {"rank": 17, "title": "He Was Publicly Humiliated — What Happened","channel": "TrueStories",     "views": 11_200_000,"likes": 740_000, "category": "Entertainment",     "url": "https://youtube.com/watch?v=mock0017", "duration_seconds": 900},
    {"rank": 18, "title": "Crypto in 2025: What Nobody Is Saying",     "channel": "CryptoTrue",      "views": 2_900_000, "likes": 210_000, "category": "Finance",           "url": "https://youtube.com/watch?v=mock0018", "duration_seconds": 1380},
    {"rank": 19, "title": "I Played Every Battle Royale in One Day",   "channel": "GamingMarathon",  "views": 4_800_000, "likes": 355_000, "category": "Gaming",            "url": "https://youtube.com/watch?v=mock0019", "duration_seconds": 7200},
    {"rank": 20, "title": "Zero Carb Diet: 30-Day Transformation",     "channel": "BodyHack",        "views": 2_400_000, "likes": 178_000, "category": "Fitness",           "url": "https://youtube.com/watch?v=mock0020", "duration_seconds": 1260},
]

_MOCK_TIKTOK_TRENDS: List[Dict[str, Any]] = [
    {"rank": 1,  "hashtag": "#AIChallenge",         "posts": 2_400_000,  "views": 890_000_000,  "growth_pct": 340, "niche": "tech"},
    {"rank": 2,  "hashtag": "#GymTok",              "posts": 8_100_000,  "views": 3_200_000_000,"growth_pct": 15,  "niche": "fitness"},
    {"rank": 3,  "hashtag": "#StockMarket",         "posts": 1_900_000,  "views": 720_000_000,  "growth_pct": 67,  "niche": "finance"},
    {"rank": 4,  "hashtag": "#FoodTok",             "posts": 14_000_000, "views": 5_600_000_000,"growth_pct": 8,   "niche": "cooking"},
    {"rank": 5,  "hashtag": "#GamingTikTok",        "posts": 6_300_000,  "views": 2_400_000_000,"growth_pct": 22,  "niche": "gaming"},
    {"rank": 6,  "hashtag": "#BeautyTok",           "posts": 9_800_000,  "views": 4_100_000_000,"growth_pct": 11,  "niche": "beauty"},
    {"rank": 7,  "hashtag": "#MotivationTok",       "posts": 3_200_000,  "views": 1_100_000_000,"growth_pct": 44,  "niche": "motivation"},
    {"rank": 8,  "hashtag": "#ViralVideo",          "posts": 21_000_000, "views": 9_800_000_000,"growth_pct": 5,   "niche": "entertainment"},
    {"rank": 9,  "hashtag": "#CryptoTok",           "posts": 1_400_000,  "views": 540_000_000,  "growth_pct": 89,  "niche": "finance"},
    {"rank": 10, "hashtag": "#SkincareTok",         "posts": 7_600_000,  "views": 3_000_000_000,"growth_pct": 19,  "niche": "beauty"},
    {"rank": 11, "hashtag": "#WorkoutMotivation",   "posts": 5_100_000,  "views": 2_100_000_000,"growth_pct": 31,  "niche": "fitness"},
    {"rank": 12, "hashtag": "#EasyRecipes",         "posts": 11_300_000, "views": 4_700_000_000,"growth_pct": 12,  "niche": "cooking"},
    {"rank": 13, "hashtag": "#TechTok",             "posts": 4_200_000,  "views": 1_600_000_000,"growth_pct": 55,  "niche": "tech"},
    {"rank": 14, "hashtag": "#MindsetMonday",       "posts": 2_100_000,  "views": 830_000_000,  "growth_pct": 38,  "niche": "motivation"},
    {"rank": 15, "hashtag": "#Fortnite",            "posts": 12_400_000, "views": 4_900_000_000,"growth_pct": 7,   "niche": "gaming"},
    {"rank": 16, "hashtag": "#MakeupTransformation","posts": 6_800_000,  "views": 2_700_000_000,"growth_pct": 24,  "niche": "beauty"},
    {"rank": 17, "hashtag": "#PassiveIncome",       "posts": 2_800_000,  "views": 1_000_000_000,"growth_pct": 73,  "niche": "finance"},
    {"rank": 18, "hashtag": "#FunnyMoments",        "posts": 18_000_000, "views": 7_200_000_000,"growth_pct": 6,   "niche": "entertainment"},
    {"rank": 19, "hashtag": "#AIArt",               "posts": 3_600_000,  "views": 1_400_000_000,"growth_pct": 210, "niche": "tech"},
    {"rank": 20, "hashtag": "#BodyTransformation",  "posts": 4_400_000,  "views": 1_700_000_000,"growth_pct": 28,  "niche": "fitness"},
]


# ── ID helpers ────────────────────────────────────────────────────────────────

def _next_id(items: List[Dict], prefix: str) -> str:
    """Generate a sequential ID like snap0, snap1, ..."""
    used = {item.get("snapshot_id", "") for item in items}
    i = 0
    while f"{prefix}{i}" in used:
        i += 1
    return f"{prefix}{i}"


# ── YouTube scraper ───────────────────────────────────────────────────────────

def _yt_dlp_fetcher(country: str, max_results: int, category: str) -> List[Dict[str, Any]]:
    """Real yt-dlp fetcher. Raises RuntimeError if yt-dlp not installed."""
    if not shutil.which("yt-dlp"):
        raise RuntimeError(
            "yt-dlp not found. Install with: pip install yt-dlp\n"
            "Or use without --live for mock trend data."
        )

    url = f"https://www.youtube.com/feed/trending?gl={country}"
    if category != "0":
        url += f"&bp={category}"

    result = subprocess.run(
        ["yt-dlp", "--flat-playlist", "--dump-json", "--playlist-end", str(max_results), url],
        capture_output=True, text=True, timeout=90
    )

    items = []
    for i, line in enumerate(result.stdout.strip().splitlines()):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
            items.append({
                "rank": i + 1,
                "title": entry.get("title", "Unknown"),
                "channel": entry.get("uploader", entry.get("channel", "Unknown")),
                "views": entry.get("view_count") or 0,
                "likes": entry.get("like_count") or 0,
                "category": entry.get("categories", [None])[0] if entry.get("categories") else "Unknown",
                "url": entry.get("webpage_url", f"https://youtube.com/watch?v={entry.get('id', '')}"),
                "duration_seconds": entry.get("duration") or 0,
            })
        except (json.JSONDecodeError, KeyError):
            continue

    return items


def fetch_youtube_trends(
    country: str = "US",
    max_results: int = 20,
    category: str = "0",
    live: bool = False,
    fetcher: Optional[Callable] = None,
) -> Dict[str, Any]:
    """Fetch YouTube trending videos.

    Args:
        country: ISO country code (US, GB, CA, AU, etc.)
        max_results: Maximum number of results to return.
        category: YouTube category ID ("0" = all).
        live: If True, attempt real yt-dlp fetch. Otherwise return mock data.
        fetcher: Injectable fetcher callable for testing.

    Returns:
        Dict with keys: success, source, country, count, items
    """
    if not live:
        items = _MOCK_YT_TRENDS[:max_results]
        return {
            "success": True,
            "source": "mock",
            "country": country,
            "count": len(items),
            "items": items,
        }

    actual_fetcher = fetcher or _yt_dlp_fetcher
    try:
        items = actual_fetcher(country, max_results, category)
        source = "yt-dlp"
        if not items:
            warnings.warn("yt-dlp returned no results, falling back to mock data")
            items = _MOCK_YT_TRENDS[:max_results]
            source = "mock-fallback"
    except Exception as e:
        warnings.warn(f"YouTube fetch failed ({e}), using mock data")
        items = _MOCK_YT_TRENDS[:max_results]
        source = "mock-fallback"

    return {
        "success": True,
        "source": source,
        "country": country,
        "count": len(items),
        "items": items,
    }


# ── TikTok scraper ────────────────────────────────────────────────────────────

def _requests_tiktok_fetcher(niche: str, max_results: int) -> List[Dict[str, Any]]:
    """Best-effort TikTok scraper via requests. Silently returns [] on failure."""
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        return []

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        resp = requests.get(
            "https://www.tiktok.com/trending",
            headers=headers,
            timeout=15,
        )
        soup = BeautifulSoup(resp.text, "html.parser")
        # TikTok's markup changes frequently — this is intentionally minimal
        items = []
        for el in soup.select("[data-e2e='challenge-item']")[:max_results]:
            tag_el = el.select_one("[data-e2e='challenge-name']")
            if tag_el:
                items.append({
                    "rank": len(items) + 1,
                    "hashtag": f"#{tag_el.get_text(strip=True)}",
                    "posts": 0,
                    "views": 0,
                    "growth_pct": 0,
                    "niche": niche,
                })
        return items
    except Exception:
        return []


def fetch_tiktok_trends(
    niche: str = "all",
    max_results: int = 20,
    live: bool = False,
    fetcher: Optional[Callable] = None,
) -> Dict[str, Any]:
    """Fetch TikTok viral trends.

    Args:
        niche: Niche filter ("all" for no filter).
        max_results: Maximum number of results.
        live: If True, attempt real HTTP fetch. Otherwise return mock data.
        fetcher: Injectable fetcher callable for testing.

    Returns:
        Dict with keys: success, source, niche, count, items
    """
    if not live:
        items = _MOCK_TIKTOK_TRENDS
        if niche != "all":
            items = [i for i in items if i.get("niche") == niche]
        items = items[:max_results]
        return {
            "success": True,
            "source": "mock",
            "niche": niche,
            "count": len(items),
            "items": items,
        }

    actual_fetcher = fetcher or _requests_tiktok_fetcher
    try:
        items = actual_fetcher(niche, max_results)
        source = "requests"
        if not items:
            # TikTok's JS rendering typically means 0 results — fall back silently
            mock_items = _MOCK_TIKTOK_TRENDS
            if niche != "all":
                mock_items = [i for i in mock_items if i.get("niche") == niche]
            items = mock_items[:max_results]
            source = "mock-fallback"
    except Exception as e:
        warnings.warn(f"TikTok fetch failed ({e}), using mock data")
        mock_items = _MOCK_TIKTOK_TRENDS
        if niche != "all":
            mock_items = [i for i in mock_items if i.get("niche") == niche]
        items = mock_items[:max_results]
        source = "mock-fallback"

    return {
        "success": True,
        "source": source,
        "niche": niche,
        "count": len(items),
        "items": items,
    }


# ── Snapshot management ───────────────────────────────────────────────────────

def get_trend_snapshot(
    session: Session,
    platform: str = "youtube",
    country: str = "US",
    niche: str = "all",
    live: bool = False,
    yt_fetcher: Optional[Callable] = None,
    tt_fetcher: Optional[Callable] = None,
) -> Dict[str, Any]:
    """Fetch trends and save a snapshot to the workspace.

    Args:
        session: Active session with a loaded workspace.
        platform: "youtube", "tiktok", or "both".
        country: Country code for YouTube trending.
        niche: Niche filter for TikTok.
        live: Whether to attempt real network fetching.
        yt_fetcher: Injectable YouTube fetcher for testing.
        tt_fetcher: Injectable TikTok fetcher for testing.

    Returns:
        The snapshot dict that was saved.
    """
    workspace = session.get_project()

    yt_items: List[Dict] = []
    tt_items: List[Dict] = []

    if platform in ("youtube", "both"):
        yt_result = fetch_youtube_trends(
            country=country, live=live, fetcher=yt_fetcher
        )
        yt_items = yt_result["items"]

    if platform in ("tiktok", "both"):
        tt_result = fetch_tiktok_trends(
            niche=niche, live=live, fetcher=tt_fetcher
        )
        tt_items = tt_result["items"]

    snap_id = _next_id(workspace["trend_snapshots"], "snap")

    snapshot = {
        "snapshot_id": snap_id,
        "timestamp": datetime.now().isoformat(),
        "platform": platform,
        "country": country,
        "niche": niche,
        "live": live,
        "youtube": yt_items,
        "tiktok": tt_items,
    }

    session.snapshot(f"Add trend snapshot {snap_id}")
    workspace["trend_snapshots"].append(snapshot)

    return {"success": True, "snapshot_id": snap_id, "snapshot": snapshot}


def list_snapshots(session: Session) -> List[Dict[str, Any]]:
    """List all saved snapshots (summary view)."""
    workspace = session.get_project()
    result = []
    for snap in workspace["trend_snapshots"]:
        result.append({
            "snapshot_id": snap["snapshot_id"],
            "timestamp": snap["timestamp"],
            "platform": snap["platform"],
            "country": snap["country"],
            "niche": snap["niche"],
            "yt_count": len(snap.get("youtube", [])),
            "tt_count": len(snap.get("tiktok", [])),
        })
    return result


def show_snapshot(session: Session, snapshot_id: str) -> Dict[str, Any]:
    """Show full detail of a snapshot."""
    workspace = session.get_project()
    snap = _find_snapshot(workspace, snapshot_id)
    return snap


def remove_snapshot(session: Session, snapshot_id: str) -> Dict[str, Any]:
    """Remove a snapshot from the workspace."""
    workspace = session.get_project()
    snap = _find_snapshot(workspace, snapshot_id)
    session.snapshot(f"Remove snapshot {snapshot_id}")
    workspace["trend_snapshots"] = [
        s for s in workspace["trend_snapshots"]
        if s["snapshot_id"] != snapshot_id
    ]
    return {"success": True, "removed": snapshot_id}


def _find_snapshot(workspace: Dict[str, Any], snapshot_id: str) -> Dict[str, Any]:
    """Find a snapshot by ID or raise ValueError."""
    for snap in workspace.get("trend_snapshots", []):
        if snap["snapshot_id"] == snapshot_id:
            return snap
    raise ValueError(f"Snapshot not found: '{snapshot_id}'")
