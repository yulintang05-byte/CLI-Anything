#!/usr/bin/env python3
"""TrendScraper CLI — scrape viral trends, optimize accounts, and build converting theme pages.

Usage:
    # Scrape YouTube trending videos
    trendscraper scrape youtube --region US --limit 50

    # Scrape TikTok trending hashtags
    trendscraper scrape tiktok --region US --limit 30

    # Fetch all trends cross-platform
    trendscraper scrape all --region US --output trends.json

    # Generate full trend report
    trendscraper trends report --region US --output report.json

    # Show trending hashtags
    trendscraper trends hashtags --platform all

    # Show trending music
    trendscraper trends music --platform tiktok

    # Optimize a caption with trending hashtags
    trendscraper optimize caption --text "My workout routine" --platform instagram --niche fitness

    # Generate a 7-day content calendar
    trendscraper optimize calendar --niche motivation --platform tiktok --days 7

    # Analyze account health
    trendscraper optimize account --platform tiktok --followers 5000 --avg-views 1200 --niche fitness

    # Theme page niche analysis
    trendscraper theme niche --name luxury

    # Compare all niches
    trendscraper theme compare

    # Get monetization strategy
    trendscraper theme monetize --method affiliate

    # Get growth playbook
    trendscraper theme playbook --platform instagram

    # Full page-flip roadmap
    trendscraper theme flip --niche luxury --platform tiktok --target 50000

    # Configure API keys
    trendscraper config set --youtube-api-key KEY
    trendscraper config set --tiktok-token TOKEN
    trendscraper config show

    # Interactive REPL
    trendscraper repl
"""

import sys
import os
import json
import click
from typing import Optional
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.trendscraper.core import youtube as yt_mod
from cli_anything.trendscraper.core import tiktok as tt_mod
from cli_anything.trendscraper.core import trends as trends_mod
from cli_anything.trendscraper.core import optimizer as opt_mod
from cli_anything.trendscraper.core import theme_pages as theme_mod

_json_output = False
_CONFIG_FILE = Path.home() / ".config" / "cli-anything-trendscraper" / "config.json"


def output(data, message: str = ""):
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.secho(message, fg="cyan", bold=True)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)
        else:
            click.echo(str(data))


def _print_dict(d: dict, indent: int = 0):
    prefix = "  " * indent
    for k, v in d.items():
        if k.startswith("_"):
            continue
        if isinstance(v, dict):
            click.echo(f"{prefix}{click.style(k, fg='yellow')}:")
            _print_dict(v, indent + 1)
        elif isinstance(v, list):
            click.echo(f"{prefix}{click.style(k, fg='yellow')}:")
            _print_list(v, indent + 1)
        else:
            click.echo(f"{prefix}{click.style(k, fg='yellow')}: {v}")


def _print_list(items: list, indent: int = 0):
    prefix = "  " * indent
    for i, item in enumerate(items):
        if isinstance(item, dict):
            click.echo(f"{prefix}[{i}]")
            _print_dict(item, indent + 1)
        else:
            click.echo(f"{prefix}- {item}")


def _load_config() -> dict:
    if _CONFIG_FILE.exists():
        return json.loads(_CONFIG_FILE.read_text())
    return {}


def _save_config(cfg: dict) -> None:
    _CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    _CONFIG_FILE.write_text(json.dumps(cfg, indent=2))


# ─── Root ────────────────────────────────────────────────────────────────────

@click.group()
@click.option("--json", "json_out", is_flag=True, default=False, help="Output in JSON format")
@click.version_option("1.0.0", prog_name="trendscraper")
def main(json_out: bool):
    """TrendScraper — viral trends, hashtag intelligence, and social media optimization."""
    global _json_output
    _json_output = json_out


# ─── Config ───────────────────────────────────────────────────────────────────

@main.group()
def config():
    """Manage API keys and settings."""


@config.command("set")
@click.option("--youtube-api-key", default=None, help="YouTube Data API v3 key")
@click.option("--tiktok-token", default=None, help="TikTok Research API access token")
def config_set(youtube_api_key: str | None, tiktok_token: str | None):
    """Save API credentials to local config."""
    cfg = _load_config()
    if youtube_api_key:
        cfg["youtube_api_key"] = youtube_api_key
        click.secho("YouTube API key saved.", fg="green")
    if tiktok_token:
        cfg["tiktok_access_token"] = tiktok_token
        click.secho("TikTok access token saved.", fg="green")
    if not youtube_api_key and not tiktok_token:
        click.secho("No values provided. Use --youtube-api-key and/or --tiktok-token.", fg="yellow")
        return
    _save_config(cfg)
    click.echo(f"Config saved to {_CONFIG_FILE}")


