"""Social Trends CLI — agent-native harness for YouTube & TikTok trend intelligence.

Usage:
    cli-anything-social-trends trends youtube [OPTIONS]
    cli-anything-social-trends trends tiktok [OPTIONS]
    cli-anything-social-trends trends compare TOPIC [OPTIONS]
    cli-anything-social-trends hashtags research TOPIC [OPTIONS]
    cli-anything-social-trends hashtags generate NICHE [OPTIONS]
    cli-anything-social-trends hashtags analyze HASHTAG [OPTIONS]
    cli-anything-social-trends music tiktok [OPTIONS]
    cli-anything-social-trends music youtube [OPTIONS]
    cli-anything-social-trends music cross-platform [OPTIONS]
    cli-anything-social-trends music search QUERY [OPTIONS]
    cli-anything-social-trends accounts optimize PLATFORM [OPTIONS]
    cli-anything-social-trends accounts schedule PLATFORM [OPTIONS]
    cli-anything-social-trends accounts audit PLATFORM [OPTIONS]
    cli-anything-social-trends theme-pages guide [OPTIONS]
    cli-anything-social-trends theme-pages niches [OPTIONS]
    cli-anything-social-trends theme-pages monetize NICHE [OPTIONS]
    cli-anything-social-trends theme-pages calendar NICHE [OPTIONS]
    cli-anything-social-trends cache clear
    cli-anything-social-trends cache stats
    cli-anything-social-trends config set KEY VALUE
    cli-anything-social-trends config show
    cli-anything-social-trends repl
"""

import json
import sys
import click

from cli_anything.social_trends.core import trends, hashtags, music, accounts, theme_pages
from cli_anything.social_trends.utils.scraper_backend import (
    clear_cache, cache_stats, load_config, save_config,
)


def _out(data: dict | list):
    click.echo(json.dumps(data, indent=2, ensure_ascii=False))


# ── Root ──────────────────────────────────────────────────────────────────────

@click.group()
def main():
    """Social Trends CLI: YouTube & TikTok viral trend intelligence for content creators."""


# ── Trends ────────────────────────────────────────────────────────────────────

@main.group()
def trends_cmd():
    """Scrape viral trends from YouTube and TikTok."""

main.add_command(trends_cmd, name="trends")


@trends_cmd.command("youtube")
@click.option("--region", default="US", show_default=True, help="ISO country code (e.g. US, GB, IN)")
@click.option("--category", default="0", show_default=True,
              help="YouTube category ID (0=all, 10=music, 20=gaming, 24=entertainment)")
@click.option("--limit", default=25, show_default=True, help="Max results (1-50)")
@click.option("--fresh", is_flag=True, default=False, help="Bypass cache")
def trends_youtube(region: str, category: str, limit: int, fresh: bool):
    """Fetch trending YouTube videos. Requires youtube_api_key for full stats."""
    _out(trends.get_youtube_trending(
        region_code=region, category_id=category,
        max_results=limit, bypass_cache=fresh,
    ))


@trends_cmd.command("tiktok")
@click.option("--region", default="US", show_default=True, help="ISO country code")
@click.option("--period", default=7, show_default=True, type=click.Choice(["7", "30", "120"]),
              help="Time window in days")
@click.option("--sort", default="popular", show_default=True,
              type=click.Choice(["popular", "new"]), help="Sort order")
@click.option("--limit", default=20, show_default=True, help="Results per page")
@click.option("--page", default=1, show_default=True, help="Page number")
@click.option("--fresh", is_flag=True, default=False, help="Bypass cache")
def trends_tiktok(region: str, period: str, sort: str, limit: int, page: int, fresh: bool):
    """Fetch trending TikTok hashtags and videos (no auth required)."""
    result = {
        "hashtags": trends.get_tiktok_trending_hashtags(
            region=region, period=int(period), sort_by=sort,
            limit=limit, page=page, bypass_cache=fresh,
        ),
        "videos": trends.get_tiktok_trending_videos(
            region=region, period=int(period),
            limit=limit, page=page, bypass_cache=fresh,
        ),
    }
    _out(result)


@trends_cmd.command("compare")
@click.argument("topic")
@click.option("--region", default="US", show_default=True, help="ISO country code")
def trends_compare(topic: str, region: str):
    """Compare a topic's trend presence across YouTube and TikTok."""
    _out(trends.compare_trends(topic=topic, region=region))


@trends_cmd.command("yt-categories")
@click.option("--region", default="US", show_default=True)
def yt_categories(region: str):
    """List YouTube video categories for a region (requires API key)."""
    _out(trends.get_youtube_categories(region_code=region))


# ── Hashtags ──────────────────────────────────────────────────────────────────

@main.group()
def hashtags_cmd():
    """Research, generate, and analyse hashtags."""

main.add_command(hashtags_cmd, name="hashtags")


