"""Viral Trends CLI - Agent-native trend analysis and content scheduling.

Scrapes YouTube and TikTok for viral trends, hashtags, and music.
Optimizes posting strategy and generates 7-day content calendars.

Usage:
    python3 -m cli_anything.viral_trends [--json] [--workspace PATH] <command>
    python3 -m cli_anything.viral_trends  (launches REPL)
"""

import json
import sys
import shlex
import click
from typing import Optional, Any

from cli_anything.viral_trends.core.session import Session
from cli_anything.viral_trends.core import workspace as ws_mod
from cli_anything.viral_trends.core import trends as trends_mod
from cli_anything.viral_trends.core import optimizer as opt_mod
from cli_anything.viral_trends.core import scheduler as sched_mod
from cli_anything.viral_trends.core import theme_pages as guide_mod

# ── Global state ──────────────────────────────────────────────────────────────

_session: Optional[Session] = None
_json_output: bool = False
_repl_mode: bool = False


def get_session() -> Session:
    global _session
    if _session is None:
        _session = Session()
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


def _print_dict(d: dict, indent: int = 2) -> None:
    pad = " " * indent
    for k, v in d.items():
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
            parts = []
            for k, v in item.items():
                if not isinstance(v, (dict, list)):
                    parts.append(f"{k}={v}")
            click.echo("  " + "  ".join(parts))
        else:
            click.echo(f"  {item}")


def _err(msg: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": msg}), err=True)
    else:
        click.echo(f"Error: {msg}", err=True)


# ── Error handling decorator ──────────────────────────────────────────────────

def handle_error(func):
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (FileNotFoundError, ValueError, IndexError, RuntimeError, KeyError) as e:
            _err(str(e))
            if not _repl_mode:
                sys.exit(1)
        except Exception as e:
            _err(f"Unexpected error: {e}")
            if not _repl_mode:
                sys.exit(1)

    return wrapper


# ── Root CLI group ────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output results as JSON")
@click.option(
    "--workspace", "workspace_path", default=None,
    help="Path to workspace file to load on startup"
)
@click.version_option("1.0.0", prog_name="viral-trends")
@click.pass_context
def cli(ctx: click.Context, use_json: bool, workspace_path: Optional[str]) -> None:
    """Viral Trends — agent-native trend analysis and content scheduling.

    Scrapes YouTube and TikTok for viral trends, hashtags, and sounds.
    Optimizes your posting strategy and generates 7-day content calendars.

    \b
    Quick start:
      viral-trends workspace new --name my_page --niche gaming -o page.json
      viral-trends --workspace page.json trends fetch --platform youtube
      viral-trends --workspace page.json optimize profile --niche gaming
      viral-trends --workspace page.json schedule generate --niche gaming --platforms tiktok
      viral-trends guide theme-page
    """
    global _json_output
    _json_output = use_json

    if workspace_path:
        sess = get_session()
        if not sess.has_project():
            try:
                ws_mod.open_workspace(sess, workspace_path)
            except Exception as e:
                _err(str(e))
                if not _repl_mode:
                    sys.exit(1)

    ctx.ensure_object(dict)

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl, workspace_path=workspace_path)


# ── workspace group ───────────────────────────────────────────────────────────

@cli.group()
def workspace():
    """Workspace lifecycle commands (new, open, save, info, niches)."""
    pass


@workspace.command("new")
@click.option("--name", default="untitled", show_default=True, help="Workspace name")
@click.option("--niche", default="entertainment", show_default=True,
              help="Content niche (run 'workspace niches' to list options)")
@click.option("-o", "--output", "output_path", default=None, help="Save path (.json)")
@handle_error
def workspace_new(name: str, niche: str, output_path: Optional[str]) -> None:
    """Create a new workspace."""
    sess = get_session()
    result = ws_mod.new_workspace(sess, name=name, niche=niche)
    if output_path:
        ws_mod.save_workspace(sess, output_path)
        result["saved_to"] = output_path
    output(result, f"Created workspace '{name}' for niche '{niche}'")


@workspace.command("open")
@click.argument("path")
@handle_error
def workspace_open(path: str) -> None:
    """Open a workspace file."""
    sess = get_session()
    result = ws_mod.open_workspace(sess, path)
    output(result, f"Opened workspace '{result['name']}' from {path}")


