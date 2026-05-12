"""cli-anything-social-trends — CLI entry point.

Commands:
  session new/info/save/load          — manage trend research sessions
  account add/remove/list             — manage social accounts
  trends fetch youtube/tiktok/all     — pull viral trend data
  hashtags recommend/sets/score       — hashtag research & sets
  music trending                      — trending sounds/music
  optimize run/calendar               — account optimization & content calendar
  theme-page guide/niches/score       — theme page strategy
  repl                                — interactive REPL
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import click

from . import __version__
from .core import TrendSession, default_session_path, session_exists
from .trends import merge_hashtags, merge_trends, generate_hashtag_sets, score_content_idea
from .optimizer import generate_optimization_report, build_content_calendar
from .theme_pages import list_niches, get_niche, score_niche, get_theme_page_guide

# ── Shared state ───────────────────────────────────────────────────────

pass_session = click.make_pass_decorator(TrendSession, ensure=False)


def _load_session_or_die(ctx: click.Context, project: str) -> TrendSession:
    path = project or default_session_path("session")
    if not session_exists(path):
        raise click.ClickException(
            f"No session found at {path!r}. Run: cli-anything-social-trends session new"
        )
    return TrendSession.load(path)


def _output(data: Any, as_json: bool) -> None:
    if as_json:
        click.echo(json.dumps(data, indent=2))
    else:
        if isinstance(data, str):
            click.echo(data)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    for k, v in item.items():
                        click.echo(f"  {k}: {v}")
                    click.echo()
                else:
                    click.echo(f"  {item}")
        elif isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, (list, dict)):
                    click.echo(f"\n  {k}:")
                    if isinstance(v, list):
                        for entry in v:
                            click.echo(f"    • {entry}")
                    else:
                        for kk, vv in v.items():
                            click.echo(f"    {kk}: {vv}")
                else:
                    click.echo(f"  {k}: {v}")


# ── Root group ─────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("--project", "-p", default="", help="Session file path (.trends.json)")
@click.version_option(__version__, prog_name="cli-anything-social-trends")
@click.pass_context
def cli(ctx: click.Context, as_json: bool, project: str) -> None:
    """cli-anything Social Trends — YouTube & TikTok viral trend research and account optimization."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = as_json
    ctx.obj["project"] = project

    if ctx.invoked_subcommand is None:
        # Launch REPL
        _launch_repl(project)


# ── session commands ───────────────────────────────────────────────────

@cli.group()
def session() -> None:
    """Manage trend research sessions."""


@session.command("new")
@click.argument("name", default="session")
@click.option("--region", "-r", default="US", help="Target region (ISO code, e.g. US, GB, IN)")
@click.option("--niche", "-n", default="", help="Focus niche (e.g. fitness, food, luxury)")
@click.option("--output", "-o", default="", help="Output file path")
@click.pass_context
def session_new(ctx: click.Context, name: str, region: str, niche: str, output: str) -> None:
    """Create a new trend research session."""
    path = output or default_session_path(name)
    if session_exists(path):
        raise click.ClickException(f"Session already exists at {path!r}. Use a different name or delete it first.")

    sess = TrendSession(name=name, region=region.upper(), niche=niche)
    sess.save(path)

    result = {"path": path, "name": name, "region": region.upper(), "niche": niche or "(all)"}
    if ctx.obj.get("json"):
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(f"  ✓ Created session: {name}")
        click.echo(f"    Path:   {path}")
        click.echo(f"    Region: {region.upper()}")
        click.echo(f"    Niche:  {niche or '(all)'}")


@session.command("info")
@click.pass_context
def session_info(ctx: click.Context) -> None:
    """Show current session summary."""
    sess = _load_session_or_die(ctx, ctx.obj.get("project", ""))
    result = sess.summary
    _output(result, ctx.obj.get("json", False))


@session.command("save")
@click.option("--output", "-o", default="", help="Save to path (defaults to current session path)")
@click.pass_context
def session_save(ctx: click.Context, output: str) -> None:
    """Save the current session."""
    project = ctx.obj.get("project", "")
    sess = _load_session_or_die(ctx, project)
    path = output or project or default_session_path(sess.name)
    sess.save(path)
    if ctx.obj.get("json"):
        click.echo(json.dumps({"saved": path}))
    else:
        click.echo(f"  ✓ Saved session to {path}")


