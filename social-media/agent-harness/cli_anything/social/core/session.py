"""Session — mutable state shared across the interactive REPL and CLI commands."""
import copy
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


_EMPTY_STATE: Dict[str, Any] = {
    "accounts": [],           # tracked social accounts
    "trends_cache": {},       # {platform: {region: {timestamp, data}}}
    "saved_hashtags": {},     # {niche: [tags]}
    "saved_music": [],        # trending music items
    "theme_pages": [],        # theme page configs
    "history": [],            # command history for undo
}


class Session:
    def __init__(self) -> None:
        self.state: Dict[str, Any] = copy.deepcopy(_EMPTY_STATE)
        self._snapshots: List[Dict] = []

    # ── snapshot / undo ──────────────────────────────────────────────────────

    def snapshot(self) -> None:
        self._snapshots.append(copy.deepcopy(self.state))

    def undo(self) -> bool:
        if not self._snapshots:
            return False
        self.state = self._snapshots.pop()
        return True

    # ── persistence ──────────────────────────────────────────────────────────

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(self.state, indent=2, ensure_ascii=False))

    def load(self, path: Path) -> None:
        self.state = json.loads(path.read_text())

    # ── accounts ─────────────────────────────────────────────────────────────

    def add_account(self, platform: str, handle: str, niche: str = "") -> Dict:
        self.snapshot()
        acct = {"id": f"acct{len(self.state['accounts'])}", "platform": platform, "handle": handle, "niche": niche, "metrics": {}}
        self.state["accounts"].append(acct)
        return acct

    def get_accounts(self, platform: Optional[str] = None) -> List[Dict]:
        accts = self.state["accounts"]
        if platform:
            accts = [a for a in accts if a["platform"].lower() == platform.lower()]
        return accts

    # ── trends cache ─────────────────────────────────────────────────────────

    def cache_trends(self, platform: str, region: str, data: Any) -> None:
        import time
        self.state["trends_cache"].setdefault(platform, {})[region] = {
            "timestamp": time.time(),
            "data": data,
        }

    def get_cached_trends(self, platform: str, region: str, max_age: int = 3600) -> Optional[Any]:
        import time
        bucket = self.state["trends_cache"].get(platform, {}).get(region)
        if bucket and (time.time() - bucket["timestamp"]) < max_age:
            return bucket["data"]
        return None

    # ── saved hashtags ────────────────────────────────────────────────────────

    def save_hashtags(self, niche: str, tags: List[str]) -> None:
        self.snapshot()
        self.state["saved_hashtags"][niche] = tags

    # ── saved music ──────────────────────────────────────────────────────────

    def save_music(self, items: List[Dict]) -> None:
        self.snapshot()
        self.state["saved_music"] = items
