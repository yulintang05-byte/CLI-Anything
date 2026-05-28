"""Social media backend — HTTP session, config, and shared helpers.

Handles all network requests and credential storage for the social-trends CLI.
Config is persisted at ~/.cli-anything-social-trends/config.json
"""

import json
import time
import random
import requests
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".cli-anything-social-trends"
CONFIG_FILE = CONFIG_DIR / "config.json"
CACHE_DIR = CONFIG_DIR / "cache"

# Common browser-like headers to avoid being blocked
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}

# TikTok-specific headers
_TIKTOK_HEADERS = {
    **_HEADERS,
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.tiktok.com/",
    "Origin": "https://www.tiktok.com",
}

# YouTube Data API v3 base
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


def get_config_dir() -> Path:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(config: dict):
    get_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_session(platform: str = "default") -> requests.Session:
    """Create a configured requests session for the given platform."""
    session = requests.Session()
    if platform == "tiktok":
        session.headers.update(_TIKTOK_HEADERS)
    else:
        session.headers.update(_HEADERS)
    return session


def cache_get(key: str) -> dict | None:
    """Read a cached response (valid for 30 minutes)."""
    get_config_dir()
    cache_file = CACHE_DIR / f"{key}.json"
    if not cache_file.exists():
        return None
    try:
        with open(cache_file, "r") as f:
            data = json.load(f)
        if time.time() - data.get("cached_at", 0) > 1800:
            return None
        return data.get("payload")
    except Exception:
        return None


def cache_set(key: str, payload: Any):
    """Write a response to cache."""
    get_config_dir()
    cache_file = CACHE_DIR / f"{key}.json"
    with open(cache_file, "w") as f:
        json.dump({"cached_at": time.time(), "payload": payload}, f)


def youtube_api_get(endpoint: str, params: dict) -> dict:
    """Make a YouTube Data API v3 GET request.

    Requires YOUTUBE_API_KEY in config.
    """
    config = load_config()
    api_key = config.get("youtube_api_key")
    if not api_key:
        raise RuntimeError(
            "YouTube API key not configured. "
            "Run: cli-anything-social-trends auth setup --youtube-api-key <KEY>"
        )
    params["key"] = api_key
    resp = requests.get(
        f"{YOUTUBE_API_BASE}/{endpoint}",
        params=params,
        headers=_HEADERS,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def fetch_url(url: str, platform: str = "default",
              params: dict | None = None, timeout: int = 30) -> requests.Response:
    """Fetch a URL with platform-appropriate headers."""
    session = get_session(platform)
    resp = session.get(url, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp


def fetch_json(url: str, platform: str = "default",
               params: dict | None = None, timeout: int = 30) -> Any:
    """Fetch a URL and parse as JSON."""
    resp = fetch_url(url, platform, params, timeout)
    return resp.json()


def jitter_sleep(min_s: float = 0.5, max_s: float = 1.5):
    """Sleep a random amount to avoid rate limiting."""
    time.sleep(random.uniform(min_s, max_s))
