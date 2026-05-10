"""social-trends CLI — agent-native viral trend intelligence for YouTube and TikTok."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import click

from cli_anything.social_trends.scrapers.youtube import scrape_youtube_trending, CATEGORIES, REGION_CODES
from cli_anything.social_trends.scrapers.tiktok import scrape_tiktok_trending, scrape_tiktok_hashtag
from cli_anything.social_trends.analyzers.trends import (
    analyze_hashtags,
    analyze_trending_music,
    analyze_topics,
    generate_full_report,
)
from cli_anything.social_trends.optimizers.account import generate_account_optimization, PLATFORMS
from cli_anything.social_trends.theme_pages.guide import generate_theme_page_guide, PROFITABLE_NICHES


def _out(data: Any, output: str | None, pretty: bool = True) -> None:
    """Write JSON result to file or stdout."""
    text = json.dumps(data, indent=2 if pretty else None, ensure_ascii=False)
    if output:
        Path(output).write_text(text, encoding="utf-8")
        click.echo(f"Saved to {output}", err=True)
    else:
        click.echo(text)


def _load_json(path: str, label: str) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as e:
        raise click.ClickException(f"Cannot load {label} from {path}: {e}")


@click.group()
@click.version_option("1.0.0", prog_name="social-trends")
def main() -> None:
    """
    social-trends — viral trend intelligence CLI for YouTube & TikTok.

    Commands:

    \b
      scrape    Fetch trending content from YouTube or TikTok
      analyze   Analyze trends for hashtags, music, and topics
      optimize  Generate account optimization plan
      report    Full trend intelligence report (scrape + analyze in one shot)
      theme     Theme page creation and conversion playbook

    Quick start (no API key needed):

    \b
      social-trends scrape youtube --region US --limit 25 -o yt.json
      social-trends scrape tiktok --region US -o tt.json
      social-trends report --youtube-data yt.json --tiktok-data tt.json -o report.json
      social-trends optimize --platform all --niche finance --followers 5000
      social-trends theme --niche finance
    """


# ---------------------------------------------------------------------------
# scrape
# ---------------------------------------------------------------------------

@main.group()
def scrape() -> None:
    """Fetch trending content from YouTube or TikTok."""


@scrape.command("youtube")
@click.option("--region", "-r", default="US", show_default=True,
              help=f"Region code. Options: {', '.join(REGION_CODES.keys())}")
@click.option("--category", "-c", default="all", show_default=True,
              help=f"Video category. Options: {', '.join(CATEGORIES.keys())}")
@click.option("--limit", "-n", default=25, show_default=True, type=int,
              help="Max number of trending videos to fetch (1–50)")
@click.option("--api-key", envvar="YOUTUBE_API_KEY",
              help="YouTube Data API v3 key. Falls back to innertube if not set. Env: YOUTUBE_API_KEY")
@click.option("--output", "-o", default=None,
              help="Path to write JSON output. Defaults to stdout.")
@click.option("--compact", is_flag=True, help="Compact JSON output (no indentation)")
def scrape_youtube(region: str, category: str, limit: int, api_key: str | None, output: str | None, compact: bool) -> None:
    """
    Fetch YouTube trending videos.

    \b
    Examples:
      social-trends scrape youtube
      social-trends scrape youtube --region US --category music --limit 50
      social-trends scrape youtube --api-key YOUR_KEY -o yt_trending.json
    """
    try:
        click.echo(f"Fetching YouTube trending [{region.upper()} / {category}]...", err=True)
        data = scrape_youtube_trending(region=region, category=category, limit=limit, api_key=api_key)
        click.echo(f"Found {data['total']} videos (source: {data['source']})", err=True)
        _out(data, output, pretty=not compact)
    except Exception as e:
        raise click.ClickException(str(e))


@scrape.command("tiktok")
@click.option("--region", "-r", default="US", show_default=True,
              help="Region code (US, GB, CA, AU, IN, BR, DE, FR, JP, KR)")
@click.option("--limit", "-n", default=25, show_default=True, type=int,
              help="Max number of videos to include")
@click.option("--output", "-o", default=None,
              help="Path to write JSON output. Defaults to stdout.")
@click.option("--compact", is_flag=True, help="Compact JSON output")
def scrape_tiktok(region: str, limit: int, output: str | None, compact: bool) -> None:
    """
    Fetch TikTok trending videos, hashtags, and sounds.

    \b
    Examples:
      social-trends scrape tiktok
      social-trends scrape tiktok --region US --limit 50 -o tt_trending.json
    """
    try:
        click.echo(f"Fetching TikTok trending [{region.upper()}]...", err=True)
        data = scrape_tiktok_trending(region=region, limit=limit)
        click.echo(
            f"Found {data['total_videos']} videos, "
            f"{data['total_hashtags']} hashtags, "
            f"{data['total_sounds']} sounds",
            err=True,
        )
        _out(data, output, pretty=not compact)
    except Exception as e:
        raise click.ClickException(str(e))


@scrape.command("hashtag")
@click.argument("hashtag")
@click.option("--limit", "-n", default=20, show_default=True, type=int)
@click.option("--output", "-o", default=None)
def scrape_hashtag(hashtag: str, limit: int, output: str | None) -> None:
    """
    Fetch TikTok videos for a specific HASHTAG challenge.

    \b
    Examples:
      social-trends scrape hashtag fyp
      social-trends scrape hashtag fitness --limit 50 -o fitness_tag.json
    """
    try:
        tag = hashtag.lstrip("#")
        click.echo(f"Fetching TikTok #{tag} content...", err=True)
        data = scrape_tiktok_hashtag(tag, limit=limit)
        _out(data, output)
    except Exception as e:
        raise click.ClickException(str(e))


# ---------------------------------------------------------------------------
# analyze
# ---------------------------------------------------------------------------

@main.group()
def analyze() -> None:
    """Analyze scraped trend data for actionable insights."""


@analyze.command("hashtags")
@click.option("--youtube-data", "-y", default=None,
              help="Path to JSON from 'scrape youtube'")
@click.option("--tiktok-data", "-t", default=None,
              help="Path to JSON from 'scrape tiktok'")
@click.option("--output", "-o", default=None)
def analyze_hashtags_cmd(youtube_data: str | None, tiktok_data: str | None, output: str | None) -> None:
    """
    Cross-platform hashtag analysis (YouTube + TikTok combined).

    \b
    Examples:
      social-trends analyze hashtags --youtube-data yt.json --tiktok-data tt.json
      social-trends analyze hashtags --tiktok-data tt.json -o hashtags.json
    """
    yt = _load_json(youtube_data, "YouTube data") if youtube_data else None
    tt = _load_json(tiktok_data, "TikTok data") if tiktok_data else None
    if not yt and not tt:
        raise click.ClickException("Provide at least one of --youtube-data or --tiktok-data")
    result = analyze_hashtags(yt, tt)
    _out(result, output)


@analyze.command("music")
@click.option("--tiktok-data", "-t", required=True,
              help="Path to JSON from 'scrape tiktok'")
@click.option("--output", "-o", default=None)
def analyze_music_cmd(tiktok_data: str, output: str | None) -> None:
    """
    Trending music/sound analysis from TikTok data.

    \b
    Example:
      social-trends analyze music --tiktok-data tt.json -o music.json
    """
    tt = _load_json(tiktok_data, "TikTok data")
    result = analyze_trending_music(tt)
    _out(result, output)


@analyze.command("topics")
@click.option("--youtube-data", "-y", default=None)
@click.option("--tiktok-data", "-t", default=None)
@click.option("--output", "-o", default=None)
def analyze_topics_cmd(youtube_data: str | None, tiktok_data: str | None, output: str | None) -> None:
    """
    Trending topic and content angle extraction.

    \b
    Example:
      social-trends analyze topics --youtube-data yt.json --tiktok-data tt.json
    """
    yt = _load_json(youtube_data, "YouTube data") if youtube_data else None
    tt = _load_json(tiktok_data, "TikTok data") if tiktok_data else None
    if not yt and not tt:
        raise click.ClickException("Provide at least one of --youtube-data or --tiktok-data")
    result = analyze_topics(yt, tt)
    _out(result, output)


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------

@main.command()
@click.option("--youtube-data", "-y", default=None,
              help="Path to JSON from 'scrape youtube'. If omitted, scrape is run automatically.")
@click.option("--tiktok-data", "-t", default=None,
              help="Path to JSON from 'scrape tiktok'. If omitted, scrape is run automatically.")
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--youtube-api-key", envvar="YOUTUBE_API_KEY", default=None)
@click.option("--limit", "-n", default=25, show_default=True, type=int)
@click.option("--output", "-o", default=None)
def report(
    youtube_data: str | None,
    tiktok_data: str | None,
    region: str,
    youtube_api_key: str | None,
    limit: int,
    output: str | None,
) -> None:
    """
    Full trend intelligence report — scrape + analyze in one command.

    Automatically fetches YouTube and TikTok data if not pre-supplied,
    then generates a unified hashtag + music + topic + action plan report.

    \b
    Examples:
      social-trends report -o full_report.json
      social-trends report --region GB --limit 50 -o uk_report.json
      social-trends report --youtube-data yt.json --tiktok-data tt.json -o report.json
    """
    yt: dict | None = None
    tt: dict | None = None

    if youtube_data:
        yt = _load_json(youtube_data, "YouTube data")
    else:
        try:
            click.echo(f"Auto-fetching YouTube trending [{region.upper()}]...", err=True)
            yt = scrape_youtube_trending(region=region, limit=limit, api_key=youtube_api_key)
            click.echo(f"YouTube: {yt['total']} videos (source: {yt['source']})", err=True)
        except Exception as e:
            click.echo(f"YouTube fetch failed: {e} — continuing without YouTube data", err=True)

    if tiktok_data:
        tt = _load_json(tiktok_data, "TikTok data")
    else:
        try:
            click.echo(f"Auto-fetching TikTok trending [{region.upper()}]...", err=True)
            tt = scrape_tiktok_trending(region=region, limit=limit)
            click.echo(
                f"TikTok: {tt['total_videos']} videos, {tt['total_hashtags']} hashtags, {tt['total_sounds']} sounds",
                err=True,
            )
        except Exception as e:
            click.echo(f"TikTok fetch failed: {e} — continuing without TikTok data", err=True)

    if not yt and not tt:
        raise click.ClickException("Both YouTube and TikTok fetches failed. Check network connectivity.")

    click.echo("Analyzing trends...", err=True)
    result = generate_full_report(yt, tt)
    result["meta"] = {
        "region": region,
        "youtube_source": yt.get("source") if yt else None,
        "tiktok_source": tt.get("source") if tt else None,
        "youtube_videos": yt.get("total", 0) if yt else 0,
        "tiktok_videos": tt.get("total_videos", 0) if tt else 0,
    }

    click.echo("Report complete.", err=True)
    _out(result, output)


# ---------------------------------------------------------------------------
# optimize
# ---------------------------------------------------------------------------

@main.command()
@click.option("--platform", "-p", default="all", show_default=True,
              type=click.Choice(PLATFORMS, case_sensitive=False),
              help="Target platform(s)")
@click.option("--niche", "-n", default="", help="Content niche (e.g., finance, fitness, beauty, gaming)")
@click.option("--followers", "-f", default=0, type=int,
              help="Current follower count (used to determine growth phase advice)")
@click.option("--trend-report", "-t", default=None,
              help="Path to JSON from 'report' command — enables trend-specific tips")
@click.option("--output", "-o", default=None)
def optimize(
    platform: str,
    niche: str,
    followers: int,
    trend_report: str | None,
    output: str | None,
) -> None:
    """
    Generate a personalized account optimization plan.

    Outputs platform specs, growth strategy, hashtag formula, content calendar,
    bio templates, and monetization roadmap based on your current stage.

    \b
    Examples:
      social-trends optimize --platform tiktok --niche fitness --followers 5000
      social-trends optimize --platform all --niche finance
      social-trends optimize --niche gaming --trend-report report.json -o plan.json
    """
    trend_data = _load_json(trend_report, "trend report") if trend_report else None
    result = generate_account_optimization(
        platform=platform,
        niche=niche,
        follower_count=followers,
        trend_data=trend_data,
    )
    _out(result, output)


# ---------------------------------------------------------------------------
# theme
# ---------------------------------------------------------------------------

@main.command()
@click.option("--niche", "-n", default="",
              help=f"Content niche. Top options: {', '.join(list(PROFITABLE_NICHES.keys())[:6])}, ...")
@click.option("--followers", "-f", default=0, type=int,
              help="Current follower count (0 = starting fresh)")
@click.option("--platform", "-p", default="all",
              help="Target platform(s)")
@click.option("--list-niches", is_flag=True,
              help="List all profitable niches ranked by revenue potential")
@click.option("--output", "-o", default=None)
def theme(
    niche: str,
    followers: int,
    platform: str,
    list_niches: bool,
    output: str | None,
) -> None:
    """
    Theme page creation, conversion, and monetization playbook.

    A theme page (niche page) curates/reposts content around a topic.
    This command outputs: niche ranking, SOP phases, monetization paths,
    tool list, legal notes, and a conversion checklist.

    \b
    Examples:
      social-trends theme --list-niches
      social-trends theme --niche finance
      social-trends theme --niche fitness --followers 5000 -o fitness_plan.json
      social-trends theme --niche motivation --platform tiktok
    """
    result = generate_theme_page_guide(
        niche=niche,
        current_followers=followers,
        target_platform=platform,
    )
    if list_niches:
        # Just show the ranking table
        result = {"top_niches_by_profit": result["top_10_niches_by_profit"]}
    _out(result, output)


# ---------------------------------------------------------------------------
# __main__
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()
