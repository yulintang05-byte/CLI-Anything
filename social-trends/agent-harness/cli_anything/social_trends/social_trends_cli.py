#!/usr/bin/env python3
"""CLI-Anything Social Trends — scrape YouTube & TikTok viral trends,
hashtags, and music; optimize accounts; and build theme pages.

Usage:
    # Setup
    cli-anything-social-trends config set-youtube-key <KEY>
    cli-anything-social-trends account add --platform tiktok --handle @mypage --niche fitness

    # Fetch trends
    cli-anything-social-trends trends fetch youtube
    cli-anything-social-trends trends fetch tiktok --type hashtags
    cli-anything-social-trends trends fetch tiktok --type music
    cli-anything-social-trends trends fetch all

    # Optimize accounts
    cli-anything-social-trends account optimize --platform tiktok

    # Theme pages
    cli-anything-social-trends themes guide
    cli-anything-social-trends themes list-niches
    cli-anything-social-trends themes playbook

    # Interactive REPL
    cli-anything-social-trends
"""

import sys
import os
import json
from datetime import datetime
from typing import Optional

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style as PtkStyle

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_trends.core import config as cfg_mod
from cli_anything.social_trends.core import youtube as yt_mod
from cli_anything.social_trends.core import tiktok as tt_mod
from cli_anything.social_trends.core import optimizer as opt_mod
from cli_anything.social_trends.core import theme_pages as theme_mod

_json_output = False
_repl_mode = False


# ── Output helpers ────────────────────────────────────────────────

ACCENT = "\033[38;5;208m"  # orange
BOLD   = "\033[1m"
RESET  = "\033[0m"
GREEN  = "\033[32m"
RED    = "\033[31m"
BLUE   = "\033[34m"
YELLOW = "\033[33m"
CYAN   = "\033[36m"
DIM    = "\033[2m"


def _banner():
    click.echo(f"""
{ACCENT}{BOLD}╔══════════════════════════════════════════════════════╗
║   CLI-Anything Social Trends  v1.0.0                 ║
║   YouTube & TikTok viral trends, hashtags & music    ║
╚══════════════════════════════════════════════════════╝{RESET}
""")


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
        elif data is not None:
            click.echo(str(data))


def _print_dict(d: dict, indent: int = 0):
    prefix = "  " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{prefix}{CYAN}{k}{RESET}:")
            _print_dict(v, indent + 1)
        elif isinstance(v, list):
            click.echo(f"{prefix}{CYAN}{k}{RESET}:")
            _print_list(v, indent + 1)
        else:
            click.echo(f"{prefix}{CYAN}{k}{RESET}: {v}")


def _print_list(items: list, indent: int = 0):
    prefix = "  " * indent
    for i, item in enumerate(items):
        if isinstance(item, dict):
            click.echo(f"{prefix}{DIM}[{i+1}]{RESET}")
            _print_dict(item, indent + 1)
        else:
            click.echo(f"{prefix}{GREEN}•{RESET} {item}")


def ok(msg: str):
    click.echo(f"  {GREEN}✓{RESET} {msg}")


def err(msg: str):
    click.echo(f"  {RED}✗{RESET} {msg}", err=True)


def info(msg: str):
    click.echo(f"  {BLUE}ℹ{RESET} {msg}")


def warn(msg: str):
    click.echo(f"  {YELLOW}⚠{RESET} {msg}")


def section(title: str):
    click.echo(f"\n{BOLD}{ACCENT}── {title} ──{RESET}\n")


def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                err(str(e))
            if not _repl_mode:
                sys.exit(1)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# ── Main CLI Group ────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx, use_json):
    """CLI-Anything Social Trends — YouTube & TikTok viral intelligence.

    Run without a subcommand to enter interactive REPL mode.
    """
    global _json_output
    _json_output = use_json
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── Config commands ───────────────────────────────────────────────

@cli.group()
def config():
    """Manage API keys and settings."""


@config.command("set-youtube-key")
@click.argument("api_key")
def config_set_yt_key(api_key: str):
    """Store YouTube Data API v3 key."""
    cfg_mod.set_youtube_api_key(api_key)
    ok(f"YouTube API key saved to {cfg_mod.CONFIG_FILE}")


@config.command("set-tiktok-token")
@click.argument("ms_token")
def config_set_tt_token(ms_token: str):
    """Store TikTok msToken cookie (optional, improves rate limits)."""
    cfg_mod.set_tiktok_ms_token(ms_token)
    ok(f"TikTok msToken saved to {cfg_mod.CONFIG_FILE}")


