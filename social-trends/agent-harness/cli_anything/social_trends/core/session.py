"""Session state — persists config, cached trends, and account profiles."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


_CONFIG_DIR = Path.home() / ".cli-anything-social-trends"


class Session:
    """Persistent session for social trends CLI."""

    def __init__(self):
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self._config_path = _CONFIG_DIR / "config.json"
        self._cache_path = _CONFIG_DIR / "trends_cache.json"
        self._accounts_path = _CONFIG_DIR / "accounts.json"
        self.config: dict = self._load(_CONFIG_DIR / "config.json", default={})
        self.cache: dict = self._load(_CONFIG_DIR / "trends_cache.json", default={})
        self.accounts: dict = self._load(_CONFIG_DIR / "accounts.json", default={})

    # ── I/O helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _load(path: Path, default: Any) -> Any:
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return default

    def _save(self, path: Path, data: Any) -> None:
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def save_config(self) -> None:
        self._save(self._config_path, self.config)

    def save_cache(self) -> None:
        self._save(self._cache_path, self.cache)

    def save_accounts(self) -> None:
        self._save(self._accounts_path, self.accounts)

    # ── Config helpers ────────────────────────────────────────────────────────

    def set_api_key(self, platform: str, key: str) -> None:
        self.config.setdefault("api_keys", {})[platform] = key
        self.save_config()

    def get_api_key(self, platform: str) -> Optional[str]:
        return self.config.get("api_keys", {}).get(platform)

    def set_region(self, region: str) -> None:
        self.config["region"] = region.upper()
        self.save_config()

    def get_region(self) -> str:
        return self.config.get("region", "US")

    # ── Cache helpers ─────────────────────────────────────────────────────────

    def cache_trends(self, platform: str, data: list, ttl_minutes: int = 30) -> None:
        self.cache[platform] = {
            "data": data,
            "fetched_at": datetime.utcnow().isoformat(),
            "ttl_minutes": ttl_minutes,
        }
        self.save_cache()

    def get_cached_trends(self, platform: str) -> Optional[list]:
        entry = self.cache.get(platform)
        if not entry:
            return None
        fetched_at = datetime.fromisoformat(entry["fetched_at"])
        age_minutes = (datetime.utcnow() - fetched_at).total_seconds() / 60
        if age_minutes > entry.get("ttl_minutes", 30):
            return None
        return entry["data"]

    # ── Account helpers ───────────────────────────────────────────────────────

    def add_account(self, platform: str, handle: str, meta: dict) -> None:
        self.accounts.setdefault(platform, {})[handle] = {
            **meta,
            "added_at": datetime.utcnow().isoformat(),
        }
        self.save_accounts()

    def list_accounts(self) -> dict:
        return self.accounts

    def get_account(self, platform: str, handle: str) -> Optional[dict]:
        return self.accounts.get(platform, {}).get(handle)

    def remove_account(self, platform: str, handle: str) -> bool:
        removed = self.accounts.get(platform, {}).pop(handle, None)
        if removed is not None:
            self.save_accounts()
        return removed is not None

    # ── Summary ───────────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        account_count = sum(len(v) for v in self.accounts.values())
        cached_platforms = list(self.cache.keys())
        return {
            "config_dir": str(_CONFIG_DIR),
            "region": self.get_region(),
            "youtube_api_key_set": bool(self.get_api_key("youtube")),
            "accounts_tracked": account_count,
            "cached_platforms": cached_platforms,
        }
