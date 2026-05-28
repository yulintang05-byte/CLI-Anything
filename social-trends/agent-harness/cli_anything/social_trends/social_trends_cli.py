"""Social Trends CLI — Agent-native social media trend scraper & optimizer.

Scrapes YouTube + TikTok for viral trends, hashtags, and music.
Provides account optimization, content calendars, and theme-page guides.

Usage:
    social-trends [--json] <command> [options]
    social-trends  (launches REPL)

Commands:
    youtube      Scrape YouTube trending videos, hashtags, music, keywords
    tiktok       Scrape TikTok trending hashtags, sounds, effects, niche tags
    analyze      Cross-platform trend analysis + content ideas
    optimize     Account optimization checklists + posting schedules
    theme-pages  Complete guide: create, grow, and monetize theme pages
    calendar     Generate a 1-week content calendar for a platform
    viral        Viral content formulas (hooks, structure, CTAs)
    hacks        Platform-specific growth hacks
"""

import json
import sys
import shlex
import functools
import click
from typing import Any, Optional

from cli_anything.social_trends.platforms import youtube as yt
from cli_anything.social_trends.platforms import tiktok as tt
from cli_anything.social_trends.core import optimizer as opt
from cli_anything.social_trends.core import trend_analyzer as ta

_json_output: bool = False
_repl_mode: bool = False


# ── Output helpers ─────────────────────────────────────────────────────────────

def output(data: Any, message: str = "") -> None:
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        _pretty(data)


def _pretty(data: Any, indent: int = 0) -> None:
    pad = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{pad}{_cyan(k)}:")
                _pretty(v, indent + 1)
            else:
                click.echo(f"{pad}{_cyan(k)}: {v}")
    elif isinstance(data, list):
        if not data:
            click.echo(f"{pad}(empty)")
            return
        for i, item in enumerate(data):
            if isinstance(item, dict):
                click.echo(f"{pad}[{i+1}]")
                _pretty(item, indent + 1)
            else:
                click.echo(f"{pad}• {item}")
    else:
        click.echo(f"{pad}{data}")


def _cyan(s: str) -> str:
    if sys.stdout.isatty():
        return f"\033[36m{s}\033[0m"
    return s


def _green(s: str) -> str:
    if sys.stdout.isatty():
        return f"\033[32m{s}\033[0m"
    return s


