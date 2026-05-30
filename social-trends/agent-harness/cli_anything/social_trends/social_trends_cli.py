#!/usr/bin/env python3
"""Social Trends CLI — scrape YouTube & TikTok for viral trends, optimize accounts, master theme pages.

Usage:
    # Fetch trending content
    cli-anything-social-trends trends fetch-youtube --category music
    cli-anything-social-trends trends fetch-tiktok --region US
    cli-anything-social-trends trends fetch-all --output trends.json
    cli-anything-social-trends trends hashtags --niche fitness --platform tiktok
    cli-anything-social-trends trends music --platform youtube

    # Account optimization
    cli-anything-social-trends account optimize --platform tiktok --niche finance --followers 5000
    cli-anything-social-trends account schedule --platforms tiktok youtube instagram
    cli-anything-social-trends account bio --platform instagram --niche fitness --name "Mike"

    # Theme pages
    cli-anything-social-trends theme-page niches --sort monetization_potential
    cli-anything-social-trends theme-page detail luxury_lifestyle
    cli-anything-social-trends theme-page content-plan tech_ai --weeks 4
    cli-anything-social-trends theme-page monetize affiliate_marketing
    cli-anything-social-trends theme-page checklist
    cli-anything-social-trends theme-page sources

    # Config / session
    cli-anything-social-trends config set yt_api_key YOUR_KEY
    cli-anything-social-trends session history

    # Interactive REPL
    cli-anything-social-trends
"""

import sys
import os
import json
import shlex
import click
from typing import Optional
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_trends.core.session import Session
from cli_anything.social_trends.core import youtube as yt_mod
from cli_anything.social_trends.core import tiktok as tt_mod
from cli_anything.social_trends.core import trends as trends_mod
from cli_anything.social_trends.core import optimizer as opt_mod
from cli_anything.social_trends.core import theme_pages as theme_mod

_CONFIG_DIR = Path.home() / ".cli-anything-social-trends"
_CONFIG_FILE = _CONFIG_DIR / "config.json"

_session: Optional[Session] = None
_json_output = False
_repl_mode = False


def get_session() -> Session:
    global _session
    if _session is None:
        sf = str(_CONFIG_DIR / "session.json")
        _session = Session(session_file=sf)
    return _session


def load_config() -> dict:
    if not _CONFIG_FILE.exists():
        return {}
    try:
        with open(_CONFIG_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_config(cfg: dict):
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


def get_yt_api_key() -> str | None:
    env_key = os.environ.get("YOUTUBE_API_KEY") or os.environ.get("YT_API_KEY")
    if env_key:
        return env_key
    return load_config().get("yt_api_key")


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
        if k == "_ts":
            continue
        if isinstance(v, dict):
            click.echo(f"{prefix}{k}:")
            _print_dict(v, indent + 1)
        elif isinstance(v, list):
            click.echo(f"{prefix}{k}: [{len(v)} items]")
            if len(v) <= 5:
                for item in v:
                    if isinstance(item, dict):
                        _print_dict(item, indent + 2)
                    else:
                        click.echo(f"{'  ' * (indent + 1)}- {item}")
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


def handle_error(func):
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (FileNotFoundError, ValueError, RuntimeError, TimeoutError, KeyError) as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
        except Exception as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"Unexpected error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)

    return wrapper


# ── Root CLI ────────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.version_option("1.0.0", prog_name="cli-anything-social-trends")
@click.pass_context
def cli(ctx, use_json):
    """Social Trends CLI — YouTube & TikTok viral scraping, account optimization, theme pages."""
    global _json_output
    _json_output = use_json
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── trends group ────────────────────────────────────────────────────────────────

@cli.group()
def trends():
    """Trend fetching — YouTube & TikTok viral content, hashtags, music."""
    pass


@trends.command("fetch-youtube")
@click.option("--category", "-c", default="all",
              type=click.Choice(["all", "music", "gaming", "news", "movies", "sports"]),
              show_default=True, help="Trend category")
@click.option("--region", "-r", default="US", show_default=True, help="Region code (US, GB, etc.)")
@click.option("--max", "max_results", type=int, default=25, show_default=True, help="Max results")
@click.option("--no-cache", is_flag=True, help="Bypass local cache")
@click.option("--output", "-o", "output_file", default=None, help="Save JSON to file")
@handle_error
def trends_fetch_youtube(category, region, max_results, no_cache, output_file):
    """Fetch YouTube trending videos, hashtags, and music."""
    api_key = get_yt_api_key()
    if not _json_output:
        source = "YouTube Data API v3" if api_key else "YouTube innertube (no key)"
        click.echo(f"Fetching YouTube trending [{category}] via {source}...")

    result = yt_mod.fetch_trending_youtube(
        category=category,
        region=region,
        max_results=max_results,
        api_key=api_key,
        use_cache=not no_cache,
    )

    sess = get_session()
    sess.record("trends fetch-youtube", {"category": category, "region": region}, {
        "video_count": len(result.get("videos", [])),
        "hashtag_count": len(result.get("hashtags", [])),
        "from_cache": result.get("from_cache", False),
    })

    if output_file:
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2, default=str)
        if not _json_output:
            click.echo(f"Saved to {output_file}")

    _display_trends_result(result, "YouTube")