# ── account commands ───────────────────────────────────────────────────

@cli.group()
def account() -> None:
    """Manage social media accounts to optimize."""


@account.command("add")
@click.argument("platform", type=click.Choice(["tiktok", "instagram", "youtube"], case_sensitive=False))
@click.argument("handle")
@click.option("--niche", "-n", default="", help="Account niche (overrides session niche)")
@click.pass_context
def account_add(ctx: click.Context, platform: str, handle: str, niche: str) -> None:
    """Add a social account to the session.

    PLATFORM: tiktok | instagram | youtube
    HANDLE: @username or channel name
    """
    project = ctx.obj.get("project", "")
    sess = _load_session_or_die(ctx, project)
    acct = sess.add_account(platform.lower(), handle, niche)
    sess.save(project or default_session_path(sess.name))

    if ctx.obj.get("json"):
        click.echo(json.dumps(acct, indent=2))
    else:
        click.echo(f"  ✓ Added {platform} account: {handle}")


@account.command("remove")
@click.argument("handle")
@click.pass_context
def account_remove(ctx: click.Context, handle: str) -> None:
    """Remove an account from the session."""
    project = ctx.obj.get("project", "")
    sess = _load_session_or_die(ctx, project)
    removed = sess.remove_account(handle)
    sess.save(project or default_session_path(sess.name))

    if ctx.obj.get("json"):
        click.echo(json.dumps({"removed": removed, "handle": handle}))
    elif removed:
        click.echo(f"  ✓ Removed account: {handle}")
    else:
        click.echo(f"  ⚠ Account not found: {handle}")


@account.command("list")
@click.pass_context
def account_list(ctx: click.Context) -> None:
    """List all accounts in the session."""
    project = ctx.obj.get("project", "")
    sess = _load_session_or_die(ctx, project)

    if ctx.obj.get("json"):
        click.echo(json.dumps(sess.accounts, indent=2))
    elif not sess.accounts:
        click.echo("  No accounts added. Use: account add <platform> <handle>")
    else:
        click.echo(f"\n  {'Platform':<12} {'Handle':<25} {'Niche':<20}")
        click.echo(f"  {'-'*11} {'-'*24} {'-'*19}")
        for a in sess.accounts:
            click.echo(f"  {a['platform']:<12} {a['handle']:<25} {a.get('niche',''):<20}")
        click.echo()


# ── trends commands ────────────────────────────────────────────────────

@cli.group()
def trends() -> None:
    """Fetch viral trends from YouTube and TikTok."""


