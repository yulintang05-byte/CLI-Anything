#!/usr/bin/env python3
"""Social Media Intelligence & Automation CLI.

Scrape YouTube & TikTok for viral trends, hashtags, and music.
Optimize your accounts. Build and convert theme pages.

Usage:
    # Scrape viral trends (YouTube + TikTok)
    cli-anything-social trends scrape --niche fitness --region US

    # Get trending hashtags
    cli-anything-social hashtags generate --niche fitness --platform instagram

    # Get trending music/sounds
    cli-anything-social music trending --platform tiktok

    # Audit an account
    cli-anything-social account audit --platform tiktok --handle @myhandle

    # Theme page guide
    cli-anything-social theme guide

    # Content calendar
    cli-anything-social theme calendar --niche finance --days 30

    # Schedule a post
    cli-anything-social schedule add --platform tiktok --time "2024-06-20T18:00:00"

    # Interactive REPL
    cli-anything-social
"""

import sys
import os
import json
from pathlib import Path
from typing import Optional

import click

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_media.utils.youtube_backend import YouTubeBackend
from cli_anything.social_media.utils.tiktok_backend import TikTokBackend
from cli_anything.social_media.core import trends as trends_mod
from cli_anything.social_media.core import hashtags as hashtags_mod
from cli_anything.social_media.core import music as music_mod
from cli_anything.social_media.core import theme_page as theme_mod
from cli_anything.social_media.core import account_optimizer as acct_mod
from cli_anything.social_media.core import scheduler as sched_mod

# Global flags
_json_output = False
_yt_backend: YouTubeBackend | None = None
_tt_backend: TikTokBackend | None = None


def _yt() -> YouTubeBackend:
    global _yt_backend
    if _yt_backend is None:
        _yt_backend = YouTubeBackend()
    return _yt_backend


def _tt() -> TikTokBackend:
    global _tt_backend
    if _tt_backend is None:
        _tt_backend = TikTokBackend()
    return _tt_backend


def output(data: object, message: str = "") -> None:
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


def _print_dict(d: dict, indent: int = 0) -> None:
    prefix = "  " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{prefix}{click.style(str(k), fg='cyan')}: ")
            _print_dict(v, indent + 1)
        elif isinstance(v, list):
            click.echo(f"{prefix}{click.style(str(k), fg='cyan')}:")
            _print_list(v, indent + 1)
        else:
            click.echo(f"{prefix}{click.style(str(k), fg='cyan')}: {v}")


def _print_list(lst: list, indent: int = 0) -> None:
    prefix = "  " * indent
    for item in lst:
        if isinstance(item, dict):
            click.echo(f"{prefix}{click.style('•', fg='yellow')} ")
            _print_dict(item, indent + 1)
        else:
            click.echo(f"{prefix}{click.style('•', fg='yellow')} {item}")


# ── Root command group ────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "json_flag", is_flag=True, help="Output JSON instead of human-readable text.")
@click.pass_context
def main(ctx: click.Context, json_flag: bool) -> None:
    """Social Media Intelligence & Automation — powered by cli-anything."""
    global _json_output
    _json_output = json_flag

    if ctx.invoked_subcommand is None:
        _run_repl()


