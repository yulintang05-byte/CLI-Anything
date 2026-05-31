"""Shared config/storage utilities for social-intel."""

import json
import os
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".cli-anything" / "social-intel"


def _ensure_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    _ensure_dir()
    path = CONFIG_DIR / "config.json"
    if path.exists():
        return json.loads(path.read_text())
    return {}


def save_config(data: dict) -> None:
    _ensure_dir()
    path = CONFIG_DIR / "config.json"
    path.write_text(json.dumps(data, indent=2))


def load_cache(name: str) -> dict:
    _ensure_dir()
    path = CONFIG_DIR / f"{name}.cache.json"
    if path.exists():
        return json.loads(path.read_text())
    return {}


def save_cache(name: str, data: Any) -> None:
    _ensure_dir()
    path = CONFIG_DIR / f"{name}.cache.json"
    path.write_text(json.dumps(data, indent=2, default=str))


def get_api_key(platform: str) -> str:
    config = load_config()
    key = config.get(f"{platform}_api_key", "") or os.environ.get(
        f"{platform.upper()}_API_KEY", ""
    )
    return key
