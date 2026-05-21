"""Config and credential management for social-media CLI."""

import os
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".cli-anything-social-media"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULTS = {
    "youtube_api_key": "",
    "tiktok_session_id": "",
    "accounts": [],
}


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return dict(DEFAULTS)
    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)
    return {**DEFAULTS, **data}


def save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


def get_youtube_api_key() -> str:
    key = os.environ.get("YOUTUBE_API_KEY", "")
    if not key:
        key = load_config().get("youtube_api_key", "")
    return key


def get_tiktok_session_id() -> str:
    sid = os.environ.get("TIKTOK_SESSION_ID", "")
    if not sid:
        sid = load_config().get("tiktok_session_id", "")
    return sid
