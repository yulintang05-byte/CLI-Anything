#!/usr/bin/env python3
"""Social Trends CLI — Scrape viral trends, optimize accounts, and build theme pages.

Covers YouTube and TikTok trend scraping, hashtag research, music discovery,
account optimization checklists, and a complete theme page monetisation playbook.

Usage:
    # Fetch trending now (TikTok + YouTube)
    cli-anything-social-trends trends fetch

    # Platform-specific
    cli-anything-social-trends trends fetch --platform tiktok
    cli-anything-social-trends trends music
    cli-anything-social-trends trends hashtags --platform tiktok --niche fitness

    # Account management
    cli-anything-social-trends account add --name "MyPage" --platform tiktok --niche fitness
    cli-anything-social-trends account optimize --platform tiktok
    cli-anything-social-trends account list

    # Theme pages
    cli-anything-social-trends theme-page niches
    cli-anything-social-trends theme-page guide --niche finance_money
    cli-anything-social-trends theme-page calendar --niche fitness --platform tiktok
    cli-anything-social-trends theme-page monetize
    cli-anything-social-trends theme-page convert

    # API config
    cli-anything-social-trends config api-key --platform youtube --key AIza...

    # Interactive REPL
    cli-anything-social-trends repl
"""

import sys
import os
import json
import click

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_trends.core import scraper
from cli_anything.social_trends.core import account_optimizer
from cli_anything.social_trends.core import theme_pages
from cli_anything.social_trends.utils import config as cfg

_json_output = False
_repl_mode = False


def output(data, message: str = ""):
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.secho(f"  {message}", bold=True)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)
        else:
            click.echo(str(data))


def _print_dict(d: dict, indent: int = 0):
    prefix = "  " * indent
    for k, v in d.items():
        label = str(k).replace("_", " ").title()
        if isinstance(v, dict):
            click.secho(f"{prefix}{label}:", bold=indent == 0)
            _print_dict(v, indent + 1)
        elif isinstance(v, list):
            click.secho(f"{prefix}{label}:", bold=indent == 0)
            _print_list(v, indent + 1)
        else:
            click.echo(f"{prefix}  {label}: {v}")


def _print_list(items: list, indent: int = 0):
    prefix = "  " * indent
    for i, item in enumerate(items):
        if isinstance(item, dict):
            # Inline dict for compact display
            parts = []
            for k, v in item.items():
                if not isinstance(v, (dict, list)):
                    parts.append(f"{k}: {v}")
            click.echo(f"{prefix}• " + " | ".join(parts) if parts else f"{prefix}[{i}]")
            if any(isinstance(v, (dict, list)) for v in item.values()):
                _print_dict(item, indent + 1)
        else:
            click.echo(f"{prefix}  • {item}")


def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.secho(f"Error: {e}", fg="red", err=True)
            if not _repl_mode:
                sys.exit(1)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# ── CLI root ─────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx, use_json):
    """Social Trends CLI — Viral trends, account optimization, and theme pages."""
    global _json_output
    _json_output = use_json
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── trends ───────────────────────────────────────────────────────

@cli.group()
def trends():
    """Scrape and browse viral trends."""
    pass


@trends.command("fetch")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "all"]), default="all",
              help="Platform to scrape")
@click.option("--region", "-r", default="US",
              help="Region code for YouTube trending (e.g. US, GB, IN)")
@click.option("--max", "max_results", type=int, default=20,
              help="Max results per platform")
@handle_error
def trends_fetch(platform, region, max_results):
    """Fetch currently trending content from TikTok and/or YouTube."""
    if platform in ("tiktok", "all"):
        click.secho("\nTikTok Trends", bold=True, fg="cyan")
        data = scraper.fetch_tiktok_trending(max_results=max_results)
        if data.get("warning"):
            click.secho(f"  Note: {data['warning']}", fg="yellow")
        output(data)

    if platform in ("youtube", "all"):
        click.secho("\nYouTube Trends", bold=True, fg="red")
        api_key = cfg.get_api_key("youtube")
        data = scraper.fetch_youtube_trending(
            api_key=api_key, region=region, max_results=max_results
        )
        output(data)


@trends.command("music")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok"]), default="tiktok",
              help="Platform (currently TikTok)")
@click.option("--max", "max_results", type=int, default=10)
@handle_error
def trends_music(platform, max_results):
    """Show trending songs and how to use them."""
    data = scraper.fetch_tiktok_music(max_results=max_results)
    output(data, "Trending Music")


@trends.command("hashtags")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube"]), default="tiktok")
@click.option("--niche", "-n", default="", help="Your content niche (e.g. fitness, food)")
@click.option("--max", "max_results", type=int, default=20)
@handle_error
def trends_hashtags(platform, niche, max_results):
    """Get trending + niche hashtags for a platform."""
    if platform == "tiktok":
        data = scraper.fetch_tiktok_hashtags(niche=niche, max_results=max_results)
    else:
        api_key = cfg.get_api_key("youtube")
        data = scraper.fetch_youtube_hashtags(
            niche=niche, api_key=api_key
        )
    output(data, f"Hashtags for {platform.title()}" + (f" › {niche}" if niche else ""))


# ── account ──────────────────────────────────────────────────────

