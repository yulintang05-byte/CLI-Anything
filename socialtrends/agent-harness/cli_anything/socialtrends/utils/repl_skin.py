"""REPL UI utilities for socialtrends."""

import shutil


class ReplSkin:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    RED = "\033[31m"
    DIM = "\033[2m"

    def __init__(self, version: str = "1.0.0"):
        self.version = version
        self._width = shutil.get_terminal_size((80, 20)).columns

    def print_banner(self) -> None:
        print(f"{self.BOLD}{self.CYAN}")
        print("  ┌─────────────────────────────────────────────┐")
        print("  │   📈  SocialTrends — CLI-Anything v" + self.version + "   │")
        print("  │  YouTube · TikTok · Hashtags · Optimization │")
        print("  └─────────────────────────────────────────────┘")
        print(self.RESET)
        print(f"  {self.DIM}Type 'help' for commands, 'quit' to exit.{self.RESET}\n")

    def print_goodbye(self) -> None:
        print(f"\n{self.CYAN}Goodbye!{self.RESET}")

    def success(self, msg: str) -> None:
        print(f"  {self.GREEN}✓{self.RESET} {msg}")

    def error(self, msg: str) -> None:
        print(f"  {self.RED}✗{self.RESET} {msg}")

    def warn(self, msg: str) -> None:
        print(f"  {self.YELLOW}⚠{self.RESET} {msg}")

    def info(self, msg: str) -> None:
        print(f"  {self.CYAN}ℹ{self.RESET} {msg}")

    def table(self, headers: list[str], rows: list[list]) -> None:
        all_rows = [headers] + rows
        widths = [max(len(str(r[i])) for r in all_rows) for i in range(len(headers))]
        sep = "  +" + "+".join("-" * (w + 2) for w in widths) + "+"

        def row_str(row):
            return "  |" + "|".join(
                f" {str(cell):<{widths[i]}} " for i, cell in enumerate(row)
            ) + "|"

        print(sep)
        print(f"  {self.BOLD}" + row_str(headers) + self.RESET)
        print(sep)
        for row in rows:
            print(row_str(row))
        print(sep)

    def section(self, title: str) -> None:
        print(f"\n  {self.BOLD}{self.CYAN}{title}{self.RESET}")
        print("  " + "─" * min(len(title) + 2, self._width - 4))

    def bullet(self, items: list[str], symbol: str = "•") -> None:
        for item in items:
            print(f"    {self.CYAN}{symbol}{self.RESET} {item}")

    def help(self, commands: dict) -> None:
        self.section("Available Commands")
        max_k = max(len(k) for k in commands)
        for cmd, desc in commands.items():
            print(f"    {self.YELLOW}{cmd:<{max_k}}{self.RESET}  {self.DIM}{desc}{self.RESET}")
        print()

    def create_prompt_session(self):
        try:
            from prompt_toolkit import PromptSession
            from prompt_toolkit.history import InMemoryHistory
            return PromptSession(history=InMemoryHistory())
        except ImportError:
            return None

    def get_input(self, session, context: str = "", modified: bool = False) -> str:
        indicator = "*" if modified else ""
        prompt_str = f"socialtrends{('[' + context + indicator + ']') if context else ''}> "
        if session is not None:
            try:
                return session.prompt(prompt_str)
            except Exception:
                pass
        return input(prompt_str)
