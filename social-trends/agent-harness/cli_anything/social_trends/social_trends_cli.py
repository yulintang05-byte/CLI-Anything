#!/usr/bin/env python3
"""Social Trends CLI — YouTube & TikTok viral trends, hashtags, music, and account optimization.

Real-time data from YouTube Data API v3 and TikTok Research/RapidAPI.
Covers trending videos, hashtags, viral sounds, account optimization,
and a complete converting theme page strategy system.

Usage:
    # Configure API keys
    social-trends config set youtube_api_key YOUR_YOUTUBE_KEY
    social-trends config set rapidapi_key YOUR_RAPIDAPI_KEY   # TikTok via RapidAPI

    # Fetch trending
    social-trends trending youtube --region US --category music
    social-trends trending tiktok --region US

    # Hashtags
    social-trends hashtags youtube --region US
    social-trends hashtags tiktok --region US

    # Music
    social-trends music youtube --region US
    social-trends music tiktok

    # Account optimization
    social-trends optimize --platform tiktok --followers 5000 --niche fitness

    # Theme page strategy
    social-trends theme-page guide
    social-trends theme-page niches
    social-trends theme-page playbook --niche finance --platform tiktok
    social-trends theme-page monetize

    # Interactive REPL
    social-trends repl
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_trends.core import config as cfg_mod
from cli_anything.social_trends.core import youtube_trends as yt
from cli_anything.social_trends.core import tiktok_trends as tt
from cli_anything.social_trends.core import account_optimizer as opt
from cli_anything.social_trends.core import theme_page as tp

# ── Output helpers ────────────────────────────────────────────────────

_json_output = False


def _out(data, message: str = "") -> None:
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        _pretty(data)


def _pretty(data, indent: int = 0) -> None:
    pad = "  " * indent
    if isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                click.echo(f"{pad}[{i + 1}]")
                _pretty(item, indent + 1)
                click.echo()
            else:
                click.echo(f"{pad}• {item}")
    elif isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{pad}\033[1m{k}\033[0m:")
                _pretty(v, indent + 1)
            else:
                click.echo(f"{pad}\033[36m{k}\033[0m: {v}")
    else:
        click.echo(f"{pad}{data}")


def _err(msg: str) -> None:
    click.echo(f"\033[31m✗ {msg}\033[0m", err=True)


def _ok(msg: str) -> None:
    click.echo(f"\033[32m✓ {msg}\033[0m")


def _header(title: str, subtitle: str = "") -> None:
    width = 60
    click.echo(f"\n\033[1m\033[38;5;80m{'━' * width}\033[0m")
    click.echo(f"\033[1m  {title}\033[0m")
    if subtitle:
        click.echo(f"\033[38;5;245m  {subtitle}\033[0m")
    click.echo(f"\033[38;5;80m{'━' * width}\033[0m\n")


def _section(title: str) -> None:
    click.echo(f"\n\033[1m\033[38;5;220m▸ {title}\033[0m")


# ── Root CLI ──────────────────────────────────────────────────────────

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--json", "use_json", is_flag=True, default=False,
              help="Output results as JSON (agent-friendly)")
@click.version_option("1.0.0", prog_name="social-trends")
def cli(use_json: bool) -> None:
    """Social Trends CLI — viral trends, hashtags, music, and account growth tools.

    \b
    Platforms: YouTube (Data API v3) • TikTok (Research API / RapidAPI)
    Setup:     social-trends config set youtube_api_key KEY
               social-trends config set rapidapi_key KEY
    """
    global _json_output
    _json_output = use_json


# ── Config ─────────────────────────────────────────────────────────────

@cli.group()
def config() -> None:
    """Manage API keys and preferences."""
    pass


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str) -> None:
    """Set a config value. Keys: youtube_api_key, rapidapi_key, tiktok_client_key, tiktok_client_secret"""
    cfg_mod.set_key(key, value)
    _ok(f"Set {key} (stored in ~/.cli-anything-social-trends/config.json)")


@config.command("get")
@click.argument("key")
def config_get(key: str) -> None:
    """Get a config value."""
    val = cfg_mod.get(key)
    if val is None:
        _err(f"Key '{key}' not set")
    else:
        # Mask secrets
        if any(k in key for k in ["key", "secret", "token", "password"]):
            masked = str(val)[:4] + "****" + str(val)[-4:] if len(str(val)) > 8 else "****"
            click.echo(f"{key}: {masked}")
        else:
            click.echo(f"{key}: {val}")


@config.command("list")
def config_list() -> None:
    """List all configured keys (values masked)."""
    data = cfg_mod.load()
    if not data:
        click.echo("No config keys set. Run: social-trends config set <key> <value>")
        return
    for k, v in data.items():
        val = str(v)
        if any(s in k for s in ["key", "secret", "token", "password"]):
            val = val[:4] + "****" if len(val) > 4 else "****"
        click.echo(f"  {k}: {val}")


@config.command("setup")
def config_setup() -> None:
    """Interactive setup wizard for API keys."""
    _header("Social Trends Setup", "Configure API keys for YouTube and TikTok")
    click.echo("You need at least one API key to fetch live data.\n")

    click.echo("\033[1mOption 1: YouTube Data API v3 (FREE)\033[0m")
    click.echo("  1. Go to https://console.developers.google.com/")
    click.echo("  2. Create a project → Enable 'YouTube Data API v3'")
    click.echo("  3. Create credentials → API Key\n")

    click.echo("\033[1mOption 2: TikTok via RapidAPI (FREEMIUM)\033[0m")
    click.echo("  1. Go to https://rapidapi.com")
    click.echo("  2. Search 'TikTok Scraper' → Subscribe to free plan")
    click.echo("  3. Copy your RapidAPI key\n")

    click.echo("\033[1mOption 3: TikTok Research API (OFFICIAL — requires application)\033[0m")
    click.echo("  1. Apply at https://developers.tiktok.com/products/research-api/")
    click.echo("  2. Approval can take 1-4 weeks\n")

    yt_key = click.prompt("YouTube API key (press Enter to skip)", default="", show_default=False)
    if yt_key:
        cfg_mod.set_key("youtube_api_key", yt_key)
        _ok("YouTube API key saved")

    rapid_key = click.prompt("RapidAPI key (press Enter to skip)", default="", show_default=False)
    if rapid_key:
        cfg_mod.set_key("rapidapi_key", rapid_key)
        _ok("RapidAPI key saved")

    if not yt_key and not rapid_key:
        click.echo("\n\033[33m⚠ No keys configured. Run this setup again or use:\033[0m")
        click.echo("  social-trends config set youtube_api_key YOUR_KEY")
    else:
        _ok("Setup complete! Try: social-trends trending youtube")


# ── Trending ─────────────────────────────────────────────────────────

@cli.group()
def trending() -> None:
    """Fetch trending videos from YouTube or TikTok."""
    pass


@trending.command("youtube")
@click.option("--region", "-r", default="US", show_default=True,
              help="Region code (US, GB, CA, AU, IN, etc.)")
@click.option("--category", "-c", default="all", show_default=True,
              type=click.Choice(["all", "music", "gaming", "entertainment", "howto",
                                 "news", "sports", "comedy", "film", "pets", "food"]),
              help="Video category filter")
@click.option("--limit", "-n", default=20, show_default=True,
              help="Number of results (max 50)")
def trending_youtube(region: str, category: str, limit: int) -> None:
    """Fetch YouTube trending videos with engagement metrics."""
    try:
        _header(f"YouTube Trending — {region.upper()} / {category}",
                f"Top {limit} trending videos")
        videos = yt.get_trending_videos(region=region, category=category, limit=limit)
        _out(videos)
        if not _json_output:
            click.echo(f"\n\033[38;5;245mTotal: {len(videos)} videos\033[0m")
    except Exception as e:
        _err(str(e))
        sys.exit(1)


@trending.command("tiktok")
@click.option("--region", "-r", default="US", show_default=True,
              help="Region code (US, GB, CA, AU, IN, etc.)")
@click.option("--limit", "-n", default=20, show_default=True,
              help="Number of results")
def trending_tiktok(region: str, limit: int) -> None:
    """Fetch TikTok trending videos with engagement metrics."""
    try:
        _header(f"TikTok Trending — {region.upper()}", f"Top {limit} trending videos")
        videos = tt.get_trending_videos(region=region, limit=limit)
        _out(videos)
        if not _json_output:
            click.echo(f"\n\033[38;5;245mTotal: {len(videos)} videos\033[0m")
    except Exception as e:
        _err(str(e))
        sys.exit(1)


# ── Hashtags ──────────────────────────────────────────────────────────

@cli.group()
def hashtags() -> None:
    """Trending hashtags from YouTube or TikTok."""
    pass


@hashtags.command("youtube")
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--limit", "-n", default=20, show_default=True)
@click.option("--search", "-s", default=None,
              help="Search videos for a specific hashtag")
def hashtags_youtube(region: str, limit: int, search: Optional[str]) -> None:
    """Trending hashtags extracted from YouTube top 50 trending videos."""
    try:
        if search:
            _header(f"YouTube: #{search.lstrip('#')} videos", f"Region: {region.upper()}")
            data = yt.search_trending_hashtag(search, region=region, limit=limit)
        else:
            _header(f"YouTube Trending Hashtags — {region.upper()}", "Aggregated from top 50 trending")
            data = yt.get_trending_hashtags(region=region, limit=limit)
        _out(data)
    except Exception as e:
        _err(str(e))
        sys.exit(1)


@hashtags.command("tiktok")
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--limit", "-n", default=20, show_default=True)
@click.option("--search", "-s", default=None,
              help="Get videos for a specific hashtag")
def hashtags_tiktok(region: str, limit: int, search: Optional[str]) -> None:
    """Trending hashtags from TikTok."""
    try:
        if search:
            _header(f"TikTok: #{search.lstrip('#')} videos", f"Region: {region.upper()}")
            data = tt.get_hashtag_videos(search, limit=limit)
        else:
            _header(f"TikTok Trending Hashtags — {region.upper()}", "Aggregated from trending feed")
            data = tt.get_trending_hashtags(region=region, limit=limit)
        _out(data)
    except Exception as e:
        _err(str(e))
        sys.exit(1)


# ── Music ─────────────────────────────────────────────────────────────

@cli.group()
def music() -> None:
    """Trending music and sounds from YouTube or TikTok."""
    pass


@music.command("youtube")
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--limit", "-n", default=20, show_default=True)
def music_youtube(region: str, limit: int) -> None:
    """Trending music on YouTube (top music videos with artist/track data)."""
    try:
        _header(f"YouTube Trending Music — {region.upper()}", f"Top {limit} music videos")
        data = yt.get_trending_music(region=region, limit=limit)
        _out(data)
    except Exception as e:
        _err(str(e))
        sys.exit(1)


@music.command("tiktok")
@click.option("--limit", "-n", default=20, show_default=True)
def music_tiktok(limit: int) -> None:
    """Trending sounds on TikTok (audio used in viral videos)."""
    try:
        _header("TikTok Trending Sounds", f"Top {limit} sounds")
        data = tt.get_trending_sounds(limit=limit)
        _out(data)
    except Exception as e:
        _err(str(e))
        sys.exit(1)


# ── Account Optimization ──────────────────────────────────────────────

@cli.command("optimize")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["youtube", "tiktok", "both"]),
              help="Platform to optimize for")
@click.option("--followers", "-f", default=0, type=int,
              help="Current follower count")
@click.option("--niche", "-n", default="entertainment",
              help="Your content niche (finance, fitness, pets, food, tech, etc.)")
@click.option("--avg-views", default=None, type=int,
              help="Average views per post (for engagement rate calculation)")
@click.option("--avg-likes", default=None, type=int,
              help="Average likes per post")
@click.option("--posts-per-week", default=None, type=int,
              help="Current posting frequency")
@click.option("--channel-id", default=None,
              help="YouTube channel ID (for live stats fetch)")
def optimize(platform: str, followers: int, niche: str, avg_views: Optional[int],
             avg_likes: Optional[int], posts_per_week: Optional[int],
             channel_id: Optional[str]) -> None:
    """Generate data-driven account optimization recommendations.

    \b
    Example:
        social-trends optimize --platform tiktok --followers 5000 \\
            --niche fitness --avg-views 3000 --avg-likes 200
    """
    try:
        platforms = ["youtube", "tiktok"] if platform == "both" else [platform]
        results = {}

        for plat in platforms:
            if plat == "youtube" and channel_id:
                _header(f"Fetching YouTube channel stats for {channel_id}")
                stats = yt.get_channel_stats(channel_id)
                followers = stats.get("subscribers", followers) or followers
                click.echo(f"Channel: {stats.get('name')} | Subscribers: {followers:,}")

            _header(f"Account Optimization — {plat.upper()} / {niche.title()}",
                    f"{followers:,} followers")
            rec = opt.analyze_account(
                followers=followers,
                platform=plat,
                niche=niche,
                avg_views=avg_views,
                avg_likes=avg_likes,
                posts_per_week=posts_per_week,
            )
            results[plat] = rec

            if not _json_output:
                _section("Tier & Engagement")
                click.echo(f"  Tier: {rec['tier'].upper()} ({rec['follower_range']})")
                er = rec["engagement_rate"]
                if er["current"]:
                    click.echo(f"  Engagement Rate: {er['current']}% — {er['rating']}")
                    click.echo(f"  Benchmark: Good ≥ {er['benchmark_good']}% | Avg ≥ {er['benchmark_avg']}%")

                _section("Posting Schedule")
                sched = rec["posting_schedule"]
                freq = sched["recommended_frequency"]
                click.echo(f"  Target: {freq['target_per_week']} posts/week")
                if freq['current_per_week']:
                    gap_str = (f"  (+{freq['gap']} needed)" if freq['gap'] and freq['gap'] > 0
                               else "  (on target!)" if freq['gap'] == 0 else "  (can reduce)")
                    click.echo(f"  Current: {freq['current_per_week']}/week{gap_str}")
                click.echo(f"  Note: {freq['note']}")

                _section("Hashtag Strategy")
                hs = rec["hashtag_strategy"]
                click.echo(f"  Formula: {hs['formula']}")
                click.echo(f"  Max hashtags: {hs['max_hashtags']}")
                click.echo(f"  Evergreen: {' '.join(hs['evergreen'][:5])}")
                click.echo(f"  Trending:  {' '.join(hs['trending_triggers'][:3])}")
                click.echo(f"  Community: {' '.join(hs['community'][:3])}")

                _section("Growth Tactics")
                for tactic in rec["growth_tactics"]:
                    click.echo(f"  • {tactic}")

                _section("Bio Optimization")
                for tip in rec["bio_optimization"]:
                    click.echo(f"  • {tip}")

                _section("Content Pillars (4E Framework)")
                for pillar in rec["content_pillars"]:
                    click.echo(f"  [{pillar['ratio']}] {pillar['pillar']}: "
                               f"{', '.join(pillar['examples'][:2])}")

        if _json_output:
            _out(results if platform == "both" else results[platforms[0]])

    except Exception as e:
        _err(str(e))
        sys.exit(1)


@cli.command("score")
@click.argument("title")
@click.option("--niche", "-n", default="entertainment")
@click.option("--hashtags", "-t", default="", help="Comma-separated trending hashtags")
def score_idea(title: str, niche: str, hashtags: str) -> None:
    """Score a video idea for viral potential (0-100).

    \b
    Example:
        social-trends score "5 Money Mistakes That Keep You Broke" --niche finance
    """
    tags = [t.strip() for t in hashtags.split(",") if t.strip()]
    result = opt.score_video_idea(title, niche, tags)
    if _json_output:
        _out(result)
    else:
        _header("Viral Potential Score", title)
        color = "\033[32m" if result["score"] >= 80 else "\033[33m" if result["score"] >= 60 else "\033[31m"
        click.echo(f"  Score: {color}{result['score']}/100 — {result['rating']}\033[0m")
        if result["signals"]:
            click.echo("\n  Positive signals:")
            for s in result["signals"]:
                click.echo(f"    ✓ {s}")
        click.echo(f"\n  Suggestion: {result['suggestion']}")


# ── Theme Page ────────────────────────────────────────────────────────

@cli.group("theme-page")
def theme_page() -> None:
    """Converting theme page strategy — build, grow, and monetize niche accounts."""
    pass


@theme_page.command("guide")
def theme_page_guide() -> None:
    """Full guide: What is a converting theme page and how to build one."""
    if _json_output:
        sourcing = tp.get_content_sourcing_guide()
        blueprint = tp.get_monetization_blueprint()
        _out({"sourcing_guide": sourcing, "monetization_blueprint": blueprint})
        return

    _header("Converting Theme Page — Complete Guide",
            "Build a niche account that grows and generates revenue")

    click.echo("""
