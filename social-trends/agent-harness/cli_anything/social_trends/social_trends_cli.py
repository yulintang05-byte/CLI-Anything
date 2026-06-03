#!/usr/bin/env python3
"""Social Trends CLI — scrape viral trends, optimize accounts, and build converting theme pages.

Usage:
    # Scrape trending content
    cli-anything-social-trends trends scrape --platform all
    cli-anything-social-trends trends hashtags --platform tiktok
    cli-anything-social-trends trends music --limit 20

    # Account management and optimization
    cli-anything-social-trends account add --platform tiktok --username myaccount --niche fitness
    cli-anything-social-trends account optimize --platform tiktok --niche fitness

    # Theme page strategy
    cli-anything-social-trends theme-page guide --niche motivational
    cli-anything-social-trends theme-page convert --niche finance --followers 5000

    # Interactive REPL
    cli-anything-social-trends
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_trends.core.session import Session
from cli_anything.social_trends.core import scraper as scraper_mod
from cli_anything.social_trends.core import trends as trends_mod
from cli_anything.social_trends.core import optimizer as optimizer_mod
from cli_anything.social_trends.core import theme_page as theme_mod
from cli_anything.social_trends.utils.social_trends_backend import (
    load_config, save_config, SUPPORTED_PLATFORMS, SUPPORTED_NICHES,
)

_session: Optional[Session] = None
_json_output = False
_repl_mode = False


def get_session() -> Session:
    global _session
    if _session is None:
        from pathlib import Path
        sf = str(Path.home() / ".config" / "social-trends" / "session.json")
        _session = Session(session_file=sf)
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
        elif data is not None:
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
        elif isinstance(item, str):
            click.echo(f"{prefix}• {item}")
        else:
            click.echo(f"{prefix}- {item}")


def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (FileNotFoundError, ValueError, RuntimeError, TimeoutError) as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def _progress(msg: str, pct: int):
    if not _json_output:
        click.echo(f"  ● {msg} ({pct}%)")


# ── Main CLI ───────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx, use_json):
    """Social Trends CLI — viral trends, account optimization, and theme pages."""
    global _json_output
    _json_output = use_json
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── Trends Group ───────────────────────────────────────────────────────

@cli.group()
def trends():
    """Scrape and analyze viral trends from YouTube and TikTok."""
    pass


@trends.command("scrape")
@click.option("--platform", "-p", default="all",
              type=click.Choice(SUPPORTED_PLATFORMS, case_sensitive=False),
              help="Platform to scrape (default: all)")
@click.option("--limit", "-n", default=30, type=int, help="Videos per platform (default: 30)")
@click.option("--country", "-c", default="US", help="Country code (default: US)")
@click.option("--no-cache", is_flag=True, help="Skip cache and force fresh scrape")
@click.option("--yt-api-key", default=None, help="YouTube Data API v3 key")
@click.option("--tiktok-session", default=None, help="TikTok sessionid cookie value")
@handle_error
def trends_scrape(platform, limit, country, no_cache, yt_api_key, tiktok_session):
    """Scrape trending videos from YouTube and/or TikTok."""
    videos = scraper_mod.scrape_platform(
        platform=platform,
        limit=limit,
        country=country,
        use_cache=not no_cache,
        on_progress=_progress,
        youtube_api_key=yt_api_key,
        tiktok_session_id=tiktok_session,
    )
    sess = get_session()
    sess.record("trends scrape", {"platform": platform, "limit": limit}, {"count": len(videos)})

    if not _json_output:
        click.echo(f"\n✓ Scraped {len(videos)} trending videos from {platform}\n")
        for i, v in enumerate(videos[:10], 1):
            views = v.get("views", 0)
            plat = v.get("platform", "")
            click.echo(f"  {i:2}. [{plat}] {v['title'][:60]}")
            click.echo(f"      Views: {views:,}  |  Channel: {v.get('channel','?')}")
            if v.get("hashtags"):
                click.echo(f"      Tags: {' '.join(v['hashtags'][:5])}")
        if len(videos) > 10:
            click.echo(f"\n  ... and {len(videos) - 10} more. Use --json for full output.")
    else:
        output(videos)


@trends.command("hashtags")
@click.option("--platform", "-p", default="all",
              type=click.Choice(SUPPORTED_PLATFORMS, case_sensitive=False))
@click.option("--limit", "-n", default=30, type=int, help="Videos to analyze")
@click.option("--top", "-t", default=20, type=int, help="Top N hashtags to show")
@click.option("--no-cache", is_flag=True)
@handle_error
def trends_hashtags(platform, limit, top, no_cache):
    """Get the top trending hashtags from scraped videos."""
    videos = scraper_mod.scrape_platform(
        platform=platform, limit=limit, use_cache=not no_cache, on_progress=_progress
    )
    hashtags = scraper_mod.get_all_hashtags(videos, top_n=top)
    sess = get_session()
    sess.record("trends hashtags", {"platform": platform}, {"count": len(hashtags)})

    if not _json_output:
        click.echo(f"\n✓ Top {len(hashtags)} trending hashtags ({platform})\n")
        click.echo(f"  {'#':2}  {'Hashtag':<30} {'Appearances':>12} {'Total Views':>15}")
        click.echo(f"  {'-'*2}  {'-'*30} {'-'*12} {'-'*15}")
        for i, h in enumerate(hashtags, 1):
            click.echo(
                f"  {i:2}.  {h['hashtag']:<30} {h['appearances']:>12,} {h['total_views']:>15,}"
            )
    else:
        output(hashtags)


@trends.command("music")
@click.option("--limit", "-n", default=50, type=int, help="TikTok videos to analyze")
@click.option("--top", "-t", default=20, type=int, help="Top N sounds to show")
@click.option("--no-cache", is_flag=True)
@handle_error
def trends_music(limit, top, no_cache):
    """Get trending music/sounds from TikTok."""
    videos = scraper_mod.scrape_platform(
        platform="tiktok", limit=limit, use_cache=not no_cache, on_progress=_progress
    )
    sounds = scraper_mod.get_all_sounds(videos)[:top]
    sess = get_session()
    sess.record("trends music", {}, {"count": len(sounds)})

    if not _json_output:
        click.echo(f"\n✓ Top {len(sounds)} trending TikTok sounds\n")
        click.echo(f"  {'#':2}  {'Title':<35} {'Artist':<25} {'Videos':>7} {'Views':>14}")
        click.echo(f"  {'-'*2}  {'-'*35} {'-'*25} {'-'*7} {'-'*14}")
        for i, s in enumerate(sounds, 1):
            click.echo(
                f"  {i:2}.  {s['title'][:35]:<35} {s['artist'][:25]:<25} "
                f"{s['video_count']:>7,} {s['total_views']:>14,}"
            )
    else:
        output(sounds)


@trends.command("analyze")
@click.option("--platform", "-p", default="all",
              type=click.Choice(SUPPORTED_PLATFORMS, case_sensitive=False))
@click.option("--limit", "-n", default=30, type=int)
@click.option("--no-cache", is_flag=True)
@handle_error
def trends_analyze(platform, limit, no_cache):
    """Full trend analysis report — hashtags, sounds, patterns, recommendations."""
    videos = scraper_mod.scrape_platform(
        platform=platform, limit=limit, use_cache=not no_cache, on_progress=_progress
    )
    report = trends_mod.analyze_trends(videos)
    sess = get_session()
    sess.record("trends analyze", {"platform": platform}, report.get("platform_breakdown"))
    output(report, f"\n✓ Trend analysis complete ({len(videos)} videos analyzed)")


# ── Account Group ──────────────────────────────────────────────────────

@cli.group()
def account():
    """Manage and optimize your social media accounts."""
    pass


@account.command("add")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["tiktok", "instagram", "youtube", "twitter"], case_sensitive=False))
@click.option("--username", "-u", required=True, help="Account username/handle")
@click.option("--niche", "-n", required=True, help=f"Account niche (e.g. {', '.join(SUPPORTED_NICHES[:4])})")
@click.option("--followers", "-f", default=0, type=int, help="Current follower count")
@handle_error
def account_add(platform, username, niche, followers):
    """Register an account for optimization tracking."""
    acct = optimizer_mod.add_account(platform, username, niche, followers)
    sess = get_session()
    sess.record("account add", {"platform": platform, "username": username}, acct)
    output(acct, f"✓ Added account: @{username} on {platform} ({niche}, {followers:,} followers)")


@account.command("remove")
@click.option("--platform", "-p", required=True)
@click.option("--username", "-u", required=True)
@handle_error
def account_remove(platform, username):
    """Remove a registered account."""
    removed = optimizer_mod.remove_account(platform, username)
    if removed:
        output({"removed": True}, f"✓ Removed @{username} from {platform}")
    else:
        output({"removed": False}, f"Account @{username} on {platform} not found")


@account.command("list")
@handle_error
def account_list():
    """List all registered accounts."""
    accounts = optimizer_mod.list_accounts()
    if not accounts:
        output([], "No accounts registered. Add one with: account add --platform tiktok --username myaccount --niche fitness")
        return
    output(accounts, f"✓ {len(accounts)} registered account(s):")


@account.command("optimize")
@click.option("--platform", "-p", required=True)
@click.option("--niche", "-n", required=True)
@click.option("--followers", "-f", default=0, type=int)
@click.option("--username", "-u", default=None)
@click.option("--limit", default=30, type=int, help="Videos to scrape for trend data")
@click.option("--no-cache", is_flag=True)
@handle_error
def account_optimize(platform, niche, followers, username, limit, no_cache):
    """Generate a full optimization plan for an account based on current trends."""
    click.echo(f"  ● Scraping trend data for {platform}/{niche}…")
    videos = scraper_mod.scrape_platform(
        platform=platform if platform in ("youtube", "tiktok") else "all",
        limit=limit,
        use_cache=not no_cache,
        on_progress=_progress,
    )
    trend_data = trends_mod.analyze_trends(videos)
    plan = optimizer_mod.optimize_account(
        platform=platform,
        niche=niche,
        trend_data=trend_data,
        follower_count=followers,
        username=username,
    )
    sess = get_session()
    sess.record("account optimize", {"platform": platform, "niche": niche}, {"score": plan.get("optimization_score")})

    if not _json_output:
        score = plan.get("optimization_score", {})
        click.echo(f"\n✓ Optimization Plan for @{username or 'your account'} ({platform} / {niche})")
        click.echo(f"  Score: {score.get('score')}/100 — {score.get('level')} | Next: {score.get('next_milestone')}\n")

        hp = plan.get("hashtag_plan", {})
        click.echo("━━ HASHTAG PLAN ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        click.echo(f"  Mega:  {' '.join(hp.get('mega_hashtags', []))}")
        click.echo(f"  Large: {' '.join(hp.get('large_hashtags', []))}")
        click.echo(f"  Niche: {' '.join(hp.get('niche_hashtags', []))}")
        click.echo(f"  Combo: {' '.join(hp.get('example_combo', []))}")
        click.echo(f"  Tip:   {hp.get('tip','')}\n")

        sched = plan.get("posting_schedule", {})
        click.echo("━━ POSTING SCHEDULE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        click.echo(f"  Frequency: {sched.get('recommended_frequency','')}")
        click.echo(f"  Best times: {', '.join(sched.get('best_times', []))}")
        click.echo(f"  Tip: {sched.get('tip','')}\n")

        click.echo("━━ CONTENT IDEAS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for idea in plan.get("content_ideas", [])[:5]:
            click.echo(f"  [{idea['format']}] {idea['title_template']}")
        click.echo()

        click.echo("━━ QUICK WINS (DO TODAY) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for win in plan.get("quick_wins", []):
            click.echo(f"  ✓ {win}")
        click.echo()

        click.echo("━━ MONETIZATION ROADMAP ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for stage in plan.get("monetization_roadmap", []):
            click.echo(f"  [{stage['stage']}]")
            click.echo(f"    {stage['monetization']}")
    else:
        output(plan)


@account.command("optimize-all")
@click.option("--limit", default=30, type=int)
@click.option("--no-cache", is_flag=True)
@handle_error
def account_optimize_all(limit, no_cache):
    """Optimize all registered accounts at once using current trends."""
    accounts = optimizer_mod.list_accounts()
    if not accounts:
        click.echo("No accounts registered. Add accounts with: account add")
        return

    click.echo(f"  ● Scraping trends for {len(accounts)} accounts…")
    videos = scraper_mod.scrape_platform(
        platform="all", limit=limit, use_cache=not no_cache, on_progress=_progress
    )
    trend_data = trends_mod.analyze_trends(videos)
    plans = optimizer_mod.optimize_all_accounts(trend_data)

    sess = get_session()
    sess.record("account optimize-all", {}, {"plans": len(plans)})
    output(plans, f"\n✓ Generated optimization plans for {len(plans)} accounts")


# ── Theme-Page Group ───────────────────────────────────────────────────

@cli.group("theme-page")
def theme_page():
    """Build and optimize converting theme pages."""
    pass


@theme_page.command("niches")
@handle_error
def theme_page_niches():
    """List all supported niches with proven theme page strategies."""
    niches = theme_mod.list_supported_niches()
    if not _json_output:
        click.echo(f"\n✓ {len(niches)} proven theme page niches:\n")
        for niche in niches:
            data = theme_mod.PROVEN_NICHES.get(niche, {})
            platforms = ", ".join(data.get("best_platforms", []))
            click.echo(f"  • {niche:<20} → {platforms}")
        click.echo("\nGet details: theme-page guide --niche <niche>")
    else:
        output(niches)


@theme_page.command("guide")
@click.option("--niche", "-n", required=True,
              help=f"Niche to build guide for (e.g. {', '.join(list(theme_mod.PROVEN_NICHES.keys())[:4])})")
@handle_error
def theme_page_guide(niche):
    """Get the full theme page strategy guide for a niche."""
    guide = theme_mod.get_niche_guide(niche)
    sess = get_session()
    sess.record("theme-page guide", {"niche": niche}, {"niche": guide.get("niche")})

    if not _json_output:
        ov = guide.get("overview", {})
        actual_niche = guide.get("niche", niche)
        click.echo(f"\n{'='*60}")
        click.echo(f"  THEME PAGE GUIDE: {actual_niche.upper()}")
        click.echo(f"{'='*60}\n")
        click.echo(f"  Description: {ov.get('description','')}")
        click.echo(f"  Avg engagement: {ov.get('avg_engagement','')}")
        click.echo(f"  Best platforms: {', '.join(ov.get('best_platforms', []))}")
        click.echo(f"  Posting cadence: {ov.get('posting_cadence','')}")
        click.echo()

        click.echo("━━ MONETIZATION METHODS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for m in ov.get("monetization", []):
            click.echo(f"  • {m}")
        click.echo()

        click.echo("━━ BIO FORMULA ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        click.echo(f"  {guide.get('bio_formula','')}")
        click.echo()
        click.echo("  Example:")
        for line in guide.get("bio_example", "").split("\n"):
            click.echo(f"    {line}")
        click.echo()

        click.echo("━━ LINK-IN-BIO STACK ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for item in guide.get("link_in_bio_stack", []):
            click.echo(f"  {item}")
        click.echo()

        click.echo("━━ STORY HIGHLIGHTS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for item in guide.get("story_highlights", []):
            click.echo(f"  • {item}")
        click.echo()

        click.echo("━━ CONTENT CALENDAR ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for day, info in guide.get("content_calendar", {}).items():
            click.echo(f"  {day.upper():<12}: {info['theme']} → {info['format']}")
        click.echo()

        click.echo("━━ GROWTH PLAYBOOK ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for phase_key, phase in guide.get("growth_playbook", {}).items():
            click.echo(f"\n  [{phase['phase']}]  KPI: {phase['kpi']}")
            for action in phase["actions"][:3]:
                click.echo(f"    ✓ {action}")

        if ov.get("converting_tip"):
            click.echo(f"\n━━ KEY CONVERTING TIP ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            click.echo(f"  🔑 {ov['converting_tip']}")
        click.echo()
    else:
        output(guide)


@theme_page.command("convert")
@click.option("--niche", "-n", required=True)
@click.option("--platform", "-p", default="tiktok")
@click.option("--followers", "-f", default=0, type=int)
@handle_error
def theme_page_convert(niche, platform, followers):
    """Get conversion-focused optimization tips for a theme page."""
    tips = theme_mod.get_conversion_tips(platform, niche, followers)
    funnel = theme_mod.CONVERSION_FUNNEL

    if not _json_output:
        click.echo(f"\n✓ Conversion Tips — {niche.upper()} on {platform.upper()} ({followers:,} followers)\n")
        for tip in tips:
            click.echo(f"  {tip}")
        click.echo()
        click.echo("━━ CONVERSION FUNNEL ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for stage, data in funnel.items():
            click.echo(f"\n  {stage.upper()} → {data['goal']}")
            for t in data["tactics"][:3]:
                click.echo(f"    • {t}")
    else:
        output({"tips": tips, "funnel": funnel})


@theme_page.command("calendar")
@click.option("--niche", "-n", required=True)
@handle_error
def theme_page_calendar(niche):
    """Generate a 7-day content calendar for a theme page."""
    calendar = theme_mod.CONTENT_CALENDAR_TEMPLATE
    niche_data = theme_mod.PROVEN_NICHES.get(niche.lower(), {})
    ratio = niche_data.get("content_ratio", {"educational": 40, "entertaining": 40, "promotional": 20})

    if not _json_output:
        click.echo(f"\n✓ 7-Day Content Calendar for {niche.upper()} Theme Page\n")
        click.echo(f"  Content mix: {ratio}\n")
        for day, info in calendar.items():
            click.echo(f"  {day.upper():<12}: [{info['theme']}]")
            click.echo(f"               Format: {info['format']}")
        click.echo()
        click.echo("  TIP: Batch-create all 7 days in one filming session (2-3 hours)")
    else:
        output({"calendar": calendar, "content_ratio": ratio, "niche": niche})


# ── Config Group ───────────────────────────────────────────────────────

@cli.group()
def config():
    """Configuration — API keys, accounts, settings."""
    pass


@config.command("set")
@click.argument("key", type=click.Choice([
    "youtube_api_key", "tiktok_session_id", "default_country", "default_platform"
]))
@click.argument("value")
def config_set(key, value):
    """Set a configuration value."""
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)
    display = value[:10] + "..." if "key" in key and len(value) > 10 else value
    output({"key": key, "value": display}, f"✓ Set {key} = {display}")


@config.command("get")
@click.argument("key", required=False)
def config_get(key):
    """Show configuration (or all config)."""
    cfg = load_config()
    if key:
        val = cfg.get(key)
        masked = val[:10] + "..." if val and "key" in key and len(val) > 10 else val
        output({"key": key, "value": masked}, f"{key} = {masked}")
    else:
        masked = {}
        for k, v in cfg.items():
            masked[k] = v[:10] + "..." if v and "key" in k and len(v) > 10 else v
        output(masked if masked else {}, "Configuration:" if masked else "No configuration set")


@config.command("path")
def config_path():
    """Show config file path."""
    from cli_anything.social_trends.utils.social_trends_backend import CONFIG_FILE
    output({"path": str(CONFIG_FILE)}, f"Config: {CONFIG_FILE}")


# ── Session Group ──────────────────────────────────────────────────────

@cli.group()
def session():
    """Session history — view, undo, redo past commands."""
    pass


@session.command("history")
@click.option("--limit", "-n", default=20, type=int)
def session_history(limit):
    """Show command history."""
    sess = get_session()
    entries = sess.history(limit=limit)
    output(entries, f"History ({len(entries)} entries):" if entries else "No history.")


@session.command("status")
def session_status():
    """Show session status."""
    sess = get_session()
    output(sess.status())


@session.command("undo")
def session_undo():
    """Undo last command."""
    sess = get_session()
    entry = sess.undo()
    if entry:
        output(entry.to_dict(), f"✓ Undone: {entry.command}")
    else:
        output({"error": "Nothing to undo"}, "Nothing to undo")


# ── REPL ───────────────────────────────────────────────────────────────

@cli.command("repl", hidden=True)
def repl():
    """Interactive REPL mode."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.social_trends.utils.repl_skin import ReplSkin
    skin = ReplSkin("social-trends", version="1.0.0")
    skin.print_banner()
    pt_session = skin.create_prompt_session()

    commands = {
        "trends scrape --platform all": "Scrape YouTube + TikTok trending",
        "trends hashtags": "Top trending hashtags",
        "trends music": "Trending TikTok sounds",
        "trends analyze": "Full trend analysis report",
        "account add --platform <p> --username <u> --niche <n>": "Register account",
        "account list": "List registered accounts",
        "account optimize --platform <p> --niche <n>": "Optimize one account",
        "account optimize-all": "Optimize all accounts",
        "theme-page niches": "List supported niches",
        "theme-page guide --niche <n>": "Full theme page guide",
        "theme-page convert --niche <n>": "Conversion optimization tips",
        "theme-page calendar --niche <n>": "7-day content calendar",
        "config set <key> <value>": "Set API key or setting",
        "config get": "Show configuration",
        "session history": "Command history",
        "help": "Show this help",
        "quit / exit": "Exit REPL",
    }

    while True:
        try:
            line = skin.get_input(pt_session, context="social-trends")
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

        if not line:
            continue
        if line in ("quit", "exit", "q"):
            skin.print_goodbye()
            break
        if line == "help":
            skin.help(commands)
            continue

        parts = line.split()
        try:
            cli.main(parts, standalone_mode=False)
        except SystemExit:
            pass
        except click.exceptions.UsageError as e:
            skin.error(str(e))
        except Exception as e:
            skin.error(str(e))


def main():
    cli()


if __name__ == "__main__":
    main()