@workspace.command("save")
@click.argument("path", required=False, default=None)
@handle_error
def workspace_save(path: Optional[str]) -> None:
    """Save the current workspace. Uses loaded path if no PATH given."""
    sess = get_session()
    result = ws_mod.save_workspace(sess, path)
    output(result, f"Saved workspace to {result['path']}")


@workspace.command("info")
@handle_error
def workspace_info() -> None:
    """Show information about the current workspace."""
    sess = get_session()
    result = ws_mod.workspace_info(sess)
    output(result, f"Workspace: {result['name']}")


@workspace.command("niches")
@handle_error
def workspace_niches() -> None:
    """List available content niches."""
    result = ws_mod.list_niches()
    if not _json_output:
        from cli_anything.viral_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["Niche", "Description", "Peak Hour", "Hashtag Seeds"],
            [[n["name"], n["description"], f"{n['peak_hour']}:00", ", ".join(n["hashtag_seed"])]
             for n in result]
        )
    else:
        output(result)


# ── trends group ──────────────────────────────────────────────────────────────

@cli.group()
def trends():
    """Trend scraping commands (fetch, list, show, remove)."""
    pass


@trends.command("fetch")
@click.option("--platform", default="youtube",
              type=click.Choice(["youtube", "tiktok", "both"], case_sensitive=False),
              show_default=True, help="Platform to scrape")
@click.option("--country", default="US", show_default=True,
              help="Country code for YouTube trending (US, GB, CA, AU, ...)")
@click.option("--niche", default="all", show_default=True,
              help="Niche filter for TikTok trends (or 'all')")
@click.option("--live", is_flag=True,
              help="Attempt real network fetch (requires yt-dlp for YouTube)")
@handle_error
def trends_fetch(platform: str, country: str, niche: str, live: bool) -> None:
    """Fetch trending content from YouTube and/or TikTok."""
    sess = get_session()
    if not sess.has_project():
        _err("No workspace loaded. Run 'workspace new' or use --workspace flag.")
        if not _repl_mode:
            sys.exit(1)
        return

    if not _json_output:
        if live:
            click.echo(f"Fetching live trends from {platform}...")
        else:
            click.echo(f"Loading trend data for {platform} (mock — add --live for real fetch)...")

    result = trends_mod.get_trend_snapshot(
        sess, platform=platform, country=country, niche=niche, live=live
    )

    if not _json_output:
        snap = result["snapshot"]
        click.echo(f"\nSnapshot {result['snapshot_id']} saved.")
        if snap["youtube"]:
            from cli_anything.viral_trends.utils.repl_skin import ReplSkin
            skin = ReplSkin()
            click.echo(f"\nYouTube Trending ({len(snap['youtube'])} videos):")
            skin.table(
                ["#", "Title", "Channel", "Views", "Category"],
                [[str(v["rank"]), v["title"][:35], v["channel"][:20],
                  f"{v['views']:,}", v.get("category", "")[:15]]
                 for v in snap["youtube"][:10]]
            )
        if snap["tiktok"]:
            from cli_anything.viral_trends.utils.repl_skin import ReplSkin
            skin = ReplSkin()
            click.echo(f"\nTikTok Trending ({len(snap['tiktok'])} hashtags):")
            skin.table(
                ["#", "Hashtag", "Posts", "Views", "Growth%", "Niche"],
                [[str(h["rank"]), h["hashtag"], f"{h['posts']:,}", f"{h['views']:,}",
                  f"+{h['growth_pct']}%", h.get("niche", "")]
                 for h in snap["tiktok"][:10]]
            )
    else:
        output(result)


@trends.command("list")
@handle_error
def trends_list() -> None:
    """List all saved trend snapshots."""
    sess = get_session()
    result = trends_mod.list_snapshots(sess)
    if not _json_output:
        if not result:
            click.echo("  No snapshots. Run 'trends fetch' to capture trend data.")
            return
        from cli_anything.viral_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["ID", "Timestamp", "Platform", "Country", "Niche", "YT", "TT"],
            [[s["snapshot_id"], s["timestamp"][:19], s["platform"],
              s["country"], s["niche"], str(s["yt_count"]), str(s["tt_count"])]
             for s in result]
        )
    else:
        output(result)


@trends.command("show")
@click.argument("snapshot_id")
@handle_error
def trends_show(snapshot_id: str) -> None:
    """Show full detail of a trend snapshot."""
    sess = get_session()
    result = trends_mod.show_snapshot(sess, snapshot_id)
    output(result, f"Snapshot: {snapshot_id}")


