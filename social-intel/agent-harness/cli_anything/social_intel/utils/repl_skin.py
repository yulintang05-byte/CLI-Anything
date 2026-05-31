"""REPL skin matching CLI-Anything house style."""

from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML

STYLE = Style.from_dict({
    "prompt":   "#ansigreen bold",
    "tool":     "#ansiyellow bold",
    "rprompt":  "#ansiblue",
})


class ReplSkin:
    def __init__(self, tool_name: str, version: str = "1.0.0"):
        self.tool_name = tool_name
        self.version = version

    def print_banner(self) -> None:
        print(f"\n  social-intel {self.version}  |  {self.tool_name}")
        print("  Social media intelligence — YouTube & TikTok")
        print("  Type 'help' for commands, 'quit' to exit.\n")

    def create_prompt_session(self) -> PromptSession:
        return PromptSession(history=InMemoryHistory(), style=STYLE)

    def get_input(self, session: PromptSession, context: str = "") -> str:
        ctx = f" ({context})" if context else ""
        prompt_text = HTML(f"<prompt>social-intel{ctx}</prompt> <tool>▶</tool> ")
        return session.prompt(prompt_text).strip()

    def success(self, msg: str) -> None:
        print(f"  \033[32m✓\033[0m  {msg}")

    def warning(self, msg: str) -> None:
        print(f"  \033[33m!\033[0m  {msg}")

    def error(self, msg: str) -> None:
        print(f"  \033[31m✗\033[0m  {msg}")

    def info(self, msg: str) -> None:
        print(f"  \033[36mℹ\033[0m  {msg}")

    def help(self, commands: dict) -> None:
        print("\n  Commands:")
        for cmd, desc in commands.items():
            print(f"    {cmd:<18} {desc}")
        print()

    def print_goodbye(self) -> None:
        print("\n  Bye!\n")
