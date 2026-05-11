"""Social Trends CLI — agent-native viral trend intelligence for social media.

Provides CLI commands for:
  • Scraping YouTube and TikTok trending content
  • Analysing viral hashtags and music
  • Optimising social media accounts
  • Building and monetising theme pages

Usage:
    python3 -m cli_anything.social_trends [--json] <command>
    python3 -m cli_anything.social_trends  (launches REPL)
"""

from __future__ import annotations

import json
import shlex
import sys
from typing import Any, Optional

import click

from cli_anything.social_trends.core import youtube as yt_mod
from cli_anything.social_trends.core import tiktok as tt_mod
from cli_anything.social_trends.core import hashtags as tag_mod
from cli_anything.social_trends.core import music as music_mod
from cli_anything.social_trends.core import account as acct_mod
from cli_anything.social_trends.core import theme_page as theme_mod

# ── Global state ──────────────────────────────────────────────────────────────

_json_output: bool = False
_repl_mode: bool = False


# ── Output helpers ────────────────────────────────────────────────────────────

def output(data: Any, message: str = "") -> None:
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        _pretty_print(data)


def _pretty_print(data: Any, indent: int = 0) -> None:
    pad = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)) and v:
                click.echo(f"{pad}{_bold(k)}:")
                _pretty_print(v, indent + 1)
            else:
                click.echo(f"{pad}{_bold(k)}: {v}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                click.echo(f"{pad}─")
                _pretty_print(item, indent + 1)
            else:
                click.echo(f"{pad}• {item}")


def _bold(s: str) -> str:
    import os
    if os.isatty(1):
        return f"\033[1m{s}\033[0m"
    return s


def _err(msg: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": msg}), err=True)
    else:
        click.echo(f"Error: {msg}", err=True)


def handle_error(func):
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, FileNotFoundError, RuntimeError, KeyError) as e:
            _err(str(e))
            if not _repl_mode:
                sys.exit(1)
        except Exception as e:
            _err(f"Unexpected error: {e}")
            if not _repl_mode:
                sys.exit(1)

    return wrapper


# ── Root group ────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output results as JSON")
@click.version_option("1.0.0", prog_name="social-trends")
@click.pass_context
def cli(ctx: click.Context, use_json: bool) -> None:
    """Social Trends CLI — viral trend intelligence for social media accounts.

    \b
    Quick start:
      social-trends tiktok hashtags --limit 20
      social-trends youtube trending --category music
      social-trends hashtags recommend --niche fitness
      social-trends music trending --genre pop
      social-trends account optimize tiktok
      social-trends theme-page niches
      social-trends theme-page playbook
    """
    global _json_output
    _json_output = use_json
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ═════════════════════════════════════════════════════════════════════════════
# TIKTOK group
# ═════════════════════════════════════════════════════════════════════════════

@cli.group()
def tiktok():
    """TikTok trending data — hashtags, sounds, and full snapshot."""
    pass


@tiktok.command("hashtags")
@click.option("--limit", default=30, show_default=True, help="Max number of hashtags to return")
@handle_error
def tiktok_hashtags(limit: int) -> None:
    """Scrape TikTok trending hashtags from the Discover page."""
    if not _json_output:
        click.echo("Fetching TikTok trending hashtags …", err=True)
    result = tt_mod.fetch_trending_hashtags(limit=limit)
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"TikTok Trending Hashtags ({result['count']} results)")
        skin.table(
            ["Rank", "Hashtag", "Views", "Platform"],
            [
                [str(i + 1), h["hashtag"], h.get("view_count_fmt", "N/A"), "tiktok"]
                for i, h in enumerate(result["hashtags"])
            ],
        )
        if result.get("scrape_error"):
            skin.warn(f"Scrape note: {result['scrape_error']} — showing seed data")
    else:
        output(result)


@tiktok.command("sounds")
@click.option("--limit", default=20, show_default=True, help="Max sounds to return")
@handle_error
def tiktok_sounds(limit: int) -> None:
    """Scrape TikTok trending sounds and music."""
    if not _json_output:
        click.echo("Fetching TikTok trending sounds …", err=True)
    result = tt_mod.fetch_trending_sounds(limit=limit)
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"TikTok Trending Sounds ({result['count']} results)")
        skin.table(
            ["Rank", "Title", "Artist", "Uses", "Duration"],
            [
                [
                    str(i + 1),
                    s["title"][:35],
                    s.get("artist", "Unknown")[:25],
                    s.get("use_count_fmt", "N/A"),
                    str(s.get("duration_sec", "")) + "s" if s.get("duration_sec") else "-",
                ]
                for i, s in enumerate(result["sounds"])
            ],
        )
    else:
        output(result)


