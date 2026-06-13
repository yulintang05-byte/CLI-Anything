"""HTTP scraping utilities with browser-like headers and rate limiting."""
import time
import random
import requests
from typing import Optional, Dict, Any

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.google.com/",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

TIKTOK_HEADERS = {
    **BROWSER_HEADERS,
    "Referer": "https://www.tiktok.com/",
    "Accept": "application/json, text/plain, */*",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


class RateLimitedSession:
    """requests.Session with configurable rate limiting between requests."""

    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0):
        self.session = requests.Session()
        self.session.headers.update(BROWSER_HEADERS)
        self.min_delay = min_delay
        self.max_delay = max_delay
        self._last_request = 0.0

    def _wait(self):
        elapsed = time.time() - self._last_request
        delay = random.uniform(self.min_delay, self.max_delay)
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_request = time.time()

    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 15,
    ) -> requests.Response:
        self._wait()
        merged = dict(self.session.headers)
        if headers:
            merged.update(headers)
        return self.session.get(url, headers=merged, params=params, timeout=timeout)

    def get_json(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 15,
    ) -> Optional[Dict]:
        try:
            resp = self.get(url, headers=headers, params=params, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None
