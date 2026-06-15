#!/usr/bin/env python3
"""YouTube CLI — Trending videos, hashtags, music discovery & channel optimization.

This CLI wraps the YouTube Data API v3. It covers trending content discovery,
hashtag research, music discovery for Shorts/Reels, channel auditing, and
SEO/monetization strategy.

Usage:
    # Setup API key
    cli-anything-youtube auth setup --api-key <KEY>

    # Check trending videos (US)
    cli-anything-youtube trends videos --region US --limit 10

    # Search by hashtag
    cli-anything-youtube trends hashtag trending --limit 20

    # Audit a channel
    cli-anything-youtube channel audit @MrBeast

    # Interactive REPL
    cli-anything-youtube repl
"""

import sys
import os
import json
import click
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.youtube.core import account as account_mod
from cli_anything.youtube.core import trends as trends_mod
from cli_anything.youtube.core import strategy as strategy_mod

# Global state
_json_output = False
_repl_mode = False


def output(data, message: str = ""):
    """Print output in JSON or human-readable format."""
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)
        else:
            click.echo(str(data))


def _print_dict(d: dict, indent: int = 0):
    prefix = "  " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{prefix}{k}:")
            _print_dict(v, indent + 1)
        elif isinstance(v, list):
            click.echo(f"{prefix}{k}:")
            _print_list(v, indent + 1)
        else:
            click.echo(f"{prefix}{k}: {v}")


def _print_list(items: list, indent: int = 0):
    prefix = "  " * indent
    for i, item in enumerate(items):
        if isinstance(item, dict):
            click.echo(f"{prefix}[{i}]")
            _print_dict(item, indent + 1)
        else:
            click.echo(f"{prefix}- {item}")