def _run_repl() -> None:
    """Launch the interactive REPL."""
    try:
        from cli_anything.social_media.utils.repl_skin import ReplSkin
        skin = ReplSkin("social_media", version="1.0.0")
    except ImportError:
        skin = None

    if skin:
        skin.print_banner()
    else:
        click.echo("cli-anything · Social Media  v1.0.0")
        click.echo("Type 'help' for commands, 'quit' to exit.\n")

    pt_session = skin.create_prompt_session() if skin else None

    while True:
        try:
            if skin:
                raw = skin.get_input(pt_session)
            else:
                raw = input("social_media ❯ ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not raw:
            continue
        if raw.lower() in ("quit", "exit", "q"):
            break
        if raw.lower() == "help":
            _print_repl_help(skin)
            continue

        # Forward to CLI parser
        try:
            args = raw.split()
            main.main(args, standalone_mode=False)
        except SystemExit:
            pass
        except Exception as e:
            if skin:
                skin.error(str(e))
            else:
                click.echo(f"Error: {e}", err=True)

    if skin:
        skin.print_goodbye()


def _print_repl_help(skin) -> None:
    commands = {
        "trends scrape":         "Scrape YouTube + TikTok for viral trends",
        "trends show":           "Show last trend report",
        "hashtags generate":     "Generate optimal hashtag set",
        "hashtags analyze":      "Analyze an existing hashtag set",
        "music trending":        "Get trending music + sounds",
        "account add":           "Add/update an account profile",
        "account audit":         "Full account audit with recommendations",
        "account list":          "List all tracked accounts",
        "theme guide":           "Complete theme page creation guide",
        "theme niches":          "Suggest niches based on your interests",
        "theme calendar":        "Generate a content calendar",
        "theme monetize":        "Monetization roadmap for your niche",
        "schedule add":          "Schedule a post",
        "schedule list":         "List upcoming scheduled posts",
        "schedule export":       "Export schedule to CSV/JSON",
        "auth youtube":          "Configure YouTube API key",
        "quit":                  "Exit",
    }
    if skin:
        skin.help(commands)
    else:
        for cmd, desc in commands.items():
            click.echo(f"  {cmd:<24} {desc}")


# ── auth ──────────────────────────────────────────────────────────────────────

@main.group()
def auth() -> None:
    """Configure API keys and credentials."""


@auth.command()
@click.option("--api-key", required=True, help="YouTube Data API v3 key.")
def youtube(api_key: str) -> None:
    """Save YouTube Data API key."""
    _yt().save_key(api_key)
    click.echo(click.style("✓ YouTube API key saved.", fg="green"))
    click.echo("Get a free key at: https://console.cloud.google.com/apis/library/youtube.googleapis.com")


# ── trends ────────────────────────────────────────────────────────────────────

@main.group()
def trends() -> None:
    """Scrape and analyze viral trends from YouTube & TikTok."""


@trends.command()
@click.option("--niche",    default="all", show_default=True, help="Content niche (e.g. fitness, finance, all).")
@click.option("--region",   default="US",  show_default=True, help="Region code (US, GB, AU…).")
@click.option("--max",      default=25,    show_default=True, help="Max items per platform.")
@click.option("--save",     is_flag=True,  help="Save report to disk.")
@click.option("--no-cache", is_flag=True,  help="Bypass cached results.")
def scrape(niche: str, region: str, max: int, save: bool, no_cache: bool) -> None:
    """Scrape YouTube + TikTok for viral trends, hashtags, and music."""
    click.echo(click.style(f"Scraping trends — niche: {niche}, region: {region}…", fg="cyan"))

    yt = _yt()
    tt = _tt()

    click.echo("  Fetching YouTube trending videos…")
    yt_videos = yt.get_trending_videos(region=region, category=niche, max_results=max)

    click.echo("  Fetching YouTube trending hashtags…")
    yt_hashtags = yt.get_trending_hashtags(region=region, category=niche, top_n=30)

    click.echo("  Fetching YouTube trending music…")
    yt_music = yt.get_trending_music(region=region, max_results=max)

    click.echo("  Fetching TikTok trending hashtags…")
    tt_hashtags = tt.get_trending_hashtags(category=niche, region=region, top_n=30)

    click.echo("  Fetching TikTok trending sounds…")
    tt_sounds = tt.get_trending_sounds(region=region, top_n=20)

    click.echo("  Fetching TikTok trending videos…")
    tt_videos = tt.get_trending_videos(region=region, category=niche, top_n=20)

    report = trends_mod.aggregate_trends(
        yt_videos=yt_videos,
        yt_hashtags=yt_hashtags,
        yt_music=yt_music,
        tt_hashtags=tt_hashtags,
        tt_sounds=tt_sounds,
        tt_videos=tt_videos,
    )

    if save:
        path = trends_mod.save_report(report, name=f"trend_{niche}_{region}")
        click.echo(click.style(f"\n✓ Report saved to {path}", fg="green"))

    output(report, f"\n=== Trend Report: {niche.upper()} / {region} ===")


@trends.command()
def show() -> None:
    """Display the most recent saved trend report."""
    report = trends_mod.load_last_report()
    if not report:
        click.echo(click.style("No saved reports found. Run: trends scrape --save", fg="yellow"))
        return
    output(report, f"=== Last Trend Report ({report.get('generated_at', '')}) ===")


@trends.command()
def diff() -> None:
    """Compare two most recent trend reports to see what changed."""
    from pathlib import Path
    reports_path = Path.home() / ".cli-anything-social" / "trend_reports"
    if not reports_path.exists():
        click.echo("No reports found.")
        return
    reports = sorted(reports_path.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if len(reports) < 2:
        click.echo("Need at least 2 saved reports to diff. Run: trends scrape --save")
        return
    old = json.loads(reports[1].read_text())
    new = json.loads(reports[0].read_text())
    delta = trends_mod.diff_reports(old, new)
    output(delta, "=== Trend Diff ===")


# ── hashtags ──────────────────────────────────────────────────────────────────

@main.group()
def hashtags() -> None:
    """Hashtag strategy — generate, analyze, and score hashtag sets."""


@hashtags.command()
@click.option("--niche",    required=True, help="Content niche.")
@click.option("--platform", default="instagram", show_default=True,
              type=click.Choice(["instagram", "tiktok", "youtube", "twitter"]),
              help="Target platform.")
@click.option("--custom",   multiple=True, help="Add custom hashtags.")
@click.option("--no-general", is_flag=True, help="Skip general growth hashtags.")
def generate(niche: str, platform: str, custom: tuple, no_general: bool) -> None:
    """Generate an optimized hashtag set for a post."""
    result = hashtags_mod.generate_hashtag_set(
        niche=niche,
        platform=platform,
        custom_tags=list(custom) if custom else None,
        include_general=not no_general,
    )
    if _json_output:
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(click.style(f"\n=== Hashtag Set: {niche} / {platform} ===", fg="cyan"))
        for tier, tags in result["by_tier"].items():
            if tags:
                click.echo(f"\n  {click.style(tier.upper(), fg='yellow')} ({len(tags)} tags):")
                click.echo("  " + " ".join(tags))
        click.echo(f"\n  Total: {result['count']} hashtags")
        click.echo(click.style("\n  Copy-paste ready:", fg="green"))
        click.echo(f"  {result['copy_paste']}")


@hashtags.command()
@click.argument("tags", nargs=-1)
@click.option("--niche", default="general", help="Niche for benchmarking.")
def analyze(tags: tuple, niche: str) -> None:
    """Analyze an existing hashtag set.

    Example: hashtags analyze #fitness #gym #workout --niche fitness
    """
    if not tags:
        click.echo("Provide hashtags to analyze. Example: hashtags analyze #fitness #gym")
        return
    result = hashtags_mod.analyze_hashtag_set(list(tags), niche=niche)
    output(result, "=== Hashtag Analysis ===")


@hashtags.command()
def niches() -> None:
    """List all available niche presets."""
    available = hashtags_mod.available_niches()
    click.echo("Available niches:")
    for n in available:
        click.echo(f"  • {n}")


# ── music ─────────────────────────────────────────────────────────────────────

@main.group()
def music() -> None:
    """Track trending music on TikTok and YouTube."""


@music.command()
@click.option("--platform", default="both", type=click.Choice(["tiktok", "youtube", "both"]),
              show_default=True)
@click.option("--content-type", "content_type", default="general",
              help="Your content type (dance, motivation, comedy, lifestyle, food, fitness).")
@click.option("--region", default="US", show_default=True)
@click.option("--save", is_flag=True)
def trending(platform: str, content_type: str, region: str, save: bool) -> None:
    """Show trending music and sounds with creator strategy tips."""
    yt_music = []
    tt_sounds = []

    if platform in ("youtube", "both"):
        click.echo("  Fetching YouTube trending music…")
        yt_music = _yt().get_trending_music(region=region, max_results=20)

    if platform in ("tiktok", "both"):
        click.echo("  Fetching TikTok trending sounds…")
        tt_sounds = _tt().get_trending_sounds(region=region, top_n=20)

    report = music_mod.format_music_report(yt_music, tt_sounds, content_type=content_type)

    if save:
        path = music_mod.save_music_report(report)
        click.echo(click.style(f"✓ Music report saved to {path}", fg="green"))

    output(report, "=== Trending Music & Sounds ===")


@music.command()
def content_types() -> None:
    """List sound strategy content types."""
    types = music_mod.available_content_types()
    click.echo("Available content types for sound strategy:")
    for t in types:
        click.echo(f"  • {t}")


# ── account ───────────────────────────────────────────────────────────────────

@main.group()
def account() -> None:
    """Manage and optimize your social media accounts."""


@account.command()
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]))
@click.option("--handle",     required=True, help="Account handle (without @).")
@click.option("--niche",      default="general", show_default=True)
@click.option("--followers",  default=0, type=int)
@click.option("--following",  default=0, type=int)
@click.option("--posts",      default=0, type=int)
@click.option("--avg-likes",  default=0.0, type=float)
@click.option("--avg-comments", default=0.0, type=float)
@click.option("--avg-views",  default=0.0, type=float)
@click.option("--bio",        default="")
@click.option("--link",       default="", help="Link in bio.")
@click.option("--freq",       default=1.0, type=float, help="Posts per day.")
@click.option("--timezone",   default="US/Eastern", show_default=True)
def add(
    platform: str, handle: str, niche: str, followers: int, following: int,
    posts: int, avg_likes: float, avg_comments: float, avg_views: float,
    bio: str, link: str, freq: float, timezone: str,
) -> None:
    """Add or update an account profile."""
    profile = acct_mod.AccountProfile(
        platform=platform, handle=handle, niche=niche,
        followers=followers, following=following, posts=posts,
        avg_likes=avg_likes, avg_comments=avg_comments, avg_views=avg_views,
        bio=bio, link_in_bio=link, posting_frequency=freq, timezone=timezone,
    )
    path = acct_mod.save_profile(profile)
    click.echo(click.style(f"✓ Account @{handle} ({platform}) saved.", fg="green"))
    click.echo(f"  Profile stored at: {path}")


