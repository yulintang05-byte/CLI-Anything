"""Session state — caches trend data and tracks current niche/platform selection."""

from typing import Optional
from datetime import datetime, timezone


class Session:
    def __init__(self) -> None:
        self._trends_cache: dict = {}
        self._current_niche: str = "general"
        self._current_platforms: list = ["tiktok", "youtube"]
        self._last_fetch: Optional[str] = None

    # ── trends cache ──────────────────────────────────────────────────────────

    def cache_trends(self, platform: str, data: dict) -> None:
        self._trends_cache[platform] = data
        self._last_fetch = datetime.now(timezone.utc).isoformat()

    def get_cached_trends(self, platform: str) -> Optional[dict]:
        return self._trends_cache.get(platform)

    def has_trends(self, platform: Optional[str] = None) -> bool:
        if platform:
            return platform in self._trends_cache
        return bool(self._trends_cache)

    def clear_cache(self) -> None:
        self._trends_cache.clear()
        self._last_fetch = None

    # ── context ───────────────────────────────────────────────────────────────

    @property
    def niche(self) -> str:
        return self._current_niche

    @niche.setter
    def niche(self, value: str) -> None:
        self._current_niche = value.lower()

    @property
    def platforms(self) -> list:
        return self._current_platforms

    @platforms.setter
    def platforms(self, value: list) -> None:
        self._current_platforms = [p.lower() for p in value]

    def status(self) -> dict:
        return {
            "current_niche": self._current_niche,
            "current_platforms": self._current_platforms,
            "cached_platforms": list(self._trends_cache.keys()),
            "last_fetch": self._last_fetch,
        }