@config.command("show")
def config_show():
    """Show current configuration (redacted)."""
    cfg = _load_config()
    display = {}
    for k, v in cfg.items():
        if "key" in k.lower() or "token" in k.lower() or "secret" in k.lower():
            display[k] = f"{str(v)[:8]}..." if v else "(not set)"
        else:
            display[k] = v
    output(display, "Current Configuration")
    if not cfg:
        click.echo("No config found. Use: trendscraper config set --youtube-api-key KEY")


# ─── Scrape ───────────────────────────────────────────────────────────────────

@main.group()
def scrape():
    """Scrape viral trends from YouTube and TikTok."""


@scrape.command("youtube")
@click.option("--region", default="US", show_default=True, help="Region code (US, GB, AU, CA, IN, etc.)")
@click.option("--category", default="", help="YouTube category ID (10=Music, 20=Gaming, 24=Entertainment)")
@click.option("--limit", default=50, show_default=True, type=int, help="Max videos to fetch")
@click.option("--output", default=None, help="Save results to JSON file")
@click.option("--api-key", default=None, envvar="YOUTUBE_API_KEY", help="YouTube Data API key")
def scrape_youtube(region: str, category: str, limit: int, output: str | None, api_key: str | None):
    """Fetch trending YouTube videos, hashtags, and music."""
    click.secho(f"Scraping YouTube trending [{region}]...", fg="cyan")
    result = yt_mod.fetch_trending_videos(
        region=region.upper(),
        category_id=category,
        max_results=limit,
        api_key=api_key,
    )
    if output:
        Path(output).write_text(json.dumps(result, indent=2, default=str))
        click.secho(f"Saved to {output}", fg="green")
    else:
        _display_youtube_result(result)


@scrape.command("tiktok")
@click.option("--region", default="US", show_default=True, help="Region code")
@click.option("--limit", default=30, show_default=True, type=int, help="Max trends to fetch")
@click.option("--output", default=None, help="Save results to JSON file")
@click.option("--token", default=None, envvar="TIKTOK_ACCESS_TOKEN", help="TikTok Research API token")
def scrape_tiktok(region: str, limit: int, output: str | None, token: str | None):
    """Fetch trending TikTok hashtags and sounds."""
    click.secho(f"Scraping TikTok trending [{region}]...", fg="cyan")
    result = tt_mod.fetch_trending_hashtags(region=region.upper(), limit=limit, token=token)
    if output:
        Path(output).write_text(json.dumps(result, indent=2, default=str))
        click.secho(f"Saved to {output}", fg="green")
    else:
        _display_tiktok_result(result)


@scrape.command("all")
@click.option("--region", default="US", show_default=True, help="Region code")
@click.option("--limit", default=50, show_default=True, type=int)
@click.option("--output", default=None, help="Save JSON to file")
def scrape_all(region: str, limit: int, output: str | None):
    """Scrape YouTube + TikTok and merge all trends."""
    click.secho(f"Scraping all platforms [{region}]...", fg="cyan")
    result = trends_mod.fetch_all_trends(region=region.upper(), max_results=limit)
    if output:
        Path(output).write_text(json.dumps(result, indent=2, default=str))
        click.secho(f"Saved to {output}", fg="green")
    else:
        _display_all_trends(result)


# ─── Trends ───────────────────────────────────────────────────────────────────

@main.group()
def trends():
    """Analyze and display trends across platforms."""


@trends.command("report")
@click.option("--region", default="US", show_default=True)
@click.option("--output", default=None, help="Save report to JSON file")
@click.option("--csv", "csv_output", default=None, help="Also export hashtags to CSV")
def trends_report(region: str, output: str | None, csv_output: str | None):
    """Generate a full cross-platform viral trend report."""
    click.secho(f"Generating trend report [{region}]...", fg="cyan")
    report = trends_mod.generate_trend_report(region=region.upper(), output_file=output)
    if csv_output:
        trends_mod.save_trends_csv(report["trends"], csv_output)
        click.secho(f"CSV saved to {csv_output}", fg="green")
    if output:
        click.secho(f"Report saved to {output}", fg="green")
    _display_report(report)