@trends.command("fetch")
@click.argument("platform", type=click.Choice(["youtube", "tiktok", "all"]), default="all")
@click.option("--region", "-r", default="", help="Region code (default: from session)")
@click.option("--niche", "-n", default="", help="Niche/topic filter")
@click.option("--max", "max_results", default=25, help="Max results per platform")
@click.option("--mock", is_flag=True, help="Use mock data (no API key needed)")
@click.pass_context
def trends_fetch(
    ctx: click.Context,
    platform: str,
    region: str,
    niche: str,
    max_results: int,
    mock: bool,
) -> None:
    """Fetch trending content from YouTube and/or TikTok.

    PLATFORM: youtube | tiktok | all (default)

    Requires API keys:
      YouTube: set YOUTUBE_API_KEY env var
      TikTok:  set TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET env vars

    Use --mock for demo mode without API keys.
    """
    project = ctx.obj.get("project", "")
    sess = _load_session_or_die(ctx, project)
    effective_region = region or sess.region
    effective_niche = niche or sess.niche

    yt_trends = []
    tt_trends = []

    verbose = not ctx.obj.get("json")

    if platform in ("youtube", "all"):
        if mock:
            if verbose:
                click.echo("  ● [Mock] Using sample YouTube trend data...")
            yt_trends = _mock_youtube_trends(effective_region)
        else:
            try:
                from .youtube import fetch_trending_videos, search_trending_topic
                if verbose:
                    click.echo(f"  ● Fetching YouTube trends (region={effective_region})...")
                if effective_niche:
                    yt_trends = search_trending_topic(effective_niche, region=effective_region, max_results=max_results)
                else:
                    yt_trends = fetch_trending_videos(region=effective_region, max_results=max_results)
            except (EnvironmentError, ImportError) as exc:
                if verbose:
                    click.echo(f"  ⚠ YouTube: {exc}\n    Use --mock for demo data.")

    if platform in ("tiktok", "all"):
        if mock:
            from .tiktok import fetch_mock_trends
            if verbose:
                click.echo("  ● [Mock] Using sample TikTok trend data...")
            tt_trends = fetch_mock_trends(effective_region)
        else:
            try:
                from .tiktok import query_videos
                keywords = [effective_niche] if effective_niche else ["trending", "viral"]
                if verbose:
                    click.echo(f"  ● Fetching TikTok trends (keywords={keywords})...")
                tt_trends = query_videos(keywords, region=effective_region, max_count=max_results)
            except (EnvironmentError, ImportError) as exc:
                if verbose:
                    click.echo(f"  ⚠ TikTok: {exc}\n    Use --mock for demo data.")

    sess.set_youtube_trends(yt_trends)
    sess.set_tiktok_trends(tt_trends)
    sess.save(project or default_session_path(sess.name))

    combined = merge_trends(yt_trends, tt_trends)

    if ctx.obj.get("json"):
        click.echo(json.dumps(combined[:20], indent=2))
    else:
        click.echo(f"\n  ✓ Fetched {len(yt_trends)} YouTube + {len(tt_trends)} TikTok trends")
        click.echo(f"\n  {'#':<4} {'Platform':<10} {'Title':<45} {'Score':<8}")
        click.echo(f"  {'-'*3} {'-'*9} {'-'*44} {'-'*7}")
        for i, t in enumerate(combined[:15], 1):
            title = str(t.get("title", ""))[:43]
            click.echo(f"  {i:<4} {t.get('platform',''):<10} {title:<45} {t.get('score', 0):<8.1f}")
        click.echo()


@trends.command("list")
@click.option("--top", default=20, help="Number of trends to show")
@click.pass_context
def trends_list(ctx: click.Context, top: int) -> None:
    """Show cached trend data from the current session."""
    project = ctx.obj.get("project", "")
    sess = _load_session_or_die(ctx, project)
    combined = sess.all_trends()[:top]

    if not combined:
        click.echo("  No trend data. Run: trends fetch --mock")
        return

    if ctx.obj.get("json"):
        click.echo(json.dumps(combined, indent=2))
    else:
        click.echo(f"\n  Top {len(combined)} trends in session '{sess.name}'\n")
        click.echo(f"  {'#':<4} {'Platform':<10} {'Title':<45} {'Score':<8}")
        click.echo(f"  {'-'*3} {'-'*9} {'-'*44} {'-'*7}")
        for i, t in enumerate(combined, 1):
            title = str(t.get("title", ""))[:43]
            click.echo(f"  {i:<4} {t.get('platform',''):<10} {title:<45} {t.get('score', 0):<8.1f}")
        click.echo()


# ── hashtags commands ──────────────────────────────────────────────────

@cli.group()
def hashtags() -> None:
    """Hashtag research and optimization."""


@hashtags.command("recommend")
@click.option("--top", default=30, help="Number of hashtags to recommend")
@click.pass_context
def hashtags_recommend(ctx: click.Context, top: int) -> None:
    """Recommend hashtags based on fetched trends."""
    project = ctx.obj.get("project", "")
    sess = _load_session_or_die(ctx, project)

    from .youtube import extract_all_hashtags
    from .tiktok import _aggregate_hashtags

    yt_tags = extract_all_hashtags(sess.youtube_trends, top_n=top)
    tt_tags = _aggregate_hashtags(sess.tiktok_trends, top_n=top)
    merged = merge_hashtags(yt_tags, tt_tags, top_n=top)

    sess.set_hashtags(merged)
    sess.save(project or default_session_path(sess.name))

    if ctx.obj.get("json"):
        click.echo(json.dumps(merged, indent=2))
    else:
        click.echo(f"\n  Top {len(merged)} recommended hashtags\n")
        click.echo(f"  {'#':<4} {'Tag':<25} {'Score':<8} {'Freq':<6} {'Platforms':<20} {'Recommendation'}")
        click.echo(f"  {'-'*3} {'-'*24} {'-'*7} {'-'*5} {'-'*19} {'-'*30}")
        for i, h in enumerate(merged[:top], 1):
            platforms = "+".join(h.get("platforms", []))
            click.echo(
                f"  {i:<4} #{h['tag']:<24} {h['score']:<8.1f} {h['frequency']:<6} "
                f"{platforms:<20} {h.get('recommendation', '')}"
            )
        click.echo()