@tiktok.command("all")
@click.option("--hashtags", "hashtag_limit", default=20, show_default=True)
@click.option("--sounds", "sound_limit", default=10, show_default=True)
@handle_error
def tiktok_all(hashtag_limit: int, sound_limit: int) -> None:
    """Fetch TikTok trending hashtags AND sounds in one call."""
    if not _json_output:
        click.echo("Fetching all TikTok trends …", err=True)
    result = tt_mod.fetch_all_tiktok_trends(
        hashtag_limit=hashtag_limit,
        sound_limit=sound_limit,
    )
    output(result, f"TikTok snapshot — {result['hashtag_count']} hashtags, {result['sound_count']} sounds")


# ═════════════════════════════════════════════════════════════════════════════
# YOUTUBE group
# ═════════════════════════════════════════════════════════════════════════════

@cli.group()
def youtube():
    """YouTube trending data — videos, hashtags, and music."""
    pass


@youtube.command("trending")
@click.option(
    "--category", default="now", show_default=True,
    type=click.Choice(["now", "music", "gaming", "movies"], case_sensitive=False),
    help="Trending category",
)
@click.option("--limit", default=25, show_default=True, help="Max videos to return")
@click.option("--region", default="US", show_default=True, help="ISO-3166 country code")
@handle_error
def youtube_trending(category: str, limit: int, region: str) -> None:
    """Scrape YouTube trending videos for a category."""
    if not _json_output:
        click.echo(f"Fetching YouTube trending [{category}] …", err=True)
    result = yt_mod.fetch_trending(category=category, limit=limit, region=region)
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"YouTube Trending [{category.upper()}] — {result['region']} ({result['count']} videos)")
        skin.table(
            ["#", "Title", "Channel", "Views", "Published"],
            [
                [
                    str(i + 1),
                    v["title"][:40],
                    v.get("channel", "")[:20],
                    v.get("view_count_fmt", ""),
                    v.get("published", ""),
                ]
                for i, v in enumerate(result["videos"])
            ],
        )
    else:
        output(result)


@youtube.command("hashtags")
@click.option("--category", default="now", show_default=True)
@click.option("--limit", default=25, show_default=True)
@click.option("--region", default="US", show_default=True)
@handle_error
def youtube_hashtags(category: str, limit: int, region: str) -> None:
    """Extract hashtags from YouTube trending videos."""
    if not _json_output:
        click.echo("Fetching YouTube trending and extracting hashtags …", err=True)
    result = yt_mod.fetch_trending(category=category, limit=limit, region=region)
    tags = yt_mod.extract_hashtags_from_videos(result["videos"])
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"Hashtags from YouTube Trending [{category}]")
        skin.table(
            ["#", "Hashtag", "Mentions"],
            [[str(i + 1), t["hashtag"], str(t["mentions"])] for i, t in enumerate(tags[:30])],
        )
    else:
        output({"source": "youtube", "category": category, "hashtags": tags})


@youtube.command("music")
@click.option("--category", default="music", show_default=True)
@click.option("--limit", default=20, show_default=True)
@click.option("--region", default="US", show_default=True)
@handle_error
def youtube_music(category: str, limit: int, region: str) -> None:
    """Extract music references from YouTube trending videos."""
    if not _json_output:
        click.echo("Extracting music from YouTube trending …", err=True)
    result = yt_mod.fetch_trending(category=category, limit=limit, region=region)
    music = yt_mod.extract_music_from_videos(result["videos"])
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"Music from YouTube Trending [{category}]")
        skin.table(
            ["#", "Track", "Channel", "Source Video"],
            [[str(i + 1), m["track"][:35], m.get("channel", "")[:20], m.get("source_video", "")]
             for i, m in enumerate(music[:20])],
        )
    else:
        output({"source": "youtube", "category": category, "music": music})


