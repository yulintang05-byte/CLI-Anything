"""Configuration management for socialtrends."""

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "cli-anything" / "socialtrends"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(data: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    existing = load_config()
    existing.update(data)
    with open(CONFIG_FILE, "w") as f:
        json.dump(existing, f, indent=2)


def get(key: str, default=None):
    return load_config().get(key, default)
