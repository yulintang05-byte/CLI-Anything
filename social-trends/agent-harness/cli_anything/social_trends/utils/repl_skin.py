"""cli-anything REPL Skin — Social Trends edition.

Extends the standard ReplSkin with social-media-themed styling.
"""

import os
import sys
import re

_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"

_CYAN = "\033[38;5;80m"
_DARK_GRAY = "\033[38;5;240m"
_LIGHT_GRAY = "\033[38;5;250m"
_WHITE = "\033[97m"
_GRAY = "\033[38;5;245m"

_GREEN = "\033[38;5;78m"
_YELLOW = "\033[38;5;220m"
_RED = "\033[38;5;196m"
_BLUE = "\033[38;5;75m"
_PINK = "\033[38;5;213m"          # TikTok pink
_SOCIAL_ACCENT = "\033[38;5;213m" # hot pink for social

_H_LINE = "─"
_V_LINE = "│"
_TL = "╭"
_TR = "╮"
_BL = "╰"
_BR = "╯"

_ICON = f"{_PINK}{_BOLD}◆{_RESET}"


def _strip_ansi(text: str) -> str:
    return re.sub(r"\033\[[^m]*m", "", text)


def _visible_len(text: str) -> int:
    return len(_strip_ansi(text))


class ReplSkin:
    def __init__(self, software: str = "social-trends", version: str = "1.0.0",
                 history_file=None):
        self.software = software
        self.display_name = "Social Trends"
        self.version = version
        self.accent = _SOCIAL_ACCENT
        self._color = self._detect_color()
        if history_file is None:
            from pathlib import Path
            hist_dir = Path.home() / ".cli-anything-social-trends"
            hist_dir.mkdir(parents=True, exist_ok=True)
            self.history_file = str(hist_dir / "history")
        else:
            self.history_file = history_file

    def _detect_color(self) -> bool:
        if os.environ.get("NO_COLOR"):
            return False
        if not hasattr(sys.stdout, "isatty"):
            return False
        return sys.stdout.isatty()

    def _c(self, code: str, text: str) -> str:
        if not self._color:
            return text
        return f"{code}{text}{_RESET}"

    def print_banner(self):
        inner = 54
        def box(content):
            pad = inner - _visible_len(content)
            vl = self._c(_DARK_GRAY, _V_LINE)
            return f"{vl}{content}{' ' * max(0, pad)}{vl}"
        top = self._c(_DARK_GRAY, f"{_TL}{_H_LINE * inner}{_TR}")
        bot = self._c(_DARK_GRAY, f"{_BL}{_H_LINE * inner}{_BR}")
        icon = self._c(_PINK + _BOLD, "◆")
        brand = self._c(_CYAN + _BOLD, "cli-anything")
        dot = self._c(_DARK_GRAY, "·")
        name = self._c(_PINK + _BOLD, "Social Trends")
        title = f" {icon}  {brand} {dot} {name}"
        ver = f" {self._c(_DARK_GRAY, f'   v{self.version} — YouTube + TikTok trend intelligence')}"
        tip = f" {self._c(_DARK_GRAY, '   Type help for commands, quit to exit')}"
        print(top)
        print(box(title))
        print(box(ver))
        print(box(""))
        print(box(tip))
        print(bot)
        print()

    def prompt(self, context: str = "", modified: bool = False) -> str:
        parts = []
        if self._color:
            parts.append(f"{_PINK}◆{_RESET} ")
        else:
            parts.append("> ")
        parts.append(self._c(_PINK + _BOLD, "social-trends"))
        if context:
            mod = "*" if modified else ""
            parts.append(f" {self._c(_DARK_GRAY, '[')}")
            parts.append(self._c(_LIGHT_GRAY, f"{context}{mod}"))
            parts.append(self._c(_DARK_GRAY, ']'))
        parts.append(self._c(_GRAY, " ❯ "))
        return "".join(parts)

    def success(self, message: str):
        print(f"  {self._c(_GREEN + _BOLD, '✓')} {self._c(_GREEN, message)}")

    def error(self, message: str):
        print(f"  {self._c(_RED + _BOLD, '✗')} {self._c(_RED, message)}", file=sys.stderr)

    def warning(self, message: str):
        print(f"  {self._c(_YELLOW + _BOLD, '⚠')} {self._c(_YELLOW, message)}")

    def info(self, message: str):
        print(f"  {self._c(_BLUE, '●')} {self._c(_LIGHT_GRAY, message)}")

    def section(self, title: str):
        print()
        print(f"  {self._c(_PINK + _BOLD, title)}")
        print(f"  {self._c(_DARK_GRAY, _H_LINE * len(title))}")

    def status(self, label: str, value: str):
        lbl = self._c(_GRAY, f"  {label}:")
        val = self._c(_WHITE, f" {value}")
        print(f"{lbl}{val}")

    def table(self, headers: list, rows: list, max_col_width: int = 40):
        if not headers:
            return
        col_widths = [min(len(h), max_col_width) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = min(max(col_widths[i], len(str(cell))), max_col_width)

        def pad(text, width):
            t = str(text)[:width]
            return t + " " * (width - len(t))

        sep = self._c(_DARK_GRAY, f" {_V_LINE} ")
        header_cells = [self._c(_PINK + _BOLD, pad(h, col_widths[i])) for i, h in enumerate(headers)]
        print(f"  {sep.join(header_cells)}")
        print(f"  {self._c(_DARK_GRAY, '───'.join([_H_LINE * w for w in col_widths]))}")
        for row in rows:
            cells = []
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    cells.append(self._c(_LIGHT_GRAY, pad(str(cell), col_widths[i])))
            print(f"  {sep.join(cells)}")

    def print_goodbye(self):
        print(f"\n  {self._c(_GRAY, 'Stay trending. Goodbye!')}\n")

    def create_prompt_session(self):
        try:
            from prompt_toolkit import PromptSession
            from prompt_toolkit.history import FileHistory
            from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
            return PromptSession(
                history=FileHistory(self.history_file),
                auto_suggest=AutoSuggestFromHistory(),
                enable_history_search=True,
            )
        except ImportError:
            return None

    def get_input(self, pt_session, context: str = "", modified: bool = False) -> str:
        if pt_session is not None:
            return pt_session.prompt(self.prompt(context, modified)).strip()
        return input(self.prompt(context, modified)).strip()