@youtube.command("all-categories")
@click.option("--limit", default=10, show_default=True, help="Videos per category")
@click.option("--region", default="US", show_default=True)
@handle_error
def youtube_all_categories(limit: int, region: str) -> None:
    """Fetch trending videos across ALL YouTube categories."""
    if not _json_output:
        click.echo("Fetching all YouTube trending categories …", err=True)
    result = yt_mod.fetch_trending_all_categories(limit_per_cat=limit, region=region)
    output(result, f"YouTube all-categories snapshot — region: {result['region']}")


# ═════════════════════════════════════════════════════════════════════════════
# HASHTAGS group
# ═════════════════════════════════════════════════════════════════════════════

@cli.group()
def hashtags():
    """Hashtag analysis — recommendations, caption audit, cross-platform merge."""
    pass


@hashtags.command("recommend")
@click.option(
    "--niche", required=True,
    help="Content niche (run 'hashtags niches' to list options)",
)
@click.option(
    "--platform", default="all", show_default=True,
    type=click.Choice(["all", "tiktok", "youtube"], case_sensitive=False),
)
@click.option("--limit", default=30, show_default=True)
@click.option(
    "--no-universal", "no_universal", is_flag=True,
    help="Exclude universal viral tags (fyp, foryou, etc.)",
)
@handle_error
def hashtags_recommend(niche: str, platform: str, limit: int, no_universal: bool) -> None:
    """Generate a recommended hashtag pack for a niche and platform."""
    result = tag_mod.recommend_hashtags(
        niche=niche,
        platform=platform,
        limit=limit,
        include_universal=not no_universal,
    )
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"Hashtag Pack — {niche} / {platform}")
        skin.table(
            ["Rank", "Hashtag", "Source", "Weight"],
            [[str(t["rank"]), t["hashtag"], t["source"], str(t["weight"])]
             for t in result["hashtags"]],
        )
        click.echo(f"\n{_bold('Copy-paste:')}\n{result['copy_paste']}\n")
    else:
        output(result)


@hashtags.command("audit")
@click.argument("caption")
@handle_error
def hashtags_audit(caption: str) -> None:
    """Audit hashtags in an existing caption string."""
    result = tag_mod.analyse_caption(caption)
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section("Caption Hashtag Audit")
        click.echo(f"  Hashtag count:   {result['hashtag_count']}")
        click.echo(f"  Unique hashtags: {len(result['unique_hashtags'])}")
        click.echo(f"  Score:           {result['score']}/100")
        click.echo(f"  Duplicates:      {', '.join(result['duplicates']) or 'none'}")
        click.echo(f"  Universal tags:  {', '.join(result['universal_tags_present']) or 'none'}")
        if result["recommendations"]:
            skin.section("Recommendations")
            for rec in result["recommendations"]:
                click.echo(f"  → {rec}")
    else:
        output(result)


@hashtags.command("niches")
@handle_error
def hashtags_niches() -> None:
    """List all supported hashtag niches."""
    niches = tag_mod.list_niches()
    if not _json_output:
        click.echo("Supported niches:\n")
        for n in niches:
            click.echo(f"  • {n}")
    else:
        output({"niches": niches})


@hashtags.command("merge")
@click.option("--yt-category", default="now", show_default=True, help="YouTube trending category")
@click.option("--tt-limit", default=30, show_default=True, help="TikTok hashtag limit")
@click.option("--limit", default=40, show_default=True, help="Output limit")
@handle_error
def hashtags_merge(yt_category: str, tt_limit: int, limit: int) -> None:
    """Merge YouTube + TikTok trending hashtags into a ranked cross-platform list."""
    if not _json_output:
        click.echo("Fetching YouTube and TikTok hashtags for merge …", err=True)
    yt_tags = []
    try:
        yt_result = yt_mod.fetch_trending(category=yt_category)
        yt_tags = yt_mod.extract_hashtags_from_videos(yt_result["videos"])
    except Exception:
        pass
    tt_result = tt_mod.fetch_trending_hashtags(limit=tt_limit)
    tt_tags = tt_result["hashtags"]

    merged = tag_mod.merge_hashtags(yt_tags, tt_tags, limit=limit)
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"Cross-Platform Hashtag Merge ({len(merged)} results)")
        skin.table(
            ["Rank", "Hashtag", "Platforms", "Cross-Platform", "TT Views"],
            [
                [
                    str(h["rank"]),
                    h["hashtag"],
                    "+".join(h.get("platforms", [])),
                    "✓" if h.get("cross_platform") else "",
                    str(h.get("tt_views", 0)),
                ]
                for h in merged
            ],
        )
    else:
        output({"merged_hashtags": merged, "count": len(merged)})


