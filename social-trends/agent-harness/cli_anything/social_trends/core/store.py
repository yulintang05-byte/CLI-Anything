"""Lightweight persistent store for social-trends session data."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


_DEFAULT_PATH = Path.home() / ".social_trends_session.json"


class Store:
    """Loads/saves all session data to a single JSON file."""

    def __init__(self, path: Optional[str] = None):
        self._path = Path(path) if path else _DEFAULT_PATH
        self._data: Dict[str, Any] = self._load()

    # ── persistence ──────────────────────────────────────────────────────────

    def _load(self) -> Dict[str, Any]:
        if self._path.exists():
            try:
                with open(self._path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return self._empty()

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._data["_updated"] = datetime.now().isoformat()
        with open(self._path, "w") as f:
            json.dump(self._data, f, indent=2, default=str)

    def _empty(self) -> Dict[str, Any]:
        return {
            "trends": [],
            "hashtags": [],
            "music": [],
            "accounts": [],
            "_updated": None,
        }

    def reset(self) -> None:
        self._data = self._empty()
        self.save()

    # ── trends ───────────────────────────────────────────────────────────────

    @property
    def trends(self) -> List[Dict[str, Any]]:
        return self._data.setdefault("trends", [])

    @trends.setter
    def trends(self, value: List[Dict[str, Any]]) -> None:
        self._data["trends"] = value

    # ── hashtags ─────────────────────────────────────────────────────────────

    @property
    def hashtags(self) -> List[Dict[str, Any]]:
        return self._data.setdefault("hashtags", [])

    @hashtags.setter
    def hashtags(self, value: List[Dict[str, Any]]) -> None:
        self._data["hashtags"] = value

    # ── music ────────────────────────────────────────────────────────────────

    @property
    def music(self) -> List[Dict[str, Any]]:
        return self._data.setdefault("music", [])

    @music.setter
    def music(self, value: List[Dict[str, Any]]) -> None:
        self._data["music"] = value

    # ── accounts ─────────────────────────────────────────────────────────────

    @property
    def accounts(self) -> List[Dict[str, Any]]:
        return self._data.setdefault("accounts", [])

    def get_account(self, account_id: str) -> Dict[str, Any]:
        for acc in self.accounts:
            if acc["id"] == account_id:
                return acc
        raise KeyError(f"Account '{account_id}' not found.")

    def add_account(self, account: Dict[str, Any]) -> None:
        self._data.setdefault("accounts", []).append(account)

    def update_account(self, account_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        acc = self.get_account(account_id)
        acc.update(updates)
        return acc