def _display_trends_result(result: dict, platform: str):
    if _json_output:
        output(result)
        return

    videos = result.get("videos", [])
    hashtags = result.get("hashtags", [])
    music = result.get("music", [])
    from_cache = result.get("from_cache", False)

    cache_note = " (cached)" if from_cache else ""
    click.echo(f"\n  {platform} Trending{cache_note} — {result.get('fetched_at', '')[:10]}")
    click.echo(f"  Region: {result.get('region', 'US')} | Source: {result.get('source', '')}\n")

    if videos:
        click.echo(f"  TOP VIDEOS ({len(videos)})")
        click.echo("  " + "─" * 60)
        for i, v in enumerate(videos[:10], 1):
            views = _fmt_number(v.get("view_count", v.get("play_count", 0)))
            title = v.get("title") or v.get("description", "")[:60]
            channel = v.get("channel") or v.get("author", "")
            click.echo(f"  {i:2}. {title[:50]:<50} {views:>10} views")
            click.echo(f"      {channel}")

    if hashtags:
        click.echo(f"\n  TOP HASHTAGS ({len(hashtags)})")
        click.echo("  " + "─" * 40)
        cols = [hashtags[i:i+5] for i in range(0, min(20, len(hashtags)), 5)]
        for row in cols:
            click.echo("  " + "  ".join(f"{h['tag']:<20}" for h in row))

    if music:
        click.echo(f"\n  TRENDING MUSIC ({len(music)})")
        click.echo("  " + "─" * 40)
        for m in music[:8]:
            title = m.get("title", "")[:35]
            artist = m.get("artist") or m.get("authorName", "")
            click.echo(f"  ♪ {title} — {artist}")

    click.echo()


def _fmt_number(n: int) -> str:
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


@trends.command("fetch-tiktok")
@click.option("--region", "-r", default="US", show_default=True, help="Region code")
@click.option("--max", "max_results", type=int, default=30, show_default=True)
@click.option("--no-cache", is_flag=True, help="Bypass local cache")
@click.option("--output", "-o", "output_file", default=None, help="Save JSON to file")
@handle_error
def trends_fetch_tiktok(region, max_results, no_cache, output_file):
    """Fetch TikTok trending videos, hashtags, and sounds."""
    if not _json_output:
        click.echo(f"Fetching TikTok trending [{region}]...")

    result = tt_mod.fetch_trending_tiktok(
        region=region,
        max_results=max_results,
        use_cache=not no_cache,
    )

    sess = get_session()
    sess.record("trends fetch-tiktok", {"region": region}, {
        "video_count": len(result.get("videos", [])),
        "hashtag_count": len(result.get("hashtags", [])),
        "from_cache": result.get("from_cache", False),
    })

    if output_file:
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2, default=str)
        if not _json_output:
            click.echo(f"Saved to {output_file}")

    _display_trends_result(result, "TikTok")


