"""HTTP backend for social media trend scraping.

Handles requests, caching, rate limiting, and config persistence.
All network I/O is isolated here.
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Any
import requests

CONFIG_DIR = Path.home() / ".cli-anything-social-trends"
CACHE_DIR = CONFIG_DIR / "cache"
CONFIG_FILE = CONFIG_DIR / "config.json"

CACHE_TTL = 3600  # 1 hour default TTL

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json, text/html, */*",
}

TIKTOK_CC_BASE = "https://ads.tiktok.com/business/creativecenter/api/v1"
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
YOUTUBE_RSS_TRENDING = "https://www.youtube.com/feeds/videos.xml?chart=trending"


def _ensure_dirs():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(config: dict):
    _ensure_dirs()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def _cache_key(url: str, params: dict) -> str:
    raw = url + json.dumps(params, sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()


def _read_cache(key: str, ttl: int = CACHE_TTL) -> dict | None:
    path = CACHE_DIR / f"{key}.json"
    if not path.exists():
        return None
    try:
        with open(path) as f:
            entry = json.load(f)
        if time.time() - entry.get("saved_at", 0) < ttl:
            return entry["data"]
    except Exception:
        pass
    return None


def _write_cache(key: str, data: Any):
    _ensure_dirs()
    path = CACHE_DIR / f"{key}.json"
    with open(path, "w") as f:
        json.dump({"saved_at": time.time(), "data": data}, f)


def get(url: str, params: dict | None = None, headers: dict | None = None,
        ttl: int = CACHE_TTL, bypass_cache: bool = False) -> dict | list:
    """GET with caching. Returns parsed JSON."""
    params = params or {}
    key = _cache_key(url, params)

    if not bypass_cache:
        cached = _read_cache(key, ttl)
        if cached is not None:
            return cached

    merged_headers = {**HEADERS, **(headers or {})}
    resp = requests.get(url, params=params, headers=merged_headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    _write_cache(key, data)
    return data


def get_html(url: str, params: dict | None = None, ttl: int = CACHE_TTL,
             bypass_cache: bool = False) -> str:
    """GET HTML with caching. Returns response text."""
    params = params or {}
    key = _cache_key(url, params) + "_html"

    if not bypass_cache:
        path = CACHE_DIR / f"{key}.txt"
        if path.exists():
            try:
                entry = json.loads(path.read_text())
                if time.time() - entry.get("saved_at", 0) < ttl:
                    return entry["data"]
            except Exception:
                pass

    resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    text = resp.text
    _ensure_dirs()
    path = CACHE_DIR / f"{key}.txt"
    path.write_text(json.dumps({"saved_at": time.time(), "data": text}))
    return text


def clear_cache():
    """Remove all cached responses."""
    _ensure_dirs()
    count = 0
    for f in CACHE_DIR.iterdir():
        f.unlink()
        count += 1
    return {"cleared": count}


def cache_stats() -> dict:
    """Return cache statistics."""
    _ensure_dirs()
    files = list(CACHE_DIR.iterdir())
    total_bytes = sum(f.stat().st_size for f in files)
    now = time.time()
    fresh = sum(
        1 for f in files
        if f.suffix == ".json" and _is_fresh(f, CACHE_TTL)
    )
    return {
        "total_entries": len(files),
        "fresh_entries": fresh,
        "total_size_kb": round(total_bytes / 1024, 1),
        "cache_dir": str(CACHE_DIR),
    }


def _is_fresh(path: Path, ttl: int) -> bool:
    try:
        with open(path) as f:
            entry = json.load(f)
        return time.time() - entry.get("saved_at", 0) < ttl
    except Exception:
        return False
