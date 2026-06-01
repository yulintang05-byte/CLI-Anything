"""TrendScout – in-memory session with undo/redo."""

import copy
from typing import Any, Dict, List, Optional


class Session:
    MAX_UNDO = 50

    def __init__(self) -> None:
        self.config: Dict[str, Any] = {
            "accounts": [],
            "watched_niches": [],
            "cached_trends": {},
        }
        self._undo_stack: List[Dict[str, Any]] = []
        self._redo_stack: List[Dict[str, Any]] = []
        self._modified: bool = False

    def snapshot(self, description: str = "") -> None:
        self._undo_stack.append(
            {"description": description, "config": copy.deepcopy(self.config)}
        )
        if len(self._undo_stack) > self.MAX_UNDO:
            self._undo_stack.pop(0)
        self._redo_stack.clear()
        self._modified = True

    def undo(self) -> str:
        if not self._undo_stack:
            raise RuntimeError("Nothing to undo")
        entry = self._undo_stack.pop()
        self._redo_stack.append(
            {"description": entry["description"], "config": copy.deepcopy(self.config)}
        )
        self.config = entry["config"]
        return entry["description"]

    def redo(self) -> str:
        if not self._redo_stack:
            raise RuntimeError("Nothing to redo")
        entry = self._redo_stack.pop()
        self._undo_stack.append(
            {"description": entry["description"], "config": copy.deepcopy(self.config)}
        )
        self.config = entry["config"]
        return entry["description"]

    def status(self) -> Dict[str, Any]:
        return {
            "accounts": len(self.config["accounts"]),
            "watched_niches": len(self.config["watched_niches"]),
            "modified": self._modified,
            "undo_count": len(self._undo_stack),
            "redo_count": len(self._redo_stack),
        }

    def list_history(self) -> List[str]:
        return [e["description"] for e in self._undo_stack]