@hashtags.command("sets")
@click.option("--niche", "-n", default="", help="Niche override")
@click.pass_context
def hashtags_sets(ctx: click.Context, niche: str) -> None:
    """Generate ready-to-paste hashtag sets (viral / niche / balanced)."""
    project = ctx.obj.get("project", "")
    sess = _load_session_or_die(ctx, project)
    effective_niche = niche or sess.niche

    sets = generate_hashtag_sets(sess.hashtags, niche=effective_niche)

    if ctx.obj.get("json"):
        click.echo(json.dumps(sets, indent=2))
    else:
        for set_name, tags in sets.items():
            caption = " ".join(f"#{t}" for t in tags)
            click.echo(f"\n  [{set_name.upper()} SET]")
            click.echo(f"  {caption}")
        click.echo()


@hashtags.command("score")
@click.argument("tag")
@click.pass_context
def hashtags_score(ctx: click.Context, tag: str) -> None:
    """Score a specific hashtag against current trend data."""
    project = ctx.obj.get("project", "")
    sess = _load_session_or_die(ctx, project)

    tag_lower = tag.lstrip("#").lower()
    match = next((h for h in sess.hashtags if h["tag"] == tag_lower), None)

    if not match:
        result = {"tag": tag_lower, "score": 0, "found": False, "message": "Not in current trend data — try fetching trends first"}
    else:
        result = {**match, "found": True}

    if ctx.obj.get("json"):
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(f"\n  #{result['tag']}")
        if result.get("found"):
            click.echo(f"    Score:       {result['score']}")
            click.echo(f"    Frequency:   {result.get('frequency', 0)}")
            click.echo(f"    Avg Views:   {result.get('avg_views', 0):,}")
            click.echo(f"    Platforms:   {'+'.join(result.get('platforms', []))}")
            click.echo(f"    Verdict:     {result.get('recommendation', '')}")
        else:
            click.echo(f"    {result['message']}")
        click.echo()


# ── music commands ─────────────────────────────────────────────────────

@cli.group()
def music() -> None:
    """Trending sounds and music research."""


@music.command("trending")
@click.option("--region", "-r", default="", help="Region code")
@click.option("--mock", is_flag=True, help="Use mock data (no API key needed)")
@click.option("--top", default=20, help="Number of sounds to show")
@click.pass_context
def music_trending(ctx: click.Context, region: str, mock: bool, top: int) -> None:
    """Fetch and display trending sounds/music across TikTok and YouTube."""
    project = ctx.obj.get("project", "")
    sess = _load_session_or_die(ctx, project)
    effective_region = region or sess.region

    tt_sounds = []
    yt_music = []

    verbose = not ctx.obj.get("json")

    if mock:
        from .tiktok import fetch_mock_sounds
        tt_sounds = fetch_mock_sounds()
        if verbose:
            click.echo("  ● [Mock] TikTok sounds loaded")
    else:
        try:
            from .tiktok import query_trending_sounds
            keywords = [sess.niche] if sess.niche else ["trending", "viral", "fyp"]
            tt_sounds = query_trending_sounds(keywords, region=effective_region, top_n=top)
            if verbose:
                click.echo(f"  ✓ TikTok: {len(tt_sounds)} trending sounds")
        except (EnvironmentError, ImportError) as exc:
            if verbose:
                click.echo(f"  ⚠ TikTok sounds: {exc}\n    Use --mock for demo data.")

    try:
        from .youtube import fetch_trending_music
        if not mock:
            yt_music = fetch_trending_music(region=effective_region, max_results=top)
            if verbose:
                click.echo(f"  ✓ YouTube: {len(yt_music)} trending music videos")
    except (EnvironmentError, ImportError) as exc:
        if not mock and verbose:
            click.echo(f"  ⚠ YouTube music: {exc}")

    # Merge and rank sounds
    all_sounds = list(tt_sounds)
    for m in yt_music[:top]:
        all_sounds.append({
            "music_id": m.get("id", ""),
            "title": m.get("title", "")[:50],
            "artist": m.get("channel", ""),
            "frequency": 1,
            "avg_views": m.get("views", 0),
            "score": m.get("score", 0),
            "platform": "youtube",
        })

    all_sounds.sort(key=lambda s: s.get("score", 0), reverse=True)
    sess.set_sounds(all_sounds)
    sess.save(project or default_session_path(sess.name))

    if ctx.obj.get("json"):
        click.echo(json.dumps(all_sounds[:top], indent=2))
    else:
        click.echo(f"\n  Top {min(top, len(all_sounds))} trending sounds\n")
        click.echo(f"  {'#':<4} {'Title':<40} {'Platform':<10} {'Avg Views':<12} {'Score'}")
        click.echo(f"  {'-'*3} {'-'*39} {'-'*9} {'-'*11} {'-'*8}")
        for i, s in enumerate(all_sounds[:top], 1):
            title = str(s.get("title", ""))[:38]
            avg_views = s.get("avg_views", 0)
            click.echo(
                f"  {i:<4} {title:<40} {s.get('platform',''):<10} "
                f"{avg_views:>10,}   {s.get('score', 0):.1f}"
            )
        click.echo()


