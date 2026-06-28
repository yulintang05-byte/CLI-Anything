"""Social Trends CLI - Agent-native viral trend discovery for YouTube & TikTok.

Fetches trending videos, hashtags, and music. Manages accounts, generates
content calendars, and provides theme page strategy guides.

Usage:
    python3 -m cli_anything.social_trends [--json] [--project PATH] <command>
    python3 -m cli_anything.social_trends   (launches REPL)
"""

import json
import sys
import shlex
import click
from typing import Optional, Any

from cli_anything.social_trends.core.session import Session
from cli_anything.social_trends.core import project as proj_mod
from cli_anything.social_trends.core import trends as trends_mod
from cli_anything.social_trends.core import hashtags as hashtags_mod
from cli_anything.social_trends.core import music as music_mod
from cli_anything.social_trends.core import accounts as accounts_mod
from cli_anything.social_trends.core import theme_pages as theme_mod
from cli_anything.social_trends.core import content_calendar as cal_mod

# ── Global state ───────────────────────────────────────────────────────────────

_session: Optional[Session] = None
_json_output: bool = False

def get_session() -> Session:
    global _session
    if _session is None:
        _session = Session()
    return _session

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
        if isinstance(v, dict):
            click.echo(f"{pad}{k}:")
            _print_dict(v, indent + 2)
        elif isinstance(v, list):
            if v and isinstance(v[0], (str, int, float)):
                click.echo(f"{pad}{k}: {', '.join(str(i) for i in v[:10])}")
            else:
                click.echo(f"{pad}{k}: [{len(v)} items]")
        else:
            click.echo(f"{pad}{k}: {v}")

def _print_list(lst: list, limit: int = 20) -> None:
    if not lst:
        click.echo("  (empty)")
        return
    for item in lst[:limit]:
        if isinstance(item, dict):
            parts = []
            priority = ["title", "tag", "name", "handle", "date", "label", "niche_key"]
            for key in priority:
                if key in item:
                    parts.append(f"{key}={item[key]}")
            for k, v in item.items():
                if k not in priority and not isinstance(v, (dict, list)) and len(parts) < 5:
                    parts.append(f"{k}={v}")
            click.echo("  " + "  ".join(parts))
        else:
            click.echo(f"  {item}")
    if len(lst) > limit:
        click.echo(f"  ... and {len(lst) - limit} more")

