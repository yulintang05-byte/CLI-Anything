"""Shared config management for cli-anything-trends."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".config" / "cli-anything-trends"
CONFIG_FILE = CONFIG_DIR / "config.json"

ENV_YOUTUBE_KEY = "YOUTUBE_API_KEY"
ENV_TIKTOK_KEY = "TIKTOK_RESEARCH_API_KEY"


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)
    CONFIG_FILE.chmod(0o600)


def get_youtube_api_key(cli_key: Optional[str] = None) -> str:
    """Resolve YouTube API key: CLI arg → env var → config file."""
    if cli_key:
        return cli_key
    key = os.environ.get(ENV_YOUTUBE_KEY)
    if key:
        return key
    cfg = load_config()
    key = cfg.get("youtube_api_key")
    if key:
        return key
    raise ValueError(
        "YouTube API key not found.\n"
        "  Option 1: export YOUTUBE_API_KEY=<key>\n"
        "  Option 2: cli-anything-trends config set youtube_api_key <key>\n"
        "  Get a free key at: https://console.cloud.google.com → YouTube Data API v3"
    )


def get_tiktok_api_key(cli_key: Optional[str] = None) -> Optional[str]:
    """Resolve TikTok Research API key (optional — falls back to scraping)."""
    if cli_key:
        return cli_key
    key = os.environ.get(ENV_TIKTOK_KEY)
    if key:
        return key
    cfg = load_config()
    return cfg.get("tiktok_api_key")


def get_tiktok_cookies(cookie_str: Optional[str] = None) -> dict:
    """Resolve TikTok session cookies for unofficial API access."""
    if cookie_str:
        return _parse_cookie_string(cookie_str)
    cfg = load_config()
    raw = cfg.get("tiktok_cookies", "")
    if raw:
        return _parse_cookie_string(raw) if isinstance(raw, str) else raw
    return {}


def _parse_cookie_string(cookie_str: str) -> dict:
    """Parse 'key=val; key2=val2' format cookie string."""
    cookies = {}
    for part in cookie_str.split(";"):
        part = part.strip()
        if "=" in part:
            k, _, v = part.partition("=")
            cookies[k.strip()] = v.strip()
    return cookies
