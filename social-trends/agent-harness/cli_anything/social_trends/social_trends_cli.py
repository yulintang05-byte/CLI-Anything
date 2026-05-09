"""Social Trends CLI — Agent-native social media trend intelligence.

Scrapes YouTube & TikTok for viral trends, hashtags, and music.
Optimises all your social media accounts.
Full theme page creation and conversion playbook.

Usage:
    python3 -m cli_anything.social_trends [--json] <command>
    python3 -m cli_anything.social_trends   (launches REPL)

Commands:
    trends      Fetch viral trends from YouTube/TikTok
    hashtags    Generate and analyse hashtag sets for any niche
    music       Get trending music/audio strategy
    account     Account registration and optimisation reports
    theme-page  Theme page creation, niche scoring, and conversion guide
    schedule    Generate a content calendar
    config      View/set configuration (API keys, defaults)
"""

import json
import sys
import shlex
import click
from typing import Optional, Any

from cli_anything.social_trends.core.session import Session
from cli_anything.social_trends.core import trends as trends_mod
from cli_anything.social_trends.core import hashtags as hashtags_mod
from cli_anything.social_trends.core import music as music_mod
from cli_anything.social_trends.core import account as account_mod
from cli_anything.social_trends.core import theme_page as theme_mod

# ── Global state ──────────────────────────────────────────────────────────────

_session: Optional[Session] = None
_json_output: bool = False
_repl_mode: bool = False


def get_session() -> Session:
    global _session
    import os
    from pathlib import Path
    config_path = Path(os.environ.get("HOME", str(Path.home()))) / ".social_trends_config.json"
    if _session is None or _session.config_path != config_path:
        _session = Session(config_path=config_path)
    return _session


# ── Output helpers ────────────────────────────────────────────────────────────

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
        else:
            click.echo(str(data))


def _print_dict(d: dict, indent: int = 2) -> None:
    pad = " " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{pad}{k}:")
            _print_dict(v, indent + 2)
        elif isinstance(v, list):
            if not v:
                click.echo(f"{pad}{k}: []")
            elif all(isinstance(i, str) for i in v):
                click.echo(f"{pad}{k}: {', '.join(v)}")
            else:
                click.echo(f"{pad}{k}: [{len(v)} items]")
                for item in v[:5]:
                    if isinstance(item, dict):
                        _print_dict(item, indent + 4)
                    else:
                        click.echo(f"{pad}  - {item}")
                if len(v) > 5:
                    click.echo(f"{pad}  ... and {len(v) - 5} more")
        else:
            click.echo(f"{pad}{k}: {v}")


def _print_list(lst: list) -> None:
    if not lst:
        click.echo("  (empty)")
        return
    for i, item in enumerate(lst):
        if isinstance(item, dict):
            click.echo(f"\n  [{i+1}]")
            _print_dict(item, 4)
        else:
            click.echo(f"  {i+1}. {item}")