def _err(msg: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": msg}))
    else:
        click.echo(f"Error: {msg}", err=True)
    sys.exit(1)

# ── Root group ─────────────────────────────────────────────────────────────────

@click.group()
@click.option("--json", "json_out", is_flag=True, help="Output JSON instead of human text")
@click.option("--project", "project_path", default=None, help="Path to project JSON file")
@click.pass_context
def cli(ctx: click.Context, json_out: bool, project_path: Optional[str]) -> None:
    """Social Trends — viral trend discovery for YouTube & TikTok."""
    global _json_output
    _json_output = json_out
    ctx.ensure_object(dict)
    if project_path:
        s = get_session()
        if not s.has_project():
            try:
                proj_mod.open_project(s, project_path)
            except FileNotFoundError:
                pass

# ── Session ────────────────────────────────────────────────────────────────────

@cli.group()
def session() -> None:
    """Session state, undo/redo, and history."""

@session.command("status")
def session_status() -> None:
    """Show session status."""
    output(get_session().status())

@session.command("undo")
def session_undo() -> None:
    """Undo the last operation."""
    desc = get_session().undo()
    output({"undone": desc})

@session.command("redo")
def session_redo() -> None:
    """Redo the last undone operation."""
    desc = get_session().redo()
    output({"redone": desc})

@session.command("history")
def session_history() -> None:
    """Show undo history."""
    output(get_session().list_history())

@session.command("save")
@click.argument("path", required=False)
def session_save(path: Optional[str]) -> None:
    """Save current project to disk."""
    saved = get_session().save_session(path)
    output({"saved": saved})

# ── Project ────────────────────────────────────────────────────────────────────

@cli.group()
def project() -> None:
    """Project management."""

@project.command("new")
@click.argument("name")
def project_new(name: str) -> None:
    """Create a new social trends project."""
    p = proj_mod.new_project(get_session(), name)
    output({"created": p["name"], "message": f"Project '{name}' created. Use 'project save PATH' to persist."})

@project.command("open")
@click.argument("path")
def project_open(path: str) -> None:
    """Open an existing project file."""
    p = proj_mod.open_project(get_session(), path)
    output({"opened": p["name"], "path": path})

@project.command("info")
def project_info() -> None:
    """Show project summary."""
    output(proj_mod.project_info(get_session()))

@project.command("set-config")
@click.argument("key")
@click.argument("value")
def project_set_config(key: str, value: str) -> None:
    """Set a project config value (e.g. youtube_api_key, default_region, niche)."""
    output(proj_mod.set_config(get_session(), key, value))

@project.command("get-config")
def project_get_config() -> None:
    """Show current project config."""
    output(proj_mod.get_config(get_session()))

# ── Trends ─────────────────────────────────────────────────────────────────────

@cli.group()
def trends() -> None:
    """Fetch and search viral trends from YouTube and TikTok."""

@trends.command("fetch")
@click.option("--platform", default="both", type=click.Choice(["youtube", "tiktok", "both"]))
@click.option("--category", default="all", help="Content category (music, gaming, fitness, etc.)")
@click.option("--region", default="US", help="Region code (US, GB, CA, AU, etc.)")
@click.option("--limit", default=20, type=int, help="Number of trends to fetch per platform")
def trends_fetch(platform: str, category: str, region: str, limit: int) -> None:
    """Fetch currently trending content. Requires yt-dlp (or YouTube API key for YouTube)."""
    result = trends_mod.fetch_trends(get_session(), platform=platform, category=category, region=region, limit=limit)
    output(result, f"Fetched {result['youtube_count']} YouTube + {result['tiktok_count']} TikTok trends")

@trends.command("list")
@click.option("--platform", default=None, help="Filter by platform")
@click.option("--limit", default=20, type=int)
def trends_list(platform: Optional[str], limit: int) -> None:
    """List cached trends."""
    result = trends_mod.list_cached_trends(get_session(), platform=platform)
    output(result[:limit], f"{len(result)} cached trends")

@trends.command("search")
@click.argument("query")
@click.option("--platform", default=None)
def trends_search(query: str, platform: Optional[str]) -> None:
    """Search cached trends by keyword."""
    result = trends_mod.search_trends(get_session(), query=query, platform=platform)
    output(result, f"{len(result)} matching trends for '{query}'")

@trends.command("top")
@click.option("--platform", default=None)
@click.option("--n", default=10, type=int, help="Number of top trends to return")
def trends_top(platform: Optional[str], n: int) -> None:
    """Show top N trends by view count."""
    result = trends_mod.get_top_trends(get_session(), platform=platform, n=n)
    output(result, f"Top {n} trends")

@trends.command("extract-hashtags")
def trends_extract_hashtags() -> None:
    """Extract and rank all hashtags found in cached trends."""
    result = trends_mod.extract_trend_hashtags(get_session())
    output(result[:30], f"Found {len(result)} unique hashtags in cached trends")

# ── Hashtags ───────────────────────────────────────────────────────────────────

@cli.group()
def hashtags() -> None:
    """Hashtag research, scoring, and set generation."""

@hashtags.command("research")
@click.argument("topic")
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]))
@click.option("--limit", default=30, type=int)
def hashtags_research(topic: str, platform: str, limit: int) -> None:
    """Research hashtags for a topic and platform."""
    result = hashtags_mod.research_hashtags(get_session(), topic=topic, platform=platform, limit=limit)
    output(result)

@hashtags.command("score")
@click.argument("tag")
def hashtags_score(tag: str) -> None:
    """Score and classify a hashtag by tier and competition."""
    output(hashtags_mod.score_hashtag(tag))

@hashtags.command("generate-set")
@click.argument("niche")
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]))
@click.option("--mix", default="balanced", type=click.Choice(["balanced", "aggressive", "safe"]))
@click.option("--name", "set_name", default=None, help="Custom name for the set")
def hashtags_generate_set(niche: str, platform: str, mix: str, set_name: Optional[str]) -> None:
    """Generate a ready-to-use hashtag set for a niche."""
    result = hashtags_mod.generate_hashtag_set(get_session(), niche=niche, platform=platform, mix=mix, set_name=set_name)
    output(result)

@hashtags.command("list")
def hashtags_list() -> None:
    """List all saved hashtag sets."""
    output(hashtags_mod.list_hashtag_sets(get_session()))