@trends.command("hashtags")
@click.option("--platform", default="all", type=click.Choice(["all", "youtube", "tiktok"]))
@click.option("--region", default="US", show_default=True)
@click.option("--top", default=20, show_default=True, type=int, help="Number of hashtags to show")
def trends_hashtags(platform: str, region: str, top: int):
    """Show top trending hashtags."""
    if platform == "youtube":
        data = yt_mod.fetch_trending_videos(region=region.upper())
        hashtags = data.get("trending_hashtags", [])[:top]
    elif platform == "tiktok":
        data = tt_mod.fetch_trending_hashtags(region=region.upper())
        hashtags = data.get("trending_hashtags", [])[:top]
    else:
        data = trends_mod.fetch_all_trends(region=region.upper())
        hashtags = data.get("trending_hashtags", [])[:top]

    click.secho(f"\nTop {top} trending hashtags [{platform.upper()} / {region}]", fg="cyan", bold=True)
    click.echo("─" * 50)
    for i, h in enumerate(hashtags, 1):
        tag = h.get("tag", "")
        score = h.get("score", h.get("count", 0))
        platforms = h.get("platforms", [])
        platform_badge = f" [{', '.join(platforms)}]" if platforms else ""
        click.echo(f"  {i:2}. #{tag:<30} score: {score}{platform_badge}")


@trends.command("music")
@click.option("--platform", default="all", type=click.Choice(["all", "youtube", "tiktok"]))
@click.option("--region", default="US", show_default=True)
@click.option("--top", default=20, show_default=True, type=int)
def trends_music(platform: str, region: str, top: int):
    """Show trending music and sounds."""
    if platform == "youtube":
        data = yt_mod.fetch_trending_music(region=region.upper())
        music = data.get("trending_music", [])[:top]
        label = "YouTube"
    elif platform == "tiktok":
        data = tt_mod.fetch_trending_sounds(region=region.upper())
        music = data.get("trending_sounds", [])[:top]
        label = "TikTok"
    else:
        data = trends_mod.fetch_all_trends(region=region.upper())
        music = data.get("trending_music", [])[:top]
        label = "All Platforms"

    click.secho(f"\nTop {top} trending music [{label} / {region}]", fg="cyan", bold=True)
    click.echo("─" * 50)
    for i, m in enumerate(music, 1):
        title = m.get("title", m.get("title", "Unknown"))
        count = m.get("count", m.get("tt_count", 0))
        click.echo(f"  {i:2}. {title} (×{count})")


# ─── Optimize ─────────────────────────────────────────────────────────────────

@main.group()
def optimize():
    """Optimize captions, schedules, and account strategy."""


@optimize.command("caption")
@click.option("--text", default="", help="Your post text")
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok", "instagram", "youtube", "twitter", "youtube_shorts"]))
@click.option("--niche", default="generic", help="Your niche (motivation, luxury, fitness, finance, etc.)")
@click.option("--region", default="US", show_default=True)
@click.option("--max-hashtags", default=None, type=int, help="Override max hashtag count")
def optimize_caption(text: str, platform: str, niche: str, region: str, max_hashtags: int | None):
    """Generate an optimized caption with trending hashtags."""
    click.secho("Fetching trending hashtags for caption optimization...", fg="cyan")
    trend_data = trends_mod.fetch_all_trends(region=region.upper(), max_results=30)
    trending_tags = [h["tag"] for h in trend_data.get("trending_hashtags", [])[:15]]

    result = opt_mod.optimize_caption(
        text=text,
        platform=platform,
        niche=niche,
        trending_hashtags=trending_tags,
        max_hashtags=max_hashtags,
    )
    output(result, f"Optimized Caption [{platform.upper()} / {niche}]")


@optimize.command("calendar")
@click.option("--niche", default="motivation", help="Your content niche")
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]))
@click.option("--days", default=7, show_default=True, type=int, help="Number of days to plan")
@click.option("--region", default="US", show_default=True)
@click.option("--output", default=None, help="Save calendar to JSON file")
def optimize_calendar(niche: str, platform: str, days: int, region: str, output: str | None):
    """Generate a content calendar with post ideas and optimal times."""
    trend_data = trends_mod.fetch_all_trends(region=region.upper(), max_results=30)
    trending_tags = [h["tag"] for h in trend_data.get("trending_hashtags", [])[:10]]

    calendar = opt_mod.generate_content_calendar(
        niche=niche,
        platform=platform,
        days=days,
        trending_hashtags=trending_tags,
    )
    if output:
        Path(output).write_text(json.dumps(calendar, indent=2, default=str))
        click.secho(f"Calendar saved to {output}", fg="green")
    output_data = calendar
    _display_calendar(output_data)


