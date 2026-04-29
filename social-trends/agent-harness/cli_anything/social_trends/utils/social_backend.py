"""Session state management and environment helpers for Social Trends CLI."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

_SESSION_PATH = Path.home() / ".cli-anything" / "social_trends_session.json"


class SocialSession:
    """Lightweight persistent session for tracking active niche, platform prefs, and cached data."""

    def __init__(self):
        self.data: dict[str, Any] = {
            "active_niche": None,
            "primary_platform": "tiktok",
            "accounts": {},
            "cached_trends": {},
            "config": {},
        }

    @property
    def active_niche(self) -> Optional[str]:
        return self.data.get("active_niche")

    @active_niche.setter
    def active_niche(self, value: str):
        self.data["active_niche"] = value

    @property
    def primary_platform(self) -> str:
        return self.data.get("primary_platform", "tiktok")

    @primary_platform.setter
    def primary_platform(self, value: str):
        self.data["primary_platform"] = value

    def add_account(self, platform: str, username: str, metadata: Optional[dict] = None):
        if platform not in self.data["accounts"]:
            self.data["accounts"][platform] = {}
        self.data["accounts"][platform][username] = metadata or {}

    def get_accounts(self, platform: Optional[str] = None) -> dict:
        if platform:
            return self.data["accounts"].get(platform, {})
        return self.data["accounts"]

    def cache_trends(self, key: str, data: Any):
        self.data["cached_trends"][key] = {
            "data": data,
            "cached_at": _now_iso(),
        }

    def get_cached(self, key: str, max_age_minutes: int = 60) -> Optional[Any]:
        entry = self.data["cached_trends"].get(key)
        if not entry:
            return None
        from datetime import datetime, timezone
        cached_at = datetime.fromisoformat(entry["cached_at"])
        now = datetime.now(timezone.utc)
        age = (now - cached_at).total_seconds() / 60
        if age > max_age_minutes:
            return None
        return entry["data"]

    def to_dict(self) -> dict:
        return self.data

    def from_dict(self, data: dict):
        self.data.update(data)


def load_session() -> SocialSession:
    session = SocialSession()
    if _SESSION_PATH.exists():
        try:
            with open(_SESSION_PATH) as f:
                session.from_dict(json.load(f))
        except (json.JSONDecodeError, KeyError):
            pass
    return session


def save_session(session: SocialSession):
    _SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_SESSION_PATH, "w") as f:
        json.dump(session.to_dict(), f, indent=2)


def get_env_status() -> dict:
    """Return status of all required environment variables."""
    return {
        "YOUTUBE_API_KEY": {
            "set": bool(os.environ.get("YOUTUBE_API_KEY")),
            "required_for": "YouTube trending, hashtag analysis, music trends",
            "how_to_get": "https://console.cloud.google.com/apis/library/youtube.googleapis.com",
        },
        "TIKTOK_API_KEY": {
            "set": bool(os.environ.get("TIKTOK_API_KEY")),
            "required_for": "TikTok Research API (optional — web scraping works without it)",
            "how_to_get": "https://developers.tiktok.com/products/research-api/",
        },
        "TIKTOK_API_SECRET": {
            "set": bool(os.environ.get("TIKTOK_API_SECRET")),
            "required_for": "TikTok Research API auth (pair with TIKTOK_API_KEY)",
            "how_to_get": "https://developers.tiktok.com/products/research-api/",
        },
    }


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
