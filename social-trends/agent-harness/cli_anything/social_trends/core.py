"""Session state management for social-trends CLI."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


@dataclass
class TrendSession:
    """Persistent session state for a trend research session."""

    name: str
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    region: str = "US"
    niche: str = ""
    youtube_trends: list[dict[str, Any]] = field(default_factory=list)
    tiktok_trends: list[dict[str, Any]] = field(default_factory=list)
    hashtags: list[dict[str, Any]] = field(default_factory=list)
    sounds: list[dict[str, Any]] = field(default_factory=list)
    optimization_report: dict[str, Any] = field(default_factory=dict)
    accounts: list[dict[str, Any]] = field(default_factory=list)
    modified: bool = False

    # ── Serialization ──────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("modified", None)
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TrendSession":
        data.pop("modified", None)
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def save(self, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.updated_at = time.time()
        self.modified = False
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> "TrendSession":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    # ── Mutations ──────────────────────────────────────────────────────

    def set_youtube_trends(self, trends: list[dict[str, Any]]) -> None:
        self.youtube_trends = trends
        self.modified = True

    def set_tiktok_trends(self, trends: list[dict[str, Any]]) -> None:
        self.tiktok_trends = trends
        self.modified = True

    def set_hashtags(self, hashtags: list[dict[str, Any]]) -> None:
        self.hashtags = hashtags
        self.modified = True

    def set_sounds(self, sounds: list[dict[str, Any]]) -> None:
        self.sounds = sounds
        self.modified = True

    def set_optimization_report(self, report: dict[str, Any]) -> None:
        self.optimization_report = report
        self.modified = True

    def add_account(self, platform: str, handle: str, niche: str = "") -> dict[str, Any]:
        account = {
            "platform": platform,
            "handle": handle,
            "niche": niche or self.niche,
            "added_at": time.time(),
            "optimized": False,
        }
        self.accounts.append(account)
        self.modified = True
        return account

    def remove_account(self, handle: str) -> bool:
        before = len(self.accounts)
        self.accounts = [a for a in self.accounts if a["handle"] != handle]
        if len(self.accounts) < before:
            self.modified = True
            return True
        return False

    # ── Queries ────────────────────────────────────────────────────────

    def top_hashtags(self, n: int = 10) -> list[dict[str, Any]]:
        return sorted(self.hashtags, key=lambda h: h.get("score", 0), reverse=True)[:n]

    def top_sounds(self, n: int = 10) -> list[dict[str, Any]]:
        return sorted(self.sounds, key=lambda s: s.get("score", s.get("usage_count", 0)), reverse=True)[:n]

    def all_trends(self) -> list[dict[str, Any]]:
        combined = []
        for t in self.youtube_trends:
            combined.append({**t, "platform": "youtube"})
        for t in self.tiktok_trends:
            combined.append({**t, "platform": "tiktok"})
        return sorted(combined, key=lambda x: x.get("score", 0), reverse=True)

    @property
    def summary(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "region": self.region,
            "niche": self.niche or "(all)",
            "youtube_trends": len(self.youtube_trends),
            "tiktok_trends": len(self.tiktok_trends),
            "hashtags": len(self.hashtags),
            "sounds": len(self.sounds),
            "accounts": len(self.accounts),
            "has_optimization": bool(self.optimization_report),
        }


# ── Session file helpers ───────────────────────────────────────────────


def default_session_path(name: str) -> str:
    return str(Path(name).with_suffix(".trends.json"))


def session_exists(path: str) -> bool:
    return Path(path).exists()
