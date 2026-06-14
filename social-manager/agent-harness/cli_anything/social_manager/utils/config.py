"""Config management — stores API keys and account info in ~/.cli-anything-social/"""
import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".cli-anything-social"
CONFIG_FILE = CONFIG_DIR / "config.json"
ACCOUNTS_FILE = CONFIG_DIR / "accounts.json"


def _ensure_dir():
    CONFIG_DIR.mkdir(exist_ok=True)


def load_config() -> dict:
    _ensure_dir()
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(data: dict):
    _ensure_dir()
    existing = load_config()
    existing.update(data)
    with open(CONFIG_FILE, "w") as f:
        json.dump(existing, f, indent=2)


def get(key: str, default=None):
    return load_config().get(key, default)


def load_accounts() -> list:
    _ensure_dir()
    if not ACCOUNTS_FILE.exists():
        return []
    with open(ACCOUNTS_FILE) as f:
        return json.load(f)


def save_accounts(accounts: list):
    _ensure_dir()
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f, indent=2)


def add_account(platform: str, handle: str, niche: str = "", notes: str = ""):
    accounts = load_accounts()
    entry = {
        "platform": platform.lower(),
        "handle": handle,
        "niche": niche,
        "notes": notes,
    }
    accounts = [a for a in accounts if not (a["platform"] == entry["platform"] and a["handle"] == entry["handle"])]
    accounts.append(entry)
    save_accounts(accounts)
    return entry