def _err(msg: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": msg}), err=True)
    else:
        click.echo(f"Error: {msg}", err=True)


def _ok(msg: str, data: Any = None) -> None:
    if _json_output:
        payload: dict = {"status": "ok", "message": msg}
        if data is not None:
            payload["data"] = data
        click.echo(json.dumps(payload, indent=2, default=str))
    else:
        click.echo(f"✓ {msg}")
        if data is not None:
            output(data)


# ── Root group ────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output JSON for agent consumption")
@click.option("--config-path", default="", help="Path to config file")
@click.pass_context
def cli(ctx: click.Context, use_json: bool, config_path: str) -> None:
    """Social Trends — viral trend intelligence for YouTube, TikTok, and beyond."""
    global _json_output
    _json_output = use_json
    ctx.ensure_object(dict)
    ctx.obj["session"] = get_session()

    if ctx.invoked_subcommand is None:
        if sys.stdin.isatty():
            _run_repl()
        else:
            click.echo(ctx.get_help())


def main() -> None:
    cli()


# ── trends ─────────────────────────────────────────────────────────────────

@cli.group()
def trends() -> None:
    """Fetch viral trends from YouTube and TikTok."""


@trends.command("fetch")
@click.option("--platform", "-p", default="all",
              type=click.Choice(["youtube", "tiktok", "all"], case_sensitive=False),
              help="Platform to fetch from")
@click.option("--niche", "-n", default="general", help="Content niche (fitness, food, finance, etc.)")
@click.option("--region", "-r", default="US", help="Region code (US, GB, CA, AU, etc.)")
@click.option("--max", "max_results", default=25, help="Max results to fetch")
@click.option("--save", is_flag=True, help="Save snapshot to session")
def trends_fetch(platform: str, niche: str, region: str, max_results: int, save: bool) -> None:
    """Fetch current viral trends from YouTube and/or TikTok."""
    sess = get_session()
    result = trends_mod.fetch_platform_trends(platform, niche=niche, region=region, max_results=max_results)
    if save:
        sess.save_trend_snapshot(platform, niche, result)
    output(result, f"Viral trends — {platform.upper()} / {niche} / {region}")


@trends.command("search")
@click.argument("query")
@click.option("--platform", "-p", default="youtube",
              type=click.Choice(["youtube", "tiktok"], case_sensitive=False))
@click.option("--max", "max_results", default=20)
def trends_search(query: str, platform: str, max_results: int) -> None:
    """Search trending content by keyword or topic."""
    result = trends_mod.search_trends(query, platform=platform, max_results=max_results)
    output(result, f"Trending '{query}' on {platform.upper()}")


@trends.command("compare")
@click.option("--niche", "-n", default="general", help="Niche to compare across platforms")
@click.option("--region", "-r", default="US")
def trends_compare(niche: str, region: str) -> None:
    """Compare trending hashtags across YouTube and TikTok side-by-side."""
    result = trends_mod.compare_platforms(niche=niche, region=region)
    output(result, f"Platform comparison — {niche} / {region}")


@trends.command("saved")
@click.option("--platform", "-p", default="all")
@click.option("--niche", "-n", default="general")
def trends_saved(platform: str, niche: str) -> None:
    """Show the latest saved trend snapshot."""
    sess = get_session()
    snapshot = sess.get_latest_snapshot(platform, niche)
    if snapshot:
        output(snapshot, f"Saved snapshot — {platform} / {niche}")
    else:
        _err(f"No saved snapshot for {platform}/{niche}. Run 'trends fetch --save' first.")


# ── hashtags ──────────────────────────────────────────────────────────────────

@cli.group()
def hashtags() -> None:
    """Generate and analyse hashtag sets for any niche and platform."""


@hashtags.command("generate")
@click.option("--niche", "-n", default="general", help="Content niche")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "instagram", "youtube", "reels"], case_sensitive=False))
@click.option("--count", "-c", default=None, type=int, help="Number of hashtags (default: platform optimal)")
@click.option("--tags", "-t", default="", help="Additional custom tags (comma-separated, no spaces)")
def hashtags_generate(niche: str, platform: str, count: int | None, tags: str) -> None:
    """Generate an optimised hashtag set ready to copy-paste."""
    custom = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
    result = hashtags_mod.generate_hashtag_set(niche, platform=platform, count=count, custom_tags=custom)
    if not _json_output:
        click.echo(f"\n  Hashtag set ({result['count']} tags for {platform}/{niche}):")
        click.echo(f"\n  {result['caption_ready']}\n")
    output(result)


@hashtags.command("analyse")
@click.argument("hashtag")
def hashtags_analyse(hashtag: str) -> None:
    """Analyse a single hashtag — tier, competition, placement advice."""
    result = hashtags_mod.analyse_hashtag(hashtag)
    output(result, f"Analysis: {hashtag}")