# ═════════════════════════════════════════════════════════════════════════════
# MUSIC group
# ═════════════════════════════════════════════════════════════════════════════

@cli.group()
def music():
    """Music trend intelligence — trending tracks, genre guide, platform timing."""
    pass


@music.command("trending")
@click.option("--genre", default=None, help="Filter by genre (run 'music genres' to list)")
@click.option("--platform", default=None, help="Filter by platform (tiktok, reels, youtube, shorts)")
@click.option("--mood", default=None, help="Filter by mood (e.g. energetic, chill, epic)")
@click.option("--limit", default=20, show_default=True)
@handle_error
def music_trending(genre: Optional[str], platform: Optional[str], mood: Optional[str], limit: int) -> None:
    """List trending music tracks filtered by genre, platform, or mood."""
    result = music_mod.list_trending_music(genre=genre, platform=platform, mood=mood, limit=limit)
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"Trending Music ({result['count']} tracks)")
        skin.table(
            ["#", "Title", "Artist", "Genre", "BPM", "Mood", "Best For"],
            [
                [
                    str(i + 1),
                    t["title"][:30],
                    t.get("artist", "")[:20],
                    t.get("genre", ""),
                    str(t.get("bpm", "")),
                    t.get("mood", ""),
                    ", ".join(t.get("best_for", [])[:3]),
                ]
                for i, t in enumerate(result["tracks"])
            ],
        )
    else:
        output(result)


@music.command("for-content")
@click.argument("content_type")
@handle_error
def music_for_content(content_type: str) -> None:
    """Recommend music for a specific content type (e.g. 'dance', 'travel', 'comedy')."""
    result = music_mod.get_music_for_content_type(content_type)
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"Music for '{content_type}' content ({result['count']} tracks)")
        skin.table(
            ["#", "Title", "Artist", "Genre", "BPM", "Mood"],
            [
                [str(i + 1), t["title"][:30], t.get("artist", "")[:20],
                 t.get("genre", ""), str(t.get("bpm", "")), t.get("mood", "")]
                for i, t in enumerate(result["tracks"])
            ],
        )
    else:
        output(result)


@music.command("platform-guide")
@click.argument("platform")
@handle_error
def music_platform_guide(platform: str) -> None:
    """Get music and posting guidance for a platform (tiktok, reels, shorts)."""
    result = music_mod.get_platform_music_guide(platform)
    output(result, f"Music guide for {result['platform']}")


@music.command("genres")
@handle_error
def music_genres() -> None:
    """List all supported music genres."""
    genres = music_mod.list_genres()
    moods = music_mod.list_moods()
    if not _json_output:
        click.echo(f"\nGenres:  {', '.join(genres)}")
        click.echo(f"Moods:   {', '.join(moods)}\n")
    else:
        output({"genres": genres, "moods": moods})


# ═════════════════════════════════════════════════════════════════════════════
# ACCOUNT group
# ═════════════════════════════════════════════════════════════════════════════

@cli.group()
def account():
    """Account optimisation — audit, playbook, calendar, and hook formulas."""
    pass


@account.command("optimize")
@click.argument("platform")
@handle_error
def account_optimize(platform: str) -> None:
    """Print the full optimisation playbook for a platform (tiktok/youtube/instagram)."""
    result = acct_mod.get_optimization_plan(platform)
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"Optimization Playbook — {result['platform'].upper()}")

        skin.section("Algorithm Signals (what the algo measures)")
        for sig in result["algorithm_signals"]:
            click.echo(f"  • {sig}")

        skin.section("Profile Checklist")
        for item in result["profile_checklist"]:
            click.echo(f"  [{item['item']}]  {item['tip']}")

        skin.section("Posting Schedule")
        sched = result["posting_schedule"]
        click.echo(f"  Frequency:   {sched['frequency']}")
        click.echo(f"  Best times:  {', '.join(sched['best_times_utc'])} UTC")
        click.echo(f"  Best days:   {', '.join(sched.get('best_days', []))}")
        click.echo(f"  Note:        {sched['consistency_note']}")

        skin.section("Content Pillars")
        for pillar in result["content_pillars"]:
            click.echo(f"  • {pillar}")

        hooks_key = "hook_formulas" if "hook_formulas" in result else "title_formulas"
        skin.section("Proven Hooks / Title Formulas")
        for hook in result.get(hooks_key, []):
            click.echo(f"  ▶ {hook}")

        skin.section("Growth Tactics")
        for tactic in result["growth_tactics"]:
            click.echo(f"  → {tactic}")
    else:
        output(result)


