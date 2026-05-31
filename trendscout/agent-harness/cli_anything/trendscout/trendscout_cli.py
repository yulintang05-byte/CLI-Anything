"""TrendScout CLI — scrape YouTube & TikTok for viral trends, hashtags, and music.

Usage:
    python3 -m cli_anything.trendscout [--json] <command>
    python3 -m cli_anything.trendscout  (launches REPL)
"""

import json
import shlex
import sys
from typing import Any, Optional

import click

from cli_anything.trendscout.core import session as session_mod
from cli_anything.trendscout.core import youtube as yt_mod
from cli_anything.trendscout.core import tiktok as tt_mod
from cli_anything.trendscout.core import trends as trends_mod
from cli_anything.trendscout.core import export as export_mod

# ── Global state ──────────────────────────────────────────────────────────────

_json_output: bool = False
_repl_mode: bool = False


# ── Output helpers ─────────────────────────────────────────────────────────────

def output(data: Any, message: str = "") -> None:
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)


def _print_dict(d: dict, indent: int = 2) -> None:
    pad = " " * indent
    for k, v in d.items():
        if k.startswith("_"):
            continue
        if isinstance(v, dict):
            click.echo(f"{pad}{k}:")
            _print_dict(v, indent + 2)
        elif isinstance(v, list):
            click.echo(f"{pad}{k}: [{len(v)} items]")
        else:
            click.echo(f"{pad}{k}: {v}")


def _print_list(lst: list) -> None:
    if not lst:
        click.echo("  (empty)")
        return
    for item in lst:
        if isinstance(item, dict):
            parts = [f"{k}={v}" for k, v in item.items() if not isinstance(v, (dict, list))]
            click.echo("  " + "  ".join(parts))
        else:
            click.echo(f"  {item}")


def _err(msg: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": msg}), err=True)
    else:
        click.echo(f"Error: {msg}", err=True)


def handle_error(func):
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (RuntimeError, ValueError, KeyError, FileNotFoundError) as e:
            _err(str(e))
            if not _repl_mode:
                sys.exit(1)
        except Exception as e:
            _err(f"Unexpected error: {e}")
            if not _repl_mode:
                sys.exit(1)

    return wrapper


# ── Root CLI ───────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output results as JSON")
@click.version_option("1.0.0", prog_name="trendscout")
@click.pass_context
def cli(ctx: click.Context, use_json: bool) -> None:
    """TrendScout — viral trend intelligence for YouTube & TikTok.

    Scrape trending videos, hashtags, and music. Identify cross-platform
    viral signals to optimise your content strategy.

    \b
    Quick start:
      trendscout trends youtube               # YouTube trending now
      trendscout trends tiktok                # TikTok trending now
      trendscout trends hashtags --niche fitness
      trendscout trends music
      trendscout trends report                # Full cross-platform report
      trendscout config set-key youtube <api_key>
    """
    global _json_output
    _json_output = use_json
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── trends group ──────────────────────────────────────────────────────────────

@cli.group()
def trends():
    """Fetch viral trends from YouTube and TikTok."""
    pass


@trends.command("youtube")
@click.option("--category", default="all", show_default=True,
              help="Category: all, music, gaming, film, sports, etc.")
@click.option("--region", default="US", show_default=True, help="ISO country code")
@click.option("--limit", default=25, show_default=True, type=int, help="Number of videos")
@click.option("--no-cache", is_flag=True, help="Bypass cache")
@handle_error
def trends_youtube(category: str, region: str, limit: int, no_cache: bool) -> None:
    """Fetch YouTube trending videos for a category and region."""
    cache_key = f"yt_{category}_{region}_{limit}"
    if not no_cache:
        cached = session_mod.get_cache(cache_key)
        if cached:
            click.echo("(from cache)")
            output(cached, f"YouTube trending [{category}] [{region}] — {cached.get('video_count', 0)} videos")
            return

    click.echo(f"Fetching YouTube trending [{category}] [{region}]...")
    api_key = session_mod.get_api_key("youtube")
    data = yt_mod.fetch_trending(api_key=api_key, category=category, region=region, limit=limit)
    session_mod.set_cache(cache_key, data)

    if not _json_output:
        from cli_anything.trendscout.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["#", "Title", "Channel", "Views", "Likes", "Top Tags"],
            [
                [
                    str(i + 1),
                    v.get("title", "")[:40],
                    v.get("channel", "")[:20],
                    f"{v.get('view_count', 0):,}",
                    f"{v.get('like_count', 0):,}",
                    " ".join((v.get("tags") or [])[:3])[:25],
                ]
                for i, v in enumerate(data.get("videos", []))
            ]
        )
        click.echo(f"\n  Top hashtags: {', '.join(h['hashtag'] for h in data.get('top_hashtags', [])[:10])}")
    else:
        output(data)


