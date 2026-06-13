"""viral-trends CLI — Agent-native social media trend intelligence.

Usage:
    viral-trends [--json] <command> [args]
    viral-trends  (launches interactive REPL)

Commands:
    trends     youtube | tiktok | cross    — Fetch platform trending data
    hashtags   analyze | build | filter    — Hashtag analysis + set builder
    music      trending | guide            — Trending music/sounds
    account    add | list | update | remove | analyze | schedule | caption | bio
    theme-page guide | niches | convert | acquire
    config     set | get | clear-cache
    history    [--limit N]
"""

from __future__ import annotations

import json
import shlex
import sys
from typing import Any, Optional

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory

from cli_anything.viral_trends.core import (
    youtube_scraper,
    tiktok_scraper,
    hashtag_analyzer,
    music_tracker,
    account_optimizer,
    theme_page_guide,
)
from cli_anything.viral_trends.utils import state as state_mod

# ── Global state ──────────────────────────────────────────────────────────────

_json_output: bool = False


def _out(data: Any, message: str = "") -> None:
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(click.style(message, bold=True))
        _pretty(data)


def _pretty(data: Any, indent: int = 0) -> None:
    pad = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{pad}{click.style(k, fg='cyan')}:")
                _pretty(v, indent + 1)
            else:
                click.echo(f"{pad}{click.style(k, fg='cyan')}: {v}")
    elif isinstance(data, list):
        if not data:
            click.echo(f"{pad}(empty)")
            return
        for i, item in enumerate(data):
            if isinstance(item, dict):
                click.echo(f"{pad}{click.style(f'[{i}]', fg='yellow')}")
                _pretty(item, indent + 1)
            else:
                click.echo(f"{pad}- {item}")
    else:
        click.echo(f"{pad}{data}")


