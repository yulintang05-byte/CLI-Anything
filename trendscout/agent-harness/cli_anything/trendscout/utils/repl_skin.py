"""TrendScout – REPL UI skin (terminal tables, banners, prompts)."""

from typing import Any, Dict, List, Optional

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.styles import Style
    from prompt_toolkit.formatted_text import HTML
    _HAS_PT = True
except ImportError:
    _HAS_PT = False


_BANNER = r"""
 _____ _                     _  ____                  _
|_   _| |_ ___ _ _ ___ ___ _| |/ ___|__ ___  _  _ | |_
  | | | '_/ -_) ' \/ _` (_-< _ \__ / _/ _ \| || || |  _|
  |_| |_| \___|_||_\__,_/__/___/___\__\___/ \_,_||_|\__|

  Viral Trend Intelligence for Social Media — CLI-Anything
"""


class ReplSkin:
    def __init__(self, version: str = "1.0.0") -> None:
        self.version = version

    def print_banner(self) -> None:
        print(_BANNER)
        print(f"  v{self.version}  |  Commands: help  quit  trends  account  theme-page\n")

    def print_goodbye(self) -> None:
        print("\n  Stay trending. Goodbye.\n")

    def success(self, msg: str) -> None:
        print(f"  ✓ {msg}")

    def error(self, msg: str) -> None:
        print(f"  ✗ {msg}")

    def info(self, msg: str) -> None:
        print(f"  → {msg}")

    def table(self, headers: List[str], rows: List[List[str]]) -> None:
        if not rows:
            print("  (empty)")
            return
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(widths):
                    widths[i] = max(widths[i], len(str(cell)))

        sep = "  " + "-+-".join("-" * w for w in widths)
        header_row = "  " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
        print(sep)
        print(header_row)
        print(sep)
        for row in rows:
            cells = [str(row[i]).ljust(widths[i]) if i < len(row) else " " * widths[i] for i in range(len(headers))]
            print("  " + " | ".join(cells))
        print(sep)

    def help(self, commands: Dict[str, str]) -> None:
        print("\n  Available commands:\n")
        for cmd, desc in commands.items():
            print(f"    {cmd:<45} {desc}")
        print()

    def create_prompt_session(self) -> Any:
        if _HAS_PT:
            return PromptSession(history=InMemoryHistory())
        return None

    def get_input(self, pt_session: Any, context: str = "", modified: bool = False) -> str:
        mod_marker = "*" if modified else ""
        prompt_str = f"trendscout{' [' + context + mod_marker + ']' if context else ''}> "
        if _HAS_PT and pt_session is not None:
            try:
                return pt_session.prompt(prompt_str)
            except Exception:
                pass
        return input(prompt_str)