@account.command()
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]))
@click.option("--handle", required=True, help="Account handle (without @).")
def audit(platform: str, handle: str) -> None:
    """Run a full account audit with recommendations."""
    profile = acct_mod.load_profile(platform, handle)
    if not profile:
        click.echo(click.style(
            f"Account @{handle} on {platform} not found. Run: account add --platform {platform} --handle {handle}",
            fg="yellow",
        ))
        return
    result = acct_mod.full_account_audit(profile)
    output(result, f"=== Account Audit: @{handle} ({platform}) ===")


@account.command("list")
def list_accounts() -> None:
    """List all tracked accounts."""
    profiles = acct_mod.list_profiles()
    if not profiles:
        click.echo("No accounts tracked yet. Run: account add")
        return
    if _json_output:
        click.echo(json.dumps(profiles, indent=2))
    else:
        click.echo(click.style("Tracked accounts:", fg="cyan"))
        for p in profiles:
            click.echo(
                f"  • {click.style(p['platform'], fg='yellow')} "
                f"@{p['handle']} — {p['niche']} — "
                f"{p['followers']:,} followers"
            )


@account.command()
@click.option("--platform", required=True, type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]))
@click.option("--handle", required=True)
@click.option("--posts-per-week", "ppw", default=7, type=int, show_default=True)
def schedule_optimize(platform: str, handle: str, ppw: int) -> None:
    """Get optimal posting schedule for an account."""
    profile = acct_mod.load_profile(platform, handle)
    niche = profile.niche if profile else "general"
    tz = profile.timezone if profile else "US/Eastern"
    result = acct_mod.optimize_posting_schedule(
        platform=platform, niche=niche, posts_per_week=ppw, timezone_str=tz,
    )
    output(result, f"=== Optimal Posting Schedule: {platform} ===")


