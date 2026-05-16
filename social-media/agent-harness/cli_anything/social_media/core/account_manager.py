"""Account manager: store and manage multiple social media accounts."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


CONFIG_DIR = Path.home() / ".cli-anything" / "social-media"
ACCOUNTS_FILE = CONFIG_DIR / "accounts.json"


def _load_accounts() -> dict:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if ACCOUNTS_FILE.exists():
        with open(ACCOUNTS_FILE) as f:
            return json.load(f)
    return {"accounts": {}}


def _save_accounts(data: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_account(
    handle: str,
    platform: str,
    niche: str = "",
    bio: str = "",
    followers: int = 0,
    notes: str = "",
) -> dict:
    """Register a social account for tracking."""
    data = _load_accounts()
    key = f"{platform}:{handle}"
    data["accounts"][key] = {
        "handle": handle,
        "platform": platform,
        "niche": niche,
        "bio": bio,
        "followers": followers,
        "notes": notes,
        "added_at": datetime.utcnow().isoformat() + "Z",
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "metrics_history": [],
    }
    _save_accounts(data)
    return {"status": "added", "key": key, "account": data["accounts"][key]}


def update_metrics(handle: str, platform: str, followers: int = None,
                   avg_views: int = None, avg_likes: int = None) -> dict:
    """Log a metrics snapshot for an account."""
    data = _load_accounts()
    key = f"{platform}:{handle}"
    if key not in data["accounts"]:
        return {"error": f"Account {key} not found. Run 'account add' first."}
    acct = data["accounts"][key]
    snapshot = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "followers": followers or acct.get("followers", 0),
        "avg_views": avg_views,
        "avg_likes": avg_likes,
    }
    acct["metrics_history"].append(snapshot)
    if followers:
        acct["followers"] = followers
    acct["last_updated"] = datetime.utcnow().isoformat() + "Z"
    _save_accounts(data)
    return {"status": "updated", "snapshot": snapshot}


def list_accounts() -> dict:
    """List all registered accounts."""
    data = _load_accounts()
    accounts = []
    for key, acct in data["accounts"].items():
        # Compute follower growth if history exists
        hist = acct.get("metrics_history", [])
        growth = None
        if len(hist) >= 2:
            growth = hist[-1].get("followers", 0) - hist[0].get("followers", 0)
        accounts.append({
            "key": key,
            "handle": acct["handle"],
            "platform": acct["platform"],
            "niche": acct.get("niche", ""),
            "followers": acct.get("followers", 0),
            "follower_growth_total": growth,
            "last_updated": acct.get("last_updated", ""),
        })
    return {
        "total_accounts": len(accounts),
        "accounts": sorted(accounts, key=lambda x: x["followers"], reverse=True),
    }


def remove_account(handle: str, platform: str) -> dict:
    """Remove an account from tracking."""
    data = _load_accounts()
    key = f"{platform}:{handle}"
    if key not in data["accounts"]:
        return {"error": f"Account {key} not found."}
    removed = data["accounts"].pop(key)
    _save_accounts(data)
    return {"status": "removed", "account": removed}


def get_account(handle: str, platform: str) -> dict:
    """Get full account details."""
    data = _load_accounts()
    key = f"{platform}:{handle}"
    if key not in data["accounts"]:
        return {"error": f"Account {key} not found."}
    return data["accounts"][key]