@hashtags_cmd.command("research")
@click.argument("topic")
@click.option("--platform", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "youtube", "instagram", "all"]))
@click.option("--region", default="US", show_default=True)
@click.option("--limit", default=30, show_default=True)
@click.option("--fresh", is_flag=True, default=False)
def hashtags_research(topic: str, platform: str, region: str, limit: int, fresh: bool):
    """Research hashtags for a topic combining live trends + curated seeds."""
    _out(hashtags.research_hashtags(
        topic=topic, platform=platform, region=region,  # type: ignore[arg-type]
        limit=limit, bypass_cache=fresh,
    ))


@hashtags_cmd.command("generate")
@click.argument("niche")
@click.option("--platform", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "youtube", "instagram", "all"]))
@click.option("--region", default="US", show_default=True)
@click.option("--posts", default=7, show_default=True, help="Number of unique post sets to generate")
@click.option("--fresh", is_flag=True, default=False)
def hashtags_generate(niche: str, platform: str, region: str, posts: int, fresh: bool):
    """Generate optimised hashtag sets using the mix-size strategy."""
    _out(hashtags.generate_hashtag_set(
        niche=niche, platform=platform, region=region,  # type: ignore[arg-type]
        post_count=posts, bypass_cache=fresh,
    ))


@hashtags_cmd.command("analyze")
@click.argument("hashtag")
@click.option("--region", default="US", show_default=True)
@click.option("--fresh", is_flag=True, default=False)
def hashtags_analyze(hashtag: str, region: str, fresh: bool):
    """Get metrics and competition level for a specific hashtag."""
    _out(hashtags.analyze_hashtag(hashtag=hashtag, region=region, bypass_cache=fresh))


# ── Music ─────────────────────────────────────────────────────────────────────

@main.group()
def music_cmd():
    """Trending music and sounds."""

main.add_command(music_cmd, name="music")


@music_cmd.command("tiktok")
@click.option("--region", default="US", show_default=True)
@click.option("--period", default=7, show_default=True, type=click.Choice(["7", "30", "120"]))
@click.option("--sort", default="popular", show_default=True,
              type=click.Choice(["popular", "new"]))
@click.option("--limit", default=20, show_default=True)
@click.option("--fresh", is_flag=True, default=False)
def music_tiktok(region: str, period: str, sort: str, limit: int, fresh: bool):
    """Fetch trending TikTok sounds."""
    _out(music.get_tiktok_trending_sounds(
        region=region, period=int(period), sort_by=sort,
        limit=limit, bypass_cache=fresh,
    ))


@music_cmd.command("youtube")
@click.option("--region", default="US", show_default=True)
@click.option("--limit", default=25, show_default=True)
@click.option("--fresh", is_flag=True, default=False)
def music_youtube(region: str, limit: int, fresh: bool):
    """Fetch trending YouTube music videos (requires API key)."""
    _out(music.get_youtube_trending_music(
        region_code=region, max_results=limit, bypass_cache=fresh,
    ))


@music_cmd.command("cross-platform")
@click.option("--region", default="US", show_default=True)
def music_cross_platform(region: str):
    """Find music trending on BOTH TikTok and YouTube simultaneously."""
    _out(music.get_cross_platform_music_trends(region=region))


@music_cmd.command("search")
@click.argument("query")
@click.option("--region", default="US", show_default=True)
@click.option("--limit", default=20, show_default=True)
@click.option("--fresh", is_flag=True, default=False)
def music_search(query: str, region: str, limit: int, fresh: bool):
    """Search TikTok sounds by keyword."""
    _out(music.search_tiktok_sounds(query=query, region=region, limit=limit, bypass_cache=fresh))


# ── Accounts ──────────────────────────────────────────────────────────────────

@main.group()
def accounts_cmd():
    """Account optimisation, posting schedules, and growth audits."""

main.add_command(accounts_cmd, name="accounts")


@accounts_cmd.command("optimize")
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram", "all"]))
@click.option("--niche", default="", help="Content niche for tailored tips")
def accounts_optimize(platform: str, niche: str):
    """Get a full profile optimisation checklist and growth strategies."""
    _out(accounts.optimize_profile(platform=platform, niche=niche))  # type: ignore[arg-type]


@accounts_cmd.command("schedule")
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram", "all"]))
@click.option("--timezone", default="US/Eastern", show_default=True)
def accounts_schedule(platform: str, timezone: str):
    """Get optimal posting schedule with day-by-day template."""
    _out(accounts.get_posting_schedule(platform=platform, timezone=timezone))  # type: ignore[arg-type]


@accounts_cmd.command("audit")
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--niche", default="", help="Content niche")
@click.option("--followers", default=0, type=int, help="Current follower count")
def accounts_audit(platform: str, niche: str, followers: int):
    """Run a strategic account audit with prioritised action items."""
    _out(accounts.audit_account(
        platform=platform, niche=niche, follower_count=followers,  # type: ignore[arg-type]
    ))


# ── Theme Pages ───────────────────────────────────────────────────────────────

@main.group()
def theme_pages_cmd():
    """Theme page creation, conversion, and monetisation strategies."""

main.add_command(theme_pages_cmd, name="theme-pages")


@theme_pages_cmd.command("guide")
@click.option("--niche", default="", help="Filter guide for specific niche")
def tp_guide(niche: str):
    """Complete guide to starting and converting a theme page."""
    _out(theme_pages.get_guide(niche=niche))


