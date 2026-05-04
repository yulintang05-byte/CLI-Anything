import json
import sys

import click

from .core.account_optimizer import (
    audit_account_profile,
    generate_content_pillars,
    get_hashtag_strategy,
    get_optimal_posting_times,
)
from .core.theme_pages import get_all_niches, get_niche_analysis, get_theme_page_playbook
from .core.tiktok_trends import (
    get_trending_hashtags_tiktok,
    get_trending_sounds,
    get_trending_videos_tiktok,
)
from .core.youtube_trends import (
    get_trending_by_category,
    get_trending_hashtags,
    get_trending_music,
    get_trending_videos,
    search_trending_topics,
)
from .utils.social_backend import get_config, save_config


def _out(data, json_flag: bool = False):
    if json_flag or isinstance(data, (list, dict)):
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        click.echo(data)


# ─── ROOT ────────────────────────────────────────────────────────────────────

@click.group()
@click.version_option("1.0.0")
def cli():
    """Social Trends CLI – viral trends, account optimisation, theme page playbooks."""


# ─── CONFIG ──────────────────────────────────────────────────────────────────

@cli.group()
def config():
    """Manage API keys and session tokens."""


@config.command("set")
@click.argument("key", type=click.Choice(["youtube-api-key", "tiktok-cookie"]))
@click.argument("value")
def config_set(key, value):
    """Set a configuration value.\n\nKEYS:\n  youtube-api-key   Google Cloud YouTube Data API v3 key\n  tiktok-cookie     TikTok session cookie (from browser DevTools)"""
    cfg = get_config()
    cfg_key = key.replace("-", "_")
    cfg[cfg_key] = value
    save_config(cfg)
    click.echo(f"✓ {key} saved")


@config.command("show")
def config_show():
    """Show current configuration (values are redacted)."""
    cfg = get_config()
    display = {
        k: (str(v)[:4] + "…" + str(v)[-4:] if v and len(str(v)) > 8 else "not set")
        for k, v in cfg.items()
    }
    _out(display)


# ─── YOUTUBE ─────────────────────────────────────────────────────────────────

@cli.group()
def youtube():
    """YouTube trending videos, hashtags, and music."""


@youtube.command("trending")
@click.option("--region", "-r", default="US", show_default=True, help="ISO region code")
@click.option("--category", "-c", default=None, help="Category ID (10=Music 20=Gaming 24=Entertainment…)")
@click.option("--count", "-n", default=20, show_default=True, help="Number of results")
@click.option("--json", "json_flag", is_flag=True)
def yt_trending(region, category, count, json_flag):
    """Get currently trending YouTube videos."""
    try:
        data = get_trending_videos(region=region, category_id=category, max_results=count)
        _out(data, json_flag)
        if not json_flag:
            click.echo(f"\n✓ {len(data)} trending videos ({region})")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@youtube.command("hashtags")
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--top", "-n", default=30, show_default=True)
@click.option("--json", "json_flag", is_flag=True)
def yt_hashtags(region, top, json_flag):
    """Extract trending hashtags from YouTube's trending videos."""
    try:
        data = get_trending_hashtags(region=region, top_n=top)
        _out(data, json_flag)
        if not json_flag:
            click.echo(f"\n✓ {len(data)} trending hashtags extracted from YouTube ({region})")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@youtube.command("music")
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--json", "json_flag", is_flag=True)
def yt_music(region, json_flag):
    """Get trending music videos on YouTube."""
    try:
        data = get_trending_music(region=region)
        _out(data, json_flag)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@youtube.command("by-category")
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--json", "json_flag", is_flag=True)
def yt_by_category(region, json_flag):
    """Get top trending videos per category (Music, Gaming, Comedy…)."""
    try:
        data = get_trending_by_category(region=region)
        _out(data, json_flag)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@youtube.command("search")
@click.argument("query")
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--count", "-n", default=20, show_default=True)
@click.option("--json", "json_flag", is_flag=True)
def yt_search(query, region, count, json_flag):
    """Search recent YouTube videos by topic (sorted by view count)."""
    try:
        data = search_trending_topics(query=query, region=region, max_results=count)
        _out(data, json_flag)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


# ─── TIKTOK ──────────────────────────────────────────────────────────────────

@cli.group()
def tiktok():
    """TikTok trending videos, hashtags, and sounds."""


@tiktok.command("trending")
@click.option("--country", "-c", default="US", show_default=True)
@click.option("--count", "-n", default=20, show_default=True)
@click.option("--json", "json_flag", is_flag=True)
def tt_trending(country, count, json_flag):
    """Get trending TikTok videos (requires session cookie for live data)."""
    data = get_trending_videos_tiktok(country=country, top_n=count)
    if not data:
        click.echo(
            "ℹ Live TikTok data requires a session cookie.\n"
            "  Run: social-trends config set tiktok-cookie <value>",
            err=True,
        )
    else:
        _out(data, json_flag)


