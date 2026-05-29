"""Viral Trends CLI - Workspace lifecycle management."""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from cli_anything.viral_trends.core.session import Session


NICHES: Dict[str, Dict[str, Any]] = {
    "gaming": {
        "hashtag_seed": ["gaming", "gamer", "gameplay"],
        "peak_hour": 20,
        "description": "Video games, esports, streaming",
    },
    "finance": {
        "hashtag_seed": ["investing", "stocks", "money"],
        "peak_hour": 8,
        "description": "Investing, trading, personal finance",
    },
    "fitness": {
        "hashtag_seed": ["workout", "gym", "fitness"],
        "peak_hour": 6,
        "description": "Gym, workouts, nutrition, wellness",
    },
    "cooking": {
        "hashtag_seed": ["food", "recipe", "cooking"],
        "peak_hour": 18,
        "description": "Recipes, food reviews, cooking tips",
    },
    "tech": {
        "hashtag_seed": ["technology", "tech", "ai"],
        "peak_hour": 10,
        "description": "AI, gadgets, software, programming",
    },
    "beauty": {
        "hashtag_seed": ["makeup", "skincare", "beauty"],
        "peak_hour": 19,
        "description": "Makeup tutorials, skincare, fashion",
    },
    "motivation": {
        "hashtag_seed": ["motivation", "mindset", "success"],
        "peak_hour": 7,
        "description": "Mindset, success, self-improvement",
    },
    "entertainment": {
        "hashtag_seed": ["viral", "funny", "trending"],
        "peak_hour": 21,
        "description": "Viral clips, memes, pop culture",
    },
}


def new_workspace(session: Session, name: str = "untitled",
                  niche: str = "entertainment") -> Dict[str, Any]:
    """Create a new empty workspace."""
    if niche not in NICHES:
        available = list(NICHES.keys())
        raise ValueError(f"Unknown niche '{niche}'. Available: {available}")

    workspace = {
        "version": "1.0",
        "name": name,
        "niche": niche,
        "trend_snapshots": [],
        "schedule": [],
        "optimizer_config": {},
        "metadata": {
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
        },
    }
    session.set_project(workspace)
    return {
        "success": True,
        "name": name,
        "niche": niche,
        "workspace": workspace,
    }


def open_workspace(session: Session, path: str) -> Dict[str, Any]:
    """Load a workspace from a JSON file."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Workspace file not found: {path}")

    with open(path, "r") as f:
        workspace = json.load(f)

    _validate_workspace(workspace)
    session.set_project(workspace, path)

    return {
        "success": True,
        "path": path,
        "name": workspace.get("name", "untitled"),
        "niche": workspace.get("niche", "entertainment"),
        "snapshots": len(workspace.get("trend_snapshots", [])),
        "schedule_entries": len(workspace.get("schedule", [])),
    }


def save_workspace(session: Session, path: Optional[str] = None) -> Dict[str, Any]:
    """Save the current workspace to disk."""
    save_path = session.save_session(path)
    return {
        "success": True,
        "path": save_path,
        "name": session.project.get("name", "untitled"),
    }


def workspace_info(session: Session) -> Dict[str, Any]:
    """Return information about the current workspace."""
    workspace = session.get_project()
    return {
        "name": workspace.get("name", "untitled"),
        "version": workspace.get("version", "1.0"),
        "niche": workspace.get("niche", "entertainment"),
        "snapshots": len(workspace.get("trend_snapshots", [])),
        "schedule_entries": len(workspace.get("schedule", [])),
        "workspace_path": session.project_path,
        "modified": session._modified,
        "metadata": workspace.get("metadata", {}),
    }


def list_niches() -> List[Dict[str, Any]]:
    """List available niches."""
    return [
        {
            "name": k,
            "hashtag_seed": v["hashtag_seed"],
            "peak_hour": v["peak_hour"],
            "description": v["description"],
        }
        for k, v in NICHES.items()
    ]


def _validate_workspace(workspace: Dict[str, Any]) -> None:
    """Validate a loaded workspace dict."""
    required_keys = ["version", "name", "niche", "trend_snapshots", "schedule"]
    for key in required_keys:
        if key not in workspace:
            raise ValueError(f"Invalid workspace file: missing key '{key}'")

    if "metadata" not in workspace:
        workspace["metadata"] = {}
    if "optimizer_config" not in workspace:
        workspace["optimizer_config"] = {}
