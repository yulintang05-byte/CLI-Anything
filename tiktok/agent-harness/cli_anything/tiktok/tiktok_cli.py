#!/usr/bin/env python3
"""TikTok CLI — scrape viral trends, hashtags, and sounds for account growth.

Usage:
    cli-anything-tiktok trends fetch [--region US] [--limit 20]
    cli-anything-tiktok trends search <hashtag>
    cli-anything-tiktok hashtags top [--niche fitness] [--limit 30]
    cli-anything-tiktok hashtags suggest <niche>
    cli-anything-tiktok sounds trending [--region US] [--limit 20]
    cli-anything-tiktok sounds niche <niche>
    cli-anything-tiktok account audit [--handle @you] [--niche fitness]
    cli-anything-tiktok report daily [--region US]
    cli-anything-tiktok niches list
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.tiktok.utils.tiktok_backend import (
    get_session_cookie, load_config, save_config,
    get_posting_schedule, account_audit_tips, list_niches,
)

_json_output = False
_repl_mode = False
_session_id: Optional[str] = None


def output(data, message: str = ""):
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)
        elif data is not None:
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
        elif isinstance(item, str):
            click.echo(f"{prefix}{item}")
        else:
            click.echo(f"{prefix}- {item}")


def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (FileNotFoundError, ValueError, RuntimeError, TimeoutError) as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# ── Main CLI ────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.option("--session-id", "session_id_opt", default=None,
              help="TikTok session cookie (optional, for better access)")
@click.pass_context
def cli(ctx, use_json, session_id_opt):
    """TikTok CLI — scrape viral trends, hashtags, and sounds."""
    global _json_output, _session_id
    _json_output = use_json
    _session_id = get_session_cookie(session_id_opt)
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── Trends ──────────────────────────────────────────────────────────────

@cli.group()
def trends():
    """Trend scraping — fetch viral content and signals."""
    pass


@trends.command("fetch")
@click.option("--region", "-r", default="US", show_default=True,
              help="Region code (US, GB, AU, CA, ...)")
@click.option("--limit", "-n", type=int, default=20, show_default=True,
              help="Number of videos to analyze")
@handle_error
def trends_fetch(region, limit):
    """Fetch currently trending TikTok videos and extract trend signals."""
    from cli_anything.tiktok.core.trends import fetch_trending
    if not _json_output:
        click.echo(f"Fetching TikTok trending feed (region={region}, limit={limit})...")
    result = fetch_trending(region=region, limit=limit, session_id=_session_id)
    output(result, f"\n✓ Analyzed {result['video_count']} videos")


@trends.command("search")
@click.argument("hashtag")
@click.option("--limit", "-n", type=int, default=20, show_default=True,
              help="Number of videos to analyze")
@handle_error
def trends_search(hashtag, limit):
    """Search trending videos for a specific hashtag."""
    from cli_anything.tiktok.core.trends import fetch_by_hashtag
    tag = hashtag.lstrip("#")
    click.echo(f"Fetching videos for #{tag} (limit={limit})...")
    result = fetch_by_hashtag(tag, limit=limit, session_id=_session_id)
    output(result, f"\n✓ Analyzed {result['video_count']} videos for #{tag}")


@trends.command("report")
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--limit", "-n", type=int, default=30, show_default=True)
@click.option("--output", "output_file", default=None, help="Save report to JSON file")
@handle_error
def trends_report(region, limit, output_file):
    """Generate a daily TikTok trend report."""
    from cli_anything.tiktok.core.trends import build_trend_report
    click.echo(f"Building daily trend report (region={region})...")
    report = build_trend_report(region=region, limit=limit)

    if output_file:
        import pathlib
        pathlib.Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2, default=str)
        click.echo(f"✓ Report saved to {output_file}")
    else:
        output(report, f"\n✓ Daily Trend Report ({report['date']})")


# ── Hashtags ────────────────────────────────────────────────────────────

@cli.group()
def hashtags():
    """Hashtag tools — curated packs, strategies, and captions."""
    pass


@hashtags.command("top")
@click.option("--niche", "-n", default=None, help="Filter by niche (fitness, food, ...)")
@click.option("--limit", "-l", type=int, default=30, show_default=True)
@handle_error
def hashtags_top(niche, limit):
    """Get top hashtags, optionally filtered by niche."""
    from cli_anything.tiktok.core.hashtags import get_top_hashtags
    result = get_top_hashtags(niche=niche, limit=limit)
    output(result, f"Top {result['count']} hashtags [{result['niche']}]:")


@hashtags.command("suggest")
@click.argument("niche")
@click.option("--limit", "-l", type=int, default=30, show_default=True)
@handle_error
def hashtags_suggest(niche, limit):
    """Generate a tiered hashtag strategy for your niche."""
    from cli_anything.tiktok.core.hashtags import suggest_hashtags
    result = suggest_hashtags(niche=niche, limit=limit)
    output(result, f"\n✓ Hashtag strategy for #{niche}:")


@hashtags.command("caption")
@click.argument("niche")
@click.option("--tags", "-t", type=int, default=5, show_default=True,
              help="Number of hashtags to include")
@handle_error
def hashtags_caption(niche, tags):
    """Build a sample caption with optimal hashtag placement."""
    from cli_anything.tiktok.core.hashtags import build_caption
    caption = build_caption(niche=niche, num_tags=tags)
    click.echo(caption)


# ── Sounds ──────────────────────────────────────────────────────────────

@cli.group()
def sounds():
    """Sound/music tools — find trending audio for your videos."""
    pass


@sounds.command("trending")
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--limit", "-n", type=int, default=20, show_default=True)
@handle_error
def sounds_trending(region, limit):
    """Get trending sounds from the TikTok trending feed."""
    from cli_anything.tiktok.core.sounds import get_trending_sounds
    click.echo(f"Fetching trending sounds (region={region})...")
    result = get_trending_sounds(region=region, limit=limit)
    output(result, f"\n✓ Found {result['count']} trending sounds")


@sounds.command("niche")
@click.argument("niche")
@click.option("--limit", "-n", type=int, default=20, show_default=True)
@handle_error
def sounds_niche(niche, limit):
    """Get trending sounds within a specific niche."""
    from cli_anything.tiktok.core.sounds import get_sounds_for_niche
    click.echo(f"Fetching trending sounds for niche '{niche}'...")
    result = get_sounds_for_niche(niche=niche, limit=limit)
    output(result, f"\n✓ Found {result['count']} sounds for {niche}")


# ── Account ─────────────────────────────────────────────────────────────

@cli.group()
def account():
    """Account optimization — audit tips and growth strategies."""
    pass


@account.command("audit")
@click.option("--handle", "-u", default="", help="Your TikTok handle (e.g. @username)")
@click.option("--niche", "-n", default="", help="Your content niche")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "instagram"], case_sensitive=False),
              default="tiktok", show_default=True)
@handle_error
def account_audit(handle, niche, platform):
    """Get personalized account optimization tips."""
    result = account_audit_tips(handle=handle, niche=niche, platform=platform)
    output(result, f"\n✓ Account audit for {result['handle']} [{platform}]:")


@account.command("schedule")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube_shorts", "instagram_reels"],
                                case_sensitive=False),
              default="tiktok", show_default=True)
@handle_error
def account_schedule(platform):
    """Show best posting times for a platform."""
    schedule = get_posting_schedule(platform=platform)
    result = {"platform": platform, "best_times": schedule}
    output(result, f"\nBest posting times for {platform}:")


# ── Niches ──────────────────────────────────────────────────────────────

@cli.group()
def niches():
    """Niche tools — list and explore available content niches."""
    pass


@niches.command("list")
def niches_list():
    """List all available content niches."""
    n = list_niches()
    if _json_output:
        click.echo(json.dumps({"niches": n, "count": len(n)}))
    else:
        click.echo(f"Available niches ({len(n)}):")
        for name in n:
            click.echo(f"  • {name}")


# ── Config ──────────────────────────────────────────────────────────────

@cli.group()
def config():
    """Configuration — manage session cookies and settings."""
    pass


@config.command("set")
@click.argument("key", type=click.Choice(["session_id", "default_region", "default_niche"]))
@click.argument("value")
def config_set(key, value):
    """Set a config value."""
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)
    display = value[:8] + "..." if key == "session_id" and len(value) > 8 else value
    output({"key": key, "value": display}, f"✓ Set {key}")


@config.command("get")
@click.argument("key", required=False)
def config_get(key):
    """Show config value(s)."""
    cfg = load_config()
    if key:
        val = cfg.get(key)
        output({"key": key, "value": val})
    else:
        output(cfg if cfg else {}, "Config:")


# ── Session ──────────────────────────────────────────────────────────────

@cli.group()
def session():
    """Session management."""
    pass


@session.command("status")
def session_status():
    """Show session status."""
    has_cookie = bool(get_session_cookie())
    output({"session_id_configured": has_cookie})


# ── REPL ─────────────────────────────────────────────────────────────────

@cli.command("repl", hidden=True)
def repl():
    """Enter interactive REPL mode."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.tiktok.utils.repl_skin import ReplSkin
    skin = ReplSkin("tiktok", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    commands = {
        "trends fetch [--region US]":       "Fetch trending TikTok videos",
        "trends search <hashtag>":           "Scrape videos for a hashtag",
        "trends report [--region US]":       "Generate daily trend report",
        "hashtags top [--niche fitness]":    "Get top hashtags by niche",
        "hashtags suggest <niche>":          "Full hashtag strategy for niche",
        "hashtags caption <niche>":          "Build caption with hashtags",
        "sounds trending [--region US]":     "Get trending sounds",
        "sounds niche <niche>":              "Get trending sounds for niche",
        "account audit [--niche fitness]":   "Account optimization tips",
        "account schedule [--platform]":     "Best posting times",
        "niches list":                       "List available niches",
        "config set <key> <value>":          "Set configuration",
        "help":                              "Show this help",
        "quit / exit":                       "Exit REPL",
    }

    while True:
        try:
            line = skin.get_input(pt_session, context="tiktok")
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

        if not line:
            continue
        if line in ("quit", "exit", "q"):
            skin.print_goodbye()
            break
        if line == "help":
            skin.help(commands)
            continue

        parts = line.split()
        try:
            cli.main(parts, standalone_mode=False)
        except SystemExit:
            pass
        except click.exceptions.UsageError as e:
            skin.error(str(e))
        except Exception as e:
            skin.error(str(e))


def main():
    cli()


if __name__ == "__main__":
    main()
