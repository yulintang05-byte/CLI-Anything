"""Social Trends CLI — agent-native viral trend scraping and account optimization.

Scrape YouTube & TikTok trends, analyze hashtags and music, optimize accounts,
and build converting theme pages.

Usage:
    social-trends [--json] <command>
    social-trends   (launches interactive REPL)
"""

import json
import sys
import click
from typing import Any, Optional

from cli_anything.social_trends.core.session import Session
from cli_anything.social_trends.core import youtube as yt_mod
from cli_anything.social_trends.core import tiktok as tt_mod
from cli_anything.social_trends.core import music as music_mod
from cli_anything.social_trends.core import hashtags as hash_mod
from cli_anything.social_trends.core import account as acct_mod
from cli_anything.social_trends.core import theme_pages as theme_mod

# ── Global state ──────────────────────────────────────────────────────────────

_session: Optional[Session] = None
_json_output: bool = False


def get_session() -> Session:
    global _session
    if _session is None:
        _session = Session()
    return _session


# ── Output helpers ─────────────────────────────────────────────────────────────

def output(data: Any, message: str = "") -> None:
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)


def _print_dict(d: dict, indent: int = 2) -> None:
    pad = " " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{pad}{k}:")
            _print_dict(v, indent + 2)
        elif isinstance(v, list):
            if v and isinstance(v[0], dict):
                click.echo(f"{pad}{k}: [{len(v)} items]")
                for item in v[:5]:
                    _print_dict(item, indent + 4)
                if len(v) > 5:
                    click.echo(f"{' ' * (indent + 4)}... and {len(v) - 5} more")
            else:
                click.echo(f"{pad}{k}: {v}")
        else:
            click.echo(f"{pad}{k}: {v}")


def _print_list(lst: list) -> None:
    if not lst:
        click.echo("  (empty)")
        return
    for i, item in enumerate(lst):
        if isinstance(item, dict):
            parts = []
            for k, v in item.items():
                if not isinstance(v, (dict, list)):
                    parts.append(f"{k}={v}")
            click.echo(f"  [{i+1}] " + "  ".join(parts))
        else:
            click.echo(f"  {item}")