def _err(msg: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": msg}), err=True)
    else:
        click.echo(f"Error: {msg}", err=True)


def handle_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            _err(str(e))
            sys.exit(1)
    return wrapper


# ── Root command ───────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output machine-readable JSON")
@click.pass_context
def cli(ctx: click.Context, use_json: bool) -> None:
    """Social Trends — scrape YouTube/TikTok trends and optimize your accounts."""
    global _json_output, _repl_mode
    _json_output = use_json

    if ctx.invoked_subcommand is None:
        _repl_mode = True
        _run_repl()


# ── YouTube commands ──────────────────────────────────────────────────────────

@cli.group()
def youtube() -> None:
    """YouTube trending data: videos, hashtags, music, keywords."""


@youtube.command("trending")
@click.option("--category", default="all",
              type=click.Choice(["all", "music", "gaming", "movies", "news"]),
              help="Trending category")
@click.option("--limit", default=20, show_default=True, help="Number of results")
@handle_error
def yt_trending(category: str, limit: int) -> None:
    """Fetch YouTube trending videos."""
    click.echo(f"Fetching YouTube trending ({category})..." if not _json_output else "", err=True)
    videos = yt.get_trending_videos(category=category, limit=limit)
    if not videos:
        click.echo("No videos returned — YouTube may be blocking scrape. Try again shortly.", err=True)
        output([], "Trending videos:")
        return
    output(videos, f"\nYouTube Trending — {category.upper()} ({len(videos)} results)")


@youtube.command("hashtags")
@click.option("--limit", default=30, show_default=True)
@handle_error
def yt_hashtags(limit: int) -> None:
    """Extract trending hashtags from YouTube."""
    click.echo("Scanning YouTube for trending hashtags..." if not _json_output else "", err=True)
    tags = yt.get_trending_hashtags(limit=limit)
    output(tags, f"\nYouTube Trending Hashtags ({len(tags)} found)")


@youtube.command("music")
@click.option("--limit", default=20, show_default=True)
@handle_error
def yt_music(limit: int) -> None:
    """Fetch trending music videos from YouTube."""
    click.echo("Loading YouTube trending music..." if not _json_output else "", err=True)
    music = yt.get_trending_music(limit=limit)
    output(music, f"\nYouTube Trending Music ({len(music)} tracks)")


@youtube.command("keywords")
@click.option("--limit", default=25, show_default=True)
@handle_error
def yt_keywords(limit: int) -> None:
    """Extract high-frequency viral keywords from YouTube trending titles."""
    click.echo("Extracting viral keywords from YouTube..." if not _json_output else "", err=True)
    keywords = yt.get_viral_keywords(limit=limit)
    output(keywords, f"\nViral Keywords on YouTube ({len(keywords)} found)")


# ── TikTok commands ───────────────────────────────────────────────────────────

@cli.group()
def tiktok() -> None:
    """TikTok trending data: hashtags, sounds, effects, niche tags."""


@tiktok.command("hashtags")
@click.option("--limit", default=30, show_default=True)
@click.option("--category", default="all", help="Filter by category")
@handle_error
def tt_hashtags(limit: int, category: str) -> None:
    """Fetch trending TikTok hashtags."""
    click.echo(f"Loading TikTok trending hashtags ({category})..." if not _json_output else "", err=True)
    tags = tt.get_trending_hashtags(limit=limit, category=category)
    output(tags, f"\nTikTok Trending Hashtags ({len(tags)} found)")


@tiktok.command("sounds")
@click.option("--limit", default=20, show_default=True)
@handle_error
def tt_sounds(limit: int) -> None:
    """Fetch trending TikTok sounds and music."""
    click.echo("Loading TikTok trending sounds..." if not _json_output else "", err=True)
    sounds = tt.get_trending_sounds(limit=limit)
    output(sounds, f"\nTikTok Trending Sounds ({len(sounds)} tracks)")


@tiktok.command("effects")
@click.option("--limit", default=15, show_default=True)
@handle_error
def tt_effects(limit: int) -> None:
    """Fetch trending TikTok effects and filters."""
    click.echo("Loading TikTok trending effects..." if not _json_output else "", err=True)
    effects = tt.get_trending_effects(limit=limit)
    output(effects, f"\nTikTok Trending Effects ({len(effects)} effects)")


@tiktok.command("niche")
@click.argument("niche")
@click.option("--limit", default=20, show_default=True)
@handle_error
def tt_niche(niche: str, limit: int) -> None:
    """Get hashtag recommendations for a specific niche."""
    click.echo(f"Getting {niche} hashtags..." if not _json_output else "", err=True)
    tags = tt.get_niche_hashtags(niche=niche, limit=limit)
    output(tags, f"\nTikTok Hashtags for '{niche}' ({len(tags)} tags)")


# ── Analysis commands ─────────────────────────────────────────────────────────

@cli.group()
def analyze() -> None:
    """Cross-platform trend analysis and content idea generation."""


@analyze.command("cross-platform")
@click.option("--limit", default=15, show_default=True)
@handle_error
def cross_platform(limit: int) -> None:
    """Find topics trending on BOTH YouTube and TikTok."""
    click.echo("Analyzing cross-platform trends (this may take 10-15 seconds)..." if not _json_output else "", err=True)
    trends = ta.get_cross_platform_trends(limit=limit)
    output(trends, f"\nCross-Platform Trends — YouTube + TikTok ({len(trends)} found)")


@analyze.command("ideas")
@click.argument("niche")
@click.option("--count", default=10, show_default=True)
@handle_error
def content_ideas(niche: str, count: int) -> None:
    """Generate viral content ideas for a niche using current trends."""
    click.echo(f"Generating {count} content ideas for '{niche}'..." if not _json_output else "", err=True)
    ideas = ta.generate_content_ideas(niche=niche, count=count)
    output(ideas, f"\nContent Ideas for '{niche}' ({len(ideas)} ideas)")


@analyze.command("viral-formulas")
@click.option("--type", "fmt", default="all",
              type=click.Choice(["all", "hook", "structure", "cta"]))
@handle_error
def viral_formulas(fmt: str) -> None:
    """Show proven viral content formulas (hooks, structure, CTAs)."""
    formulas = ta.get_viral_formula(format_type=fmt)
    output(formulas, f"\nViral Content Formulas — {fmt.upper()}")


# ── Optimize commands ─────────────────────────────────────────────────────────

@cli.group()
def optimize() -> None:
    """Account optimization: checklists, posting times, growth hacks."""


@optimize.command("checklist")
@click.option("--platform", default="all",
              type=click.Choice(["all", "tiktok", "youtube", "instagram"]))
@handle_error
def checklist(platform: str) -> None:
    """Account optimization checklist for a platform."""
    data = opt.get_account_checklist(platform=platform)
    output(data, f"\nAccount Optimization Checklist — {platform.upper()}")


@optimize.command("posting-times")
@click.option("--platform", default="all",
              type=click.Choice(["all", "tiktok", "youtube", "instagram", "twitter"]))
@handle_error
def posting_times(platform: str) -> None:
    """Best posting times for maximum engagement."""
    times = opt.get_best_posting_times(platform=platform)
    output(times, f"\nBest Posting Times — {platform.upper()}")


@optimize.command("hacks")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "instagram"]))
@handle_error
def growth_hacks(platform: str) -> None:
    """Actionable growth hacks for a platform."""
    hacks = opt.get_growth_hacks(platform=platform)
    output(hacks, f"\nGrowth Hacks — {platform.upper()} ({len(hacks)} hacks)")


