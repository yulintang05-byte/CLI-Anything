"""cli-anything REPL Skin for TrendScout.

Adapted from the shared cli-anything repl_skin.py with TrendScout branding.
"""

import os
import sys
import re

_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"

_CYAN = "\033[38;5;80m"
_WHITE = "\033[97m"
_GRAY = "\033[38;5;245m"
_DARK_GRAY = "\033[38;5;240m"
_LIGHT_GRAY = "\033[38;5;250m"

# TrendScout accent: electric violet (trend/viral feel)
_ACCENT = "\033[38;5;141m"

_GREEN = "\033[38;5;78m"
_YELLOW = "\033[38;5;220m"
_RED = "\033[38;5;196m"
_BLUE = "\033[38;5;75m"

_H_LINE = "─"
_V_LINE = "│"
_TL = "╭"
_TR = "╮"
_BL = "╰"
_BR = "╯"

_ICON = f"{_CYAN}{_BOLD}◆{_RESET}"
_ICON_SMALL = f"{_CYAN}▸{_RESET}"


def _strip_ansi(text: str) -> str:
    return re.sub(r"\033\[[^m]*m", "", text)


def _visible_len(text: str) -> int:
    return len(_strip_ansi(text))


class ReplSkin:
    """REPL skin for the TrendScout CLI harness."""

    def __init__(self, version: str = "1.0.0", history_file: str | None = None):
        self.version = version
        self._color = self._detect_color_support()

        if history_file is None:
            from pathlib import Path
            hist_dir = Path.home() / ".cli-anything-trendscout"
            hist_dir.mkdir(parents=True, exist_ok=True)
            self.history_file = str(hist_dir / "history")
        else:
            self.history_file = history_file

    def _detect_color_support(self) -> bool:
        if os.environ.get("NO_COLOR"):
            return False
        if os.environ.get("CLI_ANYTHING_NO_COLOR"):
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

        def _box_line(content: str) -> str:
            pad = inner - _visible_len(content)
            vl = self._c(_DARK_GRAY, _V_LINE)
            return f"{vl}{content}{' ' * max(0, pad)}{vl}"

        top = self._c(_DARK_GRAY, f"{_TL}{_H_LINE * inner}{_TR}")
        bot = self._c(_DARK_GRAY, f"{_BL}{_H_LINE * inner}{_BR}")

        icon = self._c(_CYAN + _BOLD, "◆")
        brand = self._c(_CYAN + _BOLD, "cli-anything")
        dot = self._c(_DARK_GRAY, "·")
        name = self._c(_ACCENT + _BOLD, "TrendScout")
        title = f" {icon}  {brand} {dot} {name}"

        ver = f" {self._c(_DARK_GRAY, f'   v{self.version}')}"
        tip = f" {self._c(_DARK_GRAY, '   Type help for commands, quit to exit')}"
        empty = ""

        print(top)
        print(_box_line(title))
        print(_box_line(ver))
        print(_box_line(empty))
        print(_box_line(tip))
        print(bot)
        print()

    def prompt(self, context: str = "", modified: bool = False) -> str:
        parts = []
        if self._color:
            parts.append(f"{_CYAN}◆{_RESET} ")
        else:
            parts.append("> ")

        parts.append(self._c(_ACCENT + _BOLD, "trendscout"))

        if context:
            parts.append(f" {self._c(_DARK_GRAY, '[')}")
            parts.append(self._c(_LIGHT_GRAY, context))
            parts.append(self._c(_DARK_GRAY, ']'))

        parts.append(self._c(_GRAY, " ❯ "))
        return "".join(parts)

    def prompt_tokens(self, context: str = "", modified: bool = False):
        tokens = [("class:icon", "◆ "), ("class:software", "trendscout")]
        if context:
            tokens += [
                ("class:bracket", " ["),
                ("class:context", context),
                ("class:bracket", "]"),
            ]
        tokens.append(("class:arrow", " ❯ "))
        return tokens

    def get_prompt_style(self):
        try:
            from prompt_toolkit.styles import Style
        except ImportError:
            return None
        return Style.from_dict({
            "icon": "#5fdfdf bold",
            "software": "#af87ff bold",
            "bracket": "#585858",
            "context": "#bcbcbc",
            "arrow": "#808080",
            "completion-menu.completion": "bg:#303030 #bcbcbc",
            "completion-menu.completion.current": "bg:#af87ff #000000",
            "auto-suggest": "#585858",
        })

    def success(self, message: str):
        print(f"  {self._c(_GREEN + _BOLD, '✓')} {self._c(_GREEN, message)}")

    def error(self, message: str):
        print(f"  {self._c(_RED + _BOLD, '✗')} {self._c(_RED, message)}", file=sys.stderr)

    def warning(self, message: str):
        print(f"  {self._c(_YELLOW + _BOLD, '⚠')} {self._c(_YELLOW, message)}")

    def info(self, message: str):
        print(f"  {self._c(_BLUE, '●')} {self._c(_LIGHT_GRAY, message)}")

    def hint(self, message: str):
        print(f"  {self._c(_DARK_GRAY, message)}")

    def section(self, title: str):
        print()
        print(f"  {self._c(_ACCENT + _BOLD, title)}")
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

        def pad(text: str, width: int) -> str:
            t = str(text)[:width]
            return t + " " * (width - len(t))

        header_cells = [
            self._c(_CYAN + _BOLD, pad(h, col_widths[i]))
            for i, h in enumerate(headers)
        ]
        sep = self._c(_DARK_GRAY, f" {_V_LINE} ")
        print(f"  {sep.join(header_cells)}")
        print(self._c(_DARK_GRAY, f"  {'───'.join([_H_LINE * w for w in col_widths])}"))
        for row in rows:
            cells = [
                self._c(_LIGHT_GRAY, pad(str(row[i]) if i < len(row) else "", col_widths[i]))
                for i in range(len(col_widths))
            ]
            print(f"  {sep.join(cells)}")

    def help(self, commands: dict):
        self.section("Commands")
        max_cmd = max(len(c) for c in commands) if commands else 0
        for cmd, desc in commands.items():
            print(
                f"{self._c(_ACCENT, f'  {cmd:<{max_cmd}}')}  "
                f"{self._c(_GRAY, desc)}"
            )
        print()

    def print_goodbye(self):
        print(f"\n  {_ICON_SMALL} {self._c(_GRAY, 'Goodbye!')}\n")

    def create_prompt_session(self):
        try:
            from prompt_toolkit import PromptSession
            from prompt_toolkit.history import FileHistory
            from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
            return PromptSession(
                history=FileHistory(self.history_file),
                auto_suggest=AutoSuggestFromHistory(),
                style=self.get_prompt_style(),
                enable_history_search=True,
            )
        except ImportError:
            return None

    def get_input(self, pt_session, context: str = "", modified: bool = False) -> str:
        if pt_session is not None:
            from prompt_toolkit.formatted_text import FormattedText
            tokens = self.prompt_tokens(context, modified)
            return pt_session.prompt(FormattedText(tokens)).strip()
        return input(self.prompt(context, modified)).strip()
