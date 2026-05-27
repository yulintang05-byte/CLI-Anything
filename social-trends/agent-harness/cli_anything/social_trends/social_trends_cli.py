#!/usr/bin/env python3
"""Social Trends CLI — Viral trend research, account optimisation, and theme page strategy.

Scrapes YouTube and TikTok for trending hashtags, sounds, and videos.
Generates content plans, optimises social accounts, and provides a complete
guide to creating and converting theme pages.

Usage:
    # Configure YouTube API key (optional — improves data quality)
    cli-anything-social-trends config set --youtube-api-key AIza...

    # Fetch TikTok trending hashtags
    cli-anything-social-trends tiktok hashtags --region US

    # Fetch YouTube trending videos
    cli-anything-social-trends youtube videos --region US --category music

    # Cross-platform trend report
    cli-anything-social-trends trends report --region US

    # Generate 7-day content plan
    cli-anything-social-trends plan weekly --platform tiktok --niche fitness

    # Optimise your TikTok account
    cli-anything-social-trends optimise tiktok --niche fitness --followers 5000

    # Theme page guide
    cli-anything-social-trends theme guide

    # Interactive REPL
    cli-anything-social-trends repl
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_trends.core import (
    tiktok_trends,
    youtube_trends,
    trend_analyzer,
    account_optimizer,
    theme_page_guide,
    content_planner,
)
from cli_anything.social_trends.utils.scraper_backend import (
    load_config, save_config, clear_cache,
)

_json_output = False
_repl_mode = False


def output(data, message: str = ""):
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        _pretty(data)


def _pretty(data, indent: int = 0):
    pad = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{pad}{k}:")
                _pretty(v, indent + 1)
            else:
                click.echo(f"{pad}{k}: {v}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                click.echo(f"{pad}[{i + 1}]")
                _pretty(item, indent + 1)
            else:
                click.echo(f"{pad}  - {item}")
    else:
        click.echo(f"{pad}{data}")


def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
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


# ── Main group ────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx, use_json):
    """Social Trends CLI — viral research, account optimisation, theme pages."""
    global _json_output
    _json_output = use_json
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── Config ────────────────────────────────────────────────────────────────────

@cli.group()
def config():
    """Configuration management."""
    pass


@config.command("set")
@click.option("--youtube-api-key", default=None, help="YouTube Data API v3 key")
@handle_error
def config_set(youtube_api_key):
    """Set configuration values."""
    cfg = load_config()
    if youtube_api_key:
        cfg["youtube_api_key"] = youtube_api_key
        click.echo("YouTube API key saved.")
    save_config(cfg)
    output({"saved": list(cfg.keys())}, "Configuration updated.")


@config.command("show")
@handle_error
def config_show():
    """Show current configuration."""
    cfg = load_config()
    safe = {k: ("***" if "key" in k or "secret" in k else v) for k, v in cfg.items()}
    output(safe or {"note": "No configuration set yet."})


@config.command("cache-clear")
@handle_error
def config_cache_clear():
    """Clear all cached API/scrape responses."""
    result = clear_cache()
    output(result, f"Cache cleared: {result['cleared']} entries removed.")


# ── TikTok commands ───────────────────────────────────────────────────────────

@cli.group()
def tiktok():
    """TikTok trend commands."""
    pass


@tiktok.command("hashtags")
@click.option("--region", "-r", default="US", help="Region code (US, UK, AU, CA…)")
@click.option("--period", "-p", type=click.Choice(["7", "30"]), default="7",
              help="Trend period in days")
@click.option("--limit", "-n", type=int, default=20, help="Number of hashtags to show")
@handle_error
def tiktok_hashtags(region, period, limit):
    """Fetch trending TikTok hashtags."""
    tags = tiktok_trends.get_trending_hashtags(region, int(period))
    output(tags[:limit], f"TikTok Trending Hashtags ({region}, {period}d):")


@tiktok.command("sounds")
@click.option("--region", "-r", default="US", help="Region code")
@click.option("--period", "-p", type=click.Choice(["7", "30"]), default="7",
              help="Trend period in days")
@click.option("--limit", "-n", type=int, default=15, help="Number of sounds to show")
@handle_error
def tiktok_sounds(region, period, limit):
    """Fetch trending TikTok sounds and music."""
    sounds = tiktok_trends.get_trending_sounds(region, int(period))
    output(sounds[:limit], f"TikTok Trending Sounds ({region}, {period}d):")


@tiktok.command("videos")
@click.option("--region", "-r", default="US", help="Region code")
@click.option("--period", "-p", type=click.Choice(["7", "30"]), default="7")
@click.option("--limit", "-n", type=int, default=10)
@handle_error
def tiktok_videos(region, period, limit):
    """Fetch trending TikTok videos."""
    videos = tiktok_trends.get_trending_videos(region, int(period))
    output(videos[:limit], f"TikTok Trending Videos ({region}):")


# ── YouTube commands ──────────────────────────────────────────────────────────

@cli.group()
def youtube():
    """YouTube trend commands."""
    pass


@youtube.command("videos")
@click.option("--region", "-r", default="US", help="Region code")
@click.option("--category", "-c",
              type=click.Choice(["all", "music", "gaming", "film", "news",
                                 "sports", "science", "howto", "travel",
                                 "pets", "entertainment"]),
              default="all", help="Video category")
@click.option("--limit", "-n", type=int, default=15)
@handle_error
def youtube_videos(region, category, limit):
    """Fetch trending YouTube videos.

    Requires a YouTube API key for full data; falls back to web scraping.
    """
    videos = youtube_trends.get_trending_videos(region, category, limit)
    output(videos, f"YouTube Trending Videos ({region}, {category}):")


@youtube.command("hashtags")
@click.option("--region", "-r", default="US")
@click.option("--limit", "-n", type=int, default=20)
@handle_error
def youtube_hashtags(region, limit):
    """Extract trending hashtags from YouTube trending videos."""
    tags = youtube_trends.get_trending_hashtags(region, limit)
    output(tags[:limit], f"YouTube Trending Hashtags ({region}):")


@youtube.command("music")
@click.option("--region", "-r", default="US")
@handle_error
def youtube_music(region):
    """Fetch trending music videos on YouTube."""
    videos = youtube_trends.get_trending_music(region)
    output(videos, f"YouTube Trending Music ({region}):")


# ── Cross-platform trends ─────────────────────────────────────────────────────

@cli.group()
def trends():
    """Cross-platform trend analysis."""
    pass


@trends.command("report")
@click.option("--region", "-r", default="US")
@click.option("--limit", "-n", type=int, default=20)
@handle_error
def trends_report(region, limit):
    """Generate a cross-platform trend report (YouTube + TikTok)."""
    if not _json_output:
        click.echo(f"Fetching trends for {region}...")
    yt_videos = youtube_trends.get_trending_videos(region, max_results=25)
    tt_videos = tiktok_trends.get_trending_videos(region)
    yt_tags = youtube_trends.get_trending_hashtags(region)
    tt_tags = tiktok_trends.get_trending_hashtags(region)

    merged_tags = trend_analyzer.merge_hashtags(yt_tags, tt_tags)
    trend_summary = trend_analyzer.merge_trends(yt_videos, tt_videos)

    report = {
        "region": region,
        "top_cross_platform_hashtags": merged_tags[:10],
        "top_themes": trend_summary.get("top_themes", []),
        "cross_platform_opportunities": trend_summary.get("cross_platform_opportunity", []),
        "youtube_videos_analysed": trend_summary.get("youtube_video_count", 0),
        "tiktok_videos_analysed": trend_summary.get("tiktok_video_count", 0),
    }
    output(report, "Cross-Platform Trend Report:")


@trends.command("hashtag-score")
@click.argument("hashtags", nargs=-1, required=True)
@handle_error
def trends_hashtag_score(hashtags):
    """Score a set of hashtags for reach and balance.

    Example: cli-anything-social-trends trends hashtag-score #fyp #fitness #workout
    """
    result = trend_analyzer.score_hashtag_set(list(hashtags))
    output(result, "Hashtag Analysis:")


# ── Content planner ───────────────────────────────────────────────────────────

@cli.group()
def plan():
    """Content planning commands."""
    pass


@plan.command("weekly")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              default="tiktok")
@click.option("--niche", "-n", default="general", help="Your content niche")
@click.option("--region", "-r", default="US")
@click.option("--posts-per-day", type=int, default=2,
              help="Number of posts per day (1-5)")
@handle_error
def plan_weekly(platform, niche, region, posts_per_day):
    """Generate a 7-day content calendar with trending hashtags and sounds."""
    if not _json_output:
        click.echo(f"Generating {platform} content plan for '{niche}' niche...")
    plan_data = content_planner.generate_weekly_plan(
        platform, niche, region, max(1, min(posts_per_day, 5))
    )
    output(plan_data, "Weekly Content Plan:")


@plan.command("hashtags")
@click.option("--niche", "-n", default="general")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              default="tiktok")
@click.option("--region", "-r", default="US")
@click.option("--count", "-c", type=int, default=7)
@handle_error
def plan_hashtags(niche, platform, region, count):
    """Generate an optimised hashtag set for a post, ready to copy-paste."""
    result = content_planner.generate_hashtag_set(niche, platform, region, count)
    if not _json_output:
        click.echo(f"\nHashtag set for {platform} / {niche}:\n")
        click.echo(f"  Copy-paste: {result['copy_paste']}\n")
        click.echo("  Analysis:")
        for h in result["analysis"]["hashtags"]:
            click.echo(f"    {h['hashtag']} → {h['tier']} ({h['estimated_reach']})")
        click.echo(f"\n  Mix score: {result['analysis']['mix_score']}")
        click.echo(f"  Suggestion: {result['analysis']['suggestion']}")
    else:
        output(result)


@plan.command("ideas")
@click.option("--niche", "-n", default="general")
@click.option("--count", "-c", type=int, default=10)
@click.option("--region", "-r", default="US")
@handle_error
def plan_ideas(niche, count, region):
    """Generate content ideas based on live trends."""
    if not _json_output:
        click.echo(f"Generating content ideas for '{niche}'...")
    ideas = content_planner.generate_content_ideas(niche, count, region)
    output(ideas, f"Content Ideas ({niche}):")


# ── Account optimiser ─────────────────────────────────────────────────────────

@cli.group()
def optimise():
    """Account optimisation commands."""
    pass


@optimise.command("tiktok")
@click.option("--username", "-u", default=None, help="Saved account username")
@click.option("--niche", "-n", default="", help="Content niche")
@click.option("--followers", "-f", type=int, default=0)
@click.option("--avg-views", type=int, default=0, help="Average views per video")
@handle_error
def optimise_tiktok(username, niche, followers, avg_views):
    """Generate TikTok account optimisation recommendations."""
    result = account_optimizer.optimise_account(
        "tiktok", username, niche, followers, avg_views
    )
    output(result, "TikTok Account Optimisation Report:")


@optimise.command("youtube")
@click.option("--username", "-u", default=None)
@click.option("--niche", "-n", default="")
@click.option("--subscribers", "-s", type=int, default=0)
@click.option("--avg-views", type=int, default=0)
@handle_error
def optimise_youtube(username, niche, subscribers, avg_views):
    """Generate YouTube channel optimisation recommendations."""
    result = account_optimizer.optimise_account(
        "youtube", username, niche, subscribers, avg_views
    )
    output(result, "YouTube Channel Optimisation Report:")


@optimise.command("instagram")
@click.option("--username", "-u", default=None)
@click.option("--niche", "-n", default="")
@click.option("--followers", "-f", type=int, default=0)
@click.option("--avg-views", type=int, default=0, help="Average Reel views")
@handle_error
def optimise_instagram(username, niche, followers, avg_views):
    """Generate Instagram account optimisation recommendations."""
    result = account_optimizer.optimise_account(
        "instagram", username, niche, followers, avg_views
    )
    output(result, "Instagram Account Optimisation Report:")


@optimise.command("add-account")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              required=True)
@click.option("--username", "-u", required=True)
@click.option("--niche", "-n", required=True)
@click.option("--followers", "-f", type=int, default=0)
@click.option("--avg-views", type=int, default=0)
@handle_error
def optimise_add_account(platform, username, niche, followers, avg_views):
    """Save an account profile for quick optimisation lookups."""
    result = account_optimizer.add_account(platform, username, niche, followers, avg_views)
    output(result, f"Account saved: {platform}:{username}")


@optimise.command("list-accounts")
@handle_error
def optimise_list_accounts():
    """List all saved account profiles."""
    accounts = account_optimizer.list_accounts()
    output(accounts, f"Saved accounts ({len(accounts)}):")


# ── Theme page guide ──────────────────────────────────────────────────────────

@cli.group()
def theme():
    """Theme page creation and conversion guide."""
    pass


@theme.command("guide")
@handle_error
def theme_guide():
    """Print the complete step-by-step theme page setup checklist."""
    checklist = theme_page_guide.get_setup_checklist()
    if not _json_output:
        click.echo("\n  THEME PAGE SETUP GUIDE\n  " + "=" * 40)
        for step in checklist:
            click.echo(f"\n  Step {step['step']}: {step['title']}")
            click.echo("  " + "-" * 35)
            for task in step["tasks"]:
                click.echo(f"    □ {task}")
    else:
        output(checklist)


@theme.command("niches")
@click.option("--sort-by",
              type=click.Choice(["viral_potential", "competition", "avg_cpm"]),
              default="viral_potential")
@handle_error
def theme_niches(sort_by):
    """List all supported niches with profitability and competition data."""
    niches = theme_page_guide.list_niches(sort_by)
    if not _json_output:
        click.echo(f"\n  Niches sorted by {sort_by}:\n")
        for n in niches:
            click.echo(
                f"  {n['niche']:<20} "
                f"competition:{n['competition']:<10} "
                f"viral:{n['viral_potential']:<12} "
                f"CPM:{n['avg_cpm']}"
            )
    else:
        output(niches)


@theme.command("niche-info")
@click.argument("niche")
@handle_error
def theme_niche_info(niche):
    """Get detailed info for a specific niche."""
    result = theme_page_guide.get_niche_info(niche)
    output(result, f"Niche: {niche}")


@theme.command("monetise")
@click.option("--niche", "-n", default="")
@click.option("--followers", "-f", type=int, default=0)
@click.option("--strategy", "-s", default=None,
              help="Specific strategy to show (shoutouts/affiliate/digital_products/…)")
@handle_error
def theme_monetise(niche, followers, strategy):
    """Show monetisation strategies available for your account size."""
    result = theme_page_guide.get_monetisation_strategy(strategy, followers)
    output(result, "Monetisation Strategies:")


@theme.command("funnel")
@click.option("--niche", "-n", default="")
@click.option("--followers", "-f", type=int, default=0)
@handle_error
def theme_funnel(niche, followers):
    """Generate a personalised conversion funnel for your theme page."""
    result = theme_page_guide.get_conversion_funnel(niche, followers)
    if not _json_output:
        click.echo(f"\n  Conversion Funnel: {niche or 'general'} | {followers:,} followers\n")
        click.echo("  Funnel Stages:")
        for stage in result["funnel_stages"]:
            click.echo(f"\n    {stage['stage'].upper()}")
            click.echo(f"      Action: {stage['action']}")
            click.echo(f"      Goal:   {stage['goal']}")
        click.echo("\n  Immediate Actions:")
        for action in result["immediate_actions"]:
            click.echo(f"    → {action}")
        if result["recommended_strategies"]:
            click.echo("\n  Best Strategies for You:")
            for s in result["recommended_strategies"]:
                click.echo(f"    [{s['priority'].upper()}] {s['name']}")
    else:
        output(result)


@theme.command("sourcing")
@click.option("--strategy", "-s", default=None,
              help="Strategy name (repost_with_credit/original_branded_content/…)")
@handle_error
def theme_sourcing(strategy):
    """Show content sourcing strategies for theme pages."""
    result = theme_page_guide.get_sourcing_strategy(strategy)
    output(result, "Content Sourcing Strategies:")


# ── REPL ──────────────────────────────────────────────────────────────────────

@cli.command()
@handle_error
def repl():
    """Start interactive REPL session."""
    from cli_anything.social_trends.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("social-trends", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _commands = {
        "config":   "set|show|cache-clear",
        "tiktok":   "hashtags|sounds|videos",
        "youtube":  "videos|hashtags|music",
        "trends":   "report|hashtag-score",
        "plan":     "weekly|hashtags|ideas",
        "optimise": "tiktok|youtube|instagram|add-account|list-accounts",
        "theme":    "guide|niches|niche-info|monetise|funnel|sourcing",
        "help":     "Show this help",
        "quit":     "Exit REPL",
    }

    skin.info("Type 'help' for commands. API key optional — web scraping works without one.")

    while True:
        try:
            line = skin.get_input(pt_session)
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                skin.print_goodbye()
                break
            if line.lower() == "help":
                skin.help(_commands)
                continue
            args = line.split()
            try:
                cli.main(args, standalone_mode=False)
            except SystemExit:
                pass
            except click.exceptions.UsageError as e:
                skin.warning(f"Usage error: {e}")
            except Exception as e:
                skin.error(str(e))
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

    _repl_mode = False


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    cli()


if __name__ == "__main__":
    main()