@hashtags.command("sets")
@click.option("--niche", "-n", default="general")
@click.option("--platform", "-p", default="instagram",
              type=click.Choice(["tiktok", "instagram", "youtube", "reels"], case_sensitive=False))
@click.option("--num-sets", default=3, help="Number of rotation sets to generate")
def hashtags_sets(niche: str, platform: str, num_sets: int) -> None:
    """Generate multiple rotating hashtag sets to avoid shadowban."""
    result = hashtags_mod.generate_multiple_sets(niche, platform=platform, num_sets=num_sets)
    if not _json_output:
        for s in result:
            click.echo(f"\n  {s['label']}:")
            click.echo(f"  {s['caption_ready']}")
    output(result)


@hashtags.command("calendar")
@click.option("--niche", "-n", default="general")
@click.option("--platform", "-p", default="instagram",
              type=click.Choice(["tiktok", "instagram", "youtube", "reels"], case_sensitive=False))
@click.option("--days", "-d", default=7, help="Number of days to plan")
def hashtags_calendar(niche: str, platform: str, days: int) -> None:
    """Generate a weekly hashtag rotation calendar."""
    result = hashtags_mod.hashtag_calendar(niche, platform=platform, days=days)
    output(result, f"{days}-day hashtag calendar — {niche}/{platform}")


# ── music ─────────────────────────────────────────────────────────────────────

@cli.group()
def music() -> None:
    """Trending music and audio strategy for all platforms."""


@music.command("trending")
@click.option("--niche", "-n", default="general", help="Content niche")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "youtube"], case_sensitive=False))
def music_trending(niche: str, platform: str) -> None:
    """Get trending audio/music recommendations for your niche."""
    result = music_mod.get_trending_sounds(niche=niche, platform=platform)
    output(result, f"Trending audio — {platform}/{niche}")


@music.command("strategy")
@click.argument("content_type")
def music_strategy(content_type: str) -> None:
    """Get audio strategy for a content type (tutorial, vlog, fitness, etc.)."""
    result = music_mod.get_audio_strategy(content_type)
    output(result, f"Audio strategy: {content_type}")


@music.command("sources")
def music_sources() -> None:
    """List all royalty-free music sources trusted by creators."""
    result = music_mod.list_royalty_free_sources()
    output(result, "Royalty-free music sources")


@music.command("archetypes")
@click.option("--niche", "-n", default="general")
def music_archetypes(niche: str) -> None:
    """Show trending audio archetypes ranked for your niche."""
    result = music_mod.analyse_trending_archetypes(niche=niche)
    output(result, f"Audio archetypes — {niche}")


# ── account ───────────────────────────────────────────────────────────────────

@cli.group()
def account() -> None:
    """Register and optimise your social media accounts."""


@account.command("add")
@click.argument("platform")
@click.argument("handle")
@click.option("--niche", "-n", default="general", help="Content niche")
def account_add(platform: str, handle: str, niche: str) -> None:
    """Register a social media account for tracking and optimisation."""
    sess = get_session()
    result = sess.add_account(platform, handle, niche=niche)
    _ok(f"Account @{handle} ({platform}) added", result)


@account.command("remove")
@click.argument("platform")
@click.argument("handle")
def account_remove(platform: str, handle: str) -> None:
    """Remove a registered account."""
    sess = get_session()
    if sess.remove_account(platform, handle):
        _ok(f"Account @{handle} ({platform}) removed")
    else:
        _err(f"Account @{handle} ({platform}) not found")


@account.command("list")
def account_list() -> None:
    """List all registered accounts."""
    sess = get_session()
    accounts = sess.list_accounts()
    if not accounts:
        click.echo("No accounts registered. Use 'account add <platform> <handle>'")
        return
    output(accounts, f"Registered accounts ({len(accounts)})")