@account.command("audit")
@click.argument("platform")
@click.option("--followers", default=0, type=int, help="Current follower count")
@click.option("--avg-views", default=0, type=int, help="Average views per post")
@click.option("--posts-per-week", default=0.0, type=float, help="Average posts per week")
@click.option("--niche", default=None, help="Your content niche")
@handle_error
def account_audit(platform: str, followers: int, avg_views: int, posts_per_week: float, niche: Optional[str]) -> None:
    """Run an account health audit and get prioritised action items."""
    result = acct_mod.audit_account(
        platform=platform,
        follower_count=followers,
        avg_views=avg_views,
        posts_per_week=posts_per_week,
        niche=niche,
    )
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"Account Audit — {result['platform'].upper()}")
        click.echo(f"  Health score:   {result['health_score']}/100  [{result['health_label']}]")
        click.echo(f"  Followers:      {result['follower_count']:,}")
        click.echo(f"  Avg views:      {result['avg_views']:,}")
        click.echo(f"  Posts/week:     {result['posts_per_week']}")

        skin.section("Priority Actions")
        for action in result["action_items"]:
            prefix = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(action["priority"], "→")
            click.echo(f"  {prefix} [{action['priority']}] {action['action']}")
            click.echo(f"       {action['detail']}")
    else:
        output(result)


@account.command("calendar")
@click.option(
    "--platforms", default="tiktok,youtube,instagram",
    help="Comma-separated platform list",
)
@handle_error
def account_calendar(platforms: str) -> None:
    """Generate a 7-day cross-platform content posting calendar."""
    platform_list = [p.strip() for p in platforms.split(",")]
    result = acct_mod.get_posting_calendar(platform_list)
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section("7-Day Cross-Platform Content Calendar")
        for day, posts in result["calendar"].items():
            click.echo(f"\n  {_bold(day)}")
            for post in posts:
                click.echo(f"    [{post['platform'].upper()}] {post['type']}  —  {post['note']}")
        skin.section("Notes")
        for note in result["notes"]:
            click.echo(f"  → {note}")
    else:
        output(result)


@account.command("hooks")
@click.argument("platform")
@handle_error
def account_hooks(platform: str) -> None:
    """Print proven hook / title formulas for a platform."""
    result = acct_mod.get_hook_formulas(platform)
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"Hook Formulas — {result['platform'].upper()}")
        for formula in result["formulas"]:
            click.echo(f"  ▶ {formula}")
        skin.section("Content Pillars")
        for pillar in result["content_pillars"]:
            click.echo(f"  • {pillar}")
    else:
        output(result)


@account.command("platforms")
@handle_error
def account_platforms() -> None:
    """List supported platforms."""
    platforms = acct_mod.list_platforms()
    if not _json_output:
        click.echo(f"Supported platforms: {', '.join(platforms)}")
    else:
        output({"platforms": platforms})


# ═════════════════════════════════════════════════════════════════════════════
# THEME-PAGE group
# ═════════════════════════════════════════════════════════════════════════════

@cli.group("theme-page")
def theme_page():
    """Theme page guide — niches, launch playbook, conversion funnels, sourcing."""
    pass


@theme_page.command("niches")
@click.option("--min-monetisation", default=None,
              type=click.Choice(["low", "medium", "high", "very_high"], case_sensitive=False))
@click.option("--platform", default=None, help="Filter by platform")
@handle_error
def theme_niches(min_monetisation: Optional[str], platform: Optional[str]) -> None:
    """List all theme page niches ranked by profitability (CPM)."""
    result = theme_mod.list_niches(min_monetisation=min_monetisation, platform=platform)
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"Theme Page Niches ({result['count']} results)")
        skin.table(
            ["Niche", "CPM $", "Monetisation", "Competition", "Growth", "Platforms"],
            [
                [
                    n["display_name"],
                    f"${n['avg_cpm_usd']:.2f}",
                    n["monetisation_ceiling"],
                    n["competition"],
                    n["growth_speed"],
                    ", ".join(n["platforms"]),
                ]
                for n in result["niches"]
            ],
        )
    else:
        output(result)


