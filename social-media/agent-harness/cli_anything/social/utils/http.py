"""Shared HTTP client with browser-like headers and retry logic."""
import time
import random
import requests
from typing import Optional, Dict, Any

_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

_DEFAULT_HEADERS = {
    "User-Agent": _BROWSER_UA,
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def get(
    url: str,
    params: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    timeout: int = 15,
    retries: int = 3,
    backoff: float = 1.5,
) -> requests.Response:
    """GET with retries and randomised back-off."""
    h = {**_DEFAULT_HEADERS, **(headers or {})}
    last_exc: Exception = RuntimeError("no attempts made")
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, headers=h, timeout=timeout)
            resp.raise_for_status()
            return resp
        except Exception as exc:
            last_exc = exc
            if attempt < retries - 1:
                sleep = backoff * (2 ** attempt) + random.uniform(0, 0.5)
                time.sleep(sleep)
    raise last_exc


def get_json(
    url: str,
    params: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    timeout: int = 15,
    retries: int = 3,
) -> Any:
    resp = get(url, params=params, headers=headers, timeout=timeout, retries=retries)
    return resp.json()
