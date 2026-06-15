#!/usr/bin/env python3
"""TikTok CLI — Viral trends, hashtags, music discovery & account optimization from the command line.

This CLI surfaces TikTok trending data and account intelligence via RapidAPI
and Apify. It covers trend discovery, hashtag analytics, music tracking,
account auditing, and full theme page monetization strategy.

Usage:
    # Configure API keys
    cli-anything-tiktok auth setup --rapidapi-key <KEY> --apify-token <TOKEN>

    # Check API status
    cli-anything-tiktok auth status

    # Browse trending videos
    cli-anything-tiktok trends videos --region US --limit 20

    # Explore trending hashtags
    cli-anything-tiktok trends hashtags --keyword fitness

    # Get trending music/sounds
    cli-anything-tiktok trends music --region US

    # Build a hashtag strategy for your niche
    cli-anything-tiktok trends hashtag-strategy --niche fitness

    # Analyze a specific hashtag
    cli-anything-tiktok trends analyze-hashtag --hashtag fyp

    # Audit a TikTok account
    cli-anything-tiktok account audit @username

    # Get optimization checklist
    cli-anything-tiktok account optimize

    # Theme page monetization guide
    cli-anything-tiktok strategy theme-page

    # Niche analysis for a theme page
    cli-anything-tiktok strategy niche-analysis --niche finance

    # Interactive REPL
    cli-anything-tiktok repl
"""

import sys
import os
import json
import click
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.tiktok.core import trends as trends_mod
from cli_anything.tiktok.core import account as account_mod
from cli_anything.tiktok.core import strategy as strategy_mod

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
    """TikTok CLI — Viral trends, hashtags, music discovery & account optimization.

    Run without a subcommand to enter interactive REPL mode.
    """
    global _json_output
    _json_output = use_json

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── Auth Commands ───────────────────────────────────────────────
@cli.group()
def auth():
    """API key setup and status."""
    pass


@auth.command("setup")
@click.option("--rapidapi-key", default="", help="RapidAPI key for TikTok API access")
@click.option("--apify-token", default="", help="Apify token for hashtag scraper")
@handle_error
def auth_setup(rapidapi_key, apify_token):
    """Configure API keys for TikTok data access.

    RapidAPI key: Subscribe to a TikTok API on rapidapi.com
    Apify token:  Sign up at apify.com for hashtag scraping
    """
    if not rapidapi_key and not apify_token:
        raise click.UsageError(
            "Provide at least one: --rapidapi-key or --apify-token"
        )
    result = account_mod.setup_api(
        rapidapi_key=rapidapi_key,
        apify_token=apify_token,
    )
    output(result, "API credentials saved.")


@auth.command("status")
@handle_error
def auth_status():
    """Check configured API key status."""
    result = account_mod.get_api_status()
    output(result)


# ── Trends Commands ─────────────────────────────────────────────
@cli.group()
def trends():
    """Trending videos, hashtags, and music discovery."""
    pass


@trends.command("videos")
@click.option("--region", "-r", default="US", show_default=True,
              help="Region code (US, GB, AU, CA, etc.)")
@click.option("--limit", "-l", type=int, default=20, show_default=True,
              help="Number of videos to fetch")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@handle_error
def trends_videos(region, limit, use_json):
    """Fetch trending TikTok videos with hashtag and music breakdown."""
    global _json_output
    if use_json:
        _json_output = True
    result = trends_mod.get_trending_videos(region=region, limit=limit)
    output(result, f"Trending videos ({region}, top {limit}):")


@trends.command("hashtags")
@click.option("--keyword", "-k", default="", help="Keyword filter for hashtag search")
@click.option("--region", "-r", default="US", show_default=True,
              help="Region code")
@click.option("--limit", "-l", type=int, default=30, show_default=True,
              help="Number of hashtags to return")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@handle_error
def trends_hashtags(keyword, region, limit, use_json):
    """Fetch trending TikTok hashtags sorted by total views."""
    global _json_output
    if use_json:
        _json_output = True
    result = trends_mod.get_trending_hashtags(keyword=keyword, region=region, limit=limit)
    output(result, f"Trending hashtags ({region}):")


@trends.command("music")
@click.option("--region", "-r", default="US", show_default=True,
              help="Region code")
@click.option("--limit", "-l", type=int, default=20, show_default=True,
              help="Number of sounds to fetch")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@handle_error
