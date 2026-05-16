"""Social Trends CLI — agent-native viral trend tracker and account optimizer.

Provides a full CLI for fetching YouTube/TikTok/Google viral trends,
optimizing social accounts, and building theme-page strategies.
Designed for AI agents (Claude Code, OpenCode, Codex) and humans alike.

Usage:
    python3 -m cli_anything.social_trends [--json] <command>
    python3 -m cli_anything.social_trends  (launches REPL)

Environment variables:
    YOUTUBE_API_KEY        YouTube Data API v3 key
    TIKTOK_CLIENT_KEY      TikTok for Developers app client key
    TIKTOK_CLIENT_SECRET   TikTok for Developers app client secret
"""

import json
import os
import sys
import shlex
import click
from typing import Optional, Any

from cli_anything.social_trends.core import (
    youtube as yt,
    tiktok as tt,
    google_trends as gt,
    optimizer as opt,
    theme_pages as tp,
)

_json_output: bool = False
_repl_mode: bool = False


# ── Output helpers ────────────────────────────────────────────────────────────

def output(data: Any, message: str = "") -> None:
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        _pretty(data)


def _pretty(data: Any, indent: int = 2) -> None:
    pad = " " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{pad}{k}:")
                _pretty(v, indent + 2)
            else:
                click.echo(f"{pad}{k}: {v}")
    elif isinstance(data, list):
        if not data:
            click.echo(f"{pad}(empty)")
            return
        for i, item in enumerate(data):
            if isinstance(item, dict):
                click.echo(f"{pad}[{i + 1}]")
                _pretty(item, indent + 2)
            else:
                click.echo(f"{pad}- {item}")
    else:
        click.echo(f"{pad}{data}")