# ── Music ──────────────────────────────────────────────────────────────────────

@cli.group()
def music() -> None:
    """Trending music and sound discovery."""

@music.command("trending")
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok", "youtube", "both"]))
@click.option("--limit", default=20, type=int)
def music_trending(platform: str, limit: int) -> None:
    """Fetch trending sounds and music."""
    result = music_mod.fetch_trending_music(get_session(), platform=platform, limit=limit)
    output(result)

@music.command("search")
@click.argument("query")
def music_search(query: str) -> None:
    """Search cached music by title or artist."""
    result = music_mod.search_music(get_session(), query=query)
    output(result, f"{len(result)} tracks matching '{query}'")

@music.command("list")
@click.option("--platform", default=None)
def music_list(platform: Optional[str]) -> None:
    """List all cached trending tracks."""
    result = music_mod.list_music(get_session(), platform=platform)
    output(result, f"{len(result)} cached tracks")

@music.command("recommend")
@click.argument("niche")
@click.option("--platform", default="tiktok")
@click.option("--n", default=5, type=int)
def music_recommend(niche: str, platform: str, n: int) -> None:
    """Recommend trending music for a given niche."""
    result = music_mod.recommend_music(get_session(), niche=niche, platform=platform, n=n)
    output(result, f"Top {n} recommended tracks for '{niche}'")

# ── Accounts ───────────────────────────────────────────────────────────────────

@cli.group()
def accounts() -> None:
    """Social media account management and optimization."""

@accounts.command("add")
@click.argument("name")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "youtube", "instagram", "twitter", "facebook"]))
@click.option("--handle", required=True, help="Account handle/username (without @)")
@click.option("--niche", default="", help="Account niche (e.g. fitness, luxury, finance)")
def accounts_add(name: str, platform: str, handle: str, niche: str) -> None:
    """Add a social media account to this project."""
    result = accounts_mod.add_account(get_session(), name=name, platform=platform, handle=handle, niche=niche)
    output(result, f"Added @{handle} on {platform}")

@accounts.command("stats")
@click.argument("handle")
@click.option("--platform", required=True)
@click.option("--followers", type=int, default=None)
@click.option("--posts", type=int, default=None)
@click.option("--avg-views", type=int, default=None)
@click.option("--avg-likes", type=int, default=None)
@click.option("--avg-comments", type=int, default=None)
def accounts_stats(handle: str, platform: str, followers: Optional[int], posts: Optional[int],
                   avg_views: Optional[int], avg_likes: Optional[int], avg_comments: Optional[int]) -> None:
    """Update account statistics."""
    kwargs = {}
    if followers is not None:
        kwargs["followers"] = followers
    if posts is not None:
        kwargs["posts"] = posts
    if avg_views is not None:
        kwargs["avg_views"] = avg_views
    if avg_likes is not None:
        kwargs["avg_likes"] = avg_likes
    if avg_comments is not None:
        kwargs["avg_comments"] = avg_comments
    result = accounts_mod.update_account_stats(get_session(), handle=handle, platform=platform, **kwargs)
    output(result, f"Updated stats for @{handle}")

@accounts.command("optimize")
@click.argument("handle")
@click.option("--platform", required=True)
def accounts_optimize(handle: str, platform: str) -> None:
    """Generate a full optimization report for an account."""
    result = accounts_mod.optimize_account(get_session(), handle=handle, platform=platform)
    output(result)

@accounts.command("list")
@click.option("--platform", default=None)
def accounts_list(platform: Optional[str]) -> None:
    """List all accounts."""
    result = accounts_mod.list_accounts(get_session(), platform=platform)
    output(result, f"{len(result)} accounts")

@accounts.command("remove")
@click.argument("handle")
@click.option("--platform", required=True)
def accounts_remove(handle: str, platform: str) -> None:
    """Remove an account from the project."""
    result = accounts_mod.remove_account(get_session(), handle=handle, platform=platform)
    output(result)

# ── Theme Pages ────────────────────────────────────────────────────────────────

@cli.group(name="theme-page")
def theme_page() -> None:
    """Theme page strategy: niches, content pillars, monetization."""

@theme_page.command("guide")
def theme_page_guide() -> None:
    """Complete step-by-step guide to building a converting theme page."""
    output(theme_mod.converting_theme_page_guide())

