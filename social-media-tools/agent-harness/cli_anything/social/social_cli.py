#!/usr/bin/env python3
"""Social Media Trend Scraper & Account Optimizer CLI.

Usage:
    # Scrape trending content
    social trends youtube --category music --limit 20
    social trends tiktok --region US --limit 30
    social trends combined --limit 30
    social trends music

    # Generate optimized hashtags
    social hashtags generate --niche fitness --platform tiktok
    social hashtags youtube --niche crypto

    # Optimize your accounts
    social optimize account --platform tiktok --handle @yourhandle --niche fitness
    social optimize schedule --platform youtube
    social optimize batch --file accounts.json

    # Theme page tools
    social theme guide --niche finance
    social theme niches --sort affiliate_potential
    social theme value --platform instagram --followers 50000 --revenue 500

    # Interactive REPL
    social
"""

import sys
import os
import json
from pathlib import Path
from typing import Optional

import click

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social.core.session import Session
from cli_anything.social.core import youtube_scraper as yt
from cli_anything.social.core import tiktok_scraper as tt
from cli_anything.social.core import trend_analyzer as ta
from cli_anything.social.core import account_optimizer as ao
from cli_anything.social.core import theme_page as tp

_session: Optional[Session] = None
_json_output = False
_repl_mode = False


def get_session() -> Session:
    global _session
    if _session is None:
        sf = str(Path.home() / ".cli-anything-social" / "session.json")
        _session = Session(session_file=sf)
    return _session


def output(data, message: str = ""):
    """Unified output: JSON or human-readable."""
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.secho(message, fg="cyan", bold=True)
        if isinstance(data, list):
            _print_list(data)
        elif isinstance(data, dict):
            _print_dict(data)
        else:
            click.echo(str(data))


def _print_list(items: list, depth: int = 0):
    indent = "  " * depth
    for item in items:
        if isinstance(item, dict):
            _print_dict(item, depth)
            click.echo("")
        else:
            click.echo(f"{indent}• {item}")


def _print_dict(d: dict, depth: int = 0):
    indent = "  " * depth
    skip_keys = {"raw", "weekly_schedule"}
    for key, val in d.items():
        if key in skip_keys:
            continue
        label = key.replace("_", " ").title()
        if isinstance(val, dict):
            click.secho(f"{indent}{label}:", fg="yellow")
            _print_dict(val, depth + 1)
        elif isinstance(val, list):
            click.secho(f"{indent}{label}:", fg="yellow")
            for item in val[:8]:  # cap list display
                if isinstance(item, dict):
                    _print_dict(item, depth + 1)
                    click.echo("")
                else:
                    click.echo(f"{indent}  • {item}")
        else:
            color = "green" if key in ("rank", "score", "priority") else None
            click.secho(f"{indent}{label}: ", fg="yellow", nl=False)
            click.secho(str(val), fg=color)


# ─── Root group ───────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output JSON")
@click.pass_context
def cli(ctx, use_json):
    """Social Media Trend Scraper & Account Optimizer."""
    global _json_output, _repl_mode
    _json_output = use_json
    if ctx.invoked_subcommand is None:
        _repl_mode = True
        _run_repl()


# ─── TRENDS group ─────────────────────────────────────────────────────────────

@cli.group()
def trends():
    """Scrape trending content from YouTube and TikTok."""
    pass


@trends.command("youtube")
@click.option("--category", "-c", default="now",
              type=click.Choice(["now", "music", "gaming", "movies"]),
              help="Trending category")
@click.option("--limit", "-n", default=20, help="Number of results")
@click.option("--region", "-r", default="US", help="Country code")
@click.option("--api-key", envvar="YOUTUBE_API_KEY", help="YouTube Data API v3 key")
def trends_youtube(category, limit, region, api_key):
    """Scrape YouTube trending videos."""
    if not _json_output:
        click.secho(f"Scraping YouTube trending ({category})...", fg="blue")
    results = yt.scrape_trending_videos(
        category=category, country=region, limit=limit, api_key=api_key
    )
    get_session().cache_trends("youtube", results)
    get_session().log("youtube_trend_scrape", f"category={category} limit={limit}")
    output(results, f"YouTube Trending — {category.title()} ({len(results)} videos)")