# ── optimize commands ──────────────────────────────────────────────────

@cli.group()
def optimize() -> None:
    """Account optimization and content planning."""


@optimize.command("run")
@click.pass_context
def optimize_run(ctx: click.Context) -> None:
    """Generate a full optimization report for all accounts in the session."""
    project = ctx.obj.get("project", "")
    sess = _load_session_or_die(ctx, project)

    if not sess.accounts:
        raise click.ClickException("No accounts found. Add accounts with: account add <platform> <handle>")

    click.echo(f"  ● Generating optimization report for {len(sess.accounts)} account(s)...")

    report = generate_optimization_report(
        accounts=sess.accounts,
        hashtags=sess.hashtags,
        sounds=sess.sounds,
        trends=sess.all_trends(),
        niche=sess.niche,
        region=sess.region,
    )

    sess.set_optimization_report(report)
    sess.save(project or default_session_path(sess.name))

    if ctx.obj.get("json"):
        click.echo(json.dumps(report, indent=2))
    else:
        _print_optimization_report(report)


@optimize.command("calendar")
@click.option("--days", default=7, help="Days to generate (default: 7)")
@click.pass_context
def optimize_calendar(ctx: click.Context, days: int) -> None:
    """Generate a content calendar based on current trends."""
    project = ctx.obj.get("project", "")
    sess = _load_session_or_die(ctx, project)

    calendar = build_content_calendar(
        trends=sess.all_trends(),
        hashtags=sess.hashtags,
        niche=sess.niche,
        days=days,
    )

    if ctx.obj.get("json"):
        click.echo(json.dumps(calendar, indent=2))
    else:
        click.echo(f"\n  {days}-Day Content Calendar — Niche: {sess.niche or 'general'}\n")
        for day in calendar:
            click.echo(f"  {day['day']:12} | {day['theme']:20} | {day['content_idea']:35} | {day['best_posting_time']}")
        click.echo()
        click.echo("  For full calendar with hashtags: use --json flag")


@optimize.command("score-idea")
@click.argument("title")
@click.option("--hashtags", "tag_list", multiple=True, help="Hashtags to include")
@click.pass_context
def optimize_score_idea(ctx: click.Context, title: str, tag_list: tuple[str, ...]) -> None:
    """Score a content idea against current trends.

    Example: optimize score-idea "My morning routine" --hashtags fyp motivation grwm
    """
    project = ctx.obj.get("project", "")
    sess = _load_session_or_die(ctx, project)

    result = score_content_idea(
        title=title,
        hashtags=list(tag_list),
        trending_hashtags=sess.hashtags,
        trending_sounds=sess.sounds,
    )

    if ctx.obj.get("json"):
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(f"\n  Content Idea: '{title}'")
        click.echo(f"  Relevance Score:   {result['relevance_score']}/100")
        click.echo(f"  Matched Hashtags:  {', '.join('#' + t for t in result['matched_hashtags']) or 'none'}")
        click.echo(f"  Sound to Use:      {result['sound_recommendation']}")
        click.echo(f"  Verdict:           {result['verdict']}")
        click.echo()


