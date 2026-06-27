"""Session state for the social-trends CLI."""

from typing import Any, Dict, List, Optional


class Session:
    def __init__(self) -> None:
        self.active_platform: Optional[str] = None   # "tiktok" | "youtube" | "all"
        self.active_niche: Optional[str] = None
        self.active_account: Optional[Dict[str, Any]] = None
        self.trend_cache: List[Dict[str, Any]] = []
        self.hashtag_cache: List[str] = []
        self.music_cache: List[Dict[str, Any]] = []
        self.history: List[str] = []

    def set_platform(self, platform: str) -> None:
        self.active_platform = platform.lower()

    def set_niche(self, niche: str) -> None:
        self.active_niche = niche

    def set_account(self, account: Dict[str, Any]) -> None:
        self.active_account = account

    def log(self, cmd: str) -> None:
        self.history.append(cmd)

    def status(self) -> Dict[str, Any]:
        return {
            "platform": self.active_platform or "not set",
            "niche": self.active_niche or "not set",
            "account": self.active_account.get("username") if self.active_account else "none",
            "cached_trends": len(self.trend_cache),
            "cached_hashtags": len(self.hashtag_cache),
            "cached_music": len(self.music_cache),
        }
