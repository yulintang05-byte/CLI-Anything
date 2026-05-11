"""REPL skin — banner, prompt, table, colored output for social-trends CLI."""

from __future__ import annotations
import os
from typing import Any, Dict, List, Optional

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.styles import Style
    _HAS_PT = True
except ImportError:
    _HAS_PT = False

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
DIM = "\033[2m"

_USE_COLOR = os.isatty(1)


def _c(color: str, text: str) -> str:
    return f"{color}{text}{RESET}" if _USE_COLOR else text


class ReplSkin:
    def __init__(self, version: str = "1.0.0") -> None:
        self.version = version

    def print_banner(self) -> None:
        banner = f"""
{_c(CYAN, BOLD + '╔══════════════════════════════════════════════════════╗')}
{_c(CYAN, '║')}  {_c(MAGENTA, BOLD + '📊  Social Trends CLI')} {_c(DIM, f'v{self.version}')}                       {_c(CYAN, '║')}
{_c(CYAN, '║')}  {_c(DIM, 'Viral trends · Hashtags · Music · Account Optimizer')}  {_c(CYAN, '║')}
{_c(CYAN, '╚══════════════════════════════════════════════════════╝')}
Type {_c(YELLOW, 'help')} to list commands.  Type {_c(YELLOW, 'quit')} to exit.
"""
        print(banner)

    def print_goodbye(self) -> None:
        print(_c(CYAN, "\nStay on trend. Goodbye!\n"))

    def success(self, msg: str) -> None:
        print(_c(GREEN, f"✓  {msg}"))

    def error(self, msg: str) -> None:
        print(_c(RED, f"✗  {msg}"))

    def warn(self, msg: str) -> None:
        print(_c(YELLOW, f"⚠  {msg}"))

    def info(self, msg: str) -> None:
        print(_c(CYAN, f"→  {msg}"))

    def table(self, headers: List[str], rows: List[List[str]]) -> None:
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        sep = "  "
        header_line = sep.join(
            _c(BOLD, h.ljust(col_widths[i])) for i, h in enumerate(headers)
        )
        divider = sep.join("─" * w for w in col_widths)
        print(header_line)
        print(_c(DIM, divider))
        for row in rows:
            line = sep.join(
                str(row[i]).ljust(col_widths[i]) if i < len(row) else " " * col_widths[i]
                for i in range(len(headers))
            )
            print(line)

    def section(self, title: str) -> None:
        print(f"\n{_c(CYAN, BOLD + f'── {title} ' + '─' * max(0, 50 - len(title)))}")

    def help(self, commands: Dict[str, str]) -> None:
        self.section("Available Commands")
        for cmd, desc in commands.items():
            print(f"  {_c(YELLOW, cmd.ljust(48))}  {_c(DIM, desc)}")
        print()

    def create_prompt_session(self) -> Any:
        if _HAS_PT:
            style = Style.from_dict({"prompt": "ansicyan bold"})
            return PromptSession(history=InMemoryHistory(), style=style)
        return None

    def get_input(self, session: Any, context: str = "", modified: bool = False) -> str:
        mod_flag = _c(YELLOW, "*") if modified else ""
        ctx = f"({context})" if context else ""
        prompt_str = f"{_c(CYAN, 'social-trends')}{_c(DIM, ctx)}{mod_flag} {_c(GREEN, '▶')} "
        if _HAS_PT and session is not None:
            return session.prompt(prompt_str)
        return input(prompt_str)