@trends.command("fetch-all")
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--no-cache", is_flag=True)
@click.option("--output", "-o", "output_file", default=None, help="Save aggregate JSON")
@handle_error
def trends_fetch_all(region, no_cache, output_file):
    """Fetch and aggregate trends from both YouTube and TikTok."""
    api_key = get_yt_api_key()

    if not _json_output:
        click.echo("Fetching YouTube trends...")
    yt_data = yt_mod.fetch_trending_youtube(
        region=region, api_key=api_key, use_cache=not no_cache
    )

    if not _json_output:
        click.echo("Fetching TikTok trends...")
    tt_data = tt_mod.fetch_trending_tiktok(
        region=region, use_cache=not no_cache
    )

    aggregate = trends_mod.aggregate_trends(yt_data, tt_data)

    sess = get_session()
    sess.record("trends fetch-all", {"region": region}, {
        "hashtags": len(aggregate.get("hashtags", [])),
        "cross_platform": len(aggregate.get("cross_platform_hashtags", [])),
    })

    if output_file:
        with open(output_file, "w") as f:
            json.dump(aggregate, f, indent=2, default=str)
        if not _json_output:
            click.echo(f"Saved aggregate trends to {output_file}")

    if _json_output:
        output(aggregate)
        return

    click.echo(f"\n  CROSS-PLATFORM TRENDS ({region})")
    click.echo("  " + "═" * 60)

    cp = aggregate.get("cross_platform_hashtags", [])
    if cp:
        click.echo(f"\n  TRENDING ON BOTH PLATFORMS ({len(cp)} tags)")
        click.echo("  " + "─" * 40)
        for h in cp[:10]:
            score = _fmt_number(h.get("virality_score", 0))
            click.echo(f"  {h['tag']:<25} score: {score}")

    ht = aggregate.get("hashtags", [])
    if ht:
        click.echo(f"\n  ALL TRENDING HASHTAGS (ranked by virality)")
        click.echo("  " + "─" * 40)
        for h in ht[:20]:
            platforms = "+".join(h.get("platforms", []))
            click.echo(f"  {h['tag']:<25} [{platforms}]")

    music = aggregate.get("music", [])
    if music:
        click.echo(f"\n  TRENDING MUSIC ({len(music)} tracks)")
        click.echo("  " + "─" * 40)
        for m in music[:8]:
            click.echo(f"  ♪ {m.get('title', '')[:40]} — {m.get('artist', '')}")

    click.echo()


@trends.command("hashtags")
@click.option("--platform", "-p", default="all",
              type=click.Choice(["all", "youtube", "tiktok"]), show_default=True)
@click.option("--niche", "-n", default="", help="Content niche for personalized set")
@click.option("--max", "top_n", type=int, default=30, show_default=True)
@click.option("--strategy", "-s", default="mixed",
              type=click.Choice(["mixed", "viral", "niche"]), show_default=True)