@trends.command("tiktok")
@click.option("--limit", "-n", default=20, help="Number of results")
@click.option("--region", "-r", default="US", help="Country/region code")
def trends_tiktok(limit, region):
    """Scrape TikTok trending videos."""
    if not _json_output:
        click.secho("Scraping TikTok trending...", fg="blue")
    results = tt.scrape_trending_videos(region=region, limit=limit)
    get_session().cache_trends("tiktok", results)
    get_session().log("tiktok_trend_scrape", f"limit={limit} region={region}")
    output(results, f"TikTok Trending ({len(results)} videos)")


@trends.command("combined")
@click.option("--limit", "-n", default=30, help="Results per platform")
@click.option("--region", "-r", default="US", help="Region code")
@click.option("--api-key", envvar="YOUTUBE_API_KEY", help="YouTube Data API v3 key")
def trends_combined(limit, region, api_key):
    """Cross-platform trend analysis (YouTube + TikTok combined)."""
    if not _json_output:
        click.secho("Scraping cross-platform trends (YouTube + TikTok)...", fg="blue")
    data = ta.get_cross_platform_trends(
        limit=limit, yt_api_key=api_key, region=region
    )
    get_session().cache_trends("combined", data.get("trending_topics", []))
    get_session().log("combined_trend_scrape", f"limit={limit}")

    if _json_output:
        output(data)
        return

    click.secho("\n🔥 TOP TRENDING TOPICS", fg="magenta", bold=True)
    for t in data["trending_topics"][:10]:
        platforms = ", ".join(t.get("platforms", []))
        cross = "✨ CROSS-PLATFORM" if t.get("is_cross_platform") else ""
        views_m = t.get("total_views", 0) / 1_000_000
        click.echo(
            f"  {t['rank']:2}. {t['keyword']:20} "
            f"[{platforms}] {views_m:.1f}M views {cross}"
        )

    click.secho("\n📌 TOP TRENDING HASHTAGS", fg="magenta", bold=True)
    for h in data["trending_hashtags"][:15]:
        platforms = ", ".join(h.get("platforms", []))
        cross = "✨" if h.get("is_cross_platform") else ""
        click.echo(f"  {h['rank']:2}. {h['hashtag']:25} [{platforms}] {cross}")

    click.secho("\n🎵 TRENDING MUSIC", fg="magenta", bold=True)
    for m in data["trending_music"][:8]:
        platforms = ", ".join(m.get("platforms", []))
        cross = "✨ CROSS-PLATFORM" if m.get("is_cross_platform") else ""
        click.echo(
            f"  {m['rank']:2}. {m['song_title']:25} — {m['artist']:20} "
            f"[{platforms}] {cross}"
        )

    click.secho("\n💡 CONTENT OPPORTUNITIES", fg="green", bold=True)
    for i, opp in enumerate(data["content_opportunities"][:5], 1):
        priority_color = "red" if opp["priority"] == "HIGH" else "yellow"
        click.secho(f"  {i}. [{opp['priority']}] ", fg=priority_color, nl=False)
        click.echo(opp["opportunity"])
        click.secho(f"     Action: {opp['action']}", fg="cyan")


@trends.command("music")
@click.option("--platform", "-p", default="both",
              type=click.Choice(["youtube", "tiktok", "both"]))
@click.option("--limit", "-n", default=20)
@click.option("--region", "-r", default="US")
@click.option("--api-key", envvar="YOUTUBE_API_KEY")
def trends_music(platform, limit, region, api_key):
    """Scrape trending music/audio across platforms."""
    results = []
    if platform in ("youtube", "both"):
        click.secho("Fetching YouTube trending music...", fg="blue")
        results += yt.scrape_trending_music(api_key=api_key, limit=limit)
    if platform in ("tiktok", "both"):
        click.secho("Fetching TikTok trending audio...", fg="blue")
        results += tt.scrape_trending_music(region=region, limit=limit)

    get_session().log("music_trend_scrape", f"platform={platform}")

    if _json_output:
        output(results)
        return

    click.secho("\n🎵 TRENDING MUSIC / AUDIO", fg="magenta", bold=True)
    for m in results[:limit]:
        if "error" in m:
            continue
        rank = m.get("rank", "?")
        song = m.get("song_title", m.get("music_title", "Unknown"))[:30]
        artist = m.get("artist", m.get("music_author", "Unknown"))[:25]
        plat = m.get("platform", "")
        views = m.get("views", 0) or m.get("total_views", 0)
        click.echo(f"  {rank:2}. {song:32} — {artist:27} [{plat}]  {views/1e6:.1f}M")