@config.command("show")
def config_show():
    """Show current configuration (keys redacted)."""
    cfg = cfg_mod.load_config()
    display = {}
    for k, v in cfg.items():
        display[k] = v[:8] + "..." if isinstance(v, str) and len(v) > 8 else v
    output(display, "Current configuration:")


# ── Account commands ──────────────────────────────────────────────

@cli.group()
def account():
    """Manage your social media accounts."""


@account.command("add")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["tiktok", "instagram", "youtube"], case_sensitive=False),
              help="Platform")
@click.option("--handle", "-h", required=True, help="Account handle (e.g. @mypage)")
@click.option("--niche", "-n", default="", help="Niche (e.g. fitness, travel, finance)")
@click.option("--goal", "-g", multiple=True, help="Goals (can repeat: --goal grow --goal monetize)")
def account_add(platform: str, handle: str, niche: str, goal: tuple):
    """Add a social media account to track and optimize."""
    entry = cfg_mod.add_account(platform, handle, niche, list(goal))
    ok(f"Added @{entry['handle']} ({platform}) — niche: {niche or 'not set'}")


@account.command("list")
def account_list():
    """List all tracked accounts."""
    accounts = cfg_mod.load_accounts()
    if not accounts:
        info("No accounts added yet. Use: account add --platform tiktok --handle @mypage")
        return
    section("Tracked Accounts")
    for a in accounts:
        goals_str = ", ".join(a.get("goals", [])) or "—"
        click.echo(f"  {ACCENT}@{a['handle']}{RESET} [{a['platform']}]  niche: {a.get('niche','—')}  goals: {goals_str}")


@account.command("remove")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["tiktok", "instagram", "youtube"], case_sensitive=False))
@click.option("--handle", "-h", required=True)
def account_remove(platform: str, handle: str):
    """Remove an account from tracking."""
    removed = cfg_mod.remove_account(platform, handle)
    if removed:
        ok(f"Removed @{handle.lstrip('@')} from {platform}")
    else:
        warn(f"Account @{handle.lstrip('@')} not found on {platform}")


@account.command("optimize")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "instagram", "youtube", "all"], case_sensitive=False),
              default="all", help="Platform to optimize (default: all)")
@click.option("--country", "-c", default="US", help="Country code for trend data")
def account_optimize(platform: str, country: str):
    """Generate optimization reports for all tracked accounts."""
    accounts = cfg_mod.load_accounts()
    if not accounts:
        warn("No accounts tracked. Add one first: account add --platform tiktok --handle @you --niche fitness")
        return

    # Fetch fresh trend data to inform recommendations
    info("Fetching trending data...")
    ms_token = cfg_mod.get_tiktok_ms_token()
    tt_hashtags = []
    tt_music = []
    try:
        tt_hashtags = tt_mod.fetch_trending_hashtags(country=country, ms_token=ms_token)
        tt_music = tt_mod.fetch_trending_music(country=country, ms_token=ms_token)
    except Exception as e:
        warn(f"TikTok trend fetch partial: {e}")

    target_accounts = accounts if platform == "all" else [a for a in accounts if a["platform"] == platform]
    if not target_accounts:
        warn(f"No accounts found for platform: {platform}")
        return

    reports = []
    for acct in target_accounts:
        p = acct["platform"]
        trending_h = tt_hashtags if p == "tiktok" else []
        trending_m = tt_music if p == "tiktok" else []
        report = opt_mod.generate_account_report(acct, trending_h, trending_m)
        reports.append(report)

        if _json_output:
            continue

        section(f"@{acct['handle']} ({p.upper()}) Optimization Report")

        click.echo(f"{BOLD}Profile Checklist:{RESET}")
        for item in report["profile_checklist"]:
            click.echo(f"  {GREEN}☐{RESET} {item}")

        if report.get("hashtag_strategy"):
            click.echo(f"\n{BOLD}Hashtag Strategy:{RESET}")
            tags = report["hashtag_strategy"]
            click.echo(f"  Tags: {' '.join(tags['hashtags'])}")
            click.echo(f"  {DIM}{tags['recommendation']}{RESET}")

        click.echo(f"\n{BOLD}Content Pillars:{RESET}")
        for pillar in report["content_pillars"]:
            click.echo(f"  {ACCENT}▸{RESET} {pillar}")

        click.echo(f"\n{BOLD}Top Trending Music to Use:{RESET}")
        if report["trending_music_to_use"]:
            for m in report["trending_music_to_use"]:
                clips = f"  ({m['clip_count']:,} clips)" if m.get("clip_count") else ""
                click.echo(f"  {GREEN}♪{RESET} {m['title']} — {m['artist']}{clips}")
        else:
            info("No music data (set TikTok msToken or run: trends fetch tiktok --type music)")

        click.echo(f"\n{BOLD}7-Day Posting Schedule:{RESET}")
        for slot in report["posting_schedule"]:
            click.echo(f"  {slot['date']} ({slot['day']:<9}) → {slot['time_window']}")

        click.echo(f"\n{BOLD}Growth Tips:{RESET}")
        for tip in report["growth_tips"][:5]:
            click.echo(f"  {BLUE}→{RESET} {tip}")

    if _json_output:
        output(reports)


