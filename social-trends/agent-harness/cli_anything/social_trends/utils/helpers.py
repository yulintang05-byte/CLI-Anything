"""Utility helpers for social-trends CLI."""

from __future__ import annotations

import json
import os
from pathlib import Path
from datetime import datetime, timezone


def load_env(dotenv_path: str = ".env") -> dict[str, str]:
    """Load environment variables from a .env file."""
    env = {}
    path = Path(dotenv_path)
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip().strip('"').strip("'")
    for k, v in env.items():
        if k not in os.environ:
            os.environ[k] = v
    return env


def save_json(data: dict | list, path: str) -> None:
    """Write data to a JSON file with pretty-printing."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def load_json(path: str) -> dict | list | None:
    """Load JSON from a file, returning None if file doesn't exist."""
    p = Path(path)
    if not p.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def timestamp_filename(prefix: str, ext: str = "json") -> str:
    """Generate a timestamped filename like 'report_20250523_143022.json'."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{ts}.{ext}"


def format_number(n: int) -> str:
    """Format large numbers: 1500000 → '1.5M', 45000 → '45K'."""
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)
