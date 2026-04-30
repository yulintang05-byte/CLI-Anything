"""Session management for social-media CLI."""

import json
import os
import copy
from datetime import datetime


class Session:
    def __init__(self):
        self._project: dict = {}
        self._path: str = ""
        self._history: list[dict] = []
        self._history_index: int = -1

    def has_project(self) -> bool:
        return bool(self._project)

    def get_project(self) -> dict:
        if not self._project:
            raise RuntimeError("No project loaded. Run 'project new' first.")
        return self._project

    def set_project(self, project: dict, path: str = ""):
        self._project = project
        self._path = path or ""
        self._history = []
        self._history_index = -1

    def snapshot(self, description: str):
        if self._history_index < len(self._history) - 1:
            self._history = self._history[:self._history_index + 1]
        self._history.append({
            "description": description,
            "state": copy.deepcopy(self._project),
            "timestamp": datetime.utcnow().isoformat(),
        })
        self._history_index = len(self._history) - 1

    def undo(self) -> str:
        if self._history_index < 0:
            raise RuntimeError("Nothing to undo.")
        entry = self._history[self._history_index]
        self._history_index -= 1
        if self._history_index >= 0:
            self._project = copy.deepcopy(self._history[self._history_index]["state"])
        return entry["description"]

    def redo(self) -> str:
        if self._history_index >= len(self._history) - 1:
            raise RuntimeError("Nothing to redo.")
        self._history_index += 1
        entry = self._history[self._history_index]
        self._project = copy.deepcopy(entry["state"])
        return entry["description"]

    def list_history(self) -> list[dict]:
        return [
            {"index": i, "description": h["description"],
             "timestamp": h["timestamp"],
             "current": i == self._history_index}
            for i, h in enumerate(self._history)
        ]

    def save_session(self, path: str = "") -> str:
        save_path = path or self._path
        if not save_path:
            raise RuntimeError("No save path specified.")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(self._project, f, indent=2, default=str)
        self._path = save_path
        return save_path

    def is_modified(self) -> bool:
        if not self._history:
            return False
        return True

    def status(self) -> dict:
        proj = self._project
        return {
            "has_project": self.has_project(),
            "project_name": proj.get("name", "") if self.has_project() else "",
            "save_path": self._path,
            "history_steps": len(self._history),
            "history_index": self._history_index,
            "accounts": len(proj.get("accounts", [])) if self.has_project() else 0,
            "cached_trends": bool(proj.get("last_trends_fetch")) if self.has_project() else False,
        }
