#!/usr/bin/env python3
"""trends-scout — Viral trend intelligence for YouTube & TikTok.

Scrapes trending videos, hashtags, and music. Optimizes account strategy.
Provides a complete theme page conversion playbook.

Usage:
    # Scrape trending content
    trends-scout youtube trending --region US --limit 20
    trends-scout tiktok trending
    trends-scout music viral

    # Get hashtag strategies
    trends-scout youtube hashtags --region US
    trends-scout tiktok hashtags
    trends-scout account hashtags --niche fitness --platform tiktok

    # Optimize your accounts
    trends-scout account add --platform tiktok --handle @yourpage --niche fitness
    trends-scout account optimize
    trends-scout account audit --platform tiktok --handle @yourpage

    # Theme page strategy
    trends-scout theme-page niches
    trends-scout theme-page strategy --niche motivation
    trends-scout theme-page monetize --platform tiktok
    trends-scout theme-page repurpose --platform tiktok_video

    # Configure API keys (all optional — works without them)
    trends-scout config set-key youtube_api_key YOUR_KEY
    trends-scout config set-key tiktok_client_key YOUR_KEY
    trends-scout config show

    # Interactive REPL
    trends-scout repl
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.trends_scout.core import youtube as yt_mod
from cli_anything.trends_scout.core import tiktok as tt_mod
from cli_anything.trends_scout.core import music as music_mod
from cli_anything.trends_scout.core import account as acc_mod
from cli_anything.trends_scout.core import theme_page as tp_mod
from cli_anything.trends_scout.utils import config as cfg_mod

_json_output = False
_repl_mode = False


# ── Output helpers ──────────────────────────────────────────────────────────

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
            click.echo(f"{prefix}[{i + 1}]")
            _print_dict(item, indent + 1)
        else:
            click.echo(f"{prefix}  {item}")


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


# ── Main CLI ────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx, use_json):
    """trends-scout — Viral trend intelligence for TikTok & YouTube.

    Scrape trending videos, hashtags, and music. Optimize account strategy.
    Run without a subcommand to enter interactive REPL mode.
    """
    global _json_output
    _json_output = use_json
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── YouTube Commands ─────────────────────────────────────────────────────────

@cli.group()
def youtube():
    """YouTube trend scraping commands."""
    pass


@youtube.command("trending")
@click.option("--region", "-r", default="US", help="Region code (US, GB, JP, etc.)")
@click.option("--limit", "-n", default=25, type=int, help="Number of videos")
@click.option("--category", "-c", default="0",
              help="YouTube category ID (0=all, 10=music, 17=sports, 20=gaming, 24=entertainment)")
@handle_error
def youtube_trending(region, limit, category):
    """Get trending YouTube videos with hashtags."""
    click.echo(f"Fetching YouTube trending for region={region}...")
    data = yt_mod.get_trending(region=region, category=category, limit=limit)
    output(data, f"YouTube Trending ({region}) — {data['total']} videos  [source: {data['source']}]")


@youtube.command("hashtags")
@click.option("--region", "-r", default="US", help="Region code")
@click.option("--limit", "-n", default=30, type=int, help="Number of hashtags")
@handle_error
def youtube_hashtags(region, limit):
    """Extract trending hashtags from YouTube."""
    click.echo(f"Extracting YouTube hashtags for region={region}...")
    data = yt_mod.get_hashtags(region=region, limit=limit)
    output(data, f"YouTube Trending Hashtags ({region})")


@youtube.command("music")
@click.option("--region", "-r", default="US", help="Region code")
@click.option("--limit", "-n", default=20, type=int, help="Number of tracks")
@handle_error
def youtube_music(region, limit):
    """Find trending music on YouTube."""
    click.echo(f"Fetching YouTube trending music for region={region}...")
    data = yt_mod.get_trending_music(region=region, limit=limit)
    output(data, f"YouTube Trending Music ({region})")


# ── TikTok Commands ──────────────────────────────────────────────────────────

@cli.group()
def tiktok():
    """TikTok trend scraping commands."""
    pass


@tiktok.command("trending")
@click.option("--region", "-r", default="US", help="Region code")
@click.option("--limit", "-n", default=25, type=int, help="Number of videos")
@handle_error
def tiktok_trending(region, limit):
    """Get trending TikTok videos with hashtags and sounds."""
    click.echo(f"Fetching TikTok trending for region={region}...")
    data = tt_mod.get_trending(region=region, limit=limit)
    output(data, f"TikTok Trending ({region}) — {data['total']} videos  [source: {data['source']}]")


@tiktok.command("hashtags")
@click.option("--region", "-r", default="US", help="Region code")
@click.option("--limit", "-n", default=30, type=int, help="Number of hashtags")
@handle_error
def tiktok_hashtags(region, limit):
    """Extract trending hashtags from TikTok."""
    click.echo(f"Extracting TikTok hashtags for region={region}...")
    data = tt_mod.get_hashtags(region=region, limit=limit)
    output(data, f"TikTok Trending Hashtags ({region})")


@tiktok.command("sounds")
@click.option("--region", "-r", default="US", help="Region code")
@click.option("--limit", "-n", default=20, type=int, help="Number of sounds")
@handle_error
def tiktok_sounds(region, limit):
    """Find trending sounds/music on TikTok."""
    click.echo(f"Fetching TikTok trending sounds for region={region}...")
    data = tt_mod.get_trending_sounds(region=region, limit=limit)
    output(data, f"TikTok Trending Sounds ({region})")


@tiktok.command("lookup-hashtag")
@click.argument("hashtag")
@handle_error
def tiktok_lookup(hashtag):
    """Look up stats for a specific TikTok hashtag (e.g. #fitness)."""
    data = tt_mod.lookup_hashtag(hashtag)
    output(data)


# ── Music Commands ───────────────────────────────────────────────────────────

@cli.group()
def music():
    """Cross-platform viral music commands."""
    pass


@music.command("viral")
@click.option("--region", "-r", default="US", help="Region code")
@click.option("--limit", "-n", default=30, type=int, help="Number of tracks")
@handle_error
def music_viral(region, limit):
    """Aggregate viral music across YouTube, TikTok, Spotify & Last.fm."""
    click.echo("Aggregating viral music across all platforms...")
    data = music_mod.get_viral_music(region=region, limit=limit)
    output(data, f"Viral Music — {data['total']} tracks from {data['sources']}")


@music.command("cross-hits")
@handle_error
def music_cross_hits():
    """Find music trending on BOTH TikTok and YouTube — maximum signal."""
    click.echo("Scanning for cross-platform music hits...")
    data = music_mod.get_cross_platform_hits()
    output(data, f"Cross-Platform Hits — {data['total']} tracks trending everywhere")


# ── Account Commands ─────────────────────────────────────────────────────────

@cli.group()
def account():
    """Account optimization and management commands."""
    pass


@account.command("add")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram", "twitter"]),
              help="Social media platform")