# ─── HASHTAGS group ───────────────────────────────────────────────────────────

@cli.group()
def hashtags():
    """Generate and analyze hashtag strategies."""
    pass


@hashtags.command("generate")
@click.option("--niche", "-n", required=True, help="Your content niche (e.g. fitness, crypto)")
@click.option("--platform", "-p", default="both",
              type=click.Choice(["youtube", "tiktok", "instagram", "both"]))
@click.option("--size", "-s", default="medium",
              type=click.Choice(["small", "medium", "large"]))
@click.option("--api-key", envvar="YOUTUBE_API_KEY")
def hashtags_generate(niche, platform, size, api_key):
    """Generate an optimized hashtag set for your niche."""
    if not _json_output:
        click.secho(f"Generating {size} hashtag set for '{niche}' on {platform}...", fg="blue")
    result = ta.generate_hashtag_set(
        niche=niche, platform=platform, size=size, yt_api_key=api_key
    )
    get_session().log("hashtag_generate", f"niche={niche} platform={platform}")

    if _json_output:
        output(result)
        return

    click.secho(f"\n#{niche.upper()} HASHTAG SET ({result['hashtag_count']} tags)", fg="magenta", bold=True)
    click.echo("")
    click.secho("Copy-paste ready:", fg="green")
    click.echo(result["hashtag_string"])
    click.echo("")
    click.secho("Strategy breakdown:", fg="yellow")
    for cat, tags in result["strategy"].items():
        click.echo(f"  {cat.replace('_', ' ').title()}: {' '.join(tags)}")
    click.echo("")
    click.secho("Tips:", fg="cyan")
    for tip in result["tips"]:
        click.echo(f"  • {tip}")


@hashtags.command("youtube")
@click.option("--niche", "-n", required=True)
@click.option("--limit", "-l", default=20)
@click.option("--api-key", envvar="YOUTUBE_API_KEY")
def hashtags_youtube(niche, limit, api_key):
    """Find top YouTube hashtags for a niche."""
    click.secho(f"Searching YouTube for '{niche}' hashtags...", fg="blue")
    results = yt.get_niche_hashtags(niche, api_key=api_key, limit=limit)
    output(results, f"YouTube hashtags for '{niche}'")


@hashtags.command("tiktok")
@click.option("--niche", "-n", required=True)
@click.option("--limit", "-l", default=20)
@click.option("--region", "-r", default="US")
def hashtags_tiktok(niche, limit, region):
    """Find top TikTok hashtags for a niche."""
    click.secho(f"Searching TikTok for '{niche}' hashtags...", fg="blue")
    all_tags = tt.scrape_trending_hashtags(region=region, limit=50)
    niche_words = set(niche.lower().split())
    filtered = [
        t for t in all_tags
        if any(w in t.get("hashtag", "").lower() for w in niche_words)
    ]
    if not filtered:
        filtered = all_tags[:limit]
    output(filtered[:limit], f"TikTok hashtags for '{niche}'")


# ─── OPTIMIZE group ───────────────────────────────────────────────────────────

@cli.group()
def optimize():
    """Optimize your social media accounts."""
    pass


