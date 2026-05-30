#!/usr/bin/env python3
"""Social Trends CLI — Scrape YouTube & TikTok for viral trends, optimize accounts,
and build profitable theme pages.

Usage:
    # Scrape YouTube trending
    social-trends trends scrape-youtube --region US --limit 20

    # Scrape TikTok trending
    social-trends trends scrape-tiktok --region US

    # Get trending hashtags for a niche
    social-trends trends hashtags --niche fitness --platform tiktok

    # Merge YouTube + TikTok trends into one report
    social-trends trends report --region US -o report.json

    # Analyze an account
    social-trends account optimize --platform tiktok --username @myaccount \\
        --followers 5000 --niche fitness --freq 3

    # Theme page guide
    social-trends theme-pages guide
    social-trends theme-pages niches --sort conversion_potential
    social-trends theme-pages calendar --niche fitness --days 7

    # Interactive REPL
    social-trends repl
"""

import json
import sys
import os
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_trends.scrapers import youtube as yt_scraper
from cli_anything.social_trends.scrapers import tiktok as tt_scraper
from cli_anything.social_trends.core.trends import merge_platform_trends
from cli_anything.social_trends.optimizer.account import analyze_account, bulk_optimize
from cli_anything.social_trends.theme_pages import guide as theme_guide
from cli_anything.social_trends.theme_pages import niches as niche_db
from cli_anything.social_trends.theme_pages.content_calendar import (
    generate_weekly_calendar,
    generate_monthly_calendar,
)
from cli_anything.social_trends.utils.export import to_json, to_markdown, save_to_file

_json_output = False


def output(data, message: str = ""):
    """Output data in JSON or human-readable format."""
    if _json_output:
        click.echo(to_json(data))
    else:
        if message:
            click.echo(f"\n{message}")
        _pretty_print(data)