def handle_error(func):
    """Decorator for consistent error handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if _json_output:
                click.echo(json.dumps({
                    "error": str(e),
                    "type": type(e).__name__,
                }))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# ── Main CLI Group ──────────────────────────────────────────────
@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx, use_json):
    """YouTube CLI — Trending videos, hashtags, music discovery & channel optimization.

    Run without a subcommand to enter interactive REPL mode.
    """
    global _json_output
    _json_output = use_json

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── Auth Commands ───────────────────────────────────────────────
@cli.group()
def auth():
    """API key setup and authentication status."""
    pass


@auth.command("setup")
@click.option("--api-key", required=True, help="YouTube Data API v3 key")
@handle_error
def auth_setup(api_key):
    """Configure YouTube Data API v3 key."""
    result = account_mod.setup_api(api_key)
    output(result, "YouTube API key configured successfully.")


@auth.command("status")
@handle_error
def auth_status():
    """Check API key configuration status."""
    result = account_mod.get_api_status()
    output(result)


# ── Trends Commands ─────────────────────────────────────────────
@cli.group()
def trends():
    """Trending videos, music, hashtags, and topics."""
    pass


@trends.command("videos")
@click.option("--region", "-r", default="US", help="Region code (e.g. US, GB, CA, AU)")
@click.option("--category", "-c", default="all",
              help="Category name or ID (e.g. music, gaming, tech, 28)")
@click.option("--limit", "-n", type=int, default=20, help="Number of videos to fetch")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@handle_error
def trends_videos(region, category, limit, use_json):
    """Fetch trending YouTube videos for a region and category."""
    global _json_output
    if use_json:
        _json_output = True
    result = trends_mod.get_trending_videos(region=region, category=category, limit=limit)
    output(result, f"Trending videos ({region} / {result.get('category', category)}):")


@trends.command("music")
@click.option("--region", "-r", default="US", help="Region code (e.g. US, GB, CA, AU)")
@click.option("--limit", "-n", type=int, default=20, help="Number of music videos to fetch")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@handle_error
def trends_music(region, limit, use_json):
    """Fetch trending music videos — great for Shorts and Reels audio."""
    global _json_output
    if use_json:
        _json_output = True
    result = trends_mod.get_trending_music(region=region, limit=limit)
    output(result, f"Trending music ({region}):")


@trends.command("topics")
@click.option("--region", "-r", default="US", help="Region code")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@handle_error
def trends_topics(region, use_json):
    """Show trending YouTube topic categories with tips."""
    global _json_output
    if use_json:
        _json_output = True
    result = trends_mod.get_trending_topics(region=region)
    output(result, f"Trending topics ({region}):")


@trends.command("hashtag")
@click.argument("hashtag")
@click.option("--limit", "-n", type=int, default=20, help="Number of videos to fetch")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@handle_error
def trends_hashtag(hashtag, limit, use_json):
    """Search trending videos for a hashtag.

    HASHTAG: The hashtag to search (with or without leading #).
    """
    global _json_output
    if use_json:
        _json_output = True
    result = trends_mod.search_by_hashtag(hashtag=hashtag, limit=limit)
    output(result, f"Hashtag search: #{hashtag.lstrip('#')}")


# ── Channel Commands ────────────────────────────────────────────
@cli.group()
def channel():
    """Channel audit and optimization tools."""
    pass


@channel.command("audit")
@click.argument("handle")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@handle_error
def channel_audit(handle, use_json):
    """Audit a YouTube channel and get optimization recommendations.

    HANDLE: Channel handle (e.g. @MrBeast) or channel ID (UCxxxxxx).
    """
    global _json_output
    if use_json:
        _json_output = True
    result = account_mod.audit_channel(handle)
    output(result, f"Channel audit: {handle}")


@channel.command("optimize")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@handle_error
def channel_optimize(use_json):
    """Get the complete channel optimization checklist."""
    global _json_output
    if use_json:
        _json_output = True
    result = account_mod.get_optimization_checklist()
    output(result, "Channel optimization checklist:")


# ── Strategy Commands ───────────────────────────────────────────
@cli.group()
def strategy():
    """Content strategy, Shorts, monetization, and SEO guides."""
    pass


@strategy.command("shorts")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@handle_error
def strategy_shorts(use_json):
    """Complete YouTube Shorts strategy for rapid growth."""
    global _json_output
    if use_json:
        _json_output = True
    result = strategy_mod.get_shorts_strategy()
    output(result, "YouTube Shorts strategy:")


@strategy.command("monetization")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@handle_error
def strategy_monetization(use_json):
    """Full monetization roadmap from 0 to $10K/month."""
    global _json_output
    if use_json:
        _json_output = True
    result = strategy_mod.get_monetization_roadmap()
    output(result, "YouTube monetization roadmap:")


@strategy.command("seo")
@click.option("--niche", required=True, help="Your content niche (e.g. fitness, finance, tech)")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@handle_error
def strategy_seo(niche, use_json):
    """Build a YouTube SEO and content strategy for your niche."""
    global _json_output
    if use_json:
        _json_output = True
    result = trends_mod.build_seo_strategy(niche=niche)
    output(result, f"SEO strategy for niche: {niche}")


@strategy.command("cpm-guide")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@handle_error
def strategy_cpm_guide(use_json):
    """YouTube CPM by niche — plan your monetization from the start."""
    global _json_output
    if use_json:
        _json_output = True
    result = strategy_mod.get_niche_cpm_guide()
    output(result, "YouTube CPM guide by niche:")


# ── REPL ─────────────────────────────────────────────────────────
@cli.command()
@handle_error
def repl():
    """Start interactive REPL session."""
    from cli_anything.youtube.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("youtube", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "auth":     "setup|status",
        "trends":   "videos|music|topics|hashtag",
        "channel":  "audit|optimize",
        "strategy": "shorts|monetization|seo|cpm-guide",
        "help":     "Show this help",
        "quit":     "Exit REPL",
    }

    # Check API key status on start
    try:
        status = account_mod.get_api_status()
        if status.get("api_key_set"):
            skin.success(f"API key configured ({status.get('api_key_preview')}) — live mode active.")
        else:
            skin.info("No API key set — running in demo mode. Run: auth setup --api-key <KEY>")
    except Exception:
        skin.info("Run 'auth setup --api-key <KEY>' to configure the YouTube Data API.")

    while True:
        try:
            line = skin.get_input(pt_session)
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                skin.print_goodbye()
                break
            if line.lower() == "help":
                skin.help(_repl_commands)
                continue

            # Parse and execute command
            args = line.split()
            try:
                cli.main(args, standalone_mode=False)
            except SystemExit:
                pass
            except click.exceptions.UsageError as e:
                skin.warning(f"Usage error: {e}")
            except Exception as e:
                skin.error(f"{e}")

        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

    _repl_mode = False


# ── Entry Point ──────────────────────────────────────────────────
def main():
    cli()


if __name__ == "__main__":
    main()
