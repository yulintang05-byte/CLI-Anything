#!/usr/bin/env python3
"""Social Trends CLI — Scrape viral trends, optimize accounts, and master theme pages.

Commands:
    cli-anything-social-trends trends fetch [--platform] [--category] [--count]
    cli-anything-social-trends trends music [--platform] [--count]
    cli-anything-social-trends trends hashtags [--platform] [--niche] [--count]

    cli-anything-social-trends account optimize [--niche] [--platform] [--followers] ...
    cli-anything-social-trends account report [--account ...] [--output]

    cli-anything-social-trends theme-page list
    cli-anything-social-trends theme-page guide [--niche]
    cli-anything-social-trends theme-page strategy [--niche] [--monetization]

    cli-anything-social-trends report full [--niches] [--platforms] [--output]
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_trends.scrapers import youtube as yt
from cli_anything.social_trends.scrapers import tiktok as tt
from cli_anything.social_trends.optimizer import account_optimizer as opt
from cli_anything.social_trends.theme_pages import guide as tpg

_json_output = False


def output(data, message: str = ""):
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(f"\n{message}")
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


def _save_output(data: dict, filepath: Optional[str]):
    if filepath:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)
        click.echo(f"Saved to: {filepath}")


# ============================================================================
# Main CLI group
# ============================================================================

@click.group(invoke_without_command=True)
@click.option("--json", "json_mode", is_flag=True, help="Output in JSON format")
@click.pass_context
def cli(ctx, json_mode):
    """Social Trends CLI — Viral trends, account optimization, and theme pages.

    Scrape YouTube & TikTok for trending hashtags, sounds, and content.
    Generate data-driven account optimization plans.
    Learn how to build and monetize converting theme pages.

    Run any subcommand with --help for details.
    """
    global _json_output
    _json_output = json_mode
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ============================================================================
# Trends group
# ============================================================================

@cli.group()
def trends():
    """Fetch viral trends from YouTube and TikTok."""
    pass


@trends.command("fetch")
@click.option("--platform", default="all",
              type=click.Choice(["youtube", "tiktok", "all"]),
              help="Platform to scrape")
@click.option("--category", default="all",
              type=click.Choice(["all", "music", "gaming", "movies"]),
              help="YouTube trend category")
@click.option("--count", default=20, type=int, help="Number of results")
@click.option("--output-file", "-o", default=None, help="Save results to JSON file")
def trends_fetch(platform, category, count, output_file):
    """Fetch trending videos, hashtags, and sounds from YouTube and/or TikTok.

    Examples:
        cli-anything-social-trends trends fetch --platform all --count 20
        cli-anything-social-trends trends fetch --platform youtube --category music
        cli-anything-social-trends trends fetch --json -o trends.json
    """
    result = {}

    if platform in ("youtube", "all"):
        click.echo("Fetching YouTube trends...", err=True)
        result["youtube"] = yt.fetch_trending(category=category, max_results=count)

    if platform in ("tiktok", "all"):
        click.echo("Fetching TikTok trends...", err=True)
        result["tiktok"] = tt.fetch_all_trends(max_hashtags=count, max_sounds=15)

    _save_output(result, output_file)
    output(result, f"Trends ({platform})")


@trends.command("music")
@click.option("--platform", default="all",
              type=click.Choice(["youtube", "tiktok", "all"]),
              help="Platform")
@click.option("--count", default=20, type=int, help="Number of results")
@click.option("--output-file", "-o", default=None, help="Save results to JSON file")
def trends_music(platform, count, output_file):
    """Fetch trending music tracks and sounds.

    Examples:
        cli-anything-social-trends trends music --platform tiktok
        cli-anything-social-trends trends music --platform youtube --count 30
    """
    result = {}

    if platform in ("youtube", "all"):
        click.echo("Fetching YouTube trending music...", err=True)
        result["youtube_music"] = yt.fetch_trending_music(max_results=count)

    if platform in ("tiktok", "all"):
        click.echo("Fetching TikTok trending sounds...", err=True)
        result["tiktok_sounds"] = tt.fetch_trending_sounds(count=count)

    _save_output(result, output_file)
    output(result, "Trending Music & Sounds")


@trends.command("hashtags")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "youtube"]),
              help="Platform")
@click.option("--niche", default=None, help="Filter by niche keyword")
@click.option("--count", default=30, type=int, help="Number of hashtags")
@click.option("--output-file", "-o", default=None, help="Save results to JSON file")
def trends_hashtags(platform, niche, count, output_file):
    """Fetch trending hashtags and suggest niche-specific ones.

    Examples:
        cli-anything-social-trends trends hashtags --platform tiktok --count 30
        cli-anything-social-trends trends hashtags --niche fitness --count 20
    """
    if platform == "tiktok":
        hashtags = tt.fetch_trending_hashtags(count=count)
    else:
        yt_data = yt.fetch_trending(max_results=50)
        hashtags = yt_data.get("hashtags", [])

    if niche:
        # Filter/prioritize niche-relevant hashtags
        niche_lower = niche.lower()
        niche_tags = [h for h in hashtags if niche_lower in h.get("hashtag", "").lower()]
        other_tags = [h for h in hashtags if niche_lower not in h.get("hashtag", "").lower()]
        hashtags = (niche_tags + other_tags)[:count]

    result = {
        "platform": platform,
        "niche_filter": niche,
        "total": len(hashtags),
        "hashtags": hashtags,
    }
    _save_output(result, output_file)
    output(result, f"Trending Hashtags ({platform})")


# ============================================================================
# Account group
# ============================================================================

@cli.group()
def account():
    """Account optimization — scoring, strategy, and action plans."""
    pass


@account.command("optimize")
@click.option("--niche", required=True,
              help="Your content niche (fitness, cooking, travel, finance, fashion, beauty, gaming)")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "instagram", "all"]),
              help="Target platform")
@click.option("--followers", default=0, type=int, help="Current follower count")
@click.option("--avg-views", default=0, type=int, help="Average views per video")
@click.option("--avg-likes", default=0, type=int, help="Average likes per video")
@click.option("--output-file", "-o", default=None, help="Save optimization plan to JSON file")
def account_optimize(niche, platform, followers, avg_views, avg_likes, output_file):
    """Generate a personalized account optimization plan.

    Examples:
        cli-anything-social-trends account optimize --niche fitness --platform tiktok
        cli-anything-social-trends account optimize --niche finance --followers 5000 --avg-views 2000 --avg-likes 150
        cli-anything-social-trends account optimize --niche travel --platform instagram -o plan.json
    """
    platforms = ["tiktok", "youtube", "instagram"] if platform == "all" else [platform]
    results = []
    for p in platforms:
        r = opt.optimize_account(
            niche=niche,
            platform=p,
            follower_count=followers,
            avg_views=avg_views,
            avg_likes=avg_likes,
        )
        results.append(r)

    result = results[0] if len(results) == 1 else {"platforms": results}
    _save_output(result, output_file)
    output(result, f"Account Optimization: {niche} on {platform}")


@account.command("report")
@click.option("--account", "accounts", multiple=True,
              help="Account spec as name:niche:platform:followers:avg_views:avg_likes (repeatable)")
@click.option("--output-file", "-o", default=None, help="Save report to JSON file")
def account_report(accounts, output_file):
    """Generate optimization reports for multiple accounts.

    Example:
        cli-anything-social-trends account report \\
          --account "MyFitPage:fitness:tiktok:12000:8000:500" \\
          --account "TravelVibes:travel:instagram:5000:1200:80"
    """
    acct_list = []
    for spec in accounts:
        parts = spec.split(":")
        acct_list.append({
            "name": parts[0] if len(parts) > 0 else "Unknown",
            "niche": parts[1] if len(parts) > 1 else "general",
            "platform": parts[2] if len(parts) > 2 else "tiktok",
            "followers": int(parts[3]) if len(parts) > 3 else 0,
            "avg_views": int(parts[4]) if len(parts) > 4 else 0,
            "avg_likes": int(parts[5]) if len(parts) > 5 else 0,
        })

    if not acct_list:
        click.echo("No accounts specified. Use --account name:niche:platform:followers:avg_views:avg_likes", err=True)
        sys.exit(1)

    result = opt.generate_report(acct_list)
    _save_output(result, output_file)
    output(result, f"Multi-Account Optimization Report ({len(acct_list)} accounts)")


# ============================================================================
# Theme page group
# ============================================================================

@cli.group("theme-page")
def theme_page():
    """Theme page creation, conversion, and monetization playbooks."""
    pass


@theme_page.command("list")
def theme_page_list():
    """List all available theme page niches with key metadata.

    Example:
        cli-anything-social-trends theme-page list
        cli-anything-social-trends theme-page list --json
    """
    result = tpg.list_niches()
    output(result, "Available Theme Page Niches")


@theme_page.command("guide")
@click.option("--niche", required=True,
              help="Theme page niche (e.g. luxury_lifestyle, fitness_transformation, pet_content)")
@click.option("--output-file", "-o", default=None, help="Save guide to JSON file")
def theme_page_guide(niche, output_file):
    """Get the full setup guide for a theme page niche.

    Examples:
        cli-anything-social-trends theme-page guide --niche fitness_transformation
        cli-anything-social-trends theme-page guide --niche luxury_lifestyle -o guide.json
    """
    result = tpg.get_niche_guide(niche)
    _save_output(result, output_file)
    output(result, f"Theme Page Guide: {niche}")


@theme_page.command("strategy")
@click.option("--niche", required=True, help="Your theme page niche")
@click.option("--monetization", "mon_focus", default="all",
              type=click.Choice(["affiliate", "brand-deals", "digital-products", "all"]),
              help="Monetization focus")
@click.option("--output-file", "-o", default=None, help="Save strategy to JSON file")
def theme_page_strategy(niche, mon_focus, output_file):
    """Get the conversion strategy to monetize a theme page.

    Examples:
        cli-anything-social-trends theme-page strategy --niche finance_tips --monetization affiliate
        cli-anything-social-trends theme-page strategy --niche pet_content
    """
    guide = tpg.get_niche_guide(niche)
    if "error" in guide:
        output(guide)
        return

    strategy = guide.get("conversion_strategy", {})
    if mon_focus != "all":
        # Filter monetization phases to relevant ones
        phase_filter = {
            "affiliate": ["affiliate", "link", "commission"],
            "brand-deals": ["brand", "sponsor", "deal", "partnership"],
            "digital-products": ["digital", "course", "product", "guide", "template"],
        }
        keywords = phase_filter.get(mon_focus, [])
        if keywords and strategy.get("phases"):
            for phase in strategy["phases"]:
                phase["actions"] = [
                    a for a in phase.get("actions", [])
                    if any(kw in a.lower() for kw in keywords)
                ] or phase.get("actions", [])

    result = {
        "niche": niche,
        "monetization_focus": mon_focus,
        "strategy": strategy,
        "30_day_plan": guide.get("30_day_plan", []),
    }
    _save_output(result, output_file)
    output(result, f"Theme Page Strategy: {niche}")


# ============================================================================
# Full report
# ============================================================================

@cli.command("report")
@click.option("--niches", default="fitness,finance,travel",
              help="Comma-separated list of niches to include")
@click.option("--platforms", default="tiktok,youtube",
              help="Comma-separated list of platforms")
@click.option("--include-trends", is_flag=True, default=True,
              help="Include live trend data in report")
@click.option("--output-file", "-o", default=None, help="Save full report to JSON file")
def full_report(niches, platforms, include_trends, output_file):
    """Generate a comprehensive trend + optimization report for all your accounts.

    Examples:
        cli-anything-social-trends report --niches fitness,travel,finance --platforms tiktok,youtube
        cli-anything-social-trends report --json -o full-report.json
    """
    niche_list = [n.strip() for n in niches.split(",")]
    platform_list = [p.strip() for p in platforms.split(",")]

    result = {
        "report_type": "full",
        "niches": niche_list,
        "platforms": platform_list,
    }

    if include_trends:
        click.echo("Fetching YouTube trends...", err=True)
        result["youtube_trends"] = yt.fetch_trending(category="all", max_results=20)
        click.echo("Fetching TikTok trends...", err=True)
        result["tiktok_trends"] = tt.fetch_all_trends(max_hashtags=30, max_sounds=15)

    result["account_optimizations"] = {}
    for niche in niche_list:
        result["account_optimizations"][niche] = {}
        for platform in platform_list:
            click.echo(f"Generating optimization for {niche}/{platform}...", err=True)
            result["account_optimizations"][niche][platform] = opt.optimize_account(
                niche=niche, platform=platform
            )

    result["theme_page_guides"] = {}
    theme_niche_map = {
        "fitness": "fitness_transformation",
        "finance": "finance_tips",
        "travel": "travel_destinations",
        "cooking": "aesthetic_food",
        "beauty": "motivational_quotes",
        "gaming": "tech_reviews",
    }
    for niche in niche_list:
        theme_niche = theme_niche_map.get(niche, niche)
        guide = tpg.get_niche_guide(theme_niche)
        if "error" not in guide:
            result["theme_page_guides"][niche] = guide

    _save_output(result, output_file)
    output(result, "Full Social Media Report")


# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":
    cli()