@account.command("optimise")
@click.argument("platform")
@click.option("--niche", "-n", default="general")
@click.option("--handle", "-h", default="")
@click.option("--followers", "-f", default=0, help="Current follower count")
def account_optimise(platform: str, niche: str, handle: str, followers: int) -> None:
    """Generate a full account optimisation report."""
    # Try to pull niche from registered account if available
    sess = get_session()
    if handle:
        registered = sess.get_account(platform, handle)
        if registered and niche == "general":
            niche = registered.get("niche", "general")

    result = account_mod.generate_optimisation_report(
        platform, niche, handle=handle, followers=followers
    )
    output(result, f"Optimisation report — @{handle} ({platform}/{niche})")


@account.command("optimise-all")
def account_optimise_all() -> None:
    """Generate optimisation reports for all registered accounts."""
    sess = get_session()
    accounts = sess.list_accounts()
    if not accounts:
        click.echo("No accounts registered. Use 'account add <platform> <handle>'")
        return
    results = []
    for acc in accounts:
        report = account_mod.generate_optimisation_report(
            acc["platform"], acc["niche"],
            handle=acc["handle"], followers=0
        )
        results.append({"account": acc, "report": report})
    output(results, f"Optimisation reports for {len(results)} accounts")


@account.command("diagnose")
@click.argument("symptoms", nargs=-1, required=True)
def account_diagnose(symptoms: tuple[str, ...]) -> None:
    """Diagnose growth problems from symptom descriptions.

    Examples:
        account diagnose "high views but low followers"
        account diagnose "stuck at plateau" "low engagement"
    """
    result = account_mod.diagnose_growth_issues(list(symptoms))
    output(result, "Growth diagnosis")


@account.command("benchmarks")
@click.argument("platform")
def account_benchmarks(platform: str) -> None:
    """Show engagement rate benchmarks for a platform."""
    result = account_mod.get_engagement_benchmarks(platform)
    output(result, f"Engagement benchmarks — {platform}")


@account.command("engagement-rate")
@click.option("--likes", default=0, type=int)
@click.option("--comments", default=0, type=int)
@click.option("--shares", default=0, type=int)
@click.option("--views", default=0, type=int)
@click.option("--followers", default=0, type=int)
def account_engagement_rate(likes: int, comments: int, shares: int, views: int, followers: int) -> None:
    """Calculate engagement rate for a post."""
    result = account_mod.calculate_engagement_rate(likes, comments, shares, views, followers)
    output(result, "Engagement rate calculation")


# ── theme-page ────────────────────────────────────────────────────────────────

@cli.group("theme-page")
def theme_page() -> None:
    """Theme page creation, niche scoring, and personal brand conversion."""


@theme_page.command("niches")
@click.option("--min-growth", default=7, help="Minimum growth speed score (1–10)")
@click.option("--min-monetisation", default=7, help="Minimum monetisation score (1–10)")
def theme_niches(min_growth: int, min_monetisation: int) -> None:
    """List recommended niches scored by growth, monetisation, and longevity."""
    result = theme_mod.get_niche_recommendations(
        min_growth=min_growth, min_monetisation=min_monetisation
    )
    if not _json_output:
        click.echo(f"\n  Top niches (growth≥{min_growth}, monetisation≥{min_monetisation}):\n")
        for i, n in enumerate(result):
            click.echo(f"  {i+1}. {n['niche']}")
            click.echo(f"     Growth: {n['growth_speed']}/10 | Monetisation: {n['monetisation']}/10 | Competition: {n['competition']}/10")
            click.echo(f"     Platforms: {', '.join(n['recommended_platforms'])}")
            click.echo()
    output(result)


@theme_page.command("score")
@click.argument("niche")
def theme_score(niche: str) -> None:
    """Get a detailed score and verdict for a specific niche."""
    result = theme_mod.score_niche(niche)
    output(result, f"Niche score: {niche}")


@theme_page.command("niche")
@click.argument("niche")
def theme_niche_details(niche: str) -> None:
    """Get full details, sub-niches, and monetisation methods for a niche."""
    result = theme_mod.get_niche_details(niche)
    if result is None:
        _err(f"Niche '{niche}' not found. Run 'theme-page niches' to see available options.")
        return
    output(result, f"Niche details: {niche}")