# ── theme-page commands ────────────────────────────────────────────────

@cli.group("theme-page")
def theme_page() -> None:
    """Theme page creation strategy and niche selection."""


@theme_page.command("niches")
@click.option("--sort", default="monetization_ease", help="Sort by: monetization_ease | avg_cpm | competition")
@click.pass_context
def theme_page_niches(ctx: click.Context, sort: str) -> None:
    """List all available niches ranked by profitability."""
    niches = list_niches(sort_by=sort)

    if ctx.obj.get("json"):
        click.echo(json.dumps(niches, indent=2))
    else:
        click.echo(f"\n  Available Niches (sorted by {sort})\n")
        click.echo(f"  {'Key':<22} {'Name':<25} {'CPM':<8} {'Competition':<15} {'Monetization'}")
        click.echo(f"  {'-'*21} {'-'*24} {'-'*7} {'-'*14} {'-'*15}")
        for n in niches:
            click.echo(
                f"  {n['key']:<22} {n['name']:<25} ${n['avg_cpm']:<7.2f} "
                f"{n['competition']:<15} {n['monetization_ease']}"
            )
        click.echo()
        click.echo("  Use: theme-page guide <niche-key>  for the full strategy guide")


@theme_page.command("guide")
@click.argument("niche_key", default="")
@click.pass_context
def theme_page_guide(ctx: click.Context, niche_key: str) -> None:
    """Show the full theme page creation guide for a niche.

    NICHE_KEY: niche key from 'theme-page niches' (e.g. luxury_lifestyle, fitness_wellness)
    """
    guide = get_theme_page_guide(niche_key)

    if ctx.obj.get("json"):
        click.echo(json.dumps(guide, indent=2))
    else:
        _print_theme_guide(guide)


@theme_page.command("score")
@click.argument("niche_key")
@click.pass_context
def theme_page_score(ctx: click.Context, niche_key: str) -> None:
    """Score a niche by opportunity (monetization, CPM, competition)."""
    result = score_niche(niche_key)

    if ctx.obj.get("json"):
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(f"\n  Niche Score: {result.get('niche', niche_key)}")
        click.echo(f"  Total Score:         {result.get('total_score', 0)}/100")
        click.echo(f"  Monetization:        {result.get('monetization_score', 0)}/100")
        click.echo(f"  CPM Value:           {result.get('cpm_score', 0)}/100")
        click.echo(f"  Competition Factor:  {result.get('competition_score', 0)}/100")
        click.echo(f"  Recommendation:      {result.get('recommendation', '')}")
        click.echo()


# ── REPL ───────────────────────────────────────────────────────────────

def _launch_repl(project: str) -> None:
    """Launch the interactive REPL."""
    try:
        from .utils.repl_skin import ReplSkin
    except ImportError:
        _launch_simple_repl(project)
        return

    skin = ReplSkin("social-trends", version=__version__)
    skin.print_banner()

    sess = None
    if project and session_exists(project):
        sess = TrendSession.load(project)
        skin.info(f"Loaded session: {sess.name} ({sess.region})")
    else:
        skin.hint("No session loaded. Use: session new <name>")

    pt_session = skin.create_prompt_session()

    while True:
        try:
            project_name = sess.name if sess else ""
            modified = sess.modified if sess else False
            line = skin.get_input(pt_session, project_name=project_name, modified=modified)
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

        if not line:
            continue
        if line.lower() in ("exit", "quit", "q"):
            skin.print_goodbye()
            break
        if line.lower() in ("help", "?"):
            skin.help({
                "session new <name>": "Create a new trend session",
                "account add <platform> <handle>": "Add a social account",
                "trends fetch --mock": "Fetch mock trend data",
                "hashtags recommend": "Recommend hashtags from trends",
                "hashtags sets": "Get ready-to-paste hashtag sets",
                "music trending --mock": "Show trending sounds",
                "optimize run": "Run optimization for all accounts",
                "optimize calendar": "Generate 7-day content calendar",
                "theme-page niches": "Browse niche opportunities",
                "theme-page guide <niche>": "Full theme page strategy guide",
                "theme-page score <niche>": "Score a niche",
            })
            continue

        # Execute via Click
        try:
            from click.testing import CliRunner
            runner = CliRunner(mix_stderr=False)
            args = line.split()
            result = runner.invoke(cli, args, catch_exceptions=False)
            if result.output:
                click.echo(result.output, nl=False)
            if result.exit_code != 0 and result.exception:
                skin.error(str(result.exception))
        except Exception as exc:
            skin.error(str(exc))


