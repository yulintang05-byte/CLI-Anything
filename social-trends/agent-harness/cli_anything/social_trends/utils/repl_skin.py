"""cli-anything REPL Skin for Social Trends.

Adapted from the shared cli-anything repl_skin with social-trends branding.
"""

import os
import re

_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"

_CYAN = "\033[38;5;80m"
_WHITE = "\033[97m"
_GRAY = "\033[38;5;245m"
_DARK_GRAY = "\033[38;5;240m"
_LIGHT_GRAY = "\033[38;5;250m"

# Social Trends accent: vibrant pink/magenta (social media feel)
_ACCENT = "\033[38;5;213m"

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

_ICON = f"{_ACCENT}{_BOLD}◆{_RESET}"
_ICON_SMALL = f"{_ACCENT}▸{_RESET}"


def _strip_ansi(text: str) -> str:
    return re.sub(r"\033\[[^m]*m", "", text)


def _visible_len(text: str) -> int:
    return len(_strip_ansi(text))


class ReplSkin:
    """REPL skin for Social Trends CLI harness."""

    def __init__(self, version: str = "1.0.0", history_file: str | None = None):
        self.version = version
        self._color = self._detect_color_support()

        if history_file is None:
            from pathlib import Path
            hist_dir = Path.home() / ".cli-anything-social-trends"
            hist_dir.mkdir(parents=True, exist_ok=True)
            self.history_file = str(hist_dir / "history")
        else:
            self.history_file = history_file

    def _detect_color_support(self) -> bool:
        if os.environ.get("NO_COLOR"):
            return False
        if os.environ.get("FORCE_COLOR"):
            return True
        return hasattr(os, "isatty") and os.isatty(1)

    def _c(self, code: str, text: str) -> str:
        if not self._color:
            return text
        return f"{code}{text}{_RESET}"

    def print_banner(self) -> None:
        w = 62
        lines = [
            "",
            self._c(_ACCENT + _BOLD, f"{'═' * w}"),
            self._c(_WHITE + _BOLD, f"  social-trends  v{self.version}".center(w)),
            self._c(_GRAY, "  Viral trend scraper + account optimizer".center(w)),
            self._c(_GRAY, "  YouTube · TikTok · Instagram".center(w)),
            self._c(_ACCENT + _BOLD, f"{'═' * w}"),
            "",
            self._c(_LIGHT_GRAY, "  Type 'help' for commands, 'quit' to exit."),
            self._c(_DIM, "  Tip: Run 'trends all' for a full trend report."),
            "",
        ]
        print("\n".join(lines))

    def create_prompt_session(self):
        try:
            from prompt_toolkit import PromptSession
            from prompt_toolkit.history import FileHistory
            return PromptSession(history=FileHistory(self.history_file))
        except ImportError:
            return None

    def get_input(self, pt_session, context: str = "", modified: bool = False) -> str:
        indicator = self._c(_YELLOW, "●") if modified else self._c(_ACCENT, "◆")
        ctx_label = self._c(_GRAY, f"[{context}] ") if context else ""
        prompt_str = f"{indicator} {ctx_label}{self._c(_ACCENT, '▸')} "

        if pt_session is not None:
            try:
                from prompt_toolkit.formatted_text import ANSI
                return pt_session.prompt(ANSI(prompt_str))
            except Exception:
                pass

        try:
            return input(prompt_str)
        except EOFError:
            raise

    def success(self, msg: str) -> None:
        print(self._c(_GREEN, f"  ✓ {msg}"))

    def error(self, msg: str) -> None:
        print(self._c(_RED, f"  ✗ Error: {msg}"))

    def info(self, msg: str) -> None:
        print(self._c(_BLUE, f"  ℹ {msg}"))

    def warn(self, msg: str) -> None:
        print(self._c(_YELLOW, f"  ⚠ {msg}"))

    def table(self, headers: list, rows: list) -> None:
        if not rows:
            print(self._c(_DIM, "    (no results)"))
            return

        col_count = len(headers)
        widths = [_visible_len(str(h)) for h in headers]
        for row in rows:
            for i, cell in enumerate(row[:col_count]):
                widths[i] = max(widths[i], _visible_len(str(cell)))

        # Cap column width to avoid wrapping
        max_col = 42
        widths = [min(w, max_col) for w in widths]

        def _cell(text: str, width: int) -> str:
            stripped = _strip_ansi(str(text))
            if len(stripped) > width:
                stripped = stripped[: width - 1] + "…"
            return stripped.ljust(width)

        sep_parts = [_H_LINE * (w + 2) for w in widths]
        top_line = _TL + ("┬".join(sep_parts)) + _TR
        mid_line = "├" + ("┼".join(sep_parts)) + "┤"
        bot_line = _BL + ("┴".join(sep_parts)) + _BR

        print(self._c(_DARK_GRAY, "  " + top_line))

        header_cells = [self._c(_BOLD + _CYAN, _cell(h, widths[i])) for i, h in enumerate(headers)]
        print("  " + self._c(_DARK_GRAY, _V_LINE) + " " + f" {self._c(_DARK_GRAY, _V_LINE)} ".join(header_cells) + " " + self._c(_DARK_GRAY, _V_LINE))
        print(self._c(_DARK_GRAY, "  " + mid_line))

        for row in rows:
            cells = [_cell(str(row[i]) if i < len(row) else "", widths[i]) for i in range(col_count)]
            print("  " + self._c(_DARK_GRAY, _V_LINE) + " " + f" {self._c(_DARK_GRAY, _V_LINE)} ".join(cells) + " " + self._c(_DARK_GRAY, _V_LINE))

        print(self._c(_DARK_GRAY, "  " + bot_line))

    def help(self, commands: dict) -> None:
        print()
        print(self._c(_BOLD + _WHITE, "  Available Commands:"))
        print()
        max_len = max(len(k) for k in commands)
        for cmd, desc in commands.items():
            cmd_str = self._c(_ACCENT, cmd.ljust(max_len))
            print(f"    {cmd_str}   {self._c(_GRAY, desc)}")
        print()

    def print_goodbye(self) -> None:
        print(self._c(_ACCENT, "\n  Later! Keep creating. 🔥\n"))
