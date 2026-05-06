"""Shared backend utilities — config, HTTP helpers, API key management."""

import os
import json
from pathlib import Path
from typing import Optional


CONFIG_DIR = Path.home() / ".cli-anything-social-trends"
CONFIG_FILE = CONFIG_DIR / "config.json"

PLATFORMS = ["tiktok", "instagram", "youtube", "youtube_shorts"]
SUPPORTED_REGIONS = [
    "US", "GB", "CA", "AU", "IN", "DE", "FR", "BR", "MX", "JP",
    "KR", "SG", "NG", "ZA", "AE", "ID", "PH", "VN", "TH", "IT",
]


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


def get_youtube_api_key(cli_opt: Optional[str] = None) -> Optional[str]:
    """Resolve YouTube API key from CLI opt → env → config."""
    if cli_opt:
        return cli_opt
    env = os.environ.get("YOUTUBE_API_KEY") or os.environ.get("YT_API_KEY")
    if env:
        return env
    cfg = load_config()
    return cfg.get("youtube_api_key")


def get_region(cli_opt: Optional[str] = None) -> str:
    """Resolve region from CLI opt → env → config → default US."""
    if cli_opt and cli_opt.upper() in SUPPORTED_REGIONS:
        return cli_opt.upper()
    env = os.environ.get("SOCIAL_TRENDS_REGION")
    if env and env.upper() in SUPPORTED_REGIONS:
        return env.upper()
    cfg = load_config()
    return cfg.get("region", "US")


def validate_platform(platform: str) -> str:
    p = platform.lower()
    if p not in PLATFORMS:
        raise ValueError(f"Unknown platform '{platform}'. Valid: {', '.join(PLATFORMS)}")
    return p