@account.command()
@click.option("--bio",       required=True, help="Your current bio text.")
@click.option("--platform",  required=True, type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]))
@click.option("--niche",     default="general")
def analyze_bio(bio: str, platform: str, niche: str) -> None:
    """Score and get suggestions for improving your bio."""
    result = acct_mod.analyze_bio(bio, platform, niche)
    output(result, "=== Bio Analysis ===")


@account.command()
@click.option("--followers",  required=True, type=int)
@click.option("--avg-likes",  required=True, type=float)
@click.option("--avg-comments", default=0.0, type=float)
@click.option("--avg-views",  default=0.0, type=float)
@click.option("--platform",   default="instagram",
              type=click.Choice(["instagram", "tiktok", "youtube"]))
def engagement(followers: int, avg_likes: float, avg_comments: float, avg_views: float, platform: str) -> None:
    """Calculate and benchmark your engagement rate."""
    result = acct_mod.engagement_rate_analysis(
        followers=followers, avg_likes=avg_likes, avg_comments=avg_comments,
        avg_views=avg_views, platform=platform,
    )
    output(result, "=== Engagement Rate Analysis ===")


# ── theme ─────────────────────────────────────────────────────────────────────

@main.group()
def theme() -> None:
    """Theme page strategy — creation, growth, and monetization."""