@trends.command("remove")
@click.argument("snapshot_id")
@handle_error
def trends_remove(snapshot_id: str) -> None:
    """Remove a trend snapshot."""
    sess = get_session()
    result = trends_mod.remove_snapshot(sess, snapshot_id)
    output(result, f"Removed snapshot {snapshot_id}")


# ── optimize group ────────────────────────────────────────────────────────────

@cli.group()
def optimize():
    """Account optimization commands (hashtags, times, hooks, profile)."""
    pass


@optimize.command("hashtags")
@click.option("--niche", required=True, help="Content niche")
@click.option("--platform", default="tiktok", show_default=True,
              help="Target platform")
@click.option("--count", default=10, show_default=True, type=int,
              help="Number of hashtags to return")
@click.option("--set", "set_name", default=None,
              help="Specific hashtag set name")
@click.option("--list", "list_sets", is_flag=True,
              help="List all available hashtag sets for this niche")
@handle_error
def optimize_hashtags(niche: str, platform: str, count: int,
                      set_name: Optional[str], list_sets: bool) -> None:
    """Get curated hashtag sets for a niche."""
    if list_sets:
        result = opt_mod.list_hashtag_sets(niche=niche)
        if not _json_output:
            from cli_anything.viral_trends.utils.repl_skin import ReplSkin
            skin = ReplSkin()
            skin.table(
                ["Set Name", "Niche", "Platform", "Reach", "Tags"],
                [[s["set_name"], s["niche"], s["platform"], s["reach_tier"],
                  " ".join(s["preview"])]
                 for s in result]
            )
        else:
            output(result)
        return

    result = opt_mod.get_hashtags(niche=niche, platform=platform,
                                   set_name=set_name, count=count)
    if not _json_output:
        click.echo(f"\nHashtag set: {result['set_name']} (reach: {result['reach_tier']})")
        click.echo("  " + "  ".join(result["tags"]))
    else:
        output(result)


@optimize.command("times")
@click.option("--platform", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "youtube", "instagram"], case_sensitive=False),
              help="Target platform")
@click.option("--day", default=None,
              help="Specific day (monday..sunday), or omit for top windows")
@handle_error
def optimize_times(platform: str, day: Optional[str]) -> None:
    """Get optimal posting times for a platform."""
    result = opt_mod.get_posting_times(platform=platform, day=day)
    if not _json_output:
        from cli_anything.viral_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        click.echo(f"\nOptimal posting windows for {platform}:")
        skin.table(
            ["Day", "Start", "End", "Score"],
            [[w.get("day", day or "all"), w["start"], w["end"], f"{w['score']}/100"]
             for w in result["windows"]]
        )
    else:
        output(result)


@optimize.command("hooks")
@click.option("--type", "hook_type", default="curiosity", show_default=True,
              type=click.Choice(["curiosity", "urgency", "authority",
                                 "relatability", "controversy"], case_sensitive=False),
              help="Hook style")
@click.option("--niche", default="general", show_default=True, help="Content niche")
@click.option("--list", "list_hooks", is_flag=True, help="List all hook types")
@handle_error
def optimize_hooks(hook_type: str, niche: str, list_hooks: bool) -> None:
    """Get caption hook templates."""
    if list_hooks:
        result = opt_mod.list_hook_types()
        if not _json_output:
            from cli_anything.viral_trends.utils.repl_skin import ReplSkin
            skin = ReplSkin()
            skin.table(
                ["Type", "Description", "Example"],
                [[h["hook_type"], h["description"][:40], h["example"][:40]] for h in result]
            )
        else:
            output(result)
        return

    result = opt_mod.get_caption_hook(hook_type=hook_type, niche=niche)
    if not _json_output:
        click.echo(f"\n{hook_type.title()} hooks for {niche}:")
        for i, hook in enumerate(result["hooks"], 1):
            click.echo(f"  {i}. {hook}")
    else:
        output(result)


@optimize.command("profile")
@click.option("--niche", required=True, help="Content niche")
@click.option("--platform", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "youtube", "instagram"], case_sensitive=False),
              help="Target platform")
@handle_error
def optimize_profile(niche: str, platform: str) -> None:
    """Generate a full account optimization report."""
    result = opt_mod.optimize_profile(niche=niche, platform=platform)
    if not _json_output:
        from cli_anything.viral_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"Optimization Report — {niche} on {platform}")
        skin.status("Hashtag Set", result["hashtag_set"])
        skin.status("Top Tags", "  ".join(result["top_hashtags"][:5]))
        skin.status("Best Day", result["best_posting_day"].title())
        skin.status("Best Time", result["best_posting_time"])
        click.echo()
        click.echo("  Action Plan:")
        for line in result["action_plan"].split("\n"):
            click.echo(f"  {line}")
    else:
        output(result)


