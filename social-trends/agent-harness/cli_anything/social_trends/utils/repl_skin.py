"""Unified REPL skin for social-trends CLI."""

from prompt_toolkit import prompt as pt_prompt
from prompt_toolkit.styles import Style

STYLE = Style.from_dict({
    "prompt": "bold #ff6b6b",
    "": "#ffffff",
})

BANNER = r"""
  ___              _      _   _____                       _
 / __| ___  __  __(_) __ | | |_   _| _ ___  _ _   __| |___
 \__ \/ _ \/ _|/ _|| |/ _` |   | || '_/ -_)| ' \ / _` (_-<
 |___/\___/\__|\__||_|\__,_|   |_||_| \___||_||_|\__,_/__/

  YouTube • TikTok • Account Optimizer • Theme Pages
  Type 'help' for commands. Type 'exit' to quit.
"""

HELP_TEXT = """
Available commands:

  YOUTUBE TRENDS
    yt trends [--region US] [--max 50]       Fetch trending YouTube videos
    yt hashtags [--region US]                Extract trending hashtags from YouTube
    yt music [--region US] [--max 25]        Fetch trending music/audio
    yt niche <query> [--max 25]              Search trending videos in a niche
    yt analyze [--region US]                 Full YouTube trend analysis

  TIKTOK TRENDS
    tt trends [--region US] [--max 30]       Fetch trending TikTok videos
    tt hashtags [--region US]                Extract trending TikTok hashtags
    tt sounds [--region US]                  Extract trending TikTok sounds/music
    tt analyze [--region US]                 Full TikTok trend analysis
    tt hashtag-info <#tag>                   Get stats for a specific hashtag

  ACCOUNT OPTIMIZER
    account add <platform> <username>        Register an account to track
    account audit <platform> <username>      Audit and score an account
    account schedule <platform> [--tz EST]   Generate optimal posting schedule
    account hashtags <niche> <platform>      Build tiered hashtag strategy
    account calendar <niche> <platform>      Generate 4-week content calendar
    account bio <niche> <platform>           Generate optimized bio templates
    account list                             List all registered accounts

  THEME PAGES
    theme niche <name>                       Get starter kit for a niche
    theme niches                             List all available niches with scores
    theme compare <n1> <n2> [n3...]          Compare niches side-by-side
    theme playbook [phase]                   View theme page growth playbook
    theme revenue <platform> <followers>     Estimate monthly revenue
    theme strategy <conversion_type>         Get a specific conversion strategy

  SESSION
    config set <key> <value>                 Set an API key or config value
    config show                              Show current config (keys redacted)
    cache clear                              Clear cached trend data
    history                                  Show command history

  OUTPUT
    --json                                   Output as JSON (pass to any command)
    --save <file.json>                       Save output to file

  help                                       Show this help
  exit / quit                                Exit REPL
"""


def print_banner() -> None:
    print(BANNER)


def print_help() -> None:
    print(HELP_TEXT)


def repl_prompt(session_info: str = "") -> str:
    label = f"[social-trends{':' + session_info if session_info else ''}]> "
    try:
        return pt_prompt(label, style=STYLE)
    except (ImportError, Exception):
        return input(label)