# ── Trends commands ───────────────────────────────────────────────

@cli.group()
def trends():
    """Fetch and analyze viral trends from YouTube and TikTok."""


@trends.command("fetch")
@click.argument("platform", type=click.Choice(["youtube", "tiktok", "all"], case_sensitive=False))
@click.option("--type", "-t", "trend_type",
              type=click.Choice(["hashtags", "music", "videos", "creators", "all"], case_sensitive=False),
              default="all", help="Type of trend data to fetch")
@click.option("--country", "-c", default="US", help="Country code (e.g. US, GB, AU)")
@click.option("--period", default=7, type=int, help="Trend period in days (7 or 30)")
@click.option("--limit", "-l", default=25, type=int, help="Number of results per category")
@click.option("--ranked", is_flag=True, default=True, help="Sort by virality score")
def trends_fetch(platform: str, trend_type: str, country: str, period: int, limit: int, ranked: bool):
    """Scrape viral trends from YouTube and/or TikTok.

    PLATFORM: youtube | tiktok | all
    """
    results = {}

    if platform in ("youtube", "all"):
        results["youtube"] = _fetch_youtube_trends(trend_type, country, limit, ranked)

    if platform in ("tiktok", "all"):
        results["tiktok"] = _fetch_tiktok_trends(trend_type, country, period, limit, ranked)

    output(results)


def _fetch_youtube_trends(trend_type: str, country: str, limit: int, ranked: bool) -> dict:
    api_key = cfg_mod.get_youtube_api_key()
    result = {}

    if not _json_output:
        section("YouTube Trends")

    if trend_type in ("videos", "all"):
        if api_key:
            try:
                videos = yt_mod.fetch_trending_videos(api_key, region=country, max_results=limit)
                if ranked:
                    videos = opt_mod.rank_trends(videos, "youtube")
                result["trending_videos"] = videos
                if not _json_output:
                    click.echo(f"{BOLD}Top Trending Videos:{RESET}")
                    for i, v in enumerate(videos[:10], 1):
                        score = f"  [{v.get('virality_score', '—')}]" if ranked else ""
                        click.echo(f"  {i:>2}. {v['title'][:55]:<55}{score}")
                        click.echo(f"      {DIM}{v['channel']}  {v.get('view_count', 0):,} views{RESET}")
            except Exception as e:
                warn(f"YouTube API error: {e}")
        else:
            # No-auth fallback
            try:
                videos = yt_mod.scrape_trending_no_auth(music_only=False, max_results=limit)
                result["trending_videos"] = videos
                if not _json_output:
                    click.echo(f"{BOLD}Trending Videos (public scrape — no API key){RESET}")
                    for i, v in enumerate(videos[:15], 1):
                        click.echo(f"  {i:>2}. {v['title'][:60]}")
                        click.echo(f"      {DIM}{v['channel']}  {v.get('views', '')}{RESET}")
            except Exception as e:
                warn(f"YouTube scrape error: {e}")
                result["trending_videos"] = []

    if trend_type in ("music", "all"):
        if api_key:
            try:
                music = yt_mod.fetch_trending_music(api_key, region=country, max_results=limit)
                if ranked:
                    music = opt_mod.rank_trends(music, "youtube")
                result["trending_music"] = music
                if not _json_output:
                    click.echo(f"\n{BOLD}Top Trending Music:{RESET}")
                    for i, v in enumerate(music[:10], 1):
                        click.echo(f"  {i:>2}. {v['title'][:55]}")
                        click.echo(f"      {DIM}{v['channel']}  {v.get('view_count', 0):,} views{RESET}")
            except Exception as e:
                warn(f"YouTube music fetch error: {e}")
        else:
            try:
                music = yt_mod.scrape_trending_no_auth(music_only=True, max_results=limit)
                result["trending_music"] = music
                if not _json_output:
                    click.echo(f"\n{BOLD}Trending Music (public scrape){RESET}")
                    for i, v in enumerate(music[:10], 1):
                        click.echo(f"  {i:>2}. {v['title'][:60]}")
                        click.echo(f"      {DIM}{v['channel']}  {v.get('views', '')}{RESET}")
            except Exception as e:
                warn(f"YouTube music scrape error: {e}")

    if trend_type in ("hashtags", "all") and api_key:
        try:
            # Extract hashtags from trending video tags/descriptions
            all_videos = result.get("trending_videos", [])
            if not all_videos:
                all_videos = yt_mod.fetch_trending_videos(api_key, region=country, max_results=50)
            hashtags = yt_mod.extract_trending_hashtags_from_titles(all_videos)
            result["trending_hashtags"] = hashtags
            if not _json_output and hashtags:
                click.echo(f"\n{BOLD}Trending Hashtags from Video Tags:{RESET}")
                for h in hashtags[:15]:
                    click.echo(f"  {GREEN}#{h['hashtag'].lstrip('#')}{RESET}  ({h['count']} videos)")
        except Exception as e:
            warn(f"Hashtag extraction error: {e}")

    if not api_key and not _json_output:
        info("Tip: Set a YouTube API key for richer data — cli-anything-social-trends config set-youtube-key <KEY>")
        info("Get a free key at: console.cloud.google.com → YouTube Data API v3")

    return result