@click.option("--region", "-r", default="US", show_default=True)
@handle_error
def trends_hashtags(platform, niche, top_n, strategy, region):
    """Get trending hashtags optimized for your niche and platform."""
    api_key = get_yt_api_key()

    yt_data = None
    tt_data = None

    if platform in ("all", "youtube"):
        if not _json_output:
            click.echo("Fetching YouTube hashtags...")
        yt_data = yt_mod.fetch_trending_youtube(region=region, api_key=api_key)

    if platform in ("all", "tiktok"):
        if not _json_output:
            click.echo("Fetching TikTok hashtags...")
        tt_data = tt_mod.fetch_trending_tiktok(region=region)

    agg = trends_mod.aggregate_trends(yt_data, tt_data, top_n=top_n)
    hashtag_set = trends_mod.build_hashtag_set(agg, niche=niche, max_tags=top_n, strategy=strategy)

    sess = get_session()
    sess.record("trends hashtags", {"platform": platform, "niche": niche, "strategy": strategy}, hashtag_set)

    if _json_output:
        output(hashtag_set)
        return

    click.echo(f"\n  HASHTAG SET — {strategy.upper()} strategy{f' | niche: {niche}' if niche else ''}")
    click.echo("  " + "═" * 60)

    for plat, tags in [("TikTok (3-8 tags)", hashtag_set["tiktok_set"]),
                       ("YouTube (15-30 tags)", hashtag_set["youtube_set"]),
                       ("Instagram (10-15 tags)", hashtag_set["instagram_set"])]:
        click.echo(f"\n  {plat}")
        click.echo("  " + " ".join(tags))

    notes = hashtag_set.get("strategy_notes", {})
    if notes:
        click.echo("\n  STRATEGY NOTES")
        for plat, note in notes.items():
            click.echo(f"  {plat}: {note}")

    click.echo()


@trends.command("music")
@click.option("--platform", "-p", default="all",
              type=click.Choice(["all", "youtube", "tiktok"]), show_default=True)
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--max", "max_results", type=int, default=20, show_default=True)
@handle_error
def trends_music(platform, region, max_results):
    """Get trending music/sounds from YouTube and TikTok."""
    api_key = get_yt_api_key()
    music = []

    if platform in ("all", "youtube"):
        yt_music = yt_mod.fetch_youtube_music(region=region, max_results=max_results, api_key=api_key)
        for m in yt_music:
            m["platform"] = "youtube"
        music.extend(yt_music)

    if platform in ("all", "tiktok"):
        tt_music = tt_mod.fetch_tiktok_music(region=region, max_results=max_results)
        music.extend(tt_music)

    sess = get_session()
    sess.record("trends music", {"platform": platform, "region": region}, {"count": len(music)})

    if _json_output:
        output(music[:max_results])
        return

    click.echo(f"\n  TRENDING MUSIC — {platform.upper()} | {region}")
    click.echo("  " + "═" * 60)
    for i, m in enumerate(music[:max_results], 1):
        title = m.get("title", "Unknown")[:40]
        artist = m.get("artist") or m.get("authorName", "")
        plat = m.get("platform", "")
        uses = m.get("use_count", 0)
        use_str = f" ({_fmt_number(uses)} uses)" if uses else ""
        click.echo(f"  {i:2}. [{plat:<8}] ♪ {title} — {artist}{use_str}")

    click.echo()


# ── account group ───────────────────────────────────────────────────────────────

@cli.group()
def account():
    """Account optimization — posting schedule, bio generator, growth tactics."""
    pass


@account.command("optimize")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram", "twitter"]),
              help="Platform to optimize for")
@click.option("--niche", "-n", default="", help="Content niche")
@click.option("--followers", "-f", type=int, default=0, show_default=True, help="Current follower count")
@click.option("--goals", "-g", multiple=True,
              type=click.Choice(["growth", "monetization", "brand_deals", "traffic"]),
              help="Goals (repeatable)")