@theme.command()
def guide() -> None:
    """Complete guide to creating and converting a theme page."""
    result = theme_mod.theme_page_guide()
    if _json_output:
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(click.style("\n=== Theme Page Complete Guide ===\n", fg="cyan", bold=True))
        click.echo(result["overview"])
        click.echo()
        for phase in result["phases"]:
            click.echo(click.style(f"\n  {phase['phase']}", fg="yellow", bold=True))
            for action in phase["actions"]:
                click.echo(f"    • {action}")

        click.echo(click.style("\n\n  MONETIZATION METHODS", fg="cyan", bold=True))
        for method in result["monetization_methods"]:
            click.echo(click.style(f"\n    {method['method']}", fg="green"))
            click.echo(f"      Income: {method['income_potential']}")
            click.echo(f"      When:   {method['when']}")
            click.echo(f"      How:    {method['how']}")

        click.echo(click.style("\n\n  CONTENT SOURCING", fg="cyan", bold=True))
        for src in result["content_sourcing"]["repost_sources"]:
            click.echo(f"    • {src}")
        click.echo(click.style("\n  Tools:", fg="yellow"))
        for tool in result["content_sourcing"]["tools"]:
            click.echo(f"    • {tool}")

        click.echo(click.style("\n\n  CONVERSION CHECKLIST", fg="cyan", bold=True))
        for item in result["conversion_checklist"]:
            click.echo(f"    ☐ {item}")
        click.echo()


@theme.command()
@click.option("--interests", multiple=True, default=[], help="Your interests (can specify multiple).")
@click.option("--monetization/--no-monetization", default=True,
              help="Prioritize high-monetization niches.")
@click.option("--top", default=5, type=int, show_default=True)
def niches(interests: tuple, monetization: bool, top: int) -> None:
    """Get niche recommendations based on your interests."""
    result = theme_mod.suggest_niches(
        interests=list(interests),
        monetization_priority=monetization,
        max_suggestions=top,
    )
    if _json_output:
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(click.style("\n=== Niche Suggestions ===\n", fg="cyan"))
        for i, n in enumerate(result, 1):
            click.echo(click.style(f"  #{i} {n['niche'].upper()}", fg="yellow", bold=True))
            click.echo(f"     Monetization: {n['monetization']}  |  Difficulty: {n['difficulty']}")
            click.echo(f"     Growth rate:  {n['monthly_growth_rate']}/month")
            click.echo(f"     Shoutout @10K: {n['shoutout_at_10k']}  |  @100K: {n['shoutout_at_100k']}")
            click.echo(f"     Sub-niches:   {', '.join(n['sub_niches'])}")
            click.echo()


