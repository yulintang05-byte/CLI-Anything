"""Social Trends CLI - Session & config management."""

import json
import os
import copy
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path


_CONFIG_DIR = Path.home() / ".cli-anything-social-trends"
_CONFIG_FILE = _CONFIG_DIR / "config.json"
_CACHE_FILE = _CONFIG_DIR / "trend_cache.json"


class Session:
    """Manages config state and trend cache with undo/redo history."""

    MAX_UNDO = 30

    def __init__(self):
        self.config: Dict[str, Any] = self._default_config()
        self._undo_stack: List[Dict[str, Any]] = []
        self._redo_stack: List[Dict[str, Any]] = []
        self._modified: bool = False
        self._trend_cache: Dict[str, Any] = {}
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self._load_config()
        self._load_cache()

    # ── defaults ──────────────────────────────────────────────────────────────

    def _default_config(self) -> Dict[str, Any]:
        return {
            "version": "1.0.0",
            "accounts": {},
            "api_keys": {
                "youtube": "",
                "tiktok_apify": "",
                "rapidapi": "",
            },
            "niches": [],
            "target_regions": ["US"],
            "posting_times": {
                "tiktok": ["7:00", "11:00", "19:00"],
                "youtube": ["15:00", "19:00"],
                "instagram": ["11:00", "17:00", "19:00"],
            },
            "theme_pages": {},
            "metadata": {
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat(),
            },
        }

    # ── persistence ───────────────────────────────────────────────────────────

    def _load_config(self) -> None:
        if _CONFIG_FILE.exists():
            try:
                with open(_CONFIG_FILE) as f:
                    data = json.load(f)
                self.config.update(data)
            except (json.JSONDecodeError, OSError):
                pass

    def save_config(self, path: Optional[str] = None) -> str:
        save_path = path or str(_CONFIG_FILE)
        self.config["metadata"]["modified"] = datetime.now().isoformat()
        with open(save_path, "w") as f:
            json.dump(self.config, f, indent=2, default=str)
        self._modified = False
        return save_path

    def _load_cache(self) -> None:
        if _CACHE_FILE.exists():
            try:
                with open(_CACHE_FILE) as f:
                    self._trend_cache = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._trend_cache = {}

    def save_cache(self) -> None:
        with open(_CACHE_FILE, "w") as f:
            json.dump(self._trend_cache, f, indent=2, default=str)

    def get_cache(self, key: str, max_age_minutes: int = 30) -> Optional[Any]:
        entry = self._trend_cache.get(key)
        if not entry:
            return None
        ts = datetime.fromisoformat(entry["timestamp"])
        age = (datetime.now() - ts).total_seconds() / 60
        if age > max_age_minutes:
            return None
        return entry["data"]

    def set_cache(self, key: str, data: Any) -> None:
        self._trend_cache[key] = {
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }
        self.save_cache()

    # ── undo/redo ─────────────────────────────────────────────────────────────

    def snapshot(self, description: str = "") -> None:
        state = {
            "config": copy.deepcopy(self.config),
            "description": description,
            "timestamp": datetime.now().isoformat(),
        }
        self._undo_stack.append(state)
        if len(self._undo_stack) > self.MAX_UNDO:
            self._undo_stack.pop(0)
        self._redo_stack.clear()
        self._modified = True

    def undo(self) -> str:
        if not self._undo_stack:
            raise RuntimeError("Nothing to undo.")
        self._redo_stack.append({
            "config": copy.deepcopy(self.config),
            "description": "redo point",
            "timestamp": datetime.now().isoformat(),
        })
        state = self._undo_stack.pop()
        self.config = state["config"]
        self._modified = True
        return state.get("description", "")

    def redo(self) -> str:
        if not self._redo_stack:
            raise RuntimeError("Nothing to redo.")
        self._undo_stack.append({
            "config": copy.deepcopy(self.config),
            "description": "undo point",
            "timestamp": datetime.now().isoformat(),
        })
        state = self._redo_stack.pop()
        self.config = state["config"]
        self._modified = True
        return state.get("description", "")

    def status(self) -> Dict[str, Any]:
        accounts = self.config.get("accounts", {})
        theme_pages = self.config.get("theme_pages", {})
        return {
            "accounts_count": len(accounts),
            "theme_pages_count": len(theme_pages),
            "niches": self.config.get("niches", []),
            "regions": self.config.get("target_regions", []),
            "modified": self._modified,
            "undo_count": len(self._undo_stack),
            "redo_count": len(self._redo_stack),
            "config_path": str(_CONFIG_FILE),
            "youtube_api_key_set": bool(self.config["api_keys"].get("youtube")),
            "tiktok_api_key_set": bool(self.config["api_keys"].get("tiktok_apify")),
        }

    def list_history(self) -> List[Dict[str, str]]:
        return [
            {
                "index": i,
                "description": s.get("description", ""),
                "timestamp": s.get("timestamp", ""),
            }
            for i, s in enumerate(reversed(self._undo_stack))
        ]
