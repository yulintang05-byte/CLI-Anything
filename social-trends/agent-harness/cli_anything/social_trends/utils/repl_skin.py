"""Repl skin stub — falls back to prompt-toolkit if available, else bare input."""

from __future__ import annotations

import click

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.styles import Style
    _HAS_PT = True
except ImportError:
    _HAS_PT = False


class ReplSkin:
    def __init__(self, app_name: str, version: str = "1.0.0"):
        self.app_name = app_name
        self.version = version

    def print_banner(self):
        click.echo(f"\n  cli-anything-{self.app_name} v{self.version}")
        click.echo(f"  Type 'help' for commands, 'quit' to exit.\n")

    def print_goodbye(self):
        click.echo(f"\nGoodbye from {self.app_name}!")

    def create_prompt_session(self):
        if _HAS_PT:
            style = Style.from_dict({"prompt": "ansicyan bold"})
            return PromptSession(style=style)
        return None

    def get_input(self, session, context: str = "") -> str:
        prompt_str = f"{self.app_name}> "
        if _HAS_PT and session:
            try:
                return session.prompt(prompt_str).strip()
            except (EOFError, KeyboardInterrupt):
                raise
        return input(prompt_str).strip()

    def help(self, commands: dict):
        click.echo("\nAvailable commands:")
        for cmd, desc in commands.items():
            click.echo(f"  {cmd:<55} {desc}")
        click.echo()

    def error(self, msg: str):
        click.echo(f"Error: {msg}", err=True)
