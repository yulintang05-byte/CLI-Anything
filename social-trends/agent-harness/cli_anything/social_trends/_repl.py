#!/usr/bin/env python3
"""Interactive REPL for the Social Trends CLI."""

import sys
import json
import click

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    _PT_AVAILABLE = True
except ImportError:
    _PT_AVAILABLE = False

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║         Social Trends CLI — Interactive Mode                 ║
║  Scrape trends · Optimize accounts · Build theme pages       ║
╚══════════════════════════════════════════════════════════════╝
Type 'help' for commands, 'quit' to exit.
"""

HELP_TEXT = """
TREND COMMANDS
  trends yt [--region US] [--limit 20]      Scrape YouTube trending
  trends tt [--region US] [--limit 20]      Scrape TikTok trending
  trends hashtags <platform> [niche]        Trending hashtags
  trends sounds [--region US]               Trending TikTok sounds
  trends report [--region US]               Merged cross-platform report

ACCOUNT COMMANDS
  account optimize <platform> <username> [options]
    Options: --followers N --avg-views N --niche X --freq N
  account schedule <platform> [--niche X]   Optimal posting schedule

THEME PAGE COMMANDS
  theme guide [--section X]                 Full playbook
  theme niches [--sort X] [--search X]      Browse niches
  theme detail <niche_key>                  Full niche details
  theme quickstart [--niche X] [--followers N]
  theme calendar [--niche X] [--days 7|30]  Generate content calendar

GENERAL
  json on/off       Toggle JSON output mode
  help              Show this help
  quit / exit       Exit REPL