@trends.command("tiktok")
@click.option("--region", default="US", show_default=True, help="ISO country code")
@click.option("--limit", default=20, show_default=True, type=int, help="Number of videos")
@click.option("--no-cache", is_flag=True, help="Bypass cache")
@handle_error
def trends_tiktok(region: str, limit: int, no_cache: bool) -> None:
    """Fetch TikTok trending videos."""
    cache_key = f"tt_{region}_{limit}"
    if not no_cache:
        cached = session_mod.get_cache(cache_key)
        if cached:
            click.echo("(from cache)")
            output(cached, f"TikTok trending [{region}] — {cached.get('video_count', 0)} videos")
            return

    click.echo(f"Fetching TikTok trending [{region}]...")
    api_token = session_mod.get_api_key("tiktok")
    data = tt_mod.fetch_trending(api_token=api_token, limit=limit, region=region)
    session_mod.set_cache(cache_key, data)

    if not _json_output:
        from cli_anything.trendscout.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["#", "Description", "Creator", "Views", "Likes", "Top Tags"],
            [
                [
                    str(i + 1),
                    v.get("description", "")[:40],
                    v.get("username", "")[:20],
                    f"{v.get('view_count', 0):,}",
                    f"{v.get('like_count', 0):,}",
                    " ".join(f"#{t}" for t in (v.get("hashtags") or [])[:3])[:25],
                ]
                for i, v in enumerate(data.get("videos", []))
            ]
        )
        click.echo(f"\n  Top hashtags: {', '.join(h['hashtag'] for h in data.get('top_hashtags', [])[:10])}")
    else:
        output(data)


@trends.command("hashtags")
@click.option("--platform", default="tiktok", show_default=True,
              type=click.Choice(["youtube", "tiktok", "both"]), help="Platform to pull from")
@click.option("--niche", default=None, help="Niche category (fitness, food, fashion, gaming, etc.)")
@click.option("--limit", default=30, show_default=True, type=int)
@click.option("--no-cache", is_flag=True)
@handle_error
def trends_hashtags(platform: str, niche: Optional[str], limit: int, no_cache: bool) -> None:
    """Get trending hashtags, optionally filtered to a niche."""
    cache_key = f"tags_{platform}_{niche}_{limit}"
    if not no_cache:
        cached = session_mod.get_cache(cache_key)
        if cached:
            click.echo("(from cache)")
            _show_hashtags(cached)
            return

    tags = tt_mod.fetch_trending_hashtags(niche=niche, limit=limit)
    session_mod.set_cache(cache_key, tags)
    _show_hashtags(tags)


def _show_hashtags(tags: list) -> None:
    if not _json_output:
        from cli_anything.trendscout.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["Hashtag", "Niche", "Est. Posts", "Virality", "Advice"],
            [
                [
                    t.get("hashtag", ""),
                    t.get("niche", ""),
                    t.get("estimated_posts", ""),
                    str(t.get("virality_score", "")),
                    t.get("recommended_use", "")[:35],
                ]
                for t in tags
            ]
        )
    else:
        output(tags)