@handle_error
def account_optimize(platform, niche, followers, goals):
    """Generate a full account optimization plan."""
    result = opt_mod.optimize_account(
        platform=platform,
        niche=niche,
        current_followers=followers,
        goals=list(goals) if goals else ["growth"],
    )

    sess = get_session()
    sess.record("account optimize", {"platform": platform, "niche": niche}, {
        "stage": result["growth_stage"]["stage"]
    })

    if _json_output:
        output(result)
        return

    stage = result["growth_stage"]
    click.echo(f"\n  ACCOUNT OPTIMIZATION — {platform.upper()}")
    click.echo("  " + "═" * 60)
    click.echo(f"  Stage: {stage['label']}")
    click.echo(f"  Priority: {stage['priority']}")
    if niche:
        click.echo(f"  Niche: {niche}")

    click.echo("\n  CONTENT RECOMMENDATIONS")
    click.echo("  " + "─" * 40)
    for tip in result.get("content_recommendations", []):
        click.echo(f"  • {tip}")

    click.echo("\n  GROWTH TACTICS")
    click.echo("  " + "─" * 40)
    for tip in result.get("growth_tactics", []):
        click.echo(f"  • {tip}")

    if result.get("monetization_path"):
        click.echo("\n  MONETIZATION PATH")
        click.echo("  " + "─" * 40)
        for step in result["monetization_path"]:
            click.echo(f"  → {step}")

    kpis = result.get("kpis_to_track", [])
    if kpis:
        click.echo("\n  KPIs TO TRACK")
        click.echo("  " + "─" * 40)
        for k in kpis:
            click.echo(f"  {k['metric']:<35} Target: {k['target']}")
            click.echo(f"    ↳ {k['why']}")

    click.echo("\n  CONTENT HOOKS (use in first 3 seconds)")
    click.echo("  " + "─" * 40)
    for hook in result.get("content_hooks", []):
        click.echo(f"  • {hook}")

    profile_tips = result.get("profile_optimization", {})
    if profile_tips:
        click.echo("\n  PROFILE OPTIMIZATION")
        click.echo("  " + "─" * 40)
        for tip in profile_tips.get("bio_tips", []):
            click.echo(f"  • {tip}")
        if profile_tips.get("link_tip"):
            click.echo(f"  Link: {profile_tips['link_tip']}")

    click.echo()


@account.command("schedule")
@click.option("--platforms", "-p", multiple=True,
              type=click.Choice(["tiktok", "youtube", "instagram", "twitter"]),
              default=["tiktok", "youtube", "instagram"],
              show_default=True,
              help="Platforms (repeatable)")
@handle_error
def account_schedule(platforms):
    """Get optimal posting schedule for your platforms."""
    result = opt_mod.get_posting_schedule(platforms=list(platforms))

    sess = get_session()
    sess.record("account schedule", {"platforms": list(platforms)}, {})

    if _json_output:
        output(result)
        return

    click.echo("\n  OPTIMAL POSTING SCHEDULE")
    click.echo("  " + "═" * 60)

    for platform, sched in result.get("platforms", {}).items():
        freq = sched.get("frequency", {})
        click.echo(f"\n  {platform.upper()} — {freq.get('min', 1)}-{freq.get('max', 3)} {freq.get('unit', 'per week')}")
        click.echo(f"  {freq.get('note', '')} | Timezone: {sched.get('timezone', 'EST')}")
        click.echo("  " + "─" * 40)
        for day, times in sched.get("best_times", {}).items():
            time_str = ", ".join(times) if isinstance(times, list) else times
            click.echo(f"  {day.capitalize():<12}: {time_str}")

    click.echo("\n  GENERAL TIPS")
    click.echo("  " + "─" * 40)
    for tip in result.get("general_tips", []):
        click.echo(f"  • {tip}")

    click.echo()


@account.command("bio")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--name", "-n", required=True, help="Your name or brand name")
@click.option("--niche", required=True, help="Content niche")
@click.option("--value-prop", "-v", default="level up your life", help="Your unique value proposition")
@click.option("--cta", default="follow",
              type=click.Choice(["follow", "subscribe", "link", "dm", "shop"]),
              help="Call to action type")
@handle_error
def account_bio(platform, name, niche, value_prop, cta):
    """Generate optimized profile bios for your platform."""
    result = opt_mod.generate_bio(
        platform=platform,
        name=name,
        niche=niche,
        value_prop=value_prop,
        cta=cta,
    )

    sess = get_session()
    sess.record("account bio", {"platform": platform, "niche": niche}, {})

    if _json_output:
        output(result)
        return

    click.echo(f"\n  BIO OPTIONS — {platform.upper()}")
    click.echo(f"  Character limit: {result['character_limit']}")
    click.echo("  " + "═" * 60)

    for i, opt in enumerate(result.get("bio_options", []), 1):
        fits = "✓" if opt["fits"] else "✗ TOO LONG"
        click.echo(f"\n  OPTION {i} ({opt['length']} chars) [{fits}]")
        click.echo("  " + "─" * 40)
        for line in opt["text"].split("\n"):
            click.echo(f"  {line}")

    click.echo("\n  BIO TIPS")
    click.echo("  " + "─" * 40)
    for tip in result.get("tips", []):
        click.echo(f"  • {tip}")

    click.echo()


