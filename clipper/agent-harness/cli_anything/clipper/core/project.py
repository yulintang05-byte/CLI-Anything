"""Clipper CLI - Project lifecycle management."""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from cli_anything.clipper.core.session import Session


PROFILES: Dict[str, Dict[str, Any]] = {
    "hd1080p30": {
        "name": "hd1080p30",
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "dar": "16:9",
        "description": "Full HD 1080p 30fps",
    },
    "hd1080p60": {
        "name": "hd1080p60",
        "width": 1920,
        "height": 1080,
        "fps": 60,
        "dar": "16:9",
        "description": "Full HD 1080p 60fps",
    },
    "hd720p30": {
        "name": "hd720p30",
        "width": 1280,
        "height": 720,
        "fps": 30,
        "dar": "16:9",
        "description": "HD 720p 30fps",
    },
    "hd720p60": {
        "name": "hd720p60",
        "width": 1280,
        "height": 720,
        "fps": 60,
        "dar": "16:9",
        "description": "HD 720p 60fps",
    },
    "vertical1080p": {
        "name": "vertical1080p",
        "width": 1080,
        "height": 1920,
        "fps": 30,
        "dar": "9:16",
        "description": "Vertical 1080x1920 (TikTok/Reels/Shorts)",
    },
    "vertical720p": {
        "name": "vertical720p",
        "width": 720,
        "height": 1280,
        "fps": 30,
        "dar": "9:16",
        "description": "Vertical 720x1280 (mobile)",
    },
    "square1080p": {
        "name": "square1080p",
        "width": 1080,
        "height": 1080,
        "fps": 30,
        "dar": "1:1",
        "description": "Square 1080x1080 (Instagram)",
    },
    "4k30": {
        "name": "4k30",
        "width": 3840,
        "height": 2160,
        "fps": 30,
        "dar": "16:9",
        "description": "4K UHD 30fps",
    },
}


def new_project(session: Session, name: str = "untitled",
                profile: str = "hd1080p30") -> Dict[str, Any]:
    """Create a new empty project."""
    if profile not in PROFILES:
        available = list(PROFILES.keys())
        raise ValueError(f"Unknown profile '{profile}'. Available: {available}")

    project = {
        "version": "1.0",
        "name": name,
        "profile": PROFILES[profile].copy(),
        "sources": [],
        "clips": [],
        "metadata": {
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
        },
    }
    session.set_project(project)
    return {
        "success": True,
        "name": name,
        "profile": profile,
        "project": project,
    }


def open_project(session: Session, path: str) -> Dict[str, Any]:
    """Load a project from a JSON file."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Project file not found: {path}")

    with open(path, "r") as f:
        project = json.load(f)

    _validate_project(project)
    session.set_project(project, path)

    return {
        "success": True,
        "path": path,
        "name": project.get("name", "untitled"),
        "sources": len(project.get("sources", [])),
        "clips": len(project.get("clips", [])),
    }


def save_project(session: Session, path: Optional[str] = None) -> Dict[str, Any]:
    """Save the current project to disk."""
    save_path = session.save_session(path)
    return {
        "success": True,
        "path": save_path,
        "name": session.project.get("name", "untitled"),
    }


def project_info(session: Session) -> Dict[str, Any]:
    """Return information about the current project."""
    project = session.get_project()
    profile = project.get("profile", {})
    sources = project.get("sources", [])
    clips = project.get("clips", [])

    total_duration = sum(
        max(0.0, c.get("out", 0.0) - c.get("in", 0.0))
        for c in clips
    )

    return {
        "name": project.get("name", "untitled"),
        "version": project.get("version", "1.0"),
        "profile": profile.get("name", "unknown"),
        "resolution": f"{profile.get('width', 0)}x{profile.get('height', 0)}",
        "fps": profile.get("fps", 30),
        "sources": len(sources),
        "clips": len(clips),
        "total_clip_duration": round(total_duration, 3),
        "project_path": session.project_path,
        "modified": session._modified,
        "metadata": project.get("metadata", {}),
    }


def list_profiles() -> List[Dict[str, Any]]:
    """List available project profiles."""
    return [
        {
            "name": k,
            "width": v["width"],
            "height": v["height"],
            "fps": v["fps"],
            "dar": v["dar"],
            "description": v["description"],
        }
        for k, v in PROFILES.items()
    ]


def _validate_project(project: Dict[str, Any]) -> None:
    """Validate a loaded project dict."""
    required_keys = ["version", "name", "sources", "clips"]
    for key in required_keys:
        if key not in project:
            raise ValueError(f"Invalid project file: missing key '{key}'")

    if "profile" not in project:
        project["profile"] = PROFILES["hd1080p30"].copy()

    if "metadata" not in project:
        project["metadata"] = {}
