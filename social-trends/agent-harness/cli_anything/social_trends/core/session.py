"""Session and config management for social-trends CLI."""

import os
import json
import copy
from pathlib import Path
from typing import Any, Dict, List, Optional


_CONFIG_DIR = Path.home() / ".cli-anything"
_CONFIG_FILE = _CONFIG_DIR / "social-trends.json"


def _default_config() -> Dict[str, Any]:
    return {
        "youtube_api_key": "",
        "tiktok_session_id": "",
        "default_region": "US",
        "default_language": "en",
        "accounts": [],
        "cache_ttl_minutes": 60,
    }


class Session:
    """Manages config, accounts, and undo/redo state."""

    def __init__(self, config_path: Optional[str] = None):
        self._config_path = Path(config_path) if config_path else _CONFIG_FILE
        self._config: Dict[str, Any] = _default_config()
        self._history: List[Dict[str, Any]] = []
        self._redo_stack: List[Dict[str, Any]] = []
        self._load_config()

    # ── Config ────────────────────────────────────────────────────────────────

    def _load_config(self) -> None:
        if self._config_path.exists():
            try:
                data = json.loads(self._config_path.read_text())
                self._config.update(data)
            except (json.JSONDecodeError, OSError):
                pass

    def save_config(self) -> None:
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config_path.write_text(json.dumps(self._config, indent=2))
        # Restrict permissions so API keys aren't world-readable
        self._config_path.chmod(0o600)

    def get_config(self) -> Dict[str, Any]:
        return copy.deepcopy(self._config)

    def set_config_value(self, key: str, value: Any) -> None:
        self._config[key] = value
        self.save_config()

    def get_youtube_api_key(self) -> str:
        return self._config.get("youtube_api_key", "") or os.environ.get("YOUTUBE_API_KEY", "")

    def get_tiktok_session_id(self) -> str:
        return self._config.get("tiktok_session_id", "") or os.environ.get("TIKTOK_SESSION_ID", "")

    def get_region(self) -> str:
        return self._config.get("default_region", "US")

    # ── Accounts ──────────────────────────────────────────────────────────────

    def list_accounts(self) -> List[Dict[str, Any]]:
        return copy.deepcopy(self._config.get("accounts", []))

    def add_account(self, platform: str, handle: str, notes: str = "") -> Dict[str, Any]:
        accounts = self._config.get("accounts", [])
        for acct in accounts:
            if acct["platform"] == platform and acct["handle"] == handle:
                raise ValueError(f"Account @{handle} on {platform} already exists.")
        record = {
            "id": f"{platform}_{handle}",
            "platform": platform,
            "handle": handle,
            "notes": notes,
            "added": _now_iso(),
        }
        self._snapshot()
        accounts.append(record)
        self._config["accounts"] = accounts
        self.save_config()
        return record

    def remove_account(self, account_id: str) -> Dict[str, Any]:
        accounts = self._config.get("accounts", [])
        for i, acct in enumerate(accounts):
            if acct["id"] == account_id:
                self._snapshot()
                removed = accounts.pop(i)
                self._config["accounts"] = accounts
                self.save_config()
                return removed
        available = [a["id"] for a in accounts]
        raise ValueError(f"Account '{account_id}' not found. Available: {available}")

    # ── Undo/redo ─────────────────────────────────────────────────────────────

    def _snapshot(self) -> None:
        self._history.append(copy.deepcopy(self._config))
        self._redo_stack.clear()

    def undo(self) -> Dict[str, Any]:
        if not self._history:
            raise RuntimeError("Nothing to undo.")
        self._redo_stack.append(copy.deepcopy(self._config))
        self._config = self._history.pop()
        self.save_config()
        return self.get_config()

    def redo(self) -> Dict[str, Any]:
        if not self._redo_stack:
            raise RuntimeError("Nothing to redo.")
        self._history.append(copy.deepcopy(self._config))
        self._config = self._redo_stack.pop()
        self.save_config()
        return self.get_config()


def _now_iso() -> str:
    import datetime
    return datetime.datetime.utcnow().isoformat() + "Z"