\033[1mWHAT IS A CONVERTING THEME PAGE?\033[0m
A theme page is a social media account that:
  • Curates and reposts viral content around a specific niche
  • Doesn't require you to show your face or create original content
  • Grows quickly by riding existing viral trends
  • Converts followers into buyers through affiliate links, products, or services

\033[1mWHY THEME PAGES WORK:\033[0m
  • Algorithm rewards consistency + engagement, not originality
  • You start posting Day 1 (no filming/editing skills needed)
  • Proven content: you only repost what's already gone viral
  • Passive income: affiliate links in bio earn 24/7
  • Scalable: run 3-5 pages across different niches simultaneously

\033[1mTHE 4-STEP SYSTEM:\033[0m
  1. PICK A NICHE    → Run: social-trends theme-page niches
  2. BUILD YOUR PAGE → Run: social-trends theme-page playbook --niche <niche>
  3. GROW AUDIENCE   → Run: social-trends optimize --platform tiktok --niche <niche>
  4. MONETIZE        → Run: social-trends theme-page monetize
""")

    _section("Content Sourcing — Where to Find Viral Content")
    sourcing = tp.get_content_sourcing_guide()
    click.echo("\n  \033[1mAlways do:\033[0m")
    for rule in sourcing["always_do"]:
        click.echo(f"    ✓ {rule}")
    click.echo("\n  \033[1mBest free sources:\033[0m")
    for src in sourcing["content_sources"]["free_licensed"]:
        click.echo(f"    • {src}")
    click.echo("\n  \033[1mRepost-friendly platforms:\033[0m")
    for src in sourcing["content_sources"]["repost_friendly_platforms"]:
        click.echo(f"    • {src}")
    click.echo("\n  \033[1mNever do:\033[0m")
    for rule in sourcing["avoid"]:
        click.echo(f"    ✗ {rule}")

    click.echo("\n\033[38;5;245mNext: social-trends theme-page niches (see all niches ranked by profit potential)\033[0m\n")


@theme_page.command("niches")
@click.option("--sort-by", default="score",
              type=click.Choice(["score", "monetization", "growth", "competition"]))
def theme_page_niches(sort_by: str) -> None:
    """All niches ranked by monetization potential and growth speed."""
    niches = tp.get_all_niches_ranked()
    if _json_output:
        _out(niches)
        return

    _header("Theme Page Niches — Ranked by Score", "Monetization × Growth ÷ Competition")

    sort_map = {
        "score": "overall_score",
        "monetization": "monetization",
        "growth": "growth_speed",
        "competition": "competition",
    }
    key = sort_map[sort_by]
    reverse = sort_by != "competition"
    niches = sorted(niches, key=lambda x: x[key], reverse=reverse)

    click.echo(f"  {'#':<3} {'Niche':<35} {'Score':<7} {'Money':<7} {'Growth':<7} {'Comp':<5} {'CPM'}")
    click.echo(f"  {'─'*3} {'─'*35} {'─'*7} {'─'*7} {'─'*7} {'─'*5} {'─'*10}")
    for i, n in enumerate(niches, 1):
        score_col = f"\033[32m{n['overall_score']}\033[0m" if n["overall_score"] >= 8 else str(n["overall_score"])
        click.echo(
            f"  {i:<3} {n['niche'][:34]:<35} {score_col:<14} "
            f"{n['monetization']:<7} {n['growth_speed']:<7} {n['competition']:<5} {n['cpm']}"
        )

    click.echo(f"\n\033[38;5;245m  Score = (Monetization × 40%) + (Growth × 40%) + ((10-Competition) × 20%)\033[0m")
    click.echo(f"\033[38;5;245m  Run: social-trends theme-page playbook --niche \"Personal Finance / Wealth\"\033[0m\n")


@theme_page.command("playbook")
@click.option("--niche", "-n", required=True,
              help="Niche name (e.g. finance, fitness, luxury, pets, food, tech)")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "instagram", "youtube"]))
def theme_page_playbook(niche: str, platform: str) -> None:
    """30-day launch playbook for a new theme page."""
    playbook = tp.get_launch_playbook(niche=niche, platform=platform)
    if _json_output:
        _out(playbook)
        return

    _header(f"30-Day Theme Page Playbook — {niche.title()}",
            f"Platform: {platform.title()}")

    for phase in playbook["phases"]:
        _section(f"{phase['phase']} (Days {phase['days']})")
        click.echo(f"  \033[38;5;245mGoal: {phase['goal']}\033[0m")
        for task in phase["tasks"]:
            click.echo(f"  □ {task}")
        click.echo()

    _section("Content Sources for This Niche")
    for src in playbook["content_sources"]:
        click.echo(f"  • {src}")

    _section("Best CTAs to Use")
    for cta in playbook["best_ctas"]:
        click.echo(f"  • {cta}")

    click.echo(f"\n\033[38;5;245mSee monetization milestones: social-trends theme-page monetize\033[0m\n")


@theme_page.command("monetize")
def theme_page_monetize() -> None:
    """Monetization blueprint by follower milestone."""
    blueprint = tp.get_monetization_blueprint()
    if _json_output:
        _out(blueprint)
        return

    _header("Theme Page Monetization Blueprint", "Revenue milestones and strategies")
    for stage in blueprint:
        _section(stage["milestone"])
        click.echo(f"  \033[33mStrategy:\033[0m {stage['strategy']}")
        click.echo(f"  \033[32mRevenue:\033[0m  {stage['realistic_revenue']}")
        click.echo(f"  \033[36mActions:\033[0m")
        for action in stage["actions"]:
            click.echo(f"    □ {action}")
        click.echo()


@theme_page.command("niche-detail")
@click.argument("niche")
def theme_page_niche_detail(niche: str) -> None:
    """Deep-dive into a specific niche: affiliate opportunities, CTAs, content sources."""
    data = tp.get_niche_score(niche)
    if not data:
        _err(f"Niche '{niche}' not found. Run: social-trends theme-page niches")
        sys.exit(1)
    if _json_output:
        _out(data)
        return

    _header(f"Niche Detail — {data['niche']}", f"Score: {data['overall_score']}/10")
    click.echo(f"  Monetization: {data['monetization']}/10")
    click.echo(f"  Growth Speed: {data['growth_speed']}/10")
    click.echo(f"  Competition:  {data['competition']}/10")
    click.echo(f"  CPM Level:    {data['cpm']}")
    click.echo(f"\n  \033[1mWhy it converts:\033[0m {data['why_converts']}")

    _section("Affiliate Opportunities")
    for aff in data["affiliate_examples"]:
        click.echo(f"  • {aff}")

    _section("Content Sources")
    for src in data["content_sources"]:
        click.echo(f"  • {src}")

    _section("Best Platforms")
    for plat in data["platforms"]:
        click.echo(f"  • {plat}")

    _section("Converting CTAs")
    for cta in data["best_ctas"]:
        click.echo(f"  • {cta}")


# ── Combined cross-platform trends ────────────────────────────────────

@cli.command("all-trends")
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--limit", "-n", default=10, show_default=True)
def all_trends(region: str, limit: int) -> None:
    """Fetch trending from both YouTube AND TikTok simultaneously.

    Requires both youtube_api_key and TikTok API key configured.
    """
    results: dict = {"youtube": [], "tiktok": [], "combined_hashtags": []}
    errors = []

    try:
        _header(f"All Platforms Trending — {region.upper()}", f"Top {limit} per platform")
        click.echo("Fetching YouTube trending...")
        results["youtube"] = yt.get_trending_videos(region=region, limit=limit)
    except Exception as e:
        errors.append(f"YouTube: {e}")

    try:
        click.echo("Fetching TikTok trending...")
        results["tiktok"] = tt.get_trending_videos(region=region, limit=limit)
    except Exception as e:
        errors.append(f"TikTok: {e}")

    # Cross-platform hashtag overlap
    yt_tags = set()
    tt_tags = set()
    for v in results["youtube"]:
        yt_tags.update(h.lower() for h in v.get("hashtags", []))
    for v in results["tiktok"]:
        tt_tags.update(h.lower() for h in v.get("hashtags", []))
    overlap = yt_tags & tt_tags
    results["combined_hashtags"] = sorted(overlap)

    if errors:
        for err in errors:
            click.echo(f"\033[33m⚠ {err}\033[0m")

    _out(results)

    if not _json_output and overlap:
        click.echo(f"\n\033[1m✨ Cross-platform viral hashtags (use these NOW):\033[0m")
        click.echo("  " + "  ".join(sorted(overlap)[:15]))


# ── REPL ──────────────────────────────────────────────────────────────

@cli.command("repl")
def repl() -> None:
    """Interactive REPL for exploring trends and optimization."""
    try:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin("social_trends", version="1.0.0")
        skin.print_banner()
    except Exception:
        click.echo("\033[1m\033[38;5;80m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")
        click.echo("\033[1m  Social Trends CLI — Interactive Mode\033[0m")
        click.echo("\033[38;5;80m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\n")

    click.echo("Commands: trending youtube | trending tiktok | hashtags | music | optimize | theme-page | quit\n")

    while True:
        try:
            cmd = click.prompt("\033[38;5;80m▸ social-trends\033[0m", prompt_suffix=" ").strip()
            if not cmd:
                continue
            if cmd.lower() in ("quit", "exit", "q"):
                click.echo("Goodbye.")
                break

            # Dispatch to CLI
            from click.testing import CliRunner
            runner = CliRunner(mix_stderr=False)
            args = cmd.split()
            result = runner.invoke(cli, args, catch_exceptions=False)
            if result.output:
                click.echo(result.output)
            if result.exception and not isinstance(result.exception, SystemExit):
                _err(str(result.exception))
        except (KeyboardInterrupt, EOFError):
            click.echo("\nGoodbye.")
            break
        except Exception as e:
            _err(str(e))


# ── Info ──────────────────────────────────────────────────────────────

@cli.command("info")
def info() -> None:
    """Show current configuration and platform status."""
    data = {
        "version": "1.0.0",
        "config_dir": str(cfg_mod._CONFIG_DIR),
        "configured_keys": list(cfg_mod.load().keys()),
        "platforms": {
            "youtube": {
                "api": "YouTube Data API v3",
                "quota": "10,000 units/day (free)",
                "key_configured": bool(cfg_mod.get("youtube_api_key")),
                "setup": "console.developers.google.com → Enable YouTube Data API v3",
            },
            "tiktok_rapidapi": {
                "api": "TikTok Scraper via RapidAPI",
                "quota": "500 req/month (free tier)",
                "key_configured": bool(cfg_mod.get("rapidapi_key")),
                "setup": "rapidapi.com → search 'TikTok Scraper'",
            },
            "tiktok_official": {
                "api": "TikTok Research API",
                "quota": "Varies by approval",
                "key_configured": bool(cfg_mod.get("tiktok_client_key")),
                "setup": "developers.tiktok.com/products/research-api/",
            },
        },
        "commands": [
            "social-trends config setup",
            "social-trends trending youtube --region US",
            "social-trends trending tiktok --region US",
            "social-trends hashtags youtube",
            "social-trends hashtags tiktok",
            "social-trends music youtube",
            "social-trends music tiktok",
            "social-trends optimize --platform tiktok --followers 5000 --niche fitness",
            "social-trends score 'Your Video Title' --niche finance",
            "social-trends theme-page guide",
            "social-trends theme-page niches",
            "social-trends theme-page playbook --niche finance",
            "social-trends theme-page monetize",
            "social-trends all-trends --region US",
        ],
    }
    _out(data)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
