#!/usr/bin/env python3
"""Social Trends CLI — YouTube + TikTok viral trend intelligence.

Scrapes trending videos, hashtags, and music from YouTube and TikTok,
provides account optimisation recommendations, and generates theme-page
conversion strategies for content creators.

Usage:
    # Fetch trending data
    social-trends-cli trends youtube --category music --limit 20
    social-trends-cli trends tiktok --limit 30 --mock
    social-trends-cli trends aggregate --niche fitness

    # Account optimisation
    social-trends-cli account add tiktok @myfitpage --niche fitness
    social-trends-cli account audit tiktok @myfitpage --followers 12000 --avg-views 5000
    social-trends-cli account posting-times tiktok --niche fitness
    social-trends-cli account bio-suggest tiktok --niche fitness --handle myfitpage

    # Theme page strategy
    social-trends-cli theme niche-guide fitness
    social-trends-cli theme conversion-guide
    social-trends-cli theme calendar fitness --days 30 --platform tiktok
    social-trends-cli theme monetization finance
    social-trends-cli theme list-niches

    # Interactive REPL
    social-trends-cli repl
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_trends.core.session import Session
from cli_anything.social_trends.core import youtube_scraper as yt
from cli_anything.social_trends.core import tiktok_scraper as tt
from cli_anything.social_trends.core import trends as trends_mod
from cli_anything.social_trends.core import account_optimizer as acct
from cli_anything.social_trends.core import theme_page as theme_mod
from cli_anything.social_trends.utils.repl_skin import ReplSkin

_session: Optional[Session] = None
_json_output = False
_mock_mode = False


def get_session() -> Session:
    global _session
    if _session is None:
        _session = Session()
    return _session


def output(data, message: str = ""):
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
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


def handle_error(e: Exception):
    if _json_output:
        click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
    else:
        click.echo(f"Error: {e}", err=True)


# ── Root CLI ──────────────────────────────────────────────────────────

@click.group()
@click.option("--json", "json_out", is_flag=True, help="Output as JSON (agent-friendly).")
@click.option("--mock", is_flag=True, help="Use mock data (no network required).")
@click.option("--session-id", default=None, help="Resume a specific session ID.")
def cli(json_out: bool, mock: bool, session_id: Optional[str]):
    """Social Trends CLI — viral trend intelligence for YouTube + TikTok."""
    global _json_output, _mock_mode, _session
    _json_output = json_out
    _mock_mode = mock
    if session_id:
        loaded = Session.load(session_id)
        _session = loaded if loaded else Session(session_id=session_id)


# ── trends group ──────────────────────────────────────────────────────

@cli.group()
def trends():
    """Fetch trending videos, hashtags, and music."""


@trends.command("youtube")
@click.option("--category", default="general",
              type=click.Choice(["general", "music", "gaming", "movies"]),
              help="Trending category.")
@click.option("--limit", default=20, show_default=True, help="Max results.")
@click.option("--country", default="US", show_default=True, help="Country code (e.g. US, GB, AU).")
@click.option("--music-only", is_flag=True, help="Return only music videos.")
def youtube_trends(category, limit, country, music_only):
    """Fetch trending YouTube videos."""
    try:
        if music_only:
            data = yt.get_trending_music(limit=limit, country=country)
        else:
            data = yt.get_trending_videos(category=category, limit=limit, country=country)
        sess = get_session()
        sess.cache_trends(f"yt:{category}:{country}", data)
        output(data, f"YouTube trending ({category}, {country}) — {len(data)} videos:")
    except Exception as e:
        handle_error(e)


@trends.command("tiktok")
@click.option("--limit", default=20, show_default=True, help="Max results.")
@click.option("--music-only", is_flag=True, help="Return only trending music/sounds.")
@click.option("--hashtags-only", is_flag=True, help="Return only trending hashtags.")
def tiktok_trends(limit, music_only, hashtags_only):
    """Fetch trending TikTok content."""
    try:
        if music_only:
            data = tt._mock_trending_music(limit) if _mock_mode else tt.get_trending_music(limit)
            output(data, f"TikTok trending music — {len(data)} tracks:")
        elif hashtags_only:
            data = tt._mock_trending_hashtags(limit) if _mock_mode else tt.get_trending_hashtags(limit)
            output(data, f"TikTok trending hashtags — {len(data)} tags:")
        else:
            videos = tt._mock_trending_hashtags(limit) if _mock_mode else tt.get_trending_videos(limit)
            get_session().cache_trends("tt:videos", videos)
            output(videos, f"TikTok trending — {len(videos)} videos:")
    except Exception as e:
        handle_error(e)


@trends.command("hashtags")
@click.option("--platform", default="both",
              type=click.Choice(["youtube", "tiktok", "both"]),
              help="Platform to pull hashtags from.")
@click.option("--niche", default=None, help="Filter to niche-relevant hashtags.")
@click.option("--limit", default=30, show_default=True)
@click.option("--country", default="US", show_default=True)
def trend_hashtags(platform, niche, limit, country):
    """Get trending hashtags across platforms."""
    try:
        results = []
        if platform in ("youtube", "both"):
            results += yt.get_trending_hashtags(limit=limit, country=country)
        if platform in ("tiktok", "both"):
            tags = tt._mock_trending_hashtags(limit) if _mock_mode else tt.get_trending_hashtags(limit)
            results += tags
        if niche:
            results = trends_mod.get_hashtag_suggestions(niche, platform, count=limit)
            output(results, f"Niche hashtags for #{niche} on {platform}:")
        else:
            output(results[:limit], f"Trending hashtags ({platform}) — {min(len(results), limit)} tags:")
    except Exception as e:
        handle_error(e)


@trends.command("music")
@click.option("--platform", default="both",
              type=click.Choice(["youtube", "tiktok", "both"]))
@click.option("--limit", default=20, show_default=True)
@click.option("--country", default="US", show_default=True)
def trend_music(platform, limit, country):
    """Get trending music / audio across platforms."""
    try:
        if platform == "both":
            data = trends_mod.get_cross_platform_music(limit=limit)
        elif platform == "tiktok":
            data = tt._mock_trending_music(limit) if _mock_mode else tt.get_trending_music(limit)
        else:
            data = yt.get_trending_music(limit=limit, country=country)
        output(data, f"Trending music ({platform}) — {len(data)} tracks:")
    except Exception as e:
        handle_error(e)


@trends.command("aggregate")
@click.option("--niche", default=None, help="Focus on a specific niche.")
@click.option("--limit", default=20, show_default=True)
@click.option("--country", default="US", show_default=True)
def trend_aggregate(niche, limit, country):
    """Aggregate trends from both YouTube and TikTok.

    Finds cross-platform trending content and niche-specific signals.
    """
    try:
        data = trends_mod.aggregate_trends(niche=niche, limit=limit, country=country)
        output(data, f"Aggregated trends{' for ' + niche if niche else ''}")
    except Exception as e:
        handle_error(e)


@trends.command("velocity")
@click.option("--category", default="general")
@click.option("--limit", default=30, show_default=True)
@click.option("--country", default="US", show_default=True)
def trend_velocity(category, limit, country):
    """Analyse trend velocity — hot, rising, and fading."""
    try:
        videos = yt.get_trending_videos(category=category, limit=limit, country=country)
        data = trends_mod.analyze_trend_velocity(videos)
        output(data, "Trend velocity analysis:")
    except Exception as e:
        handle_error(e)


@trends.command("hashtag-stats")
@click.argument("hashtag")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "youtube"]))
def hashtag_stats(hashtag, platform):
    """Get stats for a specific hashtag.

    HASHTAG: Tag name with or without #, e.g. fitness or #fitness
    """
    try:
        tag = hashtag.lstrip("#")
        if platform == "tiktok":
            data = tt.get_hashtag_stats(tag)
        else:
            data = {"hashtag": f"#{tag}", "platform": "youtube",
                    "note": "YouTube hashtag stats require the Data API. Try: yt search."}
        output(data)
    except Exception as e:
        handle_error(e)


# ── account group ─────────────────────────────────────────────────────

@cli.group()
def account():
    """Manage and optimise social media accounts."""


@account.command("add")
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.argument("handle")
@click.option("--niche", default="", help="Content niche (fitness, finance, etc.)")
def account_add(platform, handle, niche):
    """Register an account for optimisation tracking.

    PLATFORM: tiktok, youtube, or instagram
    HANDLE: Account handle (with or without @)
    """
    sess = get_session()
    a = sess.add_account(platform, handle, niche)
    output(a, f"Added account: {platform}/@{a['handle']}")


@account.command("remove")
@click.argument("platform")
@click.argument("handle")
def account_remove(platform, handle):
    """Remove a registered account."""
    sess = get_session()
    ok = sess.remove_account(platform, handle)
    msg = f"Removed {platform}/@{handle.lstrip('@')}" if ok else "Account not found."
    output({"success": ok, "message": msg}, msg)


@account.command("list")
def account_list():
    """List all registered accounts."""
    sess = get_session()
    accounts = sess.list_accounts()
    if not accounts:
        click.echo("No accounts registered. Use: account add <platform> <handle>")
        return
    output(accounts, f"{len(accounts)} registered accounts:")


@account.command("audit")
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.argument("handle")
@click.option("--niche", default="general", show_default=True)
@click.option("--followers", default=0, type=int, help="Current follower count.")
@click.option("--avg-views", default=0, type=int, help="Average views per video.")
@click.option("--avg-likes", default=0, type=int, help="Average likes per video.")
@click.option("--bio", default="", help="Current bio text (quote it).")
@click.option("--posts-per-week", default=0.0, type=float, help="Current weekly post frequency.")
def account_audit(platform, handle, niche, followers, avg_views, avg_likes, bio, posts_per_week):
    """Run a full account audit with scored recommendations.

    Example:
        account audit tiktok @mypage --niche fitness --followers 12000
        --avg-views 8000 --avg-likes 600 --posts-per-week 7
    """
    try:
        data = acct.audit_account(
            platform=platform,
            handle=handle,
            niche=niche,
            followers=followers,
            avg_views=avg_views,
            avg_likes=avg_likes,
            bio=bio,
            posts_per_week=posts_per_week,
        )
        output(data, f"Account audit: {platform}/@{handle.lstrip('@')} — Score: {data['score']}/100 (Grade: {data['grade']})")
    except Exception as e:
        handle_error(e)


@account.command("posting-times")
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--niche", default="general", show_default=True)
def posting_times(platform, niche):
    """Get the best posting times for a platform + niche."""
    try:
        data = acct.get_best_posting_times(platform, niche)
        output(data, f"Best posting times for {platform}/{niche}:")
    except Exception as e:
        handle_error(e)


@account.command("bio-suggest")
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--niche", required=True, help="Content niche.")
@click.option("--handle", default="", help="Account handle.")
@click.option("--value-prop", default="", help="Your value proposition.")
@click.option("--cta", default="", help="Call to action text.")
def bio_suggest(platform, niche, handle, value_prop, cta):
    """Generate an optimised bio template."""
    try:
        data = acct.suggest_bio(niche, platform, handle, value_prop, cta)
        output(data, "Bio suggestion:")
    except Exception as e:
        handle_error(e)


@account.command("engagement-rate")
@click.option("--views", required=True, type=int, help="Average views per post.")
@click.option("--likes", required=True, type=int, help="Average likes per post.")
@click.option("--comments", default=0, type=int, help="Average comments per post.")
def engagement_rate(views, likes, comments):
    """Calculate and benchmark your engagement rate."""
    try:
        data = acct.get_engagement_rate(views, likes, comments)
        output(data, "Engagement rate analysis:")
    except Exception as e:
        handle_error(e)


@account.command("hashtags")
@click.argument("niche")
@click.option("--platform", default="both",
              type=click.Choice(["youtube", "tiktok", "both"]))
@click.option("--count", default=30, show_default=True)
def account_hashtags(niche, platform, count):
    """Generate an optimised hashtag strategy for your niche."""
    try:
        tags = trends_mod.get_hashtag_suggestions(niche, platform, count)
        output(tags, f"Hashtag strategy for #{niche} on {platform} ({len(tags)} tags):")
    except Exception as e:
        handle_error(e)


@account.command("optimize-all")
@click.option("--country", default="US", show_default=True)
def optimize_all(country):
    """Run full optimisation audit on all registered accounts.

    Fetches live trends, then audits each registered account and outputs
    combined recommendations.
    """
    sess = get_session()
    accounts = sess.list_accounts()
    if not accounts:
        click.echo("No accounts registered. Add with: account add <platform> <handle>")
        return
    try:
        # Fetch fresh trends for context
        try:
            trend_data = trends_mod.aggregate_trends(limit=20, country=country)
            sess.cache_trends("latest_aggregate", trend_data)
        except Exception:
            trend_data = {}

        results = []
        for a in accounts:
            audit = acct.audit_account(
                platform=a["platform"],
                handle=a["handle"],
                niche=a.get("niche", "general"),
            )
            # Inject live trend hashtags if available
            niche_tags = trend_data.get("niche_hashtags", [])
            if niche_tags:
                audit["live_trend_hashtags"] = niche_tags[:10]
            results.append(audit)

        output({"accounts_audited": len(results), "audits": results},
               f"Optimised {len(results)} accounts:")
    except Exception as e:
        handle_error(e)


# ── theme group ───────────────────────────────────────────────────────

@cli.group()
def theme():
    """Theme page & niche page strategy and conversion guides."""


@theme.command("niche-guide")
@click.argument("niche")
def niche_guide(niche):
    """Full playbook for building a converting theme page.

    NICHE: fitness, finance, beauty, food, travel, tech, gaming, comedy, etc.

    Includes: content pillars, viral formats, monetization, hashtags,
    posting frequency, handle ideas, and quick-start steps.
    """
    try:
        data = theme_mod.get_niche_guide(niche)
        output(data, f"Niche guide: {niche}")
    except Exception as e:
        handle_error(e)


@theme.command("conversion-guide")
def conversion_guide():
    """The master theme page conversion playbook (all 4 phases).

    Covers: Foundation → Growth → Monetization → Scale.
    Includes common mistakes, tools, and the conversion funnel.
    """
    try:
        data = theme_mod.get_conversion_guide()
        output(data, "Theme Page Conversion Masterclass")
    except Exception as e:
        handle_error(e)


@theme.command("calendar")
@click.argument("niche")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "youtube"]))
@click.option("--days", default=30, show_default=True, help="Days to plan.")
@click.option("--posts-per-day", default=1, show_default=True)
@click.option("--start-date", default=None, help="Start date YYYY-MM-DD (defaults to today).")
def content_calendar(niche, platform, days, posts_per_day, start_date):
    """Generate a content calendar for a theme page.

    Example:
        theme calendar fitness --platform tiktok --days 30 --posts-per-day 2
    """
    try:
        from datetime import date as date_cls
        sd = date_cls.fromisoformat(start_date) if start_date else None
        data = theme_mod.generate_content_calendar(
            niche=niche,
            platform=platform,
            start_date=sd,
            days=days,
            posts_per_day=posts_per_day,
        )
        output(data, f"Content calendar: {niche}/{platform} — {len(data)} posts over {days} days")
    except Exception as e:
        handle_error(e)


@theme.command("monetization")
@click.argument("niche")
def monetization(niche):
    """Get ranked monetization strategies for a niche.

    Shows each path with difficulty and time-to-first-dollar.
    """
    try:
        data = theme_mod.get_monetization_strategies(niche)
        output(data, f"Monetization strategies for: {niche}")
    except Exception as e:
        handle_error(e)


@theme.command("list-niches")
def list_niches():
    """List all supported niches with key stats."""
    data = theme_mod.list_niches()
    output(data, f"{len(data)} supported niches:")


@theme.command("faceless-formats")
def faceless_formats():
    """List content formats that work without showing your face."""
    data = {
        "formats": theme_mod.FACELESS_CONTENT_TYPES,
        "note": (
            "Theme pages thrive on these formats. "
            "Combine stock footage (Pexels, Pixabay), AI voiceover (ElevenLabs), "
            "and trending audio for fully automated content."
        ),
    }
    output(data, "Faceless content formats for theme pages:")


# ── session group ─────────────────────────────────────────────────────

@cli.group()
def session():
    """Manage CLI sessions."""


@session.command("status")
def session_status():
    """Show current session status."""
    sess = get_session()
    output(sess.status())


@session.command("save")
def session_save():
    """Persist current session to disk."""
    path = get_session().save()
    click.echo(f"Session saved: {path}")


@session.command("load")
@click.argument("session_id")
def session_load(session_id):
    """Load a previously saved session."""
    global _session
    s = Session.load(session_id)
    if s:
        _session = s
        output(s.status(), f"Session loaded: {session_id}")
    else:
        click.echo(f"Session not found: {session_id}", err=True)


@session.command("list")
def session_list():
    """List all saved sessions."""
    sessions = Session.list_sessions()
    if not sessions:
        click.echo("No saved sessions.")
        return
    output(sessions, f"{len(sessions)} sessions:")


@session.command("set-niche")
@click.argument("niche")
def session_set_niche(niche):
    """Set the active niche for this session."""
    sess = get_session()
    sess.set_niche(niche)
    click.echo(f"Active niche set to: {niche}")


@session.command("set-platform")
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "both"]))
def session_set_platform(platform):
    """Set the active platform for this session."""
    sess = get_session()
    sess.set_platform(platform)
    click.echo(f"Active platform set to: {platform}")


@session.command("clear-cache")
def session_clear_cache():
    """Clear all cached trend data."""
    n = get_session().clear_cache()
    click.echo(f"Cleared {n} cached entries.")


# ── REPL ──────────────────────────────────────────────────────────────

@cli.command()
@click.option("--niche", default=None, help="Set active niche for this REPL session.")
@click.option("--platform", default=None,
              type=click.Choice(["tiktok", "youtube", "both"]))
def repl(niche, platform):
    """Interactive REPL — type 'help' for available commands."""
    global _session
    if _session is None:
        _session = Session()
    if niche:
        _session.set_niche(niche)
    if platform:
        _session.set_platform(platform)

    skin = ReplSkin("social-trends", version="1.0.0")
    skin.print_banner()
    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "trends youtube [--category CATEGORY] [--limit N]": "Fetch YouTube trending",
        "trends tiktok [--limit N] [--mock]": "Fetch TikTok trending",
        "trends hashtags [--platform both] [--niche NICHE]": "Get trending hashtags",
        "trends music [--platform both]": "Get trending music",
        "trends aggregate [--niche NICHE]": "Cross-platform trend summary",
        "account add PLATFORM HANDLE [--niche NICHE]": "Register an account",
        "account audit PLATFORM HANDLE [--followers N]": "Audit an account",
        "account optimize-all": "Audit all registered accounts",
        "account hashtags NICHE [--platform both]": "Hashtag strategy",
        "theme niche-guide NICHE": "Full niche page playbook",
        "theme conversion-guide": "Theme page masterclass",
        "theme calendar NICHE [--days 30]": "Content calendar",
        "theme monetization NICHE": "Monetization strategies",
        "theme list-niches": "All supported niches",
        "session status": "Show session state",
        "session save": "Save session to disk",
        "session set-niche NICHE": "Set active niche",
        "help": "Show this help",
        "quit / exit": "Exit the REPL",
    }

    context = f"{_session.active_niche or 'no niche'}/{_session.active_platform or 'all platforms'}"

    while True:
        try:
            line = skin.get_input(pt_session, context=context)
        except (KeyboardInterrupt, EOFError):
            skin.print_goodbye()
            break

        if not line:
            continue
        if line.lower() in ("quit", "exit", "q"):
            skin.print_goodbye()
            break
        if line.lower() == "help":
            skin.section("Social Trends CLI — Commands")
            for cmd, desc in _repl_commands.items():
                skin.info(f"{cmd:<55}  {desc}")
            continue

        # Route to click commands
        try:
            from click.testing import CliRunner
            runner = CliRunner(mix_stderr=False)
            args = line.split()
            result = runner.invoke(cli, args, catch_exceptions=False)
            if result.output:
                click.echo(result.output, nl=False)
            if result.exception:
                skin.error(str(result.exception))
        except SystemExit:
            pass
        except Exception as e:
            skin.error(str(e))

        # Refresh context after state-changing commands
        context = f"{_session.active_niche or 'no niche'}/{_session.active_platform or 'all platforms'}"


if __name__ == "__main__":
    cli()