@theme.command()
@click.option("--niche", required=True, help="Your chosen niche.")
@click.option("--days",  default=30, show_default=True, type=int)
@click.option("--tiktok-daily",  default=3, type=int, show_default=True)
@click.option("--ig-daily",      default=1, type=int, show_default=True)
@click.option("--yt-weekly",     default=1, type=int, show_default=True)
@click.option("--save", is_flag=True)
def calendar(niche: str, days: int, tiktok_daily: int, ig_daily: int, yt_weekly: int, save: bool) -> None:
    """Generate a content posting calendar."""
    posts_per_day = {
        "tiktok": tiktok_daily,
        "instagram": ig_daily,
        "youtube": max(1, yt_weekly // 7),
    }
    cal = theme_mod.generate_content_calendar(niche=niche, days=days, posts_per_day=posts_per_day)

    if save:
        from pathlib import Path
        out = Path.home() / ".cli-anything-social" / f"calendar_{niche}_{days}d.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(cal, indent=2))
        click.echo(click.style(f"✓ Calendar saved to {out}", fg="green"))

    if _json_output:
        click.echo(json.dumps(cal, indent=2))
    else:
        click.echo(click.style(f"\n=== {days}-Day Content Calendar: {niche} ===\n", fg="cyan"))
        for day_entry in cal[:7]:  # show first week
            click.echo(click.style(f"  {day_entry['date']} ({day_entry['day']})", fg="yellow"))
            for post in day_entry["posts"]:
                click.echo(
                    f"    • {post['platform']:<12} {post['posting_time']:<10} "
                    f"[{post['content_type']}] {post['example']}"
                )
        if days > 7:
            click.echo(f"\n  ... and {days - 7} more days. Use --save to export full calendar.")


@theme.command()
@click.option("--niche",     required=True)
@click.option("--followers", default=0, type=int, show_default=True)
def monetize(niche: str, followers: int) -> None:
    """Get your monetization roadmap based on current follower count."""
    result = theme_mod.monetization_roadmap(niche=niche, follower_count=followers)
    if _json_output:
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(click.style(f"\n=== Monetization Roadmap: {niche} ({followers:,} followers) ===\n", fg="cyan"))
        for phase in result["phases"]:
            status_color = "green" if phase["status"] == "current" else "blue" if phase["status"] == "upcoming" else "white"
            click.echo(click.style(f"  {phase['phase']}", fg=status_color, bold=True))
            click.echo(f"  Revenue potential: {phase['revenue_potential']}")
            click.echo(f"  Timeline: {phase['timeline']}")
            click.echo(f"  Focus: {phase['focus']}")
            for action in phase["actions"]:
                click.echo(f"    • {action}")
            click.echo()

        click.echo(click.style("  AFFILIATE PROGRAMS FOR YOUR NICHE", fg="yellow"))
        for prog in result["affiliate_programs"]:
            click.echo(f"    • {prog['name']}: {prog['commission']} (cookie: {prog['cookie']})")

        click.echo(click.style("\n  BRAND OUTREACH EMAIL TEMPLATE", fg="yellow"))
        click.echo(result["brand_outreach_template"])


# ── schedule ──────────────────────────────────────────────────────────────────

@main.group()
def schedule() -> None:
    """Content scheduling — plan and track your posts."""


@schedule.command()
@click.option("--platform",      required=True,
              type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]))
@click.option("--time",          "scheduled_time", required=True,
              help="ISO 8601 datetime, e.g. 2024-06-20T18:00:00")