@trends.command("music")
@click.option("--limit", default=20, show_default=True, type=int)
@click.option("--no-cache", is_flag=True)
@handle_error
def trends_music(limit: int, no_cache: bool) -> None:
    """Fetch trending TikTok sounds and music."""
    cache_key = f"music_{limit}"
    if not no_cache:
        cached = session_mod.get_cache(cache_key)
        if cached:
            click.echo("(from cache)")
            _show_music(cached)
            return

    click.echo("Fetching trending TikTok music...")
    api_token = session_mod.get_api_key("tiktok")
    sounds = tt_mod.fetch_trending_music(api_token=api_token, limit=limit)
    session_mod.set_cache(cache_key, sounds)
    _show_music(sounds)


def _show_music(sounds: list) -> None:
    if not _json_output:
        from cli_anything.trendscout.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["Title", "Author", "Original", "Videos", "Total Views", "Total Likes"],
            [
                [
                    s.get("title", "")[:35],
                    s.get("author", "")[:20],
                    "Yes" if s.get("original") else "No",
                    f"{s.get('video_count', 0):,}",
                    f"{s.get('total_views', 0):,}",
                    f"{s.get('total_likes', 0):,}",
                ]
                for s in sounds
            ]
        )
    else:
        output(sounds)


@trends.command("report")
@click.option("--region", default="US", show_default=True)
@click.option("--limit", default=20, show_default=True, type=int)
@click.option("--no-cache", is_flag=True)
@handle_error
def trends_report(region: str, limit: int, no_cache: bool) -> None:
    """Full cross-platform trend report (YouTube + TikTok combined)."""
    click.echo("Building cross-platform trend report...")

    yt_key = session_mod.get_api_key("youtube")
    tt_key = session_mod.get_api_key("tiktok")

    yt_data = None
    tt_data = None

    try:
        click.echo("  Fetching YouTube...")
        yt_data = yt_mod.fetch_trending(api_key=yt_key, region=region, limit=limit)
    except Exception as e:
        click.echo(f"  YouTube failed: {e}", err=True)

    try:
        click.echo("  Fetching TikTok...")
        tt_data = tt_mod.fetch_trending(api_token=tt_key, limit=limit, region=region)
    except Exception as e:
        click.echo(f"  TikTok failed: {e}", err=True)

    if not yt_data and not tt_data:
        _err("Both platforms failed. Check your network or set API keys.")
        if not _repl_mode:
            sys.exit(1)
        return

    aggregated = trends_mod.aggregate(youtube_data=yt_data, tiktok_data=tt_data)

    if _json_output:
        output(aggregated)
    else:
        from cli_anything.trendscout.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section("Cross-Platform Top Hashtags")
        skin.table(
            ["Rank", "Hashtag", "Score"],
            [[str(i + 1), e["hashtag"], str(e["score"])]
             for i, e in enumerate(aggregated.get("top_hashtags", [])[:15])]
        )
        cross = aggregated.get("crossplatform_trends", [])
        if cross:
            skin.section("Viral on BOTH Platforms")
            for e in cross[:10]:
                click.echo(f"    {e['hashtag']}  ({', '.join(e['platforms'])})")
        skin.section("Platform Summary")
        for plat, s in aggregated.get("platform_summary", {}).items():
            click.echo(f"  {plat}: {s.get('video_count', 0)} videos  |  method: {s.get('fetch_method', '')}")


# ── recommend group ───────────────────────────────────────────────────────────

@cli.group()
def recommend():
    """Hashtag and content recommendations based on trend data."""
    pass


@recommend.command("hashtags")
@click.option("--niche", required=True, help="Your content niche")
@click.option("--platform", default="both", show_default=True,
              type=click.Choice(["youtube", "tiktok", "both"]))
