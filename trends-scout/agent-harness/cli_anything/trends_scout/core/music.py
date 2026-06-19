"""Viral music aggregator — cross-platform trending sounds and tracks.

Combines data from YouTube Music charts, TikTok trending sounds,
and optionally Spotify/Last.fm (when API keys are configured).
"""
import re
from collections import Counter
from typing import Optional

from cli_anything.trends_scout.utils import config as cfg_mod
from cli_anything.trends_scout.utils.http import get_json, get_html

_LASTFM_API = "https://ws.audioscrobbler.com/2.0/"
_SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
_SPOTIFY_API = "https://api.spotify.com/v1"


# ── Last.fm (free API, no OAuth) ─────────────────────────────────────────────

def _lastfm_trending(limit: int = 20, country: str = "united states") -> list[dict]:
    """Get trending tracks from Last.fm charts (free API key required)."""
    api_key = cfg_mod.get("lastfm_api_key")
    if not api_key:
        return []
    params = {
        "method": "geo.getTopTracks" if country else "chart.getTopTracks",
        "country": country,
        "api_key": api_key,
        "format": "json",
        "limit": limit,
    }
    if not country:
        params["method"] = "chart.getTopTracks"
        params.pop("country", None)
    try:
        data = get_json(_LASTFM_API, params=params)
        tracks = (data.get("tracks", {}) or data.get("toptracks", {})).get("track", [])
        return [
            {
                "title": t.get("name", ""),
                "artist": t.get("artist", {}).get("name", "") if isinstance(t.get("artist"), dict) else t.get("artist", ""),
                "listeners": int(t.get("listeners", 0)),
                "playcount": int(t.get("playcount", 0)),
                "source": "lastfm",
            }
            for t in tracks
        ]
    except Exception:
        return []


# ── Spotify (requires client_id + client_secret) ────────────────────────────

def _spotify_token() -> Optional[str]:
    client_id = cfg_mod.get("spotify_client_id")
    client_secret = cfg_mod.get("spotify_client_secret")
    if not client_id or not client_secret:
        return None
    import base64
    import requests
    creds = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    resp = requests.post(
        _SPOTIFY_TOKEN_URL,
        data={"grant_type": "client_credentials"},
        headers={"Authorization": f"Basic {creds}"},
        timeout=10,
    )
    if resp.ok:
        return resp.json().get("access_token")
    return None


