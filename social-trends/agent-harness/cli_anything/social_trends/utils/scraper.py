"""HTTP scraping utilities — retry logic, headers, JSON extraction."""

import json
import re
import time
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional


_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

_JSON_HEADERS = {
    **_BROWSER_HEADERS,
    "Accept": "application/json, text/plain, */*",
    "X-Requested-With": "XMLHttpRequest",
}


def fetch_html(url: str, timeout: int = 15, retries: int = 3) -> str:
    """Fetch a URL and return its body as a string, with retry."""
    last_err: Exception = RuntimeError("no attempts made")
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=_BROWSER_HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in (429, 503):
                time.sleep(2 ** attempt)
            else:
                raise
        except Exception as e:
            last_err = e
            time.sleep(2 ** attempt)
    raise RuntimeError(f"fetch_html failed after {retries} attempts: {last_err}")


def fetch_json(url: str, timeout: int = 15, retries: int = 3,
               extra_headers: Optional[Dict[str, str]] = None) -> Any:
    """Fetch a URL and parse response as JSON."""
    headers = {**_JSON_HEADERS, **(extra_headers or {})}
    last_err: Exception = RuntimeError("no attempts made")
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8", errors="replace"))
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in (429, 503):
                time.sleep(2 ** attempt)
            else:
                raise
        except Exception as e:
            last_err = e
            time.sleep(2 ** attempt)
    raise RuntimeError(f"fetch_json failed after {retries} attempts: {last_err}")


def extract_json_var(html: str, var_name: str) -> Any:
    """Extract a JS variable assignment from an HTML page and parse it as JSON.

    Handles both `var NAME = {...};` and `window.NAME = {...};` patterns.
    """
    patterns = [
        rf'(?:var\s+|window\.){re.escape(var_name)}\s*=\s*([\[{{].*?)(?:;\s*(?:var|window|</script))',
        rf'"{re.escape(var_name)}"\s*:\s*([\[{{].*?)(?:,\s*"[a-zA-Z]|}})',
    ]
    for pat in patterns:
        m = re.search(pat, html, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                continue
    return None


def extract_all_json_objects(html: str, key_hint: str) -> List[Dict]:
    """Find all JSON objects in an HTML page that contain key_hint."""
    results: List[Dict] = []
    for m in re.finditer(r'\{[^{}]{10,}\}', html, re.DOTALL):
        try:
            obj = json.loads(m.group())
            if key_hint in obj:
                results.append(obj)
        except json.JSONDecodeError:
            pass
    return results


def shorten_number(n: int) -> str:
    """Format large numbers as 1.2M, 45K etc."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)