# ── schedule group ────────────────────────────────────────────────────────────

@cli.group()
def schedule():
    """Content calendar commands (add, remove, list, calendar, generate, mark)."""
    pass


@schedule.command("add")
@click.option("--day", required=True,
              type=click.Choice(sched_mod.DAYS, case_sensitive=False),
              help="Day of week")
@click.option("--time", "post_time", required=True,
              help="Post time in HH:MM format (e.g. 19:00)")
@click.option("--platform", required=True,
              type=click.Choice(sched_mod.PLATFORMS, case_sensitive=False),
              help="Target platform")
@click.option("--type", "content_type", default="video", show_default=True,
              type=click.Choice(sched_mod.CONTENT_TYPES, case_sensitive=False))
@click.option("--topic", default="", help="Content topic/description")
@click.option("--hashtag-set", "hashtag_set", default=None)
@click.option("--hook-type", "hook_type", default="curiosity", show_default=True,
              type=click.Choice(sched_mod._HOOK_ROTATION, case_sensitive=False))
@click.option("--notes", default="")
@handle_error
def schedule_add(day: str, post_time: str, platform: str, content_type: str,
                 topic: str, hashtag_set: Optional[str], hook_type: str,
                 notes: str) -> None:
    """Add a single schedule entry."""
    sess = get_session()
    result = sched_mod.add_entry(
        sess, day=day, time=post_time, platform=platform,
        content_type=content_type, topic=topic,
        hashtag_set=hashtag_set, hook_type=hook_type, notes=notes
    )
    output(result, f"Added {platform} entry on {day} at {post_time}")


@schedule.command("remove")
@click.argument("entry_id")
@handle_error
def schedule_remove(entry_id: str) -> None:
    """Remove a schedule entry by ID."""
    sess = get_session()
    result = sched_mod.remove_entry(sess, entry_id)
    output(result, f"Removed entry {entry_id}")


@schedule.command("update")
@click.argument("entry_id")
@click.option("--topic", default=None)
@click.option("--notes", default=None)
@click.option("--status", default=None,
              type=click.Choice(sched_mod.STATUSES, case_sensitive=False))
@click.option("--time", "post_time", default=None)
@click.option("--hook-type", "hook_type", default=None)
@handle_error
def schedule_update(entry_id: str, topic: Optional[str], notes: Optional[str],
                    status: Optional[str], post_time: Optional[str],
                    hook_type: Optional[str]) -> None:
    """Update a schedule entry."""
    sess = get_session()
    kwargs = {}
    if topic is not None:
        kwargs["topic"] = topic
    if notes is not None:
        kwargs["notes"] = notes
    if status is not None:
        kwargs["status"] = status
    if post_time is not None:
        kwargs["time"] = post_time
    if hook_type is not None:
        kwargs["hook_type"] = hook_type
    result = sched_mod.update_entry(sess, entry_id, **kwargs)
    output(result, f"Updated entry {entry_id}")


@schedule.command("list")
@click.option("--day", default=None,
              help="Filter by day (monday..sunday)")
@click.option("--platform", default=None,
              help="Filter by platform")
@handle_error
def schedule_list(day: Optional[str], platform: Optional[str]) -> None:
    """List schedule entries."""
    sess = get_session()
    result = sched_mod.list_entries(sess, day=day, platform=platform)
    if not _json_output:
        if not result:
            click.echo("  No schedule entries. Run 'schedule generate' or 'schedule add'.")
            return
        from cli_anything.viral_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["ID", "Day", "Time", "Platform", "Type", "Status", "Topic"],
            [[e["entry_id"], e["day"], e["time"], e["platform"],
              e["content_type"], e["status"], e.get("topic", "")[:25]]
             for e in result]
        )
    else:
        output(result)


@schedule.command("calendar")
@handle_error
def schedule_calendar() -> None:
    """Show the 7-day content calendar."""
    sess = get_session()
    calendar = sched_mod.show_calendar(sess)
    if not _json_output:
        from cli_anything.viral_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        click.echo()
        total = sum(len(v) for v in calendar.values())
        click.echo(f"  7-Day Content Calendar ({total} entries)")
        click.echo()
        for day, entries in calendar.items():
            if entries:
                click.echo(f"  {day.upper()}")
                for e in entries:
                    status_icon = {"planned": "○", "drafted": "◐", "published": "●"}.get(e["status"], "○")
                    click.echo(
                        f"    {status_icon} {e['time']}  [{e['platform']}]  {e.get('topic', e['content_type'])[:40]}"
                    )
                click.echo()
    else:
        output(calendar)


