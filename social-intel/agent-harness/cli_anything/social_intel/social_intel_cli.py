#!/usr/bin/env python3
"""social-intel CLI — Viral trend scraping, account optimization, and theme page strategy.

Covers YouTube Data API v3 and TikTok Research API / public trending.

Usage:
    # Set up API credentials
    social-intel auth setup --youtube-api-key KEY --tiktok-api-key TOKEN

    # YouTube trending
    social-intel youtube trending --region US --category music
    social-intel youtube music --region US
    social-intel youtube hashtag foryou

    # TikTok trending
    social-intel tiktok trending --region US
    social-intel tiktok hashtag gymtok
    social-intel tiktok search --keyword viral --keyword fyp

    # Account optimizer
    social-intel optimize --platform tiktok --niche fitness
    social-intel optimize --platform instagram --niche cars

    # Theme pages
    social-intel theme niche fitness
    social-intel theme niches
    social-intel theme roadmap --followers 5000
    social-intel theme funnel
    social-intel theme curation
    social-intel theme calendar --niche fitness --platform tiktok

    # Interactive REPL
    social-intel repl
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_intel.core import youtube as yt_mod
from cli_anything.social_intel.core import tiktok as tt_mod
from cli_anything.social_intel.core import optimizer as opt_mod
from cli_anything.social_intel.core import theme_pages as theme_mod
from cli_anything.social_intel.utils.backend import load_config, save_config

_json_output = False
_repl_mode = False

YT_CATEGORY_MAP = {
    "all": "0", "music": "10", "sports": "17", "gaming": "20",
    "entertainment": "24", "news": "25", "howto": "26", "science": "28",
}


# ── Output ───────────────────────────────────────────────────────

def output(data, message: str = "") -> None:
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(f"\n  {message}")
        _pretty(data)


def _pretty(data, indent: int = 1) -> None:
    prefix = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{prefix}{_fmt_key(k)}:")
                _pretty(v, indent + 1)
            else:
                click.echo(f"{prefix}{_fmt_key(k)}: {v}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                click.echo(f"{prefix}[{i + 1}]")
                _pretty(item, indent + 1)
            else:
                click.echo(f"{prefix}- {item}")
    else:
        click.echo(f"{prefix}{data}")


def _fmt_key(k: str) -> str:
    return k.replace("_", " ").title()


def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"\n  Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# ── Root ─────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx, use_json):
    """social-intel — YouTube & TikTok trend intelligence + account optimization."""
    global _json_output
    _json_output = use_json
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── Auth ─────────────────────────────────────────────────────────

@cli.group()
def auth():
    """API credential management."""
    pass


@auth.command("setup")
@click.option("--youtube-api-key", default=None, help="YouTube Data API v3 key")
@click.option("--tiktok-api-key", default=None, help="TikTok Research API bearer token")
@handle_error
def auth_setup(youtube_api_key, tiktok_api_key):
    """Store API credentials locally (~/.cli-anything/social-intel/config.json).

    YouTube API key: https://console.developers.google.com
      Enable 'YouTube Data API v3' — free 10,000 units/day quota.

    TikTok Research API token: https://developers.tiktok.com/application/research-api
      Requires application; takes 1–2 weeks to approve.
    """
    config = load_config()
    if youtube_api_key:
        config["youtube_api_key"] = youtube_api_key
    if tiktok_api_key:
        config["tiktok_api_key"] = tiktok_api_key
    save_config(config)
    keys_set = []
    if config.get("youtube_api_key"):
        keys_set.append("YouTube")
    if config.get("tiktok_api_key"):
        keys_set.append("TikTok")
    output({"configured": keys_set, "config_file": "~/.cli-anything/social-intel/config.json"},
           "Credentials saved.")


@auth.command("status")
@handle_error
def auth_status():
    """Show which API keys are configured."""
    config = load_config()
    output({
        "youtube_key_set": bool(config.get("youtube_api_key")),
        "tiktok_key_set": bool(config.get("tiktok_api_key")),
        "config_path": "~/.cli-anything/social-intel/config.json",
        "youtube_key_help": "Get free key: https://console.developers.google.com",
        "tiktok_key_help": "Apply: https://developers.tiktok.com/application/research-api",
    })


# ── YouTube ──────────────────────────────────────────────────────

@cli.group()
def youtube():
    """YouTube trending videos, music, and hashtag analysis."""
    pass


@youtube.command("trending")
@click.option("--region", "-r", default="US", show_default=True,
              help="ISO country code (US, GB, AU, CA, …)")
@click.option("--category", "-c", default="all", show_default=True,
              type=click.Choice(list(YT_CATEGORY_MAP.keys())),
              help="Content category")
@click.option("--count", "-n", default=20, show_default=True,
              help="Number of videos (1–50)")
@handle_error
def yt_trending(region, category, count):
    """Fetch trending YouTube videos with extracted hashtags and tags.

    Uses the YouTube Data API v3 mostPopular chart.
    Extracts top hashtags and video tags across all trending videos.
    """
    cat_id = YT_CATEGORY_MAP[category]
    result = yt_mod.get_trending_videos(
        region_code=region.upper(),
        category_id=cat_id,
        max_results=count,
    )
    output(result, f"YouTube Trending — {region.upper()} / {category}")


@youtube.command("music")
@click.option("--region", "-r", default="US", show_default=True,
              help="ISO country code")
@click.option("--count", "-n", default=20, show_default=True)
@handle_error
def yt_music(region, count):
    """Fetch trending music videos with TikTok-safe indicator.

    Shows artist, song, view count, and whether the audio is likely
    safe to use on TikTok (based on major-label licensing heuristics).
    """
    result = yt_mod.get_trending_music(region_code=region.upper(), max_results=count)
    output(result, f"YouTube Trending Music — {region.upper()}")


@youtube.command("hashtag")
@click.argument("tag")
@click.option("--count", "-n", default=20, show_default=True)
@click.option("--order", default="viewCount", show_default=True,
              type=click.Choice(["relevance", "date", "viewCount", "rating"]))
@handle_error
def yt_hashtag(tag, count, order):
    """Analyze a YouTube hashtag — engagement stats and competition level.

    TAG: Hashtag without the # prefix (e.g., fyp, fitness, viral).
    """
    result = yt_mod.search_hashtag(tag, max_results=count, order=order)
    output(result, f"YouTube Hashtag Analysis — #{tag}")


@youtube.command("categories")
@click.option("--region", "-r", default="US", show_default=True)
@handle_error
def yt_categories(region):
    """List all assignable YouTube video categories for a region."""
    result = yt_mod.list_categories(region_code=region.upper())
    output(result, f"YouTube Categories — {region.upper()}")


# ── TikTok ───────────────────────────────────────────────────────

@cli.group()
def tiktok():
    """TikTok trending sounds, hashtags, and video intelligence."""
    pass


@tiktok.command("trending")
@click.option("--region", "-r", default="US", show_default=True,
              help="ISO country code")
@click.option("--no-cache-fallback", is_flag=True,
              help="Fail instead of returning cached data on scrape failure")
@handle_error
def tt_trending(region, no_cache_fallback):
    """Scrape TikTok's public discover page for trending sounds and hashtags.

    Tries TikTok's public API endpoints. Falls back to last cached data
    if TikTok rate-limits (which is common). Use --no-cache-fallback to
    force a fresh fetch or fail explicitly.

    For reliable data at scale, use 'tiktok search' with the Research API.
    """
    result = tt_mod.get_trending_public(
        region=region.upper(),
        use_cache_on_fail=not no_cache_fallback,
    )
    output(result, f"TikTok Trending — {region.upper()}")


@tiktok.command("hashtag")
@click.argument("tag")
@handle_error
def tt_hashtag(tag):
    """Analyze a TikTok hashtag — view count, video count, and opportunity score.

    TAG: Hashtag without the # prefix (e.g., gymtok, booktok, viral).

    Opportunity score = views-per-video ratio. Higher means the hashtag
    converts views efficiently and is worth targeting.
    """
    result = tt_mod.analyze_hashtag(tag)
    output(result, f"TikTok Hashtag — #{tag}")


@tiktok.command("search")
@click.option("--keyword", "-k", multiple=True, required=True,
              help="Search keywords (use multiple -k flags)")
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--count", "-n", default=20, show_default=True,
              help="Max results (1–100)")
@click.option("--start-date", default=None, help="Start date YYYYMMDD (default: 7 days ago)")
@click.option("--end-date", default=None, help="End date YYYYMMDD (default: today)")
@handle_error
def tt_search(keyword, region, count, start_date, end_date):
    """Search TikTok videos via the Research API (requires approved access).

    Requires TikTok Research API token: social-intel auth setup --tiktok-api-key TOKEN
    Apply for access: https://developers.tiktok.com/application/research-api

    Returns videos, extracted top hashtags, and most-used sounds for
    the given keywords — ideal for identifying what's driving virality.
    """
    result = tt_mod.search_videos_research(
        keywords=list(keyword),
        max_count=count,
        region_code=region.upper(),
        start_date=start_date,
        end_date=end_date,
    )
    output(result, f"TikTok Research — {', '.join(keyword)}")


# ── Optimizer ────────────────────────────────────────────────────

@cli.command()
@click.option("--platform", "-p", required=True,
              type=click.Choice([
                  "tiktok", "youtube", "youtube_shorts",
                  "instagram", "instagram_reels",
              ]),
              help="Platform to optimize for")
@click.option("--niche", "-n", default="", help="Your content niche (for personalized tips)")
@handle_error
def optimize(platform, niche):
    """Generate a full account optimization report for a platform.

    Covers:
      - Best posting times (UTC)
      - Posting cadence recommendations
      - Hashtag strategy (size mix, placement, must-include tags)
      - Hook formulas (6 proven formats with examples)
      - Bio structure template
      - Content mix ratios (viral / educational / personal / promo)
      - Profile completeness checklist
      - Top growth levers ranked by impact
    """
    result = opt_mod.generate_report(platform=platform, niche=niche)
    output(result, f"Account Optimization — {platform.upper()}")


# ── Theme Pages ──────────────────────────────────────────────────

@cli.group()
def theme():
    """Theme page creation, niche analysis, and conversion strategy."""
    pass


@theme.command("niches")
@handle_error
def theme_niches():
    """List all supported niches with monetization scores and competition levels.

    Sorted by monetization potential (highest first).
    Use 'theme niche <name>' for a full deep-dive on any niche.
    """
    result = theme_mod.list_niches()
    output(result, "Available Niches — sorted by monetization score")


@theme.command("niche")
@click.argument("name")
@handle_error
def theme_niche(name):
    """Deep-dive analysis for a specific niche.

    NAME: Niche name (e.g., fitness, cars, finance_crypto, luxury_lifestyle).

    Returns: sub-niches, monetization score, competition, average CPM,
    best platforms, affiliate programs, content sources, and hook topics.
    """
    result = theme_mod.score_niche(name)
    output(result, f"Niche Analysis — {name}")


@theme.command("roadmap")
@click.option("--followers", "-f", required=True, type=int,
              help="Current follower/subscriber count")
@handle_error
def theme_roadmap(followers):
    """Get the monetization roadmap for your current follower tier.

    Shows what to focus on NOW and previews the next tier's strategy.
    Covers income streams, KPIs to track, and key milestones.
    """
    result = theme_mod.get_monetization_roadmap(follower_count=followers)
    output(result, f"Monetization Roadmap — {followers:,} followers")


@theme.command("funnel")
@handle_error
def theme_funnel():
    """Show the full AIDA conversion funnel for theme pages.

    Awareness → Interest → Desire → Action → Retention.

    Each stage has specific tactics to move followers toward purchase
    or sign-up. Most theme pages only execute Awareness — this shows
    the full funnel that converts views into revenue.
    """
    result = theme_mod.get_conversion_funnel()
    output(result, "Conversion Funnel — Awareness to Retention")


@theme.command("curation")
@handle_error
def theme_curation():
    """Show the content curation workflow — legal guidelines, sources, and tools.

    Covers:
      - Legal guidelines for repurposing content
      - Free, permission-required, and paid content sources
      - Repurposing tools (CapCut, Canva, Descript, OpusClip)
      - Scheduling tools (free and paid)
      - Analytics tools
    """
    result = theme_mod.get_curation_guide()
    output(result, "Content Curation Guide")


@theme.command("calendar")
@click.option("--niche", "-n", required=True,
              type=click.Choice(list(theme_mod.NICHE_DATABASE.keys())),
              help="Your content niche")
@click.option("--platform", "-p", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "instagram", "youtube"]),
              help="Target platform")
@click.option("--posts-per-week", "-w", default=7, show_default=True,
              type=click.IntRange(1, 21),
              help="Number of posts per week")
@handle_error
def theme_calendar(niche, platform, posts_per_week):
    """Generate a 1-week content calendar template.

    Produces a day-by-day posting plan with content types, hook ideas,
    source suggestions, and CTAs. Designed for theme pages that batch
    content creation in advance.
    """
    result = theme_mod.generate_content_calendar(
        niche=niche, platform=platform, posts_per_week=posts_per_week,
    )
    output(result, f"Content Calendar — {niche} / {platform} / {posts_per_week}x/week")


# ── REPL ─────────────────────────────────────────────────────────

@cli.command()
@handle_error
def repl():
    """Start interactive REPL session."""
    from cli_anything.social_intel.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("social-intel", version="1.0.0")
    skin.print_banner()
    pt_session = skin.create_prompt_session()

    _cmds = {
        "auth setup":        "--youtube-api-key KEY [--tiktok-api-key TOKEN]",
        "auth status":       "Show configured keys",
        "youtube trending":  "--region US --category music --count 20",
        "youtube music":     "--region US",
        "youtube hashtag":   "TAG [--count 20]",
        "tiktok trending":   "--region US",
        "tiktok hashtag":    "TAG",
        "tiktok search":     "-k keyword -k keyword2 [--region US]",
        "optimize":          "--platform tiktok --niche fitness",
        "theme niches":      "List all niches with scores",
        "theme niche":       "NAME  (e.g., fitness, cars)",
        "theme roadmap":     "--followers 5000",
        "theme funnel":      "Conversion funnel guide",
        "theme curation":    "Curation workflow + tools",
        "theme calendar":    "--niche fitness --platform tiktok --posts-per-week 7",
        "help":              "Show this help",
        "quit":              "Exit",
    }

    config = load_config()
    if config.get("youtube_api_key"):
        skin.success("YouTube API key configured")
    else:
        skin.warning("No YouTube API key — run: auth setup --youtube-api-key KEY")
    if config.get("tiktok_api_key"):
        skin.success("TikTok Research API token configured")
    else:
        skin.info("No TikTok Research token — public trending still works without it")

    while True:
        try:
            line = skin.get_input(pt_session)
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                skin.print_goodbye()
                break
            if line.lower() == "help":
                skin.help(_cmds)
                continue

            args = line.split()
            try:
                cli.main(args, standalone_mode=False)
            except SystemExit:
                pass
            except click.exceptions.UsageError as e:
                skin.warning(f"Usage error: {e}")
            except Exception as e:
                skin.error(str(e))

        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

    _repl_mode = False


# ── Entry Point ──────────────────────────────────────────────────

def main():
    cli()


if __name__ == "__main__":
    main()