@theme_page.command("playbook")
def theme_playbook() -> None:
    """Show the complete step-by-step theme page launch playbook."""
    result = theme_mod.get_launch_playbook()
    if not _json_output:
        click.echo("\n  Theme Page Launch Playbook\n")
        for phase in result:
            click.echo(f"  {phase['phase']}")
            for action in phase["actions"]:
                click.echo(f"    → {action}")
            click.echo(f"  Deliverable: {phase['deliverable']}\n")
    output(result)


@theme_page.command("convert")
def theme_convert() -> None:
    """Show the strategy for converting a theme page to a personal brand."""
    result = theme_mod.get_conversion_strategy()
    if not _json_output:
        click.echo("\n  Theme Page → Personal Brand Conversion Strategy\n")
        for step in result:
            click.echo(f"  {step['step']}")
            click.echo(f"    How:  {step['how']}")
            click.echo(f"    When: {step['when']}")
            click.echo(f"    Why:  {step['why']}\n")
    output(result)


@theme_page.command("ethics")
def theme_ethics() -> None:
    """Show ethical and legal guidelines for theme page operators."""
    result = theme_mod.get_ethical_guidelines()
    if not _json_output:
        click.echo("\n  Ethical Guidelines for Theme Pages\n")
        for i, g in enumerate(result, 1):
            click.echo(f"  {i}. {g}")
    output(result)


@theme_page.command("content-plan")
@click.argument("niche")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "instagram", "youtube"], case_sensitive=False))
@click.option("--days", "-d", default=7)
def theme_content_plan(niche: str, platform: str, days: int) -> None:
    """Generate a daily content plan for a theme page."""
    result = theme_mod.generate_content_plan(niche, platform=platform, days=days)
    output(result, f"{days}-day content plan — {niche}/{platform}")


# ── schedule ──────────────────────────────────────────────────────────────────

@cli.group()
def schedule() -> None:
    """Generate posting schedules and content calendars."""


@schedule.command("generate")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "instagram", "youtube", "reels"], case_sensitive=False))
@click.option("--niche", "-n", default="general")
@click.option("--days", "-d", default=7)
def schedule_generate(platform: str, niche: str, days: int) -> None:
    """Generate a complete posting schedule with hashtag sets."""
    from datetime import date, timedelta

    hash_sets = hashtags_mod.generate_multiple_sets(niche, platform=platform, num_sets=3)
    pillars = account_mod._CONTENT_PILLARS.get(niche.lower(), account_mod._CONTENT_PILLARS["general"])
    sched = account_mod._optimal_schedule(platform, niche.lower())

    calendar = []
    for day in range(days):
        post_date = date.today() + timedelta(days=day)
        hash_set = hash_sets[day % len(hash_sets)]
        pillar = pillars[day % len(pillars)]

        daily = {
            "date": post_date.isoformat(),
            "day": post_date.strftime("%A"),
            "best_times": sched["best_times"],
            "content_pillar": pillar["pillar"],
            "content_ideas": pillar["examples"],
            "hashtags": hash_set["hashtags"],
            "frequency": sched["frequency"],
        }
        calendar.append(daily)

    output(calendar, f"{days}-day posting schedule — {platform}/{niche}")


# ── config ─────────────────────────────────────────────────────────────────────

@cli.group()
def config() -> None:
    """View and set configuration (API keys, default niche, region, etc.)."""


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str) -> None:
    """Set a configuration value.

    Keys: default_niche, default_region, default_platform
    API keys are read from environment variables, not stored here.
    """
    sess = get_session()
    sess.set_config(key, value)
    _ok(f"Config set: {key} = {value}")


@config.command("get")
@click.argument("key")
def config_get(key: str) -> None:
    """Get a configuration value."""
    sess = get_session()
    value = sess.get_config(key)
    if value is None:
        _err(f"Config key '{key}' not set")
    else:
        _ok(f"{key} = {value}")


