"""cli-anything REPL Skin — adapted for social-trends harness."""

import os
import sys

_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_CYAN = "\033[38;5;80m"
_WHITE = "\033[97m"
_GRAY = "\033[38;5;245m"
_DARK_GRAY = "\033[38;5;240m"
_ACCENT = "\033[38;5;213m"   # pink-purple for social media
_GREEN = "\033[38;5;78m"
_YELLOW = "\033[38;5;220m"
_RED = "\033[38;5;196m"
_BLUE = "\033[38;5;75m"
_MAGENTA = "\033[38;5;176m"

_SUPPORTS_COLOR = (
    hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    and os.environ.get("TERM") != "dumb"
    and os.environ.get("NO_COLOR") is None
)


def _c(code: str, text: str) -> str:
    return f"{code}{text}{_RESET}" if _SUPPORTS_COLOR else text


class ReplSkin:
    def __init__(self, name: str = "social-trends", version: str = "1.0.0"):
        self.name = name
        self.version = version

    def print_banner(self):
        width = 60
        border = _c(_ACCENT + _BOLD, "━" * width)
        print(f"\n{border}")
        print(_c(_BOLD + _WHITE, f"  cli-anything — {self.name}") + _c(_DIM + _GRAY, f" v{self.version}"))
        print(_c(_GRAY, "  TikTok + YouTube trend scraping & account optimization"))
        print(f"{border}\n")

    def print_goodbye(self):
        print(_c(_DIM + _GRAY, "\n  Goodbye! Go viral. 🔥\n"))

    def prompt(self, context: str = "", modified: bool = False) -> str:
        mark = _c(_YELLOW, "*") if modified else ""
        ctx = _c(_DIM + _GRAY, f" [{context}]") if context else ""
        arrow = _c(_ACCENT + _BOLD, "▶")
        return f"{mark}{arrow}{ctx} "

    def success(self, msg: str):
        print(f"  {_c(_GREEN, '✓')} {msg}")

    def error(self, msg: str):
        print(f"  {_c(_RED, '✗')} {msg}", file=sys.stderr)

    def warning(self, msg: str):
        print(f"  {_c(_YELLOW, '⚠')} {msg}")

    def info(self, msg: str):
        print(f"  {_c(_BLUE, '→')} {msg}")

    def status(self, label: str, value: str):
        print(f"  {_c(_GRAY, label + ':')} {_c(_WHITE, value)}")

    def header(self, title: str):
        print(f"\n{_c(_BOLD + _ACCENT, title)}")
        print(_c(_DIM + _GRAY, "─" * min(len(title) + 4, 60)))

    def table(self, headers: list[str], rows: list[list], max_col_width: int = 40):
        widths = [len(h) for h in headers]
        str_rows = []
        for row in rows:
            str_row = [str(v)[:max_col_width] for v in row]
            for i, cell in enumerate(str_row):
                if i < len(widths):
                    widths[i] = max(widths[i], len(cell))
            str_rows.append(str_row)

        header_line = "  " + "  ".join(
            _c(_BOLD + _CYAN, h.ljust(widths[i])) for i, h in enumerate(headers)
        )
        sep = "  " + _c(_DARK_GRAY, "─" * (sum(widths) + 2 * len(widths)))
        print(header_line)
        print(sep)
        for row in str_rows:
            cells = "  ".join(
                cell.ljust(widths[i]) for i, cell in enumerate(row) if i < len(widths)
            )
            print(f"  {cells}")
        print()