@theme_pages_cmd.command("niches")
@click.option("--sort-by", default="monetisation_potential", show_default=True,
              type=click.Choice(["monetisation_potential", "competition"]))
@click.option("--top", default=10, show_default=True, help="Number of niches to show")
def tp_niches(sort_by: str, top: int):
    """Rank niches by monetisation potential."""
    _out(theme_pages.get_niche_rankings(sort_by=sort_by, top_n=top))


@theme_pages_cmd.command("monetize")
@click.argument("niche")
def tp_monetize(niche: str):
    """Get monetisation blueprint for a niche."""
    _out(theme_pages.get_monetisation_strategies(niche=niche))


@theme_pages_cmd.command("calendar")
@click.argument("niche")
@click.option("--platform", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--weeks", default=4, show_default=True, type=int)
def tp_calendar(niche: str, platform: str, weeks: int):
    """Generate a content calendar for a theme page."""
    _out(theme_pages.get_content_calendar(niche=niche, platform=platform, weeks=weeks))


# ── Cache ─────────────────────────────────────────────────────────────────────

@main.group()
def cache_cmd():
    """Manage cached API responses."""

main.add_command(cache_cmd, name="cache")


@cache_cmd.command("clear")
def cache_clear():
    """Remove all cached API responses."""
    _out(clear_cache())


@cache_cmd.command("stats")
def cache_stats_cmd():
    """Show cache statistics."""
    _out(cache_stats())


# ── Config ────────────────────────────────────────────────────────────────────

@main.group()
def config_cmd():
    """Manage API keys and configuration."""

main.add_command(config_cmd, name="config")


@config_cmd.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """Set a configuration value (e.g. youtube_api_key, default_region).

    \b
    Keys:
      youtube_api_key   YouTube Data API v3 key (for full stats)
      default_region    Default country code (e.g. US, GB, IN)
    """
    config = load_config()
    config[key] = value
    save_config(config)
    _out({"status": "saved", "key": key, "value": "***" if "key" in key.lower() else value})


@config_cmd.command("show")
def config_show():
    """Show current configuration (API keys are masked)."""
    config = load_config()
    masked = {
        k: ("***" + v[-4:] if "key" in k.lower() and len(v) > 4 else v)
        for k, v in config.items()
    }
    _out(masked if masked else {"status": "no config set", "tip": "Run: config set youtube_api_key YOUR_KEY"})


# ── REPL ──────────────────────────────────────────────────────────────────────

@main.command()
def repl():
    """Launch interactive REPL for the Social Trends CLI."""
    try:
        from cli_anything.social_trends.utils.repl_skin import run_repl
    except ImportError:
        click.echo("prompt-toolkit required for REPL. Run: pip install prompt-toolkit")
        sys.exit(1)

    def dispatch(parts: list[str]):
        if not parts:
            return None
        cmd = " ".join(parts[:2]).lower()
        try:
            if cmd == "trends youtube":
                return trends.get_youtube_trending()
            elif cmd == "trends tiktok":
                return {
                    "hashtags": trends.get_tiktok_trending_hashtags(),
                    "videos": trends.get_tiktok_trending_videos(),
                }
            elif cmd == "music tiktok":
                return music.get_tiktok_trending_sounds()
            elif cmd == "music youtube":
                return music.get_youtube_trending_music()
            elif cmd == "cache clear":
                return clear_cache()
            elif cmd == "cache stats":
                return cache_stats()
            elif cmd == "config show":
                return load_config()
            elif parts[0] == "hashtags" and len(parts) >= 3:
                if parts[1] == "research":
                    return hashtags.research_hashtags(parts[2])
                elif parts[1] == "generate":
                    return hashtags.generate_hashtag_set(parts[2])
                elif parts[1] == "analyze":
                    return hashtags.analyze_hashtag(parts[2])
            elif parts[0] == "accounts" and len(parts) >= 3:
                plat = parts[2] if len(parts) > 2 else "tiktok"
                if parts[1] == "optimize":
                    return accounts.optimize_profile(plat)  # type: ignore[arg-type]
                elif parts[1] == "schedule":
                    return accounts.get_posting_schedule(plat)  # type: ignore[arg-type]
                elif parts[1] == "audit":
                    return accounts.audit_account(plat)  # type: ignore[arg-type]
            elif parts[0] == "theme-pages":
                if len(parts) >= 2 and parts[1] == "guide":
                    return theme_pages.get_guide()
                elif len(parts) >= 2 and parts[1] == "niches":
                    return theme_pages.get_niche_rankings()
                elif len(parts) >= 3 and parts[1] == "monetize":
                    return theme_pages.get_monetisation_strategies(parts[2])
                elif len(parts) >= 3 and parts[1] == "calendar":
                    return theme_pages.get_content_calendar(parts[2])
            else:
                return {"error": f"Unknown command: {' '.join(parts)}", "tip": "Type 'help' for commands"}
        except Exception as e:
            return {"error": str(e)}
        return None

    run_repl(dispatch)


if __name__ == "__main__":
    main()