@schedule.command("generate")
@click.option("--niche", required=True, help="Content niche")
@click.option("--platforms", default="tiktok",
              help="Comma-separated list: tiktok,youtube,instagram")
@click.option("--posts-per-day", "posts_per_day", default=2, show_default=True, type=int,
              help="Posts per day per platform")
@click.option("--overwrite", is_flag=True,
              help="Clear existing schedule and regenerate")
@handle_error
def schedule_generate(niche: str, platforms: str, posts_per_day: int,
                      overwrite: bool) -> None:
    """Auto-generate a 7-day content schedule from optimal posting windows."""
    sess = get_session()
    platform_list = [p.strip().lower() for p in platforms.split(",")]
    if not _json_output:
        click.echo(f"Generating {posts_per_day} posts/day for {niche} on {', '.join(platform_list)}...")
    result = sched_mod.generate_week(
        sess, niche=niche, platforms=platform_list,
        posts_per_day=posts_per_day, overwrite=overwrite
    )
    if not _json_output:
        click.echo(f"\nCreated {result['entries_created']} schedule entries:")
        for day, count in result["schedule_preview"].items():
            if count:
                click.echo(f"  {day:<12} {count} posts")
        click.echo(f"\nRun 'schedule calendar' to view the full schedule.")
    else:
        output(result)


@schedule.command("mark")
@click.argument("entry_id")
@click.option("--status", required=True,
              type=click.Choice(sched_mod.STATUSES, case_sensitive=False))
@handle_error
def schedule_mark(entry_id: str, status: str) -> None:
    """Mark a schedule entry's status (planned/drafted/published)."""
    sess = get_session()
    result = sched_mod.mark_status(sess, entry_id, status)
    output(result, f"Marked {entry_id} as {status}")


# ── guide group ───────────────────────────────────────────────────────────────

@cli.group()
def guide():
    """Learning guides: theme-page, converting, hashtags, posting-times, hooks, etc."""
    pass


def _print_guide(content: dict) -> None:
    """Print a guide dict in a readable format."""
    from cli_anything.viral_trends.utils.repl_skin import ReplSkin
    skin = ReplSkin()
    click.echo()
    skin.section(content["title"])
    for section in content.get("sections", []):
        click.echo()
        click.echo(f"  ── {section['heading']} ──")
        click.echo()
        for line in section.get("body", "").split("\n"):
            click.echo(f"  {line}")
        for tip in section.get("tips", []):
            click.echo(f"    • {tip}")
        for cmd in section.get("commands", []):
            click.echo(f"    $ {cmd}")

    if content.get("quick_commands"):
        click.echo()
        skin.section("Quick Commands")
        for cmd in content["quick_commands"]:
            click.echo(f"  $ {cmd}")
    click.echo()


@guide.command("overview")
@handle_error
def guide_overview() -> None:
    """Show the viral-trends tool overview."""
    content = guide_mod.guide_content("overview")
    if _json_output:
        output(content)
    else:
        _print_guide(content)


@guide.command("theme-page")
@handle_error
def guide_theme_page() -> None:
    """Full theme page strategy masterclass."""
    content = guide_mod.guide_content("theme-page")
    if _json_output:
        output(content)
    else:
        _print_guide(content)


@guide.command("converting")
@handle_error
def guide_converting() -> None:
    """Guide to converting followers into buyers and revenue streams."""
    content = guide_mod.guide_content("converting")
    if _json_output:
        output(content)
    else:
        _print_guide(content)


@guide.command("hashtags")
@handle_error
def guide_hashtags() -> None:
    """Hashtag strategy guide."""
    content = guide_mod.guide_content("hashtags")
    if _json_output:
        output(content)
    else:
        _print_guide(content)


@guide.command("posting-times")
@handle_error
def guide_posting_times() -> None:
    """Optimal posting times guide for all platforms."""
    content = guide_mod.guide_content("posting-times")
    if _json_output:
        output(content)
    else:
        _print_guide(content)


