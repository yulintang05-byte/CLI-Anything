"""REPL skin for trend-scout — consistent UI across interactive and CLI modes."""

import sys
from typing import Any

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.styles import Style
    from prompt_toolkit.formatted_text import HTML
    _HAS_PT = True
except ImportError:
    _HAS_PT = False


_BRAND = "\033[95m"  # magenta
_CYAN  = "\033[96m"
_GREEN = "\033[92m"
_YELLOW = "\033[93m"
_RED   = "\033[91m"
_BOLD  = "\033[1m"
_DIM   = "\033[2m"
_RESET = "\033[0m"


def _c(text: str, *codes: str) -> str:
    if not sys.stdout.isatty():
        return text
    return "".join(codes) + text + _RESET


BANNER = r"""
  ████████╗██████╗ ███████╗███╗   ██╗██████╗     ███████╗ ██████╗ ██████╗ ██╗   ██╗████████╗
     ██╔══╝██╔══██╗██╔════╝████╗  ██║██╔══██╗    ██╔════╝██╔════╝██╔═══██╗██║   ██║╚══██╔══╝
     ██║   ██████╔╝█████╗  ██╔██╗ ██║██║  ██║    ███████╗██║     ██║   ██║██║   ██║   ██║
     ██║   ██╔══██╗██╔══╝  ██║╚██╗██║██║  ██║    ╚════██║██║     ██║   ██║██║   ██║   ██║
     ██║   ██║  ██║███████╗██║ ╚████║██████╔╝    ███████║╚██████╗╚██████╔╝╚██████╔╝   ██║
     ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚═════╝     ╚══════╝ ╚═════╝ ╚═════╝  ╚═════╝    ╚═╝
"""


class ReplSkin:
    def __init__(self, version: str = "1.0.0"):
        self.version = version

    def print_banner(self) -> None:
        print(_c(BANNER, _BRAND, _BOLD))
        print(_c(f"  Viral trend scraper for YouTube & TikTok  ·  v{self.version}", _DIM))
        print(_c("  Type 'help' for commands, 'quit' to exit\n", _DIM))

    def success(self, msg: str) -> None:
        print(_c(f"✓ {msg}", _GREEN))

    def error(self, msg: str) -> None:
        print(_c(f"✗ {msg}", _RED), file=sys.stderr)

    def info(self, msg: str) -> None:
        print(_c(f"→ {msg}", _CYAN))

    def warn(self, msg: str) -> None:
        print(_c(f"⚠ {msg}", _YELLOW))

    def table(self, headers: list[str], rows: list[list[str]]) -> None:
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        header_line = "  " + "  ".join(
            _c(h.ljust(col_widths[i]), _BOLD) for i, h in enumerate(headers)
        )
        sep_line = "  " + "  ".join("─" * w for w in col_widths)
        print(header_line)
        print(_c(sep_line, _DIM))
        for row in rows:
            cells = [str(row[i]).ljust(col_widths[i]) if i < len(col_widths) else str(row[i]) for i in range(len(headers))]
            print("  " + "  ".join(cells))

    def section(self, title: str) -> None:
        print()
        print(_c(f"  ── {title} ──", _CYAN, _BOLD))

    def bullet_list(self, items: list[str], indent: int = 4) -> None:
        pad = " " * indent
        for item in items:
            print(f"{pad}• {item}")

    def help(self, commands: dict[str, str]) -> None:
        self.section("Commands")
        for cmd, desc in commands.items():
            print(f"  {_c(cmd.ljust(45), _CYAN)}  {desc}")
        print()

    def print_goodbye(self) -> None:
        print(_c("\n  Later. Keep scouting. 🔥\n", _BRAND))

    def create_prompt_session(self) -> Any:
        if not _HAS_PT:
            return None

        style = Style.from_dict({
            "prompt": "#cc44ff bold",
            "platform": "#00ccff",
        })
        return PromptSession(history=InMemoryHistory(), style=style)

    def get_input(self, session: Any, context: str = "", modified: bool = False) -> str:
        indicator = _c("*", _YELLOW) if modified else ""
        if _HAS_PT and session is not None:
            ctx_str = f"[{context}]" if context else ""
            try:
                return session.prompt(
                    HTML(f"<prompt>trend-scout</prompt>{ctx_str}{indicator}> ")
                )
            except Exception:
                pass
        prompt_str = f"trend-scout{'[' + context + ']' if context else ''}{indicator}> "
        return input(prompt_str)
