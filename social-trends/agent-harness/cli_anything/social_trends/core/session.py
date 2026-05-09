"""Session state for social-trends CLI."""
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Session:
    config_path: Path = field(default_factory=lambda: Path.home() / ".social_trends_config.json")
    _data: dict = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        self._load()

    def _load(self) -> None:
        if self.config_path.exists():
            try:
                self._data = json.loads(self.config_path.read_text())
            except (json.JSONDecodeError, OSError):
                self._data = {}

    def _save(self) -> None:
        try:
            self.config_path.write_text(json.dumps(self._data, indent=2))
        except OSError:
            pass

    # ── Accounts ─────────────────────────────────────────────────────────────

    def add_account(self, platform: str, handle: str, niche: str = "general") -> dict:
        accounts = self._data.setdefault("accounts", {})
        clean_handle = handle.lstrip("@")
        key = f"{platform}:{clean_handle}"
        accounts[key] = {
            "platform": platform.lower(),
            "handle": clean_handle,
            "niche": niche.lower(),
            "added_at": _now_iso(),
            "optimizations": [],
        }
        self._save()
        return accounts[key]

    def remove_account(self, platform: str, handle: str) -> bool:
        key = f"{platform}:{handle.lstrip('@')}"
        if key in self._data.get("accounts", {}):
            del self._data["accounts"][key]
            self._save()
            return True
        return False

    def list_accounts(self) -> list[dict]:
        return [{"key": k, **v} for k, v in self._data.get("accounts", {}).items()]

    def get_account(self, platform: str, handle: str) -> dict | None:
        key = f"{platform}:{handle.lstrip('@')}"
        return self._data.get("accounts", {}).get(key)

    # ── Config ────────────────────────────────────────────────────────────────

    def set_config(self, key: str, value: Any) -> None:
        self._data.setdefault("config", {})[key] = value
        self._save()

    def get_config(self, key: str, default: Any = None) -> Any:
        return self._data.get("config", {}).get(key, default)

    def get_all_config(self) -> dict:
        return self._data.get("config", {})

    # ── Saved trends ─────────────────────────────────────────────────────────

    def save_trend_snapshot(self, platform: str, niche: str, data: dict) -> None:
        snapshots = self._data.setdefault("trend_snapshots", [])
        snapshots.insert(0, {
            "platform": platform,
            "niche": niche,
            "fetched_at": _now_iso(),
            "data": data,
        })
        # Keep last 20 snapshots
        self._data["trend_snapshots"] = snapshots[:20]
        self._save()

    def get_latest_snapshot(self, platform: str, niche: str) -> dict | None:
        for s in self._data.get("trend_snapshots", []):
            if s["platform"] == platform and s["niche"] == niche:
                return s
        return None

    def to_dict(self) -> dict:
        return dict(self._data)


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
