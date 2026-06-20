"""Config storage for social-trends CLI."""

from __future__ import annotations

import json
import os
from pathlib import Path

_CONFIG_DIR = Path.home() / ".cli-anything-social-trends"
_CONFIG_FILE = _CONFIG_DIR / "config.json"


def _load() -> dict:
    if _CONFIG_FILE.exists():
        try:
            return json.loads(_CONFIG_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save(data: dict) -> None:
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _CONFIG_FILE.write_text(json.dumps(data, indent=2))
    _CONFIG_FILE.chmod(0o600)


def get(key: str, default=None):
    return _load().get(key, default)


def set_key(key: str, value) -> None:
    data = _load()
    data[key] = value
    _save(data)


def get_api_key(platform: str) -> str:
    env_map = {
        "youtube": "YOUTUBE_API_KEY",
    }
    env_key = env_map.get(platform.lower())
    if env_key:
        val = os.environ.get(env_key, "")
        if val:
            return val
    return _load().get(f"api_key_{platform.lower()}", "")


def set_api_key(platform: str, key: str) -> None:
    set_key(f"api_key_{platform.lower()}", key)


def get_accounts() -> list[dict]:
    return _load().get("accounts", [])


def add_account(name: str, platform: str, niche: str, handle: str = "") -> dict:
    data = _load()
    accounts = data.get("accounts", [])
    account = {
        "name": name,
        "platform": platform.lower(),
        "niche": niche,
        "handle": handle,
        "added": __import__("datetime").datetime.utcnow().isoformat() + "Z",
    }
    # update if exists
    for i, a in enumerate(accounts):
        if a.get("name") == name and a.get("platform") == platform.lower():
            accounts[i] = account
            data["accounts"] = accounts
            _save(data)
            return account
    accounts.append(account)
    data["accounts"] = accounts
    _save(data)
    return account


def remove_account(name: str, platform: str) -> bool:
    data = _load()
    accounts = data.get("accounts", [])
    before = len(accounts)
    accounts = [a for a in accounts
                if not (a.get("name") == name and a.get("platform") == platform.lower())]
    data["accounts"] = accounts
    _save(data)
    return len(accounts) < before