@handle_error
def recommend_hashtags(niche: str, platform: str) -> None:
    """Get recommended hashtag mix for your niche, ranked by trending data."""
    yt_cached = session_mod.get_cache(f"yt_all_US_25")
    tt_cached = session_mod.get_cache(f"tt_US_20")

    recs = trends_mod.recommend_hashtags(
        niche=niche,
        platform=platform,
        youtube_data=yt_cached,
        tiktok_data=tt_cached,
    )

    if not _json_output:
        from cli_anything.trendscout.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        click.echo(f"\n  Recommended hashtags for niche: {niche} [{platform}]\n")
        skin.table(
            ["Hashtag", "Type", "Trending Score", "Reason"],
            [
                [r["hashtag"], r["type"], str(r["trending_score"]), r["reason"][:40]]
                for r in recs
            ]
        )
        click.echo(f"\n  Copy-paste set: {' '.join(r['hashtag'] for r in recs[:15])}")
    else:
        output(recs)


# ── export group ──────────────────────────────────────────────────────────────

@cli.group()
def export():
    """Export trend data to JSON, CSV, or Markdown."""
    pass


@export.command("json")
@click.option("-o", "--output", "output_path", required=True)
@click.option("--platform", default="both", type=click.Choice(["youtube", "tiktok", "both"]))
@click.option("--region", default="US", show_default=True)
@click.option("--limit", default=25, show_default=True, type=int)
@handle_error
def export_json_cmd(output_path: str, platform: str, region: str, limit: int) -> None:
    """Fetch and export trends to a JSON file."""
    data = _fetch_for_export(platform, region, limit)
    path = export_mod.export_json(data, output_path)
    click.echo(f"Exported JSON → {path}")


@export.command("csv")
@click.option("-o", "--output", "output_path", required=True)
@click.option("--platform", default="both", type=click.Choice(["youtube", "tiktok", "both"]))
@click.option("--region", default="US", show_default=True)
@click.option("--limit", default=25, show_default=True, type=int)
@handle_error
def export_csv_cmd(output_path: str, platform: str, region: str, limit: int) -> None:
    """Fetch and export trending videos to a CSV file."""
    data = _fetch_for_export(platform, region, limit)
    videos = []
    if isinstance(data, dict):
        videos = data.get("videos", [])
    elif isinstance(data, list):
        videos = data

    if not videos and isinstance(data, dict):
        # aggregated
        yt = data.get("youtube_data", {})
        tt = data.get("tiktok_data", {})
        videos = yt.get("videos", []) + tt.get("videos", [])

    path = export_mod.export_csv(videos, output_path)
    click.echo(f"Exported CSV ({len(videos)} rows) → {path}")


@export.command("report")
@click.option("-o", "--output", "output_path", required=True)
@click.option("--region", default="US", show_default=True)
@click.option("--limit", default=20, show_default=True, type=int)
@handle_error
def export_report_cmd(output_path: str, region: str, limit: int) -> None:
    """Generate a full Markdown trend report and save to file."""
    yt_key = session_mod.get_api_key("youtube")
    tt_key = session_mod.get_api_key("tiktok")
    yt_data = None
    tt_data = None
    try:
        yt_data = yt_mod.fetch_trending(api_key=yt_key, region=region, limit=limit)
    except Exception:
        pass
    try:
        tt_data = tt_mod.fetch_trending(api_token=tt_key, limit=limit, region=region)
    except Exception:
        pass

    aggregated = trends_mod.aggregate(youtube_data=yt_data, tiktok_data=tt_data)
    report = export_mod.generate_report(aggregated)
    path = export_mod.export_json(report, output_path.replace(".json", ".md"))
    import os
    with open(output_path, "w") as f:
        f.write(report)
    click.echo(f"Report saved → {output_path}")


