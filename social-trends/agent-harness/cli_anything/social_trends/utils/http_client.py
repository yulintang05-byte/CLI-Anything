"""Rate-limited HTTP client with browser-realistic headers for social scraping."""

import time
import random
import requests
from typing import Optional, Dict, Any


_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
]

_last_request_time: float = 0.0
_min_delay: float = 1.2  # seconds between requests


def get_session(extra_headers: Optional[Dict[str, str]] = None) -> requests.Session:
    """Return a session with realistic browser headers."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": random.choice(_USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    })
    if extra_headers:
        session.headers.update(extra_headers)
    return session


def rate_limited_get(
    url: str,
    session: Optional[requests.Session] = None,
    params: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    timeout: int = 15,
    jitter: float = 0.5,
) -> requests.Response:
    """GET with automatic rate limiting to avoid bot detection."""
    global _last_request_time

    elapsed = time.monotonic() - _last_request_time
    wait = _min_delay - elapsed + random.uniform(0, jitter)
    if wait > 0:
        time.sleep(wait)

    s = session or get_session()
    if headers:
        s.headers.update(headers)

    resp = s.get(url, params=params, timeout=timeout)
    _last_request_time = time.monotonic()
    return resp


def safe_json(resp: requests.Response) -> Any:
    """Parse JSON from response, returning {} on failure."""
    try:
        return resp.json()
    except Exception:
        return {}
