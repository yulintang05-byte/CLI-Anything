#!/usr/bin/env python3
"""YouTube CLI — scrape viral trends, hashtags, and optimize channels.

Usage:
    cli-anything-youtube trends fetch [--region US] [--category music] [--limit 25]
    cli-anything-youtube trends search <query>
    cli-anything-youtube hashtags extract <video-url>
    cli-anything-youtube hashtags channel <channel-url>
    cli-anything-youtube hashtags suggest <niche>
    cli-anything-youtube channel audit [--url <url>] [--niche fitness]
    cli-anything-youtube channel competitor <channel-url>
    cli-anything-youtube channel keywords <niche>
    cli-anything-youtube config set api_key YOUR_KEY
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.youtube.utils.yt_backend import (
    get_api_key, load_config, save_config,
    CATEGORY_IDS, REGIONS,
)

_json_output = False
_repl_mode = False
_api_key: Optional[str] = None


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
@click.option("--api-key", "api_key_opt", default=None,
              help="YouTube Data API v3 key (optional — yt-dlp used as fallback)")
@click.pass_context
def cli(ctx, use_json, api_key_opt):
    """YouTube CLI — scrape viral trends, hashtags, and optimize channels."""
    global _json_output, _api_key
    _json_output = use_json
    _api_key = get_api_key(api_key_opt)
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── Trends ──────────────────────────────────────────────────────────────

@cli.group()
def trends():
    """Trend scraping — fetch trending YouTube videos and signals."""
    pass


@trends.command("fetch")
@click.option("--region", "-r", default="US", show_default=True,
              help="Region code (US, GB, CA, AU, IN, ...)")
@click.option("--category", "-c",
              type=click.Choice(list(CATEGORY_IDS.keys()), case_sensitive=False),
              default="all", show_default=True)
@click.option("--limit", "-n", type=int, default=25, show_default=True,
              help="Number of trending videos to fetch")
@handle_error
def trends_fetch(region, category, limit):
    """Fetch currently trending YouTube videos."""
    from cli_anything.youtube.core.trends import fetch_trending
    if not _json_output:
        src = "YouTube Data API v3" if _api_key else "yt-dlp (no API key)"
        click.echo(f"Fetching YouTube trending ({region}, {category}, via {src})...")
    result = fetch_trending(region=region, category=category, limit=limit, api_key=_api_key)
    output(result, f"\n✓ Fetched {result['video_count']} trending videos")


@trends.command("categories")
def trends_categories():
    """List available video categories."""
    from cli_anything.youtube.core.trends import list_categories
    cats = list_categories()
    if _json_output:
        click.echo(json.dumps({"categories": cats}))
    else:
        click.echo("Available categories:")
        for c in cats:
            click.echo(f"  • {c}")


@trends.command("regions")
def trends_regions():
    """List supported region codes."""
    from cli_anything.youtube.core.trends import list_regions
    regions = list_regions()
    if _json_output:
        click.echo(json.dumps({"regions": regions}))
    else:
        click.echo("Supported regions: " + ", ".join(regions))


# ── Hashtags ────────────────────────────────────────────────────────────

@cli.group()
def hashtags():
    """Hashtag tools — extract from videos, channels, and get niche suggestions."""
    pass


@hashtags.command("extract")
@click.argument("video_url")
@handle_error
def hashtags_extract(video_url):
    """Extract hashtags and tags from a YouTube video URL."""
    from cli_anything.youtube.core.hashtags import extract_from_video
    click.echo(f"Extracting hashtags from {video_url}...")
    result = extract_from_video(video_url, api_key=_api_key)
    output(result, f"\n✓ Found {result['total_found']} hashtags/tags")


@hashtags.command("channel")
@click.argument("channel_url")
@click.option("--limit", "-n", type=int, default=20, show_default=True,
              help="Videos to analyze")
@handle_error
def hashtags_channel(channel_url, limit):
    """Extract top hashtags used by a YouTube channel."""
    from cli_anything.youtube.core.hashtags import extract_from_channel
    click.echo(f"Analyzing hashtags for {channel_url} (last {limit} videos)...")
    result = extract_from_channel(channel_url, limit=limit)
    output(result, f"\n✓ Analyzed {result['videos_analyzed']} videos")


@hashtags.command("suggest")
@click.argument("niche")
@click.option("--limit", "-n", type=int, default=20, show_default=True)
@handle_error
def hashtags_suggest(niche, limit):
    """Get hashtag and keyword suggestions for a YouTube niche."""
    from cli_anything.youtube.core.hashtags import suggest_for_niche
    result = suggest_for_niche(niche=niche, limit=limit)
    output(result, f"\n✓ Suggestions for '{niche}':")


@hashtags.command("niches")
def hashtags_niches():
    """List available niche categories."""
    from cli_anything.youtube.core.hashtags import list_niches
    niches = list_niches()
    if _json_output:
        click.echo(json.dumps({"niches": niches, "count": len(niches)}))
    else:
        click.echo(f"Available niches ({len(niches)}):")
        for n in niches:
            click.echo(f"  • {n}")


# ── Channel ─────────────────────────────────────────────────────────────

@cli.group()
def channel():
    """Channel tools — audit, competitor analysis, keyword research."""
    pass


@channel.command("audit")
@click.option("--url", "-u", default="", help="Your YouTube channel URL")
@click.option("--niche", "-n", default="", help="Your content niche")
@handle_error
def channel_audit(url, niche):
    """Get channel optimization recommendations."""
    from cli_anything.youtube.core.channel import audit
    result = audit(channel_url=url, niche=niche, api_key=_api_key)
    output(result, "\n✓ Channel audit complete:")


@channel.command("competitor")
@click.argument("channel_url")
@click.option("--limit", "-n", type=int, default=20, show_default=True)
@handle_error
def channel_competitor(channel_url, limit):
    """Analyze a competitor channel's hashtag strategy."""
    from cli_anything.youtube.core.channel import analyze_competitor
    click.echo(f"Analyzing competitor: {channel_url}...")
    result = analyze_competitor(channel_url, limit=limit)
    output(result, f"\n✓ Analyzed {result['videos_analyzed']} videos")


