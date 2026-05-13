"""Config management — API keys and account settings stored in ~/.social-trends/config.json."""

import json
import os
from pathlib import Path
from typing import Optional

_CONFIG_DIR = Path.home() / ".social-trends"
_CONFIG_FILE = _CONFIG_DIR / "config.json"

_DEFAULTS = {
    "youtube_api_key": "",
    "tiktok_session_cookie": "",
    "accounts": {},
    "default_region": "US",
    "default_niche": "general",
    "default_timezone": "EST",
}


def load() -> dict:
    """Load config from disk, creating defaults if missing."""
    if not _CONFIG_FILE.exists():
        return dict(_DEFAULTS)
    try:
        with open(_CONFIG_FILE) as f:
            data = json.load(f)
        merged = {**_DEFAULTS, **data}
        return merged
    except (json.JSONDecodeError, OSError):
        return dict(_DEFAULTS)


def save(config: dict) -> None:
    """Persist config to disk."""
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    # Never write secrets to stderr/stdout — write to file only
    with open(_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    # Restrict permissions
    os.chmod(_CONFIG_FILE, 0o600)


def set_key(key: str, value: str) -> dict:
    config = load()
    config[key] = value
    save(config)
    return config


def get_key(key: str, fallback: str = "") -> str:
    config = load()
    return config.get(key, fallback)


def add_account(platform: str, handle: str, metadata: Optional[dict] = None) -> dict:
    config = load()
    if "accounts" not in config:
        config["accounts"] = {}
    if platform not in config["accounts"]:
        config["accounts"][platform] = {}
    config["accounts"][platform][handle] = metadata or {}
    save(config)
    return config


def list_accounts() -> dict:
    config = load()
    return config.get("accounts", {})


def config_path() -> str:
    return str(_CONFIG_FILE)


def mask_secrets(config: dict) -> dict:
    """Return config with sensitive values masked for display."""
    masked = dict(config)
    for key in ("youtube_api_key", "tiktok_session_cookie"):
        val = masked.get(key, "")
        if val and len(val) > 8:
            masked[key] = val[:4] + "****" + val[-4:]
        elif val:
            masked[key] = "****"
    return masked