@click.option("--handle", "-h", required=True, help="Account handle or username")
@click.option("--niche", "-n", default="general",
              help="Content niche (fitness, food, fashion, finance, beauty, gaming, general)")
@handle_error
def account_add(platform, handle, niche):
    """Register an account for optimization tracking."""
    result = cfg_mod.add_account(platform=platform, handle=handle, niche=niche)
    output(result, f"Account registered: {platform}:{handle} [{niche}]")


@account.command("remove")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram", "twitter"]))
@click.option("--handle", "-h", required=True, help="Account handle")
@handle_error
def account_remove(platform, handle):
    """Remove an account from tracking."""
    result = cfg_mod.remove_account(platform=platform, handle=handle)
    output(result, f"Removed {result['removed']} account(s).")


@account.command("list")
@handle_error
def account_list():
    """List all tracked accounts."""
    accounts = cfg_mod.get_accounts()
    if not accounts:
        click.echo("No accounts registered. Use: trends-scout account add --platform tiktok --handle @you")
        return
    output(accounts, f"Tracked accounts ({len(accounts)}):")


@account.command("audit")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram", "twitter"]))
@click.option("--handle", "-h", required=True, help="Account handle")
@click.option("--niche", "-n", default="general", help="Content niche")
@handle_error
def account_audit(platform, handle, niche):
    """Run a full optimization audit on an account."""
    click.echo(f"Auditing {platform}:{handle} [{niche}]...")
    result = acc_mod.audit_account(platform=platform, handle=handle, niche=niche)
    output(result, f"Account Audit — {platform}:{handle}")


@account.command("optimize")
@handle_error
def account_optimize():
    """Optimize all registered accounts (batch audit)."""
    click.echo("Running optimization analysis on all accounts...")
    result = acc_mod.optimize_all_accounts()
    output(result, f"Optimization Report — {result.get('accounts_audited', 0)} accounts")


@account.command("schedule")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "instagram", "twitter"]),
              help="Platform for schedule")
@handle_error
def account_schedule(platform):
    """Get optimal posting schedule for a platform."""
    result = acc_mod.get_posting_schedule(platform=platform)
    output(result, f"Optimal Posting Schedule — {platform}")


