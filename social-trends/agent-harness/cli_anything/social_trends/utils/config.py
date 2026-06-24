#!/usr/bin/env python3
"""Config management for social-trends CLI — API keys, preferences, account profiles."""

import json
import os
from pathlib import Path
from typing import Any, Optional


CONFIG_DIR = Path.home() / ".cli-anything-social"
CONFIG_FILE = CONFIG_DIR / "config.json"
ACCOUNTS_FILE = CONFIG_DIR / "accounts.json"


def _ensure_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    _ensure_dir()
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def save_config(cfg: dict):
    _ensure_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


def get(key: str, default: Any = None) -> Any:
    return load_config().get(key, default)


def set_value(key: str, value: Any):
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)


def get_youtube_api_key() -> Optional[str]:
    return get("youtube_api_key") or os.environ.get("YOUTUBE_API_KEY")


def get_tiktok_session_id() -> Optional[str]:
    return get("tiktok_session_id") or os.environ.get("TIKTOK_SESSION_ID")


def load_accounts() -> list[dict]:
    _ensure_dir()
    if ACCOUNTS_FILE.exists():
        with open(ACCOUNTS_FILE) as f:
            return json.load(f)
    return []


def save_accounts(accounts: list[dict]):
    _ensure_dir()
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f, indent=2)


def add_account(platform: str, handle: str, niche: str, goal: str = "growth"):
    accounts = load_accounts()
    for acc in accounts:
        if acc["platform"] == platform and acc["handle"] == handle:
            acc.update({"niche": niche, "goal": goal})
            save_accounts(accounts)
            return acc
    new_acc = {
        "id": f"{platform}:{handle}",
        "platform": platform,
        "handle": handle,
        "niche": niche,
        "goal": goal,
    }
    accounts.append(new_acc)
    save_accounts(accounts)
    return new_acc


def remove_account(platform: str, handle: str) -> bool:
    accounts = load_accounts()
    before = len(accounts)
    accounts = [a for a in accounts if not (a["platform"] == platform and a["handle"] == handle)]
    save_accounts(accounts)
    return len(accounts) < before