@optimize.command("account")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]))
@click.option("--followers", default=0, type=int, help="Current follower count")
@click.option("--avg-views", default=0, type=int, help="Average views per post")
@click.option("--avg-likes", default=0, type=int, help="Average likes per post")
@click.option("--niche", default="generic", help="Account niche")
@click.option("--posting-frequency", default="daily", type=click.Choice(["daily", "twice_daily", "weekly", "sporadic"]))
def optimize_account(platform: str, followers: int, avg_views: int, avg_likes: int, niche: str, posting_frequency: str):
    """Analyze account health and get optimization recommendations."""
    result = opt_mod.analyze_account(
        platform=platform,
        followers=followers,
        avg_views=avg_views,
        avg_likes=avg_likes,
        niche=niche,
        posting_frequency=posting_frequency,
    )
    output(result, f"Account Analysis [{platform.upper()} / {niche}]")


@optimize.command("times")
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]))
def optimize_times(platform: str):
    """Show optimal posting times for a platform."""
    schedule = opt_mod.OPTIMAL_POST_TIMES.get(platform, [])
    click.secho(f"\nOptimal Posting Times [{platform.upper()}]", fg="cyan", bold=True)
    click.echo("─" * 50)
    for slot in schedule:
        hours = ", ".join(f"{h}:00 UTC" for h in slot["hours"])
        click.echo(f"  {slot['day']:<12}: {hours}  — {slot['note']}")


# ─── Theme ────────────────────────────────────────────────────────────────────

@main.group()
def theme():
    """Theme page strategy: niches, growth, monetization, and page flipping."""


@theme.command("niche")
@click.option("--name", required=True, help="Niche to analyze (luxury, fitness, finance, etc.)")
def theme_niche(name: str):
    """Deep-dive analysis of a specific niche."""
    result = theme_mod.get_niche_analysis(name)
    output(result, f"Niche Analysis: {name.title()}")


@theme.command("compare")
@click.option("--niches", default=None, help="Comma-separated niches to compare (default: all)")
def theme_compare(niches: str | None):
    """Compare multiple niches side-by-side."""
    niche_list = [n.strip() for n in niches.split(",")] if niches else None
    result = theme_mod.compare_niches(niche_list)
    _display_niche_comparison(result)


@theme.command("monetize")
@click.option("--method", required=True, type=click.Choice(list(theme_mod.MONETIZATION_METHODS.keys())))
def theme_monetize(method: str):
    """Get detailed guide for a monetization method."""
    result = theme_mod.get_monetization_strategy(method)
    output(result, f"Monetization Strategy: {method.replace('_', ' ').title()}")


@theme.command("playbook")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]))
def theme_playbook(platform: str):
    """Get growth playbook for a platform."""
    result = theme_mod.get_growth_playbook(platform)
    _display_playbook(result)


@theme.command("flip")
@click.option("--niche", default="luxury", help="Page niche")
@click.option("--platform", default="instagram", type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]))
@click.option("--target", default=50_000, type=int, help="Target follower count before selling")
@click.option("--budget", default=0, type=int, help="Starting budget in USD")
@click.option("--output", default=None, help="Save roadmap to JSON")
def theme_flip(niche: str, platform: str, target: int, budget: int, output: str | None):
    """Generate a full page-flip roadmap: build → grow → sell."""
    result = theme_mod.page_flip_roadmap(
        niche=niche,
        platform=platform,
        target_followers=target,
        starting_budget_usd=budget,
    )
    if output:
        Path(output).write_text(json.dumps(result, indent=2, default=str))
        click.secho(f"Roadmap saved to {output}", fg="green")
    _display_flip_roadmap(result)


@theme.command("strategies")
def theme_strategies():
    """List all available strategies, niches, and monetization methods."""
    result = theme_mod.list_all_strategies()
    if _json_output:
        output(result)
    else:
        _display_all_strategies(result)


# ─── REPL ─────────────────────────────────────────────────────────────────────