@account.command("hashtags")
@click.option("--niche", "-n", default="general", help="Content niche")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "instagram", "twitter"]))
@click.option("--count", "-c", default=10, type=int, help="Number of hashtags to generate")
@click.option("--live", is_flag=True, help="Include live trending hashtags from platform scrape")
@handle_error
def account_hashtags(niche, platform, count, live):
    """Generate optimized hashtag mix for a post."""
    trend_tags = []
    if live:
        click.echo(f"Fetching live {platform} trending hashtags...")
        if platform == "tiktok":
            live_data = tt_mod.get_hashtags(limit=10)
            trend_tags = [h["hashtag"] for h in live_data.get("hashtags", [])]
        else:
            live_data = yt_mod.get_hashtags(limit=10)
            trend_tags = [h["hashtag"] for h in live_data.get("hashtags", [])]

    result = acc_mod.optimize_hashtags(
        niche=niche, platform=platform,
        trend_hashtags=trend_tags, count=count,
    )
    output(result, f"Hashtag Strategy — {niche} on {platform}")


# ── Theme Page Commands ──────────────────────────────────────────────────────

@cli.group("theme-page")
def theme_page():
    """Theme page creation and conversion strategy commands."""
    pass


@theme_page.command("niches")
@click.option("--sort", default="conversion_rate",
              type=click.Choice(["conversion_rate", "difficulty", "time_to_monetize"]),
              help="Sort criteria")
@handle_error
def tp_niches(sort):
    """List all high-converting theme page niches ranked by potential."""
    result = tp_mod.get_niches(sort_by=sort)
    output(result, f"High-Converting Niches ({result['total']} niches)")


@theme_page.command("strategy")
@click.option("--niche", "-n", required=True,
              help="Niche to get strategy for (motivation, finance, fitness, luxury_lifestyle, etc.)")
@handle_error
def tp_strategy(niche):
    """Get full strategy + 90-day plan for a specific niche."""
    result = tp_mod.get_niche_strategy(niche=niche)
    output(result, f"Theme Page Strategy — {niche}")


@theme_page.command("roadmap")
@handle_error
def tp_roadmap():
    """Get the complete theme page growth roadmap (0 to monetization)."""
    result = tp_mod.get_growth_roadmap()
    output(result, "Theme Page Growth Roadmap")


@theme_page.command("monetize")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              help="Platform")
@handle_error
def tp_monetize(platform):
    """Get monetization tiers and thresholds for a platform."""
    result = tp_mod.get_monetization_roadmap(platform=platform)
    output(result, f"Monetization Roadmap — {platform}")


@theme_page.command("repurpose")
@click.option("--platform", "-p", default="tiktok_video",
              type=click.Choice(["tiktok_video", "youtube_shorts", "instagram_reels", "twitter_thread"]),
              help="Content format")
@handle_error
def tp_repurpose(platform):
    """Get content repurposing guide for a platform format."""
    result = tp_mod.get_repurpose_guide(platform=platform)
    output(result, f"Content Repurposing Guide — {platform}")


@theme_page.command("learn")
@handle_error
def tp_learn():
    """Full theme page crash course: niches, strategy, monetization, repurposing."""
    click.echo("\n" + "=" * 60)
    click.echo("  THEME PAGE CRASH COURSE")
    click.echo("=" * 60)

    # Niches
    click.echo("\n[1/4] TOP CONVERTING NICHES")
    niches = tp_mod.get_niches()
    for n in niches["niches"][:5]:
        click.echo(f"  {n['name']:25s}  {n['conversion_rate']:10s}  {n['time_to_monetize']:12s}  RPM: {n['avg_rpm']}")

    # Roadmap
    click.echo("\n[2/4] GROWTH PHASES")
    roadmap = tp_mod.get_growth_roadmap()
    for phase in roadmap["phases"]:
        click.echo(f"\n  {phase['phase']}")
        click.echo(f"  Goal: {phase['goal']}")
        for action in phase["actions"][:2]:
            click.echo(f"    • {action}")

    # Repurpose
    click.echo("\n[3/4] CONTENT REPURPOSING ESSENTIALS")
    for platform, guide in list(tp_mod._REPURPOSE_MATRIX.items())[:2]:
        click.echo(f"\n  {platform.upper()}")
        click.echo(f"  Tip: {guide['tip']}")
        click.echo(f"  Tools: {', '.join(guide['tools'][:3])}")

    # Monetization
    click.echo("\n[4/4] MONETIZATION QUICK REFERENCE")
    click.echo("  Platform         | Threshold               | Payout")
    click.echo("  -----------------|-------------------------|--------")
    click.echo("  TikTok (Rewards) | 10K followers + 100K v  | $0.40-1.00/1K views")
    click.echo("  YouTube Partner  | 1K subs + 4K hours      | $1-30 RPM")
    click.echo("  Brand Deals      | 1K-5K followers          | $50-500/post")
    click.echo("  Affiliate Links  | Any size                 | 5-20% commission")

    click.echo("\n" + "=" * 60)
    click.echo("  Run 'trends-scout theme-page strategy --niche <NAME>' for deep-dive")
    click.echo("=" * 60 + "\n")


# ── Config Commands ──────────────────────────────────────────────────────────