@theme_page.command("niches")
def theme_page_niches() -> None:
    """List all supported niches with difficulty and monetization potential."""
    output(theme_mod.list_niches())

@theme_page.command("strategy")
@click.argument("niche")
@click.option("--monetization", default="all", help="Filter by monetization type (affiliate/ads/brand_deals/etc.)")
def theme_page_strategy(niche: str, monetization: str) -> None:
    """Get complete theme page strategy for a niche."""
    output(theme_mod.get_strategy(niche, monetization=monetization))

@theme_page.command("content-pillars")
@click.argument("niche")
def theme_page_content_pillars(niche: str) -> None:
    """Get content pillar breakdown and posting guidelines for a niche."""
    output(theme_mod.get_content_pillars(niche))

@theme_page.command("posting-schedule")
@click.argument("niche")
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok", "instagram", "youtube"]))
def theme_page_posting_schedule(niche: str, platform: str) -> None:
    """Get optimal posting schedule for a niche+platform."""
    output(theme_mod.get_posting_schedule(niche, platform))

# ── Calendar ───────────────────────────────────────────────────────────────────

@cli.group()
def calendar() -> None:
    """Content calendar generation and management."""

@calendar.command("generate")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]))
@click.option("--niche", required=True, help="Your content niche")
@click.option("--weeks", default=4, type=int, help="Number of weeks to generate (default: 4)")
@click.option("--posts-per-day", default=2, type=int, help="Posts per day (default: 2)")
def calendar_generate(platform: str, niche: str, weeks: int, posts_per_day: int) -> None:
    """Generate a content calendar for a platform and niche."""
    result = cal_mod.generate_calendar(get_session(), platform=platform, niche=niche, weeks=weeks, posts_per_day=posts_per_day)
    output(result)

@calendar.command("view")
@click.option("--platform", default=None)
@click.option("--status", default=None, type=click.Choice(["planned", "ready", "posted", "skipped"]))
@click.option("--week", default=None, type=int, help="Week offset (0=this week, 1=next, etc.)")
@click.option("--limit", default=50, type=int)
def calendar_view(platform: Optional[str], status: Optional[str], week: Optional[int], limit: int) -> None:
    """View calendar entries."""
    result = cal_mod.view_calendar(get_session(), platform=platform, status=status, week=week)
    output(result[:limit], f"{len(result)} entries")

@calendar.command("add")
@click.option("--date", required=True, help="Date in YYYY-MM-DD format")
@click.option("--platform", required=True)
@click.option("--type", "content_type", required=True, type=click.Choice(cal_mod.CONTENT_TYPES))
@click.option("--title", required=True)
@click.option("--niche", default="")
@click.option("--hashtags", default="")
@click.option("--notes", default="")
@click.option("--time", default="12:00 PM")
def calendar_add(date: str, platform: str, content_type: str, title: str,
                 niche: str, hashtags: str, notes: str, time: str) -> None:
    """Manually add a calendar entry."""
    result = cal_mod.add_calendar_entry(
        get_session(), date=date, platform=platform, content_type=content_type,
        title=title, niche=niche, hashtags=hashtags, notes=notes, time=time,
    )
    output(result, f"Added entry for {date}")

@calendar.command("update-status")
@click.argument("entry_id")
@click.argument("status", type=click.Choice(["planned", "ready", "posted", "skipped"]))
@click.option("--notes", default="")
def calendar_update_status(entry_id: str, status: str, notes: str) -> None:
    """Update a calendar entry's status."""
    result = cal_mod.update_entry_status(get_session(), entry_id=entry_id, status=status, notes=notes)
    output(result, f"Entry {entry_id} marked as '{status}'")

@calendar.command("export")
@click.option("--format", "fmt", default="json", type=click.Choice(["json", "csv", "text"]))
@click.option("--platform", default=None)
def calendar_export(fmt: str, platform: Optional[str]) -> None:
    """Export calendar in JSON, CSV, or text format."""
    result = cal_mod.export_calendar(get_session(), fmt=fmt, platform=platform)
    if fmt in ("csv", "text"):
        click.echo(result.get("content", ""))
    else:
        output(result)

# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    """Main entry point — launches REPL if no args, otherwise runs command."""
    if len(sys.argv) == 1:
        from cli_anything.social_trends.utils.repl_skin import launch_repl
        launch_repl(cli, prog_name="social-trends")
    else:
        cli()

if __name__ == "__main__":
    main()
