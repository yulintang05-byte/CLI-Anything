"""Backend session — credentials, config, account registry, and report caching."""

import json
import os
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


_CONFIG_DIR = Path.home() / ".cli-anything-social-trends"
_CONFIG_FILE = _CONFIG_DIR / "config.json"
_ACCOUNTS_FILE = _CONFIG_DIR / "accounts.json"
_REPORTS_DIR = _CONFIG_DIR / "reports"
_HISTORY_FILE = _CONFIG_DIR / "history"


@dataclass
class AccountEntry:
    platform: str
    username: str
    channel_id: Optional[str] = None
    niche: Optional[str] = None
    ms_token: Optional[str] = None  # TikTok session token
    added_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class Config:
    youtube_api_key: Optional[str] = None
    tiktok_ms_token: Optional[str] = None
    default_region: str = "US"
    default_niche: str = "motivation"
    use_playwright: bool = True
    max_results: int = 50


class SocialBackend:
    """Manages persistent config, credentials, and account registry."""

    def __init__(self):
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        _REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()
        self.accounts: dict[str, AccountEntry] = self._load_accounts()

    # ── Config ─────────────────────────────────────────────────────────

    def _load_config(self) -> Config:
        if _CONFIG_FILE.exists():
            try:
                data = json.loads(_CONFIG_FILE.read_text())
                return Config(**{k: v for k, v in data.items() if k in Config.__dataclass_fields__})
            except Exception:
                pass
        return Config()

    def save_config(self) -> None:
        _CONFIG_FILE.write_text(json.dumps(asdict(self.config), indent=2))

    def set_youtube_api_key(self, key: str) -> None:
        self.config.youtube_api_key = key
        self.save_config()

    def set_tiktok_ms_token(self, token: str) -> None:
        self.config.tiktok_ms_token = token
        self.save_config()

    def set_region(self, region: str) -> None:
        self.config.default_region = region.upper()
        self.save_config()

    def set_niche(self, niche: str) -> None:
        self.config.default_niche = niche.lower()
        self.save_config()

    # ── Accounts ───────────────────────────────────────────────────────

    def _load_accounts(self) -> dict[str, AccountEntry]:
        if _ACCOUNTS_FILE.exists():
            try:
                data = json.loads(_ACCOUNTS_FILE.read_text())
                return {k: AccountEntry(**v) for k, v in data.items()}
            except Exception:
                pass
        return {}

    def _save_accounts(self) -> None:
        _ACCOUNTS_FILE.write_text(
            json.dumps({k: asdict(v) for k, v in self.accounts.items()}, indent=2)
        )

    def add_account(
        self,
        platform: str,
        username: str,
        channel_id: Optional[str] = None,
        niche: Optional[str] = None,
    ) -> AccountEntry:
        key = f"{platform}:{username}"
        entry = AccountEntry(
            platform=platform,
            username=username,
            channel_id=channel_id,
            niche=niche or self.config.default_niche,
        )
        self.accounts[key] = entry
        self._save_accounts()
        return entry

    def remove_account(self, platform: str, username: str) -> bool:
        key = f"{platform}:{username}"
        if key in self.accounts:
            del self.accounts[key]
            self._save_accounts()
            return True
        return False

    def list_accounts(self) -> list[AccountEntry]:
        return list(self.accounts.values())

    def get_account(self, platform: str, username: str) -> Optional[AccountEntry]:
        return self.accounts.get(f"{platform}:{username}")

    def get_accounts_by_platform(self, platform: str) -> list[AccountEntry]:
        return [a for a in self.accounts.values() if a.platform == platform]

    # ── Reports ────────────────────────────────────────────────────────

    def save_report(self, report_type: str, data: dict) -> Path:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = _REPORTS_DIR / f"{report_type}_{timestamp}.json"
        filename.write_text(json.dumps(data, indent=2, default=str))
        return filename

    def list_reports(self, report_type: Optional[str] = None) -> list[Path]:
        pattern = f"{report_type}_*.json" if report_type else "*.json"
        return sorted(_REPORTS_DIR.glob(pattern), reverse=True)

    def load_report(self, path: Path) -> dict:
        return json.loads(path.read_text())

    # ── Status ─────────────────────────────────────────────────────────

    def status(self) -> dict:
        return {
            "config_dir": str(_CONFIG_DIR),
            "youtube_api_configured": bool(self.config.youtube_api_key),
            "tiktok_token_configured": bool(self.config.tiktok_ms_token),
            "default_region": self.config.default_region,
            "default_niche": self.config.default_niche,
            "accounts": len(self.accounts),
            "saved_reports": len(list(_REPORTS_DIR.glob("*.json"))),
        }

    @property
    def history_path(self) -> Path:
        return _HISTORY_FILE
