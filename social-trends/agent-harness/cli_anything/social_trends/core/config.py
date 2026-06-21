"""Config management — stores API keys and preferences in ~/.cli-anything-social-trends/"""

import json
import os
from pathlib import Path
from typing import Any, Optional

_CONFIG_DIR = Path.home() / ".cli-anything-social-trends"
_CONFIG_FILE = _CONFIG_DIR / "config.json"


def _ensure_dir() -> None:
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load() -> dict:
    _ensure_dir()
    if not _CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(_CONFIG_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save(cfg: dict) -> None:
    _ensure_dir()
    _CONFIG_FILE.write_text(json.dumps(cfg, indent=2))
    _CONFIG_FILE.chmod(0o600)


def get(key: str, default: Any = None) -> Any:
    return load().get(key, default)


def set_key(key: str, value: Any) -> None:
    cfg = load()
    cfg[key] = value
    save(cfg)


def require(key: str, env_var: Optional[str] = None) -> str:
    """Return value or raise with setup hint."""
    if env_var:
        val = os.environ.get(env_var)
        if val:
            return val
    val = get(key)
    if val:
        return val
    hint = f"Run: social-trends config set {key} <value>"
    if env_var:
        hint += f"  or set env var {env_var}"
    raise ValueError(f"Missing config key '{key}'. {hint}")