@theme_page.command("niche-detail")
@click.argument("niche")
@handle_error
def theme_niche_detail(niche: str) -> None:
    """Deep dive into a specific niche: hooks, rate card, monetisation strategy."""
    result = theme_mod.get_niche_deep_dive(niche)
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"Niche Deep Dive — {result['display_name']}")
        click.echo(f"  CPM:           ${result['avg_cpm_usd']:.2f}")
        click.echo(f"  Monetisation:  {result['monetisation_ceiling']}")
        click.echo(f"  Competition:   {result['competition']}")
        click.echo(f"  Growth speed:  {result['growth_speed']}")
        click.echo(f"  Platforms:     {', '.join(result['platforms'])}")
        click.echo(f"  Best methods:  {', '.join(result['best_monetisation'])}")

        skin.section("Top Content Types")
        for ct in result["top_content_types"]:
            click.echo(f"  • {ct}")

        skin.section("Viral Hook Templates")
        for hook in result["viral_hooks"]:
            click.echo(f"  ▶ {hook}")

        skin.section("Shoutout Rate Card")
        for tier, rate in result["shoutout_rate_card"].items():
            click.echo(f"  {tier:<25} {rate}")

        click.echo(f"\n  Note: {result['notes']}\n")
    else:
        output(result)


@theme_page.command("playbook")
@handle_error
def theme_playbook() -> None:
    """Print the full theme page launch playbook (phases 1-5)."""
    result = theme_mod.get_launch_playbook()
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(result["title"])
        for phase in result["phases"]:
            click.echo(f"\n  {_bold(phase['phase'])}")
            for step in phase["steps"]:
                click.echo(f"    → {step}")
        skin.section("Key Rules")
        for rule in result["key_rules"]:
            click.echo(f"  ★ {rule}")
    else:
        output(result)


@theme_page.command("funnel")
@click.argument("funnel_type",
                type=click.Choice(["affiliate", "shoutout", "digital_product"], case_sensitive=False))
@handle_error
def theme_funnel(funnel_type: str) -> None:
    """Print a conversion funnel template (affiliate/shoutout/digital_product)."""
    result = theme_mod.get_conversion_funnel(funnel_type)
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(result["name"])
        for stage in result["stages"]:
            click.echo(f"  [{stage['stage']}]  {stage['action']}")
        click.echo(f"\n  Avg conversion rate:  {result['avg_conversion_rate']}")
        click.echo(f"  Avg revenue/sale:     {result['avg_commission_per_sale']}")
        click.echo(f"  Works on:             {', '.join(result['platforms'])}")
        skin.section("Tips")
        for tip in result["tips"]:
            click.echo(f"  → {tip}")
    else:
        output(result)


@theme_page.command("sourcing")
@handle_error
def theme_sourcing() -> None:
    """Content sourcing, reposting rules, and tool stack."""
    result = theme_mod.get_content_sourcing_guide()
    output(result, result["title"])


@theme_page.command("funnels")
@handle_error
def theme_funnels() -> None:
    """List available conversion funnel types."""
    funnels = theme_mod.list_funnel_types()
    if not _json_output:
        click.echo(f"Available funnels: {', '.join(funnels)}")
    else:
        output({"funnels": funnels})


# ═════════════════════════════════════════════════════════════════════════════
# REPORT group — full snapshot
# ═════════════════════════════════════════════════════════════════════════════

@cli.group()
def report():
    """Generate comprehensive trend reports."""
    pass


@report.command("snapshot")
@click.option("--region", default="US", show_default=True)
@click.option("--niche", default=None, help="Niche for hashtag recommendations")
@click.option("-o", "--output-file", "output_file", default=None,
              help="Save JSON report to file")
