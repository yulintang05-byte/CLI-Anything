"""Config management for trend-scout: API keys, accounts, and preferences."""

import os
import json
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".cli-anything-trend-scout"
CONFIG_FILE = CONFIG_DIR / "config.json"
ACCOUNTS_FILE = CONFIG_DIR / "accounts.json"


def ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    ensure_config_dir()
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_config(config: dict) -> None:
    ensure_config_dir()
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def get_api_key(key_name: str) -> str | None:
    """Get API key from environment first, then config file."""
    env_val = os.environ.get(key_name)
    if env_val:
        return env_val
    config = load_config()
    return config.get("api_keys", {}).get(key_name)


def set_api_key(key_name: str, value: str) -> None:
    config = load_config()
    if "api_keys" not in config:
        config["api_keys"] = {}
    config["api_keys"][key_name] = value
    save_config(config)


def load_accounts() -> list[dict]:
    ensure_config_dir()
    if ACCOUNTS_FILE.exists():
        try:
            data = json.loads(ACCOUNTS_FILE.read_text())
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_accounts(accounts: list[dict]) -> None:
    ensure_config_dir()
    ACCOUNTS_FILE.write_text(json.dumps(accounts, indent=2))


def add_account(platform: str, username: str, niche: str, followers: int = 0, region: str = "US") -> dict:
    accounts = load_accounts()
    account = {
        "platform": platform.lower(),
        "username": username,
        "niche": niche,
        "followers": followers,
        "region": region.upper(),
        "added_at": __import__("datetime").datetime.utcnow().isoformat(),
    }
    # Update if exists
    for i, a in enumerate(accounts):
        if a.get("platform") == platform.lower() and a.get("username") == username:
            accounts[i] = account
            save_accounts(accounts)
            return account
    accounts.append(account)
    save_accounts(accounts)
    return account


def remove_account(platform: str, username: str) -> bool:
    accounts = load_accounts()
    original_len = len(accounts)
    accounts = [a for a in accounts if not (a.get("platform") == platform.lower() and a.get("username") == username)]
    save_accounts(accounts)
    return len(accounts) < original_len


def get_api_keys_status() -> dict:
    return {
        "YOUTUBE_API_KEY": bool(get_api_key("YOUTUBE_API_KEY")),
        "TIKTOK_MS_TOKEN": bool(get_api_key("TIKTOK_MS_TOKEN")),
        "TIKTOK_SESSION_ID": bool(get_api_key("TIKTOK_SESSION_ID")),
    }
