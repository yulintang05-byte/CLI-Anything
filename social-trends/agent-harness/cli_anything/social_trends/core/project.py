"""Social Trends - Project management."""

import json
import os
from typing import Dict, Any, Optional
from datetime import datetime

from cli_anything.social_trends.core.session import Session


def new_project(session: Session, name: str) -> Dict[str, Any]:
    """Create a new social trends project."""
    project: Dict[str, Any] = {
        "name": name,
        "metadata": {
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "version": "1.0",
        },
        "config": {
            "youtube_api_key": "",
            "default_region": "US",
            "default_platforms": ["youtube", "tiktok"],
            "niche": "",
        },
        "accounts": [],
        "trends": [],
        "hashtag_sets": [],
        "music": [],
        "calendar": [],
    }
    session.set_project(project)
    return project


def open_project(session: Session, path: str) -> Dict[str, Any]:
    """Open an existing project from disk."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Project file not found: {path}")
    with open(path) as f:
        project = json.load(f)
    _validate_project(project)
    session.set_project(project, path=path)
    return project


def set_config(session: Session, key: str, value: str) -> Dict[str, Any]:
    """Set a project configuration value."""
    project = session.get_project()
    session.snapshot(f"set config {key}")
    project["config"][key] = value
    return {"key": key, "value": value}


def get_config(session: Session) -> Dict[str, Any]:
    """Get all project configuration."""
    project = session.get_project()
    cfg = dict(project.get("config", {}))
    # Mask API key in output
    if cfg.get("youtube_api_key"):
        cfg["youtube_api_key"] = cfg["youtube_api_key"][:8] + "..." if len(cfg["youtube_api_key"]) > 8 else "***"
    return cfg


def project_info(session: Session) -> Dict[str, Any]:
    """Get project summary."""
    project = session.get_project()
    return {
        "name": project.get("name"),
        "metadata": project.get("metadata", {}),
        "accounts_count": len(project.get("accounts", [])),
        "trends_cached": len(project.get("trends", [])),
        "hashtag_sets": len(project.get("hashtag_sets", [])),
        "music_tracks": len(project.get("music", [])),
        "calendar_entries": len(project.get("calendar", [])),
        "config": get_config(session),
    }


def _validate_project(project: Dict[str, Any]) -> None:
    required = ["name", "metadata", "config"]
    for field in required:
        if field not in project:
            raise ValueError(f"Invalid project file: missing field '{field}'")
