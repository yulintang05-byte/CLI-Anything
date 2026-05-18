"""Stateful session management for the Social Trends CLI.

Tracks active platform targets, cached trend results, account profiles,
and content calendar state. Persists to disk as JSON between runs.
"""

import json
import os
import time
from pathlib import Path
from typing import Optional

SESSION_DIR = Path.home() / ".social-trends-cli" / "sessions"
CACHE_DIR = Path.home() / ".social-trends-cli" / "cache"
MAX_CACHE_AGE = 3600  # 1 hour before re-fetching


class Session:
    """Represents a stateful social trends CLI session."""

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"session_{int(time.time())}"
        self._accounts: list[dict] = []
        self._cached_trends: dict = {}
        self._active_niche: Optional[str] = None
        self._active_platform: Optional[str] = None
        self._content_calendar: list[dict] = []
        self._metadata: dict = {}

    # ── Account management ────────────────────────────────────────────

    def add_account(self, platform: str, handle: str, niche: str = "") -> dict:
        """Register a social media account to optimize."""
        account = {
            "id": f"{platform}:{handle}",
            "platform": platform.lower(),
            "handle": handle.lstrip("@"),
            "niche": niche,
            "added_at": time.time(),
        }
        existing = [a for a in self._accounts if a["id"] == account["id"]]
        if existing:
            existing[0].update(account)
        else:
            self._accounts.append(account)
        return account

    def remove_account(self, platform: str, handle: str) -> bool:
        before = len(self._accounts)
        self._accounts = [
            a for a in self._accounts
            if a["id"] != f"{platform.lower()}:{handle.lstrip('@')}"
        ]
        return len(self._accounts) < before

    def list_accounts(self) -> list[dict]:
        return list(self._accounts)

    def get_account(self, platform: str, handle: str) -> Optional[dict]:
        target_id = f"{platform.lower()}:{handle.lstrip('@')}"
        for a in self._accounts:
            if a["id"] == target_id:
                return a
        return None

    # ── Trend cache ───────────────────────────────────────────────────

    def cache_trends(self, key: str, data: list | dict) -> None:
        """Store fetched trend data with a timestamp."""
        self._cached_trends[key] = {
            "data": data,
            "fetched_at": time.time(),
        }

    def get_cached_trends(self, key: str) -> Optional[list | dict]:
        """Return cached data if it's still fresh, else None."""
        entry = self._cached_trends.get(key)
        if not entry:
            return None
        age = time.time() - entry["fetched_at"]
        if age > MAX_CACHE_AGE:
            return None
        return entry["data"]

    def clear_cache(self, key: Optional[str] = None) -> int:
        if key:
            removed = 1 if key in self._cached_trends else 0
            self._cached_trends.pop(key, None)
            return removed
        removed = len(self._cached_trends)
        self._cached_trends.clear()
        return removed

    def cache_keys(self) -> list[str]:
        return list(self._cached_trends.keys())

    # ── Niche / platform state ────────────────────────────────────────

    def set_niche(self, niche: str) -> None:
        self._active_niche = niche.lower().strip()

    def set_platform(self, platform: str) -> None:
        valid = {"youtube", "tiktok", "both"}
        p = platform.lower()
        if p not in valid:
            raise ValueError(f"Platform must be one of: {', '.join(valid)}")
        self._active_platform = p

    @property
    def active_niche(self) -> Optional[str]:
        return self._active_niche

    @property
    def active_platform(self) -> Optional[str]:
        return self._active_platform

    # ── Content calendar ──────────────────────────────────────────────

    def set_calendar(self, entries: list[dict]) -> None:
        self._content_calendar = entries

    def get_calendar(self) -> list[dict]:
        return list(self._content_calendar)

    # ── Persistence ───────────────────────────────────────────────────

    def save(self) -> str:
        SESSION_DIR.mkdir(parents=True, exist_ok=True)
        state = {
            "session_id": self.session_id,
            "accounts": self._accounts,
            "active_niche": self._active_niche,
            "active_platform": self._active_platform,
            "content_calendar": self._content_calendar,
            "metadata": self._metadata,
            "timestamp": time.time(),
        }
        path = SESSION_DIR / f"{self.session_id}.json"
        with open(path, "w") as f:
            json.dump(state, f, indent=2)
        return str(path)

    @classmethod
    def load(cls, session_id: str) -> Optional["Session"]:
        path = SESSION_DIR / f"{session_id}.json"
        if not path.is_file():
            return None
        with open(path) as f:
            data = json.load(f)
        s = cls(session_id=data["session_id"])
        s._accounts = data.get("accounts", [])
        s._active_niche = data.get("active_niche")
        s._active_platform = data.get("active_platform")
        s._content_calendar = data.get("content_calendar", [])
        s._metadata = data.get("metadata", {})
        return s

    @classmethod
    def list_sessions(cls) -> list[dict]:
        SESSION_DIR.mkdir(parents=True, exist_ok=True)
        sessions = []
        for p in SESSION_DIR.glob("*.json"):
            try:
                with open(p) as f:
                    d = json.load(f)
                sessions.append({
                    "session_id": d.get("session_id"),
                    "accounts": len(d.get("accounts", [])),
                    "niche": d.get("active_niche"),
                    "platform": d.get("active_platform"),
                    "timestamp": d.get("timestamp"),
                })
            except (json.JSONDecodeError, OSError):
                continue
        sessions.sort(key=lambda s: s.get("timestamp", 0), reverse=True)
        return sessions

    def status(self) -> dict:
        return {
            "session_id": self.session_id,
            "accounts": len(self._accounts),
            "active_niche": self._active_niche or "(none)",
            "active_platform": self._active_platform or "(none)",
            "cached_keys": len(self._cached_trends),
            "calendar_entries": len(self._content_calendar),
        }
