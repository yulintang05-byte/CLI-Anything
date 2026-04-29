"""Entry point for `python -m cli_anything.social_trends` and `cli-anything-social` command."""

import json
import sys
import click
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style

from .social_trends_cli import cli
from .utils.social_backend import get_env_status, load_session, save_session


_REPL_STYLE = Style.from_dict({"prompt": "ansicyan bold"})

_BANNER = """
╔══════════════════════════════════════════════════════════════╗
║          CLI-Anything Social Trends v1.0.0                   ║
║  YouTube & TikTok Scraper · Account Optimizer · Theme Pages  ║
╚══════════════════════════════════════════════════════════════╝

Commands:
  trends youtube/tiktok/combined  — scrape viral trends
  hashtags trending/analyze/research — hashtag intelligence
  music trending/recommend         — find trending sounds
  accounts audit/optimize/schedule/bio — account tools
  theme-pages niches/strategy/guide/compare/monetization

Type 'help' for all commands, 'env' to check API key status,
'exit' or Ctrl-D to quit.
"""


def main():
    """Main entry point. Runs REPL if no arguments provided, otherwise executes subcommand."""
    if len(sys.argv) > 1:
        cli()
    else:
        _run_repl()


def _run_repl():
    """Interactive REPL for Social Trends CLI."""
    session_state = load_session()
    click.echo(_BANNER)

    _print_env_status()

    history = InMemoryHistory()
    ps = PromptSession(history=history, auto_suggest=AutoSuggestFromHistory(), style=_REPL_STYLE)

    while True:
        try:
            prompt_text = f"social-trends ({session_state.primary_platform})> "
            raw = ps.prompt(prompt_text)
            line = raw.strip()
            if not line:
                continue
            if line in ("exit", "quit", "q"):
                click.echo("Goodbye.")
                save_session(session_state)
                break
            if line == "env":
                _print_env_status()
                continue
            if line in ("help", "?"):
                cli(["--help"], standalone_mode=False)
                continue
            argv = _tokenize(line)
            try:
                cli(argv, standalone_mode=False)
            except SystemExit:
                pass
            except Exception as exc:
                click.echo(f"Error: {exc}", err=True)
        except (KeyboardInterrupt, EOFError):
            click.echo("\nGoodbye.")
            save_session(session_state)
            break


def _print_env_status():
    status = get_env_status()
    missing = [k for k, v in status.items() if not v["set"]]
    if missing:
        click.echo("API keys not set (some features limited):")
        for k in missing:
            click.echo(f"  {k}: {status[k]['required_for']}")
            click.echo(f"         Get it at: {status[k]['how_to_get']}")
        click.echo("  TikTok web scraping works without credentials.\n")
    else:
        click.echo("All API keys configured.\n")


def _tokenize(line: str) -> list[str]:
    """Simple shell-like tokenizer that handles quoted strings."""
    import shlex
    try:
        return shlex.split(line)
    except ValueError:
        return line.split()


if __name__ == "__main__":
    main()