def _err(msg: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": msg}))
    else:
        click.echo(f"Error: {msg}", err=True)
    sys.exit(1)


# ── Root ───────────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output structured JSON")
@click.pass_context
def cli(ctx: click.Context, use_json: bool) -> None:
    """Social Trends CLI — scrape viral trends, optimize accounts, build theme pages."""
    global _json_output
    _json_output = use_json
    if ctx.invoked_subcommand is None:
        _launch_repl()


# ── Trends ─────────────────────────────────────────────────────────────────────

@cli.group()
def trends() -> None:
    """Fetch and analyze viral trends from YouTube and TikTok."""


@trends.command("youtube")
@click.option("--region", default="US", show_default=True, help="Region code (e.g. US, GB, AU)")
@click.option("--category", default="all", show_default=True,
              help="Category: all, music, gaming, entertainment, news, sports, tech")
@click.option("--max", "max_results", default=20, show_default=True, help="Number of results (max 50)")
def trends_youtube(region: str, category: str, max_results: int) -> None:
    """Fetch YouTube trending videos, hashtags, and music signals."""
    try:
        sess = get_session()
        api_key = sess.get_youtube_api_key()
        data = yt_mod.fetch_trending(
            api_key=api_key or None,
            region=region,
            category=category,
            max_results=max_results,
        )
        output(data, f"YouTube trending ({region}, {category}): {data['total']} videos")
    except Exception as e:
        _err(str(e))


@trends.command("tiktok")
@click.option("--region", default="US", show_default=True, help="Region code (e.g. US, GB, AU)")
@click.option("--period", default=7, show_default=True, type=click.Choice(["7", "30", "120"]),
              help="Trend period in days")
@click.option("--limit", default=20, show_default=True, help="Number of hashtags (max 50)")
def trends_tiktok(region: str, period: str, limit: int) -> None:
    """Fetch TikTok trending hashtags from the Creative Center."""
    try:
        data = tt_mod.fetch_trending_hashtags(
            region=region,
            period_days=int(period),
            limit=limit,
        )
        output(data, f"TikTok trending hashtags ({region}, last {period} days): {data['total']} found")
    except Exception as e:
        _err(str(e))


@trends.command("tiktok-music")
@click.option("--region", default="US", show_default=True, help="Region code")
@click.option("--period", default=7, show_default=True, type=click.Choice(["7", "30", "120"]))
@click.option("--limit", default=20, show_default=True)
def trends_tiktok_music(region: str, period: str, limit: int) -> None:
    """Fetch TikTok trending sounds and music."""
    try:
        data = tt_mod.fetch_trending_music(
            region=region,
            period_days=int(period),
            limit=limit,
        )
        output(data, f"TikTok trending sounds ({region}): {data['total']} found")
    except Exception as e:
        _err(str(e))


@trends.command("tiktok-creators")
@click.option("--region", default="US", show_default=True)
@click.option("--period", default=7, show_default=True, type=click.Choice(["7", "30", "120"]))
@click.option("--limit", default=20, show_default=True)
def trends_tiktok_creators(region: str, period: str, limit: int) -> None:
    """Fetch trending TikTok creators to model and collaborate with."""
    try:
        data = tt_mod.fetch_trending_creators(region=region, period_days=int(period), limit=limit)
        output(data, f"TikTok trending creators ({region}): {data['total']} found")
    except Exception as e:
        _err(str(e))


@trends.command("music")
@click.option("--region", default="US", show_default=True)
@click.option("--chart", default="regional", show_default=True,
              type=click.Choice(["regional", "viral"]))
@click.option("--frequency", default="weekly", show_default=True,
              type=click.Choice(["weekly", "daily"]))
def trends_music(region: str, chart: str, frequency: str) -> None:
    """Fetch Spotify chart data for trending music."""
    try:
        data = music_mod.fetch_spotify_chart(region=region, chart=chart, frequency=frequency)
        output(data, f"Spotify {chart} chart ({region}, {frequency}): {data['total']} tracks")
    except Exception as e:
        _err(str(e))


@trends.command("music-safe")
def trends_music_safe() -> None:
    """Show copyright-safe music options for each platform."""
    data = music_mod.get_safe_for_use_music_tips()
    output(data, "Copyright-safe music guide:")


@trends.command("niche-hashtags")
@click.argument("keywords", nargs=-1, required=True)
@click.option("--region", default="US", show_default=True)
@click.option("--period", default=7, show_default=True, type=click.Choice(["7", "30", "120"]))
def trends_niche_hashtags(keywords: tuple, region: str, period: str) -> None:
    """Find trending TikTok hashtags relevant to your niche keywords.

    Example: social-trends trends niche-hashtags fitness gym workout
    """
    try:
        data = tt_mod.analyze_niche_hashtags(
            niche_keywords=list(keywords),
            region=region,
            period_days=int(period),
        )
        output(data, f"Niche hashtag analysis for: {', '.join(keywords)}")
    except Exception as e:
        _err(str(e))


# ── Hashtags ───────────────────────────────────────────────────────────────────

@cli.group()
def hashtags() -> None:
    """Hashtag analysis, scoring, and strategy generation."""


@hashtags.command("strategy")
@click.argument("niche")
@click.option("--platform", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "instagram", "youtube", "twitter", "linkedin"]))
def hashtags_strategy(niche: str, platform: str) -> None:
    """Generate a tiered hashtag strategy for your niche and platform."""
    data = hash_mod.generate_hashtag_strategy(niche=niche, platform=platform)
    output(data, f"Hashtag strategy for '{niche}' on {platform}:")


@hashtags.command("score")
@click.argument("tags", nargs=-1, required=True)
def hashtags_score(tags: tuple) -> None:
    """Score a set of hashtags for balance of competition tiers.

    Example: social-trends hashtags score #fitness #gym #workout #fitlife
    """
    dummy_counts = {}
    data = hash_mod.score_hashtag_set(list(tags), dummy_counts)
    output(data, f"Hashtag set score for {len(tags)} tags:")


@hashtags.command("caption")
@click.argument("caption")
@click.option("--platform", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]))
def hashtags_caption(caption: str, platform: str) -> None:
    """Analyze hashtags in a caption draft and suggest improvements."""
    data = hash_mod.suggest_caption_hashtags(caption=caption, platform=platform)
    output(data, "Caption hashtag analysis:")


# ── Account ────────────────────────────────────────────────────────────────────

@cli.group()
def account() -> None:
    """Account management, optimization, and growth planning."""


@account.command("add")
@click.argument("platform")
@click.argument("handle")
@click.option("--notes", default="", help="Optional notes about this account")
def account_add(platform: str, handle: str, notes: str) -> None:
    """Add an account to track.

    Example: social-trends account add tiktok @myhandle
    """
    try:
        record = get_session().add_account(platform=platform, handle=handle, notes=notes)
        output(record, f"Added account: @{handle} on {platform}")
    except Exception as e:
        _err(str(e))


@account.command("list")
def account_list() -> None:
    """List all tracked accounts."""
    accounts = get_session().list_accounts()
    output(accounts, f"Tracked accounts: {len(accounts)}")


@account.command("remove")
@click.argument("account_id")
def account_remove(account_id: str) -> None:
    """Remove a tracked account by ID."""
    try:
        removed = get_session().remove_account(account_id)
        output(removed, f"Removed account: {removed['handle']}")
    except Exception as e:
        _err(str(e))


