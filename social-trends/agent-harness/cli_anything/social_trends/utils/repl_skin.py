"""cli-anything REPL Skin — copy of the shared skin with social_trends accent."""

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

_ACCENT_COLORS = {
    "social_trends": "\033[38;5;213m",  # hot pink / viral
}
_DEFAULT_ACCENT = "\033[38;5;213m"

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


def _strip_ansi(text: str) -> str:
    return re.sub(r"\033\[[^m]*m", "", text)


def _visible_len(text: str) -> int:
    return len(_strip_ansi(text))


class ReplSkin:
    def __init__(self, software: str, version: str = "1.0.0", history_file=None):
        self.software = software.lower().replace("-", "_")
        self.display_name = software.replace("_", " ").title()
        self.version = version
        self.accent = _ACCENT_COLORS.get(self.software, _DEFAULT_ACCENT)
        self._color = self._detect_color()

    def _detect_color(self) -> bool:
        if os.environ.get("NO_COLOR"):
            return False
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    def _c(self, code: str, text: str) -> str:
        return f"{code}{text}{_RESET}" if self._color else text

    def print_banner(self):
        inner = 54

        def box_line(content: str) -> str:
            pad = inner - _visible_len(content)
            vl = self._c(_DARK_GRAY, _V_LINE)
            return f"{vl}{content}{' ' * max(0, pad)}{vl}"

        top = self._c(_DARK_GRAY, f"{_TL}{_H_LINE * inner}{_TR}")
        bot = self._c(_DARK_GRAY, f"{_BL}{_H_LINE * inner}{_BR}")
        icon = self._c(_CYAN + _BOLD, "◆")
        brand = self._c(_CYAN + _BOLD, "cli-anything")
        dot = self._c(_DARK_GRAY, "·")
        name = self._c(self.accent + _BOLD, self.display_name)
        title = f" {icon}  {brand} {dot} {name}"
        ver = f" {self._c(_DARK_GRAY, f'   v{self.version}')}"
        tip = f" {self._c(_DARK_GRAY, '   Type help for commands, quit to exit')}"

        print(top)
        print(box_line(title))
        print(box_line(ver))
        print(box_line(""))
        print(box_line(tip))
        print(bot)
        print()

    def prompt(self, project_name: str = "", modified: bool = False, context: str = "") -> str:
        parts = []
        parts.append(self._c(_CYAN, "◆") + " " if self._color else "> ")
        parts.append(self._c(self.accent + _BOLD, self.software))
        if project_name or context:
            ctx = context or project_name
            mod = "*" if modified else ""
            parts.append(f" {self._c(_DARK_GRAY, '[')}")
            parts.append(self._c(_LIGHT_GRAY, f"{ctx}{mod}"))
            parts.append(self._c(_DARK_GRAY, "]"))
        parts.append(self._c(_GRAY, " ❯ "))
        return "".join(parts)

    def success(self, msg: str):
        print(f"  {self._c(_GREEN, '✓')} {msg}")

    def error(self, msg: str):
        print(f"  {self._c(_RED, '✗')} {msg}", file=sys.stderr)

    def warning(self, msg: str):
        print(f"  {self._c(_YELLOW, '!')} {msg}")

    def info(self, msg: str):
        print(f"  {self._c(_BLUE, '→')} {msg}")

    def print_goodbye(self):
        print(f"\n  {self._c(_CYAN + _BOLD, '◆')} Goodbye!\n")
