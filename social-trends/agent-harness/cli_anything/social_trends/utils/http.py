"""HTTP helpers — rate-limited requests with retry logic."""

import time
import random
import requests
from typing import Any, Dict, Optional


# Browser-like headers to avoid being blocked by public endpoints
_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

_TIKTOK_HEADERS = {
    **_DEFAULT_HEADERS,
    "Referer": "https://ads.tiktok.com/",
    "Origin": "https://ads.tiktok.com",
}

_YOUTUBE_HEADERS = {
    **_DEFAULT_HEADERS,
    "Referer": "https://www.youtube.com/",
}


def get_json(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 15,
    retries: int = 3,
) -> Any:
    """GET request returning parsed JSON with retry logic."""
    merged = {**_DEFAULT_HEADERS, **(headers or {})}
    last_err = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, headers=merged, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code in (429, 503):
                wait = (2 ** attempt) + random.random()
                time.sleep(wait)
                last_err = e
            else:
                raise
        except requests.RequestException as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(1 + attempt)
    raise RuntimeError(f"HTTP GET failed after {retries} attempts: {last_err}")


def get_text(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 15,
) -> str:
    """GET request returning raw text."""
    merged = {**_DEFAULT_HEADERS, **(headers or {})}
    resp = requests.get(url, params=params, headers=merged, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def post_json(
    url: str,
    payload: Any,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 15,
) -> Any:
    """POST request with JSON body, returning parsed JSON."""
    merged = {**_DEFAULT_HEADERS, **(headers or {})}
    merged["Content-Type"] = "application/json"
    resp = requests.post(url, json=payload, headers=merged, timeout=timeout)
    resp.raise_for_status()
    return resp.json()
