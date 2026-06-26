"""Trending music aggregation — TikTok sounds + YouTube music + Billboard."""

import re
from typing import Any, Dict, List, Optional

from cli_anything.social_trends.utils.http import get_json, get_text, _DEFAULT_HEADERS

# Spotify public charts (no auth — redirects to CSV download)
_SPOTIFY_CHARTS_BASE = "https://charts.spotify.com/charts/view"
# Billboard Hot 100 JSON feed
_BILLBOARD_HOT100 = "https://www.billboard.com/charts/hot-100/"


def fetch_spotify_chart(
    region: str = "US",
    chart: str = "regional",
    frequency: str = "weekly",
) -> Dict[str, Any]:
    """
    Fetch Spotify chart data.

    chart: 'regional' (regional top 50) or 'viral' (viral 50)
    frequency: 'weekly' or 'daily'
    """
    region_lower = region.lower()
    if chart == "viral":
        chart_id = f"viral-{region_lower}-{frequency}"
    else:
        chart_id = f"regional-{region_lower}-{frequency}"

    url = f"{_SPOTIFY_CHARTS_BASE}/{chart_id}/latest"

    try:
        # Spotify charts returns a CSV; parse it
        text = get_text(
            url,
            headers={**_DEFAULT_HEADERS, "Accept": "text/csv,text/plain,*/*"},
        )
        return _parse_spotify_csv(text, region, chart, frequency)
    except Exception as e:
        raise RuntimeError(
            f"Spotify chart fetch failed for region '{region}'. "
            f"Try 'US', 'GB', 'AU', or 'global'. Error: {e}"
        )


def _parse_spotify_csv(text: str, region: str, chart: str, freq: str) -> Dict[str, Any]:
    """Parse Spotify's CSV chart format."""
    lines = text.strip().splitlines()
    tracks = []

    # Skip header lines (Spotify charts have 2-line header + column row)
    start_idx = 0
    for i, line in enumerate(lines):
        if line.lower().startswith("rank,") or line.lower().startswith('"rank"'):
            start_idx = i + 1
            break

    for line in lines[start_idx:]:
        if not line.strip():
            continue
        parts = _csv_split(line)
        if len(parts) < 4:
            continue
        try:
            tracks.append({
                "rank": int(parts[0].strip().strip('"')),
                "title": parts[1].strip().strip('"'),
                "artist": parts[2].strip().strip('"'),
                "streams": _safe_int(parts[3].strip().strip('"').replace(",", "")),
                "url": parts[4].strip().strip('"') if len(parts) > 4 else "",
            })
        except (IndexError, ValueError):
            continue

    return {
        "source": "spotify_charts",
        "region": region,
        "chart": chart,
        "frequency": freq,
        "total": len(tracks),
        "tracks": tracks[:50],
    }