def _err(msg: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": msg}))
    else:
        click.echo(click.style(f"Error: {msg}", fg="red"), err=True)


def _ok(msg: str) -> None:
    if not _json_output:
        click.echo(click.style(f"✓ {msg}", fg="green"))


# ── Root group ────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output JSON")
@click.pass_context
def main(ctx: click.Context, use_json: bool) -> None:
    """viral-trends — scrape viral trends, optimize accounts, and convert theme pages."""
    global _json_output
    _json_output = use_json

    if ctx.invoked_subcommand is None:
        _launch_repl()


# ── trends ────────────────────────────────────────────────────────────────────

@main.group()
def trends() -> None:
    """Fetch trending content from YouTube and TikTok."""


@trends.command("youtube")
@click.option("--category", default="all", show_default=True,
              type=click.Choice(["all", "music", "gaming", "films", "shorts"]),
              help="Trending category")
@click.option("--limit", default=20, show_default=True, help="Max results (1-50)")
@click.option("--refresh", is_flag=True, help="Bypass cache")
def trends_youtube(category: str, limit: int, refresh: bool) -> None:
    """Fetch YouTube trending videos and extract hashtags."""
    try:
        videos = youtube_scraper.get_trending(category, limit, force_refresh=refresh)
        _out(videos, f"YouTube Trending ({category}) — {len(videos)} videos")
        state_mod.record_command("trends youtube", f"{len(videos)} videos fetched")
    except Exception as exc:
        _err(str(exc))
        sys.exit(1)


@trends.command("tiktok")
@click.option("--niche", default="", help="Filter by niche keyword")
@click.option("--limit", default=20, show_default=True, help="Max results")
@click.option("--refresh", is_flag=True, help="Bypass cache")
def trends_tiktok(niche: str, limit: int, refresh: bool) -> None:
    """Fetch TikTok viral hashtags and trending sounds."""
    try:
        hashtags = tiktok_scraper.get_trending_hashtags(niche, limit, force_refresh=refresh)
        sounds   = tiktok_scraper.get_trending_sounds(limit=10, force_refresh=refresh)
        result = {"trending_hashtags": hashtags, "trending_sounds": sounds}
        _out(result, f"TikTok Trends — {len(hashtags)} hashtags, {len(sounds)} sounds")
        state_mod.record_command("trends tiktok", f"{len(hashtags)} hashtags")
    except Exception as exc:
        _err(str(exc))
        sys.exit(1)


@trends.command("cross")
@click.option("--limit", default=20, show_default=True, help="Max results per platform")
@click.option("--refresh", is_flag=True, help="Bypass cache")
def trends_cross(limit: int, refresh: bool) -> None:
    """Cross-platform trend comparison (YouTube + TikTok)."""
    try:
        yt = youtube_scraper.get_trending("all", limit, force_refresh=refresh)
        tt = tiktok_scraper.get_trending_hashtags(limit=limit, force_refresh=refresh)
        sounds = music_tracker.get_cross_platform_music(limit=limit)
        result = {
            "youtube_trending": yt[:10],
            "tiktok_trending":  tt[:10],
            "cross_platform_music": sounds.get("cross_platform", []),
            "usage_tips": sounds.get("usage_tips", []),
        }
        _out(result, "Cross-Platform Trend Report")
        state_mod.record_command("trends cross", "cross-platform report generated")
    except Exception as exc:
        _err(str(exc))
        sys.exit(1)


# ── hashtags ──────────────────────────────────────────────────────────────────

@main.group()
def hashtags() -> None:
    """Analyze and build optimized hashtag sets."""


@hashtags.command("analyze")
@click.option("--niche", default="", help="Filter to niche keyword")
@click.option("--limit", default=30, show_default=True)
@click.option("--refresh", is_flag=True)
def hashtags_analyze(niche: str, limit: int, refresh: bool) -> None:
    """Rank hashtags from both YouTube and TikTok by combined score."""
    try:
        yt_tags = youtube_scraper.get_all_hashtags("all", limit)
        tt_tags = tiktok_scraper.get_trending_hashtags(niche, limit, force_refresh=refresh)
        ranked  = hashtag_analyzer.analyze_hashtags(yt_tags, tt_tags)
        if niche:
            ranked = hashtag_analyzer.filter_by_niche(ranked, niche)
        _out(ranked[:limit], f"Hashtag Analysis — top {min(limit, len(ranked))} tags")
        state_mod.record_command("hashtags analyze", f"{len(ranked)} tags analyzed")
    except Exception as exc:
        _err(str(exc))
        sys.exit(1)


@hashtags.command("build")
@click.option("--niche", default="", help="Target niche")
@click.option("--limit", default=30, show_default=True, help="Max hashtags in set")
@click.option("--refresh", is_flag=True)
def hashtags_build(niche: str, limit: int, refresh: bool) -> None:
    """Build a posting-ready optimized hashtag set (balanced by competition tier)."""
    try:
        yt_tags = youtube_scraper.get_all_hashtags("all", 50)
        tt_tags = tiktok_scraper.get_trending_hashtags(niche or "", 50, force_refresh=refresh)
        ranked  = hashtag_analyzer.analyze_hashtags(yt_tags, tt_tags)
        result  = hashtag_analyzer.build_optimal_set(ranked, niche, limit)
        _out(result, f"Optimized Hashtag Set ({result['tag_count']} tags)")
        if not _json_output:
            click.echo(f"\n{click.style('Caption block ready to paste:', bold=True)}")
            click.echo(result["caption_block"])
        state_mod.record_command("hashtags build", f"{result['tag_count']} tags built")
    except Exception as exc:
        _err(str(exc))
        sys.exit(1)


@hashtags.command("filter")
@click.argument("niche")
@click.option("--limit", default=20, show_default=True)
def hashtags_filter(niche: str, limit: int) -> None:
    """Filter stored trends to a specific niche."""
    try:
        tt_tags = tiktok_scraper.get_trending_hashtags(niche, limit)
        _out(tt_tags, f"Niche '{niche}' hashtags — {len(tt_tags)} results")
    except Exception as exc:
        _err(str(exc))
        sys.exit(1)


# ── music ─────────────────────────────────────────────────────────────────────

@main.group()
def music() -> None:
    """Track trending music and sounds across platforms."""


@music.command("trending")
@click.option("--limit", default=20, show_default=True)
@click.option("--refresh", is_flag=True)
def music_trending(limit: int, refresh: bool) -> None:
    """Show trending sounds on TikTok and trending music on YouTube."""
    try:
        result = music_tracker.get_cross_platform_music(limit)
        _out(result, "Trending Music & Sounds")
        state_mod.record_command("music trending", "music trends fetched")
    except Exception as exc:
        _err(str(exc))
        sys.exit(1)


@music.command("guide")
def music_guide() -> None:
    """How to use trending music effectively without copyright strikes."""
    result = music_tracker.get_usage_guide()
    _out(result, "Music Usage Guide")


# ── account ───────────────────────────────────────────────────────────────────

@main.group()
def account() -> None:
    """Manage and optimize your social media accounts."""


@account.command("add")
@click.argument("handle")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "youtube_shorts", "instagram", "twitter_x"]),
              help="Platform")
