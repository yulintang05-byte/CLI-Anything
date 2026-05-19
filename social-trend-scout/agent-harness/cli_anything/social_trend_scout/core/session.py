import json
import os
from datetime import datetime
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "social-trend-scout"


class Session:
    """Persistent session state: API keys, cached trends, preferences."""

    def __init__(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self._config_path = CONFIG_DIR / "config.json"
        self._cache_path = CONFIG_DIR / "trend_cache.json"
        self._config = self._load(self._config_path)
        self._cache = self._load(self._cache_path)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self, path: Path) -> dict:
        if path.exists():
            try:
                return json.loads(path.read_text())
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_config(self):
        self._config_path.write_text(json.dumps(self._config, indent=2))

    def _save_cache(self):
        self._cache_path.write_text(json.dumps(self._cache, indent=2))

    # ------------------------------------------------------------------
    # API key management
    # ------------------------------------------------------------------

    def set_api_key(self, platform: str, key: str):
        self._config.setdefault("api_keys", {})[platform] = key
        self._save_config()

    def get_api_key(self, platform: str) -> str | None:
        return self._config.get("api_keys", {}).get(platform)

    # ------------------------------------------------------------------
    # Preferences
    # ------------------------------------------------------------------

    def set_preference(self, key: str, value):
        self._config.setdefault("preferences", {})[key] = value
        self._save_config()

    def get_preference(self, key: str, default=None):
        return self._config.get("preferences", {}).get(key, default)

    # ------------------------------------------------------------------
    # Trend cache (TTL = 1 hour by default)
    # ------------------------------------------------------------------

    def cache_trends(self, platform: str, data: dict, ttl_seconds: int = 3600):
        self._cache[platform] = {
            "data": data,
            "cached_at": datetime.utcnow().isoformat(),
            "ttl": ttl_seconds,
        }
        self._save_cache()

    def get_cached_trends(self, platform: str) -> dict | None:
        entry = self._cache.get(platform)
        if not entry:
            return None
        cached_at = datetime.fromisoformat(entry["cached_at"])
        age = (datetime.utcnow() - cached_at).total_seconds()
        if age > entry["ttl"]:
            return None
        return entry["data"]

    def clear_cache(self, platform: str | None = None):
        if platform:
            self._cache.pop(platform, None)
        else:
            self._cache = {}
        self._save_cache()

    # ------------------------------------------------------------------
    # Account registry
    # ------------------------------------------------------------------

    def register_account(self, platform: str, handle: str, niche: str):
        self._config.setdefault("accounts", {}).setdefault(platform, [])
        accounts = self._config["accounts"][platform]
        if not any(a["handle"] == handle for a in accounts):
            accounts.append({"handle": handle, "niche": niche, "added": datetime.utcnow().isoformat()})
        self._save_config()

    def list_accounts(self, platform: str | None = None) -> dict:
        accounts = self._config.get("accounts", {})
        if platform:
            return {platform: accounts.get(platform, [])}
        return accounts

    def remove_account(self, platform: str, handle: str):
        accts = self._config.get("accounts", {}).get(platform, [])
        self._config["accounts"][platform] = [a for a in accts if a["handle"] != handle]
        self._save_config()

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self) -> dict:
        api_keys = {k: "set" for k in self._config.get("api_keys", {})}
        accounts = {p: len(v) for p, v in self._config.get("accounts", {}).items()}
        cached = list(self._cache.keys())
        return {"api_keys": api_keys, "accounts": accounts, "cached_platforms": cached}
