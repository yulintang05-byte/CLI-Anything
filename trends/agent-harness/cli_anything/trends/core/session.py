"""Session management for cli-anything-trends — history, undo, redo."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class SessionEntry:
    command: str
    params: dict
    result: dict
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


class Session:
    def __init__(self, session_file: str):
        self.session_file = Path(session_file)
        self._history: list[SessionEntry] = []
        self._undo_stack: list[SessionEntry] = []
        self._redo_stack: list[SessionEntry] = []
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
        return [e.to_dict() for e in self._history[-limit:]]

    def status(self) -> dict:
        return {
            "history_count": len(self._history),
            "undo_count": len(self._undo_stack),
            "redo_count": len(self._redo_stack),
            "session_file": str(self.session_file),
        }

    def _load(self):
        if not self.session_file.exists():
            return
        try:
            with open(self.session_file) as f:
                data = json.load(f)
            self._history = [SessionEntry(**e) for e in data.get("history", [])]
            self._undo_stack = [SessionEntry(**e) for e in data.get("undo_stack", [])]
            self._redo_stack = [SessionEntry(**e) for e in data.get("redo_stack", [])]
        except (json.JSONDecodeError, IOError, TypeError):
            self._history = []
            self._undo_stack = []
            self._redo_stack = []

    def _save(self):
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.session_file, "w") as f:
            json.dump(
                {
                    "history": [e.to_dict() for e in self._history[-200:]],
                    "undo_stack": [e.to_dict() for e in self._undo_stack[-50:]],
                    "redo_stack": [e.to_dict() for e in self._redo_stack[-50:]],
                },
                f,
                indent=2,
            )
