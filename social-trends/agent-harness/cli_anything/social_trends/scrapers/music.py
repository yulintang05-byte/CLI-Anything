"""Music trend scraper — Billboard Hot 100 + Spotify public charts."""

import json
import re
import urllib.request
import urllib.parse
from typing import Optional


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _fetch(url: str, timeout: int = 12) -> Optional[str]:
    req = urllib.request.Request(url, headers=_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def get_billboard_hot100(limit: int = 25) -> list[dict]:
    """Scrape Billboard Hot 100 chart (public page)."""
    html = _fetch("https://www.billboard.com/charts/hot-100/")
    if not html:
        return []

    results = []

    # Extract JSON-LD or embedded chart data
    # Billboard uses a script tag with chart data
    match = re.search(
        r'data-track-action="chart"[^>]*data-track-payload="([^"]+)"', html
    )

    # Try the structured data approach
    titles = re.findall(
        r'class="o-chart-results-list__item.*?'
        r'h3[^>]*id="title-of-a-story"[^>]*>\s*([^<\n]+)',
        html,
        re.DOTALL,
    )
    artists = re.findall(
        r'class="o-chart-results-list__item.*?'
        r'span[^>]*class="c-label[^"]*a-no-trucate[^"]*"[^>]*>\s*([^<\n]+)',
        html,
        re.DOTALL,
    )

    # Alternative: extract from the JSON-LD script
    ld_match = re.search(
        r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>',
        html,
        re.DOTALL,
    )

    # Most reliable: look for the chart-item divs
    entries = re.findall(
        r'class="lrv-u-width-100p[^"]*"[^>]*>.*?'
        r'<h3[^>]*>([^<]+)</h3>.*?'
        r'<span[^>]*class="[^"]*a-no-trucate[^"]*"[^>]*>([^<]+)</span>',
        html,
        re.DOTALL,
    )

    if entries:
        for rank, (title, artist) in enumerate(entries[:limit], 1):
            results.append(
                {
                    "rank": rank,
                    "title": title.strip(),
                    "artist": artist.strip(),
                    "chart": "Billboard Hot 100",
                    "platform": "billboard",
                }
            )
        return results

    # Last resort: extract title+artist pairs from meta/og tags
    og_titles = re.findall(r'"songTitle":"([^"]+)"', html)
    og_artists = re.findall(r'"artistName":"([^"]+)"', html)

    for rank, (title, artist) in enumerate(
        zip(og_titles[:limit], og_artists[:limit]), 1
    ):
        results.append(
            {
                "rank": rank,
                "title": title.strip(),
                "artist": artist.strip(),
                "chart": "Billboard Hot 100",
                "platform": "billboard",
            }
        )

    return results


def get_spotify_viral_50(country: str = "global") -> list[dict]:
    """
    Fetch Spotify Viral 50 chart via public charts page.
    country: 'global' or ISO 2-letter code like 'us', 'gb'
    """
    if country == "global":
        url = "https://charts.spotify.com/charts/view/viral-global-daily/latest"
    else:
        url = f"https://charts.spotify.com/charts/view/viral-{country.lower()}-daily/latest"

    html = _fetch(url)
    if not html:
        # Fallback to embedded JSON
        return _try_spotify_api(country)

    results = []

    # Spotify embeds chart data as JSON
    match = re.search(r'"chartEntryData":\s*(\[.*?\])\s*[,}]', html, re.DOTALL)
    if match:
        try:
            entries = json.loads(match.group(1))
            for e in entries[:50]:
                track = e.get("trackMetadata", {})
                results.append(
                    {
                        "rank": e.get("chartEntryData", {}).get("currentRank", len(results) + 1),
                        "title": track.get("trackName", ""),
                        "artist": ", ".join(
                            a.get("name", "") for a in track.get("artists", [])
                        ),
                        "peak": e.get("chartEntryData", {}).get("peakRank", None),
                        "streak": e.get("chartEntryData", {}).get("consecutiveAppearances", 0),
                        "chart": f"Spotify Viral 50 ({country})",
                        "platform": "spotify",
                    }
                )
            return results
        except json.JSONDecodeError:
            pass

    # Try inline JSON from the page
    track_names = re.findall(r'"trackName"\s*:\s*"([^"]+)"', html)
    artist_names = re.findall(r'"artistName"\s*:\s*"([^"]+)"', html)

    for rank, (title, artist) in enumerate(
        zip(track_names[:50], artist_names[:50]), 1
    ):
        results.append(
            {
                "rank": rank,
                "title": title,
                "artist": artist,
                "chart": f"Spotify Viral 50 ({country})",
                "platform": "spotify",
            }
        )

    return results


def _try_spotify_api(country: str = "global") -> list[dict]:
    """Try Spotify public JSON endpoint."""
    region = "global" if country == "global" else country.lower()
    url = f"https://charts.spotify.com/charts/view/viral-{region}-daily/latest"
    html = _fetch(url)
    return []


def get_tiktok_trending_sounds_from_cc(region: str = "US") -> list[dict]:
    """Re-export from tiktok module for convenience."""
    from cli_anything.social_trends.scrapers.tiktok import get_trending_sounds
    return get_trending_sounds(region=region)


def score_music_for_content(
    tracks: list[dict],
    content_type: str = "general",
) -> list[dict]:
    """
    Score tracks for content suitability.
    content_type: 'general', 'motivation', 'lifestyle', 'gaming', 'beauty', 'fitness'
    """
    genre_keywords = {
        "motivation": ["pump", "rise", "power", "champion", "fight", "fire", "victory"],
        "lifestyle": ["vibes", "chill", "summer", "love", "life", "feel", "mood"],
        "gaming": ["epic", "battle", "arena", "clash", "gaming", "digital", "level"],
        "beauty": ["glow", "queen", "beautiful", "glam", "shine", "pretty"],
        "fitness": ["workout", "run", "grind", "hustle", "sweat", "beast", "gains"],
        "general": [],
    }
    keywords = genre_keywords.get(content_type, [])

    scored = []
    for t in tracks:
        title_lower = (t.get("title", "") + " " + t.get("artist", "")).lower()
        score = t.get("rank", 999)  # lower rank = better
        # Bonus for keyword match
        for kw in keywords:
            if kw in title_lower:
                score = max(1, score - 10)
        scored.append({**t, "content_score": score})

    scored.sort(key=lambda x: x["content_score"])
    return scored
