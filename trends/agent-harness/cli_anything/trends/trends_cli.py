#!/usr/bin/env python3
"""Trends CLI — scrape YouTube & TikTok viral trends, optimize your accounts.

Usage:
    # Get YouTube trending
    cli-anything-trends trends youtube --region US --category music

    # Get TikTok trending (with cookies)
    cli-anything-trends trends tiktok --region US

    # Combined trend report
    cli-anything-trends trends report --region US --niche fitness

    # Account optimization pack
    cli-anything-trends trends optimize --platform tiktok --niche fitness --followers 1500

    # Content calendar (2 weeks)
    cli-anything-trends trends calendar --niche fitness --weeks 2

    # Hashtag packs
    cli-anything-trends trends hashtags --platform all --niche lifestyle

    # Interactive REPL
    cli-anything-trends
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.trends.core.session import Session
from cli_anything.trends.core import youtube as yt_mod
from cli_anything.trends.core import tiktok as tt_mod
from cli_anything.trends.core import analyzer as analyzer_mod
from cli_anything.trends.core import optimizer as optimizer_mod
from cli_anything.trends.utils.config import (
    get_youtube_api_key,
    get_tiktok_api_key,
    get_tiktok_cookies,
    load_config,
    save_config,
    CONFIG_FILE,
)

_session: Optional[Session] = None
_json_output = False
_repl_mode = False
_yt_api_key: Optional[str] = None
_tt_api_key: Optional[str] = None
_tt_cookies: Optional[dict] = None


def get_session() -> Session:
    global _session
    if _session is None:
        from pathlib import Path
        sf = str(Path.home() / ".cli-anything-trends" / "session.json")
        _session = Session(session_file=sf)
    return _session


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


# ── Main CLI Group ──────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.option("--yt-key", "yt_key_opt", default=None, envvar="YOUTUBE_API_KEY",
              help="YouTube Data API v3 key")
@click.option("--tt-key", "tt_key_opt", default=None, envvar="TIKTOK_RESEARCH_API_KEY",
              help="TikTok Research API key (optional)")
@click.option("--tt-cookies", "tt_cookies_opt", default=None,
              help="TikTok browser cookies string (key=val; key2=val2)")
@click.pass_context
def cli(ctx, use_json, yt_key_opt, tt_key_opt, tt_cookies_opt):
    """Trends CLI — viral trend scraper & account optimizer for YouTube and TikTok."""
    global _json_output, _yt_api_key, _tt_api_key, _tt_cookies
    _json_output = use_json

    # Resolve API keys (errors shown lazily when commands actually need them)
    try:
        _yt_api_key = get_youtube_api_key(yt_key_opt)
    except ValueError:
        _yt_api_key = None

    _tt_api_key = get_tiktok_api_key(tt_key_opt)
    _tt_cookies = get_tiktok_cookies(tt_cookies_opt)

    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── Trends Command Group ─────────────────────────────────────────────────────

@cli.group()
def trends():
    """Trend scraping — YouTube, TikTok, hashtags, music, and reports."""
    pass


@trends.command("youtube")
@click.option("--region", "-r", default="US", show_default=True,
              help="Country code (US, GB, CA, AU, DE, FR, JP, KR, BR, IN)")
@click.option("--category", "-c", default="all", show_default=True,
              type=click.Choice(
                  ["all", "music", "gaming", "entertainment", "news", "howto",
                   "sports", "film", "comedy", "science"],
                  case_sensitive=False,
              ),
              help="Video category filter")
@click.option("--max", "-n", "max_results", default=50, show_default=True,
              help="Max videos to fetch (1-50)")
@handle_error
def trends_youtube(region, category, max_results):
    """Fetch YouTube trending videos and extract hashtags."""
    if not _yt_api_key:
        raise ValueError(
            "YouTube API key required.\n"
            "  export YOUTUBE_API_KEY=<key>  OR\n"
            "  cli-anything-trends config set youtube_api_key <key>\n"
            "  Free key: https://console.cloud.google.com → YouTube Data API v3"
        )
    result = yt_mod.fetch_trending(
        _yt_api_key, region=region, category=category, max_results=max_results
    )
    get_session().record("trends youtube", {"region": region, "category": category}, result)
    count = result.get("video_count", 0)
    htag_count = len(result.get("hashtags", []))
    output(result, f"✓ YouTube trending ({region}/{category}): {count} videos, {htag_count} hashtags")


@trends.command("tiktok")
@click.option("--region", "-r", default="US", show_default=True,
              help="Region code (US, GB, DE, etc.)")
@click.option("--count", "-n", default=20, show_default=True,
              help="Number of trending videos to fetch")
@handle_error
def trends_tiktok(region, count):
    """Fetch TikTok trending videos, sounds, and hashtags.

    Auth priority: Research API key > browser cookies > public scrape.
    To add cookies: cli-anything-trends config set tiktok_cookies "sessionid=xxx; ttwid=xxx"
    """
    result = tt_mod.fetch_trending(
        access_token=_tt_api_key,
        cookies=_tt_cookies or None,
        region=region,
        count=count,
    )
    get_session().record("trends tiktok", {"region": region, "count": count}, result)
    source = result.get("source", "unknown")
    count_got = result.get("video_count", 0)
    output(result, f"✓ TikTok trending ({region}, source={source}): {count_got} videos")


@trends.command("music")
@click.option("--region", "-r", default="US", show_default=True,
              help="Country code for YouTube music trends")
@click.option("--max", "-n", "max_results", default=50, show_default=True)
@handle_error
def trends_music(region, max_results):
    """Get trending music — YouTube music chart + TikTok sounds."""
    if not _yt_api_key:
        raise ValueError("YouTube API key required. Run: cli-anything-trends config set youtube_api_key <key>")

    yt_music = yt_mod.fetch_trending_music(_yt_api_key, region=region, max_results=max_results)
    tt_sounds: list[dict] = []

    if _tt_cookies:
        try:
            from cli_anything.trends.utils.tiktok_backend import cookie_get_trending_sounds
            tt_sounds = cookie_get_trending_sounds(_tt_cookies, count=20)
        except Exception:
            pass

    result = {
        "youtube_music_trends": yt_music.get("music_trends", [])[:20],
        "youtube_music_videos": yt_music.get("videos", [])[:10],
        "tiktok_sounds": tt_sounds[:20],
        "youtube_hashtags": yt_music.get("hashtags", [])[:15],
    }
    get_session().record("trends music", {"region": region}, result)
    yt_count = len(result["youtube_music_trends"])
    tt_count = len(result["tiktok_sounds"])
    output(result, f"✓ Music trends: {yt_count} YouTube artists, {tt_count} TikTok sounds")


@trends.command("hashtags")
@click.option("--platform", "-p", default="all",
              type=click.Choice(["all", "youtube", "tiktok"], case_sensitive=False),
              show_default=True)
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--niche", "-n", default="general", help="Content niche for scoring context")
@click.option("--top", "-t", default=30, show_default=True, help="Number of top hashtags")
@handle_error
def trends_hashtags(platform, region, niche, top):
    """Get ranked trending hashtags across platforms with copy-paste packs."""
    yt_hashtags = []
    tt_hashtags = []

    if platform in ("all", "youtube"):
        if not _yt_api_key:
            raise ValueError("YouTube API key required for YouTube hashtags.")
        yt_data = yt_mod.fetch_trending(_yt_api_key, region=region)
        yt_hashtags = yt_data.get("hashtags", [])

    if platform in ("all", "tiktok"):
        tt_data = tt_mod.fetch_trending(
            access_token=_tt_api_key,
            cookies=_tt_cookies or None,
            region=region,
        )
        tt_hashtags = tt_data.get("hashtags", [])

    merged = analyzer_mod.merge_hashtags(yt_hashtags, tt_hashtags)[:top]

    packs = {
        "tiktok_pack": " ".join(h["hashtag"] for h in merged[:5]),
        "youtube_pack": " ".join(h["hashtag"] for h in merged[:3]),
        "instagram_pack": " ".join(h["hashtag"] for h in merged[:30]),
    }

    result = {
        "niche": niche,
        "region": region,
        "platform": platform,
        "hashtag_count": len(merged),
        "top_hashtags": merged,
        "copy_paste_packs": packs,
        "cross_platform_tags": [h["hashtag"] for h in merged if h.get("cross_platform")],
    }
    get_session().record("trends hashtags", {"platform": platform, "region": region}, result)
    cp_count = len(result["cross_platform_tags"])
    output(result, f"✓ {len(merged)} hashtags ({cp_count} cross-platform)")


@trends.command("report")
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--niche", "-n", default="general", help="Your content niche")
@click.option("--category", "-c", default="all", show_default=True,
              type=click.Choice(["all", "music", "gaming", "entertainment", "news",
                                  "howto", "sports", "film", "comedy", "science"],
                                case_sensitive=False))
@handle_error
def trends_report(region, niche, category):
    """Generate a full cross-platform trend intelligence report."""
    yt_data = None
    tt_data = None

    if _yt_api_key:
        yt_data = yt_mod.fetch_trending(
            _yt_api_key, region=region, category=category, max_results=50
        )
    else:
        click.echo("⚠ YouTube API key not set — skipping YouTube data.", err=True)

    tt_data = tt_mod.fetch_trending(
        access_token=_tt_api_key,
        cookies=_tt_cookies or None,
        region=region,
        count=20,
    )

    report = analyzer_mod.build_trend_report(
        youtube_data=yt_data,
        tiktok_data=tt_data,
        region=region,
    )
    report["niche"] = niche
    get_session().record("trends report", {"region": region, "niche": niche}, report)

    total = report.get("total_videos_analyzed", 0)
    tags = len(report.get("top_hashtags", []))
    themes = len(report.get("content_themes", []))
    output(report, f"✓ Trend report: {total} videos, {tags} hashtags, {themes} content themes")


@trends.command("optimize")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["tiktok", "youtube", "youtube_shorts", "instagram"],
                                case_sensitive=False),
              help="Platform to optimize for")
@click.option("--niche", "-n", default="general", help="Your content niche")
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--followers", "-f", default=0, type=int, help="Current follower count")
@handle_error
def trends_optimize(platform, niche, region, followers):
    """Generate a full account optimization guide using live trend data."""
    yt_data = None
    tt_data = None

    if _yt_api_key:
        yt_data = yt_mod.fetch_trending(_yt_api_key, region=region)
    tt_data = tt_mod.fetch_trending(
        access_token=_tt_api_key,
        cookies=_tt_cookies or None,
        region=region,
    )

    report = analyzer_mod.build_trend_report(
        youtube_data=yt_data,
        tiktok_data=tt_data,
        region=region,
    )
    optimization = optimizer_mod.generate_account_optimization(
        report, platform=platform, niche=niche, current_followers=followers
    )
    get_session().record(
        "trends optimize",
        {"platform": platform, "niche": niche, "followers": followers},
        optimization,
    )
    phase = optimization.get("growth_phase", "")
    output(optimization, f"✓ Optimization guide for {platform} ({niche}) — Phase: {phase}")


@trends.command("calendar")
@click.option("--niche", "-n", default="general", help="Your content niche")
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--platforms", "-p", multiple=True,
              type=click.Choice(["tiktok", "youtube_shorts", "instagram", "youtube"],
                                case_sensitive=False),
              help="Platforms to schedule for (repeatable, default: tiktok youtube_shorts instagram)")
@click.option("--weeks", "-w", default=2, type=int, show_default=True,
              help="Number of weeks to plan (1-4)")
@handle_error
def trends_calendar(niche, region, platforms, weeks):
    """Generate a content calendar with trending topics and optimal posting times."""
    platforms = list(platforms) if platforms else ["tiktok", "youtube_shorts", "instagram"]
    weeks = max(1, min(weeks, 4))

    yt_data = None
    tt_data = None

    if _yt_api_key:
        yt_data = yt_mod.fetch_trending(_yt_api_key, region=region)
    tt_data = tt_mod.fetch_trending(
        access_token=_tt_api_key,
        cookies=_tt_cookies or None,
        region=region,
    )

    report = analyzer_mod.build_trend_report(
        youtube_data=yt_data,
        tiktok_data=tt_data,
        region=region,
    )
    calendar = optimizer_mod.generate_content_calendar(
        report, niche=niche, platforms=platforms, weeks=weeks
    )
    get_session().record(
        "trends calendar",
        {"niche": niche, "platforms": platforms, "weeks": weeks},
        calendar,
    )
    total_posts = calendar.get("total_posts", 0)
    output(calendar, f"✓ {weeks}-week content calendar: {total_posts} posts across {len(platforms)} platforms")


@trends.command("hashtag-info")
@click.argument("hashtag")
@handle_error
def trends_hashtag_info(hashtag):
    """Get public stats for a specific TikTok hashtag."""
    result = tt_mod.fetch_hashtag_info(hashtag)
    output(result, f"✓ Hashtag info: {hashtag}")


# ── Config Command Group ────────────────────────────────────────────────────

@cli.group()
def config():
    """Configuration — API keys, cookies, and settings."""
    pass


@config.command("set")
@click.argument("key", type=click.Choice(
    ["youtube_api_key", "tiktok_api_key", "tiktok_cookies", "default_region", "default_niche"]
))
@click.argument("value")
def config_set(key, value):
    """Set a configuration value."""
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)
    display = value[:12] + "..." if key.endswith("_key") and len(value) > 12 else value
    output({"key": key, "value": display}, f"✓ Set {key}")


@config.command("get")
@click.argument("key", required=False)
def config_get(key):
    """Get a configuration value or show all."""
    cfg = load_config()
    if key:
        val = cfg.get(key)
        if val:
            masked = val[:12] + "..." if key.endswith("_key") and len(val) > 12 else val
            output({"key": key, "value": masked}, f"{key} = {masked}")
        else:
            output({"key": key, "value": None}, f"{key} is not set")
    else:
        masked = {}
        for k, v in cfg.items():
            masked[k] = str(v)[:12] + "..." if k.endswith("_key") and len(str(v)) > 12 else v
        output(masked if masked else {}, "Configuration:" if masked else "No configuration set.")


@config.command("delete")
@click.argument("key")
def config_delete(key):
    """Delete a configuration value."""
    cfg = load_config()
    if key in cfg:
        del cfg[key]
        save_config(cfg)
        output({"deleted": key}, f"✓ Deleted {key}")
    else:
        output({"error": f"{key} not found"}, f"{key} not in config")


@config.command("path")
def config_path():
    """Show the config file path."""
    output({"path": str(CONFIG_FILE)}, f"Config: {CONFIG_FILE}")


@config.command("setup")
def config_setup():
    """Interactive setup wizard for API keys."""
    click.echo("\n=== Trends CLI Setup ===\n")
    click.echo("YouTube Data API v3 key (required for YouTube trends):")
    click.echo("  Get free key: https://console.cloud.google.com → APIs → YouTube Data API v3\n")

    yt_key = click.prompt("YouTube API key (press Enter to skip)", default="", show_default=False)
    if yt_key.strip():
        cfg = load_config()
        cfg["youtube_api_key"] = yt_key.strip()
        save_config(cfg)
        click.echo("✓ YouTube API key saved.")

    click.echo("\nTikTok Research API key (optional — for official TikTok data):")
    click.echo("  Apply: https://developers.tiktok.com/products/research-api/\n")

    tt_key = click.prompt("TikTok Research API key (press Enter to skip)", default="", show_default=False)
    if tt_key.strip():
        cfg = load_config()
        cfg["tiktok_api_key"] = tt_key.strip()
        save_config(cfg)
        click.echo("✓ TikTok API key saved.")

    click.echo("\nTikTok browser cookies (for cookie-based trending scrape):")
    click.echo("  1. Open TikTok in Chrome")
    click.echo("  2. DevTools → Application → Cookies → tiktok.com")
    click.echo("  3. Copy: sessionid, ttwid, tt_webid values")
    click.echo("  4. Format: sessionid=xxx; ttwid=yyy\n")

    tt_cookies = click.prompt("TikTok cookies (press Enter to skip)", default="", show_default=False)
    if tt_cookies.strip():
        cfg = load_config()
        cfg["tiktok_cookies"] = tt_cookies.strip()
        save_config(cfg)
        click.echo("✓ TikTok cookies saved.")

    click.echo("\n✓ Setup complete! Try: cli-anything-trends trends report --niche fitness\n")


# ── Session Command Group ───────────────────────────────────────────────────

@cli.group()
def session():
    """Session management — history, undo, redo."""
    pass


@session.command("status")
def session_status():
    """Show session status."""
    sess = get_session()
    output(sess.status())


@session.command("history")
@click.option("--limit", "-n", type=int, default=20, help="Max entries")
def session_history(limit):
    """Show command history."""
    sess = get_session()
    entries = sess.history(limit=limit)
    if not entries:
        output([], "No history.")
        return
    output(entries, f"History ({len(entries)} entries):")


@session.command("undo")
def session_undo():
    """Undo last command."""
    sess = get_session()
    entry = sess.undo()
    if entry:
        output(entry.to_dict(), f"✓ Undone: {entry.command}")
    else:
        output({"error": "Nothing to undo"}, "Nothing to undo")


@session.command("redo")
def session_redo():
    """Redo last undone command."""
    sess = get_session()
    entry = sess.redo()
    if entry:
        output(entry.to_dict(), f"✓ Redone: {entry.command}")
    else:
        output({"error": "Nothing to redo"}, "Nothing to redo")


# ── REPL ────────────────────────────────────────────────────────────────────

@cli.command("repl", hidden=True)
def repl():
    """Enter interactive REPL mode."""
    global _repl_mode
    _repl_mode = True

    try:
        from cli_anything.anygen.utils.repl_skin import ReplSkin
    except ImportError:
        # Fallback minimal REPL if repl_skin not installed
        _minimal_repl()
        return

    skin = ReplSkin("trends", version="1.0.0")
    skin.print_banner()
    pt_session = skin.create_prompt_session()

    commands = {
        "trends youtube": "Fetch YouTube trending videos",
        "trends tiktok": "Fetch TikTok trending",
        "trends music": "Get trending music",
        "trends hashtags": "Get ranked hashtag packs",
        "trends report": "Full cross-platform report",
        "trends optimize --platform <p> --niche <n>": "Account optimization guide",
        "trends calendar --niche <n>": "2-week content calendar",
        "config setup": "Interactive API key setup",
        "config set <key> <val>": "Set config value",
        "session history": "Command history",
        "help": "Show this help",
        "quit / exit": "Exit",
    }

    while True:
        try:
            line = skin.get_input(pt_session, context="trends")
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


def _minimal_repl():
    """Fallback REPL when repl_skin is unavailable."""
    click.echo("Trends CLI REPL — type 'help' for commands, 'quit' to exit\n")
    while True:
        try:
            line = click.prompt("trends", prompt_suffix="> ")
        except (EOFError, KeyboardInterrupt):
            click.echo("\nGoodbye!")
            break
        if not line.strip():
            continue
        if line.strip() in ("quit", "exit", "q"):
            click.echo("Goodbye!")
            break
        parts = line.strip().split()
        try:
            cli.main(parts, standalone_mode=False)
        except SystemExit:
            pass
        except Exception as e:
            click.echo(f"Error: {e}", err=True)


def main():
    cli()


if __name__ == "__main__":
    main()
