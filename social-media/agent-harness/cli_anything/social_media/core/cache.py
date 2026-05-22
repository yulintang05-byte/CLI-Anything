"""Local disk cache for trend data — avoids hammering scrapers repeatedly."""

import json
import os
import time
from pathlib import Path
from typing import Any, Optional

_CACHE_DIR = Path.home() / ".cli_anything" / "social_media_cache"
_DEFAULT_TTL = 3600  # 1 hour


def _cache_path(key: str) -> Path:
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    safe = key.replace("/", "_").replace(":", "_")
    return _CACHE_DIR / f"{safe}.json"


def get(key: str, ttl: int = _DEFAULT_TTL) -> Optional[Any]:
    p = _cache_path(key)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text())
        if time.time() - data.get("_ts", 0) > ttl:
            return None
        return data.get("payload")
    except (json.JSONDecodeError, KeyError):
        return None


def set(key: str, payload: Any) -> None:  # noqa: A001
    p = _cache_path(key)
    p.write_text(json.dumps({"_ts": time.time(), "payload": payload}))


def clear(key: Optional[str] = None) -> dict:
    if key:
        p = _cache_path(key)
        deleted = 1 if p.exists() else 0
        p.unlink(missing_ok=True)
        return {"deleted": deleted, "key": key}
    removed = 0
    if _CACHE_DIR.exists():
        for f in _CACHE_DIR.glob("*.json"):
            f.unlink()
            removed += 1
    return {"deleted": removed, "cache_dir": str(_CACHE_DIR)}


def info() -> dict:
    if not _CACHE_DIR.exists():
        return {"entries": 0, "cache_dir": str(_CACHE_DIR), "size_bytes": 0}
    files = list(_CACHE_DIR.glob("*.json"))
    total = sum(f.stat().st_size for f in files)
    now = time.time()
    entries = []
    for f in files:
        try:
            data = json.loads(f.read_text())
            age = int(now - data.get("_ts", now))
            entries.append({"key": f.stem, "age_seconds": age})
        except Exception:
            pass
    return {"entries": len(files), "cache_dir": str(_CACHE_DIR),
            "size_bytes": total, "items": entries}
