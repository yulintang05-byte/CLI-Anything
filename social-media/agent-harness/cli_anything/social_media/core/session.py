"""Social Media CLI - Session management with undo/redo."""

import json
import os
import copy
from typing import Dict, Any, Optional, List
from datetime import datetime


class Session:
    """Manages workspace state with undo/redo history."""

    MAX_UNDO = 50

    def __init__(self):
        self.workspace: Optional[Dict[str, Any]] = None
        self.workspace_path: Optional[str] = None
        self._undo_stack: List[Dict[str, Any]] = []
        self._redo_stack: List[Dict[str, Any]] = []
        self._modified: bool = False

    def has_workspace(self) -> bool:
        return self.workspace is not None

    def get_workspace(self) -> Dict[str, Any]:
        if self.workspace is None:
            raise RuntimeError("No workspace loaded. Use 'workspace new' or 'workspace open' first.")
        return self.workspace

    def set_workspace(self, workspace: Dict[str, Any], path: Optional[str] = None) -> None:
        self.workspace = workspace
        self.workspace_path = path
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._modified = False

    def snapshot(self, description: str = "") -> None:
        if self.workspace is None:
            return
        state = {
            "workspace": copy.deepcopy(self.workspace),
            "description": description,
            "timestamp": datetime.now().isoformat(),
        }
        self._undo_stack.append(state)
        if len(self._undo_stack) > self.MAX_UNDO:
            self._undo_stack.pop(0)
        self._redo_stack.clear()
        self._modified = True

    def undo(self) -> Optional[str]:
        if not self._undo_stack:
            raise RuntimeError("Nothing to undo.")
        if self.workspace is None:
            raise RuntimeError("No workspace loaded.")
        self._redo_stack.append({
            "workspace": copy.deepcopy(self.workspace),
            "description": "before undo",
            "timestamp": datetime.now().isoformat(),
        })
        state = self._undo_stack.pop()
        self.workspace = state["workspace"]
        self._modified = True
        return state.get("description", "")

    def redo(self) -> Optional[str]:
        if not self._redo_stack:
            raise RuntimeError("Nothing to redo.")
        if self.workspace is None:
            raise RuntimeError("No workspace loaded.")
        self._undo_stack.append({
            "workspace": copy.deepcopy(self.workspace),
            "description": "before redo",
            "timestamp": datetime.now().isoformat(),
        })
        state = self._redo_stack.pop()
        self.workspace = state["workspace"]
        self._modified = True
        return state.get("description", "")

    def save(self, path: Optional[str] = None) -> str:
        save_path = path or self.workspace_path
        if not save_path:
            raise RuntimeError("No path specified and no workspace path set.")
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(self.workspace, f, indent=2, default=str)
        self.workspace_path = save_path
        self._modified = False
        return save_path

    def load(self, path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            workspace = json.load(f)
        self.set_workspace(workspace, path)
        return workspace

    @property
    def modified(self) -> bool:
        return self._modified

    def status(self) -> Dict[str, Any]:
        return {
            "has_workspace": self.has_workspace(),
            "workspace_path": self.workspace_path,
            "modified": self._modified,
            "undo_levels": len(self._undo_stack),
            "redo_levels": len(self._redo_stack),
        }
