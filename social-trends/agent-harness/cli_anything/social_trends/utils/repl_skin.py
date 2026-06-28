"""Social Trends - Unified REPL interface."""

import shlex
import sys
import click


def launch_repl(cli_group: click.Group, prog_name: str = "social-trends") -> None:
    """Launch an interactive REPL for the CLI."""
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import InMemoryHistory
        from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
        session = PromptSession(history=InMemoryHistory(), auto_suggest=AutoSuggestFromHistory())
        use_prompt_toolkit = True
    except ImportError:
        use_prompt_toolkit = False

    click.echo(f"Social Trends REPL. Type 'help' for commands, 'quit' to exit.")

    while True:
        try:
            if use_prompt_toolkit:
                line = session.prompt(f"{prog_name}> ")
            else:
                line = input(f"{prog_name}> ")
        except (EOFError, KeyboardInterrupt):
            click.echo("\nExiting.")
            break

        line = line.strip()
        if not line:
            continue
        if line.lower() in ("quit", "exit", "q"):
            break

        try:
            args = shlex.split(line)
        except ValueError as e:
            click.echo(f"Parse error: {e}", err=True)
            continue

        try:
            cli_group.main(args=args, prog_name=prog_name, standalone_mode=False)
        except SystemExit:
            pass
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
