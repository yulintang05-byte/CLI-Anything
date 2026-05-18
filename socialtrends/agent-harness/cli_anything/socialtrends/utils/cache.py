"""Disk-based TTL cache to avoid hammering APIs."""

import json
import hashlib
import time
from pathlib import Path

CACHE_DIR = Path.home() / ".cache" / "cli-anything" / "socialtrends"


def _key_path(key: str) -> Path:
    h = hashlib.sha256(key.encode()).hexdigest()[:16]
    return CACHE_DIR / f"{h}.json"


def get_cached(key: str) -> dict | None:
    path = _key_path(key)
    if not path.exists():
        return None
    with open(path) as f:
        entry = json.load(f)
    if time.time() > entry.get("expires_at", 0):
        path.unlink(missing_ok=True)
        return None
    return entry.get("data")


def set_cached(key: str, data, ttl_hours: float = 6.0) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _key_path(key)
    with open(path, "w") as f:
        json.dump({"data": data, "expires_at": time.time() + ttl_hours * 3600}, f)


def clear_cache() -> int:
    if not CACHE_DIR.exists():
        return 0
    files = list(CACHE_DIR.glob("*.json"))
    for f in files:
        f.unlink(missing_ok=True)
    return len(files)
