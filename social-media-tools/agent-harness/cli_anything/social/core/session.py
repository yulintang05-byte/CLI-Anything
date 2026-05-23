"""Session state for social media tools."""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional


class Session:
    """Persists scrape history, cached trends, and account configs."""

    def __init__(self, session_file: Optional[str] = None):
        self.session_file = session_file or str(
            Path.home() / ".cli-anything-social" / "session.json"
        )
        self._data: Dict[str, Any] = {
            "created_at": datetime.utcnow().isoformat(),
            "last_scrape": None,
            "cached_trends": {},
            "accounts": [],
            "history": [],
        }
        self._load()

    def _load(self):
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file) as f:
                    self._data.update(json.load(f))
            except (json.JSONDecodeError, IOError):
                pass

    def save(self):
        os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
        with open(self.session_file, "w") as f:
            json.dump(self._data, f, indent=2, default=str)

    def cache_trends(self, platform: str, trends: List[Dict]):
        self._data["cached_trends"][platform] = {
            "fetched_at": datetime.utcnow().isoformat(),
            "data": trends,
        }
        self._data["last_scrape"] = datetime.utcnow().isoformat()
        self.save()

    def get_cached(self, platform: str, max_age_minutes: int = 60) -> Optional[List[Dict]]:
        entry = self._data["cached_trends"].get(platform)
        if not entry:
            return None
        from datetime import timezone
        fetched = datetime.fromisoformat(entry["fetched_at"]).replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - fetched).total_seconds() / 60
        if age > max_age_minutes:
            return None
        return entry["data"]

    def add_account(self, platform: str, handle: str, niche: str = ""):
        accounts = self._data["accounts"]
        for acc in accounts:
            if acc["platform"] == platform and acc["handle"] == handle:
                acc["niche"] = niche or acc.get("niche", "")
                self.save()
                return
        accounts.append({
            "platform": platform,
            "handle": handle,
            "niche": niche,
            "added_at": datetime.utcnow().isoformat(),
        })
        self.save()

    def get_accounts(self) -> List[Dict]:
        return self._data["accounts"]

    def log(self, action: str, detail: str = ""):
        self._data["history"].append({
            "ts": datetime.utcnow().isoformat(),
            "action": action,
            "detail": detail,
        })
        if len(self._data["history"]) > 500:
            self._data["history"] = self._data["history"][-500:]
        self.save()

    @property
    def last_scrape(self) -> Optional[str]:
        return self._data.get("last_scrape")
