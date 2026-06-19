"""Shared HTTP helpers for trend scraping."""
import random
import time
import requests
from typing import Optional

_DESKTOP_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]
_MOBILE_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",
]


def make_session(mobile: bool = False) -> requests.Session:
    sess = requests.Session()
    agents = _MOBILE_AGENTS if mobile else _DESKTOP_AGENTS
    sess.headers.update({
        "User-Agent": random.choice(agents),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    return sess


def get_json(url: str, params: Optional[dict] = None, headers: Optional[dict] = None,
             mobile: bool = False, retries: int = 3, timeout: int = 15) -> dict:
    sess = make_session(mobile=mobile)
    if headers:
        sess.headers.update(headers)
    for attempt in range(retries):
        try:
            resp = sess.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            raise
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise
    raise RuntimeError(f"Failed to fetch {url} after {retries} attempts")


def get_html(url: str, params: Optional[dict] = None, mobile: bool = False,
             timeout: int = 15) -> str:
    sess = make_session(mobile=mobile)
    resp = sess.get(url, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp.text