@handle_error
def report_snapshot(region: str, niche: Optional[str], output_file: Optional[str]) -> None:
    """Generate a full viral trends snapshot across YouTube + TikTok."""
    import os

    if not _json_output:
        click.echo("Generating full trends snapshot …", err=True)

    # TikTok
    if not _json_output:
        click.echo("  → TikTok hashtags …", err=True)
    try:
        tt_data = tt_mod.fetch_all_tiktok_trends(hashtag_limit=20, sound_limit=10)
    except Exception:
        tt_data = {"platform": "tiktok", "hashtags": [], "sounds": [],
                   "hashtag_count": 0, "sound_count": 0, "fetched_at": ""}

    # YouTube
    if not _json_output:
        click.echo("  → YouTube trending …", err=True)
    yt_tags = []
    try:
        yt_data = yt_mod.fetch_trending(limit=15, region=region)
        yt_tags = yt_mod.extract_hashtags_from_videos(yt_data["videos"])
    except Exception:
        import time as _time
        yt_data = {"platform": "youtube", "videos": [], "count": 0,
                   "fetched_at": _time.strftime("%Y-%m-%dT%H:%M:%SZ", _time.gmtime())}

    # Merged hashtags
    merged_tags = tag_mod.merge_hashtags(yt_tags, tt_data["hashtags"], limit=30)

    # Niche hashtags if provided
    niche_tags = None
    if niche:
        try:
            niche_tags = tag_mod.recommend_hashtags(niche=niche, limit=20)
        except ValueError:
            pass

    # Music
    top_music = music_mod.list_trending_music(limit=10)

    snapshot = {
        "report_type": "full_snapshot",
        "region": region,
        "niche": niche,
        "generated_at": yt_data.get("fetched_at", ""),
        "tiktok": tt_data,
        "youtube": yt_data,
        "merged_hashtags": merged_tags,
        "niche_hashtags": niche_tags,
        "trending_music": top_music,
    }

    if output_file:
        with open(output_file, "w") as f:
            json.dump(snapshot, f, indent=2, default=str)
        if not _json_output:
            click.echo(f"Report saved to {output_file}", err=True)

    output(snapshot, "Full Trend Snapshot")


# ═════════════════════════════════════════════════════════════════════════════
# REPL
# ═════════════════════════════════════════════════════════════════════════════

@cli.command()
def repl() -> None:
    """Launch an interactive REPL session."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.social_trends.utils.repl_skin import ReplSkin
    skin = ReplSkin(version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _commands = {
        "tiktok hashtags [--limit N]":              "TikTok trending hashtags",
        "tiktok sounds [--limit N]":                "TikTok trending sounds",
        "tiktok all":                               "TikTok hashtags + sounds snapshot",
        "youtube trending [--category music]":      "YouTube trending videos",
        "youtube hashtags":                         "Hashtags from YouTube trending",
        "youtube music":                            "Music from YouTube trending",
        "hashtags recommend --niche <niche>":       "Recommend hashtag pack for niche",
        "hashtags audit '<caption text>'":          "Audit hashtags in a caption",
        "hashtags niches":                          "List supported niches",
        "hashtags merge":                           "Cross-platform merged hashtags",
        "music trending [--genre pop]":             "Trending music tracks",
        "music for-content <type>":                 "Music for content type (e.g. dance)",
        "music platform-guide <platform>":          "Platform music & timing guide",
        "account optimize <platform>":              "Full account optimisation playbook",
        "account audit <platform> [--followers N]": "Account health audit + action plan",
        "account calendar":                         "7-day cross-platform content calendar",
        "account hooks <platform>":                 "Proven hook / title formulas",
        "theme-page niches":                        "Theme page niche profitability table",
        "theme-page niche-detail <niche>":          "Deep dive into a niche",
        "theme-page playbook":                      "Full launch playbook (phases 1-5)",
        "theme-page funnel <type>":                 "Conversion funnel template",
        "theme-page sourcing":                      "Content sourcing & reposting guide",
        "report snapshot [--niche <niche>]":        "Full trends report (YouTube + TikTok)",
        "help":                                     "Show this help",
        "quit / exit":                              "Exit REPL",
    }

    while True:
        try:
            raw = skin.get_input(pt_session)
        except (KeyboardInterrupt, EOFError):
            skin.print_goodbye()
            break

        if not raw:
            continue
        cmd = raw.strip()

        if cmd in ("quit", "exit", "q"):
            skin.print_goodbye()
            break

        if cmd in ("help", "h", "?"):
            skin.help(_commands)
            continue

        try:
            args = shlex.split(cmd)
        except ValueError as e:
            skin.error(f"Parse error: {e}")
            continue

        try:
            cli.main(args=args, standalone_mode=False)
        except SystemExit:
            pass
        except click.exceptions.UsageError as e:
            skin.error(str(e))
        except click.exceptions.BadParameter as e:
            skin.error(str(e))
        except Exception as e:
            skin.error(str(e))


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    cli()


if __name__ == "__main__":
    main()
