#!/usr/bin/env python3
"""Social Trends CLI — Scrape viral trends, hashtags, and music from TikTok & YouTube.
Optimize social media accounts and learn theme page strategies.

Usage:
    # Fetch trending data
    cli-anything-social-trends trends youtube --region US
    cli-anything-social-trends trends tiktok --region US
    cli-anything-social-trends trends music tiktok

    # Hashtag tools
    cli-anything-social-trends hashtags niche fitness --platform tiktok
    cli-anything-social-trends hashtags optimize --niche fitness --platform tiktok

    # Account optimization
    cli-anything-social-trends optimize schedule tiktok
    cli-anything-social-trends optimize profile tiktok
    cli-anything-social-trends optimize calendar --niche fitness --platforms tiktok,instagram

    # Theme pages
    cli-anything-social-trends theme niches
    cli-anything-social-trends theme niche finance
    cli-anything-social-trends theme checklist
    cli-anything-social-trends theme monetize --followers 15000

    # Interactive REPL
    cli-anything-social-trends
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_trends.core.session import Session
from cli_anything.social_trends.utils.trends_backend import (
    load_config, save_config, get_youtube_api_key, get_region,
    validate_platform, CONFIG_FILE, PLATFORMS, SUPPORTED_REGIONS,
)

_session: Optional[Session] = None
_json_output = False
_repl_mode = False


def get_session() -> Session:
    global _session
    if _session is None:
        from pathlib import Path
        sf = str(Path.home() / ".cli-anything-social-trends" / "session.json")
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
        except (RuntimeError, ValueError, OSError, TimeoutError) as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# ── Main CLI group ────────────────────────────────────────────────


@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx, use_json):
    """Social Trends CLI — viral trends, hashtags, music, and account optimization."""
    global _json_output
    _json_output = use_json
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── trends group ──────────────────────────────────────────────────


@cli.group()
def trends():
    """Fetch trending content from YouTube and TikTok."""
    pass


@trends.command("youtube")
@click.option("--region", "-r", default=None, help="2-letter region code (default: US)")
@click.option("--api-key", "api_key", default=None, envvar="YOUTUBE_API_KEY",
              help="YouTube Data API v3 key (falls back to web scrape if absent)")
@click.option("--category", "-c", default="0", help="YouTube category ID (0=all)")
@click.option("--limit", "-n", type=int, default=20, help="Max results")
@click.option("--hashtags-only", is_flag=True, help="Only show extracted hashtags")
@handle_error
def trends_youtube(region, api_key, category, limit, hashtags_only):
    """Fetch YouTube trending videos and extract viral hashtags."""
    from cli_anything.social_trends.core import youtube as yt

    region = get_region(region)
    resolved_key = get_youtube_api_key(api_key)

    if resolved_key:
        click.echo(f"Fetching YouTube trending via API (region={region})...")
        videos = yt.fetch_trending_api(resolved_key, region=region,
                                       category_id=category, max_results=limit)
    else:
        click.echo(f"No API key — scraping YouTube trending (region={region})...")
        videos = yt.fetch_trending_scrape(region=region, max_results=limit)

    get_session().record("trends youtube", {"region": region}, {"count": len(videos)})

    if hashtags_only:
        tags = yt.aggregate_trending_hashtags(videos, top_n=30)
        output(tags, f"Top {len(tags)} hashtags from YouTube trending:")
    else:
        output(videos, f"Found {len(videos)} trending YouTube videos:")


@trends.command("tiktok")
@click.option("--region", "-r", default=None, help="2-letter region code (default: US)")
@click.option("--limit", "-n", type=int, default=30, help="Max hashtag results")
@handle_error
def trends_tiktok(region, limit):
    """Scrape TikTok trending hashtags from Discover page."""
    from cli_anything.social_trends.core import tiktok as tt

    region = get_region(region)
    click.echo(f"Fetching TikTok trending hashtags (region={region})...")
    hashtags = tt.fetch_trending_hashtags(region=region, max_results=limit)
    get_session().record("trends tiktok", {"region": region}, {"count": len(hashtags)})
    output(hashtags, f"Found {len(hashtags)} trending TikTok hashtags:")


@trends.command("sounds")
@click.argument("platform", type=click.Choice(["tiktok", "youtube"], case_sensitive=False))
@click.option("--region", "-r", default=None, help="2-letter region code")
@click.option("--niche", "-n", default=None, help="Niche for curated sound suggestions")
@handle_error
def trends_sounds(platform, region, niche):
    """Fetch trending sounds/music for a platform."""
    from cli_anything.social_trends.core import music as mu

    region = get_region(region)
    if platform.lower() == "tiktok":
        click.echo(f"Fetching trending TikTok sounds (region={region})...")
        sounds = mu.fetch_trending_sounds(region=region)
        output(sounds, f"Found {len(sounds)} trending sounds:")
    else:
        click.echo(f"Fetching YouTube Music trending charts (region={region})...")
        tracks = mu.fetch_youtube_music_trending(region=region)
        output(tracks, f"Found {len(tracks)} trending tracks:")

    if niche:
        suggestions = mu.suggest_sounds_for_niche(niche)
        output(suggestions, f"\nSound style suggestions for '{niche}' niche:")

    strategy = mu.get_music_strategy(platform)
    if not _json_output and strategy:
        click.echo(f"\nStrategy for {platform}:")
        _print_dict(strategy)

    get_session().record("trends sounds", {"platform": platform}, {})


@trends.command("all")
@click.option("--region", "-r", default=None, help="2-letter region code")
@click.option("--niche", "-n", default=None, help="Filter/focus on a niche")
@handle_error
def trends_all(region, niche):
    """Fetch all trending data: YouTube, TikTok hashtags, and sounds."""
    from cli_anything.social_trends.core import youtube as yt
    from cli_anything.social_trends.core import tiktok as tt
    from cli_anything.social_trends.core import music as mu

    region = get_region(region)
    result = {"region": region}

    click.echo(f"[1/3] TikTok trending hashtags (region={region})...")
    try:
        tt_tags = tt.fetch_trending_hashtags(region=region, max_results=20)
        result["tiktok_hashtags"] = tt_tags
    except Exception as e:
        result["tiktok_hashtags"] = {"error": str(e)}

    click.echo(f"[2/3] YouTube trending (no API key — scraping)...")
    try:
        yt_videos = yt.fetch_trending_scrape(region=region, max_results=15)
        result["youtube_trending"] = yt.aggregate_trending_hashtags(yt_videos, top_n=20)
        result["youtube_top_channels"] = yt.aggregate_top_channels(yt_videos)
    except Exception as e:
        result["youtube_trending"] = {"error": str(e)}

    if niche:
        click.echo(f"[3/3] Niche hashtags for '{niche}'...")
        result["niche_hashtags"] = tt.get_niche_hashtags(niche)
        result["sound_suggestions"] = mu.suggest_sounds_for_niche(niche)
    else:
        result["sound_strategy"] = {p: mu.get_music_strategy(p) for p in ["tiktok", "youtube_shorts"]}

    get_session().record("trends all", {"region": region, "niche": niche}, {})
    output(result, "\nAll trending data fetched:")


# ── hashtags group ────────────────────────────────────────────────


@cli.group()
def hashtags():
    """Hashtag strategy tools — niche tags, optimization, and scoring."""
    pass


@hashtags.command("niche")
@click.argument("niche")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(PLATFORMS, case_sensitive=False))
@click.option("--no-universal", is_flag=True, help="Exclude universal tags (#fyp, etc.)")
@click.option("--format", "fmt", default="list",
              type=click.Choice(["list", "inline", "newline", "spaced"]))
@handle_error
def hashtags_niche(niche, platform, no_universal, fmt):
    """Get curated hashtags for a specific niche."""
    from cli_anything.social_trends.core import tiktok as tt
    from cli_anything.social_trends.core.hashtags import format_hashtags

    tags = tt.get_niche_hashtags(niche, include_universal=not no_universal)
    if fmt in ("inline", "newline", "spaced"):
        click.echo(format_hashtags(tags, style=fmt))
    else:
        output(tags, f"Hashtags for '{niche}' niche on {platform}:")
    get_session().record("hashtags niche", {"niche": niche}, {"count": len(tags)})


@hashtags.command("optimize")
@click.option("--niche", "-n", required=True, help="Your content niche")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(PLATFORMS, case_sensitive=False))
@click.option("--branded", "-b", multiple=True, help="Your branded tags (repeatable)")
@click.option("--format", "fmt", default="list",
              type=click.Choice(["list", "inline", "newline"]))
@handle_error
def hashtags_optimize(niche, platform, branded, fmt):
    """Build an optimal hashtag set for a post using trending + niche tags."""
    from cli_anything.social_trends.core import tiktok as tt
    from cli_anything.social_trends.core.hashtags import build_optimal_set, score_hashtag_set, format_hashtags

    click.echo(f"Fetching trending tags to build optimal set for '{niche}' on {platform}...")
    try:
        trending = tt.fetch_trending_hashtags(max_results=15)
    except Exception:
        trending = []

    niche_tags = tt.get_niche_hashtags(niche, include_universal=True)
    optimal = build_optimal_set(
        niche_tags=niche_tags,
        trending_tags=trending,
        platform=platform,
        branded_tags=list(branded) if branded else None,
    )

    score_data = score_hashtag_set([{"hashtag": t} for t in optimal])

    if fmt in ("inline", "newline"):
        click.echo(format_hashtags(optimal, style=fmt))
    else:
        output({"hashtags": optimal, "count": len(optimal), "score": score_data})

    if not _json_output:
        click.echo(f"\nScore: {score_data['score']}/100 — {score_data['recommendation']}")

    get_session().record("hashtags optimize", {"niche": niche, "platform": platform},
                         {"count": len(optimal), "score": score_data["score"]})


@hashtags.command("score")
@click.argument("tags", nargs=-1, required=True)
@handle_error
def hashtags_score(tags):
    """Score a hashtag set (provide tags as arguments)."""
    from cli_anything.social_trends.core.hashtags import score_hashtag_set

    tag_list = [{"hashtag": t if t.startswith("#") else f"#{t}"} for t in tags]
    result = score_hashtag_set(tag_list)
    output(result, f"Score: {result['score']}/100")


@hashtags.command("niches")
@handle_error
def hashtags_niches():
    """List all supported niches with curated hashtag sets."""
    from cli_anything.social_trends.core.tiktok import list_niches
    niches = list_niches()
    output(niches, "Supported niches:")


# ── optimize group ────────────────────────────────────────────────


@cli.group()
def optimize():
    """Account optimization — posting schedule, profile audit, content calendar."""
    pass


@optimize.command("schedule")
@click.argument("platform", type=click.Choice(PLATFORMS + ["all"], case_sensitive=False))
@click.option("--timezone", "-tz", default="EST", help="Your timezone abbreviation")
@handle_error
def optimize_schedule(platform, timezone):
    """Show optimal posting times for a platform."""
    from cli_anything.social_trends.core.optimizer import get_optimal_times, get_posting_frequency

    if platform.lower() == "all":
        results = {}
        for p in PLATFORMS:
            results[p] = {
                "times": get_optimal_times(p, timezone),
                "frequency": get_posting_frequency(p),
            }
        output(results, "Optimal posting schedules for all platforms:")
    else:
        times = get_optimal_times(platform, timezone)
        freq = get_posting_frequency(platform)
        output({"times": times, "frequency": freq},
               f"Optimal posting schedule for {platform} ({timezone}):")

    get_session().record("optimize schedule", {"platform": platform}, {})


@optimize.command("profile")
@click.argument("platform", type=click.Choice(["tiktok", "instagram", "youtube", "all"],
                                              case_sensitive=False))
@handle_error
def optimize_profile(platform):
    """Get profile optimization checklist for a platform."""
    from cli_anything.social_trends.core.optimizer import audit_profile

    if platform.lower() == "all":
        results = {}
        for p in ["tiktok", "instagram", "youtube"]:
            results[p] = audit_profile(p)
        output(results, "Profile optimization checklists:")
    else:
        checklist = audit_profile(platform)
        output(checklist, f"Profile optimization for {platform} ({len(checklist)} items):")

    get_session().record("optimize profile", {"platform": platform}, {})


@optimize.command("calendar")
@click.option("--niche", "-n", required=True, help="Content niche")
@click.option("--platforms", "-p", default="tiktok,instagram",
              help="Comma-separated platforms (e.g. tiktok,instagram,youtube)")
@click.option("--days", "-d", type=int, default=7, help="Number of days (default 7)")
@click.option("--start", "-s", default=None, help="Start date (YYYY-MM-DD, default today)")
@handle_error
def optimize_calendar(niche, platforms, days, start):
    """Generate a content calendar with post ideas and optimal times."""
    from cli_anything.social_trends.core.optimizer import generate_content_calendar

    platform_list = [p.strip() for p in platforms.split(",")]
    calendar = generate_content_calendar(
        niche=niche,
        platforms=platform_list,
        days=days,
        start_date=start,
    )
    output(calendar, f"{days}-day content calendar for '{niche}' niche:")
    get_session().record("optimize calendar", {"niche": niche, "days": days}, {"days": len(calendar)})


@optimize.command("growth")
@click.option("--start-followers", "-s", type=int, required=True, help="Followers at start of period")
@click.option("--end-followers", "-e", type=int, required=True, help="Current followers")
@click.option("--days", "-d", type=int, required=True, help="Number of days measured")
@handle_error
def optimize_growth(start_followers, end_followers, days):
    """Calculate and assess your account growth rate."""
    from cli_anything.social_trends.core.optimizer import calculate_growth_rate

    result = calculate_growth_rate(start_followers, end_followers, days)
    output(result, "Growth analysis:")
    get_session().record("optimize growth", {"start": start_followers, "end": end_followers}, result)


# ── theme group ───────────────────────────────────────────────────


@cli.group()
def theme():
    """Theme page strategy — convert, grow, and monetize niche pages."""
    pass


@theme.command("about")
def theme_about():
    """What is a theme page? Get the overview."""
    from cli_anything.social_trends.core.theme_pages import DEFINITION
    click.echo(DEFINITION)


@theme.command("niches")
@handle_error
def theme_niches():
    """Rank all niches by theme page potential."""
    from cli_anything.social_trends.core.theme_pages import rank_niches

    ranked = rank_niches()
    output(ranked, f"Niche rankings ({len(ranked)} niches):")
    get_session().record("theme niches", {}, {"count": len(ranked)})


@theme.command("niche")
@click.argument("niche")
@handle_error
def theme_niche(niche):
    """Evaluate a specific niche for theme page potential."""
    from cli_anything.social_trends.core.theme_pages import evaluate_niche

    result = evaluate_niche(niche)
    output(result, f"Niche evaluation: {niche}")
    get_session().record("theme niche", {"niche": niche}, result)


@theme.command("checklist")
@click.option("--phase", "-p", default=None, help="Filter to specific phase (e.g. 'monetization')")
@handle_error
def theme_checklist(phase):
    """Get the theme page setup checklist (all 6 phases)."""
    from cli_anything.social_trends.core.theme_pages import get_setup_checklist

    checklist = get_setup_checklist(phase)
    output(checklist, f"Theme page setup checklist ({len(checklist)} phases):")
    get_session().record("theme checklist", {"phase": phase}, {})


@theme.command("repost")
@click.argument("platform", type=click.Choice(["tiktok", "instagram", "youtube_shorts"],
                                              case_sensitive=False))
@handle_error
def theme_repost(platform):
    """Get the content reposting guide for a platform."""
    from cli_anything.social_trends.core.theme_pages import get_repost_guide

    guide = get_repost_guide(platform)
    output(guide, f"Reposting guide for {platform}:")
    get_session().record("theme repost", {"platform": platform}, {})


@theme.command("monetize")
@click.option("--followers", "-f", type=int, default=None, help="Current follower count")
@handle_error
def theme_monetize(followers):
    """Get monetization roadmap based on follower count."""
    from cli_anything.social_trends.core.theme_pages import get_monetization_roadmap

    roadmap = get_monetization_roadmap(followers)
    label = f"at {followers:,} followers" if followers else "(all tiers)"
    output(roadmap, f"Monetization roadmap {label}:")
    get_session().record("theme monetize", {"followers": followers}, {})


# ── config group ──────────────────────────────────────────────────


@cli.group()
def config():
    """Configuration management — API keys and defaults."""
    pass


@config.command("set")
@click.argument("key", type=click.Choice(["youtube_api_key", "region"]))
@click.argument("value")
def config_set(key, value):
    """Set a configuration value."""
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)
    display = value[:8] + "..." if key == "youtube_api_key" and len(value) > 8 else value
    output({"key": key, "value": display}, f"Set {key} = {display}")


@config.command("get")
@click.argument("key", required=False)
def config_get(key):
    """Show configuration."""
    cfg = load_config()
    if key:
        val = cfg.get(key, "(not set)")
        if key == "youtube_api_key" and len(str(val)) > 8:
            val = str(val)[:8] + "..."
        output({key: val}, f"{key} = {val}")
    else:
        masked = {k: v[:8] + "..." if k == "youtube_api_key" and len(v) > 8 else v
                  for k, v in cfg.items()}
        output(masked if masked else {}, "Configuration" if masked else "No configuration set")


@config.command("path")
def config_path():
    """Show config file path."""
    output({"path": str(CONFIG_FILE)}, f"Config: {CONFIG_FILE}")


# ── session group ─────────────────────────────────────────────────


@cli.group()
def session():
    """Session management — history and undo/redo."""
    pass


@session.command("status")
def session_status():
    output(get_session().status())


@session.command("history")
@click.option("--limit", "-n", type=int, default=20)
def session_history(limit):
    entries = get_session().history(limit=limit)
    output(entries, f"History ({len(entries)} entries):")


@session.command("undo")
def session_undo():
    entry = get_session().undo()
    if entry:
        output(entry.to_dict(), f"Undone: {entry.command}")
    else:
        output({"error": "Nothing to undo"}, "Nothing to undo")


@session.command("redo")
def session_redo():
    entry = get_session().redo()
    if entry:
        output(entry.to_dict(), f"Redone: {entry.command}")
    else:
        output({"error": "Nothing to redo"}, "Nothing to redo")


# ── REPL ──────────────────────────────────────────────────────────


@cli.command("repl", hidden=True)
def repl():
    """Enter interactive REPL mode."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.social_trends.utils.repl_skin import ReplSkin

    skin = ReplSkin("social_trends", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    commands = {
        "trends youtube [--region]":        "Fetch YouTube trending videos + hashtags",
        "trends tiktok [--region]":          "Fetch TikTok trending hashtags",
        "trends sounds <platform>":          "Fetch trending sounds (tiktok/youtube)",
        "trends all [--niche]":              "Fetch all trends at once",
        "hashtags niche <niche>":            "Get curated hashtags for a niche",
        "hashtags optimize --niche <n>":     "Build optimal hashtag set for a post",
        "hashtags niches":                   "List all supported niches",
        "optimize schedule <platform>":      "Show optimal posting times",
        "optimize profile <platform>":       "Get profile optimization checklist",
        "optimize calendar --niche <n>":     "Generate 7-day content calendar",
        "optimize growth -s <n> -e <n> -d <d>": "Calculate growth rate",
        "theme about":                       "What is a theme page?",
        "theme niches":                      "Rank niches by theme page potential",
        "theme niche <niche>":               "Evaluate a specific niche",
        "theme checklist":                   "Get full setup checklist",
        "theme repost <platform>":           "Content reposting guide",
        "theme monetize [--followers N]":    "Monetization roadmap",
        "config set <key> <val>":            "Set youtube_api_key or region",
        "session history":                   "Show command history",
        "help":                              "Show this help",
        "quit / exit":                       "Exit REPL",
    }

    while True:
        try:
            line = skin.get_input(pt_session, context="social-trends")
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
