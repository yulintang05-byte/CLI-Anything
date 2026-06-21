"""Social Backend — Configuration, credential management, and platform wrappers."""

import os
import json
from pathlib import Path
from typing import Optional


_CONFIG_DIR = Path.home() / ".config" / "cli-anything-social-trends"
_CREDS_FILE = _CONFIG_DIR / "credentials.json"
_PREFS_FILE = _CONFIG_DIR / "preferences.json"


class SocialConfig:
    def __init__(self):
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def load_credentials(self) -> dict:
        if _CREDS_FILE.exists():
            with open(_CREDS_FILE) as f:
                return json.load(f)
        return {}

    def save_credentials(self, creds: dict):
        with open(_CREDS_FILE, "w") as f:
            json.dump(creds, f, indent=2)
        _CREDS_FILE.chmod(0o600)

    def set_credential(self, key: str, value: str):
        creds = self.load_credentials()
        creds[key] = value
        self.save_credentials(creds)

    def get_credential(self, key: str, env_var: Optional[str] = None) -> Optional[str]:
        if env_var:
            val = os.environ.get(env_var)
            if val:
                return val
        creds = self.load_credentials()
        return creds.get(key)

    def load_preferences(self) -> dict:
        if _PREFS_FILE.exists():
            with open(_PREFS_FILE) as f:
                return json.load(f)
        return {"region": "US", "default_platform": "tiktok", "timezone_offset": 0}

    def save_preferences(self, prefs: dict):
        with open(_PREFS_FILE, "w") as f:
            json.dump(prefs, f, indent=2)

    def credentials_file(self) -> str:
        return str(_CREDS_FILE)

    def config_dir(self) -> str:
        return str(_CONFIG_DIR)


_config = SocialConfig()


def get_youtube_api_key() -> Optional[str]:
    return _config.get_credential("youtube_api_key", "YOUTUBE_API_KEY")


def get_tiktok_session() -> Optional[str]:
    return _config.get_credential("tiktok_session_id", "TIKTOK_SESSION_ID")


def get_region() -> str:
    prefs = _config.load_preferences()
    return prefs.get("region", "US")


def get_timezone_offset() -> int:
    prefs = _config.load_preferences()
    return int(prefs.get("timezone_offset", 0))


def save_credential(key: str, value: str):
    _config.set_credential(key, value)


def save_preference(key: str, value):
    prefs = _config.load_preferences()
    prefs[key] = value
    _config.save_preferences(prefs)


def config_status() -> dict:
    return {
        "config_dir": _config.config_dir(),
        "credentials_file": _config.credentials_file(),
        "youtube_api_key_set": bool(get_youtube_api_key()),
        "tiktok_session_set": bool(get_tiktok_session()),
        "region": get_region(),
        "timezone_offset": get_timezone_offset(),
    }
