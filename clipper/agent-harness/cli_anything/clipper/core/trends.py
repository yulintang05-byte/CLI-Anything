"""Trend intelligence for short-form exports (TikTok, YouTube Shorts, Reels).

Three data sources, best-first:
  1. YouTube Data API ``chart=mostPopular`` (needs ``YOUTUBE_API_KEY``).
  2. Public YouTube hashtag pages (``/hashtag/<tag>``), parsed from ytInitialData.
  3. A curated snapshot bundled below (refreshed by the daily routine).

TikTok's Creative Center API requires an authenticated session (it returns
``40101 no permission`` anonymously) and its web pages are JS-rendered, so
TikTok data comes from the curated snapshot or from a JSON file you export
from Creative Center and pass with ``--snapshot``.
"""

from __future__ import annotations

import json
import os
import re
import urllib.parse
import urllib.request
from collections import Counter
from typing import Any, Dict, List, Optional

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"

# Hashtag caps per platform. TikTok/Reels reward 3-5 targeted tags; YouTube
# ignores all tags if a title/description has more than 15 and shows the
# first 3 above the title.
PLATFORM_LIMITS = {"tiktok": 5, "shorts": 3, "reels": 5, "twitter": 2}

# ── Curated snapshot (verify on TikTok Discover / Creative Center before use) ─
SNAPSHOT: Dict[str, Any] = {
    "as_of": "2026-11-13",
    "sources": [
        "https://tokchart.com/tiktok-trending-hashtags",
        "https://www.revid.ai/tiktok-trending-hashtags",
        "https://www.howtogoviral.app/tiktok-trends",
        "https://www.revid.ai/viral-tiktok-songs",
        "https://socialbee.com/blog/trending-tiktok-songs/",
        "https://www.socialpilot.co/blog/tiktok-trends",
        "https://soundcharts.com/en/charts/tiktok/worldwide",
    ],
    "tiktok": {
        "rising_hashtags": [
            "#pick14daychallenge", "#personalfinance", "#money", "#grwm",
            "#dogsoftiktok", "#bluewave", "#livecanbeeasy", "#holidayprep",
            "#dayinmylife", "#autumnvibes", "#teslaroadster", "#roblox",
        ],
        "sounds": [
            {"title": "Coming Up Roses", "artist": "Harry Styles", "use": "aesthetic montages, music-video recreations"},
            {"title": "Housewife", "artist": "Tate McRae", "use": "dance / GRWM"},
            {"title": "Ramalama (Bang Bang)", "artist": "Róisín Murphy", "use": "transitions, fashion reveals"},
            {"title": "Nicole Kidman (Official Instrumental)", "artist": "Dan Swift Del Rey", "use": "background bed for talking/faceless edits"},
            {"title": "H4UNT", "artist": "baldgirl", "use": "'costume loading' freeze-frame transitions"},
            {"title": "Ain't In LA", "artist": "ADÉLA", "use": "'someone's gotta hold it down' trend"},
            {"title": "Rockin' Around the Christmas Tree", "artist": "Brenda Lee", "use": "holiday content (seasonal ramp starts now)"},
        ],
        "formats": [
            "14-day challenge series (#pick14daychallenge) - episodic, drives follows",
            "Freeze-frame 'loading' transitions (H4UNT sound)",
            "Holiday prep / gift guides - ramps through December",
            "Day-in-my-life and GRWM with a money/finance angle",
        ],
    },
    "shorts": {
        "rising_hashtags": ["#shorts", "#minecraft", "#comedy", "#funny", "#mukbang", "#lifehacks"],
        "formats": [
            "Micro-dramas: full story arc in <60s",
            "Friend-group POV skits",
            "Faceless explainers with AI voiceover + 'unexpected fact' hook",
            "Food challenges / extreme taste tests",
            "Non-verbal loop-first edits (no translation needed, global reach)",
        ],
        "best_length_seconds": [20, 35],
    },
    "evergreen": {
        "broad": ["#fyp", "#viral"],
        "niches": {
            "gaming": ["#gaming", "#gamingclips", "#roblox", "#minecraft", "#fortnite"],
            "finance": ["#personalfinance", "#money", "#moneytok", "#sidehustle", "#investing"],
            "motivation": ["#motivation", "#mindset", "#discipline", "#selfimprovement"],
            "comedy": ["#comedy", "#funny", "#skit", "#relatable"],
            "pets": ["#dogsoftiktok", "#catsoftiktok", "#petsoftiktok", "#funnyanimals"],
            "lifestyle": ["#dayinmylife", "#grwm", "#vlog", "#autumnvibes"],
            "tech": ["#tech", "#ai", "#techtok", "#gadgets"],
            "streamer": ["#streamer", "#twitchclips", "#clips", "#highlights"],
        },
    },
}