def _launch_simple_repl(project: str) -> None:
    """Fallback REPL without prompt_toolkit."""
    click.echo("cli-anything Social Trends v" + __version__)
    click.echo("Type 'help' for commands, 'quit' to exit.\n")
    while True:
        try:
            line = input("social-trends > ").strip()
        except (EOFError, KeyboardInterrupt):
            click.echo("\nGoodbye!")
            break
        if not line:
            continue
        if line.lower() in ("exit", "quit"):
            click.echo("Goodbye!")
            break
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(cli, line.split())
        click.echo(result.output, nl=False)


# ── Display helpers ────────────────────────────────────────────────────

def _print_optimization_report(report: dict[str, Any]) -> None:
    gs = report.get("global_strategy", {})

    click.echo(f"\n  OPTIMIZATION REPORT")
    click.echo(f"  Region: {report.get('region')}  |  Niche: {report.get('niche')}")
    click.echo(f"  Generated: {report.get('generated_at')}\n")

    click.echo("  GLOBAL STRATEGY")
    click.echo("  ─────────────────────────────────────────────")
    click.echo(f"  Posting Frequency:")
    for platform, freq in gs.get("posting_frequency", {}).items():
        click.echo(f"    {platform:<25} {freq}")

    click.echo(f"\n  Content Pillars:")
    for pillar in gs.get("content_pillars", []):
        click.echo(f"    • {pillar}")

    click.echo(f"\n  Top Hashtag Set (Balanced):")
    balanced = gs.get("hashtag_sets", {}).get("balanced", [])
    click.echo(f"    {' '.join('#' + t for t in balanced)}")

    click.echo(f"\n  Top Trending Sounds:")
    for s in gs.get("top_trending_sounds", [])[:3]:
        click.echo(f"    🎵 {s.get('title', '')}  (score: {s.get('score', 0)})")

    click.echo(f"\n  Engagement Hooks:")
    for hook in gs.get("engagement_hooks", [])[:4]:
        click.echo(f"    • {hook}")

    # Per-account
    for acct in report.get("accounts", []):
        click.echo(f"\n  ACCOUNT: @{acct['handle']} ({acct['platform'].upper()})")
        click.echo("  ─────────────────────────────────────────────")
        click.echo(f"  Bio Template:\n    {acct.get('bio_template','')}")
        click.echo(f"\n  Best Posting Times:  {', '.join(acct.get('optimal_posting_times', []))}")
        click.echo(f"\n  Content Angles:")
        for angle in acct.get("content_angles", [])[:3]:
            click.echo(f"    • {angle}")
        click.echo(f"\n  Monetization:")
        for m in acct.get("monetization_paths", [])[:2]:
            click.echo(f"    • {m['method']} — {m['est_revenue']} ({m['timeline']})")

    # Growth tactics
    click.echo(f"\n  GROWTH TACTICS")
    click.echo("  ─────────────────────────────────────────────")
    for tactic in report.get("growth_tactics", [])[:5]:
        click.echo(f"  [{tactic['impact']} impact] {tactic['tactic']}")
        click.echo(f"    {tactic['description']}")
        click.echo()

    click.echo("  Full report saved to session. Use --json for machine-readable output.\n")