@optimize.command("account")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram", "twitter", "facebook"]))
@click.option("--handle", "-h", required=True, help="Your account handle/username")
@click.option("--niche", "-n", default="", help="Your content niche")
@click.option("--bio", "-b", default="", help="Your current bio text")
@click.option("--followers", "-f", default=0, type=int, help="Current follower count")
@click.option("--posts", default=0, type=int, help="Total post count")
@click.option("--avg-views", default=0, type=int, help="Average views per post")
def optimize_account(platform, handle, niche, bio, followers, posts, avg_views):
    """Analyze and optimize a social media account."""
    if not _json_output:
        click.secho(f"Analyzing {platform} account @{handle}...", fg="blue")

    result = ao.analyze_account_profile(
        platform=platform,
        handle=handle,
        niche=niche,
        bio_text=bio,
        follower_count=followers,
        post_count=posts,
        avg_views=avg_views,
    )

    get_session().add_account(platform, handle, niche)
    get_session().log("account_optimize", f"@{handle} on {platform}")

    if _json_output:
        output(result)
        return

    score = result["optimization_score"]
    score_color = "green" if score >= 70 else ("yellow" if score >= 40 else "red")
    click.echo("")
    click.secho(f"ACCOUNT ANALYSIS: @{handle} on {platform.upper()}", fg="magenta", bold=True)
    click.secho(f"Optimization Score: ", nl=False)
    click.secho(f"{score}/100", fg=score_color, bold=True)

    stage = result["growth_stage"]
    click.secho(f"Growth Stage: {stage['stage']} ({stage.get('follower_range', '')})", fg="cyan")
    click.echo(f"  → {stage['advice']}")

    if result["wins"]:
        click.secho("\n✅ WHAT'S WORKING:", fg="green")
        for win in result["wins"]:
            click.echo(f"  ✓ {win}")

    if result["issues"]:
        click.secho("\n⚠️  ISSUES TO FIX:", fg="red")
        for issue in result["issues"]:
            click.echo(f"  ✗ {issue}")

    click.secho("\n📋 RECOMMENDATIONS:", fg="yellow")
    for rec in result["recommendations"][:6]:
        click.echo(f"  • {rec}")

    click.secho("\n🎯 NEXT STEPS:", fg="cyan")
    for step in result["next_steps"]:
        click.echo(f"  {step}")

    monetize = stage.get("monetization_unlocked", [])
    if monetize:
        click.secho("\n💰 MONETIZATION AVAILABLE:", fg="green")
        for m in monetize:
            click.echo(f"  $ {m}")


@optimize.command("schedule")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram", "twitter", "facebook"]))
def optimize_schedule(platform):
    """Get the optimal posting schedule for a platform."""
    result = ao.get_optimal_schedule(platform)
    get_session().log("schedule_optimize", f"platform={platform}")

    if _json_output:
        output(result)
        return

    click.secho(f"\nOPTIMAL POSTING SCHEDULE — {platform.upper()}", fg="magenta", bold=True)
    freq = result["frequency"]
    click.echo(f"  Frequency: {freq['min']}-{freq['max']}x per {freq['unit']}")
    click.echo(f"  Note: {freq.get('note', '')}")
    click.echo(f"  Best days: {', '.join(result['best_days'])}")
    click.echo(f"  Best hours (UTC): {', '.join(result['best_hours_utc'])}")
    click.echo(f"\n  {result['note']}")
    click.secho("\nWeekly Schedule:", fg="yellow")
    for day, info in result["weekly_schedule"].items():
        if info["post"]:
            times_str = ", ".join(info["times"])
            click.secho(f"  ✓ {day:12}", fg="green", nl=False)
            click.echo(f" Post at: {times_str}")
        else:
            click.secho(f"  - {day:12}", fg="white")
            click.echo(" Rest day")


@optimize.command("batch")
@click.option("--file", "-f", "filepath", required=True,
              help="JSON file with array of accounts")
def optimize_batch(filepath):
    """Optimize multiple accounts from a JSON file."""
    try:
        with open(filepath) as f:
            accounts = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        click.secho(f"Error reading file: {e}", fg="red")
        return

    click.secho(f"Optimizing {len(accounts)} accounts...", fg="blue")
    results = ao.batch_optimize_accounts(accounts)
    get_session().log("batch_optimize", f"count={len(accounts)}")
    output(results, f"Batch Optimization Results ({len(results)} accounts)")


# ─── THEME PAGE group ─────────────────────────────────────────────────────────

@cli.group("theme")
def theme():
    """Theme page creation, growth, and monetization tools."""
    pass


@theme.command("guide")
@click.option("--niche", "-n", default="", help="Filter guide to specific niche")
@click.option("--platform", "-p", default="all",
              type=click.Choice(["tiktok", "instagram", "youtube", "all"]))