@click.option("--niche", default="", help="Account niche")
@click.option("--followers", default=0, type=int)
@click.option("--following", default=0, type=int)
@click.option("--avg-views", default=0, type=int, help="Average views per post")
@click.option("--link", default="", help="Bio link")
def account_add(handle, platform, niche, followers, following, avg_views, link):
    """Register a social account for tracking and optimization."""
    result = account_optimizer.add_account(
        handle, platform, niche, followers, following, avg_views, link
    )
    _out(result, f"Account added: {platform}:{handle}")
    state_mod.record_command("account add", f"{platform}:{handle}")


@account.command("list")
def account_list() -> None:
    """List all tracked accounts."""
    accounts = account_optimizer.list_accounts()
    if not accounts:
        _out([], "No accounts registered. Use: viral-trends account add")
        return
    _out(accounts, f"Tracked Accounts ({len(accounts)})")


@account.command("update")
@click.argument("handle")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "youtube_shorts", "instagram", "twitter_x"]))
@click.option("--followers", type=int)
@click.option("--avg-views", type=int)
@click.option("--niche")
def account_update(handle, platform, followers, avg_views, niche) -> None:
    """Update account stats."""
    kwargs = {}
    if followers  is not None: kwargs["followers"]  = followers
    if avg_views  is not None: kwargs["avg_views"]  = avg_views
    if niche      is not None: kwargs["niche"]      = niche
    result = account_optimizer.update_account(handle, platform, **kwargs)
    if result is None:
        _err(f"Account {platform}:{handle} not found")
        sys.exit(1)
    _out(result, "Account updated")


@account.command("remove")
@click.argument("handle")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "youtube_shorts", "instagram", "twitter_x"]))
def account_remove(handle, platform) -> None:
    """Remove a tracked account."""
    if account_optimizer.remove_account(handle, platform):
        _ok(f"Removed {platform}:{handle}")
    else:
        _err(f"Account {platform}:{handle} not found")
        sys.exit(1)


@account.command("analyze")
@click.argument("handle")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "youtube_shorts", "instagram", "twitter_x"]))
def account_analyze(handle, platform) -> None:
    """Full optimization report for an account."""
    result = account_optimizer.analyze_account(handle, platform)
    _out(result, f"Optimization Report: {platform}:{handle}")
    state_mod.record_command("account analyze", f"{platform}:{handle}")


@account.command("schedule")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "youtube_shorts", "instagram", "twitter_x"]))
def account_schedule(platform) -> None:
    """Get optimal posting schedule for a platform."""
    result = account_optimizer.get_posting_schedule(platform)
    _out(result, f"Optimal Posting Schedule: {platform}")


@account.command("caption")
@click.option("--topic", required=True, help="Content topic")
@click.option("--hook", default="", help="Opening hook line")
@click.option("--body", default="", help="Main body text")
@click.option("--cta", default="Follow for more 🔥", help="Call to action")
@click.option("--niche", default="", help="Used to generate hashtags")
@click.option("--template", default=0, type=int, help="Caption template index (0–5)")
def account_caption(topic, hook, body, cta, niche, template) -> None:
    """Generate an optimized caption with hashtags."""
    try:
        tt_tags = tiktok_scraper.get_trending_hashtags(niche, 30)
        yt_tags = youtube_scraper.get_all_hashtags("all", 30)
        ranked  = hashtag_analyzer.analyze_hashtags(yt_tags, tt_tags)
        tag_set = hashtag_analyzer.build_optimal_set(ranked, niche, 20)
        hashtag_block = tag_set["caption_block"]

        caption = account_optimizer.generate_caption(
            template,
            topic=topic,
            hook=hook or f"Here's what you need to know about {topic}",
            body=body or f"[Add your {topic} content here]",
            cta=cta,
            hashtags=hashtag_block,
            n=1,
        )
        if _json_output:
            _out({"caption": caption, "hashtags": tag_set["optimal_set"]})
        else:
            click.echo(click.style("\n── Generated Caption ──", bold=True))
            click.echo(caption)
    except Exception as exc:
        _err(str(exc))
        sys.exit(1)


@account.command("bio")
@click.option("--template",
              type=click.Choice(["brand", "theme", "personal", "business"]),
              default="brand")
