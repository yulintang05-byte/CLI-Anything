#!/usr/bin/env python3
"""Social Media CLI — Viral trend scraper, hashtag optimizer, and account growth tool.

Scrapes YouTube and TikTok for viral trends, hashtags, and music.
Optimizes social media accounts and guides theme page conversion.

Usage:
    # One-shot commands
    python3 -m cli_anything.social_media trends fetch --platforms tiktok youtube
    python3 -m cli_anything.social_media trends analyze
    python3 -m cli_anything.social_media hashtags generate --niche finance --platform tiktok
    python3 -m cli_anything.social_media music trending --platform tiktok
    python3 -m cli_anything.social_media account add myhandle tiktok finance --followers 5000
    python3 -m cli_anything.social_media account optimize myhandle
    python3 -m cli_anything.social_media theme-page guide

    # Interactive REPL
    python3 -m cli_anything.social_media repl
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_media.core.session import Session
from cli_anything.social_media.core import trends as trends_mod
from cli_anything.social_media.core import hashtags as hashtags_mod
from cli_anything.social_media.core import music as music_mod
from cli_anything.social_media.core import accounts as accounts_mod
from cli_anything.social_media.core import theme_pages as theme_mod

_session: Optional[Session] = None
_json_output = False
_repl_mode = False


def get_session() -> Session:
    global _session
    if _session is None:
        _session = Session()
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
        except (ValueError, RuntimeError, FileNotFoundError) as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
        except Exception as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# -- Main CLI Group -----------------------------------------------------------
@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.option("--project", "project_path", type=str, default=None,
              help="Path to .social-media.json project file")
@click.pass_context
def cli(ctx, use_json, project_path):
    """Social Media CLI — Viral trends, hashtags, music, and account growth.

    Run without a subcommand to enter interactive REPL mode.
    """
    global _json_output
    _json_output = use_json

    if project_path:
        sess = get_session()
        if not sess.has_project():
            proj = trends_mod.open_project(project_path)
            sess.set_project(proj, project_path)

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl, project_path=None)


# -- Project Commands ---------------------------------------------------------
@cli.group()
def project():
    """Project management commands."""
    pass


@project.command("new")
@click.option("--name", "-n", default="My Social Media", help="Project name")
@click.option("--output", "-o", type=str, default=None, help="Save path")
@handle_error
def project_new(name, output):
    """Create a new social media project."""
    proj = trends_mod.create_project(name=name)
    sess = get_session()
    sess.set_project(proj, output)
    if output:
        trends_mod.save_project(proj, output)
    info = trends_mod.get_project_info(proj)
    globals()["output"](info, f"Created project: {name}")


@project.command("open")
@click.argument("path")
@handle_error
def project_open(path):
    """Open an existing project."""
    proj = trends_mod.open_project(path)
    sess = get_session()
    sess.set_project(proj, path)
    info = trends_mod.get_project_info(proj)
    globals()["output"](info, f"Opened: {path}")


@project.command("save")
@click.argument("path", required=False)
@handle_error
def project_save(path):
    """Save the current project."""
    sess = get_session()
    saved = sess.save_session(path)
    output({"saved": saved}, f"Saved to: {saved}")


@project.command("info")
@handle_error
def project_info():
    """Show project information."""
    sess = get_session()
    info = trends_mod.get_project_info(sess.get_project())
    output(info)


@project.command("json")
@handle_error
def project_json():
    """Print raw project JSON."""
    sess = get_session()
    click.echo(json.dumps(sess.get_project(), indent=2, default=str))


# -- Trends Commands ----------------------------------------------------------
@cli.group()
def trends():
    """Viral trend fetching and analysis."""
    pass


@trends.command("fetch")
@click.option("--platforms", "-p", default="tiktok,youtube",
              help="Platforms to fetch (tiktok,youtube,all)")
@click.option("--country", "-c", default="US", help="Country/region code (e.g. US, GB, AU)")
@click.option("--limit", "-l", type=int, default=20, help="Number of trends to fetch")
@handle_error
def trends_fetch(platforms, country, limit):
    """Fetch viral trends from YouTube and/or TikTok."""
    sess = get_session()
    if not sess.has_project():
        sess.set_project(trends_mod.create_project())

    platform_list = [p.strip().lower() for p in platforms.split(",")]
    sess.snapshot("Fetch trends")
    result = trends_mod.fetch_trends(
        sess.get_project(), platforms=platform_list, country=country, limit=limit
    )
    output(result, f"Fetched trends from: {', '.join(result.get('platforms', platform_list))}")


@trends.command("analyze")
@handle_error
def trends_analyze():
    """Analyze the latest trend data for cross-platform insights."""
    sess = get_session()
    analysis = trends_mod.analyze_trends(sess.get_project())
    output(analysis, "Trend Analysis:")


@trends.command("latest")
@handle_error
def trends_latest():
    """Show the most recent trend snapshot."""
    sess = get_session()
    data = trends_mod.get_latest_trends(sess.get_project())
    output(data, "Latest Trends:")


@trends.command("history")
@handle_error
def trends_history():
    """List all trend snapshot history."""
    sess = get_session()
    history = trends_mod.list_trend_history(sess.get_project())
    output(history, "Trend History:")


# -- Hashtags Commands --------------------------------------------------------
@cli.group()
def hashtags():
    """Hashtag generation, scoring, and optimization."""
    pass


@hashtags.command("generate")
@click.option("--niche", "-n", required=True, help="Content niche (finance, fitness, lifestyle, fashion, food, beauty, motivation, travel)")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "instagram", "youtube_shorts", "youtube"]),
              help="Target platform")
@click.option("--strategy", "-s", default="balanced",
              type=click.Choice(["balanced", "aggressive", "niche", "stealth"]),
              help="Hashtag strategy")
@click.option("--custom", "-c", multiple=True, help="Custom tags to include (use multiple times)")
@click.option("--save-as", type=str, default=None, help="Save this set to the project with a name")
@handle_error
def hashtags_generate(niche, platform, strategy, custom, save_as):
    """Generate an optimized hashtag set for your niche and platform."""
    result = hashtags_mod.generate_hashtag_set(
        niche=niche, platform=platform, strategy=strategy,
        custom_tags=list(custom) if custom else None,
    )
    if save_as:
        sess = get_session()
        if sess.has_project():
            hashtags_mod.save_hashtag_set(
                sess.get_project(), save_as, result["hashtags"], niche, platform
            )
            click.echo(f"Saved hashtag set as: {save_as}")
    output(result, f"Generated hashtags for {niche} on {platform} ({strategy}):")


@hashtags.command("score")
@click.argument("tags", nargs=-1)
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "instagram", "youtube_shorts", "youtube"]))
@handle_error
def hashtags_score(tags, platform):
    """Score an existing set of hashtags for quality and reach potential."""
    if not tags:
        raise ValueError("Provide at least one hashtag to score.")
    result = hashtags_mod.score_hashtags(list(tags), platform=platform)
    output(result, f"Hashtag Score ({platform}):")


@hashtags.command("list")
@handle_error
def hashtags_list():
    """List saved hashtag sets in the project."""
    sess = get_session()
    sets = hashtags_mod.list_hashtag_sets(sess.get_project())
    output(sets, "Saved Hashtag Sets:")


@hashtags.command("niches")
@handle_error
def hashtags_niches():
    """List all available niches."""
    niches = hashtags_mod.list_niches()
    output(niches, "Available Niches:")


# -- Music Commands -----------------------------------------------------------
@cli.group()
def music():
    """Trending music and sound recommendations."""
    pass


@music.command("trending")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "all"]))
@click.option("--region", "-r", default="US", help="Region code (US, GB, AU, etc.)")
@click.option("--limit", "-l", type=int, default=20)
@handle_error
def music_trending(platform, region, limit):
    """Fetch currently trending music and sounds."""
    result = music_mod.fetch_trending_music(platform=platform, region=region, limit=limit)
    output(result, f"Trending Music on {platform} ({region}):")


@music.command("recommend")
@click.argument("niche")
@click.option("--type", "content_type", default="general", help="Content type (tutorial, vlog, review, etc.)")
@handle_error
def music_recommend(niche, content_type):
    """Get music recommendations for your niche."""
    result = music_mod.recommend_sounds(niche=niche, content_type=content_type)
    output(result, f"Music Recommendations for {niche}:")


@music.command("categories")
@handle_error
def music_categories():
    """List all sound categories."""
    categories = music_mod.list_sound_categories()
    output(categories, "Sound Categories:")


# -- Account Commands ---------------------------------------------------------
@cli.group()
def account():
    """Social media account management and optimization."""
    pass


@account.command("add")
@click.argument("username")
@click.argument("platform", type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]))
@click.argument("niche")
@click.option("--followers", "-f", type=int, default=0)
@click.option("--bio", "-b", type=str, default="")
@handle_error
def account_add(username, platform, niche, followers, bio):
    """Add a social media account to track."""
    sess = get_session()
    if not sess.has_project():
        sess.set_project(trends_mod.create_project())
    sess.snapshot(f"Add account {username}")
    result = accounts_mod.add_account(
        sess.get_project(), username=username, platform=platform,
        niche=niche, followers=followers, bio=bio,
    )
    output(result, f"Added account: @{username} ({platform})")


@account.command("remove")
@click.argument("account_id")
@handle_error
def account_remove(account_id):
    """Remove an account from the project."""
    sess = get_session()
    sess.snapshot(f"Remove account {account_id}")
    removed = accounts_mod.remove_account(sess.get_project(), account_id)
    output(removed, f"Removed: @{removed.get('username', account_id)}")


@account.command("list")
@handle_error
def account_list():
    """List all tracked accounts."""
    sess = get_session()
    accounts = accounts_mod.list_accounts(sess.get_project())
    output(accounts, "Tracked Accounts:")


@account.command("optimize")
@click.argument("account_id")
@handle_error
def account_optimize(account_id):
    """Get a full optimization report for an account."""
    sess = get_session()
    sess.snapshot(f"Optimize {account_id}")
    result = accounts_mod.optimize_account(sess.get_project(), account_id)
    output(result, f"Optimization Report: @{account_id}")


@account.command("score")
@click.argument("account_id")
@handle_error
def account_score(account_id):
    """Quick account health score."""
    sess = get_session()
    result = accounts_mod.score_account(sess.get_project(), account_id)
    output(result, f"Account Score: @{account_id}")


@account.command("update")
@click.argument("account_id")
@click.option("--followers", "-f", type=int, default=None)
@click.option("--bio", "-b", type=str, default=None)
@click.option("--niche", "-n", type=str, default=None)
@handle_error
def account_update(account_id, followers, bio, niche):
    """Update account information."""
    sess = get_session()
    kwargs = {}
    if followers is not None:
        kwargs["followers"] = followers
    if bio is not None:
        kwargs["bio"] = bio
    if niche is not None:
        kwargs["niche"] = niche
    sess.snapshot(f"Update account {account_id}")
    result = accounts_mod.update_account(sess.get_project(), account_id, **kwargs)
    output(result, f"Updated: @{account_id}")


@account.command("schedule")
@click.argument("account_id")
@click.option("--mon", type=str, default=None, help="Monday post time(s)")
@click.option("--tue", type=str, default=None)
@click.option("--wed", type=str, default=None)
@click.option("--thu", type=str, default=None)
@click.option("--fri", type=str, default=None)
@click.option("--sat", type=str, default=None)
@click.option("--sun", type=str, default=None)
@handle_error
def account_schedule(account_id, mon, tue, wed, thu, fri, sat, sun):
    """Set posting schedule for an account."""
    sess = get_session()
    schedule = {}
    for day, val in [("Monday", mon), ("Tuesday", tue), ("Wednesday", wed),
                     ("Thursday", thu), ("Friday", fri), ("Saturday", sat), ("Sunday", sun)]:
        if val:
            schedule[day] = val
    sess.snapshot(f"Set schedule for {account_id}")
    result = accounts_mod.set_posting_schedule(sess.get_project(), account_id, schedule)
    output(result, f"Schedule set for @{account_id}")


# -- Theme Page Commands -------------------------------------------------------
@cli.group("theme-page")
def theme_page():
    """Theme page creation and follower conversion playbook."""
    pass


@theme_page.command("guide")
@click.option("--niche", "-n", default="general", help="Your content niche")
@handle_error
def theme_guide(niche):
    """Get the complete theme page to paying customer conversion guide."""
    result = theme_mod.get_conversion_guide(niche=niche)
    output(result, f"Theme Page Conversion Guide ({niche}):")


@theme_page.command("niches")
@handle_error
def theme_niches():
    """List proven theme page niches with monetization data."""
    niches = theme_mod.list_niches()
    output(niches, "Proven Theme Page Niches:")


@theme_page.command("niche")
@click.argument("niche")
@handle_error
def theme_niche(niche):
    """Get detailed setup guide for a specific niche."""
    result = theme_mod.get_niche_guide(niche=niche)
    output(result, f"Niche Guide: {niche}")


@theme_page.command("funnel")
@click.argument("stage", type=int)
@handle_error
def theme_funnel(stage):
    """Show details for a specific conversion funnel stage (1-5)."""
    result = theme_mod.get_funnel_stage(stage)
    output(result, f"Funnel Stage {stage}: {result.get('name', '')}")


@theme_page.command("dm-scripts")
@handle_error
def theme_dm_scripts():
    """Get DM automation scripts for follower conversion."""
    result = theme_mod.get_dm_scripts()
    output(result, "DM Automation Scripts:")


# -- Session Commands ---------------------------------------------------------
@cli.group("session")
def session_group():
    """Session management commands."""
    pass


@session_group.command("status")
@handle_error
def session_status():
    """Show session status."""
    sess = get_session()
    output(sess.status())


@session_group.command("undo")
@handle_error
def session_undo():
    """Undo the last operation."""
    sess = get_session()
    desc = sess.undo()
    output({"undone": desc}, f"Undone: {desc}")


@session_group.command("redo")
@handle_error
def session_redo():
    """Redo the last undone operation."""
    sess = get_session()
    desc = sess.redo()
    output({"redone": desc}, f"Redone: {desc}")


@session_group.command("history")
@handle_error
def session_history():
    """Show operation history."""
    sess = get_session()
    history = sess.list_history()
    output(history, "History:")


# -- REPL ---------------------------------------------------------------------
@cli.command()
@click.option("--project", "project_path", type=str, default=None)
@handle_error
def repl(project_path):
    """Start interactive REPL session."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.social_media.utils.repl_skin import ReplSkin
    skin = ReplSkin("social-media", version="1.0.0")

    if project_path:
        sess = get_session()
        proj = trends_mod.open_project(project_path)
        sess.set_project(proj, project_path)

    skin.print_banner()
    pt_session = skin.create_prompt_session()

    while True:
        try:
            sess = get_session()
            proj_name = ""
            modified = False
            if sess.has_project():
                proj = sess.get_project()
                proj_name = proj.get("name", "")
                modified = sess.is_modified()

            line = skin.get_input(pt_session, account_name=proj_name, modified=modified)
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                skin.print_goodbye()
                break
            if line.lower() == "help":
                _repl_help(skin)
                continue

            args = line.split()
            try:
                cli.main(args, standalone_mode=False)
            except SystemExit:
                pass
            except click.exceptions.UsageError as e:
                skin.error(f"Usage error: {e}")
            except Exception as e:
                skin.error(f"{e}")

        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

    _repl_mode = False


def _repl_help(skin=None):
    commands = {
        "project new|open|save|info|json": "Project management",
        "trends fetch|analyze|latest|history": "Fetch and analyze viral trends",
        "hashtags generate|score|list|niches": "Hashtag optimization",
        "music trending|recommend|categories": "Trending sounds and music",
        "account add|remove|list|optimize|score|update|schedule": "Account management",
        "theme-page guide|niches|niche|funnel|dm-scripts": "Theme page conversion guide",
        "session status|undo|redo|history": "Session management",
        "help": "Show this help",
        "quit": "Exit REPL",
    }
    if skin is not None:
        skin.help(commands)
    else:
        click.echo("\nCommands:")
        for cmd, desc in commands.items():
            click.echo(f"  {cmd:<55} {desc}")
        click.echo()


def main():
    cli()


if __name__ == "__main__":
    main()
