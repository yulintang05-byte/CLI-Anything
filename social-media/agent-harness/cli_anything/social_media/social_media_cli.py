#!/usr/bin/env python3
"""Social Media CLI — viral trend scraping, account optimization, and theme page tools.

Usage:
    # Scrape trending content
    social-media trends fetch --platform tiktok
    social-media trends fetch --platform youtube --category music
    social-media trends hashtags --platform tiktok --region US
    social-media trends sounds --region US

    # Account optimization
    social-media account optimize --handle @myaccount --platform tiktok \\
        --followers 5000 --avg-views 1200 --avg-likes 180 --freq 7 --niche fitness

    # Theme page tools
    social-media theme-page niches
    social-media theme-page analyze --niche luxury_lifestyle
    social-media theme-page strategy --platform tiktok
    social-media theme-page convert --platform tiktok --goal sales

    # Config
    social-media config set youtube_api_key YOUR_KEY
    social-media config set tiktok_session_id YOUR_SESSION
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_media.utils.config import (
    load_config,
    save_config,
    get_youtube_api_key,
    get_tiktok_session_id,
)
from cli_anything.social_media.core import (
    youtube_trends,
    tiktok_trends,
    account_optimizer,
    theme_pages,
)

_json_output = False


def output(data, message: str = ""):
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        _pretty_print(data)


def _pretty_print(data, indent: int = 0):
    prefix = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{prefix}{k}:")
                _pretty_print(v, indent + 1)
            else:
                click.echo(f"{prefix}{k}: {v}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                click.echo(f"{prefix}[{i + 1}]")
                _pretty_print(item, indent + 1)
            else:
                click.echo(f"{prefix}  - {item}")
    else:
        click.echo(f"{prefix}{data}")


def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (RuntimeError, ValueError, KeyError) as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# ─── Root ───────────────────────────────────────────────────────────────────

@click.group()
@click.option("--json", "use_json", is_flag=True, help="Output as JSON.")
def main(use_json: bool):
    """Social Media CLI — trend scraping, account optimization, theme pages."""
    global _json_output
    _json_output = use_json


# ─── Config ─────────────────────────────────────────────────────────────────

@main.group()
def config():
    """Manage API keys and settings."""


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """Set a config value (youtube_api_key, tiktok_session_id)."""
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)
    output({"key": key, "status": "saved"}, f"Config updated: {key}")


@config.command("show")
def config_show():
    """Show current config (API keys are masked)."""
    cfg = load_config()
    display = {}
    for k, v in cfg.items():
        if "key" in k or "session" in k or "token" in k:
            display[k] = f"{str(v)[:4]}{'*' * (len(str(v)) - 4)}" if len(str(v)) > 4 else "****"
        else:
            display[k] = v
    output(display, "Current config:")


# ─── Trends ─────────────────────────────────────────────────────────────────

@main.group()
def trends():
    """Scrape viral trends from YouTube and TikTok."""


@trends.command("fetch")
@click.option("--platform", type=click.Choice(["tiktok", "youtube", "all"]), default="all",
              help="Platform to fetch trends from.")
@click.option("--category", default="general",
              help="Content category (youtube: general|music|gaming|tech|sports|beauty)")
@click.option("--region", default="US", help="Region code (US, GB, CA, AU, etc.)")
@click.option("--limit", default=20, help="Max results to return.")
@handle_error
def trends_fetch(platform: str, category: str, region: str, limit: int):
    """Fetch currently trending videos."""
    results = {}

    if platform in ("youtube", "all"):
        api_key = get_youtube_api_key()
        if api_key:
            click.echo("Fetching YouTube trends via API...", err=True)
            yt_videos = youtube_trends.fetch_trending_via_api(
                api_key, category=category, region=region, max_results=limit
            )
        else:
            click.echo("No YouTube API key — falling back to scrape...", err=True)
            yt_videos = youtube_trends.fetch_trending_scrape(category=category, region=region)
        results["youtube"] = yt_videos[:limit]

    if platform in ("tiktok", "all"):
        session_id = get_tiktok_session_id()
        click.echo("Fetching TikTok trends...", err=True)
        tt_videos = tiktok_trends.fetch_trending_videos(
            session_id=session_id or None, region=region, max_results=limit
        )
        results["tiktok"] = tt_videos[:limit]

    output(results, f"Trending videos [{platform.upper()} | {region}]:")


@trends.command("hashtags")
@click.option("--platform", type=click.Choice(["tiktok", "youtube", "all"]), default="all")
@click.option("--region", default="US")
@click.option("--limit", default=30)
@handle_error
def trends_hashtags(platform: str, region: str, limit: int):
    """Fetch trending hashtags."""
    results = {}

    if platform in ("tiktok", "all"):
        session_id = get_tiktok_session_id()
        click.echo("Fetching TikTok trending hashtags...", err=True)
        tt_tags = tiktok_trends.fetch_trending_hashtags(
            session_id=session_id or None, region=region, top_n=limit
        )
        results["tiktok"] = tt_tags

    if platform in ("youtube", "all"):
        api_key = get_youtube_api_key()
        if api_key:
            yt_videos = youtube_trends.fetch_trending_via_api(api_key, region=region, max_results=50)
        else:
            yt_videos = youtube_trends.fetch_trending_scrape(region=region)
        yt_tags = youtube_trends.extract_trending_hashtags(yt_videos, top_n=limit)
        results["youtube"] = yt_tags

    output(results, f"Trending hashtags [{platform.upper()} | {region}]:")


@trends.command("sounds")
@click.option("--region", default="US")
@click.option("--limit", default=25)
@handle_error
def trends_sounds(region: str, limit: int):
    """Fetch trending TikTok sounds and YouTube music."""
    session_id = get_tiktok_session_id()
    click.echo("Fetching TikTok trending sounds...", err=True)
    tt_sounds = tiktok_trends.fetch_trending_sounds(
        session_id=session_id or None, region=region, top_n=limit
    )

    # YouTube music
    api_key = get_youtube_api_key()
    yt_music = []
    if api_key:
        click.echo("Fetching YouTube trending music...", err=True)
        yt_music_videos = youtube_trends.fetch_trending_via_api(
            api_key, category="music", region=region, max_results=25
        )
        yt_music = youtube_trends.fetch_trending_music_from_videos(yt_music_videos)

    output(
        {"tiktok_sounds": tt_sounds, "youtube_music": yt_music},
        "Trending sounds & music:"
    )


@trends.command("niche")
@click.argument("hashtag")
@click.option("--platform", type=click.Choice(["tiktok"]), default="tiktok")
@click.option("--limit", default=20)
@handle_error
def trends_niche(hashtag: str, platform: str, limit: int):
    """Fetch top videos for a specific hashtag niche."""
    session_id = get_tiktok_session_id()
    click.echo(f"Searching TikTok videos for #{hashtag}...", err=True)
    videos = tiktok_trends.search_hashtag_videos(
        hashtag=hashtag, session_id=session_id or None, max_results=limit
    )
    trending_tags = tiktok_trends.extract_niche_hashtags(videos)
    output(
        {"videos": videos, "co_occurring_hashtags": trending_tags},
        f"TikTok niche: #{hashtag}"
    )


# ─── Account ────────────────────────────────────────────────────────────────

@main.group()
def account():
    """Optimize and analyze social media accounts."""


@account.command("optimize")
@click.option("--handle", required=True, help="Account handle (e.g., @myaccount)")
@click.option("--platform", type=click.Choice(["tiktok", "youtube", "instagram"]),
              default="tiktok")
@click.option("--followers", default=0, type=int)
@click.option("--following", default=0, type=int)
@click.option("--avg-views", default=0, type=int)
@click.option("--avg-likes", default=0, type=int)
@click.option("--avg-comments", default=0, type=int)
@click.option("--freq", default=0.0, type=float, help="Posts per week.")
@click.option("--niche", default="", help="Your content niche.")
@click.option("--bio", default="", help="Your current bio text.")
@handle_error
def account_optimize(
    handle, platform, followers, following, avg_views,
    avg_likes, avg_comments, freq, niche, bio
):
    """Score your account and get specific optimization recommendations."""
    profile = {
        "handle": handle,
        "platform": platform,
        "bio": bio,
        "follower_count": followers,
        "following_count": following,
        "avg_views": avg_views,
        "avg_likes": avg_likes,
        "avg_comments": avg_comments,
        "posting_frequency_per_week": freq,
        "niche": niche,
        "last_posts": [],
    }
    result = account_optimizer.analyze_account(profile)
    output(result, f"\nAccount Analysis: {handle} [{platform.upper()}]")

    if not _json_output:
        click.echo(f"\n{'=' * 50}")
        click.echo(f"  SCORE: {result['score']}/{result['max_score']}  GRADE: {result['grade']}")
        click.echo(f"  Engagement Rate: {result['engagement_rate']}%")
        click.echo(f"{'=' * 50}\n")

        if result["strengths"]:
            click.echo("STRENGTHS:")
            for s in result["strengths"]:
                click.echo(f"  ✓ {s}")

        if result["recommendations"]:
            click.echo("\nRECOMMENDATIONS:")
            for i, r in enumerate(result["recommendations"], 1):
                click.echo(f"  {i}. {r}")

        click.echo("\nBEST POSTING TIMES:")
        for t in result["best_posting_times_utc"]:
            click.echo(f"  • {t}")

        click.echo("\nGROWTH HACKS:")
        for h in result["growth_hacks"]:
            click.echo(f"  → {h}")


@account.command("batch")
@click.argument("profiles_json", type=click.Path(exists=True))
@handle_error
def account_batch(profiles_json: str):
    """Analyze multiple accounts from a JSON file.

    JSON format: list of profile objects (same fields as 'optimize').
    """
    with open(profiles_json) as f:
        profiles = json.load(f)
    results = account_optimizer.batch_analyze_accounts(profiles)
    output(results, f"Analyzed {len(results)} accounts (sorted by score):")


# ─── Theme Pages ─────────────────────────────────────────────────────────────

@main.group(name="theme-page")
def theme_page():
    """Theme page creation, monetization, and conversion tools."""


@theme_page.command("niches")
@handle_error
def theme_page_niches():
    """List all proven theme page niches with monetization data."""
    niches = theme_pages.list_all_niches()
    output(niches, "Proven Theme Page Niches:")


@theme_page.command("analyze")
@click.option("--niche", required=True, help="Niche to analyze (e.g., luxury_lifestyle, fitness_motivation)")
@handle_error
def theme_page_analyze(niche: str):
    """Get deep analysis and 90-day roadmap for a niche."""
    result = theme_pages.get_niche_analysis(niche)
    output(result, f"Niche Analysis: {niche}")


@theme_page.command("strategy")
@click.option("--platform", type=click.Choice(["tiktok", "youtube", "instagram"]),
              default="tiktok")
@handle_error
def theme_page_strategy(platform: str):
    """Get the full growth strategy for a platform."""
    result = theme_pages.get_platform_strategy(platform)
    output(result, f"Platform Strategy: {platform.upper()}")

    if not _json_output:
        click.echo(f"\n{'=' * 50}")
        click.echo(f"  ALGORITHM: {result['algorithm']}")
        click.echo(f"{'=' * 50}\n")

        click.echo("GROWTH STRATEGY:")
        for tip in result["growth_strategy"]:
            click.echo(f"  • {tip}")

        click.echo("\nTHEME PAGE TIPS:")
        for tip in result["theme_page_tips"]:
            click.echo(f"  → {tip}")

        click.echo("\nCONTENT REPURPOSING WORKFLOW:")
        for step in result["content_repurposing_workflow"]:
            click.echo(f"  {step}")

        if result.get("monetization_milestones"):
            click.echo("\nMONETIZATION MILESTONES:")
            for milestone, detail in result["monetization_milestones"].items():
                click.echo(f"  [{milestone}] {detail}")


@theme_page.command("convert")
@click.option("--platform", type=click.Choice(["tiktok", "youtube", "instagram"]),
              default="tiktok")
@click.option("--goal", type=click.Choice(["sales", "follows", "email_signups", "affiliate_clicks"]),
              default="sales")
@click.option("--current-rate", default=None, type=float,
              help="Your current conversion rate % (optional, for diagnosis)")
@handle_error
def theme_page_convert(platform: str, goal: str, current_rate: Optional[float]):
    """Get conversion optimization tactics for a theme page."""
    result = theme_pages.get_conversion_optimization(
        platform=platform, current_conversion_rate=current_rate, goal=goal
    )
    output(result, f"Conversion Optimization [{platform.upper()} → {goal}]:")

    if not _json_output:
        click.echo(f"\nCTA PLACEMENT: {result['cta_placement']}")
        if result.get("diagnosis"):
            click.echo(f"DIAGNOSIS: {result['diagnosis']}")
        click.echo("\nCONVERSION TACTICS:")
        for t in result["conversion_tactics"]:
            click.echo(f"  → {t}")
        click.echo("\nFUNNEL STAGES:")
        for stage in result["funnel_stages"]:
            click.echo(f"  {stage}")


if __name__ == "__main__":
    main()