def aggregate_trending_music(
    tiktok_sounds: List[Dict[str, Any]],
    youtube_music: List[Dict[str, Any]],
    spotify_tracks: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Cross-reference trending music across TikTok, YouTube, and Spotify.

    Returns a unified ranked list with platform presence indicators.
    """
    # Build lookup tables
    tt_titles = {_normalize_title(s.get("title", "")): s for s in tiktok_sounds}
    yt_titles = {_normalize_title(v.get("title", "")): v for v in youtube_music}
    sp_titles = {_normalize_title(t.get("title", "")): t for t in (spotify_tracks or [])}

    # All unique titles
    all_titles = set(list(tt_titles.keys()) + list(yt_titles.keys()) + list(sp_titles.keys()))

    unified = []
    for norm_title in all_titles:
        tt = tt_titles.get(norm_title)
        yt = yt_titles.get(norm_title)
        sp = sp_titles.get(norm_title)

        platforms = []
        if tt:
            platforms.append("tiktok")
        if yt:
            platforms.append("youtube")
        if sp:
            platforms.append("spotify")

        # Cross-platform score: more platforms = stronger signal
        score = len(platforms) * 30
        if tt:
            score += min(tt.get("clip_count", 0) / 100_000, 30)
        if yt:
            score += min(yt.get("views", 0) / 1_000_000, 30)
        if sp:
            score += max(0, 50 - sp.get("rank", 50))

        title = (tt or yt or sp or {}).get("title", norm_title)
        artist = (tt or yt or {}).get("artist", "") or (sp or {}).get("artist", "")

        unified.append({
            "title": title,
            "artist": artist,
            "platforms": platforms,
            "platform_count": len(platforms),
            "virality_score": round(score),
            "tiktok_clips": tt.get("clip_count", 0) if tt else 0,
            "youtube_views": yt.get("views", 0) if yt else 0,
            "spotify_rank": sp.get("rank", None) if sp else None,
            "recommendation": _music_recommendation(platforms, score),
        })

    unified.sort(key=lambda x: (-x["platform_count"], -x["virality_score"]))
    return {
        "total": len(unified),
        "cross_platform_hits": [t for t in unified if t["platform_count"] >= 2],
        "tiktok_only": [t for t in unified if t["platforms"] == ["tiktok"]],
        "youtube_only": [t for t in unified if t["platforms"] == ["youtube"]],
        "all_tracks": unified[:50],
    }


def _music_recommendation(platforms: List[str], score: float) -> str:
    count = len(platforms)
    if count >= 3:
        return "VIRAL — trending everywhere. Use this sound immediately for maximum reach."
    if count == 2:
        return "STRONG — trending on 2 platforms. Excellent choice for Reels/Shorts/TikTok."
    if score > 40:
        return "EMERGING — high growth on one platform. Use early for algorithmic advantage."
    return "NICHE — moderate reach on one platform."


def get_safe_for_use_music_tips() -> Dict[str, Any]:
    """
    Return guidance on copyright-safe music usage across platforms.
    """
    return {
        "tiktok": {
            "safe_options": [
                "TikTok Commercial Music Library (free for business accounts)",
                "TikTok Sounds with a ✓ Commercial Use badge",
                "Original audio you create yourself",
                "Royalty-free music from Epidemic Sound, Artlist, or Pixabay",
            ],
            "avoid": "Trending chart music unless you have a license — account bans for repeat violations",
            "tip": "Using a trending sound that is NOT licensed gives your video 2-3x more reach initially, but risks removal.",
        },
        "youtube": {
            "safe_options": [
                "YouTube Audio Library (free, royalty-free)",
                "Music with CC licenses (search YouTube with Creative Commons filter)",
                "Epidemic Sound, Artlist subscription tracks",
                "Your own original music",
            ],
            "avoid": "ASCAP/BMI licensed tracks without Content ID clearance",
            "tip": "YouTube will mute or monetize-redirect videos with unlicensed music — the original uploader loses ad revenue.",
        },
        "instagram_reels": {
            "safe_options": [
                "Instagram's music library (personal accounts only)",
                "Business accounts: only music licensed by Meta",
                "Original audio",
                "Meta Business Suite licensed content",
            ],
            "avoid": "Most chart music on business/creator accounts — will silence the Reel",
            "tip": "If going viral with a trend, post as a personal account first, then reshare to your business page.",
        },
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _normalize_title(title: str) -> str:
    """Normalize a track title for fuzzy matching."""
    clean = title.lower()
    clean = re.sub(r"\(.*?\)|\[.*?\]", "", clean)
    clean = re.sub(r"feat\.?\s+\w+", "", clean)
    clean = re.sub(r"[^\w\s]", "", clean)
    return clean.strip()


def _csv_split(line: str) -> List[str]:
    """Simple CSV split handling quoted fields."""
    parts = []
    current = ""
    in_quotes = False
    for ch in line:
        if ch == '"':
            in_quotes = not in_quotes
        elif ch == "," and not in_quotes:
            parts.append(current)
            current = ""
        else:
            current += ch
    parts.append(current)
    return parts


def _safe_int(val: Any) -> int:
    try:
        return int(str(val).replace(",", "") or 0)
    except (TypeError, ValueError):
        return 0