def _fetch_tiktok_trends(trend_type: str, country: str, period: int, limit: int, ranked: bool) -> dict:
    ms_token = cfg_mod.get_tiktok_ms_token()
    result = {}

    if not _json_output:
        section("TikTok Trends")

    if trend_type in ("hashtags", "all"):
        try:
            hashtags = tt_mod.fetch_trending_hashtags(country=country, period=period, limit=limit, ms_token=ms_token)
            if ranked:
                hashtags = opt_mod.rank_trends(hashtags, "tiktok")
            result["trending_hashtags"] = hashtags
            if not _json_output:
                click.echo(f"{BOLD}Trending Hashtags:{RESET}")
                for i, h in enumerate(hashtags[:20], 1):
                    views = f"{h.get('view_count', 0):,}" if h.get('view_count') else "—"
                    score = f"  score: {h.get('virality_score', '—')}" if ranked else ""
                    click.echo(f"  {i:>2}. {GREEN}{h['hashtag']:<30}{RESET}  {views} views{score}")
        except Exception as e:
            warn(f"TikTok hashtag fetch error: {e}")

    if trend_type in ("music", "all"):
        try:
            music = tt_mod.fetch_trending_music(country=country, period=period, limit=limit, ms_token=ms_token)
            if ranked:
                music = opt_mod.rank_trends(music, "tiktok")
            result["trending_music"] = music
            if not _json_output:
                click.echo(f"\n{BOLD}Trending Songs:{RESET}")
                for i, m in enumerate(music[:15], 1):
                    clips = f"{m.get('clip_count', 0):,} clips" if m.get("clip_count") else ""
                    click.echo(f"  {i:>2}. {GREEN}♪{RESET} {m.get('title', ''):<35}  {m.get('artist', ''):<20}  {clips}")
        except Exception as e:
            warn(f"TikTok music fetch error: {e}")

    if trend_type in ("videos", "all"):
        try:
            videos = tt_mod.fetch_trending_videos(country=country, period=period, limit=min(limit, 20), ms_token=ms_token)
            if ranked:
                videos = opt_mod.rank_trends(videos, "tiktok")
            result["trending_videos"] = videos
            if not _json_output:
                click.echo(f"\n{BOLD}Trending Videos:{RESET}")
                for i, v in enumerate(videos[:10], 1):
                    tags = ", ".join(f"#{t}" for t in v.get("hashtags", [])[:3])
                    click.echo(f"  {i:>2}. @{v.get('author', ''):<20}  plays: {v.get('play_count', 0):,}")
                    if tags:
                        click.echo(f"      {DIM}{tags}{RESET}")
        except Exception as e:
            warn(f"TikTok video fetch error: {e}")

    if trend_type in ("creators", "all"):
        try:
            creators = tt_mod.fetch_trending_creators(country=country, period=period, limit=15, ms_token=ms_token)
            result["trending_creators"] = creators
            if not _json_output:
                click.echo(f"\n{BOLD}Trending Creators:{RESET}")
                for i, c in enumerate(creators[:10], 1):
                    followers = f"{c.get('follower_count', 0):,}" if c.get('follower_count') else "—"
                    avg_v = f"{c.get('avg_views', 0):,}" if c.get('avg_views') else "—"
                    click.echo(f"  {i:>2}. {ACCENT}{c.get('handle', ''):<25}{RESET}  {followers} followers  avg views: {avg_v}")
        except Exception as e:
            warn(f"TikTok creator fetch error: {e}")

    if not ms_token and not _json_output:
        info("Tip: Add TikTok msToken for higher API rate limits — cli-anything-social-trends config set-tiktok-token <TOKEN>")

    return result