def _pretty_print(data, indent=0):
    prefix = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{prefix}{_fmt_key(k)}:")
                _pretty_print(v, indent + 1)
            else:
                click.echo(f"{prefix}{_fmt_key(k)}: {v}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                click.echo(f"{prefix}[{i + 1}]")
                _pretty_print(item, indent + 1)
            else:
                click.echo(f"{prefix}  - {item}")
    else:
        click.echo(f"{prefix}{data}")


def _fmt_key(k: str) -> str:
    return k.replace("_", " ").title()


def _handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RuntimeError as e:
            if _json_output:
                click.echo(to_json({"error": str(e), "type": "runtime_error"}))
            else:
                click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        except Exception as e:
            if _json_output:
                click.echo(to_json({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"Unexpected error: {e}", err=True)
            sys.exit(1)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# ============================================================================
# Main CLI group
# ============================================================================

@click.group(invoke_without_command=True)
@click.option("--json", "json_mode", is_flag=True, help="Output in JSON format")
@click.pass_context
def cli(ctx, json_mode):
    """Social Trends CLI — Viral trend scraping, account optimization, and theme page strategy.

    Scrape YouTube and TikTok for trending content, hashtags, and music.
    Optimize your social media accounts. Build profitable theme pages.

    Run without a subcommand to enter interactive REPL mode.
    """
    global _json_output
    _json_output = json_mode
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ============================================================================
# trends group
# ============================================================================

@cli.group()
def trends():
    """Scrape and analyze viral trends from YouTube and TikTok."""
    pass


@trends.command("scrape-youtube")
@click.option("--region", default="US", show_default=True, help="ISO country code (US, GB, IN...)")
@click.option("--category", default="all", show_default=True,
              type=click.Choice(["all", "music", "gaming", "news", "movies"]))
@click.option("--limit", default=20, show_default=True, type=int, help="Number of videos to fetch")
@click.option("--no-music", is_flag=True, help="Skip music metadata extraction")
@click.option("-o", "--output", "output_path", default=None, help="Save to file (JSON)")
@_handle_error
def trends_scrape_youtube(region, category, limit, no_music, output_path):
    """Scrape YouTube trending videos for hashtags, music, and viral content."""
    click.echo(f"Scraping YouTube trending ({region}, {category}, top {limit})...")
    result = yt_scraper.scrape_trending(
        region=region, category=category, limit=limit, include_music=not no_music
    )
    if output_path:
        save_to_file(result, output_path, "json")
        click.echo(f"Saved to: {output_path}")
    output(result, f"YouTube Trending — {region}")


@trends.command("scrape-tiktok")
@click.option("--region", default="US", show_default=True, help="ISO country code")
@click.option("--limit", default=20, show_default=True, type=int)
@click.option("-o", "--output", "output_path", default=None)
@_handle_error
def trends_scrape_tiktok(region, limit, output_path):
    """Scrape TikTok trending feed for hashtags, sounds, and viral videos."""
    click.echo(f"Scraping TikTok trending ({region}, top {limit})...")
    result = tt_scraper.scrape_trending(region=region, limit=limit)
    if output_path:
        save_to_file(result, output_path, "json")
        click.echo(f"Saved to: {output_path}")
    output(result, f"TikTok Trending — {region}")


@trends.command("hashtags")
@click.option("--platform", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "youtube"]), help="Platform to query")
@click.option("--niche", default=None, help="Niche/topic for YouTube hashtag research")
@click.option("--hashtag", default=None, help="Specific hashtag to analyze")
@click.option("--region", default="US", show_default=True)
@click.option("--limit", default=30, show_default=True, type=int)
@click.option("-o", "--output", "output_path", default=None)
@_handle_error
def trends_hashtags(platform, niche, hashtag, region, limit, output_path):
    """Get trending hashtags for a platform/niche."""
    if platform == "tiktok":
        if hashtag:
            click.echo(f"Analyzing TikTok hashtag: #{hashtag.lstrip('#')}...")
            result = tt_scraper.scrape_hashtag(hashtag, limit=limit)
        else:
            click.echo(f"Fetching TikTok trending hashtags ({region})...")
            result = tt_scraper.get_trending_hashtags(region=region, limit=limit)
    else:  # youtube
        if niche:
            click.echo(f"Finding top YouTube hashtags for niche: {niche}...")
            result = yt_scraper.get_top_hashtags_for_niche(niche, limit=limit)
        elif hashtag:
            click.echo(f"Analyzing YouTube hashtag: #{hashtag.lstrip('#')}...")
            result = yt_scraper.scrape_hashtag_videos(hashtag, limit=limit)
        else:
            click.echo("Specify --niche or --hashtag for YouTube hashtag research.")
            sys.exit(1)

    if output_path:
        save_to_file(result, output_path, "json")
        click.echo(f"Saved to: {output_path}")
    output(result, "Hashtag Analysis")


@trends.command("sounds")
@click.option("--region", default="US", show_default=True)
@click.option("--limit", default=20, show_default=True, type=int)
@click.option("-o", "--output", "output_path", default=None)
@_handle_error
def trends_sounds(region, limit, output_path):
    """Get trending TikTok sounds and music."""
    click.echo(f"Fetching trending TikTok sounds ({region})...")
    result = tt_scraper.get_trending_sounds(region=region, limit=limit)
    if output_path:
        save_to_file(result, output_path, "json")
        click.echo(f"Saved to: {output_path}")
    output(result, "Trending Sounds")


@trends.command("report")
@click.option("--region", default="US", show_default=True)
@click.option("--limit", default=15, show_default=True, type=int, help="Videos per platform")
@click.option("--platform", default="both", show_default=True,
              type=click.Choice(["youtube", "tiktok", "both"]))
@click.option("-o", "--output", "output_path", default=None, help="Save report to file")
@click.option("--format", "fmt", default="json", show_default=True,
              type=click.Choice(["json", "markdown", "csv"]))
@_handle_error
def trends_report(region, limit, platform, output_path, fmt):
    """Generate a merged cross-platform trend report with insights.

    Pulls from both YouTube and TikTok, identifies cross-platform trends
    (strongest viral signals), and generates actionable insights.
    """
    yt_data = None
    tt_data = None

    if platform in ("youtube", "both"):
        click.echo(f"Scraping YouTube trending ({region})...")
        try:
            yt_data = yt_scraper.scrape_trending(region=region, limit=limit)
        except Exception as e:
            click.echo(f"YouTube scraping failed: {e}", err=True)

    if platform in ("tiktok", "both"):
        click.echo(f"Scraping TikTok trending ({region})...")
        try:
            tt_data = tt_scraper.scrape_trending(region=region, limit=limit)
        except Exception as e:
            click.echo(f"TikTok scraping failed: {e}", err=True)

    if not yt_data and not tt_data:
        raise RuntimeError("Both scrapers failed. Check your internet connection and yt-dlp installation.")

    click.echo("Merging and analyzing trends...")
    report = merge_platform_trends(yt_data, tt_data, region=region)
    report_dict = report.to_dict()

    if output_path:
        save_to_file(report_dict, output_path, fmt)
        click.echo(f"Report saved to: {output_path}")

    output(report_dict, "Cross-Platform Trend Report")


# ============================================================================
# account group
# ============================================================================

@cli.group()
def account():
    """Analyze and optimize social media accounts."""
    pass


@account.command("optimize")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--username", required=True, help="Account username")
@click.option("--followers", default=0, type=int, help="Current follower count")
@click.option("--following", default=500, type=int, help="Following count")
@click.option("--posts", default=0, type=int, help="Total post count")
@click.option("--avg-views", default=0, type=int, help="Average views per post")
@click.option("--avg-likes", default=0, type=int, help="Average likes per post")
@click.option("--avg-comments", default=0, type=int, help="Average comments per post")
@click.option("--avg-shares", default=0, type=int, help="Average shares per post")
@click.option("--bio", default="", help="Current bio text")
@click.option("--niche", default="", help="Content niche (fitness, finance, food, etc.)")
@click.option("--freq", "posting_frequency", default=0.0, type=float,
              help="Posts per week")
@click.option("--age-days", default=0, type=int, help="Account age in days")
@click.option("--has-link", is_flag=True, help="Has link in bio")
@click.option("--no-pic", is_flag=True, help="Profile photo NOT set")
@click.option("--hashtags", default="", help="Comma-separated recent hashtags used")
@click.option("-o", "--output", "output_path", default=None)
@_handle_error
def account_optimize(platform, username, followers, following, posts, avg_views,
                     avg_likes, avg_comments, avg_shares, bio, niche,
                     posting_frequency, age_days, has_link, no_pic, hashtags, output_path):
    """Run a full optimization analysis on an account.

    Scores 6 dimensions and returns prioritized recommendations + 30-day action plan.
    """
    recent_hashtags = [h.strip() for h in hashtags.split(",") if h.strip()] if hashtags else []
    profile = {
        "platform": platform,
        "username": username,
        "follower_count": followers,
        "following_count": following,
        "post_count": posts,
        "avg_views": avg_views,
        "avg_likes": avg_likes,
        "avg_comments": avg_comments,
        "avg_shares": avg_shares,
        "bio": bio,
        "niche": niche,
        "posting_frequency_per_week": posting_frequency,
        "account_age_days": age_days,
        "has_link_in_bio": has_link,
        "profile_pic_set": not no_pic,
        "recent_hashtags": recent_hashtags,
    }
    result = analyze_account(profile)
    if output_path:
        save_to_file(result, output_path, "json")
        click.echo(f"Saved to: {output_path}")
    output(result, f"Account Optimization: @{username} ({platform})")


@account.command("bulk-optimize")
@click.argument("config_file")
@click.option("-o", "--output", "output_path", default=None)
@_handle_error
def account_bulk_optimize(config_file, output_path):
    """Optimize multiple accounts from a JSON config file.

    CONFIG_FILE should be a JSON array of account profiles.
    Each profile needs: platform, username, and optional metrics.

    Example config.json:
    [
      {"platform": "tiktok", "username": "acc1", "follower_count": 500, "niche": "fitness"},
      {"platform": "youtube", "username": "acc2", "follower_count": 2000, "niche": "finance"}
    ]
    """
    with open(config_file) as f:
        accounts = json.load(f)
    results = bulk_optimize(accounts)
    if output_path:
        save_to_file(results, output_path, "json")
        click.echo(f"Saved to: {output_path}")
    output(results, f"Bulk Account Optimization ({len(results)} accounts)")


@account.command("schedule")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--niche", default="general", show_default=True)
@_handle_error
def account_schedule(platform, niche):
    """Show optimal posting schedule for a platform and niche."""
    from cli_anything.social_trends.optimizer.account import _optimal_posting_schedule
    result = _optimal_posting_schedule(platform, niche)
    output(result, f"Optimal Posting Schedule: {platform} / {niche}")


# ============================================================================
# theme-pages group
# ============================================================================

@cli.group("theme-pages")
def theme_pages():
    """Theme page creation, niches, and conversion strategies."""
    pass


@theme_pages.command("guide")
@click.option("--section", default=None,
              help="Specific section: what_is_a_theme_page, phase_1_setup, phase_2_growth, "
                   "phase_3_monetization, phase_4_scaling, common_mistakes, tools_stack, "
                   "content_reposting_rules")
@click.option("-o", "--output", "output_path", default=None)
@click.option("--format", "fmt", default="json", type=click.Choice(["json", "markdown"]))
@_handle_error
def theme_pages_guide(section, output_path, fmt):
    """Show the complete theme page creation and conversion playbook."""
    if section:
        result = theme_guide.get_section(section)
        if result is None:
            raise RuntimeError(f"Section '{section}' not found. Run without --section to see all sections.")
    else:
        result = theme_guide.get_full_playbook()

    if output_path:
        save_to_file(result, output_path, fmt)
        click.echo(f"Saved to: {output_path}")
    output(result, "Theme Page Playbook")


@theme_pages.command("niches")
@click.option("--sort", "sort_by", default="conversion_potential", show_default=True,
              type=click.Choice(["conversion_potential", "growth_speed", "avg_cpm_usd", "competition"]))
@click.option("--max-competition", default=None,
              type=click.Choice(["low", "medium", "high", "very_high"]),
              help="Filter out niches above this competition level")
@click.option("--platform", default=None, help="Filter by platform (tiktok, youtube, instagram)")
@click.option("--search", default=None, help="Search niches by keyword")
@click.option("-o", "--output", "output_path", default=None)
@_handle_error
def theme_pages_niches(sort_by, max_competition, platform, search, output_path):
    """Browse and rank profitable theme page niches."""
    if search:
        results = niche_db.search_niches(search)
        label = f"Niche Search: '{search}'"
    else:
        results = niche_db.list_niches(
            sort_by=sort_by,
            min_competition=max_competition,
            platform=platform,
        )
        label = f"Niches (sorted by {sort_by})"

    if output_path:
        save_to_file(results, output_path, "json")
        click.echo(f"Saved to: {output_path}")
    output(results, label)


@theme_pages.command("niche-detail")
@click.argument("niche_key")
@_handle_error
def theme_pages_niche_detail(niche_key):
    """Get full details for a specific niche.

    NICHE_KEY: luxury_lifestyle, fitness_motivation, finance_investing,
               food_recipes, travel, pets_animals, tech_gadgets,
               beauty_skincare, quotes_mindset
    """
    result = niche_db.get_niche(niche_key)
    if result is None:
        raise RuntimeError(f"Niche '{niche_key}' not found. Run 'theme-pages niches' to see available keys.")
    output(result, f"Niche Details: {result.get('name', niche_key)}")


@theme_pages.command("quick-start")
@click.option("--niche", default="general", show_default=True, help="Your chosen niche")
@click.option("--followers", default=0, type=int, help="Current follower count")
@click.option("--platform", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("-o", "--output", "output_path", default=None)
@_handle_error
def theme_pages_quick_start(niche, followers, platform, output_path):
    """Get a personalized quick-start action plan for your theme page."""
    quick = theme_guide.get_quick_start(niche)
    conversion = theme_guide.get_conversion_guide(followers, platform)
    result = {
        "quick_start": quick,
        "conversion_strategy": conversion,
    }
    if output_path:
        save_to_file(result, output_path, "json")
        click.echo(f"Saved to: {output_path}")
    output(result, f"Theme Page Quick Start: {niche} on {platform}")


@theme_pages.command("calendar")
@click.option("--niche", default="general", show_default=True)
@click.option("--platforms", default="tiktok,youtube", show_default=True,
              help="Comma-separated: tiktok,youtube,instagram")
@click.option("--days", default=7, show_default=True, type=click.Choice(["7", "30"]))
@click.option("--posts-per-day", default=2, show_default=True, type=int)
@click.option("--start-date", default=None, help="YYYY-MM-DD start date")
@click.option("-o", "--output", "output_path", default=None)
@click.option("--format", "fmt", default="json", type=click.Choice(["json", "markdown"]))
@_handle_error
def theme_pages_calendar(niche, platforms, days, posts_per_day, start_date, output_path, fmt):
    """Generate a content calendar for your theme page.

    Produces daily posting schedule with content type suggestions,
    hook templates, and optimal posting times.
    """
    platform_list = [p.strip() for p in platforms.split(",") if p.strip()]
    if days == "30":
        result = generate_monthly_calendar(
            niche=niche,
            platforms=platform_list,
            posts_per_day=posts_per_day,
            start_date=start_date,
        )
        label = "30-Day Content Calendar"
    else:
        result = generate_weekly_calendar(
            niche=niche,
            platforms=platform_list,
            posts_per_day=posts_per_day,
            start_date=start_date,
        )
        label = "7-Day Content Calendar"

    if output_path:
        save_to_file(result, output_path, fmt)
        click.echo(f"Saved to: {output_path}")
    output(result, label)


# ============================================================================
# REPL
# ============================================================================

@cli.command()
def repl():
    """Start an interactive REPL session."""
    from cli_anything.social_trends._repl import run_repl
    run_repl(_json_output)


# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":
    cli()
