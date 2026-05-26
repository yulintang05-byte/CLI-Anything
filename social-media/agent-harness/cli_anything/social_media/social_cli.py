#!/usr/bin/env python3
"""social-cli — Viral trend scraper, account optimizer, and theme page toolkit.

Usage:
    social-cli trends youtube --no-api --region US --max 20
    social-cli trends tiktok --niche finance --max-sounds 10
    social-cli trends all --niche fitness --region US

    social-cli optimize audit --platform tiktok --username mypage --followers 5000
    social-cli optimize playbook --platform tiktok --followers 8000 --niche finance
    social-cli optimize calendar --platform tiktok --niche motivation --posts-per-day 3
    social-cli optimize all --config accounts.json

    social-cli theme blueprint --niche finance
    social-cli theme convert --niche motivation --followers 5000
    social-cli theme niches

    social-cli repl
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_media.core import youtube as yt_mod
from cli_anything.social_media.core import tiktok as tt_mod
from cli_anything.social_media.core import account_optimizer as opt_mod
from cli_anything.social_media.core import theme_pages as theme_mod

_json_output = False
_repl_mode = False


def output(data, message: str = ""):
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        _pretty(data)


def _pretty(data, indent: int = 0):
    prefix = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{prefix}{k}:")
                _pretty(v, indent + 1)
            else:
                click.echo(f"{prefix}{k}: {v}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                click.echo(f"{prefix}[{i}]")
                _pretty(item, indent + 1)
            else:
                click.echo(f"{prefix}  - {item}")
    else:
        click.echo(f"{prefix}{data}")


def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RuntimeError as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": "runtime"}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
        except Exception as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"Unexpected error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# ============================================================================
# Root CLI
# ============================================================================

@click.group()
@click.option("--json", "json_out", is_flag=True, help="Output as JSON")
def cli(json_out: bool):
    """social-cli: Viral trend scraper, account optimizer, and theme page toolkit."""
    global _json_output
    _json_output = json_out


# ============================================================================
# trends group
# ============================================================================

@cli.group()
def trends():
    """Scrape viral trends, hashtags, and music from YouTube and TikTok."""


@trends.command("youtube")
@click.option("--api-key", envvar="YOUTUBE_API_KEY", default="", help="YouTube Data API v3 key (or set YOUTUBE_API_KEY env var)")
@click.option("--region", default="US", show_default=True, help="Region code: US, UK, CA, AU, IN…")
@click.option("--category", default="all", show_default=True,
              type=click.Choice(["all", "music", "gaming", "entertainment", "news", "sports", "tech"]),
              help="Content category")
@click.option("--max", "max_results", default=20, show_default=True, help="Max videos to fetch (max 50 with API)")
@click.option("--no-api", is_flag=True, help="Scrape trending page without API key (limited data)")
@handle_error
def youtube_trends(api_key: str, region: str, category: str, max_results: int, no_api: bool):
    """Fetch YouTube trending videos, hashtags, and viral music."""
    if no_api or not api_key:
        click.echo(f"Fetching YouTube trending (no-api mode, region={region})…", err=True)
        result = yt_mod.fetch_trending_no_api(region=region, max_results=max_results)
    else:
        click.echo(f"Fetching YouTube trending via API (region={region}, category={category})…", err=True)
        result = yt_mod.fetch_trending(api_key=api_key, region=region, category=category, max_results=max_results)

    output(result.to_dict(), f"\nYouTube Trending — {region} ({result.fetched_at})")


@trends.command("tiktok")
@click.option("--niche", default="general", show_default=True,
              type=click.Choice(["general", "lifestyle", "finance", "fitness", "food"]),
              help="Niche for targeted hashtag curation")
@click.option("--region", default="US", show_default=True, help="Region code: US, UK, CA, AU…")
@click.option("--max-hashtags", default=20, show_default=True, help="Max hashtags to return")
@click.option("--max-sounds", default=10, show_default=True, help="Max trending sounds to return")
@click.option("--live-scrape", is_flag=True, help="Attempt live scrape of TikTok trending page (may be blocked)")
@handle_error
def tiktok_trends(niche: str, region: str, max_hashtags: int, max_sounds: int, live_scrape: bool):
    """Fetch TikTok trending hashtags, sounds, and content ideas."""
    click.echo(f"Fetching TikTok trends (niche={niche}, region={region})…", err=True)
    result = tt_mod.fetch_trending(
        niche=niche, region=region,
        max_hashtags=max_hashtags, max_sounds=max_sounds,
        live_scrape=live_scrape,
    )
    output(result.to_dict(), f"\nTikTok Trends — {niche.title()} / {region} ({result.fetched_at})")


@trends.command("all")
@click.option("--niche", default="general", show_default=True, help="Niche for TikTok curation")
@click.option("--region", default="US", show_default=True, help="Region code")
@click.option("--youtube-api-key", envvar="YOUTUBE_API_KEY", default="", help="Optional YouTube API key")
@handle_error
def all_trends(niche: str, region: str, youtube_api_key: str):
    """Fetch combined trends from both YouTube and TikTok."""
    click.echo("Fetching YouTube + TikTok trends…", err=True)

    if youtube_api_key:
        yt_result = yt_mod.fetch_trending(api_key=youtube_api_key, region=region)
    else:
        yt_result = yt_mod.fetch_trending_no_api(region=region)

    tt_result = tt_mod.fetch_trending(niche=niche, region=region)

    combined = {
        "youtube": yt_result.to_dict(),
        "tiktok": tt_result.to_dict(),
        "cross_platform_strategy": [
            "Post YouTube Shorts versions of TikTok content for double reach",
            "Use trending TikTok sounds that also appear in YouTube Music charts",
            f"Top YouTube topic this week: {yt_result.videos[0].title[:60] + '…' if yt_result.videos else 'N/A'}",
            "Hashtag bridge: use YouTube title keywords as TikTok hashtags",
            "Content lag: TikTok trends hit YouTube 3-7 days later — get ahead of it",
        ],
    }
    output(combined, "\nCombined Trend Report")


# ============================================================================
# optimize group
# ============================================================================

@cli.group()
def optimize():
    """Audit, optimize, and build growth playbooks for social media accounts."""


@optimize.command("audit")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "youtube", "instagram"]), help="Platform")
@click.option("--username", required=True, help="Account username")
@click.option("--followers", default=0, show_default=True, help="Current follower count")
@click.option("--checks", default="{}", help="JSON dict of completed checks e.g. '{\"profile_pic\":true}'")
@handle_error
def audit_account(platform: str, username: str, followers: int, checks: str):
    """Run a profile optimization audit and get prioritized fixes."""
    try:
        checks_dict = json.loads(checks)
    except json.JSONDecodeError:
        checks_dict = {}

    result = opt_mod.audit_profile(platform, username, followers, checks_dict)
    output(result.to_dict(), f"\nProfile Audit: @{username} ({platform}) — Score: {result.score}/100")


@optimize.command("playbook")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--followers", default=0, help="Current follower count")
@click.option("--niche", default="general", help="Account niche")
@handle_error
def growth_playbook(platform: str, followers: int, niche: str):
    """Get a phase-specific daily/weekly/monthly growth playbook."""
    result = opt_mod.build_growth_playbook(platform, followers, niche)
    output(result.to_dict(), f"\nGrowth Playbook: {platform.title()} | Phase: {result.current_phase.title()}")


@optimize.command("calendar")
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--niche", default="general", help="Content niche")
@click.option("--posts-per-day", default=3, show_default=True, help="Posts per day (1-5)")
@handle_error
def content_calendar(platform: str, niche: str, posts_per_day: int):
    """Generate a 7-day content calendar with hooks, CTAs, and hashtag sets."""
    posts_per_day = max(1, min(5, posts_per_day))
    result = opt_mod.build_content_calendar(platform, niche, posts_per_day)
    output(result.to_dict(), f"\n7-Day Content Calendar: {platform.title()} | Niche: {niche.title()}")


@optimize.command("all")
@click.option("--config", required=True, type=click.Path(exists=True),
              help="Path to JSON file with accounts list. Example: [{\"platform\":\"tiktok\",\"username\":\"mypage\",\"followers\":5000,\"niche\":\"finance\"}]")
@handle_error
def optimize_all(config: str):
    """Optimize all accounts from a JSON config file."""
    with open(config) as f:
        accounts = json.load(f)
    if not isinstance(accounts, list):
        accounts = [accounts]
    results = opt_mod.optimize_all_accounts(accounts)
    output(results, f"\nOptimization Report: {len(results)} account(s)")


# ============================================================================
# theme group
# ============================================================================

@cli.group()
def theme():
    """Build, run, and monetize theme pages (niche content aggregators)."""


@theme.command("blueprint")
@click.option("--niche", default="motivation",
              type=click.Choice(["motivation", "finance", "fitness", "aesthetic", "food"]),
              help="Theme page niche")
@handle_error
def theme_blueprint(niche: str):
    """Get a complete theme page blueprint: content, sourcing, monetization, timeline."""
    result = theme_mod.get_blueprint(niche)
    output(result.to_dict(), f"\nTheme Page Blueprint: {niche.title()}")


@theme.command("convert")
@click.option("--niche", default="motivation",
              type=click.Choice(["motivation", "finance", "fitness", "aesthetic", "food"]),
              help="Page niche")
@click.option("--followers", default=0, help="Current follower count")
@click.option("--page-type", default="theme_page", type=click.Choice(["theme_page", "personal_brand", "faceless"]))
@handle_error
def theme_convert(niche: str, followers: int, page_type: str):
    """Get a conversion strategy: traffic → leads → revenue funnel."""
    result = theme_mod.get_conversion_strategy(page_type, niche, followers)
    output(result.to_dict(), f"\nConversion Strategy: {page_type.replace('_',' ').title()} | {niche.title()}")


@theme.command("niches")
@handle_error
def theme_niches():
    """List all available theme page niches."""
    niches = theme_mod.list_niches()
    output({"available_niches": niches}, "Supported theme page niches:")


# ============================================================================
# REPL
# ============================================================================

@cli.command("repl")
def repl():
    """Launch interactive REPL for social media automation."""
    global _repl_mode
    _repl_mode = True

    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import InMemoryHistory
        session = PromptSession(history=InMemoryHistory())
        use_prompt_toolkit = True
    except ImportError:
        use_prompt_toolkit = False

    click.echo("social-cli REPL — type 'help' for commands, 'exit' to quit")
    click.echo("Commands: trends youtube | trends tiktok | trends all | optimize audit | optimize playbook | optimize calendar | theme blueprint | theme convert | theme niches")

    while True:
        try:
            if use_prompt_toolkit:
                line = session.prompt("social> ").strip()
            else:
                line = input("social> ").strip()
        except (EOFError, KeyboardInterrupt):
            click.echo("\nGoodbye.")
            break

        if not line:
            continue
        if line in ("exit", "quit", "q"):
            click.echo("Goodbye.")
            break
        if line == "help":
            click.echo(cli.get_help(click.Context(cli)))
            continue

        args = line.split()
        try:
            cli.main(args, standalone_mode=False)
        except SystemExit:
            pass
        except Exception as e:
            click.echo(f"Error: {e}", err=True)


def main():
    cli()


if __name__ == "__main__":
    main()