@guide.command("hooks")
@handle_error
def guide_hooks() -> None:
    """Caption hook frameworks to stop the scroll."""
    content = guide_mod.guide_content("hooks")
    if _json_output:
        output(content)
    else:
        _print_guide(content)


@guide.command("youtube")
@handle_error
def guide_youtube() -> None:
    """YouTube trending content guide."""
    content = guide_mod.guide_content("youtube")
    if _json_output:
        output(content)
    else:
        _print_guide(content)


@guide.command("tiktok")
@handle_error
def guide_tiktok() -> None:
    """TikTok viral content guide."""
    content = guide_mod.guide_content("tiktok")
    if _json_output:
        output(content)
    else:
        _print_guide(content)


@guide.command("schedule")
@handle_error
def guide_schedule() -> None:
    """Content scheduling guide."""
    content = guide_mod.guide_content("schedule")
    if _json_output:
        output(content)
    else:
        _print_guide(content)


@guide.command("list")
@handle_error
def guide_list() -> None:
    """List all available guides."""
    result = guide_mod.list_guides()
    if not _json_output:
        from cli_anything.viral_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(["Key", "Title"], [[g["key"], g["title"]] for g in result])
    else:
        output(result)


# ── session group ─────────────────────────────────────────────────────────────

@cli.group("session")
def session_group():
    """Session commands (undo, redo, status, history)."""
    pass


@session_group.command("undo")
@handle_error
def session_undo() -> None:
    """Undo the last operation."""
    sess = get_session()
    description = sess.undo()
    output({"success": True, "undone": description}, f"Undone: {description}")


@session_group.command("redo")
@handle_error
def session_redo() -> None:
    """Redo the last undone operation."""
    sess = get_session()
    description = sess.redo()
    output({"success": True, "redone": description}, f"Redone: {description}")


@session_group.command("status")
@handle_error
def session_status() -> None:
    """Show session status."""
    sess = get_session()
    result = sess.status()
    output(result, "Session status:")


@session_group.command("history")
@handle_error
def session_history() -> None:
    """Show the undo history stack."""
    sess = get_session()
    result = sess.list_history()
    output(result, f"History ({len(result)} entries):")


# ── REPL ──────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--workspace", "workspace_path", default=None,
              help="Workspace file to open on start")
def repl(workspace_path: Optional[str]) -> None:
    """Start an interactive REPL session."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.viral_trends.utils.repl_skin import ReplSkin
    skin = ReplSkin("viral_trends", version="1.0.0")
    skin.print_banner()

    sess = get_session()

    if workspace_path and not sess.has_project():
        try:
            ws_mod.open_workspace(sess, workspace_path)
            skin.success(f"Opened workspace: {workspace_path}")
        except Exception as e:
            skin.error(str(e))

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "workspace new --name NAME --niche NICHE": "Create a new workspace",
        "workspace open <path>":                   "Open a workspace file",
        "workspace save [path]":                   "Save current workspace",
        "workspace info":                          "Show workspace info",
        "workspace niches":                        "List available niches",
        "trends fetch --platform youtube|tiktok":  "Fetch trending content",
        "trends list":                             "List saved snapshots",
        "trends show <snap_id>":                   "Show snapshot detail",
        "optimize profile --niche NICHE":          "Full optimization report",
        "optimize hashtags --niche NICHE":         "Get hashtag sets",
        "optimize times --platform tiktok":        "Get posting windows",
        "optimize hooks --type curiosity":         "Get caption hooks",
        "schedule generate --niche NICHE":         "Auto-generate 7-day schedule",
        "schedule calendar":                       "View 7-day calendar",
        "schedule list":                           "List entries",
        "schedule add --day mon --time 19:00":     "Add entry",
        "schedule mark <id> --status published":   "Mark entry status",
        "guide theme-page":                        "Theme page masterclass",
        "guide converting":                        "Converting followers to buyers",
        "guide hashtags":                          "Hashtag strategy",
        "guide posting-times":                     "Optimal posting times",
        "guide hooks":                             "Caption hook frameworks",
        "guide list":                              "List all guides",
        "session undo":                            "Undo last operation",
        "session redo":                            "Redo last operation",
        "session status":                          "Show session status",
        "help":                                    "Show this help",
        "quit / exit":                             "Exit the REPL",
    }

    while True:
        try:
            project_name = ""
            modified = False
            if sess.has_project():
                project_name = sess.project.get("name", "untitled")
                modified = sess._modified

            raw = skin.get_input(pt_session, project_name, modified)

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


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    cli()


if __name__ == "__main__":
    main()