@optimize.command("calendar")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--posts-per-week", default=7, show_default=True)
@handle_error
def content_calendar(platform: str, posts_per_week: int) -> None:
    """Generate a 1-week content calendar."""
    calendar = opt.get_content_calendar(platform=platform, posts_per_week=posts_per_week)
    output(calendar, f"\n1-Week Content Calendar — {platform.upper()}")


# ── Theme Pages command ───────────────────────────────────────────────────────

@cli.command("theme-pages")
@click.option("--section", default="all",
              type=click.Choice([
                  "all", "concept", "niches", "steps",
                  "sourcing", "converting", "funnel",
              ]),
              help="Which section of the guide to show")
@handle_error
def theme_pages(section: str) -> None:
    """Complete theme page guide: create, grow, and convert followers to revenue."""
    guide = opt.get_theme_page_guide()

    if section == "all":
        output(guide, "\nTheme Page Mastery Guide")
    elif section == "concept":
        output({"concept": guide["concept"]}, "\nWhat is a Theme Page?")
    elif section == "niches":
        output(guide["profitable_niches"], "\nMost Profitable Theme Page Niches")
    elif section == "steps":
        output(guide["step_by_step"], "\nStep-by-Step: Build Your Theme Page")
    elif section == "sourcing":
        output(guide["content_sourcing"], "\nFree Content Sources + Tools")
    elif section == "converting":
        converting = guide["converting_theme_pages"]
        output(converting, "\nConverting Theme Pages: Tactics + Strategy")
    elif section == "funnel":
        output(guide["converting_theme_pages"]["funnel_blueprint"], "\nConversion Funnel Blueprint")


# ── Quick commands ────────────────────────────────────────────────────────────

@cli.command("viral")
@click.option("--type", "fmt", default="all",
              type=click.Choice(["all", "hook", "structure", "cta"]))
def viral(fmt: str) -> None:
    """Shortcut: show viral content formulas."""
    formulas = ta.get_viral_formula(format_type=fmt)
    output(formulas, f"\nViral Formulas — {fmt.upper()}")


@cli.command("hacks")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "instagram"]))
def hacks(platform: str) -> None:
    """Shortcut: show growth hacks for a platform."""
    result = opt.get_growth_hacks(platform=platform)
    output(result, f"\nGrowth Hacks — {platform.upper()}")


# ── REPL ───────────────────────────────────────────────────────────────────────

_REPL_HELP = """
Social Trends REPL — type a command or 'help' to see all commands.

Commands:
  youtube trending [--category all|music|gaming] [--limit N]
  youtube hashtags [--limit N]
  youtube music [--limit N]
  youtube keywords [--limit N]
  tiktok hashtags [--limit N] [--category NAME]
  tiktok sounds [--limit N]
  tiktok effects [--limit N]
  tiktok niche NICHE [--limit N]
  analyze cross-platform [--limit N]
  analyze ideas NICHE [--count N]
  analyze viral-formulas [--type all|hook|structure|cta]
  optimize checklist [--platform all|tiktok|youtube|instagram]
  optimize posting-times [--platform ...]
  optimize hacks [--platform tiktok|youtube|instagram]
  optimize calendar [--platform ...] [--posts-per-week N]
  theme-pages [--section all|concept|niches|steps|sourcing|converting|funnel]
  viral [--type all|hook|structure|cta]
  hacks [--platform tiktok|youtube|instagram]
  json on|off
  quit
"""


def _run_repl() -> None:
    global _json_output
    click.echo("\nSocial Trends REPL — type 'help' for commands, 'quit' to exit\n")
    while True:
        try:
            raw = input("social-trends> ").strip()
        except (EOFError, KeyboardInterrupt):
            click.echo("\nBye!")
            break
        if not raw:
            continue
        if raw.lower() in ("quit", "exit", "q"):
            click.echo("Bye!")
            break
        if raw.lower() == "help":
            click.echo(_REPL_HELP)
            continue
        if raw.lower() == "json on":
            _json_output = True
            click.echo("JSON output enabled")
            continue
        if raw.lower() == "json off":
            _json_output = False
            click.echo("JSON output disabled")
            continue
        try:
            args = shlex.split(raw)
            standalone = cli.make_context("social-trends", args, standalone_mode=False)
            cli.invoke(standalone)
        except click.exceptions.Exit:
            pass
        except click.exceptions.UsageError as e:
            click.echo(f"Usage error: {e}", err=True)
        except SystemExit:
            pass
        except Exception as e:
            click.echo(f"Error: {e}", err=True)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
