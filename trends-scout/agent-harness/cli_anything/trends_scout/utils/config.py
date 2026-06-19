"""Configuration management for trends-scout: API keys and account settings."""
import json
import os
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".config" / "trends-scout"
CONFIG_FILE = CONFIG_DIR / "config.json"


def _load() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def _save(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))
    CONFIG_FILE.chmod(0o600)


def get(key: str, fallback: Optional[str] = None) -> Optional[str]:
    return os.environ.get(key.upper().replace("-", "_")) or _load().get(key) or fallback


def set_key(key: str, value: str) -> dict:
    cfg = _load()
    cfg[key] = value
    _save(cfg)
    return {"set": key, "ok": True}


def get_all() -> dict:
    cfg = _load()
    # Mask secrets
    masked = {}
    for k, v in cfg.items():
        if any(s in k.lower() for s in ("key", "secret", "token", "password")):
            masked[k] = v[:6] + "..." if v and len(v) > 6 else "***"
        else:
            masked[k] = v
    return masked


def get_accounts() -> list:
    cfg = _load()
    return cfg.get("accounts", [])


def add_account(platform: str, handle: str, niche: str = "") -> dict:
    cfg = _load()
    accounts = cfg.get("accounts", [])
    # Avoid duplicates
    for acc in accounts:
        if acc["platform"] == platform and acc["handle"] == handle:
            acc["niche"] = niche or acc.get("niche", "")
            _save(cfg)
            return {"updated": True, "account": acc}
    account = {"platform": platform, "handle": handle, "niche": niche}
    accounts.append(account)
    cfg["accounts"] = accounts
    _save(cfg)
    return {"added": True, "account": account}


def remove_account(platform: str, handle: str) -> dict:
    cfg = _load()
    before = len(cfg.get("accounts", []))
    cfg["accounts"] = [
        a for a in cfg.get("accounts", [])
        if not (a["platform"] == platform and a["handle"] == handle)
    ]
    _save(cfg)
    removed = before - len(cfg["accounts"])
    return {"removed": removed, "handle": handle, "platform": platform}
