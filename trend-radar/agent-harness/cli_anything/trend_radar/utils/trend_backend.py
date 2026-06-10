"""Trend Backend — HTTP client with retry, caching, and rate limiting for trend APIs."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    raise ImportError("requests library required. Install with: pip install requests")

CACHE_DIR = Path.home() / ".cli-anything-trend-radar" / "cache"
DEFAULT_CACHE_TTL = 900  # 15 minutes


class TrendBackend:
    """HTTP backend with retry logic and short-TTL caching for trend data."""

    def __init__(self, cache_ttl: int = DEFAULT_CACHE_TTL):
        self._ttl = cache_ttl
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self._session = self._build_session()

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: int = 15,
    ) -> dict:
        """GET with caching. Cache key = URL + sorted params. Returns parsed JSON."""
        cache_key = self._cache_key(url, params or {})
        cached = self._load_cache(cache_key)
        if cached is not None:
            return cached

        resp = self._session.get(url, params=params, headers=headers, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()

        self._save_cache(cache_key, data)
        return data

    def _cache_key(self, url: str, params: dict) -> str:
        raw = url + json.dumps(sorted(params.items()), sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def _cache_path(self, key: str) -> Path:
        return CACHE_DIR / f"{key}.json"

    def _load_cache(self, key: str) -> dict | None:
        path = self._cache_path(key)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text())
            if time.time() - data.get("_ts", 0) < self._ttl:
                return data.get("_data")
        except (json.JSONDecodeError, KeyError, OSError):
            pass
        return None

    def _save_cache(self, key: str, data: dict):
        path = self._cache_path(key)
        try:
            path.write_text(json.dumps({"_ts": time.time(), "_data": data}))
        except OSError:
            pass  # Cache write failure is non-fatal