# ── theme-page group ─────────────────────────────────────────────────────────────

@cli.group("theme-page")
def theme_page():
    """Theme page mastery — niches, content plans, monetization, legal sources."""
    pass


@theme_page.command("niches")
@click.option("--sort", "-s", default="monetization_potential",
              type=click.Choice(["monetization_potential", "growth_speed", "difficulty", "name"]),
              show_default=True)
@click.option("--difficulty", "-d", default=None,
              type=click.Choice(["easy", "medium", "hard"]))
@click.option("--platform", "-p", default=None,
              type=click.Choice(["tiktok", "youtube", "instagram", "twitter"]))
@handle_error
def theme_page_niches(sort, difficulty, platform):
    """List all profitable theme page niches."""
    results = theme_mod.list_niches(
        sort_by=sort,
        filter_difficulty=difficulty,
        filter_platform=platform,
    )

    if _json_output:
        output(results)
        return

    click.echo(f"\n  THEME PAGE NICHES — sorted by {sort}")
    click.echo("  " + "═" * 70)
    click.echo(f"  {'ID':<25} {'Name':<22} {'Potential':<12} {'Growth':<12} {'Difficulty'}")
    click.echo("  " + "─" * 70)
    for n in results:
        sat = " ⚠ saturated" if n.get("saturated") else ""
        click.echo(
            f"  {n['id']:<25} {n['name']:<22} "
            f"{n.get('monetization_potential', ''):<12} "
            f"{n.get('growth_speed', ''):<12} "
            f"{n.get('difficulty', '')}{sat}"
        )
    click.echo(f"\n  Run: theme-page detail <niche-id> for full breakdown")
    click.echo()


@theme_page.command("detail")
@click.argument("niche_id")
@handle_error
def theme_page_detail(niche_id):
    """Show full details for a specific niche."""
    result = theme_mod.get_niche_detail(niche_id)

    if _json_output:
        output(result)
        return

    click.echo(f"\n  {result['name'].upper()} — Theme Page Breakdown")
    click.echo("  " + "═" * 60)
    click.echo(f"  {result['description']}")
    click.echo()
    click.echo(f"  Difficulty:          {result.get('difficulty', '').title()}")
    click.echo(f"  Monetization:        {result.get('monetization_potential', '').replace('_', ' ').title()}")
    click.echo(f"  Growth Speed:        {result.get('growth_speed', '').replace('_', ' ').title()}")
    click.echo(f"  Avg CPM:             {result.get('avg_cpm', 'N/A')}")
    click.echo(f"  Saturated:           {'Yes ⚠' if result.get('saturated') else 'No ✓'}")
    click.echo(f"  Target Audience:     {result.get('target_audience', '')}")
    click.echo(f"  Best Platforms:      {', '.join(result.get('best_platforms', []))}")

    click.echo("\n  CONTENT TYPES")
    click.echo("  " + "─" * 40)
    for ct in result.get("content_types", []):
        click.echo(f"  • {ct}")

    click.echo()


@theme_page.command("content-plan")
@click.argument("niche_id")
@click.option("--platforms", "-p", multiple=True,
              type=click.Choice(["tiktok", "youtube", "instagram", "twitter"]),
              help="Platforms (repeatable)")