@trends.command("search")
@click.argument("hashtag")
@click.option("--platform", "-p",
              type=click.Choice(["youtube", "tiktok", "all"], case_sensitive=False),
              default="all")
@click.option("--country", "-c", default="US")
def trends_search(hashtag: str, platform: str, country: str):
    """Search for a specific hashtag across platforms."""
    results = {}

    if platform in ("youtube", "all"):
        api_key = cfg_mod.get_youtube_api_key()
        if api_key:
            try:
                videos = yt_mod.search_hashtag(api_key, hashtag, region=country)
                results["youtube"] = {"videos": videos}
                if not _json_output:
                    section(f"YouTube — #{hashtag.lstrip('#')}")
                    for i, v in enumerate(videos[:10], 1):
                        click.echo(f"  {i:>2}. {v['title'][:60]}")
                        click.echo(f"      {DIM}{v['channel']}{RESET}")
            except Exception as e:
                warn(f"YouTube search error: {e}")
        else:
            warn("YouTube API key required for hashtag search. Set with: config set-youtube-key <KEY>")

    if platform in ("tiktok", "all"):
        ms_token = cfg_mod.get_tiktok_ms_token()
        try:
            stats = tt_mod.search_hashtag_stats(hashtag, ms_token)
            results["tiktok"] = stats
            if not _json_output:
                section(f"TikTok — #{hashtag.lstrip('#')}")
                click.echo(f"  Views:  {stats.get('view_count', 0):,}")
                click.echo(f"  Videos: {stats.get('publish_count', 0):,}")
                click.echo(f"  Trend:  {stats.get('trend', '—')}")
        except Exception as e:
            warn(f"TikTok search error: {e}")

    if _json_output:
        output(results)


# ── Theme page commands ───────────────────────────────────────────

@cli.group()
def themes():
    """Theme page creation: niches, playbook, and conversion tips."""


@themes.command("guide")
def themes_guide():
    """Print the complete theme page explainer."""
    if _json_output:
        output({"guide": theme_mod.THEME_PAGE_EXPLAINER})
        return
    click.echo(f"{ACCENT}{BOLD}{theme_mod.THEME_PAGE_EXPLAINER}{RESET}")


@themes.command("list-niches")
@click.option("--sort", "-s", type=click.Choice(["difficulty", "default"]), default="difficulty")
def themes_list_niches(sort: str):
    """List top-converting theme page niches with monetization info."""
    niches = theme_mod.list_niches(sort_by=sort)
    if _json_output:
        output(niches)
        return
    section("Top Theme Page Niches")
    for n in niches:
        diff_bar = "█" * n["difficulty"] + "░" * (10 - n["difficulty"])
        click.echo(f"\n  {ACCENT}{BOLD}{n['niche']}{RESET}  difficulty: {diff_bar} {n['difficulty']}/10")
        click.echo(f"  Competition: {n['competition']}    Revenue CPM: {n['avg_cpm']}")
        click.echo(f"  Monetization: {', '.join(n['monetization'])}")
        click.echo(f"  {DIM}Tip: {n['tip']}{RESET}")


@themes.command("niche")
@click.argument("niche_name")
def themes_niche(niche_name: str):
    """Get detailed info and strategy for a specific niche."""
    detail = theme_mod.get_niche_detail(niche_name)
    if not detail:
        err(f"Niche '{niche_name}' not found. Run: themes list-niches")
        return
    output(detail)
    if not _json_output:
        section(f"{detail['niche']} Theme Page Strategy")
        click.echo(f"  Keywords:      {', '.join(detail['keywords'])}")
        click.echo(f"  Monetization:  {', '.join(detail['monetization'])}")
        click.echo(f"  Competition:   {detail['competition']}")
        click.echo(f"  CPM potential: {detail['avg_cpm']}")
        click.echo(f"\n  {BOLD}Pro Tip:{RESET} {detail['tip']}")


