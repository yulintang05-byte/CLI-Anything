"""Session state management for viral-trends CLI."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

CONFIG_DIR   = Path.home() / ".config" / "viral-trends"
SESSION_FILE = CONFIG_DIR / "session.json"


def _load() -> dict:
    if not SESSION_FILE.exists():
        return {"history": [], "last_trends": {}, "prefs": {}}
    try:
        return json.loads(SESSION_FILE.read_text())
    except (json.JSONDecodeError, IOError):
        return {"history": [], "last_trends": {}, "prefs": {}}


def _save(state: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(json.dumps(state, indent=2, default=str))


def record_command(cmd: str, result_summary: str) -> None:
    state = _load()
    state["history"].append({
        "ts":      time.time(),
        "command": cmd,
        "summary": result_summary,
    })
    state["history"] = state["history"][-200:]  # keep last 200
    _save(state)


def get_history(limit: int = 20) -> list[dict]:
    return _load()["history"][-limit:]


def set_pref(key: str, value: Any) -> None:
    state = _load()
    state["prefs"][key] = value
    _save(state)


def get_pref(key: str, default: Any = None) -> Any:
    return _load()["prefs"].get(key, default)


def clear_history() -> None:
    state = _load()
    state["history"] = []
    _save(state)
