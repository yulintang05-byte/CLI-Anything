"""Account config and persistence for SocialOptimizer."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

CONFIG_DIR = Path.home() / ".config" / "social-optimizer"
ACCOUNTS_FILE = CONFIG_DIR / "accounts.json"

SUPPORTED_PLATFORMS = {"tiktok", "youtube", "instagram", "twitter", "facebook"}


def _ensure_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_accounts() -> List[Dict[str, Any]]:
    _ensure_dir()
    if ACCOUNTS_FILE.exists():
        try:
            return json.loads(ACCOUNTS_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_accounts(accounts: List[Dict[str, Any]]) -> None:
    _ensure_dir()
    ACCOUNTS_FILE.write_text(json.dumps(accounts, indent=2))


def add_account(
    name: str,
    platform: str,
    handle: str,
    niche: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    if platform.lower() not in SUPPORTED_PLATFORMS:
        raise ValueError(f"Unsupported platform '{platform}'. Choices: {sorted(SUPPORTED_PLATFORMS)}")

    accounts = load_accounts()

    existing = next((a for a in accounts if a["handle"] == handle and a["platform"] == platform.lower()), None)
    if existing:
        raise ValueError(f"Account @{handle} on {platform} already exists.")

    account = {
        "name": name,
        "platform": platform.lower(),
        "handle": handle,
        "niche": niche or "general",
        "notes": notes or "",
        "posting_schedule": [],
        "settings": {},
    }
    accounts.append(account)
    save_accounts(accounts)
    return account


def remove_account(handle: str, platform: Optional[str] = None) -> Dict[str, Any]:
    accounts = load_accounts()
    for i, a in enumerate(accounts):
        if a["handle"] == handle and (platform is None or a["platform"] == platform.lower()):
            removed = accounts.pop(i)
            save_accounts(accounts)
            return removed
    raise ValueError(f"Account @{handle} not found.")


def get_account(handle: str, platform: Optional[str] = None) -> Dict[str, Any]:
    accounts = load_accounts()
    for a in accounts:
        if a["handle"] == handle and (platform is None or a["platform"] == platform.lower()):
            return a
    raise ValueError(f"Account @{handle} not found.")


def update_account(handle: str, platform: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    accounts = load_accounts()
    for i, a in enumerate(accounts):
        if a["handle"] == handle and a["platform"] == platform.lower():
            accounts[i].update(updates)
            save_accounts(accounts)
            return accounts[i]
    raise ValueError(f"Account @{handle} on {platform} not found.")


def list_accounts(platform: Optional[str] = None) -> List[Dict[str, Any]]:
    accounts = load_accounts()
    if platform:
        accounts = [a for a in accounts if a["platform"] == platform.lower()]
    return accounts