"""


def run_repl(json_mode: bool = False):
    """Run the interactive REPL loop."""
    click.echo(BANNER)

    _json = [json_mode]

    if _PT_AVAILABLE:
        session = PromptSession(
            history=InMemoryHistory(),
            auto_suggest=AutoSuggestFromHistory(),
        )
        def get_input():
            return session.prompt("social-trends> ")
    else:
        def get_input():
            return input("social-trends> ")

    while True:
        try:
            line = get_input().strip()
        except (KeyboardInterrupt, EOFError):
            click.echo("\nGoodbye!")
            break

        if not line:
            continue

        parts = line.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in ("quit", "exit"):
            click.echo("Goodbye!")
            break

        elif cmd == "help":
            click.echo(HELP_TEXT)

        elif cmd == "json":
            if args and args[0].lower() == "on":
                _json[0] = True
                click.echo("JSON output: ON")
            elif args and args[0].lower() == "off":
                _json[0] = False
                click.echo("JSON output: OFF")
            else:
                click.echo(f"JSON output is {'ON' if _json[0] else 'OFF'}")

        elif cmd == "trends":
            _handle_trends(args, _json[0])

        elif cmd == "account":
            _handle_account(args, _json[0])

        elif cmd == "theme":
            _handle_theme(args, _json[0])

        else:
            click.echo(f"Unknown command: {cmd}. Type 'help' for available commands.")


def _out(data, _json: bool):
    if _json:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        _pp(data)


def _pp(data, indent=0):
    prefix = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{prefix}{k.replace('_', ' ').title()}:")
                _pp(v, indent + 1)
            else:
                click.echo(f"{prefix}{k.replace('_', ' ').title()}: {v}")
    elif isinstance(data, list):
        for item in data[:20]:
            if isinstance(item, dict):
                _pp(item, indent)
                click.echo(f"{prefix}---")
            else:
                click.echo(f"{prefix}- {item}")
        if len(data) > 20:
            click.echo(f"{prefix}... and {len(data) - 20} more")
    else:
        click.echo(f"{prefix}{data}")


def _parse_flags(args: list[str]) -> dict:
    """Parse --key value pairs from a list of args."""
    flags = {}
    i = 0
    while i < len(args):
        if args[i].startswith("--") and i + 1 < len(args):
            key = args[i][2:].replace("-", "_")
            flags[key] = args[i + 1]
            i += 2
        else:
            i += 1
    return flags


def _handle_trends(args: list[str], json_mode: bool):
    from cli_anything.social_trends.scrapers import youtube as yt
    from cli_anything.social_trends.scrapers import tiktok as tt
    from cli_anything.social_trends.core.trends import merge_platform_trends

    if not args:
        click.echo("Usage: trends <yt|tt|hashtags|sounds|report>")
        return

    sub = args[0].lower()
    flags = _parse_flags(args[1:])
    region = flags.get("region", "US")
    limit = int(flags.get("limit", 15))

    try:
        if sub == "yt":
            click.echo(f"Scraping YouTube trending ({region})...")
            result = yt.scrape_trending(region=region, limit=limit)
            _out(result, json_mode)
        elif sub == "tt":
            click.echo(f"Scraping TikTok trending ({region})...")
            result = tt.scrape_trending(region=region, limit=limit)
            _out(result, json_mode)
        elif sub == "hashtags":
            platform = args[1] if len(args) > 1 else "tiktok"
            niche = flags.get("niche")
            if platform == "tiktok":
                result = tt.get_trending_hashtags(region=region, limit=limit)
            else:
                if niche:
                    result = yt.get_top_hashtags_for_niche(niche, limit=limit)
                else:
                    click.echo("For YouTube, specify --niche <topic>")
                    return
            _out(result, json_mode)
        elif sub == "sounds":
            click.echo(f"Fetching TikTok trending sounds ({region})...")
            result = tt.get_trending_sounds(region=region, limit=limit)
            _out(result, json_mode)
        elif sub == "report":
            click.echo("Scraping both platforms...")
            yt_data = tt_data = None
            try:
                yt_data = yt.scrape_trending(region=region, limit=limit)
            except Exception as e:
                click.echo(f"YouTube failed: {e}")
            try:
                tt_data = tt.scrape_trending(region=region, limit=limit)
            except Exception as e:
                click.echo(f"TikTok failed: {e}")
            report = merge_platform_trends(yt_data, tt_data, region=region)
            _out(report.to_dict(), json_mode)
        else:
            click.echo(f"Unknown trends subcommand: {sub}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


def _handle_account(args: list[str], json_mode: bool):
    from cli_anything.social_trends.optimizer.account import analyze_account, _optimal_posting_schedule

    if not args:
        click.echo("Usage: account <optimize|schedule>")
        return

    sub = args[0].lower()
    flags = _parse_flags(args[1:])

    try:
        if sub == "optimize":
            platform = args[1] if len(args) > 1 else flags.get("platform", "tiktok")
            username = args[2] if len(args) > 2 else flags.get("username", "unknown")
            profile = {
                "platform": platform,
                "username": username,
                "follower_count": int(flags.get("followers", 0)),
                "avg_views": int(flags.get("avg_views", 0)),
                "avg_likes": int(flags.get("avg_likes", 0)),
                "avg_comments": int(flags.get("avg_comments", 0)),
                "niche": flags.get("niche", ""),
                "posting_frequency_per_week": float(flags.get("freq", 0)),
                "bio": flags.get("bio", ""),
                "has_link_in_bio": "has_link" in flags,
                "profile_pic_set": True,
            }
            result = analyze_account(profile)
            _out(result, json_mode)
        elif sub == "schedule":
            platform = args[1] if len(args) > 1 else "tiktok"
            niche = flags.get("niche", "general")
            result = _optimal_posting_schedule(platform, niche)
            _out(result, json_mode)
        else:
            click.echo(f"Unknown account subcommand: {sub}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


def _handle_theme(args: list[str], json_mode: bool):
    from cli_anything.social_trends.theme_pages import guide as gd
    from cli_anything.social_trends.theme_pages import niches as nd
    from cli_anything.social_trends.theme_pages.content_calendar import (
        generate_weekly_calendar, generate_monthly_calendar
    )

    if not args:
        click.echo("Usage: theme <guide|niches|detail|quickstart|calendar>")
        return

    sub = args[0].lower()
    flags = _parse_flags(args[1:])

    try:
        if sub == "guide":
            section = flags.get("section") or (args[1] if len(args) > 1 else None)
            if section:
                result = gd.get_section(section)
            else:
                result = gd.get_full_playbook()
            _out(result, json_mode)
        elif sub == "niches":
            sort_by = flags.get("sort", "conversion_potential")
            search = flags.get("search")
            if search:
                result = nd.search_niches(search)
            else:
                result = nd.list_niches(sort_by=sort_by)
            _out(result, json_mode)
        elif sub == "detail":
            key = args[1] if len(args) > 1 else ""
            result = nd.get_niche(key)
            if not result:
                click.echo(f"Niche '{key}' not found.")
                return
            _out(result, json_mode)
        elif sub == "quickstart":
            niche = flags.get("niche", "general")
            followers = int(flags.get("followers", 0))
            platform = flags.get("platform", "tiktok")
            result = {
                "quick_start": gd.get_quick_start(niche),
                "conversion_strategy": gd.get_conversion_guide(followers, platform),
            }
            _out(result, json_mode)
        elif sub == "calendar":
            niche = flags.get("niche", "general")
            days = flags.get("days", "7")
            platforms_str = flags.get("platforms", "tiktok,youtube")
            platform_list = [p.strip() for p in platforms_str.split(",")]
            ppd = int(flags.get("posts_per_day", 2))
            if days == "30":
                result = generate_monthly_calendar(niche=niche, platforms=platform_list, posts_per_day=ppd)
            else:
                result = generate_weekly_calendar(niche=niche, platforms=platform_list, posts_per_day=ppd)
            _out(result, json_mode)
        else:
            click.echo(f"Unknown theme subcommand: {sub}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