@themes.command("playbook")
@click.option("--step", "-s", type=int, default=None, help="Show a specific step only")
def themes_playbook(step: Optional[int]):
    """7-step theme page creation playbook."""
    steps = theme_mod.get_playbook(step)
    if _json_output:
        output(steps)
        return
    section("Theme Page Creation Playbook")
    for s in steps:
        click.echo(f"\n{BOLD}{ACCENT}Step {s['step']}: {s['title']}{RESET}")
        for action in s["actions"]:
            click.echo(f"  {GREEN}→{RESET} {action}")
        if s.get("tools"):
            click.echo(f"  {DIM}Tools: {', '.join(s['tools'])}{RESET}")


@themes.command("convert")
@click.option("--category", "-c",
              type=click.Choice(["bio_cta", "caption_hooks", "engagement_boosters", "link_in_bio_stack"]),
              default=None, help="Specific conversion category")
def themes_convert(category: Optional[str]):
    """Show conversion optimization tips: CTAs, hooks, engagement boosters."""
    tips = theme_mod.get_conversion_tips(category)
    if _json_output:
        output(tips)
        return
    section("Conversion Optimization Tips")
    for cat, items in tips.items():
        click.echo(f"\n{BOLD}{ACCENT}{cat.replace('_', ' ').title()}{RESET}")
        for item in items:
            click.echo(f"  {YELLOW}▸{RESET} {item}")


# ── REPL ──────────────────────────────────────────────────────────

@cli.command()
def repl():
    """Launch interactive REPL mode."""
    global _repl_mode
    _repl_mode = True
    _banner()
    info("Type a command or 'help' for available commands. 'exit' to quit.\n")

    session = PromptSession(
        history=InMemoryHistory(),
        style=PtkStyle.from_dict({"prompt": "bold ansiorange"}),
    )

    while True:
        try:
            line = session.prompt("social-trends> ").strip()
        except (EOFError, KeyboardInterrupt):
            click.echo(f"\n{DIM}Goodbye.{RESET}")
            break

        if not line:
            continue
        if line.lower() in ("exit", "quit", "q"):
            click.echo(f"{DIM}Goodbye.{RESET}")
            break
        if line.lower() in ("help", "?", "h"):
            _repl_help()
            continue

        # Execute command through Click's test runner
        import shlex
        try:
            args = shlex.split(line)
            from click.testing import CliRunner
            runner = CliRunner(mix_stderr=False)
            result = runner.invoke(cli, args, catch_exceptions=False)
            if result.output:
                click.echo(result.output, nl=False)
        except SystemExit:
            pass
        except Exception as e:
            err(str(e))


def _repl_help():
    click.echo(f"""
{BOLD}Available Commands:{RESET}
  {ACCENT}trends fetch youtube{RESET}               Fetch YouTube trending videos/music/hashtags
  {ACCENT}trends fetch tiktok{RESET}                Fetch TikTok trending hashtags/music/videos/creators
  {ACCENT}trends fetch all{RESET}                   Fetch both platforms
  {ACCENT}trends fetch tiktok --type music{RESET}   Fetch TikTok trending songs only
  {ACCENT}trends search #hashtag{RESET}             Search a specific hashtag

  {ACCENT}account add{RESET}                        Add a social media account
  {ACCENT}account list{RESET}                       List tracked accounts
  {ACCENT}account optimize{RESET}                   Generate optimization reports

  {ACCENT}themes guide{RESET}                       What is a theme page?
  {ACCENT}themes list-niches{RESET}                 Browse top niches by difficulty
  {ACCENT}themes niche <name>{RESET}                Detail on a specific niche
  {ACCENT}themes playbook{RESET}                    Full 7-step theme page playbook
  {ACCENT}themes convert{RESET}                     Conversion tips: hooks, CTAs, bio

  {ACCENT}config set-youtube-key <KEY>{RESET}       Set YouTube Data API v3 key
  {ACCENT}config set-tiktok-token <TOKEN>{RESET}    Set TikTok msToken (optional)
  {ACCENT}config show{RESET}                        Show current config

  {DIM}exit / quit / q{RESET}                   Exit REPL
""")


def main():
    cli()


if __name__ == "__main__":
    main()
