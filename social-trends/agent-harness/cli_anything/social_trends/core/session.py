"""Session management — command history and undo/redo stack."""

import json
import time
import os
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class SessionEntry:
    command: str
    params: dict
    result: dict
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


class Session:
    def __init__(self, session_file: Optional[str] = None):
        self._file = session_file
        self._history: list[SessionEntry] = []
        self._undo_stack: list[SessionEntry] = []
        self._redo_stack: list[SessionEntry] = []
        if session_file:
            self._load()

    def record(self, command: str, params: dict, result: dict):
        entry = SessionEntry(command=command, params=params, result=result)
        self._history.append(entry)
        self._undo_stack.append(entry)
        self._redo_stack.clear()
        self._save()

    def undo(self) -> Optional[SessionEntry]:
        if not self._undo_stack:
            return None
        entry = self._undo_stack.pop()
        self._redo_stack.append(entry)
        self._save()
        return entry

    def redo(self) -> Optional[SessionEntry]:
        if not self._redo_stack:
            return None
        entry = self._redo_stack.pop()
        self._undo_stack.append(entry)
        self._save()
        return entry

    def history(self, limit: int = 20) -> list[dict]:
        entries = self._history[-limit:]
        return [e.to_dict() for e in reversed(entries)]

    def status(self) -> dict:
        return {
            "history_count": len(self._history),
            "undo_available": len(self._undo_stack),
            "redo_available": len(self._redo_stack),
            "session_file": self._file,
        }

    def _load(self):
        if not self._file or not os.path.exists(self._file):
            return
        try:
            with open(self._file) as f:
                data = json.load(f)
            for item in data.get("history", []):
                self._history.append(SessionEntry(**item))
                self._undo_stack.append(self._history[-1])
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

    def _save(self):
        if not self._file:
            return
        os.makedirs(os.path.dirname(self._file), exist_ok=True)
        with open(self._file, "w") as f:
            json.dump({"history": [e.to_dict() for e in self._history]}, f, indent=2)
