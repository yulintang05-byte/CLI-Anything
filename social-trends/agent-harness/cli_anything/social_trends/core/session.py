"""Session management — command history and undo/redo for social-trends CLI."""

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class HistoryEntry:
    command: str
    args: dict
    timestamp: str = ""
    result: dict | None = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "command": self.command,
            "args": self.args,
            "timestamp": self.timestamp,
            "result": self.result,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "HistoryEntry":
        return cls(
            command=d["command"],
            args=d.get("args", {}),
            timestamp=d.get("timestamp", ""),
            result=d.get("result"),
        )


class Session:
    def __init__(self, session_file: str | None = None):
        self._history: list[HistoryEntry] = []
        self._redo_stack: list[HistoryEntry] = []
        self._session_file = session_file
        if session_file:
            self._load(session_file)

    def record(self, command: str, args: dict, result: dict | None = None):
        self._history.append(HistoryEntry(command=command, args=args, result=result))
        self._redo_stack.clear()
        self._auto_save()

    def undo(self) -> HistoryEntry | None:
        if not self._history:
            return None
        entry = self._history.pop()
        self._redo_stack.append(entry)
        self._auto_save()
        return entry

    def redo(self) -> HistoryEntry | None:
        if not self._redo_stack:
            return None
        entry = self._redo_stack.pop()
        self._history.append(entry)
        self._auto_save()
        return entry

    def history(self, limit: int = 20) -> list[dict]:
        entries = self._history[-limit:] if limit else self._history
        return [e.to_dict() for e in entries]

    def status(self) -> dict:
        return {
            "history_count": len(self._history),
            "can_undo": len(self._history) > 0,
            "can_redo": len(self._redo_stack) > 0,
            "redo_count": len(self._redo_stack),
        }

    def _auto_save(self):
        if self._session_file:
            self.save(self._session_file)

    def save(self, path: str):
        data = {
            "history": [e.to_dict() for e in self._history],
            "redo_stack": [e.to_dict() for e in self._redo_stack],
        }
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def _load(self, path: str):
        p = Path(path)
        if not p.exists():
            return
        try:
            with open(p) as f:
                data = json.load(f)
            self._history = [HistoryEntry.from_dict(e) for e in data.get("history", [])]
            self._redo_stack = [HistoryEntry.from_dict(e) for e in data.get("redo_stack", [])]
        except (json.JSONDecodeError, IOError, KeyError):
            pass