@account.command("audit")
@click.argument("platform")
@click.argument("handle")
@click.option("--bio", default=None, help="Your current bio text")
@click.option("--followers", default=0, type=int)
@click.option("--following", default=0, type=int)
@click.option("--posts", default=0, type=int)
@click.option("--has-link/--no-link", default=False, help="Do you have a link in bio?")
@click.option("--posts-per-week", default=0.0, type=float)
@click.option("--avg-views", default=0, type=int)
@click.option("--avg-likes", default=0, type=int)
def account_audit(
    platform: str, handle: str, bio: Optional[str],
    followers: int, following: int, posts: int,
    has_link: bool, posts_per_week: float,
    avg_views: int, avg_likes: int,
) -> None:
    """Audit an account's profile and engagement health."""
    data = acct_mod.audit_account(
        platform=platform,
        handle=handle,
        bio=bio,
        follower_count=followers,
        following_count=following,
        post_count=posts,
        has_link=has_link,
        posting_frequency_per_week=posts_per_week,
        avg_views=avg_views,
        avg_likes=avg_likes,
    )
    output(data, f"Account audit for @{handle} on {platform}: Grade {data['grade']} ({data['score']}/100)")


@account.command("posting-times")
@click.argument("platform")
@click.option("--timezone", default="UTC", show_default=True)
def account_posting_times(platform: str, timezone: str) -> None:
    """Get optimal posting times for a platform."""
    try:
        data = acct_mod.get_best_posting_times(platform=platform, timezone=timezone)
        output(data, f"Best posting times for {platform} ({timezone}):")
    except Exception as e:
        _err(str(e))


@account.command("roadmap")
@click.argument("platform")
@click.argument("niche")
@click.option("--current", default=0, type=int, help="Current follower count")
@click.option("--target", default=10000, type=int, help="Target follower count")
@click.option("--days", default=90, type=int, show_default=True)
def account_roadmap(platform: str, niche: str, current: int, target: int, days: int) -> None:
    """Generate a growth roadmap to hit your follower target."""
    data = acct_mod.generate_growth_roadmap(
        platform=platform,
        current_followers=current,
        target_followers=target,
        niche=niche,
        days=days,
    )
    output(data, f"{days}-day growth roadmap: {current} → {target} followers on {platform}")


@account.command("cross-platform")
@click.argument("platforms", nargs=-1, required=True)
@click.argument("niche")
@click.option("--primary", default="tiktok", show_default=True)
def account_cross_platform(platforms: tuple, niche: str, primary: str) -> None:
    """Generate a cross-platform content repurposing strategy.

    Example: social-trends account cross-platform tiktok instagram youtube fitness --primary tiktok
    """
    data = acct_mod.cross_platform_strategy(
        platforms=list(platforms),
        niche=niche,
        primary_platform=primary,
    )
    output(data, f"Cross-platform strategy for {niche}:")


# ── Theme pages ────────────────────────────────────────────────────────────────

@cli.group()
def theme() -> None:
    """Theme page creation — niches, launch plans, content strategy."""


@theme.command("niches")
@click.option("--min-monetization", default=None,
              type=click.Choice(["medium", "high", "very_high"]),
              help="Filter by minimum monetization potential")
@click.option("--platform", default=None, help="Filter by platform (e.g. tiktok, instagram)")
def theme_niches(min_monetization: Optional[str], platform: Optional[str]) -> None:
    """List profitable theme page niches with monetization details."""
    data = theme_mod.list_niches(min_monetization=min_monetization, platform_filter=platform)
    output(data, f"Available niches: {data['total']}")


@theme.command("details")
@click.argument("slug")
def theme_details(slug: str) -> None:
    """Get full details for a specific niche.

    Slugs: luxury, motivation, memes, fitness, finance, pets, food, travel, gaming, crypto
    """
    try:
        data = theme_mod.get_niche_details(slug)
        output(data, f"Niche details: {data['name']}")
    except Exception as e:
        _err(str(e))


@theme.command("launch-plan")
@click.argument("niche_slug")
@click.option("--platform", default="instagram", show_default=True,
              type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]))
@click.option("--budget", default=0, type=int, help="Monthly budget in USD (0 = organic only)")
def theme_launch_plan(niche_slug: str, platform: str, budget: int) -> None:
    """Generate a step-by-step theme page launch plan."""
    try:
        data = theme_mod.get_theme_page_launch_plan(
            niche_slug=niche_slug,
            platform=platform,
            budget_usd=budget,
        )
        output(data, f"Launch plan for '{niche_slug}' on {platform}:")
    except Exception as e:
        _err(str(e))


