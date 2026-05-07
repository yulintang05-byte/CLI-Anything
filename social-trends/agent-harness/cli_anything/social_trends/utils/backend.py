"""Config and credential management for social-trends CLI."""

import json
import os
from pathlib import Path
from typing import Optional


CONFIG_PATH = Path.home() / ".config" / "cli-anything" / "social_trends.json"

DEFAULT_CONFIG: dict = {
    "youtube_api_key": "",
    "rapidapi_key": "",
    "use_tiktokapi": False,
    "default_region": "US",
    "default_platform": "tiktok",
    "accounts": [],
}


def load_config() -> dict:
    """Load config from file, returning defaults for any missing keys."""
    config = DEFAULT_CONFIG.copy()
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                saved = json.load(f)
            config.update(saved)
        except (json.JSONDecodeError, OSError):
            pass

    # Environment variables override file config
    if os.environ.get("YOUTUBE_API_KEY"):
        config["youtube_api_key"] = os.environ["YOUTUBE_API_KEY"]
    if os.environ.get("RAPIDAPI_KEY"):
        config["rapidapi_key"] = os.environ["RAPIDAPI_KEY"]
    if os.environ.get("SOCIAL_TRENDS_REGION"):
        config["default_region"] = os.environ["SOCIAL_TRENDS_REGION"]

    return config


def save_config(config: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def add_account(platform: str, username: str, followers: int = 0, niche: str = "general") -> dict:
    config = load_config()
    account = {
        "platform": platform.lower(),
        "username": username,
        "followers": followers,
        "niche": niche,
        "added_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
    }
    accounts = config.get("accounts", [])
    # Update existing account or append
    existing = next((i for i, a in enumerate(accounts) if a["username"] == username and a["platform"] == platform.lower()), None)
    if existing is not None:
        accounts[existing] = account
    else:
        accounts.append(account)
    config["accounts"] = accounts
    save_config(config)
    return account


def get_accounts(platform: Optional[str] = None) -> list[dict]:
    config = load_config()
    accounts = config.get("accounts", [])
    if platform:
        accounts = [a for a in accounts if a["platform"] == platform.lower()]
    return accounts


def format_output(data: dict, json_mode: bool = False) -> str:
    """Format data as JSON or pretty human-readable text."""
    if json_mode:
        return json.dumps(data, indent=2, ensure_ascii=False)
    return _pretty_format(data)


def _pretty_format(data: dict, indent: int = 0) -> str:
    prefix = "  " * indent
    lines = []
    for k, v in data.items():
        if isinstance(v, dict):
            lines.append(f"{prefix}{k}:")
            lines.append(_pretty_format(v, indent + 1))
        elif isinstance(v, list):
            lines.append(f"{prefix}{k}:")
            for item in v:
                if isinstance(item, dict):
                    lines.append(f"{prefix}  -")
                    lines.append(_pretty_format(item, indent + 2))
                else:
                    lines.append(f"{prefix}  - {item}")
        else:
            lines.append(f"{prefix}{k}: {v}")
    return "\n".join(lines)
