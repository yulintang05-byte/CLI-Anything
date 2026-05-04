import os
import json
import time
import hashlib
import sqlite3
import requests
from pathlib import Path
from typing import Optional, Any

CONFIG_DIR = Path.home() / ".cli-anything-social"
CACHE_DB = CONFIG_DIR / "cache.db"


def get_config() -> dict:
    config_file = CONFIG_DIR / "config.json"
    if config_file.exists():
        return json.loads(config_file.read_text())
    return {}


def save_config(config: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config_file = CONFIG_DIR / "config.json"
    config_file.write_text(json.dumps(config, indent=2))
    config_file.chmod(0o600)


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
    })
    return session


def _init_cache():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(CACHE_DB))
    conn.execute(
        """CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            expires_at REAL NOT NULL
        )"""
    )
    conn.commit()
    conn.close()


def get_cached(key: str) -> Optional[Any]:
    try:
        conn = sqlite3.connect(str(CACHE_DB))
        row = conn.execute(
            "SELECT value FROM cache WHERE key = ? AND expires_at > ?",
            (key, time.time()),
        ).fetchone()
        conn.close()
        if row:
            return json.loads(row[0])
    except Exception:
        pass
    return None


def set_cached(key: str, value: Any, ttl_seconds: int = 3600):
    try:
        _init_cache()
        conn = sqlite3.connect(str(CACHE_DB))
        conn.execute(
            "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
            (key, json.dumps(value), time.time() + ttl_seconds),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def cache_key(*args) -> str:
    return hashlib.md5("|".join(str(a) for a in args).encode()).hexdigest()