def theme_guide(niche, platform):
    """Complete guide for creating and converting theme pages."""
    click.secho("Loading theme page guide...", fg="blue")
    guide = tp.get_theme_page_guide(niche=niche, platform=platform)
    get_session().log("theme_guide", f"niche={niche}")

    if _json_output:
        output(guide)
        return

    def_section = guide["what_is_theme_page"]
    click.secho("\n📱 WHAT IS A THEME PAGE?", fg="magenta", bold=True)
    click.echo(f"  {def_section['definition']}")
    click.secho("\nExamples:", fg="yellow")
    for ex in def_section["examples"]:
        click.echo(f"  • {ex}")
    click.secho("\nWhy theme pages?", fg="yellow")
    for why in def_section["why_theme_pages"]:
        click.echo(f"  ✓ {why}")

    for phase_key in ["phase_1_setup", "phase_2_growth", "phase_3_monetization", "phase_4_selling"]:
        phase = guide[phase_key]
        click.secho(f"\n{'─'*60}", fg="white")
        click.secho(f"  {phase['title']}", fg="cyan", bold=True)
        items = phase.get("steps") or phase.get("strategies") or phase.get(
            "revenue_streams") or phase.get("preparation", [])
        for item in items[:4]:
            if isinstance(item, dict):
                label = item.get("step", "") or item.get("strategy", "") or item.get("method", "")
                detail = item.get("detail", "") or item.get("how", "") or item.get("action", "")
                click.secho(f"  → {label}: ", fg="yellow", nl=False)
                click.echo(detail[:120])
            else:
                click.echo(f"  • {item}")

    click.secho("\n30-DAY ACTION PLAN:", fg="green", bold=True)
    for week in guide["30_day_action_plan"]:
        click.secho(f"\n  {week['week']} — {week['focus']}", fg="cyan")
        for task in week["tasks"][:3]:
            click.echo(f"    • {task}")


@theme.command("niches")
@click.option("--sort", "-s", default="rank",
              type=click.Choice(["rank", "affiliate_potential", "difficulty"]))
@click.option("--platform", "-p", default="", help="Filter by platform")
@click.option("--difficulty", "-d", default="", help="Filter by difficulty (Low/Medium/High)")
def theme_niches(sort, platform, difficulty):
    """List profitable niches for theme pages, ranked by potential."""
    results = tp.find_profitable_niches(
        filter_difficulty=difficulty or None,
        filter_platform=platform or None,
        sort_by=sort,
    )
    get_session().log("theme_niches", f"sort={sort}")

    if _json_output:
        output(results)
        return

    click.secho("\n💰 PROFITABLE NICHES FOR THEME PAGES", fg="magenta", bold=True)
    click.echo(f"  Sorted by: {sort} | Showing {len(results)} niches\n")
    for n in results:
        click.secho(f"  #{n['rank']} {n['niche']:25}", fg="cyan", bold=True, nl=False)
        click.echo(
            f"  CPM: {n['avg_cpm']:10}  "
            f"Affiliate: {n['affiliate_potential']:6}  "
            f"Difficulty: {n['difficulty']}"
        )
        click.echo(f"      Platforms: {', '.join(n['best_platforms'])}")
        click.secho(f"      Why: {n['why_profitable']}", fg="green")
        click.echo("")


@theme.command("value")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]))
@click.option("--followers", "-f", required=True, type=int)
@click.option("--revenue", "-r", default=0.0, type=float,
              help="Monthly revenue ($)")
@click.option("--engagement", "-e", default=0.0, type=float,
              help="Engagement rate (%)")
@click.option("--niche", "-n", default="")
def theme_value(platform, followers, revenue, engagement, niche):
    """Estimate the sale value of a social media account."""
    result = tp.estimate_account_value(
        platform=platform,
        followers=followers,
        monthly_revenue=revenue,
        engagement_rate=engagement,
        niche=niche,
    )
    get_session().log("theme_value", f"platform={platform} followers={followers}")

    if _json_output:
        output(result)
        return

    click.secho(f"\n💵 ACCOUNT VALUE ESTIMATE", fg="magenta", bold=True)
    click.secho(f"  Platform:      {result['platform'].upper()}", fg="cyan")
    click.secho(f"  Followers:     {result['followers']:,}", fg="cyan")
    click.secho(f"  Estimated:     {result['value_range']}", fg="green", bold=True)
    click.echo(f"  Engagement:    {result['engagement_tier']}")
    click.echo(f"  Niche:         {result['niche_note']}")
    click.echo(f"  Where to sell: {', '.join(result['where_to_sell'])}")
    click.secho("\nTips:", fg="yellow")
    for tip in result["tips"]:
        click.echo(f"  • {tip}")


# ─── ACCOUNTS group ───────────────────────────────────────────────────────────

@cli.group()
def accounts():
    """Manage your tracked social media accounts."""
    pass


