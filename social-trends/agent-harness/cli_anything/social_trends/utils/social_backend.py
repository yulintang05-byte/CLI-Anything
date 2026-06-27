"""HTTP backend utilities: rate-limited fetching, caching, user-agent rotation."""

import json
import os
import time
import hashlib
import urllib.request
import urllib.error
import urllib.parse
from typing import Any, Dict, Optional


_CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "cli-social-trends")
_CACHE_TTL = 3600  # 1 hour

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
]
_ua_index = 0


def _next_ua() -> str:
    global _ua_index
    ua = _USER_AGENTS[_ua_index % len(_USER_AGENTS)]
    _ua_index += 1
    return ua


def _cache_path(url: str) -> str:
    os.makedirs(_CACHE_DIR, exist_ok=True)
    key = hashlib.sha256(url.encode()).hexdigest()[:16]
    return os.path.join(_CACHE_DIR, f"{key}.json")


def _read_cache(url: str) -> Optional[Any]:
    path = _cache_path(url)
    if not os.path.exists(path):
        return None
    if time.time() - os.path.getmtime(path) > _CACHE_TTL:
        return None
    with open(path) as f:
        return json.load(f)


def _write_cache(url: str, data: Any) -> None:
    with open(_cache_path(url), "w") as f:
        json.dump(data, f)


def fetch_json(url: str, headers: Optional[Dict[str, str]] = None, use_cache: bool = True) -> Any:
    """Fetch URL and parse as JSON, with disk caching."""
    if use_cache:
        cached = _read_cache(url)
        if cached is not None:
            return cached

    req_headers = {"User-Agent": _next_ua(), "Accept": "application/json"}
    if headers:
        req_headers.update(headers)

    req = urllib.request.Request(url, headers=req_headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8")
            data = json.loads(raw)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} fetching {url}: {e.reason}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error fetching {url}: {e.reason}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"JSON parse error for {url}: {e}")

    if use_cache:
        _write_cache(url, data)
    return data


def fetch_text(url: str, headers: Optional[Dict[str, str]] = None) -> str:
    """Fetch URL as raw text (no caching)."""
    req_headers = {"User-Agent": _next_ua(), "Accept": "text/html,application/xhtml+xml,*/*"}
    if headers:
        req_headers.update(headers)

    req = urllib.request.Request(url, headers=req_headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} fetching {url}: {e.reason}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error fetching {url}: {e.reason}")


def clear_cache() -> int:
    """Delete all cached responses, return count of files removed."""
    if not os.path.exists(_CACHE_DIR):
        return 0
    removed = 0
    for fname in os.listdir(_CACHE_DIR):
        if fname.endswith(".json"):
            os.remove(os.path.join(_CACHE_DIR, fname))
            removed += 1
    return removed


def set_cache_ttl(seconds: int) -> None:
    global _CACHE_TTL
    _CACHE_TTL = seconds