@click.option("--weeks", "-w", type=int, default=4, show_default=True)
@handle_error
def theme_page_content_plan(niche_id, platforms, weeks):
    """Generate a weekly content calendar for a theme page niche."""
    result = theme_mod.generate_content_plan(
        niche_id=niche_id,
        platforms=list(platforms) if platforms else None,
        weeks=weeks,
    )

    if _json_output:
        output(result)
        return

    click.echo(f"\n  {weeks}-WEEK CONTENT PLAN — {result['niche']}")
    click.echo(f"  Platforms: {', '.join(result['platforms'])}")
    click.echo("  " + "═" * 60)

    for week_data in result.get("weekly_plan", []):
        click.echo(f"\n  WEEK {week_data['week']}")
        click.echo("  " + "─" * 50)
        for post in week_data.get("posts", []):
            click.echo(f"  {post['day']:<12} {post['content_type']:<30} [{post['format']}]")
            click.echo(f"             ↳ Tip: {post['tip']}")

    click.echo(f"\n  Strategy: {result.get('general_strategy', '')}")
    click.echo(f"  Source content from: {', '.join(result.get('content_sources', []))}")
    click.echo()


@theme_page.command("monetize")
@click.argument("method", required=False)
@handle_error
def theme_page_monetize(method):
    """Show monetization strategies for theme pages (all or specific method)."""
    result = theme_mod.get_monetization_guide(method)

    if _json_output:
        output(result)
        return

    click.echo("\n  THEME PAGE MONETIZATION GUIDE")
    click.echo("  " + "═" * 60)

    for method_name, info in result.items():
        click.echo(f"\n  {method_name.upper().replace('_', ' ')}")
        click.echo(f"  {info['description']}")
        click.echo(f"  Min followers: {info.get('follower_minimum', 0):,}")
        click.echo(f"  Earnings:      {info.get('rate_range', info.get('rate', 'Varies'))}")

        how_to = info.get("how_to_get", info.get("programs", []))
        if how_to:
            click.echo("  How to start:")
            for step in how_to[:4]:
                click.echo(f"    → {step}")

    click.echo()


@theme_page.command("checklist")
@handle_error
def theme_page_checklist():
    """Show the full theme page launch checklist."""
    result = theme_mod.get_launch_checklist()

    if _json_output:
        output(result)
        return

    click.echo("\n  THEME PAGE LAUNCH CHECKLIST")
    click.echo("  " + "═" * 60)
    for item in result:
        check = "[ ]"
        click.echo(f"  {check} {item['step']:2}. {item['action']}")

    click.echo()


@theme_page.command("sources")
@handle_error
def theme_page_sources():
    """List legal content sources for theme pages (royalty-free)."""
    result = theme_mod.get_legal_sources()

    if _json_output:
        output(result)
        return

    click.echo("\n  LEGAL CONTENT SOURCES FOR THEME PAGES")
    click.echo("  " + "═" * 70)
    click.echo(f"  {'Source':<15} {'Type':<25} {'License':<30} URL")
    click.echo("  " + "─" * 70)
    for s in result:
        click.echo(f"  {s['source']:<15} {s['type']:<25} {s['license']:<30} {s['url']}")

    click.echo()


@theme_page.command("repurpose")
@handle_error
def theme_page_repurpose():
    """Show the content repurposing workflow — 1 video → 7 platforms."""
    result = theme_mod.get_content_repurposing_guide()

    if _json_output:
        output(result)
        return

    click.echo("\n  CONTENT REPURPOSING WORKFLOW")
    click.echo("  Make ONE video, post everywhere")
    click.echo("  " + "═" * 60)

    click.echo("\n  WORKFLOW (in order)")
    click.echo("  " + "─" * 40)
    for i, step in enumerate(result.get("workflow", []), 1):
        click.echo(f"  {i}. {step}")

    click.echo("\n  RECOMMENDED TOOLS")
    click.echo("  " + "─" * 40)
    for tool in result.get("tools", []):
        click.echo(f"  • {tool}")

    click.echo()


# ── config group ────────────────────────────────────────────────────────────────

@cli.group()
def config():
    """Configuration — API keys and settings."""
    pass