@click.option("--niche", default="[your niche]")
@click.option("--frequency", default="daily")
@click.option("--audience", default="everyone")
@click.option("--emoji", default="🔥")
@click.option("--name", default="")
@click.option("--cta", default="Follow for more")
@click.option("--link", default="")
@click.option("--brand-name", default="")
@click.option("--tagline", default="")
@click.option("--location", default="")
def account_bio(**kwargs) -> None:
    """Generate an optimized profile bio."""
    template = kwargs.pop("template")
    bio = account_optimizer.generate_bio(template, **kwargs)
    if _json_output:
        _out({"bio": bio, "template": template})
    else:
        click.echo(click.style("\n── Generated Bio ──", bold=True))
        click.echo(bio)


@account.command("playbook")
@click.option("--stage",
              type=click.Choice(["0_1k", "1k_10k", "10k_100k", "100k_plus"]),
              default="",
              help="Growth stage (empty = show all)")
def account_playbook(stage) -> None:
    """Show the growth playbook for your current follower stage."""
    result = account_optimizer.get_growth_playbook(stage)
    _out(result, "Growth Playbook")


# ── theme-page ────────────────────────────────────────────────────────────────

@main.group("theme-page")
def theme_page() -> None:
    """Theme page creation, acquisition, and conversion guide."""


@theme_page.command("guide")
@click.option("--section", default="", help="Specific guide section")
def theme_page_guide_cmd(section: str) -> None:
    """Full theme page playbook."""
    if section:
        result = theme_page_guide.get_section(section)
        if result is None:
            _err(f"Section '{section}' not found. Available: {', '.join(theme_page_guide.list_sections())}")
            sys.exit(1)
    else:
        result = theme_page_guide.get_full_guide()
    _out(result, "Theme Page Guide")
    state_mod.record_command("theme-page guide", section or "full")


@theme_page.command("niches")
def theme_page_niches() -> None:
    """Best niches for theme pages with monetization potential."""
    result = theme_page_guide.get_niches()
    _out(result, "Best Theme Page Niches")


@theme_page.command("convert")
def theme_page_convert() -> None:
    """Step-by-step guide for converting a theme page to a branded channel."""
    steps = theme_page_guide.get_conversion_steps()
    guide = theme_page_guide.get_section("converting_a_theme_page")
    _out(guide, "Theme Page Conversion Playbook")


@theme_page.command("acquire")
def theme_page_acquire() -> None:
    """Guide for finding and buying existing theme pages."""
    result = theme_page_guide.get_acquisition_guide()
    _out(result, "Theme Page Acquisition Guide")


@theme_page.command("sections")
def theme_page_sections() -> None:
    """List available guide sections."""
    sections = theme_page_guide.list_sections()
    _out(sections, "Available Guide Sections")


# ── config ────────────────────────────────────────────────────────────────────

@main.group()
def config() -> None:
    """Configuration and cache management."""


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str) -> None:
    """Set a configuration preference."""
    state_mod.set_pref(key, value)
    _ok(f"Set {key} = {value}")


@config.command("get")
@click.argument("key")
def config_get(key: str) -> None:
    """Get a configuration preference."""
    val = state_mod.get_pref(key)
    _out({"key": key, "value": val})


@config.command("clear-cache")
def config_clear_cache() -> None:
    """Clear all cached trend data (forces fresh scrape on next run)."""
    import shutil
    cache_dir = Path.home() / ".config" / "viral-trends" / "cache"
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    _ok("Cache cleared")


# ── history ───────────────────────────────────────────────────────────────────

@main.command()
@click.option("--limit", default=20, show_default=True)
def history(limit: int) -> None:
    """Show command history."""
    h = state_mod.get_history(limit)
    _out(h, f"Command History (last {limit})")


# ── REPL ──────────────────────────────────────────────────────────────────────

BANNER = """
╔═══════════════════════════════════════════════════════╗
║          viral-trends  ·  CLI-Anything                ║
║  YouTube + TikTok trend intelligence for creators     ║
╚═══════════════════════════════════════════════════════╝
Type a command or 'help' to list commands. Ctrl+D to exit.
"""


def _launch_repl() -> None:
    click.echo(click.style(BANNER, fg="magenta", bold=True))

    session: PromptSession = PromptSession(
        history=InMemoryHistory(),
        auto_suggest=AutoSuggestFromHistory(),
    )

    while True:
        try:
            line = session.prompt("viral-trends> ").strip()
        except (EOFError, KeyboardInterrupt):
            click.echo("\nGoodbye!")
            break

        if not line:
            continue
        if line.lower() in ("exit", "quit", "q"):
            break
        if line.lower() == "help":
            click.echo(__doc__)
            continue

        try:
            args = shlex.split(line)
            main.main(args, standalone_mode=False)
        except SystemExit:
            pass
        except Exception as exc:
            _err(str(exc))


if __name__ == "__main__":
    main()