@config.command("show")
def config_show() -> None:
    """Show all configuration and API key status."""
    import os
    sess = get_session()
    cfg = sess.get_all_config()
    api_status = {
        "YOUTUBE_API_KEY": "✓ Set" if os.environ.get("YOUTUBE_API_KEY") else "✗ Not set (fallback mode)",
        "TIKTOK_CLIENT_KEY": "✓ Set" if os.environ.get("TIKTOK_CLIENT_KEY") else "✗ Not set (fallback mode)",
        "TIKTOK_CLIENT_SECRET": "✓ Set" if os.environ.get("TIKTOK_CLIENT_SECRET") else "✗ Not set (fallback mode)",
    }
    result = {
        "configuration": cfg,
        "api_keys": api_status,
        "setup_guide": {
            "youtube": "Get free key at console.cloud.google.com → Enable YouTube Data API v3",
            "tiktok": "Apply at developers.tiktok.com/products/research-api",
            "ytdlp": "pip install yt-dlp (used for TikTok video metadata without API key)",
        },
    }
    output(result, "Social Trends Configuration")


# ── REPL ───────────────────────────────────────────────────────────────────────

def _run_repl() -> None:
    global _repl_mode
    _repl_mode = True
    click.echo("Social Trends REPL — type 'help' for commands, 'exit' to quit")
    click.echo("Set YOUTUBE_API_KEY and TIKTOK_CLIENT_KEY for live data.\n")

    while True:
        try:
            line = click.prompt("social-trends", prompt_suffix="> ", default="", show_default=False)
        except (EOFError, KeyboardInterrupt):
            click.echo("\nBye!")
            break

        line = line.strip()
        if not line:
            continue
        if line.lower() in ("exit", "quit", "q"):
            click.echo("Bye!")
            break
        if line.lower() in ("help", "?"):
            _repl_help()
            continue

        parts = shlex.split(line)
        try:
            standalone = cli.make_context("social-trends", parts, standalone_mode=False)
            cli.invoke(standalone)
        except click.UsageError as e:
            click.echo(f"  Usage error: {e}")
        except SystemExit:
            pass
        except Exception as e:
            click.echo(f"  Error: {e}")


def _repl_help() -> None:
    click.echo("""
  Commands:
    trends fetch [-p youtube|tiktok|all] [-n NICHE] [-r REGION]
    trends search QUERY [-p youtube|tiktok]
    trends compare [-n NICHE]

    hashtags generate [-n NICHE] [-p PLATFORM] [-c COUNT]
    hashtags sets [-n NICHE] [-p PLATFORM]
    hashtags calendar [-n NICHE] [-d DAYS]
    hashtags analyse HASHTAG

    music trending [-n NICHE] [-p PLATFORM]
    music strategy CONTENT_TYPE
    music sources

    account add PLATFORM HANDLE [-n NICHE]
    account list
    account optimise PLATFORM [-n NICHE] [-h HANDLE] [-f FOLLOWERS]
    account optimise-all
    account diagnose "SYMPTOM"
    account benchmarks PLATFORM
    account engagement-rate --likes N --comments N --views N --followers N

    theme-page niches [--min-growth N] [--min-monetisation N]
    theme-page score NICHE
    theme-page playbook
    theme-page convert
    theme-page ethics
    theme-page content-plan NICHE [-p PLATFORM] [-d DAYS]

    schedule generate [-p PLATFORM] [-n NICHE] [-d DAYS]

    config show
    config set KEY VALUE

  Global flags (prepend to any command):
    --json          Machine-readable JSON output

  Examples:
    trends fetch --platform tiktok --niche fitness
    hashtags generate --niche finance --platform instagram
    theme-page score "Luxury & Wealth Lifestyle"
    account optimise tiktok --niche fitness --followers 5000
    schedule generate --platform instagram --niche food --days 14
""")