@main.command("repl")
def repl():
    """Start interactive REPL for TrendScraper."""
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    import shlex

    click.secho("TrendScraper REPL — type 'help' for commands, 'exit' to quit", fg="cyan", bold=True)
    session: PromptSession = PromptSession(history=InMemoryHistory(), auto_suggest=AutoSuggestFromHistory())

    while True:
        try:
            raw = session.prompt("trendscraper> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw:
            continue
        if raw.lower() in ("exit", "quit", "q"):
            break
        if raw.lower() == "help":
            click.echo(main.get_help(click.Context(main)))
            continue
        try:
            args = shlex.split(raw)
            main.main(args, standalone_mode=False)
        except SystemExit:
            pass
        except Exception as e:
            click.secho(f"Error: {e}", fg="red")

    click.secho("Goodbye!", fg="green")


# ─── Display helpers ──────────────────────────────────────────────────────────

def _display_youtube_result(data: dict):
    click.secho(f"\nYouTube Trending [{data.get('region')}] — {data.get('video_count', 0)} videos", fg="cyan", bold=True)
    click.echo(f"Source: {data.get('source')} | Fetched: {data.get('fetched_at', '')[:16]}")
    click.echo()

    hashtags = data.get("trending_hashtags", [])[:15]
    if hashtags:
        click.secho("Top Hashtags:", fg="yellow")
        for i, h in enumerate(hashtags, 1):
            click.echo(f"  {i:2}. #{h['tag']} (×{h['count']})")

    music = data.get("trending_music", [])[:10]
    if music:
        click.echo()
        click.secho("Trending Music:", fg="yellow")
        for i, m in enumerate(music, 1):
            click.echo(f"  {i:2}. {m['title']}")

    videos = data.get("videos", [])[:5]
    if videos:
        click.echo()
        click.secho("Top 5 Videos:", fg="yellow")
        for v in videos:
            views = f"{v.get('views', 0):,}" if v.get("views") else v.get("views_raw", "?")
            click.echo(f"  • {v.get('title', '')[:60]} — {v.get('channel', '')} — {views} views")


def _display_tiktok_result(data: dict):
    click.secho(f"\nTikTok Trending [{data.get('region')}]", fg="cyan", bold=True)
    click.echo(f"Source: {data.get('source')} | Fetched: {data.get('fetched_at', '')[:16]}")
    click.echo()

    hashtags = data.get("trending_hashtags", [])[:15]
    if hashtags:
        click.secho("Top Hashtags:", fg="yellow")
        for i, h in enumerate(hashtags, 1):
            click.echo(f"  {i:2}. #{h['tag']} (×{h['count']})")

    sounds = data.get("trending_sounds", [])[:10]
    if sounds:
        click.echo()
        click.secho("Trending Sounds:", fg="yellow")
        for i, s in enumerate(sounds, 1):
            click.echo(f"  {i:2}. {s['title']} (×{s['count']})")

    if not hashtags and not sounds:
        click.secho("\nNo live data retrieved. Set TIKTOK_ACCESS_TOKEN for Research API access.", fg="yellow")
        click.echo("Or use: trendscraper config set --tiktok-token TOKEN")


def _display_all_trends(data: dict):
    summary = data.get("executive_summary") or data
    click.secho("\nCross-Platform Trend Summary", fg="cyan", bold=True)
    click.echo("─" * 50)

    cross = data.get("cross_platform_trends", [])[:5]
    if cross:
        click.secho("Cross-Platform Viral (YouTube + TikTok):", fg="green", bold=True)
        for h in cross:
            click.echo(f"  🔥 #{h['tag']} — YT: {h['youtube_count']} / TT: {h['tiktok_count']}")

    hashtags = data.get("trending_hashtags", [])[:10]
    if hashtags:
        click.echo()
        click.secho("Top Merged Hashtags:", fg="yellow")
        for i, h in enumerate(hashtags, 1):
            click.echo(f"  {i:2}. #{h['tag']:<25} score: {h.get('score', 0):.1f}")

    music = data.get("trending_music", [])[:5]
    if music:
        click.echo()
        click.secho("Trending Music:", fg="yellow")
        for m in music:
            click.echo(f"  🎵 {m.get('title', '')}")


def _display_report(report: dict):
    click.secho(f"\n{report.get('report_title', 'Trend Report')}", fg="cyan", bold=True)
    click.echo("─" * 60)

    summary = report.get("executive_summary", {})
    click.secho("Executive Summary:", fg="green")
    for k, v in summary.items():
        click.echo(f"  {k}: {v}")

    click.echo()
    recs = report.get("recommended_hashtags", [])
    if recs:
        click.secho("Recommended Hashtags for Your Next Post:", fg="yellow")
        click.echo("  " + " ".join(recs))

    click.echo()
    actions = report.get("action_items", [])
    if actions:
        click.secho("Action Items:", fg="green", bold=True)
        for a in actions:
            click.echo(f"  → {a}")


def _display_calendar(calendar: dict):
    click.secho(f"\n{calendar.get('days', 7)}-Day Content Calendar [{calendar.get('platform', '').upper()} / {calendar.get('niche', '').title()}]", fg="cyan", bold=True)
    click.echo("─" * 60)
    for post in calendar.get("posts", []):
        priority_color = "green" if post["priority"] == "HIGH" else "yellow"
        click.secho(f"\nDay {post['day']} — {post['date']} ({post['day_name']}) [{post['priority']}]", fg=priority_color, bold=True)
        click.echo(f"  Type:    {post['content_type']}")
        click.echo(f"  Idea:    {post['post_idea']}")
        click.echo(f"  Hook:    {post['hook']}")
        click.echo(f"  Times:   {', '.join(f'{t}:00 UTC' for t in post['suggested_times_utc'])}")
        click.echo(f"  Tags:    {' '.join(post['hashtags'][:5])}")
    click.echo()
    click.secho(report if (report := calendar.get("weekly_tip")) else "", fg="cyan")


def _display_niche_comparison(data: dict):
    click.secho("\nNiche Comparison", fg="cyan", bold=True)
    click.echo("─" * 80)
    click.echo(f"{'Niche':<14} {'Score':>6}  {'Saturation':<12} {'Monetization':<12} {'CPM $':>6}  {'Growth'}")
    click.echo("─" * 80)
    for n in data.get("comparison", []):
        click.echo(
            f"  {n['niche']:<12} {n['score']:>6.1f}  {n['saturation']:<12} {n['monetization_potential']:<12} {n['avg_cpm_usd']:>6.1f}  {n['growth_speed']}"
        )
    click.echo("─" * 80)
    click.secho(f"\nTop Recommendation:      {data.get('top_recommendation', '').title()}", fg="green")
    click.secho(f"Best for Beginners:      {data.get('best_for_beginners', '').title()}", fg="yellow")
    click.secho(f"Best for Monetization:   {data.get('best_for_monetization', '').title()}", fg="yellow")


def _display_playbook(data: dict):
    click.secho(f"\nGrowth Playbook: {data.get('platform', '').upper()}", fg="cyan", bold=True)
    click.echo(f"Timeline: {data.get('estimated_timeline', '')}")
    click.echo("─" * 60)
    click.secho("\nSteps:", fg="green")
    for i, step in enumerate(data.get("steps", []), 1):
        click.echo(f"  {i:2}. {step}")
    click.echo()
    click.secho("Common Mistakes to Avoid:", fg="red")
    for m in data.get("common_mistakes", []):
        click.echo(f"  ✗ {m}")


def _display_flip_roadmap(data: dict):
    click.secho(f"\nPage Flip Roadmap: {data.get('niche', '').title()} on {data.get('platform', '').upper()}", fg="cyan", bold=True)
    click.echo("─" * 60)
    click.echo(f"  Target Followers:    {data.get('target_followers', 0):,}")
    click.echo(f"  Estimated Sale:      ${data.get('estimated_sell_value_usd', 0):,}")
    click.echo(f"  Timeline:            ~{data.get('estimated_timeline_months', 0)} months")
    click.echo(f"  ROI:                 {data.get('roi_estimate', 'N/A')}")
    click.echo()
    for phase in data.get("phases", []):
        click.secho(f"\nPhase {phase['phase']}: {phase['name']} ({phase['duration']})", fg="yellow", bold=True)
        click.echo(f"Goal: {phase['goal']}")
        for action in phase["actions"]:
            click.echo(f"  • {action}")
    valuation = data.get("valuation_guide", {})
    if valuation:
        click.echo()
        click.secho("Valuation Guide:", fg="green")
        click.echo(f"  Formula: {valuation.get('formula', '')}")


def _display_all_strategies(data: dict):
    click.secho("\nAll Available Strategies", fg="cyan", bold=True)
    click.echo("─" * 70)
    click.secho("\nNiches:", fg="yellow")
    for niche, info in data.get("available_niches", {}).items():
        click.echo(f"  {niche:<16} CPM: ${info['cpm']:<6} Potential: {info['potential']:<12} Saturation: {info['saturation']}")

    click.echo()
    click.secho("Monetization Methods:", fg="yellow")
    for method, info in data.get("monetization_methods", {}).items():
        click.echo(f"  {method:<20} Difficulty: {info['difficulty']:<8} Timing: {info['timing']}")

    click.echo()
    click.secho("Quick Start:", fg="green", bold=True)
    click.echo(f"  {data.get('quick_start_recommendation', '')}")


if __name__ == "__main__":
    main()