@config.command("set")
@click.argument("key", type=click.Choice(["yt_api_key", "default_region", "default_niche"]))
@click.argument("value")
@handle_error
def config_set(key, value):
    """Set a configuration value."""
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)
    display = value[:10] + "..." if key == "yt_api_key" and len(value) > 10 else value
    output({"key": key, "value": display}, f"Set {key} = {display}")


@config.command("get")
@click.argument("key", required=False)
@handle_error
def config_get(key):
    """Get a configuration value or show all."""
    cfg = load_config()
    if key:
        val = cfg.get(key)
        masked = val[:10] + "..." if val and key == "yt_api_key" and len(val) > 10 else val
        output({"key": key, "value": masked}, f"{key} = {masked}")
    else:
        masked = {}
        for k, v in cfg.items():
            masked[k] = v[:10] + "..." if k == "yt_api_key" and len(v) > 10 else v
        output(masked)


@config.command("delete")
@click.argument("key")
@handle_error
def config_delete(key):
    """Delete a configuration value."""
    cfg = load_config()
    if key in cfg:
        del cfg[key]
        save_config(cfg)
        output({"deleted": key}, f"Deleted {key}")
    else:
        output({"error": f"{key} not found"}, f"{key} not found")


# ── session group ───────────────────────────────────────────────────────────────

@cli.group()
def session():
    """Session management — history, undo, redo."""
    pass


@session.command("status")
def session_status():
    """Show session status."""
    sess = get_session()
    output(sess.status())


@session.command("history")
@click.option("--limit", "-n", type=int, default=20)
def session_history(limit):
    """Show command history."""
    sess = get_session()
    entries = sess.history(limit=limit)
    if not entries:
        output([], "No history.")
        return
    output(entries, f"History ({len(entries)} entries):")


@session.command("undo")
def session_undo():
    """Undo last command."""
    sess = get_session()
    entry = sess.undo()
    if entry:
        output(entry.to_dict(), f"Undone: {entry.command}")
    else:
        output({"error": "Nothing to undo"}, "Nothing to undo")


@session.command("redo")
def session_redo():
    """Redo last undone command."""
    sess = get_session()
    entry = sess.redo()
    if entry:
        output(entry.to_dict(), f"Redone: {entry.command}")
    else:
        output({"error": "Nothing to redo"}, "Nothing to redo")


# ── REPL ─────────────────────────────────────────────────────────────────────────

@cli.command("repl", hidden=True)
def repl():
    """Enter interactive REPL mode."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.social_trends.utils.repl_skin import ReplSkin
    skin = ReplSkin(version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    commands = {
        "trends fetch-youtube": "Fetch YouTube trending videos",
        "trends fetch-tiktok": "Fetch TikTok trending videos",
        "trends fetch-all": "Aggregate trends from both platforms",
        "trends hashtags --niche <n>": "Get optimized hashtag set",
        "trends music": "Get trending music/sounds",
        "account optimize -p <platform> -n <niche>": "Full account optimization plan",
        "account schedule": "Optimal posting schedule",
        "account bio -p <platform> -n <niche>": "Generate profile bio options",
        "theme-page niches": "List profitable niches",
        "theme-page detail <niche-id>": "Niche breakdown",
        "theme-page content-plan <niche-id>": "Generate content calendar",
        "theme-page monetize": "Monetization strategies",
        "theme-page checklist": "Launch checklist",
        "theme-page sources": "Legal content sources",
        "theme-page repurpose": "Content repurposing workflow",
        "config set yt_api_key <key>": "Set YouTube API key",
        "session history": "Show command history",
        "session undo": "Undo last command",
        "help": "Show this help",
        "quit / exit": "Exit REPL",
    }

    while True:
        try:
            line = skin.get_input(pt_session)
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

        if not line:
            continue
        if line in ("quit", "exit", "q"):
            skin.print_goodbye()
            break
        if line in ("help", "h", "?"):
            skin.help(commands)
            continue

        try:
            args = shlex.split(line)
        except ValueError as e:
            skin.error(f"Parse error: {e}")
            continue

        try:
            cli.main(args=args, standalone_mode=False)
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
