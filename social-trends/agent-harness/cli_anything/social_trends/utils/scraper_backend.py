"""HTTP backend for social-trends — all network I/O lives here.

Handles headers, rate-limiting, user-agent rotation, and config storage.
"""

import json
import time
import random
import hashlib
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

# ── Config paths ──────────────────────────────────────────────────────────────

CONFIG_DIR = Path.home() / ".cli-anything-social-trends"
CONFIG_FILE = CONFIG_DIR / "config.json"
CACHE_DIR = CONFIG_DIR / "cache"


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


# ── User-agent pool ───────────────────────────────────────────────────────────

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
]


def _random_ua() -> str:
    return random.choice(_USER_AGENTS)


# ── Cache helpers ─────────────────────────────────────────────────────────────

def _cache_path(key: str) -> Path:
    h = hashlib.sha256(key.encode()).hexdigest()[:16]
    return CACHE_DIR / f"{h}.json"


def _cache_get(key: str, ttl_seconds: int = 1800) -> dict | None:
    """Return cached result if fresh, else None."""
    p = _cache_path(key)
    if not p.exists():
        return None
    try:
        with open(p) as f:
            entry = json.load(f)
        if time.time() - entry.get("cached_at", 0) < ttl_seconds:
            return entry.get("data")
    except Exception:
        pass
    return None


def _cache_set(key: str, data: Any):
    _ensure_dirs()
    p = _cache_path(key)
    with open(p, "w") as f:
        json.dump({"cached_at": time.time(), "data": data}, f)


# ── Generic HTTP helpers ──────────────────────────────────────────────────────

def get_html(url: str, extra_headers: dict | None = None,
             timeout: int = 15, cache_ttl: int = 1800) -> BeautifulSoup:
    """Fetch URL and return a BeautifulSoup tree."""
    cached = _cache_get(url, ttl_seconds=cache_ttl)
    if cached:
        return BeautifulSoup(cached, "html.parser")

    headers = {
        "User-Agent": _random_ua(),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
    }
    if extra_headers:
        headers.update(extra_headers)

    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    _cache_set(url, resp.text)
    return BeautifulSoup(resp.text, "html.parser")


def get_json(url: str, params: dict | None = None,
             extra_headers: dict | None = None,
             timeout: int = 15, cache_ttl: int = 1800) -> Any:
    """Fetch URL and return parsed JSON."""
    cache_key = url + json.dumps(params or {}, sort_keys=True)
    cached = _cache_get(cache_key, ttl_seconds=cache_ttl)
    if cached is not None:
        return cached

    headers = {
        "User-Agent": _random_ua(),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
    }
    if extra_headers:
        headers.update(extra_headers)

    resp = requests.get(url, params=params, headers=headers, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    _cache_set(cache_key, data)
    return data


def clear_cache():
    """Delete all cached responses."""
    _ensure_dirs()
    count = 0
    for f in CACHE_DIR.glob("*.json"):
        f.unlink()
        count += 1
    return {"cleared": count}