@cli.group()
def config():
    """Configuration and API key management."""
    pass


@config.command("set-key")
@click.argument("key")
@click.argument("value")
@handle_error
def config_set_key(key, value):
    """Set a configuration key.

    \b
    Available keys:
      youtube_api_key       YouTube Data API v3 key (console.developers.google.com)
      tiktok_client_key     TikTok Research API client key
      tiktok_client_secret  TikTok Research API client secret
      lastfm_api_key        Last.fm API key (last.fm/api/account/create)
      spotify_client_id     Spotify app client ID
      spotify_client_secret Spotify app client secret
    """
    result = cfg_mod.set_key(key, value)
    click.echo(f"Set {key} — OK")


@config.command("show")
@handle_error
def config_show():
    """Show current configuration (secrets masked)."""
    result = cfg_mod.get_all()
    output(result, "Configuration (secrets masked):")


# ── Scan Command (proactive all-in-one) ─────────────────────────────────────

@cli.command("scan")
@click.option("--region", "-r", default="US", help="Region code")
@click.option("--niche", "-n", default="general", help="Your content niche")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "both"]),
              help="Platform to scan")
@handle_error
def scan(region, niche, platform):
    """All-in-one trend scan: trending content + hashtags + music + strategy.

    This is the fastest way to get actionable trend intel in one command.
    """
    click.echo(f"\nRunning full trend scan [region={region}, niche={niche}, platform={platform}]...\n")
    results = {}

    if platform in ("tiktok", "both"):
        click.echo("Scanning TikTok...")
        try:
            tt_trends = tt_mod.get_trending(region=region, limit=10)
            results["tiktok_trending"] = {
                "top_hashtags": tt_trends.get("top_hashtags", [])[:10],
                "video_count": tt_trends.get("total", 0),
                "source": tt_trends.get("source"),
            }
            tt_sounds = tt_mod.get_trending_sounds(region=region, limit=5)
            results["tiktok_sounds"] = [
                f"{s['title']} — {s['artist']}"
                for s in tt_sounds.get("trending_sounds", [])[:5]
            ]
        except Exception as e:
            results["tiktok_error"] = str(e)

    if platform in ("youtube", "both"):
        click.echo("Scanning YouTube...")
        try:
            yt_trends = yt_mod.get_trending(region=region, limit=10)
            results["youtube_trending"] = {
                "top_hashtags": yt_trends.get("top_hashtags", [])[:10],
                "video_count": yt_trends.get("total", 0),
                "source": yt_trends.get("source"),
            }
        except Exception as e:
            results["youtube_error"] = str(e)

    # Hashtag strategy for niche
    click.echo("Building hashtag strategy...")
    try:
        trend_tags = results.get("tiktok_trending", {}).get("top_hashtags", [])
        hashtag_data = acc_mod.optimize_hashtags(
            niche=niche, platform=platform if platform != "both" else "tiktok",
            trend_hashtags=trend_tags, count=10,
        )
        results["hashtag_strategy"] = hashtag_data
    except Exception as e:
        results["hashtag_error"] = str(e)

    output(results, "TREND SCAN COMPLETE")
    click.echo("\nNext steps:")
    click.echo("  trends-scout account optimize      — audit all registered accounts")
    click.echo("  trends-scout theme-page learn      — theme page crash course")
    click.echo("  trends-scout music viral           — viral music for content")


# ── REPL ─────────────────────────────────────────────────────────────────────

@cli.command()
@handle_error
def repl():
    """Start interactive REPL session."""
    from cli_anything.trends_scout.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("trends-scout", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "youtube":    "trending|hashtags|music",
        "tiktok":     "trending|hashtags|sounds|lookup-hashtag",
        "music":      "viral|cross-hits",
        "account":    "add|remove|list|audit|optimize|schedule|hashtags",
        "theme-page": "niches|strategy|roadmap|monetize|repurpose|learn",
        "config":     "set-key|show",
        "scan":       "All-in-one trend scan",
        "help":       "Show this help",
        "quit":       "Exit REPL",
    }

    accounts = cfg_mod.get_accounts()
    if accounts:
        skin.success(f"Tracking {len(accounts)} account(s). Run 'account optimize' for recommendations.")
    else:
        skin.info("No accounts registered. Run: account add --platform tiktok --handle @you --niche fitness")

    while True:
        try:
            line = skin.get_input(pt_session, context="trends")
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                skin.print_goodbye()
                break
            if line.lower() == "help":
                skin.help(_repl_commands)
                continue
            args = line.split()
            try:
                cli.main(args, standalone_mode=False)
            except SystemExit:
                pass
            except click.exceptions.UsageError as e:
                skin.warning(f"Usage error: {e}")
            except Exception as e:
                skin.error(f"{e}")
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

    _repl_mode = False


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    cli()


if __name__ == "__main__":
    main()