def _print_theme_guide(guide: dict[str, Any]) -> None:
    click.echo(f"\n  {guide['title']}")
    click.echo("  " + "═" * 60)
    click.echo(f"\n  {guide['overview']}\n")

    # Account setup
    setup = guide.get("account_setup", {})
    click.echo("  ACCOUNT SETUP")
    click.echo("  ─────────────────────────────────────────────")
    for i, step in enumerate(setup.get("steps", []), 1):
        click.echo(f"  {i}. {step}")
    click.echo(f"\n  Bio Template:\n    {setup.get('bio_template', '')}")
    click.echo(f"\n  Platforms: {', '.join(setup.get('recommended_platforms', []))}")

    # Content strategy
    strategy = guide.get("content_strategy", {})
    click.echo("\n  CONTENT STRATEGY")
    click.echo("  ─────────────────────────────────────────────")
    click.echo(f"  Posting Frequency: {strategy.get('post_frequency', '')}")
    click.echo(f"\n  Content Mix:")
    for pct, desc in strategy.get("content_mix", {}).items():
        click.echo(f"    {pct}  {desc}")
    click.echo(f"\n  Repurposing Workflow:")
    for step in strategy.get("repurposing_workflow", []):
        click.echo(f"    {step}")

    # Growth phases
    click.echo("\n  GROWTH PLAYBOOK")
    click.echo("  ─────────────────────────────────────────────")
    for phase in guide.get("growth_playbook", []):
        click.echo(f"  [{phase['phase']}] ({phase['timeframe']})")
        click.echo(f"    {phase['strategy']}")
        click.echo()

    # Monetization
    click.echo("  MONETIZATION ROADMAP")
    click.echo("  ─────────────────────────────────────────────")
    for m in guide.get("monetization_roadmap", []):
        click.echo(f"  {m['milestone']}")
        click.echo(f"    Method:  {m['method']}")
        click.echo(f"    Action:  {m['action']}")
        click.echo(f"    Est Rev: {m['est_monthly']}/month")
        click.echo()

    # Common mistakes
    click.echo("  COMMON MISTAKES TO AVOID")
    click.echo("  ─────────────────────────────────────────────")
    for i, mistake in enumerate(guide.get("common_mistakes", []), 1):
        click.echo(f"  {i:2}. {mistake}")

    click.echo("\n  Use --json for full guide including tools, colors, and sourcing strategy.\n")


# ── Mock data helpers ──────────────────────────────────────────────────

def _mock_youtube_trends(region: str) -> list[dict[str, Any]]:
    import math
    mock = [
        {"id": "yt001", "title": "I Tried EVERY Viral TikTok Recipe (100 Days)", "channel": "FoodExplorer",
         "views": 8_400_000, "likes": 620_000, "comments": 28_000, "hashtags": ["food", "viral", "recipe", "tiktok", "challenge"],
         "url": "https://youtube.com/watch?v=yt001", "score": 0, "region": region, "published_at": "2025-01-10T00:00:00Z"},
        {"id": "yt002", "title": "Living Like a Billionaire for 30 Days", "channel": "LuxuryHacks",
         "views": 6_200_000, "likes": 480_000, "comments": 19_000, "hashtags": ["luxury", "billionaire", "lifestyle", "rich"],
         "url": "https://youtube.com/watch?v=yt002", "score": 0, "region": region, "published_at": "2025-01-08T00:00:00Z"},
        {"id": "yt003", "title": "Zero to $10K/Month Passive Income in 2025", "channel": "FinanceSimplified",
         "views": 5_100_000, "likes": 410_000, "comments": 24_000, "hashtags": ["finance", "passiveincome", "money", "investing"],
         "url": "https://youtube.com/watch?v=yt003", "score": 0, "region": region, "published_at": "2025-01-09T00:00:00Z"},
        {"id": "yt004", "title": "90-Day Body Transformation (The Truth)", "channel": "FitnessUnfiltered",
         "views": 4_700_000, "likes": 390_000, "comments": 16_000, "hashtags": ["fitness", "transformation", "gym", "workout"],
         "url": "https://youtube.com/watch?v=yt004", "score": 0, "region": region, "published_at": "2025-01-07T00:00:00Z"},
        {"id": "yt005", "title": "I Built a $1M Business on TikTok (Here's How)", "channel": "EcommerceKing",
         "views": 3_900_000, "likes": 320_000, "comments": 22_000, "hashtags": ["business", "tiktok", "entrepreneur", "money"],
         "url": "https://youtube.com/watch?v=yt005", "score": 0, "region": region, "published_at": "2025-01-06T00:00:00Z"},
    ]
    for v in mock:
        views, likes, comments = v["views"], v["likes"], v["comments"]
        er = (likes + comments * 2) / views * 1000
        v["score"] = round(er * math.log10(max(views, 1)), 2)
    return sorted(mock, key=lambda x: x["score"], reverse=True)


# ── Entry point ────────────────────────────────────────────────────────

def main() -> None:
    cli(obj={})


if __name__ == "__main__":
    main()