@cli.group()
def account():
    """Manage and optimize social media accounts."""
    pass


@account.command("add")
@click.option("--name", "-n", required=True, help="Account/page name")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              required=True)
@click.option("--niche", required=True, help="Content niche")
@click.option("--handle", default="", help="@handle on the platform")
@handle_error
def account_add(name, platform, niche, handle):
    """Register a social account for tracking."""
    acct = cfg.add_account(name, platform, niche, handle)
    output(acct, f"Account added: {name} on {platform}")


@account.command("list")
@handle_error
def account_list():
    """List all registered accounts."""
    accounts = cfg.get_accounts()
    if not accounts:
        click.echo("No accounts registered yet. Use: account add")
        return
    output(accounts, f"{len(accounts)} account(s)")


@account.command("remove")
@click.option("--name", "-n", required=True)
@click.option("--platform", "-p", required=True)
@handle_error
def account_remove(name, platform):
    """Remove a registered account."""
    removed = cfg.remove_account(name, platform)
    if removed:
        click.secho(f"Removed {name} on {platform}", fg="green")
    else:
        click.secho("Account not found.", fg="yellow")


@account.command("optimize")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "instagram", "all"]),
              default="all")
@handle_error
def account_optimize(platform):
    """Print a full optimization checklist for a platform."""
    if platform == "all":
        data = account_optimizer.get_all_optimization_report()
    else:
        data = account_optimizer.get_optimization_report(platform)
    output(data, f"Optimization Report: {platform.title()}")


# ── config ───────────────────────────────────────────────────────

@cli.group("config")
def config_group():
    """Configure API keys and preferences."""
    pass


@config_group.command("api-key")
@click.option("--platform", "-p",
              type=click.Choice(["youtube"]), required=True)
@click.option("--key", "-k", required=True, help="API key value")
@handle_error
def config_api_key(platform, key):
    """Store an API key for a platform.

    YouTube: get a free key at console.cloud.google.com → YouTube Data API v3.
    With a key, trend fetching uses the official API instead of page scraping.
    """
    cfg.set_api_key(platform, key)
    click.secho(f"API key saved for {platform}.", fg="green")


@config_group.command("show")
@handle_error
def config_show():
    """Show current configuration (keys masked)."""
    yt_key = cfg.get_api_key("youtube")
    data = {
        "youtube_api_key": f"{yt_key[:8]}..." if len(yt_key) > 8 else ("set" if yt_key else "not set"),
        "accounts": len(cfg.get_accounts()),
        "config_dir": str(__import__("pathlib").Path.home() / ".cli-anything-social-trends"),
    }
    output(data, "Current Configuration")


# ── theme-page ───────────────────────────────────────────────────

@cli.group("theme-page")
def theme_page():
    """Build and monetise theme pages."""
    pass


@theme_page.command("niches")
@handle_error
def theme_page_niches():
    """List all supported niches with CPM and monetisation info."""
    data = theme_pages.get_niche_guide()
    output(data, "Available Niches")


@theme_page.command("guide")
@click.option("--niche", "-n", default="",
              help="Niche name (e.g. finance_money, pets_animals)")
@handle_error
def theme_page_guide(niche):
    """Deep-dive guide for a specific niche."""
    data = theme_pages.get_niche_guide(niche)
    output(data, f"Niche Guide: {niche or 'all niches'}")


@theme_page.command("calendar")
@click.option("--niche", "-n", default="")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              default="tiktok")
@handle_error
def theme_page_calendar(niche, platform):
    """Generate a 7-day content calendar framework."""
    data = theme_pages.get_content_calendar(niche=niche, platform=platform)
    output(data, "7-Day Content Calendar")


@theme_page.command("monetize")
@handle_error
def theme_page_monetize():
    """Show the full monetisation roadmap by follower tier."""
    data = theme_pages.get_monetisation_roadmap()
    output(data, "Monetisation Roadmap")


@theme_page.command("convert")
@handle_error
def theme_page_convert():
    """Show the content conversion playbook (hook → value → CTA)."""
    data = theme_pages.get_conversion_playbook()
    output(data, "Conversion Playbook")


# ── REPL ─────────────────────────────────────────────────────────

@cli.command()
@handle_error
def repl():
    """Start interactive REPL session."""
    from cli_anything.social_trends.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("social_trends", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _commands = {
        "trends":        "fetch|music|hashtags",
        "account":       "add|list|remove|optimize",
        "theme-page":    "niches|guide|calendar|monetize|convert",
        "config":        "api-key|show",
        "help":          "Show this help",
        "quit":          "Exit REPL",
    }

    accounts = cfg.get_accounts()
    if accounts:
        skin.info(f"Tracking {len(accounts)} account(s). Run: account list")
    else:
        skin.info("No accounts yet. Run: account add --name MyPage --platform tiktok --niche fitness")

    while True:
        try:
            line = skin.get_input(pt_session, context="")
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                skin.print_goodbye()
                break
            if line.lower() == "help":
                skin.help(_commands)
                continue

            args = line.split()
            # Normalize hyphenated group
            if args and args[0] == "theme-page":
                args[0] = "theme-page"
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


def main():
    cli()


if __name__ == "__main__":
    main()