@click.option("--caption",       default="",   help="Post caption.")
@click.option("--content-type",  default="video",
              type=click.Choice(["video", "reel", "story", "tweet", "short", "carousel"]))
@click.option("--hashtags",      multiple=True)
@click.option("--niche",         default="")
@click.option("--media",         default="",   help="Path to media file.")
@click.option("--audio",         default="",   help="Trending audio name/URL.")
@click.option("--notes",         default="")
def add(
    platform: str, scheduled_time: str, caption: str, content_type: str,
    hashtags: tuple, niche: str, media: str, audio: str, notes: str,
) -> None:
    """Schedule a post."""
    post = sched_mod.add_post(
        platform=platform, content_type=content_type, caption=caption,
        scheduled_time=scheduled_time, hashtags=list(hashtags),
        niche=niche, media_path=media, trending_audio=audio, notes=notes,
    )
    click.echo(click.style(f"✓ Post scheduled (ID: {post.id})", fg="green"))
    click.echo(f"  Platform: {post.platform}")
    click.echo(f"  Time:     {post.scheduled_time}")
    click.echo(f"  Type:     {post.content_type}")


@schedule.command("list")
@click.option("--platform", default=None)
@click.option("--status",   default="scheduled",
              type=click.Choice(["scheduled", "posted", "cancelled", "all"]))
@click.option("--days",     default=7, type=int, show_default=True)
def list_schedule(platform: Optional[str], status: str, days: int) -> None:
    """List scheduled posts."""
    from datetime import timedelta, timezone as tz
    now = __import__("datetime").datetime.now(tz.utc).isoformat()
    cutoff = (__import__("datetime").datetime.now(tz.utc) + timedelta(days=days)).isoformat()
    posts = sched_mod.list_posts(
        platform=platform,
        status=None if status == "all" else status,
        after=now,
        before=cutoff,
    )
    if not posts:
        click.echo(f"No {status} posts in the next {days} days.")
        return
    if _json_output:
        click.echo(json.dumps([__import__("dataclasses").asdict(p) for p in posts], indent=2))
        return
    click.echo(click.style(f"\nScheduled posts (next {days} days):\n", fg="cyan"))
    for p in posts:
        click.echo(
            f"  {click.style(p.id, fg='yellow')}  "
            f"{p.platform:<12}  {p.scheduled_time[:16]}  "
            f"[{p.content_type}]  {p.caption[:40] or '(no caption)'}"
        )


@schedule.command()
@click.argument("post_id")
def cancel(post_id: str) -> None:
    """Cancel a scheduled post."""
    ok = sched_mod.cancel_post(post_id)
    if ok:
        click.echo(click.style(f"✓ Post {post_id} cancelled.", fg="green"))
    else:
        click.echo(click.style(f"Post {post_id} not found.", fg="red"))


@schedule.command()
@click.argument("post_id")
def mark_done(post_id: str) -> None:
    """Mark a scheduled post as posted."""
    ok = sched_mod.mark_posted(post_id)
    if ok:
        click.echo(click.style(f"✓ Post {post_id} marked as posted.", fg="green"))
    else:
        click.echo(click.style(f"Post {post_id} not found.", fg="red"))


@schedule.command()
@click.option("--format", "fmt", default="csv",
              type=click.Choice(["csv", "json"]), show_default=True)
@click.option("--out", "out_path", default=None, help="Output file path.")
def export(fmt: str, out_path: Optional[str]) -> None:
    """Export full schedule to CSV or JSON."""
    path = __import__("pathlib").Path(out_path) if out_path else None
    if fmt == "csv":
        out = sched_mod.export_schedule_csv(path)
    else:
        out = sched_mod.export_schedule_json(path)
    click.echo(click.style(f"✓ Schedule exported to {out}", fg="green"))


@schedule.command()
def summary() -> None:
    """Show schedule summary stats."""
    result = sched_mod.summary()
    output(result, "=== Schedule Summary ===")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
