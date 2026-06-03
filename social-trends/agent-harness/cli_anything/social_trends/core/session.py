"""Session management — history, undo, redo for social-trends CLI."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class HistoryEntry:
    command: str
    args: dict
    result: Any
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "command": self.command,
            "args": self.args,
            "result": self.result,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "HistoryEntry":
        return cls(
            command=d["command"],
            args=d.get("args", {}),
            result=d.get("result"),
            timestamp=d.get("timestamp", time.time()),
        )


class Session:
    def __init__(self, session_file: str | None = None):
        self._file = Path(session_file) if session_file else None
        self._history: list[HistoryEntry] = []
        self._undo_stack: list[HistoryEntry] = []
        self._load()

    def _load(self):
        if self._file and self._file.exists():
            try:
                with open(self._file) as f:
                    data = json.load(f)
                self._history = [HistoryEntry.from_dict(e) for e in data.get("history", [])]
            except (json.JSONDecodeError, IOError, KeyError):
                self._history = []

    def _save(self):
        if not self._file:
            return
        self._file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._file, "w") as f:
            json.dump({"history": [e.to_dict() for e in self._history[-200:]]}, f, indent=2, default=str)

    def record(self, command: str, args: dict, result: Any) -> HistoryEntry:
        entry = HistoryEntry(command=command, args=args, result=result)
        self._history.append(entry)
        self._undo_stack.clear()
        self._save()
        return entry

    def history(self, limit: int = 20) -> list[dict]:
        return [e.to_dict() for e in self._history[-limit:]]

    def undo(self) -> HistoryEntry | None:
        if not self._history:
            return None
        entry = self._history.pop()
        self._undo_stack.append(entry)
        self._save()
        return entry

    def redo(self) -> HistoryEntry | None:
        if not self._undo_stack:
            return None
        entry = self._undo_stack.pop()
        self._history.append(entry)
        self._save()
        return entry

    def status(self) -> dict:
        return {
            "history_count": len(self._history),
            "undo_available": len(self._undo_stack) > 0,
            "session_file": str(self._file) if self._file else None,
        }