def _fetch_for_export(platform: str, region: str, limit: int) -> Any:
    yt_key = session_mod.get_api_key("youtube")
    tt_key = session_mod.get_api_key("tiktok")

    if platform == "youtube":
        return yt_mod.fetch_trending(api_key=yt_key, region=region, limit=limit)
    if platform == "tiktok":
        return tt_mod.fetch_trending(api_token=tt_key, limit=limit, region=region)

    # both
    yt_data, tt_data = None, None
    try:
        yt_data = yt_mod.fetch_trending(api_key=yt_key, region=region, limit=limit)
    except Exception:
        pass
    try:
        tt_data = tt_mod.fetch_trending(api_token=tt_key, limit=limit, region=region)
    except Exception:
        pass
    return trends_mod.aggregate(youtube_data=yt_data, tiktok_data=tt_data)


# ── config group ──────────────────────────────────────────────────────────────

@cli.group("config")
def config_group():
    """Manage API keys and settings."""
    pass


@config_group.command("set-key")
@click.argument("platform", type=click.Choice(["youtube", "tiktok"]))
@click.argument("key")
@handle_error
def config_set_key(platform: str, key: str) -> None:
    """Set an API key for a platform."""
    session_mod.set_api_key(platform, key)
    output({"platform": platform, "status": "saved"}, f"API key for '{platform}' saved.")


@config_group.command("show")
@handle_error
def config_show() -> None:
    """Show current configuration."""
    info = session_mod.config_info()
    output(info, "TrendScout Configuration:")


@config_group.command("set")
@click.argument("key")
@click.argument("value")
@handle_error
def config_set(key: str, value: str) -> None:
    """Set a config value (e.g. region, default_limit)."""
    session_mod.set_config_value(key, value)
    output({"key": key, "value": value}, f"Config: {key} = {value}")


@config_group.command("clear-cache")
@handle_error
def config_clear_cache() -> None:
    """Clear all cached trend data."""
    count = session_mod.clear_cache()
    output({"cleared": count}, f"Cleared {count} cache entries.")


# ── REPL ──────────────────────────────────────────────────────────────────────

@cli.command()
def repl() -> None:
    """Start an interactive TrendScout REPL session."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.trendscout.utils.repl_skin import ReplSkin
    skin = ReplSkin(version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "trends youtube [--category <cat>] [--region <r>]": "YouTube trending videos",
        "trends tiktok [--region <r>]": "TikTok trending videos",
        "trends hashtags --niche <niche>": "Trending hashtags by niche",
        "trends music": "Trending TikTok sounds",
        "trends report": "Full cross-platform report",
        "recommend hashtags --niche <niche>": "Hashtag mix recommendations",
        "export json -o <file>": "Export trends to JSON",
        "export csv -o <file>": "Export trending videos to CSV",
        "export report -o <file>": "Generate Markdown trend report",
        "config set-key youtube <key>": "Set YouTube Data API v3 key",
        "config set-key tiktok <token>": "Set TikTok Research API token",
        "config show": "Show config and key status",
        "config clear-cache": "Clear cached trend data",
        "help": "Show this help",
        "quit / exit": "Exit the REPL",
    }

    while True:
        try:
            raw = skin.get_input(pt_session)
        except (KeyboardInterrupt, EOFError):
            skin.print_goodbye()
            break

        if not raw:
            continue
        cmd = raw.strip()

        if cmd in ("quit", "exit", "q"):
            skin.print_goodbye()
            break

        if cmd in ("help", "h", "?"):
            skin.help(_repl_commands)
            continue

        try:
            args = shlex.split(cmd)
        except ValueError as e:
            skin.error(f"Parse error: {e}")
            continue

        try:
            cli.main(args=args, standalone_mode=False)
        except SystemExit:
            pass
        except click.exceptions.UsageError as e:
            skin.error(str(e))
        except click.exceptions.BadParameter as e:
            skin.error(str(e))
        except Exception as e:
            skin.error(str(e))


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    cli()


if __name__ == "__main__":
    main()
