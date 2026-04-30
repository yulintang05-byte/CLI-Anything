"""REPL skin for social-media CLI — prompt-toolkit based interactive shell."""

from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML


_BRAND_COLOR = "ansimagenta"
_ACCENT_COLOR = "ansicyan"

_STYLE = Style.from_dict({
    "brand": "bold ansimagenta",
    "prompt": "ansicyan",
    "account": "ansigreen",
    "modified": "ansiyellow",
    "separator": "ansigray",
})

_BANNER = """\
╔══════════════════════════════════════════════════════════╗
║  📱  Social Media CLI  v1.0.0                           ║
║  Viral Trends · Hashtags · Music · Account Optimizer    ║
╚══════════════════════════════════════════════════════════╝
Type 'help' for commands, 'quit' to exit.
"""


class ReplSkin:
    def __init__(self, app_name: str = "social-media", version: str = "1.0.0"):
        self.app_name = app_name
        self.version = version

    def print_banner(self):
        print(_BANNER)

    def create_prompt_session(self) -> PromptSession:
        return PromptSession(history=InMemoryHistory(), style=_STYLE)

    def get_input(
        self,
        session: PromptSession,
        account_name: str = "",
        modified: bool = False,
    ) -> str:
        account_part = f"[{account_name}]" if account_name else ""
        mod_part = "*" if modified else ""
        prompt_str = f"social-media{account_part}{mod_part}> "
        try:
            return session.prompt(HTML(f"<prompt>{prompt_str}</prompt>"), style=_STYLE).strip()
        except (EOFError, KeyboardInterrupt):
            raise

    def print_goodbye(self):
        print("\nGoodbye! Keep creating viral content. 🚀")

    def error(self, message: str):
        print(f"Error: {message}")

    def info(self, message: str):
        print(f"  {message}")

    def help(self, commands: dict):
        print("\nAvailable Commands:")
        print("-" * 60)
        for cmd, desc in commands.items():
            print(f"  {cmd:<45} {desc}")
        print()