def _spotify_trending(limit: int = 20) -> list[dict]:
    """Get trending tracks from Spotify Global/US charts."""
    token = _spotify_token()
    if not token:
        return []
    import requests
    # Spotify's viral-50 and top-50 playlists (hardcoded IDs for US charts)
    playlist_ids = {
        "viral_us": "37i9dQZEVXbKuaTI1Z1Afx",
        "top_50_us": "37i9dQZEVXbLRQDuF5jeBp",
        "top_50_global": "37i9dQZEVXbMDoHDwVN2tF",
    }
    tracks = []
    for chart_name, playlist_id in list(playlist_ids.items())[:1]:  # one chart by default
        try:
            resp = requests.get(
                f"{_SPOTIFY_API}/playlists/{playlist_id}/tracks",
                params={"limit": limit, "fields": "items(track(name,artists,popularity))"},
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            if resp.ok:
                for item in resp.json().get("items", []):
                    track = item.get("track", {})
                    if not track:
                        continue
                    artists = ", ".join(a["name"] for a in track.get("artists", []))
                    tracks.append({
                        "title": track.get("name", ""),
                        "artist": artists,
                        "popularity": track.get("popularity", 0),
                        "chart": chart_name,
                        "source": "spotify",
                    })
        except Exception:
            continue
    return tracks


# ── YouTube Music charts scrape ──────────────────────────────────────────────

def _youtube_music_charts() -> list[dict]:
    """Scrape YouTube Music trending chart."""
    try:
        html = get_html("https://charts.youtube.com/us")
        # Extract embedded JSON data
        match = re.search(r'data\s*=\s*\'(.*?)\';\s*</script>', html, re.DOTALL)
        if not match:
            return []
        raw = match.group(1).encode().decode("unicode_escape")
        # Strip to valid JSON
        data = re.search(r'\{.*\}', raw, re.DOTALL)
        if not data:
            return []
        parsed = __import__("json").loads(data.group(0))
        items = (parsed.get("videos", {})
                       .get("items", []))
        tracks = []
        for item in items[:20]:
            tracks.append({
                "title": item.get("title", ""),
                "artist": item.get("artist", ""),
                "views": item.get("views", 0),
                "source": "youtube_music",
            })
        return tracks
    except Exception:
        return []


# ── Google Trends for music keywords ────────────────────────────────────────

def _google_trends_music() -> list[dict]:
    """Use pytrends to get Google Trends data for music-related terms."""
    try:
        from pytrends.request import TrendReq
        pt = TrendReq(hl="en-US", tz=360)
        pt.build_payload(["new music", "viral song", "trending music"],
                         cat=35, timeframe="now 7-d", geo="US")
        related = pt.related_queries()
        tracks = []
        for kw, data in related.items():
            rising = data.get("rising")
            if rising is not None and not rising.empty:
                for _, row in rising.head(5).iterrows():
                    tracks.append({
                        "query": row.get("query", ""),
                        "value": row.get("value", 0),
                        "source": "google_trends",
                    })
        return tracks
    except Exception:
        return []


# ── Public API ──────────────────────────────────────────────────────────────

def get_viral_music(region: str = "US", limit: int = 30) -> dict:
    """Aggregate viral music from all configured sources."""
    from cli_anything.trends_scout.core import tiktok as tt_mod
    from cli_anything.trends_scout.core import youtube as yt_mod

    all_tracks: list[dict] = []

    # TikTok sounds
    try:
        tt_data = tt_mod.get_trending_sounds(region=region, limit=25)
        for s in tt_data.get("trending_sounds", []):
            all_tracks.append({
                "title": s["title"],
                "artist": s["artist"],
                "platform": "tiktok",
                "metric": s["video_count"],
                "metric_label": "tiktok_videos",
                "url": s.get("url", ""),
            })
    except Exception:
        pass

    # YouTube Music
    try:
        yt_data = yt_mod.get_trending_music(region=region, limit=25)
        for t in yt_data.get("trending_music", []):
            all_tracks.append({
                "title": t["song"],
                "artist": t["artist"],
                "platform": "youtube",
                "metric": t["views"],
                "metric_label": "youtube_views",
                "url": t.get("url", ""),
            })
    except Exception:
        pass

    # Last.fm
    lastfm_tracks = _lastfm_trending(limit=20)
    for t in lastfm_tracks:
        all_tracks.append({
            "title": t["title"],
            "artist": t["artist"],
            "platform": "lastfm",
            "metric": t["listeners"],
            "metric_label": "lastfm_listeners",
            "url": "",
        })

    # Spotify
    spotify_tracks = _spotify_trending(limit=20)
    for t in spotify_tracks:
        all_tracks.append({
            "title": t["title"],
            "artist": t["artist"],
            "platform": "spotify",
            "metric": t["popularity"],
            "metric_label": "spotify_popularity",
            "url": "",
        })

    # Deduplicate by title (case-insensitive)
    seen_titles: set = set()
    unique_tracks = []
    for t in all_tracks:
        key = t["title"].lower().strip()
        if key and key not in seen_titles:
            seen_titles.add(key)
            unique_tracks.append(t)

    return {
        "total": len(unique_tracks),
        "region": region,
        "sources": list({t["platform"] for t in unique_tracks}),
        "tracks": unique_tracks[:limit],
    }


def get_cross_platform_hits() -> dict:
    """Find tracks trending on BOTH TikTok and YouTube — strongest signal."""
    from cli_anything.trends_scout.core import tiktok as tt_mod
    from cli_anything.trends_scout.core import youtube as yt_mod

    try:
        tt_sounds = tt_mod.get_trending_sounds(limit=30).get("trending_sounds", [])
        tt_titles = {s["title"].lower(): s for s in tt_sounds if s.get("title")}
    except Exception:
        tt_titles = {}

    try:
        yt_music = yt_mod.get_trending_music(limit=30).get("trending_music", [])
        yt_titles = {t["song"].lower(): t for t in yt_music if t.get("song")}
    except Exception:
        yt_titles = {}

    cross_hits = []
    for title_lower, tt_data in tt_titles.items():
        for yt_key, yt_data in yt_titles.items():
            if title_lower in yt_key or yt_key in title_lower:
                cross_hits.append({
                    "title": tt_data["title"],
                    "artist": tt_data.get("artist", yt_data.get("artist", "")),
                    "tiktok_videos": tt_data.get("video_count", 0),
                    "youtube_views": yt_data.get("views", 0),
                    "verdict": "CROSS-PLATFORM HIT — use this sound NOW",
                })
                break

    return {
        "cross_platform_hits": cross_hits,
        "total": len(cross_hits),
        "insight": "These tracks trend on both platforms — maximum reach potential.",
    }
