"""Config management — stores API keys and account metadata locally."""

import json
import os
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".config" / "cli-anything-social-trends"
CONFIG_FILE = CONFIG_DIR / "config.json"
ACCOUNTS_FILE = CONFIG_DIR / "accounts.json"


def _ensure_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    _ensure_dir()
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}


def save_config(data: dict):
    _ensure_dir()
    CONFIG_FILE.write_text(json.dumps(data, indent=2))
    CONFIG_FILE.chmod(0o600)


def get_youtube_api_key() -> Optional[str]:
    return (
        os.environ.get("YOUTUBE_API_KEY")
        or load_config().get("youtube_api_key")
    )


def set_youtube_api_key(key: str):
    cfg = load_config()
    cfg["youtube_api_key"] = key
    save_config(cfg)


def get_tiktok_ms_token() -> Optional[str]:
    """Optional TikTok msToken cookie for higher-rate scraping."""
    return (
        os.environ.get("TIKTOK_MS_TOKEN")
        or load_config().get("tiktok_ms_token")
    )


def set_tiktok_ms_token(token: str):
    cfg = load_config()
    cfg["tiktok_ms_token"] = token
    save_config(cfg)


def load_accounts() -> list:
    _ensure_dir()
    if ACCOUNTS_FILE.exists():
        return json.loads(ACCOUNTS_FILE.read_text())
    return []


def save_accounts(accounts: list):
    _ensure_dir()
    ACCOUNTS_FILE.write_text(json.dumps(accounts, indent=2))


def add_account(platform: str, handle: str, niche: str = "", goals: list = None):
    accounts = load_accounts()
    entry = {
        "platform": platform.lower(),
        "handle": handle.lstrip("@"),
        "niche": niche,
        "goals": goals or [],
    }
    # deduplicate by platform+handle
    accounts = [a for a in accounts if not (a["platform"] == entry["platform"] and a["handle"] == entry["handle"])]
    accounts.append(entry)
    save_accounts(accounts)
    return entry


def remove_account(platform: str, handle: str) -> bool:
    accounts = load_accounts()
    before = len(accounts)
    accounts = [a for a in accounts if not (a["platform"] == platform.lower() and a["handle"] == handle.lstrip("@"))]
    save_accounts(accounts)
    return len(accounts) < before