@channel.command("keywords")
@click.argument("niche")
@click.option("--limit", "-n", type=int, default=20, show_default=True)
@handle_error
def channel_keywords(niche, limit):
    """Research keywords for a niche."""
    from cli_anything.youtube.core.channel import keyword_research
    result = keyword_research(niche=niche, limit=limit)
    output(result, f"\n✓ Keywords for '{niche}':")


# ── Config ──────────────────────────────────────────────────────────────

@cli.group()
def config():
    """Configuration — API key and settings."""
    pass


@config.command("set")
@click.argument("key", type=click.Choice(["api_key", "default_region", "default_niche"]))
@click.argument("value")
def config_set(key, value):
    """Set a configuration value."""
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)
    display = value[:10] + "..." if key == "api_key" and len(value) > 10 else value
    output({"key": key, "value": display}, f"✓ Set {key}")


@config.command("get")
@click.argument("key", required=False)
def config_get(key):
    """Show configuration value(s)."""
    cfg = load_config()
    if key:
        val = cfg.get(key)
        if val and key == "api_key" and len(val) > 10:
            val = val[:10] + "..."
        output({"key": key, "value": val})
    else:
        masked = {}
        for k, v in cfg.items():
            masked[k] = v[:10] + "..." if k == "api_key" and len(v) > 10 else v
        output(masked if masked else {}, "Config:")


@config.command("path")
def config_path():
    """Show config file path."""
    from cli_anything.youtube.utils.yt_backend import CONFIG_FILE
    output({"path": str(CONFIG_FILE)}, f"Config: {CONFIG_FILE}")


# ── REPL ─────────────────────────────────────────────────────────────────

@cli.command("repl", hidden=True)
def repl():
    """Enter interactive REPL mode."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.youtube.utils.repl_skin import ReplSkin
    skin = ReplSkin("youtube", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    commands = {
        "trends fetch [--region US] [--category music]": "Fetch trending YouTube videos",
        "trends categories":                              "List video categories",
        "trends regions":                                 "List supported regions",
        "hashtags extract <video-url>":                   "Extract hashtags from a video",
        "hashtags channel <channel-url>":                 "Extract channel's top hashtags",
        "hashtags suggest <niche>":                       "Get niche hashtag suggestions",
        "hashtags niches":                                "List available niches",
        "channel audit [--niche fitness]":                "Channel optimization tips",
        "channel competitor <channel-url>":               "Analyze competitor channel",
        "channel keywords <niche>":                       "Research SEO keywords",
        "config set api_key YOUR_KEY":                    "Set YouTube API key",
        "help":                                           "Show this help",
        "quit / exit":                                    "Exit REPL",
    }

    while True:
        try:
            line = skin.get_input(pt_session, context="youtube")
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
