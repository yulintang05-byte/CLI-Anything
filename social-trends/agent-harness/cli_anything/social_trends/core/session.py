"""Session state persistence for social-trends CLI."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


SESSION_DIR = Path.home() / ".cli-anything" / "social-trends"
SESSION_FILE = SESSION_DIR / "session.json"
CACHE_DIR = SESSION_DIR / "cache"


def _ensure_dirs() -> None:
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def load_session() -> dict:
    _ensure_dirs()
    if SESSION_FILE.exists():
        try:
            with open(SESSION_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "created_at": datetime.utcnow().isoformat(),
        "accounts": {},
        "api_keys": {},
        "last_fetched": {},
        "active_niche": None,
        "active_platform": None,
        "history": [],
    }


def save_session(session: dict) -> None:
    _ensure_dirs()
    session["updated_at"] = datetime.utcnow().isoformat()
    with open(SESSION_FILE, "w") as f:
        json.dump(session, f, indent=2)


def get_api_key(session: dict, key_name: str) -> Optional[str]:
    return (
        session.get("api_keys", {}).get(key_name)
        or os.environ.get(key_name.upper())
        or os.environ.get(key_name)
    )


def set_api_key(session: dict, key_name: str, value: str) -> None:
    session.setdefault("api_keys", {})[key_name] = value


def add_account(session: dict, platform: str, username: str, data: dict) -> None:
    session.setdefault("accounts", {}).setdefault(platform, {})[username] = {
        **data,
        "added_at": datetime.utcnow().isoformat(),
    }


def get_accounts(session: dict, platform: Optional[str] = None) -> dict:
    accounts = session.get("accounts", {})
    if platform:
        return accounts.get(platform.lower(), {})
    return accounts


def cache_set(key: str, data: Any, ttl_seconds: int = 3600) -> None:
    _ensure_dirs()
    cache_path = CACHE_DIR / f"{key}.json"
    with open(cache_path, "w") as f:
        json.dump({
            "data": data,
            "expires_at": (datetime.utcnow().timestamp() + ttl_seconds),
        }, f)


def cache_get(key: str) -> Optional[Any]:
    _ensure_dirs()
    cache_path = CACHE_DIR / f"{key}.json"
    if not cache_path.exists():
        return None
    try:
        with open(cache_path) as f:
            entry = json.load(f)
        if datetime.utcnow().timestamp() < entry.get("expires_at", 0):
            return entry["data"]
        cache_path.unlink(missing_ok=True)
    except (json.JSONDecodeError, OSError, KeyError):
        pass
    return None


def cache_clear(key: Optional[str] = None) -> int:
    _ensure_dirs()
    if key:
        p = CACHE_DIR / f"{key}.json"
        if p.exists():
            p.unlink()
            return 1
        return 0
    count = 0
    for f in CACHE_DIR.glob("*.json"):
        f.unlink()
        count += 1
    return count


def log_history(session: dict, command: str, result_summary: str) -> None:
    session.setdefault("history", []).append({
        "command": command,
        "result": result_summary[:200],
        "timestamp": datetime.utcnow().isoformat(),
    })
    session["history"] = session["history"][-100:]
