#!/usr/bin/env python3
"""viral-trends — Agent-native CLI for scraping viral trends, optimizing accounts, and theme page strategy.

Commands:
    viral-trends fetch         Scrape YouTube/TikTok for trending videos
    viral-trends hashtags      Extract & rank trending hashtags
    viral-trends music         Identify trending music/sounds
    viral-trends analyze       Full trend analysis from saved data
    viral-trends optimize      Generate account optimization report
    viral-trends theme-page    Theme page guides and conversion playbooks
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.viral_trends.core import youtube, tiktok, analyzer, optimizer, theme_pages


_json_output = False


def out(data, message: str = ""):
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(click.style(message, fg="green", bold=True))
        _pprint(data)


def _pprint(data, indent=0):
    prefix = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{prefix}{click.style(str(k), bold=True)}:")
                _pprint(v, indent + 1)
            else:
                click.echo(f"{prefix}{click.style(str(k), bold=True)}: {v}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                click.echo(f"{prefix}[{i}]")
                _pprint(item, indent + 1)
            else:
                click.echo(f"{prefix}- {item}")
    else:
        click.echo(f"{prefix}{data}")


def err(msg: str):
    click.echo(click.style(f"Error: {msg}", fg="red"), err=True)
    sys.exit(1)


@click.group()
@click.option("--json", "json_output", is_flag=True, default=False, help="Output as JSON (agent mode)")
def cli(json_output: bool):
    """viral-trends — Viral trend scraper, account optimizer, and theme page guide."""
    global _json_output
    _json_output = json_output


# ─── FETCH ────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--platform", "-p", type=click.Choice(["youtube", "tiktok", "both"]), default="both",
              help="Platform to scrape")
@click.option("--category", "-c", default="general",
              type=click.Choice(["general", "music", "gaming", "movies", "shorts"]),
              help="YouTube content category")
@click.option("--hashtag", "-h", default=None, help="TikTok hashtag to scrape (e.g. #fitness)")
@click.option("--region", "-r", default="US", help="Region code (e.g. US, UK, AU)")
@click.option("--count", "-n", default=20, help="Number of videos to fetch per platform")
@click.option("--output", "-o", default=None, help="Save results to JSON file")
def fetch(platform, category, hashtag, region, count, output):
    """Scrape YouTube and/or TikTok for trending videos."""
    results = []

    if platform in ("youtube", "both"):
        click.echo(f"Fetching YouTube {category} trends ({region})...", err=True)
        yt_videos = youtube.fetch_trending(category=category, region=region, count=count)
        results.extend(yt_videos)
        click.echo(f"  Got {len(yt_videos)} YouTube videos", err=True)

    if platform in ("tiktok", "both"):
        if hashtag:
            click.echo(f"Fetching TikTok #{hashtag.lstrip('#')} feed...", err=True)
            tt_videos = tiktok.fetch_hashtag_feed(hashtag, count=count)
        else:
            click.echo(f"Fetching TikTok trending ({region})...", err=True)
            tt_videos = tiktok.fetch_trending(region=region, count=count)
        results.extend(tt_videos)
        click.echo(f"  Got {len(tt_videos)} TikTok videos", err=True)

    if output:
        with open(output, "w") as f:
            json.dump(results, f, indent=2, default=str)
        click.echo(f"Saved {len(results)} videos to {output}", err=True)

    out(results, f"Fetched {len(results)} trending videos")


# ─── HASHTAGS ─────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--platform", "-p", type=click.Choice(["youtube", "tiktok", "both"]), default="tiktok")
@click.option("--input", "-i", "input_file", default=None, help="Load from saved fetch JSON")
@click.option("--count", "-n", default=20, help="Number of videos to sample")
@click.option("--top", "-t", default=30, help="Number of top hashtags to return")
@click.option("--region", "-r", default="US")
def hashtags(platform, input_file, count, top, region):
    """Extract and rank trending hashtags."""
    if input_file:
        with open(input_file) as f:
            videos = json.load(f)
    else:
        videos = []
        if platform in ("youtube", "both"):
            videos.extend(youtube.fetch_trending(count=count, region=region))
        if platform in ("tiktok", "both"):
            videos.extend(tiktok.fetch_trending(count=count, region=region))

    tags = analyzer.extract_hashtags(videos, top=top)
    out(tags, f"Top {len(tags)} trending hashtags")


# ─── MUSIC ────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--platform", "-p", type=click.Choice(["youtube", "tiktok", "both"]), default="tiktok")
@click.option("--input", "-i", "input_file", default=None, help="Load from saved fetch JSON")
@click.option("--count", "-n", default=20, help="Number of videos to sample")
@click.option("--top", "-t", default=20, help="Number of top tracks to return")
@click.option("--region", "-r", default="US")
def music(platform, input_file, count, top, region):
    """Identify trending music and sounds."""
    if input_file:
        with open(input_file) as f:
            videos = json.load(f)
        tracks = analyzer.extract_music(videos, top=top)
    else:
        if platform == "tiktok":
            tracks = tiktok.fetch_music_trends(count=count)
        elif platform == "youtube":
            yt_vids = youtube.fetch_music_trends(region=region, count=count)
            tracks = analyzer.extract_music(yt_vids, top=top)
        else:
            tt_tracks = tiktok.fetch_music_trends(count=count)
            yt_vids = youtube.fetch_music_trends(region=region, count=count)
            yt_tracks = analyzer.extract_music(yt_vids, top=top // 2)
            tracks = tt_tracks[:top // 2] + yt_tracks

    out(tracks, f"Top {len(tracks)} trending tracks")


# ─── ANALYZE ──────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--input", "-i", "input_file", required=True, help="Path to saved fetch JSON")
@click.option("--output", "-o", default=None, help="Save analysis report to JSON file")
def analyze(input_file, output):
    """Full trend analysis: hashtags, music, and top content from saved data."""
    with open(input_file) as f:
        videos = json.load(f)

    report = analyzer.summarize_trends(videos)

    if output:
        with open(output, "w") as f:
            json.dump(report, f, indent=2, default=str)
        click.echo(f"Saved analysis to {output}", err=True)

    out(report, "Trend Analysis Report")


# ─── OPTIMIZE ─────────────────────────────────────────────────────────────────

@cli.group()
def optimize():
    """Account optimization tools."""
    pass


@optimize.command("account")
@click.option("--profile", "-f", required=True, help="Path to account profile JSON")
@click.option("--trends", "-t", default=None, help="Path to trend data JSON for trend-based recommendations")
@click.option("--output", "-o", default=None, help="Save report to JSON file")
def optimize_account(profile, trends, output):
    """Generate optimization report for an account."""
    with open(profile) as f:
        account_data = json.load(f)

    trend_data = None
    if trends:
        with open(trends) as f:
            trend_data = json.load(f)

    if isinstance(account_data, list):
        report = optimizer.optimize_multiple(account_data, trend_data)
    else:
        report = optimizer.generate_account_report(account_data, trend_data)

    if output:
        with open(output, "w") as f:
            json.dump(report, f, indent=2, default=str)
        click.echo(f"Saved optimization report to {output}", err=True)

    out(report, "Account Optimization Report")


@optimize.command("template")
@click.option("--output", "-o", default=None, help="Save template to JSON file")
def optimize_template(output):
    """Generate an empty account profile template."""
    template = optimizer.generate_template()
    if output:
        with open(output, "w") as f:
            json.dump(template, f, indent=2)
        click.echo(f"Saved template to {output}", err=True)
    out(template, "Account Profile Template")


# ─── THEME-PAGE ───────────────────────────────────────────────────────────────

@cli.group("theme-page")
def theme_page():
    """Theme page creation, conversion, and growth playbooks."""
    pass


@theme_page.command("niches")
def tp_niches():
    """List all high-converting niches with monetization metrics."""
    result = theme_pages.list_niches()
    out(result, "High-Converting Niches")


@theme_page.command("guide")
@click.argument("niche")
def tp_guide(niche: str):
    """Full guide for a converting niche (e.g. fitness, finance, tech)."""
    result = theme_pages.get_niche_guide(niche)
    if "error" in result:
        err(result["error"] + f"\nAvailable: {', '.join(result['available'])}")
    out(result, f"Theme Page Guide: {niche.title()}")


@theme_page.command("convert")
def tp_convert():
    """Step-by-step personal → theme page conversion playbook."""
    result = theme_pages.get_conversion_guide()
    out(result, "Personal → Theme Page Conversion Playbook")


@theme_page.command("phases")
def tp_phases():
    """Growth phases from 0 to 500K followers."""
    result = theme_pages.get_growth_phases()
    out(result, "Theme Page Growth Phases")


@theme_page.command("hooks")
def tp_hooks():
    """Viral hook formulas for theme pages."""
    out(theme_pages.HOOK_FORMULAS, "Viral Hook Formulas")


# ─── PIPELINE ─────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--platform", "-p", type=click.Choice(["youtube", "tiktok", "both"]), default="both")
@click.option("--profile", "-f", required=True, help="Account profile JSON path")
@click.option("--region", "-r", default="US")
@click.option("--count", "-n", default=20)
@click.option("--output", "-o", default=None, help="Save full pipeline report")
def pipeline(platform, profile, region, count, output):
    """Run full pipeline: fetch trends → analyze → optimize account in one shot."""
    click.echo("Running full viral trends pipeline...", err=True)

    videos = []
    if platform in ("youtube", "both"):
        yt = youtube.fetch_trending(region=region, count=count)
        videos.extend(yt)
        click.echo(f"  YouTube: {len(yt)} videos", err=True)

    if platform in ("tiktok", "both"):
        tt = tiktok.fetch_trending(region=region, count=count)
        videos.extend(tt)
        click.echo(f"  TikTok: {len(tt)} videos", err=True)

    trend_summary = analyzer.summarize_trends(videos)

    with open(profile) as f:
        account_data = json.load(f)

    if isinstance(account_data, list):
        account_reports = optimizer.optimize_multiple(account_data, videos)
    else:
        account_reports = optimizer.generate_account_report(account_data, videos)

    report = {
        "trend_summary": trend_summary,
        "account_optimization": account_reports,
        "raw_video_count": len(videos),
    }

    if output:
        with open(output, "w") as f:
            json.dump(report, f, indent=2, default=str)
        click.echo(f"Saved pipeline report to {output}", err=True)

    out(report, "Full Pipeline Report")


def main():
    cli()


if __name__ == "__main__":
    main()
