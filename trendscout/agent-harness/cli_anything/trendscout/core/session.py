"""TrendScout session — config, cache, and API key management."""

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional


CONFIG_DIR = Path.home() / ".config" / "trendscout"
CACHE_DIR = Path.home() / ".cache" / "trendscout"
CONFIG_FILE = CONFIG_DIR / "config.json"
CACHE_TTL = 1800  # 30 minutes


def _ensure_dirs() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Any]:
    _ensure_dirs()
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_config(config: Dict[str, Any]) -> None:
    _ensure_dirs()
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def get_api_key(platform: str) -> Optional[str]:
    cfg = load_config()
    env_map = {
        "youtube": "YOUTUBE_API_KEY",
        "tiktok": "TIKTOK_API_TOKEN",
    }
    env_key = env_map.get(platform)
    if env_key and os.environ.get(env_key):
        return os.environ[env_key]
    return cfg.get("api_keys", {}).get(platform)


def set_api_key(platform: str, key: str) -> None:
    cfg = load_config()
    cfg.setdefault("api_keys", {})[platform] = key
    save_config(cfg)


def get_cache(cache_key: str) -> Optional[Any]:
    path = CACHE_DIR / f"{cache_key}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        if time.time() - data.get("_ts", 0) < CACHE_TTL:
            return data.get("payload")
    except (json.JSONDecodeError, OSError):
        pass
    return None


def set_cache(cache_key: str, payload: Any) -> None:
    _ensure_dirs()
    path = CACHE_DIR / f"{cache_key}.json"
    path.write_text(json.dumps({"_ts": time.time(), "payload": payload}, default=str))


def clear_cache() -> int:
    count = 0
    for p in CACHE_DIR.glob("*.json"):
        p.unlink()
        count += 1
    return count


def config_info() -> Dict[str, Any]:
    cfg = load_config()
    keys = cfg.get("api_keys", {})
    return {
        "config_path": str(CONFIG_FILE),
        "cache_dir": str(CACHE_DIR),
        "cache_ttl_seconds": CACHE_TTL,
        "youtube_api_key": "set" if keys.get("youtube") else "not set",
        "tiktok_api_token": "set" if keys.get("tiktok") else "not set",
        "region": cfg.get("region", "US"),
        "default_limit": cfg.get("default_limit", 25),
    }


def set_config_value(key: str, value: Any) -> None:
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)


def get_config_value(key: str, default: Any = None) -> Any:
    return load_config().get(key, default)