@tiktok.command("hashtags")
@click.option("--country", "-c", default="US", show_default=True)
@click.option("--top", "-n", default=30, show_default=True)
@click.option("--json", "json_flag", is_flag=True)
def tt_hashtags(country, top, json_flag):
    """Get trending TikTok hashtags (live + evergreen fallback)."""
    data = get_trending_hashtags_tiktok(country=country, top_n=top)
    _out(data, json_flag)
    if not json_flag:
        click.echo(f"\n✓ {len(data)} trending TikTok hashtags")


@tiktok.command("sounds")
@click.option("--country", "-c", default="US", show_default=True)
@click.option("--top", "-n", default=20, show_default=True)
@click.option("--json", "json_flag", is_flag=True)
def tt_sounds(country, top, json_flag):
    """Get trending TikTok sounds and music."""
    data = get_trending_sounds(country=country, top_n=top)
    _out(data, json_flag)


# ─── OPTIMIZE ────────────────────────────────────────────────────────────────

@cli.group()
def optimize():
    """Account optimisation: hashtags, posting times, audits, content pillars."""


@optimize.command("hashtags")
@click.argument("platform", type=click.Choice(["tiktok", "instagram", "youtube"]))
@click.argument("niche")
@click.option("--json", "json_flag", is_flag=True)
def opt_hashtags(platform, niche, json_flag):
    """Generate a platform-specific hashtag strategy for NICHE.\n\nExample: social-trends optimize hashtags tiktok fitness"""
    data = get_hashtag_strategy(platform=platform, niche=niche)
    _out(data, json_flag)


@optimize.command("posting-times")
@click.argument("platform", type=click.Choice(["tiktok", "instagram", "youtube"]))
@click.option("--timezone", "-tz", default="EST", show_default=True)
@click.option("--json", "json_flag", is_flag=True)
def opt_times(platform, timezone, json_flag):
    """Get optimal posting times for PLATFORM."""
    data = get_optimal_posting_times(platform=platform, timezone=timezone)
    _out(data, json_flag)


@optimize.command("audit")
@click.argument("platform", type=click.Choice(["tiktok", "instagram", "youtube"]))
@click.argument("username")
@click.option("--json", "json_flag", is_flag=True)
def opt_audit(platform, username, json_flag):
    """Full profile optimisation checklist for USERNAME on PLATFORM."""
    data = audit_account_profile(platform=platform, username=username)
    _out(data, json_flag)


@optimize.command("content-pillars")
@click.argument("niche")
@click.argument("platform", type=click.Choice(["tiktok", "instagram", "youtube"]))
@click.option("--json", "json_flag", is_flag=True)
def opt_pillars(niche, platform, json_flag):
    """Generate 5 content pillars + posting calendar for NICHE on PLATFORM."""
    data = generate_content_pillars(niche=niche, platform=platform)
    _out(data, json_flag)


# ─── THEME PAGES ─────────────────────────────────────────────────────────────

@cli.group("theme-pages")
def theme_pages():
    """Theme page creation, niche research, and monetisation playbooks."""


@theme_pages.command("niches")
@click.option("--json", "json_flag", is_flag=True)
def tp_niches(json_flag):
    """List all profitable niches ranked by average RPM."""
    data = get_all_niches()
    _out(data, json_flag)


@theme_pages.command("analyze")
@click.argument("niche")
@click.option("--json", "json_flag", is_flag=True)
def tp_analyze(niche, json_flag):
    """Deep-dive analysis for NICHE: revenue, platforms, affiliates, content ideas.\n\nExample: social-trends theme-pages analyze finance_investing"""
    data = get_niche_analysis(niche=niche)
    _out(data, json_flag)


@theme_pages.command("playbook")
def tp_playbook():
    """Print the complete 6-phase theme page creation & conversion playbook."""
    click.echo(get_theme_page_playbook())


# ─── TRENDS SUMMARY ──────────────────────────────────────────────────────────

@cli.command("trends")
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--json", "json_flag", is_flag=True)
def trends_summary(region, json_flag):
    """Cross-platform viral trends summary (YouTube + TikTok combined)."""
    yt_tags: list = []
    try:
        yt_tags = [h["hashtag"] for h in get_trending_hashtags(region=region, top_n=20)[:15]]
    except Exception as exc:
        yt_tags = [f"YouTube error: {exc} — set youtube-api-key to enable"]

    tt_tags = [h.get("hashtag", "") for h in get_trending_hashtags_tiktok(country=region, top_n=20)[:15]]

    yt_set = set(yt_tags)
    tt_set = set(tt_tags)

    summary = {
        "region": region,
        "youtube_top_hashtags": yt_tags,
        "tiktok_top_hashtags": tt_tags,
        "cross_platform_viral": sorted(yt_set & tt_set),
        "all_trending": sorted(yt_set | tt_set)[:30],
        "tip": "Cross-platform hashtags have the highest viral potential. Use these first.",
    }
    _out(summary, json_flag)
    if not json_flag:
        click.echo(f"\n✓ Trends summary for region: {region}")


if __name__ == "__main__":
    cli()