@accounts.command("add")
@click.option("--platform", "-p", required=True)
@click.option("--handle", "-h", required=True)
@click.option("--niche", "-n", default="")
def accounts_add(platform, handle, niche):
    """Add an account to your tracked list."""
    get_session().add_account(platform, handle, niche)
    click.secho(f"Added @{handle} on {platform} (niche: {niche or 'unset'})", fg="green")


@accounts.command("list")
def accounts_list():
    """List all tracked accounts."""
    accs = get_session().get_accounts()
    if not accs:
        click.echo("No accounts tracked yet. Use `social accounts add` to add one.")
        return
    output(accs, f"Tracked Accounts ({len(accs)})")


@accounts.command("optimize-all")
@click.option("--api-key", envvar="YOUTUBE_API_KEY")
def accounts_optimize_all(api_key):
    """Run optimization analysis on all tracked accounts."""
    accs = get_session().get_accounts()
    if not accs:
        click.secho("No accounts tracked. Add accounts first with `social accounts add`.", fg="red")
        return

    click.secho(f"Optimizing {len(accs)} accounts...", fg="blue")
    results = ao.batch_optimize_accounts(accs)
    get_session().log("optimize_all", f"count={len(accs)}")

    if _json_output:
        output(results)
        return

    for result in results:
        score = result["optimization_score"]
        score_color = "green" if score >= 70 else ("yellow" if score >= 40 else "red")
        click.echo("")
        click.secho(
            f"@{result['handle']} ({result['platform']}) — Score: ",
            fg="cyan", nl=False
        )
        click.secho(f"{score}/100", fg=score_color, bold=True)
        if result["issues"]:
            click.secho(f"  Issues: {result['issues'][0]}", fg="red")
        if result["next_steps"]:
            click.secho(f"  Next: {result['next_steps'][0]}", fg="yellow")


# ─── REPL ─────────────────────────────────────────────────────────────────────

def _run_repl():
    """Interactive REPL mode."""
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import FileHistory
        history_file = str(Path.home() / ".cli-anything-social" / "history.txt")
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        ps = PromptSession(history=FileHistory(history_file))
        use_prompt_toolkit = True
    except ImportError:
        use_prompt_toolkit = False

    click.secho("=" * 60, fg="magenta")
    click.secho("  Social Media Trend Scraper & Account Optimizer", fg="cyan", bold=True)
    click.secho("  Type 'help' for commands, 'exit' to quit", fg="white")
    click.secho("=" * 60, fg="magenta")

    while True:
        try:
            if use_prompt_toolkit:
                user_input = ps.prompt("social> ").strip()
            else:
                user_input = input("social> ").strip()
        except (EOFError, KeyboardInterrupt):
            click.echo("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            click.echo("Goodbye!")
            break
        if user_input.lower() == "help":
            _print_help()
            continue

        try:
            args = user_input.split()
            standalone_cli(args, standalone_mode=False)
        except SystemExit:
            pass
        except Exception as e:
            click.secho(f"Error: {e}", fg="red")


def _print_help():
    click.secho("\nAvailable Commands:", fg="cyan", bold=True)
    commands = [
        ("trends youtube", "Scrape YouTube trending videos"),
        ("trends tiktok", "Scrape TikTok trending videos"),
        ("trends combined", "Cross-platform trend analysis"),
        ("trends music", "Trending music/audio"),
        ("hashtags generate --niche <n>", "Generate optimized hashtag set"),
        ("hashtags youtube --niche <n>", "YouTube niche hashtags"),
        ("hashtags tiktok --niche <n>", "TikTok niche hashtags"),
        ("optimize account -p <platform> -h <handle>", "Optimize an account"),
        ("optimize schedule -p <platform>", "Get optimal posting schedule"),
        ("optimize batch -f <file.json>", "Batch optimize accounts"),
        ("accounts add -p <platform> -h <handle>", "Track an account"),
        ("accounts list", "List tracked accounts"),
        ("accounts optimize-all", "Optimize all tracked accounts"),
        ("theme guide", "Theme page creation guide"),
        ("theme niches", "Profitable niche rankings"),
        ("theme value -p <platform> -f <followers>", "Estimate account value"),
    ]
    for cmd, desc in commands:
        click.secho(f"  social {cmd:45}", fg="yellow", nl=False)
        click.echo(f" — {desc}")
    click.echo("")


def standalone_cli(args=None, **kwargs):
    return cli(args, **kwargs)


if __name__ == "__main__":
    cli()