def _get(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - fixed https URLs
        return resp.read().decode("utf-8", errors="replace")


def _texts(node: Any, out: List[str]) -> None:
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("headline", "title") and isinstance(v, dict):
                t = v.get("simpleText") or "".join(r.get("text", "") for r in v.get("runs", []))
                if t:
                    out.append(t)
            _texts(v, out)
    elif isinstance(node, list):
        for x in node:
            _texts(x, out)


def extract_hashtags(texts: List[str]) -> Counter:
    return Counter(h.lower() for t in texts for h in re.findall(r"#[^\s#]{2,40}", t))


def fetch_youtube_hashtag(tag: str = "shorts") -> Dict[str, Any]:
    """Scrape a public YouTube hashtag page for current video titles + co-tags."""
    tag = tag.lstrip("#")
    html = _get(f"https://www.youtube.com/hashtag/{urllib.parse.quote(tag)}?hl=en&gl=US")
    m = re.search(r"var ytInitialData = (\{.*?\});</script>", html, re.S)
    if not m:
        raise RuntimeError("ytInitialData not found - YouTube page layout changed")
    titles: List[str] = []
    _texts(json.loads(m.group(1)), titles)
    titles = [t for t in titles if "#" in t]  # drop UI chrome strings
    return {"source": f"youtube:/hashtag/{tag}", "titles": titles,
            "hashtags": extract_hashtags(titles).most_common(30)}


def fetch_youtube_api(region: str = "US", api_key: Optional[str] = None, max_results: int = 50) -> Dict[str, Any]:
    """Most-popular videos via YouTube Data API v3 (needs an API key)."""
    api_key = api_key or os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY not set")
    q = urllib.parse.urlencode({"part": "snippet,statistics", "chart": "mostPopular",
                                "regionCode": region, "maxResults": max_results, "key": api_key})
    data = json.loads(_get(f"https://www.googleapis.com/youtube/v3/videos?{q}"))
    texts, tags = [], Counter()
    for item in data.get("items", []):
        sn = item.get("snippet", {})
        texts.append(sn.get("title", "") + " " + sn.get("description", "")[:500])
        tags.update(t.lower() for t in sn.get("tags", []))
    return {"source": f"youtube-api:mostPopular:{region}",
            "titles": [t.split("  ")[0][:120] for t in texts],
            "hashtags": extract_hashtags(texts).most_common(30),
            "keywords": tags.most_common(30)}


def load_snapshot(path: Optional[str] = None) -> Dict[str, Any]:
    if not path:
        return SNAPSHOT
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def suggest(platform: str = "tiktok", niche: Optional[str] = None,
            snapshot: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> Dict[str, Any]:
    """Build a hashtag set: niche tags first, then a matching trend, then one broad tag.

    Order matters: niche tags tell the algorithm who to test the video on;
    a single broad tag adds little but does not hurt.
    """
    snap = snapshot or SNAPSHOT
    if platform not in PLATFORM_LIMITS:
        raise ValueError(f"Unknown platform '{platform}'. Available: {list(PLATFORM_LIMITS)}")
    limit = limit or PLATFORM_LIMITS[platform]
    niches = snap["evergreen"]["niches"]
    if niche and niche not in niches:
        raise ValueError(f"Unknown niche '{niche}'. Available: {sorted(niches)}")

    niche_tags = niches.get(niche, []) if niche else []
    trend_src = snap.get("shorts" if platform == "shorts" else "tiktok", {}).get("rising_hashtags", [])
    trending = [t for t in trend_src if t in niche_tags] or [t for t in trend_src if t != "#shorts"][:1]

    tags: List[str] = []
    if platform == "shorts":
        tags.append("#shorts")
    for t in niche_tags[:3] + trending + snap["evergreen"]["broad"][:1]:
        if t not in tags:
            tags.append(t)
    sounds = snap.get("tiktok", {}).get("sounds", [])[:3] if platform in ("tiktok", "reels") else []
    return {"platform": platform, "niche": niche, "hashtags": tags[:limit],
            "suggested_sounds": sounds, "snapshot_as_of": snap.get("as_of")}


def apply_to_project(session, platform: str, niche: Optional[str] = None,
                     caption: Optional[str] = None,
                     snapshot: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Store a platform's caption + hashtags in project metadata (undoable)."""
    project = session.get_project()
    s = suggest(platform, niche, snapshot)
    session.snapshot(f"trends apply {platform}")
    social = project.setdefault("metadata", {}).setdefault("social", {})
    entry = {"hashtags": s["hashtags"], "snapshot_as_of": s["snapshot_as_of"]}
    if caption:
        entry["caption"] = f"{caption.strip()} {' '.join(s['hashtags'])}"
    if s["suggested_sounds"]:
        entry["sound"] = s["suggested_sounds"][0]
    social[platform] = entry
    return {"success": True, "platform": platform, **entry}