def _err(msg: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": msg}), err=True)
    else:
        click.echo(f"Error: {msg}", err=True)


def _require_env(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        raise RuntimeError(
            f"Environment variable {name} is required. "
            f"Set it with: export {name}=<your_value>"
        )
    return val


def handle_error(func):
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RuntimeError as e:
            _err(str(e))
            if not _repl_mode:
                sys.exit(1)
        except (ValueError, KeyError) as e:
            _err(str(e))
            if not _repl_mode:
                sys.exit(1)
        except Exception as e:
            _err(f"Unexpected error: {e}")
            if not _repl_mode:
                sys.exit(1)

    return wrapper


# ── Root CLI ──────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output results as JSON")
@click.version_option("1.0.0", prog_name="social-trends")
@click.pass_context
def cli(ctx: click.Context, use_json: bool) -> None:
    """Social Trends — agent-native viral trend tracker & account optimizer.

    Track YouTube/TikTok/Google trends, optimize your accounts, and build
    profitable theme pages.

    \b
    Quick start:
      social-trends trends fetch google                   # No API key needed
      social-trends trends fetch youtube --category music
      social-trends trends fetch tiktok --category all
      social-trends account score --platform tiktok
      social-trends account schedule --platform tiktok
      social-trends theme-page niches
      social-trends theme-page playbook
      social-trends theme-page checklist --niche finance --platforms tiktok,youtube
    """
    global _json_output
    _json_output = use_json
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── trends group ──────────────────────────────────────────────────────────────

@cli.group()
def trends():
    """Fetch viral trends from YouTube, TikTok, and Google."""
    pass


@trends.group("fetch")
def trends_fetch():
    """Fetch trends from a specific platform."""
    pass


@trends_fetch.command("youtube")
@click.option("--category", default="all", show_default=True,
              help="Category: all,music,gaming,news,entertainment,sports,tech,film,comedy")
@click.option("--region", default="US", show_default=True, help="ISO 3166-1 country code")
@click.option("--max", "max_results", default=20, show_default=True, type=int, help="Max videos")
@click.option("--type", "fetch_type", default="videos", show_default=True,
              help="What to fetch: videos, hashtags, music")
@handle_error
def trends_fetch_youtube(category: str, region: str, max_results: int, fetch_type: str) -> None:
    """Fetch YouTube trending videos, hashtags, or music.

    Requires: YOUTUBE_API_KEY environment variable.

    \b
    Examples:
      social-trends trends fetch youtube --type hashtags --category music
      social-trends --json trends fetch youtube --region GB --max 30
    """
    api_key = _require_env("YOUTUBE_API_KEY")

    if fetch_type == "hashtags":
        data = yt.fetch_trending_hashtags(api_key, region, category, max_results)
        output(data, f"Top YouTube hashtags ({region}, {category}):")
    elif fetch_type == "music":
        data = yt.fetch_trending_music(api_key, region, max_results)
        output(data, f"Trending YouTube music videos ({region}):")
    else:
        data = yt.fetch_trending(api_key, region, category, max_results)
        output(data, f"Trending YouTube videos ({region}, {category}):")


@trends_fetch.command("tiktok")
@click.option("--category", default="all", show_default=True,
              help="Category: all,music,comedy,fashion,gaming,food,fitness,business,lifestyle")
@click.option("--region", default="US", show_default=True, help="ISO 3166-1 country code")
@click.option("--max", "max_results", default=20, show_default=True, type=int)
@click.option("--type", "fetch_type", default="videos", show_default=True,
              help="What to fetch: videos, hashtags, sounds")
@handle_error
def trends_fetch_tiktok(category: str, region: str, max_results: int, fetch_type: str) -> None:
    """Fetch TikTok trending videos, hashtags, or sounds.

    Requires: TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET environment variables.
    Get credentials at: https://developers.tiktok.com/

    \b
    Examples:
      social-trends trends fetch tiktok --type hashtags --category music
      social-trends --json trends fetch tiktok --type sounds --region US
    """
    client_key = _require_env("TIKTOK_CLIENT_KEY")
    client_secret = _require_env("TIKTOK_CLIENT_SECRET")

    if fetch_type == "hashtags":
        data = tt.fetch_trending_hashtags(client_key, client_secret, category, region, max_results)
        output(data, f"Top TikTok hashtags ({region}, {category}):")
    elif fetch_type == "sounds":
        data = tt.fetch_trending_sounds(client_key, client_secret, region, max_results)
        output(data, f"Trending TikTok sounds ({region}):")
    else:
        data = tt.fetch_trending_videos(client_key, client_secret, category, region, max_results)
        output(data, f"Trending TikTok videos ({region}, {category}):")


@trends_fetch.command("google")
@click.option("--geo", default="US", show_default=True, help="Country code (US, GB, AU...)")
@click.option("--type", "fetch_type", default="daily", show_default=True,
              help="Type: daily, realtime")
@click.option("--limit", default=20, show_default=True, type=int, help="Max results")
@handle_error
def trends_fetch_google(geo: str, fetch_type: str, limit: int) -> None:
    """Fetch Google trending searches. No API key required.

    \b
    Examples:
      social-trends trends fetch google
      social-trends trends fetch google --type realtime --geo GB
      social-trends --json trends fetch google --limit 50
    """
    if fetch_type == "realtime":
        data = gt.fetch_realtime_trends(geo)
        output(data[:limit], f"Real-time Google trends ({geo}):")
    else:
        data = gt.fetch_daily_trends(geo, limit)
        output(data, f"Daily Google trends ({geo}):")


@trends.command("summary")
@click.option("--geo", default="US", show_default=True, help="Region code")
@handle_error
def trends_summary(geo: str) -> None:
    """Fetch a cross-platform trends summary (Google only — no API keys needed).

    Use 'trends fetch youtube' or 'trends fetch tiktok' for platform-specific data.
    """
    google_data = gt.fetch_daily_trends(geo, 10)
    summary = {
        "region": geo,
        "google_top_10": [t["query"] for t in google_data],
        "note": (
            "For YouTube trends set YOUTUBE_API_KEY. "
            "For TikTok trends set TIKTOK_CLIENT_KEY + TIKTOK_CLIENT_SECRET."
        ),
    }
    output(summary, f"Trend summary for {geo}:")


# ── account group ─────────────────────────────────────────────────────────────

@cli.group()
def account():
    """Account optimization — score, schedule, best practices."""
    pass


@account.command("score")
@click.option("--platform", required=True, help="Platform: youtube, tiktok, instagram")
@click.option("--bio", default="", help="Current bio/description text")
@click.option("--followers", default=0, type=int, help="Follower / subscriber count")
@click.option("--avg-views", default=0, type=int, help="Average views per post")
@click.option("--posts", default=0, type=int, help="Total post count")
@click.option("--avg-hashtags", default=0, type=int, help="Average hashtags per post")
@click.option("--has-pic/--no-pic", default=True, help="Has profile picture")
@click.option("--has-link/--no-link", default=False, help="Has link in bio")
@click.option("--posts-per-week", default=0.0, type=float, help="Average posts per week")
@handle_error
def account_score(
    platform: str,
    bio: str,
    followers: int,
    avg_views: int,
    posts: int,
    avg_hashtags: int,
    has_pic: bool,
    has_link: bool,
    posts_per_week: float,
) -> None:
    """Score your account 0–100 and get actionable recommendations.

    \b
    Examples:
      social-trends account score --platform tiktok --followers 500 --avg-views 2000
      social-trends account score --platform youtube --followers 1200 --posts-per-week 1
      social-trends --json account score --platform instagram --followers 8000
    """
    result = opt.score_account(
        platform=platform,
        bio=bio,
        follower_count=followers,
        avg_views=avg_views,
        post_count=posts,
        avg_hashtags=avg_hashtags,
        has_profile_pic=has_pic,
        has_link=has_link,
        posting_frequency_per_week=posts_per_week,
    )
    output(result, f"Account score for {platform}:")


@account.command("schedule")
@click.option("--platform", required=True, help="Platform: youtube, tiktok, instagram")
@click.option("--posts-per-week", default=5, type=int, show_default=True)
@click.option("--tz-offset", default=-5, type=int, show_default=True,
              help="UTC offset (e.g. -5 for EST)")
@handle_error
def account_schedule(platform: str, posts_per_week: int, tz_offset: int) -> None:
    """Generate an optimized weekly posting schedule.

    \b
    Examples:
      social-trends account schedule --platform tiktok --posts-per-week 14
      social-trends account schedule --platform youtube --posts-per-week 2
    """
    result = opt.generate_posting_schedule(platform, tz_offset, posts_per_week)
    output(result, f"Optimized posting schedule for {platform} ({posts_per_week} posts/week):")


@account.command("best-practices")
@click.option("--platform", required=True, help="Platform: youtube, tiktok, instagram")
@handle_error
def account_best_practices(platform: str) -> None:
    """Show platform best practices reference guide.

    \b
    Examples:
      social-trends account best-practices --platform tiktok
      social-trends --json account best-practices --platform youtube
    """
    bp = opt.PLATFORM_BEST_PRACTICES.get(platform.lower())
    if not bp:
        available = ", ".join(opt.PLATFORM_BEST_PRACTICES.keys())
        raise ValueError(f"Unknown platform '{platform}'. Available: {available}")
    output(bp, f"Best practices for {platform}:")


@account.command("audit-youtube")
@click.argument("channel_id")
@handle_error
def account_audit_youtube(channel_id: str) -> None:
    """Audit a YouTube channel (requires YOUTUBE_API_KEY).

    CHANNEL_ID is the YouTube channel ID (starts with UC...) or custom handle.

    \b
    Examples:
      social-trends account audit-youtube UCxxxxxxxxxxxxxxxxxxxxxx
      social-trends --json account audit-youtube UCxxxxxxxxxxxxxxxxxxxxxx
    """
    api_key = _require_env("YOUTUBE_API_KEY")
    result = yt.fetch_channel_audit(api_key, channel_id)
    output(result, f"YouTube channel audit: {result.get('title', channel_id)}")


# ── theme-page group ───────────────────────────────────────────────────────────

@cli.group("theme-page")
def theme_page():
    """Theme page (niche/faceless page) strategy and playbook."""
    pass


@theme_page.command("niches")
@click.option("--difficulty", default=None,
              help="Filter by difficulty: Easy, Medium, Hard")
@handle_error
def theme_page_niches(difficulty: Optional[str]) -> None:
    """List all profitable theme page niches with monetization info.

    \b
    Examples:
      social-trends theme-page niches
      social-trends theme-page niches --difficulty Easy
      social-trends --json theme-page niches
    """
    result = tp.get_niche_list(difficulty)
    output(result, "Profitable theme page niches:")


@theme_page.command("niche-info")
@click.argument("niche_name")
@handle_error
def theme_page_niche_info(niche_name: str) -> None:
    """Get detailed info for a specific niche.

    \b
    Examples:
      social-trends theme-page niche-info finance
      social-trends theme-page niche-info "luxury lifestyle"
    """
    result = tp.get_niche_info(niche_name)
    output(result, f"Niche: {result['niche']}")


@theme_page.command("playbook")
@click.option("--phase", default=None, type=int,
              help="Show only one phase (1–4). Omit to see all phases.")
@handle_error
def theme_page_playbook(phase: Optional[int]) -> None:
    """Show the full theme page conversion playbook (4 phases).

    \b
    Examples:
      social-trends theme-page playbook
      social-trends theme-page playbook --phase 1
      social-trends --json theme-page playbook
    """
    result = tp.get_conversion_playbook(phase)
    output(result, "Theme page conversion playbook:")


@theme_page.command("checklist")
@click.option("--niche", required=True, help="Your niche (e.g. finance, fitness, ai)")
@click.option("--platforms", required=True,
              help="Comma-separated platforms (e.g. tiktok,youtube,instagram)")
@handle_error
def theme_page_checklist(niche: str, platforms: str) -> None:
    """Generate a personalized launch checklist for your theme page.

    \b
    Examples:
      social-trends theme-page checklist --niche finance --platforms tiktok,youtube
      social-trends --json theme-page checklist --niche fitness --platforms instagram,tiktok
    """
    platform_list = [p.strip() for p in platforms.split(",")]
    result = tp.build_launch_checklist(niche, platform_list)
    output(result, f"Launch checklist for '{niche}' theme page:")


@theme_page.command("pillars")
@handle_error
def theme_page_pillars() -> None:
    """Show the 5 content pillars and recommended posting ratio.

    \b
    Example:
      social-trends theme-page pillars
    """
    result = tp.get_content_pillars()
    output(result, "Content pillars and recommended ratio:")


@theme_page.command("monetization")
@handle_error
def theme_page_monetization() -> None:
    """Show monetization thresholds for each platform.

    \b
    Example:
      social-trends theme-page monetization
    """
    result = tp.get_monetization_thresholds()
    output(result, "Platform monetization thresholds:")


@theme_page.command("tools")
@handle_error
def theme_page_tools() -> None:
    """List free and paid tools for running a faceless theme page.

    \b
    Example:
      social-trends theme-page tools
    """
    result = tp.get_tools()
    output(result, "Theme page content creation tools:")


# ── REPL ──────────────────────────────────────────────────────────────────────

@cli.command()
def repl() -> None:
    """Start an interactive REPL session."""
    global _repl_mode
    _repl_mode = True

    click.echo("=" * 60)
    click.echo("  Social Trends CLI  v1.0.0")
    click.echo("  Viral trend tracker & account optimizer")
    click.echo("=" * 60)
    click.echo("  Type 'help' for commands, 'quit' to exit\n")

    _help_text = """
Commands:
  trends fetch google [--geo US] [--type daily|realtime]
  trends fetch youtube --type videos|hashtags|music [--category music] [--region US]
  trends fetch tiktok --type videos|hashtags|sounds [--category all] [--region US]
  trends summary [--geo US]

  account score --platform tiktok|youtube|instagram [options]
  account schedule --platform <p> --posts-per-week <n>
  account best-practices --platform <p>
  account audit-youtube <CHANNEL_ID>

  theme-page niches [--difficulty Easy|Medium]
  theme-page niche-info <name>
  theme-page playbook [--phase 1|2|3|4]
  theme-page checklist --niche <n> --platforms <p1,p2>
  theme-page pillars
  theme-page monetization
  theme-page tools

Global flags (prefix before command):
  --json    Output as JSON
"""

    import readline  # noqa: F401 — enables arrow-key history in REPL

    while True:
        try:
            raw = input("social-trends> ").strip()
        except (KeyboardInterrupt, EOFError):
            click.echo("\nGoodbye!")
            break

        if not raw:
            continue
        if raw in ("quit", "exit", "q"):
            click.echo("Goodbye!")
            break
        if raw in ("help", "h", "?"):
            click.echo(_help_text)
            continue

        try:
            args = shlex.split(raw)
        except ValueError as e:
            click.echo(f"Parse error: {e}", err=True)
            continue

        try:
            cli.main(args=args, standalone_mode=False)
        except SystemExit:
            pass
        except click.exceptions.UsageError as e:
            click.echo(f"Error: {e}", err=True)
        except Exception as e:
            click.echo(f"Error: {e}", err=True)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    cli()


if __name__ == "__main__":
    main()