def trends_music(region, limit, use_json):
    """Fetch trending TikTok sounds and music sorted by video usage."""
    global _json_output
    if use_json:
        _json_output = True
    result = trends_mod.get_trending_music(region=region, limit=limit)
    output(result, f"Trending music/sounds ({region}, top {limit}):")


@trends.command("hashtag-strategy")
@click.option("--niche", "-n", required=True,
              help="Your content niche (e.g., fitness, finance, comedy)")
@click.option("--region", "-r", default="US", show_default=True,
              help="Region code")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@handle_error
def trends_hashtag_strategy(niche, region, use_json):
    """Generate a hashtag strategy mix for a given content niche.

    Returns a recommended mix of mega, niche, and custom hashtags
    with posting time recommendations.
    """
    global _json_output
    if use_json:
        _json_output = True
    result = trends_mod.build_hashtag_strategy(niche=niche, region=region)
    output(result, f"Hashtag strategy for: {niche}")


@trends.command("analyze-hashtag")
@click.option("--hashtag", "-t", required=True,
              help="Hashtag to analyze (with or without #)")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@handle_error
def trends_analyze_hashtag(hashtag, use_json):
    """Analyze a specific hashtag: views, video count, audience size, and recommendation."""
    global _json_output
    if use_json:
        _json_output = True
    result = trends_mod.analyze_hashtag(hashtag=hashtag)
    output(result, f"Hashtag analysis: #{hashtag.lstrip('#')}")


# ── Account Commands ────────────────────────────────────────────
@cli.group()
def account():
    """TikTok account auditing and optimization."""
    pass


@account.command("audit")
@click.argument("username")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@handle_error
def account_audit(username, use_json):
    """Audit a TikTok account and get optimization recommendations.

    USERNAME: TikTok username (with or without @)
    """
    global _json_output
    if use_json:
        _json_output = True
    username = username.lstrip("@")
    result = account_mod.audit_account(username=username)
    output(result, f"Account audit: @{username}")


@account.command("optimize")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@handle_error
def account_optimize(use_json):
    """Get the universal TikTok account optimization checklist.

    Covers profile setup, content strategy, growth tactics,
    and analytics tracking.
    """
    global _json_output
    if use_json:
        _json_output = True
    result = account_mod.get_optimization_checklist()
    output(result, "TikTok Account Optimization Checklist:")


# ── Strategy Commands ───────────────────────────────────────────
@cli.group()
def strategy():
    """Theme page strategy and monetization playbooks."""
    pass


@strategy.command("theme-page")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@handle_error
def strategy_theme_page(use_json):
    """Complete guide to building and monetizing a TikTok theme page.

    Covers all 4 phases: Foundation, Content Engine, Growth Hacking,
    and Monetization — plus a 30-day roadmap and conversion funnel.
    """
    global _json_output
    if use_json:
        _json_output = True
    result = strategy_mod.get_theme_page_guide()
    output(result, "TikTok Theme Page Guide:")


@strategy.command("niche-analysis")
@click.option("--niche", "-n", required=True,
              help="Niche to analyze (luxury, fitness, finance, motivation, business)")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@handle_error
def strategy_niche_analysis(niche, use_json):
    """Analyze a niche for TikTok theme page potential.

    Returns competition level, monetization ease, CPM, best content
    formats, affiliate products, and a go/no-go verdict.
    """
    global _json_output
    if use_json:
        _json_output = True
    result = strategy_mod.get_niche_analysis(niche=niche)
    output(result, f"Niche analysis: {niche}")


# ── REPL ─────────────────────────────────────────────────────────
@cli.command()
@handle_error
def repl():
    """Start interactive REPL session."""
    from cli_anything.tiktok.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("tiktok", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "auth":     "setup|status",
        "trends":   "videos|hashtags|music|hashtag-strategy|analyze-hashtag",
        "account":  "audit|optimize",
        "strategy": "theme-page|niche-analysis",
        "help":     "Show this help",
        "quit":     "Exit REPL",
    }

    # Check API status on start
    try:
        status = account_mod.get_api_status()
        if status.get("mode") == "live":
            skin.success(f"API configured — running in live mode.")
        else:
            skin.info("Running in demo mode. Run: auth setup --rapidapi-key <KEY>")
    except Exception:
        skin.info("Run 'auth setup' to configure API credentials.")

    while True:
        try:
            # Determine context for prompt
            try:
                status = account_mod.get_api_status()
                context = "live" if status.get("mode") == "live" else "demo"
            except Exception:
                context = ""

            line = skin.get_input(pt_session, context=context)
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
