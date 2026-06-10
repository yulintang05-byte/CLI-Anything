"""HTTP utilities for TrendHunter scrapers — rate limiting, retries, session management."""

import time
import random
import requests
from typing import Optional


# Rotate user agents to reduce blocking
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
]


def make_session(mobile: bool = False) -> requests.Session:
    """Create a configured requests session with realistic headers."""
    session = requests.Session()
    ua = random.choice(_USER_AGENTS)
    if mobile:
        ua = next(a for a in _USER_AGENTS if "Mobile" in a or "iPhone" in a)
    session.headers.update({
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    })
    return session


def fetch(url: str, session: Optional[requests.Session] = None,
          params: Optional[dict] = None, headers: Optional[dict] = None,
          retries: int = 3, backoff: float = 1.5,
          timeout: int = 15) -> Optional[requests.Response]:
    """Fetch a URL with retries and exponential backoff."""
    s = session or make_session()
    for attempt in range(retries):
        try:
            resp = s.get(url, params=params, headers=headers, timeout=timeout)
            if resp.status_code == 429:
                wait = backoff * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp
        except requests.RequestException:
            if attempt < retries - 1:
                time.sleep(backoff * (attempt + 1))
    return None


def fetch_json(url: str, session: Optional[requests.Session] = None,
               params: Optional[dict] = None, headers: Optional[dict] = None,
               retries: int = 3) -> Optional[dict]:
    """Fetch JSON from a URL, returning parsed dict or None."""
    s = session or make_session()
    if headers is None:
        headers = {}
    headers.setdefault("Accept", "application/json")
    resp = fetch(url, session=s, params=params, headers=headers, retries=retries)
    if resp is None:
        return None
    try:
        return resp.json()
    except Exception:
        return None


def polite_delay(min_s: float = 0.5, max_s: float = 1.5):
    """Sleep a random polite interval between requests."""
    time.sleep(random.uniform(min_s, max_s))