@theme.command("repurposing")
@click.argument("niche_slug")
def theme_repurposing(niche_slug: str) -> None:
    """Get a content repurposing guide — turn 1 video into 10+ posts."""
    try:
        data = theme_mod.get_content_repurposing_guide(niche_slug)
        output(data, f"Content repurposing guide for {data['niche']}:")
    except Exception as e:
        _err(str(e))


@theme.command("ctas")
@click.argument("niche_slug")
@click.option("--platform", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "instagram", "youtube"]))
def theme_ctas(niche_slug: str, platform: str) -> None:
    """Get proven CTA templates and hook formulas for your theme page."""
    try:
        data = theme_mod.get_converting_cta_templates(niche_slug=niche_slug, platform=platform)
        output(data, f"CTA templates for '{niche_slug}' on {platform}:")
    except Exception as e:
        _err(str(e))


# ── Config ─────────────────────────────────────────────────────────────────────

@cli.group()
def config() -> None:
    """Manage API keys and global settings."""


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str) -> None:
    """Set a config value (stored in ~/.cli-anything/social-trends.json).

    Keys: youtube_api_key, tiktok_session_id, default_region, cache_ttl_minutes
    """
    get_session().set_config_value(key, value)
    click.echo(f"Set {key} = {'*' * min(len(value), 8) if 'key' in key.lower() else value}")


@config.command("show")
def config_show() -> None:
    """Show current config (API keys are masked)."""
    cfg = get_session().get_config()
    for k, v in cfg.items():
        if "key" in k.lower() or "secret" in k.lower() or "token" in k.lower():
            display = ("*" * 8 + str(v)[-4:]) if v else "(not set)"
        else:
            display = v
        click.echo(f"  {k}: {display}")


# ── REPL ────────────────────────────────────────────────────────────────────────

def _launch_repl() -> None:
    """Launch an interactive REPL session."""
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import InMemoryHistory
        from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
        from prompt_toolkit.styles import Style

        style = Style.from_dict({
            "prompt": "#00d4ff bold",
        })
        session = PromptSession(
            history=InMemoryHistory(),
            auto_suggest=AutoSuggestFromHistory(),
            style=style,
        )
    except ImportError:
        session = None

    _print_banner()

    while True:
        try:
            if session:
                line = session.prompt("social-trends> ", style=style if style else None)
            else:
                line = input("social-trends> ")
        except (EOFError, KeyboardInterrupt):
            click.echo("\nGoodbye!")
            break

        line = line.strip()
        if not line:
            continue
        if line in ("exit", "quit", "q"):
            click.echo("Goodbye!")
            break
        if line in ("help", "?"):
            _print_help()
            continue

        import shlex
        try:
            args = shlex.split(line)
        except ValueError as e:
            click.echo(f"Parse error: {e}")
            continue

        try:
            cli.main(args=args, standalone_mode=False)
        except SystemExit:
            pass
        except Exception as e:
            click.echo(f"Error: {e}")


def _print_banner() -> None:
    click.echo("\033[96m")
    click.echo("  ╔══════════════════════════════════════════════════════╗")
    click.echo("  ║         SOCIAL TRENDS CLI  v1.0  — CLI-Anything      ║")
    click.echo("  ║   Viral trends · Hashtags · Music · Account Growth    ║")
    click.echo("  ╚══════════════════════════════════════════════════════╝")
    click.echo("\033[0m")
    click.echo("  Type \033[93mhelp\033[0m or a command. \033[93mexit\033[0m to quit.\n")


def _print_help() -> None:
    click.echo("""
  \033[96mTREND COMMANDS\033[0m
    trends youtube [--region US] [--category music] [--max 20]
    trends tiktok [--region US] [--period 7]
    trends tiktok-music [--region US]
    trends tiktok-creators [--region US]
    trends music [--region US] [--chart regional] [--frequency weekly]
    trends music-safe
    trends niche-hashtags <keyword1> [keyword2 ...]

  \033[96mHASHTAG COMMANDS\033[0m
    hashtags strategy <niche> [--platform tiktok]
    hashtags score #tag1 #tag2 #tag3
    hashtags caption "<caption text>" [--platform tiktok]

  \033[96mACCOUNT COMMANDS\033[0m
    account add <platform> <handle>
    account list
    account audit <platform> <handle> [--followers N] [--bio "text"]
    account posting-times <platform> [--timezone EST]
    account roadmap <platform> <niche> [--current 0] [--target 10000]
    account cross-platform <p1> <p2> ... <niche> [--primary tiktok]

  \033[96mTHEME PAGE COMMANDS\033[0m
    theme niches [--min-monetization high] [--platform tiktok]
    theme details <slug>
    theme launch-plan <slug> [--platform instagram] [--budget 0]
    theme repurposing <slug>
    theme ctas <slug> [--platform tiktok]

  \033[96mCONFIG\033[0m
    config set youtube_api_key YOUR_KEY
    config show
""")


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    cli()


if __name__ == "__main__":
    main()
