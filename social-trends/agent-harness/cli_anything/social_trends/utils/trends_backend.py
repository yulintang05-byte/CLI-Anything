"""Social Trends backend — HTTP wrappers for YouTube Data API v3 and TikTok Research API.

This is the only module that makes network requests. All API keys are
stored in ~/.cli-anything-social-trends/ and loaded on demand.
"""

import json
import time
import requests
from pathlib import Path
from typing import Any


# YouTube Data API v3
YT_API_BASE = "https://www.googleapis.com/youtube/v3"

# TikTok Research API
TT_RESEARCH_BASE = "https://open.tiktokapis.com/v2"
TT_AUTH_URL = "https://open.tiktokapis.com/v2/oauth/token/"

# Web-scrape fallback headers (public TikTok trending pages)
SCRAPE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json, text/plain, */*",
}

CONFIG_DIR = Path.home() / ".cli-anything-social-trends"
YT_KEY_FILE = CONFIG_DIR / "youtube_key.json"
TT_KEY_FILE = CONFIG_DIR / "tiktok_key.json"
TT_TOKEN_FILE = CONFIG_DIR / "tiktok_token.json"
CACHE_FILE = CONFIG_DIR / "trends_cache.json"

CACHE_TTL_SECONDS = 900  # 15 minutes


# ── Config helpers ──────────────────────────────────────────────────────────

def _ensure_config_dir() -> Path:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR


def save_youtube_key(api_key: str):
    _ensure_config_dir()
    with open(YT_KEY_FILE, "w") as f:
        json.dump({"api_key": api_key}, f, indent=2)


def load_youtube_key() -> str:
    if not YT_KEY_FILE.exists():
        raise RuntimeError(
            "YouTube API key not configured. "
            "Run: social-trends auth youtube --api-key <KEY>"
        )
    with open(YT_KEY_FILE) as f:
        data = json.load(f)
    key = data.get("api_key", "")
    if not key:
        raise RuntimeError("YouTube API key is empty. Re-run: social-trends auth youtube --api-key <KEY>")
    return key


def save_tiktok_creds(client_key: str, client_secret: str):
    _ensure_config_dir()
    with open(TT_KEY_FILE, "w") as f:
        json.dump({"client_key": client_key, "client_secret": client_secret}, f, indent=2)


def load_tiktok_creds() -> dict:
    if not TT_KEY_FILE.exists():
        raise RuntimeError(
            "TikTok credentials not configured. "
            "Run: social-trends auth tiktok --client-key <K> --client-secret <S>"
        )
    with open(TT_KEY_FILE) as f:
        return json.load(f)


def _load_tiktok_token() -> dict:
    if not TT_TOKEN_FILE.exists():
        return {}
    with open(TT_TOKEN_FILE) as f:
        return json.load(f)


def _save_tiktok_token(token_data: dict):
    _ensure_config_dir()
    token_data["fetched_at"] = time.time()
    with open(TT_TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)


def get_tiktok_access_token() -> str:
    """Return a valid TikTok Research API bearer token, refreshing if expired."""
    token_data = _load_tiktok_token()
    fetched_at = token_data.get("fetched_at", 0)
    expires_in = token_data.get("expires_in", 7200)

    if token_data and (time.time() - fetched_at < expires_in - 60):
        return token_data["access_token"]

    creds = load_tiktok_creds()
    resp = requests.post(
        TT_AUTH_URL,
        data={
            "client_key": creds["client_key"],
            "client_secret": creds["client_secret"],
            "grant_type": "client_credentials",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("error"):
        raise RuntimeError(f"TikTok auth error: {data['error_description']}")
    _save_tiktok_token(data)
    return data["access_token"]


# ── Cache ───────────────────────────────────────────────────────────────────

def _load_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}
    try:
        with open(CACHE_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def _save_cache(cache: dict):
    _ensure_config_dir()
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def cached(key: str, fetch_fn, ttl: int = CACHE_TTL_SECONDS) -> Any:
    """Return cached result or call fetch_fn and cache its result."""
    cache = _load_cache()
    entry = cache.get(key, {})
    if entry and (time.time() - entry.get("ts", 0)) < ttl:
        return entry["data"]
    result = fetch_fn()
    cache[key] = {"ts": time.time(), "data": result}
    _save_cache(cache)
    return result


def clear_cache():
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
    return {"status": "cache cleared"}


# ── YouTube API ─────────────────────────────────────────────────────────────

def yt_get(endpoint: str, params: dict | None = None) -> Any:
    """Make an authenticated YouTube Data API GET request."""
    api_key = load_youtube_key()
    url = f"{YT_API_BASE}/{endpoint}"
    p = {"key": api_key}
    if params:
        p.update(params)
    resp = requests.get(url, params=p, timeout=30)
    resp.raise_for_status()
    return resp.json()


# ── TikTok Research API ─────────────────────────────────────────────────────

def tt_post(endpoint: str, data: dict | None = None) -> Any:
    """Make an authenticated TikTok Research API POST request."""
    token = get_tiktok_access_token()
    url = f"{TT_RESEARCH_BASE}{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    resp = requests.post(url, json=data or {}, headers=headers, timeout=30)
    resp.raise_for_status()
    result = resp.json()
    if result.get("error", {}).get("code", "ok") != "ok":
        raise RuntimeError(f"TikTok API error: {result['error'].get('message', 'unknown')}")
    return result.get("data", result)


# ── TikTok public web scrape (no API key needed) ────────────────────────────

def tt_scrape_trending_hashtags(region: str = "US") -> list[dict]:
    """Scrape publicly visible TikTok trending hashtag data."""
    url = "https://www.tiktok.com/api/explore/item_list/"
    params = {
        "aid": "1988",
        "app_language": "en",
        "count": "30",
        "region": region,
    }
    try:
        resp = requests.get(url, headers=SCRAPE_HEADERS, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("itemList", [])
    except Exception:
        pass
    return []


def tt_scrape_trending_music(region: str = "US") -> list[dict]:
    """Scrape TikTok trending music from the discover page."""
    url = "https://www.tiktok.com/api/music/list/"
    params = {
        "aid": "1988",
        "count": "30",
        "filterGeo": region,
    }
    try:
        resp = requests.get(url, headers=SCRAPE_HEADERS, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("musicList", [])
    except Exception:
        pass
    return []


def check_youtube_configured() -> bool:
    return YT_KEY_FILE.exists() and bool(
        json.loads(YT_KEY_FILE.read_text()).get("api_key") if YT_KEY_FILE.exists() else ""
    )


def check_tiktok_configured() -> bool:
    return TT_KEY_FILE.exists()
