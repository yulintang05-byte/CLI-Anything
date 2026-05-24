"""REPL skin for the social-trends CLI — interactive prompt with history."""

import json
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from pathlib import Path

HISTORY_FILE = Path.home() / ".cli-anything-social-trends" / ".repl_history"

COMMANDS = [
    "trends youtube", "trends tiktok", "trends compare",
    "hashtags research", "hashtags generate", "hashtags analyze",
    "music trending", "music search",
    "accounts optimize", "accounts schedule", "accounts audit",
    "theme-pages guide", "theme-pages monetize", "theme-pages calendar",
    "cache clear", "cache stats",
    "config set", "config show",
    "help", "exit", "quit",
]


def run_repl(dispatch_fn):
    """Run an interactive REPL for the social-trends CLI."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    session = PromptSession(
        history=FileHistory(str(HISTORY_FILE)),
        auto_suggest=AutoSuggestFromHistory(),
        completer=WordCompleter(COMMANDS, sentence=True),
    )

    print("Social Trends CLI — type 'help' for commands, 'exit' to quit")
    while True:
        try:
            line = session.prompt("social-trends> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break

        if not line:
            continue
        if line.lower() in ("exit", "quit"):
            print("Bye!")
            break

        parts = line.split()
        result = dispatch_fn(parts)
        if result is not None:
            print(json.dumps(result, indent=2, ensure_ascii=False))
