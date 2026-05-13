"""REPL skin — banner, prompt, table renderer, color helpers."""

import click
from typing import Optional
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style

_BANNER = r"""
  ____  __  ___  _      _    ___ ___ ___ _  _ ___  ___
 / ___||  \/  | | |    | |  / __| __| __| \| |   \/ __|
 \__ \ | |\/| | | |__  | |  \__ \ _|| _||  ` | |) \__ \
 |___/ |_|  |_| |____| |_|  |___/___|___|_|\_|___/|___/
         Social Media Trend Intelligence v1.0.0
"""

_STYLE = Style.from_dict({
    "prompt": "bold #00d4ff",
    "niche": "bold #ff6b6b",
})


class ReplSkin:
    def __init__(self, version: str = "1.0.0") -> None:
        self.version = version

    def print_banner(self) -> None:
        click.echo(click.style(_BANNER, fg="cyan"))
        click.echo(click.style("  Viral trends, hashtag strategy & theme page playbook", fg="bright_white"))
        click.echo(click.style("  Type 'help' for commands, 'quit' to exit\n", fg="bright_black"))

    def success(self, msg: str) -> None:
        click.echo(click.style(f"  ✓ {msg}", fg="green"))

    def error(self, msg: str) -> None:
        click.echo(click.style(f"  ✗ {msg}", fg="red"), err=True)

    def info(self, msg: str) -> None:
        click.echo(click.style(f"  ℹ {msg}", fg="cyan"))

    def warn(self, msg: str) -> None:
        click.echo(click.style(f"  ⚠ {msg}", fg="yellow"))

    def print_goodbye(self) -> None:
        click.echo(click.style("\n  Go viral. 🚀\n", fg="cyan"))

    def table(self, headers: list, rows: list, max_col_width: int = 40) -> None:
        if not rows:
            click.echo("  (no results)")
            return

        widths = [max(len(str(h)), max(len(str(r[i])[:max_col_width]) for r in rows))
                  for i, h in enumerate(headers)]

        separator = "  +" + "+".join("-" * (w + 2) for w in widths) + "+"
        header_row = "  |" + "|".join(f" {str(h):<{w}} " for h, w in zip(headers, widths)) + "|"

        click.echo(click.style(separator, fg="bright_black"))
        click.echo(click.style(header_row, fg="bright_white", bold=True))
        click.echo(click.style(separator, fg="bright_black"))

        for row in rows:
            cells = [str(row[i])[:max_col_width] if i < len(row) else "" for i in range(len(headers))]
            data_row = "  |" + "|".join(f" {c:<{w}} " for c, w in zip(cells, widths)) + "|"
            click.echo(data_row)

        click.echo(click.style(separator, fg="bright_black"))

    def help(self, commands: dict) -> None:
        click.echo(click.style("\n  Available Commands:", fg="bright_white", bold=True))
        click.echo()
        for cmd, desc in commands.items():
            click.echo(f"  {click.style(cmd, fg='cyan'):<45} {desc}")
        click.echo()

    def create_prompt_session(self) -> PromptSession:
        return PromptSession(style=_STYLE)

    def get_input(self, pt_session: PromptSession, niche: str = "", modified: bool = False) -> str:
        niche_str = f" ({niche})" if niche else ""
        prompt_text = [
            ("class:prompt", f"social-trends{niche_str}"),
            ("", " > "),
        ]
        return pt_session.prompt(prompt_text).strip()
